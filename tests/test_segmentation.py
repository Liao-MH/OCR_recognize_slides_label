import numpy as np

from svs_label_ocr.segmentation import find_text_line_spans


def test_find_text_line_spans_detects_two_lines():
    binary = np.full((40, 20), 255, dtype=np.uint8)
    binary[5:10, 2:18] = 0
    binary[25:30, 2:18] = 0

    spans = find_text_line_spans(binary, min_ink_per_row=3, min_line_height=3, max_merge_gap=2)

    assert spans == [(5, 10), (25, 30)]
