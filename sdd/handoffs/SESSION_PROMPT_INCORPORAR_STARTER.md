# Continuar: INCORPORAR_STARTER — sessão 6: F8 Hooks

Esta sessão começa numa **worktree limpa**. Os artefatos SDD da família (features, handoffs, reports, reviews) vivem na branch `docs/incorporar-starter` do remoto, nunca mesclada em `main`.

## Preparar a worktree (antes de ler qualquer coisa)

A frente já foi aberta pela `sdd-new-session` no fim da sessão 5: worktree `/Users/robertoduarte/rdd-worktrees/sdd-open-f8-hooks`, branch `feat/f8-hooks` nascida de `origin/main` = `1d225e5` (tag `v2.2.8`), com os artefatos SDD da branch `docs/incorporar-starter` já copiados (fora do commit). Abra o agente **nessa pasta** e confira:

```bash
cd /Users/robertoduarte/rdd-worktrees/sdd-open-f8-hooks
git branch --show-current                                                 # esperado: feat/f8-hooks
git status --short | head -4                                              # esperado: só "?? sdd/…"
git log --oneline -1                                                      # esperado: 1d225e5 ou mais novo
ls sdd/handoffs/HANDOFF_INCORPORAR_STARTER.md sdd/features/PLANO_F4_F15_CONSOLIDADO.md
GIT_TERMINAL_PROMPT=0 git fetch -q origin && git log --oneline -1 origin/main   # se main andou, rebase antes de começar
GIT_TERMINAL_PROMPT=0 git fetch -q origin tag v2.2.8                      # base do check-versions
GIT_TERMINAL_PROMPT=0 git fetch -q origin docs/incorporar-starter && git diff --stat origin/docs/incorporar-starter -- sdd/handoffs   # vazio: a cópia está em dia
```

Se a pasta não existir (alguém a removeu), recrie do zero:

```bash
cd /Users/robertoduarte/rdd-public/sdd-open
GIT_TERMINAL_PROMPT=0 git fetch -q origin
git worktree add /Users/robertoduarte/rdd-worktrees/sdd-open-f8-hooks -b feat/f8-hooks origin/main
cd /Users/robertoduarte/rdd-worktrees/sdd-open-f8-hooks
GIT_TERMINAL_PROMPT=0 git fetch -q origin docs/incorporar-starter
git checkout origin/docs/incorporar-starter -- sdd/features sdd/handoffs sdd/reports sdd/reviews
git rm -r -q --cached sdd/features sdd/handoffs sdd/reports sdd/reviews   # ficam no disco, fora do commit
```

Se `/Users/robertoduarte/rdd-public/sdd-open` não for o clone de `https://github.com/robertodiasduarte/sdd-open.git`, use a worktree da sessão 5 como base (`git -C /Users/robertoduarte/rdd-worktrees/sdd-open-f7-evidencia worktree add …`), se ela ainda existir. Não trabalhe nas worktrees antigas (`sdd-open-incorporar-starter`, `sdd-open-f6-docs`, `sdd-open-f7-evidencia`). O `sdd/ambiente.md` do checkout principal é nota local da `sdd-new-session` do starter, não rastreada; não o commite.

Depois, leia nesta ordem:
- `sdd/features/PLANO_F4_F15_CONSOLIDADO.md`:
  - seção 0, com os 4 parâmetros P1–P4 (a F8 segue no **P4**);
  - seção 8: o preâmbulo comum a F7–F14, **8.0** (as 10 regras do PORTE e a tabela de degradação por vendor), o quadro **"F8 Hooks de git"** (agora com o adaptador do Claude Code da E6, transferido da F7);
  - **8.1 "F8 Hooks"** (H2–H6 e o limite do `--no-verify`), **8.2** (slot `project.context_file_max_kb`) e **8.3** (fontes no privado, linha F8);
  - seção 10 (F8 sozinha na sessão 6; F9 na 7).
- `sdd/handoffs/HANDOFF_INCORPORAR_STARTER.md`: a Ficha, `## Eventos` e a etapa "F7 Evidência", que é a do topo.
- `sdd/templates/fragments/PERGUNTA_DECISAO.md`: o formato de pergunta e de parada.
- `bin/sdd-open.sh` (687 linhas: `init`, `sync`, `doctor`, o merge de JSON do Gemini em `merge_gemini_settings`, a lista de vendors em `bin/lib/vendors.sh`), `.agents/skills/sdd-higiene-dado/scripts/alarme.sh` (82) e `pre-commit.sh` (120), `tests/test_alarme.py` (29 testes), `sdd/bin/report-lint.py` (`--stdin`) e `sdd/bin/avaliador-guard.sh`.

