import type { Status } from "@/lib/types";

const CONFIG: Record<Status, { bg: string; text: string; ring: string; label: string }> = {
  pending: {
    bg: "bg-zinc-800/50",
    text: "text-zinc-400",
    ring: "",
    label: "Pending"
  },
  running: {
    bg: "bg-blue-500/10",
    text: "text-blue-400",
    ring: "ring-1 ring-blue-500/20",
    label: "Running"
  },
  completed: {
    bg: "bg-emerald-500/10",
    text: "text-emerald-400",
    ring: "ring-1 ring-emerald-500/20",
    label: "Completed"
  },
  failed: {
    bg: "bg-red-500/10",
    text: "text-red-400",
    ring: "ring-1 ring-red-500/20",
    label: "Failed"
  },
  escalated: {
    bg: "bg-amber-500/10",
    text: "text-amber-400",
    ring: "ring-1 ring-amber-500/20",
    label: "Escalated"
  },
};

function RunningDot() {
  return (
    <span className="relative flex h-2 w-2">
      <span className={`animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75`} />
      <span className={`relative inline-flex rounded-full h-2 w-2 bg-blue-500`} />
    </span>
  );
}

export function StatusBadge({ status, size = "default" }: { status: Status; size?: "default" | "large" }) {
  const c = CONFIG[status];
  const isLarge = size === "large";
  
  return (
    <span
      className={`inline-flex items-center gap-1.5 ${c.bg} ${c.text} ${c.ring} rounded-full font-medium ${
        isLarge ? "px-3 py-1.5 text-sm" : "px-2.5 py-1 text-xs"
      }`}
    >
      {status === "running" ? (
        <RunningDot />
      ) : (
        <span
          className={`rounded-full ${status === "pending" ? "bg-zinc-600" : ""} ${
            status === "completed" ? "bg-emerald-500" : ""
          } ${status === "failed" ? "bg-red-500" : ""} ${status === "escalated" ? "bg-amber-500" : ""} w-1.5 h-1.5`}
        />
      )}
      {c.label}
    </span>
  );
}
