# Avaliação de contexto novo — F16W_WINDOWS, ciclo 2

> Bloco devolvido pelo avaliador (subagente em contexto novo, modo veredito), verbatim.

<<<AVALIACAO
FEATURE: F16W_WINDOWS · ciclo 2 · HEAD avaliado: c65e658 (branch feat/f16w-windows). Não há push, PR nem run de CI: `git ls-remote`, `gh pr list` e `gh run list` voltaram vazios (AVAL2-CI-estado.log).

## Veredito: PASS_PENDENTE_RECIBO

Tudo o que dá para provar no Mac passou. Os achados do ciclo 1 ficaram assim:
- **A1 (nan/inf):** consertado. Sai 64.
- **A2 (neto morto):** consertado. O teste agora derruba o mutante `killpg→pass`.
- **A3 (relógio):** não foi consertado; o limite foi registrado em comentário. Aceito.
- **A4 (seleção vazia):** consertado. Sai 64.
- **A5:** consertado. O DEFINE v1.2 usa `--teto-unidade`.

Nenhum achado novo bloqueia. Faltam 3 recibos:
- o CI do Windows (AT-003 a AT-006);
- a decisão do piso pelo Roberto (AT-007);
- o Verify Gate inteiro no HEAD c65e658, com a máquina livre.

## Tabela por AT
Os logs estão em `sdd/reports/evidence/F16W_WINDOWS/`.

