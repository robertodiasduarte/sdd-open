# BUILD REPORT: F4 Conversa do sdd-open

> Implementation report for F4 Conversa do sdd-open

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | F4_CONVERSA |
| **Date** | 2026-10-29 |
| **Author** | SDD Build by RDD |
| **BRAINSTORM** | `sdd/features/BRAINSTORM_F4_CONVERSA.md` |
| **DEFINE** | `sdd/features/DEFINE_F4_CONVERSA.md` (v1.2) |
| **DESIGN** | `sdd/features/DESIGN_F4_CONVERSA.md` (v1.1) |
| **Status** | Complete |

- **Branch:** `feat/f4-conversa`, sobre `dd27ef6` (M1, com o produto da `v2.2.4`).
- **Commits:** `4e77a1f` (build), `fd94876` (notas do ciclo 1 da revisão de contexto fresco) e `2fcdda1` (notas do ciclo 2).
- **PR:** https://github.com/robertodiasduarte/sdd-open/pull/6.
- **Fonte do texto:** `/Users/robertoduarte/rdd-public/sdd-starter` em `17c69c4`, com as seções e os `como-falar.md` de 7 skills.

---

## Mode Selection

| Signal | Observation |
|---|---|
| Manifest files | 36 linhas: 35 arquivos novos e 27 alterados contra a `v2.2.4` |
| Cross-file coupling | Alto. As 14 skills dividem o mesmo bloco de regras e o mesmo fragmento, e os 3 lints dividem a interface |
| Security surface | Baixa. Texto de skill e lints que só leem o arquivo indicado; sem rede nem segredo |
| LLM prompt items | None (`LLM Prompts: false`) |
| Independent volume | Médio (14 `como-falar.md`), mas a redação precisa ser a mesma em todos |
| Context-rot risk | Médio: sessão longa, do brainstorm à release. Mitigado pelos artefatos e por 2 ciclos de revisão fresca |
| Runtime capabilities | default e ralph (subagente) disponíveis; briefs não oferecido |

**Recommendation:** default. Um autor mantém o bloco comum igual nas 14 skills.

**User decision:** default (Roberto, 2026-10-29).

**Pre-build review:** Não (Roberto). A revisão pós-build de contexto fresco continuou obrigatória.

---

## Summary

| Metric | Value |
|---|---|
| **Tasks Completed** | 36/36 |
| **Files Created** | 35 |
| **Files Modified** | 27 |
| **Files Deleted** | 0 |
| **Verification Commands Run** | Baseline vermelha 2×, suíte inteira no piso 4×, Verify Gate 2×, `gerar-evidencia.sh` 2× (11 logs), sabotagem 3× (6 alvos), sonda de mutantes do avaliador 1× (27 alvos) e conferência de code points 2× |
| **Verify Gate** | Green |
| **Execution Mode** | default |

São 388 testes: 326 de antes e 62 novos. Ficam verdes no `/usr/bin/python3` 3.9.6 com `/bin/bash` 3.2.57, dentro do gate e fora dele.

---

## Task Execution

