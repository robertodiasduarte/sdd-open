# BRAINSTORM: F17b Starter gerado, etapa 2

> Sessão de exploração antes do Define. Frente F17b do programa INCORPORAR_STARTER (Decisão 5, parâmetro P3);
> continua a F17 (`v2.13.0`, starter `v1.5.17`), caminho 1 em 2 etapas.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | F17B_STARTER_ETAPA2 |
| **Date** | 2026-11-13 |
| **Author** | brainstorm-agent (Claude), decisões do Roberto |
| **Status** | Ready for Define |

---

## Initial Idea

**Raw Input:** "Brainstorm com as decisões abertas: o modo web (sem terminal, entregar o documento no chat sem fingir
que gravou; fato × inferência; pendências 🐛/✨; prova por script só quando há gate) em brainstorm, handoff e
governança no Open, para elas entrarem na lista do gerador; o destino de define, design, build, release e
ux-review-builder (modo sem script dentro do Open, ou sair do starter, com os zips da v1.5.17 ainda baixáveis); se
docs/ e exemplos/ do starter passam a ser gerados. Meta do Roberto: manutenção num repositório só; o starter simples
para o aluno iniciante." Durante o brainstorm o Roberto acrescentou: **"o importante é garantir que o modus operandi
para o aluno iniciante, ao usar o sdd-starter, continue simples e sem restrições complexas"**.

**Context Gathered:**
- Open em `v2.13.0` + passo 0 desta frente (`ce281d7`: LM-022 a LM-024 e os 7 pendentes da revisão da F17;
  2.098 testes verdes). Starter em `v1.5.17` (`d2f3085`): 10 skills geradas, 8 congeladas.
- **Downloads por zip, somados nas 25 Releases do starter** (`gh api …/releases`, medido em 2026-11-13; inclui
  robôs, vale como proporção): kb 507 · brainstorm 276 · build 273 · design 265 · define 262 · handoff 248 ·
  ux-review-builder 117 · auditoria-harness 114 · prompt-builder 68 · governança 60 · **release 23** · new-session 22 ·
  checar-ambiente 22 · higiene-dado 21 · iniciar-repo 9. As 5 de fase são baixadas juntas, ~30 por onda de alunos
  (v1.0.0, v1.1.1, v1.4.0, v1.5.8, v1.5.15); a release, 1 a 3 por Release.
- **Fato (Roberto):** no módulo 7 do RDD10+ v8 o aluno aprende a `sdd-new-session` e a release, com **GitHub +
  Vercel**. **Inferência:** esse aluno instala por `npx skills add` (que lê a branch, sem contar download), por isso a
  release tem poucos downloads de zip apesar de ser ensinada.
- Citações a arquivo do `init` nas skills do Open (`sdd/bin|templates|hooks|review|patterns`, playbook, invariants,
  contracts): brainstorm 9 · handoff 5 · governança 10 · define 38 · design 24 · build 44 · **release 73** (o
  `SKILL.md` dela está no teto de 500 linhas do teste).
- A release congelada do starter (`v1.5.17`, 355 linhas, só git e `gh`) confere o deploy pelo **run do workflow**
  (`gh run list`). **Inferência (documentação pública, não medida):** com a integração GitHub–Vercel o deploy não é
  um workflow do Actions; aparece como status/check do commit e como deployment, com preview por PR.
- A `ux-review-builder` só existe no starter (1.4.0, 268 linhas, sem script); nada no Open a cita. O Open tem a
  `sdd-ux-review` (gate de UX por feature, 12 citações ao `init`), de outra função.
- Comparação item a item da F17 (`evidence/F17_STARTER_GERADO/COMPARACAO-fases-e-apoio.md`) já mapeou o que o
  starter tem melhor em brainstorm, handoff e governança (classe C).
- No clone local do starter (`/Users/robertoduarte/rdd-public/sdd-starter`) há `docs/guia-do-aluno.pt-BR.md` fora do
  git: trabalho do Roberto, não tocado.

**Technical Context Observed (for Define):**

| Aspect | Observation | Implication |
|--------|-------------|-------------|
| Likely Location | `.agents/skills/sdd-{brainstorm,handoff,governanca,release}/`, `.agents/skills/ux-review-builder/` (nova), `scripts/gerar-starter.py`, `scripts/starter/{lista.txt,openai.tsv,trocas/,raiz/}` | o gerador ganha a regra "skill de modo"; `raiz/` ganha `docs/`, `exemplos/`, `tests/` |
| Relevant KB Domains | nenhum | — |
| IaC Patterns | N/A | — |

