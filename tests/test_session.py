from PIL import Image

from reader2pdf.session import CaptureSession


def test_add_and_remove_last() -> None:
    session = CaptureSession()
    assert session.last is None
    assert session.remove_last() is None

    first = Image.new("RGB", (1, 1))
    second = Image.new("RGB", (2, 2))
    session.add(first)
    session.add(second)
    assert session.count == 2
    assert session.last is second

    assert session.remove_last() is second
    assert session.pages == [first]
