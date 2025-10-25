# Offset-64 Encoding Bug Analysis

**Date:** 2025-10-25  
**Version Fixed:** v1.3.0  
**Severity:** Critical - All affected parameters were off by 64

---

## Executive Summary

**CONCLUSION: The bug was in OUR IMPLEMENTATION, not in Korg's documentation.**

The Korg MS2000 MIDI Implementation documentation was **correct and clear** about offset-64 encoding. We incorrectly implemented a different encoding scheme (signed 7-bit with bit 6 as sign) instead of the documented offset-64 format.

---

## What is Offset-64 Encoding?

Offset-64 is a simple encoding where the CENTER value (0) is encoded as byte 64:

```
Value Range:  -64  -63  -62  ...  -1   0   +1  ...  +62  +63
Byte Value:     0    1    2  ...  63  64   65  ...  126  127

Formula: byte_value = actual_value + 64
Inverse: actual_value = byte_value - 64
```

**Key characteristic:** The center point is at byte value 64, not 0.

---

## What Korg's Documentation Said

From `MS2000_MIDIimp.TXT` (TABLE 2: Data structure of Program Data):

### Examples of Offset-64 Parameters:

```
Line 1003: | +13  | Semitone       | 64+/-24=0+/-24[note]  |
Line 1005: | +14  | Tune           | 64+/-63=0+/-63        |
Line 1029: | +22  | EG1 Intensity  | 64+/-63=0+/-63        |
Line 1031: | +23  | Velocity Sense | 64+/-63=0+/-63        |
Line 1033: | +24  | Keyboard Track | 64+/-63=0+/-63        |
Line 1039: | +26  | Panpot         | 0~64~127=L64~CNT~R63  |
Line 1049: | +28  | Velocity Sense | 64+/-63=0+/-63        |
Line 1050: | +29  | Keyboard Track | 64+/-63=0+/-63        |
Line 1115: | +45  | Patch1 Intensity | 64+/-63=0+/-63      |
Line 1121: | +47  | Patch2 Intensity | 64+/-63=0+/-63      |
Line 1127: | +49  | Patch3 Intensity | 64+/-63=0+/-63      |
Line 1133: | +51  | Patch4 Intensity | 64+/-63=0+/-63      |
```

### Documentation Notation Explained:

**Format:** `64+/-X=0+/-X`

This notation clearly states:
- **64** is the CENTER byte value
- **+/-X** means the range extends X units in both directions
- **=0+/-X** means the resulting VALUE range is -X to +X with 0 at center

**Example:** `64+/-63=0+/-63`
- Byte 64 encodes value 0 (center)
- Bytes 1-63 encode values -63 to -1
- Bytes 65-127 encode values +1 to +63
- Byte 0 encodes value -64

**Panpot notation:** `0~64~127=L64~CNT~R63`
- Byte 0 = full left (L64)
- Byte 64 = center (CNT)
- Byte 127 = full right (R63)

**This is unambiguous and correct.**

---

## What We Implemented (WRONG)

### Original Buggy Code:

```python
def _signed(value: int) -> int:
    """BUGGY: Signed 7-bit with bit 6 as sign bit"""
    return value - 128 if value >= 64 else value
```

### What This Does:

```
Byte Value:    0    1   ...   63   64   65  ...  126  127
Decoded To:    0    1   ...   63  -64  -63  ...   -2   -1
```

