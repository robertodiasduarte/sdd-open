# BRAINSTORM: F1 Manutenção do sdd-open

> Exploratory session to clarify intent and approach before requirements capture

## Metadata

| Attribute | Value |
|---|---|
| Feature | F1_MANUTENCAO |
| Date | 2026-10-29 |
| Author | brainstorm-agent |
| Status | Handoff Ready |

## Initial Idea

**Raw Input:** "F1 Manutenção — testes unitários dos scripts `bin/sdd-open.sh`, `sdd/bin/verify-gate.sh`, `report-lint.py`, `skill-lint.py`, `playbook-lint.sh`; `check-versions.py` e linha de identificação nas 13 skills; auto-release com 2 jobs e `SHA256SUMS.txt`; `design-lint.py` e `handoff-lint.py` com `gate.sh`; padrões de PII em `scripts/publish-gate-patterns.txt`; `doctor` com segredo já no histórico." (linha F1 da tabela "Frentes, em ordem" de `sdd/features/AVALIACAO_STARTER_PARA_OPEN.md`)

**Context Gathered:**
- Provided: F1 é a primeira de 6 frentes para incorporar no sdd-open o que o sdd-starter v1.5.15 faz melhor; F2 porta ~1.000 linhas de script do starter (`checar.sh`, `alarme.sh`, `inventario.sh`) e F4 toca as 13 skills do open.
- Provided: as 5 decisões da frente estão registradas em `sdd/handoffs/HANDOFF_INCORPORAR_STARTER.md` (fonte canônica = open; conversa sempre ligada; Status `✅ ▶️ ⬜ ⏸️ ➖` com kanban intacto; descoberta nos slots do `config.yaml`; starter vira distribuição gerada do open, em frente própria).
- Provided: regras que não podem quebrar — `MANIFEST.txt` declara todo arquivo novo; `sync` idempotente; sem zsh, sem symlink, bash 3.2; os seis exits do `verify-gate.sh` e o comportamento das fixtures ficam idênticos; nenhum comando, condição, ordem de passo ou slot muda nas skills nativas nesta frente.
- Observed: o open tem 0 testes unitários; o CI (`.github/workflows/publish-gate.yml`) confere 3 dos 6 exits (5, 0, 64) mais `--strict`, o `playbook-lint.sh --self-test`, o `skill-lint.py` e o smoke do gerador.
- Observed: `scripts/publish-gate-patterns.txt` já tem `[0-9]{11,}` (CPF sem pontuação), e-mail fora de `example.*` e telefone `+NN`; faltam CPF e CNPJ com pontuação e telefone BR sem `+`. Os três padrões candidatos não acusam nada na árvore atual (`git ls-files | xargs grep -E …` saiu 1).
- Observed: o `checar.sh` do starter já confere segredo no histórico (`git ls-files` para `.env`, `.pfx`, `.p12`; `git grep --cached "PRIVATE KEY"` em `*.pem`) e entra no open na F2.
- Observed: os templates do open divergem dos do starter — `sdd/templates/HANDOFF_TEMPLATE.md` tem Ficha/Feito/Falta/Definition of Done/Landmines/Prompt de retomada/Histórico de slices; `DESIGN_TEMPLATE.md` tem Landmines aplicáveis, Contrato de aceite e Agent Assignment Rationale e não tem Requirements Traceability nem Advisor Ledger. `validate_design.py` e `validate_handoff.py` do starter não servem sem reescrita.
- Observed: o remoto tem 5 tags anotadas feitas à mão (`v1.0.0`, `v2.0.0`, `v2.0.1`, `v2.1.0`, `v2.2.0`) e nenhuma Release; o HEAD `80d7887` está depois de `v2.2.0`, sem tag. Desde `v2.2.0`, as skills alteradas já subiram de versão (`sdd-release` 2.0.0 → 2.1.0; `sdd-new-session` nova, 1.0.0).
- Observed: 12 das 13 skills têm `metadata.version`; `sdd-auditoria-harness` não tem. Nenhuma tem `metadata.updated`.
- Observed: `init` copia para o projeto do usuário só `sdd/templates`, `sdd/bin` e `sdd/playbook.md` (`sdd_faltantes` em `bin/sdd-open.sh`); uma pasta `tests/` na raiz nunca chega ao usuário.
- Observed: gitleaks 8.30.1 instalado localmente (mesma versão do CI); `python3` do sistema macOS é 3.9.6.

**Technical Context Observed (for Define):**

