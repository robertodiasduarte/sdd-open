# Plano consolidado F4–F15 da INCORPORAR_STARTER: starter, porte do SDD privado e substituição do privado pelo Open

- **Data:** 2026-10-29
- **Escrito para:** o Roberto, que decide os itens da seção 5, e a sessão que vai abrir a F4 nesta worktree.
- **Entradas:**
  - `sdd/features/AVALIACAO_STARTER_PARA_OPEN.md`, que define o plano das frentes F1–F6;
  - `sdd/handoffs/HANDOFF_INCORPORAR_STARTER.md`, com o estado em `v2.2.3`;
  - `/Users/robertoduarte/RDD/Wordpress/.claude/sdd/reports/PORTE_SDD_PRIVADO_PARA_OPEN_2026-10-29.md`, o plano do porte privado → open em ondas W0–W5, chamado aqui de **PORTE**;
  - `/Users/robertoduarte/RDD/Wordpress/.claude/sdd/reports/evidence/PORTE_SDD_OPEN/REVIEW-deepseek-2026-10-29.md`, a revisão externa do PORTE, chamada aqui de **REVIEW**.
- **Status:** proposta, versão 1.3. Nenhum código mudou. Os itens marcados com **decidir** vão para o brainstorm da frente correspondente.
- **Revisões:** 29/10 — 1ª versão (F4–F6 cruzadas com o PORTE). 29/10 — Roberto pediu frentes próprias para o porte: as ondas W1–W5 viram **F7–F14** (seção 8), com o mapa item a item (seção 9). 29/10 — auditoria de cobertura contra o PORTE: entraram os 9 princípios (8.0), os detalhes técnicos por frente (8.1), os slots com valor e unidade (8.2), as fontes no privado com o que generalizar (8.3) e as linhas que faltavam no mapa (seção 9). O plano passa a bastar sozinho: o PORTE fica como fonte histórica. 29/10 — v1.3: Roberto fixou os 4 parâmetros de verificação do programa (seção 0), pediu a tabela de degradação por vendor (8.0) e o teste de agnosticismo na F4 (item G), e definiu o fim do programa como **substituir o SDD privado pelo Open** (F15).

---

## 0. Parâmetros de verificação do programa (fixados pelo Roberto em 2026-10-29)

Toda frente, do brainstorm à release, responde a estes quatro. O handoff da família só marca ✅ completa quando os quatro estiverem provados.

| # | Parâmetro | O que significa | Frentes | Como se prova |
|---|---|---|---|---|
| P1 | **Corrigir erros** | Defeito achado no Open é corrigido antes de construir por cima, nunca contornado | W0 (5 defeitos do PORTE §4), mais o que cada revisão de contexto fresco achar (a F3 achou 11 SIM falsos e 2 títulos cegos) | teste que fica vermelho no código antigo e verde no novo (baseline vermelho, LM-002); `grep` do Verify Gate da W0 sem hit; nenhuma nota HIGH/MEDIUM de revisão rebatida sem motivo registrado no BUILD_REPORT |
| P2 | **Manter o padrão agnóstico** | A verdade de cada mecanismo roda nos 7 agentes (Claude Code, Codex CLI, Gemini CLI, Cursor, Kimi Code, Grok Build, GLM); o que depende de subagente degrada para uma parada manual, nunca quebra | todas; a tabela de degradação está em 8.0 | teste de contrato (F4, item G) que reprova nome de ferramenta de um agente só fora dos adaptadores; F9 e F12 provadas também no Codex CLI; scripts em bash 3.2 + Python stdlib, com CI em Ubuntu **e** macOS (M1) |
| P3 | **Incorporar o que o sdd-starter faz melhor** | Os 17 componentes de `sdd/features/AVALIACAO_STARTER_PARA_OPEN.md` entram no Open; depois o starter vira distribuição gerada do Open | F1–F6 (F1–F3 entregues: `v2.2.1`–`v2.2.3`) | os 6 critérios "Pronto quando" da ficha do handoff; `tests/test_skill_lint.py` com a contagem certa; o starter regenerado a partir de `.agents/skills/` sem diff funcional |
| P4 | **Acabar com o SDD privado e substituí-lo pelo Open** | Ao fim, o repositório privado (`~/RDD/Wordpress`) usa o Open instalado pelo `init`, com o que é específico da RDD em slots, playbook e KB; `.claude/commands/workflow/`, `.claude/agents/`, `scripts/` do SDD e `sdd-public/` são removidos | F7–F14 (levam o mecanismo) e **F15** (faz a troca) | no privado, `bash bin/sdd-open.sh doctor` ✅; uma feature real do RDD passa pelo fluxo do Open de ponta a ponta (brainstorm → release) com os gates verdes; `git ls-files .claude/commands/workflow .claude/agents sdd-public` vazio |

Os parâmetros se cruzam: P4 depende de P2 (o RDD usa Claude Code, mas o Open precisa continuar servindo os outros), e P1 vale dentro de P3 e P4 (toda revisão que achar erro corrige antes de seguir).

---

## 1. Em uma frase

As frentes F4, F5 e F6 continuam na ordem combinada. Antes delas entra a **W0 do PORTE**, as correções de meio dia. A **F4** absorve duas peças da W2 do PORTE que tocam as mesmas 13 skills: a linha de transição e o formato de pergunta. Ela também fixa a parada ⏸️ que a W2 vai reusar quando um vendor não tiver subagente. A **F5** pode levar o slot `kb_dir`. A **F6** publica um roadmap das ondas W1–W5, que ficam para depois da F6.

## 2. Estado de partida (conferido em `1a54da5` = `v2.2.3`)

- Há 16 skills: 13 nativas e 3 portadas na F2. O código tem 304 testes, a `sdd-build` está em 2.1.0 e a `sdd-release` em 2.2.0.
- A F3 foi publicada: `report-lint.py` com a regra de migration e um leitor de `layers:` do `sdd/config.yaml` (`ler_layers_sql()`), `deploy-espera-testes.py` e o `doctor` que avisa quando o pacote é mais novo que o projeto.
- O PORTE foi escrito sobre um snapshot anterior à F3 e tem 6 fatos desatualizados (seção 6). A conclusão dele continua valendo: os 5 defeitos da W0 existem na `v2.2.3`, reconferidos um a um (seção 3.1).

## 3. Sequência consolidada

```
F3 ✅ v2.2.3 → W0 (correções) → F4 Conversa → F5 Conhecimento → F6 Docs
            → F7 Evidência → F8 Hooks → F9 Fluxo encadeado → F10 Revisão adversarial (núcleo)
            → F11 Revisão adversarial (gate offline) → F12 Contexto e governança → F13 UX e LLM
            → F14 Playbook e orquestração → F15 Substituição do SDD privado
```

As frentes F7–F14 são as ondas W1–W5 do PORTE (seção 8). W1 e W5 foram divididas em duas cada. A F15 é o fim do programa (parâmetro P4).

O PORTE propunha `F3 → F4 → W0 (em paralelo com a F4) → F5/F6 → W1 …`. A troca de ordem tem um motivo concreto: a W0 **toca SKILL.md**, ao contrário do que o PORTE diz na §2.5.

- A correção 4.1 muda `.agents/skills/sdd-iterate/SKILL.md:43`, que hoje roda `verify-gate.sh --print` e espera "≠5". O `--print` isenta os marcadores, então a checagem nunca dispara.
- A correção 4.5 muda `.agents/skills/sdd-build/references/contexto-fresco.md:41,58` ("Não escreva em arquivo algum"), que contradiz `EVIDENCIA.md:29` (`AVAL-roteiro-3.log`).
- A F4 reescreve a camada de conversa dessas mesmas skills.

Fazer a W0 antes deixa a F4 escrever sobre o texto já corrigido. Ela é pequena (½ dia), corrige um bug real e não depende de nenhuma decisão do Roberto. A alternativa é **fundir a W0 na F4**, o que deixa a F4 maior e mistura correção de defeito com camada de conversa no mesmo diff por skill.

### 3.1 W0 conferida na `v2.2.3`

| # | Defeito (PORTE §4) | Onde está hoje | Ajuste ao PORTE |
|---|---|---|---|
| 4.1 | `sdd-iterate` nunca vê clarificação aberta | `.agents/skills/sdd-iterate/SKILL.md:43` · `sdd/bin/verify-gate.sh:38` (`--print` → `PRINT_ONLY`) | — |
| 4.2 | Promessa de "CONTEXTO de domínio / Step 1.5 / slice 2" | `sdd/templates/DEFINE_TEMPLATE.md:161,169` · `sdd/config.example.yaml:19` | `config.example.yaml:46` também diz "slice 2" (sobre editor e worktrees, que a F2 já entregou: só o rótulo está velho) |
| 4.3 | `/drive` citado sem existir | `sdd/templates/fragments/CLARIFY.md:17` | **também** `sdd/templates/DEFINE_TEMPLATE.md:91` e `sdd/templates/fragments/VERIFY_GATE.md:74` |
| 4.4 | Guard `.githooks/claude-build-report-guard.py` citado sem existir | `sdd/templates/BUILD_REPORT_TEMPLATE.md:213` · `sdd/templates/fragments/EVIDENCIA.md:4` | A linha do template mudou de 190 para 213 por causa da seção de migrations da F3 |
| 4.5 | O avaliador grava ou não grava arquivo? | `contexto-fresco.md:41,58` × `EVIDENCIA.md:29` | — |

