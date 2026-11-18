<<<AVALIACAO
feature: F14_DRIVE · ciclo: 2 · modo: veredito · commit: 58d0175 · bash 3.2 (/bin/bash) · python 3.9 (/usr/bin/python3)

## Veredito: NEEDS_WORK

1 HIGH, 4 MEDIUM, 16 LOW. O HIGH é um `gate-verde` falso. O conserto do M2 do ciclo 1 cobriu o rename sujo, mas não o mesmo rename depois de commitado. Esse commit é o que a própria ação `COMMITAR` pede.

Os 18 módulos de teste rodados na cópia de `git archive` passam (634 testes, 1 skipped). Nenhum deles pega os achados abaixo.

Contagem dos 38 ATs: PASS 30 · FAIL 5 (AT-006, 010, 013, 014, 030) · PARCIAL 2 (AT-005, 025) · NAO_VERIFICADO 1 (AT-038).

## Tabela por AT

Os logs estão em `sdd/reports/evidence/F14_DRIVE/`. "NN" abrevia `AVAL2-NN-*.log`.

| AT | Sonda | Esperado | Observado | Resultado |
|---|---|---|---|---|
| 001 | `iniciar --max 2` em pasta com espaço e acento (02) | estado completo, `rodada: 1/2`, exit 10 | isso | PASS |
| 002 | main, master, slot, origin/HEAD, HEAD destacado, kind xyz, `N/A`, marcador, sem Governança, vizinho da v2.6.0 (10, 19) | 20 ou 2, sem estado | isso | PASS |
| 003 | `--dry-run`, `git status`, `ls` (02, 10) | `simulacao`, 0, nada gravado | isso | PASS |
| 004 | flag, slot, default e 12 valores inválidos (10) | 64 citando a origem | isso; slot vazio vale como ausente | PASS |
| 005 | ordem das ações e `seguir` de mentira (03, 11) | 1 ação; 64 de `seguir` sai 2 | rename commitado dá AVALIAR; 64 com linha `PARAR:` dá DESIGN | PARCIAL (H1, L2) |
| 006 | manifest de DESIGN real e com 2 tabelas (11, 12, 13) | 1 linha por arquivo | tarefas fantasma | FAIL (M1) |
| 007 | `proximo` 3x, commit zera, `--resume` (11) | `bloqueio-humano` na 3ª | isso | PASS |
| 008 | log, `--fundo`, trava morta, commit no meio do gate (02, 09) | HEAD e digital de antes do gate | isso; um detalhe de saída em L13 | PASS |
| 009 | gate sai 3, 4, 5, 64, 1, 137, 7 (10) | motivo tabelado, 20, sem gastar rodada | isso | PASS |
| 010 | 9 formas de sujeira (11, 19); rename commitado depois do vermelho (03) | COMMITAR; CORRIGIR só se só documento mudou | sujeira ok; rename commitado fica em CORRIGIR e o gate não roda | FAIL (H1) |
| 011 | 4 campos, gate não roda, aceite com o mesmo HEAD, aceite durante o gate (07, 08, 19) | `gate-alterado`; VERIFICAR depois do aceite | isso | PASS |
| 012 | orçamento em todos os verbos; `--resume --max` (11) | 20 sem gate; retoma ao subir | isso | PASS |
| 013 | 33 mutações do estado (04, 05, 19) e versão anterior 079f5fa (06) | `estado-invalido` em toda forma errada | os casos do M4 antigo ok; outros campos dão exit 2 ou motivo errado | FAIL (M4) |
| 014 | verde + rename commitado (03, 09); tarefa reaberta, DESIGN sumido, misto (07) | VERIFICAR com mudança de código | rename dá `gate-verde`, 0; os demais ok | FAIL (H1) |
| 015 | relatório em cada parada, bloqueio + recibo, troca aceita (14) | relatório reescrito | isso; recusa do `iniciar` não reescreve | PASS (L12) |
| 016 | `aguardar` real, exit 64, recibo, bloqueio (14) | 40; 64 repetido sem gravar o motivo | isso | PASS |
| 017 | shim de git e gh em todos os verbos (14); textos (01) | sem push nem gh | 358 linhas no registro, 0 push, 0 gh | PASS |
| 018 | self-test, gpgsign global, variável herdada, sabotagem do 40 (14) | 0; exit 2 nomeando o caso | isso | PASS |
| 019 | contagem dos 12 motivos nos 4 lugares, lint, testes (01, 18) | iguais | isso | PASS |
| 020 | `despachar` e aviso da 1ª parada (14) | tarefa, `<<<RODADA`, "nada foi publicado", até n paradas | isso | PASS |
| 021 | leitura da passada 0b e testes (18, 20) | ordem e conteúdo | isso | PASS |
| 022 | verde, andando, outra branch, tag, schedule, pull_request (15) | 0 só no caso certo | isso | PASS |
| 023 | substituto, verde de filho, não contém, commit desconhecido (15) | 0, 2 ou 4 | isso; o desconhecido dá 4 | PASS |
| 024 | redisparo, marca, worktree, dispatch humano (15) | 1 `workflow run`, nunca `rerun` | isso | PASS |
| 025 | todos os passos, ponta, fetch, teto, recusa do disparo (15) | 2 | 422 e 403 dão 2; 404 dá 64; job falho sem passo `failure` redispara | PARCIAL (L4, L5) |
| 026 | sem run, teto, erro de consulta, login, workflow desconhecido, gh ausente (15, 21) | 4, 3, 64 | isso | PASS |
| 027 | leitura do item 10 e testes (18, 20) | chama o script e mapeia os exits | isso | PASS |
| 028 | limites 29/30 e 59/60, lotes, totais (19) | lista e nada muda | isso; caso de borda em L8 | PASS |
| 029 | `--aplicar`, destino existente, `index.lock` (16, 19) | staged; 2 se o `git mv` falha | isso | PASS |
| 030 | prefixos, caixa, slice, citados (16, 19) | grupo protegido | os casos exatos do ciclo 1 ok; vizinhos escapam | FAIL (M2, M3) |
| 031 | leitura dos passos 5, 11 e 15b (18) | regra do changelog e archive | isso | PASS |
| 032 | não rastreado nas 4 pastas (17) | exit 0, com aviso | isso | PASS |
| 033 | modificado, fora, nome vizinho, rename nos 2 sentidos (17) | exit 1 listando | isso | PASS |
| 034 | 12 linhas de log (17) | sem falso achado; achado real conta | isso; risco de leitura em L14 | PASS |
| 035 | grep e testes (18) | 3 slots, sem `max_tokens` | isso | PASS |
| 036 | docs, roadmap, manifest, contagem (18, 21) | 19 skills nos 3 lugares | README e guia ok; `AGENTS.md.tmpl` tem 18 | PASS, com L15 pela letra |
| 037 | `--checar`, `--print`, `seguir --drive`, 10 módulos (18, 20) | contratos mantidos | isso | PASS |
| 038 | agente real | — | fica para depois | NAO_VERIFICADO |

