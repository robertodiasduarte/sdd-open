# REVISÃO DO DESIGN F7_EVIDENCIA — contexto fresco (modo contrato, antes do build)

> Bloco devolvido pelo revisor em contexto fresco (subagente sem a conversa do design), sobre
> `DESIGN_F7_EVIDENCIA.md` v1.0 e `DEFINE_F7_EVIDENCIA.md` v1.1, com a branch em `1c9bbc7` (= `v2.2.7`).
> Logs das sondas em `sdd/reports/evidence/F7_EVIDENCIA/AVAL-DESIGN-*.log`. As decisões sobre cada nota
> estão no Advisor Ledger do DESIGN (v1.1) e no `## Contrato de aceite`.

```text
<<<CONTRATO
VEREDITO: NEEDS_WORK — 2 HIGH, 4 MEDIUM, 8 LOW

Medições (read-only; logs em sdd/reports/evidence/F7_EVIDENCIA/):
- AVAL-DESIGN-suite-base.log: a suíte no piso dá `Ran 514 tests … OK`, [exit=0] — A-001 confirmada.
- AVAL-DESIGN-relatorios-do-open.log: simulando a regra nova de cabeçalho (Result) nos 8 BUILD_REPORT,
  os 8 seguem rc=0 na parte de evidência; só F4/F5/F6 têm `AVALIACAO_<F>_\d{8}.*\.md` (2 cada, nenhum
  ignorado pelo git) e nenhum dos 8 tem declaração → a premissa da AT-011 se sustenta. `report-lint.py
  --pendente <f>` hoje sai 64 (linha de uso).
- AVAL-DESIGN-corpus-shell.log: regra textual refeita: 245 logs, 323 linhas `exit=`, 19 acusações
  (10 tail, 3 cut, 2 tr, 2 sed, 2 head) — a contagem bate com o DEFINE; a classificação não (ajuste 2).
- AVAL-DESIGN-gate-baseline-rc2.log: um gate que quebra (crash, não asserção) faz o `verify-gate.sh`
  atual imprimir `GATE VERMELHO … (rc=2)` e sair 2.
- AVAL-DESIGN-guard-prefixos.log: árvore suja nesta worktree: 23 em sdd/features/, 2 em sdd/handoffs/,
  275 em sdd/reports/ (inclui os 8 BUILD_REPORT, fora de evidence/), 10 em sdd/reviews/.
- tests/test_report_lint.py: 32 testes (14+18), 11 esperam 0; o único que não usa o helper
  (`test_titulos_reais…`, l.217) segue saindo 1 e citando MIG — AT-012 é viável como está.
- `check-versions.py --base v2.2.7 --base-obrigatoria` hoje: VERDE (17 skills; sdd-build 2.2.1,
  sdd-release 2.3.1). Grep de bashismos em sdd/bin/*.sh: nenhum hit. `git config --global`: sem
  core.hooksPath/commit.gpgsign nesta máquina.

AJUSTES (≤5)

1. alvo: AT-017/AT-018 (gate-baseline "avaliou") · classe: estado sem critério (aceite que confunde crash com dente)
   problema: no open o `(rc=N)` ecoado pelo runner é o rc BRUTO do comando (sdd/bin/verify-gate.sh:146-147 e :196),
   não um veredito interno como no privado. Crash também sai 2: `grep` com arquivo ausente, erro de sintaxe do
   `bash -c`, erro de coleta do pytest, `make`. Medido: `grep -q ok arquivo_que_nao_existe.txt` e `if then fi`
   imprimem `(rc=2)` (AVAL-DESIGN-gate-baseline-rc2.log). Com "rc=2 ⇒ avaliou", o script declara "tem dentes"
   exatamente no caso que a Decision 3 diz querer barrar; a A-002 só validou que o eco existe, não o que N significa.
   EARS: When the gate on the base copy exits 2 and its output contains the runner's `🔴 o comando declarou
   VERMELHO` line or an assertion marker of the 5 formats, gate-baseline.sh shall exit 0; If the only red signal
   is `GATE VERMELHO … (rc=N)` with no such line or marker, whatever N, then it shall exit 3 (RESULTADO:
   INCONCLUSIVO) naming the rc.
   como verificar: tests/test_gate_baseline.py — gate de base com `cmd: "grep -q ok nao_existe.txt"`, outro com
   `cmd: "if then fi"` e outro cujo cmd imprime `FAILED (errors=1)` e sai 2 ⇒ exit 3; com `FAILED (failures=1)`
   ou `RESULTADO: VERMELHO` ⇒ exit 0.

2. alvo: AT-020 (corpus) e a Clarification "todas com formatador no último estágio (acerto da regra)" · classe:
   não-verificável (alvo móvel) + premissa falsa
   problema: (a) "exactly 19 on sdd/reports/evidence" inclui evidence/F7_EVIDENCIA/, que cresce durante o build
   (os logs da F7, o corpus-shell.log — se o achado ecoar o comando como `$ …`, o log acusa a si mesmo —, os
   AVAL-DESIGN-*); a contagem deixa de ser estável. (b) Pelo menos 7 dos 19 NÃO gravam o exit do formatador,
   embora a regra textual os acuse: `git diff --stat … | tail -1 && git diff --name-status …` (3×: F4/F5/F6
   escopo.log, o exit é do git diff), F4/AVAL-at020 (termina em `; exit ${x:-0}`), F4/AVAL-at013 (termina em
   `chmod`), F6/check-versions e F4/AVAL-at006 (laço `for … done`). O critério congela uma sobreaproximação
   chamando-a de acerto.
   EARS: When gate-shell-evidencia.sh runs over the *.log of sdd/reports/evidence/ excluding F7_EVIDENCIA/, it
   shall report exactly the 19 file:line listed verbatim in evidence/F7_EVIDENCIA/corpus-shell.log; the
   Clarification shall record that the rule is conservative on compound commands (`&&`, `;`, `for…done`), with the
   count of such cases. When the log is shell-falso-verde.log, it shall print exactly its expected file:line set.
   como verificar: `bash sdd/bin/gate-shell-evidencia.sh $(ls -d sdd/reports/evidence/*/ | grep -v F7_EVIDENCIA) |
   grep -oE '^[^ ]+\.log:[0-9]+' | LC_ALL=C sort | diff - <lista-esperada>` vazio (referência: as 19 linhas de
   AVAL-DESIGN-corpus-shell.log); o teste da fixture compara o conjunto file:line (faz também a sabotagem "tirar
   tail" ficar vermelha com `head` presente).

3. alvo: AT-021/AT-022 (avaliador-guard) e a Clarification do `--permitir sdd/` · classe: efeito não
   observável / estado sem critério
   problema: (a) a Decision 2 grava sdd/traces/<F>.jsonl (não rastreado, "nunca entra em commit") a cada
   execução do gate; o 5a roda antes do 5d; o guard só permite sdd/reports/evidence/ ⇒ num projeto de usuário o
   guard sai 1 em TODO build, mandando commitar o trace (o init não mexe em .gitignore). (b) Aqui `--permitir
   sdd/` libera também sdd/bin/, sdd/templates/, sdd/fixtures/ — justamente o que a F7 entrega sem commit.
   EARS: When the only dirty paths are under sdd/reports/evidence/, sdd/traces/ or a --permitir prefix,
   avaliador-guard.sh shall exit 0; If a modified or untracked path is under sdd/bin/ while only --permitir
   sdd/features/ --permitir sdd/handoffs/ --permitir sdd/reports/ --permitir sdd/reviews/ is given, then it shall
   exit 1 listing it; the F7 dispatch shall use those 4 prefixes, never sdd/.
   como verificar: sandbox — rodar verify-gate.sh (cria sdd/traces/) e depois avaliador-guard.sh ⇒ 0; com
   sdd/bin/x.sh sujo e os 4 --permitir ⇒ 1 com `sdd/bin/x.sh` na saída.

4. alvo: AT-024 (test-baseline, remoção do que sarou) · classe: estado sem critério
   problema: o DEFINE/Decision 6 não definem "execução completa": com `--cmd` rodando um subconjunto, ou rc≠0 que
   só parcialmente casa ids (suíte interrompida), todo id do baseline que não rodou "sarou" e sai do arquivo em
   silêncio — volta como falha nova na volta seguinte, ou some.
   EARS: When test-baseline.sh runs project.test_cmd without --cmd and without --touched and finds no new failure,
   it shall remove each listed id that did not fail and list it; When --cmd is given, or the result is 2 or 3, it
   shall remove nothing and print `⚠️ baseline não podado (execução parcial)`.
   como verificar: baseline com `mod.C.test_b`, `--cmd` que imprime só a falha conhecida `mod.C.test_a` e sai 1 ⇒
   exit 0 e sdd/baselines/tests.txt idêntico (cmp); sem --cmd (test_cmd do config) o mesmo cenário remove test_b.

5. alvo: AT-027 (sdd-release 0a) · classe: estado sem critério (fail-open)
   problema: o DEFINE só dá ação para `--pendente` exit 1 e `gate-shell-evidencia` exit 2. Ficam sem ação: 64
   (base inválida "não avalio"; arquivo ilegível), 127 (script ausente) e 64 do report-lint antigo que não conhece
   --pendente (medido: rc=64) — cenário real, porque o init nunca sobrescreve sdd/bin/* (bin/sdd-open.sh:603 e
   :613-616). Leitura natural: "não deu 1/2" ⇒ seguir.
   EARS: If report-lint.py --pendente or gate-shell-evidencia.sh exits with any code other than 0, then sdd-release
   shall abort 0a citing the exit, and with 64 or 127 shall add "rode o init / atualize sdd/bin";
   tests/test_contrato_build_release.py shall find both commands with "≠ 0" (or the explicit 1/2/64/127 list) in
   0a and in "Gates de ABORTAR".
   como verificar: grep -nE 'report-lint.py --pendente.*(≠ ?0|64)' .agents/skills/sdd-release/SKILL.md e o mesmo
   para gate-shell-evidencia, no teste de contrato.

DEFEITOS DO DESIGN

- HIGH · Decision 3 / A-002: "avaliou quando o rc ecoado em `GATE VERMELHO … (rc=N)` é 2" é premissa falsa — N é o
  rc bruto do comando (verify-gate.sh:146-147, :196) e crash sai 2. Evidência: AVAL-DESIGN-gate-baseline-rc2.log
  (`grep` em arquivo ausente e erro de sintaxe ⇒ `(rc=2)`). O build entregaria "tem dentes" falso. (ajuste 1)
- HIGH · Decision 2 × Decision 5: o trace cria sdd/traces/<F>.jsonl não rastreado em toda execução (DESIGN
  l.120-121) e o guard só permite sdd/reports/evidence/ (l.190); o 5a precede o 5d (sdd-build SKILL.md:140,:162);
  não há .gitignore gerenciado (grep vazio em bin/). Resultado: o guard sai 1 em todo build de usuário e manda
  commitar o trace. (ajuste 3)
- MEDIUM · Clarification do DEFINE (l.122) e AT-020: "todas com o formatador no último estágio (acerto da regra,
  não falso positivo)" é falso para ≥7 dos 19 (comandos compostos: `| tail -1 && git diff`, `; exit ${x:-0}`,
  `for…done`, `chmod` no fim); e o corpus inclui F7_EVIDENCIA, que cresce durante o build.
  Evidência: AVAL-DESIGN-corpus-shell.log + as linhas `$ ` desses logs. (ajuste 2)
- MEDIUM · Clarification do DEFINE (l.127) e Decision 5 (l.204): `--permitir sdd/` libera sdd/bin, sdd/templates e
  sdd/fixtures sem commit — os entregáveis da F7. Evidência: AVAL-DESIGN-guard-prefixos.log. (ajuste 3)
- MEDIUM · Decision 6: "execução completa" indefinida; --cmd parcial ou rc 2/3 podam o baseline. (ajuste 4)
- MEDIUM · Decision 7 (sdd-release 0a.5/0a.7) e o Goal: ação só para exit 1/2; 64/127 ficam fail-open, inclusive no
  upgrade com sdd/bin antigo, que o init não sobrescreve (bin/sdd-open.sh:603, :613-616). Medido: report-lint atual
  responde 64 a --pendente. (ajuste 5)
- LOW · Pattern 2: trace_gravar não confere PRINT_ONLY; o trap entra depois do cd (verify-gate.sh:69) e o --print
  sai com `exit 0` em :119 — depois do trap — então gravaria uma linha (viola AT-014). A guarda
  `[ "$PRINT_ONLY" = 1 ] && return 0` precisa estar no desenho.
- LOW · Decision 8: "MANIFEST.txt ganha 22 linhas", mas a enumeração dá 4 scripts + 1 fragmento + 13 fixtures + 7
  testes = 25. G3 reprovaria se o build seguir o 22.
- LOW · DEFINE Constraints e DESIGN Risks: "sdd-release 275 linhas" — `wc -l` dá 297 (segue longe de 500).
- LOW · Goal de não regressão: "camada de conversa das 15 skills" — `ls .agents/skills` dá 17; AT-029/Success falam 17.
- LOW · Decision 3: o `git commit` da cópia não neutraliza commit.gpgsign / core.hooksPath / init.templateDir
  globais de quem roda — nesses ambientes daria sempre 3. Usar `-c commit.gpgsign=false -c core.hooksPath=/dev/null`
  ou `--no-verify`. (Os testes não pegam: apoio.py zera o config global.)
- LOW · Pattern 3: junta `git diff --name-only` (relativo à raiz) com `git ls-files --others` (relativo ao cwd) —
  precisa de `cd "$(git rev-parse --show-toplevel)"` antes; não está dito.
- LOW · DEFINE × DESIGN: o parágrafo do Verify Gate (DEFINE:144) diz que a suíte cobre "a parte de AT-016 que
  compara com a saída gravada da v2.2.7"; o DESIGN não tem saída gravada no manifest e só compara com v2.2.7 via
  `git show` num log fora do cmd. Dentro do gate, só trace-on × SDD_TRACE=off.
- LOW · Decision 2: o `define` relativo à raiz precisa ser resolvido ANTES do `cd "$REPO_ROOT"` (verify-gate.sh:62
  testa -f relativo ao cwd de quem chamou; :69 troca de pasta); calculado depois, chamado de subpasta, sai errado.
>>>
```
