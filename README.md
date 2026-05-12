# Spec-Driven Development

Um sistema de dois arquivos para transformar ideias soltas em especificações
executáveis antes de acionar agentes de código.

## O problema

Agentes de IA não falham por falta de capacidade técnica. Falham por falta
de contexto. Uma ideia vaga entregue a um executor capaz ainda produz resultado
errado — porque a ambiguidade foi resolvida pelo agente, não por você.

## A solução

Separar dois papéis que costumam se misturar:

- **Você decide** — o que construir, por que agora, qual o resultado esperado
- **O agente especifica** — investiga o código, documenta premissas, produz artefatos executáveis

## Estrutura

```
.claude/
├── commands/
│   └── idea.md          # comando de entrada — /idea "sua ideia"
└── agents/
    └── spec-writer.md   # agente que processa e gera os artefatos
```

## Como usar

1. Copie os dois arquivos para o seu projeto respeitando a estrutura acima
2. No Claude Code, execute `/idea "descrição da sua ideia"`
3. O agente investiga o código, faz perguntas se necessário, e entrega:
   - Um **PRD-Lite** salvo em `.claude/prds/`
   - Um **prompt de execução** pronto para colar no agente executor

## O que o agente produz

**PRD-Lite** — documento curto com:
- Problema concreto e beneficiário
- Definição de pronto verificável
- Escopo negativo explícito
- Áreas técnicas afetadas
- Premissas assumidas documentadas

**Prompt de execução** — texto fechado com:
- Objetivo em uma frase
- Escopo e fora de escopo
- Arquivos relevantes mapeados no código
- Domínios de preocupação a aplicar
- Critérios de pronto binários

## Adaptação

O sistema foi construído para Claude Code mas o conceito é agnóstico de
ferramenta. Os arquivos podem ser adaptados para qualquer agente que suporte
instruções em markdown e acesso ao sistema de arquivos.

O `spec-writer.md` referencia domínios de preocupação genéricos (arquitetura,
segurança, interface, observabilidade etc). Substitua por suas próprias skills
ou instruções específicas do projeto.

## Contexto

Este repositório acompanha o post:
[Spec-Driven Development: como parei de dar ideias para agentes e comecei a dar decisões](#)

---

MIT License
