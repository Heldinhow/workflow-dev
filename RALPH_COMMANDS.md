# Ralph-Loop Commands for workflow-dev

All commands point to Linear issues. Run directly from the project directory.

## Setup

```bash
# Clone the repo
git clone https://github.com/Heldinhow/workflow-dev.git
cd workflow-dev

# Configure git (first time)
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
```

## Linear Source Configuration

The Linear CLI is already configured. To use `--from linear`, configure:

```bash
# Set your Linear API key
linear config set linear.apiKey YOUR_API_KEY

# Test connection
linear source test linear
```

---

## Complete Commands (Priority Order)

### 🔴 CRITICAL - Fix These First

```bash
# HEL-8: Fix Makefile hardcoded path
ralph-starter run "Fix the Makefile to use portable paths. The current Makefile has hardcoded '/Users/helder/Projetos/workflow-dev'. Use \$(shell git rev-parse --show-toplevel) to dynamically detect project root. Make 'make api', 'make ui', and 'make dev' work from any directory." --from linear --issue 8 --commit --validate

# HEL-9: Fix Frontend API empty string (Frontend can't connect to Backend)
ralph-starter run "Fix the frontend API configuration. In frontend/app/page.tsx, const API = '' is empty, making all fetch requests go to /api/* on Next.js server instead of http://localhost:8000. Create frontend/next.config.mjs with rewrites proxy for /api/* to http://localhost:8000. Remove the empty API variable and update all fetch calls to use /api/* directly." --from linear --issue 9 --commit --validate

# HEL-11: Create comprehensive README.md
ralph-starter run "Create a comprehensive README.md for workflow-dev project. Include: project description, architecture diagram (text-based showing the flow: Idea → Researcher → Planner → Executor → Reviewer → Tester → Deployer), quick start instructions (clone, setup .env, make dev), development commands (make api, make ui), environment variables table, API documentation (endpoints), and tech stack. Use proper markdown with badges." --from linear --issue 11 --commit
```

### 🟡 HIGH PRIORITY

```bash
# HEL-10: Create .env.example files
ralph-starter run "Create .env.example files documenting all required environment variables. Root .env.example should have: MINIMAX_API_KEY, MINIMAX_MODEL (default: minimax-m2.7-highspeed), MINIMAX_API_BASE (https://api.minimax.io/v1), BRAVE_API_KEY (optional), API_PORT (8000), API_HOST (0.0.0.0). Frontend .env.example should document NEXT_PUBLIC_API_URL if needed. Also add .env entries to .gitignore." --from linear --issue 10 --commit

# HEL-16: Increase test coverage
ralph-starter run "Increase test coverage for workflow-dev. Currently only 2 basic tests exist. Add pytest.ini configuration. Create tests/conftest.py with fixtures for mocking crews, API client, and state. Add comprehensive tests for: all 6 crews (researcher, planner, executor, reviewer, tester, deployer), API endpoints in tests/test_api.py, state transitions in tests/test_state.py, and emitter pattern in tests/test_emitter.py." --from linear --issue 16 --commit --validate

# HEL-12: Add docker-compose.yml
ralph-starter run "Add docker-compose.yml for easy local development. Create services for: api (FastAPI on port 8000), ui (Next.js on port 3000), postgres (for development), redis (optional). Create Dockerfile.api and Dockerfile.ui. Add docker-up, docker-down, docker-logs targets to Makefile. Use environment variables for configuration." --from linear --issue 12 --commit
```

### 🟢 MEDIUM PRIORITY

```bash
# HEL-13: Replace polling with SSE
ralph-starter run "Replace setInterval polling with SSE in the frontend. The backend already supports SSE at /api/executions/{id}/events. Create frontend/lib/sse.ts with useExecutionEvents hook using EventSource. Update frontend/app/page.tsx and frontend/app/executions/[id]/page.tsx to use the hook instead of setInterval(fetchAll, 5000)." --from linear --issue 13 --commit --validate

# HEL-14: Add React Error Boundary
ralph-starter run "Add React Error Boundary to the frontend. Create frontend/components/ErrorBoundary.tsx with proper error handling UI. Wrap the app in frontend/app/layout.tsx with the ErrorBoundary. Show user-friendly error message with retry button when errors occur." --from linear --issue 14 --commit

# HEL-15: Add GitHub Actions CI/CD
ralph-starter run "Add GitHub Actions CI/CD pipeline. Create .github/workflows/ci.yml with jobs for: lint (Python ruff, JS ESLint), type check (mypy for Python, tsc for TypeScript), backend tests (pytest), frontend build check (npm run build). Add pull_request and push triggers. Use matrix strategy for Python versions." --from linear --issue 15 --commit
```

