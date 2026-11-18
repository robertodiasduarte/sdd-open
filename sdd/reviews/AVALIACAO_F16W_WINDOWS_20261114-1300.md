# Avaliação de contexto novo — F16W_WINDOWS, ciclo 1

> Bloco devolvido pelo avaliador (subagente em contexto novo, modo veredito, brief de `sdd-build/references/contexto-fresco.md`), verbatim.

<<<AVALIACAO
FEATURE: F16W_WINDOWS · ciclo 1 · HEAD avaliado: 9e2ad33 (branch feat/f16w-windows, sem push, sem PR e sem run de CI: `git ls-remote origin feat/f16w-windows`, `gh pr list` e `gh run list` voltaram vazios)

## Veredito: NEEDS_WORK

Tudo o que dá para provar no Mac passou. Faltam 2 consertos pequenos no executor e no teste dele (A1 e A2). Depois deles o veredito esperado é PASS_PENDENTE_RECIBO. O Windows de verdade (AT-003 a AT-006 no CI), a decisão do piso (AT-007) e o Verify Gate do HEAD 9e2ad33 continuam sem prova.

## Tabela por AT

| AT | Sonda (log em sdd/reports/evidence/F16W_WINDOWS/) | Esperado | Observado | Resultado |
|---|---|---|---|---|
| AT-001 | AVAL-AT-001-fatias.log: `--lista --fatia I/N` para N=1..12, rodado 2 vezes, em python3 3.15 e em /usr/bin/python3 3.9.6 | fatias disjuntas que juntas dão tudo, iguais a cada execução, cobrindo os 82 módulos | 359 unidades. Para todo N: 0 duplicada, estável=sim, união=todas. Cobre 82 de 82 módulos, nos 2 Pythons | PASS |
| AT-001 | AVAL-AT-001-cobertura.log: ids do `discover` × ids carregados por cada unidade | nenhum teste perdido nem a mais | 2169 = 2169 nos 2 Pythons. 0 fora, 0 a mais. Peso igual ao nº de testes carregados em todas as unidades | PASS |
| AT-001/002 | AVAL-AT-001-002-falsa.log: pasta falsa com testes verde, pulado, falha+erro, import quebrado e um módulo pendurado com neto; `--teto-unidade 5 --saida` | uma linha por unidade com estado e contagens, nomes dos testes que caíram, total, VERMELHO e exit 1, `.log` por unidade e `resumo.tsv` | tudo presente. `test_pendura.P TETO` em 5,0 s com a cauda da saída, as outras unidades seguiram, 6 s no total, nenhum neto vivo depois | PASS |
| AT-001/002 | AVAL-AT-001-002-testes.log: `test_testes_por_modulo` em 3.15 e em 3.9.6 | verde | 9/9 OK nos 2 | PASS |
| AT-002 (uso) | AVAL-AT-002-uso.log, AVAL-AT-002-nan.log | toda chamada inválida sai 64 com `RESULTADO: ERRO DE USO` | 64 em 0/12, 13/12, 1/0, a/12, 1/12x, abc, -1, x, 0, módulo ou classe inexistente, pasta vazia ou inexistente, argumento desconhecido, valor faltando. Mas `--teto-unidade nan` e `inf` saem 1 com traceback (A1) | FALHA PARCIAL |
| AT-002 (árvore) | AVAL-SABOTAGEM-S1-neto.log: mutante que troca `os.killpg` por `pass` | o teste do teto cai | o teste passa e o neto `sleep(120)` fica vivo (A2). O produto mata a árvore (sonda da linha acima), mas o teste não prova isso | FALHA PARCIAL (prova) |
| AT-003 | AVAL-AT-003-workflows.log: diff do job nos 2 workflows, campos, SHA, `test_release_workflow` | windows-latest, Git Bash e Python nativo afirmados, matriz com fail-fast false, `--fatia i/12`, tetos, artefato por SHA, mesmo N, publish-gate numa fatia só | job igual nos 2 (só 1 linha em branco de diferença). Os 12 campos estão lá. `cf430e03…` = tag v7.0.2 (`git ls-remote`). Fora do `needs:` do release. 32/32 OK | PASS (texto) · NAO_VERIFICADO (rodar no CI) |
| AT-004 (Mac) | AVAL-AT-004-mac.log: os 5 testes de rede pendurada, um a um (3.9.6 + bash 3.2) | sem `SEM_SINAL`, verdes, t ≤ 12 s | 0 `SEM_SINAL` em test_checar.py. Os 5 OK, ~11 s cada (o de 2 subtests: 20 s no total, ≤ 12 s por caso). TestVigiaNoWindows 3/3. Bloco do gh IGUAL nos 2 scripts. test_f16_textos 13/13 | PASS |
| AT-004 (gh) | AVAL-AT-004-gh-neto.log: gh falso que pendura com neto, contra `checar.sh` normal e contra `inventario.sh` | ≤ 12 s com a mensagem de hoje | checar 10,5 s ("o GitHub não respondeu em 10 s"). inventario 10,2 s ("gh: sem resposta"). 0 órfão | PASS |
| AT-004 (Windows) | — | `taskkill /F /T` corta git.exe, ssh e askpass no Git Bash | sem CI. Só a simulação com /proc falso | NAO_VERIFICADO |
| AT-005 | AVAL-AT-005-006-mac.log | `ACHADOS` cita só testes que existem; os 4 rodam no job do Windows | `test_cada_achado_tem_teste_que_roda_no_job` OK. Os 4 testes OK no Mac. As 4 classes estão nas unidades da matriz | PASS (Mac) · NAO_VERIFICADO (log do Windows) |
| AT-006 | AVAL-AT-005-006-mac.log | nenhum skip de plataforma fora de `apoio.py`; cada quebra com destino | test_windows 9/9 OK. A busca manual só acha pulos de recurso (npm, gitleaks). Destino por causa: depende da medição do CI | PASS (estático) · NAO_VERIFICADO (quebras) |
| AT-007 | grep nas 4 frases; `git diff 0475445..HEAD -- README* docs/` | piso decidido pelo Roberto e aplicado | decisão ainda não tomada. As frases seguem "no automated tests yet" / "ainda sem teste automático", coerentes com nenhuma medição feita | PENDENTE (evento não ocorreu) |
| AT-008 | AVAL-AT-008-modulos-piso.log: 22 módulos tocados pela frente, pelo executor, em /usr/bin/python3 3.9.6 + /bin/bash 3.2. AVAL-AT-008-publish-gate-versoes.log | verdes no piso; publish-gate verde | 101 unidades, 666 testes, 0 falha, 0 erro, VERDE, 587 s. publish-gate GREEN na cópia de `git archive HEAD`. check-versions VERDE, 22 skills | PASS (parcial) · Verify Gate do HEAD sem recibo |

