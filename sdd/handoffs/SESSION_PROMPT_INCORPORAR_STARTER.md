# Continuar: INCORPORAR_STARTER — sessão 11: F14 Playbook e orquestração

Esta sessão roda **dentro da worktree** `/Users/robertoduarte/rdd-worktrees/sdd-open-f14-playbook`, branch `feat/f14-playbook`, já criada de `origin/main` = `b1348bd` (tag `v2.5.0`). Os artefatos SDD da família (features, handoffs, reports, reviews) já estão no disco, fora do commit; a fonte deles é a branch `docs/incorporar-starter` do remoto, nunca mesclada em `main`.

## Conferir a worktree (antes de ler qualquer coisa)

A frente da F14 **já foi aberta**: não rode `git worktree add`. Confira que está tudo no lugar:

```bash
git rev-parse --show-toplevel                                             # esperado: /Users/robertoduarte/rdd-worktrees/sdd-open-f14-playbook
git branch --show-current                                                 # esperado: feat/f14-playbook
git log --oneline -1                                                      # esperado: b1348bd ou mais novo
git rev-parse -q --verify 'v2.5.0^{commit}'                               # base do check-versions; esperado: b1348bd…
git status --short | head -4                                              # esperado: só "?? sdd/…"
ls sdd/handoffs/HANDOFF_INCORPORAR_STARTER.md sdd/features/PLANO_F4_F15_CONSOLIDADO.md
```

Se a sessão abriu em outra pasta, pare e peça ao Roberto para abrir o agente na pasta da worktree: nenhum `cd` muda a pasta à qual a sessão fica presa. Se a worktree não existir, recrie a partir do clone principal e reabra a sessão nela:

```bash
cd /Users/robertoduarte/rdd-public/sdd-open
GIT_TERMINAL_PROMPT=0 git fetch -q origin
git worktree add /Users/robertoduarte/rdd-worktrees/sdd-open-f14-playbook -b feat/f14-playbook origin/main
cd /Users/robertoduarte/rdd-worktrees/sdd-open-f14-playbook
GIT_TERMINAL_PROMPT=0 git fetch -q origin tag v2.5.0                      # base do check-versions
GIT_TERMINAL_PROMPT=0 git fetch -q origin docs/incorporar-starter
git checkout origin/docs/incorporar-starter -- sdd/features sdd/handoffs sdd/reports sdd/reviews
git rm -r -q --cached sdd/features sdd/handoffs sdd/reports sdd/reviews   # ficam no disco, fora do commit
```

Não trabalhe na worktree antiga `sdd-open-f13-ux-llm` (branch já mesclada). O `sdd/ambiente.md` do checkout principal é nota local da `sdd-new-session` do starter, não rastreada; não o commite.

Depois, leia nesta ordem:
- `sdd/features/PLANO_F4_F15_CONSOLIDADO.md`:
  - seção 0 (P1–P4; a F14 segue no **P4**);
  - seção 8: o preâmbulo, **8.0** (as 10 regras do PORTE, com a tabela de degradação), o quadro **"F14 Playbook, orquestração e sessão"**;
  - **8.1** "F14 Playbook e orquestração" (P1–P4, O1–O4, N1, N3), **8.2** (slots `drive.*`, `drive.max_tokens` candidato a cair) e **8.3** (fontes no privado);
  - seção 10 (uma frente por sessão; a F16 não pareia com a F14).
- `sdd/handoffs/HANDOFF_INCORPORAR_STARTER.md`: a Ficha, `## Eventos` e a etapa "F13", que é a do topo.
- `.agents/skills/sdd-playbook/`, `sdd/playbook.md`, `sdd/bin/playbook-lint.sh`, `.agents/skills/sdd-release/SKILL.md` (onde entram P3, P4, O2 e o item 10), `.agents/skills/sdd-build/references/modos-e-retry.md` (o modo ralph que o `sdd-drive` reaproveita), `.agents/skills/sdd-new-session/` (N1) e `sdd/templates/` (N3).

## Onde paramos

