---
description: Modo autônomo — você aprova o PRD e a pipeline completa roda sozinha até a entrega
allowed-tools: Read, Write, Glob, Grep, Bash, Task
---

## Modo YOLO — Pipeline Autônoma

Você aprovou o PRD. A partir daqui, os agentes se encadeiam sozinhos até
a entrega completa de cada sprint.

**O que acontece:**
1. `contract-writer` gera o contrato do sprint atual
2. `spec-dev` implementa seguindo o contrato
3. `spec-verifier` valida aderência à spec
4. `tdd-reviewer` audita cobertura de testes
5. `context-writer` registra o estado e calcula o score
6. Repete para o próximo sprint — até todos estarem concluídos

**Você só será interrompido se:**
- Um desvio 🔴 for encontrado pelo spec-verifier
- Um bloqueio for reportado pelo spec-dev
- O tdd-reviewer bloquear o merge por lacunas críticas

<contexto>
$ARGUMENTS
</contexto>

---

## Instruções para execução autônoma

Use o agente context-writer para identificar o sprint atual em
`.claude/context/sprints.md`, depois encadeie os agentes na seguinte ordem
para cada sprint com status `contract: pending` ou `build: pending`:

### Para cada sprint pendente:

**Etapa 1 — Contrato**
Use o agente contract-writer:
- Leia o PRD e o batch correspondente
- Gere o contrato automaticamente (sem aguardar aprovação humana no modo YOLO)
- Marque como AGREED e registre no context-writer

**Etapa 2 — Implementação**
Use o agente spec-dev:
- Leia o contrato gerado
- Apresente o entendimento em 3 bullets (sem aguardar aprovação no modo YOLO)
- Implemente seguindo as regras absolutas
- Registre progresso no activity.log
- Se encontrar bloqueio: PARE e interrompa o modo YOLO, informe o usuário

**Etapa 3 — Verificação de aderência**
Use o agente spec-verifier:
- Verifique aderência ao PRD
- Se houver desvios 🔴: PARE e interrompa o modo YOLO, informe o usuário
- Se houver apenas desvios 🟡 ou 🟠: registre e continue
- Acione context-writer com build_update

**Etapa 4 — Auditoria de testes**
Use o agente tdd-reviewer:
- Audite cobertura por criticidade
- Se houver lacunas 🔴: PARE e interrompa o modo YOLO, informe o usuário
- Acione context-writer com qa_update

**Etapa 5 — Próximo sprint**
- Se houver sprint seguinte: repita a partir da Etapa 1
- Se todos os sprints estiverem concluídos: informe o usuário com resumo final

---

## Resumo Final (quando todos os sprints concluírem)

```
╔══════════════════════════════════════╗
║  Pipeline YOLO concluída             ║
╠══════════════════════════════════════╣
║  Sprints:  N concluídos              ║
║  Score médio: XX/100                 ║
║  Custo total: ver `python3 sdd.py`   ║
╚══════════════════════════════════════╝

Próximo passo: revise os relatórios em .claude/verify/ e .claude/tdd/
```

---

## Interrupção de emergência

Se $ARGUMENTS contiver `--stop`, encerre o modo YOLO imediatamente e
reporte o estado atual de cada sprint.

Se $ARGUMENTS estiver vazio, verifique `.claude/context/sprints.md` e
inicie pelo primeiro sprint com `contract: pending`.