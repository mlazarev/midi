#!/usr/bin/env python3
"""
Korg MS2000 SysEx Decoder

This script decodes Korg MS2000 PROGRAM DATA DUMP SysEx files.
It implements the 7-to-8 bit encoding scheme used in Korg MIDI SysEx messages.

Based on MS2000 MIDI Implementation documentation.
"""

def decode_korg_7bit(encoded_data):
    """
    Decode Korg's 7-to-8 bit encoding scheme.

    Every 8 bytes of encoded data contains:
    - 1 byte with the MSBs (bit 7) of the next 7 bytes
    - 7 bytes of 7-bit data

    This expands 7 bytes of 8-bit data into 8 bytes of 7-bit MIDI data.

    Args:
        encoded_data: bytes object containing encoded data

    Returns:
        bytes object containing decoded 8-bit data
    """
    decoded = bytearray()
    i = 0

    while i < len(encoded_data):
        if i + 8 > len(encoded_data):
            # Not enough bytes for a full group
            decoded.extend(encoded_data[i:])
            break

        # First byte contains MSBs of the next 7 bytes
        msb_byte = encoded_data[i]

        # Process the next 7 bytes
        for j in range(7):
            if i + 1 + j < len(encoded_data):
                # Get the 7-bit data byte
                data_byte = encoded_data[i + 1 + j]
                # Extract the corresponding MSB from msb_byte (bit 6 down to 0)
                msb = (msb_byte >> (6 - j)) & 0x01
                # Combine MSB with the 7-bit data to get full 8-bit byte
                full_byte = (msb << 7) | (data_byte & 0x7F)
                decoded.append(full_byte)

        i += 8

    return bytes(decoded)


class MS2000Patch:
    """Represents a single MS2000 program/patch."""

    # Constants from MIDI Implementation doc
    VOICE_MODES = ['Single', 'Split', 'Layer', 'Vocoder']
    SCALE_KEYS = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    DELAY_TYPES = ['StereoDelay', 'CrossDelay', 'L/R Delay']
    MOD_TYPES = ['Cho/Flg', 'Ensemble', 'Phaser']
    ARP_TYPES = ['Up', 'Down', 'Alt1', 'Alt2', 'Random', 'Trigger']

    def __init__(self, data):
        """
        Initialize patch from 254 bytes of decoded program data.

        Args:
            data: bytes object containing 254 bytes of patch data
        """
        if len(data) < 254:
            raise ValueError(f"Patch data must be at least 254 bytes, got {len(data)}")

        self.raw_data = data
        self.parse_parameters()

    def parse_parameters(self):
        """Parse patch parameters according to TABLE 1 in MIDI Implementation."""
        d = self.raw_data

        # Bytes 0-11: Program name (ASCII)
        self.name = d[0:12].decode('ascii', errors='replace').rstrip()

        # Byte 16: Voice Mode and Timbre
        self.timbre_voice = (d[16] >> 6) & 0x03
        self.voice_mode = self.VOICE_MODES[(d[16] >> 4) & 0x03]

        # Byte 17: Scale
        scale_key_idx = (d[17] >> 4) & 0x0F
        self.scale_key = self.SCALE_KEYS[scale_key_idx] if scale_key_idx < 12 else str(scale_key_idx)
        self.scale_type = d[17] & 0x0F

        # Byte 18: Split Point
        self.split_point = d[18]

        # Bytes 19-22: DELAY FX
        self.delay_sync = bool((d[19] >> 7) & 0x01)
        self.delay_timebase = d[19] & 0x0F
        self.delay_time = d[20]
        self.delay_depth = d[21]
        delay_type_idx = d[22]
        self.delay_type = self.DELAY_TYPES[delay_type_idx] if delay_type_idx < 3 else str(delay_type_idx)

        # Bytes 23-25: MOD FX
        self.mod_speed = d[23]
        self.mod_depth = d[24]
        mod_type_idx = d[25]
        self.mod_type = self.MOD_TYPES[mod_type_idx] if mod_type_idx < 3 else str(mod_type_idx)

        # Bytes 26-29: EQ
        self.eq_hi_freq = d[26]
        self.eq_hi_gain = d[27]
        self.eq_low_freq = d[28]
        self.eq_low_gain = d[29]

        # Bytes 30-33: ARPEGGIO
        self.arp_tempo = (d[30] << 8) | d[31]
        self.arp_on = bool((d[32] >> 7) & 0x01)
        self.arp_latch = bool((d[32] >> 6) & 0x01)
        self.arp_target = (d[32] >> 4) & 0x03
        self.arp_keysync = bool(d[32] & 0x01)

        arp_type_idx = d[33] & 0x0F
        self.arp_type = self.ARP_TYPES[arp_type_idx] if arp_type_idx < 6 else str(arp_type_idx)
        self.arp_range = ((d[33] >> 4) & 0x0F) + 1

    def __str__(self):
        """Return a formatted string representation of the patch."""
        lines = [
            f"Patch: {self.name}",
            f"  Voice Mode: {self.voice_mode}",
            f"  Scale: {self.scale_key} (Type {self.scale_type})",
            f"  Delay: {self.delay_type}, Time={self.delay_time}, Depth={self.delay_depth}",
            f"  Mod: {self.mod_type}, Speed={self.mod_speed}, Depth={self.mod_depth}",
            f"  Arpeggio: {'ON' if self.arp_on else 'OFF'}, Type={self.arp_type}, "
            f"Range={self.arp_range}oct, Tempo={self.arp_tempo}"
        ]
        return '\n'.join(lines)


