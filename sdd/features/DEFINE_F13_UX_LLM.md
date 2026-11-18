# DEFINE: F13 UX e LLM no código

> A UX review ganha veredito por critério WCAG com contraste medido por script; quem constrói software que chama IA ganha a especificação de loop, o roteador loop × prompt no Build, o inventário de prompts com colunas conferidas e o fiscal de prompt fora do inventário.

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | F13_UX_LLM |
| **Date** | 2026-11-04 |
| **Author** | SDD Define by RDD (sessão 10, Roberto Dias Duarte) |
| **Status** | Ready for Design |
| **Clarity Score** | 14/15 |

---

## Problem Statement

No Open, "contraste medido" é regra de texto, sem ferramenta nem veredito por critério; um processo que chama IA em laço vira código sem especificação de parada, orçamento e verificador; e o drift de prompt é um passo escrito, cego a quem chama a IA por uma função própria. O privado já resolve os três, e o Open precisa fazê-lo para substituí-lo na F15.

---

## Target Users

| User | Role | Pain Point |
|---|---|---|
| Quem conduz a UX review de uma feature com tela | roda `sdd-ux-review` | "contraste medido" não tem ferramenta, e a revisão não diz critério a critério o que passou |
| Quem constrói software que chama IA em laço | roda `sdd-design` e `sdd-build` numa feature com prompts de produção | o loop nasce sem regra de parada, orçamento por estágio nem verificador independente; o prompt de cada estágio é improvisado |
| O agente que executa o Build | segue o passo 4 da `sdd-build` | o drift é um critério por leitura: num projeto com wrapper próprio, procurar só as assinaturas do SDK deixa o gate cego |
| O Roberto na F15 | troca o privado pelo Open | precisa destes mecanismos no Open para remover os do privado |

---

## Goals

| Priority | Goal |
|---|---|
| **MUST** | `sdd/bin/contraste.sh`: razão WCAG entre 2 cores, com transparência composta sobre o fundo, truncada em 2 casas, com veredito contra um piso e saídas 0/2/64 (U2) |
| **MUST** | `sdd/bin/prompt-drift-scan.sh`: `--conteudo` avalia antes de gravar, modo de arquivos em disco, `--self-test` autocontido, saídas 0/2/64, sinais ancorados em `prompts.wrapper_pattern` (L4) |
| **MUST** | Skill nova `.agents/skills/sdd-loop-builder/`: LOOP_SPEC v2, perfil por risco, estado de controle, verificador independente, regras de parada, orçamento por estágio e tabela de estágios LLM × código (L1) |
| **MUST** | Roteador no passo 4 da `sdd-build`: `Tipo=loop` gera a LOOP_SPEC e depois um prompt por estágio; não encerrar o turno ao receber o bloco de texto (L2) |
| **MUST** | Fragmento `sdd/templates/fragments/LLM_PROMPTS_DESIGN.md`, colunas no `DESIGN_TEMPLATE.md`, o 5.5 da `sdd-design` e o `design-lint.py` conferindo o inventário (L3) |
| **MUST** | Tabela WCAG 2.2 AA com 7 critérios no `UX_REVIEW_TEMPLATE.md` e na `sdd-ux-review`; cada REPROVA vira 1 MUST com o critério e o par medido (U1) |
| **MUST** | Prova num agente real (Codex CLI): o roteador seguido num DESIGN de exemplo com `Tipo=loop`, depois do último conserto |
| **SHOULD** | `docs/llm-in-code.md` + PT; o roadmap passa a falar só da `sdd-drive`; README com a skill nova; guia de adaptação com o slot |
| **COULD** | Exemplo genérico de LOOP_SPEC em `.agents/skills/sdd-loop-builder/references/`, para quem nunca viu uma |

---

## Success Criteria

