# BRAINSTORM: F8 Hooks de git

> Exploratory session to clarify intent and approach before requirements capture

## Metadata

| Attribute | Value |
|---|---|
| Feature | F8_HOOKS |
| Date | 2026-10-30 |
| Author | brainstorm-agent |
| Status | Handoff Ready |

## Initial Idea

**Raw Input:** "Brainstorm da F8 com a `sdd-brainstorm`, gravando `sdd/features/BRAINSTORM_F8_HOOKS.md` a partir do quadro F8 e do 8.1 do plano. Pronto quando: D3, D10, D11, o formato da E6 e a versão foram respondidas pelo Roberto, a abordagem foi confirmada e os cortes YAGNI e os 2 checkpoints estão registrados." Escopo do prompt da sessão 6: itens H1–H6 do PORTE §5.2 mais o adaptador da E6 — `sdd/hooks/pre-commit` (teto do arquivo de contexto por vendor, credencial em config, anti-collapse do playbook, byte NUL, commit na branch padrão, `report-lint` do `BUILD_REPORT` staged), `sdd/hooks/pre-push` (base velha), `sdd-open.sh init` instalando com confirmação e `doctor` conferindo, e o `init --vendors claude` gerando o adaptador do Claude Code (PreToolUse em Write/Edit chamando `report-lint.py --stdin`; guard do despacho do avaliador chamando `avaliador-guard.sh`).

**Context Gathered:**
- Fato (conferido): worktree `feat/f8-hooks` em `1d225e5` = `origin/main` = tag `v2.2.8`; 17 skills; 630 testes no piso; a cópia do handoff bate com a branch `docs/incorporar-starter`; nenhum rebase necessário.
- Fato (conferido): as fontes do privado foram lidas do `origin/main` dele (`abd322b4e`), sem alterar nada: `.githooks/pre-commit` (154 linhas, 6 guardas; o ① bloqueia o checkout primário por `git-dir == git-common-dir`, o ⑥ é PHP), `.githooks/pre-push` (31 linhas, só aviso), `.githooks/claude-avaliador-guard.py` (88 linhas, reconhece o avaliador por `subagent_type == "avaliador-fresco"`), `resulting_content()` do `.githooks/claude-build-report-guard.py` (simula Write/Edit/MultiEdit; `old_string` ausente ⇒ não nega), o bloco `hooks.PreToolUse` do `.claude/settings.json` (matchers `Write|Edit|MultiEdit` com `timeout: 10` e `Agent|Task`) e `scripts/gates/gate-nul-no-fonte.sh` (82 linhas).
- Fato (conferido): `core.hooksPath` faz o git ignorar `.git/hooks/`; o `alarme.sh` da `sdd-higiene-dado` 1.1.1 grava o alarme em `.git/hooks/pre-commit` e **recusa** agir com qualquer `core.hooksPath` (`test_core_hooks_path_recusa` usa `.husky/_`). Ligar `sdd/hooks` sem tratar isso desligaria a proteção de CPF/CNPJ em silêncio.
- Fato (conferido): o `init` já mostra um plano por alvo (`+`/`~`/`=`) e pede uma confirmação única (`[y/N]`, `--yes`; fora de terminal sem `--yes` = cancelado); copia de `sdd/` só `templates`, `bin` e `playbook.md`, completando o que falta sem sobrescrever; `sync` nunca escreve em `sdd/`; o merge do `.gemini/settings.json` (`merge_gemini_settings`) é o molde de edição de JSON do usuário (JSON inválido = exit 66 sem alterar; chave alheia nunca some).
- Fato (conferido): `bin/lib/vendors.sh` tem a tabela de vendors como `case` (bash 3.2); não há lista de arquivo de contexto por vendor. `sdd/config.example.yaml` tem `project.default_branch: main` e nenhum slot de teto.
- Fato (conferido): `report-lint.py --stdin <caminho>` (F7) lê o conteúdo do stdin e confere como se fosse o arquivo; `avaliador-guard.sh` sai 0/1/2/64; `playbook-lint.sh --anti-collapse <head> <staged>` sai 0/1/64; fixtures `sdd/fixtures/playbook/playbook-colapso.md`, `playbook-delta-ok.md`, `sdd/fixtures/evidencia/BUILD_REPORT_sem_avaliacao.md` e `BUILD_REPORT_controle.md` existem.
- Fato (conferido): `tests/test_agnostico.py` reprova `PreToolUse`, `subagent_type`, `Agent tool`… em `.agents/skills/**`, `sdd/templates/**`, `AGENTS.md.tmpl` e `sdd/playbook.md`; `ADAPTADORES = ()` com o comentário "quem acrescentar um template por vendor declara o prefixo aqui". `bin/` está fora do escopo.
- Fato (conferido): a `sdd-build` 2.3.0 (5d) manda o brief do avaliador com "modo `veredito`" e chama `avaliador-guard.sh` antes de despachar; o open não tem nome fixo de subagente para o avaliador.
- Fato (conferido): `docs/roadmap.md` e PT têm a linha "Hooks" (*planned*) entre 7 linhas; `tests/test_docs.py` conta as linhas.
- Fato (medido): `AGENTS.md.tmpl` tem 3 KB; nenhum `.json`/`.yml` do repositório casa com regex de credencial.
- Inferência: o `init` do open é rodado por quem acabou de criar o repositório (`sdd-iniciar-repo`) ou por quem está na branch padrão; uma H6 que recusa todo commit na branch padrão bloquearia o commit do próprio `init`.

