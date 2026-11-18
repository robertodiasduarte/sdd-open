# DESIGN: F17b — starter gerado, etapa 2

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | F17B_STARTER_ETAPA2 |
| **Date** | 2026-11-13 |
| **Author** | design-agent |
| **DEFINE** | `sdd/features/DEFINE_F17B_STARTER_ETAPA2.md` (v1.0) |
| **Status** | Ready for Build |

---

## Architecture Overview

```text
 sdd-open (tag vX.Y.Z)                                        clone do sdd-starter
 ─────────────────────                                        ────────────────────
 .agents/skills/<15 da lista>  ──┐
   sdd-release/references/MODO_INICIANTE.md  (skill de modo)
 sdd/templates/… (moldes)        │
 scripts/starter/                │
   lista.txt (15) · openai.tsv (15 linhas)
   modos.tsv  ← NOVO: sdd-release<TAB>references/MODO_INICIANTE.md
   trocas/<skill>.md (+ brainstorm, handoff, governanca)
   raiz/{README.md, scripts/, .github/, docs/, exemplos/, tests/}  ← docs/exemplos/tests NOVOS
                                 ▼
 scripts/gerar-starter.py
   por skill:  é de modo? ── sim ─► compor(): SKILL.md = frontmatter do Open (description do modo)
                    │                         + corpo do modo; leva só os arquivos citados (fecho)
                    não
                    ▼
               cópia da skill inteira (como na F17)
   depois, igual para todas: trocas → fluxo encadeado sai → moldes → caminhos → identificação →
   GENERATED/MIGRAR → openai.yaml → GERADO.txt
   raiz/ → saida/ (README, scripts, workflows, docs, exemplos, tests) → lint → versões → destino
                                                                                  ▼
                                                     skills/<15>, docs/, exemplos/, tests/, …, GERADO.txt
 starter CI: check-gerado.py confere skills geradas e, inteiras, scripts/ .github/workflows/ docs/ exemplos/ tests/
```

## Components

| Componente | Papel |
|---|---|
| `scripts/gerar-starter.py` | ganha `compor()` (skill de modo) e as pastas novas de `DONO_INTEIRO` |
| `scripts/starter/modos.tsv` | `skill<TAB>arquivo de modo relativo à skill` (nesta frente, 1 linha) |
| `.agents/skills/sdd-release/references/MODO_INICIANTE.md` | o caminho curto da release (GitHub + Vercel), com frontmatter próprio (`description`) |
| `.agents/skills/ux-review-builder/` | 22ª skill do Open (porte da 1.4.0 do starter) |
| `scripts/starter/raiz/{docs,exemplos,tests}/` | semente: os arquivos do starter `v1.5.17`, atualizados |
| `scripts/starter/raiz/scripts/check-gerado.py` | `DONO_INTEIRO` ganha `docs`, `exemplos`, `tests` |

---

## Key Decisions

### Decision 1: a lista passa a 15, na ordem das fases

| **Status** | Accepted | · | **Date** | 2026-11-13 |

**Context:** decisões 1 a 3 do brainstorm.
**Choice:** `lista.txt` ganha, depois das 10 da F17, `sdd-brainstorm`, `sdd-handoff`, `sdd-governanca`, `sdd-release`,
`ux-review-builder`; `openai.tsv` ganha as 5 linhas com os textos do `agents/openai.yaml` do starter `v1.5.17` como
semente (sem mudar o que o aluno vê no botão).
**Rationale:** a ordem fixa a saída (AT-005 da F17); o texto do botão já é conhecido do aluno.
**Alternatives Rejected:** 1. reescrever os textos dos botões — rejeitada: muda o que o aluno vê sem pedido.
**Consequences:** o comentário de cabeçalho da `lista.txt` passa a dizer "3 congeladas até a F17c".

### Decision 2: a regra "skill de modo" monta o `SKILL.md` do starter só a partir do arquivo de modo

| **Status** | Accepted | · | **Date** | 2026-11-13 |