- **F1–F13, W0 e M1 entregues; o P3 (starter) está concluído; o P4 está na F14.** A última Release é https://github.com/robertodiasduarte/sdd-open/releases/tag/v2.5.0: tag em `b1348bd`, runs `release` 41930183324 e 41930183618, `SHA256SUMS.txt` conferido (`00a340380e098afc3dcc2fbd7e97b4b18dbaf4b918dd6eb36c6d910cec7023bf`).
- **Estado do pacote:** 18 skills; **1.134 testes** verdes no piso `SDD_TEST_BASH=/bin/bash /usr/bin/python3` (Python 3.9.6, bash 3.2.57), local e no CI (no último PR, Ubuntu 14m18s, macOS 28m33s); roadmap (`docs/roadmap.md` + PT) com 3 linhas; `MANIFEST.txt` 415 linhas.
- **A sessão 10 fez a F13** do brainstorm à release; esta sessão faz a **F14 inteira**, do brainstorm à release. A F15 é a sessão 12+.
- **A F13 deixou 3 riscos aceitos pelo Roberto:** 2º revisor dispensado nas 2 últimas rodadas, prova real sem rodada completa no commit final, último veredito do avaliador em NEEDS_WORK. **A conta do Codex ficou sem créditos:** confira antes de contar com ele (`codex exec` responde `Your workspace is out of credits`); sem créditos, o 2º revisor sai 67 e a prova real não roda, e isso é pergunta ao Roberto antes de começar a revisão.

## Contexto que você precisa ter

- **Remoto:** `https://github.com/robertodiasduarte/sdd-open.git`.
- **Release automática:** sai no push de `main` que toca `.agents/skills/**`, `bin/**`, `sdd/bin/**`, `sdd/hooks/**`, `sdd/templates/**`, `sdd/fixtures/**`, `sdd/review/**`, `sdd/patterns/**`, `sdd/WORKFLOW_CONTRACTS.yaml`, `sdd/playbook.md`, `sdd/config.example.yaml` ou `AGENTS.md.tmpl`. O patch vem de `scripts/next-version.sh` (dá `v2.5.1`); uma tag `vX.Y.Z` empurrada à mão junto com `main` publica exatamente essa tag (foi assim na `v2.5.0`). O job `release` espera `testes` (teto 25 min) **e** `testes-macos` (teto 45 min).
- **Escopo da F14** (plano, quadro F14 e 8.1):
  - **C5** `sdd/invariants.md` (adiado da F12);
  - **P1** `sdd/bin/playbook-curator.sh`: `--colher` (ajudou de tabela ✔, mordeu de AVAL/WAIVED, SUGESTAO por `sup:`, CANDIDATO/REJEITADO, PROMOVER?, `--desde`) e `--aplicar`, que valida a gramática antes de editar; fixtures em `sdd/fixtures/playbook/`;
  - **P2** brief `sdd-playbook/references/curator.md`: agente read-only devolve `<<<CURADORIA>>>`; toda linha da colheita aparece; flag CONTAMINAÇÃO; ACEITAR exige `arquivo:linha`;
  - **P3** no `sdd-release`: contadores com evidência aplicados sem perguntar; ADD/TOMBSTONE/PROMOVER vão para pergunta `[D3 · muda a regra do método]`;
  - **P4** robustez do 17b: rc=2 não é "0 deltas"; staging por cópia; evidência `CURATOR-*.log`; commit do curator à parte com revalidação de IDs;
  - **O1** skill nova `.agents/skills/sdd-drive/` + `sdd/bin/sdd-drive.sh`: design → (build → verify)* com o Verify Gate como parada; orçamento de rodadas e tokens; `--resume`; tabela de motivos de parada; DRIVE_REPORT; barreira dura antes do release; reaproveita o modo ralph;
  - **O2** raio de impacto por superfície no `sdd-release`: um subagente por superfície, sequencial no vendor sem subagente, citando invariantes do módulo;
  - **O3** `sdd/bin/deploy-do-sha.sh` sobre `gh run`: espera o run do SHA até 40 min em background e redispara 1× em falha transitória; deve ser a mesma lógica do item 10 da `sdd-release`, não duas;
  - **O4** `sdd/bin/sdd-archive.py`: retroativo, com dry-run; conflito de changelog = `--ours` + prepend; a colheita de permissões do privado é só de um agente e não viaja;
  - **N1** `sdd-new-session` copia BRAINSTORM/DEFINE/DESIGN untracked do checkout principal só com match exato slug ↔ feature; lista os parecidos sem copiar;
  - **N3** `HANDOFF_TEMPLATE.md` completo (o `handoff-lint` da F4 já aceita as seções extras);
  - **do handoff:** a revisão focada na fronteira de escrita (risco aceito na F12) e o isolamento de `SDD_TRACE` em `tests/apoio.py` (🐛 da F12). As pendências LOW da F13 (`design-lint`, `prompt-drift-scan.sh`, na etapa F13 do handoff) entram se couberem: pergunte.
