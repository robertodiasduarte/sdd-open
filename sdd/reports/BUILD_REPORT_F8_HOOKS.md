# BUILD REPORT: F8 Hooks de git

> Implementation report for F8 Hooks de git

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | F8_HOOKS |
| **Date** | 2026-10-30 |
| **Author** | SDD Build by RDD |
| **BRAINSTORM** | `sdd/features/BRAINSTORM_F8_HOOKS.md` |
| **DEFINE** | `sdd/features/DEFINE_F8_HOOKS.md` (v1.4) |
| **DESIGN** | `sdd/features/DESIGN_F8_HOOKS.md` (v1.3) |
| **UX REVIEW** | `sdd/reviews/UX_REVIEW_F8_HOOKS.md` (9 MUST de texto de saída) |
| **Status** | Complete |

- **Branch:** `feat/f8-hooks`, sobre `1d225e5` (= `v2.2.8`).
- **Commits:** `6a238d2` — build (38 tarefas do manifest, 39 arquivos); `938ce47` — notas do ciclo 1 da revisão de contexto fresco do build (1 MEDIUM, 5 LOW); `7c640eb` — notas do ciclo 2 (2 LOW).
- **Escopo:** 39 arquivos do produto (13 novos, 26 alterados); números do `git diff --stat v2.2.8 HEAD` (`sdd/reports/evidence/F8_HOOKS/escopo.log`).
- **Fontes (só leitura):** `origin/main` do repositório privado (`abd322b4e`): `.githooks/pre-commit`, `pre-push`, `claude-avaliador-guard.py`, `resulting_content()` de `claude-build-report-guard.py`, `scripts/gates/gate-nul-no-fonte.sh` e o bloco de hooks do `.claude/settings.json`. Nada foi alterado lá.
- **Revisões de contexto fresco:**
  - do DESIGN, antes do build: `sdd/reviews/REVISAO_DESIGN_F8_HOOKS_20261030.md` (NEEDS_WORK: 3 HIGH, 2 MEDIUM, 10 LOW; 14 aplicadas, 1 rebatida por escopo);
  - do build: `sdd/reviews/AVALIACAO_F8_HOOKS_20261030-ciclo1.md` (NEEDS_WORK, 1 MEDIUM, 5 LOW, sobre `6a238d2`; 54 sondas, 30/30 ATs provados) e `…-ciclo2.md` (PASS, 2 LOW, sobre `938ce47`; 43 sondas). As correções do ciclo 2 não passaram por um 3º avaliador: a `sdd-build` limita a 2 ciclos, e cada uma tem teste vermelho em `938ce47` (`baseline-ciclo2.log`).

---

## Mode Selection

| Signal | Observation |
|---|---|
| Manifest files | 38 linhas: 14 novos (2 hooks, 2 guards, 5 fixtures, 2 testes, 2 docs, 1 workflow tocado) e 24 alterados |
| Cross-file coupling | Alto: o hook, o `init`, o `alarme.sh` e os guards se reconhecem por marcas e configs (`# sdd-open: dispatcher…`, `sdd.higieneDado`, `core.hooksPath`) e compartilham o vocabulário de saída |
| Security surface | Hooks que leem o índice e nunca gravam; o `init` grava `core.hooksPath` com confirmação e nunca desliga alarme alheio; H3 nunca imprime o valor da credencial; guards fail-open |
| LLM prompt items | None (`LLM Prompts: false`) |
| Independent volume | Médio (hook, instalador, higiene, adaptador), mas com marcas em comum |
| Context-rot risk | Alto: a sessão foi do brainstorm ao build. Mitigado pelos artefatos, pela revisão do DESIGN em contexto fresco (3 HIGH antes do código) e por um teste de cada regra dos dois lados |
| Runtime capabilities | default e subagente disponíveis; briefs não oferecido |

**Recommendation:** default.

**User decision:** default. O Roberto pediu "execute o define, ux-review, design, review do design, build, review do build" e depois "continue o pipeline até o release"; o modo foi registrado, não perguntado.

**Pre-build review:** Sim, a revisão do DESIGN em contexto fresco, modo contrato (NEEDS_WORK: 3 HIGH, 2 MEDIUM, 10 LOW; todas aplicadas antes do build menos a L6, rebatida por escopo e documentada; os 5 ajustes de contrato ACEITOS no DEFINE v1.2).

