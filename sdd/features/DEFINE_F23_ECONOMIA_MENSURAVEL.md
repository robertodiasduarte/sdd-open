# DEFINE: F23 Economia mensurável — fatia B1 (custo por fase e por feature)

> O Open passa a registrar quanto cada fase e cada feature custou (tokens, pago, nominal, tempo ativo), a partir do registro local de cada agente, e produz a linha de base das features anteriores.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | F23_ECONOMIA_MENSURAVEL |
| **Date** | 2026-11-15 |
| **Author** | define-agent (sessão do Roberto) |
| **Status** | Ready for Design |
| **Clarity Score** | 14/15 |

---

## Problem Statement

O Open só registra o custo da revisão adversarial (`sdd/bin/eval-revisores.sh`); as sessões de brainstorm, define, ux-review, design, build e release não deixam nenhum registro de custo, então o mantenedor não consegue demonstrar economia do próprio processo nem comparar uma feature com as anteriores (seção 6 do ESCOPO).

---

## Target Users

| User | Role | Pain Point |
|------|------|------------|
| Mantenedor do Open | decide cadeia de revisão e modelo por papel (fatias B3 e B2) | decide por impressão: não sabe quanto cada fase custa nem se uma mudança economizou |
| Quem usa o Open num projeto | roda as fases com o agente que tiver | não vê o custo nominal da feature que construiu, nem por fase; com assinatura, o "pago" é zero e esconde o consumo |

---

## Goals

| Priority | Goal |
|----------|------|
| **MUST** | Marca de início e fim por fase, gravada pelas skills de fase |
| **MUST** | Adaptadores de sessão (Claude Code e Codex) que devolvem só números |
| **MUST** | Contador que soma por fase e por feature, com o custo da revisão sem contar em dobro, e grava o relatório ao lado do BUILD_REPORT |
| **MUST** | n/d nunca entra como zero; preço de cache separado do de entrada |
| **MUST** | Modo de linha de base: uma linha por feature anterior |
| **SHOULD** | Rodadas do Verify Gate até o verde, lidas do trace que o `verify-gate.sh` já grava |
| **COULD** | — |

---

## Success Criteria

- [ ] Uma fixture de sessão com 3 fases e 1 trecho sem fase sai com os números conferidos à mão: 0 de diferença em tokens; nominal com diferença ≤ US$ 0,0001 por linha.
- [ ] Uma fixture com texto de conversa, caminho de arquivo e um segredo fictício: 0 ocorrências desses textos na saída dos adaptadores e no relatório.
- [ ] A linha de base cobre as frentes F4 a F22 que têm registro local (≥ 15 linhas), cada uma com custo nominal ou n/d, rodadas de revisão e achados com dano.
- [ ] A suíte inteira passa no macOS e no Windows (job `testes-windows` do CI), com 0 falha.

---

## Acceptance Tests

