#!/usr/bin/env python3
"""
Generate a detailed reference Markdown for BOCSunday.syx (all 128 patches).

Reads the bank from patches/BoardsOfCanada/BOCSunday.syx and writes
BOCSunday_DETAILED_REFERENCE.md alongside it.
"""

from __future__ import annotations

from pathlib import Path
import sys


def project_root() -> Path:
    return Path(__file__).resolve().parents[4]


def decode():
    root = project_root()
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    from implementations.korg.ms2000.tools.ms2000_core import parse_sysex_file  # type: ignore

    boc_path = root / "implementations/korg/ms2000/patches/BoardsOfCanada/BOCSunday.syx"
    patches = parse_sysex_file(str(boc_path))
    return patches


def map_osc1_wave(v: int) -> str:
    return ['Saw','Pulse','Triangle','Sine','Vox Wave','DWGS','Noise','Audio In'][v & 0x07]


def map_osc2(v: int) -> tuple[str,str]:
    mod = (v >> 4) & 0x03
    wave = v & 0x03
    waves = ['Saw','Square','Triangle']
    mods = ['Off','Ring','Sync','Ring+Sync']
    return waves[wave], mods[mod]


def map_filter(v: int) -> str:
    return ['24dB LPF','12dB LPF','12dB BPF','12dB HPF'][v & 0x03]


def map_lfo1_wave(v: int) -> str:
    return ['Saw','Square','Triangle','S/H'][v & 0x03]


def map_lfo2_wave(v: int) -> str:
    return ['Saw','Square+','Sine','S/H'][v & 0x03]


def map_delay_type(v: int) -> str:
    return ['StereoDelay','CrossDelay','L/R Delay'][v if v < 3 else 2]


def map_mod_type(v: int) -> str:
    return ['Cho/Flg','Ensemble','Phaser'][v if v < 3 else 0]


def map_arp_type(v: int) -> str:
    return ['Up','Down','Alt1','Alt2','Random','Trigger'][v if v < 6 else 0]


def classify(category_data: dict) -> str:
    if category_data['arp_on']:
        return 'Arpeggiator Sequence'
    if category_data['bass_like']:
        return 'Analog Bass'
    if category_data['pad_like']:
        return 'Ambient Pad'
    if category_data['keys_like']:
        return 'Keys / Bell-like'
    return 'Lead'


def generate_md(patches) -> str:
    lines: list[str] = []
    lines.append('# BOCSunday.syx — Detailed Reference')
    lines.append('')
    lines.append('Complete reference for all 128 patches in BOCSunday.syx (A01–H16).')
    lines.append('')
    for i, p in enumerate(patches, start=1):
        d = p.raw_data
        name = d[0:12].decode('ascii', errors='replace').rstrip()
        t = 38
        # Header FX/Arp
        delay_type = map_delay_type(d[22])
        delay_time = d[20]
        delay_depth = d[21]
        mod_type = map_mod_type(d[25])
        mod_speed = d[23]
        mod_depth = d[24]
        arp_on = bool((d[32] >> 7) & 1)
        arp_type = map_arp_type(d[33] & 0x0F)
        arp_range = ((d[33] >> 4) & 0x0F) + 1
        arp_tempo = (d[30] << 8) | d[31]
        # Timbre
        osc1_wave = map_osc1_wave(d[t+7])
        osc1_c1 = d[t+8]
        osc1_c2 = d[t+9]
        osc2_wave, osc2_mod = map_osc2(d[t+12])
        osc2_semi = int((d[t+13] & 0x7F) - 64)
        osc2_tune = int((d[t+14] & 0x7F) - 64)
        mix_osc1 = d[t+16]
        mix_osc2 = d[t+17]
        mix_noise = d[t+18]
        filt_type = map_filter(d[t+19])
        cutoff = d[t+20]
        resonance = d[t+21]
        eg1_int = int((d[t+22] & 0x7F) - 64)
        eg1 = tuple(d[t+30:t+34])
        eg2 = tuple(d[t+34:t+38])
        lfo1_wave = map_lfo1_wave(d[t+38])
        lfo1_freq = d[t+39]
        lfo2_wave = map_lfo2_wave(d[t+41])
        lfo2_freq = d[t+42]

        # Heuristic category
        bass_like = (filt_type.startswith('24dB') and cutoff < 42 and osc2_semi <= -12 and eg2[2] > 90 and eg2[1] < 50)
        pad_like = (eg2[0] <= 10 and eg2[3] >= 95)
        keys_like = (osc1_wave in ('Sine','Triangle') and mod_type in ('Cho/Flg','Phaser') and eg2[0] >= 40)
        cat = classify({'arp_on': arp_on, 'bass_like': bass_like, 'pad_like': pad_like, 'keys_like': keys_like})

        bank = chr(ord('A') + (i - 1)//16)
        num = ((i - 1) % 16) + 1
        lines.append(f'## {bank}{num:02d}: {name}')
        lines.append(f'Category: {cat}')
        lines.append('')
        lines.append('Oscillators:')
        lines.append(f'- OSC1: {osc1_wave} (Ctrl1={osc1_c1}, Ctrl2={osc1_c2}), Level={mix_osc1}')
        lines.append(f'- OSC2: {osc2_wave} ({osc2_mod}), Semitone={osc2_semi:+}, Tune={osc2_tune:+}, Level={mix_osc2}')
        lines.append(f'- Noise: Level={mix_noise}')
        lines.append('')
        lines.append('Filter:')
        lines.append(f'- {filt_type}, Cutoff={cutoff}, Resonance={resonance}, EG1 Int={eg1_int:+}')
        lines.append('')
        lines.append('Envelopes:')
        lines.append(f'- EG1 (Filter)  A/D/S/R = {eg1[0]}/{eg1[1]}/{eg1[2]}/{eg1[3]}')
        lines.append(f'- EG2 (Amp)     A/D/S/R = {eg2[0]}/{eg2[1]}/{eg2[2]}/{eg2[3]}')
        lines.append('')
        lines.append('LFOs:')
        lines.append(f'- LFO1: {lfo1_wave}, Freq={lfo1_freq}')
        lines.append(f'- LFO2: {lfo2_wave}, Freq={lfo2_freq}')
        lines.append('')
        lines.append('FX:')
        lines.append(f'- Delay: {delay_type}, Time={delay_time}, Depth={delay_depth}')
        lines.append(f'- Mod:   {mod_type}, Speed={mod_speed}, Depth={mod_depth}')
        lines.append('')
        lines.append('Arpeggiator:')
        lines.append(f'- {"ON" if arp_on else "OFF"}, Type={arp_type}, Range={arp_range} oct, Tempo={arp_tempo}')
        lines.append('')
    lines.append('')
    return '\n'.join(lines)


def main() -> int:
    patches = decode()
    md = generate_md(patches)
    out = project_root() / 'implementations/korg/ms2000/patches/BoardsOfCanada/BOCSunday_DETAILED_REFERENCE.md'
    out.write_text(md)
    print(f'Wrote {out} (all patches)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
