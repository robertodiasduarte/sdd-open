# BRAINSTORM: F4 Conversa

> Exploratory session to clarify intent and approach before requirements capture

## Metadata

| Attribute | Value |
|---|---|
| Feature | F4_CONVERSA |
| Date | 2026-10-29 |
| Author | brainstorm-agent |
| Status | Handoff Ready |

## Initial Idea

**Raw Input:** "Esta sessão faz a F4 inteira, do brainstorm à release: a camada de conversa nas 13 skills nativas, mais os itens A–G que o plano trouxe do porte." Escopo: "a seção `## Como falar com o aluno` + `references/como-falar.md` nas 13 skills nativas […]; o `skill-lint.py` passa a conferir a seção; `design-lint.py` e `handoff-lint.py` em `sdd/bin/`; `metadata.updated` + a linha de identificação; os itens do porte: A (linha de transição ≤100 caracteres), B (`sdd/templates/fragments/PERGUNTA_DECISAO.md`), C (formato da parada ⏸️, que a F9 liga ao exit 40), D (fixtures que **reprovam** no `skill-lint`), E (o `design-lint` fixa `## Key Decisions` / `### Decision N: <nome>`), F (o `handoff-lint` aceita seção extra) e G (`tests/test_agnostico.py`)." (prompt da sessão 2; `sdd/features/PLANO_F4_F15_CONSOLIDADO.md`, seção 4.1)

**Context Gathered:**
- Fato (lido): `main` = `dd27ef6` (M1), última Release `v2.2.4` (tag em `303cc87`). 16 skills em `.agents/skills/`, 326 testes.
- Fato (lido): versões de partida: auditoria-harness 1.0.0, brainstorm 2.0.0, build 2.1.1, define 2.1.0, design 2.0.0, governanca 2.1.0, handoff 2.0.0, iterate 2.0.1, new-session 1.1.0, playbook 2.0.0, prompt-builder 2.0.0, release 2.2.0, ux-review 2.1.0, checar-ambiente 1.3.0.
- Fato (lido): 9 skills abrem com `> Abra a resposta com o banner: 🧠 FASE` (brainstorm, build, design, define, governanca, iterate, release, new-session, ux-review). A Decisão 3 da frente manda o nome da fase virar a 1ª palavra do Status.
- Fato (lido): a seção `## Como falar com o aluno` já existe em `sdd-iniciar-repo` (linha 22) e `sdd-higiene-dado` (linha 60), no formato Grupo 1 (glossário dentro, sem `como-falar.md`), e as duas já têm a linha de identificação. A `sdd-checar-ambiente` não tem a seção, nem no starter. A regra "Como reportar" dela manda responder **só** a linha ✅ quando o ambiente está saudável.
- Fato (lido): no sdd-starter `17c69c4`, 7 das skills nativas do open têm fonte. 5 estão no formato Grupo 2, com seção de 31–32 linhas e `como-falar.md` de 50–73 linhas: brainstorm, build, define, design e handoff. 2 estão no formato Grupo 1, com seção de 61 linhas e sem `como-falar.md`: new-session e release. `sdd/DEFINE_LINGUAGEM_ALUNO.md` fixa os 10 itens da camada e os nomes de etapa.
- Fato (lido): `sdd/bin/skill-lint.py` (132 linhas) só confere frontmatter. Ele vai para o projeto do usuário no `init`, e o `CONTRIBUTING.md:50` manda rodá-lo em todo `SKILL.md` tocado. No CI ele roda como `python3 sdd/bin/skill-lint.py .agents/skills/sdd-*/SKILL.md` (`publish-gate.yml:109`, conferido por `tests/test_release_workflow.py:269`). `tests/test_skill_lint.py` fixa 16 skills.
- Fato (lido): o `sdd/templates/HANDOFF_TEMPLATE.md` e a `sdd-handoff` 2.0.0 do open usam este formato: `# HANDOFF:`, `## Ficha` (Feature, Objetivo, Status, Última sessão, Branch / pasta, Artefatos, Verify Gate), `## Feito`, `## Falta`, `## Definition of Done`, `## ⛔ Landmines desta feature`, `## Casos e testes em aberto`, `## Prompt de retomada` e `## Histórico de slices` com `### … — AAAA-MM-DD`; `## Eventos` só aparece quando há mudança de escopo. O item F do plano ("ficha, Eventos, as seis seções da etapa") descreve o formato do **starter** (`validate_handoff.py`), que também é o do `HANDOFF_INCORPORAR_STARTER.md` desta família.
- Fato (lido): `sdd/templates/DESIGN_TEMPLATE.md` tem `## Key Decisions` com `### Decision N: {Decision Name}`, `## File Manifest` (`| # | File | Action | Purpose | Agent | Dependencies |`) e `**Total Files:** {N}`. DESIGN_F1, F2 e F3 têm 1 `## Key Decisions` e 5, 7 e 7 decisões no padrão `### Decision N: `.
- Fato (lido): nomes de ferramenta de um agente só no que vai para o projeto: `AskUserQuestion` em `sdd/templates/fragments/CLARIFY.md:45` e "Task tool" em `sdd/templates/BUILD_REPORT_TEMPLATE.md:75`. A palavra "subagente" aparece 4 vezes, sempre como conceito com degradação (`sdd-build/SKILL.md:122`, `sdd-build/references/contexto-fresco.md:18`, `sdd-governanca/SKILL.md:51`, `sdd-governanca/references/PROCEDIMENTO.md:12`).
- Fato (lido): `sdd/templates/fragments/RESUMO_ETAPA.md` é o dono do kanban `✅ 🏃 ⬜ ➖` e do bloco "O que precisa de você", que só aparece com N ≥ 1 e tem de ser "decidível sem abrir arquivo". Ele fica intacto (Decisão 3 da frente).
- Fato (lido): o `verify_gate` das F1–F3 roda a cópia por `git archive HEAD`, sem `.git` e sem `sdd/features/`, que não é rastreado.
- Fato (lido): `tests/test_correcoes_w0.py` confere as duas chamadas do `verify-gate.sh` no passo 4 da `sdd-iterate` e a frase do `AVAL-*.log` em `contexto-fresco.md`. `tests/test_contrato_build_release.py:75` fixa a `sdd-build` em 2.1.1.
- Inferência: com a seção, as skills nativas ficam abaixo de 270 linhas (a maior, `sdd-release`, tem 233), longe do limite de 500.

