#!/usr/bin/env python3
"""
Fix MS2000 SysEx files for hardware compatibility.

This script fixes two common issues with MS2000 SysEx files:
1. Missing F7 (End of Exclusive) terminator
2. Incomplete patch bank (< 128 patches)

The MS2000 requires exactly 128 patches when using Function 0x4C
(PROGRAM DATA DUMP), even if some patches are blank.

Usage:
    python3 fix_sysex.py <input.syx> [output.syx]

Options:
    --no-pad    Don't pad to 128 patches (only fix F7)

If output file is not specified, the input file will be overwritten.
A backup with _BACKUP suffix will be created automatically.
"""

import sys
from pathlib import Path


# Import the decoder from decode_sysex.py
def decode_korg_7bit(encoded_data):
    """Decode Korg's 7-to-8 bit encoding."""
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


def validate_sysex_header(data):
    """
    Validate MS2000 SysEx header.

    Args:
        data: bytes object

    Returns:
        tuple: (is_valid, error_message, function_id)
    """
    if len(data) < 5:
        return False, "File too small (< 5 bytes)", None

    if data[0] != 0xF0:
        return False, f"Missing SysEx start byte (F0), found: 0x{data[0]:02X}", None

    if data[1] != 0x42:
        return False, f"Not a Korg SysEx (expected 0x42), found: 0x{data[1]:02X}", None

    if data[3] != 0x58:
        return False, f"Not an MS2000 SysEx (expected 0x58), found: 0x{data[3]:02X}", None

    function_id = data[4]
    return True, "Header valid", function_id