- [ ] `contraste.sh '#767676' '#ffffff'` imprime `4.54:1 PASSA` e sai 0; `contraste.sh '#777777' '#ffffff'` imprime `4.47:1 REPROVA` e sai 2; `contraste.sh '#6c7b67' '#ffffff'` (exato 4,4999996) imprime `4.49:1 REPROVA`.
- [ ] `contraste.sh '#000' '#fff' .5` imprime `3.97:1 REPROVA` e sai 2, com o oráculo calculado fora do script.
- [ ] `prompt-drift-scan.sh --self-test` sai 0 numa pasta sem `sdd/fixtures/` nem `sdd/config.yaml`, sem deixar arquivo para trás, e ao menos 1 caso por sinal, por exclusão e por motivo de saída 64.
- [ ] `skill-lint.py .agents/skills/sdd-loop-builder/SKILL.md` sai 0; `skill-lint.py --conversa .agents/skills/sdd-*/SKILL.md` sai 0 nas **18** skills; `sdd-decisoes-lint.sh --sites .agents/skills sdd/templates/fragments` sai 0.
- [ ] Os 2 scripts novos sem achado em `grep -nE 'mapfile|declare -A|\$\{[a-zA-Z_]+\^\^'`; baseline vermelha na `v2.4.0` (os testes novos falham lá); 1 sabotagem por script faz o teste correspondente falhar.
- [ ] 3 execuções reais do Codex CLI, depois do último conserto (AT-021): caminho feliz, skill ausente e linha sem `Tipo`, conferidas por efeito, com 2 controles sem agente que reprovam.
- [ ] `git diff --name-only v2.4.0 HEAD -- sdd/hooks sdd/bin/report-lint.py sdd/bin/verify-gate.sh .agents/skills/sdd-release` vazio.
- [ ] `bash sdd/bin/verify-gate.sh --strict sdd/features/DEFINE_F13_UX_LLM.md` sai 0; `check-versions.py --base v2.4.0 --base-obrigatoria` sai 0; CI verde em `ubuntu-latest` e `macos-latest` dentro dos tetos de 25 e 45 minutos.
- [ ] Revisão adversarial real com `loop` PRONTO e `--conferir` CONFERE no commit final; Release `v2.5.0` por tag, com `SHA256SUMS.txt` conferido.

---

## Acceptance Tests

