# DESIGN: F12 Contexto, patterns e governança

> Technical design for implementing F12 Contexto, patterns e governança

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | F12_CONTEXTO |
| **Date** | 2026-11-03 |
| **Author** | SDD Design by RDD |
| **BRAINSTORM** | `sdd/features/BRAINSTORM_F12_CONTEXTO.md` |
| **DEFINE** | `sdd/features/DEFINE_F12_CONTEXTO.md` (v1.3) |
| **UX REVIEW** | `sdd/reviews/UX_REVIEW_F12_CONTEXTO.md` (U1–U10) |
| **LLM Prompts** | false |
| **Status** | Ready for Build |

---

## Architecture Overview

```text
                         sdd/config.yaml (layers:, project.default_branch)
                                     │
 BRAINSTORM / notas ──► sdd-define ──┼─ passo 1.5 Contexto de domínio ─────────────────────────────┐
                                     │    contexto-lint.sh --sugerir ── sdd/patterns/dominio.md      │
                                     │    gerar → fronteira --snapshot → despacho (escada) ──────┐   │
                                     │        cartógrafo fresco (references/cartografo.md)       │   │
                                     │        grava só sdd/contexto/<slug>.md, <<<CONTEXTO >>>   │   │
                                     │    → fronteira --comparar → contexto-lint.sh <arquivo>    │   │
                                     │    reusar → contexto-lint.sh --validade                    │   │
                                     │    linha "CONTEXTO de domínio" no Technical Context ◄─────┘   │
                                     │                                                              │
                                     ├─ passos 2–10 (EARS, clarify, gate, gravar, KB)               │
                                     │                                                              │
                                     └─ passo 11 Governança (sempre; inclusive --parar)             │
                                          grava marcador + "Governança: pendente" ANTES do despacho │
                                          fronteira --snapshot → despacho (escada) ──┐              │
                                             revisor fresco (sdd-governanca/references/revisor.md)  │
                                             passos 1–4 da sdd-governanca; grava só o relatório     │
                                             <<<GOVERNANCA resultado: NA|REVISADO|PADRAO_AUSENTE|FALHA
                                          → fronteira --comparar → lê o bloco ◄──────┘              │
                                          NA/REVISADO → perguntas D2 por lacuna → AT + prova (D8)   │
                                          → linha "Governança" final, marcador removido             │
                                          2ª falha → marcador fica → verify-gate exit 5             │
                                                                                                    │
 sdd-fluxo.sh despachar cartografo|revisor-governanca → BRIEF_<papel>_<F>.md, ⏸️, exit 40 (sem subagente)
                                                                                                    │
 verify-gate.sh <DEFINE> ── marcador ativo? → 5 · linha Governança ausente/não final? → 5 (texto próprio)
                                                                                                    │
 sdd-design ── passo 1: CONTEXTO citado (--validade, sup: → 4.5) · papel de surface em aberto → pergunta D2
             ├ passo 3: "### Decision N:" é contrato → docs-extract-decisions.sh → docs/adr/index.md
             ├ passo 4.5: abre a entrada inteira da landmine (bullet + → ficha:)
             └ passo 5: "**Pattern:** patterns/<x>.md §Esqueleto (validado_em …)" → patterns-lint.sh --design
```

---

## Components

| Component | Responsibility | Technology / Pattern | Inputs | Outputs | Dependencies |
|---|---|---|---|---|---|
| `contexto-lint.sh` | lint do CONTEXTO, `--validade`, `--sugerir`, `--self-test` | bash 3.2 + awk POSIX (porte do privado, 457 l.) | CONTEXTO, `dominio.md`, playbook, `layers:` | `RESULTADO:`/`→`, exits 0/1/2/64 | git |
| `patterns-lint.sh` | lint de patterns, `--design`, `--self-test` | bash 3.2 + awk (porte, 461 l.) | pasta de patterns, DESIGN, playbook | exits 0/2/64 | `date` BSD/GNU |
| `governanca-fronteira.sh` | snapshot sha256 e comparação; prova que o agente fresco só escreveu o permitido | bash 3.2 + Python stdlib para o `-z` (porte, 110 l.) | raiz do worktree, caminhos permitidos | `MUDOU:`/`FORA:`, exits 0/1/64 | git, `shasum` |
| `docs-extract-decisions.sh` | índice de ADR com órfãos e conservação | bash 3.2 + awk (porte, 164 l. + 50 da lib, num arquivo só) | `sdd/features/DESIGN_*.md` | `docs/adr/index.md`, exits 0/2/64 | — |
| `verify-gate.sh` (delta) | 2º motivo do exit 5: linha `Governança` ausente ou não final | bash 3.2 + awk | DEFINE | exit 5 com texto e `→` próprios | — |
| `sdd-fluxo.sh despachar` (delta) | texto da parada por papel (`cartografo`, `revisor-governanca`) | bash | papel, feature, brief | ⏸️, exit 40 | — |
| `sdd-define` (delta) | passo 1.5 e passo 11; etapa 7 "Governança" no Status | Markdown de skill | — | DEFINE com as 2 linhas | scripts acima |
| `cartografo.md` / `revisor.md` | briefs do agente fresco: contrato de entrada, proibições, bloco de retorno | Markdown | 4 / 5 campos | `<<<CONTEXTO` / `<<<GOVERNANCA` | — |
| `sdd-design` (delta) | C2, C3, C4, C10, C11 | Markdown de skill | DEFINE, UX_REVIEW, CONTEXTO | DESIGN | lints |
| `sdd/patterns/README.md` | formato dos patterns e do `dominio.md` | Markdown | — | — | — |
| `sdd/WORKFLOW_CONTRACTS.yaml` | contrato de máquina reduzido (gate, cartógrafo, revisor) | YAML num subconjunto simples | — | lido por teste | — |

---

## Key Decisions

### Decision 1: Porte fiel com raízes e caminhos genéricos

| **Status** | Accepted | · | **Date** | 2026-11-03 |

**Context:** Os 2 lints do privado já respeitam o piso (bash 3.2, awk POSIX, sem array associativo), mas fixam raízes da RDD (`supabase/functions`, `wp-content/plugins/…`) e caminhos `.claude/sdd/`.

**Choice:** Copiar a estrutura e as classes de erro; trocar os caminhos (`sdd/contexto`, `sdd/patterns`, `sdd/playbook.md`, `sdd/fixtures/contexto|patterns`). `resolve_path` resolve só a partir da raiz do repositório; `resolve_basename` usa `git ls-files` e exige casamento único (rápido, respeita o `.gitignore`, sem `find` em `node_modules`). Extensões reconhecidas como âncora: as do privado mais `tsx jsx mjs cjs go rb rs java kt cs json tsv`. Duas opções novas, globais, nos dois lints: `--dominio <arq>` (só contexto) e `--playbook <arq>`, para o `--self-test` não depender do playbook nem do mapa reais do projeto. `LC_ALL=C` no topo dos 4 scripts.

**Rationale:** Abordagem A do brainstorm (decisão do Roberto). Com `--playbook` de fixture, um projeto que aposente o LM-001 não quebra o self-test.

**Alternatives Rejected:**
1. Reescrever em Python — rejeitada no brainstorm (Abordagem B).
2. `find` nas raízes declaradas em `layers:` — rejeitada: `layers:` vem vazio no `init`, e `find` atravessa pastas ignoradas.

**Consequences:** Âncora num arquivo não versionado não resolve por nome curto (só por caminho); fica dito no README de patterns.

### Decision 2: Seções genéricas do CONTEXTO e formato do mapa de domínios

| **Status** | Accepted | · | **Date** | 2026-11-03 |

**Context:** O CONTEXTO do privado tem 8 seções com nomes de tecnologia ("Tabelas", "RPCs e funções", "Edges", "Telas e rotas"); o DEFINE pede seções genéricas.

