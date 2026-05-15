import Link from "next/link";

export function PublicFooter() {
  return (
    <footer className="mx-auto mt-6 w-full max-w-7xl rounded-[2rem] border border-white/10 bg-white/[0.04] px-6 py-8 shadow-[0_20px_70px_rgba(0,0,0,0.28)] backdrop-blur-xl sm:px-8">
      <div className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr] lg:items-end">
        <div className="space-y-4">
          <p className="text-xs uppercase tracking-[0.28em] text-slate-500">Public Experience Boundary</p>
          <p className="max-w-3xl text-sm leading-7 text-slate-300">
            Public routes use simulated scenario data and preview content only. They do not expose live household incidents, local control surfaces, or real Sentinel Core trial evidence.
          </p>
          <p className="max-w-3xl text-sm leading-7 text-slate-400">
            Sentinel Core is positioned here as local-first household intelligence for controlled residential pilots on customer-owned edge hardware.
          </p>
        </div>
        <div className="flex flex-wrap gap-3 lg:justify-end">
          <Link
            href="/public/request-pilot"
            className="rounded-full border border-teal-300/25 bg-teal-300/14 px-5 py-3 text-sm font-medium text-teal-50 transition duration-300 hover:-translate-y-px hover:bg-teal-300/20"
          >
            Request Pilot Access
          </Link>
          <Link
            href="/public/scenarios"
            className="rounded-full border border-white/10 bg-white/[0.03] px-5 py-3 text-sm text-slate-200 transition duration-300 hover:-translate-y-px hover:border-white/18 hover:bg-white/[0.06]"
          >
            Explore Scenarios
          </Link>
        </div>
      </div>
    </footer>
  );
}
