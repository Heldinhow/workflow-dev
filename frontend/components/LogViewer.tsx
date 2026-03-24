"use client";
import { useEffect, useRef } from "react";
import type { WorkflowEvent } from "@/lib/types";

const EVENT_COLORS: Record<string, string> = {
  execution_started:   "text-zinc-500",
  phase_started:       "text-blue-400",
  phase_completed:     "text-emerald-400",
  phase_failed:        "text-red-400",
  retry:               "text-amber-400",
  test_retry:          "text-amber-400",
  agent_step:          "text-zinc-400",
  execution_completed: "text-emerald-300",
  execution_escalated: "text-amber-300",
  execution_failed:    "text-red-300",
  stream_end:          "text-zinc-600",
};

const PHASE_PREFIXES: Record<string, string> = {
  research:   "[research]  ",
  planning:   "[planning]  ",
  execution:  "[executor]  ",
  review:     "[reviewer]  ",
  testing:    "[tester]    ",
  deployment: "[deployer]  ",
  "":         "[workflow]  ",
};

function ts(timestamp: string): string {
  return new Date(timestamp).toLocaleTimeString("en", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  });
}

export function LogViewer({ events, autoScroll = true }: {
  events: WorkflowEvent[];
  autoScroll?: boolean;
}) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (autoScroll && bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [events, autoScroll]);

  return (
    <div className="h-full overflow-y-auto bg-zinc-950 border border-zinc-800 rounded font-mono text-xs log-scroll">
      {/* Terminal header */}
      <div className="sticky top-0 flex items-center gap-1.5 px-3 py-2 border-b border-zinc-800 bg-zinc-900">
        <span className="w-2.5 h-2.5 rounded-full bg-red-500/60" />
        <span className="w-2.5 h-2.5 rounded-full bg-amber-500/60" />
        <span className="w-2.5 h-2.5 rounded-full bg-emerald-500/60" />
        <span className="ml-2 text-zinc-500 text-xs">execution log</span>
      </div>

      <div className="p-3 space-y-0.5">
        {events.length === 0 && (
          <span className="text-zinc-700">Waiting for events...</span>
        )}
        {events.map((ev, i) => {
          const color  = EVENT_COLORS[ev.type] ?? "text-zinc-400";
          const prefix = PHASE_PREFIXES[ev.phase] ?? "[workflow]  ";
          return (
            <div key={i} className="flex gap-2 leading-5">
              <span className="text-zinc-700 flex-shrink-0 select-none">
                {ts(ev.timestamp)}
              </span>
              <span className={`flex-shrink-0 select-none ${
                ev.phase === "execution"  ? "text-blue-500/70"   :
                ev.phase === "review"     ? "text-violet-500/70" :
                ev.phase === "testing"    ? "text-cyan-500/70"   :
                ev.phase === "deployment" ? "text-emerald-500/70":
                "text-zinc-600"
              }`}>
                {prefix}
              </span>
              <span className={color}>{ev.message}</span>
            </div>
          );
        })}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
