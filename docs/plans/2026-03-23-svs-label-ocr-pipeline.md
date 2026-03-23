# SVS Label OCR Pipeline Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a Python CLI that extracts SVS label associated images, segments handwritten text into lines, runs local-first OCR with OpenAI fallback, and exports a CSV with preserved line order.

**Architecture:** Use a small Python package with a pipeline split into scanning, SVS label extraction, preprocessing, line segmentation, OCR orchestration, and CSV export. Keep segmentation classical and deterministic, use local OCR for the main path, and isolate failures at the per-file level so batch processing never aborts on one bad sample.

**Tech Stack:** Python 3, `openslide-python`, `Pillow`, `numpy`, `opencv-python`, `pandas` or `csv`, `openai`, `pytest`

---

### Task 1: Create project skeleton and CLI contract

**Files:**
- Create: `pyproject.toml`
- Create: `src/svs_label_ocr/__init__.py`
- Create: `src/svs_label_ocr/cli.py`
- Create: `tests/test_cli.py`

**Step 1: Write the failing test**

```python
from svs_label_ocr.cli import build_parser


def test_cli_requires_input_and_output_arguments():
    parser = build_parser()
    args = parser.parse_args(["--input-dir", "/tmp/in", "--output-csv", "/tmp/out.csv"])
    assert args.input_dir == "/tmp/in"
    assert args.output_csv == "/tmp/out.csv"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_cli.py -v`
Expected: FAIL with import or symbol-not-found error

**Step 3: Write minimal implementation**

```python
import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--output-csv", required=True)
    return parser
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_cli.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add pyproject.toml src/svs_label_ocr/__init__.py src/svs_label_ocr/cli.py tests/test_cli.py
git commit -m "feat: initialize CLI for SVS label OCR"
```

### Task 2: Implement recursive SVS discovery

**Files:**
- Create: `src/svs_label_ocr/scanner.py`
- Create: `tests/test_scanner.py`
- Modify: `src/svs_label_ocr/cli.py`

**Step 1: Write the failing test**

```python
from pathlib import Path

from svs_label_ocr.scanner import find_svs_files


def test_find_svs_files_recursively_and_sorted(tmp_path: Path):
    (tmp_path / "b").mkdir()
    (tmp_path / "a").mkdir()
    (tmp_path / "b" / "case2.svs").write_text("")
    (tmp_path / "a" / "case1.svs").write_text("")
    (tmp_path / "a" / "ignore.txt").write_text("")

    result = find_svs_files(tmp_path)

    assert [p.name for p in result] == ["case1.svs", "case2.svs"]
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_scanner.py -v`
Expected: FAIL because `find_svs_files` does not exist

**Step 3: Write minimal implementation**

```python
from pathlib import Path


def find_svs_files(root: Path) -> list[Path]:
    if not root.exists():
        raise FileNotFoundError(f"Input directory not found: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"Input path is not a directory: {root}")
    return sorted(path for path in root.rglob("*.svs") if path.is_file())
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_scanner.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/svs_label_ocr/scanner.py tests/test_scanner.py src/svs_label_ocr/cli.py
git commit -m "feat: add recursive SVS scanner"
```

### Task 3: Implement SVS label extraction

**Files:**
- Create: `src/svs_label_ocr/label_extractor.py`
- Create: `tests/test_label_extractor.py`

**Step 1: Write the failing test**

```python
from PIL import Image

from svs_label_ocr.label_extractor import extract_label_image


class DummySlide:
    def __init__(self, label=None):
        self.associated_images = {}
        if label is not None:
            self.associated_images["label"] = label

    def close(self):
        pass


def test_extract_label_image_returns_label_copy():
    label = Image.new("RGB", (10, 10), "white")
    image = extract_label_image(slide=DummySlide(label=label))
    assert image.size == (10, 10)
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_label_extractor.py -v`
Expected: FAIL because the module or function does not exist

**Step 3: Write minimal implementation**

