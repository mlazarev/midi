# General MIDI + Korg MS2000 SysEx Tools, Banks, and BOC Patch Generation

Practical tools and curated content for Korg MS2000/MS2000R sound designers and developers:
- Generate, analyze, and send complete 128‑program banks
- Ship ready‑to‑use Boards of Canada–style banks
- Decode and export factory banks for inspection and tooling

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

## 🎯 What You Can Do Here

- Send banks to hardware quickly (single or full bank)
- Generate BOC‑inspired banks from code (with variety and safe parameter ranges)
- Analyze banks (FX usage, arp, naming, summary stats) and export JSON
- Inspect and modify patches at the byte level if needed

## 📚 Documentation (Focused)

Located in [`docs/general/`](docs/general/):

- **[LEARNING_SUMMARY.md](docs/general/LEARNING_SUMMARY.md)** - Complete educational guide
  - MIDI fundamentals and protocol
  - System Exclusive (SysEx) message structure
  - 7-to-8 bit encoding schemes
  - Practical decoding techniques
  - Real-world analysis examples

- **[QUICK_REFERENCE.md](docs/general/QUICK_REFERENCE.md)** - Fast-lookup reference
  - MIDI message tables
  - Manufacturer IDs
  - Control Change (CC) mappings
  - Bit manipulation formulas
  - Common code snippets

## 🔧 Korg MS2000/MS2000R

