# DEFINE: F15 Slots — smoke visual na release, teste do diff antes do OK e checagem de migration antes do apply

> Um executor de slot (`sdd/bin/slot.sh`) com contrato único de saída, 4 slots novos (3 de smoke na `sdd-release`, 1 de checagem de schema no build 4b) e o `test-baseline.sh --touched` contando o teste ao lado da fonte, rodado pela release antes do OK.

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | F15_SLOTS |
| **Date** | 2026-11-09 |
| **Author** | define-agent (worktree `sdd-open-f15-slots`, branch `feat/f15-slots`, base `9d8ac24` = `v2.7.2`) |
| **Status** | Ready for Design |
| **Clarity Score** | 14/15 |

---

## Problem Statement

A `sdd-release` do Open não tem onde o projeto ligar um smoke visual (antes do OK, antes do push, depois do deploy) nem roda teste nenhum antes do OK, e a `sdd-build` aplica migration (passo 4b) sem um ponto onde o projeto confira o SQL antes. Sem esses três pontos, o repositório privado da RDD não pode trocar o `/release` antigo pelo Open (fase 3 da F15), e nenhum outro projeto consegue ligá-los sem editar skill.

---

## Target Users

| User | Role | Pain Point |
|---|---|---|
| Projeto que usa o Open (inclui o privado da RDD) | preenche `sdd/config.yaml` | não tem slot para smoke visual nem para checagem de schema; teria de editar a skill, e o `sync` desfaz a edição |
| Quem aprova a release | responde ao bloco do OK | o bloco não diz se o teste ao lado do código alterado passou; hoje a 0b só pergunta isso ao modelo |
| Quem aplica migration | confirma o apply no 4b | SQL com problema conhecido chega ao banco, que não tem undo |

---

## Goals

| Priority | Goal |
|---|---|
| **MUST** | `sdd/bin/slot.sh` com o contrato único: vazio = PULADO (11) · 0 OK · 2 REPROVOU · 10 NADA A MEDIR · outro = INCONCLUSIVO (3) · 64 uso |
| **MUST** | 4 slots novos, vazios por padrão: `smoke.before_ok_cmd`, `smoke.before_push_cmd`, `smoke.after_deploy_cmd`, `schema.check_cmd` |
| **MUST** | `sdd-release` chama o executor nos 3 momentos, com peso por momento, e roda `test-baseline.sh --touched` na 0a |
| **MUST** | `test-baseline.sh --touched` conta o teste ao lado da fonte alterada (TS/JS e Python) |
| **MUST** | `aplicar-migration.md` roda `schema.check_cmd` antes da prévia, fail-closed |
| **SHOULD** | `docs/adaptation-guide.md` + PT e `docs/cli-conventions.md` descrevem os slots e os exits |
| **COULD** | `--self-test` no `slot.sh` (fica para depois: os testes de `tests/` já cobrem) |

---

## Success Criteria

- [ ] `slot.sh` devolve exatamente 6 exits (0, 2, 3, 10, 11, 64) sobre scripts falsos que saem 0, 2, 10, 1, 7 e 127, e o slot vazio, ausente ou sem `sdd/config.yaml`.
- [ ] O comando do slot recebe as 5 variáveis `SDD_*` e os arquivos como argumentos; o teste lê o que o script falso gravou.
- [ ] `test-baseline.sh --touched` sai 2 nos 3 casos novos (`src/foo.ts` → `src/foo.test.ts`; `src/bar.tsx` → `src/bar.spec.tsx`; `pkg/calc.py` → `pkg/test_calc.py`), quando hoje sai 0 nos 3 (linha de base vermelha medida em `9d8ac24`), e sai 0 nos 2 falsos positivos (`test_calc_total` de outro módulo; `lib/foo.test.ts` com `src/foo.ts` alterado).
- [ ] 4 sabotagens (L0, L3, L4 no script e L4 no texto) derrubam, cada uma, um teste nomeado; log em `sdd/reports/evidence/F15_SLOTS/`.
- [ ] Verify Gate numa cópia por `git archive` (sem `.git`) sai 0 com a suíte inteira (hoje 1.669 testes; a contagem só sobe).
- [ ] Os arquivos do produto que esta frente cria ou altera (lista fixa em `tests/test_f15_slots_textos.py`, sem o próprio teste) não casam a família de termos de projeto privado que `tests/test_f12_textos.py` já usa: 0 ocorrências. Termo que identifica um projeto privado de verdade fica só no padrão privado do `publish-gate.sh` (`PUBLISH_GATE_EXTRA_PATTERNS`), nunca num arquivo do repositório.
- [ ] Release `v2.8.0` publicada com `SHA256SUMS.txt` conferido por `shasum -a 256 -c`.

