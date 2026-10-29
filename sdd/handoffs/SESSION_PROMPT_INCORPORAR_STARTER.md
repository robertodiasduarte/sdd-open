# Continuar: INCORPORAR_STARTER — sessão 2: F4 Conversa

Esta sessão começa numa **worktree limpa**. Os artefatos SDD da família (features, handoffs, reports) vivem na branch `docs/incorporar-starter` do remoto, nunca mesclada em `main`.

## Preparar a worktree (antes de ler qualquer coisa)

```bash
cd /Users/robertoduarte/rdd-public/sdd-open
GIT_TERMINAL_PROMPT=0 git fetch -q origin
git worktree add /Users/robertoduarte/rdd-worktrees/sdd-open-f4-conversa -b feat/f4-conversa origin/main
cd /Users/robertoduarte/rdd-worktrees/sdd-open-f4-conversa
git checkout origin/docs/incorporar-starter -- sdd/features sdd/handoffs sdd/reports
git rm -r -q --cached sdd/features sdd/handoffs sdd/reports     # ficam no disco, fora do commit
git status --short | head -3                                    # esperado: só "?? sdd/…"
git log --oneline -1                                            # esperado: dd27ef6 ou mais novo
GIT_TERMINAL_PROMPT=0 git fetch -q origin tag v2.2.4            # base do check-versions
```

Se `/Users/robertoduarte/rdd-public/sdd-open` não for o clone de `https://github.com/robertodiasduarte/sdd-open.git`, use a worktree da sessão 1 como base: `git -C /Users/robertoduarte/rdd-worktrees/sdd-open-w0-m1 worktree add …`. Não trabalhe nas worktrees antigas (`sdd-open-incorporar-starter`, `sdd-open-w0-m1`).

Depois, leia nesta ordem:
- `sdd/features/PLANO_F4_F15_CONSOLIDADO.md`: seção 0 (os 4 parâmetros P1–P4), **4.1 (F4 Conversa, itens A–G)**, **5 (decisões 2 e 3)**, 8.0 (regra 10 e tabela de degradação por vendor) e 10 (agrupamento);
- `sdd/handoffs/HANDOFF_INCORPORAR_STARTER.md`: a Ficha, `## Eventos` e as etapas "M1" e "W0" (as duas do topo);
- `sdd/features/AVALIACAO_STARTER_PARA_OPEN.md`: a parte da camada "Como falar com o aluno".

## Onde paramos

- **F1–F3, W0 e M1 entregues.** A última Release é https://github.com/robertodiasduarte/sdd-open/releases/tag/v2.2.4 (tag em `303cc87`, SHA-256 do pacote `b8a0aab0d58b87050d80c68813c868f6a2d4f9784fe7130ad663efc63a555670`, conferido).
- **`main` está em `dd27ef6`.** É a M1: CI com job `testes-macos`, checkout v5.1.0 e o passo "Skill integrity". Ela não gerou tag.
- **Estado do pacote:** 16 skills e 326 testes verdes no piso `SDD_TEST_BASH=/bin/bash /usr/bin/python3` (Python 3.9.6, bash 3.2.57), local e no `macos-latest`.
- **Esta sessão faz a F4 inteira**, do brainstorm à release: a camada de conversa nas 13 skills nativas, mais os itens A–G que o plano trouxe do porte.

## Contexto que você precisa ter

- **Remoto:** `https://github.com/robertodiasduarte/sdd-open.git`.
- **Release automática:** sai no push de `main` que toca `.agents/skills/**`, `bin/**`, `sdd/bin/**`, `sdd/templates/**`, `sdd/fixtures/**`, `sdd/playbook.md`, `sdd/config.example.yaml` ou `AGENTS.md.tmpl` (patch calculado a partir da última tag). Uma tag `vX.Y.Z` empurrada à mão também vira Release.
  - A F4 muda as 13 skills: pergunte ao Roberto no OK se ela sai como patch automático (`v2.2.5`) ou como minor (`v2.3.0`). Sendo minor, a tag vai depois da run de `main`, para não ficarem duas tags.
  - O `release` agora espera `testes` **e** `testes-macos`. Confira na primeira run que os dois rodaram.
- **Escopo da F4** (plano, 4.1):
  - a seção `## Como falar com o aluno` + `references/como-falar.md` nas 13 skills nativas: `sdd-auditoria-harness`, `sdd-brainstorm`, `sdd-build`, `sdd-define`, `sdd-design`, `sdd-governanca`, `sdd-handoff`, `sdd-iterate`, `sdd-new-session`, `sdd-playbook`, `sdd-prompt-builder`, `sdd-release` e `sdd-ux-review`;
  - a fonte vem do starter para 7 (brainstorm, build, define, design, handoff, new-session, release); as outras 6 são escritas do zero;
  - o `skill-lint.py` passa a conferir a seção;
  - `design-lint.py` e `handoff-lint.py` em `sdd/bin/`;
  - `metadata.updated` + a linha de identificação;
  - os itens do porte: A (linha de transição ≤100 caracteres), B (`sdd/templates/fragments/PERGUNTA_DECISAO.md`), C (formato da parada ⏸️, que a F9 liga ao exit 40), D (fixtures que **reprovam** no `skill-lint`), E (o `design-lint` fixa `## Key Decisions` / `### Decision N: <nome>`), F (o `handoff-lint` aceita seção extra) e G (`tests/test_agnostico.py`).
