# BUILD REPORT: F28 — revisores pelo OpenRouter (`sdd-configurar-revisores`)

> Skill nova que mede o estado da revisão adversarial deste computador, conduz o aluno até os revisores
> configurados (CLIs que ele tem, OpenRouter, ou uma engine só) e grava a escolha no git config; o
> `adversarial-review.sh` lê essa escolha e mostra o plano mesmo sem diff.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | F28_REVISORES_OPENROUTER |
| **Date** | 2026-11-18 |
| **Author** | build-agent |
| **DEFINE** | [DEFINE_F28_REVISORES_OPENROUTER.md](../features/DEFINE_F28_REVISORES_OPENROUTER.md) (1.2) |
| **DESIGN** | [DESIGN_F28_REVISORES_OPENROUTER.md](../features/DESIGN_F28_REVISORES_OPENROUTER.md) (1.1) |
| **Status** | Complete |

---

## Summary

| Metric | Value |
|--------|-------|
| **Tasks Completed** | 32/32 do File Manifest, mais 6 arquivos fora dele (Deviations) |
| **Files Created** | 9 (7 da skill, 2 módulos de teste) |
| **Lines of Code** | +2.357 / −99 em 45 arquivos do pacote (sem os documentos da frente) |
| **Build Time** | uma sessão (18/11) |
| **Tests Passing** | 2.754 de 2.754 no Verify Gate (4 pulados), eram 2.686 em `eaeb874`; novos: 53 da skill, 9 da revisão, 6 do `checar` |
| **Agents Used** | revisor de governança, revisor e auditor da revisão adversarial (claude), avaliador fresco, 6 agentes de cenário |

---

## Landmines lidas no build

| Superfície | LM-nnn | Veredito | Como / onde |
|------------|--------|----------|-------------|
| testes novos | LM-001, LM-002 | ✔ tratado | linha de base vermelha em `eaeb874` (`evidence/…/BASELINE_eaeb874.log`) e 7 sabotagens (`SABOTAGEM.log`) |
| revisão sobre diff vazio | LM-003 | ✔ tratado | commit antes de cada rodada |
| sabotagem | LM-009 | ✔ tratado | mutantes só em cópia de `git archive` |
| OpenRouter pago | LM-010 | ✔ tratado | nenhuma chamada paga; revisão por assinatura (claude) |
| cenários | LM-011 | ✔ tratado | critério escrito antes; 6 de 6 (`CENARIOS.md`) |
| número longo | LM-012 | ✔ tratado | publish-gate verde |
| `subprocess` sem encoding, `bash` sem caminho, PATH de links | LM-014, LM-029, LM-034 | ✔ tratado | `encoding="utf-8"`, `BASH` e `path_restrito` de `tests/apoio.py` |
| skill do starter | LM-035 | ✔ tratado | mordeu: 2 citações a `sdd/bin/` na `sdd-checar-ambiente`; troca em `scripts/starter/trocas/sdd-checar-ambiente.md` (e de novo na rodada 3: a troca precisa acompanhar cada mudança do texto) |
| MANIFEST | LM-037 | ✔ tratado | 7 arquivos da skill e 2 testes no mesmo commit |
| `os.name` em teste | LM-042 | ✔ tratado | `WINDOWS`, `SEM_PTY` |
| HOME no filho | LM-043 | ✔ tratado | `HOME` passado no `env` de cada chamada |

---

## Candidatos ao playbook

```text
<<<CANDIDATO_PLAYBOOK
secao: Reviews / harness
sup: `S11` `sk-or-` `evals/cases.json` `fixture`
regra: Texto de cenário, fixture ou exemplo com a forma de uma chave (`sk-or-v1-…` com 32+ caracteres) bloqueia a varredura S11 da release como "chave secreta no código", mesmo sendo inventado. **Do instead:** descreva a chave em palavras ("um texto que começa por sk-or-") e monte o valor na hora da execução; rode `bash sdd/bin/seguranca-varredura.sh` antes do commit de arquivo de cenário.
evidencia: commit 8150a62 (evals/cases.json da sdd-configurar-revisores)
ficha: —
mordeu_antes: —
>>>
```

