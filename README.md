# Dev Workflow

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/Heldinhow/workflow-dev/actions/workflows/ci.yml/badge.svg)](https://github.com/Heldinhow/workflow-dev/actions/workflows/ci.yml)

AI-powered development workflow engine using CrewAI + MiniMax. Automates the full software development lifecycle from idea to deployment through a multi-agent pipeline.

## Architecture

```
Idea → Researcher → Planner → Executor ⇄ Reviewer → Tester ⇄ Executor ⇄ Reviewer → Deployer
                                                                                          ↓
                                                                              ✅ Deployment Complete
```

**Pipeline phases:**
- **Researcher** — Gathers context, analyzes requirements, collects dependencies
- **Planner** — Creates detailed implementation plan
- **Executor** — Writes code based on plan
- **Reviewer** — Validates code quality, security, and correctness
- **Tester** — Runs tests, verifies coverage, reports failures
- **Deployer** — Packages and deploys the solution

Retry loops handle failures: Executor/Reviewer cycle up to `max_retries`, then Tester/Executor/Reviewer cycle up to `max_test_retries` before escalation.

## Quick Start

```bash
# Clone and enter the project
git clone https://github.com/Heldinhow/workflow-dev.git
cd workflow-dev

# Set up environment
cp .env.example .env
# Edit .env and add your MINIMAX_API_KEY

# Start both API and UI (two terminals)
make dev
```

- **API**: http://localhost:8000
- **UI**: http://localhost:3000

## Development Commands

```bash
make api    # Start FastAPI server (port 8000)
make ui     # Start Next.js frontend (port 3000)
```

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `MINIMAX_API_KEY` | Yes | — | MiniMax API key for LLM inference |
| `MINIMAX_API_BASE` | No | `https://api.minimax.io/v1` | MiniMax API endpoint |
| `MINIMAX_MODEL` | No | `minimax-m2.7-highspeed` | Model to use |
| `CREWAI_STORAGE_DIR` | No | `./.crewai` | CrewAI persistence directory |
| `DATABASE_URL` | No | `sqlite:///./workflow.db` | SQLite database path |
| `GITHUB_TOKEN` | No | — | GitHub API token (optional) |
| `LINEAR_API_KEY` | No | — | Linear API key (optional) |
| `BRAVE_API_KEY` | No | — | Brave Search API key (optional) |
| `API_PORT` | No | `8000` | API server port |
| `API_HOST` | No | `0.0.0.0` | API server host |

## API Documentation

### Start Execution

```
POST /api/executions
```

Creates a new workflow execution.

**Request body:**
```json
{
  "feature_request": "Implement user authentication with JWT",
  "project_path": "./output",
  "max_retries": 3,
  "max_test_retries": 3,
  "workspace_mode": "sandbox",
  "github_repo": null
}
```

**Response:** `201 Created`
```json
{
  "id": "a1b2c3d4"
}
```

### List Executions

```
GET /api/executions
```

**Query parameters:** `status`, `phase`, `search`, `limit`, `offset`

**Response:** `200 OK` — Array of execution objects

### Get Execution

```
GET /api/executions/{execution_id}
```

**Response:** `200 OK` — Single execution object with phases, status, logs

### Stream Execution Events (SSE)

```
GET /api/executions/{execution_id}/events
```

Server-Sent Events stream for real-time execution updates.

**Event types:** `execution_started`, `phase_started`, `phase_completed`, `phase_failed`, `execution_completed`, `execution_escalated`, `execution_failed`

### Cancel Execution

```
POST /api/executions/{execution_id}/cancel
```

**Response:** `200 OK`
```json
{
  "status": "cancelled",
  "cancelled_at": "2026-03-25T10:00:00Z"
}
```

## Tech Stack

**Backend**
- [CrewAI](https://crewai.com/) — Multi-agent orchestration
- [FastAPI](https://fastapi.tiangolo.com/) — REST API server
- [Pydantic](https://docs.pydantic.dev/) — Data validation
- [SQLModel](https://sqlmodel.tiangolo.com/) — Database ORM
- [Prometheus Client](https://prometheus.io/) — Metrics

**LLM**
- [MiniMax](https://minimax.io/) — Language model (minimax-m2.7-highspeed)

**Frontend**
- [Next.js 14](https://nextjs.org/) — React framework
- [Tailwind CSS](https://tailwindcss.com/) — Styling
- [TypeScript](https://www.typescriptlang.org/) — Type safety

**Testing & Tools**
- [Pytest](https://docs.pytest.org/) — Python testing
- [Uvicorn](https://www.uvicorn.org/) — ASGI server