---

## Summary

| Metric | Value |
|---|---|
| Hooks novos | `sdd/hooks/pre-commit` (250 linhas, bash 3.2) e `sdd/hooks/pre-push` (36) |
| Adaptador do Claude Code | `bin/adapters/claude/sdd-report-guard.py` (107) e `sdd-avaliador-guard.py` (71); merge em `.claude/settings.json` (`merge.sh`) |
| Instalador | `bin/sdd-open.sh` 687 → 836 linhas (`hooks_estado`, linha do plano, `core.hooksPath`, migração, `doctor`, adaptadores com prefixo, `--check`); `vendors.sh` (lista de contexto); `merge.sh` (+82) |
| Skill | `sdd-higiene-dado` 1.1.1 → 1.2.0 (modo "hooks do projeto"; arquivo legado por `--git-common-dir`) |
| Slot | `project.context_file_max_kb: 100` |
| Testes | 630 → 683 no piso (2 arquivos novos: 23 + 11; `test_sdd_open` +11, `test_alarme` 29 → 36 com a `TestCopiaGerada` reescrita, `test_docs` +1; 9 dos novos vieram dos 2 ciclos da revisão) |
| Fixtures | 5 em `sdd/fixtures/hooks/` (placeholder do H3, 3 payloads dos guards, `settings.json` de usuário); o que o publish-gate reprovaria é montado em execução |
| Docs | `docs/hooks.md` + PT (novos), roadmap EN/PT sem a linha "Hooks" (6 linhas), READMEs, `cli-conventions.md`, guia do aluno |
| Release | `v2.2.9` automática (decisão do Roberto no brainstorm, revista pelo público: o aviso mora na linha do plano, na recusa e no `doctor`) |

---

## Task Execution

| # | Task | Status | Notes |
|---|---|---|---|
| 1–2 | `sdd/hooks/pre-commit`, `pre-push` | Done | H6 → H2 → H5 → H3 (+gitleaks `-v --redact`) → H4 → REPORT → HIGIENE, todas rodam, recusa única (UX U2/U8); UTF-16 pula H5; `grep -E` no H3 |
| 3 | `bin/lib/vendors.sh` | Done | `VENDOR_ARQUIVOS_CONTEXTO`, `vendor_arquivo_contexto`, alvos do claude |
| 4 | `bin/lib/merge.sh` | Done | `merge_claude_settings` (JSON inválido 66, nada escrito), `claude_settings_em_dia` |
| 5–6 | guards em `bin/adapters/claude/` | Done | fail-open com `systemMessage`; 1ª linha da razão diz o que foi negado (UX U9); fixtures e template pulados |
| 7 | `bin/sdd-open.sh` | Done | `hooks_estado` por `--git-common-dir` (nota H3), linha do plano com o efeito (U1), ⚠️ de OUTRO com a linha para acrescentar (U5), migração (U6), `doctor` (U7), `git switch -c` no `→` final (nota M5), `claude_settings_checar` antes de escrever (L5) |
| 8 | `sdd/config.example.yaml` | Done | slot com comentário |
| 9–16 | `sdd-higiene-dado` 1.2.0 | Done | `alarme.sh` em 3 modos; `pre-commit.sh` com a linha de desinstalar sem `rm` sob `hooksPath`; SKILL, manifest, evals, CHANGELOG, 2 referências |
| 17–21 | Fixtures | Done | `gitleaks detect` verde sobre elas e sobre `tests/` |
| 22–28 | Testes | Done | `test_hooks.py`, `test_claude_adapter.py`; `Hooks` em `test_sdd_open`; `TestCopiaGerada` reescrita + `TestModoHooks`; `test_docs`, `test_bash32`, `test_agnostico` (`sdd/hooks` no escopo) |
| 29–36 | Docs | Done | `docs/hooks.md` + PT linkados dos READMEs; roadmap 6 linhas; `COMMIT RECUSADO` e exits dos hooks em `cli-conventions.md`; ficha da higiene no guia |
| 37 | `MANIFEST.txt` | Done | +13 linhas, ordem `LC_ALL=C` |
| 38 | `.github/workflows/release.yml` | Done | `sdd/hooks/**` em `paths:`; `test_release_workflow` atualizado |