**Choice:** 7 seções, nesta ordem, iguais no lint (`SECOES`), no brief e no `WORKFLOW_CONTRACTS.yaml`: `Escopo` · `Dados` · `Operações` · `Interfaces` · `Regras vigentes` · `Landmines` · `Histórico SDD`. Cabeçalho igual ao do privado (`ctx`, `gerado_em`, `sha`, `superficies`, `sup`). O `dominio.md` é um pattern (as 6 seções de pattern) cujo `## Esqueleto` traz blocos `### ctx:<slug>` com as linhas `**Faz:**`, `**Âncoras:**` (termos entre crases: tabelas, módulos, rotas, comandos) e `sup:`. O `--sugerir` lê os termos de `**Âncoras:**` e `sup:`.

**Rationale:** "Dados/Operações/Interfaces" cobre banco, API, fila, tela e CLI sem nomear stack; o `dominio.md` como pattern passa no `patterns-lint` da mesma pasta.

**Alternatives Rejected:**
1. Seções por `layers:` (uma seção por camada) — rejeitada: o número de seções variaria por projeto e o lint não teria lista fixa.

**Consequences:** CONTEXTO do privado não passa no lint do Open sem renomear 4 seções (a F15 renomeia).

### Decision 3: `--sugerir` e `--validade` sem as heurísticas da RDD

| **Status** | Accepted | · | **Date** | 2026-11-03 |

**Context:** O privado conta camadas por tokens fixos (`supabase/functions`, `wp-content`, `.php`) e recomenda `gerar` com 0 candidatos e ≥ 2 camadas, caso que o próprio Step 1.5 dele trata como `pular`; o ref padrão é `origin/main`.

**Choice:**
- Camadas: para cada chave de `layers:` com glob não vazio, conta se o input cita o nome da camada como palavra ou o prefixo literal do glob (o trecho antes do 1º `*`, se tiver ≥ 3 caracteres). Linha `camadas=N (nomes)`.
- Recomendação: sem `dominio.md` ⇒ `pular (sem sdd/patterns/dominio.md)`, exit 0; 0 candidatos ⇒ `pular (nenhum domínio do mapa citado no pedido)`; principal válido ⇒ `reusar`; senão `gerar`. No máximo 2 candidatos impressos (≤ 2 domínios por feature); o motivo cita o 2º.
- Ref padrão de `--validade` e `--sugerir`: `origin/<default_branch>` se existir, senão `<default_branch>` (de `sdd/config.yaml`, `main` sem config); ref que não resolve ⇒ exit 2 `sha-inexistente` nomeando `--ref`.
- `termo_fraco` (sem `_ - . /` e < 6 letras) fica: evita "aula", "nota".

**Rationale:** Camada vem do config do projeto (regra 2 do 8.0); `origin/` primeiro porque o `main` local de uma worktree costuma estar atrás (é o caso desta máquina).

**Alternatives Rejected:**
1. Manter `gerar` com 0 candidatos — rejeitada: sem `ctx:` não há o que gerar (o privado já contornava no texto do Step).

**Consequences:** O DEFINE AT-002 ganha o `origin/` (v1.2).

### Decision 4: Uma fronteira sha256 para os dois agentes frescos

| **Status** | Accepted | · | **Date** | 2026-11-03 |

**Context:** O privado prova a escrita do cartógrafo com `git status --porcelain` (cego a sobrescrita de arquivo já sujo) e a do revisor com o snapshot sha256.

**Choice:** `governanca-fronteira.sh` portado (`git status --porcelain -z --untracked-files=all` e, para os ignorados de `sdd/`, `--ignored=traditional` — sem essas flags o git recolhe a pasta não rastreada ou ignorada numa linha só e o arquivo novo dentro dela fica invisível; renomeado com origem e destino, rc de git e Python checados, `sort` em byte order) e usado pelos dois papéis; o permitido do cartógrafo é `<raiz>/sdd/contexto/<slug>.md`, o do revisor o `saida:`. Acréscimos: `--snapshot` recusa (64) `<saida>` dentro do worktree (AT-006); os caminhos de incluir e de permitido passam por `pwd -P` no ancestral que existe (no macOS `/var` é link para `/private/var`: sem isso o permitido não casa com a raiz canonizada — defeito herdado do privado, achado no porte). Como o snapshot só guarda sha, o passo 11 guarda antes uma cópia do DEFINE (`cp`), que é o que permite restaurá-lo (`cp` + `cmp`). Tratamento de `FORA:` igual ao privado: nunca apagar; DEFINE em `FORA:` é regravado com o conteúdo de antes; o `saida:` que estava `AUSENTE` é removido antes do redespacho.

**Rationale:** Decisão 8 do brainstorm (P1: a prova fraca do cartógrafo é um defeito).

**Alternatives Rejected:**
1. Um script `fronteira.sh` com nome neutro — rejeitada: o plano e o "pronto quando" nomeiam `governanca-fronteira.sh`, e a F15 troca o do privado por este.

**Consequences:** Limites declarados (iguais ao privado): arquivo ignorado fora de `sdd/` e escrita fora do worktree não são vistos.

### Decision 5: Passo 1.5 e passo 11 no `sdd-define`

| **Status** | Accepted | · | **Date** | 2026-11-03 |

**Context:** No Open, o DEFINE só existe em disco no passo 9 (Gravar); a revisão de governança precisa ler o arquivo. O "Step 6.5" do privado vinha depois de um passo que já gravava.

**Choice:** `### 1.5. Contexto de domínio (cartógrafo)` entre os passos 1 e 2; `### 11. Governança (sempre, inclusive com --parar)` depois do passo 10. Nas mensagens e no `verify-gate.sh`: "o passo 11 (Governança) do sdd-define". Status do Define ganha a etapa 7 "Governança" (passo 11); a etapa 1 passa a cobrir os passos 1, 1.5 e 2. O passo 11 segue o Step 6.5 do privado com 4 mudanças: marcador gravado **antes** do despacho (decisão 9 do brainstorm); `PADRAO_AUSENTE` em vez de perguntar o padrão antes (AT-011); a prova SQL ligada ao `cmd` no próprio passo (D8); a escada de despacho do Open no lugar da ferramenta de um agente só. O "Próximo passo" do Define deixa de mandar para `/sdd-governanca`.

**Rationale:** Numerar pelo lugar real evita "Step 6.5" aparecendo depois do passo 10; o nome do PORTE fica no texto ("o Step 6.5 do PORTE").

**Alternatives Rejected:**
1. Gravar o DEFINE antes, no passo 6 — rejeitada: mexe na ordem de todas as fases que já dependem do passo 9.

**Consequences:** O DEFINE AT-009/AT-012 passa a dizer "passo 11" (v1.2).

### Decision 6: Linha `Governança` e o 2º motivo do exit 5

| **Status** | Accepted | · | **Date** | 2026-11-03 |

**Context:** AT-012/AT-013 e o achado U1 da UX.

**Choice:** Ordem, sem `--print`: marcador ativo → linha `Governança` → bloco do gate (um DEFINE sem bloco e sem linha sai 5, não 64). Na varredura do marcador, um marcador que contém `governança não rodou` (o do passo 11) imprime a mensagem da governança, não a de ambiguidade. Depois, um `awk` lê só a seção `## Technical Context`, fora de cercas, a 1ª linha `| **Governança** | <valor> | …` — a **única forma** da linha, também no passo 11 e na dispensa. Valor final aceito: `N.A.` ou `dispensada` + travessão (ou hífen) + texto que não começa com `<` nem `{`, ou `GOVERNANCA_REVIEW_` seguido de texto que não começa com `<` nem `{` (o placeholder do template não passa). Senão exit 5 com `🛑 GOVERNANÇA NÃO REVISADA (exit 5)`, o valor achado (ou `ausente`), a frase da v2.4.0, as 2 saídas numeradas (com a linha de dispensa inteira) e o `→` próprio; o `finalizar 5` ganha uma variável de motivo (`CLARIFICAR_MOTIVO=governanca`) que só troca a linha `→`. A palavra continua `RESULTADO: CLARIFICAR`.

**Rationale:** Prefixo fechado: o gate decide sem interpretar prosa. Escopo na seção evita casar uma tabela em `## Clarifications`.

