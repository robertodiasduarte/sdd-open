# BRAINSTORM: F13 UX e LLM no código

> Exploratory session to clarify intent and approach before requirements capture

## Metadata

| Attribute | Value |
|---|---|
| Feature | F13_UX_LLM |
| Date | 2026-11-04 |
| Author | brainstorm-agent |
| Status | Handoff Ready |

## Initial Idea

**Raw Input:** "Continuar: INCORPORAR_STARTER — sessão 10: F13 UX e LLM no código." Escopo do prompt: U1 (7 critérios WCAG 2.2 AA com PASSA/REPROVA/N.A. no `UX_REVIEW_TEMPLATE.md` e na `sdd-ux-review`), U2 (`sdd/bin/contraste.sh`), U3 (smoke visual antes × depois, decidir se entra), L1 (skill nova `sdd-loop-builder`, LOOP_SPEC v2), L2 (roteador loop × prompt na `sdd-build`), L3 (fragmento `LLM_PROMPTS_DESIGN.md` + colunas no `DESIGN_TEMPLATE.md`), L4 (`sdd/bin/prompt-drift-scan.sh`). Decidir D11 (slots), a U3 e a versão da Release.

**Context Gathered:**
- **Fornecido:** a F13 segue o parâmetro P4 do plano (acabar com o SDD privado e substituí-lo pelo Open); sessão 10, do brainstorm à release; a F14 é a sessão 11.
- **Observado no Open (`6b7633c` = `v2.4.0`):** 17 skills; 992 testes; `.agents/skills/sdd-build/SKILL.md` não tem passo 5.5: o drift e a chamada à `sdd-prompt-builder` estão no passo 4, itens 1 e 2; o 5.5 é da `sdd-design`. `sdd-prompt-builder/references/sdd-integration.md` já descreve a coluna `Tipo` e o contrato por prompt, e `DESIGN_TEMPLATE.md` não tem seção `LLM Prompts`; `LLM_PROMPTS_BUILD_REPORT.md` já tem a coluna Tipo. `prompts.builder_skill` só é lido por texto de skill.
- **Observado no privado (`origin/main`, só leitura):** `scripts/contraste.sh` (55 linhas), `scripts/gates/prompt-drift-scan.sh` (231), `.claude/skills/loop-builder/SKILL.md` (323), `.claude/sdd/templates/fragments/LLM_PROMPTS_DESIGN.md`, Step 4.5 de `.claude/commands/workflow/ux-review.md`, passo 4 de `workflow/build.md`, step LLM de `workflow/design.md`.
- **Observado (U3):** o plano, na 8.3, não lista fonte para a U3. No privado, o smoke visual são cerca de 1.470 linhas de `.mjs` em `scripts/a11y/`, com `playwright` e `@axe-core/playwright`, ligadas ao WordPress, à Hostinger e à Cloudflare, e chamadas nos passos 6b, 7b e 10b do `.claude/commands/release.md`.
- **Observado (LOOP_SPEC real):** há especificações preenchidas no privado (34, 210 e 268 linhas). O `EVAL_FP_LOOP_VS_ONESHOT_2026-07-14.md` mediu kappa 1,0 contra 0,45, e o próprio relatório avisa que a base é frágil (16 casos, 1 reprovado).
- **Calculado:** `#767676` sobre branco = 4,5422 (trunca em 4.54); `#777777` sobre branco = 4,4781 (trunca em **4.47**, arredonda em 4.48). O plano pedia truncar e, ao mesmo tempo, 4.48.
- **Inferência (não confirmada em uso):** o agente seguirá o roteador escrito na `sdd-build`; a prova em agente real desta frente é o que testa isso.

**Technical Context Observed (for Define):**

