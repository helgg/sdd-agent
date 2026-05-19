# Spec-Driven Development

Um sistema de agentes para transformar ideias soltas em especificações
executáveis, organizar o trabalho em sprints rastreáveis e garantir
qualidade antes do merge — com um dashboard de terminal em tempo real.

## O problema

Agentes de IA não falham por falta de capacidade técnica. Falham por falta
de contexto e estrutura. Uma ideia vaga entregue a um executor capaz ainda
produz resultado errado — porque a ambiguidade foi resolvida pelo agente,
não por você.

Sem estrutura, o executor também sofre de amnésia entre sessões, declara
vitória prematura, e mistura planejamento com execução com validação.

## A solução

Separar cinco papéis com responsabilidades claras:

- **Você decide** — o que construir, por que agora, qual o resultado esperado
- **spec-writer especifica** — investiga o código, documenta premissas, quebra em sprints
- **contract-writer formaliza** — gera o acordo executor ↔ QA antes de cada sprint
- **spec-verifier valida** — confronta o código com a spec e detecta desvios
- **tdd-reviewer audita** — verifica cobertura de testes por criticidade
- **context-writer memoriza** — persiste o estado entre sessões, elimina amnésia

## Conceitos

**Sprint** — unidade de trabalho rastreável, equivalente a um batch do Plano
de Dependências (T1, T2, T3...). Cada sprint tem goal, contrato, status de
build, QA, score e custo.

**Contract** — acordo formal gerado antes do executor começar. Define o que
o executor vai construir e o que o QA vai validar, ambos derivados do PRD-Lite.
Elimina conflito de interesses entre implementação e validação.

**Score** — qualidade do sprint calculada ao fechar: começa em 100, desconta
por desvios críticos (−10) e importantes (−5) encontrados pelo spec-verifier
e tdd-reviewer.

## Estrutura

```
.claude/
├── agents/
│   ├── spec-writer.md      # /idea → PRD-Lite + sprints + prompt de execução
│   ├── spec-verifier.md    # /verify → aderência do código à spec
│   ├── tdd-reviewer.md     # /review → cobertura de testes por criticidade
│   ├── contract-writer.md  # /contract → acordo executor ↔ QA por sprint
│   └── context-writer.md   # memória persistente entre sessões
├── commands/
│   ├── ideia.md            # /idea "sua ideia"
│   ├── verify.md           # /verify "feature" [--sprint N]
│   ├── review.md           # /review "feature" [--before]
│   ├── contract.md         # /contract --sprint N
│   └── sprint.md           # /sprint [start N | done N | status N | context]
├── prds/                   # PRDs gerados pelo spec-writer
├── prompts/                # prompts de execução gerados pelos agentes
├── tdd/                    # relatórios de cobertura do tdd-reviewer
├── verify/                 # relatórios de aderência do spec-verifier
└── context/                # estado persistente dos sprints
    ├── sprints.md          # índice geral de todos os sprints
    ├── current.md          # contexto atual — lido no início de cada sessão
    ├── sprint-N.md         # estado detalhado de cada sprint
    └── sprint-N-contract.md # contrato de cada sprint
sdd.py                      # dashboard de terminal em tempo real
install.sh                  # instalador
```

## Pipeline completa

```
/idea "sua ideia"
    → spec-writer investiga o código
    → PRD-Lite com diagrama Mermaid salvo em .claude/prds/
    → Plano de Dependências (sprints) criado
    → context-writer inicializa sprint log

/contract --sprint 1
    → contract-writer lê o PRD e o batch correspondente
    → Gera acordo: [EXECUTOR] compromete + [QA] compromete
    → Status: AGREED
    → context-writer atualiza: contract = AGREED

/sprint start 1
    → context-writer atualiza: build = in_progress

→ Executor implementa o Sprint #1

/sprint done 1
    → context-writer atualiza: build = done

/verify "feature" --sprint 1
    → spec-verifier confronta código com PRD-Lite
    → Relatório de aderência salvo em .claude/verify/
    → Prompt de correção gerado se houver desvios
    → context-writer atualiza: build = verified | failed

/review "feature" --sprint 1
    → tdd-reviewer audita cobertura por criticidade
    → Relatório salvo em .claude/tdd/
    → Prompt de fechamento gerado se houver lacunas
    → context-writer atualiza: qa = passed | failed, calcula score

/sprint
    → exibe tabela de todos os sprints com status atual

→ /contract --sprint 2 → próximo sprint...
```

## Dashboard de terminal

O `sdd.py` monitora o estado dos sprints em tempo real lendo `.claude/context/`:

```
╭─────────────────────────────────────────────────────────────────╮
│ sdd  —  Spec-Driven Development                                 │
│ feature: CSV Tools   prd: .claude/prds/2026-05-18-csv.md        │
│                                                                 │
│ ╭──────────────────── Sprints ──────────────────────────────╮   │
│ │  #   Goal                Contract    Build       QA       │   │
│ │ ─────────────────────────────────────────────────────     │   │
│ │  1   Parser CSV→Table    ✓ AGREED    ✓ verified  ✓ passed │   │
│ │  2   Table→CSV export    ✓ AGREED    … running   pending  │   │
│ │  3   CSV diff viewer       pending     pending   pending  │   │
│ ╰───────────────────────────────────────────────────────────╯   │
│ ╭──────────────────── Activity ─────────────────────────────╮   │
│ │ Próximo passo: aguardar /sprint done 2                    │   │
│ │ ↳ Executor implementando exportação...                    │   │
│ ╰───────────────────────────────────────────────────────────╯   │
│   sprint 2 / 3   score 95   elapsed 4m 12s                      │
╰─────────────────────────────────────────────────────────────────╯
```

```bash
# Execute sempre da raiz do projeto (onde está .claude/context/)
python3 sdd.py            # live — atualiza a cada 2s (padrão)
python3 sdd.py status     # snapshot estático
python3 sdd.py sprint 2   # detalhes do sprint #2
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

```bash
# Instalar na raiz do projeto atual
curl -fsSL https://raw.githubusercontent.com/helgg/sdd-agent/master/install.sh | bash

# Ou em um diretório específico
curl -fsSL https://raw.githubusercontent.com/helgg/sdd-agent/master/install.sh | bash -s ~/meu-projeto

# Ou baixar e inspecionar antes
curl -fsSL https://raw.githubusercontent.com/helgg/sdd-agent/master/install.sh -o install.sh
bash install.sh
```

**Dependências:**
- Python 3.12+
- `rich` (instalado automaticamente pelo installer)
- Qualquer executor com suporte a markdown e sistema de arquivos

## Adaptação

O sistema é agnóstico de ferramenta. Funciona com Claude Code, Cursor,
Windsurf, Cline, e qualquer executor que suporte instruções em markdown.

Os agentes referenciam domínios de preocupação genéricos. Substitua pelos
domínios e skills específicos do seu projeto para resultados mais precisos.

---

MIT License