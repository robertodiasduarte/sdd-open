# DESIGN: F23B2 Modelo por papel

> Slot `papeis:` lido por um verbo do `sdd-fluxo.sh`, despacho e marca de papel num texto só (a escada de contexto
> fresco), custo por papel no `custo-feature.sh`, e dois scripts novos: `papel-serie.sh` (roda as séries com teto e
> trava) e `papel-medir.sh` (só conta e escolhe).

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | F23B2_MODELO_POR_PAPEL |
| **Date** | 2026-11-16 |
| **Author** | design-agent (decisões [auto] registradas abaixo) · Roberto Dias Duarte (decisões do DEFINE) |
| **DEFINE** | [DEFINE_F23B2_MODELO_POR_PAPEL.md](./DEFINE_F23B2_MODELO_POR_PAPEL.md) v1.1 |
| **Status** | Ready for Build (depois da revisão do DESIGN; build só depois que a F24 entrar na `main`) |

---

## Architecture Overview

```text
 sdd/config.yaml                                   (pacote: só o método; nomes e preços ficam fora)
   papeis: curador · avaliador · revisao_design · cartografo · executor · serie_cmd
      │
      ├──► sdd-fluxo.sh modelo <papel>  ──► valor validado (ou vazio) ──┐
      │                                                                 │
      │     contexto-fresco.md (escada de despacho, texto único)        │
      │       1. marca-fase.sh inicio papel-<papel> <F>                 │
      │       2. subagente com o modelo ◄───────────────────────────────┤
      │          ou sdd-fluxo.sh despachar (parada diz o modelo) ◄──────┘
      │       3. marca-fase.sh fim papel-<papel> <F>
      │                         │
      │                         ▼  sdd/traces/<F>.jsonl (src=fase, fase=papel-*)
      │              custo-feature.sh <F>  ──► CUSTO_<F>.md: fases + "↳ papel …" (fora do total)
      │
      └──► papel-serie.sh <série>   (roda; teto e trava; nunca julga)
              para cada caso × candidato × repetição (referência primeiro):
                 confere teto ──► cópia isolada (git archive + entrada/, git sem remoto)
                 snapshot do projeto ──► bash -c "$serie_cmd" (SDD_MODELO, SDD_BRIEF…) ──► snapshot
                 custo-feature.sh --execucao <cópia> ──► meta.txt (tokens, nominal, pago, modelos)
                                │
                                ▼  <série>/execucoes/<caso>/<candidato>/<rep>/{saida.txt, meta.txt}
           papel-medir.sh <série>   (só lê; pontua contra o gabarito; escolhe ou diz por que não)
```

## Components

| Componente | Responsabilidade | Mora em |
|---|---|---|
| Slot `papeis:` | modelo por papel + comando da série; vazio = como hoje | `sdd/config.example.yaml` |
| Verbo `modelo` | lê e valida `papeis.<papel>` (aceita o nome do despacho: `revisor-design`, `executor-drive`) | `sdd/bin/sdd-fluxo.sh` |
| `despachar` | parada de sessão nova ganha a linha do modelo | `sdd/bin/sdd-fluxo.sh` |
| Escada de despacho | modelo do papel e marcas de papel, para todos os papéis | `.agents/skills/sdd-build/references/contexto-fresco.md` |
| Custo por papel | separa as marcas `papel-*` das de fase; sub-linhas fora do total; modo `--execucao` | `sdd/bin/custo-feature.sh` |
| Executor das séries | cópia isolada, teto e trava, fronteira, retomada, custo por execução | `sdd/bin/papel-serie.sh` (novo) |
| Medidor | pontua curador e avaliador, junta repetições, escolhe o mais barato na meta | `sdd/bin/papel-medir.sh` (novo) |
| Gabarito do Open | casos do histórico (fora do pacote) | `sdd/reports/evidence/F23B2_MODELO_POR_PAPEL/gabarito/` |

---

## Key Decisions

### Decision 1: O slot é lido por um verbo do `sdd-fluxo.sh`, com validação estrita

| **Status** | Accepted | · | **Date** | 2026-11-16 |

**Context:** O valor do slot vai para a linha de comando do agente (`--model`, `-m`) e para a parada que a pessoa
lê. O `sdd-fluxo.sh` já tem o leitor de YAML de 1 nível (`slot()`) e o `despachar`.
**Choice:** `sdd-fluxo.sh modelo <papel>` (núcleo Python): aceita `curador`, `avaliador`, `revisao_design`,
`cartografo`, `executor` e os nomes do despacho (`revisor-design` → `revisao_design`, `executor-drive` →
`executor`); imprime o valor (linha vazia quando vazio ou ausente) e sai 0; valor fora de
`^[A-Za-z0-9][A-Za-z0-9._:/-]{0,79}\Z` (começa por letra ou número, para não virar opção do agente) sai 64 com a chave e o motivo, sem imprimir o valor; papel fora da lista sai 64. O
`despachar` chama o verbo para os papéis com slot e, com valor, acrescenta `**Modelo:** …` à parada; com 64, sai
64 antes de gravar o brief. `revisor-governanca` não tem slot (fora dos 5 papéis do BRAINSTORM).
**Rationale:** um leitor só para o despacho e para o subagente (LM-005); a regex fecha espaço, aspas e quebra de
linha, que virariam argumento extra no agente (AT-002).
**Alternatives Rejected:** 1. script novo `papel-slot.sh` — rejeitada porque duplicaria o leitor de YAML · 2. cada
skill ler o YAML — rejeitada porque a validação ficaria em prosa.
**Consequences:** o `slot()` tira aspas e comentário antes da regex, então `"a b"` vira `a b` e é recusado; ganha-se
um ponto único de validação.

### Decision 2: O despacho e as marcas de papel ficam na escada de contexto fresco, não em cada skill

| **Status** | Accepted | · | **Date** | 2026-11-16 |

