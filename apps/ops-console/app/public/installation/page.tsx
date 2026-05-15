import { PublicCta } from "@/components/public/cta";
import { PublicSection } from "@/components/public/section";
import { PublicShell } from "@/components/public/shell";

const processItems = [
  "Prepare compatible customer-owned edge hardware, currently centered on the curated Jetson Orin Nano path.",
  "Review support boundaries, networking assumptions, and household fit before installation begins.",
  "Receive guided access to the current installer materials and deployment instructions during pilot onboarding.",
  "Install Sentinel Core locally, pair supported sensors, and complete validation before active pilot use.",
];

const boundaryItems = [
  "The current installer scripts are MVP deployment tooling, not a one-click consumer download.",
  "Public visitors can understand the process and requirements, but pilot customers receive the appropriate installation package during onboarding.",
  "Customers are guided through hardware preparation, installation, validation, and operational support boundaries.",
  "The public site does not expose live installer execution, real provisioning, or local household controls.",
];

export default function PublicInstallationPage() {
  return (
    <PublicShell>
      <header className="rounded-[36px] border border-white/8 bg-[radial-gradient(circle_at_top_left,rgba(113,159,174,0.12),transparent_28%),radial-gradient(circle_at_82%_20%,rgba(78,140,133,0.1),transparent_24%),linear-gradient(180deg,rgba(8,16,26,0.98),rgba(6,11,18,0.98))] px-6 py-8 shadow-[0_40px_140px_rgba(0,0,0,0.52)] md:px-10 md:py-10">
        <div className="max-w-4xl">
          <p className="text-[0.68rem] uppercase tracking-[0.36em] text-teal-200/60">Installation Path</p>
          <h1 className="mt-4 text-4xl font-semibold tracking-[-0.03em] text-slate-50 md:text-5xl">
            Guided self-hosted installation is part of the pilot path, not yet a public consumer download.
          </h1>
          <p className="mt-4 max-w-3xl text-base leading-8 text-slate-300">
            Sentinel Core is preparing a self-hosted installer path for customer-owned edge hardware. Early customers receive guided access to the current installer materials during onboarding rather than an open one-click download.
          </p>
        </div>
      </header>

      <div className="grid gap-6 lg:grid-cols-[1fr_1fr]">
        <PublicSection eyebrow="How Access Works" title="The process is visible publicly. The install package is issued during pilot onboarding.">
          <div className="space-y-3">
            {processItems.map((item, index) => (
              <div key={item} className="rounded-2xl border border-white/10 bg-[#0b1018]/92 p-4 text-sm leading-7 text-[#c4cbea]">
                <span className="mr-3 text-[0.72rem] uppercase tracking-[0.22em] text-[#8fa1df]">0{index + 1}</span>
                {item}
              </div>
            ))}
          </div>
        </PublicSection>

        <PublicSection eyebrow="Current Boundary" title="The current installer exists, but it is still framed as guided MVP deployment tooling.">
          <div className="space-y-3">
            {boundaryItems.map((item) => (
              <div key={item} className="rounded-2xl border border-white/10 bg-[#0b1018]/92 p-4 text-sm leading-7 text-[#c4cbea]">
                {item}
              </div>
            ))}
          </div>
        </PublicSection>
      </div>

      <PublicCta
        eyebrow="Installation and Support"
        title="Customers are guided through hardware preparation, installation, validation, and support boundaries."
        body="The early self-hosted path is designed to be transparent and credible. It remains curated, support-aware, and grounded in local-first operational reasoning rather than broad consumer automation claims."
        secondaryLabel="Preview Deployment"
        secondaryHref="/public/deployment-preview"
      />
    </PublicShell>
  );
}
