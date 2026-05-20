# Spec-Driven Development

Um sistema de agentes para transformar ideias soltas em especificações
executáveis, organizar o trabalho em sprints rastreáveis, executar com
precisão cirúrgica e garantir qualidade antes do merge — com um dashboard
de terminal em tempo real.

## O problema

Agentes de IA não falham por falta de capacidade técnica. Falham por falta
de contexto e estrutura. Uma ideia vaga entregue a um executor capaz ainda
produz resultado errado — porque a ambiguidade foi resolvida pelo agente,
não por você.

Sem estrutura, o executor também sofre de amnésia entre sessões, declara
vitória prematura, implementa além do escopo e mistura planejamento com
execução com validação.

## A solução

Separar seis papéis com responsabilidades claras:

- **Você decide** — o que construir, por que agora, qual o resultado esperado
- **spec-writer especifica** — investiga o código, documenta premissas, quebra em sprints com diagrama Mermaid
- **contract-writer formaliza** — gera o acordo executor ↔ QA antes de cada sprint
- **spec-dev executa** — implementa cirurgicamente o que foi acordado, nada além
- **spec-verifier valida** — confronta o código com a spec e detecta desvios
- **tdd-reviewer audita** — verifica cobertura de testes por criticidade
- **context-writer memoriza** — persiste o estado entre sessões, elimina amnésia

## Conceitos

**Sprint** — unidade de trabalho rastreável, equivalente a um batch do Plano
de Dependências (T1, T2, T3...). Cada sprint tem goal, contrato, status de
build, QA, score e custo.

**Contract** — acordo formal gerado antes do executor começar. Define o que
o spec-dev vai construir e o que o QA vai validar, ambos derivados do PRD-Lite.
Elimina conflito de interesses entre implementação e validação.

**Score** — qualidade do sprint calculada ao fechar: começa em 100, desconta
por desvios críticos (−10) e importantes (−5) encontrados pelo spec-verifier
e tdd-reviewer.

**Cost** — custo real em dólar extraído do `/usage` do Claude Code, exibido
no dashboard em tempo real.

**YOLO Mode** — modo autônomo onde você aprova o PRD e a pipeline inteira
roda sozinha: contract → spec-dev → spec-verifier → tdd-reviewer → próximo sprint.
Interrompido automaticamente em desvios críticos ou bloqueios.

## Estrutura

```
.claude/
├── agents/
│   ├── spec-writer.md      # /idea → PRD-Lite + sprints + diagrama Mermaid
│   ├── spec-verifier.md    # /verify → aderência do código à spec
│   ├── tdd-reviewer.md     # /review → cobertura de testes por criticidade
│   ├── contract-writer.md  # /contract → acordo spec-dev ↔ QA por sprint
│   ├── spec-dev.md         # executor cirúrgico orientado ao contrato
│   └── context-writer.md   # memória persistente entre sessões
├── commands/
│   ├── ideia.md            # /idea "sua ideia"
│   ├── verify.md           # /verify "feature" [--sprint N]
│   ├── review.md           # /review "feature" [--before]
│   ├── contract.md         # /contract --sprint N
│   ├── sprint.md           # /sprint [start N | done N | status N | context]
│   ├── yolo.md             # /yolo — modo autônomo
│   └── audit-repo.md       # /audit-repo — valida integridade do repositório
├── prds/                   # PRDs gerados pelo spec-writer
├── prompts/                # prompts de execução gerados pelos agentes
├── tdd/                    # relatórios de cobertura do tdd-reviewer
├── verify/                 # relatórios de aderência do spec-verifier
└── context/                # estado persistente dos sprints
    ├── sprints.md          # índice geral de todos os sprints
    ├── current.md          # contexto atual — lido no início de cada sessão
    ├── sprint-N.md         # estado detalhado de cada sprint
    ├── sprint-N-contract.md # contrato de cada sprint
    └── activity.log        # feed de eventos em tempo real
sdd.py                      # dashboard de terminal em tempo real
install.sh                  # instalador
```

## Pipeline manual

