from pathlib import Path

from svs_label_ocr.cli import format_run_summary
from svs_label_ocr.export import BatchProcessResult


def test_format_run_summary_includes_counts_and_output_paths(tmp_path: Path):
    csv_path = tmp_path / "result.csv"
    preview_path = tmp_path / "result.preview.png"
    summary = BatchProcessResult(
        rows=[],
        total_svs=8,
        success_count=6,
        failure_count=2,
        output_csv=csv_path,
        preview_image=preview_path,
        preview_generated=True,
    )

    text = format_run_summary(summary)

    assert "Total SVS files: 8" in text
    assert "Successful: 6" in text
    assert "Failed: 2" in text
    assert str(csv_path) in text
    assert str(preview_path) in text
