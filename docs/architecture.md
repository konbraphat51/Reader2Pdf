# Architecture

[日本語](architecture.ja.md)

## Modules

| Module              | Responsibility                                                                      |
| ------------------- | ----------------------------------------------------------------------------------- |
| `__main__.py`       | Parses command-line options into `AppConfig` and starts the app.                     |
| `app.py`            | `Reader2PdfApp` runs the flow: selection → click capture → export.                   |
| `geometry.py`       | `PaperSize`, `Orientation`, `Rect`, and `fit_aspect` for aspect-locked dragging.     |
| `region_selector.py`| Full-screen, dimmed, frozen overlay where the user drags out the capture region.     |
| `region_frame.py`   | Red always-on-top border drawn *outside* the region, so it never appears in a capture. |
| `preview_window.py` | Shows the last capture, the page count and the key bindings.                         |
| `input_listener.py` | Global mouse and keyboard hooks (pynput), mapped to clicks and `KeyCommand`s.        |
| `capturer.py`       | `ScreenCapturer` protocol and the `MssCapturer` implementation.                      |
| `session.py`        | `CaptureSession`: the ordered list of captured pages, with delete-last.              |
| `pdf_exporter.py`   | Writes the pages into one PDF whose page size matches the paper.                      |
| `i18n.py`           | UI text in English (default) and Japanese.                                          |
| `platform_setup.py` | Turns on Windows DPI awareness, so Tk, mss and pynput all use physical pixels.        |

## Class diagram

```mermaid
classDiagram
    class Reader2PdfApp {
        +run() Path | None
        -_on_click(x, y)
        -_poll()
        -_finish()
    }
    class AppConfig {
        paper: PaperSize
        orientation: Orientation
        capture_delay_s: float
        output: Path
        language: Language
    }
    class ScreenCapturer {
        <<Protocol>>
        +capture(rect) Image
        +virtual_screen() Rect
        +monitors() list~Rect~
    }
    class MssCapturer
    class RegionSelector {
        +select() RegionSelection | None
    }
    class RegionSelection {
        rect: Rect
        paper: PaperSize
        orientation: Orientation
    }
    class RegionFrame {
        +destroy()
    }
    class PreviewWindow {
        +show(page, count)
        +place_beside(rect, screen)
        +bounds() Rect
    }
    class InputListener {
        +start()
        +stop()
    }
    class CaptureSession {
        +add(page)
        +remove_last()
        +pages
        +last
    }
    class PdfExporter {
        +export(pages, path)
    }
    class Translator {
        +__call__(key, **params) str
    }

    ScreenCapturer <|.. MssCapturer
    Reader2PdfApp --> AppConfig
    Reader2PdfApp --> ScreenCapturer
    Reader2PdfApp --> RegionSelector
    RegionSelector --> RegionSelection
    Reader2PdfApp --> RegionFrame
    Reader2PdfApp --> PreviewWindow
    Reader2PdfApp --> InputListener
    Reader2PdfApp --> CaptureSession
    Reader2PdfApp --> PdfExporter
    Reader2PdfApp --> Translator
```

## Sequence: one session

```mermaid
sequenceDiagram
    actor User
    participant App as Reader2PdfApp (Tk thread)
    participant Sel as RegionSelector
    participant Hook as InputListener (hook threads)
    participant Cap as MssCapturer
    participant Q as Event queue
    participant Prev as PreviewWindow
    participant Exp as PdfExporter

    App->>Cap: capture(virtual screen)
    App->>Sel: select()
    User->>Sel: drag (P / O to change paper)
    Sel-->>App: RegionSelection
    App->>Prev: open beside region
    App->>Hook: start()

    loop every page
        User->>Hook: left click (e.g. reader's "next page")
        Hook->>Cap: capture(region) [on press, or after --delay]
        Cap-->>Q: page image
        App->>Q: poll every 20 ms
        App->>Prev: show(last, count)
    end

    opt mis-click
        User->>Hook: D
        Hook-->>Q: DELETE_LAST
        App->>Prev: show(previous, count)
    end

    User->>Hook: Space
    Hook-->>Q: FINISH
    App->>Hook: stop()
    App->>Exp: export(pages, output)
```

## Threading

pynput runs its callbacks on its own hook threads, and Tk may only be used from the main thread. So:

- The capture runs **on the hook thread**, right when the button goes down. The page is captured before the reader handles the click. mss is created per call because its handles are thread-bound.
- Captured images and key commands go into a `queue.Queue`. The Tk thread drains it every 20 ms (`Reader2PdfApp._poll`).
- The preview window's bounds are copied to an immutable `Rect` on each poll. The hook thread reads that `Rect` to ignore clicks on the preview window.
