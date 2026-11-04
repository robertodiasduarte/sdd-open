# DESIGN: F13 UX e LLM no código

> Technical design for implementing F13 UX e LLM no código

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | F13_UX_LLM |
| **Date** | 2026-11-04 |
| **Author** | SDD Design by RDD |
| **BRAINSTORM** | `sdd/features/BRAINSTORM_F13_UX_LLM.md` |
| **DEFINE** | `sdd/features/DEFINE_F13_UX_LLM.md` (v1.7) |
| **UX REVIEW** | `sdd/reviews/UX_REVIEW_F13_UX_LLM.md` (U1–U12) |
| **LLM Prompts** | false |
| **Status** | Ready for Build |

---

## Architecture Overview

```text
 UX review                     Design                         Build (sdd-build 2.6.0, passo 4)
 ─────────                     ──────                         ────────────────────────────────
 sdd-ux-review 2.5.0           sdd-design 2.5.0               arquivo está no inventário?
   │  tabela WCAG                │  5.5 copia o fragmento       ├─ sim → roteador por Tipo
   │  (UX_REVIEW_TEMPLATE)       ▼                              │         ├─ one-shot → prompts.builder_skill
   ▼                           fragments/LLM_PROMPTS_DESIGN     │         └─ loop → sdd-loop-builder 1.0.0
 sdd/bin/contraste.sh            │  inventário + contrato       │                    │ LOOP_SPEC + estágios
   │ 0 PASSA · 2 REPROVA         ▼                              │                    ▼
   │ 64 uso                    sdd/bin/design-lint.py           │              builder, 1 por estágio LLM
   ▼                             │ reprova coluna/campo         │         │ texto gerado
 1 MUST por REPROVA              ▼                              │         ▼
                               DESIGN com Tipo por linha        │   prompt-drift-scan.sh --conteudo
                                                                │   (2 aqui é o esperado) → gravar
                                                                └─ não → conteúdo a gravar → prompt-drift-scan.sh --conteudo
                                                                          lê prompts.wrapper_pattern (sdd/config.yaml)
                                                                          0 grava · 2 para e pergunta · 64 corrige a chamada
```

Nada muda em `sdd/hooks/`, `report-lint.py`, `verify-gate.sh` nem `sdd-release`.

---

## Components

| Component | Purpose | Technology / Pattern | Inputs | Outputs | Dependencies |
|---|---|---|---|---|---|
| `contraste.sh` | razão WCAG truncada, com veredito contra um piso (U2) | bash 3.2 + `awk` com `LC_ALL=C` | 2 cores, alpha, `--piso` | 1ª linha + `RESULTADO:` + `→`; exit 0/2/64 | nenhuma |
| `prompt-drift-scan.sh` | detecta prompt de produção antes de gravar (L4) | bash 3.2 + `grep -E` + `awk` | caminhos ou stdin + 1 caminho; `prompts.wrapper_pattern` | achados + `RESULTADO:` + `→`; exit 0/2/64 | `sdd/config.yaml` (opcional) |
| `design-lint.py` | confere o inventário de prompts (L3) | Python stdlib | DESIGN | `🛑` por falta; exit 0/1/64 | nenhuma |
| `LLM_PROMPTS_DESIGN.md` | dono único do inventário e do contrato (L3) | fragmento Markdown | DEFINE com prompts | seção do DESIGN | `sdd-design` |
| `sdd-loop-builder` | especifica o processo em laço (L1) | skill com 3 referências | contrato compilado | bloco de texto com LOOP_SPEC v2, estágios, prompts pendentes, gate | `sdd-prompt-builder` depois |
| Roteador no passo 4 | liga scan, skill e gravação (L2) | texto da `sdd-build` | inventário do DESIGN | prompt gravado no mesmo turno | os 2 anteriores |
| Tabela WCAG | veredito por critério (U1) | texto do template e da skill | pares medidos | 1 MUST por REPROVA | `contraste.sh` |
| Docs | explicam os mecanismos | Markdown EN + PT | — | `docs/llm-in-code.md`, roadmap, README | testes de `test_docs.py` |

---

## Key Decisions

### Decision 1: `contraste.sh` com a conta no awk e o resto no bash

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-11-04 |
| **Source** | DEFINE AT-001 a AT-007, UX U1, U3, U7; fonte no privado |

**Context:** a fonte tem 55 linhas, sem referência à RDD, e sempre sai 0. O DEFINE pede veredito, piso, saída 2 e mensagens com conserto.

**Choice:** `export LC_ALL=C` na 2ª linha útil. O bash separa as opções num laço `while`, sem array, e valida as entradas por expressão (`[[ =~ ]]`, disponível no 3.2): cor `#rgb` ou `#rrggbb`; alpha `0`, `1`, `.5`, `0.5`, `1.0`; piso maior que zero, com até 2 casas. 2 ou 3 valores posicionais; outra quantidade sai 64. `--piso` sem valor sai 64, testado antes de ler `$2`, por causa do `set -u`. Sem argumento, a mensagem mostra o exemplo com aspas e diz que `#` sem aspas começa um comentário no shell. O `awk` faz toda a conta, inclusive os centésimos do piso, porque a aritmética do bash leria `08` como base 8: `int(razão * 100 + 1e-9)` contra `int(piso * 100 + 0.5)`; o `1e-9` só protege a imprecisão de ponto flutuante em casos exatos como 21,00 e não alcança 4,4999996 (449,99996). `--piso` é aceito em qualquer posição. `--help` sai 0, com o exemplo e a frase do truncamento. `--self-test` guarda o caminho absoluto do script e o chama com `"$BASH"`, para valer o bash do teste. Toda referência nos textos é `bash sdd/bin/contraste.sh`; o arquivo nasce 100644, como 20 dos 25 de `sdd/bin/`.

**Rationale:** comparar inteiros evita `4.55 * 100 = 454.999…`; validar antes do `awk` dá a mensagem certa para `rgba(...)`.

**Alternatives Rejected:**
1. Python — o privado usa `awk`, e a conta cabe nele sem dependência nova.
2. Arredondar — decisão do Roberto.

**Consequences:**
- Quem usava a saída 0 do privado precisa tratar a saída 2 (F15, registrado no plano).
- `--piso` só com 2 casas: suficiente para 4,5 e 3.

### Decision 2: Sinais do scan generalizados, com o wrapper como expressão do parâmetro

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-11-04 |
| **Source** | DEFINE AT-008 a AT-014, Clarifications; fonte no privado |

**Context:** a fonte tem 4 referências à RDD: `*.test.ts`, `_shared/templates-*`, `_shared/*prompt*` e `systemPrompt:` fixo.

