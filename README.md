# Spec-Driven Development

Sistema de agentes que transforma ideias em **sprints → tasks** executáveis,
com dashboard de terminal em tempo real, contratos formais entre executor e
QA por task, e captura de custo real em USD.

## O problema

Agentes de IA não falham por falta de capacidade técnica. Falham por falta
de contexto e estrutura. Quando você pede uma feature inteira de uma vez,
o agente:

- Empilha tudo num único sprint gigante
- Mistura planejamento, execução e validação
- Perde contexto entre sessões
- Declara vitória prematura
- Implementa além do escopo

A solução é **quebrar em tasks pequenas e independentes**, com contrato
formal entre executor e QA para cada uma.

## A solução em uma frase

> **Uma feature = N sprints. Um sprint = N tasks. Uma task = um contrato.**

Cada task passa pelo ciclo completo: contrato → implementação → verificação
→ auditoria → fechamento. Falhas afetam só a task, não o sprint inteiro.

## Os seis agentes

| Agente | Papel |
|---|---|
| `spec-writer` | Lê a ideia, investiga o código, gera PRD + sprints + **tasks** |
| `contract-writer` | Gera o contrato formal de **uma task** (executor ↔ QA) |
| `spec-dev` | Implementa **uma task** seguindo o contrato à risca |
| `spec-verifier` | Valida que a implementação adere ao contrato da task |
| `tdd-reviewer` | Audita testes da task + captura cost real em USD |
| `context-writer` | Persiste estado de cada task e agrega por sprint |

## Estrutura

```
.claude/
├── agents/
│   ├── spec-writer.md
│   ├── contract-writer.md
│   ├── spec-dev.md
│   ├── spec-verifier.md
│   ├── tdd-reviewer.md
│   └── context-writer.md
├── commands/
│   ├── ideia.md       # /idea
│   ├── contract.md    # /contract --task N.M
│   ├── sprint.md      # /sprint start|done|block N.M
│   ├── verify.md      # /verify --task N.M
│   ├── review.md      # /review --task N.M
│   └── yolo.md        # /yolo  (modo autônomo)
├── prds/              # PRDs gerados pelo spec-writer
├── prompts/           # prompts de execução e correção
├── verify/            # relatórios por task
├── tdd/               # auditorias de teste por task
└── context/
    ├── sprints.md             # índice agregado
    ├── current.md             # próxima task
    ├── sprint-N.md            # lista de tasks do sprint
    ├── task-N-M.md            # estado de cada task
    ├── task-N-M-contract.md   # contrato de cada task
    └── activity.log           # eventos em tempo real
sdd.py                # dashboard de terminal
install.sh
```

## Pipeline manual

```
/idea "sua ideia"
    → spec-writer investiga, faz perguntas, propõe sprints e tasks
    → Sumário de Alinhamento aguarda confirmação
    → context-writer inicializa estado

→ Para cada task em ordem (respeitando dependências):

/contract --task 1.1
    → contract-writer formaliza o acordo executor ↔ QA

/sprint start 1.1
    → marca a task como em andamento

→ spec-dev implementa
    → escreve no activity.log a cada arquivo tocado

/sprint done 1.1
    → marca task como pronta para verificação

/verify --task 1.1
    → spec-verifier valida aderência ao contrato

/review --task 1.1
    → tdd-reviewer audita cobertura, captura cost via `claude /usage`
    → context-writer fecha a task, calcula score, agrega no sprint

→ próxima task...
```

## Modo autônomo (YOLO)

Aprove o PRD e a pipeline executa sozinha task por task:

```
/yolo
```

Comportamento:
- contract → spec-dev → verify → review → próxima task
- Falha 🚫 não interrompe: spec-dev corrige e reverifica
- Limite de **3 tentativas por task**
- Após 3 falhas, task vira `blocked` e YOLO pula para a próxima
- Resumo final lista o que ficou bloqueado para revisão manual

## Dashboard em tempo real

