# Runtime Log Design

## Goal

Add a default runtime log file so batch runs keep a readable execution trace even when individual `.svs` files fail and the CLI summary only shows aggregate counts.

## Confirmed Decisions

- The tool must always write a runtime log file during batch processing.
- The log file is a code execution log, not a structured export format.
- The log file path should be derived automatically from `output_csv`.
- No new CLI option is needed for configuring the log path.
- The log file should record both success and failure progress.
- The CLI summary should print the runtime log path.
- This iteration should avoid changing the `tests/` directory; verification should rely on existing tests plus targeted command-line checks.

## Recommended Approach

Use the standard library `logging` module at the batch-processing layer. The batch layer already owns the whole loop over discovered `.svs` files, so it is the natural place to log run start, per-slide processing, per-slide success, per-slide failure, preview generation, and final summary. This keeps logging out of lower-level OCR and image helpers and avoids unnecessary cross-module changes.

The log file should default to `<output_csv stem>.run.log` in the same directory as the CSV output. For example, `output/output.csv` should produce `output/output.run.log`. The log file should be created before slide processing starts so that setup failures and discovery counts are also captured.

## Logging Content

The runtime log should be readable in a terminal editor and useful for root-cause analysis. It should contain timestamped lines that cover:

- batch start
- input directory and output paths
- number of discovered `.svs` files
- start of each slide
- success of each slide
- failure of each slide with exception type and message
- preview generation status
- batch end summary

For per-slide failures, include the Python traceback in the log file only. This keeps the terminal summary compact while preserving enough detail for debugging.

## Error Handling Boundary

The current batch behavior that isolates per-slide failures and writes `ERROR: ...` into CSV should stay intact. The new logging behavior must not silently suppress additional errors in the logger itself. If the log file cannot be opened, that should be treated as a real run error because default logging is now part of the expected output contract.
