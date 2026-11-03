# AVALIAÇÃO — F12_CONTEXTO · ciclo 2 (contexto fresco, modo veredito)

- **Commit avaliado:** `a57fde6` (branch `feat/f12-contexto`, base `v2.3.1`; o ciclo 1 avaliou `fb77fa7`)
- **Avaliador:** agente fresco (subagente em contexto limpo), brief do modo `veredito` com os achados do ciclo 1
- **Evidência:** 22 logs `sdd/reports/evidence/F12_CONTEXTO/AVAL-BUILD-2-*.log` (gravados pelo `ev.sh`)
- **Piso:** `/bin/bash` 3.2.57 · `/usr/bin/python3` 3.9.6

## Veredito

VEREDITO: PASS

O gate do DEFINE sai 0 em `a57fde6` (publish-gate GREEN; 960 testes OK em 1062 s; `AVAL-BUILD-2-01`). Os 9 achados
do ciclo 1 estão corrigidos, cada um conferido por sonda de comportamento (`AVAL-BUILD-2-02` a `-12`). AT-001 a AT-026:
PASS (AT-020 por recibo). Sem HIGH nem MEDIUM aberto.

## Achados (LOW)

| # | Achado | Reprodução |
|---|---|---|
| L-A | citação de pattern em lista ou com recuo não conta (a correção de M2 abriu o caminho) | `AVAL-BUILD-2-04` |
| L-B | exemplo em cerca `~~~` conta como citação | `AVAL-BUILD-2-04` |
| L-C | árvore limpa sem `[incluir]`: `--comparar` sai 64 (regressão de M1; falha fechada) | `AVAL-BUILD-2-21`, `-03` |
| L-D | briefs não proíbem commit nem dizem que `superficies:` leva caminho versionado sem crase; `--validade` aceita pathspec que não casa nada | `AVAL-BUILD-2-02`, `-05` |
| L-E | duas dúvidas na mesma linha escondem a 2ª | `AVAL-BUILD-2-06` |
| L-F | os recibos do AT-020 são de `fb77fa7`, anteriores ao texto final dos passos | `codex-*.log` |
| L-G | `contexto-lint --self-test` vermelho antes do 1º commit de um projeto | `AVAL-BUILD-2-22` |
