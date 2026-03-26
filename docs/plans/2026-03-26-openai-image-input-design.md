# OpenAI Image Input Design

## Goal

Fix OpenAI fallback OCR so vision-capable models such as `gpt-4.1` receive cropped line images through the Responses API image-input path instead of the document/file-input path.

## Confirmed Decisions

- The fix should support `gpt-4.1` correctly.
- The OpenAI fallback should use a unified image-input path instead of branching by model name.
- The fallback should stop uploading PNG files through `input_file`.
- Existing CLI parameters should stay unchanged.
- Full batch error isolation should remain intact.

## Recommended Approach

Replace the current temporary-file plus `files.create()` flow with an in-memory PNG encoding flow that sends the line image directly as an `input_image` content item in `responses.create()`. This matches the actual task semantics: the model is being asked to read text from an image, not parse a document file.

The new request content should contain two items:

- `input_text` with the existing OCR prompt
- `input_image` with a PNG data URL derived from the current line image

This keeps the request self-contained, removes the unnecessary file-upload dependency, and avoids the unsupported `.png` document-input path that caused the `400 invalid_request_error`.

## Error Handling

If image encoding fails, the provider should raise that error directly. If the OpenAI API rejects a model or request, the error should still propagate to the existing per-slide isolation layer so the batch continues and the failure is recorded in the CSV, terminal output, and `.run.log`.
