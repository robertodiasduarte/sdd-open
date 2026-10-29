# BRAINSTORM: F5 Conhecimento

> Exploratory session to clarify intent and approach before requirements capture

## Metadata

| Attribute | Value |
|---|---|
| Feature | F5_CONHECIMENTO |
| Date | 2026-10-29 |
| Author | brainstorm-agent |
| Status | Handoff Ready |

## Initial Idea

**Raw Input:** "Esta sessão faz a F5 inteira, do brainstorm à release: a `sdd-kb` portada do starter como 17ª skill, com o validador e o gate; a entrevista do `ux-review-builder` como entrada opcional da `sdd-ux-review`; e o item G do plano (KB Domains como lista fechada)." Escopo (plano, 4.2): "`sdd-kb` com `validate_kb` e `gate.sh`, perfil normativo e RULE_MAP apontando o teste que o Verify Gate roda; entrevista do `ux-review-builder` como entrada opcional da `sdd-ux-review`; `tests/test_skill_lint.py` passa de 16 para 17 skills." Item G: "'KB Domains' vira lista fechada: o valor só pode vir de `ls <pasta da KB>`, revalidado a cada Define; `nenhum` explícito." Item H: "não entra (F11/U1 ficam na W5); anotar no DESIGN que o `UX_REVIEW_TEMPLATE.md` vai ganhar a tabela WCAG 2.2 AA na W5." (prompt da sessão 3; `sdd/features/PLANO_F4_F15_CONSOLIDADO.md`, seção 4.2)

**Context Gathered:**
- Fato (lido): `main` = `2fcdda1` = tag `v2.2.5`. 16 skills em `.agents/skills/`, 388 testes no piso (Python 3.9.6, bash 3.2.57).
- Fato (lido): no sdd-starter `17c69c4`, `skills/sdd-kb/` (2.1.0) tem `SKILL.md` (325 linhas), 4 `references/` (`como-falar.md` 54, `kb-protocol.md` 131, `normativo.md` 85, `sourcing.md` 77), `scripts/validate_kb.py` (465, saídas 0/2/64), `kb_normativo.py` (246, `sha` e `rule-map [--check]`), `gate.sh` (68), 10 moldes em `assets/`, os exemplos `assets/example-kb` (4 arquivos) e `assets/example-kb-normativo` (13 arquivos), `CHANGELOG.md` e `agents/openai.yaml`.
- Fato (lido): o `gate.sh` do starter usa caminhos `skills/sdd-kb/…`, roda `unittest discover -s tests -p 'test_sdd_kb_*.py'` e lê `tests/fixtures/kb_good_*` (1: `kb_good_codigo`) e `kb_bad_*` (6: `limite_concept`, `limite_pattern`, `limite_quick`, `naoregistrado`, `placeholder`, `placeholder_codigo`). `tests/test_sdd_kb_normativo.py` tem 484 linhas e 62 testes, cada um aplicando **uma** mutação a uma cópia do `example-kb-normativo`.
- Fato (lido): o `init` do open copia a pasta inteira de cada skill para `.agents/skills/` do usuário (`bin/sdd-open.sh:547`); `tests/` e `scripts/` da raiz não viajam. O `doctor` avisa "skills do sdd-starter detectadas" quando acha `agents/openai.yaml` (`bin/sdd-open.sh:600`); `tests/test_matriz_new_session.py::Portadas` reprova `openai.yaml`, o texto `sdd-starter` e `tests/` dentro da skill nas 3 portadas da F2.
- Fato (lido): no texto e nos testes do starter, só a linha de identificação (link `sdd-starter/releases`) e os 4 caminhos do `gate.sh` citam o starter; nenhum nome de ferramenta de um agente só (`tests/test_agnostico.py`) e nenhum literal que o `publish-gate` reprova (sequência de 11+ dígitos, e-mail, CPF/CNPJ, telefone).
- Fato (lido): a `sdd-kb` do starter, copiada como está, reprova no `skill-lint --conversa`: o `como-falar.md` tem uma pergunta sem `(recomendado)` e não cita `PERGUNTA_DECISAO.md`. A seção dela também não usa o bloco comum de regras das 14 skills da F4 (`tests/test_conversa.py::FRASES`).
- Fato (lido): `sdd/templates/DEFINE_TEMPLATE.md:158` já descreve "KB Domains" como "nomes de pasta em `sdd/kb/` ou equivalente, ou `nenhum` explícito". Nenhuma skill do open cita KB, nem `sdd/kb/`. A `sdd-define` 2.2.0 tem os passos 1–9 (9 = Gravar).
- Fato (lido): no `ux-review-builder` 1.4.0, o `INTERVIEW_GUIDE.md` (78 linhas) pergunta público, estágio, referência e URL. A pergunta de público tem a opção "outro", que o `PERGUNTA_DECISAO.md` proíbe. O `CATALOGO_DE_REFERENCIAS.md` (25 linhas) tem 9 linhas e a regra Observado × Desejado × Recomendado. O `URL_ANALYSIS.md` (37 linhas) dá o protocolo de observação e os limites.
- Fato (lido): `sdd/templates/UX_REVIEW_TEMPLATE.md` já tem `## User and Context`. A `sdd-ux-review` 2.2.0 tem os passos 1–8 em lista numerada e só `references/como-falar.md`.
- Fato (lido): o RULE_MAP do exemplo normativo tem as colunas `Implementação` e `Teste`, ambas "—" nas 3 regras, e nada confere essas colunas.
- Inferência: a F5 sobe 3 skills (`sdd-kb` nova, `sdd-define` e `sdd-ux-review`) e mexe em `sdd/templates/` e `sdd/bin/`, então o push publica uma Release.

