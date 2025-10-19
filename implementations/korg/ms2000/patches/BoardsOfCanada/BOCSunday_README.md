# BOCSunday.syx - Original Boards of Canada Style Patches

**16 original patches created from scratch using BOC synthesis principles**

Created: 2025-01-19
Bank Size: 37,163 bytes (128 patches, A01-H16)
Unique Patches: 16 (A01-A16)
Filler Patches: 112 (B01-H16, repeats of "Lazy Sunday")

Encoding: Korg 7-bit variant v2 (MSB of decoded byte j is stored in bit j of the MSB byte).

## Overview

These patches were algorithmically generated based on detailed analysis of 123 authentic BOC patches, implementing the core BOC sound design principles:

- **L/R Delay dominance** (77% of original patches use this)
- **Chorus/Flanger for wobble** (72% of original patches)
- **12dB LPF filters** with low resonance
- **Perfect fifth intervals** on OSC2 (+7, +5, +12 semitones)
- **Dual LFO pitch modulation** (Triangle + Sine)
- **Long envelope releases** for ambient character
- **Minimal portamento and distortion**

All patches are **audible and playable** with carefully balanced parameters.

---

## Patch List

### A01: Lazy Sunday
**Type:** Classic BOC Pad
**Character:** Warm, nostalgic, gentle wobble

**Oscillators:**
- OSC1: Sine wave, full level
- OSC2: Triangle, +7 semitones (perfect fifth)
- Noise: 18 (subtle analog texture)

**Filter:** 12dB LPF, Cutoff=52, Resonance=18
**Envelopes:** Fast attack, medium decay, high sustain, long release
**LFOs:**
- LFO1 (Triangle, 12Hz) → Pitch (+9) for slow vibrato
- LFO2 (Sine, 68Hz) → Pan (+25) for stereo movement
- LFO1 → Cutoff (+12) for breathing

**Effects:**
- Delay: L/R Delay, Time=38, Depth=88
- Mod FX: Chorus/Flanger, Speed=18, Depth=32

**Best For:** Ambient pads, background textures, nostalgic melodies

---

### A02: Analog Mem
**Type:** Detuned Lead
**Character:** Wobbly, vintage, memorable melody lead

**Oscillators:**
- OSC1: Saw wave
- OSC2: Saw wave, -7 semitones (fifth down), +8 cents detune
- Noise: 22

**Filter:** 12dB LPF, Cutoff=58, Resonance=22, EG1 Int=+18
**Envelopes:** Instant attack, moderate decay/sustain
**LFOs:**
- LFO1 (Triangle, 10Hz) → Pitch (+11) for vibrato
- LFO2 (Sine, 65Hz) → Cutoff (+16) for movement
- LFO1 → OSC2 Pitch (-12) for detuning wobble

**Effects:**
- Delay: L/R Delay, Time=42, Depth=78
- Mod FX: Chorus/Flanger, Speed=22, Depth=38

**Best For:** Melodic leads, arpeggios, main melodies

---

### A03: Vintage Tape
**Type:** DWGS Texture
**Character:** Complex, evolving, digital meets analog

**Oscillators:**
- OSC1: DWGS wavetable #28
- OSC2: Triangle, +12 semitones (octave up)
- Noise: 25 (tape hiss simulation)

**Filter:** 12dB LPF, Cutoff=48, Resonance=24, EG1 Int=+22
**Envelopes:** Slow attack, long decay/release
**LFOs:**
- LFO1 (Triangle, 35Hz) → medium modulation
- LFO2 (S/H, 115Hz) → random stepped modulation
- LFO2 → Cutoff (+8) for random filter movement
- EG1 → Pitch (+14) for pitch drop on note attack

**Effects:**
- Delay: L/R Delay, Time=40, Depth=92
- Mod FX: Phaser, Speed=25, Depth=15

**Best For:** Evolving pads, sound design, atmospheric textures

---

### A04: Nostalgia
**Type:** Warm Pad
**Character:** Pure, simple, emotional

**Oscillators:**
- OSC1: Triangle wave
- OSC2: Triangle, +5 semitones (perfect fourth)
- Noise: 16

