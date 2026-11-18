# Ledger da revisão adversarial real — F13_UX_LLM

Rodada 1: `sdd/reports/reviews/EXTERNAL_REVIEW_20261104-143637` (revisor claude, 2º revisor codex, auditor
openrouter:qwen/qwen3.7-plus; diff de `32cc42c`; 0 HIGH, 1 MED, 3 LOW; o auditor discordou de 1; US$ 2,42).
Rodada 2: `sdd/reports/reviews/EXTERNAL_REVIEW_20261104-145623` (mesmas engines; diff de `867d6de`; 0 HIGH, 2 MED, 5 LOW;
o auditor discordou de 1; US$ 2,28).
Rodada 3 (teto): `sdd/reports/reviews/EXTERNAL_REVIEW_20261104-151313` (mesmas engines; diff de `726c43c`; 0 HIGH, 1 MED, 3 LOW;
`loop` PRONTO; `--conferir` CONFERE; US$ 2,31). Decisão D4 do Roberto (2026-11-04): "corrigir e rodar a 4ª rodada".
Rodada 4 (D4): `sdd/reports/reviews/EXTERNAL_REVIEW_20261104-162100` (revisor claude, auditor openrouter:qwen/qwen3.7-plus; o 2º revisor,
codex, falhou por falta de créditos; diff de `cdb85a9`; 0 HIGH, 2 LOW, que o auditor julgou MED; `NÃO CONFERE`; US$ 2,39).
Rodada 5 (D4 do Roberto, 2026-11-04: "dispensar o 2º revisor e aceitar a prova anterior"): `sdd/reports/reviews/EXTERNAL_REVIEW_20261104-164103` (revisor claude, auditor openrouter:qwen/qwen3.7-plus; diff de `5ddc433`; 0 HIGH, 3 LOW; `loop` PRONTO; `--conferir` CONFERE; US$ 2,35).
revisor2: dispensado rodada=5 — sem créditos na conta do Codex; decisão D4 do Roberto, 2026-11-04
Rodada 6 (D4 do Roberto, 2026-11-04: consertar o MEDIUM do avaliador, ciclo 3, e rodar de novo): `sdd/reports/reviews/EXTERNAL_REVIEW_20261104-182724` (revisor claude, auditor openrouter:qwen/qwen3.7-plus; diff de `b1348bd`; 0 HIGH, 3 LOW; `loop` PRONTO; `--conferir` CONFERE; US$ 2,25). Esta é a revisão da release.
revisor2: dispensado rodada=6 — sem créditos na conta do Codex; decisão D4 do Roberto, 2026-11-04
Lido por `sdd/bin/sdd-fluxo.sh loop` por célula.

| achado | sev | veredito | rodada | evidência / motivo |
|---|---|---|---|---|
| R1@claude | LOW | APLICADA | rodada=1 | o teste de instalação remove a skill antes do 2º `init` e roda o `sync`; `test_init_completa_e_nao_sobrescreve_e_sync_gera_o_adaptador` |
| R2@claude | LOW | APLICADA | rodada=1 | o auditor discordou, por ser limite documentado, mas o conserto custa 1 expressão: formas de streaming e assíncronas entram; o teste de ataque confere `generateContentStreamed` e `generate_content_async_pool` limpos |
| R1@codex | MED | APLICADA | rodada=1 | `cat` que falha sai 64; `test_entrada_lida_pela_metade_nunca_vira_limpo` e `test_vermelho_quando_o_cat_que_falha_e_ignorado` |
| R2@codex | LOW | APLICADA | rodada=1 | o caso `..` do self-test leva entrada e confere o motivo; `test_vermelho_sem_a_recusa_do_ponto_ponto` |
| R1@claude | MED | APLICADA | rodada=2 | self-test só faz os casos de link, FIFO e permissão onde têm efeito; `test_nao_quebra_onde_link_e_permissao_nao_tem_efeito` |
| R2@claude | LOW | APLICADA | rodada=2 | o auditor discordou do FIFO, coberto em `tests/`; ele entra no self-test, e `tests/` ganha `sdd/` sem permissão e `awk` que falha |
| R3@claude | LOW | APLICADA | rodada=2 | item 2 do `WORKER_BRIEF.md` é o confronto com o inventário; a varredura é do item 4 |
| R4@claude | LOW | APLICADA | rodada=2 | regras e skill dizem o mesmo: sem reversão possível, `NEEDS_APPROVAL`; sem quem aprove, sai do `action_space` |
| R5@claude | LOW | APLICADA | rodada=2 | doc EN e PT diz o que um projeto sem prompt encontra |
| R1@codex | MED | APLICADA | rodada=2 | âncora e tag no cabeçalho entram no bloco; `prompts: *x` sai 64; `test_ancora_e_tag_no_cabecalho_do_bloco` |
| R2@codex | MED | APLICADA | rodada=2 | fronteira à esquerda no SDK; `regenerateContent`, `my_generate_content`, `submessages.create` limpos no teste |
| R1@claude | LOW | APLICADA | rodada=3 | título delimitado no fim; regressão do ciclo 2; `test_outra_secao_que_so_comeca_igual_nao_e_a_de_prompts` |
| R2@claude | LOW | APLICADA | rodada=3 | só a 1ª tabela conta; `test_so_a_primeira_tabela_do_inventario_conta` e `test_tabela_sem_as_colunas_seguida_da_certa_reprova` |
| R3@claude | LOW | APLICADA | rodada=3 | chave em célula do inventário ou do contrato reprova, com ou sem crase; `test_o_que_esta_entre_chaves_nunca_passa` |
| R1@codex | MED | APLICADA | rodada=3 | a linha 2.5.8 e a nota de aceite citam as exceções da norma; `test_alvo_com_as_excecoes_da_norma` |
| R1 | LOW | APLICADA | rodada=4 | hífen colado não é a seção de prompts; `test_outra_secao_que_so_comeca_igual_nao_e_a_de_prompts` com `LLM Prompt-Injection` |
| R2 | LOW | APLICADA | rodada=4 | `.stream` só com argumento, ou com a chamada aberta na linha; Java `messages.stream()` limpo e `client.messages.stream(` em várias linhas com DRIFT no teste |
| R1 | LOW | REBATIDA_ESCOPO | rodada=5 | pendência da v2.5.1: `## 5.5. LLM Prompts` não casa o título; caso raro, e o conserto no commit final invalidaria a revisão da release |
| R2 | LOW | REBATIDA_ESCOPO | rodada=5 | pendência da v2.5.1: chave entre crases em Tom/audiência, Tipo de saída e Fallback aprovado passa no lint; mesmo motivo |
| R3 | LOW | REBATIDA_ESCOPO | rodada=5 | pendência da v2.5.1: `wrapper_pattern: [a, b]` e `*pat` sem aspas viram expressão; mesmo motivo |
| R1 | LOW | REBATIDA_ESCOPO | rodada=6 | pendência da v2.5.1: chave em Tom/audiência, Tipo de saída e Fallback aprovado; mesma nota da rodada 5 |
| R2 | LOW | REBATIDA_ESCOPO | rodada=6 | pendência da v2.5.1: `prompts: {` em várias linhas vira slot vazio; caso raro, e o aviso aparece; o conserto no commit final invalidaria a revisão da release |
| R3 | LOW | REBATIDA_EVIDENCIA | rodada=6 | `wrapper_pattern: *param` vira `(*param)`, expressão que a validação recusa (saída 64); o auditor discordou do revisor pelo mesmo motivo; divergência em GNU grep segue na pendência da v2.5.1 |
