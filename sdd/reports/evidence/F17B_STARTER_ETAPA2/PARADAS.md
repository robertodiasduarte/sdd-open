# Tabela de paradas — starter v1.5.17 × skill gerada pela F17b

"Parada" = pergunta obrigatória ao aluno, ponto de aprovação, comando que o aluno roda, condição que bloqueia o fim
(DEFINE_F17B_STARTER_ETAPA2, critério de aceite do Roberto). Montada lendo os dois textos: o da tag `v1.5.17` do
starter (`git show v1.5.17:skills/<skill>/…`) e o gerado da árvore da frente (geração de ensaio sobre um clone da
`v1.5.17`). Toda linha **nova** precisa do OK do Roberto; recusada, sai do caminho sem terminal.

## sdd-brainstorm

| Parada | v1.5.17 | gerada | nova? | OK do Roberto |
|---|---|---|---|---|
| perguntas de descoberta, uma por vez, mínimo 3 antes das abordagens | sim | sim | não | — |
| pergunta de amostras | sim | sim | não | — |
| confirmar a abordagem escolhida | sim | sim | não | — |
| 2 validações incrementais antes de entregar | sim | sim | não | — |
| **perfil de risco**: 3 perguntas de segurança juntas, numa resposta (quem vê, quem muda, quanto alguém pode pedir), "não sei" vale | não | sim | **sim** | OK do Roberto, 2026-11-13 (manter) |
| não sobrescrever em silêncio um BRAINSTORM existente (pergunta só se já existe) | sim | sim | não | — |

## sdd-handoff

| Parada | v1.5.17 | gerada | nova? | OK do Roberto |
|---|---|---|---|---|
| modo inferido e confirmado em 1 linha, sem menu | sim | sim | não | — |
| ficha da mesma feature já existe ou é ambígua: perguntar antes de criar | sim | sim | não | — |
| checklist de fechamento no modo *entregar* (4 perguntas, não bloqueia) | sim | sim | não | — |
| **oferecer limpeza**: no terminal, o comando de remover a pasta da frente e, com a ficha ✅, arquivar os documentos em `sdd/archive/{F}/` com 1 OK (oferta; nada é apagado sem confirmação) | não | sim | **sim** | OK do Roberto, 2026-11-13 (manter) |
| linha Verify Gate na ficha / conferência por script | não (a v1.5.17 tinha `validate_handoff.py`, opcional) | não (sai na cópia) | não | — |

## sdd-governanca

| Parada | v1.5.17 | gerada | nova? | OK do Roberto |
|---|---|---|---|---|
| triagem: sem tema, N.A. em 1 linha | sim | sim | não | — |
| padrão do projeto: 5 perguntas no primeiro uso | sim | sim | não | — |
| uma decisão por lacuna (aplicar · recusar · adiar) | sim | sim | não | — |
| prova por script: só com Verify Gate por comando | sim ("peça também o `prova_script`") | sim | não | — |

`references/PROCEDIMENTO.md` gerado é igual, byte a byte, ao da `v1.5.17`.

## sdd-release (modo iniciante)

| Parada | v1.5.17 | gerada | nova? | OK do Roberto |
|---|---|---|---|---|
| fora de uma frente ou na branch principal: parar | sim | sim | não | — |
| identidade do git vazia: parar com 2 comandos `git config` | sim | sim | não | — |
| Fase 1 sozinha (arquivo estranho, versão staged diferente, migration sem registro, sintaxe, testes, segredo, base): parar na 1ª falha | sim | sim | não | — |
| **o único OK** ("Posso publicar?") | sim | sim | não | — |
| pasta mudou depois do OK: pedir OK de novo | sim | sim | não | — |
| `gh` sem login ou sem permissão: parar e dizer o que conferir | sim | sim | não | — |
| **abrir o endereço do deploy** quando o agente não consegue (pedido ao aluno, sem decisão) | não | sim | **sim** | OK do Roberto, 2026-11-13 (manter) |
| gravar `sdd/ambiente.md` | sim (a skill gravava) | não (só lê, se existir) | não (menos trabalho) | — |
| registro da migration | `- banco:` no `sdd/ambiente.md` **e** BUILD_REPORT | só a seção do BUILD_REPORT | não (uma exigência a menos) | — |

## Diferenças que não são paradas, mas mudam o que o aluno vê

- **Pastas** (decisão do Roberto, revisão do DESIGN): brainstorm, handoff e governança gravam em `sdd/features/`,
  `sdd/handoffs/`, `sdd/reviews/`; define, design e build (congeladas) seguem em `sdd/`. README e quickstart explicam.
- **Resumo de etapa** no fim de brainstorm e governança: um kanban de uma linha e o próximo passo (sem pergunta).
- **Release com a Vercel**: a conferência olha o status do commit e diz o endereço; nenhum token.
