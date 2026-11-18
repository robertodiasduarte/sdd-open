# Comparação skill a skill, starter (tag v1.5.18) × Open (feat/f17c-starter-etapa3) — sdd-define, sdd-design, sdd-build

Agente em contexto novo, só leitura, 2026-11-13.

Caminhos abreviados:
- **ST** = `/Users/robertoduarte/rdd-worktrees/sdd-starter-f17c-ref/skills/<skill>/` (tag `v1.5.18`, conferida com `git describe --tags`).
- **OP** = `/Users/robertoduarte/rdd-worktrees/sdd-open-f17c-starter-etapa3/.agents/skills/<skill>/`.
- **OPT** = `/Users/robertoduarte/rdd-worktrees/sdd-open-f17c-starter-etapa3/sdd/templates/` (molde e fragmentos que só existem num projeto com o `init`).
- **ST-raiz** = `/Users/robertoduarte/rdd-worktrees/sdd-starter-f17c-ref/`.

Classes: (A) o Open cobre de outro jeito · (B) o Open trocou de propósito · (C) falta no Open e vale trazer · (D) próprio do
starter. "Fato" = lido, com arquivo:linha. "(inferência)" = conclusão minha, não escrita em lugar nenhum.

Tamanhos lidos inteiros: ST define 1454 linhas em 11 arquivos (SKILL 407, 5 references, 2 assets, script, teste, openai.yaml);
OP define 570 (SKILL 414, como-falar 60, cartografo 96). ST design 1243 (SKILL 467, 4 references, template, script, openai.yaml;
**sem `tests/`**); OP design 334 (SKILL 282, como-falar 52). ST build 1867 (SKILL 496, 7 references, 3 assets, script, teste,
openai.yaml); OP build 766 (SKILL 333, 4 references). Também li, do Open, os moldes e fragmentos que as três citam:
`OPT/DEFINE_TEMPLATE.md`, `OPT/DESIGN_TEMPLATE.md`, `OPT/BUILD_REPORT_TEMPLATE.md` (estrutura), `OPT/fragments/EARS.md`,
`CLARIFY.md`, `VERIFY_GATE.md` (inteiros) e o começo de `LLM_PROMPTS_DESIGN.md`, `PERGUNTA_DECISAO.md`, `RESUMO_ETAPA.md`,
`EVIDENCIA.md`, `WORKER_BRIEF.md`, `ADVISOR_CONSULT.md`.

---

## 0. Vale para as três

- (D) `agents/openai.yaml` nas três do starter (ST/sdd-define/agents/openai.yaml:1-4; ST/sdd-design/agents/openai.yaml:1-14;
  ST/sdd-build/agents/openai.yaml:1-4); nenhuma do Open tem. O "display_name" é "SDD Define/Design/Build by RDD", o mesmo
  nome que o handoff de cada documento usa.
- (D) Handoff de documento por **nome de produto, sem comando nem caminho**: "Execute o **SDD Design by RDD**." /
  "…**SDD Build by RDD**." / "…**SDD Handoff by RDD**." e a regra "não acrescentar slash command, caminho, upload…"
  (ST/sdd-define/SKILL.md:323-333; ST/sdd-design/SKILL.md:409-419; ST/sdd-build/SKILL.md:482-492). O Open fecha com
  `/sdd-ux-review …`, `/sdd-design …`, `/sdd-build …`, `/sdd-release …` e caminhos `sdd/features/…` (OP/sdd-define/SKILL.md:394-396;
  OP/sdd-design/SKILL.md:263; OP/sdd-build/SKILL.md:314). Para a web, o do starter funciona sem barra e sem pasta; a F17b já
  resolveu o mesmo problema na governança com "a skill `sdd-design`, com o DEFINE atualizado (na web, mande o documento junto
  com o pedido)" (`scripts/starter/trocas/sdd-governanca.md`, troca do "Próximo passo"). Classe (B/C): trazer o formato da F17b.
- (D) Os três documentos do starter gravam em `sdd/` plano (ou `.claude/sdd/` se já existir) e entregam `.md` para download
  sem filesystem (ST/sdd-define/SKILL.md:310-314; ST/sdd-design/SKILL.md:400-407; ST/sdd-build/SKILL.md:447-450).
- (C) **Postura "sem acesso, não finja"** explícita nas três do starter: "Não exigir internet. Não presumir acesso ao
  repositório, filesystem, CI, banco, APIs ou comandos" (ST/sdd-define/SKILL.md:68); "Não alegar ter inspecionado
  repositório…" (ST/sdd-design/SKILL.md:55); "Não fingir um Build completo somente a partir dos arquivos de especificação"
  (ST/sdd-build/SKILL.md:88). O Open declara `compatibility: Requer bash >= 3.2 e git >= 2.20` nas três (OP/sdd-define/SKILL.md:4;
  OP/sdd-design/SKILL.md:4; OP/sdd-build/SKILL.md:4) e não tem frase equivalente (grep por "fingir|finja|inventar|pseudo" nas três
  pastas do Open: só 2 ocorrências, ambas no build, sobre prompt e senha — OP/sdd-build/SKILL.md:146; OP/sdd-build/references/aplicar-migration.md:165).
- (A) O formato "Como falar com o aluno" (Status · O que foi feito · Agora · Sua decisão · Próximo passo; parada com ⏸️) é o
  mesmo nos dois lados; o Open acrescenta "sempre **não sei**, nunca **Outro**", "até 100 caracteres" e o resumo de etapa
  no fecho (OP/sdd-define/SKILL.md:39-61), e as marcas `[D2 · muda o produto]` / `[auto · de rotina]`
  (OPT/fragments/PERGUNTA_DECISAO.md:41-56). O molde PERGUNTA_DECISAO e o RESUMO_ETAPA já existem em
  `scripts/starter/trocas/_moldes/` (fato: `ls`).

---

## 1. O que o starter tem melhor para quem está na web

### 1.1 sdd-define

| # | Item | Classe | ST | OP |
|---|---|---|---|---|
| D1 | Verify Gate da **primeira vez**: uma pergunta só, "existe um comando que devolve 0 quando funciona?"; sim → `test`; não → `manual-ux` com 3 a 5 frases "Eu abri … e vi …"; saída de LLM também cabe em `test` | **C** (forte) | SKILL.md:274-275; references/VERIFY_GATE.md:7-13 | o Open pergunta o comando só com slot vazio (SKILL.md:205-206); o fragmento não tem a fórmula "Eu abri … e vi …" (OPT/fragments/VERIFY_GATE.md:79-80, 99-100) |
| D2 | "O agente não escolhe `manual-ux` por não saber o comando: faz a pergunta" / `manual-ux` "nunca como atalho para não perguntar" | **C** | references/VERIFY_GATE.md:59; SKILL.md:282; define-protocol.md:108 | ausente (OP só recusa "UX marcada `test` só para passar técnico", SKILL.md:212-213) |
| D3 | **Exemplo pronto** de DEFINE (CPF), com o gate `test` e a troca para `manual-ux` | **C** | assets/DEFINE_EXEMPLO.md:1-165 | nenhum exemplo na skill; o molde do Open usa `npm test -- src/{modulo}.test.ts` (OPT/DEFINE_TEMPLATE.md:107-114) |
| D4 | Molde limpo, só o necessário | **C** | assets/DEFINE_TEMPLATE.md:1-157 | molde com restos de outro domínio: `{src/ \| functions/ \| gen/ \| deploy/}`, `Terraform/Terragrunt`, WAF×runner/SSH, "define-agent" (OPT/DEFINE_TEMPLATE.md:124-125, 157, 159, 233); fragmentos citam `/define`, `/build`, `ehMatriz`, "v5.0/v5.1", PESQUISA_FRAMEWORKS (OPT/fragments/EARS.md:21, 51, 64-66; CLARIFY.md:17) |
| D5 | **Precedência das fontes** (resposta mais recente > Brainstorm validado > fato > contexto > inferência rotulada) e "nunca promover hipótese a requisito" | **C** | references/define-protocol.md:22-30; SKILL.md:131-136, 151 | ausente (grep "prevalece\|mais recente\|precedên" nas três skills e nos fragmentos: 0) |
| D6 | **Tratamento de exceções**: Brainstorm ausente/incompleto/contraditório, usuário muda decisão, encerrar com pendência = rascunho `Needs Clarification`, feature sem interface (UX N/A), feature só UX | **C** | SKILL.md:362-374 | parcial: dúvida aberta deixa a trava (SKILL.md:248-249); o resto ausente |
| D7 | "Sem acesso ao código: não alegar que caminhos, testes ou infraestrutura foram inspecionados" | **C** | SKILL.md:371 | ausente |
| D8 | Mapa de extração Brainstorm → seções do DEFINE | C (baixo) | references/define-protocol.md:32-44 | só a tabela de tipo de entrada (SKILL.md:131-138) |
| D9 | Lista do que não declarar `Ready for Design` | A | SKILL.md:316-321 | Quality Gate (SKILL.md:344-359) |
| D10 | LLM Prompts: 1 sinal fraco e intenção ambígua ⇒ **pergunta** | B | SKILL.md:250 | 1 fraco ⇒ `true` "conservador", sem pergunta; tabela de pesos (SKILL.md:186-191) — o Open é melhor aqui |
| D11 | Regras EARS mais duras (≤~10 ATs; While/If/Where considerados; AT de UX visual proibido; rastreabilidade AT→gate) | A (ganho do Open) | EARS.md:1-30 | SKILL.md:154-164; OPT/fragments/EARS.md:10-27 |
| D12 | Convenção de menção do marcador (fora de cerca = ativo) | A (ganho do Open) | CLARIFY.md:7-13 | OPT/fragments/CLARIFY.md:21-25 |
| D13 | Governança: o starter **sugere** a skill avulsa | B | SKILL.md:43 | passo 11 sempre, com revisor fresco e trava no gate (SKILL.md:234-324) |
| D14 | Segurança no Define | — (falta no starter) | ausente | passo 12 (SKILL.md:326-342); a `sdd-seguranca` já é gerada no starter |
| D15 | Contradição interna do starter: o protocolo termina em `HANDOFF_TO_UX_REVIEW`, a skill manda para o Design | D (defeito) | references/define-protocol.md:18 × SKILL.md:31, 330 | — |