| # | Manifest ID | Task | Executor | Status | Verification | Evidence |
|---:|---:|---|---|---|---|---|
| 1 | 4, 7, 10, 11, 14, 29–31, 33 | Testes primeiro, vermelhos sem o código | build-agent | Complete | 78 FAIL e 34 ERROR em 114 testes antes do código | `evidence/F4_CONVERSA/baseline.log` |
| 2 | 1 | `PERGUNTA_DECISAO.md` | build-agent | Complete | `test_conversa.Fragmento` | `evidence/F4_CONVERSA/testes-f4.log` |
| 3 | 2, 3 | `skill-lint --conversa` + 7 fixtures | build-agent | Complete | As 2 skills portadas passam sem edição; 6 fixtures saem 1 e o controle 0 | `evidence/F4_CONVERSA/testes-f4.log` |
| 4 | 5, 6 | `design-lint.py` + `DESIGN_VALIDO.md` | build-agent | Complete | 4 DESIGN reais saem 0; o template cru sai 1 | `evidence/F4_CONVERSA/design-lint-reais.log` |
| 5 | 8, 9 | `handoff-lint.py` + `HANDOFF_VALIDO.md` | build-agent | Complete | Fixture 0; template cru 1 | `evidence/F4_CONVERSA/testes-f4.log` |
| 6 | 12, 13 | Os 2 nomes de ferramenta nos templates | build-agent | Complete | `test_agnostico` verde no HEAD, vermelho na `v2.2.4` | `evidence/F4_CONVERSA/baseline-agnostico.log` |
| 7 | 15–28 | As 14 skills: seção, `como-falar.md`, identificação, versão; passo 8 da design, 3b da handoff, Status na checar-ambiente | build-agent | Complete | `skill-lint --conversa` 16/16; comandos intactos | `evidence/F4_CONVERSA/skill-lint-conversa.log`, `evidence/F4_CONVERSA/comandos-intactos.log` |
| 8 | 32–35 | CI com `--conversa`, `cli-conventions.md`, `CONTRIBUTING.md` | build-agent | Complete | `test_release_workflow` | `evidence/F4_CONVERSA/testes-f4.log` |
| 9 | 36 | `MANIFEST.txt` (+35, ordem `LC_ALL=C`) | build-agent | Complete | G3 do publish-gate nos dois sentidos | `evidence/F4_CONVERSA/GATE.log` |

---

## Files Changed

| File | Lines | Agent | Verified | Notes |
|---|---:|---|---|---|
| `sdd/templates/fragments/PERGUNTA_DECISAO.md` | 92 | build-agent | ✅ | Novo |
| `sdd/bin/skill-lint.py` | +117 −5 | build-agent | ✅ | `--conversa` |
| `sdd/bin/design-lint.py` | 145 | build-agent | ✅ | Novo |
| `sdd/bin/handoff-lint.py` | 128 | build-agent | ✅ | Novo |
| `sdd/fixtures/conversa/*/` (7 pastas, 13 arquivos) · `sdd/fixtures/design/DESIGN_VALIDO.md` · `sdd/fixtures/handoff/HANDOFF_VALIDO.md` | — | build-agent | ✅ | Novos; as fixtures antigas ficaram intactas |
| `.agents/skills/<14>/SKILL.md` | +42 a +53 cada | build-agent | ✅ | Seção, identificação, versão |
| `.agents/skills/<14>/references/como-falar.md` | 46–71 cada | build-agent | ✅ | Novos |
| `sdd/templates/fragments/CLARIFY.md` · `sdd/templates/BUILD_REPORT_TEMPLATE.md` | +3 −2 · +1 −1 | build-agent | ✅ | Sem nome de ferramenta |
| `tests/test_agnostico.py` · `test_conversa.py` · `test_design_lint.py` · `test_handoff_lint.py` | — | build-agent | ✅ | Novos |
| `tests/test_skill_lint.py` · `test_correcoes_w0.py` · `test_contrato_build_release.py` · `test_matriz_new_session.py` · `test_release_workflow.py` | — | build-agent | ✅ | Mudanças de propósito: versões e a linha do CI |
| `.github/workflows/publish-gate.yml` · `docs/cli-conventions.md` · `CONTRIBUTING.md` · `MANIFEST.txt` | ±1 a +35 | build-agent | ✅ | — |

---

## Drift Detected

Houve dois drifts, ambos registrados antes de seguir:

1. **`sdd-checar-ambiente`.** A skill mandava repassar a saída do script "exatamente como veio, sem frase antes". A exceção (d) passou a valer para toda resposta dela, não só para a saudável: o Status vem antes, e o relatório não é retraduzido. Está no DESIGN, Decisão 8, e no DEFINE v1.1.
2. **Posição do lint na `sdd-handoff`.** O lint vira o passo `3b`, para não renumerar o passo 4. Está no DESIGN, Decisão 7, e no DEFINE v1.1 (AT-014).

Nenhum arquivo fora do manifest e nenhum prompt de runtime.

---

## Verification Results

### Incremental Verification

