# Ralph-Loop Commands for workflow-dev

Each command is ready to run with ralph-starter.

## How to Use

```bash
# Run a specific task
ralph-starter run "TASK_DESCRIPTION" --from ./ISSUE_TASK.md --commit --validate

# Or use auto mode from Linear
ralph-starter auto --source linear --label "bug" --limit 5
```

---

## HEL-8: Fix Makefile hardcoded path

```bash
ralph-starter run "Fix the Makefile to use portable paths instead of hardcoded /Users/helder/Projetos/workflow-dev. Use \$(shell git rev-parse --show-toplevel) to dynamically detect the project root. Make sure 'make api', 'make ui', and 'make dev' work from any directory." --from ./FIX_MAKEFILE.md --commit
```

**FIX_MAKEFILE.md content:**
```markdown
# Fix Makefile Hardcoded Path

## Task

The Makefile in this project has a hardcoded path `/Users/helder/Projetos/workflow-dev` which breaks on other machines.

## Current Problem

```makefile
api:
    cd /Users/helder/Projetos/workflow-dev && \
    source .venv/bin/activate && \
    uvicorn dev_workflow.api.server:app --reload --port 8000
```

## Solution

Replace with:

```makefile
.PHONY: api ui dev

ROOT_DIR := $(shell git rev-parse --show-toplevel 2>/dev/null || pwd)

api:
    cd $(ROOT_DIR) && \
    source .venv/bin/activate && \
    uvicorn dev_workflow.api.server:app --reload --port 8000

ui:
    cd $(ROOT_DIR)/frontend && npm run dev

dev:
    @echo "Run in two terminals:"
    @echo "  Terminal 1: make api"
    @echo "  Terminal 2: make ui"
```

## Files to Modify

- Makefile

## Acceptance Criteria

- `make api` works from any directory
- `make ui` works from any directory
- `make dev` shows instructions
```

---

## HEL-9: Fix Frontend API empty string

```bash
ralph-starter run "Fix the frontend API configuration. The const API = '' is empty, making all fetch requests go to /api/* on Next.js server instead of http://localhost:8000. Create next.config.mjs with a proxy for /api/* to http://localhost:8000, then remove the empty API variable and update all fetch calls to use /api/* directly." --from ./FIX_API.md --commit
```

**FIX_API.md content:**
```markdown
# Fix Frontend API Configuration

## Problem

In `frontend/app/page.tsx`, there's:
```typescript
const API = "";
```

This makes `${API}/api/executions` become `/api/executions` (relative to Next.js server, not the backend).

## Solution

1. Create `frontend/next.config.mjs`:

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*',
      },
    ];
  },
};
export default nextConfig;
```

2. Remove `const API = ""` from all files
3. Update fetch calls from `${API}/api/...` to `/api/...`

## Files to Modify

- `frontend/app/page.tsx` (remove const API = "")
- `frontend/app/executions/[id]/page.tsx` (same)
- `frontend/next.config.mjs` (create if not exists)

## Acceptance Criteria

- API requests go to localhost:8000
- Frontend can fetch executions list
- Frontend can create new executions
```

---

## HEL-10: Create .env.example

```bash
ralph-starter run "Create .env.example files with all required environment variables. Root .env.example should have MINIMAX_API_KEY, MINIMAX_MODEL, MINIMAX_API_BASE, BRAVE_API_KEY, API_PORT, API_HOST. Frontend .env.example should have NEXT_PUBLIC_API_URL if needed. Also add .env to .gitignore." --from ./ENV_EXAMPLE.md --commit
```

**ENV_EXAMPLE.md content:**
```markdown
# Create .env.example Files

## Task

Create .env.example files documenting all required environment variables.

## Root .env.example

```env
# MiniMax LLM (required)
MINIMAX_API_KEY=your_minimax_api_key_here
MINIMAX_MODEL=minimax-m2.7-highspeed
MINIMAX_API_BASE=https://api.minimax.io/v1

# Search (optional)
BRAVE_API_KEY=your_brave_api_key_here

# Server
API_PORT=8000
API_HOST=0.0.0.0

# Database (optional - for development)
# DATABASE_URL=postgresql://user:pass@localhost:5432/devworkflow
```

## Frontend .env.example

```env
# API URL for frontend (optional - defaults to relative)
# NEXT_PUBLIC_API_URL=http://localhost:8000
```

## .gitignore Addition

```
# Environment
.env
.env.local
.env.*.local
```

## Files to Create

- `.env.example` (root)
- `frontend/.env.example`

## Files to Modify