**Technical Context Observed (for Define):**

| Aspect | Observation | Implication |
|---|---|---|
| Likely Location | `sdd/hooks/{pre-commit,pre-push}` (novos), `bin/sdd-open.sh`, `bin/lib/{vendors,merge}.sh`, `bin/adapters/claude/` (novo), `.agents/skills/sdd-higiene-dado/{SKILL.md,scripts/alarme.sh}`, `sdd/config.example.yaml`, `sdd/fixtures/hooks/` (novo), `docs/hooks.md` + PT (novos), `docs/roadmap.md` + PT, `tests/`, `MANIFEST.txt` | `bin/**`, `sdd/**` (fora de features/reports) e `.agents/skills/**` disparam a Release |
| Relevant KB Domains | N/A (o open não tem `sdd/kb/` próprio) | `KB Domains = nenhum` no DEFINE |
| IaC Patterns | N/A | CI existente (`publish-gate.yml` + `testes-macos`) sem mudança |

## Discovery Questions & Answers

| # | Question | Answer | Impact |
|---|---|---|---|
| 1 | O open distribui hooks e os liga no projeto do usuário (D3)? | **Sim, pelo `init`, dentro do plano** (recomendada), contra "pergunta separada" e "só distribuir, sem ligar" | O `init` copia `sdd/hooks/` e mostra `+ core.hooksPath = sdd/hooks` no plano; a confirmação única cobre; `doctor` confere `hooksPath` e bit `-x`; `sync` não toca em `sdd/hooks/` |
| 2 | Como o hook convive com o alarme da `sdd-higiene-dado` (D10)? | **Dispatcher que chama a higiene-dado quando ela está ligada** (recomendada), contra "encadear qualquer `.git/hooks/pre-commit`" e "não mexer na higiene; `init` recusa ligar se houver alarme local" | `sdd/hooks/pre-commit` chama `.agents/skills/sdd-higiene-dado/scripts/pre-commit.sh` se `git config sdd.higieneDado` = `on`; `alarme.sh` reconhece `core.hooksPath = sdd/hooks` (com a marca do dispatcher) como seu — `instalar` liga a config, `desinstalar` desliga, outro `hooksPath` segue recusado; `init` migra o alarme já instalado em `.git/hooks/pre-commit` ligando a config e avisando; `sdd-higiene-dado` 1.1.1 → 1.2.0; os 29 testes ficam, entram casos novos |
| 3 | O teto do arquivo de contexto vira slot (D11)? | **Sim, `project.context_file_max_kb` com default 100** (recomendada), contra "constante no hook" e "slot sem default (vazio = pula)" | Hook lê o slot por `sed`; vazio ou ausente = 100 KB; lista de nomes por vendor em `vendors.sh` |
| 4 | Como o `init --vendors claude` entrega o adaptador da E6? | **Merge em `.claude/settings.json` + 2 scripts gerados em `.claude/hooks/`** (recomendada), contra "só `settings.json` com comando em linha" e "scripts genéricos em `sdd/bin/`" | Fonte em `bin/adapters/claude/`; cópias com cabeçalho `sdd-open:generated`; 2 entradas de hook acrescentadas ao JSON sem apagar nada alheio; `sync` regenera, `--check` acusa; falha aberta com aviso; entra neste ciclo. Ajuste do checkpoint 2: os 2 guards são Python (precisam ler o JSON do hook) |
| 5 | Qual versão a F8 publica? | **`v2.2.9` automática** (recomendação revista pelo público: alunos do Bravo, contadores), contra "`v2.3.0` por tag à mão" e "decidir no bloco do OK" | Push de `main` e nada mais; o aviso da mudança de comportamento vai para o produto: a linha do plano do `init`, a mensagem de recusa do hook e a linha do `doctor` (requisitos do DEFINE) |