- **Fontes no privado** (só leitura; o repositório privado **não** se altera). Leia do `origin/main` do privado (`git -C /Users/robertoduarte/RDD/Wordpress show 'origin/main:<arquivo>'`; o checkout local dele fica atrás; ponha o caminho entre aspas, porque no zsh `$R:s…` é um modificador): `scripts/playbook-curator.sh` (724 linhas, 5 refs RDD), `.claude/agents/workflow/curator-playbook.md`, `.claude/commands/workflow/drive.md`, `scripts/sdd-archive.py` (177, 6), `scripts/new-session.sh` (208, 3), `scripts/release/deploy-do-sha.mjs`, `scripts/fixtures/curator/`. Específico da RDD não viaja (regra 4 do 8.0). Receita por arquivo: `grep -niE 'supabase|deno|wordpress|wp-content|rdd-plataforma|hostinger|RDD/Wordpress|rdd-eval\.env|kimi|codex|gemini|muse|qwen|LM-[0-9]'`.
- **Decisões a levar ao brainstorm** (formato `PERGUNTA_DECISAO.md`, recomendada primeiro, com a marca da classe, "não sei", nunca "Outro"). O Roberto pediu, na sessão 10: **explicação para leigo, prós e contras, recomendação, e a decisão é dele**:
  - **D11**: slots `drive.max_rounds` e `drive.max_tokens` (este, candidato a cair; slot sem leitor é texto morto, como `schema.check_cmd` e `smoke.*`);
  - se a F14 cabe numa frente só (8 itens + 1 skill nova; o PORTE estima 4–5 dias) ou se divide em 2 sessões;
  - **versão da Release** (`v2.5.1` automática ou `v2.6.0` por tag: a F14 traz skill nova).
- **Decisões já tomadas, não reabrir:**
  - a camada de conversa fica sempre ligada; `flow.autonomous` liga o encadeamento, não a conversa;
  - toda pergunta tem a marca `[<código> · <rótulo>]`, a recomendada primeiro, "não sei" e nunca "Outro"; o OK da `sdd-release` fica sem marca;
  - vendor sem subagente degrada para `sdd-fluxo.sh despachar` → exit 40 e a parada ⏸️; o exit 40 não é por vendor;
  - o open é a fonte canônica de governança, auditoria-harness e prompt-builder; a KB fica em `sdd/kb/`; os artefatos SDD ficam na branch `docs/`;
  - `report-lint` fail-closed; hooks pelo `init` com confirmação; review externo obrigatório na release (R1, F10); governança em todo Define (D5, F12).
  - D1 da F14 já decidida na F9: o `/drive` só faz sentido com o mecanismo de autonomia; U3 e o ponto de extensão do smoke visual são da F15.
