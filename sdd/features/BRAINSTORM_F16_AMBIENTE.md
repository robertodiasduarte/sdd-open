# BRAINSTORM: F16 Ambiente agnóstico e proativo

> Sessão exploratória para clarear intenção e abordagem antes dos requisitos.

## Metadata

| Atributo | Valor |
|-----------|-------|
| **Feature** | F16_AMBIENTE |
| **Data** | 2026-11-10 |
| **Autor** | brainstorm-agent (sessão com o Roberto) |
| **Status** | Ready for Define |
| **Base** | `feat/f16-ambiente`, nascida de `origin/main` `36d0454` (`v2.10.1`); passo 0 em `e632432` e `f6241f4` |

---

## Ideia inicial

**Entrada:** executar a F16 do plano (`sdd/features/PLANO_F4_F15_CONSOLIDADO.md`, seção 8, F16) com o escopo de
`sdd/features/ESCOPO_F16_AMBIENTE.md` (branch `docs/incorporar-starter`): as skills de entrada descobrem cedo o
que o aluno vai precisar (`git` **e** `gh`, login, editor) e funcionam com qualquer editor ou nenhum; e o pacote
passa a ser testado no Windows (tamanho incerto).

**Contexto levantado (conferido em `36d0454`):**
- Os achados do escopo (feito em `9508ff0`) continuam valendo, com linhas deslocadas:
  `sdd-checar-ambiente/scripts/checar.sh:358,380` (o `gh` só escolhe a mensagem quando o remoto já recusou),
  `:469` (lista fechada `code cursor subl`); `sdd-new-session/SKILL.md:213` (mesma lista) e `:282` (aviso
  "Continue na janela nova"); `sdd-iniciar-repo/SKILL.md:264-272` (`gh` só no Passo 6).
- **Versões mudaram:** `sdd-checar-ambiente` 1.4.1 · `sdd-iniciar-repo` 1.1.1 · `sdd-new-session` **1.4.1** (a F14
  levou de 1.3.0 a 1.4.1). Alvos: 1.5.0 · 1.2.0 · **1.5.0**.
- Windows: `README.md:90`, `README.pt-BR.md:91`, `docs/quickstart.md:80` e `docs/pt-BR/quickstart.md:78`
  prometem Git Bash/WSL; os workflows só têm `ubuntu-latest` (teto 45 na `release.yml`) e `macos-latest`
  (teto 60). Nada do pacote rodou em Windows.
- Tamanho do Windows, por cima: 1.867 testes em 66 arquivos; 26 arquivos citam link simbólico, 20 `chmod`, 58
  `/bin/bash` ou `/usr/bin`; 14 scripts de `sdd/bin` chamam `python3`, que no Windows nativo costuma ser o
  atalho da Microsoft Store (não roda nada).
- `publish-gate.yml` roda em todo `pull_request`: um PR em rascunho mede o Windows sem tocar a `main`.

**Contexto técnico para o Define:**

| Aspecto | Observação | Implicação |
|--------|-------------|-------------|
| Onde mora | `.agents/skills/{sdd-checar-ambiente,sdd-iniciar-repo,sdd-new-session}/`, `.github/workflows/`, `sdd/bin/*.sh` (interpretador), `tests/` | sem skill nova; `test_skill_lint.py` não muda |
| Testes existentes | `tests/test_checar.py`, `test_inventario.py`, `test_matriz_new_session.py`, `test_agnostico.py` | os casos novos entram neles |
| CI | `release.yml` (`testes`, `testes-macos`, `release` com `needs:`), `publish-gate.yml` (`gate`, job macOS) | o job Windows entra nos 2, fora do `needs:` até a decisão do piso |

---

## Perguntas e respostas

| # | Pergunta | Resposta | Impacto |
|---|----------|--------|--------|
| 1 | O que do Windows entra nesta frente e o que vira frente própria? | **Tudo nesta frente**: medir, consertar, pular com motivo, decidir o piso | o Windows deixa de ser só medição; o tamanho depende da 1ª medição |
| 2 | Posso fazer push da `feat/f16-ambiente` e abrir PR em rascunho para medir cedo? | **Sim, push livre na branch** e PR em rascunho, sem merge; `main`, tag e Release continuam pedindo "sdd-open autorizado" | o ciclo de medição não para a cada rodada |
| 3 | `gh auth status` (consulta a rede) roda quando? | **Com remoto do GitHub e também sem remoto**; remoto fora do GitHub não consulta; nunca no `--frente` | quem ainda vai publicar (iniciar-repo) sabe do login cedo |
| 4 | O modo terminal entra na tabela de degradação por vendor (plano, 8.0)? | **Não: é eixo de editor**, igual para os 7 agentes; uma linha no plano diz isso, como o eixo do CI | nada muda na tabela de vendor |
| 5 | Há amostra além do CI e deste Mac? | **Só o CI e este Mac** | o CI é a única medição do Windows; o relatório declara |
| 6 | Qual abordagem? | **A: medir primeiro** | ordem do Build: README + job → push → consertos por categoria; skills em paralelo |

