# Continuar: INCORPORAR_STARTER — sessão 9: F12 Contexto, patterns e governança

Esta sessão começa numa **worktree limpa**. Os artefatos SDD da família (features, handoffs, reports, reviews) vivem na branch `docs/incorporar-starter` do remoto, nunca mesclada em `main`.

## Preparar a worktree (antes de ler qualquer coisa)

A frente da F12 **ainda não foi aberta**. Crie a worktree a partir de `origin/main` = `9508ff0` (tag `v2.3.1`) e traga os artefatos SDD da branch `docs/` (fora do commit):

```bash
cd /Users/robertoduarte/rdd-public/sdd-open
GIT_TERMINAL_PROMPT=0 git fetch -q origin
git worktree add /Users/robertoduarte/rdd-worktrees/sdd-open-f12-contexto -b feat/f12-contexto origin/main
cd /Users/robertoduarte/rdd-worktrees/sdd-open-f12-contexto
git log --oneline -1                                                      # esperado: 9508ff0 ou mais novo
GIT_TERMINAL_PROMPT=0 git fetch -q origin tag v2.3.1                      # base do check-versions
GIT_TERMINAL_PROMPT=0 git fetch -q origin docs/incorporar-starter
git checkout origin/docs/incorporar-starter -- sdd/features sdd/handoffs sdd/reports sdd/reviews
git rm -r -q --cached sdd/features sdd/handoffs sdd/reports sdd/reviews   # ficam no disco, fora do commit
git status --short | head -4                                              # esperado: só "?? sdd/…"
ls sdd/handoffs/HANDOFF_INCORPORAR_STARTER.md sdd/features/PLANO_F4_F15_CONSOLIDADO.md
command -v codex claude                                                   # o Codex CLI prova o despacho (P2)
```

Se `/Users/robertoduarte/rdd-public/sdd-open` não for o clone de `https://github.com/robertodiasduarte/sdd-open.git`, use a worktree da sessão 8 como base (`git -C /Users/robertoduarte/rdd-worktrees/sdd-open-f11-gate worktree add …`), se ela ainda existir. Não trabalhe nas worktrees antigas `sdd-open-f10-revisao` e `sdd-open-f11-gate` (branches já mescladas). O checkout principal está em `89ac76f` (`main` local atrás de `origin/main`); o `sdd/ambiente.md` dele é nota local da `sdd-new-session` do starter, não rastreada; não o commite.

Depois, leia nesta ordem:
- `sdd/features/PLANO_F4_F15_CONSOLIDADO.md`:
  - seção 0 (P1–P4; a F12 segue no **P4** e é uma das duas frentes que o **P2** manda provar no Codex CLI);
  - seção 8: o preâmbulo, **8.0** (as 10 regras do PORTE e a tabela de degradação: cartógrafo e revisor de governança sem subagente → `sdd-fluxo.sh despachar` → exit 40), o quadro **"F12 Contexto, patterns e governança"**;
  - **8.1** "F12 Contexto e governança" (C1–C9), **8.2** (slot `schema.check_cmd`, candidato a cair) e **8.3** (fontes no privado);
  - seção 10 (uma frente por sessão).
- `sdd/handoffs/HANDOFF_INCORPORAR_STARTER.md`: a Ficha, `## Eventos` e as etapas "F11" e "F10", que são as do topo.
- `.agents/skills/sdd-define/SKILL.md` (onde entram o Step 1.5 do cartógrafo e o Step 6.5 da governança), `.agents/skills/sdd-governanca/SKILL.md` (o open é a fonte canônica: o passo entra na `sdd-define`, a skill não é reescrita), `.agents/skills/sdd-design/SKILL.md` (contexto por domínio, landmine inteira, bucket de UX), `sdd/bin/design-lint.py` (os títulos de ADR que o C4 lê), `sdd/bin/verify-gate.sh` (exit 5 = clarificação aberta) e `sdd/templates/fragments/FLUXO_ENCADEADO.md` (despacho).

## Onde paramos

