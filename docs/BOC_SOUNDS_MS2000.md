# How to Make Boards of Canada Sounds on the Korg MS2000

**A comprehensive analysis and guide based on authentic BOC patch bank analysis**

## Table of Contents
1. [Introduction](#introduction)
2. [The Boards of Canada Sound](#the-boards-of-canada-sound)
3. [BOC Patch Bank Analysis](#boc-patch-bank-analysis)
4. [Core Programming Principles](#core-programming-principles)
5. [Step-by-Step Patch Recipes](#step-by-step-patch-recipes)
6. [Advanced Techniques](#advanced-techniques)
7. [Parameter Reference](#parameter-reference)

---

## Introduction

This guide is based on detailed analysis of 123 Boards of Canada-style patches created specifically for the Korg MS2000. By examining every parameter across all patches, we've identified the specific techniques, settings, and patterns that create the iconic BOC sound on this virtual analog synthesizer.

**What makes this guide unique:**
- Based on real patch data, not guesswork
- Statistical analysis of parameter distributions
- Comparative study vs. factory presets
- Specific MS2000 parameter values

---

## The Boards of Canada Sound

### Musical Characteristics
**Boards of Canada** (Michael Sandison and Marcus Eoin) are known for:
- **Nostalgic, lo-fi aesthetic** - Warm, slightly degraded analog sound
- **Simple, repetitive melodies** - 5-7 note phrases, hypnotic loops
- **Unconventional structure** - 5-bar phrases instead of typical 4
- **Detuned, wobbly textures** - Pitch drift and chorus effects
- **Vintage tape warmth** - Filtered, muffled tonality
- **Ambient soundscapes** - Lush pads with movement

### Synthesis Approach
- **Analog character** - Imperfect, organic, warm
- **Fifths intervals** - Characteristic harmonic intervals
- **Long envelopes** - Slow attack/release for pads
- **Moderate filtering** - Dark, muffled, not bright
- **Heavy modulation** - LFOs creating movement and pitch wobble
- **Stereo width** - L/R delay and panning modulation

---

## BOC Patch Bank Analysis

### Overview Statistics
- **Total Patches Analyzed:** 123
- **Voice Mode:** 100% Single (simple, monophonic character preferred)
- **Arpeggiator Usage:** 15.4% (minimal, mostly manual playing)
- **Distortion:** Rare (0.8% - almost never used)

### Effects Configuration

#### Delay FX (Critical!)
**BOC patches overwhelmingly favor L/R Delay:**
- **L/R Delay:** 95 patches (77%)  ← **KEY BOC SOUND**
- **Stereo Delay:** 28 patches (23%)
- **Cross Delay:** Rarely used

**Settings:**
- **Delay Time:** Mean=40, Median=40 (clustered around medium-short delays)
  - Factory presets: Mean=64, much more variation
- **Delay Depth:** Mean=80, Median=87 (HIGH - lots of feedback!)
  - Factory presets: Mean=45 (BOC uses nearly 2x depth)
- **Sync:** Typically OFF (free-running time-based delay)

**Why L/R Delay?**
- Creates ping-pong stereo effect
- Adds width and spaciousness
- Vintage tape echo character
- Movement in the stereo field

#### Mod FX
**BOC patches favor Chorus/Flanger:**
- **Cho/Flg:** 89 patches (72%) ← **Essential for detuned wobble**
- **Phaser:** 11 patches (9%)
- **Ensemble:** 9 patches (7%)

**Settings:**
- **Mod Speed:** Mean=34, Median=20 (slow to medium modulation)
- **Mod Depth:** Varies widely (0-163)

**Why Chorus/Flanger?**
- Creates detuned, slightly out-of-tune character
- Adds warmth and analog imperfection
- Thickens sounds
- Vintage synth wobble

#### EQ
**Subtle but important:**
- **Hi Freq:** Mean=20 (moderate high shelf)
- **Hi Gain:** Mean=0 (neutral to slight boost)
- **Lo Freq:** Mean=15 (moderate low shelf)
- **Lo Gain:** Mean slightly negative (subtle low cut)

---

## Core Programming Principles

### 1. Oscillator Configuration

#### OSC1 - Primary Sound Source
**Waveform Distribution:**
- **Saw:** 46 patches (37%) - Classic analog warmth
- **DWGS:** 26 patches (21%) - Digital wavetables for complex tones
- **Sine:** 22 patches (18%) - Pure, mellow tones
- **Triangle:** 12 patches (10%)
- **Pulse:** 8 patches (7%)

**Key Insight:** BOC patches use more SINE and DWGS than factory presets
- Sine waves = pure, mellow, vintage synth character
- DWGS = complex evolving tones without harsh harmonics

**OSC1 Level:** Mean=111, Median=127 (typically MAXED OUT)

#### OSC2 - Texture & Detuning
**Waveform Distribution:**
- **Saw:** 58 patches (47%)
- **Triangle:** 56 patches (46%) ← **More Triangle than factory!**
- **Square:** 9 patches (7%)

**Modulation:**
- **Off:** 86 patches (70%) - Clean layering
- **Ring Mod:** 18 patches (15%) - Metallic/bell tones
- **Sync:** 14 patches (11%) - Harmonic richness
- **Ring+Sync:** 5 patches (4%)

**Semitone Detuning:**
- Mean=+3.7 semitones (BOC often tunes UP for brightness)
- Factory: Mean=-0.2 (centered around unison)
- Range: -15 to +24 semitones
- **Common intervals:** +5 (fourth), +7 (fifth), +12 (octave), +19 (octave + fifth)

**OSC2 Fine Tune:** Used for subtle detuning within semitones

**Key Insight:** Triangle wave on OSC2 = softer, less harsh layering

#### Mixer Levels
- **OSC1:** Usually maxed (127)
- **OSC2:** Mean=92 (slightly lower than OSC1)
- **Noise:** Mean=18 (subtle hiss for analog texture)

### 2. Filter Settings

#### Filter Type
**BOC strongly prefers gentler filtering:**
- **12dB LPF:** 64 patches (52%) ← **MOST COMMON**
- **24dB LPF:** 45 patches (37%)
- **12dB BPF:** 12 patches (10%)
- **12dB HPF:** 2 patches (2%)

**Why 12dB LPF?**
- Less aggressive than 24dB
- Preserves more harmonic content
- Warmer, less "synthesizer-y"
- Vintage character

#### Cutoff Frequency
**BOC: Mean=61, Median=53**
- Factory: Mean=44 (BOC is BRIGHTER on average!)
- Range: 0-127 (full spectrum used)
- Mode: Clustered in 40-70 range (medium-open filter)

**Surprising Finding:** Despite "dark" reputation, BOC patches have HIGHER cutoff than factory presets. The "muffled" sound comes from:
- 12dB slope (not 24dB)
- Chorus/Delay effects
- EQ sculpting
- Envelope shaping

#### Resonance
**BOC: Mean=19, Median=20 (LOW!)**
- Factory: Mean=41 (BOC uses HALF the resonance)
- Range: 0-79
- Most patches: 0-30 range

**Why Low Resonance?**
- Natural, not "synthy"
- No resonant peak ringing
- Smooth, organic filtering
- Vintage synth character (early synths had limited resonance)

#### Filter Modulation
- **EG1 Intensity:** Mean=-4 to +29 (subtle)
- **Velocity Sensitivity:** Moderate
- **Keyboard Tracking:** Moderate

### 3. Envelopes

#### EG1 (Filter Envelope)
**Attack:** Mean=11, Median=0 (FAST/INSTANT)
- 0-105 range, heavily weighted toward 0
- Quick filter openings

**Decay:** Mean=61, Median=64 (MEDIUM)
- Consistent around middle values
- Moderate filter closure

**Sustain:** Mean=102, Median=127 (HIGH/FULL)
- Most patches sustain at full level
- Held notes don't close filter much

**Release:** Mean=68, Median=90 (MEDIUM-LONG)
- Smooth tail-offs
- 0-127 range used

**EG1 Character:** Fast attack, medium decay, high sustain, medium release
- Filter opens quickly
- Sustains bright
- Smooth release

#### EG2 (Amp Envelope)
**Attack:** Mean=14, Median=0 (FAST/INSTANT)
- Similar to EG1
- Most patches start immediately

**Decay:** Mean=68, Median=64 (MEDIUM)
- Consistent mid-range

**Sustain:** Mean=104, Median=127 (HIGH/FULL)
- Sustained sounds preferred

**Release:** Mean=82, Median=108 (MEDIUM-LONG)
- Longer than EG1
- Smooth, natural fade-outs

**EG2 Character:** Fast attack, medium decay, high sustain, long release
- Classic pad/ambient envelope
- Quick response, long tails

### 4. LFO Configuration

#### LFO1
**Waveform Distribution:**
- **Triangle:** 109 patches (89%) ← **DOMINANT**
- **S/H (Sample & Hold):** 9 patches (7%)
- **Saw:** 5 patches (4%)

**Frequency:** Mean=30, Median=10 (SLOW)
- Range: 8-188
- Most patches: very slow (8-20)

**Key Sync:** Mostly OFF
- Free-running modulation

**Tempo Sync:** Rarely used

**Why Triangle?**
- Smooth, bidirectional modulation
- No sharp transitions
- Natural vibrato/wobble

#### LFO2
**Waveform Distribution:**
- **Sine:** 102 patches (83%) ← **OVERWHELMING FAVORITE**
- **S/H (Sample & Hold):** 19 patches (15%)
- **Saw:** 2 patches (2%)

**Frequency:** Mean=67, Median=70 (MEDIUM-FAST)
- Range: 13-198
- Faster than LFO1
- Clustered around 60-80

**Why Sine?**
- Smoothest possible modulation
- No discontinuities
- Musical vibrato
- Gentle filter sweeps

**LFO Strategy:**
- LFO1 = Slow Triangle (vibrato, wobble)
- LFO2 = Medium-Fast Sine (filter movement, subtle pitch mod)

### 5. Modulation Matrix (Patch Points)

#### Patch 1 (Most Common Routings)
**Sources:**
- **LFO1:** 67 patches (54%)
- **LFO2:** 38 patches (31%)

**Destinations:**
- **Pitch:** 76 patches (62%) ← **VIBRATO IS KEY**
- **Cutoff:** 17 patches (14%)
- **OSC1 Ctrl1:** 15 patches (12%)

**Intensity:** Varies (-63 to +63), typically low to moderate

**Common Routing:** LFO1 → Pitch (+5 to +15)
- Slow triangle vibrato
- Subtle pitch wobble
- Organic character

#### Patch 2 (Second Routing)
**Sources:**
- **LFO2:** 75 patches (61%) ← **DOMINANT**
- **LFO1:** 30 patches (24%)

**Destinations:**
- **Pitch:** 75 patches (61%)
- **Cutoff:** 20 patches (16%)
- **Pan:** 11 patches (9%)

**Common Routing:** LFO2 → Pitch or Cutoff
- Secondary pitch modulation
- Filter movement
- Stereo panning for width

#### Patch 3 (Third Routing)
**Sources:**
- **LFO1:** 63 patches (51%)
- **MIDI2:** 31 patches (25%)
- **LFO2:** 25 patches (20%)

**Destinations:**
- **Cutoff:** 74 patches (60%) ← **FILTER MODULATION**
- **Pitch:** 20 patches (16%)

**Common Routing:** LFO1 or LFO2 → Cutoff
- Slow filter sweeps
- Breathing quality
- Movement

#### Patch 4 (Fourth Routing)
**Sources:**
- **LFO2:** 56 patches (46%)
- **MIDI2:** 52 patches (42%) ← **PERFORMANCE CONTROL**

**Destinations:**
- **Cutoff:** 94 patches (76%) ← **DOMINANT**
- **OSC2 Pitch:** 14 patches (11%)

**Common Routing:** MIDI2 → Cutoff
- Mod wheel controls filter
- Performance expression
- Dynamic timbral changes

### 6. Portamento
**BOC: Mean=0.2, Median=0 (MINIMAL)**
- Factory: Mean=3.0
- BOC patches use almost NO portamento
- Notes change instantly, no glide
- Crisp, defined note transitions

---

## Step-by-Step Patch Recipes

### Recipe 1: Classic BOC Pad

**Purpose:** Warm, nostalgic pad with subtle wobble

**OSCILLATORS:**
```
OSC1:
  Wave: Sine or Triangle
  CTRL1: 0-30 (subtle if using Pulse width)
  CTRL2: 0
  Level: 127

OSC2:
  Wave: Triangle
  Modulation: Off
  Semitone: +7 (perfect fifth)
  Tune: 0
  Level: 90-100
```

**MIXER:**
```
OSC1 Level: 127
OSC2 Level: 92
Noise: 15-25 (subtle analog hiss)
```

**FILTER:**
```
Type: 12dB LPF
Cutoff: 50-60
Resonance: 15-25
EG1 Intensity: 0 to +10
Velocity Sense: 0
Keyboard Track: 64 (neutral)
```

**AMP:**
```
Level: 127
Pan: 64 (center)
Distortion: OFF
```

**ENVELOPES:**
```
EG1 (Filter):
  Attack: 0-10 (fast)
  Decay: 60-70
  Sustain: 120-127
  Release: 80-100

EG2 (Amp):
  Attack: 0-5 (very fast)
  Decay: 60-75
  Sustain: 127
  Release: 100-120 (long tail)
```

**LFOs:**
```
LFO1:
  Wave: Triangle
  Frequency: 10-15 (slow)
  Key Sync: OFF
  Tempo Sync: OFF

LFO2:
  Wave: Sine
  Frequency: 65-75 (medium)
  Key Sync: OFF
  Tempo Sync: OFF
```

**MODULATION (PATCHES):**
```
Patch 1: LFO1 → Pitch (+7 to +10)
Patch 2: LFO2 → Pan (+20 to +30)
Patch 3: LFO1 → Cutoff (+5 to +15)
Patch 4: MIDI2 → Cutoff (+50 to +80)
```

**EFFECTS:**
```
Delay:
  Type: L/R Delay
  Sync: OFF
  Time: 35-45
  Depth: 80-95

Mod FX:
  Type: Cho/Flg (Chorus/Flanger)
  Speed: 15-25 (slow)
  Depth: 25-40

EQ:
  Hi Freq: 18-22
  Hi Gain: 0 to +3
  Low Freq: 14-16
  Low Gain: -5 to 0
```

**ARPEGGIATOR:**
```
OFF (play manually)
```

---

### Recipe 2: Detuned BOC Lead

**Purpose:** Simple, melodic lead with character pitch wobble

**OSCILLATORS:**
```
OSC1:
  Wave: Saw
  CTRL1: 50-70 (pulse width if applicable)
  CTRL2: 0
  Level: 127

OSC2:
  Wave: Saw
  Modulation: Off
  Semitone: -7 (perfect fifth down)
  Tune: +5 to +10 (slight detune for thickness)
  Level: 100-110
```

**FILTER:**
```
Type: 12dB LPF
Cutoff: 55-65
Resonance: 10-20
EG1 Intensity: +15 to +25
```

**ENVELOPES:**
```
EG1 (Filter):
  Attack: 0
  Decay: 55-65
  Sustain: 100-120
  Release: 60-80

EG2 (Amp):
  Attack: 0
  Decay: 50-60
  Sustain: 110-127
  Release: 70-90
```

**LFOs:**
```
LFO1:
  Wave: Triangle
  Frequency: 8-12 (very slow)

LFO2:
  Wave: Sine
  Frequency: 60-70
```

**MODULATION:**
```
Patch 1: LFO1 → Pitch (+8 to +12)
Patch 2: LFO2 → Cutoff (+10 to +20)
Patch 3: LFO1 → OSC2Pitch (-10 to -15)
Patch 4: MIDI2 → Cutoff (+60 to +100)
```

**EFFECTS:**
```
Delay:
  Type: L/R Delay
  Time: 38-42
  Depth: 85-100

Mod FX:
  Type: Cho/Flg
  Speed: 18-25
  Depth: 30-45
```

---

### Recipe 3: DWGS Texture Patch

**Purpose:** Complex, evolving digital texture

**OSCILLATORS:**
```
OSC1:
  Wave: DWGS
  CTRL1: 0 (DWGS Wave Number - experiment!)
  CTRL2: 0
  DWGS: 10-50 (try different wavetables)
  Level: 127

OSC2:
  Wave: Triangle
  Modulation: Off or Ring
  Semitone: +12 or +19 (octave or octave+fifth)
  Tune: 0
  Level: 80-100
```

**FILTER:**
```
Type: 12dB LPF or 24dB LPF
Cutoff: 45-60
Resonance: 20-35
EG1 Intensity: +20 to +35
```

**LFOs:**
```
LFO1:
  Wave: Triangle
  Frequency: 30-50 (medium)

LFO2:
  Wave: S/H (Sample & Hold)
  Frequency: 100-130 (fast random)
```

**MODULATION:**
```
Patch 1: LFO2 → Cutoff (+5 to +10)
Patch 2: EG1 → Pitch (+10 to +15)
Patch 3: LFO2 → Pitch (+8 to +12)
Patch 4: MIDI2 → Cutoff (+40 to +80)
```

**EFFECTS:**
```
Delay:
  Type: L/R Delay
  Time: 40
  Depth: 85-95

Mod FX:
  Type: Phaser or Ensemble
  Speed: 20-30
  Depth: 0-20 (subtle)
```

---

### Recipe 4: Ring Mod Bell Tone

**Purpose:** Metallic, bell-like textures

**OSCILLATORS:**
```
OSC1:
  Wave: Triangle or Sine
  Level: 108

OSC2:
  Wave: Square
  Modulation: Ring or Ring+Sync
  Semitone: 0 (unison for maximum ring effect)
  Tune: 0
  Level: 127
```

**MIXER:**
```
Noise: 15-25
```

**FILTER:**
```
Type: 24dB LPF
Cutoff: 30-40 (lower for darker bell)
Resonance: 0-10
EG1 Intensity: +15 to +25
```

**ENVELOPES:**
```
EG1:
  Attack: 5-15
  Decay: 25-35
  Sustain: 95-105
  Release: 120-127

EG2:
  Attack: 100-120 (slow swell)
  Decay: 90-100
  Sustain: 100-105
  Release: 115-125
```

**LFOs:**
```
LFO1:
  Wave: Triangle
  Frequency: 35-45

LFO2:
  Wave: Sine
  Frequency: 70
```

**MODULATION:**
```
Patch 1: LFO1 → OSC2Pitch (-10 to -15)
Patch 2: LFO2 → Pan (+20 to +30)
Patch 3: LFO2 → Amp (+30 to +45)
Patch 4: MIDI2 → Cutoff (+5 to +15)
```

**EFFECTS:**
```
Delay:
  Type: L/R Delay
  Time: 40
  Depth: 80-90

Mod FX:
  Type: Cho/Flg
  Speed: 20
  Depth: 30-40
```

---

### Recipe 5: Arpeggiator Sequence

**Purpose:** Simple melodic sequence (for occasional use)

**OSCILLATORS:**
```
OSC1:
  Wave: DWGS or Saw
  Level: 127

OSC2:
  Wave: Saw or Triangle
  Semitone: +5 to +7
  Level: 90-100
```

**FILTER:**
```
Type: 12dB LPF
Cutoff: 40-50
Resonance: 15-25
```

**ARPEGGIATOR:**
```
On/Off: ON
Type: Up
Range: 1-2 octaves
Tempo: 75-95 BPM
Gate: 75-85%
Latch: ON or OFF (depends on playing style)
Resolution: 1/16 or 1/8
```

**EFFECTS:**
```
Delay:
  Type: L/R Delay
  Time: 40
  Depth: 65-75

Mod FX:
  Type: Cho/Flg or Ensemble
  Speed: 140-160 (faster for movement)
  Depth: 10-20
```

---

## Advanced Techniques

### 1. The "Fifths" Technique
BOC frequently uses **perfect fifth intervals** (7 semitones) between oscillators:
- OSC2 Semitone: +7 or -7
- Creates hollow, open harmonic character
- Classic 1970s synth sound
- Adds richness without clashing

**Try These Intervals:**
- +5 semitones (perfect fourth)
- +7 semitones (perfect fifth) ← **Most common**
- +12 semitones (octave)
- +19 semitones (octave + fifth)
- -7 semitones (fifth down)

### 2. Dual LFO Pitch Modulation
Many BOC patches use **both LFOs modulating pitch**:
- **LFO1 (Triangle, Slow)** → Pitch (+7 to +12)
  - Slow, wide vibrato
  - "Wobbly tape" effect
- **LFO2 (Sine, Medium-Fast)** → Pitch (+2 to +10)
  - Faster, subtle warble
  - Adds complexity

**Result:** Layered pitch modulation = organic, unstable character

### 3. Filter Cutoff Modulation
Create "breathing" sounds:
- **Patch 3:** LFO1 → Cutoff (+10 to +20)
  - Slow filter sweep
- **Patch 4:** MIDI2 (Mod Wheel) → Cutoff (+50 to +100)
  - Performance control

### 4. Stereo Movement
**L/R Delay + Pan Modulation:**
- Delay Type: L/R Delay
- Patch 2: LFO2 → Pan (+20 to +40)

**Result:** Sound bounces between speakers with modulated panning

### 5. Noise as Analog "Grit"
Add subtle noise (15-30) to:
- Simulate tape hiss
- Add analog texture
- Fill out thin digital sounds
- Create vintage character

### 6. Low Resonance Philosophy
**BOC patches avoid high resonance:**
- Resonance: 0-30 range
- Smooth, natural filtering
- No resonant "screaming"
- Vintage synth limitation = aesthetic choice

### 7. Chorus for Detuning
**Chorus/Flanger is essential:**
- Speed: 15-30 (slow to medium)
- Depth: 20-50
- Creates subtle pitch wobble
- Thickens thin digital sounds
- Simulates analog drift

### 8. Long Envelope Tails
**Both EG1 and EG2 have long releases:**
- EG1 Release: 60-100
- EG2 Release: 100-127
- Sounds fade naturally
- Ambient character
- Notes overlap smoothly

---

## Parameter Reference

### Quick Value Ranges (BOC Style)

#### Effects
```
Delay Type: L/R Delay (77% of patches)
Delay Time: 35-45 (medium-short)
Delay Depth: 80-100 (high feedback)
Mod FX Type: Cho/Flg (72% of patches)
Mod Speed: 15-35 (slow to medium)
Mod Depth: 20-50
```

#### Oscillators
```
OSC1 Wave: Saw, Sine, DWGS, Triangle (in that order)
OSC1 Level: 110-127 (near max)
OSC2 Wave: Saw, Triangle (prefer Triangle for softness)
OSC2 Semitone: +7, +5, +12, -7 (intervals, not unison)
OSC2 Level: 85-105
Noise Level: 15-30
```

#### Filter
```
Type: 12dB LPF (52% of patches)
Cutoff: 45-65 (medium-open)
Resonance: 10-25 (low)
EG1 Intensity: 0 to +30
```

#### Envelopes
```
EG1: A=0-10, D=55-70, S=115-127, R=70-100
EG2: A=0-10, D=60-75, S=120-127, R=100-120
```

#### LFOs
```
LFO1: Triangle, Freq=10-20 (slow)
LFO2: Sine, Freq=60-75 (medium)
Key Sync: OFF
Tempo Sync: OFF
```

#### Modulation
```
Patch 1: LFO1 → Pitch (+7 to +12)
Patch 2: LFO2 → Pitch or Cutoff (+10 to +30)
Patch 3: LFO1 → Cutoff (+10 to +20)
Patch 4: MIDI2 → Cutoff (+50 to +100)
```

#### Voice Settings
```
Voice Mode: Single (100%)
Assign Mode: Poly
Portamento: 0 (no glide)
Distortion: OFF
```

---

## Key Takeaways

### DO:
✅ Use **L/R Delay** with high depth (80-100)
✅ Use **Chorus/Flanger** for wobbly detuning
✅ Use **12dB LPF** for gentle, warm filtering
✅ Keep **resonance LOW** (10-25)
✅ Use **Triangle** wave for LFO1, **Sine** for LFO2
✅ Modulate **pitch** with LFO1 for vibrato/wobble
✅ Use **perfect fifths** (+7 semitones) on OSC2
✅ Set long **release** times (80-120)
✅ Add subtle **noise** (15-30) for analog texture
✅ Max out **OSC1 level** (127)
✅ Use **Simple** voice mode (Single, Poly)

### DON'T:
❌ Don't use high **resonance** (BOC mean=19 vs factory=41)
❌ Don't use **Distortion** (almost never in BOC patches)
❌ Don't use **Portamento** (keep at 0)
❌ Don't use **24dB filter** as primary choice (prefer 12dB)
❌ Don't use **StereoDelay** or **CrossDelay** as first choice (prefer L/R)
❌ Don't use fast **LFO rates** on LFO1 (keep slow 8-20)
❌ Don't use **Square** or **Saw** on LFO2 (prefer Sine)
❌ Don't tune OSC2 to **unison** (use intervals like +5, +7, +12)
❌ Don't use short **releases** (keep 80+)

### The "BOC Formula":
1. **Sine or Saw** on OSC1, **Triangle** on OSC2
2. OSC2 tuned to **+7 semitones** (perfect fifth)
3. **12dB LPF** filter at cutoff **50-60**
4. **Low resonance** (15-25)
5. **Fast attack**, **medium decay**, **high sustain**, **long release**
6. **LFO1 Triangle** (slow) → **Pitch** (+8 to +12)
7. **LFO2 Sine** (medium) → **Cutoff** or **Pan**
8. **L/R Delay** (Time=40, Depth=85)
9. **Chorus/Flanger** (Speed=20, Depth=30)
10. Add subtle **noise** (20)

---

## Conclusion

The Boards of Canada sound on the MS2000 is characterized by:
- **Warm, lo-fi character** through chorus and filtering
- **Stereo movement** via L/R delay and pan modulation
- **Pitch wobble** from dual LFO pitch modulation
- **Gentle filtering** with 12dB LPF and low resonance
- **Interval-based detuning** (fifths, fourths, octaves)
- **Long, smooth envelopes** for ambient character
- **Minimal complexity** - simple oscillators, thoughtful modulation

By following these principles and using the specific parameter ranges identified in the BOC patch analysis, you can create authentic Boards of Canada-style sounds on your Korg MS2000.

**Remember:** The "secret" isn't exotic programming - it's restraint, careful effect use, and understanding that imperfection (detuning, wobble, low-fi processing) creates character.

---

*Analysis based on 123 Boards of Canada-style patches for Korg MS2000*
*Document created: 2025-01-19*
*For questions or additions, see the analysis data in `/analysis/boc_analysis_results.txt`*
