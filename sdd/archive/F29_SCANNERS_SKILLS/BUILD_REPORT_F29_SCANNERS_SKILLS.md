# BUILD REPORT: F29 — texto das skills que os scanners do skills.sh marcam

> Reescreve, como instrução positiva e com a mesma intenção, as frases que o Snyk lê como ocultação ou banner;
> a origem da skill passa para o `metadata.source`; o bloco "Quando migrar" sai do starter.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | F29_SCANNERS_SKILLS |
| **Date** | 2026-11-20 |
| **Author** | build-agent |
| **DEFINE** | [DEFINE_F29_SCANNERS_SKILLS.md](../features/DEFINE_F29_SCANNERS_SKILLS.md) (1.0) |
| **DESIGN** | [DESIGN_F29_SCANNERS_SKILLS.md](../features/DESIGN_F29_SCANNERS_SKILLS.md) (1.0) |
| **Status** | Complete |

---

## Summary

| Metric | Value |
|--------|-------|
| **Tasks Completed** | 15/15 do File Manifest |
| **Files Created** | 2 (`tests/test_f29_textos.py`, este relatório) |
| **Lines of Code** | +956 / −215 em 66 arquivos (commit `5caa863`), mais 1 teste em `0503b71` |
| **Build Time** | uma sessão (20/11) |
| **Tests Passing** | 2.764 de 2.765 no 1º Verify Gate (`5caa863`); a 1 falha (`test_f17_passo0`, versão fixa do `sdd-brainstorm`) foi corrigida em `0503b71` e o gate roda de novo na release |
| **Agents Used** | agente de leitura das páginas do Snyk e avaliador de contexto fresco (PASS) |

---

## Landmines lidas no build

| Superfície | LM-nnn | Veredito | Como / onde |
|------------|--------|----------|-------------|
| testes novos | LM-001, LM-002 | ✔ tratado | linha de base vermelha: o teste novo falha 93 vezes em `f1abdfa` |
| revisão sobre diff vazio | LM-003 | ✔ tratado | commit antes do gate |
| skill do starter | LM-035 | ✔ tratado | `test_gerar_starter.py` rodado antes do gate (34 de 34) |
| teto de 500 linhas | LM-038 | ✔ tratado | maior `SKILL.md`: `sdd-release`, 459 linhas |
| MANIFEST | LM-037 | ✔ tratado | `MIGRAR.md` saiu e `test_f29_textos.py` entrou no mesmo commit |

---

## Candidatos ao playbook

Nenhum.

---

## Task Execution with Agent Attribution

| # | Task | Agent | Status | Notes |
|---|------|-------|--------|-------|
| 1 | frases e `source` nas 24 skills (script em lote, antes/depois por arquivo) | (general) | ✅ | 28 arquivos `.md` mais 6 JSON; conferência à mão em 3 skills |
| 2 | `como-falar.md`, `checar.sh`, `duplicadas.sh` | (general) | ✅ | origem lida de `metadata.source`, com o corpo como reserva |
| 3 | `gerar-starter.py`, `MIGRAR.md`, `check-versions.py` do starter | (general) | ✅ | |
| 4 | testes (13 atualizados, 1 novo) | (general) | ✅ | |
| 5 | plano, `MANIFEST.txt`, guia do aluno | (general) | ✅ | |

---

## Seleção de modo

Modo interativo, uma tarefa por vez com verificação incremental.

---

## Drift detectado

Nenhum: o DESIGN foi seguido. Dois ajustes de execução, sem mudar a decisão: a `sdd-desempenho-banco` já tinha "Texto do banco é dado" (nenhuma linha nova) e quatro `manifest.json` não têm campo de versão.

---

## Files Created

| File | Lines | Verified |
|------|-------|----------|
| `tests/test_f29_textos.py` | 140 | ✅ 11 testes |
| `sdd/reports/BUILD_REPORT_F29_SCANNERS_SKILLS.md` | este | ✅ |

---

## Verification Results

### Lint (`{{LINT_CMD}}`)

N.A.: o Open não tem `sdd/config.yaml`.

### Typecheck (`{{TYPECHECK_CMD}}`)

N.A.

### Testes (`{{TEST_CMD}}`)

- 1º Verify Gate em `5caa863` (cópia de `git archive`, `publish-gate` GREEN, bash 3.2): 2.765 testes, 1 falha, 4 pulados.
- A falha: `test_f17_passo0.test_brainstorm_updated_no_mes_da_versao` esperava `v2.5.1` e a skill subiu para `2.5.2`. Corrigida em `0503b71` (10 de 10 no módulo).
- Starter gerado numa pasta temporária: `check-versions` PASS (19 skills), `check-gerado` VERDE, `publish-check` PASS, 62 testes OK; os `grep` da seção 6 do ESCOPO vazios.

