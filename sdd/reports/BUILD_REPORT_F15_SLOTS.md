# BUILD REPORT: F15 Slots — smoke visual na release, teste do diff antes do OK e checagem de migration antes do apply

> Relatório do build da F15_SLOTS (L0 + L3 + L4 do inventário de saída da F15), no SDD Open

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | F15_SLOTS |
| **Date** | 2026-11-10 |
| **Author** | build-agent (worktree `sdd-open-f15-slots`, branch `feat/f15-slots`, base `9d8ac24` = `v2.7.2`) |
| **DEFINE** | [DEFINE_F15_SLOTS.md](../features/DEFINE_F15_SLOTS.md) (v1.2) |
| **DESIGN** | [DESIGN_F15_SLOTS.md](../features/DESIGN_F15_SLOTS.md) (v1.5) |
| **Status** | Complete |

---

## Seleção de modo

`default` (um autor), escolhido pelo Roberto em 2026-11-09: os 21 arquivos dividem o mesmo contrato (exits do `slot.sh`, nomes dos slots, textos das skills que os testes conferem). Revisão do DESIGN: exigida (`sdd-fluxo.sh review-design` 0, 3 arquivos novos), feita por agente fresco (20 notas, todas aplicadas; Advisor Ledger do DESIGN).

---

## Summary

| Metric | Value |
|--------|-------|
| **Tasks Completed** | 21/21 (manifest do DESIGN v1.5) |
| **Files Created** | 3 (`sdd/bin/slot.sh`, `tests/test_slot.py`, `tests/test_f15_slots_textos.py`) · 18 alterados |
| **Lines of Code** | +1.171 / −30 em 21 arquivos (`git diff --shortstat origin/main..HEAD`), 7 commits `9747f9b..45e27a9` |
| **Build Time** | 2026-11-09 a 2026-11-10 |
| **Tests Passing** | 1.717/1.717 (1 skipped, como na `v2.7.2`), `evidence/F15_SLOTS/GATE-45e27a9.log` |
| **Agents Used** | 4 frescos (revisor do DESIGN, governança, avaliador ciclos 1 e 2) |

---

## Landmines lidas no build

| Superfície | LM-nnn | Veredito | Como / onde |
|------------|--------|----------|-------------|
| `tests/test_slot.py` (gate que só confere fiação) | LM-001 | ✔ tratado | o executor roda com scripts falsos dos dois lados; 14 mutantes morrem por asserção nomeada (`evidence/F15_SLOTS/SABOTAGENS.log`) |
| testes novos (asserção sem base vermelha) | LM-002 | ✔ tratado | cada leva de testes rodou antes contra o código anterior: `BASELINE-RED.log` (9d8ac24), `BASELINE-RED-ciclo2.log` (9747f9b), `BASELINE-RED-revisao.log` (d6c5ed1), `BASELINE-RED-revisao2.log` (9013b10), `BASELINE-RED-revisao3.log` (2c9b6ad) |
| revisão sobre árvore commitada | LM-003 | ✔ tratado | toda revisão e avaliação rodou sobre commit, com `avaliador-guard.sh` verde antes |
| `aplicar-migration.md` §2b | LM-004 | ✔ tratado | a checagem vem antes da prévia e não substitui a prova por leitura |
| `test-baseline.sh` (heurística sobre texto) | LM-005 | ✔ tratado | o casamento por substring do teste tocado direto não mudou; os vizinhos usam âncora (S6 e S10 provam) |
| gate sem `.git` | LM-006 | ✔ tratado | o `slot.sh` funciona sem git (`test_sem_git_funciona_com_commit_vazio`); todo teste confere o exit exato |

---

## Candidatos ao playbook