| Aspect | Observation | Implication |
|---|---|---|
| Likely Location | `tests/` (novo, raiz), `scripts/check-versions.py` (novo), `.github/workflows/release.yml` (novo), `scripts/publish-gate-patterns.txt`, `.github/workflows/publish-gate.yml`, `MANIFEST.txt`, `.agents/skills/sdd-auditoria-harness/SKILL.md` | Todo arquivo novo entra no `MANIFEST.txt` no mesmo commit (G3 do publish-gate é allowlist nos dois sentidos) |
| Relevant KB Domains | N/A — sem KB no projeto | Contratos vêm dos próprios scripts e de `docs/verify-gate-contract.md` |
| IaC Patterns | GitHub Actions com actions fixadas por SHA; `ubuntu-latest`; gitleaks instalado por curl com versão fixada | O workflow novo segue o mesmo padrão de fixação |

## Discovery Questions & Answers

| # | Question | Answer | Impact |
|---|---|---|---|
| 1 | Qual o problema principal que a F1 resolve antes da F2? | Rede de segurança: testes que acusem se algo do open quebrou antes de portar scripts (F2) e mexer nas skills (F4). | Prioridade nos testes dos 5 scripts; o resto da F1 serve à rede ou é cortado. |
| 2 | Quem decide o número da versão daqui pra frente? | Automático no push, como no starter (contra a recomendação de tag manual). | Workflow de release no push de `main` com patch automático; minor/major seguem por tag manual, que também precisa virar Release. |
| 3 | O que fazer com design-lint e handoff-lint, que não podem ser portados e que nenhuma skill chamaria nesta frente? | Adiar para a F4. | Saem da F1; o padrão "aceita o exemplo e rejeita fixtures ruins" entra já, aplicado ao report-lint e ao skill-lint. |
| 4 | Qual critério de sucesso para os testes? | Contrato + sabotagem: cada comportamento documentado tem um teste, e o BUILD_REPORT mostra uma sabotagem por script (quebra proposital → teste vermelho → desfaz). | Define os ATs e a evidência exigida no Build. |

## Sample Data Inventory

| Type | Location | Count | Notes |
|---|---|---:|---|
| Input files | `sdd/fixtures/DEFINE_FIXTURE_*.md`, `sdd/fixtures/playbook/*.md` | 8 | Fixtures existentes do gate e do playbook; ficam idênticas |
| Output examples | N/A | 0 | Usuário não forneceu |
| Ground truth | `docs/verify-gate-contract.md`; docstrings de `report-lint.py`, `skill-lint.py`, `verify-gate.sh`; `ajuda()` de `bin/sdd-open.sh` | 4 | Contratos documentados = casos de teste |
| Related code | starter: `skills/sdd-iniciar-repo/tests/test_inventario.py`, `skills/sdd-checar-ambiente/tests/test_checar.py`, `scripts/check-versions.py`, `.github/workflows/auto-release.yml`, `skills/sdd-handoff/scripts/gate.sh` | 5 | Padrão de estilo (sem rede, git isolado) e de desenho do release com 2 jobs |

**How samples will be used:**
- As fixtures existentes viram entrada dos testes sem alteração.
- Os testes do starter dão o padrão: `subprocess` em pasta temporária, `GIT_CONFIG_GLOBAL` vazio, `GIT_CONFIG_NOSYSTEM=1`, `GIT_CEILING_DIRECTORIES`, `HOME` falso, `stdin=DEVNULL`, `timeout`.
- `check-versions.py` e `auto-release.yml` do starter são a base, adaptados ao open (`.agents/skills/`, tarball do framework em vez de zips por skill, sem linha de identificação).

## Approaches Explored

### Approach A: `tests/` na raiz em Python unittest, caixa-preta — Recommended

**Description:** Um arquivo `test_*.py` por script, rodando o script real por `subprocess` em pasta temporária com git isolado e sem rede. Roda com `python3 -B -m unittest discover -s tests -p 'test_*.py'`.

**Pros:**
- Zero dependência nova: `python3` já é requisito do open.
- Fora de `sdd/` e `.agents/`: `init` e `sync` nunca copiam teste para o projeto do usuário.
- Mesmo estilo dos testes do starter que a F2 vai trazer.

**Cons:**
- Testar bash a partir de Python é mais verboso.
- Os exits 5/0/64 passam a ser conferidos também nos checks inline do CI (redundância aceita).

**Why Recommended:** única opção que mantém o teste fora do que vai ao usuário, sem dependência nova, e que já roda com o `cmd` do Verify Gate definido.

### Approach B: bats-core para bash + unittest para Python

**Description:** Testes de bash em `.bats`, testes de Python em unittest.

**Pros:**
- Testes de bash curtos e idiomáticos.

