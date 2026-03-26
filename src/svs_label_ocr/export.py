from __future__ import annotations

import csv
import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, TextIO

from svs_label_ocr.ocr import OCRProvider
from svs_label_ocr.pipeline import open_slide, process_svs_file
from svs_label_ocr.preview import PreviewSlide, render_preview_image
from svs_label_ocr.scanner import find_svs_files


@dataclass
class BatchProcessResult:
    rows: list[dict[str, str]]
    total_svs: int
    success_count: int
    failure_count: int
    output_csv: Path
    preview_image: Optional[Path]
    preview_generated: bool
    run_log: Optional[Path] = None


def default_run_log_path(output_csv: Path) -> Path:
    return output_csv.with_name(f"{output_csv.stem}.run.log")


def _build_run_logger(run_log: Path) -> tuple[logging.Logger, logging.FileHandler]:
    run_log.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(f"svs_label_ocr.run.{run_log.resolve()}")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    logger.handlers.clear()

    handler = logging.FileHandler(run_log, mode="w", encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
    logger.addHandler(handler)
    return logger, handler


def _print_discovery_count(total_svs: int, stream: TextIO) -> None:
    stream.write(f"Discovered {total_svs} SVS files\n")
    stream.flush()


def _print_progress(current_index: int, total_svs: int, slide_path: str, stream: TextIO) -> None:
    stream.write(f"\rProcessing {current_index}/{total_svs} | {slide_path}")
    stream.flush()


def _finish_progress_line(stream: TextIO, *, active: bool) -> bool:
    if active:
        stream.write("\n")
        stream.flush()
    return False


def _print_failure(
    current_index: int,
    total_svs: int,
    slide_path: str,
    exc: Exception,
    stream: TextIO,
) -> None:
    stream.write(
        f"ERROR {current_index}/{total_svs} | {slide_path} | {exc.__class__.__name__}: {exc}\n"
    )
    stream.flush()


def write_results_csv(output_path: Path, rows: list[dict[str, str]]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["svs_filename", "slide_path", "recognized_text"],
        )
        writer.writeheader()
        writer.writerows(rows)


def process_batch(
    input_dir: Path,
    output_csv: Path,
    *,
    local_provider: OCRProvider,
    fallback_provider: Optional[OCRProvider] = None,
    slide_opener=None,
    preview_image: Optional[Path] = None,
    preview_rows: int = 5,
    progress_stream: Optional[TextIO] = None,
    error_stream: Optional[TextIO] = None,
) -> BatchProcessResult:
    run_log = default_run_log_path(output_csv)
    logger, handler = _build_run_logger(run_log)
    rows: list[dict[str, str]] = []
    preview_slides: list[PreviewSlide] = []
    progress_stream = sys.stdout if progress_stream is None else progress_stream
    error_stream = progress_stream if error_stream is None else error_stream
    progress_line_active = False
    try:
        logger.info(
            "Batch started: input_dir=%s output_csv=%s preview_image=%s preview_rows=%s",
            input_dir,
            output_csv,
            preview_image,
            preview_rows,
        )
        try:
            svs_paths = find_svs_files(input_dir)
        except Exception:
            logger.exception("Failed to discover SVS files under %s", input_dir)
            raise

        logger.info("Discovered %s SVS files", len(svs_paths))
        _print_discovery_count(len(svs_paths), progress_stream)
        for index, svs_path in enumerate(svs_paths, start=1):
            relative_slide_path = str(svs_path.relative_to(input_dir))
            _print_progress(index, len(svs_paths), relative_slide_path, progress_stream)
            progress_line_active = True
            logger.info(
                "Processing slide: slide_path=%s svs_filename=%s",
                relative_slide_path,
                svs_path.name,
            )
            try:
                result = process_svs_file(
                    svs_path,
                    local_provider=local_provider,
                    fallback_provider=fallback_provider,
                    slide_opener=slide_opener or open_slide,
                )
                recognized_text = result.recognized_text
                preview_slides.append(
                    PreviewSlide(
                        svs_filename=svs_path.name,
                        slide_path=relative_slide_path,
                        recognized_text=result.recognized_text,
                        recognized_lines=result.recognized_lines,
                        wsi_thumbnail=result.wsi_thumbnail,
                        label_thumbnail=result.label_image,
                    )
                )
                logger.info(
                    "Processed slide successfully: slide_path=%s svs_filename=%s recognized_lines=%s recognized_chars=%s",
                    relative_slide_path,
                    svs_path.name,
                    len(result.recognized_lines),
                    len(result.recognized_text),
                )
            except Exception as exc:
                # Per-slide failures stay isolated in CSV, but the runtime log keeps
                # the full traceback so large batch failures remain debuggable.
                recognized_text = f"ERROR: {exc}"
                progress_line_active = _finish_progress_line(progress_stream, active=progress_line_active)
                _print_failure(index, len(svs_paths), relative_slide_path, exc, error_stream)
                logger.exception(
                    "Failed to process slide: slide_path=%s svs_filename=%s error_type=%s error=%s",
                    relative_slide_path,
                    svs_path.name,
                    exc.__class__.__name__,
                    exc,
                )

            rows.append(
                {
                    "svs_filename": svs_path.name,
                    "slide_path": relative_slide_path,
                    "recognized_text": recognized_text,
                }
            )

        progress_line_active = _finish_progress_line(progress_stream, active=progress_line_active)
        write_results_csv(output_csv, rows)
        logger.info("Wrote CSV output: path=%s rows=%s", output_csv, len(rows))

        preview_generated = False
        if preview_image is not None and preview_slides:
            logger.info(
                "Generating preview image: path=%s preview_rows=%s successful_slides=%s",
                preview_image,
                preview_rows,
                len(preview_slides),
            )
            try:
                render_preview_image(preview_image, preview_slides, preview_rows=preview_rows)
            except Exception:
                logger.exception("Failed to generate preview image at %s", preview_image)
                raise
            preview_generated = True
            logger.info("Generated preview image: path=%s", preview_image)
        else:
            logger.info(
                "Skipped preview generation: preview_image=%s successful_slides=%s",
                preview_image,
                len(preview_slides),
            )

        result = BatchProcessResult(
            rows=rows,
            total_svs=len(svs_paths),
            success_count=len(preview_slides),
            failure_count=len(svs_paths) - len(preview_slides),
            output_csv=output_csv,
            run_log=run_log,
            preview_image=preview_image,
            preview_generated=preview_generated,
        )
        logger.info(
            "Batch finished: total=%s successful=%s failed=%s csv=%s preview=%s run_log=%s",
            result.total_svs,
            result.success_count,
            result.failure_count,
            result.output_csv,
            result.preview_image if result.preview_generated else "skipped",
            result.run_log,
        )
        return result
    finally:
        _finish_progress_line(progress_stream, active=progress_line_active)
        logger.removeHandler(handler)
        handler.close()
