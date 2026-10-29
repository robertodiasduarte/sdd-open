# BRAINSTORM: F3 Build e Release

> Exploratory session to clarify intent and approach before requirements capture

## Metadata

| Attribute | Value |
|---|---|
| Feature | F3_BUILD_RELEASE |
| Date | 2026-10-29 |
| Author | brainstorm-agent |
| Status | Handoff Ready |

## Initial Idea

**Raw Input:** "F3 Build e Release — aplicar-migration e seção Migrations aplicadas com regra no report-lint; bloco da Fase 2 no momento do go, com 'o deploy espera os testes?'. Gate: report-lint reprova migration sem prova; fixture de workflow com continue-on-error." (linha F3 de `sdd/features/AVALIACAO_STARTER_PARA_OPEN.md`, retomada por `sdd/handoffs/SESSION_PROMPT_INCORPORAR_STARTER.md`)

**Context Gathered:**
- Fato (lido): `skills/sdd-build/references/aplicar-migration.md` do sdd-starter (`17c69c4`, 195 linhas) — 4 regras (descobrir sem perguntar; destino nome E ref antes do único OK; exit 0 não é prova; um passo por vez), descoberta de ferramenta/projeto/tipo de banco, parada na divergência, prévia por `--dry-run`, bloco de confirmação único, prova por leitura em dois níveis, registro em `## Migrations aplicadas`. A seção 1 grava em `sdd/ambiente.md` (o open não tem esse arquivo — decisão 4) e a linha 175 tem um CNPJ literal que o G2 do publish-gate reprova.
- Fato (lido): Fase 2 da `skills/sdd-release/SKILL.md` do starter (linhas 203–254) — bloco único com O que sobe · O que muda em produção · O push publica sozinho? · O deploy espera os testes? · Banco · Verificações; "verificação ausente dita como ausente"; nunca para duas vezes.
- Fato (lido): `sdd/bin/report-lint.py` do open (187 linhas) só lê a tabela de ATs e o veredito do avaliador; não lê arquivos criados nem `sdd/config.yaml`. `tests/test_report_lint.py` tem 14 contratos.
- Fato (lido): `sdd/templates/BUILD_REPORT_TEMPLATE.md` (244 linhas) tem `## Files Created` (`| File | Lines | Agent | Verified | Notes |`) e nenhuma seção de migration.
- Fato (lido): `sdd/playbook.md` vai até `LM-003` em `## Sempre`.
- Fato (lido): `.agents/skills/sdd-release/SKILL.md` 2.1.0 (200 linhas) — o "1 OK" é o item 7 da FASE 1, uma lista solta (diff --stat, classificação, Verify Gate, veredito 0d, `feature_id`); o item 10 da FASE 2 já diz "verde não prova teste" para `continue-on-error`/`|| true`/`exit 0`.
- Fato (lido): `aplicar()` e `sdd_faltantes()` em `bin/sdd-open.sh` — o `init` só completa arquivo que falta em `sdd/` (templates, bin, playbook, config) **e** só copia `.agents/skills/<skill>` que não existe. Projeto já instalado não recebe nenhuma mudança da F3; hoje o único caminho é apagar o arquivo/pasta e rodar `init` de novo.
- Fato (lido): `release.yml` do open tem jobs `testes` e `release` com `needs: testes` e `unittest` no `testes`; `publish-gate.yml` não publica.
- Inferência: a F4 mexerá nas 13 skills, então o aviso de versão do `doctor` serve também a ela.

**Technical Context Observed (for Define):**

| Aspect | Observation | Implication |
|---|---|---|
| Likely Location | `.agents/skills/sdd-build/` (SKILL.md + `references/aplicar-migration.md`), `.agents/skills/sdd-release/` (SKILL.md + `scripts/deploy-espera-testes.py`), `sdd/bin/report-lint.py`, `sdd/templates/BUILD_REPORT_TEMPLATE.md`, `sdd/playbook.md`, `bin/sdd-open.sh` (`doctor`), `tests/`, `MANIFEST.txt` | Primeira frente desta feature que mexe em `sdd/`; os contratos de `verify-gate.sh`, `sdd/fixtures/` e os 242 testes ficam como estão |
| Relevant KB Domains | Supabase CLI/MCP (migration list, db push --dry-run, apply_migration), GitHub Actions (`needs:`, `continue-on-error`, `if: always()`, `workflow_run`) | O script lê YAML linha a linha, só stdlib; o lint não acessa banco |
| IaC Patterns | Workflows GitHub Actions; release automática no push de `main` (F1) | Skill alterada sobe versão (`check-versions.py --base v2.2.2 --base-obrigatoria`); PR + OK citando "sdd-open" antes do push em `main` |

