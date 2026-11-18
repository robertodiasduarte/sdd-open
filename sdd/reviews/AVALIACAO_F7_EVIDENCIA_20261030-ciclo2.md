# AVALIAÇÃO F7_EVIDENCIA — contexto fresco, modo veredito, ciclo 2

> Bloco devolvido pelo avaliador em contexto fresco (subagente sem a conversa do build), sobre o commit
> `bed1f69`, numa worktree destacada. A execução caiu uma vez por erro de conexão (ECONNRESET) e foi
> retomada com o mesmo contexto. Logs das sondas em `sdd/reports/evidence/F7_EVIDENCIA/AVAL2-*.log`
> (copiados da worktree destacada). As decisões sobre cada achado estão no Advisor Ledger do
> `BUILD_REPORT_F7_EVIDENCIA.md`.

```text
<<<AVALIACAO
feature: F7_EVIDENCIA · ciclo: 2 · commit avaliado: bed1f69 (base v2.2.7, ciclo 1 em 514324f)
veredito: NEEDS_WORK

Os 9 achados do ciclo 1 estão fechados nos casos reproduzidos; o Verify Gate sai 0 (publish-gate ci verde, 625
testes OK no piso). Ficam 3 achados MEDIUM novos: uma variante residual da classe do MEDIUM-3 (pacote go que falha
sem `--- FAIL`), o deno real não reconhecido, e uma regressão introduzida pela correção do LOW-2 no comando sugerido
pelo guard. Os 19 AVAL2-*.log passam no próprio gate-shell-evidencia.sh.

Achados do ciclo 1:
| Achado | Estado | Prova |
|---|---|---|
| MEDIUM-1 | FECHADO (444, 555, subpasta de 555; 4 fixtures; byte-idêntico a SDD_TRACE=off) | AVAL2-medium1-trace-nao-gravavel.log |
| MEDIUM-2 | FECHADO (staged, modificado, renomeação, commitado, não rastreado, subpasta; --base inválida 64) | AVAL2-medium2-modo-diff.log |
| MEDIUM-3 | FECHADO para [build failed]/[setup failed]; não fechado para a classe inteira (MEDIUM-A) | AVAL2-at023-025-medium3-low5-test-baseline.log |
| LOW-1 | FECHADO nos casos citados; sobra variante (LOW-D) | AVAL2-at009-low1-veredito.log |
| LOW-2 | FECHADO; a mudança criou o MEDIUM-C | AVAL2-at021-022-low2-guard.log |
| LOW-3 | FECHADO | AVAL2-at026-028-skills-templates.log |
| LOW-4 | N/A, reproduzido em cópia | AVAL2-at030-sabotagem.log |
| LOW-5 | FECHADO (touch RODOU não criou o marcador) | AVAL2-at023-025-…log |
| LOW-6 | FECHADO | AVAL2-at019-low6-casos.log |

Tabela por AT: AT-001 a AT-008, AT-010 a AT-021, AT-025 a AT-030 PASS. AT-009 FAIL parcial (LOW-D).
AT-022 FAIL parcial (MEDIUM-C). AT-023 FAIL parcial (MEDIUM-B). AT-024 PASS com achado MEDIUM-A.
Verify Gate: exit 0 (AVAL2-verify-gate.log, "Ran 625 tests … OK"). AT-016: v2.2.7 × HEAD × HEAD off idênticos nos
8 pares (AVAL2-at016-v227-vs-head.log). AT-020: 21 = 21, conjunto idêntico, e uma reimplementação independente em
Python da regra do DEFINE dá as mesmas 21. AT-030: 6 sabotagens vermelhas e OK depois do checkout.

ACHADOS

MEDIUM-A: test-baseline.sh mascara pacote go que falha SEM linha `--- FAIL` (estouro de -timeout, os.Exit(1) em
TestMain, panic de init: o go imprime só `FAIL\t<pacote>\t<tempo>`). Com uma falha conhecida junto, a execução
completa sai 0 e poda do baseline um id que nem rodou. Reprodução (AVAL2-achado-mascara-falha-de-pacote.log, caso
A): baseline TestConhecido + TestLento; test_cmd imprime `--- FAIL: TestConhecido`, `FAIL exemplo/conta 0.005s`,
`panic: test timed out after 1s`, `running tests:`, `TestLento (1s)`, `FAIL exemplo/lento 1.012s`, `FAIL` e sai 1
⇒ "✅ sarou — removido do baseline: TestLento", VERDE, exit 0. Esperado 2 (ou 3) e nada podado.

MEDIUM-B: test-baseline.sh não reconhece a saída real do deno test: o deno 2.8.2 colore a saída mesmo redirecionada
(`conhecido\033[0m\033[38;5;245m=> ./conta_test.ts:2:6\033[0m`) e o regex não casa ⇒ sempre 3 (INCONCLUSIVO), mesmo
só com falhas conhecidas. Fecha para o lado seguro, mas o formato deno não funciona fora da fixture (A-003). Com
NO_COLOR=1 sai 2 com "nova: conta_test.ts::novo". Conserto sugerido: tirar \x1b\[[0-9;]*m antes dos regex.

MEDIUM-C: o commit sugerido pelo avaliador-guard.sh vira `git add -A --` SEM caminho quando toda a sujeira são
remoções staged (regressão da correção do LOW-2: o caminho removido não está no disco nem no índice). Sem pathspec,
`git add -A` coloca a árvore inteira no stage — sdd/traces/, evidence/, os prefixos --permitir e qualquer não
rastreado. Reprodução: `git rm -q sdd/bin/apagar.sh` com sdd/features/…, evidence/… e sdd/traces/… não rastreados ⇒
o sugerido commita os 4. Conserto: omitir o add quando a lista fica vazia, ou `git add -u -- <caminho>`.

LOW-D: AT-009 — `| Veredito do avaliador | PASS |` (tabela sem (C1) nem dois-pontos) e `**Veredito do avaliador**:
PASS` (dois-pontos fora do negrito) não são reconhecidos; com qualquer AVALIACAO antigo em sdd/reviews/, o relatório
passa com PASS sem citar a avaliação.

LOW-E: gate-shell-evidencia.sh — (a) `$ ` sozinho com o comando na linha seguinte: nada é conferido; (b)
`$ cmd | tail -1 # PIPESTATUS`: o comentário com um espaço só absolve; (c) `$ cmd | (tail -1)` e
`$ cmd | command tail -1` não são acusados. Inverso: `r=$?` antes do pipe é acusado (falso positivo, conforme a
letra do DEFINE).

LOW-F: `verify-gate.sh --sem-define` com o trace não gravável imprime "trace no-define gravado" e não grava nada
(compatível com o AT-014, mas a frase afirma o que não aconteceu).
>>>
```
