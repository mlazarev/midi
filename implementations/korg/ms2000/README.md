# Korg MS2000 SysEx Tools & Documentation

Complete tools and documentation for working with Korg MS2000/MS2000R synthesizer MIDI System Exclusive (SysEx) files.

## Overview

The Korg MS2000 is a virtual analog synthesizer featuring:
- 4-voice polyphony
- 2 oscillators per voice + noise generator
- Resonant low-pass filter (MS-20 inspired)
- Built-in effects (Delay, Modulation, EQ)
- Vocoder mode
- Arpeggiator and motion sequencer

This implementation provides tools to decode, analyze, and work with MS2000 patch data stored in SysEx format.

## Directory Structure

```
ms2000/
├── README.md                    # This file
├── docs/                        # Documentation
│   ├── SYSEX_STRUCTURE.txt     # Complete SysEx format diagrams
│   └── MS2000_MIDIimp.TXT      # Official MIDI implementation chart
├── guides/                      # How‑to and analysis guides
│   └── PATCH_ANALYSIS_GUIDE.md # Techniques to analyze patch banks
├── tools/                       # Python tooling
│   ├── ms2000_cli.py          # Unified CLI (inspect/decode/analyze/compare/etc.)
│   ├── lib/                   # Shared libraries
│   │   └── ms2000_core.py     # Decode/encode utilities
│   ├── wrappers/              # Backward-compatible entry points
│   │   ├── analyze_patch_bank.py
│   │   ├── compare_patches.py
│   │   ├── decode_parameters.py
│   │   ├── decode_sysex.py
│   │   ├── export_single_program.py
│   │   └── fix_sysex.py
│   ├── scripts/               # Standalone helpers
│   │   ├── copy_patch.py
│   │   ├── generate_boc_detailed_reference.py
│   │   └── send_to_ms2000.py
│   └── docs/                  # Tool-specific documentation
│       └── README_DECODE_PARAMETERS.md
├── patches/                     # Patch files
│   ├── factory/
│   │   └── FactoryBanks.syx    # Factory presets (128 patches)
│   └── BoardsOfCanada/
│       └── BOCSunday.syx       # BOC Sunday bank
└── examples/                    # Example outputs
    └── factory_banks.json      # Decoded factory patches (JSON)
```

## Quick Start

### Decode a SysEx file
```bash
python3 implementations/korg/ms2000/tools/ms2000_cli.py \
        inspect implementations/korg/ms2000/patches/factory/FactoryBanks.syx --limit 8
```

Example output:
```
SysEx Header:
  Manufacturer: Korg (0x42)
  Device: MS2000 (0x58)
  Function: 0x4C (PROGRAM DATA DUMP)
  Patches decoded: 128

[A01] Stab Saw
     Mode: Single    Delay: StereoDelay   Mod: Cho/Flg     Arp: OFF

[A02] Synth Lana
     Mode: Single    Delay: StereoDelay   Mod: Cho/Flg     Arp: OFF
...
```

### Compare two patch banks
```bash
python3 implementations/korg/ms2000/tools/ms2000_cli.py compare file1.syx file2.syx
```

### Send SysEx to MS2000
```bash
# List available MIDI outputs
python3 implementations/korg/ms2000/tools/scripts/send_to_ms2000.py --list-outputs

# Send the bundled factory bank to a port containing "MS2000"
python3 implementations/korg/ms2000/tools/scripts/send_to_ms2000.py

# Override port and delay (requires: pip install mido python-rtmidi)
python3 implementations/korg/ms2000/tools/scripts/send_to_ms2000.py \
        --out "Your MIDI Port" --delay-ms 50
```

## SysEx File Format

### Header Structure
```
F0 42 3g 58 4C [encoded data]
│  │  │  │  │
│  │  │  │  └─ Function: 0x4C = PROGRAM DATA DUMP
│  │  │  └──── Device: 0x58 = MS2000 Series
│  │  └─────── MIDI Channel: 30-3F (channel 0-15)
│  └────────── Manufacturer: 0x42 = Korg
└───────────── SysEx Start
```

### Data Encoding

MS2000 uses Korg's 7-to-8 bit encoding:
- MIDI limits data bytes to 0-127 (bit 7 must be 0)
- Every 7 bytes of 8-bit data → 8 bytes of 7-bit MIDI data
- First byte of each group contains MSBs (bit 7) of next 7 bytes
- 14.3% size overhead

Note: Hardware validation indicates this project uses Korg 7→8 encoding variant v2
(the MSB of decoded byte j is stored in bit j of the MSB byte). The encoding applies
to the entire data block for full program bank dumps (0x4C).

### Patch Structure

Each decoded patch is **254 bytes**:

| Bytes | Parameter | Description |
|-------|-----------|-------------|
| 0-11 | Program Name | 12 ASCII characters |
| 16 | Voice Mode | Single/Split/Layer/Vocoder |
| 17 | Scale | Key and type |
| 19-22 | Delay FX | Sync, time, depth, type |
| 23-25 | Mod FX | Speed, depth, type (Chorus/Flanger/Phaser) |
| 26-29 | EQ | Hi/Low frequency and gain |
| 30-33 | Arpeggiator | Tempo, on/off, type, range |
| 34+ | Oscillators, Filters, Envelopes, LFOs |

