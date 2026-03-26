from svs_label_ocr.ocr import OpenAIFallbackOCRProvider


class DummyClient:
    pass


def test_openai_fallback_provider_accepts_explicit_api_key():
    provider = OpenAIFallbackOCRProvider(api_key="test-key", client=DummyClient())

    assert provider.api_key == "test-key"
