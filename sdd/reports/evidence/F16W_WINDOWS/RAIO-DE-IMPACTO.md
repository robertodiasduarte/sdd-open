# Raio de impacto — F16W_WINDOWS (passo 0b da sdd-release, antes da última rodada de revisão)

Um agente em contexto novo por superfície, só leitura, com os 5 campos de `.agents/skills/sdd-release/references/raio-de-impacto.md`,
sobre `c65e658`. Blocos verbatim abaixo.

## Superfície 2 — o bash do `sdd-fluxo.sh`

<<<RAIO
superficie: sdd/bin/sdd-fluxo.sh — o ambiente exportado (SDD_FLUXO_BIN, e agora SDD_FLUXO_BASH="${BASH:-bash}") e o bash com que o núcleo Python chama sdd/bin/verify-gate.sh --print (sdd/bin/sdd-fluxo.sh:45, :133, :679)
consumidor: sdd/bin/sdd-drive.sh:611 · ok — chama [BASH, sdd-fluxo.sh, "seguir", …, "--drive"]; o bash filho define `$BASH` com o próprio caminho e o script reexporta SDD_FLUXO_BASH; nada herdado do drive vaza
consumidor: sdd/bin/sdd-drive.sh:1074 · ok — chama `despachar`, que roda em shell puro (cmd_despachar) e não passa pelo núcleo Python
consumidor: sdd/bin/sdd-drive.sh:238 · ok — só procura a marca "--drive" no texto do script, e ela continua lá
consumidor: sdd/bin/sdd-drive.sh:45 · ok — padrão gêmeo SDD_DRIVE_BASH, já presente na v2.15.0 (commit 7f4f442), sem relação de nome com SDD_FLUXO_BASH
consumidor: tests/test_fluxo.py:35 · ok — roda [BASH, FLUXO, …] pelo script; os testes de seguir (linha 423 em diante) passam pela chamada do verify-gate com o caminho absoluto
consumidor: tests/test_fluxo.py:609 · ok — --self-test numa cópia sem git; os cenários de seguir do self-test passam pelo mesmo núcleo
consumidor: tests/test_drive.py:120 · ok — põe um sdd-fluxo.sh falso no lugar; o ambiente exportado pelo verdadeiro não entra
consumidor: .github/workflows/publish-gate.yml:115 · ok — `bash sdd/bin/sdd-fluxo.sh --self-test`, interface igual
consumidor: sdd/reports/evidence/F16W_WINDOWS/scripts/sabotagem.sh:26 · ok — a troca procura `capture_output=True, text=True, encoding="utf-8", errors="replace")` e o texto continua presente (contador 1)
consumidor: .agents/skills/*/SKILL.md e docs/*chained-flow*.md · ok — só citam `bash sdd/bin/sdd-fluxo.sh <verbo>`; nenhum cita SDD_FLUXO_BIN nem SDD_FLUXO_BASH
consumidor: leitores externos de SDD_FLUXO_BIN ou SDD_FLUXO_BASH · nenhum — a busca no repositório só encontra sdd/bin/sdd-fluxo.sh
consumidor: Windows nativo (o $BASH do Git Bash vale /usr/bin/bash e precisa da conversão de caminho ao chamar o python.exe) · não localizei prova executada no Windows para o sdd-fluxo; mesma dependência do sdd-drive.sh:45 desde a F14
invariante: INV-001 · ok — trata de migration e BUILD_REPORT; não toca este módulo
invariante: INV-002 · ok — trata de como o ledger é lido (linhas_uteis/linha_solta); a mudança não toca o `loop --ledger` do sdd-fluxo
>>>

## Superfície 1 — o vigia do `checar.sh` (bloco do gh e `alcance`)

<<<RAIO
superficie: bloco "# ── gh e instalação por sistema (F16)" … "# ── fim do gh" de checar.sh (cópia em inventario.sh) e alcance() do checar.sh: gh_estado (ausente|deslogado|ok|sem resposta), alcance (saída do git + __login=N + __rc=N), vigia de teto com corta/no_windows/rc_do_vigia
consumidor: .agents/skills/sdd-checar-ambiente/scripts/checar.sh:522-532 (SAIDA: lê __gh=, __publico=, __rc=, __login= da saída de alcance e gh_estado) · ok — formato das linhas inalterado; no Windows o corte chega como 137, que o ramo *) já trata
consumidor: .agents/skills/sdd-checar-ambiente/scripts/checar.sh:535-595 (classificação do ls-remote: mensagem primeiro, depois RC 143/137 + LOGIN) · ok — o rc só decide no ramo *); a falha natural entre 9 e 10 s no Windows que vira 137 é o limite já documentado em rc_do_vigia
consumidor: .agents/skills/sdd-checar-ambiente/scripts/checar.sh:599-613 (GH="$(gh_estado)" e o case ausente/deslogado/sem resposta) · ok — mesmos 4 valores
consumidor: .agents/skills/sdd-checar-ambiente/scripts/checar.sh:108-112 (classificação interna de gh_estado) · ok — com ressalva: testa rc=137 antes da mensagem, então no Windows um "deslogado" que sai entre 9 e 10 s vira "sem resposta" (⚠️ nos dois casos); o comentário de rc_do_vigia (checar.sh:88-89) promete "mensagem primeiro", o que só vale para alcance
consumidor: .agents/skills/sdd-iniciar-repo/scripts/inventario.sh:188 (printf 'gh: %s' "$(gh_estado)") · ok — mesma saída; set -u/pipefail sem efeito nas funções novas
consumidor: tests/test_inventario.py:340-346 (GH_STUB ok/deslogado/rede → gh: ok/deslogado/sem resposta) · ok — o stub sai na hora, então rc_do_vigia não altera nada, inclusive no Windows (menos de 10 s)
consumidor: tests/test_f16_textos.py:34-37 (compara as 2 cópias do bloco e exige gh_estado/instalar_gh) · ok — blocos idênticos (diff vazio); funções presentes
consumidor: tests/test_matriz_new_session.py:23-33 (extrai add_impede/add_remoto/MSG= das seções 1-3 do checar.sh) · ok — a mudança não acrescenta nem altera mensagem
consumidor: .agents/skills/sdd-new-session/SKILL.md:160-170 (traduz o pré-voo checar.sh --frente) · ok — mensagens e códigos de saída inalterados
consumidor: bin/sdd-open.sh:868-884 (checar.sh --segredo) · ok — o modo segredo sai em checar.sh:293 antes de alcance e gh_estado; só ganha definições de função
consumidor: tests/test_sdd_open.py:336-337 (lista checar.sh e inventario.sh no pacote) · ok — só a existência do arquivo
consumidor: scripts/starter/trocas/sdd-checar-ambiente.md:3-8 (troca textual no checar.sh para o starter) · ok — o trecho "antes" fica fora do bloco alterado
consumidor: tests/test_slot.py:119 (SEM_SINAL, que continua em tests/apoio.py:49) · ok — não depende do checar.sh; só test_checar.py deixou de importar SEM_SINAL
invariante: INV-001 · ok — trata de migration e BUILD_REPORT; não toca checar.sh nem inventario.sh
invariante: INV-002 · ok — trata do LEDGER_REVISAO e do ledger-revisao-lint.sh; não toca o módulo
>>>

Tratamento da ressalva: o comentário de `rc_do_vigia` passa a dizer onde a mensagem decide primeiro (`alcance`) e onde não
(`gh_estado`, ⚠️ nos dois casos).

## Superfície 3 — a decodificação UTF-8 dos subprocessos

<<<RAIO
superficie: decodificação da saída de subprocessos e escrita de arquivos no Python embutido de sdd/bin/{adversarial-review,adversarial-review-gate,eval-agree,eval-revisores,playbook-curator,sdd-fluxo}.sh, sdd/bin/adapters/openrouter.sh, sdd/review/stubs/{comum,openrouter}.py, bin/adapters/claude/{sdd-avaliador-guard,sdd-report-guard}.py e scripts/check-versions.py — text=True + encoding="utf-8", errors="replace"; open(..., encoding="utf-8")
consumidor: sdd/bin/report-lint.py:596 · quebra — (Windows, Python < 3.15 sem PYTHONUTF8/PYTHONIOENCODING) lê --stdin na codificação do sistema (cp1252) enquanto o guard (sdd-report-guard.py:102) agora envia UTF-8: os acentos chegam trocados ("CritÃ©rio"), o ✅ não casa o TRUE_RE (linha 42) e um "⚠️" vira erro de leitura → 64 → falha aberta; antes os dois lados usavam cp1252 e batiam. Correção: env PYTHONIOENCODING=utf-8 na chamada ao lint, ou o lint ler sys.stdin.buffer em UTF-8
consumidor: sdd/bin/report-lint.py:613 · quebra (já existia antes do diff, agora mais exposta) — print("✅ …") num stdout cp1252 quebra no Windows → sai 1 → o guard trataria como reprovação; antes, relatório com →/✅ parava no próprio guard e nem chegava aqui
consumidor: bin/adapters/claude/sdd-report-guard.py:26-27 e bin/adapters/claude/sdd-avaliador-guard.py:21-22 · quebra (já existia antes do diff) — emitir() escreve 🛑/⚠️ com ensure_ascii=False num stdout cp1252 no Windows; tests/apoio.py:84 tira o PYTHONIOENCODING dos testes, então tests/test_claude_adapter.py:162-236 provavelmente vermelho no job do Windows (não confirmei: sem evidência de rodada no Windows)
consumidor: bin/adapters/claude/sdd-avaliador-guard.py:54 · quebra (fora da codificação, mesma classe da F16W) — chama "bash" pelo nome; no Windows pode resolver para o bash.exe do WSL em System32, o que o sdd-fluxo.sh corrigiu com SDD_FLUXO_BASH
consumidor: bin/adapters/claude/sdd-avaliador-guard.py:57 · ok — `"⚠️" in saida` agora casa (o byte 0x8F do U+FE0F quebrava a decodificação em cp1252)
consumidor: sdd/bin/adversarial-review.sh:677 (lê saida+".err" escrito pelo adapters/openrouter.sh:48,51) · ok — escrita e leitura em UTF-8; antes, mensagem com acento em cp1252 deixava ler() retornar None e o sinal_auth não via o texto
consumidor: sdd/bin/adversarial-review.sh:618-623 (extrair ← adapter_extrair dos sdd/bin/adapters/*.sh) · ok — json.dumps em ASCII; UnicodeDecodeError nunca foi capturado ali
consumidor: sdd/bin/adversarial-review-gate.sh:302 e :281 (lê .n e openrouter.porta escritos por sdd/review/stubs/comum.py:36-38 e openrouter.py:57) · ok — ler() em UTF-8, conteúdo ASCII
consumidor: sdd/bin/adversarial-review-gate.sh:412 · ok — "REVIEW INVÁLIDA" (Á = C3 81) agora casa; em cp1252 estrito o 0x81 quebrava a decodificação
consumidor: sdd/bin/adversarial-review-gate.sh:181-183 · ok — a saída da sonda vem do bash em UTF-8
consumidor: sdd/bin/adversarial-review-gate.sh:154-156 (stubs /bin/sh escritos em UTF-8 e executados pelo bash) · ok — caminho com acento agora em UTF-8, que é o que o MSYS lê
consumidor: sdd/bin/sdd-fluxo.sh:683 (regex kind/cmd sobre a saída do verify-gate.sh --print) · ok — o verify-gate herda PYTHONIOENCODING=utf-8 de lib/python.sh:114-115
consumidor: sdd/bin/sdd-fluxo.sh:694-697 (design-lint.py) · ok — usa só o código de saída; o filho herda PYTHONIOENCODING=utf-8
consumidor: sdd/bin/adversarial-review.sh:167, sdd/bin/eval-agree.sh:70, sdd/bin/eval-revisores.sh:226, sdd/bin/playbook-curator.sh:391,694 (raiz do git rev-parse) · ok — git emite UTF-8; caminho com bytes que não são UTF-8 (só Linux) vira U+FFFD em vez de dar erro (ponto menor)
consumidor: .github/workflows/release.yml:138 e .github/workflows/publish-gate.yml:126 (check-versions.py) · ok — leem só o código de saída e o texto; o git show do SKILL.md agora não quebra no Windows
consumidor: scripts/starter/raiz/scripts/check-versions.py:71-72 · ok — é outro programa, sem encoding, excluído de propósito em tests/test_windows.py:115 e roda só em ubuntu (scripts/starter/raiz/.github/workflows/*.yml)
consumidor: bin/sdd-open.sh:860-866 (doctor compara sdd/bin/* com cmp) · ok — vai acusar "difere do pacote" nas cópias antigas dos projetos, comportamento previsto
consumidor: bin/sdd-open.sh:299-302 (gerado_em_dia dos guards em .claude/hooks) · ok — sync acusa os guards como desatualizados, previsto; linha_marca (252) só mexe em "coding=" no cabeçalho, e a linha 1-2 dos guards não tem declaração PEP 263
consumidor: tests/test_windows.py:111-123 · ok — a varredura exige encoding em todo text=True e as 12 chamadas passam
invariante: INV-001 · ok — não toca migration
invariante: INV-002 · ok — eval-revisores.sh mudou só em raiz_git(); linhas_uteis/linha_solta e a leitura do ledger ficaram intactas
>>>

Tratamento: a quebra do `report-lint.py:596` (crítica, 0d) é consertada com `PYTHONIOENCODING=utf-8` no ambiente da chamada do
guard ao lint (resolve a entrada e o ✅ da saída dele), com teste; `emitir()` dos 2 guards passa a `ensure_ascii=True` (JSON
igual para quem lê). O `"bash"` pelo nome no `sdd-avaliador-guard.py` (rodado pelo Claude Code, não por um script bash) fica
como pendência medida no CI do PR: sem um `$BASH` de quem chama, achar o bash do Git sem medir no Windows seria palpite.

## Superfície 4 — o job `testes-windows` e o executor

<<<RAIO
superficie: job testes-windows de .github/workflows/publish-gate.yml e .github/workflows/release.yml + scripts/testes-por-modulo.py
consumidor: .github/workflows/release.yml:255 · ok — release segue com needs: [testes, testes-macos]; testes-windows fora, um vermelho de fatia não segura a Release
consumidor: .github/workflows/release.yml:47 · ok — concurrency release-${{ github.ref }} sem mudança; o run fica em andamento mais tempo (16 fatias), o pendente que é cancelado é só o intermediário da main, como o comentário de release.yml:19-22 já admite
consumidor: .github/workflows/release.yml:26 · ok — paths não inclui scripts/** nem tests/** (igual antes); mudar só o executor não dispara a release
consumidor: .github/workflows/publish-gate.yml:9 · ok — gatilhos sem paths e sem concurrency; o job gate (ubuntu) não depende do testes-windows
consumidor: .agents/skills/sdd-release/scripts/deploy-espera-testes.py:163 · ok — rodado na árvore: RESULTADO: SIM; strategy/matrix lidos; upload-artifact não casa PUBLICA_USES nem o nome casa PARECE_PUBLICAR (:182)
consumidor: tests/test_deploy_espera_testes.py:149 · ok — copia release.yml e espera SIM com "needs: testes"; saída do script conferida
consumidor: tests/test_deploy_espera_testes.py:281 · ok — mesma cópia do release.yml; a recusa vem do deploy.yml do teste, não do testes-windows
consumidor: tests/test_release_workflow.py:120 · ok — upload-artifact fixado por SHA de 40 hex; SHA cf430e0 = tag v7.0.2 no GitHub
consumidor: tests/test_release_workflow.py:126 · ok — checkout v5.1.0 continua o único checkout do job
consumidor: tests/test_release_workflow.py:181 · ok — piso lido do needs: do release, que não mudou; as frases seguem "sem teste automático"
consumidor: README.md:91 · ok — frase de Windows do piso não decidido, sem citar o job nem o comando
consumidor: README.pt-BR.md:92 · ok — idem
consumidor: docs/quickstart.md:80 · ok — idem
consumidor: docs/pt-BR/quickstart.md:78 · ok — idem
consumidor: tests/test_f14_textos.py:312 · ok — confere '- sdd/invariants.md' nos paths do release.yml, que não mudaram
consumidor: tests/test_windows.py:5 · ok — a docstring diz que roda no job testes-windows; com a suíte inteira nas fatias, continua verdade
consumidor: scripts/publish-gate.sh:112 · ok — G3: MANIFEST.txt:303 (executor), :615 e :662 (testes novos) declarados; o publish-gate roda antes do executor na fatia 1 e a saída vai para $RUNNER_TEMP, fora da árvore
consumidor: scripts/next-version.sh · ok — não cita o job nem o comando (grep sem ocorrência)
consumidor: scripts/starter/raiz/.github/workflows/ci.yml · ok — workflows do starter (ci, auto-release, release) sem job Windows nem o executor
consumidor: .agents/skills/sdd-release/SKILL.md · ok — não cita testes-windows, o nome do job nem testes-por-modulo (grep sem ocorrência)
consumidor: tests/apoio.py:24 · ok — RAIZ pelo __file__ e BASH de SDD_TEST_BASH (:26); o executor passa os.environ (testes-por-modulo.py:157) com cwd=tests (:161), como o working-directory antigo
consumidor: tests/apoio.py:84 · ok — Sandbox tira PYTHONIOENCODING do ambiente dos testes que o usam
consumidor: tests/test_f17c_passo0.py:45 · quebra — mascara: chama sdd/bin/handoff-lint.py com o ambiente herdado; o executor injeta PYTHONIOENCODING=utf-8 (testes-por-modulo.py:157), então o ✅ do stdout (handoff-lint.py:124, sem reconfigure) não cai no CI Windows, mas cai no cp1252 do Git Bash do aluno, que a sdd-handoff manda rodar direto (.agents/skills/sdd-handoff/SKILL.md:131); falso verde na cobertura nova
consumidor: tests/test_apoio_ambiente.py:21 · ok — discover com cwd=RAIZ explícito, independe do cwd=tests da unidade
consumidor: tests/test_f17c_textos.py:152 · ok — discover com caminho absoluto da pasta de testes
consumidor: GitHub, checks obrigatórios da main · ok — branch sem proteção; as regras só proíbem apagar e push forçado; nenhum check obrigatório pelo nome antigo
invariante: INV-001 · ok — migration/BUILD_REPORT, não toca workflow nem executor
invariante: INV-002 · ok — ledger de revisão, não toca workflow nem executor
>>>

Tratamento: o executor deixa de pôr `PYTHONIOENCODING` no ambiente das unidades e tira o que viria de fora (como o
`Sandbox`): a unidade vê o ambiente do aluno; a leitura da saída dela segue em UTF-8 com `errors="replace"`. Teste novo:
a unidade não recebe a variável. Ressalva da fila (36 jobs no push da `main`, 20 por vez na conta grátis): registrada no
DESIGN (Decision 3) e na ficha.