**Technical Context Observed (for Define):**

| Aspect | Observation | Implication |
|---|---|---|
| Likely Location | `.agents/skills/sdd-kb/` (nova), `.agents/skills/sdd-define/`, `.agents/skills/sdd-ux-review/`, `sdd/bin/kb-dominios.py` (novo), `sdd/templates/DEFINE_TEMPLATE.md`, `tests/`, `MANIFEST.txt` | Os 3 primeiros e o `sdd/bin` viajam para o usuário pelo `init`; `tests/` fica no pacote |
| Relevant KB Domains | `nenhum`: o open não tem `sdd/kb/` | A F5 cria o mecanismo, não uma KB do próprio open |
| IaC Patterns | N/A | Sem infraestrutura; release automática pelo `release.yml` |

## Discovery Questions & Answers

| # | Question | Answer | Impact |
|---|---|---|---|
| 1 | Decisão 4 do plano: a pasta da KB é o slot novo `project.kb_dir` ou o caminho fixo `sdd/kb/`? | **`sdd/kb/` fixo** (recomendada) | Nenhum slot novo em `sdd/config.yaml`; `sdd/kb/_index.yaml` e `sdd/kb/<slug>/`. O `DEFINE_TEMPLATE.md` perde o "ou equivalente" |
| 2 | Item G: como a `sdd-define` confere o "KB Domains"? | **Lint novo em `sdd/bin`** (recomendada), contra "modo no `validate_kb.py`" e "só texto" | `sdd/bin/kb-dominios.py <DEFINE>` (0/1/64), passo novo na `sdd-define`, fixtures e teste dos dois lados; os 6 exits do `verify-gate` ficam intocados |
| 3 | Onde mora o `gate.sh` da KB, se no usuário não existe o `tests/` do pacote? | **Na skill, autossuficiente** (recomendada), contra "só no pacote" e "sem gate.sh" | `.agents/skills/sdd-kb/scripts/gate.sh` acha validador e exemplos pela própria pasta e monta as fixturas ruins numa pasta temporária; o `tests/` do pacote o chama |
| 4 | "RULE_MAP apontando o teste que o Verify Gate roda": quanto vira checagem? | **Arquivo existe + lint lista** (recomendada), contra "lint exige o teste no `cmd`" e "só texto" | `validate_kb.py --strict` reprova regra com `implementacao` sem `teste`, ou com `teste` de arquivo inexistente; o `kb-dominios.py` imprime os testes dos domínios normativos citados para a `sdd-define` pô-los no `cmd`. Não casa texto do `cmd` (falso vermelho com `discover`/`npm test`) |
| 5 | Como a entrevista do `ux-review-builder` entra na `sdd-ux-review`? | **Opcional, dentro do passo 1** (recomendada), contra "também um perfil do projeto (`sdd/ux/PUBLICO.md`)" e "sempre, como passo 0" | `references/entrevista-publico.md`; roda só se o DEFINE não diz quem usa e em que contexto, ou se o aluno pedir; o resultado vai para `## User and Context`, sem mudar o template |

