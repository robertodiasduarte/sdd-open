---
name: sdd-brainstorm
description: Fase 0 do SDD Open — explora uma ideia vaga por diálogo antes de virar requisito. Faz perguntas uma de cada vez, coleta amostras, propõe 2–3 abordagens com prós e contras, aplica YAGNI e grava sdd/features/BRAINSTORM_{FEATURE}.md. Use quando o usuário disser "quero fazer algo mas não sei bem o quê", trouxer notas soltas ou pedir /sdd-brainstorm.
compatibility: Requer bash >= 3.2 e git >= 2.20; funciona em qualquer agente que leia AGENTS.md e .agents/skills/.
license: MIT
metadata:
  author: Roberto Dias Duarte
  version: "2.1.1"
  updated: "2026-10"
  fase: "0"
---

# sdd-brainstorm — Fase 0 (opcional)

Na primeira resposta desta skill, comece com esta linha, uma vez só, antes do Status:
`sdd-brainstorm v2.1.1 · out/2026 · versão atual: https://github.com/robertodiasduarte/sdd-open/releases/latest`

Explorar antes de especificar. O produto desta fase é **clareza**, não código: um documento
que o `/sdd-define` consegue transformar em spec com pouca pergunta.

```text
Fase 0: /sdd-brainstorm → sdd/features/BRAINSTORM_{F}.md   (ESTA SKILL)
Fase 1: /sdd-define     → sdd/features/DEFINE_{F}.md
UX:     /sdd-ux-review  → sdd/reviews/UX_REVIEW_{F}.md
Fase 2: /sdd-design     → sdd/features/DESIGN_{F}.md
Fase 3: /sdd-build      → código + sdd/reports/BUILD_REPORT_{F}.md
Fase 4: /sdd-release    → publicação com 1 OK + sdd/releases/{F}/
```

## Como falar com o aluno

Leia `references/como-falar.md` antes da primeira resposta: o glossário desta skill, o Status preenchido
e um exemplo completo. Pergunta e parada seguem `sdd/templates/fragments/PERGUNTA_DECISAO.md`.
Quem usa esta skill, em geral, nunca usou git nem terminal.

| Etapa | Nome para o aluno | Passos desta skill |
|---|---|---|
| 1 | Entender | 1 |
| 2 | Perguntas | 2 (uma por resposta) |
| 3 | Amostras | 3 |
| 4 | Abordagens | 4 e 5 (YAGNI) |
| 5 | Validar | 6 |
| 6 | Gravar | 7 |

Toda resposta, nesta ordem (pule a parte sem conteúdo):

1. **Status** — uma linha que começa pelo nome da fase: `Brainstorm: ✅ 1 Entender · ▶️ 2 Perguntas · ⬜ 3 Amostras · ⬜ 4 Abordagens · ⬜ 5 Validar · ⬜ 6 Gravar`
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

`/sdd-brainstorm <ideia | arquivo de notas | problema>`. Se não vier nada, pergunte
"O que você quer construir ou resolver?".

## Processo

### 1. Contexto

Leia `AGENTS.md`, `sdd/templates/BRAINSTORM_TEMPLATE.md` e a seção `## Sempre` de
`sdd/playbook.md`. Explore a estrutura do projeto e os commits recentes: o que já existe que
se parece com o pedido? Onde uma feature assim moraria?

### 2. Perguntas de descoberta — UMA por vez

Mínimo **3** antes de propor abordagem. Prefira múltipla escolha (2–4 opções); a
recomendada vem **primeiro**, com "(Recomendado)" e o motivo em uma frase.

| Tipo | Quando |
|---|---|
| Múltipla escolha | as opções são claras (preferido) |
| Aberta | território desconhecido |
| De esclarecimento | a resposta anterior foi vaga |

Boas perguntas: "Para quem é?", "O que muda no dia de quem usa?", "Como você saberia que
ficou pronto?", "O que NÃO precisa estar na primeira versão?".

### 3. Amostras (aterramento)

Sempre pergunte: "Existe algo que ancore a solução? (a) arquivos de entrada reais, (b) exemplos
da saída esperada, (c) dados verificados, (d) nada disponível". Se existir, leia e descreva no
documento — amostra real vale mais que descrição.

