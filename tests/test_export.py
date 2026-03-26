import csv

from svs_label_ocr.export import write_results_csv


def test_write_results_csv_preserves_newlines(tmp_path):
    output = tmp_path / "result.csv"
    rows = [
        {
            "svs_filename": "a.svs",
            "slide_path": "nested/a.svs",
            "recognized_text": "L1\nL2",
        }
    ]

    write_results_csv(output, rows)

    with output.open(newline="", encoding="utf-8") as handle:
        data = list(csv.DictReader(handle))

    assert data[0]["slide_path"] == "nested/a.svs"
    assert data[0]["recognized_text"] == "L1\nL2"