Verify Gate da W0, já com os locais corretos:
- `verify-gate.sh sdd/fixtures/DEFINE_FIXTURE_NEEDS_CLARIFICATION.md` sai 5 sem `--print`;
- `grep -rnE 'claude-build-report-guard|/drive|Step 1\.5|slice 2' sdd/ .agents/` não acha nada fora do roadmap.

Cada skill tocada sobe de versão (`sdd-iterate` e `sdd-build`) e recebe um teste em `tests/`.

## 4. O que cada frente passa a levar

### 4.1 F4 Conversa

**Escopo já definido** (handoff e avaliação):
- seção `## Como falar com o aluno` + `references/como-falar.md` nas 13 nativas: fonte no starter para 7, escrita do zero para 6;
- `skill-lint.py` confere a seção;
- diff por skill provando que comandos e ordem dos passos não mudaram;
- `design-lint.py` e `handoff-lint.py` em `sdd/bin/`;
- `metadata.updated` + linha de identificação.

**O que entra pelo PORTE:**

| # | Item do PORTE | Por que entra na F4 | Como |
|---|---|---|---|
| A | **F4 do PORTE, a linha de transição** (`✅ <fase> pronta → seguindo para…`, ≤100 caracteres) | O PORTE §2.5 (X2) pede que ela "caiba na convenção de Status da Decisão 3, sem criar uma 2ª moldura". Se ficar para a W2, as 13 skills são reabertas | Ela vira o **Próximo passo** da camada, a 5ª parte da resposta, com limite de 100 caracteres. Não ganha seção nova. O banner `🧠 FASE` continua sendo a 1ª palavra do Status |
| B | **F5 do PORTE, o formato de pergunta decidível sem abrir arquivo**: recomendada primeiro e com o porquê, números em vez de adjetivos, IDs só em `(ref:)`, eco de 1 linha depois da resposta | É o item 7 da camada do starter ("decisão com opções e efeito"), vindo de outra fonte. Escrever duas regras para a mesma pergunta cria divergência | Um fragmento só: `sdd/templates/fragments/PERGUNTA_DECISAO.md`, citado pelo `como-falar.md` de cada skill. A denylist de jargão genérica (`worktree`, `gate`, `manifest`, `slice`) vira o glossário da F4. A denylist do RDD não viaja |
| C | **A parada ⏸️ que a W2 vai reusar** (PORTE §6.4 e §7; achado 2 HIGH da REVIEW: Codex CLI, Gemini CLI e Cursor não têm subagente, e o despacho em escada vira passo manual) | O item 10 da camada já é "parada com ⏸️: motivo, onde a ação acontece, passos, o que não foi feito, 'Quando terminar, me peça de novo'". É exatamente a face humana do `exit 40 AGUARDANDO_HUMANO` do `sdd-fluxo.sh` da W2 | A F4 fixa o formato da parada no fragmento, com um campo para o caminho do brief gravado e o comando da sessão nova. A W2 só liga o exit 40 a ele. A F4 **não** cria o `sdd-fluxo.sh` |
| D | **Fixtures do lint dos dois lados** (pergunta 3 da REVIEW; LM-001) | O `skill-lint` da F4 e o futuro `sdd-decisoes-lint.sh` da W2 conferem texto de skill. Sem fixture reprovada, o lint prova só que o texto está lá | O `skill-lint` ganha fixtures que **reprovam**: skill sem a seção, `como-falar.md` ausente, pergunta sem opção recomendada, 2 opções recomendadas. A W2 acrescenta as de classe D1–D5 nas mesmas fixtures |
| E | **`design-lint.py` preserva os títulos de ADR** (PORTE C4: `## Key Decisions` / `### Decision N` não podem ser renomeados, porque o `docs-extract-decisions.sh` da W4 lê esses títulos) | O `design-lint` nasce na F4; se não fixar os títulos agora, a W4 vai ter de mudá-lo | O `design-lint.py` reprova DESIGN sem `## Key Decisions` ou com decisão fora do padrão `### Decision N: <nome>` |
| F | **`handoff-lint.py` aceita seções extras** (PORTE N3: a W5 completa o `HANDOFF_TEMPLATE.md` com Recomendações, Veredito, Setup e Ship) | Evita que a W5 tenha de reescrever o lint | O lint confere o mínimo (ficha, Eventos, as seis seções da etapa, nenhum `{placeholder}`, nada de "como discutimos") e não reprova seção a mais |
| G | **Teste de agnosticismo** (parâmetro P2): a F4 traz muito texto novo nas 13 skills | Texto de skill que cita ferramenta de um agente só (`AskUserQuestion`, `Agent`, `PreToolUse`, `TodoWrite`, `Task`, `subagent`, `/model`) quebra o padrão fora do Claude Code | `tests/test_agnostico.py`: varre `.agents/skills/*/SKILL.md` e `references/` e reprova esses nomes fora de uma lista de adaptadores declarados (`bin/lib/vendors.sh` e o que o `init --vendors claude` gera); fixture que reprova e controle que passa. Vale para todas as frentes seguintes |

**Fica fora da F4** (vai para a W2 do PORTE):
- a seção "Encerramento" e o encadeamento automático (F1, F3, F6 e P3 do PORTE): dependem da decisão D1 do PORTE, autonomia;
- as classes D1–D5 nas perguntas (F2 do PORTE);
- o `sdd-fluxo.sh` (F7 do PORTE).

A F4 deixa no `PERGUNTA_DECISAO.md` um lugar reservado para a classe (`[Dn]`), que a W2 preenche.

**Compatibilidade com decisões já tomadas:**
- A Decisão 2 da frente (camada sempre ligada, sem toggle) e a D1 do PORTE (recomendação: `flow.autonomous` configurável, default `false`) tratam de coisas diferentes. A D1 liga ou desliga o **encadeamento**, não a camada de conversa. Não há conflito.
- Uma possível tensão: o PORTE (F5) diz "sem 'Outro'" e o starter diz "sempre a saída 'não sei'". **Decidir** (seção 5, item 2).

### 4.2 F5 Conhecimento

**Escopo já definido:**
- `sdd-kb` com `validate_kb` e `gate.sh`, perfil normativo e RULE_MAP apontando o teste que o Verify Gate roda;
- entrevista do `ux-review-builder` como entrada opcional da `sdd-ux-review`;
- `tests/test_skill_lint.py` passa de 16 para 17 skills.

**O que entra pelo PORTE:**

| # | Item | Como |
|---|---|---|
| G | **F9 do PORTE, "KB Domains" como lista fechada**: o valor só pode vir de `ls <pasta da KB>`, revalidado a cada Define; `nenhum` explícito | A `sdd-kb` grava numa pasta conhecida e a `sdd-define` valida o campo `KB Domains` contra ela. Exige um slot novo, `project.kb_dir` (ou um caminho fixo `sdd/kb/`, sem slot). **Decidir** (item 4): a Decisão 4 da frente e a D11 do PORTE restringem slots novos |
| H | **F11 do PORTE (ler os `UX_REVIEW_*.md` anteriores) e U1 (tabela WCAG 2.2 AA)** | Ficam na W5. A F5 mexe na entrada da `sdd-ux-review`, não no template. Anotar no DESIGN da F5 que o `UX_REVIEW_TEMPLATE.md` vai ganhar a tabela WCAG na W5, para não fixar nada que a contradiga |

### 4.3 F6 Docs

**Escopo já definido:**
- quickstart com "valide antes de seguir";
- guia do aluno adaptado ao open, a partir de `/Users/robertoduarte/rdd-public/sdd-starter/docs/guia-do-aluno.pt-BR.md`, 494 linhas, **não rastreado**;
- "Por que cada regra existe" nas skills de fase;
- README e `AGENTS.md.tmpl` citando as 3 skills da F2 e o bloco do OK da F3.

**O que entra pelo PORTE:**

| # | Item | Como |
|---|---|---|
| I | **`docs/roadmap.md`** | Lista W1–W5 como planejadas (hooks e evidência, fluxo encadeado, revisão adversarial, contexto e governança, loop-builder e drive), no mesmo tom de "Specs como deltas" no `docs/comparison.md`, que continua declarado como planejado (critério 6 da ficha). O grep do Verify Gate da W0 já prevê esta exceção |
| J | **CI também em `macos-latest`** (PORTE, riscos §10.2: o bash 3.2 do macOS quebra script portado) | Hoje o piso Python 3.9.6 + bash 3.2.57 só é provado localmente. Mexe em `.github/workflows/`, junto com a troca do pin `actions/checkout@11d5960a…` (v4.4.0, Node 20 depreciado) por um SHA de v5, pendente desde a F1. **Decidir** (item 5) se entra na F6 ou numa manutenção à parte |
| K | Os documentos de mecanismo (`docs/hooks.md`, `docs/review-contract.md`, `docs/decisoes-D1-D5.md`) | **Não** entram na F6: cada um nasce na onda que entrega o mecanismo (W1, W3, W2) |

