from PIL import Image

from svs_label_ocr.ocr import OpenAIFallbackOCRProvider


class DummyClient:
    def __init__(self):
        self.responses = DummyResponses()


class DummyResponses:
    def __init__(self):
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return DummyResponse()


class DummyResponse:
    output_text = "A1"


def test_openai_fallback_provider_accepts_explicit_api_key():
    provider = OpenAIFallbackOCRProvider(api_key="test-key", client=DummyClient())

    assert provider.api_key == "test-key"


def test_openai_fallback_provider_sends_line_image_as_input_image():
    client = DummyClient()
    provider = OpenAIFallbackOCRProvider(api_key="test-key", client=client, model="gpt-4.1")

    result = provider.recognize_line(Image.new("RGB", (8, 8), "white"))

    assert result == "A1"
    request = client.responses.calls[0]
    content = request["input"][0]["content"]
    assert any(item["type"] == "input_text" for item in content)
    image_items = [item for item in content if item["type"] == "input_image"]
    assert len(image_items) == 1
    assert image_items[0]["image_url"].startswith("data:image/png;base64,")
