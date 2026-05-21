---
description: Gera o contrato formal entre spec-dev e QA para uma TASK específica
allowed-tools: Read, Write, Glob, Grep, Task
---

Use o agente contract-writer para gerar o contrato da seguinte task:

<contexto>
$ARGUMENTS
</contexto>

## Uso

- `/contract --task N.M` — gera contrato da Task #N.M
- `/contract --task N.M --prd YYYY-MM-DD-nome` — especifica o PRD

Se $ARGUMENTS estiver vazio, pergunte:
- Qual o ID da task (formato N.M)?
- Há PRD em `.claude/prds/`? Se sim, qual?

Pré-condições:
- A task deve existir em `.claude/context/task-N-M.md` com `contract: pending`
- As dependências em `depends_on` devem ter `qa: passed`

Após o contrato AGREED, próximo passo:
- /sprint start N.M (manual)
- ou aguardar continuação automática se em /yolo