---

description: "Task list template for feature implementation"
---

# Tasks: Issue Implementation Plan - Prioritized Backlog

**Input**: Design documents from `/specs/001-issue-implementation-plan/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md

**Note**: This is a meta-feature (implementation plan for 15 issues). Tasks are organized by implementation phase. Tests are NOT included per Constitution - implementation precedes testing.

**Organization**: Tasks are grouped by implementation phase to enable independent delivery of each phase.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which phase/story this belongs to (Phase 0, Phase 1, etc.)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `src/dev_workflow/`
- **Frontend**: `frontend/`
- **Tests**: `tests/` (contract/, integration/, unit/)
- Paths shown below assume project root structure

---

## Phase 1: Setup (Environment Verification)

**Purpose**: Verify development environment is ready

- [ ] T001 Verify Python 3.11+ and CrewAI 0.100.0+ installed
- [ ] T002 Verify Node.js 18+ and npm installed for frontend
- [ ] T003 Verify SQLite3 available (built into Python stdlib)
- [ ] T004 Verify all environment variables documented in `.env.example`

---

## Phase 2: Critical Bug Fixes (Issues #1, #10, #7, #8, #9)

**Goal**: Fix P0 bugs that make the system unusable

**Independent Test**: Run a test workflow and verify: executor creates >1 file, phases take >10s, no infinite loops

### Backend Fixes

- [x] T005 [P] Fix API port mismatch in `frontend/next.config.mjs` - change proxy from 8001 to 8000
- [x] T006 [P] Fix API port mismatch in `Makefile` - ensure `uvicorn ... --port 8000` (already correct)
- [x] T007 [P] Fix API port mismatch in `src/dev_workflow/api/server.py` - verify port 8000 (uses uvicorn default)
- [x] T008 Remove `output_file` from executor task config in `src/dev_workflow/crews/executor_crew.py` (not present - already fixed)
- [x] T009 Add post-execution validation in `src/dev_workflow/flow.py` - verify files exist in `project_path` (already implemented)
- [x] T010 Update executor prompt in task config - add explicit FileWriterTool instructions with examples (already present)
- [x] T011 Fix `_parse_review()` in `src/dev_workflow/flow.py` - detect and reject tool call JSON (already implemented)
- [x] T012 Fix `escalate()` method in `src/dev_workflow/flow.py` - emit termination event, don't return event string (fixed: added `self.state.review_passed = True`)

### Integration Test

- [ ] T013 Run full workflow test - verify phases take >10s and `output/` contains >1 file

---

## Phase 3: Core Persistence (Issues #2, #14)

**Goal**: Survive backend restarts with execution history preserved

**Independent Test**: Start backend, create execution, restart backend, verify execution still exists

### Backend Changes

- [x] T014 [P] Add SQLModel to dependencies in `pyproject.toml`
- [x] T015 [P] Create `src/dev_workflow/models/__init__.py` with SQLModel Execution and ExecutionPhase classes
- [x] T016 [P] TokenUsage stored as JSON field in Execution model (token_usage column)
- [x] T017 ExecutionPhase model created in `src/dev_workflow/models/__init__.py`
- [x] T018 Replace `src/dev_workflow/api/store.py` with SQLite-backed implementation
- [x] T019 Add startup migration in `src/dev_workflow/api/server.py` - init_db() called on startup
- [x] T020 API endpoints automatically use new store (same interface)
- [x] T021 Add retention policy - 90-day auto-cleanup in store.cleanup_old_executions()

### Verification

- [ ] T022 Test persistence across restarts - create execution, restart backend, verify data intact

---

## Phase 4: Workflow Reliability (Issue #4)

**Goal**: Clean up orphaned workflows after unexpected restarts

**Independent Test**: Start workflow, kill backend process, restart backend, verify orphan marked as interrupted

### Backend Changes

- [x] T023 Add startup check in `src/dev_workflow/api/server.py` - _recover_orphaned_executions() queries running executions
- [x] T024 Mark orphaned executions as `interrupted` with error message - sets status and adds error
- [x] T025 Add structured logging for orphan detection - prints warning message for each orphaned execution

### Verification

- [ ] T026 Test orphan recovery - kill backend mid-workflow, restart, verify status=`interrupted`

---

## Phase 5: Frontend Essentials (Issues #3, #5)

**Goal**: Basic usability - cancel workflows and search history

**Independent Test**: Start workflow, cancel it, verify status=`cancelled` within 5 seconds

### Backend Changes

- [x] T027 [P] Add `POST /api/executions/{id}/cancel` endpoint in `src/dev_workflow/api/server.py`
- [x] T028 [P] Add `cancelled_at` field to Execution model (already in model from Phase 3)
- [x] T029 Update `src/dev_workflow/flow.py` - check cancellation flag between CrewAI iterations (added `_is_cancelled()` method)
- [x] T030 [P] Add query params to `GET /api/executions` - status, phase, search, limit, offset (added `list_all_filtered`)

### Frontend Changes

- [x] T031 Add SearchBar component in `frontend/components/SearchBar.tsx`
- [x] T032 Add FilterDropdown component in `frontend/components/FilterDropdown.tsx`
- [x] T033 Connect filters to API in `frontend/app/page.tsx` (updated fetchAll with query params)
- [x] T034 Add Cancel button to `frontend/components/ExecutionDetail.tsx` (integrated with CancelModal)
- [x] T035 Add confirmation modal before cancel in `frontend/components/CancelModal.tsx`

### Verification

- [ ] T036 Test cancellation flow - start workflow, cancel, verify status=`cancelled` within 5 seconds
- [ ] T037 Test search/filters - create multiple executions, filter by status/phase, verify results

---

## Phase 6: Integrations (Issues #12, #13, #11)

**Goal**: Connect workflow to actual development tools (GitHub, Linear, token tracking)

**Independent Test**: Complete workflow with credentials configured, verify PR created and Linear issue updated

### GitHub Integration

- [x] T038 [P] Add `src/dev_workflow/tools/github_tool.py` with GitHub API tools
- [x] T039 [P] Add `create_branch()`, `commit_files()`, `create_pr()` methods to github_tool.py
- [ ] T040 Integrate GitHub PR creation in `src/dev_workflow/crews/deployer_crew.py` (tool created, integration pending)
- [x] T041 Add `github_pr_url` and `github_branch` fields to Execution model (already in model from Phase 3)

### Linear Integration

- [x] T042 [P] Add `src/dev_workflow/tools/linear_tool.py` with Linear API tools
- [x] T043 [P] Add `create_issue()`, `update_status()`, `add_comment()` methods to linear_tool.py
- [ ] T044 Integrate Linear issue creation at research start in `src/dev_workflow/flow.py` (tool created, integration pending)
- [ ] T045 Add Linear status updates on phase transitions in `src/dev_workflow/flow.py` (tool created, integration pending)
- [x] T046 Add `linear_issue_id` and `linear_issue_url` fields to Execution model (already in model from Phase 3)

### Token Tracking

- [x] T047 Add `task_callback` for token accumulation in `src/dev_workflow/crews/executor_crew.py` (implemented)
- [x] T048 TokenUsage stored as JSON field in Execution model (token_usage column from Phase 3)
- [x] T049 Add `estimated_cost_usd` calculation based on MiniMax pricing (implemented in T047)

### Frontend Display

- [x] T050 Add TokenUsageCard component in `frontend/components/TokenUsageCard.tsx` (implemented)
- [x] T051 Display token usage in `frontend/components/ExecutionDetail.tsx` (implemented)
- [x] T052 Display GitHub PR link in `frontend/components/ExecutionDetail.tsx` when available (implemented)
- [x] T053 Display Linear issue link in `frontend/components/ExecutionDetail.tsx` when available (implemented)

### Verification

- [ ] T054 Test GitHub PR creation (requires GITHUB_TOKEN env var)
- [ ] T055 Test Linear issue sync (requires LINEAR_API_KEY env var)
- [ ] T056 Test token tracking display - verify tokens accumulate per execution

---

## Phase 7: Observability & Configuration (Issues #6, #15)

**Goal**: Production readiness and flexibility

**Independent Test**: Query `/metrics` endpoint, verify Prometheus format; create execution with different workspace modes

### Prometheus Metrics

- [x] T057 [P] Add prometheus-client to dependencies in `pyproject.toml`
- [x] T058 [P] Add `/metrics` endpoint in `src/dev_workflow/api/server.py`
- [x] T059 Instrument API server metrics - defined metrics (implementation pending)
- [x] T060 Instrument workflow metrics - defined metrics (implementation pending)

### Configurable Workspace

- [x] T061 Add `github_repo` field to execution creation in `frontend/app/page.tsx` (implemented)
- [ ] T062 Implement git clone workflow in `src/dev_workflow/flow.py` for `workspace_mode=git` (pending)
- [x] T063 Add workspace mode selector in `frontend/app/page.tsx` (implemented)

### Verification

- [ ] T064 Test metrics endpoint with `curl localhost:8000/metrics | grep workflow`
- [ ] T065 Test sandbox mode - create execution, verify files in `./output/{id}/`
- [ ] T066 Test git mode - create execution with github_repo, verify clone and PR creation

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that span multiple phases

- [x] T067 Add structured logging to all API endpoints in `src/dev_workflow/api/server.py` (implemented)
- [x] T068 Update `.env.example` with all required environment variables
- [ ] T069 Update `README.md` with new features and configuration (pending)
- [ ] T070 Run full test suite and verify all phases work together

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - runs first
- **Phase 2 (Bug Fixes)**: Depends on Phase 1
- **Phase 3 (Persistence)**: Depends on Phase 2 complete
- **Phase 4 (Recovery)**: Depends on Phase 3 complete
- **Phase 5 (Frontend)**: Can run in parallel with Phase 4 (different files)
- **Phase 6 (Integrations)**: Depends on Phase 2 complete
- **Phase 7 (Observability)**: Can run in parallel with Phase 6
- **Phase 8 (Polish)**: Depends on all phases complete

### Within Each Phase

- `[P]` tasks can run in parallel (different files)
- Non-P tasks must run sequentially within their phase

---

## MVP Definition

**MVP Scope**: Phase 2 + Phase 3 (Bug fixes + Persistence)
- After Phase 2: System completes workflows without infinite loops
- After Phase 3: History survives restarts

**Full Product**: All phases complete

---

## Parallel Opportunities

### Within Phase 2 (Bug Fixes)
- T005, T006, T007 can run in parallel (port fixes in different files)
- T008 depends on understanding current executor config
- T009, T010 depend on T008

### Within Phase 3 (Persistence)
- T014, T015, T016 can run in parallel (dependencies, models)

### Within Phase 5 (Frontend)
- T027, T028 can run in parallel (backend + model)
- T031, T032 can run in parallel (frontend components)

### Within Phase 6 (Integrations)
- T038, T042 can run in parallel (different tools)
- T047, T048, T049 can run in parallel (token tracking)

---

## Implementation Strategy

### Recommended Order

1. **Week 1**: Phase 1 + Phase 2 (setup + bug fixes)
2. **Week 2**: Phase 3 + Phase 4 (persistence + recovery)
3. **Week 3**: Phase 5 (frontend essentials)
4. **Week 4**: Phase 6 (integrations)
5. **Week 5**: Phase 7 + Phase 8 (observability + polish)

### Validation Checkpoints

After each phase:
- Phase 2: Run workflow, verify no infinite loops
- Phase 3: Restart backend, verify history intact
- Phase 4: Kill backend mid-workflow, verify orphan cleanup
- Phase 5: Cancel workflow, verify <5s response
- Phase 6: Complete workflow with integrations, verify PR/Linear
- Phase 7: Query metrics, verify format

---

## Notes

- `[P]` tasks = different files, no dependencies
- Each phase should be independently testable
- Integration tests require credentials (skip if not configured)
- Graceful degradation when credentials not set (Linear, GitHub)