## Discovery Questions & Answers

| # | Question | Answer | Impact |
|---|---|---|---|
| 1 | Como o `report-lint` reconhece "migration" nos arquivos criados: glob fixo, slot `layers.sql` ou os dois? | Glob fixo + `layers.sql` (recomendado) | Casa `*.sql` ou `migrations/` no caminho **e**, se `layers.sql` estiver preenchido, o que casar com ele; config ausente ou slot vazio ⇒ só o glob. Exige mini-parser de `layers:` no lint |
| 2 | "O deploy espera os testes?" é texto da skill ou script com fixture? | Script com respostas fechadas (recomendado), em `.agents/skills/sdd-release/scripts/`, fixtures em `tests/` | Script só-stdlib, heurístico; a skill cita a saída e só julga no "não sei". Refinado no checkpoint 2 para 4 saídas (acrescenta `NAO_SE_APLICA`) |
| 3 | Como tratar que `sdd/` e `.agents/skills/` só chegam a instalação nova? | `doctor` avisa o que ficou velho (recomendado) | `doctor` compara `metadata.version` das skills e o hash de `sdd/bin/*` com o pacote; ⚠️ com "apague e rode init". Sem verbo novo, sem sobrescrever. Templates e playbook ficam fora (o usuário edita) |
| 4 | O que o `report-lint` aceita como "prova por leitura" na linha de `## Migrations aplicadas`? | Log abrível ou recibo (recomendado) | Mesmo contrato dos ATs: `evidence/{F}/*.log` com 1ª linha `$ comando`; no modo manual, `recibo: nome AAAA-MM-DD` (aceito em qualquer `kind` de gate). Declaração, "exit 0" e célula vazia reprovam |

## Sample Data Inventory

| Type | Location | Count | Notes |
|---|---|---:|---|
| Input files | `/Users/robertoduarte/RDD/Wordpress/.github/workflows/deploy-hostinger.yml`, `ci-deno-test.yml` | 2 | `deploy-hostinger` publica (rsync) no push de `main` sem passo de teste e sem `needs:`; tem `continue-on-error: true` em passos que **não** são teste e um "Lint PHP" bloqueante que não é teste. `ci-deno-test` roda a suíte com `set +e … exit 0` fixo e não publica |
| Output examples | `/Users/robertoduarte/RDD/Wordpress/.claude/sdd/reports/BUILD_REPORT_*.md` | 19 com `.sql` | Migration listada em `## Files Created / Modified` (11), `## Files Created/Modified` (7+), `## Files Created` (4), `## Files Changed`, `## Arquivos …`, `## … Manifest …`; formato de coluna variado (`# · Arquivo · Ação · Verificação`) |
| Ground truth | `.github/workflows/release.yml` e `publish-gate.yml` do sdd-open | 2 | `release.yml`: job `release` com `needs: testes` e `unittest` em `testes` ⇒ caso SIM; `publish-gate.yml` não publica |
| Related code | starter `aplicar-migration.md` (195 l.), starter `sdd-release` Fase 2 (l. 203–254), open `report-lint.py`, `bin/sdd-open.sh` | 4 | Fontes do porte e do encaixe |

**How samples will be used:**
- Fixtures do script derivadas dos dois workflows do Wordpress, **anonimizadas** (sem host, usuário, caminho de servidor ou domínio reais; hosts em `.invalid`), cobrindo: publica sem teste; teste informativo com `exit 0`; `continue-on-error` fora de passo de teste que não pode virar falso positivo; lint bloqueante que não conta como teste.
- `release.yml` do open como caso SIM por `needs:`; variantes sintéticas para `continue-on-error` no passo de teste, `|| true`, `if: always()`, `workflow_run`/workflow reutilizável (NAO_SEI) e ausência de `.github/workflows/` (NAO_SE_APLICA).
- Os títulos de seção reais definem onde o lint procura migration (`## Files…`, `## Arquivos…`, títulos com `Manifest`).

