# Continuar: INCORPORAR_STARTER — sessão 7: F9 Fluxo encadeado

Esta sessão começa numa **worktree limpa**. Os artefatos SDD da família (features, handoffs, reports, reviews) vivem na branch `docs/incorporar-starter` do remoto, nunca mesclada em `main`.

## Preparar a worktree (antes de ler qualquer coisa)

A frente da F9 **ainda não foi aberta**. Crie a worktree `/Users/robertoduarte/rdd-worktrees/sdd-open-f9-fluxo` com a branch `feat/f9-fluxo` nascida de `origin/main` = `7c640eb` (tag `v2.2.9`) — do remoto, porque a `main` local do checkout principal está em `1c9bbc7`, atrás:

```bash
cd /Users/robertoduarte/rdd-public/sdd-open
GIT_TERMINAL_PROMPT=0 git fetch -q origin
git log --oneline -1 origin/main                                          # esperado: 7c640eb ou mais novo
git worktree add /Users/robertoduarte/rdd-worktrees/sdd-open-f9-fluxo -b feat/f9-fluxo origin/main
cd /Users/robertoduarte/rdd-worktrees/sdd-open-f9-fluxo
GIT_TERMINAL_PROMPT=0 git fetch -q origin tag v2.2.9                      # base do check-versions
GIT_TERMINAL_PROMPT=0 git fetch -q origin docs/incorporar-starter
git checkout origin/docs/incorporar-starter -- sdd/features sdd/handoffs sdd/reports sdd/reviews
git rm -r -q --cached sdd/features sdd/handoffs sdd/reports sdd/reviews   # ficam no disco, fora do commit
git branch --show-current                                                 # esperado: feat/f9-fluxo
git status --short | head -4                                              # esperado: só "?? sdd/…"
ls sdd/handoffs/HANDOFF_INCORPORAR_STARTER.md sdd/features/PLANO_F4_F15_CONSOLIDADO.md
```

Se `/Users/robertoduarte/rdd-public/sdd-open` não for o clone de `https://github.com/robertodiasduarte/sdd-open.git`, use a worktree da sessão 6 como base (`git -C /Users/robertoduarte/rdd-worktrees/sdd-open-f8-hooks worktree add …`), se ela ainda existir. Não trabalhe na worktree antiga `sdd-open-f8-hooks` (branch já mesclada). O `sdd/ambiente.md` do checkout principal é nota local da `sdd-new-session` do starter, não rastreada; não o commite. Se a `sdd-new-session` for usada para abrir a frente, os nomes acima são os da família (não o `../sdd-open-frentes/<slug>` padrão da skill).

Depois, leia nesta ordem:
- `sdd/features/PLANO_F4_F15_CONSOLIDADO.md`:
  - seção 0, com os 4 parâmetros P1–P4 (a F9 segue no **P4** e é uma das duas frentes que o **P2** manda provar também no Codex CLI);
  - seção 8: o preâmbulo comum a F7–F14, **8.0** (as 10 regras do PORTE e a tabela de degradação por vendor — a linha "subagente nativo → brief em `sdd/reports/briefs/` + `exit 40 AGUARDANDO_HUMANO`" é da F9), o quadro **"F9 Fluxo encadeado e decisões"** (linhas 266–276);
  - **8.1 "F9 Fluxo encadeado"** (linhas 360–368: F1, F2, F3, F6, F7, F8, F10, F11 do PORTE), **8.2** (slots `flow.autonomous` e `review.security_globs`, linhas 426–427; o parágrafo sobre `layers:` lido pelo `sdd-fluxo.sh`, linha 444) e **8.3** (fontes no privado, linha F9: `scripts/sdd-fluxo.sh` 283 linhas / 4 refs RDD · `scripts/sdd-decisoes-lint.sh` 103 / 0);
  - seção 10 (uma frente grande por sessão; a F9 vai sozinha).
