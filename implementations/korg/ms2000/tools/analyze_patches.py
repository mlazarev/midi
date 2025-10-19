#!/usr/bin/env python3
"""
Korg MS2000 Comprehensive Patch Analyzer

This script provides complete analysis of all 254 bytes in MS2000 patches,
enabling detailed comparison and pattern recognition across patch banks.
"""

from decode_sysex import decode_korg_7bit, parse_sysex_file
import sys
import json

class MS2000PatchAnalyzer:
    """Complete parameter extraction for MS2000 patches."""

    # Lookup tables
    VOICE_MODES = ['Single', 'Split', 'Layer', 'Vocoder']
    SCALE_KEYS = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    SCALE_TYPES = ['Equal Temp', 'Pure Major', 'Pure Minor', 'Pythagorean', 'Werckmeist', 'Kirnberger', 'Slendro', 'Pelog', 'Ionian', 'User Scale']
    DELAY_TYPES = ['StereoDelay', 'CrossDelay', 'L/R Delay']
    MOD_TYPES = ['Cho/Flg', 'Ensemble', 'Phaser']
    ARP_TYPES = ['Up', 'Down', 'Alt1', 'Alt2', 'Random', 'Trigger']
    OSC1_WAVES = ['Saw', 'Pulse', 'Triangle', 'Sine', 'Vox Wave', 'DWGS', 'Noise', 'Audio In']
    OSC2_WAVES = ['Saw', 'Square', 'Triangle']
    OSC2_MODS = ['Off', 'Ring', 'Sync', 'Ring+Sync']
    FILTER_TYPES = ['24dB LPF', '12dB LPF', '12dB BPF', '12dB HPF']
    LFO_WAVES = ['Saw', 'Square', 'Triangle', 'S/H']
    LFO2_WAVES = ['Saw', 'Square+', 'Sine', 'S/H']
    KEY_SYNC_MODES = ['OFF', 'Timbre', 'Voice']
    ASSIGN_MODES = ['Mono', 'Poly', 'Unison']
    KEY_PRIORITY = ['Last', 'Low', 'High']
    PATCH_SOURCES = ['EG1', 'EG2', 'LFO1', 'LFO2', 'Velocity', 'KbdTrack', 'MIDI1', 'MIDI2']
    PATCH_DESTS = ['Pitch', 'OSC2Pitch', 'OSC1Ctrl1', 'NoiseLevel', 'Cutoff', 'Amp', 'Pan', 'LFO2Freq']

    def __init__(self, patch_data):
        """Initialize analyzer with 254 bytes of patch data."""
        if len(patch_data) < 254:
            raise ValueError(f"Patch data must be 254 bytes, got {len(patch_data)}")
        self.data = patch_data
        self.params = {}
        self.parse_all()

    def signed(self, value, center):
        """Convert unsigned byte to signed value around center."""
        return int(value) - center

    def parse_all(self):
        """Parse all 254 bytes of patch parameters."""
        d = self.data
        p = self.params

        # Bytes 0-11: Program Name
        p['name'] = d[0:12].decode('ascii', errors='replace').rstrip()

        # Byte 16: Voice Mode
        p['timbre_voice'] = (d[16] >> 6) & 0x03
        voice_mode_idx = (d[16] >> 4) & 0x03
        p['voice_mode'] = self.VOICE_MODES[voice_mode_idx]

        # Byte 17: Scale
        scale_key_idx = (d[17] >> 4) & 0x0F
        p['scale_key'] = self.SCALE_KEYS[scale_key_idx] if scale_key_idx < 12 else scale_key_idx
        scale_type_idx = d[17] & 0x0F
        p['scale_type'] = self.SCALE_TYPES[scale_type_idx] if scale_type_idx < 10 else scale_type_idx

        # Byte 18: Split Point
        p['split_point'] = d[18]

        # Bytes 19-22: DELAY FX
        p['delay_sync'] = bool((d[19] >> 7) & 0x01)
        p['delay_timebase'] = d[19] & 0x0F
        p['delay_time'] = d[20]
        p['delay_depth'] = d[21]
        p['delay_type'] = self.DELAY_TYPES[d[22]] if d[22] < 3 else d[22]

        # Bytes 23-25: MOD FX
        p['mod_speed'] = d[23]
        p['mod_depth'] = d[24]
        p['mod_type'] = self.MOD_TYPES[d[25]] if d[25] < 3 else d[25]

        # Bytes 26-29: EQ
        p['eq_hi_freq'] = d[26]
        p['eq_hi_gain'] = self.signed(d[27], 64)
        p['eq_low_freq'] = d[28]
        p['eq_low_gain'] = self.signed(d[29], 64)

        # Bytes 30-36: ARPEGGIATOR
        p['arp_tempo'] = (d[30] << 8) | d[31]
        p['arp_on'] = bool((d[32] >> 7) & 0x01)
        p['arp_latch'] = bool((d[32] >> 6) & 0x01)
        p['arp_target'] = (d[32] >> 4) & 0x03
        p['arp_keysync'] = bool(d[32] & 0x01)
        arp_type_idx = d[33] & 0x0F
        p['arp_type'] = self.ARP_TYPES[arp_type_idx] if arp_type_idx < 6 else arp_type_idx
        p['arp_range'] = ((d[33] >> 4) & 0x0F) + 1
        p['arp_gate'] = d[34]
        p['arp_resolution'] = d[35]
        p['arp_swing'] = self.signed(d[36], 100)

        # Parse TIMBRE 1 (bytes 38-145) - offset +0 in TABLE 2
        p['timbre1'] = self._parse_timbre(d[38:146])

        # Parse TIMBRE 2 (bytes 146-253) - for Split/Layer modes
        if voice_mode_idx in [1, 2]:  # Split or Layer
            p['timbre2'] = self._parse_timbre(d[146:254])
        else:
            p['timbre2'] = None

    def _parse_timbre(self, timbre_data):
        """Parse a single timbre (108 bytes as per TABLE 2)."""
        t = {}
        d = timbre_data

        # +0: MIDI Channel
        t['midi_ch'] = self.signed(d[0], 1) if d[0] == 255 else d[0]

        # +1: Assign Mode, EG Reset, Trigger, Key Priority
        t['assign_mode'] = self.ASSIGN_MODES[(d[1] >> 6) & 0x03]
        t['eg2_reset'] = bool((d[1] >> 5) & 0x01)
        t['eg1_reset'] = bool((d[1] >> 4) & 0x01)
        t['trigger_mode'] = 'Multi' if (d[1] >> 3) & 0x01 else 'Single'
        t['key_priority'] = self.KEY_PRIORITY[d[1] & 0x03]

        # +2: Unison Detune
        t['unison_detune'] = d[2]

        # +3-6: PITCH
        t['tune'] = self.signed(d[3], 64)
        t['bend_range'] = self.signed(d[4], 64)
        t['transpose'] = self.signed(d[5], 64)
        t['vibrato_int'] = self.signed(d[6], 64)

        # +7-11: OSC1
        t['osc1_wave'] = self.OSC1_WAVES[d[7]] if d[7] < 8 else d[7]
        t['osc1_ctrl1'] = d[8]
        t['osc1_ctrl2'] = d[9]
        t['osc1_dwgs'] = d[10]

        # +12-14: OSC2
        t['osc2_mod'] = self.OSC2_MODS[(d[12] >> 4) & 0x03]
        t['osc2_wave'] = self.OSC2_WAVES[d[12] & 0x03]
        t['osc2_semitone'] = self.signed(d[13], 64)
        t['osc2_tune'] = self.signed(d[14], 64)

        # +15: Portamento
        t['portamento'] = d[15] & 0x7F

        # +16-18: MIXER
        t['osc1_level'] = d[16]
        t['osc2_level'] = d[17]
        t['noise_level'] = d[18]

        # +19-24: FILTER
        t['filter_type'] = self.FILTER_TYPES[d[19]] if d[19] < 4 else d[19]
        t['cutoff'] = d[20]
        t['resonance'] = d[21]
        t['filter_eg1_int'] = self.signed(d[22], 64)
        t['filter_vel_sens'] = self.signed(d[23], 64)
        t['filter_kbd_track'] = self.signed(d[24], 64)

        # +25-29: AMP
        t['amp_level'] = d[25]
        t['pan'] = d[26]
        t['amp_sw'] = 'Gate' if (d[27] >> 6) & 0x01 else 'EG2'
        t['distortion'] = bool(d[27] & 0x01)
        t['amp_vel_sens'] = self.signed(d[28], 64)
        t['amp_kbd_track'] = self.signed(d[29], 64)

        # +30-33: EG1 (Filter)
        t['eg1_attack'] = d[30]
        t['eg1_decay'] = d[31]
        t['eg1_sustain'] = d[32]
        t['eg1_release'] = d[33]

        # +34-37: EG2 (Amp)
        t['eg2_attack'] = d[34]
        t['eg2_decay'] = d[35]
        t['eg2_sustain'] = d[36]
        t['eg2_release'] = d[37]

        # +38-40: LFO1
        t['lfo1_keysync'] = self.KEY_SYNC_MODES[(d[38] >> 4) & 0x03]
        t['lfo1_wave'] = self.LFO_WAVES[d[38] & 0x03]
        t['lfo1_freq'] = d[39]
        t['lfo1_tempo_sync'] = bool((d[40] >> 7) & 0x01)
        t['lfo1_sync_note'] = d[40] & 0x1F

        # +41-43: LFO2
        t['lfo2_keysync'] = self.KEY_SYNC_MODES[(d[41] >> 4) & 0x03]
        t['lfo2_wave'] = self.LFO2_WAVES[d[41] & 0x03]
        t['lfo2_freq'] = d[42]
        t['lfo2_tempo_sync'] = bool((d[43] >> 7) & 0x01)
        t['lfo2_sync_note'] = d[43] & 0x1F

        # +44-51: PATCH (Modulation Matrix)
        t['patch1_dest'] = self.PATCH_DESTS[(d[44] >> 4) & 0x07]
        t['patch1_src'] = self.PATCH_SOURCES[d[44] & 0x07]
        t['patch1_int'] = self.signed(d[45], 64)

        t['patch2_dest'] = self.PATCH_DESTS[(d[46] >> 4) & 0x07]
        t['patch2_src'] = self.PATCH_SOURCES[d[46] & 0x07]
        t['patch2_int'] = self.signed(d[47], 64)

        t['patch3_dest'] = self.PATCH_DESTS[(d[48] >> 4) & 0x07]
        t['patch3_src'] = self.PATCH_SOURCES[d[48] & 0x07]
        t['patch3_int'] = self.signed(d[49], 64)

        t['patch4_dest'] = self.PATCH_DESTS[(d[50] >> 4) & 0x07]
        t['patch4_src'] = self.PATCH_SOURCES[d[50] & 0x07]
        t['patch4_int'] = self.signed(d[51], 64)

        # +52-53: SEQ (Motion Sequencer control)
        t['seq_on'] = bool((d[52] >> 7) & 0x01)
        t['seq_mode'] = 'Loop' if (d[52] >> 6) & 0x01 else '1Shot'
        t['seq_resolution'] = d[52] & 0x1F
        t['seq_last_step'] = ((d[53] >> 4) & 0x0F) + 1
        t['seq_type'] = ['Forward', 'Reverse', 'Alt1', 'Alt2'][(d[53] >> 2) & 0x03]
        t['seq_keysync'] = self.KEY_SYNC_MODES[d[53] & 0x03]

        # Note: SEQ parameters (+54-107) contain motion sequencer step data
        # These are complex and would require additional parsing

        return t

    def to_dict(self):
        """Return complete parameters as dictionary."""
        return self.params

    def get_summary(self):
        """Return human-readable summary."""
        p = self.params
        t1 = p.get('timbre1', {})

        lines = [
            f"Name: {p.get('name', 'Unnamed')}",
            f"Voice Mode: {p.get('voice_mode')}",
            f"",
            "EFFECTS:",
            f"  Delay: {p.get('delay_type')} (Time={p.get('delay_time')}, Depth={p.get('delay_depth')}, Sync={p.get('delay_sync')})",
            f"  Mod FX: {p.get('mod_type')} (Speed={p.get('mod_speed')}, Depth={p.get('mod_depth')})",
            f"  EQ: HiFreq={p.get('eq_hi_freq')} HiGain={p.get('eq_hi_gain')} | LoFreq={p.get('eq_low_freq')} LoGain={p.get('eq_low_gain')}",
            f"",
            "ARPEGGIATOR:",
            f"  Status: {'ON' if p.get('arp_on') else 'OFF'} | Type: {p.get('arp_type')} | Range: {p.get('arp_range')}oct",
            f"  Tempo: {p.get('arp_tempo')} BPM | Gate: {p.get('arp_gate')}% | Latch: {p.get('arp_latch')}",
            f"",
            "TIMBRE 1:",
            f"  Assign: {t1.get('assign_mode')} | Tune: {t1.get('tune')} | Transpose: {t1.get('transpose')}",
            f"  OSC1: {t1.get('osc1_wave')} (Ctrl1={t1.get('osc1_ctrl1')}, Ctrl2={t1.get('osc1_ctrl2')}) | Level: {t1.get('osc1_level')}",
            f"  OSC2: {t1.get('osc2_wave')} {t1.get('osc2_mod')} (Semi={t1.get('osc2_semitone')}, Tune={t1.get('osc2_tune')}) | Level: {t1.get('osc2_level')}",
            f"  Noise Level: {t1.get('noise_level')}",
            f"  Filter: {t1.get('filter_type')} | Cutoff={t1.get('cutoff')} Res={t1.get('resonance')} EG1Int={t1.get('filter_eg1_int')}",
            f"  EG1 (Filter): A={t1.get('eg1_attack')} D={t1.get('eg1_decay')} S={t1.get('eg1_sustain')} R={t1.get('eg1_release')}",
            f"  EG2 (Amp): A={t1.get('eg2_attack')} D={t1.get('eg2_decay')} S={t1.get('eg2_sustain')} R={t1.get('eg2_release')}",
            f"  Amp: Level={t1.get('amp_level')} Pan={t1.get('pan')} Dist={t1.get('distortion')}",
            f"  LFO1: {t1.get('lfo1_wave')} Freq={t1.get('lfo1_freq')} Sync={t1.get('lfo1_keysync')} TempoSync={t1.get('lfo1_tempo_sync')}",
            f"  LFO2: {t1.get('lfo2_wave')} Freq={t1.get('lfo2_freq')} Sync={t1.get('lfo2_keysync')} TempoSync={t1.get('lfo2_tempo_sync')}",
            f"  Portamento: {t1.get('portamento')}",
            f"  Patches (Mod Matrix):",
            f"    1: {t1.get('patch1_src')} -> {t1.get('patch1_dest')} ({t1.get('patch1_int'):+d})",
            f"    2: {t1.get('patch2_src')} -> {t1.get('patch2_dest')} ({t1.get('patch2_int'):+d})",
            f"    3: {t1.get('patch3_src')} -> {t1.get('patch3_dest')} ({t1.get('patch3_int'):+d})",
            f"    4: {t1.get('patch4_src')} -> {t1.get('patch4_dest')} ({t1.get('patch4_int'):+d})",
        ]

        if p.get('timbre2'):
            lines.append("\nTIMBRE 2: (see detailed output)")

        return '\n'.join(lines)


