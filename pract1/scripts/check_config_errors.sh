#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
if sh run.sh --vfs; then exit 1; fi
if sh run.sh --script; then exit 1; fi
if sh run.sh --unknown; then exit 1; fi
if sh run.sh --vfs examples/minimal.zip --script /missing/script; then
    exit 1
fi
