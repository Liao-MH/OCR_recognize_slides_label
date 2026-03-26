# SVS Label Handwriting OCR Demands

## Version

`v1.2.0`

## Additional Documentation Requirement

- Add a root `README.md`
- The README should let a new user understand the tool's purpose, dependencies, installation, CLI usage, output format, and current scope without reading the source code first
- The README should match the actual implemented behavior of the repository instead of describing hypothetical future features
- The README should also include Conda-based environment setup and usage instructions

## Newly Confirmed Feature Requirement

- The CSV output must add a `slide_path` column
- `slide_path` must be relative to `--input-dir`
- The tool must also generate a preview summary image
- The preview summary image must be a single `4096x4096` image in the first implementation
- The preview image must contain 3 columns per slide row:
  - WSI thumbnail
  - label thumbnail
  - recognized label text
- The preview image must default to showing the first 5 successfully processed slides in stable processing order
- The preview text column must preserve the same line ordering and line boundaries as the CSV `recognized_text`

## Newly Confirmed CLI And Reporting Requirement

- OpenAI fallback must use an explicit `--openai-api-key` CLI argument instead of relying on environment-variable-only configuration
- If OpenAI fallback is enabled, missing `--openai-api-key` must produce an explicit CLI error
- If `--disable-openai-fallback` is used, `--openai-api-key` is not required
- The CLI must print a batch summary after execution
- The batch summary must include at least:
  - total discovered `.svs` files
  - success count
  - failure count
  - CSV output path
  - preview output path or skipped-preview status

## Newly Confirmed Runtime Log Requirement

- Every batch run must always create a default runtime log file
- The runtime log path must be derived from `output_csv` as `<stem>.run.log` in the same directory
- The runtime log must record execution progress instead of acting as a structured export file
- The runtime log must include:
  - batch start
  - discovered `.svs` count
  - per-slide processing start
  - per-slide success
  - per-slide failure with detailed exception information
  - preview generation status
  - batch end summary
- The CLI summary must print the runtime log path

## Newly Confirmed Terminal Progress Requirement

- The tool must print real-time terminal progress during batch execution by default
- Terminal progress should use a single-line overwrite style for normal processing progress
- The terminal must print immediate failure summaries as separate lines when a slide fails
- Failure summaries should include:
  - slide index / total slide count
  - relative slide path
  - exception type
  - exception message
- Full traceback details should remain in the `.run.log` file instead of being fully printed to the terminal

## Project Goal

Build a script that recursively scans a root directory, reads the `label` associated image from each `.svs` file, recognizes handwritten text on the label, writes a CSV, and generates a preview summary image.

- `svs_filename`
- `slide_path`
- `recognized_text`

`recognized_text` must preserve the top-to-bottom spatial line order from the label image, using newline characters between lines.

## Input And Output

### Input

- A root directory containing `.svs` files in nested subdirectories

### Output

- A CSV file
- Column 1: `svs_filename`
- Column 2: `slide_path`
- Column 3: `recognized_text`
- A preview summary PNG image

## Required End-To-End Pipeline

1. Recursively scan the input directory for `.svs` files
2. Extract the `label` associated image from each SVS
3. Preprocess the label image for segmentation and OCR
4. Split the label image into text lines
5. Run OCR line by line
6. Write one CSV row per SVS file
7. Render a preview summary image for the first successful slides

## Functional Requirements

### 1. SVS Scanning

- Recursively traverse the input directory
- Collect only files with the `.svs` suffix
- Sort the collected file paths to keep processing order stable and reproducible

### 2. Label Extraction

- Open each SVS with `openslide.OpenSlide`
- Read `slide.associated_images["label"]`
- Use the associated `label` image as the OCR source
- Do not crop the main slide image as a substitute for label extraction

### 3. Image Preprocessing

The preprocessing stage must support line segmentation and OCR quality improvement.

#### Required preprocessing steps

- Crop black or near-black border regions
- Convert the image to grayscale
- Apply light denoising
- Enhance contrast
- Binarize the image with a foreground/background convention suitable for projection analysis
- Apply light morphological cleanup to remove tiny isolated noise

#### Preprocessing intent

- Reduce background interference
- Highlight handwriting strokes
- Improve robustness of line segmentation
- Keep the text content intact without aggressive distortion

### 4. Text Line Segmentation

- Use horizontal projection on a binarized image
- Compute per-row ink density
- Mark rows above a minimum threshold as text rows
- Group consecutive text rows into candidate line spans
- Filter spans that are too thin to be valid lines
- Merge spans separated by very small gaps
- Return line spans ordered from top to bottom

### 5. Line-Level Cropping

For each segmented line:

- Crop the line region from the original or lightly processed image, not from the hard binary mask unless necessary
- Tighten the left/right content region with a small margin
- Upscale the cropped line image by about 2x to 3x before OCR

### 6. OCR Strategy

#### Primary OCR

