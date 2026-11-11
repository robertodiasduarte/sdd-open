---
name: sdd-define
description: Fase 1 do SDD Open — transforma um brainstorm, notas ou pedido direto em especificação com testes de aceitação em EARS, protocolo de ambiguidade (NEEDS CLARIFICATION) e um Verify Gate executável, gravando sdd/features/DEFINE_{FEATURE}.md. Use quando o usuário pedir para especificar, definir requisitos, escrever a spec, ou disser /sdd-define.
compatibility: Requer bash >= 3.2 e git >= 2.20; roda sdd/bin/verify-gate.sh --print para validar o bloco do gate.
license: MIT
metadata:
  author: Roberto Dias Duarte
  version: "2.6.0"
  updated: "2026-11"
  fase: "1"
---

# sdd-define — Fase 1

Na primeira resposta desta skill, comece com esta linha, uma vez só, antes do Status:
`sdd-define v2.6.0 · nov/2026 · versão atual: https://github.com/robertodiasduarte/sdd-open/releases/latest`

Capturar requisitos e validá-los numa passada só. O DEFINE é o **contrato**: tudo que vem
depois (design, build, release) é julgado contra ele. Por isso ele sai com um **Verify Gate
executável** — um comando com exit code, não prosa.

## Como falar com o aluno

Leia `references/como-falar.md` antes da primeira resposta: o glossário desta skill, o Status preenchido
e um exemplo completo. Pergunta e parada seguem `sdd/templates/fragments/PERGUNTA_DECISAO.md`.
Quem usa esta skill, em geral, nunca usou git nem terminal.

| Etapa | Nome para o aluno | Passos desta skill |
|---|---|---|
| 1 | Ler o brainstorm | 1, 1.5 e 2 |
| 2 | Requisitos | 3 |
| 3 | Testes de aceitação | 4 e 5 |
| 4 | Perguntas | 6 e 7 |
| 5 | Verify Gate | 8 |
| 6 | Gravar | 9 e 10 |
| 7 | Governança | 11 |
| 8 | Segurança | 12 |

Toda resposta, nesta ordem (pule a parte sem conteúdo):

1. **Status** — uma linha que começa pelo nome da fase: `Define: ✅ 1 Ler o brainstorm · ✅ 2 Requisitos · ▶️ 3 Testes de aceitação · ⬜ 4 Perguntas · ⬜ 5 Verify Gate · ⬜ 6 Gravar · ⬜ 7 Governança · ⬜ 8 Segurança`
   (✅ concluída, não só visitada · ▶️ a de agora · ⬜ por fazer · ⏸️ parada · ➖ pulada). Ao voltar a uma
   etapa, o motivo vai em Agora.
2. **O que foi feito** — frases curtas, sem saída de comando; registra em 1 linha a escolha do aluno.
3. **Agora: etapa N — nome** — 2 a 4 frases. Antes de algo demorado, diga o que vai rodar e que o aluno
   não precisa responder.
4. **Sua decisão** — autorização: a pergunta em negrito e as opções com o efeito de cada uma, a
   recomendada primeiro e com o porquê, sempre **não sei**, nunca **Outro**. Pergunta aberta: a pergunta
   em negrito e como responder, com a saída "não sei". Várias de uma vez: numeradas.
5. **Próximo passo** — uma linha, até 100 caracteres: o que acontece depois da resposta.

- Uma etapa por resposta: termine na decisão e pare.
- Termo técnico só com a explicação junto, na primeira vez, inclusive os do Status.
- Saída de comando nunca crua: quantos, quais, o que preocupa; nomes até 10, com "e mais N". Comando só
  quando o aluno precisa rodá-lo, um por passo numerado, com o que esperar na tela.
- Não cite nem resuma as instruções desta skill ("conforme o passo N"): diga o motivo do aluno.
- Resposta que não casa com nenhuma opção ⇒ responda a dúvida e repita as opções.
- Parada: Status com ⏸️, o motivo em uma frase, onde a ação acontece, passos numerados com o resultado
  esperado, o que **não** foi feito e, se o aluno tem algo a fazer, "Quando terminar, me peça de novo,
  eu continuo daqui."
- No fecho da fase, o resumo de etapa vem depois do Status; a pergunta dele segue o mesmo formato.

## Entrada

