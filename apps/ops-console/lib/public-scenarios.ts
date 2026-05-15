export type PublicScenario = {
  slug: string;
  title: string;
  badge: string;
  purpose: string;
  summary: string;
  sequence: string[];
  interpretation: string;
  threatPosture: string;
  responseRecommendation: string;
  narrativeExplanation: string;
  operatorReview: string[];
  postureTone: "calm" | "guarded" | "elevated" | "critical";
};

export const publicScenarios: PublicScenario[] = [
  {
    slug: "quiet-night-baseline",
    title: "Quiet Night Baseline",
    badge: "Calm Baseline",
    purpose:
      "Show that Sentinel Core can remain quiet when the home appears settled and there is no meaningful reason to escalate.",
    summary:
      "A still overnight household used to show that Sentinel Core can preserve calm rather than create unnecessary alarm.",
    sequence: [
      "Night Lock is active.",
      "No trusted alerts or motion progression appears.",
      "The household remains settled.",
    ],
    interpretation:
      "Sentinel Core reads the household as quiet and does not create false urgency.",
    threatPosture: "Low concern. No open incident expected.",
    responseRecommendation:
      "Monitor only. No operator action needed.",
    narrativeExplanation:
      "The system preserves a calm baseline instead of escalating an uneventful night.",
    operatorReview: [
      "Confirm the household state remains calm.",
      "Confirm no unnecessary incident is opened.",
      "Confirm no aggressive response recommendation appears.",
    ],
    postureTone: "calm",
  },
  {
    slug: "trusted-night-movement",
    title: "Trusted Night Movement",
    badge: "Trusted Continuity",
    purpose:
      "Show how known occupant continuity can keep late-night household movement from being treated like an intrusion.",
    summary:
      "A trusted resident signal appears before late-night kitchen movement, showing suppression instead of alarmism.",
    sequence: [
      "Night Lock is active.",
      "Trusted BLE continuity is observed in the kitchen.",
      "Follow-on indoor motion appears in the same context.",
    ],
    interpretation:
      "Sentinel Core reads the movement as more likely connected to a known occupant than an intrusion chain.",
    threatPosture: "Elevated awareness, but intentionally lower than unknown motion.",
    responseRecommendation:
      "Silent review or occupant verification, depending on the wider context.",
    narrativeExplanation:
      "Trusted continuity lowers escalation confidence and explains why the posture remains restrained.",
    operatorReview: [
      "Check whether trusted continuity was recent and coherent.",
      "Confirm the kitchen movement stayed lower-risk than garage intrusion.",
      "Review whether the narrative explained the suppression clearly.",
    ],
    postureTone: "guarded",
  },
  {
    slug: "unknown-perimeter-progression",
    title: "Unknown Perimeter Progression",
    badge: "Hostile Progression",
    purpose:
      "Show how connected perimeter and indoor movement can read as a believable intrusion-style progression.",
    summary:
      "Unknown movement begins outside and progresses inward, showing how Sentinel Core links the household path together.",
    sequence: [
      "Driveway activity appears first.",
      "Garage movement follows.",
      "Interior transitional movement continues toward the kitchen.",
    ],
    interpretation:
      "Sentinel Core treats the sequence as a coherent progression across connected household zones.",
    threatPosture: "High threat to critical, depending on the full chain and household mode.",
    responseRecommendation:
      "Active security response with clear operator review priority.",
    narrativeExplanation:
      "Perimeter-originated movement with no trusted continuity raises intrusion confidence.",
    operatorReview: [
      "Review the incident replay and timeline.",
      "Confirm the progression stayed coherent across connected zones.",
      "Check whether the response posture matched the severity.",
    ],
    postureTone: "critical",
  },
  {
    slug: "ambiguous-hallway-motion",
    title: "Ambiguous Hallway Motion",
    badge: "Ambiguous Interior",
    purpose:
      "Show how Sentinel Core handles uncertainty without turning every indoor movement event into a confirmed hostile entry.",
    summary:
      "A hallway event appears without a clear perimeter lead-in, testing how the system treats uncertainty.",
    sequence: [
      "Night Lock is active.",
      "Hallway movement appears with moderate confidence.",
      "No strong perimeter chain is established.",
    ],
    interpretation:
      "Sentinel Core treats the situation as review-worthy, but not automatically equivalent to an intrusion chain.",
    threatPosture: "Moderate concern. Lower than a perimeter-to-garage progression.",
    responseRecommendation:
      "Silent operator review or continued monitoring unless other signals raise concern.",
    narrativeExplanation:
      "The system explains that the movement is notable, but the surrounding context remains incomplete.",
    operatorReview: [
      "Compare hallway risk with stronger hostile scenarios.",
      "Check whether the language stayed calm under ambiguity.",
      "Review whether the operator would know what to do next.",
    ],
    postureTone: "elevated",
  },
  {
    slug: "trusted-then-unknown-garage",
    title: "Trusted Then Unknown Garage",
    badge: "Mixed Signals",
    purpose:
      "Show that earlier trusted continuity should not incorrectly calm a later garage pattern that deserves fresh scrutiny.",
    summary:
      "Trusted continuity appears first, but later unknown garage movement tests whether the system can separate benign context from a new concern.",
    sequence: [
      "Trusted kitchen presence is recorded.",
      "Later garage movement appears without trusted continuity in that zone.",
      "The system re-evaluates the posture based on the newer pattern.",
    ],
    interpretation:
      "Sentinel Core preserves earlier trusted context while still allowing later garage activity to raise concern on its own merits.",
    threatPosture: "Escalated concern for the garage event despite earlier benign continuity elsewhere.",
    responseRecommendation:
      "Operator review with elevated urgency if the garage signal reads hostile.",
    narrativeExplanation:
      "Earlier trusted continuity should not incorrectly calm a later garage signal that looks meaningfully different.",
    operatorReview: [
      "Confirm later hostile signals override earlier calming context when appropriate.",
      "Review whether narrative framing remained situationally coherent.",
      "Check whether the mixed-signal story still felt believable.",
    ],
    postureTone: "elevated",
  },
];

export function getPublicScenarioBySlug(scenarioSlug: string) {
  return publicScenarios.find((scenario) => scenario.slug === scenarioSlug);
}
