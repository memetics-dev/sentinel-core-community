#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
STATE_DIR="$REPO_ROOT/.sentinel-core"
mkdir -p "$STATE_DIR"

say() {
  printf '[check-system] %s
' "$1"
}

have_command() {
  command -v "$1" >/dev/null 2>&1
}

check_port() {
  local port="$1"

  if have_command lsof; then
    if lsof -nP -iTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1; then
      say "port $port is already in use"
      return
    fi
  elif have_command ss; then
    if ss -ltn | awk '{print $4}' | grep -E "[:.]${port}$" >/dev/null 2>&1; then
      say "port $port is already in use"
      return
    fi
  elif have_command netstat; then
    if netstat -an 2>/dev/null | grep -E "LISTEN|LISTENING" | grep -E "[\.:]${port}[[:space:]]" >/dev/null 2>&1; then
      say "port $port is already in use"
      return
    fi
  else
    say "could not inspect port $port because lsof, ss, and netstat are unavailable"
    return
  fi

  say "port $port appears available"
}

say "repo root: $REPO_ROOT"
say "checking operating system and platform"
uname -a || true
if [ -f /etc/os-release ]; then
  say "os-release summary"
  grep -E '^(NAME|VERSION|PRETTY_NAME)=' /etc/os-release || true
fi

say "checking Python availability"
if have_command python3; then
  python3 --version
else
  say "python3 was not found"
fi

say "checking Node and npm availability"
if have_command node; then
  node --version
else
  say "node was not found"
fi
if have_command npm; then
  npm --version
else
  say "npm was not found"
fi

say "checking available disk space for repo volume"
df -h "$REPO_ROOT" || true

say "checking local service ports"
check_port 8000
check_port 3000

say "system inspection complete"
