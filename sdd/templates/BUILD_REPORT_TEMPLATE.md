# BUILD REPORT: {Feature Name}

> Implementation report for {Feature Name}

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | {FEATURE_NAME} |
| **Date** | {YYYY-MM-DD} |
| **Author** | build-agent |
| **DEFINE** | [DEFINE_{FEATURE}.md](../features/DEFINE_{FEATURE}.md) |
| **DESIGN** | [DESIGN_{FEATURE}.md](../features/DESIGN_{FEATURE}.md) |
| **Status** | In Progress / Complete / Blocked |

---

## Summary

| Metric | Value |
|--------|-------|
| **Tasks Completed** | {X}/{Y} |
| **Files Created** | {N} |
| **Lines of Code** | {N} |
| **Build Time** | {Duration} |
| **Tests Passing** | {X}/{Y} |
| **Agents Used** | {N} |

---

## Landmines lidas no build

> fase Build: `sdd/bin/playbook-lint.sh --grep "<superfície>" sdd/playbook.md` por item do
> File Manifest (tabela/RPC, slug de edge, basename, cron, conceito). **Só IDs + 1 linha** — nunca colar
> blocos (orçamento de contexto). O Curator (fase Release) converte `✔ tratado` em
> `ajudou`. Seção **obrigatória**: zero hits ⇒ `varredura rodada em {YYYY-MM-DD}, 0 aplicáveis`.
> O valor está nos hits que o DESIGN **não** listou em `## Landmines aplicáveis`.

| Superfície | LM-nnn | Veredito | Como / onde |
|------------|--------|----------|-------------|
| `{tabela \| edge \| arquivo}` | LM-{nnn} | ✔ tratado \| N.A. | {arquivo do manifest / decisão que trata · ou por que não se aplica} |

---

## Candidatos ao playbook

> Contrato: `.agents/skills/sdd-playbook/SKILL.md` § Candidato. O Curator só lê blocos literais; sem
> `evidencia:` o candidato sai **REJEITADO**. Nenhum candidato ⇒ escrever "nenhum candidato nesta build".

```text
<<<CANDIDATO_PLAYBOOK
secao: {uma das 8 seções, ≠ Tombstones}
sup: `{termo}` `{termo}`
regra: {regra em 1–3 linhas}. **Do instead:** {ação concreta}.
evidencia: {path do log/AT/incidente que prova que mordeu, ou DESIGN onde ajudou}
ficha: {feedback_x | —}
mordeu_antes: {LM-nnn se a causa já tinha bullet | —}
>>>
```

---

## Task Execution with Agent Attribution

| # | Task | Agent | Status | Duration | Notes |
|---|------|-------|--------|----------|-------|
| 1 | {Task description} | @{agent-name} | ✅ Complete | {Xm} | {Any notes} |
| 2 | {Task description} | @{agent-name} | ✅ Complete | {Xm} | {Any notes} |
| 3 | {Task description} | (direct) | 🔄 In Progress | - | {No specialist matched} |
| 4 | {Task description} | @{agent-name} | ⏳ Pending | - | - |

**Legend:** ✅ Complete | 🔄 In Progress | ⏳ Pending | ❌ Blocked

**Agent Key:**
- `@{agent-name}` = Delegated to specialist agent via Task tool
- `(direct)` = Built directly by build-agent (no specialist matched)

---

## Agent Contributions

| Agent | Files | Specialization Applied |
|-------|-------|------------------------|
| @{agent-1} | {N} | {What patterns/KB used} |
| @{agent-2} | {N} | {What patterns/KB used} |
| (direct) | {N} | DESIGN patterns only |

---

## Files Created

| File | Lines | Agent | Verified | Notes |
| ---- | ----- | ----- | -------- | ----- |
| `{path/to/file1.py}` | {N} | @{agent-name} | ✅ | {Any notes} |
| `{path/to/file2.py}` | {N} | @{agent-name} | ✅ | {Any notes} |
| `{path/to/config.yaml}` | {N} | (direct) | ✅ | {Any notes} |

---

## Verification Results

### Lint Check (ruff)

```text
{Output from ruff check or "All checks passed"}
```

**Status:** ✅ Pass / ❌ Fail

### Type Check (mypy)

```text
{Output from mypy or "All checks passed" or "N/A - not configured"}
```

**Status:** ✅ Pass / ❌ Fail / ⏭️ Skipped

### Tests (pytest)

```text
{Output from pytest or summary}
```

| Test | Result |
|------|--------|
| `test_function_1` | ✅ Pass |
| `test_function_2` | ✅ Pass |
| `test_integration` | ✅ Pass |

**Status:** ✅ {X}/{Y} Pass | ❌ {N} Fail

---

## Advisor Ledger (condicional — só se houve review de 2º vendor)

