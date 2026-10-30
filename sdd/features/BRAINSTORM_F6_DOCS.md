# BRAINSTORM: F6 Docs

> Exploratory session to clarify intent and approach before requirements capture

## Metadata

| Attribute | Value |
|---|---|
| Feature | F6_DOCS |
| Date | 2026-10-29 |
| Author | brainstorm-agent |
| Status | Handoff Ready |

## Initial Idea

**Raw Input:** "Brainstorm da F6 com a `sdd-brainstorm`, gravando `sdd/features/BRAINSTORM_F6_DOCS.md` a partir da seção 4.3 do plano." Escopo do prompt da sessão 4: quickstart com "valide antes de seguir" (`docs/quickstart.md` e `docs/pt-BR/quickstart.md`) e a tabela "onde roda → ferramenta"; guia do aluno adaptado ao open a partir de `sdd-starter/docs/guia-do-aluno.pt-BR.md`; "Por que cada regra existe" nas skills de fase; README e `AGENTS.md.tmpl` citando as 3 skills da F2, a `sdd-kb` e o `kb-dominios.py` da F5 e o bloco do OK da F3; item I (`docs/roadmap.md` com W1–W5 como planejadas); item K (docs de mecanismo) fora.

**Context Gathered:**
- Fato (conferido): worktree `feat/f6-docs` em `7e19462` = `origin/main` = tag `v2.2.6`; 17 skills; 499 testes no piso.
- Fato (conferido): "Por que cada regra existe" já existe em 2 skills do open, vindas da F2 — `sdd-new-session` (`## Por que cada regra existe`, 9 itens) e `sdd-iniciar-repo` (`## Por que cada regra existe (não apague sem ler)`). Nenhuma das 7 skills de fase (brainstorm, define, governanca, ux-review, design, build, release) a tem. A `sdd-release` do starter tem 10 itens portáveis.
- Fato (conferido): o guia do starter (494 linhas, não rastreado) assume `npx skills add`, 15 skills, 2 agentes (Claude Code e Codex), `ux-review-builder` e "a pasta `sdd/` não vai para o GitHub" — esta última é falsa no open, onde `sdd/config.yaml`, `sdd/playbook.md` e as specs são versionados. Exemplos fictícios ("Honorarios"), sem CPF, telefone ou caminho `/Users/`.
- Fato (conferido): o quickstart do starter traz a "regra do método" (nunca siga com documento não lido), um "Valide antes de seguir" por fase e a tabela "Você quer… → Escreva no prompt → No Build, use", que cita Lovable e só 2 agentes.
- Fato (conferido): `docs/pt-BR/comparison.md:46` declara "Specs como deltas" *(em avaliação)* e `:45` a reconciliação spec ↔ código *(planejado)*; `:59-60` diz "Isso está no roadmap aqui".
- Fato (conferido): `scripts/publish-gate.sh` G5 tem lista fixa de docs obrigatórios (os 4 pares atuais); `docs/cli-conventions.md` existe só em português e o README em inglês o aponta com "(PT)".
- Fato (conferido): `scripts/next-version.sh` publica `latest + 1 patch` no push de `main`; uma tag `vX.Y.Z` no mesmo commit vira a única Release.
- Inferência: o guia e as skills vão divergir com o tempo; nenhum teste pega texto velho, só caminho quebrado.

**Technical Context Observed (for Define):**

| Aspect | Observation | Implication |
|---|---|---|
| Likely Location | `docs/pt-BR/guia-do-aluno.md`, `docs/roadmap.md`, `docs/pt-BR/roadmap.md`, `docs/quickstart.md`, `docs/pt-BR/quickstart.md`, `README.md`, `README.pt-BR.md`, `AGENTS.md.tmpl`, 7 `.agents/skills/sdd-*/SKILL.md`, `tests/test_docs.py`, `MANIFEST.txt` | 7 skills + `AGENTS.md.tmpl` disparam a Release; `docs/`, README e `tests/` não |
| Relevant KB Domains | N/A (o open não tem `sdd/kb/` próprio) | `KB Domains = nenhum` no DEFINE |
| IaC Patterns | N/A | CI existente (`publish-gate.yml` + `testes-macos`) sem mudança |

## Discovery Questions & Answers

