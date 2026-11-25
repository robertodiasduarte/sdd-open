# BUILD REPORT: F31 — Vermelho avaliado

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | F31_VERMELHO_AVALIADO |
| **Date** | 2026-11-25 |
| **DEFINE** | [DEFINE_F31_VERMELHO_AVALIADO.md](../features/DEFINE_F31_VERMELHO_AVALIADO.md) (1.3) |
| **DESIGN** | [DESIGN_F31_VERMELHO_AVALIADO.md](../features/DESIGN_F31_VERMELHO_AVALIADO.md) (1.2) |
| **Status** | Complete |

---

## Summary

16 de 16 itens do manifest; 41 testes novos, escritos antes do código. Revisões: codex e auditor claude (4 rodadas, US$ 1,25).

---

## Landmines lidas no build

| Superfície | LM-nnn | Veredito | Como / onde |
|------------|--------|----------|-------------|
| testes novos | LM-001, LM-002 | ✔ tratado | executam o lint dos dois lados; antes vermelho; 3 sabotagens |
| desacordo da revisão | LM-021 | ✔ tratado | R1/R2 medidos (`R1-duas-tabelas.log`) |
| juiz por regex | LM-028 | ✔ tratado | id exato no começo da linha |
| suítes em paralelo | LM-031 | ✔ tratado | o gate esperou a suíte de outra sessão |
| starter, MANIFEST, 500 linhas | LM-035, LM-037, LM-038 | ✔ tratado | `test_gerar_starter` verde; item 9; 447 linhas |

---

## Candidatos ao playbook

```text
<<<CANDIDATO_PLAYBOOK
secao: Reviews / harness
sup: `version` `SKILL.md` `check-versions` `testes de versão`
regra: Subir a versão de uma skill quebra testes que fixam o número exato, e o `check-versions` verde não os vê. **Do instead:** antes do gate, `grep -rnF '<versão antiga>' tests` sem cortar a saída, e rode os módulos achados.
evidencia: sdd/reviews/AVALIACAO_F31_VERMELHO_AVALIADO_20261125-1610.md (B1: 7 testes)
ficha: —
mordeu_antes: —
>>>
```

---

## Seleção de modo

| Item | Valor |
|---|---|
| Sinais | 9 itens acoplados, um autor |
| Recomendação | default |
| Decisão do usuário | default, pela autorização de seguir as recomendações (2026-11-25) |
| Refatorar | ligado |

---

## Drift detectado

- 7 testes com a versão fixa entraram no manifest (avaliador, B1).
- AT-004 virou não-regressão: já valia antes do código.
- A avaliação dos ciclos 2 e 3 foi gravada em resumo, não verbatim; as sondas estão nos logs `AVAL2-*` e `AVAL3-*`.

---

## Files Created

| File | Verified |
|------|----------|
| `tests/test_f31_vermelho_avaliado.py` | ✅ |

---

## Verification Results

lint: slot vazio

---

## Qualidade (avisos)

> Só o código novo ou alterado desde `origin/main` (e47c2ec). Aviso: não reprova.

### Complexidade

- não medido: lizard ausente (não está no PATH) — para medir, instale com `python3 -m pip install lizard` e rode de novo

### Duplicação

- não medido: jscpd ausente (não está no PATH) — para medir, instale com `npm install -g jscpd` e rode de novo

---

## Contrato de aceite

N.A. (1 camada).

---

## Acceptance Test Verification

