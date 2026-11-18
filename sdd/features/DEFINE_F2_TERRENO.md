# DEFINE: F2 Terreno do sdd-open

> Portar do sdd-starter as skills de terreno (`sdd-checar-ambiente`, `sdd-higiene-dado`, `sdd-iniciar-repo`) com seus 105 testes, ligar o `checar.sh` ao `doctor` (segredo salvo no git) e à `sdd-new-session` (pré-voo, tabela de tradução, descoberta dos slots do `config.yaml`).

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | F2_TERRENO |
| **Date** | 2026-10-29 |
| **Author** | SDD Define by RDD (sessão com Roberto Dias Duarte) |
| **Status** | Ready for Design |
| **Clarity Score** | 14/15 |

---

## Problem Statement

O sdd-open não confere o terreno antes da spec: pasta sincronizada pela nuvem, projeto sem git, remoto inacessível, senha ou certificado já salvos no git e dado de cliente indo para o commit só aparecem no meio do trabalho; a `sdd-new-session` 1.0.0 cobre só o remoto e deixa os slots vazios do `sdd/config.yaml` para o usuário. O sdd-starter já resolve isso com 3 skills e 105 testes verdes, que precisam entrar no open sem perder a prova, sem violar o publish-gate e sem ir parar no projeto do usuário como teste.

---

## Target Users

| User | Role | Pain Point |
|---|---|---|
| Usuário/aluno do sdd-open | Quem instala o framework (`init`/`doctor`) e abre frentes (`sdd-new-session`) | Descobre tarde que a pasta está na nuvem, que o remoto não responde ou que um `.env` já está no git; preenche à mão slots que dava para descobrir |
| Mantenedor do sdd-open | Roberto e os agentes de F3–F6 | Precisa que o comportamento portado continue provado por teste e que o script e a tabela de tradução da `new-session` não divirjam calados |

---

## Goals

| Priority | Goal |
|---|---|
| **MUST** | `.agents/skills/sdd-checar-ambiente` (1.3.0), `sdd-higiene-dado` (1.1.1) e `sdd-iniciar-repo` (1.1.1) portadas por transplante com adaptação mínima: literais do G2, links/rodapé `sdd-starter` → `sdd-open`, sem `npx … sdd-starter`, sem `sdd/ambiente.md`, sem `agents/openai.yaml` |
| **MUST** | Os 105 testes do starter em `tests/` na raiz (`test_checar.py`, `test_alarme.py`, `test_inventario.py`), verdes junto com os 115 da F1, sem rede |
| **MUST** | `checar.sh --segredo`: só dado exposto (`.env`/`.env.*` exceto `.env.example`/`.env.sample`, `.pfx`, `.p12` rastreados; `.pem` rastreado com `PRIVATE KEY`), sem rede; exit 0 sem achado, 1 com achado |
| **MUST** | `doctor` chama o `checar.sh --segredo` do pacote e mostra cada achado como ⚠️; continua saindo 0 com a linha `RESULTADO` |
| **MUST** | `sdd-new-session` 1.1.0: pré-voo por `checar.sh --frente` com tabela de tradução e o Passo 0 à mão como fallback; descoberta gravada só em slot vazio do `sdd/config.yaml` da frente, com evidência |
| **MUST** | Prova de que os testes discriminam: 5 sabotagens (`checar.sh`, `alarme.sh`, `pre-commit.sh`, `inventario.sh`, `doctor`) no BUILD_REPORT |
| **MUST** | Nenhuma regressão: 115 testes da F1, exits do `verify-gate.sh`, fixtures, `sync` idempotente, publish-gate e check-versions verdes |
| **SHOULD** | `alarme.sh instalar` grava o hook sem as linhas `sdd-open:generated` da cópia gerada |
| **SHOULD** | Teste que amarra cada mensagem de bloqueio do `checar.sh --frente` a uma linha da tabela da `new-session` |
| **COULD** | Teste de conteúdo da `new-session` que acusa a falta das regras de descoberta (slot vazio, frente, evidência, `default_branch` divergente) |

---

## Success Criteria