### 1.2 sdd-design

| # | Item | Classe | ST | OP |
|---|---|---|---|---|
| G1 | **Sem código acessível**: não inventar caminho, biblioteca ou agente; perguntar a stack e a estrutura mínima; greenfield só depois de o aluno confirmar a stack | **C** (forte) | SKILL.md:153-168, 459; references/design-protocol.md:92-101 | "Explore o código" sem alternativa (SKILL.md:69-70) |
| G2 | **Hierarquia das fontes** (requisito: resposta > UX Review > DEFINE > Brainstorm; fato técnico: código > doc > resposta > inferência marcada) e "conflito ⇒ perguntar" | **C** | SKILL.md:57-73 | ausente |
| G3 | Lê o **Brainstorm** (intenção, YAGNI, alternativas rejeitadas) | C | SKILL.md:20, 40, 111-118; design-protocol.md:30-38 | entrada só o DEFINE (SKILL.md:62, 68); o exemplo do como-falar diz "Li o brainstorm e o DEFINE" (references/como-falar.md:37), a skill não manda ler |
| G4 | **Prontidão da entrada** (DEFINE fechado, sem contradição, `LLM Prompts` literal, Verify Gate, Out of Scope) antes de desenhar | C | SKILL.md:142-151 | ausente |
| G5 | Regras do **File Manifest**: caminho real ou coerente com a stack confirmada, "não fingir observado", incluir testes/config/migrations, `(general)` e `Agent Discovery: Not available` | **C** | SKILL.md:234-255 | 3 linhas (SKILL.md:123-129); molde com `@{agent-name}`, "Cloud Run patterns", "Pydantic + LLM output" (OPT/DESIGN_TEMPLATE.md:78-132) |
| G6 | **Snippets**: com API desconhecida, pseudocódigo explícito ou pergunta, nunca pseudo-API inventada | C | references/design-protocol.md:139-148 | ausente |
| G7 | Integração com falha/retry; erro com detecção e observabilidade; configuração com "sensível?" | C | SKILL.md:303-360; assets/DESIGN_TEMPLATE.md:115-163 | molde mais pobre (OPT/DESIGN_TEMPLATE.md:192-227, 245-251) |
| G8 | Seções **Requirements Traceability** e **Risks and Mitigations** | **C** | assets/DESIGN_TEMPLATE.md:167-179; o lint exige a 1ª (scripts/validate_design.py:192-194) | ausentes do molde (grep "Traceability\|Risks" em OPT/DESIGN_TEMPLATE.md: 0) |
| G9 | Lista de **consistência cruzada** (componente no diagrama, manifest cobre componentes, testes cobrem ATs, Out of Scope fora do plano) | C | SKILL.md:362-373 | parcial: `design-lint.py` (SKILL.md:191-193) — script do init |
| G10 | **Exceções** (Brainstorm/DEFINE ausente, conflito UX×DEFINE, sem contexto de código, manifest não concretizável, encerrar com pendência ⇒ Draft) | C | SKILL.md:452-463 | ausente |
| G11 | Não sobrescrever em silêncio um DESIGN existente | C | SKILL.md:404 | ausente (grep "sobrescrev" nas 3 skills: só a do init, OP/sdd-build/SKILL.md:159) |
| G12 | Metadata com BRAINSTORM, DEFINE, UX REVIEW e LLM Prompts | C (baixo) | assets/DESIGN_TEMPLATE.md:12-15 | só DEFINE (OPT/DESIGN_TEMPLATE.md:12) |
| G13 | Molde neutro (sem Python/GCP) | **C** | assets/DESIGN_TEMPLATE.md | snippets `python`, "Cloud Logging", "pytest 80%" (OPT/DESIGN_TEMPLATE.md:149-166, 205-207, 249-251) |
| G14 | Re-checagem de LLM Prompts com 3 saídas | A | references/llm-prompts.md:9-26 | SKILL.md:90-93 |
| G15 | Contrato por prompt, `one-shot`/`loop` | A (o Open é mais rico; molde já em `_moldes/LLM_PROMPTS_DESIGN.md`) | references/llm-prompts.md:34-76 | SKILL.md:160-167; OPT/fragments/LLM_PROMPTS_DESIGN.md |
| G16 | `loop` × `one-shot` na dúvida ⇒ **pergunta** | B | references/llm-prompts.md:58 | na dúvida, `loop` (OPT/fragments/LLM_PROMPTS_DESIGN.md:24-25) |
| G17 | Revisão externa **só se houver** (advisor-review com ledger APPLIED/REBUTTED) | D/B | SKILL.md:34, 463; references/advisor-review.md:1-34 | review adversarial recomendado, por script (SKILL.md:196-221) |
| G18 | Segurança: lista livre | B | SKILL.md:348-354 | `## Segurança` com 5 itens fixos e o "evitar" do catálogo (SKILL.md:169-176) — ganho do Open |

### 1.3 sdd-build

| # | Item | Classe | ST | OP |
|---|---|---|---|---|
| B1 | **Drift geral**, 6 perguntas antes de cada item (arquivo não previsto, decisão arquitetural, fora de escopo, YAGNI reintroduzido, contrato real contradiz, prompt não inventariado) ⇒ parar e perguntar, registrar | **C** (forte) | SKILL.md:263-282 | só o drift de **prompt**, por `prompt-drift-scan.sh` (SKILL.md:162-168); grep "YAGNI\|fora de escopo\|não previsto" no build do Open: 0 |
| B2 | **Leitura do `cmd` cru sem runner**: `exit 0` ⇒ 0 verde, qualquer outro vermelho (inclusive 4 e 5 do pytest); `exit N`; `contains:`; ferramenta não rodou ⇒ inconclusivo; "o starter não traz runner" | **C** (forte — é a "prova sem script") | SKILL.md:355-366; references/verify-gate.md:23-53 | só a tabela do `verify-gate.sh` (SKILL.md:189-198) |
| B3 | "Nunca instalar pacote nem fazer mudança destrutiva só para o gate rodar, sem consentimento" | C | references/verify-gate.md:40 | ausente |
| B4 | **Modo que a plataforma não executa não é oferecido**; ralph sem contexto fresco real não se chama ralph | **C** | SKILL.md:212-213; references/execution-modes.md:7, 44, 54, 60; como-falar.md:51-52 | ausente (OP/sdd-build/SKILL.md:114-123) |
| B5 | Escada de retry **sem** despacho fresco: reduzir ao FIX brief, declarar a limitação, "não fingir que um novo contexto foi criado" | **C** | SKILL.md:305-308; references/retry-and-advisor.md:23 | a escada exige redispatch fresco (SKILL.md:172-176; references/modos-e-retry.md:40-54) |
| B6 | **Sem git**: seguir só se seguro e registrar no relatório | C | SKILL.md:172-174 | o Open supõe git (commit antes de revisão, `avaliador-guard.sh`: SKILL.md:100-101, 211, 229) |
| B7 | **Hierarquia de autoridade** (comportamento × implementação) e "nunca usar 'o código já faz assim' para invalidar requisito" | C | SKILL.md:99-115; references/build-protocol.md:30-39 | ausente |
| B8 | **Regra de escrita**: só caminhos do manifest + exceções (relatório, progresso, artefato aprovado) | C | references/build-protocol.md:41-50 | só "mudança cirúrgica" (SKILL.md:127) |
| B9 | Molde do relatório com **Mode Selection** (sinais, recomendação, decisão do usuário), **Drift Detected**, Verify Gate em tabela, **Manual UX Receipt** (quem, data, resultado, notas), Complementary Checks, Deviations, Blockers e Next Step só em COMPLETE | **C** (e defeito do Open) | assets/BUILD_REPORT_TEMPLATE.md:19-35, 81-127, 169-200 | a skill exige "Seleção de modo" e "Drift detectado" (SKILL.md:259-262), mas o molde não tem nenhuma das duas seções (grep "Sele\|Drift" em OPT/BUILD_REPORT_TEMPLATE.md: 0); molde com `ruff`/`mypy`/`pytest` e `/release`, `/iterate` (OPT/BUILD_REPORT_TEMPLATE.md:117-133, 270-276) |
| B10 | Build bloqueado: `Status: Blocked`, sem o handoff de conclusão, com a ação de desbloqueio | C | SKILL.md:420-428 | parcial (molde: "If Blocked: … `/build`", OPT/BUILD_REPORT_TEMPLATE.md:274) |
| B11 | Não sobrescrever artefato histórico sem avisar | C | SKILL.md:452 | ausente |
| B12 | Recibo manual-ux com 4 campos | A | references/verify-gate.md:55-65 | `recibo: nome AAAA-MM-DD` (SKILL.md:196, 249) |
| B13 | Segurança/prompts nunca para worker barato | A | SKILL.md:469; execution-modes.md:62-66 | references/modos-e-retry.md:15-18 |
| B14 | Migration: `- banco:` em `sdd/ambiente.md` | B | SKILL.md:342, 472; references/aplicar-migration.md:69-76 | removido: o registro vai só para `## Migrations aplicadas` (OP references/aplicar-migration.md:69-72) — alinhado com a release gerada na F17b |
| B15 | Prova de migration com valor de teste | — (ganho do Open) | `fn_cliente_valida_cnpj('<CNPJ>')` (references/aplicar-migration.md:174-175) | "valor de teste … nunca o documento de um cliente real" (OP references/aplicar-migration.md:195-197) |
| B16 | Templates de ralph/briefs dentro da skill | D | assets/PROGRESS_TEMPLATE.md; assets/WORKER_BRIEF_TEMPLATE.md | `sdd/reports/progress/PROGRESS_{F}.md` sem molde; `OPT/fragments/WORKER_BRIEF.md` |
| B17 | Contradição interna do starter: protocolo termina em `HANDOFF_TO_RELEASE` e "handoff de Release", o relatório manda "SDD Handoff by RDD"; docs dizem "publique com a sdd-release" | D (defeito) | references/build-protocol.md:22 e SKILL.md:422 × SKILL.md:36, 489; ST-raiz/docs/workflow.pt-BR.md:48 | — |
| B18 | "Entradas opcionais: `sdd.config.yaml`" (arquivo que nenhuma skill cria) | D (defeito) | SKILL.md:93 | — |

