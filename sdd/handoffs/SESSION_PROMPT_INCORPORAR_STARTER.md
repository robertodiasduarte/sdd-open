# Continuar: INCORPORAR_STARTER — sessão 14: publicar a v2.7.1 e abrir a F15 no repositório privado

Esta sessão roda **dentro da worktree** `/Users/robertoduarte/rdd-worktrees/sdd-open-f14-drive`, branch `feat/f14-drive`, em `3d69536` (três commits à frente de `origin/main` = `b0663d3` = tag `v2.7.0`: `b3526ae` curadoria, `5a1e3fc` rodada 5, `3d69536` rodada 6). A branch remota `feat/f14-drive-v271` aponta para o mesmo `3d69536` e tem o **PR #19** (https://github.com/robertodiasduarte/sdd-open/pull/19). Os artefatos SDD da família (features, handoffs, reports, reviews) estão no disco, fora do commit; a fonte deles é a branch `docs/incorporar-starter` do remoto, nunca mesclada em `main`.

## Conferir a worktree (antes de ler qualquer coisa)

Se a sessão abriu em outra pasta, pare e peça ao Roberto para abrir o agente em `/Users/robertoduarte/rdd-worktrees/sdd-open-f14-drive`: nenhum `cd` muda a pasta à qual a sessão fica presa. Se a worktree tiver sumido, ela volta com `git -C /Users/robertoduarte/rdd-public/sdd-open worktree add /Users/robertoduarte/rdd-worktrees/sdd-open-f14-drive feat/f14-drive` e os documentos com `git checkout origin/docs/incorporar-starter -- sdd/features sdd/handoffs sdd/reports sdd/reviews` + `git rm -r -q --cached` das mesmas pastas.

```bash
git rev-parse --show-toplevel                 # esperado: /Users/robertoduarte/rdd-worktrees/sdd-open-f14-drive
git branch --show-current                     # esperado: feat/f14-drive
git log --oneline -1                          # esperado: 3d69536 fix(f14): os 3 achados da rodada 6
GIT_TERMINAL_PROMPT=0 git fetch -q origin
git rev-parse --short origin/main             # esperado: b0663d3; se for outro, alguém publicou: leia antes de seguir
git rev-parse --short origin/feat/f14-drive-v271   # esperado: 3d69536
git status --short --untracked-files=no       # esperado: vazio
```

**Não apague a branch local `feat/f14-drive` antes de publicar.** As branches `feat/f14-playbook` e a worktree `sdd-open-docs-f16` já podem sair; apagar é decisão do Roberto.

Depois, leia: `sdd/handoffs/HANDOFF_INCORPORAR_STARTER.md` (Ficha, `## Eventos` e a etapa do topo, "Sessão 13") e `sdd/features/BRAINSTORM_F15_SUBSTITUICAO.md`.

## Onde paramos

- **`v2.7.1` pronta, não publicada.** Os 5 achados da rodada 5, o teste do slice e os 3 achados da rodada 6 estão consertados, cada um com teste dos 2 lados que cai no código anterior. `sdd-release` 2.8.1; `python3 scripts/check-versions.py --base v2.7.0 --base-obrigatoria` verde.
- **Revisão real:** rodada 7 sobre `3d69536`, `loop` PRONTO, `--conferir` CONFERE. Linha para o ledger da release: `review_externo: sdd/reports/reviews/EXTERNAL_REVIEW_20261107-133717 sha256=9a3ee072107b2542f581e95f6dafbd34c0874200ff397a367a78c400c69534d9 diversidade=vendor`. Um achado só de Windows nativo ficou pendente por D4 do Roberto (no ledger, `REBATIDA_ESCOPO`, `rodada=7`).
- **Verify Gate de `3d69536`:** a 1ª execução caiu em `test_duas_chamadas_juntas_repetem_uma_vez` (teto de 1 s) com a máquina carregada; sozinho passou 5 de 5; a 2ª execução, sem carga, saiu **verde**: 1.663 testes, `[exit=0]` (`sdd/reports/evidence/F14_DRIVE/verify-gate-3d69536.log`).
- **CI do PR #19** (run 42398580503): Ubuntu ✅ 18m21s; o macOS rodava no fechamento. Confira com `GIT_TERMINAL_PROMPT=0 gh pr checks 19 -R robertodiasduarte/sdd-open`.
- **Sabotagens não rodadas:** `sdd/reports/evidence/F14_DRIVE/sabotagens-5a1e3fc.sh` (10 mutantes, roda sobre `HEAD`).
- **F15:** brainstorm feito com o Roberto (abordagem A por fases; convivência até o fim; prova com feature nova de 2 camadas; documentos da execução no privado). **Plano v1.6:** F18, F19 e F20 incluídas em 2026-11-07.
- **Saldo da OpenRouter:** US$ 7,89 no fechamento (`GET https://openrouter.ai/api/v1/credits`; `limit_remaining` é o limite da chave, não o saldo). O Codex respondeu com crédito em 2026-11-07 (`codex exec -s read-only --skip-git-repo-check "responda só: ok" < /dev/null`, em pasta temporária).

## Contexto que você precisa ter

