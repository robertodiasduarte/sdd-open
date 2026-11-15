# Atualizar o SDD Open num projeto

[English](../upgrade.md)

Quando sai versão nova do SDD Open, o projeto não muda sozinho: o `init` nunca sobrescreve o que já existe, e o `sync`
só regenera os adaptadores. Quem leva a versão nova para o projeto é o `upgrade`. Ele copia o que é do pacote e você
não editou, deixa a versão nova **ao lado** de cada arquivo que você editou, e não commita nada.

## Como você fica sabendo

- O `doctor` diz a versão do projeto, a do pacote e a última publicada:
  `✅ versão: projeto v2.17.0 · pacote v2.17.0 · última publicada v2.17.0`. Quando sai uma maior, ele acrescenta
  `⚠️ saiu a v2.18.0 (seu projeto está na v2.17.0)` e o comando para atualizar.
- A `sdd-new-session` (ao abrir uma frente) e a `sdd-release` (no começo da publicação) repassam o mesmo aviso em uma
  frase. Não param nem perguntam nada: você atualiza quando quiser.
- A consulta é um `git ls-remote` anônimo do repositório público, com teto de 5 segundos. Nada do seu projeto é
  enviado. Sem internet, o `doctor` diz `ℹ️ versão nova: não conferida` e segue normalmente.
- Para desligar: `open:` → `check_updates: false` no `sdd/config.yaml` (o projeto todo), ou
  `SDD_OPEN_CHECK_UPDATES=0` no ambiente (só aquele terminal).

## Os comandos

Com o pacote num clone (`~/sdd-open`, como no guia do aluno), de dentro da pasta do projeto:

```bash
git -C ~/sdd-open pull                                  # traz a versão nova do pacote
bash ~/sdd-open/bin/sdd-open.sh upgrade --dry-run       # mostra o plano, sem escrever nada
bash ~/sdd-open/bin/sdd-open.sh upgrade                 # mostra o plano de novo e pergunta [y/N]
```

Com o pacote baixado da página de Releases, troque `~/sdd-open` pela pasta extraída (`sdd-open-v2.18.0`).

## O plano

O `upgrade` compara cada arquivo que o pacote instala (as skills em `.agents/skills/` e os arquivos de `sdd/` que o
`init` copia) com a versão nova e com a instalação anterior, registrada em `sdd/open-instalado.txt`:

| Linha do plano | O que é | O que o `upgrade` faz |
|---|---|---|
| `= N iguais ao pacote novo` | o arquivo já é o da versão nova | nada |
| `+ N novos` | o pacote novo tem e o projeto não | copia |
| `~ N do pacote, sem edição sua` | o arquivo é o que a versão anterior instalou | troca pela versão nova |
| `⚠️ N editados por você` | o arquivo difere da versão anterior e da nova | **não toca**; põe a versão nova ao lado |
| `⚠️ N saíram do pacote` | a versão anterior instalou, a nova não tem mais | **não apaga**; só avisa |

Antes do `[y/N]` ele diz: "Nada que você editou será tocado. Nada será commitado." Até 10 nomes por linha aparecem; o
resto, com `--verbose`.

## Depois

- Cada arquivo editado ganha, em `sdd/upgrade/<versão>/`, o `<arquivo>.novo` (a versão nova) e o `<arquivo>.diff` (o
  que muda do seu para o novo). Mescle quando quiser; a pasta pode ser apagada depois e não precisa ir para o git.
- O `upgrade` termina rodando o `sync` (adaptadores) e o `doctor`, e com `RESULTADO: ATUALIZADO` ou
  `RESULTADO: ATUALIZADO, N PARA MESCLAR`.
- Confira com `git status` e commite numa frente, como qualquer mudança. O `sdd/open-instalado.txt` vai junto: é ele
  que permite ao próximo `upgrade` separar o que é do pacote do que é seu.
- Se algo falhar no meio, o registro não muda: rode o `upgrade` de novo, ele retoma (o que já foi copiado vira "igual").

## Projeto instalado antes da v2.17.0

Esses projetos não têm o `sdd/open-instalado.txt`. Sem ele, o `upgrade` para antes de escrever e pede o pacote da
versão que o projeto tem, com `--de`:

```bash
bash ~/sdd-open/bin/sdd-open.sh upgrade --de v2.12.1    # a tag da versão que o projeto tem (do clone)
# ou, com a pasta do pacote antigo (o nome precisa ser sdd-open-vX.Y.Z):
git -C ~/sdd-open archive --prefix=sdd-open-v2.12.1/ v2.12.1 | tar -x -C /tmp
bash ~/sdd-open/bin/sdd-open.sh upgrade --de /tmp/sdd-open-v2.12.1
```

Não sabe a versão? Veja a mensagem do commit que instalou o SDD Open
(`git log --reverse --oneline -- sdd/playbook.md | head -1`) ou a Release que você baixou. Se a pasta do `--de` não
parecer a versão do projeto (menos da metade dos arquivos batem), o plano avisa antes do `[y/N]`.

## Códigos de saída

`0` atualizado, em dia, simulação ou cancelado · `1` falha de escrita (rode de novo, ele retoma) · `64` uso ou
pré-condição: sem registro e sem `--de`, `--de` que não é pacote, pacote mais velho que o projeto, versão do pacote
desconhecida.