| ID | Pattern | Criterion (EARS) | Gate (`kind`) |
|---|---|---|---|
| AT-001 | Event-driven | **When** `contraste.sh <fg> <bg>` runs with 2 valid colors (`#rgb` or `#rrggbb`, any case), the first line **shall** be `<N.NN>:1 PASSA (piso <P>:1)` and the exit 0 when the ratio truncated to 2 decimals is at or above the floor (default 4.5), or `<N.NN>:1 REPROVA (piso <P>:1)` and the exit 2 when it is below, and the output **shall** end in `RESULTADO:` plus a `→` line with the fix: `#767676`/`#ffffff` → `4.54:1 PASSA`, `#777777`/`#ffffff` → `4.47:1 REPROVA`, `#71796f`/`#ffffff` (exact 4,50003) → `4.50:1 PASSA` | test |
| AT-002 | Unwanted | **If** the exact ratio is below the floor by less than 0.005, **then** `contraste.sh` **shall** still print the truncated value and `REPROVA`: `#6c7b67`/`#ffffff` (exact 4,4999996) → `4.49:1 REPROVA`, exit 2 | test |
| AT-003 | Event-driven | **When** `contraste.sh <fg> <bg> <alpha>` runs with alpha between 0 and 1, the script **shall** compose the foreground over the background in sRGB before computing the ratio: `#000`/`#fff`/`.5` → `3.97:1 REPROVA`, exit 2; `#000`/`#fff`/`1` → `21.00:1 PASSA`; `#000`/`#fff`/`0` → `1.00:1 REPROVA`, each oracle calculated outside the script | test |
| AT-004 | Event-driven | **When** `contraste.sh` runs with `--piso <N>`, the script **shall** judge against N, in any argument position: `#777777`/`#ffffff`/`--piso 3` → `4.47:1 PASSA`, exit 0 | test |
| AT-005 | Unwanted | **If** `contraste.sh` receives no argument, a number of positional values other than 2 or 3, a color outside the 2 accepted forms (`#zzz`, `#12345`, `rgba(0,0,0,.5)`), an alpha outside 0 to 1, a `--piso` without value, zero, or with more than 2 decimals, or an unknown option, **then** it **shall** print the cause and the fix (for `rgba(...)`, the 3rd-value form; with no argument, the example with quotes and the reason: an unquoted `#` starts a shell comment), `RESULTADO: ERRO DE USO`, print no ratio on stdout and exit 64 | test |
| AT-006 | State-driven | **While** `LC_ALL=pt_BR.UTF-8 awk 'BEGIN{printf "%.1f", .5}'` prints `0,5`, `contraste.sh` **shall** read alpha and floor and print the ratio with a decimal point, with the same results of AT-001 and AT-003; **if** that precondition fails, the test **shall** skip with a visible reason, and **shall not** skip on the macOS job | test |
| AT-007 | Event-driven | **When** `contraste.sh --self-test` runs, it **shall** check the pairs of AT-001 to AT-004 and the invalid inputs of AT-005 against oracles fixed in the script, exit 0 when all match and exit 2 naming the case that failed | test |
| AT-008 | Event-driven | **When** `prompt-drift-scan.sh --conteudo <path>` reads text from stdin with a direct provider SDK call (`messages.create`, `chat.completions`, `responses.create`, `generateContent`), a `system` parameter receiving a literal by `:` or `=`, or a system `role`, also as a YAML list item (`- role: "system"`, `- role: system`) or an attribute (`self.system = "x"`), the script **shall** print the path and the signal, then `RESULTADO: DRIFT`, and exit 2, whether or not the path exists on disk | test |
| AT-009 | Event-driven | **When** the path, relative or absolute (also through a symbolic link to the project), has a directory named `prompts`, in any case, at any depth (`prompts/a.txt` and `x/Prompts/v1/a.ts`), even with a test-like file name (`prompts/test_a.txt`), or a file name with `prompt` in any case and an extension other than `.md`, the script **shall** report DRIFT and exit 2 without depending on the content, in `--conteudo` and on disk | test |
| AT-010 | Event-driven | **When** `prompts.wrapper_pattern` in `sdd/config.yaml` holds an extended regex, the script **shall** report DRIFT and exit 2 for a line where that regex is followed by optional spaces and a literal opened by a backtick, single quote or double quote; with `systemPrompt:` in the slot, ``systemPrompt: `x` `` is DRIFT, and with `callLLM\\(` in the slot (YAML double-quoted), `callLLM("x")` is DRIFT; a slot `a\|b` **shall** apply as a whole; a comment after the closing quote and a CRLF line ending **shall not** become part of the value | test |
| AT-011 | Unwanted | **If** the file is a test (`*.test.*`, `*.spec.*`, `*_test.*`, `*_spec.*`, `test_*`, `*Test.*`, `*Tests.*`, or under `tests/`, `test/`, `spec/` or `__tests__/`, which wins over `prompts`), **or** the wrapper parameter receives an identifier (`systemPrompt: SYSTEM_X`, `callLLM(SYSTEM_X)`), **or** a `.md` file outside `prompts/` only mentions an SDK call, **or** `system` is the end of a longer name (`package-ecosystem: "npm"`, `filesystem: "ext4"`, `operating_system: 'linux'`), **then** the script **shall not** report DRIFT and **shall** exit 0 with `RESULTADO: LIMPO` | test |
| AT-012 | State-driven | **While** `prompts.wrapper_pattern` is empty (also `""  # comment`), or the key or `sdd/config.yaml` is absent, the script **shall** run the generic signals and print on stdout a `⚠️` line saying it looked only for generic signals and how to fill the slot, in both results (`LIMPO` and `DRIFT`) | test |
| AT-013 | Unwanted | **If** the script receives no argument, a path that does not exist, a directory (also with `--conteudo`), an unreadable file, an `sdd/config.yaml` that exists and cannot be read (permission, broken link, folder, FIFO), an invalid or malformed value in `prompts.wrapper_pattern` (invalid alone or composed with the literal; `(` and `[` as test cases), or `--conteudo` with terminal stdin, with nothing on stdin, or without exactly 1 path, or if any content `grep` of the script exits 2, **then** it **shall** print the cause and the fix, `RESULTADO: ERRO DE USO`, **shall not** print `RESULTADO: LIMPO`, and **shall** exit 64 | test |
| AT-014 | Event-driven | **When** `prompt-drift-scan.sh <path...>` runs on existing files, the script **shall** evaluate the file content, name every file with a signal and exit 2 if any has one, or exit 0 with `RESULTADO: LIMPO` | test |
| AT-015 | Event-driven | **When** `prompt-drift-scan.sh --self-test` runs in a folder without `sdd/fixtures/` nor `sdd/config.yaml`, called by a relative or an absolute path, it **shall** build its cases in a `mktemp -d`, cover every signal, exclusion and exit-64 reason (terminal stdin only in `tests/`, which needs a pty), leave no file behind, and exit 0, or exit 2 naming the case that failed | test |
| AT-016 | Unwanted | **If** a DESIGN has the prompt section titled by `LLM_PROMPTS_DESIGN.md` without the `Inventário` subsection (the old `### Inventory` format included), whose first inventory table lacks a column (`Tipo`, `Versão`, `Completeness`, `Refator de?`) or has no data row, a row with `Tipo` other than `one-shot` or `loop`, or a contract block lacking a field (`Autônomo?`, `Verification interna`, `Eval mínimo pré-ship` and, in `Tipo=loop`, `Intenção`, `Perfil de risco dos efeitos`, `Ground truth disponível`), a dash counting as empty, or anything between braces left in an inventory cell or a contract field, or the number of contract blocks differs from the number of inventory rows, **then** `design-lint.py` **shall** exit 1, saying first that the prompt section format changed in v2.5.0, naming each item in one line and pointing to the fragment | test |
| AT-017 | Non-regression | `design-lint.py` **shall continue to** give the same result for a DESIGN without that prompt section, including one whose title only starts the same (`LLM Prompt Injection`, `LLM Prompt-Injection`), proved by inline DESIGNs in `tests/test_design_lint.py` and its existing cases, never by a path under `sdd/features/` | test |
| AT-018 | Event-driven | **When** `sdd/templates/fragments/LLM_PROMPTS_DESIGN.md` is filled in a test DESIGN, `design-lint.py` **shall** exit 0; the fragment **shall** carry the `Tipo` router, the inventory, the contract per prompt, versioning and the Build gate by `Tipo`; `DESIGN_TEMPLATE.md` and the 5.5 of `sdd-design` **shall** point to it, and the 5.5 **shall** forbid calling a builder in the Design phase | test |
| AT-019 | Event-driven | **When** the Build reaches a file of step 4, the text of `sdd-build` **shall**: send a file in the inventory straight to the router by `Tipo` (`one-shot` to the skill of `prompts.builder_skill`; `loop` to `sdd-loop-builder` first and then one prompt per LLM stage, whose files count as inventoried); pass the generated text through `prompt-drift-scan.sh --conteudo` before writing, where exit 2 on an inventoried file is expected and goes on to write; when the loop skill answers "item missing", write nothing for this item and iterate the DESIGN; when it answers "not a loop", change the row to `one-shot`, record it and go on; for a file outside the inventory, scan the content to be written, where exit 2 stops the Build and asks, and exit 0 writes; treat exit 64 as a wrong call, never ignored; print one progress line with the real count of prompts, and **shall** forbid ending the turn after the text block | test |
| AT-020 | Unwanted | **If** an inventory row has no `Tipo`, **then** `sdd-build` **shall** triage by the question "does the process re-prompt the model from its own previous output?", treat doubt as `loop` and record it; **if** `sdd-loop-builder` or the prompt skill is unavailable, **then** it **shall** block the item with a line saying what was left out and ask a `[D2 · muda o produto]` question, never improvising the text | test + smoke |
| AT-021 | Event-driven | **When** `evidence/F13_UX_LLM/codex-roteador.sh` runs `codex exec` in a committed temporary copy, after the last fix, holding a sample DEFINE (with the prompt flag `true`), a sample DESIGN with one `Tipo=loop` row and `sdd/config.yaml`, the check **shall** pass only if: the LOOP_SPEC file carries `<LOOP_SPEC v="2"`; the number of non-empty prompt files equals the `LLM` rows of the stage table in that file; the transcript shows, as executed commands and in this order, the reading of `sdd-loop-builder/SKILL.md`, then of `sdd-prompt-builder`; a shim in the copy records a real `prompt-drift-scan.sh --conteudo` call for each written file, not exiting 64 and made before the file existed; and `git status` lists no other path outside the report. **If** `sdd-loop-builder` is removed from the copy, **then** a 2nd run **shall** leave no prompt file at the destination and end with `[D2 · muda o produto]`. **If** the row has no `Tipo`, **then** a 3rd run **shall** produce the LOOP_SPEC and record the triage. The check **shall** reject 2 controls without an agent: 3 empty files, and filled files with a transcript without the skills | smoke |
| AT-022 | Event-driven | **When** `sdd-loop-builder` is linted, `skill-lint.py` and `skill-lint.py --conversa` **shall** exit 0, with the common block of the conversation layer, `references/como-falar.md` and identity line `v1.0.0`; `tests/test_skill_lint.py` and `tests/test_conversa.py` **shall** count 18 skills | test |
| AT-023 | Event-driven | **When** the caller gives `sdd-loop-builder` a compiled contract (intent, effect risk, literal normative reference, closed decisions, available ground truth), the skill text **shall** require exactly one text block with the LOOP_SPEC v2 for the profile chosen by effect risk (`lite`, `standard`, `high-risk`), the stage table with kind `LLM` or `código`, the list of pending prompts and the Verify Gate or the declared lack of ground truth, and **shall** forbid writing stage prompts | test |
| AT-024 | Unwanted | **If** no LLM output decides a later step, **then** `sdd-loop-builder` **shall** recommend the prompt skill and stop; **if** a contract item is missing, **then** it **shall** ask the caller to complete the DESIGN, never filling it in | test |
| AT-025 | Event-driven | **When** the example in `sdd-loop-builder/references/` is read by the test, it **shall** carry every section its declared profile requires, at least one `LLM` stage and one `código` stage, and the budget per stage | test |
| AT-026 | Event-driven | **When** `sdd-prompt-builder/references/sdd-integration.md` and `sdd/templates/fragments/LLM_PROMPTS_BUILD_REPORT.md` are read, they **shall** name `sdd-loop-builder` for `Tipo=loop`, the scan for the drift, and one report entry for the LOOP_SPEC plus one per stage | test |
| AT-027 | Event-driven | **When** `UX_REVIEW_TEMPLATE.md` is read, its accessibility section **shall** list the 7 criteria with level (1.4.3 AA, 1.4.11 AA, 1.4.1 A, 2.4.7 AA, 4.1.2 A with verdict `PASSA`, `REPROVA` or `N.A.`; 2.1.1 A and 2.5.8 AA inherited), state that 3.3.7 is level A and 2.4.13 is AAA, and its Acceptance notes **shall** carry the 2 inherited lines | test |
| AT-028 | Event-driven | **When** `sdd-ux-review` runs on a feature with a visual surface, its text **shall** require the 7 rows, contrast measured with `sdd/bin/contraste.sh` in each project theme, and 1 MUST per `REPROVA` with the criterion and the measured pair; on a feature without a visual surface, **shall** accept `N.A. — <reason>` in 1 line | test |
| AT-029 | Event-driven | **When** `sdd/config.example.yaml` and the adaptation guides (EN and PT) are read, they **shall** show `prompts.wrapper_pattern` empty by default with a wrapper example, and **shall not** carry `smoke.`, `loop_builder_skill` or the literal `callLLM` outside the example | test |
| AT-030 | Event-driven | **When** `sdd-open.sh init` runs in a new project, and again in an existing one that lacks them, the 2 scripts, the fragment and the skill **shall** be present, without overwriting a file the user already has; **when** `sync --vendors claude` runs with the skill in `.agents/skills/`, its adapter copy **shall** appear; `MANIFEST.txt` **shall** list every new file | test |
| AT-031 | Event-driven | **When** the docs are read, `docs/llm-in-code.md` and its PT version **shall** explain the skill, the router, the inventory, the scan and the `contraste.sh`; the roadmap row (EN and PT) **shall** name only `sdd-drive`, with 3 rows; README (EN and PT) **shall** list `sdd-loop-builder`, and every link **shall** open | test |
| AT-032 | State-driven | **While** the package is built, the new scripts, skill, fragment and docs **shall** contain no RDD-specific term (the recipe of section 8.3 of the plan, without hit outside a generic example the test whitelists), no single-agent tool name (`tests/test_agnostico.py`) and no bash above 3.2 | test |
| AT-033 | Event-driven | **When** the skills touched are released, `sdd-ux-review`, `sdd-build`, `sdd-design` and `sdd-prompt-builder` **shall** bump version and identity line, the version pins in the tests **shall** follow, `check-versions.py --base v2.4.0 --base-obrigatoria` **shall** exit 0, and `tests/test_decisoes_lint.py` **shall** register the measured count | smoke + test |
| AT-034 | Non-regression | Hooks, `report-lint.py`, `verify-gate.sh` and `sdd-release` **shall continue to** be byte-identical to `v2.4.0`, and the suite of F1–F12 **shall continue to** pass, except for assertions this DEFINE changes on purpose (skill count, decision count, roadmap row, versions); the first part is proved in the repository by `git diff --quiet v2.4.0 HEAD -- <those paths>`, with a log, because the gate copy has no `.git` | smoke + test |