---

## 2. Citações a arquivos do `init` no texto do Open (SKILL.md + references)

Comando (rodado em `OP/..`, isto é, `.agents/skills/`):

```bash
P='sdd/bin/|sdd/templates/|sdd/hooks/|sdd/review/|sdd/patterns/|playbook|invariants|WORKFLOW_CONTRACTS|sdd/config\.yaml'
for s in sdd-define sdd-design sdd-build; do
  for f in $(find $s -name '*.md' | sort); do
    printf "%-45s linhas=%3s ocorr=%3s\n" $f $(grep -cE "$P" $f) $(grep -oE "$P" $f | wc -l); done
  grep -ohE "$P" $(find $s -name '*.md') | sort | uniq -c | sort -rn; done
```

| Skill | Arquivo | linhas com citação | ocorrências |
|---|---|---:|---:|
| sdd-define | SKILL.md | 27 | 27 |
| | references/cartografo.md | 6 | 9 |
| | references/como-falar.md | 1 | 1 |
| | **total** | **34** | **37** |
| sdd-design | SKILL.md | 26 | 30 |
| | references/como-falar.md | 4 | 4 |
| | **total** | **30** | **34** |
| sdd-build | SKILL.md | 33 | 35 |
| | references/aplicar-migration.md | 4 | 4 |
| | references/como-falar.md | 2 | 2 |
| | references/contexto-fresco.md | 1 | 1 |
| | references/modos-e-retry.md | 1 | 1 |
| | **total** | **41** | **43** |

Por padrão: define `sdd/bin/` 21 · `sdd/templates/` 6 · `sdd/patterns/` 4 · `playbook` 4 · `sdd/config.yaml` 1 ·
`WORKFLOW_CONTRACTS` 1. Design `sdd/bin/` 13 · `playbook` 10 · `sdd/templates/` 7 · `sdd/patterns/` 2 · `sdd/config.yaml` 2.
Build `sdd/bin/` 25 · `sdd/templates/` 9 · `playbook` 5 · `sdd/config.yaml` 3 · `sdd/review/` 1. `sdd/hooks/` e
`invariants`: 0 nas três. (O padrão `playbook` também conta a palavra solta, ex. "o playbook do projeto".)

Arquivos distintos citados (segundo comando, `grep -ohE "sdd/bin/[A-Za-z0-9_./-]+|sdd/templates/…|sdd/review/…|sdd/patterns/…|sdd/fixtures/…|{{SLOT}}|AGENTS.md|sdd/kb/…|.agents/skills/…"`):

- **define**: `sdd/bin/` contexto-lint.sh (6), governanca-fronteira.sh (5), verify-gate.sh (3), sdd-fluxo.sh (3), playbook-lint.sh,
  kb-dominios.py, governanca-bloco.py, `gates/gate-{feature}.sh`; `sdd/templates/` DEFINE_TEMPLATE.md, fragments/PERGUNTA_DECISAO.md (2),
  RESUMO_ETAPA.md, FLUXO_ENCADEADO.md, EARS.md (+ CLARIFY.md e VERIFY_GATE.md citados só pelo nome, SKILL.md:73);
  `sdd/patterns/dominio.md` (3), `sdd/patterns/README.md`; `sdd/fixtures/contexto/valido-completo.md`; `sdd/kb/` (5) e
  `sdd/kb/_index.yaml`; slots `{{TEST_CMD}}`, `{{TYPECHECK_CMD}}`; `AGENTS.md`; outras skills por caminho de instalação:
  `.agents/skills/sdd-governanca` (2), `.agents/skills/sdd-seguranca`.
- **design**: `sdd/bin/` sdd-fluxo.sh (6), playbook-lint.sh (2), patterns-lint.sh, docs-extract-decisions.sh, design-lint.py,
  contexto-lint.sh, adversarial-review.sh; `sdd/templates/` DESIGN_TEMPLATE.md, fragments PERGUNTA_DECISAO (2), RESUMO_ETAPA,
  LLM_PROMPTS_DESIGN, FLUXO_ENCADEADO, ADVISOR_CONSULT; `sdd/patterns/README.md`; `AGENTS.md`.
- **build**: `sdd/bin/` sdd-fluxo.sh (5), verify-gate.sh (3), slot.sh (2), report-lint.py (2), prompt-drift-scan.sh (2),
  avaliador-guard.sh (2), adversarial-review.sh (2), test-baseline.sh, seguranca-varredura.sh, playbook-lint.sh,
  ledger-revisao-lint.sh, gate-baseline.sh, eval-revisores.sh; `sdd/templates/` LEDGER_REVISAO_TEMPLATE.md, fragments
  PERGUNTA_DECISAO (2), WORKER_BRIEF, RESUMO_ETAPA, LLM_PROMPTS_BUILD_REPORT, FLUXO_ENCADEADO, EVIDENCIA, ADVISOR_CONSULT;
  `sdd/review/CRITERIO_DANO.md`; slots `{{TEST_CMD}}`, `{{TYPECHECK_CMD}}`, `{{LINT_CMD}}`; `AGENTS.md`.

Fato adicional: o `description` do frontmatter das três cita `sdd/features/` ou `sdd/reports/` e o `compatibility` cita `sdd/bin/`
(OP/sdd-define/SKILL.md:3-4; OP/sdd-design/SKILL.md:3-4; OP/sdd-build/SKILL.md:3-4) — estão contados acima.

---

## 3. Tabelas de paradas

"Parada" = pergunta obrigatória ao aluno, ponto de aprovação, comando que o aluno roda, condição que bloqueia o fim da fase.
Comando que **o agente** roda e que bloqueia (lint, gate) entra como "condição". "só no Open?" = **sim** quando o starter
v1.5.18 não tem nada equivalente; cada **sim** precisa do OK do mantenedor para ir à web.

### 3.1 sdd-define

