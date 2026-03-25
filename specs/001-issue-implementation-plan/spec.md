# Feature Specification: Issue Implementation Plan - Prioritized Backlog

**Feature Branch**: `001-issue-implementation-plan`
**Created**: 2026-03-24
**Status**: Draft
**Input**: "veja todas as issues abertas e crie um plano detalhado de implementação seguindo uma ordem de prioridade que faça sentido. seja pensando em MVP quanto reaproveitamento de fluxo"

## User Scenarios & Testing

### User Story 1 - Prioritized Issue Implementation (Priority: P1)

As a developer, I need to implement issues in a logical priority order so that the most critical problems are fixed first and each implementation phase delivers usable value.

**Why this priority**: The system currently has 4 P0 bugs blocking all functionality and 2 P0 enhancements required for basic operation. Without fixing these, no other feature work is viable.

**Independent Test**: Can be validated by implementing any single phase and verifying that the system functions correctly with those changes applied.

**Acceptance Scenarios**:

1. **Given** the development workflow system, **When** the P0 bugs are fixed in order, **Then** the core executor, reviewer, and escalation flow work correctly without infinite loops or malformed outputs.

2. **Given** the fixed system, **When** basic persistence is added, **Then** execution history survives backend restarts.

3. **Given** the stabilized system, **When** new features are added in priority order, **Then** each phase builds on a stable foundation with maximum code reuse.

---

### User Story 2 - MVP Delivery Strategy (Priority: P2)

As a product owner, I need the implementation phased so that usable increments ship at each stage, allowing early feedback and iterative improvement.

**Why this priority**: Shiping value early and often reduces risk and allows course correction based on real usage.

**Independent Test**: Can be validated by deploying after each phase and confirming the advertised features work.

**Acceptance Scenarios**:

1. **Given** Phase 0 completion, **When** a user runs a workflow, **Then** the system completes without crashes, infinite loops, or lost data.

2. **Given** Phase 1 completion, **When** the backend restarts mid-workflow, **Then** the system recovers cleanly and displays accurate history.

3. **Given** Phase 2 completion, **When** a user needs to stop a running workflow, **Then** they can cancel it and see the cancelled status.

---

### User Story 3 - Flow Reuse and Extensibility (Priority: P3)

As a developer, I need new features to reuse existing flow patterns (executor, reviewer, deployer crews) so that the codebase remains maintainable and consistent.

**Why this priority**: The current flow architecture (research → plan → tasks → implementation → review → escalate) is well-structured. New features like GitHub integration and Linear sync should extend this pattern, not create new ones.

**Independent Test**: Can be validated by verifying that new integrations follow the same event-driven architecture and reuse existing components.

**Acceptance Scenarios**:

1. **Given** the existing CrewAI flow architecture, **When** GitHub integration is added, **Then** it follows the same deployer crew pattern and reuses existing store/event mechanisms.

2. **Given** the existing SSE event system, **When** Linear integration is added, **Then** it emits the same event types (execution_started, execution_updated, execution_completed) for consistent frontend updates.

---

### Edge Cases

- What happens when a workflow is cancelled while the LLM is generating a response? The system MUST handle this gracefully without data corruption.
- How does the system handle rate limits when creating GitHub PRs or Linear issues? Integration failures should not block workflow completion.
- How does the system behave when the SQLite database becomes corrupted? The system MUST detect this and fall back to in-memory mode with appropriate error reporting.
- How does the system handle LLM API failures (rate limits, outages, invalid responses)? The system MUST retry with exponential backoff and fail gracefully with max retries exhausted after [NEEDS CLARIFICATION: number of retries]. Integration failures should not block workflow completion.

## Requirements

### Functional Requirements

