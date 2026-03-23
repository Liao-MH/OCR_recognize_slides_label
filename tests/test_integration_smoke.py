import csv
from pathlib import Path

from PIL import Image, ImageDraw

from svs_label_ocr.export import process_batch


class DummySlide:
    def __init__(self, label):
        self.associated_images = {"label": label}

    def close(self):
        pass


class AlwaysSuspiciousProvider:
    def recognize_line(self, image):
        return ""


class SequenceProvider:
    def __init__(self, results):
        self.results = list(results)
        self.index = 0

    def recognize_line(self, image):
        result = self.results[self.index]
        self.index += 1
        return result


def build_label_image() -> Image.Image:
    image = Image.new("RGB", (120, 80), "white")
    draw = ImageDraw.Draw(image)
    draw.rectangle((15, 10, 95, 18), fill="black")
    draw.rectangle((20, 42, 85, 50), fill="black")
    return image


def test_process_batch_smoke_runs_end_to_end_with_fallback(tmp_path: Path):
    input_dir = tmp_path / "slides"
    input_dir.mkdir()
    (input_dir / "case1.svs").write_text("")
    output_csv = tmp_path / "result.csv"

    rows = process_batch(
        input_dir,
        output_csv,
        local_provider=AlwaysSuspiciousProvider(),
        fallback_provider=SequenceProvider(["Top", "Bottom"]),
        slide_opener=lambda path: DummySlide(build_label_image()),
    )

    assert rows == [{"svs_filename": "case1.svs", "recognized_text": "Top\nBottom"}]

    with output_csv.open(newline="", encoding="utf-8") as handle:
        data = list(csv.DictReader(handle))

    assert data[0]["recognized_text"] == "Top\nBottom"
