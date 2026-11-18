# DESIGN: F3 Build e Release do sdd-open

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | F3_BUILD_RELEASE |
| **Date** | 2026-10-29 |
| **Author** | SDD Design by RDD |
| **BRAINSTORM** | `sdd/features/BRAINSTORM_F3_BUILD_RELEASE.md` |
| **DEFINE** | `sdd/features/DEFINE_F3_BUILD_RELEASE.md` |
| **UX REVIEW** | `N/A` |
| **LLM Prompts** | false |
| **Status** | Ready for Build |

---

## Architecture Overview

```text
                 BUILD (sdd-build 2.1.0)                              RELEASE (sdd-release 2.2.0)
 ┌────────────────────────────────────────────┐        ┌──────────────────────────────────────────────┐
 │ manifest tem migration?                     │        │ FASE 0a.5  report-lint.py (agora com a regra │
 │   └─ sim → references/aplicar-migration.md  │        │            de migration)                     │
 │        descobrir → já aplicada? → prévia →  │        │ FASE 1 item 7 = BLOCO ÚNICO DO "GO"          │
 │        1 confirmação → aplicar → PROVAR     │        │   O que sobe · O que muda em produção        │
 │        POR LEITURA → evidence/<F>/MIG-n.log │        │   O push publica sozinho?                    │
 │                │                            │        │   O deploy espera os testes? ◄───────────┐   │
 │                ▼                            │        │   Banco: ◄── ## Migrations aplicadas      │   │
 │ BUILD_REPORT  ## Files Created …            │        │   Verificações · veredito 0d · feature_id │   │
 │               ## Migrations aplicadas ──────┼──────► │   Posso finalizar?                        │   │
 └────────────────┬───────────────────────────┘        └──────────────────────────────────────────┼───┘
                  │                                                                                │
                  ▼                                                                                │
   sdd/bin/report-lint.py                                 scripts/deploy-espera-testes.py <raiz> ──┘
   ATs (inalterado) + migrations:                           lê .github/workflows/*.yml (mini-YAML)
   Files… ∩ (*.sql | migrations/ | layers.sql)              SIM 0 · NAO 1 · NAO_SEI 2 · NAO_SE_APLICA 3
   ⇒ linha com nome·ref, data, log|recibo                   RESULTADO: … + → frase pronta para o bloco
   exit 0 · 1 · 64

   bin/sdd-open.sh doctor ── compara projeto × pacote ──► ⚠️ skill com metadata.version menor
                                                          ⚠️ sdd/bin/* diferente (cmp)  · ✅ tudo em dia
   sdd/playbook.md  LM-004 (## Sempre)        sdd/templates/BUILD_REPORT_TEMPLATE.md  ## Migrations aplicadas
```

---

## Components

| Component | Purpose | Technology / Pattern | Inputs | Outputs | Dependencies |
|---|---|---|---|---|---|
| Regra de migration no `report-lint.py` | Reprovar migration listada sem registro provado | Python 3.9 stdlib; funções novas ao lado de `check()`; reuso da checagem de log | BUILD_REPORT, `sdd/config.yaml` (`layers.sql`), `sdd/reports/evidence/<F>/` | `🛑` por migration + exit 1, ou nada | `report-lint.py` atual |
| `deploy-espera-testes.py` | Responder "o deploy espera os testes?" com prova | Python 3.9 stdlib; mini-parser de YAML por indentação; regex de comando | `<raiz>/.github/workflows/*.yml\|*.yaml` | Uma linha por job que publica, `RESULTADO:` + `→`, exit 0/1/2/3/64 | Nenhuma |
| Bloco do "go" na `sdd-release` | Uma parada só, com os campos afirmados pela skill | Texto de skill (Markdown) | Fase 0/1, saída do script, BUILD_REPORT | O bloco + "Posso finalizar (push + deploy + verificar)?" | Script, regra do lint |
| Referência `aplicar-migration.md` | Procedimento de aplicar e provar migration | Texto de referência (Markdown) | Manifest com migration | Linha em `## Migrations aplicadas` + log `MIG-nnn.log` | Template, lint |
| Passo 4b da `sdd-build` | Mandar ler a referência quando o manifest tem migration | Texto de skill | DESIGN | — | Referência |
| Template + `EVIDENCIA.md` | Lugar e formato do registro | Markdown | — | Seção condicional | — |
| `LM-004` | Memória do projeto: exit 0 não prova migration | Bullet do playbook (gramática do `playbook-lint.sh`) | — | — | — |
| Aviso de versão no `doctor` | Dizer a quem já instalou que o pacote está mais novo | bash 3.2 + `awk` + `cmp` | `$PKG` e `$ROOT` | ⚠️ por item, ✅ se em dia; exit 0 | `skills_da_fonte`, `warn`, `ok` |
| Testes | Provar cada contrato dos dois lados | `unittest` + `apoio.Sandbox` | Fixtures inline e `release.yml` real | 242 + novos verdes | Tudo acima |

