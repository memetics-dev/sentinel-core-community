# Community Installation

## Recommended First Run
From repo root:

```bash
bash install/check-system.sh
bash install/install-sentinel-core.sh
bash install/start-services.sh
```

## What To Open
After startup:
- public routes under `http://127.0.0.1:3000/public`
- ops console at `http://127.0.0.1:3000`
- Edge Core at `http://127.0.0.1:8000`

## Safe Testing Path
1. Review the public simulated product pages first.
2. Use passive observation before operational trust.
3. Run scenario scripts locally.
4. Review incidents, narratives, and response posture in the ops console.
5. Do not treat Sentinel Core as primary household security.

## Hardware Guidance
- Jetson Orin Nano is the recommended future node target.
- The current repo can be explored locally on a development machine.
- Hardware compatibility remains curated and should not be assumed beyond documented guidance.
