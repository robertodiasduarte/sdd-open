# BUILD REPORT: F17 — starter gerado a partir do Open

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | F17_STARTER_GERADO |
| **Date** | 2026-11-12 |
| **Author** | build-agent (worktree `sdd-open-f17-starter-gerado`, branch `feat/f17-starter-gerado`, de `e22a1b2` = `v2.12.1`) |
| **DEFINE** | [DEFINE_F17_STARTER_GERADO.md](../features/DEFINE_F17_STARTER_GERADO.md) v1.3 |
| **DESIGN** | [DESIGN_F17_STARTER_GERADO.md](../features/DESIGN_F17_STARTER_GERADO.md) v1.1 |
| **Status** | Complete |

---

## Summary

| Metric | Value |
|---|---|
| **Tasks Completed** | 15/15 linhas do manifest (a 11, `check-versions.py` do Open, saiu: Decision 8 superada pela 10) |
| **Files Created** | 33 no pacote: `scripts/gerar-starter.py`; `scripts/starter/` (lista, tabela do `openai.yaml`, 2 blocos, `lint-aceitos.tsv`, 13 arquivos de trocas, 9 arquivos da infra do starter em `raiz/`); `tests/test_gerar_starter.py`, `test_f17_textos.py`, `test_f17_passo0.py` |
| **Commits** | passo 0: `aaf779c`, `13e1c2e` · Open recebe do starter e consertos: `f3acd0b`, `915e2cf`, `533e707`, `1612fad` · gerador: `390c3e9`, `35dc9e4`, `910ae24`, `2be8f36` · raio de impacto: `a369f01`, `b464d1d`, `4b6a2df` · revisão e avaliador: `61a575a`, `ec557ad`, `62bfda4`, `0396642`, `02ad073`, `d813954` |
| **Tests Passing** | exit 0 em `d813954`: 2.090 testes em 32 min, 1 pulado (`evidence/F17_STARTER_GERADO/VERIFY-GATE-d813954.log`); partida: 2.033 em `e22a1b2` |
| **Skills** | `sdd-new-session` 1.6.0, `sdd-auditoria-harness` 1.2.1, `sdd-prompt-builder` 2.2.0, `sdd-governanca` 2.4.1, `sdd-engenharia-reversa-saas` 1.1.1, e do passo 0: `sdd-seguranca` 1.0.1, `sdd-checar-ambiente` 1.5.1, `sdd-release` 2.11.1, `sdd-build` 2.9.1, `sdd-define` 2.6.1, `sdd-brainstorm` 2.3.1; `check-versions.py --base v2.12.1 --base-obrigatoria` VERDE, 21 skills |

**Seleção de modo:** default (um autor; o gerador, os dados e os testes são acoplados).

**Revisão do DESIGN:** em contexto novo, 12 notas (5 HIGH), todas tratadas no Advisor Ledger do DESIGN v1.1 (Decisions 10 e 11; Decision 8 superada).

**Passo 0:** cenário `incidente-chave` executado (2 séries × 3, critério escrito antes; 2 de 3 e, com o roteiro consertado, 3 de 3); os 8 pequenos de 0b e 0c que o Roberto aprovou, cada um com teste vermelho na base.

**Comparação skill a skill (antes da 1ª geração):** 2 agentes em contexto novo, `evidence/F17_STARTER_GERADO/COMPARACAO-terreno.md` e `COMPARACAO-fases-e-apoio.md`; o que o starter tinha melhor nas skills geradas veio para o Open antes.

---

## Landmines lidas no build

