# Continuar: INCORPORAR_STARTER — sessão 8: F10 Revisão adversarial (+ F11 se sobrar folga)

Esta sessão começa numa **worktree nova**. Os artefatos SDD da família (features, handoffs, reports, reviews) vivem na branch `docs/incorporar-starter` do remoto, nunca mesclada em `main`.

## Preparar a worktree (antes de ler qualquer coisa)

A worktree da F10 **ainda não existe**. Crie-a de `origin/main` = `89ac76f` (tag `v2.2.10`) e traga os artefatos SDD, fora do commit:

```bash
cd /Users/robertoduarte/rdd-public/sdd-open
GIT_TERMINAL_PROMPT=0 git fetch -q origin
git worktree add /Users/robertoduarte/rdd-worktrees/sdd-open-f10-revisao -b feat/f10-revisao origin/main
cd /Users/robertoduarte/rdd-worktrees/sdd-open-f10-revisao
GIT_TERMINAL_PROMPT=0 git fetch -q origin tag v2.2.10                     # base do check-versions
GIT_TERMINAL_PROMPT=0 git fetch -q origin docs/incorporar-starter
git checkout origin/docs/incorporar-starter -- sdd/features sdd/handoffs sdd/reports sdd/reviews
git rm -r -q --cached sdd/features sdd/handoffs sdd/reports sdd/reviews   # ficam no disco, fora do commit
```

E confira:

```bash
git branch --show-current                                                 # esperado: feat/f10-revisao
git status --short | head -4                                              # esperado: só "?? sdd/…"
git log --oneline -1                                                      # esperado: 89ac76f ou mais novo
ls sdd/handoffs/HANDOFF_INCORPORAR_STARTER.md sdd/features/PLANO_F4_F15_CONSOLIDADO.md
command -v codex gemini claude                                            # nesta máquina, os 3 existem
```

Se `/Users/robertoduarte/rdd-public/sdd-open` não for o clone de `https://github.com/robertodiasduarte/sdd-open.git`, use a worktree da sessão 7 como base (`git -C /Users/robertoduarte/rdd-worktrees/sdd-open-f9-fluxo worktree add …`), se ela ainda existir. Não trabalhe na worktree antiga `sdd-open-f9-fluxo` (branch já mesclada). O `sdd/ambiente.md` do checkout principal é nota local da `sdd-new-session` do starter, não rastreada; não o commite.

Depois, leia nesta ordem:
- `sdd/features/PLANO_F4_F15_CONSOLIDADO.md`:
  - seção 0 (P1–P4; a F10 segue no **P4**);
  - seção 8: o preâmbulo comum, **8.0** (as 10 regras do PORTE, a tabela de degradação por vendor e a **correção medida na F9**: o Codex 0.163 abre subagente; a linha da revisão adversarial diz `codex exec`, `gemini -p` ou `openrouter:<slug>` como engines), os quadros **"F10 Revisão adversarial — núcleo"** e **"F11 … gate offline"**;
  - **8.1** "F10" e "F11" (R2–R12 com os exits 67/68, tetos 180 KB/8 MB, gatilhos do 2º revisor, `data_collection=deny`), **8.2** (slots `review.*` da F10, com unidades; candidatos a cair: `second_reviewer_*` como constantes) e **8.3** (fontes no privado);
  - seção 10 (F10 + F11 é o único par permitido; publicar a F10 antes de abrir a F11).
