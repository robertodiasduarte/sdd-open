# BUILD REPORT: F2 Terreno do sdd-open

> Implementation report for F2 Terreno do sdd-open

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | F2_TERRENO |
| **Date** | 2026-10-29 |
| **Author** | SDD Build by RDD |
| **BRAINSTORM** | `sdd/features/BRAINSTORM_F2_TERRENO.md` |
| **DEFINE** | `sdd/features/DEFINE_F2_TERRENO.md` |
| **DESIGN** | `sdd/features/DESIGN_F2_TERRENO.md` (v1.1) |
| **Status** | Complete |

Branch `feat/incorporar-starter`, commits `4ee5470` (build) e `41c6169` (notas da revisão pós-build), sobre `f75fbdb` = `v2.2.1`. Fonte do porte: `/Users/robertoduarte/rdd-public/sdd-starter` em `17c69c4`.

---

## Mode Selection

| Signal | Observation |
|---|---|
| Manifest files | 21 no DESIGN v1.0; 22 depois do drift (item 22) |
| Cross-file coupling | High — script → SKILL.md → teste → `MANIFEST.txt`; `MANIFEST.txt` tocado por todos |
| Security surface | Moderada — detecção de segredo (`--segredo`), hook de commit (`alarme.sh`); porte de código já testado |
| LLM prompt items | None (`LLM Prompts: false`) |
| Independent volume | Baixo — 3 portes paralelizáveis em tese, mas todos convergem no `MANIFEST.txt` e na `new-session` |
| Context-rot risk | Médio — sessão longa (Brainstorm → Build); mitigado pelos artefatos e pela revisão de contexto fresco |
| Runtime capabilities | default e ralph (subagentes) disponíveis; briefs não oferecido |

**Recommendation:** default — cadeia de dependência e arquivo compartilhado tiram o ganho de paralelizar; mesmo modo da F1.

**User decision:** default (Roberto, 2026-10-29).

**Pre-build review:** No — Roberto escolheu "só pós-build": porte de código já testado, decisões validadas em 2 checkpoints do Brainstorm.

---

## Summary

| Metric | Value |
|---|---|
| **Tasks Completed** | 22/22 |
| **Files Created** | 17 |
| **Files Modified** | 5 |
| **Files Deleted** | 0 |
| **Verification Commands Run** | 31 (gate 2×, suíte no piso 3×, 21 logs por AT, sabotagem 2×, medições de tempo e de gitconfig) |
| **Verify Gate** | Green |
| **Execution Mode** | default |

Testes: 242 (115 da F1 + 105 portados + 22 novos), 0 skip, verdes no `/usr/bin/python3` 3.9.6 com `/bin/bash` 3.2.57 e no `python3` do PATH dentro do gate.

---

## Task Execution