**Context:** Os 5 papéis são despachados por 5 skills (define, design, build, drive, release), e todas apontam para
`sdd-build/references/contexto-fresco.md`. A `sdd-release` está com 500 linhas (LM-038) e a F24 a reescreve.
**Choice:** uma seção nova "Modelo do papel e marca de papel" no `contexto-fresco.md`: antes do despacho,
`bash sdd/bin/marca-fase.sh inicio papel-<papel> <F>` e `bash sdd/bin/sdd-fluxo.sh modelo <papel>`; com valor,
passe-o como o modelo do subagente quando o agente deixa escolher (sem nome de agente ou modelo no texto); sem como
escolher, diga em 1 linha que o papel roda no modelo da sessão; na volta, `marca-fase.sh fim papel-<papel> <F>`. O
modo `contrato` do avaliador usa `revisao_design`. Só a `sdd-build` sobe de versão (o arquivo é dela); o fragmento
`MARCA_FASE.md` ganha 1 parágrafo sobre a marca de papel.
**Rationale:** uma edição cobre os 5 papéis; nenhuma `SKILL.md` perto do teto muda; o `contexto-fresco.md` não vai para
o starter (o build do starter sai de `web/MODO_WEB.md`), então não há troca.
**Alternatives Rejected:** 1. uma linha por skill — rejeitada pelo teto da `sdd-release` e pelo conflito com a F24 ·
2. o `despachar` gravar a marca sozinho — rejeitada porque o caminho do subagente não passa por ele.
**Consequences:** o papel despachado sem passar pela escada fica sem marca e cai na fase (como hoje); ganha-se o
custo por papel em qualquer agente.

### Decision 3: O custo por papel sai de marcas `papel-*`, em sub-linhas fora do total

| **Status** | Accepted | · | **Date** | 2026-11-16 |

**Context:** O `custo-feature.sh` só conta janelas sem sobreposição: uma marca `inicio papel-avaliador` dentro do
build fecharia o build ("fase sem fim"). A divisão por arquivo de subagente é só do Claude Code.
**Choice:** `ler_trace` separa as marcas cujo nome começa com `papel-`; as de fase seguem como hoje. As de papel
viram janelas próprias, por papel (podem se sobrepor entre papéis); cada mensagem da janela soma na sub-linha
`↳ papel <nome> · <modelos vistos>`, além de continuar na fase; a coluna Execuções da sub-linha é o número de janelas
daquele papel (3 ciclos do avaliador = 3). As sub-linhas vêm logo depois da fase e **não** entram
no total. Marca de papel sem par vai para "Fora da conta", como a de fase.
**Rationale:** total igual à soma das fases mais a revisão (AT-003); vale para qualquer agente que tenha leitor de
sessão; o modelo efetivo sai dos registros, não da palavra de quem despachou.
**Alternatives Rejected:** 1. papel como fase própria, tirando as mensagens da fase — rejeitada porque o build
deixaria de somar o avaliador e a linha de base da B1 mudaria de sentido · 2. arquivo `subagents/*.meta.json` —
rejeitada por ser de um agente só.
**Consequences:** a sub-linha inclui o que a sessão principal fez durante a janela (em primeiro plano, quase nada);
ganha-se a conta por papel sem tocar na regra das fases.

### Decision 4: O executor das séries roda o comando do projeto numa cópia isolada, com teto checado antes de cada chamada

| **Status** | Accepted | · | **Date** | 2026-11-16 |

