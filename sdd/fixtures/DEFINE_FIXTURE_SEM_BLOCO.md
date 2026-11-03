# DEFINE: FIXTURE_SEM_BLOCO

> Fixture do `verify-gate.sh`. Este DEFINE **não tem** a seção `## Verify Gate` — o runner
> correto devolve **`64`** (spec inválida) em vez de fingir que passou. Um DEFINE sem gate
> executável está incompleto por definição.

## Problem Statement

Uma spec que descreve o aceite em prosa e nunca em comando.

## Technical Context

| Aspect | Value | Notes |
|---|---|---|
| **Governança** | N.A. — fixture do pacote, sem dinheiro, tributo, folha ou dado pessoal | com a linha, o exit desta fixture continua 64 (sem bloco) |

## Acceptance Tests

| ID | Padrão | Critério (EARS) | Gate (`kind`) |
|----|--------|-----------------|---------------|
| AT-001 | Ubiquitous | The system **shall** funcionar | test |
