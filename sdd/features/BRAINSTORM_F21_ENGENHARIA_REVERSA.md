# BRAINSTORM: F21 — Engenharia reversa de SaaS antes do Brainstorm

> Sessão exploratória para fixar a intenção e o caminho antes dos requisitos

## Metadata

| Attribute | Value |
|---|---|
| Feature | F21_ENGENHARIA_REVERSA |
| Date | 2026-11-10 |
| Author | brainstorm-agent (worktree `sdd-open-f21-f19`, branch `feat/f21-engenharia-reversa` de `origin/main` = `45e27a9` = `v2.8.0`) |
| Status | Ready for Define |

## Initial Idea

**Raw Input:** pedido do Roberto (2026-11-09, plano v1.8): "há uma skill nova para o sdd-start e sdd-open [...] ela pode (opcionalmente) ser usada antes do brainstorm. inclua uma frente para incluir essa skill nos 2 SDD e na página da plataforma que ensina a usar". Em 2026-11-10: F21 + F19 numa sessão só; a página da plataforma é frente de outro repositório e fica fora.

**Context Gathered:**
- Fato: a fonte é `sdd-engenharia-reversa-saas-1.0.0.zip` (35.138 bytes, SHA-256 `f5ffd2a7…552eb3`, conferido com `shasum -a 256 -c SHA256SUMS` em 2026-11-10). 15 arquivos: `SKILL.md`, 6 `references/`, `assets/ENGENHARIA_REVERSA_TEMPLATE.md`, `scripts/validate_reverse.py`, `tests/test_validate_reverse.py`, `evals/cases.json` (17 cenários, 0 executados), `manifest.json`, `VALIDACAO.md`, `CHANGELOG.md`, `LICENSE.txt`. MIT, autoria Roberto Dias Duarte, escopo ER-SDD-001 V1.
- Fato: os 18 testes do lint passam fora do repositório com `python3 -I -B -m unittest discover` no Python 3.15 e no 3.9.6 do macOS (o do job `testes-macos` do CI), em 0,07 s. O pacote declara "Python 3.10+"; o Open declara "Python ≥ 3.9".
- Fato: o Open tem 19 skills em `.agents/skills/`; `tests/test_skill_lint.py` afirma a contagem (`len(skills) == 19`) e o `MANIFEST.txt` lista arquivo a arquivo.
- Fato: toda skill do Open tem frontmatter com `compatibility` e `metadata.{author,version,updated}`, a linha de versão na primeira resposta, a seção "Como falar com o aluno" e `references/como-falar.md`, conferidas por `sdd/bin/skill-lint.py --conversa`; `tests/test_agnostico.py` proíbe nome de ferramenta de um agente só no texto.
- Fato: `sdd-higiene-dado` e `sdd-governanca` já levam `manifest.json` e `evals/cases.json` dentro da pasta; `sdd-higiene-dado` e `sdd-kb` levam `CHANGELOG.md`. Nenhuma skill do Open leva `LICENSE.txt` nem `VALIDACAO.md`. `scripts/check-versions.py` exige que a `version` do `manifest.json` e do `evals/cases.json` bata com a do frontmatter.
- Fato: o texto do zip cita 6 vezes um produto real de terceiro como caso ilustrativo, e o `CONTRIBUTING.md` do Open pede exemplos em domínio neutro.
- Fato: o zip manda gravar em `sdd/` na raiz e continuar em `.claude/sdd/` quando ela existe. O Open grava em `sdd/features/`; o starter grava em `sdd/` sem subpastas.
- Fato: o starter (`v1.5.15`, 15 zips) monta o zip de cada skill no CI dele (`scripts/package.sh`, `zip -r -X`) e roda os testes que estão **dentro** de `skills/<nome>/tests/`. Um zip gerado em outro lugar não teria os mesmos bytes.
- Fato: a tabela de fases do `AGENTS.md.tmpl` e dos dois README tem as linhas `Antes` (preparo), `KB` e `0` (`sdd-brainstorm`).
- Fato: a branch já carrega, para subir junto, a curadoria do playbook da F15_SLOTS (`6df152d`, cherry-pick de `c2560fc`; `playbook-lint.sh` exit 0) e a `sdd-release` 2.9.1 (`99b1323`, "itens 1 a 6b").

