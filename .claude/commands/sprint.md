---
description: Exibe o estado atual de todos os sprints e gerencia transições de status (start, done)
allowed-tools: Read, Write, Glob, Grep, Task
---

Use o agente context-writer para processar o seguinte comando de sprint:

<comando>
$ARGUMENTS
</comando>

## Comandos disponíveis

- `/sprint` — exibe tabela de todos os sprints e o próximo passo recomendado
- `/sprint start N` — marca o Sprint #N como in_progress (executor iniciou)
- `/sprint done N` — marca o Sprint #N como done (executor concluiu, pronto para /verify)
- `/sprint status N` — exibe detalhes completos do Sprint #N
- `/sprint context` — exibe o current.md para reconstruir contexto em nova sessão

Se $ARGUMENTS estiver vazio, execute `/sprint` e exiba o estado geral.