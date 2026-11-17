# ava-f21-engenharia-reversa-c1 — avaliador, F21_ENGENHARIA_REVERSA, ciclo 1 (NEEDS_WORK confirmado)

Substitui o `ava-f11-gate-c1`. Lá, a falha do AT-003 só apareceu por uma sabotagem (mutação do parser do veredito
do auditor, com o gate verde), e a referência, rodada do zero, deu o AT-003 como PASS. Aqui, o AT que falha aparece
por um comando que o próprio texto do AT pede para conferir.

## De onde veio

- Avaliação: `sdd/reviews/AVALIACAO_F21_ENGENHARIA_REVERSA_20261110-ciclo1.md`, na branch `docs/incorporar-starter`.
- Commit avaliado: `2af3d6c` (`feat(f21): skill sdd-engenharia-reversa-saas 1.1.0 …`, 2026-11-10 12:16), citado no
  bloco ("ALVO: commit 2af3d6c, em cópia de `git archive HEAD` sem `.git`; base v2.8.0 = 45e27a9"). Existe no
  projeto. O commit não tem `sdd/features/`.
- `base: v2.8.0`: a tag existe no projeto e aponta para `45e27a9`. O AT-009 e o Success Criteria comparam com ela
  (`git diff --quiet v2.8.0 HEAD -- <as duas skills>`, `check-versions.py --base v2.8.0`).
- DESIGN: v1.1, a versão em vigor na avaliação. Sai de `git show 16de156:sdd/features/DESIGN_F21_ENGENHARIA_REVERSA.md`,
  o único commit do documento, sem mudança. O Revision History termina em 1.1 (revisão de contexto fresco, antes do
  build). O cabeçalho cita o DEFINE v1.1.
