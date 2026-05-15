import type { Metadata } from "next";

import "./globals.css";

export const metadata: Metadata = {
  title: "Sentinel Core Community Preview",
  description: "Public Community Preview for Sentinel Core local-first residential intelligence.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
