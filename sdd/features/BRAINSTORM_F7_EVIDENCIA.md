# BRAINSTORM: F7 Evidência que não mente

> Exploratory session to clarify intent and approach before requirements capture

## Metadata

| Attribute | Value |
|---|---|
| Feature | F7_EVIDENCIA |
| Date | 2026-10-30 |
| Author | brainstorm-agent |
| Status | Handoff Ready |

## Initial Idea

**Raw Input:** "Brainstorm da F7 com a `sdd-brainstorm`, gravando `sdd/features/BRAINSTORM_F7_EVIDENCIA.md` a partir do quadro F7 e do 8.1 do plano. Pronto quando: D4, D11, a E6 e a versão foram respondidas pelo Roberto, a abordagem foi confirmada e os cortes YAGNI e os 2 checkpoints estão registrados." Escopo do prompt da sessão 5: itens E1–E13 do PORTE §5.1 — `report-lint.py` (avaliação obrigatória com ≥ N camadas, `PENDENTE`, `git check-ignore`, veredito fora de code fence), `gate-baseline.sh`, `gate-shell-evidencia.sh` + receita com `rc=$?`, `verify-gate.sh --trace` e `--sem-define`, `test-baseline.sh` sobre `{{TEST_CMD}}`, `avaliador-guard.sh` no `sdd-build` 1.5 e 5d, coerência da flag LLM Prompts, fragmento `LLM_PROMPTS_BUILD_REPORT.md` e o adaptador PreToolUse chamando `report-lint.py --stdin`.

**Context Gathered:**
- Fato (conferido): worktree `feat/f7-evidencia` em `1c9bbc7` = `origin/main` = tag `v2.2.7`; 17 skills; 514 testes no piso; nenhum rebase necessário.
- Fato (conferido): o checkout local do privado (`~/RDD/Wordpress`, branch `main`) está **atrás** do `origin/main` dele; `scripts/gates/avaliador-pendente-guard.sh` e `.githooks/claude-avaliador-guard.py` não existem no disco e o guard local tem 321 linhas. Lidas por `git show origin/main:<arquivo>` (`ecdab8d41`, 2026-10-29), as 6 fontes têm as linhas do plano: 541, 77, 159, 111, 243 (verify-gate) e 88. Nada foi alterado no privado.
- Fato (conferido): 11 dos 32 testes de `tests/test_report_lint.py` esperam exit 0 com relatório **sem declaração nenhuma sobre o avaliador**; 7 deles (classe `Migrations`) nem têm tabela de ATs. "Ausência reprova" (E1, D4) e "os 32 contratos não mudam" conflitam; a D4 resolve.
- Fato (conferido): dos 8 `BUILD_REPORT` do open, 5 não declaram nada sobre o avaliador (F1, F2, F3, M1, W0) e saem 0 no lint atual; F4, F5 e F6 citam `AVALIACAO_*.md` que existem em `sdd/reviews/`.
- Fato (conferido): os logs de evidência do open terminam em `exit=N` (425 linhas em 8 pastas), gravados com `${PIPESTATUS[0]}` em bash; a receita do `EVIDENCIA.md` não grava exit nenhum (`{ echo "\$ $cmd"; eval "$cmd" 2>&1 | tail -n 200; }`).
- Fato (conferido): o `EVIDENCIA.md` documenta o fail-open — "Cabeçalho em inglês (`Result | Evidence`) não é reconhecido: o lint não confere linha nenhuma e sai 0".
- Fato (conferido): `tests/test_correcoes_w0.py` proíbe `PreToolUse`, `systemMessage`, `.githooks/`, "pelo hook" e "o hook NEGA" no `EVIDENCIA.md`; `tests/test_agnostico.py` proíbe nomes de ferramenta de um agente só em skills, templates, `AGENTS.md.tmpl` e playbook.
- Fato (conferido): o `init --vendors claude` gera só `.claude/skills` e `CLAUDE.md`; nunca escreveu `.claude/settings.json`. A F8 redesenha o `init`.
- Fato (conferido): a E12 no privado (`build.md:74-77`) — `LLM Prompts: true` no DEFINE exige a seção "LLM Prompts" no DESIGN (senão parar e iterar o DESIGN); `false` exige que ela não exista, com o drift detection armado.
- Inferência: o `gate-baseline.sh` não prova o gate da própria F7 (o `cmd` roda a suíte inteira do HEAD da cópia, que na base não tem os testes novos); a linha de base da F7 é rodar os testes novos contra a `v2.2.7`, como nas F5 e F6.

**Technical Context Observed (for Define):**

