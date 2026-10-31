# Como falar com o aluno — sdd-checar-ambiente

Quem roda esta skill quer ser desbloqueado, não ler. O relatório do `checar.sh` já sai no formato do
aluno: blocos 🔴 e ⚠️ com o comando que resolve e uma linha ✅ no fim. A resposta é o Status e, logo
abaixo, esse relatório como veio. O resto da moldura vale na conversa que segue, quando o aluno pergunta
por um item. Este arquivo dá as palavras e dois exemplos inteiros.

## Glossário (explique na primeira vez em que o termo aparecer, quando o aluno perguntar)

- ambiente — "o computador, a pasta e os programas onde o projeto roda";
- repositório (git) — "a pasta do projeto com o histórico de versões";
- remoto — "a cópia do projeto guardada no GitHub (ou em outro serviço)";
- pasta sincronizada — "uma pasta que o iCloud, o OneDrive, o Dropbox ou o Google Drive copiam sozinhos;
  ali o histórico do projeto se corrompe";
- frente — "uma pasta separada para uma tarefa, ao lado do projeto";
- identidade do git — "o nome e o e-mail que vão em cada versão salva";
- dado exposto — "uma senha, um certificado ou uma chave que já estão salvos no histórico do projeto".

Não fale em `HEAD`, worktree, hooksPath ou `ignore-scripts` sem traduzir: diga o efeito.

## Status desta skill, preenchido

`Ambiente: ✅ 1 Verificar · ▶️ 2 Explicar`

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

Formato completo de pergunta e de parada: `sdd/templates/fragments/PERGUNTA_DECISAO.md`.
