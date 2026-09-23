from pynput import keyboard

from reader2pdf.input_listener import KeyCommand, key_to_command


def test_key_to_command() -> None:
    assert key_to_command(keyboard.Key.space) is KeyCommand.FINISH
    assert key_to_command(keyboard.KeyCode.from_char("d")) is KeyCommand.DELETE_LAST
    assert key_to_command(keyboard.KeyCode.from_char("D")) is KeyCommand.DELETE_LAST
    assert key_to_command(keyboard.KeyCode.from_char("x")) is None
    assert key_to_command(keyboard.Key.enter) is None
    assert key_to_command(None) is None
