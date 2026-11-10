# BRAINSTORM: F15 Slots — smoke visual na release, teste do diff antes do OK e checagem de migration antes do apply

> Sessão exploratória para fixar a intenção e o caminho antes dos requisitos

## Metadata

| Attribute | Value |
|---|---|
| Feature | F15_SLOTS |
| Date | 2026-11-09 |
| Author | brainstorm-agent (worktree `sdd-open-f15-slots`, branch `feat/f15-slots` de `origin/main` = `9d8ac24` = `v2.7.2`) |
| Status | Ready for Define |

## Initial Idea

**Raw Input:** pedido do Roberto (2026-11-09): entregar no Open, numa release própria, as 3 lacunas genéricas do inventário de saída da F15 — **L0** (3 slots de smoke visual no `sdd/config.yaml`, um por momento da `sdd-release`: antes do OK, antes do push, depois do deploy; exit combinado 0 ok · 2 reprovou · 10 nada a medir; slot vazio = pula e diz que pulou), **L3** (a `sdd-release` roda `sdd/bin/test-baseline.sh --touched` antes do OK; o `--touched` passa a contar o teste ao lado da fonte alterada) e **L4** (slot de checagem de migration rodado no build 4b antes do apply, mesmo contrato de exit; vazio = pula e diz). Cada entrega com teste e sabotagem; self-test numa cópia sem `.git`. A fase 3 da F15 (publicar a feature da prova pela `sdd-release` no privado) só roda depois desta release.

**Context Gathered:**
- Fato: `origin/main` = `9d8ac24` = tag `v2.7.2`, conferido em 2026-11-09 (`git describe --tags origin/main`).
- Fato: decisão 5 de `sdd/features/BRAINSTORM_F15_SUBSTITUICAO.md` (branch `docs/incorporar-starter`) fixa os 3 slots e o exit 0/2/10. O §8.2 de `PLANO_F4_F15_CONSOLIDADO.md` registra que `schema.check_cmd` caiu na F12 e `smoke.*` na F13; **esta frente os reabre por decisão do Roberto** (pergunta 1 abaixo).
- Fato: as decisões das 9 lacunas são de 2026-11-08 (`INVENTARIO_SAIDA_F15.md` §5, no privado). L0 já estava decidida; L3 e L4 seguiram a recomendada "recurso genérico no Open"; o inventário admite as 3 numa frente só.
- Fato (`.agents/skills/sdd-release/SKILL.md`, 2.8.1): a release não roda teste nenhum. `project.test_cmd` só aparece na lista de slots (l. 77), e a 0b pergunta ao modelo "teste ao lado do módulo tocado ficou vermelho?" (l. 136), sem comando. No passo 10, "smoke da rota principal" não tem slot.
- Fato (`sdd/bin/test-baseline.sh`, l. 189–197): o `--touched` roda a suíte inteira e só aborta por falha nova cujo id cita um **arquivo de teste tocado**. Mudar `foo.ts` e quebrar `foo.test.ts` (não tocado) vira só "⚠️ nova, fora do diff" (l. 204).
- Fato (`.agents/skills/sdd-build/SKILL.md` 4b → `references/aplicar-migration.md`): descobrir → já aplicada? → prévia → confirmação → aplicar → provar. Nada confere o SQL antes da prévia.
- Fato: nenhum script do Open lê slot de config para executar. O agente lê e roda pelo texto da skill (`{{LANDMINES_CMD}}`). Slot ausente num `config.yaml` antigo equivale a vazio.
- Fato (só leitura no privado): no `/release` antigo, o smoke em 3 tempos (planejar, medir antes, medir depois) nunca aborta antes do OK (10 = nada a medir pula o resto), nunca segura o push, e depois do deploy o exit 2 para e pergunta reverter/corrigir/seguir com motivo. O gate de schema de lá recebe os `.sql` como argumento, sai 0 libera / 2 barra e é fail-closed (linter que não roda = 2). O teste do diff de lá monta o par `x.ts` → `x.test.ts`.

**Technical Context Observed (for Define):**