**Alternatives Rejected:**
1. Exit novo (6) — rejeitada: muda o contrato de 6 exits que build, release, iterate e CI leem.

**Consequences:** As 7 fixtures de DEFINE e os DEFINEs montados em texto por `tests/test_verify_gate.py`, `test_gate_baseline.py` e `test_verify_gate_trace.py` ganham a linha (o helper `define()` de cada um); `--print` segue isento. A saída 2 da mensagem diz trocar a linha **e** o marcador, porque com o marcador no arquivo o gate continua em 5. Os textos que explicam o exit 5 (`docs/verify-gate-contract.md` + PT, `sdd-build` tabela de exits, `sdd-iterate` passo 4, `guia-do-aluno.md`, `gate-baseline.sh`) ganham o 2º motivo.

### Decision 7: Texto da parada por papel no `despachar`

| **Status** | Accepted | · | **Date** | 2026-11-03 |

**Context:** U2: o texto atual diz "o agente começa a ler o DEFINE" e "o relatório não foi gravado" para qualquer papel.

**Choice:** `case "$papel"` com 3 ramos: `avaliador` (texto atual), `cartografo` (lê o código do domínio; bloco `<<<CONTEXTO`; "nada foi gravado em sdd/contexto/"), `revisor-governanca` (lê o DEFINE; `<<<GOVERNANCA`; "o relatório de governança não foi gravado; o DEFINE está marcado como pendente: o build não passa até a revisão voltar"); o ramo `*` mantém o texto genérico de hoje. A linha "parada i de 2" é da skill, não do script.

**Rationale:** O script não sabe quantas paradas o Define terá; a skill sabe.

**Alternatives Rejected:**
1. Passar o texto por argumento — rejeitada: muda a assinatura de `despachar` (contrato da F9).

**Consequences:** `tests/test_fluxo.py` ganha 2 cenários; o `--self-test` do `sdd-fluxo.sh` não muda.

### Decision 8: Briefs e blocos de retorno

| **Status** | Accepted | · | **Date** | 2026-11-03 |

**Context:** Regra 10 do 8.0: o agente do privado (`.claude/agents/*.md`) vira brief em `references/<papel>.md`.

**Choice:**
- `sdd-define/references/cartografo.md`: entrada `ctx · saida · worktree · dominio`; processo em 8 passos sobre as 7 seções; toda linha de Dados/Operações/Interfaces/Regras com `arquivo:linha` conferido; `CONTAMINAÇÃO: sim|não` no `## Escopo`; ≤ 400 linhas; zero PII, zero banco, zero opinião; termina lintado (2 passadas); retorno `<<<CONTEXTO` com `arquivo:`, `linhas:`, `ancoras:`, `lint:`, `landmines:` e `>>>`.
- `sdd-governanca/references/revisor.md`: entrada `define · skill · padrao · worktree · saida`; passos 1–4 do `PROCEDIMENTO.md` à letra; `**Decisão:** pendente` em cada lacuna; não executa os passos 5–6; padrão ausente com gatilho ⇒ `PADRAO_AUSENTE` sem gravar nada; o `prova_script` adaptado fica no relatório e **quem o grava e liga ao `cmd` é o passo 11 do Define** (D8; o Design só o lista no manifest); retorno `<<<GOVERNANCA` com `resultado: NA|REVISADO|PADRAO_AUSENTE|FALHA`, `motivo:`, `relatorio:`, `cobertura:`, trios `lacuna:`/`muda:`/`porque:`, `>>>`.
- Nenhum dos dois cita ferramenta de um agente só; a escada é a de `sdd-build/references/contexto-fresco.md`.

**Rationale:** Mesmo molde do brief do avaliador (F7/F9).

**Alternatives Rejected:**
1. Um brief só para os dois papéis — rejeitada: entradas, proibições e retornos diferentes.

**Consequences:** A gramática do bloco `<<<GOVERNANCA` fica escrita em 3 lugares (brief, passo 11, yaml); o teste do AT-019 confere que as 3 cópias dos campos batem.

### Decision 9: `patterns-lint.sh` sem bomba-relógio

| **Status** | Accepted | · | **Date** | 2026-11-03 |

**Context:** A fixture verde do privado tem `## Validado em 2026-09-04`; com limite de 90 dias, o self-test vira vermelho sozinho em dezembro.

**Choice:** A fixture verde traz `__HOJE__`, que o `--self-test` troca pela data do dia (`date +%Y-%m-%d`) ao copiar para o temporário; a vencida usa uma data fixa antiga (2020-01-01). Limite `IDADE_MAX_DIAS=90` (do privado), escrito no README. Citação canônica: `**Pattern:** \`patterns/<x>.md §Esqueleto\` (validado_em AAAA-MM-DD)`. Mensagem de vencido com data, dias e limite (U10).

**Rationale:** P1 — defeito achado no porte é corrigido antes de construir por cima.

**Alternatives Rejected:**
1. Data distante no futuro — rejeitada: `dias_desde` negativo é tratado como "não interpretável".

**Consequences:** —

### Decision 10: Extrator de ADR num arquivo só, sobre o disco

| **Status** | Accepted | · | **Date** | 2026-11-03 |

**Context:** O privado lista DESIGNs com `git ls-files` e importa `lib/docs-extract-common.sh` (que também serve a outros 4 extratores que não viajam).

**Choice:** Um arquivo, com `md_cell`/`autolink`/`rel` embutidos; lista `sdd/features/DESIGN_*.md` do disco (glob, `LC_ALL=C` ordenado), porque no Open os artefatos SDD nem sempre são versionados; `--root`, `--out`; conservação `extraídos + órfãos = lidos` (exit 2); cabeçalho do índice sem menção a CI que regenera. Sem `DOCS_EXTRACT_FORCE_FAIL` (a sabotagem do teste usa cópia alterada do script).

**Rationale:** YAGNI (os outros extratores não viajam); disco porque `sdd/features/` desta própria família vive fora do commit.

**Alternatives Rejected:**
1. `git ls-files` — rejeitada: daria 0 DESIGNs neste repositório.

**Consequences:** Rodar o extrator neste repositório lê os DESIGNs da branch `docs/` copiados para o disco; o índice gerado **não** é commitado aqui (fica no Out of Scope do DEFINE: gate de docs).

### Decision 11: `sdd-design` — C2, C3, C4, C10 e C11 por texto

| **Status** | Accepted | · | **Date** | 2026-11-03 |

**Context:** São regras de leitura e de parada do agente que escreve o DESIGN.

**Choice:** Passo 1: ler a linha `CONTEXTO de domínio` do DEFINE; com arquivo, rodar `contexto-lint.sh --validade` (vencido ⇒ aviso no DESIGN, nunca trava) e levar os termos de `sup:` para o passo 4.5; papel de surface em aberto no `UX_REVIEW` ⇒ pergunta `[D2 · muda o produto]` "Qual o papel da surface …?" antes de escrever. Passo 3: os títulos `### Decision N:` são lidos pelo `docs-extract-decisions.sh` e pelo `design-lint.py`. Passo 4.5: para cada `LM-nnn` do `--grep`, abrir a entrada inteira (`grep -F '[LM-nnn]' sdd/playbook.md`) e a `→ ficha:` que ela aponta; a linha do `--grep` é cortada. Passo 5: citar pattern na forma canônica e rodar `patterns-lint.sh --design <DESIGN>`; exit 2 ⇒ revalidar ou deixar de citar. `UX_REVIEW_TEMPLATE.md`: a frase de `## Open UX Questions` diz que papel em aberto trava o Design. `DESIGN_TEMPLATE.md`: em Code Patterns, a linha da citação canônica.

**Rationale:** A verdade mecânica mora nos lints; o texto só manda rodá-los.

**Alternatives Rejected:**
1. Script que lê o UX_REVIEW e trava o `seguir ux-review → design` — rejeitada: escopo novo no `sdd-fluxo.sh`; C11 é "P" no PORTE.

**Consequences:** 1 pergunta nova com marca no `sdd-design` (conta no `sdd-decisoes-lint --sites`).

