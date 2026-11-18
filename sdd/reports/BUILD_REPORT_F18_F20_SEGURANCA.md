# BUILD REPORT: F18 + F20 — segurança embutida no fluxo (alerta) e ações preventivas (prevenção)

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | F18_F20_SEGURANCA |
| **Date** | 2026-11-11 |
| **Author** | build-agent (worktree `sdd-open-f18-f20-seguranca`, branch `feat/f18-f20-seguranca`, de `69b7f6b` = `v2.11.0`) |
| **DEFINE** | [DEFINE_F18_F20_SEGURANCA.md](../features/DEFINE_F18_F20_SEGURANCA.md) v1.4 |
| **DESIGN** | [DESIGN_F18_F20_SEGURANCA.md](../features/DESIGN_F18_F20_SEGURANCA.md) v1.3 |
| **Status** | Complete |

---

## Summary

| Metric | Value |
|---|---|
| **Tasks Completed** | 34/34 linhas do manifest (a 34, `sdd-release/references/seguranca.md`, nasceu no build: a skill passaria de 500 linhas) |
| **Files Created** | 13 (catálogo, `INCIDENTE.md`, `como-falar.md`, `SKILL.md`, `manifest.json` e `evals/cases.json` da `sdd-seguranca`; `seguranca-varredura.sh`; `references/seguranca.md` da `sdd-release`; `docs/security.md` e o PT; 3 arquivos de teste) · 37 alterados |
| **Commits** | passo 0: `ce5ed04` (curadoria da F16), `62f0b8c` (sobras) · frente: `d67dd2d` (catálogo e varredura), `cccc4fb` (skill), `acc4706` (`AGENTS.md`), `f8b9447` (fases), `22c87da` (docs), `bf280b7` (cenários) · consertos: `a2230d2` (revisão, rodada 2), `ff164c6` (raio de impacto), `433785c` (revisão, rodada 3), `c30b54c` (avaliador, ciclo 1) |
| **Tests Passing** | exit 0 em `c30b54c`: 2.030 testes em 35 min, 1 pulado (`evidence/F18_F20_SEGURANCA/VERIFY-GATE-c30b54c.log`); a contagem subiu de 1.944 na partida (`62f0b8c`) |
| **Skills** | `sdd-seguranca` 1.0.0 (nova, 21ª), `sdd-brainstorm` 2.3.0, `sdd-define` 2.6.0, `sdd-design` 2.6.0, `sdd-build` 2.9.0, `sdd-release` 2.11.0, `sdd-new-session` 1.5.1 (passo 0); `check-versions.py --base v2.11.0` VERDE |

**Seleção de modo:** default (um autor; arquivos acoplados: o vocabulário do catálogo nas 6 skills, as contagens dos testes). Perguntado ao Roberto: "Padrão, nesta sessão".

**Revisão do DESIGN:** exigida (`sdd-fluxo.sh review-design` sai 0: 12 arquivos novos); rodada 1 antes do código das fases, registrada no Advisor Ledger do DESIGN (12 notas aplicadas) e no ledger da revisão.

**Passo 0 (sobras da F16):** curadoria com uma decisão do Roberto por candidato (LM-014 a LM-017 novas; LM-012 refinada com o id de run e posta em `## Descartados` das invariantes, porque o vigia dela, `scripts/publish-gate.sh`, não vai ao projeto do aluno); `sdd-new-session` 1.5.1 confere a versão e a forma da lista do `--editores` (rodada 4 da F16, R1); `doctor` diz a causa do Python uma vez e compara `sdd/bin/lib/`. Ficaram fora, por decisão do Roberto: o `--help` da `governanca-fronteira.sh`, o editor do `git config` no resumo do `checar` e a linha `gh:` no guia.

---

## Landmines lidas no build

