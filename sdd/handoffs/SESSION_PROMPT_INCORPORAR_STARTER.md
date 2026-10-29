# Continuar: INCORPORAR_STARTER — sessão 4: F6 Docs

Esta sessão começa numa **worktree limpa**. Os artefatos SDD da família (features, handoffs, reports, reviews) vivem na branch `docs/incorporar-starter` do remoto, nunca mesclada em `main`.

## Preparar a worktree (antes de ler qualquer coisa)

A frente já foi aberta pela `sdd-new-session` no fim da sessão 3: worktree `/Users/robertoduarte/rdd-worktrees/sdd-open-f6-docs`, branch `feat/f6-docs` nascida de `origin/main` = `7e19462`, com os artefatos SDD da branch `docs/incorporar-starter` já copiados (fora do commit). Abra o agente **nessa pasta** e confira:

```bash
cd /Users/robertoduarte/rdd-worktrees/sdd-open-f6-docs
git branch --show-current                                                 # esperado: feat/f6-docs
git status --short | head -4                                              # esperado: só "?? sdd/…"
git log --oneline -1                                                      # esperado: 7e19462 ou mais novo
ls sdd/handoffs/HANDOFF_INCORPORAR_STARTER.md sdd/features/PLANO_F4_F15_CONSOLIDADO.md
GIT_TERMINAL_PROMPT=0 git fetch -q origin && git log --oneline -1 origin/main   # se main andou, rebase antes de começar
GIT_TERMINAL_PROMPT=0 git fetch -q origin tag v2.2.6                      # base do check-versions
```

Se a pasta não existir (alguém a removeu), recrie do zero:

```bash
cd /Users/robertoduarte/rdd-public/sdd-open
GIT_TERMINAL_PROMPT=0 git fetch -q origin
git worktree add /Users/robertoduarte/rdd-worktrees/sdd-open-f6-docs -b feat/f6-docs origin/main
cd /Users/robertoduarte/rdd-worktrees/sdd-open-f6-docs
git checkout origin/docs/incorporar-starter -- sdd/features sdd/handoffs sdd/reports sdd/reviews
git rm -r -q --cached sdd/features sdd/handoffs sdd/reports sdd/reviews   # ficam no disco, fora do commit
```

Se `/Users/robertoduarte/rdd-public/sdd-open` não for o clone de `https://github.com/robertodiasduarte/sdd-open.git`, use a worktree da sessão 3 como base: `git -C /Users/robertoduarte/rdd-worktrees/sdd-open-f5-conhecimento worktree add …`. Não trabalhe nas worktrees antigas (`sdd-open-incorporar-starter`, `sdd-open-w0-m1`, `sdd-open-f4-conversa`, `sdd-open-f5-conhecimento`). O `sdd/ambiente.md` do checkout principal é nota local da `sdd-new-session` do starter, não rastreada; não o commite.

**Por que só a F6:** o Roberto perguntou se F6 e F7 cabiam juntas; a regra do par (plano, seção 10) não se aplica, porque a F7 é grande (13 itens, 5 scripts, `verify-gate.sh --trace`, 3 decisões) e as duas tocam a `sdd-build` e o `docs/roadmap.md`. A F7 fica para a sessão 5.

Depois, leia nesta ordem:
- `sdd/features/PLANO_F4_F15_CONSOLIDADO.md`:
  - seção 0, com os 4 parâmetros P1–P4;
  - **4.3 (F6 Docs)**, com os itens I (`docs/roadmap.md`), J (já entregue na M1) e K (fora da F6);
  - 8.0, com a regra 10 e a tabela de degradação;
  - 10, com o agrupamento.
- `sdd/handoffs/HANDOFF_INCORPORAR_STARTER.md`: a Ficha (critérios 1–10 do "Pronto quando"), `## Eventos` e a etapa "F5 Conhecimento", que é a do topo.
- `sdd/features/AVALIACAO_STARTER_PARA_OPEN.md`: os componentes 15 ("Por que cada regra existe") e 16 (docs).
- `sdd/templates/fragments/PERGUNTA_DECISAO.md`: o formato de pergunta e de parada.

## Onde paramos

- **F1–F5, W0 e M1 entregues.** A última Release é https://github.com/robertodiasduarte/sdd-open/releases/tag/v2.2.6:
  - tag em `7e19462`;
  - SHA-256 de `sdd-open-v2.2.6.tar.gz` `5dedf04b5046574c44664f3e1daa72af5877859ebb7bba35da58cab0e842a114`, conferido.