### Decision 12: `sdd-governanca` com delta mínimo

| **Status** | Accepted | · | **Date** | 2026-11-03 |

**Context:** Decisão 1 do programa: o Open é a fonte canônica; a skill não é reescrita.

**Choice:** Só: o brief novo; na `## Entrada`/Processo, 1 parágrafo "o passo 11 do sdd-define despacha esta skill num agente fresco com `references/revisor.md`; chamada avulsa continua valendo para revisar de novo um DEFINE"; a frase "Quem escreveu o Define não se revisa" aponta para o passo 11; versão 2.3.0 → 2.4.0.

**Rationale:** Delta-only (regra 7 do 8.0).

**Alternatives Rejected:**
1. Mover os passos 5–6 da skill para o `sdd-define` — rejeitada: duplicaria o procedimento; o passo 11 manda segui-los.

**Consequences:** O passo 5 da `sdd-governanca` (pergunta por lacuna) é o texto que o passo 11 usa.

### Decision 13: `WORKFLOW_CONTRACTS.yaml` num subconjunto que a stdlib lê

| **Status** | Accepted | · | **Date** | 2026-11-03 |

**Context:** Python 3.9 stdlib não lê YAML.

**Choice:** O arquivo usa só `chave: "texto"`, mapas aninhados por 2 espaços e listas `- "texto"`. Três chaves de topo: `verify_gate` (runner, exits, produtor `sdd-define` passo 8, consumidores `sdd-build` e `sdd-release`), `cartografo` (brief, script, ativação, 4 campos, saída, seções, retorno, permitido), `revisor_governanca` (brief, script, 5 campos, retorno, resultados, permitido, D8). O teste extrai caminhos entre crases e campos por regex e confere existência e igualdade com os briefs, o lint (`SECOES`) e o passo 11.

**Rationale:** Contrato legível por máquina sem dependência nova.

**Alternatives Rejected:**
1. JSON — rejeitada: o PORTE e a F15 esperam o mesmo nome e formato do privado.

**Consequences:** —

### Decision 14: `init`, release e MANIFEST

| **Status** | Accepted | · | **Date** | 2026-11-03 |

**Context:** O `init` já cria `sdd/contexto/`; o `sdd_faltantes` copia só `templates bin hooks review playbook.md`.

**Choice:** `sdd_faltantes` passa a listar `patterns WORKFLOW_CONTRACTS.yaml`; o `init` nunca sobrescreve (regra atual). Fixtures novas em `sdd/fixtures/contexto/` e `sdd/fixtures/patterns/` (copiadas na 1ª instalação, como as outras). `release.yml` ganha `sdd/patterns/**` e `sdd/WORKFLOW_CONTRACTS.yaml` no filtro. `MANIFEST.txt` com todo arquivo novo, `LC_ALL=C sort`.

**Rationale:** O `--self-test` dos lints precisa das fixtures no projeto instalado.

**Alternatives Rejected:**
1. Fixtures embutidas nos scripts por heredoc — rejeitada: o privado e o Open já usam `sdd/fixtures/`.

**Consequences:** `tests/test_sdd_open.py` confere as cópias.

### Decision 15: Versões e contagens

| **Status** | Accepted | · | **Date** | 2026-11-03 |

**Context:** Toda skill tocada sobe de versão; `check-versions --base v2.3.1 --base-obrigatoria`.

**Choice:** `sdd-define` 2.4.0 → 2.5.0, `sdd-design` 2.3.0 → 2.4.0, `sdd-governanca` 2.3.0 → 2.4.0 (minor: comportamento novo). `sdd-ux-review` não é tocada (o C11 mexe só em `sdd/templates/UX_REVIEW_TEMPLATE.md`). Pinos em `tests/test_contrato_build_release.py`, `test_correcoes_w0.py`, `test_matriz_new_session.py` acompanham; `tests/test_decisoes_lint.py` recebe a contagem medida depois do texto pronto; `tests/test_docs.py` conta 3 linhas no roadmap.

**Rationale:** Regra do pacote.

**Alternatives Rejected:**
1. Patch nas 3 skills — rejeitada: o Define muda de comportamento.

**Consequences:** Release `v2.4.0` por tag.

### Decision 16: Docs

| **Status** | Accepted | · | **Date** | 2026-11-03 |

**Context:** "A theme leaves this page when it ships, and its mechanism comes with its own document" (roadmap).

**Choice:** `docs/context-and-governance.md` + `docs/pt-BR/context-and-governance.md` (o que os passos 1.5 e 11 fazem, a linha de dispensa, o exit 5 depois da atualização, `dominio.md` e patterns, os 4 scripts e seus exits); roadmap EN/PT sem a linha; README EN/PT com o fluxo `brainstorm → define (com governança) → ux-review → design …`, a linha da tabela da revisão de governança dizendo que ela roda dentro do Define, e link para o doc novo; `docs/cli-conventions.md` com os exits dos 4 scripts; `docs/pt-BR/guia-do-aluno.md` com o diagrama e a seção da `sdd-governanca` ajustados.

**Rationale:** U9; `tests/test_docs.py` confere links.

**Alternatives Rejected:**
1. Só o README — rejeitada: o exit 5 pós-atualização precisa de uma página para o link da nota da Release.

**Consequences:** —

### Decision 17: Provas

| **Status** | Accepted | · | **Date** | 2026-11-03 |

**Context:** "Pronto quando" da F12 e regras 6 do 8.0, P1 e P2.

**Choice:**
- Testes novos: `tests/test_contexto_lint.py`, `test_patterns_lint.py`, `test_governanca_fronteira.py`, `test_docs_extract_decisions.py`, `test_governanca_gate.py`, `test_f12_textos.py`; cada script tem caso que passa e que falha.
- Baseline vermelha: os testes novos rodados contra a árvore da `v2.3.1` (cópia por `git archive v2.3.1` + os testes novos) falham; log em `evidence/F12_CONTEXTO/`.
- Sabotagem: 1 por script (contexto-lint sem `checa_landmines`; patterns-lint com idade não bloqueando no `--design`; fronteira comparando só o caminho, sem o sha; verify-gate sem a checagem da linha; extrator sem a conservação) ⇒ o teste correspondente falha; log em evidência.
- Codex CLI (AT-020): `evidence/F12_CONTEXTO/codex.sh` no molde da F9 (cópia commitada, `CODEX_HOME` só com `auth.json`, `--ignore-user-config`, "sem subagente nem colaborador" no prompt), 2 execuções: cartógrafo e revisor.
- Revisão de contexto fresco do DESIGN (modo `contrato`) e do build (modo `veredito`), até 2 ciclos; revisão adversarial real (claude + codex → openrouter:qwen) até `loop` PRONTO e `--conferir` CONFERE.

**Rationale:** LM-001, LM-002, P2.

**Alternatives Rejected:**
1. Provar o despacho só pelo `--self-test` — rejeitada: o P2 pede execução real no Codex.

**Consequences:** Custo: a conta do Codex (2 execuções) e ≈ US$ 1,15 por rodada da revisão real.

### Decision 18: Validador executável do bloco `<<<GOVERNANCA`

| **Status** | Accepted | · | **Date** | 2026-11-03 |

**Context:** Achado M7 da revisão do DESIGN: a gramática do bloco, a regra "ilegível = falha" e o casamento dos Gnn com o relatório só existiam em prosa; os ATs de texto provam a fiação, não o comportamento.

**Choice:** `sdd/bin/governanca-bloco.py <resposta> --saida <relatório> [--comparar <saída da fronteira>]`, Python 3.9 stdlib: lê o último bloco `<<<GOVERNANCA`/`>>>`, confere resultado, motivo, `relatorio:` × `--saida`, os trios `lacuna:`/`muda:`/`porque:`, o conjunto de Gnn × os títulos `### Gnn — ` de `## Lacunas` e, com `--comparar`, `MUDOU: <saida>` coerente com o resultado. Exits 0 válido · 1 `FALHA` · 2 inválido · 64 uso. O passo 11 o chama na volta de cada despacho.