| Task | Command / Method | Result | Evidence |
|---|---|---|---|
| Base antes de tocar em nada | `SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover -s tests -p 'test_*.py'` em `dd27ef6` | Pass | `evidence/F4_CONVERSA/base-dd27ef6.log`: 326 OK |
| Baseline vermelha dos testes da F4 | os 9 módulos antes do código | Pass (vermelho esperado) | `evidence/F4_CONVERSA/baseline.log`: 78 FAIL, 34 ERROR |
| Testes das notas da revisão contra os lints de `4e77a1f` | 3 módulos com `sdd/bin/*-lint.py` do build | Pass (vermelho esperado) | `evidence/F4_CONVERSA/baseline-notas.log`: 10 FAIL |
| Code points dos 58 + 20 arquivos tocados | Python com `unicodedata` | Pass | `evidence/F4_CONVERSA/codepoints.log`: 0 invisíveis (só FE0F de emoji) |
| Comandos e passos `v2.2.4` × HEAD | `python3 -B sdd/reports/evidence/F4_CONVERSA/comandos-intactos.py` | Pass | `evidence/F4_CONVERSA/comandos-intactos.log` |
| Versões | `python3 -B scripts/check-versions.py --base v2.2.4 --base-obrigatoria` | Pass | `evidence/F4_CONVERSA/check-versions.log` |

### Verify Gate

| Attribute | Value |
|---|---|
| **Kind** | test |
| **Command / Method** | `bash sdd/bin/verify-gate.sh --strict sdd/features/DEFINE_F4_CONVERSA.md`. O cmd faz a cópia por `git archive HEAD`, roda o `publish-gate.sh` em modo ci e a suíte no piso |
| **Exit / Result** | 0 em `4e77a1f`, `fd94876` e `2fcdda1` (G1–G5 verdes; `Ran 388 tests … OK` no último) |
| **Status** | Green |
| **Evidence** | `evidence/F4_CONVERSA/GATE.log` |

### Manual UX Receipt

N/A

### Complementary Checks

| Check | Command / Method | Status | Evidence |
|---|---|---|---|
| Lint | `python3 sdd/bin/skill-lint.py --conversa .agents/skills/sdd-*/SKILL.md` | Pass | `evidence/F4_CONVERSA/skill-lint-conversa.log` |
| Typecheck | N/A (Python sem anotação verificada) | N/A | — |
| Tests | suíte inteira no piso | Pass | `evidence/F4_CONVERSA/suite-piso.log` |
| Build / Compile | publish-gate em modo ci, dentro do gate | Pass | `evidence/F4_CONVERSA/GATE.log` |

---

## Acceptance Test Verification

| ID | Scenario | Status | Evidence |
|---|---|---|---|
| AT-001 | `skill-lint --conversa` nas 16 skills → 0 | Pass | `evidence/F4_CONVERSA/skill-lint-conversa.log` |
| AT-002 | Sem a flag: só frontmatter; os 8 contratos antigos passam | Pass | `evidence/F4_CONVERSA/testes-f4.log` |
| AT-003 | Seção ausente, repetida, sem tabela, sem parte, `como-falar.md` ausente → 1 com o motivo | Pass | `evidence/F4_CONVERSA/testes-f4.log` |
| AT-004 | Pergunta com 0/2 recomendadas, recomendada fora do 1º lugar, sem "não sei", com "Outro", arquivo sem pergunta → 1 | Pass | `evidence/F4_CONVERSA/testes-f4.log` |
| AT-005 | Próximo passo > 100 caracteres → 1 | Pass | `evidence/F4_CONVERSA/testes-f4.log` |
| AT-006 | As 14 com seção, instrução de leitura e fragmento; nenhum banner nas 16 | Pass | `evidence/F4_CONVERSA/testes-f4.log` |
| AT-007 | Fragmento com as regras da pergunta e os campos da parada | Pass | `evidence/F4_CONVERSA/testes-f4.log` |
| AT-008 | DESIGN válido → 0 | Pass | `evidence/F4_CONVERSA/testes-f4.log` |
| AT-009 | 12 casos de DESIGN quebrado → 1 com a regra | Pass | `evidence/F4_CONVERSA/testes-f4.log` |
| AT-010 | DESIGN F1, F2, F3 e F4 reais → 0 | Pass | `evidence/F4_CONVERSA/design-lint-reais.log` |
| AT-011 | HANDOFF válido, com seção extra, com e sem Eventos → 0 | Pass | `evidence/F4_CONVERSA/testes-f4.log` |
| AT-012 | 12 mutações de HANDOFF → 1; ficha ✅ sem prompt → 0 | Pass | `evidence/F4_CONVERSA/testes-f4.log` |
| AT-013 | Sem argumento ou arquivo ausente → 64; ilegível → 1 com `RESULTADO:` | Pass | `evidence/F4_CONVERSA/testes-f4.log` |
| AT-014 | `### 8. Conferir` e `### 3b. Conferir a ficha` com o lint | Pass | `evidence/F4_CONVERSA/testes-f4.log` |
| AT-015 | `test_agnostico` verde no HEAD; os 8 termos e "subagente" | Pass | `evidence/F4_CONVERSA/testes-f4.log` |
| AT-016 | `test_agnostico` do HEAD reprova a `v2.2.4` nos 2 hits | Pass | `evidence/F4_CONVERSA/baseline-agnostico.log` |
| AT-017 | Identificação = `metadata.version` e `updated` nas 16 | Pass | `evidence/F4_CONVERSA/testes-f4.log` |
| AT-018 | Comandos e passos iguais aos da `v2.2.4` nas 14, salvo as exceções | Pass | `evidence/F4_CONVERSA/comandos-intactos.log` |
| AT-019 | `check-versions --base v2.2.4 --base-obrigatoria` → 0 | Pass | `evidence/F4_CONVERSA/check-versions.log` |
| AT-020 | 388 testes no piso; contratos com diff vazio; 16 skills | Pass | `evidence/F4_CONVERSA/suite-piso.log`, `evidence/F4_CONVERSA/contratos-intactos.log` |
| AT-021 | 6 sabotagens vermelhas com o nome do teste e verdes depois do `git checkout` | Pass | `evidence/F4_CONVERSA/sabotagem.log` |
| AT-022 | CI do PR: `gate` (ubuntu) e `testes-macos` verdes, passo com `--conversa`, 0 achado de integridade | Pass | `evidence/F4_CONVERSA/ci-pr.log` |

