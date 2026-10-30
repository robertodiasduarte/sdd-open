# DEFINE: F6 Docs do sdd-open

> O open ganha um guia do aluno em português, a regra "valide antes de seguir" e a tabela "onde roda" no quickstart, um roadmap público em inglês e português, README e `AGENTS.md.tmpl` que citam as 17 skills, a KB e o bloco do OK, e a seção "Por que cada regra existe" nas 7 skills de fase. Um teste novo abre cada link relativo dos docs e exige a seção nas 9 skills que a têm.

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | F6_DOCS |
| **Date** | 2026-10-29 |
| **Author** | SDD Define by RDD (sessão com Roberto Dias Duarte) |
| **Status** | Ready for Design |
| **Clarity Score** | 14/15 |

---

## Problem Statement

O sdd-open não tem a porta de entrada que o sdd-starter tem para quem nunca usou git nem terminal. São cinco lacunas:
- **Não há guia do aluno.** O quickstart (`docs/pt-BR/quickstart.md`, 175 linhas) supõe quem sabe instalar e configurar. O guia do starter (494 linhas) não serve como está: fala em `npx skills add`, 15 skills, 2 agentes, `ux-review-builder` e diz que `sdd/` não vai para o git, o que é falso no open.
- **O quickstart não manda validar cada documento antes da fase seguinte.** O passo 4 junta Design, Build e Release numa linha, e não há a tabela "onde a solução vai rodar".
- **As skills de fase não guardam o motivo das próprias regras.** Só a `sdd-new-session` e a `sdd-iniciar-repo` têm "Por que cada regra existe". Numa limpeza, uma regra como "commit antes do gate" ou "uma pergunta por mensagem" parece burocracia e some.
- **README e `AGENTS.md.tmpl` estão atrás do pacote.** O `AGENTS.md.tmpl:13` lista só as fases. O `README.md:53` mostra o fluxo `/sdd-brainstorm → … → /sdd-release`. Nenhum dos dois cita as skills de preparo (F2), a `sdd-kb` e o `kb-dominios.py` (F5) nem o bloco do OK (F3).
- **Não há roadmap público.** O `docs/comparison.md:55` diz "This is on the roadmap here", e esse roadmap não existe.

---

## Target Users

| User | Role | Pain Point |
|---|---|---|
| Aluno sem git nem terminal (contador, analista, gestor) | Instala o open e conduz uma feature pelas skills | Não sabe por onde começar, em que ordem usar as 17 skills, nem o que fazer quando a skill para ou o gate devolve 2, 3, 4, 5 ou 64 |
| Quem avalia ou instala o open (lê README e quickstart, em inglês ou português) | Decide adotar e faz a primeira spec | Não vê as skills de preparo, a KB nem o bloco do OK; segue de fase em fase sem ler o documento |
| Agente que lê o `AGENTS.md` gerado no projeto | Escolhe a skill certa para o pedido | Conhece só as fases; não sabe que existe skill de preparo nem de KB |
| Mantenedor (ou agente) que edita uma skill de fase | Corrige ou enxuga o texto | Corta uma regra sem saber por que ela existe |

---

## Goals