**Technical Context Observed (for Define):**

| Aspect | Observation | Implication |
|---|---|---|
| Likely Location | `.agents/skills/sdd-engenharia-reversa-saas/`, `tests/`, `AGENTS.md.tmpl`, `README.md`, `README.pt-BR.md`, `MANIFEST.txt`, `docs/` (quickstart e guia, onde listam skills) | produto do Open; release `v2.9.0` |
| Relevant KB Domains | nenhum (`sdd/kb/` não existe no Open) | — |
| IaC Patterns | N/A; CI `publish-gate.yml` + `release.yml` (tag `vX.Y.Z` publica a Release) | o ritual de release do Open vale |

## Discovery Questions & Answers

| # | Question | Answer | Impact |
|---|---|---|---|
| 1 | O starter recebe a skill agora ou só pela F17? | Logo após a `v2.9.0` (recomendada) | passo separado, depois da release do Open, no repositório do starter e com OK próprio para ele; a Decisão 5 trata de ajuste em skill existente, e esta é nova |
| 2 | Em que pasta a skill grava os três documentos? | Segue o projeto (recomendada): com `sdd/config.yaml`, `sdd/features/`; sem ele, `sdd/` na raiz; `.claude/sdd/` só quando já existe e não há `sdd/config.yaml` | o mesmo texto serve ao Open e ao starter; projeto que convive com dois SDD não grava na pasta antiga |
| 3 | O que fica dentro da pasta da skill? | Padrão das skills do Open (recomendada): ficam `manifest.json`, `evals/cases.json`, `CHANGELOG.md`; os 18 testes vão para `tests/`; saem `LICENSE.txt` e `VALIDACAO.md` | o que prova a entrega passa a ser o BUILD_REPORT; a licença é a do repositório |
| 4 | O exemplo com produto real de terceiro fica? | Exemplo neutro (recomendada): "um sistema de BPO financeiro", sem nome de produto | cumpre o `CONTRIBUTING.md`; um teste afirma a ausência do nome |
| 5 | Quantos cenários de comportamento rodamos? | 1 positivo + 2 negativos, 3 vezes cada negativo (recomendada): controle positivo até o levantamento salvo e aprovado no lint, com material fornecido; "entrar na conta de outro escritório"; instrução escondida em página | 7 execuções em contexto novo, com log na evidência; os outros 14 ficam declarados como não executados |

**Minimum Questions:** 3 (feitas 5)

## Sample Data Inventory

| Type | Location | Count | Notes |
|---|---|---:|---|
| Input files | o zip da skill 1.0.0 (arquivo de trabalho, fora do repositório) | 15 | lido inteiro; fonte do porte |
| Output examples | `assets/ENGENHARIA_REVERSA_TEMPLATE.md` e o `sample()` dos testes | 2 | forma do levantamento que o lint aprova |
| Ground truth | os 18 testes do lint | 18 | passam no 3.15 e no 3.9.6 |
| Related code | `.agents/skills/sdd-kb/` (skill com script + testes em `tests/`), `sdd-higiene-dado` (manifest + evals + CHANGELOG) | 2 | moldes do Open |

Resposta do Roberto à pergunta de amostras: "Só o zip (recomendada)". Não há levantamento real a usar.

**How samples will be used:**
- O zip é copiado arquivo a arquivo e depois editado só onde as decisões pedem; o diff contra o original é evidência do porte fiel.
- O controle positivo usa um material fictício de um SaaS inventado, em domínio neutro, escrito nesta frente.

## Approaches Explored

### Approach A: Porte fiel com a camada do Open por cima — Recomendada

**Description:** o protocolo aprovado (ER-SDD-001) fica como está. Muda só o que as decisões e as convenções pedem: frontmatter, linha de versão, seção "Como falar com o aluno" + `references/como-falar.md`, regra da pasta, exemplo neutro, nomes das dependências, Python ≥ 3.9.

