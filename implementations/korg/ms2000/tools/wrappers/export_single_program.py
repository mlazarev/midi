#!/usr/bin/env python3
"""
Backward-compatible wrapper for the unified MS2000 CLI exporter.

Usage:
    python export_single_program.py <bank.syx> <patch 1..128> [-o out.syx] [--v1|--v2]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parents[1]
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    parser = argparse.ArgumentParser(description="Export a single MS2000 program")
    parser.add_argument("bank", type=Path, help="Path to MS2000 .syx bank")
    parser.add_argument("patch", type=int, help="Patch index (1..128)")
    parser.add_argument(
        "--v1",
        action="store_true",
        help="Use MSB packing variant v1 (default)",
    )
    parser.add_argument(
        "--v2",
        action="store_true",
        help="Use MSB packing variant v2",
    )
    parser.add_argument(
        "-o", "--output", type=Path, help="Output .syx file (optional)"
    )
    parsed = parser.parse_args(args)

    if parsed.patch < 1 or parsed.patch > 128:
        parser.error("Patch index must be in range 1..128")

    variant = "v2" if parsed.v2 else "v1"

    cli_args = [
        "export",
        str(parsed.bank),
        str(parsed.patch),
        "--variant",
        variant,
    ]
    if parsed.output:
        cli_args.extend(["--output", str(parsed.output)])

    from ms2000_cli import main as cli_main  # type: ignore

    return cli_main(cli_args)


if __name__ == "__main__":
    raise SystemExit(main())
