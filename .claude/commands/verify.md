---
description: Verifica aderência do código de uma TASK ao seu contrato antes do tdd-reviewer
allowed-tools: Read, Write, Glob, Grep, Bash, Task
---

Use o agente spec-verifier para verificar a aderência da seguinte task:

<contexto>
$ARGUMENTS
</contexto>

## Uso

- `/verify --task N.M` — verifica a Task #N.M

Pré-condição: a task deve estar com `build: done`.

Execute sempre antes de `/review` — desvios de escopo devem ser corrigidos
antes da auditoria de testes para evitar retrabalho.