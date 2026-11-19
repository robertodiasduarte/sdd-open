# Ledger da revisão — F28_REVISORES_OPENROUTER

> Uma linha por achado decidido, de todas as rodadas da revisão adversarial desta frente. Critério da coluna `dano`:
> `sdd/review/CRITERIO_DANO.md`.

Revisão do DESIGN. D1: revisor `claude`; o auditor não rodou (`codex` sem créditos na conta, `gemini` sem
credencial), e nenhuma engine paga do OpenRouter foi usada sem o OK do Roberto. D2: `--um-engine` com `claude`
(revisou e auditou, `diversidade: nenhuma`). Os achados da D1 reapareceram na D2 e foram decididos lá.

sem resultado: rodada=D1 EXTERNAL_REVIEW_20261118-211157 — auditor sem engine disponível (codex sem créditos, gemini sem credencial)
revisor2: dispensado rodada=D2 — sem superfície de risco

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | MED | APLICADA | rodada=D2 | DESIGN Decision 8, precedência de R05/R06 só com slot no OpenRouter, vazio ou incompleto | nao | EXTERNAL_REVIEW_20261118-211712 |
| R2 | MED | APLICADA | rodada=D2 | DESIGN Decision 4, JSON ilegível ou de forma inesperada ⇒ R20 | nao | EXTERNAL_REVIEW_20261118-211712 |
| R3 | MED | APLICADA | rodada=D2 | DESIGN Decision 5, bash no macOS ⇒ ~/.bash_profile; aviso de chave em outro perfil | nao | EXTERNAL_REVIEW_20261118-211712 |
| R4 | MED | APLICADA | rodada=D2 | DESIGN Decision 8 e DEFINE 1.2 (A4), R03 antes de R07 | nao | EXTERNAL_REVIEW_20261118-211712 |
| R5 | MED | APLICADA | rodada=D2 | DESIGN Decision 6, herança do ambiente com a fonte e o que não foi testado | nao | EXTERNAL_REVIEW_20261118-211712 |
| R6 | LOW | APLICADA | rodada=D2 | DESIGN Decision 4, prazo pelo relógio na chamada inteira | nao | EXTERNAL_REVIEW_20261118-211712 |
| R7 | LOW | APLICADA | rodada=D2 | DESIGN Decision 5, chave fora de [A-Za-z0-9_-] recusada | nao | EXTERNAL_REVIEW_20261118-211712 |
| R8 | LOW | APLICADA | rodada=D2 | DESIGN Decision 3, "sem base" vira aviso com a consequência (o auditor rebateu pela Decision 3; o ponto vale) | nao | EXTERNAL_REVIEW_20261118-211712 |
| N1 | MED | APLICADA | rodada=D2 | DESIGN Decision 4, 402 ⇒ R16, outro status ⇒ R20, nunca aceita sem a resposta reconhecida | nao | EXTERNAL_REVIEW_20261118-211712 |

Revisão do código, rodada 1: `--um-engine` com `claude` (codex sem créditos, gemini sem credencial), `diversidade: nenhuma`.

revisor2: dispensado rodada=1 — sem superfície de risco (regra antiga: 44 arquivos (limiar 8))

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | MED | APLICADA | rodada=1 | teste: `GuardarChave.test_bash_no_macos_usa_o_profile_que_ja_existe` · o .bash_profile novo esconderia o .profile e quebraria o PATH do terminal do aluno | sim | EXTERNAL_REVIEW_20261118-213723 |
| R2 | MED | APLICADA | rodada=1 | teste: `Estados.test_R05_no_perfil_local_que_o_passo_a_passo_recomenda` · diagnosticar.sh PERFIS com os .local | nao | EXTERNAL_REVIEW_20261118-213723 |
| R3 | LOW | APLICADA | rodada=1 | teste: `Testar.test_R21_slot_openrouter_sem_modelo_confere_o_modelo_do_registry` | nao | EXTERNAL_REVIEW_20261118-213723 |
| R4 | LOW | APLICADA | rodada=1 | teste: `Estados.test_R09_cli_do_slot_ausente` · o passo muda com a origem | nao | EXTERNAL_REVIEW_20261118-213723 |
| R5 | LOW | APLICADA | rodada=1 | teste: `Testar.test_R19_teto_de_10_s_pela_chamada_inteira` · consulta numa thread com prazo | nao | EXTERNAL_REVIEW_20261118-213723 |
| N1 | MED | APLICADA | rodada=1 | teste: `Testar.test_revisores_so_em_clis_o_testar_nao_consulta_o_openrouter` | nao | EXTERNAL_REVIEW_20261118-213723 |

Revisão do código, rodada 2: `--um-engine` com `claude`, `diversidade: nenhuma`.

revisor2: dispensado rodada=2 — sem superfície de risco (regra antiga: 45 arquivos (limiar 8))

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | MED | APLICADA | rodada=2 | teste: `Testar.test_R20_resposta_que_nao_e_http_sem_traceback` · exceção do http.client vira R20, sem traceback | nao | EXTERNAL_REVIEW_20261118-214759 |
| R2 | LOW | APLICADA | rodada=2 | teste: `Estados.test_marca_de_reabertura_antiga_nao_vale` · a marca vale 1 dia | nao | EXTERNAL_REVIEW_20261118-214759 |
| R3 | LOW | APLICADA | rodada=2 | teste: `TestRevisores.test_aspas_vazias_com_espaco_no_fim_contam_como_vazio` | nao | EXTERNAL_REVIEW_20261118-214759 |
| R4 | LOW | APLICADA | rodada=2 | teste: `GuardarChave.test_linha_antiga_dentro_de_if_nao_quebra_o_perfil` · um if/then vazio quebraria o perfil e o terminal do aluno | sim | EXTERNAL_REVIEW_20261118-214759 |
| N1 | MED | APLICADA | rodada=2 | teste: `Estados.test_chave_num_perfil_que_o_shell_nao_le_nao_prende` · só os perfis do shell do aluno | nao | EXTERNAL_REVIEW_20261118-214759 |

Revisão do código, rodada 3 (a última dentro do teto): `--um-engine` com `claude`, `diversidade: nenhuma`.

revisor2: dispensado rodada=3 — sem superfície de risco (regra antiga: 45 arquivos (limiar 8))

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | MED | APLICADA | rodada=3 | teste: `test_gerar_starter` (26 falhas no código antigo) · a troca do starter tinha o bloco do checar.sh de antes da rodada 2 e o gerador parava | sim | EXTERNAL_REVIEW_20261118-220828 |
| R2 | MED | APLICADA | rodada=3 | teste: `Textos.test_uma_engine_so_sempre_com_a_engine_na_flag` · sem --reviewer, "uma engine só" parava em 64 e voltava à oferta | nao | EXTERNAL_REVIEW_20261118-220828 |
