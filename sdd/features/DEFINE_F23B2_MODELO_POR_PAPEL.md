# DEFINE: F23B2 Modelo por papel

> Cada papel que roda em contexto fresco (curador, avaliador, revisão do design, cartógrafo, executor do piloto) ganha
> um slot de modelo no `sdd/config.yaml`, e o Open ganha o método para preencher o slot por evidência: um gabarito
> tirado do histórico, séries com repetição contra o modelo atual, teto de gasto com trava automática e a escolha
> do modelo mais barato que bate a meta. Nesta fatia, curador e avaliador são medidos e provados.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | F23B2_MODELO_POR_PAPEL |
| **Date** | 2026-11-16 |
| **Author** | Roberto Dias Duarte (decisões) · define-agent (redação) |
| **Status** | Ready for Design |
| **Clarity Score** | 14/15 |
| **Família** | F23_ECONOMIA_MENSURAVEL, fatia B2 (ficha `sdd/handoffs/HANDOFF_F23_ECONOMIA_MENSURAVEL.md`) |
| **Entrada** | `sdd/features/BRAINSTORM_F23_ECONOMIA_MENSURAVEL.md`, bloco 2 (linha da B2) e perfil de risco; linha de base da B1; `sdd/reports/CUSTO_F23B3_CADEIA_REVISAO.md` |

---

## Problem Statement

Todo papel despachado em contexto fresco roda no modelo da sessão principal, o mais caro. Nos registros locais do
Claude Code das frentes F4 a F24 do Open, o avaliador custou de US$ 2,08 a 8,90 nominais por ciclo (mediana US$ 5,12
em 40 execuções, 2 a 3 ciclos por frente) e o curador de US$ 0,73 a 2,45 (mediana US$ 1,53 em 8 execuções). Ninguém
sabe se um modelo mais barato daria o mesmo veredito ou o mesmo delta, porque não há gabarito, nem slot para trocar o
modelo, nem trava para a medição não virar gasto. Na B3, as sessões custaram US$ 53 nominais contra US$ 12 da revisão: a
economia maior está nos papéis que rodam em sessão.

---

## Target Users

| User | Role | Pain Point |
|------|------|------------|
| Mantenedor do Open (Roberto) | escolhe modelo e cadeia por evidência | todo subagente roda no modelo mais caro; trocar seria palpite, sem gabarito e sem teto para medir |
| Quem usa o Open num projeto | roda as fases com o próprio agente e assinatura | não tem onde dizer "o avaliador roda no modelo X" nem como provar que X basta para o projeto dele |

---

## Goals

| Priority | Goal |
|----------|------|
| **MUST** | O `sdd/config.example.yaml` ganha o mapa `papeis:` com um slot de modelo para cada papel em contexto fresco: `curador`, `avaliador`, `revisao_design` (o avaliador no modo contrato), `cartografo` e `executor` (o executor do piloto). Vazio = o modelo da sessão (o comportamento de hoje). O valor é um texto opaco que o agente interpreta: o pacote não traz nome nem preço de modelo. |
| **MUST** | O despacho em contexto fresco lê o slot do papel: no subagente, passa o modelo quando o agente deixa escolher; na parada de sessão nova (`sdd-fluxo.sh despachar`), diz qual modelo abrir. O modelo efetivo fica registrado junto do resultado do papel, para a conta por papel. |
| **MUST** | O `custo-feature.sh` mostra o custo de cada papel despachado na feature (tokens, nominal, modelo), sem contá-lo duas vezes na fase em que ele rodou. |
| **MUST** | Gabarito tirado do histórico do Open, num formato documentado: o curador pelos deltas aceitos (colheita e playbook de antes como entrada, delta aplicado como esperado); o avaliador pelos vereditos guardados em `sdd/reviews/AVALIACAO_*` (veredito e resultado por AT, confirmados pelo ciclo seguinte ou pela publicação). |
| **MUST** | Medidor que só conta (não chama modelo): pontua cada execução contra o gabarito com regra própria do papel, junta as repetições, calcula o nominal por execução pelos leitores de sessão da B1 e a tabela passada por `--precos`, e aponta o candidato mais barato que bate a meta em todas as repetições de todos os casos. Sem ganho, diz "sem ganho medido" e o slot fica vazio. |
| **MUST** | Executor das séries com teto de gasto e trava automática: roda cada execução em contexto novo, numa cópia isolada do caso, pelo comando de agente que o projeto configura; antes de cada chamada confere o gasto acumulado contra o teto e para sem chamar quando a próxima execução pode passar dele. A série do modelo atual (a referência) roda primeiro. Retoma sem repetir execução já gravada. |
| **SHOULD** | Cartógrafo, revisão do design e executor do piloto usam o mesmo slot e o mesmo despacho desde já; a medição deles espera histórico (o Open tem 0 execuções do cartógrafo). |
| **COULD** | — |

