# BRAINSTORM: F2 Terreno do sdd-open

> Exploratory session to clarify intent and approach before requirements capture

## Metadata

| Attribute | Value |
|---|---|
| Feature | F2_TERRENO |
| Date | 2026-10-29 |
| Author | brainstorm-agent |
| Status | Handoff Ready |

## Initial Idea

**Raw Input:** "F2 Terreno — checar-ambiente, higiene-dado, iniciar-repo portadas com seus testes e com a seção do aluno já ajustada aos símbolos; new-session com pré-voo, matriz e descoberta dos slots" (linha F2 da tabela "Frentes, em ordem" de `sdd/features/AVALIACAO_STARTER_PARA_OPEN.md`), mais, do handoff da F1: "`doctor` com segredo no histórico (o `checar.sh` já faz)".

**Context Gathered:**
- Provided: F2 é a segunda de 6 frentes; F1 entregou 115 testes em `tests/`, `check-versions.py` e release automática (`v2.2.1`, tag em `f75fbdb`). Decisões já tomadas, não reabertas: fonte canônica das 3 skills compartilhadas = open; camada de conversa sempre ligada; Status `✅ ▶️ ⬜ ⏸️ ➖`; descoberta só nos slots do `config.yaml`, sem `sdd/ambiente.md`; starter vira distribuição gerada do open depois da F6; release automática no push de `main`; linters de documento na F4.
- Provided: fonte em `/Users/robertoduarte/rdd-public/sdd-starter` (main `17c69c4`): `sdd-checar-ambiente` 1.2.0 (`checar.sh` 446 linhas, `test_checar.py` 694 linhas/53 testes), `sdd-higiene-dado` 1.1.0 (`alarme.sh` 79, `pre-commit.sh` 120, `test_alarme.py` 318/28, `evals/cases.json`, `manifest.json`, `CHANGELOG.md`, 3 `references/`), `sdd-iniciar-repo` 1.1.0 (`inventario.sh` 191, `test_inventario.py` 310/24), `sdd-new-session` 1.3.0 (387 linhas, matriz de tradução).
- Observed: `init` copia a pasta inteira de cada skill do pacote para `.agents/skills/` do projeto do usuário (`aplicar()`, `cp -R`); `sync` replica **cada arquivo** de `.agents/skills/<skill>/` em `.claude/skills/` e `.cursor/skills/` com 2 linhas `sdd-open:generated` (depois do shebang, quando há). O CI roda só `python3 -B -m unittest discover -s tests -p 'test_*.py'`.
- Observed: o `doctor` roda no fim de todo `init` (inclusive no `init` sem mudança) e sai sempre 0; os 12 testes de `tests/test_sdd_open.py` fazem `init`; só `test_doctor_termina_em_resultado` toca o `doctor`, conferindo a linha `RESULTADO`.
- Observed: o `doctor` atual avisa "skills do sdd-starter detectadas no mesmo projeto" quando existe `.agents/skills/sdd-*/agents/openai.yaml` ou `.claude/skills/sdd-*/agents/openai.yaml` — portar o `agents/openai.yaml` das 3 skills dispararia esse aviso em todo projeto.
- Observed: o `checar.sh` completo faz 2 saídas de rede (consulta anônima ao GitHub, teto 3 s; `git ls-remote`, teto 10 s); a parte de dado exposto é local (`git ls-files` para `.env`, `.pfx`, `.p12`; `git grep --cached -l -I -e "PRIVATE KEY"` em `*.pem`). `--frente` sai 1 quando bloqueia; o modo normal sai sempre 0.
- Observed: o `alarme.sh instalar` grava `.git/hooks/pre-commit` com `sed -n '1,2p'` + `# versão:` + `sed '1,2d'` do `pre-commit.sh` ao lado, e reconhece o alarme próprio por `grep -F` da marca `# sdd-higiene-dado: alarme de commit (pre-commit)`. Na cópia de `.claude/skills/`, as linhas 2–3 são o cabeçalho `sdd-open:generated`, que iria para dentro do hook ("sync reescreve este arquivo"); a marca continua presente, então o reconhecimento não quebra.
- Observed: literais nas pastas-fonte que o G2 do publish-gate reprova — 20 linhas de e-mail fora de `example.com/.org/.net` (inclusive `checar.sh:175`, `voce@exemplo.com` na sugestão de `git config`, e as SKILL.md de checar-ambiente, iniciar-repo e new-session) e o CPF `000.000.000-00` em `test_alarme.py:164`. Nos testes, `git@exemplo.invalid` é host que **não resolve** de propósito (teste sem rede); trocar por `example.com` faria o ssh tentar a rede.
- Observed: as 3 skills-fonte citam o starter — linha de identificação e `IDENT` do `checar.sh` com `sdd-starter/releases/latest`, `npx skills add robertodiasduarte/sdd-starter` (`checar.sh:145`, `sdd-iniciar-repo/SKILL.md:218`), `sdd/ambiente.md` (`sdd-checar-ambiente/SKILL.md:124`), rodapé "Parte do SDD Starter by RDD". As 3 têm `metadata.version` e `metadata.updated`.
- Observed: a `sdd-new-session` 1.0.0 do open já tem um Passo 0 escrito à mão (só remoto: sem `origin`, askpass/janela do editor, login, host SSH, rede, remoto vazio), com variantes PowerShell; slots `project.default_branch`, `editor`, `worktree_base`, "slot vazio = descobrir e declarar". `config.example.yaml` traz `default_branch: main` preenchido, `test_cmd`/`lint_cmd`/`editor`/`worktree_base` vazios.
- Observed: os slots `project.*`, `editor` e `worktree_base` são lidos pelos agentes (skills), não por script; o único slot lido por script é `vendors:` (`sed` em `config_vendors()`).
- Observed: README e `AGENTS.md.tmpl` não contam skills nem citam as 3 novas; `README.md` tem a tabela de recursos e `AGENTS.md.tmpl` lista as fases.
- Inference: a `sdd-iniciar-repo` no open só chega a um projeto que já tem `git init` (o `init` exige repositório); ela retoma do estado "git sem commit", que é o caso coberto.