**Choice:** ordem fixa de avaliação, por arquivo: pasta de teste → sinal de pasta `prompts` (em qualquer caixa) → nome de teste → `.md` encerra sem achado → sinal de nome com `prompt` → conteúdo. Conteúdo: SDK (`messages\.create|chat\.completions|responses\.create|generateContent|generate_content`), `system` com literal por `:` ou `=`, inclusive com a chave entre aspas, e `role` de sistema, inclusive `role: system` sem aspas, depois de `:`. A chave só vale no início da linha, também como item de lista YAML (`- `), depois de `{`, `,`, `(`, `[`, `.`, ou de `const`, `let` e `var`, para `file system:`, `package-ecosystem:`, `filesystem:` e `operating_system:` não casarem. E `(<slot>)` seguido de espaços e literal. Os parênteses em volta do slot fazem `a|b` valer inteiro. **Normalização:** o caminho, relativo ou absoluto, vira físico pelo ancestral existente mais profundo (`cd … && pwd -P`, sem `realpath`, porque com `--conteudo` a pasta pode não existir); a raiz também é física. Dentro da raiz, os sinais olham o caminho relativo a ela. Fora da raiz, o sinal de `prompts` olha todos os componentes (alarme a mais é melhor que cegueira) e a exclusão de teste olha só o nome do arquivo. `..` no trecho que não existe sai 64.

**Rationale:** o privado mediu que sem as 2 exclusões o scan vira alarme falso. Generalizar a exclusão de teste e tirar o `.md` do conteúdo mantém isso em qualquer linguagem.

**Alternatives Rejected:**
1. Slot como expressão completa, literal incluído — cada projeto teria de escrever a parte do literal, e `callLLM\(` sozinho dispararia em toda chamada.
2. Sinais `_shared/*` genéricos — é convenção de um projeto; quem a tiver usa o slot.

**Consequences:**
- Literal na linha seguinte ao parâmetro não dispara (A-003, documentado).
- O nome e o conteúdo do próprio scan caem nos sinais. Sem exceção no script: o Build registra o falso positivo, e nesta frente isso fica em `## Desvios` do BUILD_REPORT.
- `system: "linux"` num YAML dispara; o Build registra como falso positivo.

### Decision 3: Leitura do slot sem dependência

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-11-04 |
| **Source** | DEFINE AT-010, AT-012, AT-013 |

**Context:** `sdd/bin/` já lê slots por `awk` (`contexto-lint.sh`) e por Python. O slot é uma expressão com contrabarras, e o exemplo do plano vem entre aspas duplas de YAML (`"callLLM\\("`).

**Choice:** função `slot_wrapper` em `awk` dentro do bloco `prompts:` do `sdd/config.yaml`, na raiz do projeto. A raiz vem de `git rev-parse --show-toplevel` num subshell sem `GIT_DIR` nem `GIT_WORK_TREE`, com `pwd -P` como reserva. O `\r` final sai antes de tudo. Valor entre aspas é lido por varredura até a aspa de fechamento: entre aspas duplas, `\\` vira `\` e `\"` vira `"`, e outra contrabarra fica como está; entre aspas simples, literal, com `''` para a aspa. Depois da aspa de fechamento, só espaço e comentário; qualquer outra coisa sai 64. Sem aspas: corta em ` #`. A expressão é validada pura e composta com o literal, a que será usada de fato: `grep -E -e "$expr" </dev/null`, exit 2 em qualquer uma ⇒ saída 64.

**Rationale:** um hook herda `GIT_DIR` (defeito da F11): sem limpar, o script leria o config de outro repositório.

**Alternatives Rejected:**
1. Parser YAML — fora do piso stdlib.
2. Python só para isto — mais lento numa chamada por arquivo.

**Consequences:**
- A premissa A-002 fica provada no CI, em macOS e Ubuntu, com `(` e `[` como casos; outras expressões divergem entre BSD e GNU.

### Decision 4: Saídas 64 fail-closed e self-test autocontido

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-11-04 |
| **Source** | Brainstorm, decisões 7 e 8; DEFINE AT-013 e AT-015 |

**Context:** a fonte conclui `LIMPO` com caminho inexistente, grava `.falhas.$$` na pasta de fixtures e depende de fixtures instaladas.

**Choice:** caminho inexistente, pasta, arquivo ilegível (`-r`), entrada de terminal e entrada vazia saem 64, e também qualquer `grep` de conteúdo que saia 2: nenhum `if grep` trata 2 como "não achei". Sem `sdd/fixtures/`: `--self-test` guarda o caminho absoluto do script antes do `cd`, monta em `mktemp -d`, com `trap` de limpeza, um projeto com `sdd/config.yaml` e os arquivos de caso, e roda o próprio script dentro dele. `sdd/config.yaml` ilegível é conferido fora da substituição de comando: um `erro_uso` dentro dela só sairia da subshell, e o slot viraria vazio. Cada caso é uma linha: exit esperado, texto esperado, argumentos. Falha conta numa variável, sem subshell de pipe.

**Rationale:** o `init` só copia `sdd/fixtures/` na 1ª instalação; quem atualiza veria um vermelho falso.

**Alternatives Rejected:**
1. Fixture em `sdd/fixtures/prompt-drift/` — o defeito acima; `tests/` cobre os 2 lados por fora.

**Consequences:**
- Regra 6 do 8.0 atendida por `--self-test` + `tests/`, sem pasta nova.

### Decision 5: Inventário conferido só quando a seção existe

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-11-04 |
| **Source** | Abordagem A; DEFINE AT-016 e AT-017; UX U4 |

**Context:** coluna faltando é erro exato, o lugar em que a abordagem A aceita trava.

**Choice:** `lint_prompts` em `design-lint.py`, chamado por `lint`, só com a seção de título de 2º nível `LLM Prompts` presente: acha o subtítulo que começa por `### Inventário`, e a ausência dele reprova, com a frase da v2.5.0 (é o formato antigo real, `### Inventory`, da F10); a 1ª tabela dali precisa das colunas `Tipo`, `Versão`, `Completeness` e `Refator de?` e de ≥ 1 linha de dados; `Tipo` sem crases é `one-shot` ou `loop`; cada `#### Prompt N:` tem `Autônomo?`, `Verification interna` e `Eval mínimo pré-ship` com valor, e, em `loop`, `Intenção`, `Perfil de risco dos efeitos` e `Ground truth disponível`, porque a skill para sem elas; traço conta como vazio; o nº de blocos é igual ao de linhas. Na 1ª falha, a frase da v2.5.0 vem antes dos itens, e o `main` troca o `→`.

**Rationale:** o Build compila o contrato a partir dessas colunas; falta aqui vira improviso lá.

**Alternatives Rejected:**
1. Avisar sem reprovar — o aviso se perde; e o Roberto aceitou o efeito colateral no checkpoint 2.

**Consequences:**
- DESIGN em andamento com inventário antigo reprova até ganhar as colunas.

### Decision 6: Fragmento como dono único, template só aponta

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-11-04 |
| **Source** | DEFINE AT-018; regra de dono único dos fragmentos |

**Context:** a seção só existe com `LLM Prompts: true`; a tabela não pode morar em 2 lugares.

