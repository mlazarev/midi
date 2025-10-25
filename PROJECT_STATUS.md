# Project Status & Roadmap

Version: v1.3.0

## ✅ Completed

### MS2000 Tools & Banks
- [x] Robust SysEx encoder/decoder (Korg 7→8 bit, variant v2), hardware‑verified; structured JSON now feeds the encoder end-to-end
- [x] Factory bank included: `patches/factory/FactoryBanks.syx`
- [x] Boards of Canada style bank:
  - [x] `patches/BoardsOfCanada/BOCSunday.syx` (16 handcrafted + 112 generated)
- [x] Generator: `patches/BoardsOfCanada/create_boc_patches.py` (safe ranges, varied categories)
- [x] Tools:
  - [x] `ms2000_cli.py` — unified inspect/decode/analyze/export/repair
  - [x] `decode_sysex.py` — legacy wrapper (inspect)
  - [x] `analyze_patch_bank.py` — legacy wrapper (stats summary)
  - [x] `compare_patches.py` — patch diffs (wrapper)
  - [x] `send_to_ms2000.py` — convenience sender
  - [x] `copy_patch.py` — duplicate within bank
  - [x] `export_single_program.py` — 0x40 single‑program dumps (v1/v2)
  - [x] `fix_sysex.py` — add F7, strip padding (wrapper)
- [x] Troubleshooting docs updated (encoding variant v2, name corruption, silence)
- [x] Repo structure reorganized (factory/BoardsOfCanada folders, examples JSON)

### Documentation
- [x] MS2000 README with tool usage and bank layout
- [x] SysEx structure, MIDI implementation chart (vendor docs)
- [x] General learning docs retained (optional)

## 🚧 In Progress

- Decode convenience: surface motion/vocoder bytes in JSON (currently preserved but opaque)
- Analyzer: auto‑detect v1/v2 in decoder for complete compatibility

## 📋 Planned Features

### Near Term
- Full parameter map (OSC, filter, EG, LFO, motion seq, vocoder)
- Sanity validator for reserved bits / illegal combinations
- Optional Git LFS for curated .syx binaries

### Medium Term
- GUI librarian/editor
- Bidirectional MIDI (receive dumps from hardware)
- Batch operations, tagging, search

### Long Term
- Additional synths (Roland/Yamaha/Sequential)
- Web UI (WASM) proof‑of‑concept
- MIDI 2.0/MPE exploration

## 🐛 Known Notes

- Decoder now maps core synth parameters (global FX, timbres, modulation); motion sequencer and vocoder bytes remain opaque but are preserved for round-trips.
- Sending requires `mido` + `python-rtmidi` if using `send_to_ms2000.py`.

## 📊 Project Metrics (informational)

- Dependencies: Python stdlib (tools), plus `mido`/`python-rtmidi` for sending only
- Supported device: Korg MS2000/MS2000R

## 📝 Change Log

See CHANGELOG.md for release history.

---

For contribution guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md)
