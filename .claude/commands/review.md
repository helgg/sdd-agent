---
description: Audita cobertura de testes após implementação e bloqueia merge até critérios de qualidade serem atendidos
allowed-tools: Read, Write, Glob, Grep, Bash, Task
---

Use o agente tdd-reviewer para auditar o seguinte contexto:

$ARGUMENTS

Se $ARGUMENTS estiver vazio, pergunte ao usuário:
- Qual feature ou arquivo foi implementado?
- Há um PRD-Lite de referência em `.claude/prds/`?

Para TDD clássico (escrever testes antes da implementação), use `/review --before "descrição da feature"`.