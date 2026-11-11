# DEFINE: F16 — Ambiente agnóstico e proativo

> As skills de entrada descobrem cedo o `gh`, o login no GitHub e o editor, e funcionam com qualquer editor ou nenhum; o pacote passa a rodar a suíte no Windows (Git Bash + Python nativo) e só promete o que essa medição provar.

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | F16_AMBIENTE |
| **Date** | 2026-11-10 |
| **Author** | define-agent (worktree `sdd-open-f16-ambiente`; branch `feat/f16-ambiente`, de `origin/main` `36d0454` = `v2.10.1`) |
| **Status** | Ready for Design |
| **Clarity Score** | 14/15 |
| **Entrada** | `sdd/features/BRAINSTORM_F16_AMBIENTE.md` (abordagem A: medir o Windows primeiro) |

---

## Problem Statement

O aluno só descobre que falta o programa do GitHub para o terminal (`gh`) ou o login na última etapa da `sdd-iniciar-repo` (publicar), ou quando o remoto já recusou o acesso; o `checar-ambiente` responde ✅ sem `gh`. Com o editor instalado e o comando fora do PATH (caso deste Mac: VS Code em `/Applications`, sem `code`), a `sdd-new-session` diz "sem editor", e sem editor não há caminho de "só terminal": o aviso final manda continuar numa janela que não existe. E o pacote promete Windows (Git Bash/WSL) no README e no quickstart sem que nada dele tenha rodado em Windows; lá o `python3` costuma ser o atalho da Microsoft Store, e 18 scripts o chamam.

---

## Target Users

| User | Role | Pain Point |
|---|---|---|
| Aluno contador, iniciante em terminal, muitas vezes no Windows | roda `checar-ambiente`, `iniciar-repo` e `new-session` | trava na publicação sem `gh` ou sem login; scripts que chamam `python3` não rodam; o README promete suporte não provado |
| Aluno no macOS com o editor fora do PATH | abre frentes com a `sdd-new-session` | a frente abre "sem editor" com o app instalado |
| Aluno só com Claude Code ou só com Codex no terminal | abre frentes sem editor | "Continue na janela nova" não serve; não sabe como seguir |
| Mantenedor do Open | decide o que o pacote promete | não tem medição do Windows para decidir o piso |

---

## Goals

| Priority | Goal |
|---|---|
| **MUST** | `sdd-checar-ambiente` 1.4.1 → 1.5.0: `gh` ausente ou deslogado ⇒ ⚠️ (nunca 🔴); editor detectado no resumo; `--frente` sem mudança |
| **MUST** | `sdd-iniciar-repo` 1.1.1 → 1.2.0: `gh` e login no Passo 0 como aviso antecipado; `inventario.sh` imprime a linha `gh:` |
| **MUST** | `sdd-new-session` 1.4.1 → 1.5.0: detecção de editor em 2 camadas (PATH ampliado; apps fora do PATH no macOS e no Windows), slot com argumentos usado como está, modo terminal e aviso final em duas formas |
| **MUST** | tabela de instalação (macOS · Windows · Linux × `git` · `gh`) igual nas 3 skills |
| **MUST** | job `testes-windows` (Git Bash + Python nativo) nos 2 workflows; a suíte passa lá, com `skipIf` motivado para o que o Windows não tem e conserto com teste para o que for defeito do pacote |
| **MUST** | os scripts do pacote acham o Python que roda (`python3`, `python` ou `py -3`) e recusam o atalho da Store |
| **MUST** | a frase de Windows do README e do quickstart (2 idiomas cada) diz exatamente o que foi provado; piso decidido pelo Roberto com os números |
| **SHOULD** | os 5 achados de Windows guardados das revisões (CRLF do curator, `tasklist` do `sdd-drive.sh`, `report-lint`, `sdd-archive`, `O_NOFOLLOW` da trava) medidos e consertados ou rebatidos com evidência |
| **COULD** | job de WSL (fica fora: o Ubuntu cobre) |

---

## Success Criteria

