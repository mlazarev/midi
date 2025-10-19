# Send SysEx CLI

Simple cross‑platform CLI to send SysEx (.syx) files to a MIDI output using Python + Mido.

Path: `tools/send_sysex.py`

Requirements:
- Python 3.8+
- mido
- python-rtmidi (Mido backend)

Install:
```
pip install mido python-rtmidi
```

List outputs:
```
python3 tools/send_sysex.py --list-outputs
```

Send a file:
```
python3 tools/send_sysex.py --file implementations/korg/ms2000/patches/OriginalPatches.syx \
    --out "MS2000" --delay-ms 50
```

Options:
- `--file PATH`         SysEx file to send (required unless listing)
- `--out NAME`          Substring to select output port (default: first port)
- `--list-outputs`      Show available MIDI outputs and exit
- `--delay-ms N`        Delay between multiple messages in file (ms)
- `--auto-fix`          If last message is missing F7, strip trailing zeros and append F7

Notes:
- Files may contain one or more SysEx messages back‑to‑back (F0...F7 sequences). The tool sends each in order.
- Use `--delay-ms` for devices that need pacing between consecutive SysEx messages.
- Use `--auto-fix` with care. If a file is malformed (e.g., padded with zeros), this can append F7 to the final message.

