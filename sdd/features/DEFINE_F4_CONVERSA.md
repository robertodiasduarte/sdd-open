# DEFINE: F4 Conversa do sdd-open

> As 13 skills nativas e a `sdd-checar-ambiente` passam a abrir toda resposta com o Status da etapa e a seguir a camada "Como falar com o aluno", com um formato único de pergunta e de parada (`PERGUNTA_DECISAO.md`). Comandos e ordem dos passos não mudam. A prova são o `skill-lint.py --conversa`, dois lints novos para DESIGN e HANDOFF e um teste que reprova nome de ferramenta de um agente só no texto que vai para o projeto.

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | F4_CONVERSA |
| **Date** | 2026-10-29 |
| **Author** | SDD Define by RDD (sessão com Roberto Dias Duarte) |
| **Status** | Ready for Design |
| **Clarity Score** | 14/15 |

---

## Problem Statement

As 13 skills nativas do sdd-open e a `sdd-checar-ambiente` respondem sem moldura comum:
- 9 delas abrem com um banner (`🧠 BUILD (Fase 3)`) que não diz em que etapa a conversa está;
- nenhuma tem tabela de etapas nem regra para explicar termo técnico na primeira vez;
- a pergunta ao aluno sai sem opções nem efeito, e a parada sai sem passos.

O pacote também não prova três coisas que as frentes seguintes vão usar:
- o DESIGN não tem lint, e o `docs-extract-decisions.sh` da F12 vai ler os títulos de ADR;
- o HANDOFF não tem lint;
- nada impede que o texto de uma skill ou de um template cite uma ferramenta de um agente só. Hoje há `AskUserQuestion` em `sdd/templates/fragments/CLARIFY.md:45` e "Task tool" em `sdd/templates/BUILD_REPORT_TEMPLATE.md:75`, o que quebra o parâmetro P2 fora do Claude Code.

---

## Target Users

| User | Role | Pain Point |
|---|---|---|
| Aluno que usa o sdd-open em qualquer agente suportado e nunca usou git nem terminal | Roda as skills de fase e de apoio | Não sabe em que ponto está, recebe jargão e saída crua, responde "pode" sem saber o que autoriza |
| Roberto, mantenedor | Edita as skills e publica as releases | Precisa que a camada não se perca quando a F9 reabrir as 13 skills, e que um lint diga quando ela sumiu |
| Frentes F9, F12 e W5 | Ligam o `exit 40` à parada, leem os títulos de ADR e completam o template de HANDOFF | Precisam de formato fixo de pergunta e parada, de `### Decision N: <nome>` estável e de um `handoff-lint` que aceite seção nova |

---

## Goals

