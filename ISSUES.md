# GitHub Issues - Workflow Dev Multi-Agent Orchestrator

## Issues Criadas

### ✅ Já criadas no GitHub
1. **#1** `[P0] Fix API Port Mismatch` - Frontend não conecta ao Backend
2. **#2** `[P0] Adicionar persistência ao store de execuções`
3. **#3** `[P1] Frontend: Adicionar cancelamento de execuções`
4. **#4** `[P1] Adicionar recovery de workflows após restart`
5. **#5** `[P1] Frontend: Busca e filtros no histórico de execuções`
6. **#6** `[P1] Logs em tempo real: adicionar busca e filtros`

---

## Issues Pendentes (criar manualmente)

### [P0] Adicionar autenticação e autorização
```markdown
## Problema
API e frontend não têm nenhum mecanismo de autenticação. Qualquer pessoa pode:
- Ver todas as execuções
- Iniciar novas execuções
- Cancelar workflows
- Acessar código/source de projetos

## Riscos
- Acesso não autorizado a código proprietary
- Abuso de recursos (custo de LLM)
- Sem accountability/audit

## Proposta
1. Autenticação via API key (simples para início)
2. JWT tokens para sessões
3. RBAC básico (admin vs viewer)

## Tasks
- [ ] Desenhar modelo de permissões
- [ ] Implementar auth middleware
- [ ] Adicionar login/logout no frontend
- [ ] Proteger todas as rotas
```

### [P2] Shell Tool: isolar e proteger execução de comandos
```markdown
## Problema de Segurança
`ShellTool` executa comandos arbitrários no sistema host. Riscos:
- Acesso ao sistema de arquivos completo
- Possibilidade de executar comandos destrutivos
- Sem timeout configurável

## Recomendação
1. **Sandbox**: usar containers Docker ou gVisor
2. **Allowlist**: só permitir comandos específicos (git, npm, python)
3. **Timeout**: matar processos que excedam tempo limite
4. **Audit log**: logging completo de todos os comandos

## Tasks
- [ ] Mapear comandos necessários
- [ ] Criar allowlist
- [ ] Implementar timeout
- [ ] Adicionar logging estruturado
```

### [P2] Adicionar métricas e observabilidade (Prometheus + Grafana)
```markdown
## Métricas importantes
1. **Workflow metrics**: execuções por status, duração por fase, taxa de retry
2. **Agent metrics**: tempo por agente, tokens consumidos
3. **System metrics**: latência, SSE connections, memória/CPU

## Implementação
1. `/metrics` endpoint (Prometheus format)
2. prometheus-client
3. Dashboard Grafana
4. Alertas

## Tasks
- [ ] Adicionar prometheus-client
- [ ] Criar metrics endpoint
- [ ] Instrumentar código
- [ ] Dashboard Grafana
```

### [P2] Adicionar configuração de retries por execução
```markdown
## Feature
Usuários configuram max_retries antes de iniciar.

## UI
- Max retries (execution): 1-5, default 3
- Max retries (testing): 1-5, default 3

## API
```json
POST /api/executions
{
  "feature_request": "...",
  "project_path": "...",
  "max_retries": 3,
  "max_test_retries": 3
}
```

## Tasks
- [ ] Backend: adicionar campos ao schema
- [ ] Frontend: adicionar inputs no form
- [ ] Testar
```

### [P2] Deployer: implementar deploy real
```markdown
## Problema
Deployer apenas cria commits/PRs, não faz deploy real.

## Targets
- Vercel (frontend)
- AWS (EC2, ECS, Lambda)
- Docker registry
- npm publish

## Tasks
- [ ] Interface deployer abstrata
- [ ] Adapters (vercel, aws, docker)
- [ ] Mostrar URL do deploy no frontend
```

---

## Issues Futuras (Nice to Have)

### [P3] Histórico de projetos por workspace
### [P3] Webhook para notificações externas (Slack, Discord)
### [P3] DSL para definição de workflows customizados
### [P3] Multi-tenant / namespaces
### [P3] Replay de execuções passadas (re-executar mesma config)
### [P3] Diff visual antes/depois das mudanças do Executor
### [P3] Exportar execução como PDF/HTML report

---

