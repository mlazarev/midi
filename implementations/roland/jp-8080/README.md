# Roland JP-8080 SysEx Tools & Documentation

Complete tools and documentation for working with Roland JP-8080 synthesizer MIDI System Exclusive (SysEx) files.

## Overview

The Roland JP-8080 is a virtual analog synthesizer featuring:
- Digital oscillators with multiple waveform types (SuperSaw, PWM, etc.)
- 2 oscillators per voice + ring/cross modulation
- Multi-mode resonant filter (LPF, BPF, HPF)
- Built-in effects (Multi-FX, Delay)
- Ribbon controller with assignable parameters
- Motion control (real-time parameter recording)

This implementation provides tools to decode, analyze, and work with JP-8080 patch data stored in SysEx format.

## Directory Structure

```
jp-8080/
├── README.md                    # This file
├── docs/                        # Documentation
│   ├── SYSEX_STRUCTURE.txt     # Complete SysEx format reference
│   └── JP-8080_OM.txt          # MIDI implementation (from manual)
├── tools/                       # Python tooling
│   ├── jp8080_cli.py           # Unified CLI (inspect/decode/analyze)
│   ├── lib/                    # Shared libraries
│   │   └── jp8080_core.py      # Decode/encode utilities
│   └── scripts/                # Standalone helpers
│       ├── copy_patch.py
│       └── roundtrip_test.py
├── patches/                     # Patch files
│   └── factory/                # (Factory presets - to be added)
└── examples/                    # Example outputs
    └── (Decoded patches - to be added)
```

## Quick Start

### Inspect a SysEx file
```bash
python3 implementations/roland/jp-8080/tools/jp8080_cli.py \
        inspect patch.syx
```

Example output:
```
SysEx Header:
  Manufacturer: Roland (0x41)
  Device ID: 0x10
  Model ID: 00 06 (JP-8080)
  Command: 0x12
  Address: 0x02000000

[Spit'n Slide Bs]
     OSC: SuperSaw     Filter: LPF    FX: SuperChorusSlow  MONO+LEGATO
```

### Decode a SysEx file to JSON
```bash
python3 implementations/roland/jp-8080/tools/jp8080_cli.py \
        decode patch.syx -o patch.json
```

### Analyze patch parameters
```bash
python3 implementations/roland/jp-8080/tools/jp8080_cli.py \
        analyze patch.syx
```

Example output:
```
Patch Analysis: Spit'n Slide Bs
============================================================

Oscillators:
  OSC1 Waveform: SuperSaw
  OSC2 Waveform: Saw
  Balance: -32

Filter:
  Type: LPF
  Cutoff: 85
  Resonance: 64

Effects:
  Multi FX: SuperChorusSlow
  Delay: Delay

Voice Settings:
  Mono: YES
  Legato: YES
  Portamento: NO
```

### Send SysEx to JP-8080
```bash
# List available MIDI outputs (requires: pip install mido python-rtmidi)
python3 tools/send_sysex.py --list-outputs

# Send a JP-8080 patch or bulk dump
python3 tools/send_sysex.py \
        --file implementations/roland/jp-8080/examples/wc_olo_garb_jp8080.syx \
        --out "JP-8080" --delay-ms 50
```

Dependencies for MIDI send:
```bash
pip install mido python-rtmidi
```

## JP-8000 Compatibility

The JP-8080 shares its analog-modelling engine and MIDI implementation with the
JP-8000 keyboard. Many JP-8000 librarian exports contain multiple DT1 packets
per patch (performance common + parts + the editable patch bytes at addresses
`01 00 40 00` / `01 00 42 00`) and the patch payload itself is nine bytes shorter
because the rack-only unison/gain parameters do not exist.

All CLI commands now run through a loader that reassembles those JP-8000 files:
- Every DT1 packet in a file is decoded, patch segments are stitched back together,
  and the shorter payloads are padded to the JP-8080’s 248-byte layout.
- Both the modern CLI (`jp8080_cli.py`) and the legacy scripts (`roundtrip_test.py`,
  `extract_from_bulk.py`, etc.) therefore accept JP-8000 and JP-8080 dumps without
  any manual conversions.
- The additional JP-8080-only parameters (unison, detune, gain, external trigger)
  are initialised to safe defaults when importing a JP-8000 patch so you can still
  encode the JSON back to a valid JP-8080 SysEx file.

If you point any command at a full JP-8080 bulk dump, use `extract_from_bulk.py`
first to split out the 128 user-bank patches; the compatibility shim only targets
the multi-packet “single patch” files that JP-8000 editors typically produce.

## SysEx File Format

### Message Structure (DT1 - Data Set 1)