Fora do pacote (escolha local deste repositório): os candidatos medidos, a tabela de preços da medição
(`sdd/reports/evidence/F23_ECONOMIA_MENSURAVEL/linha-de-base/precos/`) e o modelo escolhido para cada papel ficam nos
documentos da frente e na ficha, nunca em arquivo do pacote.

---

## Success Criteria

Prova da fatia, medida nesta frente com o executor das séries, contra a linha de base por papel tirada dos registros
das frentes F4 a F24 (avaliador: mediana US$ 5,12 por execução; curador: US$ 1,53):

- [ ] Gabarito gravado em `sdd/reports/evidence/F23B2_MODELO_POR_PAPEL/gabarito/`: curador com ≥ 4 casos tirados das 8 curadorias guardadas (F14 a F23B3); avaliador com ≥ 3 casos, ao menos 1 `PASS` e 2 `NEEDS_WORK` confirmados pelo ciclo seguinte.
- [ ] Série de referência (o modelo atual da sessão) primeiro, 3 repetições por caso: bate a meta. Se não bater, o gabarito ou a meta está errado e é recalibrado antes de qualquer candidato (LM-011: série antiga primeiro).
- [ ] Meta do curador, em cada repetição de cada caso: contagens `ajudou`/`mordeu` com precisão ≥ 0,9 e recall ≥ 0,9 contra o delta aceito; ≥ 2 de cada 3 `ADD`/`REFINE` aceitos encontrados (o `REFINE` pelo mesmo `LM-nnn`; o `ADD` pela mesma seção e ≥ 1 termo de `sup:` em comum); delta aceito pelo `playbook-curator.sh --aplicar` (exit 0) em 100% das execuções.
- [ ] Meta do avaliador, em cada repetição de cada caso: veredito igual ao do gabarito; resultado por AT igual em ≥ 90% dos ATs; **0 AT que falha no gabarito dado como aprovado** (o erro grave: deixar passar defeito).
- [ ] Até 2 candidatos mais baratos por papel, 3 repetições por caso. Para cada papel, o escolhido tem nominal mediano por execução ≥ 30% abaixo do da referência e bate a meta em todas as repetições; senão, o papel fica registrado como "sem ganho medido", com o slot vazio, e isso não conta como economia.
- [ ] Teto desta frente: pago US$ 0,00 (só assinatura) e nominal da medição até US$ 200,00, os dois fixados no executor das séries; passar de qualquer um é parada para o Roberto.
- [ ] A suíte fica verde no macOS e no job `testes-windows` do CI do PR.

---

## Acceptance Tests

