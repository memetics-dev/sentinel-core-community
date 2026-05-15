import { notFound } from "next/navigation";

import { PublicCta } from "@/components/public/cta";
import { PublicSection } from "@/components/public/section";
import { PublicShell } from "@/components/public/shell";
import { getPublicScenarioBySlug, publicScenarios } from "@/lib/public-scenarios";

const toneClasses = {
  calm: "border-emerald-300/12 bg-emerald-300/[0.05] text-emerald-100",
  guarded: "border-teal-300/12 bg-teal-300/[0.05] text-teal-100",
  elevated: "border-amber-300/12 bg-amber-300/[0.05] text-amber-100",
  critical: "border-rose-300/12 bg-rose-300/[0.05] text-rose-100",
};

export function generateStaticParams() {
  return publicScenarios.map((scenario) => ({ scenarioSlug: scenario.slug }));
}

export default function PublicScenarioDetailPage({ params }: { params: { scenarioSlug: string } }) {
  const scenario = getPublicScenarioBySlug(params.scenarioSlug);

  if (!scenario) {
    notFound();
  }

  return (
    <PublicShell>
      <header className="rounded-[36px] border border-white/8 bg-[radial-gradient(circle_at_top_left,rgba(113,159,174,0.12),transparent_28%),radial-gradient(circle_at_82%_20%,rgba(78,140,133,0.1),transparent_24%),linear-gradient(180deg,rgba(8,16,26,0.98),rgba(6,11,18,0.98))] px-6 py-8 shadow-[0_40px_140px_rgba(0,0,0,0.52)] md:px-10 md:py-10">
        <div className="max-w-4xl">
          <div className="flex flex-wrap items-center gap-3">
            <span className="rounded-full border border-white/10 bg-black/10 px-3 py-1 text-xs uppercase tracking-[0.22em] text-slate-400">Simulated Scenario</span>
            <span className={`rounded-full border px-3 py-1 text-xs uppercase tracking-[0.22em] ${toneClasses[scenario.postureTone]}`}>{scenario.badge}</span>
          </div>
          <h1 className="mt-5 text-4xl font-semibold tracking-[-0.03em] text-slate-50 md:text-5xl">{scenario.title}</h1>
          <p className="mt-4 max-w-3xl text-base leading-8 text-slate-300">{scenario.summary}</p>
        </div>
      </header>

      <div className="grid gap-8 xl:grid-cols-[0.82fr_1.18fr]">
        <PublicSection eyebrow="Event Sequence" title="A readable path from household activity to system interpretation.">
          <div className="space-y-4">
            {scenario.sequence.map((step, stepIndex) => (
              <div key={step} className="relative rounded-2xl border border-white/8 bg-white/[0.03] px-4 py-4 transition duration-300 hover:border-white/12 hover:bg-white/[0.05]">
                {stepIndex < scenario.sequence.length - 1 ? <div className="absolute left-6 top-full h-4 w-px bg-gradient-to-b from-teal-200/35 to-transparent" /> : null}
                <p className="text-[0.7rem] uppercase tracking-[0.22em] text-teal-200/55">Step {stepIndex + 1}</p>
                <p className="mt-2 text-sm leading-6 text-slate-200">{step}</p>
              </div>
            ))}
          </div>
        </PublicSection>

        <div className="grid gap-4 md:grid-cols-2">
          <PublicSection eyebrow="Purpose" title={scenario.purpose} className="md:col-span-2" />
          <section className={`rounded-[28px] border p-5 shadow-[0_16px_50px_rgba(0,0,0,0.2)] ${toneClasses[scenario.postureTone]}`}>
            <p className="text-xs uppercase tracking-[0.24em] opacity-70">Threat Posture</p>
            <p className="mt-4 text-sm leading-7">{scenario.threatPosture}</p>
          </section>
          <PublicSection eyebrow="Response Recommendation" title={scenario.responseRecommendation} />
          <PublicSection eyebrow="Sentinel Core Interpretation" title={scenario.interpretation} className="md:col-span-2" />
          <PublicSection eyebrow="Narrative Explanation" title={scenario.narrativeExplanation} className="md:col-span-2" />
          <PublicSection eyebrow="What an Operator Would Review" className="md:col-span-2">
            <ul className="space-y-3 text-sm leading-6 text-slate-300">
              {scenario.operatorReview.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </PublicSection>
        </div>
      </div>

      <PublicCta
        eyebrow="Next Step"
        title="If this household story feels credible, the next step is a guided pilot discussion."
        body="Pilot walkthroughs review hardware fit, installation path, household topology, and whether this style of operational reasoning fits the home you have in mind."
        secondaryLabel="Back to Scenarios"
        secondaryHref="/public/scenarios"
      />
    </PublicShell>
  );
}
