# Ralph Tasks Mode Commands for workflow-dev

Tasks Mode permite processar múltiplas tasks automaticamente.

---

## Criar Task List para Issues

Copia e cola cada bloco para criar as tasks:

```bash
# Criar tasks para todos os issues
cat > .ralph/ralph-tasks.md << 'EOF'
# Ralph Tasks - workflow-dev

## Setup
- [ ] HEL-10: Create .env.example files

## Infrastructure  
- [ ] HEL-12: Add docker-compose.yml

## Frontend
- [ ] HEL-9: Fix Frontend API empty string
- [ ] HEL-13: Replace polling with SSE
- [ ] HEL-14: Add React Error Boundary

## Documentation
- [ ] HEL-11: Create comprehensive README.md

## CI/CD
- [ ] HEL-15: Add GitHub Actions CI/CD

## Testing
- [ ] HEL-16: Increase test coverage
EOF

# Criar tasks para .env.example
cat > .ralph/ralph-tasks.md << 'EOF'
# Ralph Tasks - .env.example

- [ ] Create root .env.example with MINIMAX_API_KEY, MINIMAX_MODEL, MINIMAX_API_BASE, BRAVE_API_KEY, API_PORT, API_HOST
- [ ] Create frontend/.env.example with NEXT_PUBLIC_API_URL
- [ ] Add .env entries to .gitignore
EOF
```

---

## Comandos Ralph Tasks

### Modo Interativo (criar tasks manualmente)

```bash
# Criar uma task
ralph --add-task "Create .env.example with all required variables"

# Listar tasks
ralph --list-tasks

# Remover task
ralph --remove-task 1

# Ver status
ralph --status
```

### Modo Batch (com task file)

```bash
# Criar task file primeiro
mkdir -p .ralph

# Opção 1: Tasks Mode com arquivo
ralph "Complete all tasks in ralph-tasks.md" --tasks --max-iterations 50

# Opção 2: Uma task de cada vez
ralph "Task 1: Create .env.example" --max-iterations 10
ralph "Task 2: Create frontend .env.example" --max-iterations 10
```

---

## Comandos Completos para Cada Issue

```bash
# HEL-9: Fix Frontend API
ralph "Fix the frontend API. In frontend/app/page.tsx, const API = '' is empty making fetch go to /api/* on Next.js instead of localhost:8000. Create frontend/next.config.mjs with rewrites proxy for /api/* to http://localhost:8000. Remove empty API variable. Update all fetch calls to use /api/* directly. Output COMPLETE when done." --max-iterations 15

# HEL-10: .env.example
ralph "Create .env.example files. Root: MINIMAX_API_KEY, MINIMAX_MODEL=minimax-m2.7-highspeed, MINIMAX_API_BASE=https://api.minimax.io/v1, BRAVE_API_KEY, API_PORT=8000, API_HOST=0.0.0.0. Frontend: NEXT_PUBLIC_API_URL. Add .env entries to .gitignore. Output COMPLETE when done." --max-iterations 10

# HEL-11: README.md
ralph "Create comprehensive README.md. Include: badges (Python, License), project description, architecture diagram (text-based: Idea→Researcher→Planner→Executor→Reviewer→Tester→Deployer), quick start (clone, cp .env.example .env, make dev), development commands (make api, make ui), environment variables table, API documentation (GET/POST /api/executions, SSE endpoint), tech stack. Output COMPLETE when done." --max-iterations 15

# HEL-12: docker-compose.yml
ralph "Add docker-compose.yml for local development. Services: api (FastAPI port 8000), ui (Next.js port 3000), postgres (5432), redis (6379). Create Dockerfile.api and Dockerfile.ui. Add docker-up, docker-down, docker-logs to Makefile. Output COMPLETE when done." --max-iterations 20

# HEL-13: SSE
ralph "Replace polling with SSE. Backend supports SSE at /api/executions/{id}/events. Create frontend/lib/sse.ts with useExecutionEvents hook using EventSource. Update frontend/app/page.tsx and frontend/app/executions/[id]/page.tsx to use the hook instead of setInterval(fetchAll, 5000). Output COMPLETE when done." --max-iterations 15

# HEL-14: Error Boundary
ralph "Add React Error Boundary. Create frontend/components/ErrorBoundary.tsx with proper error handling UI. Wrap app in frontend/app/layout.tsx with ErrorBoundary. Show user-friendly error message with retry button. Output COMPLETE when done." --max-iterations 10

# HEL-15: GitHub Actions
ralph "Add GitHub Actions CI/CD. Create .github/workflows/ci.yml with jobs: lint (ruff for Python, ESLint for JS), type check (mypy for Python, tsc for TypeScript), backend tests (pytest), frontend build check (npm run build). Add pull_request and push triggers. Output COMPLETE when done." --max-iterations 20

# HEL-16: Test Coverage
ralph "Increase test coverage. Add pytest.ini with testpaths=tests. Create tests/conftest.py with fixtures for mocking crews, API client, state. Add tests for: all 6 crews (researcher, planner, executor, reviewer, tester, deployer), API endpoints, state transitions, emitter pattern. Output COMPLETE when done." --max-iterations 25
```

