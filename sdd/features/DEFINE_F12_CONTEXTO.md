# DEFINE: F12 Contexto, patterns e governança

> O Define ganha um cartógrafo fresco que mapeia o domínio no código antes da spec (Step 1.5) e a revisão de governança obrigatória e fail-closed (Step 6.5); o Design ganha contexto por domínio, patterns citáveis e verificáveis, ADR como contrato de máquina, a ficha inteira da landmine e a trava do papel de surface indeterminado.

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | F12_CONTEXTO |
| **Date** | 2026-11-03 |
| **Author** | SDD Define by RDD (sessão 9, Roberto Dias Duarte) |
| **Status** | Ready for Design |
| **Clarity Score** | 14/15 |

---

## Problem Statement

O Define do Open nasce sem saber que regras já vigoram no código do domínio que a feature toca (a W0 tirou do template o "CONTEXTO de domínio" que nada preenchia), e a revisão de governança é uma skill avulsa que ninguém é obrigado a rodar: um DEFINE de sistema financeiro chega ao Build sem ela e o gate nada diz (fail-open, contra a regra 5 do plano). O Design, por sua vez, não tem patterns citáveis com data de validação, lê só o gancho da landmine e não trava quando o papel de uma surface ficou indefinido. O SDD privado já tem tudo isso (`define.md` Steps 1.5 e 6.5, 4 scripts); a F15 só desliga o privado quando o Open fizer o mesmo.

---

## Target Users

| User | Role | Pain Point |
|---|---|---|
| Quem conduz uma feature no Open (aluno contador, Roberto) | roda `sdd-define` e `sdd-design` | o DEFINE ignora regras já vigentes no código; uma lacuna de governança esquecida só aparece depois do build, quando custa migração |
| O agente que escreve o Design | lê o DEFINE e escreve o DESIGN | sem contexto do domínio nem pattern com data de validação; landmine lida só pelo gancho do índice; decide sozinho o papel de uma surface que a UX deixou em aberto |
| Quem adota o Open em agente sem subagente (Codex, Gemini, Cursor…) | segue as mesmas skills | o despacho do cartógrafo e do revisor precisa parar com instrução clara (⏸️, exit 40), não quebrar nem pular a revisão |
| O Roberto na F15 | troca o privado pelo Open | precisa do cartógrafo, do revisor, da fronteira e dos lints no Open para remover `.claude/commands/workflow/` e `scripts/` do privado |

---

## Goals

| Priority | Goal |
|---|---|
| **MUST** | `sdd/bin/contexto-lint.sh` portado (lint, `--validade`, `--sugerir`, `--self-test`) com seções genéricas, camadas de `layers:` e mapa de domínios em `sdd/patterns/dominio.md` |
| **MUST** | `sdd/bin/governanca-fronteira.sh` portado (snapshot sha256 + comparar) e usado pelos **dois** agentes frescos, cartógrafo e revisor (decisão 8 do brainstorm) |
| **MUST** | `sdd-define` Step 1.5 (cartógrafo: gerar/reusar/pular, ≤ 2 domínios, despacho pela escada, 1 redespacho, não trava) + brief `sdd-define/references/cartografo.md` |
| **MUST** | `sdd-define` Step 6.5 (governança sempre, inclusive com `--parar`; N.A. registrado; marcador gravado antes do despacho; 1 redespacho; 2ª falha mantém o marcador) + brief `sdd-governanca/references/revisor.md`; o `prova_script` é gravado e ligado ao `cmd` no Step 6.5 (D8) |
| **MUST** | `verify-gate.sh`: DEFINE sem a linha `Governança` válida ⇒ exit 5, com as 2 saídas na mensagem; `DEFINE_TEMPLATE.md` com as linhas `CONTEXTO de domínio` e `Governança` |
| **MUST** | `sdd/bin/patterns-lint.sh` portado (lint de pasta, `--design`, `--self-test`) + `sdd/patterns/README.md` (formato dos patterns e do `dominio.md`); `sdd-design` cita `§Esqueleto (validado_em …)` e roda `--design` |
| **MUST** | `sdd-design`: lê o CONTEXTO (C2), títulos de ADR como contrato (C4), abre a ficha inteira da landmine (C10), papel de surface indeterminado trava (C11) |
| **MUST** | `sdd-fluxo.sh despachar` com os papéis `cartografo` e `revisor-governanca`, e a prova dos dois despachos no Codex CLI (exit 40, brief gravado) |
| **SHOULD** | `sdd/bin/docs-extract-decisions.sh` (C4) gera `docs/adr/index.md` com órfãos e conservação, sob demanda |
| **SHOULD** | `sdd/WORKFLOW_CONTRACTS.yaml` reduzido (C9), conferido por teste contra scripts e briefs |
| **SHOULD** | Docs: `docs/context-and-governance.md` + PT; a linha "Context and governance" sai do roadmap EN/PT; README com o fluxo novo |
| **COULD** | `contexto-lint.sh --sugerir` imprime também os termos que casaram, para o aluno ver por que um domínio foi escolhido |