---

## Discovery Questions & Answers

| # | Question | Answer | Impact |
|---|----------|--------|--------|
| 1 | Destino de define, design e build (as mais baixadas, ~30 por onda; 38/24/44 citações ao `init`) | **Modo web no Open** | elas serão geradas; pela decisão 6, na F17c |
| 2 | Destino da release (23 downloads; 73 citações; módulo 7 com GitHub + Vercel) | **Modo iniciante dentro da `sdd-release`**, em `references/`, de onde o gerador monta a release do starter | mantém o nome `/sdd-release` da aula; o `SKILL.md` do Open ganha só 1–2 linhas |
| 3 | Destino da `ux-review-builder` (só no starter, 117 downloads) | **Trazer para o Open** como 22ª skill, gerada; a `sdd-ux-review` lê o `UX_STANDARD.md` quando existir | contagens fixadas (21 skills) mudam |
| 4 | `docs/`, `exemplos/` e `tests/` do starter | **Mudar para o Open** (`scripts/starter/raiz/`), atualizados; a trava protege | um guia novo do starter passa a ser escrito no Open |
| 5 | Como o modo sem terminal mora no Open | **Por peso**: leves (brainstorm, handoff, governança) com o caminho no próprio texto; pesada (release) com `references/MODO_INICIANTE.md` + 1 linha no `SKILL.md` | ver Selected Approach |
| 6 | Tamanho da frente | **Duas frentes**: F17b agora; define, design e build na **F17c** | starter fica com 3 congeladas até a F17c |
| 7 | (Roberto, sem pergunta) o modo de trabalhar do iniciante continua simples? | **Simplicidade vira critério de aceite medido** (tabela de paradas, teste do iniciante, release com 1 OK) | ver Success Criteria |

---

## Perfil de risco

| Pergunta | Resposta |
|---|---|
| Quem pode ver? | qualquer um: Open e starter são públicos; o gerador roda sem rede na máquina do Roberto; nada da RDD entra (nomes de aluno, caminhos do Wordpress, chaves, código do privado, texto do e-book de segurança) |
| Quem pode mudar? | só o Roberto: no Open com "sdd-open autorizado"; no starter, OK próprio para cada push, PR e Release |
| Quanto alguém pode pedir? | nada no Open nem no starter (sem serviço, login, upload ou chamada paga). A release iniciante manda o aluno publicar na Vercel com a conta dele: a skill **nunca pede, lê ou grava token** da Vercel ou do GitHub; usa só o login que o `gh` e o git já têm |

---

## Sample Data Inventory

| Type | Location | Count | Notes |
|------|----------|-------|-------|
| Output examples | `exemplos/baixar-nfse/` do starter `v1.5.17` | 5 arquivos | documentos de uma feature feita na web |
| Input files | skills congeladas do starter `v1.5.17` (brainstorm, handoff, governança, release, ux-review-builder) | 5 | o "modo de trabalhar" de hoje do iniciante: base da tabela de paradas |
| Ground truth | `COMPARACAO-fases-e-apoio.md` (F17) | 1 | itens C de brainstorm, handoff e governança |
| Related code | `scripts/gerar-starter.py`, `scripts/starter/raiz/`, `check-gerado.py` | — | a 2ª geração usa o mesmo caminho |

Amostra do módulo 7 ou repositório ligado à Vercel: **nenhuma** (resposta do Roberto). O comportamento do deploy da
Vercel no GitHub fica marcado como inferência até ser medido.

---

## Approaches Explored

### Abordagem A1: modo sem terminal por peso da skill ⭐ Recomendada (escolhida)

**Description:** skill leve recebe as frases do caminho sem terminal no próprio texto do Open (vale para quem usa o
Open sem o `init` também) e é gerada como as 10 da F17; skill pesada recebe `references/MODO_INICIANTE.md` com o
caminho curto e uma linha no `SKILL.md` do Open ("projeto sem `sdd/bin/`? siga …"); o gerador monta o `SKILL.md` do
starter dessa skill só a partir do arquivo de modo (regra nova "skill de modo"), levando só os arquivos que ele cita.

**Pros:** um lugar só para editar; o `SKILL.md` da release não passa de 500 linhas; quem usa o Open sem o `init` cai
no mesmo caminho curto; o texto do Open não carrega instrução do starter.

