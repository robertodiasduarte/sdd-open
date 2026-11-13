# Clarify — Ambiguity Protocol

## Honesty rule

Diante de ambiguidade, marcar e perguntar. Nunca converter silêncio em decisão.

Durante o rascunho, uma ambiguidade pode ser representada no ponto exato por:

```text
[NEEDS CLARIFICATION: pergunta específica]
```

Esse marcador é temporário e deve desaparecer do DEFINE pronto.

## Nine-category sweep

| # | Category | Guiding question |
|---|---|---|
| 1 | Scope | O que entra e sai desta entrega? |
| 2 | Data model | Quais entidades, campos, estados ou ownership importam? |
| 3 | UX flow | O que o usuário vê/faz em sucesso, vazio, erro e permissão? |
| 4 | NFRs | Latência, volume, custo, janela, disponibilidade ou precisão? |
| 5 | Integrations | Qual contrato externo, limite ou failure mode existe? |
| 6 | Edge cases | O que acontece com dado ausente, permissão negada, provider down, fila cheia etc.? |
| 7 | Constraints | O que não pode mudar? |
| 8 | Terminology | Algum termo de domínio admite mais de uma leitura? |
| 9 | Done signal | Qual resultado objetivo e qual gate dizem que terminou? |

Classificar cada categoria como `Clear`, `Partial` ou `Missing`.

## Resolution protocol

1. Perguntar apenas ambiguidades materiais.
2. Preferir uma pergunta por interação.
3. Nunca exceder 5 por rodada.
4. Quando houver opções, usar 2–4 alternativas e colocar a recomendada primeiro.
5. Integrar a resposta no corpo do spec.
6. Registrar em `## Clarifications`:

```markdown
### Session YYYY-MM-DD
- [x] (categoria) pergunta → resposta; integrada em <seção>
```

## Ready condition

Zero marcadores ativos e nenhuma questão bloqueante escondida em `Open Questions`.
