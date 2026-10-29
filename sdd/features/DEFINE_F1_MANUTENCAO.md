# DEFINE: F1 Manutenção do sdd-open

> Rede de segurança do sdd-open antes da F2: testes de contrato dos 5 scripts, gate de versão por skill, Release automática com pacote e hash, e 3 padrões de PII brasileira no publish-gate.

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | F1_MANUTENCAO |
| **Date** | 2026-10-29 |
| **Author** | SDD Define by RDD (sessão com Roberto Dias Duarte) |
| **Status** | Ready for Design |
| **Clarity Score** | 14/15 |

---

## Problem Statement

O sdd-open tem 0 testes unitários e nenhuma Release publicada, e as frentes seguintes vão portar ~1.000 linhas de script (F2) e tocar as 13 skills (F4): sem uma rede de segurança, uma regressão no `verify-gate.sh`, nos linters ou no gerador `init/sync/doctor` passa despercebida, uma skill pode mudar sem subir de versão, e quem instala não tem pacote nem hash para conferir a versão que recebeu.

---

## Target Users

| User | Role | Pain Point |
|---|---|---|
| Mantenedor do sdd-open | Roberto e os agentes que executam F2–F6 | Mudança em script ou skill pode quebrar contrato documentado sem nenhum teste acusar |
| Quem instala o sdd-open | Usuário que clona ou baixa o framework | Não há Release com pacote e `SHA256SUMS.txt` para saber e conferir a versão recebida |

---

## Goals

| Priority | Goal |
|---|---|
| **MUST** | `tests/` na raiz com um teste por contrato documentado de `sdd/bin/verify-gate.sh`, `sdd/bin/report-lint.py`, `sdd/bin/skill-lint.py`, `sdd/bin/playbook-lint.sh` e `bin/sdd-open.sh`, rodando sem rede e com git isolado |
| **MUST** | Prova de que os testes discriminam: uma sabotagem por script registrada no BUILD_REPORT |
| **MUST** | `scripts/check-versions.py`: versão X.Y.Z por skill, coerência com `manifest.json`/`evals/cases.json`, bump obrigatório contra a última tag |
| **MUST** | Workflow de Release automática no push de `main` que toca o produto, com job de testes só leitura e job de publicação com `needs`, pacote `sdd-open-vX.Y.Z.tar.gz` e `SHA256SUMS.txt` |
| **MUST** | Nenhum script existente muda de comportamento; fixtures e exits do `verify-gate.sh` idênticos; todo arquivo novo no `MANIFEST.txt` |
| **SHOULD** | 3 padrões novos em `scripts/publish-gate-patterns.txt`: CPF com pontuação, CNPJ com pontuação, telefone BR sem `+` |
| **SHOULD** | Tag manual `v*` empurrada à mão também vira Release, sem tag automática duplicada no mesmo commit |
| **COULD** | O `publish-gate.yml` passa a rodar os testes e o check-versions em PR |

---

## Success Criteria

- [ ] `python3 -B -m unittest discover -s tests -p 'test_*.py'` sai 0 com o Python 3.9.6 do macOS e no `ubuntu-latest` do CI.
- [ ] Os 6 exits do `verify-gate.sh` (0, 2, 3, 4, 5, 64), `--print` e `--strict` têm, cada um, pelo menos 1 teste.
- [ ] 6 de 6 sabotagens (5 scripts existentes + `check-versions.py`) registradas no BUILD_REPORT com: a alteração, o nome do teste que ficou vermelho, e a reversão com a suíte verde de novo.
- [ ] `git diff 80d7887 -- sdd/fixtures sdd/bin bin scripts/publish-gate.sh` vazio ao fim da F1 (nenhum script existente alterado).
- [ ] O Verify Gate abaixo sai 0 com `--strict`.
- [ ] Depois do merge em `main`, `gh release list -R robertodiasduarte/sdd-open` mostra uma Release (a primeira automática é `v2.2.1`) com `sdd-open-vX.Y.Z.tar.gz` e `SHA256SUMS.txt`, e `shasum -a 256 -c SHA256SUMS.txt` sai 0 sobre o pacote baixado.

---

## Acceptance Tests

