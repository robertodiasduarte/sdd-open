# Continuar: INCORPORAR_STARTER — sessão 13: correções da v2.7.0 e brainstorm da F15 Substituição do SDD privado

Esta sessão roda **dentro da worktree** `/Users/robertoduarte/rdd-worktrees/sdd-open-f14-drive`, branch `feat/f14-drive`, em `b3526ae` (um commit à frente de `origin/main` = `b0663d3` = tag `v2.7.0`). Os artefatos SDD da família (features, handoffs, reports, reviews) já estão no disco, fora do commit; a fonte deles é a branch `docs/incorporar-starter` do remoto, nunca mesclada em `main`.

## Conferir a worktree (antes de ler qualquer coisa)

A worktree **já existe**: não rode `git worktree add`. Confira que está tudo no lugar:

```bash
git rev-parse --show-toplevel                 # esperado: /Users/robertoduarte/rdd-worktrees/sdd-open-f14-drive
git branch --show-current                     # esperado: feat/f14-drive
git log --oneline -1                          # esperado: b3526ae chore(playbook): curadoria F14_DRIVE — 7 delta(s)
git rev-parse -q --verify 'v2.7.0^{commit}'   # base do check-versions; esperado: b0663d32b65421ea706a78ef8c9c8d1819e26f59
GIT_TERMINAL_PROMPT=0 git fetch -q origin
git rev-parse --short origin/main             # esperado: b0663d3; se for outro, alguém publicou: leia antes de seguir
git status --short | head -6                  # esperado: só "?? sdd/…"
ls sdd/handoffs/HANDOFF_INCORPORAR_STARTER.md sdd/features/PLANO_F4_F15_CONSOLIDADO.md sdd/reports/evidence/F14_DRIVE/rodada5-reviewer.md
```

Se a sessão abriu em outra pasta, pare e peça ao Roberto para abrir o agente na pasta da worktree: nenhum `cd` muda a pasta à qual a sessão fica presa. Se a worktree não existir, recrie a partir do clone principal e reabra a sessão nela:

```bash
cd /Users/robertoduarte/rdd-public/sdd-open
GIT_TERMINAL_PROMPT=0 git fetch -q origin
git worktree add /Users/robertoduarte/rdd-worktrees/sdd-open-f14-drive feat/f14-drive   # a branch local guarda o b3526ae
cd /Users/robertoduarte/rdd-worktrees/sdd-open-f14-drive
GIT_TERMINAL_PROMPT=0 git fetch -q origin tag v2.7.0                                    # base do check-versions
GIT_TERMINAL_PROMPT=0 git fetch -q origin docs/incorporar-starter
git checkout origin/docs/incorporar-starter -- sdd/features sdd/handoffs sdd/reports sdd/reviews
git rm -r -q --cached sdd/features sdd/handoffs sdd/reports sdd/reviews                 # ficam no disco, fora do commit
```

**Não apague a branch local `feat/f14-drive` antes de levar o `b3526ae`:** ele só existe nela. A branch local `feat/f14-playbook` já foi levada (`252d351` virou `aabc4a3`); apagá-la é decisão do Roberto. As pastas `EXTERNAL_REVIEW_*` da F14 Drive estão em `/Users/robertoduarte/rdd-worktrees/arquivo-sdd-open/F14_DRIVE-revisoes-traces.tar.gz`, só nesta máquina, e também no disco da worktree. O `sdd/ambiente.md` do checkout principal é nota local da `sdd-new-session` do starter, não rastreada; não o commite.

Depois, leia nesta ordem:
- `sdd/handoffs/HANDOFF_INCORPORAR_STARTER.md`: a Ficha, `## Eventos` e a etapa "F14 Drive", que é a do topo.
- `sdd/reports/evidence/F14_DRIVE/rodada5-reviewer.md` e `rodada5-reviewer2.md`: os 5 achados (ao lado, `rodada5-auditor.md`).
- `sdd/features/PLANO_F4_F15_CONSOLIDADO.md`: seção 0 (P1–P4), **8.0** (as 10 regras do PORTE), o quadro **"F15 Substituição do SDD privado"** e a seção 10.
- `/Users/robertoduarte/RDD/Wordpress/.claude/sdd/reports/PORTE_SDD_PRIVADO_PARA_OPEN_2026-10-29.md`: **Anexo A** (os 26 scripts), **Anexo C** e D7, antes do brainstorm da F15. Tem fatos velhos: confira no `origin/main` do privado.