## Approaches Explored

### Approach A: Tudo numa release — Recommended

**Description:** Um PR e a `v2.2.3` com todas as peças: `aplicar-migration.md` adaptada, seção no template, regra no `report-lint`, `LM-004`, bloco do "go" + `deploy-espera-testes.py` na `sdd-release`, aviso de versão no `doctor`.

**Pros:**
- As peças formam uma corrente: o "Banco:" do bloco do "go" lê a seção que o lint garante, que a referência manda preencher.
- Um ciclo de gate, release e handoff.

**Cons:**
- PR maior, com `sdd/`, duas skills, o `doctor` e testes no mesmo diff.

**Why Recommended:** separar entrega uma versão com metade da corrente; o tamanho é controlado por testes e sabotagem por script.

### Approach B: Duas releases

**Description:** F3a (referência, template, lint, `LM-004`) → `v2.2.3`; F3b (bloco do "go", script, `doctor`) → `v2.2.4`.

**Pros:**
- PRs menores e revisão mais focada.

**Cons:**
- Dois ciclos completos; a `v2.2.3` registra a migration sem o bloco que a mostra no momento do OK.

### Approach C: Só mecanismo agora

**Description:** Lint, script, fixtures e `doctor` agora; o texto da `sdd-build` e da `sdd-release` fica para a F4, que reescreve as skills.

**Pros:**
- Evita mexer duas vezes no texto das duas skills.

**Cons:**
- Script que nenhuma skill chama; a `v2.2.3` não muda o comportamento do agente.

## Selected Approach

| Attribute | Value |
|---|---|
| Chosen | Approach A — tudo numa release |
| User Confirmation | 2026-10-29, escolha explícita da opção "A: tudo numa release (Recomendado)"; checkpoints 1 e 2 "confirmo" |
| Reasoning | As peças dependem umas das outras; uma versão só evita estado intermediário incoerente |

## Key Decisions Made