| Priority | Goal |
|---|---|
| **MUST** | **As 14 skills**, cada uma com: (1) a seção `## Como falar com o aluno`, autocontida, com a tabela de etapas mapeada aos passos (nomes da Decisão 11 do BRAINSTORM), as 5 partes da resposta (Status · O que foi feito · Agora: etapa N, nome · Sua decisão · Próximo passo) e as regras curtas dos 10 itens da camada; (2) a instrução de ler `references/como-falar.md` antes da 1ª resposta. As 14 são `sdd-auditoria-harness`, `sdd-brainstorm`, `sdd-build`, `sdd-checar-ambiente`, `sdd-define`, `sdd-design`, `sdd-governanca`, `sdd-handoff`, `sdd-iterate`, `sdd-new-session`, `sdd-playbook`, `sdd-prompt-builder`, `sdd-release` e `sdd-ux-review` |
| **MUST** | Cada uma das 14 skills tem `references/como-falar.md` com: glossário da skill (inclusive os termos do open: exit 0/2/3/4/5/64, landmine, ledger, drift, slot vazio, adaptador/sync, waiver, vendor, contexto fresco, worktree, gate, manifest, slice, quando a skill os usar); o Status preenchido num momento real; e ≥1 exemplo de resposta completa com decisão, sem placeholder. O exemplo cita `sdd/templates/fragments/PERGUNTA_DECISAO.md` |
| **MUST** | O nome da fase vira a 1ª palavra do Status (`Build: ✅ 1 Plano · ▶️ 2 Modo · ⬜ 3 …`), e a linha `> Abra a resposta com o banner` sai das 9 skills que a têm. O Próximo passo é a linha de transição, com ≤100 caracteres. O kanban do `RESUMO_ETAPA.md` não muda |
| **MUST** | `sdd/templates/fragments/PERGUNTA_DECISAO.md` (novo). **Pergunta:** pergunta em negrito; opções `- **rótulo** — efeito`, a recomendada primeiro, com `(recomendado)` e o porquê; números em vez de adjetivos; IDs só em `(ref: …)`; a opção **não sei** sempre; nunca uma opção **Outro**; eco de 1 linha da escolha no "O que foi feito" seguinte; lugar reservado `[Dn]` para a classe da W2. **Parada ⏸️:** motivo em 1 frase, onde a ação acontece, passos numerados com o resultado esperado, o que não foi feito, `Brief:` (caminho do brief gravado, quando houver), `Sessão nova:` (comando para abrir a sessão, quando houver) e "Quando terminar, me peça de novo, eu continuo daqui." |
| **MUST** | `sdd/bin/skill-lint.py --conversa`. **Sem a flag**, o comportamento é idêntico ao de hoje. **Com a flag**, ele também reprova (exit 1, nomeando a skill e o motivo): seção ausente ou repetida; seção sem tabela com coluna `Etapa`; seção sem as 5 partes; seção que manda ler `references/como-falar.md` e o arquivo não existe; e, em cada pergunta do `como-falar.md` (linha em negrito terminada em `?` seguida de opções `- **…**`), 0 ou 2+ opções `(recomendado)`, recomendada que não é a 1ª opção, falta de **não sei**, presença de **Outro**; Próximo passo de exemplo com mais de 100 caracteres; e `como-falar.md` sem nenhuma pergunta |
| **MUST** | Fixtures do `skill-lint` que reprovam (item D): sem a seção; `como-falar.md` ausente; pergunta sem `(recomendado)`; 2 `(recomendado)`; sem **não sei**; com **Outro**. Mais 1 controle que passa. As 16 skills reais passam com `--conversa` |
| **MUST** | `sdd/bin/design-lint.py <DESIGN.md>` (novo; 0 ok · 1 violação · 64 uso). Reprova: falta de `## Key Decisions`; zero `### Decision N: <nome>`; N fora da sequência 1, 2, 3…; título `###` dentro de `## Key Decisions` fora do padrão `### Decision N: <nome>`; `## File Manifest` sem linha de dados; `**Total Files:** N` diferente do número de linhas; Dependencies que citam `#` inexistente ou formam ciclo; `{placeholder}` com espaço ou `{UPPER_SNAKE}` fora de bloco de código (`« »` não conta: é aspa comum em português) |
| **MUST** | `sdd/bin/handoff-lint.py <HANDOFF.md>` (novo; 0 · 1 · 64). Reprova: falta de `# HANDOFF:`; falta de `## Ficha` com as linhas Objetivo, Status e Verify Gate; falta de `## Prompt de retomada` com bloco de código; falta de `## Histórico de slices` com ≥1 `### … — AAAA-MM-DD`; `{placeholder}` ou `«placeholder»` fora de bloco de código; "como discutimos", "conforme combinado", "continue de onde paramos". **Aceita** seção a mais e não exige `## Eventos` (item F) |
| **MUST** | A `sdd-design` e a `sdd-handoff` ganham 1 passo logo depois do que grava o arquivo, que roda o lint novo sobre ele (vermelho ⇒ corrigir antes de entregar). São as duas únicas exceções de comando |
| **MUST** | `tests/test_agnostico.py` (novo) reprova `AskUserQuestion`, `TodoWrite`, `PreToolUse`, `PostToolUse`, `Task tool`, `Agent tool`, `subagent_type` e `/model` em `.agents/skills/**`, `sdd/templates/**`, `AGENTS.md.tmpl` e `sdd/playbook.md`, fora da lista de adaptadores declarada no teste (`bin/lib/vendors.sh` e o que o `init --vendors` gera). Tem fixture que reprova e controle que passa. "Subagente" como conceito é permitido. Os 2 hits de hoje são reescritos |
| **MUST** | Cada uma das 14 skills: bump **minor** em `metadata.version` (auditoria-harness 1.1.0, brainstorm 2.1.0, build 2.2.0, checar-ambiente 1.4.0, define 2.2.0, design 2.1.0, governanca 2.2.0, handoff 2.1.0, iterate 2.1.0, new-session 1.2.0, playbook 2.1.0, prompt-builder 2.1.0, release 2.3.0, ux-review 2.2.0), `metadata.updated: "2026-10"` e a linha de identificação `sdd-x vX.Y.Z · out/2026 · versão atual: https://github.com/robertodiasduarte/sdd-open/releases/latest`, com a mesma versão do frontmatter |
| **MUST** | Comandos e ordem dos passos não mudam, salvo as exceções declaradas: (a) sai o banner; (b) entra a linha de identificação; (c) entra o passo de lint no fim da `sdd-design` e da `sdd-handoff`; (d) na `sdd-checar-ambiente`, o Status vem antes do relatório do script, que continua como veio (saudável: Status + linha ✅). Prova: script de evidência que compara a `v2.2.4` com o HEAD |
| **MUST** | Nenhuma regressão: os 326 testes; as duas chamadas do `verify-gate.sh` no passo 4 da `sdd-iterate` e a frase do `AVAL-*.log` no `contexto-fresco.md` (`tests/test_correcoes_w0.py`); `sdd/bin/verify-gate.sh`, `report-lint.py`, `playbook-lint.sh`, `scripts/publish-gate.sh` e as fixtures existentes de `sdd/fixtures/` byte a byte; 16 skills |
| **MUST** | 1 sabotagem por script alterado ou novo (`skill-lint.py`, `design-lint.py`, `handoff-lint.py`), mais 1 no `test_agnostico.py` |
| **SHOULD** | `tests/test_conversa.py`: contrato de texto das 16 skills. Confere a linha de identificação igual a `metadata.version`, o `metadata.updated`, nenhuma linha de banner, a seção com as 5 partes e, nas 14 da F4, o `como-falar.md` citando o `PERGUNTA_DECISAO.md` |
| **SHOULD** | `docs/cli-conventions.md` com as saídas dos 2 lints novos e a flag `--conversa`; `CONTRIBUTING.md` mandando rodar `skill-lint.py --conversa` |
| **COULD** | Exemplo de parada ⏸️ completo no `como-falar.md` das skills que param por ação do aluno (new-session, release, checar-ambiente) |