| ID | Pattern | Criterion (EARS) | Gate (`kind`) |
|---|---|---|---|
| AT-001 | Event-driven | **When** `python3 -B -m unittest discover -s tests -p 'test_*.py'` runs on a clean copy of the tree, the system **shall** exit 0 without network access and without reading the caller's `~/.gitconfig` | test |
| AT-002 | Event-driven | **When** `sdd/bin/verify-gate.sh` runs a DEFINE built for each state, the system **shall** return exit 0 (passing cmd), 2 (failing cmd), 3 (missing tool, rc 127), 4 (`manual-ux`), 5 (active clarification marker in the canonical bracketed form of `fragments/CLARIFY.md`, outside code fences) and 64 (missing block, invalid `kind`, file outside a git repo) | test |
| AT-003 | Event-driven | **When** `--strict` is given, `verify-gate.sh` **shall** map 3, 4 and 5 to exit 1 and keep 0, 2 and 64 unchanged | test |
| AT-004 | Event-driven | **When** `--print` is given, `verify-gate.sh` **shall** list `kind`, `cmd` and `pass_when` and exit 0 even when the DEFINE has an active clarification marker | test |
| AT-005 | Event-driven | **When** `pass_when` is `contains: TEXT`, `verify-gate.sh` **shall** exit 0 if the output contains TEXT and 2 otherwise | test |
| AT-006 | Event-driven | **When** `report-lint.py` reads a BUILD_REPORT whose `true` criteria cite an existing log starting with `$ ` and non-empty, a fresh-context evaluation in `sdd/reviews/`, or a dated `recibo:` under a `manual-ux` gate, the system **shall** exit 0 | test |
| AT-007 | Unwanted | **If** a `true` criterion in the BUILD_REPORT cites "deve funcionar"/"por raciocínio", a missing file or an empty log, **then** `report-lint.py` **shall** exit 1, and with no argument it **shall** exit 64 | test |
| AT-008 | Unwanted | **If** a SKILL.md has no frontmatter, a `name` different from its folder, or a `description` over 1024 characters, **then** `skill-lint.py` **shall** exit 1 | test |
| AT-009 | Event-driven | **When** `skill-lint.py` runs over the 13 real skills in `.agents/skills/`, the system **shall** exit 0 | test |
| AT-010 | Event-driven | **When** `playbook-lint.sh` lints `playbook-valido.md` and `playbook-delta-ok.md`, it **shall** exit 0; with `playbook-invalido.md` it **shall** exit 2; `--anti-collapse` from `playbook-valido.md` to `playbook-colapso.md` **shall** exit 1; `--self-test` **shall** exit 0 | test |
| AT-011 | Unwanted | **If** `bin/sdd-open.sh` receives an unknown verb or option, or `init` runs outside a git repository, **then** it **shall** exit 64 | test |
| AT-012 | Event-driven | **When** `init --yes --vendors claude,codex` runs in a fresh git repository, `bin/sdd-open.sh` **shall** create `sdd/templates`, `sdd/bin`, `sdd/playbook.md`, `sdd/config.yaml`, `.agents/skills/sdd-*` and `AGENTS.md`, and exit 0 | test |
| AT-013 | Event-driven | **When** `sync --yes` runs after a committed `init`, the system **shall** leave `git status --porcelain` empty and `sync --check` **shall** exit 0 | test |
| AT-014 | Unwanted | **If** a generated adapter copy is edited by hand after `sync`, **then** `sync --check` **shall** exit non-zero | test |
| AT-015 | State-driven | **While** `AGENTS.md` has user text outside the sdd-open markers, `sync --yes` **shall continue to** preserve that text byte for byte | test |
| AT-016 | Event-driven | **When** `doctor` runs in an initialized project, `bin/sdd-open.sh` **shall** end with a `RESULTADO:` line and exit 0 | test |
| AT-017 | Event-driven | **When** every skill has `metadata.version` in X.Y.Z, matching `manifest.json`/`evals/cases.json` versions, and every skill changed since `--base` has a greater version, `scripts/check-versions.py` **shall** exit 0 | test |
| AT-018 | Unwanted | **If** a skill changed since `--base` without a version bump, has a missing or malformed version, or disagrees with its `manifest.json`, **then** `check-versions.py` **shall** exit 1 naming the skill | test |
| AT-019 | Unwanted | **If** `--base-obrigatoria` is given and the base does not resolve to a commit, **then** `check-versions.py` **shall** exit 1 instead of falling back to structural checks | test |
| AT-020 | Unwanted | **If** a file in the tree contains a formatted CPF (`000.000.000-00`), a formatted CNPJ (`00.000.000/0000-00`) or a Brazilian phone without `+` (`(11) 91234-5678`), **then** `publish-gate.sh` **shall** exit non-zero naming the pattern, while a version string or date in the same tree **shall not** match | test |
| AT-021 | Event-driven | **When** the next-version step runs in a repository whose latest tag is `vX.Y.Z` and whose HEAD has no `v*` tag, it **shall** output `vX.Y.(Z+1)`, ordering tags by version so `v2.10.0` is above `v2.9.0` | test |
| AT-022 | Unwanted | **If** HEAD already carries a `v*` tag, **then** the next-version step **shall** output no new tag and the release run **shall** publish that existing tag instead of creating another | test |
| AT-023 | Unwanted | **If** the read-only `testes` job fails, **then** the `release` job **shall** not run (`needs: testes`), and only the `release` job **shall** hold `contents: write` | test |
| AT-024 | Event-driven | **When** a push to `main` touches `.agents/skills/**`, `bin/**`, `sdd/bin/**`, `sdd/templates/**`, `sdd/fixtures/**`, `sdd/playbook.md`, `sdd/config.example.yaml` or `AGENTS.md.tmpl` and the tests pass, the workflow **shall** publish a Release with `sdd-open-vX.Y.Z.tar.gz` and `SHA256SUMS.txt` that verifies with `shasum -a 256 -c` | smoke |
| AT-025 | Non-regression | The system **shall continue to** return exits 5, 0 and 64 for `DEFINE_FIXTURE_NEEDS_CLARIFICATION.md`, `DEFINE_FIXTURE_CONTROLE.md` and `DEFINE_FIXTURE_SEM_BLOCO.md` in G4 and in the inline CI check, with `sdd/fixtures/` unchanged | test |
| AT-026 | Unwanted | **If** a test's contract is broken on purpose in the script under test (sabotage), **then** at least one named test **shall** fail, and reverting the sabotage **shall** turn the suite green again | test |

