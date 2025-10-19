# BOCSunday Changelog

This file tracks notable changes and fixes for the BOCSunday patch bank.

## 2025-10-19 — Hardware validation and final fixes

- Fixed Korg 7-bit encoding variant used by generator. Hardware requires variant v2
  (MSB of decoded byte j encoded in bit j of the MSB byte). This resolves garbled
  names (e.g., leading 'K') and silent programs when sending banks or single programs.
- Corrected OSC2 parameter byte packing strictly to MS2000 spec (B4..5 = Mod Select,
  B0..1 = Wave). Constrained OSC2 waves to Saw/Square/Triangle. Updated A12 to use
  Triangle on OSC2.
- Ensured program header byte 16 uses a sane value for Single mode.
- Regenerated full bank at 37,163 bytes. Verified A01–A16 audible on hardware and names display correctly.

## 2025-01-19 — Initial creation and encoding fix

- Implemented BOC-style patch generation and 7→8 bit encoder.
- Fixed handling of final partial group in encoder (no zero padding for incomplete group),
  yielding the correct encoded size (37,157) and total bank size (37,163).

