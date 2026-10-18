"""Создать воспроизводимые учебные ZIP локально, вне истории Git."""

from pathlib import Path
import zipfile


FIXTURES = {
    "minimal": {"hello.txt": b"hello\n"},
    "files": {
        "first.txt": b"one\ntwo\nthree\n",
        "second.txt": b"alpha\nbeta\n",
        "empty.txt": b"",
        "binary.bin": bytes(range(256)),
        "empty/": b"",
    },
    "deep": {
        "readme.txt": "Первая строка\nВторая строка\n".encode("utf-8"),
        "docs/notes.txt": b"one\ntwo\nthree\n",
        "docs/level2/level3/data.txt": b"deep\nfile\n",
        "empty/": b"",
        ".hidden": b"hidden\n",
        "binary.bin": bytes(range(256)),
    },
}


def create_archives(directory):
    """Записать три ZIP с постоянными датами записей."""
    directory.mkdir(parents=True, exist_ok=True)
    for name, files in FIXTURES.items():
        with zipfile.ZipFile(directory / f"{name}.zip", "w") as archive:
            for path, data in files.items():
                archive.writestr(zipfile.ZipInfo(path), data)


if __name__ == "__main__":
    create_archives(Path(__file__).resolve().parents[1] / "examples")