| Aspect | Observation | Implication |
|---|---|---|
| Likely Location | `sdd/bin/report-lint.py`, `sdd/bin/verify-gate.sh`, `sdd/bin/{gate-baseline,gate-shell-evidencia,avaliador-guard,test-baseline}.sh`, `sdd/config.example.yaml`, `sdd/templates/fragments/{EVIDENCIA,LLM_PROMPTS_BUILD_REPORT}.md`, `sdd/templates/BUILD_REPORT_TEMPLATE.md`, `.agents/skills/sdd-{build,release}/SKILL.md`, `sdd/fixtures/evidencia/`, `tests/`, `docs/roadmap.md` + PT, `MANIFEST.txt` | `sdd/bin/**`, `sdd/templates/**`, `sdd/fixtures/**`, `sdd/config.example.yaml` e `.agents/skills/**` disparam a Release |
| Relevant KB Domains | N/A (o open não tem `sdd/kb/` próprio) | `KB Domains = nenhum` no DEFINE |
| IaC Patterns | N/A | CI existente (`publish-gate.yml` + `testes-macos`) sem mudança |

## Discovery Questions & Answers

| # | Question | Answer | Impact |
|---|---|---|---|
| 1 | Como o `report-lint` trata o relatório que não prova a avaliação (D4)? | **Fail-closed sempre, com a forma mínima declarada** (recomendada), contra "fail-closed só quando dá para contar camadas" e "fail-open por default com `--estrito`" | Reprova cabeçalho não reconhecido (passa a reconhecer `Result \| Evidence`), ausência de `AVALIACAO` e de declaração, `N.A.` com ≥ N camadas e declaração sem motivo. Os 11 testes que esperam 0 mantêm a asserção; o relatório de exemplo deles ganha a tabela e `avaliador: N.A. (1 camada)` — única mudança de contrato, registrada no DEFINE |
| 2 | Quais dos 4 slots do plano entram no `sdd/config.example.yaml` (D11)? | **Só o limite de camadas** (recomendada), contra "os 4 slots" e "nenhum slot" | 1 slot: `evidence.require_avaliacao_layers: 2`. Caminhos fixos: `sdd/reports/evidence`, `sdd/traces` (com `SDD_TRACE_DIR` para os testes), `sdd/baselines/tests.txt` — mesma regra da KB em `sdd/kb/` (F5) |
| 3 | Onde entra a E6? | **Regra na F7, adaptador na F8** (recomendada), contra "E6 inteira na F7" e "E6 inteira na F8" | `report-lint.py --stdin <caminho>` com teste dos dois lados; a `sdd-build` chama o `avaliador-guard.sh` explicitamente; o `.claude/settings.json` com os 2 hooks é pendência da F8 |
| 4 | Qual versão a F7 publica? | **`v2.2.8` automática**, contra a recomendação "`v2.3.0` com tag à mão" e "decidir no bloco do OK" | Push fast-forward sem tag; as notas da Release e o `EVIDENCIA.md` dizem o que um relatório antigo precisa acrescentar |

## Sample Data Inventory

| Type | Location | Count | Notes |
|---|---|---:|---|
| Input files | privado `origin/main`: `scripts/gates/test-build-report-guard.sh`, `test-gate-baseline.sh`, `test-gate-shell-evidencia.sh`, `test-verify-gate-trace.sh`, `fixtures/shell-evidencia/` (3 logs) | 5 | Lista de casos já descobertos (inclusive os furos das revisões kimi, codex e fable); lidos só por `git show` |
| Output examples | `sdd/reports/BUILD_REPORT_*.md` do open | 8 | Conferência: o lint novo reprova F1, F2, F3, M1 e W0 (avaliação ausente) e aprova F4, F5 e F6, medido antes e depois |
| Ground truth | `sdd/reports/evidence/*/` do open | 425 linhas `exit=N` | Meta do `gate-shell-evidencia.sh`: 0 acusações falsas |
| Related code | privado `origin/main`: `.githooks/claude-build-report-guard.py`, `claude-avaliador-guard.py`, `scripts/gates/avaliador-pendente-guard.sh`, `gate-baseline.sh`, `gate-shell-evidencia.sh`, `scripts/verify-gate.sh` | 6 | Fontes do porte; específico da RDD não viaja (regra 4 do 8.0) |

**How samples will be used:**
- Os casos dos testes do privado são reescritos como fixtures limpas em `sdd/fixtures/evidencia/` (sem PII, sem caminho `/Users/`, sem `.claude/sdd/`); nada é copiado do privado.
- Os 8 relatórios do open são a conferência de verdade: o resultado esperado (5 reprovados por "avaliação ausente", 3 aprovados) é medido antes e depois do build; qualquer outro resultado precisa de explicação no BUILD_REPORT.
- Os 425 logs do open são o corpus de falso positivo do `gate-shell-evidencia.sh`.
- Medição sobre os 316 relatórios do privado: não feita (opção recusada).

