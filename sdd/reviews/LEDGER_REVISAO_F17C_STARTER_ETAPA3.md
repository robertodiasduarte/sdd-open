# Ledger da revisão — F17C_STARTER_ETAPA3

> Uma linha por achado decidido, de todas as rodadas da revisão adversarial desta frente. Conferido por
> `bash sdd/bin/ledger-revisao-lint.sh`; lido por `sdd-fluxo.sh loop --ledger` e por `eval-revisores.sh`.
> Critério da coluna `dano`: `sdd/review/CRITERIO_DANO.md`.

Cadeia: claude revisa, `openrouter` (qwen/qwen3.7-plus) audita, sem 2º revisor (`--no-revisor2`: codex sem cota) e sem
desempate (`--no-desempate`), como na F16, na F18 + F20, na F17 e na F17b. Rodada 1 (diff inteiro `v2.14.0..fc76456`,
sem `--paths`, 76 arquivos, com o BRAINSTORM, o DEFINE e o DESIGN de contexto): saldo da OpenRouter US$ 13,48 antes;
custo US$ 1,9855 (claude 1,9376 por assinatura nominal, qwen 0,0479). O auditor concordou com os 2.

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | LOW | APLICADA | rodada=1 | teste: `test_at006_moldes_sem_sobras_de_outro_projeto` · o molde do DESIGN ainda dizia "Custom metrics via Cloud Monitoring" | nao | EXTERNAL_REVIEW_20261114-005631 |
| R2 | LOW | APLICADA | rodada=1 | teste: `test_at004_handoffs_dos_protocolos_coerentes` · o passo 15 do build web falava em "handoff de Release" no caso bloqueado | nao | EXTERNAL_REVIEW_20261114-005631 |

Rodada 2, a última (diff inteiro `v2.14.0..e1f1b42`, sem `--paths`, depois dos consertos da rodada 1, do raio de impacto,
dos 4 ciclos do avaliador e das séries 3 a 5 do teste do iniciante): saldo da OpenRouter US$ 8,79 antes; custo US$ 1,8783
(claude 1,8202 por assinatura nominal, qwen 0,0581). O auditor concordou com os 2.

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | MED | APLICADA | rodada=2 | teste: `test_revisao_rodada_2` · o design e o build web não diziam que o UX_REVIEW fica em `sdd/reviews/`, onde a `ux-review` gerada pela builder 1.6.0 grava; o design poderia seguir sem os MUSTs de UX | nao | EXTERNAL_REVIEW_20261114-082513 |
| R2 | LOW | APLICADA | rodada=2 | teste: `test_revisao_rodada_2` · a referência de migration do modo web só tratava a saída 2 ou 3 do runner, e o modo web lê o exit cru | nao | EXTERNAL_REVIEW_20261114-082513 |

Rodada 3 (diff inteiro `v2.14.0..97503a7`, depois dos consertos da rodada 2; a revisão que vale para a release): saldo US$ 8,73
antes; custo US$ 1,9515 (claude 1,9001 nominal, qwen 0,0514). O revisor não achou nada; o auditor trouxe 1 achado novo.

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| N1 | HIGH | REBATIDA_EVIDENCIA | rodada=3 | o bloco ```` ```bash ```` com `sdd/bin/verify-gate.sh --print` está no `SKILL.md` do Open (`.agents/skills/sdd-define/SKILL.md:219`), que o gerador não leva; `grep -n '```bash\|verify-gate' .agents/skills/sdd-define/web/MODO_WEB.md .agents/skills/sdd-define/web/references/*.md` sai 1 (nada); o teste lê a skill GERADA e passa (`test_at005_define_e_design_nao_pedem_comando_ao_aluno` OK em 97503a7) | nao | EXTERNAL_REVIEW_20261114-083418 |