**Technical Context Observed (for Define):**

| Aspect | Observation | Implication |
|---|---|---|
| Likely Location | 14 × `.agents/skills/<skill>/SKILL.md` + `references/como-falar.md`; `sdd/templates/fragments/PERGUNTA_DECISAO.md` (novo); `sdd/templates/fragments/CLARIFY.md`, `sdd/templates/BUILD_REPORT_TEMPLATE.md`; `sdd/bin/skill-lint.py`, `sdd/bin/design-lint.py` e `sdd/bin/handoff-lint.py` (novos); `sdd/fixtures/`; `tests/test_skill_lint.py`, `tests/test_design_lint.py`, `tests/test_handoff_lint.py`, `tests/test_agnostico.py`; `.github/workflows/publish-gate.yml` e `release.yml` (só o passo do `skill-lint`), `tests/test_release_workflow.py`; `docs/cli-conventions.md`, `CONTRIBUTING.md`; `MANIFEST.txt` | É a frente que mais toca texto de skill. Os contratos de `verify-gate.sh`, `report-lint.py` e `playbook-lint.sh` não mudam |
| Relevant KB Domains | N/A (não há `sdd/kb`). Fontes: sdd-starter `17c69c4` (seções, `como-falar.md`, `DEFINE_LINGUAGEM_ALUNO.md`, `validate_design.py`, `validate_handoff.py`) | Os validadores do starter são **reescritos** para os templates do open, não portados |
| IaC Patterns | Release automática no push de `main` que toca `.agents/skills/**`, `sdd/bin/**`, `sdd/templates/**` e `sdd/fixtures/**`; o `release` espera `testes` **e** `testes-macos`; o passo "Skill integrity" reprova Unicode invisível e `curl … \| sh` literal em `.agents/skills/` | As 14 skills sobem de versão (`check-versions.py --base v2.2.4 --base-obrigatoria`). Patch automático (`v2.2.5`) ou minor (`v2.3.0`) é perguntado no OK da release |

