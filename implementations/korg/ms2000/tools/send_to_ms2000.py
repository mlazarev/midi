#!/usr/bin/env python3
"""
Convenience wrapper to send a SysEx (.syx) file to a Korg MS2000/MS2000R.

Defaults:
  - Output port substring: "MS2000"
  - File: implementations/korg/ms2000/patches/OriginalPatches.syx
  - Delay between messages: 50ms

Dependencies:
  pip install mido python-rtmidi

Examples:
  # List MIDI outputs
  python implementations/korg/ms2000/tools/send_to_ms2000.py --list-outputs

  # Send the bundled factory bank to a port containing "MS2000"
  python implementations/korg/ms2000/tools/send_to_ms2000.py

  # Override file or port
  python implementations/korg/ms2000/tools/send_to_ms2000.py \
      --file /path/to/your.syx --out "Your MIDI Interface"
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def project_root() -> Path:
    # This file: <repo>/implementations/korg/ms2000/tools/send_to_ms2000.py
    # repo root should be parents[4]
    return Path(__file__).resolve().parents[4]


def default_bank_path() -> Path:
    return project_root() / "implementations/korg/ms2000/patches/OriginalPatches.syx"


def import_send_sysex():
    root = project_root()
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    # Import the shared CLI as a module
    from tools import send_sysex  # type: ignore

    return send_sysex


def main(argv=None) -> int:
    send_sysex = import_send_sysex()

    p = argparse.ArgumentParser(description="Send SysEx to Korg MS2000/MS2000R")
    p.add_argument(
        "--file",
        type=Path,
        default=default_bank_path(),
        help=".syx file to send (default: bundled OriginalPatches.syx)",
    )
    p.add_argument(
        "--out",
        type=str,
        default="MS2000",
        help="Substring to select the MIDI output port (default: MS2000)",
    )
    p.add_argument(
        "--list-outputs",
        action="store_true",
        help="List available MIDI output ports and exit",
    )
    p.add_argument(
        "--delay-ms",
        type=int,
        default=50,
        help="Delay between SysEx messages in the file (ms) (default: 50)",
    )
    p.add_argument(
        "--auto-fix",
        action="store_true",
        help="If last message misses F7, strip trailing zeros and append F7",
    )

    args = p.parse_args(argv)

    if args.list_outputs:
        outs = send_sysex.list_outputs()
        if outs:
            print("Available MIDI outputs:")
            for i, name in enumerate(outs):
                print(f"  [{i}] {name}")
        else:
            print("No MIDI output ports found")
        return 0

    if not args.file.exists():
        print(f"File not found: {args.file}")
        return 1

    try:
        send_sysex.send_sysex_file(
            file_path=args.file,
            out_name=args.out,
            delay_ms=args.delay_ms,
            auto_fix=args.auto_fix,
        )
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

