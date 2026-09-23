"""Always-on-top border drawn just outside the capture region so it never appears in shots."""

import tkinter as tk

from reader2pdf.geometry import Rect

_BORDER_COLOR = "#ff3030"
_THICKNESS_PX = 3


class RegionFrame:
    """Four thin borderless windows outlining a rect; clicks inside the rect pass through."""

    def __init__(self, root: tk.Tk, rect: Rect) -> None:
        self._edges: list[tk.Toplevel] = []
        t = _THICKNESS_PX
        outer_width = rect.width + 2 * t
        edge_rects = [
            Rect(rect.left - t, rect.top - t, outer_width, t),
            Rect(rect.left - t, rect.bottom, outer_width, t),
            Rect(rect.left - t, rect.top, t, rect.height),
            Rect(rect.right, rect.top, t, rect.height),
        ]
        for edge in edge_rects:
            self._edges.append(self._create_edge(root, edge))

    def destroy(self) -> None:
        """Removes the border from the screen."""
        for edge in self._edges:
            edge.destroy()
        self._edges.clear()

    @staticmethod
    def _create_edge(root: tk.Tk, rect: Rect) -> tk.Toplevel:
        edge = tk.Toplevel(root, background=_BORDER_COLOR)
        edge.overrideredirect(True)
        edge.attributes("-topmost", True)
        edge.geometry(f"{rect.width}x{rect.height}+{rect.left}+{rect.top}")
        return edge