---

## Success Criteria

- [ ] `contexto-lint.sh --self-test` e `patterns-lint.sh --self-test` saem 0, com ≥ 1 fixture vermelha por classe de erro (7 classes no `contexto-lint`, 5 no `patterns-lint`) rodada antes das verdes, e o teste exige a classe certa, não só exit ≠ 0.
- [ ] DEFINE sem a linha `Governança` (ou com valor fora de `N.A. —`, `GOVERNANCA_REVIEW_`, `dispensada —`) ⇒ `verify-gate.sh` exit 5 com as 2 saídas; com `--strict`, exit 1.
- [ ] `governanca-fronteira.sh --comparar` sai 1 com `FORA:` em 4 casos de fixture (arquivo novo fora do permitido; sobrescrita de arquivo já sujo; arquivo apagado; nome com acento) e 0 quando só o permitido mudou.
- [ ] Despacho do cartógrafo e do revisor provados no Codex CLI: 2 logs com `[exit=40]` (ou `exited 40`), `RESULTADO: AGUARDANDO_HUMANO` e o brief existente na cópia; no do revisor, o DEFINE da cópia tem o marcador e `verify-gate.sh` sai 5.
- [ ] Todo script novo: `grep -nE 'mapfile|declare -A|\$\{[a-zA-Z_]+\^\^'` sem achado; baseline vermelha na `v2.3.1` (os testes novos falham lá); 1 sabotagem por script (a sabotagem faz o teste correspondente falhar).
- [ ] `skill-lint.py --conversa` 0 nas 17 skills; `sdd-decisoes-lint.sh --sites` 0 com a contagem nova registrada em `tests/test_decisoes_lint.py`; `check-versions.py --base v2.3.1 --base-obrigatoria` 0.
- [ ] Suíte inteira no piso: o job `testes` cabe sob 25 min e `testes-macos` sob 30 min no CI (medir; F11: 12m53s e 17m31s).
- [ ] Revisão de contexto fresco do build sem HIGH aberto; revisão adversarial real `loop` PRONTO e `--conferir` CONFERE no commit final.
- [ ] Release `v2.4.0` por tag com `SHA256SUMS.txt` conferido por `shasum -a 256 -c`.

---

## Acceptance Tests

