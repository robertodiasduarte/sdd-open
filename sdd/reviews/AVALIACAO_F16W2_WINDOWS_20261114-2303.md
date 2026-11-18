<<<AVALIACAO
feature: F16W2_WINDOWS · ciclo: 1 · HEAD: 3ba89de (branch feat/f16w2-windows, ainda sem push e sem PR) · base de comparação: ad32fe1 (v2.16.0)
veredito: NEEDS_WORK

Resumo: tudo o que dá para provar no Mac funciona. Cada correção foi rodada contra a v2.16.0, num emulador de Windows feito para isso: a base quebra e o HEAD acerta. O Verify Gate está verde. O veredito é NEEDS_WORK por um único motivo: o gate do AT-003 promete um teste no Mac com `ntpath` para os caminhos que nascem no Python. Esse teste não existe. Desfiz duas das correções de caminho e a suíte continuou verde (A1). Corrigido o A1, o veredito esperado é PASS_PENDENTE_RECIBO. O recibo que falta é o log do CI do PR no Windows (AT-008 e a parte Windows dos AT-003, 005, 006, 007 e 009), que hoje não existe.

Emuladores usados nas sondas, todos no scratchpad:
- `emul.py` (como `python3` no PATH): imita o Python nativo do Windows num pipe. A saída sai em cp1252 com "\r\n", o PYTHONIOENCODING é ignorado (como com -I), e o programa lido do stdin é decodificado em UTF-8, como faz o tokenizer.
- `winpath_run.py`: troca o `os.path.join` do script pelo `ntpath.join` e aceita "\" como separador nos caminhos.
- Armadilha no PATH: 63 programas falsos que anotam o próprio nome e repassam ao de verdade. O git é contado por GIT_TRACE.
- Windows falso para o `checar`: `gh` e `git ls-remote` que penduram com um neto que ignora TERM, um `taskkill` que deixa o processo cortado sair 0 (como no Cygwin) e um /proc falso com `winpid` (SDD_CHECAR_PROC).
- `aud.py`: um Python sem `os.O_NOFOLLOW`, com audit hook que anota todo nome de arquivo criado.

