from PIL import Image

from svs_label_ocr.label_extractor import extract_label_image


class DummySlide:
    def __init__(self, label=None):
        self.associated_images = {}
        if label is not None:
            self.associated_images["label"] = label

    def close(self):
        pass


def test_extract_label_image_returns_label_copy():
    label = Image.new("RGB", (10, 10), "white")

    image = extract_label_image(slide=DummySlide(label=label))

    assert image.size == (10, 10)
