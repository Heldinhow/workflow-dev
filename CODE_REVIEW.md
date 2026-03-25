# Code Review - workflow-dev

## ✅ JÁ IMPLEMENTADO (PRs merged #30-#38)

| Ficheiro | Status | Notes |
|-----------|--------|-------|
| Makefile | ✅ Corrigido | Paths portáteis |
| frontend/app/page.tsx | ✅ Corrigido | API variable |
| frontend/next.config.mjs | ✅ Criado | Proxy configurado |
| .env.example | ✅ Criado | Vars documentadas |
| README.md | ✅ Criado | Completo |
| docker-compose.yml | ✅ Criado | 4 serviços |
| Dockerfile.api | ✅ Criado | |
| Dockerfile.ui | ✅ Criado | |
| frontend/lib/sse.ts | ✅ Criado | EventSource hook |
| frontend/components/ErrorBoundary.tsx | ✅ Criado | |
| .github/workflows/ci.yml | ✅ Criado | 6 jobs |
| pytest.ini | ✅ Criado | |
| tests/ | ✅ Criado | 4 ficheiros |

---

## ❌ AINDA FALTA / PROBLEMAS

### 🔴 CRÍTICOS

#### 1. ShellTool com shell=True (SECURITY)
**Ficheiro:** `src/dev_workflow/tools/shell_tool.py`
**Problema:** `subprocess.run(command, shell=True)` permite command injection
**Impacto:** Qualquer input pode executar comandos arbitrários

#### 2. Executor Crew NÃO cria ficheiros
**Ficheiro:** `src/dev_workflow/crews/executor/`
**Problema:** O executor diz que usa FileWriterTool mas no flow apenas retorna texto
**Impacto:** Workflow cria planos mas não código

#### 3. max_retries não é usado
**Ficheiro:** `src/dev_workflow/api/server.py`
**Problema:** `max_retries` é guardado mas nunca passado ao flow
**Impacto:** Não há retry real

---

### 🟡 MÉDIOS

#### 4. LinearTool com bug de autenticação
**Ficheiro:** `src/dev_workflow/tools/linear_tool.py`
**Problema:** `if " LINEAR_API_KEY" in os.environ` (espaço!)
**Impacto:** Auth check sempre falha

#### 5. Store em memória
**Ficheiro:** `src/dev_workflow/api/store.py`
**Problema:** Dados em memória, perdidos no restart
**Impacto:** Executions perdem estado

#### 6. Cancellation não para thread
**Ficheiro:** `src/dev_workflow/api/server.py`
**Problema:** `/cancel` marca como cancelled mas thread continua
**Impacto:** Recursos gastos em threads órfãs

#### 7. Sem graceful shutdown
**Ficheiro:** `src/dev_workflow/api/server.py`
**Problema:** SIGTERM/SIGINT não tratados
**Impacto:** Executions órfãs no shutdown

#### 8. Sem rate limiting
**Ficheiro:** `src/dev_workflow/api/server.py`
**Problema:** Endpoint acessível sem limites
**Impacto:** DOS potential

#### 9. Sem /health endpoint
**Ficheiro:** `src/dev_workflow/api/server.py`
**Problema:** Coolify não consegue verificar saúde
**Impacto:** Deploys falham

#### 10. Sem OpenAPI docs
**Ficheiro:** `src/dev_workflow/api/server.py`
**Problema:** Swagger mencionado mas não configurado
**Impacto:** Sem documentação de API

---

### 🟢 MENORES

#### 11. Sem timeout global
**Ficheiro:** `src/dev_workflow/flow.py`
**Problema:** Execution pode correr para sempre
**Impacto:** Recursos presos

#### 12. Sem logging estruturado
**Ficheiro:** `src/dev_workflow/`
**Problema:** Logs não estruturados, sem correlation ID
**Impacto:** Dificil debugar

#### 13. Sem dark/light mode
**Ficheiro:** `frontend/`
**Problema:** Só dark theme
**Impacto:** UX limitada

#### 14. SSE sem reconnection
**Ficheiro:** `frontend/lib/sse.ts`
**Problema:** Não reconecta se ligação cair
**Impacto:** UX poor em connections instáveis

#### 15. Sem E2E tests
**Ficheiro:** `tests/`
**Problema:** Só unit tests
**Impacto:** Não sabemos se fluxo completo funciona

---

## 📊 RESUMO

| Severidade | Count |
|------------|-------|
| 🔴 CRÍTICO | 3 |
| 🟡 MÉDIO | 7 |
| 🟢 MENOR | 5 |
| **TOTAL** | **15** |

---

## 🎯 PRIORIDADES SUGERIDAS

### Fase 1: Segurança + Core (CRÍTICO)
1. 🔴 ShellTool security (shell=False)
2. 🔴 Executor cria ficheiros
3. 🔴 max_retries usado

### Fase 2: Infraestrutura (MÉDIO)
4. LinearTool auth bug
5. Cancellation real
6. Graceful shutdown
7. Rate limiting
8. /health endpoint

### Fase 3: Observability (MÉDIO)
9. Logging estruturado
10. Timeout global

### Fase 4: UX (MENOR)
11. SSE reconnection
12. Dark/light mode
13. OpenAPI docs
14. E2E tests
15. Persistence (DB)
