# BRAINSTORM: F18 + F20 — segurança embutida no fluxo (alerta) e ações preventivas (prevenção)

> Sessão exploratória conjunta das frentes F18 e F20 do programa INCORPORAR_STARTER, antes do Define.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | F18_F20_SEGURANCA |
| **Date** | 2026-11-11 |
| **Author** | brainstorm-agent (sessão com o Roberto) |
| **Status** | Ready for Define |

---

## Initial Idea

**Raw Input:** "Executar a frente F18 (onda 1) + F20 do SDD Open: segurança embutida no fluxo (alerta) e ações
preventivas do e-book (prevenção), com brainstorm conjunto." Fonte temática: as falhas de segurança de app feito
com IA (banco aberto, chave exposta, XSS, CORS, cabeçalhos, IDOR, prompt injection etc.), com o "como evitar" e a
frase preventiva de cada uma, o checklist antes de publicar, o mapa falha → fase e o plano de resposta.

**Context Gathered:**
- Plano consolidado (branch `docs/incorporar-starter`), seções F18 e F20: F18 em 3 ondas (piso de alerta,
  alerta antecipado, prova); F20 em 6 entregas (frases no `AGENTS.md.tmpl` e na `sdd-build`, "como evitar" no
  Design, checklist no release, coluna fase, plano de resposta, starter).
- O que já existe no pacote (`v2.11.0`, `69b7f6b`): `checar.sh --segredo` acusa `.env`, `.pfx`, `.p12` e `.pem`
  com chave privada salvos no git; `sdd-higiene-dado` dá o alarme de commit; `sdd-governanca` cita RLS e log
  forense (G05), mas só dispara com dinheiro, tributo, folha ou dado pessoal; a passada 0c da `sdd-release`
  (`SKILL.md:155`) é condicional ("só se o diff toca auth, dados, permissões, rota pública") e não tem lista fixa.
- Zero menções a CORS, cabeçalhos de segurança, XSS, injeção de SQL, prompt injection, source maps e
  introspecção GraphQL em `.agents/skills/` (medição do plano, conferida no brainstorm).
- `AGENTS.md.tmpl` tem 3,5 KB; o slot `project.context_file_max_kb` é 100.
- 20 skills hoje; contagens de skill, versão e perguntas fixadas em testes antigos.

**Technical Context Observed (for Define):**

| Aspect | Observation | Implication |
|--------|-------------|-------------|
| Likely Location | `.agents/skills/sdd-seguranca/` (nova), `sdd/bin/seguranca-varredura.sh` (novo), `AGENTS.md.tmpl`, `bin/sdd-open.sh` (init/sync), `sdd-brainstorm`, `sdd-define`, `sdd-design`, `sdd-build`, `sdd-release`, `sdd/config.example.yaml`, `sdd/templates/` | skill nova + 1 script + 5 skills de fase + o instalador |
| Relevant KB Domains | nenhum | — |
| IaC Patterns | N/A | — |

---

## Discovery Questions & Answers

| # | Question | Answer | Impact |
|---|----------|--------|--------|
| 1 | O que o pacote público pode usar do e-book (material da RDD)? | **Não cita o e-book.** | Catálogo com texto próprio; no lugar do capítulo, referência pública (OWASP, CWE). Nenhum texto, prompt ou checklist copiado; nenhum nome de material da RDD no pacote. |
| 2 | O que entra nesta 1ª sessão? | **O máximo numa única sessão.** | Escopo: F18 ondas 1, 2 e 3 + F20 entregas 1 a 5. Só a entrega 6 (starter) fica fora, pela F17. |
| 3 | Onde mora o catálogo (e a revisão de segurança do Define)? | **Skill nova `sdd-seguranca`.** | 21ª skill; catálogo em `references/`; modos: Define (onda 2), checklist antes de publicar (web), incidente. |
| 4 | O que bloqueia a publicação? | **2 bloqueios, para toda tabela nova:** segredo literal e tabela criada em migração sem `enable row level security` (só com Supabase presente). | Detectar "dado pessoal" pelo nome da coluna foi recusado; falso positivo sai por dispensa na linha, com motivo. |
| 5 | Teto de avisos por fase? | **5, do mais grave**, com "e mais N" e a lista inteira em arquivo; bloqueio nunca entra no corte. | Slot `security.max_warnings: 5`. |
| 6 | Quanto texto preventivo vai para o `AGENTS.md`? | **5 regras + 1 ponteiro**, filtradas pela stack. | RLS, chave fora do navegador, cadastro fechado com e-mail confirmado, limite de tentativas (login e IA), cabeçalhos no host; o ponteiro manda ler as regras da stack na `sdd-seguranca` antes de construir. `init`/`sync` refazem quando a stack muda. |
| 7 | Onde mora o plano de resposta a incidente? | **Modo da `sdd-seguranca`**, que também dispara em "vazou a chave" ou "a tabela ficou aberta"; o fecho do release aponta para ele. | Referência na skill: fechar a porta, preservar evidência, dimensionar, corrigir, comunicar (LGPD/ANPD), registrar. |
| 8 | Linha do `rdd-appsec-mentor` no fecho do release (proposta do plano) | Sai (consequência da resposta 1, aceita sem objeção). | No lugar, o fecho aponta o "confira no app publicado" da `sdd-seguranca`. |