- **Remoto:** `https://github.com/robertodiasduarte/sdd-open.git`, **público**, inclusive a branch `docs/incorporar-starter`.
- **Release automática:** o push de `main` que toca `.agents/skills/**`, `sdd/bin/**`, `sdd/playbook.md` (entre outros) publica a release; `scripts/next-version.sh` dá `v2.7.1`. O job `release` espera `testes` (teto 25 min) e `testes-macos` (teto 45 min).
- **Rode gate e sabotagens sem outra carga:** testes de tempo caem com a máquina ocupada. Pare processo pelo pid, nunca por `pkill -f`.
- **zsh:** `=====` num `echo` quebra o comando; `$M:s…` é modificador (use `${M}`); grave logs com `sdd/reports/evidence/F14_DRIVE/ev.sh <log> "<cmd>"`.
- **Decisões da F15 já tomadas, não reabrir** (`BRAINSTORM_F15_SUBSTITUICAO.md`, Key Decisions): convivência sem data-limite; 3 slots genéricos de extensão na release (antes do OK, antes do push, depois do deploy; saídas 0/2/10); OK por publicação; `gate-baseline.sh` para vermelho herdado; D7 por patch fora do git e sync com OK; worktree pelo `/new-session` do privado; a ponte `sdd-public/` sai na fase 1; ganchos numa pasta só (`sdd/hooks/` chama `.githooks/`); cópias `~/.claude/skills/sdd-*` regeneradas na fase 1; Anexo C (`model:`, `/fewer-permission-prompts`, memória) some.
- **Privado** (`~/RDD/Wordpress`, remoto `robertodiasduarte/wordpressrdd`), medido em `origin/main` = `022c14aa7`: 29 frentes de feature abertas; `/release` em `.claude/commands/release.md`; checkout principal 2.286 commits atrás com os 4 arquivos da D7. Leia sempre do `origin/main` (`git -C /Users/robertoduarte/RDD/Wordpress show "origin/main:<arquivo>"`).

## Tarefas, em ordem

1. **Publicar a `v2.7.1`:**
   - o gate de `3d69536` já está verde; confira o CI do PR #19 (os 2 jobs verdes);
   - rode `bash sdd/reports/evidence/F14_DRIVE/sabotagens-5a1e3fc.sh > sdd/reports/evidence/F14_DRIVE/sabotagens-3d69536.log 2>&1` e registre as vivas (provável: "trava em arquivo que saiu do caminho vale", janela de corrida curta);
   - siga a `sdd-release` (`.agents/skills/sdd-release/SKILL.md`): bloco do OK uma vez; push `GIT_TERMINAL_PROMPT=0 git push origin HEAD:refs/heads/main` **só com o OK do Roberto citando "sdd-open" na mesma mensagem**; nunca `--force`;
   - depois: `bash sdd/bin/deploy-do-sha.sh --commit 3d69536 --workflow release.yml --branch main`, Release e hash.

   Pronto quando: `gh release view v2.7.1 -R robertodiasduarte/sdd-open` mostra `SHA256SUMS.txt` e `shasum -a 256 -c` confere.
2. **F15, fase 1 (instalar):** pergunte ao Roberto se abre a worktree do privado agora; com o OK, pelo `/new-session` do privado: `~/rdd-worktrees/f15-substituicao`, branch `feat/f15-substituicao` a partir do `origin/main`. A execução da F15 roda **numa sessão aberta nessa worktree**: aqui, só prepare o prompt dela. Pronto quando: o Roberto tem o prompt da sessão da F15 e a worktree existe.
3. **Fechar:** `sdd-handoff`, etapa no topo; grave os documentos na branch `docs/` sem trocar de branch:

   ```bash
   cd /Users/robertoduarte/rdd-worktrees/sdd-open-f14-drive
   T=$(mktemp -d) && GIT_TERMINAL_PROMPT=0 git fetch -q origin docs/incorporar-starter
   git worktree add -q --detach "$T" origin/docs/incorporar-starter
   for d in features handoffs reports reviews; do mkdir -p "$T/sdd/$d" && rsync -a --delete "sdd/$d/" "$T/sdd/$d/"; done
   git -C "$T" add sdd/features sdd/handoffs sdd/reports sdd/reviews && git -C "$T" commit -q -m "docs(incorporar-starter): sessão 14" && GIT_TERMINAL_PROMPT=0 git -C "$T" push -q origin HEAD:docs/incorporar-starter
   git worktree remove --force "$T"
   ```

## O que não quebrar

- **Trava de estado do drive:** `flock`/`msvcrt`, sem regra por idade; nada apaga a trava de outro processo; o arquivo só sai sob a trava e com `samestat`; `O_NOFOLLOW` onde existe (`tests/test_drive.py`, `EstadoSoUmPorVez`).
- **`deploy-do-sha.sh`:** 401 sobe como `SemLogin` e apaga a marca antes de sair 3; a frase "não achei nenhum run" é a do `fim(4` sem run, e o 4 do redisparo diz outra coisa (`test_f14_drive_textos.py`).
- **`sdd-archive.py`:** ficha de slice protege a feature e a mensagem cita o arquivo da ficha que existe; solto recente em "Recentes".
- **Revisão:** qualquer mudança em `3d69536` invalida o `--conferir`; os documentos das pastas SDD ficam fora do diff.
- **Contratos herdados:** os exits e motivos do `sdd-drive.sh`, do `verify-gate.sh`, do `report-lint.py`, do `adversarial-review.sh` e do `sdd-fluxo.sh`; o bloco do OK da `sdd-release` com rótulos, ordem e uma pergunta só; `tests/test_agnostico.py`; piso Python 3.9 / bash 3.2; `sdd/features|handoffs|reports|reviews|traces/` nunca em commit da branch de trabalho; todo arquivo novo no `MANIFEST.txt`.
- **Push e remoto:** `GIT_TERMINAL_PROMPT=0`; `main` só com OK citando "sdd-open"; a branch `docs/incorporar-starter` nunca vira PR.
- **Privado:** só leitura até o OK do Roberto; específico da RDD não viaja para o Open; detalhe de infraestrutura não vai para a branch `docs/` (pública).
- **Fora de escopo nesta sessão:** a execução da F15 dentro do privado; F16 a F20.

## Como fechar

Ao terminar, rode a skill **SDD Handoff by RDD** de novo para registrar o que foi feito
e preparar a próxima retomada.