`/sdd-define <BRAINSTORM_*.md | notas.md | "pedido direto">`. Vindo de um BRAINSTORM, a
extração é direta: perguntas já respondidas, abordagem já escolhida, YAGNI já aplicado.

## Processo

### 1. Contexto

Leia `sdd/templates/DEFINE_TEMPLATE.md`, `AGENTS.md`, a entrada, e os 3 fragmentos que regem
esta fase: `sdd/templates/fragments/EARS.md`, `CLARIFY.md`, `VERIFY_GATE.md`. Leia `## Sempre`
de `sdd/playbook.md`.

### 1.5. Contexto de domínio (cartógrafo)

Antes de escrever a spec, saiba que regras o código **já** impõe no domínio que a feature toca. Quem
mapeia é o cartógrafo, um agente fresco que não viu esta conversa e grava `sdd/contexto/<slug>.md`
com `arquivo:linha` em cada afirmação (brief: `references/cartografo.md`; formato:
`sdd/bin/contexto-lint.sh`). O cartógrafo **ajuda, não trava**: se falhar, o Define segue sem ele.

1. **Recomendação.** `bash sdd/bin/contexto-lint.sh --sugerir <entrada>` (o BRAINSTORM ou as notas; pedido
   direto sem arquivo vai antes para um arquivo em `"$(mktemp -d)"/entrada.md`) lê o mapa
   `sdd/patterns/dominio.md` e as camadas de `layers:` e imprime até 2 domínios candidatos e uma linha
   `recomendacao: gerar | reusar | pular (<motivo>)`. Aplique como decisão `[auto · de rotina]` (com o
   encadeamento ligado, vai para o recibo "Decidi sozinho" com o sinal e como desfazer):

   **Sua decisão** — [auto · de rotina] **Mapeio as regras do domínio de pedidos antes de escrever a spec?**
   - **gerar o mapa agora** (recomendado) — um agente novo lê o código de pedidos e anota as regras que
     já valem, com o arquivo e a linha; leva alguns minutos e não muda nada no código.
   - **seguir sem o mapa** — o Define fica mais rápido, mas pode repetir ou contrariar uma regra que o
     código já tem.
   - **não sei** — explico com um exemplo de regra que o mapa acharia.
2. **pular** ⇒ uma linha ao aluno: `🗺️ contexto: pulado — <motivo em palavras>. Sem problema: o Define
   segue.` Sem mapa de domínios, acrescente: `Para ter o mapa, veja sdd/patterns/README.md.` No DEFINE:
   `CONTEXTO de domínio` = `nenhum (pulado: <motivo>)`.
3. **reusar** ⇒ `bash sdd/bin/contexto-lint.sh --validade sdd/contexto/<slug>.md`: 0 ⇒
   `✅ contexto: reusando sdd/contexto/<slug>.md (nada mudou desde <data>)`; 1 ⇒ `⚠️ contexto: venceu
   (<n> arquivos mudaram)` e ofereça gerar.
4. **gerar** ⇒ imprima `🗺️ contexto: mapeando ctx:<slug> em contexto fresco (alguns minutos)` e:
   1. no degrau sem subagente, grave **antes** o brief em `sdd/reports/briefs/BRIEF_cartografo_<F>.md` (gravado
      depois do snapshot, ele apareceria como escrita fora do permitido); depois
      `T="${TMPDIR:-/tmp}/sdd-fronteira-$(git rev-parse --show-toplevel | git hash-object --stdin | cut -c1-12)/<F>/cartografo-<slug>"; mkdir -p "$T"`
      (na pasta temporária, fora do projeto e gravável mesmo em agente com sandbox; o nome vem da raiz do projeto,
      então uma sessão nova o refaz igual depois de uma parada) e `bash sdd/bin/governanca-fronteira.sh --snapshot <raiz> "$T/antes" <raiz>/sdd/contexto/<slug>.md`
      imediatamente antes do despacho;
   2. despache pela escada de `sdd-build/references/contexto-fresco.md` com **só** os 4 campos
      `ctx: ctx:<slug> · saida: sdd/contexto/<slug>.md · worktree: <raiz> · dominio: sdd/patterns/dominio.md`
      e o brief `references/cartografo.md` (nada do pedido, nada desta conversa). Sem subagente, com o
      brief já gravado no item 1, rode
      `bash sdd/bin/sdd-fluxo.sh despachar cartografo <F> sdd/reports/briefs/BRIEF_cartografo_<F>.md` e pare
      no exit 40 repassando a parada; quando as duas paradas deste Define vão acontecer, escreva antes
      `⏸️ parada 1 de 2 deste Define (o cartógrafo); a 2ª é a revisão de governança.`;
   3. logo que o bloco `<<<CONTEXTO … >>>` voltar, **sem editar nada no meio**: `--snapshot … "$T/depois"`
      e `bash sdd/bin/governanca-fronteira.sh --comparar "$T/antes" "$T/depois" <raiz>/sdd/contexto/<slug>.md`;
      depois `bash sdd/bin/contexto-lint.sh sdd/contexto/<slug>.md`;
   4. falha = `--comparar` ≠ 0, lint ≠ 0 ou bloco ilegível. `FORA:` ⇒ liste os caminhos, não apague
      nada. **1 redespacho** fresco, com a saída do lint como 5º campo `lint:` (o único extra que o brief aceita
      sem marcar contaminação), **refazendo antes** o brief (sem subagente) e o
      snapshot de antes (o que ficou da 1ª tentativa não pode condenar a 2ª); 2ª falha ⇒
      `⚠️ contexto: o mapa não ficou válido (<motivo em palavras>); o Define segue sem ele.` e
      `nenhum (<motivo>)`.
