from pathlib import Path

from reader2pdf.__main__ import parse_args
from reader2pdf.geometry import Orientation, PaperSize
from reader2pdf.i18n import Language


def test_parse_args_defaults() -> None:
    config = parse_args([])
    assert config.paper is PaperSize.A4
    assert config.orientation is Orientation.PORTRAIT
    assert config.capture_delay_s == 0
    assert config.output.suffix == ".pdf"


def test_parse_args_options() -> None:
    config = parse_args(
        ["--paper", "B3", "--orientation", "landscape", "--output", "a.pdf", "--lang", "ja"]
    )
    assert config.paper is PaperSize.B3
    assert config.orientation is Orientation.LANDSCAPE
    assert config.output == Path("a.pdf")
    assert config.language is Language.JA