## Approaches Explored

### Approach A: Porte por função, um ciclo, uma Release — Recommended

**Description:** as regras novas do `report-lint.py` entram como funções ao lado das atuais (D4, E1–E5, `--stdin`, `--pendente`); 4 scripts novos em `sdd/bin/` (`gate-baseline.sh`, `gate-shell-evidencia.sh` e `avaliador-guard.sh` portados quase sem mudança; `test-baseline.sh` novo, com 5 formatos de saída reconhecidos); `verify-gate.sh --trace` e `--sem-define`; `sdd-build` e `sdd-release` ligam os mecanismos; fragmentos e template atualizados; uma Release `v2.2.8`.

**Pros:**
- Um gate, uma revisão de contexto fresco, uma Release.
- Fiel às fontes do privado, o que facilita a F15.
- A verdade de cada regra mora num script testado dos dois lados.

**Cons:**
- PR grande (≈ 26 arquivos, 6 scripts com sabotagem).

**Why Recommended:** menor custo total; o tamanho do PR é compensado pelas sabotagens e pela revisão de contexto fresco.

### Approach B: Dois ciclos

**Description:** F7a com `report-lint` e avaliador (E1–E6, E11, E2 na release, `v2.2.8`); F7b com os gates de shell, baseline, trace e testes (E7–E10, E12, E13, `v2.2.9`).

**Pros:**
- O fail-closed sai antes; cada PR tem metade do tamanho.

**Cons:**
- Gate, CI macOS e revisão duas vezes; um ciclo consome uma sessão (medida da F3), e a F8 escorrega uma sessão.

### Approach C: Um motor em Python

**Description:** `sdd/bin/evidencia.py` com subcomandos (`lint`, `baseline`, `shell`, `guard`, `tests`) no lugar dos 4 scripts bash.

**Pros:**
- Sem risco de bash 3.2; um arquivo só para testar.

**Cons:**
- Reescreve o que o plano manda portar "quase sem mudança"; diverge do privado (pior para a F15); o `--trace` continua em bash.

## Selected Approach

| Attribute | Value |
|---|---|
| Chosen | Approach A |
| User Confirmation | 2026-10-30, "A — Porte por função, um ciclo, uma Release (recomendada)" |
| Reasoning | Menor custo total e fidelidade às fontes; o risco do PR grande é coberto por 6 sabotagens e pela revisão de contexto fresco |

## Key Decisions Made

| # | Decision | Rationale | Alternative Rejected |
|---|---|---|---|
| 1 | D4: `report-lint` fail-closed por default — reprova cabeçalho não reconhecido, ausência de avaliação, `N.A.` com ≥ N camadas e declaração sem motivo; reconhece também `Result \| Evidence` | Guard que itera só sobre o que aparece é default-PASS (PORTE §9); 5 dos 8 relatórios do open provam o furo | Fail-closed só com contagem possível (deixa `layers:` vazio passar em silêncio); fail-open com `--estrito` |
| 2 | A forma mínima do relatório (tabela reconhecida + linha do avaliador) é a única mudança de contrato; as 32 asserções ficam | Sem isso, 11 testes passariam a reprovar pelo motivo novo | Reescrever as asserções; manter os testes como estão |
| 3 | `N.A.` com contagem impossível (`layers:` vazio, sem DESIGN ou sem File Manifest) é aceito **com aviso** | É o comportamento do privado; o aviso impede o silêncio | Reprovar `N.A.` sem contagem (travaria todo projeto com `layers:` vazio, o default) |
| 4 | D11: 1 slot, `evidence.require_avaliacao_layers: 2`; os 3 caminhos ficam fixos | A regra 2 do PORTE fala de comandos; caminho fixo segue a decisão da KB (F5) | Os 4 slots do plano; nenhum slot |
| 5 | E6: `report-lint.py --stdin <caminho>` na F7; o adaptador `.claude/settings.json` (Write/Edit e despacho do avaliador) na F8 | A F8 redesenha o `init`; um merge de JSON só | E6 inteira na F7; E6 inteira na F8 |
| 6 | `avaliador-pendente-guard.sh` vira `report-lint.py --pendente`; a `sdd-release` 0a o chama | Um parser só para a declaração (era assim no privado) | Script próprio |
| 7 | `PENDENTE (motivo)` sai 0 com aviso no lint comum (o build travado registra); `--pendente` sai 1 e a release aborta | A escrita nunca trava; quem barra é a release | Reprovar `PENDENTE` no lint comum |
| 8 | `test-baseline.sh` reconhece unittest, pytest, jest/vitest, go e deno; saída não reconhecida com rc≠0 sai 3 (inconclusivo), nunca verde; falha nova só entra no baseline com `--aceitar <id>` | Implementação nova sobre `{{TEST_CMD}}`; o `deno-test-gate.sh` não porta | Slot de regex por projeto (não aprovado); aceitar falha nova sozinho |
| 9 | E12 só em texto (passo 1 da `sdd-build`) + teste de contrato, sem script | Regra de leitura de dois documentos que a skill já lê | Função nova no `design-lint.py` |
| 10 | Receita do `EVIDENCIA.md`: `out=$(cmd 2>&1); rc=$?; … [exit=$rc]`; o `gate-shell-evidencia.sh` aceita também o `exit=N` dos logs antigos | Funciona em zsh e bash; 0 acusação falsa no corpus | Só `[exit=N]` |
| 11 | Release `v2.2.8` automática | Decisão do Roberto | `v2.3.0` por tag (recomendada); decidir no bloco do OK |
| 12 | `sdd-build` e `sdd-release` sobem **minor** | Passos novos, não só texto | Patch |
| 13 | Abordagem A | Ver Selected Approach | B (dois ciclos); C (motor em Python) |

