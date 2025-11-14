#!/usr/bin/env python3
"""
Shared JP-8080 SysEx decoding/encoding utilities.

This module centralises all logic for reading, decoding, analysing, exporting,
and repairing Roland JP-8080 System Exclusive data so that higher-level
tools (CLI wrappers, scripts, docs) can rely on a single source of truth.
"""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from statistics import mean, median
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

PATCH_SIZE = 248  # 0x178 bytes per patch
ROLAND_MANUFACTURER = 0x41
JP8080_MODEL_ID = [0x00, 0x06]


@dataclass
class SysexHeader:
    manufacturer: int
    device_id: int
    model_id: List[int]
    command: int


def calculate_checksum(data: bytes) -> int:
    """
    Calculate Roland checksum.
    Checksum = 128 - (sum of address and data bytes) % 128
    """
    total = sum(data) % 128
    return (128 - total) & 0x7F


def decode_roland_sysex(data: bytes) -> Tuple[SysexHeader, bytes, int]:
    """
    Decode Roland SysEx message.
    Returns: (header, payload_data, address)
    """
    if len(data) < 12:
        raise ValueError("SysEx message too short")

    if data[0] != 0xF0:
        raise ValueError("Missing SysEx start byte (F0)")

    if data[1] != ROLAND_MANUFACTURER:
        raise ValueError(f"Not a Roland SysEx file (manufacturer ID: {data[1]:02X})")

    if data[-1] != 0xF7:
        raise ValueError("SysEx message missing terminating F7 byte")

    device_id = data[2]
    model_id = [data[3], data[4]]
    command = data[5]

    # Extract address (4 bytes)
    address = (data[6] << 21) | (data[7] << 14) | (data[8] << 7) | data[9]

    # Extract data (everything between address and checksum/F7)
    payload_data = data[10:-2]

    # Verify checksum
    checksum_byte = data[-2]
    address_bytes = data[6:10]
    calculated_checksum = calculate_checksum(address_bytes + payload_data)

    if checksum_byte != calculated_checksum:
        raise ValueError(
            f"Checksum mismatch: got {checksum_byte:02X}, expected {calculated_checksum:02X}"
        )

    header = SysexHeader(
        manufacturer=data[1],
        device_id=device_id,
        model_id=model_id,
        command=command,
    )

    return header, payload_data, address


def encode_roland_sysex(
    address: int, data: bytes, device_id: int = 0x10, command: int = 0x12
) -> bytes:
    """
    Encode data into Roland SysEx format (DT1).
    Default command 0x12 = DT1 (Data Set 1)
    """
    # Split address into 4 bytes
    addr_bytes = bytes([
        (address >> 21) & 0x7F,
        (address >> 14) & 0x7F,
        (address >> 7) & 0x7F,
        address & 0x7F,
    ])

    # Calculate checksum
    checksum = calculate_checksum(addr_bytes + data)

    # Build complete message
    msg = bytes([0xF0, ROLAND_MANUFACTURER, device_id])
    msg += bytes(JP8080_MODEL_ID)
    msg += bytes([command])
    msg += addr_bytes
    msg += data
    msg += bytes([checksum, 0xF7])

    return msg


def _signed_offset64(value: int) -> int:
    """Convert offset-64 value to signed (-64 to +63)."""
    if value >= 64:
        return value - 128
    return value


def _unsigned_from_signed(value: int) -> int:
    """Convert signed value to offset-64 (0-127)."""
    if value < 0:
        return value + 128
    return value


def _decode_14bit(msb: int, lsb: int) -> int:
    """Decode 14-bit value from two 7-bit bytes."""
    return (msb << 7) | lsb


def _encode_14bit(value: int) -> Tuple[int, int]:
    """Encode 14-bit value into two 7-bit bytes."""
    msb = (value >> 7) & 0x7F
    lsb = value & 0x7F
    return msb, lsb


