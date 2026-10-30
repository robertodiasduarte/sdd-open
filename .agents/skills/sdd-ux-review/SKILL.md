---
name: sdd-ux-review
description: Gate de UX/CX do SDD Open, entre o Define e o Design — mapeia a jornada do usuário, acha atrito, estados faltantes e ambiguidade, aplica os dois princípios inegociáveis (premium e "se tem que explicar, está errado") e grava sdd/reviews/UX_REVIEW_{FEATURE}.md com requisitos concretos para o Design. Use em toda feature com interface (tela, CLI, documento gerado), ou quando o usuário disser /sdd-ux-review.
compatibility: Requer bash >= 3.2 e git >= 2.20. Independe de stack visual; usa o design system do projeto quando houver.
license: MIT
metadata:
  author: Roberto Dias Duarte
  version: "2.3.1"
  updated: "2026-10"
  fase: "UX"
---

# sdd-ux-review — gate de UX/CX

Na primeira resposta desta skill, comece com esta linha, uma vez só, antes do Status:
`sdd-ux-review v2.3.1 · out/2026 · versão atual: https://github.com/robertodiasduarte/sdd-open/releases/latest`

Traduzir requisitos em experiência **antes** que arquitetura e código endureçam. "Interface"
inclui tela, linha de comando, arquivo gerado, e-mail: qualquer coisa que uma pessoa lê e
precisa entender sem ajuda.

## Como falar com o aluno

Leia `references/como-falar.md` antes da primeira resposta: o glossário desta skill, o Status preenchido
e um exemplo completo. Pergunta e parada seguem `sdd/templates/fragments/PERGUNTA_DECISAO.md`.
Quem usa esta skill, em geral, nunca usou git nem terminal.

| Etapa | Nome para o aluno | Passos desta skill |
|---|---|---|
| 1 | Contexto | 1 |
| 2 | Jornada | 2 |
| 3 | Qualidade | 3 a 5 |
| 4 | Prioridades | 6 |
| 5 | Gravar | 7 e 8 |

Toda resposta, nesta ordem (pule a parte sem conteúdo):

1. **Status** — uma linha que começa pelo nome da fase: `UX review: ✅ 1 Contexto · ▶️ 2 Jornada · ⬜ 3 Qualidade · ⬜ 4 Prioridades · ⬜ 5 Gravar`
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

`/sdd-ux-review sdd/features/DEFINE_{FEATURE}.md`

## Os 2 princípios inegociáveis

Qualquer recomendação que viole um deles é promovida a **MUST de bloqueio**.

**1. Premium.** Qualidade percebida de produto pronto, não "MVP a polir": hierarquia óbvia
em 200 ms; densidade que respira; tipografia com propósito (≤3 tamanhos por surface);
movimento curto (150–250 ms, ease-out, zero bounce decorativo); hover/focus/active/disabled
todos pensados; estados vazios como oportunidade, não vergonha. Em CLI: um símbolo por
significado, sempre com palavra; erro com causa **e** conserto.

