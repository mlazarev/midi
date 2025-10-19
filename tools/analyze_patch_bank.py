#!/usr/bin/env python3
"""
Analyze a Korg MS2000 SysEx bank and report summary statistics.

Generic tool: does not depend on any specific bank. Works with any
MS2000 PROGRAM DATA DUMP (.syx) file and prints human‑readable stats,
optionally JSON.

Usage:
  python tools/analyze_patch_bank.py implementations/korg/ms2000/patches/factory/FactoryBanks.syx

Options:
  --json           Output JSON instead of text
  --limit N        Limit number of patches analyzed

Notes:
  Requires only Python stdlib. Imports the MS2000 decoder from
  implementations/korg/ms2000/tools/decode_sysex.py
"""

from __future__ import annotations

import argparse
import json
import statistics as stats
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List


def load_patches(syx_path: Path):
    import sys

    # Ensure repo root is on sys.path so we can import the decoder
    repo_root = Path(__file__).resolve().parents[1]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    from implementations.korg.ms2000.tools.decode_sysex import parse_sysex_file  # type: ignore

    return parse_sysex_file(str(syx_path))


def tokenise_name(name: str) -> List[str]:
    name = name.replace("_", " ")
    tokens = [t.lower() for t in name.split() if t]
    return tokens


def analyze(patches, limit: int | None = None) -> Dict[str, Any]:
    if limit is not None:
        patches = patches[:limit]

    n = len(patches)
    names = [p.name for p in patches]
    name_lengths = [len(p.name) for p in patches]
    name_tokens = Counter(t for p in patches for t in tokenise_name(p.name))

    # Distributions
    voice_modes = Counter(p.voice_mode for p in patches)
    delay_types = Counter(p.delay_type for p in patches)
    mod_types = Counter(p.mod_type for p in patches)
    arp_on = sum(1 for p in patches if getattr(p, "arp_on", False))
    arp_types = Counter(p.arp_type for p in patches if getattr(p, "arp_on", False))

    # Numeric stats (where available)
    mod_speed = [p.mod_speed for p in patches]
    mod_depth = [p.mod_depth for p in patches]
    delay_time = [p.delay_time for p in patches]
    delay_depth = [p.delay_depth for p in patches]
    arp_tempo = [p.arp_tempo for p in patches]

    def summary(values: List[int]) -> Dict[str, Any]:
        if not values:
            return {}
        return {
            "min": min(values),
            "max": max(values),
            "mean": round(stats.mean(values), 2),
            "median": stats.median(values),
        }

    result: Dict[str, Any] = {
        "patch_count": n,
        "names": {
            "avg_length": round(stats.mean(name_lengths), 2) if name_lengths else 0,
            "top_tokens": name_tokens.most_common(10),
        },
        "voice_modes": voice_modes.most_common(),
        "effects": {
            "delay_types": delay_types.most_common(),
            "mod_types": mod_types.most_common(),
        },
        "arpeggiator": {
            "enabled_count": arp_on,
            "enabled_pct": round((arp_on / n) * 100, 1) if n else 0.0,
            "types": arp_types.most_common(),
            "tempo": summary(arp_tempo),
        },
        "parameters": {
            "mod_speed": summary(mod_speed),
            "mod_depth": summary(mod_depth),
            "delay_time": summary(delay_time),
            "delay_depth": summary(delay_depth),
        },
    }

    return result


def print_text(report: Dict[str, Any]) -> None:
    print(f"Patches analyzed: {report['patch_count']}")
    print()
    print("Names:")
    print(f"  Avg length: {report['names']['avg_length']}")
    if report['names']['top_tokens']:
        print("  Top tokens:")
        for token, cnt in report['names']['top_tokens']:
            print(f"    {token}: {cnt}")
    print()
    print("Voice modes:")
    for name, cnt in report['voice_modes']:
        print(f"  {name}: {cnt}")
    print()
    print("Effects:")
    print("  Delay types:")
    for name, cnt in report['effects']['delay_types']:
        print(f"    {name}: {cnt}")
    print("  Mod types:")
    for name, cnt in report['effects']['mod_types']:
        print(f"    {name}: {cnt}")
    print()
    print("Arpeggiator:")
    print(f"  Enabled: {report['arpeggiator']['enabled_count']} "
          f"({report['arpeggiator']['enabled_pct']}%)")
    if report['arpeggiator']['types']:
        print("  Types:")
        for name, cnt in report['arpeggiator']['types']:
            print(f"    {name}: {cnt}")
    if report['arpeggiator']['tempo']:
        t = report['arpeggiator']['tempo']
        print(f"  Tempo: min {t['min']}, max {t['max']}, mean {t['mean']}, median {t['median']}")
    print()
    print("Parameter summaries:")
    for key, s in report['parameters'].items():
        if not s:
            continue
        print(f"  {key}: min {s['min']}, max {s['max']}, mean {s['mean']}, median {s['median']}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Analyze MS2000 SysEx patch banks")
    ap.add_argument("syx", type=Path, help="Path to MS2000 .syx bank (PROGRAM DATA DUMP)")
    ap.add_argument("--json", action="store_true", help="Output JSON instead of text")
    ap.add_argument("--limit", type=int, default=None, help="Limit patches analyzed")
    args = ap.parse_args()

    patches = load_patches(args.syx)
    report = analyze(patches, limit=args.limit)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_text(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
