---
description: Transforma uma ideia solta em PRD-Lite + sprints + tasks, prontos para execução
allowed-tools: Read, Write, Glob, Grep, Task
---
Use o agente spec-writer para processar a seguinte ideia:

<ideia>
$ARGUMENTS
</ideia>

Se $ARGUMENTS estiver vazio, peça ao usuário que descreva a ideia.

O spec-writer irá:
- Investigar o código existente
- Conduzir perguntas se necessário (1-3 rodadas)
- Apresentar Sumário de Alinhamento para confirmação
- Gerar PRD-Lite com diagrama Mermaid quando aplicável
- Quebrar cada sprint em tasks pequenas e independentes
- Inicializar o contexto via context-writer

Após inicialização, próximos passos típicos:
- /contract --task 1.1 (gera contrato da primeira task)
- /yolo (modo autônomo até a entrega)
- python3 sdd.py (dashboard em tempo real)