```text
<<<CANDIDATO_PLAYBOOK
secao: Reviews / harness
sup: `git checkout` `mutante` `sabotagem` `não commitado`
regra: Script de sabotagem que desfaz cada mutante com `git checkout -- <arquivo>` apaga junto todo conserto ainda não commitado naquele arquivo; os mutantes seguintes "não aplicam" e o resumo mente. **Do instead:** o script recusa rodar com mudança rastreada não commitada (`git status --porcelain --untracked-files=no` vazio) e o conserto é commitado antes da sabotagem.
evidencia: sdd/reports/evidence/F15_SLOTS/SABOTAGENS.log (o script com a trava); o incidente está em ## Issues Encountered deste relatório, linha 3
ficha: —
mordeu_antes: —
>>>
```

```text
<<<CANDIDATO_PLAYBOOK
secao: Reviews / harness
sup: `openrouter` `teto` `timeout` `saldo`
regra: Uma engine da OpenRouter que passa do teto de tempo do registry é cobrada mesmo sem resposta (a F15_SLOTS perdeu ~US$ 1 com um 2º revisor que estourou 900 s). **Do instead:** antes da rodada, confira o saldo em `/credits` e prefira, no papel de 2º revisor, um modelo já medido abaixo do teto; registre o saldo antes e depois no ledger da revisão.
evidencia: sdd/reports/reviews/EXTERNAL_REVIEW_20261110-055845/META.txt (revisor2_segundos 900, revisor2_custo $?) e o saldo medido antes (US$ 2,39) e depois (US$ 1,32) em ## Issues Encountered
ficha: —
mordeu_antes: —
>>>
```

---

## Task Execution with Agent Attribution

| # | Task | Agent | Status | Duration | Notes |
|---|------|-------|--------|----------|-------|
| 1 | testes novos, vermelhos contra `9d8ac24` | (direct) | ✅ Complete | — | 38 testes, 42 falhas/erros; os 2 de não regressão já verdes |
| 2 | `sdd/bin/slot.sh` | (direct) | ✅ Complete | — | Decisions 1–5 |
| 3 | `sdd/bin/test-baseline.sh` | (direct) | ✅ Complete | — | Decision 8 |
| 4 | config, release, build, docs, contratos, MANIFEST | (direct) | ✅ Complete | — | Decisions 6, 7, 9 |
| 5 | versões fixadas nos testes antigos (2.9.0, 2.7.0, 26 perguntas, `smoke.` fora do proibido da F13) | (direct) | ✅ Complete | — | manifest #15–19, #21 |
| 6 | sabotagens | (direct) | ✅ Complete | — | 14/14 mortas (`evidence/F15_SLOTS/SABOTAGENS.log`) |
| 7 | consertos do avaliador (ciclos 1 e 2) e da revisão paga (rodadas 1 a 3) | (direct) | ✅ Complete | — | `d6c5ed1`, `f3d1d54`, `9013b10`, `cd18e59`, `2c9b6ad`, `45e27a9` |

**Legend:** ✅ Complete | 🔄 In Progress | ⏳ Pending | ❌ Blocked

---

## Agent Contributions

| Agent | Files | Specialization Applied |
|-------|-------|------------------------|
| (direct) | 21 | DESIGN patterns only |

---

## Files Created

