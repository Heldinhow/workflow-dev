# Research: Issue Implementation Plan

**Feature**: Prioritized Issue Backlog Implementation
**Branch**: `001-issue-implementation-plan`
**Date**: 2026-03-24

## Research Summary

This is a meta-feature: an implementation plan for addressing existing issues in the dev-workflow system. The "research" is effectively the issue analysis already documented in the GitHub issues.

## Phase 0: Critical Bug Fixes Research

### Issue #1: API Port Mismatch

**Decision**: Standardize on port 8000 for the backend API

**Rationale**: FastAPI defaults to 8000, which is the industry convention. The frontend proxy should be updated to point to port 8000 instead of 8001.

**Alternatives considered**:
- Use environment variable for port (adds complexity, no immediate need)
- Use random available port (breaks frontend connectivity)

### Issues #10, #7: LLM Tool Calling & Executor

**Decision**: Remove `output_file` from executor task config; add post-execution validation

**Rationale**: The root cause is the executor relying on CrewAI's `output_file` mechanism instead of explicit FileWriterTool calls. MiniMax model appears to treat `output_file` as satisfying the task without creating actual files.

**Fix approach**:
1. Remove `output_file` from executor task YAML
2. Add explicit validation: check `project_path` for created files after executor completes
3. Improve prompt with explicit FileWriterTool usage checklist
4. Add `expected_output` requiring list of file paths created

### Issue #8: Reviewer JSON Output

**Decision**: Add JSON validation in `_parse_review()` to detect tool call JSON

**Rationale**: The reviewer is returning tool call JSON instead of ReviewOutput JSON. Need to detect this pattern and handle as a parsing failure with clear feedback.

**Fix approach**:
1. Check if parsed JSON contains `tool` key → reject as malformed
2. Clarify task prompt: output must be JSON with `passed`, `severity`, `issues`, `feedback` keys
3. Add fallback: if no files found in project_path, return `passed=False` with "No files found"

### Issue #9: Infinite Escalation Loop

**Decision**: Have `escalate` method emit termination event instead of returning event string

**Rationale**: The current implementation returns `"escalate"` which re-triggers the router, causing infinite loop. The fix is to emit `execution_escalated` event and return `None` (or just pass) to terminate cleanly.

**Fix approach**:
```python
@listen("escalate")
def escalate(self):
    _emit.emit(self.state.execution_id, "execution_escalated", "", 
               "Max retries exhausted", {"errors": self.state.errors})
    # Do NOT return event string - let flow terminate naturally
```

## Phase 1: Persistence Research

### SQLite vs PostgreSQL

**Decision**: SQLite for MVP, PostgreSQL path available

**Rationale**: 
- SQLite is zero-dependency, file-based, sufficient for single-server deployment
- SQLModel (Pydantic + SQLAlchemy) provides easy migration path
- No operational overhead (no database server needed)
- Can migrate to PostgreSQL later if needed (same SQLModel interface)

**Schema approach**:
```python
class Execution(SQLModel, table=True):
    id: str = Field(primary_key=True)
    feature_request: str
    project_path: str
    status: str
    current_phase: Optional[str]
    retry_count: int = 0
    test_retry_count: int = 0
    errors: str = "[]"  # JSON
    log: str = "[]"     # JSON
    github_pr_url: str = ""
    linear_issue_id: str = ""
    token_usage: str = "{}"  # JSON
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
```

## Phase 2: Recovery Research

### Orphan Workflow Detection

**Decision**: On startup, check for executions in `running` status and mark as `interrupted`

**Rationale**: Since we're adding persistence in Phase 1, we can now track true execution state. On restart, any `running` execution is guaranteed to be orphaned (no actual workflow running).

**Implementation**:
1. On server startup, query executions with `status='running'`
2. For each, update status to `interrupted` with error message
3. Log the orphan detection for debugging

## Phase 3: Frontend Essentials Research

### Cancellation Mechanism

**Decision**: Add `DELETE /api/executions/{id}/cancel` endpoint; set `cancelled` flag in store

**Rationale**: The CrewAI flow runs synchronously in FastAPI. To cancel, we need:
1. Store-level cancellation flag that the flow periodically checks
2. Signal to the running task that cancellation was requested
3. Flow checks flag between CrewAI agent iterations

**Implementation**:
- Add `cancelled_at: Optional[datetime]` to Execution model
- Flow's `_run_executor` checks `state.cancelled` before each agent iteration
- If cancelled, flow terminates gracefully with `cancelled` status

### Search & Filters

**Decision**: Add query parameters to `GET /api/executions`

**API Design**:
```
GET /api/executions?status=running&phase=research&search=feature+auth&limit=20&offset=0
```

**Implementation**:
- Backend: SQLModel supports filtering via `.where()` clauses
- Frontend: Debounced search input + filter dropdowns
- Response includes `total_count` for pagination UI

## Phase 4: Integration Research

### GitHub PR Creation

**Decision**: Extend deployer crew with GitHub API tools

**Tools needed**:
- `create_branch(name)` - create feature branch
- `commit_and_push(message, files)` - commit changes
- `create_pr(title, body, base, head)` - create PR

**Flow integration**:
1. After executor/reviewer cycle completes successfully
2. Deployer crew creates branch, commits output files, creates PR
3. Store `github_pr_url` on execution
4. Emit `github_pr_created` SSE event

### Linear Issue Sync

**Decision**: Create Linear issue at workflow start, update on phase changes

**API Design**:
- Create issue: `POST /api/linear/issues` with `{title, description, team_id}`
- Update status: `PATCH /api/linear/issues/{id}` with `{state}`

**Flow integration**:
1. At `research_phase` start: create Linear issue
2. On phase transition: update issue state
3. On completion: add PR URL as comment, move to Done

### Token Tracking

**Decision**: Use LiteLLM callback to accumulate token counts

**Implementation**:
- CrewAI supports `task_callback` hook
- Callback receives LLM response with `usage` field
- Accumulate `prompt_tokens`, `completion_tokens`, `total_tokens`
- Calculate `estimated_cost_usd` using MiniMax pricing

## Phase 5: Observability Research

### Prometheus Metrics

**Decision**: Add `/metrics` endpoint with prometheus-client

**Metrics to expose**:
- `workflow_executions_total{status}` - counter by status
- `workflow_phase_duration_seconds{phase}` - histogram
- `workflow_active_runs` - gauge
- `api_request_duration_seconds{endpoint}` - histogram
- `llm_tokens_total` - counter with labels

### Configurable Workspace

**Decision**: Add `github_repo` field to execution creation

**Modes**:
- `sandbox` (default): `project_path=./output/{execution_id}/`
- `git`: `project_path=/tmp/workflow-{id}/`, clone `github_repo`, modify, PR

## Technical Decisions Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Port standardization | 8000 | Industry convention, FastAPI default |
| Persistence | SQLite | Zero dependency, sufficient for MVP |
| Cancellation | Flag-based | Simple, no thread interruption needed |
| GitHub integration | Extend deployer crew | Consistent with existing pattern |
| Linear integration | Event-driven | Reuses existing SSE infrastructure |
| Metrics | Prometheus | Industry standard, easy to implement |
