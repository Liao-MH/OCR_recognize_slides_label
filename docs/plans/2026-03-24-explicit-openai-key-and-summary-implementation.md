# Explicit OpenAI Key And Batch Summary Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Require explicit `--openai-api-key` input when OpenAI fallback is enabled and print a concise batch summary after processing completes.

**Architecture:** Keep CLI validation in the command-line layer, pass the explicit key into the OpenAI fallback provider, and let the batch layer return structured statistics instead of only raw CSV rows. This preserves a clean split between OCR behavior, batch accounting, and terminal presentation.

**Tech Stack:** Python 3.9, argparse, OpenAI Python SDK, pytest

---

### Task 1: Add CLI validation for explicit OpenAI key

**Files:**
- Modify: `src/svs_label_ocr/cli.py`
- Modify: `tests/test_cli.py`

**Step 1: Write the failing tests**

Add tests asserting:
- fallback-enabled parsing/validation fails without `--openai-api-key`
- explicit `--openai-api-key` is accepted
- disabled fallback does not require a key

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_cli.py -v`
Expected: FAIL because the CLI does not expose or validate the new key argument

**Step 3: Write minimal implementation**

Implement:
- `--openai-api-key`
- post-parse validation helper
- fallback creation only when validation passes

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_cli.py -v`
Expected: PASS

### Task 2: Pass explicit key into fallback OCR provider

**Files:**
- Modify: `src/svs_label_ocr/ocr.py`
- Create: `tests/test_ocr_provider_config.py`

**Step 1: Write the failing test**

Add a test asserting the fallback provider stores or uses the explicit API key rather than depending on process environment.

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_ocr_provider_config.py -v`
Expected: FAIL because the provider does not accept explicit key input

**Step 3: Write minimal implementation**

Implement:
- explicit `api_key` parameter on `OpenAIFallbackOCRProvider`
- client construction with that key

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_ocr_provider_config.py -v`
Expected: PASS

### Task 3: Add structured batch summary

**Files:**
- Modify: `src/svs_label_ocr/export.py`
- Modify: `tests/test_integration_smoke.py`
- Create: `tests/test_summary.py`

**Step 1: Write the failing tests**

Add tests asserting:
- batch processing returns total, success, and failure counts
- preview path / skipped-preview state is reported correctly

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_summary.py tests/test_integration_smoke.py -v`
Expected: FAIL because batch processing currently returns only rows

**Step 3: Write minimal implementation**

Implement:
- summary dataclass or structured return shape
- total/success/failure accounting
- preview path / skipped-preview fields

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_summary.py tests/test_integration_smoke.py -v`
Expected: PASS

### Task 4: Print summary from the CLI

**Files:**
- Modify: `src/svs_label_ocr/cli.py`
- Create: `tests/test_cli_summary.py`

**Step 1: Write the failing test**

Add a test asserting CLI stdout includes:
- total count
- success count
- failure count
- CSV output path
- preview output path or skipped-preview message

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_cli_summary.py -v`
Expected: FAIL because CLI currently prints nothing after completion

**Step 3: Write minimal implementation**

Implement:
- small summary formatter
- stdout printing at end of `main`

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_cli_summary.py -v`
Expected: PASS

### Task 5: Sync docs and verify end to end

**Files:**
- Modify: `README.md`
- Modify: `docs/DEMANDS.MD`
- Modify: `docs/CHANGELOG.md`
- Create: `docs/plans/2026-03-24-explicit-openai-key-and-summary-design.md`

**Step 1: Update docs**

Document:
- `--openai-api-key`
- no longer relying on environment-variable-only configuration
- batch summary output

**Step 2: Run full verification**

Run:
- `pytest -v`
- `git diff --check`
- `python -m svs_label_ocr.cli --help`

Expected: PASS
