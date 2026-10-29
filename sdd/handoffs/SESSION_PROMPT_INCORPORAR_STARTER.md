# Continuar: INCORPORAR_STARTER — sessão 1: W0 (correções) + M1 (CI)

Esta sessão começa numa **worktree limpa**. Os artefatos SDD da família (features, handoffs, reports) vivem na branch `docs/incorporar-starter` do remoto, nunca mesclada em `main`.

## Preparar a worktree (antes de ler qualquer coisa)

```bash
cd /Users/robertoduarte/rdd-public/sdd-open
GIT_TERMINAL_PROMPT=0 git fetch -q origin
git worktree add /Users/robertoduarte/rdd-worktrees/sdd-open-w0-m1 -b feat/w0-m1 origin/main
cd /Users/robertoduarte/rdd-worktrees/sdd-open-w0-m1
git checkout origin/docs/incorporar-starter -- sdd/features sdd/handoffs sdd/reports
git rm -r -q --cached sdd/features sdd/handoffs sdd/reports     # ficam no disco, fora do commit
git status --short | head -3                                    # esperado: só "?? sdd/…"
git log --oneline -1                                            # esperado: 1a54da5 (= v2.2.3) ou mais novo
```

Se `/Users/robertoduarte/rdd-public/sdd-open` não for o clone do remoto `https://github.com/robertodiasduarte/sdd-open.git`, use a worktree antiga como base: `git -C /Users/robertoduarte/rdd-worktrees/sdd-open-incorporar-starter worktree add …`. Não trabalhar na worktree antiga (`sdd-open-incorporar-starter`): ela fica como está até a F15 fechar.

Depois, leia nesta ordem:
- `sdd/features/PLANO_F4_F15_CONSOLIDADO.md` — seção 0 (os 4 parâmetros de verificação), 3.1 (W0), 8 "Manutenção M1", 8.0 (regras e degradação por vendor) e 10 (agrupamento por sessão);
- `sdd/handoffs/HANDOFF_INCORPORAR_STARTER.md` — Ficha, `## Eventos` e a etapa "F3 Build e Release".

## Onde paramos

F1–F3 entregues; a última é https://github.com/robertodiasduarte/sdd-open/releases/tag/v2.2.3 (tag em `1a54da5`, SHA-256 do pacote `635e30050b83188f5965ffa5ddd09fac496973dc4a66d7bbd6391c9eb1ffd777`, conferido). São 16 skills e 304 testes verdes no piso `SDD_TEST_BASH=/bin/bash /usr/bin/python3` (Python 3.9.6, bash 3.2.57). O programa foi redesenhado em 29/10: F4–F6 (starter) → F7–F14 (porte do SDD privado) → F15 (substituir o privado pelo Open), sob 4 parâmetros: **P1** corrigir erros, **P2** manter o padrão agnóstico, **P3** incorporar o que o starter faz melhor, **P4** acabar com o SDD privado. Esta sessão faz as duas tarefas pequenas que vêm antes da F4: **W0** e **M1**, cada uma com seu PR.

## Contexto que você precisa ter

- Remoto `https://github.com/robertodiasduarte/sdd-open.git`; `main` em `1a54da5` = `v2.2.3`. Release automática no push de `main` que toca `.agents/skills/**`, `bin/**`, `sdd/bin/**`, `sdd/templates/**`, `sdd/fixtures/**`, `sdd/playbook.md`, `sdd/config.example.yaml`, `AGENTS.md.tmpl` (`.github/workflows/release.yml`); push em `.github/**` sozinho **não** publica Release.
- Decisões já tomadas, não reabrir: as 5 da frente (`## Eventos` do handoff); W0 antes da F4 e junto com M1 (seção 10 do plano); artefatos SDD na branch `docs/`, nunca em `main`.
- Skills do fluxo: `sdd-brainstorm`, `sdd-define`, `sdd-design`, `sdd-build`, `sdd-handoff`, `sdd-release` em `/Users/robertoduarte/.claude/skills/`. W0 e M1 são **fixes**: podem pular BRAINSTORM/DEFINE/DESIGN (regra "Quando pular o SDD formal" da `sdd-release`), mas cada uma tem teste, sabotagem no relatório e revisão de contexto fresco antes do PR, como F1–F3.
- Evidência: `sdd/reports/evidence/W0/` e `sdd/reports/evidence/M1/`, no molde de `sdd/reports/evidence/F3_BUILD_RELEASE/sabotagem.sh` e `gerar-at.sh`.

