# AVALIAÇÃO F7_EVIDENCIA — contexto fresco, modo veredito, ciclo 1

> Bloco devolvido pelo avaliador em contexto fresco (subagente sem a conversa do build), sobre o commit
> `514324f`, numa worktree destacada. Logs das sondas em `sdd/reports/evidence/F7_EVIDENCIA/AVAL-*.log`
> (copiados da worktree destacada). As decisões sobre cada achado estão no Advisor Ledger do
> `BUILD_REPORT_F7_EVIDENCIA.md`.

```text
<<<AVALIACAO
modo: veredito · ciclo: 1 · feature: F7_EVIDENCIA · commit avaliado: 514324f (worktree destacada) · data: 2026-10-30

VEREDITO: NEEDS_WORK

Comportamento central provado: Verify Gate 0 (619 testes, 0 falha; publish-gate ci G1–G5 verde), os 4 gates
novos, o trace e o lint fail-closed se comportam como o contrato pede. Um AT falha objetivamente (AT-014: trace
não gravável muda a saída), dois ficam parciais por regra nova sem o seu "por quê" (AT-026, AT-027), e o AT-009
é parcial na regra de "mesma unidade". Há ainda 2 achados MEDIUM de fail-open fora do texto literal dos ATs.

Todas as sondas rodaram em repositórios temporários (mktemp) ou cópia por git archive; a worktree avaliada ficou
intacta (git status: só os 4 sdd/ não rastreados; sdd/traces/ não existe). Os 34 logs de F7_EVIDENCIA passam no
próprio gate-shell-evidencia.sh (0 acusação).

| AT | sonda | esperado | observado | resultado |
|---|---|---|---|---|
| AT-001 | cabeçalho OK/Prova e relatório sem tabela | 1 nomeando a tabela | 1, `🛑 [tabela] nenhuma tabela de critérios reconhecida…` | PASS |
| AT-002 | ID/Criterion/Result/Evidence com true sem evidência; depois com log válido | confere as linhas | 1 / 0 | PASS |
| AT-003 | fixture sem_avaliacao; declaração só em bloco cercado; AVALIACAO vazio; de outra feature / sem data | 1 "avaliação ausente" + 3 saídas | 1 nos 4 casos, saídas (1)(2)(3) | PASS |
| AT-004 | AVALIACAO não citado; N.A. sem layers / sem DESIGN / sem manifest; manifest 1 camada | 0, com ⚠️ e causa quando não dá para contar | 0; ⚠️ com a causa certa em cada caso | PASS |
| AT-005 | 2 camadas N=2; N=3; N=abc e N=0 (⚠️ e 2); N=1 com 1 camada; fallback _S1 | 1 / 0 / 1 com ⚠️ / 1 | conforme, com contagem e nomes `(api, ui)` | PASS |
| AT-006 | N.A. e PENDENTE sem motivo, PENDENTE () | 1 nomeando a linha | 1, `sem motivo (linha 5)` | PASS |
| AT-007 | pendente no modo comum; --pendente 1 e vários; em bloco cercado; sem arg; ilegível | 0 ⚠️; 1 arq:linha; 0; 64; 64 | conforme | PASS |
| AT-008 | log ignorado (.gitignore, info/exclude); AVALIACAO ignorado; fora de git; git fora do PATH | 1 com conserto; ⚠️ persistência não conferida | conforme | PASS |
| AT-009 | inline, título+parágrafo, tabela, bloco cercado, PENDENTE/N.A. como declaração | AVALIACAO na mesma unidade | inline e título conferem; na tabela, AVALIACAO em outra linha da mesma tabela basta; `Veredito do avaliador: PASS` sem (C1)/negrito e `## Veredito do avaliador` sem (C1) não são reconhecidos | PARCIAL (LOW-1) |
| AT-010 | --stdin inválido/válido; disco válido com stdin inválido; nome inválido | segue o stdin, mesmo exit | 1 / 0 / 1 / 64 | PASS |
| AT-011 | os 8 BUILD_REPORT | 1 em F1 F2 F3 M1 W0 só "avaliação ausente"; 0 em F4 F5 F6 | idêntico | PASS |
| AT-012 | 32 testes atuais; testes da v2.2.7 contra o lint novo | só a forma mínima muda | 32 OK; na v2.2.7, 10 falham todas por [avaliação ausente]/[tabela]; diff só nos 2 helpers | PASS |
| AT-013 | exits 0, 2, 2, 3, 4, 64, 5, 64; JSON; --strict; subpasta; --trace | 1 linha/execução, exit antes do remapeamento | conforme | PASS |
| AT-014 | --print; SDD_TRACE=off; pai sem escrita; dir 555; arquivo 444 | nenhuma linha, mesmo exit e saída | exit igual; stderr ganha `verify-gate.sh: line 72: …/X.jsonl: Permission denied` | FAIL (MEDIUM-1) |
| AT-015 | --sem-define F9_X; sem F; com SDD_TRACE=off | linha release/no-define e 0; 64 sem F | conforme | PASS |
| AT-016 | 4 fixtures: on × off × v2.2.7; --strict | idênticos; 3/4/5 → 1 | idênticos | PASS |
| AT-017 | teste novo sobreposto contra base com o bug; comando que declara VERMELHO; BASELINE-gate.log | 0, log com `$ ` | conforme | PASS |
| AT-018 | base passa; ImportError, sintaxe, exit 2 cru, arquivo ausente, manual-ux, clarificação, sem kind; ref inexistente; 5 usos | 2 / 3 / 3 / 64 | conforme; build intacto | PASS |
| AT-019 | fixture falso-verde + casos próprios (tail, sed, wc, /usr/bin/tail, uniq, tee) | 2 com o conjunto exato | `:3 :6 :9 :12 :15 :17` e os 6 casos | PASS |
| AT-020 | honesto e assertivo; corpus sem F7; --base inválida | 0; exatamente 22; 64 | 0; 22 em 245 logs, diff vazio; 64 | PASS |
| AT-021 | limpa; logo após o trace; evidence/; --permitir sdd/reviews/ | 0 | 0 nos 4 casos | PASS |
| AT-022 | sdd/bin/x.sh com 4 prefixos; staged/untracked/apagado/renomeado/espaço; fora de git; .git quebrado; off | 1 com cada caminho, os 2 lados e o commit; 2; 0 ⚠️ | conforme, mas o commit sugerido falha com renomeação (LOW-2) | PASS |
| AT-023 | 6 fixtures (5 formatos) + saídas REAIS de unittest 3.9, 3.13 e deno 2 | 2 só com a nova; 0 com conhecidas | conforme em todas | PASS |
| AT-024 | poda completa (comentário fica); --cmd, resultado 2, resultado 3 byte-idêntico; --touched; --aceitar | conforme | conforme; --aceitar idempotente | PASS |
| AT-025 | rc 139 sem falha reconhecida; comando ausente; test_cmd vazio/sem config | 3; 0 PULADO | conforme | PASS |
| AT-026 | testes de contrato + grep na sdd-build 2.3.0 | regras nos passos; 1 "por quê" por regra nova | a regra nova da flag LLM Prompts (passo 1) não tem "por quê" | PARCIAL (LOW-3) |
| AT-027 | sdd-release 2.4.0 | --pendente e gate-shell ≠ 0; --sem-define; "por quê"; bloco do OK intacto | tudo presente; --sem-define sem "por quê" | PARCIAL (LOW-3) |
| AT-028 | EVIDENCIA, template, fragmento LLM, config | receita, forma mínima, 3 formas, reprova, check-ignore; PENDENTE; 5 partes; slot | conforme | PASS |
| AT-029 | suíte 619 OK, agnóstico, skill-lint 17, playbook-lint --self-test, publish-gate ci, roadmap, MANIFEST, check-versions | 0 | todos 0 | PASS |
| AT-030 | sabotagens do build + 20 independentes em cópia | vermelho → verde | build 6/6; independentes 19 pegas, 1 não (LOW-5); sabotagem.log não existe (LOW-4) | PASS (comportamento) |