| Priority | Goal |
|---|---|
| **MUST** | **`docs/pt-BR/guia-do-aluno.md`** (novo, só em português), adaptado de `sdd-starter/docs/guia-do-aluno.pt-BR.md` com os mesmos 10 blocos numerados e um sumário com âncoras.<br>• **Instalação:** passa a ser `bash …/bin/sdd-open.sh init --vendors …`, e o guia mostra como chamar uma skill em cada um dos 7 agentes (Claude Code, Codex CLI, Gemini CLI, Cursor, Kimi Code, Grok Build, GLM).<br>• **Linha de identificação:** aponta para `sdd-open/releases/latest`.<br>• **Mapa:** 4 blocos com as 17 skills. Preparar: checar-ambiente, iniciar-repo, higiene-dado, new-session. Criar: kb, brainstorm, define, governanca, ux-review, design, build. Fechar: handoff, release. Transversais: iterate, playbook, prompt-builder, auditoria-harness.<br>• **Catálogo:** uma ficha `#### sdd-…` por skill (17), com o molde "para que serve · quando usar · quando não usar · como pedir · o que produz · o que vai perguntar".<br>• **Parada ⏸️:** inclui as linhas Brief e Sessão nova (`PERGUNTA_DECISAO.md`).<br>• **"Quando algo dá errado":** traduz os exits do Verify Gate (2, 3, 4, 5, 64).<br>• **Atualizar:** troca `npx skills update` pelo caminho real do open: `git pull` no clone, `doctor`, apagar a pasta de cada skill que ele apontar, `init --vendors … --yes` e `sync`. O `sync` sozinho não atualiza skill instalada.<br>• **Requisitos:** git, bash ≥ 3.2 (Git Bash ou WSL no Windows) e python3 ≥ 3.9; a instalação pelo agente é `--dry-run`, ler o plano, e então `--yes`.<br>• **Correção do starter:** `sdd/` é versionada no open (config, playbook, specs), e o guia diz isso |
| **MUST** | **`docs/quickstart.md` e `docs/pt-BR/quickstart.md`**:<br>• a regra do método ("never move on with a document you have not read" / "nunca siga para a próxima fase com um documento que você não leu");<br>• uma linha "Validate before moving on" / "Valide antes de seguir" em cada fase do passo 4 (Brainstorm, Define, Design, Build);<br>• a tabela "where the solution will run → what to write in the Design" / "onde a solução vai rodar → o que escrever no Design", com o Build em qualquer um dos 7 agentes, sem Lovable;<br>• correção P1 do passo 5 ("When the package updates" / "Quando o pacote atualizar"): hoje diz que `git pull` + `sync` basta; passa a mandar rodar o `doctor` e, para cada skill que ele apontar, apagar a pasta e rodar `init` |
| **MUST** | **`docs/roadmap.md` e `docs/pt-BR/roadmap.md`** (novos), com o cabeçalho de idioma dos outros pares:<br>• 5 temas *planned* / *planejado*, sem data: hooks e evidência; fluxo encadeado; revisão adversarial; contexto e governança; loop-builder e drive;<br>• "Specs as deltas" / "Specs como deltas" *under evaluation* / *em avaliação*;<br>• reconciliação spec ↔ código *planned* / *planejado*, no mesmo status do `comparison.md` |
| **MUST** | **`README.md` e `README.pt-BR.md`**:<br>• seção nova com as 17 skills nos 4 blocos do guia;<br>• o fluxo começa por "preparar" e pela `sdd-kb` (opcional);<br>• a release cita o bloco único do OK;<br>• a `sdd-define` cita o `kb-dominios.py`;<br>• a Documentação linka o guia ("(PT)" no README em inglês) e o roadmap |
| **MUST** | **`AGENTS.md.tmpl`**:<br>• a tabela ganha as 4 skills de preparo e a `sdd-kb` (antes da fase 0), e a linha da fase 1 cita `sdd/bin/kb-dominios.py`;<br>• uma regra nova: a release pede um OK só, depois do bloco que diz o que sobe e se o push publica sozinho;<br>• o placeholder `{{VENDORS}}` e as 6 regras atuais continuam;<br>• nenhum nome de ferramenta de um agente só (`tests/test_agnostico.py`) |
| **MUST** | **"Por que cada regra existe"** nas 7 skills de fase (`sdd-brainstorm`, `sdd-define`, `sdd-governanca`, `sdd-ux-review`, `sdd-design`, `sdd-build`, `sdd-release`):<br>• título `## Por que cada regra existe`, logo antes de `## Encerramento (obrigatório)`;<br>• 3 a 10 itens no formato `- **regra** — motivo`, cada um sobre uma regra que a skill já tem;<br>• na `sdd-release`, as regras do starter adaptadas ao open: bloco do OK, `deploy-espera-testes.py`, ledger;<br>• cada skill sobe de **patch** e atualiza a linha de identificação: brainstorm 2.1.1, define 2.3.1, governanca 2.2.1, ux-review 2.3.1, design 2.1.1, build 2.2.1, release 2.3.1;<br>• nenhum passo, bloco cercado ou linha de comando muda |
| **MUST** | **`tests/test_docs.py`** (novo, stdlib, sem rede):<br>• todo link relativo de `README.md`, `README.pt-BR.md`, `CONTRIBUTING.md` e `docs/**/*.md` aponta para arquivo que existe;<br>• toda âncora `#…` para um `.md` da árvore casa com um título dele, pela regra de âncora do GitHub;<br>• o guia tem os 10 blocos, as 17 fichas, os 7 agentes e nenhuma das premissas falsas do starter;<br>• os quickstarts têm a regra, as 4 validações e nenhum "Lovable";<br>• os roadmaps têm os status e nenhum ano;<br>• os `comparison.md` continuam com "Specs como deltas" em avaliação;<br>• README e `AGENTS.md.tmpl` citam o que o Goal pede;<br>• as 9 skills com a seção (as 7 + `sdd-new-session` + `sdd-iniciar-repo`, títulos com ou sem "(não apague sem ler)") têm 1 título e ≥ 3 itens |
| **MUST** | `MANIFEST.txt` com os 4 arquivos novos (`docs/pt-BR/guia-do-aluno.md`, `docs/roadmap.md`, `docs/pt-BR/roadmap.md`, `tests/test_docs.py`), em ordem `LC_ALL=C` |
| **MUST** | Nenhuma regressão:<br>• os 499 testes;<br>• `sdd/bin/**`, `sdd/fixtures/**`, `sdd/templates/**`, `sdd/playbook.md`, `scripts/**`, `bin/**` e `.github/**` idênticos byte a byte à `v2.2.6`;<br>• o bloco comum da camada de conversa nas 15 skills, o bloco do OK da `sdd-release` e o passo 4 da `sdd-iterate` intactos |
| **MUST** | 1 sabotagem por verificação nova do `tests/test_docs.py`, no mínimo 3: link quebrado no guia, seção apagada numa skill, "Specs como deltas" marcado ✅ |
| **SHOULD** | Em `docs/comparison.md` e `docs/pt-BR/comparison.md`, a frase "This is on the roadmap here" / "Isso está no roadmap aqui" vira link para o roadmap do mesmo idioma, sem mudar a tabela |