---

## Success Criteria

- [ ] `python3 sdd/bin/skill-lint.py --conversa .agents/skills/sdd-*/SKILL.md` sai 0 nas 16 skills; o mesmo comando sem `--conversa` sai 0 numa skill sem a seção.
- [ ] As 6 fixtures do `skill-lint` saem 1 com `--conversa`, cada uma com a mensagem do seu motivo; o controle sai 0.
- [ ] `design-lint.py` sai 0 nos DESIGN_F1, F2 e F3 reais (evidência, fora do gate) e no `DESIGN_F4_CONVERSA.md`. Sai 1 em cada um dos 7 casos de violação do Goal.
- [ ] `handoff-lint.py` sai 0 na fixture do template do open, com e sem uma seção extra e sem `## Eventos`. Sai 1 em cada um dos 6 casos de violação do Goal.
- [ ] `tests/test_agnostico.py` falha na `v2.2.4` (`CLARIFY.md:45` e `BUILD_REPORT_TEMPLATE.md:75`) e passa no HEAD; a fixture reprova e o controle passa.
- [ ] Em 14 de 14 skills, o log de comandos intactos mostra só as exceções (a)–(d) entre `v2.2.4` e HEAD.
- [ ] `python3 scripts/check-versions.py --base v2.2.4 --base-obrigatoria` sai 0 com as 14 versões novas.
- [ ] A suíte sai 0 no piso `SDD_TEST_BASH=/bin/bash /usr/bin/python3` (Python 3.9.6 + bash 3.2.57) com mais de 326 testes e 0 falha.
- [ ] 4 de 4 sabotagens ficam vermelhas com o nome do teste e voltam ao verde com `git checkout`.
- [ ] `wc -l` ≤ 500 nas 16 `SKILL.md`.
- [ ] CI do PR verde em `ubuntu-latest` (`gate`) e `macos-latest` (`testes-macos`), com o passo "Skill integrity" em 0 achado.
- [ ] Depois do push em `main`, a run do `release` mostra `testes` e `testes-macos` como `needs` concluídos; `gh release view <tag> -R robertodiasduarte/sdd-open` lista `SHA256SUMS.txt`, e `shasum -a 256 -c` sai 0.