> Contrato: `fragments/ADVISOR_CONSULT.md`. Toda nota recebe **um dos três vereditos**, por
> escrito — nunca descartada em silêncio. Se não houve consulta, remover esta seção.
>
> **Ônus de prova simétrico:** acusar exige `arquivo:linha`, **rebater também**.
> `REBATIDA_EVIDENCIA` sem citação que contradiga é proibido — vira `REBATIDA_ESCOPO`
> (backlog) ou `APLICADA`. É o Caso B do paper arXiv:2608.18167 (crítico cede a rebatida
> fraca, bug some).

**Consulta:** {tipo: plan-review | delivery-review | conflito | judgment call} · {data} · {ferramenta: /adversarial-review | /codex:rescue | …}
**VERDICT do advisor:** {1 linha, verbatim}
**Proveniência:** {engines efetivos por papel; se houve fallback, declarar aqui — troca silenciosa é falso-verde}

| # | Nota | Severidade | Veredito | Evidência |
|---|------|-----------|----------|-----------|
| 1 | {resumo 1 linha} | HIGH | APLICADA | commit `{sha}` |
| 2 | {resumo 1 linha} | MED | REBATIDA_EVIDENCIA | `arquivo:linha` que contradiz |
| 3 | {resumo 1 linha} | LOW | REBATIDA_ESCOPO | fora do slice; backlog em {onde} |

---

## Issues Encountered

| # | Issue | Resolution | Time Impact |
|---|-------|------------|-------------|
| 1 | {Description of issue} | {How it was resolved} | {+Xm} |
| 2 | {Description of issue} | {How it was resolved} | {+Xm} |

---

## Deviations from Design

| Deviation | Reason | Impact |
|-----------|--------|--------|
| {What changed from DESIGN} | {Why it changed} | {Effect on system} |

---

## Blockers (if any)

| Blocker | Required Action | Owner |
|---------|-----------------|-------|
| {Description} | {What needs to happen} | {Who can unblock} |

---

## Contrato de aceite (C2) e avaliador de contexto fresco (C1)

> Gate de ativação: manifest toca **≥2 camadas** (`sql` · `edge` · `front` · `scripts` · `harness`).
> 1 camada → as duas linhas abaixo recebem `N.A. (1 camada)`.

**Camadas do manifest:** {n} ({lista})
**Contrato de aceite (Step 1.5):** {n propostas / n aceitas — seção `## Contrato de aceite` do DESIGN} | já negociado em {data} | N.A. (1 camada)
**Veredito do avaliador (C1):** {PASS | NEEDS_WORK | N.A. (1 camada)} · ciclos: {n} · achados: {n} · `AVALIACAO_{FEATURE}_{YYYYMMDD-HHMM}.md`

> O hook `build-report-guard` nega `PASS`/`NEEDS_WORK` sem o `AVALIACAO_*.md` existente em
> `sdd/reviews/`. A contagem de achados é insumo da medição P2→P3 (§6.3 do PLANO).

---

## Acceptance Test Verification

> **Default-FAIL (D1):** todo AT **nasce `false`**. `true` exige evidência que o hook
> `.githooks/claude-build-report-guard.py` consegue abrir — contrato em
> [`fragments/EVIDENCIA.md`](fragments/EVIDENCIA.md). Formas aceitas: `` `evidence/{FEATURE}/AT-nnn.log` ``
> (1ª linha `$ cmd`, output verbatim) · `` `AVALIACAO_{FEATURE}_{ts}.md` `` (provado pelo
> avaliador) · `recibo: {nome} {YYYY-MM-DD}` (gate `manual-ux`). "Por raciocínio" é negado.

| ID | Critério (EARS, verbatim do DEFINE) | Resultado | Evidência |
|----|-------------------------------------|-----------|-----------|
| AT-001 | {When …, the system shall …} | false | — |
| AT-002 | {If …, then the system shall …} | false | — |
| AT-003 | {While …, the system shall …} | false | — |

**Verify Gate (`sdd/bin/verify-gate.sh <DEFINE>`):** exit {n} · `evidence/{FEATURE}/GATE.log`

---

## Performance Notes

| Metric | Expected | Actual | Status |
|--------|----------|--------|--------|
| {Metric 1} | {From DEFINE} | {Measured} | ✅ / ❌ |
| {Metric 2} | {From DEFINE} | {Measured} | ✅ / ❌ |

---

## Final Status

### Overall: {✅ COMPLETE / 🔄 IN PROGRESS / ❌ BLOCKED}

**Completion Checklist:**

- [ ] All tasks from manifest completed
- [ ] All verification checks pass
- [ ] All tests pass
- [ ] No blocking issues
- [ ] Acceptance tests verified — todo `true` com evidência lida (nenhum "por raciocínio")
- [ ] Avaliador de contexto fresco: PASS (ou N.A. 1 camada) com `AVALIACAO_*.md` persistido
- [ ] Ready for /release

---

## Next Step

**If Complete:** `/release <descrição do que liberar>`

**If Blocked:** Resolve blockers, then `/build` to resume

**If Issues Found:** `/iterate DESIGN_{FEATURE}.md "{change needed}"`