## Consertos do ciclo 1 (itens do ciclo 1, com a numeração daquele relatório)

- **Seguram:**
  - H1, M1 e M3.
  - M4 nos casos citados.
  - M5, M6, M7 e M8 nos casos exatos.
  - M9.
  - L1, L3, L4, L5, L6, L7, L9, L11, L13 e L14.
- **Parciais:**
  - M2: o rename sujo foi coberto, o commitado não (H1 abaixo).
  - M5 e M6: os vizinhos falham (M2 e M3 abaixo).
  - L15 (ciclo 1): vira L7 e L8 abaixo.
- **Continua aberto:** L16 (ciclo 1), agora L9 abaixo.

## ACHADOS

As reproduções usam os ajudantes `mkrepo`, `drv`, `feito`, `rel`, `novo`, `mkarq`, `doc`, `ficha`, `cen` e `d1`. O texto de `lab.sh` e dos shims está em AVAL2-00-lab.log; `doc` e `ficha` estão no início de AVAL2-16 e `feito` e `rel` em AVAL2-00. O script exato de cada sonda está no início do log citado.

### HIGH

**H1. Rename de código para pasta de documento, depois de commitado, vira `gate-verde` falso (AT-014, AT-010, AT-005).**

`sdd/bin/sdd-drive.sh:464`: `so_documentos` usa `git diff --name-only` sem `--no-renames`, e aí só o nome novo aparece. É a mesma raiz do M2 do ciclo 1, do outro lado. O `fora_dos_documentos` manda COMMITAR, e o commit que a seta pede apaga o sinal.

Reprodução (AVAL2-03):
```
mkrepo "$(novo)"; echo print > codigo.py; git add -A; git commit -qm cod; touch .verde
drv iniciar $D; feito; rel; drv verificar $D      # AVALIAR_E_RELATAR
git mv codigo.py sdd/reports/codigo.py; drv verificar $D   # COMMITAR, correto
git commit -qm 'tira codigo do lugar'; drv concluir $D     # motivo: gate-verde, exit 0
```

