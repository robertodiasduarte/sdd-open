# BRAINSTORM: F9 Fluxo encadeado e decisões

> Exploratory session to clarify intent and approach before requirements capture

## Metadata

| Attribute | Value |
|---|---|
| Feature | F9_FLUXO |
| Date | 2026-10-31 |
| Author | brainstorm-agent |
| Status | Handoff Ready |

## Initial Idea

**Raw Input:** "Brainstorm da F9 com a `sdd-brainstorm`, gravando `sdd/features/BRAINSTORM_F9_FLUXO.md` a partir do quadro F9 e do 8.1 do plano. Pronto quando: D1, D11, a prova no Codex CLI, o lugar da seção "Encerramento" e a versão foram respondidas pelo Roberto, a abordagem foi confirmada e os cortes YAGNI e os 2 checkpoints estão registrados." Escopo do prompt da sessão 7: itens F1–F3, F6–F8, F10, F11 do PORTE §5.3 — `sdd/templates/fragments/FLUXO_ENCADEADO.md` + seção "Encerramento" encadeada nas skills de fase (F1); classes D1–D5 no item 9 reservado do `PERGUNTA_DECISAO.md` + `sdd/bin/sdd-decisoes-lint.sh` com `--sites` e `--self-test` (F2); recibo "Decidi sozinho" (F3); `[auto]` no `sdd-design` (F6); `sdd/bin/sdd-fluxo.sh` com `review-design` e `loop`, exits 0/10/20/30/40 AGUARDANDO_HUMANO/64 e `--self-test` (F7); pontuação forte/fraco da heurística LLM Prompts no `sdd-define` (F8); tipos de entrada no `sdd-brainstorm` (F10); `UX_REVIEW_*.md` anteriores no `sdd-ux-review` (F11).

**Context Gathered:**
- Fato (conferido): worktree `feat/f9-fluxo` em `7c640eb` = `origin/main` = tag `v2.2.9`; só `?? sdd/{features,handoffs,reports,reviews}/` no status; a cópia do handoff bate com a branch `docs/incorporar-starter`; nenhum rebase necessário.
- Fato (conferido): Codex CLI instalado nesta máquina (`codex-cli 0.163.0`, `/opt/homebrew/bin/codex`).
- Fato (conferido): as fontes do privado foram lidas do `origin/main` dele (`1b1c1d41b`), sem alterar nada. `scripts/sdd-fluxo.sh` (283 linhas) e `scripts/sdd-decisoes-lint.sh` (103) são **zsh + perl** (`#!/bin/zsh`, `perl -MJSON::PP`); o piso do Open é bash 3.2 + Python stdlib (P2).
- Fato (conferido): o `sdd-fluxo.sh` do privado tem `loop` (exits 0 PRONTO / 10 CONTINUAR / 20 BLOQUEADO / 30 AGUARDANDO_RECIBO / 64) e `review-design` (0 EXIGIDO / 1 DISPENSAVEL / 64). **Não há exit 40** lá: o 40 AGUARDANDO_HUMANO é novo, para o despacho de papel fresco em vendor sem subagente (tabela de degradação do 8.0).
- Fato (conferido): o `review-design` do privado procura superfície de segurança por uma regex de 14 termos — 8 genéricos (`auth`, `login`, `token`, `senha`, `password`, `jwt`, `GRANT`, rota pública) e 6 da RDD (`supabase/migrations/`, `supabase/functions/`, `RLS`, `policy`, `verify_jwt`, `service_role`).
- Fato (conferido): o `loop` do privado lê `META.txt` (`reviewer_exit`, `auditor_exit`, `revisor2_*`, `desempate_*`, `convergencia_1o_passe`), `reviewer.verdicts.jsonl`, `auditor.verdicts.jsonl` (AGREE/DISAGREE_EVIDENCE/DISAGREE_CONCERN/NOVO), o ledger por célula (`| achado | SEV | VEREDITO | rodada=N | evidência |`) e a avaliação (`VEREDITO: PASS|NEEDS_WORK|PASS_PENDENTE_RECIBO`). O "`| tee` proibido" é regra do `build.md` do privado ("o exit de um pipeline é o do `tee`"), não do script.
- Fato (conferido): o `--sites` do privado procura menção a `AskUserQuestion` — nome que o `tests/test_agnostico.py` do Open proíbe em `.agents/skills/`. No Open, o lugar das perguntas é o exemplo de cada `references/como-falar.md`: **15 perguntas de decisão em 15 skills**, achadas pelo `perguntas()` de `sdd/bin/skill-lint.py`; nenhum `SKILL.md` tem pergunta no formato.
- Fato (conferido): `PERGUNTA_DECISAO.md` item 9 diz "Classe da decisão: reservado. Uma versão futura do pacote marca a pergunta com `[Dn]` antes do negrito"; `tests/test_conversa.py:196` confere o trecho `[Dn]` no fragmento.
- Fato (conferido): as 9 skills com `## Encerramento (obrigatório)` são brainstorm, define, governança, ux-review, design, build, iterate, release e new-session; `tests/test_docs.py:352` exige `## Por que cada regra existe` **logo antes** do Encerramento e `tests/test_contrato_build_release.py:119` recorta o texto entre os dois títulos.
- Fato (conferido): `sdd/config.example.yaml` já tem `review:` com `vendors: ""`; não tem `flow:`.
- Fato (conferido): `scripts/next-version.sh` compara a versão por número (sem `sort -V`), então `v2.2.10` > `v2.2.9`.
- Fato (conferido): o `FLUXO_ENCADEADO.md` do privado (101 linhas) é dono da ordem das fases, da lista D1–D5, das paradas que não são decisão, da linha de transição, do recibo "Decidi sozinho", da parada espelho→worktree e do teto do loop.
- Inferência: com `flow.autonomous: false`, uma pergunta que hoje é feita continua feita; a classe só muda algo com o encadeamento ligado. Por isso precisa de uma marca para "pergunta que só existe sem autonomia" (`[auto]`), além de D1–D5.