```
/idea "sua ideia"
    → spec-writer investiga o código
    → PRD-Lite com diagrama Mermaid salvo em .claude/prds/
    → Plano de Dependências (sprints) criado
    → context-writer inicializa sprint log

/contract --sprint 1
    → contract-writer lê PRD + batch
    → Gera acordo: [spec-dev] compromete + [QA] compromete
    → context-writer: contract = AGREED

/sprint start 1
    → context-writer: build = in_progress

→ spec-dev implementa o Sprint #1
    → Declara entendimento, aguarda validação
    → Implementa cirurgicamente — nada além do contrato
    → Registra progresso no activity.log

/sprint done 1
    → context-writer: build = done

/verify "feature" --sprint 1
    → spec-verifier confronta código com PRD-Lite
    → Relatório de aderência salvo em .claude/verify/
    → context-writer: build = verified | failed

/review "feature" --sprint 1
    → tdd-reviewer audita cobertura por criticidade
    → Relatório salvo em .claude/tdd/
    → context-writer: qa = passed | failed, calcula score

/sprint
    → exibe tabela de todos os sprints

→ /contract --sprint 2 → próximo sprint...
```

## Modo autônomo (YOLO)

Após aprovar o PRD, a pipeline roda sozinha até a entrega:

```
/yolo
    → contract-writer gera contratos automaticamente
    → spec-dev implementa cada sprint
    → spec-verifier valida aderência
    → tdd-reviewer audita testes
    → context-writer atualiza estado e score
    → repete para o próximo sprint

Interrompido automaticamente em:
    → desvios 🔴 no spec-verifier
    → bloqueios reportados pelo spec-dev
    → lacunas 🔴 no tdd-reviewer

/yolo --stop   → interrompe manualmente
```

## Dashboard de terminal

O `sdd.py` monitora o estado em tempo real lendo `.claude/context/`:

```
╭──────────────────────────────────────────────────────────────╮
│ sdd  —  Spec-Driven Development                              │
│ feature: CSV Tools   prd: .claude/prds/2026-05-19-csv.md     │
│                                                              │
│ ╭──────────────────── Sprints ──────────────────────────╮    │
│ │  #   Goal              Contract    Build      QA       │    │
│ │  1   Parser CSV→Table  ✓ AGREED   ✓ verified ✓ passed  │    │
│ │  2   Table→CSV export  ✓ AGREED   ⠋ running  —         │    │
│ │  3   CSV diff viewer   —           —          —         │    │
│ ╰───────────────────────────────────────────────────────╯    │
│ ╭──────────────────── Activity ─────────────────────────╮    │
│ │ 20:00 ▶ [EXEC] Iniciando Sprint #2                    │    │
│ │ 21:00 · [EXEC] csv-export.ts: em progresso            │    │
│ ╰───────────────────────────────────────────────────────╯    │
│   sprint 2 / 3   score 95   cost $3.58   elapsed 4m 12s      │
╰──────────────────────────────────────────────────────────────╯
```

```bash
python3 sdd.py            # live — atualiza a cada 1.5s (padrão)
python3 sdd.py status     # snapshot estático
python3 sdd.py sprint 2   # detalhes do sprint #2
python3 sdd.py log        # activity log completo
python3 sdd.py context    # contexto para nova sessão
```

## Memória entre sessões

O `context-writer` mantém `.claude/context/current.md` sempre atualizado.
No início de qualquer sessão nova, o executor lê esse arquivo e sabe
exatamente onde parou — sem depender da memória da conversa anterior.

```bash
python3 sdd.py context    # exibe o contexto atual
```

## Instalação

# Instalar na raiz do projeto atual

```bash
curl -fsSL https://raw.githubusercontent.com/helgg/sdd-agent/master/install.sh | bash
```

# Ou em um diretório específico

```bash
curl -fsSL https://raw.githubusercontent.com/helgg/sdd-agent/master/install.sh | bash -s ~/meu-projeto
```
# Ou baixar e inspecionar antes
```bash

curl -fsSL https://raw.githubusercontent.com/helgg/sdd-agent/master/install.sh -o install.sh
bash install.sh
```

**Dependências:**
- Python 3.8+
- `rich` — instalado automaticamente pelo installer
- Qualquer executor com suporte a markdown e sistema de arquivos

## Adaptação

O sistema é agnóstico de ferramenta. Funciona com Claude Code, Cursor,
Windsurf, Cline, e qualquer executor que suporte instruções em markdown.

Os agentes referenciam domínios de preocupação genéricos. Substitua pelos
domínios e skills específicos do seu projeto para resultados mais precisos.

---

MIT License