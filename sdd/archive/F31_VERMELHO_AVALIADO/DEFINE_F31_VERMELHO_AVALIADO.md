# DEFINE: F31 — Vermelho avaliado

> O `report-lint.py` passa a avisar quando o log de antes de um AT diz, na linha do próprio AT, que nenhum caso foi avaliado.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | F31_VERMELHO_AVALIADO |
| **Date** | 2026-11-25 |
| **Author** | Roberto Dias Duarte, com a `sdd-define` v2.9.1 |
| **Status** | Ready for Design |
| **Clarity Score** | 14/15 |

---

## Problem Statement

O `report-lint.py` (F30 S2, v2.27.0) exige o `AT-nnn.antes.log` com exit fora de 0, 126 e 127, mas lê só o exit do
comando. Num gate composto (um comando para vários ATs), um AT sem teste nenhum herda o exit vermelho dos outros e passa
como "vermelho antes do verde".

### Reprodução (2026-11-25, `c747662`, relatório em sandbox com as fixtures de `tests/test_f30_vermelho_antes.py`)

| Caso | Log | `report-lint.py` hoje | Devia |
|---|---|---|---|
| **Alvo** | antes em `[exit=2]`, linha do AT-001 em `PASS 0 · FAIL 0`, AT-005 em `FAIL 3` | exit 0, sem aviso sobre o AT | acusar |
| Controle: falhou avaliando | linha do AT em `FAIL 1`, `[exit=2]` | exit 0 | igual |
| Controle: `shall continue to` | `PASS 3 · FAIL 0`, `[exit=0]` | exit 0 | igual |
| Controle: `manual-ux` | `N.A. (<motivo>)` | exit 0 | igual |
| Controle: log sem contagem | `ImportError`, `[exit=1]` | exit 0 | igual (aviso só com comando compartilhado, D1) |
| Controle: tabela sem a coluna `Antes` | — | exit 0 com aviso | igual (D4) |
| Vizinho a | `shall continue to` com antes `[exit=0]` e `PASS 0 · FAIL 0` | exit 0, sem aviso | acusar (D5) |
| Vizinho b | `AT-nnn.log` final `[exit=0]` com `PASS 0 · FAIL 0` | exit 0, sem aviso | acusar (D5) |
| Vizinho c | AT novo com `PASS 2 · FAIL 0`, `[exit=2]` vindo de outro AT (já passava antes) | exit 0, sem aviso | acusar (D5) |

### O que foi medido

- **O formato não existe no Open:** 0 de 2.442 logs de `sdd/reports/evidence/` têm `PASS n · FAIL n`. A `sdd-define` pede
  do gate composto só `AT-00N ✅/❌`. Sem um formato combinado, a máquina não tem o que ler.
- **Ruído do aviso:** dos 14 `AT-*.antes.log` do Open, os 14 têm comando próprio. Avisar em todo log sem contagem daria
  14 avisos, 14 deles sem risco; avisar só com o comando repetido em 2 ATs ou mais daria 0.
- **Coluna `Antes`:** dos 51 BUILD_REPORTs, 46 recebem o aviso de coluna ausente; 34 desses saem verdes e passariam a
  vermelhos se a coluna fosse exigida sem distinguir relatório novo de antigo.
- **Módulo que ainda não existe:** o `unittest` conta `Ran 1 test … errors=1`, e o `node --test` conta `fail 1`. O erro de
  carga não vira zero casos nesses dois; outros runners não foram medidos.
- **Windows:** o `·` gravado em cp1252 (byte 0xB7) chega ao leitor UTF-8 como U+FFFD.

---

## Target Users

| User | Role | Pain Point |
|------|------|------------|
| Quem conduz o build | Aluno ou dev que usa o método | Marca `true` um AT cujo teste nunca avaliou nada e só descobre em produção |
| Quem revisa ou publica | Revisor, avaliador, `sdd-release` | Lê "vermelho antes do verde" e confia numa prova que não é daquele AT |

---

## Goals

| Priority | Goal |
|----------|------|
| **MUST** | Acusar o AT novo cuja própria linha, no `antes.log`, soma zero casos avaliados |
| **MUST** | Definir e ensinar o formato da linha, para haver o que ler |
| **MUST** | Nenhum relatório aceito hoje passar a ser recusado |
| **SHOULD** | Avisar quando um comando compartilhado por vários ATs não traz contagem por AT |
| **SHOULD** | Levar a mesma leitura aos três casos vizinhos, só com aviso (D5) |

---

## Success Criteria

- [ ] O caso alvo e os 3 vizinhos da reprodução geram 1 aviso cada, que nomeia o AT e o log (hoje: 0).
- [ ] Os 5 controles da reprodução seguem com o mesmo exit e 0 avisos da classe nova.
- [ ] O exit do `report-lint.py` nos 51 BUILD_REPORTs do repositório é o mesmo antes e depois (51 de 51), com 0 avisos novos.
- [ ] Suíte inteira verde no Python 3.9 e no CI (macOS, Linux e Windows).

---

## Acceptance Tests