```text
<<<CANDIDATO_PLAYBOOK
secao: Reviews / harness
sup: `OpenRouter` `test_contrato_build_release` `nome de engine` `sdd-design` `sdd-build` `sdd-release`
regra: As seções de revisão das skills de fase (design, build, release) não podem nomear engine nem provedor: o `test_contrato_build_release` e o `test_f19_textos` reprovam "OpenRouter" ali. **Do instead:** nas fases, diga "credencial de uma engine"; o nome do provedor mora na skill própria e nos docs.
evidencia: commit e2ec9c4 (6 falhas antes do conserto)
ficha: —
mordeu_antes: —
>>>
```

```text
<<<CANDIDATO_PLAYBOOK
secao: Reviews / harness
sup: `evidence` `> $E/` `run_in_background` `VERIFY_GATE`
regra: Um log de evidência redirecionado com `{ …; } > arquivo` num comando em segundo plano fica com só a 1ª linha até o comando acabar; um `git add` da pasta no meio commita o log pela metade (o avaliador o achou com 95 bytes). **Do instead:** grave o log longo fora de `sdd/reports/evidence/` e copie para lá só depois do exit.
evidencia: commit 3629287
ficha: —
mordeu_antes: —
>>>
```

```text
<<<CANDIDATO_PLAYBOOK
secao: Reviews / harness
sup: `urllib` `redirect` `Authorization` `Bearer`
regra: `urllib.request.urlopen` segue 3xx e repassa o cabeçalho `Authorization` ao novo endereço, inclusive outro host: um redirect leva a chave para fora. **Do instead:** em chamada com chave, use um opener com `HTTPRedirectHandler` que devolve `None` (o 3xx vira erro) e teste com um servidor local que responde 302.
evidencia: sdd/reviews/AVALIACAO_F28_REVISORES_OPENROUTER_20261118-2207.md, achado 1
ficha: —
mordeu_antes: —
>>>
```

---

## Task Execution with Agent Attribution

| # | Task | Agent | Status | Duration | Notes |
|---|------|-------|--------|----------|-------|
| 1 | `adversarial-review.sh`: git config, origem, `--dry-run` sem diff, papéis extras | (direct) | ✅ Complete | — | 170 testes antigos da revisão verdes |
| 2–3 | `precos.tsv` (2026-11-18), `config.example.yaml` | (direct) | ✅ Complete | — | `deepseek/deepseek-v4-flash` passou a 0,09 / 0,18 |
| 4–10 | a skill (`diagnosticar.sh`, `guardar-chave.sh`, `PASSO_A_PASSO.md`, `como-falar.md`, `SKILL.md`, `manifest.json`, `evals/cases.json`) | (direct) | ✅ Complete | — | 26 estados, 21 do script |
| 11–16 | `checar.sh` e os ganchos das fases | (direct) | ✅ Complete | — | versões: checar 1.7.0, design 2.11.0, build 2.14.0, release 2.19.0 |
| 17–23 | docs, README, `AGENTS.md.tmpl`, `MANIFEST.txt` | (direct) | ✅ Complete | — | 24 skills |
| 24–32 | testes novos e contagens | (direct) | ✅ Complete | — | 2.686 → 2.754 |

---

## Agent Contributions

| Agent | Files | Specialization Applied |
|-------|-------|------------------------|
| (direct) | 41 | DESIGN patterns only |

---

## Seleção de modo

| Item | Valor |
|---|---|
| Sinais | 32 arquivos, a maioria texto; 2 scripts novos e 1 mudança no `adversarial-review.sh`; o pacote não tem `layers:` |
| Recomendação | default (direto, nesta sessão) — as tarefas dependem umas das outras pelo texto (estados × tabela × testes) |
| Decisão do usuário | default, pela regra da frente (recomendação aceita como padrão), 2026-11-18 |

---

## Drift detectado

| # | Onde | O que divergiu do DESIGN | Decisão | Ação |
|---|---|---|---|---|
| 1 | `.agents/skills/sdd-checar-ambiente/scripts/checar.sh`, `SKILL.md` | 2 citações a `sdd/bin/` reprovavam o gerador do starter | desvio aprovado (LM-035) | troca em `scripts/starter/trocas/sdd-checar-ambiente.md` |
| 2 | ganchos das 3 fases | "OpenRouter" proibido nas seções de revisão das fases | desvio aprovado (regra existente) | "credencial de uma engine" |

---

## Files Created

