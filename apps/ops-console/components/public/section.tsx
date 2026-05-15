import { ReactNode } from "react";

type PublicSectionProps = {
  eyebrow?: string;
  title?: string;
  body?: string;
  children?: ReactNode;
  className?: string;
};

export function PublicSection({ eyebrow, title, body, children, className = "" }: PublicSectionProps) {
  return (
    <section className={`rounded-[2rem] border border-white/10 bg-white/[0.04] px-6 py-8 shadow-[0_28px_90px_rgba(0,0,0,0.28)] backdrop-blur-xl md:px-8 ${className}`.trim()}>
      {eyebrow || title || body ? (
        <div className="max-w-3xl space-y-3">
          {eyebrow ? <p className="text-xs uppercase tracking-[0.28em] text-slate-500">{eyebrow}</p> : null}
          {title ? <h2 className="text-3xl font-semibold tracking-tight text-slate-50">{title}</h2> : null}
          {body ? <p className="text-sm leading-7 text-slate-300">{body}</p> : null}
        </div>
      ) : null}
      {children ? <div className={eyebrow || title || body ? "mt-6" : ""}>{children}</div> : null}
    </section>
  );
}
