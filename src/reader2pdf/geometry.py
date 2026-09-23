"""Paper sizes and rectangle geometry used to select an aspect-locked capture region."""

from dataclasses import dataclass
from enum import Enum


class Orientation(Enum):
    """Page orientation of the capture region."""

    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"


class PaperSize(Enum):
    """Supported paper sizes, valued as (short side, long side) in millimetres."""

    A4 = (210.0, 297.0)
    B3 = (353.0, 500.0)

    @property
    def short_mm(self) -> float:
        """Length of the short side in millimetres."""
        return self.value[0]

    @property
    def long_mm(self) -> float:
        """Length of the long side in millimetres."""
        return self.value[1]

    def size_mm(self, orientation: Orientation) -> tuple[float, float]:
        """Returns (width, height) in millimetres for the given orientation."""
        if orientation is Orientation.PORTRAIT:
            return (self.short_mm, self.long_mm)
        return (self.long_mm, self.short_mm)

    def aspect_ratio(self, orientation: Orientation) -> float:
        """Returns width / height for the given orientation."""
        width, height = self.size_mm(orientation)
        return width / height


@dataclass(frozen=True)
class Rect:
    """Axis-aligned rectangle in physical screen pixels."""

    left: int
    top: int
    width: int
    height: int

    @property
    def right(self) -> int:
        """Exclusive right edge."""
        return self.left + self.width

    @property
    def bottom(self) -> int:
        """Exclusive bottom edge."""
        return self.top + self.height

    def contains(self, x: int, y: int) -> bool:
        """Returns whether the point lies inside this rectangle."""
        return self.left <= x < self.right and self.top <= y < self.bottom


def fit_aspect(start: tuple[int, int], end: tuple[int, int], aspect_ratio: float) -> Rect:
    """Builds the largest aspect-locked rect spanning from start towards end.

    Args:
        start: The point where the drag began; stays fixed as a corner.
        end: The current pointer position; bounds the rect.
        aspect_ratio: Required width / height.
    """
    dx = end[0] - start[0]
    dy = end[1] - start[1]

    # shrink whichever side overshoots the ratio
    width = min(abs(dx), round(abs(dy) * aspect_ratio))
    height = round(width / aspect_ratio)

    left = start[0] if dx >= 0 else start[0] - width
    top = start[1] if dy >= 0 else start[1] - height
    return Rect(left, top, width, height)
