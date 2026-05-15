import { PublicCta } from "@/components/public/cta";
import { PublicSection } from "@/components/public/section";
import { PublicShell } from "@/components/public/shell";

const readinessItems = [
  {
    title: "What exists today",
    body:
      "A local-first Sentinel Core node, an operational review console, deterministic scenarios, trial reports, and a curated self-hosted positioning model.",
  },
  {
    title: "What pilot customers can expect",
    body:
      "Guided onboarding, a clearly bounded hardware path, local evidence review, controlled validation scenarios, and operational honesty about current limits.",
  },
  {
    title: "What is still evolving",
    body:
      "Broader compatibility, smoother first-run packaging, wider sensor support, and lower-touch onboarding beyond the current controlled path.",
  },
];

const audience = [
  "Technically comfortable homeowners",
  "Pilot households willing to follow a guided self-install path",
  "High-end residential experimentation with clear operational review",
  "Privacy-focused users who prefer local-first intelligence over cloud dependency",
];

const boundaries = [
  "Sentinel Core is intelligence assistance, not guaranteed prevention.",
  "Compatibility is curated and explicit, not universal.",
  "Human judgment and escalation remain necessary in uncertain or serious situations.",
  "Local power, networking, and supported hardware remain part of safe operation.",
];

export default function PublicMarketReadinessPage() {
  return (
    <PublicShell>
      <header className="rounded-[36px] border border-white/8 bg-[radial-gradient(circle_at_top_left,rgba(113,159,174,0.12),transparent_28%),radial-gradient(circle_at_82%_20%,rgba(78,140,133,0.1),transparent_24%),linear-gradient(180deg,rgba(8,16,26,0.98),rgba(6,11,18,0.98))] px-6 py-8 shadow-[0_40px_140px_rgba(0,0,0,0.52)] md:px-10 md:py-10">
        <div className="max-w-4xl">
          <p className="text-[0.68rem] uppercase tracking-[0.36em] text-teal-200/60">Market Readiness</p>
          <h1 className="mt-4 text-4xl font-semibold tracking-[-0.03em] text-slate-50 md:text-5xl">
            The smallest credible Sentinel Core package is deliberate, local, and bounded.
          </h1>
          <p className="mt-4 max-w-3xl text-base leading-8 text-slate-300">
            Sentinel Core is moving toward a controlled self-install package for pilot households. The objective is not universal readiness. The objective is a credible package that a real customer can install, validate, and operate safely without hidden founder dependency.
          </p>
        </div>
      </header>

      <div className="grid gap-6 lg:grid-cols-3">
        {readinessItems.map((item) => (
          <PublicSection key={item.title} eyebrow="Readiness Scope" title={item.title} body={item.body} />
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-[1fr_1fr]">
        <PublicSection eyebrow="Who Sentinel Core Is For Right Now" title="A precise early audience is a strength, not a weakness.">
          <div className="space-y-3">
            {audience.map((item) => (
              <div key={item} className="rounded-2xl border border-white/10 bg-[#0b1018]/92 p-4 text-sm leading-7 text-[#c4cbea]">
                {item}
              </div>
            ))}
          </div>
        </PublicSection>

        <PublicSection eyebrow="Controlled Onboarding" title="The package only works if installation, validation, and review remain disciplined.">
          <div className="space-y-4 text-sm leading-7 text-[#bcc6e8]">
            <p>
              Customers should be able to move from compatible hardware to local operation with a guided path: install the node, pair supported sensors, name zones, run validation scenarios, review evidence locally, and begin a controlled household pilot.
            </p>
            <p>
              This still assumes curated support and a bounded operating model. The goal is self-install without pretending the system is already universal, unmanaged, or risk-free.
            </p>
          </div>
        </PublicSection>
      </div>

      <PublicSection eyebrow="Safety and Honesty" title="Pilot customers should know exactly what Sentinel Core does and does not claim.">
        <div className="grid gap-4 lg:grid-cols-2">
          {boundaries.map((item) => (
            <div key={item} className="rounded-2xl border border-white/10 bg-[#0b1019]/94 p-5 text-sm leading-7 text-[#c0c9e8]">
              {item}
            </div>
          ))}
        </div>
      </PublicSection>

      <PublicCta
        eyebrow="Readiness Review"
        title="Controlled market readiness depends on disciplined self-hosted onboarding and honest support boundaries."
        body="Before a customer begins a pilot, Sentinel Core reviews hardware fit, installation path, operational stability, validation discipline, and customer safety assumptions."
        secondaryLabel="Review Installation Path"
        secondaryHref="/public/installation"
      />
    </PublicShell>
  );
}
