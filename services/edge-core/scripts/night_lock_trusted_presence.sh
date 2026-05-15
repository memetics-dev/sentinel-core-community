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
echo "Registering trusted BLE presence in the kitchen..."

curl -sS -X POST http://127.0.0.1:8000/events \
  -H "Content-Type: application/json" \
  -d '{
    "sensor_id": "ble_kitchen_resident_01",
    "sensor_type": "ble",
    "zone_id": "kitchen",
    "value": "resident_device_detected",
    "confidence": 88
  }'

echo ""
echo "Triggering kitchen movement after trusted BLE presence..."

curl -sS -X POST http://127.0.0.1:8000/events \
  -H "Content-Type: application/json" \
  -d '{
    "sensor_id": "mmwave_kitchen_01",
    "sensor_type": "mmwave",
    "zone_id": "kitchen",
    "value": "motion_detected",
    "confidence": 91
  }'

echo ""
echo "Current identity state..."

curl -sS http://127.0.0.1:8000/identity

echo ""
echo "Current threat state..."

curl -sS http://127.0.0.1:8000/threats
