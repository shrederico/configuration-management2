"""Проверки запуска отдельного процесса и пользовательских сценариев."""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts.create_vfs import create_archives


ROOT = Path(__file__).resolve().parents[1]


class TestIntegration(unittest.TestCase):
    """Проверить настоящий вход приложения без подмены команд."""

    def setUp(self):
        """Создать временные входные данные."""
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        create_archives(self.root)

    def launch(self, arguments=(), user_input=""):
        """Запустить приложение и дождаться завершения."""
        return subprocess.run(
            [sys.executable, str(ROOT / "src/main.py"), *arguments],
            input=user_input, text=True, capture_output=True, timeout=5,
            cwd=self.root,
        )

    def test_interactive(self):
        """Проверить пустой ввод, ошибку, работу VFS и выход."""
        result = self.launch(
            ["--vfs", str(self.root / "deep.zip")],
            "\n   \nunknown\ncd docs\nls\ntac notes.txt\nexit\n",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Ошибка: неизвестная команда", result.stdout)
        self.assertIn("/docs$", result.stdout)
        self.assertIn("three\ntwo\none\n", result.stdout)
        self.assertEqual(result.stderr, "")

    def test_bad_options_and_files(self):
        """Ошибки запуска возвращают ненулевой код, без traceback."""
        invalid = self.root / "bad.zip"
        invalid.write_text("not zip", encoding="utf-8")
        cases = [["--vfs"], ["--script"], ["--unknown"],
                 ["--vfs", str(invalid)], ["--vfs", "/missing/archive"],
                 ["--script", "/missing/script"]]
        for arguments in cases:
            with self.subTest(arguments=arguments):
                result = self.launch(arguments)
                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn("Traceback", result.stderr)

    def test_script_then_interactive(self):
        """После скрипта без exit доступен ручной ввод."""
        script = self.root / "start.txt"
        script.write_text("unknown\ntouch new.txt\n", encoding="utf-8")
        result = self.launch(["--script", str(script)], "ls\nexit\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("$ touch new.txt", result.stdout)
        self.assertIn("$ new.txt\n", result.stdout)
        self.assertLess(result.stdout.index("unknown"),
                        result.stdout.index("touch new.txt"))

    def test_script_exit_skips_later_lines(self):
        """Exit завершает скрипт и не открывает интерактивный сеанс."""
        script = self.root / "start.txt"
        script.write_text("exit wrong\nexit\nNEVER\n", encoding="utf-8")
        result = self.launch(["--script", str(script)], "ALSO_NEVER\n")
        self.assertEqual(result.returncode, 0)
        self.assertIn("Ошибка: exit", result.stdout)
        self.assertNotIn("NEVER", result.stdout)

    def test_non_utf8_script(self):
        """Некорректная кодировка скрипта диагностируется при запуске."""
        script = self.root / "bad.txt"
        script.write_bytes(b"\xff\xfe")
        result = self.launch(["--script", str(script)])
        self.assertEqual(result.returncode, 1)
        self.assertIn("Ошибка:", result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_launch_wrapper_from_another_directory(self):
        """Run.sh находит проект и передаёт оба аргумента программе."""
        result = subprocess.run(
            ["sh", str(ROOT / "run.sh"), "--vfs",
             str(self.root / "minimal.zip"), "--script",
             str(ROOT / "examples/stage2.txt")],
            cwd=self.root, capture_output=True, text=True, timeout=5,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("hello.txt", result.stdout)

    def test_all_stage_scenarios(self):
        """Сценарии завершаются, исходный архив остаётся неизменным."""
        archive = self.root / "deep.zip"
        before = archive.read_bytes()
        for stage in (2, 3, 4, 5):
            with self.subTest(stage=stage):
                result = self.launch([
                    "--vfs", str(archive), "--script",
                    str(ROOT / f"examples/stage{stage}.txt"),
                ])
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("Ошибка:", result.stdout)
                self.assertEqual(archive.read_bytes(), before)