| Parada | starter v1.5.18 | Open | só no Open? |
|---|---|---|---|
| Brainstorm ausente ou ilegível: pedir o arquivo antes de escrever | SKILL.md:59, 364 | não: aceita notas ou "pedido direto" (SKILL.md:65) | não (só no starter) |
| Brainstorm contraditório: perguntar qual decisão prevalece | SKILL.md:366 | ausente | não (só no starter) |
| Perguntas de clarificação, uma principal por vez, no máximo 5 por rodada, múltipla escolha com a recomendada primeiro | SKILL.md:206-236; CLARIFY.md:31-43 | SKILL.md:171-177; OPT/fragments/CLARIFY.md:43-48 | não |
| Clarity Score < 12/15: continuar perguntando, não marcar pronto | SKILL.md:202-204, 368 | SKILL.md:166-169 | não |
| Métrica sem número: perguntar o alvo, não fabricar | SKILL.md:165-167, 369 | recusa adjetivo sem número (SKILL.md:160) | não |
| EARS reprovado (sem padrão, sem If/Then com gatilho plausível, bugfix sem `shall continue to`) bloqueia | SKILL.md:173-183, 319 | SKILL.md:154-160 | não |
| **Recusa extra do EARS: mais de ~10 ATs** | ausente | SKILL.md:162 | **sim** |
| **Recusa extra: While / If–Then / Where não "considerados" (AT ou N.A. em 1 linha)** | ausente | SKILL.md:161 | **sim** |
| **Recusa extra: AT de UX visual** | ausente | SKILL.md:163 | **sim** |
| **Recusa extra: AT sem `kind` na coluna Gate ou sem cobertura no `cmd`** | ausente (o lint só exige keyword EARS, validate_define.py:88-95) | SKILL.md:164 | **sim** |
| LLM Prompts: 1 sinal fraco e intenção ambígua ⇒ perguntar | SKILL.md:250 | não pergunta: `true` conservador (SKILL.md:190) | não (só no starter) |
| Verify Gate: pergunta "existe um comando que devolve 0?" (1ª vez) / qual comando verifica | SKILL.md:274-282; VERIFY_GATE.md:9-11 | pergunta só com slot `{{TEST_CMD}}` vazio (SKILL.md:205-206) | não |
| Verify Gate ausente ou incompleto: DEFINE não fica pronto | SKILL.md:284, 321 | "recuse DEFINE sem gate" (SKILL.md:193) | não |
| Lint estrutural passa (agente: `python scripts/validate_define.py`, "quando houver filesystem e Python") | SKILL.md:295-303, 358 | substituído por `verify-gate.sh --print` sem erro 64 (SKILL.md:208-210, 353) | não (troca de ferramenta) |
| **Gate composto: script `sdd/bin/gates/gate-{feature}.sh`, um bloco por AT, com baseline vermelho** | ausente | SKILL.md:215-218 | **sim** |
| Open Questions sem questão bloqueante / zero marcadores ativos | SKILL.md:286-293; CLARIFY.md:45-47 | marcador ativo ⇒ `verify-gate.sh` sai 5 (SKILL.md:177-178, 350) | não |
| Aluno quer encerrar com pendência: só rascunho `Needs Clarification`, sem handoff | SKILL.md:372 | dúvida aberta deixa a trava de governança e a linha `pendente — clarificação aberta` (SKILL.md:247-249) | não |
| **Cartógrafo: decisão `[auto · de rotina]` "Mapeio as regras do domínio antes da spec?" (gerar · seguir sem · não sei)** | ausente | SKILL.md:83-94 | **sim** |
| **Cartógrafo sem subagente: ⏸️ parada 1 de 2 — o aluno abre sessão nova e cola o bloco `<<<CONTEXTO`** (exit 40 do `sdd-fluxo.sh despachar`) | ausente | SKILL.md:110-114; references/cartografo.md:7-8 | **sim** |
| **Cartógrafo: mapa vencido ⇒ oferecer gerar de novo** | ausente | SKILL.md:98-100 | **sim** |
| **Mais de 2 domínios ⇒ propor dividir a feature** | ausente | SKILL.md:127-129 | **sim** |
| **KB Domains: `kb-dominios.py` sai 0 (só pastas de `sdd/kb/` ou `nenhum`), senão corrigir antes de entregar** | ausente (o template aceita `{domains / N/A}`, DEFINE_TEMPLATE.md:112) | SKILL.md:145-148, 226-232, 354 | **sim** |
| **Governança, item 1: trava gravada no DEFINE antes do despacho (marcador + linha `pendente`)** | ausente (só sugere a skill avulsa, SKILL.md:43) | SKILL.md:243-250 | **sim** |
| **Governança: revisor fresco; sem subagente, ⏸️ parada 2 de 2 — sessão nova e colar o bloco `<<<GOVERNANCA`** | ausente | SKILL.md:251-271 | **sim** |
| **Governança `PADRAO_AUSENTE`: 5 perguntas `[D2]`, uma vez por projeto** | ausente na define (existem na skill avulsa gerada) | SKILL.md:294-299 | **sim** (na define) |
| **Governança: uma pergunta `[D2]` por lacuna (aplicar · recusar · adiar)** | ausente na define | SKILL.md:303-306 | **sim** (na define) |
| **Governança: `prova_script` gravado em `sdd/tests/governanca/<F>_<Gnn>.sql` e `psql …` acrescentado ao `cmd`; só banco de produção ⇒ `prova_manual`** | ausente | SKILL.md:307-312 | **sim** |
| **Governança, 2ª falha: 🛑 "o build e a release param" com 2 saídas (sessão nova só dos passos 11-12 · dispensar com motivo e nome)** | ausente | SKILL.md:316-321 | **sim** |
| **Condição de fim: linha `Governança` com valor final (`N.A. — …`, `GOVERNANCA_REVIEW_…`, `dispensada — …`) e sem marcador** | ausente | SKILL.md:323-324, 356 | **sim** |
| **Segurança: modo Define da `sdd-seguranca`, até 5 itens por rodada, uma pergunta por item; aplicado vira AT no gate** | ausente | SKILL.md:332-338 | **sim** |
| **Condição de fim: linha `Segurança` escrita** | ausente | SKILL.md:339-342, 357 | **sim** |
| **Linha `CONTEXTO de domínio` preenchida** | ausente | SKILL.md:124-126, 355 | **sim** |
| **Próximo passo: UX review se há interface; pular exige motivo registrado no DEFINE** | ausente (Next Step fixo no Design, SKILL.md:330) | SKILL.md:394-396 | **sim** |
| **Fluxo encadeado: `sdd-fluxo.sh seguir`; "Pare" desliga** | ausente | SKILL.md:398-410 | **sim** (mantenedor) |

### 3.2 sdd-design

| Parada | starter v1.5.18 | Open | só no Open? |
|---|---|---|---|
| Brainstorm ausente: pedir o arquivo | SKILL.md:454 | não lê o Brainstorm (SKILL.md:62, 68) | não (só no starter) |
| DEFINE ausente: pedir; não desenhar só do Brainstorm | SKILL.md:455 | entrada é o DEFINE (SKILL.md:62) | não |
| Prontidão da entrada (DEFINE fechado, sem contradição, flag literal, gate, Out of Scope): perguntar se bloqueia | SKILL.md:142-151 | ausente | não (só no starter) |
| Sem código acessível: perguntar stack e estrutura; greenfield só com confirmação | SKILL.md:165-168, 459 | ausente | não (só no starter) |
| Conflito entre fontes (ou UX Review × DEFINE): perguntar | SKILL.md:73, 457 | ausente | não (só no starter) |
| Decisões técnicas bloqueantes: uma pergunta principal por mensagem, 2-4 opções | SKILL.md:170-187; design-protocol.md:70-90 | etapa 2 "Decisões" com exemplo `[D2]` (references/como-falar.md:40-50) | não |
| LLM Prompts ausente/ambíguo: perguntar; `false` com sinais: 3 opções | SKILL.md:458; references/llm-prompts.md:7, 21-26 | SKILL.md:90-93 | não |
| **…com o encadeamento ligado, essas perguntas viram `[auto]` (ausente ⇒ `true`)** | ausente | SKILL.md:93-98 | **sim** (mantenedor) |
| `loop` × `one-shot` na dúvida: perguntar | references/llm-prompts.md:58 | não pergunta: na dúvida, `loop` (OPT/fragments/LLM_PROMPTS_DESIGN.md:24-25) | não (só no starter) |
| Biblioteca ou serviço não confirmado e bloqueante: alternativas e pergunta | SKILL.md:461 | ausente | não (só no starter) |
| Lint estrutural passa (`validate_design.py`, quando há filesystem e Python) | SKILL.md:385-393, 448 | `design-lint.py` no arquivo gravado (SKILL.md:189-194) | não (troca de ferramenta) |
| Sem placeholder, TBD ou clarificação em `Ready for Build` | SKILL.md:383, 447 | `design-lint.py` "nenhum placeholder" (SKILL.md:191-193) | não |
| Não sobrescrever DESIGN existente em silêncio | SKILL.md:404 | ausente | não (só no starter) |
| Encerrar com pendência ⇒ `Draft` / `Needs Clarification` | SKILL.md:462 | ausente | não (só no starter) |
| Revisão externa formal: só se houver; toda nota APPLIED/REBUTTED | SKILL.md:34, 463; references/advisor-review.md:21-34 | toda nota APLICADA/REBATIDA_EVIDENCIA/REBATIDA_ESCOPO (SKILL.md:212-214) | não |
| **Papel de surface em aberto no UX_REVIEW: parar e perguntar `[D2]`** | ausente | SKILL.md:78-88 | **sim** |
| **CONTEXTO de domínio: ler e rodar `contexto-lint.sh --validade` (aviso, não trava)** | ausente | SKILL.md:72-76, 229 | **sim** |
| **Varredura de landmines obrigatória (`playbook-lint.sh --grep` por superfície; abrir a entrada inteira); seção `## Landmines aplicáveis` nunca omitida** | ausente | SKILL.md:131-147, 227, 230 | **sim** |
| **Patterns citados: `patterns-lint.sh --design` sai 0, ou "candidato a pattern"** | ausente | SKILL.md:149-158, 228 | **sim** |
| **Títulos `### Decision N:` fixos (contrato de máquina do `design-lint` e do índice de ADR)** | ausente (o lint do starter só exige `### Decision` e os 5 rótulos, validate_design.py:143-148) | SKILL.md:119-121 | **sim** |
| **`## Segurança` com 5 itens; item aplicado no Define com o "evitar" do catálogo (aviso)** | ausente (Security Considerations livre, SKILL.md:348-354) | SKILL.md:169-176, 233 | **sim** |
| **Review adversarial: commitar DEFINE e DESIGN antes; `adversarial-review.sh`; engines vazias ⇒ perguntar quais usar** | ausente | SKILL.md:196-209 | **sim** |
| **Sem engine: sessão nova como revisor; ⏸️ parada exit 40 (`sdd-fluxo.sh despachar revisor-design`)** | ausente | SKILL.md:215-219 | **sim** |
| **Revisão exigida (`sdd-fluxo.sh review-design` 0 ou 64): o `seguir` só passa com o Advisor Ledger preenchido e nenhuma HIGH sem veredito** | ausente | SKILL.md:219-221, 276-278; OPT/DESIGN_TEMPLATE.md:255-260 | **sim** |
| **Fluxo encadeado** | ausente | SKILL.md:265-278 | **sim** (mantenedor) |