class JP8080Patch:
    """Represents a single JP-8080 program/patch."""

    LFO1_WAVES = ["Triangle", "Saw", "Square", "S/H"]
    LFO2_DEPTH_SELECT = ["Pitch", "Filter", "Amplifier"]
    LFO_ENV_DEST = ["OSC1+2", "OSC2", "X-MOD Depth"]

    OSC1_WAVES = ["SuperSaw", "TWM", "Feedback", "Noise", "Pulse", "Saw", "Triangle"]
    OSC2_WAVES = ["Pulse", "Triangle", "Saw", "Noise"]

    FILTER_TYPES = ["HPF", "BPF", "LPF"]
    FILTER_SLOPES = ["-12dB", "-24dB"]

    PAN_MODES = ["Off", "Auto Pan", "Manual Pan"]

    MULTI_FX_TYPES = [
        "SuperChorusSlow", "SuperChorusFast", "Chorus1", "Chorus2",
        "Flanger", "ShortDelay", "ShortDelayFB", "ShortDelayRev",
        "Overdrive", "Distortion1", "Distortion2", "Distortion3", "Distortion4"
    ]

    DELAY_TYPES = ["PanningL->R", "Delay", "PanningL<-R", "Delay2", "MonoLong"]

    def __init__(self, data: bytes):
        if len(data) < PATCH_SIZE:
            raise ValueError(f"Patch data must be at least {PATCH_SIZE} bytes, got {len(data)}")
        self.raw_data = data[:PATCH_SIZE]
        self._parse()

    def _parse(self) -> None:
        """Parse patch data and extract key parameters."""
        d = self.raw_data

        # Patch name (16 ASCII characters, 0x00-0x0F)
        self.name = d[0:16].decode("ascii", errors="replace").rstrip()

        # LFO1 (0x10-0x12)
        self.lfo1_waveform = self.LFO1_WAVES[d[0x10] & 0x03] if d[0x10] < 4 else f"LFO1({d[0x10]})"
        self.lfo1_rate = d[0x11]
        self.lfo1_fade = d[0x12]

        # LFO2 (0x13-0x14)
        self.lfo2_rate = d[0x13]
        self.lfo2_depth_select = self.LFO2_DEPTH_SELECT[d[0x14]] if d[0x14] < 3 else f"LFO2Sel({d[0x14]})"

        # Ring mod, cross mod, oscillator balance (0x15-0x17)
        self.ring_mod_switch = bool(d[0x15])
        self.cross_mod_depth = d[0x16]
        self.osc_balance = _signed_offset64(d[0x17])

        # LFO & Envelope destination (0x18)
        self.lfo_env_dest = self.LFO_ENV_DEST[d[0x18]] if d[0x18] < 3 else f"Dest({d[0x18]})"

        # Oscillators (0x1E-0x26)
        osc1_wave_idx = d[0x1E]
        self.osc1_waveform = self.OSC1_WAVES[osc1_wave_idx] if osc1_wave_idx < 7 else f"OSC1({osc1_wave_idx})"
        self.osc1_ctrl1 = d[0x1F]
        self.osc1_ctrl2 = d[0x20]

        osc2_wave_idx = d[0x21]
        self.osc2_waveform = self.OSC2_WAVES[osc2_wave_idx] if osc2_wave_idx < 4 else f"OSC2({osc2_wave_idx})"
        self.osc2_sync = bool(d[0x22])
        self.osc2_range = d[0x23] - 0x19  # -WIDE (-25) to +WIDE (+25), stored as 0x00-0x32
        self.osc2_fine = d[0x24] - 50  # -50 to +50 cents

        # Filter (0x27-0x32)
        filt_type_idx = d[0x27]
        self.filter_type = self.FILTER_TYPES[filt_type_idx] if filt_type_idx < 3 else f"Filt({filt_type_idx})"
        self.filter_slope = self.FILTER_SLOPES[d[0x28]] if d[0x28] < 2 else f"Slope({d[0x28]})"
        self.filter_cutoff = d[0x29]
        self.filter_resonance = d[0x2A]
        self.filter_keyfollow = _signed_offset64(d[0x2B])

        # Multi FX & Delay (0x3D-0x42)
        mfx_type_idx = d[0x3D]
        self.multi_fx_type = self.MULTI_FX_TYPES[mfx_type_idx] if mfx_type_idx < 13 else f"MFX({mfx_type_idx})"
        self.multi_fx_level = d[0x3E]

        delay_type_idx = d[0x3F]
        self.delay_type = self.DELAY_TYPES[delay_type_idx] if delay_type_idx < 5 else f"Delay({delay_type_idx})"
        self.delay_time = d[0x40]
        self.delay_feedback = d[0x41]
        self.delay_level = d[0x42]

        # Voice settings (0x45-0x48)
        self.portamento_switch = bool(d[0x45])
        self.portamento_time = d[0x46]
        self.mono_switch = bool(d[0x47])
        self.legato_switch = bool(d[0x48])

    def summary_dict(self) -> Dict[str, Any]:
        """Return summary of key patch parameters."""
        return {
            "name": self.name,
            "oscillators": {
                "osc1_wave": self.osc1_waveform,
                "osc2_wave": self.osc2_waveform,
                "balance": self.osc_balance,
            },
            "filter": {
                "type": self.filter_type,
                "cutoff": self.filter_cutoff,
                "resonance": self.filter_resonance,
            },
            "effects": {
                "multi_fx": self.multi_fx_type,
                "delay": self.delay_type,
            },
            "voice": {
                "mono": self.mono_switch,
                "legato": self.legato_switch,
                "portamento": self.portamento_switch,
            },
        }

    def summary_text(self) -> str:
        """Return human-readable text summary."""
        mono_legato = ""
        if self.mono_switch:
            mono_legato = "MONO"
            if self.legato_switch:
                mono_legato += "+LEGATO"

        return (
            f"[{self.name}]\n"
            f"     OSC: {self.osc1_waveform:12} Filter: {self.filter_type:6} "
            f"FX: {self.multi_fx_type:16} {mono_legato}"
        )