| ID | Padrão | Critério (EARS) | Gate (`kind`) |
|----|--------|-----------------|---------------|
| AT-001 | Event-driven | **When** uma skill de fase chama `sdd/bin/marca-fase.sh inicio <fase> <FEATURE>` e depois `… fim <fase> <FEATURE>`, the system **shall** acrescentar uma linha por chamada (evento, fase, feature, horário UTC em ISO 8601) ao arquivo de marcas da feature, sem apagar as linhas anteriores; **If** a fase ou a feature trouxer tabulação, quebra de linha ou outro caractere de controle, **then** o script **shall** recusar com exit 64 sem gravar nada | test |
| AT-002 | Ubiquitous | The leitores de sessão `sdd/bin/adapters/sessao-claude.py` e `sessao-codex.py` **shall** devolver, por mensagem do agente (sessão principal e subagentes), só horário, modelo e tokens de entrada, saída, cache criado e cache lido — nenhum texto de conversa, caminho de arquivo ou argumento de ferramenta (fixture com texto, caminho e segredo fictício: 0 ocorrências na saída); um nome de modelo fora de `[A-Za-z0-9._:/@-]{1,80}` (com `|`, quebra de linha ou controle) **shall** sair como `?`, para não forjar linha no relatório | test |
| AT-003 | Event-driven | **When** `sdd/bin/custo-feature.sh <FEATURE>` roda sobre marcas e sessões, the system **shall** gravar `sdd/reports/CUSTO_<FEATURE>.md` com uma linha por fase (execuções, tokens, pago, nominal, tempo ativo), uma linha `sem fase` para o trecho fora de qualquer par de marcas, uma linha `revisão` e o total, batendo com a conta à mão da fixture; as somas **shall** ser exatas (decimal, nunca ponto flutuante) e arredondadas só na hora de imprimir | test |
| AT-004 | Unwanted | **If** o registro de uma sessão não é legível (arquivo ausente, linha JSON quebrada, agente sem adaptador) ou o modelo não tem preço, **then** the system **shall** mostrar `n/d` naquela célula, somar o total como `US$ x + n/d` e nunca contar o valor como 0 | test (negativo) |
| AT-005 | Ubiquitous | The contador **shall** precificar tokens de cache lido e cache criado pelo preço de cache do modelo, separado do preço de entrada; **If** o modelo não tem preço de cache, **then** a parte de cache **shall** sair `n/d` em vez de cobrada como entrada | test |
| AT-006 | Unwanted | **If** uma chamada da revisão adversarial também deixar sessão no registro local, **then** the system **shall** contar o custo dessa chamada uma vez só (pela linha `revisão`, lida dos META.txt) | test (negativo) |
| AT-007 | State-driven | **While** uma sessão cobre várias fases, the system **shall** atribuir cada mensagem à fase cujo par início/fim contém o horário dela, e uma fase aberta sem `fim` **shall** fechar no horário da marca seguinte ou no fim da sessão, com o aviso `fase sem fim` | test |
| AT-008 | Event-driven | **When** `custo-feature.sh --linha-de-base <mapa>` roda com um mapa feature → pastas de sessão e ledgers, the system **shall** imprimir uma linha por feature com custo nominal (ou n/d), rodadas de revisão e achados com dano, sem dividir por fase | test |
| AT-009 | Ubiquitous | The skills de fase (`sdd-brainstorm`, `sdd-define`, `sdd-ux-review`, `sdd-design`, `sdd-build`, `sdd-release`) **shall** mandar chamar `marca-fase.sh` no início e no fim, e o starter gerado **shall** sair por `scripts/gerar-starter.py` sem edição à mão | test |
| AT-010 | Non-regression | The system **shall continue to** aceitar o `precos.tsv` de 6 colunas e o formato atual dos META.txt e ledgers: `eval-revisores.sh`, `adversarial-review.sh`, `adversarial-review-gate.sh` e toda a suíte passam como hoje, no macOS e no Windows | test |

Padrões considerados:
- **While:** AT-007 (sessão que cobre várias fases).
- **If/Then:** AT-004, AT-005 e AT-006.
- **Where:** a chave que já existe, `SDD_TRACE=off` (a mesma do `verify-gate.sh`), desliga também as marcas. O AT-001 é testado ligado e desligado; sem marca, nada é atribuído a fase.

---

## Clarifications

### Session 2026-11-15