**Technical Context Observed (for Define):**

| Aspect | Observation | Implication |
|---|---|---|
| Likely Location | `sdd/bin/sdd-fluxo.sh` e `sdd/bin/sdd-decisoes-lint.sh` (novos), `sdd/templates/fragments/FLUXO_ENCADEADO.md` (novo), `sdd/templates/fragments/PERGUNTA_DECISAO.md`, `sdd/config.example.yaml`, as 9 `SKILL.md` com Encerramento, os 15 `references/como-falar.md`, `sdd/fixtures/fluxo/` (novo) e `sdd/fixtures/conversa/`, `scripts/publish-gate.sh`, `tests/`, `MANIFEST.txt` | `sdd/bin/**`, `sdd/templates/**`, `sdd/fixtures/**`, `.agents/skills/**` e `sdd/config.example.yaml` disparam a Release |
| Relevant KB Domains | N/A (o Open não tem `sdd/kb/` próprio) | `KB Domains = nenhum` no DEFINE |
| IaC Patterns | N/A | CI existente (`publish-gate.yml` + `testes-macos`) sem mudança de workflow |

## Discovery Questions & Answers

| # | Question | Answer | Impact |
|---|---|---|---|
| 1 | O Open passa a encadear as fases sozinho (D1)? | **Configurável, desligado por default** (recomendada), contra "ligado por default" e "sem encadeamento" | Slot `flow.autonomous: false`; desligado, as skills fazem o que fazem hoje mais a marca da classe e a subseção nova; ligado, a fase seguinte é chamada na mesma sessão quando o gate da anterior sai 0, e perguntas `[auto]` viram a recomendada + recibo |
| 2 | Quais slots a F9 acrescenta (D11)? | **Os dois, com os termos genéricos fixos no script** (recomendada), contra "os dois, sem termos fixos" e "só `flow.autonomous`" | `flow.autonomous: false` e `review.security_globs: ""` (em `review:`, ao lado de `vendors`); os 8 termos genéricos ficam no `sdd-fluxo.sh` (falso positivo só custa uma revisão); os globs do slot e os de `layers.sql` (quando preenchida) também contam como superfície de segurança |
| 3 | Como a prova do exit 40 no Codex CLI fica registrada (P2)? | **As duas: fixture no `--self-test` e uma execução real do `codex exec`** (recomendada), contra "só a execução real" e "só a fixture" | O CI prova o contrato do script em Ubuntu e macOS sem depender do Codex; uma execução real numa cópia temporária do repositório prova que um agente sem subagente segue a instrução da skill, com o log em `evidence/F9_FLUXO/` |
| 4 | Onde entra a seção do fluxo encadeado nas 9 skills? | **Subseção `### Fluxo encadeado` dentro do `## Encerramento (obrigatório)`, depois do Próximo passo** (recomendada), contra "seção `##` nova antes do rodapé" e "trocar o Próximo passo pelo bloco" | Bloco comum idêntico nas 9 (conferido por teste, como as `FRASES` da camada de conversa) que aponta para `FLUXO_ENCADEADO.md`, mais 1 linha própria por skill; os 2 testes de ordem e o rodapé ficam intactos |
| 5 | Qual versão a F9 publica? | **`v2.2.10` automática** (recomendada), contra "`v2.3.0` por tag" e "decidir no bloco do OK" | Push em `main` e nada mais; com o encadeamento desligado por default, ninguém vê o comportamento mudar sem ligar o slot; o aviso fica no comentário do slot e na subseção |

