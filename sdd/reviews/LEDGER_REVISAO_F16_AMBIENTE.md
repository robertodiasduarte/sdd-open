# Ledger da revisão — F16_AMBIENTE

Rodada 1 (revisão do DESIGN, `--paths` com o DEFINE e o DESIGN): uma engine só (`--um-engine`), claude revisou e auditou,
`diversidade: nenhuma`, por decisão do Roberto em 2026-11-10 com o saldo da OpenRouter em US$ 0,07 (lido em `/credits`). A OpenRouter
foi recarregada durante a rodada (US$ 20,07, lido em `/credits`): da rodada 2 em diante, claude revisa e `openrouter` (qwen,
pago) audita. Sem 2º revisor (`--no-revisor2`): codex sem cota e gemini sem credencial. Teto do método: 3 rodadas de revisão e 2
ciclos do avaliador; passar dele é pergunta ao Roberto. Os achados da rodada 1 são de documento (ainda não havia código): nenhum
tem teste que falhe em código antigo, então `dano` é `nao` em todos.

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | HIGH | APLICADA | rodada=1 | Pattern 2 do DESIGN v1.1 reescrito, um `if` por candidato sem variável de laço; casos "nenhum roda" e "nenhum existe" previstos em `tests/test_python_resolver.py` | nao | EXTERNAL_REVIEW_20261110-221223 |
| R2 | MED | APLICADA | rodada=1 | `SDD_PYTHON` testado entre aspas como uma palavra (DESIGN v1.1, Decision 2 item 2); caso com espaço no caminho previsto no teste | nao | EXTERNAL_REVIEW_20261110-221223 |
| R3 | MED | APLICADA | rodada=1 | confirmado no código: `exec python3` em `sdd/bin/adversarial-review.sh:47` e em mais 4 scripts; Decision 2 troca a função exportada pelo calço no PATH | nao | EXTERNAL_REVIEW_20261110-221223 |
| R4 | MED | APLICADA | rodada=1 | confirmado: só 1 dos 16 scripts tem `set -e`; o resolvedor para na carga com exit 64 (DESIGN v1.1, Decision 2 item 6) | nao | EXTERNAL_REVIEW_20261110-221223 |
| R5 | MED | APLICADA | rodada=1 | a cópia do `init` já é recursiva (`bin/sdd-open.sh:589`), mas faltava a prova: item 22 do manifest testa `init` e `sync` com `sdd/bin/lib/` | nao | EXTERNAL_REVIEW_20261110-221223 |

Rodada 2 (revisão do DESIGN v1.1): claude revisou e `openrouter` (qwen/qwen3.7-plus) auditou, `diversidade: vendor`, US$ 0,89 no total
(US$ 0,02 pagos). Os testes citados já existem em `tests/test_python_resolver.py` e falham na v1.1 da biblioteca (que parava na carga).

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | MED | APLICADA | rodada=2 | conferido: 14 dos 16 scripts têm guarda própria; `docs-extract-decisions.sh` e `governanca-fronteira.sh` ganham `sdd_python_exigir`; `test_nenhum_python_a_guarda_falha_calada_e_exigir_para` | nao | EXTERNAL_REVIEW_20261110-221917 |
| R2 | MED | APLICADA | rodada=2 | confirmado: `bin/sdd-open.sh` só usa Python nos vendors claude e gemini, e a parada na carga o derrubaria no `init --vendors codex`; a carga nunca para e `sdd_python_pronto` substitui as 21 guardas; `test_so_o_atalho_a_carga_segue_e_a_guarda_diz_a_causa_uma_vez` | nao | EXTERNAL_REVIEW_20261110-221917 |
| R3 | LOW | APLICADA | rodada=2 | a causa diz a versão; `test_python_velho_e_dito_pela_versao` e `test_so_python_2_e_dito_pela_versao` | nao | EXTERNAL_REVIEW_20261110-221917 |
| R4 | LOW | APLICADA | rodada=2 | o motivo do calço que não se cria fica anotado e a guarda o diz; `test_calco_que_nao_se_cria_e_dito` | nao | EXTERNAL_REVIEW_20261110-221917 |