| ID | Padrão | Critério (EARS) | Gate (`kind`) |
|----|--------|-----------------|---------------|
| AT-001 | Optional feature | **Where** `papeis.<papel>` está preenchido no `sdd/config.yaml`, o `sdd-fluxo.sh despachar <papel>` **shall** dizer na parada qual modelo abrir na sessão nova, e o leitor do slot **shall** devolver o mesmo valor ao despacho por subagente; vazio ou ausente, a parada e o despacho **shall continue to** sair como hoje, sem linha de modelo. | test |
| AT-002 | Unwanted | **If** o valor de `papeis.<papel>` tem quebra de linha, espaço, aspas, caractere fora de letras, números, `.`, `_`, `:`, `/` e `-`, começa por algo que não seja letra ou número (um `-` viraria opção do agente), ou tem mais de 80 caracteres, **then** o leitor do slot **shall** sair 64 com a chave e o motivo, sem despachar nem repassar o valor. | test |
| AT-003 | Event-driven | **When** uma feature tem um papel despachado entre a marca de início e a de fim dele, o `custo-feature.sh` **shall** imprimir uma linha por papel (execuções, tokens, nominal, modelo) e manter o total da feature igual à soma das fases mais a revisão, sem somar o papel duas vezes. | test |
| AT-004 | Event-driven | **When** o medidor lê as execuções do curador e o gabarito, ele **shall** pontuar cada execução (precisão e recall das contagens; `ADD`/`REFINE` encontrados; delta aceito pelo `playbook-curator.sh --aplicar`) e marcar a execução como dentro ou fora da meta. | test |
| AT-005 | Event-driven | **When** o medidor lê as execuções do avaliador e o gabarito, ele **shall** comparar o veredito e o resultado por AT e marcar fora da meta toda execução que der como aprovado um AT que falha no gabarito, mesmo com o resto igual. | test |
| AT-006 | Event-driven | **When** o medidor tem as séries de um papel, ele **shall** escolher, entre os candidatos que batem a meta em todas as repetições de todos os casos, o de menor nominal mediano por execução, em aritmética exata; **shall** dizer "referência fora da meta" sem escolher ninguém quando a referência não bate a meta; e "sem ganho medido" quando nenhum candidato bate a meta ou nenhum fica ≥ 30% abaixo da referência. | test |
| AT-007 | Unwanted | **If** o custo de um candidato sai n/d (sem registro de sessão ou sem preço na tabela), **then** o medidor **shall** mostrá-lo como n/d, nunca como zero, e **shall** recusar escolhê-lo como o mais barato. | test |
| AT-008 | Unwanted | **If** a próxima execução pode levar o gasto acumulado da série acima do teto (pago ou nominal), ou o candidato tem cobrança pay-per-token ou desconhecida com teto pago zero, **then** o executor das séries **shall** parar antes de chamar o agente, gravar o motivo e o acumulado, e o medidor **shall** marcar o resultado como parcial, sem escolher vencedor. | test |
| AT-009 | State-driven | **While** a pasta da série já tem execuções gravadas, o executor das séries **shall** retomar só as que faltam e somar ao acumulado o gasto das já gravadas, sem repetir nem recontar nenhuma. | test |
| AT-011 | Unwanted | **If** o agente de uma execução da série grava fora da cópia isolada do caso, ou a cópia tem remoto git configurado, **then** o executor das séries **shall** marcar a execução como inválida (fora da conta e da escolha), parar a série e gravar os caminhos tocados, sem apagar nada fora da cópia. | test |
| AT-010 | Ubiquitous | O pacote **shall** manter a suíte inteira verde, sem nome nem preço de modelo em arquivo do pacote (os exemplos usam marcador), com os arquivos novos no `MANIFEST.txt`, as skills e docs dizendo o slot e o método, e o gerador do starter verde (troca em `scripts/starter/trocas/` para texto que só vale no Open). | test |

Padrões considerados:
- **While:** AT-009 (série interrompida e retomada).
- **If/Then:** AT-002 (valor do slot que sairia como argumento), AT-007 (custo que viraria zero), AT-008 (gasto acima do teto), AT-011 (agente que grava fora da cópia).
- **Where:** AT-001 (slot preenchido ou vazio).

---

## Clarifications

### Session 2026-11-16