> "Linha do próprio AT": linha do log, fora da 1ª (`$ <comando>`), que **começa** pelo id (antes dele, só marca como `✅` ou `-`), com o id **exato** do AT (AT-001 não casa AT-0010 nem
> AT-001b) e a contagem `PASS n · FAIL n`; com mais de uma contagem na linha, vale a última. Com mais de uma linha do mesmo AT, vale a soma. Um erro de carga (módulo
> ausente) soma em FAIL (D3).

| ID | Padrão | Critério (EARS) | Gate (`kind`) |
|----|--------|-----------------|---------------|
| AT-001 | Event-driven | **When** o `report-lint.py` confere um AT `true` de comportamento novo cujo `AT-nnn.antes.log`, aceito pela F30 S2, termina em exit fora de 0, 126 e 127 e cuja linha do próprio AT soma `PASS 0 · FAIL 0`, the system **shall** imprimir 1 aviso com o id do AT, o caminho do log e o conserto em 1 linha, mantendo o exit que teria sem ele | test |
| AT-002 | Unwanted | **If** o mesmo log traz contagem de outro AT, de um id com o mesmo prefixo ou na 1ª linha (`$ <comando>`), **then** the system **shall** ignorá-la ao julgar o AT: o `FAIL 3` do vizinho não tira o aviso, e o `PASS 0 · FAIL 0` do vizinho não o cria | test |
| AT-003 | State-driven | **While** o `antes.log` de um AT novo não tem linha do próprio AT com contagem, the system **shall** aceitá-lo com 0 avisos se o comando for só dele; se 2 ATs novos `true` ou mais do relatório (ids distintos, com o antes aceito) têm a mesma 1ª linha no `antes.log`, 1 aviso por comando, com os ids dos que estão sem contagem | test |
| AT-004 | Non-regression | The system **shall continue to** aceitar, com 0 avisos da classe nova, o `antes.log` cuja linha do próprio AT tem `FAIL` de 1 ou mais, inclusive pelo módulo que ainda não existe | test |
| AT-005 | Unwanted | **If** o log foi gravado no Windows (fim de linha CRLF, ou o `·` em cp1252), **then** the system **shall** chegar ao mesmo resultado do log em UTF-8 com LF | test |
| AT-006 | Event-driven | **When** alguém escreve um gate composto ou o `antes.log` pelo método, the system **shall** ensinar o mesmo formato e a regra do erro de carga em `sdd-define/SKILL.md`, `disciplina-de-teste.md` e `EVIDENCIA.md`, e o exemplo de cada texto **shall** ser reconhecido pelo leitor do `report-lint.py` | test |
| AT-007 | Non-regression | The system **shall continue to** dar o mesmo exit, sem aviso da classe nova, ao AT com `FAIL 1`, ao `shall continue to` verde com casos, ao `N.A.` de gate fora de `test`/`cmd`, ao log sem contagem de comando próprio e ao relatório sem a coluna `Antes` | test |
| AT-008 | Non-regression | The system **shall continue to** passar a suíte inteira, o `publish-gate` em modo CI sobre uma cópia de `git archive` e o `check-versions.py --base origin/main` | test |
| AT-009 | Unwanted | **If**, num AT `true` de gate `test`/`cmd` de tabela com a coluna `Antes`, a soma das linhas do próprio AT é `PASS 0 · FAIL 0` num antes `[exit=0]` de `shall continue to` ou no `AT-nnn.log` citado na evidência e terminado em `[exit=0]`, ou é `PASS ≥ 1 · FAIL 0` num antes vermelho de AT novo, **then** the system **shall** imprimir 1 aviso por log, com o id do AT, o log e o caso (zero casos avaliados, ou já passava antes), mantendo o exit | test |

**Padrões considerados:**
- **While:** AT-003.
- **If–Then:** AT-002 e AT-005.
- **Where:** N.A. — sem flag de config nova.


---

## Clarifications

### Session 2026-11-25

Roberto: "avalie as decisões, siga sua recomendação, pergunte-me apenas em casos críticos". Vale a recomendada de cada uma:

- [x] (terminologia) D1 — Formato e log sem contagem? → `AT-nnn … (PASS n · FAIL n)`; aviso só quando 2 ATs novos ou mais usam o mesmo comando; integrado em AT-001, AT-003 e AT-006
- [x] (restrições) D2 — Aviso ou bloqueio? → aviso; bloqueio em outra frente, depois de 5 relatórios com a contagem, em 2 projetos ou mais, com 0 alarmes falsos; integrado em AT-001, AT-009 e Out of Scope
- [x] (edge cases) D3 — Módulo que ainda não existe? → vermelho válido, contado em FAIL na linha do próprio AT; integrado em AT-004 e AT-006
- [x] (escopo) D4 — Exigir a coluna `Antes` em relatório novo? → outra frente; integrado em Out of Scope
- [x] (escopo) D5 — Vizinhos a, b e c? → entram, só com aviso; integrado em AT-009

---

## Verify Gate

