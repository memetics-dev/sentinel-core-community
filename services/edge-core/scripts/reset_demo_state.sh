#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
DB_PATH="${SERVICE_DIR}/data/sentinel_core.db"
EDGE_CORE_URL="${EDGE_CORE_URL:-http://127.0.0.1:8000}"

echo "Sentinel Core demo reset"
echo "Service directory: ${SERVICE_DIR}"
echo "Database path: ${DB_PATH}"
echo ""

if [[ -f "${DB_PATH}" ]]; then
  rm -f "${DB_PATH}"
  echo "Removed local SQLite demo database."
else
  echo "No local SQLite demo database was present."
fi

echo ""
if curl -fsS "${EDGE_CORE_URL}/health" >/dev/null 2>&1; then
  echo "Edge Core is currently reachable at ${EDGE_CORE_URL}."
  echo "Restart Edge Core now to clear in-memory runtime state before a demo."
  echo "After restart, /health will recreate the SQLite database automatically."
else
  echo "Edge Core does not appear to be running at ${EDGE_CORE_URL}."
  echo "Start Edge Core after this reset to recreate the SQLite database cleanly."
fi

echo ""
echo "Safe reset complete."
echo "What changed:"
echo "- local demo SQLite state was removed if present"
echo "- source files were not touched"
echo "- config/household.json was not touched"