- **FR-001**: System MUST fix API port mismatch (#1) to allow frontend to connect to backend
- **FR-002**: System MUST fix LLM tool calling issues (#10) so phases take reasonable time (>10s) and produce actual output
- **FR-003**: System MUST fix executor (#7) to create real files using FileWriterTool before marking complete
- **FR-004**: System MUST fix reviewer (#8) to return valid JSON output and detect malformed tool call responses
- **FR-005**: System MUST fix infinite loop (#9) by having escalate emit termination event instead of returning event string
- **FR-006**: System MUST add SQLite persistence (#2, #14) for execution history that survives restarts
- **FR-007**: System MUST add workflow recovery (#4) to detect and clean up orphaned running workflows on startup
- **FR-008**: System MUST add execution cancellation (#3) with backend endpoint and frontend button
- **FR-009**: System MUST add search and filters (#5) to the execution history API and frontend
- **FR-010**: System MUST add GitHub PR creation (#12) as part of deployer crew workflow
- **FR-011**: System MUST add Linear issue sync (#13) to create and update issues as workflow progresses
- **FR-012**: System MUST add token usage tracking (#11) displayed per execution in frontend
- **FR-013**: System MUST add Prometheus metrics (#6) for workflow and system observability
- **FR-014**: System MUST add configurable workspace (#15) allowing users to specify target GitHub repo per execution

### Key Entities

- **Execution**: Represents a workflow execution instance with status, current_phase, retry counts, timestamps, and associated metadata (github_pr_url, linear_issue_id, token_usage)
- **Issue**: Represents a Linear issue linked to a workflow execution, trackable via issue_id and URL
- **TokenUsage**: Tracks prompt_tokens, completion_tokens, total_tokens, and estimated_cost_usd per execution
- **WorkflowPhase**: Enum of possible phases (research, planning, implementation, review, escalate, completed, failed, cancelled)

## Success Criteria

### Measurable Outcomes

- **SC-001**: P0 bugs fixed: Executor creates real files (>1 file in output/), phases take >10s, reviewer returns valid JSON, no infinite loops
- **SC-002**: System completes workflow from start to finish without crashing or entering infinite escalation loop
- **SC-003**: Execution history persists across backend restarts with 100% data integrity
- **SC-004**: Users can cancel running workflows within 5 seconds of clicking cancel
- **SC-005**: History search returns results within 500ms for datasets up to 1000 executions
- **SC-006**: GitHub PR created automatically for every completed workflow when GITHUB_TOKEN configured
- **SC-007**: Linear issue created within 5 seconds of workflow start and updated as phases complete
- **SC-008**: Token usage displayed in frontend with <100ms latency update via SSE
- **SC-009**: Prometheus metrics endpoint returns valid metrics with <10ms latency
- **SC-010**: Workspace mode (sandbox vs git) selectable per execution without configuration changes

## Assumptions

- **Target users**: Developers using the workflow system to automate feature development (single-user personal tool)
- **Multi-user**: Not supported; system is designed for single-user local development workflow automation
- **Scope boundaries**: Mobile support is out of scope for this implementation; focus is on web dashboard and backend API
- **Data/environment**: SQLite chosen for persistence (zero dependencies, file-based, sufficient for single-server deployment)
- **Retention policy**: Execution history retained for 90 days with automatic cleanup of records older than 90 days
- **Integration patterns**: GitHub and Linear integrations are optional (graceful degradation when credentials not configured)
- **API key security**: All external API tokens (GITHUB_TOKEN, LINEAR_API_KEY, MINIMAX_API_KEY) MUST be provided via environment variables only, never stored in database
- **Flow architecture**: CrewAI Flow with executor/reviewer/deployer crews pattern is preserved and extended, not replaced

## Implementation Phases (Detailed)

### Phase 0: Critical Bug Fixes (P0)

**Issues**: #1 (port mismatch), #10 (LLM tools), #7 (executor no files), #8 (reviewer JSON), #9 (infinite loop)

**Rationale**: These bugs make the system unusable. Must fix before any feature work.

**Order**:
1. #1 - Port mismatch (enables testing)
2. #10, #7 - LLM tool usage and executor (root cause cascade)
3. #8 - Reviewer JSON parsing (depends on executor fixing)
4. #9 - Infinite loop (depends on reviewer fixing)

---

### Phase 1: Core Persistence (P0 Enhancement)

**Issues**: #2 and #14 (SQLite persistence)

**Rationale**: Without persistence, all data is lost on restart. Foundation for all subsequent features.

**Approach**: Replace in-memory store with SQLite via SQLModel, maintain same interface.

---

### Phase 2: Workflow Reliability (P1)

**Issues**: #4 (recovery after restart)

**Rationale**: If backend crashes mid-workflow, orphaned executions must be cleaned up.

---

### Phase 3: Frontend Essentials (P1)

**Issues**: #3 (cancel), #5 (search/filters)

**Rationale**: Basic usability - users need to stop long-running workflows and find historical executions.

---

### Phase 4: Integrations (P1)

**Issues**: #12 (GitHub PR), #13 (Linear sync), #11 (token tracking)

**Rationale**: Core value-add - connecting the workflow to actual development tools.

**Flow Reuse**: All three integrate with existing flow architecture via:
- GitHub: extends deployer crew with commit/PR tools
- Linear: uses events emitted by flow phases
- Token tracking: uses existing LLM callback hooks

---

### Phase 5: Observability & Configuration (P2)

**Issues**: #6 (Prometheus/Grafana), #15 (configurable workspace)

**Rationale**: Production readiness and flexibility for different use cases.

---

## Technical Notes

**Dependency Graph**:
```
#1 Port → enables testing everything
#10 LLM tools → #7 Executor → #8 Reviewer → #9 Infinite loop
#7,#8,#9 + #1 → Phase 0 complete
#2 Persistence → #4 Recovery (needs persistence to track orphaned executions)
#2 + #4 → Phase 1-2 complete
#3 Cancel + #5 Filters → Phase 3 complete
#12 GitHub + #13 Linear + #11 Tokens → Phase 4 complete
#6 Metrics + #15 Workspace → Phase 5 complete
```
