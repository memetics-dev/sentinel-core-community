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

echo "Scenario: Ambiguous Hallway Movement"
echo "Purpose: test how Sentinel Core handles transitional indoor movement without strong hostile progression."
echo "Expected interpretation: suspicious or monitor-worthy movement, but calmer than driveway-to-garage intrusion."
echo ""
echo "Setting Night Lock mode..."
post_json "/mode" '{
  "mode": "night_lock",
  "description": "High-sensitivity nighttime protection mode"
}'

sleep 1

echo ""
echo "Triggering hallway motion..."
post_json "/events" '{
  "sensor_id": "mmwave_hallway_ambiguous_01",
  "sensor_type": "mmwave",
  "zone_id": "hallway",
  "value": "motion_detected",
  "confidence": 74
}'

echo ""
echo "Current threats..."
get_json "/threats"

echo ""
echo "Active responses..."
get_json "/response/active"

echo ""
echo "Useful operator endpoints:"
echo "- ${EDGE_CORE_URL}/ops/snapshot"
echo "- ${EDGE_CORE_URL}/incidents"
echo "- ${EDGE_CORE_URL}/response/active"
echo "- ${EDGE_CORE_URL}/narratives/current"
