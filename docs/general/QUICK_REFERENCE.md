# MIDI & SysEx Quick Reference

## MIDI Message Structure

### Status Bytes (bit 7 = 1)
```
Channel Messages:  0x80-0xEF
System Messages:   0xF0-0xFF
```

### Channel Messages
| Status | Message | Data Bytes | Description |
|--------|---------|------------|-------------|
| 0x8n | Note Off | key, velocity | Release note |
| 0x9n | Note On | key, velocity | Trigger note (vel=0 = Note Off) |
| 0xBn | Control Change | controller, value | Modify parameter |
| 0xCn | Program Change | program | Select patch (0-127) |
| 0xDn | Channel Pressure | pressure | Aftertouch |
| 0xEn | Pitch Bend | lsb, msb | Pitch wheel |

*n = MIDI channel (0-F for channels 1-16)*

### Common Control Changes (0xBn)
| CC# | Hex | Name | Range |
|-----|-----|------|-------|
| 1 | 0x01 | Modulation Wheel | 0-127 |
| 7 | 0x07 | Volume | 0-127 |
| 10 | 0x0A | Pan | 0=left, 64=center, 127=right |
| 11 | 0x0B | Expression | 0-127 |
| 64 | 0x40 | Sustain Pedal | 0-63=off, 64-127=on |
| 98 | 0x62 | NRPN LSB | Parameter select (LSB) |
| 99 | 0x63 | NRPN MSB | Parameter select (MSB) |
| 6 | 0x06 | Data Entry MSB | NRPN value |

### System Messages
| Status | Name | Data | Description |
|--------|------|------|-------------|
| 0xF0 | SysEx Start | ... | Begin manufacturer-specific data |
| 0xF7 | SysEx End | - | End manufacturer-specific data |
| 0xF8 | Timing Clock | - | 24 per quarter note |
| 0xFA | Start | - | Start sequence |
| 0xFC | Stop | - | Stop sequence |

## SysEx Message Format

### Basic Structure
```
F0                    - Start of SysEx
<manufacturer_id>     - 1 or 3 bytes
<device_id>          - Device/model identifier (optional)
<function_id>        - Command type (optional)
<data>               - Arbitrary data (all bytes 0x00-0x7F)
F7                    - End of SysEx
```

### Common Manufacturer IDs
| ID | Hex | Manufacturer |
|----|-----|--------------|
| Korg | 0x42 | Korg |
| Roland | 0x41 | Roland |
| Yamaha | 0x43 | Yamaha |
| Sequential | 0x01 | Sequential Circuits / Dave Smith |
| Moog | 0x04 | Moog Music |

### Universal SysEx
```
F0 7E <device_id> <sub_id> <data> F7    - Non-Realtime
F0 7F <device_id> <sub_id> <data> F7    - Realtime
```

**Common Universal SysEx:**
- Device Inquiry: `F0 7E 7F 06 01 F7` (request device info)
- Master Volume: `F0 7F 7F 04 01 <lsb> <msb> F7`

## Korg MS2000 SysEx

### Header Format
```
F0 42 3g 58 <function> <data> F7
│  │  │  │   └─ Function ID
│  │  │  └───── Device: 0x58 = MS2000
│  │  └──────── MIDI Channel: 3g (g = 0-F)
│  └─────────── Manufacturer: 0x42 = Korg
└────────────── SysEx Start
```

### Function IDs
| Hex | Function | Direction | Description |
|-----|----------|-----------|-------------|
| 0x10 | Current Program Dump Request | TX | Request edit buffer |
| 0x40 | Current Program Data Dump | RX/TX | Edit buffer (1 patch) |
| 0x1C | Program Dump Request | TX | Request all programs |
| 0x4C | Program Data Dump | RX/TX | All 128 programs |
| 0x0E | Global Dump Request | TX | Request global data |
| 0x51 | Global Data Dump | RX/TX | Global settings |
| 0x0F | All Data Dump Request | TX | Request everything |
| 0x50 | All Data Dump | RX/TX | Programs + Global |
| 0x11 | Program Write Request | TX | Write to memory |
| 0x41 | Parameter Change | RX/TX | Single parameter edit |
| 0x12 | Mode Request | TX | Request current mode |
| 0x42 | Mode Data | TX | Current mode response |

## 7-to-8 Bit Encoding (Korg)

### The Problem
MIDI data bytes must have bit 7 = 0 (values 0-127).
To send 8-bit data (0-255), need encoding scheme.

