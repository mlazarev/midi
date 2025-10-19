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
├── tools/                       # Python tools
│   ├── decode_sysex.py         # Decode and display SysEx files
│   ├── compare_patches.py      # Compare two SysEx files
│   └── send_to_ms2000.py       # Send SysEx to MS2000/MS2000R (wrapper)
├── patches/                     # Patch files
│   └── OriginalPatches.syx     # Factory presets (128 patches)
└── examples/                    # Example outputs
    └── original_patches_decoded.txt  # Decoded factory patches
```

## Quick Start

### Decode a SysEx file
```bash
cd tools
python3 decode_sysex.py ../patches/OriginalPatches.syx
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
python3 compare_patches.py file1.syx file2.syx
```

### Send SysEx to MS2000
```bash
# List available MIDI outputs
python3 send_to_ms2000.py --list-outputs

# Send the bundled factory bank to a port containing "MS2000"
python3 send_to_ms2000.py

# Override port and delay (requires: pip install mido python-rtmidi)
python3 send_to_ms2000.py --out "Your MIDI Port" --delay-ms 50
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

**Critical:** The encoding applies to the entire data block, not individual patches.

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

Decode MS2000 SysEx files and display patch parameters.

**Features:**
- Parses SysEx header and validates format
- Implements 7-to-8 bit decoding algorithm
- Extracts all patches (up to 128)
- Displays key parameters for each patch

**Usage:**
```bash
python3 decode_sysex.py <sysex_file.syx>
```

**Output includes:**
- Patch name
- Voice mode
- Effects settings
- Arpeggiator configuration

### compare_patches.py

Compare two SysEx files and show differences.

**Features:**
- Patch-by-patch comparison
- Parameter diff display
- Summary statistics

**Usage:**
```bash
python3 compare_patches.py <file1.syx> <file2.syx>
```

### send_to_ms2000.py

Send a SysEx file to a Korg MS2000/MS2000R MIDI output port. Thin wrapper around the top‑level `tools/send_sysex.py` with sensible defaults for MS2000.

Dependencies:
- Python 3.8+
- `mido` and `python-rtmidi` (`pip install mido python-rtmidi`)

Features:
- Defaults to `--out "MS2000"`, `--file ../patches/OriginalPatches.syx`, `--delay-ms 50`
- Lists available MIDI outputs
- Allows overriding output port, file, delay, and auto-fix

Usage:
```bash
# From this tools directory
python3 send_to_ms2000.py --list-outputs
python3 send_to_ms2000.py                     # send bundled factory bank
python3 send_to_ms2000.py --out "Your Port"   # choose a specific output
python3 send_to_ms2000.py --file path\to\file.syx --delay-ms 50
```

### fix_sysex.py

Fix broken SysEx files that won't load into hardware.

**Features:**
- Validates SysEx header
- Removes zero padding
- Adds missing F7 (End of Exclusive) terminator
- Creates automatic backups

**Usage:**
```bash
python3 fix_sysex.py <input.syx> [output.syx]
```

**Why you might need this:**
Many MS2000 SysEx files found online are padded with zeros and missing the required F7 terminator byte. This prevents them from loading into the hardware even though they may decode correctly in software. This tool fixes the issue automatically.

See [SYSEX_TROUBLESHOOTING.md](docs/SYSEX_TROUBLESHOOTING.md) for details.

## Factory Patches

The included **OriginalPatches.syx** contains 128 patches:
- **A01-H12 (123 patches)**: Original factory presets
- **H13-H16 (5 patches)**: Blank placeholders to complete the bank

**Sound Categories:**
- **Leads:** Stab Saw, Synth Tp, Killa Lead, Edge Lead
- **Bass:** MG Bass, Boost Bass, Drive Bass, Fat Bass
- **Pads:** PWM Strings, Royal Pad, Stream Pad, Silk Pad
- **Keys:** Vintage EP, Lounge Organ, Reed Piano
- **Effects:** Evolution, Ice Field, Bad Dreem, Thunder
- **Vocoder:** Voice /A/, Vocoder1, Vocoder8, Vocoder16

Full patch list available in [examples/original_patches_decoded.txt](examples/original_patches_decoded.txt).

## Technical Details

### File Sizes
- Raw data: 254 bytes/patch × 128 patches = 32,512 bytes
- After encoding: ~37,157 bytes
- With header + F7: 37,163 bytes total

OriginalPatches.syx is 37,163 bytes (128 patches, complete bank ready for hardware).

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

patches = parse_sysex_file('OriginalPatches.syx')
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
