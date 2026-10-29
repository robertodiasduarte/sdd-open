---
name: sdd-define
description: Fase 1 do SDD Open — transforma um brainstorm, notas ou pedido direto em especificação com testes de aceitação em EARS, protocolo de ambiguidade (NEEDS CLARIFICATION) e um Verify Gate executável, gravando sdd/features/DEFINE_{FEATURE}.md. Use quando o usuário pedir para especificar, definir requisitos, escrever a spec, ou disser /sdd-define.
compatibility: Requer bash >= 3.2 e git >= 2.20; roda sdd/bin/verify-gate.sh --print para validar o bloco do gate.
license: MIT
metadata:
  author: Roberto Dias Duarte
  version: "2.3.0"
  updated: "2026-10"
  fase: "1"
---

# sdd-define — Fase 1

Na primeira resposta desta skill, comece com esta linha, uma vez só, antes do Status:
`sdd-define v2.3.0 · out/2026 · versão atual: https://github.com/robertodiasduarte/sdd-open/releases/latest`

Capturar requisitos e validá-los numa passada só. O DEFINE é o **contrato**: tudo que vem
depois (design, build, release) é julgado contra ele. Por isso ele sai com um **Verify Gate
executável** — um comando com exit code, não prosa.

## Como falar com o aluno

Leia `references/como-falar.md` antes da primeira resposta: o glossário desta skill, o Status preenchido
e um exemplo completo. Pergunta e parada seguem `sdd/templates/fragments/PERGUNTA_DECISAO.md`.
Quem usa esta skill, em geral, nunca usou git nem terminal.

| Etapa | Nome para o aluno | Passos desta skill |
|---|---|---|
| 1 | Ler o brainstorm | 1 e 2 |
| 2 | Requisitos | 3 |
| 3 | Testes de aceitação | 4 e 5 |
| 4 | Perguntas | 6 e 7 |
| 5 | Verify Gate | 8 |
| 6 | Gravar | 9 e 10 |

Toda resposta, nesta ordem (pule a parte sem conteúdo):

1. **Status** — uma linha que começa pelo nome da fase: `Define: ✅ 1 Ler o brainstorm · ✅ 2 Requisitos · ▶️ 3 Testes de aceitação · ⬜ 4 Perguntas · ⬜ 5 Verify Gate · ⬜ 6 Gravar`
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

### 10. Conferir o KB Domains

`python3 sdd/bin/kb-dominios.py sdd/features/DEFINE_{FEATURE}.md` sobre o arquivo gravado: o KB Domains
só cita pastas de `sdd/kb/`, ou diz `nenhum`. Exit 0 segue; exit 1 ⇒ corrija o campo e rode de novo antes
de entregar. Os testes que ele listar (`<domínio>: <REGRA> → <teste>`, das regras de uma base normativa)
entram no `cmd` do Verify Gate; se algum não entrar, registre o motivo no DEFINE e rode
`verify-gate.sh --print` de novo.

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
[ ] Resposta fechada com o resumo de etapa (fragments/RESUMO_ETAPA.md)
```

## Encerramento (obrigatório)

Feche com o **resumo de etapa** (`sdd/templates/fragments/RESUMO_ETAPA.md`); o 🏃 é
`/sdd-define`. Os 4 blocos na ordem: micro-kanban · Onde estamos · O que precisa de você (só se
N≥1) · O que vem depois, com ⚠️ inline.

**Próximo passo:** `/sdd-governanca sdd/features/DEFINE_{FEATURE}.md` se o DEFINE trata dinheiro,
saldo, lançamento, nota fiscal, tributo, folha ou dado pessoal; senão
`/sdd-ux-review sdd/features/DEFINE_{FEATURE}.md` se há interface; senão
`/sdd-design sdd/features/DEFINE_{FEATURE}.md` (registre no DEFINE por que o UX review foi
pulado — kanban marca ➖ só com decisão registrada).

---

Parte do SDD Open by RDD — https://github.com/robertodiasduarte/sdd-open