Sabotagens (AT-021, em `2fcdda1`, script `evidence/F4_CONVERSA/sabotagem.sh`, `sed` por padrão):

| Alvo | Quebra | Teste que ficou vermelho | Depois do `git checkout` |
|---|---|---|---|
| `sdd/bin/skill-lint.py` | Não exige mais "não sei" | `test_cada_fixture_reprova_pelo_seu_motivo` (`conversa-sem-nao-sei`), `test_opcao_em_duas_linhas_nao_esconde_as_seguintes` | OK |
| `sdd/bin/design-lint.py` | Ciclo deixa de reprovar | `test_cada_mutacao_reprova` (`ciclo`) | OK |
| `sdd/bin/handoff-lint.py` | Placeholder dentro do prompt deixa de reprovar | `test_cada_mutacao_reprova` (`placeholder_no_prompt`) | OK |
| `tests/test_agnostico.py` | `AskUserQuestion` sai da lista | `test_fixture_com_nome_de_ferramenta_reprova`, `test_os_8_termos_e_arquivo_sem_extensao_reprovam` | OK |
| `sdd-build/references/como-falar.md` | Perde a opção "não sei" | `test_as_16_skills_reais_passam_com_conversa` | OK |
| `sdd-define/SKILL.md` | O banner volta | `test_nenhuma_abre_com_banner` (`sdd-define`) | OK |

A sonda de mutantes do avaliador do ciclo 1 também rodou sobre `fd94876`, com 27 alvos:
- 24 ficaram vermelhos;
- 2 apontam regras que foram reescritas, e os testes novos cobrem as duas;
- 1 era equivalente: sem o `isfile`, o lint reprova pela leitura. Ele passou a morrer depois que o teste da fixture `conversa-sem-como-falar` começou a exigir a mensagem exata.

---

## Advisor Ledger

**Veredito do avaliador:** NEEDS_WORK — ciclo 1 sobre `4e77a1f`, `sdd/reviews/AVALIACAO_F4_CONVERSA_20261029-ciclo1.md`.

Revisão pós-build por avaliador de contexto fresco (subagente sem a conversa do build, numa worktree destacada). Resultado: 0 HIGH, 4 MEDIUM, 8 LOW. Dos 22 ATs, 21 foram provados por execução e o AT-022 ficou só local. Cada nota foi reproduzida aqui antes da decisão.

