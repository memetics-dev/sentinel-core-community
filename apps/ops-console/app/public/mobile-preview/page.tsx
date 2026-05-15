import { PublicCta } from "@/components/public/cta";
import { PublicSection } from "@/components/public/section";
import { PublicShell } from "@/components/public/shell";

const onboardingSteps = [
  {
    step: "01",
    title: "Discover the local node",
    detail: "Find the Sentinel Core node on the trusted household network and confirm that the companion is paired to the right home.",
  },
  {
    step: "02",
    title: "Pair supported devices",
    detail: "Guide the household through sensor pairing and optional trusted BLE identity setup without exposing internal system complexity.",
  },
  {
    step: "03",
    title: "Name zones and validate",
    detail: "Use household language for spaces such as Driveway, Garage, Hallway, Kitchen, and Bedroom, then run guided validation checks.",
  },
];

const statusCards = [
  {
    title: "Household Status",
    value: "Calm overnight posture",
    body: "Night Lock is active. No open incident. Trusted household context remains quiet.",
  },
  {
    title: "Current Narrative",
    value: "Household appears settled",
    body: "No unusual connected movement is active and no operator response is recommended.",
  },
  {
    title: "Response Guidance",
    value: "Monitor only",
    body: "No household action is recommended beyond normal awareness.",
  },
];

const notifications = [
  "Trusted occupant continuity observed before late-night kitchen activity.",
  "Unknown progression detected from driveway to garage. Review recommended.",
  "Household validation check completed successfully.",
];

const readinessChecks = [
  "Node discovered on the trusted local network",
  "Supported sensors paired to named zones",
  "Trusted identity continuity validated",
  "Quiet baseline and unknown progression scenarios reviewed",
];

const boundaries = [
  "Remote cloud surveillance",
  "Universal remote management",
  "Unsupported integrations",
  "Cloud AI dependence",
];

