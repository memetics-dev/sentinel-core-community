import Link from "next/link";

import { PublicSection } from "@/components/public/section";
import { PublicShell } from "@/components/public/shell";
import { publicScenarios } from "@/lib/public-scenarios";

const toneClasses = {
  calm: "border-emerald-300/12 bg-emerald-300/[0.05] text-emerald-100",
  guarded: "border-teal-300/12 bg-teal-300/[0.05] text-teal-100",
  elevated: "border-amber-300/12 bg-amber-300/[0.05] text-amber-100",
  critical: "border-rose-300/12 bg-rose-300/[0.05] text-rose-100",
};

export default function PublicScenariosPage() {
  return (
    <PublicShell>
      <header className="rounded-[36px] border border-white/8 bg-[radial-gradient(circle_at_top_left,rgba(113,159,174,0.12),transparent_28%),radial-gradient(circle_at_82%_20%,rgba(78,140,133,0.1),transparent_24%),linear-gradient(180deg,rgba(8,16,26,0.98),rgba(6,11,18,0.98))] px-6 py-8 shadow-[0_40px_140px_rgba(0,0,0,0.52)] md:px-10 md:py-10">
        <div className="max-w-4xl">
          <p className="text-[0.68rem] uppercase tracking-[0.36em] text-teal-200/60">Simulated Scenario Experience</p>
          <h1 className="mt-4 text-4xl font-semibold tracking-[-0.03em] text-slate-50 md:text-5xl">
            See how Sentinel Core would explain a household situation before a live pilot discussion.
          </h1>
          <p className="mt-4 max-w-3xl text-base leading-8 text-slate-300">
            Each scenario uses static mock data to walk through the household story, the resulting posture, and what an operator would likely review next.
          </p>
        </div>
      </header>

      <PublicSection
        eyebrow="Scenario Library"
        title="Each tile opens a focused household story with posture, explanation, and review context."
        body="Public scenarios are static previews only. They do not expose live Edge Core incidents, trial evidence, or internal operator controls."
      >
        <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-5">
          {publicScenarios.map((scenario, index) => (
            <Link key={scenario.slug} href={`/public/scenarios/${scenario.slug}`} className="group rounded-[26px] border border-white/8 bg-white/[0.03] p-5 shadow-[0_20px_60px_rgba(0,0,0,0.25)] transition duration-300 hover:-translate-y-1 hover:border-white/14 hover:bg-white/[0.04]">
              <div className="flex items-start justify-between gap-4">
                <p className="text-[0.7rem] uppercase tracking-[0.24em] text-slate-500">Scenario {index + 1}</p>
                <span className={`rounded-full border px-3 py-1 text-[0.68rem] uppercase tracking-[0.18em] ${toneClasses[scenario.postureTone]}`}>
                  {scenario.badge}
                </span>
              </div>
              <p className="mt-4 text-lg font-medium text-slate-100">{scenario.title}</p>
              <p className="mt-3 text-sm leading-6 text-slate-400">{scenario.summary}</p>
              <p className="mt-5 text-sm font-medium text-slate-200 transition group-hover:text-white">Open scenario story</p>
            </Link>
          ))}
        </div>
      </PublicSection>
    </PublicShell>
  );
}