| Fonte | Superfície | Veredito |
|---|---|---|
| LM-001 | testes que só conferem fiação | ✔ tratado: a varredura roda em repositórios git temporários, com caso que acusa e par que não acusa; 5 sabotagens mortas |
| LM-002 | linha de base vermelha | ✔ tratado: cada teste de conserto caiu antes (rodadas 1 a 3, raio, avaliador); os testes da frente caem em `69b7f6b` (o script nem existe lá) |
| LM-003 | commit antes de revisar | ✔ tratado: as 3 rodadas sobre árvore commitada, `diff_sha256` em cada pasta |
| LM-005 | heurística sobre texto livre | ✔ tratado: o catálogo é a fonte estruturada; um parser só (o `init` chama o script); as 2 cópias do ponteiro têm teste de identidade |
| LM-006 | script que só roda com `.git` | ✔ tratado: Verify Gate e sabotagens em cópia de `git archive`; varredura fora de git sai 64 com teste |
| LM-008 | saldo da OpenRouter | ✔ tratado: `/credits` antes de cada rodada (US$ 18,15, 18,13 e 18,09) |
| LM-009 | sabotagem que desfaz conserto | ✔ tratado: mutantes em cópias de `git archive` |
| LM-010 | 2º revisor pago | ✔ tratado: `--no-revisor2` nas 3 rodadas |
| LM-011 | cenário nunca executado | ✔ tratado: 2 cenários × 3 execuções em contexto novo, critério escrito antes, 6 de 6 |
| LM-012 | número longo no pacote | ✔ tratado: referências por id curto (CWE-nnn), nenhum id de run |
| LM-013 | edição por corte | ✔ tratado: `grep -c "def test_"` antes e depois de cada edição de teste por script |
| LM-014 | `subprocess` sem encoding | ✔ tratado: os testes usam `Sandbox.roda` (utf-8) |
| LM-015 | Python num pipe no Windows | ✔ tratado: o script lê `lib/python.sh`; o raio de impacto achou o `\r\n` e o script fixa o fim de linha |
| LM-017 | fallback silencioso | ✔ tratado: o caminho reserva do `AGENTS.md` imprime ⚠️ com a causa; o raio achou que eu mesmo calava a causa do Python (`2>/dev/null`) e o conserto tem teste |

---

## Candidatos ao playbook

<<<CANDIDATO_PLAYBOOK
secao: Reviews / harness
sup: `PIPESTATUS` `zsh` `[exit=` `evidência`
regra: Log de evidência gerado com `${PIPESTATUS[0]}` num shell zsh grava `[exit=]` vazio (a variável não existe no zsh): o log parece válido e não prova nada. **Do instead:** rode o comando sem pipe, guarde `rc=$?` e grave o log por um script executado com `bash`; confira que todo log novo termina em `[exit=<número>]`.
evidencia: sdd/reports/evidence/F18_F20_SEGURANCA/AT-001.log
ficha: —
mordeu_antes: —
>>>
<<<CANDIDATO_PLAYBOOK
secao: Reviews / harness
sup: `2>/dev/null` `dito uma vez` `sdd_python_pronto` `aviso`
regra: Calar com `2>/dev/null` uma função que avisa uma vez por processo (ela marca "já dito") apaga o aviso do processo inteiro: na F18/F20, a checagem do Python do bloco do `AGENTS.md` sumiu com a causa que o `doctor` e o `die` dos adaptadores deviam dizer depois. **Do instead:** chame a função sem calar o stderr (ela já evita repetir) e teste a frase no fluxo completo (`init`), não só no comando isolado.
evidencia: sdd/reports/evidence/F18_F20_SEGURANCA/RAIO-DE-IMPACTO.md
ficha: —
mordeu_antes: —
>>>
<<<CANDIDATO_PLAYBOOK
secao: Reviews / harness
sup: `chave falsa` `evidência` `AVAL` `varredura`
regra: Sonda de segurança que grava chave falsa por extenso (ou cabeçalho PEM) num log de evidência faz a varredura do próprio pacote bloquear e pode barrar o push da branch pública de documentos. **Do instead:** no brief do avaliador, peça que a chave seja montada em tempo de execução e que o log mostre só o comando que a monta; rode a varredura no pacote antes da release.
evidencia: sdd/reviews/AVALIACAO_F18_F20_SEGURANCA_20261111-1545-ciclo1.md
ficha: —
mordeu_antes: —
>>>
<<<CANDIDATO_PLAYBOOK
secao: Reviews / harness
sup: `DISAGREE_EVIDENCE` `auditor` `premissa` `git diff`
regra: O auditor rebateu 2 achados do revisor com premissa falsa sobre o git (que a linha `+++` não leva TAB no nome com espaço, que `git -C <subpasta> diff` devolve caminho relativo): medido num repositório temporário, os 2 achados eram reais. **Do instead:** desacordo do auditor sobre comportamento de ferramenta se decide por medição num repositório temporário, registrada no ledger, nunca pela palavra de um dos dois.
evidencia: sdd/reviews/LEDGER_REVISAO_F18_F20_SEGURANCA.md
ficha: —
mordeu_antes: —
>>>