- **`main` está em `7e19462`.** É a F5: `sdd-kb` 2.2.0 (17ª skill, KB em `sdd/kb/`, `gate.sh` autossuficiente, `validate_kb.py --strict` com `teste` existente), `sdd/bin/kb-dominios.py`, `sdd-define` 2.3.0 (passo 10) e `sdd-ux-review` 2.3.0 (entrevista de público).
- **Estado do pacote:**
  - 17 skills;
  - 499 testes verdes no piso `SDD_TEST_BASH=/bin/bash /usr/bin/python3` (Python 3.9.6, bash 3.2.57), local e no `macos-latest`.
- **Esta sessão faz a F6 inteira**, do brainstorm à release (ou ao push, se nada que dispara Release mudar).

## Contexto que você precisa ter

- **Remoto:** `https://github.com/robertodiasduarte/sdd-open.git`.
- **Release automática:** sai no push de `main` que toca:
  - `.agents/skills/**`, `bin/**`, `sdd/bin/**`, `sdd/templates/**` ou `sdd/fixtures/**`;
  - `sdd/playbook.md`, `sdd/config.example.yaml` ou `AGENTS.md.tmpl`.

  `docs/**`, `README.md` e `tests/` **não** disparam Release (a M1 saiu sem tag). Mas "Por que cada regra existe" nas skills de fase e o `AGENTS.md.tmpl` disparam. O patch é calculado a partir da última tag (`scripts/next-version.sh`); uma tag `vX.Y.Z` empurrada à mão também vira Release. O job `release` espera `testes` **e** `testes-macos`.
- **Escopo da F6** (plano, 4.3, e avaliação, componentes 15 e 16):
  - quickstart com "valide antes de seguir" (`docs/quickstart.md` e `docs/pt-BR/quickstart.md`) e a tabela "onde roda → ferramenta";
  - guia do aluno adaptado ao open, a partir de `/Users/robertoduarte/rdd-public/sdd-starter/docs/guia-do-aluno.pt-BR.md` (494 linhas, **não rastreado** naquele checkout: não rode `git clean` lá);
  - "Por que cada regra existe" nas skills de fase (no starter: `sdd-iniciar-repo/SKILL.md:342`, `sdd-new-session/SKILL.md:359`, `sdd-release/SKILL.md:331`);
  - README e `AGENTS.md.tmpl` citando as 3 skills da F2 (`sdd-checar-ambiente`, `sdd-higiene-dado`, `sdd-iniciar-repo`), a `sdd-kb` e o `kb-dominios.py` da F5, e o bloco do OK da F3. Hoje o `AGENTS.md.tmpl:13` só lista as fases, e o `README.md:53` mostra o fluxo `/sdd-brainstorm → … → /sdd-release`;
  - **item I**: `docs/roadmap.md` com W1–W5 como planejadas (hooks e evidência, fluxo encadeado, revisão adversarial, contexto e governança, loop-builder e drive), no tom de "Specs como deltas" do `docs/comparison.md`, que continua declarado como planejado (critério 6 da Ficha).
  - **item K**: `docs/hooks.md`, `docs/review-contract.md` e `docs/decisoes-D1-D5.md` **não** entram (nascem na W1, W3 e W2).
- **Decisões a levar ao brainstorm:** se o guia do aluno vai em `docs/pt-BR/guia-do-aluno.md` só em português ou também em inglês; quais skills de fase recebem "Por que cada regra existe" (todas as 7 de fase ou só as que têm regra contraintuitiva); se a F6 sai com Release (só se tocar skill ou `AGENTS.md.tmpl`) — pergunte ao Roberto se é `v2.2.7` (automático) ou `v2.3.0` (tag à mão; a F5 trouxe skill nova e saiu `v2.2.6` por escolha dele).
- **Decisões já tomadas, não reabrir:**
  - a camada de conversa fica sempre ligada;
  - o Status `✅ ▶️ ⬜ ⏸️ ➖` abre cada resposta, com o nome da fase como 1ª palavra;
  - toda pergunta tem a recomendada primeiro, a opção "não sei" e nunca "Outro" (`PERGUNTA_DECISAO.md`);
  - o open é a fonte canônica de governança, auditoria-harness e prompt-builder;
  - a KB fica em `sdd/kb/` fixo, sem slot;
  - os artefatos SDD ficam na branch `docs/`.
