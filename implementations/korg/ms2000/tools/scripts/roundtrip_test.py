#!/usr/bin/env python3
"""Quick regression check for decoder/encoder round-trips."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from implementations.korg.ms2000.tools.lib.ms2000_core import (  # type: ignore
    build_patch_bytes,
    encode_bank_from_json,
    extract_full_parameters,
    load_bank,
    slot_name,
)


def roundtrip_report(syx_path: Path) -> dict:
    header, patches = load_bank(syx_path)
    records = []
    for idx, patch in enumerate(patches, start=1):
        record = {
            "index": idx,
            "slot": slot_name(idx),
        }
        record.update(extract_full_parameters(patch))
        records.append(record)

    rebuilt = encode_bank_from_json(records, midi_channel=header.midi_channel, function=header.function)
    original = syx_path.read_bytes()

    mismatches = []
    if rebuilt != original:
        for i, (a, b) in enumerate(zip(rebuilt, original)):
            if a != b:
                mismatches.append(i)
                if len(mismatches) >= 10:
                    break

    return {
        "input": str(syx_path),
        "patch_count": len(records),
        "byte_equal": rebuilt == original,
        "first_differences": mismatches,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify decode/encode round-trip correctness.")
    parser.add_argument("syx", type=Path, help="Path to a PROGRAM DATA DUMP bank")
    parser.add_argument("--json-out", type=Path, help="Optional JSON dump of decoded patches")
    args = parser.parse_args()

    report = roundtrip_report(args.syx)

    if args.json_out:
        header, patches = load_bank(args.syx)
        records = []
        for idx, patch in enumerate(patches, start=1):
            record = {
                "index": idx,
                "slot": slot_name(idx),
            }
            record.update(extract_full_parameters(patch))
            records.append(record)
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(records, indent=2))

    print(json.dumps(report, indent=2))
    return 0 if report["byte_equal"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