| Aspect | Observation | Implication |
|---|---|---|
| Likely Location | `sdd/bin/` (script novo + `test-baseline.sh`), `sdd/config.example.yaml`, `.agents/skills/sdd-release/`, `.agents/skills/sdd-build/references/aplicar-migration.md`, `docs/adaptation-guide.md` + PT, `tests/`, `MANIFEST.txt`, `bin/sdd-open.sh` (doctor/sync do script novo) | produto do Open; release `v2.8.0` |
| Relevant KB Domains | nenhum (`sdd/kb/` não existe no Open) | — |
| IaC Patterns | N/A; CI `publish-gate.yml` + `release.yml` (tag `vX.Y.Z` publica a Release) | o ritual de release do Open vale |

## Discovery Questions & Answers

| # | Question | Answer | Impact |
|---|---|---|---|
| 1 | Que nomes os 4 slots ganham? | `smoke.before_ok_cmd`, `smoke.before_push_cmd`, `smoke.after_deploy_cmd`, `schema.check_cmd` (recomendada) | reabre os nomes que caíram na F13 e na F12; o §8.2 do plano registra a reabertura; segue o padrão inglês dos slots existentes |
| 2 | O que o exit 2 do smoke faz em cada momento? | Peso por momento (recomendada): antes do OK = FAIL-candidato no bloco do OK; antes do push = só registra, nunca segura o push; depois do deploy = para e pergunta [D1] reverter / corrigir / seguir com motivo | mantém a regra do OK único; casa com o 6b/7b/10b do privado |
| 3 | Os 3 slots são amarrados ou independentes? | Independentes + pasta comum (recomendada): cada slot roda se preenchido e responde por si; a release passa aos 3 a mesma pasta de trabalho e os mesmos dados | o Open não guarda estado entre passos; o script do projeto combina os momentos pela pasta (o privado devolve 10 no antes/depois quando o derivar não achou tela) |
| 4 | Que rigor têm os gates da L3 e da L4? | L3 aborta, L4 fail-closed (recomendada): falha nova num teste do diff aborta antes do OK (aceitar é o `--aceitar`, decisão humana); exit 3 = WAIVABLE; L4 com exit 2 ou fora do contrato = não aplica a migration; 10 = segue e diz | banco não tem undo; consumidor quebrado já é NON_WAIVABLE no 0d |

## Sample Data Inventory

| Type | Location | Count | Notes |
|---|---|---:|---|
| Input files | N/A | 0 | — |
| Output examples | privado, `/release` antigo, os 3 passos do smoke (só leitura) | 1 | contrato de exit real do smoke: 10 pula, 2 do "depois" pergunta |
| Ground truth | privado, o gate de schema por migration (só leitura) | 1 | `.sql` como argumento; 0 libera / 2 barra; fail-closed |
| Related code | privado, o teste do diff do `/release` antigo; Open, `sdd/bin/test-baseline.sh:189-204` | 2 | par fonte → teste ao lado; o filtro atual do `--touched` |
| Related doc | privado, o inventário de saída da F15 | 1 | L0/L3/L4 e as decisões de 2026-11-08 |

**How samples will be used:**
- Os contratos do privado só fixam o comportamento esperado. Nada deles entra no Open nem nestes documentos: nenhum caminho, nome de script ou projeto da RDD.
- Os testes do Open usam scripts falsos que saem 0/2/10/1/127 e um projeto mínimo neutro (`src/foo.ts` + `src/foo.test.ts`, `pkg/calc.py` + `pkg/test_calc.py`).

## Approaches Explored

### Approach A: Executor de slot único — Recomendada

**Description:** `sdd/bin/slot.sh <chave> [arquivos…]` lê a chave do `sdd/config.yaml`, roda o comando com `SDD_MOMENTO`, `SDD_FEATURE`, `SDD_BASE`, `SDD_COMMIT` e `SDD_SLOT_DIR` e devolve o contrato num lugar só: vazio = PULADO; 0 OK; 2 REPROVOU; 10 NADA A MEDIR; outro = INCONCLUSIVO. A `sdd-release` o chama nos 3 momentos; a `sdd-build` 4b o chama com os `.sql` antes da prévia. O `test-baseline.sh --touched` ganha o teste ao lado da fonte; a release o roda no 0a.

**Pros:**
- o contrato é código executado com fixtures dos dois lados, validável por mutante (LM-001);
- o privado só preenche 4 linhas do config.

