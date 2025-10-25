#!/usr/bin/env python3
"""
Shared MS2000 SysEx decoding/encoding utilities.

This module centralises all logic for reading, decoding, analysing, exporting,
and repairing Korg MS2000/MS2000R System Exclusive data so that higher-level
tools (CLI wrappers, scripts, docs) can rely on a single source of truth.
"""

from __future__ import annotations

import json
from collections import Counter
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


OSC1_WAVES = ["Saw", "Pulse", "Triangle", "Sine", "Vox Wave", "DWGS", "Noise", "Audio In"]
OSC2_WAVES = ["Saw", "Square", "Triangle"]
MOD_SELECT = ["Off", "Ring", "Sync", "Ring+Sync"]
FILTER_TYPES = ["24dB LPF", "12dB LPF", "12dB BPF", "12dB HPF"]
LFO1_WAVES = ["Saw", "Square", "Triangle", "S/H"]
LFO2_WAVES = ["Saw", "Square+", "Sine", "S/H"]
PATCH_SOURCE_NAMES = ["EG1", "EG2", "LFO1", "LFO2", "Velocity", "KeyTrack", "MIDI1", "MIDI2"]
PATCH_DEST_NAMES = ["PITCH", "OSC2PITCH", "OSC1CTRL1", "OSC1CTRL2", "CUTOFF", "RESONANCE", "LFO1FREQ", "LFO2FREQ"]


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
            "semitone": _from_offset64(d[offset + 13] & 0x7F),
            "tune": _from_offset64(d[offset + 14] & 0x7F),
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
            "eg1_intensity": _from_offset64(d[offset + 22] & 0x7F),
            "velocity_sense": _from_offset64(d[offset + 23] & 0x7F),
            "kbd_track": _from_offset64(d[offset + 24] & 0x7F),
        },
        "amp": {
            "level": d[offset + 25],
            "panpot": _from_offset64(d[offset + 26] & 0x7F),
            "switch": "GATE" if (d[offset + 27] & 0x01) else "EG2",
            "distortion": bool(d[offset + 27] & 0x01),
            "kbd_track": _from_offset64(d[offset + 29] & 0x7F),
            "velocity_sense": _from_offset64(d[offset + 28] & 0x7F),
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
            "tempo_value": d[offset + 40],
        },
        "lfo2": {
            "wave": _map_choice(["Saw", "Square+", "Sine", "S/H"], lfo2_wave_val, "LFO2"),
            "wave_value": lfo2_wave_val,
            "frequency": d[offset + 42],
            "tempo_sync": bool(d[offset + 43] & 0x01),
            "tempo_value": d[offset + 43],
        },
        "patch": {
            f"patch{i+1}": {
                "source": _map_choice(
                    ["EG1", "EG2", "LFO1", "LFO2", "Velocity", "KeyTrack", "MIDI1", "MIDI2"],
                    d[offset + 44 + (i * 2)] & 0x0F,
                    "SRC",
                ),
                "destination": _map_choice(
                    ["PITCH", "OSC2PITCH", "OSC1CTRL1", "OSC1CTRL2", "CUTOFF", "RESONANCE", "LFO1FREQ", "LFO2FREQ"],
                    (d[offset + 44 + (i * 2)] >> 4) & 0x0F,
                    "DEST",
                ),
                "intensity": _from_offset64(d[offset + 45 + (i * 2)] & 0x7F),
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
        "timbre_voice": patch.timbre_voice,
        "scale": {
            "key": patch.scale_key,
            "type": patch.scale_type,
            "split_point": patch.split_point,
        },
        "effects": {
            "delay": {
                "type": patch.delay_type,
                "sync": patch.delay_sync,
                "time": patch.delay_time,
                "depth": patch.delay_depth,
                "timebase": patch.delay_timebase,
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
    }
    if voice_mode in ("Split", "Layer"):
        result["timbre2"] = _extract_timbre(d, 134)
    result["system"] = {"base_patch": list(d[:PATCH_SIZE])}
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


def _summarise(values: Iterable[int | float]) -> Dict[str, float]:
    seq = list(values)
    if not seq:
        return {}
    return {
        "count": len(seq),
        "min": min(seq),
        "max": max(seq),
        "mean": round(float(mean(seq)), 2),
        "median": round(float(median(seq)), 2),
    }


def _counter_series(counter: Counter) -> List[Tuple[Any, int]]:
    return counter.most_common()


def deep_analyse(records: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    total_patches = len(records)
    voice_modes = Counter()
    delay_types = Counter()
    delay_time: List[int] = []
    delay_depth: List[int] = []
    delay_sync = 0

    mod_types = Counter()
    mod_speed: List[int] = []
    mod_depth: List[int] = []

    eq_hi_freq: List[int] = []
    eq_hi_gain: List[int] = []
    eq_low_freq: List[int] = []
    eq_low_gain: List[int] = []

    arp_on = 0
    arp_types = Counter()
    arp_tempo: List[int] = []
    arp_target = Counter()

    osc1_wave = Counter()
    osc1_level: List[int] = []
    osc1_dwgs = Counter()

    osc2_wave = Counter()
    osc2_mod = Counter()
    osc2_semitone: List[int] = []
    osc2_tune: List[int] = []
    osc2_level: List[int] = []

    noise_level: List[int] = []
    portamento_time: List[int] = []

    filter_types = Counter()
    filter_cutoff: List[int] = []
    filter_resonance: List[int] = []
    filter_eg_intensity: List[int] = []
    filter_kbd_track: List[int] = []

    amp_level: List[int] = []
    amp_pan: List[int] = []
    amp_velocity: List[int] = []
    amp_kbd_track: List[int] = []
    amp_distortion = 0

    eg1_attack: List[int] = []
    eg1_decay: List[int] = []
    eg1_sustain: List[int] = []
    eg1_release: List[int] = []

    eg2_attack: List[int] = []
    eg2_decay: List[int] = []
    eg2_sustain: List[int] = []
    eg2_release: List[int] = []

    lfo1_wave = Counter()
    lfo1_frequency: List[int] = []
    lfo1_sync = 0

    lfo2_wave = Counter()
    lfo2_frequency: List[int] = []
    lfo2_sync = 0

    mod_sources = Counter()
    mod_destinations = Counter()
    mod_intensity: List[int] = []

    timbre_count = 0

    for record in records:
        voice_modes[record["voice_mode"]] += 1

        effects = record["effects"]
        delay = effects["delay"]
        delay_types[delay["type"]] += 1
        delay_time.append(delay["time"])
        delay_depth.append(delay["depth"])
        if delay.get("sync"):
            delay_sync += 1

        mod_fx = effects["mod_fx"]
        mod_types[mod_fx["type"]] += 1
        mod_speed.append(mod_fx["speed"])
        mod_depth.append(mod_fx["depth"])

        eq = effects["eq"]
        eq_hi_freq.append(eq["hi_freq"])
        eq_hi_gain.append(eq["hi_gain"])
        eq_low_freq.append(eq["low_freq"])
        eq_low_gain.append(eq["low_gain"])

        arp = record["arpeggiator"]
        if arp["on"]:
            arp_on += 1
            arp_types[arp["type"]] += 1
            arp_tempo.append(arp["tempo"])
            arp_target[arp["target"]] += 1

        timbres = [record["timbre1"]]
        if "timbre2" in record:
            timbres.append(record["timbre2"])

        for timbre in timbres:
            timbre_count += 1
            voice = timbre.get("voice", {})
            if "portamento_time" in voice:
                portamento_time.append(voice["portamento_time"])

            osc1 = timbre["osc1"]
            osc1_wave[osc1["wave"]] += 1
            osc1_level.append(timbre["mixer"]["osc1_level"])
            if osc1["wave"] == "DWGS":
                osc1_dwgs[osc1.get("dwgs_wave", 0)] += 1

            osc2 = timbre["osc2"]
            osc2_wave[osc2["wave"]] += 1
            osc2_mod[osc2["modulation"]] += 1
            osc2_semitone.append(osc2["semitone"])
            osc2_tune.append(osc2["tune"])
            osc2_level.append(timbre["mixer"]["osc2_level"])

            noise_level.append(timbre["mixer"]["noise_level"])

            filt = timbre["filter"]
            filter_types[filt["type"]] += 1
            filter_cutoff.append(filt["cutoff"])
            filter_resonance.append(filt["resonance"])
            filter_eg_intensity.append(filt["eg1_intensity"])
            filter_kbd_track.append(filt["kbd_track"])

            amp = timbre["amp"]
            amp_level.append(amp["level"])
            amp_pan.append(amp["panpot"])
            amp_velocity.append(amp["velocity_sense"])
            amp_kbd_track.append(amp.get("kbd_track", 0))
            if amp.get("distortion"):
                amp_distortion += 1

            eg1 = timbre["eg1"]
            eg1_attack.append(eg1["attack"])
            eg1_decay.append(eg1["decay"])
            eg1_sustain.append(eg1["sustain"])
            eg1_release.append(eg1["release"])

            eg2 = timbre["eg2"]
            eg2_attack.append(eg2["attack"])
            eg2_decay.append(eg2["decay"])
            eg2_sustain.append(eg2["sustain"])
            eg2_release.append(eg2["release"])

            lfo1 = timbre["lfo1"]
            lfo1_wave[lfo1["wave"]] += 1
            lfo1_frequency.append(lfo1["frequency"])
            if lfo1.get("tempo_sync"):
                lfo1_sync += 1

            lfo2 = timbre["lfo2"]
            lfo2_wave[lfo2["wave"]] += 1
            lfo2_frequency.append(lfo2["frequency"])
            if lfo2.get("tempo_sync"):
                lfo2_sync += 1

            for route in timbre["patch"].values():
                intensity = route["intensity"]
                if intensity != 0:
                    mod_sources[route["source"]] += 1
                    mod_destinations[route["destination"]] += 1
                    mod_intensity.append(intensity)

    return {
        "patch_count": total_patches,
        "timbre_count": timbre_count,
        "voice_modes": _counter_series(voice_modes),
        "effects": {
            "delay": {
                "type_counts": _counter_series(delay_types),
                "time": _summarise(delay_time),
                "depth": _summarise(delay_depth),
                "sync_percent": round((delay_sync / total_patches) * 100, 2) if total_patches else 0.0,
            },
            "mod": {
                "type_counts": _counter_series(mod_types),
                "speed": _summarise(mod_speed),
                "depth": _summarise(mod_depth),
            },
            "eq": {
                "hi_freq": _summarise(eq_hi_freq),
                "hi_gain": _summarise(eq_hi_gain),
                "low_freq": _summarise(eq_low_freq),
                "low_gain": _summarise(eq_low_gain),
            },
        },
        "arpeggiator": {
            "enabled_percent": round((arp_on / total_patches) * 100, 2) if total_patches else 0.0,
            "types": _counter_series(arp_types),
            "tempo": _summarise(arp_tempo),
            "targets": _counter_series(arp_target),
        },
        "oscillators": {
            "osc1": {
                "wave_counts": _counter_series(osc1_wave),
                "level": _summarise(osc1_level),
                "dwgs_waves": _counter_series(osc1_dwgs),
            },
            "osc2": {
                "wave_counts": _counter_series(osc2_wave),
                "modulation_counts": _counter_series(osc2_mod),
                "semitone": _summarise(osc2_semitone),
                "tune": _summarise(osc2_tune),
                "level": _summarise(osc2_level),
            },
        },
        "mixer": {
            "noise_level": _summarise(noise_level),
            "portamento_time": _summarise(portamento_time),
        },
        "filter": {
            "type_counts": _counter_series(filter_types),
            "cutoff": _summarise(filter_cutoff),
            "resonance": _summarise(filter_resonance),
            "eg_intensity": _summarise(filter_eg_intensity),
            "kbd_track": _summarise(filter_kbd_track),
        },
        "amp": {
            "level": _summarise(amp_level),
            "pan": _summarise(amp_pan),
            "velocity_sense": _summarise(amp_velocity),
            "kbd_track": _summarise(amp_kbd_track),
            "distortion_count": amp_distortion,
        },
        "eg1": {
            "attack": _summarise(eg1_attack),
            "decay": _summarise(eg1_decay),
            "sustain": _summarise(eg1_sustain),
            "release": _summarise(eg1_release),
        },
        "eg2": {
            "attack": _summarise(eg2_attack),
            "decay": _summarise(eg2_decay),
            "sustain": _summarise(eg2_sustain),
            "release": _summarise(eg2_release),
        },
        "lfo": {
            "lfo1": {
                "wave_counts": _counter_series(lfo1_wave),
                "frequency": _summarise(lfo1_frequency),
                "sync_percent": round((lfo1_sync / timbre_count) * 100, 2) if timbre_count else 0.0,
            },
            "lfo2": {
                "wave_counts": _counter_series(lfo2_wave),
                "frequency": _summarise(lfo2_frequency),
                "sync_percent": round((lfo2_sync / timbre_count) * 100, 2) if timbre_count else 0.0,
            },
        },
        "mod_matrix": {
            "source_counts": _counter_series(mod_sources),
            "destination_counts": _counter_series(mod_destinations),
            "intensity": _summarise(mod_intensity),
        },
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


def _clamp_byte(value: Any) -> int:
    return max(0, min(255, int(value)))


def _lookup(options: Sequence[str], value: Any, default: int = 0) -> int:
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        stripped = value.strip()
        if stripped.startswith("-") and stripped[1:].isdigit():
            return int(stripped)
        if stripped.isdigit():
            return int(stripped)
        if "(" in stripped and stripped.endswith(")"):
            inner = stripped[stripped.rfind("(") + 1 : -1]
            if inner.isdigit():
                return int(inner)
        try:
            return options.index(value)
        except ValueError:
            return default
    return default


def _to_signed_7bit(value: Any) -> int:
    """DEPRECATED: This was incorrectly used for MS2000 offset-64 encoding."""
    value = int(value)
    if value < -64 or value > 63:
        raise ValueError(f"Signed 7-bit value out of range: {value}")
    return (value + 128) & 0x7F if value < 0 else value & 0x7F


def _to_offset64(value: Any, min_val: int = -64, max_val: int = 63) -> int:
    """Encode MS2000 offset-64 format: value range min_val~0~max_val maps to 0~64~(64+max_val)."""
    value = int(value)
    if value < min_val or value > max_val:
        raise ValueError(f"Offset-64 value out of range {min_val}~{max_val}: {value}")
    return value + 64


def _from_offset64(byte_value: int) -> int:
    """Decode MS2000 offset-64 format: byte 0~64~127 maps to -64~0~63."""
    return byte_value - 64


def _write_masked(data: bytearray, index: int, value: int, mask: int) -> None:
    current = data[index]
    data[index] = (current & ~mask) | (value & mask)


def build_patch_bytes(record: Dict[str, Any]) -> bytes:
    system = record.get("system", {})
    base_patch = system.get("base_patch")
    if base_patch:
        base_bytes = [int(b) & 0xFF for b in base_patch[:PATCH_SIZE]]
        data = bytearray(base_bytes)
        if len(data) < PATCH_SIZE:
            data.extend(b"\x00" * (PATCH_SIZE - len(data)))
    else:
        data = bytearray(PATCH_SIZE)

    name = (record.get("name") or "")[:12]
    if all(ord(ch) < 128 for ch in name):
        encoded_name = name.encode("ascii")[:12].ljust(12, b" ")
        data[0:12] = encoded_name

    voice_mode = record.get("voice_mode", "Single")
    voice_idx = _lookup(MS2000Patch.VOICE_MODES, voice_mode)
    timbre_voice = int(record.get("timbre_voice", 1)) & 0x03
    combined_voice = ((timbre_voice & 0x03) << 6) | ((voice_idx & 0x03) << 4)
    _write_masked(data, 16, combined_voice, 0xF0)

    scale = record.get("scale", {})
    scale_key = scale.get("key", "C")
    key_idx = _lookup(MS2000Patch.SCALE_KEYS, scale_key)
    scale_type = int(scale.get("type", 0)) & 0x0F
    data[17] = ((key_idx & 0x0F) << 4) | scale_type
    data[18] = _clamp_byte(scale.get("split_point", 0))

    effects = record.get("effects", {})
    delay = effects.get("delay", {})
    delay_sync = bool(delay.get("sync", False))
    delay_timebase = int(delay.get("timebase", 0)) & 0x0F
    data[19] = (0x80 if delay_sync else 0x00) | delay_timebase
    data[20] = _clamp_byte(delay.get("time", 0))
    data[21] = _clamp_byte(delay.get("depth", 0))
    data[22] = _lookup(MS2000Patch.DELAY_TYPES, delay.get("type", "StereoDelay"))

    mod_fx = effects.get("mod_fx", {})
    data[23] = _clamp_byte(mod_fx.get("speed", 0))
    data[24] = _clamp_byte(mod_fx.get("depth", 0))
    data[25] = _lookup(MS2000Patch.MOD_TYPES, mod_fx.get("type", "Cho/Flg"))

    eq = effects.get("eq", {})
    data[26] = _clamp_byte(eq.get("hi_freq", 0))
    data[27] = _clamp_byte(eq.get("hi_gain", 0))
    data[28] = _clamp_byte(eq.get("low_freq", 0))
    data[29] = _clamp_byte(eq.get("low_gain", 0))

    arp = record.get("arpeggiator", {})
    tempo = int(arp.get("tempo", 120))
    data[30] = (tempo >> 8) & 0xFF
    data[31] = tempo & 0xFF
    byte32 = 0
    if arp.get("on", False):
        byte32 |= 0x80
    if arp.get("latch", False):
        byte32 |= 0x40
    byte32 |= (int(arp.get("target", 0)) & 0x03) << 4
    if arp.get("keysync", False):
        byte32 |= 0x01
    data[32] = byte32
    arp_type_idx = _lookup(MS2000Patch.ARP_TYPES, arp.get("type", "Up"))
    arp_range = max(1, min(16, int(arp.get("range", 1))))
    data[33] = ((arp_range - 1) << 4) | (arp_type_idx & 0x0F)

    def encode_timbre(timbre: Dict[str, Any], offset: int) -> None:
        if not timbre:
            return
        voice = timbre.get("voice", {})
        data[offset + 5] = _clamp_byte(voice.get("portamento_time", 0))

        osc1 = timbre.get("osc1", {})
        wave1_idx = _lookup(OSC1_WAVES, osc1.get("wave"), osc1.get("wave_value", 0))
        _write_masked(data, offset + 7, wave1_idx, 0x07)
        data[offset + 8] = _clamp_byte(osc1.get("ctrl1", 0))
        data[offset + 9] = _clamp_byte(osc1.get("ctrl2", 0))
        dwgs_raw = osc1.get("dwgs_wave")
        if dwgs_raw is not None:
            dwgs = int(dwgs_raw) - 1
            if 0 <= dwgs <= 63:
                _write_masked(data, offset + 10, dwgs, 0x3F)

        osc2 = timbre.get("osc2", {})
        wave2_idx = _lookup(OSC2_WAVES, osc2.get("wave"), osc2.get("wave_value", 0))
        mod_idx = _lookup(MOD_SELECT, osc2.get("modulation", "Off"), osc2.get("mod_value", 0))
        _write_masked(data, offset + 12, wave2_idx, 0x03)
        _write_masked(data, offset + 12, (mod_idx & 0x03) << 4, 0x30)
        _write_masked(data, offset + 13, _to_offset64(osc2.get("semitone", 0), -24, 24), 0x7F)
        _write_masked(data, offset + 14, _to_offset64(osc2.get("tune", 0)), 0x7F)

        mixer = timbre.get("mixer", {})
        data[offset + 16] = _clamp_byte(mixer.get("osc1_level", 0))
        data[offset + 17] = _clamp_byte(mixer.get("osc2_level", 0))
        data[offset + 18] = _clamp_byte(mixer.get("noise_level", 0))

        filt = timbre.get("filter", {})
        filter_idx = _lookup(FILTER_TYPES, filt.get("type"), filt.get("type_value", 0))
        _write_masked(data, offset + 19, filter_idx, 0x03)
        data[offset + 20] = _clamp_byte(filt.get("cutoff", 0))
        data[offset + 21] = _clamp_byte(filt.get("resonance", 0))
        _write_masked(data, offset + 22, _to_offset64(filt.get("eg1_intensity", 0)), 0x7F)
        _write_masked(data, offset + 23, _to_offset64(filt.get("velocity_sense", 0)), 0x7F)
        _write_masked(data, offset + 24, _to_offset64(filt.get("kbd_track", 0)), 0x7F)

        amp = timbre.get("amp", {})
        data[offset + 25] = _clamp_byte(amp.get("level", 0))
        _write_masked(data, offset + 26, _to_offset64(amp.get("panpot", 0)), 0x7F)
        # Byte 27: Bit 6 = Amp Switch, Bit 0 = Distortion (both in same byte!)
        # Bit 6 also acts as "magic bit" for Single/Split modes (required for amp to work)
        gate_flag = 0x40 if str(amp.get("switch", "EG2")).upper() == "GATE" else 0x00
        distortion_flag = 0x01 if amp.get("distortion", False) else 0x00
        if voice_mode in ("Single", "Split"):
            # Single/Split modes: always set bit 6 (required), plus gate/distortion flags
            data[offset + 27] = 0x40 | gate_flag | distortion_flag
        else:
            # Layer/Vocoder modes: preserve existing bits, set gate/distortion flags
            data[offset + 27] = (data[offset + 27] & ~0x41) | gate_flag | distortion_flag
        _write_masked(data, offset + 28, _to_offset64(amp.get("velocity_sense", 0)), 0x7F)
        _write_masked(data, offset + 29, _to_offset64(amp.get("kbd_track", 0)), 0x7F)

        eg1 = timbre.get("eg1", {})
        data[offset + 30] = _clamp_byte(eg1.get("attack", 0))
        data[offset + 31] = _clamp_byte(eg1.get("decay", 0))
        data[offset + 32] = _clamp_byte(eg1.get("sustain", 0))
        data[offset + 33] = _clamp_byte(eg1.get("release", 0))

        eg2 = timbre.get("eg2", {})
        data[offset + 34] = _clamp_byte(eg2.get("attack", 0))
        data[offset + 35] = _clamp_byte(eg2.get("decay", 0))
        data[offset + 36] = _clamp_byte(eg2.get("sustain", 0))
        data[offset + 37] = _clamp_byte(eg2.get("release", 0))

        lfo1 = timbre.get("lfo1", {})
        lfo1_idx = _lookup(LFO1_WAVES, lfo1.get("wave"), lfo1.get("wave_value", 0))
        _write_masked(data, offset + 38, lfo1_idx, 0x03)
        data[offset + 39] = _clamp_byte(lfo1.get("frequency", 0))
        tempo1_raw = lfo1.get("tempo_value")
        if tempo1_raw is None:
            tempo_byte = 1 if lfo1.get("tempo_sync", False) else 0
        else:
            tempo_byte = int(tempo1_raw) & 0xFF
        if lfo1.get("tempo_sync", False):
            tempo_byte |= 0x01
        else:
            tempo_byte &= 0xFE
        data[offset + 40] = tempo_byte & 0xFF

        lfo2 = timbre.get("lfo2", {})
        lfo2_idx = _lookup(LFO2_WAVES, lfo2.get("wave"), lfo2.get("wave_value", 0))
        _write_masked(data, offset + 41, lfo2_idx, 0x03)
        data[offset + 42] = _clamp_byte(lfo2.get("frequency", 0))
        tempo2_raw = lfo2.get("tempo_value")
        if tempo2_raw is None:
            tempo_byte = 1 if lfo2.get("tempo_sync", False) else 0
        else:
            tempo_byte = int(tempo2_raw) & 0xFF
        if lfo2.get("tempo_sync", False):
            tempo_byte |= 0x01
        else:
            tempo_byte &= 0xFE
        data[offset + 43] = tempo_byte & 0xFF

        patch_matrix = timbre.get("patch", {})
        for route_idx in range(1, 5):
            route = patch_matrix.get(f"patch{route_idx}", {})
            base_pos = offset + 44 + (route_idx - 1) * 2
            src_idx = _lookup(PATCH_SOURCE_NAMES, route.get("source", "EG1"))
            dst_idx = _lookup(PATCH_DEST_NAMES, route.get("destination", "PITCH"))
            intensity = int(route.get("intensity", 0))
            # Source (bits 0-3) and Destination (bits 4-7) in same byte
            data[base_pos] = ((dst_idx & 0x0F) << 4) | (src_idx & 0x0F)
            data[base_pos + 1] = _to_offset64(intensity) & 0x7F

    encode_timbre(record.get("timbre1", {}), 38)
    if voice_mode in ("Split", "Layer"):
        encode_timbre(record.get("timbre2", {}), 134)

    return bytes(data)


def patches_from_json(records: Sequence[Dict[str, Any]]) -> List[MS2000Patch]:
    patches: List[MS2000Patch] = []
    for record in records:
        raw_bytes = build_patch_bytes(record)
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
    decoded_chunks = [build_patch_bytes(rec) for rec in records]
    decoded_stream = b"".join(decoded_chunks)
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
    "deep_analyse",
]
