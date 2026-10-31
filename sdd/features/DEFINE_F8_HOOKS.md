# DEFINE: F8 Hooks de git

> O `init` do sdd-open passa a instalar, com a confirmação única do plano, dois hooks de git versionados em `sdd/hooks/` (pre-commit com 5 regras + `report-lint` + o alarme da `sdd-higiene-dado`; pre-push de aviso) e, para o Claude Code, o adaptador que confere o `BUILD_REPORT` antes de gravar e barra o avaliador com a árvore suja.

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | F8_HOOKS |
| **Date** | 2026-10-30 |
| **Author** | SDD Define by RDD |
| **Status** | Ready for Design |
| **Clarity Score** | 14/15 |

---

## Problem Statement

O sdd-open não distribui hooks de git: nada recusa um commit com `AGENTS.md`/`CLAUDE.md` acima do teto da janela do agente, credencial em texto claro num `.json`/`.yml`, `sdd/playbook.md` que perde conhecimento, byte NUL em arquivo de texto, commit direto na branch padrão de um projeto com remoto ou `BUILD_REPORT` que o `report-lint` reprova. O único alarme existente (`sdd-higiene-dado`) grava em `.git/hooks/` e deixa de rodar, em silêncio, com qualquer `core.hooksPath`. No Claude Code, o `BUILD_REPORT` só é conferido depois de gravado e o avaliador pode ser despachado com trabalho não commitado, que ele pode apagar.

---

## Target Users

| User | Role | Pain Point |
|---|---|---|
| Aluno do Bravo (contador) | roda o `init` e commita pelo agente, em qualquer um dos 7 agentes | commits que estouram a janela, vazam credencial ou apagam conhecimento passam sem aviso; o alarme de CPF/CNPJ some se algo ligar `core.hooksPath` |
| Quem roda a `sdd-build` no Claude Code | constrói e despacha o avaliador | o relatório é gravado antes de ser conferido; o avaliador pode destruir trabalho não commitado |
| Roberto (mantenedor, F15) | leva o SDD privado para o open | precisa dos hooks do privado no open para substituí-lo (P4) |

---

## Goals

