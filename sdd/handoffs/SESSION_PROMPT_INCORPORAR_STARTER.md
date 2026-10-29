# Continuar: INCORPORAR_STARTER — sessão 3: F5 Conhecimento

Esta sessão começa numa **worktree limpa**. Os artefatos SDD da família (features, handoffs, reports, reviews) vivem na branch `docs/incorporar-starter` do remoto, nunca mesclada em `main`.

## Preparar a worktree (antes de ler qualquer coisa)

```bash
cd /Users/robertoduarte/rdd-public/sdd-open
GIT_TERMINAL_PROMPT=0 git fetch -q origin
git worktree add /Users/robertoduarte/rdd-worktrees/sdd-open-f5-conhecimento -b feat/f5-conhecimento origin/main
cd /Users/robertoduarte/rdd-worktrees/sdd-open-f5-conhecimento
git checkout origin/docs/incorporar-starter -- sdd/features sdd/handoffs sdd/reports sdd/reviews
git rm -r -q --cached sdd/features sdd/handoffs sdd/reports sdd/reviews   # ficam no disco, fora do commit
git status --short | head -4                                              # esperado: só "?? sdd/…"
git log --oneline -1                                                      # esperado: 2fcdda1 ou mais novo
GIT_TERMINAL_PROMPT=0 git fetch -q origin tag v2.2.5                      # base do check-versions
```

Se `/Users/robertoduarte/rdd-public/sdd-open` não for o clone de `https://github.com/robertodiasduarte/sdd-open.git`, use a worktree da sessão 2 como base: `git -C /Users/robertoduarte/rdd-worktrees/sdd-open-f4-conversa worktree add …`. Não trabalhe nas worktrees antigas (`sdd-open-incorporar-starter`, `sdd-open-w0-m1`, `sdd-open-f4-conversa`).

Depois, leia nesta ordem:
- `sdd/features/PLANO_F4_F15_CONSOLIDADO.md`:
  - seção 0, com os 4 parâmetros P1–P4;
  - **4.2 (F5 Conhecimento)**, com os itens G e H;
  - **5, decisão 4**: `sdd/kb/` fixo × slot `project.kb_dir`;
  - 8.0, com a regra 10 e a tabela de degradação;
  - 10, com o agrupamento.
- `sdd/handoffs/HANDOFF_INCORPORAR_STARTER.md`: a Ficha, `## Eventos` e a etapa "F4 Conversa", que é a do topo.
- `sdd/features/AVALIACAO_STARTER_PARA_OPEN.md`: os componentes 9 (`sdd-kb`) e 10 (`ux-review-builder`).
- `sdd/templates/fragments/PERGUNTA_DECISAO.md`: o formato de pergunta e de parada que toda skill nova segue.

## Onde paramos

- **F1–F4, W0 e M1 entregues.** A última Release é https://github.com/robertodiasduarte/sdd-open/releases/tag/v2.2.5:
  - tag em `2fcdda1`;
  - SHA-256 de `sdd-open-v2.2.5.tar.gz` `4686f3dafcb9decfeea66308055f3a9123e1413c6c5e6831855a6073a859e053`, conferido.
- **`main` está em `2fcdda1`.** É a F4: camada "Como falar com o aluno" em 14 skills, `PERGUNTA_DECISAO.md`, `skill-lint.py --conversa`, `design-lint.py`, `handoff-lint.py` e `tests/test_agnostico.py`.
- **Estado do pacote:**
  - 16 skills;
  - 388 testes verdes no piso `SDD_TEST_BASH=/bin/bash /usr/bin/python3` (Python 3.9.6, bash 3.2.57), local e no `macos-latest`.
- **Esta sessão faz a F5 inteira**, do brainstorm à release:
  - a `sdd-kb` portada do starter como 17ª skill, com o validador e o gate;
  - a entrevista do `ux-review-builder` como entrada opcional da `sdd-ux-review`;
  - o item G do plano (KB Domains como lista fechada).

## Contexto que você precisa ter