- [ ] `python3 -B -m unittest discover -s tests -p 'test_*.py'` sai 0 com o `/usr/bin/python3` 3.9.6 + `/bin/bash` 3.2.57 do macOS e no `ubuntu-latest` do CI, com ≥ 220 testes (115 da F1 + 105 portados) e 0 skip além do `GateInteiro` sem gitleaks.
- [ ] `python3 sdd/bin/skill-lint.py .agents/skills/sdd-*/SKILL.md` sai 0 sobre as 16 skills; `find .agents/skills -name openai.yaml` não acha nada.
- [ ] `grep -rIl -e sdd-starter -e 'npx skills add' -e 'sdd/ambiente.md'` nas 3 pastas portadas não acha nada.
- [ ] 5 de 5 sabotagens registradas no BUILD_REPORT com: a alteração, o nome do teste que ficou vermelho e a reversão (`git checkout`) com a suíte verde de novo.
- [ ] `git diff v2.2.1 -- sdd/ scripts/publish-gate.sh scripts/publish-gate-patterns.txt .github/` vazio ao fim da F2.
- [ ] `python3 scripts/check-versions.py --base v2.2.1 --base-obrigatoria` sai 0.
- [ ] O Verify Gate abaixo sai 0 com `--strict`.
- [ ] Depois do merge em `main`, `gh release view <tag> -R robertodiasduarte/sdd-open` mostra `SHA256SUMS.txt` e `shasum -a 256 -c SHA256SUMS.txt` sai 0 sobre o pacote baixado.

---

## Acceptance Tests

