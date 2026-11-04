# Regras da LOOP_SPEC v2

Consultar este arquivo em toda especificação ou revisão de um processo em laço. As marcas `<LOOP_SPEC>`
e os nomes das seções são contrato: ficam em inglês, sem tradução. O texto dentro delas segue a língua do
projeto.

Uma boa especificação é:

- **executável:** o estado de controle e o ciclo são concretos o bastante para virar código;
- **verificável:** um verificador independente julga por evidência, nunca pela narrativa de quem gerou;
- **limitada:** tetos duros, aplicados antes de cada ação;
- **convergente:** métrica de progresso e detecção de repetição, não só um teto total;
- **segura na falha:** estados terminais explícitos; nunca "assumir que passou".

Prefira o menor laço que resolve. Um laço só se justifica quando a saída de uma chamada ao modelo precisa
decidir a próxima; senão, é uma chamada única e vai para a skill de prompt.

## Princípios

1. **A intenção é um contrato imutável.** "Pronto" se prova por evidência (código de saída, schema, testes
   verdes), nunca por "parece bom". Invariantes (o que não pode ser violado, mesmo com sucesso) e
   não-objetivos fazem parte dela. Quem gera não altera a intenção, o critério de pronto, o verificador nem
   as fixtures.
2. **Verificar, não lembrar.** O laço confere contra o material de referência injetado e contra a coerência
   interna; nunca confia na memória do modelo sobre fatos. O que está fora da referência é "não verificável":
   estado neutro, nunca penalidade nem aprovação.
3. **Código antes do modelo.** Toda decisão que pode ser determinística é código: casamento com catálogo,
   limites e cortes, agregações, validação de schema, checagem de completude. O modelo propõe e fundamenta; o
   código decide. Pedir no prompt o que o código pode garantir é regressão.
4. **Recuperar antes de condenar.** Antes de apontar divergência, esgote as hipóteses benignas plausíveis
   (fórmula alternativa, unidade, arredondamento, tolerância). A regra de desempate é explícita: na dúvida entre
   "divergente" e "não verificável", fique com "não verificável", e diga a quem um alarme falso prejudica.
5. **Estado de controle em registro.** O laço guarda entre ciclos: registro de tentativas (subobjetivo, hash do
   estado, impressão digital da ação, assinatura normalizada do erro), orçamento gasto, métrica de progresso,
   efeitos pendentes, pontos de retomada. Toda regra lê desse estado; regra que o estado não sustenta é enfeite.
6. **Disjuntor, não proibição absoluta.** Mesma (ação, estado, assinatura de erro) já tentada: exige abordagem
   diferente ou reclassifica como `BLOCKED`. K tentativas por subobjetivo (padrão 3): escala. Falha transitória
   (tempo esgotado, limite de taxa): R novas tentativas com espera crescente (padrão 2), depois reclassifica.
7. **Convergência é separada de orçamento.** O orçamento limita o estrago; a convergência detecta desperdício:
   W ciclos sem variação na métrica de progresso (padrão 3), estado que se repete ou volta atrás, custo por
   unidade de progresso subindo.
8. **Só estados terminais explícitos.** `DONE` (verificador aprovou e invariantes intactos), `EXHAUSTED`
   (orçamento), `BLOCKED`, `NON_CONVERGENCE`, `SAFETY_STOP`, `VERIFIER_FAILURE`, `NEEDS_INPUT`/`NEEDS_APPROVAL`.
   Verificador quebrado ou evidência indisponível é `VERIFIER_FAILURE`, nunca `DONE`. O laço não para no meio de
   um ciclo para conversar: `NEEDS_INPUT` é estado terminal, com uma pergunta estruturada.
9. **Orçamento antes da ação, por estágio.** Negue a ação cujo custo estimado impede verificar, compensar e
   relatar depois. Os tetos de tokens e de saída são por estágio (extrair não é pontuar); um teto único trunca ou
   desperdiça.
10. **Anatomia adaptativa.** O perfil é escolhido pelo **risco dos efeitos** e, entre os reversíveis, por quem julga, não
    pelo tamanho da tarefa. Não force a especificação inteira num laço local e simples; não omita segurança quando há
    efeito externo ou irreversível.

