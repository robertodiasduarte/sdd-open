<!-- Idioma: [English](../llm-in-code.md) · **Português** -->

# LLM no código e contraste medido

Desde a v2.5.0, o método tem quatro peças para software que chama um modelo de linguagem em produção e uma para
acessibilidade. Nenhuma se aplica a um projeto sem prompt e sem tela: elas não atrapalham quem não as usa.

## Um processo em laço: `sdd-loop-builder`

Uma chamada única e um processo são coisas diferentes. A pergunta que decide: **o processo re-prompta o modelo com
base na própria saída anterior?** Se sim, é um laço: ele pode repetir o mesmo erro, gastar sem limite ou dizer que
terminou sem conferir.

A skill `sdd-loop-builder` escreve a ficha do processo, uma **LOOP_SPEC v2**, antes de existir código:

| O que ela fixa | Por quê |
|---|---|
| **Perfil por risco** (`lite`, `standard`, `high-risk`): efeito externo ou irreversível é `high-risk`; entre os reversíveis, `lite` é 1 estágio LLM conferido por código de saída | Um laço local e simples não precisa da ficha inteira; um que envia e-mail, sim |
| **Estado de controle** | Toda regra de nova tentativa, orçamento e parada lê dele |
| **Verificador independente** | Quem gerou o texto não o julga |
| **Regras de parada**, inclusive a falha do próprio verificador | Verificador quebrado nunca é "pronto" |
| **Orçamento por estágio**, aplicado antes de cada ação | Um teto único trunca um estágio e desperdiça outro |
| **Tabela de estágios, LLM × código** | O que pode ser determinístico é código; o modelo propõe, o código decide |

A skill não escreve os prompts dos estágios. Ela dá a cada um o contrato de saída em 1 linha, e a skill de prompt o
escreve. Sem ground truth (exemplos em que já se sabe a resposta certa), a ficha diz isso, em vez de inventar um número.

## O inventário no Design

Quando o DEFINE diz `LLM Prompts: true`, o Design copia a seção de `sdd/templates/fragments/LLM_PROMPTS_DESIGN.md`: uma
linha por prompt de produção, com `Tipo`, `Versão`, `Completeness` e `Refator de?`, e um bloco de contrato por linha, com
`Autônomo?`, `Verification interna` e `Eval mínimo pré-ship`. O `sdd/bin/design-lint.py` reprova coluna ou campo faltando.

**Depois de atualizar o pacote**, um DESIGN em andamento com o inventário antigo reprova no `design-lint.py` uma vez. Não
é defeito do desenho, e nenhum código precisa mudar: copie as colunas e os campos do fragmento.

## O roteador no Build

Passo 4 da `sdd-build`, para um arquivo do inventário:

- `Tipo=one-shot` vai para a skill de `prompts.builder_skill`;
- `Tipo=loop` vai primeiro para a `sdd-loop-builder` e depois para a skill de prompt, uma vez por estágio LLM, tudo no
  mesmo turno;
- sem `Tipo` (DESIGN antigo): a pergunta que decide, acima; na dúvida, `loop`, com registro no relatório;
- skill ausente bloqueia aquele item, nunca se improvisa.

Uma linha em laço tem como destino `<pasta do processo>/LOOP_SPEC.md`, e cada estágio LLM grava no arquivo indicado na
tabela de estágios. Esses arquivos contam como inventariados.

## O fiscal de prompt: `prompt-drift-scan.sh`

Antes de gravar um arquivo, o Build pergunta: isto cheira a prompt de produção?

```bash
printf '%s' "$TEXTO" | bash sdd/bin/prompt-drift-scan.sh --conteudo src/agente/roda.ts
bash sdd/bin/prompt-drift-scan.sh src/agente/roda.ts     # arquivos já em disco
bash sdd/bin/prompt-drift-scan.sh --self-test
```

Ele procura uma pasta `prompts/`, um nome de arquivo com `prompt` (exceto `.md`), uma chamada direta ao SDK
(`messages.create`, `messages.stream`, `chat.completions`, `responses.create`, `generateContent` e as formas de streaming), `system` com texto fixo, um `role` de
sistema e, o sinal que mais importa, **o parâmetro da sua própria função de IA**:

