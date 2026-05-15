# Sentinel Core Community Preview Export

Sentinel Core Community Preview is an experimental local-first residential intelligence preview intended for controlled technical evaluation and household behavioural testing. It is not a production-certified alarm replacement.
This folder is a cleaned public-facing Community Preview package intended for a future separate GitHub repository.

It contains:
- Community Preview documentation
- public-facing product/demo frontend routes
- installer MVP scripts
- a limited safe local Edge Core preview for scenario scripts and local experimentation

It does not contain:
- local databases
- `.sentinel-core/` runtime state
- `node_modules/`
- `.next/`
- private household notes
- personal founder pilot notes
- commercial/private strategy docs
- secrets or environment files

## Recommended First Run
From this folder:

```bash
bash install/check-system.sh
bash install/install-sentinel-core.sh
bash install/start-services.sh
```

Then open:
- public preview routes: `http://127.0.0.1:3000/public`
- ops console: `http://127.0.0.1:3000`
- Edge Core preview: `http://127.0.0.1:8000`

## Safe Testing Path
- start with simulated public scenarios
- use passive observation before operational trust
- do not rely on Sentinel Core as primary household security