---

## Files Created

| Arquivo | O que é |
|---|---|
| `.agents/skills/sdd-seguranca/references/CATALOGO_SEGURANCA.md` | 22 fichas com 13 campos fixos; texto próprio; referência OWASP/CWE |
| `sdd/bin/seguranca-varredura.sh` | único leitor do catálogo: varredura (0/1/2/64), `--stack`, `--regras`, `--checklist`, `--agents` |
| `.agents/skills/sdd-seguranca/SKILL.md` + `INCIDENTE.md`, `como-falar.md`, `manifest.json`, `evals/cases.json` | skill nova, 4 modos |
| `.agents/skills/sdd-release/references/seguranca.md` | o detalhe da varredura, da 0c e do fecho |
| `docs/security.md`, `docs/pt-BR/security.md` | como a segurança entra no fluxo |
| `tests/test_seguranca_varredura.py`, `tests/test_seguranca_catalogo.py`, `tests/test_f18_f20_textos.py` | 66, 10 e 11 testes |

Alterados (principais): as 5 skills de fase e a `sdd-new-session`; os 4 templates; `AGENTS.md.tmpl`; `bin/sdd-open.sh`
(bloco de segurança, `doctor`); `sdd/bin/design-lint.py`; `sdd/config.example.yaml`; `sdd/playbook.md` e
`sdd/invariants.md` (passo 0); READMEs, guia do aluno, `cli-conventions`; `MANIFEST.txt`; os testes com contagem ou
versão fixada.

---

## Verification Results

| Check | Resultado |
|---|---|
| Verify Gate (`verify-gate.sh --strict sdd/features/DEFINE_F18_F20_SEGURANCA.md`) | exit 0 em `c30b54c`: 2.030 testes em 35 min, 1 pulado; `publish-gate` GREEN na cópia de `git archive` (`VERIFY-GATE-c30b54c.log`). Em `22c87da` saiu 2 (3 testes com "20 skills"; consertados) |
| `check-versions.py --base v2.11.0` | VERDE, 21 skills |
| `skill-lint.py --conversa` nas 21 skills | ok |
| `sdd-decisoes-lint.sh --sites .agents/skills` | 30 perguntas em 25 arquivos, todas marcadas |
| Sabotagens (`SABOTAGEM.log`, em `22c87da`) | 5 de 5 mortas: bloqueio vira aviso; stack ignorada; dispensa sem motivo aceita; teto ignorado; regra de Supabase sem Supabase no `AGENTS.md` |
| Cenários de comportamento (`CENARIOS-criterio.md`, `CENARIOS-resultado.md`) | 6 de 6 aprovadas (sem gatilho ⇒ N.A. em 1 linha; login + Supabase ⇒ 5 itens do mais grave, 1 pergunta, DEFINE intacto) |
| Raio de impacto (`RAIO-DE-IMPACTO.md`, antes da última rodada) | 4 superfícies, 125 consumidores; 4 quebras, consertadas em `ff164c6` com testes vermelhos antes |
| Varredura no próprio pacote | `RESULTADO: NADA ACHADO` em `c30b54c` |

---

## Segurança

Itens recusados ou adiados no passo de segurança do Define: nenhum (esta frente é o próprio pacote; o passo 12 nasce nela).

---

## Issues Encountered

| # | Issue | Resolution | Time Impact |
|---|-------|------------|-------------|
| 1 | 1ª revisão de governança caiu: rodei o `verify-gate.sh` entre a foto de antes e o despacho, e o rastro dele apareceu como escrita fora do permitido | 2ª tentativa com foto nova, limpa; motivo registrado no DEFINE | +5 min |
| 2 | `sdd-release` passou de 500 linhas | detalhe para `references/seguranca.md` | +10 min |
| 3 | Logs de evidência com `[exit=]` vazio (zsh) | regenerados por script bash (candidato ao playbook) | +5 min |
| 4 | Logs do avaliador (ciclo 1) com cabeçalho PEM: a varredura do pacote bloqueava | o cabeçalho PEM passou a exigir o corpo da chave (falso positivo real em documentação); brief do ciclo 2 pediu chave montada em tempo de execução | +15 min |

---

## Deviations from Design