---

## Files Changed

| File | Action | Purpose |
|---|---|---|
| `sdd/hooks/pre-commit`, `sdd/hooks/pre-push` | Created | H2–H6, REPORT, alarme da higiene; aviso de base velha |
| `bin/sdd-open.sh`, `bin/lib/vendors.sh`, `bin/lib/merge.sh` | Modified | `init`/`doctor`/`sync --check` com hooks e adaptador do Claude Code |
| `bin/adapters/claude/sdd-report-guard.py`, `sdd-avaliador-guard.py` | Created | Guards gerados em `.claude/hooks/` |
| `sdd/config.example.yaml` | Modified | `project.context_file_max_kb` |
| `.agents/skills/sdd-higiene-dado/` (SKILL, manifest, evals, CHANGELOG, `alarme.sh`, `pre-commit.sh`, 2 referências) | Modified | 1.2.0: modo hooks |
| `sdd/fixtures/hooks/` (5 arquivos) | Created | Os dois lados das regras e dos guards |
| `tests/test_hooks.py`, `tests/test_claude_adapter.py` | Created | AT-007 a AT-016; AT-020 a AT-024 |
| `tests/test_sdd_open.py`, `test_alarme.py`, `test_docs.py`, `test_bash32.py`, `test_agnostico.py`, `test_release_workflow.py` | Modified | AT-001 a AT-006, AT-017 a AT-019, AT-025 a AT-027; um teste existente passa a commitar o `.p12` com `--no-verify` (drift 3) |
| `docs/hooks.md`, `docs/pt-BR/hooks.md` | Created | As regras, o alarme, o limite do `--no-verify`, desligar, o adaptador |
| `docs/roadmap.md`, `docs/pt-BR/roadmap.md`, `README.md`, `README.pt-BR.md`, `docs/cli-conventions.md`, `docs/pt-BR/guia-do-aluno.md` | Modified | Linha "Hooks" removida; links; palavras e exits; ficha da higiene |
| `.github/workflows/release.yml`, `MANIFEST.txt` | Modified | `sdd/hooks/**`; 13 arquivos novos |

---

## Drift Detected

| # | Drift | Decisão |
|---|---|---|
| 1 | `sdd/templates/BUILD_REPORT_TEMPLATE.md` também casa `BUILD_REPORT_*.md` e é copiado pelo `init`: o 1º commit depois da instalação era recusado por `[REPORT]` (a revisão do DESIGN tinha pego as fixtures, não o molde) | `sdd/templates/` entrou na exceção do hook e do guard (DEFINE AT-013/AT-023 v1.2, DESIGN Decision 2) |
| 2 | `AVISOS="$AVISOS⚠️ …"` no bash 3.2: o byte não-ASCII colado vira parte do nome da variável (`AVISOS�: unbound variable`) | Nome entre chaves antes do emoji, com o comentário; os testes de regra pulada ficaram vermelhos e depois verdes |
| 3 | `test_doctor_nao_perde_o_resto_de_nome_com_quebra_de_linha` commita um `.p12` depois do `init`; com os hooks ligados e o `gitleaks` instalado (regra `pkcs12-file`), o commit é recusado — comportamento correto do hook | O teste passa a commitar com `--no-verify` (o alvo dele é a mensagem do `doctor`); registrado no próprio teste |
| 4 | `tests/test_sdd_open.py` sem `import os` na classe nova | Corrigido antes do gate verde |

Nenhum prompt de runtime.

---

## Verification Results

### Incremental Verification

