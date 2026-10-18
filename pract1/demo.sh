#!/bin/sh
set -eu
cd "$(dirname "$0")"
python3 scripts/create_vfs.py
printf '\n=== Основные команды (этап 4) ===\n'
sh run.sh --vfs examples/deep.zip --script examples/stage4.txt
printf '\n=== Изменение VFS (этап 5) ===\n'
sh run.sh --vfs examples/deep.zip --script examples/stage5.txt