- `sdd/handoffs/HANDOFF_INCORPORAR_STARTER.md`: a Ficha, `## Eventos` e a etapa "F9 Fluxo encadeado", que é a do topo.
- `sdd/templates/fragments/FLUXO_ENCADEADO.md` (seção "Loop de revisão") e `sdd/bin/sdd-fluxo.sh loop` (cabeçalho `USO-INICIO`): é o **consumidor** do que a F10 produz — `META.txt` com `reviewer_exit`/`auditor_exit`, `reviewer.verdicts.jsonl` (`achado`, `severidade` HIGH/MED/LOW), `auditor.verdicts.jsonl` (`veredito` AGREE/DISAGREE_EVIDENCE/DISAGREE_CONCERN/NOVO), ledger por célula com `rodada=N`. A F10 acrescenta ao `loop` os campos do 2º revisor e do desempate como deltas (`revisor2_*`, `desempate_*`, raso, `auditor_exit 75`), com fixtures próprias.
- `.agents/skills/sdd-design/SKILL.md` (seção "Review adversarial do DESIGN", R12), `.agents/skills/sdd-build/SKILL.md` (passo 0, onde a R13 liga `sdd-fluxo.sh review-design`; 5c) e `.agents/skills/sdd-release/SKILL.md` (R1: review externo obrigatório), `sdd/templates/fragments/ADVISOR_CONSULT.md` e `RESUMO_ETAPA.md` (cita `/adversarial-review`, pendência da F10).
- `sdd/config.example.yaml`: já tem `review.vendors` e `review.security_globs` (F9).

## Onde paramos

- **F1–F9, W0 e M1 entregues; o P3 (starter) está concluído; o P4 está na F9.** A última Release é https://github.com/robertodiasduarte/sdd-open/releases/tag/v2.2.10:
  - tag em `89ac76f`, publicada por tag empurrada à mão (o push de `daf9c0f` não publicou: o job de testes do Ubuntu caiu no teto de 10 min; `89ac76f` sobe o teto para 25);
  - SHA-256 de `sdd-open-v2.2.10.tar.gz` `209e086bfd57f650da5f9b281732eaf9bb2ee350daf1978914c8a179aceb330a`, conferido.
- **`main` está em `89ac76f`.** É a F9: `sdd/bin/sdd-fluxo.sh` (`review-design`, `loop`, `despachar` com **exit 40 AGUARDANDO_HUMANO**, `seguir`, `estado`, `--self-test`), `sdd/bin/sdd-decisoes-lint.sh`, marcas `[D1 · não se desfaz]` … `[auto · de rotina]` no item 9 do `PERGUNTA_DECISAO.md`, `FLUXO_ENCADEADO.md`, subseção `### Fluxo encadeado` nas 9 skills de fase, slots `flow.autonomous: false` e `review.security_globs: ""`, seção Advisor Ledger no `DESIGN_TEMPLATE.md`, `docs/chained-flow.md` + PT.
- **Estado do pacote:** 17 skills; **744 testes** verdes no piso `SDD_TEST_BASH=/bin/bash /usr/bin/python3` (Python 3.9.6, bash 3.2.57), local e no `macos-latest` (≈ 12 min no Ubuntu, ≈ 15 no macOS); roadmap (`docs/roadmap.md` + PT) com 5 linhas; `MANIFEST.txt` 273 linhas.
- **Esta sessão faz a F10 inteira**, do brainstorm à release. A F11 só entra depois da Release da F10, se sobrar contexto.

## Contexto que você precisa ter

- **Remoto:** `https://github.com/robertodiasduarte/sdd-open.git`.
- **Release automática:** sai no push de `main` que toca `.agents/skills/**`, `bin/**`, `sdd/bin/**`, `sdd/hooks/**`, `sdd/templates/**`, `sdd/fixtures/**`, `sdd/playbook.md`, `sdd/config.example.yaml` ou `AGENTS.md.tmpl`. O patch vem de `scripts/next-version.sh` (dá `v2.2.11`); um push que só toca `.github/` **não** publica — uma tag `vX.Y.Z` empurrada à mão publica, com o `release.yml` do commit da tag. O job `release` espera `testes` (teto 25 min) **e** `testes-macos` (teto 20 min).
- **Escopo da F10** (plano, quadro F10 e 8.1), R1–R10, R12, R13:
  - `sdd/bin/adversarial-review.sh` + `sdd/bin/adapters/{claude,codex,gemini,openrouter}.sh` (um arquivo por engine, reescrito — o `adapters.sh` do privado tem 1.114 linhas e 87 refs RDD) + `sdd/review/{registry.tsv,precos.tsv,prompts/}`;
  - R2 vereditos do auditor e **exit 68** sem veredito; R3 diff congelado por merge-base com sha256, inclui untracked, para em > 8 MB; R4 contexto SDD injetado, teto 180 KB; R5 exclusão de papéis com **exit 67**; R6 2º revisor condicional (segurança, ≥ 8 arquivos, ≥ 120 KB, ≥ 2 camadas, revisor raso < 30 s) e desempate; R7 classificação de falha (AUTH sem fallback, 429 tenta de novo); R8 convergência honesta; R9 privacidade (`data_collection=deny`, recusa gravar em pasta não ignorada); R10 custo por papel (`precos.tsv`, slug ausente = `$?`); R12 revisor → auditor em cadeia, nunca em paralelo, no `sdd-design`; R1 review externo obrigatório no `sdd-release`; **R13** `sdd-build` passo 0 chama `sdd-fluxo.sh review-design` (a F9 entregou o verbo);
  - **F11** (R11): `sdd/bin/adversarial-review-gate.sh` + `sdd/review/stubs/` por engine + `sdd/bin/eval-agree.sh` — asserts sobre veredito, proveniência e custo extraídos, não só exit.