## Sample Data Inventory

| Type | Location | Count | Notes |
|---|---|---:|---|
| Input files | Privado (`origin/main` `1b1c1d41b`): `scripts/sdd-fluxo.sh`, `scripts/sdd-decisoes-lint.sh`, `.claude/sdd/templates/fragments/FLUXO_ENCADEADO.md` | 3 | Só leitura; dizem os contratos de exit, a leitura do ledger por célula e as regras de classe |
| Input files | Privado: 69 `ledger-review.md` em `.claude/sdd/reports/evidence/*/` e `.claude/sdd/archive/DOGFOOD_20260824/` (`META.txt` + `reviewer.verdicts.jsonl`) | 3–5 + 1 | Forma real das linhas: `R1@codex` e `R1@opus` na mesma rodada; `R1` reusado em `rodada=1` e `rodada=2`; DOGFOOD com `auditor_exit 68` (review inválida → CONTINUAR). Reescritos do zero, sem dado da RDD |
| Output examples | `sdd/features/DESIGN_F1_*.md` … `DESIGN_F8_*.md` (este repositório) | 8 | Verdade conhecida do `review-design`: o número esperado de EXIGIDO é anotado antes de rodar |
| Ground truth | 15 perguntas de `.agents/skills/*/references/como-falar.md` e 7 fixtures de `sdd/fixtures/conversa/` | 22 | As 15 passam no `--sites` depois de marcadas; as fixtures que já reprovam no `skill-lint --conversa` continuam reprovando pelo mesmo motivo |
| Related code | `sdd/bin/skill-lint.py` (`perguntas()`), `verify-gate.sh` (`--print`), `gate-shell-evidencia.sh`, `report-lint.py` (leitura de `layers:`), `sdd/fixtures/BRAINSTORM_EXEMPLO.md`, `DEFINE_FIXTURE_CONTROLE.md`, `DEFINE_FIXTURE_NEEDS_CLARIFICATION.md` | 7 | Pontos de ligação; o `sdd-fluxo.sh` chama o gate, não o reescreve |