| File | Lines | Agent | Verified | Notes |
| ---- | ----- | ----- | -------- | ----- |
| `.agents/skills/sdd-configurar-revisores/SKILL.md` | 188 | (direct) | ✅ | `skill-lint --conversa` verde |
| `.agents/skills/sdd-configurar-revisores/scripts/diagnosticar.sh` | 544 | (direct) | ✅ | bash 3.2 + Python 3.9 |
| `.agents/skills/sdd-configurar-revisores/scripts/guardar-chave.sh` | 111 | (direct) | ✅ | testado com pty |
| `.agents/skills/sdd-configurar-revisores/references/PASSO_A_PASSO.md` | 83 | (direct) | ✅ | fontes com data |
| `.agents/skills/sdd-configurar-revisores/references/como-falar.md` | 132 | (direct) | ✅ | 2 perguntas, lint de decisões verde |
| `.agents/skills/sdd-configurar-revisores/manifest.json` | 42 | (direct) | ✅ | — |
| `.agents/skills/sdd-configurar-revisores/evals/cases.json` | 40 | (direct) | ✅ | 3 cenários |
| `tests/test_f28_revisores.py` | 639 | (direct) | ✅ | 53 testes |
| `tests/test_f28_revisao_slots.py` | 195 | (direct) | ✅ | 9 testes |

---

## Verification Results

### Lint (`{{LINT_CMD}}`)

```text
N/A - o pacote não tem slot de lint; skill-lint --conversa, sdd-decisoes-lint --sites, ledger-revisao-lint e
design-lint verdes; seguranca-varredura: NADA ACHADO; publish-gate verde
```

**Status:** ✅ Pass

### Typecheck (`{{TYPECHECK_CMD}}`)

```text
N/A - não configurado
```

**Status:** ⏭️ Skipped

### Testes (`{{TEST_CMD}}`)

```text
Verify Gate em 016e591 (git archive + publish-gate + suíte inteira, SDD_TEST_BASH=/bin/bash):
Ran 2754 tests in 1778.665s — OK (skipped=4) — ✅ GATE VERDE — [exit=0]
1º gate em b987342: 1 falha (test_f16w2_saida: o Python embutido sem a troca de saída padrão) — GATE-1-VERMELHO_b987342.log
```

| Test | Result |
|------|--------|
| `test_f28_revisores` (53) | ✅ Pass |
| `test_f28_revisao_slots` (9) | ✅ Pass |
| `test_checar.TestRevisores` (6) | ✅ Pass |
| `test_revisao`, `test_f23b3_revisao`, `test_revisao_adapters`, `test_revisao_gate` (170) | ✅ Pass |

**Status:** ✅ 2.754/2.754 Pass (4 pulados)

---

## Advisor Ledger (condicional — só se houve review de 2º vendor)

**Consulta:** plan-review (DESIGN, D1 e D2) e delivery-review (código, rodadas 1 a 3) · 2026-11-18 · `sdd/bin/adversarial-review.sh`
**VERDICT do advisor:** código, rodada 3: 0 graves, 2 médios, 0 leves — loop PRONTO
**Ledger da revisão:** `sdd/reviews/LEDGER_REVISAO_F28_REVISORES_OPENROUTER.md`
**Proveniência:** revisor e auditor `claude` com `--um-engine` em todas as rodadas (`diversidade: nenhuma`): o `codex` está sem créditos na conta, o `gemini` sem credencial, e o OpenRouter não foi usado (gasto real exige o OK do Roberto). A D1 do DESIGN ficou sem auditor (`sem resultado`). 2º revisor dispensado pela regra (sem superfície de risco). Custo nominal, por assinatura: DESIGN US$ 0,88 + 1,76; código US$ 2,82 + 3,19 + 2,96.

| # | Nota | Severidade | Veredito | Evidência |
|---|------|-----------|----------|-----------|
| 1 | D2: 9 notas do DESIGN (precedência, JSON ilegível, perfil do bash, herança do ambiente, teto, aspas, sem base, status não classificado) | MED/LOW | APLICADA | commit `017d166`; ledger, rodada D2 |
| 2 | Código, rodada 1: 6 achados (perfil do macOS, `.local`, modelo padrão, origem do R09, teto, `--testar` com CLIs) | MED/LOW | APLICADA | commit `d850a75`; `RODADA1_VERMELHO.log` |
| 3 | Código, rodada 2: 5 achados (traceback, marca antiga, aspas com espaço, `if/then` no perfil, shell do aluno) | MED/LOW | APLICADA | commit `8f03b9e`; `RODADA2_VERMELHO.log` |
| 4 | Código, rodada 3: 2 achados (troca do starter, `--reviewer` com `--um-engine`) | MED | APLICADA | commit `b987342`; `RODADA3_VERMELHO.log` |