---

## Acceptance Tests

| ID | Pattern | Criterion (EARS) | Gate (`kind`) |
|---|---|---|---|
| AT-001 | Event-driven | **When** `skill-lint.py --conversa` runs on the 16 `.agents/skills/sdd-*/SKILL.md`, the system **shall** exit 0 | test |
| AT-002 | Non-regression | `skill-lint.py` without `--conversa` **shall continue to** check only the frontmatter: a skill without `## Como falar com o aluno` **shall** exit 0, and the 8 existing contracts of `tests/test_skill_lint.py` **shall** pass | test |
| AT-003 | Unwanted | **If** a skill run with `--conversa` lacks the section, has it twice, has no table with an `Etapa` column, misses one of the 5 parts, or tells the agent to read `references/como-falar.md` while that file is absent, **then** the lint **shall** exit 1 naming the skill and the reason | test |
| AT-004 | Unwanted | **If** a question in `references/como-falar.md` has zero or two `(recomendado)` options, a recommended option that is not the first, no **não sei** option or an **Outro** option, or the file has no question at all, **then** `skill-lint.py --conversa` **shall** exit 1 naming the file and the question | test |
| AT-005 | Unwanted | **If** an example `**Próximo passo**` line in `como-falar.md` is longer than 100 characters, **then** `skill-lint.py --conversa` **shall** exit 1 | test |
| AT-006 | Event-driven | **When** each of the 14 F4 skills is read, the system **shall** find the section, the reading instruction and `references/como-falar.md` citing `sdd/templates/fragments/PERGUNTA_DECISAO.md`, and **shall** find no `> Abra a resposta com o banner` line in any of the 16 skills | test |
| AT-007 | Event-driven | **When** `PERGUNTA_DECISAO.md` is read, the system **shall** find the question rules (recommended first with `(recomendado)`, **não sei**, no **Outro**, `(ref: …)`, 1-line echo, `[Dn]`) and the stop fields (⏸️, motivo, onde, passos with expected result, o que não foi feito, `Brief:`, `Sessão nova:`, "Quando terminar, me peça de novo") | test |
| AT-008 | Event-driven | **When** `design-lint.py` reads a DESIGN with `## Key Decisions`, `### Decision 1: …` to `### Decision N: …` in sequence, a File Manifest whose rows match `**Total Files:**` and acyclic dependencies on existing rows, the system **shall** exit 0 | test |
| AT-009 | Unwanted | **If** a DESIGN lacks `## Key Decisions`, has no decision, has a decision numbered out of sequence, has a `###` heading under `## Key Decisions` outside `### Decision N: <nome>` (e.g. `### Decisão 1`), has an empty File Manifest, a `**Total Files:**` mismatch, a dependency on a missing row or a cycle, or a placeholder outside code, **then** `design-lint.py` **shall** exit 1 naming the rule | test |
| AT-010 | Event-driven | **When** `design-lint.py` runs on `DESIGN_F1_MANUTENCAO.md`, `DESIGN_F2_TERRENO.md`, `DESIGN_F3_BUILD_RELEASE.md` and `DESIGN_F4_CONVERSA.md`, the system **shall** exit 0 on each, recorded in `evidence/F4_CONVERSA/design-lint-reais.log` | test |
| AT-011 | Event-driven | **When** `handoff-lint.py` reads a HANDOFF filled from `sdd/templates/HANDOFF_TEMPLATE.md`, also with an extra `## Recomendações` section and without `## Eventos`, the system **shall** exit 0 | test |
| AT-012 | Unwanted | **If** a HANDOFF lacks `# HANDOFF:`, the `## Ficha` rows Objetivo/Status/Verify Gate, a `## Prompt de retomada` with a code block (except when the Ficha Status is ✅, the case in which the `sdd-handoff` makes the prompt optional), or a `## Histórico de slices` entry `### … — AAAA-MM-DD`, or has a placeholder outside code, or says "como discutimos" / "continue de onde paramos", **then** `handoff-lint.py` **shall** exit 1 naming the rule | test |
| AT-013 | Event-driven | **When** either new lint is called without an argument or with a missing file, the system **shall** exit 64; **if** the file exists and cannot be read, **then** it **shall** exit 1 with a `🛑` line and `RESULTADO: VERMELHO`, never a traceback | test |
| AT-014 | Event-driven | **When** the `sdd-design` and `sdd-handoff` skills are read, the system **shall** find, in the step right after the one that writes the file (`### 8. Conferir` / `### 3b. Conferir a ficha`), the call `python3 sdd/bin/design-lint.py` / `python3 sdd/bin/handoff-lint.py` on that file | test |
| AT-015 | Unwanted | **If** `AskUserQuestion`, `TodoWrite`, `PreToolUse`, `PostToolUse`, `Task tool`, `Agent tool`, `subagent_type` or `/model` appears in `.agents/skills/**`, `sdd/templates/**`, `AGENTS.md.tmpl` or `sdd/playbook.md` outside the declared adapters, **then** `tests/test_agnostico.py` **shall** fail naming file and line; on the F4 tree it **shall** pass, and the word "subagente" **shall** not fail it | test |
| AT-016 | Event-driven | **When** `tests/test_agnostico.py` from HEAD runs against a `git archive v2.2.4` tree, the system **shall** fail on `CLARIFY.md` and `BUILD_REPORT_TEMPLATE.md`, recorded in `evidence/F4_CONVERSA/baseline.log` | test |
| AT-017 | Event-driven | **When** each of the 16 skills is read, its identification line **shall** carry the same version as `metadata.version`, and `metadata.updated` **shall** be present | test |
| AT-018 | Non-regression | Each of the 14 skills **shall continue to** have the same numbered step headings and the same command lines (code spans citing `sdd/bin`, `git`, `gh`, `bash`, `python3` or `scripts/`) as in `v2.2.4`, except exceptions (a)–(d), evidenced per skill in `evidence/F4_CONVERSA/comandos-intactos.log` | test |
| AT-019 | Event-driven | **When** `check-versions.py --base v2.2.4 --base-obrigatoria` runs on the F4 tree, the system **shall** exit 0 | test |
| AT-020 | Non-regression | The system **shall continue to** pass the 326 existing tests (with the deliberate updates of `test_skill_lint`, `test_contrato_build_release` and `test_release_workflow`), keep `verify-gate.sh`, `report-lint.py`, `playbook-lint.sh`, `scripts/publish-gate.sh` and the existing `sdd/fixtures/` files byte-identical to `v2.2.4`, and count 16 skills | test |
| AT-021 | Unwanted | **If** a contract is broken on purpose in `skill-lint.py`, `design-lint.py`, `handoff-lint.py` or the term list of `test_agnostico.py`, **then** at least one named test **shall** fail, and reverting it with `git checkout` **shall** turn the suite green again | test |
| AT-022 | Event-driven | **When** the CI runs on the PR, the `Skill frontmatter` step **shall** call `skill-lint.py --conversa`, and jobs `gate` (ubuntu) and `testes-macos` **shall** succeed with 0 integrity findings | test |

