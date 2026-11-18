# Ledger da revisão — F25_SKILLS_DUPLICADAS

Rodada 1: `claude` (claude-opus-5-5) revisa, `codex` (gpt-6.1-sol) audita, sobre o diff da frente contra `origin/main`
(`2204a14`, v2.21.0), feita na FASE 0a item 8 da `sdd-release`. A pergunta `[D3]` "rodar agora ou publicar sem revisão"
foi decidida pela recomendada (rodar), sob o pedido do Roberto de só parar nas condições do ESCOPO, seção 5.

revisor2: dispensado rodada=1 — sem superfície de risco (regra antiga: 11 arquivos (limiar 8))

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | HIGH | APLICADA | rodada=1 | teste: `test_r1_npx_que_tira_so_a_pasta_real_devolve_tudo` · `27255b2` (o ramo de falha apagava a única cópia guardada) | sim | EXTERNAL_REVIEW_20261117-122525 |
| R2 | MED | APLICADA | rodada=1 | teste: `test_r2_pasta_pessoal_por_atalho_nao_protege_a_propria_copia` · `27255b2` (dup_real resolve o caminho inteiro) | sim | EXTERNAL_REVIEW_20261117-122525 |
| R3 | MED | APLICADA | rodada=1 | teste: `test_r3_falha_no_2o_item_nao_devolve_o_registro_do_1o` · `27255b2` (registro guardado por item) | sim | EXTERNAL_REVIEW_20261117-122525 |
| R4 | MED | APLICADA | rodada=1 | teste: `test_r4_a_lista_do_que_vai_sair_fica_na_lixeira_antes_de_tirar` · `27255b2` (PLANO.txt antes da 1ª remoção) | nao | EXTERNAL_REVIEW_20261117-122525 |
| R5 | LOW | REBATIDA_EVIDENCIA | rodada=1 | `grep -n trap .agents/skills/sdd-checar-ambiente/scripts/checar.sh` não acha nada: o único `trap EXIT` é o do `duplicadas.sh` | nao | EXTERNAL_REVIEW_20261117-122525 |
| N1 | MED | APLICADA | rodada=1 | teste: `test_n1_o_codex_nao_perde_a_versao_mais_nova` · `27255b2` (a trava compara a versão mais nova de cada agente) | sim | EXTERNAL_REVIEW_20261117-122525 |

Rodada 2: as mesmas engines, sobre `27255b2`.

revisor2: dispensado rodada=2 — sem superfície de risco (regra antiga: 11 arquivos (limiar 8))

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | HIGH | APLICADA | rodada=2 | teste: `test_r1_nenhum_nome_embutido_do_gawk_como_variavel_nos_awk` · `2503187` (o array `or` virou `og`; no gawk do Git Bash o plano sairia vazio) | sim | EXTERNAL_REVIEW_20261117-124048 |
| R2 | MED | APLICADA | rodada=2 | `2503187` · `SKILL.md`: a exceção única é o modo de limpeza (`--limpar` e o `desfazer.sh` a pedido); asserção no `test_skill_md_tem_a_excecao_unica_e_a_etapa_limpar` | nao | EXTERNAL_REVIEW_20261117-124048 |
| R3 | LOW | APLICADA | rodada=2 | teste: `test_r3_sobra_do_projeto_no_git_nao_e_a_mais_velha` · `2503187` | nao | EXTERNAL_REVIEW_20261117-124048 |
| R4 | LOW | REBATIDA_EVIDENCIA | rodada=2 | `checar.sh`, `relatorio()`: `ARRUMAR="${ARRUMAR_DADO}${ARRUMAR_DUP}${ARRUMAR}"` antes do teste de "Pronto"; `test_r4_so_duplicatas_nao_sai_como_pronto` verde no código antigo e no novo | nao | EXTERNAL_REVIEW_20261117-124048 |
| R5 | LOW | REBATIDA_EVIDENCIA | rodada=2 | o `checar.sh` não tem `trap` (`grep -n trap` vazio): o único `trap EXIT` é o do `duplicadas.sh` | nao | EXTERNAL_REVIEW_20261117-124048 |
| N1 | MED | APLICADA | rodada=2 | teste: `test_n1_copia_compartilhada_com_escolha_em_aberto_nao_sai` · `2503187` (duas passadas no awk; cópia de grupo em aberto bloqueada) | sim | EXTERNAL_REVIEW_20261117-124048 |
| N2 | MED | APLICADA | rodada=2 | teste: `test_n2_limpeza_interrompida_depois_do_npx_desfaz_o_registro` · `2503187` (cksum logo depois do npx; desfazer devolve o registro de limpeza interrompida) | sim | EXTERNAL_REVIEW_20261117-124048 |

Rodada 3: as mesmas engines, sobre `2503187`. Nenhum grave.

revisor2: dispensado rodada=3 — sem superfície de risco (regra antiga: 11 arquivos (limiar 8))

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | MED | APLICADA | rodada=3 | teste: `test_r1_na_pasta_pessoal_as_globais_nao_viram_do_projeto` · `241596e` | nao | EXTERNAL_REVIEW_20261117-125555 |
| R2 | LOW | APLICADA | rodada=3 | teste: `test_r2_protegida_que_tambem_sai_no_plano` · `241596e` | nao | EXTERNAL_REVIEW_20261117-125555 |
| R3 | LOW | REBATIDA_EVIDENCIA | rodada=3 | o `checar.sh` não tem `trap` (`grep -n trap` vazio): o único `trap EXIT` é o do `duplicadas.sh` | nao | EXTERNAL_REVIEW_20261117-125555 |
| N1 | MED | APLICADA | rodada=3 | teste: `test_n1_interrompida_no_2o_item_do_npx_desfaz_o_registro` · `241596e` (resumo do registro vazio antes de cada npx) | sim | EXTERNAL_REVIEW_20261117-125555 |

