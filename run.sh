#!/usr/bin/env bash
# Python 3.11+ — Voicinator inbox-queue web app entry point.
# Creates/activates venv, installs deps (including NeMo MSDD for pipeline step 4), starts app. Control-C stops.
# NeMo MSDD setup (models, PyTorch/CUDA): see original-research/NeMo MSDD implementation guide.md

set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

VENV_DIR="${VENV_DIR:-.venv}"
if [[ ! -d "$VENV_DIR" ]]; then
  # Use Python 3.13 (or 3.12) for venv; NeMo MSDD (step 4) supports 3.10–3.13
  for py in python3.13 python3.12 python3.11 python3.10 python3; do
    if command -v "$py" >/dev/null 2>&1; then
      PY_USED=$py
      break
    fi
  done
  "${PY_USED:-python3}" -m venv "$VENV_DIR"
fi
# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"

pip install -q -r requirements.txt

# NeMo MSDD (step 4 diarization) supports only Python 3.10–3.13; install when supported
PY_VER=$(python -c "import sys; v=sys.version_info; print(f'{v.major}.{v.minor}')")
case "$PY_VER" in
  3.10|3.11|3.12|3.13)
    pip install -q -r requirements-nemo.txt
    ;;
  *)
    echo "Note: NeMo MSDD (pipeline step 4) not installed — requires Python 3.10–3.13 (current: $PY_VER). Step 4 will log an error when used."
    ;;
esac

# Start web app (Flask); Control-C stops
exec python -m backend