- [x] (1-escopo) O BRAINSTORM decidiu medir primeiro o curador e o cartógrafo. O cartógrafo nunca rodou no Open (0 execuções; os 8 mapas que existem estão no repositório privado) e o avaliador é o papel que mais custa (mediana US$ 5,12 por ciclo em 40 execuções). Qual dupla a B2 mede? → **curador + avaliador** (Roberto, 2026-11-16); o cartógrafo fica com o slot e é medido quando houver histórico; integrado em Goals e Success Criteria.
- [x] (1-escopo) [auto] "Revisão do design" é o avaliador no modo contrato (o subagente que hoje revisa o DESIGN em contexto fresco), não a revisão adversarial por engine — porque a revisão adversarial já escolhe engine e modelo pelo registry (`review.revisor1`/`auditor`), e os 5 papéis do BRAINSTORM são os que rodam em sessão · para desfazer: tirar `revisao_design` do mapa e ligar o slot ao `--reviewer` do DESIGN.
- [x] (1-escopo) [auto] "Executor" é o executor do piloto (`executor-drive`, sdd-drive) — porque é o único papel com esse nome despachado em contexto fresco; a sessão principal do build fica com o modelo que a pessoa abriu · para desfazer: acrescentar um slot de fase no Design.
- [x] (7-restrições) [auto] Teto da medição desta frente: pago US$ 0,00 (só claude e codex por assinatura) e nominal US$ 200,00 — porque a estimativa é de ~US$ 40 para o curador (4 casos × 3 repetições × 3 modelos × ~US$ 1,5) e ~US$ 100 para o avaliador (3 × 3 × 3 × ~US$ 5), com folga; chamada paga é caso crítico · para desfazer: mudar os dois números no Success Criteria e no comando da série.
- [x] (6-edge cases) [auto] Sem candidato que bata a meta com ≥ 30% de queda, o resultado é "sem ganho medido" e o slot fica vazio — porque a regra comum da família manda voltar atrás quando o dano sobe, e 30% separa ganho de ruído entre repetições · para desfazer: trocar o limiar no AT-006 e no Success Criteria.
- [x] (2-dados) [auto] O gabarito fica fora do pacote, em `sdd/reports/evidence/F23B2_MODELO_POR_PAPEL/gabarito/` (branch de documentos); o pacote leva só o formato, o medidor e o executor — porque o histórico é do Open e não serve ao projeto do aluno, que monta o próprio · para desfazer: copiar os casos para `sdd/fixtures/`.
- [x] (5-integrações) [auto] O executor das séries chama o agente por um comando que o projeto configura (com o modelo como argumento), não por um agente fixo no script — porque o pacote é vendor-agnóstico e a medição é "rodada pelo projeto" (perfil de risco do BRAINSTORM) · para desfazer: fixar adaptadores por agente no Design.
- [x] (UX) UX review → N.A.: a fatia não tem tela; a saída são linhas do `custo-feature.sh`, do relatório do medidor e a parada do `despachar`, no padrão dos medidores existentes. A `/sdd-ux-review` fica ➖ por esta decisão.

### Session 2026-11-16 (governança)

- [x] (governança) dispensada — o revisor fresco devolveu PADRAO_AUSENTE (tema: custo em US$ das chamadas de modelo, teto de gasto, cobrança por token; AT-006 a AT-010); a fronteira conferiu "só o permitido mudou" e o bloco é válido; o Roberto dispensou com motivo, como na B1, na B3 e na F19 (2026-11-16): medidor do custo de modelo do próprio mantenedor, sem lançamento, saldo, nota nem dado pessoal; a aritmética exata e o "n/d nunca é zero" estão nos AT-006 e AT-007, o teto de gasto no AT-008

### Segurança