- **Skills do fluxo** (em `/Users/robertoduarte/.claude/skills/`): `sdd-brainstorm`, `sdd-define`, `sdd-design`, `sdd-build`, `sdd-handoff`. A `sdd-release` é a do pacote (`.agents/skills/sdd-release/SKILL.md`, 2.3.0).
  - Fluxo SDD completo, com revisão de contexto fresco do DESIGN antes do build e do build depois (modo `veredito`, numa worktree destacada). Se der NEEDS_WORK, faça o ciclo 2 sobre as correções.
  - Moldes da evidência: `sdd/reports/evidence/F5_CONHECIMENTO/` (`gerar-evidencia.sh`, `sabotagem.sh`, `comandos-intactos.py`).
  - O `report-lint` exige a pasta `evidence/<FEATURE>/` com o mesmo nome do `BUILD_REPORT_<FEATURE>.md`.
  - O DESIGN passa em dois lints: `python3 sdd/bin/design-lint.py` e o `scripts/validate_design.py` da skill de design, que reprova chaves `{…}` e a sigla de "a definir" **até dentro de código** e um 2º título "Next Step" no texto.
- **Versões atuais:**
  - auditoria-harness 1.1.0, brainstorm 2.1.0, build 2.2.0, checar-ambiente 1.4.0, define 2.3.0, design 2.1.0, governanca 2.2.0, handoff 2.1.0;
  - iterate 2.1.0, kb 2.2.0, new-session 1.2.0, playbook 2.1.0, prompt-builder 2.1.0, release 2.3.0, ux-review 2.3.0;
  - (portadas, sem a F4) higiene-dado 1.1.1, iniciar-repo 1.1.1.

  Toda skill tocada sobe de versão e atualiza a linha de identificação: `python3 scripts/check-versions.py --base v2.2.6 --base-obrigatoria`.

## Tarefas, em ordem

1. **Brainstorm da F6** com a `sdd-brainstorm`, gravando `sdd/features/BRAINSTORM_F6_DOCS.md` a partir da seção 4.3 do plano. Pronto quando: as decisões acima foram respondidas pelo Roberto, a abordagem foi confirmada e os cortes YAGNI e os 2 checkpoints estão registrados.
2. **Define e design**:
   - `sdd/features/DEFINE_F6_DOCS.md`, com ATs em EARS e o `verify_gate` `kind: test` de sempre: `cmd` = `T=$(mktemp -d) && git archive HEAD | tar -x -C $T && PUBLISH_GATE_MODE=ci bash scripts/publish-gate.sh $T && cd $T && SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover -s tests -p 'test_*.py'`;
   - `sdd/features/DESIGN_F6_DOCS.md`, com o File Manifest.

   Pronto quando: `verify-gate.sh --print` 0, `python3 sdd/bin/design-lint.py` 0 e a revisão de contexto fresco do DESIGN aplicada.
3. **Build**, com commit antes do gate e todo arquivo novo no `MANIFEST.txt`, em ordem `LC_ALL=C`. Pronto quando:
   - `bash sdd/bin/verify-gate.sh --strict sdd/features/DEFINE_F6_DOCS.md` 0 e `python3 sdd/bin/report-lint.py sdd/reports/BUILD_REPORT_F6_DOCS.md` 0;
   - `python3 sdd/bin/skill-lint.py --conversa .agents/skills/sdd-*/SKILL.md` 0 nas 17 skills, e `wc -l` ≤ 500 em cada `SKILL.md` depois de "Por que cada regra existe";
   - os links dos docs novos existem (teste que abre cada link relativo);
   - houve 1 sabotagem por script alterado ou novo;
   - a revisão de contexto fresco terminou sem HIGH aberto.
4. **Release**:
   - PR com CI verde em `ubuntu-latest` **e** `macos-latest`;
   - bloco do OK da `sdd-release`;
   - OK do Roberto **citando "sdd-open" na mesma mensagem**. Sem isso, não faça o push;
   - push fast-forward em `main`.

   Pronto quando: se houve Release, `gh release view` mostra `SHA256SUMS.txt` e `shasum -a 256 -c` confere; se não houve (só `docs/`, `README.md`, `tests/`), a run do `publish-gate` em `main` está verde.
