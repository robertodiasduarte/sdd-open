# Continuar: INCORPORAR_STARTER — sessão 5: F7 Evidência

Esta sessão começa numa **worktree limpa**. Os artefatos SDD da família (features, handoffs, reports, reviews) vivem na branch `docs/incorporar-starter` do remoto, nunca mesclada em `main`.

## Preparar a worktree (antes de ler qualquer coisa)

A frente já foi aberta pela `sdd-new-session` no fim da sessão 4: worktree `/Users/robertoduarte/rdd-worktrees/sdd-open-f7-evidencia`, branch `feat/f7-evidencia` nascida de `origin/main` = `1c9bbc7` (tag `v2.2.7`), com os artefatos SDD da branch `docs/incorporar-starter` já copiados (fora do commit). Abra o agente **nessa pasta** e confira:

```bash
cd /Users/robertoduarte/rdd-worktrees/sdd-open-f7-evidencia
git branch --show-current                                                 # esperado: feat/f7-evidencia
git status --short | head -4                                              # esperado: só "?? sdd/…"
git log --oneline -1                                                      # esperado: 1c9bbc7 ou mais novo
ls sdd/handoffs/HANDOFF_INCORPORAR_STARTER.md sdd/features/PLANO_F4_F15_CONSOLIDADO.md
GIT_TERMINAL_PROMPT=0 git fetch -q origin && git log --oneline -1 origin/main   # se main andou, rebase antes de começar
GIT_TERMINAL_PROMPT=0 git fetch -q origin tag v2.2.7                      # base do check-versions
```

Se a pasta não existir (alguém a removeu), recrie do zero:

```bash
cd /Users/robertoduarte/rdd-public/sdd-open
GIT_TERMINAL_PROMPT=0 git fetch -q origin
git worktree add /Users/robertoduarte/rdd-worktrees/sdd-open-f7-evidencia -b feat/f7-evidencia origin/main
cd /Users/robertoduarte/rdd-worktrees/sdd-open-f7-evidencia
git checkout origin/docs/incorporar-starter -- sdd/features sdd/handoffs sdd/reports sdd/reviews
git rm -r -q --cached sdd/features sdd/handoffs sdd/reports sdd/reviews   # ficam no disco, fora do commit
```

Se `/Users/robertoduarte/rdd-public/sdd-open` não for o clone de `https://github.com/robertodiasduarte/sdd-open.git`, use a worktree da sessão 4 como base (`git -C /Users/robertoduarte/rdd-worktrees/sdd-open-f6-docs worktree add …`), se ela ainda existir. Não trabalhe nas worktrees antigas (`sdd-open-incorporar-starter`, `sdd-open-f6-docs`). O `sdd/ambiente.md` do checkout principal é nota local da `sdd-new-session` do starter, não rastreada; não o commite.

Depois, leia nesta ordem:
- `sdd/features/PLANO_F4_F15_CONSOLIDADO.md`:
  - seção 0, com os 4 parâmetros P1–P4 (a F7 abre o **P4**);
  - seção 8: o preâmbulo comum a F7–F14, **8.0** (as 10 regras do PORTE e a tabela de degradação por vendor), o quadro **"F7 Evidência que não mente"**;
  - **8.1 "F7 Evidência"** (detalhes de E1–E13), **8.2** (slots da F7) e **8.3** (fontes no privado, linhas F7);
  - seção 10, com o agrupamento (F7 sozinha na sessão 5; F8 na 6).
- `sdd/handoffs/HANDOFF_INCORPORAR_STARTER.md`: a Ficha (critérios 1–10 do "Pronto quando"), `## Eventos` e a etapa "F6 Docs", que é a do topo.
- `sdd/templates/fragments/PERGUNTA_DECISAO.md`: o formato de pergunta e de parada.
- `sdd/bin/report-lint.py` (323 linhas), `sdd/bin/verify-gate.sh` (197 linhas), `.agents/skills/sdd-build/SKILL.md` (passos 1.5 e 5d) e `sdd/templates/fragments/EVIDENCIA.md`.