### 3.3 sdd-build

| Parada | starter v1.5.18 | Open | só no Open? |
|---|---|---|---|
| Entradas: Brainstorm, DEFINE, DESIGN e projeto gravável; sem projeto, pedir | SKILL.md:80-88 | entrada: o DESIGN; lê DEFINE (SKILL.md:62, 80); Brainstorm não exigido | não |
| `LLM Prompts` do DEFINE × seção do DESIGN divergem: parar | SKILL.md:151-152; references/llm-prompt-gate.md:9-13 | SKILL.md:85-87 | não |
| Manifest ausente ou incompleto: parar e corrigir o Design | SKILL.md:153 | ausente | não (só no starter) |
| Branch: não trabalhar na branch padrão; criar/usar branch | SKILL.md:167-170 | ausente (fica na `sdd-new-session`) | não (só no starter) |
| Modo de execução: recomendar e o aluno escolhe antes da 1ª alteração | SKILL.md:197-219; references/execution-modes.md:78-89 | SKILL.md:114-123 ("mesmo com recomendação óbvia, **pergunte**"); o exemplo marca `[auto · de rotina]` (references/como-falar.md:48) | não |
| Revisão externa pré-build: perguntar quando o caso justifica e a ferramenta existe | SKILL.md:221-237 | troca: passo 0 por script (abaixo) | não |
| Ambiguidade material ⇒ pergunta; mudança de especificação ⇒ parar a tarefa e perguntar | SKILL.md:115, 242 | "suposição vira pergunta" (SKILL.md:127) | não |
| Drift detectado (6 perguntas) ⇒ parar, opções ao aluno, registrar | SKILL.md:263-282 | só drift de prompt: `prompt-drift-scan.sh` exit 2 ⇒ parar e perguntar (SKILL.md:164-167) | não (o geral é só do starter) |
| Skill de prompt ausente ⇒ bloquear o item e perguntar | SKILL.md:292-295; references/llm-prompt-gate.md:52-54 | pergunta `[D2]`: "instalar e continuar" (rodar o `init` de novo) · "tirar do escopo" · "não sei" (SKILL.md:155-161) | não (a opção "rodar o `init`" é nova) |
| 3ª falha da escada de retry ⇒ parar e registrar | SKILL.md:303; references/retry-and-advisor.md:25-29 | SKILL.md:175-176 | não |
| Sem comando de verificação ⇒ perguntar | SKILL.md:319-320 | slot vazio ⇒ pular e dizer (SKILL.md:207) | não |
| Migration: projetos divergentes ⇒ parar e o aluno escolhe (nome + ref) | references/aplicar-migration.md:56-67 | OP references/aplicar-migration.md:56-67 | não |
| Migration: nenhum projeto descoberto ⇒ perguntar qual | references/aplicar-migration.md:45-46 | OP :45-46 | não |
| Migration pendente fora do manifest ⇒ parar, o aluno decide | references/aplicar-migration.md:100-103 | OP :120-123 | não |
| Migration: **a** confirmação "Posso aplicar neste projeto?" com SQL inteiro | references/aplicar-migration.md:108-137 | OP :128-158 | não |
| Migration manual / `declined`: o aluno cola o SQL no SQL Editor e diz "rodei" | references/aplicar-migration.md:32-33, 148-151 | OP :169-172 | não |
| Migration: senha do banco pedida pela CLI (aluno) | references/aplicar-migration.md:143-144 | OP :164-165 | não |
| **Migration: checagem `schema.check_cmd` (`slot.sh`); exit 2/3/64 ⇒ não aplica; migration extra incluída ⇒ checar de novo** | ausente | SKILL.md:183; OP references/aplicar-migration.md:91-113 | **sim** |
| Migration: `- banco:` em `sdd/ambiente.md` (condição do checklist) | SKILL.md:342, 472 | removido (OP references/aplicar-migration.md:69-72) | não (só no starter) |
| Migration: prova por leitura e seção `## Migrations aplicadas` | SKILL.md:470-471; validate_build_report.py:87-93 | `report-lint.py` exige log `evidence/{F}/MIG-nnn.log` ou `recibo:` (OP references/aplicar-migration.md:204-228) | não (o log em arquivo é novo) |
| Verify Gate vermelho ⇒ corrigir e repetir; inconclusivo ⇒ resolver a ferramenta; manual-ux ⇒ checklist e recibo humano | SKILL.md:348-368; references/verify-gate.md:32-65 | SKILL.md:189-198 | não |
| **Verify Gate exit 5 por linha `Governança` sem valor final ⇒ parar e voltar ao Define (passos 11-12)** | ausente | SKILL.md:197 | **sim** |
| **Verify Gate exit 64 ⇒ voltar ao Define** | só como contrato do runner do sdd-open (references/verify-gate.md:44-53) | SKILL.md:198 | **sim** (como parada efetiva) |
| Checks complementares falham ⇒ build incompleto | SKILL.md:370-381 | SKILL.md:205-207 | não |
| **`test-baseline.sh`: só falha nova aborta; aceitar falha conhecida (`--aceitar`) é decisão do aluno** | ausente | SKILL.md:205-207 | **sim** |
| Revisão pós-build: recomendar; aluno decide; HIGH aplicada ⇒ rerodar o gate | SKILL.md:383-396 | troca: 5c (abaixo) | não |
| Lint do relatório passa (`validate_build_report.py`) | SKILL.md:430-438, 479 | `report-lint.py` exit 0 (SKILL.md:255-257, 274) | não (troca de ferramenta; regras novas abaixo) |
| Build bloqueado ⇒ `Status: Blocked`, sem handoff de conclusão | SKILL.md:420-423; references/build-protocol.md:79-89 | `NEEDS_WORK` 2 ciclos ⇒ `Blocked` (SKILL.md:235-236) | não |
| Não sobrescrever relatório histórico sem avisar | SKILL.md:452 | ausente | não (só no starter) |
| **Passo 0: `sdd-fluxo.sh review-design`; exigida e ledger vazio ⇒ revisão do DESIGN antes de codar (`adversarial-review.sh`)** | ausente | SKILL.md:66-76 | **sim** |
| **Script de `sdd/bin/` ausente ⇒ o aluno roda o `init` de novo** | ausente | SKILL.md:87-88 | **sim** |
| **Contagem de camadas por `layers:` do `sdd/config.yaml` (≥2 ⇒ 1.5 e 5d obrigatórios)** | ausente | SKILL.md:80-83 | **sim** |
| **Landmines de novo no build; hit que o DESIGN não listou vira tarefa antes do código** | ausente | SKILL.md:90-93 | **sim** |
| **1.5 Contrato de aceite (≥2 camadas): `avaliador-guard.sh` (exit 1 ⇒ commitar; 2 ⇒ parar), avaliador fresco, uma pergunta por proposta ACEITA/RECUSADA** | ausente | SKILL.md:95-104; references/contexto-fresco.md:33-47 | **sim** |
| **1.5/5d sem subagente: ⏸️ sessão nova e colar o bloco (exit 40)** | ausente | SKILL.md:237-241; references/contexto-fresco.md:23-27 | **sim** |
| **A 1ª tarefa é o script do gate, já falhando (baseline vermelho)** | ausente | SKILL.md:108-112 | **sim** |
| **Regras de segurança da stack (`seguranca-varredura.sh --regras`) antes da 1ª tarefa; conflito com o DESIGN ⇒ pergunta** | ausente | SKILL.md:130-133 | **sim** |
| **Varredura de drift de prompt em todo arquivo, mesmo com `LLM Prompts: false`; aviso `prompts.wrapper_pattern` vazio** | ausente (a heurística é por leitura, references/llm-prompt-gate.md:15-29) | SKILL.md:162-168 | **sim** |
| **Item em laço: `sdd-loop-builder` devolve "item faltando" ⇒ iterar o DESIGN; "não é laço" ⇒ trocar o Tipo** | ausente | SKILL.md:140-150 | **sim** |
| **Gate corrigido pelo build: `gate-baseline.sh` contra a branch de produção tem de dar vermelho** | ausente | SKILL.md:200-203 | **sim** |
| **5c Review adversarial pós-build: commitar antes; `adversarial-review.sh`; ledger `sdd/reviews/LEDGER_REVISAO_{F}.md` com marca `dano`; `ledger-revisao-lint.sh`; `sdd-fluxo.sh loop`; a release exige o review ou a dispensa** | ausente | SKILL.md:209-226 | **sim** |
| **5d Avaliador fresco bloqueante (≥2 camadas): `avaliador-guard.sh`; prova cada AT executando; `NEEDS_WORK` ⇒ novo ciclo (máx. 2); sem browser ⇒ `NAO_VERIFICADO`** | ausente | SKILL.md:228-242; references/contexto-fresco.md:49-77 | **sim** |
| **`PASS_PENDENTE_RECIBO` ⇒ recibo do aluno; sem recibo o build espera** | ausente (só o recibo do manual-ux) | references/contexto-fresco.md:73 | **sim** |
| **Relatório default-FAIL: AT `true` só com `evidence/{F}/AT-nnn.log` (1ª linha `$ cmd`), `AVALIACAO_*.md` ou `recibo:`** | ausente (o lint do starter não olha evidência por AT) | SKILL.md:246-251; OPT/fragments/EVIDENCIA.md | **sim** |
| **Linha do avaliador obrigatória (arquivo · `N.A. (motivo)` · `PENDENTE (motivo)`)** | ausente | SKILL.md:249-252 | **sim** |
| **Seções obrigatórias novas: Contrato de aceite · Landmines lidas no build · Candidatos ao playbook (bloco `<<<CANDIDATO_PLAYBOOK` com `evidencia:`) · Segurança (recusados/adiados)** | ausente | SKILL.md:259-265 | **sim** |
| **Fechar: `seguir build … release` sempre para (D1)** | ausente | SKILL.md:328-329 | **sim** (mantenedor) |