| Aspect | Observation | Implication |
|---|---|---|
| Likely Location | `sdd/bin/contraste.sh`, `sdd/bin/prompt-drift-scan.sh`, `.agents/skills/sdd-loop-builder/`, `.agents/skills/sdd-build/SKILL.md` (passo 4), `.agents/skills/sdd-design/SKILL.md` (5.5), `.agents/skills/sdd-ux-review/SKILL.md`, `.agents/skills/sdd-prompt-builder/references/sdd-integration.md`, `sdd/templates/UX_REVIEW_TEMPLATE.md`, `sdd/templates/DESIGN_TEMPLATE.md`, `sdd/templates/fragments/LLM_PROMPTS_DESIGN.md` (novo), `sdd/bin/design-lint.py`, `sdd/config.example.yaml`, `docs/` + `docs/pt-BR/` | Toda skill tocada sobe de versão; skill nova muda as contagens de `test_skill_lint.py`, `test_conversa.py` e possivelmente `test_decisoes_lint.py` |
| Relevant KB Domains | N/A no pacote; sem dinheiro, tributo ou dado pessoal à vista | A governança deve responder N.A., com revisor fresco, senão o gate sai 5 |
| IaC Patterns | N/A; a Release automática lê `release.yml` | `v2.5.0` por tag manual, push atômico com `main` |

## Discovery Questions & Answers

| # | Question | Answer | Impact |
|---|---|---|---|
| 1 | A U3 (smoke visual, só projeto web) entra na F13? | **Não, fica fora** e os slots `smoke.*` caem | A frente perde o passo no `sdd-release`; a F15 precisa de um ponto de extensão para o privado continuar chamando `scripts/a11y/` |
| 2 | Quais slots `prompts.*` a F13 cria (D11)? | **Só `prompts.wrapper_pattern`** | O scan lê esse slot; a `sdd-build` chama a `sdd-loop-builder` pelo nome; `prompts.loop_builder_skill` não existe |
| 3 | Qual versão a Release publica? | **`v2.5.0`, com tag manual** | Push atômico de `main` + tag; `check-versions` e nota da Release com essa tag |
| 4 | Qual resultado para `#777777` sobre branco? | **4.47, truncado** | O critério do plano foi corrigido; o teste exige `4.47:1 REPROVA` |

## Sample Data Inventory

| Type | Location | Count | Notes |
|---|---|---:|---|
| Input files | privado, `scripts/contraste.sh`; `scripts/gates/prompt-drift-scan.sh` | 2 | Só leitura; o self-test de cada um dá os valores de referência |
| Output examples | privado, `supabase/functions/prova-curso-gerar/LOOP_SPEC.md`, `supabase/functions/aula-avaliacao-worker/LOOP_SPEC.md`, `scripts/linkedin-redator-eval/LOOP_SPEC.md` | 3 | Molde de forma; nada do conteúdo viaja |
| Ground truth | contas de contraste calculadas fora do script, em Python | 2 | `#767676` = 4,5422; `#777777` = 4,4781. Os demais oráculos saem do self-test do privado, recalculados fora do script |
| Related code | privado, `.claude/skills/loop-builder/SKILL.md`; `LLM_PROMPTS_DESIGN.md`; Step 4.5 do `ux-review.md`; passo 4 do `build.md` | 4 | Fonte do porte; a receita de `grep` da 8.3 do plano é passada em cada arquivo |

**How samples will be used:**
- Os LOOP_SPEC reais moldam um exemplo genérico em `.agents/skills/sdd-loop-builder/references/`, escrito do zero, sem copiar nada da RDD.
- Os números do `fp-eval` **não** entram na skill, por serem dado da RDD e de base frágil.
- Limitação registrada: a skill nova não é provada num loop de produção; a prova é a rodada em agente real sobre um DESIGN de exemplo.

## Approaches Explored

### Approach A: Porte enxuto, com travas só onde a conta é exata — Recommended

**Description:** Os 2 scripts entram com testes dos dois lados; o `design-lint` reprova inventário de prompts sem as colunas obrigatórias; o roteador loop × prompt fica como passo escrito na `sdd-build`.

**Pros:**
- Frente menor e mais rápida de revisar.
- Hooks e `report-lint` não mudam de comportamento.
- Quem não usa IA no código não sente nada.

**Cons:**
- Um agente descuidado pode pular o roteador; só a revisão de contexto fresco veria.
- O `design-lint` passa a reprovar DESIGN em andamento com inventário antigo, até ganhar as colunas.

**Why Recommended:** Trava automática compensa quando o erro é fácil de medir, como coluna faltando. Decidir se um texto "é prompt de IA" depende de julgamento, e um alarme que erra muito aprende-se a ignorar: foi o que o privado mediu ao calibrar o scan.

### Approach B: Travas em toda a cadeia

**Description:** Tudo de A, mais o scan em todo commit, um lint novo para cada LOOP_SPEC e uma regra nova no `report-lint` para item em laço sem LOOP_SPEC.