- **Decisões a levar ao brainstorm** (plano, seção 5):
  - **Decisão 2:** "não sei" × "sem 'Outro'". A recomendação é (a), as duas.
  - **Decisão 3:** a F4 absorve os itens A–F? A recomendação é sim.
- **Decisões já tomadas, não reabrir:**
  - a camada fica sempre ligada, sem toggle nem slot;
  - o Status `✅ ▶️ ⬜ ⏸️ ➖` abre cada resposta; o banner `🧠 FASE` é a 1ª palavra do Status; o kanban do `RESUMO_ETAPA.md` fica intacto;
  - o open é a fonte canônica de `sdd-governanca`, `sdd-auditoria-harness` e `sdd-prompt-builder`;
  - os artefatos SDD ficam na branch `docs/`.
- **Fonte no sdd-starter:** `/Users/robertoduarte/rdd-public/sdd-starter`, em `main` `17c69c4`:
  - `skills/*/SKILL.md` (a seção `## Como falar com o aluno`) e `skills/*/references/como-falar.md`;
  - `sdd/DEFINE_LINGUAGEM_ALUNO.md`, com os 10 itens da camada;
  - `skills/sdd-design/scripts/validate_design.py` e `skills/sdd-handoff/scripts/validate_handoff.py`, para **reescrever**, não portar;
  - o `docs/guia-do-aluno.pt-BR.md` daquele checkout não é rastreado (entrada da F6): não rode `git clean` lá.
- **Skills do fluxo** (em `/Users/robertoduarte/.claude/skills/`): `sdd-brainstorm`, `sdd-define`, `sdd-design`, `sdd-build`, `sdd-handoff`. A `sdd-release` é a do pacote, `.agents/skills/sdd-release/SKILL.md`. A F4 é fluxo SDD completo: BRAINSTORM → DEFINE → DESIGN → BUILD, com revisão de contexto fresco antes do PR. Molde da evidência: `sdd/reports/evidence/W0/` e `sdd/reports/evidence/M1/` (`gerar-evidencia.sh`, `sabotagem.sh`).
- **Versões atuais:**
  - auditoria-harness 1.0.0, brainstorm 2.0.0, build 2.1.1, define 2.1.0, design 2.0.0, governanca 2.1.0;
  - handoff 2.0.0, iterate 2.0.1, new-session 1.1.0, playbook 2.0.0, prompt-builder 2.0.0, release 2.2.0, ux-review 2.1.0;
  - (portadas, fora da F4) checar-ambiente 1.3.0, higiene-dado 1.1.1, iniciar-repo 1.1.1.

  A F4 sobe as 13: `python3 scripts/check-versions.py --base v2.2.4 --base-obrigatoria`.

## Tarefas, em ordem

1. **Brainstorm da F4** com a `sdd-brainstorm`, gravando `sdd/features/BRAINSTORM_F4_CONVERSA.md`, com a seção 4.1 do plano como entrada. Pronto quando: decisões 2 e 3 respondidas pelo Roberto, abordagem confirmada, cortes YAGNI e 2 checkpoints.
2. **Define e design**: `sdd/features/DEFINE_F4_CONVERSA.md`, com ATs em EARS e o `verify_gate` `kind: test` de sempre (`cmd` = cópia por `git archive HEAD`, `PUBLISH_GATE_MODE=ci bash scripts/publish-gate.sh`, `unittest discover` no piso), e `sdd/features/DESIGN_F4_CONVERSA.md`, com o File Manifest. Pronto quando: `verify-gate.sh --print` 0 e o `design-lint` novo aprova o próprio DESIGN.
3. **Build**, com commit antes do gate e arquivo novo no `MANIFEST.txt` em ordem `LC_ALL=C`. Para cada skill, um diff que prove que comandos e ordem dos passos não mudaram. Pronto quando:
   - `bash sdd/bin/verify-gate.sh --strict sdd/features/DEFINE_F4_CONVERSA.md` 0 e `python3 sdd/bin/report-lint.py sdd/reports/BUILD_REPORT_F4_CONVERSA.md` 0;
   - o `test_agnostico` falha na `v2.2.4` (o `CLARIFY.md:45` ainda diz `AskUserQuestion`);
   - 1 sabotagem por script alterado ou novo (`skill-lint.py`, `design-lint.py`, `handoff-lint.py`);
   - a revisão de contexto fresco sem HIGH aberta.
