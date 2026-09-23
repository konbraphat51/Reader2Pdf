"""Command-line entry point: parses options and launches the capture app."""

import argparse
from datetime import datetime
from pathlib import Path

from reader2pdf.app import AppConfig, Reader2PdfApp
from reader2pdf.capturer import MssCapturer
from reader2pdf.geometry import Orientation, PaperSize
from reader2pdf.i18n import Language
from reader2pdf.platform_setup import enable_dpi_awareness


def parse_args(argv: list[str] | None = None) -> AppConfig:
    """Builds the app configuration from command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="reader2pdf",
        description="Capture a screen region on every click and bundle the shots into a PDF.",
    )
    parser.add_argument("--paper", choices=[p.name for p in PaperSize], default="A4")
    parser.add_argument("--orientation", choices=[o.value for o in Orientation], default="portrait")
    parser.add_argument(
        "--delay",
        type=float,
        default=0.0,
        help="seconds to wait after a click before capturing (default: capture on press)",
    )
    parser.add_argument("--output", type=Path, default=None, help="destination PDF path")
    parser.add_argument("--lang", choices=[lang.value for lang in Language], default="en")
    args = parser.parse_args(argv)

    default_output = Path("output") / f"reader2pdf_{datetime.now():%Y%m%d_%H%M%S}.pdf"
    return AppConfig(
        paper=PaperSize[args.paper],
        orientation=Orientation(args.orientation),
        capture_delay_s=args.delay,
        output=args.output or default_output,
        language=Language(args.lang),
    )


def main() -> None:
    """Runs Reader2Pdf."""
    config = parse_args()
    enable_dpi_awareness()
    Reader2PdfApp(config, MssCapturer()).run()


if __name__ == "__main__":
    main()