---

## Key Decisions

### Decision 1: Onde o lint procura migration e como casa o caminho

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-10-29 |
| **Source** | DEFINE (AT-001, AT-002, AT-006, AT-007) + BUILD_REPORTs reais do Wordpress |

**Context:** Os relatórios reais têm títulos variados (`## Files Created / Modified`, `## Files Changed`, `## Arquivos …`, `## … Manifest …`) e colunas variadas (`# · Arquivo · Ação · Verificação`), e citam `.sql` em outras seções (Advisor, notas).

**Choice:** Seções cujo título casa `^##\s+(files\b|arquivos\b|.*manifest)` (sem diferenciar maiúsculas), até o próximo `## ` — na v1.1, também com número ou prefixo antes (`## 2. Arquivos criados`, `## Fase A — Files Created/Modified`, títulos reais que a revisão achou com 3 migrations cada). Em cada linha de tabela, só o **primeiro** token entre crases é o caminho; linha com uma célula igual a `delete`, `deleted`, `removido`, `removida`, `excluído`, `excluido` é ignorada. Migration = termina em `.sql`, ou tem o segmento `migrations/`, ou casa (`fnmatch.fnmatchcase`) com o valor de `layers.sql` do `sdd/config.yaml`. Caminho terminado em `/` é ignorado. Em `## Migrations aplicadas`, as colunas são achadas pelo cabeçalho (prefixos `arquivo|file`, `projeto|project`, `aplicada|applied`, `prova|proof`), com posição 0–3 como reserva; o caminho é o 1º token entre crases da coluna Arquivo, comparado por igualdade de texto.

**Rationale:** Cobre os títulos reais sem ler o relatório inteiro (onde `.sql` aparece em notas); o 1º token evita que uma célula de verificação vire migration.

**Alternatives Rejected:**
1. Só `## Files Created` exato — perderia a maioria dos relatórios reais.
2. Qualquer `.sql` no relatório — falso positivo nas seções de notas e no Advisor Ledger.

**Consequences:**
- Caminho abreviado (`migrations/…_x.sql`) em uma tabela e completo na outra reprova; a mensagem diz o caminho esperado (A-002 do DEFINE).
- Relatório sem seção de arquivos não dispara a regra.

### Decision 2: Prova da migration reaproveita a checagem de log dos ATs

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-10-29 |
| **Source** | DEFINE (AT-003, AT-005, AT-008) |

**Context:** O contrato de log (`evidence/<F>/`, `.log|.txt`, não vazio, 1ª linha `$ `) já existe dentro de `evidence_ok()`; os 14 testes não podem mudar de resultado.

**Choice:** Extrair de `evidence_ok()` a função `problema_do_log(p, root, report_dir, feature) -> str | None` (None = log válido) sem mudar mensagens nem ordem; `evidence_ok()` passa a chamá-la. A prova de migration: célula vazia ou `—` ⇒ falha; `\bexit\s*(code\s*)?0\b` ⇒ "exit 0 não prova migration"; `FAKE_RE` ⇒ declaração; `RECIBO_RE` ⇒ ok em qualquer `kind`; senão, algum caminho de `PATH_RE` com `problema_do_log()` None ⇒ ok. `AVALIACAO_*.md` não vale como prova de migration.

**Rationale:** Um único dono do formato de log (`EVIDENCIA.md`); a extração é mecânica e coberta pelos 14 testes.

**Alternatives Rejected:**
1. Copiar o bloco de checagem — duas versões do contrato divergindo.
2. Aceitar `AVALIACAO_*` — o avaliador prova ATs executando, não lê o banco.

**Consequences:**
- O recibo da migration vale fora de `manual-ux`; o dos ATs continua restrito (contrato `test_recibo_fora_de_manual_ux`).

### Decision 3: Mini-parser de YAML por indentação no script

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-10-29 |
| **Source** | DEFINE (constraint: só stdlib) + Brainstorm (YAGNI: sem parser completo) |

**Context:** Python 3.9 sem PyYAML. O script precisa de `on`, `jobs.<id>` com `needs`, `if`, `continue-on-error`, `uses` e `steps`, e por passo `name`, `run`, `uses`, `if`, `continue-on-error`.

