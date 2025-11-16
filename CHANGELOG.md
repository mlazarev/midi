# Changelog

All notable changes to this project will be documented in this file.

## Unreleased

- Removed the per-synth `send_to_ms2000.py` and `send_to_jp8080.py` wrappers—use the shared `tools/send_sysex.py` helper for all hardware transfers.

# v1.3.0 (2025-10-25)

Highlights
- **CRITICAL BUG FIX**: Fixed all offset-64 encoding/decoding for MS2000 parameters
  - OSC2 semitone/tune now encode/decode correctly (was using wrong signed format)
  - Filter modulation parameters (EG1 intensity, velocity sense, keyboard track) fixed
  - Amp parameters (panpot, velocity sense, keyboard track) fixed
  - Patch matrix intensity values now correct
  - All parameters now match hardware values exactly (hardware-verified)
- Re-decoded `factory_banks.json` with corrected offset-64 values

Core Changes
- Added `_to_offset64()` and `_from_offset64()` helper functions to ms2000_core.py
- Fixed all decoding in `_extract_timbre()` function (9 parameter corrections)
- Fixed all encoding in `build_patch_bytes()` function (9 parameter corrections)
- Comprehensive roundtrip testing confirms byte-perfect encoding

Documentation
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
- Reorganized patches into factory/ subdirectories for clarity
- Examples: factory_banks.json
