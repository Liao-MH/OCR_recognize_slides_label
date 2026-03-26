# Explicit OpenAI Key And Batch Summary Design

## Goal

Improve the current CLI in two ways:

1. Stop relying on `OPENAI_API_KEY` as the primary runtime mechanism and require explicit API key input through the CLI when OpenAI fallback is enabled.
2. Print a concise run summary after batch execution so users can immediately see total files, successes, failures, and output locations.

## Confirmed Product Decisions

- OpenAI fallback should use an explicit CLI argument instead of environment-variable-only configuration.
- The CLI argument will be `--openai-api-key`.
- When OpenAI fallback is enabled, `--openai-api-key` must be explicitly provided.
- When `--disable-openai-fallback` is used, `--openai-api-key` is not required.
- Batch summary output should be printed to standard output at the end of the run.

## Recommended Architecture

Keep the fallback OCR provider responsible only for OCR behavior and client construction, and move argument-validation rules into the CLI layer.

Keep batch processing responsible for computing summary statistics, but keep human-readable printing in the CLI layer. This preserves separation of concerns:

- export layer computes the facts
- CLI layer decides how to present them

## CLI Design

Add a new CLI argument:

- `--openai-api-key`

Validation rules:

- if fallback is enabled and no `--openai-api-key` is provided, fail immediately with a clear CLI error
- if fallback is disabled, the argument may be omitted

This design intentionally avoids silent environment-variable fallback so runtime configuration is explicit and visible in the command invocation.

## OCR Provider Design

Update `OpenAIFallbackOCRProvider` to accept an explicit `api_key` value and build its OpenAI client with that key.

This removes implicit dependency on process-wide environment configuration at the application layer.

## Batch Summary Design

Extend batch processing to return a structured summary object that includes at least:

- total discovered `.svs` count
- successful slide count
- failed slide count
- CSV output path
- preview output path, if generated
- whether preview was skipped because there were no successful slides

The summary should be derived from real batch outcomes, not reconstructed later from terminal text.

## CLI Output Design

After the batch finishes, print a short summary to stdout, for example:

- total SVS files found
- successful slides
- failed slides
- CSV output path
- preview output path or skipped-preview status

The output should stay compact and command-line-friendly.

## Error Handling

- Missing `--openai-api-key` while fallback is enabled must produce an explicit CLI error
- Summary printing must not claim a preview exists if preview generation was skipped
- Failure counts must include per-file OCR or extraction failures already recorded in the CSV

## Testing Strategy

Add tests for:

1. CLI rejects fallback-enabled execution without `--openai-api-key`
2. CLI accepts explicit `--openai-api-key`
3. fallback provider can be constructed with an explicit key
4. batch processing returns correct summary counts
5. CLI prints summary lines containing total, success, failure, CSV path, and preview path/skip state

## Non-Goals

- writing summary to JSON or YAML
- preserving environment-variable-only configuration as the primary path
- adding rich progress bars or live per-file logging in this iteration

## Recommended Next Step

Create an implementation plan that updates:

- CLI argument parsing and validation
- OpenAI fallback provider construction
- batch result structure
- CLI summary printing
- tests and documentation