| ID | Critério (EARS, verbatim do DEFINE) | Antes | Resultado | Evidência |
|----|-------------------------------------|-------|-----------|-----------|
| AT-001 | **When** o `report-lint.py` confere um AT `true` de comportamento novo cujo `AT-nnn.antes.log`, aceito pela F30 S2, termina em exit fora de 0, 126 e 127 e cuja linha do próprio AT soma `PASS 0 · FAIL 0`, the system **shall** imprimir 1 aviso com o id do AT, o caminho do log e o conserto em 1 linha, mantendo o exit que teria sem ele | `evidence/F31_VERMELHO_AVALIADO/AT-001.antes.log` | true | `evidence/F31_VERMELHO_AVALIADO/AT-001.log` · `evidence/F31_VERMELHO_AVALIADO/AT-001.sabotagem.log` · `AVALIACAO_F31_VERMELHO_AVALIADO_20261125-1750.md` |
| AT-002 | **If** o mesmo log traz contagem de outro AT, de um id com o mesmo prefixo ou na 1ª linha (`$ <comando>`), **then** the system **shall** ignorá-la ao julgar o AT: o `FAIL 3` do vizinho não tira o aviso, e o `PASS 0 · FAIL 0` do vizinho não o cria | `evidence/F31_VERMELHO_AVALIADO/AT-002.antes.log` | true | `evidence/F31_VERMELHO_AVALIADO/AT-002.log` · `evidence/F31_VERMELHO_AVALIADO/AT-002.sabotagem.log` · `AVALIACAO_F31_VERMELHO_AVALIADO_20261125-1750.md` |
| AT-003 | **While** o `antes.log` de um AT novo não tem linha do próprio AT com contagem, the system **shall** aceitá-lo com 0 avisos se o comando for só dele; se 2 ATs novos `true` ou mais do relatório (ids distintos, com o antes aceito) têm a mesma 1ª linha no `antes.log`, 1 aviso por comando, com os ids dos que estão sem contagem | `evidence/F31_VERMELHO_AVALIADO/AT-003.antes.log` | true | `evidence/F31_VERMELHO_AVALIADO/AT-003.log` · `evidence/F31_VERMELHO_AVALIADO/AT-003.sabotagem.log` · `AVALIACAO_F31_VERMELHO_AVALIADO_20261125-1750.md` |
| AT-004 | The system **shall continue to** aceitar, com 0 avisos da classe nova, o `antes.log` cuja linha do próprio AT tem `FAIL` de 1 ou mais, inclusive pelo módulo que ainda não existe | `evidence/F31_VERMELHO_AVALIADO/AT-004.antes.log` | true | `evidence/F31_VERMELHO_AVALIADO/AT-004.log` · `AVALIACAO_F31_VERMELHO_AVALIADO_20261125-1750.md` |
| AT-005 | **If** o log foi gravado no Windows (fim de linha CRLF, ou o `·` em cp1252), **then** the system **shall** chegar ao mesmo resultado do log em UTF-8 com LF | `evidence/F31_VERMELHO_AVALIADO/AT-005.antes.log` | true | `evidence/F31_VERMELHO_AVALIADO/AT-005.log` · `AVALIACAO_F31_VERMELHO_AVALIADO_20261125-1750.md` |
| AT-006 | **When** alguém escreve um gate composto ou o `antes.log` pelo método, the system **shall** ensinar o mesmo formato e a regra do erro de carga em `sdd-define/SKILL.md`, `disciplina-de-teste.md` e `EVIDENCIA.md`, e o exemplo de cada texto **shall** ser reconhecido pelo leitor do `report-lint.py` | `evidence/F31_VERMELHO_AVALIADO/AT-006.antes.log` | true | `evidence/F31_VERMELHO_AVALIADO/AT-006.log` · `AVALIACAO_F31_VERMELHO_AVALIADO_20261125-1750.md` |
| AT-007 | The system **shall continue to** dar o mesmo exit, sem aviso da classe nova, ao AT com `FAIL 1`, ao `shall continue to` verde com casos, ao `N.A.` de gate fora de `test`/`cmd`, ao log sem contagem de comando próprio e ao relatório sem a coluna `Antes` | `evidence/F31_VERMELHO_AVALIADO/AT-007.antes.log` | true | `evidence/F31_VERMELHO_AVALIADO/AT-007.log` · `AVALIACAO_F31_VERMELHO_AVALIADO_20261125-1750.md` |
| AT-008 | The system **shall continue to** passar a suíte inteira, o `publish-gate` em modo CI sobre uma cópia de `git archive` e o `check-versions.py --base origin/main` | `evidence/F31_VERMELHO_AVALIADO/AT-008.antes.log` | true | `evidence/F31_VERMELHO_AVALIADO/AT-008.log` · `AVALIACAO_F31_VERMELHO_AVALIADO_20261125-1750.md` |
| AT-009 | **If**, num AT `true` de gate `test`/`cmd` de tabela com a coluna `Antes`, a soma das linhas do próprio AT é `PASS 0 · FAIL 0` num antes `[exit=0]` de `shall continue to` ou no `AT-nnn.log` citado na evidência e terminado em `[exit=0]`, ou é `PASS ≥ 1 · FAIL 0` num antes vermelho de AT novo, **then** the system **shall** imprimir 1 aviso por log, com o id do AT, o log e o caso (zero casos avaliados, ou já passava antes), mantendo o exit | `evidence/F31_VERMELHO_AVALIADO/AT-009.antes.log` | true | `evidence/F31_VERMELHO_AVALIADO/AT-009.log` · `AVALIACAO_F31_VERMELHO_AVALIADO_20261125-1750.md` |

Exit dos 51 BUILD_REPORTs igual antes e depois, 0 avisos novos: `evidence/F31_VERMELHO_AVALIADO/RELATORIOS-antes-depois.log`.

**Verify Gate (`sdd/bin/verify-gate.sh <DEFINE>`):** exit 0 · `evidence/F31_VERMELHO_AVALIADO/GATE.log`

---

## Veredito do avaliador

**Veredito do avaliador (C1):** PASS — `AVALIACAO_F31_VERMELHO_AVALIADO_20261125-1750.md` (ciclo 3, autorizado pelo Roberto; ciclos 1 e 2 NEEDS_WORK, corrigidos)

---

## Advisor Ledger

`sdd/reviews/LEDGER_REVISAO_F31_VERMELHO_AVALIADO.md`: 4 rodadas, a última sem achados; 1 APLICADA, 2 REBATIDA_EVIDENCIA.

---

## Segurança

nenhum
