# BUILD REPORT: F6 Docs do sdd-open

> Implementation report for F6 Docs do sdd-open

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | F6_DOCS |
| **Date** | 2026-10-29 |
| **Author** | SDD Build by RDD |
| **BRAINSTORM** | `sdd/features/BRAINSTORM_F6_DOCS.md` |
| **DEFINE** | `sdd/features/DEFINE_F6_DOCS.md` (v1.1) |
| **DESIGN** | `sdd/features/DESIGN_F6_DOCS.md` (v1.1) |
| **UX REVIEW** | não se aplica (DEFINE, Clarifications) |
| **Status** | Complete |

- **Branch:** `feat/f6-docs`, sobre `7e19462` (= `v2.2.6`).
- **Commits:**
  - `963c47e` — build;
  - `aaae1b4` — notas do ciclo 1 da revisão de contexto fresco;
  - `1c9bbc7` — notas do ciclo 2.
- **Escopo:** 23 arquivos do produto (4 novos, 19 alterados), `git diff --stat v2.2.6 HEAD` → 1394 inserções, 41 remoções (`sdd/reports/evidence/F6_DOCS/escopo.log`).
- **Fontes:** `/Users/robertoduarte/rdd-public/sdd-starter/docs/guia-do-aluno.pt-BR.md` (494 linhas, não rastreado, só lido), `docs/quickstart.pt-BR.md` e `skills/sdd-release/SKILL.md` do starter.
- **Revisões de contexto fresco:**
  - do DESIGN, antes do build: `sdd/reviews/REVISAO_DESIGN_F6_DOCS_20261029.md`;
  - do build: `sdd/reviews/AVALIACAO_F6_DOCS_20261029-ciclo1.md` e `…-ciclo2.md`.

---

## Mode Selection

| Signal | Observation |
|---|---|
| Manifest files | 26 linhas: 23 arquivos do produto (4 novos, 19 alterados) e 3 scripts de evidência fora do commit |
| Cross-file coupling | Alto no texto: guia, quickstarts, READMEs e `AGENTS.md.tmpl` repetem os mesmos nomes e frases fixas que o `test_docs.py` confere |
| Security surface | Nenhuma em runtime. Os riscos são de publicação (PII nos docs, Unicode invisível nas skills), cobertos pelo publish-gate e pelo `codepoints.log` |
| LLM prompt items | None (`LLM Prompts: false`) |
| Independent volume | Baixo |
| Context-rot risk | Médio: a sessão foi do brainstorm ao build; mitigado pelos artefatos e por 3 revisões de contexto fresco |
| Runtime capabilities | default e subagente disponíveis; o modo briefs não foi oferecido |

**Recommendation:** default.

**User decision:** default. O Roberto pediu "execute o design, review do design, build, review do build" em sequência; o modo foi registrado, não perguntado.

**Pre-build review:** Sim, a revisão do DESIGN em contexto fresco (NEEDS_WORK: 3 HIGH, 4 MEDIUM, 3 LOW, todas aplicadas antes do build; DESIGN e DEFINE v1.1).

---

## Summary

| Metric | Value |
|---|---|
| Arquivos novos | 4: `docs/pt-BR/guia-do-aluno.md`, `docs/roadmap.md`, `docs/pt-BR/roadmap.md`, `tests/test_docs.py` |
| Arquivos alterados | 19: 7 `SKILL.md` de fase, `AGENTS.md.tmpl`, 2 READMEs, 2 quickstarts, 2 comparison, 2 adaptation-guide, 2 testes de versão, `MANIFEST.txt` |
| Testes | 499 → 514 no piso (`tests/test_docs.py`, 15 métodos, com subtestes por idioma e por skill) |
| Correções de P1 achadas no caminho | 3: links quebrados e frase falsa no `adaptation-guide` (EN/PT); passo 5 dos quickstarts ensinava uma atualização que não atualiza; modos "continuar × entregar" do handoff do starter, que o open não tem |
| Release | `v2.2.7` automática (decisão do Roberto no brainstorm), publicada em 2026-10-30 sobre `1c9bbc7` |

---

## Task Execution