Observado:
- `git diff --name-only HEAD~1 HEAD` dá só `sdd/reports/codigo.py`. Com `--no-renames`, dá também `codigo.py`.
- O mesmo vale para um commit feito no meio do gate (AVAL2-09 A4).
- Depois de um vermelho, a mesma sequência deixa `proximo` e `verificar` em CORRIGIR, e o gate não roda (gate.calls fica com 1 linha).
- O rename de documento para código está certo: dá VERIFICAR.

Conserto sugerido: `--no-renames` nessa chamada, com teste nos 2 sentidos.

### MEDIUM

**M1. Tarefas fantasma no PROGRESS (AT-006).** `linhas_do_manifest` (linha 404) lê toda tabela até o próximo `## ` e reaproveita a coluna da 1ª.

- 9 dos 15 DESIGNs reais têm `### Agent Assignment Rationale` dentro de `## File Manifest`, inclusive o desta feature. O molde usa `##` e escapa.
- Reprodução (AVAL2-13): copiar `DESIGN_F14_DRIVE.md` como `DESIGN_F.md`, commitar e rodar `drv iniciar $D`. O PROGRESS ganha `- [ ] Files Assigned` e `- [ ] todos`, e `proximo` pede "tarefa: 39 de 40 — Files Assigned".
- Com 2 tabelas de arquivos, nasce `- [ ] File`. A célula `` `b.py` (novo) `` vira `` b.py` (novo `` (AVAL2-11). F4 e F5 têm 17 linhas assim (AVAL2-12).
- Efeito: cada fantasma gasta um executor ou uma parada de exit 40, e na 3ª repetição vira `bloqueio-humano`.

**M2. Documento de feature aberta escapa da ficha pelo nome (AT-030, vizinho do M5).**

Reprodução (AVAL2-19, última seção; nome real na prova de AVAL2-16):
```
mkarq "$(novo)"; printf '# H\n\n| **Status** | aberta |\n' > sdd/handoffs/HANDOFF_F14_DRIVE.md
doc sdd/reviews/REVISAO_FRONTEIRA_F14_DRIVE_20261105.md; doc sdd/reviews/AVALIACAO_F14_DRIVE-ciclo2.md
sdd-archive.py --lote soltos --aplicar --hoje 2026-11-05
```

Observado: os 2 são movidos. O grupo vira `FRONTEIRA_F14_DRIVE` e `F14_DRIVE-ciclo2`. Neste repositório, `REVISAO_FRONTEIRA_F14_PLAYBOOK_20261105.md` é real e entra em `soltos` com `HANDOFF_F14_PLAYBOOK` aberta. Reversível: fica só staged.

**M3. Ficha aberta com outra caixa não protege (AT-030, "whatever the case of its name").**

Reprodução (AVAL2-16): `ficha f14 aberta; doc sdd/reports/BUILD_REPORT_F14.md; doc sdd/features/DEFINE_F14.md; sdd-archive.py --hoje 2026-11-05` dá `sem-ledger=2 protegidos=0`.

Também falham:
- `HANDOFF_GO_X` com `BUILD_REPORT_go_x`.
- `HANDOFF_ação` com `BUILD_REPORT_ação` (o acento fica fora de `RX`).

Mesma caixa funciona, então o caso exato do M6 antigo segura.

**M4. Estado com forma errada ainda não dá `estado-invalido` (AT-013).** `forma_ok` não olha `motivo`, `detalhe`, `gate_linhas` nem o valor de `maximo`.

Reprodução (AVAL2-04, AVAL2-05):
- `"motivo":"xyz"` ou `3`, depois `recibo`: exit 2, `erro inesperado: KeyError`.
- `"detalhe":3`, depois `recibo`: exit 2, TypeError.
- `"gate_linhas":3` com o gate alterado, depois `proximo`: exit 2, TypeError.
- `"maximo":0` ou `-1`: `orcamento-rodadas`, `Rodadas vermelhas: 0 de 0`.
- `"versao":99` e `"feature":"OUTRA"` são aceitos.

Não há traceback nem rodada contada errado, mas o exit 2 diz "falha do próprio script", e o AT pede 20. O estado da versão anterior (079f5fa) retoma bem (AVAL2-06).

### LOW

- **L1.** Com parada de gate guardada, `proximo` dá `manual-ux` e `concluir` dá VERIFICAR. Contraria o comentário da linha 802 (AVAL2-07 B).
- **L2.** `seguir` com linha `PARAR:` e exit 64 dá DESIGN (AT-005). A linha 541 olha o texto, não o exit. Só com stub: o `seguir` real não imprime isso (AVAL2-11).
- **L3.** Rename na 2ª coluna (`git add -N`): `fora_dos_documentos` lista `igo.py` em vez de `codigo.py`. Com nome antigo de até 3 caracteres (`a.p`), o gate roda e gasta rodada (AVAL2-11, AVAL2-19).
- **L4.** Passageiro no job 1 e job 2 com `conclusion: failure` sem passo `failure` (passo `cancelled` ou lista vazia): redispara. `passos_falhos` não olha o job. Formas sintéticas (AVAL2-15).
- **L5.** Disparo recusado com `HTTP 404: workflow … not found` sai 64 dizendo "nada foi consultado". O AT-025 pede 2 (AVAL2-15).
- **L6.** `gh run view` falhando (502) dá `falhou`, exit 2, "este passo não está em deploy.transient_steps". A razão é falsa e a repetição se perde. O certo seria tentar a consulta de novo (AVAL2-15).
- **L7.** Arquivo sujo com mtime velho conta como quieto e é movido (`touch -t 202001010000`). A data vem do mtime, não de "agora" (AVAL2-16).
- **L8.** Documento rastreado que só existe num commit de merge não tem data no `git log --name-only`. Vale 10^6 dias: criado hoje, vai para `_REPORTS_0000-00` (AVAL2-19).
- **L9.** Arquivo rastreado com nome NFD cai em "sem classificação" ou "não rastreado" (AVAL2-16). É o L16 do ciclo 1.
- **L10.** PROGRESS com crase (`` - [x] `a` ``) não casa com o manifest: reabre a tarefa como pendente, e a contagem vira "3 de 4" (AVAL2-11).
- **L11.** `SDD_DRIVE_TRAVA_HERDADA=1` no ambiente de quem chama: `verificar` roda o gate com tarefa pendente, ignora a trava e gasta rodada (AVAL2-09 H).
- **L12.** `iniciar` recusado com estado válido não reescreve o DRIVE_REPORT, e o AT-015 diz "any stop … with a state file present" (AVAL2-14).
- **L13.** Vermelho com commit durante o gate imprime só `ACAO: VERIFICAR`, sem log nem aviso de que a rodada foi gasta. Linhas 783-784 (AVAL2-19).
- **L14.** `src/app.py:12: ❌ LM-001 …` de um projeto não conta como achado. O padrão `\S+:\d+: ❌ ` aceita qualquer arquivo. A letra do AT-034 permite, mas um achado real se perde em silêncio (AVAL2-17).
- **L15.** `AGENTS.md.tmpl` lista 18 skills e falta `sdd-auditoria-harness`. A v2.6.0 já não a citava (AVAL2-21). `test_docs` passa mesmo assim.
- **L16.** Trava com conteúdo `-1`: `os.kill(-1, 0)` não falha e dá ESPERAR sem fim. Só com arquivo adulterado; a mensagem cita o arquivo (AVAL2-09 E2).

## Não coberto

- `gh` real, rede, Linux e Windows. Confirmei offline, por `strings` no gh 2.102.0, que as mensagens de workflow desconhecido existem no binário. Não executei o gh real.
- O gate inteiro do DEFINE, a suíte inteira, baseline na v2.6.0, CI, revisão adversarial e Release. Das sabotagens, rodei só 1, a do self-test.
- O L8 do ciclo 1 não foi retestado por inteiro (gate órfão depois de `kill -9` no python).
- AT-038.

## Erros meus nesta avaliação

- **Arquivo solto no projeto:** um `ev.sh true` criou `./true` na raiz da worktree. Removi na hora e `git status` confere. Foi a única gravação fora de `AVAL2-*.log`.
- **Comando errado:** o script da sonda de AVAL2-19 trazia um `rm -f /dev/null` digitado por engano. O sistema recusou e `/dev/null` segue intacto; a linha aparece nesse log.
- **Trechos inválidos de sonda, refeitos:**
  - AVAL2-05, os 3 primeiros blocos: o script velho não estava commitado. Refeito em AVAL2-06.
  - AVAL2-08, casos A, A2 e G: aspas erradas no gate. Refeito em AVAL2-09.
  - AVAL2-15, caso "gh ausente": meu `grep` saiu do PATH. Refeito em AVAL2-21.
  - AVAL2-19, cmd vazio: a sonda não testou nada, porque `mkrepo` usa o default.
- **Outra sessão:** vi processos de `sdd-drive` e `verify-gate` em `/private/var/folders/…/sdd-open-ovn69mtk`. Não são meus e não mexi neles.

A pasta temporária da sonda foi apagada. Nenhum código ou documento do projeto foi editado, nada foi publicado e não houve rede externa.

Logs: `/Users/robertoduarte/rdd-worktrees/sdd-open-f14-drive/sdd/reports/evidence/F14_DRIVE/AVAL2-00-lab.log` a `AVAL2-21-agents-tmpl-e-gh-ausente.log` (22 arquivos).
>>>