**Technical Context Observed (for Define):**

| Aspect | Observation | Implication |
|---|---|---|
| Likely Location | `.agents/skills/sdd-checar-ambiente/`, `sdd-higiene-dado/`, `sdd-iniciar-repo/` (novos); `.agents/skills/sdd-new-session/SKILL.md`; `bin/sdd-open.sh` (`doctor`); `tests/test_checar.py`, `test_alarme.py`, `test_inventario.py`, `test_matriz_new_session.py` (novos); `tests/test_sdd_open.py`; `MANIFEST.txt` | Todo arquivo novo no `MANIFEST.txt` em ordem `LC_ALL=C`; skill nova/alterada com `metadata.version` X.Y.Z e bump contra `v2.2.1` |
| Relevant KB Domains | N/A — sem KB no projeto | Contrato vem dos scripts e dos 105 testes do starter |
| IaC Patterns | `.github/workflows/publish-gate.yml` e `release.yml` (F1) sem mudança; push em `main` que toca `.agents/skills/**` ou `bin/**` publica Release | A F2 sai como Release automática `v2.2.2` (ou tag manual `v2.3.0` depois da run de `main`) |

## Discovery Questions & Answers

| # | Question | Answer | Impact |
|---|---|---|---|
| 1 | Onde moram os 3 testes portados: `tests/` na raiz ou `.agents/skills/<skill>/tests/`? | `tests/` na raiz. | Nada de teste vai para o projeto do usuário; CI e Verify Gate sem mudança; muda só o caminho do script em cada teste. |
| 2 | Como o `doctor` confere segredo já salvo no git usando o `checar.sh`? | Modo novo `checar.sh --segredo`, sempre, sem rede. | `init` continua rápido e offline; `doctor` sempre mostra o achado; nada de `doctor --repo`. |
| 3 | O que da matriz de 12 achados entra na `sdd-new-session`? | Script + tabela + caminho à mão: `checar.sh --frente` como principal, tabela de tradução adaptada ao open, Passo 0 à mão como fallback sem bash; sai a linha "git sem nome/e-mail". | `new-session` 1.0.0 → 1.1.0; PowerShell continua coberto; teste amarra script e tabela. |
| 4 | Em qual `sdd/config.yaml` a descoberta grava? | No da frente nova, só slot vazio, só com evidência, sem commitar. | Checkout principal intacto (sem `git pull` abortado depois do merge); as skills da frente leem o valor; o valor chega à branch padrão com a feature. |

