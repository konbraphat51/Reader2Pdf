"""Global mouse and keyboard hooks translated into capture-session commands."""

from collections.abc import Callable
from enum import Enum

from pynput import keyboard, mouse


class KeyCommand(Enum):
    """Session commands bound to keys."""

    DELETE_LAST = "delete_last"
    FINISH = "finish"


ClickHandler = Callable[[int, int], None]
"""Called with screen (x, y) on each left-button press; runs on the hook thread."""

KeyHandler = Callable[[KeyCommand], None]
"""Called with the command of a bound key press; runs on the hook thread."""


def key_to_command(key: keyboard.Key | keyboard.KeyCode | None) -> KeyCommand | None:
    """Maps a pressed key to its command: D deletes the last page, Space finishes."""
    if key == keyboard.Key.space:
        return KeyCommand.FINISH
    if isinstance(key, keyboard.KeyCode) and key.char is not None and key.char.lower() == "d":
        return KeyCommand.DELETE_LAST
    return None


class InputListener:
    """Listens to system-wide input, even while another application has focus."""

    def __init__(self, on_click: ClickHandler, on_key: KeyHandler) -> None:
        self._on_click = on_click
        self._on_key = on_key
        self._mouse = mouse.Listener(on_click=self._handle_click)
        self._keyboard = keyboard.Listener(on_press=self._handle_key)

    def start(self) -> None:
        """Starts both hooks on background threads."""
        self._mouse.start()
        self._keyboard.start()

    def stop(self) -> None:
        """Stops both hooks."""
        self._mouse.stop()
        self._keyboard.stop()

    def _handle_click(self, x: int, y: int, button: mouse.Button, pressed: bool) -> None:
        if pressed and button == mouse.Button.left:
            self._on_click(x, y)

    def _handle_key(self, key: keyboard.Key | keyboard.KeyCode | None) -> None:
        command = key_to_command(key)
        if command is not None:
            self._on_key(command)
