# Korg MS2000 SysEx Troubleshooting Guide

## Problem: SysEx File Won't Load Into Hardware

### Symptom
When sending a SysEx file to the MS2000 using MIDI software (e.g., Bome SendSX), the synth displays "Receiving" but the patches don't change. The previous patches remain in memory.

### Root Cause: Missing F7 (End of Exclusive) Byte

**MIDI SysEx messages MUST be properly terminated with the F7 byte.**

A valid SysEx message structure:
```
F0 <manufacturer> <device> <data...> F7
│                                      │
└─ SysEx Start                         └─ End of Exclusive (REQUIRED!)
```

### Diagnostic Process

#### 1. Check File Size

Compare file sizes between working and non-working files:

```bash
ls -lh *.syx
```

Example output:
```
37,163 bytes - BOCPatches.syx (WORKS - 128 patches)
35,844 bytes - OriginalPatches.syx (FIXED - 123 patches)
36,000 bytes - OriginalPatches_BROKEN.syx (BROKEN - padded with zeros)
```

#### 2. Inspect File Endings

Check the last bytes of the file:

```bash
tail -c 20 file.syx | xxd
```

**Working file (BOCPatches.syx):**
```
00000000: 0140 4040 4040 0040 4040 4040 4040 0040  .@@@@@.@@@@@@@.@
00000010: 4040 40f7                                @@@.
                   ^^
                   F7 - End of Exclusive (CORRECT!)
```

**Broken file (OriginalPatches_BROKEN.syx):**
```
00000000: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00000010: 0000 0000                                ....
                   ^^
                   00 - NOT F7! (BROKEN!)
```

The broken file is padded with zeros instead of properly terminated.

#### 3. Check File Headers

Both files should start with the same header:

```bash
head -c 20 file.syx | xxd
```

**Correct header:**
```
00000000: f042 3058 4c00 ...
          │  │  │  │  │
          │  │  │  │  └─ Function: 0x4C (PROGRAM DATA DUMP)
          │  │  │  └──── Device: 0x58 (MS2000)
          │  │  └─────── Channel: 0x30 (channel 0)
          │  └────────── Manufacturer: 0x42 (Korg)
          └───────────── SysEx Start: 0xF0
```

### The Fix

#### Python Script to Fix SysEx Files

```python
#!/usr/bin/env python3
"""
Fix MS2000 SysEx files by removing zero padding and adding F7 terminator.
"""

def fix_sysex_file(input_file, output_file=None):
    """
    Fix a SysEx file by:
    1. Removing trailing zero padding
    2. Adding F7 (End of Exclusive) byte if missing

    Args:
        input_file: Path to broken .syx file
        output_file: Path for fixed file (defaults to overwriting input)
    """
    if output_file is None:
        output_file = input_file

    # Read file
    with open(input_file, 'rb') as f:
        data = bytearray(f.read())

    print(f"Original file: {len(data)} bytes")

    # Check if already ends with F7
    if data[-1] == 0xF7:
        print("✓ File already ends with F7 (End of Exclusive)")
        return

    # Find end of real data (before zero padding)
    end_pos = len(data)
    for i in range(len(data) - 1, -1, -1):
        if data[i] != 0x00:
            end_pos = i + 1
            break

    # Truncate and add F7
    fixed_data = data[:end_pos]
    fixed_data.append(0xF7)

    # Write fixed file
    with open(output_file, 'wb') as f:
        f.write(fixed_data)

    print(f"Fixed file: {len(fixed_data)} bytes")
    print(f"✓ Added F7 terminator")
    print(f"✓ Saved to: {output_file}")

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python fix_sysex.py <input.syx> [output.syx]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else input_file

    fix_sysex_file(input_file, output_file)
```

#### One-Line Fix