| Task | Command / Method | Result | Evidence |
|---|---|---|---|
| Base antes de tocar em nada | suíte inteira no piso em `1d225e5` | Pass | 630 OK (rodado pela revisão do DESIGN, `AVAL-DESIGN-suite-base.log`) |
| Baseline vermelha | os testes novos e as classes novas na árvore `v2.2.8` | Pass (vermelho esperado) | `sdd/reports/evidence/F8_HOOKS/baseline.log` |
| Baseline das notas do ciclo 1 | os 7 testes das correções contra `6a238d2` | Pass (vermelho esperado, 7/7) | `sdd/reports/evidence/F8_HOOKS/baseline-ciclo1.log` |
| Baseline das notas do ciclo 2 | os 3 testes das correções contra `938ce47` | Pass (vermelho esperado, 3/3) | `sdd/reports/evidence/F8_HOOKS/baseline-ciclo2.log` |
| Hooks, regra por regra | `test_hooks.py` (22) | Pass | `sdd/reports/evidence/F8_HOOKS/testes-hooks.log` |
| Adaptador e guards | `test_claude_adapter.py` (10) | Pass | `sdd/reports/evidence/F8_HOOKS/testes-adaptador.log` |
| Higiene 1.2.0 | `test_alarme.py` (34; 28 intactos) | Pass | `sdd/reports/evidence/F8_HOOKS/testes-alarme.log` |
| `init`/`doctor` | `test_sdd_open.py` (28) | Pass | `sdd/reports/evidence/F8_HOOKS/testes-init.log` |
| `init` num projeto real | sandbox: `init`, `hooksPath`, 1º commit, commit com credencial recusado, guards gerados | Pass | `sdd/reports/evidence/F8_HOOKS/init-em-projeto-real.log` |
| gitleaks sobre `tests/` e fixtures | `gitleaks detect --no-git --exit-code 1` | Pass | `sdd/reports/evidence/F8_HOOKS/gitleaks-tests.log` |
| Evidência da própria F8 (logs do build) | `gate-shell-evidencia.sh` sobre os logs de `gerar-evidencia.sh`, `GATE`, baselines, guard e sabotagem (sem `AVAL*`) | Pass (0 acusações) | `sdd/reports/evidence/F8_HOOKS/shell-da-f8.log` |
| Pasta inteira, com as sondas dos avaliadores | `gate-shell-evidencia.sh sdd/reports/evidence/F8_HOOKS` | Declarado: 62 acusações em 85 logs, todas em `AVAL*.log` (sondas do revisor do DESIGN e do avaliador do build, comandos compostos com `tail`/`head`/`tr` no meio da linha; nenhuma é evidência citada por `true` neste relatório — a mesma classe conservadora declarada no corpus da F7) | `sdd/reports/evidence/F8_HOOKS/shell-da-f8-pasta-inteira.log` |
| Guard antes do avaliador | `avaliador-guard.sh` com os 4 prefixos | Pass | `sdd/reports/evidence/F8_HOOKS/guard-antes-do-avaliador-design.log` |

### Verify Gate

| Attribute | Value |
|---|---|
| **Kind** | test |
| **Command / Method** | `bash sdd/bin/verify-gate.sh --strict sdd/features/DEFINE_F8_HOOKS.md`. O `cmd` faz a cópia por `git archive HEAD`, roda o `publish-gate.sh` em modo `ci` e a suíte no piso |
| **Exit / Result** | 0 em `6a238d2` (676 testes), `938ce47` (680) e `7c640eb` (`Ran 683 tests … OK`; G1–G5 verdes) |
| **Status** | Green |
| **Evidence** | `sdd/reports/evidence/F8_HOOKS/GATE.log` |

### Manual UX Receipt

N/A

### Complementary Checks

| Check | Command / Method | Status | Evidence |
|---|---|---|---|
| Lint | `python3 sdd/bin/skill-lint.py --conversa .agents/skills/sdd-*/SKILL.md` (17) | Pass | `sdd/reports/evidence/F8_HOOKS/skill-lint-conversa.log` |
| Versões | `check-versions.py --base v2.2.8 --base-obrigatoria` | Pass | `sdd/reports/evidence/F8_HOOKS/check-versions.log` |
| bash 3.2 | `grep` de bashismos em `sdd/bin/*.sh`, `sdd/hooks/*`, scripts da higiene, `bin/` | Pass | `sdd/reports/evidence/F8_HOOKS/bash32.log` |
| Tamanho | `wc -l` (maior `SKILL.md` tocado: 248) | Pass | `sdd/reports/evidence/F8_HOOKS/linhas.log` |
| Typecheck | N/A (bash e Python sem anotação verificada) | N/A | — |
| Tests | docs, bash32, agnóstico, release workflow | Pass | `sdd/reports/evidence/F8_HOOKS/testes-lints-do-pacote.log` |
| Sabotagem | `sabotagem.sh`, 9 mutações | Pass | `sdd/reports/evidence/F8_HOOKS/sabotagem.log` |