---

## [P1] Frontend: Redesign completo seguindo Design System profissional (baseado em Morphllm.com)

### Referência Visual
- **Site de referência**: https://www.morphllm.com/
- **Análise**: Design system moderno, dark theme elegante, tipografia clara, cards com bordas sutis, gradientes mínimos, hierarquia visual forte

### Problema
O frontend atual tem um design básico com:
- Paleta de cores limitada (apenas zinc com acentos emerald/blue/red)
- Sem identidade visual consistente
- Componentes sem sofisticação (badges simples, sem glows ou gradientes)
- Tipografia sem variação (apenas font-mono)
- Layout sem personalidade profissional

### Design System Proposto

#### 1. Paleta de Cores
```css
/* Cores Principais */
--bg-primary: #09090b      /* Zinc-950 - background principal */
--bg-secondary: #18181b     /* Zinc-900 - cards, surfaces */
--bg-tertiary: #27272a     /* Zinc-800 - borders, dividers */
--bg-elevated: #3f3f46     /* Zinc-700 - hover states */

/* Cores de Texto */
--text-primary: #fafafa     /* Zinc-50 */
--text-secondary: #a1a1aa   /* Zinc-400 */
--text-muted: #71717a      /* Zinc-500 */

/* Cores de Acento */
--accent-primary: #6366f1   /* Indigo-500 - CTAs principais */
--accent-primary-hover: #818cf8  /* Indigo-400 */
--accent-success: #10b981   /* Emerald-500 */
--accent-warning: #f59e0b   /* Amber-500 */
--accent-danger: #ef4444    /* Red-500 */
--accent-info: #3b82f6      /* Blue-500 */

/* Efeitos */
--glow-indigo: 0 0 20px rgba(99, 102, 241, 0.15)
--shadow-card: 0 1px 3px rgba(0,0,0,0.3), 0 1px 2px rgba(0,0,0,0.2)
```

#### 2. Tipografia
```css
/* Font Family */
--font-sans: 'Inter', system-ui, -apple-system, sans-serif;
--font-mono: 'JetBrains Mono', 'Fira Code', monospace;

/* Font Sizes - Escala modular */
--text-xs: 0.75rem;    /* 12px */
--text-sm: 0.875rem;   /* 14px */
--text-base: 1rem;     /* 16px */
--text-lg: 1.125rem;   /* 18px */
--text-xl: 1.25rem;    /* 20px */
--text-2xl: 1.5rem;    /* 24px */
--text-3xl: 1.875rem;  /* 30px */
--text-4xl: 2.25rem;   /* 36px */

/* Font Weights */
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
```

#### 3. Componentes a Implementar

##### Buttons
- Primary: bg-indigo-500, text-white, hover:bg-indigo-400, shadow com glow sutil
- Secondary: bg-zinc-800, text-zinc-100, hover:bg-zinc-700, border-zinc-700
- Ghost: transparent, text-zinc-400, hover:text-zinc-100, hover:bg-zinc-800/50
- Tamanhos: sm (h-8 px-3), md (h-10 px-4), lg (h-12 px-6)
- Border-radius: rounded-lg

##### Cards
- Background: bg-zinc-900
- Border: border border-zinc-800
- Border-radius: rounded-xl
- Shadow: shadow-lg com sombra sutil
- Hover: border-zinc-700 transition-colors

##### Status Badges
- Pending: bg-zinc-800/50 text-zinc-400
- Running: bg-blue-500/10 text-blue-400, com pulse animation e ring
- Completed: bg-emerald-500/10 text-emerald-400
- Failed: bg-red-500/10 text-red-400
- Escalated: bg-amber-500/10 text-amber-400
- Estilo: rounded-full, px-3 py-1, text-xs font-medium

##### Navigation
- Header: h-14, bg-zinc-950/80 com backdrop-blur
- Logo: usa indicador de status (dot) + nome estilizado
- Links: text-sm text-zinc-400 hover:text-zinc-100
- CTAs: buttons com estilo primário/secundário

##### Input Fields
- Background: bg-zinc-900
- Border: border border-zinc-700, focus:border-indigo-500
- Border-radius: rounded-lg
- Placeholder: text-zinc-500
- Font: sem font-mono para inputs de texto