**Cons:**
- Dois frameworks; bats não vem no macOS nem no runner — dependência nova no CI e na máquina de quem contribui.
- Fica isolado dos testes Python que a F2 traz.

### Approach C: `--self-test` dentro de cada script

**Description:** Cada script ganha um modo de auto-teste, como o `playbook-lint.sh --self-test` já faz.

**Pros:**
- Nenhuma pasta nova; o script prova a si mesmo.

**Cons:**
- O teste vai para o projeto de todo usuário (`sdd/bin/` é copiado pelo `init`).
- `bin/sdd-open.sh` (639 linhas) cresce muito.
- Sabotagem difícil de provar: o teste mora no arquivo sabotado.

## Selected Approach

| Attribute | Value |
|---|---|
| Chosen | Approach A |
| User Confirmation | 2026-10-29, escolha explícita "A — tests/ em Python" |
| Reasoning | Teste fora do que é instalado no usuário, sem dependência nova, alinhado aos testes da F2 e ao `cmd` do Verify Gate |

## Key Decisions Made

| # | Decision | Rationale | Alternative Rejected |
|---|---|---|---|
| 1 | F1 é rede de segurança antes da F2 | F2 porta ~1.000 linhas e F4 toca as 13 skills; sem teste, uma regressão do open passa despercebida | Os seis itens por igual |
| 2 | Release automática no push de `main`, patch calculado da última tag `v*`; tag manual `v*` também vira Release | Escolha do Roberto; o minor com mensagem escrita continua possível | Só tag manual (recomendada e rejeitada); botão "Run workflow" |
| 3 | Push que só toca docs, testes ou workflow não publica | Release só quando o produto muda: `.agents/skills/**`, `bin/**`, `sdd/bin/**`, `sdd/templates/**`, `sdd/playbook.md`, `sdd/config.example.yaml`, `AGENTS.md.tmpl` | Publicar em todo push |
| 4 | Commit que já tem tag `v*` não ganha outra | Evita `v2.3.0` manual e `v2.3.1` automática no mesmo commit | Confiar só na fila |
| 5 | Dois jobs: `testes` só com leitura, `release` com `needs: testes` e `contents: write` | Teste vermelho ⇒ `release` skipped, sem tag; token de escrita só onde é preciso | Um job só |
| 6 | Publicação por `gh release create` | Já vem no runner; uma action de terceiro a menos | `softprops/action-gh-release` (usada no starter) |
| 7 | Pacote `sdd-open-vX.Y.Z.tar.gz` por `git archive` + `SHA256SUMS.txt` | O open se instala por clone, não por zip por skill; o tarball automático do GitHub não tem hash garantido como estável | Zips por skill (ficam para a frente do starter gerado) |
| 8 | check-versions confere versão X.Y.Z, coerência com `manifest.json`/`evals/cases.json` e bump contra a última tag com base obrigatória no release | A versão não pode mentir quando F2–F6 mexerem nas skills | Checagem só estrutural |
| 9 | Critério de sucesso: um teste por contrato + uma sabotagem provada por script no BUILD_REPORT | Teste que nunca fica vermelho não prova nada | Só contrato; meta de número de testes |
| 10 | Build commita na branch antes de rodar o Verify Gate | O `cmd` usa `git archive HEAD`, que ignora o que não está commitado | Copiar a árvore de trabalho |
| 11 | Checks inline existentes do `publish-gate.yml` ficam como estão; o workflow ganha steps de unittest e check-versions | O comportamento das fixtures tem de ficar idêntico | Migrar os checks para `tests/` |

## Features Removed (YAGNI)

| Feature Suggested | Reason Removed/Deferred | Can Add Later? |
|---|---|---|
| `metadata.updated` + linha de identificação nas 13 skills | Comportamento de conversa; tocaria as 13 skills e obrigaria subir todas as versões agora. Na F4 elas já serão tocadas e sobem uma vez | Yes — F4 |
| `design-lint.py` e `handoff-lint.py` com `gate.sh` | Templates do open divergem (reescrita, não porte) e nenhuma skill os chamaria nesta frente | Yes — F4 |
| `doctor` com segredo já no histórico | O `checar.sh` do starter já faz e chega na F2 com `doctor --repo` | Yes — F2 |
| Checagem de `description` ≤ 1024 no check-versions | `skill-lint.py` já faz | N/A |
| Migrar os checks inline do `publish-gate.yml` para `tests/` | Funcionam; o comportamento das fixtures tem de ficar idêntico | Yes |
| Ferramenta automática de mutação | Sabotagem manual, uma por script, registrada no BUILD_REPORT, basta para provar que o teste discrimina | Yes |

