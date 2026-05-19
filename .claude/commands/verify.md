---
description: Verifica se o código implementado adere ao PRD-Lite original antes de avançar para auditoria de testes
allowed-tools: Read, Write, Glob, Grep, Bash, Task
---

Use o agente spec-verifier para verificar a aderência do seguinte contexto:

<contexto>
$ARGUMENTS
</contexto>

Se $ARGUMENTS estiver vazio, pergunte ao usuário:
- Qual feature foi implementada?
- Há um PRD-Lite de referência em `.claude/prds/`? Se sim, qual o nome do arquivo?

Execute sempre antes do `/review` — desvios de escopo devem ser corrigidos
antes da auditoria de testes.