---

## Acceptance Tests

| ID | Padrão | Critério (EARS) | Gate (`kind`) |
|---|---|---|---|
| AT-001 | Event-driven | **When** `bash sdd/bin/slot.sh <chave> [--feature F] [--base ref] [--commit sha] [--arvore pasta] [--dir pasta] [arquivo…]` roda com o slot preenchido, o script **shall** rodar o comando por `bash -c` na pasta onde foi chamado (a raiz do repositório), com os arquivos no fim do comando como argumentos posicionais (um por argumento, espaço no nome preservado), repassar a saída dele e responder: exit 0 ⇒ `RESULTADO: OK`, exit 0; exit 2 ⇒ `RESULTADO: REPROVOU`, exit 2; exit 10 ⇒ `RESULTADO: NADA A MEDIR`, exit 10; cada um com a linha `→` do que fazer | test |
| AT-002 | Unwanted | **If** o comando do slot sai com qualquer código que não é 0, 2 nem 10 (1, 7, 127 de comando não encontrado, morte por sinal), ou o próprio `slot.sh` recebe INT ou TERM, **then** o script **shall** imprimir o exit real (ou o sinal), `RESULTADO: INCONCLUSIVO` e sair 3, nunca 0 | test |
| AT-003 | Optional feature | **Where** a chave está vazia (`""`), ausente do `sdd/config.yaml` (inclusive com comentário na coluna 0 entre a seção e outra chave), ou o arquivo não existe, o script **shall** não rodar nada, imprimir `<chave> vazio: pulado` com o caminho do config, `RESULTADO: PULADO` e sair 11 | test |
| AT-004 | Unwanted | **If** a chave não é uma das 4 (`smoke.before_ok_cmd`, `smoke.before_push_cmd`, `smoke.after_deploy_cmd`, `schema.check_cmd`), uma flag vem sem valor, `--base` ou `--commit` dados não resolvem, o valor do slot tem aspas YAML sem fechar, o comando não passa em `bash -n` (ex.: começa com `|`, aspas do shell sem fechar) ou tem um comentário `#` do shell (os arquivos cairiam nele), **then** o script **shall** sair 64 com a causa e o conserto, sem rodar comando | test |
| AT-005 | State-driven | **While** o comando do slot roda, o ambiente dele **shall** ter `SDD_MOMENTO` (`before_ok`, `before_push`, `after_deploy` ou `schema_check`, da chave), `SDD_FEATURE` (`--feature`, vazio se ausente), `SDD_BASE` (SHA de `--base`, padrão `origin/<project.default_branch>`; vazio com ⚠️ se o padrão não resolve), `SDD_COMMIT` (SHA de `--commit`, padrão `HEAD`; vazio com ⚠️ sem git), `SDD_ARVORE` (`--arvore`, padrão a raiz do repositório: a pasta com a árvore do `SDD_COMMIT`) e `SDD_SLOT_DIR` (`--dir`, ou `${TMPDIR:-/tmp}/sdd-slot-<12 hex>/<feature>` com o hex do caminho físico da pasta git comum, `(cd "$(git rev-parse --git-common-dir)" && pwd -P)`: a mesma a partir de qualquer worktree, subpasta ou caminho com symlink; sem git, do `pwd -P`), e a pasta **shall** existir antes do comando rodar; no momento `before_ok`, a pasta padrão (nunca a de `--dir`) **shall** ser esvaziada antes | test |
| AT-006 | Event-driven | **When** `test-baseline.sh --touched` roda e o diff altera uma fonte que não é teste com um teste ao lado, na mesma pasta e existente no disco (`<nome>.test.<e>` ou `<nome>.spec.<e>` com `<e>` em `.ts`, `.tsx`, `.js`, `.jsx`, `.mjs`, `.cjs`; `test_<nome>.py` ou `<nome>_test.py` para `.py`), o script **shall** contar como do diff a falha nova cujo id começa pelo caminho desse teste (vitest, pytest, deno) ou, no unittest, tem o módulo dele como segmento (`(^|\.)<módulo>\.`), e sair 2 com `🛑 nova:`; os casos `src/foo.ts` → `src/foo.test.ts`, `src/bar.tsx` → `src/bar.spec.tsx` e `pkg/calc.py` → `pkg/test_calc.py` saem 2 (em `9d8ac24`, 0) | test |
| AT-007 | Non-regression | O `test-baseline.sh` **shall continue to**: com `--touched`, tratar como `⚠️ nova, fora do diff` (exit 0) a falha nova de um teste sem relação com o diff, inclusive a de Go, a de `lib/foo.test.ts` quando só `src/foo.ts` mudou e a de um método `test_calc_total` de outro módulo quando só `pkg/calc.py` mudou; contar o teste alterado diretamente como hoje; ignorar `sdd/`; e manter os exits 0, 2, 3, 64, o `PULADO` e a poda do modo completo | test |
| AT-008 | Ubiquitous | A `sdd-release` **shall**: na 0a, item 9, rodar `bash sdd/bin/test-baseline.sh --touched` **depois** do item 4, nunca em paralelo com ele (2 ⇒ abortar; 3 ⇒ WAIVABLE; `PULADO` declarado; as `fora do diff` vão para o bloco); na 0b, citar esse resultado para o teste ao lado do módulo tocado; no item 6b, da pasta da frente, `slot.sh smoke.before_ok_cmd --feature {F} --base origin/{default_branch} --commit <SHA landado> --arvore <worktree temporário>` (2 ⇒ FAIL-candidato; 3 ⇒ aviso; 64 ⇒ aviso "erro de configuração"; 10 e 11 declarados; nunca "ok" fora do 0); no item 7b, depois do "sim" e antes do push, `smoke.before_push_cmd` com os mesmos argumentos (só registra; nenhum exit segura o push); no passo 10, depois de `GIT_TERMINAL_PROMPT=0 git fetch`, `smoke.after_deploy_cmd --commit <SHA publicado>` quando o deploy está confirmado (`deploy-do-sha.sh` 0 ou 3, ou, sem workflow, `deploy.cmd` saiu 0), e não roda, dizendo por quê, quando o deploy saiu 2 ou 4, foi pulado ou não houve publicação (2 ⇒ pergunta `[D1 · não se desfaz]` reverter · corrigir · seguir com motivo · não sei; 3 e 64 ⇒ pendência, nunca ✅; 10 e 11 declarados); e pôr o exit 2 do item 9 na lista de abortar | test |
| AT-009 | Non-regression | O bloco do OK da `sdd-release` **shall continue to** ter os mesmos rótulos, a mesma ordem e uma pergunta só; os testes do diff e o smoke antes do OK entram dentro da linha **Verificações:** (`testes do diff <ok | ok, N fora do diff | inconclusivo — WAIVABLE | pulado — test_cmd vazio>` · `smoke <ok | reprovou — FAIL-candidato | nada a medir | pulado — slot vazio | inconclusivo | erro de configuração>`), e o exemplo do bloco em `references/como-falar.md` também | test |
| AT-010 | Ubiquitous | O passo 4b (`references/aplicar-migration.md`, citado pela `sdd-build`) **shall** rodar `bash sdd/bin/slot.sh schema.check_cmd --feature <F> <os .sql que vão ser aplicados>` depois de "Já está aplicada?" e antes da "Prévia", gravando `$ comando`, a saída e `[exit=N]` (o exit do `slot.sh`, nunca de um `tee` ou `tail`) em `sdd/reports/evidence/<F>/SCHEMA-CHECK.log`; e de novo sobre os arquivos que a prévia acrescentar, antes do bloco de confirmação; 0 ⇒ segue; 10 ⇒ segue e diz "nada a conferir"; 11 ⇒ "checagem de schema pulada: slot vazio"; 2 ⇒ não aplica, mostra a saída e volta ao SQL; 3 ou 64 ⇒ não aplica e diz que o problema é da ferramenta ou do config, não do SQL; o bloco de confirmação ganha a linha **Checagem:** com o resultado | test |
| AT-011 | Ubiquitous | `sdd/config.example.yaml` **shall** trazer as seções `smoke:` e `schema:` com os 4 slots em `""` e comentário (o que cada um recebe, o contrato de exit, uma linha só, sem `#` nem `|`/`;`/`&&` no comando); `docs/adaptation-guide.md` e `docs/pt-BR/adaptation-guide.md` **shall** descrevê-los; `docs/cli-conventions.md` **shall** ter a linha do `slot.sh` na tabela de exits; `sdd/WORKFLOW_CONTRACTS.yaml` **shall** ter o contrato `slot`; `MANIFEST.txt` **shall** listar `sdd/bin/slot.sh` e os testes novos; o texto que esta frente acrescenta aos arquivos do produto **shall not** casar a família de termos de projeto privado de `tests/test_f12_textos.py` (o texto anterior que já usa o Supabase como caminho provado da migration, F3, e o `deno` como um dos formatos de saída de teste, F7, não é termo de projeto privado e fica de fora) | test |
Considerados: **While** em AT-005 (o estado do ambiente durante o comando); **If/Then** em AT-002 e AT-004 (comando que falha fora do contrato, chamada errada); **Where** em AT-003 (slot ligado × desligado, matriz no teste). Não-regressão em AT-007 e AT-009, porque a frente mexe no `test-baseline.sh` e no bloco do OK, que já têm contrato.