- Use a lightweight handwritten text recognition model locally
- Prefer line-level OCR over full-image OCR

#### Suspicious-result detection

Treat a local OCR result as suspicious when it clearly looks unreliable, for example:

- Empty output
- Very short output
- No alphanumeric characters
- Excessively high symbol/noise ratio

#### Fallback OCR

- Use the OpenAI API only when the local OCR result is suspicious or the local OCR step fails
- Send one line image at a time
- Prompt the model to return only the handwritten text content without explanations

### 7. Text Reconstruction

- Process segmented lines from top to bottom
- Recognize one string per line
- Join recognized line strings with `\n`
- Preserve the label image's spatial reading order

### 8. Text Cleaning

Apply only light cleanup:

- Trim leading and trailing whitespace
- Normalize spaces
- Normalize newline usage
- Remove extra blank lines

Do not apply strong rule-based correction or format-specific rewriting in the first version.

### 9. Batch Robustness

- Process each SVS independently
- A failure on one file must not stop the entire batch
- Errors that can occur include:
  - Missing `label`
  - Corrupted SVS
  - Image extraction failure
  - OCR failure
  - API failure

### 10. CSV Rules

- Store only the SVS file name, not the full path, in `svs_filename`
- Store `slide_path` as the path relative to the input root directory
- Preserve newline characters inside `recognized_text`
- Ensure CSV writing handles embedded newlines correctly

### 11. Preview Summary Image Rules

- Output a single `4096x4096` image in the first implementation
- Default to the first 5 successfully processed slides in stable processing order
- Each slide row must have 3 columns:
  - WSI thumbnail
  - label thumbnail
  - recognized text
- The preview text must preserve the same OCR line order and line boundaries as the CSV `recognized_text`

## Error Handling Requirements

- Do not silently swallow exceptions
- Do not silently replace invalid states with fallback values
- For clearly invalid or missing user inputs, raise explicit errors with clear reasons
- For per-file processing errors during batch execution, isolate the error to that file and record an error string in the CSV result instead of crashing the whole run

## Scope Included In First Implementation

- Recursive SVS discovery
- Standard associated-image label extraction
- Classical image preprocessing for segmentation
- Projection-based line splitting
- Local handwritten OCR as primary path
- OpenAI fallback for difficult line images
- CSV export
- Batch error isolation

## Explicitly Out Of Scope For First Implementation

- Full-page or layout-aware OCR beyond label line extraction
- Heavy rule-based correction tied to a specific label naming format
- Training or fine-tuning a custom handwriting model
- Advanced skew correction unless a simple lightweight approach proves necessary during implementation
- GUI interface
- Database storage
- Distributed processing

## Initial Technical Assumptions

- Python will be used for the first implementation
- `openslide` is available or installable in the execution environment
- The OpenAI API key will be provided explicitly through the CLI when fallback OCR is enabled
- Labels mainly contain short handwritten lines rather than dense paragraphs

## Acceptance Criteria

- Given a directory with `.svs` files, the script finds them recursively and processes them in stable order
- For each SVS with a valid label image, the script outputs a CSV row
- The CSV contains `svs_filename` and `recognized_text`
- The CSV also contains `slide_path` relative to the input root directory
- `recognized_text` preserves line order from top to bottom
- A broken or unsupported SVS does not stop the whole batch
- When local OCR output is clearly poor, fallback OCR can be triggered
- The preview PNG is generated with the expected default size and ordering rules

## Operational Notes

- Python package entrypoint: `svs-label-ocr`
- Local OCR path uses `pytesseract` as the first implementation's local provider
- OpenAI fallback OCR is triggered only when the local result is suspicious or the local provider raises an exception
- `openslide-python` requires the system OpenSlide library in addition to the Python package; if the dylib is missing in a fresh environment, `pip install openslide-bin` is the quickest fix on macOS
- `pytesseract` requires the system `tesseract` binary to be installed and visible in `PATH`
- If OpenAI fallback is enabled, `OPENAI_API_KEY` must be present in the environment
- By default, preview output is written beside the CSV using the same stem plus `.preview.png`
- When OpenAI fallback is enabled, `--openai-api-key` must be provided explicitly
- The CLI prints a short run summary after batch completion

## Initial Usage Example

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .

svs-label-ocr \
  --input-dir /path/to/svs_root \
  --output-csv /path/to/output.csv \
  --openai-api-key YOUR_OPENAI_API_KEY
```

To set a custom preview output path:

```bash
svs-label-ocr \
  --input-dir /path/to/svs_root \
  --output-csv /path/to/output.csv \
  --openai-api-key YOUR_OPENAI_API_KEY \
  --preview-image /path/to/output.preview.png \
  --preview-rows 5
```

To disable OpenAI fallback and use only the local OCR path:

```bash
svs-label-ocr \
  --input-dir /path/to/svs_root \
  --output-csv /path/to/output.csv \
  --disable-openai-fallback
```