| # | Task | Status | Notes |
|---|---|---|---|
| 1 | `tests/test_docs.py` | Done | Escrito primeiro: 25 falhas no baseline; reforçado nos 2 ciclos |
| 2–3 | `adaptation-guide` EN/PT | Done | Link do slot de landmines para `sdd/config.example.yaml`; o slot sai vazio |
| 4–5 | Roadmaps EN/PT | Done | Tabela com 7 linhas, sem data |
| 6–7 | `comparison` EN/PT | Done | "roadmap" vira link; tabela intocada |
| 8–9 | Quickstarts EN/PT | Done | Regra, 4 validações, tabela "onde roda" no passo 4; passo 5 por `doctor` + apagar + `init --yes` + `sync --yes` |
| 10 | Guia do aluno | Done | 10 blocos, 17 fichas, 7 agentes; 8 afirmações corrigidas nos 2 ciclos |
| 11–12 | READMEs | Done | "The 17 skills", KB, OK único, guia e roadmap |
| 13 | `AGENTS.md.tmpl` | Done | Linhas Antes e KB, `kb-dominios.py`, regra 7 |
| 14–20 | 7 seções "Por que cada regra existe" | Done | Patch nas 7; 3 itens reescritos no ciclo 1 |
| 21–22 | Testes de versão | Done | `test_contrato_build_release` (2), `test_correcoes_w0` (1) |
| 23 | `MANIFEST.txt` | Done | +4 linhas, ordem `LC_ALL=C` |
| 24–26 | Scripts de evidência | Done | `comandos-intactos.py` com 2 provas; 4 sabotagens; `gerar-evidencia.sh` |

---

## Files Changed

| File | Action | Purpose |
|---|---|---|
| `tests/test_docs.py` | Created | Links e âncoras (caixa exata), guia, quickstarts, roadmaps, comparison, README/`AGENTS.md.tmpl`, seção nas 9 skills |
| `docs/pt-BR/guia-do-aluno.md` | Created | Guia do aluno adaptado ao open |
| `docs/roadmap.md` | Created | Roadmap EN |
| `docs/pt-BR/roadmap.md` | Created | Roadmap PT |
| `docs/quickstart.md`, `docs/pt-BR/quickstart.md` | Modified | Passo 4 (regra, validações, tabela) e passo 5 (P1) |
| `docs/comparison.md`, `docs/pt-BR/comparison.md` | Modified | Link do roadmap |
| `docs/adaptation-guide.md`, `docs/pt-BR/adaptation-guide.md` | Modified | P1: link e frase do slot de landmines |
| `README.md`, `README.pt-BR.md` | Modified | As 17 skills, KB, OK único, docs novos |
| `AGENTS.md.tmpl` | Modified | Preparo, KB, `kb-dominios.py`, regra 7 |
| `SKILL.md` de `sdd-brainstorm`, `sdd-define`, `sdd-governanca`, `sdd-ux-review`, `sdd-design`, `sdd-build`, `sdd-release` (em `.agents/skills/`) | Modified | Seção nova; 2.1.1 · 2.3.1 · 2.2.1 · 2.3.1 · 2.1.1 · 2.2.1 · 2.3.1 |
| `tests/test_contrato_build_release.py`, `tests/test_correcoes_w0.py` | Modified | Versões fixadas novas |
| `MANIFEST.txt` | Modified | 4 arquivos novos |

---

## Drift Detected

| # | Drift | Decisão |
|---|---|---|
| 1 | O `adaptation-guide` (EN/PT) tinha 2 links quebrados e dizia que um script de landmines vinha no pacote | Achado no design; corrigido como P1 (DESIGN Decision 7) |
| 2 | O passo 5 dos quickstarts dizia que `git pull` + `sync` atualizava a skill | Achado na revisão do DESIGN (H2); corrigido como P1 (Decision 2) |
| 3 | A ficha da `sdd-handoff` do starter falava em modos "continuar × entregar", que o open não tem | Achado no build, antes do commit; a ficha descreve a skill do open |
| 4 | 3 testes fixavam versão de skill | Previsto no DESIGN (manifest 21, 22) |

Nenhum prompt de runtime; nenhum arquivo fora do manifest.

---

## Verification Results

### Incremental Verification

