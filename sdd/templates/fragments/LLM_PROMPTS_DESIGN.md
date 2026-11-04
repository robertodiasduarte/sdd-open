<!--
Fragmento — Seção "LLM Prompts" do DESIGN. Dono único do inventário e do contrato por prompt.

Reusável. A fase Design copia daqui até o fim para o DESIGN quando o DEFINE tem `LLM Prompts: true`,
entre os padrões de código e o fluxo de dados, e troca o que está entre chaves. Com `false`, a seção
não existe. `sdd/bin/design-lint.py` confere as colunas e os campos. A Design não escreve prompt nem
chama skill de prompt: a fase Build faz isso, com o contrato em mãos.
-->

## LLM Prompts

> Inventário dos prompts de produção desta feature: o que o sistema construído manda para um modelo.
> Texto para pessoas (e-mail, manual, aviso na tela) não entra, nem instrução interna do método.

### Roteador: qual é o Tipo de cada linha

| Tipo | Quando | Quem constrói na fase Build |
|---|---|---|
| `one-shot` | chamada única: system prompt, classificador, sintetizador, passe único | a skill de `prompts.builder_skill` |
| `loop` | processo que re-prompta o modelo com base na própria saída anterior: reavaliar até, gerador + avaliador, retry com julgamento | `sdd-loop-builder` primeiro (a LOOP_SPEC); depois um prompt por estágio LLM, pela skill de `prompts.builder_skill` |

Sinal decisivo: *o processo re-prompta o modelo com base na própria saída anterior?* Sim, `loop`. Na
dúvida, `loop`. Laço só de código, sem modelo, e orquestração interna do método não entram no inventário.

### Inventário

| # | Nome | Tipo | Arquivo de destino | Versão | Provedor/Modelo | Origem da entrada | Consumidor da saída | Material de referência | Completeness | Refator de? |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | {nome} | one-shot | `{caminho do arquivo}` | {v1} | {provedor e modelo} | {de onde vem o dado} | {quem consome a saída} | {schema, regra ou trecho} | {itens contáveis, ou n/a} | {versão anterior, ou novo} |

Em `Tipo=loop`, o arquivo de destino é `<pasta do processo>/LOOP_SPEC.md`. Cada estágio LLM grava em
`<pasta do processo>/<estágio>.<ext>`, com o nome da coluna `arquivo` da tabela de estágios. Esses
arquivos contam como inventariados e como previstos no File Manifest, derivados da linha.

### Contrato por prompt

Um bloco por linha do inventário, na mesma ordem. Quanto mais concreto, melhor o prompt: a skill de
prompt não deve inferir nada.

#### Prompt 1: {nome}

| Atributo | Valor |
|---|---|
| **Tom/audiência** | {do DEFINE ou do UX_REVIEW; não invente} |
| **Tipo de saída** | {JSON, Markdown, texto; derivado do consumidor} |
| **Fallback aprovado** | {o que devolver sem dado suficiente} |
| **Autônomo?** | {sim, não pode pedir nada de volta; ou não, pode pedir} |
| **Verification interna** | {sim, com os pontos; ou não} |
| **Eval mínimo pré-ship** | {comando e amostras; por exemplo, 5 de 5 no contrato} |

Só em `Tipo=loop`, 3 linhas a mais na tabela, porque a `sdd-loop-builder` para sem elas:

| Atributo | Valor |
|---|---|
| **Intenção** | {o que o processo produz, para quem, e o que "pronto" significa de forma verificável} |
| **Perfil de risco dos efeitos** | {locais e reversíveis, locais e irreversíveis, ou externos} |
| **Ground truth disponível** | {onde estão os dados, ou nenhum} |

**Material de referência a injetar** (cópia literal; não só o ponteiro):
- {schema da saída}
- {regra do domínio}

**Decisões já fechadas** (não reabrir na fase Build):
- {provedor e modelo}
- {formato de saída}

### Versionamento

- Prompt que já atendeu ao menos uma requisição real não se edita: refator cria `v{N+1}/`.
- O prompt vivo é o que o código importa, não o de maior número.
- Rollback é mudar uma linha de import.

### Gate do Build por Tipo

- **Antes de gravar**, o texto gerado passa por `bash sdd/bin/prompt-drift-scan.sh --conteudo <caminho>`.
  Num arquivo deste inventário, a saída 2 é o esperado e o arquivo é gravado.
- **`one-shot`:** a skill de `prompts.builder_skill` recebe a linha, o bloco do contrato e o material de
  referência literal; o texto devolvido é gravado no destino no mesmo turno.
- **`loop`:** `sdd-loop-builder` recebe o contrato e devolve o bloco com a LOOP_SPEC, a tabela de estágios, os
  prompts pendentes e o Verify Gate. Para cada estágio LLM, a skill de `prompts.builder_skill` recebe o bloco da
  linha, a linha do estágio e o contrato dele em PROMPTS PENDENTES. O bloco inteiro e cada prompt são gravados no
  mesmo turno; os estágios de código viram código, nunca prompt.
- **Relatório:** 1 entrada por prompt em `sdd/templates/fragments/LLM_PROMPTS_BUILD_REPORT.md`; em `loop`, 1
  pela LOOP_SPEC e 1 por estágio, marcadas como derivadas da linha.
