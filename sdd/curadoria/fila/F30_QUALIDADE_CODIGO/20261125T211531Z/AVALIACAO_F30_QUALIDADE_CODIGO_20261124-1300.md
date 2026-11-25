# AVALIACAO — F30_QUALIDADE_CODIGO (fatia S2) · ciclo 2 · 2026-11-24

> Bloco do avaliador de contexto fresco (subagente novo, modo `veredito`, ciclo 2), sobre `e65531f`. Conteúdo do bloco
> devolvido, com as células condensadas. Logs das sondas em `sdd/reports/evidence/F30_QUALIDADE_CODIGO/AVAL2-S2-*.log`.

<<<AVALIACAO
VEREDITO: PASS_PENDENTE_RECIBO

Os três achados do ciclo 1 (N1, O1, O2) foram reproduzidos e estão corrigidos; os 7 ATs passaram nas sondas. Falta só o recibo do Verify Gate (suíte inteira e publish-gate não rodados, como pedido).

| AT | sonda | esperado | observado | resultado |
|---|---|---|---|---|
| N1 (AT-013) | reprodução exata do ciclo 1, 20 vezes, sem `-B` | rc 0 nas 20 | rc 0 nas 20, árvore igual; o fraco deu 2 | PASS |
| O1, O2 (AT-010) | evidência só na avaliação com antes de outro comando; cabeçalhos `Antes (vermelho)`, `antes`, `Antes — vermelho` | rc 1 | rc 1 | PASS |
| AT-010 | mesmo comando vermelho; ausente; `—`; 126; 127; sem `[exit=`; N.A.; ignorado; kind `cmd`; outra feature | 0 no válido, 1 nos demais | como esperado | PASS |
| AT-011 | continua verde/vermelho/sem antes/outro comando/N.A.; manual-ux com N.A. (motivo) | 0/1/1/1/1; 0 | como esperado | PASS |
| AT-012 | sem a coluna; com a coluna e sem DEFINE | 0 com o aviso; 0 com a causa | como esperado | PASS |
| AT-013 | forte (python3 e /usr/bin/python3), fraco, TMPDIR, TERM no meio, mudança não commitada | 0 com log; 2; cópia apagada; árvore igual | como esperado | PASS |
| AT-014 | trecho ausente/4×; absoluto; `..`; link; não commitado; `--feature ../x`; `--at ../AT`; já falha; 126; 127; 127 só sabotada | 3 ou 64, sem log, árvore igual | como esperado | PASS |
| AT-015 | ordem 4/5/6; textos do build, config, 2 moldes, design, MODO_WEB; `test_f30_textos_s2` sobre `git archive` | presentes; 11 OK | como esperado | PASS |
| AT-016 | check-versions; report-lint nos relatórios da S1, F23B3, F17C, F7 e no atual; módulos S2 sobre `git archive` | 0 | 0 (25, 14 e 11 testes OK) | PASS (recibo da suíte pendente) |

ACHADOS (nenhum bloqueia; todos pedem uma entrada fora do molde)
O-A — uma citação `evidence/FX/../OUT/AT-001.antes.log` passa: `problema_do_log` procura o texto `evidence/{F}/` sem normalizar o `..` (anterior à S2; a coluna Evidência tem a mesma brecha).
O-B — cabeçalho `**Antes**` ou `Antes/vermelho` não é reconhecido: cai no aviso de coluna faltando.
O-C — sem `AT-nnn.log` no disco e com a evidência só na avaliação, o comando do antes não é comparado.
O-D — `N.A.` sem `(<motivo>)` é aceito num AT `manual-ux`.
O-E — um `AT-001.antes.log` que é link simbólico para um log de fora da feature é aceito.
>>>

## Tratamento (build, 2026-11-24)

O-A a O-E ficam como pendência da ficha (candidatos a endurecer o `report-lint.py` numa fatia seguinte): exigem que quem
escreve o relatório monte uma citação fora do molde, e o O-A é anterior à S2 e vale para a coluna Evidência inteira —
consertar só a coluna `Antes` deixaria as duas regras diferentes. O recibo é o Verify Gate no commit que sobe.