def parse_sysex_file(filename):
    """
    Parse a Korg MS2000 PROGRAM DATA DUMP SysEx file.

    Args:
        filename: path to .syx file

    Returns:
        list of MS2000Patch objects (should be 128 patches)
    """
    with open(filename, 'rb') as f:
        data = f.read()

    # Verify header
    if len(data) < 5:
        raise ValueError("File too small to be a valid SysEx file")

    if data[0] != 0xF0:
        raise ValueError("Not a SysEx file (missing F0 start byte)")

    if data[1] != 0x42:
        raise ValueError("Not a Korg SysEx file (manufacturer ID != 0x42)")

    # Byte 2: MIDI channel (3g format, where g = channel)
    midi_channel = data[2] & 0x0F

    if data[3] != 0x58:
        raise ValueError("Not an MS2000 SysEx file (device ID != 0x58)")

    function_id = data[4]

    # Function ID meanings:
    # 0x40 = CURRENT PROGRAM DATA DUMP
    # 0x4C = PROGRAM DATA DUMP
    # 0x51 = GLOBAL DATA DUMP
    # 0x50 = ALL DATA DUMP

    print(f"SysEx Header:")
    print(f"  Manufacturer: Korg (0x42)")
    print(f"  MIDI Channel: {midi_channel}")
    print(f"  Device: MS2000 (0x58)")
    print(f"  Function: 0x{function_id:02X}", end='')

    if function_id == 0x40:
        print(" (CURRENT PROGRAM DATA DUMP)")
    elif function_id == 0x4C:
        print(" (PROGRAM DATA DUMP)")
    elif function_id == 0x51:
        print(" (GLOBAL DATA DUMP)")
    elif function_id == 0x50:
        print(" (ALL DATA DUMP)")
    else:
        print(" (UNKNOWN)")

    # Skip 5-byte header and decode the ENTIRE data stream
    # The 7-to-8 bit encoding applies to the entire block, not individual patches
    encoded_stream = data[5:]
    decoded_stream = decode_korg_7bit(encoded_stream)

    print(f"  Encoded size: {len(encoded_stream)} bytes")
    print(f"  Decoded size: {len(decoded_stream)} bytes")

    # Each patch is exactly 254 bytes in the decoded stream
    PATCH_SIZE = 254
    num_patches = len(decoded_stream) // PATCH_SIZE

    patches = []
    for i in range(num_patches):
        offset = i * PATCH_SIZE
        patch_data = decoded_stream[offset:offset + PATCH_SIZE]

        try:
            patch = MS2000Patch(patch_data)
            patches.append(patch)
        except Exception as e:
            print(f"Warning: Failed to parse patch {i + 1}: {e}")
            break

    print(f"  Patches decoded: {len(patches)}\n")

    return patches


def main():
    """Main function to decode and display SysEx files."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python decode_sysex.py <sysex_file.syx>")
        print("\nExample:")
        print("  python decode_sysex.py OriginalPatches.syx")
        sys.exit(1)

    filename = sys.argv[1]

    print(f"Decoding: {filename}")
    print("=" * 60)

    try:
        patches = parse_sysex_file(filename)

        print(f"\nSuccessfully decoded {len(patches)} patches\n")
        print("=" * 60)

        # Display all patches
        for i, patch in enumerate(patches, 1):
            bank = chr(ord('A') + (i - 1) // 16)
            num = ((i - 1) % 16) + 1
            print(f"\n[{bank}{num:02d}] {patch.name}")
            print(f"     Mode: {patch.voice_mode:8s}  "
                  f"Delay: {patch.delay_type:12s}  "
                  f"Mod: {patch.mod_type:10s}  "
                  f"Arp: {patch.arp_type if patch.arp_on else 'OFF'}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