## Features Removed (YAGNI)

| Feature Suggested | Reason Removed/Deferred | Can Add Later? |
|---|---|---|
| Data de corte para relatório antigo (`CORTE_AVALIACAO` do privado) | O open só confere o relatório nomeado na chamada; os antigos não são reconferidos | Yes |
| Adaptador `.claude/settings.json` (E6, parte do vendor) | Decisão 5: vai para a F8 | Yes (F8) |
| Slots `evidence.dir`, `evidence.traces_dir`, `tests.baseline_file` | Decisão 4: caminhos fixos | Yes |
| `avaliador-pendente-guard.sh` como script próprio | Decisão 6: vira `report-lint.py --pendente` | No |
| `gate-shell-evidencia.sh --all` | Passar a pasta `sdd/reports/evidence` faz o mesmo | Yes |
| Trace gravado pelo curator | O curator nasce na F14 | Yes (F14) |
| Pre-commit chamando o `report-lint` | Hooks de git são a F8 | Yes (F8) |
| Formatos de teste além de 5 (rspec, phpunit, cargo…) no `test-baseline.sh` | Saída não reconhecida já cai em 3, nunca em verde | Yes |
| `scripts/lib/camadas.tsv`, propagação do rc 3 do deno, marcas `[auto]`/`[Dn]` | Específico da RDD (regra 4 do 8.0) ou da F9; `layers:` substitui o mapa | Yes (F9, marcas) |
| Medição do lint novo sobre os 316 relatórios do privado | Opção recusada nas amostras | Yes |

## Incremental Validations

| Section | Presented | User Feedback | Adjusted? |
|---|---|---|---|
| Checkpoint 1: conceito (a verdade em `sdd/bin/`, adaptador na F8), os 9 cortes YAGNI e os 10 componentes (`report-lint.py`, `verify-gate.sh`, 4 scripts novos, 1 slot, fragmentos e template, `sdd-build` e `sdd-release`, fixtures, testes, roadmap, `MANIFEST.txt`) | Yes | "confere" | No |
| Checkpoint 2: prova de cada parte dos dois lados (tabela por script), provas da frente (gate, bash 3.2, CI Ubuntu + macOS, `skill-lint`, `check-versions`, `test_agnostico`, 6 sabotagens, testes novos vermelhos na `v2.2.7`, revisões, BUILD_REPORT da F7 nas regras novas), falhas previstas (trace sujando o repo, `check-ignore` indisponível, `--touched`, `--aceitar`, receita em zsh) e contratos intactos | Yes | "confere" | No |

## Suggested Requirements for /define

### Problem Statement (Draft)

O sdd-open é fail-open nos três pontos onde o SDD privado é fail-closed: o `report-lint.py` aprova relatório sem tabela reconhecida ou sem nenhuma palavra sobre o avaliador (5 dos 8 relatórios do próprio open passam assim), não vê evidência que o git ignora, e não sabe de `avaliador: PENDENTE`; o `[exit=N]` de um log pode ser o exit do `tail`; nenhum gate prova que a asserção fica vermelha no código anterior; nenhum registro diz quantas vezes o gate rodou; falha de teste antiga e nova são indistinguíveis; e o avaliador pode ser despachado com trabalho não commitado, que ele pode apagar ao restaurar arquivos.

