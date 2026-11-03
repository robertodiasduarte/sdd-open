# Ledger da revisão adversarial do build — F12_CONTEXTO

Rodada 1: `sdd/reports/reviews/EXTERNAL_REVIEW_20261103-112330` (revisor claude, 2º revisor codex — 90 arquivos —,
auditor openrouter:qwen/qwen3.7-plus; diff de `0f51ac9`; 11 achados, 2 HIGH; o auditor concordou com os 11; US$ 2,58).
Rodada 2: `sdd/reports/reviews/EXTERNAL_REVIEW_20261103-114007` (mesmas engines; diff de `89702c4`; 9 achados, 1 HIGH; o auditor
refutou 1 com evidência; US$ 2,56).
Rodada 3 (teto): `sdd/reports/reviews/EXTERNAL_REVIEW_20261103-115727` (mesmas engines; diff de `363d8bc`; 0 HIGH, 4 MED, 4 LOW;
`loop` PRONTO; `--conferir` CONFERE; US$ 2,65). Esta é a revisão da release. Decisão D4 do Roberto (2026-11-03): "corrigir agora e rodar a 4ª rodada" — os 6 achados
válidos da rodada 3 foram aplicados; os 2 já rebatidos com evidência ficam rebatidos.
Rodada 4: `sdd/reports/reviews/EXTERNAL_REVIEW_20261103-125947` (mesmas engines; diff de `0ca09f9`; 1 HIGH, 2 MED, 1 LOW; o
HIGH era regressão do conserto da rodada 3; US$ 2,69).
Rodada 5 (D4 do Roberto, "continue" na opção recomendada): `sdd/reports/reviews/EXTERNAL_REVIEW_20261103-164047` (mesmas
engines; diff de `d816f77`; 1 HIGH, 2 MED, 2 LOW + 1 novo do auditor; US$ 2,72). `3ebeeea` e `96a97ec` não têm revisão externa
própria: dispensa registrada em `release-ledger-v2.4.0.yaml`, a confirmar no OK da release.
Lido por `sdd/bin/sdd-fluxo.sh loop` por célula.