### 4.4 Depois da F6

- O starter vira distribuição gerada do open (Decisão 5 da frente). Isso também resolve a D6 do PORTE: as cópias em `~/.claude/skills/sdd-*` passam a ser regeneradas do open, e não serão removidas antes disso.
- O porte continua como frentes F7–F14 desta mesma frente (seção 8), com o checklist §8.1 do PORTE, que já usa as regras desta worktree (`MANIFEST.txt`, testes em `tests/`, bump de versão, sabotagem, OK citando "sdd-open").
- A F7 encontra pronta uma parte da E5 do PORTE: `report-lint.py` já lê `layers:` do `sdd/config.yaml`, por `ler_layers_sql()`, desde a F3.

## 5. Decisões do Roberto que estas frentes pedem

| # | Decisão | Opções | Recomendação | Quando |
|---|---|---|---|---|
| 1 | Ordem da W0 | (a) W0 antes da F4 · (b) W0 fundida na F4 · (c) em paralelo, como o PORTE propunha | **(a)**: são ½ dia e um bug real, e a F4 passa a escrever sobre o texto corrigido; (c) dá conflito no `sdd-iterate/SKILL.md` e no `contexto-fresco.md` | antes de abrir a próxima frente |
| 2 | Saída "não sei" (starter) × "sem 'Outro'" (privado) no formato de pergunta | (a) as duas: "não sei" como opção explícita, sem campo livre "Outro" · (b) só "não sei" · (c) só "sem Outro" | **(a)**: são regras diferentes. "Não sei" é uma saída honesta; "Outro" é um campo livre que reabre a decisão. Ferramentas que já trazem "Other" (o AskUserQuestion do Claude Code) não precisam de "Outro" escrito | brainstorm da F4 |
| 3 | A F4 absorve os itens A–F da seção 4.1? | sim / só A–C / não | **sim**: todos tocam as mesmas 13 skills ou os 2 linters novos | brainstorm da F4 |
| 4 | Pasta da KB: slot `project.kb_dir` ou caminho fixo `sdd/kb/` | slot novo (exige OK, Decisão 4 + D11) · caminho fixo | **caminho fixo `sdd/kb/`**: a decisão 4 da frente pede o mínimo de slots, e a `sdd-kb` é do próprio open | brainstorm da F5 |
| 5 | CI em `macos-latest` + pin do checkout v5 | na F6 · manutenção própria · depois | **manutenção própria, logo depois da W0**: são 2 arquivos em `.github/`, que a F3 manteve intactos de propósito, e não se misturam com docs | antes da F6 |

As decisões **D1, D9, D10 e D11 do PORTE** não travam F4–F6:
- a D1 só define a W2 (a F4 deixa o lugar reservado para a classe);
- a D9 é do repositório privado (aposentar `sdd-public/` e `port-to-public.sh`);
- a D10 é da W1 (hooks × `sdd-higiene-dado`);
- a D11 aparece aqui só no item 4.

## 6. Correções a aplicar no PORTE

O PORTE mora no repositório privado. Não foi editado. Fatos desatualizados em `v2.2.3`:

1. §2.5 X1, §11 I10: a F3 não está "em curso, 3 commits não publicados" — foi publicada como `v2.2.3`, tag em `1a54da5`. O `deploy-espera-testes.py` não é "WIP": está publicado e foi endurecido contra SIM falso na revisão pós-build.
2. §2.5, sequência: "W0 (pode correr em paralelo com F4: não toca `SKILL.md`)" — toca o `sdd-iterate/SKILL.md` e o `contexto-fresco.md` (seção 3 acima).
3. §4.3: o `/drive` também aparece em `DEFINE_TEMPLATE.md:91` e `VERIFY_GATE.md:74`.
4. §4.4: no template, a linha mudou para 213.
5. §2.2, §8.1, §12: são 304 testes, não 242+; o `report-lint` tem 32 contratos, não 14; há 16 skills, não 14.
6. §5.1 E5: o `report-lint.py` já lê `layers:` do config, por `ler_layers_sql()`, para a regra de migration; a E5 reusa o leitor.

## 7. O que não muda

- Decisões 1 a 5 da frente (`## Eventos` do handoff).
- Contratos da F3:
  - rótulos e pergunta única do bloco do OK (`tests/test_contrato_build_release.py`);
  - regra de migration e colunas de `## Migrations aplicadas`;
  - saídas `SIM`, `NAO`, `NAO_SEI` e `NAO_SE_APLICA` do `deploy-espera-testes.py`.
- Regras de trabalho:
  - `MANIFEST.txt` em `LC_ALL=C`;
  - testes em `tests/` na raiz;
  - bump de versão contra a última tag;
  - literais do G2 montados em tempo de execução;
  - push em `main` só com OK citando "sdd-open".

---

## 8. Frentes F7–F14: o porte do SDD privado

Cada frente segue o ciclo das frentes F1–F3:
- fluxo SDD completo nesta worktree;
- Verify Gate `kind: test` com o mesmo `cmd` (cópia por `git archive HEAD`, `publish-gate.sh` em modo ci, `unittest discover`);
- sabotagem por script alterado;
- revisão pós-build de contexto fresco;
- PR, OK citando "sdd-open" e Release automática.

O "critério de pronto" de cada frente vem do §12 do PORTE, com os ajustes da REVIEW.

O que é comum a todas:
- **Slots novos** só os da frente, aprovados no brainstorm dela (D11 do PORTE; Decisão 4 desta frente).
- **Skill nova** muda a contagem de `tests/test_skill_lint.py`: 16 hoje → 17 com a `sdd-kb` (F5) → 18 com a `sdd-loop-builder` (F13) → 19 com a `sdd-drive` (F14).
- **Vendor sem subagente** (Codex, Gemini, Cursor): toda frente que despacha papel fresco usa a parada ⏸️ da F4 e o exit 40 da F9. As frentes F9 e F12 são testadas também no Codex CLI (REVIEW, achado 2).
- **bash 3.2**: todo script portado passa por `grep -nE 'mapfile|declare -A|\$\{[a-zA-Z_]+\^\^' <script>` sem achado, além do piso local e do CI em macOS (REVIEW, pergunta 4; item M1 abaixo).
- **`~/.claude/skills/sdd-*` obsoletas** não contaminam os testes: `tests/apoio.py` já roda cada teste com `HOME` falso. Com a F9 em diante, que despacha agentes, o teste de fluxo confere que nenhuma skill de fora do pacote foi carregada (REVIEW, pergunta 7).

### 8.0 Regras do PORTE (§3) que valem para toda frente F7–F14

1. **A verdade mora num script ou num git hook; o adaptador por vendor é aditivo.** PreToolUse e `model:` são só Claude Code; o `init --vendors claude` gera o adaptador, os outros 6 vendors usam o script no pre-commit e no release.
2. **Slots, não constantes.** Comando de projeto vai para `sdd/config.yaml`; slot vazio = "pule e diga que pulou". Cada frente leva ao brainstorm só os slots dela (8.2).
3. **Registry, não cadeia fixa.** Engines de review em `sdd/review/registry.tsv` editável; a cadeia do privado não viaja, o mecanismo que lê o registry e exclui papéis viaja.
4. **Específico da RDD não viaja** (Anexo C do PORTE). Conceito genérico com implementação RDD (`deno-test-gate.sh`) vira conceito com slot (`{{TEST_CMD}}`) e fixture própria.
5. **Fail-closed onde o privado é fail-closed:** governança que não roda → gate exit 5; avaliador `PENDENTE` → release aborta; evidência ignorada pelo git → relatório negado. Hoje o Open é fail-open nesses três pontos.
6. **Toda regra portada leva fixture e teste** dos dois lados (LM-001): `--self-test` ou fixture em `sdd/fixtures/`, assert em `tests/`.
7. **Delta-only, nunca reescrita** das skills existentes além do necessário para ligar o mecanismo.
8. **Política de decisão é escolha do Roberto (D1), não lacuna.** Sem autonomia, D1–D5 entra só como formato de pergunta.
9. **Allowlist, nunca denylist:** no Open isso é o `MANIFEST.txt` (G3), já em vigor. A `sdd-public-allowlist.tsv` e o `port-to-public.sh` são do repo privado (D9).
10. **Texto de skill não cita ferramenta de um agente só.** O que é específico de um vendor mora no adaptador gerado pelo `init`, nunca no `SKILL.md` nem em `references/`. Provado pelo teste do item G da F4.

**Degradação por vendor (parâmetro P2).** O que é verdade roda em todos; o que depende de subagente degrada assim, sem quebrar:

| Mecanismo | Claude Code | Codex CLI · Gemini CLI · Cursor · Kimi · Grok · GLM |
|---|---|---|
| Avaliador fresco (F7/E11), cartógrafo (F12/C1), curator (F14/P2), revisor de governança (F12/C8) | subagente nativo, automático | a skill grava o brief em `sdd/reports/briefs/`, imprime o comando da sessão nova e **para** com `exit 40 AGUARDANDO_HUMANO` (F9); retoma quando o bloco de retorno aparece |
| Guard do BUILD_REPORT antes de gravar (F7/E6) | PreToolUse em Write/Edit gerado pelo `init --vendors claude` | só no pre-commit (F8) e no release 0a |
| Guard do avaliador com árvore suja (F7/E11) | PreToolUse no `Agent` | chamada explícita na skill, antes do despacho |
| Revisão adversarial (F10) | `claude -p` como engine do registry | `codex exec`, `gemini -p` ou `openrouter:<slug>` via API; sem CLI nenhuma, basta uma chave de API |
| Modo ralph do `sdd-build` e `sdd-drive` (F14/O1) | loop com contexto fresco por tarefa | loop com as mesmas paradas manuais; mais lento, não impossível |
| Raio de impacto por superfície (F14/O2) | um subagente por superfície, em paralelo | sequencial, na mesma sessão |
| Hooks de git (F8), lints, `deploy-espera-testes.py`, camada de conversa (F4) | iguais | iguais |

**Correção medida na F9 (2026-10-31):** o Codex CLI 0.163 tem `multi_agent` estável e ligado e abre colaborador mesmo com `--disable multi_agent` (`sdd/reports/evidence/F9_FLUXO/codex-despacho-subagente.log`): ele está na coluna do subagente, não na do `exit 40`. O `exit 40 AGUARDANDO_HUMANO` não é por vendor; é o degrau 2 (sessão nova) da escada de `sdd-build/references/contexto-fresco.md`, para qualquer agente que não abre o papel fresco sozinho. A prova da F9 no Codex pôs a condição "sem subagente" no prompt (`codex-despacho-40.log`).

Eixo diferente, não de agente: o `deploy-espera-testes.py` só lê GitHub Actions; em outro CI responde `NAO_SE_APLICA` (corte YAGNI da F3, registrado).

### Manutenção M1 (entre a W0 e a F4, ou logo depois da F6)

| | |
|---|---|
| **Itens** | CI também em `macos-latest` (risco "bash 3.2 quebra script portado", PORTE §10.2) · pin `actions/checkout` v4.4.0 → SHA de v5 (pendência da F1) · baseline da `sdd-auditoria-harness` sobre `.agents/skills/` no CI (risco "rug pull no próprio Open", PORTE §10.2) |
| **Toca** | `.github/workflows/publish-gate.yml`, `.github/workflows/release.yml`, `tests/test_release_workflow.py` |
| **Decidir** | item 5 da seção 5 (quando) |
| **Pronto quando** | run do PR verde em `ubuntu-latest` **e** `macos-latest`; `test_actions_fixadas_por_sha` verde com o pin novo; auditoria sem HIGH/CRITICAL |

### F7 Evidência que não mente (W1 do PORTE, parte E)

| | |
|---|---|
| **Itens** | E1–E13 (PORTE §5.1) |
| **Entrega** | `report-lint.py`: avaliação obrigatória com ≥ N camadas (E1, E5 — reusa `ler_layers_sql()`), `PENDENTE` (E2), evidência ignorada pelo git (E3, `--check-ignore`), veredito em heading/tabela/parágrafo fora de fence (E4) · `sdd/bin/gate-baseline.sh` (E7) · `sdd/bin/gate-shell-evidencia.sh` + receita com `rc=$?` no `EVIDENCIA.md` (E8) · `verify-gate.sh --trace` e `--sem-define` + `sdd/traces/` (E9) · `sdd/bin/test-baseline.sh` sobre `{{TEST_CMD}}` (E10, implementação nova) · `sdd/bin/avaliador-guard.sh` no `sdd-build` 1.5 e 5d (E11) · coerência da flag LLM Prompts no passo 0 do `sdd-build` (E12) · fragmento `LLM_PROMPTS_BUILD_REPORT.md` (E13) · adaptador PreToolUse do Claude Code chamando `report-lint.py --stdin` (E6) |
| **Decidir** | D4 (`report-lint` fail-closed por default; recomendado: reprova) · D11 (slots `evidence.require_avaliacao_layers`, `tests.baseline_file`, `evidence.traces_dir`) · se a E6 (gerar `settings.json` no `init`) entra aqui ou na F8 (as duas mexem no `init`) |
| **Depende de** | W0 (EVIDENCIA.md e BUILD_REPORT_TEMPLATE já corrigidos) |
| **Atenção** | `report-lint.py` tem 32 contratos (14 originais + 18 da F3): as regras novas entram como funções ao lado, nenhum contrato muda. A E9 mexe no `verify-gate.sh`: os seis exits e `sdd/fixtures/` ficam idênticos |
| **Esforço (PORTE)** | ~3 dias |
| **Pronto quando** | `report-lint.py` reprova as fixtures `BUILD_REPORT_sem_avaliacao`, `…_pendente`, `…_evidencia_ignorada`; `gate-shell-evidencia.sh` acusa `\| tail` sem `rc=$?`; `verify-gate.sh --trace` grava 1 linha JSONL por execução |

### F8 Hooks de git (W1 do PORTE, parte H)

| | |
|---|---|
| **Itens** | H1–H6 (PORTE §5.2) |
| **Entrega** | `sdd/hooks/pre-commit` (teto do arquivo de contexto por vendor — H2; credencial em config — H3; anti-collapse do playbook — H4; byte NUL — H5; commit na branch padrão — H6) e `sdd/hooks/pre-push` (base velha — H6); `sdd-open.sh init` instala com confirmação; `doctor` confere · **adaptador do Claude Code da E6, transferido da F7** (decisão do Roberto no brainstorm da F7, 2026-10-30): o `init --vendors claude` gera `.claude/settings.json` com PreToolUse em Write/Edit que simula o conteúdo final e chama `python3 sdd/bin/report-lint.py --stdin <caminho>` (já entregue e testado na F7) e PreToolUse no despacho do avaliador que chama `bash sdd/bin/avaliador-guard.sh`; falha aberta, mas avisa. Fontes: `resulting_content()` de `.githooks/claude-build-report-guard.py` e `.githooks/claude-avaliador-guard.py` (privado, `origin/main`) |
| **Decidir** | D3 (o Open distribui hooks? recomendado: sim, pelo `init`) · **D10** (conflito com a `sdd-higiene-dado`, que recusa agir com `core.hooksPath`; recomendado: dispatcher em `sdd/hooks/pre-commit` que chama o `pre-commit.sh` da higiene-dado, e o `alarme.sh` reconhece `sdd/hooks` como seu — exige bump da `sdd-higiene-dado` e mexe nos 29 testes de `test_alarme.py`) · D11 (`project.context_file_max_kb`) |
| **Depende de** | F7 (o pre-commit chama o `report-lint`) |
| **Atenção** | É redesenho do `init`, que estava fora de escopo até a F6; com D3 = sim, entra por decisão registrada. Hook pode ser pulado com `--no-verify`: a verdade continua no `report-lint` do release e no CI (PORTE §9) |
| **Esforço (PORTE)** | ~2 dias |
| **Pronto quando** | depois do `init`, `git config core.hooksPath` = `sdd/hooks`; o pre-commit bloqueia 5 fixtures (H2–H6) e deixa passar o controle; o alarme da `sdd-higiene-dado` continua bloqueando CPF/CNPJ com DV válido |

### F9 Fluxo encadeado e decisões (W2 do PORTE)

| | |
|---|---|
| **Itens** | F1–F3, F6–F8, F10, F11 (PORTE §5.3). F4 e F5 do PORTE já entram na F4 desta frente |
| **Entrega** | `sdd/templates/fragments/FLUXO_ENCADEADO.md` + seção "Encerramento" em cada skill de fase (F1) · classes D1–D5 no lugar reservado do `PERGUNTA_DECISAO.md` da F4 + `sdd/bin/sdd-decisoes-lint.sh` (F2) · recibo "Decidi sozinho" (F3) · decidir e registrar `[auto]` no `sdd-design` (F6) · `sdd/bin/sdd-fluxo.sh` com `review-design` e `loop`, exits 0/10/20/30/**40 AGUARDANDO_HUMANO**/64 (F7) · pontuação forte/fraco da heurística LLM Prompts no `sdd-define` (F8) · "como tratar cada tipo de entrada" no `sdd-brainstorm` (F10) · ler os `UX_REVIEW_*.md` anteriores no `sdd-ux-review` (F11) |
| **Decidir** | **D1** (o Open vira autônomo? recomendado: configurável, `flow.autonomous: false` por default) · D11 (`flow.autonomous`, `review.security_globs`) |
| **Depende de** | F4 (formato de pergunta e parada ⏸️), F7 |
| **Atenção** | Toca de novo as 13 skills (seção "Encerramento"): o diff por skill da F4 é a referência do que já mudou. REVIEW, achado 4: `sdd-fluxo.sh --self-test` com um cenário por exit code e um que prova a rejeição de `\| tee`. REVIEW, pergunta 3: `sdd-decisoes-lint.sh --self-test` com fixtures de pergunta sem classe, com "Outro", com jargão e com 2 recomendadas, todas reprovadas |
| **Esforço (PORTE)** | 3–4 dias |
| **Pronto quando** | `sdd-decisoes-lint.sh --sites .agents/skills` → 0; `sdd-fluxo.sh --self-test` → 0; com `flow.autonomous: true`, a `sdd-define` sobre `sdd/fixtures/BRAINSTORM_EXEMPLO.md` termina com `✅ DEFINE pronto → seguindo para …`; no Codex CLI, um despacho de papel fresco para em `40 AGUARDANDO_HUMANO` com o brief gravado |