- `sdd/handoffs/HANDOFF_INCORPORAR_STARTER.md`: a Ficha, `## Eventos` e a etapa "F8 Hooks", que é a do topo.
- `sdd/templates/fragments/PERGUNTA_DECISAO.md` (92 linhas): o item 9 ("Classe da decisão: reservado", linha 39) é o lugar das classes D1–D5; o formato de parada ⏸️ é a face humana do exit 40.
- As 9 `SKILL.md` com `## Encerramento (obrigatório)` em `.agents/skills/` (`grep -l '^## Encerramento (obrigatório)' .agents/skills/sdd-*/SKILL.md`): é onde a seção "Encerramento" encadeada entra; o diff por skill da F4 (`git log -p 2fcdda1 -- .agents/skills`) mostra o que já mudou lá.
- `sdd/bin/verify-gate.sh` (exits 0/2/3/4/5/64, `--print`, `--trace`), `sdd/bin/report-lint.py` e `sdd/bin/avaliador-guard.sh` — o `sdd-fluxo.sh` encadeia a partir deles.
- `.agents/skills/sdd-define/SKILL.md` (passo 8, a heurística `LLM Prompts` que ganha pontuação forte/fraco), `sdd-design` (onde entra o `[auto]`), `sdd-brainstorm` (passo 1, tipos de entrada) e `sdd-ux-review` (passo 1, onde se leem os `UX_REVIEW_*.md` anteriores).

## Onde paramos

- **F1–F8, W0 e M1 entregues; o P3 (starter) está concluído; o P4 está na F8.** A última Release é https://github.com/robertodiasduarte/sdd-open/releases/tag/v2.2.9:
  - tag em `7c640eb`;
  - SHA-256 de `sdd-open-v2.2.9.tar.gz` `b022f5529b9cac171cb38cef7d7277fd8e5e485a84d449e359b62ac07ae03f6b`, conferido.
- **`main` está em `7c640eb`.** É a F8: `sdd/hooks/pre-commit` (dispatcher H2–H6 + `report-lint --stdin` do `BUILD_REPORT` staged + alarme da higiene quando `git config sdd.higieneDado` = `on`; recusa única com classes e `RESULTADO: COMMIT RECUSADO`), `sdd/hooks/pre-push` (só avisa), `init` liga `core.hooksPath = sdd/hooks` com confirmação, `doctor` confere, slot `project.context_file_max_kb: 100`, `sdd-higiene-dado` 1.2.0 (modo hooks), adaptador do Claude Code (`init --vendors claude` gera `.claude/hooks/sdd-report-guard.py` e `sdd-avaliador-guard.py` e faz merge em `.claude/settings.json`), `docs/hooks.md` + PT.
- **Estado do pacote:**
  - 17 skills;
  - 683 testes verdes no piso `SDD_TEST_BASH=/bin/bash /usr/bin/python3` (Python 3.9.6, bash 3.2.57), local e no `macos-latest`;
  - o roadmap (`docs/roadmap.md` + PT) tem 6 linhas; `tests/test_docs.py` conta.
- **Esta sessão faz a F9 inteira**, do brainstorm à release.

## Contexto que você precisa ter

- **Remoto:** `https://github.com/robertodiasduarte/sdd-open.git`.
- **Release automática:** sai no push de `main` que toca:
  - `.agents/skills/**`, `bin/**`, `sdd/bin/**`, `sdd/hooks/**`, `sdd/templates/**` ou `sdd/fixtures/**`;
  - `sdd/playbook.md`, `sdd/config.example.yaml` ou `AGENTS.md.tmpl`.

  A F9 toca `sdd/bin/**`, `sdd/templates/**` e `.agents/skills/**`, então **sai Release**. O patch é calculado a partir da última tag (`scripts/next-version.sh`), o que dá `v2.2.10`; uma tag `vX.Y.Z` empurrada à mão também vira Release (pergunte ao Roberto se prefere `v2.3.0`: a F9 muda o comportamento de todas as skills de fase com o encadeamento). O job `release` espera `testes` **e** `testes-macos`.
