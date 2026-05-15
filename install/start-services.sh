#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
STATE_DIR="$REPO_ROOT/.sentinel-core"
VENV_DIR="$STATE_DIR/venv"
EDGE_CORE_DIR="$REPO_ROOT/services/edge-core"
OPS_CONSOLE_DIR="$REPO_ROOT/apps/ops-console"
PID_DIR="$STATE_DIR/pids"
LOG_DIR="$STATE_DIR/logs"
EDGE_PID_FILE="$PID_DIR/edge-core.pid"
OPS_PID_FILE="$PID_DIR/ops-console.pid"
EDGE_LOG="$LOG_DIR/edge-core.log"
OPS_LOG="$LOG_DIR/ops-console.log"

say() {
  printf '[start-services] %s
' "$1"
}

fail() {
  printf '[start-services] %s
' "$1" >&2
  exit 1
}

have_command() {
  command -v "$1" >/dev/null 2>&1
}

process_running() {
  local pid="$1"
  [ -n "$pid" ] && kill -0 "$pid" >/dev/null 2>&1
}

port_in_use() {
  local port="$1"
  if have_command lsof; then
    lsof -nP -iTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1
    return
  fi
  if have_command ss; then
    ss -ltn | awk '{print $4}' | grep -E "[:.]${port}$" >/dev/null 2>&1
    return
  fi
  return 1
}

mkdir -p "$PID_DIR" "$LOG_DIR"

[ -x "$VENV_DIR/bin/python" ] || fail "local virtual environment not found. Run bash install/install-sentinel-core.sh first."
[ -d "$OPS_CONSOLE_DIR/node_modules" ] || fail "ops console node_modules not found. Run bash install/install-sentinel-core.sh first."

if [ -f "$EDGE_PID_FILE" ] && process_running "$(cat "$EDGE_PID_FILE")"; then
  fail "Edge Core already appears to be running under PID $(cat "$EDGE_PID_FILE")"
fi
if [ -f "$OPS_PID_FILE" ] && process_running "$(cat "$OPS_PID_FILE")"; then
  fail "ops console already appears to be running under PID $(cat "$OPS_PID_FILE")"
fi

if port_in_use 8000; then
  fail "port 8000 is already in use"
fi
if port_in_use 3000; then
  fail "port 3000 is already in use"
fi

say "starting Edge Core on http://127.0.0.1:8000"
(
  cd "$REPO_ROOT"
  nohup "$VENV_DIR/bin/python" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --app-dir services/edge-core >"$EDGE_LOG" 2>&1 &
  echo $! >"$EDGE_PID_FILE"
)

sleep 2
if ! process_running "$(cat "$EDGE_PID_FILE")"; then
  fail "Edge Core failed to start. Check $EDGE_LOG"
fi

say "starting ops console on http://127.0.0.1:3000"
(
  cd "$OPS_CONSOLE_DIR"
  nohup npm run dev -- --hostname 127.0.0.1 --port 3000 >"$OPS_LOG" 2>&1 &
  echo $! >"$OPS_PID_FILE"
)

sleep 3
if ! process_running "$(cat "$OPS_PID_FILE")"; then
  fail "ops console failed to start. Check $OPS_LOG"
fi

say "Sentinel Core services started"
say "Edge Core: http://127.0.0.1:8000"
say "Ops Console: http://127.0.0.1:3000"
say "logs: $LOG_DIR"
say "to stop both services: bash install/stop-services.sh"
