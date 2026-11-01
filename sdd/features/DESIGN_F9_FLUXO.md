# DESIGN: F9 Fluxo encadeado e decisões

> Dois scripts em bash 3.2 com o núcleo em Python stdlib embutido — `sdd/bin/sdd-fluxo.sh` (`review-design`, `loop`, `despachar`, `seguir`, `estado`, `--self-test`) e `sdd/bin/sdd-decisoes-lint.sh` (`--sites`, `--self-test`, reusando o parser do `skill-lint.py`) —, a marca da classe com rótulo fixo no item 9 do `PERGUNTA_DECISAO.md` e em cada pergunta de decisão, o fragmento `FLUXO_ENCADEADO.md`, a subseção `### Fluxo encadeado` nas 9 skills de fase, o degrau "sessão nova" da escada de despacho ligado ao exit 40, e os itens F6, F8, F10 e F11 do PORTE nas 4 skills.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | F9_FLUXO |
| **Date** | 2026-10-31 |
| **Author** | SDD Design by RDD (sessão com Roberto Dias Duarte) |
| **BRAINSTORM** | `sdd/features/BRAINSTORM_F9_FLUXO.md` |
| **DEFINE** | `sdd/features/DEFINE_F9_FLUXO.md` (v1.3) |
| **UX REVIEW** | `sdd/reviews/UX_REVIEW_F9_FLUXO.md` (7 MUST de texto, U1–U7) |
| **LLM Prompts** | false |
| **Status** | Ready for Build |

Re-check do flag LLM Prompts (`false`): nenhum provedor ou modelo de LLM do produto citado; "prompt" aparece só como o pedido colado numa sessão nova do agente (brief de orquestração SDD) e no `codex exec` da evidência. Zero hits relevantes.

---

## Architecture Overview