## ACHADOS

**A1 (BAIXA, contrato do AT-002).** `--teto-unidade nan` e `--teto-unidade inf` saem 1 com traceback, não 64 com `ERRO DE USO`.
- Reprodução: `python3 -B scripts/testes-por-modulo.py --teto-unidade nan --so test_windows` gera `ValueError: cannot convert float NaN to integer` em testes-por-modulo.py:232 (o `%ds` do cabeçalho), exit 1. Com `inf` vem `OverflowError`.
- Conserto: aceitar só valor finito (`math.isfinite(teto) and teto > 0`), senão `uso(...)`.

**A2 (MÉDIA, prova fraca do AT-002 "matar a árvore").** `test_teto_mata_a_arvore_e_segue` só verifica TETO e o tempo. Não verifica se o neto morreu.
- Reprodução: numa cópia de `git archive HEAD`, trocar `os.killpg(p.pid, signal.SIGKILL)` por `pass` e rodar `cd tests && python3 -B -m unittest test_testes_por_modulo.Executor.test_teto_mata_a_arvore_e_segue`. Resultado: OK, e `pgrep -f 'time.sleep\(120\)'` sobe de 1 para 2 (o neto ficou vivo). Log: AVAL-SABOTAGEM-S1-neto.log.
- Por que passou na sabotagem do build: ela tirava a chamada `matar_arvore(p)` inteira, então até o filho sobrevivia. Por isso o BUILD_REPORT diz "executor sem matar a árvore: morto" e isso exagera o que o teste prova.
- Conserto: o neto grava o próprio pid num arquivo, e o teste confirma com `os.kill(pid, 0)` que ele morreu.