| Deviation | Reason | Impact |
|-----------|--------|--------|
| catálogo em fichas por item, não tabela (DEFINE v1.1) | legível na web, sem escapar `\|` | nenhum: fonte única mantida |
| `sdd-build` 2.9.0 (não 2.8.0) | já estava em 2.8.0 | — |
| `references/seguranca.md` da `sdd-release` (manifest linha 34) | teto de 500 linhas da skill | o detalhe fica na referência |
| S11 varre também `sdd/` e as pastas dos agentes (DESIGN v1.3) | avaliador ciclo 1, A1 | a exclusão de pastas fica só para os padrões de código |
| PEM só com o corpo da chave | documentação mostra o cabeçalho | chave sem corpo não bloqueia (não é chave) |
| `PAROU` sem Python (Decision 12 dizia ERRO DE USO) | igual aos outros scripts de `sdd/bin` | `cli-conventions` diz isso |

---

## Contrato de aceite (C2) e avaliador de contexto fresco (C1)

**Camadas do manifest:** 1 (o pacote não declara `layers:`)
**Contrato de aceite (passo 1.5 da `sdd-build`):** N.A. (1 camada)

**Veredito do avaliador (C1):** PASS_PENDENTE_RECIBO · ciclos: 2 · achados: 4 no ciclo 1 (NEEDS_WORK: 1 média-alta, 1 média, 1 baixa, 1 cosmética, todos resolvidos em `c30b54c` e no DEFINE v1.3), 1 baixo de texto no ciclo 2 (resolvido no DEFINE v1.4) · `AVALIACAO_F18_F20_SEGURANCA_20261111-1702-ciclo2.md` (ciclo 1: `AVALIACAO_F18_F20_SEGURANCA_20261111-1545-ciclo1.md`)

O recibo que o ciclo 2 pediu é o Verify Gate com a suíte inteira em `c30b54c`: saiu exit 0 com 2.030 testes (≥ 1.944), em `VERIFY-GATE-c30b54c.log`. Os 10 ATs passaram por execução no ciclo 2.

---

## Advisor Ledger

Ledger completo: `sdd/reviews/LEDGER_REVISAO_F18_F20_SEGURANCA.md` (23 linhas, `ledger-revisao-lint.sh` VERDE).

| Rodada | Pasta | Engines | Achados | Decisão |
|---|---|---|---|---|
| 1 (DEFINE + DESIGN) | `EXTERNAL_REVIEW_20261111-134705` | claude + `openrouter` (qwen) | 9 médios, 3 leves | 12 aplicados (4 com dano: R1, R4, R8, R10) |
| 2 (código, diff inteiro) | `EXTERNAL_REVIEW_20261111-141409` | claude + qwen; desempate codex sem cota | 3 graves (R1, R2, N2), 2 médios, 2 leves | 7 aplicados (6 com dano); R2 e R3, rebatidos pelo auditor, decididos por medição do git |
| 3 (código, depois do raio de impacto) | `EXTERNAL_REVIEW_20261111-152012` | claude + qwen | 1 médio, 3 leves | 4 aplicados (1 com dano: R1); `sdd-fluxo.sh loop` PRONTO |

Os consertos depois da rodada 3 (`433785c`, os da própria rodada; `c30b54c`, os do avaliador) não passaram por revisor externo: a rodada 3 é o teto do método.

**Medidor dos revisores (`bash sdd/bin/eval-revisores.sh`):**

| Papel | Engine (modelo) | Cobrança | Rodadas | Pago US$ | Nominal US$ | Achados | Aplicados | Com dano | Falsos positivos | Nominal por dano | AGREE |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| revisor | claude (claude-opus-5-5) | assinatura | 3 | 0.0000 | 4.5580 | 21 | 21 de 21 | 9 de 21 | 0 de 21 | 0.5064 | — |
| auditor | openrouter (qwen/qwen3.7-plus via Alibaba) | pay-per-token | 3 | 0.1082 | 0.1082 | 2 | 2 de 2 | 2 de 2 | 0 de 2 | 0.0541 | 90.5% (19 de 21) |
| desempate | codex | assinatura | 0 (1 falha: cota) | 0.0000 | n/d | 0 | 0 | 0 | 0 | — | — |

---

## Drift detectado

Nenhum: a frente não tem prompt de produção (`LLM Prompts: false`; "prompt injection" e "chamada a IA" são tema do catálogo, não código).

