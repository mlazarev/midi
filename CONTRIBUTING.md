# Contributing to MIDI SysEx Learning

First off, thank you for considering contributing to this project! It's people like you that make this a great learning resource for the MIDI and synthesizer community.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Style Guidelines](#style-guidelines)
- [Project Structure](#project-structure)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

This project aims to be welcoming and inclusive. Please:
- Be respectful and constructive
- Focus on education and learning
- Help others understand MIDI and SysEx
- Respect intellectual property and licensing

## How Can I Contribute?

### 🐛 Reporting Bugs

Before creating bug reports, please check existing issues. When creating a bug report, include:

- **Clear title** - Concise description of the issue
- **Steps to reproduce** - Detailed steps to reproduce the behavior
- **Expected behavior** - What you expected to happen
- **Actual behavior** - What actually happened
- **Environment** - OS, Python version, etc.
- **Sample files** - If applicable (ensure you have rights to share)

### 💡 Suggesting Enhancements

Enhancement suggestions are welcome! Include:

- **Use case** - Why would this be useful?
- **Proposed solution** - How might it work?
- **Alternatives** - Other approaches you considered
- **Examples** - Similar features in other tools

### 📝 Documentation Improvements

Documentation contributions are highly valued:

- Fix typos or clarify explanations
- Add examples or diagrams
- Improve tutorials and guides
- Translate to other languages
- Add missing technical details

### 🔧 Adding New Implementations

Want to add support for another synthesizer? Great!

1. Create directory: `implementations/<manufacturer>/<model>/`
2. Follow the MS2000 structure as a template
3. Include:
   - README.md with device info and usage
   - Decoder tool(s)
   - Example SysEx files (with proper licensing)
   - Documentation of SysEx format
   - MIDI implementation chart (if available)

### 🧪 Code Contributions

Code contributions should:

- Solve a specific problem or add a clear feature
- Follow the existing code style
- Include docstrings and comments
- Work with Python 3.7+
- Not require external dependencies (if possible)

## Development Setup

### Prerequisites

- Python 3.7 or higher
- Git
- Text editor or IDE

### Getting Started

1. **Fork the repository**
   ```bash
   # Click 'Fork' on GitHub
   ```

2. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR-USERNAME/midi-sysex-learning.git
   cd midi-sysex-learning
   ```

3. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bugfix-name
   ```

4. **Make your changes**
   ```bash
   # Edit files
   ```

5. **Test your changes**
   ```bash
   cd implementations/korg/ms2000/tools
   python3 decode_sysex.py ../patches/factory/FactoryBanks.syx
   ```

6. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add feature: description of your changes"
   ```

7. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

8. **Create Pull Request**
   - Go to your fork on GitHub
   - Click "Pull Request"
   - Describe your changes

## Style Guidelines

### Python Code

Follow PEP 8 with these specifics:

```python
# Imports
import sys
from pathlib import Path

# Constants
MANUFACTURER_ID = 0x42
DEVICE_ID = 0x58

# Functions - clear docstrings
def decode_sysex(data):
    """
    Decode SysEx data using 7-to-8 bit algorithm.

    Args:
        data: bytes object containing encoded data

    Returns:
        bytes object containing decoded data
    """
    # Implementation with comments explaining complex logic
    pass

# Classes - clear structure
class Patch:
    """Represents a synthesizer patch."""

    def __init__(self, data):
        """Initialize patch from raw data."""
        self.data = data
        self.parse()
```

### Documentation

- Use **Markdown** for all documentation
- Include **code examples** where helpful
- Add **diagrams** for complex concepts (ASCII art is fine)
- **Link** between related documents
- Keep **line length** under 100 characters for readability

### Commit Messages

Use clear, descriptive commit messages:

```
Add MS2000 parameter decoder for oscillator section

- Decode OSC1 and OSC2 waveform settings
- Extract pitch and modulation parameters
- Add constants for waveform types
- Update documentation with oscillator byte map
```

Format:
- First line: Brief summary (50 chars or less)
- Blank line
- Detailed description (wrapped at 72 chars)

## Project Structure

When adding new content, follow this structure:

```
midi-sysex-learning/
├── docs/
│   └── general/              # General MIDI/SysEx documentation
├── implementations/
│   └── <manufacturer>/
│       └── <model>/
│           ├── README.md     # Model-specific documentation
│           ├── docs/         # Technical specs
│           ├── tools/        # Python tools
│           ├── patches/      # Example SysEx files
│           └── examples/     # Example outputs
```

### File Naming

- **Python**: `lowercase_with_underscores.py`
- **Markdown**: `UPPERCASE_FOR_MAJOR.md` or `PascalCase.md`
- **SysEx**: `DescriptiveName.syx`
- **Docs**: `DESCRIPTIVE_NAME.txt` or `.md`

## Pull Request Process

1. **Update documentation** - If you change functionality, update relevant docs
2. **Add examples** - Show how your feature works
3. **Test thoroughly** - Ensure existing functionality still works
4. **Keep it focused** - One feature or fix per PR
5. **Describe changes** - Clear PR description with motivation

### PR Checklist

Before submitting, ensure:

- [ ] Code follows style guidelines
- [ ] Documentation is updated
- [ ] Examples are included
- [ ] No proprietary/licensed content included without permission
- [ ] No external dependencies added (or discussed first)
- [ ] Existing tests still pass
- [ ] Commit messages are clear

### Review Process

1. Maintainer reviews PR
2. Discussion and potential changes requested
3. You make updates
4. Approval and merge

Be patient - reviews may take a few days!

## Licensing

By contributing, you agree that your contributions will be licensed under the MIT License.

### Important Notes

- **Original code**: Your contributions should be your own work
- **Documentation**: Educational use of manufacturer specs is fair use
- **Sample files**: Only include files you have rights to share
- **Factory patches**: Public domain or with manufacturer permission only
- **Custom patches**: Only if you created them or have explicit permission

### Attribution

If you use or reference external sources:

1. Add attribution in the code/document
2. Ensure license compatibility
3. List in acknowledgments section

## Questions?

- **General questions**: Open a Discussion on GitHub
- **Specific issues**: Create an Issue
- **Quick questions**: Comment on related Issues/PRs

## Recognition

Contributors will be:
- Listed in repository contributors
- Mentioned in relevant documentation
- Credited in release notes

Thank you for helping make MIDI technology more accessible! 🎹🎛️

---

*Remember: The best contribution is one that helps someone learn.*