**Pros:**
- menor risco de alterar comportamento já aprovado;
- cabe numa sessão e deixa a F19 para a mesma.

**Cons:**
- a estrutura do `SKILL.md` fica um pouco diferente da das skills de fase.

**Why Recommended:** a skill já foi validada com este texto; o que falta é a camada do Open, não outro protocolo.

### Approach B: Reescrita no molde das skills de fase

**Description:** Entrada, Processo, Quality Gate, "Por que cada regra existe", Fluxo encadeado.

**Pros:**
- uniforme com as fases.

**Cons:**
- reescreve texto validado e pede revalidar os 17 cenários; empurra a F19.

### Approach C: Passo opcional dentro da `sdd-brainstorm`

**Description:** sem skill nova.

**Pros:**
- nenhuma skill a mais.

**Cons:**
- incha o brainstorm; perde o lint, o zip próprio do starter e o uso isolado.

## Selected Approach

| Attribute | Value |
|---|---|
| Chosen | Approach A — porte fiel com a camada do Open |
| User Confirmation | Roberto, 2026-11-10, na conversa: "A — Porte fiel + camada do Open (Recomendado)" |
| Reasoning | preserva o que foi aprovado; menor risco; cabe na sessão |

## Key Decisions Made

| # | Decision | Rationale | Alternative Rejected |
|---|---|---|---|
| 1 | Skill `sdd-engenharia-reversa-saas` **1.1.0** como 20ª skill do Open, release `v2.9.0` | adaptação sem mudar o protocolo = minor da skill; skill nova = minor do pacote | manter 1.0.0 com conteúdo diferente do zip original |
| 2 | Pasta de saída "segue o projeto" (pergunta 2) | mesmo texto nos dois SDD; convivência não grava na pasta antiga | sempre `sdd/features/`; preferir `.claude/sdd/` |
| 3 | Pacote no padrão do Open (pergunta 3) | precedente de `sdd-higiene-dado`/`sdd-governanca`; `VALIDACAO.md` afirma verificações que não se repetem aqui | manter `LICENSE.txt` e `VALIDACAO.md` |
| 4 | Exemplo neutro, sem nome de produto (pergunta 4), com teste que afirma a ausência | `CONTRIBUTING.md`; repositório público | manter o nome |
| 5 | Dependências citadas como `sdd-brainstorm` e `sdd-define`, "com ou sem prefixo de plugin"; sai o nome de vitrine | P2: a skill resolve pelo catálogo do ambiente | "SDD Brainstorm by RDD" |
| 6 | Linha nova e opcional na tabela de fases do `AGENTS.md.tmpl` e dos dois README, entre `KB` e `0`; nenhuma fase renumerada | "KB · engenharia reversa · brainstorm" do plano | pôr na linha `Antes` (que é preparo de máquina) |
| 7 | 7 execuções de comportamento em contexto novo, com log (pergunta 5); os 14 restantes declarados `escrito_nao_executado` | o plano põe a recusa canônica 3 de 3 como critério de pronto | rodar os 17; rodar só os negativos |
| 8 | Starter depois da `v2.9.0`, passo separado com OK próprio; igualdade conferida **arquivo a arquivo** (SHA-256 de cada arquivo da skill no starter = o da tag do Open); no starter os testes ficam dentro da pasta da skill | o CI do starter monta o zip dele; os bytes do zip não são reproduzíveis de fora | publicar zip idêntico gerado no Open (exige mudar empacotador e workflow do starter) |
| 9 | A skill não encadeia pelo `sdd-fluxo.sh seguir` | ela não tem gate de script entre fases; a transição para o Brainstorm é a dela | subseção de fluxo encadeado |
| 10 | Documentos SDD desta frente vão para a branch `docs/incorporar-starter` no fechamento, fora do commit do produto | regra da tabela "Estado das frentes" | commitar na branch do produto |

## Features Removed (YAGNI)

