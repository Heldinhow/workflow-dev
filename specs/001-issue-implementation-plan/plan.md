# Implementation Plan: Issue Implementation Plan - Prioritized Backlog

**Branch**: `001-issue-implementation-plan` | **Date**: 2026-03-24 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-issue-implementation-plan/spec.md`

## Summary

Implement 15 prioritized issues in a 5-phase approach. Phase 0 fixes critical P0 bugs that make the system unusable. Subsequent phases add persistence, reliability, frontend improvements, integrations, and observability.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: CrewAI 0.100.0+, FastAPI, SQLModel, Pydantic v2, Next.js 14, React, TailwindCSS  
**Storage**: SQLite (MVP), PostgreSQL (future)  
**Testing**: pytest, Playwright (E2E)  
**Target Platform**: Linux server, macOS development  
**Project Type**: web-service (FastAPI backend) + web-app (Next.js frontend)  
**Performance Goals**: <500ms API response, <100ms SSE latency, >10s LLM phase duration  
**Constraints**: MiniMax API rate limits, GitHub API rate limits, Linear API limits  
**Scale/Scope**: Single-server deployment, ~1000 executions/day expected  

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Principles to verify**:
- [x] **Spec-Driven Development**: All changes traced back to issues/spec.md
- [x] **Library-First**: N/A - this is bug fixes and features, not library creation
- [x] **Test-First**: Each phase will have tests before implementation
- [x] **Contract & Integration Testing**: Integration tests for CrewAI flow, API endpoints
- [x] **Observability**: Structured logging already in place; Phase 5 adds Prometheus
- [x] **Versioning**: N/A - no public API version changes in this implementation

**Gate Status**: ✅ PASS (all principles either satisfied or N/A for this feature)

## Project Structure

### Documentation (this feature)

```text
specs/001-issue-implementation-plan/
├── plan.md              # This file
├── research.md          # Phase 0 output (research findings)
├── data-model.md        # Phase 1 output (entity designs)
├── quickstart.md        # Phase 1 output (implementation guide)
├── contracts/           # Phase 1 output (API contracts - empty for this meta-feature)
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
src/dev_workflow/
├── api/
│   ├── server.py        # FastAPI server (port fix in Phase 0)
│   └── store.py         # In-memory store → SQLite (Phase 1)
├── crews/
│   ├── executor_crew.py # Executor crew (fix in Phase 0)
│   ├── reviewer_crew.py # Reviewer crew (fix in Phase 0)
│   └── deployer_crew.py # Deployer crew (GitHub PR in Phase 4)
├── flow.py              # Main flow orchestration (infinite loop fix Phase 0)
├── models/              # NEW: SQLModel entities (Phase 1)
│   └── execution.py
├── tools/               # NEW: GitHub, Linear, token tracking tools
│   ├── github_tool.py
│   ├── linear_tool.py
│   └── token_tracker.py
└── state.py             # Workflow state

frontend/
├── app/
│   └── page.tsx         # Main dashboard (filters in Phase 3)
├── components/
│   ├── ExecutionList.tsx # With search/filters (Phase 3)
│   ├── ExecutionDetail.tsx # With cancel button (Phase 3)
│   └── TokenUsageCard.tsx # NEW (Phase 4)
└── lib/
    └── api.ts           # API client