**Cons:**
- um script a mais em `sdd/bin/`, que `sync`/`doctor` passam a carregar e conferir.

**Why Recommended:** é a única das três em que a sabotagem derruba uma asserção de comportamento, não de texto.

### Approach B: Só texto nas skills

**Description:** o agente lê o slot e interpreta o exit, como hoje com `release.landmines_cmd`.

**Pros:**
- nenhum código novo.

**Cons:**
- o contrato fica escrito em 4 lugares, e o teste só confere a frase (LM-001).

### Approach C: Um script por lacuna

**Description:** `smoke-slot.sh` e `schema-check.sh` separados.

**Pros:**
- cada um fica menor.

**Cons:**
- o mesmo contrato duplicado em 2 scripts, que divergem na primeira correção.

## Selected Approach

| Attribute | Value |
|---|---|
| Chosen | Approach A — executor de slot único |
| User Confirmation | Roberto, 2026-11-09, na conversa: "A — executor de slot (Recomendado)" |
| Reasoning | contrato único e testável; o privado só aponta comandos |

## Key Decisions Made

| # | Decision | Rationale | Alternative Rejected |
|---|---|---|---|
| 1 | L0 + L3 + L4 numa frente só (F15_SLOTS), release `v2.8.0` | mesmo contrato de exit, mesmo executor; o inventário já admitia | 3 frentes/releases |
| 2 | Slots `smoke.before_ok_cmd`, `smoke.before_push_cmd`, `smoke.after_deploy_cmd`, `schema.check_cmd`, vazios por padrão; **reabertos por decisão do Roberto** (caíram na F13 e na F12) | registro limpo no §8.2 | `release.smoke_*` + `build.migration_check_cmd`; `migration.check_cmd` |
| 3 | Exit 2 do smoke com peso por momento: FAIL-candidato antes do OK; só registro antes do push; pergunta [D1] depois do deploy | OK único; o push não para depois do sim; o que está no ar pede decisão | sempre abortar; nunca abortar |
| 4 | Os 3 smokes são independentes e dividem `SDD_SLOT_DIR` | serve a quem só usa o `after_deploy`; sem estado no Open | exit 10 do 1º desliga os outros |
| 5 | Saída fora do contrato (1, 127, sinal) = INCONCLUSIVO, nunca verde: aviso antes do OK, registro antes do push, pendência depois do deploy; na L4, não aplica | nunca verde por omissão | tratar como 0 |
| 6 | L3: a release roda `test-baseline.sh --touched` no 0a; exit 2 aborta (NON_WAIVABLE); exit 3 WAIVABLE; PULADO declarado; a 0b cita o resultado em vez de perguntar ao modelo | o teste ao lado quebrado é consumidor quebrado | FAIL-candidato |
| 7 | `--touched` conta o teste alterado **e** o teste que existe ao lado de cada fonte alterada (mesma pasta) | é o que o teste do diff do privado já fazia | espelho `tests/` |
| 8 | L4 fail-closed: `schema.check_cmd <.sql do manifest>` antes da prévia; 2 ou inconclusivo = não aplica; 10 = segue e diz; vazio = "pulada: slot vazio"; log em `evidence/{F}/` | banco não tem undo | só avisar |
| 9 | Documentos SDD desta frente na branch nova `docs/f15-slots`, nascida de `origin/docs/incorporar-starter`; fora do commit do produto; push só com o OK | a `docs/incorporar-starter` está em uso na worktree `sdd-open-docs-f16`, que esta frente não toca (como fez a F21) | commitar na `docs/incorporar-starter` |

## Features Removed (YAGNI)

| Feature Suggested | Reason Removed/Deferred | Can Add Later? |
|---|---|---|
| Coluna nova em `## Migrations aplicadas` e `report-lint` exigindo a checagem de schema | o log em `evidence/` e a frase do 4b bastam; mudaria o parser | Yes |
| A release rodar `schema.check_cmd` de novo | já roda no build, antes do apply | Yes |
| `--touched` rodar só os testes do diff (como o deno do privado) | outra semântica; o Open roda a suíte e filtra o resultado | Yes |
| Teste em espelho (`tests/test_foo.py` para `src/foo.py`) | só "ao lado", na mesma pasta, como pedido | Yes |
| 2ª pergunta "rodar o smoke?" no OK, como no privado | regra do OK único: slot preenchido = roda | No |

