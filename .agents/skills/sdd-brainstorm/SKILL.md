---
name: sdd-brainstorm
description: Fase 0 do SDD Open — explora uma ideia vaga por diálogo antes de virar requisito. Faz perguntas uma de cada vez, coleta amostras, propõe 2–3 abordagens com prós e contras, aplica YAGNI e grava sdd/features/BRAINSTORM_{FEATURE}.md. Use quando o usuário disser "quero fazer algo mas não sei bem o quê", trouxer notas soltas ou pedir /sdd-brainstorm.
compatibility: Requer bash >= 3.2 e git >= 2.20; funciona em qualquer agente que leia AGENTS.md e .agents/skills/.
license: MIT
metadata:
  author: Roberto Dias Duarte
  version: "2.0.0"
  fase: "0"
---

# sdd-brainstorm — Fase 0 (opcional)

> Abra a resposta com o banner: `🧠 BRAINSTORM (Fase 0)`.

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

## Encerramento (obrigatório)

Feche com o **resumo de etapa** — contrato em `sdd/templates/fragments/RESUMO_ETAPA.md`.
Esta fase é pré-linha: renderize o kanban completo **sem casa 🏃 própria**. Os 4 blocos, na
ordem: micro-kanban · Onde estamos (≤2 linhas) · O que precisa de você (só se houver pergunta
bloqueante; senão omita o bloco) · O que vem depois, na ordem (com ⚠️ inline onde uma
landmine morde).

**Próximo passo:** `/sdd-define sdd/features/BRAINSTORM_{FEATURE}.md`

---

Parte do SDD Open by RDD — https://github.com/robertodiasduarte/sdd-open