- **Fontes no privado** (só leitura; o repositório privado **não** se altera). Leia do `origin/main` do privado (`git -C /Users/robertoduarte/RDD/Wordpress show origin/main:<arquivo>`; `origin/main` = `1b1c1d41b` em 2026-10-31): `scripts/adversarial-review.sh` (991 linhas), `scripts/adversarial-review/adapters.sh` (1.114), `scripts/adversarial-review/{registry.tsv,precos.tsv,prompts/,stubs/,consumir-auditor-sessao.sh,eval-agree.sh}` (eval-agree 207), `scripts/adversarial-review-gate.sh` (695). Exemplos reais do formato de saída: `.claude/sdd/archive/DOGFOOD_20260824/` (META.txt, reviewer.verdicts.jsonl) e 69 `ledger-review.md` em `.claude/sdd/reports/evidence/*/`. Específico da RDD não viaja (regra 4 do 8.0); cadeias fixas (`adapters.sh` l. 28–58) saem.
- **Decisões a levar ao brainstorm** (formato `PERGUNTA_DECISAO.md`, recomendada primeiro, com a marca da classe, "não sei", nunca "Outro"):
  - **D2**: engines de exemplo no `registry.tsv` (recomendado: `claude`, `codex` com `-s read-only`, `gemini`, `openrouter:<slug>`, sem cadeia default);
  - **D11**: os slots `review.*` (lista do 8.2, com unidades); quais caem para constantes (candidatos: `second_reviewer_*`, `shallow_review_secs`);
  - como provar "review real `claude` + `openrouter:<modelo>`" do critério de pronto: **não há chave do OpenRouter no ambiente desta máquina** — pergunte ao Roberto se ele fornece uma (variável de ambiente, nunca em arquivo) ou se a prova real usa `claude` + `codex` (ou `gemini`), os 3 instalados aqui, com o OpenRouter só nos stubs; não decida sozinho;
  - **R1** (review externo obrigatório na `sdd-release`): muda o comportamento de toda release — obrigatório sempre, ou só quando o `review-design`/camadas exigem;
  - F10 sozinha ou F10 + F11 nesta sessão (regra do par: publicar a primeira antes de abrir a segunda);
  - versão da Release (`v2.2.11` automática ou `v2.3.0` por tag).
- **Decisões já tomadas, não reabrir:**
  - a camada de conversa fica sempre ligada; `flow.autonomous` liga o encadeamento, não a conversa;
  - toda pergunta tem a marca `[<código> · <rótulo>]`, a recomendada primeiro, "não sei" e nunca "Outro"; o OK da `sdd-release` fica sem marca;
  - vendor sem subagente (ou com ele indisponível) degrada para `sdd-fluxo.sh despachar` → exit 40 e a parada ⏸️; o exit 40 não é por vendor;
  - o open é a fonte canônica de governança, auditoria-harness e prompt-builder; a KB fica em `sdd/kb/`; os artefatos SDD ficam na branch `docs/`;
  - `report-lint` fail-closed; hooks pelo `init` com confirmação; `review.security_globs` já existe (F9).