```
╭─────────────────────────────────────────────────────────────────────╮
│ sdd  —  Spec-Driven Development                                     │
│ feature: CV Builder AI   prd: .claude/prds/2026-05-20-cv.md         │
│                                                                     │
│ ╭─────────────────────── Sprints & Tasks ─────────────────────────╮ │
│ │  #     Goal                  Contract     Build       QA        │ │
│ │  #1    Fundação Rails        6/6          5/6         4/6       │ │
│ │   1.1  Init Rails+Tailwind   ✓ AGREED    ✓ verified  ✓ passed   │ │
│ │   1.2  Devise+migration      ✓ AGREED    ✓ verified  ✓ passed   │ │
│ │   1.3  OmniAuth Google       ✓ AGREED    ✓ verified  ✓ passed   │ │
│ │   1.5  Migrations jobs       ✓ AGREED    ✓ verified  ⠋ running  │ │
│ │   1.6  Sidekiq + Redis       ✓ AGREED    ⠙ running   —          │ │
│ │  #2    Editor + Templates    1/4          1/4         0/4       │ │
│ ╰─────────────────────────────────────────────────────────────────╯ │
│ ╭─────────────────────────── Activity ────────────────────────────╮ │
│ │ ⠹ em andamento: Lendo config/application.rb                     │ │
│ │ 19:18 ✓ [tdd-reviewer] task-1.1 Score 100, cost $0.12           │ │
│ │ 19:25 ✓ [contract-writer] task-1.6 Contrato AGREED              │ │
│ │ 21:36 ▶ [spec-dev] task-1.6 Configurando Sidekiq + Redis        │ │
│ ╰─────────────────────────────────────────────────────────────────╯ │
│ ⠸ tasks 4/10   sprint atual #1   score 97   cost $1.20   elapsed.. │
╰─────────────────────────────────────────────────────────────────────╯
```

Características:
- **Sprints expandidos em tasks** — vê cada task individualmente
- **Loading contínuo** — spinner uv-style nunca para enquanto há atividade
- **Activity feed em tempo real** — agentes escrevem em cada passo
- **Cost real em USD** — capturado da `claude /usage` por task
- **Cost agregado** — sprint mostra soma; rodapé mostra total do projeto

```bash
python3 sdd.py              # live (padrão)
python3 sdd.py status       # snapshot estático
python3 sdd.py task 1.3     # detalhes de uma task específica
python3 sdd.py sprint 2     # detalhes de um sprint
python3 sdd.py log          # activity log completo
python3 sdd.py context      # contexto para nova sessão
```

## Quebra em tasks — regra central

O `spec-writer` quebra cada sprint em tasks. Uma task deve atender **todos**:

1. **Coesa** — UM objetivo verificável
2. **Independente** — pode ser revisada/revertida isoladamente
3. **Pequena** — máx ~150 linhas alteradas ou 4 arquivos
4. **Binária** — passou ou não, sem zona cinza
5. **Dependências explícitas** — quais tasks precisam terminar antes

**Heurística da palavra "E":** se o goal contém "e" ligando duas ações,
são duas tasks. "Configurar Devise **e** OmniAuth" vira Task 1.2 (Devise)
+ Task 1.3 (OmniAuth).

## Memória entre sessões

`.claude/context/current.md` é sempre atualizado pelo `context-writer`.
Qualquer sessão nova lê esse arquivo e sabe exatamente em qual task parar.

```bash
python3 sdd.py context   # mostra current.md
```

## Instalação

```bash
# Na raiz do seu projeto
curl -fsSL https://raw.githubusercontent.com/helgg/sdd-agent/master/install.sh | bash

# Ou inspecionar antes
curl -fsSL https://raw.githubusercontent.com/helgg/sdd-agent/master/install.sh -o install.sh
bash install.sh
```

**Dependências:**
- Python 3.8+
- `rich` (instalado automaticamente)
- Claude Code (ou outro executor que entenda markdown e tenha acesso ao filesystem)

## Adaptação

O sistema é agnóstico de stack. Funciona com Ruby on Rails, Next.js,
Django, FastAPI, Go — o `tdd-reviewer` detecta a stack automaticamente.
Os agentes referenciam domínios genéricos; substitua pelos do seu projeto
para resultados mais precisos.

---

MIT License