---

## Clarifications

### Session 2026-11-04

- [x] (Scope) U3 fora, `smoke.*` e `prompts.loop_builder_skill` não existem, Release `v2.5.0` por tag (brainstorm, perguntas 1 a 3); integrado a Out of Scope e a Constraints.
- [x] (Done signal) `#777777` sobre branco é 4.47, truncado (brainstorm, pergunta 4); AT-001.
- [x] (Done signal) "Caso RGBA" do plano = cor com transparência como 3º valor; `rgba(...)` sai 64 (brainstorm, checkpoint 1); AT-003 e AT-005.
- [x] (Edge cases) Saída 2 no REPROVA e 64 em caminho inexistente, diferente do privado (brainstorm, checkpoint 2); AT-001 e AT-013.
- [x] (Constraints) **Decisão do Define:** o `--self-test` dos 2 scripts monta os próprios casos e serve de fixture (regra 6 do 8.0: "`--self-test` ou fixture"); `sdd/fixtures/` não ganha pasta nova, porque o `init` só a copia na 1ª instalação; `tests/` cobre os 2 lados por fora.
- [x] (Edge cases) **Decisão do Define:** `--conteudo` sem nada na entrada sai 64. Uma entrada vazia num caminho limpo seria `LIMPO` sem ter lido nada, o mesmo defeito do caminho inexistente. Arquivo realmente vazio não precisa de varredura.
- [x] (Edge cases) **Decisão do Define:** os sinais de conteúdo não valem para `.md` fora de `prompts/`, porque documentação cita SDK o tempo todo; template de prompt em `.md` mora em `prompts/` e cai no sinal de caminho (AT-009 e AT-011).
- [x] (Terminology) **Decisão do Define, correção de fato sobre a fonte:** a tabela do privado exige em 1.4.3 "inclusive desabilitado" e em 2.4.7 "anel ≥3:1", o que vai além da WCAG 2.2: 1.4.3 isenta componente inativo, e 2.4.7 só pede foco visível (o 3:1 do anel vem de 1.4.11). O Open fica com o texto da norma, para um REPROVA nunca afirmar uma violação que a norma não define. O privado pode manter o rigor maior no playbook dele, na F15.
- [x] (Data model) **Decisão do Define:** o valor de `prompts.wrapper_pattern` é a expressão do parâmetro do wrapper, e o script acrescenta "seguida de literal"; assim, a exclusão de identificador importado vale para qualquer forma (`systemPrompt:` ou `callLLM\(`). Corrige o exemplo do plano, em que `callLLM\(` sozinho dispararia em toda chamada.
- [x] (Done signal) **Decisão do Define:** o DESIGN de exemplo da prova real (AT-021) é genérico e mora em `evidence/`, fora do commit.
- [x] (UX flow) Interface desta feature: 2 scripts de linha de comando, texto de skill e documentação; sem tela. A UX review roda sobre esse texto, com a tabela WCAG em N.A.
- [x] (Done signal) **Revisão fresca do DESIGN, P1:** o `cmd` do gate fica como o prompt da sessão fixou (RECUSADA a mudança); AT-033 e AT-034 passam a `smoke`, com log no repositório, e o Build não fecha sem esses logs. AT-017 usa DESIGN inline.
- [x] (Done signal) **P2 e P3 aceitas:** a prova real são 3 execuções, com efeito no destino e 2 controles sem agente (AT-021).
- [x] (Edge cases) **P4, P5 e D1 a D16 da revisão** aplicadas nos ATs acima; lista completa no Advisor Ledger do DESIGN.
- [x] (Edge cases) **Avaliador, ciclo 1 (A9):** os sinais genéricos não viam `system="..."` em Python, `role` de sistema, `responses.create` e `generateContent`; entram, e o limite do resto (SDK fora da lista, texto montado por variável) fica documentado. Cabe na entrega L4; a prova é teste.
- [x] (Done signal) **Decisão D4 do Roberto, 2026-11-04, risco aceito:** a conta do Codex ficou sem créditos. O 2º revisor fica dispensado na rodada 5 da revisão real, com o motivo no ledger, e AT-021 fica aceito com a prova real completa em `867d6de` (as 3 execuções deram certo no efeito) e a execução sem a skill em `cdb85a9`; o texto da `sdd-loop-builder` mudou depois de `867d6de` (`726c43c`), sem rodada real sobre ele.
- [x] (Done signal) **Decisões D4 do Roberto, 2026-11-04:** 3º ciclo do avaliador no commit final; com o MEDIUM dele, consertar e rodar a 6ª rodada, sem 4º ciclo. O último veredito do avaliador fica NEEDS_WORK (ciclo 3), com o achado corrigido e conferido pela rodada 6 e pelo gate.
- [x] (governança) Passo 11 rodado com revisor fresco em 2026-11-04: N.A.; fronteira e bloco conferidos.