## Discovery Questions & Answers

| # | Question | Answer | Impact |
|---|---|---|---|
| 1 | Decisão 2 do plano: o formato de pergunta tem "não sei" (starter), "sem 'Outro'" (privado) ou as duas? | As duas (recomendado) | `PERGUNTA_DECISAO.md` exige a opção "não sei" escrita e proíbe a opção "Outro" escrita. Resposta fora das opções: responder a dúvida e repetir as opções. Ferramenta que traz "Other" sozinha continua trazendo. O `skill-lint --conversa` confere as duas coisas nos exemplos |
| 2 | Decisão 3 do plano: a F4 absorve os itens A–F do porte? | Sim, A–F (recomendado) | Entram a linha de transição ≤100 caracteres como Próximo passo (A), o fragmento único (B), o formato da parada ⏸️ (C), as fixtures que reprovam (D), os títulos de ADR fixos (E) e o `handoff-lint` tolerante (F) |
| 3 | O `skill-lint.py` vai para o projeto do usuário. Como ligar a conferência da seção sem reprovar as skills que o usuário escreveu? | Flag `--conversa` (recomendado) | Sem flag, o lint faz o mesmo de hoje (frontmatter). Com `--conversa`, exige a seção e o `references/como-falar.md` quando a seção mandar lê-lo, além das regras dos exemplos. O CI e o `test_skill_lint` passam a flag |
| 4 | A `sdd-checar-ambiente` (portada na F2) não tem a seção. O que fazer com ela? | Escrever a seção nela (recomendado) | São **14** skills na F4: as 13 nativas + checar-ambiente 1.3.0 → 1.4.0. As 16 skills do pacote passam no `--conversa` sem exceção |
| 5 | O `handoff-lint` confere o formato do starter (o do item F) ou o do open? | O do open (recomendado) | O lint confere o mínimo do `HANDOFF_TEMPLATE.md` do open, aceita seção a mais e não exige `## Eventos`. O `HANDOFF_INCORPORAR_STARTER.md` (formato do starter) não é controle verde. A fixture verde nova sai do template do open |
| 6 | A `sdd-design` e a `sdd-handoff` passam a rodar o lint novo sobre o arquivo que gravaram? | Sim, 1 passo no fim (recomendado) | Duas exceções declaradas à regra "comandos e ordem dos passos não mudam": um passo novo no fim de cada skill ("confira com …; vermelho ⇒ corrija antes de entregar"). O diff de cada uma mostra que esse é o único comando novo |
| 7 | O que o `tests/test_agnostico.py` reprova, e onde? | Nomes de ferramenta (recomendado) | Reprova `AskUserQuestion`, `TodoWrite`, `PreToolUse`/`PostToolUse`, "Task tool", "Agent tool", `subagent_type` e `/model`. "Subagente" fica permitido como conceito. Varre `.agents/skills/**`, `sdd/templates/**`, `AGENTS.md.tmpl` e `sdd/playbook.md`. Os 2 hits de hoje são corrigidos, e o teste falha na `v2.2.4` |

## Sample Data Inventory

