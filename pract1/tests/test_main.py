import unittest

from src.main import parse_command


class TestParseCommand(unittest.TestCase):
    """Проверки разделения команды и аргументов."""

    def test_command_with_arguments(self):
        """Сохранить имя команды и порядок двух аргументов."""
        command, arguments = parse_command("ls documents photos")

        self.assertEqual(command, "ls")
        self.assertEqual(arguments, ["documents", "photos"])

    def test_command_without_arguments(self):
        """Вернуть пустой список для команды без аргументов."""
        command, arguments = parse_command("ls")

        self.assertEqual(command, "ls")
        self.assertEqual(arguments, [])
