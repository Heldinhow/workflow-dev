# Data Model: Issue Implementation Plan

**Feature**: Prioritized Issue Backlog Implementation
**Branch**: `001-issue-implementation-plan`
**Date**: 2026-03-24

## Entity Relationships

```text
Execution (1) ──────< TokenUsage (1)
     │
     ├───────────< ExecutionPhase (1:N) - track phase history
     │
     └───────> LinearIssue (0:1) - optional Linear sync
     │
     └───────> GitHubPR (0:1) - optional GitHub PR
```

## Entities

### Execution

Main entity representing a workflow execution.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string (UUID) | yes | Primary key |
| `feature_request` | string | yes | User's original feature request text |
| `project_path` | string | yes | Path to execution workspace |
| `status` | enum | yes | Current status: `pending`, `running`, `completed`, `failed`, `cancelled`, `escalated`, `interrupted` |
| `current_phase` | enum | no | Current phase: `research`, `planning`, `implementation`, `review`, `escalate` |
| `retry_count` | int | yes | Number of retries on escalation |
| `test_retry_count` | int | yes | Number of test retries |
| `errors` | JSON array | yes | List of error objects `[{phase, message, timestamp}]` |
| `log` | JSON array | yes | List of log entries `[{timestamp, level, message, phase}]` |
| `cancelled_at` | datetime | no | When cancellation was requested |
| `github_pr_url` | string | no | URL to created GitHub PR |
| `github_branch` | string | no | Branch name used for PR |
| `linear_issue_id` | string | no | Linear issue ID (e.g., "ENG-123") |
| `linear_issue_url` | string | no | URL to Linear issue |
| `workspace_mode` | enum | yes | `sandbox` or `git` |
| `github_repo` | string | no | Target GitHub repo for git mode |
| `created_at` | datetime | yes | Execution creation timestamp |
| `started_at` | datetime | no | When execution actually started |
| `completed_at` | datetime | no | When execution finished |

### TokenUsage

Embedded document tracking LLM token consumption per execution.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `prompt_tokens` | int | yes | Tokens in prompt/input |
| `completion_tokens` | int | yes | Tokens in completion/output |
| `total_tokens` | int | yes | Sum of prompt + completion |
| `estimated_cost_usd` | float | yes | Cost based on MiniMax pricing |

**MiniMax Pricing (as of 2024)**:
- MiniMax M2.7: ~$0.001 per 1K tokens (verify current pricing)

### ExecutionPhase

Historical record of phase transitions for debugging.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `phase` | enum | yes | Phase name |
| `started_at` | datetime | yes | When phase started |
| `completed_at` | datetime | no | When phase completed |
| `duration_seconds` | float | no | Calculated duration |

### LinearIssue

Reference to Linear issue for sync.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `linear_id` | string | yes | Linear issue ID |
| `linear_url` | string | yes | Web URL to issue |
| `team_id` | string | yes | Linear team ID |
| `state` | string | no | Current state name |

### GitHubPR

Reference to created PR.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `pr_url` | string | yes | Web URL to PR |
| `pr_number` | int | no | PR number |
| `branch` | string | yes | Source branch name |
| `commit_sha` | string | no | Commit that created PR |

## Enums

### ExecutionStatus
```
pending → running → completed
                  ↓
              failed
                  ↓
              escalated (max retries)
                  
running → cancelled (user requested)
running → interrupted (orphan on restart)
```

### WorkflowPhase
```
research → planning → implementation → review
                                         ↓
                              completed ← (passed)
                              failed ← (not passed, retries exhausted)
                              escalate ← (not passed, trigger retry)
```

### WorkspaceMode
```
sandbox - uses local ./output/{execution_id}/ directory
git - clones github_repo, works in /tmp/, creates PR
```

## State Transitions

### Execution State Machine

```
                    ┌──────────────┐
                    │   pending    │
                    └──────┬───────┘
                           │ start()
                           ▼
                    ┌──────────────┐
         ┌─────────│   running    │─────────┐
         │         └──────┬───────┘         │
         │ cancel()      │ phase_complete()  │ escalate()
         ▼                ▼                   ▼
  ┌──────────────┐ ┌──────────────┐  ┌──────────────┐
  │  cancelled   │ │   review     │  │   escalate   │
  └──────────────┘ └──────┬───────┘  └──────┬───────┘
                          │ passed            │ max_retries?
                          ▼                   ▼
                   ┌──────────────┐  ┌──────────────┐
                   │  completed   │  │    failed    │
                   └──────────────┘  └──────────────┘
```

### Phase State Machine

```
research ──► planning ──► implementation ──► review
                              │                    │
                              │                    │ passed?
                              ▼                    ▼
                       ┌───────────┐          ┌───────────┐
                       │ (retry)  │          │ completed │
                       └───────────┘          └───────────┘
                              │                    │
                              │ not passed         │ not passed
                              ▼                    ▼
                       ┌───────────┐          ┌───────────┐
                       │ escalate  │          │ escalate  │
                       └───────────┘          └───────────┘
```

## Validation Rules

1. **Execution creation**: `feature_request` must be non-empty, `status` defaults to `pending`
2. **Cancellation**: Only `running` executions can be cancelled; sets `cancelled_at` timestamp
3. **Escalation**: Increments `retry_count`; if `retry_count >= max_retries`, transitions to `failed`
4. **Phase transitions**: Must follow enum order; cannot skip phases
5. **GitHub PR**: Only created when `workspace_mode = git` and execution `status = completed`
6. **Linear sync**: Graceful degradation if `LINEAR_API_KEY` not configured

## Indexes

For query performance on `GET /api/executions`:

1. `status` - for filtering by current status
2. `current_phase` - for filtering by phase
3. `created_at` - for sorting and date range queries
4. `feature_request` (text index) - for full-text search
