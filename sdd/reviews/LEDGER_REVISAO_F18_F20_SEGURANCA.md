# Ledger da revisão — F18_F20_SEGURANCA

> Uma linha por achado decidido, de todas as rodadas da revisão adversarial desta frente. Conferido por
> `bash sdd/bin/ledger-revisao-lint.sh`; lido por `sdd-fluxo.sh loop --ledger` e por `eval-revisores.sh`.
> Critério da coluna `dano`: `sdd/review/CRITERIO_DANO.md`.

Cadeia: claude revisa, `openrouter` (qwen/qwen3.7-plus) audita, sem 2º revisor (`--no-revisor2`: codex sem cota, gemini sem
credencial; 2º revisor pago evitado pela LM-010). Rodada 1 (DESIGN v1.0 + DEFINE v1.1, só os 2 documentos): saldo da
OpenRouter US$ 18,15 antes; custo US$ 0,9621 (claude 0,9362 por assinatura nominal, qwen 0,0259). O script e o catálogo já
estavam escritos fora do diff revisado: os achados que tocam código foram conferidos nele, com teste escrito antes do conserto
e vermelho no script anterior (R1, R2, R4, R8, R10); R9 já passava (o defeito era só do texto).

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | MED | APLICADA | rodada=1 | teste: `test_r1_identificador_kebab_com_sk_nao_e_segredo` · S11 `sk-` exige 32+ caracteres com dígito; a classe `sk-fading-circle-spinner…` bloqueava a publicação | sim | EXTERNAL_REVIEW_20261111-134705 |
| R2 | MED | APLICADA | rodada=1 | teste: `test_r2_o_mais_grave_vem_antes_mesmo_que_ja_existisse` · ordem pela gravidade primeiro (AT-004) | nao | EXTERNAL_REVIEW_20261111-134705 |
| R3 | MED | APLICADA | rodada=1 | só texto: o script já avaliava toda `create table` (`test_tabela_antiga_sem_rls_vira_aviso`); DESIGN v1.1, Decisions 3 e 5 | nao | EXTERNAL_REVIEW_20261111-134705 |
| R4 | MED | APLICADA | rodada=1 | teste: `test_r4_motivo_da_dispensa_nunca_leva_o_segredo` · o motivo levava a chave para a saída e para a evidência | sim | EXTERNAL_REVIEW_20261111-134705 |
| R5 | MED | APLICADA | rodada=1 | só texto: o script já reconhecia o motivo vazio (`test_dispensa_sem_motivo_ou_de_outro_item_nao_vale`); DESIGN v1.1, Decision 7 | nao | EXTERNAL_REVIEW_20261111-134705 |
| R6 | MED | APLICADA | rodada=1 | DEFINE v1.2, AT-003: S03 nas migrações | nao | EXTERNAL_REVIEW_20261111-134705 |
| R7 | MED | APLICADA | rodada=1 | só texto: os modos de leitura já rodavam fora de git (`test_agents_traz_as_frases_da_stack_e_o_ponteiro`, repositório sem commit); DESIGN v1.1, linha da LM-006 | nao | EXTERNAL_REVIEW_20261111-134705 |
| R8 | MED | APLICADA | rodada=1 | teste: `test_r8_nome_com_acento_e_diff_sem_prefixo` · `--src-prefix=a/ --dst-prefix=b/` no diff | sim | EXTERNAL_REVIEW_20261111-134705 |
| R9 | MED | APLICADA | rodada=1 | só texto: `test_r9_palavras_chave_em_maiusculas` já passava; DESIGN v1.1, Decision 5 | nao | EXTERNAL_REVIEW_20261111-134705 |
| R10 | LOW | APLICADA | rodada=1 | teste: `test_r10_revoke_so_de_public_nao_basta` · S03 exige `revoke … from anon`; a função seguia chamável sem login e sem aviso | sim | EXTERNAL_REVIEW_20261111-134705 |
| R11 | LOW | APLICADA | rodada=1 | DEFINE v1.2, Goals: a lista do catálogo no lugar de "20 itens fixos" | nao | EXTERNAL_REVIEW_20261111-134705 |
| R12 | LOW | APLICADA | rodada=1 | DEFINE v1.2, Goals: "fichas com campos fixos" | nao | EXTERNAL_REVIEW_20261111-134705 |