5. **Preencha** a linha `CONTEXTO de domínio` do Technical Context:
   `contexto/<slug>.md · sha <7 hex> · válido em <AAAA-MM-DD>` ou `nenhum (<motivo>)`. O que o CONTEXTO
   diz em `## Regras vigentes` entra nos ATs e nas Constraints como **regra existente**, não como suposição.
6. **No máximo 2 domínios por feature**, um despacho por vez (o 2º só depois que a fronteira do 1º
   fechou: em paralelo, um cartógrafo veria o arquivo do outro como escrita fora do permitido). Mais que
   isso é sinal de feature grande: proponha dividir.

### 2. Classificar a entrada

| Tipo | Foco |
|---|---|
| BRAINSTORM | extrair direto; validado |
| notas de reunião | decisões e requisitos |
| conversa / pedido direto | problema central, usuários |
| fontes mistas | consolidar, deduplicar |

### 3. Extrair

Problema · Usuários (com a dor de cada um) · Objetivos (MUST/SHOULD/COULD) · Critérios de
sucesso (com números) · Testes de aceitação · Restrições · Fora de escopo.

**KB Domains** (Technical Context): só nomes de `ls sdd/kb/` (as pastas; o `_index.yaml` não conta) ou
`nenhum`, conferidos de novo a cada Define. Sem `sdd/kb/`, escreva `nenhum` e diga ao aluno, em 1 frase,
que a `sdd-kb` cria uma base. Ao mostrar um domínio pela 1ª vez, ponha ao lado o `name:` dele no
`sdd/kb/_index.yaml`.

### 4. Testes de aceitação em EARS (obrigatório)

Reescreva cada AT na gramática de `fragments/EARS.md`: keywords em inglês (**When / While /
If–Then / Where / shall / shall continue to**), corpo na língua do projeto. **Recuse** o DEFINE
(não grave) se:

- algum AT está fora dos padrões (sem keyword);
- há gatilho indesejado plausível (provedor fora, permissão negada, fila cheia) e **nenhum**
  AT If/Then;
- é bugfix e não há ≥1 **shall continue to**;
- há adjetivo sem número ("rápido" → "em <2 s");
- While / If–Then / Where não foram **considerados** (AT presente ou N.A. em 1 linha);
- há mais de ~10 ATs;
- há AT de UX visual (isso é gate `manual-ux`, fora do EARS);
- algum AT está sem `kind` na coluna Gate ou sem cobertura no `cmd` do Verify Gate.

### 5. Clarity Score

Pontue Problema · Usuários · Objetivos · Sucesso · Escopo de 0 a 3. **Mínimo 12/15.** Abaixo
disso, pergunte (múltipla escolha, recomendada primeiro) até fechar as lacunas.

### 6. Clarify — marcar, nunca chutar

Protocolo em `fragments/CLARIFY.md`. Ambiguidade real vira marcador **no lugar exato da
dúvida**, na forma canônica (colchete + NEEDS CLARIFICATION + dois-pontos + pergunta). Varra as
9 categorias (escopo, dados, UX, NFRs, integrações, edge cases, restrições, terminologia,
sinal de conclusão). Resolva por rodadas de ≤5 perguntas; a resposta entra **no corpo** da spec
e no log `## Clarifications / ### Session YYYY-MM-DD`. Enquanto houver marcador ativo,
`sdd/bin/verify-gate.sh` devolve exit **5** e nenhuma fase avança.