| # | Manifest ID | Task | Executor | Status | Verification | Evidence |
|---:|---:|---|---|---|---|---|
| 1 | 1 | Create `checar.sh` (porte + `dado_exposto()` + `--segredo` + 3 textos) | direct | Complete | `bash -n` + `test_checar.py` | 56 OK no build; 57 OK depois da nota 2 |
| 2 | 2 | Create `sdd-checar-ambiente/SKILL.md` (1.3.0) | direct | Complete | `skill-lint.py` | frontmatter válido |
| 3 | 3 | Create `pre-commit.sh` | direct | Complete | `test_alarme.py` | OK |
| 4 | 4 | Create `alarme.sh` (filtro do cabeçalho gerado) | direct | Complete | `bash -n` + `test_alarme.py` | 29 OK |
| 5 | 5–11 | Create `sdd-higiene-dado` SKILL.md, manifest, cases, CHANGELOG, 3 references | direct | Complete | `skill-lint.py`; `json.load` nos 2 JSON | válidos |
| 6 | 12 | Create `inventario.sh` | direct | Complete | `test_inventario.py` | 24 OK |
| 7 | 13 | Create `sdd-iniciar-repo/SKILL.md` (1.1.1) | direct | Complete | `skill-lint.py` | frontmatter válido |
| 8 | 14 | Modify `sdd-new-session/SKILL.md` (1.1.0) | direct | Complete | `skill-lint.py` + `test_matriz_new_session.py` | 12 OK |
| 9 | 15 | Modify `bin/sdd-open.sh` (`doctor`) | direct | Complete | smoke com `.env` commitado em `/bin/bash` + `test_sdd_open.py` | ⚠️ com arquivo e comando, `RESULTADO: INSTALADO`, rc 0 |
| 10 | 16 | Create `tests/test_checar.py` | direct | Complete | `unittest test_checar` | 57 OK |
| 11 | 17 | Create `tests/test_alarme.py` | direct | Complete | `unittest test_alarme` | 29 OK |
| 12 | 18 | Create `tests/test_inventario.py` | direct | Complete | `unittest test_inventario` | 24 OK |
| 13 | 19 | Create `tests/test_matriz_new_session.py` | direct | Complete | `unittest test_matriz_new_session` | 12 OK |
| 14 | 20 | Modify `tests/test_sdd_open.py` | direct | Complete | `unittest test_sdd_open` | 17 OK |
| 15 | 21 | Modify `MANIFEST.txt` (+17, `LC_ALL=C`) | direct | Complete | G3 do publish-gate | árvore e manifest batem nos dois sentidos |
| 16 | 22 | Modify `tests/test_skill_lint.py` (13 → 16 skills) | direct | Complete | `unittest test_skill_lint` | OK |

---

## Files Changed

| File | Action | Manifest ID | Verified | Notes |
|---|---|---:|---|---|
| `.agents/skills/sdd-checar-ambiente/scripts/checar.sh` | Create | 1 | Yes | `--segredo`; `dado_exposto()` com pathspec `:(glob,icase)` (nota 2); `voce@example.com`; `IDENT` e caso sem `sdd-iniciar-repo` sem `sdd-starter`/`npx` |
| `.agents/skills/sdd-checar-ambiente/SKILL.md` | Create | 2 | Yes | 1.3.0; `--segredo` documentado; `sdd/ambiente.md` → slots de `sdd/config.yaml` |
| `.agents/skills/sdd-higiene-dado/scripts/pre-commit.sh` | Create | 3 | Yes | linha 3 "SDD Open by RDD" |
| `.agents/skills/sdd-higiene-dado/scripts/alarme.sh` | Create | 4 | Yes | `grep -v -F 'sdd-open:generated'` antes de montar o hook |
| `.agents/skills/sdd-higiene-dado/SKILL.md` | Create | 5 | Yes | 1.1.1; inventário sem `agents/openai.yaml`; testes apontados em `tests/` da raiz |
| `.agents/skills/sdd-higiene-dado/manifest.json` | Create | 6 | Yes | `version` 1.1.1 |
| `.agents/skills/sdd-higiene-dado/evals/cases.json` | Create | 7 | Yes | `version` 1.1.1 |
| `.agents/skills/sdd-higiene-dado/CHANGELOG.md` | Create | 8 | Yes | entrada 1.1.1 |
| `.agents/skills/sdd-higiene-dado/references/COMO_FUNCIONA.md` | Create | 9 | Yes | literal |
| `.agents/skills/sdd-higiene-dado/references/ESCOPO_CONFIRMADO.md` | Create | 10 | Yes | literal (registro histórico do escopo HD001 v1) |
| `.agents/skills/sdd-higiene-dado/references/RUNTIME_COMPATIBILITY.md` | Create | 11 | Yes | literal |
| `.agents/skills/sdd-iniciar-repo/scripts/inventario.sh` | Create | 12 | Yes | literal |
| `.agents/skills/sdd-iniciar-repo/SKILL.md` | Create | 13 | Yes | 1.1.1; `npx … sdd-starter` → a `sdd-higiene-dado` volta com o `init` do sdd-open |
| `.agents/skills/sdd-new-session/SKILL.md` | Modify | 14 | Yes | 1.0.0 → 1.1.0 (159 → 262 linhas) |
| `bin/sdd-open.sh` | Modify | 15 | Yes | +21 linhas no fim de `doctor()` |
| `tests/test_checar.py` | Create | 16 | Yes | 53 portados + 4 (`TestSegredo`) |
| `tests/test_alarme.py` | Create | 17 | Yes | 28 portados + 1 (`TestCopiaGerada`); git isolado (nota 1) |
| `tests/test_inventario.py` | Create | 18 | Yes | 24 portados |
| `tests/test_matriz_new_session.py` | Create | 19 | Yes | 12 (matriz, contrato, portadas) |
| `tests/test_sdd_open.py` | Modify | 20 | Yes | +5 (doctor ×4, `bash -n` nas cópias) |
| `MANIFEST.txt` | Modify | 21 | Yes | 93 → 110 linhas |
| `tests/test_skill_lint.py` | Modify | 22 | Yes | `test_as_16_skills_reais_passam` |