- **Remoto:** `https://github.com/robertodiasduarte/sdd-open.git`.
- **Release automática:** sai no push de `main` que toca:
  - `.agents/skills/**`, `bin/**`, `sdd/bin/**`, `sdd/templates/**` ou `sdd/fixtures/**`;
  - `sdd/playbook.md`, `sdd/config.example.yaml` ou `AGENTS.md.tmpl`.

  O patch é calculado a partir da última tag (`scripts/next-version.sh`), e uma tag `vX.Y.Z` empurrada à mão também vira Release. O job `release` espera `testes` **e** `testes-macos`, como a F4 provou na run 40952893409. No OK, pergunte ao Roberto se sai `v2.2.6` (automático) ou `v2.3.0` (tag à mão, depois da run de `main`): uma skill nova é funcionalidade.
- **Escopo da F5** (plano, 4.2):
  - `sdd-kb` com o validador (`validate_kb.py`) e o `gate.sh`, perfil normativo, e o RULE_MAP apontando o teste que o Verify Gate roda;
  - a entrevista do `ux-review-builder` como entrada opcional da `sdd-ux-review`;
  - `tests/test_skill_lint.py` passa de 16 para 17 skills.
  - **Item G**: "KB Domains" vira lista fechada. O valor só pode vir de `ls <pasta da KB>`, revalidado a cada Define, e `nenhum` é explícito. A `sdd-define` valida o campo contra a pasta.
  - **Item H**: não entra (F11/U1 ficam na W5). Anote no DESIGN que o `UX_REVIEW_TEMPLATE.md` vai ganhar a tabela WCAG 2.2 AA na W5, para não fixar nada que a contradiga.
- **Decisão a levar ao brainstorm** (plano, seção 5, item 4): pasta da KB no slot novo `project.kb_dir` ou no caminho fixo `sdd/kb/`. A recomendação é **`sdd/kb/` fixo**: a Decisão 4 da frente pede o mínimo de slots, e a `sdd-kb` é do próprio open.
- **Decisões já tomadas, não reabrir:**
  - a camada de conversa fica sempre ligada;
  - o Status `✅ ▶️ ⬜ ⏸️ ➖` abre cada resposta, com o nome da fase como 1ª palavra;
  - toda pergunta tem a recomendada primeiro, a opção "não sei" e nunca "Outro" (`PERGUNTA_DECISAO.md`);
  - o open é a fonte canônica de governança, auditoria-harness e prompt-builder;
  - os artefatos SDD ficam na branch `docs/`.
- **Fonte no sdd-starter:** `/Users/robertoduarte/rdd-public/sdd-starter`, em `main` `17c69c4`.
  - **`skills/sdd-kb/`** (2.1.0):
    - `SKILL.md` com 325 linhas;
    - `references/como-falar.md`, `kb-protocol.md`, `normativo.md` e `sourcing.md`;
    - `scripts/validate_kb.py` (465 linhas), `kb_normativo.py` (246) e `gate.sh` (68);
    - os templates de `assets/` e os exemplos `assets/example-kb` e `assets/example-kb-normativo`;
    - `agents/openai.yaml`, que **não viaja**: o `doctor` acusa "skills do sdd-starter" quando acha esse arquivo, e o `tests/test_matriz_new_session.py::Portadas` reprova.
  - **`skills/ux-review-builder/`** (1.4.0): `references/INTERVIEW_GUIDE.md`, `CATALOGO_DE_REFERENCIAS.md`, `URL_ANALYSIS.md` e mais 6; `scripts/validate_generated_bundle.py` e `tests/`. Só a entrevista de público e as referências entram, como entrada da `sdd-ux-review` (2.2.0).
  - O `gate.sh` do starter usa os caminhos `skills/sdd-kb/…` do layout de lá; no open, a skill mora em `.agents/skills/sdd-kb/`, e os testes ficam em `tests/` na raiz (decisão da F2: `init` e `sync` copiam a pasta inteira da skill).
  - O `docs/guia-do-aluno.pt-BR.md` daquele checkout não é rastreado (é entrada da F6): não rode `git clean` lá.
- **Skills do fluxo** (em `/Users/robertoduarte/.claude/skills/`): `sdd-brainstorm`, `sdd-define`, `sdd-design`, `sdd-build`, `sdd-handoff`. A `sdd-release` é a do pacote (`.agents/skills/sdd-release/SKILL.md`, 2.3.0).
  - Fluxo SDD completo, com revisão de contexto fresco depois do build. Se der NEEDS_WORK, faça o ciclo 2 sobre as correções, numa worktree destacada.
  - Moldes da evidência: `sdd/reports/evidence/F4_CONVERSA/` (`gerar-evidencia.sh`, `sabotagem.sh`, `comandos-intactos.py`).
  - O `report-lint` exige a pasta `evidence/<FEATURE>/` com o mesmo nome do `BUILD_REPORT_<FEATURE>.md`.