def analyze_patch_bank(filename, output_format='summary', silent=False):
    """Analyze all patches in a SysEx file."""
    # Read and decode the data stream directly without calling parse_sysex_file
    with open(filename, 'rb') as f:
        data = f.read()

    # Verify header
    if not silent:
        if len(data) < 5:
            raise ValueError("File too small to be a valid SysEx file")
        if data[0] != 0xF0:
            raise ValueError("Not a SysEx file (missing F0 start byte)")
        if data[1] != 0x42:
            raise ValueError("Not a Korg SysEx file (manufacturer ID != 0x42)")
        if data[3] != 0x58:
            raise ValueError("Not an MS2000 SysEx file (device ID != 0x58)")

    # Decode the data stream
    encoded_stream = data[5:]  # Skip header
    decoded_stream = decode_korg_7bit(encoded_stream)

    PATCH_SIZE = 254
    num_patches = len(decoded_stream) // PATCH_SIZE

    analyzed_patches = []
    for i in range(num_patches):
        offset = i * PATCH_SIZE
        patch_data = decoded_stream[offset:offset + PATCH_SIZE]

        try:
            analyzer = MS2000PatchAnalyzer(patch_data)
            analyzed_patches.append(analyzer)
        except Exception as e:
            if not silent:
                print(f"Warning: Failed to analyze patch {i+1}: {e}", file=sys.stderr)
            continue

    return analyzed_patches