Diff contra o starter (só as adaptações): `diff` de cada arquivo portado contra `/Users/robertoduarte/rdd-public/sdd-starter/skills/...`; o `checar.sh` tem 76 linhas de diferença no build (extração de `dado_exposto`, `--segredo`, 3 textos) e +3 na nota 2.

---

## Drift Detected

| # | Task / Path | Drift | Decision | Action |
|---:|---|---|---|---|
| 1 | `tests/test_skill_lint.py` | Teste da F1 fixava `len(skills) == 13`; com as 3 portadas são 16 e a suíte ficou vermelha. Arquivo fora do File Manifest v1.0 | approved deviation (Roberto: "Fixar 16 e renomear") | Item 22 no DESIGN v1.1; teste renomeado para `test_as_16_skills_reais_passam` |
| 2 | tag `v2.2.1` | O clone local não tinha a tag criada pela release automática; `check-versions --base v2.2.1 --base-obrigatoria` saiu VERMELHO por base indisponível | false positive (ambiente, não código) | `GIT_TERMINAL_PROMPT=0 git fetch -q origin tag v2.2.1` → `f75fbdb`; check-versions VERDE |

---

## Verification Results

### Incremental Verification

| Task | Command / Method | Result | Evidence |
|---|---|---|---|
| checar.sh | `python3 -B -m unittest discover -s tests -p 'test_checar.py'` | Pass | 56 OK (111 s) no build; 57 OK depois da nota 2 |
| alarme/pre-commit | `… -p 'test_alarme.py'` | Pass | 29 OK |
| inventario.sh | `… -p 'test_inventario.py'` | Pass | 24 OK |
| doctor | `init --yes --vendors claude` com `.env` commitado, `/bin/bash` | Pass | ⚠️ + comando + medida; `RESULTADO: INSTALADO`; rc 0 |
| doctor + gerador | `… -p 'test_sdd_open.py'` | Pass | 16 OK no build; 17 OK depois da nota 4 |
| matriz e contrato | `… -p 'test_matriz_new_session.py'` | Pass | 12 OK (2 falhas do próprio teste corrigidas na 1ª rodada: `add_impede` só com a variável MSG contado como mensagem e regex de linha) |
| skills | `python3 sdd/bin/skill-lint.py .agents/skills/sdd-*/SKILL.md` | Pass | 16 válidas |
| versões | `python3 -B scripts/check-versions.py --base v2.2.1 --base-obrigatoria` | Pass | `16 skills com versão coerente` |
| `--segredo` em repo grande | `time bash checar.sh --segredo` em repo com 5.000 arquivos | Pass (depois da nota 2) | 11,7 s → 0,056 s |

### Verify Gate