**Choice:** `sdd/templates/fragments/LLM_PROMPTS_DESIGN.md` traz um comentário de uso e a seção de prompts: roteador; `### Inventário` com 11 colunas: `#`, `Nome`, `Tipo`, `Arquivo de destino`, `Versão`, `Provedor/Modelo`, `Origem da entrada`, `Consumidor da saída`, `Material de referência`, `Completeness`, `Refator de?`; `### Contrato por prompt` com `Tom/audiência`, `Tipo de saída`, `Fallback aprovado`, `Autônomo?`, `Verification interna`, `Eval mínimo pré-ship` e, em `loop`, `Intenção`, `Perfil de risco dos efeitos` e `Ground truth disponível`; `### Versionamento`; `### Gate do Build por Tipo`. `DESIGN_TEMPLATE.md` ganha um comentário HTML entre as seções de padrões de código e de fluxo de dados, com o caminho e os nomes das colunas. Uma linha `Tipo=loop` tem como destino `<pasta do processo>/LOOP_SPEC.md`. Cada estágio LLM grava em `<pasta do processo>/<estágio>.<ext>`, nome dado pela coluna `arquivo` da tabela de estágios. Esses arquivos contam como inventariados e como previstos no File Manifest, derivados da linha. O contrato de um estágio é o bloco da linha mais a linha dele na tabela de estágios, e `sdd-integration.md` diz isso. No BUILD_REPORT, 1 entrada para a LOOP_SPEC e 1 por estágio, marcadas como derivadas da linha.

**Rationale:** um comentário não vira seção por engano em DESIGN sem prompts.

**Alternatives Rejected:**
1. Seção real no template — apagar por engano, ou esquecer de apagar, geraria reprovação sem motivo.

**Consequences:**
- A lista de `sdd-integration.md` passa a usar os nomes das colunas; um teste confere que comentário, fragmento, lint e integração não divergiram.

### Decision 7: Roteador no passo 4, com o scan no lugar da regra escrita

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-11-04 |
| **Source** | DEFINE AT-019 e AT-020; UX U6; Brainstorm, decisão 11 |

**Context:** o item 1 do passo 4 da `sdd-build` lista os sinais em prosa, e o item 2 só conhece a skill de prompt.

**Choice:** a ordem da fonte não serve: um prompt novo não tem conteúdo antes da skill. (1) Arquivo no inventário vai direto ao roteador, sem varredura prévia. `one-shot`: como hoje. `loop`: `sdd-loop-builder` e depois um prompt por estágio LLM, tudo no mesmo turno, com a linha 🔁. Sem `Tipo`, a pergunta de triagem e, na dúvida, `loop`, com registro. (2) O texto gerado passa por `--conteudo` antes de gravar: exit 2 num arquivo inventariado é o esperado e grava; exit 0 também grava. (3) Arquivo fora do inventário: varredura do conteúdo a gravar; exit 2 para e pergunta; exit 0 grava. (4) Exit 64 é chamada errada, nunca ignorada. Arquivo vazio não precisa de varredura. O aviso do slot é repassado uma vez por Build. Skill ausente: 🛑 + pergunta `[D2 · muda o produto]`, à letra. A skill devolve item faltando: nada é gravado, e o DESIGN é iterado. Devolve "não é laço": a linha vira `one-shot`, com registro. Orçamento por estágio é desenho da skill, não item do contrato; valor proposto vai para o relatório. O nome `sdd-loop-builder` fica fixo.

**Rationale:** script tem dentes, e o texto calibrado por agente ficou cego no privado por 4 meses.

**Alternatives Rejected:**
1. Passo 5.5 novo — o plano cita 5.5 por engano, e o passo existente é o 4 (Brainstorm).
2. Slot do nome da skill — decisão do Roberto.

**Consequences:**
- A contagem de `sdd-decisoes-lint.sh --sites` muda; `test_decisoes_lint.py` registra o valor medido no Build.
- A obediência ao roteador só é provada pelo agente real (AT-021, 3 execuções).
- `WORKER_BRIEF.md`, a descrição da `sdd-prompt-builder` e `sdd-integration.md` acompanham: exclusão dura vale para as 2 skills, o orquestrador varre os arquivos da wave em disco, e o builder é da fase Build, nunca do Design.

### Decision 8: `sdd-loop-builder` em português, com o molde da `sdd-prompt-builder`

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-11-04 |
| **Source** | DEFINE AT-022 a AT-025; UX U5, U10; fonte no privado |

**Context:** a fonte tem 323 linhas, com as regras em inglês e histórico da RDD. O pacote é em português, e o limite é 500 linhas por `SKILL.md`.

**Choice:** `SKILL.md` com a camada de conversa, o contrato de entrada e saída, o procedimento e as exceções. `references/loop-spec-rules.md`: princípios, regras, orientação por seção, lógica de decisão, molde e barra de qualidade, em português, com as marcas `<LOOP_SPEC v="2">` e os nomes das seções iguais aos da fonte. `references/exemplo-loop-spec.md`: exemplo `standard`, escrito do zero (redator de notas de versão com verificador por código). `references/como-falar.md`: glossário da UX U5. Tira: `FRAMEWORK_LOOP_ENGINEERING.md`, nomes de agente, `fp-eval` e `LM-nnn`; ficam as 3 lições de campo, sem citar a origem. Correções da fonte: o molde marca `action_space` sem perfil, e a lógica de decisão o tira do `lite`; aqui ele é `standard+`, e o `lite` põe o escopo negativo em `<intent>`. A fonte separa `lite` de `standard` por "curto" e "vários arquivos", o que dava perfis diferentes para o mesmo processo; aqui: efeito externo ou irreversível é `high-risk`, e entre os reversíveis `lite` é 1 estágio LLM com verificador por código de saída.

**Rationale:** quem lê é o agente de um projeto qualquer; regras em português seguem as outras skills, e as marcas ficam como contrato.

**Alternatives Rejected:**
1. Manter as regras em inglês — destoaria da `prompt-building-rules.md`.
2. Fluxo encadeado na skill — é das 9 skills de fase; esta é de apoio, como a `sdd-prompt-builder`.

**Consequences:**
- Skill nova muda 3 contagens e a linha de identificação (Decision 11).

### Decision 9: Tabela WCAG com o texto da norma

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-11-04 |
| **Source** | DEFINE AT-027, AT-028, Clarifications; UX U8 |

**Context:** o privado exige mais que a norma em 2 linhas e tem colunas de RDD.

**Choice:** seção `## Accessibility and Responsiveness` do template: nota de uso; tabela `SC · Nível · Verificação · Evidência · Veredito` com as 5 linhas de veredito e as 2 herdadas; a nota de 3.3.7 e 2.4.13; tabela `Responsiveness` com o que sai da antiga (`Mobile`). Acceptance notes ganham 2 linhas. Na `sdd-ux-review`: passo `4.5`, que fica dentro da etapa Qualidade; o passo 4 passa a nomear o `contraste.sh`; a lente L1 aponta para o 4.5; 1 linha no Quality Gate.

**Rationale:** um REPROVA não pode afirmar violação que a norma não define.

**Alternatives Rejected:**
1. Portar "inclusive desabilitado" e "anel ≥3:1" em 2.4.7 — ver Clarifications do DEFINE.

**Consequences:**
- O rigor maior do privado, se ele quiser, vai para o playbook dele na F15.

### Decision 10: Docs e listas de skills

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-11-04 |
| **Source** | DEFINE AT-029 a AT-031; UX U7, U9 |

**Context:** o roteiro do pacote exige documento próprio quando um tema sai do roadmap, e a skill nova muda listas e contagens.

