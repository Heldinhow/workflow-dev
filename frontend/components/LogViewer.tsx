"use client";

import { useEffect, useRef, useState } from "react";
import type { WorkflowEvent } from "@/lib/types";
import { Card } from "@/components/Card";

const EVENT_COLORS: Record<string, string> = {
  execution_started: "text-zinc-400",
  phase_started: "text-blue-400",
  phase_completed: "text-emerald-400",
  phase_failed: "text-red-400",
  retry: "text-amber-400",
  test_retry: "text-amber-400",
  agent_step: "text-zinc-400",
  execution_completed: "text-emerald-300",
  execution_escalated: "text-amber-300",
  execution_failed: "text-red-300",
  stream_end: "text-zinc-600",
};

const PHASE_COLORS: Record<string, string> = {
  research: "text-violet-400",
  planning: "text-blue-400",
  execution: "text-emerald-400",
  review: "text-amber-400",
  testing: "text-cyan-400",
  deployment: "text-pink-400",
};

const PHASE_LABELS: Record<string, string> = {
  research: "RES",
  planning: "PLN",
  execution: "EXE",
  review: "REV",
  testing: "TST",
  deployment: "DPL",
  "": "LOG",
};

const ALL_PHASES = [
  { id: "research", label: "Research" },
  { id: "planning", label: "Planning" },
  { id: "execution", label: "Execution" },
  { id: "review", label: "Review" },
  { id: "testing", label: "Testing" },
  { id: "deployment", label: "Deployment" },
];

function ts(timestamp: string): string {
  return new Date(timestamp).toLocaleTimeString("en", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  });
}

function EventIcon({ type, phase }: { type: string; phase: string }) {
  if (type === "phase_started" || type === "execution_started") {
    return (
      <span className="w-5 h-5 rounded-full bg-blue-500/20 flex items-center justify-center flex-shrink-0">
        <span className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-pulse" />
      </span>
    );
  }
  if (type === "phase_completed" || type === "execution_completed") {
    return (
      <span className="w-5 h-5 rounded-full bg-emerald-500/20 flex items-center justify-center flex-shrink-0">
        <svg className="w-3 h-3 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
        </svg>
      </span>
    );
  }
  if (type === "phase_failed" || type === "execution_failed") {
    return (
      <span className="w-5 h-5 rounded-full bg-red-500/20 flex items-center justify-center flex-shrink-0">
        <svg className="w-3 h-3 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M6 18L18 6M6 6l12 12" />
        </svg>
      </span>
    );
  }
  if (type === "retry" || type === "test_retry") {
    return (
      <span className="w-5 h-5 rounded-full bg-amber-500/20 flex items-center justify-center flex-shrink-0">
        <svg className="w-3 h-3 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
      </span>
    );
  }
  return (
    <span className="w-5 h-5 rounded-full bg-zinc-800 flex items-center justify-center flex-shrink-0">
      <span className="w-1 h-1 rounded-full bg-zinc-500" />
    </span>
  );
}