**Cons:** skill pesada com dois procedimentos na mesma pasta (custo da decisão 1).

### Abordagem A2: trocas exatas grandes

**Cons:** 73 trocas só na release; cada mudança no Open quebra a geração.

### Abordagem A3: blocos marcados no mesmo `SKILL.md`

**Cons:** rejeitada na F17: o agente que usa o Open lê os dois caminhos e se confunde.

### Escopo

- **B1, duas frentes (escolhido):** F17b = brainstorm, handoff, governança, release iniciante, ux-review-builder,
  `docs/`/`exemplos/`/`tests/`; F17c = define, design, build (modo web, com comparação item a item de cada uma).
- B2, tudo na F17b: várias sessões e uma revisão enorme.
- B3, define/design/build primeiro: o maior bloco antes, e a release do módulo 7 espera.

---

## Selected Approach

| Attribute | Value |
|-----------|-------|
| **Chosen** | A1 (por peso) + B1 (duas frentes) |
| **User Confirmation** | 2026-11-13, Roberto: A1 depois da explicação com o esboço da pasta; B1 direto; blocos 1 e 2 confirmados |
| **Reasoning** | manutenção num repositório só sem levar ao starter o mecanismo do Open; o que o módulo 7 usa sai primeiro |

---

## Key Decisions Made

| # | Decision | Rationale | Alternative Rejected |
|---|----------|-----------|----------------------|
| 1 | brainstorm, handoff e governança ganham no Open o caminho sem terminal (itens C da comparação) e entram na `lista.txt` | são leves (9/5/10 citações); o texto serve aos dois públicos | modo em arquivo separado para elas |
| 2 | `sdd-release` ganha `references/MODO_INICIANTE.md` (base: a release do starter `v1.5.17` + Vercel) e é gerada dele | o aluno do módulo 7 usa GitHub + Vercel; o caminho do Open é ferramenta de mantenedor | skill nova `sdd-publicar`; release fora do starter |
| 3 | `ux-review-builder` vira a 22ª skill do Open (1.5.0, maior que a 1.4.0 do starter), gerada; a `sdd-ux-review` lê o `UX_STANDARD.md` quando existir | 117 downloads; funciona sozinha | trocar pela `sdd-ux-review`; tirar do starter |
| 4 | `docs/`, `exemplos/`, `tests/` do starter mudam para `scripts/starter/raiz/`, atualizados (skills de agora, 3 congeladas) | regra "gerado ou retirado" vale também para o que não é skill | gerar dos docs do Open; deixar no starter |
| 5 | A regra "skill de modo" no gerador: o `SKILL.md` gerado = frontmatter + identificação + `GENERATED` + o arquivo de modo + `MIGRAR`; só os arquivos citados pelo modo vão | evita 73 trocas e mantém o lint do `init` valendo | trocas grandes; blocos marcados |
| 6 | define, design e build continuam congeladas até a **F17c** (modo web, mesma abordagem A1 para pesadas) | tamanho de uma sessão | tudo agora |
| 7 | **Simplicidade do iniciante é critério de aceite medido**, não intenção: toda parada nova (pergunta obrigatória, OK, comando, condição que bloqueia) na skill gerada, comparada à `v1.5.17`, precisa do OK do Roberto; sem OK, sai do caminho web | pedido explícito do Roberto; o texto do Open tem regras a mais (perfil de risco obrigatório, linha de Verify Gate, prova por script, Status formal) | confiar no lint do `init`, que não mede dificuldade |

---

## Features Removed (YAGNI)

| Feature Suggested | Reason Removed | Can Add Later? |
|-------------------|----------------|----------------|
| define, design e build web | tamanho da frente (decisão 6) | Sim (F17c) |
| Outros hosts além da Vercel (Netlify, Cloudflare) | o módulo 7 usa Vercel; GitHub Actions segue coberto pelo caminho de hoje | Sim, com pedido |
| Deploy pela CLI da Vercel | exige login e token na skill; a integração com o GitHub já publica | Sim |
| Revisão adversarial, ledger e curadoria no modo iniciante | ferramenta do mantenedor do Open | Não |
| `docs/guia-do-aluno.pt-BR.md` do clone local | trabalho do Roberto fora do git | Sim, quando ele quiser (escrito no Open) |
| Geração automática por workflow | exige token com escrita no starter | Sim |

---

## Incremental Validations

