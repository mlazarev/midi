# MS2000 Parameter Decoder

The unified CLI wraps every decoder and encoder capability for the Korg MS2000/MS2000R. Use it to read a full bank, inspect individual programs, or rebuild `.syx` files after editing JSON.

```bash
python3 implementations/korg/ms2000/tools/ms2000_cli.py decode \
  implementations/korg/ms2000/patches/factory/FactoryBanks.syx \
  implementations/korg/ms2000/examples/factory_banks.json
```

_Note:_ The JSON emitted by the CLI also includes `"system": {"base_patch": [...]}` (254 integers). The array is omitted above for readability; keep it in place to ensure motion and vocoder bytes survive round-trips.

Key features:
- Human‑readable JSON covering voice mode, global FX, both timbres, envelopes, LFOs, modulation matrix, and motion data placeholders.
- Round‑trip safe: every field that is emitted is consumed by the encoder; no `raw_hex` is required.
- Works on full banks or a single program (`--patch-index`).
- Offset‑64 aware: OSC2 pitch offsets, filter modulation depths, amp pan/velocity, and modulation intensities are translated with the dedicated `_to_offset64/_from_offset64` helpers introduced in v1.3.0, so JSON values map exactly to hardware.

## Decoded Parameters

Each patch is 254 bytes. The decoder exposes:

- **Program metadata** — name, voice mode, timbre voice selector, scale (key/type/split point).
- **Global FX** — delay (type, sync flag, timebase, time, depth), modulation FX (type/speed/depth), EQ (hi/low freq & gain).
- **Arpeggiator** — tempo (16‑bit BPM), latch, target, key sync, type, range.
- **Timbre data** (timbre1 and timbre2 for split/layer patches):
  - Voice settings (portamento).
  - Oscillators: OSC1 waveform/dwgs/controls, OSC2 waveform/modulation/pitch offset.
  - Mixer levels (OSC1/OSC2/Noise).
  - Filter: type, cutoff, resonance, EG1 intensity, keyboard tracking.
  - Amplifier: level, panpot, EG switch, distortion, keyboard tracking, velocity response.
  - EG1 / EG2 ADSR envelopes.
  - LFO1 / LFO2: waveform, frequency, tempo sync flag, serialized tempo value.
  - Modulation matrix: four patches (source, destination, signed intensity).
- **System block** — `system.base_patch` retains the original 254 decoded bytes (motion sequencer lanes, vocoder config, reserved regions). Leave it untouched unless you intend to manipulate those areas directly.
- **Offset-64 fields** — Any parameter documented as `-64..+63` (e.g., panpot, EG intensity, patch intensity) is stored in JSON as the human-readable signed value; the encoder converts it to the MS2000’s offset-64 byte form automatically.

## Encoding Back to SysEx

After editing the JSON you can rebuild a bank. If you want to reuse header metadata (MIDI channel, function byte), supply the original bank as a template.

```bash
python3 implementations/korg/ms2000/tools/ms2000_cli.py encode \
  implementations/korg/ms2000/examples/factory_banks.json \
  /tmp/factory_roundtrip.syx \
  --template implementations/korg/ms2000/patches/factory/FactoryBanks.syx
```

The encoder now derives all bytes from the structured fields and only uses preserved motion/vocoder regions when present. `raw_hex` has been completely removed from the workflow.

## Sample JSON Record

```json
{
  "index": 1,
  "slot": "A01",
  "name": "Sunday Pad",
  "voice_mode": "Single",
  "timbre_voice": 1,
  "scale": {
    "key": "C",
    "type": 0,
    "split_point": 60
  },
  "effects": {
    "delay": {
      "type": "L/R Delay",
      "sync": false,
      "timebase": 0,
      "time": 38,
      "depth": 88
    },
    "mod_fx": {
      "type": "Cho/Flg",
      "speed": 18,
      "depth": 32
    },
    "eq": {
      "hi_freq": 20,
      "hi_gain": 64,
      "low_freq": 15,
      "low_gain": 61
    }
  },
  "arpeggiator": {
    "on": false,
    "tempo": 120,
    "latch": false,
    "target": 0,
    "keysync": false,
    "type": "Up",
    "range": 1
  },
  "timbre1": {
    "voice": {
      "portamento_time": 25
    },
    "osc1": {
      "wave": "Sine",
      "wave_value": 3,
      "ctrl1": 0,
      "ctrl2": 0,
      "dwgs_wave": 11
    },
    "osc2": {
      "wave": "Triangle",
      "wave_value": 2,
      "modulation": "Off",
      "mod_value": 0,
      "semitone": -12,
      "tune": -5
    },
    "mixer": {
      "osc1_level": 127,
      "osc2_level": 95,
      "noise_level": 18
    },
    "filter": {
      "type": "12dB LPF",
      "type_value": 1,
      "cutoff": 52,
      "resonance": 18,
      "eg1_intensity": -56,
      "kbd_track": -64
    },
    "amp": {
      "level": 127,
      "panpot": 0,
      "switch": "EG2",
      "distortion": false,
      "kbd_track": -64,
      "velocity_sense": -64
    },
    "eg1": {
      "attack": 5,
      "decay": 65,
      "sustain": 120,
      "release": 95
    },
    "eg2": {
      "attack": 2,
      "decay": 68,
      "sustain": 127,
      "release": 115
    },
    "lfo1": {
      "wave": "Triangle",
      "wave_value": 2,
      "frequency": 12,
      "tempo_sync": false,
      "tempo_value": 0
    },
    "lfo2": {
      "wave": "Sine",
      "wave_value": 2,
      "frequency": 68,
      "tempo_sync": false,
      "tempo_value": 0
    },
    "patch": {
      "patch1": {
        "source": "LFO1",
        "destination": "OSC2PITCH",
        "intensity": -29
      },
      "patch2": {
        "source": "EG2",
        "destination": "OSC1CTRL1",
        "intensity": -52
      },
      "patch3": {
        "source": "EG1",
        "destination": "PITCH",
        "intensity": 0
      },
      "patch4": {
        "source": "EG1",
        "destination": "PITCH",
        "intensity": 0
      }
    }
  }
}
```

## Byte Offsets (Highlights)

- `0-11` – Program name (ASCII, space padded).
- `16` – Timbre voice (bits 6-7) and voice mode (bits 4-5).
- `19` – Delay sync flag (bit 7) and timebase (bits 0-3).
- `30-31` – Arp tempo MSB/LSB (full 16 bits, 20-300 BPM range).
- `38 onwards` – Timbre block; oscillator, filter, amp, EG, LFO, mod matrix.
- Motion sequencer lanes follow the timbre data; currently preserved but not surfaced.

Keep motion/vocoder bytes untouched for now—the encoder carries them forward until we expose them as structured data in a future release.
