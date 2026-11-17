# Ledger da revisão — F23B2_MODELO_POR_PAPEL

> Uma linha por achado decidido, de todas as rodadas da revisão adversarial desta frente. Gravado em
> `sdd/reviews/LEDGER_REVISAO_{FEATURE}.md` logo depois de cada rodada (passo 5c da `sdd-build`).
> Conferido por `bash sdd/bin/ledger-revisao-lint.sh`; lido por `bash sdd/bin/sdd-fluxo.sh loop --ledger`
> (as 4 primeiras células) e por `bash sdd/bin/eval-revisores.sh` (todas). Critério da coluna `dano`:
> `sdd/review/CRITERIO_DANO.md`.

Revisão do DESIGN, rodada D1 (`EXTERNAL_REVIEW_20261116-205900`, `--paths` DEFINE + DESIGN): claude revisa (US$ 0,9046 nominal), codex
audita (assinatura), diversidade vendor. 11 achados do revisor e 1 novo do auditor: 10 aplicados no DESIGN v1.1 (e o
R7 também no AT-002 do DEFINE v1.2), 2 rebatidos com evidência no código.

revisor2: dispensado rodada=D1 — sem superfície de risco

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | MED | APLICADA | rodada=D1 | DESIGN Decision 4: teto.txt da pasta de medição, acumulado de todas as séries | nao | EXTERNAL_REVIEW_20261116-205900 |
| R2 | MED | APLICADA | rodada=D1 | DESIGN Decision 7 e Pattern 5: parcial antes da referência; candidato sem execução fora | nao | EXTERNAL_REVIEW_20261116-205900 |
| R3 | MED | REBATIDA_EVIDENCIA | rodada=D1 | sdd/bin/playbook-curator.sh:13 (stdout = playbook novo) e :800-815 (só lê os arquivos) | nao | EXTERNAL_REVIEW_20261116-205900 |
| R4 | MED | APLICADA | rodada=D1 | DESIGN Decision 4: inicio.txt; custo da interrompida somado antes de refazer | nao | EXTERNAL_REVIEW_20261116-205900 |
| R5 | MED | APLICADA | rodada=D1 | DESIGN Decision 5: saída em arquivo temporário, movida depois do --comparar | nao | EXTERNAL_REVIEW_20261116-205900 |
| R6 | MED | APLICADA | rodada=D1 | DESIGN Decision 4: a retomada move o PARADA.txt anterior para paradas/ | nao | EXTERNAL_REVIEW_20261116-205900 |
| R7 | MED | APLICADA | rodada=D1 | DESIGN Decision 1 e Pattern 1; DEFINE AT-002 v1.2: começa por letra ou número | nao | EXTERNAL_REVIEW_20261116-205900 |
| R8 | LOW | APLICADA | rodada=D1 | DESIGN Landmines, LM-017: slot vazio sem linha (AT-001) | nao | EXTERNAL_REVIEW_20261116-205900 |
| R9 | LOW | APLICADA | rodada=D1 | DESIGN Decision 3: Execuções = janelas do papel | nao | EXTERNAL_REVIEW_20261116-205900 |
| R10 | LOW | APLICADA | rodada=D1 | DESIGN Decision 4: modelo do candidatos.tsv pela regex do slot | nao | EXTERNAL_REVIEW_20261116-205900 |
| R11 | LOW | REBATIDA_EVIDENCIA | rodada=D1 | sdd/bin/adapters/sessao-claude.py:60-61 e sdd/bin/adapters/sessao-codex.py:68 usam realpath | nao | EXTERNAL_REVIEW_20261116-205900 |
| N1 | MED | APLICADA | rodada=D1 | DESIGN Decision 4: referência inteira primeiro, papel-medir --so-referencia, exit 22 | nao | EXTERNAL_REVIEW_20261116-205900 |