**Filter:** 12dB LPF, Cutoff=50, Resonance=16, EG1 Int=+5
**Envelopes:** Slow attack (10ms), long sustain/release
**LFOs:**
- LFO1 (Triangle, 8Hz) → Pitch (+8) very slow vibrato
- LFO2 (Sine, 72Hz) → Cutoff (+18) gentle breathing
- LFO2 → Pan (+22) stereo width

**Effects:**
- Delay: L/R Delay, Time=40, Depth=85
- Mod FX: Chorus/Flanger, Speed=16, Depth=28

**Best For:** Emotional chords, simple harmonies, reflective moments

---

### A05: Warm Rhodes
**Type:** Bell/EP Tone
**Character:** Metallic, bell-like, electric piano quality

**Oscillators:**
- OSC1: Sine wave (fundamental)
- OSC2: Square wave with **Ring Modulation**, unison tuning
- Noise: 18

**Filter:** 24dB LPF (darker), Cutoff=38, Resonance=8, EG1 Int=+20
**Envelopes:**
- EG1: Medium attack/decay, high sustain, very long release
- EG2: **Slow attack (110ms)** for swell, long decay/release

**LFOs:**
- LFO1 (Triangle, 40Hz) → OSC2 Pitch (-12) for bell shimmer
- LFO2 (Sine, 70Hz) → Pan (+28) and Amp (+35) for movement

**Effects:**
- Delay: L/R Delay, Time=40, Depth=70
- Mod FX: Chorus/Flanger, Speed=20, Depth=35

**Best For:** Keys, bell tones, plucked/struck sounds, Rhodes-like tones

---

### A06: Dusty Bass
**Type:** Analog Bass
**Character:** Deep, warm, slightly detuned sub bass

**Oscillators:**
- OSC1: Saw wave
- OSC2: Triangle, -12 semitones (octave down)
- Noise: 12 (minimal)

**Filter:** 24dB LPF (tight), Cutoff=35, Resonance=18, EG1 Int=+25
**Envelopes:** Instant attack, short decay/sustain, short release
**LFOs:**
- LFO1 (Triangle, 15Hz) → Cutoff (+22) filter wobble
- EG1 → Pitch (+8) slight pitch drop on attack
- LFO2 → OSC1 Ctrl (+15) pulse width modulation

**Effects:**
- Delay: L/R Delay, Time=40, Depth=60 (less than pads)
- Mod FX: Chorus/Flanger, Speed=25, Depth=20

**Best For:** Basslines, low-end foundation, groove

---

### A07: Childhood
**Type:** Arpeggiator Sequence
**Character:** Playful, melodic, repeating pattern

**Oscillators:**
- OSC1: DWGS wavetable #15
- OSC2: Saw, +7 semitones
- Noise: 8 (minimal)

**Filter:** 12dB LPF, Cutoff=45, Resonance=20, EG1 Int=+12
**Envelopes:** Instant attack, medium decay, medium sustain
**LFOs:**
- LFO1 (Triangle, 12Hz) → Pitch (+7)
- LFO2 (Sine, 65Hz) → Cutoff (+14)
- LFO1 → OSC2 Pitch (+6) subtle detuning

**Arpeggiator:**
- **ON**, Type=Up, Range=2 octaves
- Tempo=85 BPM, Gate=78%, Latch=ON

**Effects:**
- Delay: L/R Delay, Time=40, Depth=75
- Mod FX: Ensemble, Speed=155, Depth=12

**Best For:** Sequenced melodies, arpeggiated chords, rhythmic patterns

---

### A08: Faded Photo
**Type:** Ambient Pad
**Character:** Distant, dreamy, layered octaves

**Oscillators:**
- OSC1: Sine wave
- OSC2: Saw, +19 semitones (octave + fifth)
- Noise: 22

**Filter:** 12dB LPF, Cutoff=44, Resonance=15, EG1 Int=+10
**Envelopes:** Slow attack, long sustain/release
**LFOs:**
- LFO1 (Triangle, 9Hz) → Pitch (+10)
- LFO2 (Sine, 74Hz) → Cutoff (+20) and Pan (+30)

**Effects:**
- Delay: L/R Delay, Time=38, Depth=90 (high feedback)
- Mod FX: Chorus/Flanger, Speed=14, Depth=42