| File | Lines | Agent | Verified | Notes |
| ---- | ----- | ----- | -------- | ----- |
| `sdd/bin/slot.sh` | 232 | (direct) | ✅ | executor dos 4 slots |
| `sdd/bin/test-baseline.sh` | +41 −5 | (direct) | ✅ | teste ao lado da fonte |
| `sdd/config.example.yaml` | +20 | (direct) | ✅ | seções `smoke:` e `schema:` |
| `.agents/skills/sdd-release/SKILL.md` | +42 −11 | (direct) | ✅ | 2.9.0; 492 linhas (teto 500) |
| `.agents/skills/sdd-release/references/como-falar.md` | +16 −1 | (direct) | ✅ | pergunta D1 do smoke; exemplo do bloco |
| `.agents/skills/sdd-build/SKILL.md` | +5 −4 | (direct) | ✅ | 2.7.0 |
| `.agents/skills/sdd-build/references/aplicar-migration.md` | +25 | (direct) | ✅ | §2b |
| `docs/adaptation-guide.md` · `docs/pt-BR/adaptation-guide.md` | +25 · +24 | (direct) | ✅ | seção dos 4 slots |
| `docs/cli-conventions.md` | +3 −1 | (direct) | ✅ | linha do `slot.sh` |
| `sdd/WORKFLOW_CONTRACTS.yaml` | +26 | (direct) | ✅ | contrato `slot` |
| `MANIFEST.txt` | +3 | (direct) | ✅ | 3 arquivos novos |
| `tests/test_slot.py` · `tests/test_f15_slots_textos.py` | 25 testes · 18 testes | (direct) | ✅ | AT-001 a AT-005 · AT-008 a AT-011 |
| `tests/test_test_baseline.py` | +70 | (direct) | ✅ | AT-006, AT-007 |
| `tests/test_contrato_build_release.py`, `test_correcoes_w0.py`, `test_f14_textos.py`, `test_f14_drive_textos.py`, `test_f13_textos.py`, `test_decisoes_lint.py` | ±1–2 cada | (direct) | ✅ | versões e contagens fixadas |

---

## Verification Results

### Lint Check

```text
python3 sdd/bin/skill-lint.py --conversa .agents/skills/sdd-release/SKILL.md .agents/skills/sdd-build/SKILL.md → 0
python3 scripts/check-versions.py --base v2.7.2 → PASS (19 skills com versão coerente)
bash sdd/bin/sdd-decisoes-lint.sh --sites .agents/skills → 26 pergunta(s) em 21 arquivo(s)
/bin/bash -n sdd/bin/slot.sh sdd/bin/test-baseline.sh → 0
python3 sdd/bin/design-lint.py sdd/features/DESIGN_F15_SLOTS.md → DESIGN válido
```

**Status:** ✅ Pass

### Type Check

```text
N/A — o Open não tem typecheck_cmd
```

**Status:** ⏭️ Skipped

### Tests

```text
Verify Gate (git archive, publish-gate em modo ci, bash 3.2, Python 3.9): Ran 1717 tests — OK (skipped=1) — exit 0
```

| Test | Result |
|------|--------|
| `tests/test_slot.py` (25) | ✅ Pass |
| `tests/test_test_baseline.py` (19) | ✅ Pass |
| `tests/test_f15_slots_textos.py` (18) | ✅ Pass |
| suíte inteira (1.717) | ✅ Pass |

**Status:** ✅ 1717/1717 Pass

---

## Advisor Ledger

**Consulta:** delivery-review · 2026-11-10 · `sdd/bin/adversarial-review.sh` (pastas em `sdd/reports/reviews/`), 4 rodadas; a 4ª (`EXTERNAL_REVIEW_20261110-070608`, `diff_sha256 1fbc689e…`) é a do código final `45e27a9`
**VERDICT do advisor:** rodada 1 PAROU (auditor sem cota) · rodada 2 REVIEW COMPLETA, 0/0/2 + 1 novo · rodada 3 REVIEW COMPLETA, 0 graves, 1 médio, 2 leves · rodada 4 REVIEW COMPLETA, 0 graves, 1 médio, 1 leve + 1 novo do auditor (os 3 rebatidos por medição; sem conserto, a revisão vale para o código final)
**Proveniência:** revisor claude (`claude-opus-5-5`); auditor previsto codex, sem cota nas 3 rodadas (`auditor_motivo: codex falhou (cota, cobrança ou erro)`), trocado pela reserva openrouter `qwen/qwen3.7-plus` (troca registrada no META); 2º revisor (gatilho: 21 arquivos, limiar 8): gemini sem credencial (rodada 1), `deepseek/deepseek-v4-pro` passou do teto de 900 s (rodada 2), `z-ai/glm-5.3` respondeu na rodada 3 e falhou na 4 (`cota, cobrança ou erro`): a rodada final precisa da dispensa do 2º revisor no `--conferir`, decisão da release