- **Escopo da F9** (plano, quadro F9 e 8.1), itens F1–F3, F6–F8, F10, F11 do PORTE §5.3 (F4 e F5 do PORTE já entraram na F4 desta frente):
  - **F1** `sdd/templates/fragments/FLUXO_ENCADEADO.md` + seção "Encerramento" em cada skill de fase: Define pronto + `verify-gate.sh --print` 0 + zero marcadores → chama a fase seguinte na mesma sessão; `--parar` desliga; `flow.autonomous: false` por default (D1);
  - **F2** classes de decisão no item 9 reservado do `PERGUNTA_DECISAO.md`: **D1** irreversível · **D2** produto · **D3** política · **D4** teto · **D5** impasse — toda pergunta leva a classe; `sdd/bin/sdd-decisoes-lint.sh` com `--sites <pasta>` e `--self-test` (fixtures de pergunta sem classe, com "Outro", com jargão e com 2 recomendadas, todas reprovadas — a F4 já tem as fixtures do `skill-lint --conversa` em `sdd/fixtures/conversa/`, as de classe entram ao lado);
  - **F3** recibo "Decidi sozinho": o sinal que decidiu e como reverter;
  - **F6** no `sdd-design`: flag LLM ausente vira `true` (conservador); re-check com hits decide; proposta de verificabilidade aceita sem pergunta; `[auto]` registrado no DESIGN;
  - **F7** `sdd/bin/sdd-fluxo.sh` com `review-design` (EXIGIDO com ≥ 3 arquivos novos ou superfície de segurança por `review.security_globs`; manifest ilegível → exit 64 cai no default seguro) e `loop` (teto de 3 rodadas, ledger por rodada, NEEDS_WORK conta no teto, `| tee` proibido), exits **0/10/20/30/40 AGUARDANDO_HUMANO/64**, `--self-test` com um cenário por exit e um que prova a rejeição de `| tee`; o exit 40 grava o brief em `sdd/reports/briefs/`, imprime o comando da sessão nova e **para** no formato ⏸️ do `PERGUNTA_DECISAO.md` (vendor sem subagente: Codex CLI, Gemini CLI, Cursor);
  - **F8** no `sdd-define`: pontuação da heurística `LLM Prompts` — 1 sinal forte → `true`; 2 fracos → `true`; 1 fraco → `true` conservador em Notes; sinais de loop → "candidato a loop";
  - **F10** no `sdd-brainstorm`: tabela "como tratar cada tipo de entrada" (ideia vaga → "conte mais"; feature → questionar a necessidade; comparação → trade-offs);
  - **F11** no `sdd-ux-review`: ler os `UX_REVIEW_*.md` anteriores no passo 1.
- **Fontes no privado** (só leitura; o repositório privado **não** se altera). **Leia do `origin/main` do privado** (`git -C /Users/robertoduarte/RDD/Wordpress show origin/main:<arquivo>`; `origin/main` = `6ed8558dd` em 2026-10-31): `scripts/sdd-fluxo.sh` (283 linhas; 4 referências RDD viram slots), `scripts/sdd-decisoes-lint.sh` (103; a denylist de jargão da RDD sai) e `.claude/sdd/templates/fragments/FLUXO_ENCADEADO.md` (101). O checkout local de `~/RDD/Wordpress` está atrás e pode não ter as fontes. Específico da RDD não viaja (regra 4 do 8.0).
- **Decisões a levar ao brainstorm** (formato `PERGUNTA_DECISAO.md`, recomendada primeiro):
  - **D1**: o Open vira autônomo? (recomendado: configurável, `flow.autonomous: false` por default; ligado, a fase seguinte é chamada na mesma sessão quando o gate da anterior sai 0);
  - **D11**: os slots `flow.autonomous` (default `false`) e `review.security_globs` (default `""`), com OK do Roberto;
  - como o exit 40 se prova no Codex CLI (P2): se o Codex CLI estiver instalado nesta máquina (`command -v codex`), o despacho de papel fresco para em `40 AGUARDANDO_HUMANO` com o brief gravado; se não estiver, pergunte ao Roberto se instala ou se a prova fica numa fixture de `sdd-fluxo.sh --self-test` que simula a ausência de subagente — não decida sozinho;
  - onde a seção "Encerramento" encadeada entra em relação a `## Encerramento (obrigatório)` e a "Por que cada regra existe" (as 9 skills já têm as duas; a F4 fixou a ordem);
  - versão da Release (`v2.2.10` automática ou `v2.3.0` por tag).
- **Decisões já tomadas, não reabrir:**
  - a camada de conversa fica sempre ligada; `flow.autonomous` liga o encadeamento, não a conversa;
  - o Status `✅ ▶️ ⬜ ⏸️ ➖` abre cada resposta, com o nome da fase como 1ª palavra;
  - toda pergunta tem a recomendada primeiro, a opção "não sei" e nunca "Outro";
  - o open é a fonte canônica de governança, auditoria-harness e prompt-builder;
  - a KB fica em `sdd/kb/` fixo, sem slot;
  - os artefatos SDD ficam na branch `docs/`;
  - vendor sem subagente degrada para a parada ⏸️ (tabela do 8.0), nunca quebra — a F9 só liga o exit 40 ao formato que a F4 fixou;
  - `report-lint` fail-closed (D4 da F7); hooks pelo `init` com confirmação (D3 da F8); a regra REPORT pula `sdd/fixtures/` e `sdd/templates/`; a `sdd-higiene-dado` em modo hooks usa `git config sdd.higieneDado`.