**Context:** a `sdd-release` do Open tem 73 citações ao `init` e 500 linhas; a decisão 5 do brainstorm escolheu um
arquivo de modo.
**Choice:** `scripts/starter/modos.tsv` diz quais skills são de modo e qual o arquivo. Para essas, antes das trocas, o
gerador monta uma pasta nova da skill com:
1. `SKILL.md` = o frontmatter do `SKILL.md` do Open com `description` e `compatibility` trocados pelos do
   frontmatter do arquivo de modo (os dois são obrigatórios no modo: sem a `compatibility` dele, a do Open, que fala
   de slots e scripts do `init`, vazaria); depois, o corpo do arquivo de modo (sem o frontmatter dele). O corpo traz
   o bloco de 2 linhas da identificação ("Na primeira resposta…" e a linha `` `<skill> v…` ``), e o gerador confere
   que a linha é igual, byte a byte, à do `SKILL.md` do Open (senão 65): a versão tem um dono só, o frontmatter.
   O cabeçalho `GENERATED` entra depois do frontmatter, como em toda skill gerada;
2. os arquivos que o corpo do modo cita, pelo padrão fechado `(references|assets|scripts)/[A-Za-z0-9_./-]+` com
   extensão, com fecho (um arquivo levado que cita outro leva o outro), copiados da skill do Open;
3. o arquivo de modo **não** vai (virou o `SKILL.md`).
Depois disso, a skill segue as regras da F17 como qualquer outra (trocas da skill, moldes, caminhos, identificação,
GENERATED, MIGRAR, `openai.yaml`, `GERADO.txt`). Falhas ⇒ 65 sem gravar: arquivo de modo ausente; modo sem
frontmatter ou sem `description`; citação a arquivo que não existe na skill do Open; `description` > 1.024 caracteres.
**Rationale:** evita 73 trocas; o lint do `init` continua valendo sobre o resultado; o Open mantém um lugar só.
**Alternatives Rejected:** 1. trocas grandes — rejeitada no brainstorm · 2. lista explícita de arquivos em
`modos.tsv` — rejeitada: duplica o que o texto já diz, e a lista envelhece.
**Consequences:** o `SKILL.md` gerado da release muda quando a versão da skill do Open muda (frontmatter e
identificação), mesmo sem mudar o modo; como a versão sobe, o version gate do starter aceita.

### Decision 3: o modo iniciante parte da release do starter `v1.5.17` e muda só a conferência do deploy

| **Status** | Accepted | · | **Date** | 2026-11-13 |

