from __future__ import annotations

import argparse
from pathlib import Path

from svs_label_ocr.export import process_batch
from svs_label_ocr.ocr import DEFAULT_OPENAI_PROMPT, OpenAIFallbackOCRProvider, PytesseractOCRProvider


def build_parser() -> argparse.ArgumentParser:
    """Create the minimal CLI contract required by the first implementation step."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--output-csv", required=True)
    parser.add_argument("--tesseract-language", default="eng")
    parser.add_argument("--disable-openai-fallback", action="store_true")
    parser.add_argument("--openai-model", default="gpt-5")
    parser.add_argument("--openai-prompt", default=DEFAULT_OPENAI_PROMPT)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    local_provider = PytesseractOCRProvider(language=args.tesseract_language)
    fallback_provider = None
    if not args.disable_openai_fallback:
        fallback_provider = OpenAIFallbackOCRProvider(
            model=args.openai_model,
            prompt=args.openai_prompt,
        )

    process_batch(
        Path(args.input_dir),
        Path(args.output_csv),
        local_provider=local_provider,
        fallback_provider=fallback_provider,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