| ID | Pattern | Criterion (EARS) | Gate (`kind`) |
|---|---|---|---|
| AT-001 | Event-driven | **When** `python3 -B -m unittest discover -s tests -p 'test_*.py'` runs on a clean copy of the tree, the system **shall** exit 0 with the 105 ported tests and the 115 F1 tests passing, without network access and without reading the caller's `~/.gitconfig` | test |
| AT-002 | Event-driven | **When** `skill-lint.py` runs over `.agents/skills/sdd-*/SKILL.md`, the system **shall** exit 0 for the 16 skills, and none of `sdd-checar-ambiente`, `sdd-higiene-dado`, `sdd-iniciar-repo` **shall** contain `agents/openai.yaml` | test |
| AT-003 | Unwanted | **If** a file in the 3 ported skill folders references `sdd-starter`, `npx skills add` or `sdd/ambiente.md`, **then** the test suite **shall** fail naming the file | test |
| AT-004 | Event-driven | **When** `checar.sh --segredo` runs in a repository that tracks `.env`, `.env.local`, a `.pfx`, a `.p12` or a `.pem` containing `PRIVATE KEY`, the system **shall** exit 1 and print each file with the `git rm --cached` command and the follow-up measure (change the password, revoke the certificate, replace the key) | test |
| AT-005 | Event-driven | **When** `checar.sh --segredo` runs in a repository that tracks only `.env.example`, `.env.sample` and a `.pem` without `PRIVATE KEY`, the system **shall** exit 0 with no finding | test |
| AT-006 | Unwanted | **If** `checar.sh --segredo` runs with an `origin` that hangs and a GitHub API URL that never answers, **then** it **shall** finish in under 3 seconds without calling `curl` or `git ls-remote` | test |
| AT-007 | Event-driven | **When** `sdd-open.sh doctor` runs in an initialized project that has `.env` committed, the system **shall** print a ⚠️ line naming `.env` and the command that removes it from the git, and **shall** exit 0 ending with the `RESULTADO:` line | test |
| AT-008 | Event-driven | **When** `sdd-open.sh doctor` runs in an initialized project with no tracked secret, the system **shall** print a ✅ line saying no secret is saved in the git and exit 0 | test |
| AT-009 | Unwanted | **If** the package has no `.agents/skills/sdd-checar-ambiente/scripts/checar.sh`, **then** `doctor` **shall** print a ⚠️ line saying the package is incomplete and **shall continue to** exit 0 | test |
| AT-010 | Event-driven | **When** `alarme.sh instalar` runs from a copy of `sdd-higiene-dado` whose `pre-commit.sh` carries the two `sdd-open:generated` lines, the system **shall** write a `.git/hooks/pre-commit` without `sdd-open:generated`, and `alarme.sh verificar` **shall** then report the alarm as this skill's own | test |
| AT-011 | Unwanted | **If** a staged change adds a CPF or CNPJ with a valid check digit, a `.env`, a `.pfx`/`.p12`, a `.pem` with `PRIVATE KEY` or a new spreadsheet, **then** the installed pre-commit **shall** refuse the commit, and it **shall** accept the same commit without those (ported contract of `test_alarme.py`) | test |
| AT-012 | Unwanted | **If** `alarme.sh instalar` finds `core.hooksPath` set or a pre-commit of another origin, **then** it **shall** exit 2 without writing the hook (ported contract) | test |
| AT-013 | Event-driven | **When** `inventario.sh` runs in a folder with `.env`, `.pfx`, a spreadsheet, a file over 50 MB or a secret already in the git history, the system **shall** flag each one (ported contract of `test_inventario.py`) | test |
| AT-014 | Unwanted | **If** `checar.sh --frente` finds the folder synced by a cloud provider, a home folder, a project in a subfolder, an empty folder, a project without git, no remote, no `origin`, a refused credential, an unconfirmed SSH host, an editor login window waiting, no network or an empty remote, **then** it **shall** exit 1, print the block under `🔴 Impede o trabalho` and end with "Nada foi criado." (ported contract of `test_checar.py`) | test |
| AT-015 | Event-driven | **When** the matrix test collects every blocking message that `checar.sh --frente` can emit, the system **shall** find a row for each one in the translation table of `.agents/skills/sdd-new-session/SKILL.md`, and **shall** fail naming any message without a row | test |
| AT-016 | Event-driven | **When** the content test reads `.agents/skills/sdd-new-session/SKILL.md`, the system **shall** find: the call to `checar.sh --frente` with exit 1 ⇒ stop and exit 0 + `✅ Pronto para abrir a frente` ⇒ go on; the hand-written Passo 0 as fallback; writing only empty slots of the new worktree's `sdd/config.yaml` with a `# descoberto por sdd-new-session` evidence line above; the stop when a filled `project.default_branch` diverges from the remote HEAD; `test_cmd`/`lint_cmd` only from literal evidence; and `metadata.version` `1.1.0` | test |
| AT-017 | Unwanted | **If** any file in the tree matches a pattern of `scripts/publish-gate-patterns.txt` outside the `example.com/.org/.net` exemption, **then** `PUBLISH_GATE_MODE=ci bash scripts/publish-gate.sh` **shall** exit non-zero; on the F2 tree it **shall** exit 0 | test |
| AT-018 | Event-driven | **When** `check-versions.py --base v2.2.1 --base-obrigatoria` runs on the F2 tree, the system **shall** exit 0 with `sdd-checar-ambiente` 1.3.0, `sdd-higiene-dado` 1.1.1, `sdd-iniciar-repo` 1.1.1 and `sdd-new-session` 1.1.0 | test |
| AT-019 | Event-driven | **When** `init --yes` then `sync --yes` run in a fresh repository with the 16 skills, the system **shall** leave `git status --porcelain` empty, `sync --check` **shall** exit 0, and the generated copies of `checar.sh`, `alarme.sh`, `pre-commit.sh` and `inventario.sh` **shall** pass `bash -n` | test |
| AT-020 | Non-regression | The system **shall continue to** pass the 115 F1 tests, return exits 0/2/3/4/5/64 from `verify-gate.sh`, keep `sdd/fixtures/` byte-identical and keep `doctor` exiting 0 with its `RESULTADO:` line | test |
| AT-021 | Unwanted | **If** a contract is broken on purpose in `checar.sh`, `alarme.sh`, `pre-commit.sh`, `inventario.sh` or the `doctor` (sabotage), **then** at least one named test **shall** fail, and reverting it with `git checkout` **shall** turn the suite green again | test |

---

## Clarifications

