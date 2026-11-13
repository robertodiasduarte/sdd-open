# HANDOFF: Controle de Honorários

> Exemplo preenchido. Use como referência do nível de detalhe esperado — principalmente nos **Próximos passos**, onde cada item traz o dado exato em vez de uma referência à conversa.

## Ficha da feature

| Campo | Valor |
|---|---|
| **Objetivo** | Um painel simples onde eu vejo, por cliente, quanto foi faturado no mês, o que já foi pago e o que está vencido — sem abrir a planilha. |
| **Status** | 🔨 em andamento |
| **Feito** | Etapa 1 ✅ 2026-03-04 (cadastro de clientes e lançamentos) · Etapa 2 🔨 2026-03-11 (tela de inadimplência, 70%) |
| **Falta** | Fechar a tela de inadimplência · exportar o resumo mensal em PDF |
| **Pronto quando** | Eu consigo abrir o painel no dia 1º, ver a lista de vencidos e exportar o PDF do mês anterior sem tocar na planilha. |

---

## Eventos

- 2026-03-11 — Tirei o envio automático de cobrança por e-mail do escopo. Motivo: quero conferir os valores manualmente por uns dois meses antes de deixar a ferramenta disparar mensagem para cliente. Volta depois que o painel estiver confiável.

---

## 2026-03-11 — Etapa 2: tela de inadimplência

### O que foi feito

Construímos a tela que lista os lançamentos vencidos, ordenados do mais antigo para o mais recente. A tela lê a mesma base da Etapa 1 e calcula o atraso comparando a data de vencimento com a data de hoje.

Decidimos que "vencido" considera apenas dias corridos, não úteis. O motivo é prático: a régua de cobrança do escritório também trabalha em dias corridos, então usar dois critérios diferentes geraria divergência entre a tela e o que é dito ao cliente.

Também mudamos a exibição de valores: passamos a mostrar o total em aberto por cliente no topo da linha, porque agrupar por cliente era o primeiro movimento que eu fazia toda vez que abria a lista.

### Casos e testes em aberto

- **Cliente com dois contratos ativos** — o cliente fictício "Padaria Aurora" tem dois lançamentos mensais (contrato de escrituração e contrato de folha). O total consolidado aparece correto, mas ainda não testei o que acontece quando só um dos dois está vencido.
- **Lançamento com vencimento em fim de semana** — o lançamento de 2026-02-28 (sábado) aparece com 1 dia a mais de atraso do que eu esperava. Preciso confirmar se isso é o comportamento correto sob a regra de dias corridos que acabamos de fixar, ou se é erro de cálculo.
- **Cliente sem nenhum lançamento** — ainda não verifiquei o que a tela mostra. Provavelmente é a tela vazia, mas não confirmei.

### Pendências

**🐛 Bug fix** — o que ficou quebrado, parcial ou com comportamento errado conhecido:

- O total em aberto no topo da linha ainda soma lançamentos já pagos quando o pagamento foi registrado no mesmo dia do vencimento. Reproduz com o lançamento de 2026-03-05 da Padaria Aurora.
- A ordenação quebra quando dois lançamentos têm a mesma data de vencimento — a ordem muda a cada carregamento da tela.

**✨ Feature improvement** — o que é incremento planejado, melhoria ou próxima etapa de escopo:

- Exportar o resumo mensal em PDF (era o item final da Etapa 2, ficou para a Etapa 3).
- Filtro por faixa de atraso (até 30 dias, 31 a 60, mais de 60). Não é essencial agora, mas foi a primeira coisa que pensei ao ver a lista pronta.

### Próximos passos

1. Corrigir a soma do total em aberto como discutimos na conversa anterior.
2. Definir critério de desempate na ordenação — usar o nome do cliente em ordem alfabética quando a data de vencimento for igual. Pronto quando: recarregar a tela cinco vezes seguidas produz sempre a mesma ordem.
3. Conferir o caso do vencimento em fim de semana (lançamento de 2026-02-28) contra a regra de dias corridos. Pronto quando: eu souber dizer se o número exibido está certo ou errado — e, se errado, o cálculo estiver corrigido.
4. Verificar a tela para um cliente sem lançamentos. Pronto quando: a tela mostrar uma mensagem clara em vez de uma lista vazia sem explicação.

### Alertas — o que não quebrar

- O cadastro de clientes da Etapa 1 já está em uso com dados reais do escritório. Não alterar a estrutura de cadastro sem antes exportar uma cópia.
- A regra de "vencido" é **dias corridos**. Se isso mudar, a régua de cobrança do escritório precisa mudar junto — as duas coisas têm que continuar dizendo o mesmo número.
- **Fora de escopo:** envio automático de cobrança por e-mail (retirado em 2026-03-11, ver Eventos) e qualquer integração com banco.

### Onde está o trabalho

Pasta `controle-honorarios` no computador do escritório, com cópia no drive. Os arquivos da tela de inadimplência estão em `telas/inadimplencia`. A base de dados de teste tem seis clientes fictícios — nenhum dado real de cliente foi usado durante o desenvolvimento.

---

## 2026-03-04 — Etapa 1: cadastro e lançamentos

Cadastro de clientes e lançamento de honorários mensais, com valor, data de vencimento e situação (em aberto ou pago). Funcionando e em uso com os dados reais do escritório desde 2026-03-06. Nenhuma pendência aberta desta etapa.
