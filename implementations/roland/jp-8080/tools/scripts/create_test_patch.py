#!/usr/bin/env python3
"""
Create a test patch for JP-8080 implementation testing.

This creates a minimal valid patch with known parameter values
for testing the encode/decode functionality.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add parent directories to path for imports
tools_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(tools_dir))
sys.path.insert(0, str(tools_dir / "lib"))

from jp8080_core import encode_patch_to_sysex, PATCH_SIZE  # type: ignore


def create_test_patch() -> bytes:
    """Create a minimal test patch with known values."""

    patch_data = bytearray(PATCH_SIZE)

    # Patch name (16 bytes): "Test Patch      "
    name = "Test Patch      "
    for i, char in enumerate(name[:16]):
        patch_data[i] = ord(char)

    # LFO1 settings
    patch_data[0x10] = 0x01  # LFO1 Waveform: Saw
    patch_data[0x11] = 0x40  # LFO1 Rate: 64
    patch_data[0x12] = 0x00  # LFO1 Fade: 0

    # LFO2 settings
    patch_data[0x13] = 0x50  # LFO2 Rate: 80
    patch_data[0x14] = 0x02  # LFO2 Depth Select: Amplifier

    # Modulation
    patch_data[0x15] = 0x00  # Ring Mod: OFF
    patch_data[0x16] = 0x30  # Cross Mod Depth: 48
    patch_data[0x17] = 0x40  # Osc Balance: 0 (center)
    patch_data[0x18] = 0x00  # LFO/Env Dest: OSC1+2

    # OSC1
    patch_data[0x1E] = 0x00  # OSC1 Waveform: SuperSaw
    patch_data[0x1F] = 0x7F  # OSC1 Ctrl1: 127
    patch_data[0x20] = 0x40  # OSC1 Ctrl2: 64

    # OSC2
    patch_data[0x21] = 0x02  # OSC2 Waveform: Saw
    patch_data[0x22] = 0x00  # OSC2 Sync: OFF
    patch_data[0x23] = 0x19  # OSC2 Range: 0 (center = 0x19)
    patch_data[0x24] = 0x32  # OSC2 Fine: 0 (center = 50 = 0x32)
    patch_data[0x25] = 0x40  # OSC2 Ctrl1: 64
    patch_data[0x26] = 0x40  # OSC2 Ctrl2: 64

    # Filter
    patch_data[0x27] = 0x02  # Filter Type: LPF
    patch_data[0x28] = 0x01  # Filter Slope: -24dB
    patch_data[0x29] = 0x55  # Cutoff: 85
    patch_data[0x2A] = 0x40  # Resonance: 64
    patch_data[0x2B] = 0x40  # Key Follow: 0 (center)

    # Filter EG (EG1)
    patch_data[0x2F] = 0x00  # Attack: 0
    patch_data[0x30] = 0x40  # Decay: 64
    patch_data[0x31] = 0x50  # Sustain: 80
    patch_data[0x32] = 0x30  # Release: 48

    # Amp
    patch_data[0x33] = 0x7F  # Level: 127

    # Amp EG (EG2)
    patch_data[0x36] = 0x00  # Attack: 0
    patch_data[0x37] = 0x20  # Decay: 32
    patch_data[0x38] = 0x7F  # Sustain: 127
    patch_data[0x39] = 0x20  # Release: 32

    # Pan and Tone
    patch_data[0x3A] = 0x00  # Pan Mode: Off
    patch_data[0x3B] = 0x40  # Bass: 0 (center)
    patch_data[0x3C] = 0x40  # Treble: 0 (center)

    # Effects
    patch_data[0x3D] = 0x00  # Multi FX: Super Chorus Slow
    patch_data[0x3E] = 0x40  # Multi FX Level: 64
    patch_data[0x3F] = 0x01  # Delay Type: Delay
    patch_data[0x40] = 0x40  # Delay Time: 64
    patch_data[0x41] = 0x30  # Delay Feedback: 48
    patch_data[0x42] = 0x40  # Delay Level: 64

    # Pitch Bend
    patch_data[0x43] = 0x02  # Bend Range Up: 2 semitones
    patch_data[0x44] = 0x02  # Bend Range Down: 2 semitones

    # Voice settings
    patch_data[0x45] = 0x00  # Portamento: OFF
    patch_data[0x46] = 0x00  # Portamento Time: 0
    patch_data[0x47] = 0x00  # Mono: OFF
    patch_data[0x48] = 0x00  # Legato: OFF
    patch_data[0x49] = 0x02  # Osc Shift: 0 (center = 2)

    # Unison and other settings
    # Note: Roland addresses like "00 00 01 73" decode to: (1<<7) + 0x73 = 128 + 115 = 243
    patch_data[243] = 0x00  # Unison: OFF (addr: 00 00 01 73)
    patch_data[244] = 0x00  # Unison Detune: 0 (addr: 00 00 01 74)
    patch_data[245] = 0x00  # Patch Gain: 0dB (addr: 00 00 01 75)
    patch_data[246] = 0x00  # Ext Trigger: OFF (addr: 00 00 01 76)
    patch_data[247] = 0x00  # Ext Trigger Dest: Filter (addr: 00 00 01 77)

    return bytes(patch_data)


def main() -> int:
    # Create test patch data
    patch_data = create_test_patch()

    # Encode to SysEx with User Patch A11 address
    address = 0x02000000  # User Patch A11
    sysex_data = encode_patch_to_sysex(patch_data, address)

    # Write to file
    output_dir = Path(__file__).parent.parent.parent / "examples"
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / "test_patch.syx"
    output_file.write_bytes(sysex_data)

    print(f"Created test patch: {output_file}")
    print(f"  Patch name: Test Patch")
    print(f"  Address: 0x{address:08X} (User Patch A11)")
    print(f"  Size: {len(sysex_data)} bytes")
    print(f"  Patch data: {len(patch_data)} bytes")

    return 0


if __name__ == "__main__":
    sys.exit(main())
