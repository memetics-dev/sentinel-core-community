import Link from "next/link";

type PublicCtaProps = {
  eyebrow: string;
  title: string;
  body: string;
  primaryLabel?: string;
  primaryHref?: string;
  secondaryLabel?: string;
  secondaryHref?: string;
};

export function PublicCta({
  eyebrow,
  title,
  body,
  primaryLabel = "Request Pilot Access",
  primaryHref = "/public/request-pilot",
  secondaryLabel = "Explore Scenarios",
  secondaryHref = "/public/scenarios",
}: PublicCtaProps) {
  return (
    <section className="rounded-[2rem] border border-white/10 bg-[linear-gradient(180deg,rgba(18,29,42,0.8),rgba(8,16,25,0.78))] px-6 py-8 shadow-[0_28px_90px_rgba(0,0,0,0.28)] md:px-8">
      <div className="max-w-3xl space-y-4">
        <p className="text-xs uppercase tracking-[0.28em] text-slate-500">{eyebrow}</p>
        <h2 className="text-3xl font-semibold tracking-tight text-slate-50">{title}</h2>
        <p className="text-sm leading-7 text-slate-300">{body}</p>
      </div>
      <div className="mt-6 flex flex-wrap gap-3">
        <Link
          href={primaryHref}
          className="rounded-full border border-teal-300/25 bg-teal-300/14 px-5 py-3 text-sm font-medium text-teal-50 transition duration-300 hover:-translate-y-px hover:bg-teal-300/20"
        >
          {primaryLabel}
        </Link>
        <Link
          href={secondaryHref}
          className="rounded-full border border-white/10 bg-white/[0.03] px-5 py-3 text-sm text-slate-200 transition duration-300 hover:-translate-y-px hover:border-white/18 hover:bg-white/[0.06]"
        >
          {secondaryLabel}
        </Link>
      </div>
    </section>
  );
}
