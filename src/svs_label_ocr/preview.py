from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


CANVAS_SIZE = (4096, 4096)
BACKGROUND = (248, 248, 245)
GRID = (205, 205, 205)
TEXT_COLOR = (30, 30, 30)


@dataclass
class PreviewSlide:
    svs_filename: str
    slide_path: str
    recognized_text: str
    recognized_lines: list[str]
    wsi_thumbnail: Image.Image
    label_thumbnail: Image.Image


def _load_font(size: int) -> ImageFont.ImageFont:
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size=size)
    except OSError:
        return ImageFont.load_default()


def _fit_image(source: Image.Image, max_width: int, max_height: int) -> Image.Image:
    image = source.convert("RGB").copy()
    image.thumbnail((max_width, max_height))
    return image


def _wrap_single_line(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> list[str]:
    if not text:
        return [""]

    words = text.split(" ")
    wrapped: list[str] = []
    current = ""
    for word in words:
        candidate = word if not current else f"{current} {word}"
        if draw.textbbox((0, 0), candidate, font=font)[2] <= max_width:
            current = candidate
            continue
        if current:
            wrapped.append(current)
        if draw.textbbox((0, 0), word, font=font)[2] <= max_width:
            current = word
            continue

        # Character-wrap overly long tokens, but keep them within the same OCR line.
        piece = ""
        for character in word:
            candidate_piece = piece + character
            if draw.textbbox((0, 0), candidate_piece, font=font)[2] <= max_width:
                piece = candidate_piece
            else:
                if piece:
                    wrapped.append(piece)
                piece = character
        current = piece

    if current:
        wrapped.append(current)
    return wrapped


def _draw_text_block(
    draw: ImageDraw.ImageDraw,
    position: tuple[int, int],
    width: int,
    height: int,
    lines: list[str],
    *,
    font,
) -> None:
    x, y = position
    line_height = draw.textbbox((0, 0), "Ag", font=font)[3] + 12
    max_bottom = y + height

    for original_line in lines:
        for wrapped_line in _wrap_single_line(draw, original_line, font, width):
            if y + line_height > max_bottom:
                ellipsis = "..."
                draw.text((x, max_bottom - line_height), ellipsis, fill=TEXT_COLOR, font=font)
                return
            draw.text((x, y), wrapped_line, fill=TEXT_COLOR, font=font)
            y += line_height


def render_preview_image(
    output_path: Path,
    slides: list[PreviewSlide],
    *,
    preview_rows: int = 5,
) -> None:
    if preview_rows < 1:
        raise ValueError("preview_rows must be at least 1")
    if not slides:
        raise ValueError("At least one successful slide is required to render a preview")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas = Image.new("RGB", CANVAS_SIZE, BACKGROUND)
    draw = ImageDraw.Draw(canvas)
    font = _load_font(size=34)

    selected = slides[:preview_rows]
    row_height = CANVAS_SIZE[1] // len(selected)
    column_widths = (1120, 1120, CANVAS_SIZE[0] - 2240)
    padding = 36

    for index, slide in enumerate(selected):
        top = index * row_height
        bottom = CANVAS_SIZE[1] if index == len(selected) - 1 else top + row_height
        draw.line((0, bottom - 2, CANVAS_SIZE[0], bottom - 2), fill=GRID, width=3)

        wsi_cell = (padding, top + padding, column_widths[0] - 2 * padding, row_height - 2 * padding)
        label_left = column_widths[0] + padding
        label_cell = (
            label_left,
            top + padding,
            column_widths[1] - 2 * padding,
            row_height - 2 * padding,
        )
        text_left = column_widths[0] + column_widths[1] + padding
        text_width = column_widths[2] - 2 * padding
        text_height = row_height - 2 * padding

        for image, cell in (
            (slide.wsi_thumbnail, wsi_cell),
            (slide.label_thumbnail, label_cell),
        ):
            fitted = _fit_image(image, cell[2], cell[3])
            paste_x = cell[0] + (cell[2] - fitted.width) // 2
            paste_y = cell[1] + (cell[3] - fitted.height) // 2
            canvas.paste(fitted, (paste_x, paste_y))

        _draw_text_block(
            draw,
            (text_left, top + padding),
            text_width,
            text_height,
            slide.recognized_lines,
            font=font,
        )

    canvas.save(output_path)