##### Code Blocks
- Background: bg-zinc-950
- Border: border border-zinc-800
- Syntax highlighting style (similar ao site Morph)
- Line numbers: text-zinc-600
- Border-radius: rounded-lg

##### Tables
- Header: bg-zinc-900/50, text-xs font-medium text-zinc-500 uppercase
- Rows: hover:bg-zinc-900/40
- Border: border-b border-zinc-800
- Border-radius: rounded-lg no container

##### Metrics/Stats Cards
- Background: gradient sutil bg-zinc-900 to-zinc-900/50
- Border: border border-zinc-800
- Icon: com background em circle (bg-accent/10)
- Numbers: text-2xl font-bold
- Labels: text-sm text-zinc-500

### Tasks
- [ ] Criar Tailwind config extendido com novas cores e variáveis CSS
- [ ] Implementar Design System tokens em globals.css
- [ ] Criar componente Button (variants: primary, secondary, ghost, sizes)
- [ ] Criar componente Card com estados (default, hover)
- [ ] Atualizar StatusBadge com novos estilos (pills, glows)
- [ ] Redesenhar Header/Navigation com novo estilo
- [ ] Atualizar Inputs/Forms com novos estilos
- [ ] Criar componente CodeBlock para logs
- [ ] Criar componente StatsCard para métricas
- [ ] Redesenhar ExecutionCard com novo visual
- [ ] Adicionar animações e transições suaves
- [ ] Implementar loading states com skeleton screens
- [ ] Criar EmptyState componente
- [ ] Adicionar Toast/Notification system

### Referências de Implementação
- Inspiração: https://www.morphllm.com/ (dark theme, cards, tipografia)
- shadcn/ui components (Radix UI + Tailwind)
- https://ui.shadcn.com/

---

## [P1] Frontend: Implementar Layout profissional com Hero e Seções

### Problema
O frontend atual não tem landing page profissional. A página principal mostra apenas uma lista de execuções, sem:
- Hero section com valor do produto
- Social proof (logos de empresas)
- Features highlights
- CTAs claros

### Estrutura Proposta

```
┌─────────────────────────────────────────────────────┐
│  Header (nav + logo + auth)                         │
├─────────────────────────────────────────────────────┤
│  Hero Section                                       │
│  - Headline: "AI-Powered Development Workflow"     │
│  - Subheadline: descrição do produto               │
│  - CTA: "Start Execution" + "View Demo"            │
│  - Visual: abstract UI do dashboard                │
├─────────────────────────────────────────────────────┤
│  Social Proof                                       │
│  - "Trusted by X companies"                         │
│  - Logo grid (grayscale, hover color)               │
├─────────────────────────────────────────────────────┤
│  Features Grid                                      │
│  - Card per feature (pesquisa, planning, etc)      │
│  - Icon + title + description                      │
├─────────────────────────────────────────────────────┤
│  How it Works                                       │
│  - Timeline/steps do workflow                       │
│  - Visual diagram                                  │
├─────────────────────────────────────────────────────┤
│  Metrics/Stats Section                              │
│  - "10x faster", "98% accuracy", etc              │
├─────────────────────────────────────────────────────┤
│  CTA Final                                          │
│  - "Ready to start?"                              │
│  - Form rápido para trial                          │
├─────────────────────────────────────────────────────┤
│  Footer                                             │
│  - Links, social, copyright                        │
└─────────────────────────────────────────────────────┘
```

### Tasks
- [ ] Criar landing page com hero section
- [ ] Adicionar social proof section com logos
- [ ] Implementar features grid com cards
- [ ] Criar how-it-works section com visual diagram
- [ ] Adicionar metrics/stats showcase
- [ ] Criar footer profissional
- [ ] Implementar page de pricing (se não existir)
- [ ] Adicionar page de docs (se não existir)
- [ ] Responsive design para mobile

---

## [P1] Frontend: Component Library - StatusBadge v2 com Glow Effects

### Problema
StatusBadge atual é muito básico, sem personalidade visual.

