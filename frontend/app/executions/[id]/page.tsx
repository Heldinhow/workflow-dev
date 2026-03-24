"use client";

import { useEffect, useRef, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import type { Execution, WorkflowEvent } from "@/lib/types";
import { StatusBadge } from "@/components/StatusBadge";
import { PhaseTimeline } from "@/components/PhaseTimeline";
import { LogViewer } from "@/components/LogViewer";
import { RetryBadge } from "@/components/RetryBadge";

const API = "";

function elapsed(ex: Execution): string {
  if (!ex.started_at) return "—";
  const start = new Date(ex.started_at).getTime();
  const end   = ex.completed_at ? new Date(ex.completed_at).getTime() : Date.now();
  const s     = Math.floor((end - start) / 1000);
  if (s < 60) return `${s}s`;
  return `${Math.floor(s / 60)}m ${s % 60}s`;
}

export default function ExecutionDetail() {
  const { id }                          = useParams<{ id: string }>();
  const [execution, setExecution]       = useState<Execution | null>(null);
  const [events, setEvents]             = useState<WorkflowEvent[]>([]);
  const [connected, setConnected]       = useState(false);
  const [streamDone, setStreamDone]     = useState(false);
  const [elapsedStr, setElapsedStr]     = useState("0s");
  const esRef                           = useRef<EventSource | null>(null);

  // Fetch initial execution state
  useEffect(() => {
    fetch(`${API}/api/executions/${id}`)
      .then(r => r.ok ? r.json() : null)
      .then(data => data && setExecution(data));
  }, [id]);

  // SSE connection
  useEffect(() => {
    const es = new EventSource(`${API}/api/executions/${id}/events`);
    esRef.current = es;

    es.onopen = () => setConnected(true);

    es.onmessage = (e) => {
      const event: WorkflowEvent = JSON.parse(e.data);

      if (event.type === "stream_end") {
        setStreamDone(true);
        es.close();
        // Refresh final state
        fetch(`${API}/api/executions/${id}`)
          .then(r => r.ok ? r.json() : null)
          .then(data => data && setExecution(data));
        return;
      }

      setEvents(prev => [...prev, event]);

      // Update execution state from events optimistically
      setExecution(prev => {
        if (!prev) return prev;
        const updated = { ...prev };

        if (event.type === "execution_started") {
          updated.status = "running";
          updated.started_at = event.timestamp;
        } else if (event.type === "phase_started") {
          updated.current_phase = event.phase as Execution["current_phase"];
          updated.status = "running";
          updated.phases = updated.phases.map(p =>
            p.name === event.phase
              ? { ...p, status: "running", started_at: event.timestamp }
              : p
          );
        } else if (event.type === "phase_completed") {
          updated.phases = updated.phases.map(p =>
            p.name === event.phase
              ? { ...p, status: "completed", completed_at: event.timestamp }
              : p
          );
        } else if (event.type === "phase_failed") {
          updated.phases = updated.phases.map(p =>
            p.name === event.phase
              ? { ...p, status: "failed", completed_at: event.timestamp }
              : p
          );
        } else if (event.type === "retry") {
          updated.retry_count = (event.data.retry_count as number) || updated.retry_count;
        } else if (event.type === "test_retry") {
          updated.test_retry_count = (event.data.test_retry_count as number) || updated.test_retry_count;
        } else if (event.type === "execution_completed") {
          updated.status = "completed";
          updated.completed_at = event.timestamp;
          updated.current_phase = null;
        } else if (event.type === "execution_escalated") {
          updated.status = "escalated";
          updated.completed_at = event.timestamp;
        } else if (event.type === "execution_failed") {
          updated.status = "failed";
          updated.completed_at = event.timestamp;
        }
        return updated;
      });
    };

    es.onerror = () => {
      setConnected(false);
      if (!streamDone) es.close();
    };

    return () => es.close();
  }, [id]);

  // Live elapsed timer
  useEffect(() => {
    if (!execution?.started_at || execution.completed_at) {
      if (execution) setElapsedStr(elapsed(execution));
      return;
    }
    const t = setInterval(() => setElapsedStr(elapsed(execution!)), 1000);
    return () => clearInterval(t);
  }, [execution?.started_at, execution?.completed_at]);

  if (!execution) {
    return (
      <div className="text-sm text-zinc-600 font-mono">Loading…</div>
    );
  }

  const isActive = execution.status === "running";

  return (
    <div className="space-y-6">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-xs text-zinc-600">
        <Link href="/" className="hover:text-zinc-400 transition-colors">
          Executions
        </Link>
        <span>/</span>
        <span className="font-mono text-zinc-500">{execution.id}</span>
      </div>

      {/* Header */}
      <div className="border border-zinc-800 rounded bg-zinc-900 p-5">
        <div className="flex items-start justify-between gap-4">
          <div className="space-y-1.5 flex-1 min-w-0">
            <div className="flex items-center gap-3">
              <StatusBadge status={execution.status} />
              {isActive && (
                <span className="text-xs font-mono text-zinc-600">
                  {elapsedStr}
                </span>
              )}
              {!isActive && execution.completed_at && (
                <span className="text-xs font-mono text-zinc-600">
                  {elapsedStr}
                </span>
              )}
              <span className={`text-xs ml-auto flex items-center gap-1.5 ${
                connected && !streamDone
                  ? "text-emerald-500"
                  : "text-zinc-700"
              }`}>
                <span className={`w-1.5 h-1.5 rounded-full ${
                  connected && !streamDone ? "bg-emerald-500 pulse" : "bg-zinc-700"
                }`} />
                {connected && !streamDone ? "live" : streamDone ? "ended" : "connecting"}
              </span>
            </div>
            <h1 className="text-base font-medium text-zinc-100 leading-tight">
              {execution.feature_request}
            </h1>
            <div className="flex items-center gap-4 text-xs text-zinc-600 font-mono">
              <span>id: {execution.id}</span>
              <span>path: {execution.project_path}</span>
            </div>
          </div>
        </div>

        {/* Escalation alert */}
        {execution.status === "escalated" && execution.errors.length > 0 && (
          <div className="mt-4 border border-amber-800/50 bg-amber-950/30 rounded p-3 space-y-1">
            <p className="text-xs font-medium text-amber-400">Escalation — max retries exhausted</p>
            {execution.errors.map((e, i) => (
              <p key={i} className="text-xs text-amber-300/70 font-mono">{e}</p>
            ))}
          </div>
        )}
      </div>

      {/* Main layout: left = phases + metadata | right = log */}
      <div className="grid grid-cols-[280px_1fr] gap-4 h-[600px]">

        {/* Left column */}
        <div className="flex flex-col gap-4">

          {/* Phase timeline */}
          <div className="border border-zinc-800 rounded bg-zinc-900 p-5 flex-1">
            <p className="text-xs font-medium text-zinc-500 mb-5 uppercase tracking-wider">
              Pipeline
            </p>
            <PhaseTimeline phases={execution.phases} />
          </div>

          {/* Retry counters */}
          <div className="border border-zinc-800 rounded bg-zinc-900 p-4 space-y-3">
            <p className="text-xs font-medium text-zinc-500 uppercase tracking-wider">
              Retries
            </p>
            <RetryBadge
              label="Code retries"
              count={execution.retry_count}
              max={execution.max_retries}
              color="blue"
            />
            <RetryBadge
              label="Test retries"
              count={execution.test_retry_count}
              max={execution.max_test_retries}
              color="amber"
            />
          </div>
        </div>

        {/* Right column: log viewer */}
        <LogViewer events={events} autoScroll={isActive} />
      </div>
    </div>
  );
}