| AT | Sonda | Esperado | Observado | Resultado |
|---|---|---|---|---|
| AT-001 | AVAL2-AT-001-fatias-py315.log e -py39.log: `--lista --fatia I/N` para N=1..16 e N=20, cada uma 2 vezes, em 3.15 e 3.9.6 | fatias disjuntas, união = todas, iguais a cada execução, cobrindo os 82+ módulos | 413 unidades, 99 delas em partes. Todo N: estável, disjuntas, união = todas. Cobre 82/82 módulos. A fatia 5/16 é igual nos 2 Pythons | PASS |
| AT-001 | AVAL2-AT-001-cobertura.log: ids do `discover` × ids que os alvos de cada unidade carregam | cada teste contado uma vez; classe com mais de 12 em partes | 2170 = 2170 nos 2 Pythons. 0 faltando, 0 a mais, 0 rodado 2 vezes. Peso = testes carregados em todas. Maior unidade: 12 | PASS |
| AT-001/002 | AVAL2-AT-001-002-falsa.log: pasta falsa com verde+pulado, falha+erro, import quebrado, classe de 30 testes com 1 falha, pendura com neto que anota tiques; `--teto-unidade 4 --saida`; stdout com `PYTHONIOENCODING=ascii` | linha por unidade, quedas nomeadas, total, VERMELHO e exit 1, `.log` por unidade e `resumo.tsv`, emoji sem quebrar, TETO e o neto morto | `G[1de3]/[2de3]/[3de3]` com 10 testes cada; `FAIL G.test_17` só na parte 2. `test_pendura.P TETO` em 4,0 s, com a cauda. As outras unidades seguiram; 4 s no total, exit 1. Tiques 20→20 em 2 s, 0 processo vivo. `🛑` saiu num stdout ascii. 7 `.log` + `resumo.tsv` | PASS |
| AT-002 (uso) | AVAL2-AT-002-uso.log, 30 chamadas | 64 + `RESULTADO: ERRO DE USO`, sem rodar | todas 64, 0 traceback, 0 rodou: fatia 0/16, 17/16, 1/0, a/16, 1/16x, -1/16, 1.5/16; teto nan, NaN, inf, -inf, 1e400, 0, -5, abc; paralelo 0, 1.5, x; `--so` inexistente, classe inexistente, `,`, vazio; pasta vazia ou inexistente; seleção vazia (`--fatia 2/2` numa pasta de 1 unidade); `--nada`; `--teto-modulo`. `--lista` de fatia vazia sai 0 | PASS |
| AT-002 (prova) | AVAL2-SABOTAGEM-executor.log: 6 mutantes numa cópia de `git archive HEAD` | o teste do executor cai em cada um | todos morreram: S1 killpg→pass, S2 sem `start_new_session`, S3 sem isfinite, S4 seleção vazia verde, S5 sem partes, S6 saída por pipe. O original passa | PASS |
| AT-001/002 | AVAL2-AT-001-002-testes.log | verde | 10/10 OK em 3.9.6 e em 3.15 | PASS |
| AT-003 | AVAL2-AT-003-workflows.log, AVAL2-AT-003-007-testes-texto.log | windows-latest, Git Bash e Python nativo afirmados, matriz com `fail-fast: false`, `--fatia i/N`, tetos, artefato fixado por SHA, mesmo N nos 2, publish-gate numa fatia só | Job igual nos 2 workflows (só 1 linha em branco de diferença). Matriz 1..16 e `/16` batem. Teto do job 30 min, teto da unidade 600 s. `if: matrix.fatia == 1`. `cf430e03…` = tag v7.0.2 (`git ls-remote`). Fora do `needs:` do release; sem `continue-on-error`; `contents: read`. 26/25 unidades por fatia. `test_release_workflow` 32/32 | PASS (texto) · NAO_VERIFICADO (rodar no CI) |
| AT-004 (Mac) | AVAL2-AT-004-mac.log: os 5 ex-`SEM_SINAL`, um a um, em 3.9.6 + bash 3.2 | sem `SEM_SINAL`, verdes | 0 `SEM_SINAL` no arquivo. Os 5 OK, ~11 s cada; o de 2 casos dá 20 s no total. TestVigiaNoWindows 3/3. TestGh pendurado OK | PASS |
| AT-004 (neto) | AVAL2-AT-004-neto.log: `git` falso cujo ls-remote deixa um neto segurando a saída; `gh` falso igual em `inventario.sh` | ≤ 12 s com a mensagem de hoje, sem órfão | `--frente` 10,57 s, normal 10,73 s ("Não consegui falar com example.invalid…"); inventario 10,14 s ("gh: sem resposta"); 0 órfão | PASS |
| AT-004 (Windows) | — | `taskkill /F /T` pelo winpid corta git.exe, ssh e askpass (A-001) | sem CI; só o /proc falso de TestVigiaNoWindows | NAO_VERIFICADO |
| AT-005 | AVAL2-AT-005-006-mac.log, AVAL2-AT-005-curator.log | `ACHADOS` cita só testes que existem; eles estão na matriz | Os 5 testes existem e caem nas fatias 13, 4, 8, 6 e 11 (report-lint na parte `ReportLint[1de2]`). Os 5 OK no piso | PASS (Mac) · NAO_VERIFICADO (log do Windows) |
| AT-006 | AVAL2-AT-005-006-mac.log, test_windows 9/9 | nenhum skip de plataforma fora de `apoio.py` | a busca só achou um texto de fixture dentro de test_windows.py:63; os outros pulos são de recurso (npm, gitleaks) | PASS (estático) · NAO_VERIFICADO (destino das quebras) |
| AT-007 | grep nas 4 frases | piso decidido e aplicado | as frases seguem "no automated tests yet"; a decisão ainda não foi tomada | PENDENTE (o evento não aconteceu) |
| AT-008 | AVAL2-AT-008-publish-gate-versoes.log, -checar-piso.log, -deploy-do-sha-sozinho.log | verde no piso | publish-gate GREEN na cópia de `git archive HEAD`. check-versions VERDE, 22 skills; MANIFEST tem os 2 arquivos novos. `test_checar` inteiro pelo executor no piso: 14 unidades, 88 testes, VERDE, 139 s. `test_deploy_do_sha` sozinho: 46 OK | PASS (parcial) · Verify Gate do HEAD sem recibo |

## ACHADOS (nenhum bloqueia)

**B1 (BAIXA, documento).** O BUILD_REPORT ficou para trás:
- diz "12 fatias" nas linhas 22, 92 e 132;
- não lista os commits 9e2ad33 e c65e658;
- a tabela de AT e o veredito do avaliador seguem PENDENTE.