```
F0 41 <dev> 00 06 12 <addr*4> <data...> <sum> F7
│  │  │     │  │  │  │        │          │    │
│  │  │     │  │  │  │        │          │    └─ End of SysEx
│  │  │     │  │  │  │        │          └────── Checksum
│  │  │     │  │  │  │        └───────────────── Patch data (248 bytes)
│  │  │     │  │  │  └────────────────────────── Address (4 bytes)
│  │  │     │  │  └───────────────────────────── Command: 12 = DT1
│  │  │     │  └──────────────────────────────── Model ID: 00 06 = JP-8080
│  │  │     └─────────────────────────────────── Device ID (default: 10)
│  │  └───────────────────────────────────────── Manufacturer: 41 = Roland
│  └──────────────────────────────────────────── SysEx Start
```

### Checksum Calculation

Roland SysEx uses a checksum for data integrity:

```python
checksum = (128 - (sum(address_bytes + data_bytes) % 128)) & 0x7F
```

Example:
```python
def calculate_checksum(data: bytes) -> int:
    total = sum(data) % 128
    return (128 - total) & 0x7F
```

### Patch Structure

Each patch is **248 bytes** (0x178 hex):

| Offset | Parameter              | Range       | Description                 |
|--------|------------------------|-------------|-----------------------------|
| 0x00   | Patch Name             | ASCII       | 16 characters               |
| 0x10   | LFO1 Waveform          | 0-3         | TRI, SAW, SQR, S/H          |
| 0x11   | LFO1 Rate              | 0-127       |                             |
| 0x1E   | OSC1 Waveform          | 0-6         | SuperSaw, TWM, Feedback...  |
| 0x21   | OSC2 Waveform          | 0-3         | Pulse, Triangle, Saw, Noise |
| 0x27   | Filter Type            | 0-2         | HPF, BPF, LPF               |
| 0x29   | Cutoff Frequency       | 0-127       |                             |
| 0x2A   | Resonance              | 0-127       |                             |
| 0x2F-0x32 | Filter EG (ADSR)    | 0-127 each  | Attack, Decay, Sustain, Rel |
| 0x36-0x39 | Amp EG (ADSR)       | 0-127 each  | Attack, Decay, Sustain, Rel |
| 0x3D   | Multi Effects Type     | 0-12        | Chorus, Flanger, Dist...    |
| 0x3F   | Delay Type             | 0-4         | Panning, Mono, etc.         |
| 0x47   | Mono Switch            | 0-1         | OFF, ON                     |
| 0x48   | Legato Switch          | 0-1         | OFF, ON                     |

See [SYSEX_STRUCTURE.txt](docs/SYSEX_STRUCTURE.txt) for complete memory map.

## Address Map

### User Patch Area (Base Address: 02 00 00 00)

Patches are stored with 512-byte spacing (0x200):

| Patch  | Address      | Slot    |
|--------|--------------|---------|
| A11    | 02 00 00 00  | 1       |
| A12    | 02 00 02 00  | 2       |
| A13    | 02 00 04 00  | 3       |
| ...    | ...          | ...     |
| A88    | 02 00 7E 00  | 64      |
| B11    | 02 01 00 00  | 65      |
| B12    | 02 01 02 00  | 66      |
| ...    | ...          | ...     |
| B88    | 02 01 7E 00  | 128     |

## Tools Documentation

### jp8080_cli.py

Unified command-line interface with the following subcommands:

#### inspect
Display a quick human-readable overview of a patch.

```bash
python3 jp8080_cli.py inspect patch.syx [--json]
```

#### decode
Export full patch parameters as JSON.

```bash
python3 jp8080_cli.py decode patch.syx [-o output.json]
```

#### analyze
Show detailed parameter analysis.

```bash
python3 jp8080_cli.py analyze patch.syx [--json]
```

### copy_patch.py

Copy a patch from one SysEx file to another, optionally changing the address.

```bash
python3 scripts/copy_patch.py input.syx -o output.syx [--address 0x02000200]
```

Useful for:
- Duplicating patches
- Moving patches to different slots
- Backing up individual patches

### Sending SysEx

Use the shared `tools/send_sysex.py` helper to transmit JP-8080 patches or bulk dumps. It automatically splits multi-message `.syx` files, preserving the two-packet-per-patch layout documented above.

```bash
python3 tools/send_sysex.py --list-outputs
python3 tools/send_sysex.py --file implementations/roland/jp-8080/examples/wc_olo_garb_jp8080.syx --out "JP-8080" --delay-ms 50
```

Tips:
- JP-8080 MIDI interfaces often show up as `EDIROL`, `JP8080`, or similar—pass any substring to `--out`.
- Set `--delay-ms` to 50–100 when sending large bulk dumps to avoid overrunning slower DIN interfaces.
- The tool enforces F0...F7 framing, catching truncated exports before they reach the synth.

### roundtrip_test.py

Test SysEx encoding/decoding for accuracy.

```bash
python3 scripts/roundtrip_test.py patch.syx [-v]
```

This tool:
1. Reads a SysEx file
2. Decodes the patch data
3. Re-encodes the patch data
4. Compares byte-for-byte with the original