**Choice:** `docs/llm-in-code.md` + PT; link nos READMEs; "The 18 skills" e `sdd-loop-builder` em Cross-cutting; `AGENTS.md.tmpl`; `sdd/config.example.yaml` + guias de adaptação; `docs/cli-conventions.md` (2 linhas de exit e as palavras); ficha no guia do aluno; roadmap com a linha só da `sdd-drive`, sem mudar a contagem de 3.

**Rationale:** `test_docs.py` exige a ficha, os links e a contagem.

**Alternatives Rejected:**
1. Tirar a linha do roadmap — a `sdd-drive` ainda é planejada.

**Consequences:**
- `tests/test_docs.py` muda em 4 pontos: a tupla do roadmap, a contagem do guia, o docstring e o caso do doc novo.

### Decision 11: Versões, contagens e Release

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-11-04 |
| **Source** | DEFINE AT-033; Brainstorm, decisão 3 |

**Context:** toda skill tocada sobe de versão, e os pinos dos testes acompanham.

**Choice:** `sdd-build` 2.5.1 → 2.6.0; `sdd-design` 2.4.0 → 2.5.0; `sdd-ux-review` 2.4.0 → 2.5.0; `sdd-prompt-builder` 2.1.1 → 2.1.2; `sdd-loop-builder` nasce 1.0.0. Linha de identificação com `nov/2026`, `updated: "2026-11"`. Skills 17 → 18; bloco comum em 16; `MANIFEST.txt` com `LC_ALL=C sort`. Release: `v2.5.0` por tag, push atômico.

**Rationale:** `check-versions.py` compara com a `v2.4.0` e reprova skill tocada sem subir.

**Alternatives Rejected:**
1. Patch na `sdd-build` — o roteador é comportamento novo.

**Consequences:**
- `sdd-release`, hooks, `report-lint.py` e `verify-gate.sh` ficam byte-idênticos (AT-034).

### Decision 12: Provas

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-11-04 |
| **Source** | DEFINE AT-021; regra 6 do 8.0; prompt da sessão |

**Context:** a prova real da F12 deu PASS falso quando o critério lia texto em vez de efeito.

**Choice:** `evidence/F13_UX_LLM/codex-roteador.sh` (fora do commit) monta cópias commitadas do HEAD com DEFINE e DESIGN de exemplo, `sdd/config.yaml` e `CODEX_HOME` só com `auth.json`, e roda 3 execuções: caminho feliz, sem a skill, e linha sem `Tipo`. O critério é por efeito: um calço na cópia registra cada chamada real do scan, com a saída e se o arquivo já existia, e `confere_roteador.py` lê esse registro; não interpreta o texto do agente, que muda de forma a cada execução. Os controles sem agente têm 3 execuções válidas, que passam, e 18 ruins, que reprovam. Baseline: os testes novos rodam contra a `v2.4.0` e falham. Sabotagens: `contraste.sh` arredondando e sem `LC_ALL=C`; `prompt-drift-scan.sh` sem o sinal do wrapper e com `grep` que sai 2; `design-lint.py` sem a checagem do `Tipo`. AT-033 e AT-034 têm log próprio no repositório, porque a cópia do gate não tem `.git`.

**Rationale:** arquivo no destino não aparece só porque o agente leu o script.

**Alternatives Rejected:**
1. Critério pelo texto do transcript — o PASS falso da F12.

**Consequences:**
- A prova roda depois do último conserto; se a revisão real mudar o texto do passo 4, roda de novo.

---

## File Manifest

| # | File | Action | Purpose | Agent / Owner | Dependencies |
|---:|---|---|---|---|---|
| 1 | `sdd/bin/contraste.sh` | Create | razão, veredito, `--piso`, `--self-test` (Decision 1) | (general) | None |
| 2 | `sdd/bin/prompt-drift-scan.sh` | Create | sinais, slot, `--conteudo`, `--self-test` (Decisions 2, 3, 4) | (general) | None |
| 3 | `sdd/templates/fragments/LLM_PROMPTS_DESIGN.md` | Create | dono do inventário e do contrato (Decision 6) | (general) | None |
| 4 | `sdd/bin/design-lint.py` | Modify | `lint_prompts` (Decision 5) | (general) | 3 |
| 5 | `sdd/templates/DESIGN_TEMPLATE.md` | Modify | comentário com as colunas (Decision 6) | (general) | 3 |
| 6 | `sdd/templates/fragments/LLM_PROMPTS_BUILD_REPORT.md` | Modify | `sdd-loop-builder`, scan, 1 entrada + 1 por estágio (AT-026) | (general) | 2 |
| 7 | `sdd/templates/UX_REVIEW_TEMPLATE.md` | Modify | tabela WCAG e Acceptance notes (Decision 9) | (general) | 1 |
| 8 | `sdd/config.example.yaml` | Modify | `prompts.wrapper_pattern` (Decision 3) | (general) | 2 |
| 9 | `.agents/skills/sdd-loop-builder/references/loop-spec-rules.md` | Create | regras e molde da LOOP_SPEC v2 (Decision 8) | (general) | None |
| 10 | `.agents/skills/sdd-loop-builder/references/exemplo-loop-spec.md` | Create | exemplo `standard` (Decision 8) | (general) | 9 |
| 11 | `.agents/skills/sdd-loop-builder/references/como-falar.md` | Create | glossário e exemplo completo (UX U5, U10) | (general) | None |
| 12 | `.agents/skills/sdd-loop-builder/SKILL.md` | Create | a skill (Decision 8) | (general) | 9, 10, 11 |
| 13 | `.agents/skills/sdd-build/SKILL.md` | Modify | passo 4, itens 1 e 2; 2.6.0 (Decision 7) | (general) | 2, 3, 12 |
| 14 | `.agents/skills/sdd-design/SKILL.md` | Modify | 5.5; 2.5.0 (Decision 6) | (general) | 3 |
| 15 | `.agents/skills/sdd-ux-review/SKILL.md` | Modify | passo 4.5; 2.5.0 (Decision 9) | (general) | 1, 7 |
| 16 | `.agents/skills/sdd-prompt-builder/references/sdd-integration.md` | Modify | scan, slot, nome da skill, contrato de estágio, nomes das colunas, fase Build (AT-026, Decision 6) | (general) | 2, 3, 12 |
| 17 | `.agents/skills/sdd-prompt-builder/SKILL.md` | Modify | 2.1.2; descrição fala em fase Build | (general) | 16 |
| 18 | `AGENTS.md.tmpl` | Modify | linha da skill nova (Decision 10) | (general) | 12 |
| 19 | `README.md` | Modify | 18 skills, Cross-cutting, link do doc (Decision 10) | (general) | 12, 21 |
| 20 | `README.pt-BR.md` | Modify | idem (Decision 10) | (general) | 12, 22 |
| 21 | `docs/llm-in-code.md` | Create | explica skill, roteador, inventário, scan, contraste (AT-031) | (general) | 1, 2, 3, 12 |
| 22 | `docs/pt-BR/llm-in-code.md` | Create | versão PT (AT-031) | (general) | 21 |
| 23 | `docs/roadmap.md` | Modify | linha só da `sdd-drive` | (general) | None |
| 24 | `docs/pt-BR/roadmap.md` | Modify | idem | (general) | None |
| 25 | `docs/adaptation-guide.md` | Modify | slot (AT-029) | (general) | 8 |
| 26 | `docs/pt-BR/adaptation-guide.md` | Modify | slot (AT-029) | (general) | 8 |
| 27 | `docs/cli-conventions.md` | Modify | 2 linhas de exit e palavras novas (UX U9) | (general) | 1, 2 |
| 28 | `docs/pt-BR/guia-do-aluno.md` | Modify | 18 skills e ficha `sdd-loop-builder` | (general) | 12 |
| 29 | `tests/test_contraste.py` | Create | AT-001 a AT-007 | (general) | 1 |
| 30 | `tests/test_prompt_drift_scan.py` | Create | AT-008 a AT-015 | (general) | 2 |
| 31 | `tests/test_design_lint.py` | Modify | AT-016 a AT-018 | (general) | 3, 4 |
| 32 | `tests/test_f13_textos.py` | Create | AT-018 a AT-020, AT-023 a AT-030, AT-032 | (general) | 5, 6, 7, 8, 12, 13, 14, 15, 16, 18 |
| 33 | `tests/test_skill_lint.py` | Modify | 17 → 18 | (general) | 12 |
| 34 | `tests/test_conversa.py` | Modify | 17 → 18; bloco comum em 16 | (general) | 12 |
| 35 | `tests/test_docs.py` | Modify | roadmap, guia, doc novo (Decision 10) | (general) | 19, 20, 21, 22, 23, 24, 28 |
| 36 | `tests/test_decisoes_lint.py` | Modify | contagem nova de perguntas | (general) | 11, 13 |
| 37 | `tests/test_contrato_build_release.py` | Modify | pinos de `sdd-build` e `sdd-design` | (general) | 13, 14 |
| 38 | `tests/test_correcoes_w0.py` | Modify | pino de `sdd-build` | (general) | 13 |
| 39 | `MANIFEST.txt` | Modify | arquivos novos, `LC_ALL=C sort` | (general) | 1, 2, 3, 9, 10, 11, 12, 21, 22, 29, 30, 32 |
| 40 | `sdd/templates/fragments/WORKER_BRIEF.md` | Modify | exclusão dura: as 2 skills de prompt (Decision 7) | (general) | 12 |

