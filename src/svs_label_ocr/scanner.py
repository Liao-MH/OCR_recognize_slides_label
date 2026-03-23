from pathlib import Path


def find_svs_files(root: Path) -> list[Path]:
    """
    Return all `.svs` files below `root` in stable sorted order.

    The batch entrypoint depends on explicit failures for invalid inputs so the
    caller can stop early instead of silently scanning the wrong path.
    """
    if not root.exists():
        raise FileNotFoundError(f"Input directory not found: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"Input path is not a directory: {root}")
    return sorted(path for path in root.rglob("*.svs") if path.is_file())