| ID | Pattern | Criterion (EARS) | Gate (`kind`) |
|---|---|---|---|
| AT-001 | Event-driven | **When** `contexto-lint.sh <arquivo.md \| dir>` runs, it **shall** check the CONTEXTO (header keys `ctx`, `gerado_em`, `sha`, `superficies`, `sup` in this order; the generic sections in order; every `arquivo:linha` exists and the line is within the file; every `LM-nnn` exists in `sdd/playbook.md`; the `ctx:` exists in `sdd/patterns/dominio.md`; `sup:` has ≥ 1 term) and exit 0, or exit 2 printing, per finding, `🛑 [<classe>] <arquivo>: <explicação em palavras>` and, at the end, `RESULTADO:` with the `→ <conserto>` of the first class (UX U7), with one of the stable classes `cabecalho-ausente`, `secao-ausente`, `secao-fora-de-ordem`, `path-morto`, `sup-ausente`, `ctx-desconhecido`, `lm-morto`; with no argument it **shall** exit 64 | test |
| AT-002 | Event-driven | **When** `contexto-lint.sh --validade <arquivo> [--ref <ref>]` runs, it **shall** exit 0 `CONTEXTO VALIDO` iff `git diff --quiet <sha>..<ref> -- <superficies>`, 1 `CONTEXTO VENCIDO` listing the changed files, 2 `sha-inexistente`; the default `<ref>` **shall** be `origin/<default_branch>` when it resolves, else `<default_branch>` (`project.default_branch` of `sdd/config.yaml`, `main` when absent) | test |
| AT-003 | Event-driven | **When** `contexto-lint.sh --sugerir <input.md>` runs, it **shall** print the `ctx:` candidates of `sdd/patterns/dominio.md` with ≥ 2 terms in the input (at most 2, the largest counts), the layers of `layers:` the input names, the state of `sdd/contexto/<slug>.md` (`ausente`, `valido`, `vencido`) and exactly one line `recomendacao: gerar\|reusar\|pular (<motivo>)`; **if** `sdd/patterns/dominio.md` does not exist, **then** it **shall** print `recomendacao: pular (sem sdd/patterns/dominio.md)` and exit 0 | test |
| AT-004 | Unwanted | **If** a red fixture of `contexto-lint.sh --self-test` or `patterns-lint.sh --self-test` passes, or fails with a class other than the expected one, **then** the self-test **shall** exit 2 naming the fixture; every red fixture **shall** run before the greens | test |
| AT-005 | Event-driven | **When** `governanca-fronteira.sh --snapshot <worktree> <saida> [incluir…]` and then `--comparar <antes> <depois> <permitido…>` run, it **shall** print `MUDOU: <path>` for each changed permitted path and `FORA: <path>` for every other new, removed or content-changed path (sha256), including an overwrite of a file already dirty before the snapshot, a new file inside a directory with no tracked file, a file inside an ignored directory under `sdd/`, a deleted file and a name with non-ASCII bytes (enumeration by `git status --porcelain -z --untracked-files=all --ignored=traditional`), a commit made by the agent during the dispatch, a link created on the permitted path, and comparing absolute paths resolved at snapshot time, and exit 0 only when there is no `FORA:` | test |
| AT-006 | Unwanted | **If** the snapshot path is inside the worktree, a snapshot file is missing or unreadable, a file cannot be hashed, or the arguments are wrong, **then** `governanca-fronteira.sh` **shall** exit 64 — an unverified boundary never counts as "nothing changed" | test |
| AT-007 | Event-driven | **When** `sdd-fluxo.sh despachar cartografo <F> <brief>` or `despachar revisor-governanca <F> <brief>` runs, it **shall** copy the brief to `sdd/reports/briefs/BRIEF_<papel>_<F>.md`, print the ⏸️ stop with role-specific text (UX U2: the cartographer reads the domain code and nothing was written to `sdd/contexto/`; the reviewer reads the DEFINE, the report was not written and the DEFINE stays marked pending) naming the return block of that role (`<<<CONTEXTO` … `>>>` or `<<<GOVERNANCA` … `>>>`) and exit 40 `AGUARDANDO_HUMANO`; the other roles **shall continue to** print what they print today | test |
| AT-008 | Event-driven | **When** `sdd-define` reaches Step 1.5, the skill **shall** run `contexto-lint.sh --sugerir`, apply the recommendation as an `[auto · de rotina]` decision, and: on `gerar`, take the snapshot, dispatch the cartographer with only the 4 fields of `references/cartografo.md` (`ctx`, `saida`, `worktree`, `dominio`) through the escalation ladder, compare the boundary allowing only `sdd/contexto/<slug>.md`, run `contexto-lint.sh` on it, redispatch once on failure and, on a 2nd failure, write `nenhum (<motivo>)` and go on; on `reusar`, run `--validade` and offer `gerar` when expired; on `pular`, write `nenhum (pulado: <motivo>)` and tell the student, in one line, that the Define goes on and where to read how to create the map (UX U3); before each dispatch, print the 🗺️ start line (UX U8); at most 2 domains per feature; the result **shall** fill the `CONTEXTO de domínio` row (`contexto/<slug>.md · sha <7 hex> · válido em <data>` or `nenhum (<motivo>)`) (verified on the text of `SKILL.md` and of the brief) | test |
| AT-009 | Event-driven | **When** `sdd-define` reaches step 11 (Governança, the PORTE's Step 6.5) — always, also with `--parar` —, the skill **shall** write the governance marker (colchete + `NEEDS CLARIFICATION` + `governança não rodou`, the canonical form of `fragments/CLARIFY.md`) and the table row `| **Governança** | pendente | … |` into the DEFINE **before** dispatching, keep a byte copy of the DEFINE, take the snapshot, dispatch the reviewer with only the 5 fields of `sdd-governanca/references/revisor.md` (`define`, `skill`, `padrao`, `worktree`, `saida`), compare the boundary allowing only the report, check the `<<<GOVERNANCA` block with `sdd/bin/governanca-bloco.py`, restore the DEFINE from the copy (`cp` + `cmp`) when the boundary reports it, redispatch once on failure, and on `NA` or `REVISADO` replace the marker by the final `Governança` row; before each dispatch print the ⚖️ start line and, when both stops will happen in an agent without fresh session, `parada i de 2` (UX U2, U8); on a 2nd failure the marker **shall** stay and the 🛑 message **shall** state the consequence (build and release stop), never suggest rerunning the whole Define, and give the 2 ways out (UX U4) (run only step 11 of `sdd-define` in a new session; or dispense with the table row `| **Governança** | dispensada — <motivo> | … |` **and** the marker replaced); every form of the `Governança` line in the skill **shall** be the table row (verified on the text of `SKILL.md`) | test |
| AT-010 | Event-driven | **When** the reviewer returns `REVISADO` with gaps, the step 11 **shall** ask one `[D2 · muda o produto]` question per gap (apply · refuse with reason · defer), and on "apply" **shall** write the new AT, adapt the gap's `prova_script` to `sdd/tests/governanca/<F>_<Gnn>.sql` and append `psql -v ON_ERROR_STOP=1 -f …` to the existing `verify_gate` `cmd`, or, when the project only has the production database, record that and use the `prova_manual` (D8); the brief **shall** say the Design only lists the file in the manifest (verified on the text) | test |
| AT-011 | Unwanted | **If** the reviewer returns `PADRAO_AUSENTE` (gatilho found and no `sdd/GOVERNANCA_PADRAO.md`), **then** the step 11 **shall** say in one sentence what the review found and that the standard is asked once per project, ask the 5 fields of the project standard with the `[D2 · muda o produto]` mark (UX U5), write the file and redispatch, without counting a failure; the 5 questions **shall not** be asked of a project whose review is `N.A.` (verified on the text) | test |
| AT-012 | Unwanted | **If** a DEFINE has an active marker containing `governança não rodou`, or no `Governança` row in `## Technical Context` outside code fences, or a row whose value does not start with `N.A. —`, `GOVERNANCA_REVIEW_` or `dispensada —` followed by something other than `<` or `{` (a template placeholder), **then** `verify-gate.sh` (without `--print`) **shall** exit 5, print `GOVERNANÇA NÃO REVISADA`, the value it found (or `ausente`), that since v2.4.0 every DEFINE goes through the governance review once, the 2 numbered ways out with the exact dispense row, and end in `RESULTADO: CLARIFICAR` with its own `→` (run step 11 or dispense; build and release stay stopped) — the `→` of the ambiguity marker **shall continue to** be the current one (UX U1); with `--strict` it **shall** exit 1 | test |
| AT-013 | Non-regression | `verify-gate.sh` **shall continue to** keep the exits 0/2/3/4/5/64, `--print` (exempt from both exit-5 checks), `--sem-define` and the trace, checking in this order: marker → `Governança` row → gate block; every DEFINE that carries a valid `Governança` row — the 7 fixtures and the DEFINEs built inline by `tests/test_verify_gate.py`, `test_gate_baseline.py` and `test_verify_gate_trace.py` — **shall** keep its exit | test |
| AT-014 | Event-driven | **When** `patterns-lint.sh <dir>` runs, it **shall** check each pattern (sections in order, `arquivo:linha` existing, `LM-nnn` alive, `validado_em` readable) and exit 0 or 2 with one of `secao-ausente`, `secao-fora-de-ordem`, `path-morto`, `lm-morto`, `validado-vencido`, age only warning; **when** `--design <DESIGN.md> [<dir>]` runs, age past the limit and dead path **shall** block (exit 2) only for patterns cited in the DESIGN, the message saying the validation date, the age in days and the limit (UX U10), the same defects in uncited patterns **shall** warn, and a DESIGN that cites none **shall** warn and exit 0; no argument ⇒ 64 | test |
| AT-015 | Event-driven | **When** `sdd/patterns/README.md` is read, it **shall** describe the pattern sections, the citation form `§Esqueleto (validado_em AAAA-MM-DD)`, the age limit, and the `dominio.md` format (`### ctx:<slug>` blocks with anchors and a `sup:` line); `patterns-lint.sh` **shall** skip `README.md`, exit 0 on the package `sdd/patterns` and on a folder with the green fixture pattern plus the fixture `dominio.md`, counting ≥ 1 pattern read | test |
| AT-016 | Event-driven | **When** `sdd-design` runs, its text **shall** require: reading the CONTEXTO cited in the DEFINE and running `--validade` (expired = warning in the DESIGN), its `sup:` terms feeding the landmine sweep (C2); citing patterns as `§Esqueleto (validado_em …)` and running `patterns-lint.sh --design` (C3); `### Decision N:` titles as machine contract read by `docs-extract-decisions.sh` (C4); opening the whole playbook entry of each matched landmine, not only the index line (C10) | test |
| AT-017 | Unwanted | **If** the `UX_REVIEW` leaves the role of a surface undetermined (in the `| Surface (funcional) | Papel |` table of `## Surface Assignment`, a `Papel` cell that is not exactly one of `destaque`, `operacional`, `sobreposição` — the template text with the 3 together included —, or a pending surface question in `## Open UX Questions`), **then** `sdd-design` **shall** stop with a `[D2 · muda o produto]` question ("Qual o papel da surface …?", the 3 roles + "não sei", UX U6) before writing the DESIGN, and the `UX_REVIEW_TEMPLATE.md` **shall** say this question blocks the Design (C11) | test |
| AT-018 | Event-driven | **When** `docs-extract-decisions.sh [--root DIR] [--out FILE]` runs, it **shall** write `docs/adr/index.md` (default) with one row per decision block of `sdd/features/DESIGN_*.md` (closed list of headings; id `<STEM>#D<N>`, repeated N with suffix `b`, `c`…) and an `Órfãos` section for every DESIGN without a block, and **shall** exit 2 when extracted + orphans ≠ read | test |
| AT-019 | Event-driven | **When** `tests/` reads `sdd/WORKFLOW_CONTRACTS.yaml`, every script, path, field and block it names for `verify_gate`, `cartografo` and `revisor_governanca` **shall** exist in the package and match the briefs (fields, return block, allowed write) | test |
| AT-020 | Event-driven | **When** `evidence/F12_CONTEXTO/codex.sh` runs `codex exec` in a committed temporary copy (`CODEX_HOME` with only `auth.json`, `--ignore-user-config`, prompt saying no subagent nor collaborator is available) on `sdd-define` with a domain map and a matching input, the log **shall** show exit 40, `RESULTADO: AGUARDANDO_HUMANO` and `BRIEF_cartografo_<F>.md` in the copy; a 2nd run reaching step 11 **shall** show the same for `BRIEF_revisor-governanca_<F>.md`, and `verify-gate.sh` on the copy's DEFINE **shall** exit 5 printing `GOVERNANÇA NÃO REVISADA` and the 2 ways out | manual-ux |
| AT-021 | Event-driven | **When** `sdd-open.sh init` runs, it **shall** copy `sdd/patterns/README.md` and `sdd/WORKFLOW_CONTRACTS.yaml` when missing and never overwrite them; `MANIFEST.txt` **shall** list every new file; `release.yml` **shall** publish on changes to `sdd/patterns/**` and `sdd/WORKFLOW_CONTRACTS.yaml` | test |
| AT-022 | Event-driven | **When** the docs are read, `docs/context-and-governance.md` and its PT version **shall** explain Step 1.5, Step 6.5, the exit 5 and the dispense line, `dominio.md` and the patterns; the roadmap row "Context and governance" / "Contexto e governança" **shall** be gone, with the count in `tests/test_docs.py` updated; README (EN and PT) **shall** show the flow without `/sdd-governanca` as a separate phase | test |
| AT-023 | State-driven | **While** the package is built, the new scripts, briefs, fixtures and docs **shall** contain no RDD-specific term (`grep -niE 'supabase\|deno\|wordpress\|wp-content\|rdd-plataforma\|hostinger\|RDD/Wordpress\|rdd-eval'` without hit outside a generic example the test whitelists) and no single-agent tool name (`tests/test_agnostico.py`) | test |
| AT-024 | Event-driven | **When** the skills touched by the feature are released, each **shall** bump its version and identity line (`sdd-define`, `sdd-design`, `sdd-governanca`, and `sdd-build` and `sdd-iterate` for the 2nd reason of exit 5), the version pins in the tests **shall** follow, `skill-lint.py --conversa` **shall** pass on the 17 skills and `sdd-decisoes-lint.sh --sites` **shall** pass with the new count | test |
| AT-026 | Event-driven | **When** `governanca-bloco.py <resposta> --saida <relatório> [--comparar <saída>]` runs, it **shall** exit 0 for a valid block (`NA`, `REVISADO`, `PADRAO_AUSENTE`), 1 for `resultado: FALHA`, 2 for an invalid block (missing pair, unknown result, `lacuna:` without the 3 fixed fields or without `muda:`/`porque:`, `relatorio:` ≠ `saida`, Gnn set ≠ the `### Gnn — ` titles of `## Lacunas`, `REVISADO` without `MUDOU: <saida>`, another result with the report written) and 64 for bad usage | test |
| AT-025 | Non-regression | The suite of F1–F11 (`report-lint`, hooks, `sdd-fluxo.sh`, `adversarial-review*.sh`, conversation layer, `init`/`sync`/`doctor`) **shall continue to** pass, except for assertions this DEFINE changes on purpose (decision count, roadmap count, versions, fixtures with the `Governança` row) | test |

---

## Clarifications

### Session 2026-11-03

- [x] (Scope) D5 — governança sempre no Define, N.A. registrado, inclusive com `--parar` (brainstorm, decisão 1).
- [x] (Integrations) D8 — o `prova_script` é gravado e ligado ao `cmd` no Step 6.5; o Design só lista (brainstorm, decisão 2); o brief do revisor diz isso e a frase do privado (`revisor-governanca.md:60`) é anotada para a F15.
- [x] (Edge cases) DEFINE antigo sem a linha `Governança` ⇒ exit 5 sempre, com as 2 saídas (brainstorm, decisão 3) — AT-012.
- [x] (Constraints) `schema.check_cmd` cai; nenhum slot novo (brainstorm, decisão 4).
- [x] (Done signal) Uma Release só, `v2.4.0` por tag (brainstorm, decisões 5 e 6).
- [x] (Data model) **Decisão do Define:** a linha `Governança` é uma linha da tabela `## Technical Context` (`**Governança**` na 1ª coluna, valor na 2ª), como a linha do flag de prompts; valores finais aceitos: `N.A. — <motivo>`, `GOVERNANCA_REVIEW_<F>.md · a aplicadas · r recusadas · d adiadas`, `dispensada — <motivo>`; `pendente`/`falhou` só convivem com o marcador. Motivo: o template do Open já carrega o contexto técnico nessa tabela, e um prefixo fechado deixa o gate decidir sem interpretar prosa.
- [x] (UX flow) **Decisão do Define:** o padrão do projeto (`sdd/GOVERNANCA_PADRAO.md`, 5 campos) só é perguntado quando o revisor acha gatilho e o padrão falta (resultado `PADRAO_AUSENTE`, redespacho sem contar falha); no privado ele é perguntado antes de todo despacho. Motivo: num projeto sem dinheiro, tributo ou dado pessoal o aluno não responde 5 perguntas para ouvir N.A. — AT-011.
- [x] (Data model) **Decisão do Define:** as seções do CONTEXTO são genéricas, sem nome de tecnologia (o privado tem "Edges", "RPCs", "Telas"); a lista exata e o formato ficam no Design, iguais no lint e no brief.
- [x] (Edge cases) **Decisão do Define:** o cartógrafo não trava: 2ª falha ⇒ `nenhum (<motivo>)` e segue (brainstorm, decisão 10); a governança trava.
- [x] (Done signal) AT-020 é execução de agente real, fora do `cmd` do gate (custa a conta do Codex e não é determinística): `kind: manual-ux` na tabela, com o log como recibo, como o AT-030/031 da F9. O `check-versions --base v2.3.1` roda no CI e em evidência (a cópia do `git archive` não tem `.git`).
- [x] (Done signal) **Este DEFINE passa pelo próprio Step 6.5** antes do Design: a revisão de governança roda em contexto fresco (subagente com a `sdd-governanca` 2.3.0, que já existe) e a linha `Governança` abaixo vem do bloco dele, não do autor.

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

- C5 `sdd/invariants.md` e `--cruzar`/`--validar-inv` (F14, com o curator).
- Revisão de schema do privado (`audita-schema-gate.sh`, GRANT na migration, `lint-data-api-grants.py`) e o slot `schema.check_cmd`.
- `sdd/patterns/dominio.md` preenchido no pacote; inferir domínios do código sem mapa.
- Gate do extrator de ADR na release e os gates de docs do privado (diátaxis, extração, manutenção).
- UX e LLM no código (`sdd-loop-builder`, F13); curator, `/drive` e `drive.*` (F14).
- Reescrever a `sdd-governanca` (só o brief novo, a versão e a nota de que roda pelo Step 6.5).
- Alterar o repositório privado ou o sdd-starter; regenerar o starter.

---

## Constraints

| Type | Constraint | Impact |
|---|---|---|
| Technical | Piso bash 3.2 + Python 3.9 stdlib; sem `mapfile`, `declare -A`, `${x^^}`; `${VAR}` com chaves antes de não-ASCII | porte fiel dos scripts do privado, que já respeitam o piso |
| Technical | Específico da RDD não viaja (regra 4 do 8.0); nada copiado literalmente do privado nas fixtures | camadas → `layers:`; `patterns/dominio.md` → `sdd/patterns/`; fixtures com domínio fictício |
| Technical | Texto de skill sem ferramenta de um agente só (`tests/test_agnostico.py`) | briefs com contrato de entrada, proibições, bloco `<<<…>>>` e escada de despacho; sem nome de ferramenta |
| Technical | Delta-only nas skills; contratos de exit existentes inalterados | `verify-gate.sh` ganha um segundo motivo de exit 5, não um exit novo |
| Resource | CI: 25 min Ubuntu, 30 min macOS (F11: 12m53s e 17m31s) | testes novos baratos; medir no PR |
| Other | `sdd/features|handoffs|reports|reviews|traces/` fora do commit; `git add` por nome; arquivo novo no `MANIFEST.txt` | — |
| Other | Push em `main` só com OK do Roberto citando "sdd-open" | release fora desta etapa |

---

## Technical Context

| Aspect | Value | Notes |
|---|---|---|
| **Deployment Location** | `sdd/bin/{contexto-lint,patterns-lint,docs-extract-decisions,governanca-fronteira}.sh`, deltas em `sdd/bin/verify-gate.sh` e `sdd/bin/sdd-fluxo.sh`, `sdd/patterns/README.md`, `sdd/WORKFLOW_CONTRACTS.yaml`, `sdd/templates/{DEFINE,UX_REVIEW}_TEMPLATE.md`, `.agents/skills/{sdd-define,sdd-design,sdd-governanca,sdd-ux-review}/**`, `sdd/fixtures/**`, `bin/sdd-open.sh`, `.github/workflows/release.yml`, `docs/**`, `README*.md`, `tests/**`, `MANIFEST.txt` | versão `v2.4.0` por tag |
| **KB Domains** | nenhum | `sdd/kb/` não existe no repositório do pacote |
| **IaC Impact** | Modify existing | `release.yml`: filtro de caminhos ganha `sdd/patterns/**` e `sdd/WORKFLOW_CONTRACTS.yaml` |
| **LLM Prompts** | false | os briefs `cartografo.md` e `revisor.md` são instruções de orquestração do método para um agente de código, não prompt que roda em produção de um produto; nenhum provedor, `messages.create` ou `**/prompts/**` |
| **CONTEXTO de domínio** | nenhum (pulado: sem `sdd/patterns/dominio.md` — o mecanismo nasce nesta feature) | — |
| **Governança** | N.A. — sem gatilho: o DEFINE trata do método (scripts, skills, gates), sem dinheiro, saldo, lançamento, nota fiscal, tributo, folha ou dado pessoal | revisor fresco, `sdd-governanca` 2.3.0, 2026-11-03 |

---

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|---|---|---|---|
| A-001 | Os scripts do privado (`contexto-lint.sh`, `patterns-lint.sh`, `governanca-fronteira.sh`, `docs-extract-decisions.sh`) rodam no bash 3.2 sem mudança estrutural | o porte vira reescrita, o esforço cresce | partial (cabeçalhos declaram bash 3.2 + awk POSIX; conferir no build com o grep e o piso) |
| A-002 | O Codex CLI 0.163, com a condição "sem subagente nem colaborador" no prompt, segue a escada até o `despachar` e sai 40 | o AT-020 não exercita o degrau 2 | partial (provado na F9 para o avaliador, `codex-despacho-40.log`) |
| A-003 | Os testes novos cabem no teto do CI (+≤ 3 min) | job cancelado, release não publica | no (medir no PR) |
| A-004 | Só o agente despachado escreve durante o despacho (nenhuma edição humana na janela) | `FORA:` falso | yes — o Step trata `FORA:` sem apagar nada e lista o caminho |

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---|---:|---|
| Problem | 3 | lacuna concreta: fail-open na governança, Define sem contexto, Design sem patterns verificáveis |
| Users | 3 | 4 papéis com dor própria |
| Goals | 3 | MUST/SHOULD/COULD fechados; 6 decisões do Roberto |
| Success | 3 | classes, exits, casos de fronteira, prova no Codex, CI e release |
| Scope | 2 | a lista exata das seções genéricas do CONTEXTO e o limite de idade dos patterns ficam para o Design |
| **Total** | **14/15** | |

Minimum to proceed: **12/15**.

---

## Open Questions

None - ready for Design.

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | 2026-11-03 | SDD Define by RDD | Initial version |
| 1.1 | 2026-11-03 | SDD Define by RDD | UX review (`sdd/reviews/UX_REVIEW_F12_CONTEXTO.md`): U1 no AT-012 (exit 5 com texto e `→` próprios), U2 no AT-007/AT-009 (parada por papel, "parada i de 2"), U3/U8 no AT-008, U4 no AT-009, U5 no AT-011, U6 no AT-017, U7 no AT-001, U10 no AT-014; governança N.A. confirmada por revisor fresco (triagem independente, nenhum arquivo gravado) |
| 1.4 | 2026-11-03 | SDD Build by RDD | Revisões do build: AT-005 cobre commit do agente (`#HEAD`) e link criado no permitido (`#PERMITIDO`); AT-006 recusa arquivo ilegível; o snapshot mora na pasta temporária, com nome derivado da raiz (retomada depois da parada; o `.git` é só leitura na sandbox do Codex, medido) |
| 1.3 | 2026-11-03 | SDD Design by RDD | Revisão de contexto fresco do DESIGN (`sdd/reviews/REVISAO_DESIGN_F12_CONTEXTO_20261103.md`): H2 no AT-009/AT-012 (uma forma da linha, marcador de governança com as 2 saídas), H1 no AT-013 (testes com DEFINE em texto), M2 no AT-005, M3 no AT-009, M4 no AT-012 (placeholder), M5 no AT-015, M6 no AT-017, M7 no AT-026 (validador do bloco), L6 no AT-020 |
| 1.2 | 2026-11-03 | SDD Design by RDD | Design: AT-002 com `origin/<default_branch>` (Decision 3); "Step 6.5" vira "passo 11 (Governança)", porque no Open o DEFINE só existe em disco no passo 9 (Decision 5) |

---

## Next Step

Execute o **SDD Design by RDD**.