---

## Verify Gate

```yaml
verify_gate:
  kind: test
  cmd: "T=$(mktemp -d) && git archive HEAD | tar -x -C $T && PUBLISH_GATE_MODE=ci bash scripts/publish-gate.sh $T && cd $T && SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover -s tests -p 'test_*.py'"
  pass_when: "exit 0"
  threshold: "—"
  manual_fallback: "—"
```

---

## Out of Scope

- U3 smoke visual, `smoke.urls_cmd`, `smoke.a11y_cmd` e qualquer passo novo no `sdd-release` (tarefa na F15).
- `prompts.loop_builder_skill`: o nome da skill fica fixo no texto da `sdd-build`.
- Scan no pre-commit, lint de LOOP_SPEC e regra nova no `report-lint` (abordagem B rejeitada).
- `FRAMEWORK_LOOP_ENGINEERING.md` e os números do `fp-eval`.
- Cor no formato `rgba(...)` no `contraste.sh`.
- 3.3.7 e 2.4.13 na tabela WCAG, além da nota de nível.
- Curator, `/drive`, `drive.*`, `sdd/invariants.md` e a revisão focada na fronteira (F14).
- Alterar o sdd-starter ou o repositório privado.

---

## Constraints

| Type | Constraint | Impact |
|---|---|---|
| Technical | Piso bash 3.2, Python 3.9 stdlib, `awk` e `grep` POSIX; sem Node | scripts sem `mapfile`, `declare -A`, `${x^^}`; `awk` com `LC_ALL=C` |
| Technical | Delta-only nas skills existentes (regra 7 do 8.0) | `sdd-build` muda só no passo 4; `sdd-design`, só no 5.5; `sdd-ux-review`, só na acessibilidade |
| Technical | Skill nova e contagens: `test_skill_lint.py` e `test_conversa.py` 17 → 18; bloco comum em 16; `test_decisoes_lint.py` muda | a skill segue a moldura da `sdd-prompt-builder`, sem `### Fluxo encadeado`, que é das 9 de fase |
| Technical | Padrão agnóstico (P2) e regra 10 do 8.0 | a skill não cita ferramenta de um agente só |
| Other | Específico da RDD não viaja (regra 4 do 8.0) | `callLLM` só como exemplo do slot; sem LBI, WARM/COOL, LM-nnn nem `fp-eval` |
| Other | `sdd/features|handoffs|reports|reviews|traces/` nunca entram em commit da branch | o DESIGN de exemplo da prova fica em `evidence/` |
| Other | Push em `main` só com OK citando "sdd-open"; review externo obrigatório | `v2.5.0` com `git push --atomic` |
| Resource | CI: tetos de 25 min (Ubuntu) e 45 min (macOS); hoje 14m27s e 27m58s | testes novos sem rede e sem sandbox por caso quando não precisam |
| Timeline | Uma frente por sessão: do brainstorm à release nesta sessão | a F14 é a sessão 11 |

