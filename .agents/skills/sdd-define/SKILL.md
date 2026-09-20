---
name: sdd-define
description: Fase 1 do SDD Open — transforma um brainstorm, notas ou pedido direto em especificação com testes de aceitação em EARS, protocolo de ambiguidade (NEEDS CLARIFICATION) e um Verify Gate executável, gravando sdd/features/DEFINE_{FEATURE}.md. Use quando o usuário pedir para especificar, definir requisitos, escrever a spec, ou disser /sdd-define.
compatibility: Requer bash >= 3.2 e git >= 2.20; roda sdd/bin/verify-gate.sh --print para validar o bloco do gate.
license: MIT
metadata:
  author: Roberto Dias Duarte
  version: "2.0.0"
  fase: "1"
---

# sdd-define — Fase 1

> Abra a resposta com o banner: `🧠 DEFINE (Fase 1)`.

Capturar requisitos e validá-los numa passada só. O DEFINE é o **contrato**: tudo que vem
depois (design, build, release) é julgado contra ele. Por isso ele sai com um **Verify Gate
executável** — um comando com exit code, não prosa.

## Entrada

`/sdd-define <BRAINSTORM_*.md | notas.md | "pedido direto">`. Vindo de um BRAINSTORM, a
extração é direta: perguntas já respondidas, abordagem já escolhida, YAGNI já aplicado.

## Processo

### 1. Contexto

Leia `sdd/templates/DEFINE_TEMPLATE.md`, `AGENTS.md`, a entrada, e os 3 fragmentos que regem
esta fase: `sdd/templates/fragments/EARS.md`, `CLARIFY.md`, `VERIFY_GATE.md`. Leia `## Sempre`
de `sdd/playbook.md`.

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
justificativa. Nomes de provedor citados como **plataforma-alvo** não contam.

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
`Ready for UX Review` se há interface).

## Quality Gate

```text
[ ] Problema claro e específico · ≥1 persona · critérios de sucesso com números
[ ] ATs em EARS: keyword em cada um · If/Then presente se há gatilho indesejado · While/If-Then/Where considerados · ≤~10 · zero UX visual · bugfix com shall continue to
[ ] Rastreabilidade AT→gate: todo AT tem kind e está coberto pelo cmd do Verify Gate
[ ] Zero marcadores ativos (verify-gate.sh não devolve 5)
[ ] Fora de escopo explícito · Clarity ≥12/15 · LLM Prompts true/false com nota
[ ] ## Verify Gate com kind+cmd+pass_when executáveis (ou manual-ux com manual_fallback)
[ ] verify-gate.sh --print lista o bloco sem erro 64
[ ] Resposta fechada com o resumo de etapa (fragments/RESUMO_ETAPA.md)
```

## Encerramento (obrigatório)

Feche com o **resumo de etapa** (`sdd/templates/fragments/RESUMO_ETAPA.md`); o 🏃 é
`/sdd-define`. Os 4 blocos na ordem: micro-kanban · Onde estamos · O que precisa de você (só se
N≥1) · O que vem depois, com ⚠️ inline.

**Próximo passo:** `/sdd-ux-review sdd/features/DEFINE_{FEATURE}.md` se há interface; senão
`/sdd-design sdd/features/DEFINE_{FEATURE}.md` (registre no DEFINE por que o UX review foi
pulado — kanban marca ➖ só com decisão registrada).

---

Parte do SDD Open by RDD — https://github.com/robertodiasduarte/sdd-open
