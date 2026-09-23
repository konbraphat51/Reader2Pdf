"""Orchestrates region selection, click-driven capturing and PDF export."""

import queue
import threading
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from tkinter import messagebox

from PIL.Image import Image

from reader2pdf.capturer import ScreenCapturer
from reader2pdf.geometry import Orientation, PaperSize, Rect
from reader2pdf.i18n import Language, Translator
from reader2pdf.input_listener import InputListener, KeyCommand
from reader2pdf.pdf_exporter import PdfExporter
from reader2pdf.preview_window import PreviewWindow
from reader2pdf.region_frame import RegionFrame
from reader2pdf.region_selector import RegionSelection, RegionSelector
from reader2pdf.session import CaptureSession

_POLL_INTERVAL_MS = 20


@dataclass(frozen=True)
class AppConfig:
    """User options for one run."""

    paper: PaperSize
    orientation: Orientation
    capture_delay_s: float
    """Seconds between a click and its capture; 0 captures at the moment of the press."""
    output: Path
    language: Language


type _Event = Image | KeyCommand
"""Message from the hook threads to the Tk thread: a captured page or a key command."""


class Reader2PdfApp:
    """Runs one capture session from region selection to the saved PDF."""

    def __init__(self, config: AppConfig, capturer: ScreenCapturer) -> None:
        self._config = config
        self._capturer = capturer
        self._t = Translator(config.language)
        self._session = CaptureSession()
        self._events: queue.Queue[_Event] = queue.Queue()
        self._root = tk.Tk()
        self._root.withdraw()
        self._ignored_area = Rect(0, 0, 0, 0)
        self._saved_path: Path | None = None

    def run(self) -> Path | None:
        """Runs the whole session; returns the saved PDF path, or None if nothing was saved."""
        selection = self._select_region()
        if selection is None:
            print(self._t("cancelled"))
            self._root.destroy()
            return None

        self._start_capturing(selection)
        self._root.mainloop()
        return self._saved_path

    def _select_region(self) -> RegionSelection | None:
        screen = self._capturer.virtual_screen()
        selector = RegionSelector(
            self._root,
            self._t,
            screen,
            self._capturer.monitors(),
            self._capturer.capture(screen),
            self._config.paper,
            self._config.orientation,
        )
        return selector.select()

    def _start_capturing(self, selection: RegionSelection) -> None:
        self._region = selection.rect
        self._exporter = PdfExporter(selection.paper, selection.orientation)
        self._frame = RegionFrame(self._root, selection.rect)
        self._preview = PreviewWindow(self._root, self._t)
        self._preview.place_beside(selection.rect, self._monitor_of(selection.rect))

        self._listener = InputListener(self._on_click, self._events.put)
        self._listener.start()
        self._root.after(_POLL_INTERVAL_MS, self._poll)

    def _monitor_of(self, rect: Rect) -> Rect:
        """Returns the monitor containing the centre of rect, or the whole virtual screen."""
        centre = (rect.left + rect.width // 2, rect.top + rect.height // 2)
        for monitor in self._capturer.monitors():
            if monitor.contains(*centre):
                return monitor
        return self._capturer.virtual_screen()

    def _on_click(self, x: int, y: int) -> None:
        """Hook-thread handler: captures the region unless the click hit the preview window."""
        if self._ignored_area.contains(x, y):
            return
        delay = self._config.capture_delay_s
        if delay <= 0:
            self._capture()
        else:
            threading.Timer(delay, self._capture).start()

    def _capture(self) -> None:
        self._events.put(self._capturer.capture(self._region))

    def _poll(self) -> None:
        """Tk-thread loop: applies queued events and refreshes the ignored area."""
        self._ignored_area = self._preview.bounds()
        while True:
            try:
                event = self._events.get_nowait()
            except queue.Empty:
                break
            if event is KeyCommand.FINISH:
                self._finish()
                return
            if event is KeyCommand.DELETE_LAST:
                self._session.remove_last()
            elif not isinstance(event, KeyCommand):
                self._session.add(event)
            self._preview.show(self._session.last, self._session.count)
        self._root.after(_POLL_INTERVAL_MS, self._poll)

    def _finish(self) -> None:
        self._listener.stop()
        self._frame.destroy()
        self._preview.destroy()

        if self._session.count == 0:
            message = self._t("nothing_to_save")
        else:
            self._exporter.export(self._session.pages, self._config.output)
            self._saved_path = self._config.output
            message = self._t("saved", count=self._session.count, path=self._config.output)

        print(message)
        messagebox.showinfo("Reader2Pdf", message, parent=self._root)
        self._root.destroy()
