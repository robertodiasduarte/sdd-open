# REVISÃO DO DESIGN F9_FLUXO — contexto fresco (modo contrato, antes do build)

> Bloco devolvido pelo revisor em contexto fresco (subagente sem a conversa do design), sobre
> `DESIGN_F9_FLUXO.md` v1.0 e `DEFINE_F9_FLUXO.md` v1.2, com a branch em `7c640eb` (= `v2.2.9`).
> Logs das sondas em `sdd/reports/evidence/F9_FLUXO/AVAL-DESIGN-*.log` (14; o `gate-shell-evidencia.sh`
> sai 0 sobre eles). Guard antes do despacho: `guard-antes-do-avaliador-design.log` (VERDE). As decisões
> sobre cada nota estão no Advisor Ledger do DESIGN (v1.1) e no `## Contrato de aceite`; os 5 ajustes
> foram ACEITOS e aplicados no DEFINE v1.3.

```text
<<<CONTRATO
VEREDITO: NEEDS_WORK — 3 HIGH, 2 MEDIUM, 10 LOW

Medições (todas em sdd/reports/evidence/F9_FLUXO/; as 14 passam no gate-shell-evidencia.sh, exit 0):
- AVAL-DESIGN-fonte-review-design.log — review-design do privado (cópia) sobre os DESIGNs: F1..F8 EXIGIDO com 13/17/4/10/17/7/25/13 arquivos novos (confirma AT-001); DESIGN_F9 = 33 novos + 2 linhas de segurança.
- AVAL-DESIGN-designs-fora-do-archive.log — `git ls-files sdd/features` = 0; cópia por `git archive` tem 0 `DESIGN_F*`; MANIFEST sem linha `sdd/features`.
- AVAL-DESIGN-print-fraco.log — `verify-gate.sh --print` sai 0 com bloco sem kind e sem cmd, e com marcador ativo + cmd vazio; fora de git sai 64.
- AVAL-DESIGN-ledger-vazio.log — Advisor Ledger com 0 linhas de dados em F1..F4 e no F9 (todos EXIGIDO); F5..F8 têm 8/10/14/15.
- AVAL-DESIGN-codex-git.log — `codex exec` 0.163 fora de repo git só roda com `--skip-git-repo-check`; numa cópia `git archive` (sem .git) `verify-gate --print` sai 64.
- AVAL-DESIGN-despachar-mesmo-arquivo.log — `cp X X` no macOS sai 1 ("identical (not copied)"), por caminho igual e relativo×absoluto.
- AVAL-DESIGN-fonte-loop-bordas.log — `loop` da fonte: (A) review inválida (auditor_exit 68) sem os jsonl → 10; (B) só NEEDS_WORK ciclo 1 na rodada 3 = teto → 10; (C) HIGH aberto + PASS_PENDENTE_RECIBO sem recibo → 10.
- AVAL-DESIGN-pinos-versao.log — 5 testes fixam versão de skills que a F9 sobe: test_contrato_build_release.py:36,:75, test_correcoes_w0.py:66,:144, test_matriz_new_session.py:73.
- AVAL-DESIGN-contagem-perguntas.log — com ```markdown abertos e só a linha com **Sua decisão**: .agents/skills = 15 perguntas em 15 arquivos (fora: kb-protocol e as 2 do OK da release); fragments = 1 hoje.
- AVAL-DESIGN-contagem-testes.log — 683 testes · AVAL-DESIGN-skill-lint-conversa.log — 17/17, exit 0 · AVAL-DESIGN-check-versions.log — `--base v2.2.9 --base-obrigatoria` VERDE · AVAL-DESIGN-design-lint.log — DESIGN_F9 válido · AVAL-DESIGN-heredoc-bash32.log — heredoc com aspas + `)` dentro de `$( )` funciona no /bin/bash 3.2.57.

