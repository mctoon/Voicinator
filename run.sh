#!/usr/bin/env bash
# Python 3.11+ — Voicinator inbox-queue web app entry point.
# Creates/activates venv, installs deps, starts app. Control-C stops.

set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

VENV_DIR="${VENV_DIR:-.venv}"
if [[ ! -d "$VENV_DIR" ]]; then
  python3 -m venv "$VENV_DIR"
fi
# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"

pip install -q -r requirements.txt

# Start web app (Flask); Control-C stops
exec python -m backend