### 7. LLM Prompts (flag binário)

A feature cria ou edita prompt que roda em produção (system prompt, classificador, passe de
pipeline)? Sinais: nomes de provedor, "prompt", "embeddings", "RAG", paths `**/prompts/**`,
chamadas `messages.create`/`chat.completions`. Marque `true`/`false` em Technical Context com
justificativa. Nomes de provedor citados como **plataforma-alvo** não contam. Pontue os sinais:

| Sinal | Exemplos | Peso |
|---|---|---|
| forte | provedor ou modelo nomeado como dependência, `messages.create`/`chat.completions`, `**/prompts/**`, "system prompt" | 1 forte → `true` |
| fraco | "prompt", "RAG", "embeddings", "classificar", "resumir", "chatbot" | 2 fracos → `true`; 1 fraco → `true` com a nota "conservador" |
| loop | agente, "até convergir", "a cada resposta", várias chamadas encadeadas | anote "candidato a loop" na justificativa |

### 8. Verify Gate (obrigatório — recuse DEFINE sem gate)

Derive o gate dos ATs e critérios de sucesso, seguindo `fragments/VERIFY_GATE.md`:

| Natureza do aceite | `kind` | `cmd` típico |
|---|---|---|
| lógica testável | `test` | `{{TEST_CMD}} -- <arquivo>.test` |
| rota/HTTP responde | `smoke` | `curl -sS -o /dev/null -w '%{http_code}' <url>` |
| qualidade com limiar | `eval` | limiar embutido no comando |
| tipos/compilação | `typecheck` | `{{TYPECHECK_CMD}}` |
| UX pura | `manual-ux` | `N/A (manual-ux)` + `manual_fallback` = checklist |

Os slots `{{TEST_CMD}}`/`{{TYPECHECK_CMD}}` vêm de `sdd/config.yaml`. Slot vazio: pergunte o
comando real; nunca adivinhe. Valide o bloco:

```bash
sdd/bin/verify-gate.sh --print sdd/features/DEFINE_{FEATURE}.md   # lista kind/cmd/pass_when sem erro 64
```

Anti-padrões a recusar: gate de prosa; `kind: test` com `cmd` vazio; feature de UX marcada
`test` só para "passar técnico".

**Gate composto** (feature com vários ATs automatizáveis): escreva um script
`sdd/bin/gates/gate-{feature}.sh` com **um bloco por AT**, imprimindo `AT-00N ✅/❌`, e aponte
o `cmd` para ele. Toda asserção precisa de **baseline vermelho**: rode contra a árvore antes da
mudança; se já passa, ela não prova nada.

### 9. Gravar

`sdd/features/DEFINE_{FEATURE}.md` com o template preenchido, Status `Ready for Design` (ou
`Ready for UX Review` se há interface), a linha `CONTEXTO de domínio` do passo 1.5 e a linha
`Governança` = `pendente` (o passo 11 escreve a final).

### 10. Conferir o KB Domains

`python3 sdd/bin/kb-dominios.py sdd/features/DEFINE_{FEATURE}.md` sobre o arquivo gravado: o KB Domains
só cita pastas de `sdd/kb/`, ou diz `nenhum`. Exit 0 segue; exit 1 ⇒ corrija o campo e rode de novo antes
de entregar. Os testes que ele listar (`<domínio>: <REGRA> → <teste>`, das regras de uma base normativa)
entram no `cmd` do Verify Gate; se algum não entrar, registre o motivo no DEFINE e rode
`verify-gate.sh --print` de novo.

### 11. Governança (sempre, inclusive com `--parar`)

Num sistema que trata dinheiro, tributo, folha ou dado pessoal, a revisão de governança acha o que a
spec devia exigir antes que o código endureça. Ela roda em **todo** Define (o Step 6.5 do PORTE): sem
tema, o revisor responde N.A. e isso fica registrado. **Quem escreveu o DEFINE não se revisa**: os
passos 1 a 4 da `sdd-governanca` são do revisor, um agente fresco (brief
`.agents/skills/sdd-governanca/references/revisor.md`); as decisões e a aplicação (passos 5 e 6) são
desta sessão. `--parar` desliga o encadeamento, nunca este passo.

