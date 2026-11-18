# DESIGN: F17c — starter gerado, etapa 3

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | F17C_STARTER_ETAPA3 |
| **Date** | 2026-11-13 |
| **Author** | design-agent |
| **DEFINE** | `sdd/features/DEFINE_F17C_STARTER_ETAPA3.md` (v1.3) |
| **Status** | Ready for Build |

---

## Architecture Overview

```text
 sdd-open (tag vX.Y.Z)                                              clone do sdd-starter
 ─────────────────────                                              ────────────────────
 .agents/skills/sdd-define/
   SKILL.md            (caminho do Open; ganha 1 linha: "sem sdd/bin/ ou sem acesso? siga web/MODO_WEB.md")
   web/MODO_WEB.md     ← NOVO: o SKILL.md do starter v1.5.18, mudado só no necessário
   web/references/*    ← NOVO: as references do starter (como-falar, EARS, CLARIFY, VERIFY_GATE, define-protocol)
   web/assets/*        ← NOVO: DEFINE_TEMPLATE e DEFINE_EXEMPLO do starter
 (idem sdd-design/web/, sdd-build/web/)
 scripts/starter/modos.tsv   + 3 linhas:  sdd-define<TAB>web/MODO_WEB.md<TAB>web   (3ª coluna NOVA: pasta-base)
 scripts/starter/lista.txt   18 (define, design, build depois do brainstorm)
 scripts/starter/openai.tsv  + 3 linhas (semente: agents/openai.yaml da v1.5.18)
 scripts/starter/raiz/       README, docs/quickstart, docs/workflow, exemplos/baixar-nfse/README  (18 geradas)
                                   ▼
 scripts/gerar-starter.py  compor(origem, destino, modo, base):
     SKILL.md = frontmatter do Open (description/compatibility do modo) + corpo do modo
     arquivos citados pelo modo resolvidos em <skill>/<base>/ e gravados no MESMO caminho relativo
     (web/references/como-falar.md → references/como-falar.md)
                                   ▼                                    skills/sdd-{define,design,build}/
                                                                          SKILL.md, references/, assets/,
                                                                          agents/openai.yaml, GERADO.txt
 sdd/templates/{DEFINE,DESIGN,BUILD_REPORT}_TEMPLATE.md  (Open: sem sobras; o relatório com Seleção de modo e Drift)
```

## Components

| Componente | Papel |
|---|---|
| `.agents/skills/sdd-{define,design,build}/web/` | o modo web: o texto congelado do starter `v1.5.18` com as mudanças da Decision 3 |
| `scripts/gerar-starter.py` (`ler_modos`, `compor`) | a 3ª coluna opcional de `modos.tsv` (pasta-base); sem ela, como na F17b |
| `scripts/starter/{lista.txt,openai.tsv,modos.tsv}` | as 3 na geração |
| `scripts/starter/raiz/{README.md,docs/,exemplos/baixar-nfse/README.md}` | 18 geradas, nenhuma congelada; sem validadores; pastas do Open |
| `sdd/templates/{DEFINE,DESIGN,BUILD_REPORT}_TEMPLATE.md` | P3: sem sobras; relatório com as seções que a skill pede |
| `.agents/skills/sdd-{define,design,build}/SKILL.md` | a linha do modo web; "não finja"; no define, a pergunta da 1ª vez do Verify Gate |

---

## Key Decisions

### Decision 1: a pasta do modo e a 3ª coluna de `modos.tsv`

| **Status** | Accepted | · | **Date** | 2026-11-13 |

**Context:** os arquivos do modo web colidem de nome com os do Open (`references/como-falar.md` nas 3,
`references/aplicar-migration.md` no build), e o `publish-check.sh` do starter exige `references/como-falar.md`.
**Choice:** cada uma das 3 ganha `web/` com `MODO_WEB.md`, `references/` e `assets/`. `modos.tsv` aceita uma 3ª
coluna opcional, a **pasta-base** (relativa à skill): o modo cita `references/x.md`, o gerador lê
`<skill>/<base>/references/x.md` e grava `references/x.md` na skill gerada; o fecho (arquivo citado que cita outro)
resolve na mesma base. Sem a 3ª coluna, a base é a raiz da skill (a release da F17b não muda). Base que não existe,
que sai da skill (`..`, absoluta) ou linha com 4+ colunas ⇒ 65 sem gravar. O nome `MODO_WEB.md` (não `SKILL.md`)
evita que um agente ou o `npx skills add` tome a pasta `web/` por uma skill.
**Rationale:** mantém o `SKILL.md` do Open intacto e cada arquivo do modo com o nome que o starter espera.
**Alternatives Rejected:** 1. nomes com prefixo (`references/web-como-falar.md`) e troca de nome no gerador — rejeitada:
uma regra de renomear a mais e o texto do modo citaria um nome que não existe no starter · 2. `web/SKILL.md` —
rejeitada: SKILL.md aninhado pode virar skill fantasma.
**Consequences:** o `init` do Open copia `web/` junto (a pasta inteira da skill); o `sdd-decisoes-lint` e o
`publish-gate` do Open passam a ler esses arquivos (Decision 3, itens 7 e 8).