- **Skills do fluxo** (em `/Users/robertoduarte/.claude/skills/`): `sdd-brainstorm`, `sdd-define`, `sdd-design`, `sdd-build`, `sdd-handoff`. A `sdd-release` e a UX review são as do pacote. O DEFINE desta frente precisa da linha `| **Governança** | … |` no `## Technical Context`, vinda de um revisor fresco, senão o gate sai 5: rode o passo 11 de `.agents/skills/sdd-define/SKILL.md`.
  - Fluxo SDD completo, com revisão de contexto fresco do DESIGN (modo `contrato`) antes do build e do build depois (modo `veredito`). A `sdd-build` limita a 2 ciclos; um 3º é pergunta `[D4 · limite de tentativas]` ao Roberto, **mesmo sem HIGH aberto**: na F13, o agente seguiu sem perguntar, e o 3º ciclo achou uma regressão.
  - **No brief de cada avaliador**, mande gravar só `sdd/reports/evidence/F14_<…>/AVAL*-*.log` com o helper `ev.sh` (molde: `sdd/reports/evidence/F13_UX_LLM/ev.sh`: grava `$ cmd`, saída e `[exit=N]` real) e **proíba** terminar o comando passado a ele num formatador (`tail`, `head`, `tr`, `grep`, `wc`, `sed`). Peça também que nada seja gravado na pasta temporária do sistema fora de um `mktemp -d`, e que não rode `python3 -m py_compile` no projeto (grava `__pycache__` em `sdd/bin/`; use `ast.parse`).
  - O Bash da sessão é zsh: sem `PIPESTATUS`, lista numa variável não se divide em palavras (`set -- $x` também não, e os logs `at-*` da F13 saíram vazios assim), `=====` num `echo` quebra o comando e `!` num `grep` entre aspas duplas quebra a cadeia `&&`, cortando o resto em silêncio. Grave os logs com `/bin/bash -c` terminando em `[exit=$rc]`. Confira com `bash sdd/bin/gate-shell-evidencia.sh sdd/reports/evidence/<FEATURE>`.
  - **Não edite `sdd/bin/verify-gate.sh` enquanto o gate roda** (o bash lê o script aos pedaços e dá erro de sintaxe falso) e **não chame o gate com `SDD_TRACE=off`** (derruba 10 testes de trace: pendência 🐛 da F12).
  - O `report-lint` exige `evidence/<FEATURE>/` com o mesmo nome do `BUILD_REPORT_<FEATURE>.md`, a tabela reconhecida e a linha do avaliador. O DESIGN passa no `python3 sdd/bin/design-lint.py` e no `scripts/validate_design.py` da skill de design (chaves reprovam até dentro de código e de caminho; o BUILD_REPORT também).
- **Revisão adversarial real (R1 da release):** rode `bash sdd/bin/adversarial-review.sh --reviewer claude --auditor openrouter:qwen/qwen3.7-plus --feature <F>` (com ≥ 8 arquivos o `codex` entra sozinho como 2º revisor), `sdd-fluxo.sh loop … --rodada N` (teto 3) e `--conferir` na versão final; molde: `sdd/reports/evidence/F13_UX_LLM/real-rodada.sh <N>` (com `TETO=` e `SEM_REVISOR2=`). O ledger (`ledger-review.md`) precisa existir antes do `loop` e usa `APLICADA`, `REBATIDA_EVIDENCIA` ou `REBATIDA_ESCOPO`. A chave da OpenRouter está em `~/.config/rdd-eval.env` (`OPENROUTER_API_KEY`): carregue só no ambiente do processo, nunca grave. Custo por rodada ≈ US$ 2,35 na F13 (quase tudo nominal da assinatura do Claude). Antes, rode o gate offline: `bash sdd/bin/adversarial-review-gate.sh`. Na F12, consertos feitos depois da rodada 3 trouxeram regressão grave; na F13, restringir um sinal contra falso alarme cegou formas reais. Conserto novo pede teste de ataque **dos 2 lados**, não só o do caso relatado.
- **Prova num agente real:** se a frente mudar o texto de um passo que outro agente segue, rode a prova **depois** do último conserto. Na F12, um conserto da rodada 3 quebrou o despacho no Codex (`.git` é só leitura na sandbox) e só a execução real mostrou. Critério: efeito, nunca texto: a linha ` exited 40 in ` do transcript no despacho; arquivo no destino e um calço que registra a chamada real, como `sdd/reports/evidence/F13_UX_LLM/codex-roteador.sh` e `confere_roteador.py`, com controles que passam e que reprovam. **Nunca repita a prova com o mesmo nome de arquivo:** na F13, isso apagou os transcritos da execução que valia.
- **Versões atuais:**
  - auditoria-harness 1.1.1, brainstorm 2.2.0, build 2.6.0, checar-ambiente 1.4.1, define 2.5.0, design 2.5.0, governanca 2.4.0, handoff 2.1.1;
  - iterate 2.2.1, kb 2.2.1, loop-builder 1.0.0, new-session 1.3.0, playbook 2.1.1, prompt-builder 2.1.2, release 2.6.0, ux-review 2.5.0;
  - (portadas, sem a camada F4) higiene-dado 1.2.0, iniciar-repo 1.1.1.

  Toda skill tocada sobe de versão e atualiza a linha de identificação; os pinos de versão em `tests/test_contrato_build_release.py`, `test_correcoes_w0.py` e `test_matriz_new_session.py` mudam junto. Skill nova muda a contagem de `tests/test_skill_lint.py`, `test_conversa.py` e `test_docs.py` (18 → 19). Confira com `python3 scripts/check-versions.py --base v2.5.0 --base-obrigatoria`.