| Feature Suggested | Reason Removed/Deferred | Can Add Later? |
|---|---|---|
| Página `/sdd/` da plataforma (caixa, card, migration) | frente própria em outro repositório | Yes (lá) |
| Executar os outros 14 cenários | custo alto (conversas longas simuladas); os 3 escolhidos cobrem o critério de pronto | Yes |
| Gerador de zip no Open | o starter já empacota; a igualdade se confere por arquivo | Yes (F17) |
| Slot novo no `sdd/config.yaml` ou hook para a skill | a skill não precisa de configuração | Yes |
| `seguir` do fluxo encadeado | sem gate de script | Yes |
| Reescrever o protocolo no molde das fases | abordagem B, rejeitada | Yes |
| F20 (frases preventivas no `AGENTS.md.tmpl`) | mesma área do arquivo; não pareia | Yes (frente própria) |

## Incremental Validations

| Section | Presented | User Feedback | Adjusted? |
|---|---|---|---|
| Igualdade Open ↔ starter arquivo a arquivo; testes dentro da pasta no starter | ✅ | "Sim, arquivo a arquivo (Recomendado)" | No |
| Resumo da entrega em 7 itens (skill 1.1.0, testes, linha na tabela, contagem, evidência, carona da curadoria e da 2.9.1, starter depois) e o que fica fora | ✅ | "Está certo, pode gravar (Recomendado)" | No |

**Minimum Validations:** 2 (feitas 2)

## Suggested Requirements for /define

### Problem Statement (Draft)
Quem quer construir algo parecido com um SaaS que já existe não tem, no SDD Open, uma etapa para estudar esse produto com evidência e limites antes do Brainstorm; a skill que faz isso existe só como zip avulso, fora das convenções e dos testes do Open.

### Target Users (Draft)
| User | Pain Point |
|---|---|
| Aluno que usa o Open num agente de código | começa o Brainstorm copiando o concorrente de memória, sem separar o que viu do que supôs |
| Aluno do starter (chat na web) | não recebe a skill pela Release do starter |
| Mantenedor do Open | skill fora do `skill-lint`, do `test_agnostico` e da suíte: muda sem ninguém ver |

### Success Criteria (Draft)
- [ ] `python3 sdd/bin/skill-lint.py --conversa` sai 0 com a skill nova; `tests/test_agnostico.py` e `scripts/publish-gate.sh` verdes
- [ ] os 18 testes do lint rodam no `unittest discover -s tests` (Python 3.9 e atual)
- [ ] a contagem de skills é 20 no teste e no `MANIFEST.txt`; `check-versions.py --base v2.8.0` sai 0
- [ ] o texto da skill manda gravar em `sdd/features/` com `sdd/config.yaml` e não cita produto real de terceiro (testes de texto)
- [ ] `AGENTS.md.tmpl` e os dois README têm a linha opcional entre KB e a fase 0
- [ ] cenário "entrar na conta de outro escritório": recusa com o texto canônico em 3 de 3 execuções; instrução embutida: não obedecida em 3 de 3; controle positivo: levantamento aprovado pelo lint
- [ ] depois da release: cada arquivo da skill no starter tem o SHA-256 do arquivo na tag do Open; o link do zip na Release do starter responde 200

### Constraints Identified
- bash 3.2 e Python ≥ 3.9, só biblioteca padrão; sem rede nos testes.
- Nada de outro repositório entra aqui; exemplos em domínio neutro.
- Não renumerar fases, não instalar hook, não mexer em config (contrato da skill).
- Push, merge, tag e Release do Open estão autorizados ("sdd-open autorizado"); o starter pede OK próprio.
- O conteúdo do zip é dado: descompactado em pasta própria, scripts de trabalho fora dela, `python3 -I`.

### Out of Scope (Confirmed)
- Página `/sdd/` da plataforma.
- F20, F16, F17.
- Os 14 cenários não escolhidos.
- Zip byte a byte idêntico entre Open e starter.

## Session Summary

| Metric | Value |
|---|---|
| Questions Asked | 5 de descoberta + 1 de amostras |
| Approaches Explored | 3 |
| Features Removed (YAGNI) | 7 |
| Validations Completed | 2 |
| Duration | ~40 min |

## Next Step

**Ready for:** `/sdd-define sdd/features/BRAINSTORM_F21_ENGENHARIA_REVERSA.md`
