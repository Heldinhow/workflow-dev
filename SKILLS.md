# Skills para Workflow Dev

Este documento lista as skills disponíveis para desenvolvimento do projeto workflow-dev.

## Skills Criadas (Custom)

### 1. `crewai-workflow-orchestrator`
**Path:** `~/.config/opencode/skills/crewai-workflow-orchestrator/SKILL.md`

Padrões de orquestração multi-agent usando CrewAI:
- Flow State Management com Pydantic
- Retry loops com feedback entre agents
- Event-driven architecture
- Crew configuration com YAML
- Phase lifecycle patterns

**Quando usar:**
- Implementar novo workflow de agentes
- Adicionar novas fases ao pipeline
- Modificar retry logic
- Desenhar comunicação entre agentes

**Conteúdo:**
- Padrão 1: Flow State Management
- Padrão 2: Retry Loops com Feedback
- Padrão 3: Structured Outputs
- Padrão 4: Event-Driven Architecture
- Padrão 5: Crew Configuration
- Padrão 6: Phase Lifecycle

---

### 2. `workflow-observability`
**Path:** `~/.config/opencode/skills/workflow-observability/SKILL.md`

Observabilidade para workflows AI:
- Prometheus metrics (counters, histograms, gauges)
- Structured logging com structlog
- OpenTelemetry tracing
- DORA metrics
- Alerting rules para Prometheus
- Grafana dashboard

**Quando usar:**
- Adicionar métricas ao projeto
- Implementar logging estruturado
- Criar tracing distribuído
- Configurar alertas
- Desenhar dashboard de monitoring

**Conteúdo:**
- Pattern 1: Prometheus Metrics
- Pattern 2: Structured Logging
- Pattern 3: OpenTelemetry Tracing
- Pattern 4: DORA Metrics
- Pattern 5: Alerting Rules
- Pattern 6: Grafana Dashboard

---

### 3. `workflow-api-design`
**Path:** `~/.config/opencode/skills/workflow-api-design/SKILL.md`

FastAPI patterns para APIs de workflow:
- Thread-safe ExecutionStore
- Server-Sent Events (SSE) streaming
- Background task execution
- Cancellation support
- Request/Response models com Pydantic
- CORS e middleware

**Quando usar:**
- Criar novos endpoints de API
- Implementar streaming em tempo real
- Adicionar suporte a cancelamento
- Desenhar modelos de request/response
- Configurar middleware

**Conteúdo:**
- Pattern 1: Execution Store
- Pattern 2: SSE Streaming
- Pattern 3: Background Task Execution
- Pattern 4: Cancellation Support
- Pattern 5: Request/Response Models
- Pattern 6: CORS and Middleware

---

### 4. `shell-sandboxing`
**Path:** `~/.config/opencode/skills/shell-sandboxing/SKILL.md`

Shell command sandboxing e segurança:
- Command allowlisting
- Timeout e resource limits
- Audit logging
- Docker sandboxing
- Content scanning
- ShellTool integration para CrewAI

**Quando usar:**
- Implementar shell tool seguro
- Adicionar allowlist de comandos
- Configurar timeout
- Criar audit trail
- Isolar execução em containers

**Conteúdo:**
- Pattern 1: Command Allowlisting
- Pattern 2: Timeout and Resource Limits
- Pattern 3: Audit Logging
- Pattern 4: Shell Tool Integration
- Pattern 5: Docker Sandboxing
- Pattern 6: Content Scanning

---

## Skills Existentes (Disponíveis no awesome-copilot)

### Agent Governance
**Repo:** `github/awesome-copilot/skills/agent-governance`

Padrões para governança, safety e trust controls:
- Policy-based access controls
- Semantic intent classification
- Tool-level governance decorator
- Trust scoring systems
- Audit trail
- Framework integration (CrewAI, PydanticAI, etc.)

**Use para:** Adicionar segurança e governança aos agentes.

---

### Agentic Eval
**Repo:** `github/awesome-copilot/skills/agentic-eval`

Padrões para avaliar e melhorar outputs de AI:
- Self-critique e reflection loops
- Evaluator-optimizer pipelines
- Code-specific reflection
- LLM-as-Judge evaluation
- Rubric-based scoring

**Use para:** Implementar loops de avaliação nos agentes Reviewer e Tester.

---

### Autoresearch
**Repo:** `github/awesome-copilot/skills/autoresearch`

Autonomous iterative experimentation loop:
- Goal and metric definition
- Experiment loop (think → edit → commit → run → measure → decide)
- Baseline measurement
- Simplicity criterion

**Use para:** Workflows de otimização automática.

---

### Expert Next.js Developer
**Repo:** `github/awesome-copilot/skills/expert-nextjs-developer.agent.md`

Padrões avançados de Next.js:
- App Router patterns
- Server/Client Components
- Data fetching strategies
- Middleware e auth
- Cache Components (`use cache`)
- React 19.2 features

**Use para:** Desenvolver features no frontend Next.js.

---

### Python MCP Server Expert
**Repo:** `github/awesome-copilot/skills/python-mcp-expert.agent.md`

Padrões para MCP servers em Python:
- FastMCP usage
- Tool design com Pydantic
- Structured output
- Context usage (logging, progress)
- Transport setup (stdio, HTTP)

**Use para:** Criar MCP servers para integrar ferramentas.

---

### Cloud Design Patterns
**Repo:** `github/awesome-copilot/skills/cloud-design-patterns`

42 padrões de sistemas distribuídos:
- Reliability patterns
- Performance patterns
- Messaging patterns
- Security patterns
- Deployment patterns

**Use para:** Arquitetura de sistemas distribuídos.

---

### Code Review
**Repo:** `~/.config/opencode/skills/code-review/SKILL.md`

Padrões para code review estruturado:
- Correctness, security, performance checks
- Readability and test coverage
- Structured review framework

**Use para:** Criar checklist de code review.

---

### TDD / Test-Driven Development
**Repo:** `~/.config/opencode/skills/TDD/SKILL.md`

Padrões TDD:
- Red-green-refactor cycle
- Test structure
- Mocking patterns

**Use para:** Adicionar testes ao projeto.

---

## Roadmap de Skills

### Fase 1: Fundamentos (Já criado)
- [x] `crewai-workflow-orchestrator`
- [x] `workflow-api-design`
- [x] `workflow-observability`
- [x] `shell-sandboxing`

### Fase 2: Melhorias de Agentes (Skills existentes)
- [ ] Usar `agent-governance` para segurança
- [ ] Usar `agentic-eval` para loops de avaliação
- [ ] Usar `code-review` para checklist

### Fase 3: Frontend
- [ ] Usar `expert-nextjs-developer` para patterns avançados
- [ ] Criar skill específica para SSE + real-time UI

### Fase 4: Infraestrutura
- [ ] Usar `prometheus-monitoring` para métricas
- [ ] Usar `cloud-design-patterns` para arquitetura

---

## Como Usar

Para carregar uma skill durante conversa:

```
Use a skill [nome-da-skill] quando [cenário de uso]
```

Exemplo:
```
Use a skill crewai-workflow-orchestrator quando implementar nova fase no workflow
```

---

## Referências

- **Agent Skills Spec:** https://agentskills.io/specification
- **Awesome Copilot:** https://github.com/github/awesome-copilot
- **CrewAI Docs:** https://docs.crewai.com/
