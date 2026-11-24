# BUILD REPORT: F30 — Qualidade do código gerado · fatia S1 (itens 1, 3, 4)

> Lint e tipos a cada tarefa do Build com evidência conferida pelo `report-lint.py`, regras de qualidade por stack no
> AGENTS.md e no texto da build do starter, e sugestão do linter da stack quando o projeto não tem um, sem instalar nada.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | F30_QUALIDADE_CODIGO (fatia S1) |
| **Date** | 2026-11-23 |
| **Author** | build-agent |
| **DEFINE** | [DEFINE_F30_QUALIDADE_CODIGO.md](../features/DEFINE_F30_QUALIDADE_CODIGO.md) (1.3) |
| **DESIGN** | [DESIGN_F30_QUALIDADE_CODIGO.md](../features/DESIGN_F30_QUALIDADE_CODIGO.md) (1.1) |
| **Status** | Complete |

---

## Summary

| Metric | Value |
|--------|-------|
| **Tasks Completed** | 21/21 do File Manifest (o item 21, `gerar-starter.py`, conferido sem mudança) |
| **Files Created** | 7 (catálogo, `qualidade-regras.sh`, 5 módulos `tests/test_f30_*.py`) e este relatório |
| **Lines of Code** | +1.485 / −48 em 34 arquivos em `07198f3`, mais 5 commits de correção da revisão e do raio de impacto até `76827bf` |
| **Build Time** | uma sessão (23/11) |
| **Tests Passing** | 52 testes novos (`test_f30_*`), todos vermelhos na árvore anterior (`git archive` de `cb3ac3c`) e verdes em `07198f3`; suíte inteira no Verify Gate (abaixo) |
| **Agents Used** | revisores externos do DESIGN e do código (openrouter `qwen/qwen3.7-plus`, codex, auditor claude) e avaliador de contexto fresco |

---

## Landmines lidas no build

| Superfície | LM-nnn | Veredito | Como / onde |
|------------|--------|----------|-------------|
| gate e testes novos | LM-001, LM-002 | ✔ tratado | os 5 módulos novos falham na árvore anterior (13+18+10+2+7 falhas/erros); o gate exige os 5 arquivos por `test -f`, porque o discover vazio do Python 3.9 sai 0 |
| revisão sobre diff vazio | LM-003 | ✔ tratado | código commitado (`07198f3`) antes da revisão externa |
| duas cópias do mesmo dado | LM-005 | ✔ tratado | um leitor do catálogo; tabela de ferramentas do `checar.sh` com teste de paridade; ponteiro do AGENTS.md e `ler_mapa` com teste que compara as cópias |
| restauração de arquivo | LM-009 | ✔ tratado | baseline do `report-lint` com cópia de segurança e `cmp` depois; os outros baselines numa cópia de `git archive` |
| `subprocess` e Windows | LM-014, LM-029, LM-042 | ✔ tratado | testes pelos ajudantes de `tests/apoio.py` (`Sandbox.roda`, `BASH`) e as bases de `test_checar`/`test_gerar_starter` |
| saída do script novo | LM-015 | ✔ tratado | `qualidade-regras.sh` reconfigura stdout/stderr no início |
| caminho de reserva | LM-017, LM-019 | ✔ tratado | ponteiro com 3 testes de causa (catálogo ausente, fora do formato, sem Python); `sdd_python_pronto` sem `2>/dev/null` |
| `[exit=` do log | LM-018 | ✔ tratado | logs gravados por script `bash` com `rc=$?`; o `report-lint` recusa `[exit=]` vazio |
| starter | LM-035 | ✔ tratado | catálogo e `MODO_WEB.md` sem `sdd/bin/`; `test_gerar_starter.py` 34/34 e `test_f17c_gerador.py` 7/7 antes do gate |
| MANIFEST | LM-037 | ✔ tratado | 7 arquivos novos no `MANIFEST.txt` no mesmo commit |
| teto de 500 linhas | LM-038 | ✔ tratado | `sdd-build` 369, `MODO_WEB.md` 488, `sdd-new-session` 444, `sdd-checar-ambiente` 344; `test_conversa.py` 19/19 |
| contagem de perguntas | LM-044 | ✔ tratado | `test_decisoes_lint` 40 → 41 no mesmo commit |

---

## Candidatos ao playbook

```text
<<<CANDIDATO_PLAYBOOK
secao: Reviews / harness
sup: `unittest discover` `Ran 0 tests` `python 3.9` `verify-gate` `test -f`
texto: No Python 3.9 (o /usr/bin/python3 do macOS), `unittest discover` sem nenhum teste que case o padrão sai 0 ("Ran 0 tests … OK"); um Verify Gate que só roda `discover -p 'test_fNN_*.py'` fica verde antes de o teste existir. **Do instead:** o gate confere a existência de cada módulo de teste da feature (`test -f`) antes do discover, e o baseline vermelho é conferido rodando o gate na árvore de antes.
evidencia: sdd/features/DEFINE_F30_QUALIDADE_CODIGO.md (Verify Gate, nota de baseline)
>>>
```

