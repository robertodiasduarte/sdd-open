# ESCOPO: F16 Ambiente agnóstico e proativo

- **Data:** 2026-11-02
- **Escrito para:** a sessão que vai abrir a F16 (brainstorm em diante) numa worktree nova de `origin/main`.
- **Origem:** auditoria de leitura pedida pelo Roberto no sdd-starter (`17c69c4`, v1.5.15), conferida
  depois no Open (`origin/main` = `9508ff0`, `v2.3.1`). Primeiro foi aberta uma frente no starter
  (`feat/agnostico-proativo`), que foi descartada sem código: pela **Decisão 5** a fonte é o Open, e o
  starter recebe estes ajustes quando for gerado a partir dele (**F17**). Decisão do Roberto em 2026-11-02:
  o aluno do starter fica sem os ajustes até a F17 sair (sem remendo no starter).
- **Quadro no plano:** `sdd/features/PLANO_F4_F15_CONSOLIDADO.md`, seção 8, F16.

## 1. Em uma frase

As skills de entrada do Open (`sdd-checar-ambiente`, `sdd-iniciar-repo`, `sdd-new-session`) passam a
**descobrir cedo tudo o que o aluno vai precisar** (`git` **e** `gh`, login, editor) e a **funcionar igual
com qualquer editor ou com nenhum**, inclusive só com Claude Code ou só com Codex no terminal.

- **Proativo:** o que falta aparece no pré-voo, não na última etapa.
- **Agnóstico:** nenhuma instrução presume VS Code, macOS ou um agente só (vale o `tests/test_agnostico.py`).

## 2. Achados (em `origin/main` = `9508ff0`)

Versões de partida: `sdd-checar-ambiente` 1.4.1 · `sdd-iniciar-repo` 1.1.1 · `sdd-new-session` 1.3.0.

### 2.1 `git` e `gh`

| # | Skill | Achado | Onde |
|---|---|---|---|
| A1 | checar-ambiente | `git` conferido ✅ | `scripts/checar.sh:202` |
| A2 | checar-ambiente | **`gh` nunca é conferido por si**: só escolhe a mensagem quando o remoto **já recusou** o acesso. Sem `gh` e sem erro de remoto, a saída é ✅ | `checar.sh:358`, `:380` |
| A3 | checar-ambiente | `gh auth status` não é consultado | — |
| A4 | iniciar-repo | `git` conferido no Passo 0, com passos por sistema ✅ | `SKILL.md:97-104`, `scripts/inventario.sh:46` |
| A5 | iniciar-repo | **`gh` só no Passo 6** (publicar), depois de inventário, alarme e 1º commit | `SKILL.md:264-272` |
| A6 | iniciar-repo | instalar o `gh`: Mac = "baixe o instalador" (sem `brew install gh`); **Linux sem instrução** | `SKILL.md:265` |

### 2.2 `sdd-new-session` e o editor

| # | Achado | Onde |
|---|---|---|
| B1 | Núcleo (fetch + worktree + `.env`) só depende de git ✅ | Passo 2, itens 1–4 |
| B2 | Sem editor não aborta ✅ | `SKILL.md:242` |
| B3 | O slot `editor` vazio cai na lista fechada `code`, `cursor`, `subl` | `SKILL.md:213`; `checar.sh:469` |
| B4 | **macOS: `code`/`cursor` fora do `PATH`** caem em "sem editor" com o app instalado. Prova: o `sdd/ambiente.md` local do Open diz `editor: cursor` porque "o `code` não está no PATH deste computador"; o do starter diz `open -a "Visual Studio Code"` pelo mesmo motivo | `sdd/ambiente.md` dos dois checkouts |
| B5 | Fora da lista: `code-insiders`, `windsurf`, `zed`, JetBrains (`idea`, `pycharm`, `webstorm`) | `SKILL.md:213` |
| B6 | "Sem editor" mostra só o caminho; não diz como continuar só no terminal | `SKILL.md:242` |
| B7 | **Aviso final "Continue na janela nova"** não serve para quem usa só o terminal | `SKILL.md:271` |

## 3. Ajustes

### 3.1 `sdd-checar-ambiente` (1.4.1 → 1.5.0)

1. **`gh` no relatório, modo normal:** ausente ⇒ ⚠️ *"O programa do GitHub para o terminal (gh) não está
   instalado — sem ele, publicar o projeto e logar no GitHub ficam manuais."* com o comando do sistema em
   uso (§3.4). **Nunca 🔴**: quem loga por SSH ou pelo gerenciador de credenciais não precisa dele. Remoto
   fora do GitHub ⇒ não acusa.
2. **`gh auth status`** (só com `gh` presente e remoto do GitHub, ou sem remoto): sem conta ⇒ ⚠️ com
   `gh auth login`. Teto de tempo igual ao do `ls-remote`.
