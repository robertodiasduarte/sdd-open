# REVISAO FRONTEIRA: F14_PLAYBOOK

- **Data:** 2026-11-05
- **Commit lido:** `b1348bd` (branch `feat/f14-playbook`; os 4 arquivos lidos estavam sem diff contra o HEAD)
- **Quem revisou:** agente de contexto fresco, despachado pela Decision 12 do DESIGN; não viu a conversa do build
- **Ambiente:** macOS, `/bin/bash` 3.2, git 2.54.0. O 1º lote de sondas (controles, F3, F4, F5, F6) foi repetido com `/usr/bin/python3` 3.9.6, com o mesmo resultado.
- **Logs:** `sdd/reports/evidence/F14_PLAYBOOK/AVAL-FRONTEIRA-01` a `-12-*.log`, gravados com `ev.sh`. Cada log traz o roteiro inteiro, a saída e os exits.
- **Projeto:** nada editado, nenhum commit, add, checkout ou stash; só os 12 logs foram gravados.

## O que foi lido

- `sdd/bin/governanca-fronteira.sh` (inteiro)
- `.agents/skills/sdd-define/SKILL.md`: passo 1.5 (cartógrafo) e passo 11 (itens 1 a 9)
- `tests/test_governanca_fronteira.py` (inteiro); os 14 testes passam com `/bin/bash` + Python 3.9
- `sdd/bin/governanca-bloco.py` (inteiro, pelo encadeamento)
- `sdd/bin/sdd-fluxo.sh`, só `cmd_despachar` (não grava no worktree quando o brief já está no destino)

## Sondas que passaram

- **Controles:** só o relatório ⇒ `MUDOU`, exit 0. Árvore limpa ⇒ 0. Só mtime ⇒ 0. Permitido que não mudou ⇒ 0. Dois permitidos ⇒ 2 `MUDOU`, 0.
- **Escritas fora:** DEFINE não rastreado sobrescrito, arquivo limpo editado, arquivo novo ⇒ `FORA`, exit 1.
- **Nomes:** espaço, tab, aspas, não-ASCII, espaço inicial e final ⇒ `FORA` com o caminho certo. Quebra de linha ⇒ 64. Retorno de carro no nome ⇒ `FORA`.
- **Links:** link no lugar do DEFINE, com o mesmo conteúdo, apontando para dentro ou para fora ⇒ `FORA … (virou ou deixou de ser link)`.
- **Troca de tipo:** arquivo → pasta, DEFINE → pasta vazia ⇒ `FORA`. Arquivo de 0 bytes criado ou apagado ⇒ `FORA`.
- **Git:** commit, commit + amend, commit só do permitido ⇒ `FORA: HEAD mudou`. `stash -u` esquecido ⇒ `FORA`. Repositório aninhado criado pelo agente ⇒ `FORA`.
- **Config:** `status.showUntrackedFiles=no` e `core.quotepath=true` não cegam. `.gitignore` com `sdd/` inteiro ⇒ os arquivos de `sdd/` continuam medidos.
- **Falha fechada:** `chmod 000` no DEFINE ⇒ 64. Snapshot dentro do worktree ⇒ 64. `sdd` como link para fora ⇒ 64.
- **Caminhos:** raiz com espaço, colchete ou asterisco ⇒ correto. `TMPDIR` com barra final ⇒ correto. Rodar de subpasta com permitido absoluto ⇒ correto.
- **Uso legítimo do cartógrafo:** `playbook-lint.sh --grep` e `contexto-lint.sh` entre os snapshots ⇒ só `MUDOU: sdd/contexto/…`, exit 0.
- **Ressalva sem consequência:** rename com `git add -N` gera um caminho-lixo que pode aparecer como `FORA`; sem falso verde nem falso vermelho achado.

## Achados

### F1 — MEDIUM — `governanca-bloco.py` devolve ✅ e exit 0 com `FORA:` no `comparar.txt`, ou com ele vazio

O item 4 do passo 11 manda o stdout do `--comparar` para `comparar.txt` e passa o arquivo ao `governanca-bloco.py`, que só lê as linhas `MUDOU:`. Com `FORA:` no arquivo, ou com o arquivo vazio (fronteira saiu 64), a última coisa que a sessão vê é `✅ bloco válido … tire o marcador de governança`. O vermelho fica só no exit do comando anterior.

- **Reprodução:** DEFINE adulterado entre os snapshots, bloco `NA`; `--comparar > comparar.txt` sai 1; `governanca-bloco.py … --comparar comparar.txt` sai 0. Variante 64: arquivo com quebra de linha no nome ⇒ `comparar.txt` com 0 bytes, bloco sai 0. Variante `REVISADO` + DEFINE adulterado ⇒ 0.
- **Esperado:** bloco inválido (exit 2) sempre que a fronteira não saiu verde.
- **Log:** `AVAL-FRONTEIRA-04-F1-bloco-valido-com-fora-ou-64.log`
- **Correção sugerida:** com `--comparar`, devolver 2 se houver linha `FORA:` ou se faltar a linha exata `RESULTADO: SÓ O PERMITIDO MUDOU`.
- **Teste dos 2 lados:** `FORA:` + NA ⇒ 2; vazio + NA ⇒ 2; só o `RESULTADO:` verde + NA ⇒ 0; `MUDOU: <saida>` + verde + REVISADO ⇒ 0.

### F2 — MEDIUM — A restauração do item 5 apaga o DEFINE quando a cópia não é alcançada

