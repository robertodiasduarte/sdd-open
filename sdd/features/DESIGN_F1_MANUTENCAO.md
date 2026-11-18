# DESIGN: F1 Manutenção do sdd-open

> Technical design for implementing F1 Manutenção do sdd-open

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | F1_MANUTENCAO |
| **Date** | 2026-10-29 |
| **Author** | SDD Design by RDD |
| **BRAINSTORM** | `sdd/features/BRAINSTORM_F1_MANUTENCAO.md` |
| **DEFINE** | `sdd/features/DEFINE_F1_MANUTENCAO.md` |
| **UX REVIEW** | N/A |
| **LLM Prompts** | false |
| **Status** | Ready for Build |

---

## Architecture Overview

```text
                     scripts existentes (NÃO mudam)
   ┌──────────────────────────────────────────────────────────────────┐
   │ sdd/bin/verify-gate.sh   sdd/bin/report-lint.py   sdd/bin/skill-lint.py │
   │ sdd/bin/playbook-lint.sh bin/sdd-open.sh (+ bin/lib/*)  scripts/publish-gate.sh │
   └───────────────▲──────────────────────────────────────────────────┘
                   │ subprocess (caixa-preta, pasta temporária, git isolado, sem rede)
   ┌───────────────┴──────────────┐      ┌──────────────────────────────┐
   │ tests/apoio.py (sandbox)     │◄─────│ tests/test_*.py  (9 suítes)  │
   └──────────────────────────────┘      └──────────────┬───────────────┘
                                                        │ também testam
   ┌──────────────────────────────┐      ┌──────────────▼───────────────┐
   │ scripts/check-versions.py    │      │ scripts/next-version.sh      │
   │ versão por skill + bump      │      │ TAG / NEW / BASE da release  │
   └──────────────▲───────────────┘      └──────────────▲───────────────┘
                  │                                     │
   ┌──────────────┴─────────────────────────────────────┴───────────────┐
   │ .github/workflows/publish-gate.yml  (PR e push: + unittest + versões) │
   │ .github/workflows/release.yml                                        │
   │   job testes (contents: read) ──needs──► job release (contents: write)│
   │   publish-gate · unittest · check-versions       git archive → tar.gz │
   │                                                  SHA256SUMS.txt       │
   │                                                  gh release create    │
   └──────────────────────────────────────────────────────────┬─────────┘
                                                              ▼
                                   GitHub Release vX.Y.Z (tarball + SHA256SUMS.txt)
```

---

## Components

| Component | Purpose | Technology / Pattern | Inputs | Outputs | Dependencies |
|---|---|---|---|---|---|
| Sandbox de teste | Pasta temporária com git isolado, HOME falso, sem config global, sem rede; helpers para criar repo, commitar e rodar script | Python 3.9 stdlib (`unittest`, `subprocess`, `tempfile`) | Caminho do script, args, arquivos de fixture | `(rc, stdout, stderr)` | bash, git, python3 |
| Suítes de contrato | Um arquivo por script: verify-gate, report-lint, skill-lint, playbook-lint, sdd-open, check-versions, next-version, padrões de PII, workflow de release | `unittest.TestCase`, caixa-preta | Scripts reais do repo | Pass/fail por contrato (AT-001…AT-025) | Sandbox de teste |
| check-versions | Versão X.Y.Z por skill; coerência com `manifest.json`/`evals/cases.json`; bump contra base | Python 3.9 stdlib, porte enxuto do starter | `.agents/skills/*/SKILL.md`, `--base REF`, `--base-obrigatoria`, `--root DIR` | `PASS`/`FAIL` + `RESULTADO:`; exit 0/1/64 | git |
| next-version | Calcula a tag da release e a base de comparação | bash 3.2, `git for-each-ref --sort=-v:refname`, `git tag --points-at HEAD` | Repo git com tags `vX.Y.Z` | Linhas `TAG=`, `NEW=`, `BASE=` (cabem direto em `$GITHUB_OUTPUT`); exit 0/1 | git |
| Padrões de PII | CPF e CNPJ com pontuação, telefone BR sem `+` | 3 ERE em `scripts/publish-gate-patterns.txt` | Árvore do repo | Hit no G2 do publish-gate | `publish-gate.sh` (inalterado) |
| Workflow de CI | Roda os testes e o check-versions em PR e push | GitHub Actions (`publish-gate.yml`) | Checkout com histórico e tags | Job verde/vermelho | Suítes, check-versions, next-version |
| Workflow de release | Testa só com leitura; publica tag + Release com pacote e hash | GitHub Actions (`release.yml`), `gh` do runner | Push em `main` nos paths do produto ou push de tag `v*` | Release `vX.Y.Z` com `sdd-open-vX.Y.Z.tar.gz` e `SHA256SUMS.txt` | next-version, check-versions, publish-gate |