| Attribute | Value |
|---|---|
| **Kind** | test |
| **Command / Method** | `bash sdd/bin/verify-gate.sh --strict sdd/features/DEFINE_F2_TERRENO.md` (cmd: `T=$(mktemp -d) && git archive HEAD \| tar -x -C $T && PUBLISH_GATE_MODE=ci bash scripts/publish-gate.sh $T && cd $T && python3 -B -m unittest discover -s tests -p 'test_*.py'`) |
| **Exit / Result** | 0 — publish-gate G1–G5 verdes na cópia de `git archive 41c6169`; `Ran 242 tests … OK` |
| **Status** | Green |
| **Evidence** | `evidence/F2_TERRENO/AT-001.log` (também verde em `4ee5470`, 240 testes, antes das notas da revisão) |

### Manual UX Receipt

N/A

### Complementary Checks

| Check | Command / Method | Status | Evidence |
|---|---|---|---|
| Lint | `python3 sdd/bin/skill-lint.py .agents/skills/sdd-*/SKILL.md` | Pass | `evidence/F2_TERRENO/AT-018.log` |
| Typecheck | N/A | N/A | projeto sem typecheck |
| Tests | `SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover -s tests -p 'test_*.py' -v` (piso Python 3.9.6 + bash 3.2.57) | Pass | `evidence/F2_TERRENO/suite-piso.log` — 242 OK, 0 skip, exit 0 |
| Build / Compile | `bash -n` nos 4 scripts portados e nas cópias geradas pelo `sync` | Pass | `evidence/F2_TERRENO/AT-019.log` |

---

## Acceptance Test Verification

| ID | Scenario | Status | Evidence |
|---|---|---|---|
| AT-001 | Suíte na cópia limpa: 105 portados + 115 da F1, sem rede, sem gitconfig de quem roda | Pass | `evidence/F2_TERRENO/AT-001.log` |
| AT-002 | `skill-lint` 0 nas 16; nenhuma `agents/openai.yaml` nas 3 portadas | Pass | `evidence/F2_TERRENO/AT-002.log` |
| AT-003 | Referência a `sdd-starter`/`npx skills add`/`sdd/ambiente.md` nas portadas reprova nomeando o arquivo | Pass | `evidence/F2_TERRENO/AT-003.log` |
| AT-004 | `--segredo` com `.env`, `.env.local`, `.pfx`, `.p12`, `.pem` com chave → exit 1, comando e medida | Pass | `evidence/F2_TERRENO/AT-004.log` |
| AT-005 | `--segredo` só com `.env.example`, `.env.sample`, `.pem` público → exit 0 calado | Pass | `evidence/F2_TERRENO/AT-005.log` |
| AT-006 | `--segredo` com origin e API pendurados → < 3 s, sem `curl` nem `ls-remote` | Pass | `evidence/F2_TERRENO/AT-006.log` |
| AT-007 | `doctor` com `.env` commitado → ⚠️ com arquivo e comando, exit 0, `RESULTADO:` | Pass | `evidence/F2_TERRENO/AT-007.log` |
| AT-008 | `doctor` sem segredo → ✅ | Pass | `evidence/F2_TERRENO/AT-008.log` |
| AT-009 | Pacote sem `checar.sh` → ⚠️ pacote incompleto, exit 0 | Pass | `evidence/F2_TERRENO/AT-009.log` |
| AT-010 | Hook instalado da cópia gerada sem `sdd-open:generated` e igual ao da fonte; `verificar` reconhece | Pass | `evidence/F2_TERRENO/AT-010.log` |
| AT-011 | pre-commit recusa CPF/CNPJ válido, `.env`, `.pfx`/`.p12`, `.pem` com chave, planilha nova | Pass | `evidence/F2_TERRENO/AT-011.log` |
| AT-012 | `core.hooksPath` ou hook alheio → exit 2 sem gravar | Pass | `evidence/F2_TERRENO/AT-012.log` |
| AT-013 | `inventario.sh` sinaliza `.env`, `.pfx`, planilha, > 50 MB, segredo no histórico | Pass | `evidence/F2_TERRENO/AT-013.log` |
| AT-014 | `--frente` bloqueia os 12 casos com `🔴 Impede o trabalho` e "Nada foi criado." | Pass | `evidence/F2_TERRENO/AT-014.log` |
| AT-015 | Toda mensagem de bloqueio do `--frente` tem linha na tabela, e vice-versa | Pass | `evidence/F2_TERRENO/AT-015.log` |
| AT-016 | Contrato escrito da `new-session` 1.1.0 | Pass | `evidence/F2_TERRENO/AT-016.log` |
| AT-017 | publish-gate `ci` sai 0 na árvore da F2 (G2 sem literal proibido) | Pass | `evidence/F2_TERRENO/AT-017.log` |
| AT-018 | `check-versions --base v2.2.1 --base-obrigatoria` sai 0 com 1.3.0/1.1.1/1.1.1/1.1.0 | Pass | `evidence/F2_TERRENO/AT-018.log` |
| AT-019 | `init` + `sync` idempotentes; cópias geradas dos 4 scripts passam `bash -n` | Pass | `evidence/F2_TERRENO/AT-019.log` |
| AT-020 | 115 da F1 verdes; `git diff v2.2.1 -- sdd/ scripts/publish-gate* .github/` vazio | Pass | `evidence/F2_TERRENO/AT-020.log` |
| AT-021 | 5 sabotagens (4 scripts + `doctor`) com teste nomeado vermelho e verde depois do `git checkout` | Pass | `evidence/F2_TERRENO/AT-021.log` |