### The Solution
Pack 7 bytes of 8-bit data into 8 bytes of 7-bit data:

```
Input: 7 bytes of 8-bit data
  Byte 0: b7 b6 b5 b4 b3 b2 b1 b0
  Byte 1: b7 b6 b5 b4 b3 b2 b1 b0
  ...
  Byte 6: b7 b6 b5 b4 b3 b2 b1 b0

Output: 8 bytes of 7-bit data
  Byte 0: 0 b7₆ b7₅ b7₄ b7₃ b7₂ b7₁ b7₀  ← MSB byte
  Byte 1: 0 b6 b5 b4 b3 b2 b1 b0           ← Data byte 0 (lower 7 bits)
  Byte 2: 0 b6 b5 b4 b3 b2 b1 b0           ← Data byte 1 (lower 7 bits)
  ...
  Byte 7: 0 b6 b5 b4 b3 b2 b1 b0           ← Data byte 6 (lower 7 bits)
```

### Python Decode Function
```python
def decode_korg_7bit(encoded_data):
    decoded = bytearray()
    i = 0
    while i + 8 <= len(encoded_data):
        msb_byte = encoded_data[i]
        for j in range(7):
            lower_7 = encoded_data[i + 1 + j] & 0x7F
            msb = (msb_byte >> (6 - j)) & 0x01
            full_byte = (msb << 7) | lower_7
            decoded.append(full_byte)
        i += 8
    return bytes(decoded)
```

### Size Calculations
- Overhead: 7 bytes → 8 bytes = 14.3%
- 254-byte patch → ~291 bytes encoded
- 128 patches (32,512 bytes) → ~37,157 bytes encoded

## MS2000 Patch Structure (254 bytes)

### Memory Map
| Bytes | Parameter | Values | Notes |
|-------|-----------|--------|-------|
| 0-11 | Program Name | ASCII | 12 characters, padded with spaces |
| 12-15 | Reserved | - | Not used |
| 16 | Voice Mode | b6-7: Timbre (0-2)<br>b4-5: Mode (0-3) | 0=Single, 1=Split, 2=Layer, 3=Vocoder |
| 17 | Scale | b4-7: Key (0-11)<br>b0-3: Type (0-9) | Key: C, C#, D, etc.<br>Type: Equal, etc. |
| 18 | Split Point | 0-127 | MIDI note (C-1 to G9) |
| 19 | Delay FX | b7: Sync (0-1)<br>b0-3: Timebase (0-14) | Sync to tempo on/off |
| 20 | Delay Time | 0-127 | Delay time value |
| 21 | Delay Depth | 0-127 | Effect depth |
| 22 | Delay Type | 0-2 | 0=Stereo, 1=Cross, 2=L/R |
| 23 | Mod FX Speed | 0-127 | LFO speed |
| 24 | Mod FX Depth | 0-127 | Effect depth |
| 25 | Mod FX Type | 0-2 | 0=Cho/Flg, 1=Ensemble, 2=Phaser |
| 26-29 | EQ | Hi/Lo Freq & Gain | 2-band EQ |
| 30-31 | Arp Tempo | 16-bit MSB/LSB | 20-300 BPM |
| 32 | Arp Flags | b7: On/Off<br>b6: Latch<br>b4-5: Target<br>b0: Key Sync | Multiple packed flags |
| 33 | Arp Settings | b0-3: Type (0-5)<br>b4-7: Range (0-3) | Type: Up, Down, Alt1, Alt2, Random, Trigger<br>Range: 1-4 octaves |
| 34+ | Oscillators, Filters, Envelopes, LFOs | ... | See MIDI implementation doc |

### Voice Modes
| Value | Mode | Description |
|-------|------|-------------|
| 0 | Single | One timbre across keyboard |
| 1 | Split | Two timbres, split at split point |
| 2 | Layer | Two timbres layered |
| 3 | Vocoder | Vocoder mode |

### Delay Types
| Value | Type | Description |
|-------|------|-------------|
| 0 | Stereo Delay | Standard stereo delay |
| 1 | Cross Delay | L→R, R→L crossfeed |
| 2 | L/R Delay | Independent L/R times |

### Mod FX Types
| Value | Type | Description |
|-------|------|-------------|
| 0 | Cho/Flg | Chorus/Flanger |
| 1 | Ensemble | Ensemble chorus |
| 2 | Phaser | Phaser effect |