## Sample Data Inventory

| Type | Location | Count | Notes |
|---|---|---:|---|
| Input files | N/A | 0 | Usuário não forneceu repositório-cenário |
| Output examples | `skills/sdd-new-session/SKILL.md` do starter (tabela "Como traduzir cada achado"); exemplos em `skills/sdd-checar-ambiente/SKILL.md` | 2 | Formato da tradução e do relatório |
| Ground truth | `tests/test_checar.py` (53), `test_alarme.py` (28), `test_inventario.py` (24) do starter | 105 | Comportamento já afinado; portados como contrato |
| Related code | `tests/apoio.py` e as 9 suítes da F1; `tests/test_publish_gate_patterns.py` (amostra por concatenação) | 10 | Estilo de sandbox (git isolado, HOME falso, `PYTHON = sys.executable`) e de literal montado em tempo de execução |

**How samples will be used:**
- Os 105 testes do starter viram `tests/` do open com 2 ajustes: caminho do script (`.agents/skills/<skill>/scripts/…` a partir da raiz) e literais montados por concatenação (e-mails em `example.com`; host `.invalid` preservado; CPF de amostra).
- A tabela do starter é a base da tabela da `sdd-new-session` 1.1.0, com as linhas de instalação do starter trocadas pela `sdd-iniciar-repo`, que já vem junto no open.
- Os testes novos (`--segredo`, `doctor`, alarme sem cabeçalho, matriz) seguem o padrão de `tests/apoio.py`.

## Approaches Explored

### Approach A: Transplante com adaptação mínima — Recommended

**Description:** As 3 skills entram em `.agents/skills/` quase literais; muda só o que o open exige: literais do G2, links e rodapé `sdd-starter` → `sdd-open`, instruções `npx … sdd-starter`, `sdd/ambiente.md` → slots do `config.yaml`, sem `agents/openai.yaml`; `checar.sh` ganha `--segredo`; `alarme.sh` tira o cabeçalho `sdd-open:generated` ao instalar. Testes em `tests/`. `new-session` ganha pré-voo por script, tabela e descoberta; `doctor` chama o `--segredo`.

**Pros:**
- Os 105 testes continuam provando o comportamento afinado no starter.
- Diff contra o starter pequeno e auditável no BUILD_REPORT.
- A conversa das skills já chega nos símbolos decididos (`✅ ▶️ ⬜ ⏸️ ➖`).

**Cons:**
- Skills portadas longas (217–376 linhas) perto das do open (~160).
- O Passo 0 à mão e o `checar.sh --frente` coexistem na `new-session` (mitigado pelo teste da matriz).

**Why Recommended:** única opção que mantém a prova dos 105 testes e não antecipa a F4.

### Approach B: Reescrita no estilo do open

**Description:** Skills curtas com a conversa em `references/`, scripts reorganizados, testes reescritos.

**Pros:**
- Homogêneo com as 13 skills do open.

**Cons:**
- Os 105 testes deixam de ser prova (viram outros testes).
- Antecipa o trabalho da F4; maior risco de regressão em comportamento afinado.

### Approach C: `checar.sh` como ferramenta do framework (`sdd/bin/`)

**Description:** Script em `sdd/bin/`, copiado pelo `init`; `doctor` e `new-session` o acham num caminho fixo; a skill vira invólucro.

**Pros:**
- Um caminho só para quem chama.

**Cons:**
- `sdd/` é território do usuário e o `init` nunca sobrescreve o que existe: correção no `checar.sh` nunca chega a quem já instalou.

## Selected Approach

| Attribute | Value |
|---|---|
| Chosen | Approach A |
| User Confirmation | 2026-10-29, escolha explícita "A — Transplante" |
| Reasoning | Mantém os 105 testes como prova, diff auditável, não antecipa a F4 nem cria cópia que envelhece em `sdd/` |

