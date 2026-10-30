# HANDOFF: INCORPORAR_STARTER

> Registro do que ficou pronto e do que vem depois. Um arquivo por feature — cada etapa nova entra como seção no topo, nunca como arquivo separado.

## Ficha da feature

| Campo | Valor |
|---|---|
| **Objetivo** | Fazer do sdd-open o único SDD do Roberto, sob 4 parâmetros fixados em 2026-10-29 (`sdd/features/PLANO_F4_F15_CONSOLIDADO.md`, seção 0): **P1** corrigir erros antes de construir por cima; **P2** manter o padrão agnóstico (7 agentes; o que depende de subagente degrada para parada manual); **P3** incorporar o que o sdd-starter faz melhor (F1–F6: camada "Como falar com o aluno", skills de terreno, migration provada por leitura, validadores de fase, versão/testes/release, sdd-kb, docs); **P4** levar para o Open o que o SDD privado faz e o Open não (F7–F14: evidência fail-closed, hooks, fluxo encadeado, revisão adversarial, contexto e governança, UX/LLM, playbook e drive) e então **substituir o SDD privado pelo Open** (F15). Sem abrandar o mecanismo do open (gate com seis estados, evidência, avaliador fresco, playbook, release com veredito). |
| **Status** | 🔨 em andamento |
| **Feito** | 2026-10-29 — avaliação do starter (`sdd/features/AVALIACAO_STARTER_PARA_OPEN.md`) e abertura da worktree. 2026-10-29 — as 5 decisões do Roberto (ver `## Eventos`); **F1 Manutenção entregue**: 115 testes em `tests/`, `scripts/check-versions.py`, `scripts/next-version.sh`, `.github/workflows/release.yml`, 3 padrões de PII; merge em `main` (`f75fbdb`, PR #1) e **Release `v2.2.1`** publicada sozinha com `sdd-open-v2.2.1.tar.gz` + `SHA256SUMS.txt` (hash conferido). 2026-10-29 — **F2 Terreno entregue**: `sdd-checar-ambiente` 1.3.0 (`checar.sh --segredo`), `sdd-higiene-dado` 1.1.1, `sdd-iniciar-repo` 1.1.1 em `.agents/skills/`; `doctor` confere segredo salvo no git; `sdd-new-session` 1.1.0 (pré-voo por `checar.sh --frente`, tabela de tradução, descoberta gravada no config da frente); 242 testes; merge em `main` (`41c6169`, PR #2) e **Release `v2.2.2`** (hash conferido). 2026-10-29 — **F3 Build e Release entregue**: `sdd-build` 2.1.0 com `references/aplicar-migration.md`; `report-lint.py` reprova migration sem linha provada em `## Migrations aplicadas`; `sdd-release` 2.2.0 com o bloco único do OK e `scripts/deploy-espera-testes.py` (SIM/NAO/NAO_SEI/NAO_SE_APLICA); `doctor` avisa skill e `sdd/bin/` mais velhos que o pacote; `LM-004`; 304 testes; merge em `main` (`1a54da5`, PR #3) e **Release `v2.2.3`** (hash conferido). 2026-10-29 — **W0 entregue** (sessão 1, worktree `sdd-open-w0-m1`): `sdd-iterate` 2.0.1 vê clarificação aberta (`--print` + gate sem `--print`); templates sem contexto de domínio, `/drive`, guard inexistente e passos de outro SDD; `sdd-build` 2.1.1 (avaliador grava só `AVAL-*.log`); `tests/test_correcoes_w0.py`; 316 testes; merge em `main` (`303cc87`, PR #4) e **Release `v2.2.4`** (hash conferido). 2026-10-29 — **M1 entregue**: job `testes-macos` nos dois workflows (Python 3.9.6 e bash 3.2.57 afirmados, `release` espera por ele), `actions/checkout` v5.1.0 por SHA, passo "Skill integrity" em `.agents/skills/`; 326 testes; push em `main` (`dd27ef6`, PR #5), **sem Release** (só `.github/**` e `tests/`). 2026-10-29 — **F4 Conversa entregue** (sessão 2, worktree `sdd-open-f4-conversa`): camada "Como falar com o aluno" nas 13 skills nativas + `sdd-checar-ambiente` (seção, `references/como-falar.md`, Status com o nome da fase no lugar do banner, linha de identificação, bump minor); `sdd/templates/fragments/PERGUNTA_DECISAO.md`; `skill-lint.py --conversa` + 7 fixtures; `sdd/bin/design-lint.py` e `handoff-lint.py` (passo 8 da `sdd-design`, 3b da `sdd-handoff`); `tests/test_agnostico.py`; 388 testes; 2 ciclos de revisão de contexto fresco; push em `main` (`2fcdda1`, PR #6) e **Release `v2.2.5`** (hash conferido). 2026-10-29 — **F5 Conhecimento entregue** (sessão 3, worktree `sdd-open-f5-conhecimento`): `sdd-kb` 2.2.0 como 17ª skill (porte do starter 2.1.0; KB em `sdd/kb/` fixo; `validate_kb.py --strict` exige `teste` existente dentro da raiz; `gate.sh` autossuficiente, 4 aceitas e 12 rejeitadas pelo motivo certo, recusa a cópia do `sync`); `sdd/bin/kb-dominios.py` (KB Domains fechado em `ls sdd/kb/` ou `nenhum`, só no `## Technical Context`); `sdd-define` 2.3.0 (passo 10); `sdd-ux-review` 2.3.0 (entrevista de público no passo 1); 499 testes; revisão do DESIGN e 2 ciclos de revisão do build em contexto fresco; push em `main` (`7e19462`, PR #7) e **Release `v2.2.6`** (hash conferido). 2026-10-30 — **F6 Docs entregue** (sessão 4, worktree `sdd-open-f6-docs`): `docs/pt-BR/guia-do-aluno.md` (só PT), `docs/roadmap.md` + PT, quickstarts com "valide antes de seguir" e o caminho de atualização corrigido (P1), `adaptation-guide` corrigido (P1), READMEs com as 17 skills, `AGENTS.md.tmpl` com preparo, KB e a regra 7 "um OK só", "Por que cada regra existe" nas 7 skills de fase (bump patch), `tests/test_docs.py`; 514 testes; revisão do DESIGN e 2 ciclos de revisão do build em contexto fresco; push em `main` (`1c9bbc7`, PR #8) e **Release `v2.2.7`** (hash conferido). **P3 (starter) concluído.** |
| **Falta** | Próxima: o porte do SDD privado como **F7 Evidência** (sessão 5) · **F8 Hooks · F9 Fluxo encadeado · F10/F11 Revisão adversarial · F12 Contexto e governança · F13 UX e LLM · F14 Playbook e orquestração** e **F15 Substituição do SDD privado** (`sdd/features/PLANO_F4_F15_CONSOLIDADO.md`, seções 8 e 9; agrupamento por sessão na seção 10) — cada uma como fluxo SDD completo numa worktree própria; os artefatos SDD desta família vivem na branch `docs/incorporar-starter`, nunca mesclada; `MANIFEST.txt` a cada arquivo novo; cada push em `main` que toca o produto publica uma Release sozinho. |
| **Pronto quando** | **P3 (starter):** (1) `bash scripts/publish-gate.sh .` sai 0 na worktree com os steps novos (testes unitários, check-versions, design-lint, handoff-lint, padrões de PII); (2) `python3 sdd/bin/skill-lint.py --conversa .agents/skills/sdd-*/SKILL.md` sai 0 e as 13 skills nativas (mais a `sdd-checar-ambiente`) têm a seção `## Como falar com o aluno` mais `references/como-falar.md` ✅ (F4); (3) existem `.agents/skills/sdd-checar-ambiente`, `sdd-higiene-dado`, `sdd-iniciar-repo` e `sdd-kb` com `tests/` passando ✅ (F5); (4) `sdd-build` tem `references/aplicar-migration.md` e `sdd/bin/report-lint.py` reprova migration listada sem prova por leitura ✅; (5) existe pelo menos uma Release no GitHub de `robertodiasduarte/sdd-open` com `SHA256SUMS.txt` ✅; (6) o item "Specs como deltas" do `docs/comparison.md` continua declarado como planejado, não como feito. **P1 (erros):** (7) `grep -rnE 'claude-build-report-guard|/drive|Step 1\.5|slice 2' sdd/ .agents/` sem hit e `verify-gate.sh` sem `--print` sai 5 na fixture de clarificação (W0) ✅; toda nota HIGH/MEDIUM de revisão aplicada ou rebatida com motivo. **P2 (agnóstico):** (8) `tests/test_agnostico.py` verde (nenhum nome de ferramenta de um agente só em skills, templates, `AGENTS.md.tmpl` e playbook) ✅ (F4); CI verde em `ubuntu-latest` e `macos-latest` ✅ (M1); F9 e F12 provadas no Codex CLI. **P4 (substituição):** (9) F7–F14 publicadas; (10) no repositório privado, `bash bin/sdd-open.sh doctor` sai ✅, uma feature real do RDD percorre o fluxo do Open de ponta a ponta e `git ls-files .claude/commands/workflow .claude/agents sdd-public` está vazio (F15). |

---

## Eventos

> Toda mudança de escopo, pausa ou replanejamento entra aqui como **linha nova**. Nunca reescreva o campo "Falta" sem registrar o porquê aqui — senão a decisão desaparece.

- 2026-10-29 — Frente criada a partir da avaliação do sdd-starter pedida pelo Roberto ("incluir no OPEN tudo de bom que tem no STARTER, inclusive o jeito de conversar com o aluno"). Nenhum código alterado ainda; só análise, documento e abertura da worktree.
- 2026-10-29 — Decisão 1 (Roberto): a fonte canônica de `sdd-governanca`, `sdd-auditoria-harness` e `sdd-prompt-builder` é o **open**. O starter deixa de editar as três; nada do starter é portado para elas.
- 2026-10-29 — Decisão 2 (Roberto): a camada "Como falar com o aluno" fica **sempre ligada**, sem toggle e sem slot novo em `sdd/config.yaml`.
- 2026-10-29 — Decisão 3 (Roberto): Status `✅ ▶️ ⬜ ⏸️ ➖` abre cada resposta em todas as skills; o banner `🧠 FASE` vira a primeira palavra do Status (`Define: ✅ 1 … · ▶️ 2 …`); o kanban `✅ 🏃 ⬜ ➖` de `sdd/templates/fragments/RESUMO_ETAPA.md` fica **intacto**, só no fechamento da fase.
- 2026-10-29 — Decisão 4 (Roberto): a descoberta de ambiente grava nos **slots existentes de `sdd/config.yaml`** (`project.default_branch`, `editor`, `worktree_base`, `project.test_cmd`, `project.lint_cmd`); não existe `sdd/ambiente.md`. Achado sem slot (cenário de branching, arquivos locais) fica só na conversa.
- 2026-10-29 — Decisão 5 (Roberto, depois de pedir explicação): o sdd-starter passa a ser uma **distribuição gerada a partir de `.agents/skills/` do open**. Mantém repositório, instalação por `npx skills add` e zips por skill, porque é a única porta para quem usa claude.ai ou ChatGPT na web, sem terminal: 11 das 13 skills do open citam arquivos criados pelo `init` e não funcionam como zip. Leva só as skills que funcionam sozinhas, com o gate em modo "confira à mão" e um aviso de quando migrar para o open. Fica em frente própria, depois da F6; nada muda no starter nesta frente.
- 2026-10-29 — Brainstorm da F1 (`sdd/features/BRAINSTORM_F1_MANUTENCAO.md`) muda o escopo das frentes: F1 é rede de segurança (testes dos 5 scripts, `check-versions.py`, release, 3 padrões de PII). **Para a F4**: `design-lint.py`/`handoff-lint.py` (templates do open divergem do starter; reescrita, não porte) e `metadata.updated` + linha de identificação nas 13 skills. **Para a F2**: `doctor` com segredo no histórico (o `checar.sh` já faz). Release: Roberto escolheu **automática no push de `main`** (patch calculado da última tag), contra a recomendação de tag manual; tag manual `v*` também vira Release.
- 2026-10-29 — Build da F1: o `init` copia `sdd/fixtures/` para o projeto do usuário na 1ª instalação (`aplicar()` em `bin/sdd-open.sh`, linha 506) — a premissa "copia só templates, bin e playbook" do Brainstorm e do Design estava errada. `sdd/fixtures/**` entrou nos paths que disparam a Release (DEFINE v1.1, DESIGN v1.1). A decisão de `tests/` na raiz continua válida.
- 2026-10-29 — Revisão de contexto fresco do `release.yml` (veredito FIX FIRST, 5 notas) aplicada em `f75fbdb`: gatilho só em tags `vX.Y.Z`, `next-version.sh vX.Y.Z` publica a tag empurrada, HEAD atrás da última tag não publica, fila por ref, `permissions: contents: read` no `publish-gate.yml`. Parte "mover os checks inline para um script" recusada: mexeria em steps existentes.
- 2026-10-29 — Roberto: "ok, push no sdd-open". Push fast-forward `80d7887..f75fbdb` em `main`; PR #1 MERGED; run `release` 40876615567 publicou `v2.2.1` (inclui o `sdd-new-session` 1.0.0 que estava em `main` sem tag).
- 2026-10-29 — Brainstorm da F2 (`sdd/features/BRAINSTORM_F2_TERRENO.md`), 4 decisões do Roberto: testes portados em `tests/` na raiz (não dentro da skill: `init`/`sync` copiam a pasta inteira ao usuário); `doctor` chama um modo novo `checar.sh --segredo` (sem rede), sempre — sem `doctor --repo`; `sdd-new-session` com script + tabela + pré-voo à mão como fallback (PowerShell); descoberta grava no `sdd/config.yaml` **da frente** (não no checkout principal, que ficaria sujo e faria o `git pull` abortar depois do merge). Abordagem A (transplante com adaptação mínima).
- 2026-10-29 — Build da F2, drift aprovado pelo Roberto: `tests/test_skill_lint.py` fixava 13 skills; vira `test_as_16_skills_reais_passam` (DESIGN v1.1, item 22). Cada frente que acrescenta skill (F5: `sdd-kb`) atualiza esse número de propósito.
- 2026-10-29 — Revisão de contexto fresco do build da F2 (veredito FIX FIRST, 0 HIGH, 2 MEDIUM, 4 LOW): 5 aplicadas em `41c6169` (`test_alarme` isolado do gitconfig global; `--segredo` por pathspec, 11,7 s → 0,06 s com 5 mil arquivos; `SDD_TEST_BASH` nos testes portados; `doctor` não perde linha de nome com quebra; texto da `new-session`); 1 recusada (caminho relativo do `git rm --cached` rodado de subpasta — herdado, o `doctor` não é afetado).
- 2026-10-29 — Roberto: "OK, push no sdd-open — v2.2.2" (contra a alternativa de tag manual `v2.3.0`). Push fast-forward `f75fbdb..41c6169` em `main`; PR #2 MERGED; run `release` 40900694496 publicou `v2.2.2`.
- 2026-10-29 — Brainstorm da F3 (`sdd/features/BRAINSTORM_F3_BUILD_RELEASE.md`), 4 decisões do Roberto: migration = glob fixo (`*.sql`, `migrations/`) **e** `layers.sql` quando preenchido; "o deploy espera os testes?" vira script com fixtures (`.agents/skills/sdd-release/scripts/deploy-espera-testes.py`), não só texto; instalação existente é avisada pelo `doctor` (versão de skill e `sdd/bin/*` diferente do pacote), sem verbo `upgrade`; prova de migration = log de `evidence/` ou `recibo:` (este em qualquer `kind`). Abordagem A (tudo numa release). No checkpoint 2, o script ganhou a 4ª saída `NAO_SE_APLICA`.
- 2026-10-29 — Build da F3: 1º Verify Gate vermelho em `8c1a593` — `test_contrato_build_release` rodava o `playbook-lint.sh` na raiz, e a cópia de `git archive` do gate não tem `.git`; corrigido em `af8b0e3` (sandbox com `git init`).
- 2026-10-29 — Revisão de contexto fresco do build da F3 (veredito FIX FIRST: 1 HIGH, 6 MEDIUM, 6 LOW; 23/23 ATs PASS): 11 SIM falsos do `deploy-espera-testes.py` reproduzidos e corrigidos em `1a54da5` (DESIGN v1.1, Decisão 4); `report-lint` aceita títulos `## 2. Arquivos …` e `## Fase A — Files …`; 10 notas aplicadas inteiras, 1 em parte (`— · —`), 2 rebatidas (escolhas do DESIGN/DEFINE).
- 2026-10-29 — Roberto: "push do sdd-open autorizado" (sem escolher versão ⇒ patch automático). Push fast-forward `41c6169..1a54da5` em `main`; PR #3 MERGED; run `release` 40915091971 publicou `v2.2.3`.
- 2026-10-29 — Roberto pediu para consolidar F4–F6 com o plano do porte privado → open (`/Users/robertoduarte/RDD/Wordpress/.claude/sdd/reports/PORTE_SDD_PRIVADO_PARA_OPEN_2026-10-29.md`, ondas W0–W5) e a revisão externa dele (`…/evidence/PORTE_SDD_OPEN/REVIEW-deepseek-2026-10-29.md`). Resultado em `sdd/features/PLANO_F4_F15_CONSOLIDADO.md`: (1) os 5 defeitos da W0 conferidos na `v2.2.3`, com 2 locais a mais de `/drive` e 1 de "slice 2"; a W0 **toca** `sdd-iterate/SKILL.md` e `contexto-fresco.md`, ao contrário do que o porte diz, então a recomendação é W0 **antes** da F4, não em paralelo; (2) a F4 absorve do porte a linha de transição, o formato de pergunta (`PERGUNTA_DECISAO.md`), a parada ⏸️ que o `exit 40 AGUARDANDO_HUMANO` da W2 vai reusar, fixtures que reprovam no `skill-lint`, títulos de ADR fixos no `design-lint` e `handoff-lint` tolerante a seções extras; (3) a F5 pode levar "KB Domains" como lista fechada (pasta da KB); (4) a F6 ganha `docs/roadmap.md` com W1–W5. Cinco decisões pendentes (seção 5 do plano). Nada de código mudou; o porte (repo privado) não foi editado — 6 correções listadas na seção 6 do plano.
- 2026-10-29 — Roberto: "podemos criar a F7 (e outras) para incorporar as funcionalidades do SDD privado". As ondas W1–W5 do porte viram **F7–F14** desta frente, mais a manutenção M1 (`sdd/features/PLANO_F4_F15_CONSOLIDADO.md`, seção 8: entrega, decisões, dependências, atenção e "pronto quando" de cada uma; seção 9: mapa dos 77 itens do porte → frente). Escopo da frente INCORPORAR_STARTER passa a cobrir também o porte privado → open. Esforço estimado F7–F14: 29–36 dias de agente. Skills novas previstas: `sdd-loop-builder` (F13) e `sdd-drive` (F14) — `test_skill_lint.py` 16 → 17 (F5) → 18 → 19.
- 2026-10-29 — Auditoria de cobertura do plano contra o porte (pedida pelo Roberto): os 77 itens e as 5 notas da revisão externa já tinham frente, mas faltavam os 9 princípios do §3, ~60 detalhes técnicos (exits 67/68, tetos 180 KB/8 MB/100 KB, gatilhos do 2º revisor, flags do curator e do drive, regras do cartógrafo), 7 dos 23 slots do §6.2 e as fontes do Anexo A com linhas/refs. Entraram nas seções 8.0–8.3 e no mapa da seção 9 de `sdd/features/PLANO_F4_F15_CONSOLIDADO.md`. O plano passa a bastar sozinho, sem depender do porte (que mora no repo privado e já tem 6 fatos velhos).
- 2026-10-29 — Roberto fixou os **4 parâmetros de verificação** do programa (P1 corrigir erros · P2 manter o padrão agnóstico · P3 incorporar o que o starter faz melhor · P4 acabar com o SDD privado e substituí-lo pelo Open) e pediu a tabela de degradação por vendor e o teste de agnosticismo. Plano v1.3 (`PLANO_F4_F15_CONSOLIDADO.md`): seção 0 com os parâmetros e como cada um se prova; regra 10 e tabela de degradação em 8.0; item G da F4 (`tests/test_agnostico.py`); **F15 Substituição do SDD privado** como fim do programa (o caminho inverso §11 do porte deixa de existir); agrupamento por sessão na seção 10 (uma frente grande por sessão; pares só W0+M1 e F10+F11). A Ficha ganhou o objetivo novo e os critérios (7)–(10). **Versionamento dos artefatos SDD** (decisão do Roberto): branch `docs/incorporar-starter`, nunca mesclada em `main` (o CI só roda em `main` e PR; 9 arquivos têm caminhos `/Users/` que o G2 reprova e nada está no `MANIFEST.txt`), com tag anotada `docs-2026-10-29`. Prompt da sessão 1 (W0 + M1) em worktree limpa gravado em `sdd/handoffs/SESSION_PROMPT_INCORPORAR_STARTER.md`.
- 2026-10-29 — Sessão 1 (worktree `/Users/robertoduarte/rdd-worktrees/sdd-open-w0-m1`, branch `feat/w0-m1`), W0: o grep do gate da W0 achava 2 locais a mais que o plano (`BUILD_REPORT_TEMPLATE.md:202`, `DESIGN_TEMPLATE.md:105`), onde "Step 1.5" é o passo 1.5 **real** da `sdd-build` (contrato de aceite) — viraram "passo 1.5 da `sdd-build`". O texto pedido para a 4.5 ("sem Write/Edit") citava ferramenta de um agente só (P2): virou "não edite código nem documento do projeto". Revisão de contexto fresco do `b1df8c8`: FIX FIRST, 0 HIGH, 5 MEDIUM, 5 LOW — aplicadas em `303cc87`, 3 rebatidas (`/build` como forma curta da fase; `avaliador-fresco` é nome de papel; `/adversarial-review` no `RESUMO_ETAPA.md` fica pela Decisão 3 e vai para a F10).
- 2026-10-29 — Roberto: "pode finalizar (push + deploy + verificar)" sem citar o repositório → push **recusado** pela regra; depois "ok \"sdd-open\"". Push fast-forward `1a54da5..303cc87` em `main`; PR #4 MERGED; run `release` 40926754472 publicou `v2.2.4`.
- 2026-10-29 — M1, decisão do Roberto (pergunta com 3 opções): o item "baseline da `sdd-auditoria-harness` no CI, falha com HIGH/CRITICAL" do plano não existe como ferramenta — o `collect_evidence.py` não lê `.agents/skills/` (só `.claude/skills/*/SKILL.md`), não tem severidade e sempre sai 0. Escolhida a **varredura inline no CI** (Unicode invisível e código remoto entregue a shell), contra "tirar da M1" e "rodar o collect_evidence como smoke".
- 2026-10-29 — Revisão de contexto fresco do `eac5484` (M1): FIX FIRST, 0 HIGH, 4 MEDIUM, 6 LOW — aplicadas em `dd27ef6` (varredura fail-closed com alvo vazio; piso **afirmado** e `python3` do PATH = piso; regex de código remoto e faixas Unicode ampliadas); 3 aceitas com motivo (escopo só `.agents/skills/`; texto que cita `curl … | sh` reprova; `release` preso ao runner macOS).
- 2026-10-29 — Roberto: "finalizar (push + deploy + verificar)" sem o repositório → recusado; depois "finalizar (push + deploy + verificar) sdd-open". Push fast-forward `303cc87..dd27ef6` em `main`; PR #5 MERGED; só o `publish-gate` roda (run 40931927983) — `.github/**` e `tests/` ficam fora dos `paths` do `release.yml`, então a M1 **não gera tag**; a última Release continua `v2.2.4`.
- 2026-10-29 — Brainstorm da F4 (`sdd/features/BRAINSTORM_F4_CONVERSA.md`), 7 decisões do Roberto, todas na opção recomendada: decisão 2 do plano = **"não sei" e "sem Outro"**, as duas; decisão 3 = a F4 **absorve A–F**; `skill-lint` ganha a flag **`--conversa`** (o padrão continua só frontmatter, porque o lint vai para o projeto do usuário); a **`sdd-checar-ambiente` entra** (14 skills, não 13); o `handoff-lint` confere o **template do open**, não o formato do starter (o item F do plano descrevia o do starter); `sdd-design` e `sdd-handoff` **rodam o lint** no próprio documento (2 exceções declaradas à regra "comandos não mudam"); `test_agnostico` reprova **nomes de ferramenta** e permite "subagente" como conceito, varrendo skills, templates, `AGENTS.md.tmpl` e playbook. Abordagem A (seção autocontida + `como-falar.md` + fragmento único, uma release).
- 2026-10-29 — Design da F4: a `sdd-checar-ambiente` manda repassar a saída do script "sem frase antes"; a exceção (d) passou a valer para toda resposta dela (Status antes do relatório, sem retraduzir). O lint da `sdd-handoff` virou o passo `3b` para não renumerar o passo 4. DEFINE v1.1.
- 2026-10-29 — Revisão de contexto fresco da F4, ciclo 1 sobre `4e77a1f`: NEEDS_WORK, 0 HIGH, 4 MEDIUM, 8 LOW (21/22 ATs PASS; o AT-022 depende do CI). Aplicadas em `fd94876` (L1 em parte: opção desconhecida no `skill-lint` continua 64). M3 mudou o contrato: ficha com Status ✅ dispensa o prompt de retomada, porque a `sdd-handoff` o declara opcional sem continuação (DEFINE v1.2, AT-012). Ciclo 2 sobre `fd94876`: **PASS**, 0 HIGH, 0 MEDIUM, 6 LOW — 5 aplicados e 1 em parte em `2fcdda1` (lista numerada, `__negrito__` e prosa entre pergunta e opções ficam fora do formato do DEFINE).
- 2026-10-29 — Roberto: "push sdd-open autorizado" (sem escolher versão ⇒ patch automático, contra a alternativa `v2.3.0` por tag manual). Push fast-forward `dd27ef6..2fcdda1` em `main`; PR #6 MERGED; run `release` 40952893409 com `testes` e `testes-macos` antes do `Publicar release` (20:57:35 → 20:57:37); publicou `v2.2.5`.
- 2026-10-29 — Brainstorm da F5 (`sdd/features/BRAINSTORM_F5_CONHECIMENTO.md`), 6 decisões do Roberto, todas na opção recomendada: decisão 4 do plano = **`sdd/kb/` fixo**, sem slot `project.kb_dir`; o item G vira **lint novo em `sdd/bin`** (`kb-dominios.py`), contra "modo no `validate_kb.py`" e "só texto"; o `gate.sh` fica **na skill, autossuficiente** (casos montados dos exemplos), contra "só no pacote"; RULE_MAP → Verify Gate = **arquivo existe + lint lista** (sem casar texto do `cmd`); entrevista do `ux-review-builder` **opcional, dentro do passo 1** da `sdd-ux-review`, gravada em `## User and Context`; amostras **só as do starter** (não a KB real `programa-irpf`). Abordagem A (transplante, uma release). O Roberto pediu define → ux-review → design → revisão do design → build → revisão do build em sequência.
- 2026-10-29 — Revisão do DESIGN em contexto fresco (modo contrato): NEEDS_WORK, 2 HIGH, 4 MEDIUM, 2 LOW, aplicadas antes do build. H1: a cópia que o `init --vendors claude` gera ganha 2 linhas `sdd-open:generated` em todo arquivo não-JSON, e o exemplo normativo reprovava lá (SHA-256 e RULE_MAP) — os textos passam a apontar `.agents/skills/sdd-kb/…`, o gate recusa a cópia gerada (AT-017 novo) e `.gitattributes` com `-text` só em `fontes/`. H2: o passo 10 sem bloco cercado, para o `comandos-intactos` bater. DESIGN v1.1, DEFINE v1.3.
- 2026-10-29 — Build da F5: a sabotagem do `kb_normativo.py` não deixou teste vermelho (o `rule-map --check` só tinha o lado verde) → `RuleMapCheck` em `7e5b25c`. Ciclo 1 da revisão do build sobre `7e5b25c`: NEEDS_WORK, 0 HIGH, 3 MEDIUM, 6 LOW, todos aplicados em `0e0dba5` (KB Domains só do `## Technical Context`; RULE_MAP do exemplo conferido antes dos casos; testes de caso bom rejeitado e de outro motivo; `teste` fora da raiz reprova). Ciclo 2 sobre `0e0dba5`: **PASS** (15/15 mutações reversas pegas), 3 LOW novos aplicados em `7e19462`.
- 2026-10-29 — Roberto: "release do sdd-open autorizado" (sem escolher versão ⇒ patch automático, contra a alternativa `v2.3.0` por tag manual). CI do PR #7 verde (run 40969129265: `gate` e `Testes no piso (macOS)`). Push fast-forward `2fcdda1..7e19462` em `main`; PR #7 MERGED; run `release` 40970012304 com `testes` e `testes-macos` antes do `Publicar release`; publicou `v2.2.6`.
- 2026-10-29 — Roberto perguntou se F6 e F7 cabem na mesma sessão. Recomendação: não. A regra do par (plano, seção 10) exige duas frentes pequenas que não toquem os mesmos arquivos: a F7 tem 13 itens (E1–E13), 5 scripts novos, `verify-gate.sh --trace` e 3 decisões (D4, D11, E6), ~3 dias no PORTE; a F6 adapta um guia de 494 linhas; as duas mexem na `sdd-build` e no `docs/roadmap.md`. Roberto: "prepare o prompt para F6. documente tudo. /sdd-new-session F6" — a F6 vai sozinha na sessão 4.
- 2026-10-29 — Frente F6 aberta com a `sdd-new-session` (starter 1.3.0, em `~/.claude/skills/`): worktree `/Users/robertoduarte/rdd-worktrees/sdd-open-f6-docs`, branch `feat/f6-docs` nascida de `origin/main` = `7e19462`, nomes no padrão da família (não o `../sdd-open-frentes/<slug>` padrão da skill); os artefatos SDD da branch `docs/incorporar-starter` já copiados para lá, fora do commit. A skill gravou `sdd/ambiente.md` no checkout principal (`/Users/robertoduarte/rdd-public/sdd-open`), não rastreado: é nota local da skill do starter, não do open (Decisão 4 da frente: o open usa os slots do `sdd/config.yaml`).
- 2026-10-29 — Brainstorm da F6 (`sdd/features/BRAINSTORM_F6_DOCS.md`), decisões do Roberto: guia do aluno **só em português** (`docs/pt-BR/guia-do-aluno.md`), roadmap em inglês e português; "Por que cada regra existe" nas **7 skills de fase**; Release **`v2.2.7` automática** (sem tag à mão); amostras: nenhuma; abordagem A (adaptação escrita à mão, uma Release só); os 2 checkpoints confirmados.
- 2026-10-29 — Revisão do DESIGN da F6 em contexto fresco (modo contrato): NEEDS_WORK, 3 HIGH, 4 MEDIUM, 3 LOW, aplicadas antes do build (DEFINE v1.1, DESIGN v1.1). H2 achou um P1 no produto publicado: o passo 5 dos quickstarts ensinava `git pull` + `sync`, que não atualiza skill nenhuma (o `init` não sobrescreve, o `sync` só regera adaptadores) — corrigido nos quickstarts e no guia. M4: a regra "um OK só" entrou como regra 7 do `AGENTS.md.tmpl`.
- 2026-10-29 — Revisão do build da F6, ciclo 1 sobre `963c47e`: NEEDS_WORK, 3 HIGH (o guia dizia que o alarme "registra e libera"; que a `sdd-design` devolve Define com dúvida; uma regra inventada no brainstorm), 3 MEDIUM, 6 LOW, todas aplicadas em `aaae1b4`. Ciclo 2 sobre `aaae1b4`: **PASS**, 6 LOW aplicados em `1c9bbc7`.
- 2026-10-30 — Roberto: "Push sdd-open autorizado". CI do PR #8 verde (run 40984992013: `gate` e `Testes no piso (macOS)`). Push fast-forward `7e19462..1c9bbc7` em `main`; PR #8 MERGED; run `release` 41025735985 com `testes` e `testes-macos` antes do `Publicar release`; publicou `v2.2.7`. Com a F6, os itens do P3 (F1–F6) estão entregues; o programa segue no P4 (F7–F15).

---

## 2026-10-30 — F6 Docs (entregue, Release v2.2.7)

### O que foi feito

- **Fluxo SDD completo** (sessão 4, worktree `/Users/robertoduarte/rdd-worktrees/sdd-open-f6-docs`, branch `feat/f6-docs`):
  - artefatos: `sdd/features/BRAINSTORM_F6_DOCS.md`, `DEFINE_F6_DOCS.md` (v1.1, 14 ATs EARS, Clarity 14/15), `DESIGN_F6_DOCS.md` (v1.1, 8 decisões, 26 linhas no manifest) e `sdd/reports/BUILD_REPORT_F6_DOCS.md` (`report-lint` 0, `validate_build_report` PASS);
  - revisões: `sdd/reviews/REVISAO_DESIGN_F6_DOCS_20261029.md` (NEEDS_WORK, 3 HIGH, 4 MEDIUM, 3 LOW, aplicadas antes do build), `AVALIACAO_F6_DOCS_20261029-ciclo1.md` (NEEDS_WORK, 3 HIGH, 3 MEDIUM, 6 LOW, sobre `963c47e`) e `…-ciclo2.md` (**PASS**, 6 LOW, sobre `aaae1b4`);
  - commits `963c47e` (build), `aaae1b4` (ciclo 1) e `1c9bbc7` (ciclo 2), sobre `7e19462`;
  - PR https://github.com/robertodiasduarte/sdd-open/pull/8 (MERGED); 23 arquivos (4 novos, 19 alterados, +1394/−41).
- **`docs/pt-BR/guia-do-aluno.md`** (novo, ~690 linhas, só em português, decisão do Roberto): adaptado do guia do starter (`/Users/robertoduarte/rdd-public/sdd-starter/docs/guia-do-aluno.pt-BR.md`, não rastreado lá, só lido). 10 blocos, 17 fichas de skill, 7 agentes, `init --vendors … --dry-run` e `--yes`, `git init -b main`, caminho de atualização (`doctor` → apagar a skill ou o arquivo de `sdd/bin` não editado → `init --yes` → `sync --yes`), tabela dos exits do Verify Gate, glossário, FAQ do starter instalado global (o `doctor` não o vê).
- **`docs/roadmap.md` e `docs/pt-BR/roadmap.md`** (novos): 7 temas, 6 *planned*/planejado e "Specs as deltas"/"Specs como deltas" *under evaluation*/em avaliação, sem datas. O `comparison` (EN/PT) aponta para eles.
- **Quickstarts (EN/PT)**: passo 4 com a regra do método, 4 linhas "Validate before moving on:"/"Valide antes de seguir:", a tabela "Você quer… / Escreva no Design / No Build" e os 7 agentes; passo 5 corrigido (P1: `git pull` + `sync` não atualizava skill); "Coming from sdd-starter" diz que o `doctor` não vê instalação global.
- **`adaptation-guide` (EN/PT)**: P1 — 2 links quebrados e a frase de que um script de landmines vinha no pacote (o slot `release.landmines_cmd` sai vazio).
- **READMEs**: seção "As 17 skills"/"The 17 skills", linha da base de conhecimento, "um OK só", "prepare uma vez" + `sdd-new-session` por frente, links do roadmap e do guia.
- **`AGENTS.md.tmpl`**: linha "Antes" (4 skills de preparo), linha "KB" (`sdd-kb`), fase 1 cita `sdd/bin/kb-dominios.py`, regra 7 "**Publicar pede um OK só.**"; o marcador da lista de agentes que o `init` preenche ficou intacto.
- **"Por que cada regra existe"** nas 7 skills de fase, logo antes de `## Encerramento (obrigatório)`, passos intactos (`comandos-intactos.py`: extração + texto normalizado). Versões: brainstorm 2.1.1, define 2.3.1, governanca 2.2.1, ux-review 2.3.1, design 2.1.1, build 2.2.1, release 2.3.1.
- **`tests/test_docs.py`** (novo, 15 métodos): links relativos com âncora (regra do GitHub por `unicodedata`, caixa exata por `os.listdir`), guia (blocos, fichas, agentes, frases proibidas como "registra e libera"), quickstart, roadmap, `comparison` (só a célula do SDD Open), README e `AGENTS.md.tmpl`, seções "Por que". `MANIFEST.txt` +4.
- **Evidência** em `sdd/reports/evidence/F6_DOCS/`: scripts `gerar-evidencia.sh`, `sabotagem.sh`, `comandos-intactos.py`, `baseline-notas2.py`, `links-pr.sh`; logs `GATE`, `check-versions`, `comandos-intactos`, `contratos-intactos`, `codepoints`, `skill-lint-conversa`, `linhas`, `escopo`, `testes-f6`, `baseline`, `baseline-notas`, `baseline-notas2`, `sabotagem`, `links-pr`, `ci-pr`, `release`, e os `AVAL-DESIGN-*`, `AVAL-*` e `AVAL2-*` dos revisores.
- **Release**: OK "Push sdd-open autorizado" (2026-10-30); push fast-forward `7e19462..1c9bbc7`; run `release` 41025735985 (testes, testes no piso macOS, publicar) e `publish-gate` 41025736350 verdes → https://github.com/robertodiasduarte/sdd-open/releases/tag/v2.2.7, tag em `1c9bbc7`; SHA-256 de `sdd-open-v2.2.7.tar.gz` `6a3eaea3c996301af6c289d32fe88a1f49df65bd8c4b57eaf4b31c92b45ebb59`, `shasum -a 256 -c` OK.

### Casos e testes em aberto

- **Piso:** `SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover -s tests -p 'test_*.py'` → 514 OK em `1c9bbc7` (dentro do Verify Gate). A base `7e19462` tinha 499.
- **Gate e versões:** `bash sdd/bin/verify-gate.sh --strict sdd/features/DEFINE_F6_DOCS.md` → 0 em `963c47e`, `aaae1b4` e `1c9bbc7`. `check-versions --base v2.2.6 --base-obrigatoria` VERDE. `skill-lint --conversa` 17/17; maior `SKILL.md` com 376 linhas.
- **Âncoras no GitHub (A-002):** os 43 títulos do guia têm, na página renderizada da branch do PR, a mesma âncora que o `ancora()` do teste gera; as 10 do sumário abrem (`links-pr.log`).
- **Sabotagem:** 4/4 (link do sumário para âncora inexistente, seção "Por que" apagada da `sdd-build`, "Specs como deltas" ✅ na coluna do open, 1 palavra mudada no Quality Gate da `sdd-build` contra o `comandos-intactos.py`).
- **Conferência de fechamento** (inventário): o código roda (514 no piso e no CI ubuntu + macOS); os critérios combinados passam (gate 0, `report-lint` 0, `skill-lint --conversa` 17/17, ≤ 500 linhas por `SKILL.md`, teste de links, 1 sabotagem por script, revisão sem HIGH aberto); as mudanças estão em `origin/main` e na tag `v2.2.7`, e os artefatos SDD na branch `docs/incorporar-starter`; o que ficou de fora está nas pendências.
- **Não verificado:** um aluno real seguindo o guia do zero num dos 7 agentes; os testes conferem só texto, links e âncoras.

### Pendências

**🐛 Bug fix** — o que ficou quebrado, parcial ou com comportamento errado conhecido:

- nenhuma.

**✨ Feature improvement** — o que é incremento planejado, melhoria ou próxima etapa de escopo:

- **Conferência com um aluno real** (ou num agente, do zero): guia + quickstart num projeto vazio, até o primeiro Verify Gate verde. Junta-se às conferências pendentes da F4 (A-002) e da F5.
- **Roadmap a manter:** cada frente que entrega um tema tira a linha de `docs/roadmap.md` e `docs/pt-BR/roadmap.md` (a regra está no próprio texto: "A theme leaves this page when it ships"). A linha "Hooks and evidence" cobre F7 **e** F8: a F7 reescreve a linha só com o que falta (hooks), a F8 a remove. O `test_docs.Roadmap` conta 7 linhas: atualizar a contagem junto.
- **Guia do aluno só em português** (decisão do Roberto): o README em inglês aponta para ele como "Portuguese only".
- **Risco aceito:** o regex `FORA_DO_GIT` do `test_docs.py` tem autoteste com 7 redações de "a pasta sdd fica fora do git"; uma redação nova no guia pode precisar de mais uma alternativa.
- **Pendência herdada:** o `report-lint.py` com cabeçalho não reconhecido continua fail-open (**F7**, próxima); `RESUMO_ETAPA.md:4,49` cita `/adversarial-review` (F10); o sdd-starter como distribuição gerada do open (Decisão 5) é frente própria, agora desbloqueada.

### Próximos passos

1. **Sessão 5 — F7 Evidência** (prompt em `sdd/handoffs/SESSION_PROMPT_INCORPORAR_STARTER.md`), numa worktree nova `/Users/robertoduarte/rdd-worktrees/sdd-open-f7-evidencia`, branch `feat/f7-evidencia` de `origin/main` = `1c9bbc7`. Pronto quando: `report-lint.py` reprova as fixtures `BUILD_REPORT_sem_avaliacao`, `…_pendente` e `…_evidencia_ignorada`; `gate-shell-evidencia.sh` acusa `| tail` sem `rc=$?`; `verify-gate.sh --trace` grava 1 linha JSONL por execução; Release publicada com o hash conferido.
2. **F8 → F14** e **F15** (plano, seções 8 e 10); a frente do sdd-starter gerado (Decisão 5) entra quando o Roberto quiser.

### Alertas — o que não quebrar

- **Os docs agora são contrato testado** (`tests/test_docs.py`): todo link relativo e âncora de `README*.md` e `docs/**` tem de abrir; renomear um título do guia quebra o sumário. O roadmap conta 7 linhas e "Specs como deltas" tem de ficar fora do ✅ na coluna do open.
- **"Por que cada regra existe"** nas 7 skills de fase fica logo antes de `## Encerramento (obrigatório)`; o `PorQueCadaRegra` confere a posição. Skill nova de fase precisa da seção.
- **`AGENTS.md.tmpl`**: rótulos "Antes", "KB" e a regra 7 estão testados (`ReadmeEAgents`).
- **Evidência:** `report-lint` só aceita `evidence/<FEATURE>/` com o nome exato do relatório.
- Demais alertas das etapas F5, F4, M1, W0 e F3 continuam valendo.

### Onde está o trabalho

- Remoto `https://github.com/robertodiasduarte/sdd-open.git`, `main` = `1c9bbc7` = tag `v2.2.7`. Última Release: https://github.com/robertodiasduarte/sdd-open/releases/tag/v2.2.7.
- Worktree da sessão 4: `/Users/robertoduarte/rdd-worktrees/sdd-open-f6-docs`. A branch `feat/f6-docs` está em `1c9bbc7`, já mesclada. A worktree de revisão `sdd-open-f6-aval` já foi removida.
- Os artefatos SDD (`sdd/features|handoffs|reports|reviews`) estão gravados na branch `docs/incorporar-starter`.
- Limpeza, rodada de fora da pasta e só depois de gravar a branch `docs/`: `git -C /Users/robertoduarte/rdd-public/sdd-open worktree remove /Users/robertoduarte/rdd-worktrees/sdd-open-f6-docs && git -C /Users/robertoduarte/rdd-public/sdd-open branch -d feat/f6-docs`. As worktrees das sessões 1–3 já não existem; resta a antiga `sdd-open-incorporar-starter`, que não deve ser usada.

---

## 2026-10-29 — F5 Conhecimento (entregue, Release v2.2.6)

### O que foi feito

- **Fluxo SDD completo** (sessão 3, worktree `/Users/robertoduarte/rdd-worktrees/sdd-open-f5-conhecimento`, branch `feat/f5-conhecimento`):
  - artefatos: `sdd/features/BRAINSTORM_F5_CONHECIMENTO.md`, `DEFINE_F5_CONHECIMENTO.md` (v1.4, 17 ATs EARS, Clarity 14/15), `DESIGN_F5_CONHECIMENTO.md` (v1.4, 9 decisões, 25 linhas no manifest), `sdd/reviews/UX_REVIEW_F5_CONHECIMENTO.md` e `sdd/reports/BUILD_REPORT_F5_CONHECIMENTO.md` (`report-lint` 0);
  - revisões: `sdd/reviews/REVISAO_DESIGN_F5_CONHECIMENTO_20261029.md`, `AVALIACAO_F5_CONHECIMENTO_20261029-ciclo1.md` e `…-ciclo2.md`;
  - commits `bafc63c` (build), `7e5b25c` (teste achado pela sabotagem), `0e0dba5` (ciclo 1) e `7e19462` (ciclo 2), sobre `2fcdda1`;
  - PR https://github.com/robertodiasduarte/sdd-open/pull/7 (MERGED); 50 arquivos (42 novos e 8 alterados).
- **`.agents/skills/sdd-kb/` 2.2.0** (36 arquivos), portada de `sdd-starter/skills/sdd-kb` 2.1.0 (`17c69c4`):
  - sem `agents/openai.yaml`, sem `tests/` dentro e sem citar o starter (`PORTADAS` + `sdd-kb`);
  - KB em `sdd/kb/_index.yaml` + `sdd/kb/<slug>/`; todo comando e molde citado por `.agents/skills/sdd-kb/…`;
  - camada da F4 com o bloco comum idêntico ao das 14 (agora são 15 com o bloco); `como-falar.md` com a pergunta do perfil (**não** recomendado);
  - `validate_kb.py`: mensagens do starter em inglês, exits 0/2/64; `--strict` reprova `implementacao` sem `teste`, `teste` de arquivo ausente e `teste` fora da raiz (a pasta acima de `sdd/kb/`; contenção pela forma do caminho, então link simbólico dentro do projeto passa); `sys.dont_write_bytecode`;
  - `gate.sh` reescrito (bash 3.2): monta 16 casos em `mktemp -d` a partir dos exemplos (4 aceitas, 12 rejeitadas com a razão conferida), confere o RULE_MAP do exemplo antes dos casos, diferencia `kb_normativo.py` quebrado, recusa rodar de uma cópia com `sdd-open:generated`; saída `RESULTADO: VERDE — 4 aceitas, 12 rejeitadas pelo motivo certo, RULE_MAP do exemplo em dia`.
- **`sdd/bin/kb-dominios.py`** (0/1/64): lê a linha `| **KB Domains** |` do `## Technical Context`; `nenhum` sozinho ou nomes de pasta de `sdd/kb/` (sem ocultas); vermelho com `🛑` por problema, os nomes que existem (até 10 + "e mais N"), `RESULTADO:` e `→`; verde lista `<domínio>: <REGRA> → <teste>` dos RULE_MAP (pipe escapado tratado). Não importa a `sdd-kb`.
- **`sdd-define` 2.3.0**: frase no passo 3 (KB Domains de `ls sdd/kb/` ou `nenhum`, estado vazio em 1 frase, `name:` ao lado do slug), `### 10. Conferir o KB Domains` em prosa (sem bloco cercado), linha no Quality Gate; `DEFINE_TEMPLATE.md` sem "ou equivalente".
- **`sdd-ux-review` 2.3.0**: 1 frase no passo 1 e `references/entrevista-publico.md` (público, frequência e aparelho, estágio, referência e URL como perguntas abertas; catálogo com "Uma referência sua"; Observado × Desejado × Recomendado; só a confirmação "Posso gravar este público em User and Context?" tem opções). O `UX_REVIEW_TEMPLATE.md` não mudou; a tabela WCAG fica para a W5 (anotado no DESIGN, Decision 6).
- **Testes**: `tests/test_sdd_kb_normativo.py` (62, porte com `-B`), `test_sdd_kb.py` (21), `test_kb_dominios.py` (22), `test_conversa.py` (+6: `EntrevistaPublico`, 17 skills); `test_skill_lint.py` 16 → 17; `test_matriz_new_session.PORTADAS` + `sdd-kb`. `docs/cli-conventions.md` com as saídas novas e a exceção do `validate_kb.py`. `MANIFEST.txt` +42. `.gitattributes` novo.
- **Evidência** em `sdd/reports/evidence/F5_CONHECIMENTO/`: scripts `gerar-evidencia.sh`, `sabotagem.sh`, `comandos-intactos.py`; logs `GATE`, `base-2fcdda1`, `baseline`, `baseline-notas`, `baseline-notas2`, `check-versions`, `comandos-intactos`, `contratos-intactos`, `codepoints`, `gate-kb`, `skill-lint-conversa`, `kb-dominios-proprio`, `testes-f5`, `sabotagem`, `escopo`, `linhas`, `ci-pr`, `release`, e os `AVAL-DESIGN-*`, `AVAL-*` e `AVAL2-*` dos revisores.
- **Release**: OK "release do sdd-open autorizado"; push fast-forward `2fcdda1..7e19462`; run `release` 40970012304 → https://github.com/robertodiasduarte/sdd-open/releases/tag/v2.2.6, tag em `7e19462`; SHA-256 de `sdd-open-v2.2.6.tar.gz` `5dedf04b5046574c44664f3e1daa72af5877859ebb7bba35da58cab0e842a114`, `shasum -a 256 -c` OK.

### Casos e testes em aberto

- **Piso:** `SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover -s tests -p 'test_*.py'` → 499 OK em `7e19462` (dentro do Verify Gate, 259 s). A base `2fcdda1` tinha 388.
- **Gate e versões:** `bash sdd/bin/verify-gate.sh --strict sdd/features/DEFINE_F5_CONHECIMENTO.md` → 0 em `bafc63c`, `0e0dba5` e `7e19462`. `check-versions --base v2.2.5 --base-obrigatoria` VERDE (17 skills).
- **Baseline vermelha:** 33 FAIL + 74 ERROR em 152 testes antes do código; 9 FAIL das notas do ciclo 1 contra `7e5b25c`; 4 FAIL das notas do ciclo 2 contra `0e0dba5`.
- **Sabotagem:** 4/4 (validador sem a regra de `teste`, `rule-map --check` permissivo, `gate.sh` que aceita caso ruim, `kb-dominios.py` que aceita nome sem pasta) vermelhas com o nome do teste e verdes depois do `git checkout`.
- **Conferência de fechamento** (inventário): o código roda (499 no piso e no CI ubuntu + macOS); os critérios combinados passam (gate 0, `report-lint` 0, `skill-lint --conversa` 17/17, gate da KB, 1 sabotagem por script, revisão sem HIGH aberto); as mudanças estão em `origin/main` e na tag `v2.2.6`, e os artefatos SDD na branch `docs/incorporar-starter`; o que ficou de fora está nas pendências.
- **Não verificado:** um agente real conduzindo a `sdd-kb`, a entrevista de público e o passo 10 da `sdd-define`. Os testes conferem só o texto e os scripts.

### Pendências

**🐛 Bug fix** — o que ficou quebrado, parcial ou com comportamento errado conhecido:

- nenhuma.

**✨ Feature improvement** — o que é incremento planejado, melhoria ou próxima etapa de escopo:

- **Conferência num agente real** (Codex CLI e Claude Code): `sdd-kb` num projeto vazio (cria `sdd/kb/`, roda o validador, traduz a saída), `sdd-define` com e sem `sdd/kb/` (passo 10), `sdd-ux-review` com DEFINE sem público (entrevista). Junta-se à pendência A-002 da F4.
- **README e `AGENTS.md.tmpl` não citam a `sdd-kb`** nem o `kb-dominios.py`: entra na F6 (plano 4.3), junto com as 3 skills da F2.
- **Risco aceito:** as mensagens do `validate_kb.py` e do `kb_normativo.py` ficam em inglês (`PASS:`/`FAIL:`/`WARN:`, exit 2): os 62 testes portados conferem o texto; a skill manda traduzir. Registrado em `docs/cli-conventions.md`.
- **Risco aceito:** o `kb-dominios.py` não exige o domínio registrado no `_index.yaml` (isso é do `validate_kb.py`) nem julga se o domínio é relevante para a feature.
- **Risco aceito:** DEFINE antigo com `KB Domains = N/A` reprova se alguém rodar o lint nele; a `sdd-define` só o roda no DEFINE que acabou de gravar.
- **Risco aceito:** o `.gitattributes` com `-text` só cobre `example-kb-normativo/fontes/` (o único lugar onde o byte importa: SHA-256).
- **Para a F9:** o bloco comum da camada está em **15** `SKILL.md` (as 14 da F4 + `sdd-kb`); trocar nas 15 e nas `FRASES` do `test_conversa`. A substituição em massa continua excluindo `sdd-iniciar-repo` e `sdd-higiene-dado`.
- **Para a W5 (item H):** a tabela WCAG 2.2 AA no `UX_REVIEW_TEMPLATE.md` e a leitura de `UX_REVIEW_*.md` anteriores.
- **Pendência herdada:** o `report-lint.py` com cabeçalho não reconhecido continua fail-open (F7); `RESUMO_ETAPA.md:4,49` cita `/adversarial-review` (F10).

### Próximos passos

1. **Sessão 4 — F6 Docs** (prompt em `sdd/handoffs/SESSION_PROMPT_INCORPORAR_STARTER.md`), na worktree já aberta `/Users/robertoduarte/rdd-worktrees/sdd-open-f6-docs` (branch `feat/f6-docs`, de `origin/main` = `7e19462`, com os artefatos SDD copiados). Pronto quando: `BRAINSTORM_F6_*.md` gravado; define, design, build e Release (ou push sem Release, se a F6 só tocar `docs/` e `README.md`) com o hash conferido quando houver Release.
2. **F7 → F14** e **F15** (plano, seções 8 e 10).

### Alertas — o que não quebrar

- **A `sdd-kb` agora é contrato testado:** `gate.sh` (4/12, linha única no verde), `TextoDaSkill` (nenhum caminho de fora, nenhum `scripts/validate_kb.py` sem `.agents/skills/sdd-kb/`, nenhum link relativo `](assets/`), `PORTADAS`, `EntrevistaPublico` (1 pergunta de decisão só). Mexer no exemplo normativo exige regerar o RULE_MAP e conferir as âncoras do `gate.sh`.
- **O `kb-dominios.py` lê só o `## Technical Context`**: renomear essa seção no `DEFINE_TEMPLATE.md` quebra o passo 10.
- **17 skills**: `test_skill_lint` e `test_conversa` contam; a F13 e a F14 sobem para 18 e 19 de propósito.
- **Evidência:** `report-lint` só aceita `evidence/<FEATURE>/` com o nome exato do relatório.
- Demais alertas das etapas F4, M1, W0 e F3 continuam valendo.

### Onde está o trabalho

- Remoto `https://github.com/robertodiasduarte/sdd-open.git`, `main` = `7e19462` = tag `v2.2.6`. Última Release: https://github.com/robertodiasduarte/sdd-open/releases/tag/v2.2.6.
- Worktree da sessão 3: `/Users/robertoduarte/rdd-worktrees/sdd-open-f5-conhecimento`. A branch `feat/f5-conhecimento` está em `7e19462`, já mesclada.
- Os artefatos SDD (`sdd/features|handoffs|reports|reviews`) estão gravados na branch `docs/incorporar-starter`.
- Limpeza, rodada de fora da pasta e só depois de gravar a branch `docs/`: `git -C /Users/robertoduarte/rdd-public/sdd-open worktree remove /Users/robertoduarte/rdd-worktrees/sdd-open-f5-conhecimento && git -C /Users/robertoduarte/rdd-public/sdd-open branch -d feat/f5-conhecimento`.

---

## 2026-10-29 — F4 Conversa (entregue, Release v2.2.5)

### O que foi feito

- **Fluxo SDD completo** (sessão 2, worktree `/Users/robertoduarte/rdd-worktrees/sdd-open-f4-conversa`, branch `feat/f4-conversa`):
  - artefatos: `sdd/features/BRAINSTORM_F4_CONVERSA.md`, `DEFINE_F4_CONVERSA.md` (v1.2, 22 ATs EARS, Clarity 14/15), `DESIGN_F4_CONVERSA.md` (v1.1, 10 decisões, 36 linhas no manifest) e `sdd/reports/BUILD_REPORT_F4_CONVERSA.md` (`report-lint` 0);
  - commits `4e77a1f` (build), `fd94876` (ciclo 1) e `2fcdda1` (ciclo 2), sobre `dd27ef6`;
  - PR https://github.com/robertodiasduarte/sdd-open/pull/6 (MERGED); 62 arquivos (35 novos e 27 alterados).
- **As 14 skills** (bump minor): auditoria-harness 1.1.0, brainstorm 2.1.0, build 2.2.0, checar-ambiente 1.4.0, define 2.2.0, design 2.1.0, governanca 2.2.0, handoff 2.1.0, iterate 2.1.0, new-session 1.2.0, playbook 2.1.0, prompt-builder 2.1.0, release 2.3.0, ux-review 2.2.0. Cada uma tem:
  - a seção `## Como falar com o aluno`, logo antes do 1º `## `. Ela traz 3 linhas de abertura, a tabela `| Etapa | Nome para o aluno | Passos desta skill |` e o **bloco comum de regras**, igual nas 14: as 5 partes, o Status começando pelo nome da fase (`Build: ✅ 1 Plano · ▶️ 2 Modo · …`) e o Próximo passo ≤100 caracteres;
  - `references/como-falar.md`, com glossário, Status preenchido e ≥1 exemplo com decisão (recomendada primeiro, **não sei**, sem **Outro**);
  - a linha de identificação ("uma vez só, antes do Status") e `metadata.updated: "2026-10"`;
  - sai o `> Abra a resposta com o banner` das 9 que o tinham.

  Casos próprios:
  - `sdd-design` ganha o `### 8. Conferir`, com `design-lint`;
  - `sdd-handoff` ganha o `### 3b. Conferir a ficha`, com `handoff-lint`;
  - na `sdd-checar-ambiente`, o Status vem antes do relatório do script, e a identificação continua na linha ✅.
- **`sdd/templates/fragments/PERGUNTA_DECISAO.md`**: dono único do formato.
  - Pergunta: `(recomendado)` primeiro com o porquê, números, `(ref: …)`, **não sei**, nunca **Outro**, eco de 1 linha, `[Dn]` reservado.
  - Parada ⏸️: **Por que parei:**, **Onde:**, **Passos:**, **O que não foi feito:**, **Brief:** e **Sessão nova:** (que a F9 liga ao `exit 40`).
- **`sdd/bin/skill-lint.py --conversa`**: sem a flag, só frontmatter, com a mensagem da `v2.2.4`. Com a flag, confere:
  - a seção (fora de bloco de código), a coluna `Etapa`, as 5 partes e o `como-falar.md` quando a seção manda lê-lo;
  - em cada pergunta de decisão do `como-falar.md` (negrito com `?` + opções `-`/`*`, também depois de linha em branco, em citação ou quebradas em 2 linhas): exatamente 1 `(recomendado)`, e ela é a 1ª; **não sei**; nada que comece por Outro/Outra/Outros;
  - `**Próximo passo**` ≤100 caracteres.

  As 7 fixtures ficam em `sdd/fixtures/conversa/` (controle + 6 que reprovam). O CI (`publish-gate.yml`, passo "Skill frontmatter") roda com `--conversa`.
- **`sdd/bin/design-lint.py`** (0/1/64): `## Key Decisions` com `### Decision N: <nome>` em sequência; File Manifest com `**Total Files:**` = linhas; dependências que existem, sem autodependência e sem ciclo; placeholder entre chaves fora de código (aspas angulares passam). Arquivo ilegível sai 1 com `RESULTADO:`.
- **`sdd/bin/handoff-lint.py`** (0/1/64): confere o mínimo do `HANDOFF_TEMPLATE.md` do open:
  - `# HANDOFF:`;
  - Ficha com Objetivo, Status e Verify Gate;
  - `## Prompt de retomada` com bloco, delimitada sem os blocos (só a ficha cujo Status **começa** por ✅ dispensa o prompt);
  - `### … — AAAA-MM-DD` no histórico;
  - placeholder; frases que dependem da conversa anterior (a lista está na docstring do lint).

  Seção extra passa, e `## Eventos` é opcional.
- **`tests/test_agnostico.py`**: reprova `AskUserQuestion`, `TodoWrite`, `PreToolUse`, `PostToolUse`, `subagent_type`, `Task tool`/`Agent tool` (sem caixa) e `/model`.
  - Varre todo arquivo de texto de `.agents/skills/`, `sdd/templates/`, `AGENTS.md.tmpl` e `sdd/playbook.md`.
  - Texto não-UTF-8 é achado; binário é pulado.
  - `CLARIFY.md:45` e `BUILD_REPORT_TEMPLATE.md:75` foram reescritos.
- **Outros testes:**
  - novos: `tests/test_conversa.py` (identificação = versão nas 16, sem banner, bloco comum nas 14, fragmento, passos 8/3b), `test_design_lint.py` e `test_handoff_lint.py`;
  - `test_skill_lint.py`: 8 → 32 testes;
  - versões esperadas atualizadas em `test_correcoes_w0`, `test_contrato_build_release` e `test_matriz_new_session`;
  - `test_release_workflow` passa a esperar `--conversa`.
- **Evidência** em `sdd/reports/evidence/F4_CONVERSA/`:
  - scripts: `gerar-evidencia.sh`, `sabotagem.sh` e `comandos-intactos.py`;
  - logs: `GATE`, `suite-piso`, `testes-f4`, `baseline`, `baseline-notas`, `baseline-agnostico`, `comandos-intactos`, `contratos-intactos`, `design-lint-reais`, `skill-lint-conversa`, `check-versions`, `codepoints`, `ci-pr`, `release`, e os `AVAL-*`/`AVAL2-*` dos avaliadores;
  - vereditos: `sdd/reviews/AVALIACAO_F4_CONVERSA_20261029-ciclo1.md` e `…-ciclo2.md`.
- **Sabotagem** (6, em `2fcdda1`):
  - `skill-lint` sem "não sei";
  - `design-lint` sem ciclo;
  - `handoff-lint` sem placeholder no prompt;
  - `test_agnostico` sem `AskUserQuestion`;
  - `como-falar.md` da build sem "não sei";
  - banner de volta na define.

  As 6 ficaram vermelhas com o nome do teste e verdes depois do `git checkout`.
- **Release**:
  - o CI do PR (run 40951200708) deu `gate` e `Testes no piso (macOS)` verdes, com 388 testes, integridade "0 finding(s) in 57 file(s)" e o passo com `--conversa`;
  - o Roberto respondeu "push sdd-open autorizado". Houve push fast-forward `dd27ef6..2fcdda1`;
  - a run `release` 40952893409 rodou `testes` e `testes-macos` antes de publicar → https://github.com/robertodiasduarte/sdd-open/releases/tag/v2.2.5, tag em `2fcdda1`;
  - SHA-256 de `sdd-open-v2.2.5.tar.gz`: `4686f3dafcb9decfeea66308055f3a9123e1413c6c5e6831855a6073a859e053`, com `shasum -a 256 -c` OK.

### Casos e testes em aberto

- **Piso:** `SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover -s tests -p 'test_*.py'` → 388 OK em `2fcdda1` (202 s). A base `dd27ef6` tinha 326.
- **Gate e versões:** `bash sdd/bin/verify-gate.sh --strict sdd/features/DEFINE_F4_CONVERSA.md` → 0 em `4e77a1f`, `fd94876` e `2fcdda1`. `check-versions --base v2.2.4 --base-obrigatoria` VERDE.
- **Baseline vermelha:**
  - os 9 módulos da F4, antes do código, deram 78 FAIL e 34 ERROR em 114 testes;
  - os testes das notas, contra os lints de `4e77a1f`, deram 10 FAIL;
  - o `test_agnostico` sobre `git archive v2.2.4` reprova `BUILD_REPORT_TEMPLATE.md:75: Task tool` e `CLARIFY.md:45: AskUserQuestion`.
- **Comandos e passos `v2.2.4` × HEAD nas 14:** só `+ passo ### 8. Conferir`/`+ cmd … design-lint.py …` (design) e `+ passo ### 3b. Conferir a ficha`/`+ cmd … handoff-lint.py …` (handoff).
- **Conferência de fechamento** (inventário):
  - o código roda: 388 testes no piso e no CI;
  - os critérios combinados passam: gate 0, `report-lint` 0, `test_agnostico` vermelho na `v2.2.4`, 1 sabotagem por script e revisão sem HIGH aberto;
  - as mudanças estão em `origin/main` e na tag `v2.2.5`, e os artefatos SDD na branch `docs/incorporar-starter`;
  - o que ficou de fora está nas pendências abaixo.
- **Não verificado:** a obediência de um agente real à camada (tom, ordem das 5 partes, leitura do `como-falar.md`). Os testes conferem só o texto escrito.

### Pendências

**🐛 Bug fix** — o que ficou quebrado, parcial ou com comportamento errado conhecido:

- nenhuma.

**✨ Feature improvement** — o que é incremento planejado, melhoria ou próxima etapa de escopo:

- **Conferência num agente real** (Codex CLI e Claude Code):
  - rodar `sdd-define`, `sdd-new-session` (num projeto sem git) e `sdd-release`;
  - ver o Status na 1ª linha, a identificação antes dele, a pergunta com `(recomendado)` e "não sei", e a parada ⏸️.

  É a pendência A-002 do DEFINE e não entra em gate.
- **Risco aceito:** o bloco comum de regras está copiado em 14 `SKILL.md`. O `test_conversa` segura 7 frases-chave; outra frase pode divergir. Quando a F9 reabrir as 13 skills, troque o bloco de uma vez, por substituição de texto.
- **Risco aceito:** o `skill-lint --conversa` não confere pergunta em lista numerada, com `__negrito__` ou com prosa entre a pergunta e as opções, porque ficam fora do formato do DEFINE (ciclo 2, LOW-2).
- **Risco aceito:** opção desconhecida no `skill-lint` (`--verbose`) sai 64. Na `v2.2.4`, ela virava caminho de arquivo e saía 1 (DESIGN, Decisão 2).
- **Pendência herdada:** o `report-lint.py` com cabeçalho não reconhecido continua fail-open (F7); `RESUMO_ETAPA.md:4,49` ainda cita `/adversarial-review` (F10).
- **Para a F5:** a `sdd-kb` nova precisa nascer com a seção e o `references/como-falar.md` no formato da F4, porque o CI roda `skill-lint --conversa` em toda `sdd-*`. O `test_conversa.F4` (14 nomes) e o `test_skill_lint` (16 → 17) mudam de propósito.

### Próximos passos

1. **Sessão 3 — F5 Conhecimento** (prompt em `sdd/handoffs/SESSION_PROMPT_INCORPORAR_STARTER.md`), numa worktree nova a partir de `origin/main` = `2fcdda1`. Pronto quando: `BRAINSTORM_F5_*.md` gravado com a decisão 4 do plano respondida pelo Roberto; depois define, design, build e Release com `SHA256SUMS.txt` conferido.
2. **F6 Docs**, depois **F7 → F14** e **F15** (plano, seções 8 e 10).

### Alertas — o que não quebrar

- **A camada é contrato testado:**
  - toda skill `sdd-*` precisa passar no `skill-lint --conversa`: seção, tabela `Etapa`, 5 partes e o `como-falar.md` com pergunta de decisão válida;
  - mudar uma das `FRASES` do bloco comum quebra o `test_conversa` nas 14;
  - mudar a versão de uma skill exige mudar a linha de identificação (`<nome> vX.Y.Z · `).
- **`PERGUNTA_DECISAO.md`** é o dono do formato. A W2/F9 preenche o `[Dn]` e liga o `exit 40` aos campos `Brief:`/`Sessão nova:`; não crie um 2º formato.
- **Os 2 lints novos** viajam para o projeto do usuário (`sdd/bin/`). O `handoff-lint` confere o template do **open**; o HANDOFF desta família está no formato do starter e reprova nele, o que é esperado.
- **Evidência:** o `report-lint` só aceita evidência em `evidence/<FEATURE>/`, com o nome exato do relatório (`F4_CONVERSA`, não `F4`).
- **A F4 não mexeu** em `sdd-iniciar-repo` nem `sdd-higiene-dado`. Uma substituição em massa nas skills tem de excluir as duas, ou elas sobem de versão.
- Demais alertas das etapas M1, W0 e F3 continuam valendo.

### Onde está o trabalho

- Remoto `https://github.com/robertodiasduarte/sdd-open.git`, `main` = `2fcdda1` = tag `v2.2.5`. Última Release: https://github.com/robertodiasduarte/sdd-open/releases/tag/v2.2.5.
- Worktree da sessão 2: `/Users/robertoduarte/rdd-worktrees/sdd-open-f4-conversa`. A branch `feat/f4-conversa` está em `2fcdda1`, já mesclada.
- Os artefatos SDD (`sdd/features|handoffs|reports|reviews`) estão gravados na branch `docs/incorporar-starter`.
- Limpeza, rodada de fora da pasta e só depois de gravar a branch `docs/`: `git -C /Users/robertoduarte/rdd-public/sdd-open worktree remove /Users/robertoduarte/rdd-worktrees/sdd-open-f4-conversa && git -C /Users/robertoduarte/rdd-public/sdd-open branch -d feat/f4-conversa`.

---

## 2026-10-29 — M1 Manutenção do CI (entregue, sem Release)

### O que foi feito

- **Escopo** (plano, seção 8, "Manutenção M1"; parâmetro P2): só `.github/workflows/publish-gate.yml`, `.github/workflows/release.yml` e `tests/test_release_workflow.py`. Nenhuma skill mudou de versão. Commits `eac5484` (build) e `dd27ef6` (notas da revisão), sobre `303cc87` = `v2.2.4`; branch `feat/m1`, PR https://github.com/robertodiasduarte/sdd-open/pull/5 (MERGED).
- **Piso no robô**: job `testes-macos` (`macos-latest`, `timeout-minutes: 20`) nos dois workflows. O passo "Floor versions (asserted)" sai ≠0 se `/usr/bin/python3` não for 3.9 ou `/bin/bash` não for 3.2. Ele também põe `$RUNNER_TEMP/piso/python3` (`exec /usr/bin/python3 "$@"`) na frente do `PATH`, então os scripts que chamam `python3` (`bin/sdd-open.sh`, `bin/lib/merge.sh`) também rodam no piso. O job instala o gitleaks 8.30.1 darwin_arm64 (`curl -fsSL`, `gitleaks version`), para nenhuma classe ser pulada, e roda `SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover -s tests -p 'test_*.py'`. No `release.yml`, o `release` passa a `needs: [testes, testes-macos]`.
- **Checkout**: `actions/checkout@11d5960a…` (v4.4.0, Node 20) → `actions/checkout@fbc6f3992d24b796d5a048ff273f7fcc4a7b6c09 # v5.1.0`, nos 3 `uses:`. É tag leve no commit, `using: node24`, conferida com `git ls-remote` e `gh api`.
- **Integridade das skills** (no lugar do "baseline da `sdd-auditoria-harness`", decisão do Roberto, ver `## Eventos`): passo "Skill integrity (invisible Unicode, remote code piped to a shell)" no job `gate` do `publish-gate.yml` e no job `testes` do `release.yml`. É um programa Python inline idêntico nos dois, com o argumento `.agents/skills`. Ele reprova:
  - Unicode invisível, bidi, de tag (U+E0000–E007F) ou seletor de variação (U+FE00–FE0E, U+E0100–E01EF), além de U+00AD, U+034F, U+061C, os fillers Hangul, U+180E, U+2028–202E e U+FFF9–FFFB;
  - `curl|wget … | sh/bash/zsh/dash/ksh/python/perl/ruby/node` (também com `sudo -E` e caminho absoluto), `base64 -d|-D|--decode … | sh`, `eval "$(curl…)"`, `bash <(curl…)`, `sh -c "$(curl…)"` e `source|. <(curl…)`;
  - arquivo não-UTF-8, e diretório ausente ou sem nenhum arquivo lido.

  O U+200D e o U+FE0F ficam de fora, porque montam emoji (55 usos de FE0F nas skills). As lacunas declaradas no comentário são `| tee x | sh`, pipe quebrado por `\` e PowerShell `iex`. Hoje dá 0 achados em 43 arquivos.
- **`tests/test_release_workflow.py`** 17 → 27 testes:
  - `PisoNoMacos`: job, piso afirmado, PATH, gitleaks, timeout e `needs`;
  - `IntegridadeDasSkills`: o programa é **extraído do workflow** e executado contra 19 amostras montadas com `chr()`, mais o controle com emoji ZWJ/FE0F e `| shasum`, o alvo vazio ou inexistente, o binário e as skills do `MANIFEST.txt`;
  - `test_checkout_e_o_v5_em_todo_job`.
- **Relatório**: `sdd/reports/BUILD_REPORT_M1.md` (`report-lint` 0). A evidência está em `sdd/reports/evidence/M1/`: `baseline.log`, `sabotagem.sh`/`.log`, `gerar-evidencia.sh`, `GATE.log`, `suite-piso.log`, `check-versions.log`, `deploy-espera-testes.log`, `checkout-v5.log`, `escopo.log`, `testes-m1.log` e `ci-pr5.log`.
- **Sabotagem** (8, em `dd27ef6`, revertidas com `git checkout`):
  - `release` sem `testes-macos` no `needs`;
  - job do piso em ubuntu;
  - um checkout de volta ao v4.4.0;
  - sem U+061C;
  - alvo vazio passando;
  - piso só impresso;
  - `source <(curl)` passando;
  - a varredura do gate sem `exit 1`.

  As 8 ficaram vermelhas com o nome do teste.
- **Publicação**: o Roberto respondeu "finalizar (push + deploy + verificar) sdd-open". Push fast-forward `303cc87..dd27ef6` em `main`. Só o `publish-gate` roda: run 40931927983 verde, com `gate` e `testes-macos` em success. Nenhuma run de `release.yml` em `dd27ef6`, então **não há tag nem Release** da M1 (`paths` do `release.yml`); a última Release continua `v2.2.4` (`evidence/M1/main-push.log`).

### Casos e testes em aberto

- CI do PR #5 (run 40929387392, `dd27ef6`): `gate` (ubuntu) 326 OK, com a varredura dando 0 achados em 43 arquivos; `testes-macos` 326 OK, 0 skip, `3.9.6 (default, May 22 2026, 11:13:45)` e `bash 3.2.57(1)-release` afirmados, `command -v python3` = `/Users/runner/work/_temp/piso/python3`. A suíte levou 219,8 s no macOS e 140 s no ubuntu.
- Piso local (Python 3.9.6, bash 3.2.57): 326 OK em 187,9 s. publish-gate ci 0; `check-versions --base v2.2.4` VERDE; `deploy-espera-testes.py .` SIM.
- Baseline: o `test_release_workflow` novo sobre `v2.2.4` dá 8 FAIL e 25 ERROR.
- Não verificado: a primeira run de `release.yml` com o `needs: [testes, testes-macos]` só acontece no próximo push que tocar os `paths` do produto (a F4); confira nela que o `release` esperou os dois jobs.

### Pendências

**🐛 Bug fix** — o que ficou quebrado, parcial ou com comportamento errado conhecido:

- nenhuma.

**✨ Feature improvement** — o que é incremento planejado, melhoria ou próxima etapa de escopo:

- Varredura de integridade também em `AGENTS.md.tmpl`, `sdd/templates/**` e `sdd/playbook.md` (nota 5 da revisão; o escopo declarado da M1 era `.agents/skills/`).
- Risco aceito: um texto de skill que **alerta** contra `curl … | sh` escrito literalmente reprova. A regra é descrever sem o padrão literal.
- Risco aceito: o `release` depende do runner macOS. Uma falha só do macOS deixa aquele push sem Release até um re-run ou um próximo push nos `paths`; como o repositório é público, os minutos não custam.
- Risco aceito: se o `macos-latest` deixar de trazer Python 3.9, o job reprova e a Release trava. Isso é de propósito (o piso deixou de ser provado); a saída é decidir o piso novo ou fixar a imagem.
- O gitleaks do job Ubuntu (anterior à M1) usa `curl -sSL`, sem `-f` e sem checksum.

### Próximos passos

1. **Sessão 2 — F4 Conversa** (prompt em `sdd/handoffs/SESSION_PROMPT_INCORPORAR_STARTER.md`), numa worktree nova a partir de `origin/main` = `dd27ef6`. Pronto quando: o BRAINSTORM da F4 estiver gravado com as decisões 2 e 3 da seção 5 do plano respondidas pelo Roberto.
2. **F4 — define, design, build e release**, com o ciclo das F1–F3. Pronto quando: `verify-gate.sh --strict` 0, `report-lint.py` 0, CI verde em ubuntu **e** macOS, e a Release com `SHA256SUMS.txt` conferido.
3. **F5 → F6**, depois **F7 → F14** e **F15** (plano, seções 8 e 10).

### Alertas — o que não quebrar

- **O CI agora tem 3 portas novas.** Texto novo de skill (a F4 escreve muito) não pode trazer caractere invisível nem `curl … | sh` literal; emoji com ZWJ e com FE0F passa. Toda release espera o macOS (~4 min a mais). O piso de 3.9 e 3.2 é **afirmado**: código que só roda em Python ≥3.10 quebra no CI.
- **Testes com Unicode invisível** montam a amostra com `chr()`, nunca com o caractere literal. Na sessão 1, um `\u200b` digitado virou o caractere de verdade ao passar pelo agente: confira os bytes depois de escrever (`python3 -c` contando os code points).
- **A M1 não gera tag.** O `check-versions` da F4 compara com `v2.2.4`.
- Demais alertas da etapa W0 e da F3 continuam valendo.

### Onde está o trabalho

- Remoto `https://github.com/robertodiasduarte/sdd-open.git`, `main` = `dd27ef6`. Última Release: https://github.com/robertodiasduarte/sdd-open/releases/tag/v2.2.4.
- Worktree da sessão 1: `/Users/robertoduarte/rdd-worktrees/sdd-open-w0-m1` (branches `feat/w0-m1` em `303cc87`, `feat/m1` em `dd27ef6`). Os artefatos SDD (`sdd/features|handoffs|reports`) estão gravados na branch `docs/incorporar-starter`.

---

## 2026-10-29 — W0 As 5 correções do porte (entregue, Release v2.2.4)

### O que foi feito

- **Escopo** (plano, seção 3.1; parâmetro P1): fix sem BRAINSTORM/DEFINE/DESIGN (regra "Quando pular o SDD formal" da `sdd-release`). Commits `b1df8c8` (build) e `303cc87` (notas da revisão), sobre `1a54da5` = `v2.2.3`; branch `feat/w0-m1`, PR https://github.com/robertodiasduarte/sdd-open/pull/4 (MERGED).
- **4.1** `.agents/skills/sdd-iterate/SKILL.md` 2.0.0 → 2.0.1. O passo 4 roda duas chamadas, nesta ordem:
  - `sdd/bin/verify-gate.sh --print <DEFINE>`: 0 = bloco presente, 64 = ausente. Não valida `kind`/`cmd` e é isento de marcador.
  - `sdd/bin/verify-gate.sh <DEFINE>`: 5 = voltar ao Define; 64 = corrigir o bloco; 0/2/3/4 não são deste passo, e a seta do vermelho não vale ali.

  Com `kind` smoke/eval ou `cmd` que grava, envia ou cobra, o passo procura o marcador pela forma canônica do `CLARIFY.md` em vez de rodar o gate.
- **4.2** sai a linha e o bullet "CONTEXTO de domínio" do `sdd/templates/DEFINE_TEMPLATE.md` (volta na F12). No `sdd/config.example.yaml`, os dois "(slice 2)" saem; o comentário de `layers` diz que `sql` também decide migration, e o de `editor`/`worktree_base` aponta a `sdd-new-session`.
- **4.3** sai `/drive` de `sdd/templates/fragments/CLARIFY.md`, `sdd/templates/DEFINE_TEMPLATE.md` e `sdd/templates/fragments/VERIFY_GATE.md` (a skill volta na F14).
- **4.4** `sdd/templates/fragments/EVIDENCIA.md` e `sdd/templates/BUILD_REPORT_TEMPLATE.md` apontam `sdd/bin/report-lint.py` (o guard `.githooks/claude-build-report-guard.py` volta na F7). O EVIDENCIA.md muda em quatro pontos:
  - os 13 "o hook" viram "o lint";
  - a regra 4 ("falha ABERTO … `systemMessage`") vira "falha FECHADO em erro interno";
  - passa a dizer que o lint acha a tabela pelo cabeçalho (coluna `Evid…` + `Resultado`/`Status`/`Passou`): cabeçalho em inglês sai 0 sem conferir;
  - `pass`/`verde` também contam como `true`.

  Ainda nos templates: "Step 1.5" vira "passo 1.5 da `sdd-build`" (`BUILD_REPORT_TEMPLATE.md`, `DESIGN_TEMPLATE.md`), e "§6.3 do PLANO" vira o `contexto-fresco.md`.
- **4.5** `.agents/skills/sdd-build/references/contexto-fresco.md` (com a `sdd-build` 2.1.0 → 2.1.1): os dois briefs dizem "Não edite código nem documento do projeto: o único arquivo que você grava de propósito, pelo shell, é `sdd/reports/evidence/{F}/AVAL-*.log`".
- **Vizinhos corrigidos pela revisão**: `CLARIFY.md` ("Lido pela `sdd-define` (passo 6)"), `sdd/templates/fragments/EARS.md` (sem `/define` (Step 4.5) e sem `/bug-pipeline`) e `DEFINE_TEMPLATE.md:91` (sem `AskUserQuestion`).
- **`tests/test_correcoes_w0.py`** (12 testes, novo no `MANIFEST.txt`): executa as chamadas **escritas** no passo 4 sobre `sdd/fixtures/DEFINE_FIXTURE_NEEDS_CLARIFICATION.md` (5) e `DEFINE_FIXTURE_CONTROLE.md` (≠5). Também varre todo arquivo do `MANIFEST.txt` atrás de `build-report-guard|/drive|Step 1\.5|slice 2|CONTEXTO de domínio|/bug-pipeline|`/define` \(Step`, e confere os briefs e as versões. `tests/test_contrato_build_release.py` passa a esperar a `sdd-build` 2.1.1.
- **Relatório**: `sdd/reports/BUILD_REPORT_W0.md` (`report-lint` 0, 7 ATs). A evidência está em `sdd/reports/evidence/W0/`: `baseline.log`, `sabotagem.sh`/`.log`, `gerar-evidencia.sh`, `W0-4.1-fixture.log`, `W0-testes.log`, `W0-grep.log`, `GATE.log`, `suite-piso.log`, `check-versions.log`, `contratos-intactos.log` e `release.log`.
- **Sabotagem** (8, em `303cc87`): passo 4 só com `--print`; "(slice 2)" de volta; `/drive` no `CLARIFY.md`; guard no `EVIDENCIA.md`; "O hook `build-report-guard`" no template; `/drive` no `AGENTS.md.tmpl`; aviso de smoke/eval removido; "Não escreva em arquivo algum". As 8 ficaram vermelhas e voltaram ao verde.
- **Release**: CI do PR #4 (run 40926042337) com 316 OK, publish-gate verde e check-versions VERDE. O Roberto respondeu "ok \"sdd-open\"". Push fast-forward `1a54da5..303cc87`, run `release` 40926754472 → https://github.com/robertodiasduarte/sdd-open/releases/tag/v2.2.4, tag em `303cc87`, SHA-256 de `sdd-open-v2.2.4.tar.gz` `b8a0aab0d58b87050d80c68813c868f6a2d4f9784fe7130ad663efc63a555670`, `shasum -a 256 -c` OK.

### Casos e testes em aberto

- Piso: `SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover -s tests -p 'test_*.py'` → 316 OK em `303cc87` (192 s).
- Baseline: o `test_correcoes_w0` sobre `v2.2.3` dá 9 FAIL de 12. Os 3 verdes caracterizam o `verify-gate.sh`, que não mudou.
- Contratos intactos: `git diff v2.2.3 HEAD -- sdd/bin/ sdd/fixtures/ scripts/ .github/` vazio; `playbook-lint.sh --self-test` 0.
- Conferência de fechamento (inventário):
  - o código roda: 316 testes no piso e no `ubuntu-latest`;
  - os critérios combinados passam: grep sem hit, fixture 0/5, publish-gate 0, check-versions 0, revisão sem HIGH aberta;
  - as mudanças estão em `origin/main` e na tag `v2.2.4`, e os artefatos SDD na branch `docs/incorporar-starter`;
  - o que ficou de fora está nas pendências abaixo.
- Não verificado: a obediência do agente ao passo 4 novo da `sdd-iterate` (só o texto e as chamadas escritas são testados).

### Pendências

**🐛 Bug fix** — o que ficou quebrado, parcial ou com comportamento errado conhecido:

- `sdd/bin/report-lint.py` sai 0 quando nenhuma tabela tem o cabeçalho reconhecido mas há linhas `AT-nnn` com `true` (nota 4 da revisão; reproduzido com `| ID | Criterion (EARS) | Result | Evidence |`). Hoje está só **documentado** no `EVIDENCIA.md`. A correção (fail-closed) muda o contrato de `sdd/bin/` e fica para a **F7**.

**✨ Feature improvement** — o que é incremento planejado, melhoria ou próxima etapa de escopo:

- `sdd/templates/fragments/CLARIFY.md:45` ainda diz `AskUserQuestion`; o `tests/test_agnostico.py` da F4 (item G) pega.
- `sdd/templates/fragments/RESUMO_ETAPA.md:4,49` cita `/adversarial-review`, que o pacote não tem; fica para a F10 (a Decisão 3 manda deixar o kanban intacto).
- Templates citam `/build`, `/define`, `/design` (forma curta da fase) e não `/sdd-build`; a F4 reescreve a camada de conversa.

### Próximos passos

1. Ver a etapa M1, acima: a F4 Conversa é a próxima.

### Alertas — o que não quebrar

- O passo 4 da `sdd-iterate` e os briefs de `contexto-fresco.md` são conferidos por `tests/test_correcoes_w0.py`. Se a F4 reescrever essas skills, mantenha as duas chamadas `sdd/bin/verify-gate.sh … <DEFINE>` entre crases, o aviso de smoke/eval e a frase "o único arquivo que você grava de propósito, pelo shell, é `sdd/reports/evidence/{F}/AVAL-*.log`", ou atualize o teste de propósito.
- Nenhum arquivo do `MANIFEST.txt` pode citar `/drive`, `build-report-guard`, `CONTEXTO de domínio`, "Step 1.5", "slice 2", `/bug-pipeline` ou "`/define` (Step". Quando a F7, a F12 ou a F14 trouxer o mecanismo de volta, o teste muda junto.
- `sdd-iterate` 2.0.1 e `sdd-build` 2.1.1: o `check-versions` da F4 compara com `v2.2.4`.

### Onde está o trabalho

- Ver a etapa M1, acima (mesma worktree e mesmo remoto).

---

## 2026-10-29 — F3 Build e Release (entregue, Release v2.2.3)

### O que foi feito

- **Fluxo SDD da F3** (artefatos não rastreados, nesta worktree): `sdd/features/BRAINSTORM_F3_BUILD_RELEASE.md` (abordagem A — tudo numa release; 15 decisões; 8 cortes YAGNI; 2 checkpoints), `sdd/features/DEFINE_F3_BUILD_RELEASE.md` (23 ATs EARS, Clarity 14/15, `verify-gate.sh --print` 0, `validate_define.py` PASS), `sdd/features/DESIGN_F3_BUILD_RELEASE.md` v1.1 (14 arquivos, 7 ADRs, `validate_design.py` PASS), `sdd/reports/BUILD_REPORT_F3_BUILD_RELEASE.md` (Complete; `report-lint.py` 0; `validate_build_report.py` PASS; evidência em `sdd/reports/evidence/F3_BUILD_RELEASE/`: `AT-001.log`…`AT-023.log`, `GATE.log`, `GATE-1-vermelho.log`, `baseline.log`, `suite-piso.log`, `release.log`, `sabotagem.sh`, `gerar-at.sh`).
- **Código em `main`** (commits `8c1a593` build, `af8b0e3` teste fora de git, `1a54da5` notas da revisão):
  - `sdd/bin/report-lint.py` — `problema_do_log()` extraída de `evidence_ok()` sem mudar mensagens; regra nova: migration (1º caminho entre crases de uma linha de tabela em seção `## Files…`/`## Arquivos…`/`…Manifest…`, também numerada ou com prefixo `… —`; termina em `.sql`, tem `migrations/` ou casa `layers.sql` do `sdd/config.yaml`; linha com Delete/Removido ignorada) exige linha em `## Migrations aplicadas` com o mesmo caminho, projeto `nome · ref`, data `AAAA-MM-DD` (ou "já aplicada em …") e prova = log de `evidence/<F>/` com `$ ` ou `recibo: nome AAAA-MM-DD`; "exit 0" e declaração reprovam. Relatório sem migration não muda.
  - `.agents/skills/sdd-release/scripts/deploy-espera-testes.py` (423 linhas, `100755`, só stdlib, mini-parser de YAML) — `SIM` 0 · `NAO` 1 · `NAO_SEI` 2 · `NAO_SE_APLICA` 3 · 64 uso; teste só em posição de comando (instalar `pytest` não é testar); `continue-on-error`, `|| true`, pipe sem pipefail, `set +e … exit 0`, `if: always()` no passo, no job ou num job do meio do `needs:` ⇒ NAO; `workflow_run`, reutilizável, teste com `if:`, `set +e`, job com nome de deploy não reconhecido, arquivo que não abre ⇒ NAO_SEI. Na raiz do sdd-open dá SIM; no `/Users/robertoduarte/RDD/Wordpress` dá NAO (`deploy-hostinger.yml · job deploy-production`, passo 'Sync theme patch').
  - `.agents/skills/sdd-release/SKILL.md` 2.1.0 → 2.2.0 — item 7 da FASE 1 = bloco único do OK (O que sobe · O que muda em produção · O push publica sozinho? · O deploy espera os testes? · Banco · Verificações · Veredito · Ledger · "Posso finalizar (push + deploy + verificar)?"); 0a.5 e item 10 citam a regra e o script.
  - `.agents/skills/sdd-build/SKILL.md` 2.0.0 → 2.1.0 (passo 4b) + `references/aplicar-migration.md` (206 linhas; porte do starter sem `sdd/ambiente.md`; CNPJ literal virou `<valor de teste>`; log `MIG-nnn.log` ou recibo).
  - `sdd/templates/BUILD_REPORT_TEMPLATE.md` (seção condicional `## Migrations aplicadas`), `sdd/templates/fragments/EVIDENCIA.md` (parágrafo "Migration aplicada"), `sdd/playbook.md` (`LM-004`, `promovido_para: sdd/bin/report-lint.py`).
  - `bin/sdd-open.sh` — `versao_skill()` (aspas simples, duplas ou nenhuma), `versao_menor()` (awk), e no `doctor`: ⚠️ `<skill> <vp> no projeto, <vq> no pacote — para receber: apague .agents/skills/<skill> e rode init (edições suas nela se perdem)`; ⚠️ `sdd/bin/<f> difere do pacote — se você não editou, apague e rode init`; ✅ `skills e sdd/bin/ em dia com o pacote`; exit 0.
  - `tests/` — `test_report_lint.py` (+18 em `Migrations`), `test_deploy_espera_testes.py` (29), `test_sdd_open.py` (+3 de `doctor`), `test_contrato_build_release.py` (12). Total **304**. `MANIFEST.txt` 110 → 114.
- **Nada de `sdd/bin/verify-gate.sh`, `sdd/fixtures/`, `scripts/publish-gate*` ou `.github/` mudou** (`git diff --stat v2.2.2 HEAD -- …` vazio, `evidence/F3_BUILD_RELEASE/AT-022.log`).
- **Sabotagem** (3, em `1a54da5`, revertidas com `git checkout`): `report-lint.py` sem a violação de linha ausente → `test_migration_sem_linha_reprova`, `test_migration_sem_a_secao_reprova` e mais 2 (+4 subtests); script sem `continue-on-error` do passo → `test_continue_on_error_no_passo_de_teste_nao_segura`; `doctor` sem o `cmp` → `test_doctor_avisa_sdd_bin_diferente_do_pacote`. Todas verdes depois.
- **Release**: PR https://github.com/robertodiasduarte/sdd-open/pull/3 (CI run 40912938021: publish-gate verde, `Ran 304 tests`, check-versions VERDE) → OK do Roberto ("push do sdd-open autorizado") → push fast-forward → run 40915091971 → https://github.com/robertodiasduarte/sdd-open/releases/tag/v2.2.3, tag em `1a54da5`, SHA-256 de `sdd-open-v2.2.3.tar.gz` `635e30050b83188f5965ffa5ddd09fac496973dc4a66d7bbd6391c9eb1ffd777`, `shasum -a 256 -c` OK.

### Casos e testes em aberto

- Verify Gate: `bash sdd/bin/verify-gate.sh --strict sdd/features/DEFINE_F3_BUILD_RELEASE.md` → exit 0 em `1a54da5` (G1–G5 verdes na cópia de `git archive HEAD`, `Ran 304 tests … OK` no `python3` 3.15 do PATH). Log: `sdd/reports/evidence/F3_BUILD_RELEASE/GATE.log`.
- Piso: `SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover -s tests -p 'test_*.py'` → 304 OK em `1a54da5` (Python 3.9.6, bash 3.2.57), ~3,1 min; 129 s no CI.
- Casos do revisor: `/private/tmp/claude-501/-Users-robertoduarte-rdd-worktrees-sdd-open-incorporar-starter/b8371a83-c760-4658-af04-e6321f52e2df/scratchpad/de_casos.py` (15 workflows; some quando o `/private/tmp` for limpo) — depois de `1a54da5`, 0 SIM falso; casos 3, 6, 8 e 11 dão NAO_SEI onde o revisor esperava NAO (aceito: não afirma o que não sabe).
- Conferência de fechamento (inventário): o código roda (304 testes local no piso e no `ubuntu-latest`); os critérios combinados passam (gate `--strict` 0, `report-lint` 0, 23 ATs com log, 3 sabotagens); as mudanças estão em `origin/main` = `1a54da5` = tag `v2.2.3`, e os artefatos SDD em `sdd/features|reports|handoffs` desta worktree (não rastreados, de propósito); o que ficou de fora está nas pendências abaixo.
- Não verificado: a obediência do agente à `sdd-build` 2.1.0 e à `sdd-release` 2.2.0 (A-003 do DEFINE: só o contrato escrito é testado); o bloco do OK num projeto real com migration aplicada de verdade.

### Pendências

**🐛 Bug fix** — o que ficou quebrado, parcial ou com comportamento errado conhecido:

- nenhuma no sdd-open. (Fora desta frente, no starter: `README.md` e `docs/quickstart*.md` ainda apontam para `robertodiasduarte/specgate`.)

**✨ Feature improvement** — o que é incremento planejado, melhoria ou próxima etapa de escopo:

- F4 Conversa — próxima (ver Próximos passos e o prompt de retomada).
- Risco aceito (nota 11 da revisão, rebatida): teste pgTAP em `*.sql` (`supabase/tests/*.sql`, `tests/security/*.sql`) listado nos arquivos do relatório passa a exigir linha em `## Migrations aplicadas`. Contorno hoje: não listar o teste como `.sql` na tabela de arquivos. Melhoria possível: excluir caminhos com segmento `tests/` — muda o contrato "`*.sql` = migration" do DEFINE, então pede decisão.
- Risco aceito (nota 10, em parte rebatida): o lint só vê o 1º caminho entre crases de cada linha e isenta a linha com uma célula "removido" em qualquer coluna (Decisão 1 do DESIGN; 1 linha afetada em 250 relatórios reais).
- Risco aceito: o `deploy-espera-testes.py` é heurística; o que ele não entende vira NAO_SEI (a skill então lê os workflows e escreve "não consegui afirmar"). Teste rodado por script próprio (`./ci.sh`) dá NAO_SEI.
- Para depois: o `doctor` avisa, mas o caminho para atualizar continua "apague e rode init" — um verbo `upgrade` com backup é redesenho da CLI (fora de escopo até aqui). Ligar `checar.sh --segredo` ao `release.landmines_cmd`; README e `AGENTS.md.tmpl` citando as 3 skills da F2 e o bloco do OK (F6).
- Carregados da F1/F2: trocar o pin `actions/checkout@11d5960a…` (v4.4.0, Node 20 depreciado) por SHA de v5 nos dois workflows; observar o CI no Ubuntu 26; tag manual e push de `main` no mesmo commit podem deixar duas tags (para minor/major, empurrar a tag depois da run de `main`); guia do aluno não rastreado em `/Users/robertoduarte/rdd-public/sdd-starter/docs/guia-do-aluno.pt-BR.md` (494 linhas, entrada da F6 — um `git clean` naquele checkout o apaga); `checar.sh` rodado de subpasta sugere `git rm --cached` com caminho relativo à raiz (nota 6 da F2).

### Próximos passos

0. **Sessão 1 em worktree limpa (prompt em `sdd/handoffs/SESSION_PROMPT_INCORPORAR_STARTER.md`): W0 + M1.** A ordem da W0 antes da F4 ficou decidida com o agrupamento da seção 10 do plano. **Fazer a W0**: 5 correções da seção 3.1 do plano, cada skill tocada com bump (`sdd-iterate`, `sdd-build`) e teste em `tests/`. Pronto quando: `verify-gate.sh sdd/fixtures/DEFINE_FIXTURE_NEEDS_CLARIFICATION.md` (sem `--print`) sai 5 por teste, e `grep -rnE 'claude-build-report-guard|/drive|Step 1\.5|slice 2' sdd/ .agents/` não acha nada; Release publicada.
1. **F4 Conversa — brainstorm** com `sdd-brainstorm`, gravando `sdd/features/BRAINSTORM_F4_CONVERSA.md`, com o plano consolidado (seção 4.1, itens A–F) como entrada. Entradas: seção `## Como falar com o aluno` + `references/como-falar.md` nas 13 skills nativas (fonte no starter `17c69c4` para 7: brainstorm, build, define, design, handoff, new-session, release; escrever do zero para 6: auditoria-harness, governanca, iterate, playbook, prompt-builder, ux-review); `skill-lint.py` conferindo a seção; `design-lint.py` e `handoff-lint.py` em `sdd/bin/` (reescrita a partir de `skills/sdd-design/scripts/validate_design.py` e `skills/sdd-handoff/scripts/validate_handoff.py` do starter); `metadata.updated` + linha de identificação nas 13. Pronto quando: abordagem confirmada, YAGNI, 2 checkpoints.
2. **F4 — define, design, build** com o mesmo `verify_gate` da F3; manifest com `MANIFEST.txt`; commit antes do gate; diff por skill provando que comandos e ordem dos passos não mudaram. Pronto quando: `verify-gate.sh --strict` 0, `report-lint.py` 0, 1 sabotagem por script alterado.
3. **F4 — release**: PR, CI verde, OK citando "sdd-open", push em `main`. Pronto quando: `gh release view` mostra `SHA256SUMS.txt` e o hash confere.
4. **F5 → F6**, mesmo ciclo; depois **F7 → F14** na ordem da seção 8 do plano (F7 Evidência depende da W0; F8 de F7; F9 de F4 e F7; F10 de F9; F11 de F10; F12 de F7 e F9; F13 de F5 e F7; F14 de todas); por fim **F15** no repositório privado (parâmetro P4). M1 vai junto com a W0 na sessão 1.

### Alertas — o que não quebrar

- **A branch `docs/incorporar-starter` nunca vai para `main`**: ela carrega os artefatos SDD do desenvolvimento do próprio Open (caminhos `/Users/`, sem `MANIFEST.txt`); em `main` iriam para o pacote que o aluno baixa e o G2/G3 reprovariam. O CI não roda nela (só `main` e PR). Nunca abrir PR dela.
- **W0 × F4 tocam os mesmos arquivos** (`.agents/skills/sdd-iterate/SKILL.md`, `.agents/skills/sdd-build/references/contexto-fresco.md`, `sdd/templates/fragments/{CLARIFY,VERIFY_GATE,EVIDENCIA}.md`, `sdd/templates/{DEFINE,BUILD_REPORT}_TEMPLATE.md`): não rodar as duas em paralelo.
- **O `report-lint` agora lê arquivos e migrations**: qualquer mudança no template do BUILD_REPORT (F4 pode mexer) mantém `## Files…` e `## Migrations aplicadas` com as colunas Arquivo · Projeto (nome · ref) · Aplicada em · Prova por leitura; `tests/test_contrato_build_release.py` confere.
- **O bloco do OK da `sdd-release`** tem os rótulos e a ordem conferidos por `test_contrato_build_release.SddRelease` (uma pergunta só, na última linha). A camada de conversa da F4 entra **em volta** do bloco, sem renomear rótulo nem acrescentar pergunta.
- **Skill alterada sobe versão** (`sdd-build` 2.1.0, `sdd-release` 2.2.0, demais como em `.agents/skills/*/SKILL.md`): `check-versions.py --base v2.2.3 --base-obrigatoria`. Se o clone não tiver a tag: `GIT_TERMINAL_PROMPT=0 git fetch -q origin tag v2.2.3`. A F4 muda as 13 ⇒ 13 bumps.
- **O `doctor` passa a avisar** projeto com skill mais velha que o pacote: depois da F4, toda instalação existente verá 13 avisos — é o comportamento esperado.
- **Literais do G2**: e-mail só em `example.com/.org/.net`; `git@host`, CPF, CNPJ, telefone e qualquer sequência de 11+ dígitos (timestamp de migration!) montados em tempo de execução; hosts em `.invalid`.
- **Testes que dependem de git** rodam numa sandbox com `git init` (`apoio.Sandbox.repo()`): a cópia do Verify Gate vem de `git archive` e não tem `.git`.
- **Modo de arquivo**: `bin/sdd-open.sh` e `sdd/bin/report-lint.py` são `100644` no índice; `deploy-espera-testes.py` é `100755`. Não fazer `chmod` em massa.
- Demais alertas continuam valendo (`GIT_TERMINAL_PROMPT=0`, push em `main` só com OK citando "sdd-open", `MANIFEST.txt` em `LC_ALL=C`, `python3 -B`, `git add` por nome, bash 3.2, sem zsh/symlink, `sync` idempotente, 16 skills em `tests/test_skill_lint.py`).

### Onde está o trabalho

- Worktree `/Users/robertoduarte/rdd-worktrees/sdd-open-incorporar-starter`, branch `feat/incorporar-starter` em `1a54da5` = `origin/main` = tag `v2.2.3`. Não rastreados nela: `sdd/features/`, `sdd/handoffs/`, `sdd/reports/` — **versionados na branch `docs/incorporar-starter`** (tag `docs-2026-10-29`), nunca mesclada em `main`; cada sessão nova os recupera com `git checkout docs/incorporar-starter -- sdd/features sdd/handoffs sdd/reports && git rm -r -q --cached sdd/features sdd/handoffs sdd/reports` e, ao fechar, grava a etapa nova lá (comandos no prompt de retomada).
- Plano do programa: `sdd/features/PLANO_F4_F15_CONSOLIDADO.md` v1.3 (parâmetros P1–P4, F4–F15, slots, fontes, agrupamento por sessão).
- Release: https://github.com/robertodiasduarte/sdd-open/releases/tag/v2.2.3 · PR #3 merged.
- Fonte da F4: `/Users/robertoduarte/rdd-public/sdd-starter` (main `17c69c4`): `skills/*/SKILL.md` (seção `## Como falar com o aluno`), `skills/*/references/como-falar.md`, `sdd/DEFINE_LINGUAGEM_ALUNO.md` (193 linhas, os 10 itens da camada), `skills/sdd-design/scripts/validate_design.py` (212 linhas), `skills/sdd-handoff/scripts/validate_handoff.py` (94), `skills/sdd-handoff/scripts/gate.sh` (32).

---

## 2026-10-29 — F2 Terreno (entregue, Release v2.2.2)

### O que foi feito

- **Fluxo SDD da F2** (artefatos não rastreados, nesta worktree): `sdd/features/BRAINSTORM_F2_TERRENO.md` (abordagem A — transplante com adaptação mínima; 15 decisões; 9 cortes YAGNI; 2 checkpoints), `sdd/features/DEFINE_F2_TERRENO.md` (21 ATs EARS, Clarity 14/15, `verify-gate.sh --print` 0 e `validate_define.py` PASS), `sdd/features/DESIGN_F2_TERRENO.md` v1.1 (22 arquivos, 7 ADRs, `validate_design.py` PASS), `sdd/reports/BUILD_REPORT_F2_TERRENO.md` (Complete; `report-lint.py` 0; `validate_build_report.py` PASS; evidência em `sdd/reports/evidence/F2_TERRENO/`: `AT-001.log`…`AT-021.log`, `suite-piso.log`, `release.log`, `sabotagem.sh`).
- **Código em `main`** (commits `4ee5470` build, `41c6169` notas da revisão):
  - `.agents/skills/sdd-checar-ambiente/` 1.3.0 — `SKILL.md` + `scripts/checar.sh`: porte do starter 1.2.0; `dado_exposto()` extraída da seção 6 e filtrada por pathspec `:(glob,icase)**/.env`, `**/.env.*`, `**/*.pfx`, `**/*.p12` + `grep --cached "PRIVATE KEY"` em `*.pem`; modo novo `--segredo` (só o bloco `🔴 Dado exposto`, sem rede, exit 1 com achado / 0 sem); `voce@example.com`; identificação aponta `sdd-open/releases/latest`.
  - `.agents/skills/sdd-higiene-dado/` 1.1.1 — `alarme.sh instalar` tira as linhas `sdd-open:generated` (o hook da cópia de `.claude/skills/` sai igual byte a byte ao da fonte); `pre-commit.sh`, `manifest.json`, `evals/cases.json`, `CHANGELOG.md` (entrada 1.1.1), 3 `references/` literais.
  - `.agents/skills/sdd-iniciar-repo/` 1.1.1 — `SKILL.md` + `scripts/inventario.sh`; `npx … sdd-starter` trocado pela `sdd-higiene-dado` que volta com o `init`.
  - Nenhuma das 3 tem `agents/openai.yaml` (o `doctor` usa esse arquivo para avisar "skills do sdd-starter detectadas").
  - `bin/sdd-open.sh` — fim de `doctor()`: roda o `.agents/skills/sdd-checar-ambiente/scripts/checar.sh --segredo` do pacote a partir da raiz do projeto; ⚠️ por achado (no stderr) com comando e medida; `✅ nenhum segredo salvo no git (…)`; ⚠️ "pacote incompleto" sem o script; continua exit 0 com `RESULTADO`.
  - `.agents/skills/sdd-new-session/SKILL.md` 1.0.0 → 1.1.0 (262 linhas): Passo 0 por `checar.sh --frente` (exit 1 para e traduz; exit 0 com `✅ Pronto para abrir a frente: repo <r>, principal <b>` segue; resto ⇒ pré-voo à mão); tabela "Como traduzir cada achado" com 17 trechos literais + "Qualquer outro achado"; Passo 1 descobre os 5 slots (`default_branch` cheio que diverge do remoto ⇒ para e pergunta; `test_cmd`/`lint_cmd` só com evidência literal: workflow > `package.json` > `Makefile`); Passo 2 item 6 grava só slot vazio no `sdd/config.yaml` da frente com `# descoberto por sdd-new-session (AAAA-MM-DD): <evidência>`, sem commit.
  - `tests/` — `test_checar.py` (53 portados + 4), `test_alarme.py` (28 + 1, git isolado), `test_inventario.py` (24), `test_matriz_new_session.py` (12: matriz script×tabela nos dois sentidos, contrato da `new-session`, portadas sem starter/`openai.yaml`/`tests/`), `test_sdd_open.py` (+5), `test_skill_lint.py` (16 skills). Total **242**.
  - `MANIFEST.txt` 93 → 110 linhas.
- **Nada de `sdd/`, `scripts/publish-gate*` ou `.github/` mudou**: `git diff v2.2.1 41c6169 -- sdd/ scripts/publish-gate.sh scripts/publish-gate-patterns.txt .github/` vazio.
- **Sabotagem** (5, em `41c6169`, revertidas com `git checkout`): `checar.sh` sem `*.p12` → `test_p12_e_env_variante` + `test_acusa_cada_tipo_e_sai_1`; `alarme.sh` sem o filtro → `test_hook_da_copia_gerada_sem_cabecalho_e_igual_ao_da_fonte`; `pre-commit.sh` aceita qualquer 2º DV de CPF → `test_digito_errado_nao_bloqueia`; `inventario.sh` `LIMITE_MB=500` → 4 testes; `doctor` sem `--segredo` → 2 testes. Todas verdes depois.
- **Release**: PR https://github.com/robertodiasduarte/sdd-open/pull/2 (CI run 40899262016: publish-gate verde, `Ran 242 tests`, version gate VERDE com 16 skills) → OK do Roberto → push fast-forward → run 40900694496 → https://github.com/robertodiasduarte/sdd-open/releases/tag/v2.2.2, tag em `41c6169`, SHA-256 de `sdd-open-v2.2.2.tar.gz` `fc7737a35c6252c428f6fd5614cc6d6a37560732e74345e3dea9ea3e3c8d164a`, `shasum -a 256 -c` OK.

### Casos e testes em aberto

- Verify Gate: `bash sdd/bin/verify-gate.sh --strict sdd/features/DEFINE_F2_TERRENO.md` → exit 0 em `41c6169` (G1–G5 verdes na cópia de `git archive HEAD`, `Ran 242 tests … OK`). Log: `sdd/reports/evidence/F2_TERRENO/AT-001.log`.
- Piso: `SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover -s tests -p 'test_*.py' -v` → 242 OK, 0 skip (Python 3.9.6, bash 3.2.57). Tempo da suíte ~2,9 min local, 131 s no CI; `test_checar.py` sozinho ~100 s (casos que esperam o teto de 10 s do `alcance`).
- Medição do `--segredo`: repo com 5.000 arquivos rastreados, 11,7 s antes da nota 2, 0,056 s depois; `test_repositorio_grande_continua_rapido` (3.000 arquivos, < 3 s) protege.
- Conferência de fechamento (inventário): o código roda (242 testes local no piso e no `ubuntu-latest` do CI); os critérios combinados passam (gate `--strict` 0, `report-lint` 0, 21 ATs com log, 5 sabotagens); as mudanças estão em `origin/main` = `41c6169` = tag `v2.2.2`, e os artefatos SDD em `sdd/features|reports|handoffs` desta worktree (não rastreados, de propósito); o que ficou de fora está nas pendências abaixo.
- Não verificado: a suíte com a rede de fato desligada (o isolamento vem dos servidores HTTP locais e de hosts `.invalid`); a obediência do agente à `sdd-new-session` (A-003 do DEFINE: só o contrato escrito é testado).

### Pendências

**🐛 Bug fix** — o que ficou quebrado, parcial ou com comportamento errado conhecido:

- nenhuma no sdd-open. (Fora desta frente, no starter: `README.md` e `docs/quickstart*.md` ainda apontam para `robertodiasduarte/specgate`.)

**✨ Feature improvement** — o que é incremento planejado, melhoria ou próxima etapa de escopo:

- F3 Build e Release — próxima (ver Próximos passos e o prompt de retomada).
- Risco aceito (nota 6 da revisão, recusada): `checar.sh` rodado de uma subpasta sugere `git rm --cached "<caminho relativo à raiz>"`, que falha a partir da subpasta. Herdado do starter; o `doctor` entra na raiz antes. Corrigir quando a saída do `checar.sh` puder mudar (os 57 testes conferem o texto).
- Risco aceito: `config.example.yaml` vem com `default_branch: main`; num remoto em `master`, a `new-session` 1.1.0 para e pergunta em toda frente até o usuário corrigir a linha.
- Risco aceito (decisão do Roberto no Brainstorm): `editor` e `worktree_base` descobertos vão para o `sdd/config.yaml` commitado (compartilhado); a skill declara a evidência ("`command -v code` neste computador", "padrão do sdd-open") e avisa que qualquer um corrige a linha.
- Ruído: `ResourceWarning: unclosed socket` dos servidores HTTP locais do `test_checar.py` portado (veio do starter; não é falha).
- Para depois: ligar `checar.sh --segredo` (sai 1 com achado) ou o `pre-commit.sh` ao `release.landmines_cmd`; `init` sem git oferecer a `sdd-iniciar-repo`; README e `AGENTS.md.tmpl` citando as 3 skills novas (F6).
- Carregados da F1: trocar o pin `actions/checkout@11d5960a…` (v4.4.0, Node 20 depreciado) por SHA de v5 nos dois workflows; observar o CI no Ubuntu 26; tag manual e push de `main` no mesmo commit podem deixar duas tags (para minor/major, empurrar a tag depois da run de `main`); guia do aluno não rastreado em `/Users/robertoduarte/rdd-public/sdd-starter/docs/guia-do-aluno.pt-BR.md` (494 linhas, entrada da F6 — um `git clean` naquele checkout o apaga).

### Próximos passos

1. **F3 Build e Release — brainstorm** com `sdd-brainstorm`, gravando `sdd/features/BRAINSTORM_F3_BUILD_RELEASE.md`. Entradas: `references/aplicar-migration.md` do starter (195 linhas) → `.agents/skills/sdd-build/references/`; seção `## Migrations aplicadas` em `sdd/templates/BUILD_REPORT_TEMPLATE.md` + regra em `sdd/bin/report-lint.py`; bullet `LM-004` no `sdd/playbook.md`; bloco único do "go" da Fase 2 da `sdd-release` do starter (linhas 203–254 de `skills/sdd-release/SKILL.md`). Pronto quando: abordagem confirmada, YAGNI, 2 checkpoints.
2. **F3 — define, design, build**: `DEFINE_F3_BUILD_RELEASE.md` com o mesmo `verify_gate` da F2; manifest com `MANIFEST.txt`; commit antes do gate. Pronto quando: `verify-gate.sh --strict` 0, `report-lint.py` 0, 1 sabotagem por script alterado.
3. **F3 — release**: PR, CI verde, OK citando "sdd-open", push em `main` → `v2.2.3` automática (ou tag manual depois da run). Pronto quando: `gh release view` mostra `SHA256SUMS.txt` e o hash confere.
4. **F4 → F5 → F6**, mesmo ciclo.

### Alertas — o que não quebrar

- **`sdd/` é território do usuário**: o `init` só completa arquivo que falta e nunca sobrescreve (`sdd_faltantes`/`aplicar()` em `bin/sdd-open.sh`). Mudança da F3 em `sdd/bin/report-lint.py`, `sdd/templates/` ou `sdd/playbook.md` só chega a instalação nova — decidir no Brainstorm da F3 se isso basta ou como avisar.
- **A F3 vai mexer em `sdd/`** pela primeira vez nesta frente: os seis exits do `verify-gate.sh`, as fixtures de `sdd/fixtures/` e os 242 testes ficam como estão; `report-lint.py` ganha regra sem perder nenhum contrato dos 14 testes de `tests/test_report_lint.py`.
- **Skill alterada sobe versão** (`sdd-build` 2.0.0, `sdd-release` 2.1.0 hoje): `check-versions.py --base v2.2.2 --base-obrigatoria` reprova no CI e na release. Se o clone local não tiver a tag: `GIT_TERMINAL_PROMPT=0 git fetch -q origin tag v2.2.2`.
- **Literais do G2**: e-mail só em `example.com/.org/.net`; `git@host`, CPF, CNPJ montados em tempo de execução; host de teste em `.invalid`.
- **Contagem de skills** em `tests/test_skill_lint.py` é 16; F3 não acrescenta skill.
- Demais alertas continuam valendo (`GIT_TERMINAL_PROMPT=0`, push em `main` só com OK citando "sdd-open", `MANIFEST.txt` em `LC_ALL=C`, `python3 -B`, `git add` por nome, bash 3.2, sem zsh/symlink, `sync` idempotente, a camada de conversa nas nativas é da F4).

### Onde está o trabalho

- Worktree `/Users/robertoduarte/rdd-worktrees/sdd-open-incorporar-starter`, branch `feat/incorporar-starter` em `41c6169` = `origin/main` = tag `v2.2.2`. Não rastreados: `sdd/features/`, `sdd/handoffs/`, `sdd/reports/`.
- Release: https://github.com/robertodiasduarte/sdd-open/releases/tag/v2.2.2 · PR #2 merged.
- Fonte da F3: `/Users/robertoduarte/rdd-public/sdd-starter` (main `17c69c4`): `skills/sdd-build/references/aplicar-migration.md`, `skills/sdd-release/SKILL.md` (Fase 2, linhas 203–254).

---

## 2026-10-29 — Decisões e F1 Manutenção (entregue, Release v2.2.1)

### O que foi feito

- **5 decisões do Roberto**, registradas em `## Eventos`: (1) fonte canônica de `sdd-governanca`, `sdd-auditoria-harness`, `sdd-prompt-builder` = open; (2) camada de conversa sempre ligada, sem toggle; (3) Status `✅ ▶️ ⬜ ⏸️ ➖` abre cada resposta, banner vira 1ª palavra do Status, kanban `✅ 🏃 ⬜ ➖` do `RESUMO_ETAPA.md` intacto; (4) descoberta grava nos slots de `sdd/config.yaml`, sem `sdd/ambiente.md`; (5) starter vira distribuição gerada de `.agents/skills/` do open, em frente própria depois da F6.
- **Fluxo SDD da F1** (artefatos não rastreados, nesta worktree): `sdd/features/BRAINSTORM_F1_MANUTENCAO.md` (abordagem A: `tests/` na raiz em unittest, 6 cortes YAGNI, 2 checkpoints), `sdd/features/DEFINE_F1_MANUTENCAO.md` v1.1 (26 ATs EARS, Clarity 14/15), `sdd/features/DESIGN_F1_MANUTENCAO.md` v1.1 (18 arquivos, 5 ADRs), `sdd/reports/BUILD_REPORT_F1_MANUTENCAO.md` (Complete; evidência em `sdd/reports/evidence/F1_MANUTENCAO/`).
- **Código em `main`** (commits `3db1686`, `9db642b`, `f75fbdb`):
  - `tests/apoio.py` (sandbox: git isolado, HOME falso, `PYTHON = sys.executable`, `SDD_TEST_BASH`) + 9 suítes: `test_verify_gate.py` (23), `test_report_lint.py` (14), `test_skill_lint.py` (8), `test_playbook_lint.py` (8), `test_sdd_open.py` (12), `test_check_versions.py` (16), `test_next_version.py` (12), `test_publish_gate_patterns.py` (5), `test_release_workflow.py` (17) = **115 testes**.
  - `scripts/check-versions.py` (versão X.Y.Z por skill, `manifest.json`/`evals/cases.json` coerentes, bump contra `--base`; exit 0/1/64).
  - `scripts/next-version.sh` (bash 3.2; imprime `TAG=`/`NEW=`/`BASE=`; aceita a tag empurrada como argumento; recusa HEAD que não descende da última tag).
  - `.github/workflows/release.yml` (push em `main` nos paths do produto ou tag `v[0-9]+.[0-9]+.[0-9]+`; job `testes` só leitura → job `release` com `needs` e `contents: write`; `git archive` + `sha256sum` + `gh release create`).
  - `.github/workflows/publish-gate.yml` (+ `permissions: contents: read`, `fetch-depth: 0`, steps "Unit tests" e "Version gate").
  - `scripts/publish-gate-patterns.txt` (+ CPF e CNPJ com pontuação, telefone BR sem `+55`).
  - `.agents/skills/sdd-auditoria-harness/SKILL.md` (+ `version: "1.0.0"`, só frontmatter); `CONTRIBUTING.md`; `MANIFEST.txt` (+13).
- **Nenhum script existente mudou**: `git diff 80d7887 -- sdd/fixtures sdd/bin bin scripts/publish-gate.sh` vazio.
- **Sabotagem** (uma por script, revertida com `git checkout`): 6 de 6 deixaram teste nomeado vermelho. A do `report-lint` (desligar "deve funcionar não é prova") só foi pega depois do teste novo `test_declaracao_nega_mesmo_com_log_valido_na_celula` — lacuna real fechada em `9db642b`.
- **Release**: PR https://github.com/robertodiasduarte/sdd-open/pull/1 (CI run 40875642307 verde, 115 testes no Linux, sem skip) → OK do Roberto → push fast-forward → run 40876615567 → https://github.com/robertodiasduarte/sdd-open/releases/tag/v2.2.1 (Latest), tag em `f75fbdb`, SHA-256 do pacote `636f702580dca80c2c5ca3214af682cdf1a9434b4ea664048f3344d025d950f7`, `shasum -a 256 -c` OK.

### Casos e testes em aberto

- Verify Gate do DEFINE: `bash sdd/bin/verify-gate.sh --strict sdd/features/DEFINE_F1_MANUTENCAO.md` → exit 0 em `f75fbdb` (publish-gate G1–G5 verdes na cópia de `git archive HEAD`, 115 testes OK). Log em `sdd/reports/evidence/F1_MANUTENCAO/AT-001.log`.
- Suíte rodada local no `/usr/bin/python3` 3.9.6 e no `python3` 3.15, com `/bin/bash` 3.2.57; no CI, Python do `ubuntu-latest` com bash 5. Tempo: ~35 s (o `test_sdd_open.py` faz `init` em cada teste, ~22 s).
- `GateInteiro` em `test_publish_gate_patterns.py` é pulado onde não há `gitleaks`; no CI e nesta máquina (gitleaks 8.30.1) ele roda.
- Nenhum caso em aberto na F1.

### Pendências

**🐛 Bug fix** — o que ficou quebrado, parcial ou com comportamento errado conhecido:

- nenhuma no sdd-open. (Fora desta frente, no starter: `README.md` e `docs/quickstart*.md` ainda apontam para `robertodiasduarte/specgate`; corrigir na próxima release do starter, com OK citando "sdd-starter".)

**✨ Feature improvement** — o que é incremento planejado, melhoria ou próxima etapa de escopo:

- F2 Terreno — próxima (ver Próximos passos e o prompt de retomada).
- `actions/checkout@11d5960a326750d5838078e36cf38b85af677262` (v4.4.0) roda em Node.js 20, que o GitHub marcou como depreciado (anotação nos runs 40876615494 e 40876615567). Trocar o pin por um SHA de release v5 nos dois workflows; `tests/test_release_workflow.py::test_actions_fixadas_por_sha` continua valendo.
- `ubuntu-latest` migra para Ubuntu 26 a partir de 19/10/2026 (anotação dos runs): observar o próximo CI.
- Risco aceito: com a fila por ref, um push de tag manual e um push de `main` no mesmo commit, quase ao mesmo tempo, podem deixar duas tags no commit (ex.: `v2.2.2` e `v2.3.0`). Recomendação para minor/major: empurrar a tag **depois** que a run de `main` terminar.
- Risco aceito: o job `testes` da release não repete os checks inline de fixtures/smoke do `publish-gate.yml` (a suíte cobre o mesmo contrato); mover tudo para um script fica para quando o `publish-gate.yml` puder mudar.
- Guia do aluno do starter: a worktree `sdd-starter-linguagem-aluno` foi removida, mas o arquivo sobreviveu **não rastreado** em `/Users/robertoduarte/rdd-public/sdd-starter/docs/guia-do-aluno.pt-BR.md` (494 linhas, conferido em 29/10). Entrada da F6; um `git clean` naquele checkout o apaga — copiar ou commitar no starter (com OK citando "sdd-starter") antes.

### Próximos passos

1. **F2 Terreno — brainstorm** com `sdd-brainstorm`, gravando `sdd/features/BRAINSTORM_F2_TERRENO.md`. Decisões a levar: onde moram os testes portados (`tests/` na raiz, como na F1, ou `.agents/skills/<skill>/tests/` como no starter — o `sync` copia a pasta da skill para o projeto do usuário e o CI só roda `-s tests`); como o `doctor` chama o `checar.sh` (`doctor --repo`); pré-voo `checar.sh --frente` e matriz de 12 achados na `sdd-new-session` 1.0.0 do open; descoberta que grava `project.default_branch`, `editor`, `worktree_base`, `project.test_cmd`, `project.lint_cmd`. Pronto quando: abordagem confirmada, YAGNI, 2 checkpoints.
2. **F2 — define, design, build**: `DEFINE_F2_TERRENO.md` com `verify_gate` `kind: test` e o mesmo `cmd` da F1; manifest com `MANIFEST.txt`. Pronto quando: `verify-gate.sh --strict` sai 0, `report-lint.py` sai 0 e 1 sabotagem por script portado no BUILD_REPORT.
3. **F2 — release**: PR, CI verde, OK citando "sdd-open", push em `main` → Release automática (`v2.2.2`) ou tag manual `v2.3.0` empurrada depois da run de `main`. Pronto quando: `gh release view` mostra a Release com `SHA256SUMS.txt` e o hash confere.
4. **F3 → F4 → F5 → F6**, mesmo ciclo.

### Alertas — o que não quebrar

- **Push em `main` publica Release sozinho** quando toca `.agents/skills/**`, `bin/**`, `sdd/bin/**`, `sdd/templates/**`, `sdd/fixtures/**`, `sdd/playbook.md`, `sdd/config.example.yaml` ou `AGENTS.md.tmpl`. Push em `main` só com OK explícito citando "sdd-open", depois de PR com CI verde.
- **Skill alterada sobe `metadata.version`**: `python3 scripts/check-versions.py --base v2.2.1 --base-obrigatoria` reprova no CI e na release.
- **Nenhum arquivo da árvore pode conter literal que case com `scripts/publish-gate-patterns.txt`**: os testes do starter que a F2 vai portar têm `git@github.com` (3 linhas), e-mails em `exemplo.invalid`/`exemplo.com` (16 — o gate só isenta `example.com/.org/.net`) e o CPF literal `000.000.000-00` em `skills/sdd-higiene-dado/tests/test_alarme.py:164`. Trocar para `example.com` e montar amostras por concatenação em tempo de execução (padrão de `tests/test_publish_gate_patterns.py`).
- **`python3 -B` sempre** e `git add` por nome de arquivo: o open não tem `.gitignore`, e um `__pycache__` ou um doc de `sdd/features/` commitado reprova o G3.
- Demais alertas da etapa anterior continuam valendo (`GIT_TERMINAL_PROMPT=0`, MANIFEST allowlist, bash 3.2, `skill-lint` ≤ 1024, `sync` idempotente, só a camada de conversa muda nas skills nativas na F4, árvore `sdd/features|reviews|reports|releases|handoffs`).

### Onde está o trabalho

- Worktree `/Users/robertoduarte/rdd-worktrees/sdd-open-incorporar-starter`, branch `feat/incorporar-starter` em `f75fbdb` = `origin/main` = tag `v2.2.1`. Não rastreados: `sdd/features/`, `sdd/handoffs/`, `sdd/reports/`.
- Release: https://github.com/robertodiasduarte/sdd-open/releases/tag/v2.2.1 · PR #1 merged.
- Fonte da F2: `/Users/robertoduarte/rdd-public/sdd-starter` (main em `17c69c4`): `skills/sdd-checar-ambiente` 1.2.0 (`scripts/checar.sh` 446 linhas, `tests/test_checar.py` 53 testes), `skills/sdd-higiene-dado` 1.1.0 (`scripts/alarme.sh` 79 + `scripts/pre-commit.sh` 120, `tests/test_alarme.py` 28, `evals/`, `manifest.json`, `CHANGELOG.md`, `references/`), `skills/sdd-iniciar-repo` 1.1.0 (`scripts/inventario.sh` 191, `tests/test_inventario.py` 24), `skills/sdd-new-session` 1.3.0 (pré-voo e matriz). Nenhum `grep -P`, `readlink -f`, `declare -A` ou `mapfile` nesses scripts.

---

## 2026-10-29 — Avaliação do starter e abertura da frente

### O que foi feito

- **Comparativo lado a lado** sdd-starter v1.5.15 (commit `17c69c4`, worktree `/Users/robertoduarte/rdd-worktrees/sdd-starter-linguagem-aluno`) × sdd-open commit `80d7887` (24/10/2026, `/Users/robertoduarte/rdd-public/sdd-open`). Números medidos: starter 15 skills, 4.532 linhas de SKILL.md, 2.977 linhas de scripts, 144 funções de teste em 6 suítes, release v1.5.15 publicada em 27/10 com 15 zips; open 13 skills, 1.721 linhas de SKILL.md, 1.993 linhas de scripts, 0 testes unitários, nenhuma Release no GitHub.
- **Três skills com o mesmo nome divergiram em todos os arquivos**: `sdd-governanca` (starter 1.0.1 × open 2.1.0), `sdd-auditoria-harness` (1.0.0 × sem versão no open), `sdd-prompt-builder` (1.0.0 × 2.0.0). Nas três, o open é o mais novo.
- **Avaliação profunda** gravada em `sdd/features/AVALIACAO_STARTER_PARA_OPEN.md`: tabela de 17 componentes (o que faz bem · já existe no open? · entra como), anatomia dos 10 itens da camada "Como falar com o aluno" (fonte: `sdd/DEFINE_LINGUAGEM_ALUNO.md` do starter, Clarity 14/15), tabela de encaixe com o que o open já tem (banner `🧠 FASE`, `RESUMO_ETAPA.md` com kanban ✅ 🏃 ⬜ ➖, regra "só existe se N ≥ 1", scripts terminando em `RESULTADO:`), 5 decisões e 6 frentes com gate.
- **Fatos do open que condicionam o trabalho**, conferidos no código: `scripts/publish-gate.sh` G3 é allowlist por `MANIFEST.txt` — todo arquivo da árvore precisa estar declarado; `sdd/bin/skill-lint.py` exige `description` ≤ 1024 caracteres e avisa acima de 500 linhas; `.github/workflows/publish-gate.yml` roda gitleaks, fixtures do gate (exits 5/0/64 e `--strict`), self-test do playbook, skill-lint, smoke do gerador (init idempotente, `sync --check`) e proíbe zsh e symlink; o open não tem `.gitignore`.
- **Worktree aberta**: `git worktree add /Users/robertoduarte/rdd-worktrees/sdd-open-incorporar-starter -b feat/incorporar-starter origin/main` → HEAD `80d7887`, branch rastreando `origin/main`. Pastas `sdd/features/` e `sdd/handoffs/` criadas, **não rastreadas**.

### Casos e testes em aberto

- Nenhum teste foi executado nesta sessão; o trabalho foi de leitura e análise. Os números de teste acima vêm de `grep -c "def test_"` nas 6 suítes do starter.
- Verificação pendente de duas afirmações da avaliação: (a) o starter diz que o `validate_design.py` cruza o inventário LLM com o manifest — conferido no código (`validate_design.py` linhas 174–186); (b) o open "não tem procedimento de migration" — conferido por grep em `.agents/skills/sdd-build/SKILL.md` e `sdd/config.example.yaml` (só `layers.sql` e `deploy.drift_check_cmd`).
- O guia do aluno do starter (`docs/guia-do-aluno.pt-BR.md`, 494 linhas) existe só na worktree `sdd-starter-linguagem-aluno`, sem commit; é entrada da F6 e pode sumir se aquela worktree for removida — copiar antes.

### Pendências

**🐛 Bug fix** — o que ficou quebrado, parcial ou com comportamento errado conhecido:

- nenhuma no sdd-open. (Fora desta frente, no starter: `README.md` e `docs/quickstart*.md` apontam para `robertodiasduarte/specgate`, repositório que não existe; o nome atual é sdd-open. Corrigir na próxima release do starter, com OK citando "sdd-starter".)

**✨ Feature improvement** — o que é incremento planejado, melhoria ou próxima etapa de escopo:

- Decisões 1–5 (ver próximos passos).
- F1 Manutenção: `tests/` para `bin/sdd-open.sh` (639 linhas), `sdd/bin/verify-gate.sh` (197), `report-lint.py`, `skill-lint.py`, `playbook-lint.sh`; `scripts/check-versions.py` portado e linha de identificação nas 13 skills; workflow de auto-release com 2 jobs e `SHA256SUMS.txt`; `sdd/bin/design-lint.py` e `handoff-lint.py` com `gate.sh` que aceita o exemplo e rejeita fixtures ruins; padrões de PII brasileira (CPF 11 dígitos, `+55`, e-mail pessoal) em `scripts/publish-gate-patterns.txt`; `doctor` conferindo segredo já no histórico (`git ls-files` para `.env`, `.pfx`, `.p12`, `.pem` com `PRIVATE KEY`).
- F2 Terreno: portar `sdd-checar-ambiente` 1.2.0 (`scripts/checar.sh` 446 linhas, 53 testes), `sdd-higiene-dado` 1.1.0 (`alarme.sh`, `pre-commit.sh` 120 linhas, 28 testes, evals 8 casos), `sdd-iniciar-repo` 1.1.0 (`inventario.sh` 191 linhas, 24 testes) para `.agents/skills/`, com a seção do aluno já nos símbolos decididos; `sdd-new-session` do open (1.0.0) ganha o pré-voo via `checar.sh --frente`, a matriz de 12 achados e a descoberta que preenche `project.default_branch`, `editor`, `worktree_base`, `project.test_cmd`, `project.lint_cmd` em `sdd/config.yaml`.
- F3 Build e Release: `references/aplicar-migration.md` do starter em `.agents/skills/sdd-build/references/`; seção `## Migrations aplicadas` em `sdd/templates/BUILD_REPORT_TEMPLATE.md` e regra em `sdd/bin/report-lint.py` (migration em Files Created sem linha arquivo · projeto nome e ref · data · prova por leitura ⇒ falha); bullet `LM-004` no `## Sempre` de `sdd/playbook.md` ("exit 0 não prova migration; prova é ler de volta"); bloco único do "go" na `sdd-release` com os campos do starter (O que sobe em palavras · O que muda em produção · O push publica sozinho? · O deploy espera os testes? lido de `.github/workflows/*`, `continue-on-error`/`|| true` contam como não · Banco · Verificações).
- F4 Conversa: seção `## Como falar com o aluno` curta (≈32 linhas, padrão do Grupo 2 do starter) mais `references/como-falar.md` (glossário · Status preenchido · exemplo completo) nas 13 skills do open, inclusive `sdd-governanca`, `sdd-prompt-builder`, `sdd-auditoria-harness`, `sdd-iterate`, `sdd-playbook`, `sdd-ux-review`; glossário dos termos do open (exits 0/2/3/4/5/64, landmine, ledger, drift, slot vazio, adaptador e sync, waiver, vendor, contexto fresco, iterate); `skill-lint.py` passa a exigir a seção e o arquivo; diff por skill no BUILD_REPORT provando que nenhum comando, condição ou ordem de passo mudou.
- F5 Conhecimento: portar `sdd-kb` 2.1.0 (`validate_kb.py`, `kb_normativo.py`, `gate.sh`, assets e exemplos) e ligar o `RULE_MAP.md` ao Verify Gate (coluna Teste = o `cmd` do gate); entrevista de público e referências do `ux-review-builder` como entrada opcional da `sdd-ux-review`.
- F6 Docs: "nunca siga para a próxima fase com um documento que você não leu" e a tabela onde-roda → ferramenta no `docs/pt-BR/quickstart.md`; guia do aluno adaptado ao open em `docs/pt-BR/`; seção "Por que cada regra existe" nas skills de fase.
- Risco aceito por ora: o modo `briefs`, o playbook ACE-lite e o veredito graduado ficam como estão; a camada de conversa não os remove, só os explica.

### Próximos passos

1. **Colher as 5 decisões do Roberto**, uma pergunta por vez, com recomendação primeiro — (1) fonte canônica das 3 skills compartilhadas = open; (2) camada de conversa ligada por padrão, sem toggle; (3) símbolos do Status unificados em `✅ ▶️ ⬜ ⏸️ ➖` e banner virando a primeira palavra do Status; (4) descoberta de ambiente grava nos slots de `sdd/config.yaml`, sem `sdd/ambiente.md`; (5) o starter vira distribuição gerada a partir do open. Pronto quando: as 5 respostas estão registradas em `## Eventos` deste arquivo.
2. **F1 Manutenção — brainstorm** com a skill `sdd-brainstorm`, entrada `sdd/features/AVALIACAO_STARTER_PARA_OPEN.md` seção 3 linha F1, gravando `sdd/features/BRAINSTORM_F1_MANUTENCAO.md`. Pronto quando: o arquivo existe com abordagem confirmada, YAGNI e 2 checkpoints.
3. **F1 — define, design, build** nesta worktree: `sdd/features/DEFINE_F1_MANUTENCAO.md` com `verify_gate` `kind: test`, `cmd: "bash scripts/publish-gate.sh . && python3 -m unittest discover -s tests -p 'test_*.py'"`; `DESIGN_F1_MANUTENCAO.md` com manifest que inclui `MANIFEST.txt`; build em modo default. Pronto quando: `sdd/bin/verify-gate.sh --strict sdd/features/DEFINE_F1_MANUTENCAO.md` sai 0 e `sdd/reports/BUILD_REPORT_F1_MANUTENCAO.md` passa em `python3 sdd/bin/report-lint.py`.
4. **F1 — release**: PR de `feat/incorporar-starter` para `main`, CI `publish-gate` verde, push em `main` só com OK do Roberto citando "sdd-open". Pronto quando: a tag e a Release com `SHA256SUMS.txt` existem em `https://github.com/robertodiasduarte/sdd-open/releases`.
5. **F2 → F3 → F4 → F5 → F6**, cada uma repetindo os passos 2–4 com seu próprio `{F}` (`F2_TERRENO`, `F3_BUILD_RELEASE`, `F4_CONVERSA`, `F5_CONHECIMENTO`, `F6_DOCS`). F2 e F3 antes de F4 porque as skills portadas já chegam com a seção do aluno. Pronto quando: os 6 critérios da ficha estão satisfeitos.

### Alertas — o que não quebrar

- **Todo comando que fala com o remoto roda com `GIT_TERMINAL_PROMPT=0`** (`fetch`, `push`, `ls-remote`, `gh`). Nunca deixar o git pedir senha no terminal do agente.
- **Push em `main` só com OK explícito do Roberto nomeando "sdd-open"** no mesmo turno — mesma regra que vale para o sdd-starter. PR + CI verde antes.
- **`MANIFEST.txt` é allowlist**: `scripts/publish-gate.sh` G3 reprova qualquer arquivo da árvore que não esteja declarado. Cada arquivo novo (skill, teste, referência, workflow) entra no `MANIFEST.txt` no mesmo commit. Os documentos de trabalho em `sdd/features/` e `sdd/handoffs/` desta frente ficam **fora do commit** e reprovam o gate local — rodar o gate sobre uma cópia limpa (`git archive HEAD | tar -x -C <tmp>`) ou movê-los antes.
- **Compatibilidade declarada do open**: bash 3.2, sem `declare -A`, sem zsh, sem symlink, variável sempre entre chaves antes de texto não-ASCII; o CI reprova shebang zsh e symlink. Os scripts do starter (`checar.sh`, `alarme.sh`, `inventario.sh`) já rodam em bash 3.2 do macOS, mas o `grep -P` e o `readlink -f` não existem lá — conferir ao portar.
- **`skill-lint.py`**: `description` ≤ 1024 caracteres (medido no starter: `sdd-checar-ambiente` 766, `sdd-higiene-dado` 859, `sdd-iniciar-repo` 978, `sdd-kb` 911 — todas passam, mas a da `sdd-iniciar-repo` tem só 46 de folga), `name` igual à pasta, corpo ≤ 500 linhas de preferência.
- **`sync` precisa continuar idempotente** (smoke do CI: `init --yes` + `sync --yes` + `git status --porcelain` vazio + `sync --check`). Skills novas em `.agents/skills/` entram no `sync` automaticamente; conferir que o cabeçalho `sdd-open:generated` não quebra `tests/*.py` copiados.
- **Só a camada de conversa muda nas skills nativas do open** (F4): comandos, condições, ordem dos passos, slots do config e exits ficam idênticos, provado por diff.
- **O open continua com a árvore `sdd/features`, `reviews`, `reports`, `releases`, `handoffs`** — não adotar a pasta plana do starter.
- **Fora de escopo:** redesenhar a CLI `init/sync/doctor` ou o `config.yaml`; mexer no `verify-gate.sh` além de testes; alterar o sdd-starter nesta frente (exceto o que a decisão 5 determinar, em frente própria); modo `briefs`; curadoria do playbook além do `LM-004`; teste no Windows.

### Onde está o trabalho

- Worktree: `/Users/robertoduarte/rdd-worktrees/sdd-open-incorporar-starter` — branch `feat/incorporar-starter`, base `origin/main` em `80d7887`, remoto `https://github.com/robertodiasduarte/sdd-open.git`.
- Checkout principal do open: `/Users/robertoduarte/rdd-public/sdd-open` (não trabalhar nele).
- Avaliação de entrada: `sdd/features/AVALIACAO_STARTER_PARA_OPEN.md` nesta worktree (cópia de `/private/tmp/claude-501/-Users-robertoduarte-rdd-worktrees-sdd-starter-linguagem-aluno/d33e2c2a-ce4a-4569-9547-7611306204d2/scratchpad/avaliacao-starter-para-open.md`).
- Fonte do que vai ser portado: sdd-starter v1.5.15 — tag `v1.5.15` em `https://github.com/robertodiasduarte/sdd-starter`; localmente em `/Users/robertoduarte/rdd-worktrees/sdd-starter-linguagem-aluno` (commit `17c69c4`; pode ser removida — nesse caso `git -C /Users/robertoduarte/rdd-public/sdd-starter pull` e usar `main`). O guia do aluno (`docs/guia-do-aluno.pt-BR.md`) só existe nessa worktree, sem commit.
- Skills do fluxo SDD usadas nesta frente: as `sdd-*` globais em `/Users/robertoduarte/.claude/skills/` (starter v1.5.15); artefatos gravados no layout do open (`sdd/features/`, `sdd/reports/`, `sdd/handoffs/`), não rastreados.