**Total Files:** 40

### Agent Assignment Rationale

| Agent / Owner | Files Assigned | Why |
|---|---|---|
| (general) | 1–40 | modo default (um agente), como nas F9–F12; sem catálogo de agentes no repositório |

**Agent Discovery:** Not available

Fora do commit (evidência, branch `docs/`): `sdd/reports/evidence/F13_UX_LLM/` (`ev.sh`, `codex-roteador.sh`, DESIGN de exemplo, baseline, sabotagens, `ledger-review.md`, `real-rodada.sh`).

---

## Landmines aplicáveis

Varredura rodada em 2026-11-04 com `playbook-lint.sh --grep` sobre `contraste`, `scan`, `grep`, `LC_ALL`, `awk`, `exit 64`, `drift`, `prompt`, `loop`, `skill`, `design-lint`, `template`, `fragment`: 2 achados, os 2 de `grep`.

| LM-nnn | Superfície | Tratamento |
|---|---|---|
| LM-001 | `contraste.sh`, scan, `design-lint.py` | ✔ cada regra roda com casos dos 2 lados, o teste confere exit e texto; 1 sabotagem por script |
| LM-002 | testes novos e o `grep` do scan | ✔ baseline vermelha na `v2.4.0`; expressão inválida no slot sai 64, nunca "não achei" |

---

## Code Patterns

### Pattern 1: 1ª linha, `RESULTADO:` e `→`

```bash
printf '%s:1 %s (piso %s:1)\n' "$razao" "$veredito" "$piso"
printf 'RESULTADO: %s\n' "$veredito"
printf '→ %s\n' "$conserto"
```

### Pattern 2: erro de uso

```bash
erro_uso() {
  printf '🛑 %s\n' "$1" >&2
  printf 'RESULTADO: ERRO DE USO\n' >&2
  printf '→ %s\n' "$2" >&2
  exit 64
}
```

### Pattern 3: expressão do slot validada antes de usar

```bash
if [ -n "$slot" ]; then
  grep -E -e "$slot" </dev/null >/dev/null 2>&1
  [ "$?" -eq 2 ] && erro_uso "prompts.wrapper_pattern não é uma expressão válida" "corrija o slot em sdd/config.yaml"
fi
```

### Pattern 4: raiz sem o ambiente de um hook

```bash
raiz="$( (unset GIT_DIR GIT_WORK_TREE; git rev-parse --show-toplevel) 2>/dev/null )"
[ -n "$raiz" ] || raiz="$(pwd -P)"
```

### Pattern 5: teste contra o contrato observável

```python
class Contraste(Sandbox):
    def medir(self, *args):
        return self.roda([BASH, RAIZ / "sdd/bin/contraste.sh", *args], self.tmp)

    def test_truncado_nunca_arredondado(self):
        rc, out, _ = self.medir("#6c7b67", "#ffffff")
        self.assertEqual(rc, 2)
        self.assertEqual(out.splitlines()[0], "4.49:1 REPROVA (piso 4.5:1)")
```

---

## Data Flow

```text
UX review
1. par real de cores → contraste.sh → PASSA ou REPROVA → linha da tabela com a evidência
2. REPROVA → 1 MUST em UX/CX Findings; 2.1.1 e 2.5.8 → Acceptance notes

Design (LLM Prompts: true)
3. fragmento copiado para o DESIGN → linhas com Tipo + 1 contrato por linha → design-lint.py

Build, para cada arquivo
4. o arquivo está no inventário (ou é estágio de uma LOOP_SPEC gerada)?
   ├─ sim → Tipo
   │        ├─ one-shot → skill de prompts.builder_skill → texto
   │        ├─ loop → sdd-loop-builder → LOOP_SPEC + estágios → 1 prompt por estágio LLM → textos
   │        └─ ausente → triagem; na dúvida, loop; registrar
   │        texto → prompt-drift-scan.sh --conteudo <caminho>
   │        ├─ 0 ou 2 → gravar (2 é o esperado aqui)
   │        └─ 64 → corrigir a chamada; nunca ignorar
   └─ não → conteúdo a gravar → prompt-drift-scan.sh --conteudo <caminho>
            ├─ 0 → gravar
            ├─ 2 → parar: iterar o DESIGN ou registrar falso positivo
            └─ 64 → corrigir a chamada; nunca ignorar
5. BUILD_REPORT: 1 entrada por prompt; em loop, 1 pela LOOP_SPEC + 1 por estágio
```

---

## Integration Points

| External System | Integration Type | Authentication | Direction | Failure / Retry |
|---|---|---|---|---|
| None em runtime | N/A | N/A | N/A | os 2 scripts não usam rede |
| Codex CLI (só a prova, fora do pacote) | CLI | `auth.json` copiado para `CODEX_HOME` temporário | out | sem credencial, a prova não roda e isso é registrado; não há retry automático |
| OpenRouter + CLIs (só a revisão real, fora do pacote) | `adversarial-review.sh` | `OPENROUTER_API_KEY` só no ambiente do processo | out | exits já contratados pela F10 |

