from pathlib import Path

import pytest
from PIL import Image

from reader2pdf.geometry import Orientation, PaperSize
from reader2pdf.pdf_exporter import PdfExporter


def test_export_writes_all_pages(tmp_path: Path) -> None:
    pages = [Image.new("RGB", (210, 297), color) for color in ("red", "blue", "green")]
    out = tmp_path / "sub" / "book.pdf"
    PdfExporter(PaperSize.A4, Orientation.PORTRAIT).export(pages, out)

    data = out.read_bytes()
    assert data.startswith(b"%PDF")
    assert b"/Count 3" in data


def test_export_rejects_empty(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        PdfExporter(PaperSize.A4, Orientation.PORTRAIT).export([], tmp_path / "x.pdf")
