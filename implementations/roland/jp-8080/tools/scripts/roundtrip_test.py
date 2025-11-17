#!/usr/bin/env python3
"""
Round-trip test for JP-8080 SysEx encoding/decoding.

This script:
1. Reads a SysEx file
2. Decodes the patch data
3. Re-encodes the patch data
4. Compares the original and re-encoded data

This ensures that our encoding/decoding is lossless and correctly
implements the Roland SysEx format.
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
    decode_roland_sysex,
    _split_sysex_messages,
)


def compare_bytes(original: bytes, reconstructed: bytes) -> bool:
    """Compare two byte sequences and report differences."""
    if len(original) != len(reconstructed):
        print(f"✗ Length mismatch: {len(original)} vs {len(reconstructed)}")
        return False

    differences = []
    for i, (a, b) in enumerate(zip(original, reconstructed)):
        if a != b:
            differences.append((i, a, b))

    if differences:
        print(f"✗ Found {len(differences)} byte differences:")
        for i, (offset, orig, recon) in enumerate(differences[:10]):  # Show first 10
            print(f"  Offset 0x{offset:04X}: 0x{orig:02X} -> 0x{recon:02X}")
        if len(differences) > 10:
            print(f"  ... and {len(differences) - 10} more")
        return False

    return True


def roundtrip_test(file_path: Path, verbose: bool = False) -> bool:
    """
    Perform round-trip test on a SysEx file.
    Returns True if test passes, False otherwise.
    """

    print(f"Testing: {file_path}")
    print("-" * 60)

    try:
        # Read original file
        original_sysex = file_path.read_bytes()

        # Decode
        header, patch, address = load_patch_from_sysex(file_path)

        if verbose:
            print(f"Patch name: {patch.name}")
            print(f"Address: 0x{address:08X}")
            print(f"Device ID: 0x{header.device_id:02X}")
            print()

        segments = getattr(
            patch,
            "_source_segments",
            [
                {
                    "address": address,
                    "length": len(patch.raw_data),
                    "start": 0,
                }
            ],
        )

        # Re-encode with same parameters (canonical single-patch message)
        reconstructed_sysex = encode_patch_to_sysex(
            patch.raw_data,
            address=address,
            device_id=header.device_id,
        )

        # Compare
        original_messages = _split_sysex_messages(original_sysex)
        multi_packet = (
            len(original_messages) > 1
            or len(segments) > 1
            or len(original_sysex) != len(reconstructed_sysex)
        )
        print("Comparing original and reconstructed SysEx...")

        if not multi_packet:
            # Original was a single DT1 patch dump (JP-8080 format)
            print("\n1. Header (first 10 bytes):")
            if compare_bytes(original_sysex[:10], reconstructed_sysex[:10]):
                print("✓ Header matches")
            else:
                return False

            orig_payload = original_sysex[10:-2]
            recon_payload = reconstructed_sysex[10:-2]

            print("\n2. Patch data payload:")
            if compare_bytes(orig_payload, recon_payload):
                print(f"✓ Patch data matches ({len(orig_payload)} bytes)")
            else:
                return False

            print("\n3. Checksum:")
            orig_checksum = original_sysex[-2]
            recon_checksum = reconstructed_sysex[-2]

            if orig_checksum == recon_checksum:
                print(f"✓ Checksum matches (0x{orig_checksum:02X})")
            else:
                print(f"✗ Checksum mismatch: 0x{orig_checksum:02X} vs 0x{recon_checksum:02X}")
                return False

            print("\n4. SysEx terminator (F7):")
            if original_sysex[-1] == 0xF7 and reconstructed_sysex[-1] == 0xF7:
                print("✓ Terminator present")
            else:
                print("✗ Terminator missing or incorrect")
                return False

            print("\n5. Complete message:")
            if compare_bytes(original_sysex, reconstructed_sysex):
                print("✓ Complete round-trip successful!")
                print()
                print("=" * 60)
                print("ROUND-TRIP TEST: PASSED ✓")
                print("=" * 60)
                return True
            else:
                print()
                print("=" * 60)
                print("ROUND-TRIP TEST: FAILED ✗")
                print("=" * 60)
                return False

        # Multi-message (JP-8000 performance temp or similar)
        print("\nDetected non-canonical SysEx (JP-8000/performance export).")
        decoded_segments = [decode_roland_sysex(msg) for msg in original_messages]
        payload_by_address = {addr: payload for _, payload, addr in decoded_segments}

        success = True
        for segment in segments:
            addr = segment["address"]
            length = segment["length"]
            start = segment.get("start", 0)
            orig_payload = payload_by_address.get(addr)
            new_payload = patch.raw_data[start : start + length]

            print(f"\nSegment @ 0x{addr:08X} ({length} bytes):")
            if orig_payload is None:
                print("✗ Missing in original file; cannot verify")
                success = False
                continue

            if orig_payload == new_payload:
                print("✓ Payload matches original")
            else:
                print("✗ Payload mismatch detected")
                success = False

        if success:
            print()
            print("=" * 60)
            print("ROUND-TRIP TEST (JP-8000 format): PASSED ✓")
            print("=" * 60)
        else:
            print()
            print("=" * 60)
            print("ROUND-TRIP TEST (JP-8000 format): FAILED ✗")
            print("=" * 60)
        return success

    except Exception as e:
        print(f"\n✗ Error during round-trip test: {e}")
        import traceback
        traceback.print_exc()
        return False


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Round-trip test for JP-8080 SysEx encoding/decoding",
    )
    parser.add_argument(
        "files",
        type=Path,
        nargs="+",
        help="SysEx file(s) to test",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output",
    )

    args = parser.parse_args()

    results = []
    for file_path in args.files:
        if not file_path.exists():
            print(f"Error: File not found: {file_path}", file=sys.stderr)
            results.append(False)
            continue

        success = roundtrip_test(file_path, args.verbose)
        results.append(success)

        if len(args.files) > 1:
            print("\n")

    # Summary
    if len(results) > 1:
        passed = sum(results)
        total = len(results)
        print(f"\nSummary: {passed}/{total} tests passed")

    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