Sabotagens (AT-021, rodadas em `41c6169`, script em `evidence/F2_TERRENO/sabotagem.sh`):

| Script | Quebra | Teste que ficou vermelho | Depois do `git checkout` |
|---|---|---|---|
| `checar.sh` | `*.p12` sai do `case` de `dado_exposto` | `test_p12_e_env_variante`, `test_acusa_cada_tipo_e_sai_1` | 57 OK |
| `alarme.sh` | `grep -v -F 'sdd-open:generated'` → `cat` | `test_hook_da_copia_gerada_sem_cabecalho_e_igual_ao_da_fonte` | 29 OK |
| `pre-commit.sh` | 2º dígito verificador do CPF sempre aceito | `test_digito_errado_nao_bloqueia` | 29 OK |
| `inventario.sh` | `LIMITE_MB=50` → `500` | `test_cinco_categorias` e mais 3 | 24 OK |
| `bin/sdd-open.sh` | `doctor` sem a chamada ao `--segredo` | `test_doctor_acusa_env_salvo_no_git_e_sai_0`, `test_doctor_nao_perde_o_resto_de_nome_com_quebra_de_linha` | 17 OK |

O avaliador de contexto fresco repetiu as sabotagens numa cópia de rascunho (6, inclusive tirar `dado_exposto` do modo normal) e todas discriminaram.

---

## Advisor Ledger

Revisão pós-build por avaliador de contexto fresco (subagente sem a conversa do build), sobre `4ee5470`. Veredito: **FIX FIRST** — 0 HIGH, 2 MEDIUM, 4 LOW; 20 de 21 ATs PASS, AT-001 FAIL parcial (nota 1).

