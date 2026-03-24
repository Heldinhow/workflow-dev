import type { PhaseStatus } from "@/lib/types";

const ICONS: Record<string, string> = {
  research:   "⬡",
  planning:   "⬡",
  execution:  "⬡",
  review:     "⬡",
  testing:    "⬡",
  deployment: "⬡",
};

const PHASE_LABELS: Record<string, string> = {
  research:   "Research",
  planning:   "Planning",
  execution:  "Execution",
  review:     "Review",
  testing:    "Testing",
  deployment: "Deployment",
};

const PHASE_DESCS: Record<string, string> = {
  research:   "Gather technical context & approaches",
  planning:   "Create detailed implementation plan",
  execution:  "Write production-ready code",
  review:     "Code quality & security audit",
  testing:    "Run full test suite",
  deployment: "Commit, PR & deploy",
};

function dotClass(status: string): string {
  switch (status) {
    case "running":   return "bg-blue-400 pulse ring-2 ring-blue-400/30";
    case "completed": return "bg-emerald-400";
    case "failed":    return "bg-red-400";
    default:          return "bg-zinc-700";
  }
}

function labelClass(status: string): string {
  switch (status) {
    case "running":   return "text-blue-400";
    case "completed": return "text-emerald-400";
    case "failed":    return "text-red-400";
    default:          return "text-zinc-500";
  }
}

function duration(phase: PhaseStatus): string | null {
  if (!phase.started_at) return null;
  const start = new Date(phase.started_at).getTime();
  const end   = phase.completed_at ? new Date(phase.completed_at).getTime() : Date.now();
  const sec   = ((end - start) / 1000).toFixed(1);
  return `${sec}s`;
}

export function PhaseTimeline({ phases }: { phases: PhaseStatus[] }) {
  return (
    <div className="flex flex-col gap-0">
      {phases.map((phase, i) => (
        <div key={phase.name} className="relative flex gap-4 pb-6 last:pb-0">
          {/* Connector line */}
          {i < phases.length - 1 && (
            <div className="absolute left-[7px] top-5 bottom-0 w-px bg-zinc-800" />
          )}

          {/* Status dot */}
          <div className="relative z-10 mt-1 flex-shrink-0">
            <div className={`w-3.5 h-3.5 rounded-full ${dotClass(phase.status)}`} />
          </div>

          {/* Content */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-0.5">
              <span className={`text-sm font-medium ${labelClass(phase.status)}`}>
                {PHASE_LABELS[phase.name]}
              </span>
              {phase.status === "running" && (
                <span className="text-xs font-mono text-blue-400/70 animate-pulse">
                  running...
                </span>
              )}
              {(phase.status === "completed" || phase.status === "failed") && duration(phase) && (
                <span className="text-xs font-mono text-zinc-600">
                  {duration(phase)}
                </span>
              )}
            </div>
            <p className="text-xs text-zinc-600">{PHASE_DESCS[phase.name]}</p>
            {phase.status === "failed" && phase.output && (
              <p className="mt-1 text-xs text-red-400/80 font-mono truncate">
                {phase.output}
              </p>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
