from __future__ import annotations

import csv
from pathlib import Path
from typing import Optional

from svs_label_ocr.ocr import OCRProvider
from svs_label_ocr.pipeline import open_slide, process_svs_file
from svs_label_ocr.scanner import find_svs_files


def write_results_csv(output_path: Path, rows: list[dict[str, str]]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["svs_filename", "recognized_text"])
        writer.writeheader()
        writer.writerows(rows)


def process_batch(
    input_dir: Path,
    output_csv: Path,
    *,
    local_provider: OCRProvider,
    fallback_provider: Optional[OCRProvider] = None,
    slide_opener=None,
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for svs_path in find_svs_files(input_dir):
        try:
            recognized_text = process_svs_file(
                svs_path,
                local_provider=local_provider,
                fallback_provider=fallback_provider,
                slide_opener=slide_opener or open_slide,
            )
        except Exception as exc:
            recognized_text = f"ERROR: {exc}"

        rows.append(
            {
                "svs_filename": svs_path.name,
                "recognized_text": recognized_text,
            }
        )

    write_results_csv(output_csv, rows)
    return rows
