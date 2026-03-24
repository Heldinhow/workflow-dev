import type { Status } from "@/lib/types";

const CONFIG: Record<Status, { dot: string; text: string; label: string }> = {
  pending:   { dot: "bg-zinc-600",   text: "text-zinc-400",   label: "Pending"   },
  running:   { dot: "bg-blue-400",   text: "text-blue-400",   label: "Running"   },
  completed: { dot: "bg-emerald-400",text: "text-emerald-400",label: "Completed" },
  failed:    { dot: "bg-red-400",    text: "text-red-400",    label: "Failed"    },
  escalated: { dot: "bg-amber-400",  text: "text-amber-400",  label: "Escalated" },
};

export function StatusBadge({ status }: { status: Status }) {
  const c = CONFIG[status];
  return (
    <span className={`inline-flex items-center gap-1.5 text-xs font-mono ${c.text}`}>
      <span
        className={`w-1.5 h-1.5 rounded-full ${c.dot} ${status === "running" ? "pulse" : ""}`}
      />
      {c.label}
    </span>
  );
}