- **Versões atuais:**
  - auditoria-harness 1.1.0, brainstorm 2.1.0, build 2.2.0, checar-ambiente 1.4.0, define 2.2.0, design 2.1.0, governanca 2.2.0, handoff 2.1.0;
  - iterate 2.1.0, new-session 1.2.0, playbook 2.1.0, prompt-builder 2.1.0, release 2.3.0, ux-review 2.2.0;
  - (portadas, sem a F4) higiene-dado 1.1.1, iniciar-repo 1.1.1.

  Toda skill tocada sobe de versão e atualiza a linha de identificação: `python3 scripts/check-versions.py --base v2.2.5 --base-obrigatoria`.

## Tarefas, em ordem

1. **Brainstorm da F5** com a `sdd-brainstorm`, gravando `sdd/features/BRAINSTORM_F5_CONHECIMENTO.md` a partir da seção 4.2 do plano. Pronto quando:
   - a decisão 4 foi respondida pelo Roberto;
   - a abordagem foi confirmada;
   - os cortes YAGNI e os 2 checkpoints estão registrados.
2. **Define e design**:
   - `sdd/features/DEFINE_F5_CONHECIMENTO.md`, com ATs em EARS e o `verify_gate` `kind: test` de sempre: `cmd` = `T=$(mktemp -d) && git archive HEAD | tar -x -C $T && PUBLISH_GATE_MODE=ci bash scripts/publish-gate.sh $T && cd $T && SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover -s tests -p 'test_*.py'`;
   - `sdd/features/DESIGN_F5_CONHECIMENTO.md`, com o File Manifest.

   Pronto quando: `verify-gate.sh --print` 0 e `python3 sdd/bin/design-lint.py sdd/features/DESIGN_F5_CONHECIMENTO.md` 0.
3. **Build**, com commit antes do gate e todo arquivo novo no `MANIFEST.txt`, em ordem `LC_ALL=C`. Pronto quando:
   - `bash sdd/bin/verify-gate.sh --strict sdd/features/DEFINE_F5_CONHECIMENTO.md` 0 e `python3 sdd/bin/report-lint.py sdd/reports/BUILD_REPORT_F5_CONHECIMENTO.md` 0;
   - `python3 sdd/bin/skill-lint.py --conversa .agents/skills/sdd-*/SKILL.md` 0 nas 17 skills, com a `sdd-kb` incluída;
   - o validador da KB aceita os exemplos e rejeita as fixtures ruins dos dois lados (LM-001);
   - houve 1 sabotagem por script alterado ou novo;
   - a revisão de contexto fresco terminou sem HIGH aberto.
4. **Release**:
   - PR com CI verde em `ubuntu-latest` **e** `macos-latest`;
   - bloco do OK da `sdd-release`;
   - OK do Roberto **citando "sdd-open" na mesma mensagem**. Sem isso, não faça o push;
   - push fast-forward em `main`.

   Pronto quando: `gh release view` mostra `SHA256SUMS.txt` e `shasum -a 256 -c` confere.
5. **Fechar**: rode a `sdd-handoff` com a etapa F5 no topo e o prompt da sessão 4 (F6 Docs: plano, seção 4.3). Grave os artefatos na branch `docs/` **sem trocar de branch na worktree**:

   ```bash
   cd /Users/robertoduarte/rdd-worktrees/sdd-open-f5-conhecimento
   T=$(mktemp -d) && GIT_TERMINAL_PROMPT=0 git fetch -q origin docs/incorporar-starter
   git worktree add -q "$T" docs/incorporar-starter
   for d in features handoffs reports reviews; do mkdir -p "$T/sdd/$d" && rsync -a --delete "sdd/$d/" "$T/sdd/$d/"; done
   git -C "$T" add sdd/features sdd/handoffs sdd/reports sdd/reviews && git -C "$T" commit -q -m "docs(incorporar-starter): sessão 3 — F5 Conhecimento" && GIT_TERMINAL_PROMPT=0 git -C "$T" push -q origin docs/incorporar-starter
   git worktree remove --force "$T"
   ```