| Section | Presented | User Feedback | Adjusted? |
|---------|-----------|---------------|-----------|
| Abordagem A (mecanismo) | ✅ | "não entendi" → reapresentada com o esboço da pasta → confirmada | Yes |
| Bloco 1: o que entra e o YAGNI | ✅ | Confere | No |
| Bloco 2: simplicidade medida, geração, versões, release | ✅ | Confere (depois da pergunta do Roberto sobre o modo do iniciante) | Yes (critério de simplicidade acrescentado) |

---

## Suggested Requirements for /define

### Problem Statement (Draft)
Cinco skills do starter (brainstorm, handoff, governança, release, ux-review-builder) e `docs/`, `exemplos/`, `tests/`
ainda são texto próprio do starter, que diverge do Open e exige manutenção dobrada; a release congelada confere o
deploy por workflow, e o aluno do módulo 7 publica pela Vercel. Gerar tudo do Open sem deixar o caminho do aluno
iniciante mais difícil.

### Target Users (Draft)
| User | Pain Point |
|------|------------|
| Roberto (mantenedor) | dois repositórios para manter |
| Aluno iniciante na web (claude.ai, ChatGPT) | precisa de brainstorm e handoff que entreguem no chat, sem terminal |
| Aluno do módulo 7 (terminal, GitHub + Vercel, sem o `init`) | precisa de uma release curta que confira o deploy da Vercel |

### Success Criteria (Draft)
- [ ] brainstorm, handoff, governança, release e ux-review-builder na `lista.txt`; a 2ª geração pela tag sai 0; o
      starter fica com 15 skills geradas e 3 congeladas (define, design, build), e o README diz isso nos 2 idiomas.
- [ ] Regra "skill de modo": o `SKILL.md` gerado da release vem só de `references/MODO_INICIANTE.md`; nenhum arquivo
      do caminho pesado vai; lint do `init` verde; baseline vermelho com a release crua.
- [ ] **Tabela de paradas** (`evidence/`): por skill, starter `v1.5.17` × gerada, com perguntas obrigatórias, OKs,
      comandos que o aluno roda e condições que bloqueiam; toda linha nova com o OK do Roberto ou retirada do caminho web.
- [ ] **Teste do iniciante:** brainstorm, handoff e governança geradas, num agente em contexto novo e **sem
      ferramentas**, com um pedido de aluno: nenhum comando pedido, documento entregue no chat com o aviso de que
      nada foi gravado, nenhuma exigência de script ou Verify Gate (critério escrito antes de rodar; log em `evidence/`).
- [ ] **Release iniciante:** exatamente 1 OK; nenhum token pedido, lido ou gravado; só git e `gh`; confere o deploy
      da Vercel pelo status do commit (ou o PR, com o preview) e diz a URL; o caminho por workflow do Actions continua.
- [ ] `ux-review-builder` 1.5.0 no Open com as convenções (Como falar, identificação, `skill-lint --conversa`),
      contagens dos testes de 21 para 22; a `sdd-ux-review` lê o `UX_STANDARD.md` quando existir.
- [ ] `docs/`, `exemplos/`, `tests/` em `scripts/starter/raiz/`, protegidos pela trava; os 62 testes da raiz verdes no
      starter gerado.
- [ ] `SKILL.md` da `sdd-release` em até 500 linhas; `check-versions.py --base v2.13.0` verde.
- [ ] Release do Open publicada; PR e Release do starter com OK próprio do Roberto; F17c registrada no plano.

### Constraints Identified
- bash 3.2 + Python stdlib; o gerador só roda igual ao da tag (64): gerar de uma worktree da tag.
- Nada da RDD no Open nem no starter; nada da F15 (a frente toca a `sdd-release`).
- 11 dígitos no pacote (LM-012); sha256 só no `GERADO.txt` do starter.
- Contagens fixadas (21 skills, 30 perguntas do `sdd-decisoes-lint`, versões em `test_f*_textos`).

### Out of Scope (Confirmed)
- Itens da tabela YAGNI; remendo à mão no starter; qualquer trabalho da F15.

---

## Session Summary

| Metric | Value |
|--------|-------|
| Questions Asked | 6 de descoberta + perfil de risco + amostras |
| Approaches Explored | 3 (mecanismo) + 3 (escopo) |
| Features Removed (YAGNI) | 6 |
| Validations Completed | 3 |
| Duration | ~1 sessão parcial |

---

## Next Step

**Ready for:** `/sdd-define sdd/features/BRAINSTORM_F17B_STARTER_ETAPA2.md`
