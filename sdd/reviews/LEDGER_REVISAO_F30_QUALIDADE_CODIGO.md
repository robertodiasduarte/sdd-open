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

Revisão do código da S2, rodada 2 (`e65531f`, depois do conserto do ciclo 1 do avaliador): revisor `openrouter`
(`qwen/qwen3.7-plus`), auditor `claude`; `diversidade: vendor`; US$ 0,89. Nenhum achado.

revisor2: dispensado rodada=2 — sem superfície de risco (regra antiga: 24 arquivos (limiar 8))
sem achados: rodada=2 EXTERNAL_REVIEW_20261124-092744

Revisão do código da S2, rodada 3 (`d734b18`, depois dos consertos do raio de impacto): revisor `openrouter`
(`qwen/qwen3.7-plus`), auditor `claude`; `diversidade: vendor`; US$ 0,88. 2 achados LOW do revisor, confirmados pelo auditor.

revisor2: dispensado rodada=3 — sem superfície de risco (regra antiga: 26 arquivos (limiar 8))

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | LOW | REBATIDA_ESCOPO | rodada=3 | sabotagem.sh:34: o molde de reserva sem `lib/python.sh` é o mesmo dos outros scripts de sdd/bin; sem Python sai 3 (inconclusivo), nunca um falso 0; pendência na ficha | nao | EXTERNAL_REVIEW_20261124-100402 |
| R2 | LOW | REBATIDA_ESCOPO | rodada=3 | sabotagem.sh:95: sem `pipefail`, a falha do `git archive` (já precedido do `git cat-file -e HEAD:<arquivo>`) vira 64 em vez de 3; sem log nem toque na árvore; pendência na ficha | nao | EXTERNAL_REVIEW_20261124-100402 |

Revisão do código da S2, rodadas 4 e 5 (`ea3bc55` contra a `main`, 4 linhas de teste): recusadas como rasas pelo
`--conferir`; US$ 0,42 cada.

sem resultado: rodada=4 EXTERNAL_REVIEW_20261124-132408 — 2º revisor raso (0 achados em 14 s): não conta
sem resultado: rodada=5 EXTERNAL_REVIEW_20261124-132501 — 2º revisor raso (0 achados em 28 s): não conta

Revisão da S2 inteira, rodada 6 (`ea3bc55`, base `08f41a8`): revisor `codex` (`gpt-6.1-sol`), auditor `claude`;
`diversidade: vendor`; US$ 1,89. O R2 da rodada 3 (pipefail), antes rebatido, foi aplicado junto em `79f64c5`.

revisor2: dispensado rodada=6 — sem superfície de risco (regra antiga: 63 arquivos (limiar 8))

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | HIGH | APLICADA | rodada=6 | `79f64c5`: o destino do log e as pastas dele não podem ser link, conferido no início e na gravação; teste: test_log_que_e_link_simbolico_nao_e_seguido | sim | EXTERNAL_REVIEW_20261124-132608 |
| R2 | MED | APLICADA | rodada=6 | `79f64c5`: quebra de linha garantida antes do [exit=]; teste: test_saida_sem_quebra_de_linha_no_fim | nao | EXTERNAL_REVIEW_20261124-132608 |

Revisão da S2 inteira, rodada 7 (`aee8d67`, base `08f41a8`): revisor `codex` (`gpt-6.1-sol`), auditor `claude`;
`diversidade: vendor`; US$ 1,91.

revisor2: dispensado rodada=7 — sem superfície de risco (regra antiga: 63 arquivos (limiar 8))

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | HIGH | APLICADA | rodada=7 | `26ea320`: log gravado em arquivo novo e renomeado; teste: test_log_que_e_hard_link_nao_apaga_o_outro_nome | sim | EXTERNAL_REVIEW_20261124-133334 |
| R2 | MED | APLICADA | rodada=7 | `26ea320`: o commit é resolvido uma vez; teste: test_commit_no_meio_nao_troca_a_versao_da_segunda_copia | nao | EXTERNAL_REVIEW_20261124-133334 |
| R3 | MED | APLICADA | rodada=7 | `26ea320`: WORKER_BRIEF com o antes verde do shall continue to; teste: test_brief_do_worker_tem_a_excecao_da_nao_regressao | nao | EXTERNAL_REVIEW_20261124-133334 |

Revisão da S2 inteira, rodada 8 (`cb35651`, base `08f41a8`): revisor `codex` (`gpt-6.1-sol`), auditor `claude`;
`diversidade: vendor`; US$ 1,93. Nenhum achado.

revisor2: dispensado rodada=8 — sem superfície de risco (regra antiga: 63 arquivos (limiar 8))
sem achados: rodada=8 EXTERNAL_REVIEW_20261124-133818

Revisão da S2 inteira, rodada 9 (`2864d26`, base `08f41a8`): revisor `codex` (`gpt-6.1-sol`), auditor `claude`;
`diversidade: vendor`; US$ 1,97. Nenhum achado. A revisão `EXTERNAL_REVIEW_20261124-162027` foi interrompida de propósito
(o commit mudou: `MANIFEST.txt`) e não conta; o custo dela não foi medido.

revisor2: dispensado rodada=9 — sem superfície de risco (regra antiga: 68 arquivos (limiar 8))
sem achados: rodada=9 EXTERNAL_REVIEW_20261124-162303