---

## Clarifications

### Session 2026-11-09

- [x] (escopo) As 3 lacunas numa frente só? → sim, F15_SLOTS, release `v2.8.0` (brainstorm, decisão 1).
- [x] (terminologia) Nomes dos slots → `smoke.before_ok_cmd`, `smoke.before_push_cmd`, `smoke.after_deploy_cmd`, `schema.check_cmd`; reabertos por decisão do Roberto (caíram na F13 e na F12); integrado em Goals e AT-004.
- [x] (edge cases) Exit 2 do smoke por momento → FAIL-candidato antes do OK; só registro antes do push; D1 depois do deploy; integrado em AT-008.
- [x] (integrações) Os 3 smokes amarrados? → independentes, com `SDD_SLOT_DIR` comum; integrado em AT-005.
- [x] (restrições) Rigor → L3 aborta (3 = WAIVABLE); L4 fail-closed; integrado em AT-008 e AT-010.
- [x] (escopo) Linguagens do teste ao lado → TS/JS e Python; Go fora, limite declarado (o `go test` não põe o arquivo no id da falha); integrado em AT-006 e AT-007.
- [x] (dados) Exit do slot vazio → 11 `PULADO`, distinto do 0 `OK`; integrado em AT-003.
- [x] (revisão do DESIGN, 2026-11-09) 20 notas do revisor fresco; as que mudam o aceite entraram aqui (v1.1): AT-002 (sinal no próprio script), AT-003 (comentário na coluna 0), AT-004 (`bash -n`, `#`, `--base`/`--commit` que não resolvem), AT-005 (`SDD_ARVORE`, fórmula da pasta comum, `before_ok` esvazia), AT-006/AT-007 (casamento com âncora e os 2 falsos positivos), AT-008 (6b no worktree temporário por `--arvore`, item 9 em sequência, tabela do passo 10, `fetch`, 64), AT-009 (texto da linha Verificações e o exemplo do `como-falar.md`), AT-010 (reconferir o que a prévia acrescentar, log, ação de 3/64), AT-011 (lista fixa, sem termo privado no repositório). Ledger completo no DESIGN.
- [x] (avaliação ciclo 1, 2026-11-09) ressalva 3: o AT-011 passou a dizer "o texto que esta frente acrescenta"; o achado 1 (flag seguida de flag) e o 2 (`#` no meio da palavra) são consertos do código, sem mudar o aceite.
- Nota: o bloco do OK não ganha rótulo novo (AT-009); a F14 fixou rótulos, ordem e pergunta única em `tests/test_contrato_build_release.py:46`.