- **Skills do fluxo** (em `/Users/robertoduarte/.claude/skills/`): `sdd-brainstorm`, `sdd-define`, `sdd-design`, `sdd-build`, `sdd-handoff`. A `sdd-release` e a UX review são as do pacote.
  - Fluxo SDD completo, com revisão de contexto fresco do DESIGN antes do build e do build depois (modo `veredito`, numa worktree destacada; remova-a no fim). A `sdd-build` limita a 2 ciclos; um 3º é pergunta `[D4 · limite de tentativas]` ao Roberto.
  - **Antes de despachar cada avaliador**, rode `bash sdd/bin/avaliador-guard.sh --permitir sdd/features/ --permitir sdd/handoffs/ --permitir sdd/reports/ --permitir sdd/reviews/` (nunca `--permitir sdd/`) e grave o log. No brief, peça que as sondas sigam a receita do `EVIDENCIA.md` (`out=$(cmd 2>&1); rc=$?` antes do pipe): na F9 a pasta inteira de evidência passou no `gate-shell-evidencia.sh`.
  - Moldes da evidência: `sdd/reports/evidence/F9_FLUXO/` (`gerar-evidencia.sh`, `sabotagem.sh`, `codex.sh`). O Bash da sessão é zsh (sem `PIPESTATUS`): grave os logs com `/bin/bash -c` e terminando em `[exit=$rc]`; sem formatador no último estágio da linha `$`. Confira com `bash sdd/bin/gate-shell-evidencia.sh sdd/reports/evidence/F10_REVISAO`.
  - **Codex CLI como engine ou avaliador:** o 0.163 tem `multi_agent` estável e abre colaborador mesmo com `--disable multi_agent`; `codex exec` precisa de repositório git (commite a cópia temporária) e `~/.codex/skills/` desta máquina tem cópias velhas das skills SDD — isole com `CODEX_HOME` temporário só com o `auth.json` e `--ignore-user-config`.
  - O `report-lint` exige `evidence/<FEATURE>/` com o mesmo nome do `BUILD_REPORT_<FEATURE>.md`, a tabela reconhecida e a linha do avaliador (ou o `AVALIACAO_<FEATURE>_<AAAAMMDD>…md` em `sdd/reviews/`). O DESIGN passa no `python3 sdd/bin/design-lint.py` e no `scripts/validate_design.py` da skill de design (chaves `{…}` reprovam até dentro de código: use `"$X"`; título `## X` citado no meio do texto e 2º "Next Step" também).
  - Rede: a sessão 7 perdeu o avaliador 2 vezes por `ENOTFOUND`; retome o mesmo agente com o contexto em vez de despachar outro.
- **Versões atuais:**
  - auditoria-harness 1.1.1, brainstorm 2.2.0, build 2.4.0, checar-ambiente 1.4.1, define 2.4.0, design 2.2.0, governanca 2.3.0, handoff 2.1.1;
  - iterate 2.2.0, kb 2.2.1, new-session 1.3.0, playbook 2.1.1, prompt-builder 2.1.1, release 2.5.0, ux-review 2.4.0;
  - (portadas, sem a camada F4) higiene-dado 1.2.0, iniciar-repo 1.1.1.

  Toda skill tocada sobe de versão e atualiza a linha de identificação; os pinos de versão em `tests/test_contrato_build_release.py`, `test_correcoes_w0.py` e `test_matriz_new_session.py` mudam junto. Confira com `python3 scripts/check-versions.py --base v2.2.10 --base-obrigatoria`.

## Tarefas, em ordem

1. **Brainstorm da F10** com a `sdd-brainstorm`, gravando `sdd/features/BRAINSTORM_F10_REVISAO.md` a partir dos quadros F10/F11 e do 8.1. Pronto quando: D2, D11, a prova real (chave do OpenRouter ou `claude` + `codex`), a R1 e a versão foram respondidas pelo Roberto, a abordagem foi confirmada e os cortes YAGNI e os 2 checkpoints estão registrados.
2. **Define, UX review e design**:
   - `sdd/features/DEFINE_F10_REVISAO.md`, com ATs em EARS e o `verify_gate` `kind: test` de sempre: `cmd` = `T=$(mktemp -d) && git archive HEAD | tar -x -C $T && PUBLISH_GATE_MODE=ci bash scripts/publish-gate.sh $T && cd $T && SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover -s tests -p 'test_*.py'`;
   - `sdd/reviews/UX_REVIEW_F10_REVISAO.md` (a interface é a saída do `adversarial-review.sh`, o relatório da revisão e o que a `sdd-release` mostra);
   - `sdd/features/DESIGN_F10_REVISAO.md`, com o File Manifest e o Advisor Ledger.

   Pronto quando: `verify-gate.sh --print` 0, os 2 lints do DESIGN 0 e a revisão de contexto fresco do DESIGN aplicada.
