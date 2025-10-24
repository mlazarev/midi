# Changelog

All notable changes to this project will be documented in this file.

# v1.1.0 (2025-10-21)

Highlights
- Introduced `ms2000_cli.py` `compare` subcommand for patch/bank diffs with JSON output
- Added `ms2000_cli.py encode` to rebuild SysEx banks from decoded JSON
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
