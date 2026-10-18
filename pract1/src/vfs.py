"""ZIP-VFS: каталоги и содержимое файлов хранятся только в памяти."""

import base64
import posixpath
import zipfile
import time


class VirtualFileSystem:
    """Хранить пути каталогов и файлы в кодировке base64."""

    def __init__(self, archive=None):
        """Создать корень и при необходимости прочитать ZIP."""
        self.directories = {"/"}
        self.files = {}
        self.modified = {}
        if archive:
            self.load(archive)

    def normalize(self, path, cwd="/"):
        """Разрешить абсолютный или относительный путь внутри VFS."""
        if not path.startswith("/"):
            path = posixpath.join(cwd, path)
        return "/" + posixpath.normpath(path).lstrip("/")

    def add_parents(self, path):
        """Создать неявные родительские каталоги архивной записи."""
        parent = posixpath.dirname(path)
        while parent != "/":
            if parent in self.files:
                raise ValueError(f"Файл вместо каталога: {parent}")
            self.directories.add(parent)
            parent = posixpath.dirname(parent)

    def load(self, archive):
        """Прочитать записи ZIP без распаковки на физический диск."""
        with zipfile.ZipFile(archive) as source:
            for entry in source.infolist():
                self.load_entry(source, entry)

    def load_entry(self, source, entry):
        """Проверить путь и сохранить каталог либо base64 файла."""
        name = entry.filename
        if name.startswith("/") or ".." in name.split("/"):
            raise ValueError(f"Недопустимый путь в ZIP: {name}")
        if "\\" in name:
            raise ValueError(f"Недопустимый разделитель в ZIP: {name}")
        path = self.normalize(name)
        self.add_parents(path)
        if entry.is_dir():
            if path in self.files:
                raise ValueError(f"Файл вместо каталога: {path}")
            self.directories.add(path)
        else:
            if path in self.directories or path in self.files:
                raise ValueError(f"Конфликт записей ZIP: {path}")
            self.files[path] = base64.b64encode(source.read(entry)).decode()

    def list_directory(self, path):
        """Вернуть имена непосредственных детей каталога."""
        if path not in self.directories:
            raise ValueError(f"Нет каталога: {path}")
        entries = self.directories | set(self.files)
        return sorted(posixpath.basename(item) for item in entries
                      if item != path and posixpath.dirname(item) == path)

    def read_file(self, path):
        """Декодировать содержимое виртуального файла в байты."""
        if path not in self.files:
            raise ValueError(f"Нет файла: {path}")
        return base64.b64decode(self.files[path])

    def touch(self, path):
        """Создать пустой файл или обновить время существующей записи."""
        parent = posixpath.dirname(path)
        if parent not in self.directories:
            raise ValueError(f"Нет родительского каталога: {parent}")
        if path not in self.directories:
            self.files.setdefault(path, "")
        self.modified[path] = time.time()

    def remove(self, path):
        """Удалить файл только из памяти; каталоги удалять нельзя."""
        if path in self.directories:
            raise ValueError(f"rm: это каталог: {path}")
        if path not in self.files:
            raise ValueError(f"Нет файла: {path}")
        del self.files[path]
        self.modified.pop(path, None)