### F10 Revisão adversarial — núcleo (W3a do PORTE)

| | |
|---|---|
| **Itens** | R1–R10, R12, R13 (PORTE §5.4) |
| **Entrega** | `sdd/bin/adversarial-review.sh` + `sdd/bin/adapters/{claude,codex,gemini,openrouter}.sh` (um arquivo por engine, reescrito — o `adapters.sh` do privado tem 1.114 linhas e 87 referências RDD) + `sdd/review/{registry.tsv,precos.tsv,prompts/}`; diff congelado com sha256 (R3), contexto SDD injetado (R4), exclusão de papéis com exit 67 (R5), 2º revisor condicional (R6), classificação de falha (R7), convergência honesta (R8), privacidade (R9), custo por papel (R10); review externo obrigatório no `sdd-release` (R1); revisor → auditor no `sdd-design` (R12); `sdd-build` passo 0 chama `sdd-fluxo.sh review-design` (R13) |
| **Decidir** | D2 (engines de exemplo no registry; recomendado: claude, codex, gemini, openrouter, sem cadeia default) · D11 (`review.*`, com unidades explícitas — REVIEW, pergunta 6: `second_reviewer_min_diff_kb` = `wc -c` do patch congelado / 1024) |
| **Depende de** | F9 (`sdd-fluxo.sh`) |
| **Atenção** | REVIEW, achado 1: a W3 original (5–8 dias) não cabia; o gate offline foi separado (F11). Cadeias fixas do RDD não viajam |
| **Esforço (PORTE)** | 6–8 dias |
| **Pronto quando** | `review.auditor == review.revisor1` → exit 67; 1 engine só → ledger com `diversidade: nenhuma`; `sdd-release` sem `review_externo` no ledger aborta; review real `claude` + `openrouter:<modelo>` produz relatório com tokens, custo ≠ 0 e sha256 do diff |

### F11 Revisão adversarial — gate offline (W3b do PORTE)

| | |
|---|---|
| **Itens** | R11 (PORTE §5.4) |
| **Entrega** | `sdd/bin/adversarial-review-gate.sh` (núcleo do privado, 695 linhas e 47 refs RDD) + `sdd/review/stubs/` por engine + `sdd/bin/eval-agree.sh` |
| **Depende de** | F10 |
| **Atenção** | REVIEW, achado 3: stub genérico não reproduz o formato de cada engine — cada stub é uma resposta simulada **daquele** engine, e os asserts conferem os campos extraídos (veredito, proveniência, custo), não só o exit code |
| **Esforço (PORTE)** | 3–4 dias |
| **Pronto quando** | `adversarial-review-gate.sh` → 0 sem rede, com asserts por engine; `eval-agree` roda sobre as fixtures |

### F12 Contexto, patterns e governança (W4 do PORTE)

| | |
|---|---|
| **Itens** | C1–C11 (PORTE §5.5), mais a correção 4.6 do PORTE (dono do `prova_script`) |
| **Entrega** | cartógrafo de domínio no `sdd-define` Step 1.5 + `sdd/bin/contexto-lint.sh` + brief `sdd-define/references/cartografo.md` (C1 — recoloca o "CONTEXTO de domínio" que a W0 tirou do template) · contexto por domínio no `sdd-design` (C2) · `sdd/patterns/README.md` + `sdd/bin/patterns-lint.sh` (C3) · `sdd/bin/docs-extract-decisions.sh` sobre os títulos de ADR que o `design-lint` da F4 fixou (C4) · `sdd/invariants.md` (C5) · governança obrigatória no `sdd-define` Step 6.5, fail-closed com exit 5 (C6, C7) · `sdd/bin/governanca-fronteira.sh` + brief `sdd-governanca/references/revisor.md` (C8) · `sdd/WORKFLOW_CONTRACTS.yaml` reduzido (C9) · abrir a ficha inteira da landmine no `sdd-design` (C10) · bucket de UX indeterminado trava o design (C11) |
| **Decidir** | D5 (governança obrigatória no Define; recomendado: sim, N.A. registrado) · **D8** (dono do `prova_script`; recomendado: o `sdd-define` Step 6.5) |
| **Depende de** | F7, F9 |
| **Atenção** | A `sdd-governanca` tem o open como fonte canônica (Decisão 1): o passo entra na `sdd-define`, a skill não é reescrita. Testar o despacho do cartógrafo no Codex CLI (exit 40) |
| **Esforço (PORTE)** | 5–7 dias |
| **Pronto quando** | `contexto-lint.sh --self-test` e `patterns-lint.sh --self-test` → 0; DEFINE sem a linha `Governança` → `verify-gate.sh` exit 5; `governanca-fronteira.sh` detecta escrita fora do relatório |

### F13 UX e LLM no código (W5 do PORTE, parte U + L)

| | |
|---|---|
| **Itens** | U1–U3, L1–L4 (PORTE §5.6) |
| **Entrega** | tabela WCAG 2.2 AA com veredito no `UX_REVIEW_TEMPLATE.md` e no `sdd-ux-review` (U1; 3.3.7 é nível A e 2.4.13 é AAA, PORTE §9) · `sdd/bin/contraste.sh` (U2) · smoke visual antes × depois, só projeto web, slots `smoke.*` (U3) · **skill nova** `.agents/skills/sdd-loop-builder/` (L1) · roteador loop × prompt no `sdd-build` 5.5 (L2) · fragmento `LLM_PROMPTS_DESIGN.md` + colunas no `DESIGN_TEMPLATE.md` (L3) · `sdd/bin/prompt-drift-scan.sh` com `prompts.wrapper_pattern` (L4) |
| **Decidir** | D11 (`smoke.urls_cmd`, `smoke.a11y_cmd`, `prompts.loop_builder_skill`, `prompts.wrapper_pattern`) · se U3 entra (é só para projeto web) |
| **Depende de** | F5 (a entrevista do `ux-review-builder` já mexeu na entrada da `sdd-ux-review`), F7 |
| **Atenção** | REVIEW, pergunta 5: o `contraste.sh` tem de tratar cor com alpha sobre o fundo (composição antes da razão) e truncar, nunca arredondar (4,49 reprova o piso 4,5:1); fixtures dos dois lados. `test_skill_lint.py` 17 → 18 |
| **Esforço (PORTE)** | ~3 dias |
| **Pronto quando** | `contraste.sh '#767676' '#ffffff'` → 4.54 PASSA e `'#777777'` → 4.48 REPROVA, com caso RGBA; `skill-lint.py .agents/skills/sdd-loop-builder/SKILL.md` → 0; `prompt-drift-scan.sh --self-test` → 0 |

### F14 Playbook, orquestração e sessão (W5 do PORTE, parte P + O + N)

| | |
|---|---|
| **Itens** | P1–P4, O1–O4, N1, N3 (PORTE §5.6). N2 já entregue na F2 |
| **Entrega** | `sdd/bin/playbook-curator.sh` com `--colher` e `--aplicar` (P1) + brief `sdd-playbook/references/curator.md` (P2) + contagem AUTO × pergunta de política e robustez do 17b no `sdd-release` (P3, P4) · **skill nova** `.agents/skills/sdd-drive/` + `sdd/bin/sdd-drive.sh` (O1) · raio de impacto por superfície no `sdd-release` (O2) · `sdd/bin/deploy-do-sha.sh` sobre `gh run` (O3) · `sdd/bin/sdd-archive.py` (O4) · `sdd-new-session` copia os documentos SDD de papel com match exato (N1) · `HANDOFF_TEMPLATE.md` completo (N3; o `handoff-lint` da F4 já aceita as seções extras) |
| **Decidir** | D1 já decidida na F9 (o `/drive` só faz sentido com o mecanismo de autonomia) · D11 (`drive.max_rounds`, `drive.max_tokens`) |
| **Depende de** | F7–F13 |
| **Atenção** | O `sdd-drive` reaproveita o modo ralph do `sdd-build` e tem barreira dura antes do release. `deploy-do-sha` e o item 10 da `sdd-release` 2.2.0 (verificar pelo SHA publicado) devem ser a mesma lógica, não duas. `test_skill_lint.py` 18 → 19 |
| **Esforço (PORTE)** | 4–5 dias |
| **Pronto quando** | `playbook-curator.sh --colher` sobre `sdd/fixtures/playbook/` produz os 4 tipos de linha; `sdd-drive.sh --dry-run` para no Verify Gate com motivo tabelado; `skill-lint.py .agents/skills/sdd-drive/SKILL.md` → 0 |