Rodada 1 do código (diff `origin/main..f512f0f`, 38 arquivos): claude US$ 1,4247 nominal (assinatura), codex audita
(assinatura), diversidade vendor. 7 achados do revisor e 1 novo do auditor (N1, HIGH): os 8 aplicados em `1fc9ce4`, cada
um com teste; os 9 testes novos ou mudados caem no código de `f512f0f` (`evidence/F23B2_MODELO_POR_PAPEL/RODADA1-VERMELHO.log`).
O R1 se confirmou no código antigo: a refeita gravava 2,002 em vez de 1,001. O R3 mudou de forma no conserto: o
`inicio.txt` mora no projeto e tem de vir antes da foto de antes; o conserto tira o arquivo se a foto falha e marca
`chamado.txt` fora do projeto logo antes de chamar o agente.

revisor2: dispensado rodada=1 — sem superfície de risco (regra antiga: 38 arquivos (limiar 8))

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | HIGH | APLICADA | rodada=1 | teste: `test_refeita_em_pasta_nova_nao_cobra_a_interrompida_duas_vezes` · cada tentativa numa pasta de cópia própria; a refeita somava a sessão da interrompida (2,002 em vez de 1,001) | sim | EXTERNAL_REVIEW_20261116-230146 |
| R2 | MED | APLICADA | rodada=1 | teste: `test_execucao_com_rc_diferente_de_zero_fica_fora_da_meta` · rc ≠ 0 fora da meta; o barato que sai 1 era escolhido | sim | EXTERNAL_REVIEW_20261116-230146 |
| R3 | MED | APLICADA | rodada=1 | teste: `test_snapshot_que_falha_nao_deixa_execucao_interrompida` · inicio.txt tirado quando a foto falha; chamado.txt separa a que não chamou o agente | sim | EXTERNAL_REVIEW_20261116-230146 |
| R4 | MED | APLICADA | rodada=1 | teste: `test_marca_fase_aceita_o_nome_de_cada_papel_da_escada` · a escada lista os nomes do despacho; o marca-fase.sh já os aceitava, o texto deixava usar o nome do slot (revisao_design, 64) | nao | EXTERNAL_REVIEW_20261116-230146 |
| R5 | LOW | APLICADA | rodada=1 | teste: `test_interrompida_de_outra_serie_para_antes_de_chamar` · interrompida sem custo em outra série para (20) | sim | EXTERNAL_REVIEW_20261116-230146 |
| R6 | LOW | APLICADA | rodada=1 | teste: `test_papel_sem_pontuador_com_candidatos_nao_paga_a_referencia` · o medidor confere a série antes da 1ª chamada; só o exit 3 vira 22 | sim | EXTERNAL_REVIEW_20261116-230146 |
| R7 | LOW | APLICADA | rodada=1 | teste: `test_serie_cmd_entre_aspas_no_yaml_desfaz_os_escapes` · escapes de string YAML desfeitos | sim | EXTERNAL_REVIEW_20261116-230146 |
| N1 | HIGH | APLICADA | rodada=1 | teste: `test_gabarito_sem_o_que_comparar_e_recusado_antes_de_chamar` · gabarito sem VEREDITO, sem AT ou sem playbook.md sai 64 | sim | EXTERNAL_REVIEW_20261116-230146 |

Rodada 2 do código (diff `origin/main..1fc9ce4`): claude US$ 1,5297 nominal (assinatura), codex audita (assinatura).
4 achados do revisor e 2 novos do auditor (N1 HIGH, N2 MED): os 6 aplicados em `e60222c`, cada um com teste que cai
no código de `5706214` (`evidence/F23B2_MODELO_POR_PAPEL/RODADA2-VERMELHO.log`). O auditor pediu prova em R2 e R3: o
R3 se confirmou (o `--aplicar` aceita a contagem repetida e soma +2); o R2, pela escada (o degrau de sessão nova só
citava `despachar avaliador`). Entre as rodadas, `5706214` (o `entrada/` fora do commit da cópia, achado da série real
do avaliador) entra na rodada 3.

