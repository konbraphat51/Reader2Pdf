"""Ordered store of the pages captured so far in one capture session."""

from PIL.Image import Image


class CaptureSession:
    """Keeps captured page images in capture order."""

    def __init__(self) -> None:
        self._pages: list[Image] = []

    @property
    def pages(self) -> list[Image]:
        """A copy of the captured pages, oldest first."""
        return list(self._pages)

    @property
    def count(self) -> int:
        """Number of captured pages."""
        return len(self._pages)

    @property
    def last(self) -> Image | None:
        """The most recent page, or None if nothing is captured."""
        return self._pages[-1] if self._pages else None

    def add(self, page: Image) -> None:
        """Appends a newly captured page."""
        self._pages.append(page)

    def remove_last(self) -> Image | None:
        """Removes and returns the most recent page, or None if empty."""
        return self._pages.pop() if self._pages else None