### Target Users (Draft)

| User | Pain Point |
|---|---|
| Quem roda a `sdd-build` num projeto com o open (qualquer um dos 7 agentes) | O relatório passa verde sem provar a avaliação; evidência some no commit; o avaliador pode destruir trabalho não commitado |
| Quem roda a `sdd-release` | Publica feature com avaliação pendente ou com log de exit falso |
| Mantenedor do open e do privado (Roberto, F15) | Precisa dos mecanismos do privado no open para substituí-lo (P4) |

### Success Criteria (Draft)

- [ ] `report-lint.py` reprova `BUILD_REPORT_sem_avaliacao`, `…_pendente` (no modo `--pendente`) e `…_evidencia_ignorada` e aprova o controle; reprova F1, F2, F3, M1 e W0 do open e aprova F4, F5 e F6.
- [ ] As 32 asserções de `tests/test_report_lint.py` ficam iguais; só o relatório de exemplo dos 11 testes que esperam 0 ganha a forma mínima.
- [ ] `gate-shell-evidencia.sh` acusa `| tail` sem `rc=$?` e `[exit=]` vazio, e não acusa nada nos 425 logs do open.
- [ ] `verify-gate.sh --trace` grava 1 linha JSONL por execução; `--print` e `SDD_TRACE=off` não gravam; os 6 exits e as fixtures de `sdd/fixtures/` ficam idênticos aos da `v2.2.7`.
- [ ] `gate-baseline.sh`, `avaliador-guard.sh` e `test-baseline.sh` têm fixture e teste dos dois lados; todo script novo passa no `grep` de bash 3.2 sem achado.
- [ ] `sdd-build` e `sdd-release` ligam os mecanismos (1.5, 5b, 5d, 6; 0a) com o "por quê" de cada regra nova; `skill-lint --conversa` 17/17; `check-versions --base v2.2.7 --base-obrigatoria` verde.
- [ ] Verify Gate `--strict` 0; 1 sabotagem por script alterado ou novo; testes novos vermelhos na `v2.2.7`; revisão de contexto fresco sem HIGH aberto; o `BUILD_REPORT_F7_EVIDENCIA.md` passa nas regras novas.
- [ ] Release `v2.2.8` com `SHA256SUMS.txt` conferido por `shasum -a 256 -c`.

### Constraints Identified

- Os 32 contratos do `report-lint.py` (com a exceção da forma mínima), os 6 exits do `verify-gate.sh` e `sdd/fixtures/` intactos; lints com 0/1/64 e mensagens com `🛑`, `RESULTADO:` e `→`.
- P2: nenhum nome de ferramenta de um agente só em skill, template, `EVIDENCIA.md`, `AGENTS.md.tmpl` ou playbook; o adaptador da E6 só no que o `init` gerar (F8).
- bash 3.2 e Python 3.9 stdlib; CI em Ubuntu e macOS; nada de `mapfile`, `declare -A`, `${x^^}`; `rm -rf` só com `"${X:?}"`.
- Publish-gate: fixtures sem e-mail fora de `example.com/.org/.net`, CPF, CNPJ, telefone, 11+ dígitos seguidos ou `/Users/<nome>/`.
- Camada de conversa intacta (bloco comum nas 15 skills, `FRASES` do `test_conversa`); "Por que cada regra existe" logo antes de `## Encerramento (obrigatório)`; bloco do OK da `sdd-release` com os mesmos rótulos, ordem e uma pergunta só.
- `docs/roadmap.md` e PT continuam com 7 linhas; a linha "Hooks and evidence"/"Hooks e evidência" passa a falar só dos hooks.
- Todo arquivo novo no `MANIFEST.txt` (`LC_ALL=C`); `git add` por nome; `sdd/features|handoffs|reports|reviews|traces/` fora dos commits da branch de trabalho.

### Out of Scope (Confirmed)

- Os itens da tabela YAGNI acima.
- Hooks de git `pre-commit`/`pre-push`, `core.hooksPath`, a D10 e o `.claude/settings.json` (F8); encadeamento entre fases, `exit 40 AGUARDANDO_HUMANO` e classes D1–D5 (F9); revisão adversarial e registry (F10/F11).
- Regenerar o sdd-starter; alterar o sdd-starter ou o repositório privado.

## Session Summary

| Metric | Value |
|---|---:|
| Questions Asked | 5 |
| Approaches Explored | 3 |
| Features Removed (YAGNI) | 10 |
| Validations Completed | 2 |

## Next Step

Execute o **SDD Define by RDD**.