| achado | sev | veredito | rodada | evidência / motivo |
|---|---|---|---|---|
| R1@claude | MED | APLICADA | rodada=1 | o `rm -f` do snapshot passou para depois da validação do destino; `test_r1_snapshot_dentro_do_worktree_nao_apaga_o_arquivo` (vermelho em `baseline-real1.log`) |
| R2@claude | MED | APLICADA | rodada=1 | passo 11, item 6: refazer o snapshot de antes depois de gravar o padrão; `test_padrao_ausente_refaz_o_snapshot` |
| R3@claude | MED | REBATIDA_EVIDENCIA | rodada=1 | `tests/test_matriz_new_session.py` não fixa versão de nenhuma skill tocada (`grep -n versao tests/test_matriz_new_session.py` sem pino de define, design, governanca, build ou iterate); o item 76 do manifest ficou sem mudança necessária, e a suíte inteira passa no Verify Gate |
| R4@claude | LOW | REBATIDA_EVIDENCIA | rodada=1 | `DEFINE_FIXTURE_GOVERNANCA.md` é a entrada da revisão de governança (um DEFINE de cobrança ainda não revisado): `pendente` é o valor verdadeiro, e o AT-013 fala de DEFINEs com linha válida; a fixture documenta o exit 5 e `test_governanca_gate.test_fixtures_mantem_o_exit` o fixa |
| R5@claude | LOW | APLICADA | rodada=1 | a âncora curta `pedidos.py:6` virou caminho completo nas 13 fixtures de contexto (não depende de nome único no projeto instalado) |
| R6@claude | LOW | APLICADA | rodada=1 | diagrama dos READMEs sem "(if money)"/"(se há dinheiro)" e realinhado |
| R7@claude | LOW | APLICADA | rodada=1 | `sdd-iterate` `metadata.updated` 2026-11 |
| R1@codex | HIGH | APLICADA | rodada=1 | mesmo conserto do R1@claude |
| R2@codex | HIGH | APLICADA | rodada=1 | `shasum` que falha ou hash vazio recusa o snapshot (64); `test_r2_arquivo_ilegivel_recusa_o_snapshot` |
| R3@codex | MED | APLICADA | rodada=1 | `--validade`: arquivo apagado depois do sha é VENCIDO (o pathspec é conferido no sha com `git grep` e no índice); `test_r3_ultimo_arquivo_da_superficie_apagado_e_vencido` |
| R4@codex | LOW | APLICADA | rodada=1 | âncora na linha 0 é `path-morto` nos dois lints; `test_r4_ancora_na_linha_zero_e_path_morto` (2) |
| R1@claude | MED | APLICADA | rodada=2 | passo 1.5, item 4.4: o redespacho do cartógrafo refaz antes o brief e o snapshot; `test_redespacho_do_cartografo_refaz_brief_e_snapshot` |
| R2@claude | LOW | APLICADA | rodada=2 | `governanca-bloco.py`: bloco vazio ou sem `resultado` sai 2 (era KeyError e 1); `test_invalidos_saem_2` com os 2 casos novos |
| R3@claude | LOW | REBATIDA_EVIDENCIA | rodada=2 | mesma nota do R4@claude da rodada 1; o auditor a refutou com evidência (DISAGREE_EVIDENCE): o AT-013 fala de DEFINE com linha válida, e a fixture de entrada da revisão é `pendente` de propósito |
| R4@claude | LOW | APLICADA | rodada=2 | `--self-test` sem as fixtures versionadas sai 64 dizendo por quê; `test_self_test_sem_fixtures_versionadas_sai_64` |
| R1@codex | HIGH | APLICADA | rodada=2 | `verify-gate.sh`: cerca `~~~` também esconde a linha Governança; `test_real2_linha_em_cerca_til_nao_vale` (vermelho em `baseline-real2.log`) |
| R2@codex | MED | APLICADA | rodada=2 | `canon()` pelo `os.path.realpath`: link de arquivo permitido casa com o destino; `test_permitido_por_link_de_arquivo_casa_com_o_destino` |
| R3@codex | MED | APLICADA | rodada=2 | `--design`: todo defeito de pattern NÃO citado só avisa (seções e landmines também); `test_design_sem_citacao_com_pattern_defeituoso_na_pasta_sai_0` |
| R4@codex | MED | APLICADA | rodada=2 | `--validade` confere o diff antes do pathspec: superfície vazia ou binária apagada é VENCIDO; `test_superficie_vazia_ou_binaria_apagada_e_vencida` |
| R5@codex | LOW | APLICADA | rodada=2 | mesmo conserto do R2@claude |
| R1@claude | MED | APLICADA | rodada=3 | D4 do Roberto (corrigir e rodar a 4ª): snapshot e cópia do DEFINE em caminho fixo que uma sessão nova refaz (no `.git` em `0ca09f9`; na pasta temporária em `96a97ec`, porque a sandbox do Codex recusa o `.git`); `test_snapshot_num_lugar_fixo_e_lint_no_redespacho` |
| R2@claude | MED | REBATIDA_EVIDENCIA | rodada=3 | mesma nota do R3@claude da rodada 1: `tests/test_matriz_new_session.py` só fixa a versão da `sdd-new-session` (1.3.0), que não foi tocada; a suíte passa no Verify Gate |
| R3@claude | LOW | APLICADA | rodada=3 | o lint vai no redespacho como 5º campo `lint:`, previsto no brief do cartógrafo e no yaml (`campo_redespacho`) |
| R4@claude | LOW | REBATIDA_EVIDENCIA | rodada=3 | o auditor refutou com evidência (DISAGREE_EVIDENCE), como nas rodadas 1 e 2 |
| R5@claude | LOW | APLICADA | rodada=3 | `test_exits_do_yaml_batem_com_o_verify_gate` (guarda nova; prova por mutação em `mutacao-exits-yaml.log`) |
| R1@codex | MED | APLICADA | rodada=3 | o snapshot canoniza cada caminho (realpath) e registra o destino de cada link: um link não versionado para o permitido não vira FORA; `test_alias_por_link_do_permitido_casa_com_ele` (vermelho em `baseline-real3-alias.log`) |
| R2@codex | MED | APLICADA | rodada=3 | `awk 'END { print NR }'` no lugar de `wc -l` nos 2 lints; `test_ancora_na_ultima_linha_sem_quebra_final_vale` (2) |
| R3@codex | LOW | APLICADA | rodada=3 | `sup:` exige um termo de verdade entre crases; `test_sup_so_com_crases_vazias_e_sup_ausente` |
| R1@claude | MED | APLICADA | rodada=4 | dentro de cerca, só `caminho:linha` é âncora (import relativo é código) nos 2 lints; `test_import_relativo_no_esqueleto_nao_e_ancora` |
| R2@claude | LOW | APLICADA | rodada=4 | a saída de dispensa do exit 5 diz como criar a seção que um DEFINE antigo não tem; `test_governanca_gate` |
| R1@codex | HIGH | APLICADA | rodada=4 | o permitido é resolvido no snapshot de ANTES (linha `#PERMITIDO`), nunca depois; caminho que vira link é FORA; `test_link_criado_no_permitido_nao_autoriza_outro_arquivo` (vermelho em `baseline-real4.log`) |
| R2@codex | MED | APLICADA | rodada=4 | nome de pattern citado aceita ponto; `test_citacao_com_ponto_no_nome_conta` |
| R1@claude | MED | REBATIDA_EVIDENCIA | rodada=5 | o auditor refutou com evidência: o `revisor.md` manda copiar à letra os títulos do template (`## Lacunas`, `### Gnn — `); o validador recusar outro título é o contrato |
| R2@claude | LOW | APLICADA | rodada=5 | os links do índice de ADR são relativos à pasta do `--out`; `test_links_relativos_a_pasta_do_out` |
| R1@codex | HIGH | APLICADA | rodada=5 | passo 11: `rm -f` do DEFINE antes do `cp` da restauração (um link posto no lugar dele não desvia a escrita); `test_restauracao_do_define_desfaz_link_antes_do_cp` (vermelho em `baseline-real5.log`) |
| R2@codex | MED | APLICADA | rodada=5 | o auditor discordou, mas `patterns-lint.sh:82` só reconhecia a cerca de crases (o mesmo defeito do N1): títulos dentro de `~~~` não contam como seção nos 2 lints; `test_titulo_dentro_de_cerca_til_nao_conta_como_secao` (2) |
| R3@codex | LOW | APLICADA | rodada=5 | mesmo conserto do R2@claude |
| N1 | MED | APLICADA | rodada=5 | mesmo conserto do R2@codex, no `contexto-lint.sh` |
