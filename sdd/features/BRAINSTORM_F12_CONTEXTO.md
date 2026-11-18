# BRAINSTORM: F12 Contexto, patterns e governança

> Exploratory session to clarify intent and approach before requirements capture

## Metadata

| Attribute | Value |
|---|---|
| Feature | F12_CONTEXTO |
| Date | 2026-11-03 |
| Author | brainstorm-agent |
| Status | Handoff Ready |

## Initial Idea

**Raw Input:** "Sessão 9 da frente INCORPORAR_STARTER: F12 sozinha (a F13 fica para a sessão 10). /sdd-brainstorm Leia e execute o prompt da sessão 9 da frente INCORPORAR_STARTER. […] A sessão faz a F12 (Contexto, patterns e governança) do brainstorm à release, numa worktree nova […] criada de origin/main = 9508ff0 (tag v2.3.1)." O prompt da sessão (`sdd/handoffs/SESSION_PROMPT_INCORPORAR_STARTER.md`, branch `docs/incorporar-starter`, `5246c7a`) pede C1–C11 do PORTE §5.5 mais a correção 4.6 (dono do `prova_script`).

**Context Gathered:**
- Fato (conferido): worktree `/Users/robertoduarte/rdd-worktrees/sdd-open-f12-contexto`, branch `feat/f12-contexto` em `9508ff0` = `origin/main` = tag `v2.3.1`; artefatos SDD da branch `docs/` no disco, fora do commit; `codex` e `claude` instalados.
- Fato (conferido): o `DEFINE_TEMPLATE.md` do Open não tem a linha `Governança` nem `CONTEXTO de domínio` (a W0 tirou a 2ª); existem 7 DEFINEs de fixture rastreados (`sdd/fixtures/DEFINE_FIXTURE_*.md`, `sdd/fixtures/fluxo/DEFINE_*.md`).
- Fato (conferido): a `sdd-governanca` do Open (2.3.0) já grava o `prova_script` adaptado em `sdd/tests/governanca/{FEATURE}_<Gnn>.sql` e acrescenta `psql -v ON_ERROR_STOP=1 -f …` ao `cmd` existente; banco só de produção ⇒ `prova_manual`. Hoje é skill avulsa, rodada à parte (fail-open).
- Fato (conferido, privado `origin/main` = `f70a7aba9`, só leitura): `define.md` Steps 1.5 (l. 68–108) e 6.5 (l. 306–395); `scripts/contexto-lint.sh` e `patterns-lint.sh` são bash 3.2 + awk POSIX, sem array associativo, com `--self-test` por classe de erro estável; `governanca-fronteira.sh` faz snapshot sha256 com `git status -z`; `docs-extract-decisions.sh` com conservação (extraídos + órfãos = lidos).
- Fato (conferido): no privado, o cartógrafo prova "só o agente escreveu" comparando `git status --porcelain` — prova que o próprio `governanca-fronteira.sh` documenta como cega para sobrescrita de arquivo já sujo.
- Fato (conferido): PORTE §4.6 — `revisor-governanca.md:60` diz que o `/design` escolhe onde roda o `prova_script`, mas o `design.md` não tem esse passo.
- Fato (conferido): `WORKFLOW_CONTRACTS.yaml` é lido no privado por 2 gates (`sdd-contexto-patterns-gate.sh`, gate de UX); `invariants.md` só pelo curator, release e gates de docs (F14 ou específicos da RDD).
- Fato (conferido): o quadro F15 do plano cita `schema.check_cmd` como destino do `audita-schema-gate.sh` do privado; o Open já tem `release.landmines_cmd`.
- Inferência: gravar o marcador de governança **antes** do despacho fecha o buraco de uma parada exit 40 deixar o DEFINE sem trava.

**Technical Context Observed (for Define):**

| Aspect | Observation | Implication |
|---|---|---|
| Likely Location | `.agents/skills/sdd-define`, `sdd-design`, `sdd-governanca` (+ `sdd-ux-review` se o C11 tocar o template); `sdd/bin/`; `sdd/templates/DEFINE_TEMPLATE.md`; `sdd/patterns/`; `sdd/WORKFLOW_CONTRACTS.yaml`; `sdd/fixtures/`; `tests/` | 3–4 skills sobem de versão; 4 scripts novos com fixture e teste dos dois lados |
| Relevant KB Domains | nenhum (`sdd/kb/` ausente no repositório do pacote) | — |
| IaC Patterns | N/A | CI existente (`release.yml`, Ubuntu + macOS) cobre a suíte maior; conferir o teto de 25/30 min |

