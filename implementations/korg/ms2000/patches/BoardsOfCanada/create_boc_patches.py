#!/usr/bin/env python3
"""
Create BOC-style patches from scratch for Korg MS2000.

Generates BOCSunday.syx with 16 original Boards of Canada-inspired patches
based on analysis of authentic BOC patch bank and synthesis principles.
"""

import os
import struct

class MS2000PatchBuilder:
    """Build MS2000 patches from parameters."""

    def __init__(self, name=""):
        """Initialize with default BOC-style settings."""
        self.data = bytearray(254)  # 254 bytes per patch

        # Program name (bytes 0-11)
        self.set_name(name)

        # Reserved bytes 12-15
        self.data[12:16] = [0, 0, 0, 0]

        # Default BOC settings
        self.set_voice_mode('Single')
        self.set_scale('C', 'Equal Temp')
        self.set_split_point(60)

        # Effects - BOC defaults
        self.set_delay('L/R Delay', time=40, depth=85, sync=False)
        self.set_mod_fx('Cho/Flg', speed=20, depth=30)
        self.set_eq(hi_freq=20, hi_gain=0, low_freq=15, low_gain=-3)

        # Arpeggiator - default OFF
        self.set_arp(on=False, tempo=120, type='Up', range=1, gate=80, latch=False)

        # Initialize Timbre1 with BOC defaults (bytes 38-145)
        self.init_timbre1()

    def set_name(self, name):
        """Set patch name (max 12 chars, padded with spaces)."""
        name = name[:12].ljust(12)
        self.data[0:12] = name.encode('ascii')

    def set_voice_mode(self, mode):
        """Set voice mode: Single, Split, Layer, Vocoder."""
        modes = {'Single': 0, 'Split': 1, 'Layer': 2, 'Vocoder': 3}
        # Byte 16 layout (per MS2000 docs):
        #   bits 6-7: Timbre select/enable
        #     01 = Timbre1, 10 = Timbre2, 11 = Both (Layer/Split)
        #   bits 4-5: Voice mode (0=Single,1=Split,2=Layer,3=Vocoder)
        # For our generated patches we explicitly enable Timbre1.
        timbre_bits = (1 << 6)  # 0b01 in bits 6-7
        self.data[16] = (self.data[16] & 0x0F) | timbre_bits | ((modes[mode] & 0x03) << 4)

    def set_scale(self, key, type):
        """Set scale key and type."""
        keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        types = ['Equal Temp', 'Pure Major', 'Pure Minor', 'Pythagorean',
                 'Werckmeist', 'Kirnberger', 'Slendro', 'Pelog', 'Ionian', 'User Scale']
        key_idx = keys.index(key) if key in keys else 0
        type_idx = types.index(type) if type in types else 0
        self.data[17] = (key_idx << 4) | type_idx

    def set_split_point(self, note):
        """Set split point (0-127)."""
        self.data[18] = note & 0x7F

    def set_delay(self, type, time=40, depth=85, sync=False, timebase=0):
        """Set delay FX."""
        types = {'StereoDelay': 0, 'CrossDelay': 1, 'L/R Delay': 2}
        self.data[19] = (1 if sync else 0) << 7 | (timebase & 0x0F)
        self.data[20] = time & 0x7F
        self.data[21] = depth & 0x7F
        self.data[22] = types.get(type, 2)

    def set_mod_fx(self, type, speed=20, depth=30):
        """Set modulation FX."""
        types = {'Cho/Flg': 0, 'Ensemble': 1, 'Phaser': 2}
        self.data[23] = speed & 0x7F
        self.data[24] = depth & 0x7F
        self.data[25] = types.get(type, 0)

    def set_eq(self, hi_freq=20, hi_gain=0, low_freq=15, low_gain=0):
        """Set EQ (gain is signed, centered at 64)."""
        self.data[26] = hi_freq & 0x7F
        self.data[27] = (hi_gain + 64) & 0x7F
        self.data[28] = low_freq & 0x7F
        self.data[29] = (low_gain + 64) & 0x7F

    def set_arp(self, on=False, tempo=120, type='Up', range=1, gate=80,
                latch=False, resolution=1, swing=0):
        """Set arpeggiator."""
        types = {'Up': 0, 'Down': 1, 'Alt1': 2, 'Alt2': 3, 'Random': 4, 'Trigger': 5}
        self.data[30] = (tempo >> 8) & 0xFF
        self.data[31] = tempo & 0xFF
        self.data[32] = ((1 if on else 0) << 7 |
                        (1 if latch else 0) << 6 |
                        0)  # target=0 (both), keysync=0
        self.data[33] = ((range - 1) << 4) | types.get(type, 0)
        self.data[34] = gate & 0x7F
        self.data[35] = resolution & 0x7F
        self.data[36] = (swing + 100) & 0x7F

    def init_timbre1(self):
        """Initialize Timbre1 with BOC defaults."""
        t = 38  # Timbre1 starts at byte 38

        # +0: MIDI Channel (0 = channel 1, 255 = global)
        self.data[t] = 255  # Global

        # +1: Assign Mode (Poly), trigger, priority
        self.data[t+1] = (1 << 6)  # Poly mode

        # +2: Unison Detune
        self.data[t+2] = 0

        # +3-6: Pitch
        self.data[t+3] = 64  # Tune (centered)
        self.data[t+4] = 64 + 2  # Bend range +2
        self.data[t+5] = 64  # Transpose (centered)
        self.data[t+6] = 64  # Vibrato intensity (centered = 0)

        # +7-11: OSC1 (default to Saw)
        self.data[t+7] = 0  # Saw
        self.data[t+8] = 0  # CTRL1
        self.data[t+9] = 0  # CTRL2
        self.data[t+10] = 0  # DWGS
        self.data[t+11] = 0  # dummy

        # +12-14: OSC2 (default to Triangle, Off)
        self.data[t+12] = 2  # Triangle, Off modulation
        self.data[t+13] = 64 + 7  # +7 semitones (perfect fifth)
        self.data[t+14] = 64  # Tune centered

        # +15: Portamento
        self.data[t+15] = 0  # No portamento

        # +16-18: Mixer
        self.data[t+16] = 127  # OSC1 level MAX
        self.data[t+17] = 92   # OSC2 level
        self.data[t+18] = 20   # Noise level

        # +19-24: Filter (12dB LPF, moderate cutoff, low res)
        self.data[t+19] = 1  # 12dB LPF
        self.data[t+20] = 55  # Cutoff
        self.data[t+21] = 20  # Resonance
        self.data[t+22] = 64  # EG1 intensity (centered = 0)
        self.data[t+23] = 64  # Vel sense (centered = 0)
        self.data[t+24] = 64  # Kbd track (centered = 0)

        # +25-29: Amp
        self.data[t+25] = 127  # Level MAX
        self.data[t+26] = 64   # Pan center
        self.data[t+27] = 0    # Amp SW = EG2, Distortion OFF
        self.data[t+28] = 64   # Vel sense (centered = 0)
        self.data[t+29] = 64   # Kbd track (centered = 0)

        # +30-33: EG1 (Filter) - Fast attack, medium decay, high sustain, long release
        self.data[t+30] = 0    # Attack
        self.data[t+31] = 64   # Decay
        self.data[t+32] = 127  # Sustain
        self.data[t+33] = 90   # Release

        # +34-37: EG2 (Amp) - Fast attack, medium decay, high sustain, long release
        self.data[t+34] = 0    # Attack
        self.data[t+35] = 64   # Decay
        self.data[t+36] = 127  # Sustain
        self.data[t+37] = 110  # Release

        # +38-40: LFO1 (Triangle, slow)
        self.data[t+38] = 2  # Triangle, Key Sync OFF
        self.data[t+39] = 10  # Frequency (slow)
        self.data[t+40] = 0   # Tempo sync OFF

        # +41-43: LFO2 (Sine, medium)
        self.data[t+41] = 2  # Sine, Key Sync OFF
        self.data[t+42] = 70  # Frequency (medium)
        self.data[t+43] = 0   # Tempo sync OFF

        # +44-51: Patch points (Modulation matrix)
        # Patch 1: LFO1 -> Pitch (+10)
        self.data[t+44] = (0 << 4) | 2  # Dest=Pitch, Src=LFO1
        self.data[t+45] = 64 + 10  # Intensity +10

        # Patch 2: LFO2 -> Cutoff (+15)
        self.data[t+46] = (4 << 4) | 3  # Dest=Cutoff, Src=LFO2
        self.data[t+47] = 64 + 15  # Intensity +15

        # Patch 3: LFO1 -> Cutoff (+8)
        self.data[t+48] = (4 << 4) | 2  # Dest=Cutoff, Src=LFO1
        self.data[t+49] = 64 + 8  # Intensity +8

        # Patch 4: MIDI2 -> Cutoff (+60)
        self.data[t+50] = (4 << 4) | 7  # Dest=Cutoff, Src=MIDI2
        self.data[t+51] = 64 + 60  # Intensity +60

        # +52-107: SEQ and other params - leave at defaults (zeros)
        self.data[t+52:t+108] = [0] * 56

    def set_timbre_osc1(self, wave='Saw', ctrl1=0, ctrl2=0, dwgs=0, level=127):
        """Set OSC1 parameters."""
        waves = {'Saw': 0, 'Pulse': 1, 'Triangle': 2, 'Sine': 3,
                 'Vox Wave': 4, 'DWGS': 5, 'Noise': 6, 'Audio In': 7}
        t = 38
        self.data[t+7] = waves.get(wave, 0)
        self.data[t+8] = ctrl1 & 0x7F
        self.data[t+9] = ctrl2 & 0x7F
        self.data[t+10] = dwgs & 0x7F
        self.data[t+16] = level & 0x7F

    def set_timbre_osc2(self, wave='Triangle', mod='Off', semitone=7, tune=0, level=92):
        """Set OSC2 parameters (per MS2000 spec).

        Byte layout (+12):
          - B4..5: Mod Select (0..3 = Off, Ring, Sync, Ring+Sync)
          - B0..1: Wave (0..2 = Saw, Square, Triangle)
          - Other bits must be 0
        """
        waves = {'Saw': 0, 'Square': 1, 'Triangle': 2}
        mods = {'Off': 0, 'Ring': 1, 'Sync': 2, 'Ring+Sync': 3}
        t = 38
        osc2 = ((mods.get(mod, 0) & 0x03) << 4) | (waves.get(wave, 2) & 0x03)
        self.data[t+12] = osc2
        self.data[t+13] = (semitone + 64) & 0x7F
        self.data[t+14] = (tune + 64) & 0x7F
        self.data[t+17] = level & 0x7F

    def set_timbre_mixer(self, osc1=127, osc2=92, noise=20):
        """Set mixer levels."""
        t = 38
        self.data[t+16] = osc1 & 0x7F
        self.data[t+17] = osc2 & 0x7F
        self.data[t+18] = noise & 0x7F

    def set_timbre_filter(self, type='12dB LPF', cutoff=55, resonance=20, eg1_int=0):
        """Set filter parameters."""
        types = {'24dB LPF': 0, '12dB LPF': 1, '12dB BPF': 2, '12dB HPF': 3}
        t = 38
        self.data[t+19] = types.get(type, 1)
        self.data[t+20] = cutoff & 0x7F
        self.data[t+21] = resonance & 0x7F
        self.data[t+22] = (eg1_int + 64) & 0x7F

    def set_timbre_envelopes(self, eg1_adsr=(0, 64, 127, 90), eg2_adsr=(0, 64, 127, 110)):
        """Set EG1 (filter) and EG2 (amp) envelopes."""
        t = 38
        self.data[t+30:t+34] = [v & 0x7F for v in eg1_adsr]
        self.data[t+34:t+38] = [v & 0x7F for v in eg2_adsr]

    def set_timbre_lfos(self, lfo1_wave='Triangle', lfo1_freq=10,
                       lfo2_wave='Sine', lfo2_freq=70):
        """Set LFO parameters."""
        waves1 = {'Saw': 0, 'Square': 1, 'Triangle': 2, 'S/H': 3}
        waves2 = {'Saw': 0, 'Square+': 1, 'Sine': 2, 'S/H': 3}
        t = 38
        self.data[t+38] = waves1.get(lfo1_wave, 2)
        self.data[t+39] = lfo1_freq & 0x7F
        self.data[t+41] = waves2.get(lfo2_wave, 2)
        self.data[t+42] = lfo2_freq & 0x7F

    def set_timbre_patch(self, patch_num, source, dest, intensity):
        """Set modulation patch point (1-4)."""
        sources = {'EG1': 0, 'EG2': 1, 'LFO1': 2, 'LFO2': 3, 'Velocity': 4,
                   'KbdTrack': 5, 'MIDI1': 6, 'MIDI2': 7}
        dests = {'Pitch': 0, 'OSC2Pitch': 1, 'OSC1Ctrl1': 2, 'NoiseLevel': 3,
                 'Cutoff': 4, 'Amp': 5, 'Pan': 6, 'LFO2Freq': 7}
        t = 38
        offset = 44 + (patch_num - 1) * 2
        self.data[t+offset] = (dests.get(dest, 0) << 4) | sources.get(source, 0)
        self.data[t+offset+1] = (intensity + 64) & 0x7F

    def get_bytes(self):
        """Return the 254-byte patch data."""
        return bytes(self.data)