### Decision 2: as 3 na lista, na ordem das fases

| **Status** | Accepted | · | **Date** | 2026-11-13 |

**Choice:** `lista.txt` ganha `sdd-define`, `sdd-design`, `sdd-build` logo depois de `sdd-brainstorm` (18); o
comentário deixa de falar em congeladas. `openai.tsv` ganha as 3 linhas com os textos de `interface:` do
`agents/openai.yaml` da `v1.5.18` (o aluno vê o mesmo botão; os nomes "SDD Define/Design/Build by RDD" seguem, e são
eles que os handoffs dos documentos citam). O bloco `policy:` do `openai.yaml` da design congelada não vai (o gerador
só escreve `interface:`, como nas 15; sem `policy`, a skill vale para todos os produtos).
**Rationale:** a ordem fixa a saída; o texto do botão é conhecido do aluno.

### Decision 3: o que muda no texto do starter `v1.5.18` ao virar modo web

| **Status** | Accepted | · | **Date** | 2026-11-13 |

**Choice:** `web/MODO_WEB.md` = `SKILL.md` da `v1.5.18`; `web/references/` e `web/assets/` = os da `v1.5.18`
(sem `scripts/`, `tests/`, `agents/`). Mudanças, e só elas:
1. **Frontmatter:** só `description` da `v1.5.18` (sem citar o Open) e `compatibility` nova — `name`, `license` e a
   versão vêm do `SKILL.md` do Open (revisão, nota 10); (define e design: "Funciona na
   web (claude.ai, ChatGPT), onde o documento sai no chat, e em qualquer agente com acesso ao projeto, sem o `init` do
   Open"; build: "Requer um agente com acesso gravável ao projeto; sem o `init` do Open; o Verify Gate se confere
   lendo a saída do comando").
2. **Identificação:** a linha igual à do `SKILL.md` do Open (versão nova, `nov/2026`, URL do Open; o gerador troca a URL).
3. **Pastas (decisão do Roberto):** DEFINE e DESIGN em `sdd/features/`, BUILD_REPORT em `sdd/reports/`; sai o
   ".claude/sdd/ se já existir"; "os documentos das cinco fases ficam lado a lado, sem subpastas" vira a lista de onde
   cada um fica. **Documento de uma fase anterior** (projeto começado antes desta versão): "leia de onde estiver —
   `sdd/features/`, `sdd/` ou `.claude/sdd/` —, grave o novo na pasta desta versão e não pergunte onde está" (nota 5;
   não é parada: a frase tira a pergunta).
4. **Prova sem script:** saem as instruções de rodar `validate_define.py`, `validate_design.py`,
   `validate_build_report.py` e os itens de checklist que os citam; no lugar, "releia o documento contra o checklist
   desta seção". O que só o validador conferia entra no checklist (nota 6): no define, `manual-ux` com `cmd: "N/A
   (manual-ux)"` e checklist, `eval` com limiar numérico, todas as seções do asset; no design, diagrama em
   ```` ```text ````, `Total Files` igual às linhas do manifest, os rótulos de cada decisão, Requirements Traceability
   ligando AT e MUST; no build, Mode Selection e a tabela do Verify Gate. A releitura é do agente, não parada.
5. **Defeitos do starter:** `define-protocol.md` termina no Design (não `HANDOFF_TO_UX_REVIEW`); `build-protocol.md`
   termina no handoff (não `HANDOFF_TO_RELEASE`); sai "Entradas opcionais: `sdd.config.yaml`"; sai a chave
   `- banco:` em `sdd/ambiente.md` (SKILL.md e `aplicar-migration.md`), ficando só a seção `## Migrations aplicadas`
   do BUILD_REPORT (o que a release gerada na F17b já lê).