## Tarefas, em ordem

1. **Brainstorm da F14** com a `sdd-brainstorm`, gravando `sdd/features/BRAINSTORM_F14_PLAYBOOK.md` a partir do quadro F14 e do 8.1. Pronto quando: D11, o tamanho da frente e a versão foram respondidos pelo Roberto, a abordagem foi confirmada e os cortes YAGNI e os 2 checkpoints estão registrados.
2. **Define, governança, UX review e design**:
   - `sdd/features/DEFINE_F14_PLAYBOOK.md`, com ATs em EARS, a linha `Governança` e o `verify_gate` `kind: test` de sempre: `cmd` = `T=$(mktemp -d) && git archive HEAD | tar -x -C $T && PUBLISH_GATE_MODE=ci bash scripts/publish-gate.sh $T && cd $T && SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover -s tests -p 'test_*.py'`;
   - `sdd/reviews/UX_REVIEW_F14_PLAYBOOK.md`;
   - `sdd/features/DESIGN_F14_PLAYBOOK.md`, com o File Manifest e o Advisor Ledger.

   Pronto quando: `verify-gate.sh --print` 0, os 2 lints do DESIGN 0 e a revisão de contexto fresco do DESIGN aplicada. O `validate_define.py` e o `validate_design.py` da skill leem o título da seção de prompts e os títulos de seção até em prosa: não os cite no corpo.
3. **Build**, com commit antes do gate e todo arquivo novo no `MANIFEST.txt` (`LC_ALL=C sort`; o arquivo é igual a `git ls-files`). Pronto quando:
   - `bash sdd/bin/verify-gate.sh --strict sdd/features/DEFINE_F14_PLAYBOOK.md` 0 e `python3 sdd/bin/report-lint.py sdd/reports/BUILD_REPORT_F14_PLAYBOOK.md` 0;
   - `playbook-curator.sh --colher` sobre `sdd/fixtures/playbook/` produz os 4 tipos de linha; `sdd-drive.sh --dry-run` para no Verify Gate com motivo tabelado; `skill-lint.py .agents/skills/sdd-drive/SKILL.md` → 0;
   - todo script novo passa por `grep -nE 'mapfile|declare -A|\$\{[a-zA-Z_]+\^\^' <script>` sem achado, tem fixture e teste dos dois lados (regra 6 do 8.0), baseline vermelha na `v2.5.0` e 1 sabotagem;
   - `python3 sdd/bin/skill-lint.py --conversa .agents/skills/sdd-*/SKILL.md` 0 nas 19 skills e `bash sdd/bin/sdd-decisoes-lint.sh --sites .agents/skills sdd/templates/fragments` 0;
   - a revisão de contexto fresco terminou sem HIGH aberto, e a revisão adversarial real deu `loop` PRONTO com `--conferir` CONFERE no commit final.
