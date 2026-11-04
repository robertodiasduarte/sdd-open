# Continuar: INCORPORAR_STARTER — sessão 10: F13 UX e LLM no código

Esta sessão roda **dentro da worktree** `/Users/robertoduarte/rdd-worktrees/sdd-open-f13-ux-llm`, branch `feat/f13-ux-llm`, já criada de `origin/main` = `6b7633c` (tag `v2.4.0`). Os artefatos SDD da família (features, handoffs, reports, reviews) já estão no disco, fora do commit; a fonte deles é a branch `docs/incorporar-starter` do remoto, nunca mesclada em `main`.

## Conferir a worktree (antes de ler qualquer coisa)

A frente da F13 **já foi aberta**: não rode `git worktree add`. Confira que está tudo no lugar:

```bash
git rev-parse --show-toplevel                                             # esperado: /Users/robertoduarte/rdd-worktrees/sdd-open-f13-ux-llm
git branch --show-current                                                 # esperado: feat/f13-ux-llm
git log --oneline -1                                                      # esperado: 6b7633c ou mais novo
git rev-parse -q --verify 'v2.4.0^{commit}'                               # base do check-versions; esperado: 6b7633c…
git status --short | head -4                                              # esperado: só "?? sdd/…"
ls sdd/handoffs/HANDOFF_INCORPORAR_STARTER.md sdd/features/PLANO_F4_F15_CONSOLIDADO.md
```

Se a sessão abriu em outra pasta, pare e peça ao Roberto para abrir o agente na pasta da worktree: nenhum `cd` muda a pasta à qual a sessão fica presa. Se a worktree não existir, recrie a partir do clone principal e reabra a sessão nela:

```bash
cd /Users/robertoduarte/rdd-public/sdd-open
GIT_TERMINAL_PROMPT=0 git fetch -q origin
git worktree add /Users/robertoduarte/rdd-worktrees/sdd-open-f13-ux-llm -b feat/f13-ux-llm origin/main
cd /Users/robertoduarte/rdd-worktrees/sdd-open-f13-ux-llm
GIT_TERMINAL_PROMPT=0 git fetch -q origin tag v2.4.0                      # base do check-versions
GIT_TERMINAL_PROMPT=0 git fetch -q origin docs/incorporar-starter
git checkout origin/docs/incorporar-starter -- sdd/features sdd/handoffs sdd/reports sdd/reviews
git rm -r -q --cached sdd/features sdd/handoffs sdd/reports sdd/reviews   # ficam no disco, fora do commit
```

Não trabalhe na worktree antiga `sdd-open-f12-contexto` (branch já mesclada). O `sdd/ambiente.md` do checkout principal é nota local da `sdd-new-session` do starter, não rastreada; não o commite.

Depois, leia nesta ordem:
- `sdd/features/PLANO_F4_F15_CONSOLIDADO.md`:
  - seção 0 (P1–P4; a F13 segue no **P4**);
  - seção 8: o preâmbulo, **8.0** (as 10 regras do PORTE), o quadro **"F13 UX e LLM no código"**;
  - **8.1** "F13 UX e LLM" (U1–U3, L1–L4), **8.2** (slots `prompts.*` e `smoke.*`, os `smoke.*` candidatos a cair) e **8.3** (fontes no privado);
  - seção 10 (uma frente por sessão).
- `sdd/handoffs/HANDOFF_INCORPORAR_STARTER.md`: a Ficha, `## Eventos` e a etapa "F12", que é a do topo.
- `.agents/skills/sdd-ux-review/SKILL.md` e `sdd/templates/UX_REVIEW_TEMPLATE.md` (onde entra a tabela WCAG), `.agents/skills/sdd-build/SKILL.md` (o 5.5, onde entra o roteador loop × prompt), `.agents/skills/sdd-prompt-builder/`, `sdd/templates/DESIGN_TEMPLATE.md` (colunas de LLM Prompts) e `.agents/skills/sdd-design/SKILL.md` (o 5.5).

## Onde paramos

