# DEFINE: F3 Build e Release do sdd-open

> Migration aplicada só conta quando lida de volta do banco (referência na `sdd-build`, seção `## Migrations aplicadas` exigida pelo `report-lint`, `LM-004`), o OK da `sdd-release` vira um bloco único que diz se o deploy espera os testes (por script com fixtures) e qual banco mudou, e o `doctor` avisa quando skills e `sdd/bin/` do projeto ficaram mais velhos que os do pacote.

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | F3_BUILD_RELEASE |
| **Date** | 2026-10-29 |
| **Author** | SDD Define by RDD (sessão com Roberto Dias Duarte) |
| **Status** | Ready for Design |
| **Clarity Score** | 14/15 |

---

## Problem Statement

No sdd-open, o Design lista a migration, o Build grava o `.sql` e a Release faz o push — e nada obriga alguém a executá-la no banco e lê-la de volta: o `report-lint.py` só confere os ATs, então um BUILD_REPORT com migration "aplicada (exit 0)" passa, e o código chega a produção chamando coluna que não existe ou mexendo no projeto errado. No momento do único OK, a `sdd-release` mostra uma lista solta que não diz se o deploy espera os testes nem qual banco mudou; e quem já tem o sdd-open instalado não recebe nada disso, porque o `init` nunca sobrescreve `sdd/` nem `.agents/skills/<skill>`, sem que nenhum comando avise.

---

## Target Users

| User | Role | Pain Point |
|---|---|---|
| Usuário/aluno que roda a `sdd-build` em projeto com banco (Supabase) | Grava e aplica migrations durante o Build | `exit 0` confundido com prova; migration publicada sem ter rodado; projeto errado sem undo |
| Quem dá o OK na `sdd-release` | Aprova push e deploy | Aprova sem saber que o workflow publica mesmo com teste vermelho e sem ver qual banco mudou |
| Quem já tem o sdd-open instalado | Atualizou o pacote e roda `init`/`doctor` | Continua com `sdd-build`, `sdd-release` e `report-lint.py` velhos sem saber |
| Mantenedor do sdd-open | Roberto e os agentes de F4–F6 | Precisa que regra nova em `sdd/` e skill nova sejam provadas por teste e não quebrem os contratos existentes |

---

## Goals

| Priority | Goal |
|---|---|
| **MUST** | `sdd/bin/report-lint.py` reprova (exit 1) BUILD_REPORT que lista migration sem linha válida em `## Migrations aplicadas`: mesmo caminho, projeto `nome · ref`, data `AAAA-MM-DD`, prova por log abrível de `evidence/{F}/` ou `recibo: nome AAAA-MM-DD`; migration = `*.sql`, `migrations/` no caminho ou glob de `layers.sql` quando preenchido |
| **MUST** | Os 14 contratos de `tests/test_report_lint.py` continuam verdes; relatório sem migration não muda de resultado |
| **MUST** | `.agents/skills/sdd-release/scripts/deploy-espera-testes.py` responde `SIM` (0) / `NAO` (1) / `NAO_SEI` (2) / `NAO_SE_APLICA` (3) lendo `.github/workflows/*`, com motivo citando workflow, job e passo; fixtures dos dois lados em `tests/` (derivadas do Wordpress, anonimizadas, e do `release.yml` do open) |
| **MUST** | `.agents/skills/sdd-release/SKILL.md` 2.2.0: o item 7 da FASE 1 vira o bloco único do "go" (O que sobe · O que muda em produção · O push publica sozinho? · O deploy espera os testes? · Banco · Verificações · veredito 0d/WAIVED · `feature_id` · uma pergunta), com o script chamado e `NAO_SEI` dito como "não consegui afirmar" |
| **MUST** | `.agents/skills/sdd-build/references/aplicar-migration.md` portada (sem `sdd/ambiente.md`, prova em log ou recibo, sem CNPJ literal) e `sdd-build` 2.1.0 mandando lê-la quando o manifest tem migration |
| **MUST** | `sdd/templates/BUILD_REPORT_TEMPLATE.md` com a seção condicional `## Migrations aplicadas`; `sdd/playbook.md` com `LM-004` no `## Sempre` |
| **MUST** | `doctor`: ⚠️ por skill do projeto com `metadata.version` abaixo da do pacote e por `sdd/bin/*` diferente do pacote, com o remédio "apague e rode init"; ✅ quando tudo em dia; continua saindo 0 |
| **MUST** | Nenhuma regressão: 242 testes, exits do `verify-gate.sh`, `sdd/fixtures/` idênticas, `playbook-lint.sh --self-test` 0, `sync` idempotente, 16 skills, publish-gate e `check-versions` verdes |
| **MUST** | 1 sabotagem por script alterado no BUILD_REPORT (`report-lint.py`, `deploy-espera-testes.py`, `bin/sdd-open.sh`) |
| **SHOULD** | Teste de contrato que confere o texto das duas skills (campos do bloco, chamada do script, leitura da referência, versão) |
| **COULD** | Fixture extra de `if: always()` e de workflow reutilizável além dos casos mínimos |

