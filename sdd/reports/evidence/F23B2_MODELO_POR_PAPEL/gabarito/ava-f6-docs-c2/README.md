# ava-f6-docs-c2 — avaliador, F6_DOCS, ciclo 2 (PASS)

## De onde veio

- Avaliação: `sdd/reviews/AVALIACAO_F6_DOCS_20261029-ciclo2.md`, na branch `docs/incorporar-starter`.
- Commit avaliado: `aaae1b4` (`fix(f6): revisão de contexto fresco, ciclo 1 — 3 HIGH, 3 MEDIUM e 6 LOW`,
  2026-10-29 22:01), citado no cabeçalho ("sobre o commit `aaae1b4` na worktree destacada"). Existe no projeto.
- DEFINE e DESIGN: os mesmos v1.1 do ciclo 1 (`git show e6f8cb2:sdd/features/…`); o Revision History não tem linha
  do build, logo nada mudou neles entre os dois ciclos.
- Brief: a seção "Brief — modo `veredito`" de `contexto-fresco.md`, com `ciclo: 2`. **Diferença da época:** o
  avaliador histórico do ciclo 2 recebeu também os achados do ciclo 1 como brief de conferência (cabeçalho da
  avaliação); aqui vai só o brief padrão, como pede o formato do gabarito. A última linha (tabela por AT) foi
  acrescentada para o medidor.

## O esperado, linha a linha

`VEREDITO: PASS`: a linha `VEREDITO: PASS — 0 HIGH, 0 MEDIUM, 6 LOW (novos)` do bloco.

AT-001 a AT-014 PASS: o bloco não tem uma linha por AT. Ele diz, numa frase só, "AT-001 a AT-014: PASS
(sabotagens AT-001a/b, 002a–g, 003a/b, 004a, 005e, 006a, 007a, 008a/b/b2/c, 009 ×13, 014a/b/c vermelhas; clone limpo
verde; gate com 514 OK; contratos 0 linhas; check-versions VERDE; texto normalizado igual à v2.2.6 nas 7; baseline
v2.2.6 com 26 falhas)". Cada linha do esperado sai dessa frase.

Confirmação do PASS: os 6 LOW novos são de texto de documentação (guia, quickstarts, uma docstring de teste) e foram
aplicados em `1c9bbc7` (`fix(f6): revisão de contexto fresco, ciclo 2 — 6 LOW`), que é o commit da tag `v2.2.7`, a
release da F6. Nenhum AT mudou de resultado depois.

## Medidas

- Arquivos `tests/test_*.py` no commit: **24**. Suíte: 514 testes em 242 s (`evidence/F6_DOCS/AVAL2-gate.log`).
- Tempo e custo do avaliador histórico: **não registrados**. Há 14 sondas `AVAL2-*.log`. O custo guardado é só o da
  feature inteira (US$ 41.5481 nominal, linha de base da F23), sem divisão por papel.
- Cabe em ~15 min: a suíte inteira leva ~4 min.

## Ressalva que pesa: ATs que precisam da tag `v2.2.6`

Igual ao `ava-f6-docs-c1`: AT-011, AT-012 e AT-013 comparam com a `v2.2.6`, que não existe na cópia do
`papel-serie.sh` (git archive + 1 commit, sem histórico nem tags). O próprio ciclo 2 histórico cita "texto
normalizado igual à v2.2.6", "check-versions VERDE" e "baseline v2.2.6". Um avaliador que não acha a tag tende a dar
NAO_VERIFICADO, e 2 diferenças em 14 já tiram a execução da meta.