| Task | Command / Method | Result | Evidence |
|---|---|---|---|
| Base antes de tocar em nada | suíte inteira no piso em `7e19462` (cópia por `git archive`) | Pass | 499 OK (A-001 do DEFINE; rodado na sessão antes do build) |
| Baseline vermelha | `test_docs.py` novo na árvore `v2.2.6` | Pass (vermelho esperado) | `sdd/reports/evidence/F6_DOCS/baseline.log` |
| Baseline das notas do ciclo 1 | `test_docs.py` corrigido contra os docs de `963c47e` | Pass (vermelho esperado) | `sdd/reports/evidence/F6_DOCS/baseline-notas.log` |
| Baseline das notas do ciclo 2 | `afirma_sdd_fora_do_git()` de `aaae1b4` × corrigida, nas 4 paráfrases | Pass (vermelho → verde) | `sdd/reports/evidence/F6_DOCS/baseline-notas2.log` |
| Passos intactos | `comandos-intactos.py` (extração + texto normalizado) | Pass | `sdd/reports/evidence/F6_DOCS/comandos-intactos.log` |
| Contratos byte a byte | `git diff --stat v2.2.6 HEAD` de `sdd/bin`, `sdd/fixtures`, `sdd/templates`, `sdd/playbook.md`, `sdd/config.example.yaml`, `scripts`, `bin`, `.github` + `playbook-lint --self-test` | Pass | `sdd/reports/evidence/F6_DOCS/contratos-intactos.log` |
| Code points das 7 seções | Python com `unicodedata` | Pass | `sdd/reports/evidence/F6_DOCS/codepoints.log`: 0 invisíveis |
| Versões | `check-versions.py --base v2.2.6 --base-obrigatoria` | Pass | `sdd/reports/evidence/F6_DOCS/check-versions.log` |

### Verify Gate

| Attribute | Value |
|---|---|
| **Kind** | test |
| **Command / Method** | `bash sdd/bin/verify-gate.sh --strict sdd/features/DEFINE_F6_DOCS.md`. O `cmd` faz a cópia por `git archive HEAD`, roda o `publish-gate.sh` em modo `ci` e a suíte no piso |
| **Exit / Result** | 0 em `963c47e` (513 testes), `aaae1b4` (514) e `1c9bbc7` (G1–G5 verdes; `Ran 514 tests … OK`) |
| **Status** | Green |
| **Evidence** | `sdd/reports/evidence/F6_DOCS/GATE.log` |

### Manual UX Receipt

N/A

### Complementary Checks

| Check | Command / Method | Status | Evidence |
|---|---|---|---|
| Lint | `python3 sdd/bin/skill-lint.py --conversa .agents/skills/sdd-*/SKILL.md` (17) | Pass | `sdd/reports/evidence/F6_DOCS/skill-lint-conversa.log` |
| Tamanho das skills | `wc -l .agents/skills/sdd-*/SKILL.md` (maior: 376) | Pass | `sdd/reports/evidence/F6_DOCS/linhas.log` |
| Typecheck | N/A (Markdown e Python sem anotação verificada) | N/A | — |
| Tests | os 7 módulos tocados, `-v` | Pass | `sdd/reports/evidence/F6_DOCS/testes-f6.log` |
| Build / Compile | publish-gate em modo `ci`, dentro do gate | Pass | `sdd/reports/evidence/F6_DOCS/GATE.log` |

---

## Acceptance Test Verification

