"""Проверки результатов команд, путей и обработки ошибок."""

import contextlib
import io
from pathlib import Path
import platform
import tempfile
import unittest

from scripts.create_vfs import create_archives
from src.main import Shell


class TestCommands(unittest.TestCase):
    """Запускать команды с независимой VFS."""

    def setUp(self):
        """Загрузить вложенный учебный архив."""
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        create_archives(self.root)
        self.shell = Shell(self.root / "deep.zip")

    def execute(self, line):
        """Перехватить вывод одной команды."""
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = self.shell.execute(line)
        return result, output.getvalue()

    def test_listing_and_navigation(self):
        """Проверить относительные пути, корень и пустой каталог."""
        self.assertIn("docs\n", self.execute("ls")[1])
        self.assertNotIn(".hidden", self.execute("ls")[1])
        self.execute("cd docs/level2/level3")
        self.assertEqual(self.execute("ls")[1], "data.txt\n")
        self.execute("cd ../../..")
        self.assertEqual(self.shell.cwd, "/")
        self.assertEqual(self.execute("ls /empty")[1], "")
        self.assertEqual(self.execute("ls /readme.txt")[1], "readme.txt\n")
        self.execute("cd docs")
        self.execute("cd")
        self.assertEqual(self.shell.cwd, "/")

    def test_tac_and_uname(self):
        """Проверить порядок строк и реальное название ОС."""
        self.assertEqual(self.execute("tac docs/notes.txt")[1],
                         "three\ntwo\none\n")
        self.assertEqual(self.execute("uname")[1], platform.system() + "\n")
        text = self.execute("tac docs/notes.txt readme.txt")[1]
        expected = "three\ntwo\none\nВторая строка\nПервая строка\n"
        self.assertEqual(text, expected)

    def test_errors_keep_shell_alive(self):
        """Ошибочные команды не завершают сеанс и не меняют каталог."""
        lines = ["ls /missing", "ls a b", "cd readme.txt", "cd missing",
                 "cd a b", "tac", "tac binary.bin", "tac /empty",
                 "uname -a", "unknown", "exit wrong", "ls -l", "cd -x"]
        for line in lines:
            with self.subTest(line=line):
                running, output = self.execute(line)
                self.assertTrue(running)
                self.assertIn("Ошибка:", output)
                self.assertEqual(self.shell.cwd, "/")
        self.assertFalse(self.execute("exit")[0])

    def test_tac_continues_after_missing_file(self):
        """Ошибка одного файла не мешает обработке следующего."""
        output = self.execute("tac missing docs/notes.txt")[1]
        self.assertIn("Ошибка:", output)
        self.assertTrue(output.endswith("three\ntwo\none\n"))