| Type | Location | Count | Notes |
|---|---|---:|---|
| Input files | `/Users/robertoduarte/rdd-public/sdd-starter/skills/{sdd-brainstorm,sdd-build,sdd-define,sdd-design,sdd-handoff,sdd-new-session,sdd-release}/SKILL.md` (seção) e `references/como-falar.md` | 7 seções + 5 `como-falar.md` | Fonte das 7 skills com origem no starter. new-session e release estão no Grupo 1 (sem `como-falar.md`) e passam ao formato curto + referência |
| Output examples | `.agents/skills/sdd-iniciar-repo/SKILL.md:22` e `.agents/skills/sdd-higiene-dado/SKILL.md:60` (open); `sdd-build/references/como-falar.md` do starter (2 exemplos completos) | 3 | Forma já aceita no open: símbolos `✅ ▶️ ⬜ ⏸️ ➖`, linha de identificação e "Quando terminar, me peça de novo" |
| Ground truth | `/Users/robertoduarte/rdd-public/sdd-starter/sdd/DEFINE_LINGUAGEM_ALUNO.md` | 10 itens | Os 10 itens da camada, os nomes de etapa e o glossário mínimo por skill |
| Related code | `sdd/features/DESIGN_F{1,2,3}_*.md` (controle verde do `design-lint`); `validate_design.py` e `validate_handoff.py` do starter (só como referência); `sdd/bin/skill-lint.py`, `tests/test_skill_lint.py`, `tests/apoio.py` | 3 DESIGN + 2 validadores + lint e testes atuais | Nenhum HANDOFF real no formato do open: a fixture verde do `handoff-lint` é escrita a partir do template |

**How samples will be used:**
- As 7 seções do starter são a fonte do texto. Os nomes de etapa são remapeados aos passos de cada skill do open no Design.
- As seções da iniciar-repo e da higiene-dado mostram o formato já publicado no open.
- Os DESIGN_F1–F3 viram fixtures verdes do `design-lint`.
- O `validate_handoff.py` do starter dá as regras genéricas (placeholder, "como discutimos"), não a lista de seções.

## Approaches Explored

### Approach A: Seção autocontida por skill + `como-falar.md` + fragmento único de pergunta e parada — Recommended

**Description:**
- **Em cada `SKILL.md`**, a seção `## Como falar com o aluno` tem ~25–30 linhas:
  - a tabela de etapas, mapeada aos passos;
  - as 5 partes, com o Status abrindo a resposta e o Próximo passo ≤100 caracteres;
  - as regras curtas.
- **`references/como-falar.md`** traz o glossário da skill, o Status preenchido e um exemplo completo.
- **`sdd/templates/fragments/PERGUNTA_DECISAO.md`** é a fonte única do formato detalhado:
  - da pergunta: recomendada primeiro + porquê, números, `(ref:)`, "não sei", nenhum "Outro", eco de 1 linha, `[Dn]` reservado;
  - da parada ⏸️.

  O `como-falar.md` de cada skill cita o fragmento.
- **Uma release só.**

**Pros:**
- A skill funciona lida sozinha. É o que a Decisão 5 da frente precisa quando o starter for gerado a partir do open.
- O `skill-lint --conversa` confere cada skill, não só um ponteiro.
- É o padrão já provado nas 10 skills do starter.

**Cons:**
- As regras curtas ficam repetidas em 14 arquivos, e mudá-las depois reabre as 14. Quem segura a deriva são os testes, que conferem as frases-chave.

**Why Recommended:** é a única abordagem em que a camada não depende de o agente abrir um segundo arquivo, e ela cabe numa release, que é o orçamento desta sessão.

### Approach B: Fragmento central `CONVERSA.md`, seção mínima por skill

**Description:** as 10 regras moram em `sdd/templates/fragments/CONVERSA.md`. A seção de cada skill fica só com a tabela de etapas e o ponteiro (~8 linhas).

**Pros:**
- Uma fonte de verdade.
- A F9, que reabre as 13 skills, mexeria num arquivo só.

**Cons:**
- O agente precisa abrir 2–3 arquivos antes de responder, e se não abrir, a camada inteira some.
- A skill deixa de funcionar como zip, o que contraria a Decisão 5.
- O lint confere só o ponteiro.

### Approach C: A em duas releases

**Description:**
- **R1:** só o mecanismo (fragmento, 3 lints, `test_agnostico`, correção dos 2 templates), sem `--conversa` no CI.
- **R2:** as 14 skills, com o `--conversa` ligado.

**Pros:**
- Diffs menores.
- Um ponto de parada no meio da sessão.

**Cons:**
- Dois ciclos de gate, CI e OK numa sessão; a F3 consumiu uma sessão com um ciclo.
- `sdd-design` e `sdd-handoff` sobem de versão duas vezes.

## Selected Approach