- [ ] Sem `gh` no PATH: `checar.sh` ⇒ ⚠️ do `gh` com o comando de instalação do sistema e rc 0; `checar.sh --frente` ⇒ ✅ sem a palavra `gh`.
- [ ] `gh` stub deslogado, com remoto do GitHub e sem remoto ⇒ ⚠️ com `gh auth login`; stub logado ⇒ nenhuma linha de `gh`; remoto fora do GitHub ⇒ o stub não é chamado.
- [ ] `inventario.sh` imprime `gh: ausente`, `gh: deslogado`, `gh: ok` e `gh: sem resposta` nos 4 casos de stub.
- [ ] Com PATH sem editor e um app `Visual Studio Code.app` numa pasta de aplicativos de teste, a detecção devolve `open -a "Visual Studio Code"`; neste Mac, a prova manual abre a frente no VS Code.
- [ ] Com um `python3` falso que sai 9009 (o atalho da Store) e um `python` válido no PATH, um script de `sdd/bin` que usa Python roda com o `python`; sem nenhum Python válido, o script que precisa dele para com a causa certa e o conserto, sem traceback, e o que não precisa segue.
- [ ] Job `testes-windows` com o caminho do aluno rodado num run do PR (evidência: o run e o log), com a contagem de testes rodados, pulados (com motivo) e o que falhou, no relatório; a 1ª medição da suíte inteira registrada (282 de ~1.900 em 90 min, 156 quebras) como ponto de partida da F16W; tempo do job medido e teto conferido antes da tag.
- [ ] Linha de base vermelha: os testes novos falham em `36d0454`.
- [ ] Sabotagens: ao menos 4 mutantes (gh ausente vira ✅; `open -a` some; atalho da Store aceito; README afirma suporte com o job informativo) derrubam, cada um, um teste nomeado.
- [ ] Verify Gate numa cópia de `git archive` sai 0, com a suíte inteira (a contagem só sobe a partir de 1.867, medida em `f6241f4` + `58d1bd2`).
- [ ] Release publicada com `SHA256SUMS.txt` conferido.

---

## Acceptance Tests