---

## Technical Context

| Aspect | Value | Notes |
|---|---|---|
| **Deployment Location** | `sdd/bin/`, `.agents/skills/sdd-loop-builder/`, `.agents/skills/sdd-{build,design,ux-review,prompt-builder}/`, `sdd/templates/`, `sdd/config.example.yaml`, `docs/`, `tests/` | pacote; o projeto do usuário recebe pelo `init`/`sync` |
| **KB Domains** | N/A | o pacote não tem `sdd/kb/` próprio |
| **IaC Impact** | None | `release.yml` já publica nos caminhos tocados |
| **LLM Prompts** | false | a skill e o fragmento são instruções do método para um agente de código, não prompt que roda em produção de um produto; nenhum provedor é chamado por código do pacote nesta frente (a prova usa `codex exec`) |
| **CONTEXTO de domínio** | nenhum (pulado: sem `sdd/patterns/dominio.md`) | `contexto-lint.sh --sugerir` respondeu `pular` |
| **Governança** | N.A. — o DEFINE trata contraste WCAG, varredura de drift de prompt e skills de método, sem dinheiro, saldo, lançamento, nota fiscal, tributo, folha nem dado pessoal ("orçamento por estágio" é limite de computação de laço de IA) | revisor fresco, 2026-11-04 |

