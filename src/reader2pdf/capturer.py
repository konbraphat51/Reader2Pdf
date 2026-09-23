"""Screen capture of a rectangular region into a Pillow image."""

from typing import Protocol

import mss
from PIL import Image as PilImage
from PIL.Image import Image

from reader2pdf.geometry import Rect


class ScreenCapturer(Protocol):
    """Captures a region of the screen."""

    def capture(self, rect: Rect) -> Image:
        """Returns the pixels inside rect, in physical screen pixels."""
        ...

    def virtual_screen(self) -> Rect:
        """Returns the bounding rect of all monitors combined."""
        ...

    def monitors(self) -> list[Rect]:
        """Returns the rect of each individual monitor."""
        ...


class MssCapturer:
    """ScreenCapturer backed by mss; safe to call from any thread."""

    def capture(self, rect: Rect) -> Image:
        """Returns the pixels inside rect, in physical screen pixels."""
        # a fresh mss instance per call because its handles are thread-bound
        with mss.MSS() as sct:
            shot = sct.grab(
                {"left": rect.left, "top": rect.top, "width": rect.width, "height": rect.height}
            )
        return PilImage.frombytes("RGB", shot.size, shot.bgra, "raw", "BGRX")

    def virtual_screen(self) -> Rect:
        """Returns the bounding rect of all monitors combined."""
        with mss.MSS() as sct:
            monitor = sct.monitors[0]
        return Rect(monitor["left"], monitor["top"], monitor["width"], monitor["height"])

    def monitors(self) -> list[Rect]:
        """Returns the rect of each individual monitor."""
        with mss.MSS() as sct:
            monitors = sct.monitors[1:]
        return [Rect(m["left"], m["top"], m["width"], m["height"]) for m in monitors]