**Pros:**
- Agente nenhum consegue pular a regra, nem por distração.

**Cons:**
- Mexe em 2 contratos protegidos (hooks da F8 e `report-lint`).
- Falso alarme no commit atrapalha todos os projetos.
- Nada disso existe no privado, então não há uso real que prove a utilidade.
- Estimativa de esforço cerca de 1,5 vez maior, com mais rodadas de revisão.

## Selected Approach

| Attribute | Value |
|---|---|
| Chosen | Approach A |
| User Confirmation | 2026-11-04, conversa: "A — porte enxuto (recomendado)" |
| Reasoning | Trava só onde a conta é exata; se o roteador escrito falhar em uso, a trava entra depois, com um caso concreto |

## Key Decisions Made

| # | Decision | Rationale | Alternative Rejected |
|---|---|---|---|
| 1 | U3 e `smoke.*` fora da F13; tarefa registrada na F15 | Sem projeto web real para provar nesta sessão; slot sem leitor é texto morto | Versão mínima por slots, com script de cerca de 300 linhas e prova só em fixture |
| 2 | Só `prompts.wrapper_pattern` | Tem leitor real e testável; evita o scan cego | Criar também `prompts.loop_builder_skill` |
| 3 | `v2.5.0` por tag manual | O número informa a novidade; segue a `v2.3.0` e a `v2.4.0` | `v2.4.1` automática |
| 4 | Contraste truncado: `#777777` → 4.47 REPROVA | Nunca aprova cor abaixo do piso; 4,496 arredondado apareceria como 4.50 | 4.48, arredondado |
| 5 | Abordagem A | Ver Selected Approach | Abordagem B |
| 6 | `contraste.sh`: REPROVA sai 2 | Um gate pode confiar na saída sem ler o texto; no privado sai 0 sempre | Manter como no privado |
| 7 | Scan: caminho inexistente sai 64 | Fail-closed; o privado avisa e conclui `LIMPO` sem ter lido nada | Manter como no privado |
| 8 | Self-test do scan monta os casos numa pasta temporária | O `init` só copia `sdd/fixtures/` na 1ª instalação; quem atualiza veria um vermelho falso | Fixtures instaladas, como no privado |
| 9 | `contraste.sh` imprime número com ponto em qualquer idioma do sistema | Num Mac em português, o `awk` pode imprimir `4,54` | Depender do idioma do sistema |
| 10 | Exclusões de teste do scan valem para qualquer linguagem | No privado, só `*.test.ts` | Manter só TypeScript |
| 11 | Roteador no passo 4 da `sdd-build` | O plano cita 5.5, que é da `sdd-design` | Criar um passo 5.5 na `sdd-build` |
| 12 | 3.3.7 e 2.4.13 ficam fora da tabela, só com a nota de nível (A e AAA) | Evita rotulá-los como AA | Incluí-los na tabela |

## Features Removed (YAGNI)

| Feature Suggested | Reason Removed/Deferred | Can Add Later? |
|---|---|---|
| U3 smoke visual e `smoke.urls_cmd`, `smoke.a11y_cmd` | Decisão do Roberto; sem projeto web real nesta sessão | Yes, na F15 |
| `prompts.loop_builder_skill` | Decisão do Roberto; ninguém precisa dele hoje | Yes |
| Travas da abordagem B (scan no commit, lint de LOOP_SPEC, regra no `report-lint`) | Decisão do Roberto; sem caso real | Yes, se o roteador falhar em uso |
| `FRAMEWORK_LOOP_ENGINEERING.md` (295 linhas) | Os princípios já estão na skill; o resto é histórico da RDD | Yes |
| Números do `fp-eval` na skill | Base frágil e dado da RDD | No |
| "LBI art. 63" e temas WARM/COOL | Específicos da RDD; viram "cada tema do projeto" | No |
| Cor no formato `rgba(...)` no `contraste.sh` | A transparência entra como 3º valor: `contraste.sh '#000' '#fff' .5` | Yes |

## Incremental Validations

| Section | Presented | User Feedback | Adjusted? |
|---|---|---|---|
| Checkpoint 1: 6 entregas, 7 cortes, 2 correções ao plano | Yes | "sim, confirmado" | No |
| Checkpoint 2: comportamento e falhas de cada peça, 5 diferenças em relação ao privado, dependências e prova | Yes | "sim, confirmado" | No |

