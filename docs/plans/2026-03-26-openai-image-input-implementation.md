# OpenAI Image Input Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make OpenAI fallback OCR send cropped line images through the Responses API `input_image` path so `gpt-4.1` and similar vision-capable models work correctly.

**Architecture:** Keep the change focused in `src/svs_label_ocr/ocr.py`. Replace file upload logic with in-memory PNG-to-data-URL encoding and send the image directly in the Responses payload. Update docs and version metadata to reflect the new behavior. Add one focused test that asserts the fallback provider sends `input_image`.

**Tech Stack:** Python 3.9+, standard library `base64` and `io`, OpenAI Responses API, pytest.

---

### Task 1: Record the new requirement

**Files:**
- Modify: `docs/DEMANDS.MD`
- Modify: `docs/CHANGELOG.md`
- Modify: `README.md`
- Modify: `pyproject.toml`
- Modify: `src/svs_label_ocr/__init__.py`

**Step 1: Add the OpenAI image-input requirement**

Document that OpenAI fallback sends line images as image inputs, and that this fixes model compatibility for `gpt-4.1`.

**Step 2: Bump the version**

Update the package and docs version to the next compatible release.

### Task 2: Write the failing test

**Files:**
- Modify: `tests/test_ocr_provider_config.py`

**Step 1: Add a payload-shape test**

Create a dummy client that records `responses.create()` arguments and returns a fake response object. Assert that:

- the request contains an `input_text` item
- the request contains an `input_image` item
- the `input_image` item carries a PNG data URL

**Step 2: Run the focused test to verify it fails**

Run: `pytest tests/test_ocr_provider_config.py -v`

Expected: FAIL because the current implementation uses `files.create()` plus `input_file`.

### Task 3: Implement the minimal provider change

**Files:**
- Modify: `src/svs_label_ocr/ocr.py`

**Step 1: Add image encoding helper**

Encode the incoming `PIL.Image` into PNG bytes in memory and convert it to a `data:image/png;base64,...` URL.

**Step 2: Replace file-upload flow**

Remove the temporary-file and uploaded-file path from `OpenAIFallbackOCRProvider.recognize_line()` and build a Responses payload with `input_text` plus `input_image`.

### Task 4: Verify green

**Files:**
- No additional file changes required

**Step 1: Run the focused test**

Run: `pytest tests/test_ocr_provider_config.py -v`

**Step 2: Run the full suite**

Run: `pytest -v`

**Step 3: Run formatting verification**

Run: `git diff --check`
