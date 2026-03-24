import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "Dev Workflow",
  description: "AI-powered automated development workflow",
};

function GithubIcon() {
  return (
    <svg
      className="w-5 h-5"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.5}
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22" />
    </svg>
  );
}

function TwitterIcon() {
  return (
    <svg
      className="w-4 h-4"
      viewBox="0 0 24 24"
      fill="currentColor"
    >
      <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
    </svg>
  );
}

function NavLink({ href, children }: { href: string; children: React.ReactNode }) {
  return (
    <Link
      href={href}
      className="text-sm text-zinc-400 hover:text-zinc-100 transition-colors duration-150"
    >
      {children}
    </Link>
  );
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-zinc-950 text-zinc-100 antialiased">
        {/* Header */}
        <header className="sticky top-0 z-50 glass border-b border-zinc-800/50">
          <div className="max-w-7xl mx-auto px-6 h-14 flex items-center justify-between">
            {/* Logo */}
            <div className="flex items-center gap-3">
              <Link href="/" className="flex items-center gap-2.5 group">
                <div className="relative">
                  <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-indigo-600 flex items-center justify-center shadow-glow-sm group-hover:shadow-glow transition-shadow duration-200">
                    <span className="text-white font-bold text-sm">D</span>
                  </div>
                  <div className="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full bg-emerald-500 border-2 border-zinc-950" />
                </div>
                <div className="flex items-baseline gap-1">
                  <span className="text-sm font-semibold text-zinc-100 tracking-tight">
                    dev<span className="text-zinc-500">/</span>workflow
                  </span>
                </div>
              </Link>
              
              {/* Status indicator */}
              <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-zinc-900/80 border border-zinc-800">
                <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                <span className="text-xs text-zinc-500 font-medium">Active</span>
              </div>
            </div>

            {/* Navigation */}
            <nav className="hidden md:flex items-center gap-6">
              <NavLink href="/">Dashboard</NavLink>
              <NavLink href="/executions">Executions</NavLink>
              <NavLink href="/docs">Docs</NavLink>
              <NavLink href="/pricing">Pricing</NavLink>
            </nav>

            {/* Actions */}
            <div className="flex items-center gap-3">
              {/* Social links */}
              <div className="hidden sm:flex items-center gap-2">
                <a
                  href="https://github.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="p-2 text-zinc-500 hover:text-zinc-300 transition-colors duration-150"
                  aria-label="GitHub"
                >
                  <GithubIcon />
                </a>
                <a
                  href="https://twitter.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="p-2 text-zinc-500 hover:text-zinc-300 transition-colors duration-150"
                  aria-label="Twitter"
                >
                  <TwitterIcon />
                </a>
              </div>

              {/* Divider */}
              <div className="hidden sm:block w-px h-5 bg-zinc-800" />

              {/* CTA Button */}
              <Link
                href="/executions/new"
                className="inline-flex items-center gap-2 px-4 py-1.5 text-sm font-medium bg-indigo-500 text-white rounded-lg hover:bg-indigo-400 transition-all duration-150 hover:shadow-glow"
              >
                <span>New Execution</span>
                <svg
                  className="w-4 h-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M13 7l5 5m0 0l-5 5m5-5H6"
                  />
                </svg>
              </Link>
            </div>
          </div>
        </header>

        {/* Main content */}
        <main className="max-w-7xl mx-auto px-6 py-8">
          {children}
        </main>

        {/* Footer */}
        <footer className="border-t border-zinc-800/50 mt-auto">
          <div className="max-w-7xl mx-auto px-6 py-8">
            <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
              <div className="flex items-center gap-2 text-sm text-zinc-500">
                <span>Powered by</span>
                <span className="text-zinc-400 font-medium">MiniMax + CrewAI</span>
              </div>
              <div className="flex items-center gap-6 text-sm text-zinc-500">
                <a href="#" className="hover:text-zinc-300 transition-colors">Documentation</a>
                <a href="#" className="hover:text-zinc-300 transition-colors">Privacy</a>
                <a href="#" className="hover:text-zinc-300 transition-colors">Terms</a>
              </div>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