- **Skills do fluxo** (em `/Users/robertoduarte/.claude/skills/`): `sdd-brainstorm`, `sdd-define`, `sdd-design`, `sdd-build`, `sdd-handoff`. A `sdd-release` é a do pacote (`.agents/skills/sdd-release/SKILL.md`, 2.4.0); a UX review é a do pacote (`.agents/skills/sdd-ux-review/SKILL.md`).
  - Fluxo SDD completo, com revisão de contexto fresco do DESIGN antes do build e do build depois (modo `veredito`, numa worktree destacada; remova-a no fim). Se der NEEDS_WORK, faça o ciclo 2 sobre as correções; a `sdd-build` limita a 2 ciclos.
  - **Antes de despachar cada avaliador**, rode `bash sdd/bin/avaliador-guard.sh --permitir sdd/features/ --permitir sdd/handoffs/ --permitir sdd/reports/ --permitir sdd/reviews/` (nunca `--permitir sdd/`) e grave o log. No brief do avaliador, peça que as sondas sigam a receita do `EVIDENCIA.md` (`rc=$?` antes do pipe): na F8, 62 acusações do `gate-shell-evidencia` vieram só de `AVAL*.log`.
  - Moldes da evidência: `sdd/reports/evidence/F8_HOOKS/` (`gerar-evidencia.sh`, `sabotagem.sh`). O Bash da sessão é zsh (sem `PIPESTATUS`): grave os logs com `/bin/bash -c` e `out=$(cmd 2>&1); rc=$?` antes de qualquer pipe, terminando em `[exit=$rc]`; sem formatador (`tail`, `sed`, `sort`…) no último estágio da linha `$`. Confira com `bash sdd/bin/gate-shell-evidencia.sh sdd/reports/evidence/F9_FLUXO` (sempre com o caminho: as frentes antigas têm acusações conhecidas e não rastreadas).
  - O `report-lint` exige a pasta `evidence/<FEATURE>/` com o mesmo nome do `BUILD_REPORT_<FEATURE>.md`, a tabela reconhecida e a linha do avaliador (ou o `AVALIACAO_<FEATURE>_<AAAAMMDD>…md` em `sdd/reviews/`).
  - O DESIGN passa em dois lints: `python3 sdd/bin/design-lint.py` e o `scripts/validate_design.py` da skill de design, que reprova chaves `{…}` numa linha **até dentro de código** (use `"$X"`, não `${X}`), título `## X` citado no meio do texto e um 2º título "Next Step".
  - `sdd/traces/` é criado a cada execução do gate na raiz e nunca entra em commit.
- **Versões atuais:**
  - auditoria-harness 1.1.0, brainstorm 2.1.1, build 2.3.0, checar-ambiente 1.4.0, define 2.3.1, design 2.1.1, governanca 2.2.1, handoff 2.1.0;
  - iterate 2.1.0, kb 2.2.0, new-session 1.2.0, playbook 2.1.0, prompt-builder 2.1.0, release 2.4.0, ux-review 2.3.1;
  - (portadas, sem a F4) higiene-dado 1.2.0, iniciar-repo 1.1.1.

  Toda skill tocada sobe de versão e atualiza a linha de identificação: `python3 scripts/check-versions.py --base v2.2.9 --base-obrigatoria`.

## Tarefas, em ordem

1. **Brainstorm da F9** com a `sdd-brainstorm`, gravando `sdd/features/BRAINSTORM_F9_FLUXO.md` a partir do quadro F9 e do 8.1 do plano. Pronto quando: D1, D11, a prova no Codex CLI, o lugar da seção "Encerramento" e a versão foram respondidas pelo Roberto, a abordagem foi confirmada e os cortes YAGNI e os 2 checkpoints estão registrados.
2. **Define, UX review e design**:
   - `sdd/features/DEFINE_F9_FLUXO.md`, com ATs em EARS e o `verify_gate` `kind: test` de sempre: `cmd` = `T=$(mktemp -d) && git archive HEAD | tar -x -C $T && PUBLISH_GATE_MODE=ci bash scripts/publish-gate.sh $T && cd $T && SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover -s tests -p 'test_*.py'`;
   - `sdd/reviews/UX_REVIEW_F9_FLUXO.md` (a interface é a saída do `sdd-fluxo.sh`, a parada do exit 40 e a seção "Encerramento" das skills);
   - `sdd/features/DESIGN_F9_FLUXO.md`, com o File Manifest.

   Pronto quando: `verify-gate.sh --print` 0, `python3 sdd/bin/design-lint.py` 0 e a revisão de contexto fresco do DESIGN aplicada.