---

## Clarifications

### Session 2026-10-29

- [x] (Done signal) O Brainstorm deixou "número mínimo de testes por script" como TBD → resolvido pela decisão 4 do Brainstorm (critério é cobertura de contrato + sabotagem, não quantidade); integrado em Success Criteria sem meta numérica de testes.
- [x] (Constraints) O `cmd` do Verify Gate não pode ter aspas duplas internas: `verify-gate.sh` só remove as aspas das pontas do valor e o roda com `bash -c` a partir da raiz do repositório (observado em `field()`) → `cmd` escrito sem aspas duplas internas; integrado em Verify Gate.
- [x] (Edge cases) Testes rodam dentro da cópia limpa, que não tem `.git` → todo teste que precisa de git monta o próprio repositório temporário; integrado em AT-001 e Assumptions.
- [x] (Edge cases) Exits reais conferidos antes de escrever os ATs: `playbook-lint.sh` 0/2 nas fixtures e `--self-test` 0; `report-lint.py` sem argumento 64; `skill-lint.py` 0 nas 13 skills; `sdd-open.sh` verbo inválido 64 e `init` fora de git 64 → integrados em AT-007, AT-009, AT-010, AT-011.

---

## Verify Gate

```yaml
verify_gate:
  kind: test
  cmd: "T=$(mktemp -d) && git archive HEAD | tar -x -C $T && PUBLISH_GATE_MODE=ci bash scripts/publish-gate.sh $T && cd $T && python3 -B -m unittest discover -s tests -p 'test_*.py'"
  pass_when: "exit 0"
  threshold: "—"
  manual_fallback: "—"
```

O gate só enxerga o que está commitado (`git archive HEAD`): o Build commita na branch antes de rodar. `PUBLISH_GATE_MODE=ci` porque o modo padrão exige a camada privada de padrões. AT-024 (Release publicada) é conferido depois do merge, fora deste gate, com `gh release view` e `shasum -a 256 -c`.

---

## Out of Scope

- `metadata.updated` e linha de identificação na primeira resposta das 13 skills (F4).
- `design-lint.py`, `handoff-lint.py` e `gate.sh` de documento (F4).
- `doctor` conferindo segredo já no histórico (F2, via `checar.sh`).
- Alterar comportamento de `verify-gate.sh`, `report-lint.py`, `skill-lint.py`, `playbook-lint.sh`, `bin/sdd-open.sh` ou `publish-gate.sh`.
- Migrar os checks inline do `publish-gate.yml` para `tests/`.
- Zips por skill na Release (frente do starter gerado, depois da F6).
- Ferramenta automática de mutação.
- Redesenhar CLI ou `config.yaml`; modo `briefs`; curadoria do playbook; alterar o sdd-starter; teste no Windows.