---

## 4. Onde cada skill grava e lê

### 4.1 sdd-define

| | starter v1.5.18 | Open |
|---|---|---|
| Grava | `sdd/DEFINE_{F}.md` (ou `.claude/sdd/` se existir); sem filesystem, `.md` para download (SKILL.md:310-314) | `sdd/features/DEFINE_{F}.md` (SKILL.md:220-224); `sdd/contexto/<slug>.md` pelo cartógrafo (SKILL.md:79-80); `sdd/reports/briefs/BRIEF_cartografo_<F>.md` e `BRIEF_revisor-governanca_<F>.md` (SKILL.md:102, 252); `sdd/reviews/GOVERNANCA_REVIEW_<F>.md` pelo revisor (SKILL.md:263); `sdd/GOVERNANCA_PADRAO.md` (SKILL.md:296-297); `sdd/tests/governanca/<F>_<Gnn>.sql` (SKILL.md:309); `sdd/bin/gates/gate-{feature}.sh` (SKILL.md:215-216); cópias em `${TMPDIR}/sdd-fronteira-…` (SKILL.md:104, 254) |
| Lê | o `BRAINSTORM_*.md` que o aluno enviar (SKILL.md:53-59) | entrada `BRAINSTORM_*.md \| notas.md \| "pedido direto"` (SKILL.md:65); `sdd/templates/DEFINE_TEMPLATE.md`, `AGENTS.md`, fragmentos, `## Sempre` de `sdd/playbook.md` (SKILL.md:72-74); `sdd/patterns/dominio.md`, `layers:` (SKILL.md:85); `sdd/kb/` e `_index.yaml` (SKILL.md:145-148); `sdd/config.yaml` (SKILL.md:205); `## Perfil de risco` do BRAINSTORM (SKILL.md:333); as skills `.agents/skills/sdd-governanca/` e `sdd-seguranca/` (SKILL.md:240, 332) |
| Espera de outra fase | BRAINSTORM (do `sdd-brainstorm`) | BRAINSTORM (opcional) com `## Perfil de risco`; mapa de domínios; base `sdd/kb/` |

### 4.2 sdd-design

| | starter v1.5.18 | Open |
|---|---|---|
| Grava | `sdd/DESIGN_{F}.md` (ou `.claude/sdd/`); sem filesystem, download; não sobrescreve em silêncio (SKILL.md:400-407) | `sdd/features/DESIGN_{F}.md` (SKILL.md:187); `sdd/reports/briefs/BRIEF_revisor-design_{F}.md` (SKILL.md:217); o índice `docs/adr/index.md` é montado por `docs-extract-decisions.sh` (SKILL.md:120-121); pasta de revisão do `adversarial-review.sh` (SKILL.md:204-209) |
| Lê | BRAINSTORM + DEFINE obrigatórios; `UX_REVIEW_{F}.md` opcional (SKILL.md:38-53) | DEFINE (entrada `sdd/features/DEFINE_{F}.md`), `UX_REVIEW_{F}.md` se existir, `sdd/templates/DESIGN_TEMPLATE.md`, `AGENTS.md`, `sdd/config.yaml`, playbook (SKILL.md:62, 68-70); `sdd/contexto/<slug>.md` (SKILL.md:72-76); `sdd/patterns/` (SKILL.md:151); `references/CATALOGO_SEGURANCA.md` da `sdd-seguranca` (SKILL.md:174) |
| Espera de outra fase | DEFINE com `LLM Prompts` literal, Verify Gate e Out of Scope; UX_REVIEW opcional | DEFINE com as linhas `CONTEXTO de domínio`, `Segurança` (e `Governança`, que o build cobra); `sdd/reviews/UX_REVIEW_{F}.md` com `## Surface Assignment` (o `sdd-ux-review` grava em `sdd/reviews/`, OP/sdd-ux-review/SKILL.md:134) |

### 4.3 sdd-build

| | starter v1.5.18 | Open |
|---|---|---|
| Grava | código nos caminhos do manifest; `sdd/BUILD_REPORT_{F}.md` (SKILL.md:442-450); `PROGRESS_{FEATURE}.md` no ralph (references/execution-modes.md:52, sem pasta definida); `sdd/ambiente.md` chave `- banco:` (SKILL.md:342) | código; `sdd/reports/BUILD_REPORT_{F}.md` (SKILL.md:246); `sdd/reports/evidence/{F}/AT-nnn.log`, `GATE.log`, `MIG-nnn.log`, `SCHEMA-CHECK.log`, `AVAL-*.log` (SKILL.md:247; OP references/aplicar-migration.md:97-100, 207-209; references/contexto-fresco.md:45, 63); `sdd/reviews/AVALIACAO_{F}_{ts}.md` (SKILL.md:234); `sdd/reviews/LEDGER_REVISAO_{F}.md` (SKILL.md:215); `sdd/reports/briefs/BRIEF_avaliador_{F}.md` (SKILL.md:238); `sdd/reports/progress/PROGRESS_{F}.md` (references/modos-e-retry.md:22); edita o DEFINE (propostas ACEITAS) e o DESIGN (`## Contrato de aceite`, `Tipo` do prompt) (SKILL.md:101-104, 148-150); commits antes das revisões |
| Lê | BRAINSTORM, DEFINE, DESIGN, `UX_REVIEW` opcional, guias do projeto (SKILL.md:80-97) | DESIGN e DEFINE em `sdd/features/` (SKILL.md:62, 189), `AGENTS.md`, `sdd/config.yaml` (`layers:`, `evidence.require_avaliacao_layers`, `prompts.builder_skill`, `prompts.wrapper_pattern`, `schema.check_cmd`, slots de teste), playbook, `sdd/review/CRITERIO_DANO.md`, fragmentos (SKILL.md:80-83, 138, 168, 183, 205, 218) |
| Espera de outra fase | DESIGN com File Manifest numerado e, se `true`, `## LLM Prompts`; DEFINE com `verify_gate` | DESIGN com `## Advisor Ledger` preenchido quando a revisão é exigida, `## Landmines aplicáveis`; DEFINE com a linha `Governança` final (senão o gate sai 5) e a sessão `### Segurança` |
| Quem lê o relatório depois | `sdd-handoff` (Next Step, SKILL.md:489); a `sdd-release` gerada lê `## Migrations aplicadas` (ST/sdd-release/SKILL.md:188, 253) | `sdd-release` (SKILL.md:314), que roda `report-lint.py --pendente` (sdd/bin/report-lint.py:28) |

Fato que importa para a próxima frente: as skills **já geradas** do starter procuram nos dois lugares. O `RESUMO_ETAPA.md` gerado
(ex.: ST/sdd-brainstorm/references/RESUMO_ETAPA.md:44-49) marca a etapa como feita com `sdd/features/DEFINE_{F}.md` **ou**
`sdd/DEFINE_{F}.md`, `sdd/features/DESIGN_{F}.md` **ou** `sdd/DESIGN_{F}.md`, `sdd/reports/BUILD_REPORT_{F}.md` **ou**
`sdd/BUILD_REPORT_{F}.md`. Mas a `sdd-governanca` gerada usa como entrada `sdd/features/DEFINE_{FEATURE}.md`
(ST/sdd-governanca/SKILL.md:68) enquanto a define congelada grava em `sdd/DEFINE_…` — o quickstart explica que até a próxima
geração elas "recebem o documento anterior pelo caminho que você indicar" (ST-raiz/docs/quickstart.pt-BR.md:33; README.md:58).

---

## 5. Essencial sem `init` × ferramenta do mantenedor

### 5.1 Essencial e independente do `init` (deveria ir para a web)

Define:
- Regras EARS do Open, que são texto: ≤~10 ATs, While/If/Where considerados, sem AT de UX visual, rastreabilidade AT→gate
  (OP/sdd-define/SKILL.md:154-164; OPT/fragments/EARS.md:10-62). (Ressalva: a regra dos ~10 ATs reprova o exemplo `baixar-nfse`,
  que tem 49 linhas `| AT-` — ver §6.)
- Marcador NEEDS CLARIFICATION na forma canônica, no lugar da dúvida, e a convenção de menção (OPT/fragments/CLARIFY.md:7-25).
- Taxonomia do Verify Gate e "manual-ux não finge automação" (OPT/fragments/VERIFY_GATE.md:46-87), **mais** a pergunta da
  primeira vez e o "Eu abri … e vi …" do starter (ST/sdd-define/references/VERIFY_GATE.md:7-13).
