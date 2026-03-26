from __future__ import annotations

from tempfile import NamedTemporaryFile
from typing import Optional, Protocol

from PIL import Image


DEFAULT_OPENAI_PROMPT = (
    "Read only the handwritten text in this image and return only that text. "
    "Do not add explanations."
)


class OCRProvider(Protocol):
    def recognize_line(self, image: Image.Image) -> str:
        ...


def normalize_ocr_text(text: str) -> str:
    lines = [" ".join(part.split()) for part in text.replace("\r\n", "\n").split("\n")]
    return "\n".join(line for line in lines if line).strip()


def is_suspicious_ocr_result(text: str) -> bool:
    normalized = normalize_ocr_text(text)
    if not normalized:
        return True
    if len(normalized) <= 1:
        return True

    alnum_count = sum(character.isalnum() for character in normalized)
    if alnum_count == 0:
        return True

    symbol_count = sum(
        not character.isalnum() and not character.isspace() for character in normalized
    )
    return symbol_count > alnum_count


class PytesseractOCRProvider:
    def __init__(self, *, language: str = "eng", page_segmentation_mode: int = 7) -> None:
        self.language = language
        self.page_segmentation_mode = page_segmentation_mode

    def recognize_line(self, image: Image.Image) -> str:
        try:
            import pytesseract
        except ImportError as exc:  # pragma: no cover - depends on system install
            raise ImportError(
                "pytesseract is required for local OCR. Install pytesseract and the "
                "system tesseract binary."
            ) from exc

        result = pytesseract.image_to_string(
            image,
            lang=self.language,
            config=f"--psm {self.page_segmentation_mode}",
        )
        return normalize_ocr_text(result)


class OpenAIFallbackOCRProvider:
    def __init__(
        self,
        *,
        api_key: str,
        model: str = "gpt-5",
        prompt: str = DEFAULT_OPENAI_PROMPT,
        client=None,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.prompt = prompt
        self._client = client

    @property
    def client(self):
        if self._client is None:  # pragma: no cover - network path not exercised in tests
            try:
                from openai import OpenAI
            except ImportError as exc:
                raise ImportError("openai package is required for OpenAI fallback OCR") from exc
            self._client = OpenAI(api_key=self.api_key)
        return self._client

    def recognize_line(self, image: Image.Image) -> str:
        # The official Responses API supports uploaded files as input. We upload
        # the cropped line image and prompt the model to return only the text.
        with NamedTemporaryFile(suffix=".png") as handle:  # pragma: no cover - network path
            image.save(handle.name, format="PNG")
            with open(handle.name, "rb") as image_handle:
                uploaded_file = self.client.files.create(
                    file=image_handle,
                    purpose="user_data",
                )

        response = self.client.responses.create(
            model=self.model,
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_file", "file_id": uploaded_file.id},
                        {"type": "input_text", "text": self.prompt},
                    ],
                }
            ],
        )
        return normalize_ocr_text(response.output_text)


def recognize_line_with_fallback(
    image: Image.Image,
    *,
    local_provider: OCRProvider,
    fallback_provider: Optional[OCRProvider] = None,
) -> str:
    try:
        local_text = normalize_ocr_text(local_provider.recognize_line(image))
    except Exception:
        if fallback_provider is None:
            raise
        return normalize_ocr_text(fallback_provider.recognize_line(image))

    if is_suspicious_ocr_result(local_text) and fallback_provider is not None:
        return normalize_ocr_text(fallback_provider.recognize_line(image))
    return local_text
