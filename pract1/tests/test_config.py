"""Проверки параметров и выполнения стартового скрипта."""

import contextlib
import io
from pathlib import Path
import tempfile
import unittest

from src.main import Shell, parse_options, run_script


class TestConfiguration(unittest.TestCase):
    """Проверить пути и продолжение после ошибочных строк."""

    def test_paths(self):
        """Оба пути передаются независимо."""
        options = parse_options(["--vfs", "a.zip", "--script", "b.txt"])
        self.assertEqual((options.vfs, options.script), ("a.zip", "b.txt"))

    def test_script_continues_and_stops(self):
        """Неизвестная команда пропускается, exit завершает скрипт."""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "commands.txt"
            path.write_text("unknown\nls\nexit\nNEVER\n", encoding="utf-8")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = run_script(Shell(), path)
        self.assertFalse(result)
        self.assertIn("неизвестная команда", output.getvalue())
        self.assertIn("ls", output.getvalue())
        self.assertNotIn("NEVER", output.getvalue())