---

## Key Decisions

### Decision 1: Testes caixa-preta em `tests/` na raiz, com Python unittest

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-10-29 |
| **Source** | Brainstorm (Approach A, confirmada) e DEFINE |

**Context:** O open tem 0 testes; os scripts são bash e Python; o `init` copia `sdd/templates`, `sdd/bin` e `sdd/playbook.md` para o projeto do usuário.

**Choice:** `tests/test_<script>.py` rodando cada script real por `subprocess` dentro de uma sandbox (`tests/apoio.py`). Cada teste copia o script para um repo temporário quando o script depende de `git rev-parse --show-toplevel` (verify-gate, playbook-lint, report-lint).

**Rationale:** Sem dependência nova; fora do que o `init` copia; mesmo estilo dos testes do starter que a F2 vai trazer; testa o contrato observável, não a implementação.

**Alternatives Rejected:**
1. bats-core — dependência nova no CI e na máquina de quem contribui; dois frameworks.
2. `--self-test` em cada script — o teste iria para o projeto do usuário e a sabotagem ficaria no mesmo arquivo do teste.

**Consequences:**
- Testes de bash ficam mais verbosos.
- A suíte roda igual dentro da cópia limpa do Verify Gate, que não tem `.git`: todo teste que precisa de git monta o próprio repo.

### Decision 2: `scripts/next-version.sh` concentra a lógica de tag

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-10-29 |
| **Source** | DEFINE (AT-021, AT-022) e checkpoint 2 do Brainstorm |

**Context:** O cálculo da próxima versão, a regra "commit já com tag não ganha outra" e a base do check-versions precisariam ficar inline no YAML, onde não dá para testar.

**Choice:** Script bash 3.2 que imprime três linhas: `TAG=vX.Y.Z`, `NEW=1` (tag a criar) ou `NEW=0` (HEAD já tem tag `v*`; publica essa), e `BASE=<maior tag v* com versão menor que TAG>`. Só aceita tags `^v[0-9]+\.[0-9]+\.[0-9]+$`. Sem nenhuma tag válida: exit 1 com causa e conserto. Lê a lista inteira de `for-each-ref` num `while read`, nunca `| head -1` (SIGPIPE sob `pipefail`).

**Rationale:** Uma fonte testável para o CI e para a release; a saída `chave=valor` vai direto para `$GITHUB_OUTPUT`.

**Alternatives Rejected:**
1. Lógica inline no YAML, como no starter — não testável por unittest.
2. Calcular em Python dentro do check-versions — mistura duas responsabilidades.

**Consequences:**
- Um arquivo a mais no `MANIFEST.txt`.
- AT-021 e AT-022 viram testes com repos temporários e tags reais.

### Decision 3: Release em 2 jobs, publicação por `gh release create`, pacote próprio

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-10-29 |
| **Source** | Brainstorm (decisões 2, 5, 6, 7) e DEFINE (AT-023, AT-024) |

**Context:** Release automática no push de `main` (escolha do Roberto); tag manual `v*` também vira Release; tag criada pelo `GITHUB_TOKEN` não dispara outro workflow; o tarball automático do GitHub não tem hash garantido como estável.

