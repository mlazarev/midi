#!/usr/bin/env python3
"""
Create original BOC-style patches from scratch.
Based on "How to Make Boards of Canada Sounds on the Korg MS2000" guide.

This generates 128 completely new patches using the 5 recipe archetypes:
1. Classic BOC Pad
2. Detuned BOC Lead
3. DWGS Texture Patch
4. Ring Mod Bell Tone
5. Arpeggiator Sequence
"""

import json
import random
from pathlib import Path
from typing import Dict, Any, List

# BOC-style patch names
PREFIXES = [
    'Amber', 'Azure', 'Cerulean', 'Crimson', 'Dusk', 'Indigo',
    'Lunar', 'Rust', 'Violet', 'Emerald', 'Golden', 'Silver',
    'Ochre', 'Slate', 'Twilight', 'Dawn', 'Copper', 'Bronze',
    'Misty', 'Hazy', 'Faded', 'Worn', 'Aged', 'Vintage'
]

SUFFIXES = [
    'Aurora', 'Cascade', 'Circuit', 'Drift', 'Echo', 'Horizon',
    'Lattice', 'Memory', 'Pulse', 'Shimmer', 'Waves', 'Dream',
    'Vision', 'Shadow', 'Glow', 'Mist', 'Haze', 'Flow',
    'Pattern', 'Field', 'Tape', 'Ghost', 'Whisper', 'Swell'
]

def rand_int(min_val: int, max_val: int) -> int:
    """Random integer in range."""
    return random.randint(min_val, max_val)

def rand_choice(choices: List) -> Any:
    """Random choice from list."""
    return random.choice(choices)

def create_base_patch(index: int, name: str) -> Dict[str, Any]:
    """Create base patch structure with common BOC settings."""
    slot = f"{chr(65 + index // 16)}{(index % 16) + 1:02d}"

    return {
        'name': name,
        'index': index,
        'slot': slot,
        'voice_mode': 'Single',  # 100% BOC

        'scale': {
            'key': 'C',
            'type': 0  # Major scale
        },

        'voice': {
            'portamento_time': 0  # NO portamento in BOC
        },

        # Effects are CRITICAL for BOC sound
        'effects': {
            'delay': {
                'type': 'L/R Delay',  # 77% of BOC patches
                'sync': False,
                'timebase': rand_int(0, 15),
                'time': rand_int(35, 45),
                'depth': rand_int(80, 100)
            },
            'mod': {
                'type': 'Cho/Flg',  # 72% of BOC patches
                'speed': rand_int(15, 35),
                'depth': rand_int(20, 50)
            },
            'eq': {
                'hi_freq': rand_int(18, 22),
                'hi_gain': rand_int(0, 3),
                'lo_freq': rand_int(14, 16),
                'lo_gain': rand_int(-5, 0)
            }
        },

        # Minimal arpeggiator use
        'arpeggiator': {
            'on': False,
            'latch': False,
            'target': 0,
            'keysync': False,
            'type': 'Up',
            'range': 1,
            'tempo': 120
        },

        'system': {
            'timbre_voice': 0,
            'split_point': 60
        }
    }