| Attribute | Value |
|---|---|
| Chosen | Approach A, com seção autocontida por skill, `como-falar.md` e `PERGUNTA_DECISAO.md`, numa release |
| User Confirmation | 2026-10-29, escolha explícita da opção "A (Recomendado)"; checkpoints 1 e 2 "Confirmo" |
| Reasoning | A camada não depende de o agente abrir outro arquivo; o lint confere cada skill; serve ao starter gerado do open; cabe numa sessão |

## Key Decisions Made

| # | Decision | Rationale | Alternative Rejected |
|---|---|---|---|
| 1 | Toda pergunta de decisão tem a opção "não sei" escrita e nunca uma opção "Outro" escrita (Decisão 2 do plano) | "Não sei" é saída honesta; "Outro" é campo livre que reabre a decisão | Só "não sei"; só "sem Outro" |
| 2 | A F4 absorve os itens A–F do porte, além de G (Decisão 3 do plano) | Todos tocam as mesmas skills ou os 2 lints novos | Só A–C; nenhum |
| 3 | São **14 skills**: as 13 nativas + `sdd-checar-ambiente` | Com `--conversa` sobre as 16, sem exceção; o aluno chama a checar-ambiente direto | Exceção declarada; deixar fora do `--conversa` |
| 4 | `skill-lint.py --conversa`: sem flag, o comportamento é o de hoje. Com a flag, exige: a seção; a tabela de etapas; o `references/como-falar.md` quando a seção manda lê-lo; em cada pergunta de exemplo do `como-falar.md`, exatamente 1 opção `(recomendado)` e 1 "não sei", e nenhuma "Outro" | O lint vai para o projeto do usuário; as skills dele não podem reprovar | Ligado sempre; ligado pelo prefixo `sdd-` |
| 5 | Fixtures do `skill-lint` que **reprovam** (item D): sem a seção; `como-falar.md` ausente; pergunta sem `(recomendado)`; 2 `(recomendado)`; sem "não sei"; com "Outro". Mais 1 controle que passa | Sem fixture reprovada, o lint só prova que o texto está lá (LM-001) | Só o controle verde |
| 6 | `sdd/templates/fragments/PERGUNTA_DECISAO.md` é a fonte única do formato. **Pergunta:** a recomendada primeiro, com o porquê; números em vez de adjetivos; IDs só em `(ref:)`; "não sei"; nenhum "Outro"; eco de 1 linha depois da resposta; `[Dn]` reservado para a W2. **Parada ⏸️:** motivo, onde a ação acontece, passos com resultado esperado, o que não foi feito, caminho do brief gravado e comando da sessão nova (campos que a F9 liga ao `exit 40`) e "Quando terminar, me peça de novo, eu continuo daqui" | Itens B e C; uma regra só para a mesma pergunta | Duas regras (starter e privado) |
| 7 | Glossário genérico da F4: `worktree`, `gate`, `manifest` e `slice` só com a explicação junto, mais os termos do open sem equivalente no starter: exit 0/2/3/4/5/64, landmine, ledger, drift, slot vazio, adaptador e sync, waiver, vendor, contexto fresco, iterate. A denylist do RDD não viaja | Item B; regra 4 do 8.0 | Copiar a denylist do privado |
| 8 | O nome da fase vira a 1ª palavra do Status (`Build: ✅ 1 Plano · ▶️ 2 Modo · …`), e a linha `> Abra a resposta com o banner` sai das 9 skills que a têm | Decisão 3 da frente (não reabrir) | Banner e Status juntos |
| 9 | O Próximo passo é a linha de transição, com ≤100 caracteres (item A), sem seção nova. O kanban do `RESUMO_ETAPA.md` fica intacto e só fecha a fase; o "O que precisa de você" dele segue o `PERGUNTA_DECISAO.md` | Sem 2ª moldura (porte §2.5 X2) | Seção "Encerramento" nova (é da W2) |
| 10 | Cada uma das 14 skills ganha a linha de identificação (`sdd-x vX.Y.Z · out/2026 · versão atual: https://github.com/robertodiasduarte/sdd-open/releases/latest`), o `metadata.updated: "2026-10"` e um bump **minor** | É o mesmo formato da iniciar-repo e da higiene-dado; a camada é funcionalidade nova | Bump patch |
| 11 | Os nomes de etapa das 7 skills com fonte no starter são os do `DEFINE_LINGUAGEM_ALUNO.md`, remapeados no Design aos passos do open. As 7 sem fonte: auditoria-harness `Segurança · SDD principal · Inventário · Achados · Relatório`; governança `Triagem · Padrão do projeto · Item a item · Relatório · Suas decisões · Aplicar no DEFINE`; iterate `Ler · Classificar · Aplicar · Cascata · Fechar`; playbook `Leitura · Candidato · Promoção`; prompt-builder `Objetivo e contrato · Regras · Conferir · Entregar`; ux-review `Contexto · Jornada · Qualidade · Prioridades · Gravar`; checar-ambiente `Verificar · Explicar` | Confirmado no checkpoint 1 | — |
| 12 | Na `sdd-checar-ambiente` saudável, a resposta tem 2 linhas, o Status e a linha ✅, em vez de "exatamente a linha ✅" | O Status abre toda resposta (Decisão 3) | Exceção à Decisão 3 |
| 13 | `sdd/bin/design-lint.py` confere: `## Key Decisions` presente, com ≥1 `### Decision N: <nome>`, N sequencial a partir de 1, e nenhum título de decisão fora do padrão (item E); `## File Manifest` com ≥1 linha; `**Total Files:**` igual ao número de linhas; Dependencies apontando para `#` existente e sem ciclo; nenhum `{placeholder}` | Os títulos de ADR são lidos pelo `docs-extract-decisions.sh` da F12/W4 | Portar o `validate_design.py` do starter |
| 14 | `sdd/bin/handoff-lint.py` confere o mínimo do template do open: `# HANDOFF:`; `## Ficha` com Objetivo, Status e Verify Gate; `## Prompt de retomada` com bloco de código; `## Histórico de slices` com ≥1 `### … — AAAA-MM-DD`; nenhum `{placeholder}` ou `«placeholder»`; nada de "como discutimos" / "de onde paramos". Seção a mais passa (item F); `## Eventos` é opcional | É o formato da `sdd-handoff` do open; a W5 completa o template sem reescrever o lint | Formato do starter; aceitar os dois |
| 15 | A `sdd-design` e a `sdd-handoff` ganham 1 passo no fim, que roda o lint novo sobre o arquivo gravado. São as duas únicas exceções de comando, declaradas no diff | Um lint que a skill não roda só prova alguma coisa no CI | Lints só como ferramenta |
| 16 | `tests/test_agnostico.py` reprova `AskUserQuestion`, `TodoWrite`, `PreToolUse`, `PostToolUse`, "Task tool", "Agent tool", `subagent_type` e `/model` em `.agents/skills/**`, `sdd/templates/**`, `AGENTS.md.tmpl` e `sdd/playbook.md`, fora de uma lista de adaptadores declarados. Leva fixture que reprova e controle que passa. "Subagente" como conceito é permitido | Regra 10 do 8.0; a tabela de degradação precisa do conceito | Proibir "subagente"; varrer só `SKILL.md` e `references/` (não pegaria o `CLARIFY.md`) |
| 17 | `CLARIFY.md:45` (`AskUserQuestion`) e `BUILD_REPORT_TEMPLATE.md:75` ("Task tool") são reescritos sem nome de ferramenta | O `test_agnostico` falha na `v2.2.4` por eles e passa no HEAD | — |
| 18 | A prova de que comandos e passos não mudaram é um **script de evidência**, não um teste. Ele compara, em cada `SKILL.md`, a `v2.2.4` com o HEAD: os títulos de passo numerado e as linhas com código entre crases que citam `sdd/bin`, `git`, `gh`, `bash`, `python3` ou `scripts/`. A diferença tem de ser exatamente as exceções declaradas: sai o banner; entram a linha de identificação e o lint da `sdd-design`/`sdd-handoff`; muda a regra da checar-ambiente saudável | A cópia por `git archive` do gate não tem `.git` para comparar com a tag | Diff só lido à mão; teste no gate |
| 19 | O Verify Gate é o de sempre: cópia por `git archive HEAD`, `PUBLISH_GATE_MODE=ci bash scripts/publish-gate.sh` e `unittest discover` no piso (`SDD_TEST_BASH=/bin/bash /usr/bin/python3`). O `design-lint` sobre o próprio DESIGN e o `check-versions --base v2.2.4 --base-obrigatoria` viram ATs com log, fora do `cmd`. O `scripts/publish-gate.sh` não muda: os lints novos rodam pela suíte de testes | O `sdd/features/` não é rastreado e a cópia não tem `.git` | Novo G6 no publish-gate |
| 20 | Sabotagem: 1 por script (`skill-lint`, `design-lint`, `handoff-lint`), mais 1 no `test_agnostico` (tirar `AskUserQuestion` da lista). Cada uma fica vermelha com o nome do teste | Critério da sessão; padrão da W0 e da M1 | — |
| 21 | A versão do pacote (`v2.2.5` automática × `v2.3.0` por tag manual) é perguntada no OK da release | Instrução da sessão | Decidir agora |