### Session 2026-10-29

- [x] (Constraints) O `cmd` do Verify Gate não pode ter aspas duplas internas (`verify-gate.sh` só tira as aspas das pontas e roda com `bash -c` da raiz) → o `cmd` pedido já vem sem aspas internas; integrado em Verify Gate.
- [x] (Done signal) "Número de testes novos além dos 105" ficou TBD no Brainstorm → critério é cobertura de contrato + sabotagem; o piso numérico é só o que já existe (115 + 105 = 220); integrado em Success Criteria.
- [x] (Edge cases) Linha de base medida antes de escrever os ATs: os 3 testes do starter passam nesta máquina (`/usr/bin/python3` 3.9.6, `/bin/bash` 3.2.57): 53 em 105,8 s, 28 em 8,8 s, 24 em 3,9 s → AT-011 a AT-014 citam esses contratos como portados; o tempo vira Open Question não bloqueante.
- [x] (Data model) A mensagem de achado do `checar.sh` já diz "Tirar do git não apaga do histórico" quando o repositório não é público (seção 6 do script); no `--segredo` não há consulta de rede, então vale sempre essa variante → integrado em AT-004 e Assumptions (A-002).
- [x] (Terminology) "Segredo no histórico" do handoff = o que está salvo no git **agora** (`git ls-files`/`git grep --cached`); commit antigo de onde o arquivo foi removido não é visto → integrado em Goals e Out of Scope.
- [x] (UX flow) A `sdd-new-session` é texto lido pelo agente; o comportamento do agente não é executável em teste → AT-015/AT-016 conferem o **contrato escrito** na SKILL.md; a obediência do agente fica em Assumptions (A-003).

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

O gate só enxerga o que está commitado (`git archive HEAD`): o Build commita na branch antes de rodar. `PUBLISH_GATE_MODE=ci` porque o modo padrão exige a camada privada de padrões. A Release (último Success Criterion) é conferida depois do merge, fora deste gate, com `gh release view` e `shasum -a 256 -c`.

---

## Out of Scope

- Redesenhar a CLI ou o `config.yaml`; `doctor --repo`; `init` oferecendo a `sdd-iniciar-repo` quando não há git.
- Ligar `pre-commit.sh` ou `checar.sh --segredo` ao `release.landmines_cmd`.
- Achar segredo em commits antigos de onde o arquivo já foi removido (varredura do histórico inteiro).
- Camada "Como falar com o aluno" nas skills nativas, inclusive na `sdd-new-session` (F4); `design-lint`/`handoff-lint` (F4).
- Migration e bloco do "go" (F3).
- README, `AGENTS.md.tmpl` e docs citando as skills novas (F6).
- `sdd/ambiente.md`, cenário de branching A/B/C, `agents/openai.yaml`; descobrir `typecheck_cmd`, `layers`, `deploy`.
- Alterar o sdd-starter; modo `briefs`; `checar.sh` em PowerShell; teste no Windows.

---

## Constraints

| Type | Constraint | Impact |
|---|---|---|
| Technical | bash 3.2, sem `grep -P`, `readlink -f`, `declare -A`, `mapfile`, zsh ou symlink; Python ≥ 3.9 só com stdlib; `python3 -B` sempre | Scripts e testes rodam no macOS de fábrica e no runner |
| Technical | Testes sem rede e sem a configuração git de quem roda; hosts de teste em `.invalid` | Host `.invalid` preservado e montado por concatenação, nunca trocado por `example.com` |
| Technical | G2 do publish-gate: nenhum literal casa com `scripts/publish-gate-patterns.txt` fora de `example.com/.org/.net` (isenção só em padrão de e-mail) | E-mails em `example.com`; CPF/CNPJ/`git@` de amostra montados em tempo de execução |
| Technical | G3: `MANIFEST.txt` é allowlist nos dois sentidos, ordem `LC_ALL=C` | Todo arquivo novo declarado no mesmo commit; `git add` por nome; `sdd/features/`, `sdd/handoffs/`, `sdd/reports/` fora do commit |
| Technical | `init` copia a pasta inteira da skill e `sync` replica cada arquivo com cabeçalho `sdd-open:generated` | Nada de teste dentro de `.agents/skills/`; scripts portados precisam funcionar também como cópia gerada |
| Technical | Skill nova ou alterada com `metadata.version` X.Y.Z e bump contra `v2.2.1` | Versões fixadas em AT-018 |
| Technical | `doctor` roda no fim de todo `init` e os testes de `test_sdd_open.py` fazem `init` | `--segredo` sem rede e rápido; `doctor` continua saindo 0 |
| Other | Comandos remotos com `GIT_TERMINAL_PROMPT=0`; push em `main` só com OK explícito citando "sdd-open", após PR com CI verde | A Release depende desse OK |

