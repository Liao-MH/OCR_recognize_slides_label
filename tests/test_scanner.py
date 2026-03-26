from pathlib import Path

from svs_label_ocr.scanner import find_svs_files


def test_find_svs_files_recursively_and_sorted(tmp_path: Path):
    (tmp_path / "b").mkdir()
    (tmp_path / "a").mkdir()
    (tmp_path / "b" / "case2.svs").write_text("")
    (tmp_path / "a" / "case1.svs").write_text("")
    (tmp_path / "a" / "ignore.txt").write_text("")

    result = find_svs_files(tmp_path)

    assert [path.name for path in result] == ["case1.svs", "case2.svs"]