## Features Removed (YAGNI)

| Feature Suggested | Reason Removed/Deferred | Can Add Later? |
|---|---|---|
| Runner ou eval de conversa (medir o tom no agente) | O gate prova estrutura; o tom fica para conferência humana (o starter cortou o mesmo) | Yes |
| `design-lint` cruzando o inventário LLM com o manifest e a rastreabilidade AT → arquivo (`validate_design.py` do starter) | A F13 traz LLM no código; a rastreabilidade não tem formato fixo no template do open | Yes |
| "Por que cada regra existe (não apague sem ler)" nas skills | Item da F6 | Yes |
| Seção "Encerramento"/encadeamento, classes D1–D5 e `sdd-fluxo.sh` | São da W2/F9 (plano, 4.1); fica só o lugar `[Dn]` | Yes |
| Conferência manual da conversa no Codex depois da release como critério | Vira pendência registrada no handoff | Yes |
| `handoff-lint` no formato do starter | Decisão 5: o lint confere o formato do open | No |
| G6 no `scripts/publish-gate.sh` para os lints | A suíte de testes já roda no CI e no gate | Yes |

## Incremental Validations

| Section | Presented | User Feedback | Adjusted? |
|---|---|---|---|
| Checkpoint 1 — cortes YAGNI, componentes (fragmento, 3 lints, `test_agnostico`, 14 `como-falar.md`, mudanças em cada skill), nomes de etapa das 7 skills sem fonte, checar-ambiente saudável com 2 linhas | Yes | "Confirmo" | No |
| Checkpoint 2 — ordem do build (testes vermelhos primeiro), prova de comandos por script de evidência, falhas e invariantes (`test_correcoes_w0`, `test_contrato_build_release`, integridade do CI, 500 linhas), Verify Gate, publish-gate sem mudança, 4 sabotagens | Yes | "Confirmo" | No |