**Choice:** `release.yml` com `on.push.branches: [main]` + `paths` do produto e `on.push.tags: ['v*']` (o GitHub não avalia `paths` em push de tag). Permissão global `contents: read`. Job `testes`: checkout com `fetch-depth: 0`, gitleaks 8.30.1, `publish-gate.sh` em modo `ci`, unittest, `next-version.sh` e `check-versions.py --base BASE --base-obrigatoria`. Job `release` (`needs: testes`, `contents: write`, `timeout-minutes: 10`): `next-version.sh`; se já existe Release para `TAG`, encerra verde sem nada publicar; senão `git archive --format=tar.gz --prefix=sdd-open-TAG/` do `GITHUB_SHA`, `sha256sum` para `SHA256SUMS.txt`, `gh release create TAG --target GITHUB_SHA --generate-notes` com os dois arquivos. `concurrency: release`, sem cancelar.

**Rationale:** Teste vermelho ⇒ `release` skipped, sem tag; escrita só onde é preciso; menos uma action de terceiro; Release idempotente quando o push de tag e o push de `main` chegam juntos.

**Alternatives Rejected:**
1. `softprops/action-gh-release` — dependência de terceiro desnecessária, `gh` já está no runner.
2. Um job só — o token de escrita ficaria exposto também aos testes.

**Consequences:**
- Tags automáticas são leves (criadas pela API); as manuais continuam anotadas. `for-each-ref` e `--points-at` tratam as duas igual.
- A primeira Release automática depois do merge da F1 é `v2.2.1` e inclui o `sdd-new-session` 1.0.0, hoje sem tag.

### Decision 4: check-versions enxuto, com `--root`

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-10-29 |
| **Source** | DEFINE (AT-017…AT-019) e YAGNI do Brainstorm |

**Context:** O check-versions do starter também confere `metadata.updated`, linha de identificação e `description`; os dois primeiros foram para a F4 e o terceiro já é do `skill-lint.py`.

**Choice:** Porte só das checagens de versão X.Y.Z, coerência com `manifest.json`/`evals/cases.json` (quando o JSON tem a chave `version`) e bump contra `--base`. Raiz em `.agents/skills/`. `--root DIR` (default: raiz do pacote) para os testes apontarem para um repo temporário. Exit 0 PASS, 1 FAIL, 64 uso. Saída termina em `RESULTADO:` + `→` (convenção de `docs/cli-conventions.md`).

**Rationale:** Mínimo que impede a versão de mentir em F2–F6, sem tocar as 13 skills agora.

**Alternatives Rejected:**
1. Porte integral do starter — exigiria `updated` e linha de identificação nas 13 skills já na F1.
2. Só estrutural, sem bump — não pega skill alterada com versão velha.

**Consequences:**
- `sdd-auditoria-harness` ganha `version: "1.0.0"` (única mudança em skill).
- Na F4 o check-versions ganha `updated` e a linha de identificação.

### Decision 5: Amostras de PII montadas em tempo de execução

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-10-29 |
| **Source** | Evidência do projeto: G2 do `publish-gate.sh` só isenta os arquivos de padrão pelo caminho exato |

**Context:** Um teste que contenha um CPF, CNPJ ou telefone literal faria o publish-gate reprovar o próprio `tests/`. O mesmo vale para sequência de 11+ dígitos, `/Users/…`, `/home/…` e e-mail fora de `example.com`.

**Choice:** As amostras positivas são concatenadas em tempo de execução (`"123.456" + ".789-09"`). Os testes do padrão leem as linhas de `scripts/publish-gate-patterns.txt` e aplicam com `grep -E -i`, igual ao G2; um teste extra roda o `publish-gate.sh` inteiro sobre uma cópia temporária com um arquivo plantado, pulado só quando o gitleaks não está instalado (no CI ele sempre está).

**Rationale:** O teste prova o padrão sem que o repositório carregue o dado que o padrão proíbe.

**Alternatives Rejected:**
1. Isentar `tests/` no G2 — abranda o gate (proibido nesta frente).
2. Testar só o regex em Python `re` — não prova o comportamento do `grep -E` que o gate usa.

**Consequences:**
- Regra para todo teste futuro: nenhum literal que case com `publish-gate-patterns.txt`.

---

## File Manifest