| # | Question | Answer | Impact |
|---|---|---|---|
| 1 | Em que idioma saem o guia do aluno e o `docs/roadmap.md`? | **Guia só em português, roadmap em inglês e português** (recomendada), contra "os dois em EN e PT" e "os dois só em PT" | `docs/pt-BR/guia-do-aluno.md` sem par em inglês (o README EN aponta "(PT)"); `docs/roadmap.md` + `docs/pt-BR/roadmap.md` com o cabeçalho de idioma dos outros pares |
| 2 | Quais skills recebem "Por que cada regra existe"? | **As 7 de fase** (recomendada): brainstorm, define, governanca, ux-review, design, build, release — contra "só define, design, build e release" e "só a release" | 7 bumps de patch; teste exige a seção nas 7 + nas 2 que já a têm (`sdd-new-session`, `sdd-iniciar-repo`), aceitando os 2 títulos atuais |
| 3 | Qual versão a F6 publica? | **`v2.2.7`, automática** (recomendada), contra "`v2.3.0` com tag à mão" e "decidir no bloco do OK" | Nenhuma tag manual; o push fast-forward em `main` calcula o patch |

## Sample Data Inventory

| Type | Location | Count | Notes |
|---|---|---:|---|
| Input files | `sdd-starter/docs/guia-do-aluno.pt-BR.md`, `sdd-starter/docs/quickstart.pt-BR.md` | 2 | Molde do guia e da regra "valide antes de seguir" + tabela "onde roda" |
| Output examples | `.agents/skills/sdd-new-session/SKILL.md` e `sdd-iniciar-repo/SKILL.md` (seção já portada); `sdd-starter/skills/sdd-release/SKILL.md` (10 itens) | 3 | Formato `- **regra** — motivo` |
| Ground truth | `docs/comparison.md` / `docs/pt-BR/comparison.md` (tom "planejado"/"em avaliação"); plano, seção 8 (F7–F14) | 2 | Conteúdo e status do roadmap |
| Related code | `sdd/reports/evidence/F5_CONHECIMENTO/comandos-intactos.py`, `sabotagem.sh`, `gerar-evidencia.sh` | 3 | Molde da prova de passos intactos e da sabotagem |

**How samples will be used:**
- O guia do starter é adaptado bloco a bloco (mesmos 10 blocos), corrigindo instalação, contagem, agentes, `ux-review-builder` → `sdd-ux-review` e o versionamento de `sdd/`.
- A seção da `sdd-release` do starter é adaptada ao open (bloco do OK, `deploy-espera-testes.py`, ledger); as outras 6 seções seguem o formato das 2 que o open já tem.
- O roadmap copia o status literal do `comparison.md` para não prometer o que está em avaliação.
- Nenhuma outra amostra: o Roberto respondeu "nenhuma".

## Approaches Explored

### Approach A: Adaptação escrita à mão, uma Release só — Recommended

**Description:** guia, quickstart, roadmap, README, `AGENTS.md.tmpl` e as 7 seções escritos à mão num único ciclo SDD, com `tests/test_docs.py` (links relativos, âncoras do sumário, seção nas 9 skills, status do `comparison.md`) e Release automática `v2.2.7`.

**Pros:**
- Um ciclo, um gate, uma revisão de contexto fresco, uma Release.
- Texto escrito para o aluno, não derivado de `description` escrita para o agente.
- Nenhum mecanismo novo para manter.

**Cons:**
- O guia pode ficar velho quando uma skill mudar; o teste só pega link quebrado.

**Why Recommended:** a F6 é documentação; o custo de mecanismo (B) ou de dois ciclos (C) é maior que o risco de texto velho, que fica registrado.

### Approach B: Catálogo do guia gerado das skills

**Description:** um script monta as fichas do catálogo a partir do frontmatter de cada `SKILL.md`; um teste reprova guia desatualizado.

**Pros:**
- O catálogo não envelhece.

**Cons:**
- Script novo, com teste e sabotagem próprios, para manter.
- As `description` foram escritas para o agente; o texto para o aluno piora.

### Approach C: Dois ciclos

**Description:** primeiro skills e `AGENTS.md.tmpl` (Release `v2.2.7`), depois os docs (push sem Release).

**Pros:**
- PRs menores.

**Cons:**
- Gate, CI macOS e revisão de contexto fresco duas vezes; um ciclo consome uma sessão (medida da F3).

## Selected Approach

| Attribute | Value |
|---|---|
| Chosen | Approach A |
| User Confirmation | 2026-10-29, "A — adaptação escrita à mão, uma Release só (recomendado)." |
| Reasoning | Menor custo para uma frente de documentação; o risco de texto velho é aceito e registrado |