---

## Task Execution with Agent Attribution

| # | Task | Agent | Status | Notes |
|---|------|-------|--------|-------|
| 1 | catálogo de qualidade (`web/references/`) | (general) | ✅ | 12 regras (6 gerais, 6 de stack) e 5 fichas de ferramenta |
| 2 | `sdd/bin/qualidade-regras.sh` | (general) | ✅ | `--stack`, `--regras`, `--agents`; 64 com a causa |
| 3–4 | `AGENTS.md.tmpl` e `bin/sdd-open.sh` | (general) | ✅ | `gerar_qualidade_agents`, no molde da segurança |
| 5 | `report-lint.py` | (general) | ✅ | `check_lint` com o log de antes (revisão do DESIGN, N1) |
| 6–7 | `sdd-build/SKILL.md` e `web/MODO_WEB.md` | (general) | ✅ | versão 2.15.0 |
| 8–9 | `BUILD_REPORT_TEMPLATE.md`, `fragments/EVIDENCIA.md` | (general) | ✅ | |
| 10–12 | `checar.sh`, `sdd-checar-ambiente` 1.8.0, `sdd-new-session` 1.8.0 | (general) | ✅ | aviso, `--linter`, pergunta `[D2]` |
| 13 | `sdd/config.example.yaml` | (general) | ✅ | comentários dos 2 slots |
| 14–18 | 5 módulos `tests/test_f30_*.py` | (general) | ✅ | 52 testes |
| 19–20 | `test_decisoes_lint.py`, `MANIFEST.txt` | (general) | ✅ | |
| 21 | `scripts/gerar-starter.py` | (general) | ✅ | sem mudança: o modo cita o catálogo e o gerador o copia (Decision 1) |
| — | fora do manifest: versões fixas em 9 testes antigos e o recorte do bloco de segurança em `test_sdd_open.py` | (general) | ✅ | consequência das versões novas e do bloco novo logo depois do de segurança |

---

## Seleção de modo

Sinais: 21 itens, um mantenedor, ambiente com subagentes. Recomendação: `default` (sequencial). Decisão: `default`,
pela autorização do Roberto em 23/11 de seguir o pipeline com as recomendações.

---

## Drift detectado

- O AT-007 dizia "a tabela de tradução tem a linha do aviso novo". A tabela é do `--frente`, e o `--frente` não fala de linter (Decision 6). A tradução ficou no passo dos slots; o DEFINE foi para a versão 1.3.
- O `test_sdd_open.py` (`SegurancaNoAgents`) recortava o bloco de segurança até "Agentes preparados". O bloco de qualidade entra nesse meio, e o recorte passou a ir até `### Qualidade ao construir`.

---

## Files Created

| File | Lines | Verified | Notes |
|------|-------|----------|-------|
| `.agents/skills/sdd-build/web/references/CATALOGO_QUALIDADE.md` | 120 | ✅ | |
| `sdd/bin/qualidade-regras.sh` | 260 | ✅ | |
| `tests/test_f30_report_lint.py` · `test_f30_textos.py` · `test_f30_agents_qualidade.py` · `test_f30_checar_linter.py` · `test_f30_starter.py` | — | ✅ | 15 + 8 + 15 + 11 + 3 testes |

---

## Verification Results

### Lint (`{{LINT_CMD}}`)

O pacote não tem `sdd/config.yaml`: os slots `project.lint_cmd` e `project.typecheck_cmd` estão vazios.

lint: slot vazio

### Testes (`{{TEST_CMD}}`)

Ver o Verify Gate em Acceptance Test Verification.

---

## Segurança

N.A. na S1 (DEFINE: sem login, rota, dado de terceiros ou chamada paga). O `checar.sh` continua só lendo: o AT-006
confere o hash da árvore antes e depois.

---

## Issues Encountered

| # | Issue | Resolution | Time Impact |
|---|-------|------------|-------------|
| 1 | O gemini não tinha credencial na revisão do DESIGN (exit 65) | o revisor foi o openrouter (`qwen/qwen3.7-plus`), com o saldo conferido antes em `/credits` (US$ 10,18; LM-008) | ~2 min |
| 2 | A revisão do DESIGN achou 2 defeitos médios (N1, N2) | aplicados antes do código: log de antes e tipos sem arquivos anexados | — |

---

## Deviations from Design

