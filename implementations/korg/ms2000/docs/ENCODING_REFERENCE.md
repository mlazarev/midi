# Korg MS2000 - Encoding Reference

## SysEx Format
- Header: `F0 42 3g 58 4C`
- Patch size (decoded): 254 bytes
- Encoding: Korg 7-to-8 bit packing (variant v2)
- Terminator: `F7`
- Checksum: None (bank dumps rely on transport integrity)

## Encoding Schemes

### Offset-64 Parameters
- **Notation in docs:** `64+/-X=0+/-X`, `0~64~127=L64~CNT~R63`
- **Formula:** `byte = value + 64`, `value = byte - 64`
- **Range validation:** `min_val <= value <= max_val`
- **Patch offsets:**
  - `+13` — `timbreX.osc2.semitone` (min -24, max +24)
  - `+14` — `timbreX.osc2.tune` (min -63, max +63)
  - `+22` — `timbreX.filter.eg1_intensity` (min -63, max +63)
  - `+23` — `timbreX.filter.velocity_sense` (min -63, max +63)
  - `+24` — `timbreX.filter.kbd_track` (min -63, max +63)
  - `+26` — `timbreX.amp.panpot` (min -64, max +63)
  - `+28` — `timbreX.amp.velocity_sense` (min -63, max +63)
  - `+29` — `timbreX.amp.kbd_track` (min -63, max +63)
  - `+45 + (patch * 2)` — `timbreX.patch.patch{1-4}.intensity` (min -63, max +63)

### Unsigned Parameters
- **Notation:** `0~127`, specific scalar ranges in documentation.
- **Formula:** `byte = value`, `value = byte`
- **Examples:**
  - Filter `cutoff`, `resonance`
  - FX `delay_time`, `delay_depth`, `mod_depth`
  - Mixer levels (`osc1_level`, `osc2_level`, `noise_level`)
  - Envelope rates/levels (`eg1.*`, `eg2.*`)

### Nibble / Bit-Packed Fields
- **Notation:** `B0~3`, `B4~7`, bit tables in doc.
- **Examples:**
  - Byte `+16`: bits 6-7 select `timbre_voice`, bits 4-5 select `voice_mode`.
  - Byte `+17`: bits 4-7 `scale_key`, bits 0-3 `scale_type`.
  - Byte `+19`: bit 7 delay sync flag, bits 0-3 delay timebase.
  - Byte `+33`: low nibble arpeggiator type, high nibble (`+1`) range (stored as 0-based, add 1 in decoder).

### Multi-Byte Values
- **Arpeggiator tempo:** `+30` (MSB) and `+31` (LSB) store BPM as 16-bit big-endian.
- **Motion/Vocoder blocks:** Not yet surfaced; preserved raw in `system.base_patch`.

## Helper Functions
- `_to_offset64` / `_from_offset64` (see `tools/lib/ms2000_core.py:822-832`)
- `_write_masked` manages nibble-wise updates without disturbing packed neighbours.
- `decode_korg_7bit` / `encode_korg_7bit` implement the Korg packing variant v2.

## Edge-Case Tests to Maintain
- [ ] `value 0` ↔ `byte 64` for every offset-64 field.
- [ ] Roundtrip for min/max: `-64` ↔ `0`, `+63` ↔ `127`.
- [ ] OSC2 semitone musical intervals (±12, ±7) encode correctly.
- [ ] Mod matrix intensities survive decode→encode without drift.

## Observations
- MS2000 never sets the MSB of packed parameter bytes; all ranges fit 7-bit transport when offset is applied.
- Signed 7-bit (two's complement) does **not** appear anywhere in the official spec.
- Any addition of new parameters must extend this reference so future implementations stay aligned with documentation.
