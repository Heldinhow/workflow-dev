"""FastAPI server — execution management + SSE streaming."""

import asyncio
import json
import logging
import os
import queue
import sys
import threading
import uuid
from datetime import datetime

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, PlainTextResponse
from pydantic import BaseModel
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    generate_latest,
    CONTENT_TYPE_LATEST,
)

load_dotenv()

from dev_workflow.api import store
from dev_workflow import emitter


def _json_log(level: str, event: str, **kwargs) -> None:
    """Output structured log as JSON."""
    log_entry = {
        "time": datetime.now().isoformat(),
        "level": level,
        "logger": "dev_workflow.api",
        "event": event,
        **kwargs,
    }
    print(json.dumps(log_entry), file=sys.stdout)


def setup_logging():
    """Configure structured JSON logging."""
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    for h in root_logger.handlers[:]:
        root_logger.removeHandler(h)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(message)s"))
    root_logger.addHandler(handler)


setup_logging()
logger = logging.getLogger("dev_workflow.api")

# ── Prometheus Metrics ─────────────────────────────────────────────────────────
WORKFLOW_EXECUTIONS_TOTAL = Counter(
    "workflow_executions_total",
    "Total workflow executions",
    ["status"],
)
WORKFLOW_PHASE_DURATION = Histogram(
    "workflow_phase_duration_seconds",
    "Duration of workflow phases",
    ["phase"],
)
WORKFLOW_ACTIVE_RUNS = Gauge("workflow_active_runs", "Currently running workflows")
API_REQUEST_DURATION = Histogram(
    "api_request_duration_seconds",
    "API request duration",
    ["endpoint"],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 5.0],
)

# ── SSE subscriber registry ───────────────────────────────────────────────────
# execution_id → list of thread-safe queues (one per connected browser tab)
_sse_queues: dict[str, list[queue.Queue]] = {}
_sse_lock = threading.Lock()

PHASE_MAP = {
    "research_start": ("research", "phase_started"),
    "research_end": ("research", "phase_completed"),
    "planning_start": ("planning", "phase_started"),
    "planning_end": ("planning", "phase_completed"),
    "deploy_start": ("deployment", "phase_started"),
    "deploy_end": ("deployment", "phase_completed"),
    "escalated": ("", "execution_escalated"),
}


def _on_event(event: dict) -> None:
    """Handler registered with emitter — updates store + fans out to SSE subscribers."""
    execution_id = event.get("execution_id", "")
    if not execution_id:
        return

    # Persist to log
    store.append_log(execution_id, event)

    # Update metrics
    etype = event.get("type", "")
    phase = event.get("phase", "")
    if etype in (
        "execution_started",
        "execution_completed",
        "execution_escalated",
        "execution_failed",
    ):
        WORKFLOW_EXECUTIONS_TOTAL.labels(status=etype.replace("execution_", "")).inc()

    # Structured log key events
    if etype in (
        "phase_started",
        "phase_completed",
        "execution_completed",
        "execution_escalated",
        "execution_failed",
    ):
        _json_log(
            "INFO"
            if "completed" in etype
            else "WARNING"
            if "escalated" in etype
            else "ERROR"
            if "failed" in etype
            else "INFO",
            etype,
            execution_id=execution_id,
            phase=phase,
            message=event.get("message", "")[:200],
        )
    phase = event.get("phase", "")
    ts = event.get("timestamp", datetime.now().isoformat())
    data = event.get("data", {})

    if etype == "execution_started":
        store.update(execution_id, status="running", started_at=ts)

    elif etype == "phase_started":
        store.update(execution_id, current_phase=phase)
        store.update_phase(execution_id, phase, status="running", started_at=ts)

    elif etype == "phase_completed":
        store.update_phase(
            execution_id,
            phase,
            status="completed",
            completed_at=ts,
            output=data.get("output"),
        )

    elif etype == "phase_failed":
        store.update_phase(execution_id, phase, status="failed", completed_at=ts)

    elif etype == "retry":
        store.update(
            execution_id,
            retry_count=data.get("retry_count", 0),
            current_phase="execution",
        )

    elif etype == "test_retry":
        store.update(execution_id, test_retry_count=data.get("test_retry_count", 0))

    elif etype == "execution_completed":
        store.update(
            execution_id,
            status="completed",
            completed_at=ts,
            current_phase=None,
            current_agent=None,
        )

    elif etype == "execution_escalated":
        store.update(
            execution_id,
            status="escalated",
            completed_at=ts,
            errors=data.get("errors", []),
            current_phase=None,
        )

    elif etype == "execution_failed":
        store.update(execution_id, status="failed", completed_at=ts, current_phase=None)

    # Fan out to SSE subscribers
    with _sse_lock:
        qs = list(_sse_queues.get(execution_id, []))
    for q in qs:
        q.put(event)


emitter.register(_on_event)


# ── FastAPI app ───────────────────────────────────────────────────────────────

app = FastAPI(title="Dev Workflow API", version="1.0.0")


@app.on_event("startup")
def on_startup():
    store.init_db()
    _recover_orphaned_executions()