def create_classic_pad(index: int) -> Dict[str, Any]:
    """
    Recipe 1: Classic BOC Pad
    - Sine/Triangle oscillators
    - Perfect fifth interval
    - Slow vibrato
    - Long release
    """
    name = f"{rand_choice(PREFIXES)} {rand_choice(SUFFIXES)}"
    patch = create_base_patch(index, name)

    # OSC1: Sine or Triangle for mellow tone
    osc1_wave = rand_choice(['Sine', 'Triangle'])
    osc1_wave_val = {'Saw': 0, 'Pulse': 1, 'Triangle': 2, 'Sine': 3,
                     'Vox Wave': 4, 'DWGS': 5, 'Noise': 6, 'Audio In': 7}[osc1_wave]

    # OSC2: Triangle for softness
    osc2_semitone = rand_choice([+7, +5, +12])  # Fifths, fourths, octaves

    patch['timbre1'] = {
        'voice': {'portamento_time': 0},

        'osc1': {
            'wave': osc1_wave,
            'wave_value': osc1_wave_val,
            'ctrl1': rand_int(0, 30),
            'ctrl2': 0,
            'dwgs_wave': 1
        },

        'osc2': {
            'wave': 'Triangle',
            'wave_value': 2,
            'modulation': 'Off',
            'mod_value': 0,
            'semitone': osc2_semitone,
            'tune': rand_int(-5, 5)
        },

        'mixer': {
            'osc1_level': 127,
            'osc2_level': rand_int(90, 100),
            'noise_level': rand_int(15, 25)
        },

        'filter': {
            'type': '12dB LPF',
            'type_value': 1,
            'cutoff': rand_int(50, 60),
            'resonance': rand_int(15, 25),
            'eg1_intensity': rand_int(0, 10),
            'velocity_sense': 0,
            'kbd_track': 0
        },

        'amp': {
            'level': 127,
            'panpot': 0,
            'switch': 'EG2',
            'distortion': False,
            'kbd_track': 0,
            'velocity_sense': rand_int(0, 10)
        },

        'eg1': {
            'attack': rand_int(0, 10),
            'decay': rand_int(60, 70),
            'sustain': rand_int(120, 127),
            'release': rand_int(80, 100)
        },

        'eg2': {
            'attack': rand_int(0, 5),
            'decay': rand_int(60, 75),
            'sustain': 127,
            'release': rand_int(100, 120)
        },

        'lfo1': {
            'wave': 'Triangle',
            'wave_value': 2,
            'frequency': rand_int(10, 15),
            'tempo_sync': False,
            'tempo_value': 0
        },

        'lfo2': {
            'wave': 'Sine',
            'wave_value': 2,
            'frequency': rand_int(65, 75),
            'tempo_sync': False,
            'tempo_value': 0
        },

        'patch': {
            'patch1': {
                'source': 'LFO1',
                'destination': 'PITCH',
                'intensity': rand_int(7, 10)
            },
            'patch2': {
                'source': 'LFO2',
                'destination': rand_choice(['PITCH', 'CUTOFF']),
                'intensity': rand_int(20, 30)
            },
            'patch3': {
                'source': 'LFO1',
                'destination': 'CUTOFF',
                'intensity': rand_int(5, 15)
            },
            'patch4': {
                'source': 'MIDI2',
                'destination': 'CUTOFF',
                'intensity': rand_int(50, 63)
            }
        }
    }

    return patch

def create_detuned_lead(index: int) -> Dict[str, Any]:
    """
    Recipe 2: Detuned BOC Lead
    - Saw waves
    - Detuned intervals
    - More filter movement
    """
    name = f"{rand_choice(PREFIXES)} {rand_choice(SUFFIXES)}"
    patch = create_base_patch(index, name)

    # Both saws for classic analog sound
    osc2_semitone = rand_choice([+7, -7, +5])

    patch['timbre1'] = {
        'voice': {'portamento_time': 0},

        'osc1': {
            'wave': 'Saw',
            'wave_value': 0,
            'ctrl1': rand_int(50, 70),
            'ctrl2': 0,
            'dwgs_wave': 1
        },

        'osc2': {
            'wave': 'Saw',
            'wave_value': 0,
            'modulation': 'Off',
            'mod_value': 0,
            'semitone': osc2_semitone,
            'tune': rand_int(5, 10)  # Slight detune for thickness
        },

        'mixer': {
            'osc1_level': 127,
            'osc2_level': rand_int(100, 110),
            'noise_level': rand_int(18, 28)
        },

        'filter': {
            'type': '12dB LPF',
            'type_value': 1,
            'cutoff': rand_int(55, 65),
            'resonance': rand_int(10, 20),
            'eg1_intensity': rand_int(15, 25),
            'velocity_sense': rand_int(5, 15),
            'kbd_track': rand_int(0, 10)
        },

        'amp': {
            'level': 127,
            'panpot': 0,
            'switch': 'EG2',
            'distortion': False,
            'kbd_track': 0,
            'velocity_sense': rand_int(10, 20)
        },

        'eg1': {
            'attack': 0,
            'decay': rand_int(55, 65),
            'sustain': rand_int(100, 120),
            'release': rand_int(60, 80)
        },

        'eg2': {
            'attack': 0,
            'decay': rand_int(50, 60),
            'sustain': rand_int(110, 127),
            'release': rand_int(70, 90)
        },

        'lfo1': {
            'wave': 'Triangle',
            'wave_value': 2,
            'frequency': rand_int(8, 12),
            'tempo_sync': False,
            'tempo_value': 0
        },

        'lfo2': {
            'wave': 'Sine',
            'wave_value': 2,
            'frequency': rand_int(60, 70),
            'tempo_sync': False,
            'tempo_value': 0
        },

        'patch': {
            'patch1': {
                'source': 'LFO1',
                'destination': 'PITCH',
                'intensity': rand_int(8, 12)
            },
            'patch2': {
                'source': 'LFO2',
                'destination': 'CUTOFF',
                'intensity': rand_int(10, 20)
            },
            'patch3': {
                'source': 'LFO1',
                'destination': 'OSC2PITCH',
                'intensity': rand_int(-15, -10)
            },
            'patch4': {
                'source': 'MIDI2',
                'destination': 'CUTOFF',
                'intensity': rand_int(60, 63)
            }
        }
    }

    return patch

