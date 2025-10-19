#!/usr/bin/env python3
"""
Fix MS2000 SysEx files by removing zero padding and adding F7 terminator.

This script fixes common issues with MS2000 SysEx files that prevent them
from loading into hardware:
- Removes trailing zero padding
- Adds F7 (End of Exclusive) byte if missing
- Validates the file structure

Usage:
    python3 fix_sysex.py <input.syx> [output.syx]

If output file is not specified, the input file will be overwritten.
A backup with _BACKUP suffix will be created automatically.
"""

import sys
from pathlib import Path


def validate_sysex_header(data):
    """
    Validate MS2000 SysEx header.

    Args:
        data: bytes object

    Returns:
        tuple: (is_valid, error_message)
    """
    if len(data) < 5:
        return False, "File too small (< 5 bytes)"

    if data[0] != 0xF0:
        return False, f"Missing SysEx start byte (F0), found: 0x{data[0]:02X}"

    if data[1] != 0x42:
        return False, f"Not a Korg SysEx (expected 0x42), found: 0x{data[1]:02X}"

    if data[3] != 0x58:
        return False, f"Not an MS2000 SysEx (expected 0x58), found: 0x{data[3]:02X}"

    return True, "Header valid"


def fix_sysex_file(input_file, output_file=None, create_backup=True):
    """
    Fix a SysEx file by removing padding and adding F7 terminator.

    Args:
        input_file: Path to input .syx file
        output_file: Path for output file (None = overwrite input)
        create_backup: Create backup of original file

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
    print(f"{'='*60}")
    print(f"Original size: {len(data):,} bytes")

    # Validate header
    is_valid, message = validate_sysex_header(data)
    if not is_valid:
        print(f"✗ Error: {message}")
        return False

    print(f"✓ {message}")

    # Get function ID
    function_id = data[4]
    function_names = {
        0x40: "CURRENT PROGRAM DATA DUMP",
        0x4C: "PROGRAM DATA DUMP",
        0x51: "GLOBAL DATA DUMP",
        0x50: "ALL DATA DUMP",
    }
    function_name = function_names.get(function_id, f"UNKNOWN (0x{function_id:02X})")
    print(f"  Function: 0x{function_id:02X} - {function_name}")

    # Check current termination
    already_correct = data[-1] == 0xF7

    if already_correct:
        print(f"✓ File already ends with F7 (End of Exclusive)")
        print(f"\nNo changes needed!")
        return False

    # Find end of real data (before zero padding)
    end_pos = len(data)
    for i in range(len(data) - 1, -1, -1):
        if data[i] != 0x00:
            end_pos = i + 1
            break

    # Check if we're removing padding
    padding_removed = len(data) - end_pos
    if padding_removed > 0:
        print(f"  Removing {padding_removed} bytes of zero padding")

    # Create fixed data
    fixed_data = data[:end_pos]
    fixed_data.append(0xF7)

    print(f"\nFixed size: {len(fixed_data):,} bytes")
    print(f"  Last 10 bytes: {' '.join(f'{b:02x}' for b in fixed_data[-10:])}")

    # Estimate number of patches
    encoded_size = len(fixed_data) - 6  # Remove header and F7
    estimated_patches = (encoded_size * 7) // 8 // 254
    print(f"  Estimated patches: {estimated_patches}")

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
    print(f"\n{'='*60}")
    print("SUCCESS! File is now ready to send to MS2000.")
    print(f"{'='*60}")

    return True


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nExamples:")
        print("  python3 fix_sysex.py patches/OriginalPatches.syx")
        print("  python3 fix_sysex.py broken.syx fixed.syx")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        modified = fix_sysex_file(input_file, output_file)
        sys.exit(0 if modified else 1)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