## Key Decisions Made

| # | Decision | Rationale | Alternative Rejected |
|---|---|---|---|
| 1 | Guia só em português (`docs/pt-BR/guia-do-aluno.md`); roadmap em EN e PT | O público do guia é quem nunca usou git, no Brasil; o roadmap segue o par dos docs que o README EN cita | Guia também em inglês (dobra ~450 linhas e cada mudança de skill); tudo só em PT |
| 2 | "Por que cada regra existe" nas 7 skills de fase, com título `## Por que cada regra existe` | Todas têm regras que parecem burocracia e seriam cortadas numa "limpeza" | Só define/design/build/release; só release |
| 3 | O teste aceita os 2 títulos atuais (`## Por que cada regra existe` e `… (não apague sem ler)`) | Igualar o título custaria 2 bumps sem ganho | Igualar os títulos de `sdd-new-session` e `sdd-iniciar-repo` |
| 4 | Release `v2.2.7` automática | Sem comportamento novo; patch é o que o fluxo calcula | `v2.3.0` por tag à mão; decidir no bloco do OK |
| 5 | Abordagem A (à mão, um ciclo) | Ver Selected Approach | B (catálogo gerado); C (dois ciclos) |
| 6 | Tabela "onde a solução vai rodar → o que escrever no Design" sem a linha Lovable, com o build em qualquer um dos 7 agentes | No open o build precisa do Verify Gate num terminal; P2 pede os 7 agentes por igual | Copiar a tabela do starter (Lovable, 2 agentes) |
| 7 | Roadmap com os 5 temas de W1–W5 como *planejado*, "Specs como deltas" como *em avaliação* e reconciliação spec ↔ código como *planejado*, sem datas | Mesmo status literal do `comparison.md` (critério 6 da Ficha) | Roadmap com datas ou numeração interna F7–F14 |
| 8 | Skills tocadas sobem de **patch** (ex.: `sdd-build` 2.2.1, `sdd-release` 2.3.1) | Seção de texto, sem passo novo | Minor |

## Features Removed (YAGNI)

| Feature Suggested | Reason Removed/Deferred | Can Add Later? |
|---|---|---|
| Guia do aluno em inglês | Decisão 1 | Yes |
| Catálogo do guia gerado das skills | Abordagem B rejeitada | Yes |
| Porte do `workflow.md` do starter | O fluxo do README e o mapa do guia já cobrem | Yes |
| Linha Lovable na tabela "onde roda" | O build do open precisa do gate num terminal | No |
| Checagem de links externos (http) | Exige rede; os testes rodam sem rede | Yes |
| Igualar os títulos da seção em `sdd-new-session` e `sdd-iniciar-repo` | 2 bumps sem ganho | Yes |
| Docs novos na lista G5 do `publish-gate.sh` | O `test_docs.py` já abre cada link do README | Yes |
| "Por que cada regra existe" em iterate, handoff, playbook, prompt-builder, auditoria-harness, kb, checar-ambiente, higiene-dado | Decisão 2 limita às de fase | Yes |
| `docs/hooks.md`, `docs/review-contract.md`, `docs/decisoes-D1-D5.md` (item K) | Nascem na W1, W3 e W2 (F7/F8, F10, F9) | Yes |
| Conferência do guia e das seções num agente real | Pendência já aberta (A-002 da F4, F5) | Yes |

## Incremental Validations

| Section | Presented | User Feedback | Adjusted? |
|---|---|---|---|
| Checkpoint 1: os 8 componentes (guia, quickstart EN/PT, roadmap EN/PT, README EN/PT, `AGENTS.md.tmpl`, 7 seções, `test_docs.py`, `MANIFEST.txt`) e os 10 cortes YAGNI | Yes | "confere" | No |
| Checkpoint 2: como cada parte se prova (gate, `skill-lint --conversa`, `wc -l` ≤ 500, `check-versions`, `comandos-intactos`, `test_docs`, publish-gate, `test_agnostico`, 3 sabotagens, revisão de contexto fresco), falhas (âncora com acento, bloco do `AGENTS.md` maior, seção no lugar errado, guia velho, `MANIFEST.txt`) e contratos intactos | Yes | "confere" | No |

## Suggested Requirements for /define

### Problem Statement (Draft)

