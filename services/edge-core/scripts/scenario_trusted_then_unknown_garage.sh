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

echo "Scenario: Trusted Presence Then Unknown Garage"
echo "Purpose: test whether prior trusted continuity is overridden cleanly when later garage activity looks hostile."
echo "Expected interpretation: trusted continuity is recorded, but later unknown garage movement should still raise concern."
echo ""
echo "Setting Night Lock mode..."
post_json "/mode" '{
  "mode": "night_lock",
  "description": "High-sensitivity nighttime protection mode"
}'

sleep 1

echo ""
echo "Registering trusted BLE presence in kitchen..."
post_json "/events" '{
  "sensor_id": "ble_kitchen_resident_01",
  "sensor_type": "ble",
  "zone_id": "kitchen",
  "value": "resident_device_detected",
  "confidence": 89
}'

sleep 1

echo ""
echo "Triggering unknown garage motion..."
post_json "/events" '{
  "sensor_id": "mmwave_garage_unknown_after_trusted_01",
  "sensor_type": "mmwave",
  "zone_id": "garage",
  "value": "motion_detected",
  "confidence": 92
}'

echo ""
echo "Current narratives..."
get_json "/narratives/current"

echo ""
echo "Active responses..."
get_json "/response/active"

echo ""
echo "Useful operator endpoints:"
echo "- ${EDGE_CORE_URL}/ops/snapshot"
echo "- ${EDGE_CORE_URL}/presence"
echo "- ${EDGE_CORE_URL}/incidents"
echo "- ${EDGE_CORE_URL}/response/active"