---

## Success Criteria

- [ ] `python3 -B -m unittest discover -s tests -p 'test_*.py'` sai 0 no piso `SDD_TEST_BASH=/bin/bash /usr/bin/python3` (Python 3.9.6 + bash 3.2.57) e no `ubuntu-latest` do CI, com mais de 242 testes (242 atuais + os novos) e 0 skip além do `GateInteiro` sem gitleaks.
- [ ] `report-lint.py` sai 1 em cada uma das fixtures de migration inválida (sem linha, prova declarativa, "exit 0", célula vazia, log inexistente, projeto sem `·`, sem data) e 0 nas válidas (log, recibo, "já aplicada em", migration por `layers.sql`).
- [ ] `deploy-espera-testes.py` dá o `RESULTADO` esperado em 100% das fixtures (mínimo: 1 SIM por `needs:`, 1 SIM no mesmo job com `continue-on-error` só em passo que não é teste, 4 NAO — sem teste, `continue-on-error`, `|| true`, `exit 0` fixo —, 1 NAO_SEI, 1 NAO_SE_APLICA).
- [ ] 3 de 3 sabotagens registradas no BUILD_REPORT com a alteração (sed por padrão), o teste nomeado que ficou vermelho e a reversão por `git checkout` com a suíte verde de novo.
- [ ] `git diff v2.2.2 -- sdd/bin/verify-gate.sh sdd/fixtures/ scripts/publish-gate.sh scripts/publish-gate-patterns.txt .github/` vazio ao fim da F3.
- [ ] `python3 scripts/check-versions.py --base v2.2.2 --base-obrigatoria` sai 0 com `sdd-build` 2.1.0 e `sdd-release` 2.2.0.
- [ ] `bash sdd/bin/playbook-lint.sh --self-test` e `bash sdd/bin/playbook-lint.sh sdd/playbook.md` saem 0 com `LM-004`.
- [ ] O Verify Gate abaixo sai 0 com `--strict`; `python3 sdd/bin/report-lint.py sdd/reports/BUILD_REPORT_F3_BUILD_RELEASE.md` sai 0.
- [ ] Depois do merge em `main`, `gh release view <tag> -R robertodiasduarte/sdd-open` mostra `SHA256SUMS.txt` e `shasum -a 256 -c SHA256SUMS.txt` sai 0 sobre o pacote baixado.

---

## Acceptance Tests