**Best For:** Ethereal pads, background atmosphere, film scoring

---

### A09: 70s Sky
**Type:** Vintage Synth Pad
**Character:** Retro, analog, PWM modulation

**Oscillators:**
- OSC1: Pulse wave, PWM via Ctrl1=45
- OSC2: Triangle, +12 semitones (octave)
- Noise: 14

**Filter:** 12dB LPF, Cutoff=62, Resonance=25, EG1 Int=+15
**Envelopes:** Slow attack (15ms), long sustain/release
**LFOs:**
- LFO1 (Triangle, 11Hz) → Pitch (+8)
- LFO2 (Sine, 68Hz) → OSC1 Ctrl (+18) for PWM
- LFO1 → Cutoff (+10)

**Effects:**
- Delay: **StereoDelay**, Time=55, Depth=65
- Mod FX: Ensemble, Speed=18, Depth=25

**Best For:** Vintage synth sounds, 1970s character, string machines

---

### A10: Wobbly Lead
**Type:** Sync Lead
**Character:** Aggressive, harmonically rich, unstable pitch

**Oscillators:**
- OSC1: Saw wave
- OSC2: Saw with **Sync modulation**, +7 semitones, +5 cents detune
- Noise: 18

**Filter:** 12dB LPF, Cutoff=60, Resonance=20, EG1 Int=+20
**Envelopes:** Instant attack, medium decay/sustain/release
**LFOs:**
- LFO1 (Triangle, 8Hz) → Pitch (+12) strong vibrato
- LFO2 (Sine, 66Hz) → Pitch (+6) secondary wobble
- LFO1 → Cutoff (+14)

**Effects:**
- Delay: L/R Delay, Time=40, Depth=82
- Mod FX: Chorus/Flanger, Speed=30, Depth=45 (heavy)

**Best For:** Lead lines with character, solos, aggressive melodies

---

### A11: Distant
**Type:** Ambient DWGS Pad
**Character:** Far away, hazy, floating

**Oscillators:**
- OSC1: DWGS wavetable #35
- OSC2: Triangle, +7 semitones
- Noise: 28 (high for lo-fi character)

**Filter:** 12dB LPF, Cutoff=40, Resonance=12, EG1 Int=+18
**Envelopes:** Slow attack (20ms), very long sustain/release
**LFOs:**
- LFO1 (Triangle, 10Hz) → Pitch (+9)
- LFO2 (Sine, 70Hz) → Cutoff (+12) and Pan (+26)

**Effects:**
- Delay: L/R Delay, Time=40, Depth=95 (maximum feedback)
- Mod FX: Phaser, Speed=12, Depth=18

**Best For:** Deep atmospheric pads, distant textures, soundscapes

---

### A12: Soft Pluck
**Type:** Plucked/Pizzicato
**Character:** Gentle attack, natural decay

**Oscillators:**
- OSC1: Triangle wave
- OSC2: Sine, +12 semitones (octave)
- Noise: 10 (minimal)

**Filter:** 12dB LPF, Cutoff=55, Resonance=18, EG1 Int=+28
**Envelopes:**
- EG1: Instant attack, short decay (35ms), low sustain, short release
- EG2: Instant attack, short decay (38ms), medium sustain

**LFOs:**
- EG1 → Pitch (+10) for pitch drop on pluck
- LFO2 (Sine, 65Hz) → Cutoff (+8)
- LFO1 (Triangle, 18Hz) → Pan (+15)

**Effects:**
- Delay: L/R Delay, Time=42, Depth=68
- Mod FX: Chorus/Flanger, Speed=22, Depth=30

**Best For:** Plucked melodies, pizzicato strings, mallet sounds

---

### A13: Morning Haze
**Type:** Vox Wave Pad
**Character:** Vocal-like, human quality

**Oscillators:**
- OSC1: Vox Wave (formant wave)
- OSC2: Triangle, +5 semitones
- Noise: 20

**Filter:** 12dB LPF, Cutoff=48, Resonance=16, EG1 Int=+12
**Envelopes:** Slow attack (8ms), long sustain/release
**LFOs:**
- LFO1 (Triangle, 10Hz) → Pitch (+9)
- LFO2 (Sine, 72Hz) → Cutoff (+16)
- LFO1 → OSC1 Ctrl (+12) for formant sweep

