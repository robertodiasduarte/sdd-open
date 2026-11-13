# DEFINE: Cadastro de cliente com CPF

> Exemplo pronto para copiar. O cadastro de cliente recusa CPF inválido antes de gravar. Veja a seção Verify Gate: o gate usa `kind: test` (existe comando) e, logo abaixo, mostra a troca para `kind: manual-ux` (não existe comando).

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | CADASTRO_CLIENTE_CPF |
| **Date** | 2026-10-26 |
| **Author** | Exemplo do SDD Starter |
| **Status** | Ready for Design |
| **Clarity Score** | 13/15 |

---

## Problem Statement

O escritório cadastra clientes com CPF digitado à mão e grava CPF com dígito verificador errado; a nota fiscal emitida depois volta rejeitada e alguém precisa corrigir o cadastro e reemitir.

---

## Target Users

| User | Role | Pain Point |
|---|---|---|
| Assistente do escritório | Cadastra clientes novos | Só descobre o CPF errado quando a nota volta rejeitada |
| Contador responsável | Revisa e emite as notas | Perde tempo reemitindo nota por erro de cadastro |

---

## Goals

| Priority | Goal |
|---|---|
| **MUST** | Recusar CPF com dígito verificador inválido antes de gravar o cliente |
| **MUST** | Aceitar CPF com ou sem pontuação (o mesmo CPF válido de teste com e sem pontos e traço) |
| **SHOULD** | Mostrar ao usuário qual é o problema do CPF, em português |
| **COULD** | Avisar quando o CPF já está cadastrado em outro cliente |

---

## Success Criteria

- [ ] 100% dos CPFs com dígito verificador inválido da lista de teste são recusados.
- [ ] 100% dos CPFs válidos da lista de teste são aceitos, com e sem pontuação.
- [ ] Nenhum cliente é gravado quando o CPF é recusado.

---

## Acceptance Tests

| ID | Pattern | Criterion (EARS) | Gate (`kind`) |
|---|---|---|---|
| AT-001 | Event-driven | **When** o usuário salva um cliente com um CPF válido de teste, o sistema **shall** gravar o cliente com o CPF sem pontuação | test |
| AT-002 | Unwanted | **If** o CPF tem dígito verificador inválido (o CPF válido de teste com o último dígito trocado), **then** o sistema **shall** recusar o cadastro e mostrar "CPF inválido: confira os dois últimos dígitos" | test |
| AT-003 | Unwanted | **If** o CPF tem todos os dígitos iguais (onze vezes o 1), **then** o sistema **shall** recusar o cadastro | test |
| AT-004 | Event-driven | **When** o usuário digita o CPF sem pontos e traço, o sistema **shall** aceitar o CPF como se tivesse pontuação | test |

---

## Clarifications

### Session 2026-10-26

- [x] (Edge cases) CPF com todos os dígitos iguais passa no cálculo do dígito verificador. Recusar? → Sim, recusar; integrated into AT-003

---

## Verify Gate

O projeto tem testes automatizados, então a resposta à pergunta "existe um comando que devolve 0 quando funciona?" é **sim**:

```yaml
verify_gate:
  kind: test
  cmd: "python3 -m pytest tests/test_cpf.py"
  pass_when: "exit 0"
  threshold: "—"
  manual_fallback: "—"
```

Se você não tem comando, troque o bloco acima por este (e mude a coluna `Gate` dos testes para `manual-ux`):

```text
verify_gate:
  kind: manual-ux
  cmd: "N/A (manual-ux)"
  pass_when: "checklist signed"
  threshold: "—"
  manual_fallback: "Eu abri o cadastro, salvei um cliente com um CPF válido de teste e vi o cliente na lista. Eu abri o cadastro, digitei o mesmo CPF com o último dígito trocado e vi a mensagem 'CPF inválido: confira os dois últimos dígitos'. Eu abri o cadastro, digitei um CPF com os onze dígitos iguais e vi o cadastro ser recusado. Eu abri a lista de clientes depois das recusas e vi que nenhum cliente novo foi gravado."
```

---

## Out of Scope

- Consulta do CPF na Receita Federal.
- Validação de CNPJ.
- Correção de CPFs já gravados antes desta feature.

---

## Constraints

| Type | Constraint | Impact |
|---|---|---|
| Technical | O cadastro atual grava o CPF como texto | A validação acontece antes de gravar, sem mudar o banco |
| Timeline | N/A | — |
| Resource | N/A | — |
| Other | CPFs dos testes são fictícios | Nenhum dado de cliente real nos testes |

---

## Technical Context

| Aspect | Value | Notes |
|---|---|---|
| **Deployment Location** | Formulário de cadastro de cliente | Validação na camada que grava o cliente |
| **KB Domains** | N/A | Regra do dígito verificador do CPF é pública |
| **IaC Impact** | None | Sem recurso novo |
| **LLM Prompts** | false | Validação por cálculo, sem IA |

---

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|---|---|---|---|
| A-001 | O projeto já usa pytest | Trocar o `cmd` pelo comando de teste que o projeto usa | yes |

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---|---:|---|
| Problem | 3 | Erro concreto e consequência (nota rejeitada) |
| Users | 3 | Quem cadastra e quem sofre o retrabalho |
| Goals | 2 | Mensagem exata só para o dígito verificador |
| Success | 3 | Percentuais sobre a lista de teste |
| Scope | 2 | Duplicidade ficou como COULD |
| **Total** | **13/15** | |

Minimum to proceed: **12/15**.

---

## Open Questions

None - ready for Design.

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | 2026-10-26 | SDD Define by RDD | Initial version |

---

## Next Step

Execute o **SDD Design by RDD**.
