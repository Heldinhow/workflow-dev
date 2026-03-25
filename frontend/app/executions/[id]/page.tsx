"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import type { Execution, WorkflowEvent } from "@/lib/types";
import { useExecutionEvents } from "@/lib/sse";
import { StatusBadge } from "@/components/StatusBadge";
import { PhaseTimeline } from "@/components/PhaseTimeline";
import { LogViewer } from "@/components/LogViewer";
import { RetryBadge } from "@/components/RetryBadge";
import { CancelModal } from "@/components/CancelModal";
import { TokenUsageCard } from "@/components/TokenUsageCard";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/Card";
import { Button } from "@/components/Button";

function elapsed(ex: Execution): string {
  if (!ex.started_at) return "—";
  const start = new Date(ex.started_at).getTime();
  const end = ex.completed_at ? new Date(ex.completed_at).getTime() : Date.now();
  const s = Math.floor((end - start) / 1000);
  if (s < 60) return `${s}s`;
  return `${Math.floor(s / 60)}m ${s % 60}s`;
}

function ArrowLeftIcon() {
  return (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
    </svg>
  );
}

function ConnectionStatus({
  connected,
  streamDone,
}: {
  connected: boolean;
  streamDone: boolean;
}) {
  const status = connected && !streamDone ? "live" : streamDone ? "ended" : "connecting";
  const colorClass =
    connected && !streamDone
      ? "text-emerald-400"
      : streamDone
        ? "text-zinc-500"
        : "text-zinc-600";

  return (
    <span className={`inline-flex items-center gap-1.5 text-xs font-medium ${colorClass}`}>
      <span
        className={`w-1.5 h-1.5 rounded-full ${
          connected && !streamDone ? "bg-emerald-500 pulse" : "bg-zinc-600"
        }`}
      />
      {status}
    </span>
  );
}