```yaml
prompts:
  wrapper_pattern: "systemPrompt:"     # ou "callLLM\\(": entre aspas duplas, a contrabarra vai dobrada
```

O script acrescenta "seguida de texto fixo" a essa expressão, então um parâmetro que recebe um nome importado não
dispara: esse prompt mora no arquivo importado. **Vazio, o fiscal fica parcialmente cego**, e diz isso a cada execução: um
projeto que chama o modelo por uma função própria é invisível para quem procura assinaturas de SDK.

| Saída | Resultado | O que fazer |
|---|---|---|
| `0` | `LIMPO` | grave o arquivo |
| `2` | `DRIFT` | no inventário, é o esperado e o arquivo é gravado; fora dele, o Build para: itere o Design, ou registre o falso positivo |
| `64` | `ERRO DE USO` | chamada errada, caminho que não dá para ler ou slot inválido; nunca é tratado como limpo |

Arquivo de teste não dispara, nas convenções comuns: `a.test.x`, `a.spec.x`, `a_test.x`, `a_spec.x`, `test_a.x`, `ATest.x`,
`ATests.x` e as pastas `tests/`, `test/`, `spec/`, `__tests__/`. O conteúdo de um `.md` fora de `prompts/` não é avaliado.
**Limites:** a busca cobre formas comuns, linha a linha, e não é exaustiva: texto fixo na linha seguinte ao parâmetro, SDK
fora da lista e texto montado por variável não disparam. Para esses, use o slot. Sem git, a raiz é a pasta atual. Um `system: "linux"` num
YAML dispara: registre como falso positivo.

## Contraste medido: `contraste.sh`

```bash
bash sdd/bin/contraste.sh '#767676' '#ffffff'            # 4.54:1 PASSA (piso 4.5:1), saída 0
bash sdd/bin/contraste.sh '#777777' '#ffffff'            # 4.47:1 REPROVA (piso 4.5:1), saída 2
bash sdd/bin/contraste.sh '#000000' '#ffffff' .5         # transparência como 3º valor: composta sobre o fundo
bash sdd/bin/contraste.sh '#777777' '#ffffff' --piso 3   # texto grande, borda, ícone
```

**A cor vai entre aspas:** sem aspas, o `#` começa um comentário no shell, e as cores não chegam ao comando. As formas
aceitas são `#rgb` e `#rrggbb`; `rgba(...)` sai 64 e mostra a forma com o 3º valor.

**O resultado é truncado de propósito.** Calculadoras online costumam arredondar: uma pode mostrar 4.48 onde este mostra
4.47. Um 4,496 arredondado apareceria como 4.50 e passaria; truncado, mostra 4.49 e reprova o piso 4,5.

## A tabela WCAG na UX review

A `sdd-ux-review` preenche 7 linhas, WCAG 2.2 AA, sempre que a feature tem superfície visual; sem ela, uma linha
`N.A. — <motivo>`.

| Critério | Nível | Veredito |
|---|---|---|
| 1.4.3 contraste de texto | AA | `PASSA`, `REPROVA` ou `N.A.` |
| 1.4.11 contraste de não-texto, inclusive o anel de foco | AA | `PASSA`, `REPROVA` ou `N.A.` |
| 1.4.1 significado nunca só por cor | A | `PASSA`, `REPROVA` ou `N.A.` |
| 2.4.7 foco visível | AA | `PASSA`, `REPROVA` ou `N.A.` |
| 4.1.2 nome, papel e valor | A | `PASSA`, `REPROVA` ou `N.A.` |
| 2.1.1 teclado | A | herdado: vai para as notas de aceite |
| 2.5.8 tamanho do alvo | AA | herdado: vai para as notas de aceite |

Todo `REPROVA` vira 1 MUST, com o critério e o par medido. As 2 linhas herdadas só se provam na tela pronta. A tabela segue
o texto da norma; o projeto que quer mais guarda essa regra no próprio playbook. 3.3.7 é nível A e 2.4.13 é AAA: nenhum dos
2 é critério AA, e nenhum está na tabela.
