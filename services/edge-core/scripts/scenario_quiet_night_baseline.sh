#!/bin/bash

set -euo pipefail

EDGE_CORE_URL="${EDGE_CORE_URL:-http://127.0.0.1:8000}"

post_json() {
  local path="$1"
  local payload="$2"
  curl -fsS -X POST "${EDGE_CORE_URL}${path}" \
    -H "Content-Type: application/json" \
    -d "${payload}"
}

get_json() {
  local path="$1"
  curl -fsS "${EDGE_CORE_URL}${path}"
}

echo "Scenario: Quiet Night Baseline"
echo "Purpose: confirm Sentinel Core remains calm during a clean Night Lock baseline."
echo "Expected interpretation: low operational activity, no open incidents, no active response posture."
echo ""
echo "Setting Night Lock mode..."
post_json "/mode" '{
  "mode": "night_lock",
  "description": "High-sensitivity nighttime protection mode"
}'

echo ""
echo "Checking current open incidents..."
get_json "/incidents/open"

echo ""
echo "Checking current active responses..."
get_json "/response/active"

echo ""
echo "Useful operator endpoints:"
echo "- ${EDGE_CORE_URL}/ops/snapshot"
echo "- ${EDGE_CORE_URL}/incidents/open"
echo "- ${EDGE_CORE_URL}/response/active"
echo "- ${EDGE_CORE_URL}/trial/report"