---

## Success Criteria

- [ ] `tests/test_docs.py` passa e cobre os 7 grupos do Goal (links, âncoras, guia, quickstarts, roadmaps, README/`AGENTS.md.tmpl`, seção nas 9 skills).
- [ ] O guia tem 10 blocos `## N.`, 17 fichas `#### sdd-…` e cita os 7 agentes; nenhuma ocorrência de `npx skills`, `15 skills`, `ux-review-builder` ou `sdd-starter/releases`.
- [ ] Cada quickstart (EN e PT) tem ≥ 4 linhas "Validate before moving on" / "Valide antes de seguir" e 0 "Lovable".
- [ ] Cada roadmap tem os 5 temas, "deltas" em avaliação e 0 ocorrências de `20\d\d`.
- [ ] `python3 sdd/bin/skill-lint.py --conversa .agents/skills/sdd-*/SKILL.md` sai 0 nas **17** skills, e `wc -l` ≤ 500 em cada `SKILL.md`.
- [ ] `python3 scripts/check-versions.py --base v2.2.6 --base-obrigatoria` sai 0, com as 7 versões de patch do Goal.
- [ ] O log de comandos intactos (`v2.2.6` × HEAD) mostra, nas 7 skills, só 3 tipos de mudança: a seção nova, `version:` no frontmatter e a linha de identificação.
- [ ] A suíte sai 0 no piso `SDD_TEST_BASH=/bin/bash /usr/bin/python3` (Python 3.9.6 + bash 3.2.57), com mais de 499 testes e 0 falha.
- [ ] Baseline vermelha: `tests/test_docs.py` falha na árvore `v2.2.6`.
- [ ] As 3 sabotagens ficam vermelhas com o nome do teste e voltam ao verde com `git checkout`.
- [ ] O CI do PR sai verde em `ubuntu-latest` (`gate`) e `macos-latest` (`testes-macos`), com 0 achado de integridade; os links do sumário do guia abrem na página do PR no GitHub.
- [ ] Depois do push em `main`, a run do `release` publica `v2.2.7`, `gh release view v2.2.7 -R robertodiasduarte/sdd-open` lista `SHA256SUMS.txt` e `shasum -a 256 -c` sai 0.

