# Ledger da revisão — F16W2_WINDOWS

> Uma linha por achado decidido, de todas as rodadas da revisão adversarial desta frente. Conferido por
> `bash sdd/bin/ledger-revisao-lint.sh`; lido por `sdd-fluxo.sh loop --ledger` e por `eval-revisores.sh`.
> Critério da coluna `dano`: `sdd/review/CRITERIO_DANO.md`.

Cadeia: claude revisa, `openrouter` (qwen/qwen3.7-plus) audita, sem 2º revisor (`--no-revisor2`: codex sem cota) e sem
desempate (`--no-desempate`), como da F16 à F16W. Rodada 1 (diff inteiro `v2.16.0..696e94d`, sem `--paths`, 93 arquivos,
167 KB, com o BRAINSTORM, o DEFINE e o DESIGN de contexto): saldo da OpenRouter US$ 5,90 antes; custo US$ 2,0084 (claude
1,9706 por assinatura nominal, qwen 0,0378). O auditor concordou com R1, R2, R4 e R5, discordou do R3 por falta de contexto
(o código do guard está fora do diff) e trouxe o N1. Em paralelo, o raio de impacto (6 superfícies) achou 4 quebras reais,
consertadas em `cb08ead` e `e68bc88` (fora deste ledger: não são achados da revisão).

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | MED | APLICADA | rodada=1 | teste: `test_sem_pcre_o_caminho_por_arquivo_recusa_igual` · o git grep do índice inteiro só entra com mais de 40 candidatos a texto; commit pequeno vai pelo caminho por arquivo (`e68bc88`) | nao | EXTERNAL_REVIEW_20261114-213217 |
| R2 | MED | APLICADA | rodada=1 | teste: `test_hooks_path_absoluto_na_forma_do_windows_e_modo_hooks` (só no Windows, SO_NO_WINDOWS) · as recusas sobre o hook de `ad32fe1` estão em `evidence/F16W2_WINDOWS/AT-004-baseline-hook-antigo.log` (verdes nos dois hooks) | nao | EXTERNAL_REVIEW_20261114-213217 |
| R3 | MED | REBATIDA_EVIDENCIA | rodada=1 | `bin/adapters/claude/sdd-report-guard.py:85` e `sdd-avaliador-guard.py:55` já leem o payload por `sys.stdin.buffer` em UTF-8 (F16W, `103697e`); teste `test_report_guard_le_o_payload_em_utf8_cru_num_sistema_cp1252` | nao | EXTERNAL_REVIEW_20261114-213217 |
| R4 | MED | APLICADA | rodada=1 | teste: `test_valor_com_cr_e_lido_e_roda` · o python3 falso escreve o `\r` por awk, não por sed (o sed BSD antigo troca `\r` pela letra r) | nao | EXTERNAL_REVIEW_20261114-213217 |
| R5 | LOW | REBATIDA_ESCOPO | rodada=1 | `sdd-archive.py` e `test-baseline.sh` juntam com "/" por concatenação, sem `os.path`; `ntpath` não simula isso no Mac; a prova é o CI do PR no Windows (DESIGN v1.2, estratégia de testes) | nao | EXTERNAL_REVIEW_20261114-213217 |
| N1 | HIGH | REBATIDA_EVIDENCIA | rodada=1 | o destino de `escrever_gerado` é sempre `${ROOT}/…` (`bin/sdd-open.sh`, os 2 chamadores em `declare_alvos_skills` e `declare_alvos_adaptadores`): `${dest%/*}` nunca fica sem "/"; o raio de impacto confirmou | nao | EXTERNAL_REVIEW_20261114-213217 |

