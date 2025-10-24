#!/usr/bin/env python3
"""
Copy a patch within a Korg MS2000 PROGRAM DATA DUMP (.syx) bank.

Usage:
  python copy_patch.py <input.syx> <src_patch> <dst_patch> [-o output.syx]

Notes:
  - Patches are 1-based (1..128). A01 = 1, A16 = 16, B01 = 17, etc.
  - Creates a new .syx preserving the original header and proper F7 terminator.
  - No external dependencies; uses MS2000 7-bit encoding inline.
"""

from __future__ import annotations

import sys
from pathlib import Path


def decode_korg_7bit(encoded_data: bytes) -> bytes:
    decoded = bytearray()
    i = 0
    while i < len(encoded_data):
        if i + 8 > len(encoded_data):
            # leftover - decode what’s possible (not expected here for full banks)
            break
        msb = encoded_data[i]
        for j in range(7):
            b = encoded_data[i + 1 + j]
            full = ((msb >> (6 - j)) & 1) << 7 | (b & 0x7F)
            decoded.append(full)
        i += 8
    return bytes(decoded)


def encode_korg_7bit(decoded_data: bytes) -> bytes:
    encoded = bytearray()
    i = 0
    while i < len(decoded_data):
        chunk = decoded_data[i:i+7]
        if not chunk:
            break
        msb_byte = 0
        for j, b in enumerate(chunk):
            if b & 0x80:
                msb_byte |= 1 << (6 - j)
        encoded.append(msb_byte)
        for b in chunk:
            encoded.append(b & 0x7F)
        i += 7
    return bytes(encoded)


def copy_patch(input_path: Path, src_idx: int, dst_idx: int, output_path: Path | None) -> Path:
    data = input_path.read_bytes()
    if len(data) < 6 or data[0] != 0xF0 or data[1] != 0x42 or data[3] != 0x58 or data[4] != 0x4C:
        raise ValueError("Not an MS2000 PROGRAM DATA DUMP file (F0 42 30 58 4C ... F7)")

    header = data[:5]
    if data[-1] != 0xF7:
        # Trim trailing zeros and add F7
        end = next((i for i in range(len(data)-1, -1, -1) if data[i] != 0x00), 4) + 1
        data = data[:end] + b"\xF7"

    encoded = data[5:-1]
    decoded = bytearray(decode_korg_7bit(encoded))

    PATCH_SIZE = 254
    total_patches = len(decoded) // PATCH_SIZE
    if total_patches < 128:
        # pad decoded to full 128 patches of zeros if needed
        decoded.extend(b"\x00" * (PATCH_SIZE * 128 - len(decoded)))
        total_patches = 128

    if not (1 <= src_idx <= total_patches and 1 <= dst_idx <= total_patches):
        raise ValueError(f"src/dst out of range: have {total_patches} patches")

    s_off = (src_idx - 1) * PATCH_SIZE
    d_off = (dst_idx - 1) * PATCH_SIZE
    decoded[d_off:d_off+PATCH_SIZE] = decoded[s_off:s_off+PATCH_SIZE]

    new_encoded = encode_korg_7bit(bytes(decoded[:PATCH_SIZE*total_patches]))
    out = header + new_encoded + bytes([0xF7])

    if output_path is None:
        output_path = input_path.with_name(input_path.stem + f"_copy_{src_idx}_to_{dst_idx}" + input_path.suffix)
    output_path.write_bytes(out)
    return output_path


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print(__doc__)
        return 1
    in_path = Path(argv[0])
    src = int(argv[1])
    dst = int(argv[2])
    out_path = None
    if len(argv) >= 5 and argv[3] == '-o':
        out_path = Path(argv[4])
    out = copy_patch(in_path, src, dst, out_path)
    print(f"Wrote: {out} (copied {src} -> {dst})")
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))

