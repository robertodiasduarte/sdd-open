# Ledger da revisão — F16W_WINDOWS

> Uma linha por achado decidido, de todas as rodadas da revisão adversarial desta frente. Conferido por
> `bash sdd/bin/ledger-revisao-lint.sh`; lido por `sdd-fluxo.sh loop --ledger` e por `eval-revisores.sh`.
> Critério da coluna `dano`: `sdd/review/CRITERIO_DANO.md`.

Cadeia: claude revisa, `openrouter` (qwen/qwen3.7-plus) audita, sem 2º revisor (`--no-revisor2`: codex sem cota) e sem
desempate (`--no-desempate`), como da F16 à F17c. Rodada 1 (diff inteiro `v2.15.0..ce3a779`, sem `--paths`, 34 arquivos,
com o BRAINSTORM, o DEFINE e o DESIGN de contexto): saldo da OpenRouter US$ 6,52 antes; custo US$ 1,1780 (claude 1,1496
por assinatura nominal, qwen 0,0284). O auditor concordou com R1 e R3 e discordou do R2 (os 5 testes cobririam o ramo no CI
do Windows); o R2 foi aplicado mesmo assim: o DEFINE promete um teste do ramo que rode também no gate do Mac, e o job do
Windows é informativo.

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | MED | APLICADA | rodada=1 | teste: `test_saida_fora_do_cp1252_nao_derruba_o_executor` · no Windows o stdout do executor num pipe é cp1252 estrito: a cauda de uma unidade com 🛑 derrubava o print antes do log e do resumo; e um módulo que sai ou imprime na importação derrubava a enumeração ou sujava o `--lista` | nao | EXTERNAL_REVIEW_20261114-121622 |
| R2 | MED | APLICADA | rodada=1 | teste: `TestVigiaNoWindows` · o ramo do `taskkill` e a regra do relógio (com o caso vizinho, rc 0 tarde) não tinham teste fora do CI do Windows; a regra virou a função `rc_do_vigia` e o /proc ganhou `SDD_CHECAR_PROC` para os testes | nao | EXTERNAL_REVIEW_20261114-121622 |
| R3 | LOW | APLICADA | rodada=1 | teste: `test_classes_viram_unidades_e_a_herdada_conta_uma_vez` · a classe importada por outro módulo pesava 2 (os ids repetidos): o peso conta cada id uma vez | nao | EXTERNAL_REVIEW_20261114-121622 |

Rodada 2 (diff inteiro `v2.15.0..c9cde6e`, sem `--paths`, 35 arquivos, depois dos consertos da rodada 1, dos 2 ciclos do avaliador
e do raio de impacto): saldo da OpenRouter US$ 6,46 antes; custo US$ 1,2726 (claude 1,2490 nominal, qwen 0,0236). O auditor
concordou com os 2.

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | MED | APLICADA | rodada=2 | teste: `test_avaliador_guard_usa_o_bash_do_claude_code_e_nao_o_nome` e `test_subprocess_nunca_chama_bash_pelo_nome` · o hook do avaliador chamava "bash" pelo nome (no Windows, o bash.exe do WSL em System32), contra a Decision 6; agora CLAUDE_CODE_GIT_BASH_PATH, depois shutil.which (ordem do PATH); a guarda de test_windows barra "bash" pelo nome em subprocess | nao | EXTERNAL_REVIEW_20261114-134503 |
| R2 | MED | APLICADA | rodada=2 | teste: `test_saida_fora_do_cp1252_nao_derruba_o_executor` · a unidade da fixture imprimia o 🛑 pela codificação dela (cp1252 no Windows, onde o executor não lhe dá PYTHONIOENCODING) e o teste cairia lá; a fixture grava os bytes UTF-8 direto e o teste mede só o stdout do executor | nao | EXTERNAL_REVIEW_20261114-134503 |

Rodada 3, a última dentro do teto (diff inteiro `v2.15.0..e6c845a`, sem `--paths`, depois dos consertos da rodada 2): saldo
US$ 6,43 antes; custo US$ 1,5885 (claude 1,5638 nominal, qwen 0,0247). O auditor discordou por falta de contexto (o diff
cortava o começo do `main()`); conferido no arquivo: `json.load(sys.stdin)` nos 2 guards, o defeito é real.

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | MED | APLICADA | rodada=3 | teste: `test_report_guard_le_o_payload_em_utf8_cru_num_sistema_cp1252` · os 2 guards liam o payload do hook com `json.load(sys.stdin)` (cp1252 no Windows): o ⚠️ em UTF-8 cru derrubava a leitura e a gravação passava sem guarda; agora em bytes, decodificado em UTF-8 | nao | EXTERNAL_REVIEW_20261114-135448 |

O conserto da rodada 3 (`103697e`, 2 guards e 1 teste) ficou sem revisor externo: **dispensa do Roberto** (2026-11-14,
pergunta do teto do método: rodada 4 só do delta, rodada 4 inteira ou dispensa). Prova: o teste novo falha em `e6c845a` e
passa em `103697e`. A revisão que vale para a release é a rodada 3 (`EXTERNAL_REVIEW_20261114-135448`, sobre `e6c845a`).

Depois da rodada 3, até `ad32fe1`, sem revisor externo: **dispensa do Roberto** (2026-11-14, no bloco da publicação), com o
teste de cada mudança: `103697e` (os 2 guards leem o payload em UTF-8: `test_report_guard_le_o_payload_em_utf8_cru_num_sistema_cp1252`,
dispensa anterior), `4e76b39` (o número de 11 dígitos montado no teste: o publish-gate verde), `491efa6` (o teto do
`test_deploy_do_sha`: o módulo verde e a corrida tirada), `ad32fe1` (as 4 frases de Windows: `test_frases_dizem_o_que_o_workflow_prova`;
o log do executor sem CR: `test_log_da_unidade_sem_cr`).