**Rationale:** O passo 11 é a peça fail-closed da frente; a decisão "o revisor falhou?" passa a ser um exit, não uma leitura.

**Alternatives Rejected:**
1. Subcomando `--bloco` no `governanca-fronteira.sh` — rejeitada: parsing de texto livre em bash 3.2 é frágil; o pacote já tem linters em Python (`report-lint.py`, `design-lint.py`).

**Consequences:** 1 script e 1 teste a mais (AT-026); o cartógrafo não ganha validador próprio — o `contexto-lint.sh` sobre o arquivo gravado já decide.

---

## File Manifest

| # | File | Action | Purpose | Agent / Owner | Dependencies |
|---:|---|---|---|---|---|
| 1 | `sdd/fixtures/contexto/playbook.md` | Create | playbook de fixture: LM-001 ativo, LM-002 em `## Tombstones` (Decision 1) | (general) | None |
| 2 | `sdd/fixtures/contexto/dominio.md` | Create | mapa de fixture: pattern com `ctx:pedidos` e `ctx:estoque` (Decision 2) | (general) | None |
| 3 | `sdd/fixtures/contexto/app/pedidos.py` | Create | código fictício que as âncoras citam | (general) | None |
| 4 | `sdd/fixtures/contexto/valido-completo.md` | Create | CONTEXTO verde (7 seções, âncoras reais, LM-001, aviso `superficie-nao-cobre`) | (general) | 1, 2, 3 |
| 5 | `sdd/fixtures/contexto/sem-cabecalho.md` | Create | vermelho `cabecalho-ausente` | (general) | 2 |
| 6 | `sdd/fixtures/contexto/sem-secao.md` | Create | vermelho `secao-ausente` | (general) | 2 |
| 7 | `sdd/fixtures/contexto/secao-fora-de-ordem.md` | Create | vermelho `secao-fora-de-ordem` | (general) | 2 |
| 8 | `sdd/fixtures/contexto/path-morto.md` | Create | vermelho `path-morto` | (general) | 2 |
| 9 | `sdd/fixtures/contexto/linha-alem-do-fim.md` | Create | vermelho `path-morto` (linha além do fim) | (general) | 2, 3 |
| 10 | `sdd/fixtures/contexto/sup-ausente.md` | Create | vermelho `sup-ausente` | (general) | 2 |
| 11 | `sdd/fixtures/contexto/ctx-desconhecido.md` | Create | vermelho `ctx-desconhecido` | (general) | 2 |
| 12 | `sdd/fixtures/contexto/lm-morto.md` | Create | vermelho `lm-morto` (LM-002 aposentado) | (general) | 1, 2 |
| 13 | `sdd/fixtures/contexto/superficies-nao-e-ancora.md` | Create | verde: caminho inexistente só em `superficies:` | (general) | 2 |
| 14 | `sdd/fixtures/contexto/validade-template.md` | Create | molde `__SHA__` para os 3 ramos de `--validade` | (general) | None |
| 15 | `sdd/fixtures/contexto/INPUT_FIXTURE_PEDIDOS.md` | Create | pedido que cita ≥ 2 termos de `ctx:pedidos` e 2 camadas | (general) | 2 |
| 16 | `sdd/fixtures/contexto/INPUT_FIXTURE_SEM_DOMINIO.md` | Create | pedido sem termo do mapa | (general) | None |
| 17 | `sdd/bin/contexto-lint.sh` | Create | lint, `--validade`, `--sugerir`, `--self-test` (Decisions 1–3) | (general) | 1–16 |
| 18 | `sdd/fixtures/patterns/valido-completo.md` | Create | pattern verde com `__HOJE__` (Decision 9) | (general) | 1, 3 |
| 19 | `sdd/fixtures/patterns/valido-vencido.md` | Create | pattern de 2020-01-01 | (general) | 1, 3 |
| 20 | `sdd/fixtures/patterns/sem-secao.md` | Create | vermelho `secao-ausente` | (general) | None |
| 21 | `sdd/fixtures/patterns/secao-fora-de-ordem.md` | Create | vermelho `secao-fora-de-ordem` | (general) | None |
| 22 | `sdd/fixtures/patterns/path-morto.md` | Create | vermelho `path-morto` | (general) | None |
| 23 | `sdd/fixtures/patterns/lm-morto.md` | Create | vermelho `lm-morto` | (general) | 1 |
| 24 | `sdd/fixtures/patterns/linha-alem-do-fim.md` | Create | vermelho `path-morto` (caminho completo) | (general) | 3 |
| 25 | `sdd/fixtures/patterns/linha-alem-do-fim-basename.md` | Create | vermelho `path-morto` (só o nome do arquivo) | (general) | 3 |
| 26 | `sdd/fixtures/patterns/DESIGN_FIXTURE_CITA_PEDIDOS.md` | Create | DESIGN que cita `patterns/pedidos.md` | (general) | None |
| 27 | `sdd/fixtures/patterns/DESIGN_FIXTURE_CITA_INEXISTENTE.md` | Create | citação órfã | (general) | None |
| 28 | `sdd/fixtures/patterns/DESIGN_FIXTURE_SEM_CITACAO.md` | Create | DESIGN sem citação | (general) | None |
| 29 | `sdd/bin/patterns-lint.sh` | Create | lint, `--design`, `--self-test` (Decisions 1, 9) | (general) | 18–28 |
| 30 | `sdd/bin/governanca-fronteira.sh` | Create | snapshot e comparação (Decision 4) | (general) | None |
| 31 | `sdd/bin/docs-extract-decisions.sh` | Create | índice de ADR (Decision 10) | (general) | None |
| 32 | `sdd/bin/verify-gate.sh` | Modify | linha `Governança` e o 2º motivo do exit 5 (Decision 6) | (general) | None |
| 33 | `sdd/fixtures/DEFINE_FIXTURE_SEM_GOVERNANCA.md` | Create | DEFINE válido sem a linha ⇒ exit 5 | (general) | 32 |
| 34 | `sdd/fixtures/DEFINE_FIXTURE_CONTROLE.md` | Modify | linha `Governança` (exit esperado inalterado) | (general) | 32 |
| 35 | `sdd/fixtures/DEFINE_FIXTURE_GOVERNANCA.md` | Modify | linha `Governança` | (general) | 32 |
| 36 | `sdd/fixtures/DEFINE_FIXTURE_NEEDS_CLARIFICATION.md` | Modify | linha `Governança` (continua 5 pelo marcador) | (general) | 32 |
| 37 | `sdd/fixtures/DEFINE_FIXTURE_SEM_BLOCO.md` | Modify | linha `Governança` (continua 64) | (general) | 32 |
| 38 | `sdd/fixtures/fluxo/DEFINE_pronto.md` | Modify | linha `Governança` | (general) | 32 |
| 39 | `sdd/fixtures/fluxo/DEFINE_rascunho.md` | Modify | linha `Governança` | (general) | 32 |
| 40 | `sdd/fixtures/fluxo/DEFINE_sem_kind.md` | Modify | linha `Governança` | (general) | 32 |
| 41 | `sdd/templates/DEFINE_TEMPLATE.md` | Modify | linhas `CONTEXTO de domínio` e `Governança` no Technical Context, com os valores aceitos | (general) | 32 |
| 42 | `sdd/bin/sdd-fluxo.sh` | Modify | texto da parada por papel (Decision 7) | (general) | None |
| 43 | `.agents/skills/sdd-define/references/cartografo.md` | Create | brief do cartógrafo (Decision 8) | (general) | 17, 30 |
| 44 | `.agents/skills/sdd-governanca/references/revisor.md` | Create | brief do revisor (Decision 8) | (general) | 30 |
| 45 | `.agents/skills/sdd-define/SKILL.md` | Modify | passos 1.5 e 11, etapa 7, Próximo passo, Quality Gate, "Por que", versão 2.5.0 (Decision 5) | (general) | 17, 30, 32, 42, 43, 44 |
| 46 | `.agents/skills/sdd-define/references/como-falar.md` | Modify | glossário (cartógrafo, governança), Status com 7 etapas | (general) | 45 |
| 47 | `.agents/skills/sdd-governanca/SKILL.md` | Modify | delta mínimo, versão 2.4.0 (Decision 12) | (general) | 44 |
| 48 | `sdd/patterns/README.md` | Create | formato de pattern e de `dominio.md`, citação, limite de 90 dias (AT-015) | (general) | None |
| 49 | `sdd/templates/DESIGN_TEMPLATE.md` | Modify | linha da citação canônica em Code Patterns | (general) | 48 |
| 50 | `sdd/templates/UX_REVIEW_TEMPLATE.md` | Modify | papel em aberto trava o Design (C11) | (general) | None |
| 51 | `.agents/skills/sdd-design/SKILL.md` | Modify | C2, C3, C4, C10, C11, versão 2.4.0 (Decision 11) | (general) | 17, 29, 31, 48, 50 |
| 52 | `sdd/WORKFLOW_CONTRACTS.yaml` | Create | contrato reduzido (Decision 13) | (general) | 17, 30, 43, 44 |
| 53 | `bin/sdd-open.sh` | Modify | `sdd_faltantes` com `patterns` e `WORKFLOW_CONTRACTS.yaml` (Decision 14) | (general) | 48, 52 |
| 54 | `.github/workflows/release.yml` | Modify | filtro de caminhos (Decision 14) | (general) | None |
| 55 | `docs/context-and-governance.md` | Create | doc do mecanismo (Decision 16) | (general) | 17, 29–32 |
| 56 | `docs/pt-BR/context-and-governance.md` | Create | versão PT | (general) | 55 |
| 57 | `docs/roadmap.md` | Modify | sai a linha "Context and governance" | (general) | None |
| 58 | `docs/pt-BR/roadmap.md` | Modify | sai a linha "Contexto e governança" | (general) | None |
| 59 | `README.md` | Modify | fluxo, linha da revisão de governança, link | (general) | 55 |
| 60 | `README.pt-BR.md` | Modify | idem em PT | (general) | 56 |
| 61 | `docs/cli-conventions.md` | Modify | exits dos 4 scripts e o 2º motivo do 5 | (general) | 17, 29–32 |
| 62 | `docs/pt-BR/guia-do-aluno.md` | Modify | diagrama e seção da `sdd-governanca` | (general) | 45 |
| 63 | `tests/test_contexto_lint.py` | Create | AT-001–AT-004, sabotagem | (general) | 17 |
| 64 | `tests/test_patterns_lint.py` | Create | AT-004, AT-014, AT-015 | (general) | 29, 48 |
| 65 | `tests/test_governanca_fronteira.py` | Create | AT-005, AT-006 | (general) | 30 |
| 66 | `tests/test_docs_extract_decisions.py` | Create | AT-018 | (general) | 31 |
| 67 | `tests/test_governanca_gate.py` | Create | AT-012, AT-013 | (general) | 32–40 |
| 68 | `tests/test_f12_textos.py` | Create | AT-008–AT-011, AT-016, AT-017, AT-019, AT-023 | (general) | 41–52 |
| 69 | `tests/test_fluxo.py` | Modify | AT-007 (2 papéis novos; o genérico continua) | (general) | 42 |
| 70 | `tests/test_decisoes_lint.py` | Modify | contagem nova (AT-024) | (general) | 45, 51 |
| 71 | `tests/test_docs.py` | Modify | roadmap com 3 linhas; links novos (AT-022) | (general) | 55–62 |
| 72 | `tests/test_sdd_open.py` | Modify | `init` copia `sdd/patterns/README.md` e `WORKFLOW_CONTRACTS.yaml` sem sobrescrever (AT-021) | (general) | 53 |
| 73 | `tests/test_release_workflow.py` | Modify | filtro com os 2 caminhos novos (AT-021) | (general) | 54 |
| 74 | `tests/test_contrato_build_release.py` | Modify | pinos de versão | (general) | 45, 47, 51 |
| 75 | `tests/test_correcoes_w0.py` | Modify | pinos de versão | (general) | 45, 47, 51 |
| 76 | `tests/test_matriz_new_session.py` | Modify | pinos de versão | (general) | 45, 47, 51 |
| 77 | `sdd/bin/governanca-bloco.py` | Create | validador do bloco `<<<GOVERNANCA` (Decision 18) | (general) | None |
| 78 | `tests/test_governanca_bloco.py` | Create | AT-026: válido, FALHA, 7 casos inválidos, uso | (general) | 77 |
| 79 | `tests/test_verify_gate.py` | Modify | helper `define()` com a linha `Governança`; casos que esperam 5 de propósito (AT-013) | (general) | 32 |
| 80 | `tests/test_gate_baseline.py` | Modify | helper `define()` com a linha (AT-013) | (general) | 32 |
| 81 | `tests/test_verify_gate_trace.py` | Modify | DEFINE em texto com a linha (AT-013) | (general) | 32 |
| 82 | `docs/verify-gate-contract.md` | Modify | 2º motivo do exit 5 e a ordem das checagens | (general) | 32 |
| 83 | `docs/pt-BR/verify-gate-contract.md` | Modify | idem em PT | (general) | 82 |
| 84 | `.agents/skills/sdd-build/SKILL.md` | Modify | tabela de exits: 2º motivo do 5; versão 2.5.1 | (general) | 32 |
| 85 | `.agents/skills/sdd-iterate/SKILL.md` | Modify | passo 4: 2º motivo do 5; versão 2.2.1 | (general) | 32 |
| 86 | `sdd/bin/gate-baseline.sh` | Modify | mensagem do inconclusivo cita a governança | (general) | 32 |
| 87 | `MANIFEST.txt` | Modify | arquivos novos | (general) | 1–86 |

