# Ledger da revisão — F14_PLAYBOOK (retroativo)

retroativo: sim

Convertido em 2026-11-10 do ledger de 5 colunas da frente (`sdd/reports/evidence/F14_PLAYBOOK/ledger-review.md`), sem mudar veredito nem
evidência. Acrescentados: a pasta da rodada e a marca `dano`. Regra do retroativo: `sim` = APLICADA cuja evidência cita o teste
do conserto (o efeito sobre dado, dinheiro, acesso, publicação ou disponibilidade **não** foi julgado de novo); `?` = APLICADA
sem teste citado; `nao` = rebatida. Critério: `sdd/review/CRITERIO_DANO.md`.

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1@claude | HIGH | APLICADA | rodada=1 | teste: `test_playbook_curator.FalhaNuncaENada` · exceção não tratada sai 2 com a causa, nunca 1 nem traceback; `real1-repro-antes.log` caso 1; `FalhaNuncaENada` em `test_playbook_curator.py`, com o lado "nada a colher continua 1" | sim | EXTERNAL_REVIEW_20261105-120949 |
| R2@claude | MED | APLICADA | rodada=1 | teste: `test_falha_de_coleta_nao_e_zero_deltas` · o auditor discordou, com evidência que fala do `--preparar`, não do redirecionamento: `1` só vale com `RESULTADO: NADA A COLHER` em `colheita.txt`; outro exit do `--preparar` para o passo; `test_falha_de_coleta_nao_e_zero_deltas` | sim | EXTERNAL_REVIEW_20261105-120949 |
| R3@claude | MED | APLICADA | rodada=1 | teste: `test_sugestao_em_2_arquivos_nao_volta_na_release_seguinte` · toda linha da sugestão, de qualquer arquivo e termo, entra no registro; caso 2 do repro; `test_sugestao_em_2_arquivos_nao_volta_na_release_seguinte`, `test_linha_que_casa_o_2o_termo_tambem_entra` | sim | EXTERNAL_REVIEW_20261105-120949 |
| R4@claude | MED | REBATIDA_EVIDENCIA | rodada=1 | premissa falsa: `governanca-fronteira.sh:30` exporta `LC_ALL=C`; com `LANG`, `LC_ALL` e `LANGUAGE` em alemão, sai 64 (`real1-repro-antes.log` caso 4) | nao | EXTERNAL_REVIEW_20261105-120949 |
| R5@claude | LOW | APLICADA | rodada=1 | teste: `test_verbo_do_delta_combina_com_o_tipo` · o verbo do delta combina com o tipo da linha; `test_verbo_do_delta_combina_com_o_tipo` | sim | EXTERNAL_REVIEW_20261105-120949 |
| R6@claude | LOW | APLICADA | rodada=1 | brief trata `TABELA_SEM_CABECALHO` | ? | EXTERNAL_REVIEW_20261105-120949 |
| R7@claude | LOW | APLICADA | rodada=1 | teste: `test_refine_com_evidencia_e_candidato_passa` · brief: evidência de `refine` começa por `arquivo:linha`; `test_refine_com_evidencia_e_candidato_passa` | sim | EXTERNAL_REVIEW_20261105-120949 |
| R1@codex | HIGH | APLICADA | rodada=1 | `rm -f` do nome intermediário antes do `cp`; caso 3 do repro; `RestauracaoDoDefine` executa a sequência do texto, com os 2 links e a cópia inalcançável | ? | EXTERNAL_REVIEW_20261105-120949 |
| R2@codex | HIGH | APLICADA | rodada=1 | mesmo defeito de R1@claude | ? | EXTERNAL_REVIEW_20261105-120949 |
| R3@codex | MED | APLICADA | rodada=1 | mesmo defeito de R3@claude | ? | EXTERNAL_REVIEW_20261105-120949 |
| R4@codex | MED | APLICADA | rodada=1 | teste: `test_check_por_link_que_sai_da_raiz_reprova_e_link_interno_passa` · `caminho_dentro` resolve o link; caso 5 do repro; `test_check_por_link_que_sai_da_raiz_reprova_e_link_interno_passa` | sim | EXTERNAL_REVIEW_20261105-120949 |
| N1 | MED | APLICADA | rodada=1 | teste: `test_nome_com_quebra_de_linha_nao_vira_2_caminhos` · achado do auditor: `read -d ''` no lugar de `tr`; `test_nome_com_quebra_de_linha_nao_vira_2_caminhos` | sim | EXTERNAL_REVIEW_20261105-120949 |
| R1@claude | LOW | APLICADA | rodada=2 | teste: `test_regra_que_cita_o_nome_do_campo_nao_e_cortada` · o `--aplicar` troca a última ocorrência do campo, como o parser lê; `test_regra_que_cita_o_nome_do_campo_nao_e_cortada` | sim | EXTERNAL_REVIEW_20261105-123246 |
| R2@claude | LOW | APLICADA | rodada=2 | teste: `test_referencia_precisa_ser_a_exata` · referência exata na cobertura; `test_referencia_precisa_ser_a_exata` | sim | EXTERNAL_REVIEW_20261105-123246 |
| R3@claude | LOW | APLICADA | rodada=2 | `description` da `sdd-playbook` diz o que o P3 faz | ? | EXTERNAL_REVIEW_20261105-123246 |
| R4@claude | LOW | APLICADA | rodada=2 | o auditor discordou, por falta de evidência; o conserto é 1 frase: rodado do checkout principal, com a pasta das skills; qualquer outro exit é dito | ? | EXTERNAL_REVIEW_20261105-123246 |
| R5@claude | LOW | APLICADA | rodada=2 | teste: `test_entrada_do_cruzar_nao_passa_pelo_shell` · o auditor discordou, pelo mesmo motivo; heredoc com delimitador entre aspas no passo e no brief; `test_entrada_do_cruzar_nao_passa_pelo_shell` | sim | EXTERNAL_REVIEW_20261105-123246 |
| R1@codex | HIGH | APLICADA | rodada=2 | teste: `test_hook_que_e_link_mede_o_conteudo_do_destino` · hook que é link mede o conteúdo do destino; `test_hook_que_e_link_mede_o_conteudo_do_destino`, com o lado intocado e o link quebrado | sim | EXTERNAL_REVIEW_20261105-123246 |
| R2@codex | MED | APLICADA | rodada=2 | teste: `test_sugestao_repetida_nao_soma_2` · o que pode entrar soma 1 vez, de qualquer tipo; `test_sugestao_repetida_nao_soma_2`, com o lado da sugestão descartada | sim | EXTERNAL_REVIEW_20261105-123246 |
| R3@codex | MED | APLICADA | rodada=2 | teste: `test_formas_do_slot_que_a_varredura_nao_le_saem_64` · contagem de chaves na linha, no lugar da expressão; caso no self-test e em `test_formas_do_slot_que_a_varredura_nao_le_saem_64` | sim | EXTERNAL_REVIEW_20261105-123246 |
| R1 | MED | APLICADA | rodada=3 | teste: `test_outra_frente_abrindo_branch_nao_e_o_agente` · `branch.*` fora da medida do config comum; `test_outra_frente_abrindo_branch_nao_e_o_agente`, com o lado `test_o_resto_do_config_continua_contando` | sim | EXTERNAL_REVIEW_20261105-130247 |
| R2 | LOW | APLICADA | rodada=3 | teste: `test_json_preenchido_nao_e_chave_sem_preencher` · o auditor discordou, citando o `nome not in campos`, que é a linha do defeito; molde não tem aspas nem dois-pontos; `test_json_preenchido_nao_e_chave_sem_preencher`, e `test_chave_sem_preencher_nos_3_campos_do_contrato` segue | sim | EXTERNAL_REVIEW_20261105-130247 |
| R3 | LOW | APLICADA | rodada=3 | teste: `test_refine_com_regra_que_cita_o_campo_nao_guarda_o_texto_velho` · o `REFINE` guarda a última ocorrência; `test_refine_com_regra_que_cita_o_campo_nao_guarda_o_texto_velho` | sim | EXTERNAL_REVIEW_20261105-130247 |
| R4 | LOW | APLICADA | rodada=3 | teste: `test_campo_vazio_em_qualquer_estado_reprova` · campo vazio reprova em qualquer estado; `test_campo_vazio_em_qualquer_estado_reprova` | sim | EXTERNAL_REVIEW_20261105-130247 |
| R5 | LOW | APLICADA | rodada=3 | teste: `test_so_no_indice_e_copiado_nao_e_commit_nao_enviado` · só no índice é copiado; a lista de salvos vem de `ls-tree HEAD`; `test_so_no_indice_e_copiado_nao_e_commit_nao_enviado` | sim | EXTERNAL_REVIEW_20261105-130247 |
| R6 | LOW | APLICADA | rodada=3 | teste: `test_link_ignorado_aparece_na_seta_mesmo_com_copia` · `test_link_ignorado_aparece_na_seta_mesmo_com_copia` | sim | EXTERNAL_REVIEW_20261105-130247 |
| R7 | LOW | APLICADA | rodada=3 | `grep -x … >/dev/null` lê tudo, sem SIGPIPE sob pipefail | ? | EXTERNAL_REVIEW_20261105-130247 |
| R1@openrouter-deepseek-deepseek-v4-pro | HIGH | REBATIDA_EVIDENCIA | rodada=4 | premissa falsa, medida: sem `--exclude-standard`, `ls-files --others` já lista o ignorado, o script real copia, e `--ignored` dá `fatal` (`deepseek-r1-repro.log`); `test_arquivo_ignorado_pelo_git_tambem_vem` existe e passa. O auditor concordou sem medir: rebatida a mostrar à pessoa no bloco de OK | nao | EXTERNAL_REVIEW_20261105-132615 |
| R1@claude | MED | REBATIDA_ESCOPO | rodada=4 | decisão D4 do Roberto, 2026-11-05: publicar sem 5ª rodada; primeira tarefa da F14_DRIVE. Fim de linha no Windows: não medido, auditor discorda | nao | EXTERNAL_REVIEW_20261105-132615 |
| R2@claude | LOW | REBATIDA_ESCOPO | rodada=4 | decisão D4 do Roberto, 2026-11-05: publicar sem 5ª rodada; primeira tarefa da F14_DRIVE. Byte inválido vira U+FFFD no `--aplicar`: confirmado, raro | nao | EXTERNAL_REVIEW_20261105-132615 |
| R3@claude | LOW | REBATIDA_ESCOPO | rodada=4 | decisão D4 do Roberto, 2026-11-05: publicar sem 5ª rodada; primeira tarefa da F14_DRIVE. Seta omite o PARECIDO quando há IGNORADO: confirmado, veio do conserto de R6 da rodada 3 | nao | EXTERNAL_REVIEW_20261105-132615 |
| R4@claude | LOW | REBATIDA_ESCOPO | rodada=4 | decisão D4 do Roberto, 2026-11-05: publicar sem 5ª rodada; primeira tarefa da F14_DRIVE. Limite de redespacho entre sessões: plausível, auditor discorda | nao | EXTERNAL_REVIEW_20261105-132615 |
| R5@claude | LOW | REBATIDA_ESCOPO | rodada=4 | decisão D4 do Roberto, 2026-11-05: publicar sem 5ª rodada; primeira tarefa da F14_DRIVE. Staging previsível em máquina multiusuário: plausível, auditor discorda | nao | EXTERNAL_REVIEW_20261105-132615 |

<!-- 33 linhas: 19 sim, 7 ?, 7 nao -->
