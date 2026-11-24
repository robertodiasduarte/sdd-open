# Ledger da revisão — F30_QUALIDADE_CODIGO

> Uma linha por achado decidido, de todas as rodadas da revisão adversarial desta frente. Critério da coluna `dano`:
> `sdd/review/CRITERIO_DANO.md`.

Revisão do DESIGN, rodada D1: revisor `openrouter` (`qwen/qwen3.7-plus`), 2º revisor `codex` (`gpt-6.1-sol`),
auditor `claude`; `diversidade: vendor`. O `gemini` caiu antes, por credencial (`EXTERNAL_REVIEW_20261123-201202`,
exit 65, sem custo). Os dois revisores não acharam nada; os 2 achados são do auditor.

sem resultado: rodada=D0 EXTERNAL_REVIEW_20261123-201202 — gemini sem credencial (exit 65)

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| N1 | MED | APLICADA | rodada=D1 | DESIGN Decisions 3 e 4 (1.1): log de antes; vermelho→vermelho avisa, verde→vermelho bloqueia | nao | EXTERNAL_REVIEW_20261123-201231 |
| N2 | MED | APLICADA | rodada=D1 | DESIGN Decision 4 (1.1): o typecheck_cmd roda como está, sem arquivos anexados | nao | EXTERNAL_REVIEW_20261123-201231 |

Revisão do código, rodada 1 (`07198f3`): revisor `openrouter` (`qwen/qwen3.7-plus`), auditor `claude`;
`diversidade: vendor`. O revisor não achou nada; os 2 achados são do auditor.

revisor2: dispensado rodada=1 — sem superfície de risco (regra antiga: 30 arquivos (limiar 8))

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| N1 | MED | APLICADA | rodada=1 | `dac782a`: a dívida antiga confere o comando do slot; teste `test_antes_sem_os_arquivos_novos_ainda_e_divida_antiga` | nao | EXTERNAL_REVIEW_20261123-202810 |
| N2 | MED | APLICADA | rodada=1 | `dac782a`: sdd-build passo 4, o LINT.log final cobre todos os arquivos de código do manifest | nao | EXTERNAL_REVIEW_20261123-202810 |

Revisão do código, rodada 2 (`7eee8d7`): revisor `openrouter` (`qwen/qwen3.7-plus`), auditor `claude`;
`diversidade: vendor`. O revisor não achou nada; 1 achado do auditor.

revisor2: dispensado rodada=2 — sem superfície de risco (regra antiga: 32 arquivos (limiar 8))

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| N1 | MED | APLICADA | rodada=2 | `bb32004`: sdd-build passo 4, o lint de antes roda só sobre os arquivos do manifest que já existem; teste em `test_f30_textos.py` | nao | EXTERNAL_REVIEW_20261123-211144 |

Revisão do código, rodada 3 (`bb32004`): revisor `openrouter` (`qwen/qwen3.7-plus`), auditor `claude`;
`diversidade: vendor`. 1 achado do revisor (o auditor concordou) e 1 do auditor.

revisor2: dispensado rodada=3 — sem superfície de risco (regra antiga: 32 arquivos (limiar 8))

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | LOW | APLICADA | rodada=3 | `d94bb8b`: checar.sh, o find fora do git pula .cursor, .gemini, .codex e .kimi | nao | EXTERNAL_REVIEW_20261123-211621 |
| N1 | MED | APLICADA | rodada=3 | `d94bb8b`: sdd-build passo 4, o log de antes sempre existe com o slot cheio (sem arquivo existente, ou comando sem arquivos, o projeto inteiro) | nao | EXTERNAL_REVIEW_20261123-211621 |

Revisão do código, rodada 4 (`d94bb8b`): revisor `openrouter` (`qwen/qwen3.7-plus`), auditor `claude`;
`diversidade: vendor`. O revisor não achou nada; 2 achados do auditor.

revisor2: dispensado rodada=4 — sem superfície de risco (regra antiga: 32 arquivos (limiar 8))

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| N1 | MED | APLICADA | rodada=4 | report-lint: exit 126/127 antes ou depois não vale como dívida antiga; teste `test_ferramenta_ausente_antes_nao_e_divida_antiga` | nao | EXTERNAL_REVIEW_20261123-212311 |
| N2 | MED | APLICADA | rodada=4 | catálogo e checar.sh: `npx eslint`, sem `.` no fim (o Build acrescenta os arquivos da tarefa) | nao | EXTERNAL_REVIEW_20261123-212311 |

Revisão do código, rodada 5 (`76827bf`, a versão que sobe): revisor `openrouter` (`qwen/qwen3.7-plus`), auditor `claude`;
`diversidade: vendor`. O revisor não achou nada; 1 achado do auditor. Última rodada: daqui em diante, só achado grave
reabriria o código.

revisor2: dispensado rodada=5 — sem superfície de risco (regra antiga: 32 arquivos (limiar 8))

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| N1 | MED | REBATIDA_ESCOPO | rodada=5 | compatibilidade de BUILD_REPORT feito antes da v2.26.0 num projeto com lint_cmd cheio: o conserto é 1 comando que o próprio report-lint imprime (rodar o slot e gravar LINT.log); afrouxar para aviso quando o relatório não fala de lint deixaria build novo escapar por omissão; vai como nota de atualização na ficha e no ledger da release | nao | EXTERNAL_REVIEW_20261123-212910 |

## S2

Revisão do DESIGN da S2, rodada D2: revisor `openrouter` (`qwen/qwen3.7-plus`, 28 s), 2º revisor `codex` (`gpt-6.1-sol`),
auditor `claude`; `diversidade: vendor`; US$ 0,67. Os dois revisores não acharam nada; o achado é do auditor.

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| N1 | MED | APLICADA | rodada=D2 | DESIGN Decision 9 (2.1): a classe `continua` vem do início da célula; teste `test_criterio_que_so_cita_shall_continue_to_e_novo` | nao | EXTERNAL_REVIEW_20261124-083851 |

Revisão do código da S2, rodada 1 (`52bd4da`): revisor `openrouter` (`qwen/qwen3.7-plus`), auditor
`claude`; `diversidade: vendor`; US$ 0,88. Nenhum achado; o auditor conferiu a classe do AT, os exits, o relatório
antigo, a contenção do caminho e a limpeza da cópia, e descartou 3 pontos LOW já cobertos pelas Decisions 8 e 10.

revisor2: dispensado rodada=1 — sem superfície de risco (regra antiga: 24 arquivos (limiar 8))
sem achados: rodada=1 EXTERNAL_REVIEW_20261124-091418