6. **Valores de exemplo (A-001):** CPF e CNPJ por extenso (`<CPF de teste>`, `<CNPJ>`) viram descrições
   em prosa ("um CPF válido de teste", "o mesmo CPF com o último dígito trocado", "onze vezes o 1", "<um CNPJ de
   teste>", "nunca o documento de um cliente real"): o `publish-gate` do Open barra o formato (medido no protótipo: 6
   linhas). Na história do git eles também não entram: o commit da cópia verbatim foi desfeito antes de qualquer push
   (nota 8).
7. **Marcas de decisão (A-002):** as perguntas de exemplo dos 3 `como-falar.md` ganham a marca `[D2 · muda o
   produto]` ou `[auto · de rotina]` e a opção "(recomendado)", porque o `sdd-decisoes-lint` do Open lê
   `.agents/skills/` inteiro (medido: 5 achados em 3 arquivos). É texto de exemplo, não parada nova; a contagem fixada
   do lint muda (de 31 perguntas em 26 arquivos para 34 em 29).
8. O build gerado cabe em 500 linhas (nota 15): as duas listas da hierarquia de autoridade viram uma linha cada.
9. Nada mais: perguntas, ordens, checklists, handoffs por nome de produto ("Execute o **SDD Design by RDD**.") e o
   formato de "Como falar com o aluno" ficam como estão.
**Rationale:** decisão do Roberto (brainstorm, pergunta 1): as paradas do aluno ficam iguais.
**Alternatives Rejected:** 1. recorte do texto do Open — rejeitada no brainstorm.
**Consequences:** a tabela de paradas deve mostrar 0 parada nova; a única diferença esperada é a pasta.

### Decision 4: a linha do modo no `SKILL.md` do Open e o "não finja"

| **Status** | Accepted | · | **Date** | 2026-11-13 |

**Choice:** no topo de cada uma das 3, logo depois da identificação, como na release:
"**Projeto sem `sdd/bin/` (sem o `init`) ou sem acesso aos arquivos (claude.ai, ChatGPT)?** Siga `web/MODO_WEB.md`
desta skill." E, no passo de contexto de cada uma, uma regra curta: "**Sem acesso, não finja:** não diga que leu,
escreveu ou rodou o que não leu, escreveu ou rodou; sem o código à vista, não invente caminho nem biblioteca" (no
design, mais: "sem código e sem a stack escrita no projeto (`AGENTS.md`, `sdd/config.yaml`, README), pergunte a stack
e a estrutura mínima antes do File Manifest" — nota 14; no build: "sem o projeto acessível,
peça o projeto; não monte um BUILD_REPORT a partir só dos documentos"). No passo 8 do define, a pergunta da 1ª vez:
sem comando conhecido (slot vazio e nenhum no projeto), "**existe um comando que devolve 0 quando funciona?**"; sim
⇒ `kind: test` com ele; não ⇒ `kind: manual-ux` com 3 a 5 frases "Eu abri … e vi …" no `manual_fallback`;
"`manual-ux` nunca como atalho para não perguntar". Também no fragmento `sdd/templates/fragments/VERIFY_GATE.md`
(a fórmula "Eu abri … e vi …" no `manual-ux`).
**Rationale:** itens D1, D2, D7, G1, B4/B5 da comparação (C forte) que servem a todo usuário do Open (decisão do
Roberto, pergunta 2); não criam parada: a pergunta da 1ª vez já existia com slot vazio, só ganha a forma.
**Consequences:** bump minor: `sdd-define` 2.7.0, `sdd-design` 2.7.0, `sdd-build` 2.10.0 (as 3 maiores que as do
starter). O `SKILL.md` do build passa de 333 para ~336 linhas; o do define, de 414 para ~420.

### Decision 5: os moldes do Open

| **Status** | Accepted | · | **Date** | 2026-11-13 |

