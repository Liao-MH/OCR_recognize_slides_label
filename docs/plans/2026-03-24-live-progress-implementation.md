# Live Progress Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add real-time terminal progress and immediate failure output during batch processing while keeping the `.run.log` file as the full diagnostic record.

**Architecture:** Extend `src/svs_label_ocr/export.py` with small helper functions for progress refresh, progress-line finalization, and immediate error printing. Keep file logging untouched. Wire the new behavior into the existing batch loop and finalize the terminal line before the CLI prints its summary.

**Tech Stack:** Python 3.9+, standard library `sys`, `io`, and `logging`, pytest for verification.

---

### Task 1: Record the new requirement

**Files:**
- Modify: `docs/DEMANDS.MD`
- Modify: `docs/CHANGELOG.md`
- Modify: `README.md`
- Modify: `pyproject.toml`
- Modify: `src/svs_label_ocr/__init__.py`

**Step 1: Add the terminal-progress requirement**

Document that the tool now prints live single-line progress and immediate failure summaries to the terminal in addition to writing the `.run.log` file.

**Step 2: Bump the version**

Update the package and docs version to the next feature release.

### Task 2: Write the failing test

**Files:**
- Create: `tests/test_live_progress.py`

**Step 1: Add a progress/error capture test**

Create a test that passes in in-memory stdout/stderr streams to `process_batch()`, runs one success and one failure slide, and asserts:

- stdout contains overwritten `Processing i/N | ...` text and ends with a newline
- stderr contains the immediate `ERROR i/N | ...` summary
- the batch result still reports success/failure counts correctly

**Step 2: Run the test to verify it fails**

Run: `pytest tests/test_live_progress.py -v`

Expected: FAIL because `process_batch()` does not yet accept terminal streams or emit progress/error output.

### Task 3: Implement the minimal terminal progress layer

**Files:**
- Modify: `src/svs_label_ocr/export.py`

**Step 1: Add progress helper functions**

Implement small helpers for:

- printing discovery count
- refreshing the single-line progress display
- finalizing the progress line before summary/error output
- printing one-line failure summaries to stderr

**Step 2: Thread streams into `process_batch()`**

Add optional terminal stream parameters defaulting to `sys.stdout` and `sys.stderr` and call the helpers from the batch loop.

**Step 3: Keep existing behavior intact**

Preserve CSV writing, `.run.log`, preview generation, and final summary data.

### Task 4: Verify green

**Files:**
- No additional file changes required

**Step 1: Run the new focused test**

Run: `pytest tests/test_live_progress.py -v`

Expected: PASS

**Step 2: Run the full suite**

Run: `pytest -v`

Expected: PASS

**Step 3: Run formatting verification**

Run: `git diff --check`

**Step 4: Run a CLI/manual smoke check**

Run a small `process_batch()` script and confirm the terminal shows progress plus immediate failure summaries.