4. **Release**: PR com CI verde em `ubuntu-latest` **e** `macos-latest`; bloco do OK da `sdd-release`; OK do Roberto **citando "sdd-open" na mesma mensagem** (sem isso, não faça o push); push fast-forward em `main`. Pronto quando: `gh release view` mostra `SHA256SUMS.txt` e `shasum -a 256 -c` confere.
5. **Fechar**: rode a `sdd-handoff` com a etapa F4 no topo e o prompt da sessão 3 (F5 Conhecimento: plano, seção 4.2, e decisão 4 da seção 5). Grave os artefatos na branch `docs/` **sem trocar de branch na worktree**:

   ```bash
   cd /Users/robertoduarte/rdd-worktrees/sdd-open-f4-conversa
   T=$(mktemp -d) && GIT_TERMINAL_PROMPT=0 git fetch -q origin docs/incorporar-starter
   git worktree add -q "$T" docs/incorporar-starter
   rsync -a --delete sdd/features/ "$T/sdd/features/" && rsync -a --delete sdd/handoffs/ "$T/sdd/handoffs/" && rsync -a --delete sdd/reports/ "$T/sdd/reports/"
   git -C "$T" add sdd/features sdd/handoffs sdd/reports && git -C "$T" commit -q -m "docs(incorporar-starter): sessão 2 — F4 Conversa" && GIT_TERMINAL_PROMPT=0 git -C "$T" push -q origin docs/incorporar-starter
   git worktree remove --force "$T"
   ```

## O que não quebrar

- **Contratos de `sdd/`**:
  - os seis exits de `sdd/bin/verify-gate.sh` (0/2/3/4/5/64) e `sdd/fixtures/` ficam idênticos; `playbook-lint.sh --self-test` 0;
  - o bloco do OK da `sdd-release` mantém os rótulos e a ordem, com uma pergunta só, na última linha (`tests/test_contrato_build_release.py`); a camada entra **em volta** dele;
  - o BUILD_REPORT mantém `## Files…` e `## Migrations aplicadas`, com as colunas que o `report-lint` lê.
- **Contratos da W0** (`tests/test_correcoes_w0.py`):
  - o passo 4 da `sdd-iterate` mantém as duas chamadas `sdd/bin/verify-gate.sh … <DEFINE>` entre crases e o aviso de smoke/eval;
  - os briefs de `contexto-fresco.md` mantêm "o único arquivo que você grava de propósito, pelo shell, é `sdd/reports/evidence/{F}/AVAL-*.log`";
  - nenhum arquivo do `MANIFEST.txt` cita `/drive`, `build-report-guard`, `CONTEXTO de domínio`, "Step 1.5", "slice 2", `/bug-pipeline` ou "`/define` (Step".
- **CI da M1** (`tests/test_release_workflow.py`):
  - texto novo de skill sem caractere invisível (U+200B/200C, bidi, tag, seletor de variação, soft hyphen) e sem `curl … | sh`, `bash <(curl …)` ou `source <(curl …)` literal; emoji com ZWJ e FE0F passa;
  - código que só roda em Python ≥3.10 reprova no `macos-latest`, porque o piso é afirmado;
  - em teste, amostra com Unicode invisível se monta com `chr()`, nunca com o caractere literal, e os bytes se conferem depois de escrever.
- **Padrão agnóstico (P2)**: nenhum texto novo cita ferramenta de um agente só (`AskUserQuestion`, `Agent`, `PreToolUse`, `TodoWrite`, `Task`, `subagent`, `/model`, `Write`/`Edit` como ferramenta). O que é de um vendor mora no adaptador do `init`.
- **Literais que o publish-gate reprova** (`scripts/publish-gate-patterns.txt`): e-mail só em `example.com/.org/.net`; CPF, CNPJ, telefone, `git@host` e sequências de 11+ dígitos montados em tempo de execução; hosts em `.invalid`.
- **Arquivos**:
  - `python3 -B`; `git add` por nome (não há `.gitignore`); bash 3.2, sem `mapfile`/`declare -A`/`${x^^}`; sem shebang zsh nem symlink; nada de `chmod` em massa;
  - `tests/test_skill_lint.py` continua com 16 skills;
  - `sdd/features/`, `sdd/handoffs/` e `sdd/reports/` **nunca** entram em commit da branch de trabalho.
- **Push e remoto**: todo comando remoto com `GIT_TERMINAL_PROMPT=0`; push em `main` só com OK explícito do Roberto citando "sdd-open"; nunca `--force`; a branch `docs/incorporar-starter` nunca vira PR.
- **Fora de escopo nesta sessão:**
  - o encadeamento automático entre fases, a seção "Encerramento", as classes D1–D5 nas perguntas e o `sdd-fluxo.sh` (tudo da F9);
  - qualquer item de F5–F15;
  - corrigir o fail-open do `report-lint.py` com cabeçalho não reconhecido (F7);
  - alterar o sdd-starter ou o repositório privado.

## Como fechar

Ao terminar, rode a skill **SDD Handoff by RDD** de novo para registrar o que foi feito
e preparar a próxima retomada.