| # | Nota | Severidade | Veredito | Evidência |
|---|------|-----------|----------|-----------|
| 1 | r1·R1: o `trap` vinha depois da leitura do config; um sinal nessa janela saía 130/143 | LOW | APLICADA | commit `f3d1d54` (trap logo depois das flags) |
| 2 | r1·R2: com `before_ok` vazio, a pasta comum nunca era limpa | LOW | APLICADA | commit `f3d1d54`; `test_before_ok_vazio_tambem_esvazia` |
| 3 | r1·R3: id relativo à subpasta do runner escapava do vizinho | LOW | APLICADA | commit `f3d1d54`; `test_touched_id_relativo_a_subpasta_conta`; S10 |
| 4 | r2·R1: comando terminado em `;`, `&` ou `|` fazia o slot sair 0 com o smoke reprovado | LOW | APLICADA | commit `cd18e59`; 4 casos em `test_config_que_nao_da_para_rodar_e_64`; S12 |
| 5 | r2·R2: arquivo, `--arvore` e `--dir` relativos eram lidos da raiz | LOW | APLICADA | commit `cd18e59`; `test_caminhos_relativos_valem_de_onde_foi_chamado`; S13 |
| 6 | r2·N1 (auditor): `declare -f` preservaria comentários e a checagem de `#` nunca reprovaria | HIGH | REBATIDA_EVIDENCIA | `sdd/reports/evidence/F15_SLOTS/REVIEW-N1-declare-f.log`: no bash 3.2, `bash x.sh 0 # gate` vira `bash x.sh 0` sem `"$@"`; `sdd/bin/slot.sh:180` reprova; `test_config_que_nao_da_para_rodar_e_64` (caso "comentario do shell") e S9 provam |
| 7 | r3·R1@claude: o `declare -f` põe `2>&1`, `>` e `<` depois do `"$@"`; comando válido saía 64 | MED | APLICADA | commit `45e27a9`; `test_redirecao_no_fim_roda`; S14 |
| 8 | r3·R2@claude: a lista anti-termos omitia arquivos do diff | LOW | APLICADA | commit `45e27a9`; `SemProjetoPrivado.ARQUIVOS` com os 21 e isenções nomeadas |
| 9 | r3·R1@glm: `-h` imprimia `set -uo pipefail` | LOW | APLICADA | commit `45e27a9`; `test_ajuda_mostra_so_o_cabecalho` |
| 10 | r4·R1: falha de carga do teste ao lado escaparia como "fora do diff" | MED | REBATIDA_EVIDENCIA | `sdd/reports/evidence/F15_SLOTS/REVIEW-R4-medicoes.log`: a linha não é reconhecida e o script sai `INCONCLUSIVO` (3), que a release trata como WAIVABLE, nunca verde; ignorar linha não reconhecida ao lado de outra falha é do parser da F7 (`sdd/bin/test-baseline.sh:146-176`), fora desta frente; o auditor deu DISAGREE_CONCERN |
| 11 | r4·R2: sufixo do vizinho conta teste homônimo de outro pacote | LOW | REBATIDA_ESCOPO | limite declarado no cabeçalho (`sdd/bin/test-baseline.sh:18-19`) e na Decision 8; erra para o lado seguro; o auditor deu DISAGREE_EVIDENCE |
| 12 | r4·N1 (auditor): o `eval` com quebra de linha protegeria o `"$@"` só na checagem, e na execução real o `#` descartaria os arquivos | HIGH | REBATIDA_EVIDENCIA | `sdd/reports/evidence/F15_SLOTS/REVIEW-R4-medicoes.log`: `bash e.sh 0 # gate` sai 64; `bash e.sh 0 a#b` roda com `args=[a#b f1.sql]`; a quebra vem depois do `"$@"` e não muda se ele é comentado (`sdd/bin/slot.sh:178-181`) |