- **F1–F12, W0 e M1 entregues; o P3 (starter) está concluído; o P4 está na F13.** A última Release é https://github.com/robertodiasduarte/sdd-open/releases/tag/v2.4.0: tag em `6b7633c`, runs `release` 41734697736 e 41734699387, `SHA256SUMS.txt` conferido (`9561e03c63a0013e1f89b2a9892ecdce16f71176bc0b396ac582548838264944`).
- **Estado do pacote:** 17 skills; **992 testes** verdes no piso `SDD_TEST_BASH=/bin/bash /usr/bin/python3` (Python 3.9.6, bash 3.2.57), local e no CI (no último PR, Ubuntu 14m27s, macOS 27m58s); roadmap (`docs/roadmap.md` + PT) com 3 linhas; `MANIFEST.txt` 403 linhas.
- **A sessão 9 fez a F12** do brainstorm à release; esta sessão faz a **F13 inteira**, do brainstorm à release. A F14 é a sessão 11.

## Contexto que você precisa ter

- **Remoto:** `https://github.com/robertodiasduarte/sdd-open.git`.
- **Release automática:** sai no push de `main` que toca `.agents/skills/**`, `bin/**`, `sdd/bin/**`, `sdd/hooks/**`, `sdd/templates/**`, `sdd/fixtures/**`, `sdd/review/**`, `sdd/patterns/**`, `sdd/WORKFLOW_CONTRACTS.yaml`, `sdd/playbook.md`, `sdd/config.example.yaml` ou `AGENTS.md.tmpl`. O patch vem de `scripts/next-version.sh` (dá `v2.4.1`); uma tag `vX.Y.Z` empurrada à mão junto com `main` publica exatamente essa tag (foi assim na `v2.4.0`). O job `release` espera `testes` (teto 25 min) **e** `testes-macos` (teto 45 min).
- **Escopo da F13** (plano, quadro F13 e 8.1):
  - **U1** 7 critérios WCAG 2.2 AA com PASSA/REPROVA/N.A. no `UX_REVIEW_TEMPLATE.md` e na `sdd-ux-review`; cada REPROVA vira 1 MUST com o SC e o par medido; 2.1.1 e 2.5.8 herdados para Acceptance Notes; 3.3.7 é nível A e 2.4.13 é AAA;
  - **U2** `sdd/bin/contraste.sh`: razão com alpha composto sobre o fundo, truncando (4,49 reprova o piso 4,5:1);
  - **U3** smoke visual antes × depois, só projeto web: deriva as telas do diff, mede axe antes e depois, catraca de contraste com override no ledger; slots `smoke.*` (decidir se entra);
  - **L1** skill nova `.agents/skills/sdd-loop-builder/` (LOOP_SPEC v2: perfil por risco, estado de controle, verificador independente, regras de parada, orçamento por estágio, tabela de estágios LLM × código);
  - **L2** roteador no `sdd-build` 5.5: `Tipo=loop` gera LOOP_SPEC e depois um prompt por estágio; não encerrar o turno após o TXT BLOCK;
  - **L3** fragmento `LLM_PROMPTS_DESIGN.md` + colunas no `DESIGN_TEMPLATE.md`: inventário com Versão / Completeness / Refator de?; contrato com Autônomo?, Verification interna, Eval mínimo pré-ship; gate do build por Tipo;
  - **L4** `sdd/bin/prompt-drift-scan.sh`: `--conteudo` avalia antes do Write; `--self-test`; exits 0/2/64; sinais ancorados em `prompts.wrapper_pattern`.
- **Fontes no privado** (só leitura; o repositório privado **não** se altera). Leia do `origin/main` do privado (`git -C /Users/robertoduarte/RDD/Wordpress show origin/main:<arquivo>`; o checkout local dele fica atrás): `scripts/contraste.sh` (55 linhas, 0 refs RDD), `scripts/gates/prompt-drift-scan.sh` (231, 4 refs), `.claude/skills/loop-builder/` (323). `callLLM` vira exemplo do slot. Específico da RDD não viaja (regra 4 do 8.0). Receita por arquivo: `grep -niE 'supabase|deno|wordpress|wp-content|rdd-plataforma|hostinger|RDD/Wordpress|rdd-eval\.env|kimi|codex|gemini|muse|qwen|LM-[0-9]'`.
- **Decisões a levar ao brainstorm** (formato `PERGUNTA_DECISAO.md`, recomendada primeiro, com a marca da classe, "não sei", nunca "Outro"):
  - **D11**: slots `prompts.loop_builder_skill`, `prompts.wrapper_pattern`, `smoke.urls_cmd`, `smoke.a11y_cmd` (os `smoke.*` são candidatos a cair; slot sem leitor é texto morto, como o `schema.check_cmd` que caiu na F12);
  - se a **U3** entra nesta frente (é só para projeto web);
  - **versão da Release** (`v2.4.1` automática ou `v2.5.0` por tag: a F13 traz skill nova).