Rodada 4 (confirmação da release, FASE 0a item 8): as mesmas engines, sobre o código final. Nenhum grave, nenhum médio do
revisor. Os achados não reabrem o código: cada correção pediria outra revisão da versão exata, e cada rodada traz 3 a 4
leves novos; o laço já disse PRONTO na rodada 3. Ficam como pendências ✨ da ficha, para a próxima versão da skill.

revisor2: dispensado rodada=4 — sem superfície de risco (regra antiga: 11 arquivos (limiar 8))

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | LOW | REBATIDA_EVIDENCIA | rodada=4 | o `checar.sh` não tem `trap` (`grep -n trap` vazio): o único `trap EXIT` é o do `duplicadas.sh` | nao | EXTERNAL_REVIEW_20261117-130734 |
| R2 | LOW | REBATIDA_ESCOPO | rodada=4 | pendência ✨: falha no 1º item diz "Nada foi tirado" mesmo quando o npx tocou pasta fora do plano (a frase do erro já nomeia a pasta); trocar por "Nada do plano foi tirado" | nao | EXTERNAL_REVIEW_20261117-130734 |
| R3 | LOW | REBATIDA_ESCOPO | rodada=4 | pendência ✨: caminho com barra invertida passado ao awk por `-v` (passar por `ENVIRON`); não ocorre em macOS, Linux nem Git Bash, que usam `/` | nao | EXTERNAL_REVIEW_20261117-130734 |
| N1 | MED | REBATIDA_ESCOPO | rodada=4 | pendência ✨: conferir também que o npx tirou a linha do registro; com o CLI 1.9.0 medido (`removeInstalledSkills`, EXP-3) a pasta só sai junto com a linha, e o `desfazer.sh` devolve tudo | nao | EXTERNAL_REVIEW_20261117-130734 |

Rodada 5 (confirmação depois do raio de impacto da release, sobre `132643a`): `claude` revisor passou do teto de 15 min
duas vezes, com o Verify Gate rodando junto; a 3ª tentativa inverteu os papéis (`codex` revisa, `claude` audita).
Pergunta `[D4 · limite de tentativas]` ao Roberto, 2026-11-17: "corrigir os 3 e 1 última revisão" (a recomendada).

sem resultado: rodada=5 EXTERNAL_REVIEW_20261117-133131 — o revisor (claude) passou do teto de 15 min
sem resultado: rodada=5 EXTERNAL_REVIEW_20261117-134644 — o revisor (claude) passou do teto de 15 min
revisor2: dispensado rodada=5 — sem superfície de risco (regra antiga: 11 arquivos (limiar 8))

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | HIGH | APLICADA | rodada=5 | teste: `test_r1_desfazer_nao_apaga_a_guardada_se_o_lugar_virou_atalho_para_ela` · `2af4bf7` | sim | EXTERNAL_REVIEW_20261117-140738 |
| R2 | HIGH | APLICADA | rodada=5 | teste: `test_r2_sem_a_linha_do_desfazer_nada_sai` · `2af4bf7` | sim | EXTERNAL_REVIEW_20261117-140738 |
| R3 | MED | APLICADA | rodada=5 | teste: `test_r3_npx_que_deixa_a_linha_no_registro_e_falha` · `2af4bf7` (era a pendência N1 da rodada 4) | sim | EXTERNAL_REVIEW_20261117-140738 |

Rodada 6 (última confirmação, sobre `2af4bf7`): `codex` revisa, `claude` audita. Pergunta `[D4 · limite de tentativas]`
ao Roberto, 2026-11-17: "corrigir e publicar sem 7ª revisão" (a recomendada) — o `review_externo` do ledger da release
fica `dispensado`, com o motivo: a rodada 6 revisou `2af4bf7`; o delta até `c854f81` são só estes 4 consertos, cada um com
teste vermelho antes (`REVISAO6-VERMELHO.log`) e verde depois, e o Verify Gate final roda em `c854f81`.

revisor2: dispensado rodada=6 — sem superfície de risco (regra antiga: 11 arquivos (limiar 8))

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | HIGH | APLICADA | rodada=6 | teste: `test_r1_sem_a_copia_do_registro_o_npx_nao_roda` · `c854f81` | sim | EXTERNAL_REVIEW_20261117-142426 |
| R2 | HIGH | APLICADA | rodada=6 | teste: `test_r2_desfazer_nunca_apaga_a_copia_guardada` · `c854f81` | sim | EXTERNAL_REVIEW_20261117-142426 |
| R3 | HIGH | APLICADA | rodada=6 | teste: `test_r3_pasta_do_plano_apagada_pela_metade_volta_inteira` · `c854f81` | sim | EXTERNAL_REVIEW_20261117-142426 |
| N1 | MED | APLICADA | rodada=6 | teste: `test_n1_protegida_que_nao_sai_inteira_para_o_item` · `c854f81` | sim | EXTERNAL_REVIEW_20261117-142426 |