---

## Acceptance Test Verification

| ID | Scenario | Status | Evidence |
|---|---|---|---|
| AT-001 | `init` copia e liga os hooks, linha do plano, `git switch -c` só com remoto | Pass | `sdd/reports/evidence/F8_HOOKS/testes-init.log` |
| AT-002 | `--dry-run` não escreve nem liga | Pass | `sdd/reports/evidence/F8_HOOKS/testes-init.log` |
| AT-003 | Outro `hooksPath` ou pre-commit alheio: nada tocado, linha para acrescentar | Pass | `sdd/reports/evidence/F8_HOOKS/testes-init.log` |
| AT-004 | Alarme da higiene migra sem perder a proteção | Pass | `sdd/reports/evidence/F8_HOOKS/testes-init.log` |
| AT-005 | `init` repetido idempotente; hook apagado é recriado | Pass | `sdd/reports/evidence/F8_HOOKS/testes-init.log` |
| AT-006 | `doctor` com ✅ ou um ⚠️ por causa | Pass | `sdd/reports/evidence/F8_HOOKS/testes-init.log` |
| AT-007 | H2: teto pelo slot, default 100 | Pass | `sdd/reports/evidence/F8_HOOKS/testes-hooks.log` |
| AT-008 | H3: credencial recusada, só a chave; placeholder e package-lock passam | Pass | `sdd/reports/evidence/F8_HOOKS/testes-hooks.log` |
| AT-009 | H3: gitleaks 1 recusa, 0 passa, outro avisa | Pass | `sdd/reports/evidence/F8_HOOKS/testes-hooks.log` |
| AT-010 | H4: delete/rename e colapso recusados; delta-ok passa; lint ausente avisa | Pass | `sdd/reports/evidence/F8_HOOKS/testes-hooks.log` |
| AT-011 | H5: NUL em texto recusado; binário e UTF-16 passam | Pass | `sdd/reports/evidence/F8_HOOKS/testes-hooks.log` |
| AT-012 | H6: só na branch padrão com remoto; `git switch -c` antes de `sdd-new-session` | Pass | `sdd/reports/evidence/F8_HOOKS/testes-hooks.log` |
| AT-013 | REPORT: staged pelo lint; fixtures e template pulados; sem python3 avisa | Pass | `sdd/reports/evidence/F8_HOOKS/testes-hooks.log` |
| AT-014 | Higiene ligada recusa CPF/CNPJ/.env, última linha sem `rm` | Pass | `sdd/reports/evidence/F8_HOOKS/testes-hooks.log` |
| AT-015 | Vários achados numa recusa só; limpo é silencioso | Pass | `sdd/reports/evidence/F8_HOOKS/testes-hooks.log` |
| AT-016 | pre-push avisa base velha e sai 0 | Pass | `sdd/reports/evidence/F8_HOOKS/testes-hooks.log` |
| AT-017 | `alarme.sh` em modo hooks: verificar/instalar/desinstalar pela config; dispatcher intocado | Pass | `sdd/reports/evidence/F8_HOOKS/testes-alarme.log` |
| AT-018 | Outro `hooksPath` ou `sdd/hooks` sem a marca: exit 2 | Pass | `sdd/reports/evidence/F8_HOOKS/testes-alarme.log` |
| AT-019 | 28 testes intactos; `TestCopiaGerada` afirma o modo hooks | Pass | `sdd/reports/evidence/F8_HOOKS/testes-alarme.log` |
| AT-020 | Guards gerados com cabeçalho; 2 entradas no `settings.json` | Pass | `sdd/reports/evidence/F8_HOOKS/testes-adaptador.log` |
| AT-021 | JSON inválido 66; sem python3 64; sem duplicar; `--check` acusa | Pass | `sdd/reports/evidence/F8_HOOKS/testes-adaptador.log` |
| AT-022 | Write/Edit que o lint reprova é negado com a saída do lint | Pass | `sdd/reports/evidence/F8_HOOKS/testes-adaptador.log` |
| AT-023 | Outro arquivo, fixture, template, Edit sem `old_string`: silêncio; falha aberta avisa | Pass | `sdd/reports/evidence/F8_HOOKS/testes-adaptador.log` |
| AT-024 | Despacho com `veredito` e árvore suja negado; limpo ou sem a palavra passa | Pass | `sdd/reports/evidence/F8_HOOKS/testes-adaptador.log` |
| AT-025 | `test_agnostico` com `sdd/hooks` no escopo; `test_bash32` varre os hooks | Pass | `sdd/reports/evidence/F8_HOOKS/testes-lints-do-pacote.log` |
| AT-026 | `docs/hooks*.md` linkados, com `--no-verify`; roadmap com 6 linhas | Pass | `sdd/reports/evidence/F8_HOOKS/testes-lints-do-pacote.log` |
| AT-027 | `check-versions --base v2.2.8` com a higiene em 1.2.0 | Pass | `sdd/reports/evidence/F8_HOOKS/check-versions.log` |
| AT-028 | 630 testes anteriores, publish-gate ci, 17 skills | Pass | `sdd/reports/evidence/F8_HOOKS/GATE.log` |
| AT-029 | 9 sabotagens vermelhas e restauradas | Pass | `sdd/reports/evidence/F8_HOOKS/sabotagem.log` |
| AT-030 | Testes novos vermelhos na `v2.2.8` | Pass | `sdd/reports/evidence/F8_HOOKS/baseline.log` |

