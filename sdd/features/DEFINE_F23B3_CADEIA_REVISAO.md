# DEFINE: F23B3 Cadeia de revisão pelos dados

> O 2º revisor roda só quando a mudança toca superfície de risco, a discordância vai para o desempate que já existe,
> e toda revisão da frente entra na conta do `eval-revisores.sh`, que passa a mostrar as chamadas evitadas e as
> dispensas à mão.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | F23B3_CADEIA_REVISAO |
| **Date** | 2026-11-16 |
| **Author** | Roberto Dias Duarte (decisões) · define-agent (redação) |
| **Status** | Ready for Design |
| **Clarity Score** | 15/15 |
| **Família** | F23_ECONOMIA_MENSURAVEL, fatia B3 (ficha `sdd/handoffs/HANDOFF_F23_ECONOMIA_MENSURAVEL.md`) |
| **Entrada** | `sdd/features/BRAINSTORM_F23_ECONOMIA_MENSURAVEL.md`, bloco 2 e decisão 7; linha de base da B1 |

---

## Problem Statement

A regra escrita do 2º revisor (`adversarial-review.sh`) o aciona por tamanho (8 arquivos, 120 KB ou 2 camadas), e toda
revisão de código da F22 e da F23 (41 a 44 arquivos) o acionou; desde a F16 ele foi dispensado à mão em 11 de 12
frentes, por falta de engine e não por risco, inclusive na F18_F20, de segurança. Com uma engine a mais disponível, a
regra voltaria a chamá-lo em quase toda rodada. Além disso, o `eval-revisores.sh` deixa fora da conta a revisão do
DESIGN e a rodada interrompida (6 de 26 achados da F23 e 20 de 42 da F22 ficam "sem classificar"), e o custo nominal do
codex sai n/d porque o adaptador não grava o modelo.

---

## Target Users

| User | Role | Pain Point |
|------|------|------------|
| Mantenedor do Open (Roberto) | decide a cadeia de revisão | dispensa o 2º revisor e o desempate à mão em toda rodada, sem regra; não vê quanto a regra evita nem o custo do codex |
| Quem usa o Open num projeto | roda a revisão adversarial no build | paga um 2º revisor em diff grande sem risco, e a dispensa exige `--aceitar-sem-revisor2` |

---

## Goals

| Priority | Goal |
|----------|------|
| **MUST** | O 2º revisor é acionado só por superfície de risco: segmento de segurança no caminho, glob de `review.security_globs` ou de `layers.sql`, a mesma lista do `sdd-fluxo.sh review-design`; tamanho, número de arquivos e camadas deixam de acionar. O revisor raso (0 achados em menos de 30 s) continua acionando, com o motivo à parte. |
| **MUST** | Sem superfície de risco, a dispensa é automática e fica registrada com o motivo (no META e no ledger da revisão), junto do gatilho que a regra antiga teria acionado. |
| **MUST** | A discordância revisor × auditor é tratada pelo desempate que já existe (achado HIGH rebatido com evidência ⇒ 3ª engine decide só ele), ligado por padrão; desligá-lo à mão fica registrado. |
| **MUST** | Toda revisão da frente entra na conta do `eval-revisores.sh`: a revisão do DESIGN e a rodada interrompida ou sem resultado ganham linha própria no ledger; o que continuar sem linha segue em "fora da conta", nunca some. |
| **MUST** | O `eval-revisores.sh` mostra as rodadas em que a regra evitou o 2º revisor (com o nominal do revisor dessas rodadas como estimativa do custo evitado) e as dispensas à mão (`--no-revisor2`, `--no-desempate`). |
| **MUST** | O adaptador do codex grava o modelo efetivo; com preço na tabela, o nominal sai calculado, com o cache lido à parte; sem preço, n/d, nunca zero. |
| **MUST** | O dano que escapa (3º número da seção 6 do ESCOPO) tem registro: defeito de frente já publicada, achado depois, ganha uma linha `escapou` no ledger da frente de origem (commit do conserto, teste que falha no código antigo, área de dano pelo `CRITERIO_DANO.md`); escape numa frente em que a regra dispensou o 2º revisor dispara a revisão da regra, caso a caso (volta atrás ou o caminho entra na superfície de risco). |
| **COULD** | — |

