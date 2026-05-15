import { PublicCta } from "@/components/public/cta";
import { PublicSection } from "@/components/public/section";
import { PublicShell } from "@/components/public/shell";

const flow = [
  {
    step: "01",
    title: "Prepare compatible hardware",
    detail:
      "Start with a recommended edge device, stable power, trusted local networking, and the supported pilot sensor set.",
  },
  {
    step: "02",
    title: "Flash or install Sentinel Core",
    detail:
      "Install the curated Sentinel Core node image or deployment bundle onto the local node.",
  },
  {
    step: "03",
    title: "Boot the node locally",
    detail:
      "Bring the device online, connect it to the household network, and confirm it reaches a ready-for-onboarding state.",
  },
  {
    step: "04",
    title: "Discover and onboard",
    detail:
      "Use a phone or local browser to discover the node, attach to the onboarding flow, and begin setup.",
  },
  {
    step: "05",
    title: "Pair and validate",
    detail:
      "Pair supported sensors, name zones, validate household behaviour, and confirm readiness before pilot use.",
  },
];

const deploymentChecks = [
  "Node image installed and booted locally",
  "Local discovery available on the trusted network",
  "Supported sensors paired to named zones",
  "Quiet baseline and hostile progression checks completed",
  "Local review and evidence workflows confirmed",
];

const recoveryPoints = [
  "Core local operation should continue even when internet access is unavailable.",
  "Updates should be controlled and understandable, not silently imposed.",
  "Rollback should favor a known good node state over improvisation.",
  "Household-safe recovery assumes clear restart, revalidation, and review steps.",
];

const notAutomated = [
  "Universal sensor discovery across arbitrary devices",
  "Unsupported edge hardware enablement",
  "Advanced remote management or fleet control",
  "Unbounded compatibility migration without validation",
];

export default function PublicDeploymentPreviewPage() {
  return (
    <PublicShell>
      <header className="rounded-[36px] border border-white/8 bg-[radial-gradient(circle_at_top_left,rgba(113,159,174,0.12),transparent_28%),radial-gradient(circle_at_82%_20%,rgba(78,140,133,0.1),transparent_24%),linear-gradient(180deg,rgba(8,16,26,0.98),rgba(6,11,18,0.98))] px-6 py-8 shadow-[0_40px_140px_rgba(0,0,0,0.52)] md:px-10 md:py-10">
        <div className="max-w-4xl">
          <p className="text-[0.68rem] uppercase tracking-[0.36em] text-teal-200/60">Deployment Ergonomics</p>
          <h1 className="mt-4 text-4xl font-semibold tracking-[-0.03em] text-slate-50 md:text-5xl">
            A future Sentinel Core deployment path should feel guided, local, and recoverable.
          </h1>
          <p className="mt-4 max-w-3xl text-base leading-8 text-slate-300">
            This preview simulates how a first-generation self-hosted deployment experience could work on customer-owned edge hardware. It uses static mock data only and does not perform real provisioning.
          </p>
        </div>
      </header>

      <PublicSection
        eyebrow="How Deployment Works"
        title="Install the node, connect it locally, then validate the household before activation."
      >
        <div className="grid gap-4 lg:grid-cols-5">
          {flow.map((item) => (
            <article key={item.step} className="rounded-[1.5rem] border border-white/10 bg-[#0b1019]/94 p-5 shadow-[0_20px_50px_rgba(0,0,0,0.22)] transition duration-200 hover:border-white/16 hover:bg-[#0d1320]">
              <p className="text-xs uppercase tracking-[0.32em] text-[#8fa1df]">{item.step}</p>
              <h3 className="mt-3 text-lg font-semibold text-white">{item.title}</h3>
              <p className="mt-3 text-sm leading-7 text-[#b9c2e0]">{item.detail}</p>
            </article>
          ))}
        </div>
      </PublicSection>

      <div className="grid gap-6 lg:grid-cols-[1fr_1fr]">
        <PublicSection eyebrow="Validation Checks" title="Deployment should end with household readiness, not just a powered node.">
          <div className="space-y-3">
            {deploymentChecks.map((check) => (
              <div key={check} className="rounded-2xl border border-white/10 bg-[#0b1018]/92 p-4 text-sm leading-7 text-[#c4cbea]">
                {check}
              </div>
            ))}
          </div>
        </PublicSection>

        <PublicSection eyebrow="Reliability and Recovery" title="Local operation should remain understandable even when conditions are imperfect.">
          <div className="space-y-3">
            {recoveryPoints.map((point) => (
              <div key={point} className="rounded-2xl border border-white/10 bg-[#0b1018]/92 p-4 text-sm leading-7 text-[#c4cbea]">
                {point}
              </div>
            ))}
          </div>
        </PublicSection>
      </div>

      <PublicSection eyebrow="What Sentinel Core Does Not Yet Automate" title="The first-generation deployment path stays intentionally bounded.">
        <div className="grid gap-4 lg:grid-cols-2">
          {notAutomated.map((item) => (
            <div key={item} className="rounded-2xl border border-white/10 bg-[#0b1019]/94 p-5 text-sm leading-7 text-[#c0c9e8]">
              {item}
            </div>
          ))}
        </div>
      </PublicSection>

      <PublicCta
        eyebrow="Installation and Deployment"
        title="Controlled deployment remains part of the guided pilot path."
        body="Deployment previews, installation path guidance, and onboarding expectations are shown publicly so customers understand what is mature, what is curated, and what still requires guided support."
        secondaryLabel="Review Installation Path"
        secondaryHref="/public/installation"
      />
    </PublicShell>
  );
}
