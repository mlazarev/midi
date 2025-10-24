#!/usr/bin/env python3
"""
Shared MS2000 SysEx decoding/encoding utilities.

This module centralises all logic for reading, decoding, analysing, exporting,
and repairing Korg MS2000/MS2000R System Exclusive data so that higher-level
tools (CLI wrappers, scripts, docs) can rely on a single source of truth.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from statistics import mean, median
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

PATCH_SIZE = 254


@dataclass
class SysexHeader:
    manufacturer: int
    midi_channel: int
    device: int
    function: int


def decode_korg_7bit(encoded_data: bytes) -> bytes:
    """Decode Korg's 7-to-8 bit encoding scheme."""
    decoded = bytearray()
    i = 0

    while i < len(encoded_data):
        msb_byte = encoded_data[i]
        remaining = len(encoded_data) - (i + 1)
        chunk_len = min(7, remaining)
        for j in range(chunk_len):
            data_byte = encoded_data[i + 1 + j]
            msb = (msb_byte >> (6 - j)) & 0x01
            full_byte = (msb << 7) | (data_byte & 0x7F)
            decoded.append(full_byte)
        i += 1 + chunk_len

    return bytes(decoded)


def encode_korg_7bit(decoded_data: bytes, *, variant: str = "v1") -> bytes:
    """Encode 8-bit data back into Korg's 7-bit SysEx format."""
    encoded = bytearray()
    i = 0
    while i < len(decoded_data):
        chunk = decoded_data[i : i + 7]
        if not chunk:
            break
        msb_byte = 0
        for j, byte in enumerate(chunk):
            if byte & 0x80:
                if variant == "v2":
                    msb_byte |= 1 << j
                else:
                    msb_byte |= 1 << (6 - j)
        encoded.append(msb_byte)
        for byte in chunk:
            encoded.append(byte & 0x7F)
        i += 7
    return bytes(encoded)


class MS2000Patch:
    """Represents a single MS2000 program/patch."""

    VOICE_MODES = ["Single", "Split", "Layer", "Vocoder"]
    SCALE_KEYS = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    DELAY_TYPES = ["StereoDelay", "CrossDelay", "L/R Delay"]
    MOD_TYPES = ["Cho/Flg", "Ensemble", "Phaser"]
    ARP_TYPES = ["Up", "Down", "Alt1", "Alt2", "Random", "Trigger"]

    def __init__(self, data: bytes):
        if len(data) < PATCH_SIZE:
            raise ValueError(f"Patch data must be {PATCH_SIZE} bytes, got {len(data)}")
        self.raw_data = data[:PATCH_SIZE]
        self._parse()

    def _parse(self) -> None:
        d = self.raw_data
        self.name = d[0:12].decode("ascii", errors="replace").rstrip()
        self.timbre_voice = (d[16] >> 6) & 0x03
        self.voice_mode = self.VOICE_MODES[(d[16] >> 4) & 0x03]
        scale_key_idx = (d[17] >> 4) & 0x0F
        self.scale_key = (
            self.SCALE_KEYS[scale_key_idx] if scale_key_idx < 12 else str(scale_key_idx)
        )
        self.scale_type = d[17] & 0x0F
        self.split_point = d[18]
        self.delay_sync = bool((d[19] >> 7) & 0x01)
        self.delay_timebase = d[19] & 0x0F
        self.delay_time = d[20]
        self.delay_depth = d[21]
        delay_type_idx = d[22]
        self.delay_type = (
            self.DELAY_TYPES[delay_type_idx]
            if delay_type_idx < len(self.DELAY_TYPES)
            else str(delay_type_idx)
        )
        self.mod_speed = d[23]
        self.mod_depth = d[24]
        mod_type_idx = d[25]
        self.mod_type = (
            self.MOD_TYPES[mod_type_idx]
            if mod_type_idx < len(self.MOD_TYPES)
            else str(mod_type_idx)
        )
        self.eq_hi_freq = d[26]
        self.eq_hi_gain = d[27]
        self.eq_low_freq = d[28]
        self.eq_low_gain = d[29]
        self.arp_tempo = (d[30] << 8) | d[31]
        self.arp_on = bool((d[32] >> 7) & 0x01)
        self.arp_latch = bool((d[32] >> 6) & 0x01)
        self.arp_target = (d[32] >> 4) & 0x03
        self.arp_keysync = bool(d[32] & 0x01)
        arp_type_idx = d[33] & 0x0F
        self.arp_type = (
            self.ARP_TYPES[arp_type_idx]
            if arp_type_idx < len(self.ARP_TYPES)
            else str(arp_type_idx)
        )
        self.arp_range = ((d[33] >> 4) & 0x0F) + 1

    def summary_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "voice_mode": self.voice_mode,
            "scale_key": self.scale_key,
            "scale_type": self.scale_type,
            "delay": {
                "type": self.delay_type,
                "sync": self.delay_sync,
                "time": self.delay_time,
                "depth": self.delay_depth,
            },
            "mod": {
                "type": self.mod_type,
                "speed": self.mod_speed,
                "depth": self.mod_depth,
            },
            "arp": {
                "on": self.arp_on,
                "type": self.arp_type,
                "range": self.arp_range,
                "tempo": self.arp_tempo,
            },
        }

    def summary_text(self) -> str:
        lines = [
            f"[{self.name}]",
            f"     Mode: {self.voice_mode:7} Delay: {self.delay_type:12} "
            f"Mod: {self.mod_type:9} Arp: {'ON' if self.arp_on else 'OFF'}",
        ]
        return "\n".join(lines)