`rm -f DEFINE && cp "$T/DEFINE.antes" DEFINE`: o `rm` vem antes de saber se o `cp` funciona. Variável de shell não persiste entre chamadas do agente; com `$T` vazio ou a cópia ausente, o DEFINE some e nada entra no lugar.

- **Reprodução:** `( unset T; rm -f sdd/features/DEFINE_F.md && cp "$T/DEFINE.antes" sdd/features/DEFINE_F.md )` ⇒ `cp: /DEFINE.antes: No such file or directory`, e `sdd/features/` fica vazia. Com o DEFINE trocado por pasta: `rm: … is a directory`, nada restaurado.
- **Esperado:** falha sem perda.
- **Log:** `AVAL-FRONTEIRA-05-F2-restauracao-apaga-o-define.log`; controles em `AVAL-FRONTEIRA-03-controle-restauracao-do-define.log`.
- **Correção sugerida:** copiar primeiro, trocar depois (`cp cópia DEFINE.restaurando && rm -f DEFINE && mv DEFINE.restaurando DEFINE && cmp`), ou um modo `--restaurar` no script; repetir a fórmula de `T` no item 5.
- **Teste dos 2 lados:** cópia ausente ⇒ exit ≠ 0 e o DEFINE permanece; link para arquivo e para pasta no lugar do DEFINE ⇒ arquivo regular igual à cópia, alvo intocado; DEFINE sobrescrito ⇒ restaurado.

### F3 — MEDIUM — Estado do git fora do snapshot: índice, branch, flags do índice e `.git/` passam como "nada mudou"

- **Reprodução** (cada um entre os 2 snapshots): (a) editar arquivo limpo e `git update-index --assume-unchanged` (ou `--skip-worktree`); (b) `git add -A`; (c) `git checkout -b agente` (ou `--detach`); (d) gravar `.git/hooks/pre-commit` ou acrescentar a `.git/info/exclude` e criar o arquivo escondido.
- **Observado:** nos quatro, `RESULTADO: SÓ O PERMITIDO MUDOU`, exit 0.
- **Esperado:** `FORA`, ou 64.
- **Log:** `AVAL-FRONTEIRA-06-F3-estado-do-git-invisivel.log`
- **Correção sugerida:** 3 linhas a mais no snapshot, comparadas como o `#HEAD`: `#REF` (branch ou DETACHED), `#INDICE` (sha256 de `git ls-files -s -v -z`) e `#GIT` (sha256 do config local, de `info/exclude` e da listagem de `hooks/`). Medido: o hash do índice não muda com `git status`.
- **Teste dos 2 lados:** os 4 cenários ⇒ exit 1 nomeando o que mudou; `git status` e `git diff` rodados pelo agente ⇒ exit 0.

### F4 — LOW — Pasta sem permissão faz o `git status` avisar no stderr e sair 0: enumeração parcial vira verde

- **Reprodução:** `mkdir oculto; printf payload > oculto/p.txt; chmod 000 oculto` entre os snapshots ⇒ exit 0.
- **Log:** `AVAL-FRONTEIRA-07-F4-pasta-ilegivel-vira-verde.log`
- **Correção sugerida:** capturar o stderr do `git status`; não vazio ⇒ 64.

### F5 — LOW — Repositório ou worktree aninhado que já existia entra como `AUSENTE`; escrita dentro é invisível

- **Log:** `AVAL-FRONTEIRA-08-F5-repo-aninhado-ausente.log`
- **Correção sugerida:** percorrer a pasta e gravar um hash dela, ou recusar com 64.

### F6 — LOW — Mudança só de permissão em arquivo já sujo ou não rastreado não é vista

- **Log:** `AVAL-FRONTEIRA-09-F6-so-permissao.log`
- **Correção sugerida:** gravar o modo junto do sha.

### F7 — LOW — Falso vermelho: o permitido escrito de outro jeito no `--comparar` sai `FORA:` para o próprio relatório

`//`, `/./`, caminho relativo e `/var` no lugar de `/private/var` ⇒ `FORA`, exit 1. Permitido relativo no `--snapshot`, chamado de uma subpasta, é resolvido contra a pasta atual.

- **Log:** `AVAL-FRONTEIRA-10-F7-grafia-do-permitido.log`
- **Correção sugerida:** resolver o relativo contra a raiz; no `--comparar`, canonizar e aceitar só o que está entre os `#PERMITIDO` do antes.

### F8 — LOW — Raiz do projeto com `&`, barra vertical ou contrabarra: a lista de arquivos do commit do agente sai errada

A linha 159 interpola a raiz no programa do `sed`. O exit continua 1 (o `FORA: HEAD mudou` segura).

- **Log:** `AVAL-FRONTEIRA-11-F8-raiz-com-e-comercial.log`
- **Correção sugerida:** trocar o `sed` por um laço `while read` com `printf`.

### F9 — LOW — Retomada que refaz o item 2 lava a escrita do revisor

A sessão nova que reexecuta o item 2 inteiro regrava a cópia e o snapshot de antes depois do despacho; a adulteração vira linha de base.

- **Log:** `AVAL-FRONTEIRA-12-F9-retomada-refaz-o-antes.log`
- **Correção sugerida:** separar no texto "recalcule `T`" de "cópia + snapshot de antes"; guarda com um arquivo `fechado`; `cp -n` na cópia.

VEREDITO: NEEDS_WORK — HIGH 0 · MEDIUM 3 (F1, F2, F3) · LOW 6 (F4, F5, F6, F7, F8, F9)