---

## Technical Context

| Aspect | Value | Notes |
|---|---|---|
| **Deployment Location** | `.agents/skills/sdd-checar-ambiente/`, `sdd-higiene-dado/`, `sdd-iniciar-repo/` (novos); `.agents/skills/sdd-new-session/SKILL.md`; `bin/sdd-open.sh` (`doctor`); `tests/test_checar.py`, `test_alarme.py`, `test_inventario.py`, `test_matriz_new_session.py` (novos); `tests/test_sdd_open.py`; `MANIFEST.txt` | Fonte: `/Users/robertoduarte/rdd-public/sdd-starter` em `17c69c4` |
| **KB Domains** | N/A | Contrato vem dos scripts e dos 105 testes do starter |
| **IaC Impact** | None | Workflows da F1 sem mudança; o push em `main` publica a Release sozinho porque toca `.agents/skills/**` e `bin/**` |
| **LLM Prompts** | false | Nenhum prompt de runtime: scripts, testes e texto de skill lido pelo agente de desenvolvimento |

---

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|---|---|---|---|
| A-001 | Os 105 testes do starter passam com `/usr/bin/python3` 3.9.6 e `/bin/bash` 3.2.57 | O porte partiria de uma base vermelha | yes — rodados em 2026-10-29: 53/28/24 OK |
| A-002 | Sem rede, o `--segredo` usa a variante "Tirar do git não apaga do histórico" do texto de achado | O texto prometeria algo errado sobre repositório público | yes — seção 6 de `checar.sh` lida |
| A-003 | O agente segue a tabela e as regras de descoberta escritas na `sdd-new-session` | O contrato escrito passaria e o agente faria outra coisa | no — não executável em teste; mitigado por AT-015/AT-016 |
| A-004 | O cabeçalho `sdd-open:generated` entra depois do shebang (linhas 2–3) nos `.sh` gerados | O teste do AT-010 cobriria o caso errado | yes — `perfil_arquivo()`/`renderizar_gerado()` em `bin/sdd-open.sh` |
| A-005 | O `doctor` acha o `checar.sh` em `${PKG}/.agents/skills/sdd-checar-ambiente/scripts/` em todo pacote (clone ou `git archive`) | `doctor` cairia sempre no ⚠️ "pacote incompleto" | no — conferir no Build com a cópia de `git archive` |

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---|---:|---|
| Problem | 3 | Dor, quem sente e o que falta no open, com números medidos |
| Users | 3 | Usuário/aluno e mantenedor, cada um com dor específica |
| Goals | 3 | MUST/SHOULD/COULD confirmados no Brainstorm e nos 2 checkpoints |
| Success | 2 | Todos observáveis; a obediência do agente à `new-session` só é provada pelo contrato escrito |
| Scope | 3 | YAGNI e destinos (F3, F4, F6) registrados |
| **Total** | **14/15** | |

Minimum to proceed: **12/15**.

---

## Open Questions

- Tempo da suíte: `test_checar.py` leva ~106 s nesta máquina e a suíte inteira passa de ~35 s para ~2,5 min (não bloqueante: o Design decide se mantém, encurta tetos por variável de ambiente já existente no script, ou fixa `timeout-minutes` no CI).

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | 2026-10-29 | SDD Define by RDD | Initial version |

---

## Next Step

Execute o **SDD Design by RDD**.