## Tarefas, em ordem

1. **W0 — as 5 correções** (seção 3.1 do plano; parâmetro P1):
   - 4.1 bug: `.agents/skills/sdd-iterate/SKILL.md:43` roda `sdd/bin/verify-gate.sh --print <DEFINE>` e espera "exit ≠5", mas `sdd/bin/verify-gate.sh:38` isenta `--print` dos marcadores: a checagem nunca dispara. Trocar por duas chamadas: `--print` (prova que o bloco parseia, exit 0/64) **e** o gate sem `--print` (marcador ativo ⇒ 5). Teste novo em `tests/`: a fixture `sdd/fixtures/DEFINE_FIXTURE_NEEDS_CLARIFICATION.md` dá 0 com `--print` e 5 sem; e um teste de contrato que lê a `sdd-iterate` e exige as duas chamadas.
   - 4.2: tirar "CONTEXTO de domínio / Step 1.5 / slice 2" de `sdd/templates/DEFINE_TEMPLATE.md:161,169` e `sdd/config.example.yaml:19,46` (a F12 recoloca o contexto de domínio quando o cartógrafo existir).
   - 4.3: tirar `/drive` de `sdd/templates/fragments/CLARIFY.md:17`, `sdd/templates/DEFINE_TEMPLATE.md:91` e `sdd/templates/fragments/VERIFY_GATE.md:74` (a F14 cria a `sdd-drive`).
   - 4.4: trocar `.githooks/claude-build-report-guard.py` por `sdd/bin/report-lint.py` em `sdd/templates/BUILD_REPORT_TEMPLATE.md:213` e `sdd/templates/fragments/EVIDENCIA.md:4` (a F7 traz o guard; aí apontam para os dois).
   - 4.5: `.agents/skills/sdd-build/references/contexto-fresco.md:41,58` dizem "Não escreva em arquivo algum"; `sdd/templates/fragments/EVIDENCIA.md:29` espera `AVAL-roteiro-3.log`. Alinhar: "sem Write/Edit em código; via shell, escreve **só** em `sdd/reports/evidence/<F>/AVAL-*.log`".

   Bump: `sdd-iterate` 2.0.0 → 2.0.1 e `sdd-build` 2.1.0 → 2.1.1. Teste de contrato para o grep: `grep -rnE 'claude-build-report-guard|/drive|Step 1\.5|slice 2' sdd/ .agents/` sem hit. Sabotagem: 1 por script alterado (aqui só o teste da 4.1 tem script; os outros são texto: o teste de contrato basta). Pronto quando: `PUBLISH_GATE_MODE=ci bash scripts/publish-gate.sh <cópia de git archive HEAD>` 0, suíte verde no piso, `python3 scripts/check-versions.py --base v2.2.3 --base-obrigatoria` 0, revisão de contexto fresco sem HIGH aberta, PR com CI verde, OK do Roberto citando "sdd-open", push fast-forward em `main`, Release `v2.2.4` com `SHA256SUMS.txt` conferido por `shasum -a 256 -c`.

