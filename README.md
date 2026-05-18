# Spec-Driven Development

Um sistema de agentes para transformar ideias soltas em especificações
executáveis, verificar aderência à spec e garantir cobertura de testes
antes do merge.

## O problema

Agentes de IA não falham por falta de capacidade técnica. Falham por falta
de contexto. Uma ideia vaga entregue a um executor capaz ainda produz resultado
errado — porque a ambiguidade foi resolvida pelo agente, não por você.

O mesmo vale para o ciclo completo: sem verificação de aderência e sem portão
de testes, o executor entrega código que funciona mas não é o que foi pedido,
ou funciona mas sem cobertura adequada.

## A solução

Separar quatro papéis que costumam se misturar:

- **Você decide** — o que construir, por que agora, qual o resultado esperado
- **O agente especifica** — investiga o código, documenta premissas, produz artefatos executáveis
- **O agente verifica** — confronta o código implementado com a spec original e detecta desvios
- **O agente audita** — verifica cobertura de testes por criticidade, bloqueia merge se necessário

## Estrutura

```
.claude/
├── agents/
│   ├── spec-writer.md    # transforma ideia em PRD-Lite + prompt de execução
│   ├── spec-verifier.md  # verifica aderência do código à spec original
│   └── tdd-reviewer.md   # audita cobertura e gera prompt de fechamento de testes
├── commands/
│   ├── ideia.md          # /idea "sua ideia"
│   ├── verify.md         # /verify "feature"
│   └── review.md         # /review "feature"
├── prds/                 # PRDs gerados pelo spec-writer
├── prompts/              # prompts de execução e fechamento gerados pelos agentes
├── tdd/                  # relatórios de cobertura gerados pelo tdd-reviewer
└── verify/               # relatórios de aderência gerados pelo spec-verifier
install.sh
README.md
```

## Pipeline completa

```
/idea "sua ideia"
    → spec-writer investiga e especifica
    → PRD-Lite salvo em .claude/prds/
    → Prompt de execução pronto

→ Executor implementa

/verify "nome da feature"
    → spec-verifier confronta código com PRD-Lite
    → Relatório de aderência salvo em .claude/verify/
    → Prompt de correção gerado (se houver desvios)

→ Executor corrige desvios (se necessário)

/review "nome da feature"
    → tdd-reviewer audita cobertura por criticidade
    → Relatório salvo em .claude/tdd/
    → Prompt de fechamento gerado (se houver lacunas)

→ Executor escreve testes ausentes

→ Merge aprovado
```

## Como usar

### Especificar uma feature

```
/idea "descrição da sua ideia"
```

O agente investiga o código, faz perguntas se necessário, e entrega:
- Um **PRD-Lite** salvo em `.claude/prds/` — com diagrama Mermaid quando relevante
- Um **prompt de execução** pronto para colar no executor

### Verificar aderência após implementação

```
/verify "nome da feature implementada"
```

O agente lê o PRD-Lite de referência, inspeciona o código implementado e entrega:
- Um **relatório de aderência** salvo em `.claude/verify/`
- Um **prompt de correção** com os desvios a corrigir (se houver)
- Um **veredicto**: aprovado, aprovado com ressalvas, ou não aprovado

Execute sempre antes do `/review` — desvios de escopo corrigidos antes da
auditoria de testes evitam retrabalho duplo.

### Auditar testes após verificação

```
/review "nome da feature"
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
- Diagrama Mermaid (quando a feature envolver fluxo, sequência ou estrutura)
- Escopo negativo explícito
- Áreas técnicas afetadas com caminhos reais do código
- Premissas assumidas documentadas

**Prompt de execução** — texto fechado com:
- Objetivo em uma frase
- Escopo e fora de escopo
- Arquivos relevantes mapeados no código
- Domínios de preocupação a aplicar
- Critérios de pronto binários
- Verificação pós-implementação (🔴/🟡/🟢)

### spec-verifier

**Relatório de aderência** — auditoria com:
- Verificação item a item dos critérios de pronto do PRD
- Verificação dos componentes do diagrama Mermaid (se existir)
- Desvios classificados: 🔴 Crítico / 🟡 Importante / 🟠 Adição não autorizada / 🟢 Conforme
- Veredicto: aprovado, aprovado com ressalvas, ou não aprovado

**Prompt de correção** — tarefa para o executor com:
- Desvios a corrigir por prioridade
- Arquivo afetado e correção esperada
- Restrição explícita de não alterar o que já está conforme

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

O sistema é agnóstico de ferramenta. Funciona com qualquer executor que suporte
instruções em markdown e acesso ao sistema de arquivos: Claude Code, Cursor,
Windsurf, Cline, e outros.

Os agentes referenciam domínios de preocupação genéricos (arquitetura,
segurança, interface, observabilidade etc). Substitua pelos domínios e skills
específicos do seu projeto para resultados mais precisos.

---

MIT License