## O que não quebrar

- **Camada de conversa** (F4):
  - a `sdd-kb` nova precisa da seção `## Como falar com o aluno` e do `references/como-falar.md` no formato do `PERGUNTA_DECISAO.md`. Conferido em 2026-10-29: a `sdd-kb` do starter, copiada como está, reprova no `skill-lint --conversa` com "references/como-falar.md sem nenhuma pergunta de decisão". Adapte: o exemplo precisa de uma pergunta de decisão com `(recomendado)` na 1ª opção e **não sei**, e precisa citar o fragmento. O CI roda `--conversa` em toda `sdd-*`;
  - a linha de identificação vem "uma vez só, antes do Status", com a versão do frontmatter (`tests/test_conversa.py`);
  - não mexa no bloco comum de regras das 14 skills sem trocá-lo nas 14 e nas `FRASES` do `test_conversa`.
  - Se a `sdd-ux-review` mudar, ela sobe de versão e continua passando no `test_conversa` e no `comandos-intactos`: só a entrada nova entra, e os passos 1–8 ficam.
- **Contratos de `sdd/`**:
  - os seis exits de `sdd/bin/verify-gate.sh` (0/2/3/4/5/64) e as fixtures existentes de `sdd/fixtures/` ficam idênticos; `playbook-lint.sh --self-test` sai 0;
  - os 2 lints novos (`design-lint.py`, `handoff-lint.py`) e o `skill-lint.py` mantêm 0/1/64; o `--conversa` é opt-in;
  - o bloco do OK da `sdd-release` mantém rótulos, ordem e uma pergunta só (`tests/test_contrato_build_release.py`);
  - o passo 4 da `sdd-iterate` e os briefs de `contexto-fresco.md` seguem como a W0 fixou (`tests/test_correcoes_w0.py`).
- **CI da M1** (`tests/test_release_workflow.py`):
  - nada de caractere invisível nem `curl … | sh` literal em `.agents/skills/` (emoji com ZWJ e FE0F passa);
  - o piso Python 3.9 / bash 3.2 é afirmado;
  - em teste, amostra com Unicode invisível se monta com `chr()`, e os bytes se conferem depois de escrever.
- **Padrão agnóstico (P2)**: o `tests/test_agnostico.py` reprova `AskUserQuestion`, `TodoWrite`, `PreToolUse`, `PostToolUse`, `subagent_type`, `Task tool`, `Agent tool` e `/model` em `.agents/skills/**`, `sdd/templates/**`, `AGENTS.md.tmpl` e `sdd/playbook.md`. Texto não-UTF-8 também reprova. Confira o texto portado da `sdd-kb` antes do commit.
- **Literais que o publish-gate reprova** (`scripts/publish-gate-patterns.txt`):
  - e-mail só em `example.com/.org/.net`;
  - CPF, CNPJ, telefone, `git@host` e sequências de 11+ dígitos montados em tempo de execução, e hosts em `.invalid`.

  Os exemplos de KB normativa do starter podem ter número de lei ou de CNPJ: confira antes de copiar.
- **Arquivos**:
  - use `python3 -B` e `git add` por nome (não há `.gitignore`);
  - bash 3.2, sem `mapfile`/`declare -A`/`${x^^}`; nada de `rm -rf` com variável (use `"${X:?}"`);
  - `sdd/features|handoffs|reports|reviews/` **nunca** entram em commit da branch de trabalho;
  - `tests/test_skill_lint.py` e `tests/test_conversa.py` contam as skills: mude de 16 para 17 de propósito.
- **Push e remoto**: todo comando remoto com `GIT_TERMINAL_PROMPT=0`; push em `main` só com OK explícito do Roberto citando "sdd-open"; nunca `--force`; a branch `docs/incorporar-starter` nunca vira PR.
- **Fora de escopo nesta sessão:**
  - a tabela WCAG e a leitura de `UX_REVIEW_*.md` anteriores (W5);
  - o encadeamento entre fases e as classes D1–D5 (F9);
  - o fail-open do `report-lint.py` com cabeçalho não reconhecido (F7);
  - docs, guia do aluno e roadmap (F6);
  - alterar o sdd-starter ou o repositório privado.

## Como fechar

Ao terminar, rode a skill **SDD Handoff by RDD** de novo para registrar o que foi feito
e preparar a próxima retomada.