def _map_choice(options: Sequence[str], index: int, label: str) -> str:
    if 0 <= index < len(options):
        return options[index]
    return f"{label}({index})"


def _signed(value: int) -> int:
    return value - 128 if value >= 64 else value


def _extract_timbre(d: bytes, offset: int) -> Dict[str, Any]:
    osc1_wave_val = d[offset + 7] & 0x07
    osc2_byte = d[offset + 12]
    osc2_wave_val = osc2_byte & 0x03
    osc2_mod_val = (osc2_byte >> 4) & 0x03
    filt_type_val = d[offset + 19] & 0x03
    lfo1_wave_val = d[offset + 38] & 0x03
    lfo2_wave_val = d[offset + 41] & 0x03

    return {
        "voice": {
            "portamento_time": d[offset + 5],
        },
        "osc1": {
            "wave": _map_choice(
                ["Saw", "Pulse", "Triangle", "Sine", "Vox Wave", "DWGS", "Noise", "Audio In"],
                osc1_wave_val,
                "OSC1",
            ),
            "wave_value": osc1_wave_val,
            "ctrl1": d[offset + 8],
            "ctrl2": d[offset + 9],
            "dwgs_wave": d[offset + 10] + 1,
        },
        "osc2": {
            "wave": _map_choice(["Saw", "Square", "Triangle"], osc2_wave_val, "OSC2"),
            "wave_value": osc2_wave_val,
            "modulation": _map_choice(
                ["Off", "Ring", "Sync", "Ring+Sync"], osc2_mod_val, "MOD"
            ),
            "mod_value": osc2_mod_val,
            "semitone": _signed(d[offset + 13] & 0x7F),
            "tune": _signed(d[offset + 14] & 0x7F),
        },
        "mixer": {
            "osc1_level": d[offset + 16],
            "osc2_level": d[offset + 17],
            "noise_level": d[offset + 18],
        },
        "filter": {
            "type": _map_choice(
                ["24dB LPF", "12dB LPF", "12dB BPF", "12dB HPF"], filt_type_val, "FILTER"
            ),
            "type_value": filt_type_val,
            "cutoff": d[offset + 20],
            "resonance": d[offset + 21],
            "eg1_intensity": _signed(d[offset + 22] & 0x7F),
            "kbd_track": _signed(d[offset + 23] & 0x7F),
        },
        "amp": {
            "level": d[offset + 24],
            "panpot": _signed(d[offset + 25] & 0x7F),
            "switch": "GATE" if (d[offset + 26] & 0x01) else "EG2",
            "distortion": bool(d[offset + 27] & 0x01),
            "kbd_track": _signed(d[offset + 28] & 0x7F),
            "velocity_sense": _signed(d[offset + 29] & 0x7F),
        },
        "eg1": {
            "attack": d[offset + 30],
            "decay": d[offset + 31],
            "sustain": d[offset + 32],
            "release": d[offset + 33],
        },
        "eg2": {
            "attack": d[offset + 34],
            "decay": d[offset + 35],
            "sustain": d[offset + 36],
            "release": d[offset + 37],
        },
        "lfo1": {
            "wave": _map_choice(["Saw", "Square", "Triangle", "S/H"], lfo1_wave_val, "LFO1"),
            "wave_value": lfo1_wave_val,
            "frequency": d[offset + 39],
            "tempo_sync": bool(d[offset + 40] & 0x01),
        },
        "lfo2": {
            "wave": _map_choice(["Saw", "Square+", "Sine", "S/H"], lfo2_wave_val, "LFO2"),
            "wave_value": lfo2_wave_val,
            "frequency": d[offset + 42],
            "tempo_sync": bool(d[offset + 43] & 0x01),
        },
        "patch": {
            f"patch{i+1}": {
                "source": _map_choice(
                    ["EG1", "EG2", "LFO1", "LFO2", "Velocity", "KeyTrack", "MIDI1", "MIDI2"],
                    d[offset + 44 + (i * 3)] & 0x07,
                    "SRC",
                ),
                "destination": _map_choice(
                    ["PITCH", "OSC2PITCH", "OSC1CTRL1", "OSC1CTRL2", "CUTOFF", "RESONANCE", "LFO1FREQ", "LFO2FREQ"],
                    d[offset + 45 + (i * 3)] & 0x07,
                    "DEST",
                ),
                "intensity": _signed(d[offset + 46 + (i * 3)] & 0x7F),
            }
            for i in range(4)
        },
    }


