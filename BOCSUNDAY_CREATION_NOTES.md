# BOCSunday.syx Creation - Fixed and Verified

## 2025-10-19 — Hardware validation final fixes

Observed on real MS2000 hardware:

- Symptom: Only A01, A08, A15 were audible. Copying A01→A02 inside the bank still produced silence at A02. Sending a single program showed garbled names with a leading 'K' and silence.
- Root causes:
  - 7-bit encoding variant: MSB packing must use bit order v2 (place MSB of byte j into bit j of the MSB byte), not v1 (bit 6−j). Using v1 causes corrupted program headers/names and parameter bytes on this unit.
  - OSC2 parameter byte: must follow MS2000 spec strictly. Bits B4..5 = Mod Select (Off/Ring/Sync/Ring+Sync), bits B0..1 = Wave (Saw/Square/Triangle). Other bits must be 0. Illegal waves (e.g., Sine, DWGS) or stray bits can mute the timbre.
  - Program header byte 16: ensure a sane value for Single mode; our generator now sets voice mode in B4..5 and leaves other bits safe for Single timbre operation.

Fixes applied:

- Switched encoder in `create_boc_patches.py` to v2 MSB packing (bit j).
- Corrected OSC2 byte packing and constrained OSC2 waves to Saw/Square/Triangle. Updated A12 (Soft Pluck) to use Triangle on OSC2.
- Ensured program header (byte 16) is written with correct voice mode and timbre selection for Single.

Verification:

- Full bank size: 37,163 bytes (5 header + 37,157 encoded + 1 F7).
- All patches A01–A16 audible on hardware; names display correctly; no stray characters.
- Single‑program tests (0x40) also audible when using v2 encoding.

New tools:

- `implementations/korg/ms2000/tools/copy_patch.py` — copy patches within a bank.
- `implementations/korg/ms2000/tools/export_single_program.py` — export a single patch as a CURRENT PROGRAM DATA DUMP for slot‑by‑slot testing.

## Issue Found
The initial version had an encoding bug that resulted in 37,166 bytes instead of the correct 37,163 bytes.

### Root Cause
The `encode_korg_7bit()` function was padding incomplete groups with zeros, causing the last 4 bytes to be encoded as a full 7-byte group (8 encoded bytes) instead of just 5 encoded bytes.

### Fix Applied
Changed the encoding function to handle incomplete groups correctly and (as of 2025‑10‑19) to use v2 MSB bit order required by hardware:
- Don't pad the last chunk with zeros
- Only encode the bytes that actually exist
- Result: 4 remainder bytes → 5 encoded bytes (1 MSB + 4 data) ✓

### Verification
```
Raw bytes: 128 patches × 254 bytes = 32,512 bytes
Complete groups: 32,512 ÷ 7 = 4,644 complete groups + 4 remainder bytes
Encoded complete: 4,644 × 8 = 37,152 bytes
Encoded remainder: 1 MSB + 4 data = 5 bytes
Total encoded: 37,157 bytes
With header + footer: 5 + 37,157 + 1 = 37,163 bytes ✓ (using v2 encoding)
```

### File Comparison
```
BOCPatches.syx:       37,163 bytes ✓
BOCSunday.syx:        37,163 bytes ✓
OriginalPatches.syx:  37,163 bytes ✓
```

All three files are now identical in size and structure, confirming correct encoding.

## Testing Results

**Decode Test:** ✓ PASSED
- All 128 patches decode successfully
- Patch names are correct
- Parameters are correct
- No decoding errors

**File Structure:** ✓ VERIFIED
- Header: F0 42 30 58 4C (5 bytes)
- Encoded data: 37,157 bytes
- Footer: F7 (1 byte)
- Total: 37,163 bytes

## Ready for Use

The BOCSunday.syx file is now correctly formatted and ready to send to the MS2000:

```bash
python3 tools/send_sysex.py --file implementations/korg/ms2000/patches/BOCSunday.syx \
    --out "MS2000" --delay-ms 50
```

## Files Modified
- `implementations/korg/ms2000/tools/create_boc_patches.py` - Fixed encode_korg_7bit()
- `implementations/korg/ms2000/patches/BOCSunday.syx` - Regenerated with correct encoding

---
**Fixed:** 2025-01-19
**Status:** ✅ VERIFIED AND READY