**Choice:** Parser de ~70 linhas: remove comentários fora de aspas, entende `chave: valor`, `chave:` com bloco filho, itens `- ` (escalar ou mapa iniciado na mesma linha), escalares de bloco `|`/`>` (com `-`/`+`), listas `[a, b]` e aspas simples/duplas. Âncoras, merge keys e multi-documento não são suportados: o workflow que usa isso cai em `NAO_SEI` com "não consegui ler <arquivo>".

**Rationale:** Workflows do Actions usam um subconjunto pequeno; o que não for entendido nunca vira `SIM`.

**Alternatives Rejected:**
1. Grep por linha sem árvore — não distingue passo de teste de job nem `needs:` de outro job.
2. Exigir PyYAML — quebra o piso do macOS de fábrica.

**Consequences:**
- O parser é testado indiretamente por todas as fixtures; um caso de "não consegui ler" entra nos testes.

### Decision 4: Regras do script (publicar, testar, segurar)

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-10-29 |
| **Source** | DEFINE (AT-009 a AT-014) + amostras do Wordpress |

**Context:** O `deploy-hostinger.yml` tem `echo "... deploy bloqueado"` num passo de lint e "deploy" em nomes de passos que não publicam; o `ci-deno-test.yml` roda a suíte com `set +e … exit 0`.

**Choice:**
- **Workflow considerado:** o que tem algum gatilho além de `pull_request`/`pull_request_target`. `workflow_run` com job que publica ⇒ `NAO_SEI`.
- **Passo que publica:** `uses:` cujo nome contém `deploy`, `publish`, `gh-release`, `gh-pages`, `release-action`; ou alguma linha de `run:` que, sem contar linhas iniciadas por `echo`, `printf` ou `#`, casa um comando de publicação (`rsync`, `scp`, `gh release create|upload`, `npm|yarn|pnpm publish`, `twine upload`, `cargo publish`, `docker push`, `git push`, `vercel`, `netlify deploy`, `firebase deploy`, `wrangler deploy|publish`, `fly(ctl)? deploy`, `supabase functions deploy`, `supabase db push`, `kubectl apply`, `helm upgrade`, `aws s3 sync`, `make deploy`, `npm run deploy`, `./deploy…`). Job com `uses:` de workflow reutilizável ⇒ `NAO_SEI`.
- **Passo de teste:** linha de `run:` com `pytest`, `unittest`, `jest`, `vitest`, `mocha`, `phpunit`, `rspec`, `tox`, `ctest`, `<npm|yarn|pnpm|bun> (run )?test`, `<go|cargo|deno|dotnet|mvn|gradle|mix> test`, `make test`. Lint nunca é teste.
- **Teste bloqueante:** passo sem `continue-on-error` diferente de `false`, cuja linha de teste não tem `|| true`, `|| :`, `|| exit 0` nem `|| echo`, e cujo `run:` não tem `set +e` com última linha `exit 0`; e o job do teste sem `continue-on-error` diferente de `false`.
- **Job que publica está seguro** se: (a) um passo de teste bloqueante vem antes do 1º passo que publica no mesmo job e esse passo que publica não tem `if:` com `always()`, `failure()` ou `!cancelled()`; ou (b) o job tem `needs:` (transitivo) num job com teste bloqueante e o próprio job não tem `if:` com `always()`, `failure()` ou `!cancelled()`.
- **Agregação:** algum job inseguro ⇒ `NAO` (lista todos); senão algum `NAO_SEI` ⇒ `NAO_SEI`; senão ≥1 job que publica ⇒ `SIM`; senão, se algum nome de workflow/job/passo contém `deploy`, `publish` ou `release` sem passo reconhecido ⇒ `NAO_SEI`, e nada disso ⇒ `NAO_SE_APLICA`. Job inseguro sem nenhum passo de teste reconhecido, mas com nome de passo contendo `test` ⇒ `NAO_SEI` (o teste pode estar num script próprio), nunca `NAO`.