export function LogViewer({ events, autoScroll = true, selectedPhases, onPhasesChange }: {
  events: WorkflowEvent[];
  autoScroll?: boolean;
  selectedPhases?: string[];
  onPhasesChange?: (phases: string[]) => void;
}) {
  const bottomRef = useRef<HTMLDivElement>(null);
  const [localSelectedPhases, setLocalSelectedPhases] = useState<string[]>(selectedPhases || []);

  useEffect(() => {
    if (autoScroll && bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [events, autoScroll]);

  const activePhases = selectedPhases !== undefined ? selectedPhases : localSelectedPhases;

  const togglePhase = (phaseId: string) => {
    const newPhases = activePhases.includes(phaseId)
      ? activePhases.filter((p) => p !== phaseId)
      : [...activePhases, phaseId];
    
    if (selectedPhases !== undefined) {
      onPhasesChange?.(newPhases);
    } else {
      setLocalSelectedPhases(newPhases);
    }
  };

  const filteredEvents = activePhases.length === 0
    ? events
    : events.filter((ev) => activePhases.includes(ev.phase));

  return (
    <Card padding="none" className="overflow-hidden">
      {/* Terminal header */}
      <div className="flex flex-col gap-3 px-4 py-3 border-b border-zinc-800 bg-zinc-900/50">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded-full bg-red-500/60" />
              <span className="w-3 h-3 rounded-full bg-amber-500/60" />
              <span className="w-3 h-3 rounded-full bg-emerald-500/60" />
            </div>
            <span className="ml-2 text-xs text-zinc-500 font-medium uppercase tracking-wider">
              Execution Log
            </span>
          </div>
          <span className="text-xs text-zinc-600 font-mono">
            {filteredEvents.length} / {events.length} events
          </span>
        </div>
        {/* Phase filter chips */}
        <div className="flex flex-wrap gap-1.5">
          {ALL_PHASES.map((phase) => {
            const isActive = activePhases.includes(phase.id);
            const phaseColor = PHASE_COLORS[phase.id] || "text-zinc-400";
            return (
              <button
                key={phase.id}
                onClick={() => togglePhase(phase.id)}
                className={`px-2 py-0.5 text-xs rounded-full border transition-colors ${
                  isActive
                    ? `${phaseColor} border-current bg-current/10`
                    : "text-zinc-500 border-zinc-700 hover:border-zinc-600"
                }`}
              >
                {phase.label}
              </button>
            );
          })}
          {activePhases.length > 0 && (
            <button
              onClick={() => {
                if (selectedPhases !== undefined) {
                  onPhasesChange?.([]);
                } else {
                  setLocalSelectedPhases([]);
                }
              }}
              className="px-2 py-0.5 text-xs rounded-full border border-zinc-700 text-zinc-500 hover:border-zinc-600 transition-colors"
            >
              Clear
            </button>
          )}
        </div>
      </div>

      {/* Log content */}
      <div className="h-[500px] overflow-y-auto bg-zinc-950 font-mono text-xs log-scroll">
        <div className="p-4 space-y-1">
          {filteredEvents.length === 0 && events.length > 0 && (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <p className="text-zinc-500 text-sm">No events match the selected filters</p>
              <button
                onClick={() => {
                  if (selectedPhases !== undefined) {
                    onPhasesChange?.([]);
                  } else {
                    setLocalSelectedPhases([]);
                  }
                }}
                className="mt-2 text-xs text-indigo-400 hover:text-indigo-300"
              >
                Clear filters
              </button>
            </div>
          )}
          {events.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <div className="w-12 h-12 rounded-xl bg-zinc-900 border border-zinc-800 flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-zinc-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
              <p className="text-zinc-500 text-sm">Waiting for events...</p>
              <p className="text-zinc-600 text-xs mt-1">Logs will appear here as the workflow runs</p>
            </div>
          )}
          {filteredEvents.map((ev, i) => {
            const color = EVENT_COLORS[ev.type] ?? "text-zinc-400";
            const phaseColor = PHASE_COLORS[ev.phase] ?? "text-zinc-500";
            const phaseLabel = PHASE_LABELS[ev.phase] ?? "LOG";

            return (
              <div
                key={i}
                className="flex items-start gap-3 py-1.5 px-2 rounded hover:bg-zinc-900/30 transition-colors group"
              >
                <EventIcon type={ev.type} phase={ev.phase} />
                <span className="text-zinc-600 flex-shrink-0 font-mono w-16">{ts(ev.timestamp)}</span>
                <span className={`${phaseColor} flex-shrink-0 font-semibold w-8`}>{phaseLabel}</span>
                <span className={`${color} flex-1 break-all`}>{ev.message}</span>
              </div>
            );
          })}
          <div ref={bottomRef} />
        </div>
      </div>
    </Card>
  );
}
