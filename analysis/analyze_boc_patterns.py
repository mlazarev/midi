#!/usr/bin/env python3
"""Analyze BOC patch patterns and characteristics."""

import json
from collections import Counter
import statistics
from pathlib import Path

# Get the directory where this script is located
script_dir = Path(__file__).parent

# Load both patch banks
with open(script_dir / 'boc_patches.json') as f:
    boc_patches = json.load(f)

with open(script_dir / 'original_patches.json') as f:
    original_patches = json.load(f)

def analyze_field(patches, field_path, label):
    """Analyze a specific field across patches."""
    values = []
    for p in patches:
        obj = p
        for key in field_path.split('.'):
            obj = obj.get(key, {})
            if not isinstance(obj, dict):
                values.append(obj)
                break

    if not values:
        return None

    # Check if all values are numeric
    numeric = all(isinstance(v, (int, float)) for v in values)

    if numeric:
        return {
            'label': label,
            'min': min(values),
            'max': max(values),
            'mean': round(statistics.mean(values), 1),
            'median': statistics.median(values),
            'stdev': round(statistics.stdev(values), 1) if len(values) > 1 else 0
        }
    else:
        counter = Counter(values)
        return {
            'label': label,
            'distribution': dict(counter.most_common())
        }

print("=" * 80)
print("BOARDS OF CANADA MS2000 PATCH ANALYSIS")
print("=" * 80)

print("\n### VOICE MODE ###")
boc_voice = analyze_field(boc_patches, 'voice_mode', 'Voice Mode')
orig_voice = analyze_field(original_patches, 'voice_mode', 'Voice Mode')
print("BOC:", boc_voice['distribution'])
print("ORIG:", orig_voice['distribution'])

print("\n### DELAY FX ###")
boc_delay_type = analyze_field(boc_patches, 'delay_type', 'Delay Type')
orig_delay_type = analyze_field(original_patches, 'delay_type', 'Delay Type')
print("BOC Delay Type:", boc_delay_type['distribution'])
print("ORIG Delay Type:", orig_delay_type['distribution'])

boc_delay_time = analyze_field(boc_patches, 'delay_time', 'Delay Time')
orig_delay_time = analyze_field(original_patches, 'delay_time', 'Delay Time')
print("BOC Delay Time:", boc_delay_time)
print("ORIG Delay Time:", orig_delay_time)

boc_delay_depth = analyze_field(boc_patches, 'delay_depth', 'Delay Depth')
orig_delay_depth = analyze_field(original_patches, 'delay_depth', 'Delay Depth')
print("BOC Delay Depth:", boc_delay_depth)
print("ORIG Delay Depth:", orig_delay_depth)

print("\n### MOD FX ###")
boc_mod_type = analyze_field(boc_patches, 'mod_type', 'Mod Type')
orig_mod_type = analyze_field(original_patches, 'mod_type', 'Mod Type')
print("BOC Mod Type:", boc_mod_type['distribution'])
print("ORIG Mod Type:", orig_mod_type['distribution'])

boc_mod_speed = analyze_field(boc_patches, 'mod_speed', 'Mod Speed')
orig_mod_speed = analyze_field(original_patches, 'mod_speed', 'Mod Speed')
print("BOC Mod Speed:", boc_mod_speed)
print("ORIG Mod Speed:", orig_mod_speed)

print("\n### OSC1 ###")
boc_osc1_wave = analyze_field(boc_patches, 'timbre1.osc1_wave', 'OSC1 Wave')
orig_osc1_wave = analyze_field(original_patches, 'timbre1.osc1_wave', 'OSC1 Wave')
print("BOC OSC1 Wave:", boc_osc1_wave['distribution'])
print("ORIG OSC1 Wave:", orig_osc1_wave['distribution'])

boc_osc1_level = analyze_field(boc_patches, 'timbre1.osc1_level', 'OSC1 Level')
orig_osc1_level = analyze_field(original_patches, 'timbre1.osc1_level', 'OSC1 Level')
print("BOC OSC1 Level:", boc_osc1_level)
print("ORIG OSC1 Level:", orig_osc1_level)

print("\n### OSC2 ###")
boc_osc2_wave = analyze_field(boc_patches, 'timbre1.osc2_wave', 'OSC2 Wave')
orig_osc2_wave = analyze_field(original_patches, 'timbre1.osc2_wave', 'OSC2 Wave')
print("BOC OSC2 Wave:", boc_osc2_wave['distribution'])
print("ORIG OSC2 Wave:", orig_osc2_wave['distribution'])

boc_osc2_mod = analyze_field(boc_patches, 'timbre1.osc2_mod', 'OSC2 Mod')
orig_osc2_mod = analyze_field(original_patches, 'timbre1.osc2_mod', 'OSC2 Mod')
print("BOC OSC2 Mod:", boc_osc2_mod['distribution'])
print("ORIG OSC2 Mod:", orig_osc2_mod['distribution'])

boc_osc2_semi = analyze_field(boc_patches, 'timbre1.osc2_semitone', 'OSC2 Semitone')
orig_osc2_semi = analyze_field(original_patches, 'timbre1.osc2_semitone', 'OSC2 Semitone')
print("BOC OSC2 Semitone:", boc_osc2_semi)
print("ORIG OSC2 Semitone:", orig_osc2_semi)

print("\n### FILTER ###")
boc_filter_type = analyze_field(boc_patches, 'timbre1.filter_type', 'Filter Type')
orig_filter_type = analyze_field(original_patches, 'timbre1.filter_type', 'Filter Type')
print("BOC Filter Type:", boc_filter_type['distribution'])
print("ORIG Filter Type:", orig_filter_type['distribution'])