## Onde paramos

- **F1–F7, W0 e M1 entregues; o P3 (starter) está concluído; o P4 começou com a F7.** A última Release é https://github.com/robertodiasduarte/sdd-open/releases/tag/v2.2.8:
  - tag em `1d225e5`;
  - SHA-256 de `sdd-open-v2.2.8.tar.gz` `1fdf742b3068edf2a55526b6734b92251099d81095a627c284e67846464947de`, conferido.
- **`main` está em `1d225e5`.** É a F7: `report-lint.py` fail-closed (tabela reconhecida, avaliação ausente reprova, `N.A.` contra `layers:`, `PENDENTE`/`--pendente`, `git check-ignore`, `--stdin`), `verify-gate.sh --trace`/`--sem-define`, e `gate-baseline.sh`, `gate-shell-evidencia.sh`, `avaliador-guard.sh` e `test-baseline.sh` em `sdd/bin/`; `sdd-build` 2.3.0, `sdd-release` 2.4.0.
- **Estado do pacote:**
  - 17 skills;
  - 630 testes verdes no piso `SDD_TEST_BASH=/bin/bash /usr/bin/python3` (Python 3.9.6, bash 3.2.57), local e no `macos-latest`.
- **Esta sessão faz a F8 inteira**, do brainstorm à release.

## Contexto que você precisa ter

- **Remoto:** `https://github.com/robertodiasduarte/sdd-open.git`.
- **Release automática:** sai no push de `main` que toca:
  - `.agents/skills/**`, `bin/**`, `sdd/bin/**`, `sdd/templates/**` ou `sdd/fixtures/**`;
  - `sdd/playbook.md`, `sdd/config.example.yaml` ou `AGENTS.md.tmpl`.

  A F8 toca `bin/**` e provavelmente `sdd/` e a `sdd-higiene-dado`, então **sai Release**. O patch é calculado a partir da última tag (`scripts/next-version.sh`), o que dá `v2.2.9`; uma tag `vX.Y.Z` empurrada à mão também vira Release (pergunte ao Roberto se prefere `v2.3.0`, porque a F8 instala hooks no projeto do usuário). O job `release` espera `testes` **e** `testes-macos`.
- **Escopo da F8** (plano, quadro F8 e 8.1), itens H1–H6 do PORTE §5.2, mais o adaptador da E6:
  - `sdd/hooks/pre-commit`: teto do arquivo de contexto por vendor (H2: `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.cursorrules`, 100 KB, lista em `bin/lib/vendors.sh`); credencial em texto claro em `.json/.yml/.env` (H3: placeholder passa; `gitleaks protect --staged` se instalado); anti-collapse do playbook (H4: `playbook-lint.sh --anti-collapse` quando `sdd/playbook.md` está no staged); byte NUL em arquivo de texto (H5); commit no checkout da `project.default_branch` bloqueado (H6); o `report-lint.py` sobre o `BUILD_REPORT` do staged (dependência da F7);
  - `sdd/hooks/pre-push`: avisa base velha (H6);
  - `sdd-open.sh init` instala com confirmação (`core.hooksPath` = `sdd/hooks`); `doctor` confere; `sync` não sobrescreve sem perguntar;
  - **adaptador do Claude Code da E6** (transferido da F7 por decisão do Roberto): o `init --vendors claude` gera `.claude/settings.json` com PreToolUse em Write/Edit (simula o conteúdo final do Edit e chama `python3 sdd/bin/report-lint.py --stdin <caminho>`) e no despacho do avaliador (`bash sdd/bin/avaliador-guard.sh`); falha aberta, mas avisa. O nome da ferramenta do vendor mora **só** no que o `init` gera, nunca em `.agents/skills/` nem `sdd/templates/` (`tests/test_agnostico.py`);
  - limite documentado: hook de cliente é pulado com `--no-verify`; a verdade continua no `report-lint` da release e no CI (`docs/hooks.md`).