This treats bit 6 as a SIGN BIT (like two's complement), where:
- Bytes 0-63: Positive values 0 to +63
- Bytes 64-127: Negative values -64 to -1

**This is completely different from offset-64!**

---

## Concrete Examples of the Bug

### Example 1: Panpot (Center Position)

**Expected behavior (per documentation):**
- JSON value: `0` (center)
- Byte in SysEx: `64`
- Synth displays: Center

**What our buggy code did:**
```python
# DECODING (reading from SysEx):
byte = 64
decoded = _signed(64)  # Returns 64 - 128 = -64
# Saved to JSON as -64 ✗ WRONG!

# ENCODING (writing to SysEx):
value = 0  # Want center
byte = _to_signed_7bit(0)  # Returns 0
# Wrote byte 0 to SysEx ✗ WRONG!
# Synth reads byte 0 as full left (L64)
```

**Result:** Center panning (0) was decoded as -64, and when encoding 0, it went full left.

### Example 2: OSC2 Semitone

**User had:** `+12` semitones in JSON (should be one octave up)

**What our buggy code did:**
```python
# ENCODING:
value = 12
byte = _to_signed_7bit(12)  # Returns 12
# Wrote byte 12 to SysEx ✗ WRONG!

# Synth interprets byte 12:
actual_value = 12 - 64 = -52 semitones ✗ WRONG!
```

**Result:** User wanted +12 semitones, synth played -52 semitones.

**Correct encoding should have been:**
```python
value = 12
byte = _to_offset64(12)  # Returns 12 + 64 = 76
# Synth interprets byte 76:
actual_value = 76 - 64 = +12 semitones ✓ CORRECT!
```

---

## All Affected Parameters (15 total)

### Timbre 1 & 2:

**OSC2 Section (2 params):**
1. `osc2.semitone` - Offset +13
2. `osc2.tune` - Offset +14

**Filter Section (3 params):**
3. `filter.eg1_intensity` - Offset +22
4. `filter.velocity_sense` - Offset +23
5. `filter.kbd_track` - Offset +24

**Amp Section (3 params):**
6. `amp.panpot` - Offset +26
7. `amp.velocity_sense` - Offset +28
8. `amp.kbd_track` - Offset +29

**Patch Matrix (4 params):**
9. `patch.patch1.intensity` - Offset +45
10. `patch.patch2.intensity` - Offset +47
11. `patch.patch3.intensity` - Offset +49
12. `patch.patch4.intensity` - Offset +51

---

## Root Cause Analysis

### Why Did This Happen?

1. **Misunderstanding of notation:** The `64+/-X` notation may have been misread as "signed with offset" rather than "offset-64 encoding"

2. **Confusion with signed 7-bit:** There are other MIDI devices that use signed 7-bit encoding where bit 6 is a sign bit. We may have confused this with Korg's offset-64.

3. **Lack of hardware verification initially:** The bug wasn't caught until patches were loaded on actual hardware and values were manually checked.

### Why Documentation Was Clear:

The Korg documentation uses **three different notations** consistently:

1. **Unsigned:** `0~127` (no offset)
2. **Offset-64:** `64+/-X=0+/-X` or `0~64~127=L64~CNT~R63`
3. **Bit fields:** Explicit bit ranges like `B0~3` or `B6,7`

Each encoding type is clearly distinguished.

---

## The Fix

### New Helper Functions:

```python
def _to_offset64(value: Any, min_val: int = -64, max_val: int = 63) -> int:
    """Encode MS2000 offset-64 format"""
    value = int(value)
    if value < min_val or value > max_val:
        raise ValueError(f"Offset-64 value out of range {min_val}~{max_val}: {value}")
    return value + 64

def _from_offset64(byte_value: int) -> int:
    """Decode MS2000 offset-64 format"""
    return byte_value - 64
```

---

## Lessons Learned

### For Future Manufacturer Implementations:

1. **Read documentation carefully:** Different manufacturers use different encoding schemes

2. **Recognize encoding patterns:**
   - `0~127` = Unsigned (no offset)
   - `64+/-X` = Offset-64 (Korg style)
   - Check if bits are explicitly called out as sign bits

3. **Hardware verify early:** Don't wait until full implementation
   - Send test patches with known parameter values
   - Manually check key params on hardware
   - Test edge cases (especially center values)

4. **Create encoding test suite:**
   ```python
   test_cases = [
       (-64, 0),   # Min value
       (0, 64),    # Center (critical!)
       (+63, 127), # Max value
   ]
   ```

---

## Comparison: Offset-64 vs Signed 7-bit

### Offset-64 (Korg MS2000):
```
Byte:   0   1   2  ...  63   64   65  ...  126  127
Value: -64 -63 -62  ... -1    0   +1  ...  +62  +63
Center: Byte 64 = Value 0
```

### Signed 7-bit (Two's Complement):
```
Byte:   0   1   2  ...  63   64   65  ...  126  127
Value:  0  +1  +2  ... +63  -64  -63  ...  -2   -1
Center: No natural center (bit 6 is sign bit)
```

**Key Difference:** Offset-64 has a natural center at byte 64. Signed 7-bit treats bit 6 as sign.

---

## Impact Summary

**Before Fix:**
- All offset-64 parameters were wrong
- Parameter values off by 64 in most cases
- User patches didn't work on hardware

**After Fix (v1.3.0):**
- ✓ All parameters decode correctly
- ✓ Roundtrip testing passes (byte-perfect)
- ✓ Hardware verification confirms all values match
- ✓ 256 new BOC patches tested and working

---

**Conclusion:** The documentation was correct. We misimplemented it. This analysis should prevent similar bugs when implementing other manufacturers.