**Choice:** `BUILD_REPORT_TEMPLATE.md` ganha `## Seleção de modo` (sinais, recomendação, decisão do usuário) e
`## Drift detectado` (tabela; "nenhum" vale), antes de `## Files Created`; as subseções `### Lint Check (ruff)`,
`### Type Check (mypy)`, `### Tests (pytest)` viram `### Lint`, `### Typecheck`, `### Testes` com o comando do projeto
(`{{LINT_CMD}}`…); `/release`, `/iterate`, `/build` viram o nome da skill (`sdd-release`, …). `DEFINE_TEMPLATE.md`:
sai a linha de Terraform/Terragrunt, `{src/ | functions/ | gen/ | deploy/}` vira `{pasta(s) do projeto}`, WAF×runner
e SSH saem, "define-agent" fica (é o autor). `DESIGN_TEMPLATE.md`: snippets `python` viram ```` ```text ```` com
pseudocódigo neutro, "Cloud Logging"/"Cloud Run patterns"/"Pydantic + LLM output"/"pytest 80%" saem ou viram genérico.
Cada troca conferida contra os testes que leem os moldes (`test_contrato_build_release`, `test_f13_textos`,
`test_f18_f20_textos`, `test_f19_textos`, `test_kb_dominios`, `test_playbook_curator`, `test_patterns_lint`,
`test_hooks`, `test_correcoes_w0`) e contra o `design-lint.py`/`report-lint.py`.
**Rationale:** defeito (a skill pede seção que o molde não tem) e sobras de outro domínio (P1).
**Consequences:** nenhum molde destes é levado por skill gerada (medido: nenhuma das 15 cita o caminho deles), então
nenhuma versão de skill gerada muda por isso.

### Decision 6: `docs/`, README e o exemplo do starter

| **Status** | Accepted | · | **Date** | 2026-11-13 |

**Choice:** `raiz/README.md` (PT e EN): "As 18 skills são geradas do sdd-open"; sai o parágrafo das 3 congeladas;
a tabela das fases diz onde cada documento fica. `raiz/docs/quickstart*.md`: sai o "Opcional: valide os artefatos
localmente" com os 3 validadores; os caminhos `sdd/` viram `sdd/features/`/`sdd/reports/`. `raiz/docs/workflow*.md`:
o relatório do Build aponta a `sdd-handoff`, depois a `sdd-release` (nota 9). Quickstart: "projeto começado numa
versão anterior, com documentos em `sdd/` ou `.claude/sdd/`: as skills os leem de onde estiverem" no lugar de "com
`.claude/sdd/`, continuam nela" e de "até a próxima geração". `exemplos/baixar-nfse/README.md` (decisão do Roberto): o aluno guarda BRAINSTORM, DEFINE e DESIGN em
`sdd/features/`; o relatório fica em `sdd/reports/`; sai "registre que o validador não rodou"; o nome
"SDD Build by RDD" fica (botão). Os 4 documentos do exemplo não mudam.
**Rationale:** regra "gerado ou retirado"; o texto que o aluno lê bate com as skills.

### Decision 7: o teste do iniciante para as 3

| **Status** | Accepted | · | **Date** | 2026-11-13 |

**Choice:** `scripts/iniciante2.py` (novo; base no `iniciante.py` da F17b; notas 2, 3 e 7): `claude -p --tools ""`, pasta
temporária vazia, `--strict-mcp-config` com MCP vazio, `--setting-sources ""`, várias voltas por `--resume`, roteiro escrito antes, até 14 voltas), com o
`SKILL.md` gerado e as references coladas no system prompt. Pedidos de aluno (escritos antes, em
`INICIANTE-roteiro.json`), num domínio diferente do exemplo (empréstimo de notebooks): **define** recebe um BRAINSTORM
curto; **design** recebe BRAINSTORM e DEFINE e uma volta com a stack; **build** recebe os três, sem o projeto.
Juízes: além dos da F17b, o validador (`validate_*`, `scripts/validate`) conta como script exigido; no build, "finge
que construiu" (1ª pessoa no passado sem negação, "testes passaram", `Status: Complete`) reprova e a entrega é dizer
que precisa do projeto. `--autoteste` roda os juízes contra 8 respostas (7 sabotadas) antes da rodada (LM-002).
**Controle de simplicidade:** o mesmo roteiro, 3 vezes, sobre a skill congelada da `v1.5.18`; a mediana de voltas
até a entrega da gerada ≤ a da congelada + 1. Uma rodada fora do Claude fica fora (sem crédito na OpenAI).
Critério (escrito antes): define e design passam só se o documento sai no chat sem afirmar que foi gravado, nenhum
comando é pedido ao aluno e nenhum script é exigido; build passa só se não finge (nenhum arquivo dito escrito,
nenhum teste dito rodado), diz que precisa do projeto acessível e não pede comando ao aluno. Pergunta sem entrega no
fim do roteiro reprova. 3 execuções por skill.

### Decision 8: a tabela de paradas

| **Status** | Accepted | · | **Date** | 2026-11-13 |

**Choice:** `evidence/F17C_STARTER_ETAPA3/PARADAS.md`, colunas `parada · v1.5.18 · gerada · nova? · OK do Roberto`,
montada lendo o texto da tag `v1.5.18` e o gerado (geração de ensaio); as paradas listadas pela comparação (§3, lado
do starter) são a base. Toda linha nova vai ao Roberto numa pergunta D2.

### Decision 9: `ux-review-builder` e `sdd-engenharia-reversa-saas` nas pastas do Open

| **Status** | Accepted | · | **Date** | 2026-11-13 |

**Context:** revisão do DESIGN, nota 4: as duas geradas ainda guardavam documento em `sdd/` sem subpastas (a
`ux-review` gerada pela builder lia o DEFINE "lado a lado"; a engenharia, sem `sdd/config.yaml`, gravava em `sdd/` e
perguntava a pasta ativa). **Decisão do Roberto (2026-11-13): incluir as duas.**
**Choice:** `ux-review-builder` 1.6.0: o padrão e o modelo em `sdd/`, o DEFINE em `sdd/features/`, o UX_REVIEW em
`sdd/reviews/`, com a frase do documento antigo; o validador exige `sdd/features/`, `sdd/reviews/` e "de onde
estiver" na `ux-review` gerada e aceita essas duas subpastas (as outras continuam recusadas); teste novo. A
`sdd-engenharia-reversa-saas` 1.2.0 grava sempre em `sdd/features/`; a pergunta da pasta ativa fica só para o mesmo
documento deste ciclo em duas pastas. `manifest.json` e `evals/cases.json` acompanham as versões.
**Consequences:** um pacote gerado pela builder 1.5.0 reprova no validador novo até ser regerado (CHANGELOG); o
AT-010 ("as 15 da F17b saem iguais") passa a ter estas duas como exceção, com versão nova.

---

## File Manifest

| # | Arquivo | Ação | Propósito | Dependências |
|---|---|---|---|---|
| 1 | `.agents/skills/sdd-define/web/**` | criar | modo web (Decision 3) | — |
| 2 | `.agents/skills/sdd-design/web/**` | criar | modo web (Decision 3) | — |
| 3 | `.agents/skills/sdd-build/web/**` | criar | modo web (Decision 3) | — |
| 4 | `.agents/skills/sdd-{define,design,build}/SKILL.md` | modificar | linha do modo, "não finja", pergunta da 1ª vez; versões (Decision 4) | 1–3 |
| 5 | `sdd/templates/fragments/VERIFY_GATE.md` | modificar | "Eu abri … e vi …" no `manual-ux` (Decision 4) | — |
| 6 | `sdd/templates/{DEFINE,DESIGN,BUILD_REPORT}_TEMPLATE.md` | modificar | Decision 5 | — |
| 7 | `scripts/gerar-starter.py` | modificar | pasta-base (Decision 1) | — |
| 8 | `scripts/starter/{lista.txt,openai.tsv,modos.tsv}` | modificar | Decisions 1, 2 | 1–3, 7 |
| 9 | `scripts/starter/raiz/{README.md,docs/*.md,exemplos/baixar-nfse/README.md}` | modificar | Decision 6 | 8 |
| 10 | `tests/test_gerar_starter.py` | modificar | réplica sem congeladas, as 3 com as versões da `v1.5.18`; pasta-base; AT-001–AT-003, AT-008, AT-009 | 7–9 |
| 11 | `tests/test_f17c_textos.py` | criar | AT-004–AT-007 | 1–6 |
| 12 | testes com contagem ou versão fixada: `test_decisoes_lint`, `test_contrato_build_release`, `test_correcoes_w0`, `test_f14_textos`, `test_f15_slots_textos`, `test_f18_f20_textos`, `test_f19_textos`, `test_f21_textos`; `test_f17b_textos` (`CaminhoCurto` olha só a pasta do modo; nota 1) | modificar | AT-010 | 1–4 |
| 14 | `.agents/skills/ux-review-builder/**`, `.agents/skills/sdd-engenharia-reversa-saas/**` | modificar | Decision 9 | — |
| 15 | `tests/test_f17c_gerador.py` | criar | AT-002, AT-003, AT-008, AT-009 (separado do de textos) | 7–9 |
| 13 | `MANIFEST.txt` | modificar | arquivos novos | 1–3, 11 |

**Total Files:** 15

---

## Landmines aplicáveis

Varredura rodada em 2026-11-13 (`playbook-lint.sh --grep` com: gerado, modo, lint, version, teste, regex, sabotagem,
baseline, publish-gate, exemplo, ls, prosa) mais o `## Sempre`.

| Landmine (⛔) | Fonte | Veredito | Como / Por quê |
|---|---|---|---|
| gate que só confere fiação | LM-001 | ✔ tratado | o gerador roda numa réplica com tag; o teste do iniciante executa o comportamento |
| asserção sem baseline vermelho | LM-002 | ✔ tratado | cada teste novo rodado contra `53bba4a` antes da mudança |
| review sobre diff vazio | LM-003 | ✔ tratado | commit antes de cada rodada; `git diff --stat` conferido |
| sabotagem com `git checkout --` | LM-009 | ✔ tratado | só em cópia de `git archive` |
| cenário escrito e não executado | LM-011 | ✔ tratado | o teste do iniciante roda as 3 skills geradas |
| número de 11 dígitos / CPF no pacote | LM-012 | ✔ tratado | Decision 3, item 6 (medido no protótipo) |
| edição por âncora apaga testes | LM-013 | ✔ tratado | contagem de testes antes e depois; trocas exatas |
| chave por extenso em log | LM-020 | ✔ tratado | os logs do iniciante não têm segredo |
| tag no arquivo gerado | LM-022 | ✔ tratado | a regra continua; o modo não leva tag |
| aceite que cala a linha | LM-023 | ✔ tratado | nenhum aceite novo no `lint-aceitos.tsv` (o texto do starter passa no lint, medido) |
| `ls a b` com caminho ausente | LM-025 | N.A. | nenhuma checagem de existência por `ls` nesta frente |
| regex de comando deixa passar a obrigação em prosa | LM-026 | ✔ tratado | o AT-005 confere também as linhas de checklist que citavam os validadores ("`validate_…` passa"), não só blocos de shell |

---

## Contrato de aceite

N.A. (1 camada: scripts e textos do pacote).

## Agent Assignment Rationale

| Agent | Files Assigned | Why This Agent |
|---|---|---|
| (general) | todos | sem especialista no harness |

---

## Code Patterns

### Pattern 1: `modos.tsv` com pasta-base

```python
def ler_modos(arq: Path) -> dict[str, tuple[str, str]]:
    """`skill<TAB>arquivo de modo[<TAB>pasta-base]`, relativos à skill; sem a base, a raiz da skill."""
    modos = {}
    for linha in arq.read_text(encoding="utf-8").splitlines():
        if not linha.strip() or linha.startswith("#"):
            continue
        c = linha.split("\t")
        if len(c) not in (2, 3) or not all(x.strip() for x in c):
            raise Falha(65, "modos.tsv: linha sem 2 ou 3 campos (skill, arquivo de modo[, pasta-base]): %s" % linha[:60])
        base = c[2] if len(c) == 3 else "."
        if Path(base).is_absolute() or ".." in Path(base).parts:
            raise Falha(65, "modos.tsv: a pasta-base de %s sai da skill: %s" % (c[0], base))
        modos[c[0]] = (c[1], base)
    return modos
```

`compor(origem, destino, modo_rel, base)`: `raiz = origem / base` (65 se não for pasta); os citados resolvem em
`raiz / rel` e vão para `destino / rel`; o arquivo de modo (`origem / modo_rel`) não vai.

---

## Data Flow

tag → árvore → (skill de modo? compor com a pasta-base : copiar) → trocas → regras → lint → versões → destino.

## Integration Points

`git`; `claude` CLI só no teste do iniciante (evidência, fora do gate).

## Testing Strategy

| Tipo | Escopo | Ferramenta | Meta |
|---|---|---|---|
| gerador | AT-001–AT-003, AT-008, AT-009 | `tests/test_gerar_starter.py` (réplica sem congeladas; as 3 com as versões da `v1.5.18`) | exits e saída |
| texto | AT-004–AT-007 | `tests/test_f17c_textos.py` (Open e saída gerada); no AT-005, o `cmd` do Verify Gate dos documentos de exemplo (`assets/`) é isento: é o comando do projeto do aluno, não um pedido a ele (nota 12) | trechos e ausências |
| regressão | AT-010 | suítes existentes | verde |
| comportamento | teste do iniciante | `claude -p --tools ""`, 3 × 3 | 3 de 3 por skill |
| paradas | tabela | leitura `v1.5.18` × gerada | 0 nova sem OK |

## Error Handling

Exits do gerador inalterados (0 · 64 · 65 · 1); a pasta-base acrescenta causas de 65 (Decision 1).

## Configuration

Sem slot novo.

## Segurança

1. **Onde mora cada segredo:** N.A. — sem segredo.
2. **Quem vê e quem muda cada tabela (RLS):** N.A. — sem banco na feature (o build do aluno mantém a confirmação do projeto e a prova por leitura da migration).
3. **Credencial de cada agente ou integração:** N.A. — nada novo.
4. **Cabeçalhos e CORS do host:** N.A. — sem host.
5. **Itens aplicados no Define:** N.A. (linha Segurança do DEFINE).

## Observability

| Aspect | Implementation |
|---|---|
| Logging | saída do gerador: 1 linha por skill, com "de modo (web/MODO_WEB.md)"; o tempo do job do Windows no CI, antes e depois (nota 13, `.agents/skills` +25 arquivos), vai para o BUILD_REPORT |
| Metrics | — |
| Tracing | — |

## Advisor Ledger

| # | Nota | Severidade | Veredito | Evidência |
|---|---|---|---|---|
| 1 | `test_f17b_textos` (`CaminhoCurto`) quebra com as 3 na lista; manifest sem os testes de versão | HIGH | APLICADA | manifest #12; o teste olha a pasta do modo |
| 2 | roteiro sem o BRAINSTORM para design e build (o texto congelado exige) | HIGH | APLICADA | Decision 7; `INICIANTE-roteiro.json` |
| 3 | `iniciante.py` deixa passar o build que finge e o validador | HIGH | APLICADA | `scripts/iniciante2.py`, `INICIANTE-AUTOTESTE.log` |
| 4 | `ux-review-builder` e engenharia reversa na pasta plana | HIGH | APLICADA (decisão do Roberto: incluir) | Decision 9 |
| 5 | projeto começado na `v1.5.18`: documentos em `sdd/` ou `.claude/sdd/` | MEDIUM | APLICADA | Decision 3, item 3; `test_at004_pastas_do_open_e_entrega_no_chat` |
| 6 | regras que só o validador conferia | MEDIUM | APLICADA | Decision 3, item 4 |
| 7 | simplicidade sem controle; domínio igual ao exemplo; só no Claude | MEDIUM | APLICADA em parte (fora do Claude: sem crédito) | Decision 7 |
| 8 | CPF e CNPJ na história pelo commit verbatim | MEDIUM | APLICADA | commit desfeito antes do push (`git reset --soft 53bba4a`) |
| 9 | workflow e quickstart contradizem o novo fim do build e as pastas | MEDIUM | APLICADA | Decision 6; `raiz/docs/` |
| 10 | frontmatter do modo repete `name`, `license`, versão | LOW | APLICADA | Decision 3, item 1 |
| 11 | o AT-002 por nome não prova a origem | LOW | APLICADA | `test_at002_as_3_saem_so_do_modo_web` compara o conteúdo |
| 12 | AT-005 sem dizer o que é isento | LOW | APLICADA | Testing Strategy |
| 13 | custo de CI não medido | LOW | APLICADA | Observability (no BUILD_REPORT) |
| 14 | o design do Open pergunta a stack mesmo com ela escrita | LOW | APLICADA | Decision 4 |
| 15 | build gerado com 503 linhas | LOW | APLICADA | Decision 3, item 8 (495) |

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.1 | 2026-11-13 | design-agent | Revisão do DESIGN em contexto novo (15 notas, 4 HIGH), todas aplicadas (a 7 em parte); decisão do Roberto: as duas skills de pasta plana entram (Decision 9) |
| 1.0 | 2026-11-13 | design-agent | Initial version |

## Next Step

**Ready for:** `/sdd-build sdd/features/DEFINE_F17C_STARTER_ETAPA3.md`