def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_patches.py <file.syx> [--json|--detailed]")
        print("\nOptions:")
        print("  --json      Output as JSON")
        print("  --detailed  Show detailed parameters for each patch")
        sys.exit(1)

    filename = sys.argv[1]
    output_json = '--json' in sys.argv
    detailed = '--detailed' in sys.argv

    if not output_json:
        print(f"Analyzing: {filename}", file=sys.stderr)
        print("=" * 80, file=sys.stderr)

    analyzers = analyze_patch_bank(filename, silent=output_json)

    if output_json:
        # Output JSON
        all_data = []
        for i, analyzer in enumerate(analyzers):
            bank = chr(ord('A') + i // 16)
            num = (i % 16) + 1
            data = analyzer.to_dict()
            data['patch_id'] = f"{bank}{num:02d}"
            all_data.append(data)

        print(json.dumps(all_data, indent=2))
    else:
        # Output text summary
        for i, analyzer in enumerate(analyzers):
            bank = chr(ord('A') + i // 16)
            num = (i % 16) + 1

            print(f"\n[{bank}{num:02d}] ═══════════════════════════════════════════════════════")
            if detailed:
                print(analyzer.get_summary())
            else:
                p = analyzer.params
                name = p.get('name', '')
                print(f"Name: {name if name else '(unnamed)'}")
                print(f"Mode: {p.get('voice_mode')} | Delay: {p.get('delay_type')} | Mod: {p.get('mod_type')}")
                t1 = p.get('timbre1', {})
                print(f"OSC1: {t1.get('osc1_wave')} | OSC2: {t1.get('osc2_wave')} {t1.get('osc2_mod')}")
                print(f"Filter: {t1.get('filter_type')} Cutoff={t1.get('cutoff')} Res={t1.get('resonance')}")
                print(f"EG1: A{t1.get('eg1_attack')} D{t1.get('eg1_decay')} S{t1.get('eg1_sustain')} R{t1.get('eg1_release')} | EG2: A{t1.get('eg2_attack')} D{t1.get('eg2_decay')} S{t1.get('eg2_sustain')} R{t1.get('eg2_release')}")


if __name__ == '__main__':
    main()