## Sample Data Inventory

| Type | Location | Count | Notes |
|---|---|---:|---|
| Input files | `sdd-starter/skills/sdd-kb/assets/example-kb`, `assets/example-kb-normativo` | 2 | KBs canônicas (geral e normativa); devem passar no validador portado |
| Output examples | `sdd-starter/skills/sdd-kb/assets/example-kb-normativo/RULE_MAP.md` | 1 | Gerado por `kb_normativo.py rule-map`; `--check` não pode derivar |
| Ground truth | `sdd-starter/tests/fixtures/kb_good_*` e `kb_bad_*` | 7 | 1 boa e 6 ruins, que viram mutações dentro do `gate.sh` |
| Related code | `sdd-starter/tests/test_sdd_kb_normativo.py` | 62 | Testes por mutação do exemplo normativo, portados para `tests/` |

**How samples will be used:**
- Os exemplos e as 7 fixturas provam o validador dos dois lados (LM-001), no `gate.sh` e no `tests/`.
- Os 62 testes normativos rodam no pacote com os caminhos `.agents/skills/sdd-kb/`.
- Pergunta das amostras: o Roberto escolheu **só as do starter**, em vez de rodar também o validador, só para leitura, na KB real `programa-irpf`. Nada de fora entra na evidência.

## Approaches Explored

### Approach A: Transplante com adaptação mínima, numa release — Recommended

**Description:** a `sdd-kb` do starter entra como 17ª skill quase como está. Mudam a linha de identificação, a camada de conversa (no formato da F4), o `gate.sh` (autossuficiente), a pasta fixa `sdd/kb/` e a checagem de `teste` no `--strict`. Os 62 testes vão para `tests/`. Entram também o `sdd/bin/kb-dominios.py` com o passo novo na `sdd-define` e a entrevista como `references/` da `sdd-ux-review`. Tudo sai numa release, no molde da F2.

**Pros:**
- Reaproveita 465 + 246 linhas já revisadas no starter (inclusive a nota A1, do comentário depois de `perfil:`) e os 62 testes como estão.
- Tudo o que é novo (gate, `--strict`, lint, entrevista) ganha teste dos dois lados.
- Um só ciclo de gate, CI, revisão, OK e release.

**Cons:**
- O `validate_kb.py` sai 2 na falha, e os lints do open saem 1. A diferença fica, porque é porte.
- O push é maior: uma skill nova, mais 2 skills e 1 template mexidos.

**Why Recommended:** é o menor risco de regressão, porque o validador já foi revisado. E mantém a frente numa sessão, como a seção 10 do plano prevê.

### Approach B: As mesmas peças em duas releases

**Description:** primeiro o porte da `sdd-kb` e do gate. Depois, o item G, o RULE_MAP e a UX.

**Pros:**
- O risco de cada push é menor.

**Cons:**
- Dobra o custo fixo de CI, revisão de contexto fresco e OK.
- O item G depende da pasta que o porte cria.

### Approach C: Reescrita no idioma do open

**Description:** o validador vira `sdd/bin/kb-lint.py` (0/1/64), com o `kb_normativo` fundido nele.

**Pros:**
- Saídas uniformes com os outros lints.

**Cons:**
- Reabre um validador de 465 linhas já revisado e perde os 62 testes como estão.
- Põe em `sdd/bin` o que é da skill.

## Selected Approach

| Attribute | Value |
|---|---|
| Chosen | Approach A — transplante com adaptação mínima, numa release |
| User Confirmation | 2026-10-29, na conversa ("A — transplante, 1 release (recomendado)") |
| Reasoning | Reaproveita o que já foi testado e revisado; o que é novo ganha teste dos dois lados; uma só release, como F2–F4 |

## Key Decisions Made