5. **Fechar**: rode a `sdd-handoff` com a etapa F6 no topo e o prompt da sessão 5 (F7 Evidência: plano, seção 8, "F7"). Grave os artefatos na branch `docs/` **sem trocar de branch na worktree**:

   ```bash
   cd /Users/robertoduarte/rdd-worktrees/sdd-open-f6-docs
   T=$(mktemp -d) && GIT_TERMINAL_PROMPT=0 git fetch -q origin docs/incorporar-starter
   git worktree add -q "$T" docs/incorporar-starter
   for d in features handoffs reports reviews; do mkdir -p "$T/sdd/$d" && rsync -a --delete "sdd/$d/" "$T/sdd/$d/"; done
   git -C "$T" add sdd/features sdd/handoffs sdd/reports sdd/reviews && git -C "$T" commit -q -m "docs(incorporar-starter): sessão 4 — F6 Docs" && GIT_TERMINAL_PROMPT=0 git -C "$T" push -q origin docs/incorporar-starter
   git worktree remove --force "$T"
   ```

## O que não quebrar

- **Camada de conversa** (F4 + F5): o bloco comum está em 15 `SKILL.md` (as 14 da F4 + `sdd-kb`); não mexa nele sem trocar nas 15 e nas `FRASES` do `tests/test_conversa.py`. A linha de identificação vem "uma vez só, antes do Status", com a versão do frontmatter. "Por que cada regra existe" entra como seção nova, sem mexer nos passos (o `comandos-intactos` da F5 é o molde).
- **`sdd-kb`** (F5): `gate.sh` (linha única no verde, 4/12), `TextoDaSkill` (nenhum caminho de fora, nenhum `scripts/validate_kb.py` sem `.agents/skills/sdd-kb/`), `PORTADAS`, `EntrevistaPublico`; o `kb-dominios.py` lê só o `## Technical Context` do DEFINE.
- **Contratos de `sdd/`**: os seis exits de `sdd/bin/verify-gate.sh` (0/2/3/4/5/64) e as fixtures de `sdd/fixtures/` ficam idênticos; `playbook-lint.sh --self-test` sai 0; os lints mantêm 0/1/64; o bloco do OK da `sdd-release` mantém rótulos, ordem e uma pergunta só; o passo 4 da `sdd-iterate` segue como a W0 fixou.
- **CI da M1**: nada de caractere invisível nem `curl … | sh` literal em `.agents/skills/` (os docs podem descrever, mas confira o passo "Skill integrity"); piso Python 3.9 / bash 3.2 afirmado.
- **Padrão agnóstico (P2)**: `tests/test_agnostico.py` reprova `AskUserQuestion`, `TodoWrite`, `PreToolUse`, `PostToolUse`, `subagent_type`, `Task tool`, `Agent tool` e `/model` em `.agents/skills/**`, `sdd/templates/**`, `AGENTS.md.tmpl` e `sdd/playbook.md`. O guia do aluno do starter cita ferramentas de agentes específicos: o que for para o `AGENTS.md.tmpl` ou para uma skill tem de passar nesse teste; os `docs/` não são varridos, mas a tabela "onde roda → ferramenta" deve tratar os 7 agentes por igual.
- **Literais que o publish-gate reprova** (`scripts/publish-gate-patterns.txt`): e-mail só em `example.com/.org/.net`; CPF, CNPJ, telefone, sequências de 11+ dígitos e caminho `/Users/<nome>/` não podem aparecer nos docs. O guia do starter pode ter exemplo real: confira antes de copiar.
- **Arquivos**: `python3 -B` e `git add` por nome (não há `.gitignore`); bash 3.2, nada de `rm -rf` com variável sem `"${X:?}"`; `sdd/features|handoffs|reports|reviews/` **nunca** entram em commit da branch de trabalho; todo arquivo novo de `docs/` entra no `MANIFEST.txt`.
- **Push e remoto**: todo comando remoto com `GIT_TERMINAL_PROMPT=0`; push em `main` só com OK explícito do Roberto citando "sdd-open"; nunca `--force`; a branch `docs/incorporar-starter` nunca vira PR.
- **Fora de escopo nesta sessão:**
  - os documentos de mecanismo `docs/hooks.md`, `docs/review-contract.md`, `docs/decisoes-D1-D5.md` (W1, W3, W2);
  - a tabela WCAG e a leitura de `UX_REVIEW_*.md` anteriores (W5);
  - o encadeamento entre fases e as classes D1–D5 (F9);
  - o fail-open do `report-lint.py` (F7);
  - regenerar o sdd-starter a partir do open (frente própria, depois da F6);
  - alterar o sdd-starter ou o repositório privado.

## Como fechar

Ao terminar, rode a skill **SDD Handoff by RDD** de novo para registrar o que foi feito
e preparar a próxima retomada.