ACHADOS

MEDIUM-1: AT-014 — trace não gravável muda a saída do verify-gate.sh. Reprodução: sdd/traces/X.jsonl com chmod 444
(ou SDD_TRACE_DIR em dir 555) ⇒ stderr ganha `verify-gate.sh: line 72: sdd/traces/X.jsonl: Permission denied`; com
SDD_TRACE=off não. Causa: em `printf … >> "${arquivo}" 2>/dev/null`, a falha do `>>` é impressa antes de o
2>/dev/null valer. Conserto: `{ printf …; } 2>/dev/null >> …` ou 2>/dev/null antes do >>.

MEDIUM-2: o modo diff do gate-shell-evidencia.sh (a chamada da release 0a) não vê log staged nem log rastreado
modificado e não commitado: só entram `git diff BASE...HEAD` e `ls-files --others`. Reprodução: base b; um log novo
com `$ y | head -1` / `[exit=0]` só com git add ⇒ sai 0, "nenhum *.log no escopo". Idem para log rastreado
modificado sem commit.

MEDIUM-3: test-baseline.sh — pacote Go que não compila é mascarado por uma falha conhecida em outro pacote e a
execução completa poda o baseline. Reprodução: test_cmd imprime `--- FAIL: TestConhecido` e
`FAIL\texemplo/outro [build failed]` e sai 1; com baseline TestConhecido + TestOutroConhecido ⇒ 0 VERDE e remove
TestOutroConhecido ("sarou"), que nem rodou. Sugestão: tratar [build failed]/[setup failed] como inconclusivo, ou
não podar quando rc≠0 e o comando acusa algo fora dos ids.

LOW-1: AT-009 — `Veredito do avaliador: PASS` (sem (C1), sem negrito) e `## Veredito do avaliador` (sem (C1)) não
são reconhecidos; na forma de tabela a unidade é a tabela inteira, não a linha.

LOW-2: o commit que o avaliador-guard.sh sugere falha com renomeação staged: `git add -- 'a.txt' 'b.txt'` ⇒ 128
(pathspec 'a.txt' did not match). Conserto: `git add -A -- <caminhos>`.

LOW-3: AT-026/AT-027 — falta "por quê" para a coerência da flag LLM Prompts (passo 1 da sdd-build) e para o
verify-gate.sh --sem-define (0a da sdd-release).

LOW-4: AT-030 cita evidence/F7_EVIDENCIA/sabotagem.log, que não existe na cópia avaliada; o script do build, rodado
em cópia, deu 6/6.

LOW-5: os testes não pegam `--aceitar` rodando o test_cmd sem imprimir nada (sabotagem independente verde).
Sugestão: test_cmd que grava um marcador e afirmar que o marcador não existe.

LOW-6: bordas do gate-shell-evidencia.sh: `$ cmd | LC_ALL=C sort` e `$ cmd |& tail -1` seguidos de `[exit=0]` não
são acusados; `[exit= ]` não é tratado como vazio; `cmd | tail; echo ${PIPESTATUS[0]}` (honesto no bash) é acusado.

NAO_VERIFICADO: nenhum AT. Release v2.2.8 e CI do PR (ubuntu, macOS) são critérios de sucesso, não ATs.
>>>
```