- **Decisões já tomadas, não reabrir:**
  - a camada de conversa fica sempre ligada; `flow.autonomous` liga o encadeamento, não a conversa;
  - toda pergunta tem a marca `[<código> · <rótulo>]`, a recomendada primeiro, "não sei" e nunca "Outro"; o OK da `sdd-release` fica sem marca;
  - vendor sem subagente degrada para `sdd-fluxo.sh despachar` → exit 40 e a parada ⏸️; o exit 40 não é por vendor;
  - o open é a fonte canônica de governança, auditoria-harness e prompt-builder; a KB fica em `sdd/kb/`; os artefatos SDD ficam na branch `docs/`;
  - `report-lint` fail-closed; hooks pelo `init` com confirmação; review externo obrigatório na release (R1, F10); governança em todo Define (D5, F12).
- **Skills do fluxo** (em `/Users/robertoduarte/.claude/skills/`): `sdd-brainstorm`, `sdd-define`, `sdd-design`, `sdd-build`, `sdd-handoff`. A `sdd-release` e a UX review são as do pacote. O DEFINE desta frente precisa da linha `| **Governança** | … |` no `## Technical Context`, vinda de um revisor fresco, senão o gate sai 5: rode o passo 11 de `.agents/skills/sdd-define/SKILL.md`.
  - Fluxo SDD completo, com revisão de contexto fresco do DESIGN (modo `contrato`) antes do build e do build depois (modo `veredito`). A `sdd-build` limita a 2 ciclos; um 3º é pergunta `[D4 · limite de tentativas]` ao Roberto.
  - **No brief de cada avaliador**, mande gravar só `sdd/reports/evidence/F13_<…>/AVAL*-*.log` com o helper `ev.sh` (molde: `sdd/reports/evidence/F12_CONTEXTO/ev.sh`: grava `$ cmd`, saída e `[exit=N]` real) e **proíba** terminar o comando passado a ele num formatador (`tail`, `head`, `tr`, `grep`, `wc`, `sed`). Peça também que nada seja gravado na pasta temporária do sistema fora de um `mktemp -d`, e que não rode `python3 -m py_compile` no projeto (grava `__pycache__` em `sdd/bin/`; use `ast.parse`).
  - O Bash da sessão é zsh: sem `PIPESTATUS`, lista numa variável não se divide em palavras e `!` num `grep` entre aspas duplas quebra a cadeia `&&`, cortando o resto em silêncio. Grave os logs com `/bin/bash -c` terminando em `[exit=$rc]`. Confira com `bash sdd/bin/gate-shell-evidencia.sh sdd/reports/evidence/<FEATURE>`.
  - **Não edite `sdd/bin/verify-gate.sh` enquanto o gate roda** (o bash lê o script aos pedaços e dá erro de sintaxe falso) e **não chame o gate com `SDD_TRACE=off`** (derruba 10 testes de trace: pendência 🐛 da F12).
  - O `report-lint` exige `evidence/<FEATURE>/` com o mesmo nome do `BUILD_REPORT_<FEATURE>.md`, a tabela reconhecida e a linha do avaliador. O DESIGN passa no `python3 sdd/bin/design-lint.py` e no `scripts/validate_design.py` da skill de design (chaves reprovam até dentro de código e de caminho; o BUILD_REPORT também).
