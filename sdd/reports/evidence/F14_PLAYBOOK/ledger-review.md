# Ledger da revisão adversarial real — F14_PLAYBOOK

Revisor claude, 2º revisor codex (o Roberto repôs os créditos em 2026-11-05, conferido com execução real), auditor
openrouter:qwen/qwen3.7-plus. Decisão D4 do Roberto, 2026-11-05: a revisão pode ir até a 4ª rodada ("pode ir para quarta", lido assim e dito a ele).
Créditos do Codex acabaram de novo na rodada 3 (exit 67, conferido): a rodada 4 usa `openrouter:deepseek/deepseek-v4-pro` como 2º revisor, o caminho que o Roberto já tinha escolhido no brainstorm. Uma linha por achado, lida por `sdd/bin/sdd-fluxo.sh loop` por célula.

| id | severidade | veredito | rodada | motivo |
|---|---|---|---|---|
| R1@claude | HIGH | APLICADA | rodada=1 | exceção não tratada sai 2 com a causa, nunca 1 nem traceback; `real1-repro-antes.log` caso 1; `FalhaNuncaENada` em `test_playbook_curator.py`, com o lado "nada a colher continua 1" |
| R2@claude | MED | APLICADA | rodada=1 | o auditor discordou, com evidência que fala do `--preparar`, não do redirecionamento: `1` só vale com `RESULTADO: NADA A COLHER` em `colheita.txt`; outro exit do `--preparar` para o passo; `test_falha_de_coleta_nao_e_zero_deltas` |
| R3@claude | MED | APLICADA | rodada=1 | toda linha da sugestão, de qualquer arquivo e termo, entra no registro; caso 2 do repro; `test_sugestao_em_2_arquivos_nao_volta_na_release_seguinte`, `test_linha_que_casa_o_2o_termo_tambem_entra` |
| R4@claude | MED | REBATIDA_EVIDENCIA | rodada=1 | premissa falsa: `governanca-fronteira.sh:30` exporta `LC_ALL=C`; com `LANG`, `LC_ALL` e `LANGUAGE` em alemão, sai 64 (`real1-repro-antes.log` caso 4) |
| R5@claude | LOW | APLICADA | rodada=1 | o verbo do delta combina com o tipo da linha; `test_verbo_do_delta_combina_com_o_tipo` |
| R6@claude | LOW | APLICADA | rodada=1 | brief trata `TABELA_SEM_CABECALHO` |
| R7@claude | LOW | APLICADA | rodada=1 | brief: evidência de `refine` começa por `arquivo:linha`; `test_refine_com_evidencia_e_candidato_passa` |
| R1@codex | HIGH | APLICADA | rodada=1 | `rm -f` do nome intermediário antes do `cp`; caso 3 do repro; `RestauracaoDoDefine` executa a sequência do texto, com os 2 links e a cópia inalcançável |
| R2@codex | HIGH | APLICADA | rodada=1 | mesmo defeito de R1@claude |
| R3@codex | MED | APLICADA | rodada=1 | mesmo defeito de R3@claude |
| R4@codex | MED | APLICADA | rodada=1 | `caminho_dentro` resolve o link; caso 5 do repro; `test_check_por_link_que_sai_da_raiz_reprova_e_link_interno_passa` |
| N1 | MED | APLICADA | rodada=1 | achado do auditor: `read -d ''` no lugar de `tr`; `test_nome_com_quebra_de_linha_nao_vira_2_caminhos` |
| R1@claude | LOW | APLICADA | rodada=2 | o `--aplicar` troca a última ocorrência do campo, como o parser lê; `test_regra_que_cita_o_nome_do_campo_nao_e_cortada` |
| R2@claude | LOW | APLICADA | rodada=2 | referência exata na cobertura; `test_referencia_precisa_ser_a_exata` |
| R3@claude | LOW | APLICADA | rodada=2 | `description` da `sdd-playbook` diz o que o P3 faz |
| R4@claude | LOW | APLICADA | rodada=2 | o auditor discordou, por falta de evidência; o conserto é 1 frase: rodado do checkout principal, com a pasta das skills; qualquer outro exit é dito |
| R5@claude | LOW | APLICADA | rodada=2 | o auditor discordou, pelo mesmo motivo; heredoc com delimitador entre aspas no passo e no brief; `test_entrada_do_cruzar_nao_passa_pelo_shell` |
| R1@codex | HIGH | APLICADA | rodada=2 | hook que é link mede o conteúdo do destino; `test_hook_que_e_link_mede_o_conteudo_do_destino`, com o lado intocado e o link quebrado |
| R2@codex | MED | APLICADA | rodada=2 | o que pode entrar soma 1 vez, de qualquer tipo; `test_sugestao_repetida_nao_soma_2`, com o lado da sugestão descartada |
| R3@codex | MED | APLICADA | rodada=2 | contagem de chaves na linha, no lugar da expressão; caso no self-test e em `test_formas_do_slot_que_a_varredura_nao_le_saem_64` |
| R1 | MED | APLICADA | rodada=3 | `branch.*` fora da medida do config comum; `test_outra_frente_abrindo_branch_nao_e_o_agente`, com o lado `test_o_resto_do_config_continua_contando` |
| R2 | LOW | APLICADA | rodada=3 | o auditor discordou, citando o `nome not in campos`, que é a linha do defeito; molde não tem aspas nem dois-pontos; `test_json_preenchido_nao_e_chave_sem_preencher`, e `test_chave_sem_preencher_nos_3_campos_do_contrato` segue |
| R3 | LOW | APLICADA | rodada=3 | o `REFINE` guarda a última ocorrência; `test_refine_com_regra_que_cita_o_campo_nao_guarda_o_texto_velho` |
| R4 | LOW | APLICADA | rodada=3 | campo vazio reprova em qualquer estado; `test_campo_vazio_em_qualquer_estado_reprova` |
| R5 | LOW | APLICADA | rodada=3 | só no índice é copiado; a lista de salvos vem de `ls-tree HEAD`; `test_so_no_indice_e_copiado_nao_e_commit_nao_enviado` |
| R6 | LOW | APLICADA | rodada=3 | `test_link_ignorado_aparece_na_seta_mesmo_com_copia` |
| R7 | LOW | APLICADA | rodada=3 | `grep -x … >/dev/null` lê tudo, sem SIGPIPE sob pipefail |
| R1@openrouter-deepseek-deepseek-v4-pro | HIGH | REBATIDA_EVIDENCIA | rodada=4 | premissa falsa, medida: sem `--exclude-standard`, `ls-files --others` já lista o ignorado, o script real copia, e `--ignored` dá `fatal` (`deepseek-r1-repro.log`); `test_arquivo_ignorado_pelo_git_tambem_vem` existe e passa. O auditor concordou sem medir: rebatida a mostrar à pessoa no bloco de OK |
| R1@claude | MED | REBATIDA_ESCOPO | rodada=4 | decisão D4 do Roberto, 2026-11-05: publicar sem 5ª rodada; primeira tarefa da F14_DRIVE. Fim de linha no Windows: não medido, auditor discorda |
| R2@claude | LOW | REBATIDA_ESCOPO | rodada=4 | decisão D4 do Roberto, 2026-11-05: publicar sem 5ª rodada; primeira tarefa da F14_DRIVE. Byte inválido vira U+FFFD no `--aplicar`: confirmado, raro |
| R3@claude | LOW | REBATIDA_ESCOPO | rodada=4 | decisão D4 do Roberto, 2026-11-05: publicar sem 5ª rodada; primeira tarefa da F14_DRIVE. Seta omite o PARECIDO quando há IGNORADO: confirmado, veio do conserto de R6 da rodada 3 |
| R4@claude | LOW | REBATIDA_ESCOPO | rodada=4 | decisão D4 do Roberto, 2026-11-05: publicar sem 5ª rodada; primeira tarefa da F14_DRIVE. Limite de redespacho entre sessões: plausível, auditor discorda |
| R5@claude | LOW | REBATIDA_ESCOPO | rodada=4 | decisão D4 do Roberto, 2026-11-05: publicar sem 5ª rodada; primeira tarefa da F14_DRIVE. Staging previsível em máquina multiusuário: plausível, auditor discorda |