| # | File | Action | Purpose | Agent / Owner | Dependencies |
|---:|---|---|---|---|---|
| 1 | `tests/apoio.py` | Create | Sandbox: pasta temporária, env git isolado, helpers `repo()`, `commit()`, `roda()`, `copia_script()` | (general) | None |
| 2 | `tests/test_verify_gate.py` | Create | AT-002…AT-005, AT-025 | (general) | 1 |
| 3 | `tests/test_report_lint.py` | Create | AT-006, AT-007 | (general) | 1 |
| 4 | `tests/test_skill_lint.py` | Create | AT-008, AT-009 | (general) | 1 |
| 5 | `tests/test_playbook_lint.py` | Create | AT-010 | (general) | 1 |
| 6 | `tests/test_sdd_open.py` | Create | AT-011…AT-016 | (general) | 1 |
| 7 | `scripts/check-versions.py` | Create | Gate de versão por skill | (general) | None |
| 8 | `tests/test_check_versions.py` | Create | AT-017…AT-019 | (general) | 1, 7 |
| 9 | `scripts/next-version.sh` | Create | TAG / NEW / BASE da release | (general) | None |
| 10 | `tests/test_next_version.py` | Create | AT-021, AT-022 | (general) | 1, 9 |
| 11 | `scripts/publish-gate-patterns.txt` | Modify | +3 padrões: CPF e CNPJ com pontuação, telefone BR sem `+` | (general) | None |
| 12 | `tests/test_publish_gate_patterns.py` | Create | AT-020 | (general) | 1, 11 |
| 13 | `.agents/skills/sdd-auditoria-harness/SKILL.md` | Modify | `metadata.version: "1.0.0"` (só o frontmatter) | (general) | None |
| 14 | `.github/workflows/release.yml` | Create | Release automática em 2 jobs | (general) | 7, 9 |
| 15 | `tests/test_release_workflow.py` | Create | AT-023 e a parte estática de AT-024 (paths, permissões, `needs`, sem `continue-on-error`) | (general) | 1, 14 |
| 16 | `.github/workflows/publish-gate.yml` | Modify | Checkout com `fetch-depth: 0`; steps "Unit tests" e "Version gate"; checks existentes intocados | (general) | 7, 9 |
| 17 | `CONTRIBUTING.md` | Modify | Como rodar os testes; skill tocada sobe `metadata.version`; Release com tarball e `SHA256SUMS.txt` | (general) | 14 |
| 18 | `MANIFEST.txt` | Modify | Declarar 1–10, 12, 14, 15 | (general) | 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 15 |

**Total Files:** 18

### Agent Assignment Rationale

| Agent / Owner | Files Assigned | Why |
|---|---|---|
| (general) | 1–18 | Bash, Python stdlib e GitHub Actions; nenhum agente especializado catalogado no projeto |

**Agent Discovery:** Not available

---

## Code Patterns

### Pattern 1: Sandbox de teste (`tests/apoio.py`)

```python
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
BASH = shutil.which("bash") or "bash"


class Sandbox(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="sdd-open-")).resolve()
        self.home = self.tmp / "home"
        self.home.mkdir()
        vazio = self.tmp / "gitconfig-vazio"
        vazio.write_text("", encoding="utf-8")
        self.env = dict(os.environ, HOME=str(self.home), GIT_CONFIG_GLOBAL=str(vazio),
                        GIT_CONFIG_NOSYSTEM="1", GIT_CEILING_DIRECTORIES=str(self.tmp),
                        GIT_TERMINAL_PROMPT="0", LC_ALL="C.UTF-8")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def roda(self, args, cwd):
        r = subprocess.run(args, cwd=cwd, env=self.env, capture_output=True, text=True,
                           stdin=subprocess.DEVNULL, timeout=120)
        return r.returncode, r.stdout, r.stderr
```

### Pattern 2: Sabotagem no Build (prova de que o teste discrimina)

```bash
# 1. sabotar UMA linha do script sob teste (arquivo rastreado e limpo)
sed -i.bak 's/finalizar 5/finalizar 2/' sdd/bin/verify-gate.sh && rm sdd/bin/verify-gate.sh.bak
# 2. a suíte TEM de ficar vermelha, com o nome do teste
python3 -B -m unittest discover -s tests -p 'test_verify_gate.py' 2>&1 | tail -20
# 3. desfazer e provar verde de novo
git checkout -- sdd/bin/verify-gate.sh && python3 -B -m unittest discover -s tests -p 'test_*.py'
```

### Pattern 3: Saída do next-version

