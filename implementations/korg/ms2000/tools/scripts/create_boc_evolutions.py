#!/usr/bin/env python3
"""
Create BOC-style evolutions of factory patches.
Based on "How to Make Boards of Canada Sounds on the Korg MS2000" guide.
"""

import json
import random
from pathlib import Path
from typing import Dict, Any, List

# BOC-specific parameter ranges from the guide
BOC_PARAMS = {
    # Effects (critical!)
    'delay_type': 'L/R Delay',  # 77% of BOC patches
    'delay_time': (35, 45),
    'delay_depth': (80, 100),
    'mod_type': 'Cho/Flg',  # 72% of BOC patches
    'mod_speed': (15, 35),
    'mod_depth': (20, 50),

    # Oscillators
    'osc1_waves': ['Saw', 'Sine', 'DWGS', 'Triangle'],
    'osc2_waves': ['Saw', 'Triangle'],  # Prefer Triangle
    'osc2_semitones': [+5, +7, +12, +19, -7, -12],  # Intervals, not unison!
    'noise_level': (15, 30),

    # Filter
    'filter_type': '12dB LPF',  # 52% of BOC patches
    'cutoff': (45, 65),
    'resonance': (10, 25),  # LOW resonance is key
    'filter_eg1_int': (0, 30),

    # Envelopes
    'eg1': {'attack': (0, 10), 'decay': (55, 70), 'sustain': (115, 127), 'release': (70, 100)},
    'eg2': {'attack': (0, 10), 'decay': (60, 75), 'sustain': (120, 127), 'release': (100, 120)},

    # LFOs
    'lfo1_wave': 'Triangle',  # 89% of BOC patches
    'lfo1_freq': (10, 20),  # Slow
    'lfo2_wave': 'Sine',  # 83% of BOC patches
    'lfo2_freq': (60, 75),  # Medium

    # Modulation routing (all intensities must be -64 to +63!)
    'patch1': ('LFO1', 'PITCH', (7, 12)),  # Vibrato is KEY
    'patch2': ('LFO2', ['PITCH', 'CUTOFF'], (10, 30)),
    'patch3': ('LFO1', 'CUTOFF', (10, 20)),
    'patch4': ('MIDI2', 'CUTOFF', (40, 63)),  # Max is +63 for offset-64
}

def random_choice(choices: List) -> Any:
    """Random choice from list."""
    return random.choice(choices)

def random_int(min_val: int, max_val: int) -> int:
    """Random integer in range."""
    return random.randint(min_val, max_val)