| ID | Padrão | Critério (EARS) | Gate (`kind`) |
|---|---|---|---|
| AT-001 | Event-driven | **When** `checar.sh` roda no modo normal e o comando `gh` não existe no PATH, o script **shall** incluir um ⚠️ que diz que o programa do GitHub para o terminal (`gh`) não está instalado e que publicar e logar ficam manuais, com o comando de instalação do sistema em uso (macOS `brew install gh`, Windows `winget install --id GitHub.cli -e`, Linux o link da instalação), e **shall** manter o rc que teria sem esse aviso (nunca 🔴 por causa do `gh`); **when** roda com `--frente`, **shall** não mencionar o `gh` em parte alguma da saída | test |
| AT-002 | Unwanted | **When** `checar.sh` roda no modo normal, o `gh` existe e o remoto `origin` é do GitHub ou não existe, o script **shall** consultar `gh auth status` com o mesmo teto de tempo do `ls-remote`; **if** a consulta diz que não há conta logada, **then** **shall** incluir um ⚠️ com `gh auth login`; **if** a consulta passa do teto, **then** **shall** dizer que não deu para conferir o login e seguir, sem 🔴; com o `gh` logado, **shall** não imprimir linha de `gh`; **where** o remoto é de outro serviço, o script **shall** não chamar o `gh` nem falar dele | test |
| AT-003 | Event-driven | **When** a detecção de editor roda com o slot `editor` vazio, ela **shall** devolver o primeiro que existir, nesta ordem: no PATH, `code`, `cursor`, `code-insiders`, `windsurf`, `zed`, `subl`, `idea`, `pycharm`, `webstorm`; no macOS, fora do PATH, o app `Visual Studio Code`, `Cursor`, `Windsurf`, `Zed` ou `Sublime Text` em `/Applications` ou `~/Applications`, devolvido como `open -a "<App>"` com a dica de pôr o comando no PATH; no Windows, fora do PATH, `code.cmd` ou `cursor.cmd` sob `%LOCALAPPDATA%\Programs`, devolvido pelo caminho; nenhum ⇒ vazio. O modo `--editores` **shall** listar todos os achados, um por linha (`<nome><TAB><comando>`), na mesma ordem e sem repetir o mesmo editor achado por dois caminhos. O `checar.sh` **shall** citar o editor achado no resumo ✅ e **shall** continuar sem ⚠️ quando não há editor | test |
| AT-004 | Event-driven | **When** `inventario.sh` da `sdd-iniciar-repo` roda, **shall** imprimir exatamente uma linha `gh: ausente`, `gh: deslogado`, `gh: ok` ou `gh: sem resposta` (a consulta passou do teto de 10 s); o Passo 0 do `SKILL.md` **shall** conferir o `gh` e o login junto com o `git` como aviso antecipado, com as opções "instalar agora" e "depois" (sem parar a skill), e o Passo 6 **shall** manter a checagem de retomada | test |
| AT-005 | Event-driven | **When** a `sdd-new-session` encontra o slot `editor` vazio e nenhuma preferência deste computador (`git config sdd.editor`), ela **shall** perguntar uma vez, sem escolher sozinha, onde abrir as frentes (cada editor que `checar.sh --editores` achou, o 1º recomendado; só no terminal com Claude Code ou com Codex, gravados como `terminal:claude` e `terminal:codex`; dizer o meu comando; não sei), gravar a resposta em `git config --local sdd.editor` (nunca no slot, que só chega à branch padrão na integração) e não perguntar de novo enquanto ela existir (pedido do Roberto, 2026-11-11; rodada 5, R1); **when** o slot é `terminal:<agente>`, ou não há editor, ela **shall** responder em modo terminal: o Próximo passo diz 1. abrir um terminal novo, 2. `cd "<pasta da frente>"`, 3. rodar o agente do slot (`claude`, `codex`…, sem presumir um só), e a última linha **shall** ser o aviso de continuar num terminal novo aberto na pasta da frente; com editor, o aviso de janela nova continua; o slot `editor` com argumentos (`open -a "Cursor"`) **shall** ser usado como está; as 3 skills **shall** trazer a mesma tabela de instalação (macOS · Windows · Linux × `git` · `gh`) e o login `gh auth login` → GitHub.com → HTTPS → Yes → Login with a web browser; o texto novo **shall** passar no `tests/test_agnostico.py` | test |
| AT-006 | Unwanted | **When** um script do pacote precisa de Python, ele **shall** usar o primeiro interpretador que rode e seja ≥ 3.9 entre `SDD_PYTHON` (se definido), `python3`, `python` e `py -3`; **if** um candidato existe e não roda (o atalho da Microsoft Store, que sai 9009 ou não imprime versão) ou é mais velho que o 3.9, **then** **shall** passar ao próximo; **if** nenhum serve, **then** a carga **shall** seguir sem parar (quem não precisa de Python não para), e a guarda do script, no momento em que ele precisa de Python, **shall** dizer a causa certa (não roda; versão X.Y; pasta temporária sem escrita) e parar pelo contrato de "python3 ausente" do próprio script, ou, sem contrato próprio, com o conserto por sistema, `RESULTADO: PAROU` e exit 64, sem traceback e sem tentar seguir | test |
| AT-007 | Optional feature | Os workflows `release.yml` e `publish-gate.yml` **shall** ter o job `testes-windows` em `windows-latest`, com `shell: bash` (Git Bash) e Python do `setup-python`, rodando o `publish-gate.sh` em modo ci e os testes do caminho do aluno (`test_checar`, `test_inventario`, `test_python_resolver`, `test_windows`, `test_f16_textos`, com `-v`), com teto de 30 min — a suíte inteira no Windows é a frente F16W (decisão do Roberto, 2026-11-11, depois da 1ª medição); **where** o piso Windows foi decidido como testado, o job **shall** estar no `needs:` do job `release` e o README e o quickstart (2 idiomas cada) **shall** afirmar o suporte no Windows com Git Bash; **where** não foi, o job **shall** ficar fora do `needs:` (sem `continue-on-error`, que a suíte proíbe), e as 4 frases **shall** dizer "sem teste automático" para o Windows | test |
| AT-008 | Unwanted | **If** um teste depende de recurso que o Windows com Git Bash não tem (trava `fcntl`, link simbólico sem modo de desenvolvedor, bit de execução por `chmod`, sinal POSIX), **then** **shall** ser pulado por `skipIf` com um motivo que nomeia o recurso, vindo de uma constante única de `tests/apoio.py`; os 5 achados guardados (CRLF no stdout do `playbook-curator.sh`, ramo `tasklist` do `sdd-drive.sh`, `report-lint`, `sdd-archive`, trava sem `O_NOFOLLOW`) **shall** ter, cada um, o teste que o mede listado em `tests/test_windows.py`; o do CRLF roda no job desta frente, e os outros 4, que dependem da suíte inteira, são medidos na F16W | test |
| AT-009 | Non-regression | O `checar.sh --frente` **shall continue to** emitir as mesmas mensagens de bloqueio que a tabela "Como traduzir cada achado" da `sdd-new-session` traduz (`tests/test_matriz_new_session.py`); os jobs `testes` (Ubuntu) e `testes-macos` **shall continue to** rodar a mesma suíte, com os tetos de 45 min (Ubuntu) e 75 min (macOS; era 60, subiu por decisão do Roberto antes da tag, com 1.936 testes em 47m19s); o `init`/`sync` **shall continue to** não copiar o `.gitignore` nem nada da raiz do pacote além do que já copia; a suíte **shall continue to** passar no bash 3.2 do macOS (`SDD_TEST_BASH=/bin/bash`) | test |

