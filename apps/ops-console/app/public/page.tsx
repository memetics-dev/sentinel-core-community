import Link from "next/link";

import { PublicCta } from "@/components/public/cta";
import { PublicSection } from "@/components/public/section";
import { PublicShell } from "@/components/public/shell";

const thinkingModel = [
  {
    title: "Presence",
    body: "Sentinel Core weighs trusted continuity and recent household presence before treating motion as automatically hostile.",
  },
  {
    title: "Rhythm",
    body: "It compares activity against what looks normal for the household and time of day, rather than assuming every signal means the same thing.",
  },
  {
    title: "Zones",
    body: "It understands that driveway, garage, hallway, kitchen, and bedroom do not carry the same meaning or sensitivity.",
  },
  {
    title: "Progression",
    body: "It looks for movement continuity across connected zones to distinguish isolated noise from believable intrusion patterns.",
  },
  {
    title: "Response Posture",
    body: "It stages operator posture from monitoring to active response, with explainable reasoning for escalation or suppression.",
  },
];

const designedFor = [
  "High-end residential environments",
  "Pilot households and controlled residential pilots",
  "Operationally disciplined in-home evaluations",
  "Privacy-focused users who prefer customer-owned edge hardware",
];

const gettingStarted = [
  "Review the installation path and compatible hardware expectations.",
  "Prepare a recommended local node and supported household sensors.",
  "Complete guided onboarding, pairing, and household validation.",
  "Run scenario validation before active residential pilot use.",
  "Begin a controlled pilot with local review and evidence discipline.",
];

const pilotSupport = [
  "Remote onboarding and installation guidance",
  "Guided setup for the initial pilot workflow",
  "Optional assisted installation or callout where appropriate",
];