3. **Build**, com commit antes do gate e todo arquivo novo no `MANIFEST.txt` (`LC_ALL=C`). Pronto quando:
   - `bash sdd/bin/verify-gate.sh --strict sdd/features/DEFINE_F10_REVISAO.md` 0 e `python3 sdd/bin/report-lint.py sdd/reports/BUILD_REPORT_F10_REVISAO.md` 0;
   - `review.auditor == review.revisor1` → exit 67; auditor sem veredito → exit 68; 1 engine só → ledger com `diversidade: nenhuma`; `sdd-release` sem `review_externo` no ledger aborta;
   - review real (as 2 engines decididas no brainstorm) produz relatório com tokens, custo ≠ 0 (ou `$?` declarado) e sha256 do diff, e o `sdd-fluxo.sh loop` lê a saída dela;
   - todo script novo passa por `grep -nE 'mapfile|declare -A|\$\{[a-zA-Z_]+\^\^' <script>` sem achado, tem fixture e teste dos dois lados (regra 6 do 8.0) e 1 sabotagem;
   - `python3 sdd/bin/skill-lint.py --conversa .agents/skills/sdd-*/SKILL.md` 0 nas 17 skills e `bash sdd/bin/sdd-decisoes-lint.sh --sites .agents/skills sdd/templates/fragments` 0;
   - a revisão de contexto fresco terminou sem HIGH aberto.
4. **Release**:
   - PR com CI verde em `ubuntu-latest` **e** `macos-latest`;
   - bloco do OK da `sdd-release`;
   - OK do Roberto **citando "sdd-open" na mesma mensagem**. Sem isso, não faça o push;
   - push fast-forward em `main`.

   Pronto quando: `gh release view <tag> -R robertodiasduarte/sdd-open` mostra `SHA256SUMS.txt` e `shasum -a 256 -c` confere. Se o run `release` não publicar, leia os jobs antes de qualquer outra coisa (na F9 foi o teto de tempo).
5. **Fechar**: rode a `sdd-handoff` com a etapa F10 no topo e o prompt da sessão seguinte (F11, se não coube aqui; senão F12 Contexto e governança). Grave os artefatos na branch `docs/` **sem trocar de branch na worktree**:

   ```bash
   cd /Users/robertoduarte/rdd-worktrees/sdd-open-f10-revisao
   T=$(mktemp -d) && GIT_TERMINAL_PROMPT=0 git fetch -q origin docs/incorporar-starter
   git worktree add -q --detach "$T" origin/docs/incorporar-starter   # do remoto: a branch local pode estar atrás
   for d in features handoffs reports reviews; do mkdir -p "$T/sdd/$d" && rsync -a --delete "sdd/$d/" "$T/sdd/$d/"; done
   git -C "$T" add sdd/features sdd/handoffs sdd/reports sdd/reviews && git -C "$T" commit -q -m "docs(incorporar-starter): sessão 8 — F10 Revisão adversarial" && GIT_TERMINAL_PROMPT=0 git -C "$T" push -q origin HEAD:docs/incorporar-starter
   git worktree remove --force "$T"
   ```

## O que não quebrar