| Deviation | Reason | Impact |
|-----------|--------|--------|
| A sugestão do `checar.sh` é calculada numa variável, não num arquivo temporário | um nome fixo no `/tmp` poderia virar um link (o mesmo cuidado do `checar.sh:103`) | nenhum |
| O catálogo ganhou a ficha `sql` em Ferramentas, com `lint: —` | a detecção de stack do script lê só as fichas; `sql` serve só para escolher regras | nenhum |

---

## Raio de impacto (feito na release, 0b)

3 agentes frescos, um por superfície, só leitura, com o brief `sdd-release/references/raio-de-impacto.md`. Nenhum
consumidor quebrado e nenhuma invariante violada (INV-001 e INV-002 não tocam os módulos).

| Superfície | Consumidores lidos | Resultado | Tratado |
|---|---|---|---|
| `report-lint.py` (`check_lint`) | pre-commit, `sdd-report-guard.py`, `sdd-drive.sh`, `sdd-release` 0a.5, `gate-shell-evidencia.sh`, docs de hooks, 8 módulos de teste (178 testes OK) | ok | `docs/hooks.md` e `docs/pt-BR/hooks.md` citam o log de lint no conserto da regra REPORT (`7eee8d7`) |
| bloco `### Qualidade ao construir` do AGENTS.md | sed do template, merge entre marcadores, `sync --check`, doctor, teto do arquivo de contexto, CLAUDE.md/GEMINI.md, testes de texto do template | ok | a mensagem do `--regras` com só um slot vazio mandava escrever `lint: slot vazio`: corrigida, com teste |
| `checar.sh` (`--linter`, ⚠️) e versões 1.8.0 / 1.8.0 / 2.15.0 | doctor (`--segredo`), new-session, iniciar-repo (`--frente`), gerador do starter e trocas, check-versions do starter, `test_checar` (137 testes OK com os vizinhos) | ok | a new-session confere a versão da checar antes do `--linter` (a anterior à 1.8.0 rodaria o diagnóstico com rede) |

Pendências que ficam (não quebram nada): o doctor pula em silêncio um arquivo novo de `sdd/bin` ausente num projeto
atualizado só com `sync` (anterior à F30; nesta release ele avisa pela versão da `sdd-build` e pelo `report-lint.py`
mudado); a frase do item 5 da `sdd-release` não cita o log de lint (a tabela de abortar cobre; skill a 41 linhas do
teto); o diagnóstico normal rodado no próprio repositório do Open mostra o ⚠️ de Python (sem `sdd/config.yaml`).

---

## Blockers (if any)

Nenhum.

---

## Contrato de aceite (C2) e avaliador de contexto fresco (C1)

**Camadas do manifest:** 1 (o pacote não declara `layers:`)
**Contrato de aceite (passo 1.5 da `sdd-build`):** N.A. (1 camada)
**Veredito do avaliador (C1):** PASS_PENDENTE_RECIBO · ciclos: 2 · achados: ciclo 1 NEEDS_WORK por 1 item (AT-006, PHP sem `php -l`: o AT foi emendado, DEFINE 1.4); ciclo 2 sem achado de código, só o recibo da suíte, que é o Verify Gate em `dac782a` · `AVALIACAO_F30_QUALIDADE_CODIGO_20261123-2050.md` (ciclo 1: `AVALIACAO_F30_QUALIDADE_CODIGO_20261123-2035.md`)

---

## Acceptance Test Verification

| ID | Critério (EARS, resumido do DEFINE) | Resultado | Evidência |
|----|-------------------------------------|-----------|-----------|
| AT-001 | When o `report-lint` confere um relatório com o slot cheio, shall exigir `LINT.log`/`TIPOS.log` com o comando do slot e `[exit=0]` (dívida antiga provada pelo log de antes: aviso) | true | `evidence/F30_QUALIDADE_CODIGO/AT-001.log` |
| AT-002 | While os dois slots estão vazios, shall aprovar, com aviso se faltar a linha `lint: slot vazio` | true | `evidence/F30_QUALIDADE_CODIGO/AT-002.log` |
| AT-003 | When a tarefa chega ao verificar, o texto da `sdd-build` shall nomear os 2 slots, os arquivos da tarefa, a escada, os logs e a linha do slot vazio | true | `evidence/F30_QUALIDADE_CODIGO/AT-003.log` |
| AT-004 | When `init`/`sync` gera o AGENTS.md, shall escrever `### Qualidade ao construir` com as gerais e as da stack; 1 bloco depois de 2 `sync` | true | `evidence/F30_QUALIDADE_CODIGO/AT-004.log` |
| AT-005 | If o catálogo falta, está fora do formato ou não há Python, then shall ficar o ponteiro e o aviso com a causa | true | `evidence/F30_QUALIDADE_CODIGO/AT-005.log` |
| AT-006 | When o `checar.sh` roda numa stack sem linter, shall sugerir o padrão da stack sem gravar nada (hash igual) | true | `evidence/F30_QUALIDADE_CODIGO/AT-006.log` |
| AT-007 | When a `sdd-new-session` acha os slots sem evidência, shall rodar `--linter` e perguntar `[D2]`, gravando só com o sim | true | `evidence/F30_QUALIDADE_CODIGO/AT-007.log` |
| AT-008 | When o gerador monta o starter, a `sdd-build` dele shall trazer as regras e o catálogo, sem `sdd/bin/`, e passar nos grep da F29 | true | `evidence/F30_QUALIDADE_CODIGO/AT-008.log` |
| AT-009 | The system shall continue to passar a suíte inteira, o `publish-gate` e o `check-versions`, com o bloco de segurança igual | true | `evidence/F30_QUALIDADE_CODIGO/GATE_S1_76827bf.log` |

