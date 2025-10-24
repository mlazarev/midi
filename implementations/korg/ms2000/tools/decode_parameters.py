#!/usr/bin/env python3
"""
Backward-compatible wrapper for the unified MS2000 CLI decoder.

Original usage:
    python decode_parameters.py <input.syx> <output.json> [--patch-index N]

The implementation now forwards to `ms2000_cli.py decode ...`.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    parser = argparse.ArgumentParser(description="Decode MS2000 patches to JSON")
    parser.add_argument("input", type=Path, help="Path to MS2000 .syx bank")
    parser.add_argument("output", type=Path, help="Output JSON file")
    parser.add_argument(
        "--patch-index",
        type=int,
        default=None,
        help="Decode a single patch (1..128)",
    )
    parsed = parser.parse_args(args)

    cli_args = ["decode", str(parsed.input), "--output", str(parsed.output)]
    if parsed.patch_index is not None:
        cli_args.extend(["--patch-index", str(parsed.patch_index)])

    from ms2000_cli import main as cli_main  # type: ignore

    return cli_main(cli_args)


if __name__ == "__main__":
    raise SystemExit(main())
