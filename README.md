# Reader2Pdf

[日本語](README.ja.md)

Capture the pages of an on-screen PDF reader, one click per page, and bundle the screenshots into a single PDF.

## Requirements

- Windows (tested on Windows 11), Python 3.12+
- [uv](https://docs.astral.sh/uv/)

## Setup

```sh
uv sync
```

## Usage

```sh
uv run reader2pdf [--paper A4|B3] [--orientation portrait|landscape] [--delay SECONDS] [--output PATH] [--lang en|ja]
```

1. **Select the region.** The screen freezes and dims. Drag to draw the capture region. Its aspect ratio stays locked to the chosen paper.
   - `P`: switch paper size (A4 / B3)
   - `O`: switch orientation (portrait / landscape)
   - `Esc`: cancel
2. **Capture.** A red frame marks the region and a preview window opens beside it. Every left click outside the preview window captures the region. Clicking the reader's "next page" button therefore captures the current page and turns to the next one.
3. **Keys** (they work even while the reader has focus):
   - `D`: delete the last capture (for a mis-click)
   - `Space`: finish and save the PDF

The PDF is saved to `output/reader2pdf_YYYYmmdd_HHMMSS.pdf` unless you pass `--output`. Each PDF page has the physical size of the chosen paper.

### Options

| Option          | Default    | Description                                                                                                            |
| --------------- | ---------- | ---------------------------------------------------------------------------------------------------------------------- |
| `--paper`       | `A4`       | Paper whose aspect ratio the region uses. `P` also switches it during selection.                                        |
| `--orientation` | `portrait` | Region orientation. `O` also switches it during selection.                                                              |
| `--delay`       | `0`        | Seconds between a click and its capture. `0` captures the moment the button goes down, before the reader reacts.       |
| `--output`      | timestamp  | Destination PDF path.                                                                                                  |
| `--lang`        | `en`       | UI language (`en` / `ja`).                                                                                              |

### Notes

- A4 (210×297 mm) and B3 (353×500 mm) have nearly the same aspect ratio (≈1:√2). The paper choice mainly sets the physical page size of the output PDF.
- The keys are global. If the reader scrolls on `Space`, that scroll happens after the PDF is saved, so it does no harm.
- Keep the preview window outside the red frame. If it overlaps the region, it will appear in the captures.

## Development

```sh
uv run pytest            # tests
uv run mypy src tests    # strict type check
uv run ruff check .      # lint
uv run ruff format .     # format
```

See [docs/architecture.md](docs/architecture.md) for the design.