## Discovery Questions & Answers

| # | Question | Answer | Impact |
|---|---|---|---|
| 1 | D5 — a revisão de governança passa a rodar dentro de todo Define (Step 6.5)? `[D3]` | Sim, sempre, com N.A. registrado (inclusive com `--parar`) | Step 6.5 obrigatório; revisor fresco decide N.A.; não rodar ⇒ exit 5 |
| 2 | D8 — em que fase o SQL de prova da governança é gravado e ligado ao Verify Gate? `[D3]` | No Define, no mesmo passo da revisão | O Step 6.5 grava o `.sql` e liga o `psql` ao `cmd`; o Design só lista no manifest; brief do revisor corrige a frase do privado |
| 3 | DEFINE sem a linha `Governança`: trava sempre ou só DEFINE novo? `[D3]` | Trava sempre, com a saída explicada (rodar o 6.5 ou dispensar com motivo) | `verify-gate.sh` exit 5 em qualquer DEFINE sem a linha; fixtures que esperam 0 ganham a linha |
| 4 | O slot `schema.check_cmd` entra no `sdd/config.yaml`? `[D3]` | Cai: nenhum slot novo | Na F15 o gate de schema do privado vai para `release.landmines_cmd`; corrigir o quadro F15 do plano |
| 5 | A F12 sai numa Release só ou em duas? `[D3]` | Uma Release só (um DEFINE, um build, uma revisão) | Risco aceito: se a sessão não chegar à release, nada sai; mitigação: commits parciais na branch |
| 6 | Versão da Release? `[D3]` | `v2.4.0` por tag (push atômico com `main`) | Nota da Release explica o exit 5 nos DEFINEs antigos e a linha de dispensa |

## Sample Data Inventory

| Type | Location | Count | Notes |
|---|---|---:|---|
| Input files | privado `origin/main`: `.claude/sdd/fixtures/contexto/` · `.claude/sdd/fixtures/patterns/` | 13 · 12 | Fixtures dos dois lados (passa/reprova) dos lints; casos de borda (linha além do fim, ctx desconhecido, 2 camadas) |
| Output examples | privado: `.claude/sdd/contexto/*.md` (8 + README) · `GOVERNANCA_REVIEW_*` · `docs/adr/` (3) | 8 · 56 refs · 3 | Molde de formato do CONTEXTO, do relatório de governança e do índice de ADR |
| Ground truth | `sdd/fixtures/DEFINE_FIXTURE_GOVERNANCA.md` (Open) · `architecture/patterns/dominio.md` (privado) | 1 · 1 | DEFINE com gatilho; mapa de domínios `ctx:` |
| Related code | privado `scripts/contexto-lint.sh` (457), `patterns-lint.sh` (461), `docs-extract-decisions.sh` (164), `governanca-fronteira.sh` (110); `.claude/agents/exploration/cartografo-contexto.md`, `workflow/revisor-governanca.md` | 6 | Fonte do porte fiel |

**How samples will be used:**
- As fixtures e os CONTEXTOs/relatórios do privado são molde; tudo que entra no Open é reescrito com um domínio fictício (ex.: pedidos/estoque), sem nome de tabela, edge ou caminho da RDD (regra 4 do 8.0; `publish-gate`). Nada é copiado literalmente.

## Approaches Explored

### Approach A: Porte fiel, com uma fronteira só para os dois papéis — Recommended

**Description:** Os 4 scripts vêm do privado quase linha a linha (já bash 3.2 + awk), com refs da RDD → `layers:` e `sdd/patterns/`; o `governanca-fronteira.sh` (snapshot sha256) prova a escrita do cartógrafo **e** do revisor, cada um com seu arquivo permitido; briefs `sdd-define/references/cartografo.md` e `sdd-governanca/references/revisor.md` usam a escada de despacho existente (subagente → `sdd-fluxo.sh despachar` → exit 40).

**Pros:**
- Menor risco e esforço: o código já roda no piso; as fixtures do privado mapeiam 1:1.
- Corrige a prova fraca do cartógrafo do privado (P1).

**Cons:**
- Carrega ~900 linhas de bash/awk, com a fragilidade de locale e UTF-8 já mitigada no privado.