Rodada 2 (diff inteiro `v2.16.0..452c1a3`, sem `--paths`, depois da Decision 2 revista, do raio de impacto e do ciclo 1 do
avaliador): saldo da OpenRouter US$ 5,74 antes; custo US$ 2,6005 (claude 2,5545 nominal, qwen 0,0460). O auditor concordou
com o R4, discordou do R1 e do R2 com argumento (o MSYS não expande chaves; o sufixo do mktemp é aleatório) e do R3 pela
guarda textual; os 3 foram aplicados mesmo assim, pelo lado seguro e baratos.

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | MED | APLICADA | rodada=2 | teste: `test_todo_padrao_e_ere_valida` · o padrão vai ao grep por variável de ambiente (PADRAO), que o runtime do MSYS não expande; antes, como argumento do bash.exe, ainda passava pelo glob dele no Windows | nao | EXTERNAL_REVIEW_20261114-230738 |
| R2 | LOW | APLICADA | rodada=2 | teste: `test_corte_que_volta_0_e_sem_resposta` · a marca do vigia mora numa pasta própria do `mktemp -d` (antes, um nome livre no /tmp que um link poderia ocupar) | nao | EXTERNAL_REVIEW_20261114-230738 |
| R3 | LOW | APLICADA | rodada=2 | teste: `test_os_scripts_imprimem_o_caractere_e_saem_com_o_exit_de_sempre` · validate_kb e collect_evidence entram nos casos com cp1252; o kb_normativo segue coberto por `test_sdd_kb_normativo` com a emulação Latin-1 | nao | EXTERNAL_REVIEW_20261114-230738 |
| R4 | LOW | APLICADA | rodada=2 | teste: `test_commit_de_600_arquivos_lanca_no_maximo_3_programas_por_arquivo` · o PATH da armadilha e dos python3 falsos com `os.pathsep` e caminho nativo (no Windows, ";") | nao | EXTERNAL_REVIEW_20261114-230738 |

Rodada 3, a última dentro do teto (diff inteiro `v2.16.0..50afa50`, sem `--paths`, depois das rodadas de medição no PR #31 e
do piso): saldo da OpenRouter US$ 5,64 antes; custo US$ 1,9428 do claude (nominal); o auditor (qwen) estourou o tempo
(1.202 s, exit 67), a revisão não completou e o `--conferir` não a aceita. Decisão do Roberto (2026-11-15): rodada 4, acima do
teto, sobre o diff final.

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | MED | REBATIDA_EVIDENCIA | rodada=3 | o mesmo R3 da rodada 1: `bin/adapters/claude/sdd-report-guard.py:85` e `sdd-avaliador-guard.py:55` leem o payload por `sys.stdin.buffer` em UTF-8 desde a F16W (`103697e`); a linha 124 citada é o bloco que troca a saída | nao | EXTERNAL_REVIEW_20261115-030620 |
| R2 | LOW | APLICADA | rodada=3 | `tests/apoio.py`: o write_text em LF do Windows por `open(newline=)`, que existe no 3.9 (o `write_text(newline=)` é do 3.10); conferido com /usr/bin/python3 3.9.6 importando o apoio (`c2690d5`) | nao | EXTERNAL_REVIEW_20261115-030620 |

Rodada 4, acima do teto (decisão do Roberto, 2026-11-15), sobre o diff final (`v2.16.0..c2690d5`, sem `--paths`): saldo US$ 5,59
antes; custo US$ 2,5050 (claude 2,4486 nominal, qwen 0,0564). Completa; o auditor discordou do R1 por falta de contexto.

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | MED | REBATIDA_EVIDENCIA | rodada=4 | pela 3ª vez: os 2 guards leem o stdin por `sys.stdin.buffer` em UTF-8 (`sdd-report-guard.py:85`, `sdd-avaliador-guard.py:55`; teste `test_report_guard_le_o_payload_em_utf8_cru_num_sistema_cp1252`); o stub `sdd/review/stubs/openrouter.py` não lê o stdin (grep sem ocorrência) | nao | EXTERNAL_REVIEW_20261115-040405 |

escapou: commit=e2a1be8 · teste: test_disputa_pela_trava_nao_falha_nem_perde_gravacao · dano=disponibilidade — no Windows, a trava apagada ao largar (8a5a746) recusa a abertura de quem chega, e o verbo do sdd-drive saía 2 (CI 45634528055)
