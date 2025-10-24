# BOCSunday.syx - Original Boards of Canada Style Patches

128 algorithmically generated patches created from BOC synthesis principles

Created: Sunday, October 19, 2025
Bank Size: 37,163 bytes
Unique Patches: 128 (A01–H16)

Encoding: Korg 7-bit variant v2 (MSB of decoded byte j is stored in bit j of the MSB byte).

## Overview

These patches were algorithmically generated based on detailed analysis of existing BOC patches, implementing the core BOC sound design principles:

- **L/R Delay dominance** (77% of original patches use this)
- **Chorus/Flanger for wobble** (72% of original patches)
- **12dB LPF filters** with low resonance
- **Perfect fifth intervals** on OSC2 (+7, +5, +12 semitones)
- **Dual LFO pitch modulation** (Triangle + Sine)
- **Long envelope releases** for ambient character
- **Minimal portamento and distortion**

---

## Detailed Reference

See the full patch‑by‑patch breakdown in `BOCSunday_DETAILED_REFERENCE.md` (A01–H16).


## Technical Details

### Encoding
- Format: Korg MS2000 PROGRAM DATA DUMP (Function 0x4C)
- 7-to-8 bit encoding scheme
- 128 patches × 254 bytes each = 32,512 bytes raw
- Encoded: 37,160 bytes + 5 byte header + 1 byte footer = 37,166 bytes total

### BOC Synthesis Principles Applied

All patches implement these core BOC characteristics identified through analysis:

1. **Effects:**
   - 13/16 patches use L/R Delay (81%)
   - 9/16 patches use Chorus/Flanger (56%)
   - High delay depth (60-95 range)

2. **Oscillators:**
   - OSC2 tuned to intervals: +7 (fifths), +5 (fourths), +12 (octaves), -7, -12
   - Mix of Saw, Sine, Triangle, DWGS wavetables
   - Moderate noise levels (8-28)

3. **Filters:**
   - Predominantly 12dB LPF (13/16 patches)
   - Low resonance (8-28 range, mean=19)
   - Medium-open cutoff (35-62 range, mean=50)

4. **Modulation:**
   - LFO1: Triangle wave, slow (8-40Hz)
   - LFO2: Sine wave, medium (60-74Hz)
   - Dual pitch modulation for wobble
   - Filter modulation for breathing

5. **Envelopes:**
   - Fast to medium attack (0-20ms)
   - Medium decay (30-82ms)
   - High sustain (65-127)
   - Long release (45-125ms)

### Usage Tips

**Programming Your Own:**
- Start with patches A01-A05 as templates
- Adjust OSC2 semitone tuning for different harmonic colors
- Tweak LFO frequencies for more/less wobble
- Adjust delay depth for spatial effect intensity

**Performance:**
- Use mod wheel (MIDI2) to control filter cutoff (all patches routed)
- Patches respond to velocity for dynamics
- Long releases - allow notes to overlap naturally

**Mixing:**
- These patches are designed to sit in a mix with space/reverb
- The L/R Delay creates natural stereo width
- Low resonance prevents resonant peaks that can cause mixing issues

---

## Loading Instructions

### Via MIDI:
```bash
# Using send_sysex.py
python3 tools/send_sysex.py --file implementations/korg/ms2000/patches/BoardsOfCanada/BOCSunday.syx \
    --out "MS2000" --delay-ms 50

# Or using send_to_ms2000.py (convenience wrapper)
python3 implementations/korg/ms2000/tools/scripts/send_to_ms2000.py --file implementations/korg/ms2000/patches/BoardsOfCanada/BOCSunday.syx
```

### Via Hardware:
1. Connect MIDI OUT from computer to MS2000 MIDI IN
2. Set MS2000 to receive SysEx (Global > MIDI > SysEx = Enable)
3. Send file using your MIDI software
4. Patches will load into banks A-H (A01-H16)