```

**Structure Decision**: Web application with backend API + Next.js frontend. All bug fixes and new features modify existing files in their respective modules. No new top-level directories.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |

## Phase 0: Bug Fixes

**Order**: #1 (port) → #10,#7 (LLM/executor) → #8 (reviewer) → #9 (infinite loop)

### Tasks for Phase 0

- [ ] **T001** [P] Fix API port mismatch - update frontend proxy, Makefile, server.py to use port 8000
- [ ] **T002** [P] Remove output_file from executor task config - prevent CrewAI auto-writing
- [ ] **T003** Add post-execution validation in flow.py - verify files exist in project_path
- [ ] **T004** Update executor prompt - explicit FileWriterTool instructions with examples
- [ ] **T005** Fix _parse_review() - detect and reject tool call JSON
- [ ] **T006** Fix escalate() method - emit termination event, don't return event string
- [ ] **T007** Integration test - verify phases take >10s and create real files

## Phase 1: Persistence

**Issues**: #2, #14

### Tasks for Phase 1

- [ ] **T008** Add SQLModel dependency
- [ ] **T009** [P] Create Execution model with SQLModel
- [ ] **T010** [P] Create TokenUsage, ExecutionPhase models
- [ ] **T011** Replace store.py with SQLite-backed implementation
- [ ] **T012** Add startup migration (create tables)
- [ ] **T013** Update API endpoints to use new store
- [ ] **T014** Test persistence across restarts

## Phase 2: Recovery

**Issues**: #4

### Tasks for Phase 2

- [ ] **T015** Add startup check in server.py - find running executions
- [ ] **T016** Mark orphaned executions as interrupted
- [ ] **T017** Add structured logging for orphan detection
- [ ] **T018** Test recovery on restart

## Phase 3: Frontend Essentials

**Issues**: #3, #5

### Tasks for Phase 3

- [ ] **T019** [P] Add cancel endpoint: POST /api/executions/{id}/cancel
- [ ] **T020** [P] Add cancelled_at field to Execution model
- [ ] **T021** Update flow.py to check cancellation flag between iterations
- [ ] **T022** [P] Add query params to GET /api/executions (status, phase, search, limit, offset)
- [ ] **T023** Add SearchBar component
- [ ] **T024** Add FilterDropdown component (status, phase)
- [ ] **T025** Connect filters to API
- [ ] **T026** Test cancellation flow

## Phase 4: Integrations

**Issues**: #12, #13, #11

### Tasks for Phase 4

- [ ] **T027** [P] Add GitHub tools to deployer crew (create_branch, commit, create_pr)
- [ ] **T028** [P] Add LinearTool (create_issue, update_status, add_comment)
- [ ] **T029** Add task_callback for token accumulation
- [ ] **T030** Integrate GitHub PR creation in deployer flow
- [ ] **T031** Integrate Linear issue creation at research start
- [ ] **T032** Update Linear status on phase transitions
- [ ] **T033** Display token usage in frontend detail view
- [ ] **T034** Test with GitHub API (requires GITHUB_TOKEN)
- [ ] **T035** Test with Linear API (requires LINEAR_API_KEY)

## Phase 5: Observability

**Issues**: #6, #15

### Tasks for Phase 5

- [ ] **T036** [P] Add prometheus-client dependency
- [ ] **T037** [P] Add /metrics endpoint
- [ ] **T038** Instrument API server metrics (request duration, active connections)
- [ ] **T039** Instrument workflow metrics (executions by status, phase duration)
- [ ] **T040** Add github_repo field to execution creation
- [ ] **T041** Implement git clone workflow for workspace_mode=git
- [ ] **T042** Create Grafana dashboard (optional, nice-to-have)
- [ ] **T043** Test metrics endpoint with promtool

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 0**: No dependencies - can start immediately
- **Phase 1**: Depends on Phase 0 complete (need working system to test persistence)
- **Phase 2**: Depends on Phase 1 complete (need persistence to track orphaned executions)
- **Phase 3**: Can start in parallel with Phase 2 (different files)
- **Phase 4**: Can start after Phase 0 (basic flow must work for integrations)
- **Phase 5**: Can start in parallel with Phase 4 (different concerns)

### Within Each Phase

- Bug fixes should be sequential (they cascade)
- Frontend components can be parallel ([P] tasks)
- Integration tests last in each phase

## Implementation Strategy

### Recommended Order

1. **Week 1**: Phase 0 bug fixes (make system usable)
2. **Week 2**: Phase 1 + Phase 2 (persistence + recovery)
3. **Week 3**: Phase 3 frontend improvements
4. **Week 4**: Phase 4 integrations
5. **Week 5**: Phase 5 observability

### MVP Definition

- **MVP**: Phase 0 + Phase 1
- After Phase 0: System completes workflows without infinite loops
- After Phase 1: History survives restarts

### Parallel Opportunities

- T001, T002 can run in parallel (different files)
- T003 depends on T002
- T019, T020 can run in parallel (backend + model changes)
- T027, T028 can run in parallel (different integrations)