| # | Phase | Note | Severity | Decision | Evidence |
|---:|---|---|---|---|---|
| M1 | post-build | Opções depois de linha em branco ou com `*` não eram conferidas | MEDIUM | APPLIED | Reproduzido (exit 0). Agora o lint pula a linha em branco entre opções e aceita `*`/`+`. Teste: `test_opcoes_depois_de_linha_em_branco_ou_com_asterisco_sao_conferidas`. `fd94876` |
| M2 | post-build | `## ` dentro do prompt colado encerrava a seção no `handoff-lint` | MEDIUM | APPLIED | Reproduzido (exit 1). A seção agora é delimitada sem os blocos de código. Teste: `test_titulo_dentro_do_prompt_nao_encerra_a_secao` |
| M3 | post-build | A `sdd-handoff` deixa o prompt opcional sem continuação, e o lint o exigia | MEDIUM | APPLIED | Ficha com Status ✅ dispensa o prompt; o texto do passo 3b diz isso; DEFINE v1.2, AT-012. Testes: `test_ficha_fechada_dispensa_o_prompt`, `test_ficha_aberta_sem_prompt_reprova` |
| M4 | post-build | 7 regras do DEFINE sem teste | MEDIUM | APPLIED | Casos novos: zero decisões, placeholder maiúsculo e autodependência (design); Status da ficha, "conforme combinado" e placeholder maiúsculo (handoff); os 8 termos (agnóstico) |
| L1 | post-build | Sem a flag, a mensagem e o tratamento de `--x` mudaram | LOW | APPLIED (mensagem) / REBUTTED (exit 64) | A mensagem da `v2.2.4` voltou: `test_sem_flag_mensagem_de_frontmatter_nao_muda`. Opção desconhecida = 64 é a Decisão 2 do DESIGN: antes, `--verbose` virava um caminho de arquivo inexistente |
| L2 | post-build | `**Próximo passo:**` e `> ` fora do limite | LOW | APPLIED | `test_proximo_passo_com_dois_pontos_ou_em_citacao_tambem_tem_limite` |
| L3 | post-build | "Outro (descreva)" passava | LOW | APPLIED | Rótulo que começa por Outro/Outra/Other reprova: `test_outro_com_complemento_reprova` |
| L4 | post-build | `test_agnostico` sem arquivo sem extensão e com caixa | LOW | APPLIED | Agora varre todo arquivo de texto, e "Task tool"/"Agent tool" sem caixa: `test_os_8_termos_e_arquivo_sem_extensao_reprovam`, `test_binario_no_escopo_nao_quebra_a_varredura` |
| L5 | post-build | Arquivo ilegível dava traceback nos 2 lints | LOW | APPLIED | `OSError` agora sai 1 com 🛑 e `RESULTADO:` (DEFINE v1.2, AT-013) |
| L6 | post-build | `« »` tratado como placeholder no DESIGN | LOW | APPLIED | Saiu do `design-lint` e ficou no `handoff-lint`, cuja skill cita `«placeholder»`: `test_aspas_angulares_em_prosa_passam` |
| L7 | post-build | Identificação × Status na 1ª resposta | LOW | APPLIED | "uma vez só, antes do Status" nas 13 skills com a linha; a `checar-ambiente` se identifica na linha ✅ |
| L8 | post-build | Seção dentro de bloco de código contava | LOW | APPLIED | `test_secao_dentro_de_bloco_de_codigo_nao_conta` |

Depois das notas, o Verify Gate rodou de novo em `fd94876` e ficou verde, com 382 testes.

**Veredito do avaliador:** PASS — ciclo 2 sobre `fd94876`, `sdd/reviews/AVALIACAO_F4_CONVERSA_20261029-ciclo2.md`.

Um 2º avaliador em contexto fresco recebeu os achados do ciclo 1 como brief. Resultado:
- os 4 MEDIUM estão fechados;
- dos 8 LOW, 7 estão fechados, e o L1 foi aceito com motivo na parte do exit 64;
- 6 LOW novos, todos no diff das correções.