**A3 (BAIXA, só no Windows).** A regra do relógio em `rc_do_vigia` usa `SECONDS`, que tem granularidade de segundo inteiro. Uma falha natural (rc 128) aos ~9,2 s reais vira 137 ("o vigia cortou").
- Reprodução: bloco do gh carregado com `SDD_CHECAR_PROC` falso marcando Windows, t0 tomado logo antes de um tique, `sleep 9.2`. Saída: `tempo real: 9.25 s; SECONDS - t0 = 10; rc_do_vigia 128 -> 137` (AVAL-AT-004-relogio.log).
- Efeito: no Windows, uma falha que termina entre 9 e 10 s e que nenhum texto conhecido classifica sai como "sem internet", não como o erro real. No gh, "deslogado" lento sai como "sem resposta".
- Saída sugerida: exigir `≥ 11` ou registrar em comentário.

**A4 (BAIXA).** Seleção vazia sai VERDE com 0 testes.
- Reprodução: `python3 -B scripts/testes-por-modulo.py --so ''` (ou `--so ,`, ou `--fatia 12/12` numa pasta com menos de 12 unidades) imprime `0 unidade(s)… RESULTADO: VERDE` e sai 0 (AVAL-AT-002-uso.log).
- Sugestão: seleção vazia vira 64. Não morde na matriz de hoje (359 unidades).

**A5 (BAIXA, documento).** O DEFINE v1.1 (AT-002, Success Criteria, Goals) ainda diz `--teto-modulo`. O executor rejeita essa opção com 64 ("argumento desconhecido: --teto-modulo") e usa `--teto-unidade`. O DESIGN v1.1 registra o desvio, mas o contrato não foi atualizado.

**Observação (risco A-002, não é defeito).** As fatias são equilibradas pelo nº de testes, não pelo tempo. Pela linha de base do Mac (medida com carga), a fatia 5 dá ~623 s e a 11 dá ~386 s. `test_sdd_open.Projeto` sozinho dá ≥ 450 s, e é limite inferior, porque o módulo já bateu no teto de 900 s na linha de base. Com o Windows várias vezes mais lento, é provável TETO na unidade (600 s) e/ou estouro dos 30 min do job nessas fatias. Log: AVAL-A-002-carga-fatias.log.

## Pendente de recibo (sem prova aqui)

1. **CI do PR no windows-latest:** as 12 fatias rodando, a tabela por unidade no log e os artefatos (AT-003); os 5 testes de rede verdes com t ≤ 12 s, o que prova o `taskkill` e a premissa A-001 (AT-004); os 4 achados (AT-005); o destino de cada quebra (AT-006). Roteiro para ler o run:
   - todas as fatias concluídas;
   - `test_checar.TestRemoto` e `TestFrente` OK;
   - grep de `TETO|FALHOU|ERRO` nas tabelas;
   - artefatos `testes-windows-fatia-1..12` com `resumo.tsv`.
2. **Decisão do piso pelo Roberto e as 4 frases** (AT-007).
3. **Verify Gate inteiro no HEAD 9e2ad33.** O que está rodando nesta máquina começou às 12:14 e fez `git archive` de ce3a779; a rodada 1 (9e2ad33, 12:27) não é coberta por ele. O log `VERIFY-GATE-ce3a779.log` ainda não tem rc.

## Evidência gravada

16 arquivos `sdd/reports/evidence/F16W_WINDOWS/AVAL-*.log`. Em cada um, a 1ª linha é `$ comando`, depois vem a saída verbatim e `[exit=N]`. Nenhum código nem documento do projeto foi editado. As fixtures ficaram no scratchpad.
>>>