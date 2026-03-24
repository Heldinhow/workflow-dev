import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Dev Workflow",
  description: "AI-powered automated development workflow",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-zinc-950 text-zinc-100">
        <header className="border-b border-zinc-800 bg-zinc-950 sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-6 h-12 flex items-center gap-3">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-emerald-400" />
              <span className="text-sm font-medium text-zinc-100 tracking-tight">
                dev<span className="text-zinc-500">/</span>workflow
              </span>
            </div>
            <span className="text-zinc-700 text-xs font-mono">
              powered by MiniMax + CrewAI
            </span>
          </div>
        </header>
        <main className="max-w-7xl mx-auto px-6 py-8">
          {children}
        </main>
      </body>
    </html>
  );
}