**Total Files:** 87

### Agent Assignment Rationale

| Agent / Owner | Files Assigned | Why |
|---|---|---|
| (general) | 1–87 | modo default (um agente), como nas F9–F11; sem catálogo de agentes no repositório |

**Agent Discovery:** Not available

Fora do commit (evidência, branch `docs/`): `sdd/reports/evidence/F12_CONTEXTO/` (`ev.sh`, `codex.sh`, baseline, sabotagens, logs), `sdd/reports/BUILD_REPORT_F12_CONTEXTO.md`, as revisões.

---

## Landmines aplicáveis

Varredura rodada em 2026-11-03 com `playbook-lint.sh --grep` sobre `verify-gate`, `exit 0`, `baseline`, `git status`, `review`, `untracked`, `grep -q`, `asserção`; entradas abertas inteiras.

| LM-nnn | Superfície | Tratamento |
|---|---|---|
| LM-001 | lints, fronteira, gate | ✔ cada script roda com fixtures dos dois lados e o teste exige a classe certa; 1 sabotagem por script |
| LM-002 | testes novos | ✔ baseline vermelha na `v2.3.1`; a fixture verde de patterns não envelhece (Decision 9) |
| LM-003 | fronteira e revisões | ✔ a fronteira mede untracked e ignorados de `sdd/`; commit antes de cada revisão externa |
| LM-004 | — | N.A.: sem migration (o `prova_script` só é ligado a `cmd` de projetos de usuário) |

---

## Code Patterns

### Pattern 1: Linha `Governança` no `verify-gate.sh`

Extração (um `awk` no build): só as linhas entre `## Technical Context` e o próximo `## `, pulando o que está entre cercas; a 1ª linha cujo 1º campo da tabela é `**Governança**`; o valor é o 2º campo, sem espaços nas pontas. Decisão:

```bash
if ! printf '%s' "$GOV" | grep -qE '^((N\.A\.|dispensada)[[:space:]]+(—|-)[[:space:]]+[^[:space:]]|GOVERNANCA_REVIEW_)'; then
  CLARIFICAR_MOTIVO=governanca   # só troca a linha → do finalizar 5
  # mensagem U1 em stderr (valor achado ou "ausente", a frase da v2.4.0, as 2 saídas), depois: finalizar 5
fi
```

