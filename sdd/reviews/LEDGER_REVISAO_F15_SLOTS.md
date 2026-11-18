# Ledger da revisão — F15_SLOTS (retroativo)

retroativo: sim

Transcrito em 2026-11-10 do Advisor Ledger de `sdd/reports/BUILD_REPORT_F15_SLOTS.md` (a frente não gravou ledger próprio), sem mudar
veredito nem evidência. Acrescentados: a pasta da rodada e a marca `dano`. Regra do retroativo: `sim` = APLICADA cuja evidência cita o
teste do conserto (o efeito sobre dado, dinheiro, acesso, publicação ou disponibilidade **não** foi julgado de novo); `?` = APLICADA sem
teste citado; `nao` = rebatida. Critério: `sdd/review/CRITERIO_DANO.md`. Na rodada 1 o auditor falhou (sem cota); os achados do revisor
foram decididos assim mesmo.

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1@claude | LOW | APLICADA | rodada=1 | o `trap` vinha depois da leitura do config; um sinal nessa janela saía 130/143; commit `f3d1d54` (trap logo depois das flags) | ? | EXTERNAL_REVIEW_20261110-052050 |
| R2@claude | LOW | APLICADA | rodada=1 | teste: `test_before_ok_vazio_tambem_esvazia` · com `before_ok` vazio, a pasta comum nunca era limpa; commit `f3d1d54` | sim | EXTERNAL_REVIEW_20261110-052050 |
| R3@claude | LOW | APLICADA | rodada=1 | teste: `test_touched_id_relativo_a_subpasta_conta` · id relativo à subpasta do runner escapava do vizinho; commit `f3d1d54`; S10 | sim | EXTERNAL_REVIEW_20261110-052050 |
| R1@claude | LOW | APLICADA | rodada=2 | teste: `test_config_que_nao_da_para_rodar_e_64` · comando terminado em `;`, `&` ou barra vertical fazia o slot sair 0 com o smoke reprovado; commit `cd18e59`; S12 | sim | EXTERNAL_REVIEW_20261110-055845 |
| R2@claude | LOW | APLICADA | rodada=2 | teste: `test_caminhos_relativos_valem_de_onde_foi_chamado` · arquivo, `--arvore` e `--dir` relativos eram lidos da raiz; commit `cd18e59`; S13 | sim | EXTERNAL_REVIEW_20261110-055845 |
| N1@openrouter | HIGH | REBATIDA_EVIDENCIA | rodada=2 | `declare -f` preservaria comentários e a checagem de `#` nunca reprovaria: medido no bash 3.2, `sdd/reports/evidence/F15_SLOTS/REVIEW-N1-declare-f.log` | nao | EXTERNAL_REVIEW_20261110-055845 |
| R1@claude | MED | APLICADA | rodada=3 | teste: `test_redirecao_no_fim_roda` · o `declare -f` põe `2>&1`, `>` e `<` depois do `"$@"`; comando válido saía 64; commit `45e27a9`; S14 | sim | EXTERNAL_REVIEW_20261110-062431 |
| R2@claude | LOW | APLICADA | rodada=3 | a lista anti-termos omitia arquivos do diff; commit `45e27a9`; `SemProjetoPrivado.ARQUIVOS` com os 21 e isenções nomeadas | ? | EXTERNAL_REVIEW_20261110-062431 |
| R1@openrouter-z-ai-glm-5.3 | LOW | APLICADA | rodada=3 | teste: `test_ajuda_mostra_so_o_cabecalho` · `-h` imprimia `set -uo pipefail`; commit `45e27a9` | sim | EXTERNAL_REVIEW_20261110-062431 |
| R1@claude | MED | REBATIDA_EVIDENCIA | rodada=4 | falha de carga do teste ao lado escaparia como "fora do diff": medido, o script sai INCONCLUSIVO (3); `sdd/reports/evidence/F15_SLOTS/REVIEW-R4-medicoes.log` | nao | EXTERNAL_REVIEW_20261110-070608 |
| R2@claude | LOW | REBATIDA_ESCOPO | rodada=4 | sufixo do vizinho conta teste homônimo de outro pacote: limite declarado em `sdd/bin/test-baseline.sh:18-19` e na Decision 8 | nao | EXTERNAL_REVIEW_20261110-070608 |
| N1@openrouter | HIGH | REBATIDA_EVIDENCIA | rodada=4 | o `eval` com quebra de linha protegeria o `"$@"` só na checagem: medido, `bash e.sh 0 # gate` sai 64; `sdd/reports/evidence/F15_SLOTS/REVIEW-R4-medicoes.log`. É o mesmo ponto do N1 da rodada 2, repetido pelo auditor | nao | EXTERNAL_REVIEW_20261110-070608 |