## Onde paramos

- **F1–F14, W0 e M1 estão publicados; o P3 (starter) está concluído; no P4 falta só a F15.** A última Release é https://github.com/robertodiasduarte/sdd-open/releases/tag/v2.7.0: tag em `b0663d3`, runs `release` 42216757169 (main) e 42216757289 (tag), `SHA256SUMS.txt` conferido (`a3864d39c8e95f9f9999ab9f24df854ad4c547d3f8a7e65171c6415a1db2419c`).
- **Estado do pacote:** 19 skills; **1.656 testes** verdes no piso `SDD_TEST_BASH=/bin/bash /usr/bin/python3` (Python 3.9.6, bash 3.2.57), local e no CI (no PR #18, Ubuntu 20m35s de 25, macOS 35m38s de 45); `MANIFEST.txt` 452 linhas.
- **A `v2.7.0` saiu com riscos aceitos pelo Roberto (D4 de 2026-11-06):** 5 achados da rodada 5, incluído 1 HIGH de concorrência; `loop` BLOQUEADO no teto; nenhum avaliador depois de `68d2341`. **Curadoria não enviada:** o commit `b3526ae` (5 contagens e as lições LM-007 e LM-008). A F15 instala o Open no privado: ele deve receber a versão com esses consertos, por isso a tarefa 1 vem antes.
- **Saldo da OpenRouter:** cerca de US$ 9,90 depois da rodada 5. Confira com `GET https://openrouter.ai/api/v1/credits`: o `limit_remaining` da chave é o limite dela, **não o saldo** (LM-008). **A conta do Codex tem crédito**, com `gpt-6.1-sol`; confira com o stdin fechado (`codex exec -s read-only --skip-git-repo-check "responda só: ok" < /dev/null`, em pasta temporária). Sem stdin fechado, o `rc=0` engana.

## Contexto que você precisa ter

- **Remoto:** `https://github.com/robertodiasduarte/sdd-open.git`.
- **Release automática:** sai no push de `main` que toca `.agents/skills/**`, `bin/**`, `sdd/bin/**`, `sdd/hooks/**`, `sdd/templates/**`, `sdd/fixtures/**`, `sdd/review/**`, `sdd/patterns/**`, `sdd/WORKFLOW_CONTRACTS.yaml`, `sdd/playbook.md`, `sdd/config.example.yaml` ou `AGENTS.md.tmpl`. O patch vem de `scripts/next-version.sh` (dá `v2.7.1`). O job `release` espera `testes` (teto 25 min) **e** `testes-macos` (teto 45 min).
- **Os 5 achados da rodada 5** (tarefa 1):
  - R1@codex HIGH, `sdd/bin/sdd-drive.sh:330`: a trava de estado vence aos 60 s com o dono vivo, e outro processo a toma. Nasceu no conserto da rodada 4 (`b0663d3`). Conserto: pid na trava e checar se está vivo;
  - R1@claude MED, `.agents/skills/sdd-release/SKILL.md:231`: "`--teto 300` e repita enquanto sair 4" não tem teto total; o texto antigo dizia ~2 min sem run;
  - R2@claude LOW, `sdd/bin/deploy-do-sha.sh:130`: 401 no disparo sai 3 sem `desmarcar()`;
  - R3@claude LOW, `sdd/bin/sdd-drive.sh:333`: `except OSError: continue` sem sleep nem limite, laço de CPU;
  - R4@claude LOW, `sdd/bin/sdd-archive.py:258`: documento recente em "sem classificação".
- **Teste que falta:** ficha aberta de slice sem documento com o nome do slice (a sabotagem viva "archive: slice não protege", em `sdd/reports/evidence/F14_DRIVE/sabotagens.sh`).
- **Quadro da F15** (plano, seção 8):
  - **Objetivo:** o repositório privado (`~/RDD/Wordpress`) passa a usar o Open instalado pelo `init`, e o SDD privado deixa de existir como código próprio.
  - **Entrega:** (1) `bash bin/sdd-open.sh init --vendors claude` no privado, com `sdd/config.yaml` preenchido: `test_cmd` (deno), `deploy.cmd` (rsync Hostinger), `drift_check_cmd`, `landmines_cmd`, `layers` (edge/sql/wp-content), `review.*`, `release.landmines_cmd` (inclui o gate de schema por migration); (2) o que é da RDD vai para onde o Open prevê: landmines LM-nnn → `sdd/playbook.md` do privado; KBs → `sdd/kb/`; patterns → `sdd/patterns/`; invariantes → `sdd/invariants.md`; buckets WARM/COOL e lentes por público → `sdd/contexto/` ou slot de UX a decidir; (3) remoção: `.claude/commands/workflow/*`, `.claude/agents/*` do SDD, `scripts/` do SDD (os 26 do Anexo A), `.githooks/`, `sdd-public/`, `port-to-public.sh`, `sdd-public-allowlist.tsv`, `gate-sdd-open-s1.sh`, `gate-sdd-prompt-builder.sh`; (4) `CLAUDE.md` do privado aponta para o `AGENTS.md` gerado; (5) as cópias `~/.claude/skills/sdd-*` e `anthropic-skills:sdd-*` regeneradas do Open (D6).
  - **Atenção:** o smoke visual (U3) ficou fora do Open; a `sdd-release` precisa de um ponto de extensão para o privado continuar chamando `scripts/a11y/` (passos 6b, 7b e 10b do `/release` de hoje). Quem chama o `contraste.sh` no privado precisa tratar a saída 2 do REPROVA. Específico da RDD não viaja para o Open: o privado passa a ser um **usuário** do Open. O caminho inverso §11 do PORTE deixa de existir.
  - **Esforço:** não estimado; estime no brainstorm.
  - **Pronto quando:** no privado, `doctor` ✅ sem ⚠️; uma feature real do RDD percorre brainstorm → define → design → build → release pelo Open, com Verify Gate, report-lint, review adversarial e deploy verificado pelo SHA; `git ls-files .claude/commands/workflow .claude/agents scripts/sdd-fluxo.sh sdd-public` vazio; `publish-gate.sh` do Open continua verde.
- **O privado, medido em `origin/main` = `68c630d3f` (2026-11-06; refaça depois de um `fetch`):** `.claude/commands/workflow` 8 arquivos; `.claude/agents` 13; `sdd-public` 80; `scripts/` 241 entradas no 1º nível; `.claude/kb/` 51 pastas (o plano diz 46); `.githooks/` com `pre-commit`, `pre-push` e 3 ganchos do Claude; os gates estão em `scripts/gates/` (`audita-schema-gate.sh`, `gate-sdd-open-s1.sh`, `gate-sdd-prompt-builder.sh`), e `scripts/port-to-public.sh`, `scripts/sdd-public-allowlist.tsv`, `scripts/lint-data-api-grants.py` existem. `git worktree list` tem 34 linhas: **há muitas frentes abertas no SDD privado**. Leia sempre do `origin/main` (`git -C /Users/robertoduarte/RDD/Wordpress show 'origin/main:<arquivo>'`; o checkout local fica atrás; ponha o caminho entre aspas, porque no zsh `$R:s…` é um modificador).
- **Decisões a levar ao brainstorm da F15** (formato `PERGUNTA_DECISAO.md`, recomendada primeiro, com a marca da classe, "não sei", nunca "Outro"). O Roberto pediu: **explicação para leigo, prós e contras, recomendação, e a decisão é dele**. Limites do método (rodadas, ciclos, teto) são pergunta D4 a ele, nunca decisão do agente:
  - migração de uma vez ou por fase (o plano sugere o `/define` do Open primeiro e o `/release` por último, porque o deploy é o passo de maior risco);
  - o que acontece com as frentes abertas no privado durante a migração;
  - o que do Anexo C vira slot, KB ou some (`model:` por fase, `/fewer-permission-prompts`, memória do Roberto);
  - destino do espelho travado e dos 4 arquivos (D7);
  - buckets WARM/COOL e lentes por público: `sdd/contexto/` ou slot de UX;
  - forma do ponto de extensão do smoke visual;
  - qual feature real faz a prova de ponta a ponta;
  - onde moram os artefatos SDD da F15: na branch `docs/incorporar-starter` ou no privado.
- **Decisões já tomadas, não reabrir:**
  - a camada de conversa fica sempre ligada; `flow.autonomous` liga o encadeamento, não a conversa;
  - toda pergunta tem a marca `[<código> · <rótulo>]`, a recomendada primeiro, "não sei" e nunca "Outro"; o OK da `sdd-release` fica sem marca;
  - vendor sem subagente degrada para `sdd-fluxo.sh despachar` → exit 40 e a parada ⏸️; o exit 40 não é por vendor;
  - o open é a fonte canônica de governança, auditoria-harness e prompt-builder; a KB fica em `sdd/kb/`; os artefatos SDD ficam na branch `docs/`;
  - `report-lint` fail-closed; hooks pelo `init` com confirmação; review externo obrigatório na release (R1, F10); governança em todo Define (D5, F12);
  - `drive.max_rounds` default 3; `drive.max_tokens` caiu; o drive para antes do release e nunca publica.
- **Skills do fluxo** (em `/Users/robertoduarte/.claude/skills/`): `sdd-brainstorm`, `sdd-define`, `sdd-design`, `sdd-build`, `sdd-handoff`. A `sdd-release` e a UX review são as do pacote.
  - **No brief de cada avaliador**, mande gravar só `sdd/reports/evidence/<FEATURE>/AVAL*-*.log` com o helper `ev.sh` (molde: `sdd/reports/evidence/F14_DRIVE/ev.sh`: grava `$ cmd`, saída e `[exit=N]` real) e **proíba** terminar o comando passado a ele num formatador (`tail`, `head`, `tr`, `grep`, `wc`, `sed`). Peça também que nada seja gravado na pasta temporária do sistema fora de um `mktemp -d`, e que não rode `python3 -m py_compile` no projeto (grava `__pycache__` em `sdd/bin/`; use `ast.parse`). Um 3º ciclo é pergunta `[D4 · limite de tentativas]` ao Roberto, mesmo sem HIGH aberto.
  - O Bash da sessão é zsh: sem `PIPESTATUS`, lista numa variável não se divide em palavras, `=====` num `echo` quebra o comando e `!` num `grep` entre aspas duplas quebra a cadeia `&&`, cortando o resto em silêncio. Grave os logs com `/bin/bash -c` terminando em `[exit=$rc]`. Confira com `bash sdd/bin/gate-shell-evidencia.sh sdd/reports/evidence/<FEATURE>`.
  - **Não edite `sdd/bin/verify-gate.sh` enquanto o gate roda** (o bash lê o script aos pedaços e dá erro de sintaxe falso). O mesmo vale para qualquer script em execução. Heredoc com o mesmo delimitador de um heredoc aninhado quebra o comando inteiro. Sabotagens rodam em paralelo (4) e presas a um SHA; pare processos pelo pid, nunca por `pkill -f` de padrão de comando (atinge outra sessão).
  - O `report-lint` exige `evidence/<FEATURE>/` com o mesmo nome do `BUILD_REPORT_<FEATURE>.md`, a tabela reconhecida e a linha do avaliador.
- **Revisão adversarial real (R1 da release):** `bash sdd/bin/adversarial-review.sh --reviewer claude --auditor openrouter:qwen/qwen3.7-plus --feature <F> --revisor2 <engine>`, `sdd-fluxo.sh loop … --rodada N` (teto 3) e `--conferir` na versão final; molde: `sdd/reports/evidence/F14_DRIVE/real-rodada.sh <N>` (com `TETO=` e `REVISOR2=`; a rodada 5 usou o Codex). O ledger precisa existir antes do `loop` e usa `APLICADA`, `REBATIDA_EVIDENCIA` ou `REBATIDA_ESCOPO`. A chave da OpenRouter está em `~/.config/rdd-eval.env` (`OPENROUTER_API_KEY`): carregue só no ambiente do processo, nunca grave. A rodada 5 custou US$ 5,02, e a parte paga na OpenRouter é pequena perto do total, mas confira o saldo antes. **Qualquer mudança no código depois da revisão invalida o `--conferir`**, até teste novo; os documentos das pastas SDD ficam fora do diff. Antes, rode o gate offline: `bash sdd/bin/adversarial-review-gate.sh`. O HIGH da rodada 5 nasceu de um conserto da rodada 4: conserto de concorrência pede teste de ataque **dos 2 lados**. Achado de modelo barato pede medição (`sdd/reports/evidence/F14_DRIVE/r1-repro.log`).
- **Prova num agente real:** se a frente mudar o texto de um passo que outro agente segue, rode a prova **depois** do último conserto. Molde: `sdd/reports/evidence/F14_DRIVE/codex-drive.sh`, com `PREFIXO=` novo a cada vez; sem `OR_MODELO`, usa a conta do Codex. O git do projeto de prova fica fora da sandbox (`--separate-git-dir` + `--add-dir`), para o commit do agente valer. Critério: efeito no disco, nunca texto.
- **Versões atuais:**
  - auditoria-harness 1.1.1, brainstorm 2.2.0, build 2.6.0, checar-ambiente 1.4.1, define 2.5.1, design 2.5.0, drive 1.0.0, governanca 2.4.0, handoff 2.1.2;
  - iterate 2.2.1, kb 2.2.1, loop-builder 1.0.0, new-session 1.4.1, playbook 2.2.0, prompt-builder 2.1.2, release 2.8.0, ux-review 2.5.0;
  - (portadas, sem a camada F4) higiene-dado 1.2.0, iniciar-repo 1.1.1.

  Toda skill tocada sobe de versão e atualiza a linha de identificação; os pinos de versão em `tests/test_contrato_build_release.py`, `test_correcoes_w0.py` e `test_matriz_new_session.py` mudam junto. Confira com `python3 scripts/check-versions.py --base v2.7.0 --base-obrigatoria`.

## Tarefas, em ordem

1. **Levar a curadoria e consertar os 5 achados, publicando a `v2.7.1`**, nesta worktree. O `b3526ae` já está na branch; ele sobe junto.
   - conserte R1@codex, R1@claude, R2@claude, R3@claude e R4@claude e escreva o teste que falta, cada um com teste dos 2 lados; a `sdd-release` sobe para 2.8.1;
   - **pergunte ao Roberto** se a revisão real roda sobre esse diff (recomendação: sim, 1 rodada, porque o conserto toca concorrência; confira o saldo antes) ou se vai a dispensa D3 com motivo, que a release aceita;
   - PR com CI verde em `ubuntu-latest` **e** `macos-latest`; bloco do OK da `sdd-release`; OK do Roberto **citando "sdd-open" na mesma mensagem**. Sem isso, não faça o push; push fast-forward: `git push origin HEAD:refs/heads/main`.

   Pronto quando: `bash sdd/bin/verify-gate.sh --strict sdd/features/DEFINE_F14_DRIVE.md` 0; a sabotagem "archive: slice não protege" cai; `gh release view v2.7.1 -R robertodiasduarte/sdd-open` mostra `SHA256SUMS.txt` e `shasum -a 256 -c` confere.
2. **Brainstorm da F15** com a `sdd-brainstorm`, gravando `sdd/features/BRAINSTORM_F15_SUBSTITUICAO.md`, só lendo o privado. Pronto quando: as decisões acima foram respondidas pelo Roberto, a abordagem foi confirmada, o esforço foi estimado, e os cortes YAGNI e os 2 checkpoints estão registrados.
3. **Fechar**: rode a `sdd-handoff` com a etapa no topo e o prompt da sessão seguinte, a execução da F15, **aberta numa worktree do privado**. Abrir essa worktree é a primeira alteração no privado: faça só com o OK do Roberto, no molde que ele escolher no brainstorm. Grave os artefatos na branch `docs/` **sem trocar de branch na worktree**:

   ```bash
   cd /Users/robertoduarte/rdd-worktrees/sdd-open-f14-drive
   T=$(mktemp -d) && GIT_TERMINAL_PROMPT=0 git fetch -q origin docs/incorporar-starter
   git worktree add -q --detach "$T" origin/docs/incorporar-starter   # do remoto: a branch local pode estar atrás
   for d in features handoffs reports reviews; do mkdir -p "$T/sdd/$d" && rsync -a --delete "sdd/$d/" "$T/sdd/$d/"; done
   git -C "$T" add sdd/features sdd/handoffs sdd/reports sdd/reviews && git -C "$T" commit -q -m "docs(incorporar-starter): sessão 13" && GIT_TERMINAL_PROMPT=0 git -C "$T" push -q origin HEAD:docs/incorporar-starter
   git worktree remove --force "$T"
   ```

## O que não quebrar

- **Drive (F14):** as saídas 0/2/10/20/40/64, os 12 motivos e as 8 ações do `sdd-drive.sh`; só o script roda o gate que decide; o drive nunca publica; "só documento" = pasta + extensão, com `--no-renames` e `--ignore-submodules=none` (`tests/test_drive.py`, `test_f14_drive_textos.py`); `deploy-do-sha.sh` é a lógica única do item 10 da `sdd-release` (`tests/test_deploy_do_sha.py`); ficha aberta protege no `sdd-archive.py` (`tests/test_sdd_archive.py`).
- **Curadoria e invariantes (F14):** as saídas 0/1/2/3/64 do `playbook-curator.sh`, a tabela lida pelo cabeçalho, `AUTO` só em `contador` igual à colheita, stdout vazio em delta inválido (`tests/test_playbook_curator.py`, `test_curadoria_bloco.py`, `test_playbook_invariantes.py`); `COPIADO`/`JA_EXISTE`/`PARECIDO`/`IGNORADO`/`NAO_COPIADO` e nome idêntico (`tests/test_copiar_docs.py`); `branch.*` fora do `#GIT` e o resto dentro (`tests/test_governanca_fronteira.py`); as 6 seções do molde do handoff (`tests/test_f14_textos.py`).
- **UX e LLM (F13):** as saídas 0/2/64 e "nunca LIMPO sem ter lido" do `prompt-drift-scan.sh`, e 0/2/64 truncado do `contraste.sh` (`tests/test_prompt_drift_scan.py`, `test_contraste.py`); as colunas e os campos iguais em fragmento, template, lint e integração, e o roteador do passo 4 da `sdd-build` (`tests/test_f13_textos.py`); o inventário do `design-lint.py` (`tests/test_design_lint.py`).
- **Contexto e governança (F12):** os 2 motivos do exit 5, a ordem marcador → linha → bloco e o `--print` isento (`tests/test_governanca_gate.py`); o permitido resolvido no snapshot de antes e o snapshot fora do worktree, **nunca no `.git`** (`tests/test_governanca_fronteira.py`); seções, campos, retornos e exits iguais no brief, no passo, no lint e no yaml (`tests/test_f12_textos.py`); o padrão "Step 1.5" e "slice 2" continua proibido no pacote (`tests/test_correcoes_w0.py`).
- **Revisão adversarial (F10 + F11):** os exits de `adversarial-review.sh` (0/64/65/66/67/68; `--conferir` 0/2; `--ledger` 0/2/64), as chaves do META e a identidade adapter + modelo são contrato (`tests/test_revisao.py`, `test_revisao_adapters.py`); o gate offline (`adversarial-review-gate.sh`, 0/2/3/64) nunca usa rede, CLI real nem o repositório de quem o chama (`tests/test_revisao_gate.py`); o `eval-agree.sh` só lê arquivos. A release exige `review_externo` (`--conferir` CONFERE, ou dispensa D3 com motivo).
- **Fluxo encadeado (F9):** os exits do `sdd-fluxo.sh` e o `--self-test` são contrato (`tests/test_fluxo.py`); nomes do `despachar` por lista explícita, nunca faixa `[A-Za-z]`.
- **Marcas e lint de decisões:** a tabela do item 9 do `PERGUNTA_DECISAO.md` é a dona dos rótulos; toda pergunta nova de decisão leva marca; `sdd-decisoes-lint.sh --sites` acha 25 perguntas em 21 arquivos nas skills e 2 nos fragmentos — uma pergunta nova muda essa contagem em `tests/test_decisoes_lint.py`.
- **Subseção `### Fluxo encadeado`:** bloco comum idêntico nas 9 skills de fase, dentro do `## Encerramento (obrigatório)`; "Por que cada regra existe" logo antes do Encerramento.
- **Hooks (F8):** `sdd/hooks/pre-commit` recusa com `RESULTADO: COMMIT RECUSADO`; a regra REPORT pula `sdd/fixtures/` e `sdd/templates/`; o `pre-push` nunca recusa; `tests/test_hooks.py`, `test_claude_adapter.py` e `test_alarme.py` são contrato.
- **`report-lint.py`** fail-closed (exits 0/1/64); **`verify-gate.sh`** com os seis exits (0/2/3/4/5/64), `--print`, `--trace` e as fixtures de `sdd/fixtures/`.
- **Camada de conversa** (F4 + F5 + F13): bloco comum em 16 `SKILL.md`, seção nas 19, `FRASES` do `tests/test_conversa.py`.
- **`init`/`sync`/`doctor`:** o `init` nunca sobrescreve skill instalada nem `sdd/bin/*` (completa o que falta) e copia `sdd/fixtures/` só na 1ª instalação; `tests/test_sdd_open.py` fica.
- **Docs testados** (`tests/test_docs.py`): todo link de `README*.md` e `docs/**` abre; o padrão `/drive` segue proibido no pacote (`tests/test_correcoes_w0.py`): o documento é `docs/sdd-drive.md`.
- **Contratos de `sdd/`:** `playbook-lint.sh --self-test` 0; o bloco do OK da `sdd-release` mantém rótulos, ordem e uma pergunta só (`tests/test_contrato_build_release.py`).
- **CI:** nada de caractere invisível nem `curl … | sh` literal em `.agents/skills/`; piso Python 3.9 / bash 3.2; `release.yml` com teto 25 no `testes` e 45 no `testes-macos` (a suíte levou 20m35s no Ubuntu e 35m38s no macOS na F14 Drive): confira se ainda cabe.
- **Padrão agnóstico (P2):** `tests/test_agnostico.py` reprova `AskUserQuestion`, `TodoWrite`, `PreToolUse`, `PostToolUse`, `subagent_type`, `Task tool`, `Agent tool` e `/model` em `.agents/skills/**`, `sdd/templates/**`, `sdd/hooks/**`, `AGENTS.md.tmpl` e `sdd/playbook.md`. Os nomes de engine são dado do `registry.tsv` e dos adapters em `sdd/bin/adapters/`, não texto de skill.
- **Literais que o publish-gate reprova** (`scripts/publish-gate-patterns.txt`): e-mail só em `example.*`; CPF, CNPJ, telefone, 11+ dígitos e caminho `/Users/<nome>/` fora de arquivo rastreado; o G1 (gitleaks) varre `tests/` e `sdd/review/stubs/` — chave de API nunca em arquivo, nem em stub.
- **Arquivos:** `python3 -B` e `git add` por nome; bash 3.2; `rm -rf` só com `"${X:?}"`; `sdd/features|handoffs|reports|reviews|traces/` **nunca** entram em commit da branch de trabalho; todo arquivo novo no `MANIFEST.txt`.
- **Push e remoto:** todo comando remoto com `GIT_TERMINAL_PROMPT=0`; push em `main` só com OK explícito do Roberto citando "sdd-open"; nunca `--force`; a branch `docs/incorporar-starter` nunca vira PR.
- **Repositório privado:** só leitura nesta sessão, até o OK do Roberto; específico da RDD não viaja para o Open.
- **Fora de escopo nesta sessão:** a execução da F15 no privado (`init`, remoção de arquivos, deploy); F16 e F17; regenerar o sdd-starter; alterar o sdd-starter.

## Como fechar

Ao terminar, rode a skill **SDD Handoff by RDD** de novo para registrar o que foi feito
e preparar a próxima retomada.