**Revisão v1.1 (revisão pós-build de contexto fresco, 11 SIM falsos reproduzidos):**
- **Teste** só conta em posição de comando (início, ou depois de `&&`, `;`, `|`, atribuição, `$(`, `env`, `sudo`, `npx`, `uv/poetry run`, `python -m`); linha de instalação (`pip install`, `npm install`, `yarn add`, `apt-get install`…) nunca é teste; `make test-deps` não é `make test`.
- `if:` com `always()`/`failure()`/`!cancelled()` em **qualquer** passo que publica, ou num job do meio do `needs:` (sem teste próprio que segure), ⇒ `NAO`.
- Teste por pipe (`pytest | tee`) sem `shell: bash` nem `pipefail` ⇒ `NAO` (o shell padrão do Actions é `bash -e`, sem pipefail).
- Teste com `if:` que não seja só `always()`/`success()`, ou com `set +e` sem `exit 0` no fim ⇒ `NAO_SEI`.
- Job cujo id ou nome fala em deploy/publish/release (fora `…-gate`, `…-check`, `…-lint`) sem passo reconhecido ⇒ `NAO_SEI`, que impede `SIM` por cima dele; o nome do workflow só pesa se nenhum job dele publicar de forma reconhecida.
- `uses:` com `push-action` publica (`docker/build-push-action`); workflow só com `workflow_call` não é avaliado sozinho (quem chama dá `NAO_SEI`); arquivo que não abre (`OSError`) ⇒ `NAO_SEI` com `RESULTADO:`.

**Rationale:** Ignorar `echo`/`printf` evita o falso "publica" do lint; `NAO_SEI` absorve o que a heurística não alcança (A-004). O SIM falso é o pior erro possível do script, então na dúvida ele cai em `NAO_SEI`.

**Alternatives Rejected:**
1. A palavra "deploy" em qualquer lugar ⇒ publica — o lint do Wordpress viraria publicação.
2. Passo com nome "test" conta como teste — `SIM` sem prova.

**Consequences:**
- Projeto com teste e deploy em scripts próprios (`./ci.sh`) recebe `NAO_SEI` e a skill diz "não consegui afirmar".

### Decision 5: Fixtures inline nos testes, `release.yml` real como caso SIM

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-10-29 |
| **Source** | Padrão de `tests/` (todos montam a sandbox com `escreve()`) + G3 do publish-gate |

**Context:** O plano pede "fixture de workflow com `continue-on-error`"; arquivos soltos em `tests/fixtures/` entrariam no `MANIFEST.txt` e no G2 um a um.

**Choice:** Cada fixture é uma constante de texto em `tests/test_deploy_espera_testes.py`, escrita em `<sandbox>/.github/workflows/` por `escreve()`. As derivadas do Wordpress (`DEPLOY_HOSTINGER`, `DENO_INFORMATIVO`) mantêm a estrutura (passos, `continue-on-error` do standby, lint com `echo … deploy bloqueado`, `set +e … exit 0`) com hosts `deploy.invalid`, sem usuário, caminho de servidor ou domínio. O caso SIM por `needs:` copia o `.github/workflows/release.yml` real do sdd-open (`self.copia`).

**Rationale:** Mesmo padrão das suítes existentes; o caso SIM real não envelhece em silêncio.

**Alternatives Rejected:**
1. Pasta `tests/fixtures/workflows/` — mais arquivos no manifest sem ganho de prova.

**Consequences:**
- Se o `release.yml` do open perder o `needs: testes`, o teste SIM fica vermelho: é desejado.

### Decision 6: `doctor` compara versão de skill e conteúdo de `sdd/bin/`

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-10-29 |
| **Source** | Brainstorm (decisão 13) + DEFINE (AT-015, AT-016) |

**Context:** `init` nunca sobrescreve `.agents/skills/<skill>` nem arquivo de `sdd/`.

**Choice:** No fim de `doctor()`, antes do bloco do `checar.sh --segredo`: para cada skill de `skills_da_fonte` do pacote com `SKILL.md` no projeto, ler `version:` do frontmatter dos dois (`sed` no bloco entre os dois `---`); projeto sem versão conta como `0.0.0`; versão do projeto menor (comparação numérica por `awk`, campo a campo) ⇒ `warn "<skill> <vp> no projeto, <vq> no pacote — para receber: apague .agents/skills/<skill> e rode init (edições suas nela se perdem)"`. Para cada arquivo de `$PKG/sdd/bin/` que existe em `$ROOT/sdd/bin/`: `cmp -s` diferente ⇒ `warn "sdd/bin/<f> difere do pacote — se você não editou, apague e rode init"`. Nenhum aviso ⇒ `ok "skills e sdd/bin/ em dia com o pacote"`. Arquivo ausente continua com o aviso já existente "sdd/ incompleto".

**Rationale:** `cmp` existe no macOS e no Ubuntu; versão é o contrato que o `check-versions.py` já garante.

**Alternatives Rejected:**
1. SHA-256 — `shasum`/`sha256sum` mudam de nome entre sistemas; `cmp` basta para "diferente".
2. Versão de projeto maior também avisar — o usuário pode ter evoluído a skill; não é atraso.

**Consequences:**
- Quem edita `report-lint.py` de propósito vê um ⚠️ permanente; a mensagem diz "se você não editou".