| Priority | Goal |
|---|---|
| **MUST** | `sdd/hooks/pre-commit` (bash 3.2): H6 branch padrão com remoto → H2 teto do arquivo de contexto → H5 byte NUL → H3 credencial em config (+ `gitleaks protect --staged` se instalado) → H4 anti-collapse do playbook → `report-lint.py --stdin` sobre cada `BUILD_REPORT_*.md` staged → alarme da `sdd-higiene-dado` quando `git config sdd.higieneDado` = `on`; roda todas, junta os achados numa só recusa (`🛑 [Hn] …`, `RESULTADO: COMMIT RECUSADO`, um `→` por classe), sucesso silencioso |
| **MUST** | `sdd/hooks/pre-push`: avisa `⚠️` quando o tip empurrado está N commits atrás de `origin/<default_branch>`; sai 0 sempre |
| **MUST** | `sdd-open.sh init`: copia `sdd/hooks/` (completa o que falta, nunca sobrescreve), `chmod +x`, mostra `+ core.hooksPath = sdd/hooks (…)` no plano e liga sob a confirmação única; **não** liga quando há outro `core.hooksPath` ou um `.git/hooks/pre-commit` que não é da higiene (imprime a linha para acrescentar); migra o alarme da higiene já instalado em `.git/hooks` ligando `sdd.higieneDado=on` e avisando |
| **MUST** | `doctor`: ✅ hooks ligados (`hooksPath` = `sdd/hooks`, os 2 arquivos com `-x`) ou ⚠️ nomeando o que falta e o comando |
| **MUST** | Slot `project.context_file_max_kb: 100` em `sdd/config.example.yaml`; vazio ou ausente vale 100; lista de arquivos de contexto por vendor em `bin/lib/vendors.sh` (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.cursorrules`) |
| **MUST** | `sdd-higiene-dado` 1.2.0: `alarme.sh` reconhece `core.hooksPath = sdd/hooks` com o dispatcher presente como seu (`instalar` liga `sdd.higieneDado=on`, `desinstalar` desliga); qualquer outro `hooksPath` ou `.git/hooks/pre-commit` alheio continua recusado (exit 2); sem `hooksPath`, grava `.git/hooks/pre-commit` como hoje |
| **MUST** | Adaptador do Claude Code (`init --vendors claude`/`sync`): fonte em `bin/adapters/claude/` (`sdd-report-guard.py`, `sdd-avaliador-guard.py`), cópias em `.claude/hooks/` com o cabeçalho `sdd-open:generated`, 2 entradas acrescentadas a `hooks.PreToolUse` de `.claude/settings.json` sem apagar chave alheia nem duplicar; JSON inválido aborta (66) sem escrever; `sync --check` acusa cópia ou entrada divergente; os guards falham abertos com aviso |
| **MUST** | `docs/hooks.md` + `docs/pt-BR/hooks.md` (as 5 regras, o dispatcher, `--no-verify` como limite, desligar, o adaptador), linkados do README e do README PT; roadmap EN/PT sem a linha "Hooks" (6 linhas) e `tests/test_docs.py` ajustado |
| **MUST** | Fixtures em `sdd/fixtures/hooks/` e testes dos dois lados para cada regra, para o `init`/`doctor`, para o `alarme.sh` e para os 2 guards; `tests/test_bash32.py` cobre `sdd/hooks/*`; `MANIFEST.txt` com todo arquivo novo |
| **SHOULD** | O guia do aluno (`docs/pt-BR/guia-do-aluno.md`, ficha da `sdd-higiene-dado`) diz onde o alarme fica nos dois casos (arquivo em `.git/` ou ligado nos hooks do projeto) |
| **COULD** | O `doctor` com vendor `claude` acusa `.claude/hooks/` ou as entradas do `settings.json` ausentes (`rode sync --vendors claude`) |

---

## Success Criteria

- [ ] Em repositório limpo, depois de `init --yes --vendors codex`: `git config core.hooksPath` imprime `sdd/hooks`; `sdd/hooks/pre-commit` e `pre-push` existem com `-x`; a saída do plano tem a linha `+ core.hooksPath = sdd/hooks`; com `--dry-run` nada é escrito e o `hooksPath` fica vazio.
- [ ] O pre-commit sai 1 com `🛑 [H2]`, `[H3]`, `[H4]`, `[H5]`, `[H6]` e `[REPORT]` nas 6 fixtures de recusa e 0 em silêncio na de controle; dois achados no mesmo commit saem juntos, com um só `RESULTADO: COMMIT RECUSADO`; `--no-verify` grava.
- [ ] H6 passa sem `refs/remotes/origin/<default_branch>` e recusa com ele; H2 lê o slot (1 KB → arquivo de 2 KB recusado) e usa 100 KB com o slot vazio; H3 passa `${VAR}`, `CHANGEME`, `example`, `<…>` e nunca imprime o valor; H4 recusa delete/rename e `playbook-colapso.md`, aceita `playbook-delta-ok.md`; H5 recusa NUL em `.md` e `.sh`, ignora `.png`.
- [ ] Com `sdd.higieneDado=on`, o pre-commit recusa CPF e CNPJ com DV válido, `.env`, `.pfx`, `.pem` com chave privada e planilha nova (mensagem da higiene, com `alarme.sh desinstalar` e sem `rm ` na última linha); desligado, só H2–H6 rodam. O primeiro commit depois do `init --yes` (com as fixtures de `sdd/fixtures/evidencia/`) sai 0.
- [ ] `alarme.sh instalar` com `hooksPath = sdd/hooks` e o dispatcher presente liga a config (sem escrever `.git/hooks/`), `desinstalar` desliga sem tocar em `sdd/hooks/pre-commit`, `.husky/_` segue exit 2; os 28 testes de `TestDeteccao`, `TestInstalacao` e `TestGeradores` continuam verdes sem alteração e a `TestCopiaGerada` afirma o modo hooks; `check-versions --base v2.2.8 --base-obrigatoria` verde com a higiene em 1.2.0.
- [ ] `init` não liga os hooks com `core.hooksPath = .husky/_` nem com `.git/hooks/pre-commit` alheio, imprime `bash sdd/hooks/pre-commit || exit 1` e termina `INSTALADO`; com o alarme da higiene em `.git/hooks`, liga `hooksPath` e `sdd.higieneDado=on`.
- [ ] `init --vendors claude` gera `.claude/hooks/sdd-report-guard.py`, `sdd-avaliador-guard.py` (compilam) e `.claude/settings.json` com 2 entradas em `hooks.PreToolUse`, preservando chaves existentes; `sync` de novo não duplica; `sync --check` acusa cópia editada; JSON inválido sai 66 sem escrever.
- [ ] `sdd-report-guard.py` nega (JSON com `permissionDecision: deny` e o texto do lint) um Write de `BUILD_REPORT_X.md` sem avaliação e um Edit que resulta nisso; silencia num Write do controle, num Edit com `old_string` ausente e num arquivo que não é `BUILD_REPORT_*.md`; com `report-lint.py` ausente ou payload ilegível emite `systemMessage` e sai 0.
- [ ] `sdd-avaliador-guard.py` nega o despacho quando o prompt contém `veredito` e a árvore está suja (lista os caminhos); silencia com árvore limpa ou prompt sem `veredito`.
- [ ] `pre-push` imprime `⚠️ … N commit(s) atrás de origin/main` quando atrás e sai 0; silencioso em dia ou sem o ref remoto.
- [ ] `doctor` imprime ✅ com os hooks ligados e ⚠️ com `hooksPath` ausente, `hooksPath` alheio ou arquivo sem `-x`, cada ⚠️ com o comando que resolve.
- [ ] `grep -nE 'mapfile|declare -A|\$\{[a-zA-Z_]+\^\^'` sem achado em `sdd/hooks/*` e nos scripts tocados; `tests/test_agnostico.py` verde (`PreToolUse` só em `bin/adapters/claude/`, no gerado, em `tests/` e em `docs/hooks*.md`); `skill-lint.py --conversa` 17/17; `playbook-lint.sh --self-test` 0; publish-gate `ci` verde (gitleaks, G2, G3, G5).
- [ ] 1 sabotagem por script novo ou alterado derruba um teste nomeado; os testes novos ficam vermelhos na `v2.2.8`; revisão de contexto fresco sem HIGH aberto; Release `v2.2.9` com `SHA256SUMS.txt` conferido por `shasum -a 256 -c`.

---

## Acceptance Tests

| ID | Pattern | Criterion (EARS) | Gate (`kind`) |
|---|---|---|---|
| AT-001 | Event-driven | **When** `sdd-open.sh init --yes --vendors <v>` runs in a repository with no `core.hooksPath` and no `.git/hooks/pre-commit`, the system **shall** copy `sdd/hooks/pre-commit` and `sdd/hooks/pre-push` with the execute bit, print `+ core.hooksPath = sdd/hooks` in the plan before applying, and set `core.hooksPath` to `sdd/hooks` in the repository config; **when** HEAD is on `project.default_branch` and `refs/remotes/origin/<branch>` exists, the final `→` of `RESULTADO: INSTALADO` **shall** contain `git switch -c` (how to commit the installation without hitting H6); otherwise it **shall not** | test |
| AT-002 | Unwanted | **If** `init` runs with `--dry-run`, or without `--yes` outside a terminal, **then** the system **shall** print the plan line and write nothing, leaving `core.hooksPath` unset and `sdd/hooks/` absent | test |
| AT-003 | Unwanted | **If** the repository already has a `core.hooksPath` other than `sdd/hooks`, or a `.git/hooks/pre-commit` without the `sdd-higiene-dado` mark, **then** `init` **shall** still copy `sdd/hooks/`, **shall not** change `core.hooksPath`, **shall** print a ⚠️ naming the existing hook and the line `bash sdd/hooks/pre-commit \|\| exit 1` to add to it, and **shall** end in `RESULTADO: INSTALADO` | test |
| AT-004 | Event-driven | **When** `.git/hooks/pre-commit` carries the `sdd-higiene-dado` mark, `init` **shall** set `core.hooksPath = sdd/hooks`, set `sdd.higieneDado = on`, leave the old file in place (now inert) and print a ⚠️ saying the alarm now runs through `sdd/hooks` | test |
| AT-005 | Event-driven | **When** `init` runs again on a project already installed, the system **shall** report `sdd/hooks` and `core.hooksPath` as already correct (`=`), **shall** recreate only a missing hook file (never overwrite an existing one) and **shall** keep `sdd.higieneDado` as it was | test |
| AT-006 | Event-driven | **When** `doctor` runs, the system **shall** print ✅ when `core.hooksPath` is `sdd/hooks` and both hooks exist with the execute bit, and otherwise one ⚠️ per cause (hooksPath unset → `rode init`; hooksPath foreign → the line to add; file missing → `rode init`; file without execute bit → `chmod +x sdd/hooks/<nome>`) | test |
| AT-007 | Unwanted | **If** a staged file named `AGENTS.md`, `CLAUDE.md`, `GEMINI.md` or `.cursorrules` (at any depth) has a blob size above `project.context_file_max_kb` KB, **then** the pre-commit **shall** exit 1 with `🛑 [H2] <arquivo>: <bytes> bytes (teto <N> KB)`; with the slot empty, absent or not a positive integer the limit **shall** be 100 KB; a file at or below the limit **shall** pass | test |
| AT-008 | Unwanted | **If** a staged `.json`, `.yaml`, `.yml`, `.toml`, `.ini`, `.cfg`, `.conf` or `.env*` file contains a key matching the credential regex (`password`, `passwd`, `senha`, `secret`, `token`, `key`, `api_key`, `access_key`, with optional `api|access|auth|db|ftp|smtp|client|private` prefix) followed by a quoted value of 6+ characters — or, in `.env*` files, an unquoted `KEY=value` with 6+ non-space characters —, **then** the pre-commit **shall** exit 1 with `🛑 [H3] <arquivo>: credencial em texto claro (chave <nome>)` and **shall not** print the value; values containing `${`, `{{`, `<`, `changeme`, `example`, `xxx` or `***` (case-insensitive) and version numbers (`^2.0.0`, `~1.4.2`, `1.2.3`) **shall** pass; `package-lock.json`-style `"parse-passwd": "^1.0.0"` and `"token": "^2.0.0"` **shall** pass; a placeholder or a version **before** a real credential in the same file **shall not** make the file pass (every occurrence is checked) | test |
| AT-009 | Event-driven | **When** a `gitleaks` executable is on `PATH`, the pre-commit **shall** run `gitleaks protect --staged --redact` and treat exit 1 as `🛑 [H3] gitleaks: …`; **when** it is absent, the rule **shall** be skipped silently; any other exit **shall** print ⚠️ and pass | test |
| AT-010 | Unwanted | **If** `sdd/playbook.md` is staged as deleted or renamed, **then** the pre-commit **shall** exit 1 with `🛑 [H4]`; **if** it is staged as modified and `sdd/bin/playbook-lint.sh --anti-collapse <HEAD> <staged>` exits 1, **then** it **shall** exit 1 with `🛑 [H4]` and the lint's lines; `playbook-delta-ok.md` over `playbook-valido.md` and a newly added playbook **shall** pass; with `playbook-lint.sh` absent it **shall** print ⚠️ and pass | test |
| AT-011 | Unwanted | **If** a staged file with a text extension (`.md`, `.sh`, `.py`, `.js`, `.ts`, `.json`, `.yaml`, `.yml`, `.toml`, `.txt`, `.css`, `.html`, `.sql`, `.php`, or no extension with a shebang) contains a NUL byte, **then** the pre-commit **shall** exit 1 with `🛑 [H5] <arquivo>: byte NUL em arquivo de texto`; `.png`, `.pdf`, `.zip` and other binary extensions **shall** be ignored | test |
| AT-012 | Unwanted | **If** `HEAD` is on `project.default_branch` (default `main`) **and** `refs/remotes/origin/<branch>` exists, **then** the pre-commit **shall** exit 1 with `🛑 [H6] commit direto em <branch>` and a `→ [H6]` that gives `git switch -c <nome>` (the staged work goes along) before naming `sdd-new-session`; on another branch, on a detached HEAD, with a different `default_branch` in `sdd/config.yaml`, or without the remote ref, it **shall** pass | test |
| AT-013 | Unwanted | **If** a staged `BUILD_REPORT_<F>.md` whose path has no `sdd/fixtures/` nor `sdd/templates/` component fails `python3 sdd/bin/report-lint.py --stdin <caminho>` fed with the **staged** content (`git show :<caminho>`), **then** the pre-commit **shall** exit 1 with `🛑 [REPORT] <arquivo>` followed by the lint's `🛑` lines; a passing report **shall** pass; a `BUILD_REPORT_*.md` under `sdd/fixtures/` or `sdd/templates/` (the fixtures and the `BUILD_REPORT_TEMPLATE.md` that `init` copies) **shall** be skipped silently, so the first commit after `init --yes` exits 0; with `python3` or `sdd/bin/report-lint.py` absent it **shall** print ⚠️ naming the skipped rule and pass | test |
| AT-014 | State-driven | **While** `git config sdd.higieneDado` is `on` and `.agents/skills/sdd-higiene-dado/scripts/pre-commit.sh` exists, the pre-commit **shall** run it last and propagate its refusal (CPF/CNPJ with valid check digit, `.env`, `.pfx`, `.p12`, `.pem` with private key, new spreadsheet), with the alarm's own message, whose last line **shall** contain `alarme.sh desinstalar` and **shall not** contain `rm ` (under `core.hooksPath` the legacy `rm <HOOK>` line would name the dispatcher); **while** the config is unset or not `on`, it **shall not** run it; with the config `on` and the script absent it **shall** print ⚠️ and pass | test |
| AT-015 | Event-driven | **When** two or more rules fail in the same commit, the pre-commit **shall** print every `🛑 [..]` line, a single `RESULTADO: COMMIT RECUSADO`, one `→` per failed class (the hygiene alarm counts as the class `[alarme]`) and one final `→` about `git commit --no-verify` after checking; **when** only the alarm fails, the header **shall** name the alarm and no empty findings block **shall** be printed; **when** no rule fails, it **shall** exit 0 and print nothing | test |
| AT-016 | Event-driven | **When** `pre-push` receives a ref whose local sha is N > 0 commits behind `refs/remotes/<remote>/<default_branch>`, it **shall** print `⚠️ <branch> está N commit(s) atrás de <remote>/<default_branch>` to stderr and exit 0; up to date, without the remote ref, or on a deletion (zero sha) it **shall** print nothing and exit 0 | test |
| AT-017 | Event-driven | **When** `core.hooksPath` is `sdd/hooks` and `sdd/hooks/pre-commit` carries the dispatcher mark, `alarme.sh verificar` **shall** say the alarm runs through the project's hooks and whether it is on; `instalar` **shall** set `sdd.higieneDado = on`, write nothing under `.git/hooks/` and exit 0; `desinstalar` **shall** unset it, remove the legacy `$(git rev-parse --git-common-dir)/hooks/pre-commit` only if it carries the higiene mark, leave `sdd/hooks/pre-commit` untouched (the test asserts it still exists), and exit 0 | test |
| AT-018 | Unwanted | **If** `core.hooksPath` is set to anything else (e.g. `.husky/_`), or to `sdd/hooks` without the dispatcher mark in `sdd/hooks/pre-commit`, **then** `alarme.sh verificar`/`instalar`/`desinstalar` **shall** refuse with exit 2 and the line to add by hand, as today | test |
| AT-019 | Non-regression | Without any `core.hooksPath`, `alarme.sh` **shall continue to** install, verify and remove `.git/hooks/pre-commit` exactly as in 1.1.1; the 28 tests of `TestDeteccao`, `TestInstalacao` and `TestGeradores` in `tests/test_alarme.py` **shall continue to** pass unchanged, and `TestCopiaGerada` (which runs `init --vendors claude`, now turning the hooks on) **shall** be rewritten to assert the hooks mode (`sdd.higieneDado` = `on`, nothing written under `.git/hooks/`, the generated copy's `verificar` naming `sdd/hooks`), with `git diff v2.2.8 -- tests/test_alarme.py` touching only that class and the new class | test |
| AT-020 | Event-driven | **When** `init --vendors claude` or `sync --vendors claude` runs, the system **shall** write `.claude/hooks/sdd-report-guard.py` and `.claude/hooks/sdd-avaliador-guard.py` rendered from `bin/adapters/claude/` with the 2 `sdd-open:generated` lines, and add to `.claude/settings.json` two `hooks.PreToolUse` entries (matcher `Write\|Edit\|MultiEdit` → `python3 "$CLAUDE_PROJECT_DIR/.claude/hooks/sdd-report-guard.py"` with `timeout: 10`; matcher `Agent\|Task` → `python3 "$CLAUDE_PROJECT_DIR/.claude/hooks/sdd-avaliador-guard.py"`), keeping every other key and entry of the file | test |
| AT-021 | Unwanted | **If** `.claude/settings.json` is not valid JSON, or its top is not an object, or `hooks` is not an object, or `hooks.PreToolUse` is not a list, **then** the system **shall** exit 66 naming the problem and write nothing (checked in the plan, before `sdd/`, skills or `core.hooksPath` are touched); **if** `python3` is absent, **then** it **shall** exit 64 before any write; **when** the two entries already exist, a second `sync` **shall** not duplicate them and `sync --check` **shall** report `EM DIA`; an edited copy in `.claude/hooks/` or a missing entry **shall** make `sync --check` exit 1 naming it | test |
| AT-022 | Unwanted | **If** the hook payload is a `Write` of a file whose basename matches `BUILD_REPORT_*.md` and `report-lint.py --stdin <file_path>` exits 1 on its `content`, or an `Edit`/`MultiEdit` whose simulated result (`old_string` → `new_string`, `replace_all` honoured) exits 1, **then** `sdd-report-guard.py` **shall** print `{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":<lint output>}}` and exit 0 | test |
| AT-023 | Event-driven | **When** the payload targets another file or a `BUILD_REPORT_*.md` under `sdd/fixtures/` or `sdd/templates/`, is a Write whose content passes the lint, or is an Edit whose `old_string` is absent from the file, `sdd-report-guard.py` **shall** print nothing and exit 0; **when** the payload is unreadable, `report-lint.py` is missing or exits 64 or above, it **shall** print `{"systemMessage":"⚠️ …"}` and exit 0 (fail-open) | test |
| AT-024 | Unwanted | **If** the payload's `tool_input.prompt` (or `description`) contains `veredito` (case-insensitive) and `bash sdd/bin/avaliador-guard.sh` exits 1, **then** `sdd-avaliador-guard.py` **shall** print a `deny` with the guard's output as reason; with exit 0 it **shall** print nothing; with exit 2 or 64 it **shall** print a `systemMessage`; a prompt without `veredito` **shall** never run the guard | test |
| AT-025 | Event-driven | **When** `tests/test_agnostico.py` runs, it **shall** pass with `bin/adapters/claude/` outside its scope; **when** `tests/test_bash32.py` runs, it **shall** also scan `sdd/hooks/pre-commit` and `sdd/hooks/pre-push` and find no bashism | test |
| AT-026 | Event-driven | **When** `tests/test_docs.py` runs, it **shall** find `docs/hooks.md` and `docs/pt-BR/hooks.md` linked from `README.md` and `README.pt-BR.md`, every link in them resolving, the string `--no-verify` in both, and the roadmap tables with 6 rows and no "Hooks" row | test |
| AT-027 | Event-driven | **When** `scripts/check-versions.py --base v2.2.8 --base-obrigatoria` runs, it **shall** pass with `sdd-higiene-dado` at `1.2.0` in `SKILL.md` (frontmatter and identification line), `manifest.json` and `CHANGELOG.md` | test |
| AT-028 | Non-regression | The system **shall continue to** pass the 630 existing tests, `tests/test_sdd_open.py` (init idempotent, `sync --check` in day, Gemini merge), `skill-lint.py --conversa` on the 17 skills, `playbook-lint.sh --self-test`, and `publish-gate.sh` in `ci` mode (G1 gitleaks over the fixtures, G2, G3 `MANIFEST.txt`, G5) | test |
| AT-029 | Unwanted | **If** one of the 7 scripts (`pre-commit`, `pre-push`, `sdd-open.sh`, `vendors.sh`, `alarme.sh`, `sdd-report-guard.py`, `sdd-avaliador-guard.py`) is sabotaged (a rule removed or inverted), **then** at least one named test **shall** fail, and `git checkout` **shall** turn the suite green again, evidenced in `evidence/F8_HOOKS/sabotagem.log` | test |
| AT-030 | Event-driven | **When** the new tests run against the `v2.2.8` tree (`sdd/hooks/`, `bin/adapters/` and the alarm changes absent), they **shall** fail, evidenced in `evidence/F8_HOOKS/baseline.log` | test |

---

## Clarifications

### Session 2026-10-30

- [x] (Scope) D3: hooks distribuídos e ligados pelo `init`, dentro do plano, sob a confirmação única (BRAINSTORM, decisões 1 e 2). Integrado em Goals e AT-001 a AT-006.
- [x] (Integrations) D10: dispatcher chama o `pre-commit.sh` da higiene quando `sdd.higieneDado=on`; `alarme.sh` reconhece `sdd/hooks` com a marca do dispatcher; `init` migra o alarme já instalado (BRAINSTORM, decisões 3 e 4). Integrado em AT-004, AT-014, AT-017 a AT-019.
- [x] (Data model) D11: slot `project.context_file_max_kb`, default 100 (BRAINSTORM, decisão 5). Integrado em AT-007.
- [x] (Integrations) E6: fonte em `bin/adapters/claude/`, cópias em `.claude/hooks/`, merge de 2 entradas no `.claude/settings.json`; guards em Python, fail-open com aviso; despacho do avaliador reconhecido por `veredito` no prompt (BRAINSTORM, decisões 6 a 8). Integrado em AT-020 a AT-024.
- [x] (Constraints) Release `v2.2.9` automática; o aviso da mudança de comportamento fica na linha do plano (AT-001), na recusa (AT-015) e no `doctor` (AT-006) (BRAINSTORM, decisão 9).
- [x] (Edge cases) H6 só com `refs/remotes/origin/<default_branch>` presente (BRAINSTORM, decisão 10). Integrado em AT-012.
- [x] (Edge cases) **Achado do Define:** o publish-gate roda `gitleaks detect` sobre a árvore inteira (G1), e o `generic-api-key` do gitleaks casa `password`/`token`/`secret` seguido de valor com entropia alta. Fixtures de credencial (H3) e de CPF/CNPJ (higiene) são montadas em tempo de execução pelo teste, nunca gravadas em `sdd/fixtures/hooks/`; a fixture em disco do H3 leva só placeholders (`${VAR}`, `CHANGEME`), que são o caso que **passa**. Integrado em Constraints.
- [x] (Edge cases) Na migração (AT-004), o `.git/hooks/pre-commit` da higiene fica no lugar, inerte (o git o ignora com `hooksPath`): apagar arquivo do usuário não é papel do `init`; o `desinstalar` da higiene remove-o se ainda estiver lá (AT-017).
- [x] (Edge cases) "Marca do dispatcher": uma linha fixa de comentário em `sdd/hooks/pre-commit` (`# sdd-open: dispatcher de hooks (pre-commit)`) que o `alarme.sh` procura; `hooksPath = sdd/hooks` sem ela é OUTRO (AT-018). Evita que um `sdd/hooks/pre-commit` escrito à mão seja tratado como nosso.
- [x] (Edge cases) `core.hooksPath` relativo (`sdd/hooks`) é resolvido pelo git a partir da raiz da worktree onde o hook roda: vale em toda worktree do projeto sem caminho absoluto (é como o privado usa `.githooks`). A-003. Um `hooksPath` absoluto que resolve (links simbólicos inclusos, como `/tmp` → `/private/tmp` no macOS) para `<raiz>/sdd/hooks` também é "nosso", no `init`/`doctor` e no `alarme.sh` (ciclo 1 do avaliador, LOW 5); idem as variantes relativas que o git aceita, `sdd/hooks/` e `./sdd/hooks` (ciclo 2, LOW 2).
- [x] (Edge cases) O pre-commit do open usa o conteúdo **staged** (`git show :<f>`/`git cat-file -s :<f>`), não o do disco: o commit grava o staged.
- [x] (UX flow) Não há tela: a interface é a saída do `init`, do `doctor`, do hook e dos guards. Cada mensagem segue `docs/cli-conventions.md` (símbolo + palavra, `RESULTADO:`, `→`) e a `sdd-ux-review` revisa esse texto.
- [x] (Terminology) `[REPORT]` é a classe da regra do `BUILD_REPORT` no pre-commit (não é item do PORTE; as classes H2–H6 seguem a numeração do PORTE §5.2 e H1 — "distribuir hooks" — é a própria entrega).
- [x] (Constraints) `sdd-iniciar-repo` continua chamando `bash .git/hooks/pre-commit` antes do 1º commit: nesse momento não há `init` nem `sdd/hooks`, e o `alarme.sh` grava em `.git/hooks` como hoje (AT-019). O texto dela não muda.
- [x] (Constraints) O `cmd` do gate roda numa cópia por `git archive HEAD`, sem `.git`: AT-029 (sabotagem), AT-030 (baseline), `check-versions` e a conferência do `init` num projeto real ficam fora do `cmd`, com log em `evidence/F8_HOOKS/`.

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

- Os 11 cortes YAGNI do brainstorm: aviso da branch `dev` no pre-push; item ⑥ (PHP); cores ANSI; subcomando `hooks ligar/desligar`; `SDD_HOOKS=off`; migrar husky/lefthook; outros hooks (`commit-msg`, `post-checkout`); `sync` regenerando `sdd/hooks/`; teto por vendor; guard do avaliador por nome de subagente; data de corte para relatório antigo.
- Encadeamento entre fases, `exit 40 AGUARDANDO_HUMANO` e classes D1–D5 (F9); revisão adversarial e registry (F10/F11); `RESUMO_ETAPA.md` com `/adversarial-review` (F10).
- Regenerar o sdd-starter; alterar o sdd-starter ou o repositório privado.
- Projeto real de aluno como amostra (opção recusada; a migração é provada em repositório temporário).

---

## Constraints

| Type | Constraint | Impact |
|---|---|---|
| Technical | bash ≥ 3.2 e Python ≥ 3.9 só com stdlib, `python3 -B`; testes sem rede; só bash e git para commitar | Nada de `mapfile`, `declare -A`, `${x^^}`; `rm -rf` só com `"${X:?}"`; `python3` opcional no hook, com ⚠️ |
| Technical | P2 (`tests/test_agnostico.py`): `PreToolUse`, `subagent_type`, `tool_input` só em `bin/adapters/claude/`, no gerado em `.claude/`, em `tests/` e em `docs/hooks*.md`; nunca em `.agents/skills/`, `sdd/templates/`, `sdd/bin/`, `AGENTS.md.tmpl` ou `sdd/playbook.md` | A `sdd-higiene-dado` fala de "hooks do projeto", não do Claude Code |
| Technical | G1 do publish-gate (`gitleaks detect` na árvore inteira, **inclusive `tests/`**) e G2 (`publish-gate-patterns.txt`) | Credencial que deve reprovar o H3 é gerada em execução (alfanumérico aleatório ≥ 10) ou é literal de baixa entropia sem dígito; CPF/CNPJ pelo `dv_cpf`/`dv_cnpj`; fixture em disco só com placeholder; `gitleaks detect --source tests --no-git --exit-code 1` e o mesmo sobre `sdd/fixtures/hooks` saem 0 antes do commit (`evidence/F8_HOOKS/gitleaks-tests.log`); sem `/Users/<nome>/` nem 11+ dígitos |
| Technical | G3: `MANIFEST.txt` em ordem `LC_ALL=C`; `git add` por nome | `sdd/hooks/*`, `bin/adapters/claude/*`, `sdd/fixtures/hooks/*`, `docs/hooks.md`, `docs/pt-BR/hooks.md` e os testes novos entram no mesmo commit |
| Technical | `init` nunca sobrescreve skill instalada, `sdd/bin/*` nem `sdd/hooks/*`; `sync` nunca escreve em `sdd/`; merge do `.gemini/settings.json` e os 20 testes de `test_sdd_open.py` intactos | O merge do `.claude/settings.json` é função nova em `merge.sh`, ao lado da do Gemini |
| Technical | `sdd-higiene-dado`: detecções e exits do `pre-commit.sh` não mudam; a única mensagem que muda é a linha "Para desinstalar", que passa a citar `alarme.sh desinstalar` quando há `core.hooksPath` (sem ele, continua `rm <HOOK>`); `alarme.sh` mantém 0/1/2; `SKILL.md` ≤ 500 linhas, camada de conversa e seção "Como falar" intactas | Bump 1.1.1 → 1.2.0 em `SKILL.md`, `manifest.json`, `evals/cases.json`, `CHANGELOG.md`; `references/` atualizadas onde citam `.git/hooks` |
| Technical | `report-lint.py` (32 + F7), `verify-gate.sh`, `avaliador-guard.sh`, `playbook-lint.sh` não mudam: o hook e os guards só os chamam | Saída deles reaproveitada nas mensagens |
| Technical | Camada de conversa (F4/F5) e "Por que cada regra existe" (F6) são contrato | Texto novo na `sdd-higiene-dado` entra nos passos e nas referências, sem tocar no bloco comum |
| Technical | `docs/roadmap.md` e PT passam a 6 linhas; `test_docs.py` (`ROADMAP`) perde "Hooks" | Linha removida nas 2 línguas no mesmo commit |
| Other | Push em `main` só com o OK do Roberto citando "sdd-open", depois de PR com CI verde em ubuntu e macOS | A Release `v2.2.9` depende desse OK |

---

## Technical Context

| Aspect | Value | Notes |
|---|---|---|
| **Deployment Location** | novos: `sdd/hooks/pre-commit`, `sdd/hooks/pre-push`, `bin/adapters/claude/sdd-report-guard.py`, `bin/adapters/claude/sdd-avaliador-guard.py`, `sdd/fixtures/hooks/`, `docs/hooks.md`, `docs/pt-BR/hooks.md`, `tests/test_hooks.py`, `tests/test_claude_adapter.py`; alterados: `bin/sdd-open.sh`, `bin/lib/vendors.sh`, `bin/lib/merge.sh`, `sdd/config.example.yaml`, `.agents/skills/sdd-higiene-dado/{SKILL.md,manifest.json,CHANGELOG.md,scripts/alarme.sh,references/*.md}`, `docs/roadmap.md` + PT, `README.md`, `README.pt-BR.md`, `docs/pt-BR/guia-do-aluno.md`, `tests/{test_alarme,test_sdd_open,test_docs,test_bash32,test_agnostico}.py`, `MANIFEST.txt` | Fontes no privado (`origin/main` `abd322b4e`, só leitura): `.githooks/pre-commit`, `pre-push`, `claude-avaliador-guard.py`, `resulting_content()` de `claude-build-report-guard.py`, `scripts/gates/gate-nul-no-fonte.sh`, bloco `hooks.PreToolUse` de `.claude/settings.json` |
| **KB Domains** | nenhum | O open não tem `sdd/kb/` próprio |
| **IaC Impact** | None | O push em `main` publica a Release sozinho (`bin/**`, `sdd/fixtures/**`, `sdd/config.example.yaml`, `.agents/skills/**`); nota: `sdd/hooks/**` não está nos `paths:` do `release.yml`, mas toda entrega da F8 toca `bin/**` |
| **LLM Prompts** | false | Hooks de git, scripts de instalação e guards de ferramenta; nenhum texto vai para um LLM em runtime |

---

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|---|---|---|---|
| A-001 | Os 630 testes passam no piso em `1d225e5` | O Build partiria de base vermelha | yes; reconferido no início desta sessão |
| A-002 | O Claude Code lê `hooks.PreToolUse[]` de `.claude/settings.json` como `{matcher, hooks:[{type:"command", command, timeout}]}`, chama o comando com o JSON do evento no stdin (`tool_name`, `tool_input`, `cwd`) e honra `hookSpecificOutput.permissionDecision = deny` e `systemMessage` | O adaptador gerado não negaria nada | yes; é o formato em uso no `.claude/settings.json` e nos 2 guards do privado |
| A-003 | `core.hooksPath` relativo é resolvido pelo git a partir da raiz da worktree em que o hook roda, em toda worktree | Em worktree secundária o hook não rodaria | yes; é o uso do privado (`.githooks`) em worktrees, e o teste AT-001/AT-012 cobre worktree |
| A-004 | O `generic-api-key` do gitleaks 8.30 não casa placeholder de baixa entropia (`${VAR}`, `CHANGEME`) | A fixture de H3 em disco reprovaria o G1 | yes; medido pela revisão do DESIGN (`AVAL-DESIGN-gitleaks-fixtures.log`: exit 0); um literal de alta entropia num teste, ao contrário, reprova (`AVAL-DESIGN-gitleaks-literal-teste.log`) |
| A-005 | `git diff --cached --name-only -z --diff-filter=ACM` e `git cat-file -s :<f>` bastam para H2/H3/H5 sem ler o disco | O hook conferiria o arquivo errado quando staged ≠ disco | yes; é o que o privado e a higiene fazem |

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---|---:|---|
| Problem | 3 | Seis classes de commit sem guarda e o alarme que some com `hooksPath`, com a fonte do privado lida |
| Users | 3 | Aluno contador, quem constrói no Claude Code, o mantenedor da F15 |
| Goals | 3 | Cada hook, regra, comando e versão com interface e exits |
| Success | 3 | Todo critério é um exit, uma linha de saída, uma config do git ou um arquivo |
| Scope | 2 | O formato dos hooks do Claude Code (A-002) é inferido do uso no privado, não de contrato publicado |
| **Total** | **14/15** | |

Minimum to proceed: **12/15**.

---

## Open Questions

None - ready for Design.

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.4 | 2026-10-30 | SDD Build by RDD | Ciclo 2 da revisão do build (`AVALIACAO_F8_HOOKS_20261030-ciclo2.md`, PASS com 2 LOW): AT-008 olha toda ocorrência do arquivo (placeholder antes não absolve); `core.hooksPath` `sdd/hooks/` e `./sdd/hooks` contam como nosso (Clarifications) |
| 1.3 | 2026-10-30 | SDD Build by RDD | Ciclo 1 da revisão do build (`AVALIACAO_F8_HOOKS_20261030-ciclo1.md`): AT-021 confere a forma do `settings.json` no plano (MEDIUM); AT-008 cobre `.env` sem aspas e deixa passar número de versão (LOW 2 e 3); AT-015 com a classe `[alarme]` e sem bloco vazio (LOW 4); `core.hooksPath` absoluto por link simbólico é nosso (LOW 5, em Clarifications); união de vendors sem `paste` (LOW 6) |
| 1.2 | 2026-10-30 | SDD Design by RDD | Revisão de contexto fresco do DESIGN (`REVISAO_DESIGN_F8_HOOKS_20261030.md`), 5 ajustes aceitos: AT-013/AT-023 pulam `BUILD_REPORT_*.md` sob `sdd/fixtures/`; AT-019 com 28 intactos e `TestCopiaGerada` reescrita; AT-014/AT-017 com a linha sem `rm` e o dispatcher intocado pelo `desinstalar`; Constraints G1 sobre `tests/`; AT-012/AT-001 com `git switch -c`; A-004 validada |
| 1.1 | 2026-10-30 | SDD Design by RDD | Constraint da higiene: a linha "Para desinstalar" do `pre-commit.sh` muda quando há `core.hooksPath` (Decision 4 do DESIGN); `evals/cases.json` no bump |
| 1.0 | 2026-10-30 | SDD Define by RDD | Versão inicial a partir de `BRAINSTORM_F8_HOOKS.md`, com o achado do gitleaks (G1) sobre as fixtures |

---

## Next Step

Execute o **SDD Design by RDD**.