| Fonte | Superfície | Veredito |
|---|---|---|
| LM-001 | gate de fiação | ✔ tratado: o gerador roda num repositório com tag e numa réplica do starter; casos dos dois lados; 5 sabotagens mortas |
| LM-002 | baseline vermelho | ✔ tratado: todo teste de conserto conferido vermelho numa cópia do commit anterior |
| LM-003 | commit antes de revisar | ✔ tratado: 4 rodadas sobre árvore commitada, `diff_sha256` em cada pasta |
| LM-005 | heurística sobre texto livre | ✔ tratado: trocas exatas e lista fechada de padrões; o par que define a pasta é casado por regex exata |
| LM-006 | script que só roda com `.git` | ✔ tratado: o teste monta o repositório no Sandbox; verde em cópia de `git archive` com o Python 3.9.6 |
| LM-008 | saldo da OpenRouter | ✔ tratado: `/credits` antes de cada rodada (US$ 15,02, 14,83, 14,79, 14,78) |
| LM-009 | sabotagem que desfaz conserto | ✔ tratado: mutantes em cópia de `git archive` |
| LM-010 | 2º revisor pago | ✔ tratado: `--no-revisor2` nas 4 rodadas |
| LM-011 | cenário nunca executado | ✔ tratado: o `incidente-chave` rodou e achou um defeito de texto |
| LM-012 | 11 dígitos no pacote | ✔ tratado: sha256 só no `GERADO.txt` do starter, que o publish-check de lá pula |
| LM-013 | edição por corte | ✔ tratado: edições de teste por troca exata, verificadas por contagem de testes |
| LM-014 | `subprocess` sem encoding | ✔ tratado: `Sandbox.roda` e `encoding="utf-8"` |
| LM-017 | fallback silencioso | ✔ tratado: tag, destino, troca, tabela e versão falham alto, nada gravado |
| LM-018 | `PIPESTATUS` no zsh | ✔ tratado: logs por script bash com `rc=$?` (`[exit=N]` em todo log) |

---

## Candidatos ao playbook

<<<CANDIDATO_PLAYBOOK
secao: Reviews / harness
sup: `GENERATED` `gerado` `tag` `version gate` `check-versions`
regra: Um gerador que escreve a tag ou o commit de origem em cada arquivo gerado muda todos os arquivos a cada geração: o version gate do destino pede versão nova em tudo, inclusive no que não mudou de verdade (achado da revisão do DESIGN da F17, antes de existir código). **Do instead:** a tag e o commit vão num manifesto só, na raiz do destino; os arquivos gerados levam só o que muda quando a fonte muda, e o gerador confere, antes de gravar, que o que mudou tem versão maior que a do destino.
evidencia: sdd/features/DESIGN_F17_STARTER_GERADO.md
ficha: —
mordeu_antes: —
>>>

<<<CANDIDATO_PLAYBOOK
secao: Reviews / harness
sup: `aceite` `allowlist` `dispensa` `lint` `mesma linha`
regra: Uma lista de exceções do lint que casa "a linha contém o trecho" e pula para a próxima linha cala qualquer outra citação proibida na mesma linha (na F17, o aceite de `sdd/hooks/` também escondia a 2ª citação da mesma linha). **Do instead:** o lint percorre toda ocorrência de cada padrão na linha, e o aceite cobre só a ocorrência que está dentro do trecho dele; teste com uma citação aceita e outra não aceita na mesma linha.
evidencia: sdd/reviews/LEDGER_REVISAO_F17_STARTER_GERADO.md
ficha: —
mordeu_antes: —
>>>

<<<CANDIDATO_PLAYBOOK
secao: Reviews / harness
sup: `default_branch` `origin/HEAD` `slot` `comparação` `raio de impacto`
regra: Trocar a fonte de um valor que outro código compara com a mesma fonte faz a comparação virar "o slot contra ele mesmo" e a pergunta de divergência nunca dispara: na F17, o checar.sh passou a preferir `project.default_branch`, e a new-session comparava o slot com o "principal" do pré-voo. Os testes de texto passaram; só o raio de impacto achou. **Do instead:** ao mudar de onde vem um valor, procure quem o compara com outra fonte e confira que as duas continuam independentes; teste o caso em que elas divergem.
evidencia: sdd/reports/evidence/F17_STARTER_GERADO/RAIO-DE-IMPACTO.md
ficha: —
mordeu_antes: —
>>>

---

## Files Created

