#!/usr/bin/env bash
set -euo pipefail

# Run this script from Git Bash on Windows.
project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
python="$project_dir/.venv/Scripts/python.exe"

if [[ ! -x "$python" ]]; then
    printf 'Windows Python environment not found. Create it and install requirements first.\n' >&2
    printf '  py -m venv .venv\n  .venv/Scripts/python.exe -m pip install -r requirements.txt\n' >&2
    exit 1
fi

exec "$python" "$project_dir/gallery_dl_gui.py" "$@"