- **F1–F11, W0 e M1 entregues; o P3 (starter) está concluído; o P4 está na F12.** A última Release é https://github.com/robertodiasduarte/sdd-open/releases/tag/v2.3.1: tag em `9508ff0`, publicada automática no push de `main` (run `release` 41307505438), `SHA256SUMS.txt` conferido (`def48c99e135bd394bb11f9673a87ca56476711d666f0923cbf246ce75ff8ecc`). A `v2.3.0` (F10) saiu por tag em `248301d`.
- **Estado do pacote:** 17 skills; **894 testes** verdes no piso `SDD_TEST_BASH=/bin/bash /usr/bin/python3` (Python 3.9.6, bash 3.2.57), local e no CI (≈ 13 min no Ubuntu, ≈ 18 no macOS); roadmap (`docs/roadmap.md` + PT) com 4 linhas; `MANIFEST.txt` 353 linhas.
- **A sessão 8 fez F10 + F11** do brainstorm à release (o par permitido); esta sessão faz a **F12 inteira**, do brainstorm à release.

## Contexto que você precisa ter

- **Remoto:** `https://github.com/robertodiasduarte/sdd-open.git`.
- **Release automática:** sai no push de `main` que toca `.agents/skills/**`, `bin/**`, `sdd/bin/**`, `sdd/hooks/**`, `sdd/templates/**`, `sdd/fixtures/**`, `sdd/review/**`, `sdd/playbook.md`, `sdd/config.example.yaml` ou `AGENTS.md.tmpl`. O patch vem de `scripts/next-version.sh` (dá `v2.3.2`); uma tag `vX.Y.Z` empurrada à mão junto com `main` publica exatamente essa tag (foi assim na `v2.3.0`). O job `release` espera `testes` (teto 25 min) **e** `testes-macos` (teto 30 min).
- **Escopo da F12** (plano, quadro F12 e 8.1), C1–C11 e a correção 4.6 do PORTE:
  - **C1** cartógrafo de domínio no `sdd-define` Step 1.5 + `sdd/bin/contexto-lint.sh` + brief `sdd-define/references/cartografo.md` (heurística gerar/reusar/pular; agente fresco faz engenharia reversa com `arquivo:linha`; validade por `git diff <sha>..<default_branch> -- <superfícies>`; prova de que só o agente escreveu; **máx. 2 domínios por feature**; camadas de `layers:`) — recoloca o "CONTEXTO de domínio" que a W0 tirou do template;
  - **C2** contexto por domínio no `sdd-design`; **C3** `sdd/patterns/README.md` + `sdd/bin/patterns-lint.sh` (cita `§Esqueleto (validado_em)`; `--design` bloqueia pattern vencido ou path morto); **C4** `sdd/bin/docs-extract-decisions.sh` gera `docs/adr/index.md` com órfãos, sobre os títulos de ADR do `design-lint`; **C5** `sdd/invariants.md` (`--cruzar`/`--validar-inv` ficam com o curator, F14);
  - **C6/C7** governança obrigatória no `sdd-define` Step 6.5, roda sempre (inclusive com `--parar`), N.A. permitido; 2ª falha ou clarificação aberta grava `[NEEDS CLARIFICATION: governança não rodou…]` → `verify-gate.sh` exit 5;
  - **C8** `sdd/bin/governanca-fronteira.sh` + brief `sdd-governanca/references/revisor.md` (prompt só com 5 campos; snapshot sha256 antes/depois prova que o revisor só escreveu o relatório; 1 redespacho; bloco `<<<GOVERNANCA>>>`);
  - **C9** `sdd/WORKFLOW_CONTRACTS.yaml` reduzido a produtor/consumidor do gate, schema e invariantes do cartógrafo e do revisor; **C10** abrir a ficha inteira da landmine no `sdd-design`; **C11** bucket de UX indeterminado trava o design.