### Decision 7: Bloco do "go" substitui o item 7 da FASE 1

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-10-29 |
| **Source** | Brainstorm (checkpoint 1) + DEFINE (AT-017) |

**Context:** A `sdd-release` 2.1.0 pede o OK numa lista solta; o starter tem o bloco de campos afirmados.

**Choice:** O item 7 vira "PARAR e mostrar (o 1 OK) — um bloco só" com, nesta ordem: **O que sobe** · **O que muda em produção** · **O push publica sozinho?** · **O deploy espera os testes?** (saída do script traduzida; `NAO_SEI` ⇒ "não consegui afirmar: <motivo>"; `NAO_SE_APLICA` ⇒ "não se aplica: o push não publica") · **Banco:** (de `## Migrations aplicadas`; sem migration ⇒ "sem migração nesta frente") · **Verificações:** (Verify Gate exit, report-lint, lint, landmines, drift — pulado dito como pulado) · **Veredito:** 0d com FAIL-candidatos e WAIVED · **Ledger:** `feature_id` · última linha **Posso finalizar (push + deploy + verificar)?**. Regras do starter: verificação ausente dita como ausente; uma pergunta só; ambiguidade dita dentro do bloco. O item 10 da FASE 2 cita o script para o "verde não prova teste".

**Rationale:** Mantém o mecanismo do open (veredito, WAIVED, ledger) dentro da única parada.

**Alternatives Rejected:**
1. Bloco ao lado do item 7 — duas listas no mesmo momento.

**Consequences:**
- `sdd-release` 2.2.0; o texto continua abaixo de 500 linhas.

---

## File Manifest

| # | File | Action | Purpose | Agent / Owner | Dependencies |
|---:|---|---|---|---|---|
| 1 | `sdd/bin/report-lint.py` | Modify | `problema_do_log()` extraída; `ler_layers_sql()`, `migrations_listadas()`, `linhas_migrations()`, `check_migrations()`; docstring e mensagem `→` citam migrations | (general) | None |
| 2 | `sdd/templates/BUILD_REPORT_TEMPLATE.md` | Modify | Seção condicional `## Migrations aplicadas` depois de `## Files Created` | (general) | None |
| 3 | `sdd/templates/fragments/EVIDENCIA.md` | Modify | Parágrafo "Migration aplicada": log `MIG-nnn.log` ou recibo; exit 0 não prova | (general) | None |
| 4 | `sdd/playbook.md` | Modify | `LM-004` no `## Sempre` | (general) | None |
| 5 | `.agents/skills/sdd-build/references/aplicar-migration.md` | Create | Porte adaptado do starter | (general) | 2, 3 |
| 6 | `.agents/skills/sdd-build/SKILL.md` | Modify | 2.1.0; passo 4b "Migration (só se o manifest tem)" antes da validação; seção obrigatória `## Migrations aplicadas` no item 6 | (general) | 5 |
| 7 | `.agents/skills/sdd-release/scripts/deploy-espera-testes.py` | Create | Script SIM/NAO/NAO_SEI/NAO_SE_APLICA, executável, shebang `python3` | (general) | None |
| 8 | `.agents/skills/sdd-release/SKILL.md` | Modify | 2.2.0; item 7 = bloco do "go"; item 10 cita o script; 0a.5 cita a regra de migration | (general) | 7, 1 |
| 9 | `bin/sdd-open.sh` | Modify | `versao_skill()`, `versao_menor()` e o bloco de atraso no `doctor()` | (general) | None |
| 10 | `tests/test_report_lint.py` | Modify | Classe `Migrations` (AT-001 a AT-007) | (general) | 1 |
| 11 | `tests/test_deploy_espera_testes.py` | Create | AT-009 a AT-014 com fixtures inline e `release.yml` real | (general) | 7 |
| 12 | `tests/test_sdd_open.py` | Modify | AT-015, AT-016 no `Projeto` | (general) | 9 |
| 13 | `tests/test_contrato_build_release.py` | Create | AT-017 a AT-019 (texto das skills, template, playbook) | (general) | 2, 4, 5, 6, 8 |
| 14 | `MANIFEST.txt` | Modify | 4 linhas novas (5, 7, 11, 13) em ordem `LC_ALL=C` | (general) | 5, 7, 11, 13 |

**Total Files:** 14

**Agent Discovery:** Not available — `(general)` em todos.

### Agent Assignment Rationale

| Agent / Owner | Files Assigned | Why |
|---|---|---|
| (general) | 1–14 | Sem catálogo de agentes no projeto; o build roda in-context, como F1 e F2 |

---

## Code Patterns

### Pattern 1: extração da checagem de log (report-lint.py)

