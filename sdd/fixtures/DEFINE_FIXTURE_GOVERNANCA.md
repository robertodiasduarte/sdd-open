# DEFINE: CONTAS_A_PAGAR

> Contas a pagar do Escritório Exemplo Ltda. (fixture da skill `sdd-governanca`: domínio fictício, sem
> dado real).

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | CONTAS_A_PAGAR |
| **Date** | 2026-10-11 |
| **Author** | define-agent |
| **Status** | Ready for Design |
| **Clarity Score** | 13/15 |

## Problem Statement

A equipe do Escritório Exemplo Ltda. paga as contas dos clientes por planilha: o mesmo boleto já foi pago
duas vezes, e ninguém consegue dizer depois quem lançou cada pagamento nem em que competência ele caiu.

## Target Users

| User | Role | Pain Point |
|------|------|------------|
| Analista financeiro | Lança e paga os boletos dos clientes | Retrabalho para achar pagamento em duplicidade |
| Coordenadora | Aprova os pagamentos acima da alçada | Aprova sem ver o histórico do lançamento |

## Goals

| Priority | Goal |
|----------|------|
| **MUST** | Lançar contas a pagar com débito e crédito em partidas dobradas |
| **MUST** | Importar boletos sem duplicar |
| **MUST** | Pagamento acima de R$ 5.000,00 aprovado por outra pessoa |
| **SHOULD** | Rateio do valor por centro de custo |

## Success Criteria

- [ ] 0 boleto pago em duplicidade em 3 meses
- [ ] 100% dos pagamentos acima de R$ 5.000,00 com aprovação de outro usuário
- [ ] Rateio de qualquer valor fecha no centavo

## Acceptance Tests

| ID | Padrão | Critério (EARS) | Gate (`kind`) |
|----|--------|-----------------|---------------|
| AT-001 | Unwanted | **If** a soma dos débitos de um lançamento for diferente da soma dos créditos, **then** o sistema **shall** recusar a gravação | test |
| AT-002 | Event-driven | **When** o analista corrige o valor de um lançamento já gravado, o sistema **shall** atualizar o valor e mostrar o novo saldo do fornecedor | test |
| AT-003 | Event-driven | **When** o analista grava um lançamento, o sistema **shall** aceitar qualquer data de competência informada | test |
| AT-004 | Event-driven | **When** o analista estorna um pagamento, o sistema **shall** apagar o lançamento original e criar o lançamento contrário | test |
| AT-005 | Unwanted | **If** qualquer coluna de valor (lançamento, linhas de débito e crédito, rateio, saldo) for declarada em ponto flutuante, **then** o sistema **shall** reprovar a migration — todas em `numeric(14,2)`; e **when** R$ 100,00 é rateado em 3 centros de custo, grava 33,34 + 33,33 + 33,33, com o centavo residual no primeiro centro da lista | test |
| AT-006 | Unwanted | **If** o mesmo boleto (mesma linha digitável) for importado duas vezes, **then** o sistema **shall** recusar a 2ª inserção pela chave única da linha digitável e manter a mesma contagem | test |
| AT-007 | Unwanted | **If** o usuário que criou um pagamento acima de R$ 5.000,00 tentar aprová-lo, **then** o sistema **shall** recusar a aprovação | test |

## Verify Gate

```yaml
verify_gate:
  kind: test
  cmd: "true"
  pass_when: "exit 0"
  threshold: "—"
  manual_fallback: "—"
```

## Out of Scope

- Conciliação bancária
- Emissão de nota fiscal

## Constraints

| Type | Constraint | Impact |
|------|------------|--------|
| Technical | Postgres, um único CNPJ por banco | Sem isolamento entre clientes nesta versão |
| Technical | Nenhuma IA grava, classifica ou sugere lançamento | Itens de IA não se aplicam |