def extract_full_parameters(patch: MS2000Patch) -> Dict[str, Any]:
    d = patch.raw_data
    voice_mode = patch.voice_mode
    result = {
        "name": patch.name,
        "voice_mode": voice_mode,
        "scale": {
            "key": patch.scale_key,
            "type": patch.scale_type,
        },
        "effects": {
            "delay": {
                "type": patch.delay_type,
                "sync": patch.delay_sync,
                "time": patch.delay_time,
                "depth": patch.delay_depth,
            },
            "mod_fx": {
                "type": patch.mod_type,
                "speed": patch.mod_speed,
                "depth": patch.mod_depth,
            },
            "eq": {
                "hi_freq": patch.eq_hi_freq,
                "hi_gain": patch.eq_hi_gain,
                "low_freq": patch.eq_low_freq,
                "low_gain": patch.eq_low_gain,
            },
        },
        "arpeggiator": {
            "on": patch.arp_on,
            "tempo": patch.arp_tempo,
            "latch": patch.arp_latch,
            "target": patch.arp_target,
            "keysync": patch.arp_keysync,
            "type": patch.arp_type,
            "range": patch.arp_range,
        },
        "timbre1": _extract_timbre(d, 38),
        "raw_hex": d[:PATCH_SIZE].hex(),
    }
    if voice_mode in ("Split", "Layer"):
        result["timbre2"] = _extract_timbre(d, 134)
    return result


