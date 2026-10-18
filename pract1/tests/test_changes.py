"""Проверки rm и touch, сохранности ZIP и физических файлов."""

import contextlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.create_vfs import create_archives
from src.main import Shell
from src.vfs import VirtualFileSystem


class TestChanges(unittest.TestCase):
    """Каждый тест использует отдельный архив."""

    def setUp(self):
        """Создать архив и сохранить его исходные байты."""
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        create_archives(self.root)
        self.path = self.root / "deep.zip"
        self.original = self.path.read_bytes()
        self.shell = Shell(self.path)

    def execute(self, line):
        """Выполнить строку с перехватом вывода."""
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.shell.execute(line)
        return output.getvalue()

    def test_create_touch_remove(self):
        """Создание и удаление меняют только память текущего сеанса."""
        self.execute("cd docs")
        self.execute("touch new.txt another.txt")
        self.assertEqual(self.shell.vfs.read_file("/docs/new.txt"), b"")
        original = self.shell.vfs.read_file("/docs/notes.txt")
        with patch("src.vfs.time.time", return_value=12345):
            self.execute("touch notes.txt")
        self.assertEqual(self.shell.vfs.modified["/docs/notes.txt"], 12345)
        self.assertEqual(self.shell.vfs.read_file("/docs/notes.txt"), original)
        self.execute("rm new.txt another.txt notes.txt")
        self.assertEqual(self.shell.vfs.list_directory("/docs"), ["level2"])
        self.assertEqual(self.path.read_bytes(), self.original)
        fresh = VirtualFileSystem(self.path)
        self.assertEqual(fresh.read_file("/docs/notes.txt"), original)
        self.assertNotIn("/docs/new.txt", fresh.files)
        self.assertFalse((self.root / "docs").exists())

    def test_errors_and_multiple_paths(self):
        """Каталоги защищены, отсутствующие родители не создаются."""
        for line in ("rm", "touch", "rm /docs", "rm /missing",
                     "touch /missing/file", "touch /readme.txt/child",
                     "rm -r /docs", "touch -x"):
            with self.subTest(line=line):
                self.assertIn("Ошибка:", self.execute(line))
        self.execute("touch /empty")
        self.assertIn("/empty", self.shell.vfs.directories)
        self.execute("touch /missing/child /ok.txt")
        self.assertIn("/ok.txt", self.shell.vfs.files)
        self.execute("rm /missing /ok.txt")
        self.assertNotIn("/ok.txt", self.shell.vfs.files)
        self.assertEqual(self.path.read_bytes(), self.original)

    def test_host_file_is_untouched(self):
        """Абсолютный путь команды относится к VFS, а не к диску ОС."""
        sentinel = self.root / "host.txt"
        sentinel.write_text("keep", encoding="utf-8")
        self.assertIn("Ошибка:", self.execute(f"rm {sentinel}"))
        self.assertIn("Ошибка:", self.execute(f"touch {sentinel}"))
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep")
