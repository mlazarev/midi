#!/usr/bin/env python3
"""
Compare two MS2000 SysEx patch banks and show differences.
"""

import sys
from decode_sysex import parse_sysex_file, MS2000Patch


def compare_patches(patch1, patch2, patch_num):
    """
    Compare two patches and return list of differences.

    Args:
        patch1: MS2000Patch object
        patch2: MS2000Patch object
        patch_num: Patch number for display

    Returns:
        List of difference strings
    """
    diffs = []

    # Compare names
    if patch1.name != patch2.name:
        diffs.append(f"  Name: '{patch1.name}' vs '{patch2.name}'")

    # Compare voice mode
    if patch1.voice_mode != patch2.voice_mode:
        diffs.append(f"  Voice Mode: {patch1.voice_mode} vs {patch2.voice_mode}")

    # Compare delay
    if patch1.delay_type != patch2.delay_type:
        diffs.append(f"  Delay Type: {patch1.delay_type} vs {patch2.delay_type}")
    if patch1.delay_time != patch2.delay_time:
        diffs.append(f"  Delay Time: {patch1.delay_time} vs {patch2.delay_time}")

    # Compare mod
    if patch1.mod_type != patch2.mod_type:
        diffs.append(f"  Mod Type: {patch1.mod_type} vs {patch2.mod_type}")
    if patch1.mod_speed != patch2.mod_speed:
        diffs.append(f"  Mod Speed: {patch1.mod_speed} vs {patch2.mod_speed}")

    # Compare arpeggio
    if patch1.arp_on != patch2.arp_on:
        diffs.append(f"  Arp On/Off: {patch1.arp_on} vs {patch2.arp_on}")
    if patch1.arp_type != patch2.arp_type:
        diffs.append(f"  Arp Type: {patch1.arp_type} vs {patch2.arp_type}")

    # Compare raw data for comprehensive check
    if patch1.raw_data != patch2.raw_data:
        # Count differing bytes
        diff_bytes = sum(1 for a, b in zip(patch1.raw_data, patch2.raw_data) if a != b)
        if diff_bytes > 0 and not diffs:
            # There are differences in raw data not captured by our parsing
            diffs.append(f"  Raw data differs ({diff_bytes} bytes)")

    return diffs


def main():
    if len(sys.argv) != 3:
        print("Usage: python compare_patches.py <file1.syx> <file2.syx>")
        print("\nExample:")
        print("  python compare_patches.py file1.syx file2.syx")
        sys.exit(1)

    file1, file2 = sys.argv[1], sys.argv[2]

    print(f"Comparing:")
    print(f"  File 1: {file1}")
    print(f"  File 2: {file2}")
    print("=" * 70)
    print()

    # Parse both files
    try:
        patches1 = parse_sysex_file(file1)
        print()
        patches2 = parse_sysex_file(file2)
        print()
    except Exception as e:
        print(f"Error parsing files: {e}")
        sys.exit(1)

    # Compare counts
    print(f"Patch counts: {len(patches1)} vs {len(patches2)}")

    if len(patches1) != len(patches2):
        print(f"WARNING: Different number of patches!")
        print(f"  Will compare first {min(len(patches1), len(patches2))} patches")

    print()
    print("=" * 70)
    print("DIFFERENCES:")
    print("=" * 70)

    # Compare each patch
    diff_count = 0
    identical_count = 0

    for i in range(min(len(patches1), len(patches2))):
        p1, p2 = patches1[i], patches2[i]
        bank = chr(ord('A') + i // 16)
        num = (i % 16) + 1

        diffs = compare_patches(p1, p2, i + 1)

        if diffs:
            diff_count += 1
            print(f"\n[{bank}{num:02d}] Patch {i+1}")
            for diff in diffs:
                print(diff)
        else:
            identical_count += 1

    print()
    print("=" * 70)
    print("SUMMARY:")
    print("=" * 70)
    print(f"Identical patches: {identical_count}")
    print(f"Different patches: {diff_count}")

    if len(patches1) != len(patches2):
        extra = abs(len(patches1) - len(patches2))
        which = "File 1" if len(patches1) > len(patches2) else "File 2"
        print(f"Extra patches in {which}: {extra}")


if __name__ == '__main__':
    main()
