# Installation Overview

## Purpose

This overview explains the expected self-hosted installation model for Sentinel Core pilot customers.

## Local-Only Architecture

Sentinel Core is designed to run locally within the customer environment.

Core assumptions:

- local processing remains on the edge device
- household intelligence remains customer-controlled
- local operational review happens through the self-hosted ops console
- the system does not depend on managed cloud inference for the pilot model described here

## Expected Networking Assumptions

A typical pilot environment should provide:

- a stable local network
- local access between the edge device and the operator console device
- local service discovery or known local addresses for setup
- no requirement for permanent external cloud connectivity to run the core local pilot experience

## Installation Flow

1. prepare the compatible edge device
2. install Sentinel Core locally
3. confirm local startup of Edge Core and the ops console
4. verify local routes and pilot readiness
5. connect the existing household systems intended for the pilot pathway
6. run scenario validation before live household evaluation

## Before Pilot Go-Live

Before beginning a household pilot:

- run the scenario validation scripts
- verify session grouping and evidence export
- verify the operator can review incidents, narratives, and pilot notes clearly
- confirm the household understands the pilot boundaries and support model