### 4. Abordagens — 2 ou 3, com recomendação

```markdown
### Abordagem A: {Nome} ⭐ Recomendada
**Por quê:** {1–2 frases}  ·  **Prós:** …  ·  **Contras:** …

### Abordagem B: {Nome}
**Por que não recomendada:** …
```

Lidere com a recomendação. Nunca entregue três opções sem opinião.

### 5. YAGNI

Para cada funcionalidade que surgiu: precisa para a primeira versão? Resolve o problema
central? Se não, sai — e fica **registrada** na tabela "Removidas", com o motivo e se pode
voltar depois. O que sai é tão importante quanto o que fica.

### 6. Validação incremental

Apresente o entendimento em blocos de 200–300 palavras e confirme cada um antes do
próximo. Mínimo **2** confirmações. Se o usuário corrigir, volte: "Entendi diferente. Revisando…".

### 7. Documento

Preencha `sdd/templates/BRAINSTORM_TEMPLATE.md` e grave em
`sdd/features/BRAINSTORM_{FEATURE}.md` (nome em CAIXA_ALTA_COM_UNDERSCORE, estável — é o
`feature_id` de toda a linha). Inclua a seção **Suggested Requirements for /define** com
problema, usuários, critérios de sucesso mensuráveis e fora de escopo confirmado.

## Se o agente não puder perguntar (sessão autônoma)

Responda cada pergunta pela evidência disponível, marque a resposta como `ASSUMIDO` e liste as
assunções em "O que precisa de você" no fechamento. Nunca invente uma resposta do usuário.

## Quality Gate

```text
[ ] ≥3 perguntas de descoberta feitas (ou ASSUMIDO marcado)
[ ] Pergunta de amostras feita
[ ] ≥2 abordagens exploradas, com recomendação
[ ] YAGNI aplicado e registrado
[ ] ≥2 validações incrementais
[ ] Abordagem escolhida confirmada pelo usuário (ou marcada pendente)
[ ] Requisitos-rascunho para o Define incluídos
[ ] Resposta fechada com o resumo de etapa (fragments/RESUMO_ETAPA.md)
```

## Por que cada regra existe

- **Uma pergunta por mensagem** — duas perguntas juntas recebem uma resposta só, quase sempre à mais
  fácil; a outra some sem ninguém perceber.
- **Pelo menos 3 perguntas antes das abordagens** — abordagem proposta cedo ancora a conversa: as
  perguntas seguintes passam a confirmar a solução em vez de entender o problema.
- **Sempre perguntar por amostras** — uma planilha real derruba suposições que uma descrição não
  derruba (o campo que vem vazio, o formato que muda no meio do mês).
- **Liderar com a recomendação** — três opções sem opinião devolvem a decisão a quem pediu ajuda
  justamente para decidir.
- **O que sai pelo YAGNI fica registrado, e nenhum corte é inventado** — o registro impede que a ideia
  volte escondida no Design; um corte inventado só para preencher a tabela apaga uma decisão que
  ninguém tomou.
- **Duas confirmações antes de gravar** — o documento vira a entrada do Define; um mal-entendido gravado
  aqui chega ao código com cara de requisito.
- **Sessão autônoma marca `ASSUMIDO`, nunca inventa a resposta do usuário** — no documento, uma resposta
  inventada não se distingue de uma real, e o Define a trata como decisão tomada.

## Encerramento (obrigatório)

Feche com o **resumo de etapa** — contrato em `sdd/templates/fragments/RESUMO_ETAPA.md`.
Esta fase é pré-linha: renderize o kanban completo **sem casa 🏃 própria**. Os 4 blocos, na
ordem: micro-kanban · Onde estamos (≤2 linhas) · O que precisa de você (só se houver pergunta
bloqueante; senão omita o bloco) · O que vem depois, na ordem (com ⚠️ inline onde uma
landmine morde).

**Próximo passo:** `/sdd-define sdd/features/BRAINSTORM_{FEATURE}.md`

---

Parte do SDD Open by RDD — https://github.com/robertodiasduarte/sdd-open