1. **Antes de tudo, a trava.** Grave no DEFINE, em `## Clarifications`, uma sessão nova com o marcador
   de governança (colchete + `NEEDS CLARIFICATION` + `: governança não rodou — rode só o passo 11 do
   sdd-define numa sessão nova, ou dispense com motivo`, fora de cerca) e deixe a linha `Governança` =
   `pendente`. Assim, se a sessão parar aqui (exit 40 ou a pessoa fecha a janela), o `verify-gate.sh`
   sai 5 e o build não passa sem a revisão. Com outro marcador de dúvida aberto, espere a resposta e
   rode este passo depois; se o Define terminar com dúvida aberta, a trava fica e a linha diz
   `pendente — clarificação aberta`. A linha `Governança` é **sempre a linha da tabela** do
   `## Technical Context` — `| **Governança** | <valor> | <nota> |` —, a única que o `verify-gate.sh` lê.
2. Imprima `⚖️ governança: revisando em contexto fresco (alguns minutos)`. No degrau sem subagente, grave
   **antes** o brief em `sdd/reports/briefs/BRIEF_revisor-governanca_<F>.md` (depois do snapshot ele
   apareceria como escrita fora do permitido).
   `T="${TMPDIR:-/tmp}/sdd-fronteira-$(git rev-parse --show-toplevel | git hash-object --stdin | cut -c1-12)/<F>/governanca"; mkdir -p "$T"` — na pasta
   temporária, fora do projeto e gravável mesmo em agente com sandbox; o nome vem da raiz do projeto, então uma
   sessão nova que retoma depois da parada (exit 40) o refaz igual e acha o snapshot e a cópia do DEFINE. Se a
   pasta temporária tiver sido limpa, o `--comparar` sai 64 e isso conta como falha: refaça e redespache;
   **Sessão que retoma depois da parada** (o `"$T/antes"` já existe e a volta do revisor ainda não foi
   conferida): recalcule só o `T` e vá para o item 4; refazer a cópia e o snapshot de antes agora tomaria por
   linha de base o que o revisor já escreveu.
   `cp sdd/features/DEFINE_<F>.md "$T/DEFINE.antes"` (o snapshot só guarda o sha: é esta cópia que
   permite restaurar o DEFINE se o revisor o mexer);
   `bash sdd/bin/governanca-fronteira.sh --snapshot <raiz> "$T/antes" <raiz>/sdd/reviews/GOVERNANCA_REVIEW_<F>.md`
   imediatamente antes do despacho.
3. **Despache** pela escada de `sdd-build/references/contexto-fresco.md` com **só** os 5 campos
   absolutos (também no redespacho):
   `define: <raiz>/sdd/features/DEFINE_<F>.md · skill: <raiz>/.agents/skills/sdd-governanca/ · padrao: <raiz>/sdd/GOVERNANCA_PADRAO.md · worktree: <raiz> · saida: <raiz>/sdd/reviews/GOVERNANCA_REVIEW_<F>.md`.
   Sem subagente, com o brief já gravado no item 2, rode
   `bash sdd/bin/sdd-fluxo.sh despachar revisor-governanca <F> sdd/reports/briefs/BRIEF_revisor-governanca_<F>.md`
   e pare no exit 40 (`⏸️ parada 2 de 2 deste Define` quando houve a do cartógrafo). A trava do item 1
   segura o build até o bloco voltar.
4. **Na volta, sem editar nada no meio:** grave a resposta do revisor em `"$T/resposta.txt"`;
   `--snapshot … "$T/depois"`;
   `bash sdd/bin/governanca-fronteira.sh --comparar "$T/antes" "$T/depois" <raiz>/sdd/reviews/GOVERNANCA_REVIEW_<F>.md > "$T/comparar.txt"`;
   e confira o bloco com
   `python3 sdd/bin/governanca-bloco.py "$T/resposta.txt" --saida <raiz>/sdd/reviews/GOVERNANCA_REVIEW_<F>.md --comparar "$T/comparar.txt"`
   (0 bloco válido · 1 `resultado: FALHA` · 2 bloco inválido).
