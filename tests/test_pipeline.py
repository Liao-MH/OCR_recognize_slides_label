from svs_label_ocr.pipeline import join_recognized_lines


def test_join_recognized_lines_preserves_top_to_bottom_order():
    assert join_recognized_lines(["Top", "Bottom"]) == "Top\nBottom"
