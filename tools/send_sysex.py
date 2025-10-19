#!/usr/bin/env python3
"""
Send SysEx (.syx) files to a MIDI output port.

Requirements:
  - Python 3.8+
  - mido
  - python-rtmidi (Mido backend)

Install (one time):
  pip install mido python-rtmidi

Usage examples:
  # List MIDI output ports
  python tools/send_sysex.py --list-outputs

  # Send a .syx file to a specific output by substring match
  python tools/send_sysex.py --file implementations/korg/ms2000/patches/factory/FactoryBanks.syx \
      --out "MS2000" --delay-ms 50

Notes:
  - This tool sends the SysEx messages found in the file as-is.
  - If the file contains trailing zeros and no F7 terminator, you can use
    '--auto-fix' to strip trailing zeros and append F7. Use with care.
  - For devices that require pacing between multiple messages, use '--delay-ms'.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import Iterable, List, Tuple


def read_syx_messages(data: bytes, auto_fix: bool = False) -> List[bytes]:
    """Extract one or more SysEx messages from raw .syx file content.

    Returns a list of complete messages including F0...F7.
    If auto_fix is True, strips trailing zeros and appends F7 when missing
    for the last message.
    """
    msgs: List[bytes] = []
    i = 0
    n = len(data)

    while i < n:
        # Find start (F0)
        try:
            start = data.index(0xF0, i)
        except ValueError:
            break

        # Find end (F7)
        try:
            end = data.index(0xF7, start + 1)
            msgs.append(data[start : end + 1])
            i = end + 1
        except ValueError:
            # No F7 found. Optionally fix by trimming zeros and appending F7.
            if auto_fix:
                # Trim trailing zeros
                end_pos = n
                for j in range(n - 1, start - 1, -1):
                    if data[j] != 0x00:
                        end_pos = j + 1
                        break
                fixed = data[start:end_pos] + bytes([0xF7])
                msgs.append(fixed)
            else:
                raise ValueError(
                    "Malformed SysEx: message starting at offset "
                    f"0x{start:02X} has no terminating F7. Use --auto-fix to append."
                )
            break

    if not msgs:
        raise ValueError("No SysEx (F0...F7) messages found in file")

    return msgs


def list_outputs() -> List[str]:
    try:
        import mido
    except ImportError as e:
        raise SystemExit(
            "Missing dependency: mido. Install with: pip install mido python-rtmidi"
        ) from e
    return mido.get_output_names()


def choose_output(port_query: str | None) -> str:
    outputs = list_outputs()
    if not outputs:
        raise SystemExit("No MIDI output ports available")

    if port_query is None:
        # Default to first port, but show choices
        print("Available MIDI outputs:")
        for idx, name in enumerate(outputs):
            print(f"  [{idx}] {name}")
        print("\nUse --out <substring> to select a port by name.")
        return outputs[0]

    # Substring match (case-insensitive)
    q = port_query.lower()
    matches = [name for name in outputs if q in name.lower()]
    if not matches:
        raise SystemExit(
            f"No output port matches '{port_query}'.\nAvailable: "
            + ", ".join(outputs)
        )
    if len(matches) > 1:
        print("Multiple matches; using the first:")
        for name in matches:
            print(f"  - {name}")
        print()
    return matches[0]


def send_sysex_file(
    file_path: Path, out_name: str, delay_ms: int = 0, auto_fix: bool = False
) -> None:
    try:
        import mido
    except ImportError as e:
        raise SystemExit(
            "Missing dependency: mido. Install with: pip install mido python-rtmidi"
        ) from e

    data = file_path.read_bytes()
    messages = read_syx_messages(data, auto_fix=auto_fix)

    port_name = choose_output(out_name)
    print(f"Opening MIDI out: {port_name}")
    with mido.open_output(port_name) as out:
        for idx, msg_bytes in enumerate(messages, 1):
            # mido expects sysex data without F0/F7
            if not (msg_bytes and msg_bytes[0] == 0xF0 and msg_bytes[-1] == 0xF7):
                raise ValueError("Internal error: extracted message is not F0...F7")
            payload = msg_bytes[1:-1]
            msg = mido.Message('sysex', data=list(payload))
            print(f"Sending SysEx message {idx}/{len(messages)}: {len(msg_bytes)} bytes")
            out.send(msg)
            if delay_ms > 0 and idx < len(messages):
                time.sleep(delay_ms / 1000.0)
    print("Done.")


def main(argv: List[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Send SysEx (.syx) files to a MIDI port")
    p.add_argument(
        "--file",
        type=Path,
        help="Path to .syx file to send (may contain one or more SysEx messages)",
    )
    p.add_argument(
        "--out",
        type=str,
        default=None,
        help="Substring to select MIDI output port (case-insensitive). Defaults to first port.",
    )
    p.add_argument(
        "--list-outputs",
        action="store_true",
        help="List available MIDI outputs and exit",
    )
    p.add_argument(
        "--delay-ms",
        type=int,
        default=0,
        help="Delay between multiple SysEx messages in the file (milliseconds)",
    )
    p.add_argument(
        "--auto-fix",
        action="store_true",
        help="If last message misses F7, strip trailing zeros and append F7",
    )

    args = p.parse_args(argv)

    if args.list_outputs:
        outs = list_outputs()
        if outs:
            print("Available MIDI outputs:")
            for i, name in enumerate(outs):
                print(f"  [{i}] {name}")
        else:
            print("No MIDI output ports found")
        return 0

    if not args.file:
        p.print_help()
        return 1

    if not args.file.exists():
        print(f"File not found: {args.file}")
        return 1

    try:
        send_sysex_file(args.file, args.out, args.delay_ms, args.auto_fix)
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
