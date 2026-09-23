"""In-UI text catalogue with English as the default and Japanese localization."""

from enum import Enum


class Language(Enum):
    """Supported UI languages."""

    EN = "en"
    JA = "ja"


_MESSAGES: dict[str, dict[Language, str]] = {
    "select_hint": {
        Language.EN: (
            "Drag to select the capture region: {paper} {orientation}"
            "   [P] paper  [O] orientation  [Esc] cancel"
        ),
        Language.JA: (
            "ドラッグで撮影範囲を選択: {paper} {orientation}   [P] 用紙  [O] 向き  [Esc] キャンセル"
        ),
    },
    "portrait": {Language.EN: "portrait", Language.JA: "縦"},
    "landscape": {Language.EN: "landscape", Language.JA: "横"},
    "preview_title": {
        Language.EN: "Reader2Pdf - Last capture",
        Language.JA: "Reader2Pdf - 直前の撮影",
    },
    "no_capture": {
        Language.EN: "Click anywhere outside this window to capture.",
        Language.JA: "このウィンドウの外をクリックすると撮影します。",
    },
    "status": {
        Language.EN: "Pages: {count}    [Click] capture   [D] delete last   [Space] finish",
        Language.JA: "ページ数: {count}    [クリック] 撮影   [D] 直前を削除   [Space] 完了",
    },
    "saved": {
        Language.EN: "Saved {count} pages to {path}",
        Language.JA: "{count}ページを保存しました: {path}",
    },
    "nothing_to_save": {
        Language.EN: "No pages were captured; nothing saved.",
        Language.JA: "撮影されたページがないため、保存しませんでした。",
    },
    "cancelled": {
        Language.EN: "Region selection cancelled.",
        Language.JA: "範囲選択をキャンセルしました。",
    },
}


class Translator:
    """Looks up UI text for one language, falling back to English."""

    def __init__(self, language: Language = Language.EN) -> None:
        self._language = language

    def __call__(self, key: str, **params: object) -> str:
        """Returns the text for key in the current language, formatted with params."""
        entry = _MESSAGES[key]
        template = entry.get(self._language, entry[Language.EN])
        return template.format(**params)