---

## Acceptance Test Verification

| ID | Critério (resumo do EARS do DEFINE v1.4) | Resultado | Evidência |
|---|---|---|---|
| AT-001 | segredo literal acrescentado ⇒ 2 com `🛑 S11 <grav> arq:linha` em qualquer caminho (menos `node_modules/` e o catálogo); já existia ⇒ aviso; leitura por nome não é segredo; sem base ⇒ tudo novo; valor nunca na saída | true | `evidence/F18_F20_SEGURANCA/AT-001.log` |
| AT-002 | tabela nova sem RLS (com Supabase) ⇒ 2; sem Supabase, S01 não avalia | true | `evidence/F18_F20_SEGURANCA/AT-002.log` |
| AT-003 | 7 padrões ⇒ 1 com id, gravidade, `arq:linha` e a prova à mão; pares negativos não acusam; sem achado ⇒ 0 | true | `evidence/F18_F20_SEGURANCA/AT-003.log` |
| AT-004 | teto `security.max_warnings`, os mais graves, "e mais K", bloqueio fora do teto, `--saida` com tudo | true | `evidence/F18_F20_SEGURANCA/AT-004.log` |
| AT-005 | dispensa com motivo ⇒ aceito uma vez; sem motivo ou de outro item ⇒ não vale | true | `evidence/F18_F20_SEGURANCA/AT-005.log` |
| AT-006 | stack detectada ou do slot; item de outra stack não dispara; `--stack` | true | `evidence/F18_F20_SEGURANCA/AT-006.log` |
| AT-007 | `AGENTS.md` com as regras da stack e o ponteiro; `sync --check` acusa stack nova; ≤ 2 KB; sem catálogo, só o ponteiro | true | `evidence/F18_F20_SEGURANCA/AT-007.log` |
| AT-008 | catálogo com 22 itens e 13 campos; bloqueio só S01 e S11; padrões com par; sem material de origem | true | `evidence/F18_F20_SEGURANCA/AT-008.log` |
| AT-009 | textos das fases, `test_agnostico`, `skill-lint`, aviso do `design-lint` | true | `evidence/F18_F20_SEGURANCA/AT-009.log` |
| AT-010 | não-regressão: `checar --segredo`, governança, um OK, gate só pela Governança, bash 3.2, contagens | true | `evidence/F18_F20_SEGURANCA/VERIFY-GATE-c30b54c.log` |

**Verify Gate:** exit 0 em `c30b54c`: 2.030 testes em 35 min, 1 pulado (`evidence/F18_F20_SEGURANCA/VERIFY-GATE-c30b54c.log`)

---

## Final Status

### Overall: ✅ COMPLETE

- [x] 34 linhas do manifest
- [x] Verify Gate verde, linhas de base vermelhas, 5 sabotagens mortas
- [x] ATs com evidência abrível
- [x] revisão: 3 rodadas (o teto), 23 achados aplicados, loop PRONTO
- [x] avaliador de contexto novo: PASS_PENDENTE_RECIBO no ciclo 2 (o último do teto), recibo = o Verify Gate acima
- [x] Pronto para a `sdd-release`, com as ressalvas abaixo

**Pendências que saem desta frente:**
- **Consertos depois da rodada 3 sem revisor externo** (`433785c`, `c30b54c`): decisão do Roberto na release (4ª rodada acima do teto, ou dispensa registrada).
- **Cenário `incidente-chave`** escrito e não executado (LM-011); os 2 do modo Define foram executados.
- **Windows:** o fim de linha `\n` da varredura tem teste de texto e de bytes no macOS; no Windows não roda teste automático (F16W).
- **Falso positivo no mundo real** não medido (os casos são escritos do zero, decisão do brainstorm).
- **"item 10"** da FASE 2 da `sdd-release` (citado em `docs/adaptation-guide.md`, `slot.sh`, `deploy-do-sha.sh`) convive com o item 10 da 0a: ambíguo, não quebra.
- **Sessão de recuperação "rode só o passo 11"** do `verify-gate.sh` pula o passo 12 (sem trava, a linha Segurança fica pendente).
- **Starter:** recebe pela F17.

---

## Next Step

**If Complete:** `/sdd-release F18_F20_SEGURANCA` — bump minor do pacote (`v2.12.0`: skill nova e funcionalidade nova em 5 skills)
