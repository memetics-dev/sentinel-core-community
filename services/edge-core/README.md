# Sentinel Core Edge Core

The Edge Core is the local intelligence hub for Sentinel Core.

Responsibilities include:

- sensor event ingestion
- occupancy state management
- identity confidence evaluation
- contextual threat scoring
- escalation orchestration

The Edge Core is designed to continue operating even if internet connectivity is unavailable.
Trial-ready local persistence is stored in `data/sentinel_core.db` using SQLite.
Trial household configuration is loaded from `config/household.json`.

Initial MVP focus:

- local event ingestion
- occupancy simulation
- threat scoring
- explainable escalation

## Run Edge Core

Install the local requirements, then start the API:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Useful endpoints during local validation:

- `GET /config`
- `GET /health`
- `GET /occupants`
- `GET /devices`
- `GET /trial/readiness`
- `GET /trial/metrics`
- `GET /trial/evaluation`
- `POST /trial/feedback`
- `GET /trial/export`
- `GET /trial/report`
- `GET /behaviour/baseline`
- `GET /behaviour/anomalies`
- `GET /correlation/recent`
- `GET /presence`
- `GET /presence/occupants`
- `GET /response/active`
- `GET /response/history`
- `GET /narratives/current`
- `GET /narratives/history`
- `GET /zones`
- `GET /occupancy`
- `GET /identity`
- `GET /threats`
- `GET /escalations`
- `GET /ops/snapshot`
- `GET /ops/feed`
- `GET /history/events`
- `GET /history/identity`
- `GET /history/threats`
- `GET /history/escalations`
- `GET /history/incidents`
- `GET /incidents`
- `GET /incidents/open`
- `GET /incidents/{incident_id}/timeline`
- `GET /incidents/{incident_id}/replay`
- `POST /incidents/{incident_id}/monitor`
- `POST /incidents/{incident_id}/resolve`
- `POST /incidents/{incident_id}/dismiss`
- `POST /incidents/{incident_id}/notes`
- `GET /incidents/{incident_id}/notes`

Local ops console development uses explicit CORS allow-listing for:

- `http://localhost:3000` through `http://localhost:3004`
- `http://127.0.0.1:3000` through `http://127.0.0.1:3004`

This is local-dev only and does not use `allow_origins=["*"]`.

Timeline and replay examples:

```bash
curl http://127.0.0.1:8000/incidents
curl http://127.0.0.1:8000/incidents/<incident_id>/timeline
curl http://127.0.0.1:8000/incidents/<incident_id>/replay
```

Operations feed examples:

```bash
curl http://127.0.0.1:8000/ops/snapshot
curl -N http://127.0.0.1:8000/ops/feed
```

Trial readiness examples:

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/trial/readiness
```

Trial evaluation examples:

```bash
curl http://127.0.0.1:8000/trial/metrics
curl http://127.0.0.1:8000/trial/evaluation
curl -X POST http://127.0.0.1:8000/trial/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "incident_id": "incident_example",
    "feedback_type": "false_positive",
    "note": "Resident confirmed expected movement."
  }'
curl http://127.0.0.1:8000/trial/export
curl http://127.0.0.1:8000/trial/report
```

Behaviour examples:

```bash
curl http://127.0.0.1:8000/behaviour/baseline
curl http://127.0.0.1:8000/behaviour/anomalies
```

Correlation example:

```bash
curl http://127.0.0.1:8000/correlation/recent
```

Presence examples:

```bash
curl http://127.0.0.1:8000/presence
curl http://127.0.0.1:8000/presence/occupants
curl http://127.0.0.1:8000/ops/snapshot
```

Response orchestration examples:

```bash
curl http://127.0.0.1:8000/response/active
curl http://127.0.0.1:8000/response/history
```

Operational narrative examples:

```bash
curl http://127.0.0.1:8000/narratives/current
curl http://127.0.0.1:8000/narratives/history
```

## Run Scenario Scripts

With the API running on `127.0.0.1:8000`, use the repeatable local scenarios in `scripts/`:

```bash
bash scripts/night_lock_garage_intrusion.sh
bash scripts/night_lock_kitchen_movement.sh
bash scripts/night_lock_trusted_presence.sh
```

These scripts preserve the current curl-based workflow and exercise:

- unknown garage movement during `night_lock`
- unknown kitchen movement during `night_lock`
- trusted BLE resident presence suppressing follow-on movement risk

## Demo Flow

For controlled MVP demos, run from repo root so the paths below work as-is.

Start Edge Core:

```bash
python -m uvicorn app.main:app --reload --app-dir services/edge-core
```

Start the ops console in another terminal:

```bash
cd apps/ops-console
npm install
npm run dev
```

Reset demo state before each walkthrough:

```bash
bash services/edge-core/scripts/reset_demo_state.sh
```

This reset is safe by design:

- it only removes the local SQLite demo database at `services/edge-core/data/sentinel_core.db`
- it does not touch source files
- it does not touch `services/edge-core/config/household.json`

After reset, restart Edge Core so in-memory runtime state is also cleared. On startup, Edge Core recreates the SQLite database automatically.

Run the end-to-end intrusion demo:

```bash
bash services/edge-core/scripts/demo_intrusion_flow.sh
```

This flow sets `Night Lock`, triggers unknown perimeter driveway movement, then garage movement, then follow-on kitchen movement so the operator console can show incidents, response guidance, and perimeter-to-indoor correlations.

Run the trusted presence demo:

```bash
bash services/edge-core/scripts/demo_trusted_presence_flow.sh
```

This flow sets `Night Lock`, registers a configured trusted BLE resident device, then triggers follow-on kitchen movement so the operator can observe suppression and more benign response guidance.

Useful demo endpoints while the ops console is open:

- `http://127.0.0.1:8000/ops/snapshot`
- `http://127.0.0.1:8000/incidents`
- `http://127.0.0.1:8000/response/active`
- `http://127.0.0.1:8000/correlation/recent`

Trial evaluation workflow:

1. Run a controlled demo or household trial flow.
2. Review incidents, responses, and narratives in the ops console.
3. Record operator feedback with `POST /trial/feedback` for correct detections, false positives, uncertain outcomes, or narrative quality.
4. Inspect `GET /trial/metrics` and `GET /trial/evaluation` for current operational quality signals.
5. Export a local JSON bundle from `GET /trial/export` for offline trial review.
6. Generate a deterministic local summary from `GET /trial/report` for operator-facing trial reporting.
