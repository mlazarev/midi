import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from implementations.korg.ms2000.tools.lib.ms2000_core import (  # noqa: E402
    MS2000Patch,
    build_patch_bytes,
    extract_full_parameters,
    load_bank,
    slot_name,
    _from_offset64,
    _to_offset64,
)


def _edge_case_patch() -> dict:
    """Return a single timbre patch exercising offset-64 fields."""
    return {
        "name": "Unit Test Edge",
        "voice_mode": "Single",
        "timbre_voice": 1,
        "effects": {
            "delay": {"type": "L/R Delay", "sync": False, "time": 50, "depth": 64, "timebase": 0},
            "mod_fx": {"type": "Cho/Flg", "speed": 20, "depth": 30},
            "eq": {"hi_freq": 20, "hi_gain": 64, "low_freq": 15, "low_gain": 61},
        },
        "arpeggiator": {"on": False, "tempo": 120, "latch": False, "target": 0, "keysync": False, "type": "Up", "range": 1},
        "timbre1": {
            "voice": {"portamento_time": 3},
            "osc1": {"wave": "Saw", "ctrl1": 10, "ctrl2": 20},
            "osc2": {"wave": "Square", "semitone": 12, "tune": -5, "modulation": "Off"},
            "mixer": {"osc1_level": 90, "osc2_level": 80, "noise_level": 10},
            "filter": {
                "type": "12dB LPF",
                "cutoff": 70,
                "resonance": 20,
                "eg1_intensity": -21,
                "velocity_sense": -9,
                "kbd_track": 18,
            },
            "amp": {
                "level": 100,
                "panpot": 0,
                "switch": "EG2",
                "distortion": False,
                "velocity_sense": -17,
                "kbd_track": 11,
            },
            "eg1": {"attack": 5, "decay": 40, "sustain": 90, "release": 60},
            "eg2": {"attack": 3, "decay": 50, "sustain": 100, "release": 70},
            "lfo1": {"wave": "Triangle", "frequency": 30, "tempo_sync": False, "tempo_value": 0},
            "lfo2": {"wave": "Sine", "frequency": 45, "tempo_sync": False, "tempo_value": 0},
            "patch": {
                "patch1": {"source": "EG1", "destination": "PITCH", "intensity": -63},
                "patch2": {"source": "EG2", "destination": "OSC2PITCH", "intensity": 0},
                "patch3": {"source": "LFO1", "destination": "CUTOFF", "intensity": 15},
                "patch4": {"source": "MIDI1", "destination": "RESONANCE", "intensity": 63},
            },
        },
    }


def test_offset64_helpers_edge_cases():
    assert _to_offset64(-64) == 0
    assert _to_offset64(0) == 64
    assert _to_offset64(63) == 127
    assert _from_offset64(0) == -64
    assert _from_offset64(64) == 0
    assert _from_offset64(127) == 63

    with pytest.raises(ValueError):
        _to_offset64(-65)
    with pytest.raises(ValueError):
        _to_offset64(64)

    for value in range(-64, 64):
        byte = _to_offset64(value)
        assert _from_offset64(byte) == value


def test_build_patch_bytes_sets_expected_offset64_bytes():
    record = _edge_case_patch()
    patch_bytes = build_patch_bytes(record)

    timbre_offset = 38
    assert patch_bytes[timbre_offset + 13] == 12 + 64  # OSC2 semitone
    assert patch_bytes[timbre_offset + 14] == 64 - 5   # OSC2 tune
    assert patch_bytes[timbre_offset + 22] == 64 - 21  # Filter EG1 intensity
    assert patch_bytes[timbre_offset + 23] == 64 - 9   # Filter velocity sense
    assert patch_bytes[timbre_offset + 24] == 64 + 18  # Filter keyboard track
    assert patch_bytes[timbre_offset + 26] == 64       # Amp panpot center
    assert patch_bytes[timbre_offset + 28] == 64 - 17  # Amp velocity sense
    assert patch_bytes[timbre_offset + 29] == 64 + 11  # Amp keyboard track

    for route_idx, expected in enumerate([-63, 0, 15, 63], start=1):
        base_pos = timbre_offset + 44 + (route_idx - 1) * 2
        assert patch_bytes[base_pos + 1] == _to_offset64(expected)


def test_patch_roundtrip_preserves_offset_fields():
    record = _edge_case_patch()
    encoded = build_patch_bytes(record)
    patch = MS2000Patch(encoded)
    extracted = extract_full_parameters(patch)
    rebuilt = build_patch_bytes(extracted)
    assert rebuilt == encoded


def test_factory_patch_offset64_bytes_match():
    bank_path = Path("implementations/korg/ms2000/patches/factory/FactoryBanks.syx")
    _, patches = load_bank(bank_path)
    first_patch = patches[0]
    parsed = extract_full_parameters(first_patch)
    raw = first_patch.raw_data
    t1 = parsed["timbre1"]
    offset = 38

    assert raw[offset + 13] == _to_offset64(t1["osc2"]["semitone"], -24, 24)
    assert raw[offset + 14] == _to_offset64(t1["osc2"]["tune"])
    assert raw[offset + 22] == _to_offset64(t1["filter"]["eg1_intensity"])
    assert raw[offset + 23] == _to_offset64(t1["filter"]["velocity_sense"])
    assert raw[offset + 24] == _to_offset64(t1["filter"]["kbd_track"])
    assert raw[offset + 26] == _to_offset64(t1["amp"]["panpot"])
    assert raw[offset + 28] == _to_offset64(t1["amp"]["velocity_sense"])
    assert raw[offset + 29] == _to_offset64(t1["amp"]["kbd_track"])

    for route_idx in range(1, 5):
        route = t1["patch"][f"patch{route_idx}"]
        base_pos = offset + 44 + (route_idx - 1) * 2
        assert raw[base_pos + 1] == _to_offset64(route["intensity"])


def test_slot_name_helper_bounds():
    assert slot_name(1) == "A01"
    assert slot_name(16) == "A16"
    assert slot_name(17) == "B01"

    with pytest.raises(ValueError):
        slot_name(0)
    with pytest.raises(ValueError):
        slot_name(129)