---

## Acceptance Tests

| ID | Pattern | Criterion (EARS) | Gate (`kind`) |
|---|---|---|---|
| AT-001 | Event-driven | **When** `tests/test_docs.py` reads `docs/pt-BR/guia-do-aluno.md`, the system **shall** find 10 headings `## 1.` to `## 10.`, one `#### sdd-<name>` heading for each of the 17 folders in `.agents/skills/`, the 7 agent names, `init --vendors`, `--yes`, `python3`, `doctor` together with "apague" and `init` (the update path), and `sdd-open/releases/latest` | test |
| AT-002 | Unwanted | **If** the guide contains `npx skills`, `15 skills`, `ux-review-builder`, `sdd-starter/releases`, a path in the starter's flat layout (`sdd/BRAINSTORM_`, `sdd/DEFINE_` …), a claim that `sdd/` stays out of git or off GitHub, or a literal the W0 test forbids in packaged files, **then** `tests/test_docs.py` (or `tests/test_correcoes_w0.py`) **shall** fail naming the forbidden text | test |
| AT-003 | Event-driven | **When** `tests/test_docs.py` reads `docs/quickstart.md` and `docs/pt-BR/quickstart.md`, each **shall** contain the method rule, at least 4 "Validate before moving on" / "Valide antes de seguir" lines, and, inside step 4, the "where it runs" table header and the 7 agent names; step 5 **shall** cite `doctor` and `init` as the way to receive a newer skill; neither file **shall** contain "Lovable" | test |
| AT-004 | Event-driven | **When** `tests/test_docs.py` reads `docs/roadmap.md` and `docs/pt-BR/roadmap.md`, each **shall** carry the language header linking the other, the 5 themes marked *planned* / *planejado*, "Specs as deltas" / "Specs como deltas" marked *under evaluation* / *em avaliação*, and no four-digit year | test |
| AT-005 | Non-regression | `docs/comparison.md` and `docs/pt-BR/comparison.md` **shall continue to** mark "Specs as deltas" / "Specs como deltas", in the SDD Open column (the last cell of that row), as ❌ *under evaluation* / *em avaliação*, never ✅ | test |
| AT-006 | Event-driven | **When** `tests/test_docs.py` reads `README.md` and `README.pt-BR.md`, each **shall** name the 17 skills, `kb-dominios.py` and the release's single-approval block, link `docs/pt-BR/guia-do-aluno.md` and its roadmap, and keep the cross-link to the other README | test |
| AT-007 | Event-driven | **When** `tests/test_docs.py` reads `AGENTS.md.tmpl`, the system **shall** find `sdd-checar-ambiente`, `sdd-iniciar-repo`, `sdd-higiene-dado`, `sdd-new-session`, `sdd-kb`, `sdd/bin/kb-dominios.py`, the release rule (one approval after the block) and the `{{VENDORS}}` placeholder, and `tests/test_agnostico.py` **shall** stay green | test |
| AT-008 | Unwanted | **If** a relative link in `README.md`, `README.pt-BR.md`, `CONTRIBUTING.md` or `docs/**/*.md` points to a file that does not exist, or an `#anchor` into a `.md` of the tree matches none of its headings by GitHub's anchor rule, **then** `tests/test_docs.py` **shall** fail naming `file:line` and the target; external `http(s)://` and `mailto:` links **shall** be skipped | test |
| AT-009 | Unwanted | **If** any of `sdd-brainstorm`, `sdd-define`, `sdd-governanca`, `sdd-ux-review`, `sdd-design`, `sdd-build`, `sdd-release`, `sdd-new-session` or `sdd-iniciar-repo` has no `## Por que cada regra existe` heading (optionally followed by `(não apague sem ler)`), has it more than once, or has fewer than 3 items `- **…** —` under it, **then** `tests/test_docs.py` **shall** fail naming the skill | test |
| AT-010 | Event-driven | **When** the 7 phase skills are read, the section **shall** come right before `## Encerramento (obrigatório)`, each skill **shall** have the patch version of the Goal in `metadata.version` and in the identification line, and `skill-lint.py --conversa` **shall** exit 0 on the 17 skills | test |
| AT-011 | Non-regression | The 7 phase skills **shall continue to** have the same text as in `v2.2.6`, byte for byte, once the new section is removed and the version in `version:` and in the identification line is normalized, and the same steps, numbered items and command lines, evidenced in `evidence/F6_DOCS/comandos-intactos.log` | test |
| AT-012 | Event-driven | **When** `check-versions.py --base v2.2.6 --base-obrigatoria` runs on the F6 tree, the system **shall** exit 0, evidenced in `evidence/F6_DOCS/check-versions.log` | test |
| AT-013 | Non-regression | The system **shall continue to** pass the 499 existing tests, keep `sdd/bin/**`, `sdd/fixtures/**`, `sdd/templates/**`, `sdd/playbook.md`, `scripts/**`, `bin/**` and `.github/**` byte-identical to `v2.2.6`, keep each `SKILL.md` at ≤ 500 lines, and pass `publish-gate.sh` in `ci` mode (G2 personal-data patterns over the new docs, G3 `MANIFEST.txt`) | test |
| AT-014 | Unwanted | **If** a link of the guide is broken, the section is removed from one skill, or "Specs como deltas" is marked ✅, **then** at least one named test of `tests/test_docs.py` **shall** fail, and reverting it with `git checkout` **shall** turn the suite green again | test |