| # | Decision | Rationale | Alternative Rejected |
|---|---|---|---|
| 1 | Pasta da KB fixa em `sdd/kb/` (índice `sdd/kb/_index.yaml`) | A Decisão 4 da frente e a D11 do PORTE pedem o mínimo de slots; a `sdd-kb` é do próprio open; o `DEFINE_TEMPLATE.md` já cita `sdd/kb/` | Slot `project.kb_dir` |
| 2 | "KB Domains" conferido por `sdd/bin/kb-dominios.py <DEFINE>` (0/1/64), no passo novo `### 10. Conferir o KB Domains` da `sdd-define` | Regra 6 do plano (fixture e teste dos dois lados); viaja pelo `init`; funciona sem a `sdd-kb` instalada | Modo `--dominios` no `validate_kb.py`; só texto |
| 3 | `gate.sh` dentro da skill, autossuficiente: as fixturas são mutações temporárias dos exemplos | Roda igual no pacote e no usuário; as fixturas nunca derivam do que a skill entrega | `scripts/kb-gate.sh` só no pacote; sem `gate.sh` |
| 4 | `--strict` reprova `implementacao` sem `teste` e `teste` de arquivo inexistente; o lint lista os testes dos domínios normativos | Prova que o RULE_MAP aponta um teste real, sem falso vermelho com `cmd` por descoberta | Exigir o caminho no `cmd`; só texto |
| 5 | Entrevista de público e referências como `references/entrevista-publico.md`, opcional, no passo 1 da `sdd-ux-review`, gravada em `## User and Context` | Não pergunta o que o DEFINE já responde; não muda o template (a W5 mexe nele) | `sdd/ux/PUBLICO.md` do projeto; entrevista sempre |
| 6 | Amostras: só as do starter | Cobrem os dois perfis e os dois lados; nada de fora na evidência | Rodar também na KB real `programa-irpf` |
| 7 | Abordagem A, numa release | Ver Selected Approach | B (duas releases), C (reescrita) |

## Features Removed (YAGNI)

| Feature Suggested | Reason Removed/Deferred | Can Add Later? |
|---|---|---|
| `UX_STANDARD.md`, a skill `ux-review` gerada, o `UX_REVIEW_TEMPLATE` do builder e o `validate_generated_bundle.py` | O open já tem a `sdd-ux-review` genérica; a F5 só traz a entrevista | Sim |
| `GOVERNANCE.md`, `GENERATION_CONTRACT.md`, `UNIVERSAL_PRINCIPLES.md`, `RUNTIME_COMPATIBILITY.md`, `COMO_FUNCIONA.md`, `evals/` e `manifest.json` do builder | Servem à geração do bundle, que não entra | Sim |
| Slot `project.kb_dir` | Decisão 1 | Sim (frente própria, com OK) |
| Lint que exige o caminho do teste dentro do `cmd` do Verify Gate | Falso vermelho com `cmd` por descoberta | Sim |
| Lint que julga se o domínio citado é relevante para a feature | Julgamento, não fato verificável | Não |
| `--strict` que roda o teste do RULE_MAP | O Verify Gate do DEFINE já roda os testes | N/A |
| `doctor` que valida a KB do projeto | A `sdd-kb` e o `gate.sh` já fazem; o `doctor` confere instalação | Sim |
| Migração de KBs existentes em `.claude/kb/` | Nenhum usuário do open tem KB hoje | Sim |
| `agents/openai.yaml` | O `doctor` o usa para detectar skills do starter | Não |
| Tabela WCAG 2.2 AA e a leitura de `UX_REVIEW_*.md` anteriores (item H) | W5 (F13); o DESIGN anota que o template vai ganhar a tabela | Sim (W5) |
| O `init` criar `sdd/kb/` vazia | A `sdd-kb` cria a pasta na 1ª vez; pasta vazia faria a `sdd-define` oferecer lista vazia | Sim |

## Incremental Validations

| Section | Presented | User Feedback | Adjusted? |
|---|---|---|---|
| Checkpoint 1: o conceito, os 5 componentes (skill `sdd-kb` 2.2.0, `kb-dominios.py`, `sdd-define` 2.3.0, `sdd-ux-review` 2.3.0, testes e contagens) e os cortes YAGNI | Yes | "Confere" | No |
| Checkpoint 2: o fluxo no projeto do aluno, as saídas de `validate_kb.py`, `gate.sh` e `kb-dominios.py`, as falhas da entrevista e os contratos intactos | Yes | "Confere" | No |

## Suggested Requirements for /define

### Problem Statement (Draft)