---

## Testing Strategy

| Test Type | Scope / Requirement | Files | Tools | Pass Signal |
|---|---|---|---|---|
| Unit (script) | AT-001 a AT-007 | `tests/test_contraste.py` | `unittest` + `apoio.Sandbox` | exit e 1ª linha iguais aos oráculos calculados fora do script |
| Unit (script) | AT-008 a AT-015; ataques: `a\|b` no slot, comentário depois da aspa, CRLF, pasta `tests` acima da raiz, symlink para o projeto, `package-ecosystem:`, `GIT_DIR` herdado, arquivo ilegível (`chmod 000`, com skip como root), self-test por caminho relativo, entrada de terminal por `pty` | `tests/test_prompt_drift_scan.py` | idem | exit, caminho e sinal corretos; pasta temporária sem resíduo |
| Unit (lint) | AT-016 a AT-018 | `tests/test_design_lint.py` | idem | cada falta nomeada; DESIGN sem seção igual |
| Contrato de texto | AT-018 a AT-020, AT-023 a AT-030, AT-032 | `tests/test_f13_textos.py` | idem | frases e nomes coerentes entre skill, fragmento, lint e integração |
| Contagens | AT-022, AT-033 | `test_skill_lint.py`, `test_conversa.py`, `test_decisoes_lint.py`, pinos | idem | 18 skills; versões; `check-versions.py` 0 |
| Docs | AT-031 | `tests/test_docs.py` | idem | links abrem; 3 linhas no roadmap |
| Smoke real | AT-020, AT-021 | `evidence/F13_UX_LLM/codex-roteador.sh` | `codex exec` | 3 execuções por efeito; 2 controles reprovados |
| Smoke no repositório | AT-033, AT-034 | logs em `evidence/F13_UX_LLM/` | `git diff --quiet`, `check-versions.py` | exit 0 |
| E2E / Verify Gate | todos os de `kind: test` | `verify-gate.sh --strict` | `git archive`, `publish-gate.sh`, `unittest discover` | exit 0 no piso bash 3.2 + Python 3.9 |

Baseline vermelha na `v2.4.0` e 1 sabotagem por script ficam em `evidence/F13_UX_LLM/`.

---

## Error Handling

| Error Type | Detection | Handling Strategy | Retry? | Observability |
|---|---|---|---|---|
| Cor, alpha ou piso inválido | expressão no bash | saída 64 com causa e conserto; `rgba(...)` ensina o 3º valor | N/A | `🛑` + `RESULTADO: ERRO DE USO` |
| Caminho inexistente, pasta, arquivo ilegível, entrada de terminal ou vazia | `-e`, `-f`, `-r`, `-t 0`, `-s` | saída 64, sem `LIMPO` | N/A | idem |
| `grep` de conteúdo com saída 2 | exit medido em cada chamada | saída 64, nunca "não achei" | N/A | idem |
| Expressão inválida ou valor malformado no slot | exit 2 do `grep -E` na pura e na composta; texto depois da aspa | saída 64 | N/A | idem |
| Slot vazio ou config ausente | valor vazio | roda sinais genéricos e avisa | N/A | `⚠️` na saída |
| Inventário sem coluna ou campo | `lint_prompts` | exit 1, um item por linha, frase da v2.5.0 | N/A | `🛑` + `RESULTADO: VERMELHO` |
| Linha sem `Tipo` no Build | leitura do inventário | triagem; dúvida vira `loop`; registro | N/A | linha no BUILD_REPORT |
| Skill ausente | o agente não acha a skill | bloqueia o item, pergunta `[D2 · muda o produto]` | N/A | 🛑 na conversa |
| Falha de self-test | exit ou texto diferente | exit 2, nomeando o caso | N/A | `RESULTADO: VERMELHO` |

---

## Configuration

| Config Key | Type | Source / Default | Sensitive? | Description |
|---|---|---|---|---|
| `prompts.wrapper_pattern` | string (expressão estendida) | `sdd/config.yaml`; `""` | No | expressão do parâmetro do wrapper de LLM; o script acrescenta "seguida de literal" |
| `prompts.builder_skill` | string | já existe; `sdd-prompt-builder` | No | continua como está |

---

## Security Considerations

- O slot vai só para `grep -E -e`, nunca para `eval`; expressão inválida sai 64.
- `--conteudo` grava a entrada numa pasta de `mktemp -d`, com `trap` de limpeza, e não a imprime na saída; um segredo no texto avaliado não vai para o log.
- `rm -rf` só com a variável protegida contra vazio, no self-test.
- Sem rede nos 2 scripts; a chave da OpenRouter só existe no ambiente do processo da revisão real, nunca em arquivo.
- Os testes não levam literal que o publish-gate reprove.

---

## Observability

| Aspect | Implementation | Signal / Why |
|---|---|---|
| Logging | saída dos scripts, sem arquivo | `RESULTADO:` + `→` em toda saída |
| Metrics | N/A em runtime | na F15: quantos DRIFT viraram inventário e quantos foram falso positivo (UX, lente S) |
| Tracing | `AVAL*-*.log` e o transcript da prova, fora do commit | prova do que rodou |

---

## Requirements Traceability

| Requirement / AT | Design Element | Test / Gate |
|---|---|---|
| AT-001 a AT-007 (U2) | Decision 1; manifest 1 | `tests/test_contraste.py` |
| AT-008 a AT-015 (L4) | Decisions 2, 3, 4; manifest 2 | `tests/test_prompt_drift_scan.py` |
| AT-016, AT-017 (L3) | Decision 5; manifest 4 | `tests/test_design_lint.py` |
| AT-018 (L3) | Decision 6; manifest 3, 5, 14 | `test_design_lint.py`, `test_f13_textos.py` |
| AT-019, AT-020 (L2) | Decision 7; manifest 13, 40 | `test_f13_textos.py`; AT-020 também em `codex-roteador.sh` |
| AT-021 (L2) | Decision 12 | `codex-roteador.sh`, com 3 execuções e 2 controles |
| AT-022 (L1) | Decisions 8, 11; manifest 9–12 | `test_skill_lint.py`, `test_conversa.py` |
| AT-023 a AT-025 (L1) | Decision 8; manifest 9, 10, 12 | `test_f13_textos.py` |
| AT-026 (L2) | manifest 6, 16 | `test_f13_textos.py` |
| AT-027, AT-028 (U1) | Decision 9; manifest 7, 15 | `test_f13_textos.py` |
| AT-029 | Decisions 3, 10; manifest 8, 25, 26 | `test_f13_textos.py` |
| AT-030 | Decision 11; manifest 39 | `test_f13_textos.py`, `publish-gate.sh` |
| AT-031 | Decision 10; manifest 19–24, 27, 28 | `test_docs.py` |
| AT-032 | regras 4 e 10 do 8.0 | `test_f13_textos.py`, `test_agnostico.py` |
| AT-033 | Decision 11; manifest 13–17, 36–38 | log de `check-versions.py` no repositório, pinos |
| AT-034 | Decision 11 | log de `git diff --quiet v2.4.0 HEAD` + Verify Gate |
| Governança N.A. | passo 11 do `sdd-define` | `verify-gate.sh` |

