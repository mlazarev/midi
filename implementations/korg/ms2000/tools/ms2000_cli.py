#!/usr/bin/env python3
"""
Unified command-line interface for Korg MS2000 tooling.

Subcommands:
  inspect  - Quick human-readable overview (optionally JSON) of bank or patch
  decode   - Emit full parameter JSON for whole bank or a single patch
  analyze  - Statistical summaries or single-patch snapshot
  compare  - Diff two banks or individual patches
  export   - Write a CURRENT PROGRAM DATA DUMP (.syx) for a selected patch
  repair   - Fix common SysEx issues (missing F7, optional 128-patch warning)

Each subcommand accepts --patch-index where applicable to focus on a single
program, and supports JSON output for automation as well as human-readable text.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple

if __package__:
    from .lib.ms2000_core import (
        analyse_patches,
        analyse_single_patch,
        extract_full_parameters,
        load_bank,
        parse_sysex_file,
        repair_sysex,
        select_patches,
        slot_name,
        export_single_program,
    )
else:  # pragma: no cover - invoked as script
    tools_dir = Path(__file__).resolve().parent
    sys.path.insert(0, str(tools_dir))
    sys.path.insert(0, str(tools_dir / "lib"))
    from ms2000_core import (  # type: ignore
        analyse_patches,
        analyse_single_patch,
        extract_full_parameters,
        load_bank,
        parse_sysex_file,
        repair_sysex,
        select_patches,
        slot_name,
        export_single_program,
    )


def _format_header(header) -> str:
    return (
        "SysEx Header:\n"
        f"  Manufacturer: 0x{header.manufacturer:02X}\n"
        f"  MIDI Channel: {header.midi_channel}\n"
        f"  Device: 0x{header.device:02X}\n"
        f"  Function: 0x{header.function:02X}"
    )


def _records_with_metadata(
    pairs: Sequence[Tuple[int, Any]], extractor
) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    for index, patch in pairs:
        record = {
            "index": index,
            "slot": slot_name(index),
        }
        record.update(extractor(patch))
        records.append(record)
    return records


def _print_patch_summaries(pairs: Sequence[Tuple[int, Any]]) -> None:
    for index, patch in pairs:
        summary = patch.summary_dict()
        line = (
            f"{slot_name(index)} {summary['name'] or '(Unnamed)'} "
            f"| Mode: {summary['voice_mode']} "
            f"| Delay: {summary['delay']['type']} "
            f"| Mod: {summary['mod']['type']} "
            f"| Arp: {'ON' if summary['arp']['on'] else 'OFF'}"
        )
        print(line)


def _print_full_records(records: Sequence[Dict[str, Any]]) -> None:
    for record in records:
        header = f"{record['slot']} – {record['name']} ({record['voice_mode']})"
        print(header)
        print("-" * len(header))
        print(json.dumps(record, indent=2))
        print()


def _print_analyse_report(report: Dict[str, Any]) -> None:
    if report.get("patch_count", 0) == 0 and "name" not in report:
        print("No patches to analyse.")
        return
    if "name" in report:
        print(f"Patch: {report['name']}")
        print(f"  Voice Mode : {report['voice_mode']}")
        print(f"  Delay Type : {report['delay']}")
        print(f"  Mod Type   : {report['mod']}")
        print(f"  Arp Enabled: {'YES' if report['arp_on'] else 'NO'}")
        if report['arp_on']:
            print(f"  Arp Tempo  : {report['arp_tempo']}")
        return

    print(f"Patches analysed: {report['patch_count']}")
    print()
    print("Name tokens:")
    for token, count in report["names"]["top_tokens"]:
        print(f"  {token}: {count}")
    print()
    print("Voice modes:")
    for name, count in report["voice_modes"]:
        print(f"  {name}: {count}")
    print()
    print("Effects (top counts):")
    for name, count in report["effects"]["delay_types"]:
        print(f"  Delay {name}: {count}")
    for name, count in report["effects"]["mod_types"]:
        print(f"  Mod {name}: {count}")
    print()
    arp = report["arpeggiator"]
    print(f"Arpeggiator enabled: {arp['enabled_count']} ({arp['enabled_pct']}%)")
    if arp["types"]:
        for name, count in arp["types"]:
            print(f"  {name}: {count}")
    if arp["tempo"]:
        tempo = arp["tempo"]
        print(
            f"  Tempo min {tempo['min']} max {tempo['max']} "
            f"mean {tempo['mean']} median {tempo['median']}"
        )


def _patch_index_type(value: str) -> int:
    idx = int(value)
    if idx < 1 or idx > 128:
        raise argparse.ArgumentTypeError("Patch index must be between 1 and 128")
    return idx


def _compare_patch(patch1, patch2, index: int) -> Dict[str, Any]:
    fields = [
        ("name", patch1.name, patch2.name),
        ("voice_mode", patch1.voice_mode, patch2.voice_mode),
        ("delay.type", patch1.delay_type, patch2.delay_type),
        ("delay.time", patch1.delay_time, patch2.delay_time),
        ("mod.type", patch1.mod_type, patch2.mod_type),
        ("mod.speed", patch1.mod_speed, patch2.mod_speed),
        ("arp.on", patch1.arp_on, patch2.arp_on),
        ("arp.type", patch1.arp_type, patch2.arp_type),
    ]
    differences = [
        {"field": field, "file1": left, "file2": right}
        for field, left, right in fields
        if left != right
    ]
    raw_diff = sum(1 for a, b in zip(patch1.raw_data, patch2.raw_data) if a != b)
    identical = not differences and raw_diff == 0
    return {
        "index": index,
        "slot": slot_name(index),
        "differences": differences,
        "raw_diff_bytes": raw_diff,
        "identical": identical,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Korg MS2000 unified tooling")
    subparsers = parser.add_subparsers(dest="command", required=True)

    parser_inspect = subparsers.add_parser("inspect", help="Show summary information")
    parser_inspect.add_argument("file", type=Path, help="Path to MS2000 .syx bank")
    parser_inspect.add_argument(
        "--patch-index",
        type=_patch_index_type,
        help="Inspect a single patch (1..128)",
    )
    parser_inspect.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of patches displayed (ignored with --patch-index)",
    )
    parser_inspect.add_argument(
        "--json", action="store_true", help="Emit JSON summary instead of text"
    )

    parser_decode = subparsers.add_parser(
        "decode", help="Dump full parameter data as JSON"
    )
    parser_decode.add_argument("file", type=Path, help="Path to MS2000 .syx bank")
    parser_decode.add_argument(
        "--patch-index",
        type=_patch_index_type,
        help="Decode a single patch (1..128)",
    )
    parser_decode.add_argument(
        "--output",
        type=Path,
        help="Write JSON to file instead of stdout",
    )
    parser_decode.add_argument(
        "--json",
        action="store_true",
        help="Print JSON to stdout (default human-readable summary)",
    )

    parser_analyze = subparsers.add_parser(
        "analyze", help="Summarise bank statistics or single patch"
    )
    parser_analyze.add_argument("file", type=Path, help="Path to MS2000 .syx bank")
    parser_analyze.add_argument(
        "--patch-index",
        type=_patch_index_type,
        help="Analyse a single patch instead of the whole bank",
    )
    parser_analyze.add_argument(
        "--json", action="store_true", help="Emit JSON instead of text"
    )

    parser_export = subparsers.add_parser(
        "export", help="Write a CURRENT PROGRAM DATA DUMP (.syx) for one patch"
    )
    parser_export.add_argument("file", type=Path, help="Path to MS2000 .syx bank")
    parser_export.add_argument(
        "patch_index",
        type=_patch_index_type,
        help="Patch number to export (1..128)",
    )
    parser_export.add_argument(
        "--variant",
        choices=("v1", "v2"),
        default="v1",
        help="Encoding variant for MSB packing (default: v1)",
    )
    parser_export.add_argument(
        "--output",
        type=Path,
        help="Output .syx path (defaults to bank stem with suffix)",
    )

    parser_repair = subparsers.add_parser(
        "repair", help="Fix missing F7 terminator and warn about short banks"
    )
    parser_repair.add_argument("file", type=Path, help="Path to MS2000 .syx bank")
    parser_repair.add_argument(
        "--output",
        type=Path,
        help="Write repaired file to this path (defaults to in-place overwrite)",
    )
    parser_repair.add_argument(
        "--no-pad",
        action="store_true",
        help="Skip 128-patch padding check (still appends missing F7)",
    )
    parser_repair.add_argument(
        "--json", action="store_true", help="Emit JSON report instead of text"
    )

    parser_compare = subparsers.add_parser(
        "compare", help="Compare two banks or individual patches"
    )
    parser_compare.add_argument("file1", type=Path, help="First MS2000 .syx bank")
    parser_compare.add_argument("file2", type=Path, help="Second MS2000 .syx bank")
    parser_compare.add_argument(
        "--patch-index",
        type=_patch_index_type,
        help="Compare a single patch (1..128)",
    )
    parser_compare.add_argument(
        "--json", action="store_true", help="Emit JSON instead of text"
    )

    return parser


def cmd_inspect(args: argparse.Namespace) -> int:
    header, patches = load_bank(args.file)
    pairs = select_patches(patches, args.patch_index)
    if args.patch_index is None and args.limit is not None:
        pairs = pairs[: max(args.limit, 0)]

    if args.json:
        records = _records_with_metadata(pairs, lambda p: p.summary_dict())
        payload = {
            "header": {
                "manufacturer": header.manufacturer,
                "midi_channel": header.midi_channel,
                "device": header.device,
                "function": header.function,
            },
            "patches": records,
        }
        print(json.dumps(payload, indent=2))
    else:
        print(_format_header(header))
        print()
        _print_patch_summaries(pairs)
    return 0


def cmd_decode(args: argparse.Namespace) -> int:
    header, patches = load_bank(args.file)
    pairs = select_patches(patches, args.patch_index)
    records = _records_with_metadata(pairs, extract_full_parameters)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(records, indent=2))
        if not args.json:
            print(f"Wrote JSON: {args.output}")

    if args.json:
        print(json.dumps(records, indent=2))
    elif not args.output:
        print(_format_header(header))
        print()
        _print_full_records(records)
    return 0


def cmd_analyze(args: argparse.Namespace) -> int:
    patches = parse_sysex_file(args.file)
    if args.patch_index:
        patch = select_patches(patches, args.patch_index)[0][1]
        report = analyse_single_patch(patch)
    else:
        report = analyse_patches(patches)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        _print_analyse_report(report)
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    header, patches = load_bank(args.file)
    _ = header  # header unused but load_bank validates file
    output_path = export_single_program(
        args.file,
        patches,
        args.patch_index,
        variant=args.variant,
        output=args.output,
    )
    print(f"Wrote: {output_path}")
    return 0


def cmd_repair(args: argparse.Namespace) -> int:
    report = repair_sysex(
        args.file,
        output_path=args.output,
        pad_to_128=not args.no_pad,
    )
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"Input : {report['input']}")
        print(f"Output: {report['output']}")
        for change in report.get("changes", []):
            print(f"Applied: {change}")
        if "warning" in report:
            print(f"Warning: {report['warning']}")
        if "patch_count" in report:
            print(f"Patches detected: {report['patch_count']}")
    return 0


def cmd_compare(args: argparse.Namespace) -> int:
    header1, patches1 = load_bank(args.file1)
    header2, patches2 = load_bank(args.file2)

    if args.patch_index:
        if args.patch_index > len(patches1) or args.patch_index > len(patches2):
            raise ValueError("Patch index out of range for one of the banks")
        indices = [args.patch_index]
    else:
        max_pairs = min(len(patches1), len(patches2))
        indices = list(range(1, max_pairs + 1))

    results = [
        _compare_patch(patches1[i - 1], patches2[i - 1], i) for i in indices
    ]

    identical = sum(1 for r in results if r["identical"])
    different = len(results) - identical

    extra_info: Dict[str, Any] = {}
    if not args.patch_index and len(patches1) != len(patches2):
        if len(patches1) > len(patches2):
            extra_info = {"file": str(args.file1), "count": len(patches1) - len(patches2)}
        else:
            extra_info = {"file": str(args.file2), "count": len(patches2) - len(patches1)}

    if args.json:
        payload = {
            "file1": str(args.file1),
            "file2": str(args.file2),
            "patch_counts": {
                "file1": len(patches1),
                "file2": len(patches2),
            },
            "patch_index": args.patch_index,
            "identical_count": identical,
            "different_count": different,
            "differences": [r for r in results if not r["identical"]],
        }
        if extra_info:
            payload["extra_patches"] = extra_info
        print(json.dumps(payload, indent=2))
        return 0

    print("File 1:", args.file1)
    print("File 2:", args.file2)
    print()
    print(f"Patches compared: {len(results)} (File1: {len(patches1)}, File2: {len(patches2)})")
    print()

    for record in results:
        if record["identical"]:
            continue
        print(f"[{record['slot']}] Patch {record['index']}")
        for diff in record["differences"]:
            print(
                f"  {diff['field']}: {diff['file1']}  vs  {diff['file2']}"
            )
        if not record["differences"] and record["raw_diff_bytes"] > 0:
            print(f"  Raw data differs ({record['raw_diff_bytes']} bytes)")
        elif record["raw_diff_bytes"] > 0:
            print(f"  Raw data differs ({record['raw_diff_bytes']} bytes)")
        print()

    print("Summary")
    print("-------")
    print(f"Identical patches: {identical}")
    print(f"Different patches: {different}")
    if extra_info:
        print(f"Extra patches in {extra_info['file']}: {extra_info['count']}")
    return 0


COMMANDS = {
    "inspect": cmd_inspect,
    "decode": cmd_decode,
    "analyze": cmd_analyze,
    "export": cmd_export,
    "repair": cmd_repair,
    "compare": cmd_compare,
}


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        handler = COMMANDS[args.command]
    except KeyError:  # pragma: no cover - argparse enforces command
        parser.error(f"Unknown command: {args.command}")
        return 2
    try:
        return handler(args)
    except Exception as exc:  # pragma: no cover - runtime errors
        parser.exit(2, f"Error: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
