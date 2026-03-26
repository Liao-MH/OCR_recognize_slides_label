# Preview Slide Summary Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add `slide_path` to CSV output and generate a `4096x4096` preview image showing WSI thumbnail, label thumbnail, and recognized text for the first successful slides.

**Architecture:** Extend the batch pipeline to return structured per-slide results instead of only flattened CSV rows. Keep OCR line reconstruction as the single source of truth, then let CSV export and preview rendering consume the same structured results so text layout stays consistent between outputs.

**Tech Stack:** Python 3.9, Pillow, OpenSlide, pytest

---

### Task 1: Add structured batch result objects and `slide_path`

**Files:**
- Modify: `src/svs_label_ocr/pipeline.py`
- Modify: `src/svs_label_ocr/export.py`
- Modify: `tests/test_export.py`
- Modify: `tests/test_integration_smoke.py`

**Step 1: Write the failing tests**

Add tests asserting:
- CSV includes `slide_path`
- `slide_path` is relative to `--input-dir`

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_export.py tests/test_integration_smoke.py -v`
Expected: FAIL because CSV fieldnames and batch rows do not include `slide_path`

**Step 3: Write minimal implementation**

Implement:
- a structured slide result from the pipeline
- relative `slide_path`
- CSV writer fieldnames `["svs_filename", "slide_path", "recognized_text"]`

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_export.py tests/test_integration_smoke.py -v`
Expected: PASS

### Task 2: Add preview renderer

**Files:**
- Create: `src/svs_label_ocr/preview.py`
- Create: `tests/test_preview.py`
- Modify: `tests/test_integration_smoke.py`

**Step 1: Write the failing tests**

Add tests asserting:
- preview image is generated
- preview image size is `4096x4096`
- only the first 5 successful slides are used

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_preview.py tests/test_integration_smoke.py -v`
Expected: FAIL because preview renderer does not exist

**Step 3: Write minimal implementation**

Implement:
- a preview renderer that lays out 3 columns
- line-by-line text drawing using recognized OCR lines
- thumbnail fitting with aspect-ratio preservation

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_preview.py tests/test_integration_smoke.py -v`
Expected: PASS

### Task 3: Integrate preview generation into batch flow and CLI

**Files:**
- Modify: `src/svs_label_ocr/export.py`
- Modify: `src/svs_label_ocr/cli.py`
- Modify: `tests/test_cli.py`

**Step 1: Write the failing tests**

Add tests asserting:
- CLI accepts `--preview-image`
- CLI accepts `--preview-rows`
- invalid preview row values are rejected

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_cli.py -v`
Expected: FAIL because preview arguments do not exist

**Step 3: Write minimal implementation**

Implement:
- preview CLI arguments
- default preview image path beside CSV
- explicit validation for preview row count
- batch call into preview renderer

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_cli.py -v`
Expected: PASS

### Task 4: Final verification and docs sync

**Files:**
- Modify: `docs/DEMANDS.MD`
- Modify: `docs/CHANGELOG.md`
- Modify: `README.md`

**Step 1: Update docs**

Document:
- new CSV column
- preview image output
- new CLI arguments

**Step 2: Run full verification**

Run:
- `pytest -v`
- `git diff --check`

Expected: PASS
