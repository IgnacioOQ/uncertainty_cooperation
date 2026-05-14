#!/usr/bin/env bash
# Bootstrap a reproducible environment for the uncertainty_cooperation repo.
#
# Usage:
#   ./setup.sh                  # core deps only (tabular notebooks)
#   ./setup.sh --with-torch     # core + torch (all notebooks, including 04_deep_ensembles/)
#
# Honours these env vars:
#   PYTHON    - which Python to use (default: python3)
#   VENV_DIR  - venv location       (default: .venv)
set -euo pipefail

PYTHON="${PYTHON:-python3}"
VENV_DIR="${VENV_DIR:-.venv}"
KERNEL_NAME="uncertainty-cooperation"
KERNEL_DISPLAY="Python (uncertainty_cooperation)"

WITH_TORCH=0
for arg in "$@"; do
  case "$arg" in
    --with-torch) WITH_TORCH=1 ;;
    -h|--help)
      sed -n '2,12p' "$0"
      exit 0
      ;;
    *)
      echo "Unknown argument: $arg" >&2
      exit 2
      ;;
  esac
done

if [ ! -d "$VENV_DIR" ]; then
  echo ">> Creating venv at $VENV_DIR using $PYTHON"
  "$PYTHON" -m venv "$VENV_DIR"
else
  echo ">> Reusing existing venv at $VENV_DIR"
fi

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

echo ">> Upgrading pip"
python -m pip install --upgrade pip

if [ "$WITH_TORCH" -eq 1 ]; then
  echo ">> Installing core + torch (requirements-deep.txt)"
  pip install -r requirements-deep.txt
else
  echo ">> Installing core requirements (requirements.txt)"
  pip install -r requirements.txt
fi

echo ">> Registering Jupyter kernel '$KERNEL_NAME'"
python -m ipykernel install --user --name "$KERNEL_NAME" --display-name "$KERNEL_DISPLAY"

cat <<EOF

Setup complete.

Activate the environment:
  source $VENV_DIR/bin/activate

Launch Jupyter:
  jupyter lab

Select the kernel "$KERNEL_DISPLAY" inside each notebook.

EOF

if [ "$WITH_TORCH" -eq 0 ]; then
  cat <<'EOF'
The 04_deep_ensembles/ notebooks (and the deep-ensemble version of the
Polluted River) need torch. Re-run with:
  ./setup.sh --with-torch

EOF
fi
