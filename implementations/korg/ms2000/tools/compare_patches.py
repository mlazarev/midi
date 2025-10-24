#!/usr/bin/env python3
"""
Backward-compatible wrapper for the unified MS2000 CLI compare command.

Usage:
    python compare_patches.py <file1.syx> <file2.syx> [--patch-index N] [--json]
"""

from __future__ import annotations

import sys


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    from ms2000_cli import main as cli_main  # type: ignore

    return cli_main(["compare", *args])


if __name__ == "__main__":
    raise SystemExit(main())
