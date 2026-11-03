# Revisão de contexto fresco do DESIGN — F12_CONTEXTO (modo contrato)

- **Data:** 2026-11-03
- **Revisor:** agente fresco (subagente em contexto limpo), brief do modo `contrato` de `sdd-build/references/contexto-fresco.md`
- **Entrada:** `sdd/features/DEFINE_F12_CONTEXTO.md` v1.2 · `sdd/features/DESIGN_F12_CONTEXTO.md` v1.0
- **Evidência:** 14 logs `sdd/reports/evidence/F12_CONTEXTO/AVAL-DESIGN-01-*.log` (gravados pelo `ev.sh`; `gate-shell-evidencia.sh` 0)
- **Veredito:** NEEDS_WORK — 2 HIGH, 7 MEDIUM, 7 LOW

## Medições

- Suíte de 8 módulos (`test_verify_gate`, `test_gate_baseline`, `test_verify_gate_trace`, `test_avaliador_guard`, `test_fluxo`, `test_sdd_open`, `test_correcoes_w0`, `test_contrato_build_release`) numa cópia: base 195 OK; com o Pattern 1 simulado e as 7 fixtures com a linha, **FAILED (failures=28)** — 18 em `test_verify_gate.py`, 9 em `test_gate_baseline.py`, 1 em `test_verify_gate_trace.py`.
- Gate simulado: (A) `Governança: dispensada — …` com dois-pontos ⇒ 5 "ausente"; (B) linha da tabela dispensada com o marcador no arquivo ⇒ 5 com a mensagem antiga; (C) placeholder `N.A. — <motivo>` ⇒ **0**; (D) sem bloco e sem linha ⇒ 5.
- `git status --porcelain` sem `-uall` recolhe pastas não rastreadas e ignoradas.

## Achados

| # | Sev. | Alvo | Problema | Ajuste |
|---|---|---|---|---|
| H1 | HIGH | Manifest, AT-013 | 3 arquivos de teste com DEFINE em texto quebram e não estão no manifest | manifest + AT-013 |
| H2 | HIGH | AT-009, AT-012, Decision 6 | 2 formas da linha; marcador da 2ª falha esconde as 2 saídas | 1 forma (linha da tabela); marcador de governança imprime as 2 saídas |
| M1 | MEDIUM | Manifest | textos do exit 5 em `verify-gate-contract.md` (+PT), `sdd-build` 5a, `sdd-iterate` 4, `guia-do-aluno.md`, `gate-baseline.sh` | manifest |
| M2 | MEDIUM | Decision 4 | porcelain sem `-uall --ignored=traditional` | fixar as flags; AT-005 com os 2 casos |
| M3 | MEDIUM | passo 11 | snapshot só guarda sha: DEFINE em FORA não se restaura | cópia do DEFINE antes do despacho, `cp` + `cmp` |
| M4 | MEDIUM | template + regex | placeholder `N.A. — <motivo>` passa | template com `pendente`; regex recusa `<`/`{` após o travessão |
| M5 | MEDIUM | AT-015 | aceite vazio (pasta só com README) | pasta de fixture com ≥ 1 pattern; README pulado declarado |
| M6 | MEDIUM | AT-017 | 2 tabelas com coluna `Papel` | nomear a tabela `Surface (funcional)`; placeholder com os 3 papéis = indeterminado |
| M7 | MEDIUM | ATs de texto | gramática do bloco só em prosa | validador executável do bloco `<<<GOVERNANCA` |
| L1 | LOW | Decision 6 | precedência marcador → linha → bloco não declarada | declarar e testar |
| L2 | LOW | `sdd-fluxo.sh` PARES | `define→governanca` obsoleto | linha "Nesta skill" sem governanca; par fica |
| L3 | LOW | Decision 14 | fixtures só na 1ª instalação | self-test sai 64 nomeando a pasta; doc |
| L4 | LOW | passo 1.5 | pedido direto sem arquivo | entrada vai para arquivo temporário |
| L5 | LOW | AT-018 | exit 2 de conservação sem gatilho natural | sabotagem (cópia alterada) |
| L6 | LOW | AT-020 | "sai 5" não discrimina da v2.3.1 | exigir `governança não rodou` e as 2 saídas |
| L7 | LOW | passo 1.5, AT-002 | 2 cartógrafos em paralelo; `superficies` vazio | despacho sequencial; cabeçalho exige `superficies` |

O tratamento de cada nota está no Advisor Ledger do DESIGN v1.1.