3. **Build**, com commit antes do gate e todo arquivo novo no `MANIFEST.txt`, em ordem `LC_ALL=C`. Pronto quando:
   - `bash sdd/bin/verify-gate.sh --strict sdd/features/DEFINE_F9_FLUXO.md` 0 e `python3 sdd/bin/report-lint.py sdd/reports/BUILD_REPORT_F9_FLUXO.md` 0;
   - `bash sdd/bin/sdd-decisoes-lint.sh --sites .agents/skills` 0 e `--self-test` 0 (as 4 fixtures reprovadas pelo motivo certo);
   - `bash sdd/bin/sdd-fluxo.sh --self-test` 0, com um cenário por exit (0/10/20/30/40/64) e um que rejeita `| tee`;
   - com `flow.autonomous: true`, a `sdd-define` sobre `sdd/fixtures/BRAINSTORM_EXEMPLO.md` termina com `✅ DEFINE pronto → seguindo para …`; com `false` (default), nada muda nas 17 skills além da seção nova;
   - no Codex CLI (ou na fixture decidida no brainstorm), um despacho de papel fresco para em `40 AGUARDANDO_HUMANO` com o brief gravado em `sdd/reports/briefs/`;
   - todo script novo passa por `grep -nE 'mapfile|declare -A|\$\{[a-zA-Z_]+\^\^' <script>` sem achado (bash 3.2; `tests/test_bash32.py` cobre `sdd/bin/*.sh` e `sdd/hooks/`) e tem fixture e teste dos dois lados (regra 6 do 8.0);
   - `python3 sdd/bin/skill-lint.py --conversa .agents/skills/sdd-*/SKILL.md` 0 nas 17 skills;
   - houve 1 sabotagem por script alterado ou novo;
   - a revisão de contexto fresco terminou sem HIGH aberto.
4. **Release**:
   - PR com CI verde em `ubuntu-latest` **e** `macos-latest`;
   - bloco do OK da `sdd-release`;
   - OK do Roberto **citando "sdd-open" na mesma mensagem**. Sem isso, não faça o push;
   - push fast-forward em `main`.

   Pronto quando: `gh release view <tag> -R robertodiasduarte/sdd-open` mostra `SHA256SUMS.txt` e `shasum -a 256 -c` confere.
5. **Fechar**: rode a `sdd-handoff` com a etapa F9 no topo e o prompt da sessão 8 (F10 + F11 Revisão adversarial: plano, seção 8, "F10" e "F11"; a seção 10 permite o par F10+F11). Grave os artefatos na branch `docs/` **sem trocar de branch na worktree**:

   ```bash
   cd /Users/robertoduarte/rdd-worktrees/sdd-open-f9-fluxo
   T=$(mktemp -d) && GIT_TERMINAL_PROMPT=0 git fetch -q origin docs/incorporar-starter
   git worktree add -q --detach "$T" origin/docs/incorporar-starter   # do remoto: a branch local pode estar atrás
   for d in features handoffs reports reviews; do mkdir -p "$T/sdd/$d" && rsync -a --delete "sdd/$d/" "$T/sdd/$d/"; done
   git -C "$T" add sdd/features sdd/handoffs sdd/reports sdd/reviews && git -C "$T" commit -q -m "docs(incorporar-starter): sessão 7 — F9 Fluxo encadeado" && GIT_TERMINAL_PROMPT=0 git -C "$T" push -q origin HEAD:docs/incorporar-starter
   git worktree remove --force "$T"
   ```

## O que não quebrar