## Escolher o perfil pelo risco dos efeitos

Primeiro o risco: efeito externo ou irreversível é sempre `high-risk`. Entre os 2 perfis de efeito reversível, decide
quem julga e quantos passos usam o modelo.

| Perfil | Quando | Seções |
|---|---|---|
| `lite` | efeito local e reversível, **1** estágio LLM e verificador só por código de saída (conserto + testes, refatoração, geração de um arquivo) | `intent` (com o escopo negativo), `control_state` mínimo, `observation`, `verifier` por código de saída, `stop_rules`, `budget` |
| `standard` | efeito local e reversível, em todo outro caso: **2 ou mais** estágios LLM, ou quem julga não é um código de saída (um modelo, uma pessoa) | as do `lite` + `cycle_protocol`, `context_assembly`, `action_space`, `recovery_and_convergence_policy`, `observability` |
| `high-risk` | efeito externo ou irreversível (deploy, escrita em produção, e-mail, dinheiro) | as do `standard` + `safety_and_effects`, `NEEDS_APPROVAL` em toda ação irreversível e reserva de orçamento para reverter |

Em qualquer perfil, sempre: o modelo de dano (qual erro é pior) e a regra de desempate dele; a tabela de estágios
LLM × código; o Verify Gate, quando há ground truth. Nunca inclua seção vazia.

## O que cada seção diz

- **`intent`** — objetivo, artefato ou efeito final, critério de pronto verificável por evidência, invariantes,
  não-objetivos, versão do contrato e dono. Modelo de dano: qual erro é pior (falso positivo ou falso negativo),
  porque ele decide cada desempate. No `lite`, também o escopo negativo: o que o laço não toca, sempre com o
  verificador, os critérios de pronto, as fixtures e o material normativo.
- **`control_state`** — campos concretos: id do ciclo, id do subobjetivo, hash do estado do mundo, registro de
  tentativas por (subobjetivo, hash, ação, assinatura do erro), orçamento gasto e restante, efeitos pendentes,
  pontos de retomada, métrica de progresso. Diga onde persiste (memória, arquivo, tabela): retomar depende disso.
- **`cycle_protocol`** — ordem fixa: SNAPSHOT → PROPOSTA → VALIDAÇÃO PRÉ-AÇÃO (autorizado? o orçamento cobre agir,
  verificar, compensar e relatar? o registro permite?) → EXECUÇÃO → OBSERVAÇÃO → VERIFICAÇÃO → TRANSIÇÃO. Papéis
  separados: quem gera propõe, quem executa age, quem coleta observa, quem verifica julga. Nenhum absorve o
  verificador.
- **`context_assembly`** — o que é relido a cada ciclo e o que é imutável; tamanho limitado; procedência e
  atualidade; material **normativo** (schemas, catálogos, fórmulas, checagens canônicas: imutável, fora do alcance de
  quem gera) separado do informativo. Detecção de mudança externa por hash, quando importa.
- **`action_space`** — cada ação: pré-condições, pós-condições esperadas, idempotente?, reversível?, tempo limite,
  compensação. Escopo negativo: o que o laço não toca, sempre com o verificador, os critérios de pronto, as fixtures
  e o material normativo.
- **`observation`** — evidência por ação: códigos de saída, saídas, diffs, resultados analisados; assinatura de erro
  **normalizada** (comparável entre ciclos); resultado ambíguo (a ação pode ter acontecido mesmo se a coleta falhou:
  confira o estado do mundo antes de repetir ação não idempotente); procedência.
- **`verifier`** — independente e bloqueante. Julga a observação contra o critério de pronto e os invariantes:
  DONE, progrediu, igual, regrediu ou INDETERMINATE. Independência operacional: quem gera não altera testes, fixtures,
  critérios, evidência nem o verificador. Prefira código de saída a julgamento em prosa. Evidência instável: repita N
  vezes; ainda inconsistente é INDETERMINATE, nunca DONE. Verificador indisponível é `VERIFIER_FAILURE`.