See [SYSEX_STRUCTURE.txt](docs/SYSEX_STRUCTURE.txt) for complete memory map.

## Tools Documentation

### decode_sysex.py

Decode MS2000 SysEx (.syx) files and display patch parameters.

- Parses SysEx header and validates format
- Implements Korg 7→8 decoding
- Extracts up to 128 patches
- Prints key parameters (mode, FX, arp)

Usage:
```bash
python3 implementations/korg/ms2000/tools/wrappers/decode_sysex.py \
        implementations/korg/ms2000/patches/factory/FactoryBanks.syx
```

### decode_parameters.py

Emit full patch parameter data (all 254 bytes) as structured JSON.

- Covers oscillators, filters, envelopes, modulation matrix, FX, arp, voice routing
- Supports single-patch export (`--patch-index`) or full-bank dumps
- Uses empirically verified offsets documented in `README_DECODE_PARAMETERS.md`

Usage:
```bash
python3 implementations/korg/ms2000/tools/wrappers/decode_parameters.py \
        implementations/korg/ms2000/patches/factory/FactoryBanks.syx \
        implementations/korg/ms2000/examples/factory_banks.json
```

See [`README_DECODE_PARAMETERS.md`](tools/docs/README_DECODE_PARAMETERS.md) for details.

### analyze_patch_bank.py

Summarize a bank: name tokens, voice modes, FX usage, arp, parameter ranges.

Usage:
```bash
python3 implementations/korg/ms2000/tools/wrappers/analyze_patch_bank.py \
        implementations/korg/ms2000/patches/factory/FactoryBanks.syx
```

Deep analysis with full parameter statistics:
```bash
python3 implementations/korg/ms2000/tools/ms2000_cli.py analyze \
        implementations/korg/ms2000/patches/factory/FactoryBanks.syx --deep --json
```

### compare_patches.py

Wrapper around the CLI `compare` subcommand for patch-by-patch diffs.

Usage:
```bash
python3 implementations/korg/ms2000/tools/wrappers/compare_patches.py \
        <file1.syx> <file2.syx> [--patch-index N] [--json]
```

### send_to_ms2000.py

Send a SysEx file to MS2000/MS2000R. Thin wrapper around top‑level `tools/send_sysex.py` with sane defaults.

Dependencies:
- Python 3.8+
- `mido`, `python-rtmidi` (`pip install mido python-rtmidi`)

Defaults:
- `--out "MS2000"`, `--file ../patches/factory/FactoryBanks.syx`, `--delay-ms 50`

Usage:
```bash
python3 implementations/korg/ms2000/tools/scripts/send_to_ms2000.py --list-outputs
python3 implementations/korg/ms2000/tools/scripts/send_to_ms2000.py                     # send bundled factory bank
python3 implementations/korg/ms2000/tools/scripts/send_to_ms2000.py --out "Your Port"   # choose a specific output
python3 implementations/korg/ms2000/tools/scripts/send_to_ms2000.py --file path\to\file.syx --delay-ms 50
```

### fix_sysex.py

Fix broken SysEx files (e.g., missing F7, zero‑padded).

Usage:
```bash
python3 implementations/korg/ms2000/tools/wrappers/fix_sysex.py <input.syx> [output.syx]
```

See [docs/SYSEX_TROUBLESHOOTING.md](docs/SYSEX_TROUBLESHOOTING.md) and top‑level [tools/SEND_SYSEX.md](../../../tools/SEND_SYSEX.md) for more.

### copy_patch.py

Copy a patch within a bank (e.g., A01 → A02).

Usage:
```bash
python3 implementations/korg/ms2000/tools/scripts/copy_patch.py \
        <input.syx> <src_index 1..128> <dst_index 1..128> [-o output.syx]
```

### export_single_program.py

Export a single program to a CURRENT PROGRAM DATA DUMP (.syx, 0x40). Supports encoding variants.

Usage:
```bash
python3 implementations/korg/ms2000/tools/wrappers/export_single_program.py \
        <bank.syx> <index 1..128> [--v1|--v2] [-o out.syx]
```

### ms2000_cli.py

Unified entry point for inspection, decoding, analysis, exporting, and repair.

Subcommands:
- `inspect` — quick human/JSON summary of whole bank or a single patch
- `decode` — full parameter JSON dump (bank or `--patch-index`)
- `analyze` — statistical overview or single-patch snapshot
- `compare` — diff banks or individual patches, human-readable or JSON
- `export` — write a CURRENT PROGRAM DATA DUMP for a chosen patch
- `repair` — append missing F7 terminator and warn about short banks