- **Fontes no privado** (só leitura; o repositório privado **não** se altera). Leia do `origin/main` do privado (`git -C /Users/robertoduarte/RDD/Wordpress show origin/main:<arquivo>`; o checkout local dele fica atrás): `scripts/contexto-lint.sh` (457 linhas, 12 refs RDD), `scripts/patterns-lint.sh` (461, 4), `scripts/docs-extract-decisions.sh` (164, 0), `scripts/governanca-fronteira.sh` (110, 5); camadas `edge/sql/wp-content` viram `layers:`; `patterns/dominio.md` vira `sdd/patterns/`. Específico da RDD não viaja (regra 4 do 8.0).
- **Decisões a levar ao brainstorm** (formato `PERGUNTA_DECISAO.md`, recomendada primeiro, com a marca da classe, "não sei", nunca "Outro"):
  - **D5** (governança obrigatória no Define; recomendado: sim, com N.A. registrado) — `[D3 · muda a regra do método]`;
  - **D8** (dono do `prova_script`, correção 4.6; recomendado: o `sdd-define` Step 6.5);
  - o slot `schema.check_cmd` (recomendado: cai — a revisão de schema não viaja);
  - F12 numa Release só ou em duas (contexto/patterns × governança) — a frente é a maior do P4 (5–7 dias no PORTE);
  - versão da Release (`v2.3.2` automática ou `v2.4.0` por tag — a F12 muda o `sdd-define` de toda feature).
- **Decisões já tomadas, não reabrir:**
  - a camada de conversa fica sempre ligada; `flow.autonomous` liga o encadeamento, não a conversa;
  - toda pergunta tem a marca `[<código> · <rótulo>]`, a recomendada primeiro, "não sei" e nunca "Outro"; o OK da `sdd-release` fica sem marca;
  - vendor sem subagente degrada para `sdd-fluxo.sh despachar` → exit 40 e a parada ⏸️; o exit 40 não é por vendor;
  - o open é a fonte canônica de governança, auditoria-harness e prompt-builder; a KB fica em `sdd/kb/`; os artefatos SDD ficam na branch `docs/`;
  - `report-lint` fail-closed; hooks pelo `init` com confirmação; review externo obrigatório na release (R1, F10).
- **Skills do fluxo** (em `/Users/robertoduarte/.claude/skills/`): `sdd-brainstorm`, `sdd-define`, `sdd-design`, `sdd-build`, `sdd-handoff`. A `sdd-release` e a UX review são as do pacote.
  - Fluxo SDD completo, com revisão de contexto fresco do DESIGN (modo `contrato`) antes do build e do build depois (modo `veredito`). A `sdd-build` limita a 2 ciclos; um 3º é pergunta `[D4 · limite de tentativas]` ao Roberto.
  - **No brief de cada avaliador**, mande gravar só `sdd/reports/evidence/F12_<…>/AVAL*-*.log` com o helper `ev.sh` (molde: `sdd/reports/evidence/F11_GATE/ev.sh` — grava `$ cmd`, saída e `[exit=N]` real) e **proíba** terminar o comando passado a ele num formatador (`tail`, `head`, `tr`, `grep`, `wc`, `sed`): na F11, 6 logs dos avaliadores caíram no `gate-shell-evidencia.sh` por isso e viraram `.sonda.txt`. Peça também que nada seja gravado na pasta temporária do sistema fora de um `mktemp -d`.
  - O Bash da sessão é zsh (sem `PIPESTATUS`): grave os logs com `/bin/bash -c` terminando em `[exit=$rc]`. Confira com `bash sdd/bin/gate-shell-evidencia.sh sdd/reports/evidence/<FEATURE>`.
  - **Codex CLI como avaliador ou para provar o exit 40:** o 0.163 abre colaborador mesmo com `--disable multi_agent`; `codex exec` precisa de repositório git (commite a cópia temporária) e `~/.codex/skills/` tem cópias velhas das skills SDD — isole com `CODEX_HOME` temporário só com o `auth.json` e `--ignore-user-config`; para provar o 40, ponha "sem subagente nem colaborador" no prompt (molde: `sdd/reports/evidence/F9_FLUXO/codex.sh`).
  - O `report-lint` exige `evidence/<FEATURE>/` com o mesmo nome do `BUILD_REPORT_<FEATURE>.md`, a tabela reconhecida e a linha do avaliador. O DESIGN passa no `python3 sdd/bin/design-lint.py` e no `scripts/validate_design.py` da skill de design (chaves `{…}` reprovam até dentro de código e de caminho; o BUILD_REPORT também).
