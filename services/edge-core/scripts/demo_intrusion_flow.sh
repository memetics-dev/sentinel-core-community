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

echo "Running Sentinel Core intrusion demo against ${EDGE_CORE_URL}"
echo ""
echo "Setting Night Lock mode..."
post_json "/mode" '{
  "mode": "night_lock",
  "description": "High-sensitivity nighttime protection mode"
}'

echo ""
echo "Triggering unknown perimeter driveway movement..."
post_json "/events" '{
  "sensor_id": "mmwave_driveway_demo_01",
  "sensor_type": "mmwave",
  "zone_id": "driveway",
  "value": "motion_detected",
  "confidence": 86
}'

sleep 1

echo ""
echo "Triggering unknown garage ingress movement..."
post_json "/events" '{
  "sensor_id": "mmwave_garage_demo_01",
  "sensor_type": "mmwave",
  "zone_id": "garage",
  "value": "motion_detected",
  "confidence": 93
}'

sleep 1

echo ""
echo "Triggering hallway transition movement..."
post_json "/events" '{
  "sensor_id": "mmwave_hallway_demo_01",
  "sensor_type": "mmwave",
  "zone_id": "hallway",
  "value": "motion_detected",
  "confidence": 90
}'

sleep 1

echo ""
echo "Triggering follow-on indoor kitchen movement..."
post_json "/events" '{
  "sensor_id": "mmwave_kitchen_demo_01",
  "sensor_type": "mmwave",
  "zone_id": "kitchen",
  "value": "motion_detected",
  "confidence": 89
}'

echo ""
echo "Open incidents..."
get_json "/incidents/open"

echo ""
echo "Active response assessments..."
get_json "/response/active"

echo ""
echo "Recent correlated signals..."
get_json "/correlation/recent"

echo ""
echo "Useful operator endpoints:"
echo "- ${EDGE_CORE_URL}/ops/snapshot"
echo "- ${EDGE_CORE_URL}/incidents"
echo "- ${EDGE_CORE_URL}/response/active"
echo "- ${EDGE_CORE_URL}/correlation/recent"
