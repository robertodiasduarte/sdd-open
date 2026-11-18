# Ledger da revisão — F16W2_F22 (curadoria do playbook)

> Uma linha por achado decidido. Conferido por `bash sdd/bin/ledger-revisao-lint.sh`; lido por `sdd-fluxo.sh loop --ledger`
> e por `eval-revisores.sh`. Critério da coluna `dano`: `sdd/review/CRITERIO_DANO.md`.

Cadeia: claude revisa (o CLI escolheu `claude-fable-5-2`), `openrouter` (qwen/qwen3.7-plus) audita, `--no-revisor2` e
`--no-desempate`. Rodada 1 (diff `v2.17.0..66362e0`, só `sdd/playbook.md`): saldo US$ 14,67 antes; custo US$ 0,3451. O
auditor discordou dos 2 (sem contexto para confirmar).

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | LOW | REBATIDA_EVIDENCIA | rodada=1 | a contagem `LM-015 ajudou+1` vem da colheita e da conferência (`BUILD_REPORT_F16W2_WINDOWS.md:60`, ✔ tratado; `CURATOR-conferido.txt` linha AUTO); a curadoria proíbe mudar contagem à mão; o refino e a contagem são itens separados, ambos registrados | nao | EXTERNAL_REVIEW_20261115-181908 |
| R2 | LOW | REBATIDA_EVIDENCIA | rodada=1 | o conserto (o ajudante `path_restrito`) é da F16W2 (`DESIGN_F16W2_WINDOWS.md:101`, `BUILD_REPORT_F16W2_WINDOWS.md:134`); a F16W só mediu as quedas: a ficha F16W2_WINDOWS é a do conserto | nao | EXTERNAL_REVIEW_20261115-181908 |

Depois da rodada 1, o CI do PR #33 caiu no `test_f17c_passo0` e no `test_f16w2_passo0` (fixavam as contagens de
curadorias passadas; conserto em `fa466b5`). Rodada 2 (diff `v2.17.0..fa466b5`): custo US$ 0,3502; o auditor concordou com
os 2.

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | LOW | APLICADA | rodada=2 | teste: `test_as_tres_licoes_da_f16w_estao_no_playbook` · a janela `conf=2026-11-1[4-9]` reprovaria toda curadoria a partir de 20/11; agora a data é comparada (`>=`), em `8f944fc` | nao | EXTERNAL_REVIEW_20261115-183115 |
| R2 | LOW | APLICADA | rodada=2 | teste: `test_as_contagens_da_f17b_foram_aplicadas` · `mordeu=\d+` no lugar do `mordeu=0` literal, em `8f944fc` | nao | EXTERNAL_REVIEW_20261115-183115 |

Rodada 3 = teto (diff `v2.17.0..8f944fc`): custo US$ 0,3735; o auditor concordou. Só leve: adiado para a ficha, sem
mudar o código; esta rodada vale para a versão da release.

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | LOW | REBATIDA_ESCOPO | rodada=3 | pendência na ficha: `test_as_contagens_ajudou_da_f16w_nao_foram_aplicadas` com `assertLessEqual` passa também com o conjunto vazio; hoje ele não é vazio (LM-012, LM-027, LM-028 seguem com conf=2026-11-14); a troca é exigir ≥ 1 lição datada ou guardar as datas num arquivo de referência | nao | EXTERNAL_REVIEW_20261115-183446 |
