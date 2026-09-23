"""Writes captured page images into a single PDF sized to the chosen paper."""

from pathlib import Path

from PIL.Image import Image

from reader2pdf.geometry import Orientation, PaperSize

_MM_PER_INCH = 25.4


class PdfExporter:
    """Exports page images as a PDF whose pages match a paper size."""

    def __init__(self, paper: PaperSize, orientation: Orientation) -> None:
        self._paper = paper
        self._orientation = orientation

    def export(self, pages: list[Image], path: Path) -> None:
        """Saves pages to path as one PDF, one image per page.

        Args:
            pages: Page images in output order; must not be empty.
            path: Destination file; parent directories are created.
        """
        if not pages:
            raise ValueError("pages must not be empty")

        path.parent.mkdir(parents=True, exist_ok=True)
        rgb_pages = [page.convert("RGB") for page in pages]
        first, rest = rgb_pages[0], rgb_pages[1:]
        first.save(
            path,
            "PDF",
            save_all=True,
            append_images=rest,
            resolution=self._resolution_dpi(first),
        )

    def _resolution_dpi(self, page: Image) -> float:
        """DPI that makes the page image span exactly the paper width."""
        width_mm, _ = self._paper.size_mm(self._orientation)
        return page.width / (width_mm / _MM_PER_INCH)
