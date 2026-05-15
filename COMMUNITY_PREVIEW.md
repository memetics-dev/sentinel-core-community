# Sentinel Core Community Preview

Sentinel Core Community Preview is a carefully scoped public preview of a local-first residential intelligence system.

It is intended for:
- developers
- edge-AI builders
- smart-home enthusiasts
- early technical evaluators

It is not:
- a production alarm replacement
- guaranteed prevention
- managed monitoring
- a cloud account platform

## What Is Included
- Edge Core local runtime
- ops console
- public product and demo pages
- installer MVP scripts
- scenario scripts
- trial review tools
- documentation

## What Is Not Included
- production mobile app
- universal hardware support
- cloud account system
- managed monitoring
- certified alarm-company replacement
- production installer or image flashing workflow

## Recommended First Run
From repo root:

```bash
bash install/check-system.sh
bash install/install-sentinel-core.sh
bash install/start-services.sh
```

Then open:
- public product pages under `http://127.0.0.1:3000/public`
- ops console at `http://127.0.0.1:3000`
- Edge Core at `http://127.0.0.1:8000`

Try the scenario scripts after the services are running.

## Safe Testing Path
- run simulated public scenarios first
- use passive observation before operational trust
- do not rely on Sentinel Core as primary security

## Hardware Guidance
- Jetson Orin Nano is the recommended future node target
- the current repo can be explored on a normal development machine
- hardware support remains curated, not universal

## Contribution Focus
Useful contributions include:
- docs clarity
- installer ergonomics
- hardware notes
- scenario feedback
- UI polish

Please avoid broad unsupported integrations, cloud surveillance features, or alarm-company claims.
