# Live Progress Design

## Goal

Add real-time terminal feedback during batch processing so users can see the current slide being processed and immediate per-slide failures while keeping the existing `.run.log` as the full diagnostic record.

## Confirmed Decisions

- Terminal output should show progress and failure information, but not the full verbose log.
- Progress should use a single-line overwrite style instead of printing one success line per slide.
- Failures should be printed immediately as separate lines.
- The existing `.run.log` file should remain the place for full traceback details.
- No new CLI option is needed for this first implementation.

## Recommended Approach

Keep the file logger unchanged and add a second, lightweight terminal reporting path in `process_batch()`. The batch loop already knows the current index, total slide count, relative slide path, and exception object, so it can drive both the durable file log and a concise terminal UX without changing lower-level OCR/image modules.

The terminal path should display a single overwritten line while slides are being processed:

`Processing 17/406 | nested/case17.svs`

On failure, the progress line should be terminated first so the error line is readable. Then print a one-line failure summary to standard error:

`ERROR 17/406 | nested/case17.svs | KeyError: missing label associated image`

After an error line, the next slide can resume the single-line progress display.

## Output Boundary

The terminal output is intentionally less detailed than the `.run.log`. It should show:

- discovery count
- current slide progress
- immediate failure summaries
- final summary (already handled by the CLI)

It should not show traceback or per-slide success detail. That remains in the log file. This keeps the terminal responsive and readable during large runs while still preserving the full debug trail in the file log.
