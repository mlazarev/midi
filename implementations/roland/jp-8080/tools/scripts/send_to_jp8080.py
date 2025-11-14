#!/usr/bin/env python3
"""
Send a JP-8080 SysEx patch to the synthesizer via MIDI.

This script uses mido to send SysEx messages. It provides options for
selecting MIDI output port and timing delays.

Dependencies:
  pip install mido python-rtmidi
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

try:
    import mido
except ImportError:
    print("Error: mido not installed. Install with: pip install mido python-rtmidi", file=sys.stderr)
    sys.exit(1)


def list_outputs() -> None:
    """List available MIDI output ports."""
    outputs = mido.get_output_names()
    if not outputs:
        print("No MIDI output ports found.")
        return

    print("Available MIDI output ports:")
    for i, name in enumerate(outputs):
        print(f"  [{i}] {name}")


def send_sysex_file(
    file_path: Path,
    port_name: str | None = None,
    delay_ms: int = 50,
) -> None:
    """Send a SysEx file to the specified MIDI port."""

    # Auto-detect port if not specified
    if port_name is None:
        outputs = mido.get_output_names()
        # Look for JP-8080 or Roland
        for name in outputs:
            if "JP-8080" in name or "JP8080" in name or "EDIROL" in name:
                port_name = name
                break

        if port_name is None and outputs:
            port_name = outputs[0]

    if port_name is None:
        raise ValueError("No MIDI output ports available")

    # Read SysEx file
    sysex_data = file_path.read_bytes()

    if sysex_data[0] != 0xF0 or sysex_data[-1] != 0xF7:
        raise ValueError("Invalid SysEx file (missing F0 or F7)")

    # Open MIDI port and send
    print(f"Sending to: {port_name}")
    print(f"File: {file_path}")
    print(f"Size: {len(sysex_data)} bytes")

    with mido.open_output(port_name) as port:
        # Convert to mido SysEx message
        msg = mido.Message('sysex', data=list(sysex_data[1:-1]))  # Strip F0 and F7

        port.send(msg)
        time.sleep(delay_ms / 1000.0)

        print("✓ SysEx sent successfully")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Send JP-8080 SysEx patch to synthesizer",
    )
    parser.add_argument(
        "--list-outputs",
        action="store_true",
        help="List available MIDI output ports and exit",
    )
    parser.add_argument(
        "file",
        type=Path,
        nargs="?",
        help="SysEx file to send",
    )
    parser.add_argument(
        "--out",
        type=str,
        help="MIDI output port name (auto-detect if not specified)",
    )
    parser.add_argument(
        "--delay-ms",
        type=int,
        default=50,
        help="Delay after sending in milliseconds (default: 50)",
    )

    args = parser.parse_args()

    if args.list_outputs:
        list_outputs()
        return 0

    if not args.file:
        parser.print_help()
        return 1

    try:
        send_sysex_file(args.file, args.out, args.delay_ms)
        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