| Arquivo | Para quê |
|---|---|
| `scripts/gerar-starter.py` | o gerador (Decisions 1–5, 10, 11) |
| `scripts/starter/{lista.txt,openai.tsv,lint-aceitos.tsv,blocos/*}` | dados do gerador |
| `scripts/starter/trocas/*.md` (7) e `trocas/_moldes/*.md` (4) | 17 trocas exatas |
| `scripts/starter/raiz/{README.md,.gitattributes,scripts/*,.github/workflows/*}` | infra do starter (semente v1.5.16 + trava) |
| `scripts/starter/raiz/scripts/check-gerado.py` | a trava do starter |
| `tests/test_gerar_starter.py`, `tests/test_f17_textos.py`, `tests/test_f17_passo0.py` | AT-001 a AT-010 e o passo 0 |

---

## Verification Results

| Check | Resultado |
|---|---|
| Verify Gate (`verify-gate.sh --strict sdd/features/DEFINE_F17_STARTER_GERADO.md`) | exit 0 em `d813954`: 2.090 testes, 1 pulado; publish-gate GREEN na cópia de `git archive` (`VERIFY-GATE-d813954.log`; a 1ª execução caiu num teste de tempo sob carga, `VERIFY-GATE-d813954-1a.log` e `DEPLOY-tempo-d813954.log`); antes: `0396642` 2.088, `2be8f36` 2.078 |
| `check-versions.py --base v2.12.1 --base-obrigatoria` | VERDE, 21 skills |
| `skill-lint.py --conversa` nas 21 skills | ok |
| ATs | 10 logs, um por AT, todos `[exit=0]` (`AT-001.log` … `AT-010.log`, em `d813954`) |
| Sabotagens (`SABOTAGEM-4b6a2df.log`) | 5 de 5 mortas: troca aceita 0 vez; trava sem sobra; versão não conferida; lint calado; URL do Open fica |
| Prova real (clone do starter `v1.5.16`, tag de teste) | as 9 checagens do CI do starter verdes: trava, publish-check, check-versions contra v1.5.16, py_compile, `bash -n`, testes de skill, gate.sh da kb, testes da raiz, package (18 zips) |
| Raio de impacto (`RAIO-DE-IMPACTO.md`) | 4 superfícies; 3 quebras em código não modificado, consertadas com teste vermelho antes |
| Cenário `incidente-chave` (passo 0) | `CENARIO-incidente-chave-resultado.md`: 2 de 3, depois 3 de 3 |

---

## Segurança

Itens recusados ou adiados no passo de segurança do Define: nenhum (N.A.: sem login, rota pública, dado de terceiros, upload, banco nem chamada paga).

---

## Issues Encountered

- O `publish-check.sh` do starter barra 11 dígitos seguidos, e um sha256 escrito inteiro os traz com frequência: o `GERADO.txt` reprovaria. O gerador é dono do script, que passou a pular o `GERADO.txt`.
- A cópia crua das 10 skills tinha 73 citações a arquivo do `init`; a maior parte estava nos moldes de `sdd/templates/` que vão para dentro das skills: trocas aplicadas uma vez por molde.
- O `collect_evidence.py` do starter classificava o `.codex/config.toml` sem inventariá-lo: consertado junto com o porte.

---

## Deviations from Design

| Item | Desvio | Motivo |
|---|---|---|
| Decision 8 | superada pela Decision 10 | revisão do DESIGN: deixaria o version gate do próprio Open vermelho |
| Decision 7 | sem `GERADO.txt` na raiz, a trava sai 1, não 0 | os workflows que rodam a trava só existem depois da geração; a ausência é remoção |
| Decision 3 | regras de caminho só em `.md`; nos scripts, `<pasta da skill X>/`; seção `### Fluxo encadeado` sai inteira | revisão do DESIGN (6) e avaliador, ciclo 1 |
| Manifest | `lint-aceitos.tsv` e `.gitattributes` do starter a mais | Decision 11 |

---

## Contrato de aceite (C2) e avaliador de contexto fresco (C1)

**Camadas do manifest:** 1 (o pacote não declara `layers:`)
**Contrato de aceite (passo 1.5 da `sdd-build`):** N.A. (1 camada)