```python
def problema_do_log(p, root, report_dir, feature):
    """None = log válido da feature; senão, o motivo (mesmas mensagens de antes)."""
    norm = p.replace("\\", "/")
    if ("evidence/" + feature + "/") not in norm or not norm.endswith((".log", ".txt")):
        return "`%s` fora de evidence/%s/*.log — só evidência da própria feature vale" % (p, feature)
    cands = (os.path.join(report_dir, p), os.path.join(root, p), os.path.join(root, REPORTS_DIR, p))
    found = next((c for c in cands if os.path.isfile(c)), None)
    if not found:
        return "`%s` não existe" % p
    if os.path.getsize(found) == 0:
        return "`%s` está vazio" % p
    if not open(found, encoding="utf-8", errors="replace").readline().startswith("$ "):
        return "`%s` sem a 1ª linha `$ <comando>` (não é output capturado)" % p
    return None
```

As strings ficam idênticas às atuais (no código real continuam como f-strings); só o corpo muda de lugar.

### Pattern 2: veredito por migration

```python
EXIT0_RE = re.compile(r"\bexit\s*(?:code\s*)?0\b", re.IGNORECASE)
DATA_RE = re.compile(r"\b\d\d\d\d-\d\d-\d\d\b")

def prova_migration(cell, root, report_dir, feature):
    if not cell or cell in ("—", "-"):
        return "prova por leitura vazia"
    if EXIT0_RE.search(cell):
        return "exit 0 não prova migration — leia de volta (migration list, select)"
    if FAKE_RE.search(cell):
        return "declaração não é prova"
    if RECIBO_RE.search(cell):
        return None
    probs = [problema_do_log(p, root, report_dir, feature) for p in PATH_RE.findall(cell)]
    if any(x is None for x in probs):
        return None
    return "; ".join(x for x in probs if x) or "sem log de evidence/<F>/ nem recibo"
```

### Pattern 3: saída do script

```python
EXIT = dict(SIM=0, NAO=1, NAO_SEI=2, NAO_SE_APLICA=3)

def frase(res, detalhe):
    if res == "SIM":
        return "sim — " + detalhe
    if res == "NAO":
        return "não — " + detalhe + ": um teste vermelho não impede a publicação"
    if res == "NAO_SEI":
        return "não consegui afirmar — " + detalhe
    return "não se aplica: nenhum workflow publica"

print("RESULTADO: " + res)
print("→ O deploy espera os testes? " + frase(res, detalhe))
sys.exit(EXIT[res])
```

### Pattern 4: atraso no doctor (bash 3.2)

```bash
# versão do frontmatter: 1ª linha "version:" entre os dois --- do topo
versao_skill() (
  sed -n '2,/^---$/ s/^ *version: *"*\([0-9][0-9.]*\)"*.*$/\1/p' "$1" | head -1
)
# versao_menor A B: exit 0 se A < B, comparando os 3 campos numericamente com awk split(".");
# A vazia conta como 0.0.0
```

---

## Data Flow

```text
1. sdd-build lê o DESIGN; manifest tem *.sql | migrations/ | ação "migration"?
   │ não → passo 4b pulado, sem mencionar banco
   ▼ sim
2. references/aplicar-migration.md: descobrir ferramenta, projeto (nome E ref), tipo de banco
   │ divergência de ref → PARA e mostra os dois; nada aplicado
   ▼
3. já aplicada? → sim: registrar "já aplicada em <data>" e ir à prova
   ▼ não
4. prévia (dry-run) → migration fora do manifest → PARA; bloco único de confirmação → "sim"?
   │ resposta ≠ sim → não aplica
   ▼
5. aplicar → provar por leitura (migration list + select) → evidence/<F>/MIG-nnn.log (1ª linha `$ `)
   ▼
6. BUILD_REPORT: ## Files Created … lista o .sql; ## Migrations aplicadas tem a linha
   ▼
7. report-lint.py: ATs (como antes) + check_migrations → 🛑 por migration sem linha/prova → exit 1
   ▼ exit 0
8. sdd-release FASE 0a.5 roda o lint de novo; FASE 1 monta o bloco:
   deploy-espera-testes.py . → RESULTADO + frase; "Banco:" ← ## Migrations aplicadas
   ▼
9. 1 OK humano → FASE 2 (push, deploy, verificar pelo SHA publicado)

Paralelo: sdd-open.sh doctor → para cada skill do pacote: versão do projeto < pacote? ⚠️ ;
          para cada sdd/bin/* do pacote: cmp diferente? ⚠️ ; nenhum → ✅ ; exit 0 + RESULTADO
```

---