Considerados: **While** — N.A.: nenhum comportamento depende de um estado que dura (o teto de tempo do `gh auth status` é um evento, coberto por If/Then no AT-002). **If/Then** em AT-002 (deslogado; consulta que passa do teto), AT-006 (atalho da Store; nenhum Python) e AT-008 (recurso ausente). **Where** em AT-002 (remoto de outro serviço) e AT-007 (piso decidido ou não: o teste roda com o estado do workflow e confere o README contra ele). Não-regressão em AT-009, porque a frente mexe no `checar.sh`, que o pré-voo da `sdd-new-session` lê, e nos 2 workflows.

O resultado do job Windows num run do GitHub (verde, com a contagem) não é AT do gate local: é critério de sucesso com evidência (o id do run e o log em `evidence/`). O gate local prova que os testes, os `skipIf` e a coerência README × workflow existem e passam aqui.

---

## Clarifications

### Session 2026-11-10

- [x] (escopo) Windows inteiro nesta frente: medir, consertar, `skipIf` com motivo, decidir o piso (brainstorm, pergunta 1); integrado em AT-006, AT-007, AT-008.
- [x] (restrições) Push livre na `feat/f16-ambiente` e PR em rascunho para medir, sem merge; `main`, tag e Release pedem "sdd-open autorizado" (pergunta 2).
- [x] (integrações) `gh auth status` com remoto do GitHub e também sem remoto; nunca no `--frente`; fora do GitHub não consulta (pergunta 3); integrado em AT-002.
- [x] (terminologia) Modo terminal é eixo de editor, fora da tabela de degradação por vendor (pergunta 4).
- [x] (dados) Amostras: este Mac (VS Code instalado, `code` fora do PATH, `cursor` no PATH, `gh` logado) e o job `windows-latest` (pergunta 5).
- [x] (sinal de conclusão) Abordagem A: o 1º commit corrige a frase do README/quickstart para "sem teste automático" e cria o job informativo; o piso é decidido depois da medição, pelo Roberto; até lá vale o ramo "não foi" do AT-007.
- [x] (edge cases) 1ª medição muito maior que o esperado (centenas de quebras fora do interpretador) ⇒ parar e trazer os números ao Roberto (brainstorm, decisão 7). Aconteceu em 2026-11-11 (run 42938720292): o Roberto escolheu o subconjunto do caminho do aluno nesta frente e o porte da suíte inteira numa frente própria (F16W).
- [x] (dados) A detecção de editor hoje é texto da skill (o agente roda `command -v`): para o AT-003 ser testável, ela passa a morar num script com as pastas de aplicativos e o `%LOCALAPPDATA%` injetáveis por variável de ambiente; o Design escolhe onde.
- [x] (UX) Sem interface: texto de skill e saída de terminal no padrão de `docs/cli-conventions.md`. UX review pulado.

- [x] (sinal de conclusão) Piso do Windows decidido pelo Roberto em 2026-11-11, com os números finais (caminho do aluno verde no Windows: 144 testes, 136 ok, 8 pulados; suíte inteira não provada; teto do `checar` sem efeito no Windows): **continua "sem teste automático"**; o job segue informativo, fora do `needs:` da release, até a F16W. Vale o ramo "não foi" do AT-007.