AJUSTES (≤5)
1. AT-013/AT-014/AT-015, Decision 5, Pattern 2 · HIGH / estado que quebra sem critério + contradição DEFINE×DESIGN · (a) `--print` 0 só prova que o bloco existe (sai 0 sem kind/cmd); o `seguir` nunca lê o Status do artefato: DEFINE `Draft`/`Needs Clarification` ou UX_REVIEW `Needs Requirement Iteration` encadeiam; (b) `seguir design … build` não confere a revisão do DESIGN, e o Ledger está vazio em F1..F4 e no F9; (c) `build` não está nas fases do AT-013: `seguir build <DEFINE> release` sairia 64 pelo AT-015, contra o Pattern 2/Decision 5 (PARAR D1). · EARS: Status do artefato da fase (DEFINE para define/governanca; UX_REVIEW para ux-review; DESIGN para design) tem de começar por `Ready for`, senão PARAR; `kind:`/`cmd:` `<vazio>` no `--print` → PARAR; fase design com review-design 0 ou 64 → PARAR sem linha de dados no Advisor Ledger, ou com HIGH cujo veredito não começa por APLICADA/REBATIDA_; `build` válido só com `release`, sempre PARAR D1; L5 e Goal reescritos como "bloco do gate válido". · Verificar: sandbox com git init + config-autonomo: Status Draft → 1; bloco `verify_gate: {nada: 1}` → 1; DESIGN com ≥3 Create e Ledger vazio → 1, com linha HIGH APLICADA → 0; `seguir build D release` → 1 com a frase do D1; sabotagem da checagem do Ledger → teste nomeado vermelho.
2. AT-001 + test_fluxo.ReviewDesign · HIGH / aceite que o gate não executa · os 8 DESIGNs moram em `sdd/features/` (não rastreado); no `git archive` o teste cai ou é pulado (circular). · EARS: o teste do AT-001 roda sobre fixtures rastreadas em `sdd/fixtures/fluxo/` que reproduzem os casos de extração dos 8 manifests (cabeçalho `## N. File Manifest (…)`, `**Create**`, `criar`, `NOVO`, `new`, `Modify` não conta, 2ª coluna com crases), cada uma com contagem conhecida; a verdade F1–F8 fica como evidência em `evidence/F9_FLUXO/review-design-8.log` com `porte=<n> fonte=<n>` por DESIGN; nenhum teste novo pula por arquivo ausente. · Verificar: `git archive HEAD | tar -t | grep -c '^sdd/fixtures/fluxo/DESIGN_'` ≥ 4; `grep -c 'sdd/features' tests/test_fluxo.py` = 0; log das 8 com porte = fonte.
3. AT-030/AT-031, Decision 9 (codex.sh) · HIGH / aceite falso, sem critério de falha · (a) cópia `git archive` sem .git: `codex exec` recusa sem `--skip-git-repo-check` e, com ela, `--print` sai 64 → `seguir` 1 → a linha ✅ nunca aparece; (b) AT-030 espera `seguindo para /sdd-`, mas o AT-013 fixa `seguindo para o DESIGN (…)` + `→ /sdd-design …`; (c) "desvio no BUILD_REPORT" não falha nada; (d) a sdd-define faz perguntas D2 que travam um exec não interativo; (e) com `layers` vazio o 5d é N.A. e o agente pode não chamar `despachar`. · EARS: codex.sh roda `git init -q && git add -A && git commit -q` (identidade example.com) na cópia; para AT-031 grava ≥2 globs em `layers` tocados pela feature de fixture; o prompt manda responder D1–D5 pela recomendada (no log); AT-030 passa sse o log tem `✅ DEFINE pronto → seguindo para ` e `→ /sdd-`; AT-031 sse tem `[exit=40]`, `RESULTADO: AGUARDANDO_HUMANO` e o brief existe; senão FAIL (❌ no BUILD_REPORT). · Verificar: `grep -c 'git init' codex.sh` ≥1; `grep -c 'seguindo para ' codex-define-autonomo.log` ≥1; `grep -c '\[exit=40\]' codex-despacho-40.log` ≥1; `test -f` do brief na cópia, no log.
4. despachar (Decision 4, Pattern 3) + degrau 2 de contexto-fresco.md · MEDIUM / falha de execução no caminho principal · o degrau 2 manda gravar o brief exatamente em `sdd/reports/briefs/BRIEF_avaliador_{F}.md`, que é o destino do `cp`; `cp X X` sai 1, então o despacho natural falha em vez de 40; os testes usam o brief da fixture (outro caminho) e não pegam. · EARS: quando o brief resolve (pwd -P + nome) para o mesmo arquivo do destino, `despachar` pula a cópia, ainda exige brief não vazio, imprime a parada e sai 40; o degrau 2 diz para gravar o brief nesse caminho e passá-lo ao `despachar`. · Verificar: teste com o brief já no destino, relativo e absoluto → 40, `cmp` igual, mtime inalterado.
5. loop, AT-006–AT-009 (Decision 3 "porte linha a linha") · MEDIUM / ATs contradizem a fonte, medido · a fonte sai 10 nos casos A/B/C, os ATs mandam 64 (A), 20 (B) e 30 sem precedência (C). · EARS: precedência 64 > 20 > 10 > 30 > 0; D4 teto só quando o CONTINUAR vem da review (inválida, HIGH aberto ou APLICADA) e a rodada ≥ teto; D4 ciclos só para NEEDS_WORK com ciclo ≥ 2; D5 sobrepõe; com `reviewer_exit`/`auditor_exit` ≠ 0, o loop não lê os jsonl e sai 10 mesmo sem eles. · Verificar: 3 testes reproduzindo A/B/C e um diferencial porte × privado (10/10/10) em `evidence/F9_FLUXO/loop-diferencial.log`.

NOTAS MENORES (LOW)
- O manifest omite pinos de versão: test_contrato_build_release.py:75 (build 2.3.0), test_correcoes_w0.py:66 (iterate 2.1.0) e :144 (build 2.3.0), test_matriz_new_session.py:73 (new-session 1.2.0).
- Motivos do AT-019 ≠ "mesma redação do skill-lint" ("nenhuma opção (recomendado)", "tem a opção **Outro**", "sem a opção **não sei**"); faltam zero recomendadas e "marca fora do lugar".
- Concordância: "GOVERNANÇA pronto", "UX REVIEW pronto" → "pronta".
- Linha 79 do manifest diz 30 novos; são 33.
- "o cmd do gate cobre os outros 31" não vale para `check-versions --base v2.2.9` (AT-028; sem .git na cópia) nem para AT-032 (evidência): declarar como CI/evidência.
- Pattern 1 "Exit 64: repasse a linha ⚠️" — o 64 também sai por argumento ruim/DEFINE ilegível sem ⚠️: "repasse a saída".
- `review-design` acha a raiz por `git -C <pasta do DESIGN>`, `seguir`/`estado` pela pasta atual: unificar.
- O exemplo "Pergunta aberta" do PERGUNTA_DECISAO.md (l. 47) tem **Sua decisão** sem opções; o lint o ignora; o AT-022 tem de dizer se leva marca.
- AT-020 com vários caminhos: "zero perguntas → 64" por caminho ou no total?
- Projeto atualizado: o `init` não copia fixtures novas nem sobrescreve o PERGUNTA_DECISAO.md; `--self-test` sai 64 lá e o item 9 fica velho — registrar em docs/chained-flow.md ou no doctor.
>>>
```