| # | Decision | Rationale | Alternative Rejected |
|---|---|---|---|
| 1 | Migration = caminho que termina em `.sql` ou tem `migrations/`, **ou** casa com `layers.sql` do `sdd/config.yaml` quando preenchido | Funciona sem config e respeita quem preencheu | Só glob (perde padrão próprio); só slot (vazio por padrão ⇒ regra nunca dispara) |
| 2 | O lint procura migration nas seções cujo título começa com `## Files` ou `## Arquivos` ou contém `Manifest`; linha com ação Delete/Removido é ignorada | Títulos reais dos BUILD_REPORTs do Wordpress | Só `## Files Created` exato (perderia a maioria dos relatórios reais) |
| 3 | Cada migration exige linha em `## Migrations aplicadas` com o **mesmo caminho**, projeto `nome · ref`, data `AAAA-MM-DD` (ou "já aplicada em …") e prova | Contrato do starter, verificável sem banco | Exigir só a seção existir |
| 4 | Prova = log abrível de `evidence/{F}/` (1ª linha `$ `) ou `recibo: nome AAAA-MM-DD` (em qualquer `kind` de gate); declaração, "exit 0" e vazio reprovam | Mesmo contrato default-FAIL dos ATs; modo manual não tem log | Texto descritivo (✓ sem leitura); só log (modo manual travado) |
| 5 | Relatório sem migration ⇒ regra muda | Relatórios existentes continuam passando | Exigir a seção sempre |
| 6 | `deploy-espera-testes.py [raiz]` em `.agents/skills/sdd-release/scripts/`: `SIM` 0 · `NAO` 1 · `NAO_SEI` 2 · `NAO_SE_APLICA` 3, linha `RESULTADO:` + motivo citando workflow/job/passo | Prova comportamento com fixtures dos dois lados (LM-001) | Só texto da skill; script em `sdd/bin/` (território do usuário) |
| 7 | SIM só quando **todo** job que publica tem teste bloqueante antes no mesmo job ou `needs:` num job com teste bloqueante; NAO para `continue-on-error`, `\|\| true`, `set +e`/`exit 0` fixo no teste, `if: always()` no job que publica, ou nenhum teste; NAO_SEI para `workflow_run`, workflow reutilizável ou publicação não reconhecida; NAO_SE_APLICA sem workflow que publica | Campo do starter; "não sei" evita afirmar o que o script não entende | Parser de YAML completo |
| 8 | "Teste" = palavras de teste (test, pytest, unittest, jest, vitest, `deno test`, phpunit, `go test`…); lint não é teste. "Publicar" = deploy, publish, `gh release`, `npm publish`, rsync/scp, `vercel`, `supabase … deploy`, `docker push`… | Amostra real: "Lint PHP" bloqueante e `continue-on-error` em passo de standby não podem gerar SIM nem falso NAO | — |
| 9 | Na skill, `NAO_SEI` ⇒ o agente lê os workflows e escreve "não consegui afirmar: <motivo>", nunca "sim" | Verificação ausente dita como ausente | Agente decide sozinho |
| 10 | Bloco único do "go" **substitui** a lista solta do item 7 da FASE 1 da `sdd-release`, mantendo dentro dele o veredito 0d, WAIVED e o `feature_id` do ledger; acrescenta O push publica sozinho? · O deploy espera os testes? · Banco · Verificações | Uma parada só, sem perder o mecanismo do open | Bloco ao lado do item 7 (duas listas no mesmo momento) |
| 11 | "Banco:" vem de `## Migrations aplicadas` do BUILD_REPORT; sem `.sql` ⇒ "sem migração nesta frente" | Decisão 4: sem `sdd/ambiente.md` | Ler `sdd/ambiente.md` como o starter |
| 12 | `aplicar-migration.md` sem o registro em `sdd/ambiente.md`; prova em log de `evidence/{F}/` ou recibo; CNPJ da linha 175 reescrito sem número | Decisão 4 e G2 do publish-gate | Porte literal |
| 13 | `doctor`: ⚠️ por skill com `metadata.version` do projeto abaixo da do pacote e por `sdd/bin/*` com hash diferente, com o remédio "apague e rode init"; ✅ quando tudo em dia; exit continua 0 | Instalação existente não recebe a F3 (nem a F4) sem saber | Só nota na Release; verbo `upgrade` (redesenho da CLI) |
| 14 | `LM-004` no `## Sempre`: "exit 0 não prova migration; prova é ler de volta" | Item do plano; formato do `playbook-lint.sh` | — |
| 15 | `sdd-build` 2.0.0 → 2.1.0 e `sdd-release` 2.1.0 → 2.2.0; `MANIFEST.txt` com os arquivos novos | `check-versions.py` reprova skill alterada sem bump | — |

## Features Removed (YAGNI)

| Feature Suggested | Reason Removed/Deferred | Can Add Later? |
|---|---|---|
| CI além do GitHub Actions (GitLab, CircleCI) | Nenhum projeto atual usa; script responde NAO_SE_APLICA sem `.github/workflows/` | Yes |
| Parser de YAML completo | Só stdlib; leitura linha a linha cobre os casos das amostras; o resto cai em NAO_SEI | Yes |
| Lint ler o SQL ou acusar DDL destrutivo | A linha ⛔ é texto da skill, no bloco de confirmação; o lint confere o registro, não o banco | Yes |
| `doctor` comparar templates, playbook e fixtures | São arquivos que o usuário edita; diferença não significa versão velha | No |
| `doctor` consertar sozinho | Apagaria edição do usuário; o remédio é dito, não executado | No |
| Verbo `upgrade` | Redesenho da CLI, fora de escopo | Yes |
| Passos próprios para Prisma, Flyway, Rails | Fica a frase "mesmo protocolo com os comandos dela"; Supabase é o caminho provado | Yes |
| Registro em `sdd/ambiente.md` | Decisão 4 (descoberta só nos slots do config) | No |

## Incremental Validations

| Section | Presented | User Feedback | Adjusted? |
|---|---|---|---|
| Checkpoint 1 — componentes (8 itens), cortes YAGNI, bloco do "go" substituindo o item 7 | Yes | "confirmo" | No |
| Checkpoint 2 — comportamento do lint, das 4 saídas do script (com `NAO_SE_APLICA` novo), do `doctor` e do "Banco:" | Yes | "confirmo" | Yes — 4ª saída `NAO_SE_APLICA` acrescentada à decisão da pergunta 2 |