### Session 2026-11-10 (governança)

- [x] (governança) N.A. — o revisor fresco leu o DEFINE pelo sentido: ferramentas do ambiente (`gh`, editor, Python, CI no Windows), sem dinheiro, lançamento, tributo, folha nem dado pessoal; "conta logada" é a do GitHub, só lida, nunca guardada. Fronteira conferida (só o permitido mudou; nenhum arquivo gravado).

---

## Verify Gate

```yaml
verify_gate:
  kind: test
  cmd: "T=$(mktemp -d) && git archive HEAD | tar -x -C $T && PUBLISH_GATE_MODE=ci bash scripts/publish-gate.sh $T && cd $T && SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover -s tests -p 'test_*.py'"
  pass_when: "exit 0"
  threshold: "—"
  manual_fallback: "—"
```

Cobertura: AT-001 e AT-002 em `tests/test_checar.py` (stubs de `gh` e PATH restrito); AT-003 no teste do script de detecção (pastas de aplicativos e `%LOCALAPPDATA%` falsos) e em `tests/test_checar.py` (resumo); AT-004 em `tests/test_inventario.py` e no teste de textos da frente; AT-005 em `tests/test_matriz_new_session.py`, `tests/test_agnostico.py` e no teste de textos da frente; AT-006 no teste do resolvedor de Python (stubs que saem 9009, versão antiga, nenhum); AT-007 em `tests/test_release_workflow.py` (os 2 workflows e a coerência com as 4 frases); AT-008 num teste que varre os `skipIf` da suíte e nos testes dos 5 achados; AT-009 na suíte inteira (matriz, workflows, `init`, `SDD_TEST_BASH=/bin/bash`).

---

## Out of Scope

- Instalar `git`, `gh`, Python ou editor pelo aluno (as skills indicam o comando; o `checar-ambiente` continua só leitura).
- Tornar o `gh` obrigatório (SSH e gerenciador de credenciais continuam válidos).
- Mudar a `sdd-release` (já confere `gh auth status` onde precisa).
- O starter (recebe tudo pela F17).
- Job de WSL; prova manual num Windows real.
- PowerShell como shell do pacote (os scripts continuam bash; no Windows, Git Bash).

---

## Constraints

| Type | Constraint | Impact |
|---|---|---|
| Technical | bash 3.2, sem zsh, sem link simbólico no pacote; `sdd/bin/*.sh` sempre com `bash` | `tests/test_bash32.py` |
| Technical | `checar-ambiente` só lê; toda consulta de rede com teto de tempo | AT-002 |
| Technical | a detecção de editor e o resolvedor de Python aceitam variáveis de ambiente para as pastas e o interpretador, para o teste injetar casos sem depender da máquina | AT-003, AT-006 |
| Agnóstico | texto de skill não presume VS Code, macOS nem um agente só | `tests/test_agnostico.py` |
| Skills | a tabela de instalação é repetida nas 3 skills (cada uma é instalada sozinha; a F17 as gera como zip); skill tocada sobe `metadata.version` | `scripts/check-versions.py --base v2.10.1` |
| CI | o teto de cada job é olhado **antes** da tag; tag com job cancelado fica sem Release e não se move | tempo do job Windows medido no PR |
| Público | repositório público: nada da RDD, nenhum caminho de máquina real nos testes | `publish-gate.sh` |
| Processo | `git add` por caminho; suíte com `-B`; sabotagem só em cópia de `git archive` | lições F19/F21 |
| Escopo | se a 1ª medição do Windows trouxer centenas de quebras fora do interpretador, parar e perguntar | decisão 7 do brainstorm |

---

## Technical Context

