import pytest

from reader2pdf.geometry import Orientation, PaperSize, Rect, fit_aspect


def test_aspect_ratio_orientation() -> None:
    assert PaperSize.A4.aspect_ratio(Orientation.PORTRAIT) == pytest.approx(210 / 297)
    assert PaperSize.B3.aspect_ratio(Orientation.LANDSCAPE) == pytest.approx(500 / 353)


@pytest.mark.parametrize("end", [(300, 1000), (1000, 300), (-300, -1000), (-1000, 300)])
def test_fit_aspect_keeps_ratio_and_stays_within_drag(end: tuple[int, int]) -> None:
    ratio = PaperSize.A4.aspect_ratio(Orientation.PORTRAIT)
    rect = fit_aspect((0, 0), end, ratio)
    assert rect.width / rect.height == pytest.approx(ratio, rel=0.01)
    assert rect.width <= abs(end[0])
    assert rect.height <= abs(end[1]) + 1


def test_fit_aspect_negative_direction_anchors_at_start() -> None:
    rect = fit_aspect((500, 500), (0, 0), 1.0)
    assert (rect.right, rect.bottom) == (500, 500)


def test_rect_contains() -> None:
    rect = Rect(10, 10, 5, 5)
    assert rect.contains(10, 14)
    assert not rect.contains(15, 10)
