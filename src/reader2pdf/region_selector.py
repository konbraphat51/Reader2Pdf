"""Full-screen overlay that lets the user drag out an aspect-locked capture region."""

import tkinter as tk
from dataclasses import dataclass

from PIL import ImageEnhance, ImageTk
from PIL.Image import Image

from reader2pdf.geometry import Orientation, PaperSize, Rect, fit_aspect
from reader2pdf.i18n import Translator

_OUTLINE_COLOR = "#ff3030"
_HINT_COLOR = "#ffffff"
_DIM_FACTOR = 0.45
_MIN_SIZE_PX = 20


@dataclass(frozen=True)
class RegionSelection:
    """The region chosen by the user together with the paper it represents."""

    rect: Rect
    paper: PaperSize
    orientation: Orientation


class RegionSelector:
    """Shows a dimmed, frozen screenshot and records a drag locked to the paper ratio.

    Keys while selecting: P cycles the paper size, O toggles the orientation, Esc cancels.
    """

    def __init__(
        self,
        root: tk.Tk,
        translate: Translator,
        screen: Rect,
        screenshot: Image,
        paper: PaperSize,
        orientation: Orientation,
    ) -> None:
        self._root = root
        self._t = translate
        self._screen = screen
        self._screenshot = screenshot
        self._paper = paper
        self._orientation = orientation
        self._start: tuple[int, int] | None = None
        self._current: Rect | None = None
        self._result: RegionSelection | None = None

    def select(self) -> RegionSelection | None:
        """Blocks until the user finishes a drag (returns it) or presses Esc (returns None)."""
        window = tk.Toplevel(self._root)
        window.overrideredirect(True)
        window.attributes("-topmost", True)
        s = self._screen
        window.geometry(f"{s.width}x{s.height}+{s.left}+{s.top}")

        canvas = tk.Canvas(window, highlightthickness=0, cursor="crosshair")
        canvas.pack(fill=tk.BOTH, expand=True)
        dimmed = ImageEnhance.Brightness(self._screenshot).enhance(_DIM_FACTOR)
        photo = ImageTk.PhotoImage(dimmed)
        canvas.create_image(0, 0, anchor=tk.NW, image=photo)
        self._outline = canvas.create_rectangle(0, 0, 0, 0, outline=_OUTLINE_COLOR, width=2)
        self._hint = canvas.create_text(
            s.width // 2, 30, fill=_HINT_COLOR, font=("Segoe UI", 16, "bold")
        )
        self._canvas = canvas
        self._window = window
        self._refresh_hint()

        canvas.bind("<ButtonPress-1>", self._on_press)
        canvas.bind("<B1-Motion>", self._on_drag)
        canvas.bind("<ButtonRelease-1>", self._on_release)
        window.bind("<Escape>", lambda _e: window.destroy())
        window.bind("<KeyPress-p>", lambda _e: self._cycle_paper())
        window.bind("<KeyPress-o>", lambda _e: self._toggle_orientation())

        window.focus_force()
        window.grab_set()
        window.wait_window()
        del photo
        return self._result

    def _to_screen(self, event: "tk.Event[tk.Canvas]") -> tuple[int, int]:
        return (event.x + self._screen.left, event.y + self._screen.top)

    def _on_press(self, event: "tk.Event[tk.Canvas]") -> None:
        self._start = self._to_screen(event)

    def _on_drag(self, event: "tk.Event[tk.Canvas]") -> None:
        if self._start is None:
            return
        self._current = fit_aspect(self._start, self._to_screen(event), self._ratio())
        self._redraw_outline()

    def _on_release(self, event: "tk.Event[tk.Canvas]") -> None:
        self._on_drag(event)
        rect = self._current
        self._start = None
        if rect is None or rect.width < _MIN_SIZE_PX or rect.height < _MIN_SIZE_PX:
            return
        self._result = RegionSelection(rect, self._paper, self._orientation)
        self._window.destroy()

    def _cycle_paper(self) -> None:
        papers = list(PaperSize)
        self._paper = papers[(papers.index(self._paper) + 1) % len(papers)]
        self._refresh_hint()

    def _toggle_orientation(self) -> None:
        self._orientation = (
            Orientation.LANDSCAPE
            if self._orientation is Orientation.PORTRAIT
            else Orientation.PORTRAIT
        )
        self._refresh_hint()

    def _ratio(self) -> float:
        return self._paper.aspect_ratio(self._orientation)

    def _refresh_hint(self) -> None:
        text = self._t(
            "select_hint", paper=self._paper.name, orientation=self._t(self._orientation.value)
        )
        self._canvas.itemconfigure(self._hint, text=text)

    def _redraw_outline(self) -> None:
        rect = self._current
        if rect is None:
            return
        left = rect.left - self._screen.left
        top = rect.top - self._screen.top
        self._canvas.coords(self._outline, left, top, left + rect.width, top + rect.height)