5. **Falha** = `--comparar` ≠ 0 (1 = `FORA:`; 64 = fronteira não verificada) ou `governanca-bloco.py` ≠ 0
   (1 = `resultado: FALHA`; 2 = bloco inválido: sem o par `<<<GOVERNANCA`/`>>>`, `resultado` fora da
   lista, `lacuna:` sem os 3 campos ou sem `muda:`/`porque:`, `relatorio:` diferente do `saida:`, Gnn do
   bloco diferente dos títulos `### Gnn — ` de `## Lacunas`, `REVISADO` sem `MUDOU: <saida>`, ou outro
   resultado com o relatório gravado). Tratamento, **nada destrutivo**: DEFINE em `FORA:` ⇒
   `rm -f sdd/features/DEFINE_<F>.md.restaurando && cp "$T/DEFINE.antes" sdd/features/DEFINE_<F>.md.restaurando && rm -f sdd/features/DEFINE_<F>.md && mv sdd/features/DEFINE_<F>.md.restaurando sdd/features/DEFINE_<F>.md && cmp "$T/DEFINE.antes" sdd/features/DEFINE_<F>.md`,
   recalculando o `T` pela fórmula do item 2 na mesma chamada (variável de shell não passa de uma chamada para
   a outra; com o `T` vazio, a cópia falha primeiro e o DEFINE fica onde está). A cópia vem **antes** do `rm` do DEFINE: se
   ela não for alcançada, nada é apagado. O 1º `rm` tira um link que o agente tenha posto no nome intermediário:
   um `cp` sobre ele escreveria no arquivo para onde ele aponta. O `cmp` no fim confere o resultado. DEFINE trocado por uma pasta ⇒ não apague: mostre à pessoa. (o
   `rm` antes desfaz um link que o agente tenha posto no lugar do DEFINE: um `cp` sobre o link escreveria no
   arquivo para onde ele aponta); outros `FORA:` ⇒ liste, não
   apague; o `saida:` que estava `AUSENTE` no antes ⇒ remova.
   Imprima `↻ governança: a 1ª tentativa falhou (<motivo>); tentando de novo em contexto fresco.`,
   refaça o snapshot de antes e **redespache uma vez**, com os mesmos 5 campos (o motivo fica nesta
   sessão). 2ª falha ⇒ item 9.
6. **`PADRAO_AUSENTE`** (achou tema e o projeto não tem `sdd/GOVERNANCA_PADRAO.md`) ⇒ uma frase:
   `A revisão achou <tema> neste Define e o projeto ainda não tem o padrão de governança; são 5 perguntas,
   uma vez por projeto.` Pergunte os 5 campos do passo 2 da `sdd-governanca`, com a marca
   `[D2 · muda o produto]`, grave o padrão pelo `assets/GOVERNANCA_PADRAO_TEMPLATE.md` dela, **refaça o
   snapshot de antes** (o padrão recém-gravado é escrita desta sessão, não do revisor; sem o snapshot novo ele
   apareceria como `FORA:`) e redespache (não conta como falha). Projeto com revisão N.A. nunca ouve essas perguntas.
7. **`NA`** ⇒ `✅ governança: N.A. — <motivo>` e a linha `| **Governança** | N.A. — <motivo> | revisor fresco, <data> |`.
   Nenhum arquivo.
   **`REVISADO` com 0 lacunas** ⇒ `✅ governança: 0 lacunas — <cobertura>` e item 8 sem perguntas.
8. **`REVISADO` com lacunas** ⇒ `⚖️ governança: <n> lacuna(s) — <n> pergunta(s)` e o caminho do relatório
   (uma vez). **Uma pergunta por lacuna**, em ordem de severidade, no formato do passo 5 da
   `sdd-governanca` (`[D2 · muda o produto]`: aplicar no DEFINE · recusar com motivo · adiar; o AT que
   contradiz o requisito mostrado antes e depois; nunca "aplicar todas"). Depois, o passo 6 da skill,
   por esta sessão: AT contradito reescrito primeiro; AT novo no próximo ID; e, para cada lacuna aplicada
   que tem `prova_script` no catálogo, **este passo é o dono da prova** (o Design só a lista no manifest):
   grave o script adaptado em `sdd/tests/governanca/<F>_<Gnn>.sql` e acrescente
   `psql -v ON_ERROR_STOP=1 -f sdd/tests/governanca/<F>_<Gnn>.sql` ao `cmd` do bloco `verify_gate`
   existente, contra banco de desenvolvimento, de teste ou branch — **nunca produção**. Projeto só com o
   banco de produção: escreva isso no DEFINE e use o `prova_manual` até existir um de teste. No
   relatório: *Riscos aceitos* e *Aplicado no DEFINE*. Linha
   `| **Governança** | GOVERNANCA_REVIEW_<F>.md · <a> aplicadas · <r> recusadas · <d> adiadas | <data> |`.
   Toda saída que escreve a linha final (itens 7 e 8) **remove o marcador de governança** do item 1.