- **`recovery_and_convergence_policy`** — taxonomia de falhas, com critério objetivo, cada falha em exatamente uma:
  RECOVERABLE, TRANSIENT, BLOCKED, INDETERMINATE, SAFETY_STOP, VERIFIER_FAILURE. Disjuntor (registro + K tentativas + R
  novas tentativas transitórias). Convergência: métrica de progresso explícita (numerador ÷ denominador), janela de W
  ciclos sem progresso, detecção de repetição, escalada por custo por progresso.
- **`stop_rules`** — todos os estados terminais, com os gatilhos.
- **`budget`** — tetos duros aplicados antes da ação: máximo de ciclos, teto de tokens ou custo **por estágio**, tempo
  de relógio, K, W, reserva obrigatória para verificar, compensar e relatar, limite de escalada (prefira `NEEDS_INPUT`
  a um `EXHAUSTED` seco quando o restante não paga um ciclo inteiro).
- **`safety_and_effects`** — só com ação irreversível ou externa: classifique cada ação (local reversível, local
  irreversível, externa); ponto de retomada antes do irreversível; reversão definida; sem reversão possível (um e-mail enviado), a ação só fica
  com `NEEDS_APPROVAL`, e sem quem aprove sai do `action_space`; ação externa exige idempotência ou chave de deduplicação;
  `high-risk` exige `NEEDS_APPROVAL` em toda ação irreversível; depois de resultado
  ambíguo, confira o estado do mundo antes de repetir ação com efeito.
- **`observability`** — rastro por ciclo, que alimenta o controle e a auditoria: id do ciclo → hash → proposta →
  validação → ação → observação (assinatura) → veredito → transição → orçamento restante. Também: métrica de progresso
  por ciclo, registro, pontos de retomada e o estado terminal com a justificativa. Diga onde o rastro fica.

## Lições de campo, aplicar por padrão

- **JSON de prosa longa quebra** (aspas sem escape): limite os campos de prosa, instrua aspas simples dentro das strings,
  1 nova tentativa de JSON estrito, depois `VERIFIER_FAILURE`.
- **Completude da extração é o elo fraco:** quando o laço começa por um estágio de inventário, acrescente uma checagem de
  cobertura (itens por seção × seções presentes).
- **Fórmula com várias hipóteses:** uma só hipótese de reserva recria falsos positivos.

## Molde da resposta

Sempre um bloco de texto, com as seções do perfil e sem seção vazia:

```text
<LOOP_SPEC v="2" perfil="lite|standard|high-risk" nome="<nome>">
<intent>...</intent>
<control_state>...</control_state>
<cycle_protocol>...</cycle_protocol>                          (standard e high-risk)
<context_assembly>...</context_assembly>                      (standard e high-risk)
<action_space>...</action_space>                              (standard e high-risk)
<observation>...</observation>
<verifier>...</verifier>
<recovery_and_convergence_policy>...</recovery_and_convergence_policy>  (standard e high-risk)
<stop_rules>...</stop_rules>
<budget>...</budget>
<safety_and_effects>...</safety_and_effects>                  (high-risk, ou com efeito irreversível ou externo)
<observability>...</observability>                            (standard e high-risk)
</LOOP_SPEC>

ESTÁGIOS:
| # | estágio | tipo | entrada → saída | verificador | maxTokens | nova tentativa | arquivo |

PROMPTS PENDENTES: um por estágio LLM, com o contrato de saída em 1 linha.
VERIFY GATE: comando, métrica, limite e código de saída; ou "sem ground truth: definir o eval antes da release".
```

`tipo` é `LLM` ou `código`. `arquivo` é o destino do prompt de um estágio LLM (`<pasta do processo>/<estágio>.<ext>`) e
`—` num estágio de código. `maxTokens` é `—` num estágio de código.

## Barra de qualidade

Antes de entregar, confira:

- o critério de pronto é verificável por evidência, e os invariantes estão escritos;
- o modelo de dano e a regra de desempate são explícitos;
- toda decisão determinística é um estágio de código, não uma instrução de prompt;
- a checagem de fatos vem da referência injetada, nunca da memória do modelo;
- os campos de `control_state` sustentam cada regra citada;
- os estados terminais cobrem a falha do próprio verificador;
- os orçamentos são por estágio e aplicados antes da ação;
- a tabela de estágios e a lista de prompts pendentes estão presentes;
- a especificação está num bloco de texto.
