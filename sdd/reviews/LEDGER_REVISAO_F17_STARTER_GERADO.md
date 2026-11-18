# Ledger da revisão — F17_STARTER_GERADO

> Uma linha por achado decidido, de todas as rodadas da revisão adversarial desta frente. Conferido por
> `bash sdd/bin/ledger-revisao-lint.sh`; lido por `sdd-fluxo.sh loop --ledger` e por `eval-revisores.sh`.
> Critério da coluna `dano`: `sdd/review/CRITERIO_DANO.md`.

Cadeia: claude revisa, `openrouter` (qwen/qwen3.7-plus) audita, sem 2º revisor (`--no-revisor2`: codex sem cota; 2º
revisor pago evitado pela LM-010) e sem desempate (`--no-desempate`). Rodada 1 (diff `e22a1b2..2be8f36`, 80 arquivos,
207 KB, mais DEFINE/DESIGN/BRAINSTORM): saldo da OpenRouter US$ 15,02 antes; custo US$ 1,5683 (claude 1,5248 por
assinatura nominal, qwen 0,0435). O auditor concordou com os 5.

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | HIGH | APLICADA | rodada=1 | teste: `test_r1_testes_de_skill_sem_nenhuma_pasta_tests_nao_quebram` · hoje não quebra (sdd-build, sdd-define e ux-review-builder têm `tests/` na v1.5.16; a geração real passou os testes de skill), mas a F17b pode tirar todas | nao | EXTERNAL_REVIEW_20261112-175357 |
| R2 | MED | APLICADA | rodada=1 | teste: `test_r2_arquivo_que_saiu_da_semente_sai_do_destino` · arquivo que sai de `scripts/starter/raiz/` sai do destino; antes ficava e a trava o recusava | nao | EXTERNAL_REVIEW_20261112-175357 |
| R3 | MED | REBATIDA_EVIDENCIA | rodada=1 | `.agents/skills/sdd-seguranca/manifest.json` não tem a chave `version` (0 ocorrências); o check-versions do starter só compara quando ela existe (`scripts/starter/raiz/scripts/check-versions.py:105`); a geração real passou no check-versions contra a v1.5.16 | nao | EXTERNAL_REVIEW_20261112-175357 |
| R4 | LOW | APLICADA | rodada=1 | teste: `test_readme_sem_ambiente_md` · o README gerado dizia que a new-session grava `sdd/ambiente.md` | nao | EXTERNAL_REVIEW_20261112-175357 |
| R5 | LOW | APLICADA | rodada=1 | teste: `test_gerador_diferente_do_da_tag` (exige `worktree add`) · a recuperação de /tmp tirava o gerador do repositório e dizia "tag inexistente" | nao | EXTERNAL_REVIEW_20261112-175357 |

Rodada 2 (diff `e22a1b2..ec557ad`, 220 KB, depois dos consertos da rodada 1, do raio de impacto e do ciclo 1 do avaliador):
saldo US$ 14,83 antes; custo US$ 1,8516 (claude 1,8057 nominal, qwen 0,0459). O auditor concordou com 4 e discordou de R5
com evidência (o hash do GERADO.txt é do arquivo já escrito).

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | MED | APLICADA | rodada=2 | `scripts/starter/trocas/sdd-kb.md` entrou no `MANIFEST.txt` (o `publish-gate` em modo ci reprovaria o pacote); `comm` entre `git ls-files` e o MANIFEST vazio | nao | EXTERNAL_REVIEW_20261112-183050 |
| R2 | MED | REBATIDA_EVIDENCIA | rodada=2 | as 2 fichas que leem `.sql` (S01 `regra:rls`, S03 `regra:definer`) usam `sem_comentarios_sql`, nunca `comentado()` (`CATALOGO_SEGURANCA.md:41,71`); medido também no raio de impacto (superfície 3) | nao | EXTERNAL_REVIEW_20261112-183050 |
| R3 | LOW | APLICADA | rodada=2 | teste: `test_frente_usa_a_branch_padrao_do_config_e_avisa_da_ref_velha` (exige a 2ª causa) · o aviso só sugeria `set-head`, que não resolve divergência real | nao | EXTERNAL_REVIEW_20261112-183050 |
| R4 | LOW | APLICADA | rodada=2 | teste: `test_r4_aceite_nao_isenta_outra_citacao_na_mesma_linha` · o aceite de uma citação calava outra na mesma linha; o conserto achou a 2ª citação da linha 52 do `alarme.sh`, agora coberta pelo trecho do aceite | nao | EXTERNAL_REVIEW_20261112-183050 |
| R5 | LOW | REBATIDA_EVIDENCIA | rodada=2 | nenhum arquivo de texto das skills tem `\r` (medido em `git ls-files .agents/skills`); o auditor discordou com evidência | nao | EXTERNAL_REVIEW_20261112-183050 |

Rodada 3 (só o delta `ec557ad..62bfda4`, 6 arquivos, 6 KB): saldo US$ 14,79 antes; custo US$ 0,3968 (claude 0,3855 nominal,
qwen 0,0113). O auditor concordou com os 2.

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | MED | REBATIDA_EVIDENCIA | rodada=3 | o bump já existe nesta frente: `sdd-checar-ambiente` 1.5.0 na v2.12.1 → 1.5.1 (`13e1c2e`); `check-versions.py --base v2.12.1 --base-obrigatoria` VERDE; o delta revisado só não o mostrava | nao | EXTERNAL_REVIEW_20261112-184704 |
| R2 | LOW | APLICADA | rodada=3 | teste: `test_r4_aceite_nao_isenta_outra_citacao_na_mesma_linha` (o mesmo trecho duas vezes na linha) · `ln.index` via só a 1ª ocorrência; o efeito era reprovar demais, nunca deixar passar | nao | EXTERNAL_REVIEW_20261112-184704 |