```text
 skill de fase (agente)                     sdd/bin/sdd-fluxo.sh (bash 3.2 + python3 -B embutido)
 ──────────────────────────────             ────────────────────────────────────────────────────────
 pergunta [auto · de rotina] ──estado──────► estado   → lê sdd/config.yaml (flow.autonomous)
   ligado: recomendada + recibo                         0 ligado · 1 desligado · 64 inválido
 fim de fase (### Fluxo encadeado) ─seguir─► seguir <fase> <DEFINE> <próxima> [--parar]
                                               ├─ estado (acima)
                                               ├─ verify-gate.sh --print <DEFINE>   (chama, não reescreve)
                                               ├─ marcador ativo de clarificação (mesma regex do gate)
                                               └─ design-lint.py <DESIGN> (fase design)
                                               0 SEGUIR (linha de transição) · 1 PARAR · 64
 sdd-design (revisão do DESIGN) ─review-design► review-design <DESIGN>
                                               manifest: ≥3 Create · 8 termos · review.security_globs · layers.sql
                                               0 EXIGIDO · 1 DISPENSAVEL · 64 (quem chama roda)
 sdd-build 5d / revisão do DESIGN ─despachar─► despachar <papel> <F> <brief>
   (agente sem papel fresco)                   cp → sdd/reports/briefs/BRIEF_<papel>_<F>.md
                                               parada ⏸️ (rótulos do PERGUNTA_DECISAO) · 40
 F10 (futuro) ───────────────loop───────────► loop --review <dir> --ledger <arq> --rodada N [--log]
                                               META.txt + *.verdicts.jsonl + ledger + AVALIACAO
                                               0 PRONTO · 10 CONTINUAR · 20 BLOQUEADO · 30 RECIBO · 64

 CI e gate                                  sdd/bin/sdd-decisoes-lint.sh
 ──────────────────────────────             ────────────────────────────────────────────────────────
 publish-gate.yml (passo novo) ─────────────► --sites .agents/skills sdd/templates/fragments
 tests/test_decisoes_lint.py (no gate)        perguntas() do skill-lint.py (blocos ```markdown abertos)
                                              só a linha com **Sua decisão** · marca [<código> · <rótulo>]
                                              rótulos lidos do item 9 do PERGUNTA_DECISAO.md (dono único)
                                              0 · 2 (arquivo:linha — motivo) · 64
                                            --self-test → sdd/fixtures/conversa/decisoes/*.md
```

---

## Components

| Component | Responsibility | Technology | Inputs | Outputs | Depends on |
|---|---|---|---|---|---|
| `sdd-fluxo.sh` (frente) | Verbos, uso, checagem de `python3`, `despachar` e `--self-test` | bash 3.2, `set -u` | argumentos | exit + saída no padrão `RESULTADO:` + `→` | `python3`, `verify-gate.sh`, `design-lint.py`, `gate-shell-evidencia.sh` |
| núcleo Python do `sdd-fluxo.sh` | `review-design`, `loop`, `seguir`, `estado` | Python 3.9 stdlib, heredoc `python3 -B -` | DESIGN, `META.txt`, jsonl, ledger, AVALIACAO, `sdd/config.yaml` | linhas `ESTADO:`/`EXIGIDO:`/`PARAR:` + exit | — |
| `sdd-decisoes-lint.sh` | Confere marca, rótulo, recomendada, "não sei", "Outro", identificador | bash 3.2 + Python embutido | pastas/arquivos `.md`, `PERGUNTA_DECISAO.md` | `🛑 arquivo:linha — motivo`, `RESULTADO:` + exit 0/2/64 | `skill-lint.py` (`perguntas()`) |
| `PERGUNTA_DECISAO.md` item 9 | Dono da tabela das 6 marcas e do comportamento com o encadeamento ligado | Markdown | — | tabela lida pelo lint | — |
| `FLUXO_ENCADEADO.md` | Dono da ordem, do `seguir`, da linha de transição, do recibo, das paradas, do teto e da pergunta D4 | Markdown | — | lido pelas 9 skills | `PERGUNTA_DECISAO.md` |
| Subseção `### Fluxo encadeado` | Liga cada skill de fase ao `seguir`, com bloco comum + 1 linha | Markdown nas 9 `SKILL.md` | — | — | `FLUXO_ENCADEADO.md` |
| Fixtures | Os dois lados de cada exit e de cada motivo | `sdd/fixtures/fluxo/`, `sdd/fixtures/conversa/decisoes/` | — | — | — |

---

## Key Decisions

### Decision 1: Um arquivo por script, frente em bash 3.2 e núcleo em Python embutido por heredoc

| **Status** | Accepted | · | **Date** | 2026-10-31 |

**Context:** as fontes do privado são zsh (`exec zsh "$0"`) com `perl -MJSON::PP`; o piso do Open é bash 3.2 + Python 3.9 stdlib (P2) e o `tests/test_bash32.py` varre `sdd/bin/*.sh`. O brainstorm escolheu a abordagem A.

**Choice:** `sdd-fluxo.sh` e `sdd-decisoes-lint.sh` começam com `#!/usr/bin/env bash`, `set -u`, um comentário de cabeçalho que é o `uso` (impresso por `sed -n` entre duas marcas, como o privado) e `command -v python3` antes de qualquer verbo que não seja uso (sem ele: `🛑 python3 não encontrado`, `RESULTADO: ERRO DE USO`, exit 64). Cada verbo com lógica de dados roda `python3 -B - "$@" <<'PY' … PY` (heredoc com aspas: nada é expandido pelo bash), recebendo os argumentos por `sys.argv` e os caminhos do pacote por variáveis de ambiente (`SDD_FLUXO_BIN`, a pasta do script). O `despachar` e o `--self-test` são bash puro.

**Rationale:** mantém os nomes do plano e um arquivo por script como a fonte; a parte que pesa (JSON, tabela por célula, glob) fica em Python stdlib, testável pela saída.

**Alternatives Rejected:** 1. Python puro (`.py`) — foge do nome do plano e o `test_bash32` não cobre. 2. Python em arquivo separado (`sdd_fluxo_core.py`) — 2 arquivos por script, `MANIFEST.txt` e `init` com mais uma peça que pode faltar.

**Consequences:** `python3` vira obrigatório para os dois scripts (64 sem ele, AT-016). Um heredoc com aspas não aceita interpolação; os caminhos vão por ambiente.

### Decision 2: `review-design` — porte da fonte com os 8 termos fixos, os globs do slot e `layers.sql`

| **Status** | Accepted | · | **Date** | 2026-10-31 |

**Context:** a fonte procura `## [N.] File Manifest`, conta linhas numeradas cuja ação (coluna 3) começa por create/criar/novo/nova/new e testa uma regex de 14 termos (6 da RDD). Rodada nos 8 DESIGNs deste repositório, deu 8/8 EXIGIDO (13, 17, 4, 10, 17, 7, 25, 13 arquivos novos).

**Choice:** mesma extração do manifest e da ação (minúscula, sem `*`, `` ` `` e `_`). Termos fixos (Python `re`, `IGNORECASE`): `\bauth`, `\blogin\b`, `\btokens?\b`, `\bsenhas?\b`, `password`, `\bjwt\b`, `\bGRANT\b`, `rota p(ú|u)blica`. Globs: `review.security_globs` (separados por vírgula, espaços cortados) e o valor de `layers.sql`, casados por `fnmatch` contra cada caminho entre crases da coluna 2, com `**` tratado como "qualquer profundidade". Saída: `EXIGIDO: <sinais separados por " · ">` (exit 0) ou `DISPENSAVEL: <n> arquivo(s) novo(s), sem superfície de segurança no manifest` (exit 1). Manifest ausente ou sem linha numerada: `🛑 …`, `RESULTADO: MANIFEST ILEGÍVEL`, `→ rode a revisão do DESIGN mesmo assim (default seguro) e registre o motivo no Advisor Ledger`, exit 64. O `sdd/config.yaml` é procurado na raiz do repositório do DESIGN (`git -C <dir> rev-parse --show-toplevel`; sem git, a pasta atual); ausente = só os termos fixos.

**Rationale:** regra 4 (específico da RDD não viaja) e D11 do brainstorm; o slot cobre o que o projeto chama de segurança.

**Alternatives Rejected:** 1. Regex do slot em vez de glob — o aluno escreve caminho, não regex. 2. Ler `layers:` inteiro — só `sql` tem semântica de risco no pacote (é o que conta como migration no `report-lint`).

**Consequences:** os 8 DESIGNs continuam EXIGIDO pela contagem (AT-001); a F10 liga a chamada no `sdd-build` passo 0 (R13).

### Decision 3: `loop` — o núcleo da fonte, sem o 2º revisor, com `RESULTADO:` e `--log`

| **Status** | Accepted | · | **Date** | 2026-10-31 |

**Context:** a fonte decide PRONTO/CONTINUAR/BLOQUEADO/AGUARDANDO_RECIBO a partir do `META.txt`, dos vereditos e do ledger, com 9 correções de revisão embutidas (célula, rodada, última linha por id, NOVO depois do dedup, base única). Nenhuma skill do Open chama o `loop` antes da F10, que define o `META.txt`.

**Choice:** porte linha a linha da fonte, em Python, das partes 1 (review inválida por `reviewer_exit`/`auditor_exit` ≠ "0"), 2 (graves: última linha por id no `reviewer.verdicts.jsonl` com `HIGH`; `NOVO` com `HIGH` no `auditor.verdicts.jsonl`), 3 (ledger por célula: `| achado | SEV | VEREDITO | rodada=N | evidência |`, só `SEV` = `HIGH` fecha grave; id completo ou base única para `R1@engine`), refutação (`DISAGREE_EVIDENCE` sem veredito no ledger da rodada → impasse D5, sempre: não há desempate antes da F10) e 4 (avaliador: só a linha inteira `VEREDITO: X`; 0 ou 2 valores distintos → 64; `PASS_PENDENTE_RECIBO` exige `--recibo` com data `AAAA-MM-DD`). Fica de fora: `revisor2_*`, `desempate_*`, `convergencia_1o_passe`/raso, `auditor_exit 75`. A validação de entrada (jsonl, ledger, argumentos) sai 64 exatamente nos casos da fonte. Saída: as 5 linhas da fonte (`ESTADO:`, `rodada: N de T`, `graves_abertos:`, `aplicadas:`, `rebatidas:`), um `motivo:` por causa, `RESULTADO: <ESTADO>` e `→` (PRONTO → "siga para o avaliador ou a release"; CONTINUAR → "corrija, rode o Verify Gate e a revisão de novo com --rodada N+1"; BLOQUEADO → "pare: pergunta D4/D5 do FLUXO_ENCADEADO.md"; AGUARDANDO_RECIBO → "percorra o roteiro e passe --recibo"). `--log <arq>` grava `$ sdd-fluxo.sh loop <args sem o --log>`, a saída e `[exit=N]` no arquivo, e imprime e sai igual.

Precedência, a mesma da fonte e medida nela: 64 > 20 > 10 > 30 > 0 — review inválida não lê os jsonl e sai 10 mesmo sem eles; o teto D4 só vale quando o CONTINUAR vem da review; NEEDS_WORK com ciclo 1 na rodada do teto fica 10; HIGH aberto com `PASS_PENDENTE_RECIBO` sai 10. Um teste diferencial roda os 3 casos de borda no porte e na fonte (só quando a fonte existe na máquina, como evidência `loop-diferencial.log`; no gate, os 3 casos ficam como asserções do porte).

**Rationale:** fixa o contrato que a F10 vai produzir sem portar o que só ela usa; o `--log` torna desnecessário o `| tee` que o privado proíbe em texto.

**Alternatives Rejected:** 1. Porte inteiro — 30 % de código sem chamador nem fixture real no Open. 2. Formato de `META.txt` novo — a F10 porta o `adversarial-review.sh`, que já escreve o formato da fonte.

**Consequences:** a F10 acrescenta os campos do 2º revisor e o desempate como deltas, com as fixtures dela. O DOGFOOD do privado (`auditor_exit 68`) vira a fixture de review inválida.

### Decision 4: `despachar` — o degrau "sessão nova" da escada com exit 40

| **Status** | Accepted | · | **Date** | 2026-10-31 |

**Context:** `references/contexto-fresco.md` da `sdd-build` já tem a escada (1 subagente · 2 sessão nova com `sdd/reports/briefs/BRIEF_avaliador_<F>.md` · 3 outro vendor); o Codex 0.163 tem `multi_agent` estável, então a parada não é "do Codex", é de quem não abre papel fresco sozinho (DEFINE, Clarifications).

**Choice:** `despachar <papel> <FEATURE> <brief>`, bash puro: valida `papel` e `FEATURE` (`^[A-Za-z0-9_-]+$`, por `case`/`grep -E`, sem `[[ =~ ]]`), o brief (legível, não vazio); acha a raiz (`git rev-parse --show-toplevel`, senão a pasta atual); `mkdir -p sdd/reports/briefs`; `cp` para `BRIEF_<papel>_<FEATURE>.md` (sobrescreve; a saída diz o caminho) e `cmp` para conferir — quando o brief já é esse arquivo (`[ "$BRIEF" -ef "$DESTINO" ]`, que resolve relativo × absoluto e link), a cópia é pulada e o arquivo fica intacto (no macOS, `cp X X` sai 1); imprime o bloco ⏸️ (Code Pattern 3) com o retorno por papel (`avaliador` → a linha `VEREDITO: …`; outro → o bloco final `<<<…>>>`), `RESULTADO: AGUARDANDO_HUMANO`, `→ quando a pessoa colar o retorno, continue do passo que parou`; exit 40. Erro: 64, nada gravado. As 3 skills (5d da `sdd-build`, degrau 2 do `contexto-fresco.md`, revisão do DESIGN da `sdd-design`) mandam gravar o brief em `sdd/reports/briefs/BRIEF_<papel>_<F>.md`, passar esse mesmo caminho ao verbo e **parar** no exit 40, repassando a parada.

**Rationale:** o formato e os rótulos já são da F4; a F9 só dá um exit, um lugar fixo e o retorno (UX U5).

**Alternatives Rejected:** 1. Detectar o vendor pelo `sdd/config.yaml` — o projeto pode usar vários; o agente sabe o que pode. 2. Nome com data (`<F>-<papel>-<data>.md`, brainstorm) — diverge do nome que o Open já publica no degrau 2.

**Consequences:** um 2º despacho do mesmo papel sobrescreve o brief anterior (o ciclo 2 do avaliador recebe brief novo de qualquer forma).

### Decision 5: `seguir` e `estado` — a decisão de encadear por exit, lida pelo script

| **Status** | Accepted | · | **Date** | 2026-10-31 |

**Context:** com `flow.autonomous: true`, a skill deve seguir só com o gate verde e sem marcador; com `false`, nada muda (D1). O `verify-gate.sh --print` precisa de um repositório git (fora dele sai 64 — medido nesta fase).

**Choice:** `estado`: lê `flow.autonomous` do `sdd/config.yaml` da raiz (parser de 1 nível: bloco `flow:` até a próxima chave de coluna 0; valor sem aspas e sem comentário) → `encadeamento: ligado` (0), `encadeamento: desligado` (1, valor `false`, vazio, chave ausente ou arquivo ausente), ou a linha ⚠️ de U6 (64). A raiz é sempre `git -C <pasta> rev-parse --show-toplevel` (sem git, a pasta atual), com `<pasta>` = a do artefato recebido (`review-design`, `seguir`) ou a atual (`estado`). `seguir <fase> <DEFINE> <próxima> [--parar]`: pares válidos `define → governanca|ux-review|design`, `governanca → ux-review|design`, `ux-review → design`, `design → build` e `<fase> → release` com `fase` em define, governanca, ux-review, design ou build; fora disso, 64. Ordem: argumentos (64) → DEFINE legível (64) → `estado` (64 propaga) → `--parar` → desligado → `release` (D1) → **Status** do artefato da fase (`| **Status** | <valor> |` do Metadata; DEFINE para define e governanca, `sdd/reviews/UX_REVIEW_<F>.md` para ux-review, `DESIGN_<F>.md` ao lado do DEFINE para design) começa por `Ready for` → `verify-gate.sh --print` (sibling do script, rodado na raiz) sai 0 e não mostra `kind:` nem `cmd:` como `<vazio>` → marcador ativo (`[NEEDS` + ` CLARIFICATION:` fora de bloco cercado, como o gate) → na fase design: `design-lint.py` 0 e, quando o `review-design` interno sai 0 ou 64, `## Advisor Ledger` com ≥ 1 linha de dados e toda linha de severidade HIGH com veredito começando por `APLICADA` ou `REBATIDA_` → SEGUIR. SEGUIR imprime a linha de U2 com a concordância do documento (o DEFINE pronto, a GOVERNANÇA pronta, a UX REVIEW pronta, o DESIGN pronto) e `→ /sdd-<próxima> <arquivo>` (o DEFINE; para `build`, o DESIGN). PARAR imprime `PARAR: <motivo>`, `RESULTADO: PARAR` e `→ Próximo passo: /sdd-<próxima> <arquivo>`. O item 9 do `PERGUNTA_DECISAO.md` manda rodar `estado` antes da primeira pergunta `[auto]` da sessão. Como o Advisor Ledger é o que o `seguir design` lê, o `sdd/templates/DESIGN_TEMPLATE.md` ganha a seção de mesmo nome (a `sdd-design` já manda registrar a revisão nela; os DESIGNs F5–F8 a acrescentaram à mão).

**Rationale:** quem decide é o script (o porquê do `sdd-fluxo.sh` no privado: "decididos por leitura de prosa viram exit code"); `estado` evita que o agente leia o YAML.

**Alternatives Rejected:** 1. O agente lê o config — dois agentes leriam diferente. 2. `seguir` sem a fase atual — a linha de transição não saberia o que terminou.

**Consequences:** o `--self-test` do `seguir` monta um repositório temporário com `git init -q` (o gate roda na cópia do `git archive`, sem `.git`); `seguir` passa a precisar de fixtures de DEFINE e DESIGN com Status (as do `verify-gate.sh` não têm Metadata): `sdd/fixtures/fluxo/DEFINE_pronto.md`, `DEFINE_rascunho.md`, `DEFINE_sem_kind.md`, `DESIGN_pronto.md` e `DESIGN_ledger_vazio.md`.

### Decision 6: Marca com rótulo fixo, tabela no item 9, lint pela linha do Sua decisão

| **Status** | Accepted | · | **Date** | 2026-10-31 |

**Context:** UX U1 (marca crua é jargão); o `perguntas()` do `skill-lint` acha 17 negritos-com-opções em `.agents/skills`: 15 nos `como-falar.md`, 1 na `entrevista-publico.md` (decisão real) e 1 na `kb-protocol.md` (heurística de classificação para quem escreve a KB, não pergunta ao aluno). O bloco do OK da `sdd-release` (`Posso finalizar…?`) é contrato byte a byte (`tests/test_contrato_build_release.py:57`). Os exemplos do `PERGUNTA_DECISAO.md` ficam em blocos ```` ```markdown ````, que o parser ignora.

**Choice:** pergunta de decisão = achado do `perguntas()` cuja linha contém `**Sua decisão**`, depois de abrir os blocos ```` ```markdown ```` (as cercas viram linhas vazias: a numeração não muda). Marca: exatamente uma ocorrência de `[<código>…]` na linha (`\[(?:D\d+|auto)\b[^\]]*\]`), imediatamente antes do negrito da pergunta, no formato `[<código> · <rótulo>]`; `<código>` ∈ D1…D5, auto; `<rótulo>` igual ao da tabela do item 9 (lida das linhas `` | `[<código> · <rótulo>]` | … `` do fragmento, caminho por `PERGUNTA_FRAG` ou ao lado do pacote; tabela vazia → 64). Identificador técnico: `\b(?:AT|LM)-\d+\b`, `\bD\d+\b` e SHA (palavra de 7 a 40 caracteres hexadecimais com ao menos 1 dígito e 1 letra) na pergunta e nos rótulos/efeitos das opções, depois de tirar a marca e um `(ref: …)` final. As outras regras (1 recomendada e primeira, "não sei", sem "Outro") reusam as do `skill-lint` com a mesma redação de motivo (`nenhuma opção (recomendado)`, `<k> opções (recomendado); deve haver exatamente 1`, `a opção (recomendado) não é a primeira`, `sem a opção **não sei**`, `tem a opção **Outro**: …`). Zero perguntas é contado no total dos caminhos. Pergunta aberta (sem opções) leva marca no exemplo do fragmento, mas o lint só confere pergunta com opções. A pergunta do OK da `sdd-release` não tem `**Sua decisão**` e fica de fora (é D1 por construção; declarado no item 9). Com isso, `--sites .agents/skills` acha 15 (14 `como-falar.md` + `entrevista-publico.md`) e `--sites sdd/templates/fragments` acha 2 (exemplo do `PERGUNTA_DECISAO.md` e a pergunta D4 do `FLUXO_ENCADEADO.md`). A pergunta da `sdd-playbook` tira `LM-004` do texto (fica no `(ref: …)` da opção).

**Rationale:** "Sua decisão" é a parte 4 da resposta (F4): é o marcador explícito de decisão; o rótulo é a única forma de a marca se explicar sozinha.

**Alternatives Rejected:** 1. Toda pergunta do `perguntas()` — reprovaria a heurística da `sdd-kb` e o bloco do OK. 2. Marca sem rótulo — falha o teste do suporte (UX U1). 3. Denylist de jargão — específica da RDD.

**Consequences:** uma pergunta escrita sem `**Sua decisão**` escapa do lint (o `skill-lint --conversa` continua conferindo o `como-falar.md`); declarado na seção Risks.

### Decision 7: Subseção `### Fluxo encadeado` com bloco comum idêntico e 1 linha por skill

| **Status** | Accepted | · | **Date** | 2026-10-31 |

**Context:** brainstorm, decisão 4; `test_docs.py:352` e `test_contrato_build_release.py:119` fixam "Por que cada regra existe" logo antes do Encerramento.

**Choice:** no fim do `## Encerramento (obrigatório)` de cada uma das 9 skills, antes do `---` do rodapé, o título `### Fluxo encadeado`, o bloco comum (Code Pattern 1, byte a byte igual) e uma linha `Nesta skill: …` (Code Pattern 2). Teste novo confere: o bloco comum aparece uma vez em cada uma das 9, dentro do Encerramento e depois do `**Próximo passo:**` quando houver; a linha própria nomeia `seguir <fase>` nas 5 que encadeiam e "não encadeia" nas 4.

**Rationale:** um lugar, testado; os 2 testes de ordem e o rodapé não mudam.

**Alternatives Rejected:** seção `##` nova; trocar o Próximo passo (brainstorm).

**Consequences:** as 9 sobem minor; `iterate`, `release` e `new-session` não têm `**Próximo passo:**` no Encerramento: a subseção vem depois da frase do resumo de etapa.

### Decision 8: Itens F6, F8, F10, F11 como deltas de texto; F6 só com o encadeamento ligado

| **Status** | Accepted | · | **Date** | 2026-10-31 |

**Context:** regra 7 (delta-only); regra 8 (sem autonomia, D1–D5 só como formato de pergunta); DEFINE v1.1 (F6 gated).

**Choice:** `sdd-design` passo 1: o parágrafo do flag LLM Prompts ganha "Com o encadeamento ligado (`sdd-fluxo.sh estado` 0): ausente → `true` (o lado conservador), re-check com hits → `true`, proposta de verificabilidade do avaliador aceita; cada uma vira uma linha `[auto] <decisão> — porque <…> · para desfazer: <…>` em Revision History do DESIGN. Desligado: pergunte como hoje (`[auto · de rotina]`)". `sdd-define` passo 7: tabela forte/fraco (fortes: provedor ou modelo nomeado como dependência, `messages.create`/`chat.completions`, `**/prompts/**`, system prompt; fracos: "prompt", "RAG", "embeddings", "classificar", "resumir", "chatbot"), 1 forte → `true`; 2 fracos → `true`; 1 fraco → `true` com nota "conservador" em Technical Context; loop, agente, "até convergir", "a cada resposta" → "candidato a loop" na nota. `sdd-brainstorm` passo 1: tabela "Como tratar cada tipo de entrada" (ideia vaga → "conte mais" antes de qualquer opção; pedido específico → confirmar o entendimento; problema → investigar a dor; feature → questionar a necessidade; comparação → o que se ganha e o que se perde; notas/arquivo → ler tudo antes de perguntar). `sdd-ux-review` passo 1: "Leia os `sdd/reviews/UX_REVIEW_*.md` anteriores: o que já foi decidido de copy, estados e símbolos vale aqui, salvo motivo registrado".

**Rationale:** PORTE §5.3 com o mínimo de texto; nenhum passo renumerado.

**Alternatives Rejected:** F6 sempre ligado (brainstorm, decisão 13 v1) — mudaria o comportamento com o slot desligado.

**Consequences:** os testes conferem as frases-chave de cada item, não a obediência do agente.

### Decision 9: Provas — fixtures dos dois lados, CI, sabotagem, baseline e 2 execuções reais do Codex

| **Status** | Accepted | · | **Date** | 2026-10-31 |

**Context:** regra 6 (fixture e teste dos dois lados); P2 (provar no Codex CLI); `~/.codex/skills` desta máquina tem cópias antigas de skills SDD.

**Choice:** `tests/test_fluxo.py` (cada verbo × cada exit × cada motivo, num sandbox do `tests/apoio.py` com `git init`; a subseção das 9 skills; F6/F8/F10/F11; o slot) e `tests/test_decisoes_lint.py` (os 2 alvos reais verdes, cada motivo vermelho em fixture montada no teste, as 5 fixtures do `--self-test`, 64). O AT-001 roda sobre fixtures rastreadas (`DESIGN_novos.md`: `Create`, `**Create**`, `criar`, `Modify` fora; `DESIGN_numerado.md`: título `## 3. File Manifest (slice 1)`, `NOVO`, `new`), nunca sobre `sdd/features/` (não rastreado; o teste não pula por arquivo ausente); a verdade dos 8 DESIGNs vira `evidence/F9_FLUXO/review-design-8.log` (`porte=<n> fonte=<n>` por DESIGN). CI: passo novo no `publish-gate.yml` (job `gate`) com `sdd-decisoes-lint.sh --sites .agents/skills sdd/templates/fragments`, `sdd-decisoes-lint.sh --self-test` e `sdd-fluxo.sh --self-test` (o `publish-gate.sh` não muda: os testes, que ele não roda, já estão no `cmd` do gate). Sabotagem: 1 por script novo (`sdd-fluxo.sh` × 3 verbos, `sdd-decisoes-lint.sh` × 2 regras). Baseline: os testes novos na árvore `v2.2.9` ficam vermelhos. Codex: `evidence/F9_FLUXO/codex.sh` copia o repositório por `git archive HEAD` para uma pasta temporária e a commita (`git init -q`, `git add -A`, `git commit -q` com identidade em example.com: sem `.git`, o `codex exec` recusa e o `--print` sai 64), monta um `CODEX_HOME` temporário só com `auth.json` e `config.toml` (sem `skills/`), grava `sdd/config.yaml` com `flow.autonomous: true` e roda `codex exec -s workspace-write -C <cópia>` duas vezes: (a) a `sdd-define` sobre `sdd/fixtures/BRAINSTORM_EXEMPLO.md`, com o prompt mandando responder D1–D5 pela recomendada (exec não interativo); (b) com `--disable multi_agent` e `layers` com 2 globs tocados por uma feature de fixture (DEFINE/DESIGN copiados para a cópia), a `sdd-build` 5d; o log (`codex-define-autonomo.log`, `codex-despacho-40.log`) mostra o `$`, a saída e `[exit=N]`; critério: (a) passa sse há linha começando `✅ DEFINE pronto → seguindo para ` e linha começando `→ /sdd-`; (b) sse há `[exit=40]`, `RESULTADO: AGUARDANDO_HUMANO` e `test -f` do brief na cópia, gravado no log; senão FAIL (❌ no BUILD_REPORT). O `CODEX_HOME` é apagado no fim.

**Rationale:** o CI prova o contrato sem rede nem conta; o Codex prova o comportamento do agente.

**Alternatives Rejected:** pôr os 3 comandos no `publish-gate.sh` — mexeria no G1–G5 que o `test_release_workflow` e a M1 fixam.

**Consequences:** as execuções reais não são determinísticas: o AT é `manual-ux` com o log como recibo; se o agente desviar, o log mostra e o BUILD_REPORT registra.

---

## File Manifest

| # | File | Action | Purpose | Agent | Dependencies |
|---|------|--------|---------|-------|--------------|
| 1 | `sdd/bin/sdd-fluxo.sh` | Create | `review-design`, `loop`, `despachar`, `seguir`, `estado`, `--self-test` (Decisions 1–5) | (general) | None |
| 2 | `sdd/bin/sdd-decisoes-lint.sh` | Create | `--sites`, `--self-test` (Decisions 1, 6) | (general) | 3 |
| 3 | `sdd/templates/fragments/PERGUNTA_DECISAO.md` | Modify | item 9 com a tabela das 6 marcas, `estado`, a exceção do OK da release; marca no exemplo (Decision 6) | (general) | None |
| 4 | `sdd/templates/fragments/FLUXO_ENCADEADO.md` | Create | ordem, `seguir`, transição, recibo, paradas, teto, pergunta D4, `--parar` (Decisions 3–5) | (general) | 3 |
| 5 | `sdd/fixtures/fluxo/DESIGN_novos.md` | Create | 3 Create, sem segurança → EXIGIDO | (general) | None |
| 6 | `sdd/fixtures/fluxo/DESIGN_seguranca.md` | Create | 1 Create + linha `auth` → EXIGIDO | (general) | None |
| 7 | `sdd/fixtures/fluxo/DESIGN_dispensavel.md` | Create | 2 Create → DISPENSAVEL | (general) | None |
| 8 | `sdd/fixtures/fluxo/DESIGN_sem_manifest.md` | Create | sem File Manifest → 64 | (general) | None |
| 9 | `sdd/fixtures/fluxo/review-ok/META.txt` | Create | `reviewer_exit: 0`, `auditor_exit: 0` | (general) | None |
| 10 | `sdd/fixtures/fluxo/review-ok/reviewer.verdicts.jsonl` | Create | 1 HIGH `R1@rev` + 1 MED | (general) | None |
| 11 | `sdd/fixtures/fluxo/review-ok/auditor.verdicts.jsonl` | Create | AGREE em `R1` | (general) | None |
| 12 | `sdd/fixtures/fluxo/review-invalida/META.txt` | Create | `auditor_exit: 68` (forma do DOGFOOD) | (general) | None |
| 13 | `sdd/fixtures/fluxo/review-invalida/reviewer.verdicts.jsonl` | Create | 1 MED | (general) | None |
| 14 | `sdd/fixtures/fluxo/review-invalida/auditor.verdicts.jsonl` | Create | vazio (0 vereditos) | (general) | None |
| 15 | `sdd/fixtures/fluxo/review-impasse/META.txt` | Create | exits 0 | (general) | None |
| 16 | `sdd/fixtures/fluxo/review-impasse/reviewer.verdicts.jsonl` | Create | 1 HIGH | (general) | None |
| 17 | `sdd/fixtures/fluxo/review-impasse/auditor.verdicts.jsonl` | Create | `DISAGREE_EVIDENCE` no HIGH | (general) | None |
| 18 | `sdd/fixtures/fluxo/ledger-rebatida.md` | Create | `R1` HIGH REBATIDA_EVIDENCIA `rodada=1` + linha de outra rodada + MED | (general) | None |
| 19 | `sdd/fixtures/fluxo/ledger-aplicada.md` | Create | `R1` HIGH APLICADA `rodada=1` | (general) | None |
| 20 | `sdd/fixtures/fluxo/AVALIACAO_pass.md` | Create | `VEREDITO: PASS` | (general) | None |
| 21 | `sdd/fixtures/fluxo/AVALIACAO_needs_work.md` | Create | `VEREDITO: NEEDS_WORK` | (general) | None |
| 22 | `sdd/fixtures/fluxo/AVALIACAO_recibo.md` | Create | `VEREDITO: PASS_PENDENTE_RECIBO` | (general) | None |
| 23 | `sdd/fixtures/fluxo/AVALIACAO_ambigua.md` | Create | `VEREDITO: PASS` e `VEREDITO: NEEDS_WORK` → 64 | (general) | None |
| 24 | `sdd/fixtures/fluxo/brief-avaliador.md` | Create | brief de exemplo (modo `veredito`) | (general) | None |
| 25 | `sdd/fixtures/fluxo/config-autonomo.yaml` | Create | `flow.autonomous: true` | (general) | None |
| 26 | `sdd/fixtures/conversa/decisoes/controle.md` | Create | pergunta certa → 0 | (general) | 3 |
| 27 | `sdd/fixtures/conversa/decisoes/sem-classe.md` | Create | sem marca → 2 | (general) | None |
| 28 | `sdd/fixtures/conversa/decisoes/com-outro.md` | Create | opção Outro → 2 | (general) | None |
| 29 | `sdd/fixtures/conversa/decisoes/com-jargao.md` | Create | `AT-003` fora do `(ref: …)` → 2 | (general) | None |
| 30 | `sdd/fixtures/conversa/decisoes/dois-recomendados.md` | Create | 2 `(recomendado)` → 2 | (general) | None |
| 31 | `sdd/config.example.yaml` | Modify | `flow.autonomous: false`, `review.security_globs: ""` com comentário (Decision 5) | (general) | None |
| 32 | `.agents/skills/sdd-brainstorm/SKILL.md` | Modify | 2.2.0: subseção (não encadeia), tabela de tipos de entrada (Decisions 7, 8) | (general) | 4 |
| 33 | `.agents/skills/sdd-define/SKILL.md` | Modify | 2.4.0: subseção (encadeia), pontuação forte/fraco (Decisions 7, 8) | (general) | 4 |
| 34 | `.agents/skills/sdd-governanca/SKILL.md` | Modify | 2.3.0: subseção (encadeia) (Decision 7) | (general) | 4 |
| 35 | `.agents/skills/sdd-governanca/manifest.json` | Modify | 2.3.0 | (general) | None |
| 36 | `.agents/skills/sdd-ux-review/SKILL.md` | Modify | 2.4.0: subseção (encadeia), `UX_REVIEW_*.md` anteriores (Decisions 7, 8) | (general) | 4 |
| 37 | `.agents/skills/sdd-design/SKILL.md` | Modify | 2.2.0: subseção (encadeia), F6 com o encadeamento ligado, `despachar` na revisão do DESIGN, `review-design` citado (Decisions 4, 7, 8) | (general) | 1, 4 |
| 38 | `.agents/skills/sdd-build/SKILL.md` | Modify | 2.4.0: subseção (nunca segue para a release), `despachar` no 5d (Decisions 4, 7) | (general) | 1, 4 |
| 39 | `.agents/skills/sdd-build/references/contexto-fresco.md` | Modify | degrau 2 com `despachar` e o exit 40 (Decision 4) | (general) | 1 |
| 40 | `.agents/skills/sdd-iterate/SKILL.md` | Modify | 2.2.0: subseção (não encadeia) (Decision 7) | (general) | 4 |
| 41 | `.agents/skills/sdd-release/SKILL.md` | Modify | 2.5.0: subseção (não encadeia; publicar é D1) (Decision 7) | (general) | 4 |
| 42 | `.agents/skills/sdd-new-session/SKILL.md` | Modify | 1.3.0: subseção (não encadeia: troca de janela) (Decision 7) | (general) | 4 |
| 43 | `.agents/skills/sdd-auditoria-harness/SKILL.md` | Modify | 1.1.1: identificação (Decision 6) | (general) | None |
| 44 | `.agents/skills/sdd-checar-ambiente/SKILL.md` | Modify | 1.4.1: identificação | (general) | None |
| 45 | `.agents/skills/sdd-handoff/SKILL.md` | Modify | 2.1.1: identificação | (general) | None |
| 46 | `.agents/skills/sdd-kb/SKILL.md` | Modify | 2.2.1: identificação | (general) | None |
| 47 | `.agents/skills/sdd-kb/CHANGELOG.md` | Modify | entrada 2.2.1 | (general) | None |
| 48 | `.agents/skills/sdd-playbook/SKILL.md` | Modify | 2.1.1: identificação | (general) | None |
| 49 | `.agents/skills/sdd-prompt-builder/SKILL.md` | Modify | 2.1.1: identificação | (general) | None |
| 50 | `.agents/skills/sdd-auditoria-harness/references/como-falar.md` | Modify | marca `[auto · de rotina]` | (general) | 3 |
| 51 | `.agents/skills/sdd-brainstorm/references/como-falar.md` | Modify | marca `[D2 · muda o produto]` | (general) | 3 |
| 52 | `.agents/skills/sdd-build/references/como-falar.md` | Modify | marca `[auto · de rotina]` | (general) | 3 |
| 53 | `.agents/skills/sdd-checar-ambiente/references/como-falar.md` | Modify | marca `[auto · de rotina]` | (general) | 3 |
| 54 | `.agents/skills/sdd-define/references/como-falar.md` | Modify | marca `[D2 · muda o produto]` | (general) | 3 |
| 55 | `.agents/skills/sdd-design/references/como-falar.md` | Modify | marca `[D2 · muda o produto]` (onde a pessoa guarda os dados dela muda o produto) | (general) | 3 |
| 56 | `.agents/skills/sdd-governanca/references/como-falar.md` | Modify | marca `[D2 · muda o produto]` | (general) | 3 |
| 57 | `.agents/skills/sdd-handoff/references/como-falar.md` | Modify | marca `[D1 · não se desfaz]` | (general) | 3 |
| 58 | `.agents/skills/sdd-iterate/references/como-falar.md` | Modify | marca `[auto · de rotina]` (atualizar o DESIGN junto é a rotina da iteração) | (general) | 3 |
| 59 | `.agents/skills/sdd-kb/references/como-falar.md` | Modify | marca `[D2 · muda o produto]` | (general) | 3 |
| 60 | `.agents/skills/sdd-new-session/references/como-falar.md` | Modify | marca `[D1 · não se desfaz]` | (general) | 3 |
| 61 | `.agents/skills/sdd-playbook/references/como-falar.md` | Modify | marca `[D3 · muda a regra do método]`; `LM-004` sai da pergunta | (general) | 3 |
| 62 | `.agents/skills/sdd-prompt-builder/references/como-falar.md` | Modify | marca `[D2 · muda o produto]` | (general) | 3 |
| 63 | `.agents/skills/sdd-ux-review/references/como-falar.md` | Modify | marca `[D2 · muda o produto]` | (general) | 3 |
| 64 | `.agents/skills/sdd-ux-review/references/entrevista-publico.md` | Modify | marca `[auto · de rotina]` | (general) | 3 |
| 65 | `.github/workflows/publish-gate.yml` | Modify | passo "Decision classes and chained flow" (Decision 9) | (general) | 1, 2 |
| 66 | `tests/test_fluxo.py` | Create | contratos do `sdd-fluxo.sh`, da subseção, dos itens F6/F8/F10/F11 e do slot (Decision 9) | (general) | 1, 4, 5, 31 |
| 67 | `tests/test_decisoes_lint.py` | Create | contratos do `sdd-decisoes-lint.sh` (Decision 9) | (general) | 2, 26 |
| 68 | `tests/test_conversa.py` | Modify | `test_pergunta_tem_as_regras` também confere a tabela das 6 marcas | (general) | 3 |
| 69 | `tests/test_contrato_build_release.py` | Modify | pinos de versão: release 2.4.0 → 2.5.0, build 2.3.0 → 2.4.0 | (general) | 38, 41 |
| 70 | `tests/test_docs.py` | Modify | roadmap com 5 linhas sem "Chained flow"; `docs/chained-flow.md` linkado dos READMEs | (general) | 73, 74 |
| 71 | `tests/test_release_workflow.py` | Modify | o passo novo do `publish-gate.yml` existe e roda os 3 comandos | (general) | 65 |
| 72 | `docs/cli-conventions.md` | Modify | exits do `sdd-fluxo.sh` e do `sdd-decisoes-lint.sh` | (general) | None |
| 73 | `docs/chained-flow.md` | Create | mecanismo (UX U10), em inglês | (general) | None |
| 74 | `docs/pt-BR/chained-flow.md` | Create | mecanismo, em português | (general) | None |
| 75 | `docs/roadmap.md` | Modify | sem a linha "Chained flow" | (general) | None |
| 76 | `docs/pt-BR/roadmap.md` | Modify | sem a linha "Fluxo encadeado" | (general) | None |
| 77 | `README.md` | Modify | link para `docs/chained-flow.md` | (general) | 73 |
| 78 | `README.pt-BR.md` | Modify | link para `docs/pt-BR/chained-flow.md` | (general) | 74 |
| 79 | `MANIFEST.txt` | Modify | 39 arquivos novos, `LC_ALL=C` | (general) | 1, 2, 4, 5, 26, 66, 67, 73, 74, 80 |
| 80 | `sdd/fixtures/fluxo/DESIGN_numerado.md` | Create | `## 3. File Manifest (slice 1)`, `NOVO`, `new`, `**Create**` → 3 novos | (general) | None |
| 81 | `sdd/fixtures/fluxo/DEFINE_pronto.md` | Create | Status `Ready for Design`, gate `kind: test` / `cmd: "true"` | (general) | None |
| 82 | `sdd/fixtures/fluxo/DEFINE_rascunho.md` | Create | Status `Draft` → PARAR | (general) | None |
| 83 | `sdd/fixtures/fluxo/DEFINE_sem_kind.md` | Create | Status pronto, bloco sem kind/cmd → PARAR | (general) | None |
| 84 | `sdd/fixtures/fluxo/DESIGN_pronto.md` | Create | `Ready for Build`, `design-lint` 0, 3 Create, Ledger com HIGH APLICADA → SEGUIR | (general) | None |
| 85 | `sdd/fixtures/fluxo/DESIGN_ledger_vazio.md` | Create | igual, Ledger sem linha → PARAR | (general) | None |
| 86 | `sdd/templates/DESIGN_TEMPLATE.md` | Modify | seção do Advisor Ledger (Decision 5) | (general) | None |
| 87 | `tests/test_correcoes_w0.py` | Modify | pinos de versão da `sdd-iterate` (2.2.0) e da `sdd-build` (2.4.0) | (general) | 38, 40 |
| 88 | `tests/test_matriz_new_session.py` | Modify | pino de versão da `sdd-new-session` (1.3.0) | (general) | 42 |

**Total Files:** 88

Agent Discovery: Not available (um agente faz o build, modo default).

---

## Landmines aplicáveis

O playbook do pacote tem 4 landmines (`sdd/playbook.md`, `## Sempre`); nenhuma cita encadeamento, classe de decisão ou despacho. Três se aplicam pelo processo:

| LM-nnn | Superfície | Tratamento |
|---|---|---|
| LM-001 | testes do `seguir` e do lint | ✔ tratado: cada teste afirma a linha de saída e o motivo, não só o exit; a fixture `com-jargao` reprova pelo motivo "identificador técnico", não por outro |
| LM-002 | todo teste novo | ✔ tratado: os testes novos rodam na árvore `v2.2.9` e ficam vermelhos (`baseline.log`, AT-032); sabotagem por script |
| LM-003 | revisão de contexto fresco | ✔ tratado: commit antes de cada revisão; worktree destacada; `avaliador-guard.sh` com os 4 prefixos desta família |
| LM-004 | — | N.A.: sem migration |

---

## Contrato de aceite

Ajustes feitos no Define durante o Design (DEFINE v1.2), antes da revisão de contexto fresco:

| # | Alvo | Classe | Decisão |
|---|---|---|---|
| 1 | AT-028 | premissa contradita pelo código (o `publish-gate.sh` não roda lints de skill; o CI roda no `publish-gate.yml`) | o passo vai para o `publish-gate.yml`; os testes no `cmd` do gate cobrem o mesmo |
| 2 | AT-018, AT-020 | aceite falso ("15 em `.agents/skills`" contava os 15 `como-falar.md`, mas a do OK da release não tem "Sua decisão" e a `entrevista-publico.md` tem) | pergunta de decisão = linha com `**Sua decisão**`; 15 = 14 + entrevista; fragmentos: 2, com os blocos ```` ```markdown ```` abertos |
| 3 | AT-022 | contrato intocável | a pergunta do OK da release fica sem marca (D1 por construção), declarada no item 9 |
| 4 | AT-015, AT-013 | verbo faltando | `estado` (0/1/64) para as perguntas `[auto]` no meio da fase |
| 5 | A-004 | premissa errada | `verify-gate.sh --print` fora de git sai 64: o `--self-test` monta `git init` |

A revisão de contexto fresco do DESIGN v1.0 (`sdd/reviews/REVISAO_DESIGN_F9_FLUXO_20261031.md`) propôs 5 ajustes, todos **ACEITOS** e aplicados no DEFINE v1.3: o `seguir` lê o Status e a revisão do DESIGN (AT-013–AT-015); AT-001 sobre fixtures rastreadas; critério de falha das 2 execuções do Codex (AT-030/AT-031); brief já no destino (AT-011); precedência do `loop` da fonte (AT-006/AT-007).

---

## Agent Assignment Rationale

| Agent | Files | Why |
|---|---|---|
| (general) | 1–88 | Modo default: os 2 scripts, os fragmentos e as 15 skills compartilham as marcas, os rótulos e a linha de transição; um autor mantém o vocabulário igual |

---

## Code Patterns

### Pattern 1: Bloco comum da subseção (igual nas 9 skills)

```markdown
### Fluxo encadeado

Ao fechar, a skill roda `bash sdd/bin/sdd-fluxo.sh seguir <fase> <DEFINE> <próxima>` só quando a linha
"Nesta skill" abaixo nomeia o `seguir` (contrato em `sdd/templates/fragments/FLUXO_ENCADEADO.md`).
Exit 0: escreva a linha de transição que o script imprimiu, o recibo **Decidi sozinho** (se houver) e
chame a próxima fase nesta sessão. Exit 1 com `encadeamento desligado`: só o Próximo passo acima, sem
repassar a linha. Exit 1 por outro motivo: diga o motivo em 1 frase e mostre o Próximo passo. Exit 64:
repasse a saída e trate como desligado. A pergunta `[auto · de rotina]` com o encadeamento ligado
vira a opção recomendada e uma linha do recibo; as marcadas D1 a D5 continuam perguntadas. "Pare"
desliga nesta chamada (`--parar`).
```

### Pattern 2: Linha própria por skill

```markdown
Nesta skill: `seguir define <DEFINE> <próxima>`, com a próxima do Próximo passo acima (governanca, ux-review ou design).
Nesta skill: `seguir design <DEFINE> build` depois da revisão do DESIGN; `sdd-fluxo.sh review-design` diz se ela é exigida.
Nesta skill: `seguir build <DEFINE> release` sempre para — publicar não se desfaz e é decisão sua (D1).
Nesta skill: não encadeia — o brainstorm não tem gate; o Define começa quando você pedir.
Nesta skill: não encadeia — a fase seguinte roda na pasta nova, em outra janela (troca de janela, não decisão).
```

### Pattern 3: Parada do exit 40 (bash 3.2, `despachar`)

```bash
printf '⏸️ sdd-open: esta etapa precisa de uma sessão nova do agente.\n\n'
printf '**Por que parei:** a conferência precisa de alguém que não viu esta conversa.\n'
printf '**Onde:** numa janela nova do seu agente, na pasta %s.\n' "$RAIZ"
printf '**Passos:**\n'
printf '1. Abra uma sessão nova do agente nesta pasta → você vê o agente pronto, sem histórico.\n'
printf '2. Cole o conteúdo de %s → o agente começa a ler o DEFINE.\n' "$DESTINO_REL"
printf '3. Quando ele terminar, copie %s e cole aqui.\n' "$RETORNO"
printf '**O que não foi feito:** nada foi publicado e o relatório não foi gravado.\n'
printf '**Brief:** %s\n' "$DESTINO_REL"
printf '**Sessão nova:** abra o agente nesta pasta e cole o conteúdo do brief.\n\n'
printf 'Quando terminar, me peça de novo, eu continuo daqui.\n'
printf 'RESULTADO: AGUARDANDO_HUMANO\n→ quando a pessoa colar o retorno, continue do passo que parou.\n'
exit 40
```

### Pattern 4: Leitura do slot (Python embutido, `estado`)

```python
def slot(caminho, bloco, chave):
    """Valor de bloco.chave num YAML de 1 nível; None se o arquivo ou a chave não existem."""
    try:
        linhas = open(caminho, encoding="utf-8").read().splitlines()
    except OSError:
        return None
    dentro = False
    for ln in linhas:
        if ln and not ln[0].isspace() and not ln.startswith("#"):
            dentro = ln.split("#", 1)[0].strip() == bloco + ":"
            continue
        m = re.match(r"^\s+" + re.escape(chave) + r":\s*(.*)$", ln) if dentro else None
        if m:
            return m.group(1).split(" #", 1)[0].strip().strip('"').strip("'")
    return None
```

### Pattern 5: Marca e rótulo (Python embutido, `--sites`)

```python
MARCA = re.compile(r"\[(?:D\d+|auto)\b[^\]]*\]")
FORMA = re.compile(r"^\[(D[1-5]|auto) · ([^\]]+)\]$")

def confere_marca(linha, pergunta, rotulos):
    marcas = MARCA.findall(linha)
    if not marcas:
        return "sem marca de classe"
    if len(marcas) > 1:
        return "%d marcas" % len(marcas)
    if not linha.split(pergunta, 1)[0].rstrip().endswith(marcas[0]):
        return "marca fora do lugar (vem logo antes da pergunta em negrito)"
    m = FORMA.match(marcas[0])
    if not m:
        return "marca sem o rótulo" if re.match(r"^\[(D[1-5]|auto)\]$", marcas[0]) else "marca desconhecida " + marcas[0]
    if rotulos.get(m.group(1)) != m.group(2):
        return "rótulo %s diferente de %s" % (m.group(2), rotulos.get(m.group(1)))
    return None
```

### Pattern 6: Receita de evidência com `rc` honesto (F7)

```bash
/bin/bash -c 'out=$(bash sdd/bin/sdd-fluxo.sh --self-test 2>&1); rc=$?; printf "%s\n" "$ bash sdd/bin/sdd-fluxo.sh --self-test" "$out" "[exit=$rc]"' > sdd/reports/evidence/F9_FLUXO/self-test-fluxo.log
```

---

## Data Flow

1. A skill chega a uma pergunta `[auto · de rotina]`: na primeira da sessão, roda `sdd-fluxo.sh estado`; 0 → escolhe a recomendada e guarda uma linha do recibo; 1 → pergunta; 64 → repassa a linha ⚠️ e pergunta.
2. A skill fecha a fase (resumo de etapa) e, se a linha "Nesta skill" nomeia o `seguir`, roda-o com o DEFINE e a próxima. O script lê o slot, roda `verify-gate.sh --print` na raiz, procura marcador ativo e, na fase design, roda o `design-lint.py`.
3. Exit 0 → a skill escreve a linha de transição e o recibo e invoca a próxima skill nesta sessão. Exit 1 → mostra o Próximo passo (com o motivo, salvo "desligado"). Exit 64 → ⚠️ e Próximo passo.
4. Na `sdd-design`, antes da revisão do DESIGN, `review-design` diz se ela é exigida (0/1) ou se o manifest está ilegível (64 → roda assim mesmo e registra).
5. Na revisão do DESIGN e no 5d da build, o agente que não abre papel fresco escreve o brief e roda `despachar`: o brief vai para `sdd/reports/briefs/`, a parada sai com 40 e a skill para. A sessão de origem retoma quando a pessoa cola o retorno.
6. A F10 rodará o `loop` depois de cada revisão adversarial, com `--log` em `evidence/<F>/LOOP-rodada-N.log`.
7. Caminho de erro principal: entrada ausente ou malformada → 64 com `RESULTADO:` e `→`; nunca 0 por omissão.

---

## Integration Points

| System | Type | Authentication | Direction | Timeout/Retry | Failure Behavior |
|---|---|---|---|---|---|
| `sdd/bin/verify-gate.sh` | processo local | — | `seguir` → gate (`--print`) | sem retry | ≠ 0 → PARAR com o rc e a 1ª linha do erro |
| `sdd/bin/design-lint.py` | processo local | — | `seguir design` → lint | sem retry | ≠ 0 → PARAR; ausente → PARAR "design-lint ausente" |
| `sdd/bin/skill-lint.py` | import Python | — | `decisoes-lint` → `perguntas()` | — | ausente ou sem `perguntas` → 64 |
| `sdd/bin/gate-shell-evidencia.sh` | processo local | — | `--self-test` → gate do log | — | ausente → cenário do `tee` 🛑 |
| `git` | processo local | — | raiz do repositório | — | sem repositório → pasta atual |
| Codex CLI (`codex exec`) | processo local, só na evidência | `auth.json` copiado para `CODEX_HOME` temporário | evidência → agente | 1 execução por cenário, sem retry | desvio do agente registrado no BUILD_REPORT |

---

## Testing Strategy

| Test Type | Scope | Files | Tools | Coverage Goal |
|---|---|---|---|---|
| Unit (contrato) | `review-design` 0/1/64 sobre as fixtures rastreadas (contagens conhecidas); os 8 DESIGNs reais só na evidência `review-design-8.log` | `tests/test_fluxo.py` | `unittest` + sandbox | AT-001–AT-004 |
| Unit (contrato) | `loop` 0/10/20/30/64 com cada causa; `--log` aceito pelo `gate-shell-evidencia`; `\| tee` acusado | `tests/test_fluxo.py` | idem | AT-005–AT-010 |
| Unit (contrato) | `despachar` 40 (arquivo idêntico, rótulos, retorno por papel) e 64 (nada gravado) | `tests/test_fluxo.py` | idem | AT-011, AT-012 |
| Unit (contrato) | `seguir`/`estado` 0/1/64 com repositório temporário e `git init` | `tests/test_fluxo.py` | idem | AT-013–AT-016 |
| Unit (contrato) | `--self-test` dos 2 scripts numa cópia sem `.git` | `tests/test_fluxo.py`, `tests/test_decisoes_lint.py` | idem | AT-017, AT-021 |
| Unit (contrato) | `--sites` verde nos alvos reais, vermelho por motivo, 64 | `tests/test_decisoes_lint.py` | idem | AT-018–AT-020 |
| Texto | item 9, `FLUXO_ENCADEADO.md`, subseção nas 9, F6/F8/F10/F11, slot, docs | `tests/test_fluxo.py`, `test_conversa.py`, `test_docs.py` | idem | AT-022–AT-027 |
| CI | passo novo do `publish-gate.yml`; `check-versions` | `tests/test_release_workflow.py`, `scripts/check-versions.py` | idem | AT-028 |
| Regressão | suíte inteira no piso, `skill-lint --conversa`, `playbook-lint --self-test`, `publish-gate.sh ci` | `cmd` do Verify Gate | `/usr/bin/python3`, `/bin/bash` | AT-029 |
| Agente real | `codex exec` 2× | `evidence/F9_FLUXO/codex.sh` | Codex CLI 0.163 | AT-030, AT-031 |
| Sabotagem e baseline | 1 por script; árvore `v2.2.9` | `evidence/F9_FLUXO/sabotagem.sh` | bash | AT-032 |

---

## Error Handling

| Error Type | Handling Strategy | Retry? |
|---|---|---|
| Argumento ausente, opção sem valor, verbo desconhecido | uso + `RESULTADO: ERRO DE USO` + exit 64 | No |
| `python3` ausente | `🛑 python3 não encontrado` + 64 (AT-016) | No |
| Entrada ausente ou malformada no `loop` | `🛑 <entrada>: <motivo>` + 64; nunca PRONTO por omissão | No |
| Manifest ilegível | 64 com o `→` do default seguro | No |
| Slot inválido | ⚠️ de U6 + 64; a skill trata como desligado | No |
| Gate ou lint vermelho no `seguir` | PARAR com o motivo (não é erro do script) | No |
| Brief ausente ou nome inválido | 64, nada gravado | No |
| Tabela de rótulos vazia ou fragmento ausente | 64 no `decisoes-lint` | No |
| Zero perguntas no alvo do `--sites` | 64 (nada conferido nunca é verde) | No |

---

## Configuration

| Config Key | Type | Default | Description |
|---|---|---|---|
| `flow.autonomous` | bool | `false` | liga o encadeamento; não liga nem desliga a camada de conversa |
| `review.security_globs` | string (globs por vírgula) | `""` | superfície de segurança do projeto, além dos 8 termos fixos e de `layers.sql` |
| `PERGUNTA_FRAG` | env | fragmento ao lado do pacote | caminho do `PERGUNTA_DECISAO.md` lido pelo lint (testes) |

---

## Security Considerations

- O `despachar` só copia o arquivo que a skill escreveu e valida `papel`/`FEATURE` por lista de caracteres: nenhum caminho do argumento entra no nome de destino além desses campos (sem `../`).
- O brief vai para `sdd/reports/briefs/`; o pacote não decide se essa pasta entra no git do usuário (o `avaliador-guard.sh` já permite `sdd/reports/`).
- A evidência do Codex copia `auth.json` só para um `CODEX_HOME` no scratchpad, apagado ao fim por `rm -rf` com o guarda `:?` na variável (regra do pacote); o log nunca imprime o arquivo.
- `review-design` com falso positivo só custa uma revisão; o default de manifest ilegível é rodar.

---

## Observability

- Toda saída que não é sucesso termina em `RESULTADO: <PALAVRA>` + `→` (UX U9; `docs/cli-conventions.md`).
- O `loop --log` grava o exit real; o `gate-shell-evidencia.sh` confere a pasta da evidência.
- O `seguir` roda `verify-gate.sh --print`, que não grava trace; as voltas vermelhas continuam em `sdd/traces/<F>.jsonl` pelas execuções do gate.

---

## Requirements Traceability

| AT | Componente / arquivo | Teste |
|---|---|---|
| AT-001–AT-004 | `sdd-fluxo.sh review-design` (1), fixtures 5–8 e 80 | `test_fluxo.ReviewDesign` |
| AT-005–AT-010 | `sdd-fluxo.sh loop` (1), fixtures 9–23 | `test_fluxo.Loop` |
| AT-011, AT-012 | `sdd-fluxo.sh despachar` (1), fixture 24 | `test_fluxo.Despachar` |
| AT-013–AT-015, AT-033 | `sdd-fluxo.sh seguir`/`estado` (1), fixtures 25, 81–85, template 86 | `test_fluxo.Seguir`, `test_fluxo.Estado` |
| AT-016 | os 2 scripts | `test_fluxo.SemPython`, `test_decisoes_lint.SemPython` |
| AT-017 | `sdd-fluxo.sh --self-test` | `test_fluxo.SelfTest` |
| AT-018–AT-021 | `sdd-decisoes-lint.sh` (2), fixtures 26–30, marcas 50–64 | `test_decisoes_lint` |
| AT-022 | `PERGUNTA_DECISAO.md` (3) | `test_conversa.Fragmento`, `test_fluxo.Marcas` |
| AT-023 | `FLUXO_ENCADEADO.md` (4) | `test_fluxo.Fragmento`, `test_agnostico` |
| AT-024 | 9 `SKILL.md` (32–34, 36–38, 40–42) | `test_fluxo.Subsecao`, `test_docs`, `test_contrato_build_release` |
| AT-025 | `config.example.yaml` (31) | `test_fluxo.Slots` |
| AT-026 | 37, 38, 39 | `test_fluxo.Despacho` |
| AT-027 | 32, 33, 36, 37 | `test_fluxo.ItensDoPorte` |
| AT-028 | 65; versões 32–49 | `test_release_workflow`, `check-versions.log` |
| AT-029 | tudo | `cmd` do gate |
| AT-030, AT-031 | evidência | `codex-define-autonomo.log`, `codex-despacho-40.log` |
| AT-032 | 1, 2 | `sabotagem.log`, `baseline.log` |

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Pergunta escrita sem `**Sua decisão**` escapa do `--sites` | uma pergunta sem marca chega ao aluno | o `skill-lint --conversa` continua no `como-falar.md`; o formato da F4 manda "Sua decisão" como parte 4 da resposta |
| O agente não obedece à subseção | encadeamento não roda ou roda sem o script | o contrato é o exit do `seguir`; as 2 execuções do Codex mostram o comportamento real; o resto é texto testado |
| `codex exec` muda de flag ou de comportamento | AT-030/031 sem prova | o `codex.sh` grava a versão do Codex no log; o desvio vai ao BUILD_REPORT |
| Rótulo da marca deriva entre skill e fragmento | marca inconsistente | o lint lê os rótulos do fragmento (dono único) e reprova o diferente |
| O `loop` porta um formato que a F10 mude | retrabalho na F10 | fixado o núcleo; a F10 acrescenta por delta com as fixtures dela |

---

## Advisor Ledger

Revisão de contexto fresco do DESIGN v1.0 (`sdd/reviews/REVISAO_DESIGN_F9_FLUXO_20261031.md`, modo `contrato`, 14 logs `AVAL-DESIGN-*.log`): NEEDS_WORK, 3 HIGH, 2 MEDIUM, 10 LOW.

| # | Nota | Severidade | Veredito | Evidência |
|---|---|---|---|---|
| A1 | `seguir` encadeava com DEFINE/UX/DESIGN não prontos, com bloco do gate sem kind/cmd e sem a revisão do DESIGN registrada; `build → release` sairia 64 | HIGH | APLICADA (Decision 5; DEFINE AT-013–AT-015; fixtures 81–85; template 86) | `AVAL-DESIGN-print-fraco.log`, `AVAL-DESIGN-ledger-vazio.log` |
| A2 | AT-001 sobre `sdd/features/`, que o `git archive` não leva | HIGH | APLICADA (Decision 9; fixtures 5, 80; `review-design-8.log`) | `AVAL-DESIGN-designs-fora-do-archive.log` |
| A3 | `codex.sh` sem `.git` na cópia, string esperada errada, sem critério de falha, perguntas D2 travando o exec, 5d N.A. sem `layers` | HIGH | APLICADA (Decision 9; DEFINE AT-030/AT-031) | `AVAL-DESIGN-codex-git.log` |
| A4 | `despachar` com o brief já no destino: `cp X X` sai 1 | MEDIUM | APLICADA (Decision 4; DEFINE AT-011) | `AVAL-DESIGN-despachar-mesmo-arquivo.log` |
| A5 | Precedência do `loop` nos ATs ≠ fonte em 3 casos de borda | MEDIUM | APLICADA (Decision 3; DEFINE AT-006/AT-007; teste diferencial) | `AVAL-DESIGN-fonte-loop-bordas.log` |
| L1 | Pinos de versão em 5 testes fora do manifest | LOW | APLICADA (linhas 69, 87, 88) | `AVAL-DESIGN-pinos-versao.log` |
| L2 | Motivos do lint com redação ≠ `skill-lint`; faltavam zero recomendadas e marca fora do lugar | LOW | APLICADA (Decision 6; AT-019) | `sdd/bin/skill-lint.py:192-203` |
| L3 | Concordância "GOVERNANÇA pronto" | LOW | APLICADA (Decision 5; AT-013) | — |
| L4 | "30 arquivos novos" no `MANIFEST.txt`; são 33 (39 com as fixtures da A1/A2) | LOW | APLICADA (linha 79) | `AVAL-DESIGN-fonte-review-design.log` |
| L5 | `check-versions --base` e AT-032 fora do `cmd` | LOW | APLICADA (DEFINE, Clarifications) | — |
| L6 | Pattern 1: 64 nem sempre tem ⚠️ | LOW | APLICADA ("repasse a saída") | — |
| L7 | Raiz achada de 2 jeitos | LOW | APLICADA (Decision 5: `git -C <pasta do artefato>`) | — |
| L8 | Pergunta aberta do fragmento sem regra de marca | LOW | APLICADA (Decision 6; AT-022) | `PERGUNTA_DECISAO.md:47` |
| L9 | Zero perguntas por caminho ou no total | LOW | APLICADA (total; AT-020) | — |
| L10 | Projeto atualizado não recebe as fixtures novas nem o item 9 novo; `--self-test` sai 64 lá | LOW | APLICADA (registrado em `docs/chained-flow.md` como limite: o `init` completa só o que falta; a 64 do `--self-test` nomeia a pasta ausente) | `bin/sdd-open.sh` (cópia de `sdd/fixtures/` só na 1ª instalação) |

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.1 | 2026-10-31 | SDD Design by RDD | Revisão de contexto fresco: 3 HIGH, 2 MEDIUM e 10 LOW aplicados (Decisions 3–6 e 9; manifest 79 → 88; Advisor Ledger) |
| 1.0 | 2026-10-31 | SDD Design by RDD | Versão inicial a partir do BRAINSTORM, do DEFINE v1.2 e da UX review |

---

## Next Step

Execute o **SDD Build by RDD**.