- [x] (sinal de conclusão) "Rodadas até o Verify Gate ficar verde" (ESCOPO §6) não existe registrado nas frentes F4 a F22: nenhuma worktree tem `sdd/traces/`, e os BUILD_REPORTs dizem isso em prosa. → Na linha de base, o 2º número é **rodadas de revisão** (contadas nos ledgers). Da F23 em diante, o contador lê também as voltas do Verify Gate em `sdd/traces/<F>.jsonl`, que o `verify-gate.sh` já grava (SHOULD). Decisão do agente, registrada para o Roberto reverter; integrado em AT-008 e Goals.
- [x] (dados) Onde mora o relatório? → `sdd/reports/CUSTO_<FEATURE>.md`, ao lado do BUILD_REPORT, e não dentro dele: assim o `report-lint.py` e o molde do BUILD_REPORT não mudam. Integrado em AT-003.
- [x] (escopo) Quais skills são "de fase"? → As seis da linha de produção: brainstorm, define, ux-review, design, build e release. Avaliador, cartógrafo e curador rodam dentro delas, e a divisão por papel fica para a B2. Integrado em AT-009.
- [x] (dados) "Tempo ativo" → soma, por turno, do intervalo entre a mensagem que dispara o turno e o último registro do agente naquele turno. A espera humana fica fora (YAGNI do BRAINSTORM). Integrado em AT-003.
- [x] (integrações) Conta em dobro da revisão → as chamadas da revisão rodam com `--no-session-persistence` (claude) e com a pasta de trabalho numa pasta temporária vazia (`adversarial-review.sh:593`). O adaptador de sessão só lê sessões cuja pasta de trabalho é a do projeto. AT-006 prova isso com uma fixture.
- [x] (restrições) Preços de modelo → o pacote do Open não ganha linha nova de modelo na `precos.tsv` (vendor-agnóstico). Os testes usam fixtures, e cada projeto preenche os próprios preços com fonte e data.

- [x] (UX) UX review → N.A.: a fatia não tem tela. A saída é um relatório em Markdown no padrão de saída dos outros medidores (`eval-revisores.sh`), já revisado na F10. A `/sdd-ux-review` fica ➖ por esta decisão.

### Session 2026-11-15 (governança)

- [x] (governança) dispensada — o revisor fresco devolveu PADRAO_AUSENTE (tema: preço e custo em US$); o Roberto dispensou com motivo, como na F19 (2026-11-15); o item que vale (aritmética exata) foi aplicado no AT-003, e o "n/d nunca é zero" está no AT-004

### Segurança

- Gatilho: `dado-de-terceiros` (o registro de sessão lido contém a conversa inteira, com possível dado de cliente e segredo). Stack detectada: nenhuma (só itens `stack: todas`).
- S10 (segredo guardado errado): já atendido pelo AT-002 (só números, horários e modelo saem; segredo fictício da fixture com 0 ocorrências).
- S17 (log que aceita linha forjada): **aplicado** no AT-001 (marca com caractere de controle é recusada) e no AT-002 (nome de modelo fora do padrão sai `?`). Decidido pela opção recomendada, sob o pedido do Roberto de executar o pipeline até a release; reversível na revisão do DESIGN.

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
- AT-001 a AT-008: um módulo novo, `tests/test_f23_custo.py`, com fixtures em `sdd/fixtures/custo/`. São sessões sintéticas do Claude Code e do Codex, com subagente, cache, uma linha quebrada, texto e segredo fictício, mais um META.txt e um ledger.
- AT-009: teste de texto sobre `.agents/skills/` e `test_gerar_starter.py`.
- AT-010: a suíte inteira, que inclui `test_eval_revisores.py`.

O gate roda de um `git archive HEAD`, como na F22. O Windows é provado pelo job `testes-windows` do CI do PR.

---

## Out of Scope

- Fatias B3, B2 e Grupo A (cada uma com Define próprio).
- Adaptadores de outros agentes além do Claude Code e do Codex (ficam n/d).
- Divisão por fase nas frentes F4 a F22 (a linha de base é por feature).
- Tempo de espera humana, cota de assinatura, painel ou gráfico, alerta de orçamento durante a sessão.
- Linhas de preço de modelo no pacote.
- As sobras `--conferir` com `--paths` e version gate do starter.

---

## Constraints

| Type | Constraint | Impact |
|------|------------|--------|
| Technical | bash 3.2 e Python 3.9 stdlib, como o resto de `sdd/bin/`; Windows (Git Bash + Python nativo) | o núcleo dos scripts é Python embutido, com saída UTF-8 e `\n` |
| Technical | Vendor-agnóstico: método, nunca nome nem preço de modelo | só fixtures de teste citam modelo; o pacote não ganha preço |
| Technical | Nada é corrigido direto no starter | as skills mudam no Open e o starter é gerado |
| Technical | `MANIFEST.txt` a cada arquivo novo do pacote | o publish-gate reprova arquivo fora do manifesto |
| Technical | O contador não chama modelo nem rede; só lê arquivos | testes sem rede |
| Process | Os artefatos SDD (BRAINSTORM, DEFINE, DESIGN, relatórios) vivem na branch `docs/incorporar-starter`, nunca na `main` | ficam fora do commit desta branch |