## Onde paramos

- **F1–F6, W0 e M1 entregues; o P3 (starter) está concluído.** A última Release é https://github.com/robertodiasduarte/sdd-open/releases/tag/v2.2.7:
  - tag em `1c9bbc7`;
  - SHA-256 de `sdd-open-v2.2.7.tar.gz` `6a3eaea3c996301af6c289d32fe88a1f49df65bd8c4b57eaf4b31c92b45ebb59`, conferido.
- **`main` está em `1c9bbc7`.** É a F6: guia do aluno em PT, roadmap EN/PT, quickstarts com "valide antes de seguir", `AGENTS.md.tmpl` com preparo/KB/regra 7, "Por que cada regra existe" nas 7 skills de fase, `tests/test_docs.py`.
- **Estado do pacote:**
  - 17 skills;
  - 514 testes verdes no piso `SDD_TEST_BASH=/bin/bash /usr/bin/python3` (Python 3.9.6, bash 3.2.57), local e no `macos-latest`.
- **Esta sessão faz a F7 inteira**, do brainstorm à release.

## Contexto que você precisa ter

- **Remoto:** `https://github.com/robertodiasduarte/sdd-open.git`.
- **Release automática:** sai no push de `main` que toca:
  - `.agents/skills/**`, `bin/**`, `sdd/bin/**`, `sdd/templates/**` ou `sdd/fixtures/**`;
  - `sdd/playbook.md`, `sdd/config.example.yaml` ou `AGENTS.md.tmpl`.

  A F7 toca `sdd/bin/**` e a `sdd-build`, então **sai Release**. O patch é calculado a partir da última tag (`scripts/next-version.sh`), o que dá `v2.2.8`; uma tag `vX.Y.Z` empurrada à mão também vira Release (pergunte ao Roberto se prefere `v2.3.0`, porque a F7 muda o comportamento do `report-lint`). O job `release` espera `testes` **e** `testes-macos`.
- **Escopo da F7** (plano, quadro F7 e 8.1), itens E1–E13 do PORTE §5.1:
  - `report-lint.py`: avaliação obrigatória quando o manifest toca ≥ N camadas de `layers:` (E1, E5, reusando `ler_layers_sql()`), nega relatório sem `AVALIACAO_*.md` **e** sem declaração explícita, `N.A.` só com motivo; `avaliador: PENDENTE` conhecido pelo `VERDICT_RE` e a `sdd-release` 0a aborta com ele (E2); `git check-ignore` em cada caminho de evidência citado (E3); veredito achado em heading, tabela ou parágrafo seguinte, fora de code fence (E4);
  - `sdd/bin/gate-baseline.sh` (E7): roda o gate contra `origin/<default_branch>` numa cópia e exige vermelho lá;
  - `sdd/bin/gate-shell-evidencia.sh` (E8): exit 2 quando o `[exit=N]` do log é do formatador (`| tail` sem `rc=$?`); a receita do `EVIDENCIA.md` passa a gravar `rc=$?`;
  - `verify-gate.sh --trace` (ligado por default) e `--sem-define`, 1 linha JSONL por execução em `sdd/traces/<F>.jsonl` (E9);
  - `sdd/bin/test-baseline.sh` (E10), **implementação nova** sobre `{{TEST_CMD}}`: só falha nova aborta, `--touched`, teste que sarou sai do baseline (o `deno-test-gate.sh` do privado não porta);
  - `sdd/bin/avaliador-guard.sh` (E11): nega despachar o avaliador com worktree não commitado; chamado no `sdd-build` 1.5 e 5d;
  - coerência da flag `LLM Prompts` no passo 0 da `sdd-build` (E12) e fragmento `sdd/templates/fragments/LLM_PROMPTS_BUILD_REPORT.md` (E13);
  - adaptador PreToolUse do Claude Code chamando `report-lint.py --stdin` (E6), gerado só pelo `init --vendors claude`; falha aberta mas avisa.