## Suggested Requirements for /define

### Problem Statement (Draft)

As 13 skills nativas do sdd-open e a `sdd-checar-ambiente` respondem sem moldura comum. O aluno não sabe em que etapa está, recebe jargão sem explicação e pergunta sem opções nem efeito. Os documentos de Design e Handoff não têm lint, e nada impede que o texto de uma skill cite ferramenta de um agente só. A F4 põe a camada "Como falar com o aluno" nas 14 skills sem mudar comandos nem ordem dos passos, e prova isso com 3 lints e 1 teste de agnosticismo.

### Target Users (Draft)

| User | Pain Point |
|---|---|
| Aluno que usa o sdd-open (em qualquer um dos agentes suportados) e nunca usou git nem terminal | Não sabe em que ponto está, não entende os termos, responde "pode" sem saber o que autoriza |
| Roberto, mantenedor | Precisa que a camada não se perca em edições futuras (F9 reabre as 13 skills) e que os lints novos não mudem quando a W4/W5 chegarem |
| Frentes seguintes (F9, F12, F14) | Precisam de um formato de pergunta e parada fixo para ligar o `exit 40`, e de títulos de ADR estáveis |

### Success Criteria (Draft)

- [ ] `python3 sdd/bin/skill-lint.py --conversa .agents/skills/sdd-*/SKILL.md` sai 0 nas 16 skills; sem a flag, sai 0 numa skill sem a seção.
- [ ] Cada uma das 6 fixtures do `skill-lint` reprova (exit 1) e o controle passa.
- [ ] `design-lint.py` sai 0 nos DESIGN_F1–F3 e no próprio `DESIGN_F4_CONVERSA.md`, e 1 em `### Decisão 1`, em `## Decisions`, em manifest com ciclo e em `Total Files` errado.
- [ ] `handoff-lint.py` sai 0 na fixture do template do open, com e sem seção extra, e 1 sem `## Prompt de retomada`, com `{placeholder}` e com "como discutimos".
- [ ] `tests/test_agnostico.py` falha na `v2.2.4` e passa no HEAD; a fixture reprova e o controle passa.
- [ ] O script de evidência mostra, para cada uma das 14 skills, que a diferença de comandos e passos entre a `v2.2.4` e o HEAD são só as exceções declaradas.
- [ ] `python3 scripts/check-versions.py --base v2.2.4 --base-obrigatoria` sai 0, com as 14 versões acima da base.
- [ ] Verify Gate exit 0 (`git archive` + publish-gate ci + suíte no piso), e CI verde em `ubuntu-latest` e `macos-latest`.
- [ ] 4 sabotagens vermelhas com o nome do teste.
- [ ] Tom da conversa num agente real: TBD (conferência humana, fora do gate).

