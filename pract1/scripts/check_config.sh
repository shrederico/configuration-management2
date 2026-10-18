#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
python3 scripts/create_vfs.py
printf 'exit\n' | sh run.sh
printf 'exit\n' | sh run.sh --vfs examples/minimal.zip
sh run.sh --script examples/stage2.txt
sh run.sh --vfs examples/minimal.zip --script examples/stage2.txt