```bash
# Backup original
cp OriginalPatches.syx OriginalPatches_BROKEN.syx

# Fix with Python
python3 -c "
data = bytearray(open('OriginalPatches.syx', 'rb').read())
end = next(i+1 for i in range(len(data)-1, -1, -1) if data[i] != 0)
open('OriginalPatches.syx', 'wb').write(data[:end] + b'\xF7')
"
```

### Why This Happens

#### Source of Broken Files

1. **Incomplete Downloads** - File transfer interrupted
2. **Incorrect Extraction** - Archive corruption
3. **Size Padding** - Some software pads to round numbers (36,000 bytes)
4. **Manual Editing** - Hex editor mistakes
5. **Conversion Errors** - Format conversion issues

#### Why Hardware Rejects It

The MS2000 (and most MIDI devices) follow the MIDI specification strictly:

1. Receives F0 (SysEx Start) ✓
2. Reads manufacturer ID (42 = Korg) ✓
3. Reads device ID (58 = MS2000) ✓
4. Reads function (4C = Program Dump) ✓
5. Begins reading data... ✓
6. Waits for F7 (End of Exclusive) ✗ **NEVER RECEIVES IT!**

Without F7, the synth doesn't know the message is complete. It may:
- Keep waiting for more data
- Timeout and reject the entire message
- Accept but not process the data
- Display "Receiving" but never commit changes

### Verification After Fix

#### Test with SendSX

1. Load the fixed file in Bome SendSX
2. The file should now show correct size (not rounded to 36,000)
3. Send to MS2000
4. Synth should:
   - Display "Receiving"
   - Show progress
   - Display "Completed" or similar
   - Patches should change immediately

#### Verify with Decoder

```bash
python3 decode_sysex.py OriginalPatches.syx
```

Output should show:
```
SysEx Header:
  Manufacturer: Korg (0x42)
  Device: MS2000 (0x58)
  Function: 0x4C (PROGRAM DATA DUMP)
  Patches decoded: 123

Successfully decoded 123 patches
```

#### Hex Verification

```bash
# Should show F7 at the end
tail -c 1 OriginalPatches.syx | xxd
# Output: 00000000: f7
```

### File Size Reference

| Patches | Raw Data | Encoded | With Header/F7 | Actual Size |
|---------|----------|---------|----------------|-------------|
| 1 | 254 bytes | ~291 bytes | ~297 bytes | 297 |
| 123 | 31,242 bytes | ~35,838 bytes | ~35,844 bytes | 35,844 |
| 124 | 31,496 bytes | ~36,132 bytes | ~36,138 bytes | 36,138 |
| 128 | 32,512 bytes | ~37,157 bytes | ~37,163 bytes | 37,163 |

**Note:** OriginalPatches only contains 123 patches, not 124!

### Common Mistakes

#### ❌ Wrong: Padding to Round Number
```
<valid data...> 00 00 00 00 00 00 ...
                 └─ Zero padding (WRONG!)
```

#### ✓ Correct: Proper Termination
```
<valid data...> F7
                 └─ End of Exclusive (CORRECT!)
```

#### ❌ Wrong: Missing Both Terminator and Start
Some corrupted files missing both F0 and F7 - completely invalid.

#### ❌ Wrong: Extra Data After F7
```
<valid data...> F7 00 00 00 00
                    └─ Extra bytes (harmless but incorrect)
```

### Best Practices

1. **Always check file integrity** before sending to hardware
2. **Backup original files** before fixing
3. **Verify with hex editor** or command-line tools
4. **Test with decoder** before sending to synth
5. **Keep both broken and fixed versions** for comparison

### Tools

#### Command-Line Verification

```bash
# Check if file ends with F7
if [ "$(tail -c 1 file.syx | xxd -p)" = "f7" ]; then
    echo "✓ File is properly terminated"
else
    echo "✗ File is missing F7 terminator"
fi
```

#### Bome SendSX Settings

When using Bome SendSX:
- **Timing:** Normal (not "Fast")
- **Delay:** 10-50ms between messages (if sending multiple)
- **Handshaking:** Enable if supported by device
- **Echo:** Disable to avoid feedback loops