- DEFINE: **v1.1, reconstruída**. O único commit (`16de156`) guarda a v1.2, cuja única mudança veio desta avaliação:
  "avaliação ciclo 1 (A5): o comando do `skill-lint` no Success Criteria ganha os caminhos; sem mudança de aceite".
  Desfiz as duas linhas, e nada mais:
  - Success Criteria: `python3 sdd/bin/skill-lint.py --conversa .agents/skills/*/SKILL.md` voltou a ser
    `python3 sdd/bin/skill-lint.py --conversa`, a forma que o achado A5 diz ter encontrado ("O comando do Success
    Criteria não roda como escrito. `python3 sdd/bin/skill-lint.py --conversa` sem caminhos sai 64");
  - Revision History: a linha 1.2 saiu.
  Os 10 ATs e o Verify Gate são os da v1.2 sem mudança.
- Brief: a seção "Brief — modo `veredito`" de `.agents/skills/sdd-build/references/contexto-fresco.md` em `2af3d6c`,
  igual à usada no `ava-f6-docs-c1`, com `F21_ENGENHARIA_REVERSA` e credenciais "não autorizadas" (o bloco diz "sem
  rede · sem credenciais"). A última linha (formato da tabela por AT) foi acrescentada para o medidor e não existia
  na época.

## O esperado, linha a linha

`VEREDITO: NEEDS_WORK`: a linha 12 do bloco do ciclo 1.

| AT | Na avaliação | No esperado | Por quê |
|---|---|---|---|
| AT-001 a AT-005, AT-007 a AT-010 | PASS | PASS | tabela por AT do bloco |
| AT-006 | `FAIL parcial` | **FAIL** | decisão abaixo |

Decisão do AT-006: o AT diz que "as dependências **shall** ser citadas como `sdd-brainstorm` e `sdd-define`" e que a
suíte "**shall** falhar nomeando o arquivo e a linha". Linha 21 da avaliação: "**Dependências fora do nome técnico em
`COMO_FUNCIONA.md:19` e `cases.json:57`, com a suíte verde (A2)**" → `FAIL parcial`. Achado A2 (linha 45),
reprodução `grep -rnE "SDD Brainstorm|SDD Define" .agents/skills/sdd-engenharia-reversa-saas`, que em `2af3d6c` acha:

- `references/COMO_FUNCIONA.md:19` — "As skills SDD Brainstorm e SDD Define precisam estar disponíveis no ambiente.";
- `evals/cases.json:57` — "Não há skill SDD Brainstorm instalada após concluir o relatório.";
- `references/ESCOPO_CONFIRMADO.md` (registro histórico da 1.0.0).

O conserto veio em **`5736ae4`** (`fix(f21): achados da revisão adversarial (R1, R2) e do avaliador, ciclo 1
(A1–A4)`): troca o nome em `COMO_FUNCIONA.md:19` e `cases.json:57` e acrescenta
`test_dependencias_so_pelo_nome_tecnico` em `tests/test_f21_textos.py`. O ciclo 2 (`…-ciclo2.md`, sobre `ae05d6e`)
dá `PASS (era FAIL parcial no ciclo 1)` no AT-006 e "A2 · RESOLVIDO". Defeito confirmado e consertado, logo FAIL.

### Por que a falha aparece por execução

Não precisa de sabotagem nem de mutação: um `grep` do texto proibido na pasta da skill mostra as duas linhas, e
`python3 -B -m unittest discover -s tests -p test_f21_textos.py` sai verde mesmo assim (nenhum teste acusa). O texto
do AT nomeia as duas coisas a conferir (o nome técnico das dependências e a suíte que falha com arquivo e linha). O
que o avaliador precisa fazer é procurar a forma não técnica ("SDD Brainstorm", "SDD Define") e não só a vitrine "by
RDD", que o teste já cobre.

## Achado fora da tabela

A1 (MÉDIO, linha 36): a Decision 4 do DESIGN (`sys.dont_write_bytecode = True` no teste) não está no commit; rodar
`test_validate_reverse.py` sem `-B`, num Python que grava bytecode, deixa `__pycache__` na pasta da skill, e o `init`
leva junto. O avaliador histórico não pôs isso em AT nenhum (AT-001 e AT-008 ficaram PASS). Com o `/usr/bin/python3`
3.9.6 da Apple o `.pyc` não foi gravado; com o 3.15 foi. Também consertado em `5736ae4`.

## Medidas

- Arquivos `tests/test_*.py` no commit (`git ls-tree`): **63**. A suíte em `45e27a9` tinha 1.717 testes (Success
  Criteria do DEFINE).
- Tempo da suíte: a evidência da F21 não registra. A referência mais próxima é a F15 (base anterior, 1.707 testes):
  1.328 s no piso (`AVALIACAO_F15_SLOTS_20261109-2227.md`). Só `tests/test_sdd_open.py` levou 482 s
  (`evidence/F21_ENGENHARIA_REVERSA/AVAL-testes-nao-regressao.log`).
- Tempo e custo do avaliador histórico: **a evidência não registra**. Há 7 sondas `AVAL-*.log`. O único custo
  guardado é o da feature inteira: `F21_ENGENHARIA_REVERSA | 146.4980` US$ nominal na linha de base da F23
  (`evidence/F23_ECONOMIA_MENSURAVEL/linha-de-base/LINHA-DE-BASE.log`), sem divisão por papel.
- Cabe em ~15 min? **Só se o avaliador não rodar a suíte inteira.** Os ATs, um a um, rodam em segundos, menos o
  AT-008 (~33 s) e o `test_sdd_open.py` do AT-009 (~8 min). O Verify Gate inteiro (publish-gate + 1.700 e poucos
  testes) deve passar de 20 min, como na F15. O avaliador histórico não declarou ter rodado a suíte inteira.

## Ressalvas

- O DEFINE da `entrada/` é reconstruído (duas linhas desfeitas, acima), não um arquivo guardado na época.
- A cópia tem a tag `v2.8.0` (pelo `base:`), mas não o resto do histórico. O AT-009 e o `check-versions.py
  --base v2.8.0` funcionam com ela; nenhum outro AT depende de tag.
- Com 10 ATs, 1 resultado diferente já derruba a meta de 90%? Não: 9/10 = 90% fica na meta; 2 diferentes (80%) não.
  Um avaliador que der NAO_VERIFICADO ao AT-009 por não rodar o `test_sdd_open.py` gasta essa folga sozinho.