## Incremental Validations

| Section | Presented | User Feedback | Adjusted? |
|---|---|---|---|
| Checkpoint 1 — componentes e limites: `tests/` com 7 arquivos, `check-versions.py`, `release.yml` com 2 jobs e tarball + SHA256SUMS, 3 padrões de PII, 2 steps novos no `publish-gate.yml`, nenhum script existente muda de comportamento | Yes | "Certo, seguir" | No |
| Checkpoint 2 — gatilhos, falhas e dependências: paths do produto, tag manual vira Release, sem tag dupla, teste vermelho sem tag, `gh release create`, tarball + SHA256SUMS, commit antes do gate, Python ≥ 3.9 | Yes | "Certo, gerar o brainstorm" | No |

## Suggested Requirements for /define

### Problem Statement (Draft)

O sdd-open não tem nenhum teste unitário nem Release publicada, e as próximas frentes vão portar ~1.000 linhas de script e tocar as 13 skills; sem uma rede de segurança, uma regressão no gate, nos linters ou no gerador passa despercebida, e quem instala não tem como conferir qual versão recebeu.

### Target Users (Draft)

| User | Pain Point |
|---|---|
| Mantenedor do sdd-open (Roberto e agentes que executam F2–F6) | Mudança em script ou skill pode quebrar contrato sem nenhum teste acusar |
| Quem instala o sdd-open | Não há Release com pacote e hash para saber e conferir a versão recebida |

### Success Criteria (Draft)

- [ ] Cada comportamento documentado dos 5 scripts (`verify-gate.sh` com os 6 exits, `--print`, `--strict`, `contains:`; `report-lint.py`; `skill-lint.py`; `playbook-lint.sh`; `bin/sdd-open.sh` init/sync/`--check`/doctor/merge do AGENTS.md/verbo inválido) tem pelo menos um teste em `tests/`.
- [ ] `python3 -B -m unittest discover -s tests -p 'test_*.py'` sai 0 em Python 3.9 e no runner do CI.
- [ ] O BUILD_REPORT registra uma sabotagem por script (5 scripts + `check-versions.py`): a alteração, o teste que ficou vermelho e a reversão.
- [ ] `scripts/check-versions.py --base <última tag>` sai 0 na árvore da F1 e sai 1 numa fixture com skill alterada sem bump.
- [ ] Os 3 padrões novos de PII pegam o caso positivo e não pegam o vizinho inofensivo; `publish-gate.sh` em modo `ci` sai 0 na cópia limpa da árvore.
- [ ] Depois do merge em `main`, existe uma Release `v2.2.1` (ou a próxima) com `sdd-open-vX.Y.Z.tar.gz` e `SHA256SUMS.txt` que confere com `shasum -a 256 -c`.
- [ ] Número mínimo de testes por script: TBD — o critério é cobertura de contrato, não quantidade.

### Constraints Identified

- bash 3.2, sem `declare -A`, sem zsh, sem symlink; Python ≥ 3.9 só com stdlib.
- Testes sem rede, sem ler `~/.gitconfig` de quem roda.
- Todo arquivo novo no `MANIFEST.txt` no mesmo commit; `sdd/features/`, `sdd/handoffs/`, `sdd/reports/` ficam fora do commit.
- Os seis exits do `verify-gate.sh` e as fixtures em `sdd/fixtures/` ficam idênticos; nenhum script existente muda de comportamento.
- Nas skills nativas, nenhum comando, condição, ordem de passo ou slot muda; a única mudança em skill é `version` na `sdd-auditoria-harness`.
- `sync` idempotente; smoke do CI continua verde.
- Comando que fala com o remoto roda com `GIT_TERMINAL_PROMPT=0`; push em `main` só com OK explícito citando "sdd-open", depois de PR com CI verde.
- Verify Gate roda o publish-gate em `PUBLISH_GATE_MODE=ci` sobre `git archive HEAD`; o Build commita na branch antes de rodar.

### Out of Scope (Confirmed)

- Linha de identificação e `metadata.updated` nas skills (F4).
- `design-lint.py`, `handoff-lint.py` e `gate.sh` de documento (F4).
- `doctor` com segredo no histórico (F2).
- Redesenhar CLI ou `config.yaml`; modo `briefs`; curadoria do playbook; alterar o sdd-starter; teste no Windows.
- Ferramenta automática de mutação.

## Session Summary

| Metric | Value |
|---|---:|
| Questions Asked | 5 |
| Approaches Explored | 3 |
| Features Removed (YAGNI) | 6 |
| Validations Completed | 2 |

## Next Step

Execute o **SDD Define by RDD**.
