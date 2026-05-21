---
description: Audita cobertura de testes de uma TASK e captura cost real em USD
allowed-tools: Read, Write, Glob, Grep, Bash, Task
---

Use o agente tdd-reviewer para auditar o seguinte contexto:

<contexto>
$ARGUMENTS
</contexto>

## Uso

- `/review --task N.M` — audita Task #N.M (modo padrão)
- `/review --task N.M --before` — TDD clássico (testes antes do código)

Pré-condição (modo padrão): task com `build: verified`.

Após /review aprovado, a task fecha e o context-writer atualiza o estado.
Próximo passo: /contract --task próxima ou aguardar continuação no /yolo.