**Minimum Questions:** 3 — feitas 8 (7 respondidas pelo Roberto, 1 derivada e apresentada).

---

## Sample Data Inventory

| Type | Location | Count | Notes |
|------|----------|-------|-------|
| Input files | N/A | 0 | Decisão: só casos escritos do zero (sem projeto real, sem repositório público) |
| Output examples | N/A | 0 | — |
| Ground truth | N/A | 0 | — |
| Related code | `.agents/skills/sdd-governanca/` (molde da skill e do catálogo), `checar.sh --segredo`, passada 0c da `sdd-release`, `tests/test_agnostico.py` | 4 | Molde a seguir; derivar, não duplicar (RLS e log forense já estão no G05) |

**How samples will be used:**

- Cada padrão da varredura ganha um caso que deve acusar **e** o par que não pode acusar (falso positivo).
- Chaves falsas dos casos montadas em tempo de execução: o pacote não carrega texto com forma de segredo.
- O falso positivo do mundo real só será medido depois, em uso (registrado como limite).

---

## Approaches Explored

### Approach A: catálogo estruturado único, script e frases derivados dele ⭐ Recommended

**Description:** `sdd-seguranca/references/CATALOGO_SEGURANCA.md` com uma tabela rígida, uma linha por item
(S01–S22): id, falha, stack (`todas`, `supabase`, `vercel`, `web`), fase em que se evita, gravidade, bloqueia,
padrão da varredura (ou "só à mão"), prova "confira à mão", frase preventiva, "como evitar", referência pública,
`agents` (sim/não). A varredura lê os padrões do catálogo; o `init`/`sync` monta as regras do `AGENTS.md` das
linhas `agents=sim` da stack presente; um teste reprova linha fora da forma.

**Pros:**
- Uma mudança no item muda aviso, frase preventiva e prova juntos (LM-005: fonte estruturada, uma cópia).
- O starter da F17 gera a forma "confira à mão" do mesmo arquivo.

**Cons:**
- Tabela larga.
- O `init` passa a ler um arquivo de skill.

**Why Recommended:** é a única das três em que alerta (F18) e prevenção (F20) não se desencontram por construção.

---

### Approach B: catálogo em prosa, padrões no script

**Description:** catálogo legível em prosa; os padrões da varredura escritos dentro do script.

**Pros:**
- Mais rápida de escrever.

**Cons:**
- Duas fontes da mesma regra; a LM-005 registra divergência desse tipo em 2 a 3 ciclos.

---

### Approach C: sem script, só a passada do modelo guiada pelo catálogo

**Description:** a passada 0c do release lê o catálogo e julga o diff.

**Pros:**
- Igual em qualquer agente e na web.

**Cons:**
- Não determinística: não serve para bloquear, e o critério pede `arquivo:linha` reproduzível. (A passada de
  modelo continua existindo ao lado do script, agora com lista fixa.)

---

## Selected Approach

| Attribute | Value |
|-----------|-------|
| **Chosen** | Approach A |
| **User Confirmation** | 2026-11-11, nesta sessão |
| **Reasoning** | Fonte única para alerta, prevenção, varredura e "confira à mão" |

---

## Key Decisions Made