| ID | Pattern | Criterion (EARS) | Gate (`kind`) |
|---|---|---|---|
| AT-001 | Event-driven | **When** `report-lint.py` reads a BUILD_REPORT whose `## Files…` section lists `supabase/migrations/<ts>_x.sql` and whose `## Migrations aplicadas` has a row with the same path, `nome · ref`, a `AAAA-MM-DD` date and a proof cell citing an existing `evidence/{F}/*.log` whose first line starts with `$ `, the system **shall** exit 0 | test |
| AT-002 | Unwanted | **If** a migration path listed in a section titled `## Files…`, `## Arquivos…` or containing `Manifest` has no row with the same path in `## Migrations aplicadas` (or the section is absent), **then** `report-lint.py` **shall** exit 1 with a `🛑` line naming that path | test |
| AT-003 | Unwanted | **If** the proof cell of a migration row is empty, declarative (`por raciocínio`, `deve funcionar`), says `exit 0`, or cites a log that does not exist, is empty or lacks the `$ ` first line, **then** `report-lint.py` **shall** exit 1 naming the migration | test |
| AT-004 | Unwanted | **If** the project cell of a migration row lacks a name or a ref separated by `·`, or the row has no `AAAA-MM-DD` date, **then** `report-lint.py` **shall** exit 1 naming the migration | test |
| AT-005 | Event-driven | **When** the proof cell is `recibo: <nome> AAAA-MM-DD`, the system **shall** accept it even if the feature's DEFINE has `kind: test`, and **when** the date cell reads `já aplicada em AAAA-MM-DD`, the system **shall** accept the date | test |
| AT-006 | Optional feature | **Where** `sdd/config.yaml` has `layers.sql` filled (e.g. `db/changes/**`), a listed path matching that glob **shall** be treated as a migration; **where** the slot is empty or the config is absent, only `*.sql` and `migrations/` **shall** count | test |
| AT-007 | Event-driven | **When** a Files row for a migration has the action `Delete`/`Removido`, or the report lists no migration at all, the system **shall** not require a `## Migrations aplicadas` row for it | test |
| AT-008 | Non-regression | `report-lint.py` **shall continue to** pass the 14 contracts of `tests/test_report_lint.py` (exits 0/1/64 and messages for ATs, recibo, avaliador) | test |
| AT-009 | Event-driven | **When** `deploy-espera-testes.py <raiz>` reads workflows where every job that publishes runs a blocking test step before publishing in the same job, or `needs:` a job with a blocking test step (fixture: `release.yml` of the sdd-open), the system **shall** print `RESULTADO: SIM` and exit 0 | test |
| AT-010 | Unwanted | **If** a workflow triggered by push publishes (rsync/deploy) with no test step in the job and no `needs:` on a tested job (fixture derived from `deploy-hostinger.yml`, anonymized), **then** the script **shall** print `RESULTADO: NAO` naming the workflow file and the job, and exit 1 | test |
| AT-011 | Unwanted | **If** the only test step that guards publishing has `continue-on-error: true`, ends with `\|\| true`, or runs under `set +e` ending with a fixed `exit 0` (fixture derived from `ci-deno-test.yml`), or the publishing job has `if: always()`, **then** the script **shall** print `RESULTADO: NAO` naming the step or job and the reason, and exit 1 | test |
| AT-012 | Event-driven | **When** `continue-on-error: true` appears only on steps that are not tests and a blocking test step precedes the publishing step, and a lint step is the only other check, the system **shall** print `RESULTADO: SIM` (no false `NAO` from the non-test step, no `SIM` credited to lint alone) | test |
| AT-013 | Unwanted | **If** a publishing job depends on a `workflow_run` trigger or a reusable workflow (`uses: ./.github/workflows/…`), **then** the script **shall** print `RESULTADO: NAO_SEI` with the reason and exit 2 | test |
| AT-014 | Event-driven | **When** the root has no `.github/workflows/` or no workflow publishes, the system **shall** print `RESULTADO: NAO_SE_APLICA` and exit 3; **if** the argument is not a directory, **then** it **shall** exit 64 | test |
| AT-015 | Event-driven | **When** `sdd-open.sh doctor` runs in a project whose `.agents/skills/sdd-build/SKILL.md` has a `metadata.version` lower than the package's, the system **shall** print a ⚠️ line with the skill name, both versions and "apague .agents/skills/sdd-build e rode init", and exit 0 | test |
| AT-016 | Event-driven | **When** `doctor` runs in a project whose `sdd/bin/report-lint.py` differs from the package's, the system **shall** print a ⚠️ line naming the file with "se você não editou, apague e rode init"; **when** every skill and `sdd/bin/*` match the package, it **shall** print one ✅ line; in both cases it **shall** exit 0 ending with `RESULTADO:` | test |
| AT-017 | Event-driven | **When** the contract test reads `.agents/skills/sdd-release/SKILL.md`, the system **shall** find `metadata.version` `2.2.0`, the call to `scripts/deploy-espera-testes.py`, the six labels of the go block, `NAO_SEI` ⇒ "não consegui afirmar", "Banco:" read from `## Migrations aplicadas`, the 0d verdict/WAIVED and `feature_id` inside the block, and a single question | test |
| AT-018 | Event-driven | **When** the contract test reads the `sdd-build` skill, the system **shall** find `metadata.version` `2.1.0`, the instruction to read `references/aplicar-migration.md` when the manifest has a migration, and in the reference the four rules, the stop on divergence and the `## Migrations aplicadas` row; and **shall** find no `sdd/ambiente.md` in it | test |
| AT-019 | Event-driven | **When** the tree is checked, `sdd/templates/BUILD_REPORT_TEMPLATE.md` **shall** contain the `## Migrations aplicadas` section with the columns Arquivo · Projeto (nome · ref) · Aplicada em · Prova por leitura, and `sdd/playbook.md` **shall** contain `LM-004` under `## Sempre` passing `playbook-lint.sh` | test |
| AT-020 | Unwanted | **If** any file in the tree matches `scripts/publish-gate-patterns.txt` outside the `example.com/.org/.net` exemption (e.g. a literal CNPJ in `aplicar-migration.md` or a real host in a workflow fixture), **then** `PUBLISH_GATE_MODE=ci bash scripts/publish-gate.sh` **shall** exit non-zero; on the F3 tree it **shall** exit 0 | test |
| AT-021 | Event-driven | **When** `check-versions.py --base v2.2.2 --base-obrigatoria` runs on the F3 tree, the system **shall** exit 0 | test |
| AT-022 | Non-regression | The system **shall continue to** pass the 242 existing tests, return exits 0/2/3/4/5/64 from `verify-gate.sh`, keep `sdd/fixtures/` byte-identical, keep `playbook-lint.sh --self-test` at 0, count 16 skills and leave `git status --porcelain` empty after `init --yes` + `sync --yes` | test |
| AT-023 | Unwanted | **If** a contract is broken on purpose in `report-lint.py`, `deploy-espera-testes.py` or the `doctor` (sabotage), **then** at least one named test **shall** fail, and reverting it with `git checkout` **shall** turn the suite green again | test |