---

## Technical Context

| Aspect | Value | Notes |
|--------|-------|-------|
| **Deployment Location** | `sdd/bin/` (`marca-fase.sh`, `custo-feature.sh`), `sdd/bin/adapters/` (`sessao-claude.py`, `sessao-codex.py`), `sdd/review/precos-cache.tsv` (preço de cache), `.agents/skills/sdd-{brainstorm,define,ux-review,design,build,release}/SKILL.md`, `sdd/fixtures/custo/`, `tests/test_f23_custo.py`, `MANIFEST.txt`, `docs/` (a página do medidor), dados do gerador do starter se preciso | `scripts/` é do mantenedor |
| **KB Domains** | nenhum | o Open não tem `sdd/kb/` |
| **IaC Impact** | None | — |
| **LLM Prompts** | false | nenhum prompt de produção; os scripts leem registros e contam, e as skills são instruções de agente, não runtime |
| **CONTEXTO de domínio** | nenhum (pulado: o Open não tem `sdd/patterns/dominio.md`) | `contexto-lint.sh --sugerir` → PULAR |
| **Governança** | dispensada — medidor só de leitura do custo de ferramenta, sem lançamento, saldo, nota nem dado pessoal; aritmética exata e "n/d nunca é zero" aplicados nos AT-003 e AT-004 | Roberto, 2026-11-15 |
| **Segurança** | 1 aplicado (S17) · 0 recusados · 0 adiados; S10 já atendido pelo AT-002 | 2026-11-15 |

---

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|----|------------|------------------|------------|
| A-001 | O registro do Claude Code traz `timestamp`, `message.model` e `message.usage` (entrada, saída, cache criado, cache lido) por mensagem, e os subagentes ficam em `<sessão>/subagents/*.jsonl` | o adaptador precisa de outro campo | [x] conferido nesta máquina em 2026-11-15 |
| A-002 | O registro do Codex traz `session_meta.cwd` e eventos `token_count` com o total acumulado | o adaptador soma diferenças em vez de valores | [x] conferido em 2026-11-15 |
| A-003 | A pasta de sessões do Claude Code é o caminho da worktree com todo caractere fora de A-Z, a-z e 0-9 trocado por `-` | o leitor recebe a pasta por `--dir` | [x] conferido nas pastas reais (`_`, `~`, `.` e acento viram `-`) |
| A-004 | Chamadas da revisão não deixam sessão com a pasta de trabalho do projeto | conta em dobro | [ ] o AT-006 prova com fixture; o Design confere o caminho real |

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---------|-------------|-------|
| Problem | 3 | dor e lacuna concretas |
| Users | 3 | dois perfis com a dor |
| Goals | 3 | MUST e SHOULD explícitos |
| Success | 3 | números e fixtures |
| Scope | 2 | o 2º número da linha de base mudou para rodadas de revisão (decisão registrada) |
| **Total** | **14/15** | |

---

## Open Questions

None - ready for Design. A decisão sobre o 2º número da linha de base está em Clarifications, para o Roberto reverter se quiser.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-11-15 | define-agent | Initial version (fatia B1) |
| 1.1 | 2026-11-15 | design-agent | Leitores de sessão em Python (`sessao-*.py`, Decision 2 do DESIGN); as marcas vão no trace do `verify-gate.sh` e respeitam `SDD_TRACE=off` (Decision 1) |

---

## Next Step

**Ready for:** `/sdd-design sdd/features/DEFINE_F23_ECONOMIA_MENSURAVEL.md` (sem interface: UX review pulada, ver Clarifications)