---

## Clarifications

### Session 2026-10-29

- [x] (Scope) Idioma: guia só em PT; roadmap em EN e PT (BRAINSTORM, decisão 1). Integrado em Goals e AT-001/AT-004.
- [x] (Scope) Seção nas 7 skills de fase; o teste aceita os 2 títulos atuais da `sdd-new-session` e da `sdd-iniciar-repo` (BRAINSTORM, decisões 2 e 3). Integrado em AT-009.
- [x] (Constraints) Release `v2.2.7` automática; bump de **patch** nas 7 skills (BRAINSTORM, decisões 4 e 8). Integrado em Goals e AT-010/AT-012.
- [x] (Data model) "Regra de âncora do GitHub": texto do título em minúsculas, sem o que não for letra (acentuada inclusive), dígito, espaço, `-` ou `_`, com cada espaço virando `-`; títulos repetidos ganham `-1`, `-2`. → A-002 registra que a conferência final é abrir o sumário no PR.
- [x] (Data model) "Link relativo": alvo de `](…)` que não começa com `http://`, `https://`, `mailto:` nem `#`, resolvido a partir da pasta do arquivo; `#…` sozinho é âncora no próprio arquivo. Links dentro de blocos cercados não contam.
- [x] (Edge cases) O `README.md` aponta `CONTRIBUTING.md`, `LICENSE` e `NOTICE`: todos existem e entram na checagem de existência. Links para `../../../releases/latest` (forma do starter) não são usados no open.
- [x] (Edge cases) "Nenhum ano" no roadmap = nenhuma sequência `\b20\d\d\b`. O roadmap não cita datas, versões futuras nem o número interno das frentes (F7–F14).
- [x] (Terminology) "Os 5 temas" usam os nomes do plano 4.3, item I: hooks e evidência, fluxo encadeado, revisão adversarial, contexto e governança, loop-builder e drive. O teste confere por palavras-chave de cada tema nos dois idiomas, fixadas no Design.
- [x] (UX flow) Não há tela; o "fluxo" é a leitura do guia. Uma revisão de UX não se aplica: o tom e o glossário vêm do guia do starter, já usado com alunos, e da camada da F4.
- [x] (Integrations) O CI roda o `publish-gate.sh` (G2) sobre a árvore inteira, docs inclusive: o guia não pode ter CPF, CNPJ, telefone, e-mail real, 11+ dígitos nem caminho `/Users/`. Integrado em AT-013.
- [x] (Constraints) O `cmd` do gate não pode ter aspas duplas internas e roda da raiz com `bash -c`. A cópia por `git archive` não tem `.git` nem `sdd/features/`. → AT-011 e AT-012 são `test` com log em `evidence/F6_DOCS/`, fora do `cmd`, como na F5. Integrado em Verify Gate.

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

