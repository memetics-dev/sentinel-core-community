import { PublicCta } from "@/components/public/cta";
import { PublicSection } from "@/components/public/section";
import { PublicShell } from "@/components/public/shell";

const steps = [
  {
    step: "01",
    title: "Prepare the local node",
    detail:
      "Install Sentinel Core onto a compatible edge device and connect it to the trusted home network.",
  },
  {
    step: "02",
    title: "Discover and pair locally",
    detail:
      "A mobile companion or local browser discovers the node, confirms identity, and begins guided pairing.",
  },
  {
    step: "03",
    title: "Name the household zones",
    detail:
      "Map sensors into plain-language spaces such as Driveway, Garage, Hallway, Kitchen, Living Room, and Bedroom.",
  },
  {
    step: "04",
    title: "Run validation scenarios",
    detail:
      "Confirm quiet-night behaviour, trusted continuity, and unknown progression before beginning the pilot.",
  },
  {
    step: "05",
    title: "Review readiness",
    detail:
      "Check local evidence, pairing state, and household validation outcomes before active pilot use.",
  },
];

const pairingItems = [
  { label: "Driveway motion sensor", state: "Paired", zone: "Driveway" },
  { label: "Garage motion sensor", state: "Paired", zone: "Garage" },
  { label: "Hallway motion sensor", state: "Ready to validate", zone: "Hallway" },
  { label: "Resident BLE tag", state: "Trusted continuity available", zone: "Identity" },
];

const validationChecks = [
  "Quiet Night baseline remains calm with no unusual escalation.",
  "Trusted night movement shows continuity and restrained response posture.",
  "Unknown perimeter progression elevates concern across connected zones.",
  "Local evidence is visible for operator review before pilot activation.",
];

export default function PublicOnboardingPreviewPage() {
  return (
    <PublicShell>
      <header className="rounded-[36px] border border-white/8 bg-[radial-gradient(circle_at_top_left,rgba(113,159,174,0.12),transparent_28%),radial-gradient(circle_at_82%_20%,rgba(78,140,133,0.1),transparent_24%),linear-gradient(180deg,rgba(8,16,26,0.98),rgba(6,11,18,0.98))] px-6 py-8 shadow-[0_40px_140px_rgba(0,0,0,0.52)] md:px-10 md:py-10">
        <div className="max-w-4xl">
          <p className="text-[0.68rem] uppercase tracking-[0.36em] text-teal-200/60">Future Self-Hosted Setup</p>
          <h1 className="mt-4 text-4xl font-semibold tracking-[-0.03em] text-slate-50 md:text-5xl">
            A guided local onboarding path for privacy-first pilot households.
          </h1>
          <p className="mt-4 max-w-3xl text-base leading-8 text-slate-300">
            This preview illustrates how a future Sentinel Core node could be prepared, paired, validated, and reviewed without turning setup into a cloud-managed process. The experience shown here uses static mock data only.
          </p>
        </div>
      </header>

      <div className="grid gap-6 lg:grid-cols-[1.05fr_0.95fr]">
        <PublicSection eyebrow="What You Need" title="Curated hardware, local networking, guided setup.">
          <div className="grid gap-4 sm:grid-cols-2">
            {[
              ["Recommended node", "NVIDIA Jetson Orin Nano or future curated compatible edge hardware."],
              ["Sensors", "Supported perimeter and indoor motion sensors, with optional BLE identity tags."],
              ["Networking", "Trusted local Wi-Fi or Ethernet, with the node and onboarding device on the same network."],
              ["Operator tools", "A phone or local browser for guided pairing, naming, and validation review."],
            ].map(([title, text]) => (
              <div key={title} className="rounded-2xl border border-white/10 bg-[#0b0f17]/92 p-5">
                <h3 className="text-sm font-semibold uppercase tracking-[0.24em] text-[#cad2f5]">{title}</h3>
                <p className="mt-3 text-sm leading-7 text-[#b7bfdc]">{text}</p>
              </div>
            ))}
          </div>
        </PublicSection>

        <PublicSection eyebrow="Pilot Compatibility" title="Measured compatibility over broad promises.">
          <div className="space-y-4 text-sm leading-7 text-[#bcc5e5]">
            <p>
              Sentinel Core pilot support is intentionally curated. The immediate goal is not universal smart-home coverage. The goal is a believable, self-hosted household intelligence system that behaves consistently on known hardware.
            </p>
            <p>
              Home Assistant remains a planned future pathway for compatibility expansion, but onboarding should not depend on broad third-party integration claims before the pilot hardware and pairing experience are stable.
            </p>
            <p>
              Future compatible edge devices may be added over time, but each addition should preserve local-first processing, privacy, and explainable household topology.
            </p>
          </div>
        </PublicSection>
      </div>

      <PublicSection eyebrow="Onboarding Sequence" title="A future setup flow that guides the household from hardware to validation.">
        <div className="grid gap-4 lg:grid-cols-5">
          {steps.map((item) => (
            <article key={item.step} className="rounded-[1.5rem] border border-white/10 bg-[#0b1019]/94 p-5 shadow-[0_20px_50px_rgba(0,0,0,0.22)] transition duration-200 hover:border-white/16 hover:bg-[#0d1320]">
              <p className="text-xs uppercase tracking-[0.32em] text-[#8fa1df]">{item.step}</p>
              <h3 className="mt-3 text-lg font-semibold text-white">{item.title}</h3>
              <p className="mt-3 text-sm leading-7 text-[#b9c2e0]">{item.detail}</p>
            </article>
          ))}
        </div>
      </PublicSection>

      <div className="grid gap-6 lg:grid-cols-[0.95fr_1.05fr]">
        <PublicSection eyebrow="Simulated Pairing State" title="Connected deliberately, not automatically.">
          <div className="space-y-3">
            {pairingItems.map((item) => (
              <div key={item.label} className="rounded-2xl border border-white/10 bg-[#0b1018]/92 p-4">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <h3 className="text-base font-medium text-white">{item.label}</h3>
                    <p className="mt-1 text-sm text-[#b7bfdc]">Assigned zone: {item.zone}</p>
                  </div>
                  <span className="rounded-full border border-[#8bd7c0]/22 bg-[#8bd7c0]/10 px-3 py-1 text-xs uppercase tracking-[0.22em] text-[#a7ecd6]">
                    {item.state}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </PublicSection>

        <PublicSection eyebrow="Validation and Readiness" title="The system should feel credible before the pilot begins.">
          <div className="space-y-3">
            {validationChecks.map((check) => (
              <div key={check} className="rounded-2xl border border-white/10 bg-[#0b1018]/92 p-4 text-sm leading-7 text-[#c4cbea]">
                {check}
              </div>
            ))}
          </div>
          <div className="mt-6 rounded-2xl border border-[#8da7ff]/16 bg-[#0c1220]/92 p-5 text-sm leading-7 text-[#bcc6e8]">
            The future onboarding goal is simple: the household should understand what is connected, what is trusted, what has been validated, and whether the node is genuinely ready for controlled pilot use.
          </div>
        </PublicSection>
      </div>

      <PublicCta
        eyebrow="Onboarding and Installation"
        title="The onboarding path is designed to make local-first deployment understandable, not opaque."
        body="Customers should be able to follow a guided path from compatible hardware through pairing, validation, and household readiness without turning Sentinel Core into a cloud-managed setup experience."
        secondaryLabel="Review Installation Path"
        secondaryHref="/public/installation"
      />
    </PublicShell>
  );
}