def slot_name(index: int) -> str:
    """Return human-readable slot name (A01..H16) for a 1-based index."""
    if not 1 <= index <= 128:
        raise ValueError("Slot index must be in range 1..128")
    zero_based = index - 1
    bank = chr(ord("A") + (zero_based // 16))
    num = (zero_based % 16) + 1
    return f"{bank}{num:02d}"


def load_bank(path: Path) -> Tuple[SysexHeader, List[MS2000Patch]]:
    data = path.read_bytes()
    if len(data) < 6:
        raise ValueError("File too small to contain a valid SysEx header")
    if data[0] != 0xF0:
        raise ValueError("Missing SysEx start byte (F0)")
    if data[1] != 0x42:
        raise ValueError("Not a Korg SysEx file (manufacturer ID)")
    if data[3] != 0x58:
        raise ValueError("Not an MS2000 SysEx file (device ID)")
    header = SysexHeader(
        manufacturer=data[1],
        midi_channel=data[2] & 0x0F,
        device=data[3],
        function=data[4],
    )
    if data[-1] != 0xF7:
        raise ValueError("SysEx message missing terminating F7 byte")
    encoded_stream = data[5:-1]
    decoded_stream = decode_korg_7bit(encoded_stream)
    patches = []
    for i in range(0, len(decoded_stream), PATCH_SIZE):
        chunk = decoded_stream[i : i + PATCH_SIZE]
        if len(chunk) < PATCH_SIZE:
            break
        patches.append(MS2000Patch(chunk))
    return header, patches


def parse_sysex_file(path: str | Path) -> List[MS2000Patch]:
    _, patches = load_bank(Path(path))
    return patches


def select_patches(
    patches: Sequence[MS2000Patch], patch_index: Optional[int] = None
) -> List[Tuple[int, MS2000Patch]]:
    if patch_index is None:
        return list(enumerate(patches, start=1))
    if not 1 <= patch_index <= len(patches):
        raise ValueError(f"Patch index {patch_index} out of range (1..{len(patches)})")
    return [(patch_index, patches[patch_index - 1])]


def analyse_patches(patches: Sequence[MS2000Patch]) -> Dict[str, Any]:
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

    arp_enabled = [p for p in patches if getattr(p, "arp_on", False)]

    return {
        "patch_count": len(patches),
        "names": {
            "avg_length": round(mean(len(p.name) for p in patches), 2),
            "top_tokens": sorted(name_tokens.items(), key=lambda kv: kv[1], reverse=True)[:10],
        },
        "voice_modes": _counter([(p.voice_mode, 1) for p in patches]),
        "effects": {
            "delay_types": _counter([(p.delay_type, 1) for p in patches]),
            "mod_types": _counter([(p.mod_type, 1) for p in patches]),
        },
        "arpeggiator": {
            "enabled_count": len(arp_enabled),
            "enabled_pct": round((len(arp_enabled) / len(patches)) * 100, 1),
            "types": _counter([(p.arp_type, 1) for p in arp_enabled]),
            "tempo": summary(p.arp_tempo for p in arp_enabled),
        },
        "parameters": {
            "mod_speed": summary(p.mod_speed for p in patches),
            "mod_depth": summary(p.mod_depth for p in patches),
            "delay_time": summary(p.delay_time for p in patches),
            "delay_depth": summary(p.delay_depth for p in patches),
        },
    }


def _counter(items: Iterable[Tuple[str, int]]) -> List[Tuple[str, int]]:
    counter: Dict[str, int] = {}
    for key, value in items:
        counter[key] = counter.get(key, 0) + value
    return sorted(counter.items(), key=lambda kv: kv[1], reverse=True)


def analyse_single_patch(patch: MS2000Patch) -> Dict[str, Any]:
    return {
        "name": patch.name,
        "voice_mode": patch.voice_mode,
        "delay": patch.delay_type,
        "mod": patch.mod_type,
        "arp_on": patch.arp_on,
        "arp_tempo": patch.arp_tempo,
    }


def export_single_program(
    bank_path: Path,
    patches: Sequence[MS2000Patch],
    patch_index: int,
    *,
    variant: str = "v1",
    output: Optional[Path] = None,
) -> Path:
    if not 1 <= patch_index <= len(patches):
        raise ValueError(f"Patch index {patch_index} out of range (1..{len(patches)})")
    raw = patches[patch_index - 1].raw_data[:PATCH_SIZE]
    encoded = encode_korg_7bit(raw, variant=variant)
    syx = bytes([0xF0, 0x42, 0x30, 0x58, 0x40]) + encoded + bytes([0xF7])
    if output is None:
        output = bank_path.with_name(
            bank_path.stem + f"_P{patch_index:03d}_current_{variant}.syx"
        )
    output.write_bytes(syx)
    return output


def repair_sysex(
    input_path: Path,
    *,
    output_path: Optional[Path] = None,
    pad_to_128: bool = True,
) -> Dict[str, Any]:
    data = bytearray(input_path.read_bytes())
    report: Dict[str, Any] = {"input": str(input_path), "changes": []}
    if len(data) < 6 or data[0] != 0xF0 or data[1] != 0x42 or data[3] != 0x58:
        raise ValueError("Not a valid MS2000 SysEx file")
    if data[-1] != 0xF7:
        for i in range(len(data) - 1, -1, -1):
            if data[i] != 0x00:
                data = data[: i + 1]
                break
        data.append(0xF7)
        report["changes"].append("appended_f7")
    if data[4] == 0x4C and pad_to_128:
        encoded_section = data[5:-1]
        decoded = decode_korg_7bit(encoded_section)
        patch_count = len(decoded) // PATCH_SIZE
        report["patch_count"] = patch_count
        if patch_count < 128:
            report["warning"] = (
                "Bank has fewer than 128 patches; manual padding required for hardware."
            )
    out_path = output_path or input_path
    out_path.write_bytes(data)
    report["output"] = str(out_path)
    return report


def patches_from_json(records: Sequence[Dict[str, Any]]) -> List[MS2000Patch]:
    patches: List[MS2000Patch] = []
    for idx, record in enumerate(records, start=1):
        raw_hex = record.get("raw_hex")
        if not raw_hex:
            raise ValueError(f"Record {idx} missing 'raw_hex' field required for encoding")
        raw_bytes = bytes.fromhex(raw_hex)
        if len(raw_bytes) != PATCH_SIZE:
            raise ValueError(
                f"Record {idx} raw_hex length {len(raw_bytes)} != {PATCH_SIZE} bytes"
            )
        patches.append(MS2000Patch(raw_bytes))
    return patches


def encode_bank_from_json(
    records: Sequence[Dict[str, Any]],
    *,
    midi_channel: int = 0,
    function: int = 0x4C,
) -> bytes:
    if not 0 <= midi_channel <= 0x0F:
        raise ValueError("MIDI channel must be in range 0..15")
    header = bytes([0xF0, 0x42, 0x30 | midi_channel, 0x58, function])
    chunks = [bytes.fromhex(rec["raw_hex"]) for rec in records]
    for idx, chunk in enumerate(chunks, start=1):
        if len(chunk) != PATCH_SIZE:
            raise ValueError(f"Record {idx} raw_hex does not represent {PATCH_SIZE} bytes")
    decoded_stream = b"".join(chunks)
    if len(decoded_stream) % PATCH_SIZE != 0:
        raise ValueError("Decoded stream size is not a multiple of patch size")
    encoded_stream = encode_korg_7bit(decoded_stream)
    return header + encoded_stream + bytes([0xF7])


def json_records_from_path(path: Path) -> List[Dict[str, Any]]:
    data = json.loads(path.read_text())
    if isinstance(data, dict):
        return [data]
    if not isinstance(data, list):
        raise ValueError("JSON must be an object or array of objects")
    return data


__all__ = [
    "SysexHeader",
    "MS2000Patch",
    "decode_korg_7bit",
    "encode_korg_7bit",
    "parse_sysex_file",
    "load_bank",
    "select_patches",
    "slot_name",
    "extract_full_parameters",
    "analyse_patches",
    "analyse_single_patch",
    "export_single_program",
    "repair_sysex",
    "json_records_from_path",
    "patches_from_json",
    "encode_bank_from_json",
]