### Novo Design (Morphllm-inspired)
```tsx
// StatusBadge com glow effect e pill style
// Running: bg-blue-500/10 text-blue-400 ring-1 ring-blue-500/20
// Completed: bg-emerald-500/10 text-emerald-400
// Failed: bg-red-500/10 text-red-400
// Escalated: bg-amber-500/10 text-amber-400
// Pending: bg-zinc-800/50 text-zinc-400
```

### Tasks
- [ ] Implementar StatusBadge v2 com novos estilos
- [ ] Adicionar glow/ring effects baseados no status
- [ ] Incluir ícone de loading spinner para running
- [ ] Criar variants: default, large (para detail pages)
- [ ] Adicionar tooltip com descrição do status

---

## [P2] Frontend: Dark Mode Premium com Gradientes Sutis

### Problema
Design atual é plano, sem profundidade ou sofisticação.

### Solução
Adicionar:
- Backgrounds com gradientes sutis (bg-gradient-to-b)
- Borders com glow em elementos importantes
- Shadows em camadas para profundidade
- Glass morphism em overlays/modais
- Backdrop blur em elementos flutuantes

### Tasks
- [ ] Adicionar CSS variables para gradientes
- [ ] Implementar glassmorphism utilities
- [ ] Criar elevated cards com múltiplas sombras
- [ ] Adicionar glow effects em CTAs importantes
- [ ] Implementar backdrop-blur em dropdowns/modais

---

## [P2] Frontend: Animações e Micro-interactions

### Problema
Interface estática, sem feedback visual dinâmico.

### Solução
Adicionar:
- Hover transitions suaves (150-200ms)
- Loading skeletons
- Stagger animations em listas
- Page transition hints
- Skeleton loading para async content
- Progress indicators animados

### Tasks
- [ ] Criar Skeleton component
- [ ] Implementar staggered list animations
- [ ] Adicionar page transition styles
- [ ] Criar ProgressBar animado
- [ ] Implementar fade-in/slide-up para conteúdo carregado

---

## [P2] Frontend: Design Responsivo Mobile-First

### Problema
Layout não é otimizado para mobile.

### Tasks
- [ ] Implementar breakpoints mobile-first
- [ ] Sidebar colapsável em mobile
- [ ] Table responsive (card view em mobile)
- [ ] Touch-friendly tap targets (min 44px)
- [ ] Bottom navigation para mobile
- [ ] Responsive typography scale

---

## [P3] Frontend: Empty States e Loading States Designer

### Problema
Falta tratamento visual para estados vazios e loading.

### Tasks
- [ ] Criar EmptyState component com ilustração
- [ ] Implementar Skeleton variants
- [ ] Criar NoResultsState para buscas
- [ ] Adicionar ErrorState com sugestões
- [ ] Implementar OfflineState

---

## [P3] Frontend: Sistema de Notificação Toast

### Problema
Sem feedback visual para ações do usuário.

### Tasks
- [ ] Criar Toast component (success, error, warning, info)
- [ ] Implementar toast store/hook
- [ ] Adicionar animações de entrada/saída
- [ ] Auto-dismiss com progress bar
- [ ] Toast para: execução iniciada, concluída, falha, cancelada

---

## Sugestão de Priorização

| Prioridade | Issue | Esforço | Impacto |
|------------|-------|---------|---------|
| P0 | Fix Port Mismatch | Low | Alto (bloqueante) |
| P0 | Persistência | Medium | Alto |
| P0 | Autenticação | Medium | Alto |
| P1 | Redesign Design System | High | Alto |
| P1 | Layout Profissional c/ Hero | Medium | Alto |
| P1 | StatusBadge v2 | Low | Médio |
| P1 | Cancelamento | Low | Médio |
| P1 | Recovery | Medium | Médio |
| P1 | Busca/Filtros | Medium | Médio |
| P1 | Log search | Medium | Médio |
| P2 | Dark Mode Premium | Medium | Médio |
| P2 | Animações | Medium | Médio |
| P2 | Responsive Mobile | Medium | Médio |
| P2 | Shell Security | High | Alto |
| P2 | Métricas | Medium | Médio |
| P2 | Retry config | Low | Baixo |
| P2 | Deploy real | High | Médio |
| P3 | Empty/Loading States | Low | Baixo |
| P3 | Toast Notifications | Low | Baixo |