O sdd-open não tem um caminho para quem nunca usou git nem terminal (guia do aluno), não diz ao aluno para validar cada documento antes da fase seguinte, não registra dentro das skills de fase por que cada regra existe, e o README e o `AGENTS.md.tmpl` não citam as skills de terreno (F2), a `sdd-kb` e o `kb-dominios.py` (F5) nem o bloco do OK (F3); também falta um roadmap público do que está planejado (W1–W5).

### Target Users (Draft)

| User | Pain Point |
|---|---|
| Aluno que nunca usou git nem terminal (contador, analista) | Não sabe por onde começar, em que ordem usar as 17 skills, nem o que fazer quando algo para |
| Quem instala o open num projeto (lê README/quickstart) | Não vê as skills de terreno, a KB nem o bloco do OK; não tem a regra "valide antes de seguir" |
| Agente que lê `AGENTS.md` no projeto do usuário | Lista só as fases; não sabe das skills de preparo nem da `sdd-kb` |
| Mantenedor (ou agente) que edita uma skill de fase | Corta uma regra que parece burocracia sem saber o motivo |

### Success Criteria (Draft)

- [ ] `docs/pt-BR/guia-do-aluno.md` existe, com os 10 blocos, as 17 skills no mapa e no catálogo, e nenhuma das 4 premissas falsas do starter (`npx skills add`, 15 skills, 2 agentes, `sdd/` fora do git).
- [ ] Quickstart EN e PT têm "valide antes de seguir" em cada fase e a tabela "onde roda" com os 7 agentes por igual, sem Lovable.
- [ ] `docs/roadmap.md` e `docs/pt-BR/roadmap.md` listam os 5 temas como planejados, "Specs como deltas" como em avaliação, sem datas; `comparison.md` continua com "Specs como deltas" em avaliação.
- [ ] README EN e PT citam as 17 skills em 4 blocos, o bloco do OK e linkam guia e roadmap; `AGENTS.md.tmpl` cita as 4 de preparo, a `sdd-kb`, o `kb-dominios.py` e a regra do OK, e `tests/test_agnostico.py` passa.
- [ ] As 7 skills de fase têm `## Por que cada regra existe` com ≥ 3 itens, `wc -l` ≤ 500, versão em patch e passos idênticos aos da `v2.2.6` (prova por `comandos-intactos`).
- [ ] `tests/test_docs.py` verde (todo link relativo e âncora do sumário abre; 9 skills com a seção) e vermelho em 3 sabotagens.
- [ ] Verify Gate `--strict` 0; `skill-lint --conversa` 17/17; `check-versions --base v2.2.6 --base-obrigatoria` VERDE; 499 testes anteriores intactos.
- [ ] Release `v2.2.7` com `SHA256SUMS.txt` conferido por `shasum -a 256 -c`.

### Constraints Identified

- P2: nenhum nome de ferramenta de um agente só em `AGENTS.md.tmpl` ou nas skills; os docs tratam os 7 agentes por igual.
- Publish-gate: nos docs, nenhum `/Users/<nome>/`, e-mail fora de `example.com/.org/.net`, CPF, CNPJ, telefone ou 11+ dígitos.
- CI "Skill integrity": nenhum caractere invisível nem `curl … | sh` literal em `.agents/skills/`.
- Camada de conversa (F4/F5) intacta: bloco comum nas 15 skills e `FRASES` do `test_conversa`; linha de identificação com a versão do frontmatter.
- Contratos de `sdd/` intactos (6 exits do gate, fixtures, `playbook-lint --self-test`, lints 0/1/64, bloco do OK da release, passo 4 da `sdd-iterate`).
- Todo arquivo novo no `MANIFEST.txt` em ordem `LC_ALL=C`; `git add` por nome; `sdd/features|handoffs|reports|reviews/` fora dos commits da branch de trabalho.
- Piso Python 3.9 / bash 3.2; testes sem rede.

### Out of Scope (Confirmed)

- Os itens da tabela YAGNI acima.
- A tabela WCAG e a leitura de `UX_REVIEW_*.md` anteriores (W5); o encadeamento entre fases e as classes D1–D5 (F9); o fail-open do `report-lint.py` (F7).
- Regenerar o sdd-starter a partir do open; alterar o sdd-starter ou o repositório privado.

## Session Summary

| Metric | Value |
|---|---:|
| Questions Asked | 4 |
| Approaches Explored | 3 |
| Features Removed (YAGNI) | 10 |
| Validations Completed | 2 |

## Next Step

Execute o **SDD Define by RDD**.