9. **2ª falha** ⇒ o marcador fica e a linha diz `| **Governança** | falhou — <motivo> | <data> |`. Mensagem:
   `🛑 governança não rodou — <motivo em palavras>. Efeito: o build e a release param até resolver.`
   e as 2 saídas numeradas: (1) numa sessão nova, pedir "rode só o passo 11 (Governança) do sdd-define
   sobre <DEFINE>" — não o Define inteiro, que regravaria a spec; (2) dispensar: trocar a linha da tabela
   por `| **Governança** | dispensada — <motivo> | <nome, data> |` **e** trocar o marcador por
   `- [x] (governança) dispensada — <motivo>` (com o marcador no arquivo, o gate continua em 5).

A linha `Governança` só é escrita por este passo (ou pela dispensa da pessoa). O `verify-gate.sh` sai 5
enquanto ela não tiver um valor final: `N.A. — …`, `GOVERNANCA_REVIEW_…` ou `dispensada — …`.

### 12. Segurança (sempre, nesta sessão)

Todo app com login, rota pública, dado de terceiros, envio de arquivo, banco ou chamada paga tem as falhas de
segurança mais comuns de app feito com IA ao alcance; perguntar aqui custa uma linha de AT, e no build custa
retrabalho. Este passo roda **nesta sessão** (sem revisor fresco) e **não trava** o gate: é alerta, não bloqueio.

1. Siga o **modo Define** da skill `sdd-seguranca` (`.agents/skills/sdd-seguranca/SKILL.md`) sobre este DEFINE,
   com o `## Perfil de risco` do BRAINSTORM se existir: gatilhos pelo sentido; sem gatilho, `✅ segurança: N.A. —
   <motivo>` em 1 linha e nenhuma pergunta; com gatilho, os itens da stack (até 5 por rodada, do mais grave), uma
   pergunta por item, no formato do exemplo da skill.
2. **Aplicado** ⇒ AT novo no próximo id, em EARS, com o lado negativo, coberto pelo `cmd` do bloco `verify_gate`
   existente; rode `verify-gate.sh --print` de novo. **Recusado** e **adiado** ⇒ uma linha cada na sessão
   `### Segurança` de `## Clarifications`, com o motivo (o Build as copia para o BUILD_REPORT).
3. Escreva a linha da tabela do `## Technical Context`:
   `| **Segurança** | <a> aplicados (Snn, …) · <r> recusados (Snn, …) · <d> adiados (Snn, …) | <data> |` ou
   `| **Segurança** | N.A. — <motivo> | <data> |`. O Design lê a linha: com item aplicado, ele escreve o "como
   evitar" na seção `## Segurança`.

## Quality Gate

```text
[ ] Problema claro e específico · ≥1 persona · critérios de sucesso com números
[ ] ATs em EARS: keyword em cada um · If/Then presente se há gatilho indesejado · While/If-Then/Where considerados · ≤~10 · zero UX visual · bugfix com shall continue to
[ ] Rastreabilidade AT→gate: todo AT tem kind e está coberto pelo cmd do Verify Gate
[ ] Zero marcadores ativos (verify-gate.sh não devolve 5)
[ ] Fora de escopo explícito · Clarity ≥12/15 · LLM Prompts true/false com nota
[ ] ## Verify Gate com kind+cmd+pass_when executáveis (ou manual-ux com manual_fallback)
[ ] verify-gate.sh --print lista o bloco sem erro 64
[ ] kb-dominios.py sai 0 (KB Domains de ls sdd/kb/ ou nenhum)
[ ] Linha CONTEXTO de domínio preenchida (contexto/<slug>.md · sha · data, ou nenhum com motivo)
[ ] Passo 11 rodou: linha Governança final (N.A. — …, GOVERNANCA_REVIEW_…, dispensada — …) e sem marcador de governança
[ ] Passo 12 rodou: linha Segurança (N.A. — … ou aplicados · recusados · adiados); aplicados viraram AT no gate
[ ] Resposta fechada com o resumo de etapa (fragments/RESUMO_ETAPA.md)
```

