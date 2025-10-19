#!/usr/bin/env python3
"""
Export a single MS2000 program (254-byte patch) from a bank to a
CURRENT PROGRAM DATA DUMP (.syx) message (Function 0x40).

Usage:
  python export_single_program.py <bank.syx> <patch_number 1..128> [-o out.syx]

Sends no MIDI; just writes a .syx file containing one program.
This format is useful to test whether a patch sounds correct when
loaded into the edit buffer, bypassing full-bank encoding concerns.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from decode_sysex import parse_sysex_file  # type: ignore


def encode_korg_7bit(decoded_data: bytes, variant: str = 'v1') -> bytes:
    encoded = bytearray()
    i = 0
    while i < len(decoded_data):
        chunk = decoded_data[i:i+7]
        if not chunk:
            break
        msb_byte = 0
        for j, b in enumerate(chunk):
            if b & 0x80:
                # Two observed variants in Korg encodings:
                #  v1: MSBs placed into bits 6..0 (j -> 6-j)
                #  v2: MSBs placed into bits 0..6 (j -> j)
                if variant == 'v2':
                    msb_byte |= 1 << j
                else:
                    msb_byte |= 1 << (6 - j)
        encoded.append(msb_byte)
        for b in chunk:
            encoded.append(b & 0x7F)
        i += 7
    return bytes(encoded)


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 1
    bank = Path(argv[0])
    idx = int(argv[1])
    out = None
    if len(argv) >= 4 and argv[2] == '-o':
        out = Path(argv[3])
        variant = 'v1'
    else:
        # Optional variant flag after index
        variant = 'v1'
        if len(argv) >= 3 and argv[2] in ('--v1','--v2'):
            variant = argv[2][2:]
            if len(argv) >= 5 and argv[3] == '-o':
                out = Path(argv[4])

    patches = parse_sysex_file(str(bank))
    if not (1 <= idx <= len(patches)):
        print(f"Patch index out of range (1..{len(patches)}): {idx}")
        return 1

    raw = patches[idx - 1].raw_data
    assert len(raw) >= 254
    raw = raw[:254]
    enc = encode_korg_7bit(raw, variant=variant)

    # CURRENT PROGRAM DATA DUMP header
    syx = bytes([0xF0, 0x42, 0x30, 0x58, 0x40]) + enc + bytes([0xF7])

    if out is None:
        out = bank.with_name(bank.stem + f"_P{idx:03d}_current_{variant}.syx")
    out.write_bytes(syx)
    print(f"Wrote: {out} (single program {idx})")
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