- **Fontes no privado** (só leitura; o repositório privado **não** se altera). **Leia do `origin/main` do privado** (`git -C /Users/robertoduarte/RDD/Wordpress show origin/main:<arquivo>`): o checkout local de `~/RDD/Wordpress` está atrás dele e não tem algumas fontes. `.githooks/pre-commit` (154 l.; sem o item ⑥ "require PHP"), `.githooks/pre-push` (31 l.), `.githooks/claude-build-report-guard.py` (541 l.; `resulting_content()` simula o Edit) e `.githooks/claude-avaliador-guard.py` (88 l.). Específico da RDD não viaja (regra 4 do 8.0).
- **Decisões a levar ao brainstorm** (formato `PERGUNTA_DECISAO.md`, recomendada primeiro):
  - **D3**: o Open distribui hooks? (recomendado: sim, pelo `init`, com confirmação);
  - **D10**: o conflito com a `sdd-higiene-dado`, que recusa agir com `core.hooksPath` (recomendado: dispatcher em `sdd/hooks/pre-commit` que chama o `pre-commit.sh` da higiene-dado, e o `alarme.sh` reconhece `sdd/hooks` como seu — exige bump da `sdd-higiene-dado` 1.1.1 e mexe nos 29 testes de `tests/test_alarme.py`);
  - **D11**: o slot `project.context_file_max_kb` (default `100`), com OK do Roberto;
  - o formato do adaptador da E6 (`.claude/settings.json` com merge como o do Gemini, ou arquivo próprio) e se ele entra no mesmo ciclo;
  - versão da Release (`v2.2.9` automática ou `v2.3.0` por tag).
- **Decisões já tomadas, não reabrir:**
  - a camada de conversa fica sempre ligada;
  - o Status `✅ ▶️ ⬜ ⏸️ ➖` abre cada resposta, com o nome da fase como 1ª palavra;
  - toda pergunta tem a recomendada primeiro, a opção "não sei" e nunca "Outro";
  - o open é a fonte canônica de governança, auditoria-harness e prompt-builder;
  - a KB fica em `sdd/kb/` fixo, sem slot;
  - os artefatos SDD ficam na branch `docs/`;
  - vendor sem subagente degrada para a parada ⏸️ (tabela do 8.0), nunca quebra;
  - `report-lint` fail-closed (D4 da F7); só o slot `evidence.require_avaliacao_layers` da F7 (caminhos fixos); a regra da E6 (`--stdin`) já existe — a F8 só gera o adaptador.
- **Skills do fluxo** (em `/Users/robertoduarte/.claude/skills/`): `sdd-brainstorm`, `sdd-define`, `sdd-design`, `sdd-build`, `sdd-handoff`. A `sdd-release` é a do pacote (`.agents/skills/sdd-release/SKILL.md`, 2.4.0); a UX review é a do pacote (`.agents/skills/sdd-ux-review/SKILL.md`).
  - Fluxo SDD completo, com revisão de contexto fresco do DESIGN antes do build e do build depois (modo `veredito`, numa worktree destacada; remova-a no fim). Se der NEEDS_WORK, faça o ciclo 2 sobre as correções; a `sdd-build` limita a 2 ciclos.
  - **Antes de despachar cada avaliador**, rode `bash sdd/bin/avaliador-guard.sh --permitir sdd/features/ --permitir sdd/handoffs/ --permitir sdd/reports/ --permitir sdd/reviews/` (nunca `--permitir sdd/`) e grave o log.
  - Moldes da evidência: `sdd/reports/evidence/F7_EVIDENCIA/` (`gerar-evidencia.sh`, `sabotagem.sh`). O Bash da sessão é zsh (sem `PIPESTATUS`): grave os logs com `/bin/bash -c` e `out=$(cmd 2>&1); rc=$?` antes de qualquer pipe, terminando em `[exit=$rc]`; sem formatador (`tail`, `sed`, `sort`…) no último estágio da linha `$`. Confira com `bash sdd/bin/gate-shell-evidencia.sh sdd/reports/evidence/F8_HOOKS` (sempre com o caminho: as frentes antigas têm 22 acusações conhecidas e não rastreadas).
  - O `report-lint` exige a pasta `evidence/<FEATURE>/` com o mesmo nome do `BUILD_REPORT_<FEATURE>.md`, a tabela reconhecida e a linha do avaliador (ou o `AVALIACAO_<FEATURE>_<AAAAMMDD>…md` em `sdd/reviews/`).
  - O DESIGN passa em dois lints: `python3 sdd/bin/design-lint.py` e o `scripts/validate_design.py` da skill de design, que reprova chaves `{…}` numa linha **até dentro de código** (use `"$X"`, não `${X}`), título `## X` citado no meio do texto e um 2º título "Next Step".
  - `sdd/traces/` é criado a cada execução do gate na raiz e nunca entra em commit.