4. **Release**:
   - PR com CI verde em `ubuntu-latest` **e** `macos-latest`;
   - bloco do OK da `sdd-release` (0a item 8: `--conferir` e o `--ledger` num registro fora do commit);
   - OK do Roberto **citando "sdd-open" na mesma mensagem**. Sem isso, não faça o push;
   - push fast-forward em `main` (com a tag junto, se a versão for por tag: `git push --atomic origin HEAD:refs/heads/main refs/tags/vX.Y.Z`).

   Pronto quando: `gh release view <tag> -R robertodiasduarte/sdd-open` mostra `SHA256SUMS.txt` e `shasum -a 256 -c` confere. Se o run `release` não publicar, leia os jobs antes de qualquer outra coisa.
5. **Fechar**: rode a `sdd-handoff` com a etapa F14 no topo e o prompt da sessão seguinte (F15 Substituição do SDD privado). Grave os artefatos na branch `docs/` **sem trocar de branch na worktree**:

   ```bash
   cd /Users/robertoduarte/rdd-worktrees/sdd-open-f14-playbook
   T=$(mktemp -d) && GIT_TERMINAL_PROMPT=0 git fetch -q origin docs/incorporar-starter
   git worktree add -q --detach "$T" origin/docs/incorporar-starter   # do remoto: a branch local pode estar atrás
   for d in features handoffs reports reviews; do mkdir -p "$T/sdd/$d" && rsync -a --delete "sdd/$d/" "$T/sdd/$d/"; done
   git -C "$T" add sdd/features sdd/handoffs sdd/reports sdd/reviews && git -C "$T" commit -q -m "docs(incorporar-starter): sessão 11 — F14 Playbook e orquestração" && GIT_TERMINAL_PROMPT=0 git -C "$T" push -q origin HEAD:docs/incorporar-starter
   git worktree remove --force "$T"
   ```

## O que não quebrar