### ⚪ LOW PRIORITY

```bash
# HEL-17: Add .editorconfig
ralph-starter run "Add .editorconfig for consistent formatting across editors. Settings for: Python files (indent_size=4), TypeScript/JS files (indent_size=2), YAML files (indent_size=2), markdown files (indent_size=2), end_of_line=lf, charset=utf-8, trim_trailing_whitespace=true." --from linear --issue 17 --commit
```

---

## Batch Commands

### Run all CRITICAL issues:
```bash
ralph-starter run "Fix HEL-8: Fix the Makefile to use portable paths..." --from linear --issue 8 --commit --validate && \
ralph-starter run "Fix HEL-9: Fix the frontend API empty string..." --from linear --issue 9 --commit --validate && \
ralph-starter run "Create HEL-11: Comprehensive README.md..." --from linear --issue 11 --commit
```

### Run with Auto Mode:
```bash
# Process all Bug labeled issues
ralph-starter auto --source linear --label "bug" --limit 5 --commit --validate

# Process all Improvement labeled issues
ralph-starter auto --source linear --label "Improvement" --limit 10 --commit

# Process all issues
ralph-starter auto --source linear --limit 20 --commit
```

### Sequential by Priority:
```bash
# Priority 1 (CRITICAL)
ralph-starter run "$(cat << 'EOF'
Fix HEL-8 and HEL-9 in this task:
1. HEL-8: Replace Makefile hardcoded '/Users/helder/Projetos/workflow-dev' with \$(shell git rev-parse --show-toplevel)
2. HEL-9: Create frontend/next.config.mjs with API proxy, remove empty const API = '', update fetch calls
Commit after each fix.
EOF
)" --from linear --label "bug" --commit --validate --max-iterations 40

# Priority 2
ralph-starter run "$(cat << 'EOF'
Complete HEL-10, HEL-11, HEL-16:
1. HEL-10: Create .env.example files for root and frontend
2. HEL-11: Create comprehensive README.md with badges, architecture diagram, quick start
3. HEL-16: Add pytest.ini, conftest.py, and comprehensive tests
EOF
)" --from linear --label "Improvement" --commit --validate --max-iterations 50
```

---

## Quick Start (Copy & Paste)

```bash
# 1. Clone
git clone https://github.com/Heldinhow/workflow-dev.git && cd workflow-dev

# 2. Fix Critical Issues
ralph-starter run "Fix HEL-8: Replace hardcoded Makefile path with \$(shell git rev-parse --show-toplevel)" --from linear --issue 8 --commit --validate
ralph-starter run "Fix HEL-9: Create next.config.mjs with API proxy, fix frontend fetch calls" --from linear --issue 9 --commit --validate
ralph-starter run "Create HEL-11: README.md with architecture, quick start, API docs" --from linear --issue 11 --commit

# 3. High Priority
ralph-starter run "HEL-10: Create .env.example files" --from linear --issue 10 --commit
ralph-starter run "HEL-16: Add pytest.ini, conftest.py, comprehensive tests" --from linear --issue 16 --commit --validate
ralph-starter run "HEL-12: Add docker-compose.yml, Dockerfiles" --from linear --issue 12 --commit

# 4. Medium Priority
ralph-starter run "HEL-13: Replace polling with SSE hook" --from linear --issue 13 --commit --validate
ralph-starter run "HEL-14: Add React Error Boundary" --from linear --issue 14 --commit
ralph-starter run "HEL-15: Add GitHub Actions CI/CD" --from linear --issue 15 --commit

# 5. Low Priority
ralph-starter run "HEL-17: Add .editorconfig" --from linear --issue 17 --commit
```

---

## Labels Available

| Label | Color | Issues |
|-------|-------|--------|
| Bug | Red | HEL-8, HEL-9 |
| Improvement | Blue | HEL-10, HEL-11, HEL-12, HEL-13, HEL-14, HEL-15, HEL-16, HEL-17 |

---

## Notes

- All commands use `--commit` for auto-commits
- Add `--validate` for tests/lint validation
- Add `--push` to push commits immediately
- Use `--max-iterations 30-50` for larger tasks
- The `--from linear` flag fetches issue details automatically
