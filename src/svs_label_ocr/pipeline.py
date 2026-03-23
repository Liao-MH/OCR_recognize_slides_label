from __future__ import annotations

from pathlib import Path
from typing import Optional

from PIL import Image

from svs_label_ocr.label_extractor import extract_label_image
from svs_label_ocr.line_images import crop_and_upscale_line
from svs_label_ocr.ocr import OCRProvider, recognize_line_with_fallback
from svs_label_ocr.preprocess import prepare_label_image
from svs_label_ocr.segmentation import find_text_line_spans


def join_recognized_lines(lines: list[str]) -> str:
    cleaned = [" ".join(line.split()) for line in lines if line and line.strip()]
    return "\n".join(cleaned)


def process_label_image(
    label_image: Image.Image,
    *,
    local_provider: OCRProvider,
    fallback_provider: Optional[OCRProvider] = None,
    min_ink_per_row: int = 3,
    min_line_height: int = 3,
    max_merge_gap: int = 2,
    crop_margin: int = 2,
    upscale_factor: int = 3,
) -> str:
    prepared = prepare_label_image(label_image)
    spans = find_text_line_spans(
        prepared.binary,
        min_ink_per_row=min_ink_per_row,
        min_line_height=min_line_height,
        max_merge_gap=max_merge_gap,
    )

    recognized_lines: list[str] = []
    for span in spans:
        line_image = crop_and_upscale_line(
            prepared.grayscale,
            span,
            margin=crop_margin,
            scale=upscale_factor,
        )
        recognized_lines.append(
            recognize_line_with_fallback(
                line_image,
                local_provider=local_provider,
                fallback_provider=fallback_provider,
            )
        )

    return join_recognized_lines(recognized_lines)


def open_slide(path: Path):
    try:
        import openslide
    except ImportError as exc:  # pragma: no cover - depends on system install
        raise ImportError(
            "openslide-python is required to open .svs files, and the system "
            "OpenSlide library must also be installed."
        ) from exc

    return openslide.OpenSlide(str(path))


def process_svs_file(
    svs_path: Path,
    *,
    local_provider: OCRProvider,
    fallback_provider: Optional[OCRProvider] = None,
    slide_opener=open_slide,
) -> str:
    slide = slide_opener(svs_path)
    try:
        label_image = extract_label_image(slide=slide)
        return process_label_image(
            label_image,
            local_provider=local_provider,
            fallback_provider=fallback_provider,
        )
    finally:
        close = getattr(slide, "close", None)
        if callable(close):
            close()
