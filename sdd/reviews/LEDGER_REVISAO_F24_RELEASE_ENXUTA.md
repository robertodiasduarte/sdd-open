# Ledger da revisão — F24_RELEASE_ENXUTA

Rodada 1 (código, `45bf1fe`): claude revisa, codex como 2º revisor (gatilho: 44 arquivos, limiar 8), openrouter
qwen/qwen3.7-plus audita. O auditor concordou com 13 achados e discordou de R5@claude. A revisão do DESIGN (`rodada=D1`,
claude revisa, qwen audita, codex desempata) também está no Advisor Ledger do DESIGN.

sem resultado: rodada=D1 EXTERNAL_REVIEW_20261116-190805 — o auditor falhou por credencial (OPENROUTER_API_KEY fora do ambiente); refeita em EXTERNAL_REVIEW_20261116-191150
sem resultado: rodada=2 EXTERNAL_REVIEW_20261116-195427 — interrompida: a main recebeu a F23B3 no meio da rodada, e a F24 foi rebaseada (o diff revisado deixou de ser o que vai subir)
revisor2: dispensado rodada=2 — sem superfície de risco (regra antiga: 44 arquivos (limiar 8))
revisor2: dispensado rodada=3 — sem superfície de risco (regra antiga: 44 arquivos (limiar 8))
sem resultado: rodada=4 EXTERNAL_REVIEW_20261116-210442 — o auditor (qwen) passou do teto de tempo; os achados dos 2 revisores foram decididos abaixo e a rodada foi refeita como 4a, com o codex na cadeia do auditor (4ª rodada acima do teto: OK do Roberto, 2026-11-16)
rodada 5 (EXTERNAL_REVIEW_20261116-220949, acima do teto com o OK do Roberto): corrigida sem 6ª rodada por decisão do Roberto (2026-11-17); as correções têm teste vermelho em 60e4839 e verde depois (REVISAO5-VERMELHO-60e4839.log, REVISAO5-VERDE.log)

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | HIGH | REBATIDA_ESCOPO | rodada=D1 | revisão do DESIGN: o código vem no build; o módulo ausente é o baseline vermelho declarado no DEFINE (desempate: REFUTADO) | nao | EXTERNAL_REVIEW_20261116-191150 |
| R2 | HIGH | REBATIDA_EVIDENCIA | rodada=D1 | os artefatos SDD ficam sem commit nesta branch (DEFINE › Constraints › Process); o gate roda de `git archive HEAD` | nao | EXTERNAL_REVIEW_20261116-191150 |
| R3 | MED | APLICADA | rodada=D1 | DESIGN Decision 3 (proveniência); teste no build: `test_entrada_fabricada_num_commit_so` | nao | EXTERNAL_REVIEW_20261116-191150 |
| R4 | MED | APLICADA | rodada=D1 | DESIGN Decision 2 (só entradas boas excluem; a colheita que termina apaga as falhas) | nao | EXTERNAL_REVIEW_20261116-191150 |
| R5 | MED | APLICADA | rodada=D1 | AT-004 do DEFINE por linha; DESIGN Decision 1 | nao | EXTERNAL_REVIEW_20261116-191150 |
| R6 | LOW | APLICADA | rodada=D1 | AT-009 do DEFINE cita o DEFINE arquivado | nao | EXTERNAL_REVIEW_20261116-191150 |
| N1 | MED | APLICADA | rodada=D1 | `handoff-lint.py --curta` (DESIGN manifest 5) | nao | EXTERNAL_REVIEW_20261116-191150 |
| R1@claude | MED | APLICADA | rodada=1 | teste: `test_r1_claude_mesma_impressao_em_duas_entradas_conta_na_mais_antiga` · a impressão conta só na entrada mais antiga da fila (`--conferir-entrada`) | sim | EXTERNAL_REVIEW_20261116-193502 |
| R2@claude | MED | APLICADA | rodada=1 | teste: `test_r2_claude_log_sem_commit_vai_para_ausentes_e_nao_recusa_a_entrada` · documento não commitado como está vai para `ausentes.txt` (por linha), nunca recusa a entrada | sim | EXTERNAL_REVIEW_20261116-193502 |
| R3@claude | MED | APLICADA | rodada=1 | teste: `test_r3_claude_retomar_nao_refaz_o_staging` · `--conferir-entrada --retomar` só diz onde está o staging | sim | EXTERNAL_REVIEW_20261116-193502 |
| R4@claude | MED | APLICADA | rodada=1 | teste: `test_r4_claude_ficha_curta_aberta_com_prompt_passa` · `--curta` conta fora do prompt de retomada; o Status vem no item 14, antes do lint | nao | EXTERNAL_REVIEW_20261116-193502 |
| R5@claude | MED | REBATIDA_EVIDENCIA | rodada=1 | a impressão do candidato é `digital(base, "cand", bloco)`, sem o ID proposto (`sdd/bin/playbook-curator.sh:652`); o auditor discordou pelo mesmo motivo | nao | EXTERNAL_REVIEW_20261116-193502 |
| R6@claude | LOW | APLICADA | rodada=1 | teste: `test_r5_codex_escrita_do_curador_isola_a_entrada` · a entrada fica na fila, o playbook volta ao commit e o lote segue | nao | EXTERNAL_REVIEW_20261116-193502 |
| R7@claude | LOW | APLICADA | rodada=1 | teste: `test_r7_claude_o_papel_e_conferido_com_a_lista_real` · nomes reais no OK e nova conferência com `git diff --cached` antes do envio | sim | EXTERNAL_REVIEW_20261116-193502 |
| R1@codex | HIGH | APLICADA | rodada=1 | teste: `test_r3_claude_retomar_nao_refaz_o_staging` · o mesmo de R3@claude | sim | EXTERNAL_REVIEW_20261116-193502 |
| R2@codex | HIGH | APLICADA | rodada=1 | teste: `test_r1_claude_mesma_impressao_em_duas_entradas_conta_na_mais_antiga` · o mesmo de R1@claude | sim | EXTERNAL_REVIEW_20261116-193502 |
| R3@codex | HIGH | APLICADA | rodada=1 | teste: `test_r7_claude_o_papel_e_conferido_com_a_lista_real` · o mesmo de R7@claude | sim | EXTERNAL_REVIEW_20261116-193502 |
| R4@codex | HIGH | APLICADA | rodada=1 | teste: `test_nada_aceito_tem_caminho_e_evidencia_nao_versionada_tambem` · no conflito, registro e fila nunca por checkout: `--registrar` na base, entrada já julgada sai do lote (`lote-delta-<entrada>.txt`) | sim | EXTERNAL_REVIEW_20261116-193502 |
| R5@codex | MED | APLICADA | rodada=1 | teste: `test_r5_codex_escrita_do_curador_isola_a_entrada` · o mesmo de R6@claude | nao | EXTERNAL_REVIEW_20261116-193502 |
| R6@codex | MED | APLICADA | rodada=1 | teste: `test_r6_codex_aspas_sem_fechar_e_ledger_ilegivel` · aspas sem fechar ⇒ ledger ilegível, `n/d` e exit 2 | sim | EXTERNAL_REVIEW_20261116-193502 |
| R7@codex | MED | APLICADA | rodada=1 | teste: `test_r7_codex_arquivo_novo_acentuado_conta` · `core.quotePath=false`; arquivo que o git não mede conta como binário | sim | EXTERNAL_REVIEW_20261116-193502 |
| R1 | MED | APLICADA | rodada=2 | teste: `test_r1_documento_sem_commit_avisa_e_nao_vira_julgado` · `--enfileirar` avisa o documento fora do commit; `--registrar` não registra o que ficou sem evidência | sim | EXTERNAL_REVIEW_20261116-202240 |
| R2 | MED | APLICADA | rodada=2 | teste: `test_r2_sem_documentos_na_trilha_completa_e_falha` · sem documentos na trilha completa é `Curadoria: FALHOU (sem documentos)` | nao | EXTERNAL_REVIEW_20261116-202240 |
| R3 | LOW | APLICADA | rodada=2 | teste: `test_r3_impressao_da_entrada_mais_antiga_nao_e_registrada_pela_nova` · a impressão fica com a entrada mais antiga até ela ser julgada | sim | EXTERNAL_REVIEW_20261116-202240 |
| R4 | MED | APLICADA | rodada=2 | teste: `test_r4_brief_e_fronteira_por_entrada` · `BRIEF_curador_<F>_<entrada>.md` e `curador-<entrada>` | nao | EXTERNAL_REVIEW_20261116-202240 |
| N1 | MED | APLICADA | rodada=2 | teste: `test_n1_o_lote_comeca_com_o_playbook_limpo` · `git diff --quiet` antes de começar; a volta ao commit não apaga mudança alheia | nao | EXTERNAL_REVIEW_20261116-202240 |
| R1 | MED | APLICADA | rodada=3 | teste: `test_r1_entrada_recusada_nao_prende_as_impressoes` · `--recusar` marca a entrada; a colheita seguinte traz as linhas e tira a recusada | sim | EXTERNAL_REVIEW_20261116-203629 |
| R2 | MED | REBATIDA_ESCOPO | rodada=3 | a release commita os documentos SDD no commit atômico (FASE 1, item 4), e o `--enfileirar` avisa (⚠️) o que não está commitado; o Open guarda os seus documentos fora da `main` de propósito e cura no worktree de documentos; o auditor discordou do achado | nao | EXTERNAL_REVIEW_20261116-203629 |
| R3 | MED | APLICADA | rodada=3 | teste: `test_r3_contrato_do_curador_por_entrada` · `WORKFLOW_CONTRACTS.yaml` com brief e snapshot por entrada | nao | EXTERNAL_REVIEW_20261116-203629 |
| R4 | LOW | APLICADA | rodada=3 | teste: `test_r4_linha_sem_evidencia_volta_na_colheita_seguinte` · a exclusão pela fila não prende o que ficou em `ausentes.txt` | sim | EXTERNAL_REVIEW_20261116-203629 |
| R5 | LOW | APLICADA | rodada=3 | teste: `test_r5_branch_integrada_por_conteudo` · `git cherry` no item 17 (a branch aterrissada por cherry-pick nunca é ancestral) | sim | EXTERNAL_REVIEW_20261116-203629 |
| N1 | MED | APLICADA | rodada=3 | item 0 da sdd-release diz o exit de cada caso do `trilha.sh` (1 completa; 2 ou 64 não decidiu) | nao | EXTERNAL_REVIEW_20261116-203629 |
| R1@claude | MED | APLICADA | rodada=4 | teste: `test_textos_da_rodada_4` · `git fetch` da branch e `git cherry` que sai ≠ 0 não apaga | sim | EXTERNAL_REVIEW_20261116-210442 |
| R2@claude | MED | APLICADA | rodada=4 | teste: `test_r2_claude_sha_do_commit_publicado` · `ficha-publicado.py --ref origin/<branch padrão>` | sim | EXTERNAL_REVIEW_20261116-210442 |
| R3@claude | MED | APLICADA | rodada=4 | teste: `test_textos_da_rodada_4` · o item 3 manda gravar `data`, `veredito` e `deploy` no ledger | nao | EXTERNAL_REVIEW_20261116-210442 |
| R4@claude | LOW | APLICADA | rodada=4 | DEFINE v1.4: o AT-009 conta a ficha curta fora do prompt de retomada, como o `--curta` | nao | EXTERNAL_REVIEW_20261116-210442 |
| R5@claude | LOW | APLICADA | rodada=4 | teste: `test_textos_da_rodada_4` · o item 16 remove o worktree temporário do aterrissamento | nao | EXTERNAL_REVIEW_20261116-210442 |
| R1@codex | HIGH | APLICADA | rodada=4 | teste: `test_textos_da_rodada_4` · os itens aceitos vão para o `lote-delta-<entrada>.txt` e as invariantes para `lote-inv-<entrada>.txt` | sim | EXTERNAL_REVIEW_20261116-210442 |
| R2@codex | MED | APLICADA | rodada=4 | teste: `test_r2_codex_impressao_sem_evidencia_na_antiga_nao_tira_da_nova` · a exclusão pela entrada antiga desconta o `ausentes.txt` dela | sim | EXTERNAL_REVIEW_20261116-210442 |
| R3@codex | MED | APLICADA | rodada=4 | teste: `test_r3_codex_registrar_duas_entradas_sobrepostas_grava_cada_impressao_uma_vez` · o `--registrar` não regrava impressão já registrada | sim | EXTERNAL_REVIEW_20261116-210442 |
| R4@codex | MED | APLICADA | rodada=4 | teste: `test_r4_codex_mais_no_filtro_e_nao_sei` · `+` no filtro vira `NAO_SEI` | sim | EXTERNAL_REVIEW_20261116-210442 |
| R1@claude | MED | APLICADA | rodada=4a | teste: `test_r1_claude_arquivo_desconhecido_recusa_a_entrada` · arquivo que a colheita não cria recusa a entrada | sim | EXTERNAL_REVIEW_20261116-214955 |
| R2@claude | MED | APLICADA | rodada=4a | teste: `test_r2_claude_sem_workflow_que_publica_e_nao_sei` · sem workflow que publica, `NAO_SEI` | sim | EXTERNAL_REVIEW_20261116-214955 |
| R3@claude | MED | REBATIDA_EVIDENCIA | rodada=4a | a impressão do candidato não inclui o ID proposto (`sdd/bin/playbook-curator.sh:652`); o auditor discordou | nao | EXTERNAL_REVIEW_20261116-214955 |
| R4@claude | LOW | APLICADA | rodada=4a | teste: `test_r4_claude_branch_local_com_D` · `git branch -D` depois da conferência por `git cherry` | nao | EXTERNAL_REVIEW_20261116-214955 |
| R5@claude | LOW | APLICADA | rodada=4a | teste: `test_r5_claude_marca_de_recusa_sai_junto` · a marca sai no `--registrar` e no ramo da entrada que falhou | nao | EXTERNAL_REVIEW_20261116-214955 |
| R1@codex | HIGH | APLICADA | rodada=4a | teste: `test_r1_codex_playbook_limpo_inclui_o_staged` · `git diff --quiet HEAD` no item 0 do lote | sim | EXTERNAL_REVIEW_20261116-214955 |
| R2@codex | HIGH | APLICADA | rodada=4a | teste: `test_r2_codex_registrar_desconta_ausentes_da_antiga` · o `--registrar` desconta o `ausentes.txt` da entrada antiga | sim | EXTERNAL_REVIEW_20261116-214955 |
| R3@codex | MED | APLICADA | rodada=4a | teste: `test_r3_codex_temporarios_por_feature_e_entrada` · `lote-delta-<F>_<entrada>.txt` | nao | EXTERNAL_REVIEW_20261116-214955 |
| R4@codex | MED | REBATIDA_ESCOPO | rodada=4a | o leitor de ledger é de linhas `chave: valor` de propósito (stdlib, como os outros de `sdd/bin/`); ledger com sintaxe estranha mas campos legíveis gera a linha; o auditor discordou do achado; pendência ✨ na ficha | nao | EXTERNAL_REVIEW_20261116-214955 |
| R1@codex | HIGH | APLICADA | rodada=5 | teste: `test_r1_codex_registro_da_entrada_nao_suprime_contagem` · o `CURATOR-colhidos.txt` da entrada não vai para o staging; o já julgado vem só da base e da fila (desempate: PROCEDE) | sim | EXTERNAL_REVIEW_20261116-220949 |
| R2@codex | HIGH | APLICADA | rodada=5 | teste: `test_r2_codex_desfaz_pelo_commit_nao_pelo_index` · `git checkout HEAD --` no item 3 do lote | sim | EXTERNAL_REVIEW_20261116-220949 |
| R3@codex | MED | APLICADA | rodada=5 | teste: `test_r3_codex_lista_sem_fechar_e_ilegivel` · valor com `[` ou `{` sem fechar torna o ledger ilegível | nao | EXTERNAL_REVIEW_20261116-220949 |
| R1@claude | MED | APLICADA | rodada=5 | teste: `test_r1_claude_temporarios_com_valor_padrao` · `${TMPDIR:-/tmp}` em todo o `lote.md` | nao | EXTERNAL_REVIEW_20261116-220949 |
| R2@claude | MED | REBATIDA_ESCOPO | rodada=5 | o despacho real do curador depende do agente (subagente ou sessão nova); os scripts que o cercam (`--conferir-bloco`, `--selar`, fronteira) têm testes próprios da F14; pendência ✨ na ficha: teste de ponta a ponta do lote com um bloco gravado | nao | EXTERNAL_REVIEW_20261116-220949 |
| R3@claude | LOW | APLICADA | rodada=5 | teste: `test_r3_claude_escrita_no_playbook_marca_a_recusa` · `--recusar "$E" "curador escreveu no playbook"` | nao | EXTERNAL_REVIEW_20261116-220949 |
| R4@claude | LOW | APLICADA | rodada=5 | teste: `test_r4_claude_marcador_de_inicio_sem_fim_nao_grava` · início sem fim sai 2 e não grava | nao | EXTERNAL_REVIEW_20261116-220949 |
| R5@claude | LOW | APLICADA | rodada=5 | teste: `test_r5_claude_so_tags_ignore_nao_roda_em_branch` · `tags-ignore` sozinho não roda em push de branch | nao | EXTERNAL_REVIEW_20261116-220949 |
| R6@claude | LOW | APLICADA | rodada=5 | teste: `test_r6_claude_excecao_inesperada_e_nao_sei` · exceção inesperada vira `NAO_SEI` (exit 2) | nao | EXTERNAL_REVIEW_20261116-220949 |
| N1 | HIGH | REBATIDA_EVIDENCIA | rodada=5 | `git add -- <pasta>` põe no index a remoção de arquivo apagado (git ≥ 2.0; conferido em git 2.50.1: `D  d/a/f` depois de `rm -rf d/a && git add -- d`) | nao | EXTERNAL_REVIEW_20261116-220949 |