[![MS2000](https://img.shields.io/badge/Korg-MS2000-red)](implementations/korg/ms2000/)

Complete SysEx workflow for Korg MS2000: generator, decoder, analyzer, sender.

**Location:** [`implementations/korg/ms2000/`](implementations/korg/ms2000/)

**Highlights for sound designers:**
- Banks ready to send:
  - Factory: implementations/korg/ms2000/patches/factory/FactoryBanks.syx
  - Boards of Canada: implementations/korg/ms2000/patches/BoardsOfCanada/BOCSunday.syx
- BOCSunday generator creates 128‑program bank:
  - 16 handcrafted patches (A01–A16)
  - 112 additional varied patches (pads/leads/bass/keys/arp) influenced by Factory distributions
- Robust 7→8 encoding (variant v2) verified on hardware
- Tools for compare, analyze, JSON export, single‑program dumps

**Quick Start:**
```bash
cd implementations/korg/ms2000/tools
python3 decode_sysex.py ../patches/factory/FactoryBanks.syx
```

See [MS2000 README](implementations/korg/ms2000/README.md) for full documentation.

### Boards of Canada Example Banks

- BOCSunday.syx — new BOC bank: 16 handcrafted + 112 algorithmic patches
  - Generator: implementations/korg/ms2000/patches/BoardsOfCanada/create_boc_patches.py
  - Ready‑to‑send bank at: implementations/korg/ms2000/patches/BoardsOfCanada/BOCSunday.syx

Send to hardware:
```bash
python3 tools/send_sysex.py --file implementations/korg/ms2000/patches/BoardsOfCanada/BOCSunday.syx \
    --out "MS2000" --delay-ms 50
```

## 🏗️ Repository Structure

```
midi-sysex-learning/
├── README.md                          # This file
├── LICENSE                            # MIT License
├── .gitignore                         # Git ignore rules
│
├── docs/                              # General documentation
│   └── general/
│       ├── LEARNING_SUMMARY.md        # Complete MIDI/SysEx tutorial
│       └── QUICK_REFERENCE.md         # Quick lookup tables
│
└── implementations/                   # Device-specific implementations
    └── korg/                          # Korg manufacturer
        └── ms2000/                    # MS2000 synthesizer
            ├── README.md              # MS2000-specific documentation
            ├── docs/                  # Technical specifications
            ├── tools/                 # Python tools
            ├── patches/               # SysEx patch files
            └── examples/              # Example outputs
```

## 🚀 Getting Started (MS2000)

### Prerequisites

- Python 3.7 or higher
- No external dependencies (uses standard library only)

### Installation

Clone the repository:
```bash
git clone https://github.com/yourusername/midi-sysex-learning.git
cd midi-sysex-learning
```

### Basic Usage

**1. Learn MIDI fundamentals:**
```bash
# Read the learning guide
cat docs/general/LEARNING_SUMMARY.md
```

**2. Decode a SysEx file (Factory):**
```bash
python3 implementations/korg/ms2000/tools/ms2000_cli.py \
        inspect implementations/korg/ms2000/patches/factory/FactoryBanks.syx --limit 8
```

**3. Compare two patch banks:**
```bash
python3 implementations/korg/ms2000/tools/ms2000_cli.py compare file1.syx file2.syx
```

**4. Send a SysEx file to hardware:**
```bash
# List MIDI outputs
python3 implementations/korg/ms2000/tools/scripts/send_to_ms2000.py --list-outputs

# Send a .syx file (requires 'mido' + 'python-rtmidi')
python3 implementations/korg/ms2000/tools/scripts/send_to_ms2000.py \
    --file implementations/korg/ms2000/patches/factory/FactoryBanks.syx \
    --out "MS2000" --delay-ms 50
```

## 📖 Learning Path (Optional)

For newcomers to MIDI and SysEx, we recommend this progression:

1. **Start with basics** → [LEARNING_SUMMARY.md](docs/general/LEARNING_SUMMARY.md)
   - Read sections 1-2 (MIDI Fundamentals, SysEx Messages)
   - Understand the 7-bit limitation and why encoding is needed

2. **Study a real implementation** → [MS2000 Implementation](implementations/korg/ms2000/)
   - Examine the SysEx file structure
   - Run the decoder on factory patches
   - Study the decoded output

3. **Deep dive** → Read the decoder source code
   - [`decode_sysex.py`](implementations/korg/ms2000/tools/wrappers/decode_sysex.py)
   - Understand 7-to-8 bit decoding algorithm
   - See how patch parameters are extracted

4. **Reference as needed** → [QUICK_REFERENCE.md](docs/general/QUICK_REFERENCE.md)
   - Look up message formats
   - Find bit manipulation formulas
   - Check manufacturer IDs

## 🎓 What You'll Learn (Optional)

- ✅ MIDI protocol fundamentals (status/data bytes, channels, messages)
- ✅ System Exclusive (SysEx) message structure and purpose
- ✅ Manufacturer-specific implementations
- ✅ Binary data encoding schemes (7-to-8 bit packing)
- ✅ Hexadecimal and binary number systems
- ✅ File format analysis and reverse engineering
- ✅ Building practical MIDI tools in Python

## 🛠️ Use Cases

### Sound Designers
- Backup and organize synthesizer patches
- Analyze factory presets to learn sound design
- Share patch banks with collaborators
- Archive sounds from specific projects

### Developers
- Build patch librarian applications
- Create automated testing tools
- Develop patch editors with GUIs
- Implement MIDI-to-audio renderers

### Educators (Optional)
- Teach synthesis and MIDI concepts
- Demonstrate data encoding techniques
- Show real-world protocol implementation
- Provide hands-on learning materials

### Researchers (Optional)
- Study parameter distributions in sound banks
- Analyze relationships between parameters and timbre
- Extract features for machine learning
- Document vintage equipment specifications

## 🔬 Technical Highlights

### 7→8 Bit Encoding (Korg variant v2)

One of the key concepts demonstrated in this project is Korg's 7-to-8 bit encoding:

```python
def decode_korg_7bit(encoded_data):
    """
    MIDI restricts data bytes to 0-127 (bit 7 = 0).
    To transmit 8-bit data (0-255), Korg packs:
    - 7 bytes of 8-bit data → 8 bytes of 7-bit MIDI data
    - First byte contains MSBs (bit 7) of next 7 bytes
    - Remaining 7 bytes contain lower 7 bits
    """
    decoded = bytearray()
    i = 0
    while i + 8 <= len(encoded_data):
        msb_byte = encoded_data[i]
        for j in range(7):
            lower_7 = encoded_data[i + 1 + j] & 0x7F
            # Note: hardware here uses variant v2 (MSB of byte j in bit j)
            msb = (msb_byte >> (6 - j)) & 0x01
            full_byte = (msb << 7) | lower_7
            decoded.append(full_byte)
        i += 8
    return bytes(decoded)
```

This adds ~14.3% overhead while maintaining MIDI compatibility.

## 🤝 Contributing

Contributions are welcome! Here are some ideas:

### New Implementations
- Add support for other synthesizers (Roland, Yamaha, Sequential, etc.)
- Implement bidirectional MIDI communication
- Create real-time parameter editors

### Documentation
- Add more visual diagrams
- Create video tutorials
- Translate to other languages
- Document additional MIDI features (NRPN, MPE, etc.)

### Tools
- Build GUI applications
- Add patch randomization/generation
- Implement parameter interpolation
- Create audio feature to parameter mapping

### Testing
- Add unit tests for decoder
- Test with more SysEx files
- Validate against hardware

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

**Important Notes:**
- Educational documentation and tools: MIT License (open source)
- Device specifications: Property of respective manufacturers (educational use)
- Factory patches: Property of manufacturers (archival/educational purposes)
- Custom/commercial patches: Respect original licensing

## 🙏 Acknowledgments

- **MIDI Specification** - MIDI Manufacturers Association
- **Korg** - MS2000 MIDI Implementation documentation
- **Sound on Sound** - Educational articles on SysEx
- **Open source community** - Python, Git, and various tools

## 📚 Resources

### Official Specifications
- [MIDI Association](https://www.midi.org/) - Official MIDI specs and resources
- [MIDI 1.0 Specification](https://www.midi.org/specifications/midi1-specifications)

### Learning Resources
- [MIDI Implementation Chart Guide](https://www.midi.org/specifications/midi1-specifications/midi-1-addenda/midi-implementation-chart-instructions)
- This project's [Learning Summary](docs/general/LEARNING_SUMMARY.md)

### Related Projects
- [python-rtmidi](https://github.com/SpotlightKid/python-rtmidi) - Python MIDI I/O
- [mido](https://github.com/mido/mido) - MIDI objects for Python
- [SendMIDI/ReceiveMIDI](https://github.com/gbevin/SendMIDI) - Command-line MIDI tools

## 🗺️ Roadmap

### Current Status
- ✅ Complete MIDI/SysEx educational documentation
- ✅ Korg MS2000 implementation with tools
- ✅ 7-to-8 bit encoding/decoding
- ✅ Patch parameter extraction (partial)

### Planned
- ⬜ Complete MS2000 parameter decoder (all 254 bytes)
- ⬜ Add more synthesizer implementations
- ⬜ GUI patch editor
- ⬜ Bidirectional MIDI communication
- ⬜ MIDI 2.0 support
- ⬜ Interactive web-based tools

## 💬 Contact & Support

- **Issues:** Use [GitHub Issues](https://github.com/yourusername/midi-sysex-learning/issues) for bugs and feature requests
- **Discussions:** For questions and discussions
- **Pull Requests:** Welcome! Please follow existing code style

---

**Made with ❤️ for the MIDI and synthesizer community**

*Learn by doing. Understand by building.*