### Constraints Identified

- Só a camada de conversa muda. As exceções de comando estão declaradas: o lint no fim da `sdd-design` e da `sdd-handoff`, a regra da checar-ambiente saudável e a retirada do banner.
- Decisões da frente que não se reabrem: camada sempre ligada, sem toggle nem slot; Status `✅ ▶️ ⬜ ⏸️ ➖` abrindo cada resposta, com o nome da fase como 1ª palavra; kanban do `RESUMO_ETAPA.md` intacto; o open como fonte canônica de governanca, auditoria-harness e prompt-builder.
- Piso: Python 3.9 stdlib e bash 3.2, provados no CI macOS.
- Texto novo não pode trazer Unicode invisível nem `curl … | sh` literal (integridade do CI). O FE0F de `▶️`/`⏸️` é permitido; os bytes são conferidos depois de escrever.
- Ficam intactos: as duas chamadas do `verify-gate.sh` no passo 4 da `sdd-iterate` e a frase do `AVAL-*.log` no `contexto-fresco.md` (`tests/test_correcoes_w0.py`).
- `SKILL.md` ≤ 500 linhas.
- Arquivo novo entra no `MANIFEST.txt` em ordem `LC_ALL=C`; commit antes do gate.
- Push em `main` só com OK do Roberto citando "sdd-open" na mesma mensagem.
- Os artefatos SDD ficam na branch `docs/incorporar-starter`, nunca em `main`.

### Out of Scope (Confirmed)

- Encerramento/encadeamento automático, classes D1–D5 nas perguntas, `sdd-fluxo.sh` e o `exit 40` (W2/F9).
- Eval ou runner de conversa; conferência no Codex como critério.
- Inventário LLM e rastreabilidade no `design-lint` (F13).
- "Por que cada regra existe", guia do aluno, quickstart (F6).
- Mudança no `scripts/publish-gate.sh`, no `verify-gate.sh`, no `report-lint.py` e no `playbook-lint.sh`.
- `sdd-iniciar-repo` e `sdd-higiene-dado` (já têm a seção).
- Regenerar o sdd-starter a partir do open (frente própria, depois da F6).

## Session Summary

| Metric | Value |
|---|---:|
| Questions Asked | 11 (7 de descoberta, 1 de amostras, 1 de abordagem, 2 de checkpoint) |
| Approaches Explored | 3 |
| Features Removed (YAGNI) | 7 |
| Validations Completed | 2 |

## Next Step

Execute o **SDD Define by RDD**.