### Session 2026-11-09 (governança)

- [x] (governança) revisor fresco → N.A.: ferramenta de desenvolvimento, sem tema de governança; fronteira "só o permitido mudou", bloco válido.

---

## Verify Gate

```yaml
verify_gate:
  kind: test
  cmd: "T=$(mktemp -d) && git archive HEAD | tar -x -C $T && PUBLISH_GATE_MODE=ci bash scripts/publish-gate.sh $T && cd $T && SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover -s tests -p 'test_*.py'"
  pass_when: "exit 0"
  threshold: "—"
  manual_fallback: "—"
```

Cobertura: AT-001 a AT-005 em `tests/test_slot.py` (scripts falsos, repositório temporário com 2 worktrees, subpasta, symlink e pasta sem git para AT-005); AT-006 e AT-007 em `tests/test_test_baseline.py`; AT-008 a AT-011 em `tests/test_f15_slots_textos.py` (texto das skills, config, docs, MANIFEST e o grep anti-RDD), com `tests/test_contrato_build_release.py` continuando verde para AT-009. A cópia por `git archive` não tem `.git`: os testes que precisam de git montam o próprio repositório temporário.

---

## Out of Scope

- Coluna nova em `## Migrations aplicadas` e `report-lint` exigindo a checagem de schema.
- A release rodar `schema.check_cmd` de novo.
- `--touched` rodando só os testes do diff (o Open roda a suíte e filtra).
- Teste em espelho (`tests/test_foo.py` para `src/foo.py`) e o teste ao lado em Go.
- A 2ª pergunta "rodar o smoke?" no OK.
- `--self-test` no `slot.sh`.
- L1, L2, L5–L9 do inventário de saída e a ligação dos slots no privado.