| # | Decision | Rationale | Alternative Rejected |
|---|----------|-----------|----------------------|
| 1 | O pacote não cita o e-book; texto próprio e referência pública (OWASP/CWE) | material da RDD não vai para o repositório público | citar capítulo; parafrasear de perto |
| 2 | Escopo máximo numa sessão: F18 ondas 1–3 + F20 entregas 1–5 | pedido do Roberto | só a onda 1; onda 1 + frases |
| 3 | Skill nova `sdd-seguranca` (modos: Define, checklist antes de publicar, incidente) | gatilho próprio (login, rota pública, dado de terceiros, upload, IA paga); não infla a governança | modo da `sdd-governanca`; arquivo em `sdd/` sem skill |
| 4 | 2 bloqueios (segredo literal; tabela nova sem RLS com Supabase), para toda tabela nova | as duas falhas mais caras; detectar dado pessoal por texto erra | só tabela "sensível"; nada bloqueia |
| 5 | Bloqueio só no que a publicação acrescenta; o que já existia vira aviso "já existia" | a 1ª release depois da instalação não trava por tabela antiga | bloquear a árvore inteira |
| 6 | Dispensa por comentário na linha ou na de cima: `sdd-seguranca: aceito S<nn> — <motivo>`; sem motivo não vale; aparece uma vez no relatório | falso positivo não pode travar para sempre nem sumir calado | lista de exceções em arquivo separado |
| 7 | Teto de 5 avisos por fase, do mais grave; lista inteira em `sdd/reports/evidence/{F}/` | aviso demais vira ruído | 3; sem teto |
| 8 | `AGENTS.md`: 5 regras + 1 ponteiro, filtradas pela stack; marcador preenchido por `init`/`sync` | regra demais no arquivo de contexto é ignorada; projeto sem Supabase não recebe regra de Supabase | todas as ~20; nenhuma |
| 9 | Plano de resposta como modo incidente da `sdd-seguranca` | o aluno procura na hora do aperto, fora do release | referência da `sdd-release` |
| 10 | Stack: detectada pelo projeto; slot `security.stack` passa por cima (vazio = detectar; `nenhuma` = só os itens de todas as stacks) | P2: item de Supabase só dispara com Supabase | só detecção; só slot |
| 11 | Varredura `sdd/bin/seguranca-varredura.sh`: só leitura, sem rede, bash 3.2 + Python stdlib; exits `0` nada · `1` avisos · `2` bloqueio · `64` uso | roda em toda publicação, em qualquer máquina do aluno | varredura pela rede |
| 12 | Passada 0c do release deixa de ser condicional e segue a lista fixa de 20 itens antes de publicar, com os 5 de maior risco primeiro | o plano mediu que a 0c sem lista não cobre CORS, cabeçalhos, XSS etc. | manter condicional |
| 13 | Linha do `rdd-appsec-mentor` sai; o fecho do release aponta o "confira no app publicado" da skill | nome e repositório da RDD | manter a linha |

---

## Features Removed (YAGNI)

| Feature Suggested | Reason Removed | Can Add Later? |
|-------------------|----------------|----------------|
| Linha do `rdd-appsec-mentor` no release e completar os 5 temas dele | nome e repositório da RDD | Sim, no privado (frente de lá) |
| Prompts de diagnóstico e correção do e-book | decisão de não citar nem copiar | Não |
| Varredura do app publicado pela rede (cabeçalhos, CORS por `curl`) | o release não depende de rede; vira "confira à mão" com passo a passo | Sim, como modo opcional |
| Detectar dado pessoal pelo nome da coluna | decisão: RLS vale para toda tabela nova | Não |
| Padrão de varredura para log injection, desserialização, JWT e pacote inventado | texto não acha com segurança; viram itens "só à mão" | Sim, item a item, com caso de teste |
| Starter (F20, entrega 6) | chega pela geração da F17, sem remendo no starter | Sim, na F17 |

---

## Incremental Validations

| Section | Presented | User Feedback | Adjusted? |
|---------|-----------|---------------|-----------|
| Bloco 1 — o que o aluno vê, fase a fase (AGENTS.md, Brainstorm, Define, Design, Build, Release, incidente) | ✅ | "Sim, está certo" | No |
| Bloco 2 — por dentro (stack, varredura, bloqueio só no acrescentado, dispensa, `AGENTS.md`, P2, contagens) | ✅ | "Sim, está certo" | No |

**Minimum Validations:** 2 — feitas 2.

---

## Suggested Requirements for /define

### Problem Statement (Draft)
O aluno que constrói com IA publica, sem saber, as falhas de segurança mais comuns de app gerado por IA (tabela
sem RLS, chave no código, CORS aberto, HTML cru de usuário, cabeçalhos ausentes), porque nenhuma fase do SDD Open
pergunta por elas, previne ao construir ou confere antes de publicar.