---

## Issues Encountered

| # | Issue | Resolution | Time Impact |
|---|-------|------------|-------------|
| 1 | O revisor fresco do DESIGN achou uma ref de projeto privado que eu tinha posto no critério anti-RDD do DEFINE (nunca commitado nem enviado) | retirada; o termo privado fica só no `PUBLISH_GATE_EXTRA_PATTERNS`; os 3 documentos limpos de caminho do privado | +10m |
| 2 | Os testes de texto não esperavam o recuo nem a quebra de linha do bloco do OK | o teste normaliza espaços antes de comparar | +5m |
| 3 | O script de sabotagem desfez com `git checkout` consertos ainda não commitados (`slot.sh`, `test-baseline.sh`) | restaurados das cópias de `/tmp/novo.*` e conferidos pelos testes; o script agora recusa rodar com árvore suja (candidato ao playbook) | +15m |
| 4 | Codex sem cota nas 4 rodadas; gemini sem credencial; deepseek estourou o teto e foi cobrado (~US$ 1; saldo US$ 2,39 → 1,32); glm falhou na rodada 4 | auditor na reserva qwen; 2º revisor trocado por `z-ai/glm-5.3` dentro da escolha D3 do Roberto (OpenRouter); a dispensa do 2º revisor da rodada 4 é pergunta da release | +45m |
| 5 | `gate-shell-evidencia.sh` acusou `AVAL-AT011-TERMOS.log` (avaliador, ciclo 1): o `[exit=0]` era de um formatador | o original ficou intacto como `AVAL-AT011-TERMOS.orig.txt`; o build refez a mesma medição sem pipe, com a origem dita na 2ª linha do log novo; a guarda sai VERDE em 50 logs | +10m |

---

## Deviations from Design