---

## Clarifications

### Session 2026-10-29

- [x] (Constraints) O `cmd` do Verify Gate não pode ter aspas duplas internas (`verify-gate.sh` só tira as aspas das pontas e roda com `bash -c` da raiz) → `cmd` do SESSION_PROMPT usado literalmente; integrado em Verify Gate.
- [x] (Terminology) "Hash diferente" do Brainstorm (decisão 13) = conteúdo do arquivo diferente do pacote, byte a byte; o Design escolhe `cmp` ou SHA-256 → integrado em AT-016.
- [x] (Edge cases) O Brainstorm aceita `recibo:` "em qualquer `kind` de gate" só na linha de migration; o recibo dos ATs continua restrito a `manual-ux` (contrato `test_recibo_fora_de_manual_ux`) → integrado em AT-005 e AT-008.
- [x] (Data model) "Mesmo caminho" = o texto entre crases na tabela de arquivos igual ao da 1ª célula da linha de migration (sem normalizar `…` abreviado) → integrado em AT-001/AT-002; risco em A-002.
- [x] (Done signal) Uma sabotagem por script alterado: `report-lint.py`, `deploy-espera-testes.py` e `bin/sdd-open.sh` (`doctor`) = 3 → integrado em Success Criteria e AT-023.
- [x] (UX flow) As duas skills são texto lido pelo agente; a obediência do agente não é executável em teste → AT-017/AT-018 conferem o contrato escrito; obediência em Assumptions (A-003).

---

## Verify Gate

```yaml
verify_gate:
  kind: test
  cmd: "T=$(mktemp -d) && git archive HEAD | tar -x -C $T && PUBLISH_GATE_MODE=ci bash scripts/publish-gate.sh $T && cd $T && python3 -B -m unittest discover -s tests -p 'test_*.py'"
  pass_when: "exit 0"
  threshold: "—"
  manual_fallback: "—"
```

O gate só enxerga o que está commitado (`git archive HEAD`): o Build commita na branch antes de rodar. `PUBLISH_GATE_MODE=ci` porque o modo padrão exige a camada privada de padrões. A Release (último Success Criterion) é conferida depois do merge, fora deste gate, com `gh release view` e `shasum -a 256 -c`.

---

## Out of Scope

- Redesenhar a CLI ou o `config.yaml`; verbo `upgrade`; `doctor` que conserta sozinho; `doctor` comparando templates, playbook ou fixtures.
- CI além do GitHub Actions; parser de YAML completo.
- `report-lint` lendo o SQL, acusando DDL destrutivo ou acessando o banco.
- Passos próprios para Prisma, Flyway e Rails (fica a frase "mesmo protocolo com os comandos dela").
- `sdd/ambiente.md` e a chave `- banco:` do starter.
- Camada "Como falar com o aluno" nas skills nativas, `design-lint`/`handoff-lint` (F4); `sdd-kb` (F5); docs, README, `AGENTS.md.tmpl` (F6).
- Curadoria do playbook além do `LM-004`.
- Alterar o sdd-starter; modo `briefs`; teste no Windows.

---

## Constraints