### Target Users (Draft)
| User | Pain Point |
|------|------------|
| Aluno iniciante que constrói com Supabase, Vercel e um agente de código | não sabe o nome das trancas nem que vêm desligadas; descobre no incidente |
| Aluno que usa o agente na web (claude.ai, ChatGPT), sem terminal | não roda script: precisa da forma "confira à mão" |
| Quem mantém o pacote | alerta e prevenção não podem divergir; o pacote é agnóstico (7 agentes) e público |

### Success Criteria (Draft)
- [ ] Caso com segredo literal acrescentado ⇒ `seguranca-varredura.sh` sai `2` com `arquivo:linha`, e a `sdd-release` dá FAIL.
- [ ] Caso com migração nova que cria tabela sem `enable row level security`, com Supabase presente ⇒ exit `2` com `arquivo:linha`.
- [ ] O mesmo achado só em linha que já existia na branch padrão ⇒ aviso "já existia", exit `1`, não `2`.
- [ ] Caso com `select('*')`, `dangerouslySetInnerHTML`, `eval(` e `Access-Control-Allow-Origin: *` ⇒ exit `1` (CONCERNS), cada aviso com id do catálogo e a prova "confira à mão".
- [ ] Cada padrão tem um par que não acusa (ex.: variável de ambiente lida pelo nome, `select('id, nome')`, CORS com origem fixa).
- [ ] Projeto sem Supabase ⇒ nenhum aviso nem regra de Supabase (varredura e `AGENTS.md`).
- [ ] Dispensa com motivo na linha ⇒ o achado sai do bloqueio e aparece uma vez como aceito; dispensa sem motivo não vale.
- [ ] Mais de 5 avisos ⇒ a tela mostra 5, os mais graves, e "e mais N"; a lista inteira fica no arquivo de evidência.
- [ ] `AGENTS.md` gerado pelo `init` traz as 5 regras da stack presente e passa no limite de tamanho; o `sync` refaz o bloco quando a stack muda.
- [ ] `sdd-seguranca` com DEFINE sem login, rota pública, dado de terceiros, upload nem IA paga ⇒ N.A. em 1 linha.
- [ ] Item recusado na `sdd-seguranca` aparece no BUILD_REPORT; item aceito vira AT com teste negativo no Verify Gate e o "como evitar" na seção "Segurança" do DESIGN.
- [ ] A passada 0c do release segue a lista fixa (5 de maior risco primeiro) em toda publicação.
- [ ] O catálogo passa no teste de forma (toda linha com os campos; `bloqueia=sim` só em S-segredo e S-RLS); nenhum texto cita o e-book nem material da RDD.
- [ ] `publish-gate.sh`, `skill-lint.py --conversa`, `test_agnostico.py`, `check-versions.py --base v2.11.0` e a suíte inteira verdes.

### Constraints Identified
- P2 agnóstico: nenhum nome de ferramenta de um agente só fora dos adaptadores; cada item com forma "confira à mão".
- bash 3.2 + Python stdlib; script novo de `sdd/bin` lê `sdd/bin/lib/python.sh` (guarda `sdd_python_pronto`).
- Repositório público: nada da RDD (nomes, caminhos, chaves, código do privado, texto do e-book).
- Número com 11 dígitos em arquivo do pacote é barrado pelo `publish-gate` (LM-012).
- Contagens fixadas em testes antigos mudam de propósito (21 skills, versões, perguntas do `sdd-decisoes-lint`).
- Tetos do CI (Ubuntu 45, macOS 75, Windows 30 min): suíte que cresce pede olhar o teto antes da tag.
- F15 não pareia (toca a `sdd-release`).

### Out of Scope (Confirmed)
- Starter (`sdd-starter`): recebe pela F17.
- Qualquer texto, prompt ou checklist copiado do e-book; qualquer citação a ele.
- `rdd-appsec-mentor` e o repositório privado.
- Varredura por rede do app publicado.
- Detecção de dado pessoal por nome de coluna.

---

## Session Summary

| Metric | Value |
|--------|-------|
| Questions Asked | 8 (+1 de amostras) |
| Approaches Explored | 3 |
| Features Removed (YAGNI) | 6 |
| Validations Completed | 2 |
| Duration | ~1 h (com o passo 0 da F16) |

---

## Next Step

**Ready for:** `/sdd-define sdd/features/BRAINSTORM_F18_F20_SEGURANCA.md`