def encode_korg_7bit(decoded_data):
    """Encode 8-bit data to Korg's 7-bit format (variant v2: MSBs in bits 0..6)."""
    encoded = bytearray()
    i = 0

    while i < len(decoded_data):
        # Get up to 7 bytes of 8-bit data
        chunk = decoded_data[i:i+7]
        if not chunk:
            break

        # Create MSB byte from bit 7 of each byte (bit order j -> bit j)
        msb_byte = 0
        for j, b in enumerate(chunk):
            if b & 0x80:
                msb_byte |= (1 << j)

        encoded.append(msb_byte)

        # Write lower 7 bits of each byte
        for b in chunk:
            encoded.append(b & 0x7F)

        i += 7

    return bytes(encoded)


def create_boc_sunday_patches():
    """Create 16 original BOC-style patches."""

    patches = []

    # === PATCH 1: Sunday Pad (Classic BOC Pad) ===
    p = MS2000PatchBuilder("Sunday Pad")
    p.set_delay('L/R Delay', time=38, depth=88)
    p.set_mod_fx('Cho/Flg', speed=18, depth=32)
    p.set_timbre_osc1(wave='Sine', level=127)
    p.set_timbre_osc2(wave='Triangle', mod='Off', semitone=7, level=95)
    p.set_timbre_mixer(osc1=127, osc2=95, noise=18)
    p.set_timbre_filter(type='12dB LPF', cutoff=52, resonance=18, eg1_int=8)
    p.set_timbre_envelopes(eg1_adsr=(5, 65, 120, 95), eg2_adsr=(2, 68, 127, 115))
    p.set_timbre_lfos(lfo1_wave='Triangle', lfo1_freq=12, lfo2_wave='Sine', lfo2_freq=68)
    p.set_timbre_patch(1, 'LFO1', 'Pitch', 9)
    p.set_timbre_patch(2, 'LFO2', 'Pan', 25)
    p.set_timbre_patch(3, 'LFO1', 'Cutoff', 12)
    p.set_timbre_patch(4, 'MIDI2', 'Cutoff', 55)
    patches.append(p.get_bytes())

    # === PATCH 2: Analog Memory (Detuned Lead) ===
    p = MS2000PatchBuilder("Analog Mem")
    p.set_delay('L/R Delay', time=42, depth=78)
    p.set_mod_fx('Cho/Flg', speed=22, depth=38)
    p.set_timbre_osc1(wave='Saw', ctrl1=60, level=127)
    p.set_timbre_osc2(wave='Saw', mod='Off', semitone=-7, tune=8, level=105)
    p.set_timbre_mixer(osc1=127, osc2=105, noise=22)
    p.set_timbre_filter(type='12dB LPF', cutoff=58, resonance=22, eg1_int=18)
    p.set_timbre_envelopes(eg1_adsr=(0, 58, 110, 75), eg2_adsr=(0, 55, 115, 82))
    p.set_timbre_lfos(lfo1_wave='Triangle', lfo1_freq=10, lfo2_wave='Sine', lfo2_freq=65)
    p.set_timbre_patch(1, 'LFO1', 'Pitch', 11)
    p.set_timbre_patch(2, 'LFO2', 'Cutoff', 16)
    p.set_timbre_patch(3, 'LFO1', 'OSC2Pitch', -12)
    p.set_timbre_patch(4, 'MIDI2', 'Cutoff', 70)
    patches.append(p.get_bytes())

    # === PATCH 3: Vintage Tape (DWGS Texture) ===
    p = MS2000PatchBuilder("Vintage Tape")
    p.set_delay('L/R Delay', time=40, depth=92)
    p.set_mod_fx('Phaser', speed=25, depth=15)
    p.set_timbre_osc1(wave='DWGS', dwgs=28, level=127)
    p.set_timbre_osc2(wave='Triangle', mod='Off', semitone=12, level=85)
    p.set_timbre_mixer(osc1=127, osc2=85, noise=25)
    p.set_timbre_filter(type='12dB LPF', cutoff=48, resonance=24, eg1_int=22)
    p.set_timbre_envelopes(eg1_adsr=(8, 68, 118, 100), eg2_adsr=(5, 70, 127, 108))
    p.set_timbre_lfos(lfo1_wave='Triangle', lfo1_freq=35, lfo2_wave='S/H', lfo2_freq=115)
    p.set_timbre_patch(1, 'LFO2', 'Cutoff', 8)
    p.set_timbre_patch(2, 'EG1', 'Pitch', 14)
    p.set_timbre_patch(3, 'LFO2', 'Pitch', 10)
    p.set_timbre_patch(4, 'MIDI2', 'Cutoff', 50)
    patches.append(p.get_bytes())

    # === PATCH 4: Nostalgia Pad ===
    p = MS2000PatchBuilder("Nostalgia")
    p.set_delay('L/R Delay', time=40, depth=85)
    p.set_mod_fx('Cho/Flg', speed=16, depth=28)
    p.set_timbre_osc1(wave='Triangle', ctrl1=25, level=127)
    p.set_timbre_osc2(wave='Triangle', mod='Off', semitone=5, level=98)
    p.set_timbre_mixer(osc1=127, osc2=98, noise=16)
    p.set_timbre_filter(type='12dB LPF', cutoff=50, resonance=16, eg1_int=5)
    p.set_timbre_envelopes(eg1_adsr=(10, 70, 125, 105), eg2_adsr=(8, 72, 127, 118))
    p.set_timbre_lfos(lfo1_wave='Triangle', lfo1_freq=8, lfo2_wave='Sine', lfo2_freq=72)
    p.set_timbre_patch(1, 'LFO1', 'Pitch', 8)
    p.set_timbre_patch(2, 'LFO2', 'Cutoff', 18)
    p.set_timbre_patch(3, 'LFO2', 'Pan', 22)
    p.set_timbre_patch(4, 'MIDI2', 'Cutoff', 65)
    patches.append(p.get_bytes())

    # === PATCH 5: Warm Rhodes (Bell-like) ===
    p = MS2000PatchBuilder("Warm Rhodes")
    p.set_delay('L/R Delay', time=40, depth=70)
    p.set_mod_fx('Cho/Flg', speed=20, depth=35)
    p.set_timbre_osc1(wave='Sine', level=115)
    p.set_timbre_osc2(wave='Square', mod='Ring', semitone=0, level=127)
    p.set_timbre_mixer(osc1=115, osc2=127, noise=18)
    p.set_timbre_filter(type='24dB LPF', cutoff=38, resonance=8, eg1_int=20)
    p.set_timbre_envelopes(eg1_adsr=(8, 30, 100, 125), eg2_adsr=(110, 95, 102, 120))
    p.set_timbre_lfos(lfo1_wave='Triangle', lfo1_freq=40, lfo2_wave='Sine', lfo2_freq=70)
    p.set_timbre_patch(1, 'LFO1', 'OSC2Pitch', -12)
    p.set_timbre_patch(2, 'LFO2', 'Pan', 28)
    p.set_timbre_patch(3, 'LFO2', 'Amp', 35)
    p.set_timbre_patch(4, 'MIDI2', 'Cutoff', 10)
    patches.append(p.get_bytes())

    # === PATCH 6: Dusty Bass ===
    p = MS2000PatchBuilder("Dusty Bass")
    p.set_delay('L/R Delay', time=40, depth=60)
    p.set_mod_fx('Cho/Flg', speed=25, depth=20)
    p.set_timbre_osc1(wave='Saw', ctrl1=70, level=127)
    p.set_timbre_osc2(wave='Triangle', mod='Off', semitone=-12, level=110)
    p.set_timbre_mixer(osc1=127, osc2=110, noise=12)
    p.set_timbre_filter(type='24dB LPF', cutoff=35, resonance=18, eg1_int=25)
    p.set_timbre_envelopes(eg1_adsr=(0, 45, 75, 55), eg2_adsr=(0, 40, 90, 60))
    p.set_timbre_lfos(lfo1_wave='Triangle', lfo1_freq=15, lfo2_wave='Sine', lfo2_freq=60)
    p.set_timbre_patch(1, 'LFO1', 'Cutoff', 22)
    p.set_timbre_patch(2, 'EG1', 'Pitch', 8)
    p.set_timbre_patch(3, 'LFO2', 'OSC1Ctrl1', 15)
    p.set_timbre_patch(4, 'MIDI2', 'Cutoff', 45)
    patches.append(p.get_bytes())

    # === PATCH 7: Childhood Arp ===
    p = MS2000PatchBuilder("Childhood")
    p.set_delay('L/R Delay', time=40, depth=75)
    p.set_mod_fx('Ensemble', speed=155, depth=12)
    p.set_arp(on=True, tempo=85, type='Up', range=2, gate=78, latch=True)
    p.set_timbre_osc1(wave='DWGS', dwgs=15, level=127)
    p.set_timbre_osc2(wave='Saw', mod='Off', semitone=7, level=95)
    p.set_timbre_mixer(osc1=127, osc2=95, noise=8)
    p.set_timbre_filter(type='12dB LPF', cutoff=45, resonance=20, eg1_int=12)
    p.set_timbre_envelopes(eg1_adsr=(0, 50, 85, 68), eg2_adsr=(0, 48, 95, 72))
    p.set_timbre_lfos(lfo1_wave='Triangle', lfo1_freq=12, lfo2_wave='Sine', lfo2_freq=65)
    p.set_timbre_patch(1, 'LFO1', 'Pitch', 7)
    p.set_timbre_patch(2, 'LFO2', 'Cutoff', 14)
    p.set_timbre_patch(3, 'LFO1', 'OSC2Pitch', 6)
    p.set_timbre_patch(4, 'MIDI2', 'Cutoff', 58)
    patches.append(p.get_bytes())

    # === PATCH 8: Faded Photo ===
    p = MS2000PatchBuilder("Faded Photo")
    p.set_delay('L/R Delay', time=38, depth=90)
    p.set_mod_fx('Cho/Flg', speed=14, depth=42)
    p.set_timbre_osc1(wave='Sine', level=127)
    p.set_timbre_osc2(wave='Saw', mod='Off', semitone=19, level=88)
    p.set_timbre_mixer(osc1=127, osc2=88, noise=22)
    p.set_timbre_filter(type='12dB LPF', cutoff=44, resonance=15, eg1_int=10)
    p.set_timbre_envelopes(eg1_adsr=(12, 72, 122, 110), eg2_adsr=(10, 75, 127, 120))
    p.set_timbre_lfos(lfo1_wave='Triangle', lfo1_freq=9, lfo2_wave='Sine', lfo2_freq=74)
    p.set_timbre_patch(1, 'LFO1', 'Pitch', 10)
    p.set_timbre_patch(2, 'LFO2', 'Cutoff', 20)
    p.set_timbre_patch(3, 'LFO2', 'Pan', 30)
    p.set_timbre_patch(4, 'MIDI2', 'Cutoff', 62)
    patches.append(p.get_bytes())

    # === PATCH 9: Seventies Sky ===
    p = MS2000PatchBuilder("70s Sky")
    p.set_delay('StereoDelay', time=55, depth=65)
    p.set_mod_fx('Ensemble', speed=18, depth=25)
    p.set_timbre_osc1(wave='Pulse', ctrl1=45, level=127)
    p.set_timbre_osc2(wave='Triangle', mod='Off', semitone=12, level=100)
    p.set_timbre_mixer(osc1=127, osc2=100, noise=14)
    p.set_timbre_filter(type='12dB LPF', cutoff=62, resonance=25, eg1_int=15)
    p.set_timbre_envelopes(eg1_adsr=(15, 68, 115, 88), eg2_adsr=(12, 70, 125, 98))
    p.set_timbre_lfos(lfo1_wave='Triangle', lfo1_freq=11, lfo2_wave='Sine', lfo2_freq=68)
    p.set_timbre_patch(1, 'LFO1', 'Pitch', 8)
    p.set_timbre_patch(2, 'LFO2', 'OSC1Ctrl1', 18)
    p.set_timbre_patch(3, 'LFO1', 'Cutoff', 10)
    p.set_timbre_patch(4, 'MIDI2', 'Cutoff', 48)
    patches.append(p.get_bytes())

    # === PATCH 10: Wobbly Lead ===
    p = MS2000PatchBuilder("Wobbly Lead")
    p.set_delay('L/R Delay', time=40, depth=82)
    p.set_mod_fx('Cho/Flg', speed=30, depth=45)
    p.set_timbre_osc1(wave='Saw', level=127)
    p.set_timbre_osc2(wave='Saw', mod='Sync', semitone=7, tune=5, level=108)
    p.set_timbre_mixer(osc1=127, osc2=108, noise=18)
    p.set_timbre_filter(type='12dB LPF', cutoff=60, resonance=20, eg1_int=20)
    p.set_timbre_envelopes(eg1_adsr=(0, 60, 100, 70), eg2_adsr=(0, 58, 110, 80))
    p.set_timbre_lfos(lfo1_wave='Triangle', lfo1_freq=8, lfo2_wave='Sine', lfo2_freq=66)
    p.set_timbre_patch(1, 'LFO1', 'Pitch', 12)
    p.set_timbre_patch(2, 'LFO2', 'Pitch', 6)
    p.set_timbre_patch(3, 'LFO1', 'Cutoff', 14)
    p.set_timbre_patch(4, 'MIDI2', 'Cutoff', 75)
    patches.append(p.get_bytes())

    # === PATCH 11: Distant Dream ===
    p = MS2000PatchBuilder("Distant")
    p.set_delay('L/R Delay', time=40, depth=95)
    p.set_mod_fx('Phaser', speed=12, depth=18)
    p.set_timbre_osc1(wave='DWGS', dwgs=35, level=127)
    p.set_timbre_osc2(wave='Triangle', mod='Off', semitone=7, level=90)
    p.set_timbre_mixer(osc1=127, osc2=90, noise=28)
    p.set_timbre_filter(type='12dB LPF', cutoff=40, resonance=12, eg1_int=18)
    p.set_timbre_envelopes(eg1_adsr=(20, 80, 127, 115), eg2_adsr=(18, 82, 127, 125))
    p.set_timbre_lfos(lfo1_wave='Triangle', lfo1_freq=10, lfo2_wave='Sine', lfo2_freq=70)
    p.set_timbre_patch(1, 'LFO1', 'Pitch', 9)
    p.set_timbre_patch(2, 'LFO2', 'Cutoff', 12)
    p.set_timbre_patch(3, 'LFO2', 'Pan', 26)
    p.set_timbre_patch(4, 'MIDI2', 'Cutoff', 52)
    patches.append(p.get_bytes())

    # === PATCH 12: Soft Pluck ===
    p = MS2000PatchBuilder("Soft Pluck")
    p.set_delay('L/R Delay', time=42, depth=68)
    p.set_mod_fx('Cho/Flg', speed=22, depth=30)
    p.set_timbre_osc1(wave='Triangle', level=120)
    # OSC2 does not support Sine; use Triangle for soft plucks
    p.set_timbre_osc2(wave='Triangle', mod='Off', semitone=12, level=85)
    p.set_timbre_mixer(osc1=120, osc2=85, noise=10)
    p.set_timbre_filter(type='12dB LPF', cutoff=55, resonance=18, eg1_int=28)
    p.set_timbre_envelopes(eg1_adsr=(0, 35, 65, 45), eg2_adsr=(0, 38, 80, 58))
    p.set_timbre_lfos(lfo1_wave='Triangle', lfo1_freq=18, lfo2_wave='Sine', lfo2_freq=65)
    p.set_timbre_patch(1, 'EG1', 'Pitch', 10)
    p.set_timbre_patch(2, 'LFO2', 'Cutoff', 8)
    p.set_timbre_patch(3, 'LFO1', 'Pan', 15)
    p.set_timbre_patch(4, 'MIDI2', 'Cutoff', 40)
    patches.append(p.get_bytes())

    # === PATCH 13: Morning Haze ===
    p = MS2000PatchBuilder("Morning Haze")
    p.set_delay('L/R Delay', time=40, depth=88)
    p.set_mod_fx('Cho/Flg', speed=15, depth=35)
    p.set_timbre_osc1(wave='Vox Wave', level=127)
    p.set_timbre_osc2(wave='Triangle', mod='Off', semitone=5, level=95)
    p.set_timbre_mixer(osc1=127, osc2=95, noise=20)
    p.set_timbre_filter(type='12dB LPF', cutoff=48, resonance=16, eg1_int=12)
    p.set_timbre_envelopes(eg1_adsr=(8, 68, 120, 100), eg2_adsr=(5, 70, 127, 112))
    p.set_timbre_lfos(lfo1_wave='Triangle', lfo1_freq=10, lfo2_wave='Sine', lfo2_freq=72)
    p.set_timbre_patch(1, 'LFO1', 'Pitch', 9)
    p.set_timbre_patch(2, 'LFO2', 'Cutoff', 16)
    p.set_timbre_patch(3, 'LFO1', 'OSC1Ctrl1', 12)
    p.set_timbre_patch(4, 'MIDI2', 'Cutoff', 58)
    patches.append(p.get_bytes())

    # === PATCH 14: Quiet Moment ===
    p = MS2000PatchBuilder("Quiet Moment")
    p.set_delay('L/R Delay', time=38, depth=80)
    p.set_mod_fx('Ensemble', speed=10, depth=22)
    p.set_timbre_osc1(wave='Sine', level=127)
    p.set_timbre_osc2(wave='Sine', mod='Off', semitone=7, tune=3, level=92)
    p.set_timbre_mixer(osc1=127, osc2=92, noise=15)
    p.set_timbre_filter(type='12dB LPF', cutoff=46, resonance=14, eg1_int=6)
    p.set_timbre_envelopes(eg1_adsr=(15, 75, 125, 108), eg2_adsr=(12, 78, 127, 118))
    p.set_timbre_lfos(lfo1_wave='Triangle', lfo1_freq=9, lfo2_wave='Sine', lfo2_freq=68)
    p.set_timbre_patch(1, 'LFO1', 'Pitch', 7)
    p.set_timbre_patch(2, 'LFO2', 'Pan', 24)
    p.set_timbre_patch(3, 'LFO1', 'Cutoff', 8)
    p.set_timbre_patch(4, 'MIDI2', 'Cutoff', 50)
    patches.append(p.get_bytes())

    # === PATCH 15: Retro Sweep ===
    p = MS2000PatchBuilder("Retro Sweep")
    p.set_delay('L/R Delay', time=40, depth=72)
    p.set_mod_fx('Phaser', speed=28, depth=30)
    p.set_timbre_osc1(wave='Pulse', ctrl1=55, level=127)
    p.set_timbre_osc2(wave='Saw', mod='Off', semitone=12, level=102)
    p.set_timbre_mixer(osc1=127, osc2=102, noise=18)
    p.set_timbre_filter(type='12dB BPF', cutoff=58, resonance=28, eg1_int=35)
    p.set_timbre_envelopes(eg1_adsr=(5, 65, 95, 80), eg2_adsr=(3, 68, 108, 90))
    p.set_timbre_lfos(lfo1_wave='Triangle', lfo1_freq=32, lfo2_wave='Sine', lfo2_freq=70)
    p.set_timbre_patch(1, 'LFO1', 'Cutoff', 25)
    p.set_timbre_patch(2, 'LFO2', 'OSC1Ctrl1', 20)
    p.set_timbre_patch(3, 'EG1', 'Pitch', 12)
    p.set_timbre_patch(4, 'MIDI2', 'Cutoff', 68)
    patches.append(p.get_bytes())

    # === PATCH 16: Sunset Chords ===
    p = MS2000PatchBuilder("Sunset")
    p.set_delay('L/R Delay', time=40, depth=86)
    p.set_mod_fx('Cho/Flg', speed=17, depth=33)
    p.set_timbre_osc1(wave='Saw', ctrl1=40, level=127)
    p.set_timbre_osc2(wave='Triangle', mod='Off', semitone=7, level=98)
    p.set_timbre_mixer(osc1=127, osc2=98, noise=20)
    p.set_timbre_filter(type='12dB LPF', cutoff=53, resonance=19, eg1_int=10)
    p.set_timbre_envelopes(eg1_adsr=(10, 68, 118, 98), eg2_adsr=(8, 70, 127, 110))
    p.set_timbre_lfos(lfo1_wave='Triangle', lfo1_freq=10, lfo2_wave='Sine', lfo2_freq=70)
    p.set_timbre_patch(1, 'LFO1', 'Pitch', 9)
    p.set_timbre_patch(2, 'LFO2', 'Cutoff', 15)
    p.set_timbre_patch(3, 'LFO2', 'Pan', 28)
    p.set_timbre_patch(4, 'MIDI2', 'Cutoff', 60)
    patches.append(p.get_bytes())

    return patches