Fora do pacote (escolha local deste repositório, decisão do Roberto em 2026-11-16): nas próximas frentes do Open, o
auditor passa a ser a lista "codex, depois o modelo da OpenRouter"; o 2º da lista entra só se o 1º falhar. Registrado
na ficha, sem nome de modelo no pacote.

---

## Success Criteria

Prova da fatia (decisão do Roberto em 2026-11-16, troca da prova do BRAINSTORM), medida nas frentes publicadas depois
da B3:

- [ ] Chamadas do 2º revisor evitadas pela regra: ≥ 1 por frente cujo diff passa de 8 arquivos sem superfície de risco, cada uma com o custo estimado (nominal do revisor da mesma rodada) no `eval-revisores.sh`.
- [ ] Dispensas à mão (`--no-revisor2`, `--no-desempate`): 0 nas frentes seguintes, contadas pelo `eval-revisores.sh`.
- [ ] Achados com dano que escaparam para produção: cada linha `escapou` de uma frente com o 2º revisor dispensado pela regra leva à revisão da regra pelo Roberto, caso a caso (volta atrás ou o caminho entra na superfície de risco); as frentes antigas ficam n/d, sem linha de base (decisão 7 do BRAINSTORM, medida decidida em 2026-11-16).
- [ ] Sobre as revisões guardadas da F23 (`sdd/reports/reviews-medicao/F23_ECONOMIA_MENSURAVEL/`), com o ledger completado no formato novo: "fora da conta" cai de 2 para 0 e "sem classificar" de 6 para 0.
- [ ] O custo nominal do codex sai calculado (com a tabela de preços passada por `--precos`) em vez de n/d: numa fixture de META com modelo e tokens de cache, e na 1ª rodada real desta fatia com o codex auditando. O META da 5ª rodada da F23 foi gravado sem o modelo e continua n/d (corrigido no Design, 2026-11-16: o modelo não se recupera depois).
- [ ] A suíte fica verde no macOS e no job `testes-windows` do CI do PR.

---

## Acceptance Tests

| ID | Padrão | Critério (EARS) | Gate (`kind`) |
|----|--------|-----------------|---------------|
| AT-001 | Event-driven | **When** o diff congelado não toca superfície de risco, o `adversarial-review.sh` **shall** rodar só o revisor e o auditor, sem chamar o 2º revisor, com 8 ou mais arquivos, 120 KB ou 2 camadas, e gravar no META o motivo da dispensa e o gatilho que a regra antiga teria acionado. | test |
| AT-002 | Optional feature | **Where** `review.security_globs` ou `layers.sql` estiverem preenchidos, o `adversarial-review.sh` **shall** acionar o 2º revisor quando um caminho do diff casar um desses globs ou trouxer um segmento de segurança, gravando o caminho e o termo ou glob; vazios, só os segmentos fixos acionam; a lista de termos é a mesma do `sdd-fluxo.sh review-design`, lida pela mesma função. | test |
| AT-003 | Non-regression | O `adversarial-review.sh --conferir` **shall continue to** recusar a revisão com superfície de risco rodada com `--no-revisor2` sem `--aceitar-sem-revisor2 "<motivo>"`, e passa a aceitar sem a flag a revisão sem superfície de risco. | test |
| AT-004 | Event-driven | **When** o auditor rebate com evidência um achado HIGH e há engine disponível fora do revisor e do auditor, o `adversarial-review.sh` **shall** rodar o desempate sem flag nenhuma; com `--no-desempate`, o META **shall** registrar a dispensa à mão. | test |
| AT-005 | Event-driven | **When** o `eval-revisores.sh` lê as revisões de uma frente, ele **shall** imprimir as rodadas em que a regra evitou o 2º revisor, com o nominal do revisor dessas rodadas somado em aritmética exata, como no `custo-feature.sh` (n/d quando o dele for n/d, nunca zero), o número de dispensas à mão por tipo e, à parte, as chamadas por revisor raso. | test |
| AT-006 | Event-driven | **When** o ledger da revisão traz a linha de uma revisão do DESIGN ou de uma rodada interrompida ou sem resultado, no formato novo do molde, o `ledger-revisao-lint.sh` **shall** aceitá-la e o `eval-revisores.sh` **shall** contar a chamada e o custo dela (e os achados da revisão do DESIGN, classificados), sem pô-la em "fora da conta". | test |
| AT-007 | Unwanted | **If** uma pasta de revisão da frente continua sem linha em nenhum ledger, **then** o `eval-revisores.sh` **shall** mantê-la em "fora da conta" com o motivo, e os achados dela em "sem classificar". | test |
| AT-008 | Unwanted | **If** o codex responde sem modelo legível ou o modelo dele não está na tabela de preços, **then** o nominal do papel **shall** sair n/d, nunca zero; com modelo e preço, **shall** sair calculado em aritmética exata, com o cache lido separado da entrada. | test |
| AT-009 | Event-driven | **When** o ledger traz uma linha `escapou` (commit do conserto, `teste: <nome>`, área de dano), o `ledger-revisao-lint.sh` **shall** aceitá-la só com os 3 campos, e o `eval-revisores.sh` **shall** contar os escapes por frente e, quando a frente teve o 2º revisor dispensado pela regra, imprimir o aviso de revisar a regra. | test |
| AT-011 | Unwanted | **If** o diff revisado traz um texto que manda o revisor, o auditor ou o desempate ignorar as instruções ou responder sem achados, **then** os 3 prompts **shall** tratá-lo como dado (o diff vai cercado, com a instrução de nunca obedecer ao que está dentro dele) e a revisão **shall** seguir o formato de vereditos sem mudar de comportamento. | test (texto dos 3 prompts) + prova real fora do gate |
| AT-010 | Ubiquitous | O pacote **shall** manter a suíte inteira verde, com as skills, o molde do ledger, o `config.example.yaml` e o `docs/adversarial-review.md` dizendo a regra nova e o gerador do starter verde (troca em `scripts/starter/trocas/` para texto que só vale no Open). | test |