**How samples will be used:**
- Fixtures de `loop` em `sdd/fixtures/fluxo/` montadas a partir da forma dos ledgers e do DOGFOOD reais, com nomes genéricos (o publish-gate reprova caminho `/Users/…` e dado do privado).
- Os 8 DESIGNs servem de verdade conhecida do `review-design` (contagem anotada antes de rodar).
- As 15 perguntas de exemplo ganham marca e passam no `--sites`; 4 fixtures novas de pergunta (sem classe, com Outro, com jargão, com 2 recomendadas) reprovam pelo motivo certo.
- `BRAINSTORM_EXEMPLO.md` é a entrada da execução real da `sdd-define` com `flow.autonomous: true`.

## Approaches Explored

### Approach A: Porte por mecanismo, um ciclo, `.sh` com o núcleo em Python embutido — Recommended

**Description:** argumento, verbos e exits em bash 3.2; a lógica que lê JSON, ledger, manifest e config num `python3 -B - <<'PY'` dentro do mesmo arquivo, como o privado faz com `perl -e`. Três peças: `sdd-fluxo.sh` (`review-design`, `loop`, `despachar`, `seguir`, `--self-test`); `sdd-decisoes-lint.sh` (`--sites`, `--self-test`) importando o `perguntas()` do `skill-lint.py`; e o texto das skills (classes, subseção, recibo, F6/F8/F10/F11). Uma Release.

**Pros:**
- Nomes iguais aos do plano, do prompt e do critério de pronto; `tests/test_bash32.py` cobre os dois scripts.
- Um arquivo por script, como a fonte; nenhum parser de pergunta duplicado.
- Uma Release, um gate, uma revisão de contexto fresco.

**Cons:**
- Python dentro de heredoc é menos cômodo de testar por import (os testes chamam o script).
- `python3` passa a ser obrigatório para os dois scripts (sem ele, 64).

**Why Recommended:** fidelidade à fonte e ao plano com o piso do Open; a parte bash é pequena e o que pesa (JSON, tabelas) fica em Python stdlib.

### Approach B: Scripts Python puros

**Description:** `sdd/bin/sdd-fluxo.py` e `sdd/bin/sdd-decisoes-lint.py`.

**Pros:**
- Teste por import; um só verificador.

**Cons:**
- Foge dos nomes do plano e do prompt; `test_bash32` não os cobre.
- Ganha pouco: a parte bash é só o despacho de verbos.

### Approach C: Duas Releases (F9a scripts + classes; F9b texto das skills)

**Description:** primeiro os scripts e as marcas, depois a subseção, o recibo e F6/F8/F10/F11.

**Pros:**
- Revisões menores.

**Cons:**
- 2 gates de ~4 min, 2 revisões de contexto fresco e 2 OKs na mesma sessão; a F9b depende da F9a publicada.

## Selected Approach

| Attribute | Value |
|---|---|
| Chosen | Approach A |
| User Confirmation | 2026-10-31, "A — porte por mecanismo, um ciclo, .sh com o núcleo em Python embutido (recomendado)" |
| Reasoning | Nomes e piso do plano, um arquivo por script, uma Release |

## Key Decisions Made

