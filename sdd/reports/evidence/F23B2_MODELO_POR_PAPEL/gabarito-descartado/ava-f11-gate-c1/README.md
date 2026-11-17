# ava-f11-gate-c1 — avaliador, F11_GATE, ciclo 1 (NEEDS_WORK confirmado)

## De onde veio

- Avaliação: `sdd/reviews/AVALIACAO_F11_GATE_20261101-ciclo1.md`, na branch `docs/incorporar-starter`.
- Commit avaliado: `468d605` (`fix(f11): eval-agree agrupa pela engine base…`, 2026-11-01 07:35), citado no
  cabeçalho ("sobre `468d605`") e no bloco ("HEAD 468d605 (feat/f11-gate)"). Existe no projeto.
- DEFINE e DESIGN: v1.1 os dois. O `BUILD_REPORT_F11_GATE.md` cita "DEFINE v1.1, 27 ATs" e "DESIGN v1.1"; o
  Revision History dos dois termina em 1.1 (revisão do DESIGN, antes do código), sem linha do build. Os arquivos de
  `entrada/` saem de `git show 7e947d4:sdd/features/…`, o único commit desses documentos. O commit avaliado não tem
  `sdd/features/`.
- Brief: a seção "Brief — modo `veredito`" de `contexto-fresco.md`; o texto dela em `468d605` é igual ao de hoje. A
  última linha (tabela por AT) foi acrescentada para o medidor; o avaliador da época devolveu a tabela comprimida
  (`| 001, 002, 004–027, Verify Gate | PASS |`).

## O esperado, linha a linha

`VEREDITO: NEEDS_WORK`: a linha `Veredito: NEEDS_WORK — 1 MEDIUM e 4 LOW` do bloco.

| AT | Na avaliação | No esperado | Por quê |
|---|---|---|---|
| AT-001, AT-002, AT-004 a AT-027 | linha `001, 002, 004–027, Verify Gate` → PASS | PASS | tabela da avaliação (uma linha para o intervalo) |
| AT-003 | `FALHA PARCIAL (M1)` | **FAIL** | decisão abaixo |

Decisão do AT-003: "falha parcial" — o gate não confere DISAGREE_EVIDENCE, DISAGREE_CONCERN nem NOVO; sabotar
`vereditos_auditor` para aceitar só AGREE deixa o gate VERDE (`evidence/F11_GATE/AVAL1-15-…log`). O conserto veio em
**`a9813ff`** (`fix(f11): revisão de contexto fresco do build, ciclo 1 — 1 MEDIUM e 4 LOW`), que cria
`sdd/review/stubs/respostas/auditor-misto.md` e o teste; o ciclo 2 (`AVALIACAO_F11_GATE_20261101-ciclo2.md`) diz
"Os 5 achados do ciclo 1 (M1, L1, L2, L3, L4) FECHADOS por execução (AVAL2-15/45…)". Defeito confirmado, logo FAIL.

Atenção para a meta: três ATs ficaram PASS na tabela histórica com um LOW pendurado, também consertados em
`a9813ff`: AT-002 (L1, custo do claude igual nos dois campos), AT-006 (L2, credencial só provada no claude) e
AT-016 (L3, `eval-agree` sem pasta sai 64 em vez de 2). O esperado segue a tabela (PASS). Um candidato mais estrito
que der FAIL num deles conta como diferença (não como erro grave); 3 diferenças em 27 já tiram da meta (24/27 =
88,9%).

## Medidas

- Arquivos `tests/test_*.py` no commit: **39**. Suíte inteira: 881 testes em **801 s** (~13,4 min,
  `evidence/F11_GATE/AVAL1-30-verify-gate.log`).
- Tempo e custo do avaliador histórico: **não registrados**. Há 40 sondas `AVAL1-*` (35 `.log` e 5 `.sonda.txt`).
  A linha de base da F23 dá `F11_GATE | n/d` até para a feature inteira.
- Cabe em ~15 min? **Só se o avaliador não rodar o Verify Gate inteiro.** Os ATs se provam pelo gate
  (`adversarial-review-gate.sh`: "90 asserções, 5 s" no texto da avaliação) e por testes dirigidos; o histórico rodou também o Verify
  Gate (13,4 min) e o AT-024 (`AVAL1-31`, 137 s), o que passa de 15 min. O `--teto-s` padrão do `papel-serie.sh`
  (1800 s) comporta, mas a meta de ~15 min não.

## Ressalva: AT que precisa da tag `v2.3.0`

AT-024 (os testes da F10 passam sem mudança) foi provado rodando os testes de `v2.3.0` contra o HEAD
(`git archive v2.3.0 tests/…`). A cópia do `papel-serie.sh` não tem tags; o avaliador tende a dar NAO_VERIFICADO.
É 1 de 27: sozinho não tira da meta (26/27 = 96%).
