#!/usr/bin/env python3
"""
Unified command-line interface for Roland JP-8080 tooling.

Subcommands:
  inspect  - Quick human-readable overview of patch
  decode   - Emit full parameter JSON for a patch
  analyze  - Statistical summaries or single-patch snapshot

Each subcommand supports JSON output for automation as well as human-readable text.

Note: Currently supports individual patch SysEx files. Bulk dump support
will be added in a future update.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

if __package__:
    from .lib.jp8080_core import (
        analyse_patches,
        extract_full_parameters,
        load_patch_from_sysex,
        parse_sysex_file,
        slot_name,
    )
else:  # pragma: no cover - invoked as script
    tools_dir = Path(__file__).resolve().parent
    sys.path.insert(0, str(tools_dir))
    sys.path.insert(0, str(tools_dir / "lib"))
    from jp8080_core import (  # type: ignore
        analyse_patches,
        extract_full_parameters,
        load_patch_from_sysex,
        parse_sysex_file,
        slot_name,
    )


def _format_header(header) -> str:
    return (
        "SysEx Header:\n"
        f"  Manufacturer: Roland (0x{header.manufacturer:02X})\n"
        f"  Device ID: 0x{header.device_id:02X}\n"
        f"  Model ID: {header.model_id[0]:02X} {header.model_id[1]:02X} (JP-8080)\n"
        f"  Command: 0x{header.command:02X}"
    )


def cmd_inspect(args: argparse.Namespace) -> int:
    """Inspect command - show patch overview."""
    try:
        header, patch, address = load_patch_from_sysex(args.file)

        if args.json:
            result = {
                "header": {
                    "manufacturer": header.manufacturer,
                    "device_id": header.device_id,
                    "model_id": header.model_id,
                    "command": header.command,
                    "address": f"0x{address:08X}",
                },
                "patch": patch.summary_dict(),
            }
            print(json.dumps(result, indent=2))
        else:
            print(_format_header(header))
            print(f"  Address: 0x{address:08X}")
            print()
            print(patch.summary_text())

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_decode(args: argparse.Namespace) -> int:
    """Decode command - emit full JSON parameters."""
    try:
        header, patch, address = load_patch_from_sysex(args.file)
        params = extract_full_parameters(patch)

        # Add metadata
        result = {
            "index": 1,
            "address": f"0x{address:08X}",
            **params,
        }

        output_path = args.output or Path(args.file).with_suffix('.json')
        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2)

        print(f"Decoded patch saved to: {output_path}")
        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_analyze(args: argparse.Namespace) -> int:
    """Analyze command - show statistics."""
    try:
        header, patch, _ = load_patch_from_sysex(args.file)

        if args.json:
            analysis = {
                "patch_count": 1,
                "patch": patch.summary_dict(),
            }
            print(json.dumps(analysis, indent=2))
        else:
            print(f"Patch Analysis: {patch.name}")
            print("=" * 60)
            print()

            summary = patch.summary_dict()

            print("Oscillators:")
            print(f"  OSC1 Waveform: {summary['oscillators']['osc1_wave']}")
            print(f"  OSC2 Waveform: {summary['oscillators']['osc2_wave']}")
            print(f"  Balance: {summary['oscillators']['balance']:+d}")
            print()

            print("Filter:")
            print(f"  Type: {summary['filter']['type']}")
            print(f"  Cutoff: {summary['filter']['cutoff']}")
            print(f"  Resonance: {summary['filter']['resonance']}")
            print()

            print("Effects:")
            print(f"  Multi FX: {summary['effects']['multi_fx']}")
            print(f"  Delay: {summary['effects']['delay']}")
            print()

            print("Voice Settings:")
            print(f"  Mono: {'YES' if summary['voice']['mono'] else 'NO'}")
            print(f"  Legato: {'YES' if summary['voice']['legato'] else 'NO'}")
            print(f"  Portamento: {'YES' if summary['voice']['portamento'] else 'NO'}")

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Roland JP-8080 SysEx Tools",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # INSPECT subcommand
    inspect_parser = subparsers.add_parser(
        "inspect",
        help="Display patch overview",
    )
    inspect_parser.add_argument("file", type=Path, help="SysEx file to inspect")
    inspect_parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )

    # DECODE subcommand
    decode_parser = subparsers.add_parser(
        "decode",
        help="Decode patch to JSON",
    )
    decode_parser.add_argument("file", type=Path, help="SysEx file to decode")
    decode_parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Output JSON file (default: input.json)",
    )

    # ANALYZE subcommand
    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Analyze patch parameters",
    )
    analyze_parser.add_argument("file", type=Path, help="SysEx file to analyze")
    analyze_parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    if args.command == "inspect":
        return cmd_inspect(args)
    elif args.command == "decode":
        return cmd_decode(args)
    elif args.command == "analyze":
        return cmd_analyze(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