### 8.1 Detalhes técnicos do PORTE a preservar, por frente

**F7 Evidência**
- E1: nega BUILD_REPORT sem `AVALIACAO_*.md` **e** sem declaração explícita; nega `N.A.` quando o manifest toca ≥ N camadas; exige motivo. Fail-closed: ausência reprova, não só veredito errado (PORTE §9, "guard que itera sobre o que aparece é default-PASS").
- E2: `avaliador: PENDENTE` é uma opção do template para build travado; `VERDICT_RE` passa a conhecê-la; `sdd-release` 0a aborta.
- E3: `git check-ignore` sobre cada caminho citado (no privado, 12 de 19 avaliações se perderam assim).
- E4: veredito em heading, tabela ou parágrafo seguinte; ignora code fence.
- E6: o guard PreToolUse simula o conteúdo final do Edit; **falha aberta mas avisa**.
- E7: `gate-baseline.sh` roda o gate contra `origin/<default_branch>` numa cópia e exige vermelho lá; obrigatório quando o build corrige uma asserção (fonte: 159 l., 1 ref RDD).
- E8: exit 2 quando o `[exit=N]` do log é do formatador (`| tail` sem `rc=$?`); a receita do `EVIDENCIA.md` passa a gravar `rc=$?` (fonte: 111 l., 3 refs).
- E9: 1 linha JSONL por execução em `sdd/traces/{F}.jsonl`, `--trace` ligado por default, `--sem-define` para release sem DEFINE; o curator (F14) também grava.
- E10: `test-baseline.sh` é **implementação nova** sobre `{{TEST_CMD}}` (o `deno-test-gate.sh`, 152 l. e 16 refs, não porta): só falha nova aborta, `--touched` para as superfícies tocadas, teste que sarou sai do baseline.
- E11: `avaliador-guard.sh` nega despachar o avaliador com worktree não commitado (fonte `claude-avaliador-guard.py`, 88 l., 0 refs); chamado no `sdd-build` 1.5 e 5d.
- E13: fragmento com inventário executado, detalhe por prompt, drift, versionamento e rollback.

