#!/bin/sh
# Free-threaded build (no GIL), where entity rendering actually runs in parallel.
# Set up with:  py -V:3.14t -m venv .venv314t && .venv314t/Scripts/python -m pip install pynput
cd "$(dirname "$0")"

PYTHON=".venv314t/Scripts/python.exe"
[ -x "$PYTHON" ] || PYTHON=".venv314t/bin/python"

"$PYTHON" main.py --threaded --render-workers 8 "$@"
