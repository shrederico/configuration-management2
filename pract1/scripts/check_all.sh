#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
python3 -m unittest discover -s tests -v
sh scripts/check_config.sh
sh scripts/check_config_errors.sh
sh scripts/check_vfs_minimal.sh
sh scripts/check_vfs_files.sh
sh scripts/check_vfs_deep.sh
sh scripts/check_commands.sh
sh scripts/check_changes.sh