O open não tem como ensinar a IA o contexto do projeto (leis, normas, processos): não há skill de base de conhecimento, o campo "KB Domains" do DEFINE aceita qualquer texto, o RULE_MAP do perfil normativo não liga uma regra a um teste real e a `sdd-ux-review` não pergunta quem é o público quando o DEFINE não diz.

### Target Users (Draft)

| User | Pain Point |
|---|---|
| Aluno que usa o open (contador, advogado, gestor, sem git nem terminal) | Reexplica o mesmo contexto em toda conversa; uma regra que vale por período fica errada sem aviso |
| Agente que roda a `sdd-define` e a `sdd-design` | Inventa nome de domínio no "KB Domains"; não sabe qual teste cobre qual regra |
| Mantenedor do pacote (Roberto) | Precisa provar dos dois lados que o validador da KB discrimina, no pacote e no projeto do usuário |

### Success Criteria (Draft)

- [ ] `python3 sdd/bin/skill-lint.py --conversa .agents/skills/sdd-*/SKILL.md` sai 0 nas **17** skills, com a `sdd-kb` incluída.
- [ ] `bash .agents/skills/sdd-kb/scripts/gate.sh` sai 0: aceita os 2 exemplos e a fixtura boa, rejeita as 6 fixturas ruins do starter, as normativas e a de teste ausente. Uma fixtura ruim aceita (sabotagem) faz o gate sair 2.
- [ ] Os 62 testes normativos portados passam em `tests/`.
- [ ] `kb-dominios.py` sai 0 para `nenhum` e para nomes que existem em `sdd/kb/`. Sai 1 para nome inventado, placeholder, linha ausente, `nenhum` misturado com nome, e `sdd/kb/` ausente com nome citado. Sai 64 para uso errado.
- [ ] `validate_kb.py --strict` reprova `implementacao` sem `teste` e `teste` de arquivo inexistente, e aceita teste que existe.
- [ ] Os 388 testes de antes continuam verdes no piso, e a contagem de skills passa de 16 para 17 de propósito.
- [ ] `check-versions --base v2.2.5 --base-obrigatoria` VERDE, com `sdd-define` e `sdd-ux-review` acima da base.

### Constraints Identified

- bash 3.2 e Python 3.9 stdlib. Sem `mapfile`, `declare -A` ou `${x^^}`. Nada de `rm -rf` com variável sem `"${X:?}"`.
- A camada da F4 continua contrato testado:
  - a seção, o `como-falar.md` com pergunta válida e o bloco comum idêntico (`FRASES`);
  - a linha de identificação com a versão do frontmatter, "uma vez só, antes do Status".
- `tests/test_agnostico.py`: nenhum nome de ferramenta de um agente só no texto portado.
- O `publish-gate` não aceita e-mail fora de `example.*`, CPF/CNPJ, telefone ou 11+ dígitos literais.
- Contratos que não mudam:
  - os 6 exits do `verify-gate.sh`, as fixtures de `sdd/fixtures/` e o `playbook-lint.sh --self-test` 0;
  - `skill-lint`/`design-lint`/`handoff-lint` com 0/1/64;
  - o bloco do OK da `sdd-release`;
  - o passo 4 da `sdd-iterate`.
- Na `sdd-define`, os passos 1–9 ficam iguais. Na `sdd-ux-review`, ficam os passos 1–8, e só a entrada nova entra (o `comandos-intactos` declara as 2 exceções).
- A `sdd-kb` não traz `agents/openai.yaml`, o texto `sdd-starter` nem `tests/` dentro da skill (`Portadas`).
- Todo arquivo novo entra no `MANIFEST.txt`, em ordem `LC_ALL=C`. `git add` vai por nome, e os artefatos de `sdd/features|handoffs|reports|reviews` nunca entram no commit.

### Out of Scope (Confirmed)

- A tabela WCAG e a leitura de `UX_REVIEW_*.md` anteriores (W5).
- O encadeamento e as classes D1–D5 (F9).
- O fail-open do `report-lint` (F7).
- Docs e guia do aluno (F6).
- O sdd-starter e o repositório privado.
- Os itens cortados pela YAGNI acima.

## Session Summary

| Metric | Value |
|---|---:|
| Questions Asked | 6 |
| Approaches Explored | 3 |
| Features Removed (YAGNI) | 11 |
| Validations Completed | 2 |

## Next Step

Execute o **SDD Define by RDD**.