## Incremental Validations

| Section | Presented | User Feedback | Adjusted? |
|---|---|---|---|
| Bloco 1: os 4 slots, `slot.sh`, o efeito de cada saída na release e no build | Yes | "Sim, está certo" | No |
| Bloco 2: L3, provas (teste + sabotagem + cópia sem `.git`), entrega `v2.8.0`, documentos em `docs/f15-slots` | Yes | "Sim, está certo" | No |

## Suggested Requirements for /define

### Problem Statement (Draft)

A `sdd-release` do Open não tem onde o projeto ligar um smoke visual, não roda teste nenhum antes do OK, e a `sdd-build` aplica migration sem um ponto de checagem do SQL. O privado da RDD não pode trocar o `/release` antigo pelo Open (fase 3 da F15) sem esses três pontos.

### Target Users (Draft)

| User | Pain Point |
|---|---|
| Projeto que usa o Open (inclui o privado da RDD) | não tem onde ligar smoke visual nem checagem de schema sem editar skill |
| Quem aprova a release | o bloco do OK não diz se o teste ao lado do código mudado passou |
| Quem aplica migration | SQL com problema conhecido chega ao banco, que não tem undo |

### Success Criteria (Draft)

- [ ] `sdd/bin/slot.sh` sai PULADO com o slot vazio ou ausente e repassa 0/2/10. Qualquer outro exit vira INCONCLUSIVO (código próprio), nunca 0. Testado com scripts falsos.
- [ ] O comando do slot recebe `SDD_MOMENTO`, `SDD_FEATURE`, `SDD_BASE`, `SDD_COMMIT`, `SDD_SLOT_DIR` e os arquivos como argumentos (teste lê o que o script falso recebeu).
- [ ] `test-baseline.sh --touched` com `src/foo.ts` alterado e `src/foo.test.ts` falhando sai 2 (hoje sai 0); o mesmo para `test_calc.py` ao lado de `calc.py` e `foo_test.go` ao lado de `foo.go`; teste não relacionado continua "fora do diff".
- [ ] `sdd-release` cita `slot.sh` nos 3 momentos e `test-baseline.sh --touched` no 0a, com o efeito de cada exit (decisões 3, 5, 6); o bloco do OK ganha as linhas de smoke e de testes do diff.
- [ ] `aplicar-migration.md` roda `schema.check_cmd` antes da prévia, fail-closed (decisão 8).
- [ ] `sdd/config.example.yaml` com os 4 slots vazios e comentados; o `adaptation-guide` (EN + PT) os descreve.
- [ ] Uma sabotagem por entrega (L0, L3, L4) derruba um teste nomeado.
- [ ] Verify Gate numa cópia por `git archive` (sem `.git`) sai 0, junto com `skill-lint --conversa`, `check-versions` e `publish-gate.sh`; grep de termos da RDD no diff vazio.
- [ ] Release `v2.8.0` publicada com `SHA256SUMS.txt` conferido.

### Constraints Identified

- Repositório público: nenhum caminho, tabela, edge, projeto ou script da RDD; a ligação dos slots é feita depois, no privado.
- bash 3.2 + python3 ≥ 3.9 stdlib; `docs/cli-conventions.md` (símbolo com palavra, `RESULTADO:` + `→`).
- Não tocar as worktrees `sdd-open-docs-f16` e `sdd-open-docs-f21`.
- Push só com "sdd-open autorizado".
- Instalação antiga sem os slots no `config.yaml` = vazio = pula e diz (compatível).

### Out of Scope (Confirmed)

- Os itens da tabela YAGNI.
- L1, L2, L5–L9 do inventário (scripts do privado ou já decididas lá).
- Ligar os slots no privado (feito depois, no privado).

## Session Summary

| Metric | Value |
|---|---:|
| Questions Asked | 4 (+ amostras) |
| Approaches Explored | 3 |
| Features Removed (YAGNI) | 5 |
| Validations Completed | 2 |

## Next Step

**Ready for:** `/sdd-define sdd/features/BRAINSTORM_F15_SLOTS.md`