---

## Clarifications

### Session 2026-10-29

- [x] (Data model) O BRAINSTORM dizia "DESIGN_F1–F3 copiados como fixture". Esses documentos não são rastreados, e um deles tem caminho `/Users/` que o G2 do publish-gate reprova. → Os DESIGN reais são conferidos como evidência (AT-010); as fixtures do `design-lint` são escritas a partir do `DESIGN_TEMPLATE.md`. Integrado em AT-008/AT-010.
- [x] (Data model) "Pergunta" no `como-falar.md`, para o lint: uma linha cujo trecho em negrito termina em `?`, seguida de itens `- **rótulo**`. Rótulos `não sei` e `Outro` são comparados sem caixa. `(recomendado)` é procurado no item. → Integrado em AT-004.
- [x] (Edge cases) As skills portadas `sdd-iniciar-repo` e `sdd-higiene-dado` estão no formato Grupo 1 (glossário dentro, sem `como-falar.md`). → O `--conversa` só exige o `como-falar.md` quando a seção manda lê-lo; as duas passam sem mudança. Integrado em AT-001/AT-003.
- [x] (Constraints) O `cmd` do Verify Gate não pode ter aspas duplas internas e roda com `bash -c` da raiz. A suíte no piso usa o `/usr/bin/python3` e o `/bin/bash` do macOS. → `cmd` abaixo. Integrado em Verify Gate.
- [x] (Done signal) `check-versions` (AT-019), comandos intactos (AT-018) e `design-lint` nos DESIGN reais (AT-010) precisam de `.git` ou de `sdd/features/`, que a cópia do gate não tem. → São ATs `test` com log em `evidence/F4_CONVERSA/`, rodados fora do `cmd`. Integrado em AT-010/AT-018/AT-019.
- [x] (Scope) A linha de identificação igual à versão (AT-017) fica num teste de contrato, não no `check-versions.py` (que não muda), para não mexer no gate da release. → Integrado em Goals (SHOULD `test_conversa.py`) e AT-017.
- [x] (UX flow) A obediência do agente à camada não é executável em teste. → Os ATs conferem o contrato escrito e a conferência num agente real vira pendência no handoff (A-002).

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