- **UX e LLM (F13):** as saídas 0/2/64 e "nunca LIMPO sem ter lido" do `prompt-drift-scan.sh`, e 0/2/64 truncado do `contraste.sh` (`tests/test_prompt_drift_scan.py`, `test_contraste.py`); as colunas e os campos iguais em fragmento, template, lint e integração, e o roteador do passo 4 da `sdd-build` (`tests/test_f13_textos.py`); o inventário do `design-lint.py` (`tests/test_design_lint.py`).
- **Contexto e governança (F12):** os 2 motivos do exit 5, a ordem marcador → linha → bloco e o `--print` isento (`tests/test_governanca_gate.py`); o permitido resolvido no snapshot de antes e o snapshot fora do worktree, **nunca no `.git`** (`tests/test_governanca_fronteira.py`); seções, campos, retornos e exits iguais no brief, no passo, no lint e no yaml (`tests/test_f12_textos.py`); o padrão "Step 1.5" e "slice 2" continua proibido no pacote (`tests/test_correcoes_w0.py`).
- **Revisão adversarial (F10 + F11):** os exits de `adversarial-review.sh` (0/64/65/66/67/68; `--conferir` 0/2; `--ledger` 0/2/64), as chaves do META e a identidade adapter + modelo são contrato (`tests/test_revisao.py`, `test_revisao_adapters.py`); o gate offline (`adversarial-review-gate.sh`, 0/2/3/64) nunca usa rede, CLI real nem o repositório de quem o chama (`tests/test_revisao_gate.py`); o `eval-agree.sh` só lê arquivos. A release exige `review_externo` (`--conferir` CONFERE, ou dispensa D3 com motivo).
- **Fluxo encadeado (F9):** os exits do `sdd-fluxo.sh` e o `--self-test` são contrato (`tests/test_fluxo.py`); nomes do `despachar` por lista explícita, nunca faixa `[A-Za-z]`.
- **Marcas e lint de decisões:** a tabela do item 9 do `PERGUNTA_DECISAO.md` é a dona dos rótulos; toda pergunta nova de decisão leva marca; `sdd-decisoes-lint.sh --sites` acha 20 nas skills e 2 nos fragmentos — uma pergunta nova muda essa contagem em `tests/test_decisoes_lint.py`.
- **Subseção `### Fluxo encadeado`:** bloco comum idêntico nas 9 skills de fase, dentro do `## Encerramento (obrigatório)`; "Por que cada regra existe" logo antes do Encerramento.
- **Hooks (F8):** `sdd/hooks/pre-commit` recusa com `RESULTADO: COMMIT RECUSADO`; a regra REPORT pula `sdd/fixtures/` e `sdd/templates/`; o `pre-push` nunca recusa; `tests/test_hooks.py`, `test_claude_adapter.py` e `test_alarme.py` são contrato.
- **`report-lint.py`** fail-closed (exits 0/1/64); **`verify-gate.sh`** com os seis exits (0/2/3/4/5/64), `--print`, `--trace` e as fixtures de `sdd/fixtures/`.
- **Camada de conversa** (F4 + F5 + F13): bloco comum em 16 `SKILL.md`, seção nas 18 (a skill nova entra), `FRASES` do `tests/test_conversa.py`.
- **`init`/`sync`/`doctor`:** o `init` nunca sobrescreve skill instalada nem `sdd/bin/*` (completa o que falta) e copia `sdd/fixtures/` só na 1ª instalação; `tests/test_sdd_open.py` fica.
- **Docs testados** (`tests/test_docs.py`): todo link de `README*.md` e `docs/**` abre; o roadmap conta 3 linhas; a linha `sdd-drive` sai com a F14, e o mecanismo vem com o documento dele: a contagem vai a 2 em `tests/test_docs.py::Roadmap`.
- **Contratos de `sdd/`:** `playbook-lint.sh --self-test` 0; o bloco do OK da `sdd-release` mantém rótulos, ordem e uma pergunta só (`tests/test_contrato_build_release.py`).
- **CI:** nada de caractere invisível nem `curl … | sh` literal em `.agents/skills/`; piso Python 3.9 / bash 3.2; `release.yml` com teto 25 no `testes` e 45 no `testes-macos` (a suíte levou 14m18s no Ubuntu e 28m33s no macOS na F13) — confira se a suíte maior ainda cabe.
- **Padrão agnóstico (P2):** `tests/test_agnostico.py` reprova `AskUserQuestion`, `TodoWrite`, `PreToolUse`, `PostToolUse`, `subagent_type`, `Task tool`, `Agent tool` e `/model` em `.agents/skills/**`, `sdd/templates/**`, `sdd/hooks/**`, `AGENTS.md.tmpl` e `sdd/playbook.md`. Os nomes de engine são dado do `registry.tsv` e dos adapters em `sdd/bin/adapters/`, não texto de skill.
- **Literais que o publish-gate reprova** (`scripts/publish-gate-patterns.txt`): e-mail só em `example.*`; CPF, CNPJ, telefone, 11+ dígitos e caminho `/Users/<nome>/` fora de arquivo rastreado; o G1 (gitleaks) varre `tests/` e `sdd/review/stubs/` — chave de API nunca em arquivo, nem em stub.
- **Arquivos:** `python3 -B` e `git add` por nome; bash 3.2; `rm -rf` só com `"${X:?}"`; `sdd/features|handoffs|reports|reviews|traces/` **nunca** entram em commit da branch de trabalho; todo arquivo novo no `MANIFEST.txt`.
- **Push e remoto:** todo comando remoto com `GIT_TERMINAL_PROMPT=0`; push em `main` só com OK explícito do Roberto citando "sdd-open"; nunca `--force`; a branch `docs/incorporar-starter` nunca vira PR.
- **Fora de escopo nesta sessão:** a troca do privado e o ponto de extensão do smoke visual (F15); F16 e F17; regenerar o sdd-starter; alterar o sdd-starter ou o repositório privado.

## Como fechar

Ao terminar, rode a skill **SDD Handoff by RDD** de novo para registrar o que foi feito
e preparar a próxima retomada.
