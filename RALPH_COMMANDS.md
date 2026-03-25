# Ralph-Loop Commands for workflow-dev

**IMPORTANT:** Use `--` to separate the message from flags. Commits must be done manually after opencode runs.

## Correct Syntax

```bash
# WRONG (flags get parsed as part of message):
opencode run "Create file" --commit

# CORRECT (-- separates message from flags):
opencode run -- "Create file" --commit
```

After opencode completes, manually commit:
```bash
git add . && git commit -m "Your message" && git push
```

---

## Commands (Copy & Paste)

### HEL-17: Add .editorconfig ✅ ALREADY DONE

```bash
# Already completed - committed as 0379402
```

---

### HEL-8: Fix Makefile hardcoded path

```bash
cd workflow-dev
opencode run -- "Fix the Makefile. Current path '/Users/helder/Projetos/workflow-dev' is hardcoded. Use \$(shell git rev-parse --show-toplevel) to dynamically detect project root. Make targets 'api', 'ui', 'dev' work from any directory."
git add . && git commit -m "fix: Makefile portable paths" && git push
```

---

### HEL-9: Fix Frontend API empty string

```bash
cd workflow-dev
opencode run -- "Fix the frontend API. In frontend/app/page.tsx, const API = '' is empty making fetch go to /api/* on Next.js instead of localhost:8000. Create frontend/next.config.mjs with rewrites proxy for /api/* to http://localhost:8000. Remove empty API variable. Update all fetch calls to use /api/* directly."
git add . && git commit -m "fix: Frontend API proxy to backend" && git push
```

---

### HEL-11: Create README.md

```bash
cd workflow-dev
opencode run -- "Create comprehensive README.md. Include: project description, architecture diagram (text-based showing flow: Idea→Researcher→Planner→Executor→Reviewer→Tester→Deployer), quick start (clone, cp .env.example .env, make dev), development commands (make api, make ui), environment variables table, API documentation (GET/POST /api/executions, SSE endpoint), tech stack badges. Use proper markdown."
git add . && git commit -m "docs: Add comprehensive README" && git push
```

---

### HEL-10: Create .env.example

```bash
cd workflow-dev
opencode run -- "Create .env.example files. Root: MINIMAX_API_KEY, MINIMAX_MODEL (default: minimax-m2.7-highspeed), MINIMAX_API_BASE (https://api.minimax.io/v1), BRAVE_API_KEY (optional), API_PORT (8000), API_HOST (0.0.0.0). Frontend: NEXT_PUBLIC_API_URL if needed. Also add .env entries to .gitignore."
git add . && git commit -m "feat: Add .env.example files" && git push
```

---

### HEL-16: Increase test coverage

```bash
cd workflow-dev
opencode run -- "Increase test coverage. Add pytest.ini with testpaths=tests, python_files=test_*.py. Create tests/conftest.py with fixtures for mocking crews, API client, state. Add tests for: all 6 crews (researcher, planner, executor, reviewer, tester, deployer), API endpoints, state transitions, emitter pattern. Run pytest to verify."
git add . && git commit -m "test: Add comprehensive test coverage" && git push
```

---

### HEL-12: Add docker-compose.yml

```bash
cd workflow-dev
opencode run -- "Add docker-compose.yml for local development. Services: api (FastAPI port 8000), ui (Next.js port 3000), postgres (5432), redis (6379). Create Dockerfile.api and Dockerfile.ui. Add docker-up, docker-down, docker-logs to Makefile."
git add . && git commit -m "feat: Add Docker Compose for local dev" && git push
```

---

### HEL-13: Replace polling with SSE

```bash
cd workflow-dev
opencode run -- "Replace polling with SSE. Backend supports SSE at /api/executions/{id}/events. Create frontend/lib/sse.ts with useExecutionEvents hook using EventSource. Update frontend/app/page.tsx and frontend/app/executions/[id]/page.tsx to use the hook instead of setInterval(fetchAll, 5000)."
git add . && git commit -m "feat: Replace polling with SSE" && git push
```

---

### HEL-14: Add React Error Boundary

```bash
cd workflow-dev
opencode run -- "Add React Error Boundary. Create frontend/components/ErrorBoundary.tsx with proper error handling UI. Wrap app in frontend/app/layout.tsx with ErrorBoundary. Show user-friendly error message with retry button."
git add . && git commit -m "feat: Add React Error Boundary" && git push
```

---

### HEL-15: Add GitHub Actions CI/CD

```bash
cd workflow-dev
opencode run -- "Add GitHub Actions CI/CD. Create .github/workflows/ci.yml with jobs: lint (ruff for Python, ESLint for JS), type check (mypy for Python, tsc for TypeScript), backend tests (pytest), frontend build check (npm run build). Add pull_request and push triggers."
git add . && git commit -m "ci: Add GitHub Actions workflow" && git push
```

---

## Quick Summary

| Issue | Command |
|-------|---------|
| HEL-8 | `opencode run -- "Fix Makefile..."` + commit |
| HEL-9 | `opencode run -- "Fix API empty string..."` + commit |
| HEL-10 | `opencode run -- "Create .env.example..."` + commit |
| HEL-11 | `opencode run -- "Create README.md..."` + commit |
| HEL-12 | `opencode run -- "Add docker-compose..."` + commit |
| HEL-13 | `opencode run -- "Replace polling with SSE..."` + commit |
| HEL-14 | `opencode run -- "Add Error Boundary..."` + commit |
| HEL-15 | `opencode run -- "Add GitHub Actions..."` + commit |
| HEL-16 | `opencode run -- "Increase test coverage..."` + commit |
| HEL-17 | ✅ DONE |

---

## Notes

- Always use `--` to separate message from flags
- opencode's `--commit` flag does NOT auto-commit (bug/limitation)
- Always commit manually after opencode completes
- Use `--max-iterations 30` for complex tasks: `opencode run -- "task" --max-iterations 30`
