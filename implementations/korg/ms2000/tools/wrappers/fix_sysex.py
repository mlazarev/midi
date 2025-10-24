#!/usr/bin/env python3
"""
Backward-compatible wrapper for the unified MS2000 CLI repair command.

Usage:
    python fix_sysex.py <bank.syx> [--no-pad] [--json] [--output fixed.syx]
"""

from __future__ import annotations

import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parents[1]
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    from ms2000_cli import main as cli_main  # type: ignore

    return cli_main(["repair", *args])


if __name__ == "__main__":
    raise SystemExit(main())
