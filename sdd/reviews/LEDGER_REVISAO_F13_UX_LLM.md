# Ledger da revisão — F13_UX_LLM (retroativo)

retroativo: sim

Convertido em 2026-11-10 do ledger de 5 colunas da frente (`sdd/reports/evidence/F13_UX_LLM/ledger-review.md`), sem mudar veredito nem
evidência. Acrescentados: a pasta da rodada e a marca `dano`. Regra do retroativo: `sim` = APLICADA cuja evidência cita o teste
do conserto (o efeito sobre dado, dinheiro, acesso, publicação ou disponibilidade **não** foi julgado de novo); `?` = APLICADA
sem teste citado; `nao` = rebatida. Critério: `sdd/review/CRITERIO_DANO.md`.

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1@claude | LOW | APLICADA | rodada=1 | teste: `test_init_completa_e_nao_sobrescreve_e_sync_gera_o_adaptador` · o teste de instalação remove a skill antes do 2º `init` e roda o `sync`; `test_init_completa_e_nao_sobrescreve_e_sync_gera_o_adaptador` | sim | EXTERNAL_REVIEW_20261104-143637 |
| R2@claude | LOW | APLICADA | rodada=1 | o auditor discordou, por ser limite documentado, mas o conserto custa 1 expressão: formas de streaming e assíncronas entram; o teste de ataque confere `generateContentStreamed` e `generate_content_async_pool` limpos | ? | EXTERNAL_REVIEW_20261104-143637 |
| R1@codex | MED | APLICADA | rodada=1 | teste: `test_entrada_lida_pela_metade_nunca_vira_limpo` · `cat` que falha sai 64; `test_entrada_lida_pela_metade_nunca_vira_limpo` e `test_vermelho_quando_o_cat_que_falha_e_ignorado` | sim | EXTERNAL_REVIEW_20261104-143637 |
| R2@codex | LOW | APLICADA | rodada=1 | teste: `test_vermelho_sem_a_recusa_do_ponto_ponto` · o caso `..` do self-test leva entrada e confere o motivo; `test_vermelho_sem_a_recusa_do_ponto_ponto` | sim | EXTERNAL_REVIEW_20261104-143637 |
| R1@claude | MED | APLICADA | rodada=2 | teste: `test_nao_quebra_onde_link_e_permissao_nao_tem_efeito` · self-test só faz os casos de link, FIFO e permissão onde têm efeito; `test_nao_quebra_onde_link_e_permissao_nao_tem_efeito` | sim | EXTERNAL_REVIEW_20261104-145623 |
| R2@claude | LOW | APLICADA | rodada=2 | o auditor discordou do FIFO, coberto em `tests/`; ele entra no self-test, e `tests/` ganha `sdd/` sem permissão e `awk` que falha | ? | EXTERNAL_REVIEW_20261104-145623 |
| R3@claude | LOW | APLICADA | rodada=2 | item 2 do `WORKER_BRIEF.md` é o confronto com o inventário; a varredura é do item 4 | ? | EXTERNAL_REVIEW_20261104-145623 |
| R4@claude | LOW | APLICADA | rodada=2 | regras e skill dizem o mesmo: sem reversão possível, `NEEDS_APPROVAL`; sem quem aprove, sai do `action_space` | ? | EXTERNAL_REVIEW_20261104-145623 |
| R5@claude | LOW | APLICADA | rodada=2 | doc EN e PT diz o que um projeto sem prompt encontra | ? | EXTERNAL_REVIEW_20261104-145623 |
| R1@codex | MED | APLICADA | rodada=2 | teste: `test_ancora_e_tag_no_cabecalho_do_bloco` · âncora e tag no cabeçalho entram no bloco; `prompts: *x` sai 64; `test_ancora_e_tag_no_cabecalho_do_bloco` | sim | EXTERNAL_REVIEW_20261104-145623 |
| R2@codex | MED | APLICADA | rodada=2 | fronteira à esquerda no SDK; `regenerateContent`, `my_generate_content`, `submessages.create` limpos no teste | ? | EXTERNAL_REVIEW_20261104-145623 |
| R1@claude | LOW | APLICADA | rodada=3 | teste: `test_outra_secao_que_so_comeca_igual_nao_e_a_de_prompts` · título delimitado no fim; regressão do ciclo 2; `test_outra_secao_que_so_comeca_igual_nao_e_a_de_prompts` | sim | EXTERNAL_REVIEW_20261104-151313 |
| R2@claude | LOW | APLICADA | rodada=3 | teste: `test_so_a_primeira_tabela_do_inventario_conta` · só a 1ª tabela conta; `test_so_a_primeira_tabela_do_inventario_conta` e `test_tabela_sem_as_colunas_seguida_da_certa_reprova` | sim | EXTERNAL_REVIEW_20261104-151313 |
| R3@claude | LOW | APLICADA | rodada=3 | teste: `test_o_que_esta_entre_chaves_nunca_passa` · chave em célula do inventário ou do contrato reprova, com ou sem crase; `test_o_que_esta_entre_chaves_nunca_passa` | sim | EXTERNAL_REVIEW_20261104-151313 |
| R1@codex | MED | APLICADA | rodada=3 | teste: `test_alvo_com_as_excecoes_da_norma` · a linha 2.5.8 e a nota de aceite citam as exceções da norma; `test_alvo_com_as_excecoes_da_norma` | sim | EXTERNAL_REVIEW_20261104-151313 |
| R1 | LOW | APLICADA | rodada=4 | teste: `test_outra_secao_que_so_comeca_igual_nao_e_a_de_prompts` · hífen colado não é a seção de prompts; `test_outra_secao_que_so_comeca_igual_nao_e_a_de_prompts` com `LLM Prompt-Injection` | sim | EXTERNAL_REVIEW_20261104-162100 |
| R2 | LOW | APLICADA | rodada=4 | `.stream` só com argumento, ou com a chamada aberta na linha; Java `messages.stream()` limpo e `client.messages.stream(` em várias linhas com DRIFT no teste | ? | EXTERNAL_REVIEW_20261104-162100 |
| R1 | LOW | REBATIDA_ESCOPO | rodada=5 | pendência da v2.5.1: `## 5.5. LLM Prompts` não casa o título; caso raro, e o conserto no commit final invalidaria a revisão da release | nao | EXTERNAL_REVIEW_20261104-164103 |
| R2 | LOW | REBATIDA_ESCOPO | rodada=5 | pendência da v2.5.1: chave entre crases em Tom/audiência, Tipo de saída e Fallback aprovado passa no lint; mesmo motivo | nao | EXTERNAL_REVIEW_20261104-164103 |
| R3 | LOW | REBATIDA_ESCOPO | rodada=5 | pendência da v2.5.1: `wrapper_pattern: [a, b]` e `*pat` sem aspas viram expressão; mesmo motivo | nao | EXTERNAL_REVIEW_20261104-164103 |
| R1 | LOW | REBATIDA_ESCOPO | rodada=6 | pendência da v2.5.1: chave em Tom/audiência, Tipo de saída e Fallback aprovado; mesma nota da rodada 5 | nao | EXTERNAL_REVIEW_20261104-182724 |
| R2 | LOW | REBATIDA_ESCOPO | rodada=6 | pendência da v2.5.1: `prompts: {` em várias linhas vira slot vazio; caso raro, e o aviso aparece; o conserto no commit final invalidaria a revisão da release | nao | EXTERNAL_REVIEW_20261104-182724 |
| R3 | LOW | REBATIDA_EVIDENCIA | rodada=6 | `wrapper_pattern: *param` vira `(*param)`, expressão que a validação recusa (saída 64); o auditor discordou do revisor pelo mesmo motivo; divergência em GNU grep segue na pendência da v2.5.1 | nao | EXTERNAL_REVIEW_20261104-182724 |

<!-- 23 linhas: 10 sim, 7 ?, 6 nao -->