- `.gitignore` (add .env entries)
```

---

## HEL-11: Create README.md

```bash
ralph-starter run "Create a comprehensive README.md for the workflow-dev project. Include: project description, architecture diagram (text-based), quick start instructions, development setup (make api, make ui), environment variables, API documentation, and feature list. Use proper markdown formatting with badges." --from ./README.md --commit
```

**README.md content:**
```markdown
# Dev Workflow

100% automated AI development workflow using CrewAI + MiniMax.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Dev Workflow Flow                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  💡 Idea → 🔍 Researcher → 📋 Planner →                    │
│                      │                                      │
│                      ▼                                      │
│  🚀 Deploy ← 🧪 Tester ← 👀 Reviewer ←                   │
│                      │                                      │
│                      ▼                                      │
│               💻 Executor                                   │
│                      │                                      │
│                      ▼                                      │
│              ✅ Approved → Next Phase                       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

```bash
# 1. Clone
git clone https://github.com/Heldinhow/workflow-dev.git
cd workflow-dev

# 2. Setup environment
cp .env.example .env
# Edit .env with your API keys

# 3. Install
make setup

# 4. Run
make dev
```

## Development

```bash
make api    # Start FastAPI backend (port 8000)
make ui     # Start Next.js frontend (port 3000)
make dev    # Show instructions for running both
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| MINIMAX_API_KEY | MiniMax API key | Yes |
| MINIMAX_MODEL | Model to use | No (default: minimax-m2.7-highspeed) |
| BRAVE_API_KEY | Brave Search API key | No |

## API Endpoints

- `GET /api/executions` - List all executions
- `POST /api/executions` - Create new execution
- `GET /api/executions/{id}` - Get execution details
- `GET /api/executions/{id}/events` - SSE stream for execution events
- `DELETE /api/executions/{id}` - Cancel execution

## Tech Stack

- **Backend**: Python, CrewAI, FastAPI, SSE
- **Frontend**: Next.js 14, React, Tailwind CSS, TypeScript
```

---

## HEL-12: Add docker-compose.yml

```bash
ralph-starter run "Add docker-compose.yml for easy local development. Include services for: backend (FastAPI), frontend (Next.js), postgres (for development), and redis (optional). Create Dockerfiles for both backend and frontend. Add docker-compose commands to Makefile." --from ./DOCKER.md --commit
```

**DOCKER.md content:**
```markdown
# Add Docker Compose for Local Development

## Task

Create Docker-based development environment.

## docker-compose.yml

```yaml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile.api
    ports:
      - "8000:8000"
    environment:
      - MINIMAX_API_KEY=\${MINIMAX_API_KEY}
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/workflow
    depends_on:
      - db
      - redis
    volumes:
      - .:/app
    command: uvicorn dev_workflow.api.server:app --reload --host 0.0.0.0 --port 8000

  ui:
    build:
      context: ./frontend
      dockerfile: Dockerfile.ui
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    volumes:
      - ./frontend:/app
      - /app/node_modules

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=workflow
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

## Files to Create

- `docker-compose.yml`
- `Dockerfile.api`
- `Dockerfile.ui`
- `.dockerignore`

## Makefile Additions

```makefile
docker-up:
    docker-compose up -d

docker-down:
    docker-compose down

docker-logs:
    docker-compose logs -f
```
```

---

## Running All Issues

### Option 1: Run specific issues by number
```bash
ralph-starter run "Fix HEL-8: Fix Makefile hardcoded path..." --from ./FIX_MAKEFILE.md --commit
ralph-starter run "Fix HEL-9: Fix Frontend API..." --from ./FIX_API.md --commit
# etc.
```

### Option 2: Auto mode from Linear
```bash
# Get all "Bug" labeled issues
ralph-starter auto --source linear --label "bug" --limit 10

# Get all "Improvement" labeled issues  
ralph-starter auto --source linear --label "Improvement" --limit 10
```

### Option 3: Sequential by priority
```bash
# Priority 1 (CRITICAL)
ralph-starter run "Fix the Makefile hardcoded path issue" --from ./FIX_MAKEFILE.md --commit --validate
ralph-starter run "Fix the frontend API empty string issue" --from ./FIX_API.md --commit --validate

# Priority 2
ralph-starter run "Create .env.example files" --from ./ENV_EXAMPLE.md --commit
ralph-starter run "Create comprehensive README.md" --from ./README.md --commit
ralph-starter run "Increase test coverage" --from ./TESTS.md --commit

# Priority 3
ralph-starter run "Add docker-compose.yml" --from ./DOCKER.md --commit
ralph-starter run "Replace polling with SSE" --from ./SSE.md --commit
# etc.
```

---

## Notes

- All commands use `--commit` to auto-commit changes
- Add `--validate` for tests/lint validation
- Add `--push` to push to remote after commit
- Use `--max-iterations 30` for larger tasks