### Pattern 2: Parada por papel no `despachar`

```bash
case "$papel" in
  avaliador)          le='o DEFINE'; retorno='o bloco inteiro da resposta, de `<<<AVALIACAO` até `>>>` (com a linha `VEREDITO: …`)'
                      nao_feito='nada foi publicado e o relatório não foi gravado.' ;;
  cartografo)         le='o código do domínio'; retorno='o bloco que começa com `<<<CONTEXTO` até `>>>`'
                      nao_feito='nada foi gravado em sdd/contexto/.' ;;
  revisor-governanca) le='o DEFINE'; retorno='o bloco que começa com `<<<GOVERNANCA` até `>>>`'
                      nao_feito='o relatório de governança não foi gravado; o DEFINE está marcado como pendente (o build não passa até a revisão voltar).' ;;
  *)                  le='o DEFINE'; retorno='o bloco final da resposta (o que começa com <<<)'
                      nao_feito='nada foi publicado e o relatório não foi gravado.' ;;
esac
```

### Pattern 3: Bloco de retorno do revisor (gramática que o passo 11 valida)

```text
<<<GOVERNANCA
resultado: NA | REVISADO | PADRAO_AUSENTE | FALHA
motivo: <1 frase>
relatorio: <o saida: exatamente como veio> | —
cobertura: <a linha **Cobertura:** do relatório> | —
lacuna: Gnn | alta|média|baixa | AT-0nn[, AT-0nn…]|—
muda: <1 frase>
porque: <1 frase>
>>>
```

Ilegível (= falha): sem o par `<<<GOVERNANCA`/`>>>`; `resultado` fora da lista; `lacuna:` sem os 3 campos; `NA` com `MUDOU: <saida>` na fronteira; `REVISADO` com `relatorio:` ≠ `saida:` ou sem `MUDOU: <saida>`; conjunto de `Gnn` do bloco ≠ títulos `### Gnn — ` de `## Lacunas` do relatório.

### Pattern 4: Citação canônica de pattern no DESIGN

```markdown
**Pattern:** `patterns/pedidos.md §Esqueleto` (validado_em 2026-11-03) — adaptações: nenhuma.
```

### Pattern 5: Bloco de domínio em `sdd/patterns/dominio.md`

```markdown
### ctx:pedidos

**Faz:** o pedido do cliente, do carrinho à entrega.
**Âncoras:** `pedido` · `pedido_item` · `app/pedidos.py` · `/pedidos`
sup: `pedido` `pedido_item` `checkout`
```

---

## Data Flow

1. **Passo 1.5.** `contexto-lint.sh --sugerir <entrada>` lê `sdd/patterns/dominio.md` e `layers:`; imprime candidatos (≤ 2), camadas, estado e `recomendacao:`. A skill aplica como `[auto · de rotina]`.
2. **gerar.** `T=$(mktemp -d)`; `governanca-fronteira.sh --snapshot <raiz> $T/antes <raiz>/sdd/contexto/<slug>.md`; despacho (subagente com o brief; sem subagente, a skill grava `sdd/reports/briefs/BRIEF_cartografo_<F>.md` e roda `sdd-fluxo.sh despachar cartografo <F> <brief>` ⇒ exit 40 ⇒ ⏸️). Na volta: `--snapshot … $T/depois`, `--comparar $T/antes $T/depois <permitido>`, `contexto-lint.sh <arquivo>`. Falha ⇒ 1 redespacho com a saída do lint anexada; 2ª ⇒ `nenhum (<motivo>)`.
3. **Passos 2–10** inalterados; o passo 9 grava o DEFINE com as 2 linhas (`Governança` provisória `pendente`).
4. **Passo 11.** Marcador + `pendente` gravados; snapshot; despacho do revisor (5 campos; ou brief + `despachar revisor-governanca` ⇒ exit 40). Na volta: comparar, validar o bloco. `PADRAO_AUSENTE` ⇒ 5 perguntas D2 ⇒ grava `sdd/GOVERNANCA_PADRAO.md` ⇒ redespacho (não conta falha). `NA` ⇒ linha final. `REVISADO` ⇒ 1 pergunta D2 por lacuna ⇒ AT novo + `.sql` + `psql` no `cmd` (ou `prova_manual` se só há produção) ⇒ linha `GOVERNANCA_REVIEW_<F>.md · a aplicadas · r recusadas · d adiadas` ⇒ marcador removido. 2ª falha ⇒ marcador fica, 🛑 com as 2 saídas.
5. **Build/release.** `verify-gate.sh` ⇒ marcador ⇒ 5; linha ausente ou não final ⇒ 5 (texto U1); senão roda o `cmd`.
6. **Design.** Lê o CONTEXTO (`--validade`), pergunta o papel em aberto, cita patterns, roda `patterns-lint.sh --design`; opcional: `docs-extract-decisions.sh`.

---

## Integration Points

| System | Type | Auth | Direction | Timeout / Retry | Failure Behavior |
|---|---|---|---|---|---|
| git | CLI local | — | leitura (`status -z`, `diff`, `cat-file`, `ls-files`) | — | erro do git ⇒ 64 (fronteira) ou 2 (`sha-inexistente`) |
| agente fresco (subagente ou sessão nova) | despacho | o do agente | ida: brief; volta: bloco `<<<…>>>` | 1 redespacho | 2ª falha: cartógrafo segue sem CONTEXTO; governança mantém o marcador |
| Codex CLI (só na prova AT-020) | CLI | `auth.json` copiado | ida | — | log com o exit real; falha da prova reprova o AT-020 |

---

## Testing Strategy

| Level | What | Tool | AT |
|---|---|---|---|
| Unit (script) | classes de erro, ramos de validade, matriz do sugerir, uso | `--self-test` + `unittest` chamando o script | AT-001–AT-004, AT-014 |
| Unit (script) | fronteira: novo, sobrescrito sujo, apagado, acento, ignorado de `sdd/`, snapshot dentro do worktree, snapshot ausente | `unittest` com repo temporário | AT-005, AT-006 |
| Unit (script) | extrator: blocos, sufixo `b`, órfão, conservação | `unittest` com `--root` temporário | AT-018 |
| Integration | `verify-gate.sh` sobre as 8 fixtures de DEFINE e variações (valor vazio, `pendente`, `N.A.` sem motivo, `--print`, `--strict`) | `unittest` | AT-012, AT-013 |
| Contract (texto) | passos 1.5/11, briefs, template, yaml, sem termo da RDD | `unittest` com regex sobre os `.md`/`.yaml` | AT-008–AT-011, AT-016, AT-017, AT-019, AT-023 |
| E2E manual | Codex CLI real, 2 execuções | `codex.sh` | AT-020 |
| Suíte | tudo, no piso | Verify Gate do DEFINE | AT-024, AT-025 |

Baseline vermelha e sabotagens: Decision 17.

---

## Error Handling

| Error | Detection | Response |
|---|---|---|
| lint sem argumento, flag desconhecida, flag sem valor | parser | exit 64 com uso; flag sem valor nunca entra em laço (teste com teto de 5 s) |
| `dominio.md` ausente no `--sugerir` | `-f` | `recomendacao: pular (sem sdd/patterns/dominio.md)`, exit 0 |
| `dominio.md` ausente no lint de um CONTEXTO | `-f` | `ctx-desconhecido` com o motivo |
| `sha`/ref inexistente | `git cat-file -e`, `rev-parse --verify` | exit 2 `sha-inexistente` |
| `git status` falha / caminho com quebra de linha | rc do git e do Python | 64, snapshot não gravado |
| snapshot dentro do worktree | prefixo do caminho | 64 |
| bloco de retorno ilegível | gramática (Pattern 3) | conta como falha ⇒ 1 redespacho |
| `FORA:` | `--comparar` exit 1 | lista; não apaga; DEFINE regravado; conta como falha |
| DEFINE antigo sem a linha | `verify-gate.sh` | exit 5 com as 2 saídas |

---

## Configuration

