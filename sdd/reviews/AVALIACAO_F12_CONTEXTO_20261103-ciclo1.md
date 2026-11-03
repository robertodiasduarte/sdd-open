# AVALIAÇÃO — F12_CONTEXTO · ciclo 1 (contexto fresco, modo veredito)

- **Commit avaliado:** `fb77fa7` (branch `feat/f12-contexto`, base `v2.3.1`)
- **Avaliador:** agente fresco (subagente em contexto limpo), brief do modo `veredito` de `sdd-build/references/contexto-fresco.md`
- **Evidência:** 20 logs `sdd/reports/evidence/F12_CONTEXTO/AVAL-BUILD-1-*.log` (gravados pelo `ev.sh`)
- **Piso:** `/bin/bash` 3.2.57 · `/usr/bin/python3` 3.9.6

## Veredito

VEREDITO: NEEDS_WORK

## Por AT

| AT | Resultado |
|---|---|
| AT-001 | PARCIAL (L1: ordem das chaves do cabeçalho não conferida) |
| AT-002 | PASS com achado M3 |
| AT-003, AT-004, AT-006 a AT-011, AT-013, AT-015 a AT-024, AT-026 | PASS |
| AT-005 | FALHA PARCIAL (M1) |
| AT-012 | PASS com achados L2, L3 |
| AT-014 | FALHA PARCIAL (M2) |
| AT-020 | PASS por recibo (`codex-*.log`) |
| AT-025 | NAO_VERIFICADO (suíte inteira não rodada pelo avaliador; o Verify Gate cobre) |

## Achados

| # | Sev. | Achado | Reprodução |
|---|---|---|---|
| M1 | MEDIUM | a fronteira não vê arquivo limpo editado e commitado pelo agente | `AVAL-BUILD-1-06` caso `edita-limpo-e-commita` |
| M2 | MEDIUM | `patterns-lint --design` conta o blockquote do template e exemplos em cerca como citação | `AVAL-BUILD-1-08`, `-09` |
| M3 | MEDIUM | `superficies:` com crase ou com erro de digitação deixa o CONTEXTO válido para sempre | `AVAL-BUILD-1-11` §2 |
| L1 | LOW | ordem das chaves do cabeçalho não conferida | `AVAL-BUILD-1-11` §1 |
| L2 | LOW | marcador de governança esconde outra dúvida aberta | `AVAL-BUILD-1-05` |
| L3 | LOW | linha `Governança` com recuo ou sem negrito dá "ausente" | `AVAL-BUILD-1-02` |
| L4 | LOW | os 2 lints chamados de subpasta com caminho relativo saem 64 | `AVAL-BUILD-1-11` §3 |
| L5 | LOW | ordem snapshot → brief no texto dos passos 1.5 e 11 gasta o redespacho | `AVAL-BUILD-1-14` |
| L6 | LOW | `governanca-bloco.py` aceita Gnn repetido | `AVAL-BUILD-1-07` |

Os 9 achados foram aplicados em `a57fde6`, cada um com teste vermelho em `fb77fa7` (`baseline-aval1.log`).