def create_dwgs_texture(index: int) -> Dict[str, Any]:
    """
    Recipe 3: DWGS Texture Patch
    - DWGS wavetables for complex tones
    - Ring mod occasionally
    - More experimental
    """
    name = f"{rand_choice(PREFIXES)} {rand_choice(SUFFIXES)}"
    patch = create_base_patch(index, name)

    # Use ring mod 15% of the time
    use_ring = random.random() < 0.15
    osc2_mod = rand_choice(['Ring', 'Ring+Sync']) if use_ring else 'Off'
    osc2_mod_val = {'Off': 0, 'Ring': 1, 'Sync': 2, 'Ring+Sync': 3}[osc2_mod]

    osc2_semitone = rand_choice([+12, +19, +7]) if not use_ring else 0

    patch['timbre1'] = {
        'voice': {'portamento_time': 0},

        'osc1': {
            'wave': 'DWGS',
            'wave_value': 5,
            'ctrl1': 0,
            'ctrl2': 0,
            'dwgs_wave': rand_int(10, 50)
        },

        'osc2': {
            'wave': 'Triangle',
            'wave_value': 2,
            'modulation': osc2_mod,
            'mod_value': osc2_mod_val,
            'semitone': osc2_semitone,
            'tune': 0
        },

        'mixer': {
            'osc1_level': 127,
            'osc2_level': rand_int(80, 100),
            'noise_level': rand_int(20, 30)
        },

        'filter': {
            'type': rand_choice(['12dB LPF', '24dB LPF']),
            'type_value': rand_int(0, 1),
            'cutoff': rand_int(45, 60),
            'resonance': rand_int(20, 35),
            'eg1_intensity': rand_int(20, 35),
            'velocity_sense': rand_int(5, 15),
            'kbd_track': rand_int(0, 10)
        },

        'amp': {
            'level': 127,
            'panpot': 0,
            'switch': 'EG2',
            'distortion': False,
            'kbd_track': 0,
            'velocity_sense': rand_int(5, 15)
        },

        'eg1': {
            'attack': rand_int(5, 15),
            'decay': rand_int(50, 70),
            'sustain': rand_int(110, 127),
            'release': rand_int(80, 110)
        },

        'eg2': {
            'attack': rand_int(0, 10),
            'decay': rand_int(60, 80),
            'sustain': rand_int(115, 127),
            'release': rand_int(90, 120)
        },

        'lfo1': {
            'wave': 'Triangle',
            'wave_value': 2,
            'frequency': rand_int(30, 50),
            'tempo_sync': False,
            'tempo_value': 0
        },

        'lfo2': {
            'wave': rand_choice(['Sine', 'S/H']),
            'wave_value': 2 if random.random() < 0.8 else 3,
            'frequency': rand_int(100, 130) if random.random() < 0.3 else rand_int(60, 80),
            'tempo_sync': False,
            'tempo_value': 0
        },

        'patch': {
            'patch1': {
                'source': 'LFO2',
                'destination': 'CUTOFF',
                'intensity': rand_int(5, 10)
            },
            'patch2': {
                'source': 'EG1',
                'destination': 'PITCH',
                'intensity': rand_int(10, 15)
            },
            'patch3': {
                'source': 'LFO2',
                'destination': 'PITCH',
                'intensity': rand_int(8, 12)
            },
            'patch4': {
                'source': 'MIDI2',
                'destination': 'CUTOFF',
                'intensity': rand_int(40, 60)
            }
        }
    }

    # Sometimes use Phaser instead of Chorus
    if random.random() < 0.2:
        patch['effects']['mod']['type'] = 'Phaser'
        patch['effects']['mod']['speed'] = rand_int(20, 30)
        patch['effects']['mod']['depth'] = rand_int(0, 20)

    return patch