| Type | Constraint | Impact |
|---|---|---|
| Technical | bash 3.2 sem `declare -A`/`mapfile`/`readlink -f`/`grep -P`, sem zsh nem symlink; Python ≥ 3.9 só stdlib; `python3 -B` | Script, lint e testes rodam no macOS de fábrica e no runner |
| Technical | G2 do publish-gate: nenhum literal casa com `scripts/publish-gate-patterns.txt` fora de `example.*`; CPF/CNPJ/telefone/`git@host` montados em tempo de execução; hosts em `.invalid` | Fixtures do Wordpress anonimizadas; CNPJ da referência reescrito sem número |
| Technical | G3: `MANIFEST.txt` allowlist nos dois sentidos, ordem `LC_ALL=C`; sem `.gitignore` | Arquivo novo declarado no mesmo commit; `git add` por nome; `sdd/features|handoffs|reports/` fora do commit |
| Technical | `init`/`sync` copiam a pasta inteira da skill com cabeçalho `sdd-open:generated` | Fixtures e testes em `tests/` na raiz, nunca dentro da skill; o script tem de rodar também como cópia gerada |
| Technical | `sdd/` é território do usuário: `init` nunca sobrescreve | A regra nova só chega a instalação nova; o aviso do `doctor` (AT-015/016) cobre as existentes |
| Technical | Skill alterada sobe `metadata.version` contra `v2.2.2` | `sdd-build` 2.1.0, `sdd-release` 2.2.0 |
| Other | Comandos remotos com `GIT_TERMINAL_PROMPT=0`; push em `main` só com OK explícito citando "sdd-open", após PR com CI verde | A Release depende desse OK |

---

## Technical Context

| Aspect | Value | Notes |
|---|---|---|
| **Deployment Location** | `sdd/bin/report-lint.py`, `sdd/templates/BUILD_REPORT_TEMPLATE.md`, `sdd/playbook.md`, `.agents/skills/sdd-build/` (SKILL.md + `references/aplicar-migration.md`), `.agents/skills/sdd-release/` (SKILL.md + `scripts/deploy-espera-testes.py`), `bin/sdd-open.sh` (`doctor`), `tests/` (novos e `test_report_lint.py`, `test_sdd_open.py`), `MANIFEST.txt` | Fonte: `/Users/robertoduarte/rdd-public/sdd-starter` em `17c69c4`; amostras em `/Users/robertoduarte/RDD/Wordpress` |
| **KB Domains** | Supabase CLI/MCP (migration list, db push --dry-run, apply_migration, execute_sql); GitHub Actions (`needs:`, `continue-on-error`, `if: always()`, `workflow_run`, reusable workflows) | Texto da referência do starter; semântica do Actions só no que o script lê |
| **IaC Impact** | None | Workflows da F1 sem mudança; o push em `main` publica a Release sozinho porque toca `sdd/**`, `.agents/skills/**` e `bin/**` |
| **LLM Prompts** | false | Nenhum prompt de runtime: lint, script, testes e texto de skill lido pelo agente de desenvolvimento |

---

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|---|---|---|---|
| A-001 | Os 242 testes atuais passam no piso antes da F3 | O Build partiria de base vermelha | yes — handoff da F2 (`41c6169`): 242 OK, 0 skip; reconferir no início do Build |
| A-002 | O agente escreve na tabela de arquivos e na linha de migration o mesmo caminho completo | Relatório real com `migrations/…_x.sql` abreviado reprovaria | no — a referência e o template dizem "caminho completo"; a mensagem do lint diz qual caminho faltou |
| A-003 | O agente segue o bloco do "go" e a referência de migration como escritos | O contrato escrito passaria e o agente faria outra coisa | no — não executável; mitigado por AT-017/AT-018 |
| A-004 | Palavras-chave de "teste" e "publicar" cobrem os workflows reais vistos (Wordpress, sdd-open) | Script daria NAO_SEI ou NAO onde há SIM | yes — 4 workflows lidos no Brainstorm; o resto cai em NAO_SEI, nunca em SIM |
| A-005 | `metadata.version` está no frontmatter de toda skill do pacote | `doctor` não teria o que comparar | yes — `check-versions.py` já exige |
| A-006 | Relatório antigo com migration e sem a seção, se relintado, passa a reprovar | Um build em andamento na atualização precisaria preencher a seção | yes — aceito: a `sdd-release` só linta o relatório da feature corrente |

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---|---:|---|
| Problem | 3 | Três dores concretas, com onde cada uma acontece no código |
| Users | 3 | Quatro papéis, cada um com dor específica |
| Goals | 3 | MUST/SHOULD/COULD vindos das 4 decisões e dos 2 checkpoints |
| Success | 2 | Todos observáveis; a obediência do agente às duas skills só é provada pelo contrato escrito |
| Scope | 3 | YAGNI e destinos (F4, F5, F6) registrados |
| **Total** | **14/15** | |

Minimum to proceed: **12/15**.

---

## Open Questions

None - ready for Design.

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | 2026-10-29 | SDD Define by RDD | Initial version |

---

## Next Step

Execute o **SDD Design by RDD**.