---

## Risks and Mitigations

| Risk | Impact | Mitigation | Residual Risk |
|---|---|---|---|
| O agente pula o roteador | Prompt escrito sem LOOP_SPEC | AT-021 com 3 execuções em agente real; revisão fresca | Aceito pelo Roberto (abordagem A) |
| GNU grep e mawk não medidos localmente | Diferença só no Ubuntu | Casos `(` e `[`; `awk` POSIX; CI nos 2 | Baixo; medido no PR |
| `awk` de macOS e de Ubuntu diferem | Número diferente | Oráculos fixos, CI nos 2 | Baixo |
| Scan dispara demais em YAML e config | Alarme ignorado | Falso positivo tem caminho de registro; exclusões | Medir na F15 |
| `design-lint` reprova DESIGN em andamento | Susto depois de atualizar | Frase própria e `→` para o fragmento | Baixo |
| A suíte passa do teto do macOS | CI cancelado | Testes sem rede; poucos `init`; medir no PR | Baixo: 28 de 45 min |
| Regressão em conserto tardio | Defeito novo depois da revisão | Teste de ataque em cada conserto; prova real no fim | Médio; lição da F12 |

---

## Advisor Ledger

Revisão de contexto fresco do DESIGN v1.0 (`sdd/reviews/REVISAO_DESIGN_F13_UX_LLM_20261104.md`, modo `contrato`, logs `AVAL-DESIGN-01-*.log`): NEEDS_WORK, 3 HIGH, 7 MEDIUM, 6 LOW, 5 propostas. Aplicada por quem conduz o fluxo; o Roberto recebe a lista na conversa.

| # | Nota | Severidade | Veredito | Onde |
|---|---|---|---|---|
| P1 | O gate não cobre AT-033, AT-034; AT-017 lê arquivo não versionado | proposta | ACEITA em parte: AT-017 inline, AT-033 e AT-034 com log no repositório. RECUSADA a mudança do `cmd`: o prompt da sessão o fixou, e o CI já roda `check-versions.py` na release | DEFINE v1.2; Decision 12 |
| P2 | AT-021 circular | proposta | ACEITA | DEFINE AT-021; Decision 12 |
| P3 | Bloqueio e triagem nunca rodam num agente | proposta | ACEITA: 3 execuções | DEFINE AT-020, AT-021; Decision 12 |
| P4 | AT-006 sem dentes sem o locale | proposta | ACEITA | DEFINE AT-006 |
| P5 | Arquivo ilegível e `grep` com saída 2 concluem `LIMPO` | proposta | ACEITA | DEFINE AT-013; Decision 4 |
| D1 | Roteador pede o texto que ele deveria produzir | HIGH | APLICADA | Decision 7; DEFINE AT-019; Data Flow |
| D2 | Caminho absoluto por symlink vira falso `LIMPO` | HIGH | APLICADA | Decision 2; DEFINE AT-009 |
| D3 | AT-030 contra o `sync` | HIGH | APLICADA: `init` completa, `sync` só gera o adaptador; `test_sdd_open.py` fora da Traceability | DEFINE AT-030 |
| D4 | `Tipo=loop` não fecha | MEDIUM | APLICADA | Decision 6; manifest 16 |
| D5 | `system:` casa substring | MEDIUM | APLICADA | Decision 2; DEFINE AT-011 |
| D6 | Formato antigo passa no lint | MEDIUM | APLICADA | Decision 5; DEFINE AT-016 |
| D7 | Fim do valor entre aspas | MEDIUM | APLICADA | Decision 3; DEFINE AT-010, AT-012 |
| D8 | Self-test com caminho relativo | MEDIUM | APLICADA | Decisions 1, 4; DEFINE AT-015 |
| D9 | Textos que contradizem o roteador | MEDIUM | APLICADA | Decision 7; manifest 16, 17, 40 |
| D10 | Colunas sem nome; racional falso | MEDIUM | APLICADA | Decision 6 |
| D11 | Casos de borda do `contraste.sh` | LOW | APLICADA | Decision 1; DEFINE AT-005 |
| D12 | `#` sem aspas | LOW | APLICADA | Decision 1; DEFINE AT-005 |
| D13 | O scan cai nos próprios sinais | LOW | APLICADA: registro, sem exceção no script | Decision 2 |
| D14 | Modo de execução | LOW | APLICADA: `bash sdd/bin/…`, 100644 | Decision 1 |
| D15 | Contagem prevista | LOW | APLICADA: o teste registra o valor medido | Decision 7 |
| D16 | Validação do slot diverge entre sistemas | LOW | APLICADA: pura e composta; `(` e `[` | Decision 3; DEFINE AT-013 |

Avaliador de contexto fresco, ciclo 1 (`sdd/reviews/AVALIACAO_F13_UX_LLM_20261104-ciclo1.md`, logs `AVAL1-*.log`): NEEDS_WORK, 1 HIGH, 8 MEDIUM, 11 LOW.

| # | Nota | Severidade | Veredito | Onde |
|---|---|---|---|---|
| A1 | AT-021 sem prova no HEAD | HIGH | APLICADA: a prova roda depois do último conserto; a amostra ganhou o que faltava | Decision 12 |
| A2 | `--conteudo` com pasta conclui LIMPO | MEDIUM | APLICADA, com teste de ataque | DEFINE AT-013 |
| A3 | Contrato do laço não se compila; Build sem rota para a recusa | MEDIUM | APLICADA | Decisions 5, 6, 7; DEFINE AT-016, AT-019 |
| A4 | Modo `briefs` sem quem rode o scan | MEDIUM | APLICADA: orquestrador varre em disco na wave | Decision 7; `WORKER_BRIEF.md` |
| A5 | Furos da conferência da prova | MEDIUM | APLICADA: 16 controles, 3 válidos e 13 ruins | Decision 12 |
| A6 | Perfil não se decide só pelo risco | MEDIUM | APLICADA | Decision 8 |
| A7 | Gate verde só no commit anterior | MEDIUM | APLICADA: gate no commit final | Build |
| A8 | `sdd/config.yaml` ilegível vira slot vazio | MEDIUM | APLICADA, com teste | DEFINE AT-013; Decision 4 |
| A9 | Formas comuns de prompt passam LIMPO | MEDIUM | APLICADA: sinais ampliados, limite documentado | Decision 2; DEFINE AT-008 |
| L1 | PROMPTS PENDENTES não chega à skill de prompt | LOW | APLICADA | `sdd-build`, `sdd-integration.md`, fragmento |
| L2 | Tabela de estágios fora do arquivo | LOW | APLICADA: o bloco inteiro vai para `LOOP_SPEC.md` | `sdd-build`, fragmento |
| L3 | Exclusão de teste vence a pasta `prompts` | LOW | APLICADA: pasta de teste → `prompts` → nome de teste. `src/test_gerador.py` segue excluído, por ser nome de teste | Decision 2; DEFINE AT-009, AT-011 |
| L4 | "Em qualquer linguagem" falso | LOW | APLICADA: lista das convenções, `spec/`, `*_spec.*`, `*Test.*` | DEFINE AT-011; docs |
| L5 | `src/Prompts/` e link de arquivo | LOW | APLICADA em parte: caixa. REBATIDA_ESCOPO o link para arquivo: o caminho que o Build grava é o do manifest, e o link é caso que nenhum fluxo gera | DEFINE AT-009 |
| L6 | Slot em formas válidas de YAML | LOW | APLICADA em parte: mapa em linha e bloco saem 64, `null` e `~` são vazio, BOM sai. REBATIDA_ESCOPO sem git em subpasta: a raiz é a pasta atual, documentado | Decision 3 |
| L7 | Variações no lint | LOW | APLICADA em parte: variações do título, traço, frase neutra, rumo com os 2 erros. REBATIDA_ESCOPO a 2ª seção e o destino fora do manifest: o passo 5.5 manda usar arquivo do manifest, e item sem linha no relatório é item não construído | Decision 5 |
| L8 | Teste de idioma não pega a retirada da guarda | LOW | APLICADA em parte: não pula no macOS; a sabotagem com `%f` derruba o teste. REBATIDA_EVIDENCIA a retirada isolada: a saída é inteiro + ponto literal, e `sabotagens.log` mostra que o idioma não a alcança; a guarda é proteção extra | `tests/test_contraste.py` |
| L9 | Self-test sem terminal e sem grep 2 | LOW | APLICADA: grep 2 no self-test; terminal só em `tests/`, com pty | DEFINE AT-015 |
| L10 | Bordas do `contraste.sh` | LOW | APLICADA: `RGBA`, `#rrggbbaa`, `CDPATH`. REBATIDA_ESCOPO `--piso` repetido: vale o último, como em outros comandos | Decision 1 |
| L11 | `codex-roteador.sh` sem `trap` | LOW | APLICADA | evidência |

