"""Window that shows the most recent capture and the session status."""

import tkinter as tk

from PIL import ImageTk
from PIL.Image import Image

from reader2pdf.geometry import Rect
from reader2pdf.i18n import Translator

_MAX_PREVIEW_PX = (420, 560)


class PreviewWindow:
    """Displays the last captured page, the page count and the key bindings."""

    def __init__(self, root: tk.Tk, translate: Translator) -> None:
        self._t = translate
        self._window = tk.Toplevel(root)
        self._window.title(translate("preview_title"))
        self._window.attributes("-topmost", True)
        self._window.resizable(False, False)
        # a 1px image makes the label size itself in pixels rather than characters
        self._blank = tk.PhotoImage(width=1, height=1)

        self._image_label = tk.Label(
            self._window,
            text=translate("no_capture"),
            width=_MAX_PREVIEW_PX[0],
            height=_MAX_PREVIEW_PX[1],
            image=self._blank,
            compound=tk.CENTER,
            background="#303030",
            foreground="#ffffff",
        )
        self._image_label.pack(padx=8, pady=(8, 4))
        self._status_label = tk.Label(self._window, anchor=tk.W)
        self._status_label.pack(fill=tk.X, padx=8, pady=(0, 8))
        self._photo: ImageTk.PhotoImage | None = None
        self.show(None, 0)

    def place_beside(self, rect: Rect, screen: Rect) -> None:
        """Moves the window next to rect, on whichever side has room, so it is not captured."""
        self._window.update_idletasks()
        width = self._window.winfo_reqwidth()
        margin = 16
        left = rect.right + margin
        if left + width > screen.right:
            left = max(screen.left, rect.left - margin - width)
        self._window.geometry(f"+{left}+{rect.top}")

    def show(self, page: Image | None, count: int) -> None:
        """Shows page (or the placeholder when None) and the current page count."""
        if page is None:
            self._photo = None
            self._image_label.configure(image=self._blank, text=self._t("no_capture"))
        else:
            thumbnail = page.copy()
            thumbnail.thumbnail(_MAX_PREVIEW_PX)
            self._photo = ImageTk.PhotoImage(thumbnail)
            self._image_label.configure(image=self._photo, text="")
        self._status_label.configure(text=self._t("status", count=count))

    def bounds(self) -> Rect:
        """Screen rect currently covered by the window, including its frame and title bar."""
        w = self._window
        border = w.winfo_rootx() - w.winfo_x()
        right = w.winfo_rootx() + w.winfo_width() + border
        bottom = w.winfo_rooty() + w.winfo_height() + border
        return Rect(w.winfo_x(), w.winfo_y(), right - w.winfo_x(), bottom - w.winfo_y())

    def destroy(self) -> None:
        """Closes the window."""
        self._window.destroy()