- Tabela de pesos do LLM Prompts (OP/sdd-define/SKILL.md:180-191).
- Segurança no Define (passo 12), porque a `sdd-seguranca` já é gerada no starter e o passo roda "nesta sessão, sem trava"
  (OP/sdd-define/SKILL.md:326-342). Precisa de troca: o caminho `.agents/skills/sdd-seguranca/SKILL.md` não existe num zip avulso
  (inferência: na web cada skill é um upload separado).
- Governança como **recomendação** com a trava escrita (linha `Governança` no DEFINE, valor final ou `dispensada — motivo`):
  o conceito é texto; o despacho fresco, a fronteira e o `governanca-bloco.py` não (OP/sdd-define/SKILL.md:234-324). Na web,
  "revisor fresco" = conversa nova com só o DEFINE e a skill — a troca da F17b já diz isso para a skill avulsa.
- "Por que cada regra existe" (OP/sdd-define/SKILL.md:361-386), sem as linhas de cartógrafo e de trava do script.

Design:
- `## Segurança` com 5 itens (OP/sdd-design/SKILL.md:169-176; OPT/DESIGN_TEMPLATE.md:231-241).
- ADR com título fixo `### Decision N:` (o motivo é de máquina, mas o formato é bom igual) (OP/sdd-design/SKILL.md:105-121).
- Seção LLM Prompts do fragmento (já em `scripts/starter/trocas/_moldes/LLM_PROMPTS_DESIGN.md`).
- Papel de surface em aberto ⇒ pergunta (OP/sdd-design/SKILL.md:78-88) — só se a `ux-review` gerada pela `ux-review-builder`
  tiver `## Surface Assignment` (não conferi o molde da ux-review gerada; incerto).
- "Revisão por outro vendor antes do código" como **recomendação** de conversa nova, sem script (OP/sdd-design/SKILL.md:196-221).

Build (inferência sobre o que cabe na web: o próprio starter diz que o Build "exige um agente que escreva código no seu projeto",
ST-raiz/docs/quickstart.pt-BR.md:117):
- Verify Gate como critério de parada, com a leitura do `cmd` cru do starter (B2) e a tabela de exit só como vocabulário.
- "A primeira tarefa é o gate, falhando" (OP/sdd-build/SKILL.md:106-112) — texto; precisa de execução.
- Escada de retry por redispatch fresco (OP/sdd-build/references/modos-e-retry.md:40-54) com a saída honesta do starter (B5).
- "Quem julga não é quem constrói" (OP/sdd-build/references/contexto-fresco.md:1-14, briefs 33-65): na web, conversa nova com o
  brief; o `avaliador-guard.sh` e o despacho por exit 40 não.
- Evidência abrível, default-FAIL (OPT/fragments/EVIDENCIA.md): na web, a evidência vira a saída colada no chat ou o
  `recibo: nome data` (inferência).
- Migration provada por leitura (já igual nos dois lados) e o valor de teste fictício (B15).
- Segurança: itens recusados/adiados no relatório; regras da stack lidas do catálogo "sem terminal: leia o catálogo e filtre pela
  stack" — o próprio Open já prevê o caminho sem script (OP/sdd-build/SKILL.md:130-133).

### 5.2 Ferramenta do mantenedor (não faz sentido na web)

- Encadeamento e despacho: `sdd-fluxo.sh` (`seguir`, `despachar` com exit 40, `estado`, `loop`, `review-design`), recibo "Decidi
  sozinho", marcas `[auto]` com fluxo ligado (OPT/fragments/FLUXO_ENCADEADO.md; OP/sdd-define/SKILL.md:398-410;
  OP/sdd-design/SKILL.md:265-278; OP/sdd-build/SKILL.md:317-329).
- Cartógrafo e CONTEXTO de domínio: `contexto-lint.sh`, `sdd/patterns/dominio.md`, `governanca-fronteira.sh`, snapshot em
  `$TMPDIR`, `WORKFLOW_CONTRACTS.yaml`, `sdd/fixtures/` (OP/sdd-define/SKILL.md:76-129; references/cartografo.md).
- Fronteira e bloco da governança: `governanca-fronteira.sh`, `governanca-bloco.py`, restauração do DEFINE por `cp/mv/cmp`
  (OP/sdd-define/SKILL.md:251-293).
- Playbook e landmines: `playbook-lint.sh`, `sdd/playbook.md`, `## Landmines aplicáveis`, `## Landmines lidas no build`,
  Candidatos ao playbook (OP/sdd-design/SKILL.md:131-147; OP/sdd-build/SKILL.md:90-93, 259-261).
- Patterns: `patterns-lint.sh`, `sdd/patterns/README.md` (OP/sdd-design/SKILL.md:149-158).
- Revisão adversarial e ledger: `adversarial-review.sh`, engines `review.revisor1`/`review.auditor`, `LEDGER_REVISAO`,
  `ledger-revisao-lint.sh`, `CRITERIO_DANO.md`, `eval-revisores.sh`, `ADVISOR_CONSULT.md` (OP/sdd-design/SKILL.md:196-221;
  OP/sdd-build/SKILL.md:209-226).
- Lints e runners: `verify-gate.sh`, `design-lint.py`, `report-lint.py`, `kb-dominios.py`, `docs-extract-decisions.sh`,
  `gate-baseline.sh`, `test-baseline.sh`, `slot.sh`/`schema.check_cmd`, `prompt-drift-scan.sh`, `seguranca-varredura.sh`,
  `avaliador-guard.sh`.
- Camadas por `layers:` e `evidence.require_avaliacao_layers`; slots `{{TEST_CMD}}`/`{{TYPECHECK_CMD}}`/`{{LINT_CMD}}`.
- Gate composto em `sdd/bin/gates/` e `psql -f sdd/tests/governanca/…` no `cmd`.

---

## 6. `exemplos/baixar-nfse/` e o kit do build congelado

Fato: os 5 arquivos do exemplo no starter (`README.md`, `BRAINSTORM_`, `DEFINE_`, `DESIGN_`, `GOVERNANCA_REVIEW_BAIXAR_NFSE.md`)
são **iguais byte a byte** à semente do Open em `scripts/starter/raiz/exemplos/baixar-nfse/` (`cmp`). O gerador trata `exemplos`
como pasta de dono inteiro (`scripts/gerar-starter.py:534-535`), e `tests/test_gerar_starter.py:69, 114, 413-414` a cobre.

### 6.1 O que o exemplo cita

| Onde | O que cita |
|---|---|
| README.md:29, 31-37 | "crie uma subpasta chamada `sdd`" e salve os três documentos em `sdd/`, sem mudar o nome |
| README.md:44 | o prompt "Execute o **SDD Build by RDD** para a feature BAIXAR_NFSE" (o nome do `display_name` do openai.yaml congelado) |
| README.md:46 | "Os documentos estão em `sdd/`: BRAINSTORM_…, DEFINE_… e DESIGN_…. Leia os três" |
| README.md:49 | "Crie somente os arquivos do File Manifest, todos dentro de `extensao/`. O relatório do build fica em `sdd/`." |
| README.md:51 | "Use o modo de execução **default, sem revisão externa, e não me pergunte**… sem parar a cada etapa" |
| README.md:53 | "Se o comando python não existir, use python3… registre no relatório que **o validador** não rodou" (o `validate_build_report.py` do kit congelado) |
| README.md:55 | Verify Gate manual-ux: checklist um item por vez, registrar no BUILD_REPORT |
| README.md:20 | quickstart `../../docs/quickstart.pt-BR.md` |
| BRAINSTORM:16 | "O aluno roda o `/build` (sdd-build) no repositório dele" |
| DEFINE:11, 251-255, 259-261 | Author "SDD Define by RDD"; Next Step "Execute o **SDD Design by RDD**." |
| DEFINE:27 | "Constrói a extensão com `/build`" |
| DEFINE:115-133 | sessão de Clarifications; a governança citada por nome de arquivo "na pasta do exemplo no GitHub; o build não precisa dele" |
| DEFINE:159-170 | `verify_gate` `kind: manual-ux`, `cmd: "N/A (manual-ux)"`, 5 frases "Eu abri … e vi …" |
| DEFINE:200-207 | Technical Context com 4 linhas (sem `CONTEXTO de domínio`, `Governança`, `Segurança`) |
| DESIGN:11-16 | Metadata no formato do starter (BRAINSTORM, DEFINE, UX REVIEW N/A, LLM Prompts false, Ready for Build) |
| DESIGN:228-262 | File Manifest com `(general)`, caminhos `extensao/…` |
| DESIGN:694, 711, 726 | Requirements Traceability, Risks and Mitigations, Advisor Ledger (seções do molde congelado) |
| DESIGN:720 | skill `sdd-higiene-dado` |
| DESIGN:750-752 | Next Step "Execute o **SDD Build by RDD**." |
| GOVERNANCA_REVIEW:139-143 | "No Build, o passo *Aplicar a migration* da `sdd-build` prova por leitura…" |

Conferido rodando os validadores (só leem): `validate_define.py` e `validate_design.py` do starter dão **PASS** no exemplo; o
`design-lint.py` do Open também dá exit 0; `verify-gate.sh --print` do Open lê o bloco (exit 0); **`verify-gate.sh --checar`
do Open sai 5 — "GOVERNANÇA NÃO REVISADA … não tem a linha Governança com um valor final (encontrado: ausente)".**

