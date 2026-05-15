import { ReactNode } from "react";

import { PublicFooter } from "@/components/public/footer";
import { PublicNav } from "@/components/public/nav";

type PublicShellProps = {
  children: ReactNode;
};

export function PublicShell({ children }: PublicShellProps) {
  return (
    <main className="min-h-screen bg-[#06070b] text-[#eef2ff]">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,_rgba(88,120,255,0.16),_transparent_34%),radial-gradient(circle_at_85%_18%,_rgba(85,198,170,0.12),_transparent_28%),linear-gradient(180deg,_rgba(8,10,18,0.96),_rgba(5,6,10,1))]" />
      <div className="relative mx-auto flex w-full max-w-[92rem] flex-col gap-6 px-5 py-6 md:px-8 md:py-8 lg:px-10">
        <PublicNav />
        {children}
        <PublicFooter />
      </div>
    </main>
  );
}
