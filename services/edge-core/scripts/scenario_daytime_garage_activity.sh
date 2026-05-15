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

echo "Scenario: Daytime Garage Activity"
echo "Purpose: compare daytime garage motion with higher-sensitivity nighttime garage behaviour."
echo "Expected interpretation: lower concern than Night Lock garage activity, with calmer response and narrative wording."
echo ""
echo "Setting Home Active mode..."
post_json "/mode" '{
  "mode": "home_active",
  "description": "Normal daytime occupied mode"
}'

sleep 1

echo ""
echo "Triggering daytime garage motion..."
post_json "/events" '{
  "sensor_id": "mmwave_garage_daytime_01",
  "sensor_type": "mmwave",
  "zone_id": "garage",
  "value": "motion_detected",
  "confidence": 81
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
echo "- ${EDGE_CORE_URL}/threats"
echo "- ${EDGE_CORE_URL}/response/active"
echo "- ${EDGE_CORE_URL}/narratives/current"
