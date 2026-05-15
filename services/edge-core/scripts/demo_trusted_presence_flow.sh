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

echo "Running Sentinel Core trusted presence demo against ${EDGE_CORE_URL}"
echo ""
echo "Setting Night Lock mode..."
post_json "/mode" '{
  "mode": "night_lock",
  "description": "High-sensitivity nighttime protection mode"
}'

echo ""
echo "Registering trusted BLE presence for a configured resident..."
post_json "/events" '{
  "sensor_id": "ble_kitchen_resident_01",
  "sensor_type": "ble",
  "zone_id": "kitchen",
  "value": "resident_device_detected",
  "confidence": 90
}'

sleep 1

echo ""
echo "Triggering follow-on movement in kitchen..."
post_json "/events" '{
  "sensor_id": "mmwave_kitchen_demo_resident_01",
  "sensor_type": "mmwave",
  "zone_id": "kitchen",
  "value": "motion_detected",
  "confidence": 88
}'

echo ""
echo "Presence summary..."
get_json "/presence"

echo ""
echo "Active response assessments..."
get_json "/response/active"

echo ""
echo "Current threat state..."
get_json "/threats"

echo ""
echo "Useful operator endpoints:"
echo "- ${EDGE_CORE_URL}/ops/snapshot"
echo "- ${EDGE_CORE_URL}/presence"
echo "- ${EDGE_CORE_URL}/response/active"
echo "- ${EDGE_CORE_URL}/incidents/open"