| # | Decision | Rationale | Alternative Rejected |
|---|---|---|---|
| 1 | D1: `flow.autonomous: false` por default; ligado, a fase seguinte é chamada na mesma sessão quando o gate da anterior sai 0 e não há marcador; `--parar` desliga numa chamada | Política de decisão é escolha do Roberto (regra 8 do 8.0); quem já instalou não vê o comportamento mudar | Ligado por default; sem encadeamento |
| 2 | D11: slots `flow.autonomous: false` e `review.security_globs: ""` (em `review:`); os 8 termos genéricos fixos no script; `layers.sql` preenchida também conta como segurança | Regra 2 (slots) e regra 4 (específico da RDD não viaja); falso positivo só custa uma revisão | Slot sem termos fixos (projeto com login que não preencheu pula a revisão); só `flow.autonomous` |
| 3 | Marcas de classe: `[D1]` irreversível ou externo · `[D2]` produto, escopo ou texto para o usuário · `[D3]` política do pacote · `[D4]` teto estourado · `[D5]` impasse de evidência — perguntadas mesmo com o encadeamento ligado; **`[auto]`** — perguntada só com o encadeamento desligado; ligado, vale a recomendada e a decisão vai para o recibo. Uma marca por pergunta, antes do negrito | "Toda pergunta leva a classe" sem mudar o comportamento com o slot desligado; a tabela fica no item 9 do `PERGUNTA_DECISAO.md` (dono do formato), que mantém o `[Dn]` conferido pelo `test_conversa` | Só D1–D5 (as perguntas de hoje que não são D1–D5 sumiriam do formato); tabela no `FLUXO_ENCADEADO.md` |
| 4 | As 15 perguntas de exemplo dos `como-falar.md` ganham marca; as 15 skills sobem de versão | `check-versions` exige bump de toda skill tocada | Marcar só as 9 de fase (o `--sites .agents/skills` reprovaria as outras 6) |
| 5 | `sdd-decisoes-lint.sh --sites <pasta|arquivo…>` confere toda pergunta de decisão (parser do `skill-lint`): exatamente uma marca antes do negrito, 1 recomendada e primeira, "não sei", sem "Outro" e sem identificador técnico (AT-, LM-, SHA) fora do `(ref: …)` final; `--self-test` com 4 fixtures reprovadas e o controle aceito; exits 0/2/64 | "Jargão" genérico = regra 5 do `PERGUNTA_DECISAO.md`, sem denylist da RDD; reusa o parser em vez de duplicar | Denylist de jargão; procurar nome de ferramenta de pergunta (proibido pelo P2) |
| 6 | `sdd-fluxo.sh review-design <DESIGN>`: 0 EXIGIDO (≥ 3 arquivos novos, termo genérico, glob de `review.security_globs` ou de `layers.sql` no manifest) · 1 DISPENSAVEL · 64 manifest ilegível (quem chama roda a revisão e registra) | Porte da fonte com os slots | — |
| 7 | `sdd-fluxo.sh loop`: núcleo da fonte — review inválida (`reviewer_exit`/`auditor_exit` ≠ 0) → CONTINUAR; graves = HIGH dos revisores + NOVO HIGH do auditor; ledger lido por célula com `rodada=N`, só veredito de linha HIGH fecha grave; DISAGREE_EVIDENCE sem veredito no ledger → D5 impasse → BLOQUEADO; avaliador `NEEDS_WORK` conta no teto (2 ciclos), `PASS_PENDENTE_RECIBO` sem `--recibo` → 30; teto 3 → 20; META/jsonl ausente ou linha inválida → 64, nunca PRONTO por omissão | Nenhuma skill do Open chama o `loop` antes da F10; o núcleo fixa o contrato que a F10 vai produzir | Porte inteiro (2º revisor, desempate, lotes, `auditor_exit 75`) |
| 8 | `loop --log <arquivo>` grava a saída com o `[exit=N]` real; o `--self-test` prova que um log feito com `\| tee` reprova no `gate-shell-evidencia.sh` | O "`\| tee` proibido" do plano passa a ter dente | Só a regra em texto |
| 9 | `sdd-fluxo.sh despachar <papel> <brief>` (novo): copia o brief para `sdd/reports/briefs/<FEATURE>-<papel>-<AAAAMMDD-HHMMSS>.md`, imprime a parada ⏸️ com os rótulos do `PERGUNTA_DECISAO.md` (Por que parei · Onde · Passos · O que não foi feito · Brief · Sessão nova) e `RESULTADO: AGUARDANDO_HUMANO`, sai 40; chamado pela `sdd-build` 5d (avaliador) e pela revisão de contexto fresco da `sdd-design` quando o agente não abre papel fresco sozinho | O script não sabe se o agente tem subagente; o agente sabe. A F9 só liga o exit 40 ao formato que a F4 fixou | Detectar o vendor pelo `sdd/config.yaml` (um projeto pode usar vários) |
| 10 | `sdd-fluxo.sh seguir <artefato> <próxima>` (novo): lê `flow.autonomous`, roda `verify-gate.sh --print` e procura marcador aberto; 0 SEGUIR com a linha `✅ <FASE> pronto → seguindo para <próxima>`; 1 PARAR com o motivo (desligado, `--parar`, gate, marcador, próxima = release); 64 uso ou slot inválido | A decisão de encadear vira exit, não prosa (o porquê do script no privado); com o slot desligado a skill mostra o Próximo passo de hoje | Deixar o agente ler o config e decidir |
| 11 | Quem encadeia: define → governança/ux-review/design (a skill escolhe a próxima); governança → ux-review/design; ux-review → design; design → revisão de contexto fresco (EXIGIDO) ou build (DISPENSAVEL); build **nunca** → release (D1). Não encadeiam: brainstorm (pré-linha, sem gate), iterate (volta à fase do documento), new-session (a próxima fase roda em outra pasta: troca de janela, não decisão), release | Ordem do privado sem a parada "espelho" (da RDD) | Brainstorm encadeando para a define |
| 12 | Recibo "Decidi sozinho" (`<decisão> · sinal: <…> · reverter: <…>`, omitido se vazio) no resumo de etapa e nas linhas `[auto]` do DESIGN; fora do `BUILD_REPORT` | `report-lint` é fail-closed: seção nova no template pede regra nova | Recibo também no `BUILD_REPORT` |
| 13 | F6 (`sdd-design`): flag LLM ausente vira `true` (conservador) em vez de pergunta; re-check com hits decide; proposta de verificabilidade aceita sem pergunta; cada uma registrada como `[auto]` no DESIGN | PORTE §5.3 F6 | Perguntar (hoje) |
| 14 | F8 (`sdd-define` passo 7): 1 sinal forte → `true`; 2 fracos → `true`; 1 fraco → `true` conservador com nota; sinais de loop → "candidato a loop" | PORTE §5.3 F8 | Flag binária sem pontuação (hoje) |
| 15 | F10 (`sdd-brainstorm` passo 1): tabela "como tratar cada tipo de entrada" — ideia vaga → "conte mais"; feature → questionar a necessidade; comparação → o que se ganha e o que se perde | PORTE §5.3 F10 | — |
| 16 | F11 (`sdd-ux-review` passo 1): ler os `UX_REVIEW_*.md` anteriores | PORTE §5.3 F11 | — |
| 17 | Provas: testes `tests/test_fluxo.py` e `tests/test_decisoes_lint.py` com fixtures dos dois lados; `seguir` com `flow.autonomous: true` sobre DEFINE de fixture num repositório temporário; bloco comum idêntico nas 9 conferido por teste; `sdd-decisoes-lint.sh --sites .agents/skills` como passo do `publish-gate.sh`; 2 execuções reais do `codex exec` numa cópia temporária (a `sdd-define` sobre `BRAINSTORM_EXEMPLO.md` com o slot ligado termina na linha de transição; a `sdd-build` 5d sem subagente termina com `[exit=40]` e o brief gravado), com o log mostrando que a skill lida é a da cópia | Contrato no CI; comportamento do agente na execução real (P2) | Só fixture; só execução real |
| 18 | Falhas sempre para o lado seguro: config ausente = `false`; valor fora de `true`/`false` → 64 e a skill trata como desligado com aviso; sem `python3` → 64 | Encadeamento nunca liga por engano | Falhar aberto |
| 19 | Versão `v2.2.10` automática | Ninguém vê o comportamento mudar sem ligar o slot | `v2.3.0` por tag; decidir no bloco do OK |
| 20 | Abordagem A | Ver Selected Approach | B (Python puro); C (duas Releases) |

