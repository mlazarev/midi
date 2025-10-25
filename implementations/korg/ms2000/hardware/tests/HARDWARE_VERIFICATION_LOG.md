# Hardware Verification Log — Korg MS2000

> 2025-??-?? — User confirmed full hardware verification completed for Korg MS2000 offset-64 edge cases. Capture detailed readings below when available.

| Date | Firmware | Test Patch | Parameter Focus | Expected | Actual | Status | Notes |
|------|----------|------------|-----------------|----------|--------|--------|-------|
| TBD  | 1.x      | `edge_case_pan_center.json` | Amp panpot | 0 → byte 64 → synth CNT | — | ☐ | Verify after sending via `send_to_ms2000.py`. |
| TBD  | 1.x      | `edge_case_pan_extremes.json` | Amp panpot | -64/63 ↔ bytes 0/127 | — | ☐ | Confirm extremes mirror hardware display (L64/R63). |
| TBD  | 1.x      | `edge_case_osc2_semitone.json` | OSC2 semitone | -12/0/+12 ↔ bytes 52/64/76 | — | ☐ | Ensure octave offsets map correctly. |
| TBD  | 1.x      | `edge_case_mod_intensity.json` | Patch matrix intensity | -63/0/+63 ↔ bytes 1/64/127 | — | ☐ | Confirm modulation depth sign handling. |

## Procedure
1. Encode each JSON patch with `ms2000_cli.py encode`.
2. Transmit via `tools/scripts/send_to_ms2000.py` (target port: MS2000/MS2000R).
3. Inspect the front-panel parameter display; capture photos or notes.
4. Record results in the table above, including any deviations.
5. If discrepancies are found, open an issue and re-run unit roundtrip tests.

## Attachments
- Patches referenced above live alongside this log in the same directory.
- Keep raw SysEx captures for failing cases if possible (name with timestamp).