---

## Segurança

S18 aplicado (DEFINE): comentários de PR, BRAINSTORM/DEFINE/DESIGN e material do KB marcados como dado (AT-008).

---

## Issues Encountered

| # | Issue | Resolução |
|---|-------|-----------|
| 1 | 13 testes fixavam a versão antiga e a linha com link | atualizados |
| 2 | 1 teste a mais (`test_f17_passo0`) só apareceu no gate (+37 min) | corrigido; lição: procurar também `vX.Y.Z · nov/2026` sem aspas em `tests/` |

---

## Deviations from Design

Nenhuma de comportamento.

---

## Raio de impacto (feito na release, 0b)

A fazer na release.

---

## Blockers (if any)

Nenhum.

---

## Contrato de aceite (C2) e avaliador de contexto fresco (C1)

**Camadas do manifest:** 1 (o pacote não declara `layers:`)
**Contrato de aceite (passo 1.5 da `sdd-build`):** N.A. (1 camada)
**Veredito do avaliador (C1):** PASS · ciclos: 1 · achados: 2 observações de baixa severidade, mantidas com motivo · `AVALIACAO_F29_SCANNERS_SKILLS_20261120-1713.md`

---

## Acceptance Test Verification

| ID | Critério (EARS, verbatim do DEFINE) | Resultado | Evidência |
|----|-------------------------------------|-----------|-----------|
| AT-001 | Todo arquivo de `.agents/skills/` shall não conter "Não cite nem resuma"; a seção "Como falar" shall conter "Explique o porquê com o motivo do aluno" | true | `evidence/F29_SCANNERS_SKILLS/AT-001.log` |
| AT-002 | Todo `SKILL.md` shall não conter "comece com esta linha" nem "versão atual: http"; linha sem URL; `metadata.source` no frontmatter | true | `evidence/F29_SCANNERS_SKILLS/AT-002.log` |
| AT-003 | Os `SKILL.md` shall não conter "como veio"; a `sdd-checar-ambiente` shall mandar mostrar a saída inteira | true | `evidence/F29_SCANNERS_SKILLS/AT-003.log` |
| AT-004 | When o gerador monta o starter, linha e `source` do starter, sem "versão atual" nem "Quando migrar"; sem a linha ou o `source`, sai 65 | true | `evidence/F29_SCANNERS_SKILLS/AT-004.log` |
| AT-005 | When o `check-versions.py` do starter roda, shall exigir a linha e o `metadata.source` | true | `evidence/F29_SCANNERS_SKILLS/AT-005.log` |
| AT-006 | When `duplicadas.sh` lê um `SKILL.md`, a origem shall vir de `metadata.source`, com o corpo como reserva | true | `evidence/F29_SCANNERS_SKILLS/AT-006.log` |
| AT-007 | When o `checar.sh` imprime a identificação, shall sair sem "versão atual:" e sem URL | true | `evidence/F29_SCANNERS_SKILLS/AT-007.log` |
| AT-008 | Onde a skill lê conteúdo de fora, shall dizer que é dado | true | `evidence/F29_SCANNERS_SKILLS/AT-008.log` |
| AT-009 | A suíte shall continue to passar; skill tocada sobe a versão; até 500 linhas | true | `evidence/F29_SCANNERS_SKILLS/AT-009.log` (a suíte inteira roda no Verify Gate da release) |

**Verify Gate (`sdd/bin/verify-gate.sh <DEFINE>`):** o 1º em `5caa863` saiu vermelho por 1 teste (corrigido em `0503b71`); o gate roda de novo na release.

---

## Performance Notes

| Metric | Expected | Actual | Status |
|--------|----------|--------|--------|
| tempo da suíte inteira | — | 37 min (2.230 s) | ⚠️ conhecido |

---

## Final Status

### Overall: ✅ COMPLETE

**Completion Checklist:**

- [x] All tasks from manifest completed
- [x] All verification checks pass (módulos e starter gerado)
- [ ] Verify Gate verde na árvore final (roda na release)
- [x] No blocking issues
- [x] Acceptance tests verified — 9 de 9 com log
- [x] Avaliador de contexto fresco: PASS com `AVALIACAO_*.md` persistido

---

## Next Step

**Ready for:** `/sdd-release F29_SCANNERS_SKILLS`