- **Revisão adversarial real (R1 da release):** rode `bash sdd/bin/adversarial-review.sh --reviewer claude --auditor openrouter:qwen/qwen3.7-plus --feature <F>` (com ≥ 8 arquivos o `codex` entra sozinho como 2º revisor), `sdd-fluxo.sh loop … --rodada N` (teto 3) e `--conferir` na versão final; molde: `sdd/reports/evidence/F11_GATE/real-rodada1.sh`. A chave da OpenRouter está em `~/.config/rdd-eval.env` (`OPENROUTER_API_KEY`): carregue só no ambiente do processo, nunca grave. Custo por rodada ≈ US$ 1,15 (quase tudo nominal da assinatura do Claude). Antes, rode o gate offline: `bash sdd/bin/adversarial-review-gate.sh`.
- **Versões atuais:**
  - auditoria-harness 1.1.1, brainstorm 2.2.0, build 2.5.0, checar-ambiente 1.4.1, define 2.4.0, design 2.3.0, governanca 2.3.0, handoff 2.1.1;
  - iterate 2.2.0, kb 2.2.1, new-session 1.3.0, playbook 2.1.1, prompt-builder 2.1.1, release 2.6.0, ux-review 2.4.0;
  - (portadas, sem a camada F4) higiene-dado 1.2.0, iniciar-repo 1.1.1.

  Toda skill tocada sobe de versão e atualiza a linha de identificação; os pinos de versão em `tests/test_contrato_build_release.py`, `test_correcoes_w0.py` e `test_matriz_new_session.py` mudam junto. Confira com `python3 scripts/check-versions.py --base v2.3.1 --base-obrigatoria`.

## Tarefas, em ordem

1. **Brainstorm da F12** com a `sdd-brainstorm`, gravando `sdd/features/BRAINSTORM_F12_CONTEXTO.md` a partir do quadro F12 e do 8.1. Pronto quando: D5, D8, o `schema.check_cmd`, uma ou duas Releases e a versão foram respondidas pelo Roberto, a abordagem foi confirmada e os cortes YAGNI e os 2 checkpoints estão registrados.
2. **Define, UX review e design**:
   - `sdd/features/DEFINE_F12_CONTEXTO.md`, com ATs em EARS e o `verify_gate` `kind: test` de sempre: `cmd` = `T=$(mktemp -d) && git archive HEAD | tar -x -C $T && PUBLISH_GATE_MODE=ci bash scripts/publish-gate.sh $T && cd $T && SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover -s tests -p 'test_*.py'`;
   - `sdd/reviews/UX_REVIEW_F12_CONTEXTO.md` (a interface é o que o `sdd-define` mostra no Step 1.5 e no 6.5 e a parada ⏸️ do cartógrafo);
   - `sdd/features/DESIGN_F12_CONTEXTO.md`, com o File Manifest e o Advisor Ledger.

   Pronto quando: `verify-gate.sh --print` 0, os 2 lints do DESIGN 0 e a revisão de contexto fresco do DESIGN aplicada.
3. **Build**, com commit antes do gate e todo arquivo novo no `MANIFEST.txt` (`LC_ALL=C sort`; o arquivo é igual a `git ls-files`). Pronto quando:
   - `bash sdd/bin/verify-gate.sh --strict sdd/features/DEFINE_F12_CONTEXTO.md` 0 e `python3 sdd/bin/report-lint.py sdd/reports/BUILD_REPORT_F12_CONTEXTO.md` 0;
   - `contexto-lint.sh --self-test` e `patterns-lint.sh --self-test` → 0; DEFINE sem a linha `Governança` → `verify-gate.sh` exit 5; `governanca-fronteira.sh` detecta escrita fora do relatório;
   - o despacho do cartógrafo (e do revisor de governança) provado no Codex CLI: exit 40 com o brief gravado (P2);
   - todo script novo passa por `grep -nE 'mapfile|declare -A|\$\{[a-zA-Z_]+\^\^' <script>` sem achado, tem fixture e teste dos dois lados (regra 6 do 8.0), baseline vermelha na `v2.3.1` e 1 sabotagem;
   - `python3 sdd/bin/skill-lint.py --conversa .agents/skills/sdd-*/SKILL.md` 0 nas 17 skills e `bash sdd/bin/sdd-decisoes-lint.sh --sites .agents/skills sdd/templates/fragments` 0;
   - a revisão de contexto fresco terminou sem HIGH aberto, e a revisão adversarial real deu `loop` PRONTO com `--conferir` CONFERE no commit final.