Example output:
```
Testing: patch.syx
------------------------------------------------------------
Patch name: Spit'n Slide Bs
Address: 0x02000000
Device ID: 0x10

Comparing original and reconstructed SysEx...

1. Header (first 10 bytes):
✓ Header matches

2. Patch data payload:
✓ Patch data matches (248 bytes)

3. Checksum:
✓ Checksum matches (0x6D)

4. SysEx terminator (F7):
✓ Terminator present

5. Complete message:
✓ Complete round-trip successful!

============================================================
ROUND-TRIP TEST: PASSED ✓
============================================================
```

## Technical Details

### Device Identification

The JP-8080 responds to Universal Device Inquiry:

**Request:**
```
F0 7E 7F 06 01 F7
```

**Response:**
```
F0 7E <ch> 06 02 41 00 06 00 <ver> F7
│     │        │  │     │  └──────────── Version info
│     │        │  │     └─────────────── Model ID (00 06)
│     │        │  └───────────────────── Manufacturer (41 = Roland)
│     │        └──────────────────────── Identity Reply
│     └───────────────────────────────── MIDI Channel
└─────────────────────────────────────── Universal SysEx
```

### Command IDs

| Command | Hex | Description               |
|---------|-----|---------------------------|
| RQ1     | 11  | Data Request              |
| DT1     | 12  | Data Set (Send to synth)  |

### Parameter Encoding

#### Signed Values (Offset-64)
Many parameters use offset-64 encoding for signed values:
- 0x00 (0) = -64
- 0x40 (64) = 0 (center)
- 0x7F (127) = +63

Examples:
- Oscillator Balance: 0-127 maps to OSC1 ←→ OSC2
- Filter Keyfollow: 0-127 maps to -64 to +63
- Tone Bass/Treble: 0-127 maps to -64 to +63

#### 14-bit Values
Some control parameters (marked with # in the manual) use 14-bit encoding:
- First byte: MSB (bit 7 of value)
- Second byte: LSB (bits 0-6 of value)

### Preset Banks

The JP-8080 contains:
- **User Bank**: 128 patches (A11-B88) - User-editable
- **Preset Banks**: 384 patches (P1-P3) - Read-only factory presets
- **Card Banks**: Up to 2048 patches (C01-C64) - With memory card

## JSON Parameter Format

Decoded patches are exported in a structured JSON format with consistent
parameter names matching the MS2000 implementation where applicable:

```json
{
  "name": "Spit'n Slide Bs",
  "lfo1": {
    "waveform": "Saw",
    "rate": 64,
    "fade": 0
  },
  "osc1": {
    "waveform": "SuperSaw",
    "ctrl1": 127,
    "ctrl2": 64
  },
  "osc2": {
    "waveform": "Saw",
    "sync_switch": false,
    "range": -12,
    "fine": 0
  },
  "filter": {
    "type": "LPF",
    "slope": "-24dB",
    "cutoff": 85,
    "resonance": 64
  },
  "eg1": {
    "depth": 42,
    "attack": 0,
    "decay": 64,
    "sustain": 64,
    "release": 32
  },
  "eg2": {
    "attack": 0,
    "decay": 32,
    "sustain": 127,
    "release": 24
  },
  "effects": {
    "multi_fx": {
      "type": "SuperChorusSlow",
      "level": 64
    },
    "delay": {
      "type": "Delay",
      "time": 64,
      "feedback": 32,
      "level": 48
    }
  }
}
```

Parameter names follow these conventions:
- **osc1, osc2**: Oscillators (not "oscillator1")
- **eg1, eg2**: Envelope generators (Filter EG and Amp EG)
- **lfo1, lfo2**: Low-frequency oscillators

## Known Limitations

1. **Bulk Dumps**: Currently, the tools support individual patch files. Full
   bank dump support (all 128 patches in one file) will be added in a future
   update.

2. **Performance Data**: Performance mode parameters (split/layer settings)
   are not yet supported. Focus is on individual patch data.

3. **Motion Control**: Motion control recording/playback data is not yet
   decoded.

## Resources

### Official Documentation
- [Roland JP-8080 Product Page](https://www.roland.com/global/products/jp-8080/)
- Owner's Manual (MIDI Implementation section included in docs/)

### Related Tools
- [SysEx Librarian](https://www.snoize.com/SysExLibrarian/) - Mac OS X
- [MIDI-OX](http://www.midiox.com/) - Windows
- [SendMIDI](https://github.com/gbevin/SendMIDI) - Command-line MIDI tools

### Related Synths
- **JP-8000**: Keyboard version with identical sound engine and MIDI implementation
- Both synths share the same patch format and can exchange patches

## Contributing

Contributions welcome! Possible enhancements:
- Bulk dump support (send/receive all 128 patches)
- Performance mode parameter editing
- Motion control data decode/encode
- Patch editor GUI
- Random patch generator
- Preset bank dumps from factory ROMs

## License

MIT License - see [LICENSE](../../../LICENSE) for details.

Tools and documentation are open source. Roland JP-8080 specifications
and factory patches remain property of Roland Corporation.

---

**Note:** This implementation is for educational and archival purposes.
Always respect copyright and licensing of commercial patches and content.