Correção do `sdd-drive` (`v2.27.4`), rodada 10 (`2b015b4`, base `origin/main` = `b85d1c9`): revisor `codex` (`gpt-6.1-sol`,
20 s e 0 achados: raso, não conta sozinho), 2º revisor openrouter `qwen/qwen3.7-plus`, auditor `claude`; `diversidade: vendor`;
US$ 0,11. Rodada sem os documentos SDD da feature (o `--feature` não foi passado).

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1@openrouter | MED | REBATIDA_EVIDENCIA | rodada=10 | `sdd/bin/sdd-drive.sh`, `trava(p)`: o caminho é o mesmo literal `sdd/reports/progress/DRIVE_<F>.lock`, na mesma pasta; auditor: DISAGREE_CONCERN | nao | EXTERNAL_REVIEW_20261124-181536 |

## S3

Revisão do DESIGN da S3, rodada D3 (base `fce8c61`): revisor openrouter `qwen/qwen3.7-plus` (46 s, 0 achados), auditor
`claude`; `diversidade: vendor`; US$ 0,73. Os 3 achados são do auditor.

revisor2: dispensado rodada=D3 — sem superfície de risco

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| N1 | MED | APLICADA | rodada=D3 | DESIGN 3.1, Decisions 16 e 17; teste: test_jscpd_que_leu_o_projeto_mas_nao_o_diff | nao | EXTERNAL_REVIEW_20261125-064417 |
| N2 | MED | APLICADA | rodada=D3 | DESIGN 3.1, Decision 16; teste: test_config_do_projeto_nao_chega_a_ferramenta | nao | EXTERNAL_REVIEW_20261125-064417 |
| N3 | MED | APLICADA | rodada=D3 | DESIGN 3.1, Decision 15; teste: test_apagar_o_que_vem_depois_nao_marca_a_funcao_anterior | nao | EXTERNAL_REVIEW_20261125-064417 |

Revisão do código da S3, rodada 11 (base `fce8c61`): revisor openrouter `qwen/qwen3.7-plus` (155 s, 0 achados), auditor
`claude`; `diversidade: vendor`; US$ 0,92. Os 2 achados são do auditor.

revisor2: dispensado rodada=11 — sem superfície de risco (regra antiga: 17 arquivos (limiar 8))

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| N1 | MED | APLICADA | rodada=11 | nome do jscpd normalizado e conferido; teste: test_nome_do_jscpd_em_outra_forma | nao | EXTERNAL_REVIEW_20261125-065922 |
| N2 | MED | APLICADA | rodada=11 | --raiz em subpasta; teste: test_raiz_numa_subpasta | nao | EXTERNAL_REVIEW_20261125-065922 |

Revisão do código da S3, rodada 12 (base `fce8c61`): revisor `codex` (`gpt-6.1-sol`, 252 s), auditor `claude`;
`diversidade: vendor`; US$ 0,87.

revisor2: dispensado rodada=12 — sem superfície de risco (regra antiga: 18 arquivos (limiar 8))

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | HIGH | APLICADA | rodada=12 | `d33ffed`: qualidade: numa linha só; teste: test_mapa_numa_linha_so | nao | EXTERNAL_REVIEW_20261125-070718 |
| R2 | MED | APLICADA | rodada=12 | `d33ffed`; teste: test_remoto_sem_ancestral_nao_cai_na_branch_local | nao | EXTERNAL_REVIEW_20261125-070718 |
| R3 | MED | APLICADA | rodada=12 | `d33ffed`; teste: test_arquivo_antigo_grande_e_dito | nao | EXTERNAL_REVIEW_20261125-070718 |

Revisão do código da S3, rodada 13 (base `fce8c61`): revisor `codex` (`gpt-6.1-sol`, 140 s), auditor `claude`;
`diversidade: vendor`; US$ 0,88.

revisor2: dispensado rodada=13 — sem superfície de risco (regra antiga: 18 arquivos (limiar 8))

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | MED | APLICADA | rodada=13 | `976c970`; teste: test_tmpdir_relativo_e_apagado | nao | EXTERNAL_REVIEW_20261125-072013 |
| R2 | MED | APLICADA | rodada=13 | `976c970`; teste: test_config_do_git_de_quem_roda_nao_muda_a_medida | nao | EXTERNAL_REVIEW_20261125-072013 |
| R3 | MED | APLICADA | rodada=13 | `976c970`; teste: test_saida_ilegivel | nao | EXTERNAL_REVIEW_20261125-072013 |

Revisão do código da S3, rodada 14 (base `fce8c61`): revisor `codex` (`gpt-6.1-sol`, 213 s), auditor `claude`;
`diversidade: vendor`; US$ 0,90.

revisor2: dispensado rodada=14 — sem superfície de risco (regra antiga: 20 arquivos (limiar 8))

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | MED | APLICADA | rodada=14 | `77db690`; teste: test_numero_enorme_nao_derruba | nao | EXTERNAL_REVIEW_20261125-073150 |
| R2 | LOW | APLICADA | rodada=14 | `77db690`; teste: test_limite_grande_vale | nao | EXTERNAL_REVIEW_20261125-073150 |
| N1 | MED | APLICADA | rodada=14 | `77db690`: sem relpath; teste de texto test_pasta_temporaria_em_outra_unidade (não executado em duas unidades) | nao | EXTERNAL_REVIEW_20261125-073150 |

Revisão do código da S3, rodada 15 (base `fce8c61`): revisor `codex` (`gpt-6.1-sol`, 224 s), auditor `claude`;
`diversidade: vendor`; US$ 0,87.

revisor2: dispensado rodada=15 — sem superfície de risco (regra antiga: 20 arquivos (limiar 8))

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | MED | APLICADA | rodada=15 | `1585b12`; teste: test_saida_ilegivel | nao | EXTERNAL_REVIEW_20261125-074156 |
