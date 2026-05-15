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

echo "Scenario: Repeated Low-Confidence Noise"
echo "Purpose: test whether repeated weak signals remain restrained and do not over-escalate aggressively."
echo "Expected interpretation: low-confidence anomaly cluster, likely monitoring or silent review rather than urgent response."
echo ""
echo "Setting Night Lock mode..."
post_json "/mode" '{
  "mode": "night_lock",
  "description": "High-sensitivity nighttime protection mode"
}'

sleep 1

echo ""
echo "Triggering low-confidence driveway noise..."
post_json "/events" '{
  "sensor_id": "mmwave_driveway_noise_01",
  "sensor_type": "mmwave",
  "zone_id": "driveway",
  "value": "motion_detected",
  "confidence": 38
}'

sleep 1

echo ""
echo "Triggering low-confidence driveway noise again..."
post_json "/events" '{
  "sensor_id": "mmwave_driveway_noise_02",
  "sensor_type": "mmwave",
  "zone_id": "driveway",
  "value": "motion_detected",
  "confidence": 41
}'

sleep 1

echo ""
echo "Triggering low-confidence hallway noise..."
post_json "/events" '{
  "sensor_id": "mmwave_hallway_noise_01",
  "sensor_type": "mmwave",
  "zone_id": "hallway",
  "value": "motion_detected",
  "confidence": 43
}'

echo ""
echo "Active responses..."
get_json "/response/active"

echo ""
echo "Recent correlations..."
get_json "/correlation/recent"

echo ""
echo "Useful operator endpoints:"
echo "- ${EDGE_CORE_URL}/ops/snapshot"
echo "- ${EDGE_CORE_URL}/response/active"
echo "- ${EDGE_CORE_URL}/correlation/recent"
echo "- ${EDGE_CORE_URL}/trial/review"
