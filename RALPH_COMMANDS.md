# workflow-dev Improvement Commands

## Issues Created on GitHub

| GitHub # | Title | Linear | Status |
|----------|-------|--------|--------|
| #21 | Fix Makefile hardcoded path | HEL-8 | TODO |
| #22 | Frontend API points to empty string | HEL-9 | TODO |
| #23 | Create .env.example files | HEL-10 | TODO |
| #24 | Create comprehensive README.md | HEL-11 | TODO |
| #25 | Add docker-compose.yml | HEL-12 | TODO |
| #26 | Replace polling with SSE | HEL-13 | TODO |
| #27 | Add React Error Boundary | HEL-14 | TODO |
| #28 | Add GitHub Actions CI/CD | HEL-15 | TODO |
| #29 | Increase test coverage | HEL-16 | TODO |
| #17 | Add .editorconfig | HEL-17 | ✅ DONE |

---

## Ralph-Starter Status

**⚠️ NOTE:** The OpenCode SDK agent in ralph-starter has issues (creates empty commits). 
Use opencode directly instead for reliable results.

---

## OpenCode Commands (RECOMMENDED)

### #21: Fix Makefile
```bash
cd workflow-dev
opencode run -- "Fix the Makefile. Replace hardcoded '/Users/helder/Projetos/workflow-dev' path with \$(shell git rev-parse --show-toplevel). Make targets 'api', 'ui', 'dev' work from any directory."
git add . && git commit -m "fix: Makefile portable paths" && git push
```

### #22: Fix Frontend API
```bash
cd workflow-dev
opencode run -- "Fix frontend API. In frontend/app/page.tsx, const API = '' is empty making fetch go to /api/* on Next.js instead of localhost:8000. Create frontend/next.config.mjs with rewrites proxy for /api/* to http://localhost:8000. Remove empty API variable. Update all fetch calls to use /api/* directly."
git add . && git commit -m "fix: Frontend API proxy to backend" && git push
```

### #23: Create .env.example
```bash
cd workflow-dev
opencode run -- "Create .env.example files. Root: MINIMAX_API_KEY, MINIMAX_MODEL=minimax-m2.7-highspeed, MINIMAX_API_BASE=https://api.minimax.io/v1, BRAVE_API_KEY, API_PORT=8000, API_HOST=0.0.0.0. Frontend: NEXT_PUBLIC_API_URL. Add .env to .gitignore."
git add . && git commit -m "feat: Add .env.example files" && git push
```

### #24: Create README.md
```bash
cd workflow-dev
opencode run -- "Create comprehensive README.md. Include: badges (Python, License), project description, architecture diagram (text-based: Idea→Researcher→Planner→Executor→Reviewer→Tester→Deployer), quick start (clone, cp .env.example .env, make dev), development commands (make api, make ui), environment variables table, API documentation (GET/POST /api/executions, SSE endpoint), tech stack."
git add . && git commit -m "docs: Add comprehensive README" && git push
```

### #25: Add docker-compose.yml
```bash
cd workflow-dev
opencode run -- "Add docker-compose.yml for local development. Services: api (FastAPI port 8000), ui (Next.js port 3000), postgres (5432), redis (6379). Create Dockerfile.api and Dockerfile.ui. Add docker-up, docker-down, docker-logs to Makefile."
git add . && git commit -m "feat: Add Docker Compose for local dev" && git push
```

### #26: Replace polling with SSE
```bash
cd workflow-dev
opencode run -- "Replace polling with SSE. Backend supports SSE at /api/executions/{id}/events. Create frontend/lib/sse.ts with useExecutionEvents hook using EventSource. Update frontend/app/page.tsx and frontend/app/executions/[id]/page.tsx to use the hook instead of setInterval(fetchAll, 5000)."
git add . && git commit -m "feat: Replace polling with SSE" && git push
```

### #27: Add React Error Boundary
```bash
cd workflow-dev
opencode run -- "Add React Error Boundary. Create frontend/components/ErrorBoundary.tsx with proper error handling UI. Wrap app in frontend/app/layout.tsx with ErrorBoundary. Show user-friendly error message with retry button."
git add . && git commit -m "feat: Add React Error Boundary" && git push
```

### #28: Add GitHub Actions CI/CD
```bash
cd workflow-dev
opencode run -- "Add GitHub Actions CI/CD. Create .github/workflows/ci.yml with jobs: lint (ruff for Python, ESLint for JS), type check (mypy for Python, tsc for TypeScript), backend tests (pytest), frontend build check (npm run build). Add pull_request and push triggers."
git add . && git commit -m "ci: Add GitHub Actions workflow" && git push
```

### #29: Increase test coverage
```bash
cd workflow-dev
opencode run -- "Increase test coverage. Add pytest.ini with testpaths=tests. Create tests/conftest.py with fixtures for mocking crews, API client, state. Add tests for: all 6 crews (researcher, planner, executor, reviewer, tester, deployer), API endpoints, state transitions, emitter pattern."
git add . && git commit -m "test: Add comprehensive test coverage" && git push
```

---

## Ralph-Starter Commands (Experimental)

If you want to try ralph-starter anyway:

```bash
# Test with GitHub (works better than Linear)
cd workflow-dev
ralph-starter run --from github --project Heldinhow/workflow-dev --issue 21 --commit --validate

# Auto mode - process all bug issues
ralph-starter auto --source github --project Heldinhow/workflow-dev --label bug --limit 5
```

---

## Quick Reference

```bash
# Clone (if needed)
git clone https://github.com/Heldinhow/workflow-dev.git && cd workflow-dev

# Run each command sequentially
opencode run -- "TASK DESCRIPTION"
git add . && git commit -m "MESSAGE" && git push
```
