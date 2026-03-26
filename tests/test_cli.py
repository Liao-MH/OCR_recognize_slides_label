import pytest

from svs_label_ocr.cli import build_parser, validate_cli_args


def test_cli_requires_input_and_output_arguments():
    parser = build_parser()
    args = parser.parse_args(["--input-dir", "/tmp/in", "--output-csv", "/tmp/out.csv"])
    assert args.input_dir == "/tmp/in"
    assert args.output_csv == "/tmp/out.csv"


def test_cli_accepts_preview_arguments():
    parser = build_parser()

    args = parser.parse_args(
        [
            "--input-dir",
            "/tmp/in",
            "--output-csv",
            "/tmp/out.csv",
            "--preview-image",
            "/tmp/out.preview.png",
            "--preview-rows",
            "7",
        ]
    )

    assert args.preview_image == "/tmp/out.preview.png"
    assert args.preview_rows == 7


def test_cli_rejects_non_positive_preview_rows():
    parser = build_parser()

    with pytest.raises(SystemExit):
        parser.parse_args(
            [
                "--input-dir",
                "/tmp/in",
                "--output-csv",
                "/tmp/out.csv",
                "--preview-rows",
                "0",
            ]
        )


def test_cli_requires_explicit_openai_key_when_fallback_enabled():
    parser = build_parser()
    args = parser.parse_args(["--input-dir", "/tmp/in", "--output-csv", "/tmp/out.csv"])

    with pytest.raises(ValueError, match="--openai-api-key"):
        validate_cli_args(args)


def test_cli_accepts_explicit_openai_key():
    parser = build_parser()
    args = parser.parse_args(
        [
            "--input-dir",
            "/tmp/in",
            "--output-csv",
            "/tmp/out.csv",
            "--openai-api-key",
            "test-key",
        ]
    )

    validate_cli_args(args)


def test_cli_does_not_require_openai_key_when_fallback_disabled():
    parser = build_parser()
    args = parser.parse_args(
        [
            "--input-dir",
            "/tmp/in",
            "--output-csv",
            "/tmp/out.csv",
            "--disable-openai-fallback",
        ]
    )

    validate_cli_args(args)
