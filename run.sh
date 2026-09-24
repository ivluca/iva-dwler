#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
python="$project_dir/.venv/bin/python"

if [[ ! -x "$python" ]]; then
    printf 'Python environment not found. Create it and install requirements first.\n' >&2
    printf '  python3 -m venv .venv\n  .venv/bin/python -m pip install -r requirements.txt\n' >&2
    exit 1
fi

exec "$python" "$project_dir/gallery_dl_gui.py" "$@"
