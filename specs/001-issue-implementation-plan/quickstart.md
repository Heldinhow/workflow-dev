# Quickstart: Issue Implementation Plan

**Feature**: Prioritized Issue Backlog Implementation
**Branch**: `001-issue-implementation-plan`

## Overview

This document provides guidance for implementing the 15 open issues in prioritized order. Each phase builds on the previous one.

## Phase-by-Phase Quickstart

### Phase 0: Critical Bug Fixes

**Goal**: Make the system functional

```bash
# Order of implementation
# 1. Fix port mismatch (#1)
#    - Update frontend/next.config.mjs proxy to port 8000
#    - Update Makefile to use 8000
#    - Update src/dev_workflow/api/server.py port if hardcoded

# 2. Fix LLM tool calling (#10, #7)
#    - Remove output_file from executor task YAML
#    - Add post-execution validation in flow.py
#    - Update executor prompt with explicit FileWriterTool instructions

# 3. Fix reviewer JSON output (#8)
#    - Update _parse_review() to detect tool call JSON
#    - Add validation: reject if JSON contains "tool" key

# 4. Fix infinite loop (#9)
#    - Update escalate() to emit event without returning
#    - Test: ensure escalate called only once per execution
```

**Testing**:
```bash
# Start backend
make dev

# In another terminal, run a test workflow
curl -X POST http://localhost:8000/api/executions \
  -H "Content-Type: application/json" \
  -d '{"feature_request": "Add user authentication"}'

# Verify:
# - Backend starts without errors
# - Frontend connects to backend
# - Executor creates files in output/
# - Phases take >10 seconds
# - Reviewer returns valid JSON
# - No infinite escalation loops
```

### Phase 1: SQLite Persistence

**Goal**: Survive restarts

```bash
# Add SQLModel to dependencies
# pip install sqlmodel

# Implementation order:
# 1. Create src/dev_workflow/models/execution.py with SQLModel
# 2. Replace src/dev_workflow/api/store.py with SQLite-backed implementation
# 3. Maintain same interface (create, get, list_all, update)
# 4. Add startup migration (create tables if not exist)
```

**Testing**:
```bash
# Start backend, create execution
# Restart backend
# Verify execution still exists
curl http://localhost:8000/api/executions
```

### Phase 2: Workflow Recovery

**Goal**: Clean up orphaned workflows

```python
# In server.py startup:
# 1. Query executions with status='running'
# 2. For each, update status to 'interrupted'
# 3. Log orphan detection
```

### Phase 3: Frontend Essentials

**Goal**: Usability improvements

```bash
# Cancellation (#3):
# - Add POST /api/executions/{id}/cancel endpoint
# - Add cancelled_at field to Execution model
# - Update flow.py to check cancellation flag

# Search/Filters (#5):
# - Add query params to GET /api/executions
# - Add SearchBar and FilterDropdown components
```

### Phase 4: Integrations

**Goal**: Connect to development tools

```bash
# GitHub PR (#12):
# - Add github tools to deployer crew
# - Create branch, commit, PR on completion

# Linear Sync (#13):
# - Add LinearTool
# - Create issue at start, update on phase changes

# Token Tracking (#11):
# - Add task_callback to CrewAI config
# - Accumulate tokens in state
# - Display in frontend
```

### Phase 5: Observability

**Goal**: Production readiness

```bash
# Prometheus Metrics (#6):
# - Add prometheus-client
# - Add /metrics endpoint
# - Instrument key operations

# Configurable Workspace (#15):
# - Add github_repo field to execution creation
# - Implement git clone workflow for non-sandbox mode
```

## Verification Commands

```bash
# Run all tests
make test

# Run linting
make lint

# Verify no TypeScript errors (frontend)
cd frontend && npm run build

# Integration test
curl http://localhost:8000/health
curl http://localhost:3000  # frontend
```

## Common Issues

| Issue | Symptom | Fix |
|-------|---------|-----|
| Port mismatch | Frontend shows "connection refused" | Standardize on port 8000 |
| Executor no files | output/ is empty | Remove output_file, add validation |
| Infinite loop | "escalate called 100 times" | Don't return event string from escalate |
| Model not found | LiteLLM completion error | Check MINIMAX_API_KEY env var |