2. **M1 — manutenção do CI** (seção 8 do plano, "Manutenção M1"; parâmetro P2). Só depois da Release da W0:
   - job em `macos-latest` nos dois workflows (`.github/workflows/publish-gate.yml` e `release.yml`, job `testes`), rodando a suíte com o `/usr/bin/python3` e o `/bin/bash` do runner (`SDD_TEST_BASH=/bin/bash`), para o piso Python 3.9 + bash 3.2 ser provado pelo robô, não só na máquina do Roberto;
   - trocar o pin `actions/checkout@11d5960a326750d5838078e36cf38b85af677262` (v4.4.0, Node 20 depreciado) por um SHA completo de uma release v5 do `actions/checkout` (conferir no GitHub; nunca tag mutável); `tests/test_release_workflow.py::test_actions_fixadas_por_sha` continua verde;
   - baseline da `sdd-auditoria-harness` sobre `.agents/skills/` no CI (risco de alteração maliciosa de skill publicada): ler `.agents/skills/sdd-auditoria-harness/SKILL.md` e `scripts/collect_evidence.py` para o comando; falha com HIGH/CRITICAL.

   Mexe só em `.github/workflows/` e em `tests/test_release_workflow.py`; nenhuma skill sobe de versão. Pronto quando: PR com CI verde em `ubuntu-latest` **e** `macos-latest`; OK do Roberto citando "sdd-open"; push em `main`. Como `.github/**` não dispara Release, M1 **não** gera tag; registrar isso no handoff.

3. **Fechar a sessão**: `sdd-handoff` com duas etapas novas no topo (M1 e W0) e o prompt da sessão 2 (F4 Conversa: escopo nas seções 4.1 e 8.0 do plano, decisões 2 e 3 da seção 5). Depois gravar os artefatos na branch `docs/` **sem trocar de branch nesta worktree**:

   ```bash
   cd /Users/robertoduarte/rdd-worktrees/sdd-open-w0-m1
   T=$(mktemp -d) && GIT_TERMINAL_PROMPT=0 git fetch -q origin docs/incorporar-starter
   git worktree add -q "$T" docs/incorporar-starter
   rsync -a --delete sdd/features/ "$T/sdd/features/" && rsync -a --delete sdd/handoffs/ "$T/sdd/handoffs/" && rsync -a --delete sdd/reports/ "$T/sdd/reports/"
   git -C "$T" add sdd/features sdd/handoffs sdd/reports && git -C "$T" commit -q -m "docs(incorporar-starter): sessão 1 — W0 e M1" && GIT_TERMINAL_PROMPT=0 git -C "$T" push -q origin docs/incorporar-starter
   git worktree remove --force "$T"
   ```

## O que não quebrar

- **Contratos de `sdd/`**: os seis exits de `sdd/bin/verify-gate.sh` (0/2/3/4/5/64) e `sdd/fixtures/` ficam idênticos (a 4.1 muda a skill, não o script); `report-lint.py` (32 testes), `playbook-lint.sh --self-test` 0; os 304 testes continuam verdes no piso.
- **Contratos da F3**: `tests/test_contrato_build_release.py` confere o bloco do OK da `sdd-release`, o passo 4b da `sdd-build` e a referência `aplicar-migration.md` — a 4.5 mexe em `contexto-fresco.md`, não nesses.
- **Padrão agnóstico (P2)**: nenhum texto novo cita ferramenta de um agente só (`AskUserQuestion`, `Agent`, `PreToolUse`); o teste formal chega na F4.
- **Literais que o publish-gate reprova** (`scripts/publish-gate-patterns.txt`): e-mail só em `example.com/.org/.net`; CPF, CNPJ, telefone, `git@host` e sequências de 11+ dígitos montados em tempo de execução; hosts em `.invalid`.
- **Arquivos**: novo arquivo entra no `MANIFEST.txt` em ordem `LC_ALL=C`; `python3 -B`; `git add` por nome (não há `.gitignore`); sem shebang zsh, sem symlink, bash 3.2; não fazer `chmod` em massa. `sdd/features/`, `sdd/handoffs/`, `sdd/reports/` **nunca** entram em commit da branch de trabalho.
- **Push e remoto**: todo comando remoto com `GIT_TERMINAL_PROMPT=0`; push em `main` só com OK explícito do Roberto citando "sdd-open" na mesma mensagem; nunca `--force`; a branch `docs/incorporar-starter` nunca vira PR.
- **Fora de escopo nesta sessão:** F4 (camada de conversa, linters, identificação); qualquer item de F5–F15; redesenhar a CLI ou o `config.yaml`; alterar o sdd-starter ou o repositório privado.

## Como fechar

Ao terminar, rode a skill **SDD Handoff by RDD** de novo para registrar o que foi feito
e preparar a próxima retomada.