O gate só enxerga o que está commitado (`git archive HEAD`), então o Build commita na branch antes de rodar. `PUBLISH_GATE_MODE=ci` é necessário porque o modo padrão exige a camada privada de padrões. A suíte roda no piso (Python 3.9 do macOS, bash 3.2) e cobre AT-001 a AT-009, a parte de AT-010 que não depende da tag (posição da seção, linha de identificação = frontmatter em `tests/test_conversa.py`, `skill-lint --conversa`, versões fixadas da `sdd-build` e da `sdd-release`) e a parte de AT-013 que roda na cópia (499 testes, ≤ 500 linhas em `tests/test_skill_lint.py`, publish-gate ci).

Ficam fora do `cmd`, com log em `evidence/F6_DOCS/`, porque precisam de `.git` ou da tag: AT-011, AT-012, as versões de patch das outras 5 skills (AT-010, `check-versions.log`), os caminhos idênticos byte a byte (AT-013, `contratos-intactos.log`), AT-014 (sabotagem), a baseline vermelha e a Release (último Success Criterion).

---

## Out of Scope

- O guia em inglês; o catálogo gerado das skills; o porte do `workflow.md` do starter.
- A linha Lovable na tabela "onde roda"; a checagem de links externos (rede).
- Igualar os títulos da seção na `sdd-new-session` e na `sdd-iniciar-repo`; a seção nas 8 skills que não são de fase e ainda não a têm.
- Os docs novos na lista G5 do `scripts/publish-gate.sh` (o `scripts/` fica intocado).
- `docs/hooks.md`, `docs/review-contract.md`, `docs/decisoes-D1-D5.md` (item K: W1, W3, W2).
- A tabela WCAG e a leitura de `UX_REVIEW_*.md` anteriores (W5); o encadeamento e as classes D1–D5 (F9); o fail-open do `report-lint.py` (F7).
- A conferência do guia e das seções num agente real (pendência A-002 da F4).
- Regenerar o sdd-starter a partir do open; alterar o sdd-starter ou o repositório privado.

---

## Constraints

| Type | Constraint | Impact |
|---|---|---|
| Technical | Python ≥ 3.9 só com stdlib, rodado com `python3 -B`; testes sem rede | `tests/test_docs.py` não abre URL externa |
| Technical | `tests/test_agnostico.py` varre `.agents/skills/**`, `sdd/templates/**`, `AGENTS.md.tmpl` e `sdd/playbook.md` | As 7 seções e o `AGENTS.md.tmpl` sem nome de ferramenta de um agente só; "subagente" como conceito pode |
| Technical | Integridade do CI em `.agents/skills/`: nenhum Unicode invisível e nenhum `curl … \| sh` literal | Conferir os code points das 7 seções depois de escrever |
| Technical | G2 do publish-gate sobre a árvore inteira | Docs sem CPF/CNPJ/telefone/e-mail real (só `example.com/.org/.net`), sem 11+ dígitos e sem `/Users/<nome>/` |
| Technical | `tests/test_correcoes_w0.py` (`PROMESSA_VAZIA`) varre todo arquivo do `MANIFEST.txt` | Guia e roadmaps sem `/drive`, `build-report-guard`, `Step 1.5`, `slice 2`, `CONTEXTO de domínio`, `/bug-pipeline`; o roadmap cita `sdd-drive` pelo nome da skill |
| Technical | G3: `MANIFEST.txt` é allowlist nos dois sentidos, em ordem `LC_ALL=C` | Os 4 arquivos novos entram no mesmo commit; `sdd/features|handoffs|reports|reviews/` ficam fora |
| Technical | A camada da F4/F5 é contrato: o bloco comum nas 15 skills e as `FRASES` do `test_conversa`; linha de identificação "uma vez só, antes do Status", com a versão do frontmatter | A seção entra depois da camada e dos passos, sem tocar neles |
| Technical | `SKILL.md` ≤ 500 linhas | Folga mínima de 225 linhas (`sdd-release`, 275) |
| Technical | Decisões que não se reabrem: camada sempre ligada; Status `✅ ▶️ ⬜ ⏸️ ➖` com o nome da fase; pergunta com a recomendada primeiro, **não sei** e sem **Outro**; open como fonte canônica; KB em `sdd/kb/`; artefatos SDD desta família na branch `docs/` | O guia descreve as 5 primeiras como estão; a última é convenção deste repositório e não vai para o guia |
| Other | Push em `main` só com o OK do Roberto citando "sdd-open" na mesma mensagem, depois de PR com CI verde em ubuntu e macOS | A Release `v2.2.7` depende desse OK |