```bash
$ bash scripts/next-version.sh
TAG=v2.2.1
NEW=1
BASE=v2.2.0
```

### Pattern 4: Amostra de PII sem literal no arquivo

```python
cpf = "123.456" + ".789-09"
alvo = self.tmp / "planilha.md"
alvo.write_text("cliente " + cpf + "\n", encoding="utf-8")
```

---

## Data Flow

```text
1. Local / Verify Gate: commit na branch → git archive HEAD → cópia limpa em mktemp
   │
   ▼
2. publish-gate.sh (modo ci) na cópia: G1 gitleaks · G2 padrões (+3 de PII) · G3 MANIFEST · G4 fixtures · G5 docs
   │
   ▼
3. python3 -B -m unittest discover -s tests na cópia: cada suíte cria sandbox → roda o script real → compara rc/saída
   │
   ▼
4. PR → publish-gate.yml: gate + checks inline existentes + unittest + check-versions --base BASE
   │
   ▼
5. Push em main (paths do produto) ou push de tag v* → release.yml
   job testes (read): publish-gate · unittest · next-version → check-versions --base BASE --base-obrigatoria
   │ vermelho → job release skipped, nenhuma tag
   ▼
6. job release (write): next-version → Release já existe? encerra verde
   │ não
   ▼
7. git archive → sdd-open-TAG.tar.gz → SHA256SUMS.txt → gh release create TAG --target GITHUB_SHA
   │
   ▼
8. Quem baixa: shasum -a 256 -c SHA256SUMS.txt
```

---

## Integration Points

| External System | Integration Type | Authentication | Direction | Failure / Retry |
|---|---|---|---|---|
| GitHub Actions | Workflow YAML | `GITHUB_TOKEN` do workflow; `contents: write` só no job `release` | in | Job vermelho; sem retry automático — rerun manual |
| GitHub Releases | `gh release create` / `gh release view` | `GH_TOKEN` = token do workflow | out | Falha na criação deixa o job vermelho; rerun é seguro porque a Release existente encerra verde |
| gitleaks 8.30.1 | Binário baixado por `curl` com versão fixada | N/A | in | Download falhou ⇒ step vermelho; publish-gate nunca pula o G1 |

---

## Testing Strategy

| Test Type | Scope / Requirement | Files | Tools | Pass Signal |
|---|---|---|---|---|
| Unit (contrato) | verify-gate: 6 exits, `--print`, `--strict`, `contains:`, smoke+403, VERMELHO declarado, INCONCLUSIVO declarado (AT-002…AT-005) | `tests/test_verify_gate.py` | unittest + bash + git | rc esperado por caso |
| Unit (contrato) | report-lint: evidência válida por log, avaliação e recibo; declarativa, ausente, vazia; uso (AT-006, AT-007) | `tests/test_report_lint.py` | unittest | 0 / 1 / 64 |
| Unit (contrato) | skill-lint: 13 skills reais; sem frontmatter; `name` ≠ pasta; description > 1024 (AT-008, AT-009) | `tests/test_skill_lint.py` | unittest | 0 / 1 |
| Unit (contrato) | playbook-lint: 4 fixtures, `--anti-collapse`, `--self-test` (AT-010) | `tests/test_playbook_lint.py` | unittest | 0 / 1 / 2 |
| Integration | sdd-open: verbo e opção inválidos, init fora de git, init, sync idempotente, `--check` com cópia editada, AGENTS.md preservado, doctor (AT-011…AT-016) | `tests/test_sdd_open.py` | unittest + git | rc + `git status --porcelain` vazio + bytes iguais |
| Unit | check-versions: PASS, sem bump, versão ausente/malformada, manifest divergente, base obrigatória ausente (AT-017…AT-019) | `tests/test_check_versions.py` | unittest + git | 0 / 1 |
| Unit | next-version: patch, ordem por versão, HEAD já com tag, sem tags (AT-021, AT-022) | `tests/test_next_version.py` | unittest + git | linhas TAG/NEW/BASE |
| Unit | Padrões de PII: positivos montados em runtime; negativos (data, versão, hash); gate inteiro com arquivo plantado (AT-020) | `tests/test_publish_gate_patterns.py` | unittest + grep + gitleaks | hit / sem hit |
| Unit (estático) | release.yml: permissões, `needs`, paths, tags, sem `continue-on-error` nem `\|\| true` (AT-023, AT-024) | `tests/test_release_workflow.py` | unittest (texto) | asserts |
| Non-regression | Fixtures de G4 e checks inline intocados (AT-025) | `tests/test_verify_gate.py` + `git diff 80d7887 -- sdd/fixtures sdd/bin bin scripts/publish-gate.sh` | unittest + git | 5/0/64 e diff vazio |
| Sabotagem | Uma por script: verify-gate, report-lint, skill-lint, playbook-lint, sdd-open, check-versions (AT-026) | `sdd/reports/evidence/F1_MANUTENCAO/` | Pattern 2 | vermelho nomeado → verde após reverter |
| E2E / Verify Gate | Cópia limpa: publish-gate + suíte inteira (AT-001) | DEFINE `verify_gate.cmd` | `sdd/bin/verify-gate.sh --strict` | exit 0 |
| Smoke pós-merge | Release publicada (AT-024) | N/A | `gh release view`, `shasum -a 256 -c` | Release com 2 assets e hash conferido |