## Key Decisions Made

| # | Decision | Rationale | Alternative Rejected |
|---|---|---|---|
| 1 | Testes portados em `tests/` na raiz (`test_checar.py`, `test_alarme.py`, `test_inventario.py`) | `init`/`sync` copiam a pasta inteira da skill; teste dentro dela iria 2–3× para cada projeto do usuário e exigiria mudar CI e gate | `.agents/skills/<skill>/tests/`; sync pulando `tests/` (muda o gerador) |
| 2 | `checar.sh --segredo`: só dado exposto, sem rede, sem agentes; sai 0 sem achado e 1 com achado | `doctor` roda em todo `init`; o completo faz 13 s de rede no pior caso | `doctor --repo` opt-in; os dois |
| 3 | `doctor` chama o `checar.sh` do **pacote** (`${PKG}/.agents/skills/sdd-checar-ambiente/scripts/checar.sh`), mostra cada achado como ⚠️ com o comando que resolve, `✅` sem achado, ⚠️ "pacote incompleto" sem o script; sai sempre 0 | Versão do script casa com a da CLI; contrato atual do `doctor` (exit 0, linha `RESULTADO`) fica igual | Cópia do projeto (`${ROOT}/.agents/skills/…`), que o usuário pode ter editado |
| 4 | O texto do achado diz que confere o que está salvo no git **agora** e que `git rm --cached` não limpa o histórico (trocar a senha) | `ls-files`/`grep --cached` não veem commit antigo de onde o arquivo foi removido; prometer mais seria mentir | Chamar de "segredo no histórico" sem ressalva |
| 5 | `new-session`: `checar.sh --frente` (pasta de skills vizinha) como caminho principal; exit 1 ⇒ para e traduz pela tabela; exit 0 com `✅ Pronto para abrir a frente` ⇒ segue; qualquer outra coisa ⇒ Passo 0 à mão de hoje | PowerShell puro continua coberto; script ausente ou antigo não vira falso "liberado" | Remover o Passo 0 à mão; só a tabela sem script |
| 6 | Tabela de tradução adaptada: linhas `npx … sdd-starter` → `sdd-iniciar-repo`; sai "git sem nome/e-mail" (o `--frente` não produz) | No open a `sdd-iniciar-repo` sempre vem junto | Copiar a tabela literal |
| 7 | `tests/test_matriz_new_session.py`: cada mensagem de bloqueio que o `checar.sh --frente` emite tem linha na tabela da `new-session` | Script e tabela vivem em arquivos diferentes; sem teste divergem calados | Conferir à mão |
| 8 | Descoberta grava no `sdd/config.yaml` **da frente**, só slot vazio, com `# descoberto por sdd-new-session (AAAA-MM-DD): <evidência>` na linha de cima, sem commitar; frente sem `sdd/config.yaml` ⇒ não grava e diz como resolver | Checkout principal sujo faz o `git pull` abortar depois do merge; as skills da frente leem o config da frente; comentário na mesma linha arrisca leitura ingênua | Checkout principal; propor e gravar com OK |
| 9 | `default_branch` cheio que diverge da HEAD do remoto ⇒ para e pergunta; nunca sobrescreve slot cheio | O exemplo já vem com `main`; um `master` no remoto faria o `fetch` falhar no meio | Confiar no config; sobrescrever |
| 10 | `test_cmd`/`lint_cmd` só com evidência literal (o comando que o CI roda > `scripts.test` do `package.json` sem o placeholder do npm > alvo `test:` do `Makefile`); sem evidência ou ambíguo ⇒ vazio, declarado | `test_cmd` alimenta gates `kind: test`; um chute roda a coisa errada | Inferir pelo tipo de projeto |
| 11 | Sem `agents/openai.yaml` nas skills portadas | O `doctor` usa esse arquivo para detectar o starter no mesmo projeto | Portar e mudar a detecção do `doctor` |
| 12 | `alarme.sh instalar` remove as linhas `sdd-open:generated` ao gravar o hook | A cópia de `.claude/skills/` levaria "sync reescreve este arquivo" para dentro de `.git/hooks/pre-commit` | Aceitar o cabeçalho no hook |
| 13 | Versões: `sdd-checar-ambiente` 1.3.0 (modo novo), `sdd-higiene-dado` 1.1.1, `sdd-iniciar-repo` 1.1.1 (adaptação), `sdd-new-session` 1.1.0; mantêm `metadata.updated` e a linha de identificação, apontando para `sdd-open/releases/latest` | O open passa a ser a fonte canônica e continua a linha de versão do starter | Recomeçar em 1.0.0; tirar a linha de identificação |
| 14 | Literais: e-mails → `example.com`; host `.invalid` dos testes preservado e montado por concatenação (`"git" + "@" + …`); CPF de amostra montado em tempo de execução | G2 reprova; trocar o host por `example.com` faria o teste tentar rede | Trocar tudo por `example.com` |
| 15 | Sabotagem: uma por script portado (`checar.sh`, `alarme.sh`, `pre-commit.sh`, `inventario.sh`) e uma no `doctor`; Build commita antes do gate | Teste que nunca fica vermelho não prova nada; o gate lê `git archive HEAD` | Só contrato |

