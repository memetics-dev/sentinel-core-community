#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
STATE_DIR="$REPO_ROOT/.sentinel-core"
PID_DIR="$STATE_DIR/pids"
EDGE_PID_FILE="$PID_DIR/edge-core.pid"
OPS_PID_FILE="$PID_DIR/ops-console.pid"

say() {
  printf '[stop-services] %s
' "$1"
}

process_running() {
  local pid="$1"
  [ -n "$pid" ] && kill -0 "$pid" >/dev/null 2>&1
}

matches_expected_process() {
  local pid="$1"
  local expected="$2"
  local command_line
  command_line="$(ps -p "$pid" -o command= 2>/dev/null || true)"
  printf '%s' "$command_line" | grep -F "$expected" >/dev/null 2>&1
}

stop_from_pid_file() {
  local pid_file="$1"
  local label="$2"
  local expected="$3"

  if [ ! -f "$pid_file" ]; then
    say "no pid file found for $label"
    return
  fi

  local pid
  pid="$(cat "$pid_file")"

  if ! process_running "$pid"; then
    say "$label is not running; removing stale pid file"
    rm -f "$pid_file"
    return
  fi

  if ! matches_expected_process "$pid" "$expected"; then
    say "$label pid $pid does not match expected Sentinel Core process; leaving it untouched"
    return
  fi

  say "stopping $label (pid $pid)"
  kill "$pid"

  for _ in 1 2 3 4 5; do
    if ! process_running "$pid"; then
      break
    fi
    sleep 1
  done

  if process_running "$pid"; then
    say "$label is still running after a graceful stop request; leaving it for manual inspection"
    return
  fi

  rm -f "$pid_file"
  say "$label stopped"
}

stop_from_pid_file "$EDGE_PID_FILE" "Edge Core" "uvicorn app.main:app"
stop_from_pid_file "$OPS_PID_FILE" "ops console" "next dev"
