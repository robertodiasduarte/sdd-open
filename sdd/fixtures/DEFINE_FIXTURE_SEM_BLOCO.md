# DEFINE: FIXTURE_SEM_BLOCO

> Fixture do `verify-gate.sh`. Este DEFINE **não tem** a seção `## Verify Gate` — o runner
> correto devolve **`64`** (spec inválida) em vez de fingir que passou. Um DEFINE sem gate
> executável está incompleto por definição.

## Problem Statement

Uma spec que descreve o aceite em prosa e nunca em comando.

## Acceptance Tests

| ID | Padrão | Critério (EARS) | Gate (`kind`) |
|----|--------|-----------------|---------------|
| AT-001 | Ubiquitous | The system **shall** funcionar | test |