export default function ExecutionDetail() {
  const { id } = useParams<{ id: string }>();
  const [execution, setExecution] = useState<Execution | null>(null);
  const [notFound, setNotFound] = useState(false);
  const [events, setEvents] = useState<WorkflowEvent[]>([]);
  const [elapsedStr, setElapsedStr] = useState("0s");
  const [showCancelModal, setShowCancelModal] = useState(false);
  const [cancelling, setCancelling] = useState(false);

  const handleEvent = (event: WorkflowEvent) => {
    setEvents((prev) => [...prev, event]);

    setExecution((prev) => {
      if (!prev) return prev;
      const updated = { ...prev };

      if (event.type === "execution_started") {
        updated.status = "running";
        updated.started_at = event.timestamp;
      } else if (event.type === "phase_started") {
        updated.current_phase = event.phase as Execution["current_phase"];
        updated.status = "running";
        updated.phases = updated.phases.map((p) =>
          p.name === event.phase ? { ...p, status: "running", started_at: event.timestamp } : p
        );
      } else if (event.type === "phase_completed") {
        updated.phases = updated.phases.map((p) =>
          p.name === event.phase
            ? { ...p, status: "completed", completed_at: event.timestamp }
            : p
        );
      } else if (event.type === "phase_failed") {
        updated.phases = updated.phases.map((p) =>
          p.name === event.phase
            ? { ...p, status: "failed", completed_at: event.timestamp }
            : p
        );
      } else if (event.type === "retry") {
        updated.retry_count = (event.data.retry_count as number) || updated.retry_count;
      } else if (event.type === "test_retry") {
        updated.test_retry_count =
          (event.data.test_retry_count as number) || updated.test_retry_count;
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

  const handleStreamEnd = () => {
    fetch(`/api/executions/${id}`)
      .then((r) => (r.ok ? r.json() : null))
      .then((data) => data && setExecution(data));
  };

  const { connected, streamDone } = useExecutionEvents(id, {
    onEvent: handleEvent,
    onStreamEnd: handleStreamEnd,
  });

  async function handleCancel() {
    setCancelling(true);
    try {
      const r = await fetch(`/api/executions/${id}/cancel`, { method: "POST" });
      if (r.ok) {
        setShowCancelModal(false);
        setExecution((prev) => prev ? { ...prev, status: "cancelled" } : prev);
      }
    } finally {
      setCancelling(false);
    }
  }

  useEffect(() => {
    fetch(`/api/executions/${id}`)
      .then((r) => {
        if (!r.ok) {
          setNotFound(true);
          return null;
        }
        return r.json();
      })
      .then((data) => data && setExecution(data));
  }, [id]);

  useEffect(() => {
    if (!execution?.started_at || execution.completed_at) {
      if (execution) setElapsedStr(elapsed(execution));
      return;
    }
    const t = setInterval(() => setElapsedStr(elapsed(execution!)), 1000);
    return () => clearInterval(t);
  }, [execution?.started_at, execution?.completed_at]);

  if (notFound) {
    return (
      <div className="space-y-6 animate-fade-in">
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-sm text-zinc-500 hover:text-zinc-300 transition-colors"
        >
          <ArrowLeftIcon />
          Back to Executions
        </Link>
        <Card>
          <CardContent className="py-16 text-center">
            <h2 className="text-lg font-semibold text-zinc-300 mb-2">Execution not found</h2>
            <p className="text-sm text-zinc-500 mb-6">
              This execution may have been deleted or never existed.
            </p>
            <Button variant="secondary" onClick={() => (window.location.href = "/")}>
              Go to Dashboard
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!execution) {
    return (
      <div className="space-y-6">
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-sm text-zinc-500 hover:text-zinc-300 transition-colors"
        >
          <ArrowLeftIcon />
          Back to Executions
        </Link>
        <Card>
          <CardContent className="py-16 flex flex-col items-center justify-center">
            <div className="w-8 h-8 border-2 border-indigo-500/30 border-t-indigo-500 rounded-full animate-spin mb-4" />
            <p className="text-sm text-zinc-500">Loading execution...</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  const isActive = execution.status === "running";

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Breadcrumb */}
      <div className="flex items-center justify-between">
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-sm text-zinc-500 hover:text-zinc-300 transition-colors"
        >
          <ArrowLeftIcon />
          Back to Executions
        </Link>
        <ConnectionStatus connected={connected} streamDone={streamDone} />
      </div>

      {/* Header Card */}
      <Card>
        <CardContent className="p-6">
          <div className="flex flex-col lg:flex-row lg:items-start justify-between gap-4">
            <div className="space-y-3 flex-1 min-w-0">
              <div className="flex flex-wrap items-center gap-3">
                <StatusBadge status={execution.status} size="large" />
                <span className="text-sm font-mono text-zinc-500">{id}</span>
                {isActive && (
                  <span className="text-sm font-mono text-zinc-400 bg-zinc-800/50 px-2 py-0.5 rounded">
                    {elapsedStr}
                  </span>
                )}
                {!isActive && execution.completed_at && (
                  <span className="text-sm font-mono text-zinc-500">{elapsedStr}</span>
                )}
              </div>
              <h1 className="text-xl font-semibold text-zinc-100 leading-tight max-w-2xl">
                {execution.feature_request}
              </h1>
              <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-zinc-500 font-mono">
                <span>Project: {execution.project_path}</span>
              </div>
            </div>

            {/* Action buttons */}
            {isActive && (
              <div className="flex items-center gap-2">
                <Button variant="danger" size="sm" onClick={() => setShowCancelModal(true)}>
                  Cancel
                </Button>
              </div>
            )}
          </div>

          {/* Escalation alert */}
          {execution.status === "escalated" && execution.errors.length > 0 && (
            <div className="mt-5 border border-amber-500/20 bg-amber-500/10 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <svg
                  className="w-4 h-4 text-amber-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                  />
                </svg>
                <p className="text-sm font-medium text-amber-400">Escalation — max retries exhausted</p>
              </div>
              <div className="space-y-1">
                {execution.errors.map((e, i) => (
                  <p key={i} className="text-xs text-amber-300/70 font-mono bg-amber-500/5 px-2 py-1 rounded inline-block mr-2">
                    {e}
                  </p>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Main layout: left = phases + metadata | right = log */}
      <div className="grid grid-cols-1 lg:grid-cols-[320px_1fr] gap-4 min-h-[600px]">
        {/* Left column */}
        <div className="flex flex-col gap-4">
          {/* Phase timeline */}
          <Card>
            <CardHeader className="p-5 pb-0">
              <CardTitle as="h2">Pipeline</CardTitle>
            </CardHeader>
            <CardContent className="p-5">
              <PhaseTimeline phases={execution.phases} />
            </CardContent>
          </Card>

          {/* Retry counters */}
          <Card>
            <CardHeader className="p-5 pb-0">
              <CardTitle as="h3">Retries</CardTitle>
            </CardHeader>
            <CardContent className="p-5 space-y-3">
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
            </CardContent>
          </Card>

          {/* Token usage */}
          <TokenUsageCard tokenUsage={execution.token_usage || {}} />

          {/* GitHub PR link */}
          {execution.github_pr_url && (
            <Card>
              <CardHeader className="p-5 pb-0">
                <CardTitle as="h3">Pull Request</CardTitle>
              </CardHeader>
              <CardContent className="p-5">
                <a
                  href={execution.github_pr_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-indigo-400 hover:text-indigo-300 font-mono break-all"
                >
                  {execution.github_pr_url}
                </a>
                {execution.github_branch && (
                  <p className="text-xs text-zinc-500 mt-1">
                    Branch: <span className="font-mono">{execution.github_branch}</span>
                  </p>
                )}
              </CardContent>
            </Card>
          )}

          {/* Linear issue link */}
          {execution.linear_issue_url && (
            <Card>
              <CardHeader className="p-5 pb-0">
                <CardTitle as="h3">Linear Issue</CardTitle>
              </CardHeader>
              <CardContent className="p-5">
                <a
                  href={execution.linear_issue_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-purple-400 hover:text-purple-300 font-mono break-all"
                >
                  {execution.linear_issue_url}
                </a>
                {execution.linear_issue_id && (
                  <p className="text-xs text-zinc-500 mt-1">
                    Issue ID: <span className="font-mono">{execution.linear_issue_id}</span>
                  </p>
                )}
              </CardContent>
            </Card>
          )}
        </div>

        {/* Right column: log viewer */}
        <LogViewer events={events} autoScroll={isActive} />
      </div>

      <CancelModal
        isOpen={showCancelModal}
        onConfirm={handleCancel}
        onCancel={() => setShowCancelModal(false)}
        executionId={id}
      />
    </div>
  );
}