## Suggested Requirements for /define

### Problem Statement (Draft)

O SDD Open não mede acessibilidade com veredito, não especifica processos de IA em laço e não detecta prompt de produção fora do inventário por script; o privado faz os três, e o Open precisa fazer o mesmo para substituí-lo na F15.

### Target Users (Draft)

| User | Pain Point |
|---|---|
| Quem conduz a UX review de uma feature com tela | "Contraste medido" é regra de texto, sem ferramenta e sem veredito por critério |
| Quem constrói software que chama IA em laço | Não há especificação de parada, orçamento nem verificador antes de o código nascer |
| A fase Build de qualquer projeto | O drift de prompt é um passo escrito, cego a wrapper próprio |
| Roberto, na F15 | Precisa destes mecanismos no Open para desligar os do privado |

### Success Criteria (Draft)

- [ ] `contraste.sh '#767676' '#ffffff'` → `4.54:1 PASSA`, saída 0.
- [ ] `contraste.sh '#777777' '#ffffff'` → `4.47:1 REPROVA`, saída 2.
- [ ] Caso com transparência composta sobre o fundo, com oráculo calculado fora do script; cor inválida e alpha fora de 0 a 1 saem 64.
- [ ] `skill-lint.py .agents/skills/sdd-loop-builder/SKILL.md` → 0 e `skill-lint.py --conversa` 0 nas 18 skills.
- [ ] `prompt-drift-scan.sh --self-test` → 0, sem depender de `sdd/fixtures/`.
- [ ] O scan reprova texto de instrução em `--conteudo` antes de gravar, lê `prompts.wrapper_pattern`, avisa quando vazio, sai 64 com expressão inválida ou caminho inexistente.
- [ ] `design-lint.py` reprova DESIGN com `## LLM Prompts` sem as colunas novas e não muda para DESIGN sem a seção.
- [ ] Cada REPROVA da tabela WCAG vira 1 MUST com o critério e o par medido; 2.1.1 e 2.5.8 vão para as notas de aceite; sem tela, 1 linha de N.A.
- [ ] Todo script novo sem `mapfile`, `declare -A` nem `${x^^}`, com fixture e teste dos dois lados, baseline vermelha na `v2.4.0` e 1 sabotagem.
- [ ] Depois do último conserto, um agente real (Codex CLI) segue o roteador num DESIGN de exemplo com `Tipo=loop`, e o transcript mostra LOOP_SPEC, prompt por estágio e gravação no mesmo turno.
- [ ] Revisão adversarial real com `loop` PRONTO e `--conferir` CONFERE no commit final; Release `v2.5.0` com `SHA256SUMS.txt` conferido.

### Constraints Identified

- Piso: bash 3.2, Python 3.9 stdlib, `awk` e `grep` POSIX; sem Node.
- Padrão agnóstico: texto de skill não cita ferramenta de um agente só (`tests/test_agnostico.py`).
- Específico da RDD não viaja; `callLLM` só como exemplo do slot.
- Delta-only nas skills existentes; toda skill tocada sobe de versão.
- Hooks, `report-lint` e `verify-gate` não mudam de comportamento.
- Artefatos SDD ficam fora do commit da branch de trabalho.
- O repositório privado e o sdd-starter não se alteram.
- Limitação: DESIGN em andamento com inventário antigo passa a reprovar no `design-lint`, até ganhar as colunas.
- Dependência para a F15: quem chama o `contraste.sh` no privado precisa tratar a saída 2; o `sdd-release` precisa de um ponto de extensão para o smoke do privado.

### Out of Scope (Confirmed)

- U3, `smoke.*` e qualquer passo novo no `sdd-release`.
- `prompts.loop_builder_skill`.
- Travas da abordagem B.
- Curator, `/drive`, `drive.*`, `sdd/invariants.md` e a revisão focada na fronteira (F14).
- Regenerar ou alterar o sdd-starter; alterar o repositório privado.

## Session Summary

| Metric | Value |
|---|---:|
| Questions Asked | 4 |
| Approaches Explored | 2 |
| Features Removed (YAGNI) | 7 |
| Validations Completed | 2 |

## Next Step

Execute o **SDD Define by RDD**.
