# Runtime Log Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a default runtime log file for each batch run and surface its path in the CLI summary without changing the `tests/` directory.

**Architecture:** Keep the change centered in the batch orchestration path. `src/svs_label_ocr/export.py` will create and write the runtime log because it already owns the slide loop and batch summary data. `src/svs_label_ocr/cli.py` will surface the log path in the terminal summary. Docs and version files will describe the new default output.

**Tech Stack:** Python 3.9+, standard library `logging`, existing CLI and batch processing modules.

---

### Task 1: Record the feature in repo docs

**Files:**
- Modify: `docs/DEMANDS.MD`
- Modify: `docs/CHANGELOG.md`
- Modify: `pyproject.toml`
- Modify: `src/svs_label_ocr/__init__.py`

**Step 1: Add the new requirement**

Document that every batch run must create a default runtime log file derived from `output_csv`, that the log contains execution progress and per-slide errors, and that the CLI summary prints the log path.

**Step 2: Bump the version**

Update package and docs version from `v1.0.0` / `1.0.0` to the next compatible feature version.

### Task 2: Implement runtime log creation in the batch layer

**Files:**
- Modify: `src/svs_label_ocr/export.py`

**Step 1: Add a derived log path helper and summary field**

Introduce a helper that maps `output_csv` to `<stem>.run.log`, and extend `BatchProcessResult` with the runtime log path.

**Step 2: Add logger setup**

Create a file logger dedicated to the current batch run. Ensure the output directory exists before the logger is attached.

**Step 3: Log batch lifecycle**

Write minimal lifecycle logs for:

- batch start
- discovered slide count
- per-slide start
- per-slide success
- per-slide failure with traceback
- preview generation status
- batch end summary

### Task 3: Surface the log path in the CLI summary

**Files:**
- Modify: `src/svs_label_ocr/cli.py`
- Modify: `README.md`

**Step 1: Update summary formatting**

Add a `Run log: ...` line to the printed summary.

**Step 2: Update README usage docs**

Document that the tool always writes a default runtime log file next to the CSV output and that this file contains detailed execution logs for debugging failures.

### Task 4: Verify without modifying tests

**Files:**
- No repository file changes required

**Step 1: Run the existing test suite**

Use the project environment to run `pytest -v` and confirm there are no regressions.

**Step 2: Run formatting verification**

Run `git diff --check`.

**Step 3: Run a targeted CLI smoke check**

Run `python -m svs_label_ocr.cli --help` and a small direct `process_batch` script or CLI invocation to confirm the runtime log file is created and the summary includes its path.

### Task 5: Commit and integrate

**Files:**
- All modified files above

**Step 1: Commit only implementation and documentation files**

Do not stage the `tests/` directory.

**Step 2: Merge to `main` and push**

Fast-forward merge the feature branch into `main`, push `main` to `origin`, then remove the temporary worktree and local feature branch.