## Features Removed (YAGNI)

| Feature Suggested | Reason Removed/Deferred | Can Add Later? |
|---|---|---|
| Campos do 2º revisor no `loop` (`revisor2_*`, dispensa D3, retomada), desempate (`desempate_*`), revisor raso, rodadas em lote (`5a`), `auditor_exit 75` | Nenhuma skill do Open chama o `loop` antes da F10, que define o `META.txt` (R5, R6, R8) | Yes (F10) |
| `sdd-decisoes-lint.sh --curadoria` | Bloco `<<<CURADORIA>>>` é da F14 | Yes (F14) |
| Denylist de jargão da RDD | Específico da RDD (regra 4); o Open usa a regra 5 do `PERGUNTA_DECISAO.md` | No |
| Parada "espelho → worktree" antes do build | Específico da RDD (`ESPELHO`, branch `dev`); o pre-commit H6 da F8 já recusa commit na branch padrão | No |
| Recibo "Decidi sozinho" no `BUILD_REPORT` | `report-lint` fail-closed: seção nova pede regra e fixture | Yes |
| `sdd-build` passo 0 chamando `review-design` | R13 da F10: a F9 entrega o verbo, a F10 liga a chamada | Yes (F10) |
| Verbo para retomar depois do exit 40 | A skill retoma quando a pessoa cola a linha `VEREDITO: …` (formato da F4) | Yes |
| Detecção automática de subagente pelo script | O agente sabe o que pode; o script não tem como saber | No |

