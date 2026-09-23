"""OS-specific process setup that must run before any window is created."""

import ctypes
import sys

_PER_MONITOR_DPI_AWARE = 2


def enable_dpi_awareness() -> None:
    """Makes Tk, mss and pynput all use physical pixels on scaled Windows displays."""
    if sys.platform != "win32":
        return
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(_PER_MONITOR_DPI_AWARE)
    except (AttributeError, OSError):
        ctypes.windll.user32.SetProcessDPIAware()