def apply_boc_transform(patch: Dict[str, Any], index: int) -> Dict[str, Any]:
    """
    Apply dramatic BOC-style transformation to a patch.

    Based on the guide's core principles:
    - L/R Delay with high depth
    - Chorus/Flanger for wobble
    - 12dB LPF with low resonance
    - OSC2 detuned to intervals (fifths, fourths)
    - Triangle LFO1 → Pitch for vibrato
    - Sine LFO2 → Cutoff/Pan
    - Long release times
    - Subtle noise
    """

    # Work on a copy
    evolved = patch.copy()

    # Update name with BOC-style prefix
    boc_prefixes = ['Amber', 'Azure', 'Cerulean', 'Crimson', 'Dusk', 'Indigo',
                    'Lunar', 'Rust', 'Violet', 'Emerald', 'Golden', 'Silver']
    boc_suffixes = ['Aurora', 'Cascade', 'Circuit', 'Drift', 'Echo', 'Horizon',
                    'Lattice', 'Memory', 'Pulse', 'Shimmer', 'Waves', 'Dream']

    prefix = random_choice(boc_prefixes)
    suffix = random_choice(boc_suffixes)
    evolved['name'] = f"{prefix} {suffix}"

    # VOICE: Always Single (100% of BOC patches)
    evolved['voice_mode'] = 'Single'
    evolved['voice'] = {'portamento_time': 0}  # NO portamento

    # EFFECTS: Critical BOC sound
    evolved['effects'] = {
        'delay': {
            'type': BOC_PARAMS['delay_type'],
            'sync': False,
            'timebase': random_int(0, 15),
            'time': random_int(*BOC_PARAMS['delay_time']),
            'depth': random_int(*BOC_PARAMS['delay_depth'])
        },
        'mod': {
            'type': BOC_PARAMS['mod_type'],
            'speed': random_int(*BOC_PARAMS['mod_speed']),
            'depth': random_int(*BOC_PARAMS['mod_depth'])
        },
        'eq': {
            'hi_freq': random_int(18, 22),
            'hi_gain': random_int(0, 3),
            'lo_freq': random_int(14, 16),
            'lo_gain': random_int(-5, 0)
        }
    }

    # Transform timbre1 (main timbre)
    timbre1 = evolved.get('timbre1', {})

    # OSCILLATORS
    osc1 = timbre1.get('osc1', {})
    osc1['wave'] = random_choice(BOC_PARAMS['osc1_waves'])
    osc1['wave_value'] = {'Saw': 0, 'Pulse': 1, 'Triangle': 2, 'Sine': 3,
                          'Vox Wave': 4, 'DWGS': 5, 'Noise': 6, 'Audio In': 7}.get(osc1['wave'], 0)

    # If DWGS, set a random wavetable
    if osc1['wave'] == 'DWGS':
        osc1['dwgs_wave'] = random_int(1, 64)

    osc2 = timbre1.get('osc2', {})
    # Triangle wave preferred for softness (46% of BOC patches)
    osc2['wave'] = 'Triangle' if random.random() < 0.6 else 'Saw'
    osc2['wave_value'] = {'Saw': 0, 'Square': 1, 'Triangle': 2}.get(osc2['wave'], 0)

    # Detuning to intervals (fifths, fourths) - NOT unison!
    osc2['semitone'] = random_choice(BOC_PARAMS['osc2_semitones'])
    osc2['tune'] = random_int(-10, 10)  # Fine tune for thickness

    # Modulation: Ring mod for bell tones (15% chance)
    if random.random() < 0.15:
        osc2['modulation'] = random_choice(['Ring', 'Ring+Sync'])
        osc2['mod_value'] = {'Off': 0, 'Ring': 1, 'Sync': 2, 'Ring+Sync': 3}.get(osc2['modulation'], 0)
    else:
        osc2['modulation'] = 'Off'
        osc2['mod_value'] = 0

    timbre1['osc1'] = osc1
    timbre1['osc2'] = osc2

    # MIXER
    mixer = timbre1.get('mixer', {})
    mixer['osc1_level'] = 127  # Max out OSC1
    mixer['osc2_level'] = random_int(85, 105)
    mixer['noise_level'] = random_int(*BOC_PARAMS['noise_level'])  # Subtle noise for analog texture
    timbre1['mixer'] = mixer

    # FILTER: 12dB LPF with LOW resonance
    filt = timbre1.get('filter', {})
    filt['type'] = BOC_PARAMS['filter_type']
    filt['type_value'] = 1  # 12dB LPF
    filt['cutoff'] = random_int(*BOC_PARAMS['cutoff'])
    filt['resonance'] = random_int(*BOC_PARAMS['resonance'])  # LOW resonance is critical!
    filt['eg1_intensity'] = random_int(*BOC_PARAMS['filter_eg1_int'])
    filt['velocity_sense'] = random_int(-10, 10)
    filt['kbd_track'] = random_int(-10, 10)
    timbre1['filter'] = filt

    # AMP
    amp = timbre1.get('amp', {})
    amp['level'] = 127
    amp['panpot'] = random_int(-20, 20)
    amp['switch'] = 'EG2'
    amp['distortion'] = False  # NO distortion (0.8% in BOC patches)
    amp['velocity_sense'] = random_int(0, 20)
    amp['kbd_track'] = random_int(-10, 10)
    timbre1['amp'] = amp

    # ENVELOPES: Fast attack, medium decay, high sustain, LONG release
    eg1 = timbre1.get('eg1', {})
    eg1['attack'] = random_int(*BOC_PARAMS['eg1']['attack'])
    eg1['decay'] = random_int(*BOC_PARAMS['eg1']['decay'])
    eg1['sustain'] = random_int(*BOC_PARAMS['eg1']['sustain'])
    eg1['release'] = random_int(*BOC_PARAMS['eg1']['release'])
    timbre1['eg1'] = eg1

    eg2 = timbre1.get('eg2', {})
    eg2['attack'] = random_int(*BOC_PARAMS['eg2']['attack'])
    eg2['decay'] = random_int(*BOC_PARAMS['eg2']['decay'])
    eg2['sustain'] = random_int(*BOC_PARAMS['eg2']['sustain'])
    eg2['release'] = random_int(*BOC_PARAMS['eg2']['release'])  # Long release
    timbre1['eg2'] = eg2

    # LFOs: Triangle LFO1 (slow), Sine LFO2 (medium)
    lfo1 = timbre1.get('lfo1', {})
    lfo1['wave'] = BOC_PARAMS['lfo1_wave']
    lfo1['wave_value'] = 2  # Triangle
    lfo1['frequency'] = random_int(*BOC_PARAMS['lfo1_freq'])
    lfo1['tempo_sync'] = False
    lfo1['tempo_value'] = 0
    timbre1['lfo1'] = lfo1

    lfo2 = timbre1.get('lfo2', {})
    lfo2['wave'] = BOC_PARAMS['lfo2_wave']
    lfo2['wave_value'] = 2  # Sine
    lfo2['frequency'] = random_int(*BOC_PARAMS['lfo2_freq'])
    lfo2['tempo_sync'] = False
    lfo2['tempo_value'] = 0
    timbre1['lfo2'] = lfo2

    # MODULATION MATRIX: Critical for BOC character
    patch_routes = timbre1.get('patch', {})

    # Patch 1: LFO1 → Pitch (vibrato/wobble) - ESSENTIAL
    patch_routes['patch1'] = {
        'source': 'LFO1',
        'destination': 'PITCH',
        'intensity': random_int(*BOC_PARAMS['patch1'][2])
    }

    # Patch 2: LFO2 → Pitch or Cutoff
    dest2 = random_choice(['PITCH', 'CUTOFF'])
    patch_routes['patch2'] = {
        'source': 'LFO2',
        'destination': dest2,
        'intensity': random_int(*BOC_PARAMS['patch2'][2])
    }

    # Patch 3: LFO1 → Cutoff (filter breathing)
    patch_routes['patch3'] = {
        'source': 'LFO1',
        'destination': 'CUTOFF',
        'intensity': random_int(*BOC_PARAMS['patch3'][2])
    }

    # Patch 4: MIDI2 (Mod Wheel) → Cutoff (performance control)
    patch_routes['patch4'] = {
        'source': 'MIDI2',
        'destination': 'CUTOFF',
        'intensity': random_int(*BOC_PARAMS['patch4'][2])
    }

    timbre1['patch'] = patch_routes
    evolved['timbre1'] = timbre1

    # No timbre2 for Single mode
    if 'timbre2' in evolved:
        del evolved['timbre2']

    # ARPEGGIATOR: Minimal use (15.4% of BOC patches)
    arp = evolved.get('arpeggiator', {})
    if random.random() < 0.15:  # 15% chance
        arp['on'] = True
        arp['type'] = random_choice(['Up', 'Down', 'Alt1'])
        arp['tempo'] = random_int(75, 95)
        arp['gate'] = random_int(75, 85)
    else:
        arp['on'] = False
    evolved['arpeggiator'] = arp

    # Update metadata
    evolved['index'] = index
    evolved['slot'] = f"{chr(65 + index // 16)}{(index % 16) + 1:02d}"

    return evolved


