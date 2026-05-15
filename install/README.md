# Sentinel Core Installer MVP

## Purpose
This directory contains the first script-driven installer MVP for a self-hosted Sentinel Core node on compatible Ubuntu and Jetson-style hardware.

This is not a production installer. It is a transparent local setup path intended to make repeatable pilot installation possible without introducing hidden system changes.

## What The Scripts Do
- `check-system.sh`: inspect the local machine and report readiness signals
- `install-sentinel-core.sh`: create a local Python virtual environment for Edge Core and install local dependencies for both services
- `start-services.sh`: start Edge Core and the ops console and write scoped PID and log files under `.sentinel-core/`
- `stop-services.sh`: stop only the Sentinel Core processes started by the start script when possible

## Local State
The installer MVP keeps its local state under:
- `.sentinel-core/venv`
- `.sentinel-core/logs/`
- `.sentinel-core/pids/`

No source files or household config are modified by these scripts.

## Usage
From repo root:

```bash
bash install/check-system.sh
bash install/install-sentinel-core.sh
bash install/start-services.sh
```

To stop services:

```bash
bash install/stop-services.sh
```

## Notes
- These scripts avoid `sudo` and global package installation.
- Python dependencies are installed into a local virtual environment.
- Node dependencies are installed into `apps/ops-console/node_modules` using the local project manifest.
- If required prerequisites are missing, the scripts stop and explain what was found.