- **Hooks (F8):** `sdd/hooks/pre-commit` recusa com `RESULTADO: COMMIT RECUSADO` e um `→ [classe]` por conserto; a regra REPORT pula `sdd/fixtures/` e `sdd/templates/`; o `pre-push` nunca recusa; `tests/test_hooks.py` (23), `tests/test_claude_adapter.py` (11) e a classe `Hooks` de `tests/test_sdd_open.py` são o contrato. A `sdd-higiene-dado` resolve o arquivo antigo por `--git-common-dir`, nunca por `--git-path hooks/…`; os 28 testes de `TestDeteccao`, `TestInstalacao` e `TestGeradores` em `tests/test_alarme.py` (36) ficam byte a byte. Neste repositório o `init` não roda: `core.hooksPath` fica vazio e o CI é a verdade.
- **`report-lint.py`** (F7): fail-closed; `--stdin` e `--pendente`; exits 0/1/64; mensagens com `🛑 [classe]`, `RESULTADO:` e `→`.
- **`verify-gate.sh`**: os seis exits (0/2/3/4/5/64), as fixtures de `sdd/fixtures/` e a saída idêntica com e sem trace. O `sdd-fluxo.sh` **chama** o gate; não o reescreve.
- **`PERGUNTA_DECISAO.md`**: os itens 1–8 e o formato ⏸️ ficam; a classe entra no item 9 reservado. As fixtures de `sdd/fixtures/conversa/` que já reprovam no `skill-lint --conversa` continuam reprovando pelo mesmo motivo.
- **Camada de conversa** (F4 + F5): o bloco comum está em 15 `SKILL.md` e a seção nas 17; não mexa nele sem trocar nas 15 e nas `FRASES` do `tests/test_conversa.py`. "Por que cada regra existe" fica logo antes de `## Encerramento (obrigatório)` nas 7 skills de fase; a seção encadeada da F9 entra onde o brainstorm decidir, igual nas 9.
- **`init`/`sync`/`doctor`**: o `init` nunca sobrescreve skill instalada nem `sdd/bin/*` (completa o que falta); o `sync` regenera adaptadores e `.claude/hooks/*.py`; os merges de `.gemini/settings.json` e `.claude/settings.json` continuam; os testes de `tests/test_sdd_open.py` (31) ficam.
- **Docs testados** (`tests/test_docs.py`): todo link e âncora de `README*.md` e `docs/**` abre; o roadmap conta 6 linhas — se houver linha da F9, **remova-a** (EN e PT) ao entregar e atualize a contagem do teste junto.
- **Contratos de `sdd/`**: `playbook-lint.sh --self-test` sai 0; os lints mantêm 0/1/64; o bloco do OK da `sdd-release` mantém rótulos, ordem e uma pergunta só.
- **CI da M1**: nada de caractere invisível nem `curl … | sh` literal em `.agents/skills/`; piso Python 3.9 / bash 3.2 afirmado.
- **Padrão agnóstico (P2)**: `tests/test_agnostico.py` reprova `AskUserQuestion`, `TodoWrite`, `PreToolUse`, `PostToolUse`, `subagent_type`, `Task tool`, `Agent tool` e `/model` em `.agents/skills/**`, `sdd/templates/**`, `sdd/hooks/**`, `AGENTS.md.tmpl` e `sdd/playbook.md`. O `sdd-fluxo.sh` fala em "papel fresco" e "sessão nova", nunca no nome da ferramenta de um agente; o que é de um vendor só mora em `bin/adapters/<vendor>/` e no que o `init` gera.
- **Literais que o publish-gate reprova** (`scripts/publish-gate-patterns.txt`): e-mail só em `example.com/.org/.net`; CPF, CNPJ, telefone, sequências de 11+ dígitos e caminho `/Users/<nome>/` não podem aparecer em arquivo rastreado; o G1 (gitleaks) varre `tests/` — valores de teste gerados em execução.
- **Arquivos**: `python3 -B` e `git add` por nome (não há `.gitignore`); bash 3.2 (`${VAR}` antes de emoji; nada de `mapfile`, `declare -A`, `${x^^}`), nada de `rm -rf` com variável sem `"${X:?}"`; `sdd/features|handoffs|reports|reviews|traces/` **nunca** entram em commit da branch de trabalho; todo arquivo novo entra no `MANIFEST.txt`.
- **Push e remoto**: todo comando remoto com `GIT_TERMINAL_PROMPT=0`; push em `main` só com OK explícito do Roberto citando "sdd-open"; nunca `--force`; a branch `docs/incorporar-starter` nunca vira PR.
- **Fora de escopo nesta sessão:**
  - a revisão adversarial, o registry, os adapters por engine e o 2º revisor (F10/F11); `RESUMO_ETAPA.md` com `/adversarial-review` (F10); o `sdd-build` passo 0 chamando `sdd-fluxo.sh review-design` é R13 da F10 — a F9 entrega o verbo, a F10 liga a chamada;
  - cartógrafo, curator, `/drive` e `drive.*` (F12–F14);
  - regenerar o sdd-starter a partir do open (frente própria);
  - alterar o sdd-starter ou o repositório privado.

## Como fechar

Ao terminar, rode a skill **SDD Handoff by RDD** de novo para registrar o que foi feito
e preparar a próxima retomada.