| Deviation | Reason | Impact |
|-----------|--------|--------|
| comentário do shell decidido pelo próprio bash (`declare -f`), não por `shlex`/varredura em Python | avaliação ciclo 2, achado 1 (`$'it\'s' # c` passava; `a\ #b` era recusado) | mais exato; o `bash -n` antes garante que a checagem não executa nada (`test_comando_nao_escapa_da_checagem`) |
| `slot.sh` recusa valor de flag que começa com `--`, texto depois das aspas YAML e separador no fim; caminhos relativos valem de onde foi chamado | avaliação ciclo 1, revisão rodadas 2 e 3 | 3 causas de 64 a mais, cada uma com teste e a causa conferida na mensagem |
| `tests/test_decisoes_lint.py` no manifest (#21) | a pergunta D1 nova sobe a contagem fixada de 25 para 26 | DESIGN v1.2 |

---

## Blockers (if any)

Nenhum.

---

## Contrato de aceite (C2) e avaliador de contexto fresco (C1)

**Camadas do manifest:** 0 de `layers:` (o próprio Open não preenche `layers:`); scripts, skills, docs e testes
**Contrato de aceite (passo 1.5 da `sdd-build`):** N.A. (1 camada) — a revisão fresca do DESIGN cobriu o aceite (DEFINE v1.1)
**Veredito do avaliador (C1):** PASS · ciclos: 2 · achados: 3 no ciclo 1 (1 médio), 4 baixos no ciclo 2 · `AVALIACAO_F15_SLOTS_20261110-0542.md` (ciclo 1: `AVALIACAO_F15_SLOTS_20261109-2227.md`, NEEDS_WORK). Rodado por decisão D3 do Roberto, apesar da regra de camadas dar N.A.

---

## Acceptance Test Verification

| ID | Critério (EARS, verbatim do DEFINE) | Resultado | Evidência |
|----|-------------------------------------|-----------|-----------|
| AT-001 | **When** `slot.sh <chave> …` roda com o slot preenchido, … 0 ⇒ OK · 2 ⇒ REPROVOU · 10 ⇒ NADA A MEDIR, com `→` | true | `evidence/F15_SLOTS/AT-001.log` · `AVALIACAO_F15_SLOTS_20261110-0542.md` |
| AT-002 | **If** o comando sai fora de {0, 2, 10} ou o `slot.sh` recebe INT/TERM, **then** … INCONCLUSIVO, 3 | true | `evidence/F15_SLOTS/AT-002.log` · `AVALIACAO_F15_SLOTS_20261110-0542.md` |
| AT-003 | **Where** a chave está vazia, ausente ou sem config, … PULADO, 11 | true | `evidence/F15_SLOTS/AT-003.log` · `AVALIACAO_F15_SLOTS_20261110-0542.md` |
| AT-004 | **If** chave desconhecida, flag sem valor, ref que não resolve, aspas sem fechar, `bash -n` ou `#` do shell, **then** … 64 sem rodar | true | `evidence/F15_SLOTS/AT-004.log` · `AVALIACAO_F15_SLOTS_20261110-0542.md` |
| AT-005 | **While** o comando roda, … as 6 variáveis `SDD_*` e a pasta comum | true | `evidence/F15_SLOTS/AT-005.log` · `AVALIACAO_F15_SLOTS_20261110-0542.md` |
| AT-006 | **When** `--touched` roda e o diff altera uma fonte com teste ao lado, … sai 2 | true | `evidence/F15_SLOTS/AT-006.log` · `evidence/F15_SLOTS/BASELINE-RED.log` |
| AT-007 | O `test-baseline.sh` **shall continue to** tratar como fora do diff a falha sem relação … | true | `evidence/F15_SLOTS/AT-007.log` · `AVALIACAO_F15_SLOTS_20261110-0542.md` |
| AT-008 | A `sdd-release` **shall** rodar os testes do diff no 0a e os 3 smokes nos itens 6b, 7b e 10 … | true | `evidence/F15_SLOTS/AT-008.log` |
| AT-009 | O bloco do OK **shall continue to** ter os mesmos rótulos … e a linha Verificações nova | true | `evidence/F15_SLOTS/AT-009.log` |
| AT-010 | O passo 4b **shall** rodar `schema.check_cmd` antes da prévia, fail-closed, com o log | true | `evidence/F15_SLOTS/AT-010.log` · `AVALIACAO_F15_SLOTS_20261110-0542.md` |
| AT-011 | config, guias, cli-conventions, contrato e MANIFEST; texto novo sem termo de projeto privado | true | `evidence/F15_SLOTS/AT-011.log` |

**Verify Gate (`sdd/bin/verify-gate.sh <DEFINE>`):** exit 0 · `evidence/F15_SLOTS/GATE-45e27a9.log`

---

## Drift detectado

nenhum — o Open não tem `deploy.drift_check_cmd`; o produto só chega a quem instala por release.

---

## Performance Notes

| Metric | Expected | Actual | Status |
|--------|----------|--------|--------|
| suíte no gate | ≥ 1.669 testes (v2.7.2) | 1.714 | ✅ |
| sabotagens | 1 por entrega (L0, L3, L4) | 14 mortas de 14 | ✅ |

---

## Final Status

### Overall: ✅ COMPLETE

**Completion Checklist:**

- [x] All tasks from manifest completed
- [x] All verification checks pass
- [x] All tests pass
- [x] No blocking issues
- [x] Acceptance tests verified — todo `true` com evidência lida (nenhum "por raciocínio")
- [x] Avaliador de contexto fresco: PASS com `AVALIACAO_*.md` persistido
- [x] Ready for /release

---

## Next Step

**If Complete:** `/sdd-release F15_SLOTS — slots de smoke e de checagem de schema, testes do diff antes do OK (v2.8.0)`