- [x] (segurança) S20 Agente com poder demais e sem teto — [auto] aplicado — porque o executor das séries roda um agente que executa comandos (o avaliador roda os testes do caso); o teto de gasto já está no AT-008 e a permissão mínima (só a cópia do caso, sem remoto git) virou o AT-011 · para desfazer: tirar o AT-011 e a linha dele no Verify Gate.
- [x] (segurança) S18 Instrução escondida em conteúdo externo — [auto] recusado: o conteúdo que a série manda ao agente é o histórico do próprio Open, escrito nas sessões do mantenedor e já publicado; os briefs do curador e do avaliador não mudam (LLM Prompts false); e o AT-011 limita o que um agente desviado consegue fazer · para desfazer: aplicar como AT novo de cerca nos briefs (vira LLM Prompts true).
- S07 (limite de uso) não vale: é da stack web, e a stack detectada do pacote é "nenhuma".

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
- AT-001 a AT-009 e AT-011: um módulo novo, `tests/test_f23b2_papeis.py`, com `sdd/config.yaml` de fixture, registros de sessão sintéticos (só números, como os da B1), gabaritos e execuções sintéticas dos dois papéis e um agente falso no comando da série (que grava a chamada e devolve um bloco fixo), sem modelo nem rede.
- AT-010: a suíte inteira, que inclui `test_gerar_starter.py`, `test_conversa.py` (teto de 500 linhas), os testes atuais do `sdd-fluxo.sh` e do `custo-feature.sh`, e a guarda de nome de modelo; o `publish-gate` do `cmd` confere o `MANIFEST.txt`.
- A prova (Success Criteria) roda fora do gate, porque os testes não chamam modelo: séries reais em `sdd/reports/evidence/F23B2_MODELO_POR_PAPEL/`, com o relatório do medidor.

O gate roda de um `git archive HEAD`, como na B1 e na B3. O Windows é provado pelo job `testes-windows` do CI do PR.

---

## Out of Scope

- Medir cartógrafo, revisão do design e executor do piloto (só o slot e o despacho entram).
- Modelo da sessão principal de cada fase (define, design, build, release): é a pessoa que abre a sessão.
- Chamada paga (OpenRouter ou outra pay-per-token) na medição desta frente: teto pago zero.
- Escolha do auditor da revisão adversarial por gabarito (fica com o registry e a B3).
- Divisão por papel nas frentes antigas além da linha de base por execução (o que os registros já separam).
- Grupo A da F23.
- Pendências herdadas: preço do modelo do codex na fonte, versão do prompt no META, aviso de prompt v1 editado, version gate do starter fora do Verify Gate, `--conferir` com `--paths`.

---

## Constraints

| Type | Constraint | Impact |
|------|------------|--------|
| Technical | Vendor-agnóstico: nenhum nome nem preço de modelo no pacote; o slot é texto opaco; preços só por `--precos` | a guarda do AT-010 e os testes usam marcador |
| Technical | bash 3.2 e Python 3.9 stdlib, como o resto de `sdd/bin/`; regex de validação com `\Z` | AT-002 |
| Technical | O medidor só lê arquivos (não chama modelo nem rede); quem chama é o executor das séries, com o teto | AT-004 a AT-008 |
| Technical | Os leitores de sessão da B1 agrupam por `message.id` e separam o cache (LM-036) | o nominal por execução reusa esses leitores |
| Technical | O `custo-feature.sh` só conta janelas de marca sem sobreposição | o papel dentro da fase é decisão do Design (AT-003) |
| Technical | Skills de fase e as que despacham estão na lista do starter: texto que cita `sdd/bin/` sai por troca (LM-035); `wc -l` antes de escrever numa `SKILL.md`, a `sdd-release` está com 500 (LM-038) | o despacho mora de preferência em `contexto-fresco.md` e no `sdd-fluxo.sh`, não em cada skill |
| Technical | Arquivo novo no pacote entra no `MANIFEST.txt` no mesmo commit; publish-gate numa cópia de `git archive` antes do gate (LM-037) | — |
| Process | A F24 (release enxuta) reescreve o curador (`playbook-curator.sh`, `sdd-playbook`) e a `sdd-release`: o build da B2 começa só depois que ela entrar na `main`, e o gabarito do curador usa o formato de delta que valer depois dela | Design lê a F24 já publicada |
| Process | A medição real usa o executor das séries com teto pago zero; acima disso, ou acima do nominal de US$ 200, para e pergunta | Success Criteria |
| Process | A revisão leva os não rastreados para o diff: `.gitignore` local durante a revisão, tirado de `sdd/reports/evidence` antes do `report-lint` | — |
| Process | Suíte verde no Windows; medir lá exige push da branch (PR) | — |

