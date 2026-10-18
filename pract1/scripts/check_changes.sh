#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
python3 scripts/create_vfs.py
sh run.sh --vfs examples/deep.zip --script examples/stage5.txt
