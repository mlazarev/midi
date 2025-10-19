# MIDI and SysEx Learning Summary

This document summarizes our comprehensive exploration of MIDI (Musical Instrument Digital Interface) and System Exclusive (SysEx) messages, with specific focus on the Korg MS2000 synthesizer implementation.

## Table of Contents
1. [MIDI Fundamentals](#midi-fundamentals)
2. [System Exclusive (SysEx) Messages](#system-exclusive-sysex-messages)
3. [Korg MS2000 Implementation](#korg-ms2000-implementation)
4. [7-to-8 Bit Encoding](#7-to-8-bit-encoding)
5. [Practical Decoding](#practical-decoding)
6. [Key Insights](#key-insights)

---

## MIDI Fundamentals

### What is MIDI?
MIDI (Musical Instrument Digital Interface) is a technical standard that describes a communications protocol, digital interface, and electrical connectors that connect a wide variety of electronic musical instruments, computers, and related audio devices.

**Key Facts:**
- Standardized in 1983 by Dave Smith (Sequential Circuits) and Ikutaro Kakehashi (Roland)
- Serial communication at 31,250 bits/second (31.25 kbaud)
- 8-bit bytes, but only 7 bits used for data (MSB is status/data flag)
- Data values range from 0-127 (0x00-0x7F)

### MIDI Message Types

#### 1. Channel Messages (0x80-0xEF)
Messages that target specific MIDI channels (1-16):
- **Note On** (0x9n): Trigger a note with velocity
- **Note Off** (0x8n): Release a note
- **Control Change** (0xBn): Modify controller parameters (mod wheel, sustain, etc.)
- **Program Change** (0xCn): Select a patch/program
- **Pitch Bend** (0xEn): Bend pitch up or down
- **Channel Pressure** (0xDn): Aftertouch pressure

Where `n` is the MIDI channel (0-F for channels 1-16).

#### 2. System Messages (0xF0-0xFF)
Messages that affect the entire system:
- **System Exclusive** (0xF0...0xF7): Manufacturer-specific data
- **System Common**: Song position, timing, etc.
- **System Real-Time**: MIDI clock, start, stop, continue

### NRPN (Non-Registered Parameter Numbers)
A method to extend MIDI control beyond the standard 128 Control Change messages:
- Uses CC #99 (NRPN MSB) and CC #98 (NRPN LSB) to select parameter
- Uses CC #6 (Data Entry MSB) to set the value
- Allows access to manufacturer-specific parameters

---

## System Exclusive (SysEx) Messages

### Structure
SysEx messages allow manufacturers to send device-specific data:

```
F0              - SysEx start byte
<manufacturer>  - Manufacturer ID (1 or 3 bytes)
<device>        - Device/model identifier
<data>          - Arbitrary data (all bytes must be 0x00-0x7F)
F7              - End of Exclusive (EOX)
```

### Manufacturer IDs
- Korg: 0x42
- Roland: 0x41
- Yamaha: 0x43
- Sequential/Dave Smith: 0x01
- (Many others...)

### Why SysEx?
- Transfer patch/program data between devices and computers
- Dump entire synth memory for backup
- Remote parameter editing
- Firmware updates
- Identity requests (Universal SysEx)

---

## Korg MS2000 Implementation

### Device Identification
- **Manufacturer ID**: 0x42 (Korg)
- **Device Family ID**: 0x58 (MS2000 Series)
- **Member ID**:
  - 0x01 = MS2000 (keyboard version)
  - 0x08 = MS2000R (rack version)

### SysEx Header Format
```
F0 42 3g 58 [function] [data...] F7
```
Where:
- `3g` = MIDI channel (30-3F for channels 0-15)
- `58` = MS2000 device ID
- `[function]` = Message type

### Function IDs

| Function | Hex | Description |
|----------|-----|-------------|
| CURRENT PROGRAM DATA DUMP | 0x40 | Dump edit buffer (one patch) |
| PROGRAM DATA DUMP | 0x4C | Dump all 128 programs |
| GLOBAL DATA DUMP | 0x51 | Dump global settings |
| ALL DATA DUMP | 0x50 | Dump programs + global |
| PARAMETER CHANGE | 0x41 | Change single parameter |
| MODE DATA | 0x42 | Report current mode |

### Request Messages

| Function | Hex | Description |
|----------|-----|-------------|
| MODE REQUEST | 0x12 | Request current mode |
| CURRENT PROGRAM DUMP REQUEST | 0x10 | Request edit buffer |
| PROGRAM DUMP REQUEST | 0x1C | Request all programs |
| GLOBAL DUMP REQUEST | 0x0E | Request global data |
| ALL DATA DUMP REQUEST | 0x0F | Request everything |

### Program Data Structure
Each program/patch consists of **254 bytes** containing:

| Bytes | Parameter | Description |
|-------|-----------|-------------|
| 0-11 | Program Name | 12 ASCII characters |
| 12-15 | Reserved | Not used |
| 16 | Voice Mode | Single/Split/Layer/Vocoder |
| 17 | Scale | Key and type |
| 18 | Split Point | Keyboard split point |
| 19-22 | Delay FX | Sync, timebase, time, depth, type |
| 23-25 | Mod FX | LFO speed, depth, type |
| 26-29 | EQ | Hi/Low frequency and gain |
| 30-33 | Arpeggiator | Tempo, on/off, latch, type, range |
| 34+ | Oscillators, Filters, Envelopes, etc. |

---

## 7-to-8 Bit Encoding

### The Problem
MIDI data bytes must have bit 7 = 0 (values 0-127). To transmit 8-bit data (values 0-255) through MIDI, Korg uses a packing scheme.

### The Solution: Bit Packing
Every 7 bytes of 8-bit data are packed into 8 bytes of 7-bit MIDI data:

```
Original Data (7 bytes of 8-bit):
  [7n+0] [7n+1] [7n+2] [7n+3] [7n+4] [7n+5] [7n+6]
  b7...b0 for each byte

Encoded MIDI Data (8 bytes of 7-bit):
  [Byte 0]: 0 b7₆ b7₅ b7₄ b7₃ b7₂ b7₁ b7₀  ← MSB byte (contains bit 7 of next 7 bytes)
  [Byte 1]: 0 b6...b0 of 7n+0
  [Byte 2]: 0 b6...b0 of 7n+1
  [Byte 3]: 0 b6...b0 of 7n+2
  [Byte 4]: 0 b6...b0 of 7n+3
  [Byte 5]: 0 b6...b0 of 7n+4
  [Byte 6]: 0 b6...b0 of 7n+5
  [Byte 7]: 0 b6...b0 of 7n+6
```

Where b7₆ means "bit 7 from byte 7n+6", etc.

### Encoding Efficiency
- 7 bytes → 8 bytes = 14.3% overhead
- 254 bytes of patch data → ~291 bytes encoded
- 128 patches (32,512 bytes) → ~37,157 bytes encoded

### Decoding Algorithm
```python
def decode_korg_7bit(encoded_data):
    decoded = bytearray()
    i = 0

    while i + 8 <= len(encoded_data):
        msb_byte = encoded_data[i]  # First byte has MSBs

        for j in range(7):  # Next 7 bytes have data
            lower_7 = encoded_data[i + 1 + j] & 0x7F
            msb = (msb_byte >> (6 - j)) & 0x01
            full_byte = (msb << 7) | lower_7
            decoded.append(full_byte)

        i += 8

    return bytes(decoded)
```

**Critical Insight:** The encoding applies to the **entire data block**, not individual patches. You must decode the entire stream first, then extract fixed-size patches.

---

## Practical Decoding

### File Structure

**OriginalPatches.syx:**
```
Size: 36,000 bytes
Structure:
  - 5 bytes: Header (F0 42 30 58 4C)
  - 35,995 bytes: Encoded data
  - Decoded: 31,496 bytes = 124 patches × 254 bytes
  - Contains factory presets with names
```

**BOCPatches.syx:**
```
Size: 37,158 bytes
Structure:
  - 5 bytes: Header (F0 42 30 58 4C)
  - 37,153 bytes: Encoded data
  - Decoded: 32,514 bytes = 128 patches × 254 bytes (full bank)
  - Contains custom patches (names appear blank/minimal)
```

### Decoding Process
1. Read file, verify header bytes (F0 42 30 58 4C)
2. Extract encoded data (skip 5-byte header)
3. Decode ENTIRE stream using 7-to-8 bit algorithm
4. Extract patches as sequential 254-byte chunks
5. Parse each patch according to parameter table

### Python Implementation
See `decode_sysex.py` for complete implementation:
- `decode_korg_7bit()` - Decodes 7-to-8 bit stream
- `MS2000Patch` class - Parses patch parameters
- `parse_sysex_file()` - Complete file parsing
- Command-line tool for easy decoding

---

## Key Insights

### MIDI Protocol Insights
1. **7-bit limitation is fundamental** - Status bytes (bit 7 = 1) vs Data bytes (bit 7 = 0)
2. **Efficiency matters** - 31,250 baud is slow by modern standards
3. **Extensibility through SysEx** - Manufacturers can extend MIDI infinitely
4. **NRPN provides middle ground** - More parameters without full SysEx complexity

### SysEx Implementation Insights
1. **Encoding applies to blocks, not messages** - Don't decode individual patches
2. **Always verify headers** - Check manufacturer ID and device ID
3. **Documentation is essential** - Bit-level specifications are critical
4. **ASCII in MIDI is common** - Patch names, display text (but must be < 128)

### Reverse Engineering Insights
1. **Start with known data** - Patch names visible in hex dump
2. **Look for patterns** - Repeating structures indicate encoding
3. **Calculate sizes** - File size math reveals structure
4. **Test incrementally** - Decode one patch before attempting all
5. **Read specs carefully** - Diagrams show exact bit layouts

### Practical Applications
1. **Patch librarian software** - Organize and backup synth patches
2. **Sound design sharing** - Exchange patches between musicians
3. **Automated testing** - Generate parameter sweeps programmatically
4. **Education** - Understand synthesis by examining patch parameters
5. **Archival** - Preserve sounds from vintage equipment

---

## Files in This Project

### Documentation
- `general/docs/sysex/MIDI.pdf` - Wikipedia overview of MIDI
- `general/docs/sysex/Everything You Ever Wanted To Know About System Exclusive.pdf` - Sound on Sound article
- `korgms2000/docs/MS2000_MIDIimp.TXT` - Complete MIDI implementation chart
- `korgms2000/docs/MS2000_FMIDIDef/` - FreeMIDI device definitions

### SysEx Files
- `korgms2000/sysex/OriginalPatches.syx` - 124 factory patches
- `korgms2000/sysex/BOCPatches.syx` - 128 custom patches

### Tools
- `decode_sysex.py` - Python decoder for MS2000 SysEx files
- `original_patches_decoded.txt` - Decoded factory patches
- `boc_patches_decoded.txt` - Decoded custom patches

---

## Further Learning

### Topics to Explore
1. **MIDI 2.0** - Modern extension with higher resolution and bidirectional communication
2. **MPE (MIDI Polyphonic Expression)** - Per-note control for expressive instruments
3. **OSC (Open Sound Control)** - Alternative to MIDI for modern networks
4. **Max/MSP, Pure Data** - Visual programming for MIDI
5. **DAW Automation** - MIDI control in production environments

### Hands-On Projects
1. Build a MIDI monitor to visualize messages in real-time
2. Create a patch randomizer for the MS2000
3. Write a patch comparison tool to find similar sounds
4. Develop a MIDI arpeggiator or sequencer
5. Implement bidirectional SysEx communication with hardware

### References
- [MIDI Association](https://www.midi.org/) - Official MIDI specifications
- [MIDI Implementation Chart Guide](https://www.midi.org/specifications/midi1-specifications/midi-1-addenda/midi-implementation-chart-instructions) - How to read implementation docs
- [Korg MS2000 Manual](https://www.korg.com/us/support/download/product/0/158/) - Full synthesizer documentation

---

## Conclusion

This exploration demonstrated the complete journey from MIDI theory to practical SysEx decoding:

1. **Conceptual Understanding** - MIDI protocol, message types, 7-bit limitation
2. **Manufacturer Implementation** - Korg's specific SysEx format and device IDs
3. **Encoding Mechanics** - 7-to-8 bit packing algorithm
4. **Reverse Engineering** - Analyzing binary files to understand structure
5. **Implementation** - Building a working decoder from specifications

The MS2000 SysEx format exemplifies typical synthesizer implementations while teaching fundamental concepts applicable to any MIDI device. The 7-to-8 bit encoding, while initially confusing, reveals elegant engineering solving the 7-bit data constraint.

Most importantly: **MIDI remains relevant 40+ years later** because its extensibility (via SysEx, NRPN, and now MIDI 2.0) allows evolution while maintaining backward compatibility with decades of equipment.

---

*Generated through interactive exploration of MIDI and SysEx with Claude Code*
*Date: 2025-01-19*