- **Versões atuais:**
  - auditoria-harness 1.1.0, brainstorm 2.1.1, build 2.3.0, checar-ambiente 1.4.0, define 2.3.1, design 2.1.1, governanca 2.2.1, handoff 2.1.0;
  - iterate 2.1.0, kb 2.2.0, new-session 1.2.0, playbook 2.1.0, prompt-builder 2.1.0, release 2.4.0, ux-review 2.3.1;
  - (portadas, sem a F4) higiene-dado 1.1.1, iniciar-repo 1.1.1.

  Toda skill tocada sobe de versão e atualiza a linha de identificação: `python3 scripts/check-versions.py --base v2.2.8 --base-obrigatoria`.

## Tarefas, em ordem

1. **Brainstorm da F8** com a `sdd-brainstorm`, gravando `sdd/features/BRAINSTORM_F8_HOOKS.md` a partir do quadro F8 e do 8.1 do plano. Pronto quando: D3, D10, D11, o formato da E6 e a versão foram respondidas pelo Roberto, a abordagem foi confirmada e os cortes YAGNI e os 2 checkpoints estão registrados.
2. **Define, UX review e design**:
   - `sdd/features/DEFINE_F8_HOOKS.md`, com ATs em EARS e o `verify_gate` `kind: test` de sempre: `cmd` = `T=$(mktemp -d) && git archive HEAD | tar -x -C $T && PUBLISH_GATE_MODE=ci bash scripts/publish-gate.sh $T && cd $T && SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover -s tests -p 'test_*.py'`;
   - `sdd/reviews/UX_REVIEW_F8_HOOKS.md` (a interface é a saída dos hooks e do `init`);
   - `sdd/features/DESIGN_F8_HOOKS.md`, com o File Manifest.

   Pronto quando: `verify-gate.sh --print` 0, `python3 sdd/bin/design-lint.py` 0 e a revisão de contexto fresco do DESIGN aplicada.
3. **Build**, com commit antes do gate e todo arquivo novo no `MANIFEST.txt`, em ordem `LC_ALL=C`. Pronto quando:
   - `bash sdd/bin/verify-gate.sh --strict sdd/features/DEFINE_F8_HOOKS.md` 0 e `python3 sdd/bin/report-lint.py sdd/reports/BUILD_REPORT_F8_HOOKS.md` 0;
   - depois do `init`, `git config core.hooksPath` = `sdd/hooks`; o pre-commit bloqueia as 5 fixtures (H2–H6) e deixa passar o controle; o alarme da `sdd-higiene-dado` continua bloqueando CPF/CNPJ com DV válido;
   - o `init --vendors claude` gera o adaptador da E6, e um Write de `BUILD_REPORT` sem avaliação é negado por ele;
   - todo script novo passa por `grep -nE 'mapfile|declare -A|\$\{[a-zA-Z_]+\^\^' <script>` sem achado (bash 3.2; `tests/test_bash32.py` cobre `sdd/bin/*.sh`) e tem fixture e teste dos dois lados (regra 6 do 8.0);
   - `python3 sdd/bin/skill-lint.py --conversa .agents/skills/sdd-*/SKILL.md` 0 nas 17 skills;
   - houve 1 sabotagem por script alterado ou novo;
   - a revisão de contexto fresco terminou sem HIGH aberto.
4. **Release**:
   - PR com CI verde em `ubuntu-latest` **e** `macos-latest`;
   - bloco do OK da `sdd-release`;
   - OK do Roberto **citando "sdd-open" na mesma mensagem**. Sem isso, não faça o push;
   - push fast-forward em `main`.

   Pronto quando: `gh release view <tag> -R robertodiasduarte/sdd-open` mostra `SHA256SUMS.txt` e `shasum -a 256 -c` confere.
5. **Fechar**: rode a `sdd-handoff` com a etapa F8 no topo e o prompt da sessão 7 (F9 Fluxo encadeado: plano, seção 8, "F9"). Grave os artefatos na branch `docs/` **sem trocar de branch na worktree**:

   ```bash
   cd /Users/robertoduarte/rdd-worktrees/sdd-open-f8-hooks
   T=$(mktemp -d) && GIT_TERMINAL_PROMPT=0 git fetch -q origin docs/incorporar-starter
   git worktree add -q --detach "$T" origin/docs/incorporar-starter   # do remoto: a branch local pode estar atrás
   for d in features handoffs reports reviews; do mkdir -p "$T/sdd/$d" && rsync -a --delete "sdd/$d/" "$T/sdd/$d/"; done
   git -C "$T" add sdd/features sdd/handoffs sdd/reports sdd/reviews && git -C "$T" commit -q -m "docs(incorporar-starter): sessão 6 — F8 Hooks" && GIT_TERMINAL_PROMPT=0 git -C "$T" push -q origin HEAD:docs/incorporar-starter
   git worktree remove --force "$T"
   ```