## Incremental Validations

| Section | Presented | User Feedback | Adjusted? |
|---|---|---|---|
| Checkpoint 1: peças (`sdd-fluxo.sh` com `review-design`, `loop`, `despachar`, `seguir`, `--self-test` e `--log`; `sdd-decisoes-lint.sh`; marcas `[D1]`…`[D5]` e `[auto]` nas 15 perguntas; `FLUXO_ENCADEADO.md`, subseção nas 9, `despachar` na build 5d e na revisão do design, F6/F8/F10/F11) e cortes (2º revisor e afins para a F10, `--curadoria` para a F14, espelho e denylist não viajam, recibo fora do `BUILD_REPORT`) | Yes | "sim" | No |
| Checkpoint 2: comportamento com o slot desligado (a skill roda `seguir`, que sai 1, e mostra o Próximo passo de hoje) e ligado (`[auto]` → recomendada + recibo; `seguir` 0 → linha de transição e próxima fase), linha de cada skill, falhas para o lado seguro, provas (testes, `publish-gate`, 2 execuções do `codex exec`) | Yes | "grave o brainstorm, depois execute o define, ux-review, design, review do design, build, review do build" | No |

## Suggested Requirements for /define

### Problem Statement (Draft)

O sdd-open para no fim de cada fase e pergunta tudo, sem distinguir o que é decisão da pessoa (publicar, mudar o produto, mudar a política) do que a recomendação resolve; não tem como encadear as fases quando o gate da anterior está verde; decide por leitura de prosa se um DESIGN precisa de revisão e se o loop de review convergiu; e, num agente sem subagente (Codex CLI, Gemini CLI, Cursor), o despacho de um papel fresco não tem uma parada com código de saída — o que impede o fluxo do privado de rodar no Open (P4) e o padrão agnóstico de ser provado (P2).

### Target Users (Draft)

| User | Pain Point |
|---|---|
| Aluno do Bravo (contador) que roda as skills de fase | Responde a perguntas que a recomendação resolveria; não sabe quais são decisões dele de verdade |
| Quem liga `flow.autonomous` (Roberto, F15) | Precisa que o fluxo siga sozinho com gate verde e só pare em D1–D5, com recibo do que foi decidido |
| Quem usa Codex CLI, Gemini CLI ou Cursor | O avaliador fresco exige uma sessão nova; hoje a parada é só texto, sem exit nem brief gravado |

### Success Criteria (Draft)