O gate só enxerga o que está commitado (`git archive HEAD`), então o Build commita na branch antes de rodar. `PUBLISH_GATE_MODE=ci` é necessário porque o modo padrão exige a camada privada de padrões. A suíte roda no piso: Python 3.9 do macOS, bash 3.2.

Ficam fora do `cmd`, com log em `evidence/F4_CONVERSA/`, porque precisam de `.git` ou de `sdd/features/`: AT-010, AT-016, AT-018 e AT-019, mais a Release (último Success Criterion).

---

## Out of Scope

- Seção "Encerramento", encadeamento automático, classes D1–D5 nas perguntas, `sdd-fluxo.sh` e `exit 40` (W2/F9). Do `[Dn]`, só o lugar reservado.
- Eval ou runner de conversa; conferência num agente real como critério.
- Inventário LLM e rastreabilidade AT → arquivo no `design-lint` (F13).
- "Por que cada regra existe", guia do aluno, quickstart, README (F6).
- Mudança em `scripts/publish-gate.sh`, `sdd/bin/verify-gate.sh`, `sdd/bin/report-lint.py`, `sdd/bin/playbook-lint.sh`, `scripts/check-versions.py` e no kanban do `RESUMO_ETAPA.md`.
- `sdd-iniciar-repo` e `sdd-higiene-dado` (já têm a seção; não mudam de versão).
- Formato de HANDOFF do starter; a W5 completar o `HANDOFF_TEMPLATE.md`.
- Regenerar o sdd-starter a partir do open; mexer no checkout do starter.

---

## Constraints

| Type | Constraint | Impact |
|---|---|---|
| Technical | bash 3.2 sem `declare -A`/`mapfile`/`readlink -f`/`grep -P`; Python ≥ 3.9 só stdlib; `python3 -B` | Lints e testes rodam no macOS de fábrica e no CI macOS, que afirma o piso |
| Technical | Integridade do CI em `.agents/skills/`: nenhum Unicode invisível (o FE0F de `▶️`/`⏸️` e o ZWJ de emoji passam), nenhum `curl … \| sh` literal | Conferir os code points depois de escrever; descrever sem o padrão literal |
| Technical | G2 do publish-gate: nenhum literal casa com `scripts/publish-gate-patterns.txt` | Exemplos de `como-falar.md` e fixtures sem CPF/CNPJ/telefone/e-mail real nem caminho `/Users/` |
| Technical | G3: `MANIFEST.txt` allowlist nos dois sentidos, ordem `LC_ALL=C` | Cada arquivo novo é declarado no mesmo commit; `sdd/features|handoffs|reports/` ficam fora |
| Technical | `skill-lint.py` vai para o projeto do usuário | O padrão (sem flag) não muda de comportamento |
| Technical | `SKILL.md` ≤ 500 linhas | Seção de ~25–30 linhas; o resto vai para `references/como-falar.md` |
| Technical | Decisões da frente que não se reabrem: camada sempre ligada, sem toggle nem slot; Status `✅ ▶️ ⬜ ⏸️ ➖` abrindo cada resposta, com o nome da fase como 1ª palavra; kanban do `RESUMO_ETAPA.md` intacto; o open como fonte canônica de governanca, auditoria-harness e prompt-builder | — |
| Technical | Skill alterada sobe `metadata.version` contra `v2.2.4` | As 14 versões do Goal |
| Other | Push em `main` só com o OK do Roberto citando "sdd-open" na mesma mensagem, depois de PR com CI verde; a versão do pacote (`v2.2.5` × `v2.3.0`) é perguntada nesse OK | A Release depende desse OK |
| Other | Os artefatos SDD ficam na branch `docs/incorporar-starter`, nunca mesclada | Não entram no commit de `feat/f4-conversa` |