def create_bell_tone(index: int) -> Dict[str, Any]:
    """
    Recipe 4: Ring Mod Bell Tone
    - Ring modulation
    - Slow swell attack
    - Metallic character
    """
    name = f"{rand_choice(PREFIXES)} {rand_choice(SUFFIXES)}"
    patch = create_base_patch(index, name)

    patch['timbre1'] = {
        'voice': {'portamento_time': 0},

        'osc1': {
            'wave': rand_choice(['Triangle', 'Sine']),
            'wave_value': rand_int(2, 3),
            'ctrl1': 0,
            'ctrl2': 0,
            'dwgs_wave': 1
        },

        'osc2': {
            'wave': 'Square',
            'wave_value': 1,
            'modulation': rand_choice(['Ring', 'Ring+Sync']),
            'mod_value': rand_int(1, 3),
            'semitone': 0,  # Unison for max ring effect
            'tune': 0
        },

        'mixer': {
            'osc1_level': 108,
            'osc2_level': 127,
            'noise_level': rand_int(15, 25)
        },

        'filter': {
            'type': '24dB LPF',
            'type_value': 0,
            'cutoff': rand_int(30, 40),
            'resonance': rand_int(0, 10),
            'eg1_intensity': rand_int(15, 25),
            'velocity_sense': rand_int(5, 15),
            'kbd_track': 0
        },

        'amp': {
            'level': 127,
            'panpot': 0,
            'switch': 'EG2',
            'distortion': False,
            'kbd_track': 0,
            'velocity_sense': rand_int(10, 20)
        },

        'eg1': {
            'attack': rand_int(5, 15),
            'decay': rand_int(25, 35),
            'sustain': rand_int(95, 105),
            'release': rand_int(120, 127)
        },

        'eg2': {
            'attack': rand_int(100, 120),  # Slow swell
            'decay': rand_int(90, 100),
            'sustain': rand_int(100, 105),
            'release': rand_int(115, 125)
        },

        'lfo1': {
            'wave': 'Triangle',
            'wave_value': 2,
            'frequency': rand_int(35, 45),
            'tempo_sync': False,
            'tempo_value': 0
        },

        'lfo2': {
            'wave': 'Sine',
            'wave_value': 2,
            'frequency': 70,
            'tempo_sync': False,
            'tempo_value': 0
        },

        'patch': {
            'patch1': {
                'source': 'LFO1',
                'destination': 'OSC2PITCH',
                'intensity': rand_int(-15, -10)
            },
            'patch2': {
                'source': 'LFO2',
                'destination': 'CUTOFF',
                'intensity': rand_int(20, 30)
            },
            'patch3': {
                'source': 'LFO2',
                'destination': 'PITCH',
                'intensity': rand_int(30, 45)
            },
            'patch4': {
                'source': 'MIDI2',
                'destination': 'CUTOFF',
                'intensity': rand_int(5, 15)
            }
        }
    }

    return patch

def create_arp_sequence(index: int) -> Dict[str, Any]:
    """
    Recipe 5: Arpeggiator Sequence
    - Arpeggiator ON
    - Simple melodic pattern
    - DWGS or Saw
    """
    name = f"{rand_choice(PREFIXES)} {rand_choice(SUFFIXES)}"
    patch = create_base_patch(index, name)

    # Enable arpeggiator
    patch['arpeggiator']['on'] = True
    patch['arpeggiator']['type'] = rand_choice(['Up', 'Down', 'Alt1'])
    patch['arpeggiator']['range'] = rand_int(1, 2)
    patch['arpeggiator']['tempo'] = rand_int(75, 95)

    osc1_wave = rand_choice(['DWGS', 'Saw'])
    osc1_wave_val = 5 if osc1_wave == 'DWGS' else 0

    patch['timbre1'] = {
        'voice': {'portamento_time': 0},

        'osc1': {
            'wave': osc1_wave,
            'wave_value': osc1_wave_val,
            'ctrl1': 0,
            'ctrl2': 0,
            'dwgs_wave': rand_int(15, 45) if osc1_wave == 'DWGS' else 1
        },

        'osc2': {
            'wave': rand_choice(['Saw', 'Triangle']),
            'wave_value': rand_int(0, 2),
            'modulation': 'Off',
            'mod_value': 0,
            'semitone': rand_choice([+5, +7]),
            'tune': 0
        },

        'mixer': {
            'osc1_level': 127,
            'osc2_level': rand_int(90, 100),
            'noise_level': rand_int(10, 20)
        },

        'filter': {
            'type': '12dB LPF',
            'type_value': 1,
            'cutoff': rand_int(40, 50),
            'resonance': rand_int(15, 25),
            'eg1_intensity': rand_int(10, 20),
            'velocity_sense': rand_int(10, 20),
            'kbd_track': rand_int(5, 15)
        },

        'amp': {
            'level': 127,
            'panpot': 0,
            'switch': 'EG2',
            'distortion': False,
            'kbd_track': 0,
            'velocity_sense': rand_int(15, 25)
        },

        'eg1': {
            'attack': 0,
            'decay': rand_int(40, 55),
            'sustain': rand_int(90, 110),
            'release': rand_int(50, 70)
        },

        'eg2': {
            'attack': 0,
            'decay': rand_int(45, 60),
            'sustain': rand_int(95, 120),
            'release': rand_int(60, 80)
        },

        'lfo1': {
            'wave': 'Triangle',
            'wave_value': 2,
            'frequency': rand_int(12, 18),
            'tempo_sync': False,
            'tempo_value': 0
        },

        'lfo2': {
            'wave': 'Sine',
            'wave_value': 2,
            'frequency': rand_int(140, 160),
            'tempo_sync': False,
            'tempo_value': 0
        },

        'patch': {
            'patch1': {
                'source': 'LFO1',
                'destination': 'CUTOFF',
                'intensity': rand_int(15, 25)
            },
            'patch2': {
                'source': 'LFO2',
                'destination': 'PITCH',
                'intensity': rand_int(3, 8)
            },
            'patch3': {
                'source': 'Velocity',
                'destination': 'CUTOFF',
                'intensity': rand_int(20, 35)
            },
            'patch4': {
                'source': 'MIDI2',
                'destination': 'CUTOFF',
                'intensity': rand_int(40, 60)
            }
        }
    }

    # Faster mod for movement
    patch['effects']['mod']['speed'] = rand_int(140, 160)
    patch['effects']['mod']['depth'] = rand_int(10, 20)

    # Lower delay depth for sequences
    patch['effects']['delay']['depth'] = rand_int(65, 75)

    return patch