---

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|---|---|---|---|
| A-001 | O agente segue o roteador escrito no passo 4 | A abordagem A pede trava depois, com o caso concreto | no — AT-021 testa num agente real |
| A-002 | `grep -E` de bash 3.2/BSD e GNU devolvem 2 para expressão inválida, o que permite a saída 64 | O script precisaria de outro jeito de validar a expressão | no — a testar no CI em macOS e Ubuntu |
| A-003 | Comparar a linha inteira basta para o sinal de wrapper; um literal na linha seguinte ao parâmetro não dispara | Prompt em várias linhas passa sem aviso; a limitação vai na documentação | yes — é o comportamento do privado, medido lá |
| A-004 | A suíte com os testes novos cabe nos tetos de 25 e 45 minutos | Ajustar os tetos, como na F12 | no — medida no CI do PR |

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---|---:|---|
| Problem | 3 | dor, afetados e motivo presentes |
| Users | 3 | 4 usuários com dor específica |
| Goals | 3 | MUST, SHOULD e COULD por item do plano |
| Success | 2 | a maioria é número ou saída exata; a prova real depende de julgar o transcript do agente |
| Scope | 3 | cortes confirmados pelo Roberto, com destino |
| **Total** | **14/15** | |

Minimum to proceed: **12/15**.