3. **Editor:** a detecção da §3.3, citada no resumo ✅; continua **sem** ⚠️ quando não há editor.
4. `--frente` **não** muda (a frente nasce sem `gh`).
5. Testes em `tests/test_checar.py`: sem `gh` no `PATH` ⇒ ⚠️ e rc 0; stub logado ⇒ nada; stub deslogado ⇒
   ⚠️ `gh auth login`; remoto fora do GitHub ⇒ sem `gh`; `--frente` sem `gh` ⇒ ✅.

### 3.2 `sdd-iniciar-repo` (1.1.1 → 1.2.0)

1. **Passo 0 confere o `gh` junto com o `git`**, como aviso antecipado e não parada: *"Para a última
   etapa (publicar no GitHub) você vai precisar do programa do GitHub para o terminal. Quer instalar agora,
   enquanto eu confiro o resto?"* — **sim** (passos do sistema; sigo quando você voltar) / **depois** (sigo
   e paro só na publicação). Também `gh auth status`, pelo mesmo motivo.
2. `scripts/inventario.sh` imprime a linha `gh: ausente|deslogado|ok`.
3. O Passo 6 mantém a checagem (retomada), com a instalação da §3.4.
4. Teste em `tests/test_inventario.py` para a linha `gh:` (sem `gh`, stub logado, stub deslogado).

### 3.3 `sdd-new-session` (1.3.0 → 1.4.0)

1. **Slot `editor` vazio ⇒ detecção em 2 camadas:**
   - `PATH`: `code`, `cursor`, `code-insiders`, `windsurf`, `zed`, `subl`, `idea`, `pycharm`, `webstorm`;
   - **macOS fora do `PATH`:** `/Applications/<App>.app` ou `~/Applications/<App>.app` (`Visual Studio
     Code`, `Cursor`, `Windsurf`, `Zed`, `Sublime Text`) ⇒ grava `open -a "<App>"` no slot, e dá a dica de
     uma linha (Command Palette → *Shell Command: Install 'code' command in PATH*);
   - **Windows fora do `PATH`:** `code.cmd`/`cursor.cmd` em `%LOCALAPPDATA%\Programs\…`.
2. **O slot `editor` aceita comando com argumentos** (`open -a "Cursor"`), e a skill o usa como está.
3. **Sem editor = modo terminal**, sem ar de falha. O "Próximo passo" vira: 1. abra um terminal novo;
   2. `cd "<pasta da frente>"`; 3. `claude` (ou `codex`, o agente em uso).
4. **Aviso final em duas formas:** com editor, o atual; sem editor, *"⚠️ Continue num terminal novo aberto
   na pasta da frente. Esta sessão do agente continua presa à pasta onde foi aberta — nenhum cd muda isso.
   Build, commit e push rodam lá."*
5. `tests/test_matriz_new_session.py` e `tests/test_agnostico.py` cobrem os textos novos.

### 3.4 Instalação por sistema (repetida nas 3 skills: cada uma é instalada sozinha, e a F17 as gera como zip)

| | git | gh |
|---|---|---|
| macOS | `xcode-select --install` (ou `brew install git`) | `brew install gh` (sem Homebrew: instalador em https://cli.github.com) |
| Windows | `winget install --id Git.Git -e` | `winget install --id GitHub.cli -e` |
| Linux | gerenciador da distribuição (`sudo apt install git`) | https://github.com/cli/cli/blob/trunk/docs/install_linux.md |

Depois de instalar, fechar e abrir o terminal. Login: `gh auth login` → GitHub.com → HTTPS → Yes → Login
with a web browser.

## 4. Fora do escopo

- Instalar algo pelo aluno (as skills indicam o comando; `checar-ambiente` continua somente leitura).
- Tornar o `gh` obrigatório (SSH e gerenciador de credenciais continuam válidos).
- `sdd-release` (já confere `gh auth status` onde precisa).
- O starter: recebe tudo isto pela F17.

## 5. Pronto quando

O ciclo de toda frente desta família (cópia por `git archive HEAD`, `publish-gate.sh` em modo ci,
`unittest discover`, sabotagem, revisão de contexto fresco, PR, OK citando "sdd-open", Release), mais:

1. sem `gh` no `PATH`: `checar.sh` ⇒ ⚠️ do `gh` e rc 0; `checar.sh --frente` ⇒ ✅ sem menção ao `gh`;
2. `gh` stub deslogado ⇒ ⚠️ com `gh auth login`;
3. `inventario.sh` imprime a linha `gh:`;
4. `sdd-new-session` sem editor no `PATH` responde com o modo terminal e o aviso "terminal novo";
5. no macOS com o app do VS Code e sem `code` no `PATH`, o slot recebe `open -a "Visual Studio Code"` e a
   frente abre;
6. `tests/test_agnostico.py` verde;
7. Release com `SHA256SUMS.txt` conferido.