Os consertos da rodada 3 vieram depois da última revisão dentro do teto: a versão final não tem revisão própria. A
release pergunta (D3) se roda uma 4ª rodada (acima do teto) ou segue com a dispensa e o motivo.

---

## Segurança

| Item | Decisão | Motivo |
|---|---|---|
| — | nenhum recusado nem adiado | S10, S17, S18, S20 aplicados no Define (AT-002, AT-003) |

---

## Issues Encountered

| # | Issue | Resolution | Time Impact |
|---|-------|------------|-------------|
| 1 | codex sem créditos e gemini sem credencial: sem auditor de outro vendor | `--um-engine` com claude, registrado; OpenRouter não usado sem o OK do Roberto | +1 rodada (D1 sem auditor) |
| 2 | varredura S11 bloqueou o texto do cenário da chave colada | texto sem a forma de chave | +5 min |
| 3 | gerador do starter (LM-035), duas vezes | troca da `sdd-checar-ambiente`, refeita na rodada 3 | +20 min |
| 4 | log do gate commitado pela metade | log fora da pasta até o fim; o parcial saiu (`3629287`) | +1 gate |
| 6 | 1º gate completo vermelho: `test_f16w2_saida` exige o bloco padrão de troca de saída no Python embutido | nomes `_sdd_sys`/`_sdd_c` (`016e591`) | +1 gate (30 min) |
| 5 | `test_f17_textos` acusa um arquivo de `sdd/archive/` da F27 | anterior a esta frente (já em `eaeb874`); fora da cópia de `git archive` do gate (`sdd/** export-ignore`) | — |

---

## Deviations from Design

| Deviation | Reason | Impact |
|-----------|--------|--------|
| 6 arquivos fora do manifest: `tests/test_f16_textos.py`, `test_f25_skills_duplicadas.py`, `test_contrato_build_release.py`, `test_correcoes_w0.py`, `test_f14_drive_textos.py`, `test_f14_textos.py`, `test_f15_slots_textos.py`, `test_f18_f20_textos.py`, `test_f19_textos.py` (versões fixadas) e os 3 modos web/iniciante (linha de identificação), `scripts/starter/trocas/sdd-checar-ambiente.md` | as versões novas das skills tocadas e a LM-035 | só contagem e texto |
| "uma engine só" não é gravada | gravar a mesma engine nos dois papéis afrouxaria a regra "auditor diferente do revisor" (pergunta ao Roberto) | cada fase oferece `--reviewer <engine> --um-engine` |
| `--testar` não segue redirect; com os slots no OpenRouter, mede o par configurado | achados do avaliador | mais seguro; preço certo |

---

## Raio de impacto (feito na release, 0b)

2 superfícies, 2 agentes frescos, nenhum consumidor quebrado, nenhuma invariante tocada: `adversarial-review.sh`
(31 consumidores, entre testes, scripts e docs) e `checar.sh` (21). Observações sem quebra: a leitura usa
`git config --get`, que também vê o git config global (benigno; a skill grava só o local); quem escolhe uma engine
só continua vendo o aviso do `checar`; o glossário da `sdd-checar-ambiente` não traduz "revisão adversarial" nem
"OpenRouter"; o `SKILL.md` gerado no starter fica com 3 linhas em branco seguidas.

---

## Blockers (if any)

| Blocker | Required Action | Owner |
|---------|-----------------|-------|
| nenhum | — | — |

---

## Contrato de aceite (C2) e avaliador de contexto fresco (C1)

**Camadas do manifest:** 1 (o pacote não declara `layers:`)
**Contrato de aceite (passo 1.5 da `sdd-build`):** N.A. (1 camada)
**Veredito do avaliador (C1):** PASS_PENDENTE_RECIBO · ciclos: 1 · achados: 2 corrigidos com teste (redirect; par configurado) e o recibo do gate · `AVALIACAO_F28_REVISORES_OPENROUTER_20261118-2207.md`. Recibos: o Verify Gate (AT-010, abaixo) e o CI do PR nos 3 sistemas (na release).