---

## Open Questions

None - ready for Design.

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | 2026-11-04 | SDD Define by RDD | Initial version |
| 1.7 | 2026-11-04 | avaliador, ciclo 3 | M1 no AT-008 (`AVALIACAO_F13_UX_LLM_20261104-ciclo3.md`) |
| 1.6 | 2026-11-04 | decisão D4 do Roberto | risco aceito em AT-021 e dispensa do 2º revisor na rodada 5 |
| 1.5 | 2026-11-04 | revisão real, rodadas 1 a 3 | leitura parcial da entrada e formas do slot no AT-013; o lint só confere a 1ª tabela e reprova chave sem preencher no AT-016; título que só começa igual fica fora no AT-017; 2.5.8 com as exceções da norma no AT-027 |
| 1.4 | 2026-11-04 | avaliador, ciclo 2 | N1 no AT-013; N2 no AT-021 (`AVALIACAO_F13_UX_LLM_20261104-ciclo2.md`) |
| 1.3 | 2026-11-04 | avaliador, ciclo 1 | A2, A3, A8, A9, L3, L4, L5, L7, L9 nos ATs (`AVALIACAO_F13_UX_LLM_20261104-ciclo1.md`) |
| 1.2 | 2026-11-04 | revisão fresca do DESIGN | P1 em parte; P2 a P5; D1, D2, D3, D5, D6, D7, D8, D11, D12, D16 nos ATs (`REVISAO_DESIGN_F13_UX_LLM_20261104.md`) |
| 1.1 | 2026-11-04 | sdd-ux-review | U1 no AT-001; U2 no AT-012; U3 no AT-005 e AT-013; U4 no AT-016; U6 no AT-019 e AT-020 |

---

## Next Step

Execute o **SDD Design by RDD**.
