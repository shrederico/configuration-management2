"""Реализация команд оболочки над виртуальной файловой системой."""

import platform
import posixpath


MAX_SINGLE_ARGUMENT = 1


def require_single(arguments, command):
    """Отклонить лишние аргументы и неподдерживаемые флаги."""
    if len(arguments) > MAX_SINGLE_ARGUMENT:
        raise ValueError(f"{command}: ожидается не более одного пути")
    reject_options(arguments)


def reject_options(arguments):
    """Отклонить флаги, не входящие в реализованный режим команды."""
    for argument in arguments:
        if argument.startswith("-"):
            raise ValueError(f"Неподдерживаемый параметр: {argument}")


def ls(shell, arguments):
    """Показать каталог или имя файла; без аргументов — текущий каталог."""
    require_single(arguments, "ls")
    path = shell.vfs.normalize(arguments[0] if arguments else ".", shell.cwd)
    if path in shell.vfs.files:
        print(posixpath.basename(path))
        return
    names = shell.vfs.list_directory(path)
    for name in names:
        if not name.startswith("."):
            print(name)


def cd(shell, arguments):
    """Изменить текущий каталог; без аргументов перейти в корень VFS."""
    require_single(arguments, "cd")
    path = shell.vfs.normalize(arguments[0] if arguments else "/", shell.cwd)
    if path not in shell.vfs.directories:
        raise ValueError(f"Нет каталога: {path}")
    shell.cwd = path


def tac(shell, arguments):
    """Вывести строки текстовых файлов в обратном порядке."""
    reject_options(arguments)
    if not arguments:
        raise ValueError("tac: укажите хотя бы один файл")
    for argument in arguments:
        try:
            path = shell.vfs.normalize(argument, shell.cwd)
            text = shell.vfs.read_file(path).decode("utf-8")
            lines = text.splitlines(keepends=True)
            print("".join(reversed(lines)), end="")
        except (ValueError, UnicodeError) as error:
            print(f"Ошибка: {argument}: {error}")


def uname(shell, arguments):
    """Показать название ядра реальной ОС; флаги не поддерживаются."""
    if arguments:
        raise ValueError("uname: аргументы не поддерживаются")
    print(platform.system())


def change_files(shell, arguments, operation, name):
    """Изменять каждый указанный путь, сообщая об ошибках отдельно."""
    reject_options(arguments)
    if not arguments:
        raise ValueError(f"{name}: укажите хотя бы один путь")
    for argument in arguments:
        try:
            path = shell.vfs.normalize(argument, shell.cwd)
            operation(path)
        except ValueError as error:
            print(f"Ошибка: {argument}: {error}")


def touch(shell, arguments):
    """Создать файлы или обновить время без изменения их содержимого."""
    change_files(shell, arguments, shell.vfs.touch, "touch")


def rm(shell, arguments):
    """Удалить виртуальные файлы без рекурсивного удаления каталогов."""
    change_files(shell, arguments, shell.vfs.remove, "rm")


COMMANDS = {
    "ls": ls, "cd": cd, "tac": tac, "uname": uname,
    "touch": touch, "rm": rm,
}