| Aspect | Value | Notes |
|---|---|---|
| **Deployment Location** | `.agents/skills/{sdd-checar-ambiente,sdd-iniciar-repo,sdd-new-session}/`, `.github/workflows/{release,publish-gate}.yml`, `sdd/bin/` e `bin/` (interpretador Python), `README.md`, `README.pt-BR.md`, `docs/quickstart.md`, `docs/pt-BR/quickstart.md`, `tests/`, `MANIFEST.txt` | produto do Open |
| **KB Domains** | nenhum | o Open não tem `sdd/kb/`; a skill `sdd-kb` cria uma base quando o projeto quiser |
| **IaC Impact** | None | só os workflows do GitHub Actions |
| **LLM Prompts** | false | nenhum prompt de produção; "agente" aqui é o programa que o aluno roda no terminal |
| **CONTEXTO de domínio** | nenhum (pulado: o Open não tem `sdd/patterns/dominio.md`) | `contexto-lint.sh --sugerir` → PULAR |
| **Governança** | N.A. — ferramentas do ambiente (gh, editor, Python, CI no Windows); sem dinheiro, lançamento, tributo, folha nem dado pessoal | revisor fresco, 2026-11-10 |

---

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|---|---|---|---|
| A-001 | `gh auth status` sai diferente de 0 quando não há conta logada | o AT-002 precisaria ler o texto; o teste do stub fixa o contrato | [ ] conferir na doc do `gh` no Design |
| A-002 | No `windows-latest`, `shell: bash` é o Git Bash e o `setup-python` põe `python` no PATH | o job precisaria de passo extra; a 1ª medição prova | [ ] |
| A-003 | O atalho `python3` da Store sai 9009 (ou não imprime versão) sem abrir nada no CI | o resolvedor precisaria de outro sinal; teste por stub cobre a lógica | [ ] |
| A-004 | A suíte cabe em 90 min no `windows-latest` | teto maior ou suíte dividida; medido no 1º run | [ ] |
| A-005 | `tests/apoio.py` acha o bash do Git (não o `bash.exe` do WSL em `System32`) | o job rodaria a suíte no WSL; o Design fixa `SDD_TEST_BASH` no job | [ ] |

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---|---|---|
| Problem | 3 | 4 lacunas com arquivo e linha, amostra real neste Mac |
| Users | 3 | 4 papéis |
| Goals | 3 | MUST/SHOULD/COULD |
| Success | 3 | casos de stub nomeados, 4 sabotagens, run do CI com contagem |
| Scope | 2 | o tamanho do Windows só se conhece na 1ª medição (com parada definida) |
| **Total** | **14/15** | |

---

## Open Questions

None - ready for Design.

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | 2026-11-10 | define-agent | Initial version |
| 1.6 | 2026-11-11 | define-agent | rodada 5, R1: a escolha do editor vai para `git config --local sdd.editor`, não para o slot da frente (a pergunta voltava em cada frente até a integração) (AT-005) |
| 1.5 | 2026-11-11 | define-agent | pedido do Roberto antes da release: com o slot `editor` vazio, a `sdd-new-session` pergunta o padrão uma vez (lista do `checar.sh --editores` + terminal com Claude Code ou Codex + dizer o comando), em vez de escolher o 1º achado (AT-003, AT-005) |
| 1.4 | 2026-11-11 | define-agent | release: o teto do job macOS sobe de 60 para 75 min antes da tag (decisão do Roberto), no AT-009 |
| 1.3 | 2026-11-11 | define-agent | 1ª medição do Windows (suíte inteira cancelada nos 90 min com 15% feito, 156 quebras em 282): decisão do Roberto — o job roda o caminho do aluno, com teto de 30 min; o porte da suíte inteira e 4 dos 5 achados guardados vão para a frente F16W (AT-007, AT-008, critério de sucesso) |
| 1.2 | 2026-11-10 | define-agent | revisão do DESIGN, rodada 2 (R1 a R4): AT-006 — a carga não para; a guarda de cada script diz a causa certa (não roda, versão, calço) e para só quando ele precisa de Python. AT-007 — o job informativo fica fora do `needs:`, sem `continue-on-error` (a suíte o proíbe) |
| 1.1 | 2026-11-10 | define-agent | DESIGN, Decision 3: a linha `gh:` ganha o 4º valor `sem resposta` (consulta que passa do teto), em AT-004 e no critério de sucesso |

---

## Next Step

**Ready for:** `/sdd-design sdd/features/DEFINE_F16_AMBIENTE.md` — UX review pulado: a feature não tem interface (texto de skill, scripts de terminal e workflows).
