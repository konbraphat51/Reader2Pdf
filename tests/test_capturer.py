from reader2pdf.capturer import MssCapturer
from reader2pdf.geometry import Rect


def test_capture_returns_requested_size() -> None:
    capturer = MssCapturer()
    screen = capturer.virtual_screen()
    image = capturer.capture(Rect(screen.left, screen.top, 40, 30))
    assert image.size == (40, 30)
    assert image.mode == "RGB"