---

## Constraints

| Type | Constraint | Impact |
|---|---|---|
| Technical | bash 3.2, sem `declare -A`, sem zsh, sem symlink; Python ≥ 3.9 só com stdlib | Testes e scripts novos rodam no macOS de fábrica e no runner |
| Technical | Testes sem rede e sem a configuração git de quem roda (`GIT_CONFIG_GLOBAL` vazio, `GIT_CONFIG_NOSYSTEM=1`, `GIT_CEILING_DIRECTORIES`, `HOME` falso) | Resultado igual em qualquer máquina |
| Technical | `MANIFEST.txt` é allowlist nos dois sentidos (G3) | Todo arquivo novo declarado no mesmo commit; `sdd/features/`, `sdd/handoffs/`, `sdd/reports/` fora do commit |
| Technical | `verify-gate.sh` lê o `cmd` sem parser YAML | `cmd` sem aspas duplas internas |
| Technical | Nas skills nativas nenhum comando, condição, ordem de passo ou slot muda | Única mudança em skill: `version: "1.0.0"` na `sdd-auditoria-harness` |
| Other | Comandos remotos com `GIT_TERMINAL_PROMPT=0`; push em `main` só com OK explícito citando "sdd-open", após PR com CI verde | A Release (AT-024) depende desse OK |
| Other | Tag criada pelo `GITHUB_TOKEN` não dispara outro workflow | Cálculo da versão, tag e publicação no mesmo job `release` |

---

## Technical Context

| Aspect | Value | Notes |
|---|---|---|
| **Deployment Location** | `tests/` (novo), `scripts/check-versions.py` (novo), `.github/workflows/release.yml` (novo), `.github/workflows/publish-gate.yml`, `scripts/publish-gate-patterns.txt`, `MANIFEST.txt`, `.agents/skills/sdd-auditoria-harness/SKILL.md` | `tests/` fora de `sdd/` e `.agents/`: o `init` copia só `sdd/templates`, `sdd/bin` e `sdd/playbook.md` |
| **KB Domains** | N/A | Contratos vêm de `docs/verify-gate-contract.md` e das docstrings dos scripts |
| **IaC Impact** | New resources | Workflow GitHub Actions novo com permissão de escrita só no job de publicação; actions fixadas por SHA |
| **LLM Prompts** | false | Nenhum prompt de runtime: só scripts, testes e workflow |

---

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|---|---|---|---|
| A-001 | A última tag no remoto é `v2.2.0` e as skills alteradas desde ela já subiram de versão | A primeira Release automática não seria `v2.2.1` ou o check-versions reprovaria o merge | yes — `git ls-remote --tags` e diff de versões em 2026-10-29 |
| A-002 | `gh` vem instalado no `ubuntu-latest` e aceita `GITHUB_TOKEN` para `gh release create` | Publicação precisaria de action de terceiro | no |
| A-003 | Os 3 padrões novos de PII não acusam nada na árvore atual | publish-gate ficaria vermelho por falso positivo | yes — `git ls-files \| xargs grep -E` saiu 1 |
| A-004 | Saída de teste com falha que contenha "command not found" faria o `verify-gate.sh` devolver 3 em vez de 2 | Com `--strict` os dois saem ≠ 0; só o rótulo muda | yes — regra lida em `verify-gate.sh` |

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---|---:|---|
| Problem | 3 | Dor, quem sente e impacto concretos, com números medidos |
| Users | 3 | Mantenedor e quem instala, cada um com dor específica |
| Goals | 3 | MUST/SHOULD/COULD separados e confirmados no Brainstorm |
| Success | 2 | Todos observáveis; sem meta de tempo de execução da suíte |
| Scope | 3 | YAGNI e destinos (F2, F4) registrados |
| **Total** | **14/15** | |

Minimum to proceed: **12/15**.

---

## Open Questions

- Tempo máximo da suíte de testes no CI (não bloqueante: o Design fixa um `timeout-minutes` para o job).

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | 2026-10-29 | SDD Define by RDD | Initial version |
| 1.1 | 2026-10-29 | SDD Build by RDD | O critério AT-024 passa a incluir `sdd/fixtures/**` nos paths do produto: o Build achou que o `init` copia as fixtures para o projeto do usuário na 1ª instalação (`aplicar()` em `bin/sdd-open.sh`), então elas são parte do que se distribui |

---

## Next Step

Execute o **SDD Design by RDD**.