**Veredito do avaliador (C1):** PASS_PENDENTE_RECIBO · ciclos: 2 · achados: 3 no ciclo 1 (NEEDS_WORK: 1 médio — caminho e `sync` do Open na kb gerada, consertado em `ec557ad`; 2 baixos), 4 baixos de letra no ciclo 2 (DEFINE v1.3) · avaliações: `sdd/reviews/AVALIACAO_F17_STARTER_GERADO_20261112-1835.md` (ciclo 1) e `sdd/reviews/AVALIACAO_F17_STARTER_GERADO_20261112-1905.md` (ciclo 2).

 O recibo pendente é o que o DEFINE põe fora do gate: a 1ª geração no clone real, PR, CI e Release do starter, CI do PR nas 3 plataformas, Release do Open e o D6.

---

## Advisor Ledger

Ledger completo: `sdd/reviews/LEDGER_REVISAO_F17_STARTER_GERADO.md` (12 linhas e 1 rodada sem achados, `ledger-revisao-lint.sh` VERDE).

| Rodada | Pasta | Engines | Achados | Decisão |
|---|---|---|---|---|
| 1 (diff inteiro) | `EXTERNAL_REVIEW_20261112-175357` | claude + `openrouter` (qwen) | 1 grave, 2 médios, 2 leves | 4 aplicados, 1 rebatido com evidência |
| 2 (diff inteiro, depois do raio e do ciclo 1) | `EXTERNAL_REVIEW_20261112-183050` | claude + qwen | 2 médios, 3 leves | 3 aplicados, 2 rebatidos com evidência |
| 3 (delta) | `EXTERNAL_REVIEW_20261112-184704` | claude + qwen | 1 médio, 1 leve | 1 aplicado, 1 rebatido com evidência |
| 4 (delta, acima do teto por decisão do Roberto) | `EXTERNAL_REVIEW_20261112-202310` | claude + qwen | nenhum (o conferidor a marcou rasa) | — |
| 5 (diff inteiro, decisão do Roberto) | `EXTERNAL_REVIEW_20261112-204706` | claude + qwen | 1 médio, 3 leves | 1 aplicado, 3 rebatidos (evidência ou escopo) |
| 6 (diff inteiro, decisão do Roberto) | `EXTERNAL_REVIEW_20261112-210000` | claude + qwen | 3 leves | 2 aplicados, 1 rebatido com evidência |
| 7 (diff inteiro, a última por decisão do Roberto) | `EXTERNAL_REVIEW_20261112-211515` | claude + qwen | 2 leves (o auditor subiu para médio) + 1 médio novo do auditor | 3 rebatidos: nenhum ocorre hoje; os que poderiam falham alto (65); viram pendência |

2º revisor dispensado nas 4 rodadas (`--no-revisor2`: codex sem cota; 2º revisor pago evitado pela LM-010) e desempate dispensado (`--no-desempate`).

**Medidor dos revisores (`bash sdd/bin/eval-revisores.sh`, `evidence/F17_STARTER_GERADO/EVAL-REVISORES.log`):**

| Papel | Engine (modelo) | Cobrança | Rodadas | Pago US$ | Nominal US$ | Achados | Aplicados | Com dano | Falsos positivos | AGREE |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| revisor | claude (claude-opus-5-5) | assinatura | 4 | 0.0000 | 4.0020 | 12 | 8 de 12 | 0 de 12 | 4 de 12 | — |
| auditor | openrouter (qwen/qwen3.7-plus via Alibaba) | pay-per-token | 4 | 0.1093 | 0.1093 | 0 | 0 | 0 | 0 | 91.7% (11 de 12) |

---

## Drift detectado

Nenhum: a frente não tem prompt de produção (`LLM Prompts: false`; o `default_prompt` do `openai.yaml` é texto de botão).

---

## Acceptance Test Verification

