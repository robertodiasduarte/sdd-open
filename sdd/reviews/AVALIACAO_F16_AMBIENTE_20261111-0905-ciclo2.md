# AVALIACAO F16_AMBIENTE — ciclo 2

> Avaliador de contexto novo (subagente, sem a conversa do build), modo `veredito`, ciclo 2 (o último do teto), sobre o HEAD
> `28caf3a`. O brief levou só os campos do molde e os achados do ciclo 1, como estavam. Bloco devolvido, gravado como veio.

<<<AVALIACAO
feature: F16_AMBIENTE · ciclo: 2 · HEAD avaliado: 28caf3a (branch feat/f16-ambiente, PR #25 em rascunho)
veredito: PASS_PENDENTE_RECIBO

Resumo: provei cada AT por execução. Usei cópias de `git archive` do HEAD, stubs de `gh` e de Python e PATH sem Python. A saída de cada prova está em `sdd/reports/evidence/F16_AMBIENTE/AVAL2-*.log`.
- Os 6 achados do ciclo 1 estão resolvidos, cada um conferido de novo por execução.
- O Verify Gate do DEFINE sai 0: 1933 testes, mais que os 1.867 da base.
- O job `testes-windows` (caminho do aluno) está verde no CI do HEAD.

Falta recibo de três coisas:
- o job macOS do run 42987378256, que ainda estava rodando;
- o BUILD_REPORT com a contagem do Windows;
- a Release com o `SHA256SUMS.txt`, que é critério de sucesso e não AT.

## Tabela por AT

| AT | Sonda (log AVAL2-…) | Esperado | Observado | Resultado |
|---|---|---|---|---|
| AT-001 | AT001-003-checar.log: `checar.sh` com PATH=/usr/bin:/bin (sem gh); SDD_CHECAR_UNAME Darwin, MINGW64_NT e Linux; sem remoto e com remoto do GitHub; `--frente` | ⚠️ com o comando do sistema; rc 0; o `--frente` não fala do gh | ⚠️ "O programa do GitHub para o terminal (gh) não está instalado…", com `brew install gh`, `winget install --id GitHub.cli -e` ou o link do Linux; rc=0 nos 3 sistemas. `--frente`: só ✅, 0 chamadas ao gh, sem a palavra gh, rc 0 | PASS |
| AT-002 | mesmo log: stubs logado, deslogado e lento (30 s); remoto GitHub (insteadOf apontando para um bare local), sem remoto e gitlab; `--frente` com o stub deslogado | deslogado ⇒ ⚠️ com `gh auth login`; logado ⇒ nenhuma linha; teto ⇒ "não deu para conferir" e nenhum 🔴; gitlab ⇒ o gh não é chamado | logado: só ✅, 1 chamada `auth status --hostname github.com`. Deslogado (remoto GitHub e sem remoto): ⚠️ com `gh auth login (GitHub.com → HTTPS → Yes → Login with a web browser)`. Lento: ⚠️ "não respondeu em 10 s", cerca de 10 s, rc 0. Gitlab: 0 chamadas. `--frente`: 0 chamadas | PASS |
| AT-003 | mesmo log: `checar.sh --editor` com SDD_CHECAR_EDITOR_PATH, SDD_APPS_DIRS e LOCALAPPDATA falsos; resumo do modo normal | ordem do PATH; `open -a` com dica; `.cmd` do %LOCALAPPDATA%; vazio ⇒ rc 1; o resumo cita o editor | cursor vence zed; code numa pasta posterior do PATH vence cursor. **Zed em A e VS Code em B ⇒ `open -a "Visual Studio Code"`** (achado 4 resolvido). Zed e Sublime ⇒ Zed. Windows: code.cmd vence cursor.cmd, pelo caminho entre aspas, com dica. Linux sem nada: rc 1. Neste Mac, sem injeção: `open -a "Visual Studio Code"` com dica. Resumo: "…, editor open -a "Zed"" e "…, editor code" | PASS |
| AT-004 | AT004-inventario.log: `inventario.sh` com stubs ausente, ok, deslogado, lento e erro de rede; diff do bloco gh entre as 2 cópias; grep do Passo 0 e do Passo 6 | exatamente 1 linha `gh:` com os 4 valores; Passo 0 avisa sem parar; Passo 6 retoma | `gh: ausente`, `ok`, `deslogado`, `sem resposta` (11 s) e `sem resposta` (rede): 1 linha em cada caso, rc 0. Bloco IGUAL nas 2 cópias (38 linhas). SKILL: Passo 0 com "não pare", "instalar agora" e "depois"; Passo 6 refaz a checagem | PASS |
| AT-005 | leitura executada da SKILL da new-session (linhas 225-234 e 300-312); `test_f16_textos`, `test_agnostico` e `test_matriz_new_session` no Verify Gate; mutante M5 | modo terminal em 3 passos; última linha nas 2 formas; slot usado como está; tabela igual nas 3 skills | texto conforme; versões 1.5.0, 1.2.0 e 1.5.0; o Verify Gate verde cobre os 3 testes | PASS (texto) |
| AT-006 | AT006-python.log: `ledger-revisao-lint.sh`, `docs-extract-decisions.sh` e `test-baseline.sh` reais, com PATH sem Python e stubs | o 1º Python que roda e é ≥3.9 serve; o atalho (9009) é pulado; nenhum Python ⇒ causa certa, sem traceback | Atalho que escreve no **stdout** e sai 9009, mais python ⇒ VERDE com o python (achado 2 resolvido). Imprime "3.12" e sai 9009 ⇒ pulado. Atalho no stderr ⇒ pulado. 3.8 ⇒ passa ao próximo. `py -3` ok. `SDD_PYTHON=python3` sem laço. `SDD_PYTHON` com espaço ok. Só o atalho ⇒ "existe, mas não roda" mais o contrato de cada script (64 / PAROU 64 / INCONCLUSIVO 3). TMPDIR sem escrita ⇒ a causa do calço. Nenhum Python ⇒ 🛑, PAROU, 64. 0 tracebacks. Calço com mais de 1 dia apagado, o recente mantido (achado 5) | PASS |
| AT-007 | AT007-workflows.log: grep nos 2 workflows e nas 4 frases; diff contra 36d0454 | `testes-windows` em windows-latest, bash, setup-python, publish-gate ci, os 5 módulos com -v, teto 30, fora do `needs:`, sem continue-on-error; as 4 frases dizem "sem teste automático" | tudo presente nos 2 workflows; `needs: [testes, testes-macos]`; o diff só acrescenta linhas (0 removidas); as 4 frases em 2 idiomas dizem "sem teste automático" | PASS |
| AT-008 | ci-windows-28caf3a.log (run 42987378256, job 130411675429); Verify Gate local | pulo de plataforma só pela constante de `apoio.py`, com motivo; os 5 achados listados; o do CRLF roda no job | Windows: `Ran 144 tests … OK (skipped=8)`. Os 8 pulos são 5 por SEM_SINAL e 3 por SEM_NOME_ESPECIAL, com o motivo impresso. `test_pulo_de_plataforma_so_por_constante_do_apoio`, `test_cada_achado_tem_teste_que_roda_no_job` e `test_stdout_do_curator_sem_crlf` ok. Os 23 testes do resolvedor ok no Windows. `test_nao_grava_nada` ok (achado 3 resolvido). Job de 4m36s, teto 30 | PASS (ressalva no achado A) |
| AT-009 | Verify Gate com SDD_TEST_BASH=/bin/bash; diff dos workflows | matriz, init/sync e tetos 45/60 intactos; suíte verde no bash 3.2 | tetos 45 e 60 e os jobs Ubuntu e macOS sem mudança; suíte inteira verde (linha abaixo) | PASS |
| Verify Gate | verify-gate-28caf3a.log (comando exato do DEFINE) | exit 0 | publish-gate GREEN; `Ran 1933 tests in 1523.198s — OK (skipped=1)`; EXIT=0 | PASS |

Achados do ciclo 1, conferidos de novo:
1. Resolvido: o Verify Gate sai 0; `test_decisoes_lint` está verde.
2. Resolvido: o atalho com texto no stdout e rc 9009 é pulado. O mutante M1 (o rc volta a ser ignorado) morre em `test_candidato_que_imprime_versao_e_sai_com_erro_nao_serve`.
3. Resolvido: o job Windows está verde (144 testes, 8 pulos com motivo). `app\nul` era do harness (os.devnull); o `test_nao_grava_nada` passa no Windows.
4. Resolvido: a ordem da lista de apps vence a ordem das pastas. O mutante M4 morre em `test_a_ordem_da_lista_de_apps_vence_a_ordem_das_pastas`.
5. Mitigado: o calço com mais de 1 dia é apagado (caso K da sonda). O mutante M3 morre em `test_calco_velho_sai_e_o_novo_fica`.
6. Resolvido: a SKILL manda as aspas simples. O YAML `editor: 'open -a "Visual Studio Code"'` é lido como `open -a "Visual Studio Code"`; a forma antiga dá erro de sintaxe. O `slot.sh` roda normal com esse config. O mutante M5 morre em `test_f16_textos`.

Mutantes do ciclo 2 (mutantes.log), em cópia de archive: 5 de 5 mortos (M1 a M5, acima). O M2 (qualquer texto vale como versão) morre em `test_candidato_que_imprime_lixo_nao_serve`.

## ACHADOS

A. **BAIXO — 5 testes de rede pendurada do `checar.sh` são pulados no Windows. O pulo esconde um defeito do pacote, que só está registrado em comentário.**
   - Os 5 testes são `test_rede_pendurada_inteira_api_e_remoto`, `test_ssh_pendurado_vigia`, `test_login_do_editor_esperando`, `test_rede_parada_com_editor_nao_e_janela_de_login` e `TestFrente.test_frente_bloqueia_login_do_editor`.
   - O pulo usa `@unittest.skipIf(*SEM_SINAL)`, com o comentário `# F16: no Windows o vigia não mata o grupo; o conserto é a F16W`. A mensagem do commit d556851 diz "defeito conhecido".
   - O AT-008 aceita o motivo "sinal POSIX". Mas a consequência para o aluno no Windows é um defeito do pacote: um ssh ou askpass pendurado pode passar do teto no `checar.sh` e no pré-voo `--frente`. O Goal MUST diz "conserto com teste para o que for defeito do pacote".
   - O DEFINE só manda para a F16W 4 dos 5 achados guardados; este é novo.
   - Reprodução: `grep -n 'SEM_SINAL' tests/test_checar.py`, e as linhas `skipped 'sinal POSIX…'` em AVAL2-ci-windows-28caf3a.log.
   - Pedido: registrar no BUILD_REPORT e no escopo da F16W como defeito conhecido, não só como recurso ausente.
   - Não medi o travamento real num Windows (ver NAO_VERIFICADO).

B. **BAIXO (observação, não executei) — a limpeza do calço apaga pelo tempo da pasta.**
   - A limpeza (`find … -mmin +1440 -exec rm -rf`) não confere se o processo dono do calço ainda está vivo.
   - Um processo que rode mais de 24 h e chame `python3` depois disso perderia o calço (ex.: `sdd-drive` em laço).
   - Caso raro. Basta registrar.

## NAO_VERIFICADO

- O job "Testes no piso (macOS)" do run 42987378256 (HEAD 28caf3a) estava em andamento na última leitura; o job "gate" (Ubuntu) já tinha terminado em success.
- O BUILD_REPORT com a contagem do Windows (144 rodados, 8 pulados com motivo, 0 falhas, 4m36s) ainda não existe. A Release e o `SHA256SUMS.txt` também não; são critério de sucesso.
- Modo terminal da `sdd-new-session` numa sessão real de agente. O roteiro do ciclo 1 continua valendo: (1) repositório temporário com remoto bare; (2) `editor: ""`, com `SDD_CHECAR_EDITOR_PATH=/var/empty` e `SDD_APPS_DIRS=/var/empty`; (3) pedir "/sdd-new-session teste"; (4) conferir os 3 passos e a última linha "⚠️ Continue num terminal novo…"; (5) repetir com o slot `open -a "Cursor"`.
- Comportamento real do `checar.sh` no Windows com ssh ou askpass pendurado (achado A).
- `${0//\\//}` com caminho do Windows: não dá para simular no macOS. A evidência é indireta: os testes do resolvedor passam no job Windows.

## Logs gravados (sdd/reports/evidence/F16_AMBIENTE/)
AVAL2-verify-gate-28caf3a.log, AVAL2-AT001-003-checar.log, AVAL2-AT004-inventario.log, AVAL2-AT006-python.log, AVAL2-AT007-workflows.log,
AVAL2-achado6-yaml.log, AVAL2-ci-windows-28caf3a.log, AVAL2-mutantes.log. Cada um começa por `$ comando`.

Não editei código nem documento do projeto. Todos os stubs, cópias e repositórios temporários ficaram no scratchpad. No CI, só leitura.
>>>