---

## Error Handling

| Error Type | Detection | Handling Strategy | Retry? | Observability |
|---|---|---|---|---|
| Teste vermelho no job `testes` | rc ≠ 0 do unittest | `release` skipped; nenhuma tag | No | Log do job com o nome do teste |
| Repo sem tag `v*` válida | `next-version.sh` sem candidatos | exit 1 com causa e conserto ("crie a primeira tag vX.Y.Z") | No | `RESULTADO:` no log |
| Base que não resolve | `git rev-parse --verify BASE^commit` falha | Com `--base-obrigatoria`: FAIL, nunca "só estrutura" | No | `FAIL: base … indisponível` |
| Release já existe para a TAG | `gh release view TAG` exit 0 | Encerra o job verde sem publicar | N/A | `::notice::` com a TAG |
| gitleaks ausente | `command -v gitleaks` | publish-gate sai 1 (comportamento atual); teste do gate inteiro é pulado localmente com motivo | No | `skipTest` com motivo explícito |
| Teste trava | `timeout=120` no `subprocess.run` | `TimeoutExpired` vira erro do teste | No | Traceback com o comando |
| `__pycache__` na árvore | G3 acusaria arquivo não declarado | Sempre `python3 -B`; arquivos adicionados por nome, nunca `git add -A` | N/A | G3 do publish-gate |

---

## Configuration

| Config Key | Type | Source / Default | Sensitive? | Description |
|---|---|---|---|---|
| `PUBLISH_GATE_MODE` | env | `ci` no Verify Gate e nos workflows | No | Camada genérica de padrões; o modo `port` exige a camada privada |
| `GH_TOKEN` | env | Token do próprio workflow, só no job `release` | Yes | Autoriza `gh release create`; nunca impresso |
| `timeout-minutes` | workflow | 10 em cada job | No | Teto da suíte e da publicação (resolve a Open Question do DEFINE) |
| `--root` | CLI | Raiz do pacote | No | Raiz que o check-versions inspeciona; os testes apontam para um repo temporário |

---

## Security Considerations

- Menor privilégio: permissão global `contents: read`; `contents: write` só no job `release`, que roda depois e só se `testes` passar.
- Actions fixadas por SHA (`actions/checkout@11d5960a326750d5838078e36cf38b85af677262`, igual ao workflow atual); publicação pelo `gh` do runner, sem action de terceiro.
- Integridade do pacote: `SHA256SUMS.txt` publicado junto; quem baixa confere com `shasum -a 256 -c`.
- PII: 3 padrões novos fail-closed; os testes nunca carregam o dado literal (Decision 5).
- Testes não leem `~/.gitconfig` nem credenciais de quem roda (`GIT_CONFIG_GLOBAL` vazio, `HOME` falso, `GIT_TERMINAL_PROMPT=0`) e não abrem rede.
- Nenhum script existente muda: o gate não é abrandado.

---

## Observability