- **Fontes no privado** (só leitura; o repositório privado **não** se altera): `.githooks/claude-build-report-guard.py` (541 l.), `scripts/gates/avaliador-pendente-guard.sh` (77 l.), `scripts/gates/gate-baseline.sh` (159 l.), `scripts/gates/gate-shell-evidencia.sh` (111 l.), `scripts/verify-gate.sh` (243 l.; só `--trace` e `--sem-define`), `.githooks/claude-avaliador-guard.py` (88 l.), em `/Users/robertoduarte/RDD/Wordpress`. Específico da RDD não viaja (regra 4 do 8.0).
- **Decisões a levar ao brainstorm** (formato `PERGUNTA_DECISAO.md`, recomendada primeiro):
  - **D4**: `report-lint` fail-closed por default (recomendado: reprova cabeçalho não reconhecido e ausência de avaliação);
  - **D11**: os slots `evidence.dir`, `evidence.traces_dir`, `evidence.require_avaliacao_layers` (default `2`) e `tests.baseline_file` (`sdd/baselines/tests.txt`) em `sdd/config.example.yaml`, cada um com OK do Roberto;
  - se a **E6** (gerar o PreToolUse no `init`) entra aqui ou vai para a F8, que também redesenha o `init`;
  - versão da Release (`v2.2.8` automática ou `v2.3.0` por tag).
- **Decisões já tomadas, não reabrir:**
  - a camada de conversa fica sempre ligada;
  - o Status `✅ ▶️ ⬜ ⏸️ ➖` abre cada resposta, com o nome da fase como 1ª palavra;
  - toda pergunta tem a recomendada primeiro, a opção "não sei" e nunca "Outro";
  - o open é a fonte canônica de governança, auditoria-harness e prompt-builder;
  - a KB fica em `sdd/kb/` fixo, sem slot;
  - os artefatos SDD ficam na branch `docs/`;
  - vendor sem subagente degrada para a parada ⏸️ (tabela do 8.0), nunca quebra.
- **Skills do fluxo** (em `/Users/robertoduarte/.claude/skills/`): `sdd-brainstorm`, `sdd-define`, `sdd-design`, `sdd-build`, `sdd-handoff`. A `sdd-release` é a do pacote (`.agents/skills/sdd-release/SKILL.md`, 2.3.1).
  - Fluxo SDD completo, com revisão de contexto fresco do DESIGN antes do build e do build depois (modo `veredito`, numa worktree destacada; remova-a no fim). Se der NEEDS_WORK, faça o ciclo 2 sobre as correções.
  - Moldes da evidência: `sdd/reports/evidence/F6_DOCS/` e `F5_CONHECIMENTO/` (`gerar-evidencia.sh`, `sabotagem.sh`, `comandos-intactos.py`). O Bash da sessão é zsh (sem `PIPESTATUS`): gere logs com `/bin/bash -c` ou dentro do `gerar-evidencia.sh`.
  - O `report-lint` exige a pasta `evidence/<FEATURE>/` com o mesmo nome do `BUILD_REPORT_<FEATURE>.md`. Cuidado: a F7 muda o próprio `report-lint`, então o BUILD_REPORT da F7 tem de passar nas regras novas.
  - O DESIGN passa em dois lints: `python3 sdd/bin/design-lint.py` e o `scripts/validate_design.py` da skill de design, que reprova chaves `{…}` e a sigla de "a definir" **até dentro de código** e um 2º título "Next Step" no texto.
- **Versões atuais:**
  - auditoria-harness 1.1.0, brainstorm 2.1.1, build 2.2.1, checar-ambiente 1.4.0, define 2.3.1, design 2.1.1, governanca 2.2.1, handoff 2.1.0;
  - iterate 2.1.0, kb 2.2.0, new-session 1.2.0, playbook 2.1.0, prompt-builder 2.1.0, release 2.3.1, ux-review 2.3.1;
  - (portadas, sem a F4) higiene-dado 1.1.1, iniciar-repo 1.1.1.

  Toda skill tocada sobe de versão e atualiza a linha de identificação: `python3 scripts/check-versions.py --base v2.2.7 --base-obrigatoria`.