```python
from PIL import Image


def extract_label_image(*, slide) -> Image.Image:
    if "label" not in slide.associated_images:
        raise ValueError("SVS associated_images does not contain 'label'")
    return slide.associated_images["label"].copy()
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_label_extractor.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/svs_label_ocr/label_extractor.py tests/test_label_extractor.py
git commit -m "feat: add SVS label extraction"
```

### Task 4: Implement preprocessing for segmentation

**Files:**
- Create: `src/svs_label_ocr/preprocess.py`
- Create: `tests/test_preprocess.py`

**Step 1: Write the failing test**

```python
import numpy as np
from PIL import Image

from svs_label_ocr.preprocess import preprocess_label_for_segmentation


def test_preprocess_returns_binary_image_for_projection():
    image = Image.fromarray(np.full((50, 50, 3), 255, dtype=np.uint8))
    binary = preprocess_label_for_segmentation(image)
    assert binary.ndim == 2
    assert binary.shape == (50, 50)
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_preprocess.py -v`
Expected: FAIL because preprocessing function does not exist

**Step 3: Write minimal implementation**

Implement:
- border cropping
- grayscale conversion
- light blur
- contrast normalization
- Otsu binarization
- light morphology open

Keep the first implementation simple and deterministic. Raise explicit errors on empty or zero-sized images.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_preprocess.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/svs_label_ocr/preprocess.py tests/test_preprocess.py
git commit -m "feat: add label preprocessing for segmentation"
```

### Task 5: Implement projection-based line segmentation

**Files:**
- Create: `src/svs_label_ocr/segmentation.py`
- Create: `tests/test_segmentation.py`

**Step 1: Write the failing test**

```python
import numpy as np

from svs_label_ocr.segmentation import find_text_line_spans


def test_find_text_line_spans_detects_two_lines():
    binary = np.full((40, 20), 255, dtype=np.uint8)
    binary[5:10, 2:18] = 0
    binary[25:30, 2:18] = 0

    spans = find_text_line_spans(binary, min_ink_per_row=3, min_line_height=3, max_merge_gap=2)

    assert spans == [(5, 10), (25, 30)]
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_segmentation.py -v`
Expected: FAIL because segmentation function does not exist

**Step 3: Write minimal implementation**

Implement:
- row-wise ink counting
- thresholding into text rows
- grouping into spans
- min-height filtering
- short-gap merging

Return spans as top-inclusive and bottom-exclusive tuples.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_segmentation.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/svs_label_ocr/segmentation.py tests/test_segmentation.py
git commit -m "feat: add text line segmentation"
```

### Task 6: Implement line cropping and upscaling

**Files:**
- Create: `src/svs_label_ocr/line_images.py`
- Create: `tests/test_line_images.py`

**Step 1: Write the failing test**

```python
from PIL import Image, ImageDraw

from svs_label_ocr.line_images import crop_and_upscale_line


def test_crop_and_upscale_line_returns_larger_image():
    image = Image.new("L", (80, 30), "white")
    draw = ImageDraw.Draw(image)
    draw.rectangle((20, 10, 40, 18), fill="black")

    line = crop_and_upscale_line(image, (8, 20), margin=2, scale=2)

    assert line.size[0] > 20
    assert line.size[1] > 8
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_line_images.py -v`
Expected: FAIL because line-image helper does not exist

**Step 3: Write minimal implementation**

Implement:
- crop by y span
- detect non-white content within the cropped region
- expand by a small margin
- upscale with a smooth interpolation method

Raise an explicit error if the requested span is invalid.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_line_images.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/svs_label_ocr/line_images.py tests/test_line_images.py
git commit -m "feat: add per-line crop and upscale"
```

### Task 7: Implement OCR providers and suspicious-result detection

**Files:**
- Create: `src/svs_label_ocr/ocr.py`
- Create: `tests/test_ocr.py`

**Step 1: Write the failing test**

```python
from svs_label_ocr.ocr import is_suspicious_ocr_result