| ID | Critério (resumo do EARS do DEFINE v1.3) | Resultado | Evidência |
|---|---|---|---|
| AT-001 | gera da tag, sem rede, as 10 skills, README, `.gitattributes`, `GERADO.txt`, `scripts/` e workflows; o resto byte a byte igual | true | `evidence/F17_STARTER_GERADO/AT-001.log` |
| AT-002 | 64 (tag, forma, destino sujo) e 65 (troca, tabela, lint, versão), nada gravado | true | `evidence/F17_STARTER_GERADO/AT-002.log` |
| AT-003 | cada skill: frontmatter depois das trocas, identificação do starter, GENERATED, moldes dentro, `openai.yaml`, bloco final, `GERADO.txt` | true | `evidence/F17_STARTER_GERADO/AT-003.log` |
| AT-004 | lint do `init`: crua reprova, gerada passa; aceites e o par que define a pasta | true | `evidence/F17_STARTER_GERADO/AT-004.log` |
| AT-005 | duas gerações idênticas byte a byte | true | `evidence/F17_STARTER_GERADO/AT-005.log` |
| AT-006 | `check-gerado.py`: mudou, falta, sobra ⇒ 1; ilegível ⇒ 64; nos workflows antes dos testes | true | `evidence/F17_STARTER_GERADO/AT-006.log` |
| AT-007 | publish-check, check-versions e gate.sh do starter verdes; versão que não sobe ⇒ 65 | true | `evidence/F17_STARTER_GERADO/AT-007.log` |
| AT-008 | o Open recebeu new-session C1–C4, prompt-builder sem script, auditoria de vários motores | true | `evidence/F17_STARTER_GERADO/AT-008.log` |
| AT-009 | sem `rdd-audita-`; molde neutro; prova pós-build pelo "Aplicar a migration" | true | `evidence/F17_STARTER_GERADO/AT-009.log` |
| AT-010 | skill-lint, agnóstico, check-versions; doctor avisa skill do starter; o `init` não copia `scripts/` | true | `evidence/F17_STARTER_GERADO/AT-010.log` |

**Verify Gate:** exit 0 em `d813954`: 2.090 testes em 32 min, 1 pulado (`evidence/F17_STARTER_GERADO/VERIFY-GATE-d813954.log`). A 1ª execução nesse commit caiu num teste de tempo da `sdd-deploy-do-sha` (`test_dispatch_com_404_sai_2_e_nao_64`) com a rodada 7 rodando junto; isolado, 3 de 3 verdes em cópia de `git archive` (`DEPLOY-tempo-d813954.log`), e a 2ª execução inteira, com a máquina livre, passou.

---

## Final Status

### Overall: ✅ COMPLETE

- [x] 15 linhas do manifest
- [x] Verify Gate verde, linhas de base vermelhas, 5 sabotagens mortas
- [x] ATs com evidência abrível
- [x] revisão: 3 rodadas no teto e mais 4 por decisão do Roberto (a 4ª só do delta; 5 a 7 sobre o diff inteiro, a 7ª a última); `--conferir` CONFERE em `d813954`, com o 2º revisor dispensado e registrado; ledger verde
- [x] avaliador de contexto novo: PASS_PENDENTE_RECIBO no ciclo 2 (o último do teto)
- [x] Pronto para a `sdd-release`

**Pendências que saem desta frente:**
- **Starter:** a 1ª geração no clone real, PR e Release, com OK próprio do Roberto (fora do gate).
- **D6:** regenerar `~/.claude/skills/sdd-*` pela tag publicada, com OK do Roberto.
- **F17b:** modo web de brainstorm, handoff e governança; destino de define, design, build, release e ux-review-builder; `docs/` e `exemplos/` do starter.
- **Lint e `sdd/hooks` sem barra:** ~15 linhas condicionais da higiene-dado citam `sdd/hooks` sem barra e passam no lint (hoje o texto é condicional e certo; uma instrução nova sem barra não seria pega).
- **Bit de execução do `gate.sh` da kb:** cai para 644 no starter (o modo vem da tag); todo uso é `bash …`.
- **Cenários em outros agentes:** o `incidente-chave` rodou só no Claude.
- **Da revisão (rodadas 5 e 7), sem ocorrência hoje:** CI do starter sem os testes de `tests/` da raiz (a v1.5.16 também não rodava); `collect_evidence.py` sem excluir `node_modules/` (já valia para o `CLAUDE.md`); cópia byte a byte do que nenhuma regra muda (CRLF); `trazer_moldes` lendo o CHANGELOG; caminho de skill irmã nos scripts (os dois últimos falham alto, com 65).

---

## Next Step

**If Complete:** `/sdd-release F17_STARTER_GERADO` — bump minor do pacote (`v2.13.0`: gerador novo e funcionalidade nova em 4 skills)