O bloco de código do DESIGN também segue com `fatia: [1..8]` e `--teto-modulo`.
- Reprodução: `grep -n -E "12 fatias|8 fatias" sdd/reports/BUILD_REPORT_F16W_WINDOWS.md`; no DESIGN, a seção "Code Patterns", bloco yaml.

**B2 (RISCO, não é defeito).** A divisão em partes conta testes, não tempo:
- `test_claude_adapter.Projeto` tem 12 testes, então não se divide. Levou 154 s em série no Mac (tpm-piso do ciclo 1).
- Com o Windows ~4× mais lento (A-002), dá ≈ 616 s, acima do teto de 600 s. A unidade sairia TETO, e o tempo dela não seria medido.
- Pela minha estimativa, nenhuma fatia passa de ~260 s no Mac (fatia 11). Isso cabe nos 30 min do job, mesmo a ×4–5.
- Reprodução: `python3 -B <scratchpad>/aval2/carga16.py $PWD sdd/reports/evidence/F16W_WINDOWS/MAC-BASE-resumo.tsv <scratchpad>/tpm-piso/resumo.tsv`. Log: AVAL2-A-002-estimativa-16.log.

**B3 (MUITO BAIXA).** `--fatia 1/100000000000` faz o sistema matar o processo por memória (rc −9) em vez de sair 64. `1/1000000` responde normal. O contrato fala de "número que não é finito", então isto fica na borda.
- Reprodução: `python3 -B scripts/testes-por-modulo.py --lista --fatia 1/100000000000; echo $?`. Log: AVAL2-AT-002-n-enorme.log.

**B4 (BAIXA, comentário).** A linha 184 do executor diz que import quebrado vira `ERRO`. Na prática, o unittest devolve `FAILED (errors=1)`, e a unidade sai `FALHOU` com `ERROR _FailedTest.<modulo>` (AVAL2-AT-001-002-falsa.log). O contrato aceita os dois; só o comentário engana.

**Observação (Verify Gate).** O único log do gate, `VERIFY-GATE-ce3a779.log`, é de ce3a779 e saiu VERMELHO:
- 1 falha em `test_deploy_do_sha.Redisparo.test_passo_passageiro_na_ponta_repete_uma_vez`, que esperava rc 0 e veio rc 4 ("ainda não sei");
- a rodada inteira levou 2285 s, com a máquina carregada;
- o módulo sozinho, agora, passa: 46 OK em 32 s.

É teste de tempo sob carga, não regressão. Mesmo assim, o gate de c65e658 precisa rodar com a máquina livre.

**Observação (AT-007).** Depois do merge, o job do Windows passa a existir, como job informativo. A frase "ainda sem teste automático" fica imprecisa. Fica para a decisão do piso.

## Pendente de recibo
1. **CI do PR em windows-latest.** O que conferir no run:
   - as 16 fatias concluídas dentro dos 30 min;
   - a tabela por unidade no log;
   - os artefatos `testes-windows-fatia-1..16`, cada um com `resumo.tsv`;
   - `test_checar.TestRemoto[1de2]/[2de2]` e `TestFrente` OK com t ≤ 12 s, o que prova o `taskkill` e a A-001;
   - as 5 unidades de `ACHADOS` (fatias 4, 6, 8, 11, 13);
   - grep de `TETO|FALHOU|ERRO`, com atenção a `test_claude_adapter.Projeto` (B2).
2. Decisão do piso pelo Roberto e as 4 frases (AT-007).
3. Verify Gate inteiro em c65e658.

## Evidência gravada
São 15 logs `AVAL2-*.log` em `/Users/robertoduarte/rdd-worktrees/sdd-open-f16w-windows/sdd/reports/evidence/F16W_WINDOWS/`. Em cada um, a 1ª linha é `$ comando`; depois vem a saída verbatim e `[exit=N]`. Nenhum código nem documento do projeto foi editado. As sondas e fixtures estão em `/private/tmp/claude-501/-Users-robertoduarte-rdd-worktrees-sdd-open-f16w-windows/fd210694-ded6-4d95-a500-52e0521f4ae8/scratchpad/aval2/`.
>>>
