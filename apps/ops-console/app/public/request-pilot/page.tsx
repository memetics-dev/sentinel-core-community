"use client";

import Link from "next/link";
import { useState } from "react";

import { PublicSection } from "@/components/public/section";
import { PublicShell } from "@/components/public/shell";

type InterestType = "self-hosted pilot" | "assisted installation" | "walkthrough only";

type FormState = {
  name: string;
  email: string;
  location: string;
  securitySetup: string;
  homeAssistant: string;
  edgeHardware: string;
  interestType: InterestType;
  message: string;
};

const initialState: FormState = {
  name: "",
  email: "",
  location: "",
  securitySetup: "",
  homeAssistant: "No / not yet",
  edgeHardware: "Yes, willing to use customer-owned edge hardware",
  interestType: "self-hosted pilot",
  message: "",
};

export default function RequestPilotPage() {
  const [form, setForm] = useState<FormState>(initialState);
  const [submitted, setSubmitted] = useState(false);

  const handleChange = <K extends keyof FormState>(key: K, value: FormState[K]) => {
    setForm((current) => ({ ...current, [key]: value }));
  };

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setSubmitted(true);
  };

  const mailtoHref = `mailto:hello@sentinelcore.ai?subject=${encodeURIComponent(
    `Sentinel Core pilot request - ${form.name || "prospective pilot"}`,
  )}&body=${encodeURIComponent(
    [
      `Name: ${form.name}`,
      `Email: ${form.email}`,
      `Location / city: ${form.location}`,
      `Current security setup: ${form.securitySetup}`,
      `Home Assistant or similar: ${form.homeAssistant}`,
      `Customer-owned edge hardware: ${form.edgeHardware}`,
      `Interest type: ${form.interestType}`,
      `Short message: ${form.message}`,
    ].join("\n"),
  )}`;

  return (
    <PublicShell>
      <header className="rounded-[36px] border border-white/8 bg-[radial-gradient(circle_at_top_left,rgba(120,168,180,0.14),transparent_28%),radial-gradient(circle_at_80%_18%,rgba(103,170,160,0.12),transparent_24%),linear-gradient(180deg,rgba(8,16,26,0.98),rgba(6,11,18,0.98))] px-6 py-8 shadow-[0_40px_140px_rgba(0,0,0,0.52)] md:px-10 md:py-10">
        <div className="max-w-4xl">
          <p className="text-[0.68rem] uppercase tracking-[0.36em] text-teal-200/60">Request Pilot Access</p>
          <h1 className="mt-4 text-4xl font-semibold tracking-[-0.03em] text-slate-50 md:text-5xl">
            Request a guided conversation about whether Sentinel Core is a fit for your home.
          </h1>
          <p className="mt-4 max-w-3xl text-base leading-8 text-slate-300">
            Sentinel Core is currently preparing controlled self-hosted pilots. We review hardware fit, household setup, and support boundaries before onboarding, and the public scenarios shown here use simulated data only.
          </p>
        </div>
      </header>

      <div className="grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
        <PublicSection eyebrow="Pilot Interest Form" title="Share a few practical details so we can judge whether a pilot is appropriate.">
          <p className="max-w-2xl text-sm leading-7 text-slate-400">
            This form is currently a local placeholder. It does not submit anywhere yet, but it mirrors the information needed to assess household fit, hardware expectations, and pilot readiness.
          </p>

          {submitted ? (
            <div className="mt-8 rounded-[28px] border border-teal-300/14 bg-teal-300/[0.06] p-5 text-sm leading-7 text-slate-200">
              <p className="text-sm font-medium text-slate-50">Pilot request captured locally.</p>
              <p className="mt-3">
                This confirmation is local only. Sentinel Core is currently preparing controlled self-hosted pilots, and hardware compatibility is assessed before onboarding.
              </p>
              <p className="mt-3">If you want to send this request now, use the mail fallback below and we can continue the conversation manually.</p>
              <div className="mt-5 flex flex-wrap gap-3">
                <a href={mailtoHref} className="rounded-full border border-white/10 bg-white/[0.03] px-4 py-2 text-sm text-slate-100 transition duration-300 hover:-translate-y-px hover:border-white/18 hover:bg-white/[0.06]">
                  Open Mail Draft
                </a>
                <button type="button" onClick={() => setSubmitted(false)} className="rounded-full border border-white/10 bg-transparent px-4 py-2 text-sm text-slate-300 transition duration-300 hover:-translate-y-px hover:border-white/18 hover:text-slate-100">
                  Edit Request
                </button>
              </div>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="mt-8 grid gap-4">
              <div className="grid gap-4 md:grid-cols-2">
                <label className="grid gap-2 text-sm text-slate-300">
                  <span>Name</span>
                  <input value={form.name} onChange={(event) => handleChange("name", event.target.value)} className="rounded-2xl border border-white/10 bg-black/10 px-4 py-3 text-slate-100 outline-none transition focus:border-white/18" />
                </label>
                <label className="grid gap-2 text-sm text-slate-300">
                  <span>Email</span>
                  <input type="email" value={form.email} onChange={(event) => handleChange("email", event.target.value)} className="rounded-2xl border border-white/10 bg-black/10 px-4 py-3 text-slate-100 outline-none transition focus:border-white/18" />
                </label>
              </div>
              <label className="grid gap-2 text-sm text-slate-300">
                <span>Location / city</span>
                <input value={form.location} onChange={(event) => handleChange("location", event.target.value)} className="rounded-2xl border border-white/10 bg-black/10 px-4 py-3 text-slate-100 outline-none transition focus:border-white/18" />
              </label>
              <label className="grid gap-2 text-sm text-slate-300">
                <span>Current security setup</span>
                <textarea rows={3} value={form.securitySetup} onChange={(event) => handleChange("securitySetup", event.target.value)} className="rounded-2xl border border-white/10 bg-black/10 px-4 py-3 text-slate-100 outline-none transition focus:border-white/18" placeholder="Existing sensors, alarm panel, cameras, automation, or monitoring context." />
              </label>
              <div className="grid gap-4 md:grid-cols-2">
                <label className="grid gap-2 text-sm text-slate-300">
                  <span>Home Assistant or similar</span>
                  <select value={form.homeAssistant} onChange={(event) => handleChange("homeAssistant", event.target.value)} className="rounded-2xl border border-white/10 bg-black/10 px-4 py-3 text-slate-100 outline-none transition focus:border-white/18">
                    <option>No / not yet</option>
                    <option>Yes, Home Assistant</option>
                    <option>Yes, another local platform</option>
                    <option>Unsure</option>
                  </select>
                </label>
                <label className="grid gap-2 text-sm text-slate-300">
                  <span>Customer-owned edge hardware</span>
                  <select value={form.edgeHardware} onChange={(event) => handleChange("edgeHardware", event.target.value)} className="rounded-2xl border border-white/10 bg-black/10 px-4 py-3 text-slate-100 outline-none transition focus:border-white/18">
                    <option>Yes, willing to use customer-owned edge hardware</option>
                    <option>Maybe, subject to compatibility review</option>
                    <option>No, not at this stage</option>
                  </select>
                </label>
              </div>
              <label className="grid gap-2 text-sm text-slate-300">
                <span>Interest type</span>
                <select value={form.interestType} onChange={(event) => handleChange("interestType", event.target.value as InterestType)} className="rounded-2xl border border-white/10 bg-black/10 px-4 py-3 text-slate-100 outline-none transition focus:border-white/18">
                  <option>self-hosted pilot</option>
                  <option>assisted installation</option>
                  <option>walkthrough only</option>
                </select>
              </label>
              <label className="grid gap-2 text-sm text-slate-300">
                <span>Short message</span>
                <textarea rows={4} value={form.message} onChange={(event) => handleChange("message", event.target.value)} className="rounded-2xl border border-white/10 bg-black/10 px-4 py-3 text-slate-100 outline-none transition focus:border-white/18" placeholder="Tell us about the household, the pilot interest, or the kind of walkthrough you want." />
              </label>
              <div className="flex flex-wrap gap-3 pt-2">
                <button type="submit" className="rounded-full border border-teal-300/25 bg-teal-300/14 px-5 py-3 text-sm font-medium text-teal-50 transition duration-300 hover:-translate-y-px hover:bg-teal-300/20">
                  Request Pilot Access
                </button>
                <a href={mailtoHref} className="rounded-full border border-white/10 bg-white/[0.03] px-5 py-3 text-sm font-medium text-slate-200 transition duration-300 hover:-translate-y-px hover:border-white/18 hover:bg-white/[0.06]">
                  Use Mail Fallback
                </a>
              </div>
            </form>
          )}
        </PublicSection>

        <div className="grid gap-6">
          <PublicSection eyebrow="Pilot Positioning" title="A local-first household intelligence system for carefully guided early customers.">
            <div className="space-y-4 text-sm leading-7 text-slate-300">
              <p>
                Sentinel Core is currently preparing controlled self-hosted pilots. Hardware compatibility is assessed before onboarding.
              </p>
              <p>
                Public scenarios use simulated data. The live trial environment remains separate from this public request flow.
              </p>
            </div>
          </PublicSection>

          <PublicSection eyebrow="Before Onboarding" title="What to expect before a pilot begins.">
            <ul className="space-y-3 text-sm leading-7 text-slate-300">
              <li>Compatible hardware is reviewed before a pilot begins.</li>
              <li>Self-hosted expectations and support boundaries are confirmed early.</li>
              <li>Existing household systems are discussed before any integration path is suggested.</li>
              <li>Scenario validation remains part of every controlled pilot onboarding path.</li>
            </ul>
          </PublicSection>
        </div>
      </div>
    </PublicShell>
  );
}