| # | Phase | Note | Severity | Decision | Evidence |
|---:|---|---|---|---|---|
| LOW-1 | post-build (ciclo 2) | Linha `>` vazia na citação escondia as opções | LOW | APPLIED | `>` sozinho conta como linha em branco: `test_pergunta_em_citacao_com_linha_vazia_e_conferida`. Commit `2fcdda1` |
| LOW-2 | post-build (ciclo 2) | Plural "Outros"/"Outras" passava; lista numerada, `__negrito__` e prosa entre pergunta e opções também | LOW | APPLIED (plural) / REBUTTED (resto) | Plural: `test_outros_no_plural_reprova`. Lista numerada, `__…__` e prosa no meio ficam fora do formato `- **rótulo**` do DEFINE e do fragmento, e nenhum `como-falar.md` os usa |
| LOW-3 | post-build (ciclo 2) | Qualquer ✅ na célula Status dispensava o prompt | LOW | APPLIED | Só a célula que começa por ✅ dispensa: `test_check_no_meio_do_status_nao_dispensa_o_prompt` |
| LOW-4 | post-build (ciclo 2) | `test_agnostico` ignorava texto não-UTF-8 sem avisar | LOW | APPLIED | Texto não-UTF-8 vira achado (falha fechado), e binário com NUL é pulado: `test_texto_fora_de_utf8_reprova` |
| LOW-5 | post-build (ciclo 2) | "Ilegível sai 1" sem teste | LOW | APPLIED | `test_arquivo_ilegivel_sai_1_com_resultado` nos 2 lints |
| LOW-6 | post-build (ciclo 2) | O corpo do DESIGN v1.1 contradizia o código | LOW | APPLIED | Decisões 2, 4, 5 e o Code Pattern 3 alinhados; docstring do `skill-lint` também; `design-lint` e `validate_design` verdes no DESIGN |

---

## Issues Encountered

| # | Issue | Resolution | Impact |
|---:|---|---|---|
| 1 | A opção que quebra em 2 linhas encerrava a leitura das opções seguintes: 12 das 14 skills saíam "sem não sei" | A linha recuada depois de uma opção conta como continuação dela: `test_opcao_em_duas_linhas_nao_esconde_as_seguintes` | Nenhum: achado antes do commit |
| 2 | O `rm -rf` com variável na geração das fixtures foi barrado pela checagem de segurança | Fixtures geradas em Python, sem remoção | Nenhum |
| 3 | A troca da linha de identificação (L7) pegou a `sdd-iniciar-repo` e a `sdd-higiene-dado`, que estão fora do escopo | `git checkout` das duas antes do commit; `check-versions` verde | Nenhum |
| 4 | O `report-lint` só aceita evidência em `evidence/<FEATURE>/`, e a pasta se chamava `evidence/F4/` | Renomeada para `evidence/F4_CONVERSA/`; DEFINE, DESIGN e scripts atualizados | Nenhum |
| 5 | Depois do L7, a sabotagem do banner não casava (o `sed` usava o texto antigo) | Padrão atualizado; 6/6 provadas | +1 rodada de sabotagem |

---

## Deviations from Design

| Deviation | User Decision | Reason | Impact |
|---|---|---|---|
| Decisões 2, 4, 5 e 6 ajustadas pelas notas da revisão (DESIGN v1.1) | Revisão de contexto fresco escolhida pelo Roberto; notas aplicadas sem reabrir decisão do Brainstorm | 4 MEDIUM reproduzidos | Lints mais estritos onde deixavam passar e mais tolerantes onde reprovavam um documento certo |
| AT-012 e AT-013 do DEFINE (v1.2) | idem | O AT-012 contradizia a `sdd-handoff`; o AT-013 não falava de arquivo ilegível | Ficha ✅ sem prompt passa; ilegível sai 1 |

---

## Blockers

None.

---

## Final Status

### Overall: COMPLETE

- [x] All File Manifest tasks completed
- [x] Incremental verification recorded
- [x] Verify Gate green or manual-ux receipt positive
- [x] Complementary checks applicable pass
- [x] Acceptance Tests verified
- [x] LLM prompt receipts complete when required
- [x] Drift decisions recorded
- [x] Advisor findings disposed when applicable
- [x] No unresolved blocker
- [x] No TODO/FIXME used as unfinished implementation

---

## Next Step

Execute o **SDD Handoff by RDD**.