- **Revisão adversarial real (R1 da release):** rode `bash sdd/bin/adversarial-review.sh --reviewer claude --auditor openrouter:qwen/qwen3.7-plus --feature <F>` (com ≥ 8 arquivos o `codex` entra sozinho como 2º revisor), `sdd-fluxo.sh loop … --rodada N` (teto 3) e `--conferir` na versão final; molde: `sdd/reports/evidence/F12_CONTEXTO/real-rodada.sh <N>`. O ledger (`ledger-review.md`) precisa existir antes do `loop` e usa `APLICADA`, `REBATIDA_EVIDENCIA` ou `REBATIDA_ESCOPO`. A chave da OpenRouter está em `~/.config/rdd-eval.env` (`OPENROUTER_API_KEY`): carregue só no ambiente do processo, nunca grave. Custo por rodada ≈ US$ 2,70 num diff do tamanho da F12 (quase tudo nominal da assinatura do Claude). Antes, rode o gate offline: `bash sdd/bin/adversarial-review-gate.sh`. Na F12, consertos feitos depois da rodada 3 trouxeram regressão grave: conserto novo pede teste de ataque, não só o do caso relatado.
- **Prova num agente real:** se a frente mudar o texto de um passo que outro agente segue, rode a prova **depois** do último conserto. Na F12, um conserto da rodada 3 quebrou o despacho no Codex (`.git` é só leitura na sandbox) e só a execução real mostrou. Critério: a linha ` exited 40 in ` do transcript, nunca o texto `AGUARDANDO_HUMANO`.
- **Versões atuais:**
  - auditoria-harness 1.1.1, brainstorm 2.2.0, build 2.5.1, checar-ambiente 1.4.1, define 2.5.0, design 2.4.0, governanca 2.4.0, handoff 2.1.1;
  - iterate 2.2.1, kb 2.2.1, new-session 1.3.0, playbook 2.1.1, prompt-builder 2.1.1, release 2.6.0, ux-review 2.4.0;
  - (portadas, sem a camada F4) higiene-dado 1.2.0, iniciar-repo 1.1.1.

  Toda skill tocada sobe de versão e atualiza a linha de identificação; os pinos de versão em `tests/test_contrato_build_release.py`, `test_correcoes_w0.py` e `test_matriz_new_session.py` mudam junto. Skill nova muda a contagem de `tests/test_skill_lint.py` (17 → 18). Confira com `python3 scripts/check-versions.py --base v2.4.0 --base-obrigatoria`.

## Tarefas, em ordem

1. **Brainstorm da F13** com a `sdd-brainstorm`, gravando `sdd/features/BRAINSTORM_F13_UX_LLM.md` a partir do quadro F13 e do 8.1. Pronto quando: D11, a U3 e a versão foram respondidas pelo Roberto, a abordagem foi confirmada e os cortes YAGNI e os 2 checkpoints estão registrados.
2. **Define, governança, UX review e design**:
   - `sdd/features/DEFINE_F13_UX_LLM.md`, com ATs em EARS, a linha `Governança` e o `verify_gate` `kind: test` de sempre: `cmd` = `T=$(mktemp -d) && git archive HEAD | tar -x -C $T && PUBLISH_GATE_MODE=ci bash scripts/publish-gate.sh $T && cd $T && SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover -s tests -p 'test_*.py'`;
   - `sdd/reviews/UX_REVIEW_F13_UX_LLM.md`;
   - `sdd/features/DESIGN_F13_UX_LLM.md`, com o File Manifest e o Advisor Ledger.

   Pronto quando: `verify-gate.sh --print` 0, os 2 lints do DESIGN 0 e a revisão de contexto fresco do DESIGN aplicada.
3. **Build**, com commit antes do gate e todo arquivo novo no `MANIFEST.txt` (`LC_ALL=C sort`; o arquivo é igual a `git ls-files`). Pronto quando:
   - `bash sdd/bin/verify-gate.sh --strict sdd/features/DEFINE_F13_UX_LLM.md` 0 e `python3 sdd/bin/report-lint.py sdd/reports/BUILD_REPORT_F13_UX_LLM.md` 0;
   - `contraste.sh '#767676' '#ffffff'` → 4.54 PASSA e `'#777777'` → 4.48 REPROVA, com caso RGBA; `skill-lint.py .agents/skills/sdd-loop-builder/SKILL.md` → 0; `prompt-drift-scan.sh --self-test` → 0;
   - todo script novo passa por `grep -nE 'mapfile|declare -A|\$\{[a-zA-Z_]+\^\^' <script>` sem achado, tem fixture e teste dos dois lados (regra 6 do 8.0), baseline vermelha na `v2.4.0` e 1 sabotagem;
   - `python3 sdd/bin/skill-lint.py --conversa .agents/skills/sdd-*/SKILL.md` 0 nas 18 skills e `bash sdd/bin/sdd-decisoes-lint.sh --sites .agents/skills sdd/templates/fragments` 0;
   - a revisão de contexto fresco terminou sem HIGH aberto, e a revisão adversarial real deu `loop` PRONTO com `--conferir` CONFERE no commit final.