Rodada 2 (código, o diff inteiro da frente desde `origin/main`, 48 arquivos, sobre `bf280b7`): saldo US$ 18,13 antes;
custo US$ 1,6916 (claude 1,6518 nominal, qwen 0,0398) + o desempate do codex, que caiu sem cota (exit 67, custo
desconhecido). O auditor discordou de R2 e R3 com premissa falsa: medido num repositório temporário, o git põe um TAB no
fim da linha `+++ b/<nome com espaço>` e, com `git -C <subpasta> diff`, devolve o caminho a partir do topo, enquanto o
`ls-files` devolve a partir da subpasta. O R2, que o desempate deixou para uma pessoa (D5), foi decidido por essa medição.
Os 7 testes caíram no script de antes do conserto.

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | HIGH | APLICADA | rodada=2 | teste: `test_r1_rls_comentado_nao_conta` · RLS comentado liberava a tabela; os comentários SQL saem antes da regra | sim | EXTERNAL_REVIEW_20261111-141409 |
| R2 | HIGH | APLICADA | rodada=2 | teste: `test_r2_nome_com_espaco_commitado_na_branch` · o TAB do git no fim do nome rebaixava o segredo novo a "já existia" | sim | EXTERNAL_REVIEW_20261111-141409 |
| R3 | MED | APLICADA | rodada=2 | teste: `test_r3_raiz_numa_subpasta` · `--relative` no diff | sim | EXTERNAL_REVIEW_20261111-141409 |
| R4 | LOW | APLICADA | rodada=2 | teste: `test_r4_linha_que_comeca_com_mais_mais_nao_e_cabecalho` · o `+++` só é cabeçalho entre o `diff --git` e o 1º `@@` | sim | EXTERNAL_REVIEW_20261111-141409 |
| R5 | LOW | APLICADA | rodada=2 | teste: `test_r5_marca_de_outro_item_na_linha_nao_esconde_a_de_cima` · vale a marca do próprio item | nao | EXTERNAL_REVIEW_20261111-141409 |
| N1 | MED | APLICADA | rodada=2 | teste: `test_n1_tabela_em_bloco_comentado_nao_conta` · tabela em `/* */` travava a publicação | sim | EXTERNAL_REVIEW_20261111-141409 |
| N2 | HIGH | APLICADA | rodada=2 | teste: `test_n2_revoke_de_uma_funcao_nao_cobre_a_outra` · o `revoke` vale para a função que ele nomeia | sim | EXTERNAL_REVIEW_20261111-141409 |

Rodada 3 (código, diff inteiro desde `origin/main`, sobre `ff164c6`, depois do raio de impacto): saldo US$ 18,09 antes;
custo US$ 2,0125 (claude 1,9700 nominal, qwen 0,0425); desempate desligado (`--no-desempate`: codex sem cota). É a
última rodada do teto do método (3): os consertos dela vão para a publicação sem revisor externo, com o registro aqui.

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | MED | APLICADA | rodada=3 | teste: `test_r3_1_tabela_recriada_ou_rls_desligada_numa_migracao_nova` · a regra do RLS segue a ordem das migrações (criar, ligar, desligar, apagar) | sim | EXTERNAL_REVIEW_20261111-152012 |
| R2 | LOW | APLICADA | rodada=3 | dispensa na linha dos 6 casos de teste com `eval(`; a varredura no próprio pacote sai NADA ACHADO | nao | EXTERNAL_REVIEW_20261111-152012 |
| R3 | LOW | APLICADA | rodada=3 | o script mantém `PAROU` sem Python, como os outros de `sdd/bin`; `docs/cli-conventions.md` passa a dizê-lo | nao | EXTERNAL_REVIEW_20261111-152012 |
| R4 | LOW | APLICADA | rodada=3 | o `unittest.main()` vai para o fim de `tests/test_design_lint.py` e `tests/test_sdd_open.py` (neste, a classe `Hooks` antiga também ficava depois dele) | nao | EXTERNAL_REVIEW_20261111-152012 |

Rodada 4 (acima do teto, decisão do Roberto na release: só o delta desde a rodada 3, `--base ff164c6`, 8 arquivos, sobre
`c30b54c`): saldo US$ 17,02 antes (caiu US$ 1,07 desde a rodada 3, mais que o custo dela: a chave tem outro uso);
custo US$ 0,7739 (claude 0,7511 nominal, qwen 0,0228). Os 3 achados vieram dos consertos feitos depois da rodada 3; os
3 testes caíram no script de antes.

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | MED | APLICADA | rodada=4 | teste: `test_r4_1_create_if_not_exists_nao_zera_a_rls` · migração idempotente travava a publicação | sim | EXTERNAL_REVIEW_20261111-171628 |
| R2 | LOW | APLICADA | rodada=4 | teste: `test_r4_2_rls_num_arquivo_que_ordena_antes_vale` · `enable` num arquivo que ordena antes vale para a tabela criada depois | sim | EXTERNAL_REVIEW_20261111-171628 |
| R3 | LOW | APLICADA | rodada=4 | teste: `test_r4_3_cabecalho_sem_corpo_nao_esconde_outra_chave_na_linha` · todo casamento da linha é avaliado | sim | EXTERNAL_REVIEW_20261111-171628 |