revisor2: dispensado rodada=2 — sem superfície de risco (regra antiga: 38 arquivos (limiar 8))

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | HIGH | APLICADA | rodada=2 | teste: `test_sinal_na_serie_mata_o_agente` · SIGTERM e Ctrl-C na série matam o grupo do agente; antes ele seguia gastando fora do teto | sim | EXTERNAL_REVIEW_20261116-233506 |
| R2 | MED | APLICADA | rodada=2 | teste: `test_modo_contrato_despacha_como_revisor_design` · a escada manda o modo contrato despachar e marcar como revisor-design (slot revisao_design) | sim | EXTERNAL_REVIEW_20261116-233506 |
| R3 | LOW | APLICADA | rodada=2 | teste: `test_contagem_repetida_conta_em_dobro_na_precisao` · contagens em multiconjunto; +1 repetido dava precisão 1 | sim | EXTERNAL_REVIEW_20261116-233506 |
| R4 | LOW | APLICADA | rodada=2 | teste: `test_doc_do_limiar_diz_queda_minima` · a doc dizia o limiar ao contrário do código | nao | EXTERNAL_REVIEW_20261116-233506 |
| N1 | HIGH | APLICADA | rodada=2 | teste: `test_trava_da_pasta_de_medicao` · trava na pasta de medição; trava de processo morto é tomada | sim | EXTERNAL_REVIEW_20261116-233506 |
| N2 | MED | APLICADA | rodada=2 | teste: `test_execucao_gravada_com_outro_modelo_nao_vale` · a retomada recusa (64) e o medidor invalida a execução de outro modelo | sim | EXTERNAL_REVIEW_20261116-233506 |

Rodada 3 do código, o teto (diff `origin/main..e60222c`, com o `5706214` dentro): claude US$ 1,6007 nominal
(assinatura), codex audita (assinatura). 4 achados do revisor (0 graves) e 1 novo do auditor (N1 HIGH): 4 aplicados em
`7b84b5d` com teste que cai no código de `e60222c` (`evidence/F23B2_MODELO_POR_PAPEL/RODADA3-VERMELHO.log`), o R2 tirado do
DESIGN (v1.2) e o R4 rebatido no código.

revisor2: dispensado rodada=3 — sem superfície de risco (regra antiga: 38 arquivos (limiar 8))

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | MED | APLICADA | rodada=3 | teste: `test_agente_que_grava_no_projeto_invalida_a_execucao` · a inválida vira invalida-N.txt (custo no acumulado) e é refeita; antes ficava pulada para sempre | sim | EXTERNAL_REVIEW_20261116-235036 |
| R2 | LOW | APLICADA | rodada=3 | DESIGN v1.2: `--casos` sai da Decision 4 (a barreira exige a referência inteira; a retomada cobre o caso longo) | nao | EXTERNAL_REVIEW_20261116-235036 |
| R3 | LOW | APLICADA | rodada=3 | teste: `test_escada_le_o_slot_antes_de_marcar_o_inicio` · a escada lê o slot e só então marca o início | nao | EXTERNAL_REVIEW_20261116-235036 |
| R4 | LOW | REBATIDA_EVIDENCIA | rodada=3 | sdd/bin/sdd-fluxo.sh:108-123: revisor-design cai no texto padrão (lê o DEFINE; volta o bloco que começa com <<<), certo para o modo contrato; nenhum leitor procura BRIEF_avaliador no modo contrato | nao | EXTERNAL_REVIEW_20261116-235036 |
| N1 | HIGH | APLICADA | rodada=3 | teste: `test_interrompida_que_gravou_no_projeto_para_na_retomada` · a retomada compara o projeto com a foto de antes da interrompida (FORA ou foto sumida ⇒ 21, com os caminhos) | sim | EXTERNAL_REVIEW_20261116-235036 |

Rodada 4 do código, além do teto, com o OK do Roberto (D4: "Rodada 4 curta", 2026-11-17); diff inteiro
`origin/main..7b84b5d`, porque o `--conferir` não aceita revisão com `--paths`: claude US$ 1,7298 nominal (assinatura),
codex audita (assinatura). 5 achados do revisor (0 graves) e 2 novos do auditor (N1 HIGH, N2 MED): 6 aplicados em
`36cf144`, cada um com teste que cai no código de `7b84b5d` (`evidence/F23B2_MODELO_POR_PAPEL/RODADA4-VERMELHO.log`);
o R5 rebatido como o R4 da rodada 3.

