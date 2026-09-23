from reader2pdf.i18n import _MESSAGES, Language, Translator


def test_every_message_has_all_languages() -> None:
    for entry in _MESSAGES.values():
        assert set(entry) == set(Language)


def test_translator_formats_params() -> None:
    assert "3" in Translator(Language.JA)("status", count=3)
    assert Translator()("portrait") == "portrait"
