"""Проверки загрузки VFS, уровней вложенности и двоичных файлов."""

from pathlib import Path
import tempfile
import unittest
import zipfile

from scripts.create_vfs import create_archives
from src.vfs import VirtualFileSystem


class TestVFS(unittest.TestCase):
    """Проверить ZIP без распаковки и изменения исходных данных."""

    def setUp(self):
        """Создать независимые временные архивы для каждого теста."""
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        create_archives(self.root)

    def test_three_layouts(self):
        """Прочитать минимальную, плоскую и вложенную VFS."""
        for name in ("minimal", "files", "deep"):
            with self.subTest(name=name):
                path = self.root / f"{name}.zip"
                before = path.read_bytes()
                vfs = VirtualFileSystem(path)
                self.assertTrue(vfs.list_directory("/"))
                self.assertEqual(path.read_bytes(), before)
        self.assertFalse((self.root / "docs").exists())

    def test_binary_and_deep_paths(self):
        """Base64 сохраняет все байты, неявные каталоги существуют."""
        vfs = VirtualFileSystem(self.root / "deep.zip")
        self.assertEqual(vfs.read_file("/binary.bin"), bytes(range(256)))
        self.assertEqual(vfs.list_directory("/docs/level2/level3"),
                         ["data.txt"])
        self.assertEqual(vfs.normalize("../../x", "/"), "/x")

    def test_unsafe_archive(self):
        """Путь с выходом из корня отклоняется без распаковки."""
        path = self.root / "unsafe.zip"
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr("../outside.txt", "bad")
        with self.assertRaises(ValueError):
            VirtualFileSystem(path)
        self.assertFalse((self.root / "outside.txt").exists())