| Key | Source | Default | Notes |
|---|---|---|---|
| `layers:` | `sdd/config.yaml` | vazio | camadas do `--sugerir` |
| `project.default_branch` | `sdd/config.yaml` | `main` | ref padrão (`origin/<…>` se existir) |
| `IDADE_MAX_DIAS` | constante em `patterns-lint.sh` | 90 | escrita no README |
| `LIMIAR_TERMOS` | constante em `contexto-lint.sh` | 2 | — |
| `--dominio`, `--playbook` | flags | `sdd/patterns/dominio.md`, `sdd/playbook.md` | para o self-test |

Nenhum slot novo (decisão 4 do brainstorm).

---

## Security Considerations

- Fronteira de escrita dos agentes frescos por sha256 (Decision 4); limites declarados.
- O cartógrafo não consulta banco nem grava PII (brief); o `publish-gate` varre fixtures e docs.
- Nenhuma credencial: os scripts não fazem rede; a prova no Codex usa `CODEX_HOME` temporário só com `auth.json`, nunca gravado no repositório.
- `superficies:` passada ao git com globbing desligado (`set -f`) e como argv, nunca por `eval`.

---

## Observability

- Toda saída dos scripts termina em `RESULTADO:` + `→`; achados com classe estável + explicação.
- `verify-gate.sh` continua gravando o trace JSONL (o exit 5 da governança aparece como `"exit":5`).
- Linhas de status do Define (🗺️, ⚖️, ⏸️, ↻, 🛑) — UX U2–U4, U8.

---

## Requirements Traceability

| Requirement | Decision | Files |
|---|---|---|
| AT-001–AT-004 | 1, 2, 3 | 1–17, 63 |
| AT-005, AT-006 | 4 | 30, 65 |
| AT-007 | 7 | 42, 69 |
| AT-008–AT-011 | 5, 8 | 43–47, 68 |
| AT-012, AT-013 | 6 | 32–41, 67, 79–86 |
| AT-014, AT-015 | 1, 9 | 18–29, 48, 64 |
| AT-016, AT-017 | 11 | 49–51, 68 |
| AT-018 | 10 | 31, 66 |
| AT-019 | 13 | 52, 68 |
| AT-020 | 17 | evidência `codex.sh` |
| AT-021 | 14 | 53, 54, 72, 73, 77 |
| AT-022 | 16 | 55–62, 71 |
| AT-023 | 1, 8 | 68 |
| AT-024 | 15 | 45, 47, 51, 70, 74–76 |
| AT-025 | 17 | suíte inteira |
| AT-026 | 18 | 77, 78 |

---

## Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Testes que criam DEFINE em texto (sem fixture) passam a sair 5 | rodar a suíte cedo no build; cada caso ganha a linha ou passa a esperar 5 de propósito |
| A suíte passa do teto do CI | testes novos baratos (scripts locais); medir no PR |
| `date -j` (BSD) × `date -d` (GNU) | `dias_desde` do privado tenta os dois; CI em Ubuntu e macOS |
| Codex 0.163 abre colaborador apesar do prompt | condição no prompt (molde F9); se ainda abrir, registrar e repetir com `--disable multi_agent` + prompt |
| Projeto de usuário atualiza e todo DEFINE em andamento trava | decisão do Roberto (trava sempre); texto U1, doc e nota da Release com a linha de dispensa |

---

## Advisor Ledger

Preenchido pela revisão de contexto fresco do DESIGN (modo `contrato`), antes do build.

Revisão de contexto fresco do DESIGN v1.0 (`sdd/reviews/REVISAO_DESIGN_F12_CONTEXTO_20261103.md`, modo `contrato`, 14 logs `AVAL-DESIGN-01-*.log`): NEEDS_WORK, 2 HIGH, 7 MEDIUM, 7 LOW.

| # | Nota | Severidade | Veredito | Evidência |
|---|---|---|---|---|
| H1 | 3 arquivos de teste com DEFINE em texto quebram (28 falhas) e não estão no manifest | HIGH | APLICADA (manifest 79–81; DEFINE AT-013) | `AVAL-DESIGN-01-sonda-gate-simulado.log` |
| H2 | 2 formas da linha; o marcador da 2ª falha esconde as 2 saídas | HIGH | APLICADA (Decision 6: uma forma; marcador de governança imprime as 2 saídas; DEFINE AT-009, AT-012) | `AVAL-DESIGN-01-gate-casos-de-borda.log` (A, B) |
| M1 | textos do exit 5 fora do manifest | MEDIUM | APLICADA (manifest 62, 82–86; `sdd-build` e `sdd-iterate` sobem patch) | `AVAL-DESIGN-01-textos-exit5-fora-do-manifest.log` |
| M2 | porcelain recolhe pastas | MEDIUM | APLICADA (Decision 4; DEFINE AT-005) | `AVAL-DESIGN-01-porcelain-recolhe-pasta.log` |
| M3 | DEFINE em FORA sem como restaurar | MEDIUM | APLICADA (Decision 4; passo 11 com cópia e `cmp`; DEFINE AT-009) | — |
| M4 | placeholder do template passa | MEDIUM | APLICADA (Decision 6: valor seguido de `<`/`{` reprova; template nasce `pendente`; DEFINE AT-012) | `AVAL-DESIGN-01-gate-casos-de-borda.log` (C) |
| M5 | AT-015 vazio | MEDIUM | APLICADA (DEFINE AT-015: pasta de fixture com ≥ 1 pattern; README pulado) | — |
| M6 | 2 tabelas com coluna Papel | MEDIUM | APLICADA (Decision 11 e `sdd-design`: só a tabela `Surface (funcional)`; DEFINE AT-017) | `AVAL-DESIGN-01-ux-papel-tabelas.log` |
| M7 | gramática do bloco só em prosa | MEDIUM | APLICADA (Decision 18; DEFINE AT-026) | — |
| L1 | precedência não declarada | LOW | APLICADA (Decision 6; DEFINE AT-013) | `AVAL-DESIGN-01-gate-casos-de-borda.log` (D) |
| L2 | par `define→governanca` obsoleto | LOW | APLICADA em parte: a linha "Nesta skill" do `sdd-define` sai de governanca; REBATIDA_ESCOPO a remoção do par no `sdd-fluxo.sh`: a `sdd-governanca` avulsa continua valendo para revisar de novo, e o par não muda nada para quem não o chama | `AVAL-DESIGN-01-fluxo-pares.log` |
| L3 | fixtures só na 1ª instalação | LOW | APLICADA (self-test sai 64 nomeando a pasta; `docs/context-and-governance.md`) | `AVAL-DESIGN-01-init-fixtures-1a-vez.log` |
| L4 | pedido direto sem arquivo | LOW | APLICADA (passo 1.5: arquivo temporário) | — |
| L5 | exit 2 de conservação sem gatilho natural | LOW | APLICADA (sabotagem por cópia alterada, Decision 17; sem gatilho natural por construção: todo DESIGN vai a extraído ou órfão) | — |
| L6 | AT-020 não discrimina | LOW | APLICADA (DEFINE AT-020: `GOVERNANÇA NÃO REVISADA` e as 2 saídas no log) | — |
| L7 | 2 cartógrafos em paralelo; `superficies` vazio | LOW | APLICADA (passo 1.5: despacho sequencial; o cabeçalho já exige `superficies:` não vazio) | — |

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | 2026-11-03 | SDD Design by RDD | Initial version |
| 1.1 | 2026-11-03 | SDD Design by RDD | revisão de contexto fresco: 2 HIGH, 7 MEDIUM e 7 LOW (Advisor Ledger); Decision 18 nova; manifest 77 → 87 |
| 1.2 | 2026-11-03 | SDD Build by RDD | revisões do build (Deviations do BUILD_REPORT): snapshot em Python com realpath, `#HEAD` e `#PERMITIDO`, na pasta temporária com nome derivado da raiz; `superficies:` sem crase e casando arquivo; `--validade` confere o diff antes; `--design` só avisa em pattern não citado; dentro de cerca só `caminho:linha` é âncora |

---

## Next Step

Execute o **SDD Build by RDD**.