- **Fluxo encadeado (F9):** os exits do `sdd-fluxo.sh` e o `--self-test` são contrato (`tests/test_fluxo.py`, 48); o `loop` ganha campos por delta e os 3 casos de borda (review inválida sem jsonl, NEEDS_WORK no teto, HIGH com recibo pendente) continuam saindo 10; o `--log` é regravado em toda saída; nomes do `despachar` por lista explícita, nunca faixa `[A-Za-z]` (no bash 3.2 com UTF-8 ela aceita acento).
- **Marcas e lint de decisões:** a tabela do item 9 do `PERGUNTA_DECISAO.md` é a dona dos rótulos; toda pergunta nova de decisão leva marca; `sdd-decisoes-lint.sh --sites` acha 15 nas skills e 2 nos fragmentos — uma pergunta nova muda essa contagem em `tests/test_decisoes_lint.py`.
- **Subseção `### Fluxo encadeado`:** bloco comum idêntico nas 9 skills de fase, dentro do `## Encerramento (obrigatório)`; "Por que cada regra existe" logo antes do Encerramento.
- **Hooks (F8):** `sdd/hooks/pre-commit` recusa com `RESULTADO: COMMIT RECUSADO`; a regra REPORT pula `sdd/fixtures/` e `sdd/templates/`; o `pre-push` nunca recusa; `tests/test_hooks.py`, `test_claude_adapter.py` e `test_alarme.py` são contrato.
- **`report-lint.py`** fail-closed (exits 0/1/64); **`verify-gate.sh`** com os seis exits (0/2/3/4/5/64), `--print`, `--trace` e as fixtures de `sdd/fixtures/`.
- **Camada de conversa** (F4 + F5): bloco comum em 15 `SKILL.md`, seção nas 17, `FRASES` do `tests/test_conversa.py`.
- **`init`/`sync`/`doctor`:** o `init` nunca sobrescreve skill instalada nem `sdd/bin/*` (completa o que falta) e copia `sdd/fixtures/` só na 1ª instalação; `tests/test_sdd_open.py` fica.
- **Docs testados** (`tests/test_docs.py`): todo link de `README*.md` e `docs/**` abre; o roadmap conta 5 linhas — a linha "Adversarial review" sai quando a F10+F11 entregar o tema (EN e PT), e a contagem do teste muda junto.
- **Contratos de `sdd/`:** `playbook-lint.sh --self-test` 0; o bloco do OK da `sdd-release` mantém rótulos, ordem e uma pergunta só (`tests/test_contrato_build_release.py`).
- **CI:** nada de caractere invisível nem `curl … | sh` literal em `.agents/skills/`; piso Python 3.9 / bash 3.2; `release.yml` com teto 25 no `testes` e 20 no `testes-macos` — confira se a suíte maior ainda cabe.
- **Padrão agnóstico (P2):** `tests/test_agnostico.py` reprova `AskUserQuestion`, `TodoWrite`, `PreToolUse`, `PostToolUse`, `subagent_type`, `Task tool`, `Agent tool` e `/model` em `.agents/skills/**`, `sdd/templates/**`, `sdd/hooks/**`, `AGENTS.md.tmpl` e `sdd/playbook.md`. Os nomes de engine (`claude`, `codex`, `gemini`, `openrouter`) são dado do `registry.tsv` e dos adapters em `sdd/bin/adapters/`, não texto de skill.
- **Literais que o publish-gate reprova** (`scripts/publish-gate-patterns.txt`): e-mail só em `example.*`; CPF, CNPJ, telefone, 11+ dígitos e caminho `/Users/<nome>/` fora de arquivo rastreado; o G1 (gitleaks) varre `tests/` e `sdd/review/stubs/` — chave de API nunca em arquivo, nem em stub (valor gerado em execução ou obviamente falso de baixa entropia).
- **Arquivos:** `python3 -B` e `git add` por nome; bash 3.2; `rm -rf` só com `"${X:?}"`; `sdd/features|handoffs|reports|reviews|traces/` **nunca** entram em commit da branch de trabalho; todo arquivo novo no `MANIFEST.txt`.
- **Push e remoto:** todo comando remoto com `GIT_TERMINAL_PROMPT=0`; push em `main` só com OK explícito do Roberto citando "sdd-open"; nunca `--force`; a branch `docs/incorporar-starter` nunca vira PR.
- **Fora de escopo nesta sessão:** cartógrafo, curator, `/drive` e `drive.*` (F12–F14); regenerar o sdd-starter; alterar o sdd-starter ou o repositório privado.

## Como fechar

Ao terminar, rode a skill **SDD Handoff by RDD** de novo para registrar o que foi feito
e preparar a próxima retomada.