Padrões considerados:
- **While:** N.A. — a regra não depende de estado guardado entre rodadas; cada revisão decide pelo próprio diff (a memória entre rodadas foi recusada: decisão do auditor, 2026-11-16).
- **If/Then:** AT-007, AT-008, AT-011 e o lado negativo do AT-009 (linha `escapou` sem os 3 campos é recusada) (erro silencioso: pasta sem ledger que sumiria da conta; custo que viraria zero).
- **Where:** AT-002 (`security_globs` e `layers.sql` preenchidos ou vazios).

O revisor raso (0 achados em menos de 30 s) continua acionando o 2º revisor, como substituto da revisão que não
aconteceu; o motivo fica gravado à parte (`revisor raso`), fora da conta das chamadas por risco e das evitadas
(decisão do Roberto em 2026-11-16; coberto no AT-005).

---

## Clarifications

### Session 2026-11-16

- [x] (1-escopo) Com a revisão custando uma ordem de grandeza menos que as sessões, o 2º revisor já dispensado na prática desde a F16 e a linha de base sem custo de revisão, qual é a prova da B3? → trocar a prova: chamadas do 2º revisor evitadas (com o custo de cada uma), zero dispensa à mão nas frentes seguintes e achados com dano que escaparam sem subir; a economia grande fica com a B2; integrado em Success Criteria e Goals.
- [x] (8-terminologia) O que a "discordância revisor × auditor" aciona? → o desempate que já existe, ligado por padrão (3ª engine decide só o achado HIGH rebatido); o 2º revisor do diff inteiro fica só para superfície de risco; integrado em Goals e AT-004.
- [x] (5-integrações) O que a B3 faz com o auditor (qwen passou do teto em 2 de 5 rodadas da F23 e concordou em 56%)? → só trocar a cadeia deste repositório (codex, depois o modelo da OpenRouter; escolha local, fora do pacote) e fechar o n/d do codex; escolha do auditor por evidência vai para a B2; integrado em Goals e AT-008.
- [x] (9-sinal de conclusão) Como se mede o dano que escapou para produção, se nenhum registro o conta? → linha `escapou` no ledger da frente de origem, com o critério de dano que já existe; escape em frente com o 2º revisor dispensado pela regra dispara a revisão da regra caso a caso; sem linha de base (frentes antigas n/d); integrado em Goals, Success Criteria e AT-009.
- [x] (6-edge cases) O revisor raso (0 achados em menos de 30 s) continua acionando o 2º revisor? → continua, como substituto da revisão que não aconteceu (0 casos em 21 rodadas guardadas da F22 e da F23), com o motivo gravado à parte, fora da conta da regra; integrado em Goals, AT-005 e no texto abaixo dos ATs.
- [x] (7-restrições) A lista de termos de segurança fica só com os termos do `review-design`? → ampliada com termos em português e gerais (autenticação, autorização, segurança, security, secret/segredo, credencial, permissão, cripto), mantendo `token` (decisão do Roberto na revisão D1 do DESIGN, 2026-11-16); vale para o 2º revisor e para o `review-design`; integrado no AT-002 pelo DESIGN (Decision 2).
- [x] (UX) UX review → N.A.: a fatia não tem tela; a saída são linhas do META, do ledger e do relatório do `eval-revisores.sh`, no padrão dos medidores existentes. A `/sdd-ux-review` fica ➖ por esta decisão.