```yaml
verify_gate:
  kind: test
  cmd: "test -f tests/test_f31_vermelho_avaliado.py && /usr/bin/python3 scripts/check-versions.py --base origin/main && T=$(mktemp -d) && git archive HEAD | tar -x -C $T && PUBLISH_GATE_MODE=ci bash scripts/publish-gate.sh $T && cd $T && test -f tests/test_f31_vermelho_avaliado.py && SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover -s tests -p 'test_f31_*.py' && SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover -s tests -p 'test_*.py'"
  pass_when: "exit 0"
  threshold: "—"
  manual_fallback: "—"
```

AT-001 a AT-007 e AT-009 ficam em `tests/test_f31_vermelho_avaliado.py`; o AT-008 é a suíte inteira, o `publish-gate` e o
`check-versions.py`. O `test -f` existe porque o `unittest discover` do Python 3.9 sai 0 sem nenhum teste.

---

## Out of Scope

- O que a F30 S2 já cobre: antes obrigatório, mesmo comando, antes verde recusado, `shall continue to`, gate inteiro
  vermelho sem asserção (`gate-baseline.sh`).
- Bloquear (exit 1) pela contagem (D2).
- Exigir a coluna `Antes` em relatório novo (D4).
- `AT-nnn.log` final terminado em `[exit≠0]`: o `report-lint.py` o aceita hoje. Nos 287 logs finais citados no
  repositório há 0 casos (94 não têm `[exit=]`); fica como pendência de outra frente.
- Ler a saída de cada runner (pytest, jest, vitest) para deduzir a contagem.

---

## Constraints

| Type | Constraint | Impact |
|------|------------|--------|
| Technical | Python stdlib, 3.9, Windows e bash 3.2, como o resto do `sdd/bin` | Leitura tolerante a CRLF e cp1252 (AT-005) |
| Technical | Texto de skill em frase positiva (F29); SKILL.md de até 500 linhas (`sdd-define/SKILL.md` tem 446) | Uma linha na `sdd-define`; o resto em `disciplina-de-teste.md` e `EVIDENCIA.md` |
| Technical | Texto que vai para o starter não cita `sdd/bin/…` (LM-035) | `disciplina-de-teste.md` ensina o formato sem citar o script |
| Technical | Arquivo novo no pacote entra no `MANIFEST.txt` no mesmo commit (LM-037) | `tests/test_f31_vermelho_avaliado.py` |

---

## Technical Context

| Aspect | Value | Notes |
|--------|-------|-------|
| **Deployment Location** | `sdd/bin/report-lint.py`, `sdd/templates/fragments/EVIDENCIA.md`, `.agents/skills/sdd-build/web/references/disciplina-de-teste.md`, `.agents/skills/sdd-define/SKILL.md`, `tests/` | Pacote do método |
| **KB Domains** | nenhum | O repositório não tem `sdd/kb/` |
| **IaC Impact** | None | — |
| **LLM Prompts** | false | Texto de skill e script local; nenhum prompt de produção |
| **CONTEXTO de domínio** | nenhum (pulado: sem `sdd/patterns/dominio.md`) | `contexto-lint.sh --sugerir`, 2026-11-25 |
| **Governança** | N.A. — só lê contagem de log de teste e imprime aviso; sem dinheiro, tributo, folha ou dado pessoal | revisor fresco, 2026-11-25 |
| **Segurança** | N.A. — script local só de leitura; sem login, rota pública, dado de terceiros, upload, IA ou banco | 2026-11-25 |
| **Desempenho** | N.A. — sem banco | 2026-11-25 |

---

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|----|------------|------------------|------------|
| A-001 | Quem escreve o gate composto consegue imprimir a contagem por AT | Só sobra o aviso de comando compartilhado (AT-003) | [ ] uso real |
| A-002 | O erro de carga aparece como falha no runner | Alarme falso no módulo que ainda não existe; por isso aviso (D2) | [x] `unittest` e `node --test`; outros não medidos |

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---------|-------------|-------|
| Problem | 3 | Reproduzido |
| Users | 2 | Dois papéis, sem amostra de uso fora do Open |
| Goals | 3 | Priorizados |
| Success | 3 | Contagens |
| Scope | 3 | D1 a D5 respondidas |
| **Total** | **14/15** | |

---

## Open Questions

None - ready for Design.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1 | 2026-11-25 | sdd-define | Rascunho com a reprodução, as medições e D1 a D5 abertas |
| 1.0 | 2026-11-25 | sdd-define | D1 a D5 com a recomendada; AT-009 |
| 1.3 | 2026-11-25 | build | Avaliador, ciclo 2 (O1): AT-001 fala do antes aceito |
| 1.2 | 2026-11-25 | build | Avaliador, ciclo 1: última contagem da linha; AT-003 fala de ids distintos com o antes aceito |
| 1.1 | 2026-11-25 | build | AT-004 vira não-regressão: já vale antes da mudança (medido) |

---

## Next Step

`/sdd-design sdd/features/DEFINE_F31_VERMELHO_AVALIADO.md`
(UX review não se aplica: sem interface).
