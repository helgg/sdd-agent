---
description: Exibe estado dos sprints e tasks, gerencia transições de status
allowed-tools: Read, Write, Glob, Grep, Task
---

Use o agente context-writer para processar o seguinte comando:

<comando>
$ARGUMENTS
</comando>

## Comandos disponíveis

- `/sprint` — exibe tabela geral de sprints (com progresso por tasks)
- `/sprint N` — detalhes do Sprint #N e suas tasks
- `/sprint start N.M` — marca Task #N.M como `build: in_progress`
- `/sprint done N.M` — marca Task #N.M como `build: done` (pronta para /verify)
- `/sprint block N.M "razão"` — marca task como `build: blocked`
- `/sprint context` — exibe `current.md` para reconstruir contexto em nova sessão

Se $ARGUMENTS estiver vazio, execute `/sprint` e exiba estado geral.