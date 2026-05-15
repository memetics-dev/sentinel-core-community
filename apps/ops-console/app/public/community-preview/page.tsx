import { PublicCta } from "@/components/public/cta";
import { PublicSection } from "@/components/public/section";
import { PublicShell } from "@/components/public/shell";

const included = [
  "Edge Core local runtime",
  "Ops console",
  "Public product and demo pages",
  "Installer MVP scripts",
  "Scenario scripts",
  "Trial review tools",
  "Documentation",
];

const excluded = [
  "Production mobile app",
  "Universal hardware support",
  "Cloud account system",
  "Managed monitoring",
  "Certified alarm-company replacement",
  "Production installer or image flashing",
];

const contributions = [
  "Docs clarity",
  "Installer ergonomics",
  "Hardware notes",
  "Scenario feedback",
  "UI polish",
];

export default function PublicCommunityPreviewPage() {
  return (
    <PublicShell>
      <header className="rounded-[36px] border border-white/8 bg-[radial-gradient(circle_at_top_left,rgba(113,159,174,0.12),transparent_28%),radial-gradient(circle_at_82%_20%,rgba(78,140,133,0.1),transparent_24%),linear-gradient(180deg,rgba(8,16,26,0.98),rgba(6,11,18,0.98))] px-6 py-8 shadow-[0_40px_140px_rgba(0,0,0,0.52)] md:px-10 md:py-10">
        <div className="max-w-4xl">
          <p className="text-[0.68rem] uppercase tracking-[0.36em] text-teal-200/60">Community Preview</p>
          <h1 className="mt-4 text-4xl font-semibold tracking-[-0.03em] text-slate-50 md:text-5xl">
            A carefully scoped public preview for developers, edge-AI builders, and early technical evaluators.
          </h1>
          <p className="mt-4 max-w-3xl text-base leading-8 text-slate-300">
            Sentinel Core Community Preview is a local-first residential intelligence preview for controlled testing first. It is not a production alarm replacement, guaranteed prevention system, or managed monitoring service.
          </p>
        </div>
      </header>

      <div className="grid gap-6 lg:grid-cols-[1fr_1fr]">
        <PublicSection eyebrow="Included" title="A usable technical preview with local tooling and review surfaces.">
          <div className="space-y-3">
            {included.map((item) => (
              <div key={item} className="rounded-2xl border border-white/10 bg-[#0b1018]/92 p-4 text-sm leading-7 text-slate-300">
                {item}
              </div>
            ))}
          </div>
        </PublicSection>

        <PublicSection eyebrow="Not Included" title="Boundaries remain explicit and commercially responsible.">
          <div className="space-y-3">
            {excluded.map((item) => (
              <div key={item} className="rounded-2xl border border-white/10 bg-[#0b1018]/92 p-4 text-sm leading-7 text-slate-300">
                {item}
              </div>
            ))}
          </div>
        </PublicSection>
      </div>

      <PublicSection eyebrow="Safe Testing Path" title="Use controlled local testing before any operational trust.">
        <div className="space-y-4 text-sm leading-7 text-slate-300">
          <p>
            Start with simulated public scenarios, then local installer checks, then passive observation, and only then move into more realistic household testing. Sentinel Core Community Preview should not be used as primary security.
          </p>
          <p>
            Jetson Orin Nano remains the recommended future node target, but the current repository can be explored on a normal development machine first.
          </p>
        </div>
      </PublicSection>

      <PublicSection eyebrow="Community Contributions" title="The most useful community work improves clarity, ergonomics, and realism.">
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
          {contributions.map((item) => (
            <div key={item} className="rounded-2xl border border-white/10 bg-[#0b1019]/94 p-4 text-sm leading-7 text-slate-300">
              {item}
            </div>
          ))}
        </div>
      </PublicSection>

      <PublicCta
        eyebrow="Community Preview Direction"
        title="Community Preview is for careful local exploration, not broad security claims."
        body="It exists to help technical evaluators understand the system, improve installation and documentation ergonomics, and stress the local-first residential intelligence model under controlled conditions."
        secondaryLabel="Review Installation Path"
        secondaryHref="/public/installation"
      />
    </PublicShell>
  );
}