---

## Acceptance Test Verification

| ID | Critério (EARS, verbatim do DEFINE) | Resultado | Evidência |
|----|-------------------------------------|-----------|-----------|
| AT-001 | When o diagnóstico roda, shall imprimir 1 `ESTADO:` com frase e passo e sair pela classe; só leitura; estados do script = linhas `script` da tabela | true | `evidence/F28_REVISORES_OPENROUTER/AT-001.log` |
| AT-002 | If a chave está no ambiente, then nada que a skill imprime ou grava a contém; perfil sem ler o valor; gravação sem eco; chave no chat ⇒ revogar | true | `evidence/F28_REVISORES_OPENROUTER/AT-002.log` |
| AT-003 | When `--testar`, shall fazer só GET da chave e dos modelos, 10 s, classificar; nenhum texto da resposta; decimal em centavos; 0 chat/completions | true | `evidence/F28_REVISORES_OPENROUTER/AT-003.log` |
| AT-004 | While a chave está no perfil e não no agente, shall dar a parada; na volta, seguir sem repetir; slots no OpenRouter sem chave ⇒ só a chave | true | `evidence/F28_REVISORES_OPENROUTER/AT-004.log` |
| AT-005 | When o OK, shall gravar no git config; a revisão lê com o slot vazio; slot > git config; flag > os dois; origem no plano; modelo × 67 | true | `evidence/F28_REVISORES_OPENROUTER/AT-005.log` |
| AT-006 | When `--dry-run` sem diff, shall sair 0 com o plano, a disponibilidade e os papéis extras; a revisão real sem diff continua 64 | true | `evidence/F28_REVISORES_OPENROUTER/AT-006.log` |
| AT-007 | If não quer o OpenRouter, then CLIs, uma engine só, agora não; Where OpenRouter, custo e privacidade antes do OK; modelo e preço só das tabelas | true | `evidence/F28_REVISORES_OPENROUTER/AT-007.log` |
| AT-008 | When os textos são lidos, shall valer: conversa, tabela, passos, glossário, parada, ganchos, docs, README, MANIFEST, lints | true | `evidence/F28_REVISORES_OPENROUTER/AT-008.log` |
| AT-009 | While o projeto tem a revisão e os revisores faltam, o `checar.sh` dá ⚠️, nunca 🔴; quieto nos outros modos e no starter | true | `evidence/F28_REVISORES_OPENROUTER/AT-009.log` |
| AT-010 | A revisão real, o gate offline, o `--conferir`, o adapter, a release, o `checar` shall continue to valer; bash 3.2 e Windows | true | `evidence/F28_REVISORES_OPENROUTER/AT-010.log` (Verify Gate em `016e591`, bash 3.2; o Windows é o recibo do CI do PR, na release) |

**Verify Gate (`sdd/bin/verify-gate.sh <DEFINE>`):** exit 0 em `016e591` · `evidence/F28_REVISORES_OPENROUTER/AT-010.log`

---

## Performance Notes

| Metric | Expected | Actual | Status |
|--------|----------|--------|--------|
| teto por consulta do `--testar` | 10 s pela chamada inteira | servidor mudo e servidor lento cortados em ~10 s (`Testar.test_R19_*`; avaliador: 10,2 s) | ✅ |
| chamadas de rede sem `--testar` | 0 | 0 (`test_so_le_nada_muda_e_nenhuma_chamada_de_rede`) | ✅ |

---

## Final Status

### Overall: ✅ COMPLETE

**Completion Checklist:**

- [x] All tasks from manifest completed
- [x] All verification checks pass (módulos)
- [x] All tests pass (Verify Gate em `016e591`)
- [x] No blocking issues
- [x] Acceptance tests verified — 10 de 10 com log
- [x] Avaliador de contexto fresco: PASS_PENDENTE_RECIBO com `AVALIACAO_*.md` persistido
- [x] Pronto para a `sdd-release` (o CI do PR nos 3 sistemas é o recibo que falta)

---

## Next Step

**If Complete:** `sdd-release` — publicar a skill `sdd-configurar-revisores` e o git config dos revisores na revisão adversarial.
