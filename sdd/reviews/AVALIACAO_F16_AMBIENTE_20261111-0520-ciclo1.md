# AVALIACAO F16_AMBIENTE — ciclo 1

> Avaliador de contexto novo (subagente, sem a conversa do build), modo `veredito`, ciclo 1, sobre o HEAD `0a68960`.
> Bloco devolvido, gravado como veio (só a indentação do relato foi retirada).

<<<AVALIACAO
feature: F16_AMBIENTE · ciclo: 1 · HEAD avaliado: 0a68960 (branch feat/f16-ambiente, PR #25 em rascunho)
veredito: NEEDS_WORK

Resumo: provei os ATs por execução, com stubs em pastas temporárias e cópias de `git archive`. Os comportamentos de AT-001 a AT-005, AT-007 e AT-009 batem com o contrato. A nota é NEEDS_WORK por três motivos:
1. O Verify Gate do DEFINE sai 1 no HEAD.
2. O resolvedor de Python ignora o rc 9009, que o AT-006 nomeia.
3. O job Windows do caminho do aluno está vermelho no HEAD. As falhas incluem 9 testes do próprio resolvedor e testes que dependem de recurso que o Windows não tem, que falham em vez de serem pulados.

## Tabela por AT

| AT | Sonda (log em sdd/reports/evidence/F16_AMBIENTE/) | Esperado | Observado | Resultado |
|---|---|---|---|---|
| AT-001 | AVAL-AT001-AT002-checar-gh.log: `checar.sh` com PATH=/usr/bin:/bin (sem gh), uname Darwin/MINGW64/Linux, com remoto do GitHub e sem remoto; `--frente` | ⚠️ com o comando do sistema e rc 0; `--frente` não cita `gh` | ⚠️ "O programa do GitHub para o terminal (gh) não está instalado…" com `brew install gh` / `winget install --id GitHub.cli -e` / link do Linux; rc=0 nos 3 sistemas. `--frente`: ✅, 0 ocorrências da palavra gh, rc 0 (com remoto) ou 1 (sem remoto, 🔴 de remoto) | PASS |
| AT-002 | mesmo log: stubs gh-logado, gh-deslogado, gh-lento (30 s) × remoto GitHub (insteadOf → bare local) / sem remoto / gitlab; `--frente` com stub | deslogado ⇒ ⚠️ com `gh auth login`; logado ⇒ nenhuma linha; teto ⇒ "não deu para conferir", sem 🔴; fora do GitHub ⇒ o stub não é chamado | logado: só ✅, 1 chamada `gh auth status --hostname github.com`. Deslogado: ⚠️ com `gh auth login (GitHub.com → HTTPS → Yes → …)` nos dois casos. Lento: ⚠️ "não respondeu em 10 s", 10–11 s no total, rc 0. Gitlab: 0 chamadas ao stub nos 3 casos. `--frente`: 0 chamadas | PASS |
| AT-003 | AVAL-AT003-editor.log: `checar.sh --editor` com SDD_CHECAR_EDITOR_PATH, SDD_APPS_DIRS e LOCALAPPDATA falsos; resumo do modo normal. AVAL-AT003-manual-mac.log: o comando detectado abre uma pasta neste Mac | ordem do PATH; `open -a "<App>"` + dica no macOS; `.cmd` do %LOCALAPPDATA% no Windows; vazio ⇒ rc 1; resumo cita o editor; sem editor, nenhum ⚠️ | cursor vence zed; code vence a lista; os 9 nomes funcionam. VS Code, Cursor, Windsurf, Zed e Sublime ⇒ `open -a`, com dica só nos 3 que têm comando. Windows: code.cmd antes de cursor.cmd, pelo caminho entre aspas. Nada ⇒ rc 1 e saída vazia. Resumo: "…, editor code" / "…, editor open -a "Visual Studio Code""; sem editor, nenhum ⚠️. Manual: `open -a "Visual Studio Code" -g <pasta>` exit 0 e processo presente. Ressalva no achado 4 | PASS |
| AT-004 | AVAL-AT004-inventario.log: `inventario.sh` com stubs ausente/ok/deslogado/lento/erro de rede; diff do bloco `gh_estado` entre os 2 scripts; leitura do Passo 0/6 da SKILL | exatamente 1 linha `gh:` com os 4 valores; Passo 0 avisa, com "instalar agora" e "depois", sem parar; Passo 6 retoma | `gh: ausente` / `ok` / `deslogado` / `sem resposta` (10 s) / `sem resposta` (rede), 1 linha em cada caso, rc 0. As cópias (38 linhas) são IGUAIS. O Passo 0 traz as 3 opções e "não pare"; o Passo 6 refaz a checagem | PASS |
| AT-005 | leitura executada da SKILL da new-session (Passos 2.5, 3.4 e 3.5); hash dos blocos INSTALAR nas 3 skills; `test_agnostico` e `test_f16_textos` na suíte | modo terminal em 3 passos; última linha em 2 formas; slot usado como está; tabela igual nas 3 | os 3 blocos têm o mesmo sha `cff50036144b`; texto conforme; `test_agnostico` passou no Verify Gate. Prova manual do modo terminal: não há log de sessão real (ver NAO_VERIFICADO) | PASS (texto) |
| AT-006 | AVAL-AT006-python.log: `ledger-revisao-lint.sh` real (cópia de archive) com stubs no PATH; `docs-extract-decisions.sh`, `governanca-fronteira.sh`, `sdd-open.sh init`; calço visto por exec, env, shebang e bash -c | o 1º Python que roda e é ≥3.9; o que "sai 9009 ou não imprime versão" é pulado; nenhum serve ⇒ causa certa, sem traceback; quem não precisa segue | Store (msg no stderr) + python ⇒ roda com python. `py -3` ok. 3.8 ⇒ passa ao próximo. `SDD_PYTHON` com espaço ok. Só Store ⇒ "existe, mas não roda" + contrato do script (rc 64). Só 3.8 ⇒ "é o Python 3.8". exigir ⇒ 🛑 + `RESULTADO: PAROU` + rc 64. TMPDIR sem escrita ⇒ causa do calço. `init --vendors codex` segue (rc 0); `--vendors claude` para com a causa. O calço vale para exec, env, shebang e bash -c. **Falha:** a Store que escreve a mensagem no stdout e sai 9009 é aceita (achado 2) | FAIL parcial |
| AT-007 | AVAL-AT009-workflows-diff.log, grep nos 2 workflows e nas 4 frases; `gh run view` (só leitura) | job `testes-windows` nos 2 workflows, windows-latest, bash, setup-python, publish-gate ci e os 5 módulos com `-v`, teto 30, fora do `needs:`, sem continue-on-error; frases "sem teste automático" | tudo presente; `needs: [testes, testes-macos]`; 4 frases em 2 idiomas dizem "sem teste automático"; diff contra 36d0454 só acrescenta linhas | PASS |
| AT-008 | Verify Gate (`test_windows` verde aqui); log do job Windows do HEAD (AVAL-ci-windows-0a68960.log) | pulo por recurso só pela constante; os 5 achados listados; o do CRLF roda no job | local verde. No Windows: 136 testes, 116 ok, 11 FAIL, 9 ERROR, **0 skipped**. Testes que dependem de recurso ausente falham em vez de serem pulados (achado 3) | PASS local / FAIL no job |
| AT-009 | Verify Gate (suíte inteira, `SDD_TEST_BASH=/bin/bash`); diff dos workflows | matriz, `init`/`sync` e tetos 45/60 intactos; suíte verde no bash 3.2 | tetos e jobs Ubuntu/macOS sem mudança; matriz e init verdes. **Suíte: 1925 testes, 1 FAIL ⇒ EXIT=1** (achado 1) | FAIL |
| Verify Gate | AVAL-verify-gate-0a68960.log (comando exato do DEFINE) | exit 0 | publish-gate GREEN; unittest `Ran 1925 … FAILED (failures=1, skipped=1)`, EXIT=1 | FAIL |

Mutantes próprios, em cópia de archive (AVAL-mutantes-proprios.log, AVAL-mutante-MA2.log):
- 6 mortos: MA2 (o `--frente` consulta o gh), MB, MC, MD, ME (teto 40 s) e MF (ordem do PATH).
- MA sobreviveu, mas é equivalente: o `--frente` nunca imprime o bloco ⚠️.

## ACHADOS

1. **ALTO — o Verify Gate sai 1 no HEAD 0a68960.**
   - O commit 0a68960 pôs a marca de classe na pergunta nova do Passo 0 da `sdd-iniciar-repo`. Com isso, o lint passa a contar 28 perguntas em 23 arquivos.
   - `tests/test_decisoes_lint.py:33-36` (`test_skills_do_pacote_27_perguntas`) ainda espera "27 pergunta(s) em 22 arquivo(s)".
   - Reprodução: `T=$(mktemp -d) && git archive HEAD | tar -x -C $T && cd $T && SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover -s tests -p test_decisoes_lint.py -k AlvosReais` ⇒ `AssertionError: '27 pergunta(s) em 22 arquivo(s)' not found in '🟢 sdd-decisoes-lint --sites: 28 pergunta(s) em 23 arquivo(s)…'`.
   - Log: AVAL-achado-decisoes-lint.log.
   - Os logs VERIFY-GATE-* do build são de commits anteriores (o de 30b5448 tem só o cabeçalho). O job "gate" do run 42981139991 deve cair no mesmo ponto: estava em andamento na leitura.

2. **MÉDIO — AT-006: um candidato que sai 9009 é aceito quando escreve qualquer coisa no stdout.**
   - `sdd_python_testa` (`sdd/bin/lib/python.sh`) ignora o rc. Ele só olha se o stdout está vazio ou é uma versão velha. Qualquer texto que não seja uma versão vale como Python bom.
   - O DEFINE define o atalho como o que "sai 9009 **ou** não imprime versão". O stub de teste (`ATALHO = "#!/bin/sh\nexit 9009\n"`) não imprime nada, por isso não cobre o caso.
   - Reprodução: num PATH com `python3` = `#!/bin/sh` + `echo "Python was not found; …"; exit 9009` e com `python` válido, rodar `bash sdd/bin/ledger-revisao-lint.sh sdd/reviews/LEDGER_REVISAO_F16_AMBIENTE.md` ⇒ rc=49, stdout "Python was not found…". O script fez `exec` no atalho e não usou o `python` (caso F de AVAL-AT006-python.log).
   - Conserto sugerido: exigir rc 0 e versão no formato `^[0-9]+\.[0-9]+$`, mais um teste com a mensagem no stdout.

3. **MÉDIO — o job `testes-windows` (caminho do aluno) está vermelho no HEAD, sem pulo nem classificação.**
   - Run 42981139991, job 130391596284: `Ran 136 tests … FAILED (failures=11, errors=9)`, 0 skipped. Log: AVAL-ci-windows-0a68960.log.
   - 9 das quebras são do `test_python_resolver`, o módulo do AT-006. Exemplos: `test_vale_para_exec` com rc 49 (o atalho rodou) e `test_atalho_da_store_e_python_nativo_usa_o_python` com ValueError. A causa provável é do harness: `roda_script` monta `PATH=str(bin)+":"+str(ferr)` com caminhos `C:\…` separados por `:`. Até ser conferido, não há prova verde do resolvedor no Windows.
   - Pelo AT-008, recurso ausente deveria virar `skipIf`. Exemplo: `test_inventario.test_nome_com_aspas_e_barra` cai com `OSError [WinError 123]`, porque o Windows não aceita `"` em nome de arquivo, e não é pulado.
   - `test_checar.TestSomenteLeitura.test_nao_grava_nada` acusa uma entrada `app\nul` nova no projeto depois do `checar.sh`. Pode ser escrita no projeto do aluno no Windows, o que contraria o "só lê". Precisa ser medido.
   - Outros 6 do `test_checar` e do `test_inventario` comparam caminho `/c/…` com `C:\…` ou dependem de `sh -c 'sleep 60'` / askpass.
   - O DEFINE trata o job como informativo e pede a contagem no relatório. Mesmo assim, o Goal MUST ("conserto com teste para o que for defeito do pacote") e o AT-008 não estão cumpridos no subconjunto que esta frente mede. Ainda não há BUILD_REPORT com essa contagem.

4. **BAIXO — AT-003: a ordem entre pastas de apps segue a pasta, não a lista de apps.**
   - Com Zed.app na 1ª pasta e Visual Studio Code.app na 2ª, sai `open -a "Zed"`. O texto do AT lista os apps em ordem ("VS Code, Cursor, …, em /Applications ou ~/Applications").
   - Reprodução: `SDD_CHECAR_EDITOR_PATH=<vazio> SDD_CHECAR_UNAME=Darwin SDD_APPS_DIRS="A:B" bash checar.sh --editor`, com `A/Zed.app` e `B/Visual Studio Code.app`.
   - É ambíguo. Vale decidir e fixar num teste.

5. **BAIXO — os calços do Python não são apagados.**
   - Cada processo de topo que usa o fallback deixa uma pasta `sdd-python.XXXXXX` em `$TMPDIR`. Minha sonda deixou 7 por rodada (as minhas, eu apaguei). Depois do Verify Gate ficou 1.
   - O DESIGN aceita isso como consequência. No Windows, o uso diário acumula pastas sem limite.

6. **BAIXO — o slot `editor` do YAML com aspas internas.**
   - A new-session grava o editor descoberto no slot. Agora ele pode ser `open -a "Visual Studio Code"` ou `"C:/…/code.cmd"`, mas a SKILL não diz como escrever esse valor no YAML.
   - O exemplo do Passo 2.6 usa aspas duplas. `editor: "open -a "Visual Studio Code""` é YAML inválido.
   - Os scripts do pacote leem o config por linha, então hoje nada quebra.

## NAO_VERIFICADO

- Modo terminal da `sdd-new-session` numa sessão real: não há log, e eu não rodei a skill como agente. Roteiro:
  1. Repo temporário com remoto bare local.
  2. Slot `editor: ""`, com PATH e apps sem editor (`SDD_CHECAR_EDITOR_PATH=/var/empty`, `SDD_APPS_DIRS=/var/empty`).
  3. Pedir "/sdd-new-session teste".
  4. Conferir que o Próximo passo traz 1. terminal novo, 2. `cd "<pasta>"`, 3. `claude`/`codex`, e que a última linha é "⚠️ Continue num terminal novo aberto na pasta da frente…".
  5. Repetir com o slot `open -a "Cursor"` e conferir que o comando usado é `open -a "Cursor" "<pasta>"`.
- CI do HEAD: o "gate" (Ubuntu) e o "Testes no piso (macOS)" do run 42981139991 estavam em andamento. O run anterior (2f556fb) teve o macOS vermelho (5 testes, corrigidos depois segundo os commits). A Release e o `SHA256SUMS.txt` ainda não existem.

## Logs gravados
Todos em sdd/reports/evidence/F16_AMBIENTE/: AVAL-verify-gate-0a68960.log, AVAL-AT001-AT002-checar-gh.log, AVAL-AT003-editor.log,
AVAL-AT003-manual-mac.log, AVAL-AT004-inventario.log, AVAL-AT006-python.log, AVAL-AT009-workflows-diff.log, AVAL-ci-windows-0a68960.log,
AVAL-mutantes-proprios.log, AVAL-mutante-MA2.log, AVAL-achado-decisoes-lint.log.

Não editei nenhum código nem documento do projeto. Efeito colateral: a sonda manual abriu uma janela do VS Code numa pasta temporária.
>>>
