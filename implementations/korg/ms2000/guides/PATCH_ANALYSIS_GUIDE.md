# MS2000 Patch Analysis Guide

This guide describes practical techniques for analyzing Korg MS2000 patch banks to understand stylistic tendencies, parameter usage, and common building blocks across presets. It is intended for education and exploration of sound design on the MS2000.

Contents
- Goals
- What you can learn
- How to run the analyzer
- Interpreting results
- Deeper investigations
- Tips for reproducibility

Goals
- Summarize how patches use voice modes, effects, arpeggiator, and key parameters.
- Identify recurring patterns (e.g., modulation depth ranges, delay types).
- Provide a foundation for library organization or style exploration.

What you can learn
- Naming conventions: frequent tokens (e.g., “pad”, “bass”) and average name length.
- Voice modes: distribution between Single / Layer / Split / Vocoder.
- Effects usage: delay type popularity, modulation types (Chorus/Flanger/Ensemble/Phaser).
- Arpeggiator: how often it’s enabled, common types, typical tempos.
- Parameter ranges: summaries (min/max/mean/median) for modulation speed/depth, delay time/depth.

How to run the analyzer
- Use the generic analyzer (works for any MS2000 bank):
```
python tools/analyze_patch_bank.py implementations/korg/ms2000/patches/OriginalPatches.syx
```

- Optional JSON output:
```
python tools/analyze_patch_bank.py implementations/korg/ms2000/patches/OriginalPatches.syx --json > report.json
```

- Limit analysis to first N patches:
```
python tools/analyze_patch_bank.py implementations/korg/ms2000/patches/OriginalPatches.syx --limit 32
```

Interpreting results
- Names
  - Top tokens: Helps you categorize patches by names appearing frequently.
  - Avg length: Shorter names may indicate working banks; longer names often appear in curated libraries.
- Voice modes
  - High proportion of Single may indicate lead/bass focus; Layer/Split suggests performance/texture focus.
- Effects
  - Delay types: “StereoDelay” vs “L/R Delay” vs “CrossDelay” hints at spatial design preferences.
  - Mod types: “Cho/Flg”, “Ensemble”, “Phaser” reveal the modulation aesthetic.
- Arpeggiator
  - Enabled %: How often rhythmic motion is used.
  - Type distribution: Up/Down/Alt/Random/Trigger highlights rhythmic variety.
  - Tempo summary: Typical tempo ranges in arpeggiated patches.
- Parameters
  - Mod Speed/Depth: Typical ranges for motion intensity; slow/fast LFO preferences.
  - Delay Time/Depth: Ambient vs rhythmic bias.

Deeper investigations
- Compare two banks with `compare_patches.py` to see differences patch-by-patch.
- Extend the analyzer to compute additional stats:
  - EQ distributions (hi/low freq, gain)
  - Arp flags (latch, target, keysync)
  - Name similarity clustering (e.g., normalized edit distance)
  - Per-bank fingerprints (e.g., histogram vectors) for rough similarity matching

Tips for reproducibility
- Work from exact .syx sources and record checksums or file sizes.
- Avoid modifying patches during analysis; keep a clean copy.
- For public sharing, avoid including proprietary content; share only your metrics and methodology.

Disclaimer
This guide focuses on analysis techniques. It does not depend on or reference any specific commercial or third‑party banks. Apply these methods to your own material and public domain sources as appropriate.

