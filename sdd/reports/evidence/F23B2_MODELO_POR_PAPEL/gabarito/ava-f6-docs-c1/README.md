# ava-f6-docs-c1 — avaliador, F6_DOCS, ciclo 1 (NEEDS_WORK confirmado)

## De onde veio

- Avaliação: `sdd/reviews/AVALIACAO_F6_DOCS_20261029-ciclo1.md`, na branch `docs/incorporar-starter`.
- Commit avaliado: `963c47e` (`feat(f6): guia do aluno, roadmap, quickstart…`, 2026-10-29 21:37), citado no
  cabeçalho da avaliação ("sobre o commit `963c47e` numa worktree destacada"). Existe no projeto.
- DEFINE e DESIGN: v1.1 os dois, a versão citada no cabeçalho ("contra `DEFINE_F6_DOCS.md` v1.1 e
  `DESIGN_F6_DOCS.md` v1.1"). Os arquivos de `entrada/` saem de `git show e6f8cb2:sdd/features/…`, o único commit
  desses documentos; o Revision History deles termina em 1.1 (fase Design), sem linha do build, então a versão
  guardada é a que o avaliador leu. O commit avaliado não tem `sdd/features/`.
- Brief: a seção "Brief — modo `veredito`" de `contexto-fresco.md`. O texto dela em `963c47e` é igual ao de hoje;
  a última linha (formato da tabela por AT) foi acrescentada para o medidor e não existia na época.

## O esperado, linha a linha

`VEREDITO: NEEDS_WORK`: a linha `VEREDITO: NEEDS_WORK — 3 HIGH, 3 MEDIUM, 6 LOW` do bloco.

| AT | Na avaliação | No esperado | Por quê |
|---|---|---|---|
| AT-001, AT-003 a AT-007, AT-009 a AT-014 | PASS | PASS | tabela por AT da avaliação |
| AT-008 | `PASS (L1)` | PASS | a 1ª palavra é PASS; o L1 (caixa do link no macOS) ficou como achado à parte |
| AT-002 | `PARCIAL (M2)` | **FAIL** | decisão abaixo |

Decisão do AT-002: a avaliação não deu PASS nem FAIL, deu PARCIAL — as sabotagens AT-002a–f mostraram que
`tests/test_docs.py` não falha com a frase do starter (linha 144), a do glossário (459) e "A pasta `sdd/` não entra
no git" (achado M2: `SDD_FORA_DO_GIT` só pega 2 frases, caixa exata). O conserto veio em **`aaae1b4`**
(`fix(f6): revisão de contexto fresco, ciclo 1 — 3 HIGH, 3 MEDIUM e 6 LOW`), que reescreve `SDD_FORA_DO_GIT` em
`tests/test_docs.py`; o ciclo 2 (`AVALIACAO_F6_DOCS_20261029-ciclo2.md`) registra "M2 SDD_FORA_DO_GIT | resolvido
no que foi pedido (2 frases do starter, "não entra", caixa alta vermelhos)" e as sabotagens AT-002a–g vermelhas.
Defeito confirmado e consertado, logo FAIL.

O veredito NEEDS_WORK vem sobretudo de 3 HIGH fora do texto dos ATs (afirmações falsas no guia e numa skill: H1
"registra e libera", H2 ficha da sdd-design, H3 YAGNI da sdd-brainstorm), todos resolvidos em `aaae1b4` segundo o
ciclo 2. É um caso que mede se o candidato acha defeito fora da tabela.

## Medidas

- Arquivos `tests/test_*.py` no commit (`git ls-tree`): **24**. A suíte tinha 513 testes e rodou em 244 s no
  piso (`evidence/F6_DOCS/AVAL-gate-suite.log`).
- Tempo e custo do avaliador histórico: **a evidência não registra**. Há 16 sondas `AVAL-*.log` (fora as
  `AVAL-DESIGN-*`). O único custo guardado é o da feature inteira: `F6_DOCS | 41.5481` US$ nominal na linha de
  base da F23 (`evidence/F23_ECONOMIA_MENSURAVEL/linha-de-base/LINHA-DE-BASE.log`), sem divisão por papel.
- Cabe em ~15 min? A suíte inteira (~4 min) cabe; as sabotagens do AT-002/AT-014 rodam o `test_docs` (segundos).

## Ressalva que pesa: ATs que precisam da tag `v2.2.6`

A cópia do `papel-serie.sh` é `git archive` + `git init` + 1 commit: **não tem histórico nem tags**. O avaliador
histórico rodou numa worktree com o histórico inteiro. AT-011 (texto igual à `v2.2.6`), AT-012
(`check-versions.py --base v2.2.6 --base-obrigatoria`) e AT-013 (caminhos idênticos byte a byte à `v2.2.6`)
dependem da tag; um avaliador honesto tende a dar NAO_VERIFICADO neles. Com 14 ATs, 2 diferentes já derrubam a
meta de 90% (12/14 = 85,7%). Sem a tag na cópia, a referência pode sair "FORA DA META" por causa do ambiente, não
do modelo.