---

## Contrato de aceite (C2) e avaliador de contexto fresco (C1)

**Camadas do manifest:** contagem impossível neste repositório (sem `sdd/config.yaml`); o avaliador roda mesmo assim.
**Contrato de aceite (passo 1.5 da `sdd-build`):** 5 propostas / 5 aceitas — `## Contrato de aceite` do DESIGN.
**Veredito do avaliador (C1):** PASS · ciclos: 2 · achados: 6 (ciclo 1: 1 MEDIUM, 5 LOW) + 2 (ciclo 2: 2 LOW), 0 HIGH · `AVALIACAO_F8_HOOKS_20261030-ciclo2.md`

Os 8 achados foram aplicados (`938ce47` e `7c640eb`), cada um com teste dos dois lados e baseline vermelha no commit anterior (`baseline-ciclo1.log`, `baseline-ciclo2.log`). As correções do ciclo 2 **não** passaram por um 3º avaliador: a `sdd-build` limita a 2 ciclos.

---

## Advisor Ledger

**Revisão do DESIGN (pré-build):** NEEDS_WORK, `sdd/reviews/REVISAO_DESIGN_F8_HOOKS_20261030.md`. As 15 notas estão no Advisor Ledger do DESIGN v1.1: 14 APPLIED, 1 REBUTTED (L6, escopo: documentado em `docs/hooks.md`).

**Revisão do build (pós-build):** avaliador em contexto fresco, numa worktree destacada, com o guard verde antes de cada despacho (`guard-antes-do-avaliador.log`, `guard-antes-do-avaliador-ciclo2.log`).

| # | Phase | Note | Severity | Decision | Evidence |
|---:|---|---|---|---|---|
| M1 | ciclo 1 | `settings.json` com topo lista, `hooks` lista ou `PreToolUse` objeto: o `init` escrevia tudo e só depois saía 66 dizendo "nada foi alterado" | MEDIUM | APPLIED | forma conferida em `claude_settings_checar`, no plano; `test_settings_com_forma_errada_aborta_antes_de_escrever`. `938ce47` |
| L1 | ciclo 1 | H3 recusava `"token": "^2.0.0"` num `package-lock.json` | LOW | APPLIED | número de versão é placeholder; caso novo em `test_h3_placeholder_e_package_lock_passam`. `938ce47` |
| L2 | ciclo 1 | H3 não via `PASSWORD=valor` sem aspas em `.env*` | LOW | APPLIED | regex de dotenv só para `.env*`; caso `.env.prod` em `test_h3_credencial…`. `938ce47` |
| L3 | ciclo 1 | só o alarme falhando: cabeçalho de achados com bloco vazio e sem `→` da classe | LOW | APPLIED | cabeçalho próprio e `→ [alarme]`; `test_higiene_ligada…`. `938ce47` |
| L4 | ciclo 1 | `core.hooksPath` absoluto por link simbólico (`/tmp`) virava OUTRO no `doctor` | LOW | APPLIED | `hooks_path_e_nosso` por `pwd -P` no `init` e no `alarme.sh`; 2 testes. `938ce47` |
| L5 | ciclo 1 | `init` repetido sem `paste` no PATH esvaziava os vendors em silêncio | LOW | APPLIED | `tr` no lugar do `paste`; `test_init_repetido_sem_paste…`. `938ce47` |
| LA | ciclo 2 | H3 decidia pela primeira ocorrência: placeholder ou versão antes da credencial real absolvia o arquivo | LOW | APPLIED | `credencial_real` sobre toda ocorrência; `test_h3_placeholder_antes_nao_absolve_a_credencial_real`. `7c640eb` |
| LB | ciclo 2 | `core.hooksPath` `sdd/hooks/` ou `./sdd/hooks` (que o git aceita) viravam OUTRO | LOW | APPLIED | normalização em `hooks_path_e_nosso` (init e alarme); 2 testes. `7c640eb` |