### Arpeggiator Types
| Value | Type | Description |
|-------|------|-------------|
| 0 | Up | Ascending notes |
| 1 | Down | Descending notes |
| 2 | Alt1 | Up/down alternating |
| 3 | Alt2 | Up/down alternating (variant) |
| 4 | Random | Random note order |
| 5 | Trigger | Retrigger sequence |

## Hexadecimal Quick Reference

### Decimal ↔ Hex
| Dec | Hex | Binary | Dec | Hex | Binary |
|-----|-----|--------|-----|-----|--------|
| 0 | 00 | 0000 0000 | 8 | 08 | 0000 1000 |
| 1 | 01 | 0000 0001 | 9 | 09 | 0000 1001 |
| 2 | 02 | 0000 0010 | 10 | 0A | 0000 1010 |
| 3 | 03 | 0000 0011 | 11 | 0B | 0000 1011 |
| 4 | 04 | 0000 0100 | 12 | 0C | 0000 1100 |
| 5 | 05 | 0000 0101 | 13 | 0D | 0000 1101 |
| 6 | 06 | 0000 0110 | 14 | 0E | 0000 1110 |
| 7 | 07 | 0000 0111 | 15 | 0F | 0000 1111 |

| Dec | Hex | Dec | Hex | Dec | Hex | Dec | Hex |
|-----|-----|-----|-----|-----|-----|-----|-----|
| 16 | 10 | 64 | 40 | 112 | 70 | 160 | A0 |
| 32 | 20 | 80 | 50 | 128 | 80 | 192 | C0 |
| 48 | 30 | 96 | 60 | 144 | 90 | 224 | E0 |

### Bit Manipulation
```python
# Extract bit n (0-7) from byte
bit_n = (byte >> n) & 0x01

# Set bit n to 1
byte |= (1 << n)

# Clear bit n to 0
byte &= ~(1 << n)

# Extract bits n-m (e.g., bits 4-7)
bits = (byte >> n) & ((1 << (m - n + 1)) - 1)

# Set bits 0-6 (lower 7 bits)
lower_7 = byte & 0x7F

# Set bit 7 (MSB)
byte |= 0x80
```

## Common Tasks

### Send Program Change
```
0xC0 + channel, program_number
Example: 0xC0 0x05 = Program 6 on channel 1
```

### Send Control Change
```
0xB0 + channel, controller, value
Example: 0xB0 0x01 0x40 = Mod wheel to 64 on channel 1
```

### Send NRPN
```
1. 0xB0 0x63 <nrpn_msb>  # Select parameter MSB
2. 0xB0 0x62 <nrpn_lsb>  # Select parameter LSB
3. 0xB0 0x06 <value>     # Set value

Example (MS2000 Arp On/Off):
  0xB0 0x63 0x00         # NRPN MSB = 0
  0xB0 0x62 0x02         # NRPN LSB = 2
  0xB0 0x06 0x7F         # Value = ON (127)
```

### Request MS2000 Patch Dump
```
F0 42 30 58 1C F7      # Request all 128 programs
F0 42 30 58 10 F7      # Request current edit buffer
```

### Send MS2000 Parameter Change
```
F0 42 30 58 41 <pp> <PP> <vv> <VV> F7

Where:
  pp = Parameter ID LSB
  PP = Parameter ID MSB
  vv = Value LSB
  VV = Value MSB
```

## Debugging Tips

### View MIDI Messages (Python)
```python
import mido

# List ports
print(mido.get_input_names())
print(mido.get_output_names())

# Monitor incoming messages
with mido.open_input('Your MIDI Port') as inport:
    for msg in inport:
        print(msg)
```

### Hex Dump SysEx File (Linux/Mac)
```bash
hexdump -C file.syx | head -20       # View first 20 lines
xxd file.syx | head -20              # Alternative viewer
```

### Search for Patterns
```bash
hexdump -C file.syx | grep "f0 42"   # Find Korg SysEx starts
hexdump -C file.syx | grep "f7"      # Find SysEx ends
```

### Calculate Sizes
```python
# File with N patches of 254 bytes each
raw_size = N * 254
encoded_size = (raw_size // 7) * 8 + (raw_size % 7)
total_with_header = 5 + encoded_size  # F0 42 3g 58 4C = 5 bytes
```

---

*Quick reference for MIDI and SysEx development*
*See LEARNING_SUMMARY.md for detailed explanations*