### Session 2026-11-16 (governança)

- [x] (governança) dispensada — o revisor fresco devolveu PADRAO_AUSENTE (tema: custo e preço de modelo, AT-005 e AT-008); a 1ª conferência da fronteira acusou `sdd/traces/F23B3_CADEIA_REVISAO.jsonl`, escrito pelo `verify-gate.sh` desta sessão no segundo do snapshot, não pelo revisor; o Roberto dispensou com motivo, como na B1 e na F19 (2026-11-16); a aritmética exata entrou nos AT-005 e AT-008, e o "n/d nunca é zero" está no AT-008

### Segurança

- [x] (segurança) S18 Instrução escondida em conteúdo externo — aplicado (Roberto, 2026-11-16): com um revisor só na maioria das rodadas, um diff que manda calar o revisor não teria 2ª opinião; virou o AT-011.
- [x] (segurança) S20 Agente com poder demais e sem teto — recusado (Roberto, 2026-11-16): "o teto de tempo basta"; as engines rodam só com leitura, o desempate roda no máximo 1 vez por rodada sobre 1 achado, e o custo de cada chamada fica no META.

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

Cobertura:
- AT-001 a AT-009: um módulo novo, `tests/test_f23b3_revisao.py`, com engines falsas (como os testes atuais do `adversarial-review.sh`), diffs sintéticos com e sem superfície de risco, ledgers no formato novo e um META do codex com e sem modelo.
- AT-011: teste de texto sobre os 3 prompts de `sdd/review/prompts/` (cerca do diff e a instrução de não obedecer, com mutante que tira a frase); a prova de comportamento fica fora do gate, porque os testes não chamam engine: 3 rodadas reais com um diff que traz a frase, critério de aprovado escrito antes (LM-011), julgadas por um leitor em contexto novo (LM-028), em `sdd/reports/evidence/F23B3_CADEIA_REVISAO/`.
- AT-010: a suíte inteira, que inclui `test_gerar_starter.py`, `test_eval_revisores.py` e os testes atuais do `adversarial-review.sh` e do `sdd-fluxo.sh`.

O gate roda de um `git archive HEAD`, como na B1. O Windows é provado pelo job `testes-windows` do CI do PR.

---

## Out of Scope

- B2 (modelo por papel, inclusive a escolha do auditor por gabarito) e Grupo A.
- A regra da revisão do DESIGN (`sdd-fluxo.sh review-design`: EXIGIDO com 3 ou mais arquivos novos) continua como está; só a lista de termos de segurança passa a ser compartilhada.
- Regra no pacote que tira da rodada seguinte a engine que estourou o tempo (recusada pelo Roberto em 2026-11-16; a lista de engines por papel já troca na mesma rodada).
- Recuperar o custo da revisão das frentes antigas: os META sumiram com as worktrees e ficam n/d.
- Sobras de fora da F23: o version gate contra a versão real do starter fora do Verify Gate e o `--conferir` sem aceitar revisão com `--paths`.

---

## Constraints