4. **Release**:
   - PR com CI verde em `ubuntu-latest` **e** `macos-latest`;
   - bloco do OK da `sdd-release` (0a item 8: `--conferir` e o `--ledger` num registro fora do commit);
   - OK do Roberto **citando "sdd-open" na mesma mensagem**. Sem isso, não faça o push;
   - push fast-forward em `main` (com a tag junto, se a versão for por tag: `git push --atomic origin HEAD:refs/heads/main refs/tags/vX.Y.Z`).

   Pronto quando: `gh release view <tag> -R robertodiasduarte/sdd-open` mostra `SHA256SUMS.txt` e `shasum -a 256 -c` confere. Se o run `release` não publicar, leia os jobs antes de qualquer outra coisa.
5. **Fechar**: rode a `sdd-handoff` com a etapa F13 no topo e o prompt da sessão seguinte (F14 Playbook e orquestração). Grave os artefatos na branch `docs/` **sem trocar de branch na worktree**:

   ```bash
   cd /Users/robertoduarte/rdd-worktrees/sdd-open-f13-ux-llm
   T=$(mktemp -d) && GIT_TERMINAL_PROMPT=0 git fetch -q origin docs/incorporar-starter
   git worktree add -q --detach "$T" origin/docs/incorporar-starter   # do remoto: a branch local pode estar atrás
   for d in features handoffs reports reviews; do mkdir -p "$T/sdd/$d" && rsync -a --delete "sdd/$d/" "$T/sdd/$d/"; done
   git -C "$T" add sdd/features sdd/handoffs sdd/reports sdd/reviews && git -C "$T" commit -q -m "docs(incorporar-starter): sessão 10 — F13 UX e LLM no código" && GIT_TERMINAL_PROMPT=0 git -C "$T" push -q origin HEAD:docs/incorporar-starter
   git worktree remove --force "$T"
   ```

## O que não quebrar

