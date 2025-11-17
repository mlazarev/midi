import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
TOOLS_DIR = ROOT / "implementations" / "roland" / "jp-8080" / "tools"
LIB_DIR = TOOLS_DIR / "lib"

for entry in (TOOLS_DIR, LIB_DIR):
    if str(entry) not in sys.path:
        sys.path.insert(0, str(entry))

from jp8080_core import (  # type: ignore  # noqa: E402
    encode_roland_sysex,
    load_patch_from_sysex,
    PATCH_SIZE,
)


TEST_PATCH = ROOT / "implementations" / "roland" / "jp-8080" / "examples" / "test_patch.syx"


@pytest.fixture(scope="module")
def reference_patch_bytes():
    """Return the canonical JP-8080 patch bytes used for test synthesis."""
    _, patch, _ = load_patch_from_sysex(TEST_PATCH)
    return patch.raw_data


def test_load_patch_handles_jp8000_temp_multi_message(tmp_path, reference_patch_bytes):
    """JP-8000 style files split data into two DT1 packets – ensure we reassemble."""
    base = reference_patch_bytes
    main = base[:-9]  # JP-8000 temp dumps omit the last 9 bytes (unison/gain params)
    extension = base[-9:]

    temp_path = tmp_path / "jp8000_temp.syx"
    temp_path.write_bytes(
        encode_roland_sysex(0x01004000, main) + encode_roland_sysex(0x01004172, extension)
    )

    header, patch, address = load_patch_from_sysex(temp_path)
    assert address == 0x01004000
    assert patch.raw_data == base
    assert header.model_id == [0x00, 0x06]


def test_load_patch_pads_single_message_jp8000_payload(tmp_path, reference_patch_bytes):
    """Even if only the short payload is present, we should pad to PATCH_SIZE."""
    base = reference_patch_bytes
    truncated = base[:-9]

    temp_path = tmp_path / "jp8000_short.syx"
    temp_path.write_bytes(encode_roland_sysex(0x01004000, truncated))

    _, patch, _ = load_patch_from_sysex(temp_path)
    assert patch.raw_data[: len(truncated)] == truncated
    assert patch.raw_data[len(truncated) :] == bytes(PATCH_SIZE - len(truncated))