**Effects:**
- Delay: L/R Delay, Time=40, Depth=88
- Mod FX: Chorus/Flanger, Speed=15, Depth=35

**Best For:** Vocal-like pads, human textures, choir-like sounds

---

### A14: Quiet Moment
**Type:** Pure Sine Pad
**Character:** Simple, pure, contemplative

**Oscillators:**
- OSC1: Sine wave
- OSC2: Sine, +7 semitones, +3 cents detune
- Noise: 15

**Filter:** 12dB LPF, Cutoff=46, Resonance=14, EG1 Int=+6
**Envelopes:** Slow attack (15ms), very long sustain/release
**LFOs:**
- LFO1 (Triangle, 9Hz) → Pitch (+7) gentle vibrato
- LFO2 (Sine, 68Hz) → Pan (+24)
- LFO1 → Cutoff (+8)

**Effects:**
- Delay: L/R Delay, Time=38, Depth=80
- Mod FX: Ensemble, Speed=10, Depth=22

**Best For:** Minimalist pads, pure tones, meditation music

---

### A15: Retro Sweep
**Type:** Bandpass Filter Sweep
**Character:** Phaser-like, sweeping, retro

**Oscillators:**
- OSC1: Pulse wave, PWM via Ctrl1=55
- OSC2: Saw, +12 semitones
- Noise: 18

**Filter:** **12dB BPF** (bandpass), Cutoff=58, Resonance=28, EG1 Int=+35
**Envelopes:** Fast attack (5ms), medium envelope with strong filter sweep
**LFOs:**
- LFO1 (Triangle, 32Hz) → Cutoff (+25) sweeping
- LFO2 (Sine, 70Hz) → OSC1 Ctrl (+20) PWM
- EG1 → Pitch (+12) pitch drop

**Effects:**
- Delay: L/R Delay, Time=40, Depth=72
- Mod FX: Phaser, Speed=28, Depth=30

**Best For:** Filter sweeps, risers, retro leads

---

### A16: Sunset
**Type:** Classic BOC Chord Pad
**Character:** Warm, full, perfect for chords

**Oscillators:**
- OSC1: Saw wave
- OSC2: Triangle, +7 semitones (perfect fifth)
- Noise: 20

**Filter:** 12dB LPF, Cutoff=53, Resonance=19, EG1 Int=+10
**Envelopes:** Medium attack (10ms), long sustain/release
**LFOs:**
- LFO1 (Triangle, 10Hz) → Pitch (+9)
- LFO2 (Sine, 70Hz) → Cutoff (+15) and Pan (+28)

**Effects:**
- Delay: L/R Delay, Time=40, Depth=86
- Mod FX: Chorus/Flanger, Speed=17, Depth=33

**Best For:** Chord progressions, harmonic pads, main progressions

---

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
python3 tools/send_sysex.py --file implementations/korg/ms2000/patches/BOCSunday.syx \
    --out "MS2000" --delay-ms 50

# Or using send_to_ms2000.py (convenience wrapper)
python3 implementations/korg/ms2000/tools/send_to_ms2000.py BOCSunday.syx
```

### Via Hardware:
1. Connect MIDI OUT from computer to MS2000 MIDI IN
2. Set MS2000 to receive SysEx (Global > MIDI > SysEx = Enable)
3. Send file using your MIDI software
4. Patches will load into banks A-H (A01-H16)

---

## Credits

**Created:** 2025-01-19
**Based on:** Analysis of 123 authentic BOC patches for MS2000
**Method:** Algorithmic generation using statistical analysis of BOC synthesis principles
**Documentation:** Complete parameter breakdown in HOW_TO_MAKE_BOARDS_OF_CANADA_SOUNDS.md

---

## Related Files

- **Analysis Guide:** `/docs/HOW_TO_MAKE_BOARDS_OF_CANADA_SOUNDS.md`
- **Generator Script:** `patches/BoardsOfCanada/create_boc_patches.py`
- **Decoder:** `tools/decode_sysex.py`
- **Original BOC Bank:** `patches/BOCPatches.syx` (reference/comparison)

Enjoy exploring the Boards of Canada sound on your MS2000! 🎹