## Integration Points

| External System | Integration Type | Authentication | Direction | Failure / Retry |
|---|---|---|---|---|
| Supabase CLI/MCP (só texto da referência, executado pelo agente do usuário) | CLI / MCP | senha do banco do `supabase link` ou sessão do MCP; nunca no repositório | out | Falha ou `declined` ⇒ não reescrever a migration; entregar ao SQL Editor; sem retry automático |
| GitHub Actions (só leitura de arquivos `.github/workflows/`) | Arquivo local | N/A | in | Arquivo ilegível ⇒ `NAO_SEI` com o nome; sem rede |

---

## Testing Strategy

| Test Type | Scope / Requirement | Files | Tools | Pass Signal |
|---|---|---|---|---|
| Unit (subprocess) | AT-001 a AT-007: regra de migration (válida por log, por recibo em gate `test`, "já aplicada em"; sem linha; sem seção; célula vazia; declarativa; "exit 0"; log inexistente/sem `$ `; projeto sem `·`; sem data; `layers.sql` preenchido e vazio; ação Delete; relatório sem migration) | `tests/test_report_lint.py` | unittest + `apoio.Sandbox` | exit 0/1 e `🛑` com o caminho |
| Non-regression | AT-008: os 14 contratos atuais sem edição | `tests/test_report_lint.py` | unittest | 14 verdes |
| Unit (subprocess) | AT-009 a AT-014: `release.yml` real ⇒ SIM; teste no mesmo job + `continue-on-error` no standby + lint ⇒ SIM; `DEPLOY_HOSTINGER` ⇒ NAO com arquivo e job; teste com `continue-on-error`, `\|\| true`, `set +e…exit 0` ⇒ NAO com o passo; `if: always()` ⇒ NAO; `workflow_run` ⇒ NAO_SEI; reutilizável ⇒ NAO_SEI; YAML ilegível ⇒ NAO_SEI; sem `.github/workflows/` e só `DENO_INFORMATIVO` ⇒ NAO_SE_APLICA; argumento inválido ⇒ 64; PR-only ignorado | `tests/test_deploy_espera_testes.py` | unittest + `apoio.Sandbox` | `RESULTADO:` e exit esperados |
| Integration | AT-015, AT-016: `doctor` num projeto com `init` (skill rebaixada para `1.0.0`; `sdd/bin/report-lint.py` com linha a mais; projeto limpo) | `tests/test_sdd_open.py` | unittest | ⚠️/✅ e exit 0 com `RESULTADO:` |
| Contract | AT-017 a AT-019: texto da `sdd-release`, da `sdd-build`, da referência, do template e do playbook; `playbook-lint.sh sdd/playbook.md` 0 | `tests/test_contrato_build_release.py` | unittest | asserções verdes |
| Gate | AT-020 a AT-022: publish-gate em modo ci, `check-versions --base v2.2.2 --base-obrigatoria`, suíte inteira no piso | Verify Gate do DEFINE | `verify-gate.sh --strict` | exit 0 |
| Sabotage | AT-023: (1) `report-lint.py` sem a checagem de linha ausente; (2) script sem o `continue-on-error` do passo; (3) `doctor` sem o `cmp` | `sdd/reports/evidence/F3_BUILD_RELEASE/sabotagem.sh` | `sed` por padrão + `git checkout` | teste nomeado vermelho, depois verde |

---

## Error Handling

| Error Type | Detection | Handling Strategy | Retry? | Observability |
|---|---|---|---|---|
| BUILD_REPORT ilegível / nome fora do padrão | `open()` / `REPORT_RE` | exit 64 (inalterado) | No | `🛑` no stderr |
| `sdd/config.yaml` ausente ou `layers.sql` vazio | arquivo/valor | só o glob fixo | N/A | — |
| `## Migrations aplicadas` sem cabeçalho reconhecível | prefixos ausentes | colunas por posição 0–3 | N/A | violação nomeia a migration se faltar campo |
| Argumento do script não é diretório / argumentos a mais | `os.path.isdir` | exit 64 com uso | No | stderr |
| Workflow ilegível pelo mini-parser | exceção no parser | `NAO_SEI` "não consegui ler <arquivo>" | No | linha `❓` |
| Pacote sem `sdd/bin/` ou skill sem `SKILL.md` no projeto | teste de arquivo | pula o item (o aviso "sdd/ incompleto" já cobre falta) | N/A | — |
| `awk`/`cmp` ausentes | — | ambos POSIX e presentes em macOS e Ubuntu; não tratado | N/A | — |

---

## Configuration