Rodada 4, acima do teto por decisão do Roberto (2026-11-12), só o delta `62bfda4..0396642` (o conserto do R2 da rodada 3):
saldo US$ 14,78 antes; custo US$ 0,2946 (claude 0,2860 nominal, qwen 0,0086); nenhum achado.

sem achados: rodada=4 EXTERNAL_REVIEW_20261112-202310

Rodada 5, acima do teto por decisão do Roberto (o conferidor marcou a rodada 4 como rasa), diff inteiro `e22a1b2..0396642`:
saldo US$ 14,77 antes; custo US$ 2,0278 (claude 1,9867 nominal, qwen 0,0411). O auditor concordou com R1 e R2 e discordou
de R3 (DISAGREE_CONCERN) e R4 (DISAGREE_EVIDENCE).

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | MED | REBATIDA_ESCOPO | rodada=5 | o `ci.yml` e o `auto-release.yml` da v1.5.16 também não rodam `tests/` da raiz (`git show v1.5.16:.github/workflows/ci.yml`, linhas 35-37: só `skills/*/tests`); a semente é fiel; rodar a suíte da raiz no CI do starter é escopo novo, pendência para a F17b | nao | EXTERNAL_REVIEW_20261112-204706 |
| R2 | LOW | APLICADA | rodada=5 | teste: `test_aval1_lint_pega_caminho_da_skill_gerada_fora_do_par` (par de `sdd-playbook`) · o par isentava qualquer `sdd-X`; hoje sem ocorrência | nao | EXTERNAL_REVIEW_20261112-204706 |
| R3 | LOW | REBATIDA_EVIDENCIA | rodada=5 | nenhum arquivo de texto das skills tem `\r` (medido); o auditor discordou (DISAGREE_CONCERN); igual ao R5 da rodada 2 | nao | EXTERNAL_REVIEW_20261112-204706 |
| R4 | LOW | REBATIDA_ESCOPO | rodada=5 | `rglob` sem excluir `node_modules/` já valia para `CLAUDE.md` antes desta frente; o auditor discordou com evidência; pendência para a próxima frente que tocar a auditoria | nao | EXTERNAL_REVIEW_20261112-204706 |

Rodada 6, acima do teto por decisão do Roberto (o conserto do R2 da rodada 5 mudou o código), diff inteiro
`e22a1b2..02ad073`: saldo US$ 14,73 antes; custo US$ 2,0426 (claude 1,9857 nominal, qwen 0,0569). O auditor concordou com
os 3. Decisão do Roberto: consertar os 2 reais, rodada 7, e parar aí (leves da rodada 7 viram pendência).

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | LOW | APLICADA | rodada=6 | teste: `test_r6_ds_store_no_destino_nao_conta_como_mudanca` · um `.DS_Store` do Finder no clone travava a geração seguinte pedindo versão nova sem mudança | nao | EXTERNAL_REVIEW_20261112-210000 |
| R2 | LOW | APLICADA | rodada=6 | teste: `test_r6_tag_anterior_ao_gerador_diz_a_causa` · tag sem o gerador dava traceback com exit 1 | nao | EXTERNAL_REVIEW_20261112-210000 |
| R3 | LOW | REBATIDA_EVIDENCIA | rodada=6 | todos os arquivos das 10 skills têm extensão de `TEXTO` (medido em `git ls-files .agents/skills`: nenhum fora de md, py, sh, json, yaml, yml, txt, toml, tsv); pendência se uma skill gerada ganhar outro tipo | nao | EXTERNAL_REVIEW_20261112-210000 |

Rodada 7, a última por decisão do Roberto (leves viram pendência, sem rodada 8), diff inteiro `e22a1b2..d813954`: saldo
US$ 14,67 antes; custo US$ 1,9569 (claude 1,9137 nominal, qwen 0,0432). O revisor deu 2 leves; o auditor concordou, subiu os
2 para médio e acrescentou o N1 (médio). Conferidos no código: nenhum ocorre hoje, e os dois que poderiam ocorrer falham alto
(65, nada gravado), que é o desenho do gerador.

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | LOW | REBATIDA_EVIDENCIA | rodada=7 | nenhum arquivo de texto das 10 skills tem `\r` (3ª medição); pendência: copiar byte a byte o que nenhuma regra muda | nao | EXTERNAL_REVIEW_20261112-211515 |
| R2 | LOW | REBATIDA_ESCOPO | rodada=7 | nenhum `CHANGELOG.md` das 10 skills cita `sdd/templates/` (grep vazio); se citar, o lint sai 65 e nada é gravado; pendência: `trazer_moldes` ignorar o CHANGELOG | nao | EXTERNAL_REVIEW_20261112-211515 |
| N1 | MED | REBATIDA_ESCOPO | rodada=7 | nenhum script das 10 skills cita outra skill da lista (grep vazio); se citar, o lint sai 65 e nada é gravado; pendência: reescrever caminho de irmã também nos scripts | nao | EXTERNAL_REVIEW_20261112-211515 |
