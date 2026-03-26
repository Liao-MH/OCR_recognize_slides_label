import io
from pathlib import Path

from PIL import Image

from svs_label_ocr.export import process_batch


class DummySlide:
    def __init__(self):
        self.associated_images = {"label": Image.new("RGB", (50, 30), "white")}
        self._thumbnail = Image.new("RGB", (100, 60), "gray")

    def close(self):
        pass

    def get_thumbnail(self, size):
        image = self._thumbnail.copy()
        image.thumbnail(size)
        return image


class GoodProvider:
    def recognize_line(self, image):
        return "A1"


def test_process_batch_prints_live_progress_and_failures(tmp_path: Path):
    input_dir = tmp_path / "slides"
    input_dir.mkdir()
    (input_dir / "ok.svs").write_text("")
    (input_dir / "bad.svs").write_text("")
    output_csv = tmp_path / "result.csv"
    progress_stream = io.StringIO()
    error_stream = io.StringIO()

    result = process_batch(
        input_dir,
        output_csv,
        local_provider=GoodProvider(),
        slide_opener=lambda path: DummySlide() if path.name == "ok.svs" else (_ for _ in ()).throw(ValueError("broken slide")),
        progress_stream=progress_stream,
        error_stream=error_stream,
    )

    assert result.total_svs == 2
    assert result.success_count == 1
    assert result.failure_count == 1
    assert "Processing 1/2 | bad.svs" in progress_stream.getvalue()
    assert "Processing 2/2 | ok.svs" in progress_stream.getvalue()
    assert progress_stream.getvalue().endswith("\n")
    assert "ERROR 1/2 | bad.svs | ValueError: broken slide" in error_stream.getvalue()
