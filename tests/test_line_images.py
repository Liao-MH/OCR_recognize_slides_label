from PIL import Image, ImageDraw

from svs_label_ocr.line_images import crop_and_upscale_line


def test_crop_and_upscale_line_returns_larger_image():
    image = Image.new("L", (80, 30), "white")
    draw = ImageDraw.Draw(image)
    draw.rectangle((20, 10, 40, 18), fill="black")

    line = crop_and_upscale_line(image, (8, 20), margin=2, scale=2)

    assert line.size[0] > 20
    assert line.size[1] > 8