## Tarefas, em ordem

1. **Brainstorm da F7** com a `sdd-brainstorm`, gravando `sdd/features/BRAINSTORM_F7_EVIDENCIA.md` a partir do quadro F7 e do 8.1 do plano. Pronto quando: D4, D11, a E6 e a versão foram respondidas pelo Roberto, a abordagem foi confirmada e os cortes YAGNI e os 2 checkpoints estão registrados.
2. **Define e design**:
   - `sdd/features/DEFINE_F7_EVIDENCIA.md`, com ATs em EARS e o `verify_gate` `kind: test` de sempre: `cmd` = `T=$(mktemp -d) && git archive HEAD | tar -x -C $T && PUBLISH_GATE_MODE=ci bash scripts/publish-gate.sh $T && cd $T && SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover -s tests -p 'test_*.py'`;
   - `sdd/features/DESIGN_F7_EVIDENCIA.md`, com o File Manifest.

   Pronto quando: `verify-gate.sh --print` 0, `python3 sdd/bin/design-lint.py` 0 e a revisão de contexto fresco do DESIGN aplicada.
3. **Build**, com commit antes do gate e todo arquivo novo no `MANIFEST.txt`, em ordem `LC_ALL=C`. Pronto quando:
   - `bash sdd/bin/verify-gate.sh --strict sdd/features/DEFINE_F7_EVIDENCIA.md` 0 e `python3 sdd/bin/report-lint.py sdd/reports/BUILD_REPORT_F7_EVIDENCIA.md` 0;
   - `report-lint.py` reprova as fixtures `BUILD_REPORT_sem_avaliacao`, `…_pendente` e `…_evidencia_ignorada`, e aprova o controle;
   - `gate-shell-evidencia.sh` acusa `| tail` sem `rc=$?`; `verify-gate.sh --trace` grava 1 linha JSONL por execução;
   - todo script novo passa por `grep -nE 'mapfile|declare -A|\$\{[a-zA-Z_]+\^\^' <script>` sem achado (bash 3.2) e tem fixture e teste dos dois lados (regra 6 do 8.0);
   - `python3 sdd/bin/skill-lint.py --conversa .agents/skills/sdd-*/SKILL.md` 0 nas 17 skills;
   - houve 1 sabotagem por script alterado ou novo;
   - a revisão de contexto fresco terminou sem HIGH aberto.
4. **Release**:
   - PR com CI verde em `ubuntu-latest` **e** `macos-latest`;
   - bloco do OK da `sdd-release`;
   - OK do Roberto **citando "sdd-open" na mesma mensagem**. Sem isso, não faça o push;
   - push fast-forward em `main`.

   Pronto quando: `gh release view <tag> -R robertodiasduarte/sdd-open` mostra `SHA256SUMS.txt` e `shasum -a 256 -c` confere.
5. **Fechar**: rode a `sdd-handoff` com a etapa F7 no topo e o prompt da sessão 6 (F8 Hooks: plano, seção 8, "F8"). Grave os artefatos na branch `docs/` **sem trocar de branch na worktree**:

   ```bash
   cd /Users/robertoduarte/rdd-worktrees/sdd-open-f7-evidencia
   T=$(mktemp -d) && GIT_TERMINAL_PROMPT=0 git fetch -q origin docs/incorporar-starter
   git worktree add -q --detach "$T" origin/docs/incorporar-starter   # do remoto: a branch local pode estar atrás
   for d in features handoffs reports reviews; do mkdir -p "$T/sdd/$d" && rsync -a --delete "sdd/$d/" "$T/sdd/$d/"; done
   git -C "$T" add sdd/features sdd/handoffs sdd/reports sdd/reviews && git -C "$T" commit -q -m "docs(incorporar-starter): sessão 5 — F7 Evidência" && GIT_TERMINAL_PROMPT=0 git -C "$T" push -q origin HEAD:docs/incorporar-starter
   git worktree remove --force "$T"
   ```