**Verify Gate (`bash sdd/bin/verify-gate.sh sdd/features/DEFINE_F30_QUALIDADE_CODIGO.md`):** exit 0 em `76827bf` (o commit que sobe, registrado na 2ª linha do log): grep da F29 vazio, `check-versions` VERDE, `publish-gate` em modo CI verde sobre a cópia de `git archive`, os 5 `test_f30_*` (54 testes) e a suíte inteira, 2.819 testes, OK (4 pulados), com `/bin/bash` 3.2 e `/usr/bin/python3` 3.9. Um gate anterior, em `07198f3`, também saiu verde (2.817 testes, `GATE_S1.log`); os de `dac782a`, `7eee8d7`, `bb32004` e `d94bb8b` foram interrompidos de propósito, porque o código mudou antes de terminarem.

---

## Performance Notes

| Metric | Expected | Actual | Status |
|--------|----------|--------|--------|
| tempo do Verify Gate inteiro | — | 31 min (1.857 s) | ✅ |

---

## Advisor Ledger

O ledger completo, uma linha por achado, está em `sdd/reviews/LEDGER_REVISAO_F30_QUALIDADE_CODIGO.md` (o
`ledger-revisao-lint.sh` dá VERDE). Resumo:

| Rodada | Commit | Achados | Decisão |
|---|---|---|---|
| D1 (DESIGN) | `c539af3` | 2 MED do auditor (queda do lint para o projeto inteiro; tipos com arquivos anexados) | 2 APLICADA (DESIGN 1.1) |
| 1 | `07198f3` | 2 MED (a 1ª linha idêntica impedia a dívida antiga; o log final era só da última tarefa) | 2 APLICADA (`dac782a`) |
| 2 | `7eee8d7` | 1 MED (o lint de antes com arquivos que ainda não existem) | APLICADA (`bb32004`) |
| 3 | `bb32004` | 1 MED (manifest só de arquivos novos ficava sem log de antes) e 1 LOW (o `find` sem as pastas dos agentes) | 2 APLICADA (`d94bb8b`) |
| 4 | `d94bb8b` | 2 MED (exit 127 valia como dívida; `npx eslint .` com arquivos conferia o projeto inteiro) | 2 APLICADA (`76827bf`) |
| 5 | `76827bf` | 1 MED (relatório feito antes da v2.26.0 num projeto com `lint_cmd` cheio) | REBATIDA_ESCOPO: o conserto é 1 comando que o próprio `report-lint` imprime; vai como nota de atualização |

Revisores: openrouter `qwen/qwen3.7-plus` nas 6 rodadas (0 achados próprios, salvo o LOW da rodada 3), codex
`gpt-6.1-sol` como 2º revisor no DESIGN, auditor claude em todas; `diversidade: vendor`. O gemini caiu por
credencial antes da D1. Custo: US$ 0,49 (DESIGN) + 0,73 + 0,80 + 0,82 + 0,88 + 0,81 (código) = US$ 4,53.
`review_externo`: `EXTERNAL_REVIEW_20261123-212910`, sha256 igual ao do código que sobe (`--conferir`: CONFERE).

---

## Final Status

### Overall: ✅ COMPLETE

**Completion Checklist:**

- [x] All tasks from manifest completed
- [x] Testes novos vermelhos na árvore anterior e verdes na nova
- [x] Verify Gate verde no commit que sobe (`76827bf`)
- [x] No blocking issues
- [x] Acceptance tests verified — 9 de 9 com log
- [x] Avaliador de contexto fresco com `AVALIACAO_*.md` persistido

---

## Next Step

**Ready for:** `/sdd-release F30_QUALIDADE_CODIGO`