| AT | sonda | esperado | observado | resultado |
|---|---|---|---|---|
| AT-001 | Os 10 scripts nomeados com `PYTHONIOENCODING=cp1252 PYTHONUTF8=0`, base × HEAD (AVAL-AT-001.log). Guarda independente sobre o MANIFEST (AVAL-AT-001-guarda.log). `report-lint --stdin` no emulador (AVAL-AT-001-stdin.log). Guarda sabotada (AVAL-guardas-sabotagem.log). | ✅, → e "ç" saem sem erro; o exit é o mesmo de antes; a guarda pega o `.py` sem a troca | Na base, 6 scripts caem com UnicodeEncodeError. No HEAD, 0, e todos imprimem UTF-8. O exit é igual com e sem cp1252 (design 0, report 1, handoff 1). 20 de 21 `.py` com `__main__` têm a troca; a exceção é `validate_reverse.py`, ver A2. Pelo caminho e pelo `--stdin`, o `report-lint` dá a mesma saída. As 3 sabotagens fazem a guarda reprovar. | PASS, com a ressalva A2 |
| AT-002 | 19 heredocs `<<'PY'` examinados (todos começam pela troca; na base, 1 de 19). No emulador, base × HEAD: `slot.sh` (com valor ASCII, com ✅, e sem a rede local de tirar `\r`), `sdd-decisoes-lint --self-test`, `design-lint` chamado direto, e os 9 `--self-test` de `sdd/bin` (AVAL-AT-002.log, AVAL-AT-002-varredura.log). Diff do `python.sh`. | Saída UTF-8 com `\n` também com -I; reserva e pre-commit exportam UTF-8; o calço continua transparente | Na base, o slot ASCII diz "vazio: PULADO" (rc 11), o slot com ✅ dá INCONCLUSIVO (rc 3), e `decisoes-lint` e `sdd-fluxo` ficam VERMELHOS. No HEAD dá OK (rc 0) mesmo sem a rede local, e tudo fica VERDE. O `python.sh` só mudou num comentário, e o calço segue `exec %s "$@"`. Os 15 scripts com reserva exportam o PYTHONIOENCODING, e o pre-commit também. | PASS (Mac, emulado) |
| AT-003 | `alarme.sh verificar` com `core.hooksPath=C:/…/sdd/hooks`, e a pasta `C:` como link para / (AVAL-AT-003-hookspath.log). `sdd-archive` com `ntpath.join`, base × HEAD (AVAL-AT-003-archive-ntpath.log). Busca por `os.popen`. Mutação dos consertos (AVAL-AT-003-sem-guarda.log). | Uma forma só de caminho; `C:` reconhecido; raiz do git sem cmd.exe; teste no Mac com ntpath | Com o hooksPath em C:, a base diz OUTRO (rc 2) e o HEAD reconhece os hooks do sdd-open (rc 0); o controle com outra pasta segue OUTRO. Com caminhos de Windows, a base deixa tudo "Recentes, quieto há 0 dia" e não arquiva nada; o HEAD acha os 4+1 arquivos certos. Não sobrou nenhum `os.popen`: o `report-lint` usa `subprocess.run(["git","rev-parse",…])`. **Mas nenhum teste usa ntpath, e as duas correções desfeitas passam em 60 testes (A1).** | NEEDS_WORK (comportamento certo; o gate de teste do Mac não existe). Windows real: NAO_VERIFICADO |
| AT-004 | `init --vendors claude,codex` e o 1º commit de 629 arquivos sob a armadilha, base × HEAD, com higiene on e off (AVAL-AT-004-contagem.log). 15 casos de recusa e 12 casos de borda × 2 hooks × higiene on/off (AVAL-AT-004-recusas*.log). Fidelidade do init: o renderizador novo × o velho sobre os mesmos arquivos (AVAL-AT-004-init-fidelidade.log). | No máximo 3 programas por arquivo; init com no máximo metade dos processos; as mesmas recusas | Commit: base 12,2 a 14,2 por arquivo; HEAD 0,20 por arquivo (132 ao todo, git incluído). Init: 5041 → 1015 processos (20%). As recusas são idênticas nos dois hooks em todos os casos (CPF, CNPJ, pfx, p12, pem com chave, .env, .env.local, .ENV, xlsx, csv, credencial em json/yml/ini, NUL, nomes maiúsculos, nome com acento e espaço). Os controles passam. O init do HEAD e o do híbrido saem byte a byte iguais (630 arquivos, os mesmos 20 executáveis, o mesmo hooksPath). | PASS |
| AT-005 | `checar.sh` normal e `--frente`, com e sem askpass; ls-remote e gh pendurados com neto (AVAL-AT-005.log). Windows falso com taskkill que sai 0 (AVAL-AT-005-windows-emulado.log). Igualdade das funções entre os dois scripts (AVAL-AT-005-igualdade.log). | Responder em até 12 s; o vigia anuncia o corte; `gh_estado` igual nos dois scripts | No Mac, base e HEAD levam 10 a 11 s. No Windows falso, a base leva 30 a 31 s e erra: diz "remoto sem commit" e "gh deslogado". O HEAD leva 11 s e diz "sem resposta" nos dois. `corta`, `marca_nova` e `gh_estado` são IGUAIS; `rc_do_vigia` aparece 0 vezes. | PASS (Mac, emulado). Windows real: NAO_VERIFICADO |
| AT-006 | O Verify Gate (inclui `test_windows.py`) | O arnês roda sem defeito próprio | Verde no Mac. O ramo de Windows de `path_restrito` e `falso` só roda no Windows. | Mac PASS. Windows: NAO_VERIFICADO |
| AT-007 | `--self-test` de `sdd-drive` e `playbook-curator` com TMPDIR vazio, sem O_NOFOLLOW e com audit de nomes. Trava como link para fora do repo em `sdd-drive iniciar` (AVAL-AT-007*.log). | Verde, sem nome proibido, sem sobra; a trava-link é recusada sem criar nada fora | Base e HEAD verdes, 0 sobras. A base cria `BUILD_REPORT_qu"o te.md` (proibido no Windows); o HEAD não cria nenhum nome proibido. Trava-link sem O_NOFOLLOW: a base **cria `criado-fora.lock` fora do repo** e segue (rc 10); o HEAD recusa ("a trava é um link"), rc 2, sem criar nada. | PASS (Mac, emulado). Os 4 achados guardados no job Windows: NAO_VERIFICADO |
| AT-008 | Não há push, PR nem run. O BUILD_REPORT está PENDENTE, e o README ainda diz "about 64%". | Medição no CI do PR; tabela por módulo; piso e frases | Ainda não executável | NAO_VERIFICADO (recibo do CI) |
| AT-009 | Verify Gate com /bin/bash 3.2.57 e /usr/bin/python3 3.9.6 (AVAL-verify-gate.log) | A suíte segue passando no piso do macOS e no Ubuntu | publish-gate ok; Ran 2199 tests em 1454 s, OK (skipped=2), rc=0. Não há Linux aqui (o daemon do docker está parado). | macOS PASS. Ubuntu: NAO_VERIFICADO |