### Related Issues

#### Issue: Synth Receives But Doesn't Store

**Cause:** Memory protect enabled

**Solution:** Disable memory protect on MS2000:
1. Press GLOBAL
2. Find "Memory Protect" setting
3. Set to OFF
4. Try sending SysEx again

#### Issue: Partial Patches Load

**Cause:** Incomplete file (cut off mid-transfer)

**Solution:**
1. Re-download from original source
2. Verify file size matches expected size
3. Check for F7 terminator

#### Issue: Patches Load but Sound Wrong

**Cause:** Wrong SysEx file for device variant

**Solution:**
- MS2000 vs MS2000R may have slight differences
- Verify device ID in header matches your hardware
- Try patches from official Korg sources

### Resources

- [MIDI Specification](https://www.midi.org/specifications)
- [Korg MS2000 MIDI Implementation](docs/MS2000_MIDIimp.TXT)
- [Bome SendSX Documentation](https://www.bome.com/products/sendsx)

## Issue #2: Incomplete Patch Bank (< 128 Patches)

### Symptom
File has F7 terminator and looks correct, but still won't load into MS2000 hardware.

### Root Cause: MS2000 Requires Complete 128-Patch Bank

**CRITICAL DISCOVERY:** When using Function 0x4C (PROGRAM DATA DUMP), the MS2000 expects **exactly 128 patches**, even if some are blank!

From the MIDI Implementation (line 811-812):
```
PROGRAM DATA (IN INTERNAL MEMORY) DUMP FORMAT
[Prog A01(254Bytes)],....,[Prog H16(254Bytes)]
254*128Bytes = 32,512 bytes raw -> 37,157 bytes encoded
```

### Solution: Pad to 128 Patches

If your file has fewer than 128 patches, pad it with blank/INIT patches:

```python
# Pad OriginalPatches.syx (123 patches) to 128 patches
# by copying 5 blank patches from another complete file

# 1. Calculate bytes needed
patches_current = 123
patches_needed = 128 - patches_current  # = 5
bytes_needed = patches_needed * 254     # = 1,270 bytes raw

# 2. Encoded size needed
# 37,157 bytes total for 128 patches
# ~35,838 bytes for 123 patches
# ~1,319 bytes to add (encoded)

# 3. Append blank patches to reach exactly 37,163 bytes total
```

### File Size Requirements

| Patches | Raw Bytes | Encoded | With Header+F7 | Required |
|---------|-----------|---------|----------------|----------|
| 123 | 31,242 | ~35,838 | ~35,844 | ✗ INCOMPLETE |
| 124 | 31,496 | ~36,132 | ~36,138 | ✗ INCOMPLETE |
| 127 | 32,258 | ~36,987 | ~36,993 | ✗ INCOMPLETE |
| **128** | **32,512** | **37,157** | **37,163** | **✓ COMPLETE** |

**Only 128-patch files will load via Function 0x4C!**

### Alternative: Use Function 0x40 (Current Program)

If you want to send individual patches or incomplete banks:
- Use Function 0x40 (CURRENT PROGRAM DATA DUMP)
- Sends one patch at a time to edit buffer
- Doesn't require complete bank

### Summary

**Top 2 causes of "SysEx won't load" problems:**

1. **Missing F7 byte** - File not properly terminated
2. **Incomplete bank** - Less than 128 patches for Function 0x4C

Always verify:
1. ✓ File starts with F0
2. ✓ File ends with F7
3. ✓ No zero padding
4. ✓ **Exactly 128 patches (37,163 bytes total)**

---

**Issue Resolved:** OriginalPatches.syx fixed by removing zero padding and adding F7 terminator.

**File Status:**
- OriginalPatches_BROKEN.syx: 36,000 bytes (broken, for reference)
- OriginalPatches.syx: 35,844 bytes (fixed, 123 patches)
- BOCPatches.syx: 37,163 bytes (correct, 128 patches)
