"""Консольный эмулятор, вариант 10: ввод и конфигурация."""

import argparse
import getpass
from pathlib import Path
import socket
import zipfile

if __package__:
    from .vfs import VirtualFileSystem
else:
    from vfs import VirtualFileSystem


def parse_command(user_input):
    """Разделить строку на команду и аргументы по пробелам."""
    parts = user_input.split()
    if not parts:
        return "", []
    return parts[0], parts[1:]


def parse_options(argv=None):
    """Прочитать пути к ZIP-VFS и стартовому скрипту."""
    parser = argparse.ArgumentParser(description="Эмулятор оболочки, №10")
    parser.add_argument("--vfs", help="Путь к ZIP с виртуальными файлами")
    parser.add_argument("--script", help="Путь к стартовому скрипту UTF-8")
    return parser.parse_args(argv)


class Shell:
    """Хранить состояние сеанса и выполнять команды."""

    def __init__(self, archive=None):
        """Получить реальные данные пользователя и компьютера."""
        self.username = getpass.getuser()
        self.hostname = socket.gethostname()
        self.cwd = "/"
        self.vfs = VirtualFileSystem(archive)

    def prompt(self):
        """Сформировать приглашение с текущим виртуальным каталогом."""
        return f"{self.username}@{self.hostname}:{self.cwd}$ "

    def execute(self, line):
        """Выполнить строку; вернуть False только при правильном exit."""
        command, arguments = parse_command(line)
        if not command:
            return True
        if command == "exit":
            if arguments:
                print("Ошибка: exit не принимает аргументы")
                return True
            return False
        if command in ("ls", "cd"):
            print(f"Команда: {command}")
            print("Аргументы:", arguments)
        else:
            print(f"Ошибка: неизвестная команда '{command}'")
        return True


def run_script(shell, path):
    """Показать и выполнить строки скрипта, сохраняя порядок команд."""
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    for line in lines:
        print(shell.prompt() + line)
        if not shell.execute(line):
            return False
    return True


def interactive(shell):
    """Повторять ввод до exit или завершения потока ввода."""
    while True:
        try:
            line = input(shell.prompt())
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if not shell.execute(line):
            return


def main(argv=None):
    """Вывести конфигурацию, выполнить скрипт и начать диалог."""
    options = parse_options(argv)
    print(f"VFS: {options.vfs or '(не задана)'}")
    print(f"Стартовый скрипт: {options.script or '(не задан)'}")
    try:
        shell = Shell(options.vfs)
        if options.script and not run_script(shell, options.script):
            return 0
    except (OSError, UnicodeError, ValueError, zipfile.BadZipFile) as error:
        print(f"Ошибка: {error}")
        return 1
    interactive(shell)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
