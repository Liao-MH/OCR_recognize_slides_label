# Preview Slide Summary Design

## Goal

Extend the current SVS label OCR batch tool with two output upgrades:

1. Add a `slide_path` column to the CSV output.
2. Generate a preview summary image that helps users quickly inspect the first successfully processed slides.

The design keeps the current OCR pipeline intact and adds minimal new structure around result objects and rendering.

## Confirmed Product Decisions

- `slide_path` stores the path relative to `--input-dir`
- The preview image shows the first 5 successfully processed slides in batch order
- The preview image is a single `4096x4096` image in the first implementation
- Each preview row has 3 columns:
  - WSI thumbnail
  - label thumbnail
  - recognized label text
- The text column must preserve the same line structure and reading order as the CSV `recognized_text`
- Text display may wrap within a single OCR line if needed for width, but it must not merge different OCR lines into one paragraph

## Recommended Architecture

Use a structured per-slide result object that is produced by the batch pipeline and consumed by both CSV export and preview rendering.

This is preferred over rebuilding the preview from the CSV after export because preview rendering needs direct access to:

- the WSI thumbnail
- the label thumbnail
- the OCR line list before it is flattened into a single string

Keeping those values in a shared result object avoids reopening files and avoids inconsistencies between CSV and preview rendering.

## Data Model Changes

Introduce a structured batch result shape with at least these fields for successful items:

- `svs_filename`
- `slide_path`
- `recognized_text`
- `recognized_lines`
- `wsi_thumbnail`
- `label_thumbnail`

For failed items, keep the current batch-robustness rule:

- they still appear in the CSV
- `recognized_text` contains an `ERROR: ...` string
- they do not enter preview candidate selection

`recognized_text` remains the newline-joined form of `recognized_lines`, so CSV and preview text are generated from the same source.

## Pipeline Changes

### CSV export

Update CSV writing to include:

- `svs_filename`
- `slide_path`
- `recognized_text`

`slide_path` must be computed relative to the input root directory so the CSV remains portable across machines as long as the dataset root is preserved.

### Preview generation

Add a new renderer module that receives the successful batch results and writes a summary PNG.

Suggested behavior:

- select successful results only
- keep original processing order
- take the first `N` results where `N` defaults to 5
- render one row per selected slide

The output image stays fixed at `4096x4096` in the first implementation to avoid unnecessary configuration complexity.

## Layout Design

The preview image contains 3 fixed columns:

1. WSI thumbnail
2. label thumbnail
3. recognized text

With 5 default rows, each row gets roughly one fifth of the canvas height.

Recommended rendering rules:

- preserve image aspect ratio inside each thumbnail cell
- center thumbnails inside their cells with a small margin
- reserve the widest column for text
- render text top-aligned within the third column
- draw text line by line from `recognized_lines`
- if a single OCR line exceeds available width, wrap only within that line
- keep a visible separator between rows to improve readability

If fewer than 5 successful slides exist, render only the available rows.

## Thumbnail Strategy

### WSI thumbnail

Use the SVS slide object to generate a small main-image thumbnail.

Preferred strategy:

- use a low-resolution slide level when available
- otherwise use a thumbnail helper from OpenSlide if available

The thumbnail should favor speed and visual context over detail.

### Label thumbnail

Use the extracted label image directly and downscale it into the preview cell while preserving aspect ratio.

## CLI Design

Add two optional CLI arguments:

- `--preview-image`
- `--preview-rows`

Defaults:

- `--preview-rows`: `5`
- `--preview-image`: if omitted, write a sibling file next to the output CSV using the same stem plus `.preview.png`

Do not add a configurable preview size in the first implementation; keep it fixed at `4096x4096`.

## Error Handling

- Invalid `--preview-rows` values must raise explicit errors
- CSV export should still complete even if no successful slides exist
- If no successful slides exist, skip preview generation with a clear warning or explicit no-preview outcome
- A failed preview should not silently pass as success
- A failed slide should not be used to build the preview

## Testing Strategy

Add tests for:

1. CSV now includes `slide_path`
2. `slide_path` is relative to `--input-dir`
3. preview renderer creates a `4096x4096` image
4. preview renderer only uses the first 5 successful results
5. preview text preserves OCR line boundaries from the pipeline result
6. failed items remain in CSV but are excluded from preview candidate selection

Also add or extend one smoke test to ensure:

- batch processing creates CSV rows with `slide_path`
- preview image is written
- successful rows appear in preview selection order

## Non-Goals For This Iteration

- multi-page preview reports
- configurable preview canvas size
- mixing failed samples into the preview
- rich annotation overlays on thumbnails
- OCR confidence visualization

## Recommended Next Step

Create an implementation plan that updates:

- batch result structures
- CSV exporter
- CLI arguments
- preview rendering module
- smoke and regression tests
