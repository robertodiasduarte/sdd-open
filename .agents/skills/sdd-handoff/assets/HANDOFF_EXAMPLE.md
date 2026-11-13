# HANDOFF: Controle de Honorários

> Exemplo preenchido, com dados fictícios. Use como referência do nível de detalhe esperado — principalmente nas
> **Tarefas** e no **Prompt de retomada**, onde cada item traz o dado exato em vez de uma referência à conversa.

## Ficha

| Attribute | Value |
|-----------|-------|
| **Feature** | CONTROLE_HONORARIOS |
| **Objetivo** | Ver, por cliente, quanto foi faturado no mês, o que já foi pago e o que está vencido, sem abrir a planilha. |
| **Status** | 🔨 em andamento |
| **Última sessão** | 2026-03-11 |
| **Branch / pasta** | `feat/inadimplencia` · `controle-honorarios/` |
| **Artefatos** | `sdd/features/DEFINE_CONTROLE_HONORARIOS.md` · `sdd/features/DESIGN_CONTROLE_HONORARIOS.md` · `sdd/reports/BUILD_REPORT_CONTROLE_HONORARIOS.md` |
| **Verify Gate** | 🔴 2 em 2026-03-11 (o caso do pagamento no dia do vencimento) — `sdd/bin/verify-gate.sh sdd/features/DEFINE_CONTROLE_HONORARIOS.md` |

## Feito

- Etapa 1 (2026-03-04): cadastro de clientes e lançamentos mensais, com valor, vencimento e situação; em uso com os
  dados reais do escritório desde 2026-03-06.
- Etapa 2, 70% (2026-03-11): a tela de inadimplência lista os vencidos do mais antigo para o mais recente, com o total
  em aberto por cliente no topo da linha. Prova: os 6 clientes fictícios da base de teste aparecem na ordem certa.

## Falta

- Corrigir o total em aberto, que ainda soma o lançamento pago no mesmo dia do vencimento.
- Fixar o desempate da ordenação quando dois lançamentos vencem no mesmo dia.
- Exportar o resumo mensal em PDF (Etapa 3).

## Definition of Done

- [ ] No dia 1º, o painel mostra a lista de vencidos sem abrir a planilha.
- [ ] O PDF do mês anterior sai do painel.
- [ ] Recarregar a tela cinco vezes seguidas dá sempre a mesma ordem.

## ⛔ Landmines desta feature

- "Vencido" conta **dias corridos**, não úteis, porque a régua de cobrança do escritório também conta assim: com dois
  critérios, a tela e o que se diz ao cliente dariam números diferentes. Mudou a regra? Mude a régua junto.

## Casos e testes em aberto

- **Cliente com dois contratos ativos** — a "Padaria Aurora" (fictícia) tem escrituração e folha; o total consolidado
  está certo, mas o caso em que só um dos dois venceu não foi testado.
- **Vencimento no fim de semana** — o lançamento de 2026-02-28 (sábado) mostra 1 dia a mais de atraso do que o
  esperado; falta confirmar se é a regra de dias corridos ou erro de cálculo.
- **Cliente sem lançamento** — a tela ainda não foi vista nesse caso.

## Eventos

> Toda mudança de escopo, pausa ou replanejamento entra aqui como **linha nova**, com a data. Nunca
> reescreva "Falta" sem registrar o porquê aqui: senão a decisão desaparece.

- 2026-03-11 — O envio automático de cobrança por e-mail saiu do escopo (decisão da dona do escritório): ela quer
  conferir os valores à mão por dois meses antes de deixar a ferramenta escrever para cliente.

## Recomendações

- Corrigir o total em aberto antes do PDF: o PDF repetiria o número errado para o cliente.

## Setup

1. Abrir a pasta `controle-honorarios/` na branch `feat/inadimplencia` (`git status` mostra a árvore limpa).
2. Usar só a base de teste com os 6 clientes fictícios: nenhum dado real de cliente entra no desenvolvimento.

## Tarefas

1. **Corrigir a soma do total em aberto** para ignorar o lançamento pago — reproduzir com a Padaria Aurora,
   lançamento de 2026-03-05. Pronto quando: o total do cliente cai ao registrar o pagamento, sem recarregar a tela.
2. **Desempatar a ordenação** pelo nome do cliente, em ordem alfabética, quando o vencimento for igual. Pronto
   quando: cinco recargas seguidas dão a mesma ordem.
3. **Conferir o vencimento de 2026-02-28** contra a regra de dias corridos. Pronto quando: está escrito se o número
   está certo e, se não estiver, o cálculo foi corrigido.
4. **Ver a tela de um cliente sem lançamento.** Pronto quando: aparece uma mensagem clara em vez da lista vazia.

## Ship

- **Publicar:** a Etapa 2 sobe pela `sdd-release` depois das tarefas 1 e 2.
- **Limpar:** nada ainda; a branch fica até a Etapa 3.

---

## Prompt de retomada

```text
Retomar a feature CONTROLE_HONORARIOS.

Contexto: painel de honorários por cliente (faturado, pago, vencido) para não abrir a planilha. A Etapa 1
(cadastro e lançamentos) está em uso; a Etapa 2 (tela de inadimplência) está em 70%.
Pasta: controle-honorarios/ · branch feat/inadimplencia.
Leia primeiro: sdd/handoffs/HANDOFF_CONTROLE_HONORARIOS.md, depois sdd/features/DEFINE_CONTROLE_HONORARIOS.md e DESIGN_CONTROLE_HONORARIOS.md.
Estado do gate: `sdd/bin/verify-gate.sh sdd/features/DEFINE_CONTROLE_HONORARIOS.md` saiu 2 em 2026-03-11.

Próxima ação: corrigir o total em aberto da Padaria Aurora (lançamento de 2026-03-05, pago no dia do vencimento).
Não faça: mudar a estrutura do cadastro da Etapa 1 (está em uso com dados reais; exporte uma cópia antes) nem o
envio automático de cobrança (fora de escopo desde 2026-03-11).
Landmines: "vencido" é dias corridos, igual à régua de cobrança do escritório.
```

---

## Histórico de slices

### Etapa 2: tela de inadimplência — 2026-03-11

- A tela lê a mesma base da Etapa 1 e calcula o atraso pela data de hoje contra o vencimento.
- Fixada a regra de dias corridos (ver Landmines) e o total em aberto por cliente no topo da linha, porque agrupar
  por cliente era o primeiro movimento de quem abria a lista.
- Ficaram 2 defeitos (total com pagamento no dia, ordem instável) e 3 casos sem teste.

### Etapa 1: cadastro e lançamentos — 2026-03-04

- Cadastro de clientes e lançamentos mensais; em uso com os dados reais desde 2026-03-06. Nenhuma pendência aberta.