4. **Release**:
   - PR com CI verde em `ubuntu-latest` **e** `macos-latest`;
   - bloco do OK da `sdd-release` (0a item 8: `--conferir` e o `--ledger` num registro fora do commit);
   - OK do Roberto **citando "sdd-open" na mesma mensagem**. Sem isso, não faça o push;
   - push fast-forward em `main` (com a tag junto, se a versão for por tag: `git push --atomic origin HEAD:refs/heads/main refs/tags/vX.Y.Z`).

   Pronto quando: `gh release view <tag> -R robertodiasduarte/sdd-open` mostra `SHA256SUMS.txt` e `shasum -a 256 -c` confere. Se o run `release` não publicar, leia os jobs antes de qualquer outra coisa.
5. **Fechar**: rode a `sdd-handoff` com a etapa F12 no topo e o prompt da sessão seguinte (F13 UX e LLM no código). Grave os artefatos na branch `docs/` **sem trocar de branch na worktree**:

   ```bash
   cd /Users/robertoduarte/rdd-worktrees/sdd-open-f12-contexto
   T=$(mktemp -d) && GIT_TERMINAL_PROMPT=0 git fetch -q origin docs/incorporar-starter
   git worktree add -q --detach "$T" origin/docs/incorporar-starter   # do remoto: a branch local pode estar atrás
   for d in features handoffs reports reviews; do mkdir -p "$T/sdd/$d" && rsync -a --delete "sdd/$d/" "$T/sdd/$d/"; done
   git -C "$T" add sdd/features sdd/handoffs sdd/reports sdd/reviews && git -C "$T" commit -q -m "docs(incorporar-starter): sessão 9 — F12 Contexto e governança" && GIT_TERMINAL_PROMPT=0 git -C "$T" push -q origin HEAD:docs/incorporar-starter
   git worktree remove --force "$T"
   ```

## O que não quebrar

