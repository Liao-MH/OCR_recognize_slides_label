from svs_label_ocr.ocr import is_suspicious_ocr_result


def test_is_suspicious_ocr_result_flags_empty_text():
    assert is_suspicious_ocr_result("") is True
    assert is_suspicious_ocr_result("A123") is False
