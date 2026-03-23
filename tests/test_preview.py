from pathlib import Path

from PIL import Image

from svs_label_ocr.preview import PreviewSlide, render_preview_image


def make_preview_slide(index: int) -> PreviewSlide:
    thumbnail = Image.new("RGB", (200, 120), (240, 240, 240))
    label = Image.new("RGB", (160, 90), (255, 255, 255))
    return PreviewSlide(
        svs_filename=f"case{index}.svs",
        slide_path=f"nested/case{index}.svs",
        recognized_text=f"Top {index}\nBottom {index}",
        recognized_lines=[f"Top {index}", f"Bottom {index}"],
        wsi_thumbnail=thumbnail,
        label_thumbnail=label,
    )


def test_render_preview_image_creates_4096_square_preview(tmp_path: Path):
    output = tmp_path / "preview.png"

    render_preview_image(output, [make_preview_slide(1)])

    image = Image.open(output)
    assert image.size == (4096, 4096)


def test_render_preview_image_uses_only_first_requested_successes(tmp_path: Path):
    output = tmp_path / "preview.png"
    slides = [make_preview_slide(index) for index in range(6)]

    render_preview_image(output, slides, preview_rows=5)

    image = Image.open(output)
    assert image.size == (4096, 4096)
    assert output.exists()