| Aspect | Implementation | Signal / Why |
|---|---|---|
| Logging | Scripts novos terminam em `RESULTADO:` + `→`; `next-version.sh` imprime TAG/NEW/BASE no log do job | Diagnóstico de por que a release saiu ou não saiu |
| Metrics | Contagem de testes do unittest (`Ran N tests`) no log e no BUILD_REPORT | Rede de segurança mensurável |
| Tracing | N/A | Pipeline curto e linear |

---

## Requirements Traceability

| Requirement / AT | Design Element | Test / Gate |
|---|---|---|
| AT-001 | Sandbox sem rede e sem config global; manifest 1 | Verify Gate (cópia limpa) |
| AT-002, AT-003, AT-004, AT-005 | Suíte de contrato do verify-gate | `tests/test_verify_gate.py` |
| AT-006, AT-007 | Suíte do report-lint | `tests/test_report_lint.py` |
| AT-008, AT-009 | Suíte do skill-lint | `tests/test_skill_lint.py` |
| AT-010 | Suíte do playbook-lint | `tests/test_playbook_lint.py` |
| AT-011, AT-012, AT-013, AT-014, AT-015, AT-016 | Suíte do sdd-open | `tests/test_sdd_open.py` |
| AT-017, AT-018, AT-019 | check-versions (Decision 4) | `tests/test_check_versions.py` |
| AT-020 | Padrões de PII (Decision 5) | `tests/test_publish_gate_patterns.py` |
| AT-021, AT-022 | next-version (Decision 2) | `tests/test_next_version.py` |
| AT-023 | release.yml 2 jobs (Decision 3) | `tests/test_release_workflow.py` |
| AT-024 | release.yml publicação | `tests/test_release_workflow.py` + smoke pós-merge |
| AT-025 | Scripts e fixtures intocados | `tests/test_verify_gate.py` + `git diff 80d7887` |
| AT-026 | Sabotagem (Pattern 2) | Evidência no BUILD_REPORT |
| MUST nenhum script existente muda | Manifest sem `sdd/bin/*`, `bin/*`, `publish-gate.sh` | `git diff 80d7887` vazio nesses caminhos |

---

## Risks and Mitigations

| Risk | Impact | Mitigation | Residual Risk |
|---|---|---|---|
| Teste com literal que o publish-gate proíbe | Gate vermelho no próprio `tests/` | Decision 5; o Verify Gate roda o publish-gate antes da suíte | Baixo |
| Diferença BSD × GNU (`sed -i`, `grep`, `mktemp`) entre macOS e runner | Teste verde num lado e vermelho no outro | Testes não chamam `sed -i`; scripts novos usam só o portátil; suíte roda local (macOS) e no CI (Linux) | Baixo |
| Python 3.9 do macOS | Sintaxe 3.10+ quebra local | `from __future__ import annotations`; sem `match` nem `X \| Y` em runtime; suíte rodada com `/usr/bin/python3` | Baixo |
| Saída de teste falho contendo "command not found" | verify-gate devolve 3 em vez de 2 | Com `--strict` ambos são ≠ 0 (A-004 do DEFINE) | Aceito |
| Push de tag e push de `main` no mesmo commit | Duas execuções publicando a mesma tag | `concurrency` + Release existente encerra verde | Baixo |
| `gh` ausente ou sem permissão no runner (A-002) | Release não publica | Job vermelho com erro do `gh`; conferido no smoke pós-merge | Médio, conferido na tarefa 5 |
| Primeiro release automático no merge da F1 | `v2.2.1` inclui o `sdd-new-session` 1.0.0 sem tag | Registrado em Decision 3; notas geradas listam os commits | Aceito |

---

## Advisor Ledger

None — no formal external design review.

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | 2026-10-29 | SDD Design by RDD | Initial version |
| 1.1 | 2026-10-29 | SDD Build by RDD | Revisão de contexto fresco pós-build (Advisor Ledger do BUILD_REPORT): `next-version.sh` aceita a tag empurrada como argumento e exige que HEAD descenda da última tag quando NEW=1; gatilho só em tags vX.Y.Z; fila por ref; job `testes` confere sintaxe, zsh e symlink; `publish-gate.yml` com `permissions: contents: read`; `sdd/fixtures/**` nos paths do produto (o `init` copia as fixtures) |

---

## Next Step

Execute o **SDD Build by RDD**.