revisor2: dispensado rodada=4 — sem superfície de risco (regra antiga: 38 arquivos (limiar 8))

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | MED | APLICADA | rodada=4 | teste: `test_parada_fica_se_a_retomada_sai_antes_de_chamar` · o PARADA.txt só é arquivado quando a série volta a chamar o agente, ou no fim | sim | EXTERNAL_REVIEW_20261117-054829 |
| R2 | LOW | APLICADA | rodada=4 | teste: `test_um_add_proposto_nao_cobre_dois_esperados` · cada ADD proposto vale para um esperado só | sim | EXTERNAL_REVIEW_20261117-054829 |
| R3 | LOW | APLICADA | rodada=4 | teste: `test_precos_relativo_vale_pela_pasta_atual` · --precos vira caminho absoluto pela pasta atual | sim | EXTERNAL_REVIEW_20261117-054829 |
| R4 | LOW | APLICADA | rodada=4 | teste: `test_parada_de_outra_serie_nao_conta_como_escrita_da_interrompida` · os arquivos que a série grava na pasta de medição ficam fora da fronteira da interrompida | nao | EXTERNAL_REVIEW_20261117-054829 |
| R5 | LOW | REBATIDA_EVIDENCIA | rodada=4 | sdd/bin/sdd-fluxo.sh:108-123: revisor-design usa o texto padrão (lê o DEFINE; volta o bloco que começa com <<<), certo para o modo contrato (mesmo ponto do R4 da rodada 3) | nao | EXTERNAL_REVIEW_20261117-054829 |
| N1 | HIGH | APLICADA | rodada=4 | teste: `test_agente_vivo_da_interrompida_trava_a_retomada` · o grupo do agente fica gravado ao lado da cópia; vivo, a retomada sai 64 sem medir | sim | EXTERNAL_REVIEW_20261117-054829 |
| N2 | MED | APLICADA | rodada=4 | teste: `test_trava_da_pasta_de_medicao` · trava do sistema (flock/msvcrt), solta com o processo; sem trava velha a tomar | sim | EXTERNAL_REVIEW_20261117-054829 |

Rodada 5 do código, com o OK do Roberto (D4: "Rodada 5, sem mais código", 2026-11-17), sobre o código já rebaseado na
`main` com a F24 (`origin/main..77ba5f7`): claude US$ 1,9212 nominal (assinatura), codex audita (assinatura). 0 graves:
1 leve do revisor e 1 médio novo do auditor, os 2 registrados como pendência sem conserto, pela regra combinada.
Depois dela, um só commit de teste (`test_windows` exige as constantes de `tests/apoio.py` no lugar de `os.name`; o Verify
Gate de `77ba5f7` caiu por isso).

revisor2: dispensado rodada=5 — sem superfície de risco (regra antiga: 38 arquivos (limiar 8))

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | LOW | REBATIDA_ESCOPO | rodada=5 | pendência (decisão do Roberto: rodada 5 sem mais código): a isenção por nome de arquivo da fronteira da interrompida deixa passar um meta.txt forjado pelo agente na pasta de medição | nao | EXTERNAL_REVIEW_20261117-065720 |
| N1 | MED | REBATIDA_ESCOPO | rodada=5 | pendência (decisão do Roberto: rodada 5 sem mais código): a retomada não confere remoto na cópia da execução interrompida | nao | EXTERNAL_REVIEW_20261117-065720 |

Rebase sobre a `main` com a F24 (2026-11-17), depois da rodada 4: os commits citados acima mudaram de nome —
`1fc9ce4`→`367c625`, `5706214`→`2c2fd37`, `e60222c`→`fd31760`, `7b84b5d`→`60094b1`, `36cf144`→`77ba5f7`. A rodada 5
já revisou o código rebaseado.
