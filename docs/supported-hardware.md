# Supported Hardware

## Hardware Philosophy

Sentinel Core is intended for compatible local edge hardware that can support deterministic residential intelligence processing without relying on cloud inference.

The hardware philosophy is:

- local processing first
- operational reliability over novelty
- realistic pilot supportability
- privacy-preserving deployment

## Recommended Pilot Device

### NVIDIA Jetson Orin Nano

Jetson Orin Nano is the current recommended pilot platform.

Why it fits the current pilot model:

- compact self-hosted edge form factor
- suitable local compute profile for on-device reasoning and future integration growth
- appropriate for premium pilot households that want customer-controlled deployment

## Minimum Pilot Requirements

The current minimum requirements should be treated conservatively:

- modern Linux-capable edge device
- stable local networking
- enough local storage for runtime artifacts and local evidence
- enough compute headroom for Sentinel Core services and future integration connectors
- operator access for installation, restart, and local troubleshooting

## Supported Pilot Topology

The intended pilot topology is:

- one household
- one self-hosted local edge device
- one local Sentinel Core instance
- existing household systems kept in place
- controlled operator review through the local ops console

## Compatibility Position

Sentinel Core should not currently claim universal compatibility.

Current guidance should remain:

- Jetson Orin Nano is recommended
- future compatible edge devices are possible
- compatibility should be validated before the pilot begins
