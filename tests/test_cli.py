from svs_label_ocr.cli import build_parser


def test_cli_requires_input_and_output_arguments():
    parser = build_parser()
    args = parser.parse_args(["--input-dir", "/tmp/in", "--output-csv", "/tmp/out.csv"])
    assert args.input_dir == "/tmp/in"
    assert args.output_csv == "/tmp/out.csv"