## Features Removed (YAGNI)

| Feature Suggested | Reason Removed/Deferred | Can Add Later? |
|---|---|---|
| Ligar o `pre-commit.sh`/`--segredo` ao `release.landmines_cmd` | Mexe no `config.yaml` (fora de escopo); o `--segredo` já sai 1 com achado para servir depois | Yes |
| `init` sem git oferecer a `sdd-iniciar-repo` | Muda a CLI; a skill cobre o projeto depois de `git init` + `init` | Yes |
| `doctor --repo` com o diagnóstico completo | A skill `sdd-checar-ambiente` já faz; mais superfície de CLI | Yes |
| README e `AGENTS.md.tmpl` citando as 3 skills | Nenhum dos dois conta skills; é trabalho de docs | Yes — F6 |
| Port do `checar.sh` para PowerShell | O Passo 0 à mão cobre PowerShell; teste no Windows fora de escopo | Yes |
| Descobrir `typecheck_cmd`, `layers`, `deploy` | Fora dos 5 slots decididos | Yes |
| `sdd/ambiente.md` e cenário de branching A/B/C | Decisão 4: só slots do `config.yaml`; cenário não tem slot | N/A |
| `agents/openai.yaml` | Dispara o aviso "skills do starter" no `doctor` | N/A |
| Seção "Como falar com o aluno" na `new-session` do open | Skill nativa: F4 | Yes — F4 |

## Incremental Validations

| Section | Presented | User Feedback | Adjusted? |
|---|---|---|---|
| Checkpoint 1 — conceito, componentes (3 skills, 4 arquivos de teste, `new-session` 1.1.0, `doctor` com `--segredo` do pacote, versões 1.3.0/1.1.1/1.1.1) e 6 cortes YAGNI | Yes | "Certo, seguir" | No |
| Checkpoint 2 — fluxo do `doctor` (sem rede, ⚠️, exit 0, ressalva do histórico), da `new-session` (script → tabela → mão; `default_branch` divergente para; evidência literal; grava na frente), alarme sem cabeçalho, 5 sabotagens | Yes | "Certo, gerar o brainstorm" | No |

## Suggested Requirements for /define

### Problem Statement (Draft)

O sdd-open não confere o terreno antes da spec — pasta na nuvem, projeto sem git, remoto inacessível, senha ou certificado já salvos no git, dado de cliente indo para o commit — e a `sdd-new-session` cobre só o remoto e deixa os slots vazios para o usuário; o sdd-starter já resolve isso com 3 skills e 105 testes que precisam entrar no open sem perder a prova nem violar o publish-gate.

### Target Users (Draft)

| User | Pain Point |
|---|---|
| Aluno/usuário do sdd-open que abre frente ou instala o framework | Descobre tarde, no meio do trabalho, que a pasta está na nuvem, que o remoto não responde ou que um `.env` já foi para o git |
| Mantenedor do sdd-open (Roberto e agentes de F3–F6) | Precisa que o comportamento portado continue provado por teste e que script e tabela de tradução não divirjam |

### Success Criteria (Draft)