---

## Technical Context

| Aspect | Value | Notes |
|--------|-------|-------|
| **Deployment Location** | `sdd/config.example.yaml`, `sdd/bin/sdd-fluxo.sh` (despachar), leitor do slot em `sdd/bin/`, `sdd/bin/custo-feature.sh`, medidor e executor das séries novos em `sdd/bin/`, `.agents/skills/sdd-build/references/contexto-fresco.md` (a escada de despacho), skills que despacham papéis, `docs/`, `tests/` | o Design fecha os nomes e o manifest |
| **KB Domains** | nenhum | o projeto não tem `sdd/kb/` |
| **IaC Impact** | None | só scripts e texto |
| **LLM Prompts** | false | o executor das séries reusa sem mudar os briefs do curador e do avaliador; nenhum prompt de produção é criado ou editado. Se o Design precisar mudar um brief, vira `true` e o Build o trata como entregável |
| **CONTEXTO de domínio** | nenhum (pulado: sem `sdd/patterns/dominio.md`) | — |
| **Governança** | dispensada — medidor do custo de modelo do próprio mantenedor, sem lançamento, saldo, nota nem dado pessoal; aritmética exata e "n/d nunca é zero" nos AT-006 e AT-007, teto de gasto no AT-008 | Roberto, 2026-11-16 |
| **Segurança** | 1 aplicado (S20) · 1 recusado (S18) · 0 adiados | 2026-11-16 |

---

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|----|------------|------------------|------------|
| A-001 | O agente da sessão consegue rodar um papel com outro modelo sem sessão nova (o subagente do Claude Code aceita o modelo; a CLI do codex aceita `-m`) | o despacho por subagente só repassa a parada de sessão nova com o modelo | [ ] |
| A-002 | Os casos do avaliador se reconstroem: o commit avaliado, o DEFINE e o DESIGN daquela hora existem no histórico do git e na branch de documentos | menos casos, ou casos só dos ciclos mais recentes | [ ] |
| A-003 | O formato do delta do curador depois da F24 continua aceito pelo `playbook-curator.sh --aplicar` | o pontuador do curador lê o formato novo da F24 | [ ] |
| A-004 | Uma execução do avaliador cabe em ~15 min, e as séries cabem numa sessão de trabalho | a medição do avaliador vira trabalho de mais de uma sessão (o AT-009 cobre a retomada) | [ ] |

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---------|-------------|-------|
| Problem | 3 | custo por papel medido nos registros F4–F24 |
| Users | 3 | — |
| Goals | 3 | — |
| Success | 3 | metas numéricas por papel, teto e limiar de ganho |
| Scope | 2 | o custo por papel dentro da fase e o comando do agente da série ficam para o Design |
| **Total** | **14/15** | |

---

## Open Questions

Nenhuma — pronto para o Design, depois da governança e da segurança.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-11-16 | define-agent | 10 ATs; decisão do Roberto (curador + avaliador); 6 decisões [auto] |
| 1.1 | 2026-11-16 | define-agent | Governança dispensada pelo Roberto (PADRAO_AUSENTE, como na B1 e na B3); S20 aplicado [auto] (AT-011); S18 recusado [auto] |
| 1.2 | 2026-11-16 | design-agent | AT-002: o valor começa por letra ou número (R7 da revisão D1 do DESIGN) |

---

## Next Step

**Ready for:** `/sdd-design sdd/features/DEFINE_F23B2_MODELO_POR_PAPEL.md` (sem interface: a UX review não se aplica), depois da governança e da segurança.