- [ ] `bash sdd/bin/sdd-decisoes-lint.sh --sites .agents/skills` sai 0 e `--self-test` sai 0, com as 4 fixtures (sem classe, com Outro, com jargão, com 2 recomendadas) reprovadas pelo motivo certo e o controle aceito.
- [ ] `bash sdd/bin/sdd-fluxo.sh --self-test` sai 0, com um cenário por exit (0/10/20/30/40/64) e um que prova que um log feito com `| tee` reprova no `gate-shell-evidencia.sh`.
- [ ] `review-design` sobre os 8 DESIGNs F1–F8 dá a contagem de EXIGIDO anotada antes de rodar; manifest ilegível sai 64.
- [ ] Com `flow.autonomous: true`, `seguir` sobre o DEFINE de fixture sai 0 com `✅ DEFINE pronto → seguindo para …`; com `false`, ausente, `--parar`, gate ≠ 0, marcador aberto ou próxima = release, sai 1 com o motivo; valor inválido sai 64.
- [ ] No `codex exec`, a `sdd-define` sobre `sdd/fixtures/BRAINSTORM_EXEMPLO.md` com o slot ligado termina com `✅ DEFINE pronto → seguindo para …`, e a `sdd-build` 5d sem subagente termina com `[exit=40]` e o brief em `sdd/reports/briefs/`.
- [ ] As 15 perguntas de exemplo têm marca; a subseção `### Fluxo encadeado` está nas 9 skills, com o bloco comum idêntico; os itens F6, F8, F10 e F11 estão nas 4 skills; toda skill tocada sobe de versão (`check-versions --base v2.2.9 --base-obrigatoria`).
- [ ] Todo script novo passa em `grep -nE 'mapfile|declare -A|\$\{[a-zA-Z_]+\^\^'` sem achado; 1 sabotagem por script novo ou alterado; `skill-lint --conversa` 17/17; `test_agnostico` verde.
- [ ] Verify Gate `--strict` 0; revisão de contexto fresco sem HIGH aberto; Release `v2.2.10` com `SHA256SUMS.txt` conferido por `shasum -a 256 -c`.

### Constraints Identified

- bash 3.2 + Python stdlib (`python3 -B`); nada de `mapfile`, `declare -A`, `${x^^}`; nome da variável entre chaves antes de emoji; `rm -rf` só com `"${X:?}"`.
- P2: o texto fala em "papel fresco" e "sessão nova", nunca no nome da ferramenta de um agente, em `.agents/skills/`, `sdd/templates/`, `sdd/hooks/`, `AGENTS.md.tmpl` e `sdd/playbook.md`.
- `verify-gate.sh` (6 exits, fixtures, saída com e sem trace) intacto — o `sdd-fluxo.sh` o chama; `report-lint` fail-closed; hooks da F8; bloco do OK da `sdd-release`; camada de conversa (bloco comum em 15 `SKILL.md`, seção nas 17, `FRASES` do `test_conversa`); "Por que cada regra existe" logo antes do Encerramento.
- `PERGUNTA_DECISAO.md`: itens 1–8 e o formato ⏸️ ficam; as fixtures de `sdd/fixtures/conversa/` que já reprovam no `skill-lint --conversa` continuam reprovando pelo mesmo motivo.
- Publish-gate: nenhuma fixture com `/Users/<nome>/`, e-mail fora de `example.*`, CPF, CNPJ, telefone ou 11+ dígitos seguidos; dado do privado reescrito.
- Todo arquivo novo no `MANIFEST.txt` (`LC_ALL=C`); `git add` por nome; `sdd/features|handoffs|reports|reviews|traces/` fora dos commits; os testes não carregam skill de fora do pacote (`HOME` falso do `tests/apoio.py`).

### Out of Scope (Confirmed)

- Os itens da tabela YAGNI acima.
- Revisão adversarial, registry, adapters por engine e 2º revisor (F10/F11); `RESUMO_ETAPA.md` com `/adversarial-review` (F10).
- Cartógrafo, curator, `/drive` e `drive.*` (F12–F14).
- Regenerar o sdd-starter; alterar o sdd-starter ou o repositório privado.

## Session Summary

| Metric | Value |
|---|---:|
| Questions Asked | 6 |
| Approaches Explored | 3 |
| Features Removed (YAGNI) | 8 |
| Validations Completed | 2 |

## Next Step

Execute o **SDD Define by RDD**.