### 6.2 O que quebraria se define/design/build passassem a gravar e ler nas pastas do Open

1. **Os caminhos do README** (fato + inferência): o aluno põe os três documentos em `sdd/` (README.md:29-37) e o prompt diz que estão
   em `sdd/` e que o relatório fica em `sdd/` (README.md:46-49). Um build gerado do Open procura `sdd/features/DESIGN_{F}.md` e
   `sdd/features/DEFINE_{F}.md` (OP/sdd-build/SKILL.md:62, 189) e grava em `sdd/reports/` (SKILL.md:246). O prompt explícito do
   README provavelmente prevalece (inferência), mas o relatório e a evidência iriam para `sdd/reports/…`, contradizendo a linha 49.
2. **O nome do prompt** "Execute o SDD Build by RDD" (README.md:44) depende do `display_name` do `agents/openai.yaml` congelado;
   a skill gerada do Open não tem openai.yaml (fato) — se o gerador não o recriar, o nome deixa de existir (inferência).
3. **O "não me pergunte" do modo e da revisão** (README.md:51) bate de frente com o Open: "mesmo com recomendação óbvia,
   **pergunte**" (OP/sdd-build/SKILL.md:122-123), o passo 0 da revisão do DESIGN (SKILL.md:66-76), o 5c que a release exige
   (SKILL.md:209-211) e o 5d bloqueante com ≥2 camadas (SKILL.md:228) — sem `sdd/config.yaml`, a contagem de camadas não existe.
4. **O validador** "se python não existir, use python3" (README.md:53) aponta para `scripts/validate_build_report.py` da skill
   congelada; no Open o lint é `sdd/bin/report-lint.py` (OP/sdd-build/SKILL.md:255-257), que exige `evidence/{F}/AT-nnn.log`, a linha
   do avaliador e seções que o exemplo não prevê.
5. **O Verify Gate do exemplo para no 5 do Open** (fato, rodado): o DEFINE não tem a linha `Governança`; o build do Open trata
   exit 5 como "pare e volte ao Define" (OP/sdd-build/SKILL.md:197). Na web, sem script, a regra escrita diria o mesmo.
6. **O DEFINE do exemplo seria recusado pelo Define do Open**: 49 linhas de AT contra "há mais de ~10 ATs" (OP/sdd-define/SKILL.md:162);
   sem `CONTEXTO de domínio`, `Governança`, `Segurança` no Technical Context (DEFINE:200-207 × OPT/DEFINE_TEMPLATE.md:161-163).
7. **O DESIGN do exemplo** não tem `## Landmines aplicáveis` nem `## Segurança` nem `## Contrato de aceite` (lista de `## ` do
   arquivo), que o Quality Gate do design do Open pede (OP/sdd-design/SKILL.md:227, 233); tem Requirements Traceability e Risks,
   que o molde do Open não tem. O `design-lint.py` passa mesmo assim (fato), então a quebra é de checklist, não de script.
8. **Handoffs**: os documentos do exemplo terminam em "Execute o **SDD Design/Build by RDD**." (DEFINE:259-261; DESIGN:750-752);
   uma define/design gerada que feche com outro texto deixa o exemplo com um formato que nenhuma skill escreve mais — e o
   `validate_define.py`/`validate_design.py` congelados exigem exatamente esse rabo (validate_define.py:124-132;
   validate_design.py:196-201). Se os scripts saírem, isso deixa de ser checado (inferência).
9. **`.claude/sdd/`**: as três congeladas continuam em `.claude/sdd/` quando ela existe (ST/sdd-define/SKILL.md:310); o validador do
   design comenta isso (validate_design.py:111-114). O Open não fala de `.claude/sdd/`.
10. A **GOVERNANCA_REVIEW** do exemplo cita "o passo *Aplicar a migration* da `sdd-build`" (GOVERNANCA_REVIEW:139-143) — existe dos
    dois lados (OP passo 4b), sem quebra.

---

## 7. Scripts e testes das congeladas

| Arquivo | O que faz (fato) | Quem chama (fato) |
|---|---|---|
| `ST/sdd-define/scripts/validate_define.py` (140 l.) | lint estrutural: 16 seções, nenhum marcador NEEDS CLARIFICATION, Clarity ≥ 12, AT com keyword EARS, bloco `verify_gate` com 5 campos e `kind` válido, `eval` com limiar numérico, `manual-ux` com `cmd: "N/A (manual-ux)"` e checklist, `LLM Prompts` literal, Next Step exato; exit 0/2/64 | a própria skill, "quando houver filesystem e Python" (SKILL.md:297-303, 358); ST-raiz/docs/quickstart.md:124 e quickstart.pt-BR.md:124 ("Opcional: valide os artefatos localmente"); CI só compila (`.github/workflows/ci.yml:32-33`) |
| `ST/sdd-define/tests/test_validate_define.py` (254 l., 15 testes) | roda o validador como subprocesso em DEFINEs mínimos; um teste passa o `DEFINE_EXEMPLO.md` (test_exemplo_passa, :248) | CI "Skill tests" `for t in skills/*/tests; … unittest discover` (ci.yml:38-44); CONTRIBUTING.md:31 |
| `ST/sdd-design/scripts/validate_design.py` (212 l.) | 18 seções; sem `[NEEDS CLARIFICATION`, `TBD`, `{…}`; Metadata com BRAINSTORM/DEFINE/LLM Prompts/Status `Ready for Build`; diagrama em ```` ```text ````; Components; `### Decision` com os 5 rótulos; manifest numerado sem dependência faltante nem ciclo, `Total Files` igual; snippet; LLM Prompts coerente com a flag e com caminhos `prompts/`; Testing Strategy; Traceability com AT/MUST; Next Step exato | a skill (SKILL.md:30, 385-393, 448); quickstart.md:125 / quickstart.pt-BR.md:125; CI compila |
| `ST/sdd-design/tests/` | **não existe** (fato: `ls`) | — |
| `ST/sdd-build/scripts/validate_build_report.py` (160 l.) | 13 seções; nenhum placeholder `{…}`; `.sql`/`migrations/` em Files Changed ⇒ `## Migrations aplicadas` com linha cheia; Mode Selection com Recommendation e User decision; tabela do Verify Gate; COMPLETE ⇒ Status Complete, gate Green/Manual receipt, sem blocker, Next Step "SDD Handoff by RDD"; não-COMPLETE ⇒ sem Next Step | a skill (SKILL.md:35, 430-438, 479); quickstart.md:126 / quickstart.pt-BR.md:126; README do exemplo, indiretamente (exemplos/baixar-nfse/README.md:53); CI compila |
| `ST/sdd-build/tests/test_validate_build_report.py` (230 l., 8 testes) | casos de migration (sem `.sql` passa; `.sql` sem seção reprova; seção vazia reprova; preenchida passa; "já aplicada" passa; `migrations/` sem `.sql` exige; caminho sem crase exige; o template tem a seção) | CI "Skill tests" (ci.yml:38-44); CONTRIBUTING.md:31 |

Outros fatos:
- O `scripts/package.sh` zipa a pasta inteira de cada skill, só exclui `.DS_Store`, `__MACOSX`, `.pyc`, `__pycache__`
  (ST-raiz/scripts/package.sh:12-13): **scripts e tests vão no zip** que o aluno da web sobe.
- `tests/` da raiz do starter não chama nenhum dos três validadores: tem `test_sdd_kb_normativo.py` e fixtures da kb (fato: `ls`).
- `scripts/publish-check.sh:36-46` exige `## Como falar com o aluno` e `references/como-falar.md` nas três (entre outras).
- `scripts/check-gerado.py` só confere skills com `GERADO.txt`; as três congeladas não têm (fato: `ls`), então hoje ficam fora
  do gate de arquivos gerados. O gate de versão (ci.yml:24-30) vale para elas.
- O README só diz que as três "continuam como estavam, congeladas" (README.md:58, 159); não cita os validadores.

Se o aluno da web os usa: **não** (inferência apoiada em fato). As skills os condicionam a "quando houver filesystem e Python"
(ST/sdd-define/SKILL.md:297; ST/sdd-design/SKILL.md:30, 387); o quickstart os põe como **opcionais e locais**, com
`python skills/…` a partir do repositório clonado (quickstart.pt-BR.md:119-126), e diz que as fases 1–3 funcionam sem filesystem
e a 4 exige um agente que escreva no projeto (quickstart.pt-BR.md:117). Quem os usa de fato: o CI do starter (testes), quem
clona o repositório, e o kit do exemplo (o build congelado roda o `validate_build_report.py` no agente com terminal). Na web, um
ambiente com execução de Python (ex.: a ferramenta de análise do ChatGPT) poderia rodá-los se o zip os trouxer — não conferi.

Consequência para a geração (inferência): tirar os scripts das três exige (a) mudar o quickstart (linhas 119-126 dos dois idiomas),
(b) a linha 53 do README do exemplo, (c) a CI deixa de ter `skills/sdd-define/tests` e `skills/sdd-build/tests` (o laço já tolera
pasta ausente, ci.yml:41), e (d) o teste `test_exemplo_passa` some com o `DEFINE_EXEMPLO.md` se o exemplo não for levado.
