import type { PhaseStatus } from "@/lib/types";
import { Card } from "@/components/Card";

const PHASE_ICONS: Record<string, JSX.Element> = {
  research: (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
    </svg>
  ),
  planning: (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
    </svg>
  ),
  execution: (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
    </svg>
  ),
  review: (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
    </svg>
  ),
  testing: (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  ),
  deployment: (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
    </svg>
  ),
};

const PHASE_LABELS: Record<string, string> = {
  research: "Research",
  planning: "Planning",
  execution: "Execution",
  review: "Review",
  testing: "Testing",
  deployment: "Deployment",
};

const PHASE_DESCS: Record<string, string> = {
  research: "Gather technical context & approaches",
  planning: "Create detailed implementation plan",
  execution: "Write production-ready code",
  review: "Code quality & security audit",
  testing: "Run full test suite",
  deployment: "Commit, PR & deploy",
};

function RunningIndicator() {
  return (
    <span className="relative flex h-3 w-3">
      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75" />
      <span className="relative inline-flex rounded-full h-3 w-3 bg-blue-500" />
    </span>
  );
}

function CompletedIcon() {
  return (
    <svg className="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
    </svg>
  );
}

function FailedIcon() {
  return (
    <svg className="w-4 h-4 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
    </svg>
  );
}

function PhaseIcon({ name, status }: { name: string; status: string }) {
  if (status === "completed") return <CompletedIcon />;
  if (status === "failed") return <FailedIcon />;
  if (status === "running") return <RunningIndicator />;
  return PHASE_ICONS[name] || null;
}

function dotClass(status: string): string {
  switch (status) {
    case "running":
      return "bg-blue-500 ring-4 ring-blue-500/20";
    case "completed":
      return "bg-emerald-500";
    case "failed":
      return "bg-red-500";
    default:
      return "bg-zinc-700";
  }
}

function labelClass(status: string): string {
  switch (status) {
    case "running":
      return "text-blue-400";
    case "completed":
      return "text-emerald-400";
    case "failed":
      return "text-red-400";
    default:
      return "text-zinc-500";
  }
}

function bgClass(status: string): string {
  switch (status) {
    case "running":
      return "bg-blue-500/5 border-blue-500/20";
    case "completed":
      return "bg-emerald-500/5 border-emerald-500/20";
    case "failed":
      return "bg-red-500/5 border-red-500/20";
    default:
      return "bg-zinc-900 border-zinc-800";
  }
}

function duration(phase: PhaseStatus): string | null {
  if (!phase.started_at) return null;
  const start = new Date(phase.started_at).getTime();
  const end = phase.completed_at ? new Date(phase.completed_at).getTime() : Date.now();
  const sec = ((end - start) / 1000).toFixed(1);
  return `${sec}s`;
}

export function PhaseTimeline({ phases }: { phases: PhaseStatus[] }) {
  return (
    <div className="flex flex-col gap-3">
      {phases.map((phase, i) => (
        <div key={phase.name} className="relative">
          {/* Connector line */}
          {i < phases.length - 1 && (
            <div
              className={`absolute left-[15px] top-10 bottom-0 w-px ${
                phase.status === "completed" ? "bg-emerald-500/30" : "bg-zinc-800"
              }`}
            />
          )}

          <Card className={`border ${bgClass(phase.status)}`}>
            <div className="flex items-start gap-4 p-4">
              {/* Status indicator */}
              <div
                className={`flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center ${dotClass(
                  phase.status
                )}`}
              >
                <PhaseIcon name={phase.name} status={phase.status} />
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className={`text-sm font-semibold ${labelClass(phase.status)}`}>
                    {PHASE_LABELS[phase.name]}
                  </span>
                  {phase.status === "running" && (
                    <span className="text-xs text-blue-400/70 animate-pulse">running...</span>
                  )}
                  {(phase.status === "completed" || phase.status === "failed") && duration(phase) && (
                    <span className="text-xs text-zinc-600 font-mono">{duration(phase)}</span>
                  )}
                </div>
                <p className="text-xs text-zinc-500">{PHASE_DESCS[phase.name]}</p>
                {phase.status === "failed" && phase.output && (
                  <p className="mt-2 text-xs text-red-400/80 font-mono bg-red-500/10 rounded px-2 py-1.5 inline-block">
                    {phase.output}
                  </p>
                )}
              </div>

              {/* Status badge */}
              <div className="flex-shrink-0">
                {phase.status === "running" && (
                  <span className="inline-flex items-center gap-1.5 px-2 py-1 rounded-full bg-blue-500/10 text-blue-400 text-xs font-medium">
                    <span className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse" />
                    Active
                  </span>
                )}
                {phase.status === "completed" && (
                  <span className="inline-flex items-center gap-1.5 px-2 py-1 rounded-full bg-emerald-500/10 text-emerald-400 text-xs font-medium">
                    Done
                  </span>
                )}
                {phase.status === "failed" && (
                  <span className="inline-flex items-center gap-1.5 px-2 py-1 rounded-full bg-red-500/10 text-red-400 text-xs font-medium">
                    Failed
                  </span>
                )}
              </div>
            </div>
          </Card>
        </div>
      ))}
    </div>
  );
}