Roteiro do que falta (NAO_VERIFICADO), para o CI do PR:
1. Abrir o PR e conferir o job `testes-windows` nas 16 fatias: nenhuma no teto de 600 s; proporção de testes que passam ≥ 95% (meta 100%).
2. No log, conferir: `test_alarme` (hooksPath em C:\), `test_governanca_fronteira`, `test_sdd_archive`, `test_gate_baseline`, `test_checar` (os 3 casos do vigia), `test_sdd_open` e os 4 achados guardados (tasklist, report-lint, sdd-archive, O_NOFOLLOW) verdes ou pulados por constante com motivo.
3. Conferir Ubuntu e macOS verdes no mesmo run.
4. Pôr no BUILD_REPORT a tabela por módulo, antes × depois. Com a decisão do Roberto, ajustar os 2 workflows e as 4 frases (README EN/PT, quickstart EN/PT).

ACHADOS

A1 (média, bloqueia o gate do AT-003): o teste no Mac com `ntpath` que o DEFINE promete não existe, e as correções de caminho do Python ficam sem guarda no Mac.
Reprodução:
```
T=$(mktemp -d); git -C /Users/robertoduarte/rdd-worktrees/sdd-open-f16w-windows archive HEAD | tar -x -C $T; cd $T
sed -i '' 's|        base = "sdd/" + sub   # F16W2.*|        base = os.path.join("sdd", sub)|' sdd/bin/sdd-archive.py
sed -i '' 's|            cam = pasta + "/" + c if pasta else c   # F16W2.*|            cam = os.path.join(pasta, c) if pasta else c|' sdd/bin/test-baseline.sh
cd tests && SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest test_sdd_archive test_test_baseline test_f16w2_caminhos test_f16w2_saida   # → Ran 60, OK
grep -rln ntpath .   # → vazio
```
O DEFINE diz, no AT-003: "Gate: test (Mac, com `ntpath` onde o caminho é do Python)". O DESIGN, na Testing Strategy, diz: "sdd-archive e test-baseline com ntpath". O `test_f16w2_caminhos.py` tem 1 teste só, do slot com CR. Sem esse teste, uma regressão só aparece no job Windows, que é informativo. A prova de comportamento existe (AVAL-AT-003-archive-ntpath.log mostra a base errando e o HEAD certo), mas não há teste que a repita. O caminho: um teste que rode o `sdd-archive.py` e a parte de vizinhos do `test-baseline` com `os.path.join` trocado por `ntpath.join`, com linha de base vermelha em ad32fe1.

A2 (baixa, desvio de contrato não registrado): `validate_reverse.py` foi isento da troca para UTF-8 (`CONGELADOS` em `tests/test_f16w2_saida.py:19`, commit a0ee4a5, congelado por SHA-256). O AT-001 diz "Todo script … shall", e o DEFINE v1.2 não registra a exceção.
Reprodução: `/usr/bin/python3 <scratchpad>/guard.py <cópia HEAD>` (AVAL-AT-001-guarda.log) → `ATENCAO validate_reverse.py SEM reconfigure`.
Impacto prático pequeno: a saída é JSON em ASCII, que cp1252 codifica, então só sai `\r\n` no Windows. O caminho: uma linha de exceção no DEFINE, ou a decisão do Roberto.

A3 (baixa, texto desatualizado): o comentário em `sdd/bin/slot.sh` (`LIDO="${LIDO//$'\r'/}"   # … o calço do Windows já tira o \r …`) descreve a v1.1. Desde a Decision 2 revista, o calço é transparente e não tira mais nada.
Reprodução: `grep -n 'calço do Windows já tira' sdd/bin/slot.sh`.

A4 (baixa, cosmético): `bin/sdd-open.sh:811` (`pyv="$(python3 -I -c '…print(…)')"`) e as mensagens de `saida=$(python3 -I -c …)` nas linhas 519 e 537 não trocam o `newline`. No Windows, o doctor imprime "python3 3.12\r" (invisível no terminal). Nada é comparado com esse valor.
Reprodução: `sed -n 811p bin/sdd-open.sh`. Pelo emulador: `PATH=<winpy>:$PATH bash bin/sdd-open.sh doctor | od -c | grep '\\r'`.
>>>
