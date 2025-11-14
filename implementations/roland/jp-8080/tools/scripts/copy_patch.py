#!/usr/bin/env python3
"""
Copy a patch from one SysEx file to another, optionally changing its address.

This tool reads a JP-8080 patch SysEx file and writes it to a new location,
optionally modifying the target address (useful for copying to different patch slots).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Add parent directories to path for imports
tools_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(tools_dir))
sys.path.insert(0, str(tools_dir / "lib"))

from jp8080_core import (  # type: ignore
    load_patch_from_sysex,
    encode_patch_to_sysex,
    PATCH_SIZE,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Copy a JP-8080 patch to a new SysEx file, optionally changing address",
    )
    parser.add_argument("input_file", type=Path, help="Source SysEx file")
    parser.add_argument(
        "-o", "--output",
        type=Path,
        required=True,
        help="Output SysEx file",
    )
    parser.add_argument(
        "--address",
        type=str,
        help="New address in hex (e.g., 0x02000000 for User Patch A11)",
    )
    parser.add_argument(
        "--device-id",
        type=lambda x: int(x, 0),
        default=0x10,
        help="Device ID (default: 0x10)",
    )

    args = parser.parse_args()

    try:
        # Load source patch
        header, patch, orig_address = load_patch_from_sysex(args.input_file)

        # Determine target address
        if args.address:
            target_address = int(args.address, 0)
        else:
            target_address = orig_address

        # Encode to new SysEx
        new_sysex = encode_patch_to_sysex(
            patch.raw_data,
            address=target_address,
            device_id=args.device_id,
        )

        # Write output
        args.output.write_bytes(new_sysex)

        print(f"Copied patch: {patch.name}")
        print(f"  From: {args.input_file}")
        print(f"  To:   {args.output}")
        print(f"  Original address: 0x{orig_address:08X}")
        print(f"  New address:      0x{target_address:08X}")

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