**Why Recommended:** Cabe numa Release só (decisão 5) na maior frente do P4, sem reescrever código provado.

### Approach B: Núcleo em Python stdlib

**Description:** `.sh` finos com o miolo em Python, como a F9 fez com o `sdd-fluxo.sh`; um só leitor de cabeçalho para contexto e patterns.

**Pros:**
- Mais robusto a locale/acento; menos duplicação entre os dois lints.

**Cons:**
- ~900 linhas reescritas; fixtures deixam de corresponder 1:1; esforço maior na frente maior.

### Approach C: Cartógrafo sem agente fresco

**Description:** O próprio Define faz a engenharia reversa do domínio; o `contexto-lint` só confere o formato.

**Pros:**
- Sem despacho nem exit 40 para o cartógrafo; mais barato.

**Cons:**
- Quem escreve o DEFINE descreve o código que vai mudar (o viés que o C1 quer evitar); a prova no Codex fica só para o revisor.

## Selected Approach

| Attribute | Value |
|---|---|
| Chosen | Approach A |
| User Confirmation | 2026-11-03, resposta "1" à pergunta de abordagem |
| Reasoning | Porte fiel de código já compatível com o piso, mais a fronteira sha256 para os dois agentes frescos, cabe numa Release só e corrige a prova fraca do cartógrafo |

## Key Decisions Made

| # | Decision | Rationale | Alternative Rejected |
|---|---|---|---|
| 1 | D5: governança sempre no Define (Step 6.5), N.A. registrado, inclusive com `--parar` | Fail-closed (regra 5 do 8.0); quem decide N.A. não é quem escreveu | Só com gatilho por triagem local (o autor se triaria); continuar avulsa (fail-open) |
| 2 | D8: o `prova_script` é gravado e ligado ao `cmd` no Step 6.5 | A prova nasce com o Gnn; nada fica órfão; é o que o Open já faz | No Design (passo novo, prova pendente no Define); o revisor decide (não conhece o banco e só escreve o relatório) |
| 3 | DEFINE sem `Governança` ⇒ exit 5 sempre, com as 2 saídas na mensagem | Critério de pronto literal; sem buraco de marca de versão | Só DEFINE novo (fail-open por omissão da marca); aviso por uma versão |
| 4 | `schema.check_cmd` cai | Slot sem leitor é texto morto; `release.landmines_cmd` recebe o mesmo comando na F15 | Slot vazio documentado; slot com consumidor (escopo novo) |
| 5 | Uma Release só | Escolha do Roberto: um ciclo de CI e revisão | Duas Releases (governança primeiro) |
| 6 | `v2.4.0` por tag | O número avisa que o método mudou (Define com 2 passos novos; DEFINE antigo trava) | `v2.3.2` automática; `v3.0.0` |
| 7 | Amostras do privado como molde, reescritas com domínio fictício | Preserva os casos de borda sem vazar nada da RDD | Só fixtures do zero |
| 8 | Fronteira sha256 única para cartógrafo e revisor | Corrige a prova cega a sobrescrita do cartógrafo (P1) | `git status --porcelain` como no privado |
| 9 | Marcador `[NEEDS CLARIFICATION: governança não rodou…]` gravado antes do despacho do revisor | Uma parada exit 40 não pode deixar o DEFINE destravado | Gravar só depois da 2ª falha (como no privado) |
| 10 | Cartógrafo não trava: 2ª falha ⇒ `nenhum (<motivo>)` e segue | O CONTEXTO é ajuda; a trava é da governança | Cartógrafo bloqueante |

## Features Removed (YAGNI)

| Feature Suggested | Reason Removed/Deferred | Can Add Later? |
|---|---|---|
| C5 `sdd/invariants.md` | Sem leitor até o curator (F14); arquivo sem leitor apodrece | Yes (F14) |
| `sdd/patterns/dominio.md` preenchido | O README descreve o formato; sem mapa, o Step 1.5 grava `pular (sem sdd/patterns/dominio.md)` e diz como criar | Yes |
| Gate do extrator de ADR na release (C4) e os gates de docs do privado | O `design-lint` já protege os títulos; o extrator roda sob demanda com `--self-test` | Yes |
| `sdd-contexto-patterns-gate.sh` do privado (leitor do C9) | Substituído por 1 teste que confere o yaml reduzido contra os scripts | Yes |
| Slot `schema.check_cmd` | Decisão 4 | Yes |