boc_cutoff = analyze_field(boc_patches, 'timbre1.cutoff', 'Cutoff')
orig_cutoff = analyze_field(original_patches, 'timbre1.cutoff', 'Cutoff')
print("BOC Cutoff:", boc_cutoff)
print("ORIG Cutoff:", orig_cutoff)

boc_reso = analyze_field(boc_patches, 'timbre1.resonance', 'Resonance')
orig_reso = analyze_field(original_patches, 'timbre1.resonance', 'Resonance')
print("BOC Resonance:", boc_reso)
print("ORIG Resonance:", orig_reso)

print("\n### ENVELOPES ###")
print("BOC EG1 (Filter):")
print("  Attack:", analyze_field(boc_patches, 'timbre1.eg1_attack', 'EG1 Attack'))
print("  Decay:", analyze_field(boc_patches, 'timbre1.eg1_decay', 'EG1 Decay'))
print("  Sustain:", analyze_field(boc_patches, 'timbre1.eg1_sustain', 'EG1 Sustain'))
print("  Release:", analyze_field(boc_patches, 'timbre1.eg1_release', 'EG1 Release'))

print("\nBOC EG2 (Amp):")
print("  Attack:", analyze_field(boc_patches, 'timbre1.eg2_attack', 'EG2 Attack'))
print("  Decay:", analyze_field(boc_patches, 'timbre1.eg2_decay', 'EG2 Decay'))
print("  Sustain:", analyze_field(boc_patches, 'timbre1.eg2_sustain', 'EG2 Sustain'))
print("  Release:", analyze_field(boc_patches, 'timbre1.eg2_release', 'EG2 Release'))

print("\n### LFOs ###")
boc_lfo1_wave = analyze_field(boc_patches, 'timbre1.lfo1_wave', 'LFO1 Wave')
print("BOC LFO1 Wave:", boc_lfo1_wave['distribution'])

boc_lfo2_wave = analyze_field(boc_patches, 'timbre1.lfo2_wave', 'LFO2 Wave')
print("BOC LFO2 Wave:", boc_lfo2_wave['distribution'])

boc_lfo1_freq = analyze_field(boc_patches, 'timbre1.lfo1_freq', 'LFO1 Freq')
print("BOC LFO1 Frequency:", boc_lfo1_freq)

boc_lfo2_freq = analyze_field(boc_patches, 'timbre1.lfo2_freq', 'LFO2 Freq')
print("BOC LFO2 Frequency:", boc_lfo2_freq)

print("\n### MODULATION MATRIX (PATCHES) ###")
print("BOC Patch Sources:")
for i in range(1, 5):
    field = f'timbre1.patch{i}_src'
    dist = analyze_field(boc_patches, field, f'Patch{i} Source')
    print(f"  Patch{i}:", dist['distribution'])

print("\nBOC Patch Destinations:")
for i in range(1, 5):
    field = f'timbre1.patch{i}_dest'
    dist = analyze_field(boc_patches, field, f'Patch{i} Dest')
    print(f"  Patch{i}:", dist['distribution'])

print("\n### ARPEGGIATOR ###")
boc_arp_on = sum(1 for p in boc_patches if p.get('arp_on'))
orig_arp_on = sum(1 for p in original_patches if p.get('arp_on'))
print(f"BOC: Arp ON in {boc_arp_on}/{len(boc_patches)} patches ({100*boc_arp_on/len(boc_patches):.1f}%)")
print(f"ORIG: Arp ON in {orig_arp_on}/{len(original_patches)} patches ({100*orig_arp_on/len(original_patches):.1f}%)")

print("\n### PORTAMENTO ###")
boc_port = analyze_field(boc_patches, 'timbre1.portamento', 'Portamento')
orig_port = analyze_field(original_patches, 'timbre1.portamento', 'Portamento')
print("BOC Portamento:", boc_port)
print("ORIG Portamento:", orig_port)

print("\n### DISTORTION ###")
boc_dist = sum(1 for p in boc_patches if p.get('timbre1', {}).get('distortion'))
orig_dist = sum(1 for p in original_patches if p.get('timbre1', {}).get('distortion'))
print(f"BOC: Distortion ON in {boc_dist}/{len(boc_patches)} patches")
print(f"ORIG: Distortion ON in {orig_dist}/{len(original_patches)} patches")

print("\n" + "=" * 80)
print("KEY FINDINGS:")
print("=" * 80)

# Calculate key differences
findings = []

# Delay
if boc_delay_type['distribution'].get('L/R Delay', 0) > 100:
    findings.append("• HEAVY use of L/R Delay (ping-pong stereo delay)")

# Mod FX
cho_pct = 100 * boc_mod_type['distribution'].get('Cho/Flg', 0) / len(boc_patches)
if cho_pct > 50:
    findings.append(f"• Chorus/Flanger used in {cho_pct:.0f}% of patches (detuned/wobbly sound)")

# OSC1
dwgs_count = boc_osc1_wave['distribution'].get('DWGS', 0)
if dwgs_count > 20:
    findings.append(f"• {dwgs_count} patches use DWGS waveforms (digital wavetables)")

# Filter Cutoff
if boc_cutoff['mean'] < 50:
    findings.append(f"• Low average filter cutoff ({boc_cutoff['mean']}) = darker, muffled tones")

# LFO
sine_count = boc_lfo2_wave['distribution'].get('Sine', 0)
if sine_count > 50:
    findings.append(f"• LFO2 frequently uses Sine wave ({sine_count} patches) for smooth modulation")

for finding in findings:
    print(finding)

print("\n")