## Suggested Requirements for /define

### Problem Statement (Draft)

No sdd-open, uma migration listada no build pode ir para produção sem ter sido aplicada nem lida de volta do banco, e o OK da release é pedido sem dizer se o deploy espera os testes nem qual banco mudou; e quem já instalou o pacote não fica sabendo que skills e scripts do projeto ficaram mais velhos que os do pacote.

### Target Users (Draft)

| User | Pain Point |
|---|---|
| Aluno/usuário que roda `sdd-build` em projeto com banco (Supabase) | Migration gravada e publicada sem ter sido executada; exit 0 confundido com prova; projeto errado sem undo |
| Quem dá o OK na `sdd-release` | Aprova sem saber que o deploy publica mesmo com teste vermelho e sem ver qual banco mudou |
| Quem já tem o sdd-open instalado | Continua com `sdd-build`/`sdd-release`/`report-lint.py` velhos sem aviso |

### Success Criteria (Draft)

- [ ] `report-lint.py` sai 1 para BUILD_REPORT que lista migration (glob fixo ou `layers.sql`) sem linha válida em `## Migrations aplicadas`, e 0 com linha válida (log abrível ou recibo); os 14 contratos atuais continuam verdes.
- [ ] `deploy-espera-testes.py` dá NAO para as fixtures derivadas do Wordpress e para teste com `continue-on-error`, `|| true` e `exit 0` fixo; SIM para o `release.yml` do open; NAO_SEI para `workflow_run`; NAO_SE_APLICA sem workflow que publica.
- [ ] `doctor` mostra ⚠️ para skill com versão abaixo da do pacote e para `sdd/bin/*` com hash diferente, e continua saindo 0.
- [ ] `sdd/playbook.md` tem `LM-004` e `playbook-lint.sh --self-test` sai 0.
- [ ] Verify Gate (`kind: test`, cópia por `git archive HEAD`, `publish-gate.sh` em modo ci + `unittest discover`) sai 0; os 242 testes atuais continuam verdes no piso Python 3.9.6 + bash 3.2.57.
- [ ] Uma sabotagem por script alterado no BUILD_REPORT (quebra → teste nomeado vermelho → `git checkout` → verde).
- [ ] Release `v2.2.3` publicada com `SHA256SUMS.txt` conferido.

### Constraints Identified

- Exits de `verify-gate.sh` (0/2/3/4/5/64) e `sdd/fixtures/` idênticos; 14 contratos de `test_report_lint.py` intactos; `playbook-lint.sh --self-test` 0.
- Nada na árvore casa com `scripts/publish-gate-patterns.txt`: e-mail só em `example.*`, CPF/CNPJ/telefone/`git@host` montados em tempo de execução, hosts em `.invalid`; fixtures do Wordpress anonimizadas.
- Só stdlib, `python3 -B`, bash 3.2, sem zsh/symlink; arquivo novo no `MANIFEST.txt` em `LC_ALL=C`; `git add` por nome.
- Skill alterada sobe versão; `tests/test_skill_lint.py` continua com 16 skills; testes em `tests/` na raiz.
- `sync` idempotente; `GIT_TERMINAL_PROMPT=0` em todo comando remoto; push em `main` só com OK citando "sdd-open".

### Out of Scope (Confirmed)

- Redesenhar a CLI ou o `config.yaml` (inclui verbo `upgrade`).
- Camada de conversa nas skills nativas, `design-lint`/`handoff-lint` (F4); `sdd-kb` (F5); docs, README, `AGENTS.md.tmpl` (F6).
- Curadoria do playbook além do `LM-004`.
- Alterar o sdd-starter, modo `briefs`, teste no Windows.
- Os itens da tabela YAGNI.

## Session Summary

| Metric | Value |
|---|---:|
| Questions Asked | 6 (4 de descoberta, 1 de amostras, 1 de abordagem) |
| Approaches Explored | 3 |
| Features Removed (YAGNI) | 8 |
| Validations Completed | 2 |

## Next Step

Execute o **SDD Define by RDD**.