**Context:** A medição chama agente (perfil de risco: teto fechado e trava automática, "rodada pelo projeto"). O
avaliador executa comandos; o curador lê arquivos. O pacote não pode fixar agente nem modelo.
**Choice:** `papel-serie.sh <série> [--cmd <comando>] [--candidatos x,y] [--teto-s 1800]` (sem `--casos`: v1.2). A série
mora numa pasta de medição: `<medição>/teto.txt` (`teto_pago`, `teto_nominal`) vale para **todas** as séries da
pasta, e o acumulado soma as execuções de todas elas (R1: o teto do DEFINE é da frente, não de cada papel). Cada
série tem `serie.txt` (`papel`, `gabarito`, `repeticoes`) e `candidatos.tsv` (`id · modelo · cobranca`, 1ª linha =
referência; o `modelo` passa pela mesma regex do slot, R10). Ordem: **todas** as execuções da referência, em todos os
casos; depois o executor roda `papel-medir.sh <série> --so-referencia` e, se a referência sai fora da meta, para
antes de qualquer candidato (exit 22, N1); só então cada candidato, caso por caso, cada repetição. O comando vem de
`--cmd` ou de `papeis.serie_cmd` e roda por `bash -c`, na cópia, com `SDD_MODELO`, `SDD_BRIEF`, `SDD_PAPEL`,
`SDD_CASO`, `SDD_REP` (os docs mandam usar `"$SDD_MODELO"` entre aspas). Antes de cada chamada: cobrança
`pay-per-token` com `teto_pago` 0, ou `desconhecida`, ⇒ para; acumulado + estimativa > teto (pago ou nominal) ⇒ para;
estimativa = o maior nominal de uma execução já gravada na medição (0 na 1ª); acumulado com n/d ⇒ para ("o teto não
se confere"). A parada grava `PARADA.txt` (motivo, acumulados, execução seguinte) e sai 20. Antes de chamar, o executor
grava `inicio.txt` (caminho da cópia, horário) na pasta da execução; na retomada, a execução com `inicio.txt` e sem
`meta.txt` foi interrompida: o custo dela é medido pelo caminho gravado (`custo-feature.sh --execucao`), entra no
acumulado como `interrompida` e só então ela é refeita (R4). Cada execução gravada é pulada na retomada e seu custo
entra no acumulado (AT-009). A retomada move o `PARADA.txt` anterior para `paradas/<horário>.txt` antes de seguir, e
o medidor só lê o `PARADA.txt` atual (R6).
**Rationale:** a trava é código, não instrução; o projeto escolhe o agente (vendor-agnóstico); a estimativa pelo maior
custo já visto é conservadora sem tabela de preço no script.
**Alternatives Rejected:** 1. adaptadores do registry da revisão — rejeitada porque são texto-entra-texto-sai, sem
executar comando no caso · 2. subagentes da sessão — rejeitada porque a trava ficaria em prosa.
**Consequences:** a 1ª execução de uma série nova não tem estimativa (só o teto pago zero a segura); ganha-se uma série
retomável e com gasto limitado.

### Decision 5: Cópia isolada sem remoto e fronteira conferida pelo snapshot do projeto

| **Status** | Accepted | · | **Date** | 2026-11-16 |

**Context:** S20 aplicado (AT-011): o agente da série só pode gravar na cópia do caso.
**Choice:** a cópia nasce em `${TMPDIR:-/tmp}/sdd-serie-<12 hex>/<caso>-<candidato>-<rep>/` por `git archive <commit>`
(ou vazia com `commit: -`), recebe `entrada/` por cima e um `git init` com 1 commit, sem remoto (identidade local
na linha de comando). Antes e depois do comando: `governanca-fronteira.sh --snapshot <raiz do projeto>` e
`--comparar`; entre os dois snapshots o executor não grava nada no projeto: a saída padrão do comando vai para um
arquivo na pasta temporária, ao lado da cópia, e só é movida para `saida.txt` depois do `--comparar` (R5); `git -C <cópia> remote` não vazio antes ou depois ⇒ inválida. Fronteira com `FORA:` ⇒ a execução fica
`invalida` (fora da conta e da escolha), a série para (exit 21) com os caminhos em `PARADA.txt`; nada é apagado fora
da cópia. A cópia é apagada no fim da execução válida e mantida na inválida.
**Rationale:** reusa a fronteira que já protege cartógrafo, governança e curador; a cópia fora do projeto não mexe na
árvore medida.
**Alternatives Rejected:** 1. worktree do git — rejeitada porque traria o remoto e o `.git` do projeto · 2. container —
rejeitada por não ser bash 3.2 + Python stdlib.
**Consequences:** a conferência cobre o projeto, não o disco inteiro: o resto depende da caixa de areia do agente, e o
`docs/model-per-role.md` diz isso; ganha-se a prova do AT-011 com agente falso.

### Decision 6: O custo de uma execução sai de um modo novo do `custo-feature.sh`

| **Status** | Accepted | · | **Date** | 2026-11-16 |

**Context:** O nominal por execução precisa dos mesmos leitores de sessão, da mesma tabela e da mesma conta da B1
(LM-036, LM-005).
**Choice:** `custo-feature.sh --execucao <raiz> [--precos <pasta>] [--registry …]` lê as sessões cuja pasta é `<raiz>`
(a cópia) e imprime linhas `chave=valor`: `entrada`, `saida`, `cache_lido`, `cache_criado`, `nominal` (decimal ou
`n/d`), `modelos` (lista), `leitores`, e `RESULTADO: MEDIDO` (0) ou `SEM DADOS` (2). O executor grava isso no
`meta.txt` e calcula o pago pela cobrança do candidato (`assinatura` = 0; `pay-per-token` = nominal; `desconhecida`
= n/d).
**Rationale:** uma função de custo só no pacote; o executor não lê sessão nem preço.
**Alternatives Rejected:** 1. `--output-format json` do agente — rejeitada por ser de um agente · 2. copiar `custo_msg`
para o executor — rejeitada (LM-005).
**Consequences:** depende de o agente gravar o registro local da cópia (Claude Code e Codex gravam); ganha-se o mesmo
n/d da B1 quando não há registro.

### Decision 7: O medidor só lê, com uma regra de pontuação por papel e um veredito por exit

| **Status** | Accepted | · | **Date** | 2026-11-16 |

**Context:** AT-004 a AT-008; LM-005 (heurística sobre texto livre) e LM-028 (juiz por regex).
**Choice:** `papel-medir.sh <série> [--limiar 30] [--saida <arq>|-]`. Pontuação por execução:
- **curador** — lê o último bloco `<<<CURADORIA … >>>` de `saida.txt`, linhas da tabela pela coluna (`Tipo`, `LM`,
  `Delta`, `Recomendação`); "proposto" = `AUTO` ou `ACEITAR`; `promover` e `inv` ficam fora da conta (dependem de
  pergunta à pessoa). Contagens `LM-nnn (ajudou|mordeu)+1` contra o `esperado.txt`: precisão e recall ≥ 0,9.
  `REFINE`/`TOMBSTONE` casam pelo `LM-nnn`; `ADD` pela seção e ≥ 1 termo de `sup:` em comum; recall ≥ 2/3 (com 0
  esperados, vale 1). O delta proposto (com `\|` → `|`) passa pelo `playbook-curator.sh --aplicar` sobre o
  `playbook.md` do caso: exit 0.
- **avaliador** — lê o último bloco `<<<AVALIACAO … >>>`: a 1ª palavra depois de `VEREDITO:` e as linhas
  `| AT-nnn | … |`, com o resultado na última célula normalizado por lista fechada (`PASS`/`✅`/`passa` → PASS;
  `FAIL`/`❌`/`falha`/`NEEDS_WORK` → FAIL; `NAO_VERIFICADO`/`NÃO VERIFICADO` → NAO_VERIFICADO; outra coisa →
  ILEGIVEL). Meta: veredito igual, ≥ 90% dos ATs do gabarito com o mesmo resultado, 0 AT que é FAIL no gabarito e
  PASS na execução. AT ausente conta como diferente, nunca como PASS.
- Sem bloco, bloco ilegível ou execução `invalida` ⇒ fora da meta (a inválida também fora do custo).
Decisão, nesta ordem (R2): (1) referência com execução faltando ou `invalida` ⇒ exit 4 `PARCIAL`; (2) referência
fora da meta em qualquer execução ⇒ exit 3 `REFERÊNCIA FORA DA META` (recalibrar), mesmo com a série parada — o
executor para exatamente por isso (exit 22); (2b) série com `PARADA.txt`, candidato pela metade ou execução `invalida`
⇒ exit 4 `PARCIAL`, sem vencedor; (3) candidato sem execução não concorre (nunca `all()` sobre vazio), e
candidato com nominal n/d em alguma execução também não (AT-007); `--so-referencia` aplica só (1) e (2) às execuções
da referência e sai 0 quando ela está na meta; o `--aplicar` do curador escreve só na saída padrão
(`playbook-curator.sh:13`), que vai para um arquivo temporário: o gabarito nunca é escrito; entre os que batem a meta em todas as execuções, o de menor nominal mediano, se ≥ `--limiar`% abaixo
da mediana da referência ⇒ exit 0 `ESCOLHIDO: <id>`; senão exit 1 `SEM GANHO MEDIDO`. Somas e medianas em `Decimal`.
**Rationale:** fontes estruturadas (bloco com tabela, lista fechada de palavras) e a série da referência como prova de
calibração: se o pontuador lê errado o texto real, a referência cai e nada é escolhido (LM-011).
**Alternatives Rejected:** 1. juiz por leitor em contexto novo para cada execução — rejeitada por custo (dobraria as
chamadas) e porque os dois papéis já devolvem bloco estruturado · 2. veredito só pelo `VEREDITO:` — rejeitada porque
deixaria passar o AT com defeito dado como aprovado.
**Consequences:** o pontuador do curador depende do formato do bloco depois da F24 (A-003 do DEFINE); ganha-se uma
escolha reproduzível por exit.

### Decision 8: Formato do gabarito por caso, e o do Open fora do pacote

| **Status** | Accepted | · | **Date** | 2026-11-16 |

**Context:** o pacote leva o método; os casos do Open vêm do histórico dele (DEFINE, decisão [auto]).
**Choice:** `<gabarito>/<caso>/` com `caso.txt` (`papel:`, `commit:` sha ou `-`, `origem:` de onde veio, 1 linha
cada), `brief.md` (o brief do papel, com `@COPIA@` onde vai o caminho absoluto da cópia), `entrada/` (posta por cima
do commit), `esperado.txt` (curador: delta aceito na gramática do `--aplicar`; avaliador: `VEREDITO: <X>` e uma linha
`AT-nnn PASS|FAIL|NAO_VERIFICADO` por AT) e, no curador, `playbook.md` (o de antes da curadoria). O do Open fica em
`sdd/reports/evidence/F23B2_MODELO_POR_PAPEL/gabarito/`, montado no build: curador com 4 casos entre F14_DRIVE,
F14_PLAYBOOK, F15_SLOTS, F16W_WINDOWS, F16W2_F22, F18_F20_SEGURANCA, F23 e F23B3 (os de colheita com candidato
primeiro); avaliador com 3 casos (1 `PASS` e 2 `NEEDS_WORK` confirmados pelo ciclo seguinte), dos `AVALIACAO_*` da
branch de documentos.
**Rationale:** o brief do papel vai sem mudança (LLM Prompts false); só o caminho é trocado, mecanicamente.
**Alternatives Rejected:** 1. o executor montar o brief a partir da skill — rejeitada porque o brief do caso é o da
época, não o de hoje · 2. casos no pacote — rejeitada (são do Open, não do aluno).
**Consequences:** montar o gabarito é trabalho do build (dado, não código); ganha-se o mesmo formato para o projeto do
aluno.

### Decision 9: A guarda de nome de modelo vale para o que esta fatia cria ou muda

| **Status** | Accepted | · | **Date** | 2026-11-16 |

**Context:** O pacote já tem nomes de modelo em `sdd/review/precos.tsv`, `registry.tsv`, `stubs/` e docs da revisão;
uma guarda global reprovaria o que já está publicado.
**Choice:** teste que procura nome de modelo (famílias conhecidas e o formato `<família>-<n>-<n>`) nos arquivos novos
desta fatia, no bloco `papeis:` do `config.example.yaml`, na seção nova do `contexto-fresco.md` e no `MARCA_FASE.md`,
com mutante que planta um nome e faz o teste falhar.
**Rationale:** prova o AT-010 sem reabrir arquivos de outras fatias.
**Alternatives Rejected:** 1. padrão no `publish-gate-patterns.txt` — rejeitada porque reprovaria os arquivos antigos.
**Consequences:** os docs novos dão exemplo com marcador (`<modelo>`); ganha-se uma guarda que não cresce sozinha.

### Decision 10: Ordem do build e da medição

| **Status** | Accepted | · | **Date** | 2026-11-16 |

**Context:** A F24 (release enxuta) mexe no curador e na `sdd-release` e ainda não entrou na `main`. As séries reais
são longas (avaliador: ~27 execuções de ~15 min).
**Choice:** (1) código e testes desta fatia já, com commits locais e só o módulo novo e os testes dos arquivos tocados
rodando (a F24 não muda o bloco do curador nem o `--aplicar`, conferido no diff dela em 2026-11-16; ela só cruza
`MANIFEST.txt` e `docs/cli-conventions.md`, onde a B2 acrescenta linhas); (2) quando a F24 estiver na `main`, rebase
sobre `origin/main` e Verify Gate verde — a suíte inteira não roda enquanto a F24 roda o gate dela (LM-031: carga
derruba teste de tempo); (4) montar o gabarito; (5) série do curador (referência, depois
os 2 candidatos), série do avaliador (idem), com `--candidatos` para rodar um candidato por vez; (6) relatório do
medidor na evidência e o resultado na ficha. Candidatos e o comando local ficam na evidência (fora do pacote): o
comando roda o agente da assinatura com caixa de areia de escrita na pasta da cópia, nunca com as permissões
desligadas.
**Rationale:** a prova depende do formato do curador depois da F24; um candidato por vez deixa parar cedo.
**Alternatives Rejected:** 1. construir agora e reconciliar depois — rejeitada porque a `MANIFEST.txt`, o curador e os
testes de texto colidiriam.
**Consequences:** um rebase com 2 conflitos de acréscimo; ganha-se o tempo do build enquanto a F24 publica.

---

## File Manifest

| # | File | Action | Purpose | Agent | Dependencies |
|---|------|--------|---------|-------|--------------|
| 1 | `sdd/config.example.yaml` | Modify | mapa `papeis:` (5 slots + `serie_cmd`) com o porquê, sem nome de modelo | (general) | None |
| 2 | `sdd/bin/sdd-fluxo.sh` | Modify | verbo `modelo`; linha do modelo no `despachar`; cenários no `--self-test` | (general) | 1 |
| 3 | `sdd/bin/custo-feature.sh` | Modify | marcas `papel-*` em sub-linhas fora do total; modo `--execucao` | (general) | None |
| 4 | `sdd/bin/papel-serie.sh` | Create | executor das séries: cópia, teto e trava, fronteira, retomada, custo por execução | (general) | 1, 3 |
| 5 | `sdd/bin/papel-medir.sh` | Create | medidor: pontua, junta repetições, escolhe ou diz por que não | (general) | 4 |
| 6 | `.agents/skills/sdd-build/references/contexto-fresco.md` | Modify | seção "Modelo do papel e marca de papel" | (general) | 2 |
| 7 | `.agents/skills/sdd-build/SKILL.md` | Modify | versão nova (o `contexto-fresco.md` é desta skill) | (general) | 6 |
| 8 | `sdd/templates/fragments/MARCA_FASE.md` | Modify | parágrafo da marca de papel | (general) | 3 |
| 9 | `docs/model-per-role.md` | Create | método: slot, gabarito, série, medidor, teto, limite da fronteira | (general) | 4, 5 |
| 10 | `docs/pt-BR/model-per-role.md` | Create | mesmo conteúdo em português | (general) | 9 |
| 11 | `docs/adversarial-review.md` | Modify | seção do `custo-feature`: sub-linhas de papel e `--execucao` | (general) | 3 |
| 12 | `docs/pt-BR/adversarial-review.md` | Modify | idem em português | (general) | 11 |
| 13 | `docs/cli-conventions.md` | Modify | exits de `papel-serie.sh`, `papel-medir.sh` e do verbo `modelo` | (general) | 2, 4, 5 |
| 14 | `sdd/fixtures/f23b2/` | Create | gabaritos e séries sintéticas, sessões só com números, agente falso | (general) | None |
| 15 | `tests/test_f23b2_papeis.py` | Create | AT-001 a AT-011 com fixtures e agente falso | (general) | 2, 3, 4, 5, 14 |
| 16 | `MANIFEST.txt` | Modify | arquivos novos (scripts, docs, fixtures, teste) | (general) | 4, 5, 9, 10, 14, 15 |

**Total Files:** 16

---

## Landmines aplicáveis

| Landmine (⛔) | Fonte | Veredito | Como / Por quê |
|---------------|-------|----------|----------------|
| Gate que só confere fiação | LM-001 | ✔ tratado | os testes executam `papel-serie.sh` e `papel-medir.sh` com fixtures dos dois lados; mutante que tira a checagem do teto e outro que soma a sub-linha no total |
| Asserção sem baseline vermelho | LM-002 | ✔ tratado | o módulo novo roda contra a árvore antes da mudança (falha por falta dos scripts e do verbo) e o log vai para a evidência |
| Review revisando o vazio | LM-003 | ✔ tratado | commit antes de cada revisão; `.gitignore` local para os documentos durante a revisão |
| Heurística sobre texto livre | LM-005 | ✔ tratado | Decision 7: tabela lida pela coluna e lista fechada de palavras; o custo vem de uma função só (Decision 6); a série de referência cai se o pontuador ler errado |
| Script que só roda com `.git` | LM-006 | ✔ tratado | `papel-serie.sh` exige git (usa `git archive`) e diz isso com 64; o teste do medidor roda numa cópia sem `.git`; gate por `git archive` |
| Mutante que apaga o conserto | LM-009 | ✔ tratado | mutantes aplicados numa cópia de `git archive`, nunca por `git checkout` |
| Engine paga que estoura o teto | LM-010 | ✔ tratado | teto pago 0 nesta frente; `--teto-s` por execução; a parada grava o acumulado |
| Prova de comportamento sem série antiga | LM-011 | ✔ tratado | a referência roda primeiro e, fora da meta, para a escolha (exit 3) |
| Número longo no pacote | LM-012 | ✔ tratado | fixtures com prefixos curtos de hash e tokens pequenos; `publish-gate` no gate |
| Corte de teste por âncora | LM-013 | N.A. | arquivo de teste novo; nenhum teste existente é cortado |
| `text=True` sem encoding no Windows | LM-014 | ✔ tratado | todo `subprocess` dos testes e dos scripts lê com `encoding="utf-8", errors="replace"` |
| Saída do Python no pipe do Windows | LM-015 | ✔ tratado | os núcleos Python trocam stdout e stderr no início (padrão do `sdd-fluxo.sh`) |
| Vigia de grupo de processos no Windows | LM-016 | ✔ tratado | `--teto-s` usa o `timeout` do `subprocess` do Python; o teste do teto fica pulado por `SEM_SINAL` onde não vale |
| Fallback silencioso | LM-017 | ✔ tratado | slot vazio sai como hoje, sem linha (AT-001); slot preenchido num agente que não deixa escolher o modelo diz isso em 1 linha, nunca em silêncio |
| `PIPESTATUS` no zsh | LM-018 | ✔ tratado | evidências gravadas por script `bash` com `rc=$?` e `[exit=N]` |
| Desacordo sobre ferramenta decidido por palavra | LM-021 | ✔ tratado | achado da revisão sobre git ou sessão se decide medindo num repositório temporário |
| Comparação contra a própria fonte | LM-024 | N.A. | o slot não é comparado com outra fonte |
| Juiz por regex | LM-028 | ✔ tratado | o medidor não julga prosa: lê bloco estruturado; a calibração é a série de referência |
| `bash` pelo nome no Windows | LM-029 | ✔ tratado | o executor chama o comando pelo bash que o roda (`SDD_PAPEL_SERIE_BASH="${BASH:-bash}"`) |
| Executor de teste com `PYTHONIOENCODING` | LM-030 | ✔ tratado | testes pelo `Sandbox` de `tests/apoio.py` |
| Testes de tempo em paralelo | LM-031 | ✔ tratado | o teste do `--teto-s` roda em série no módulo |
| Saída do git com cor | LM-033 | ✔ tratado | o executor chama o git com `-c color.ui=never` |
| Skill do starter cita `sdd/bin/` | LM-035 | N.A. | o `contexto-fresco.md` não vai para o starter (build sai do modo web); `test_gerar_starter` roda antes do gate mesmo assim |
| `usage` repetido | LM-036 | ✔ tratado | o custo por execução reusa os leitores da B1 (Decision 6) |
| Arquivo novo fora do `MANIFEST.txt` | LM-037 | ✔ tratado | item 16 no mesmo commit; `publish-gate` numa cópia de `git archive` antes do gate |
| Teto de 500 linhas de `SKILL.md` | LM-038 | ✔ tratado | nenhuma `SKILL.md` ganha texto, só a versão da `sdd-build`; `test_conversa` antes do gate |

Varredura rodada em 2026-11-16 (`playbook-lint.sh --grep` por: sdd-fluxo, despachar, custo-feature, marca-fase,
config.example, contexto-fresco, playbook-curator, teto, subprocess, slot, MANIFEST, starter, Windows, timeout, git
archive, mutante, regex, juiz, usage, heurística, PYTHONIOENCODING, evidência, sabotagem, fallback, CreateProcess,
color.ui), entradas inteiras lidas.

---

## Contrato de aceite

N.A. (1 camada): o projeto não declara `layers:` e a fatia é toda de scripts do método; o avaliador de veredito
segue a regra do `require_avaliacao_layers`.

---

## Agent Assignment Rationale

| Agent | Files Assigned | Why This Agent |
|-------|----------------|----------------|
| (general) | 1–16 | o projeto não tem agentes especialistas; o build roda direto |

---

## Code Patterns

### Pattern 1: verbo `modelo` (núcleo Python do `sdd-fluxo.sh`)

```python
PAPEIS = {"curador": "curador", "avaliador": "avaliador", "revisao_design": "revisao_design",
          "revisor-design": "revisao_design", "cartografo": "cartografo",
          "executor": "executor", "executor-drive": "executor"}
MODELO_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:/-]{0,79}\Z")   # R7: nunca começa por "-"

def cmd_modelo():
    if len(args) != 1 or args[0] not in PAPEIS:
        erro_uso("modelo exige um papel: " + ", ".join(sorted(set(PAPEIS))))
    chave = PAPEIS[args[0]]
    v = slot(os.path.join(raiz_de(os.getcwd()), "sdd/config.yaml"), "papeis", chave)
    if not v:
        print("")
        return 0
    if not MODELO_RE.match(v):
        erro_uso("papeis.%s inválido (começa por letra ou número; depois letras, números e . _ : / -; até 80)" % chave,
                 "corrija papeis.%s em sdd/config.yaml; nada foi despachado." % chave)
    print(v)
    return 0
```

### Pattern 2: linha do modelo no `despachar` (bash)

```bash
case "$papel" in
  avaliador|curador|cartografo|revisor-design|executor-drive)
    mod="$(nucleo modelo "$papel")" || exit 64 ;;
  *) mod="" ;;
esac
# … depois do "**Passos:**":
[ -n "$mod" ] && printf '**Modelo:** abra a sessão nova com o modelo %s (papeis do sdd/config.yaml).\n' "$mod"
```

### Pattern 3: marcas de papel separadas no `custo-feature.sh`

```python
fases = [m for m in marcas if not m[3].startswith("papel-")]
papeis = [m for m in marcas if m[3].startswith("papel-")]
ivs, janela = intervalos(fases, fim_sessoes)
ivs_papel = {}
for nome in sorted({m[3] for m in papeis}):
    ivs_papel[nome] = intervalos([m for m in papeis if m[3] == nome], fim_sessoes)[0]
# na volta das mensagens: além da fase, cada janela de papel que contém m["t"] soma na sub-linha
# (contas_papel[nome]) e guarda m["modelo"] em modelos_papel[nome]; o total NÃO soma contas_papel.
```

### Pattern 4: trava antes de cada chamada (`papel-serie.sh`, núcleo Python)

```python
def pode_chamar(cand, acum, estimativa, teto_pago, teto_nominal):
    """(True, "") ou (False, motivo). Decimal em tudo; acum["*_nd"] > 0 = acumulado desconhecido."""
    if cand["cobranca"] == "desconhecida":
        return False, "cobrança desconhecida: o gasto não tem como ser conferido"
    if cand["cobranca"] == "pay-per-token" and teto_pago == 0:
        return False, "candidato pay-per-token com teto pago zero"
    if acum["nominal_nd"] or acum["pago_nd"]:
        return False, "acumulado com n/d: o teto não se confere"
    if acum["nominal"] + estimativa > teto_nominal:
        return False, "nominal %s + %s passaria do teto %s" % (acum["nominal"], estimativa, teto_nominal)
    pago_prox = estimativa if cand["cobranca"] == "pay-per-token" else Decimal(0)
    if acum["pago"] + pago_prox > teto_pago:
        return False, "pago %s + %s passaria do teto %s" % (acum["pago"], pago_prox, teto_pago)
    return True, ""
```

### Pattern 5: escolha no `papel-medir.sh`

```python
if os.path.isfile(os.path.join(serie, "PARADA.txt")) or faltando or any(e["invalida"] for s in series.values() for e in s):
    return 4, "PARCIAL"                                  # R2: parcial antes de qualquer outro diagnóstico
ref = series[candidatos[0]["id"]]
if not ref or not all(e["na_meta"] for e in ref):
    return 3, "REFERÊNCIA FORA DA META"
med_ref = mediana([e["nominal"] for e in ref])
ok = [c for c in candidatos[1:] if series[c["id"]] and all(e["na_meta"] for e in series[c["id"]])
      and all(e["nominal"] is not None for e in series[c["id"]])]
melhor = min(ok, key=lambda c: (mediana([e["nominal"] for e in series[c["id"]]]), c["id"]), default=None)
if melhor and mediana(...) <= med_ref * (1 - Decimal(limiar) / 100):
    return 0, "ESCOLHIDO: " + melhor["id"]
return 1, "SEM GANHO MEDIDO"
```

---

## Data Flow

```text
1. Despacho de um papel numa feature
   skill → contexto-fresco.md → marca inicio papel-X → sdd-fluxo.sh modelo X → subagente(modelo) | despachar
         → volta do bloco → marca fim papel-X → (release) custo-feature.sh → CUSTO_<F>.md com "↳ papel X"

2. Medição de um papel
   gabarito/<caso>/ + serie.txt + candidatos.tsv
     → papel-serie.sh: para cada (caso, candidato, rep) sem meta.txt:
          pode_chamar? → cópia → snapshot → bash -c serie_cmd → snapshot/comparar → custo-feature --execucao
          → execucoes/.../{saida.txt, meta.txt}  (ou PARADA.txt e exit 20/21)
     → papel-medir.sh → MEDICAO (stdout ou --saida) e exit 0/1/3/4
```

---

## Integration Points

| Sistema | Como | Falha |
|---|---|---|
| `sdd/config.yaml` | `slot()` do `sdd-fluxo.sh` | ausente ⇒ vazio (como hoje) |
| Registro local do agente | leitores `sdd/bin/adapters/sessao-*.py` via `custo-feature.sh --execucao` | sem registro ⇒ n/d, e a série para no próximo teto |
| `governanca-fronteira.sh` | `--snapshot`/`--comparar` | ≠ 0 ⇒ execução inválida, série para |
| `playbook-curator.sh --aplicar` | pontuador do curador | ≠ 0 ⇒ execução fora da meta |
| Agente (via `serie_cmd`) | `bash -c` na cópia | exit ≠ 0 ou passou do `--teto-s` ⇒ execução gravada com `rc` e fora da meta (o custo conta) |

---

## Testing Strategy

| Tipo | Escopo | Ferramenta | Meta |
|---|---|---|---|
| unit/integração | AT-001, AT-002: `modelo` com slot vazio, válido, inválido (espaço, aspas, 81 caracteres, `;`), papel desconhecido; `despachar` com e sem linha de modelo e com 64 antes de gravar o brief | `tests/test_f23b2_papeis.py` + `sdd/fixtures/f23b2/config/` | exit e texto exatos |
| integração | AT-003: trace com marcas de fase e de papel aninhadas, sessões sintéticas com 2 modelos; total = fases + revisão; sub-linha com os modelos; marca de papel sem par em "Fora da conta"; mutante que soma a sub-linha no total cai | idem + `sdd/fixtures/f23b2/sessoes/` | total exato em Decimal |
| integração | AT-004: blocos do curador (igual ao esperado; contagem a mais; ADD faltando; delta que o `--aplicar` recusa; sem bloco) | idem + `sdd/fixtures/f23b2/serie-curador/` | dentro/fora da meta por execução |
| integração | AT-005: blocos do avaliador (igual; veredito diferente; AT FAIL dado como PASS com o resto igual; AT ausente; palavra fora da lista) | idem + `serie-avaliador/` | idem |
| integração | AT-006, AT-007: séries com vencedor, sem ganho (< 30%), referência fora da meta, candidato n/d mais barato | idem | exit 0/1/3 e o id |
| integração | AT-008, AT-009: agente falso que grava a chamada; teto pago 0 com candidato pay-per-token (0 chamadas); teto nominal atingido no meio (PARADA.txt, exit 20); 2 séries na mesma pasta de medição somando para o mesmo teto (R1); retomada (só as que faltam, acumulado igual, `PARADA.txt` antigo movido, R6); execução interrompida com `inicio.txt` somada antes de refazer (R4); referência fora da meta ⇒ exit 22 com 0 chamadas de candidato (N1); medidor com série parada ou execução inválida ⇒ exit 4 antes do 3 (R2); candidato sem execução não vence; modelo do `candidatos.tsv` com `-` inicial ou espaço ⇒ 64 (R10) | idem + `sdd/fixtures/f23b2/agente-falso.sh` | contagem exata de chamadas |
| integração | R5: agente falso honesto (grava só na cópia) ⇒ execução válida, sem `FORA:` pela escrita da própria série | idem | exit 0 |
| integração | AT-011: agente falso que grava no projeto e outro que acrescenta remoto ⇒ inválida, exit 21, caminhos no PARADA.txt, nada apagado | idem | idem |
| guarda | AT-010: nome de modelo nos arquivos desta fatia (com mutante); `MANIFEST.txt` pelo `publish-gate`; suíte inteira, `test_gerar_starter`, `test_conversa`, `test_bash32` | Verify Gate | exit 0 |
| prova real | Success Criteria: séries do curador e do avaliador, fora do gate | `papel-serie.sh` + `papel-medir.sh` | relatório na evidência |

Baseline vermelho: o módulo novo roda contra `origin/main` antes do 1º commit de código e o log vai para
`sdd/reports/evidence/F23B2_MODELO_POR_PAPEL/BASELINE-VERMELHO.log`.

---

## Error Handling

| Erro | Tratamento | Exit |
|---|---|---|
| slot inválido | mensagem com a chave e o motivo, sem o valor | 64 (`modelo`, `despachar`) |
| série sem `serie.txt`, `candidatos.tsv` vazio, repetições < 1, teto não decimal, gabarito sem caso do papel | `RESULTADO: ERRO DE USO` + `→` | 64 |
| sem comando (`--cmd` e `papeis.serie_cmd` vazios) | diz onde configurar; nada roda | 64 |
| fora do git (sem `git archive`) | diz que a série precisa de um repositório | 64 |
| teto (pago, nominal, n/d, cobrança), somado em toda a pasta de medição | `PARADA.txt`, `RESULTADO: PARADO PELO TETO` | 20 |
| referência fora da meta antes dos candidatos | `PARADA.txt`, `RESULTADO: REFERÊNCIA FORA DA META` (nenhum candidato chamado) | 22 |
| execução interrompida (tem `inicio.txt`, sem `meta.txt`) | na retomada, custo medido e somado como `interrompida`, depois refeita | — |
| modelo do `candidatos.tsv` fora da regex do slot | `RESULTADO: ERRO DE USO`, nada roda | 64 |
| fronteira ou remoto | execução `invalida`, `PARADA.txt` com os caminhos, `RESULTADO: FRONTEIRA` | 21 |
| agente sai ≠ 0 ou passa do `--teto-s` | execução gravada com `rc`, conta no custo, fora da meta; a série segue | — |
| medidor: referência fora da meta / parcial / sem ganho | `RESULTADO:` + `→` | 3 / 4 / 1 |

---

## Configuration

| Chave | Tipo | Vazio | Lida por |
|---|---|---|---|
| `papeis.curador` · `avaliador` · `revisao_design` · `cartografo` · `executor` | texto opaco, `[A-Za-z0-9._:/-]{1,80}` | modelo da sessão | `sdd-fluxo.sh modelo` |
| `papeis.serie_cmd` | comando de 1 linha (`bash -c`, na cópia) | `papel-serie.sh` exige `--cmd` | `papel-serie.sh` |

---

## Segurança

1. **Onde mora cada segredo:** nenhum segredo novo. O comando da série usa a credencial que o agente já tem
   (assinatura); o pacote não lê nem grava credencial.
2. **Quem vê e quem muda cada tabela:** não há banco. O gabarito e as séries são arquivos da branch de documentos
   (públicos no Open): o `meta.txt` guarda só números e nomes de modelo; a `saida.txt` guarda o bloco do papel sobre o
   histórico já público do Open. Num projeto do aluno com dado de cliente, a série grava a saída do papel: o
   `docs/model-per-role.md` diz para manter a pasta da série fora do git quando o caso tiver dado de terceiros.
3. **Credencial de cada agente ou integração:** o agente da série roda com a credencial da sessão do usuário, numa
   cópia isolada sem remoto (não consegue publicar), com teto de gasto e de tempo; o desligamento é o `PARADA.txt`/
   Ctrl-C (a execução interrompida não grava `meta.txt` e é refeita na retomada).
4. **Cabeçalhos e CORS do host:** N.A. — não há host.
5. **Itens aplicados no Define:** S20 — cada execução da série tem permissão mínima (só a cópia do caso, sem remoto,
   conferida pela fronteira do projeto antes e depois), teto de gasto pago e nominal checado antes de cada chamada
   (cobrança desconhecida nunca roda), teto de tempo por execução, e o interruptor documentado (`PARADA.txt`,
   retomada pelo mesmo comando). O comando local desta frente roda o agente com caixa de areia de escrita na pasta
   da cópia, nunca com as permissões desligadas.

---

## Observability

- `custo-feature.sh`: sub-linhas `↳ papel <nome> · <modelos>` e marcas de papel sem par em "Fora da conta".
- `papel-serie.sh`: 1 linha por execução (`caso · candidato · rep · rc · nominal · acumulado`), `PARADA.txt` com
  motivo e acumulados, `meta.txt` por execução.
- `papel-medir.sh`: tabela por candidato (execuções na meta / total, mediana do nominal, queda contra a referência),
  linha por execução fora da meta com o motivo, e o `RESULTADO:`.

---

## Advisor Ledger

| # | Fonte | Achado | Decisão |
|---|---|---|---|
| R1 | D1 · claude (auditor AGREE) | teto nominal por série, e o DEFINE fixa o da frente | APLICADA — `teto.txt` na pasta de medição, acumulado de todas as séries (Decision 4) |
| R2 | D1 · claude (auditor DISAGREE_CONCERN) | precedência parcial × referência; `all()` vazio | APLICADA — ordem fixa (parcial, referência, candidatos), candidato sem execução fora (Decision 7, Pattern 5) |
| R3 | D1 · claude (auditor DISAGREE_CONCERN) | `--aplicar` poderia gravar no gabarito | REBATIDA_EVIDENCIA — `sdd/bin/playbook-curator.sh:13` (stdout = playbook novo) e `:800-815` (só lê); a frase de que o gabarito nunca é escrito entrou na Decision 7 |
| R4 | D1 · claude (auditor AGREE) | gasto da execução interrompida some do acumulado | APLICADA — `inicio.txt` antes de chamar; na retomada, custo medido e somado (Decision 4) |
| R5 | D1 · claude (auditor DISAGREE_CONCERN) | a série grava no projeto entre os snapshots | APLICADA — saída em arquivo temporário, movida depois do `--comparar` (Decision 5) |
| R6 | D1 · claude (auditor DISAGREE_CONCERN) | `PARADA.txt` antigo deixaria PARCIAL para sempre | APLICADA — a retomada move para `paradas/` (Decision 4) |
| R7 | D1 · claude (auditor DISAGREE_CONCERN) | valor do slot começando por `-` vira opção | APLICADA — regex começa por letra ou número (Decision 1, Pattern 1; DEFINE AT-002 v1.2) |
| R8 | D1 · claude (auditor AGREE) | linha do LM-017 contrariava o AT-001 | APLICADA — slot vazio sai como hoje, sem linha |
| R9 | D1 · claude (auditor AGREE) | sub-linha sem contagem de execuções | APLICADA — Execuções = janelas do papel (Decision 3) |
| R10 | D1 · claude (auditor DISAGREE_CONCERN) | modelo do `candidatos.tsv` sem validação | APLICADA — mesma regex do slot; docs com `"$SDD_MODELO"` entre aspas (Decision 4) |
| R11 | D1 · claude (auditor DISAGREE_CONCERN) | `/var` × `/private/var` no macOS | REBATIDA_EVIDENCIA — `sdd/bin/adapters/sessao-claude.py:60-61` e `sdd/bin/adapters/sessao-codex.py:68` já usam `realpath` |
| N1 | D1 · codex (auditor, novo) | candidatos rodam antes de a referência ser julgada | APLICADA — toda a referência primeiro, `papel-medir.sh --so-referencia`, exit 22 sem chamar candidato (Decision 4) |

Revisão D1: `sdd/reports/reviews/EXTERNAL_REVIEW_20261116-205900` (claude revisa, codex audita, diversidade vendor,
2º revisor sem gatilho de risco, US$ 0,90 + assinatura).

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-11-16 | design-agent | 10 decisões, 16 arquivos; [auto] em todas as escolhas técnicas (abaixo) |
| 1.1 | 2026-11-16 | design-agent | Revisão D1: 10 achados aplicados (R1, R2, R4–R10, N1) e 2 rebatidos com evidência (R3, R11); DEFINE v1.2 (AT-002) |
| 1.2 | 2026-11-17 | build-agent | Decision 4 sem `--casos` (R2 da rodada 3 da revisão do código) |

Decisões automáticas desta fase:
- [auto] slot lido por `sdd-fluxo.sh modelo`, com regex estrita — porque um leitor só serve despacho e subagente · para desfazer: Decision 1.
- [auto] despacho e marcas de papel só no `contexto-fresco.md` — porque cobre os 5 papéis sem tocar a `sdd-release` (500 linhas, reescrita pela F24) · para desfazer: uma linha por skill.
- [auto] custo por papel em sub-linhas fora do total — porque mantém a regra das fases e a linha de base da B1 · para desfazer: papel como fase própria.
- [auto] executor das séries com comando do projeto e trava em código — porque é vendor-agnóstico e a trava não fica em prosa · para desfazer: Decision 4.
- [auto] medidor sem juiz de prosa, calibrado pela referência — porque os papéis devolvem bloco estruturado · para desfazer: juiz em contexto novo por execução.
- [auto] guarda de nome de modelo só nos arquivos desta fatia — porque o pacote já tem nomes em arquivos antigos · para desfazer: padrão no `publish-gate-patterns.txt` e limpeza dos antigos.
- [auto] build começa já, e o gate, a suíte inteira e as séries reais só depois da F24 na `main` — porque a F24 não muda o bloco do curador nem o `--aplicar` e só cruza 2 arquivos de acréscimo, mas a suíte em paralelo com o gate dela derrubaria testes de tempo · para desfazer: esperar a F24 antes do 1º commit.
- [auto] `--casos` sai da Decision 4 (v1.2) — porque a barreira de calibração exige a referência inteira antes de qualquer candidato, e a retomada já cobre o caso longo do avaliador (A-004) · para desfazer: implementar o filtro e a barreira por caso.
- [auto] LLM Prompts continua `false` (re-check: o executor manda o brief do caso sem mudança; "prompt" aparece só como brief) — para desfazer: virar `true` se um brief mudar.

---

## Next Step

**Ready for:** revisão do DESIGN (exigida: 3 ou mais arquivos novos), depois `/sdd-build sdd/features/DESIGN_F23B2_MODELO_POR_PAPEL.md` quando a F24 estiver na `main`.