Contagem de achados: DESIGN 15, build ciclo 1 6, ciclo 2 2 (0 HIGH nos 3).

---

## Issues Encountered

| Issue | Resolution |
|---|---|
| `git rev-parse --git-path hooks/pre-commit` segue o `core.hooksPath` (achado da revisão do DESIGN) | Arquivo legado sempre por `--git-common-dir`, no `init`, no `alarme.sh` e no `pre-commit.sh` |
| O `gitleaks` do G1 varre `tests/`: um literal de alta entropia no teste reprovaria o gate | Valores gerados em execução; `gitleaks-tests.log` |
| Dois `.pyc` entraram no primeiro commit (um `py_compile` sem `-B`) | Tirados do commit (amend); `python3 -B` em todo lugar |
| `PATH` sem `python3` no macOS levaria junto `git` e `awk` | O teste monta um diretório de `PATH` só com links para as ferramentas do hook |
| Dois comandos do `gerar-evidencia.sh` (`escopo`, `init-em-projeto-real`) tinham formatador no pipe e foram acusados pelo `gate-shell-evidencia.sh`; a sonda da credencial no projeto real quebrava por aspas escapadas dentro de aspas simples | Reescritos sem `tail`/`head`/`sed` e com `python3 -c` para o valor aleatório; logs regenerados; o `shell-da-f8.log` fica com a única acusação do revisor do DESIGN |

---

## Deviations from Design

| Deviation | Reason |
|---|---|
| `sdd/templates/` também fica fora da regra REPORT e do guard | Drift 1 |
| Um teste existente de `test_sdd_open.py` commita com `--no-verify` | Drift 3 (o hook, agora ligado pelo `init`, recusa `.p12` quando o gitleaks está instalado) |

---

## Blockers

Nenhum.

---

## Final Status

### Overall: COMPLETE

- [x] Todas as tarefas do manifest concluídas (38/38)
- [x] Verify Gate verde (`GATE.log`)
- [x] Testes novos vermelhos na base (`baseline.log`) e 9 sabotagens com dentes (`sabotagem.log`)
- [x] Nenhum TODO/FIXME como implementação pendente
- [x] Avaliador de contexto fresco do build, ciclo 1: NEEDS_WORK (1 MEDIUM, 5 LOW), tudo aplicado em `938ce47`
- [x] Ciclo 2 sobre `938ce47`: PASS (2 LOW, aplicados em `7c640eb`); `AVALIACAO_F8_HOOKS_20261030-ciclo2.md` persistido
- [x] Release `v2.2.9` (2026-10-31): PR #10 com CI verde em ubuntu e macOS (run 41154964749), bloco do OK, OK do Roberto ("push sdd-open"), push fast-forward `1d225e5..7c640eb` em `main`; run `release` 41185402408 verde; tag `v2.2.9` em `7c640eb`; `sdd-open-v2.2.9.tar.gz` SHA-256 `b022f5529b9cac171cb38cef7d7277fd8e5e485a84d449e359b62ac07ae03f6b` conferido com `shasum -a 256 -c`

---

## Next Step

Execute o **SDD Handoff by RDD**.