---

## Inventário de amostras

| Tipo | Onde | Qtde | Notas |
|------|----------|-------|-------|
| Máquina real (macOS) | este Mac | 1 | VS Code em `/Applications/Visual Studio Code.app` e **sem `code` no PATH**; `cursor` no PATH; `gh` em `/opt/homebrew/bin`, logado (keyring). Reproduz o achado B4 |
| Arquivo real | `sdd/ambiente.md` do checkout local do Open | 1 | `editor: cursor` com a suposição "o `code` não está no PATH deste computador" |
| Medição Windows | job `testes-windows` (`windows-latest`, Git Bash, Python do `setup-python`) | — | a criar no 1º commit; é o caso real do aluno |
| Código a reusar | `checar.sh` (teto de tempo do `ls-remote`, função `tem`), stubs de `PATH` em `tests/test_checar.py` | — | os casos `gh` ausente/deslogado saem de stub, como o escopo previa |

**Uso:** este Mac prova o critério do `open -a "Visual Studio Code"` (PATH restrito no teste, app real na prova
manual); o log do job Windows é a evidência de cada categoria de conserto ou `skipIf`.

---

## Abordagens exploradas

### Abordagem A: Medir primeiro, consertar por categoria ⭐ Recomendada

**Descrição:** o 1º commit corrige a frase do README/quickstart e cria o job `testes-windows` informativo nos 2
workflows; push e PR em rascunho; a medição agrupa as quebras por causa (interpretador Python, link simbólico,
`chmod`, sinal, caminho com `\`, CRLF); cada categoria vira conserto com teste ou `skipIf` com motivo; as 3 skills
andam em paralelo; no fim, o Roberto decide o piso com os números.

**Prós:** a estimativa fica real no 1º dia; as skills nascem já testadas no Windows.

**Contras:** PR em rascunho aberto a frente toda; o job Windows deve ser o mais lento.

**Por que recomendada:** o tamanho do Windows é a única incerteza da frente, e o primeiro push a responde.

### Abordagem B: Skills primeiro, Windows no fim

**Prós:** entrega as skills cedo.
**Contras:** a incerteza fica para o fim; se a medição quebrar centenas de testes, a frente estoura com a
release pronta.

### Abordagem C: Só WSL

**Prós:** o WSL é Linux por dentro e já fica perto do Ubuntu do CI.
**Contras:** o caso real do aluno contador (Git Bash + Python nativo) segue sem prova; contradiz a resposta 1.

---

## Abordagem escolhida

| Atributo | Valor |
|-----------|-------|
| **Escolhida** | Abordagem A |
| **Confirmação** | 2026-11-10, nesta sessão |
| **Motivo** | resolver a incerteza do tamanho no 1º push |

---

## Decisões

| # | Decisão | Motivo | Alternativa rejeitada |
|---|----------|-----------|----------------------|
| 1 | Windows inteiro na F16 (medir, consertar, `skipIf`, piso) | decisão do Roberto | frente própria F16W para os consertos |
| 2 | Push livre na `feat/f16-ambiente` + PR em rascunho | medir sem parar a cada rodada | perguntar a cada push; medir só no PR da release |
| 3 | `gh auth status` com remoto do GitHub ou sem remoto | quem ainda vai publicar precisa saber cedo | só com remoto do GitHub |
| 4 | Modo terminal fora da tabela de vendor | é eixo de editor, igual nos 7 agentes | linha nova na tabela |
| 5 | `gh` ausente/deslogado é ⚠️, nunca 🔴 | SSH e gerenciador de credenciais continuam válidos | `gh` obrigatório |
| 6 | Até a decisão do piso, a frase do README/quickstart diz "sem teste automático" | nada promete o que não foi provado | manter a promessa até medir |
| 7 | 1ª medição muito maior que o esperado (centenas de quebras fora do interpretador) ⇒ parar e trazer os números | passar do tamanho é pergunta ao Roberto | seguir consertando sem teto |

---

## Removidas (YAGNI)

| Sugerida | Por que saiu | Volta? |
|-------------------|----------------|----------------|
| Instalar `git`/`gh` pelo aluno | o `checar-ambiente` é só leitura; as skills indicam o comando | Não |
| `gh` obrigatório | SSH e gerenciador de credenciais continuam válidos | Não |
| Job de WSL | o Ubuntu do CI já cobre | Sim, se aparecer defeito só de WSL |
| Prova manual num Windows real | sem máquina disponível; o CI é a medição | Sim, por relato de aluno |
| Ajustes no starter | chegam pela F17 (Decisão 5) | F17 |
| `sdd-release` conferindo `gh` | já confere `gh auth status` onde precisa | Não |

---

## Validações incrementais

| Seção | Apresentada | Retorno | Ajustou? |
|---------|-----------|---------------|-----------|
| Bloco 1: as 3 skills (versões, `gh`, login, editor em 2 camadas, modo terminal, tabela de instalação, testes) | ✅ | "Está certo" | Não |
| Bloco 2: Windows (1º commit, medição, categorias, achados guardados, piso, tetos, parada com números) | ✅ | "Está certo" | Não |

---

## Requisitos sugeridos para o /define

### Problema (rascunho)
O aluno só descobre que falta o `gh`, o login no GitHub ou um editor reconhecível na última etapa (ou nunca,
quando o editor está fora do PATH), e o pacote promete Windows sem nunca ter rodado lá.

### Usuários (rascunho)
| Usuário | Dor |
|------|------------|
| Aluno contador, iniciante em terminal, muitas vezes no Windows | trava na publicação sem `gh`; Python do Windows não é `python3`; promessa de suporte não provada |
| Aluno no macOS com o editor instalado e o comando fora do PATH | a frente abre "sem editor" com o app instalado |
| Aluno só com Claude Code ou só com Codex no terminal | "Continue na janela nova" não serve para quem não tem janela |

### Critérios de sucesso (rascunho)
- [ ] Sem `gh` no PATH: `checar.sh` ⇒ ⚠️ do `gh` e rc 0; `checar.sh --frente` ⇒ ✅ sem menção ao `gh`.
- [ ] `gh` stub deslogado (remoto do GitHub e sem remoto) ⇒ ⚠️ com `gh auth login`; remoto fora do GitHub ⇒ nem
      `gh` nem login.
- [ ] `inventario.sh` imprime `gh: ausente|deslogado|ok` (3 casos por stub).
- [ ] `sdd-iniciar-repo` Passo 0 avisa do `gh`/login com "instalar agora / depois"; Passo 6 mantém a checagem.
- [ ] `sdd-new-session` sem editor no PATH responde com o modo terminal e o aviso "terminal novo".
- [ ] No macOS com o app do VS Code e sem `code` no PATH, o slot recebe `open -a "Visual Studio Code"` e a
      frente abre (teste com PATH restrito + prova manual neste Mac).
- [ ] Slot `editor` com argumentos é usado como está.
- [ ] Tabela de instalação (macOS/Windows/Linux × git/gh) igual nas 3 skills.
- [ ] `tests/test_agnostico.py` verde com o texto novo.
- [ ] Job `testes-windows` (Git Bash + Python nativo) nos 2 workflows; relatório com o que passou, o que foi pulado
      (com motivo) e o que foi consertado; os 5 achados guardados medidos (CRLF do curator, `tasklist` do
      `sdd-drive.sh`, `report-lint`, `sdd-archive`, `O_NOFOLLOW` da trava).
- [ ] Frase de Windows do README e do quickstart (2 idiomas cada) diz exatamente o que foi provado; piso decidido
      pelo Roberto com os números.
- [ ] Tempo do job Windows medido e teto conferido antes da tag.
- [ ] Release com `SHA256SUMS.txt` conferido.

### Restrições
- bash 3.2, sem zsh, sem link simbólico no pacote; `sdd/bin/*.sh` sempre com `bash`.
- `checar-ambiente` continua somente leitura; teto de tempo em toda consulta de rede.
- Texto de skill não presume VS Code, macOS nem um agente só (`test_agnostico.py`).
- Tabela de instalação repetida nas 3 skills (cada uma é instalada sozinha; a F17 as gera como zip).
- Tetos do CI: olhar o teto **antes** da tag; tag com job cancelado fica sem Release e não se move.
- Repositório público: nada da RDD.

### Fora do escopo (confirmado)
- Instalar algo pelo aluno; `gh` obrigatório; `sdd-release`; o starter (F17); job de WSL; prova manual em Windows
  real.

---

## Resumo da sessão

| Métrica | Valor |
|--------|-------|
| Perguntas | 6 |
| Abordagens | 3 |
| Removidas (YAGNI) | 6 |
| Validações | 2 |

---

## Próximo passo

**Pronto para:** `/sdd-define sdd/features/BRAINSTORM_F16_AMBIENTE.md`