## O que não quebrar

- **`report-lint.py`**: os 32 contratos atuais (14 originais + 18 da F3, incluindo a regra de migration) não mudam; as regras novas entram como funções ao lado. Ele também vai para o projeto do usuário: mensagens com `🛑`, `RESULTADO:` e `→`, exits 0/1/64.
- **`verify-gate.sh`**: os seis exits (0/2/3/4/5/64) e as fixtures de `sdd/fixtures/` ficam idênticos; `--trace` e `--sem-define` são aditivos.
- **Docs testados** (`tests/test_docs.py`, F6): todo link e âncora de `README*.md` e `docs/**` abre; o roadmap conta 7 linhas. A linha "Hooks and evidence"/"Hooks e evidência" cobre F7 **e** F8: ao entregar a F7, reescreva-a só com os hooks (EN e PT); quem remove a linha é a F8.
- **Camada de conversa** (F4 + F5): o bloco comum está em 15 `SKILL.md`; não mexa nele sem trocar nas 15 e nas `FRASES` do `tests/test_conversa.py`. "Por que cada regra existe" (F6) fica logo antes de `## Encerramento (obrigatório)` nas 7 skills de fase: regra nova da `sdd-build` ganha também o seu "por quê" ali.
- **Contratos de `sdd/`**: `playbook-lint.sh --self-test` sai 0; os lints mantêm 0/1/64; o bloco do OK da `sdd-release` mantém rótulos, ordem e uma pergunta só; o passo 4 da `sdd-iterate` segue como a W0 fixou.
- **CI da M1**: nada de caractere invisível nem `curl … | sh` literal em `.agents/skills/`; piso Python 3.9 / bash 3.2 afirmado.
- **Padrão agnóstico (P2)**: `tests/test_agnostico.py` reprova `AskUserQuestion`, `TodoWrite`, `PreToolUse`, `PostToolUse`, `subagent_type`, `Task tool`, `Agent tool` e `/model` em `.agents/skills/**`, `sdd/templates/**`, `AGENTS.md.tmpl` e `sdd/playbook.md`. O adaptador da E6 (PreToolUse) mora **só** no que o `init --vendors claude` gera, nunca no `SKILL.md` nem em `references/`.
- **Literais que o publish-gate reprova** (`scripts/publish-gate-patterns.txt`): e-mail só em `example.com/.org/.net`; CPF, CNPJ, telefone, sequências de 11+ dígitos e caminho `/Users/<nome>/` não podem aparecer em arquivo rastreado. Fixtures copiadas do privado precisam ser limpas.
- **Arquivos**: `python3 -B` e `git add` por nome (não há `.gitignore`); bash 3.2, nada de `rm -rf` com variável sem `"${X:?}"`; `sdd/features|handoffs|reports|reviews/` **nunca** entram em commit da branch de trabalho; todo arquivo novo entra no `MANIFEST.txt`.
- **Push e remoto**: todo comando remoto com `GIT_TERMINAL_PROMPT=0`; push em `main` só com OK explícito do Roberto citando "sdd-open"; nunca `--force`; a branch `docs/incorporar-starter` nunca vira PR.
- **Fora de escopo nesta sessão:**
  - os hooks de git `pre-commit`/`pre-push`, `core.hooksPath` e a D10 (F8);
  - o encadeamento entre fases, o `exit 40 AGUARDANDO_HUMANO` e as classes D1–D5 (F9);
  - a revisão adversarial e o registry (F10/F11); `RESUMO_ETAPA.md` com `/adversarial-review` (F10);
  - regenerar o sdd-starter a partir do open (frente própria);
  - alterar o sdd-starter ou o repositório privado.

## Como fechar

Ao terminar, rode a skill **SDD Handoff by RDD** de novo para registrar o que foi feito
e preparar a próxima retomada.