---

## Technical Context

| Aspect | Value | Notes |
|---|---|---|
| **Deployment Location** | 14 × `.agents/skills/<skill>/SKILL.md` + `references/como-falar.md`; `sdd/templates/fragments/PERGUNTA_DECISAO.md`; `sdd/templates/fragments/CLARIFY.md`; `sdd/templates/BUILD_REPORT_TEMPLATE.md`; `sdd/bin/skill-lint.py`, `design-lint.py`, `handoff-lint.py`; fixtures novas; `tests/test_skill_lint.py`, `test_design_lint.py`, `test_handoff_lint.py`, `test_agnostico.py`, `test_conversa.py`, `test_contrato_build_release.py`, `test_release_workflow.py`; `.github/workflows/publish-gate.yml` (passo do `skill-lint`); `docs/cli-conventions.md`; `CONTRIBUTING.md`; `MANIFEST.txt` | Fonte do texto: `/Users/robertoduarte/rdd-public/sdd-starter` em `17c69c4` |
| **KB Domains** | N/A | Não há `sdd/kb` neste repositório |
| **IaC Impact** | Modify existing | Só o comando do passo `Skill frontmatter` do `publish-gate.yml` ganha `--conversa`. O push em `main` publica a Release sozinho, porque toca `.agents/skills/**`, `sdd/bin/**` e `sdd/templates/**` |
| **LLM Prompts** | false | Os `SKILL.md` são instruções de orquestração SDD lidas pelo agente de desenvolvimento; nenhum prompt de runtime de produto |

---

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|---|---|---|---|
| A-001 | Os 326 testes passam no piso em `dd27ef6` antes da F4 | O Build partiria de base vermelha | yes (handoff da M1: 326 OK no piso e no CI); reconferir no início do Build |
| A-002 | O agente lê o `references/como-falar.md` quando a seção manda e segue a camada | O glossário não aparece; Status e regras continuam valendo, porque ficam no `SKILL.md` | no; não é executável em teste, e a conferência num agente real fica como pendência |
| A-003 | As F9, F12 e W5 vão ler os mesmos títulos e campos que a F4 fixa (`### Decision N: <nome>`, `Brief:`, `Sessão nova:`, seções do template do open) | A frente seguinte teria de mudar o lint ou o fragmento | no; vem do plano consolidado, seções 4.1 e 8.1 |
| A-004 | Nenhum texto legítimo das skills precisa citar `/model` ou `Task tool` fora de um adaptador | O teste reprovaria texto legítimo | yes; a varredura de `v2.2.4` achou só os 2 hits do Goal |

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---|---:|---|
| Problem | 3 | Sintomas com onde acontecem (banner em 9 skills, 2 hits de ferramenta com linha, 2 documentos sem lint) |
| Users | 3 | Aluno, mantenedor e as frentes que dependem do formato |
| Goals | 3 | Vêm das 7 respostas e dos 2 checkpoints, com versões e regras do lint enumeradas |
| Success | 2 | Tudo mecânico é observável; o tom da conversa num agente real fica para conferência humana |
| Scope | 3 | 14 skills, arquivos, exceções de comando e destinos do que ficou fora (W2/F9, F6, F13) |
| **Total** | **14/15** | |

Minimum to proceed: **12/15**.

---

## Open Questions

None - ready for Design.

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | 2026-10-29 | SDD Define by RDD | Initial version |
| 1.2 | 2026-10-29 | SDD Build by RDD | Revisão de contexto fresco (M3, L5, L6): AT-012 dispensa o prompt na ficha ✅ (a `sdd-handoff` o declara opcional sem continuação); AT-013 cobre arquivo ilegível; `« »` deixa de ser placeholder no `design-lint` |
| 1.1 | 2026-10-29 | SDD Design by RDD | Design: AT-014 aponta o passo logo depois da gravação (`### 3b` na handoff, para não renumerar a limpeza); exceção (d) vale para toda resposta da checar-ambiente (Status antes do relatório do script, sem retradução), porque a skill manda repassar a saída como veio |

---

## Next Step

Execute o **SDD Design by RDD**.
