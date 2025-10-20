# Project Status & Roadmap

Version: v1.0.0

## ✅ Completed

### MS2000 Tools & Banks
- [x] Robust SysEx encoder/decoder (Korg 7→8 bit, variant v2), hardware‑verified
- [x] Factory bank included: `patches/factory/FactoryBanks.syx`
- [x] Boards of Canada banks:
  - [x] `patches/BoardsOfCanada/BOCPatches.syx` (reference)
  - [x] `patches/BoardsOfCanada/BOCSunday.syx` (16 handcrafted + 112 generated)
- [x] Generator: `patches/BoardsOfCanada/create_boc_patches.py` (safe ranges, varied categories)
- [x] Tools:
  - [x] `decode_sysex.py` — decode/display
  - [x] `analyze_patch_bank.py` — stats summary
  - [x] `compare_patches.py` — patch diffs
  - [x] `send_to_ms2000.py` — convenience sender
  - [x] `copy_patch.py` — duplicate within bank
  - [x] `export_single_program.py` — 0x40 single‑program dumps (v1/v2)
  - [x] `dump_bank_json.py` — export bank as JSON
  - [x] `fix_sysex.py` — add F7, strip padding
- [x] Troubleshooting docs updated (encoding variant v2, name corruption, silence)
- [x] Repo structure reorganized (factory/BoardsOfCanada folders, examples JSON)

### Documentation
- [x] MS2000 README with tool usage and bank layout
- [x] SysEx structure, MIDI implementation chart (vendor docs)
- [x] General learning docs retained (optional)

## 🚧 In Progress

- Decode convenience: expand `decode_sysex.py` to parse full timbre bytes (34‑253)
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

- Decoder exposes raw 254 bytes; parsed fields currently focus on header/FX/arp. Full timbre decode is planned.
- Sending requires `mido` + `python-rtmidi` if using `send_to_ms2000.py`.

## 📊 Project Metrics (informational)

- Dependencies: Python stdlib (tools), plus `mido`/`python-rtmidi` for sending only
- Supported device: Korg MS2000/MS2000R

## 📝 Change Log

See CHANGELOG.md for release history.

---

For contribution guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md)
