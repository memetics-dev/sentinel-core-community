#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
STATE_DIR="$REPO_ROOT/.sentinel-core"
VENV_DIR="$STATE_DIR/venv"
EDGE_CORE_DIR="$REPO_ROOT/services/edge-core"
OPS_CONSOLE_DIR="$REPO_ROOT/apps/ops-console"

say() {
  printf '[install] %s
' "$1"
}

fail() {
  printf '[install] %s
' "$1" >&2
  exit 1
}

require_command() {
  command -v "$1" >/dev/null 2>&1 || fail "required command not found: $1"
}

say "repo root: $REPO_ROOT"
mkdir -p "$STATE_DIR"

say "verifying prerequisites"
require_command python3
require_command npm

if [ ! -f "$EDGE_CORE_DIR/requirements.txt" ]; then
  fail "missing Edge Core requirements file at $EDGE_CORE_DIR/requirements.txt"
fi
if [ ! -f "$OPS_CONSOLE_DIR/package.json" ]; then
  fail "missing ops console package.json at $OPS_CONSOLE_DIR/package.json"
fi

say "creating local Python virtual environment at $VENV_DIR"
python3 -m venv "$VENV_DIR"

say "installing Edge Core Python dependencies into the local virtual environment"
"$VENV_DIR/bin/python" -m pip install --upgrade pip
"$VENV_DIR/bin/python" -m pip install -r "$EDGE_CORE_DIR/requirements.txt"

say "installing ops console npm dependencies locally"
(
  cd "$OPS_CONSOLE_DIR"
  npm install
)

say "installation steps complete"
say "next step: bash install/start-services.sh"