- [ ] Existem `.agents/skills/sdd-checar-ambiente`, `sdd-higiene-dado` e `sdd-iniciar-repo`; `python3 sdd/bin/skill-lint.py .agents/skills/sdd-*/SKILL.md` sai 0; nenhuma tem `agents/openai.yaml`.
- [ ] Os 105 testes do starter rodam em `tests/` (`test_checar.py`, `test_alarme.py`, `test_inventario.py`) e passam, junto com os 115 da F1, em `python3 -B -m unittest discover -s tests -p 'test_*.py'`, sem rede.
- [ ] `checar.sh --segredo` sai 1 e nomeia o arquivo com `.env`, `.pfx`, `.p12` ou `.pem` com `PRIVATE KEY` rastreado; sai 0 sem achado; não chama rede.
- [ ] `sdd-open.sh doctor` num projeto com `.env` commitado mostra ⚠️ com o arquivo e o comando, e sai 0; sem achado, mostra a linha ✅.
- [ ] `alarme.sh instalar` a partir de uma cópia com cabeçalho `sdd-open:generated` grava um hook sem a marca, reconhecido depois como alarme próprio.
- [ ] Toda mensagem de bloqueio do `checar.sh --frente` tem linha na tabela da `sdd-new-session` (teste).
- [ ] A `sdd-new-session` 1.1.0 descreve: pré-voo por script com fallback à mão; parada em `default_branch` divergente; gravação só em slot vazio do config da frente com evidência.
- [ ] `PUBLISH_GATE_MODE=ci bash scripts/publish-gate.sh` sai 0 na cópia de `git archive HEAD`; `python3 scripts/check-versions.py --base v2.2.1 --base-obrigatoria` sai 0.
- [ ] O BUILD_REPORT registra 5 sabotagens (4 scripts portados + `doctor`) com teste nomeado vermelho e reversão.
- [ ] Número de testes novos além dos 105: TBD — o critério é cobertura de contrato.

### Constraints Identified

- bash 3.2, sem `grep -P`, `readlink -f`, `declare -A`, `mapfile`, zsh ou symlink; Python ≥ 3.9 só com stdlib; `python3 -B` sempre.
- Testes sem rede e sem ler o `~/.gitconfig` de quem roda.
- Nenhum literal que case com `scripts/publish-gate-patterns.txt` (só `example.com/.org/.net` isentos, e só em padrão de e-mail).
- Todo arquivo novo no `MANIFEST.txt` em ordem `LC_ALL=C`; `git add` por nome; `sdd/features/`, `sdd/handoffs/`, `sdd/reports/` fora do commit.
- `sync` idempotente; os seis exits do `verify-gate.sh` e as fixtures de `sdd/fixtures/` idênticos; os 115 testes da F1 verdes; `doctor` continua saindo 0 com a mesma linha `RESULTADO`.
- Skill nova/alterada com `metadata.version` X.Y.Z e bump contra `v2.2.1`.
- Comando que fala com o remoto com `GIT_TERMINAL_PROMPT=0`; push em `main` só com OK explícito citando "sdd-open", depois de PR com CI verde.
- Verify Gate roda o publish-gate em `PUBLISH_GATE_MODE=ci` sobre `git archive HEAD`; o Build commita antes.

### Out of Scope (Confirmed)

- Redesenhar a CLI ou o `config.yaml`; `doctor --repo`; `init` oferecendo a `sdd-iniciar-repo`.
- Ligação com `release.landmines_cmd`.
- Camada de conversa nas skills nativas, inclusive na `new-session` (F4); `design-lint`/`handoff-lint` (F4).
- Migration e bloco do "go" (F3).
- README, `AGENTS.md.tmpl` e docs (F6).
- `sdd/ambiente.md`, cenário de branching, `agents/openai.yaml`.
- Alterar o sdd-starter; modo `briefs`; PowerShell do `checar.sh`; teste no Windows.

## Session Summary

| Metric | Value |
|---|---:|
| Questions Asked | 5 |
| Approaches Explored | 3 |
| Features Removed (YAGNI) | 9 |
| Validations Completed | 2 |

## Next Step

Execute o **SDD Define by RDD**.