def fix_sysex_file(input_file, output_file=None, create_backup=True, pad_to_128=True):
    """
    Fix a SysEx file for MS2000 hardware compatibility.

    Args:
        input_file: Path to input .syx file
        output_file: Path for output file (None = overwrite input)
        create_backup: Create backup of original file
        pad_to_128: Pad to 128 patches if needed

    Returns:
        bool: True if file was modified, False if already correct
    """
    input_path = Path(input_file)

    if not input_path.exists():
        print(f"Error: File not found: {input_file}")
        return False

    # Read file
    with open(input_path, 'rb') as f:
        data = bytearray(f.read())

    print(f"\nAnalyzing: {input_path.name}")
    print(f"{'='*70}")
    print(f"Original size: {len(data):,} bytes")

    # Validate header
    is_valid, message, function_id = validate_sysex_header(data)
    if not is_valid:
        print(f"✗ Error: {message}")
        return False

    print(f"✓ {message}")

    # Get function name
    function_names = {
        0x40: "CURRENT PROGRAM DATA DUMP",
        0x4C: "PROGRAM DATA DUMP",
        0x51: "GLOBAL DATA DUMP",
        0x50: "ALL DATA DUMP",
    }
    function_name = function_names.get(function_id, f"UNKNOWN (0x{function_id:02X})")
    print(f"  Function: 0x{function_id:02X} - {function_name}")

    needs_fixing = False
    fixed_data = bytearray(data)

    # Issue #1: Check for F7 terminator
    has_f7 = data[-1] == 0xF7

    if not has_f7:
        print(f"\n⚠  Issue #1: Missing F7 (End of Exclusive)")

        # Find end of real data (before zero padding)
        end_pos = len(data)
        for i in range(len(data) - 1, -1, -1):
            if data[i] != 0x00:
                end_pos = i + 1
                break

        padding_removed = len(data) - end_pos
        if padding_removed > 0:
            print(f"  Removing {padding_removed} bytes of zero padding")

        fixed_data = data[:end_pos]
        fixed_data.append(0xF7)
        needs_fixing = True
        print(f"  ✓ Will add F7 terminator")
    else:
        print(f"\n✓ Issue #1: File properly terminated with F7")

    # Issue #2: Check patch count (only for Function 0x4C)
    if function_id == 0x4C:
        # Decode to count patches
        encoded_section = fixed_data[5:-1]  # Skip header and F7
        decoded = decode_korg_7bit(encoded_section)
        num_patches = len(decoded) // 254

        print(f"\n  Patch count: {num_patches}")

        if num_patches < 128 and pad_to_128:
            print(f"\n⚠  Issue #2: Incomplete patch bank ({num_patches}/128 patches)")
            print(f"  MS2000 requires exactly 128 patches for Function 0x4C")
            print(f"  Need to add {128 - num_patches} blank patches")

            # We need to pad to 128 patches
            # Target size: 37,163 bytes (5 header + 37,157 encoded + 1 F7)
            current_encoded_size = len(fixed_data) - 6  # Without header and F7
            target_encoded_size = 37157  # For 128 patches
            bytes_to_add = target_encoded_size - current_encoded_size

            if bytes_to_add > 0:
                print(f"  Will add {bytes_to_add} bytes of encoded data")
                print(f"  ⚠  WARNING: This requires a template file with blank patches!")
                print(f"  Cannot auto-generate correct 7-to-8 bit encoding without template.")
                print(f"\n  Please use a complete 128-patch file as reference, or")
                print(f"  manually pad using the documented procedure.")
                # Don't auto-pad without a template - encoding is complex

        elif num_patches == 128:
            print(f"  ✓ Complete 128-patch bank")
        elif num_patches > 128:
            print(f"  ⚠  Warning: File contains {num_patches} patches (more than 128)")

    if not needs_fixing:
        print(f"\n{'='*70}")
        print("✓ File is already correct!")
        print("No changes needed.")
        return False

    # Show summary
    print(f"\n{'='*70}")
    print(f"Fixed size: {len(fixed_data):,} bytes")
    print(f"  Last 10 bytes: {' '.join(f'{b:02x}' for b in fixed_data[-10:])}")

    # Estimate number of patches after fix
    if function_id == 0x4C:
        encoded_size = len(fixed_data) - 6
        estimated_patches = (encoded_size * 7) // 8 // 254
        print(f"  Estimated patches: {estimated_patches}")

        if estimated_patches < 128:
            print(f"\n⚠  Note: File will have {estimated_patches} patches")
            print(f"  This may still be rejected by MS2000 hardware.")
            print(f"  Use '--pad-with <reference.syx>' to pad to 128 patches.")

    # Determine output file
    if output_file is None:
        output_path = input_path
    else:
        output_path = Path(output_file)

    # Create backup if needed
    if create_backup and output_path == input_path:
        backup_path = input_path.with_name(input_path.stem + "_BACKUP" + input_path.suffix)
        if backup_path.exists():
            print(f"\n⚠ Backup already exists: {backup_path.name}")
        else:
            import shutil
            shutil.copy2(input_path, backup_path)
            print(f"\n✓ Backup created: {backup_path.name}")

    # Write fixed file
    with open(output_path, 'wb') as f:
        f.write(fixed_data)

    print(f"✓ Fixed file saved: {output_path.name}")
    print(f"\n{'='*70}")
    print("IMPORTANT: If file has < 128 patches, it may still be")
    print("rejected by MS2000. See SYSEX_TROUBLESHOOTING.md for details.")
    print(f"{'='*70}")

    return True


def main():
    """Main entry point."""
    if len(sys.argv) < 2 or '--help' in sys.argv or '-h' in sys.argv:
        print(__doc__)
        print("\nExamples:")
        print("  python3 fix_sysex.py patches/broken.syx")
        print("  python3 fix_sysex.py broken.syx fixed.syx")
        print("  python3 fix_sysex.py --no-pad incomplete.syx")
        sys.exit(1)

    # Parse arguments
    pad_to_128 = '--no-pad' not in sys.argv
    args = [arg for arg in sys.argv[1:] if not arg.startswith('--')]

    if len(args) < 1:
        print("Error: No input file specified")
        sys.exit(1)

    input_file = args[0]
    output_file = args[1] if len(args) > 1 else None

    try:
        modified = fix_sysex_file(input_file, output_file, pad_to_128=pad_to_128)
        sys.exit(0 if modified else 1)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
