# REVISAO DESIGN: F14_DRIVE

- **Data:** 2026-11-05 · **Modo:** contrato · **Lido:** DEFINE v1.2 e DESIGN v1.0
- **Quem revisou:** agente de contexto fresco; não viu a conversa do build
- **Veredito:** NEEDS_WORK — 5 propostas de aceite; 4 HIGH · 14 MEDIUM · 8 LOW
- **Logs:** `sdd/reports/evidence/F14_DRIVE/AVAL-DESIGN-01` a `-12-*.log`

## Propostas de aceite

| # | Alvo | Problema | Como verificar |
|---|---|---|---|
| A1 | AT-008, AT-012 | depois de `orcamento-rodadas`, `proximo` devolve CORRIGIR e `verificar` roda de novo | `iniciar --max 1`, vermelho, commit novo, `proximo` e `verificar` saem 20; o gate roda 1 vez só |
| A2 | AT-011, AT-010, AT-014 | gate rodado com o comando antigo vale depois de `--aceitar-gate-novo` | verde, troca, aceite: `concluir` sai 10; vermelho, troca, aceite: `verificar` no mesmo HEAD roda |
| A3 | AT-002 | `verify-gate.sh` velho ao lado do script novo vira `define-invalido` | `verify-gate.sh` e `sdd-fluxo.sh` da `v2.6.0`: `iniciar` sai 2, sem estado |
| A4 | AT-010, AT-014 | arquivo sem `git add` passa como verde de HEAD | `src/novo.py` não rastreado: COMMITAR, 0 chamadas do gate |
| A5 | AT-017 | o grep prova o texto; o UX não está no `git archive` | toda a sequência com `git` e `gh` de mentira: nada de push, release ou workflow run; as 12 frases fixas no teste |

## Achados

### HIGH

- **H1. Orçamento não barra por script.** A ordem do Decision 3 não consulta o limite; depois de exit 20, `proximo` dá CORRIGIR e `verificar` roda a 4ª vez, podendo chegar a `gate-verde`.
- **H2. Gate antigo vale depois de aceitar o novo.** Os gates são gravados sem impressão digital: verde com A, troca para B, aceite, `concluir` dá `gate-verde` sem B ter rodado; vermelho por `cmd` errado exigiria commit vazio.
- **H3. Upgrade quebra com diagnóstico falso.** O `init` repõe só script ausente (log 12): `sdd-drive.sh` novo com `verify-gate.sh` velho diz "O DEFINE não tem um teste final válido" em qualquer DEFINE; `seguir` 64 viraria `ACAO: DESIGN`; fixture em pasta nova não chega no upgrade.
- **H4. `verificar` não sobrevive a gate longo e não tem trava.** O gate desta frente leva 17m41s no CI e a ferramenta de shell do agente corta em 600 s: fica log sem `[exit=N]`, e `proximo` repete VERIFICAR até `bloqueio-humano`. 2 gates juntos e o último `os.replace` apaga o outro.

### MEDIUM

- **M1.** O `--print` não imprime `manual_fallback` (log 01): o checklist muda sem parar.
- **M2.** Pattern 5 grava o log invertido (log 02): falta `f.flush()`.
- **M3.** Verde pode não ser do commit: `git add` esquecido, com gate na árvore de trabalho.
- **M4.** Commit só de documento depois de um vermelho gasta rodada com o mesmo código.
- **M5.** Lugar do `--checar` indefinido: `kind: xyz` e `cmd: N/A` passariam, e manual-ux sairia 4.
- **M6.** Fonte da branch padrão: projeto em `master` com o slot de exemplo `main` passa; HEAD destacado também.
- **M7.** Corrida depois do redisparo: sem run novo na lista, sairia 2 com publicação em andamento.
- **M8.** Filtro por `event` se perde no porte: `schedule` no mesmo SHA daria `✅ no ar`.
- **M9.** `--ours` depende da operação (log 06): em `git merge` é a frente; e o conflito nasce no passo 5, não no 11.
- **M10.** O filtro da L10 deixa `…/x.md:0: ❌ ID duplicado: LM-005`, diagnóstico de `playbook-lint.sh:134` (log 11).
- **M11.** `DRIVE-gate-r<k>.log` por rodada se sobrescreve: exits 0, 3, 4, 5 e 64 não gastam rodada.
- **M12.** "Sem ✅" diverge do `handoff-lint.py:74`, que usa `startswith`: `🔨 em andamento — F1 ✅` contaria como fechada.
- **M13.** AT-005 e AT-001 discordam do Decision 3.
- **M14.** AT-038 fora do alcance do `cmd`; AT-018 sem teste explícito do `--self-test`.

### LOW

- **L1.** Pattern 1: `NUCLEO="$(cat <<'PY'` com apóstrofo quebra no bash 3.2 (log 03); `-c` importa `json.py` do projeto.
- **L2.** `RE_REVISAO` lê frase humana; a linha de transição diria "encadeamento ligado em sdd/config.yaml" sob `--drive`.
- **L3.** Archive: destino dos lotes, `AAAA-MM` dos soltos e expressão de nomes não escritos no DESIGN.
- **L4.** `deploy-do-sha`: sem `GIT_TERMINAL_PROMPT=0`; `timed_out` com substituto; marca por worktree; erro de login dito como "não achei o run".
- **L5.** AT-033 e `evidence/`; AT-027 e o `merge-base` legítimo fora do item 10.
- **L6.** manual-ux é terminal; Decision 4 e AT-010 se contradizem sobre repetir.
- **L7.** AT-013 omite 3 verbos; AT-020 não diz de onde lê a tarefa nem o que fazer se `despachar` sair 64.
- **L8.** CORRIGIR por DESIGN com linha nova no manifest não cria tarefa.

Premissas confirmadas: A-002 (log 10); `design-lint.py` passa e `review-design` EXIGIDO (log 04); NON_WAIVABLE para consumidor quebrado existe; marcas D2, D4 e auto existem; `despachar` aceita o brief já no destino.
