#!/usr/bin/env python3
"""
Dump an MS2000 PROGRAM DATA DUMP (.syx) bank as JSON.

Usage:
  python dump_bank_json.py <bank.syx> <output.json>
"""

from __future__ import annotations

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from decode_sysex import parse_sysex_file  # type: ignore


def slot_name(index: int) -> str:
    bank = chr(ord('A') + (index // 16))
    num = (index % 16) + 1
    return f"{bank}{num:02d}"


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 1
    in_path = Path(argv[0])
    out_path = Path(argv[1])

    patches = parse_sysex_file(str(in_path))
    out = []
    for i, p in enumerate(patches):
        d = p.raw_data
        entry = {
            "index": i + 1,
            "slot": slot_name(i),
            "name": p.name,
            "voice_mode": getattr(p, "voice_mode", ""),
            "scale": {"key": getattr(p, "scale_key", ""), "type": getattr(p, "scale_type", 0)},
            "delay": {
                "type": getattr(p, "delay_type", ""),
                "time": getattr(p, "delay_time", 0),
                "depth": getattr(p, "delay_depth", 0),
            },
            "mod_fx": {
                "type": getattr(p, "mod_type", ""),
                "speed": getattr(p, "mod_speed", 0),
                "depth": getattr(p, "mod_depth", 0),
            },
            "arp": {
                "on": getattr(p, "arp_on", False),
                "type": getattr(p, "arp_type", ""),
                "range": getattr(p, "arp_range", 0),
                "tempo": getattr(p, "arp_tempo", 0),
            },
            "raw_hex": d[:254].hex(),
        }
        out.append(entry)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2))
    print(f"Wrote JSON: {out_path} ({len(out)} patches)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