Rodada 3 (revisão do código, o diff inteiro da frente desde `origin/main`, 52 arquivos): claude revisou e `openrouter` (qwen) auditou,
`diversidade: vendor`, US$ 1,68 no total (US$ 0,03 pagos); o auditor concordou com os 7. É a última rodada do teto do método. A
linha de base dos testes novos está em `sdd/reports/evidence/F16_AMBIENTE/BASELINE-vermelho-rodada3.log`: R1, R2 e R5 falham no
código de antes; R3 e R4 pediam cobertura e passam nos dois lados.

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | MED | APLICADA | rodada=3 | teste: `test_sdd_python_igual_a_python3_nao_entra_em_laco` · com `SDD_PYTHON=python3`, o calço chamava `python3` e achava a si mesmo no PATH: todo script do pacote ficava parado para sempre (reproduzido: sem resposta em 8 s); o calço passa a chamar o caminho absoluto | sim | EXTERNAL_REVIEW_20261111-044013 |
| R2 | MED | APLICADA | rodada=3 | a versão só vale com rc 0 e no formato X.Y; `test_candidato_que_imprime_versao_e_sai_com_erro_nao_serve` e `test_candidato_que_imprime_lixo_nao_serve` | nao | EXTERNAL_REVIEW_20261111-044013 |
| R3 | MED | APLICADA | rodada=3 | cobertura: `test_script_real_de_sdd_bin_com_o_atalho_da_store` roda o `ledger-revisao-lint.sh` pelo trecho de carga dele, com o atalho e com o `python` ao lado; no Windows, a medição achou o caminho com `\` que fazia a carga cair na guarda antiga (conserto: `${0//\\//}`) | nao | EXTERNAL_REVIEW_20261111-044013 |
| R4 | MED | APLICADA | rodada=3 | `report-lint` e `sdd-archive` citam `test_log_capturado_da_feature_passa` e `test_lista_por_lote_e_nao_muda_nada`, e a asserção exige um teste por achado | nao | EXTERNAL_REVIEW_20261111-044013 |
| R5 | LOW | APLICADA | rodada=3 | `\|\| :` depois do calço; `test_set_e_com_calco_que_nao_se_cria_nao_derruba_na_carga` | nao | EXTERNAL_REVIEW_20261111-044013 |
| R6 | LOW | APLICADA | rodada=3 | `sistema` lida uma vez em `editor_achado` e passada a `editor_no_path` (`checar.sh`) | nao | EXTERNAL_REVIEW_20261111-044013 |
| R7 | LOW | APLICADA | rodada=3 | o `if __name__ == "__main__"` foi para o fim de `tests/test_inventario.py` | nao | EXTERNAL_REVIEW_20261111-044013 |

Rodada 4 (fecho, acima do teto do método por decisão do Roberto em 2026-11-11, sobre `1bf3b1f`, o commit final): claude revisou e
`openrouter` (qwen) auditou, `diversidade: vendor`, US$ 1,78 (US$ 0,04 pagos). Regra de fecho, como na F19: só achado grave pede
conserto; médio e leve viram pendência na ficha (`REBATIDA_ESCOPO`). Nenhum grave.

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | MED | REBATIDA_ESCOPO | rodada=4 | real: com uma `sdd-checar-ambiente` anterior à 1.5.0 instalada, `checar.sh --editor` cai no modo normal, sai 0 e a 1ª linha do diagnóstico iria para o slot `editor`; pendência na ficha (a `sdd-new-session` conferir a versão da checar-ambiente, ou o formato da 1ª linha) | nao | EXTERNAL_REVIEW_20261111-071016 |
| R2 | MED | REBATIDA_EVIDENCIA | rodada=4 | `.agents/skills/sdd-iniciar-repo/scripts/inventario.sh:15-16` tem só `set -u` e `set -o pipefail`, sem `set -e`: o `wait` com 137 não encerra o subshell; a função é idêntica à do `checar.sh` (`tests/test_f16_textos.py`), onde o teto é testado (`test_gh_pendurado_respeita_o_teto`); o auditor também discordou | nao | EXTERNAL_REVIEW_20261111-071016 |
| R3 | MED | REBATIDA_EVIDENCIA | rodada=4 | `.github/workflows/release.yml:44-45` e `.github/workflows/publish-gate.yml:15-16` declaram `permissions: contents: read` no topo: o job Windows herda leitura; só o job `release` pede escrita (`test_token_global_so_le`, `test_release_depende_dos_testes_e_e_o_unico_com_escrita`) | nao | EXTERNAL_REVIEW_20261111-071016 |
| R4 | LOW | REBATIDA_ESCOPO | rodada=4 | real e cosmético: no `doctor` (`bin/sdd-open.sh:763`), o `sdd_python_pronto` roda dentro de `$(…)` e o aviso "dito uma vez" pode repetir; pendência na ficha | nao | EXTERNAL_REVIEW_20261111-071016 |

Rodada 5 (só o delta desde a rodada 4, `--base 1bf3b1f`, sobre `9ab4541`: o teto do macOS e o ajuste do editor pedido pelo Roberto;
acima do teto do método, por decisão dele): claude revisou e `openrouter` (qwen) auditou, `diversidade: vendor`, US$ 0,76 (US$ 0,02
pagos). Por decisão do Roberto, o R1 e o R2 foram consertados já (texto da `sdd-new-session` e teste, vermelho em `9ab4541`:
`BASELINE-vermelho-rodada5.log`); esse delta, só de texto, fica sem revisão externa, com dispensa no ledger da release.

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | MED | APLICADA | rodada=5 | a escolha do editor ia para o `sdd/config.yaml` da frente, que só chega à branch padrão na integração: a pergunta "uma vez só" voltava em cada frente nova; agora vai para `git config --local sdd.editor` (preferência deste computador, vale na hora para todas as frentes); `test_slot_vazio_pergunta_uma_vez_e_nunca_escolhe_sozinho` | nao | EXTERNAL_REVIEW_20261111-084600 |
| R2 | LOW | APLICADA | rodada=5 | a opção recomendada passa a dizer "o 1º na ordem da detecção (o comando no PATH vem antes do app do macOS e do `.cmd` do Windows)"; mesmo teste | nao | EXTERNAL_REVIEW_20261111-084600 |