- **Revisão adversarial (F10 + F11):** os exits de `adversarial-review.sh` (0/64/65/66/67/68; `--conferir` 0/2; `--ledger` 0/2/64), as chaves do META e a identidade adapter + modelo são contrato (`tests/test_revisao.py`, `test_revisao_adapters.py`); o gate offline (`adversarial-review-gate.sh`, 0/2/3/64) nunca usa rede, CLI real nem o repositório de quem o chama (`tests/test_revisao_gate.py`); o `eval-agree.sh` só lê arquivos. A release exige `review_externo` (`--conferir` CONFERE, ou dispensa D3 com motivo).
- **Fluxo encadeado (F9):** os exits do `sdd-fluxo.sh` e o `--self-test` são contrato (`tests/test_fluxo.py`); o `loop` lê 2º revisor, revisão rasa e desempate; o `--log` é regravado em toda saída; nomes do `despachar` por lista explícita, nunca faixa `[A-Za-z]` (no bash 3.2 com UTF-8 ela aceita acento).
- **Marcas e lint de decisões:** a tabela do item 9 do `PERGUNTA_DECISAO.md` é a dona dos rótulos; toda pergunta nova de decisão leva marca; `sdd-decisoes-lint.sh --sites` acha 16 nas skills e 2 nos fragmentos (a F10 acrescentou a D3 da `sdd-release`) — uma pergunta nova muda essa contagem em `tests/test_decisoes_lint.py`.
- **Subseção `### Fluxo encadeado`:** bloco comum idêntico nas 9 skills de fase, dentro do `## Encerramento (obrigatório)`; "Por que cada regra existe" logo antes do Encerramento.
- **Hooks (F8):** `sdd/hooks/pre-commit` recusa com `RESULTADO: COMMIT RECUSADO`; a regra REPORT pula `sdd/fixtures/` e `sdd/templates/`; o `pre-push` nunca recusa; `tests/test_hooks.py`, `test_claude_adapter.py` e `test_alarme.py` são contrato.
- **`report-lint.py`** fail-closed (exits 0/1/64); **`verify-gate.sh`** com os seis exits (0/2/3/4/5/64), `--print`, `--trace` e as fixtures de `sdd/fixtures/`.
- **Camada de conversa** (F4 + F5): bloco comum em 15 `SKILL.md`, seção nas 17, `FRASES` do `tests/test_conversa.py`.
- **`init`/`sync`/`doctor`:** o `init` nunca sobrescreve skill instalada nem `sdd/bin/*` (completa o que falta) e copia `sdd/fixtures/` só na 1ª instalação; `tests/test_sdd_open.py` fica.
- **Docs testados** (`tests/test_docs.py`): todo link de `README*.md` e `docs/**` abre; o roadmap conta 4 linhas — a linha "Context and governance" (EN) / "Contexto e governança" (PT) sai quando a F12 entregar o tema, e a contagem do teste muda junto (`tests/test_docs.py::Roadmap`).
- **Contratos de `sdd/`:** `playbook-lint.sh --self-test` 0; o bloco do OK da `sdd-release` mantém rótulos, ordem e uma pergunta só (`tests/test_contrato_build_release.py`).
- **CI:** nada de caractere invisível nem `curl … | sh` literal em `.agents/skills/`; piso Python 3.9 / bash 3.2; `release.yml` com teto 25 no `testes` e 30 no `testes-macos` (a suíte levou 12m53s no Ubuntu e 17m31s no macOS na F11) — confira se a suíte maior ainda cabe.
- **Padrão agnóstico (P2):** `tests/test_agnostico.py` reprova `AskUserQuestion`, `TodoWrite`, `PreToolUse`, `PostToolUse`, `subagent_type`, `Task tool`, `Agent tool` e `/model` em `.agents/skills/**`, `sdd/templates/**`, `sdd/hooks/**`, `AGENTS.md.tmpl` e `sdd/playbook.md`. Os nomes de engine (`claude`, `codex`, `gemini`, `openrouter`) são dado do `registry.tsv` e dos adapters em `sdd/bin/adapters/`, não texto de skill.
- **Literais que o publish-gate reprova** (`scripts/publish-gate-patterns.txt`): e-mail só em `example.*`; CPF, CNPJ, telefone, 11+ dígitos e caminho `/Users/<nome>/` fora de arquivo rastreado; o G1 (gitleaks) varre `tests/` e `sdd/review/stubs/` — chave de API nunca em arquivo, nem em stub (valor gerado em execução ou obviamente falso de baixa entropia). Pastas `EXTERNAL_REVIEW_*` de fixture não podem ter 11+ dígitos seguidos no nome.
- **Arquivos:** `python3 -B` e `git add` por nome; bash 3.2; `rm -rf` só com `"${X:?}"`; `sdd/features|handoffs|reports|reviews|traces/` **nunca** entram em commit da branch de trabalho; todo arquivo novo no `MANIFEST.txt`.
- **Push e remoto:** todo comando remoto com `GIT_TERMINAL_PROMPT=0`; push em `main` só com OK explícito do Roberto citando "sdd-open"; nunca `--force`; a branch `docs/incorporar-starter` nunca vira PR.
- **Fora de escopo nesta sessão:** UX e LLM no código (`sdd-loop-builder`, F13); curator, `/drive` e `drive.*` (F14); a revisão de schema do privado (`audita-schema-gate.sh`, GRANT na migration, `lint-data-api-grants.py`: não viaja; fica só o slot `schema.check_cmd` vazio, candidato a cair); regenerar o sdd-starter; alterar o sdd-starter ou o repositório privado.

## Como fechar

Ao terminar, rode a skill **SDD Handoff by RDD** de novo para registrar o que foi feito
e preparar a próxima retomada.