---

## Technical Context

| Aspect | Value | Notes |
|---|---|---|
| **Deployment Location** | `docs/pt-BR/guia-do-aluno.md`, `docs/roadmap.md`, `docs/pt-BR/roadmap.md` (novos); `docs/quickstart.md`, `docs/pt-BR/quickstart.md`, `docs/comparison.md`, `docs/pt-BR/comparison.md`; `README.md`, `README.pt-BR.md`; `AGENTS.md.tmpl`; `.agents/skills/sdd-{brainstorm,define,governanca,ux-review,design,build,release}/SKILL.md`; `tests/test_docs.py` (novo); `MANIFEST.txt` | Fontes: `sdd-starter/docs/guia-do-aluno.pt-BR.md`, `sdd-starter/docs/quickstart.pt-BR.md`, `sdd-starter/skills/sdd-release/SKILL.md` |
| **KB Domains** | nenhum | O open não tem `sdd/kb/` próprio |
| **IaC Impact** | None | O push em `main` publica a Release sozinho, porque toca `.agents/skills/**` e `AGENTS.md.tmpl` |
| **LLM Prompts** | false | `SKILL.md` e `AGENTS.md.tmpl` são instruções de orquestração lidas pelo agente de desenvolvimento; nenhum prompt de runtime de produto |

---

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|---|---|---|---|
| A-001 | Os 499 testes passam no piso em `7e19462` | O Build partiria de base vermelha | yes (handoff da F5: 499 OK no piso e no CI); reconferir no início do Build |
| A-002 | A regra de âncora do teste reproduz a do GitHub para títulos com acento e pontuação | Um link do sumário passa no teste e não abre no GitHub | yes; na página do guia da branch do PR, os 43 títulos têm a mesma âncora que o `ancora()` gera e as 10 do sumário abrem (`evidence/F6_DOCS/links-pr.log`) |
| A-003 | O agente lê a seção "Por que cada regra existe" antes de cortar uma regra | A seção vira só documentação para pessoas | no; não é executável em teste |
| A-004 | Nenhum teste existente compara o texto do bloco gerado a partir do `AGENTS.md.tmpl` | Um teste do `init`/`sync` ficaria vermelho | yes; `tests/test_sdd_open.py` confere marcadores e bytes fora do bloco, não o texto |

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---|---:|---|
| Problem | 3 | Cinco lacunas com o local (`AGENTS.md.tmpl:13`, `README.md:53`, `comparison.md:55`, as 2 skills que já têm a seção) |
| Users | 3 | Aluno, quem avalia, agente e mantenedor, com a dor de cada um |
| Goals | 3 | Arquivos, conteúdo mínimo, versões e verificações enumerados |
| Success | 2 | Todo critério mecânico é observável; a qualidade do texto para o aluno e a âncora no GitHub ficam para conferência humana |
| Scope | 3 | Arquivos tocados, os intocados byte a byte e o destino de cada corte |
| **Total** | **14/15** | |

Minimum to proceed: **12/15**.

---

## Open Questions

None - ready for Design.

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.1 | 2026-10-29 | SDD Design by RDD | Revisão de contexto fresco do DESIGN (H1, H2, M1, M2, M3, L2, L3): AT-005 só na célula do SDD Open; caminho de atualização real (`doctor` + apagar + `init`) no guia e correção P1 do passo 5 dos quickstarts; requisitos python3/bash e `--yes`; AT-001/AT-002/AT-003 ampliados; AT-011 com igualdade de texto; cobertura do gate reescrita; restrição `PROMESSA_VAZIA` |
| 1.0 | 2026-10-29 | SDD Define by RDD | Versão inicial a partir de `BRAINSTORM_F6_DOCS.md` |

---

## Next Step

Execute o **SDD Design by RDD**.
