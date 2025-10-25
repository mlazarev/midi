# Korg MS2000 Documentation Audit

| Source | Location | Revision | Notes |
|--------|----------|----------|-------|
| **MS2000_MIDIimp.TXT** | `implementations/korg/ms2000/docs/MS2000_MIDIimp.TXT` | Rev 1.1 (2000-01-05) | Official Korg MIDI implementation chart. Primary authority for SysEx layout, parameter ranges, and notation (e.g., `64+/-X`). |
| **SYSEX_STRUCTURE.txt** | `implementations/korg/ms2000/docs/SYSEX_STRUCTURE.txt` | Project-authored (2025-10-25) | Derived memory map based on Rev 1.1. Includes 7→8 encoding walkthrough and byte-by-byte layout for all 254 patch bytes. |
| **SYSEX_TROUBLESHOOTING.md** | `implementations/korg/ms2000/docs/SYSEX_TROUBLESHOOTING.md` | Project-authored | Operational guidance (terminators, padding). Supports hardware transfer validation. |
| **OFFSET_64_BUG_ANALYSIS.md** | `implementations/korg/ms2000/docs/OFFSET_64_BUG_ANALYSIS.md` | Project-authored (2025-10-25) | Post-mortem documenting the signed-7-bit vs offset-64 mistake. Enumerates every parameter affected. |
| **Factory Bank Dump** | `implementations/korg/ms2000/patches/factory/FactoryBanks.syx` | Firmware 1.x (factory) | Reference data set for decoding, roundtrip, and hardware checks. |

## Firmware Coverage
- Documentation explicitly states MS2000/MS2000R Revision 1.1 (firmware 1.x). No deltas for later firmware revisions are known; keep watch for MS2000B or user OS updates.
- Factory bank source matches ROM programs for v1.x. No custom bank dumps archived here yet.

## Quick Reference (per guide Phase 1.2)
```python
SYSEX_HEADER = [0xF0, 0x42, 0x30, 0x58, 0x4C]
PATCH_SIZE = 254
ENCODING = "korg_7to8_v2"
CHECKSUM = "None (Korg bank dumps rely on 7-bit packing and terminal F7)"
TERMINATOR = 0xF7
```

## Coverage Summary
- ✅ Official spec present and archived in plain text.
- ✅ Derived structural diagram aligns byte offsets with implementation.
- ✅ Bug analysis captures offset-64 interpretation and affected fields.
- ⚠️ No errata or supplemental docs located beyond Rev 1.1.
- ⚠️ Community notes (forums, mailing lists) not yet gathered; add if discrepancies appear during future hardware sessions.

## Next Actions
1. Reconfirm manufacturer docs if firmware 1.2 or higher becomes available.
2. Archive any third-party discoveries about motion sequencer or vocoder regions once decoded.
3. Link newly added encoding reference and hardware verification materials when available.