def main():
    output_json_path = Path('../examples/boc_originals.json')

    print("╔═══════════════════════════════════════════════════════════════╗")
    print("║  Creating Original BOC Patches from Scratch                  ║")
    print("╚═══════════════════════════════════════════════════════════════╝")
    print()
    print("Using 5 patch archetypes from the BOC guide:")
    print("  1. Classic BOC Pad (35%)")
    print("  2. Detuned BOC Lead (30%)")
    print("  3. DWGS Texture Patch (20%)")
    print("  4. Ring Mod Bell Tone (10%)")
    print("  5. Arpeggiator Sequence (5%)")
    print()

    # Create 128 patches using the archetypes
    patches = []

    # Recipe distribution (128 patches total)
    recipe_counts = {
        'pad': 45,      # 35%
        'lead': 38,     # 30%
        'dwgs': 26,     # 20%
        'bell': 13,     # 10%
        'arp': 6        # 5%
    }

    # Build list of recipe types
    recipe_list = (
        ['pad'] * recipe_counts['pad'] +
        ['lead'] * recipe_counts['lead'] +
        ['dwgs'] * recipe_counts['dwgs'] +
        ['bell'] * recipe_counts['bell'] +
        ['arp'] * recipe_counts['arp']
    )

    # Shuffle for variety
    random.shuffle(recipe_list)

    # Generate patches
    recipe_funcs = {
        'pad': create_classic_pad,
        'lead': create_detuned_lead,
        'dwgs': create_dwgs_texture,
        'bell': create_bell_tone,
        'arp': create_arp_sequence
    }

    for i, recipe_type in enumerate(recipe_list):
        patch = recipe_funcs[recipe_type](i)
        patches.append(patch)

        if (i + 1) % 16 == 0:
            bank_letter = chr(65 + i // 16)
            print(f"  ✓ Created bank {bank_letter} ({i + 1}/128)")

    # Save to JSON
    print()
    print(f"Writing {len(patches)} original BOC patches to {output_json_path}...")
    with open(output_json_path, 'w') as f:
        json.dump(patches, f, indent=2)

    print()
    print("✓ Complete!")
    print()
    print(f"Created {len(patches)} completely original BOC-style patches:")
    print(f"  - {recipe_counts['pad']} Classic Pads")
    print(f"  - {recipe_counts['lead']} Detuned Leads")
    print(f"  - {recipe_counts['dwgs']} DWGS Textures")
    print(f"  - {recipe_counts['bell']} Ring Mod Bells")
    print(f"  - {recipe_counts['arp']} Arpeggiator Sequences")
    print()
    print("Next step: Encode to .syx file")

if __name__ == '__main__':
    main()