## Sample Data Inventory

| Type | Location | Count | Notes |
|---|---|---:|---|
| Input files | `.githooks/pre-commit`, `pre-push`, `claude-avaliador-guard.py`, `claude-build-report-guard.py`, `scripts/gates/gate-nul-no-fonte.sh`, `.claude/settings.json` do privado (`origin/main` `abd322b4e`) | 6 | Só leitura; dizem o que cada regra pega e o que deixa passar (placeholder `${VAR}`, `CHANGEME`, `example`, `<…>`, `***`) |
| Output examples | `sdd/fixtures/playbook/playbook-{colapso,delta-ok}.md`, `sdd/fixtures/evidencia/BUILD_REPORT_{sem_avaliacao,controle}.md` | 4 | Reusados pela H4 e pelo guard da E6 |
| Ground truth | `tests/test_alarme.py` (29 testes; CPF/CNPJ montados em execução) | 1 | Molde das fixtures de hook: literal de CPF/CNPJ não entra em arquivo rastreado (publish-gate) |
| Related code | `bin/sdd-open.sh`, `bin/lib/*.sh`, `alarme.sh`, `pre-commit.sh` da higiene, `report-lint.py --stdin`, `avaliador-guard.sh`, `playbook-lint.sh --anti-collapse` | 9 | Pontos de ligação |

**How samples will be used:**
- Fixtures H2–H6 + controle escritas do zero em `sdd/fixtures/hooks/` com os casos do privado; as que levam CPF/CNPJ ou credencial são montadas em execução pelo teste.
- A migração da D10 (alarme em `.git/hooks` → `sdd.higieneDado=on`) e a recusa com husky são provadas em repositório temporário nos testes.
- Não há projeto real de aluno com hooks de outra ferramenta nem `AGENTS.md` perto do teto (opções recusadas); registrado como limitação.

## Approaches Explored

### Approach A: Um dispatcher em bash, regras como funções, um ciclo — Recommended

**Description:** `sdd/hooks/pre-commit` é um script bash 3.2 com as regras em funções, na ordem da mais barata à mais cara, rodando **todas** e juntando os achados numa só recusa. Delega ao que já existe (`playbook-lint.sh --anti-collapse`, `report-lint.py --stdin`, `pre-commit.sh` da higiene); H2, H3, H5 e H6 ficam no próprio hook, com fixture e teste. `pre-push` é um script curto de aviso. O `init` copia `sdd/hooks/` como copia `sdd/bin/` e acrescenta a linha do `hooksPath` ao plano.

