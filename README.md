# Spec-Driven Development

Um sistema de arquivos para transformar ideias soltas em especificações
executáveis e garantir cobertura de testes antes do merge.

## O problema

Agentes de IA não falham por falta de capacidade técnica. Falham por falta
de contexto. Uma ideia vaga entregue a um executor capaz ainda produz resultado
errado — porque a ambiguidade foi resolvida pelo agente, não por você.

O mesmo vale para testes: sem uma etapa de verificação explícita, o executor
entrega código funcionando mas sem cobertura adequada.

## A solução

Separar três papéis que costumam se misturar:

- **Você decide** — o que construir, por que agora, qual o resultado esperado
- **O agente especifica** — investiga o código, documenta premissas, produz artefatos executáveis
- **O agente audita** — verifica cobertura de testes por criticidade, bloqueia merge se necessário

## Estrutura

```
.claude/
├── commands/
│   ├── idea.md          # /idea "sua ideia" → spec-writer
│   └── review.md        # /review "feature" → tdd-reviewer
└── agents/
    ├── spec-writer.md   # transforma ideia em PRD-Lite + prompt de execução
    └── tdd-reviewer.md  # audita cobertura e gera prompt de fechamento de testes
```

## Pipeline completa

```
/idea "sua ideia"
    → spec-writer investiga e especifica
    → PRD-Lite salvo em .claude/prds/
    → Prompt de execução pronto

→ Claude Code implementa

/review "nome da feature"
    → tdd-reviewer audita cobertura por criticidade
    → Relatório salvo em .claude/tdd/
    → Prompt de fechamento gerado (se houver lacunas)

→ Claude Code escreve testes ausentes

→ Merge aprovado
```

## Como usar

### Especificar uma feature

```
/idea "descrição da sua ideia"
```

O agente investiga o código, faz perguntas se necessário, e entrega:
- Um **PRD-Lite** salvo em `.claude/prds/`
- Um **prompt de execução** pronto para colar no executor

### Auditar testes após implementação (padrão)

```
/review "nome da feature implementada"
```

O agente detecta a stack de testes automaticamente, analisa os arquivos
tocados, julga criticidade e entrega:
- Um **relatório de cobertura** salvo em `.claude/tdd/`
- Um **prompt de fechamento** com os testes ausentes (se houver lacunas 🔴/🟡)
- Um **veredicto**: merge aprovado ou bloqueado

### TDD clássico (escrever testes antes)

```
/review --before "nome da feature"
```

Use quando o PRD-Lite já existir e a interface pública estiver clara.
O agente gera os testes primeiro; o executor implementa até fazê-los passar.

## O que cada agente produz

### spec-writer

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
- Verificação pós-implementação (🔴/🟡/🟢)

### tdd-reviewer

**Relatório de cobertura** — auditoria com:
- Stack detectada automaticamente
- Mapeamento arquivo de produção → arquivo de teste
- Lacunas classificadas por criticidade (🔴 Crítico / 🟡 Importante / 🟢 Opcional)
- Veredicto: aprovado ou merge bloqueado

**Prompt de fechamento** — tarefa para o executor com:
- Casos de teste a implementar por arquivo
- Restrições de mock e estilo de assertion
- Critérios de pronto binários

## Instalação

### Instalar na raiz do projeto atual

```bash
curl -fsSL https://raw.githubusercontent.com/helgg/sdd-agent/master/install.sh | bash
```

### Ou em um diretório específico

```bash
curl -fsSL https://raw.githubusercontent.com/helgg/sdd-agent/master/install.sh | bash -s ~/meu-projeto
```

### Ou baixar e inspecionar antes

```bash
curl -fsSL https://raw.githubusercontent.com/helgg/sdd-agent/master/install.sh -o install.sh
bash install.sh
```

## Adaptação

O sistema foi construído para Claude Code mas o conceito é agnóstico de
ferramenta. Os arquivos podem ser adaptados para qualquer agente que suporte
instruções em markdown e acesso ao sistema de arquivos.

O `spec-writer.md` e o `tdd-reviewer.md` referenciam domínios de preocupação
genéricos. Substitua pelos domínios e skills específicos do seu projeto.

---

MIT License