export default function PublicPage() {
  return (
    <PublicShell>
      <header className="relative overflow-hidden rounded-[36px] border border-white/8 bg-[radial-gradient(circle_at_top_left,rgba(120,168,180,0.14),transparent_28%),radial-gradient(circle_at_80%_18%,rgba(103,170,160,0.12),transparent_24%),linear-gradient(180deg,rgba(8,16,26,0.98),rgba(6,11,18,0.98))] shadow-[0_40px_140px_rgba(0,0,0,0.52)]">
        <div className="absolute inset-0 bg-[linear-gradient(135deg,rgba(255,255,255,0.02),transparent_42%)]" />
        <div className="relative grid gap-8 px-6 py-8 md:px-10 md:py-12 xl:grid-cols-[1.15fr_0.85fr] xl:gap-10">
          <div className="max-w-4xl">
            <p className="text-[0.68rem] uppercase tracking-[0.38em] text-teal-200/55">Sentinel Core</p>
            <h1 className="mt-5 max-w-4xl text-4xl font-semibold tracking-[-0.03em] text-slate-50 md:text-5xl xl:text-6xl">
              A local-first household security intelligence system for privacy-focused early pilots.
            </h1>
            <p className="mt-5 max-w-2xl text-base leading-8 text-slate-300 md:text-lg">
              Sentinel Core is a self-hosted intelligence layer for the home. It reads household activity in context, explains why concern rises or falls, and helps an operator understand whether movement looks expected, ambiguous, or genuinely concerning.
            </p>
            <p className="mt-4 max-w-2xl text-sm leading-7 text-slate-400 md:text-base">
              It runs on customer-owned edge hardware, fits alongside existing household sensors, and is being prepared for controlled residential pilots with guided onboarding. This public surface shows simulated product experience only.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link href="/public/scenarios" className="rounded-full border border-teal-300/25 bg-teal-300/14 px-5 py-3 text-sm font-medium text-teal-50 transition duration-300 hover:-translate-y-px hover:bg-teal-300/20">
                Explore Scenarios
              </Link>
              <Link href="/public/installation" className="rounded-full border border-white/10 bg-white/[0.03] px-5 py-3 text-sm font-medium text-slate-200 transition duration-300 hover:-translate-y-px hover:border-white/18 hover:bg-white/[0.06]">
                Review Installation Path
              </Link>
              <Link href="/public/mobile-preview" className="rounded-full border border-white/10 bg-transparent px-5 py-3 text-sm font-medium text-slate-300 transition duration-300 hover:-translate-y-px hover:border-white/18 hover:text-slate-100">
                Preview Mobile Companion
              </Link>
              <Link href="/public/request-pilot" className="rounded-full border border-white/10 bg-transparent px-5 py-3 text-sm font-medium text-slate-300 transition duration-300 hover:-translate-y-px hover:border-white/18 hover:text-slate-100">
                Request Pilot Access
              </Link>
            </div>
          </div>

          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-1">
            <div className="rounded-[28px] border border-white/8 bg-[rgba(255,255,255,0.035)] p-5 shadow-[0_18px_60px_rgba(0,0,0,0.25)] backdrop-blur">
              <p className="text-xs uppercase tracking-[0.24em] text-slate-500">Public Demonstration Note</p>
              <p className="mt-4 text-sm leading-7 text-slate-300">
                Public pages use simulated scenario data and preview content only. No live household incidents, local Edge Core controls, or pilot evidence are exposed here.
              </p>
            </div>
            <div className="rounded-[28px] border border-white/8 bg-[rgba(255,255,255,0.03)] p-5 shadow-[0_18px_60px_rgba(0,0,0,0.25)]">
              <p className="text-xs uppercase tracking-[0.24em] text-slate-500">Why It Feels Different</p>
              <ul className="mt-4 space-y-3 text-sm leading-7 text-slate-300">
                <li>Reads household activity in context rather than as isolated alerts.</li>
                <li>Explains escalation and suppression with calm, deterministic reasoning.</li>
                <li>Built to reduce noise and improve operator confidence.</li>
              </ul>
            </div>
          </div>
        </div>
      </header>

      <div className="grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
        <PublicSection
          eyebrow="How Sentinel Core Thinks"
          title="It reads a household as a changing system, not a stream of disconnected alerts."
        >
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {thinkingModel.map((item, index) => (
              <article key={item.title} className="group rounded-[24px] border border-white/8 bg-[linear-gradient(180deg,rgba(255,255,255,0.04),rgba(255,255,255,0.02))] p-5 transition duration-300 hover:-translate-y-px hover:border-white/14">
                <p className="text-[0.7rem] uppercase tracking-[0.24em] text-teal-200/55">0{index + 1}</p>
                <p className="mt-4 text-lg font-medium text-slate-100">{item.title}</p>
                <p className="mt-3 text-sm leading-7 text-slate-400">{item.body}</p>
              </article>
            ))}
          </div>
        </PublicSection>

        <div className="grid gap-6">
          <PublicSection
            eyebrow="Why Local-First?"
            title="Operational privacy, resilience during internet disruption, and customer-owned intelligence."
          >
            <div className="space-y-4 text-sm leading-7 text-slate-300">
              <p>
                Sentinel Core is designed so household interpretation does not depend on cloud inference for the self-hosted pilot model described here.
              </p>
              <p>
                That local-first posture supports operational privacy, resilience when internet connectivity is disrupted, and customer-owned intelligence that remains grounded in the home it is observing.
              </p>
            </div>
          </PublicSection>

          <PublicSection eyebrow="Designed For" title="Who Sentinel Core is for right now.">
            <div className="grid gap-3 sm:grid-cols-2">
              {designedFor.map((item) => (
                <div key={item} className="rounded-2xl border border-white/8 bg-black/10 px-4 py-4 text-sm text-slate-200 transition duration-300 hover:border-white/14 hover:bg-white/[0.04]">
                  {item}
                </div>
              ))}
            </div>
          </PublicSection>
        </div>
      </div>

      <div className="grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
        <PublicSection
          eyebrow="Getting Started"
          title="A controlled self-hosted pilot begins with hardware, validation, and clear support boundaries."
        >
          <div className="space-y-3">
            {gettingStarted.map((item, index) => (
              <div key={item} className="rounded-2xl border border-white/8 bg-black/10 px-4 py-4 text-sm leading-7 text-slate-300 transition duration-300 hover:border-white/14 hover:bg-white/[0.04]">
                <span className="mr-3 text-[0.72rem] uppercase tracking-[0.22em] text-teal-200/55">0{index + 1}</span>
                {item}
              </div>
            ))}
          </div>
        </PublicSection>

        <div className="grid gap-6">
          <PublicSection eyebrow="Pilot Hardware" title="Recommended today for the curated path: NVIDIA Jetson Orin Nano.">
            <div className="space-y-4 text-sm leading-7 text-slate-300">
              <p>
                Sentinel Core is intended for customer-owned edge hardware. Jetson Orin Nano is the current recommended platform for local-first processing and future integration growth.
              </p>
              <p>
                Future compatible edge devices are possible, but the current guidance stays conservative and avoids promising universal compatibility.
              </p>
            </div>
          </PublicSection>

          <PublicSection eyebrow="Integration Philosophy" title="The intelligence layer stays local and deliberately bounded.">
            <div className="space-y-4 text-sm leading-7 text-slate-300">
              <p>
                Sentinel Core is positioned as the intelligence layer. Existing household sensors remain in place where useful, while Sentinel Core interprets what they mean together.
              </p>
              <p>
                A future Home Assistant pathway is planned as a local integration route, but current positioning remains careful and does not imply unsupported integration coverage.
              </p>
            </div>
          </PublicSection>
        </div>
      </div>

      <div className="grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
        <PublicSection eyebrow="Pilot Support" title="Early pilots remain guided, not fully unattended.">
          <div className="space-y-3">
            {pilotSupport.map((item) => (
              <div key={item} className="rounded-2xl border border-white/8 bg-black/10 px-4 py-4 text-sm leading-7 text-slate-300 transition duration-300 hover:border-white/14 hover:bg-white/[0.04]">
                {item}
              </div>
            ))}
          </div>
          <div className="mt-6 flex flex-wrap gap-3">
            <Link href="/public/installation" className="rounded-full border border-white/10 bg-white/[0.03] px-4 py-2 text-sm text-slate-200 transition duration-300 hover:-translate-y-px hover:border-white/18 hover:bg-white/[0.06]">
              Review Installation Path
            </Link>
            <Link href="/public/request-pilot" className="rounded-full border border-teal-300/25 bg-teal-300/14 px-4 py-2 text-sm text-teal-50 transition duration-300 hover:-translate-y-px hover:bg-teal-300/20">
              Request Pilot Access
            </Link>
          </div>
        </PublicSection>

        <PublicSection eyebrow="Self-Hosted Position" title="Local-first household intelligence with restrained claims and clear boundaries.">
          <div className="space-y-4 text-sm leading-7 text-slate-300">
            <p>
              Sentinel Core is intended for self-hosted pilot onboarding where the customer owns the local device, the household environment, and the operational evidence.
            </p>
            <p>
              It is not presented here as managed cloud hosting, mass-market consumer setup, or enterprise fleet deployment.
            </p>
          </div>
          <div className="mt-6 flex flex-wrap gap-3">
            <Link href="/public/scenarios" className="rounded-full border border-white/10 bg-white/[0.03] px-4 py-2 text-sm text-slate-200 transition duration-300 hover:-translate-y-px hover:border-white/18 hover:bg-white/[0.06]">
              Explore Simulated Scenarios
            </Link>
            <Link href="/public/market-readiness" className="rounded-full border border-white/10 bg-white/[0.03] px-4 py-2 text-sm text-slate-200 transition duration-300 hover:-translate-y-px hover:border-white/18 hover:bg-white/[0.06]">
              Review Market Readiness
            </Link>
          </div>
        </PublicSection>
      </div>

      <PublicCta
        eyebrow="Next Step"
        title="If the model fits your household and operating posture, the next conversation is a guided pilot review."
        body="Pilot onboarding reviews hardware fit, local network assumptions, installation path, validation discipline, and support boundaries before a controlled residential pilot begins."
        secondaryLabel="Review Installation Path"
        secondaryHref="/public/installation"
      />
    </PublicShell>
  );
}
