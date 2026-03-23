from __future__ import annotations

import numpy as np


def _validate_binary_image(binary: np.ndarray) -> None:
    if binary.ndim != 2:
        raise ValueError("Binary image for segmentation must be 2-dimensional")
    if binary.size == 0:
        raise ValueError("Binary image for segmentation cannot be empty")


def _merge_spans(spans: list[tuple[int, int]], max_merge_gap: int) -> list[tuple[int, int]]:
    if not spans:
        return []

    merged = [spans[0]]
    for start, end in spans[1:]:
        previous_start, previous_end = merged[-1]
        if start - previous_end <= max_merge_gap:
            merged[-1] = (previous_start, end)
        else:
            merged.append((start, end))
    return merged


def find_text_line_spans(
    binary: np.ndarray,
    *,
    min_ink_per_row: int = 3,
    min_line_height: int = 3,
    max_merge_gap: int = 2,
) -> list[tuple[int, int]]:
    """
    Detect text lines from a binary image where dark pixels are treated as ink.
    """
    _validate_binary_image(binary)
    if min_ink_per_row < 1:
        raise ValueError("min_ink_per_row must be at least 1")
    if min_line_height < 1:
        raise ValueError("min_line_height must be at least 1")
    if max_merge_gap < 0:
        raise ValueError("max_merge_gap cannot be negative")

    ink_per_row = np.count_nonzero(binary < 128, axis=1)
    text_rows = ink_per_row >= min_ink_per_row

    spans: list[tuple[int, int]] = []
    start: int | None = None
    for row_index, has_text in enumerate(text_rows):
        if has_text and start is None:
            start = row_index
        elif not has_text and start is not None:
            spans.append((start, row_index))
            start = None

    if start is not None:
        spans.append((start, binary.shape[0]))

    filtered = [span for span in spans if span[1] - span[0] >= min_line_height]
    return _merge_spans(filtered, max_merge_gap)
