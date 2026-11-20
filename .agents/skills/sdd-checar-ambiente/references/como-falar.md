# Como falar com o aluno — sdd-checar-ambiente

Quem roda esta skill quer ser desbloqueado, não ler. O relatório do `checar.sh` já sai no formato do
aluno: blocos 🔴 e ⚠️ com o comando que resolve e uma linha ✅ no fim. A resposta é o Status e, logo
abaixo, esse relatório inteiro. O resto da moldura vale na conversa que segue, quando o aluno pergunta
por um item. Este arquivo dá as palavras e três exemplos inteiros.

## Glossário (explique na primeira vez em que o termo aparecer, quando o aluno perguntar)

- ambiente — "o computador, a pasta e os programas onde o projeto roda";
- repositório (git) — "a pasta do projeto com o histórico de versões";
- remoto — "a cópia do projeto guardada no GitHub (ou em outro serviço)";
- pasta sincronizada — "uma pasta que o iCloud, o OneDrive, o Dropbox ou o Google Drive copiam sozinhos;
  ali o histórico do projeto se corrompe";
- frente — "uma pasta separada para uma tarefa, ao lado do projeto";
- identidade do git — "o nome e o e-mail que vão em cada versão salva";
- dado exposto — "uma senha, um certificado ou uma chave que já estão salvos no histórico do projeto";
- skill duplicada — "a mesma skill instalada em dois lugares que o seu agente lê; ele roda uma só, e pode ser a
  mais velha";
- global — "instalada na sua pasta pessoal: vale para todos os projetos deste computador";
- do projeto — "instalada dentro desta pasta: só vale aqui, e em geral está salva no git";
- lixeira — "a pasta `~/.sdd-lixeira`, onde guardo cada cópia antes de tirá-la; o `desfazer.sh` de lá devolve tudo".

Não fale em `HEAD`, worktree, hooksPath ou `ignore-scripts` sem traduzir: diga o efeito.

## Status desta skill, preenchido

`Ambiente: ✅ 1 Verificar · ▶️ 2 Explicar`

Na limpeza das skills duplicadas (só quando o aluno pede): `Ambiente: ✅ 1 Verificar · ✅ 2 Explicar · ▶️ 3 Limpar`

## Exemplo 1 — resposta à pergunta sobre um item, com decisão (etapa 2 — Explicar)

Situação: o relatório mostrou "Esta pasta está dentro do iCloud"; o aluno pergunta o que isso quer dizer.

**Status** — `Ambiente: ✅ 1 Verificar · ▶️ 2 Explicar`
(no Status: "Verificar" é a conferência que já rodou; "Explicar" é esta conversa sobre o que ela achou.)

**O que foi feito** — Conferi a pasta, o git e a cópia no GitHub. Achei 1 problema que impede o
trabalho: a pasta do projeto está dentro do iCloud. Nada foi mudado.

**Agora: etapa 2 — Explicar** — O iCloud copia os arquivos enquanto o git ainda está gravando o
histórico, e o histórico se corrompe. A saída é mover a pasta para fora da nuvem; leva 2 minutos.

**Sua decisão** — [auto · de rotina] **Quer o passo a passo para mover a pasta para fora do iCloud?**
- **sim** (recomendado) — mostro 2 passos, com o que você deve ver em cada um.
- **não** — fica como está; o problema volta a aparecer na próxima conferência.
- **não sei** — explico o que pode acontecer com o histórico se a pasta ficar no iCloud.

**Próximo passo** — Com o seu sim, mostro os passos e, no fim, rodo a conferência de novo.

## Exemplo 2 — parada (etapa 2 — Explicar)

**Status** — `Ambiente: ✅ 1 Verificar · ⏸️ 2 Explicar`

**Por que parei:** a pasta do projeto precisa sair do iCloud antes de qualquer outra coisa.

**Onde:** no Finder, e depois no terminal.

**Passos:**
1. Arraste a pasta do projeto para `~/Projetos` → a pasta some do iCloud.
2. Abra o terminal e o agente na pasta nova → o agente mostra o nome da pasta nova.

**O que não foi feito:** nada foi mudado no projeto.

Quando terminar, me peça de novo, eu continuo daqui.

## Exemplo 3 — limpeza das skills duplicadas, com decisão (etapa 3 — Limpar)

Situação: o relatório mostrou que o Claude Code roda a `sdd-define` global (2.6.1), não a 2.7.0 do projeto, e
mais 2 skills no mesmo caso; o aluno pediu para limpar. O plano (`--duplicadas`) vem antes, inteiro.

**Status** — `Ambiente: ✅ 1 Verificar · ✅ 2 Explicar · ▶️ 3 Limpar`

**O que foi feito** — Montei o plano sem mudar nada: 3 skills estão na sua pasta pessoal (global) e neste
projeto, e a global, que é a que o Claude Code roda, é a mais velha nas 3.

**Agora: etapa 3 — Limpar** — Tirar as 3 cópias globais faz o Claude Code rodar as do projeto, que são as
mais novas. Elas valem para todos os projetos deste computador: os que não têm cópia própria ficam sem elas.
Cada uma vai para a lixeira antes, e um comando devolve tudo.

**Sua decisão** — [D1 · não se desfaz] **Posso tirar estas 3 cópias globais mais velhas (vão para a lixeira e dá para desfazer)?**
- **sim** (recomendado) — tiro as 3, guardo cada uma antes em `~/.sdd-lixeira` e mostro no fim o comando que desfaz; o Claude Code passa a rodar as do projeto.
- **mostrar o plano como veio** — mostro o plano inteiro de novo, com os caminhos, e pergunto outra vez.
- **não** — nada muda; o aviso volta na próxima conferência.
- **não sei** — explico a diferença entre a cópia global e a do projeto com o exemplo da `sdd-define`.

**Próximo passo** — Com o seu sim, tiro as 3 cópias e mostro o comando que desfaz.

Depois da limpeza, a última linha é sempre `Para desfazer: bash <…>/desfazer.sh`: repita-a ao aluno e rode-a só
se ele pedir para desfazer.

Formato completo de pergunta e de parada: `sdd/templates/fragments/PERGUNTA_DECISAO.md`.
