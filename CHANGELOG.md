# Changelog

All notable changes to this project will be documented in this file.

# v1.3.0 (2025-10-25)

Highlights
- **CRITICAL BUG FIX**: Fixed all offset-64 encoding/decoding for MS2000 parameters
  - OSC2 semitone/tune now encode/decode correctly (was using wrong signed format)
  - Filter modulation parameters (EG1 intensity, velocity sense, keyboard track) fixed
  - Amp parameters (panpot, velocity sense, keyboard track) fixed
  - Patch matrix intensity values now correct
  - All parameters now match hardware values exactly (hardware-verified)
- **New BOC Patch Banks**: Created two complete Boards of Canada style banks (128 patches each)
  - `factory_evolutions.syx`: Factory patches transformed with authentic BOC characteristics *(now maintained in the companion `boc-sound-lab` repository)*
  - `boc_originals.syx`: 128 completely original patches designed from BOC principles *(now maintained in `boc-sound-lab`)*
  - Both banks based on comprehensive "How to Make Boards of Canada Sounds" guide analysis
- Re-decoded `factory_banks.json` with corrected offset-64 values

Core Changes
- Added `_to_offset64()` and `_from_offset64()` helper functions to ms2000_core.py
- Fixed all decoding in `_extract_timbre()` function (9 parameter corrections)
- Fixed all encoding in `build_patch_bytes()` function (9 parameter corrections)
- Comprehensive roundtrip testing confirms byte-perfect encoding

New Scripts
- `create_boc_evolutions.py`: Transforms factory patches with BOC characteristics *(now part of `boc-sound-lab`)*
  - L/R Delay with high depth, Chorus/Flanger modulation
  - 12dB LPF with low resonance, OSC2 interval detuning
  - LFO modulation (Triangle→Pitch, Sine→Cutoff)
  - Long release times, subtle noise for analog texture
- `create_boc_originals.py`: Generates original BOC patches from 5 archetypes *(now part of `boc-sound-lab`)*
  - Classic BOC Pad (35%), Detuned Lead (30%), DWGS Texture (20%)
  - Ring Mod Bell (10%), Arpeggiator Sequence (5%)
  - All patches crafted from scratch using authentic BOC recipe principles

Patch Banks
- `patches/factory/factory_evolutions.syx`: 128 BOC-transformed factory patches *(relocated to `boc-sound-lab`)*
- `patches/factory/boc_originals.syx`: 128 original BOC-style patches *(relocated to `boc-sound-lab`)*
- `examples/factory_evolutions.json`: JSON for factory evolutions *(relocated to `boc-sound-lab`)*
- `examples/boc_originals.json`: JSON for original BOC patches *(relocated to `boc-sound-lab`)*

Documentation
- All patches feature BOC-style evocative naming (e.g., "Amber Aurora", "Dusk Memory")
- Comprehensive patch design based on statistical analysis of 123 BOC patches
- Hardware-verified: all parameters tested and confirmed working on MS2000

Technical Notes
- Offset-64 encoding: value range -64~0~63 maps to byte range 0~64~127
- Previous decoder was using true signed 7-bit for offset-64 fields (incorrect)
- Affects: OSC2 pitch, filter mod, amp mod, patch intensity (15 fields total)
- Bug caused parameter values to be off by 64 (e.g., panpot 0 read as -64)

# v1.2.0 (2025-10-24)

Highlights
- Encoder rebuild no longer relies on `raw_hex`; modulation routing offsets fixed and new fields (`timbre_voice`, delay timebase, LFO tempo values) round out structured JSON.
- Factory JSON refreshed (`factory_banks.json`) with canonical schema, index/slot metadata, and level/pan safeguards for every patch.
- Documentation tightened around the decode/encode workflow and the CLI now carries motion/vocoder regions forward automatically.

Docs
- Rewrote decoder guide to reflect the raw-free pipeline and new JSON sample.
- Added cross-project note: Boards of Canada experiment assets relocated to the companion `boc-sound-lab` repo (the toolkit retains the core factory bank only).

# v1.1.0 (2025-10-21)

Highlights
- Introduced `ms2000_cli.py` `compare` subcommand for patch/bank diffs with JSON output
- Added `ms2000_cli.py encode` to rebuild SysEx banks from decoded JSON
- Added `ms2000_cli.py analyze --deep` for full-parameter statistical reports
- Reorganized MS2000 tooling into `lib/`, `wrappers/`, `scripts/`, and `docs/` for clarity

Docs
- Updated README files and decoder docs to reflect new tool locations and usage

## v1.0.0 (2025-10-19)

Highlights
- Korg MS2000/MS2000R: hardware‑verified Korg 7→8 encoding (variant v2)
- Boards of Canada style bank:
  - BOCSunday.syx (16 handcrafted + 112 generated; varied categories)
- Factory bank included: patches/factory/FactoryBanks.syx

Tools
- ms2000_cli.py — unified inspect/decode/analyze/export/repair interface
- decode_sysex.py — decode/display SysEx
- analyze_patch_bank.py — summary stats
- compare_patches.py — patch diffs
- send_to_ms2000.py — convenience sender
- copy_patch.py — copy patch within bank
- export_single_program.py — 0x40 single program dumps (v1/v2 variants)
- fix_sysex.py — add F7, strip padding

Docs & Structure
- MS2000 README: tool usage, bank layout, encoding notes
- Troubleshooting: v2 encoding detection (garbled names/K), silent program diagnosis
- Reorganized patches into factory/ and BoardsOfCanada/
- Examples: factory_banks.json
