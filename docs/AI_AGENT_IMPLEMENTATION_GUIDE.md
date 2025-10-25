# AI Agent Guide: Implementing MIDI SysEx Decoders/Encoders

**Audience:** AI coding agents implementing support for new synthesizer manufacturers
**Last Updated:** 2025-10-25
**Based on:** Korg MS2000 implementation (v1.0.0 - v1.3.0)

---

## Table of Contents

1. [Overview](#overview)
2. [Phase 1: Documentation Analysis](#phase-1-documentation-analysis)
3. [Phase 2: Encoding Scheme Recognition](#phase-2-encoding-scheme-recognition)
4. [Phase 3: Test Suite Creation](#phase-3-test-suite-creation)
5. [Phase 4: Core Implementation](#phase-4-core-implementation)
6. [Phase 5: Hardware Verification](#phase-5-hardware-verification)
7. [Phase 6: Patch Generation](#phase-6-patch-generation)
8. [Common Pitfalls](#common-pitfalls)
9. [Checklist](#implementation-checklist)

---

## Overview

### Purpose

This guide provides a step-by-step process for implementing MIDI SysEx decoders and encoders for synthesizers from manufacturers like Roland, Yamaha, Sequential, etc.

### Key Learnings from MS2000 Implementation

**Critical Bug Discovered:** Offset-64 encoding was misimplemented as signed 7-bit, causing all affected parameters to be off by 64. This was caught only through hardware verification.

**Lesson:** Documentation may be correct, but encoding schemes can be subtle. Always verify with hardware early in the process.

---

## Phase 1: Documentation Analysis

### Step 1.1: Locate Official Documentation

**Required documents:**
- MIDI Implementation Chart
- SysEx specification (data dump format)
- Parameter reference (if separate)
- Supplement documents (errata, updates)

**Storage location:**
```
implementations/{manufacturer}/{model}/docs/
```

**Action items:**
- [ ] Download all official documentation
- [ ] Check for firmware version differences
- [ ] Note documentation date and revision
- [ ] Look for community-contributed documentation

### Step 1.2: Identify SysEx Message Format

**Look for:**
```
Header format:     F0 {manufacturer_id} {device_id} {function} ...
Data structure:    Patch size, bank organization
Encoding scheme:   7-bit, 8-to-7, nibblized, etc.
Checksum/footer:   Validation bytes, F7 terminator
```

**Document:**
```python
# Example structure
SYSEX_HEADER = [0xF0, 0x42, 0x30, 0x58, 0x4C]  # Korg MS2000
PATCH_SIZE = 254  # Bytes per patch (before encoding)
ENCODING = "korg_7to8"  # 7-to-8 bit encoding (variant v2)
```

### Step 1.3: Map Parameter Layout

**Create a reference table:**

```markdown
| Offset | Bits  | Parameter       | Format       | Range           |
|--------|-------|-----------------|--------------|-----------------|
| +0     | all   | Name            | ASCII        | 12 chars        |
| +13    | all   | OSC Semitone    | 64+/-24      | -24~0~+24       |
| +26    | all   | Panpot          | 0~64~127     | L64~CNT~R63     |
```

**Critical:** Note the exact notation used for each parameter type.

---

## Phase 2: Encoding Scheme Recognition

### Step 2.1: Recognize Encoding Patterns

**Common patterns in MIDI documentation:**

#### Pattern A: Unsigned (No Offset)
```
Notation:  "0~127"
Encoding:  Direct byte value
Example:   Cutoff: 0~127 → byte 0 = value 0, byte 127 = value 127
Code:      value = byte_value  # No conversion needed
```

#### Pattern B: Offset-64 (Korg Style) ⚠️ CRITICAL
```
Notation:  "64+/-X=0+/-X" or "0~64~127=L64~CNT~R63"
Encoding:  value = byte_value - 64
Example:   Panpot: 64+/-63 → byte 64 = value 0 (center)
Code:      value = byte_value - 64
           byte_value = value + 64
```

**Warning:** This is NOT signed 7-bit! Do not use bit 6 as a sign bit.

#### Pattern C: Offset-40 (Some Roland)
```
Notation:  "40+/-X"
Encoding:  value = byte_value - 40
Example:   byte 40 = value 0 (center)
Code:      value = byte_value - 40
           byte_value = value + 40
```

#### Pattern D: Signed 7-bit (Two's Complement)
```
Notation:  Explicitly states "bit 6 = sign" or shows binary
Encoding:  Bit 6 is sign bit, bits 0-5 are magnitude
Example:   byte 0-63 = +0 to +63, byte 64-127 = -64 to -1
Code:      value = byte_value - 128 if byte_value >= 64 else byte_value
```

#### Pattern E: Nibblized/Packed
```
Notation:  "B0~3", "B4~7" (bit ranges)
Encoding:  Multiple parameters packed into one byte
Example:   Byte bits 0-3 = source, bits 4-7 = destination
Code:      source = byte_value & 0x0F
           dest = (byte_value >> 4) & 0x0F
```

### Step 2.2: Create Encoding Helper Functions FIRST

**Before implementing full decoder, create and test these:**

```python
def _to_offset64(value: int, min_val: int = -64, max_val: int = 63) -> int:
    """For Korg-style 64+/-X notation."""
    if value < min_val or value > max_val:
        raise ValueError(f"Value {value} out of range {min_val}~{max_val}")
    return value + 64

def _from_offset64(byte_value: int) -> int:
    """For Korg-style 64+/-X notation."""
    return byte_value - 64

# Test these IMMEDIATELY:
assert _from_offset64(64) == 0    # Center
assert _from_offset64(0) == -64   # Min
assert _from_offset64(127) == 63  # Max
assert _to_offset64(0) == 64      # Center
assert _to_offset64(12) == 76     # Positive value
```

### Step 2.3: Document Your Interpretation

**Create an ENCODING_REFERENCE.md:**

```markdown
# {Manufacturer} {Model} Encoding Reference

## Parameter Encoding Types

### Type 1: Offset-64
- **Used for:** OSC2 semitone, panpot, filter modulation, etc.
- **Notation in docs:** "64+/-X=0+/-X"
- **Formula:** byte = value + 64
- **Test case:** value 0 → byte 64 ✓

### Type 2: Unsigned
- **Used for:** Levels, cutoff, resonance, etc.
...
```

---

## Phase 3: Test Suite Creation

### Step 3.1: Create Encoding Test Cases

**BEFORE implementing full decoder, create test suite:**

```python
import pytest

def test_offset64_encoding():
    """Test offset-64 encoding scheme."""
    # Edge cases (MOST IMPORTANT!)
    assert encode_offset64(-64) == 0    # Minimum
    assert encode_offset64(0) == 64     # Center (CRITICAL!)
    assert encode_offset64(63) == 127   # Maximum

    # Just above/below center
    assert encode_offset64(-1) == 63
    assert encode_offset64(1) == 65

    # Common musical values
    assert encode_offset64(12) == 76    # Octave
    assert encode_offset64(7) == 71     # Fifth

def test_offset64_decoding():
    """Test offset-64 decoding scheme."""
    assert decode_offset64(0) == -64
    assert decode_offset64(64) == 0     # Center (CRITICAL!)
    assert decode_offset64(127) == 63

def test_roundtrip_offset64():
    """Test encode → decode roundtrip."""
    for value in range(-64, 64):
        byte = encode_offset64(value)
        decoded = decode_offset64(byte)
        assert decoded == value, f"Roundtrip failed for {value}"
```

### Step 3.2: Create Test Patch Data

**Create minimal test patches with known values:**

```python
# test_patches.py
TEST_PATCH_CENTER_PAN = {
    "name": "Test Center Pan",
    "amp": {
        "panpot": 0  # Should encode to byte 64
    },
    # ... minimal other params
}

TEST_PATCH_OSC2_OCTAVE_UP = {
    "name": "Test OSC2 +12",
    "osc2": {
        "semitone": 12  # Should encode to byte 76
    },
    # ...
}

EXPECTED_BYTES = {
    "TEST_PATCH_CENTER_PAN": {
        26: 64,  # Offset +26 (panpot) should be byte 64
    },
    "TEST_PATCH_OSC2_OCTAVE_UP": {
        13: 76,  # Offset +13 (semitone) should be byte 76
    }
}
```

---

## Phase 4: Core Implementation

### Step 4.1: Implement Decoder First

**Order of implementation:**

1. ✅ SysEx unwrapping (remove header, decode 7-to-8 if needed)
2. ✅ Extract name/metadata (easy to verify)
3. ✅ Extract unsigned parameters (levels, cutoff, etc.)
4. ✅ Extract offset-64 parameters (with tests!)
5. ✅ Extract bit-packed parameters
6. ✅ Extract complex structures (envelopes, LFOs, etc.)

**Implementation pattern:**

```python
def extract_parameters(patch_bytes: bytes) -> dict:
    """Extract all parameters from patch bytes."""
    # Start with simple, verifiable fields
    name = patch_bytes[0:12].decode('ascii').rstrip()

    # Unsigned parameters (safe)
    cutoff = patch_bytes[20]
    resonance = patch_bytes[21]

    # Offset-64 parameters (use helper!)
    osc2_semitone = _from_offset64(patch_bytes[13])
    panpot = _from_offset64(patch_bytes[26])

    # Validate ranges
    assert -24 <= osc2_semitone <= 24, f"OSC2 semitone out of range: {osc2_semitone}"
    assert -64 <= panpot <= 63, f"Panpot out of range: {panpot}"

    return {
        "name": name,
        "filter": {"cutoff": cutoff, "resonance": resonance},
        "osc2": {"semitone": osc2_semitone},
        "amp": {"panpot": panpot},
        # ...
    }
```

### Step 4.2: Test Decoder with Factory Patches

**Load official factory patches and verify:**

```python
def test_decoder_with_factory_patches():
    """Test decoder with manufacturer's factory patches."""
    factory_syx = load_sysex("patches/factory/FactoryBank.syx")

    # Decode first patch
    patch = decode_patch(factory_syx[0])

    # Sanity checks
    assert len(patch["name"]) <= 12
    assert 0 <= patch["filter"]["cutoff"] <= 127

    # If you have documentation about factory patch A01:
    # assert patch["name"] == "Ambient Pad"  # Example

    # Check that offset-64 values are in expected ranges
    assert -24 <= patch["osc2"]["semitone"] <= 24
    assert -64 <= patch["amp"]["panpot"] <= 63
```

### Step 4.3: Implement Encoder

**After decoder works:**

```python
def build_patch_bytes(patch_dict: dict) -> bytes:
    """Build SysEx patch from JSON structure."""
    data = bytearray(PATCH_SIZE)

    # Name (pad to 12 chars)
    name_bytes = patch_dict["name"].ljust(12)[:12].encode('ascii')
    data[0:12] = name_bytes

    # Unsigned parameters
    data[20] = clamp_byte(patch_dict["filter"]["cutoff"])
    data[21] = clamp_byte(patch_dict["filter"]["resonance"])

    # Offset-64 parameters (use helper!)
    data[13] = _to_offset64(patch_dict["osc2"]["semitone"], -24, 24)
    data[26] = _to_offset64(patch_dict["amp"]["panpot"])

    return bytes(data)
```

### Step 4.4: Roundtrip Testing (CRITICAL!)

**This catches encoding bugs:**

```python
def test_roundtrip_encoding():
    """Test decode → encode → decode produces same result."""
    # Load factory patch
    original_bytes = load_factory_patch("A01")

    # Decode
    decoded = decode_patch(original_bytes)

    # Encode back
    encoded_bytes = encode_patch(decoded)

    # Compare byte-for-byte
    for i, (orig, enc) in enumerate(zip(original_bytes, encoded_bytes)):
        assert orig == enc, f"Byte {i}: original={orig:02X}, encoded={enc:02X}"

    # Or decode again and compare values
    re_decoded = decode_patch(encoded_bytes)
    assert re_decoded == decoded
```

---

## Phase 5: Hardware Verification

### Step 5.1: Create Hardware Test Patches

**DON'T SKIP THIS! This is where the MS2000 offset-64 bug was caught.**

**Create test patches with edge-case values:**

```python
test_patches = [
    {
        "name": "Test Pan Left",
        "amp": {"panpot": -64},  # Full left
    },
    {
        "name": "Test Pan Center",
        "amp": {"panpot": 0},  # Center (CRITICAL!)
    },
    {
        "name": "Test Pan Right",
        "amp": {"panpot": 63},  # Full right
    },
    {
        "name": "Test OSC2 Down",
        "osc2": {"semitone": -12},  # Octave down
    },
    {
        "name": "Test OSC2 Center",
        "osc2": {"semitone": 0},  # Unison (CRITICAL!)
    },
    {
        "name": "Test OSC2 Up",
        "osc2": {"semitone": 12},  # Octave up
    },
]
```

### Step 5.2: Hardware Verification Protocol

**Process:**

1. ✅ Encode test patches to SysEx
2. ✅ Send to hardware synthesizer
3. ✅ **Manually check EVERY test parameter on the synth display**
4. ✅ Compare displayed value with JSON value
5. ✅ Document discrepancies

**Verification checklist:**

```markdown
## Hardware Verification - Test Pan Center

**JSON Value:** `{"amp": {"panpot": 0}}`
**Expected on Synth:** Center (CNT or 0)
**Actual on Synth:** _________
**Status:** ☐ Pass ☐ Fail

If fail: Encoded byte was _____, synth shows _____
```

### Step 5.3: Fix Encoding Bugs

**If hardware values don't match:**

1. ⚠️ **DO NOT assume documentation is wrong**
2. ✅ Re-read documentation carefully
3. ✅ Check your encoding helper functions
4. ✅ Test with edge cases (especially center values like 0, 64)
5. ✅ Look for pattern mismatches (offset-64 vs signed 7-bit)

**Common bug patterns:**

```python
# WRONG - Using signed 7-bit for offset-64
def encode_panpot_WRONG(value):
    return value if value >= 0 else value + 128  # ✗

# CORRECT - Using offset-64
def encode_panpot_CORRECT(value):
    return value + 64  # ✓
```

---

## Phase 6: Patch Generation

### Step 6.1: Understand Patch Design Principles

**If creating sound-design patches (like BOC):**

1. ✅ Read comprehensive sound design guides
2. ✅ Analyze existing patches statistically
3. ✅ Document parameter distributions and ranges
4. ✅ Create recipe archetypes based on analysis

**Example from MS2000 BOC implementation:**

```python
# Based on analysis of 123 BOC patches
BOC_PARAMS = {
    'delay_type': 'L/R Delay',  # 77% of patches
    'delay_depth': (80, 100),   # High feedback
    'mod_type': 'Cho/Flg',      # 72% of patches
    'filter_type': '12dB LPF',  # 52% of patches
    'resonance': (10, 25),      # LOW resonance (key characteristic)
    'lfo1_wave': 'Triangle',    # 89% of patches
    'lfo2_wave': 'Sine',        # 83% of patches
}
```

### Step 6.2: Hardware Verify Generated Patches

**CRITICAL: Test generated patches on hardware BEFORE releasing:**

```python
# Generate patches
patches = generate_boc_originals(count=128)

# Encode to SysEx
sysex_data = encode_bank(patches)

# Save and send to hardware
write_sysex("test_bank.syx", sysex_data)

# USER MUST:
# 1. Load onto hardware
# 2. Play through several patches
# 3. Check key parameters match expectations
# 4. Listen for sonic characteristics
```

**If patches don't sound right:**
- Check encoding (especially offset-64!)
- Verify parameter ranges
- Check for out-of-bounds values

---

## Common Pitfalls

### Pitfall 1: Misinterpreting Offset Notation ⚠️ CRITICAL

**Problem:** Seeing `64+/-X` and thinking it's signed 7-bit

**Solution:**
- `64+/-X=0+/-X` means offset-64 (add 64 to encode)
- True signed 7-bit will explicitly say "bit 6 = sign"
- Test with center value (0 should encode to 64)

### Pitfall 2: Not Testing Edge Cases

**Problem:** Testing with random values, missing edge cases

**Solution:**
- ALWAYS test: minimum, maximum, center, ±1 from center
- Center values (0, 64) expose encoding bugs immediately

### Pitfall 3: Skipping Hardware Verification

**Problem:** Assuming implementation is correct without hardware test

**Solution:**
- Create hardware test patches EARLY
- Verify edge cases on actual hardware
- Don't wait until full implementation

### Pitfall 4: Assuming Documentation is Wrong

**Problem:** When hardware doesn't match, blame the docs

**Solution:**
- Documentation is usually correct (manufacturers test this)
- Re-read notation carefully
- Check YOUR implementation first
- Compare with other implementations if available

### Pitfall 5: Not Doing Roundtrip Testing

**Problem:** Only testing decode OR encode, not both

**Solution:**
- Always test: original → decode → encode → compare bytes
- Catches encoding bugs before hardware testing

### Pitfall 6: Ignoring Parameter Ranges

**Problem:** Not validating values are in expected ranges

**Solution:**
```python
def _to_offset64(value, min_val=-64, max_val=63):
    if value < min_val or value > max_val:
        raise ValueError(f"Out of range: {value}")  # Catch early!
    return value + 64
```

---

## Implementation Checklist

### Phase 1: Documentation ☐
- [ ] Downloaded official MIDI implementation docs
- [ ] Identified SysEx message format
- [ ] Created parameter offset table
- [ ] Documented encoding schemes found
- [ ] Created ENCODING_REFERENCE.md

### Phase 2: Encoding Recognition ☐
- [ ] Identified all encoding pattern types (unsigned, offset-64, etc.)
- [ ] Created encoding helper functions
- [ ] Tested helper functions with edge cases
- [ ] Documented interpretation of notation

### Phase 3: Test Suite ☐
- [ ] Created encoding unit tests (min, max, center values)
- [ ] Created roundtrip tests
- [ ] Created test patch data with known values
- [ ] All tests passing

### Phase 4: Implementation ☐
- [ ] Implemented decoder (name, metadata, params)
- [ ] Tested decoder with factory patches
- [ ] Implemented encoder
- [ ] Roundtrip testing passes (byte-perfect)
- [ ] Parameter validation in place

### Phase 5: Hardware Verification ☐
- [ ] Created hardware test patches (edge cases)
- [ ] Sent test patches to hardware
- [ ] Manually verified EVERY parameter on hardware
- [ ] All values match JSON ✓
- [ ] Fixed any encoding bugs found
- [ ] Re-verified fixes on hardware

### Phase 6: Patch Generation (Optional) ☐
- [ ] Studied sound design guides
- [ ] Analyzed existing patches
- [ ] Created generation scripts
- [ ] Generated test patches
- [ ] Hardware verified generated patches sound correct

### Phase 7: Documentation ☐
- [ ] Created README for manufacturer/model
- [ ] Documented encoding quirks
- [ ] Created bug analysis if issues found
- [ ] Updated main project documentation

---

## Template Files

### Encoding Reference Template

```markdown
# {Manufacturer} {Model} - Encoding Reference

## SysEx Format
- Header: F0 XX XX ...
- Patch size: XXX bytes
- Encoding: 7-to-8 / nibblized / direct

## Encoding Schemes

### Offset-64 Parameters
Used for: [list parameters]
Notation in docs: "64+/-X"
Formula: byte = value + 64

### Unsigned Parameters
Used for: [list parameters]
Notation: "0~127"
Formula: byte = value

## Edge Case Tests
- [ ] Center pan (0) → byte 64 ✓
- [ ] OSC semitone (0) → byte 64 ✓
...
```

### Hardware Verification Template

```markdown
# Hardware Verification Log - {Model}

## Test Patch: Center Values
Date: YYYY-MM-DD
Firmware: X.X.X

| Parameter | JSON Value | Expected Byte | Synth Display | Status |
|-----------|------------|---------------|---------------|---------|
| Panpot    | 0          | 64           | CNT           | ✓ Pass  |
| OSC2 Semi | 0          | 64           | 0             | ✓ Pass  |
| Filter EG1| -31        | 33           | -31           | ✓ Pass  |

## Issues Found
None - all parameters match!

## Sign-off
Verified by: [USER]
All offset-64 parameters working correctly.
```

---

## Quick Reference: Encoding Pattern Recognition

```python
# Quick decision tree for encoding schemes:

if documentation says "0~127":
    # Unsigned - no conversion
    byte_value = value

elif documentation says "64+/-X=0+/-X":
    # Offset-64 (Korg style)
    byte_value = value + 64
    value = byte_value - 64

elif documentation says "40+/-X":
    # Offset-40 (some Roland)
    byte_value = value + 40
    value = byte_value - 40

elif documentation explicitly says "bit 6 = sign":
    # Signed 7-bit
    byte_value = value if value >= 0 else value + 128
    value = byte_value - 128 if byte_value >= 64 else byte_value

elif documentation shows bit ranges "B0~3", "B4~7":
    # Bit-packed
    value1 = byte_value & 0x0F
    value2 = (byte_value >> 4) & 0x0F
```

---

## Summary for AI Agents

**When implementing a new manufacturer:**

1. 📖 **Read docs carefully** - notation matters
2. 🧪 **Test encoding FIRST** - before full implementation
3. 🎯 **Edge cases are critical** - especially center values (0, 64)
4. 🔄 **Roundtrip test everything** - catches encoding bugs
5. 🎛️ **Hardware verify EARLY** - don't wait until the end
6. ✅ **Trust the documentation** - manufacturers test this
7. 🐛 **Document bugs found** - help future implementations

**The MS2000 offset-64 bug could have been avoided by:**
- Testing with center value (0) early
- Hardware verification before full implementation
- Recognizing `64+/-X` notation pattern
- Creating encoding test suite first

**Follow this guide to avoid similar bugs!**

---

**Document Version:** 1.0
**Based On:** Korg MS2000 implementation (2025-10-25)
**Next Update:** After Roland/Yamaha/Sequential implementation