**Context:** a simplicidade do iniciante é critério medido; o aluno do módulo 7 publica pela integração GitHub–Vercel.
A documentação da Vercel (https://vercel.com/docs/git/vercel-for-github, lida em 2026-11-13) diz: cada commit recebe
um **commit status** por projeto; o deploy usa a **API de Deployments** do GitHub; cada PR recebe um comentário com a
URL de preview; push na branch de produção publica.
**Choice:** `MODO_INICIANTE.md` = o texto da release do starter `v1.5.17`, com as mesmas paradas (Fase 1 sozinha,
Fase 2 com o único OK, Fase 3 depois do OK) e estas mudanças:
1. Passo 1 descobre também "a Vercel publica" (sem ler segredo): há `vercel.json` ou `.vercel/` no projeto, ou o commit
   mais recente da principal tem status com contexto que começa com `Vercel` (`gh api repos/{owner}/{repo}/commits/<sha>/status`);
2. a conferência da Fase 3, quando a Vercel publica: o status `Vercel` do SHA publicado (`success` ⇒ pegar a URL por
   `gh api "repos/{owner}/{repo}/deployments?sha=<sha>"` e o `environment_url` do status mais recente do deployment;
   `pending` ⇒ esperar e consultar de novo, até 10 min; `failure`/`error` ⇒ dizer o que viu e o link do status, sem
   refazer deploy); no PR (cenário B), `gh pr checks` e o link de preview do comentário da Vercel;
3. o caminho por workflow do Actions (`gh run list …`) continua igual para quem não usa Vercel;
4. o texto diz que o comportamento da Vercel vem da documentação dela (inferência até o primeiro uso real);
5. sem nenhuma instrução de login ou token (`vercel login`, `VERCEL_TOKEN`, `gh auth login --with-token`): se o `gh`
   não está logado, o caminho é o que a v1.5.17 já dizia (parar e explicar).
6. sem gravar `sdd/ambiente.md`: a new-session gerada desde a F17 não usa esse arquivo; o modo lê, como ponto de
   partida, o `sdd/config.yaml` da frente (onde a new-session grava o que descobriu) ou o `sdd/ambiente.md` antigo, e
   a conferência da migration passa a ser só a seção `## Migrations aplicadas` do BUILD_REPORT (revisão do DESIGN,
   nota 3; vai para a tabela de paradas como diferença, não como parada nova);
7. a Vercel se reconhece pelo status do commit (o sinal que vale); `vercel.json`/`.vercel/` são só pista; o endereço
   devolvido é o **deste deploy**, e o texto diz isso (nota 13).
Frontmatter do modo: `description` da v1.5.17 (sem citar o Open) e `compatibility` própria (git; `gh` com o login
que já existe; nenhum token). A seção `## Como falar com o aluno` vem junto (o `publish-check` do starter exige).
"Exatamente 1 ponto de aprovação" se confere por: uma só linha `**Posso publicar?**` e a regra "Nunca um segundo
ponto de parada" presente; o "OK novo" quando a pasta muda depois do OK é a mesma parada repetida, como na v1.5.17
(nota 15).
**Rationale:** o aluno não perde nada do que já sabe; a única coisa nova é olhar o lugar certo.
**Alternatives Rejected:** 1. reescrever do zero a partir da release do Open — rejeitada: traria as regras do
mantenedor · 2. CLI da Vercel — rejeitada no YAGNI.
**Consequences:** a release do Open ganha 1 linha no topo ("projeto sem `sdd/bin/`? siga
`references/MODO_INICIANTE.md`"); para caber em 500, uma linha redundante sai (medida no build).

### Decision 4: o caminho sem terminal das leves é texto do Open, condicionado, e o que é só do Open sai por troca

| **Status** | Accepted | · | **Date** | 2026-11-13 |

**Context:** decisão 1 do brainstorm; itens C da comparação da F17.
**Choice:** em cada uma, uma seção `## Sem terminal` (curta, ≤ 15 linhas), escrita para valer também no Open quando o
agente não tem acesso aos arquivos:
- **brainstorm:** sem acesso aos arquivos, entregar o documento inteiro no chat e dizer que nada foi gravado; nunca
  dizer que gravou; marcar cada contexto como fornecido, observado ou inferido; não sobrescrever em silêncio um
  BRAINSTORM existente; YAGNI com zero cortes vale ("nada saiu" é resposta);
- **handoff:** entregar no chat sem fingir que gravou (com o aviso de copiar para um arquivo); modos "continuar"
  (prompt para a próxima sessão) e "entregar" (a ficha para outra pessoa); pendências 🐛/✨ com "nenhuma" escrito; sem
  terminal, a linha do Verify Gate diz "sem gate por comando";
- **governança:** prova por script só quando o DEFINE tem Verify Gate por comando; sem ele, prova manual (o
  `prova_manual` do catálogo); "onde entregar" (no chat, sem arquivo; com arquivo, em `sdd/reviews/`); "quando não usar"
  (sem gatilho do catálogo: N.A. em 1 linha).
O que só existe no Open (`sdd/bin/handoff-lint.py`, `sdd/bin/verify-gate.sh`, `sdd/playbook.md`, o brief do revisor
com `WORKFLOW_CONTRACTS.yaml` e `governanca-fronteira.sh`) sai na cópia por troca exata. Meta: ≤ 10 trocas por skill
(A-002 do DEFINE). Os passos que valem sempre ganham, no ponto de uso, a ponte para a seção (brainstorm passo 7,
handoff passo 3b) e a prova por script da governança passa a ser condicionada ali mesmo ("**Com Verify Gate por
comando no DEFINE**…"), que é o marcador do AT-006: comando de prova só dentro desse parágrafo do `SKILL.md`; o escopo
do teste são `SKILL.md`, `references/PROCEDIMENTO.md` e `references/como-falar.md` (o `CATALOGO` descreve o
`prova_script` e só é lido quando há gate). No starter, a ficha do handoff não tem a linha Verify Gate nem o estado
do gate no prompt (troca no molde; nota 11). O `references/revisor.md` da governança fica na cópia com 2 trocas
(o gerador não tem regra para deixar arquivo de fora, e um arquivo a mais não pede nada ao aluno; nota 10).
**Rationale:** o texto serve aos dois públicos; o gerador continua mecânico.
**Alternatives Rejected:** 1. modo em arquivo também para as leves — rejeitada no brainstorm (por peso).
**Consequences:** bump minor nas três (2.4.0, 2.2.0, 2.5.0).

### Decision 5: pastas dos documentos — as geradas seguem o Open

| **Status** | Accepted | · | **Date** | 2026-11-13 |

**Context:** as skills congeladas do starter gravam em `sdd/` sem subpastas; as do Open, em `sdd/features/`,
`sdd/handoffs/`, `sdd/reviews/`. Na F17 a new-session gerada já seguiu o Open.
**Choice:** brainstorm, handoff e governança geradas usam as pastas do Open; o `README` do starter diz onde cada
documento fica e que define, design e build (congeladas) recebem o documento pelo caminho que o aluno passar. Na web
não há pasta (tudo no chat). A F17c alinha as 3 restantes.
**Rationale:** trocar pastas por troca para depois destrocar na F17c é trabalho dobrado; o aluno passa o arquivo.
**Alternatives Rejected:** 1. trocas para `sdd/` plano até a F17c — rejeitada (trabalho dobrado, 2 conjuntos de regras).
**Consequences:** entra na tabela de paradas como diferença a mostrar ao Roberto (não é parada, mas muda o que o aluno vê).
**Decisão do Roberto (revisão do DESIGN, nota 9):** pastas do Open nas geradas, e o README, o quickstart (2 idiomas)
explicam onde cada documento fica; o exemplo `baixar-nfse` é um kit do build congelado e continua em `sdd/`. Para o
kanban não mentir no starter, o molde `RESUMO_ETAPA` ganha trocas (sem a etapa "review adversarial"; DEFINE, DESIGN e
BUILD_REPORT valem em `sdd/` também; a release vale pelo commit ou PR da frente), o que pede patch em toda skill que
leva o molde (`sdd-new-session` 1.6.1, `sdd-seguranca` 1.0.2); o diagrama da brainstorm e o "Próximo passo" da
governança apontam a `ux-review` do projeto (nota 6).

### Decision 6: `ux-review-builder` no Open, com o mínimo de mudança

| **Status** | Accepted | · | **Date** | 2026-11-13 |

**Choice:** copiar a skill do starter `v1.5.17` (sem `agents/openai.yaml`, que vira linha no `openai.tsv`) para
`.agents/skills/ux-review-builder/`; versão 1.5.0, `updated` 2026-11; identificação com a URL do Open; CHANGELOG com a
entrada 1.5.0; o parágrafo "Pasta do SDD" passa a dizer que o `UX_STANDARD.md` fica em `sdd/UX_STANDARD.md` e que,
num projeto com a `sdd-ux-review`, é ela que lê o padrão na etapa entre Define e Design (a `ux-review` gerada fica
como alternativa). Conferir `skill-lint --conversa`, `test_agnostico` e o `sdd-decisoes-lint` (se tiver pergunta de
decisão sem marca, ganha a marca). A `sdd-ux-review` (2.6.0) ganha no passo 1: "se existir `sdd/UX_STANDARD.md`, é o
padrão do projeto: leia antes e aplique; diferença entre ele e o achado vira pergunta, não troca silenciosa".
**Rationale:** 117 downloads; a skill já funciona sozinha.
**Consequences:** contagens de 21 para 22 nos testes. **Decisão do Roberto (revisão do DESIGN, nota 1):** o nome
continua `ux-review-builder` e o `init`/`sync` do Open passam a copiá-la (`skills_da_fonte` e `orfaos_listar` de
`bin/sdd-open.sh`), com o lint do CI e os testes que contavam por `sdd-*`; ela entra no `AGENTS.md.tmpl`, no guia do
aluno (sai da lista do que o guia não pode citar) e nos READMEs do Open. `manifest.json` e `evals/cases.json`
acompanham a versão (nota 12).

### Decision 7: `docs/`, `exemplos/`, `tests/` passam a ser do gerador, inteiras

| **Status** | Accepted | · | **Date** | 2026-11-13 |

**Choice:** `scripts/starter/raiz/{docs,exemplos,tests}` com os arquivos do starter `v1.5.17` (48 arquivos; lint do
`init` verde e sem número de 11 dígitos, medido); `DONO_INTEIRO` do gerador e do `check-gerado.py` ganha as 3 pastas
(arquivo a mais nelas é mudança feita à mão; arquivo que saiu da semente sai do destino). Os `docs/` são atualizados
só onde citam a lista de skills ou o que mudou (release com Vercel; 3 congeladas).
**Rationale:** regra "gerado ou retirado"; a trava cobre o que o aluno lê.
**Consequences:** o `guia-do-aluno.pt-BR.md` do clone local, se for commitado lá, seria acusado como sobra: tem de nascer
no Open.

### Decision 8: o teste do iniciante roda por `claude -p --tools ""`

| **Status** | Accepted | · | **Date** | 2026-11-13 |

**Context:** "agente sem ferramentas" (como o claude.ai sem acesso a arquivo). Um subagente desta sessão tem
ferramentas e contexto do pacote.
**Choice:** `claude -p --tools "" --system-prompt-file <SKILL.md gerado com as references coladas>` com o pedido de
aluno escrito antes; 3 execuções por skill (brainstorm, handoff, governança). Critério escrito antes de rodar: nenhuma
instrução para o aluno rodar comando; o documento entregue no chat com o aviso de que nada foi gravado (ou, numa
conversa que ainda pergunta, nenhuma afirmação de arquivo gravado); nenhuma exigência de script ou de Verify Gate.
Brainstorm, handoff e governança rodam como **conversa de várias voltas** (`--resume` da sessão), com um roteiro de
respostas de aluno escrito antes, uma por volta, até a entrega ou 14 voltas; as paradas obrigatórias (perfil de
risco, validações) acontecem de verdade. **Passa** só a execução que entrega o documento no chat com o aviso de que
nada foi gravado, sem nenhum comando pedido e sem exigir script ou Verify Gate; pergunta sem entrega no fim do
roteiro **reprova** (nota 4). Para "sem ferramenta e contexto novo" valer de fato (nota 7): pasta temporária vazia
como diretório de trabalho, `--tools ""`, `--strict-mcp-config` com configuração MCP vazia, `--setting-sources ""`
quando aceito, e o log registra a versão do CLI e os flags. Log por script bash em
`evidence/F17B_STARTER_ETAPA2/INICIANTE-*.log`.
**Rationale:** sem ferramenta por construção; sem custo pago.
**Alternatives Rejected:** 1. subagente com instrução "não use ferramentas" — rejeitada: não prova · 2. modelo pela
OpenRouter — rejeitada: custo e outro modelo que o aluno não usa.

### Decision 9: a tabela de paradas

| **Status** | Accepted | · | **Date** | 2026-11-13 |

**Choice:** `evidence/F17B_STARTER_ETAPA2/PARADAS.md`: para brainstorm, handoff, governança e release, as colunas
`parada · v1.5.17 · gerada · nova? · OK do Roberto`. "Parada" = pergunta obrigatória ao aluno, ponto de aprovação,
comando que o aluno roda, condição que bloqueia o fim. Montada lendo os dois textos (o gerado vem da 2ª geração na
réplica). Toda linha "nova" vai ao Roberto numa pergunta D2; recusada ⇒ o texto do Open muda (condicionada ou
retirada do caminho sem terminal) e a tabela é refeita.

---

## File Manifest

| # | Arquivo | Ação | Propósito | Dependências |
|---|---|---|---|---|
| 1 | `.agents/skills/sdd-brainstorm/{SKILL.md,CHANGELOG.md?}` | modificar | `## Sem terminal`; 2.4.0 (AT-005) | — |
| 2 | `.agents/skills/sdd-handoff/{SKILL.md,CHANGELOG.md?}` | modificar | `## Sem terminal`; 2.2.0 (AT-005) | — |
| 3 | `.agents/skills/sdd-governanca/{SKILL.md,references/PROCEDIMENTO.md?,CHANGELOG.md?}` | modificar | `## Sem terminal`; 2.5.0 (AT-005) | — |
| 4 | `.agents/skills/sdd-release/{SKILL.md,references/MODO_INICIANTE.md,CHANGELOG.md?}` | modificar/criar | modo iniciante; 2.12.0 (AT-004) | — |
| 5 | `.agents/skills/ux-review-builder/**` | criar | 22ª skill, 1.5.0 (AT-007) | — |
| 6 | `.agents/skills/sdd-ux-review/{SKILL.md,CHANGELOG.md?}` | modificar | lê `sdd/UX_STANDARD.md`; 2.6.0 (AT-007) | 5 |
| 7 | `scripts/starter/{lista.txt,openai.tsv,modos.tsv}` | modificar/criar | as 15 (Decisions 1, 2) | 1–5 |
| 8 | `scripts/starter/trocas/{sdd-brainstorm,sdd-handoff,sdd-governanca}.md`, `trocas/_moldes/{HANDOFF_TEMPLATE,RESUMO_ETAPA}.md` | criar/modificar | o que só existe no Open (Decisions 4, 5); a release não tem troca (Decision 2) | 1–4, 9 |
| 9 | `scripts/gerar-starter.py` | modificar | `compor()`; `DONO_INTEIRO` (Decisions 2, 7) | 7 |
| 10 | `scripts/starter/raiz/{README.md,docs/**,exemplos/**,tests/**,scripts/check-gerado.py}` | modificar/criar | Decisions 5, 7 | 9 |
| 11 | `tests/test_gerar_starter.py` | modificar | réplica com 3 congeladas e as versões das 5; AT-001–AT-003, AT-008, AT-009 | 7–10 |
| 12 | `tests/test_f17b_textos.py` | criar | AT-004–AT-007 | 1–6, 9 |
| 13 | testes com contagem ou versão fixada (`21` skills, versões das 6 skills) | modificar | bumps e 22 skills (AT-010) | 1–6 |
| 14 | `MANIFEST.txt`, `README.md`, `README.pt-BR.md`, `AGENTS.md.tmpl`, `docs/pt-BR/guia-do-aluno.md` | modificar | arquivos novos; a 22ª skill | 5, 10 |
| 15 | `bin/sdd-open.sh`, `.github/workflows/publish-gate.yml` | modificar | o `init`/`sync` e o lint do CI incluem a `ux-review-builder` (Decision 6) | 5 |
| 16 | `.agents/skills/{sdd-new-session,sdd-seguranca}/SKILL.md` | modificar | patch: o molde `RESUMO_ETAPA` do starter mudou (Decision 5) | 8 |

**Total Files:** 16

---

## Landmines aplicáveis

Varredura rodada em 2026-11-13 (`playbook-lint.sh --grep` com: gerado, aceite, lint, version, tag, cenário, teste,
release, deploy, workflow, mesma linha, slot, baseline, sabotagem).

| Landmine (⛔) | Fonte | Veredito | Como / Por quê |
|---|---|---|---|
| gate que só confere fiação | LM-001 | ✔ tratado | o teste executa o gerador numa réplica e confere a saída e os exits; os de texto conferem o trecho, e o teste do iniciante executa o comportamento |
| asserção sem baseline vermelho | LM-002 | ✔ tratado | cada teste novo rodado contra `ce281d7` antes da mudança (log em `evidence/`) |
| review sobre diff vazio | LM-003 | ✔ tratado | commit antes de cada rodada; `git diff --stat` conferido |
| sabotagem com `git checkout --` | LM-009 | ✔ tratado | sabotagem só em cópia de `git archive` |
| cenário escrito e não executado | LM-011 | ✔ tratado | o teste do iniciante é executado (Decision 8), com critério escrito antes |
| edição por âncora apaga testes | LM-013 | ✔ tratado | contagem de testes antes e depois de cada edição em `tests/` |
| fallback que esconde o caminho errado | LM-017 | ✔ tratado | a skill de modo falha alto (65) em vez de cair na cópia inteira |
| `2>/dev/null` em aviso dito uma vez | LM-019 | N.A. | o gerador não chama `sdd_python_pronto` |
| chave por extenso em log | LM-020 | ✔ tratado | os logs do teste do iniciante não têm segredo; a release iniciante não pede token |
| tag no arquivo gerado | LM-022 | ✔ tratado | a regra da F17 continua: a tag fica só no `GERADO.txt` da raiz; a skill de modo não leva tag |
| aceite que cala a linha | LM-023 | ✔ tratado | o lint do passo 0 já percorre toda ocorrência; nenhum aceite novo por linha inteira |
| comparação "o slot contra ele mesmo" | LM-024 | ✔ tratado | a decisão "a Vercel publica" vem do status do commit; o arquivo do projeto é só pista, e o texto diz o que fazer quando divergem (o teste confere as duas respostas escritas) |

---

## Contrato de aceite

N.A. (1 camada: scripts e textos do pacote).

## Agent Assignment Rationale

| Agent | Files Assigned | Why This Agent |
|---|---|---|
| (general) | todos | sem especialista no harness |

---

## Code Patterns

### Pattern 1: compor a skill de modo

```python
CITA = re.compile(r"(?<![\w/.-])((?:references|assets|scripts)/[A-Za-z0-9_./-]+\.[A-Za-z0-9]+)")

def compor(origem: Path, destino: Path, modo_rel: str) -> None:
    modo = origem / modo_rel
    if not modo.is_file():
        raise Falha(65, "%s: o arquivo de modo %s não existe" % (origem.name, modo_rel))
    fm_modo, corpo = separar_frontmatter(ler(modo))          # 65 se não houver frontmatter ou description
    fm_open, resto = separar_frontmatter(ler(origem / "SKILL.md"))
    ident = linha_de_identificacao(resto, origem.name)       # a linha `<skill> v…` do SKILL.md do Open
    destino.mkdir(parents=True)
    (destino / "SKILL.md").write_bytes(juntar(trocar_campos(fm_open, fm_modo), ident, corpo).encode("utf-8"))
    pendentes, feitos = set(CITA.findall(corpo)), set()
    while pendentes:
        rel = pendentes.pop()
        if rel in feitos or rel == modo_rel:
            continue
        if not (origem / rel).is_file():
            raise Falha(65, "%s: o modo cita %s, que não existe na skill" % (origem.name, rel))
        feitos.add(rel)
        (destino / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(origem / rel, destino / rel)
        if eh_texto(origem / rel):
            pendentes |= set(CITA.findall(ler(origem / rel)))
```

### Pattern 2: teste do iniciante (log de evidência)

```bash
#!/usr/bin/env bash
# uso: iniciante.sh <skill-prompt.md> <pedido.txt> <log>
{ echo "$ claude -p --tools \"\" --system-prompt-file $1 < $2"; claude -p --tools "" --system-prompt-file "$1" < "$2"; echo "rc=$?"; } > "$3" 2>&1
```

---

## Data Flow

tag → árvore → (skill de modo? compor : copiar) → trocas → regras → lint → versões → destino.

## Integration Points

`git`; `gh` só na release iniciante (texto); `claude` CLI só no teste do iniciante (evidência, fora do gate).

## Testing Strategy

| Tipo | Escopo | Ferramenta | Meta |
|---|---|---|---|
| gerador | AT-001–AT-003, AT-008, AT-009 | `tests/test_gerar_starter.py` (réplica com as 3 congeladas e as 5 com as versões do starter `v1.5.17`) | exits e saída conferidos |
| texto | AT-004–AT-007 | `tests/test_f17b_textos.py` (Open e saída gerada) | trechos e ausências |
| regressão | AT-010 | suítes existentes + linha ≤ 500 | verde |
| comportamento | teste do iniciante | `claude -p --tools ""`, 3 × 3 | 3 de 3 por skill |
| paradas | tabela | leitura v1.5.17 × gerada | 0 nova sem OK |

## Error Handling

Exits do gerador inalterados (0 · 64 · 65 · 1); a skill de modo acrescenta causas de 65 (Decision 2).

## Configuration

Sem slot novo.

## Segurança

1. **Onde mora cada segredo:** N.A. — sem segredo; a release iniciante não pede nem guarda token.
2. **Quem vê e quem muda cada tabela (RLS):** N.A. — sem banco.
3. **Credencial de cada agente ou integração:** o `gh` do aluno, com o login que ele já tem; nada novo.
4. **Cabeçalhos e CORS do host:** N.A. — sem host.
5. **Itens aplicados no Define:** N.A. (linha Segurança do DEFINE).

## Observability

| Aspect | Implementation |
|---|---|
| Logging | saída do gerador: 1 linha por skill (agora com "de modo" quando for) e `RESULTADO:` |
| Metrics | — |
| Tracing | — |

## Advisor Ledger

| # | Nota | Severidade | Veredito | Evidência |
|---|---|---|---|---|
| 1 | `ux-review-builder` fora do padrão `sdd-*`: o `init`/`sync` não a copiariam; lint e testes contam por `sdd-*` | HIGH | APLICADA (decisão do Roberto: o `init` copia, nome mantido) | Decision 6; `bin/sdd-open.sh` `skills_da_fonte`/`orfaos_listar`; `publish-gate.yml`; `test_skill_lint`, `test_conversa`, `test_release_workflow` |
| 2 | `voce@exemplo.com` da v1.5.17 reprova no publish-gate | HIGH | APLICADA | `MODO_INICIANTE.md` com `voce@example.com` |
| 3 | release iniciante dependia do `sdd/ambiente.md`, que a new-session gerada não grava | HIGH | APLICADA | Decision 3, item 6 |
| 4 | teste do iniciante aceitava conversa sem entrega e pulava as paradas | HIGH | APLICADA | Decision 8: várias voltas, entrega obrigatória |
| 5 | regra da identificação ambígua; ordem do AT-002 | MEDIUM | APLICADA | Decision 2, item 1; DEFINE v1.1 (AT-002) |
| 6 | kanban do resumo de etapa e "Próximo passo" errados no starter | MEDIUM | APLICADA | Decision 5; `trocas/_moldes/RESUMO_ETAPA.md`, `trocas/sdd-brainstorm.md`, `trocas/sdd-governanca.md` |
| 7 | `--tools ""` não garante contexto limpo | MEDIUM | APLICADA | Decision 8 (pasta vazia, MCP vazio, settings) |
| 8 | seção separada contradiz passos que valem sempre; marcador do AT-006 indefinido | MEDIUM | APLICADA | Decision 4 (ponte no ponto de uso; marcador e escopo) |
| 9 | pastas do Open × docs do starter em `sdd/` | MEDIUM | APLICADA (decisão do Roberto) | Decision 5; quickstart PT/EN; README |
| 10 | manifest sem as trocas de molde; `revisor.md` | MEDIUM | APLICADA | manifest #8; Decision 4 |
| 11 | a linha Verify Gate continuava no handoff do starter | MEDIUM | APLICADA | `trocas/_moldes/HANDOFF_TEMPLATE.md`; `test_at006_sem_comando_no_caminho_sem_terminal` |
| 12 | builder 1.5.0 incompleta (`cases.json`, parágrafo da pasta) | LOW | APLICADA | `evals/cases.json`; `SKILL.md` "Pasta do SDD" |
| 13 | detecção da Vercel e LM-024 superestimadas; qual URL | LOW | APLICADA | Decision 3, item 7; Landmines (LM-024) |
| 14 | troca da release no manifest; `compatibility` vazando; limite do padrão de citação | LOW | APLICADA | manifest #8; Decision 2; comentário do `CITA` |
| 15 | como medir "1 ponto de aprovação" | LOW | APLICADA | Decision 3 (último parágrafo); `test_um_ponto_de_aprovacao` |

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.1 | 2026-11-13 | design-agent | Revisão do DESIGN em contexto novo (15 notas, 4 HIGH), todas aplicadas; 2 decisões do Roberto (nome da builder com o `init`; pastas do Open) |
| 1.0 | 2026-11-13 | design-agent | Initial version |

## Next Step

**Ready for:** `/sdd-build sdd/features/DEFINE_F17B_STARTER_ETAPA2.md`