---

## Constraints

| Type | Constraint | Impact |
|---|---|---|
| Technical | bash 3.2 + Python ≥ 3.9 stdlib; sem `declare -A`, `mapfile`, `${var,,}` | `tests/test_bash32.py` confere |
| Technical | `docs/cli-conventions.md`: símbolo com palavra, erro com causa e conserto, `RESULTADO:` + `→` | todo caminho do `slot.sh` termina assim |
| Technical | instalação antiga sem os slots no `config.yaml` = vazio = PULADO | compatível sem migração do config |
| Público | repositório público: nada da RDD (caminho, tabela, edge, projeto, `scripts/…`) | grep anti-RDD no gate (AT-011) |
| Processo | não tocar as worktrees `sdd-open-docs-f16` e `sdd-open-docs-f21`; push só com "sdd-open autorizado" | documentos SDD na branch `docs/f15-slots` |
| Skills | skill tocada sobe `metadata.version` (`scripts/check-versions.py`) | `sdd-release` e `sdd-build` com bump minor |

---

## Technical Context

| Aspect | Value | Notes |
|---|---|---|
| **Deployment Location** | `sdd/bin/slot.sh` (novo), `sdd/bin/test-baseline.sh`, `sdd/config.example.yaml`, `.agents/skills/sdd-release/`, `.agents/skills/sdd-build/` (`SKILL.md` 4b e `references/aplicar-migration.md`), `docs/`, `tests/`, `MANIFEST.txt` | produto do Open; o `init` copia `sdd/bin/*` e o `doctor` já compara cada arquivo de `sdd/bin/` com o pacote |
| **KB Domains** | nenhum | o Open não tem `sdd/kb/`; a skill `sdd-kb` cria uma base quando o projeto quiser |
| **IaC Impact** | None | CI existente (`publish-gate.yml`, `release.yml`) |
| **LLM Prompts** | false | nenhum prompt de runtime; "smoke" e "schema" são comandos do projeto |
| **CONTEXTO de domínio** | nenhum (pulado: o Open não tem `sdd/patterns/dominio.md`) | `contexto-lint.sh --sugerir` → PULAR |
| **Governança** | N.A. — ferramenta de desenvolvimento (slots de smoke e de checagem de schema, test-baseline), sem dinheiro, saldo, lançamento, NF, tributo, folha nem dado pessoal | revisor fresco, 2026-11-09 |

---

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|---|---|---|---|
| A-001 | Arquivo novo de `sdd/bin/` chega a quem já instalou: o `sdd_faltantes` do `init` completa o que falta (`bin/sdd-open.sh:587-593`); o laço do `doctor` em `:823-829` só compara os que existem | o privado não receberia o `slot.sh` | [x] `bin/sdd-open.sh:587-593` |
| A-002 | Os ids de falha de vitest, deno, pytest e unittest trazem o caminho ou o nome do arquivo de teste | o par fonte → teste não casaria; os casos do AT-006 provam | [x] `test-baseline.sh:146-176` |
| A-003 | `git rev-parse --git-common-dir` é o mesmo em todas as worktrees do repositório | a pasta comum do smoke mudaria entre a frente e o worktree temporário do passo 5 | [ ] (teste do AT-005) |

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---|---|---|
| Problem | 3 | as 3 lacunas, com linha e arquivo, e o que trava a fase 3 |
| Users | 3 | 3 papéis com a dor de cada um |
| Goals | 3 | MUST/SHOULD/COULD com o contrato de exit fechado |
| Success | 3 | contagens, exits e a linha de base vermelha |
| Scope | 2 | fora de escopo explícito; o Go entrou e saiu no Define |
| **Total** | **14/15** | |

---

## Open Questions

None - ready for Design.

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | 2026-11-09 | define-agent | Initial version |
| 1.1 | 2026-11-09 | define-agent | notas da revisão fresca do DESIGN (Advisor Ledger do DESIGN); termo de projeto privado retirado do critério anti-RDD |
| 1.2 | 2026-11-09 | define-agent | avaliação ciclo 1, ressalva 3: AT-011 fala do texto novo, não do arquivo inteiro (`sdd/reviews/AVALIACAO_F15_SLOTS_20261109-2227.md`) |

---

## Next Step

**Ready for:** `/sdd-design sdd/features/DEFINE_F15_SLOTS.md` — UX review pulado: a feature não tem interface (scripts, slots de config e texto de skill).