**Pros:**
- Espelha a fonte do privado (154 linhas, provadas em uso).
- 2 arquivos novos em `sdd/hooks/`; só bash e git para commitar (`python3` só quando há `BUILD_REPORT` staged, com aviso se faltar).
- Uma Release.

**Cons:**
- Um arquivo de ~180 linhas.
- Desligar uma regra é editar o hook (território do usuário; `sync` não mexe).

**Why Recommended:** menor número de arquivos e dependências, fidelidade à fonte, e o `doctor` continua sabendo o que é "instalação incompleta".

### Approach B: Um arquivo por regra em `sdd/hooks/pre-commit.d/`

**Description:** o dispatcher percorre `pre-commit.d/*.sh` em ordem; cada regra é um script de 20–40 linhas.

**Pros:**
- Desligar uma regra é apagar um arquivo; teste unitário por arquivo.

**Cons:**
- 7 arquivos novos em vez de 2, cada um com cabeçalho, `MANIFEST.txt` e teste de ordem.
- Arquivo apagado de propósito e instalação incompleta ficam indistinguíveis para o `doctor` e para o `init` que completa o que falta.

### Approach C: Hook em Python

**Description:** `sdd/hooks/pre-commit` com 3 linhas chamando `python3 sdd/bin/hooks.py pre-commit`; as regras no estilo do `report-lint.py`.

**Pros:**
- Regex e leitura do YAML mais limpas; um só verificador de sintaxe.

**Cons:**
- Todo commit passa a depender de `python3` no PATH; sem ele o hook tem de falhar aberto e H2–H6 somem em silêncio na máquina sem Python.
- `tests/test_bash32.py` deixa de cobrir o hook.

## Selected Approach

| Attribute | Value |
|---|---|
| Chosen | Approach A |
| User Confirmation | 2026-10-30, "A — um dispatcher em bash, regras como funções, um ciclo (recomendada)" |
| Reasoning | Menos arquivos e dependências, fiel à fonte, mantém a leitura de "incompleto" do `doctor` |

## Key Decisions Made