## O que não quebrar

- **`report-lint.py`** (F7): fail-closed; os 32 contratos antigos e os de `tests/test_report_lint_evidencia.py`; `--stdin` e `--pendente`; exits 0/1/64; mensagens com `🛑 [classe]`, `RESULTADO:` e `→`.
- **`verify-gate.sh`**: os seis exits (0/2/3/4/5/64), as fixtures de `sdd/fixtures/` e a saída idêntica com e sem trace.
- **`sdd-higiene-dado`**: o alarme continua recusando CPF/CNPJ com DV válido, `.env`, `.pfx/.p12/.pem` e planilha nova; os 29 testes de `tests/test_alarme.py` mudam só no que a D10 exigir, com registro.
- **`init`/`sync`/`doctor`**: o `init` nunca sobrescreve skill instalada nem `sdd/bin/*` (completa o que falta); o `sync` regenera adaptadores; o merge do `.gemini/settings.json` continua; os testes de `tests/test_sdd_open.py` ficam.
- **Docs testados** (`tests/test_docs.py`): todo link e âncora de `README*.md` e `docs/**` abre; o roadmap conta 7 linhas; a linha "Hooks" é a da F8 — ao entregar, **remova-a** (EN e PT) e atualize a contagem do teste junto.
- **Camada de conversa** (F4 + F5): o bloco comum está em 15 `SKILL.md` e a seção nas 17; não mexa nele sem trocar nas 15 e nas `FRASES` do `tests/test_conversa.py`. "Por que cada regra existe" fica logo antes de `## Encerramento (obrigatório)` nas 7 skills de fase.
- **Contratos de `sdd/`**: `playbook-lint.sh --self-test` sai 0; os lints mantêm 0/1/64; o bloco do OK da `sdd-release` mantém rótulos, ordem e uma pergunta só.
- **CI da M1**: nada de caractere invisível nem `curl … | sh` literal em `.agents/skills/`; piso Python 3.9 / bash 3.2 afirmado.
- **Padrão agnóstico (P2)**: `tests/test_agnostico.py` reprova `AskUserQuestion`, `TodoWrite`, `PreToolUse`, `PostToolUse`, `subagent_type`, `Task tool`, `Agent tool` e `/model` em `.agents/skills/**`, `sdd/templates/**`, `AGENTS.md.tmpl` e `sdd/playbook.md`. O adaptador da E6 (PreToolUse) mora **só** no que o `init --vendors claude` gera.
- **Literais que o publish-gate reprova** (`scripts/publish-gate-patterns.txt`): e-mail só em `example.com/.org/.net`; CPF, CNPJ, telefone, sequências de 11+ dígitos e caminho `/Users/<nome>/` não podem aparecer em arquivo rastreado. Fixtures de CPF/CNPJ do hook são montadas em execução, como no `tests/test_alarme.py`.
- **Arquivos**: `python3 -B` e `git add` por nome (não há `.gitignore`); bash 3.2, nada de `rm -rf` com variável sem `"${X:?}"`; `sdd/features|handoffs|reports|reviews|traces/` **nunca** entram em commit da branch de trabalho; todo arquivo novo entra no `MANIFEST.txt`.
- **Push e remoto**: todo comando remoto com `GIT_TERMINAL_PROMPT=0`; push em `main` só com OK explícito do Roberto citando "sdd-open"; nunca `--force`; a branch `docs/incorporar-starter` nunca vira PR.
- **Fora de escopo nesta sessão:**
  - o encadeamento entre fases, o `exit 40 AGUARDANDO_HUMANO` e as classes D1–D5 (F9);
  - a revisão adversarial e o registry (F10/F11); `RESUMO_ETAPA.md` com `/adversarial-review` (F10);
  - regenerar o sdd-starter a partir do open (frente própria);
  - alterar o sdd-starter ou o repositório privado.

## Como fechar

Ao terminar, rode a skill **SDD Handoff by RDD** de novo para registrar o que foi feito
e preparar a próxima retomada.