Usage examples:
```bash
# Summarise first few patches (text)
python3 ms2000_cli.py inspect ../patches/factory/FactoryBanks.syx --limit 5

# Decode patch A01 to JSON file
python3 ms2000_cli.py decode ../patches/factory/FactoryBanks.syx \
        --patch-index 1 --output ../../examples/factory_A01.json

# Encode JSON back into a bank (preserving header from template)
python3 ms2000_cli.py encode ../../examples/factory_banks.json \
        ../patches/factory/FactoryBanks_roundtrip.syx --template ../patches/factory/FactoryBanks.syx

# Analyse complete bank as JSON
python3 ms2000_cli.py analyze ../patches/factory/FactoryBanks.syx --json

# Compare a single patch between two banks
python3 ms2000_cli.py compare ../patches/factory/FactoryBanks.syx \
        ../patches/BoardsOfCanada/BOCSunday.syx --patch-index 1
```

### create_boc_patches.py

Generate the BOCSunday bank and write BOCSunday.syx into `patches/BoardsOfCanada/`.

Usage:
```bash
cd implementations/korg/ms2000/patches/BoardsOfCanada
python3 create_boc_patches.py
```

## Factory Patches

The included **FactoryBanks.syx** contains 128 patches:
- **A01-H12 (123 patches)**: Original factory presets
- **H13-H16 (5 patches)**: Blank placeholders to complete the bank

**Sound Categories:**
- **Leads:** Stab Saw, Synth Tp, Killa Lead, Edge Lead
- **Bass:** MG Bass, Boost Bass, Drive Bass, Fat Bass
- **Pads:** PWM Strings, Royal Pad, Stream Pad, Silk Pad
- **Keys:** Vintage EP, Lounge Organ, Reed Piano
- **Effects:** Evolution, Ice Field, Bad Dreem, Thunder
- **Vocoder:** Voice /A/, Vocoder1, Vocoder8, Vocoder16

Full patch list available in `examples/factory_banks.json`.

## Technical Details

### File Sizes
- Raw data: 254 bytes/patch × 128 patches = 32,512 bytes
- After encoding: ~37,157 bytes
- With header + F7: 37,163 bytes total

FactoryBanks.syx is 37,163 bytes (128 patches, complete bank ready for hardware).

### Device Identification

**Universal Device Inquiry:**
```
Request:  F0 7E 7F 06 01 F7
Response: F0 7E 0g 06 02 42 58 00 mm 00 xx xx xx xx F7
```

Where:
- `42` = Korg
- `58 00` = MS2000 Series
- `mm` = Member ID (01=MS2000, 08=MS2000R)
- `xx xx xx xx` = Version (minor LSB/MSB, major LSB/MSB)

### Function IDs

| Function | Hex | Description |
|----------|-----|-------------|
| Current Program Dump Request | 0x10 | Request edit buffer |
| **Program Data Dump** | **0x4C** | **All 128 programs** |
| Global Data Dump | 0x51 | Global settings |
| All Data Dump | 0x50 | Programs + Global |
| Parameter Change | 0x41 | Edit single parameter |

## Advanced Usage

### Extract Specific Patch
```python
from decode_sysex import parse_sysex_file

patches = parse_sysex_file('patches/factory/FactoryBanks.syx')
patch = patches[0]  # First patch

print(f"Name: {patch.name}")
print(f"Voice Mode: {patch.voice_mode}")
print(f"Arp Type: {patch.arp_type}")
```

### Modify Patch Parameters
```python
# Read patch data
patch_data = bytearray(patch.raw_data)

# Modify parameters (example: change arp tempo)
tempo = 140
patch_data[30] = (tempo >> 8) & 0xFF  # MSB
patch_data[31] = tempo & 0xFF         # LSB

# Re-encode and save (encoding function needed)
```

## Resources

### Official Documentation
- [MS2000 Owner's Manual](https://www.korg.com/us/support/download/product/0/158/)
- [Korg MS2000 Product Page](https://www.korg.com/us/products/synthesizers/ms2000/)
- MIDI Implementation Chart (included in docs/)

### Related Tools
- [SysEx Librarian](https://www.snoize.com/SysExLibrarian/) - Mac OS X
- [MIDI-OX](http://www.midiox.com/) - Windows
- [SendMIDI](https://github.com/gbevin/SendMIDI) - Command-line MIDI tools

### Further Reading
- See [../../docs/general/LEARNING_SUMMARY.md](../../docs/general/LEARNING_SUMMARY.md) for MIDI fundamentals
- See [../../docs/general/QUICK_REFERENCE.md](../../docs/general/QUICK_REFERENCE.md) for quick lookup

## Contributing

Contributions welcome! Possible enhancements:
- Complete parameter decoder (bytes 34-253)
- Bidirectional SysEx communication with hardware
- Patch editor GUI
- Random patch generator
- Audio feature extraction and parameter mapping

## License

MIT License - see [LICENSE](../../../LICENSE) for details.

Tools and documentation are open source. Korg MS2000 specifications and factory patches remain property of Korg Inc.

---

**Note:** This implementation is for educational and archival purposes. Always respect copyright and licensing of commercial patches and content.