def test_is_suspicious_ocr_result_flags_empty_text():
    assert is_suspicious_ocr_result("") is True
    assert is_suspicious_ocr_result("A123") is False
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_ocr.py -v`
Expected: FAIL because OCR helpers do not exist

**Step 3: Write minimal implementation**

Implement:
- `is_suspicious_ocr_result`
- local OCR provider interface
- OpenAI fallback provider interface
- simple result normalization

Defer model-specific tuning until there are sample labels to evaluate.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_ocr.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/svs_label_ocr/ocr.py tests/test_ocr.py
git commit -m "feat: add OCR orchestration helpers"
```

### Task 8: Implement one-file pipeline orchestration

**Files:**
- Create: `src/svs_label_ocr/pipeline.py`
- Create: `tests/test_pipeline.py`

**Step 1: Write the failing test**

```python
from svs_label_ocr.pipeline import join_recognized_lines


def test_join_recognized_lines_preserves_top_to_bottom_order():
    assert join_recognized_lines(["Top", "Bottom"]) == "Top\nBottom"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_pipeline.py -v`
Expected: FAIL because pipeline helpers do not exist

**Step 3: Write minimal implementation**

Implement orchestration that:
- extracts the label
- preprocesses for segmentation
- finds line spans
- crops each line
- runs OCR with fallback
- joins the lines with `\n`

Keep per-step errors explicit and let the batch layer decide how to record failures.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_pipeline.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/svs_label_ocr/pipeline.py tests/test_pipeline.py
git commit -m "feat: add single-file OCR pipeline"
```

### Task 9: Implement batch processing and CSV export

**Files:**
- Create: `src/svs_label_ocr/export.py`
- Modify: `src/svs_label_ocr/cli.py`
- Create: `tests/test_export.py`

**Step 1: Write the failing test**

```python
import csv

from svs_label_ocr.export import write_results_csv


def test_write_results_csv_preserves_newlines(tmp_path):
    output = tmp_path / "result.csv"
    rows = [{"svs_filename": "a.svs", "recognized_text": "L1\nL2"}]

    write_results_csv(output, rows)

    with output.open(newline="", encoding="utf-8") as handle:
        data = list(csv.DictReader(handle))

    assert data[0]["recognized_text"] == "L1\nL2"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_export.py -v`
Expected: FAIL because export helper does not exist

**Step 3: Write minimal implementation**

Implement:
- batch loop over sorted SVS files
- per-file `try/except` isolation
- `svs_filename` output using `Path.name`
- CSV writing with correct newline-safe handling

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_export.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/svs_label_ocr/export.py src/svs_label_ocr/cli.py tests/test_export.py
git commit -m "feat: add batch CSV export"
```

### Task 10: Add integration smoke tests and operational docs

**Files:**
- Create: `tests/test_integration_smoke.py`
- Modify: `docs/DEMANDS.MD`
- Modify: `docs/CHANGELOG.md`

**Step 1: Write the failing test**

```python
def test_placeholder():
    assert True
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_integration_smoke.py -v`
Expected: Replace placeholder with a real smoke test against mocked components before implementation completes

**Step 3: Write minimal implementation**

Add:
- a smoke test for end-to-end orchestration with mocked OCR providers
- operational notes on required system dependencies for `openslide`
- initial usage example

**Step 4: Run test to verify it passes**

Run: `pytest -v`
Expected: PASS

**Step 5: Commit**

```bash
git add tests/test_integration_smoke.py docs/DEMANDS.MD docs/CHANGELOG.md
git commit -m "docs: finalize operational notes and smoke coverage"
```

### Verification Checklist

Run these before claiming completion:

```bash
pytest -v
python -m svs_label_ocr.cli --help
git diff --check
```

If sample `.svs` files are available, also run:

```bash
python -m svs_label_ocr.cli --input-dir /path/to/svs_root --output-csv /path/to/output.csv
```

Verify:
- CSV is produced
- `svs_filename` contains file names only
- newline structure is preserved in `recognized_text`
- one broken SVS does not stop the batch
