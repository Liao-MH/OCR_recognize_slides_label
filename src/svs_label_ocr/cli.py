from __future__ import annotations

import argparse
from pathlib import Path

from svs_label_ocr.export import process_batch
from svs_label_ocr.ocr import DEFAULT_OPENAI_PROMPT, OpenAIFallbackOCRProvider, PytesseractOCRProvider


def _positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("preview row count must be at least 1")
    return parsed


def _default_preview_path(output_csv: Path) -> Path:
    return output_csv.with_name(f"{output_csv.stem}.preview.png")


def validate_cli_args(args) -> None:
    if not args.disable_openai_fallback and not args.openai_api_key:
        raise ValueError("--openai-api-key is required unless --disable-openai-fallback is set")


def format_run_summary(summary) -> str:
    lines = [
        f"Total SVS files: {summary.total_svs}",
        f"Successful: {summary.success_count}",
        f"Failed: {summary.failure_count}",
        f"CSV output: {summary.output_csv}",
    ]
    if summary.run_log is not None:
        lines.append(f"Run log: {summary.run_log}")
    if summary.preview_generated and summary.preview_image is not None:
        lines.append(f"Preview output: {summary.preview_image}")
    else:
        lines.append("Preview output: skipped")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    """Create the minimal CLI contract required by the first implementation step."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--output-csv", required=True)
    parser.add_argument("--tesseract-language", default="eng")
    parser.add_argument("--disable-openai-fallback", action="store_true")
    parser.add_argument("--openai-api-key")
    parser.add_argument("--openai-model", default="gpt-5")
    parser.add_argument("--openai-prompt", default=DEFAULT_OPENAI_PROMPT)
    parser.add_argument("--preview-image")
    parser.add_argument("--preview-rows", type=_positive_int, default=5)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    validate_cli_args(args)
    output_csv = Path(args.output_csv)

    local_provider = PytesseractOCRProvider(language=args.tesseract_language)
    fallback_provider = None
    if not args.disable_openai_fallback:
        fallback_provider = OpenAIFallbackOCRProvider(
            api_key=args.openai_api_key,
            model=args.openai_model,
            prompt=args.openai_prompt,
        )

    summary = process_batch(
        Path(args.input_dir),
        output_csv,
        local_provider=local_provider,
        fallback_provider=fallback_provider,
        preview_image=Path(args.preview_image) if args.preview_image else _default_preview_path(output_csv),
        preview_rows=args.preview_rows,
    )
    print(format_run_summary(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
