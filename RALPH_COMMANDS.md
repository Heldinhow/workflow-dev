# Ralph Wiggum Commands for workflow-dev

**Ralph Wiggum:** `ralph "prompt"` — loop iterativo até COMPLETE

---

## Comandos Completos

### HEL-8: Fix Makefile ✅ DONE

```bash
# Já feito - commitado como 347882f
```

---

### HEL-9: Fix Frontend API empty string

```bash
ralph "Fix the frontend API. In frontend/app/page.tsx, const API = '' is empty making fetch go to /api/* on Next.js instead of localhost:8000. Create frontend/next.config.mjs with rewrites proxy for /api/* to http://localhost:8000. Remove empty API variable. Update all fetch calls to use /api/* directly. Output COMPLETE when done." --max-iterations 10
git add . && git commit -m "fix: Frontend API proxy to backend" && git push
```

---

### HEL-10: Create .env.example

```bash
ralph "Create .env.example files. Root: MINIMAX_API_KEY, MINIMAX_MODEL=minimax-m2.7-highspeed, MINIMAX_API_BASE=https://api.minimax.io/v1, BRAVE_API_KEY, API_PORT=8000, API_HOST=0.0.0.0. Frontend: NEXT_PUBLIC_API_URL. Add .env entries to .gitignore. Output COMPLETE when done." --max-iterations 10
git add . && git commit -m "feat: Add .env.example files" && git push
```

---

### HEL-11: Create README.md

```bash
ralph "Create comprehensive README.md. Include: badges (Python, License), project description, architecture diagram (text-based: Idea→Researcher→Planner→Executor→Reviewer→Tester→Deployer), quick start (clone, cp .env.example .env, make dev), development commands (make api, make ui), environment variables table, API documentation (GET/POST /api/executions, SSE endpoint), tech stack. Output COMPLETE when done." --max-iterations 10
git add . && git commit -m "docs: Add comprehensive README" && git push
```

---

### HEL-12: Add docker-compose.yml

```bash
ralph "Add docker-compose.yml for local development. Services: api (FastAPI port 8000), ui (Next.js port 3000), postgres (5432), redis (6379). Create Dockerfile.api and Dockerfile.ui. Add docker-up, docker-down, docker-logs to Makefile. Output COMPLETE when done." --max-iterations 15
git add . && git commit -m "feat: Add Docker Compose for local dev" && git push
```

---

### HEL-13: Replace polling with SSE

```bash
ralph "Replace polling with SSE. Backend supports SSE at /api/executions/{id}/events. Create frontend/lib/sse.ts with useExecutionEvents hook using EventSource. Update frontend/app/page.tsx and frontend/app/executions/[id]/page.tsx to use the hook instead of setInterval(fetchAll, 5000). Output COMPLETE when done." --max-iterations 15
git add . && git commit -m "feat: Replace polling with SSE" && git push
```

---

### HEL-14: Add React Error Boundary

```bash
ralph "Add React Error Boundary. Create frontend/components/ErrorBoundary.tsx with proper error handling UI. Wrap app in frontend/app/layout.tsx with ErrorBoundary. Show user-friendly error message with retry button. Output COMPLETE when done." --max-iterations 10
git add . && git commit -m "feat: Add React Error Boundary" && git push
```

---

### HEL-15: Add GitHub Actions CI/CD

```bash
ralph "Add GitHub Actions CI/CD. Create .github/workflows/ci.yml with jobs: lint (ruff for Python, ESLint for JS), type check (mypy for Python, tsc for TypeScript), backend tests (pytest), frontend build check (npm run build). Add pull_request and push triggers. Output COMPLETE when done." --max-iterations 15
git add . && git commit -m "ci: Add GitHub Actions workflow" && git push
```

---

### HEL-16: Increase test coverage

```bash
ralph "Increase test coverage. Add pytest.ini with testpaths=tests. Create tests/conftest.py with fixtures for mocking crews, API client, state. Add tests for: all 6 crews (researcher, planner, executor, reviewer, tester, deployer), API endpoints, state transitions, emitter pattern. Run pytest to verify. Output COMPLETE when done." --max-iterations 20
git add . && git commit -m "test: Add comprehensive test coverage" && git push
```

---

## Quick Reference

| Flag | O que faz |
|------|-----------|
| `--max-iterations N` | Limite de iterações |
| `--no-commit` | Não fazer commit automático |
| `--tasks` | Modo tasks (lista de tarefas) |
| `--status` | Ver estado do loop |
| `--add-context "hint"` | Adicionar dica mid-loop |

## Syntax

```bash
# Basic
ralph "Your task description. Output COMPLETE when done." --max-iterations 10

# With commit (default is auto-commit!)
ralph "Your task" --max-iterations 10
git add . && git commit -m "message" && git push

# Tasks mode
ralph "Build a full-stack app" --tasks --max-iterations 50
```

## Notes

- **Output COMPLETE** or `<promise>COMPLETE</promise>` to end the loop
- Default is `--no-commit` = auto-commit (mas pode não funcionar sem config git)
- Sempre fazer `git add . && git commit` depois

## Git Config (importante!)

```bash
git config --global user.email "you@email.com"
git config --global user.name "Your Name"
```