**F8 Hooks**
- H2: teto de 100 KB para o arquivo de contexto, lista por vendor (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.cursorrules`) em `bin/lib/vendors.sh`.
- H3: `.json/.yml/.env` com segredo em texto claro bloqueado, placeholder passa; `gitleaks protect --staged` se instalado.
- H4: chama `playbook-lint.sh --anti-collapse` quando `sdd/playbook.md` está no staged (sumiço de LM-, reescrita > 20 %, delete/rename).
- H5: byte NUL em arquivo de texto.
- H6: commit no checkout da `project.default_branch` bloqueado; `pre-push` avisa base velha (fonte 31 l., 0 refs).
- Limite: hook de cliente é pulado com `--no-verify`; a política fica no `report-lint` do release + CI (documentar em `docs/hooks.md`).

**F9 Fluxo encadeado**
- F1: Define pronto + `--print` ok + zero marcadores → chama a fase seguinte na mesma sessão; `--parar` desliga.
- F2: D1 irreversível · D2 produto · D3 política · D4 teto · D5 impasse; toda pergunta leva a classe.
- F3: recibo com o sinal que decidiu e como reverter.
- F6: flag LLM ausente vira `true` (conservador); re-check com hits decide; proposta de verificabilidade aceita sem pergunta; `[auto]` no DESIGN.
- F7: `review-design` EXIGIDO com ≥ 3 arquivos novos ou superfície de segurança (`review.security_globs`); manifest ilegível (exit 64) cai no default seguro; `loop` com teto de 3 rodadas, exits 0/10/20/30/**40**/64, ledger por rodada, `| tee` proibido, NEEDS_WORK conta no teto (fonte 283 l., 4 refs).
- F8: 1 sinal forte → true; 2 fracos → true; 1 fraco → true conservador em Notes; sinais de loop → "candidato a loop".
- F10: tabela de entrada: ideia vaga → "conte mais"; feature → questionar a necessidade; comparação → trade-offs.
- F11: ler os `UX_REVIEW_*.md` anteriores no Step 1.

**F10 Revisão adversarial, núcleo**
- R2: auditor emite AGREE / DISAGREE_EVIDENCE / DISAGREE_CONCERN / NOVO; **exit 68** se faltar veredito; "vendor novo = 1 linha" no registry; o `registry.tsv` nasce com `claude`, `codex` (`-s read-only`), `gemini`, `openrouter:<slug>`.
- R3: diff por merge-base com sha256, inclui untracked, exclui a pasta de reviews, para em > 8 MB, `--paths` genérico.
- R4: injeta BRAINSTORM, DEFINE, DESIGN e BUILD_REPORT, teto 180 KB.
- R5: auditor ∉ revisores; desempate ∉ {origem, auditor}; **exit 67** em vez de self-review.
- R6: 2º revisor com segurança, ≥ 8 arquivos, ≥ 120 KB de diff, ≥ 2 camadas, revisor raso (< 30 s); desempate quando o auditor refuta HIGH.
- R7: AUTH não faz fallback; 429 tenta de novo; quota avança; META default × efetivo com aviso.
- R8: `convergencia: n/a` com cadeia incompleta; 3 quedas seguidas por PERSISTENTE geram aviso.
- R9: `data_collection=deny` e `require_parameters` no roteador; recusa gravar em pasta não ignorada pelo git (`review.output_dir`).
- R10: `precos.tsv` com preços públicos; slug ausente = `$?`, nunca 0.
- R12: dois vendors em cadeia, nunca em paralelo (o paralelo foi medido como pior).

**F11 Gate offline**
- R11: stubs por engine (resposta simulada de claude, codex, gemini, openrouter) com asserts sobre veredito, proveniência e custo; `eval-agree` mede a taxa de AGREE do auditor (fonte 207 l., 10 refs).

**F12 Contexto e governança**
- C1: heurística gerar/reusar/pular; agente fresco faz engenharia reversa com `arquivo:linha`; validade por `git diff <sha>..<default_branch> -- <superfícies>`; prova de que só o agente escreveu; **máx. 2 domínios por feature**; camadas de `layers:` (fonte 457 l., 12 refs).
- C3: cita `§Esqueleto (validado_em)`; `patterns-lint.sh --design` bloqueia pattern vencido ou path morto (fonte 461 l., 4 refs).
- C4: `docs-extract-decisions.sh` gera `docs/adr/index.md` com órfãos (fonte 164 l., 0 refs).
- C5: `--cruzar` / `--validar-inv` no curator; opção atômica quando um TOMBSTONE afeta uma INV.
- C6/C7: roda sempre, inclusive com `--parar`; N.A. permitido; 2ª falha ou clarificação aberta grava `[NEEDS CLARIFICATION: governança não rodou…]` → exit 5.
- C8: prompt do revisor leva só 5 campos; snapshot sha256 antes/depois prova que só escreveu o relatório; 1 redespacho; bloco `<<<GOVERNANCA>>>` (fonte 110 l., 5 refs).
- C9: `WORKFLOW_CONTRACTS.yaml` reduzido a produtor/consumidor do gate, schema e invariantes do cartógrafo e do revisor.
- ⛔ não viaja: revisão de schema (`audita-schema-gate.sh`, GRANT na migration, `lint-data-api-grants.py`); fica só o slot `schema.check_cmd` vazio.

**F13 UX e LLM**
- U1: 7 critérios WCAG 2.2 AA com PASSA/REPROVA/N.A.; cada REPROVA vira 1 MUST com o SC e o par medido; 2.1.1 e 2.5.8 herdados para Acceptance Notes; 3.3.7 é nível A e 2.4.13 é AAA.
- U2: razão com alpha composto sobre o fundo, truncando (4,49 reprova o piso 4,5:1) (fonte 55 l., 0 refs).
- U3: deriva as telas do diff, mede axe antes e depois; catraca de contraste com override no ledger; só projeto web.
- L1: LOOP_SPEC v2 — perfil por risco, estado de controle, verificador independente, regras de parada, orçamento por estágio, tabela de estágios LLM × código (fonte 323 l.).
- L2: `Tipo=loop` gera LOOP_SPEC e depois um prompt por estágio; não encerrar o turno após o TXT BLOCK.
- L3: inventário com Versão / Completeness / Refator de?; contrato com Autônomo?, Verification interna, Eval mínimo pré-ship; gate do build por Tipo.
- L4: `prompt-drift-scan.sh --conteudo` avalia antes do Write; `--self-test`; exits 0/2/64; sinais ancorados em `prompts.wrapper_pattern` (fonte 231 l., 4 refs).

**F14 Playbook e orquestração**
- P1: `--colher` (ajudou de tabela ✔, mordeu de AVAL/WAIVED, SUGESTAO por `sup:`, CANDIDATO/REJEITADO, PROMOVER?, `--desde`); `--aplicar` valida a gramática antes de editar (fonte 724 l., 5 refs; fixtures em `sdd/fixtures/playbook/`).
- P2: agente read-only devolve `<<<CURADORIA>>>`; toda linha da colheita aparece; flag CONTAMINAÇÃO; ACEITAR exige `arquivo:linha`.
- P3: contadores com evidência aplicados sem perguntar; ADD/TOMBSTONE/PROMOVER vão para pergunta [D3].
- P4: rc=2 não é "0 deltas"; staging por cópia; evidência `CURATOR-*.log`; commit do curator à parte com revalidação de IDs.
- O1: design → (build → verify)\* com o Verify Gate como parada; orçamento de rodadas e tokens; `--resume`; tabela de motivos de parada; DRIVE_REPORT; barreira dura antes do release.
- O2: um subagente por superfície; cita invariantes do módulo.
- O3: espera o run do SHA até 40 min em background e redispara 1× em falha transitória.
- O4: `sdd-archive.py` retroativo com dry-run; conflito de changelog = `--ours` + prepend (fonte 177 l., 6 refs; a colheita `/fewer-permission-prompts` é só Claude Code).
- N1: copia BRAINSTORM/DEFINE/DESIGN untracked do checkout principal só com match exato slug ↔ feature; lista os parecidos sem copiar (fonte 208 l., 3 refs).
- N3: seções Eventos, Recomendações, Veredito, Setup (rebase/worktree fresco), Tarefas numeradas, Ship com limpeza.

### 8.2 Slots do `sdd/config.yaml` por frente (lista máxima do PORTE §6.2; cada um exige OK no brainstorm da frente)

| Frente | Slot | Default | Unidade / regra |
|---|---|---|---|
| F5 | `project.kb_dir` ou caminho fixo `sdd/kb/` | `""` | decisão 4 desta seção 5 |
| F7 | `evidence.dir` | `sdd/reports/evidence` | — |
| F7 | `evidence.traces_dir` | `sdd/traces` | — |
| F7 | `evidence.require_avaliacao_layers` | `2` | camadas de `layers:` tocadas pelo manifest |
| F7 | `tests.baseline_file` | `sdd/baselines/tests.txt` | — |
| F8 | `project.context_file_max_kb` | `100` | KB do arquivo de contexto por vendor |
| F9 | `flow.autonomous` | `false` | D1; liga o encadeamento, não a camada de conversa |
| F9/F10 | `review.security_globs` | `""` | globs de superfície de segurança (ex.: `auth/**,api/public/**`) |
| F10 | `review.registry` | `sdd/review/registry.tsv` | — |
| F10 | `review.revisor1`, `review.auditor` | `""` | id do registry; vazio = pergunta; `auditor ≠ revisor1` |
| F10 | `review.second_reviewer_min_files` | `8` | `git diff --name-only \| wc -l` do diff congelado |
| F10 | `review.second_reviewer_min_diff_kb` | `120` | `wc -c` do patch congelado / 1024 |
| F10 | `review.second_reviewer_min_layers` | `2` | camadas de `layers:` |
| F10 | `review.shallow_review_secs` | `30` | revisor1 abaixo disso conta como raso |
| F10 | `review.context_max_kb` | `180` | teto do contexto SDD injetado |
| F10 | `review.diff_max_mb` | `8` | teto do diff congelado |
| F10 | `review.output_dir` | `sdd/reports/reviews` | deve estar no `.gitignore` ou `.git/info/exclude` |
| F12 | `schema.check_cmd` | `""` | placeholder vazio; candidato a cair |
| F13 | `prompts.loop_builder_skill` | `sdd-loop-builder` | — |
| F13 | `prompts.wrapper_pattern` | `""` | regex do wrapper de LLM (ex.: `callLLM\\(`) |
| F13 | `smoke.urls_cmd`, `smoke.a11y_cmd` | `""` | só projeto web; candidatos a cair |
| F14 | `drive.max_rounds` | `3` | — |
| F14 | `drive.max_tokens` | `0` | 0 = sem teto; candidato a cair |

`layers:` já existe e passa a ser lido por `report-lint` (F7, já parcialmente na F3) e `sdd-fluxo.sh` (F9). Candidatos a cair, segundo o PORTE: `second_reviewer_*` (podem ser constantes no script), `smoke.*`, `drive.max_tokens`, `schema.check_cmd`.

### 8.3 Fontes no privado e o que generalizar (PORTE §8.2, §8.3, Anexo A)

| Frente | Fonte no privado | Linhas / refs RDD | O que generalizar |
|---|---|---|---|
| F7 | `.githooks/claude-build-report-guard.py` | 541 / 2 | vira funções do `report-lint.py`; a leitura de stdin do PreToolUse vira `--stdin` opcional |
| F7 | `scripts/gates/avaliador-pendente-guard.sh` | 77 / — | função do `report-lint.py` |
| F7 | `scripts/gates/gate-baseline.sh` · `gate-shell-evidencia.sh` | 159 / 1 · 111 / 3 | quase sem mudança |
| F7 | `scripts/verify-gate.sh` (privado) | 243 / 9 | só `--trace` e `--sem-define` para o do Open (197 l.); a propagação do rc 3 do deno fica |
| F7 | `scripts/deno-test-gate.sh` | 152 / 16 | **não porta**; `test-baseline.sh` novo sobre `{{TEST_CMD}}` |
| F7 | `.githooks/claude-avaliador-guard.py` | 88 / 0 | quase sem mudança |
| F8 | `.githooks/pre-commit` · `pre-push` | 154 / 4 · 31 / 0 | sem o item ⑥ (require PHP) |
| F9 | `scripts/sdd-fluxo.sh` · `sdd-decisoes-lint.sh` | 283 / 4 · 103 / 0 | 4 refs viram slots; denylist de jargão do RDD sai |
| F10 | `scripts/adversarial-review.sh` | 991 / 22 | engines → registry; `--paths ".claude/"` → genérico; `precos.tsv` público |
| F10 | `scripts/adversarial-review/adapters.sh` | 1.114 / 87 | **reescrever** um arquivo por engine; cadeias fixas (l. 28–58) saem |
| F11 | `scripts/adversarial-review-gate.sh` · `eval-agree.sh` | 695 / 47 · 207 / 10 | só os asserts de contrato (exclusão de papéis, exit 67/68, diff congelado, convergência n/a) |
| F12 | `scripts/contexto-lint.sh` · `patterns-lint.sh` · `docs-extract-decisions.sh` · `governanca-fronteira.sh` | 457 / 12 · 461 / 4 · 164 / 0 · 110 / 5 | camadas edge/sql/wp-content → `layers:`; `patterns/dominio.md` → `sdd/patterns/` |
| F13 | `scripts/contraste.sh` · `gates/prompt-drift-scan.sh` · `.claude/skills/loop-builder/` | 55 / 0 · 231 / 4 · 323 | quase sem mudança; `callLLM` vira exemplo do slot |
| F14 | `scripts/playbook-curator.sh` · `sdd-archive.py` · `new-session.sh` · `release/deploy-do-sha.mjs` | 724 / 5 · 177 / 6 · 208 / 3 · — | paths e memória do Roberto saem; `deploy-do-sha` genérico sobre `gh run` |
| — | `scripts/playbook-lint.sh` | 338 / 2 | já existe no Open (342 l.); **sincronizar** os dois lados quando a F14 tocar o curator |

Receita por arquivo (PORTE §8.1): `grep -niE 'supabase|deno|wordpress|wp-content|rdd-plataforma|hostinger|RDD/Wordpress|rdd-eval\.env|kimi|codex|gemini|muse|qwen|LM-[0-9]'` em cada fonte, e cada hit vira slot, exemplo em comentário ou linha removida; paths `.claude/sdd/` → `sdd/`, `scripts/` → `sdd/bin/`; agente `.claude/agents/*.md` → brief em `references/<papel>.md` com contrato de entrada, proibições, bloco de retorno `<<<BLOCO>>>` e escada de despacho; saída termina em `RESULTADO:` + `→`.

### F15 Substituição do SDD privado pelo Open (parâmetro P4)

| | |
|---|---|
| **Objetivo** | O repositório privado (`~/RDD/Wordpress`) passa a usar o Open instalado pelo `init`, e o SDD privado deixa de existir como código próprio |
| **Entrega** | (1) `bash bin/sdd-open.sh init --vendors claude` no privado, com `sdd/config.yaml` preenchido: `test_cmd` (deno), `deploy.cmd` (rsync Hostinger), `drift_check_cmd`, `landmines_cmd`, `layers` (edge/sql/wp-content), `review.*`, `schema.check_cmd` (gate de schema por migration, hoje `audita-schema-gate.sh`) · (2) o que é específico da RDD vai para onde o Open prevê: landmines LM-nnn → `sdd/playbook.md` do privado; 46 KBs → `sdd/kb/` (F5); patterns → `sdd/patterns/` (F12); invariantes → `sdd/invariants.md` (F12); buckets WARM/COOL e lentes por público → `sdd/contexto/` ou slot de UX a decidir · (3) remoção: `.claude/commands/workflow/*`, `.claude/agents/*` do SDD, `scripts/` do SDD (os 26 do Anexo A), `.githooks/` (substituído por `sdd/hooks/`), `sdd-public/`, `port-to-public.sh`, `sdd-public-allowlist.tsv`, `gate-sdd-open-s1.sh`, `gate-sdd-prompt-builder.sh` · (4) `CLAUDE.md` do privado aponta para `AGENTS.md` gerado · (5) as cópias `~/.claude/skills/sdd-*` e `anthropic-skills:sdd-*` regeneradas do Open (D6) |
| **Decidir** | o que do Anexo C do PORTE vira slot, KB ou simplesmente some (ex.: `model:` por fase, `/fewer-permission-prompts`, memória do Roberto); se a migração é de uma vez ou por fase (ex.: `/define` do Open primeiro, `/release` por último, porque o deploy é o passo de maior risco); destino do espelho travado e dos 4 arquivos (D7) |
| **Depende de** | F7–F14 (sem eles o Open não tem o que o privado tem: evidência fail-closed, hooks, review adversarial, contexto, curator, drive) |
| **Atenção** | É a única frente que roda **no repositório privado**, não nesta worktree; o fluxo SDD dela pode ser o próprio Open já instalado lá. O caminho inverso §11 do PORTE (I1–I11) deixa de existir: não há mais privado para absorver nada. Mantém-se a regra "específico da RDD não viaja para o Open": o privado passa a ser um **usuário** do Open, com seus slots, KB e playbook |
| **Esforço** | não estimado pelo PORTE; a estimar no brainstorm da F15 |
| **Pronto quando** | no privado: `doctor` ✅ sem ⚠️; uma feature real do RDD percorre brainstorm → define → design → build → release pelo Open, com Verify Gate, report-lint, review adversarial e deploy verificado pelo SHA; `git ls-files .claude/commands/workflow .claude/agents scripts/sdd-fluxo.sh sdd-public` vazio; `publish-gate.sh` do Open continua verde (nada da RDD vazou) |

### Itens de programa do PORTE

| Item | Onde fica |
|---|---|
| `gate-porte-open.sh` composto (§12), que cresce a cada onda | **Substituído** pelo Verify Gate de cada frente + a suíte cumulativa de `tests/`: cada critério de pronto acima vira teste em `tests/test_*.py`, e o `unittest discover` do gate roda todos os anteriores. **Decidir** no brainstorm da F7 se ainda vale um script único de conferência |
| Gate de paridade privado × Open | Fora desta frente: é do repo privado (D9, D6(b) do PORTE) |
| Política de slots por onda (D11) | Em cada frente acima, linha "Decidir" |
| Itens que fluem ao contrário (§11 do PORTE, I1–I11) | Fora desta frente: são mudanças no SDD privado |
| Anexo C do PORTE (o que não viaja) | Fora, por definição |

## 9. Mapa completo: cada item do PORTE e onde mora

| Item do PORTE | Frente | Situação |
|---|---|---|
| 4.1–4.5 (defeitos) | W0 | incorporado (seção 3.1) |
| 4.6 (dono do `prova_script`) | F12 | incorporado (D8) |
| E1–E13 | F7 | incorporado |
| H1–H6 | F8 | incorporado |
| F1, F2, F3, F6, F7, F8, F10, F11 | F9 | incorporado |
| F4 (linha de transição), F5 (formato de pergunta) | F4 | incorporado (itens A e B da seção 4.1) |
| F7 — face humana da parada (exit 40) | F4 | em parte na F4 (item C); o exit e o `sdd-fluxo.sh` na F9 |
| F9 (KB Domains lista fechada) | F5 | incorporado (item G) |
| R1–R10, R12, R13 | F10 | incorporado |
| R11 | F11 | incorporado |
| C1–C3, C5–C11 | F12 | incorporado |
| C4 (ADR) | F4 + F12 | títulos fixos no `design-lint` (F4, item E); extrator na F12 |
| U1–U3, L1–L4 | F13 | incorporado |
| P1–P4, O1–O4, N1 | F14 | incorporado |
| N2 (new-session por tipo) | F2 | já entregue (`sdd-new-session` 1.1.0) |
| N3 (HANDOFF_TEMPLATE completo) | F4 + F14 | `handoff-lint` tolerante (F4, item F); template na F14 |
| §2.3 (quatro lugares com o nome `sdd-build`), D6 (cópias em `~/.claude/skills/`) | depois da F6 | o starter e as cópias viram distribuição gerada do Open (Decisão 5 desta frente) |
| §2.4 (espelho travado), D7 (4 arquivos modificados), D9 (ponte `sdd-public/`), Anexo B (allowlist) | F15 | resolvidos na substituição: a ponte, a allowlist e os gates privados são removidos; D7 vira item "Decidir" da F15 |
| §2.5 X1–X7 (interferências) | X1 → F7 ("depois da F3", já publicada) · X2 → F4 e F9 · X3 → D10 na F8 · X4 → D6 · X5 → D11 (8.2) · X6 → N2 já entregue, I10 fora · X7 → F12 | resolvidas |
| §3 (9 princípios) | todas F7–F14 | seção 8.0 |
| §6.2 (slots), §6.3 (registry), §6.4 (adaptadores por vendor) | 8.2 · F10 · 8.0 regra 1 e exit 40 na F9 | incorporado |
| §7.1 (ordem dentro da onda, com `port-to-public.sh`) | — | substituída pelo ciclo das frentes F1–F3 (D9 = aposentar a ponte) |
| §8.1–8.3 e Anexo A (receita e fontes) | 8.3 | incorporado |
| §9 (conceitos: ACE, EARS, LLM-as-judge, Ralph, ToxicSkills, WCAG 2.2, hooks versionados, fail-closed, trace, diff congelado) | — | fundo teórico; cada frente cita o item ao escrever "Por que cada regra existe" (F6) e os `docs/` do mecanismo |
| §11 I1–I11 (caminho inverso) | F15 | deixa de existir: com a substituição não há privado para absorver nada; o que o Open faz melhor já está no Open |
| Riscos §10.2: macOS, rug pull | M1 | incorporado |
| Risco §10.2: skills obsoletas no ambiente | F9 em diante | `HOME` falso já em `tests/apoio.py`; checagem explícita a partir da F9 |
| Risco §10.2: divergência privado × Open | F15 | eliminado pela substituição: uma fonte só |
| Achados da REVIEW 1–5 e perguntas 1–7 | F9, F10, F11, F12, F13, M1 | incorporados nas linhas "Atenção" e "Decidir" de cada frente |
| ⛔ das tabelas do §5 e Anexo C | — | não viaja |

São 77 itens genéricos: 5 da W0, 72 de E/H/F/R/C/U/L/P/O/N. Todos têm frente, salvo a N2, já entregue. Da revisão externa, os 5 achados e as 7 perguntas estão em alguma frente.

**Esforço somado (estimativas do PORTE):** M1 ½ dia · W0 ½ dia · F7–F14 ≈ 29–36 dias de agente, fora F4–F6 e F15.

## 10. Agrupamento por sessão (proposta)

Uma frente grande por sessão; pares só quando as duas são pequenas e não tocam os mesmos arquivos. A medida vem da F3: um fluxo inteiro consumiu uma sessão (3 gates de 3,5 min, 3 suítes no piso, revisão de contexto fresco, CI e release). Regra do par: publicar a primeira (commit, gate, OK, release) antes de abrir a segunda; o handoff registra duas etapas.

| Sessão | Frentes | Motivo |
|---|---|---|
| 1 | W0 + M1 | meio dia cada; W0 toca templates de `sdd/` e 2 skills, M1 toca `.github/` e 1 teste: nada em comum |
| 2 | F4 | 13 skills + 2 linters + teste de agnosticismo |
| 3 | F5 | skill nova com validador |
| 4 | F6 | guia do aluno (494 linhas) + README + roadmap |
| 5 | F7 | `report-lint`, `verify-gate` e 5 scripts novos |
| 6 | F8 | redesenho do `init` e a D10 |
| 7 | F9 | reabre as 13 skills |
| 8 | F10 (+ F11 se sobrar folga) | a F11 é o gate offline do que a F10 escreveu |
| 9 | F12 | |
| 10 | F13 | skill nova |
| 11 | F14 | skill nova |
| 12+ | F15 | no repositório privado; provavelmente mais de uma sessão (migração por fase) |

Sessões paralelas em worktrees distintas não ajudam: a release é fast-forward em `main`, uma por vez, e o `check-versions` compara com a última tag; frentes vizinhas tocam as mesmas skills. Se aparecer o aviso de compactação do contexto, fechar depois da release e passar o bastão.