| ID | Scenario | Status | Evidence |
|---|---|---|---|
| AT-001 | Guia: 10 blocos, 17 fichas, 7 agentes, `init --vendors`/`--yes`/`python3`/`doctor`, apagar + `init`, releases do open | Pass | `sdd/reviews/AVALIACAO_F6_DOCS_20261029-ciclo2.md` |
| AT-002 | Guia sem as premissas do starter (npx, 15 skills, layout plano, `sdd/` fora do git em 7 redações, `registra e libera`) e sem os literais do W0 | Pass | `sdd/reports/evidence/F6_DOCS/testes-f6.log` |
| AT-003 | Quickstarts: regra, ≥ 4 validações, tabela e 7 agentes no passo 4, `doctor` e `init` no passo 5, sem Lovable | Pass | `sdd/reports/evidence/F6_DOCS/testes-f6.log` |
| AT-004 | Roadmaps: cabeçalho, 6 temas planejados, deltas em avaliação, sem ano | Pass | `sdd/reports/evidence/F6_DOCS/testes-f6.log` |
| AT-005 | `comparison`: deltas ❌ em avaliação na célula do SDD Open | Pass | `sdd/reports/evidence/F6_DOCS/testes-f6.log` |
| AT-006 | READMEs: 17 skills, `kb-dominios.py`, OK único, guia, roadmap, link cruzado | Pass | `sdd/reports/evidence/F6_DOCS/testes-f6.log` |
| AT-007 | `AGENTS.md.tmpl`: 5 skills, `sdd/bin/kb-dominios.py`, "um OK só", marcador de vendors; agnóstico verde | Pass | `sdd/reports/evidence/F6_DOCS/testes-f6.log` |
| AT-008 | Link ou âncora inexistente, ou caixa errada, reprova com `arquivo:linha → alvo` | Pass | `sdd/reports/evidence/F6_DOCS/sabotagem.log` |
| AT-009 | Seção ausente, repetida ou com < 3 itens reprova nomeando a skill (9 skills) | Pass | `sdd/reviews/AVALIACAO_F6_DOCS_20261029-ciclo2.md` |
| AT-010 | Seção antes de Encerramento; patch no frontmatter e na identificação; `skill-lint --conversa` 0 | Pass | `sdd/reports/evidence/F6_DOCS/check-versions.log` |
| AT-011 | Texto das 7 skills igual à `v2.2.6` fora da seção e da versão | Pass | `sdd/reports/evidence/F6_DOCS/comandos-intactos.log` |
| AT-012 | `check-versions --base v2.2.6 --base-obrigatoria` → 0 | Pass | `sdd/reports/evidence/F6_DOCS/check-versions.log` |
| AT-013 | 499 testes de antes, caminhos intocados byte a byte, ≤ 500 linhas, publish-gate `ci` | Pass | `sdd/reports/evidence/F6_DOCS/GATE.log` |
| AT-014 | 3 sabotagens do `test_docs.py` (+1 do `comandos-intactos.py`) vermelhas; clone limpo verde | Pass | `sdd/reports/evidence/F6_DOCS/sabotagem.log` |

Os 14 ATs também foram provados por execução pelos 2 avaliadores. O ciclo 2 deu PASS: `sdd/reviews/AVALIACAO_F6_DOCS_20261029-ciclo2.md`.

---

## Advisor Ledger

**Revisão do DESIGN (pré-build):** NEEDS_WORK, `sdd/reviews/REVISAO_DESIGN_F6_DOCS_20261029.md`. As 10 notas estão no Advisor Ledger do DESIGN v1.1: todas APPLIED (a M4 pela regra 7 no `AGENTS.md.tmpl`).

**Veredito do avaliador:** PASS — ciclo 2 sobre `aaae1b4`, `sdd/reviews/AVALIACAO_F6_DOCS_20261029-ciclo2.md` (0 HIGH, 0 MEDIUM, 6 LOW novos). O ciclo 1, sobre `963c47e`, deu NEEDS_WORK: `sdd/reviews/AVALIACAO_F6_DOCS_20261029-ciclo1.md`.

Revisão pós-build por avaliador em contexto fresco, numa worktree destacada. Cada HIGH foi reproduzido antes da correção.