| Config Key | Type | Source / Default | Sensitive? | Description |
|---|---|---|---|---|
| `layers.sql` | glob (string) | `sdd/config.yaml`; vazio por padrão | No | Caminhos extras tratados como migration pelo `report-lint` |
| `SDD_TEST_BASH` | caminho | ambiente dos testes; `bash` do PATH | No | Roda a suíte no bash 3.2 do macOS |

---

## Security Considerations

- Fixtures derivadas do Wordpress sem host, usuário, porta, caminho de servidor ou domínio reais (`deploy.invalid`, segredos do Actions só pelo nome); G2 do publish-gate confere.
- A referência de migration nunca pede senha no chat nem a grava: `SUPABASE_DB_PASSWORD` só como variável de ambiente; o exemplo de função com CNPJ vira chamada sem número literal.
- O script só lê arquivos sob `<raiz>/.github/workflows/`; não executa nada do workflow nem acessa rede.
- O `doctor` não sobrescreve nada: só compara e sugere o comando.
- `report-lint.py` só abre arquivos citados dentro de `evidence/<F>/` (contrato existente).

---

## Observability

| Aspect | Implementation | Signal / Why |
|---|---|---|
| Logging | Linhas `🛑`/`⚠️`/`✅`/`❓` por item; `RESULTADO:` + `→` no fim (convenção do open) | O agente traduz a linha RESULTADO sem colar saída crua |
| Metrics | Contagem de testes no `unittest` (`Ran N tests`) | Success Criterion: mais de 242 |
| Tracing | N/A | — |

---

## Requirements Traceability

| Requirement / AT | Design Element | Test / Gate |
|---|---|---|
| MUST lint de migration / AT-001–AT-007 | Decisions 1, 2; manifest 1 | `tests/test_report_lint.py` (`Migrations`) |
| MUST 14 contratos / AT-008 | Decision 2 (extração sem mudar mensagens) | `tests/test_report_lint.py` (`ReportLint`) |
| MUST script / AT-009–AT-014 | Decisions 3, 4, 5; manifest 7 | `tests/test_deploy_espera_testes.py` |
| MUST bloco do "go" / AT-017 | Decision 7; manifest 8 | `tests/test_contrato_build_release.py` |
| MUST referência + `sdd-build` / AT-018 | manifest 5, 6 | `tests/test_contrato_build_release.py` |
| MUST template + `LM-004` / AT-019 | manifest 2, 3, 4 | `tests/test_contrato_build_release.py` |
| MUST doctor / AT-015, AT-016 | Decision 6; manifest 9 | `tests/test_sdd_open.py` |
| AT-020 G2 limpo | Security; manifest 5, 11 | Verify Gate (publish-gate ci) |
| AT-021 versões | manifest 6, 8 | Verify Gate (`check-versions` no publish-gate) e comando do Success Criterion |
| AT-022 não regressão | manifest 14; nada em `verify-gate.sh`/`fixtures/` | Verify Gate (suíte inteira) |
| AT-023 sabotagem | Testing Strategy (Sabotage) | `sdd/reports/evidence/F3_BUILD_RELEASE/sabotagem.sh` |

---

## Risks and Mitigations

| Risk | Impact | Mitigation | Residual Risk |
|---|---|---|---|
| Heurística do script dá `SIM` falso | OK dado com deploy que não espera teste | `SIM` exige teste reconhecido e bloqueante antes de **todo** passo que publica; o resto vira `NAO_SEI` | Comando de teste disfarçado (`./ci.sh` que não testa) com nome de teste reconhecido: improvável |
| Extração de `problema_do_log` muda mensagem | Contrato dos ATs quebra | Copiar as strings literalmente; 14 testes inalterados | Nenhum |
| Relatório real com caminho abreviado reprova | Atrito no 1º uso | Mensagem diz o caminho esperado; template e referência pedem caminho completo | Aceito (A-002) |
| `doctor` avisa sempre para `sdd/bin/` editado de propósito | Ruído | Texto "se você não editou" | Aceito |
| `if:` com expressão composta não reconhecida | Publicação com `always()` escondido em expressão maior | Busca por substring `always()`, `failure()`, `!cancelled()` em qualquer lugar do `if:` | Baixo |

---

## Advisor Ledger

None — no formal external design review.

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | 2026-10-29 | SDD Design by RDD | Initial version |
| 1.1 | 2026-10-29 | SDD Build by RDD | Revisão pós-build de contexto fresco: Decisão 4 endurecida contra SIM falso; Decisão 1 aceita títulos numerados/com prefixo; projeto `— · —` reprova; `doctor` lê `version` entre aspas simples |

---

## Next Step

Execute o **SDD Build by RDD**.
