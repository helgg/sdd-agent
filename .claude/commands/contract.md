---
description: Gera o contrato formal entre executor e QA para um sprint antes da implementação começar
allowed-tools: Read, Write, Glob, Grep, Task
---

Use o agente contract-writer para gerar o contrato do seguinte sprint:

<contexto>
$ARGUMENTS
</contexto>

## Uso

- `/contract --sprint N` — gera o contrato para o Sprint #N
- `/contract --sprint N --prd YYYY-MM-DD-nome` — especifica o PRD de referência

Se $ARGUMENTS estiver vazio, pergunte:
- Qual o número do sprint?
- Há um PRD-Lite em `.claude/prds/`? Se sim, qual?

Execute sempre após o PRD ser aprovado e antes do executor iniciar o sprint.
Após o contrato ser gerado e confirmado, execute `/sprint start N`.