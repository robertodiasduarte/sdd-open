# EARS — Acceptance Test Grammar

## Rules

1. Manter as palavras-âncora em inglês: `When`, `While`, `If`, `then`, `Where`, `shall`.
2. Cada teste representa um comportamento observável principal.
3. Bugfix exige pelo menos um `shall continue to`.
4. Adjetivo sem número não é critério mensurável.
5. Se existir gatilho indesejado plausível, incluir um teste `If ... then ... shall ...`.

## Patterns

| Pattern | Form | Natural gate |
|---|---|---|
| Ubiquitous | The `<system>` **shall** `<response>` | test/typecheck |
| Event-driven | **When** `<trigger>`, the `<system>` **shall** `<response>` | test |
| State-driven | **While** `<state>`, the `<system>` **shall** `<response>` | test |
| Unwanted | **If** `<undesired trigger>`, **then** the `<system>` **shall** `<response>` | negative test/smoke |
| Optional | **Where** `<feature present>`, the `<system>` **shall** `<response>` | test matrix |
| Non-regression | The `<system>` **shall continue to** `<existing behavior>` | regression test |

Combinações são aceitáveis quando ainda deixam um comportamento claramente observável.

## Rejection checklist

- [ ] Todo AT usa um padrão reconhecido.
- [ ] Há If/Then quando existe trigger indesejado plausível.
- [ ] Bugfix inclui `shall continue to`.
- [ ] Não há adjetivo de qualidade sem alvo observável.
- [ ] Cada AT pode ser ligado a um método de verificação.