| # | Phase | Note | Severity | Decision | Evidence |
|---:|---|---|---|---|---|
| 1 | post-build | `tests/test_alarme.py` rodava git e alarme com a configuração git de quem roda: com `core.hooksPath` global, 24 de 29 vermelhos (contradiz AT-001) | MEDIUM | APPLIED | Reproduzido aqui (24 falhas; `test_checar` e `test_inventario` não afetados). `ISOLADO` (`GIT_CONFIG_GLOBAL=os.devnull`, `GIT_CONFIG_NOSYSTEM=1`) em todos os `subprocess.run`; com o mesmo gitconfig, 29 OK. Commit `41c6169` |
| 2 | post-build | `--segredo` fazia `basename \| tr` por arquivo rastreado: 5.000 arquivos = 12,3 s, no fim de todo `init` | MEDIUM | APPLIED | Medido aqui: 11,7 s. Pathspec `:(glob,icase)` filtra no git (superconjunto conferido do `case` antigo); 0,056 s. Teste novo `test_repositorio_grande_continua_rapido` (3.000 arquivos, < 3 s) vermelho no script antigo (7,1 s), verde no novo |
| 3 | post-build | Testes portados ignoravam `SDD_TEST_BASH`: o piso bash 3.2 só valia porque o PATH desta máquina tem só o `/bin/bash` | LOW | APPLIED | `which -a bash` = só `/bin/bash`, então as rodadas anteriores valeram. Os 3 testes portados passam a usar `SDD_TEST_BASH` |
| 4 | post-build | `doctor` descartava a linha de continuação quando o nome do arquivo tem quebra de linha | LOW | APPLIED | `case` do doctor: linha vazia e cabeçalho 🔴 ignorados, resto recuado. Teste novo `test_doctor_nao_perde_o_resto_de_nome_com_quebra_de_linha` vermelho no doctor antigo, verde no novo |
| 5 | post-build | `new-session`: "evidência literal" para `editor` (preferência da máquina) e `worktree_base` (convenção) ia para o config compartilhado; não dizia o que fazer depois da resposta sobre `default_branch` divergente | LOW | APPLIED | Texto: evidência declarada ("`command -v code` neste computador", "padrão do sdd-open"), aviso de que o config é compartilhado, e a resposta vale para esta frente sem sobrescrever o slot. Comportamento decidido no Brainstorm (gravar os 5 slots) mantido |
| 6 | post-build | `checar.sh` rodado de uma subpasta sugere `git rm --cached` com caminho relativo à raiz | LOW | REBUTTED | Herdado do starter, igual no modo normal; o `doctor` entra na raiz do projeto antes de rodar e a skill manda rodar "de dentro da pasta do projeto". Mudar o texto do comando alteraria a saída que os 57 testes provam; fica como melhoria futura |

Depois das notas 1–5, o Verify Gate rodou de novo em `41c6169`: verde, 242 testes.

---

## Issues Encountered

| # | Issue | Resolution | Impact |
|---:|---|---|---|
| 1 | Linha `exit=` vazia no 1º log do piso: o terminal do agente é zsh e `PIPESTATUS` não existe lá | Log refeito dentro de `bash -c`, com o código capturado antes do filtro | Nenhum; o log foi refeito, não editado |
| 2 | 1ª geração dos logs por AT gravou em caminho relativo depois de `cd tests` (nenhum arquivo criado) | Caminho absoluto no script; logs regenerados | Nenhum |
| 3 | `test_checar.py` leva ~100 s (casos que esperam o teto de 10 s do `alcance`); suíte inteira ~2,9 min | Aceito (Decision 7 do DESIGN) | Gate e CI ~2 min mais longos |
| 4 | `ResourceWarning: unclosed socket` dos servidores HTTP locais do `test_checar.py` portado | Filtrado dos logs; não é falha (veio do starter) | Ruído no stderr da suíte |

---

## Deviations from Design

| Deviation | User Decision | Reason | Impact |
|---|---|---|---|
| Item 22 do manifest (`tests/test_skill_lint.py`) | Roberto: fixar 16 e renomear | O teste da F1 fixava 13 skills | DESIGN v1.1 |
| `dado_exposto()` filtra por pathspec em vez de `ls-files` inteiro | Nota 2 da revisão (MEDIUM, aplicada) | Desempenho exigido pela Constraint do DEFINE ("`--segredo` sem rede e rápido") | Classificação igual (superconjunto filtrado pelo mesmo `case`) |

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

Fora deste gate, ainda a fazer: PR, CI no `ubuntu-latest`, OK do Roberto citando "sdd-open", push em `main` e a Release com `SHA256SUMS.txt`. Não verificado: a suíte com a rede de fato desligada (o isolamento vem dos servidores locais e de `.invalid`) e a obediência do agente à `sdd-new-session` (A-003 do DEFINE).

---

## Next Step

Execute o **SDD Handoff by RDD**.
