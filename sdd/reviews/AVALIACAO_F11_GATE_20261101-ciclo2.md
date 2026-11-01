# AVALIAÇÃO F11_GATE — contexto fresco, modo veredito, ciclo 2

> Bloco devolvido pelo avaliador em contexto fresco (subagente sem a conversa do build), sobre `a9813ff`.
> Evidências: `sdd/reports/evidence/F11_GATE/AVAL2-*.log` (35) e `AVAL2-42-env-git-em-hooks.sonda.txt` (log que
> terminava em `sed`; o H1 é provado por AVAL2-43 e por `baseline-aval2.log`). Correções em `06e5a9d`, com teste
> vermelho antes. Ciclo 2 é o último que a sdd-build permite; a prova seguinte é a revisão real.

```text
<<<AVALIACAO
FEATURE: F11_GATE · ciclo 2 · modo veredito · HEAD a9813ff (feat/f11-gate)
Veredito: NEEDS_WORK — 1 HIGH novo e 1 LOW novo. Os 5 achados do ciclo 1 (M1, L1, L2, L3, L4) FECHADOS por execução
(AVAL2-15/45, -19, -37/38/39, -32/32b, -29). Todos os ATs PASS; Verify Gate em a9813ff: 886 OK (AVAL2-30).
Init num repo novo copia os 10 stubs e o gate instalado sai verde com 103 asserções.

ACHADOS
- H1 · HIGH · AT-001/AT-011: o gate escreve no repositório real do usuário quando herda GIT_DIR / GIT_INDEX_FILE (o git
  os exporta absolutos para hooks numa worktree, AVAL2-42). De um pre-commit/pre-push numa worktree, o git init /
  checkout -b / add / commit do repositório descartável agem no repo do usuário: o staged vira commit "gate: base" na
  branch dele, o HEAD vai para "feat", e o gate morre com traceback e exit 1 (AVAL2-43; só GIT_DIR: AVAL2-41).
  Correção: tirar todo GIT_* não definido pelo gate; conferir --show-toplevel == REPO antes do commit (senão 3); teste
  vermelho com GIT_DIR apontando para um repo em mktemp, provando que fica intacto.
- L1 · LOW · AT-003: o gate não confere arquivo, linha nem severidade do NOVO, só achado/veredito; severidade sempre
  HIGH passa VERDE (AVAL2-46). O loop trata NOVO HIGH como grave. Rótulo "4 tipos" errado (o misto tem 3).
Notas: o init copia sdd/fixtures/revisao/eval/ para o projeto (as fixtures são exemplos copiados na 1ª instalação).
Não verificado localmente: CI Ubuntu/macOS, macOS ≤ 25 min, release v2.3.1.
>>>
```

## Decisão do build

| Achado | Veredito | Evidência |
|---|---|---|
| H1 | APLICADA: todo `GIT_*` herdado sai, `GIT_CEILING_DIRECTORIES` na pasta temporária, raiz conferida antes do commit (exit 3) | `baseline-aval2.log` (vermelho: traceback, exit 1) → `verde-aval2.log`; `test_aval2_h1_…` |
| L1 | APLICADA: jsonl comparado por (achado, veredito, arquivo, linha, severidade); rótulo "auditor com DISAGREE e NOVO" | `test_aval2_l1_severidade_do_novo_e_conferida` |
| Nota (fixtures no init) | REBATIDA_ESCOPO: comportamento do `init` desde a F1 — `sdd/fixtures/` são exemplos copiados só na 1ª instalação (`bin/sdd-open.sh:644`), apagáveis; o `eval-agree` lê `review.output_dir`, nunca `sdd/fixtures/` | `bin/sdd-open.sh:644–646` |