def create_sysex_file(patches, output_path):
    """Create a complete MS2000 PROGRAM DATA DUMP SysEx file."""

    # Combine all patch data and encode as a single stream (per Korg bank dump)
    all_patch_data = b''.join(patches)
    encoded_data = encode_korg_7bit(all_patch_data)

    # Create SysEx file with header
    header = bytes([
        0xF0,  # SysEx start
        0x42,  # Korg
        0x30,  # MIDI channel 0 (3g format, g=0)
        0x58,  # MS2000 device ID
        0x4C   # PROGRAM DATA DUMP
    ])

    footer = bytes([0xF7])  # End of SysEx

    # Complete SysEx message
    sysex_data = header + encoded_data + footer

    # Write to file
    with open(output_path, 'wb') as f:
        f.write(sysex_data)

    print(f"Created {output_path}")
    print(f"  Total size: {len(sysex_data)} bytes")
    print(f"  Patches: {len(patches)}")
    print(f"  Encoded data: {len(encoded_data)} bytes")
    print(f"  Raw data: {254 * len(patches)} bytes")

    return sysex_data


if __name__ == '__main__':
    # Create patches
    print("Creating BOC Sunday patches...")
    patches = create_boc_sunday_patches()

    # Pad to 128 patches if needed (fill remaining with first patch)
    while len(patches) < 128:
        patches.append(patches[0])

    # Output path (this folder)
    output_dir = os.path.dirname(__file__)
    output_path = os.path.join(output_dir, 'BOCSunday.syx')

    # Create SysEx file
    create_sysex_file(patches, output_path)

    print("\nPatch List:")
    patch_names = [
        "Sunday Pad", "Analog Mem", "Vintage Tape", "Nostalgia",
        "Warm Rhodes", "Dusty Bass", "Childhood", "Faded Photo",
        "70s Sky", "Wobbly Lead", "Distant", "Soft Pluck",
        "Morning Haze", "Quiet Moment", "Retro Sweep", "Sunset"
    ]
    for i, name in enumerate(patch_names, 1):
        bank = chr(ord('A') + (i - 1) // 16)
        num = ((i - 1) % 16) + 1
        print(f"  [{bank}{num:02d}] {name}")

    print(f"\nPatches {len(patch_names)+1}-128: Repeated '{patch_names[0]}' for full bank")
    print("\n✓ BOCSunday.syx created successfully!")
    print("  Ready to load into your MS2000 or send via MIDI")