| # | Decision | Rationale | Alternative Rejected |
|---|---|---|---|
| 1 | D3: o `init` distribui `sdd/hooks/` e liga `core.hooksPath = sdd/hooks` como mais uma linha do plano, sob a confirmação única | Regra 7 do `AGENTS.md.tmpl` ("um OK só"); hooks versionados valem em toda worktree | Segundo `[y/N]` só para hooks; só distribuir sem ligar |
| 2 | O `init` **não** liga os hooks quando já há outro `core.hooksPath` (husky, lefthook) ou um `.git/hooks/pre-commit` que não é da higiene; imprime a linha para acrescentar ao gerenciador existente | Ligar desligaria o alarme alheio em silêncio | Migrar o gerenciador do usuário |
| 3 | D10: dispatcher chama o `pre-commit.sh` da higiene quando `git config sdd.higieneDado` = `on`; `alarme.sh` reconhece `sdd/hooks` (com a marca do dispatcher) como seu; `init` migra o alarme já instalado em `.git/hooks` ligando a config | Usa a cópia versionada da skill (não envelhece como a cópia em `.git/hooks`); a proteção de CPF/CNPJ nunca some | Encadear qualquer `.git/hooks/pre-commit` (código fora do git a cada commit); não mexer na higiene |
| 4 | `sdd-higiene-dado` 1.1.1 → 1.2.0; os 29 testes de `test_alarme.py` ficam como estão, entram casos novos | Mudança de comportamento do `instalar`/`desinstalar` | Patch |
| 5 | D11: slot `project.context_file_max_kb`, default 100 quando vazio ou ausente; lista de arquivos de contexto por vendor em `vendors.sh` (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.cursorrules`) | Regra 2 do PORTE (slots, não constantes); o default protege projeto que instalou antes da F8 | Constante; slot vazio = pula (perderia a proteção em silêncio) |
| 6 | E6: fonte em `bin/adapters/claude/` (`sdd-report-guard.py`, `sdd-avaliador-guard.py`), cópias geradas em `.claude/hooks/` com cabeçalho `sdd-open:generated`, merge de 2 entradas em `.claude/settings.json` nos moldes do Gemini | Nome de ferramenta do vendor só no que o `init` gera (P2); `--check` confere sintaxe; `sync` regenera | Comando em linha no JSON; scripts genéricos em `sdd/bin/` |
| 7 | Guards do Claude Code falham **abertos** com aviso (`systemMessage`); `report-lint` exit 1 nega com o texto do lint | Hook quebrado não pode travar toda escrita (fonte: `claude-build-report-guard.py`) | Falha fechada |
| 8 | O guard do avaliador age quando o prompt do subagente traz o modo `veredito` | O open não tem nome fixo de subagente; o brief da `sdd-build` já leva o modo | Guard em todo despacho (travaria advisor e workers); nome fixo |
| 9 | Versão `v2.2.9` automática; o aviso da mudança vai para a linha do plano, a mensagem de recusa e a linha do `doctor` | Público (contadores) não lê lista de Releases; o número não protege ninguém, a tela protege | `v2.3.0` por tag (recomendada antes da revisão pelo público); decidir no bloco do OK |
| 10 | H6 recusa commit na `project.default_branch` só quando existe `origin/<branch>`; sem remoto passa | Protege o commit do próprio `init` e o primeiro commit da `sdd-iniciar-repo`; sem remoto não há produção a proteger | Recusar sempre (exigiria `--no-verify` na instalação) |
| 11 | O pre-commit roda todas as regras e junta os achados numa só recusa | O aluno vê tudo num commit (padrão do alarme da higiene) | Parar na primeira regra (padrão do privado) |
| 12 | Saída do hook no padrão do pacote: `🛑 [Hn] <arquivo>: <motivo>`, `RESULTADO: COMMIT RECUSADO`, um `→` por classe; sucesso silencioso; sem ANSI | `docs/cli-conventions.md`; cor não aparece no log de evidência | Cores do privado |
| 13 | `python3` ausente: só a regra do `BUILD_REPORT` avisa `⚠️` e segue; `playbook-lint.sh` ausente: idem para a H4 | Commitar não pode depender de Python | Falha fechada |
| 14 | `init` dá `chmod +x` aos hooks e o `doctor` confere `-x` e `hooksPath` | Hook sem bit de execução é ignorado pelo git em silêncio | Confiar no bit da cópia |
| 15 | `sdd/hooks/` é território do usuário: `init` completa o que falta, `sync` não toca | Mesma regra de `sdd/bin/` | `sync` regenerando hooks |
| 16 | Abordagem A | Ver Selected Approach | B (um arquivo por regra); C (Python) |

## Features Removed (YAGNI)

| Feature Suggested | Reason Removed/Deferred | Can Add Later? |
|---|---|---|
| Aviso do `pre-push` para a branch `dev` | Específico da RDD (regra 4 do PORTE) | Yes |
| Item ⑥ do pre-commit privado (require de PHP) | WordPress; não viaja | No |
| Cores ANSI nas mensagens | O pacote fala com `🛑`, `RESULTADO:`, `→` | No |
| Subcomando `sdd-open.sh hooks ligar/desligar` | `init` liga; desligar é `git config --unset core.hooksPath`, em `docs/hooks.md` | Yes |
| `SDD_HOOKS=off` para pular o hook | `git commit --no-verify` já é o limite documentado | Yes |
| Migrar husky/lefthook para `sdd/hooks` | O `init` só imprime a linha para acrescentar; migração é decisão do dono | Yes |
| Outros hooks (`commit-msg`, `post-checkout`) | Nenhum item H1–H6 precisa | Yes |
| `sync` regenerando `sdd/hooks/` | Território do usuário (Decisão 15) | Yes |
| Teto diferente por vendor | Um slot; nomes em `vendors.sh` | Yes |
| Guard do avaliador por nome de subagente | O open não tem nome fixo (Decisão 8) | Yes (F9, se nascer um nome) |
| Data de corte para relatório antigo no guard da E6 | O `report-lint` da F7 já decidiu sem corte | Yes |

Ficam, embora opcionais: `gitleaks protect --staged` quando instalado (H3, testado com binário falso no PATH) e `docs/hooks.md` em EN e PT (padrão dos docs do pacote; público PT).

## Incremental Validations

| Section | Presented | User Feedback | Adjusted? |
|---|---|---|---|
| Checkpoint 1: conceito (2 hooks versionados ligados pelo `init`, 5 classes + `report-lint` + higiene, pre-push só avisa, adaptador do Claude Code), limites (`--no-verify`, outro `hooksPath`, falha aberta dos guards, só bash e git) e componentes (lista de arquivos novos e tocados, testes) | Yes | "sim" | No |
| Checkpoint 2: ordem das regras (H6 → H2 → H5 → H3 → H4 → relatório → higiene), todas rodam e juntam os achados, saída no padrão do pacote, falhas que não travam (`python3`, `playbook-lint`, bit `-x`), guards em Python, dependências (F7, `playbook-lint`, higiene 1.1.1, `merge.sh`), H6 passando sem `origin/<branch>` | Yes | "grave" | Sim: os 2 guards passam de `.sh`/`.py` para Python, registrado na Q4 |

## Suggested Requirements for /define

### Problem Statement (Draft)

O sdd-open não distribui hooks de git: nada impede um commit com `AGENTS.md`/`CLAUDE.md` acima do teto da janela do agente, credencial em texto claro num `.json`/`.yml`, playbook que perde conhecimento, byte NUL em arquivo de texto, commit direto na branch padrão de um projeto com remoto ou `BUILD_REPORT` que o `report-lint` reprova; o único alarme existente (`sdd-higiene-dado`) grava em `.git/hooks` e deixa de funcionar com qualquer `core.hooksPath`; e, no Claude Code, o `BUILD_REPORT` só é conferido depois de gravado, e o avaliador pode ser despachado com a árvore suja.

### Target Users (Draft)

| User | Pain Point |
|---|---|
| Aluno do Bravo (contador) que roda o `init` e commita pelo agente | Commits que estouram a janela, vazam credencial ou apagam conhecimento passam sem aviso; o alarme de CPF/CNPJ some se algo ligar `core.hooksPath` |
| Quem roda a `sdd-build` no Claude Code | O relatório é gravado antes de ser conferido; o avaliador pode destruir trabalho não commitado |
| Mantenedor do open e do privado (Roberto, F15) | Precisa dos hooks do privado no open para substituí-lo (P4) |

### Success Criteria (Draft)

- [ ] Depois do `init` num repositório limpo, `git config core.hooksPath` = `sdd/hooks`, `sdd/hooks/pre-commit` e `pre-push` existem com bit `-x`, e a linha `+ core.hooksPath = sdd/hooks` apareceu no plano antes da confirmação.
- [ ] O pre-commit recusa as 5 fixtures H2–H6 e a de `BUILD_REPORT` sem avaliação, cada uma com `🛑 [Hn]`, `RESULTADO: COMMIT RECUSADO` e `→`, e deixa passar o controle em silêncio; `--no-verify` grava.
- [ ] H6 passa sem `origin/<default_branch>` e recusa com ele; H2 lê o slot e usa 100 KB quando vazio; H3 passa placeholder e nunca imprime o valor; H4 recusa delete/rename e `playbook-colapso.md`, aceita `playbook-delta-ok.md`; H5 recusa NUL em `.md`/`.sh` e ignora `.png`.
- [ ] Com `sdd.higieneDado=on`, o pre-commit continua recusando CPF/CNPJ com DV válido, `.env`, `.pfx/.p12/.pem` e planilha nova; `alarme.sh instalar` com `hooksPath = sdd/hooks` liga a config, `desinstalar` desliga, `.husky/_` segue recusado; o `init` migra um alarme já em `.git/hooks`; os 29 testes de `test_alarme.py` continuam verdes.
- [ ] O `init` não liga os hooks com outro `hooksPath` ou `.git/hooks/pre-commit` alheio e imprime a linha para acrescentar; o `doctor` acusa `hooksPath` ausente e hook sem `-x`.
- [ ] `init --vendors claude` gera `.claude/hooks/sdd-report-guard.py` e `sdd-avaliador-guard.py` com cabeçalho e as 2 entradas em `.claude/settings.json` sem apagar chave alheia; JSON inválido aborta sem escrever; `sync --check` acusa cópia divergente; um Write de `BUILD_REPORT` sem avaliação é negado com o texto do lint; um Edit cujo `old_string` não existe não é negado; erro interno vira aviso, não negação.
- [ ] `pre-push` avisa `⚠️` quando o tip está atrás de `origin/<default_branch>` e sai 0 sempre.
- [ ] Todo script novo passa em `grep -nE 'mapfile|declare -A|\$\{[a-zA-Z_]+\^\^'` sem achado; fixture e teste dos dois lados; 1 sabotagem por script; `test_agnostico` verde (os guards só em `bin/adapters/` e no gerado).
- [ ] `check-versions --base v2.2.8 --base-obrigatoria` verde com `sdd-higiene-dado` 1.2.0; `skill-lint --conversa` 17/17; roadmap EN/PT sem a linha "Hooks" e `test_docs` ajustado; `docs/hooks.md` EN/PT com o limite do `--no-verify`.
- [ ] Verify Gate `--strict` 0; revisão de contexto fresco sem HIGH aberto; Release `v2.2.9` com `SHA256SUMS.txt` conferido por `shasum -a 256 -c`.

### Constraints Identified

- `init` nunca sobrescreve skill instalada nem `sdd/bin/*`/`sdd/hooks/*`; `sync` nunca escreve em `sdd/`; merge do `.gemini/settings.json` intacto; testes de `test_sdd_open.py` ficam.
- Só bash 3.2 e git para commitar; `python3` opcional com aviso; nada de `mapfile`, `declare -A`, `${x^^}`; `rm -rf` só com `"${X:?}"`.
- P2: `PreToolUse`, `subagent_type`, `tool_input` etc. só em `bin/adapters/claude/` e no que o `init` gera; nunca em `.agents/skills/`, `sdd/templates/`, `sdd/bin/`, `AGENTS.md.tmpl` ou playbook.
- `report-lint.py` (32 contratos + F7), `verify-gate.sh` (6 exits, fixtures), `playbook-lint.sh --self-test` e a camada de conversa intactos; o bloco do OK da `sdd-release` não muda.
- Publish-gate: fixtures sem e-mail fora de `example.*`, CPF, CNPJ, telefone, 11+ dígitos seguidos ou `/Users/<nome>/`; credencial de fixture montada em execução ou com valor obviamente falso que o H3 **deve** pegar sem casar com os padrões do publish-gate.
- Todo arquivo novo no `MANIFEST.txt` (`LC_ALL=C`); `git add` por nome; `sdd/features|handoffs|reports|reviews|traces/` fora dos commits da branch de trabalho.
- `sdd/traces/` segue permitido pelo `avaliador-guard.sh`; a regra do relatório no pre-commit usa o conteúdo **staged** (`git show :<f>`), não o do disco.

### Out of Scope (Confirmed)

- Os itens da tabela YAGNI acima.
- Encadeamento entre fases, `exit 40 AGUARDANDO_HUMANO`, classes D1–D5 (F9); revisão adversarial e registry (F10/F11); `RESUMO_ETAPA.md` com `/adversarial-review` (F10).
- Regenerar o sdd-starter; alterar o sdd-starter ou o repositório privado.
- Projeto real de aluno como amostra (opção recusada; limitação registrada).

## Session Summary

| Metric | Value |
|---|---:|
| Questions Asked | 5 |
| Approaches Explored | 3 |
| Features Removed (YAGNI) | 11 |
| Validations Completed | 2 |

## Next Step

Execute o **SDD Define by RDD**.
