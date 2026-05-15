#!/bin/bash

set -euo pipefail

echo "Setting Night Lock mode..."

curl -sS -X POST http://127.0.0.1:8000/mode \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "night_lock",
    "description": "High-sensitivity nighttime protection mode"
  }'

echo ""
echo "Triggering unknown garage movement..."

curl -sS -X POST http://127.0.0.1:8000/events \
  -H "Content-Type: application/json" \
  -d '{
    "sensor_id": "mmwave_garage_01",
    "sensor_type": "mmwave",
    "zone_id": "garage",
    "value": "motion_detected",
    "confidence": 91
  }'

echo ""
echo "Current threat state..."

curl -sS http://127.0.0.1:8000/threats

echo ""
echo "Current escalation state..."

curl -sS http://127.0.0.1:8000/escalations
