# アーキテクチャ

[English](architecture.md)

## モジュール

| モジュール          | 役割                                                                         |
| ------------------- | ---------------------------------------------------------------------------- |
| `__main__.py`       | コマンドライン引数を `AppConfig` に変換し、アプリを起動する。                  |
| `app.py`            | `Reader2PdfApp` が、範囲選択 → クリック撮影 → 書き出し の流れを進める。         |
| `geometry.py`       | `PaperSize`、`Orientation`、`Rect`、および縦横比固定ドラッグ用の `fit_aspect`。 |
| `region_selector.py`| 暗く静止させた全画面オーバーレイ。ユーザーはここで撮影範囲をドラッグする。       |
| `region_frame.py`   | 撮影範囲の*外側*に常に最前面で描く赤枠。撮影画像には写らない。                  |
| `preview_window.py` | 直前の撮影画像、ページ数、キー操作を表示する。                                 |
| `input_listener.py` | グローバルなマウス・キーボードのフック（pynput）。クリックと `KeyCommand` に変換する。 |
| `capturer.py`       | `ScreenCapturer` プロトコルと、その実装 `MssCapturer`。                         |
| `session.py`        | `CaptureSession`：撮影したページを順に保持する。直前のページを削除できる。       |
| `pdf_exporter.py`   | ページを 1 つの PDF に書き出す。ページサイズは用紙の実寸に合わせる。             |
| `i18n.py`           | UI の文言（英語が既定、日本語にも対応）。                                      |
| `platform_setup.py` | Windows の DPI 認識を有効にし、Tk・mss・pynput がすべて物理ピクセルを使うようにする。 |

## クラス図

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

## シーケンス図：1 回のセッション

```mermaid
sequenceDiagram
    actor User as ユーザー
    participant App as Reader2PdfApp（Tk スレッド）
    participant Sel as RegionSelector
    participant Hook as InputListener（フックスレッド）
    participant Cap as MssCapturer
    participant Q as イベントキュー
    participant Prev as PreviewWindow
    participant Exp as PdfExporter

    App->>Cap: capture(仮想スクリーン全体)
    App->>Sel: select()
    User->>Sel: ドラッグ（P / O で用紙を変更）
    Sel-->>App: RegionSelection
    App->>Prev: 撮影範囲の横に開く
    App->>Hook: start()

    loop 各ページ
        User->>Hook: 左クリック（例：リーダーの「次ページ」）
        Hook->>Cap: capture(撮影範囲)［押した瞬間、または --delay 後］
        Cap-->>Q: ページ画像
        App->>Q: 20 ms ごとにポーリング
        App->>Prev: show(直前の画像, ページ数)
    end

    opt ミスクリック
        User->>Hook: D
        Hook-->>Q: DELETE_LAST
        App->>Prev: show(1 つ前の画像, ページ数)
    end

    User->>Hook: Space
    Hook-->>Q: FINISH
    App->>Hook: stop()
    App->>Exp: export(ページ, 保存先)
```

## スレッド構成

pynput はコールバックを専用のフックスレッドで呼び出します。一方、Tk はメインスレッドからしか操作できません。そのため次のようにしています。

- 撮影は、ボタンが押された瞬間に**フックスレッド上で**行います。リーダーがクリックを処理する前にページを撮影できます。mss のハンドルはスレッドに紐づくため、呼び出しごとに mss を生成します。
- 撮影画像とキーコマンドは `queue.Queue` に入れます。Tk スレッドが 20 ms ごとに取り出します（`Reader2PdfApp._poll`）。
- プレビューウィンドウの位置と大きさは、ポーリングのたびに不変の `Rect` へコピーします。フックスレッドはこの `Rect` を参照し、プレビューウィンドウ上のクリックを無視します。