def extract_full_parameters(patch: JP8080Patch) -> Dict[str, Any]:
    """Extract all patch parameters into a structured dictionary."""
    d = patch.raw_data

    result = {
        "name": patch.name,

        # LFOs
        "lfo1": {
            "waveform": patch.lfo1_waveform,
            "rate": d[0x11],
            "fade": d[0x12],
        },
        "lfo2": {
            "rate": d[0x13],
            "depth_select": patch.lfo2_depth_select,
        },

        # Modulation
        "modulation": {
            "ring_mod_switch": patch.ring_mod_switch,
            "cross_mod_depth": d[0x16],
            "osc_balance": patch.osc_balance,
            "lfo_env_dest": patch.lfo_env_dest,
            "osc_lfo1_depth": _signed_offset64(d[0x19]),
            "pitch_lfo2_depth": _signed_offset64(d[0x1A]),
        },

        # Pitch envelope
        "pitch_env": {
            "depth": _signed_offset64(d[0x1B]),
            "attack": d[0x1C],
            "decay": d[0x1D],
        },

        # Oscillators
        "osc1": {
            "waveform": patch.osc1_waveform,
            "ctrl1": d[0x1F],
            "ctrl2": d[0x20],
        },
        "osc2": {
            "waveform": patch.osc2_waveform,
            "sync_switch": patch.osc2_sync,
            "range": patch.osc2_range,
            "fine": patch.osc2_fine,
            "ctrl1": d[0x25],
            "ctrl2": d[0x26],
        },

        # Filter
        "filter": {
            "type": patch.filter_type,
            "slope": patch.filter_slope,
            "cutoff": d[0x29],
            "resonance": d[0x2A],
            "keyfollow": patch.filter_keyfollow,
            "lfo1_depth": _signed_offset64(d[0x2C]),
            "lfo2_depth": _signed_offset64(d[0x2D]),
        },

        # Filter envelope (EG1)
        "eg1": {
            "depth": _signed_offset64(d[0x2E]),
            "attack": d[0x2F],
            "decay": d[0x30],
            "sustain": d[0x31],
            "release": d[0x32],
        },

        # Amplifier
        "amp": {
            "level": d[0x33],
            "lfo1_depth": _signed_offset64(d[0x34]),
            "lfo2_depth": _signed_offset64(d[0x35]),
        },

        # Amp envelope (EG2)
        "eg2": {
            "attack": d[0x36],
            "decay": d[0x37],
            "sustain": d[0x38],
            "release": d[0x39],
        },

        # Tone control and pan
        "tone": {
            "pan_mode": JP8080Patch.PAN_MODES[d[0x3A]] if d[0x3A] < 3 else f"Pan({d[0x3A]})",
            "bass": _signed_offset64(d[0x3B]),
            "treble": _signed_offset64(d[0x3C]),
        },

        # Effects
        "effects": {
            "multi_fx": {
                "type": patch.multi_fx_type,
                "level": d[0x3E],
            },
            "delay": {
                "type": patch.delay_type,
                "time": d[0x40],
                "feedback": d[0x41],
                "level": d[0x42],
            },
        },

        # Pitch bend and portamento
        "pitch": {
            "bend_range_up": d[0x43],
            "bend_range_down": d[0x44],
            "portamento_switch": patch.portamento_switch,
            "portamento_time": d[0x46],
        },

        # Voice settings
        # Note: Roland addresses decode as: (byte3 << 7) | byte4
        # e.g., "00 00 01 73" = (1 << 7) + 0x73 = 128 + 115 = 243
        "voice": {
            "mono_switch": patch.mono_switch,
            "legato_switch": patch.legato_switch,
            "osc_shift": d[0x49] - 2,  # -2 to +2 octaves
            "unison_switch": bool(d[243]),  # Roland addr: 00 00 01 73
            "unison_detune": d[244],  # Roland addr: 00 00 01 74
        },

        # Patch gain and other settings
        "settings": {
            "patch_gain": d[245],  # Roland addr: 00 00 01 75 (0=0dB, 1=+6dB, 2=+12dB)
            "ext_trigger_switch": bool(d[246]),  # Roland addr: 00 00 01 76
            "ext_trigger_dest": d[247],  # Roland addr: 00 00 01 77 (0=Filter, 1=Amp, 2=Filter&Amp)
        },

        # Store raw data for round-trip testing
        "system": {
            "base_patch": list(d[:PATCH_SIZE])
        },
    }

    return result