| Type | Constraint | Impact |
|------|------------|--------|
| Technical | Vendor-agnóstico: nenhum nome nem preço de modelo no pacote; preços para medir ficam em `sdd/reports/evidence/F23_ECONOMIA_MENSURAVEL/linha-de-base/precos/` (`--precos`) | o teste do AT-008 usa tabela de fixture |
| Technical | bash 3.2 e Python 3.9 stdlib, como o resto de `sdd/bin/`; regex de validação com `\Z` | — |
| Technical | Dois scripts que leem a mesma lista usam a mesma função, com teste que compara (LM-005) | a lista de segurança sai de um lugar só para `adversarial-review.sh` e `sdd-fluxo.sh` |
| Technical | O `token_count` do codex traz o cache lido dentro da entrada (LM-036) | o nominal do AT-008 separa o cache |
| Technical | Skills de fase estão na lista do starter: texto que cita `sdd/bin/` sai por troca (LM-035); rodar `test_gerar_starter.py` antes do gate | — |
| Technical | Os testes não chamam engine de verdade nem rede | engines falsas no PATH |
| Process | A revisão leva os não rastreados para o diff: `.gitignore` local durante a revisão, tirado de `sdd/reports/evidence` antes do `report-lint` | — |
| Process | Suíte verde no Windows; medir lá exige push da branch (PR) | — |

---

## Technical Context

| Aspect | Value | Notes |
|--------|-------|-------|
| **Deployment Location** | `sdd/bin/adversarial-review.sh`, `sdd/bin/eval-revisores.sh`, `sdd/bin/ledger-revisao-lint.sh`, `sdd/bin/adapters/codex.sh`, `sdd/bin/sdd-fluxo.sh`, `sdd/review/prompts/` (revisor, auditor, desempate), `sdd/templates/LEDGER_REVISAO_TEMPLATE.md`, `sdd/config.example.yaml`, `docs/adversarial-review.md`, skills `sdd-build`, `sdd-release` e `sdd-design`, `tests/` | onde a cadeia de revisão já mora |
| **KB Domains** | nenhum | o projeto não tem `sdd/kb/` |
| **IaC Impact** | None | só scripts e texto |
| **LLM Prompts** | true | o S18 aplicado edita os 3 prompts de produção da revisão (`sdd/review/prompts/` do revisor, do auditor e do desempate): o Design inventaria os 3 e o Build trata cada um como entregável |
| **CONTEXTO de domínio** | nenhum (pulado: sem `sdd/patterns/dominio.md`) | — |
| **Governança** | dispensada — medidor só de leitura do custo de revisão, sem lançamento, saldo, nota nem dado pessoal; aritmética exata e "n/d nunca é zero" aplicados nos AT-005 e AT-008 | Roberto, 2026-11-16 |
| **Segurança** | 1 aplicado (S18) · 1 recusado (S20) · 0 adiados | 2026-11-16 |

---

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|----|------------|------------------|------------|
| A-001 | O registro do codex traz o modelo efetivo legível (no evento de sessão ou na saída `--json`) | o AT-008 só cobre o n/d; o nominal do codex continua n/d até o adaptador ter outra fonte | [ ] |
| A-002 | Os testes atuais do `adversarial-review.sh` que dependem do gatilho por tamanho são poucos e trocáveis | mais testes a reescrever no build | [ ] |

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---------|-------------|-------|
| Problem | 3 | números das frentes F16 a F23 e da F23 |
| Users | 3 | — |
| Goals | 3 | — |
| Success | 3 | — |
| Scope | 3 | — |
| **Total** | **15/15** | |

---

## Open Questions

Nenhuma — pronto para o Design, depois da governança e da segurança.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1 | 2026-11-16 | define-agent | Rascunho com 3 decisões do Roberto e 2 dúvidas abertas |
| 1.0 | 2026-11-16 | define-agent | 5 decisões do Roberto integradas; 10 ATs; zero marcador de dúvida |
| 1.1 | 2026-11-16 | define-agent | Governança dispensada pelo Roberto; S18 aplicado (AT-011, LLM Prompts true); S20 recusado |
| 1.2 | 2026-11-16 | design-agent | Critério do codex: a 5ª rodada da F23 não tem o modelo no META; a prova vai para fixture e 1ª rodada real (Decision 7 do DESIGN) |

---

## Next Step

**Ready for:** `/sdd-design sdd/features/DEFINE_F23B3_CADEIA_REVISAO.md` (sem interface: a UX review não se aplica), depois das 2 dúvidas, da governança e da segurança.
