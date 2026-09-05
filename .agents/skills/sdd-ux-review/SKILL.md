---
name: sdd-ux-review
description: Gate de UX/CX do SDD Open, entre o Define e o Design — mapeia a jornada do usuário, acha atrito, estados faltantes e ambiguidade, aplica os dois princípios inegociáveis (premium e "se tem que explicar, está errado") e grava sdd/reviews/UX_REVIEW_{FEATURE}.md com requisitos concretos para o Design. Use em toda feature com interface (tela, CLI, documento gerado), ou quando o usuário disser /sdd-ux-review.
compatibility: Requer bash >= 3.2 e git >= 2.20. Independe de stack visual; usa o design system do projeto quando houver.
license: MIT
metadata:
  author: RDD
  version: "2.0.0"
  fase: "UX"
---

# sdd-ux-review — gate de UX/CX

> Abra a resposta com o banner: `🧠 UX-REVIEW`.

Traduzir requisitos em experiência **antes** que arquitetura e código endureçam. "Interface"
inclui tela, linha de comando, arquivo gerado, e-mail: qualquer coisa que uma pessoa lê e
precisa entender sem ajuda.

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
2. **Jornada.** Antes → Entrada → Ação central → Feedback → Recuperação → Conclusão →
   Follow-up. Para cada passo: intenção, emoção/risco, atrito, o que o sistema precisa
   confirmar, o que acontece quando falha.
3. **Qualidade UX/CX.** Clareza · Eficiência · Confiança · Acessibilidade · Responsividade ·
   Estados (loading, vazio, erro, sucesso, parcial, sem permissão, desabilitado) ·
   Continuidade (e-mail, suporte, expectativa) · Premium · Autoexplicativo · Gamificação
   (só quando serve ao usuário; senão, diga por que não).
4. **60/30/10.** Fundo dominante, surfaces secundárias (destaque × operacional ×
   sobreposição) e acento que aponta a próxima ação. Cite os tokens do design system do
   projeto; sem design system, proponha os papéis e registre como candidato. Contraste
   **medido** nos pares reais (≥4.5:1 texto, ≥3:1 não-texto). Significado nunca só por cor.
5. **Priorizar.** MUST (quebra o sucesso do usuário) · SHOULD · COULD · WONT (ideia boa,
   excluída — diga por quê).
6. **Handoff para o Design.** Requisitos de interação, componentes, estados obrigatórios,
   guia de copy (CTA com verbo, erro humano e acionável, confirmação com próximo passo),
   guia visual, gamificação (ou por que não), notas de aceite.
7. **Gravar** `sdd/reviews/UX_REVIEW_{FEATURE}.md`.

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
[ ] Handoff concreto para o Design
[ ] Resposta fechada com o resumo de etapa (fragments/RESUMO_ETAPA.md)
```

## Encerramento (obrigatório)

Feche com o **resumo de etapa** (`sdd/templates/fragments/RESUMO_ETAPA.md`); o 🏃 é
`/sdd-ux-review`.

**Próximo passo:** `/sdd-design sdd/features/DEFINE_{FEATURE}.md`
