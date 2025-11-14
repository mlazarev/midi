#!/usr/bin/env python3
"""
Extract individual patches from a JP-8080 bulk dump.

JP-8080 bulk dumps store each 248-byte patch as TWO SysEx messages:
1. Main patch data (242 bytes) at offset 0x00
2. Extended parameters (6 bytes) at offset 0xF2 (242 decimal)

This tool reassembles complete patches and can extract them individually
or export all patches to JSON.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Add parent directories to path for imports
tools_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(tools_dir))
sys.path.insert(0, str(tools_dir / "lib"))

from jp8080_core import (  # type: ignore
    JP8080Patch,
    extract_full_parameters,
    encode_patch_to_sysex,
    PATCH_SIZE,
)


def parse_bulk_dump(file_path: Path) -> list[bytes]:
    """
    Parse a bulk dump file and return list of reassembled patches.

    Each patch is stored as two messages:
    - Message 1: 242 bytes at offset 0
    - Message 2: 6 bytes at offset 242
    """
    data = file_path.read_bytes()

    # Find all SysEx message boundaries
    messages = []
    pos = 0
    while pos < len(data):
        if data[pos] == 0xF0:
            f7_pos = data.find(0xF7, pos)
            if f7_pos == -1:
                break
            messages.append(data[pos:f7_pos+1])
            pos = f7_pos + 1
        else:
            pos += 1

    print(f"Found {len(messages)} SysEx messages in bulk dump")

    # Group messages by patch
    patches = []
    i = 0

    while i < len(messages):
        msg = messages[i]

        # Check if this is a patch message (address starts with 0x02)
        if len(msg) >= 10 and msg[6] == 0x02:
            # Check message length
            if len(msg) == 254:  # 242 data + 12 overhead
                # This is the main patch data
                main_data = msg[10:-2]  # Extract payload (242 bytes)

                # Look for the extended parameters message
                extended_data = b'\x00' * 6  # Default to zeros

                if i + 1 < len(messages):
                    next_msg = messages[i + 1]
                    # Check if next message is at offset 242 (address byte 3 = 0x01, byte 4 = 0x72)
                    if (len(next_msg) >= 10 and
                        next_msg[6:8] == msg[6:8] and  # Same patch base address
                        next_msg[8] == 0x01 and next_msg[9] == 0x72):
                        extended_data = next_msg[10:-2]  # Extract 6 bytes
                        i += 1  # Skip the extended message

                # Reassemble complete 248-byte patch
                complete_patch = main_data + extended_data
                if len(complete_patch) == PATCH_SIZE:
                    patches.append(complete_patch)
                else:
                    print(f"Warning: Patch size mismatch: {len(complete_patch)} bytes")

        i += 1

    return patches


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extract patches from JP-8080 bulk dump",
    )
    parser.add_argument("input_file", type=Path, help="Bulk dump SysEx file")
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all patches in the dump",
    )
    parser.add_argument(
        "--extract",
        type=int,
        metavar="N",
        help="Extract patch number N (1-based)",
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Output file for extracted patch",
    )
    parser.add_argument(
        "--export-json",
        type=Path,
        help="Export all patches to JSON file",
    )

    args = parser.parse_args()

    try:
        # Parse the bulk dump
        patches = parse_bulk_dump(args.input_file)
        print(f"Successfully parsed {len(patches)} complete patches")
        print()

        # List patches
        if args.list or not any([args.extract, args.export_json]):
            print("Patches in dump:")
            print("-" * 60)
            for i, patch_data in enumerate(patches, 1):
                patch = JP8080Patch(patch_data)
                print(f"{i:3d}. {patch.name:20s} | {patch.osc1_waveform:12s} | {patch.filter_type}")
            return 0

        # Extract single patch
        if args.extract is not None:
            if not 1 <= args.extract <= len(patches):
                print(f"Error: Patch {args.extract} out of range (1-{len(patches)})", file=sys.stderr)
                return 1

            patch_data = patches[args.extract - 1]
            patch = JP8080Patch(patch_data)

            # Calculate address for this patch (User Patch area starts at 0x02000000)
            address = 0x02000000 + (args.extract - 1) * 0x200

            # Encode to SysEx
            sysex = encode_patch_to_sysex(patch_data, address)

            # Determine output file
            if args.output:
                output_file = args.output
            else:
                safe_name = "".join(c if c.isalnum() else "_" for c in patch.name).lower()
                output_file = Path(f"{safe_name}_patch_{args.extract}.syx")

            output_file.write_bytes(sysex)
            print(f"Extracted patch #{args.extract}: {patch.name}")
            print(f"Saved to: {output_file}")
            return 0

        # Export all to JSON
        if args.export_json:
            all_patches = []
            for i, patch_data in enumerate(patches, 1):
                patch = JP8080Patch(patch_data)
                params = extract_full_parameters(patch)
                params["index"] = i
                all_patches.append(params)

            with open(args.export_json, 'w') as f:
                json.dump(all_patches, f, indent=2)

            print(f"Exported {len(all_patches)} patches to: {args.export_json}")
            return 0

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