export default function PublicMobilePreviewPage() {
  return (
    <PublicShell>
      <header className="rounded-[36px] border border-white/8 bg-[radial-gradient(circle_at_top_left,rgba(113,159,174,0.12),transparent_28%),radial-gradient(circle_at_82%_20%,rgba(78,140,133,0.1),transparent_24%),linear-gradient(180deg,rgba(8,16,26,0.98),rgba(6,11,18,0.98))] px-6 py-8 shadow-[0_40px_140px_rgba(0,0,0,0.52)] md:px-10 md:py-10">
        <div className="max-w-4xl">
          <p className="text-[0.68rem] uppercase tracking-[0.36em] text-teal-200/60">Mobile Companion Preview</p>
          <h1 className="mt-4 text-4xl font-semibold tracking-[-0.03em] text-slate-50 md:text-5xl">
            A future mobile companion for onboarding, household review, and calm local visibility.
          </h1>
          <p className="mt-4 max-w-3xl text-base leading-8 text-slate-300">
            This preview shows how a Sentinel Core mobile companion could guide onboarding, show household status, surface narratives, and present notifications without becoming the intelligence engine. The experience uses static mock data only.
          </p>
        </div>
      </header>

      <div className="grid gap-6 lg:grid-cols-[1fr_1fr]">
        <PublicSection eyebrow="Why Local-First Mobile Matters" title="The companion makes local intelligence usable without relocating the intelligence itself.">
          <div className="space-y-4 text-sm leading-7 text-slate-300">
            <p>
              Sentinel Core reasoning remains on the household node. The companion simply makes onboarding, review, and notifications approachable for the people living in the home.
            </p>
            <p>
              That keeps operational privacy closer to the household, reduces dependence on cloud reachability, and preserves customer-controlled intelligence on the local node.
            </p>
          </div>
        </PublicSection>

        <PublicSection eyebrow="Household Privacy" title="The household node remains the source of truth.">
          <div className="space-y-4 text-sm leading-7 text-slate-300">
            <p>
              Intelligence, narratives, operational reasoning, and household state remain local to the node unless the household chooses to export evidence intentionally.
            </p>
            <p>
              The mobile companion is a local client for setup, review, and notifications rather than a remote surveillance control plane.
            </p>
          </div>
        </PublicSection>
      </div>

      <PublicSection eyebrow="Mobile Onboarding Flow" title="The companion helps the household move from node discovery to readiness validation.">
        <div className="grid gap-4 lg:grid-cols-3">
          {onboardingSteps.map((item) => (
            <article key={item.step} className="rounded-[1.5rem] border border-white/10 bg-[#0b1019]/94 p-5 shadow-[0_20px_50px_rgba(0,0,0,0.22)] transition duration-200 hover:border-white/16 hover:bg-[#0d1320]">
              <p className="text-xs uppercase tracking-[0.32em] text-[#8fa1df]">{item.step}</p>
              <h3 className="mt-3 text-lg font-semibold text-white">{item.title}</h3>
              <p className="mt-3 text-sm leading-7 text-[#b9c2e0]">{item.detail}</p>
            </article>
          ))}
        </div>
      </PublicSection>

      <div className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
        <PublicSection eyebrow="Companion Status Surface" title="Calm operational cards for the household, not an internal operator dashboard.">
          <div className="space-y-3">
            {statusCards.map((card) => (
              <div key={card.title} className="rounded-2xl border border-white/10 bg-[#0b1018]/92 p-4">
                <p className="text-xs uppercase tracking-[0.24em] text-slate-500">{card.title}</p>
                <h3 className="mt-2 text-lg font-semibold text-white">{card.value}</h3>
                <p className="mt-2 text-sm leading-7 text-slate-300">{card.body}</p>
              </div>
            ))}
          </div>
        </PublicSection>

        <div className="grid gap-6">
          <PublicSection eyebrow="Notifications" title="Meaningful household notifications rather than constant event mirroring.">
            <div className="space-y-3">
              {notifications.map((item) => (
                <div key={item} className="rounded-2xl border border-white/10 bg-[#0b1018]/92 p-4 text-sm leading-7 text-slate-300">
                  {item}
                </div>
              ))}
            </div>
          </PublicSection>

          <PublicSection eyebrow="Household Readiness" title="Validation should remain visible in the companion experience.">
            <div className="space-y-3">
              {readinessChecks.map((item) => (
                <div key={item} className="rounded-2xl border border-white/10 bg-[#0b1018]/92 p-4 text-sm leading-7 text-slate-300">
                  {item}
                </div>
              ))}
            </div>
          </PublicSection>
        </div>
      </div>

      <PublicSection eyebrow="Customer-Controlled Intelligence" title="The companion helps the household see and manage what the node is already reasoning about locally.">
        <div className="space-y-4 text-sm leading-7 text-slate-300">
          <p>
            The future companion should support onboarding, setup, scenario validation, notifications, and household review. It should not displace the local node or create a second independent reasoning layer.
          </p>
          <p>
            Its role is to make local-first operational reasoning understandable and approachable inside the home.
          </p>
        </div>
      </PublicSection>

      <PublicSection eyebrow="What the Mobile Companion Does Not Yet Do" title="The mobile companion remains deliberately bounded.">
        <div className="grid gap-4 lg:grid-cols-2">
          {boundaries.map((item) => (
            <div key={item} className="rounded-2xl border border-white/10 bg-[#0b1019]/94 p-5 text-sm leading-7 text-[#c0c9e8]">
              {item}
            </div>
          ))}
        </div>
      </PublicSection>

      <PublicCta
        eyebrow="Mobile Companion Direction"
        title="The future companion is intended to make local-first intelligence easier to onboard and easier to understand."
        body="It is designed as a guided household client for setup, review, and notifications, while the real intelligence, narratives, household state, and operational reasoning remain on the local Sentinel Core node."
        secondaryLabel="Preview Onboarding"
        secondaryHref="/public/onboarding-preview"
      />
    </PublicShell>
  );
}