| # | Phase | Note | Severity | Decision | Evidence |
|---:|---|---|---|---|---|
| H1 | ciclo 1 | "é dado fictício (ela registra e libera)": a skill troca o número por um inválido | HIGH | APPLIED | guia, seção 8 e ficha; `registra e libera` em `PROIBIDO_NO_GUIA`; `baseline-notas.log`. `aaae1b4` |
| H2 | ciclo 1 | a ficha da `sdd-design` dizia que ela devolve o Define com dúvida | HIGH | APPLIED | quem segura é o Verify Gate (exit 5). `aaae1b4` |
| H3 | ciclo 1 | item "nenhum corte é inventado" na `sdd-brainstorm`, regra que a skill não tem | HIGH | APPLIED | item reescrito sobre o passo 5. `aaae1b4` |
| M1 | ciclo 1 | o `doctor` não vê o starter global | MEDIUM | APPLIED | FAQ do guia; os quickstarts no ciclo 2 (L6). `aaae1b4`, `1c9bbc7` |
| M2 | ciclo 1 | "sdd/ fora do git" só pegava 2 frases | MEDIUM | APPLIED | regex sem caixa por parágrafo + autoteste com as 2 frases do starter. `aaae1b4` |
| M3 | ciclo 1 | atualização do guia sem `sdd/bin/` | MEDIUM | APPLIED | passo 2–4 do guia e seção 8. `aaae1b4` |
| L1 | ciclo 1 | link com caixa errada passava no macOS | LOW | APPLIED | `existe()` com `os.listdir`; autoteste `C.md` |
| L2 | ciclo 1 | `sync` sem `--yes` | LOW | APPLIED | guia e quickstarts; linha do CANCELADO |
| L3 | ciclo 1 | "não encerra sem mudar nada" | LOW | APPLIED | "encerra sem publicar" |
| L4 | ciclo 1 | "quebra quem lê, sem erro visível" | LOW | APPLIED | item cita o `design-lint` |
| L5 | ciclo 1 | rótulo do bloco do OK com `?` na seção da release | LOW | APPLIED | item reescrito |
| L6 | ciclo 1 | `=` do plano, doctor × release publicada, "prepare once" com a new-session | LOW | APPLIED | guia e READMEs |
| L1' | ciclo 2 | "copia de volta só o que você apagou" | LOW | APPLIED | o `init` também atualiza o trecho do `AGENTS.md`. `1c9bbc7` |
| L2' | ciclo 2 | regra do doctor trocada (skill por versão, `sdd/bin/` por bytes) | LOW | APPLIED | guia e quickstarts. `1c9bbc7` |
| L3' | ciclo 2 | "o do Verify Gate" em python | LOW | APPLIED | Define, design, relatório. `1c9bbc7` |
| L4' | ciclo 2 | regex de "sdd/ fora do git" deixava 4 paráfrases | LOW | APPLIED | 4 redações na regex e no autoteste; `baseline-notas2.log`. `1c9bbc7` |
| L5' | ciclo 2 | alarme também recusa planilha nova | LOW | APPLIED | seção 8 do guia. `1c9bbc7` |
| L6' | ciclo 2 | quickstarts: "o doctor avisa se detectar os dois" | LOW | APPLIED | EN e PT. `1c9bbc7` |

Contagem de achados: DESIGN 10, ciclo 1 12, ciclo 2 6 (todos LOW). Os 6 LOW do ciclo 2 foram aplicados sem novo ciclo: são texto, e o gate e a evidência rodaram de novo sobre `1c9bbc7`.

---

## Issues Encountered

| Issue | Resolution |
|---|---|
| A 1ª gravação do `GATE.log` saiu sem a linha `exit=`: o shell da sessão é zsh, sem `PIPESTATUS` | O gate entrou no `gerar-evidencia.sh`, que roda em bash |
| A normalização do `comandos-intactos.py` deixava uma linha em branco a mais | Defeito do script de evidência, não da skill; corrigido antes de qualquer conclusão |
| A sonda do baseline do L4' perdeu as crases nas aspas do shell | Refeita com `baseline-notas2.py` em arquivo |

---

## Deviations from Design

| Deviation | Reason |
|---|---|
| `sabotagem.sh` com 4 casos (o DESIGN previa 3) | O 4º prova que o próprio `comandos-intactos.py` acusa uma mudança em prosa (só a 2ª prova, a do texto inteiro, pega) |
| `test_docs.py` com `existe()` de caixa exata e a regex ampliada | Notas L1 e M2/L4' dos avaliadores |
| O guia ganhou o caminho de atualização com `sdd/bin/` e `sync --yes` | Notas M3 e L2 do ciclo 1 |

---

## Blockers

Nenhum.

---

## Final Status

### Overall: COMPLETE

- Verify Gate `--strict` verde sobre `1c9bbc7`; `report-lint` e `validate_build_report` rodados sobre este arquivo.
- Avaliador de contexto fresco: PASS no ciclo 2, sem HIGH aberto.
- Âncoras no GitHub (A-002): os 43 títulos do guia têm, na página da branch do PR, a mesma âncora que o `ancora()` do teste gera; as 10 do sumário abrem (`sdd/reports/evidence/F6_DOCS/links-pr.log`).
- PR: https://github.com/robertodiasduarte/sdd-open/pull/8, CI verde em `ubuntu-latest` e `macos-latest` (run 40984992013, `ci-pr.log`).
- Release: bloco do OK apresentado; OK do Roberto citando "sdd-open" em 2026-10-30; push fast-forward `7e19462..1c9bbc7` em `main`. Run `release` 41025735985 verde (testes, testes no piso macOS, publicar), `publish-gate` 41025736350 verde; `v2.2.7` aponta para `1c9bbc7` com `sdd-open-v2.2.7.tar.gz` e `SHA256SUMS.txt`, e `shasum -a 256 -c` dá OK (`sdd/reports/evidence/F6_DOCS/release.log`).

---

## Next Step

Execute o **SDD Handoff by RDD**.