- **Contexto e governança (F12):** os 2 motivos do exit 5, a ordem marcador → linha → bloco e o `--print` isento (`tests/test_governanca_gate.py`); o permitido resolvido no snapshot de antes e o snapshot fora do worktree, **nunca no `.git`** (`tests/test_governanca_fronteira.py`); seções, campos, retornos e exits iguais no brief, no passo, no lint e no yaml (`tests/test_f12_textos.py`); o padrão "Step 1.5" e "slice 2" continua proibido no pacote (`tests/test_correcoes_w0.py`).
- **Revisão adversarial (F10 + F11):** os exits de `adversarial-review.sh` (0/64/65/66/67/68; `--conferir` 0/2; `--ledger` 0/2/64), as chaves do META e a identidade adapter + modelo são contrato (`tests/test_revisao.py`, `test_revisao_adapters.py`); o gate offline (`adversarial-review-gate.sh`, 0/2/3/64) nunca usa rede, CLI real nem o repositório de quem o chama (`tests/test_revisao_gate.py`); o `eval-agree.sh` só lê arquivos. A release exige `review_externo` (`--conferir` CONFERE, ou dispensa D3 com motivo).
- **Fluxo encadeado (F9):** os exits do `sdd-fluxo.sh` e o `--self-test` são contrato (`tests/test_fluxo.py`); nomes do `despachar` por lista explícita, nunca faixa `[A-Za-z]`.
- **Marcas e lint de decisões:** a tabela do item 9 do `PERGUNTA_DECISAO.md` é a dona dos rótulos; toda pergunta nova de decisão leva marca; `sdd-decisoes-lint.sh --sites` acha 18 nas skills e 2 nos fragmentos — uma pergunta nova muda essa contagem em `tests/test_decisoes_lint.py`.
- **Subseção `### Fluxo encadeado`:** bloco comum idêntico nas 9 skills de fase, dentro do `## Encerramento (obrigatório)`; "Por que cada regra existe" logo antes do Encerramento.
- **Hooks (F8):** `sdd/hooks/pre-commit` recusa com `RESULTADO: COMMIT RECUSADO`; a regra REPORT pula `sdd/fixtures/` e `sdd/templates/`; o `pre-push` nunca recusa; `tests/test_hooks.py`, `test_claude_adapter.py` e `test_alarme.py` são contrato.
- **`report-lint.py`** fail-closed (exits 0/1/64); **`verify-gate.sh`** com os seis exits (0/2/3/4/5/64), `--print`, `--trace` e as fixtures de `sdd/fixtures/`.
- **Camada de conversa** (F4 + F5): bloco comum em 15 `SKILL.md`, seção nas 17 (a skill nova entra), `FRASES` do `tests/test_conversa.py`.
- **`init`/`sync`/`doctor`:** o `init` nunca sobrescreve skill instalada nem `sdd/bin/*` (completa o que falta) e copia `sdd/fixtures/` só na 1ª instalação; `tests/test_sdd_open.py` fica.
- **Docs testados** (`tests/test_docs.py`): todo link de `README*.md` e `docs/**` abre; o roadmap conta 3 linhas; a linha "`sdd-loop-builder` and `sdd-drive`" fala das 2 skills: a F13 entrega só a 1ª, então a linha muda, mas não sai (`tests/test_docs.py::Roadmap`).
- **Contratos de `sdd/`:** `playbook-lint.sh --self-test` 0; o bloco do OK da `sdd-release` mantém rótulos, ordem e uma pergunta só (`tests/test_contrato_build_release.py`).
- **CI:** nada de caractere invisível nem `curl … | sh` literal em `.agents/skills/`; piso Python 3.9 / bash 3.2; `release.yml` com teto 25 no `testes` e 45 no `testes-macos` (a suíte levou 14m27s no Ubuntu e 27m58s no macOS na F12, com um corte nos 30 min antes do teto novo) — confira se a suíte maior ainda cabe.
- **Padrão agnóstico (P2):** `tests/test_agnostico.py` reprova `AskUserQuestion`, `TodoWrite`, `PreToolUse`, `PostToolUse`, `subagent_type`, `Task tool`, `Agent tool` e `/model` em `.agents/skills/**`, `sdd/templates/**`, `sdd/hooks/**`, `AGENTS.md.tmpl` e `sdd/playbook.md`. Os nomes de engine são dado do `registry.tsv` e dos adapters em `sdd/bin/adapters/`, não texto de skill.
- **Literais que o publish-gate reprova** (`scripts/publish-gate-patterns.txt`): e-mail só em `example.*`; CPF, CNPJ, telefone, 11+ dígitos e caminho `/Users/<nome>/` fora de arquivo rastreado; o G1 (gitleaks) varre `tests/` e `sdd/review/stubs/` — chave de API nunca em arquivo, nem em stub.
- **Arquivos:** `python3 -B` e `git add` por nome; bash 3.2; `rm -rf` só com `"${X:?}"`; `sdd/features|handoffs|reports|reviews|traces/` **nunca** entram em commit da branch de trabalho; todo arquivo novo no `MANIFEST.txt`.
- **Push e remoto:** todo comando remoto com `GIT_TERMINAL_PROMPT=0`; push em `main` só com OK explícito do Roberto citando "sdd-open"; nunca `--force`; a branch `docs/incorporar-starter` nunca vira PR.
- **Fora de escopo nesta sessão:** curator, `/drive`, `drive.*` e `sdd/invariants.md` (F14); a revisão focada na fronteira de escrita (F14); regenerar o sdd-starter; alterar o sdd-starter ou o repositório privado.

## Como fechar

Ao terminar, rode a skill **SDD Handoff by RDD** de novo para registrar o que foi feito
e preparar a próxima retomada.
