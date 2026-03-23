from __future__ import annotations

from PIL import Image


def crop_and_upscale_line(
    image: Image.Image,
    span: tuple[int, int],
    *,
    margin: int = 2,
    scale: int = 2,
) -> Image.Image:
    """
    Crop one segmented line from a lightly processed source image and enlarge it.
    """
    start, end = span
    if start < 0 or end <= start or end > image.height:
        raise ValueError(f"Invalid line span for image height {image.height}: {span}")
    if margin < 0:
        raise ValueError("margin cannot be negative")
    if scale < 1:
        raise ValueError("scale must be at least 1")

    grayscale = image.convert("L")
    row_crop = grayscale.crop((0, start, grayscale.width, end))
    row_array = row_crop.load()

    dark_columns: list[int] = []
    for x in range(row_crop.width):
        for y in range(row_crop.height):
            if row_array[x, y] < 245:
                dark_columns.append(x)
                break

    if dark_columns:
        left = max(0, min(dark_columns) - margin)
        right = min(row_crop.width, max(dark_columns) + margin + 1)
    else:
        left = 0
        right = row_crop.width

    cropped = row_crop.crop((left, 0, right, row_crop.height))
    return cropped.resize(
        (max(1, cropped.width * scale), max(1, cropped.height * scale)),
        resample=Image.Resampling.LANCZOS,
    )