## Por que cada regra existe

- **A segurança roda em todo Define, nesta sessão e sem trava** — a pergunta "quem pode ver esta linha?" custa
  um AT aqui e uma migração depois do build; como é alerta e o catálogo escolhe os itens, um revisor fresco e uma
  trava a mais no gate custariam mais do que acham.
- **O aceite é um comando com exit** — prosa ("o desconto deve funcionar") cada um lê do seu jeito; um
  comando dá a mesma resposta para quem construiu, para quem revisa e para a release.
- **EARS, com o padrão indesejado (If–Then)** — a gramática fixa obriga a nomear o gatilho, e o If–Then
  obriga a nomear a falha antes de construir, quando decidir o que fazer com ela ainda é barato.
- **Adjetivo sem número é recusado** — "rápido" passa em qualquer teste e não reprova nenhum; "em menos
  de 2 s" pode falhar, e só o que pode falhar prova alguma coisa.
- **A dúvida vira marcador no lugar exato, nunca suposição** — a suposição silenciosa vira código; o
  marcador faz o gate devolver 5 e segura todas as fases até alguém responder.
- **Cerca de 10 ATs, no máximo** — acima disso a spec está descrevendo implementação ou juntando duas
  features, e o gate fica caro demais para rodar a cada mudança.
- **KB Domains só de `ls sdd/kb/`, ou `nenhum`** — um domínio inventado manda o Design procurar padrões
  onde não há nada; o `kb-dominios.py` reprova o nome que não tem pasta.
- **O mapa do domínio vem de um agente que não viu a conversa** — quem vai escrever a spec já sabe o
  que quer construir e lê o código procurando confirmação; o cartógrafo descreve o que o código faz hoje,
  com o arquivo e a linha, e a fronteira prova que ele só gravou o mapa.
- **A governança roda em todo Define e trava o build** — skill avulsa ninguém é obrigado a rodar, e a
  lacuna esquecida só aparece depois do build, quando custa migração; N.A. registrado custa uma linha.
- **A trava é gravada antes do despacho** — se a sessão parar no meio, o DEFINE já diz que a revisão
  não rodou, e o gate segura o build em vez de deixá-lo passar em silêncio.
- **O gate composto nasce vermelho** — uma asserção que já passa antes da mudança não prova a mudança;
  rodá-la contra a árvore antiga mostra que ela avalia alguma coisa.

## Encerramento (obrigatório)

Feche com o **resumo de etapa** (`sdd/templates/fragments/RESUMO_ETAPA.md`); o 🏃 é
`/sdd-define`. Os 4 blocos na ordem: micro-kanban · Onde estamos · O que precisa de você (só se
N≥1) · O que vem depois, com ⚠️ inline.

**Próximo passo:** `/sdd-ux-review sdd/features/DEFINE_{FEATURE}.md` se há interface; senão
`/sdd-design sdd/features/DEFINE_{FEATURE}.md` (registre no DEFINE por que o UX review foi
pulado — kanban marca ➖ só com decisão registrada).

### Fluxo encadeado

Ao fechar, rode `bash sdd/bin/sdd-fluxo.sh seguir <fase> <DEFINE> <próxima>` só quando a linha
"Nesta skill" abaixo nomeia o `seguir` (contrato em `sdd/templates/fragments/FLUXO_ENCADEADO.md`).
Exit 0: escreva a linha de transição que o script imprimiu, o recibo **Decidi sozinho** (se houver) e
chame a próxima fase nesta sessão. Exit 1 com `encadeamento desligado`: só o Próximo passo acima, sem
repassar a linha. Exit 1 por outro motivo: diga o motivo em 1 frase e mostre o Próximo passo. Exit 64:
repasse a saída e trate como desligado. A pergunta `[auto · de rotina]` com o encadeamento ligado
vira a opção recomendada e uma linha do recibo; as marcadas D1 a D5 continuam perguntadas. "Pare"
desliga nesta chamada (`--parar`).

Nesta skill: `seguir define sdd/features/DEFINE_{FEATURE}.md <próxima>`, com a próxima do Próximo
passo acima (ux-review ou design). A governança já rodou no passo 11 e a segurança no 12.

---

Parte do SDD Open by RDD — https://github.com/robertodiasduarte/sdd-open