Avaliador de contexto fresco, ciclo 2 (`sdd/reviews/AVALIACAO_F13_UX_LLM_20261104-ciclo2.md`, logs `AVAL2-*.log`): NEEDS_WORK, 2 MEDIUM, 9 LOW, nenhum HIGH. Limite de 2 ciclos da `sdd-build`: os consertos abaixo não têm ciclo 3, e a revisão adversarial real é o olhar independente sobre eles.

| # | Nota | Severidade | Veredito | Onde |
|---|---|---|---|---|
| N1 | `sdd/config.yaml` que existe e não se lê conclui LIMPO | MEDIUM | APLICADA: link quebrado, pasta, FIFO, `sdd/` sem permissão e falha do `awk` saem 64, com teste | DEFINE AT-013; Decision 4 |
| N2 | Conferência aceita execuções ruins | MEDIUM | APLICADA: calço registra a chamada real; 21 controles | DEFINE AT-021; Decision 12 |
| L1 | Casos de slot inválido do self-test passavam por outro motivo | LOW | APLICADA: arquivo existente | self-test |
| L2 | Mutantes que sobrevivem | LOW | APLICADA: testes de CDPATH relativo, `role: "system:admin"` e `generate_content` | testes |
| L3 | Formas de prompt que passam | LOW | APLICADA em parte: `:=`, `=>`, `['role']`, `const`. REBATIDA_ESCOPO o resto: a busca é por formas comuns e não é exaustiva, agora dito nos 2 idiomas; o slot cobre o que faltar | Decision 2; docs |
| L4 | Sinais falsos | LOW | APLICADA: fronteira no fim do SDK; a chave só vale no início da linha ou depois de `{`, `,`, `(`, `[` e `const`/`let`/`var` | Decision 2 |
| L5 | Variações no lint | LOW | APLICADA em parte: traços e títulos. REBATIDA_ESCOPO blocos por posição: o fragmento diz "na mesma ordem"; o mesmo título em 3º nível é subtítulo de outra seção | Decision 5 |
| L6 | Formas de YAML | LOW | APLICADA em parte: `prompts: {}` é vazio, chaves entre aspas, `&` e `!` saem 64. REBATIDA_ESCOPO sub-chave aninhada: nenhum exemplo do pacote a usa | Decision 3 |
| L7 | Rota "não é laço" sem destino | LOW | APLICADA | `sdd-build` |
| L8 | "Depois da entrega" ficou para trás | LOW | APLICADA | `sdd-loop-builder` |
| L9 | Regra de perfil com sobra | LOW | APLICADA: `standard` é "todo outro caso" | `loop-spec-rules.md` |

Avaliador de contexto fresco, ciclo 3, por decisão D4 do Roberto (`sdd/reviews/AVALIACAO_F13_UX_LLM_20261104-ciclo3.md`, logs `AVAL3-*.log`): NEEDS_WORK, 1 MEDIUM, 5 LOW, sobre `5ddc433`. Sem 4º ciclo, por decisão D4.

| # | Nota | Severidade | Veredito | Onde |
|---|---|---|---|---|
| M1 | Regressão do conserto de L4 do ciclo 2: lista YAML e atributo concluem LIMPO; `role: system` nunca disparou | MEDIUM | APLICADA, com testes dos 2 lados | Decision 2; DEFINE AT-008 |
| L1 | 2 motivos de saída 64 sem dente no self-test; `tests/` os cobre | LOW | REBATIDA_ESCOPO: pendência da v2.5.1 | `tests/test_prompt_drift_scan.py` |
| L2 | Formas raras (`String system = "x";`, `ask system: "x"`, `Role: "system"`) | LOW | REBATIDA_ESCOPO: a busca não é exaustiva, como diz o doc; o slot cobre | docs |
| L3 | Títulos com palavra depois de "LLM Prompts" ("v2", "do sistema") passam sem conferência | LOW | REBATIDA_ESCOPO: pendência da v2.5.1 | `design-lint.py` |
| L4 | O log da rodada 5 não mostra `--aceitar-sem-revisor2` | LOW | APLICADA | evidência |
| L5 | Decision 2 defasada | LOW | APLICADA | Decision 2 |

Revisão adversarial real, rodadas 1 a 3: 0 HIGH, 4 MED e 12 LOW, com auditor independente; veredito por achado em `sdd/reports/evidence/F13_UX_LLM/ledger-review.md`. A rodada 3 deu `loop` PRONTO no teto. Decisão D4 do Roberto (2026-11-04): corrigir os 4 achados dela e rodar a 4ª. Sem créditos no Codex, nova decisão D4: 2º revisor dispensado na rodada 5 e prova real aceita como está, com o risco registrado no DEFINE.

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | 2026-11-04 | SDD Design by RDD | Initial version |
| 1.1 | 2026-11-04 | revisão fresca | Ledger acima; roteador na ordem nova; 40 arquivos |
| 1.2 | 2026-11-04 | avaliador, ciclo 1 | A1 a A9 e L1 a L11 no Ledger; sinais ampliados; perfil decidido sem ambiguidade |
| 1.3 | 2026-11-04 | avaliador, ciclo 2 | N1, N2 e L1 a L9 no Ledger; calço na prova real |
| 1.4 | 2026-11-04 | avaliador, ciclo 3 | M1 e L1 a L5 no Ledger |

---

## Next Step

Execute o **SDD Build by RDD**.