## Incremental Validations

| Section | Presented | User Feedback | Adjusted? |
|---|---|---|---|
| Checkpoint 1 — conceito, componentes e limites | Yes | "1 — está certo, siga" | No |
| Checkpoint 2 — caminho, falhas (cartógrafo não trava; marcador antes do despacho) e provas | Yes | "grave o brainstorm e execute o define, ux-review, design, review do design, build, review do build" | No |

## Suggested Requirements for /define

### Problem Statement (Draft)

O Define do Open nasce sem saber que regras já vigoram no código do domínio que a feature toca e deixa a governança como skill avulsa que ninguém é obrigado a rodar (fail-open); a F12 põe um cartógrafo fresco no Step 1.5, a governança obrigatória e fail-closed no Step 6.5, e dá ao Design contexto, patterns e ADR verificáveis.

### Target Users (Draft)

| User | Pain Point |
|---|---|
| Quem conduz uma feature no Open (aluno contador, Roberto) | O DEFINE ignora regras já vigentes no código; governança esquecida só aparece depois do build, quando custa migração |
| O agente que escreve o Design | Não tem contexto de domínio nem patterns citáveis e verificáveis; landmine lida só pelo gancho do índice |
| O Roberto na F15 | Precisa do mecanismo do privado (cartógrafo, revisor, fronteira, lints) no Open para desligar o privado |

### Success Criteria (Draft)

- [ ] `contexto-lint.sh --self-test` e `patterns-lint.sh --self-test` saem 0, cada classe de erro com fixture vermelha e verde.
- [ ] DEFINE sem a linha `Governança` ⇒ `verify-gate.sh` exit 5 (e a mensagem traz as 2 saídas).
- [ ] `governanca-fronteira.sh --comparar` sai 1 com `FORA:` quando o agente escreve fora do arquivo permitido, inclusive sobrescrevendo arquivo já sujo.
- [ ] Despacho do cartógrafo e do revisor provados no Codex CLI: exit 40 com o brief gravado.
- [ ] Todo script novo sem `mapfile|declare -A|${x^^}`, com baseline vermelha na `v2.3.1` e 1 sabotagem.
- [ ] `skill-lint --conversa` 0 nas 17 skills; `sdd-decisoes-lint --sites` 0 com a contagem nova; `check-versions --base v2.3.1 --base-obrigatoria` 0.
- [ ] Suíte inteira no piso cabe no teto do CI (25 min Ubuntu, 30 macOS) — número exato TBD na medição.
- [ ] Revisão de contexto fresco sem HIGH aberto; revisão adversarial real `loop` PRONTO e `--conferir` CONFERE no commit final.

### Constraints Identified

- bash 3.2 + Python 3.9 stdlib; nenhum nome de ferramenta de um agente só em skill/template (`tests/test_agnostico.py`).
- Específico da RDD não viaja; `publish-gate` reprova caminho `/Users/<nome>/`, e-mail fora de `example.*`, 11+ dígitos.
- Delta-only nas skills; a `sdd-governanca` não é reescrita (o passo entra na `sdd-define`).
- Contratos que não quebram: exits do `verify-gate.sh` (0/2/3/4/5/64), `sdd-fluxo.sh`, `adversarial-review.sh`, `report-lint.py`, hooks, camada de conversa, `init` sem sobrescrever.
- Todo arquivo novo no `MANIFEST.txt` (`LC_ALL=C sort`); artefatos SDD nunca no commit da branch de trabalho.
- Uma Release (`v2.4.0` por tag); push só com OK do Roberto citando "sdd-open".

### Out of Scope (Confirmed)

- C5 `invariants.md` e `--cruzar`/`--validar-inv` (F14).
- Revisão de schema do privado e o slot `schema.check_cmd`.
- UX e LLM no código (`sdd-loop-builder`, F13); curator, `/drive` (F14).
- Alterar o repositório privado ou o sdd-starter.
- `dominio.md` preenchido; gate de docs na release.

## Session Summary

| Metric | Value |
|---|---:|
| Questions Asked | 7 |
| Approaches Explored | 3 |
| Features Removed (YAGNI) | 5 |
| Validations Completed | 2 |

## Next Step

Execute o **SDD Define by RDD**.
