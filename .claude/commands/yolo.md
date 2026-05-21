---
description: Modo autônomo — encadeia agentes por todas as tasks pendentes até a entrega
allowed-tools: Read, Write, Glob, Grep, Bash, Task
---

## Modo YOLO — Pipeline Autônoma por Tasks

A partir do PRD aprovado, os agentes se encadeiam sozinhos task por task
até todas concluírem.

<contexto>
$ARGUMENTS
</contexto>

---

## Comportamento

Para cada task em ordem (respeitando `depends_on`):

1. **contract-writer** gera o contrato da task → AGREED
2. **spec-dev** implementa seguindo o contrato
3. **spec-verifier** valida aderência
4. **tdd-reviewer** audita cobertura + captura cost USD
5. **context-writer** registra estado e score

### Tratamento de falhas (sem interrupção)

Se `spec-verifier` retornar 🚫 (desvios críticos):
- O spec-dev é acionado para corrigir usando o prompt gerado
- A task é reverificada
- Contador de tentativas incrementa

Se `tdd-reviewer` retornar 🚫 (lacunas críticas):
- O spec-dev é acionado para escrever os testes
- A task volta para o review
- Contador de tentativas incrementa

**Limite de 3 tentativas por task.** Após a 3ª tentativa falhando:
- Task vira `build: blocked`
- YOLO **pula** para a próxima task
- Bloqueio registrado no relatório final

---

## Workflow do YOLO

1. Use o context-writer para identificar a próxima task elegível:
   - `contract: pending` ou `build: pending` ou `build: failed`
   - `depends_on` com todas `qa: passed`

2. Se houver task elegível, execute o ciclo completo:
   - contract-writer → spec-dev → spec-verifier → tdd-reviewer
   - Cada agente registra no activity.log
   - Em caso de falha 🚫: spec-dev corrige → reverifica (até 3 tentativas)

3. Após task fechar (passed ou blocked após 3 tentativas):
   - Recalcule agregados
   - Identifique próxima task
   - Repita

4. Quando nenhuma task elegível restar:
   - Emita o resumo final

---

## Resumo Final

```
╔══════════════════════════════════════════════╗
║  Pipeline YOLO concluída                     ║
╠══════════════════════════════════════════════╣
║  Tasks concluídas: N/Total                   ║
║  Tasks bloqueadas: N                         ║
║  Score médio: XX/100                         ║
║  Cost total: $X.XX                           ║
║  Tempo total: Xh Xm                          ║
╚══════════════════════════════════════════════╝

Tasks bloqueadas (revisar manualmente):
- Task X.Y — [razão] — 3 tentativas
- Task X.Z — [razão] — 3 tentativas

Relatórios em:
- .claude/verify/
- .claude/tdd/
```

---

## Interrupção manual

`/yolo --stop` — encerra o ciclo atual após concluir a task em andamento
e reporta o estado.

Se $ARGUMENTS estiver vazio, inicie pela primeira task elegível em
`.claude/context/sprints.md`.