# Pilot Scenario Suite

## Purpose

This scenario suite provides a consistent set of controlled household tests for Sentinel Core pilot evaluations.

The goal is disciplined comparison across realistic household conditions, not feature discovery.

## General Run Discipline

Before each scenario:

1. stop Edge Core if a clean state is required
2. run `bash services/edge-core/scripts/reset_demo_state.sh`
3. restart Edge Core
4. open `/trial-review`
5. start a new trial session label
6. execute one scenario only
7. review incidents, narratives, responses, and pilot notes before moving to the next scenario

## Quiet Night Baseline

### Purpose

Confirm that Sentinel Core stays calm when Night Lock is active and no meaningful activity is introduced.

### Setup

- clean reset recommended
- start a fresh trial session

### Commands Or Manual Steps

```bash
bash services/edge-core/scripts/scenario_quiet_night_baseline.sh
```

### Expected System Behaviour

- mode changes to `night_lock`
- no new incidents should appear
- no active response posture should appear
- narratives should remain absent or minimal

### What To Inspect In Ops Console

- overview status
- `/incidents`
- `/trial-review`

### Suggested Pilot Note

- Night Lock baseline remained calm with no unnecessary incident activity.

### Suggested Feedback Label

- no incident feedback required unless unexpected activity appears

## Trusted Night Movement

### Purpose

Confirm that trusted continuity suppresses or softens follow-on kitchen movement during Night Lock.

### Setup

- clean reset recommended
- start a fresh trial session

### Commands Or Manual Steps

```bash
bash services/edge-core/scripts/demo_trusted_presence_flow.sh
```

### Expected System Behaviour

- trusted BLE presence is recorded first
- kitchen motion is treated more calmly than unknown garage intrusion
- response guidance remains restrained
- narratives explain trusted continuity rather than hostile progression

### What To Inspect In Ops Console

- presence page
- response panel on overview
- trial review metrics and narratives

### Suggested Pilot Note

- Trusted presence reduced escalation appropriately before kitchen movement.

### Suggested Feedback Label

- `correct_detection` if the restrained posture felt appropriate

## Unknown Perimeter Progression

### Purpose

Confirm that perimeter-to-indoor progression reads as a coherent hostile scenario.

### Setup

- clean reset recommended
- start a fresh trial session

### Commands Or Manual Steps

```bash
bash services/edge-core/scripts/demo_intrusion_flow.sh
```

### Expected System Behaviour

- driveway activity appears first
- garage movement follows with elevated concern
- hallway and kitchen movement extend the progression
- incidents, correlations, response posture, and narratives stay aligned

### What To Inspect In Ops Console

- overview incident priority strip
- incident detail replay and timeline
- trial review report summary

### Suggested Pilot Note

- Intrusion progression felt believable from driveway into garage and indoor zones.

### Suggested Feedback Label

- `correct_detection`

## Ambiguous Hallway Movement

### Purpose

Check how Sentinel Core handles indoor transitional motion without a clear hostile entry chain.

### Setup

- clean reset recommended
- start a fresh trial session

### Commands Or Manual Steps

```bash
bash services/edge-core/scripts/scenario_ambiguous_hallway_motion.sh
```

### Expected System Behaviour

- hallway movement may be suspicious or monitoring-worthy
- concern should remain lower than driveway-to-garage intrusion
- response wording should remain calm

### What To Inspect In Ops Console

- threats
- active responses
- narratives
- trial review notes panel

### Suggested Pilot Note

- Hallway motion remained ambiguous and did not read as a clear intrusion chain.

### Suggested Feedback Label

- `uncertain`

## Repeated Low-Confidence Noise

### Purpose

Evaluate whether weak repeated signals remain restrained instead of escalating aggressively.

### Setup

- clean reset recommended
- start a fresh trial session

### Commands Or Manual Steps

```bash
bash services/edge-core/scripts/scenario_low_confidence_noise.sh
```

### Expected System Behaviour

- multiple low-confidence signals are recorded
- monitoring or silent review may appear
- urgent or critical posture should be uncommon without stronger support

### What To Inspect In Ops Console

- response history
- recent correlations
- trial metrics

### Suggested Pilot Note

- Repeated low-confidence noise remained reviewable without disproportionate escalation.

### Suggested Feedback Label

- `correct_detection` or `false_positive` depending on observed posture

## Trusted Presence Then Unknown Garage

### Purpose

Confirm that earlier trusted continuity does not incorrectly calm a later hostile garage pattern.

### Setup

- clean reset recommended
- start a fresh trial session

### Commands Or Manual Steps

```bash
bash services/edge-core/scripts/scenario_trusted_then_unknown_garage.sh
```

### Expected System Behaviour

- trusted continuity is recorded first
- later garage motion still raises concern
- hostile framing should override calming continuity language if needed

### What To Inspect In Ops Console

- current narratives
- active responses
- incident list
- trial report summary

### Suggested Pilot Note

- Earlier trusted continuity did not prevent later garage movement from being treated as suspicious.

### Suggested Feedback Label

- `correct_detection`

## Daytime Garage Activity

### Purpose

Compare daytime garage movement with higher-sensitivity nighttime garage behaviour.

### Setup

- clean reset recommended
- start a fresh trial session

### Commands Or Manual Steps

```bash
bash services/edge-core/scripts/scenario_daytime_garage_activity.sh
```

### Expected System Behaviour

- mode changes to `home_active`
- garage movement remains reviewable but calmer than Night Lock garage movement
- response and narrative language should be less severe

### What To Inspect In Ops Console

- threats
- response panel
- current narratives

### Suggested Pilot Note

- Daytime garage activity remained lower concern than the Night Lock intrusion pattern.

### Suggested Feedback Label

- `correct_detection` if the reduced concern felt proportionate

## Session Evidence Review

### Purpose

Confirm that session grouping, pilot notes, metrics, report, and export all stay coherent for one controlled run.

### Setup

- after completing any scenario above
- keep the current session open until review is complete

### Commands Or Manual Steps

- open `/trial-review`
- record one or more pilot notes
- download report JSON
- download export JSON
- end the session only after evidence is retained

### Expected System Behaviour

- session notes appear in the pilot note panel
- session conclusions update deterministically
- report JSON includes pilot notes and conclusions
- export JSON includes pilot notes and conclusions

### What To Inspect In Ops Console

- trial session panel
- pilot session notes panel
- trial report summary
- trial evidence download section

### Suggested Pilot Note

- Session evidence remained coherent and grouped cleanly for operator review.

### Suggested Feedback Label

- `narrative_helpful` or `narrative_confusing` if the review flow exposed narrative clarity issues
