from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from PIL import Image, ImageFilter, ImageOps


@dataclass(frozen=True)
class PreparedLabelImage:
    cropped_rgb: Image.Image
    grayscale: Image.Image
    binary: np.ndarray


def _validate_image(image: Image.Image) -> None:
    if image.width <= 0 or image.height <= 0:
        raise ValueError("Label image must have non-zero width and height")


def _crop_dark_border(image: Image.Image, *, threshold: int = 20) -> Image.Image:
    rgb = image.convert("RGB")
    array = np.asarray(rgb, dtype=np.uint8)
    non_dark_mask = np.any(array > threshold, axis=2)

    if not np.any(non_dark_mask):
        raise ValueError("Label image is entirely black after border inspection")

    rows = np.where(non_dark_mask.any(axis=1))[0]
    cols = np.where(non_dark_mask.any(axis=0))[0]
    top, bottom = int(rows[0]), int(rows[-1]) + 1
    left, right = int(cols[0]), int(cols[-1]) + 1
    return rgb.crop((left, top, right, bottom))


def _otsu_threshold(grayscale: np.ndarray) -> int:
    histogram = np.bincount(grayscale.ravel(), minlength=256).astype(np.float64)
    total = grayscale.size
    if total == 0:
        raise ValueError("Cannot threshold an empty grayscale image")

    sum_total = np.dot(np.arange(256), histogram)
    sum_background = 0.0
    weight_background = 0.0
    best_threshold = 0
    best_variance = -1.0

    for threshold in range(256):
        weight_background += histogram[threshold]
        if weight_background == 0:
            continue
        weight_foreground = total - weight_background
        if weight_foreground == 0:
            break

        sum_background += threshold * histogram[threshold]
        mean_background = sum_background / weight_background
        mean_foreground = (sum_total - sum_background) / weight_foreground
        between_class_variance = (
            weight_background
            * weight_foreground
            * (mean_background - mean_foreground) ** 2
        )
        if between_class_variance > best_variance:
            best_variance = between_class_variance
            best_threshold = threshold

    return best_threshold


def prepare_label_image(image: Image.Image) -> PreparedLabelImage:
    """
    Prepare the label for both segmentation and later line cropping.

    We crop obvious black scanner borders first so downstream projection and OCR
    run on the content region instead of large uniform margins.
    """
    _validate_image(image)
    cropped_rgb = _crop_dark_border(image)
    grayscale = ImageOps.grayscale(cropped_rgb)
    denoised = grayscale.filter(ImageFilter.MedianFilter(size=3))
    contrasted = ImageOps.autocontrast(denoised)

    gray_array = np.asarray(contrasted, dtype=np.uint8)
    threshold = _otsu_threshold(gray_array)
    binary = np.where(gray_array <= threshold, 0, 255).astype(np.uint8)

    # A light open removes isolated single-pixel noise while keeping strokes.
    opened = Image.fromarray(binary).filter(ImageFilter.MinFilter(size=3)).filter(
        ImageFilter.MaxFilter(size=3)
    )
    return PreparedLabelImage(
        cropped_rgb=cropped_rgb,
        grayscale=contrasted,
        binary=np.asarray(opened, dtype=np.uint8),
    )


def preprocess_label_for_segmentation(image: Image.Image) -> np.ndarray:
    return prepare_label_image(image).binary