def slot_name(index: int) -> str:
    """Return human-readable slot name (A11..B88) for a 1-based index."""
    if not 1 <= index <= 128:
        raise ValueError("Slot index must be in range 1..128")

    zero_based = index - 1
    bank = "A" if zero_based < 64 else "B"
    slot_in_bank = zero_based % 64
    row = (slot_in_bank // 8) + 1
    col = (slot_in_bank % 8) + 1

    return f"{bank}{row}{col}"


def load_patch_from_sysex(path: Path) -> Tuple[SysexHeader, JP8080Patch, int]:
    """Load a single patch from a SysEx file."""
    data = path.read_bytes()
    header, payload, address = decode_roland_sysex(data)

    if len(payload) < PATCH_SIZE:
        raise ValueError(f"Payload too small: {len(payload)} bytes, expected {PATCH_SIZE}")

    patch = JP8080Patch(payload)
    return header, patch, address


def parse_sysex_file(path: str | Path) -> List[JP8080Patch]:
    """Parse SysEx file and return list of patches."""
    data = Path(path).read_bytes()
    patches = []

    # Check if this is a single patch or bulk dump
    try:
        header, patch, _ = load_patch_from_sysex(Path(path))
        return [patch]
    except:
        # Try parsing as bulk dump (multiple patches)
        # For now, we'll implement single patch support
        # Bulk dump support can be added later if needed
        raise ValueError("Bulk dump parsing not yet implemented. Please use individual patch files.")


def select_patches(
    patches: Sequence[JP8080Patch], patch_index: Optional[int] = None
) -> List[Tuple[int, JP8080Patch]]:
    """Select patches to process."""
    if patch_index is None:
        return list(enumerate(patches, start=1))

    if not 1 <= patch_index <= len(patches):
        raise ValueError(f"Patch index {patch_index} out of range (1..{len(patches)})")

    return [(patch_index, patches[patch_index - 1])]


def analyse_patches(patches: Sequence[JP8080Patch]) -> Dict[str, Any]:
    """Analyze a collection of patches and return statistics."""
    if not patches:
        return {"patch_count": 0}

    name_tokens: Dict[str, int] = {}
    for p in patches:
        tokens = [tok.lower() for tok in p.name.replace("_", " ").split() if tok]
        for tok in tokens:
            name_tokens[tok] = name_tokens.get(tok, 0) + 1

    def summary(values: Iterable[int]) -> Dict[str, float]:
        seq = list(values)
        if not seq:
            return {}
        return {
            "min": float(min(seq)),
            "max": float(max(seq)),
            "mean": float(round(mean(seq), 2)),
            "median": float(median(seq)),
        }

    mono_enabled = [p for p in patches if getattr(p, "mono_switch", False)]

    return {
        "patch_count": len(patches),
        "names": {
            "avg_length": round(mean(len(p.name) for p in patches), 2),
            "top_tokens": sorted(name_tokens.items(), key=lambda kv: kv[1], reverse=True)[:10],
        },
        "oscillators": {
            "osc1_waves": _counter([(p.osc1_waveform, 1) for p in patches]),
            "osc2_waves": _counter([(p.osc2_waveform, 1) for p in patches]),
        },
        "filters": {
            "types": _counter([(p.filter_type, 1) for p in patches]),
            "cutoff": summary(p.filter_cutoff for p in patches),
            "resonance": summary(p.filter_resonance for p in patches),
        },
        "effects": {
            "multi_fx_types": _counter([(p.multi_fx_type, 1) for p in patches]),
            "delay_types": _counter([(p.delay_type, 1) for p in patches]),
        },
        "voice": {
            "mono_count": len(mono_enabled),
            "mono_pct": round((len(mono_enabled) / len(patches)) * 100, 1),
        },
    }


def _counter(items: Iterable[Tuple[str, int]]) -> List[Tuple[str, int]]:
    """Count occurrences and return sorted list."""
    counter: Dict[str, int] = {}
    for key, value in items:
        counter[key] = counter.get(key, 0) + value
    return sorted(counter.items(), key=lambda kv: kv[1], reverse=True)


def encode_patch_to_sysex(
    patch_data: bytes, address: int = 0x02000000, device_id: int = 0x10
) -> bytes:
    """
    Encode patch data into a Roland SysEx message.
    Default address 0x02000000 is User Patch area.
    """
    if len(patch_data) != PATCH_SIZE:
        raise ValueError(f"Patch data must be exactly {PATCH_SIZE} bytes")

    return encode_roland_sysex(address, patch_data, device_id)


def _from_offset64(value: int) -> int:
    """Convert offset-64 value to signed."""
    return _signed_offset64(value)


def _to_offset64(value: int) -> int:
    """Convert signed value to offset-64."""
    return _unsigned_from_signed(value)
