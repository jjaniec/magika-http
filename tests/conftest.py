"""
Shared pytest fixtures for magika-http tests.
"""

import io
import os
import sys

import pytest
from fastapi.testclient import TestClient

# Add src/ to path so imports resolve without installing the package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from main import app  # noqa: E402


@pytest.fixture(scope="session")
def client() -> TestClient:
    """Reusable synchronous test client (model loaded once per session)."""
    with TestClient(app) as c:
        yield c


# ---------------------------------------------------------------------------
# Sample file fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def python_file() -> tuple[str, io.BytesIO, str]:
    """A Python source snippet."""
    content = b"def hello():\n    print('hello world')\n"
    return ("hello.py", io.BytesIO(content), "application/octet-stream")


@pytest.fixture
def png_file() -> tuple[str, io.BytesIO, str]:
    """Minimal valid PNG header (1x1 white pixel)."""
    # PNG magic bytes + minimal IHDR
    png_bytes = (
        b"\x89PNG\r\n\x1a\n"  # PNG signature
        b"\x00\x00\x00\rIHDR"  # IHDR chunk length + type
        b"\x00\x00\x00\x01"  # width = 1
        b"\x00\x00\x00\x01"  # height = 1
        b"\x08\x02"  # bit depth = 8, color type = RGB
        b"\x00\x00\x00"  # compression, filter, interlace
        b"\x90wS\xde"  # CRC
        b"\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N"
        b"\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    return ("image.png", io.BytesIO(png_bytes), "application/octet-stream")


@pytest.fixture
def pdf_file() -> tuple[str, io.BytesIO, str]:
    """Minimal but structurally complete PDF so Magika can identify it."""
    content = (
        b"%PDF-1.4\n"
        b"%\xe2\xe3\xcf\xd3\n"
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>\nendobj\n"
        b"xref\n0 4\n0000000000 65535 f \n"
        b"trailer\n<< /Size 4 /Root 1 0 R >>\n"
        b"startxref\n%%EOF\n"
    )
    return ("document.pdf", io.BytesIO(content), "application/octet-stream")


@pytest.fixture
def empty_file() -> tuple[str, io.BytesIO, str]:
    """Empty file."""
    return ("empty.bin", io.BytesIO(b""), "application/octet-stream")