def _recover_orphaned_executions() -> None:
    """Check for executions stuck in 'running' state and mark them as interrupted."""
    from datetime import datetime

    executions = store.list_all()
    orphaned = [ex for ex in executions if ex.get("status") == "running"]
    for ex in orphaned:
        execution_id = ex["id"]
        store.update(
            execution_id,
            status="interrupted",
            completed_at=datetime.now().isoformat(),
            errors=[
                "Orphaned workflow: backend restarted while execution was in progress"
            ],
        )
        print(f"⚠️ Recovered orphaned execution {execution_id}")


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)


class StartRequest(BaseModel):
    feature_request: str
    project_path: str = "./output"
    max_retries: int = 3
    max_test_retries: int = 3
    workspace_mode: str = "sandbox"
    github_repo: str | None = None


@app.post("/api/executions", status_code=201)
def start_execution(req: StartRequest):
    execution_id = str(uuid.uuid4())[:8]
    store.create(execution_id, req.feature_request, req.project_path)
    store.update(
        execution_id,
        max_retries=req.max_retries,
        max_test_retries=req.max_test_retries,
        workspace_mode=req.workspace_mode,
        github_repo=req.github_repo,
    )
    _json_log(
        "INFO",
        "execution_created",
        execution_id=execution_id,
        feature_request=req.feature_request[:100],
        workspace_mode=req.workspace_mode,
        github_repo=req.github_repo,
    )

    thread = threading.Thread(
        target=_run_workflow,
        args=(
            execution_id,
            req.feature_request,
            req.project_path,
            req.max_retries,
            req.max_test_retries,
            req.workspace_mode,
            req.github_repo,
        ),
        daemon=True,
    )
    thread.start()
    return {"id": execution_id}


def _run_workflow(
    execution_id: str,
    feature_request: str,
    project_path: str,
    max_retries: int,
    max_test_retries: int,
    workspace_mode: str = "sandbox",
    github_repo: str | None = None,
) -> None:
    from dev_workflow.flow import DevWorkflowFlow

    emitter.emit(execution_id, "execution_started", "", "Workflow started")
    try:
        flow = DevWorkflowFlow()
        flow.kickoff(
            inputs={
                "feature_request": feature_request,
                "project_path": project_path,
                "execution_id": execution_id,
                "max_retries": max_retries,
                "max_test_retries": max_test_retries,
                "workspace_mode": workspace_mode,
                "github_repo": github_repo,
            }
        )
        state = flow.state
        if state.deploy_succeeded:
            emitter.emit(
                execution_id,
                "execution_completed",
                "deployment",
                "Workflow completed — deployment successful",
            )
        elif state.errors:
            emitter.emit(
                execution_id,
                "execution_escalated",
                "",
                "Workflow escalated after max retries",
                {"errors": state.errors},
            )
    except Exception as exc:
        emitter.emit(execution_id, "execution_failed", "", f"Workflow error: {exc}")
    finally:
        # Sentinel to close SSE streams
        with _sse_lock:
            qs = list(_sse_queues.get(execution_id, []))
        for q in qs:
            q.put(None)


@app.get("/api/executions")
def list_executions(
    status: str = None,
    phase: str = None,
    search: str = None,
    limit: int = 100,
    offset: int = 0,
):
    return store.list_all_filtered(
        status=status, phase=phase, search=search, limit=limit, offset=offset
    )


@app.get("/api/executions/{execution_id}")
def get_execution(execution_id: str):
    ex = store.get(execution_id)
    if not ex:
        raise HTTPException(404, "Execution not found")
    return ex


@app.post("/api/executions/{execution_id}/cancel")
def cancel_execution(execution_id: str):
    ex = store.get(execution_id)
    if not ex:
        raise HTTPException(404, "Execution not found")
    if ex.get("status") != "running":
        raise HTTPException(400, "Only running executions can be cancelled")
    from datetime import datetime

    store.update(
        execution_id, cancelled_at=datetime.now().isoformat(), status="cancelled"
    )
    _json_log("INFO", "execution_cancelled", execution_id=execution_id)
    return {"status": "cancelled", "cancelled_at": datetime.now().isoformat()}


@app.get("/api/executions/{execution_id}/events")
async def stream_events(execution_id: str):
    ex = store.get(execution_id)
    if not ex:
        raise HTTPException(404, "Execution not found")

    q: queue.Queue = queue.Queue()
    with _sse_lock:
        _sse_queues.setdefault(execution_id, []).append(q)

    existing_log = list(ex.get("log", []))

    async def generate():
        # Replay history for clients that connect mid-run
        for entry in existing_log:
            yield f"data: {json.dumps(entry)}\n\n"

        loop = asyncio.get_event_loop()
        while True:
            try:
                event = await loop.run_in_executor(None, lambda: q.get(timeout=25))
                if event is None:
                    yield f"data: {json.dumps({'type': 'stream_end'})}\n\n"
                    break
                yield f"data: {json.dumps(event)}\n\n"
            except Exception:
                yield ": heartbeat\n\n"

        with _sse_lock:
            qs = _sse_queues.get(execution_id, [])
            if q in qs:
                qs.remove(q)

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.get("/metrics")
def metrics():
    return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)
