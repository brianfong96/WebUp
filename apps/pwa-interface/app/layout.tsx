import "./globals.css";
import type { Metadata } from "next";
import { Nav } from "@/components/nav";

export const metadata: Metadata = {
  title: "WebUp Control Plane",
  description: "Agnostic data pipeline command center and observability viewer",
  manifest: "/manifest.json"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <main className="mx-auto min-h-screen max-w-6xl p-6">
          <header className="mb-6 flex flex-col gap-3 rounded-xl bg-gradient-to-r from-ink to-slate-800 p-4 text-white">
            <h1 className="text-2xl font-semibold">WebUp Pipeline</h1>
            <Nav />
          </header>
          {children}
        </main>
      </body>
    </html>
  );
}