---

## Comandos com Auto-Commit

```bash
# Cada comando = uma issue
ralph "HEL-9: Fix the frontend API..." --max-iterations 15 && git add . && git commit -m "fix: Frontend API proxy" && git push
ralph "HEL-10: Create .env.example..." --max-iterations 10 && git add . && git commit -m "feat: Add .env.example" && git push
ralph "HEL-11: Create README.md..." --max-iterations 15 && git add . && git commit -m "docs: Add README" && git push
```

---

## Tasks Mode (Avançado)

```bash
# Criar tasks file
mkdir -p .ralph

# Com tasks format
ralph "Implement all workflow-dev improvements" --tasks --max-iterations 100

# Listar tasks atuais
ralph --list-tasks

# Ver status do loop
ralph --status

# Adicionar context mid-loop
ralph --add-context "Focus on the API proxy first"

# Limpar context
ralph --clear-context
```

---

## Exemplo: Criar Tasks File

```bash
mkdir -p .ralph

cat > .ralph/ralph-tasks.md << 'TASKS'
# workflow-dev Improvements

## Critical
- [ ] Fix frontend API empty string (HEL-9)
- [ ] Create .env.example (HEL-10)

## High
- [ ] Create README.md (HEL-11)
- [ ] Add docker-compose (HEL-12)
- [ ] Increase test coverage (HEL-16)

## Medium
- [ ] Replace polling with SSE (HEL-13)
- [ ] Add Error Boundary (HEL-14)
- [ ] Add GitHub Actions (HEL-15)
TASKS

# Executar tasks mode
ralph "Implement all tasks from ralph-tasks.md" --tasks --max-iterations 100
```

---

## Quick Copy & Paste

```bash
# HEL-9: Frontend API
ralph "Fix the frontend API. const API = '' is empty. Create next.config.mjs with proxy. Output COMPLETE." --max-iterations 15

# HEL-10: .env.example
ralph "Create .env.example files with MINIMAX_API_KEY, MINIMAX_MODEL, API_PORT, etc. Output COMPLETE." --max-iterations 10

# HEL-11: README.md
ralph "Create README.md with badges, architecture, quick start, commands, API docs. Output COMPLETE." --max-iterations 15

# HEL-12: Docker
ralph "Add docker-compose.yml with api, ui, postgres, redis services. Output COMPLETE." --max-iterations 20

# HEL-13: SSE
ralph "Replace setInterval polling with SSE EventSource hook. Output COMPLETE." --max-iterations 15

# HEL-14: Error Boundary
ralph "Add React ErrorBoundary component. Output COMPLETE." --max-iterations 10

# HEL-15: GitHub Actions
ralph "Add .github/workflows/ci.yml with lint, typecheck, tests. Output COMPLETE." --max-iterations 20

# HEL-16: Tests
ralph "Increase pytest coverage. Add conftest.py fixtures. Test all crews. Output COMPLETE." --max-iterations 25
```