**2. Se tem que explicar, está errado.** Tooltip-muleta, helper text do óbvio, tour
obrigatório e "está na documentação" são sintomas. Estado ambíguo ("foi salvo? foi
enviado?") é defeito. Cor que conflita com semântica (rascunho em verde com ✅) é defeito.

**Teste do estranho:** alguém que nunca viu a feature completa a tarefa em silêncio?
**Teste do suporte:** você consegue imaginar um usuário mandando print perguntando "isso é
bug?" ou "como faço X?" — essa pergunta **é** o bug; resolve-se na interface.

## Processo

1. **Contexto.** Leia o DEFINE, `sdd/templates/UX_REVIEW_TEMPLATE.md`, `AGENTS.md` e, se
   existir, o design system do projeto. Extraia usuário, objetivo, dor, critérios, restrições e
   fora de escopo.
   Se o DEFINE não diz quem usa e em que contexto, ou se o aluno pedir, conduza antes a entrevista
   de `references/entrevista-publico.md` e grave o resultado em `## User and Context`.
2. **Jornada.** Antes → Entrada → Ação central → Feedback → Recuperação →
   (Interrupção → Retomada) → Conclusão → Follow-up. Para cada passo: intenção, emoção/risco, atrito, o que o sistema precisa
   confirmar, o que acontece quando falha.
3. **Qualidade UX/CX.** Clareza · Eficiência · Confiança · Acessibilidade · Responsividade ·
   Estados (loading, vazio, erro, sucesso, parcial, sem permissão, desabilitado) ·
   Continuidade (e-mail, suporte, expectativa) · Premium · Autoexplicativo · Gamificação
   (só quando serve ao usuário; senão, diga por que não).
4. **60/30/10.** Fundo dominante, surfaces secundárias (destaque × operacional ×
   sobreposição) e acento que aponta a próxima ação. Cite os tokens do design system do
   projeto; sem design system, proponha os papéis e registre como candidato. Contraste
   **medido** nos pares reais (≥4.5:1 texto, ≥3:1 não-texto). Significado nunca só por cor.
5. **Lentes cognitivas (não bloqueiam).** Lente nunca gera MUST, não entra no cálculo do
   status (`Ready for Design`) e nunca rebaixa uma regra: se o achado já viola a regra da última
   coluna, o MUST vem dela, citado à parte. Todo status diferente de `N.A.` exige evidência.
   Status: `OK` · `RECOMENDAÇÃO` (SHOULD ou COULD; vai ao handoff como `(lente Lx)`) · `ALERTA`
   (aplicar a lente ao pé da letra pioraria esta tela) · `N.A.` (com motivo; podem ir juntas numa linha).

   | Lente | Pergunta | Alerta embutido | Regra que manda |
   |---|---|---|---|
   | L1 Alcance (Fitts) | Ação principal perto da decisão? Linha/card inteiro clicável? 44 px recomendado | — | acessibilidade do passo 3 (alvo < 24×24 px, WCAG 2.2 AA) |
   | L2 Escolhas por passo (Hick-Hyman) | Quantas opções competem por decisão? Revelação progressiva cabe? | uso diário: densidade é recurso | 60/30/10 (acento aponta a próxima ação) |
   | L3 Retomada (Zeigarnik) | Sair no meio preserva o preenchido? A volta mostra o que falta? | sem lembrete que culpe | princípio 2, "Se tem que explicar, está errado" (estado ambíguo) |
   | L4 Convenção (Jakob) | Padrão fora da convenção de mercado tem justificativa? | não reaprender ação básica | — |
   | L5 Progresso real (Gradiente de meta) | Progresso vem do estado real e mostra o que falta? | progresso inflado é dark pattern | princípio 2 + gamificação honesta (passo 3) |
   | L6 Destaque único (Von Restorff) | Só o que importa se destaca? | `ALERTA` só com destaques concorrentes | 60/30/10 (passo 4) |
   | L7 Agrupamento (Miller) | Campos e dados em grupos com nome? | 7±2 não é regra de contagem | — |
   | S Sinal de validação real | Que número, depois da entrega, diz se funcionou? | recomendação, nunca critério de aceite | — |
6. **Priorizar.** MUST (quebra o sucesso do usuário) · SHOULD · COULD · WONT (ideia boa,
   excluída — diga por quê). Lente nunca é MUST.
7. **Handoff para o Design.** Requisitos de interação, componentes, estados obrigatórios,
   guia de copy (CTA com verbo, erro humano e acionável, confirmação com próximo passo),
   guia visual, gamificação (ou por que não), recomendações `(lente Lx)`, "Como medir
   depois" (sinal S), notas de aceite.
8. **Gravar** `sdd/reviews/UX_REVIEW_{FEATURE}.md`.

Se a feature **não tem** interface de nenhum tipo, escreva isso no DEFINE (Constraints) e o
kanban marca ➖. Não rode a revisão por cerimônia — mas antes pergunte: existe terminal,
arquivo ou mensagem que alguém vai ler? Então existe UX.

## Quality Gate

```text
[ ] Jornada mapeada · riscos explícitos · 7 estados considerados
[ ] Acessibilidade e responsividade tratadas · contraste com números medidos
[ ] 60/30/10 aplicado com papéis claros (ou N.A. justificado para não-visual)
[ ] Gamificação recomendada ou explicitamente dispensada
[ ] Premium e Autoexplicativo verificados; teste do estranho e do suporte aplicados
[ ] Cores nunca conflitam com semântica
[ ] Recomendações em MUST/SHOULD/COULD/WONT; violação de princípio = MUST
[ ] Lentes cognitivas com evidência; nenhuma vira MUST nem muda o status
[ ] Handoff concreto para o Design
[ ] Resposta fechada com o resumo de etapa (fragments/RESUMO_ETAPA.md)
```

## Por que cada regra existe

- **Interface inclui linha de comando, arquivo gerado e e-mail** — tudo que uma pessoa lê e precisa
  entender sem ajuda pode confundir, e o suporte paga por cada confusão.
- **Violação de princípio vira MUST** — "premium" e "se tem que explicar, está errado" deixados como
  sugestão são os primeiros cortados quando o prazo aperta.
- **Contraste medido, nunca estimado** — o olho de quem desenhou se acostuma com a tela; o número
  (4.5:1, 3:1) não.
- **Lente cognitiva nunca vira MUST nem muda o status** — as lentes são heurísticas com exceções
  conhecidas; promovê-las a regra bloqueia telas que estão certas.
- **Entrevista de público só quando o DEFINE não diz quem usa, ou quando o aluno pede** — perguntar o que
  já está escrito gasta a paciência que a pessoa vai precisar nas decisões que importam.
- **Sem interface de nenhum tipo, ➖ registrado; nunca revisão por cerimônia** — revisão sem objeto
  produz recomendações genéricas que o Design ignora, e ensina a ignorar as próximas.

## Encerramento (obrigatório)

Feche com o **resumo de etapa** (`sdd/templates/fragments/RESUMO_ETAPA.md`); o 🏃 é
`/sdd-ux-review`.

**Próximo passo:** `/sdd-design sdd/features/DEFINE_{FEATURE}.md`

---

Parte do SDD Open by RDD — https://github.com/robertodiasduarte/sdd-open