def main():
    # Load the correctly decoded factory_banks.json
    input_path = Path('../examples/factory_banks.json')
    output_json_path = Path('../examples/factory_evolutions.json')

    print("Loading factory patches...")
    with open(input_path, 'r') as f:
        factory_patches = json.load(f)

    print(f"Loaded {len(factory_patches)} factory patches")

    # Apply BOC transformations
    print("\nApplying BOC-style transformations...")
    print("Based on: 'How to Make Boards of Canada Sounds on the Korg MS2000'")
    print("\nKey transformations:")
    print("  - L/R Delay with high depth (80-100)")
    print("  - Chorus/Flanger for wobble")
    print("  - 12dB LPF with LOW resonance (10-25)")
    print("  - OSC2 detuned to intervals (+5, +7, +12 semitones)")
    print("  - LFO1 Triangle → Pitch for vibrato")
    print("  - LFO2 Sine → Cutoff/Pan")
    print("  - Long release times (100-120)")
    print("  - Subtle noise (15-30) for analog texture")
    print("  - NO portamento, NO distortion")
    print()

    evolved_patches = []
    for i, patch in enumerate(factory_patches):
        evolved = apply_boc_transform(patch, i)
        evolved_patches.append(evolved)
        if (i + 1) % 16 == 0:
            print(f"  Transformed bank {chr(65 + i // 16)} ({i + 1}/128)")

    # Save to JSON
    print(f"\nWriting evolved patches to {output_json_path}...")
    with open(output_json_path, 'w') as f:
        json.dump(evolved_patches, f, indent=2)

    print(f"✓ Created {len(evolved_patches)} BOC-style evolved patches")
    print(f"\nNext step: Encode to .syx file")


if __name__ == '__main__':
    main()
