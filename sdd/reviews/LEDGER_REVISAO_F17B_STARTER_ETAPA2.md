# Ledger da revisão — F17B_STARTER_ETAPA2

> Uma linha por achado decidido, de todas as rodadas da revisão adversarial desta frente. Conferido por
> `bash sdd/bin/ledger-revisao-lint.sh`; lido por `sdd-fluxo.sh loop --ledger` e por `eval-revisores.sh`.
> Critério da coluna `dano`: `sdd/review/CRITERIO_DANO.md`.

Cadeia: claude revisa, `openrouter` (qwen/qwen3.7-plus) audita, sem 2º revisor (`--no-revisor2`: codex sem cota) e sem
desempate (`--no-desempate`), como na F16, na F18 + F20 e na F17. Rodada 1 (diff `v2.13.0..c8826b7`, 57 arquivos, 178 KB,
sem as cópias byte a byte do starter em `scripts/starter/raiz/{docs,exemplos,tests}` e da `ux-review-builder`, com o
BRAINSTORM, o DEFINE e o DESIGN de contexto): saldo da OpenRouter US$ 14,22 antes; custo US$ 1,7519 (claude 1,6990 por
assinatura nominal, qwen 0,0529). O auditor concordou com os 6.

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | HIGH | REBATIDA_EVIDENCIA | rodada=1 | `scripts/gerar-starter.py` `conferir_destino` roda `git status --porcelain --untracked-files=all` e sai 64 com arquivo não rastreado; medido: com `docs/guia-do-aluno.pt-BR.md` não rastreado no clone de ensaio, o gerador saiu 64 e o arquivo ficou | nao | EXTERNAL_REVIEW_20261113-143814 |
| R2 | MED | APLICADA | rodada=1 | teste: `test_sem_consultar_o_github_nunca_conclui_que_o_push_nao_publica` · sem `gh` utilizável o modo iniciante caía em "Nenhum" e o bloco do OK dizia que o push não publica | sim | EXTERNAL_REVIEW_20261113-143814 |
| R3 | MED | REBATIDA_ESCOPO | rodada=1 | a réplica do teste só tem `SKILL.md` mínimo; com as versões reais da `v1.5.17` (iguais às do Open) toda geração sairia 65; a prova contra a `v1.5.17` real é a geração de ensaio num clone dela com as 9 checagens do CI de lá verdes (`evidence/F17B_STARTER_ETAPA2/ENSAIO-v1.5.17.log`) e a 2ª geração real antes do PR | nao | EXTERNAL_REVIEW_20261113-143814 |
| R4 | LOW | REBATIDA_EVIDENCIA | rodada=1 | `.gitattributes:3` `* text=auto eol=lf` vale para todo checkout (inclusive Windows com `core.autocrlf`); o gerador lê os blobs por `git archive`; nenhum arquivo de `.agents/skills` tem `\r` (medido no passo 0) | nao | EXTERNAL_REVIEW_20261113-143814 |
| R5 | LOW | APLICADA | rodada=1 | teste: `test_at003_modo_quebrado_sai_65_sem_gravar` (caso "description acima de 1.024") · o limite estava só no teste de texto do Open | nao | EXTERNAL_REVIEW_20261113-143814 |
| R6 | LOW | APLICADA | rodada=1 | teste: `test_at001_gera_as_15_e_nao_toca_no_resto` (quickstart com "18 skills") · os 2 quickstarts diziam 15 | nao | EXTERNAL_REVIEW_20261113-143814 |

Rodada 2 (diff inteiro `v2.13.0..f9a0af1`, 63 arquivos, mesmas exclusões das cópias byte a byte, depois dos consertos
da rodada 1, do raio de impacto, do teste do iniciante e dos 2 ciclos do avaliador): saldo US$ 14,17 antes; custo
US$ 1,6469 (claude 1,6012 nominal, qwen 0,0457). O auditor concordou com R1 e R3 e discordou de R2 com evidência.

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | MED | REBATIDA_ESCOPO | rodada=2 | o mesmo R3 da rodada 1: a réplica do teste não pode ter as versões reais da `v1.5.17` (iguais às do Open: toda geração sairia 65); a geração de ensaio sobre a `v1.5.17` real com as 9 checagens de lá (`ENSAIO-v1.5.17.log`, refeita em `f9a0af1`) cobre o version gate, e a 2ª geração real roda antes do PR | nao | EXTERNAL_REVIEW_20261113-160601 |
| R2 | MED | REBATIDA_EVIDENCIA | rodada=2 | a `sdd-build` 1.2.0 congelada do starter tem "## 11. Aplicar a migration no banco" e grava a seção `## Migrations aplicadas` do BUILD_REPORT (`git show v1.5.17:skills/sdd-build/SKILL.md`, linhas 324, 342 e 471): a release iniciante encontra o registro que pede; o auditor discordou com o mesmo motivo | nao | EXTERNAL_REVIEW_20261113-160601 |
| R3 | LOW | APLICADA | rodada=2 | teste: `test_at001_gera_as_15_e_nao_toca_no_resto` · o quickstart em inglês mandava copiar só 6 das 18 pastas | nao | EXTERNAL_REVIEW_20261113-160601 |

Rodada 3, a última (diff inteiro `v2.13.0..e583889`, as mesmas exclusões, depois do R3 da rodada 2): saldo US$ 14,12 antes;
custo US$ 1,6535 (claude 1,6177 nominal, qwen 0,0358). R1, R2 e R3 repetem achados já decididos com medição (rodada 1: R3,
R1, R4); o auditor concordou com R1 e R3, discordou de R2 e trouxe N1.

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | MED | REBATIDA_ESCOPO | rodada=3 | o mesmo da rodada 1 (R3) e da rodada 2 (R1): a réplica não pode ter as versões reais da `v1.5.17`; o version gate contra a `v1.5.17` real é a geração de ensaio (`ENSAIO-v1.5.17.log`) e a 2ª geração real antes do PR | nao | EXTERNAL_REVIEW_20261113-161527 |
| R2 | MED | REBATIDA_EVIDENCIA | rodada=3 | o mesmo da rodada 1 (R1): `conferir_destino` sai 64 com arquivo não rastreado (`--untracked-files=all`), medido com o `docs/guia-do-aluno.pt-BR.md` no clone de ensaio; o auditor discordou | nao | EXTERNAL_REVIEW_20261113-161527 |
| R3 | LOW | REBATIDA_EVIDENCIA | rodada=3 | o mesmo da rodada 1 (R4): `.gitattributes:3` `* text=auto eol=lf`; o gerador lê blobs por `git archive`; nenhum arquivo de `.agents/skills` tem `\r` | nao | EXTERNAL_REVIEW_20261113-161527 |
| N1 | MED | REBATIDA_EVIDENCIA | rodada=3 | o quickstart é do starter, que tem 18 skills (15 geradas + 3 congeladas: `ls skills/` da geração de ensaio = 18; `check-versions --base v1.5.17` "18 skills" em `AVAL2-AT008-saida-gerada.log`); 22 é o Open | nao | EXTERNAL_REVIEW_20261113-161527 |
