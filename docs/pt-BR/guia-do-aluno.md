# Guia do aluno — SDD Open passo a passo

> Para quem nunca usou git, terminal ou programou. Se você já conhece essas coisas, o
> [Quickstart](quickstart.md) é mais direto.

O SDD Open é um conjunto de 17 **skills** — roteiros que a IA segue para trabalhar com método — mais
alguns conferidores que rodam no seu computador. Cada skill faz uma coisa só, conversa com você em
etapas e **não faz nada que não se desfaz sem você escolher**. Este guia mostra o caminho inteiro:
preparar o computador, criar o primeiro projeto e publicá-lo.

---

## Sumário

1. [O que você precisa](#1-o-que-você-precisa)
2. [Instalar e chamar uma skill](#2-instalar-e-chamar-uma-skill)
3. [Como as skills falam com você](#3-como-as-skills-falam-com-você)
4. [O mapa do caminho](#4-o-mapa-do-caminho)
5. [Catálogo das skills](#5-catálogo-das-skills)
6. [Seu primeiro projeto, do zero à publicação](#6-seu-primeiro-projeto-do-zero-à-publicação)
7. [O dia a dia depois do primeiro projeto](#7-o-dia-a-dia-depois-do-primeiro-projeto)
8. [Quando algo dá errado](#8-quando-algo-dá-errado)
9. [Glossário](#9-glossário)
10. [Perguntas frequentes](#10-perguntas-frequentes)

---

## 1. O que você precisa

**Ter:**
- um computador (Mac, Windows ou Linux);
- uma conta no [GitHub](https://github.com) — gratuita; é onde a cópia de segurança do seu projeto
  vai morar;
- um **agente de código**: o programa em que você conversa com a IA e que mexe nos arquivos. Qualquer
  um destes sete serve, e as skills são as mesmas em todos: Claude Code, Codex CLI, Gemini CLI,
  Cursor, Kimi Code, Grok Build ou GLM via Claude Code;
- três programas que os conferidores usam:
  - **git** — guarda o histórico de versões;
  - **bash 3.2 ou mais novo** — já vem no Mac e no Linux; no Windows, use o Git Bash (vem com o git)
    ou o WSL;
  - **python3 3.9 ou mais novo** — as fases rodam pequenos conferidores escritos nele (o do Verify
    Gate, o do relatório, o do design).

Não sabe se tem os três? A skill `sdd-checar-ambiente` olha por você e diz o comando que resolve cada
falta.

**Não precisa saber:**
- git, terminal, programação ou qualquer palavra deste guia que você ainda não conheça. Toda vez que
  um termo aparece pela primeira vez, a skill explica — e o [Glossário](#9-glossário) no fim reúne
  todos.

**A promessa das skills:** uma etapa por vez, sempre dizendo o que já foi feito, o que vem agora e
quais são as suas opções. Quando precisar de algo que você ainda não tem instalado, a skill **para**,
diz o que fazer e espera você voltar. Nada é publicado, apagado ou enviado para fora sem o seu OK.

---

## 2. Instalar e chamar uma skill

### Instalar

O SDD Open é instalado **dentro do projeto**: as skills ficam na pasta `.agents/skills/` e as regras
do método no arquivo `AGENTS.md`, que todo agente lê. Abra o agente na pasta do projeto e peça para
ele rodar, um por vez (troque `codex` pelo seu agente: `claude`, `codex`, `gemini`, `cursor` ou
`kimi`; Grok Build e GLM usam `claude`):

```bash
git clone https://github.com/robertodiasduarte/sdd-open.git ~/sdd-open
bash ~/sdd-open/bin/sdd-open.sh init --vendors codex --dry-run
bash ~/sdd-open/bin/sdd-open.sh init --vendors codex --yes
```

1. O `git clone` baixa o pacote para a pasta `sdd-open` da sua pasta pessoal. É lá que ele fica para
   as próximas atualizações.
2. O `--dry-run` mostra o plano — o que vai ser criado (`+`), o que muda (`~`) e o que já está certo
   (`=`) — **sem escrever nada**. Leia.
3. O `--yes` aplica o plano. Ele é necessário porque o agente roda o comando sem um terminal onde
   você possa digitar "y": sem o `--yes`, o `init` responde `CANCELADO` e não escreve nada.

No fim, o `init` roda o `doctor` (o diagnóstico) e diz, por agente, o que foi preparado. Nada seu é
sobrescrito: se você já tem um `AGENTS.md`, o SDD Open só cuida do trecho entre os marcadores
`<sdd-open-instructions>`.

**Projeto que ainda não usa git?** O `init` para e diz "rode `git init` aqui". Antes, confira que a
pasta **não** está dentro do iCloud, OneDrive, Dropbox ou Google Drive (eles corrompem o histórico do
git); depois rode `git init -b main`, que só cria o git vazio — nada é salvo ainda — e repita o
`init`. A `sdd-iniciar-repo` cuida do resto (seção 6).

**Quando sair versão nova:**
1. `git pull` dentro da pasta `~/sdd-open`;
2. `bash ~/sdd-open/bin/sdd-open.sh doctor` na pasta do projeto — ele aponta cada skill mais velha
   que o pacote;
3. para cada skill apontada, apague a pasta dela em `.agents/skills/` e rode o `init` de novo com
   `--yes` (edições que você fez nela se perdem);
4. `bash ~/sdd-open/bin/sdd-open.sh sync`, que regenera as cópias de cada agente.

O `sync` sozinho não traz versão nova: ele só copia o que já está em `.agents/skills/`.

### Chamar uma skill

Você chama uma skill pelo nome, dentro da conversa com o agente. Em qualquer um dos sete, uma frase
basta:

> use a skill **sdd-checar-ambiente** para ver se meu computador está pronto

> use a skill **sdd-brainstorm** — quero um app para controlar as notas fiscais do escritório

Cada agente também tem um atalho:

| Agente | Atalho | O que o `init` prepara |
|---|---|---|
| Claude Code | `/sdd-define …` | `CLAUDE.md` e cópias em `.claude/skills/` |
| Codex CLI | `$sdd-define …`, ou peça pela descrição | nada: lê `AGENTS.md` e `.agents/skills/` direto |
| Gemini CLI | `/sdd-define …` | `GEMINI.md` e `.gemini/settings.json` |
| Cursor | `/sdd-define …` | cópias em `.cursor/skills/` |
| Kimi Code | `/skill:sdd-define …` | nada: lê `AGENTS.md` e `.agents/skills/` direto |
| Grok Build · GLM via Claude Code | `/sdd-define …` | o mesmo do Claude Code |

As cópias de cada agente são **geradas**: quem manda é `.agents/skills/`.

### Como saber que a skill certa carregou

A primeira resposta de toda skill começa com uma **linha de identificação**, assim:

```text
sdd-release v2.3.1 · out/2026 · versão atual: https://github.com/robertodiasduarte/sdd-open/releases/latest
```

Se essa linha não aparecer, a skill não foi carregada: confira a instalação e repita o pedido com o
nome exato. A versão da linha é a da skill no seu projeto; o link mostra a mais nova publicada.

---

## 3. Como as skills falam com você

Toda resposta de uma skill tem **cinco partes**, sempre na mesma ordem. Depois de duas ou três
respostas você lê de olho fechado.

| Parte | O que traz |
|---|---|
| **Status** | A linha do andamento, com o nome da fase na frente: `Define: ✅ 1 Ler o brainstorm · ▶️ 2 Requisitos · ⬜ 3 Testes` |
| **O que foi feito** | O resultado da etapa anterior, em palavras — nunca a saída crua de um comando |
| **Agora: etapa N — nome** | Em que ponto estamos e o que esta etapa faz |
| **Sua decisão** | A pergunta, com as opções escritas e o efeito de cada uma |
| **Próximo passo** | O que acontece depois da sua resposta |

### Os ícones do Status

| Ícone | Significa |
|---|---|
| ✅ | etapa concluída |
| ▶️ | etapa em andamento (onde estamos) |
| ⬜ | etapa ainda por fazer |
| ⏸️ | parada: falta algo que só você pode resolver |
| ➖ | etapa que não se aplica desta vez (com o motivo registrado) |

No fim de cada fase, a skill fecha com um **resumo de etapa**: um quadro de todas as fases (✅ feita,
🏃 a atual, ⬜ por fazer, ➖ pulada), onde estamos, o que precisa de você e o que vem depois.

### Dois tipos de pergunta

- **Autorização** — a skill quer fazer algo e pede permissão. Vem com as opções e o efeito de cada
  uma; a **recomendada vem primeiro**, marcada como "(recomendado)", com o motivo.
- **Pergunta aberta** — a skill precisa de uma informação sua (o nome do projeto, um tempo máximo).
  Vem com orientação de como responder.

**"Não sei" é resposta válida em qualquer pergunta** — a skill explica com um exemplo e pergunta de
novo. Nunca chute. E não há opção "Outro": se você quer algo diferente das opções, diga com as suas
palavras, e a skill trata como dúvida — responde e repete as opções.

### A parada ⏸️

Quando falta algo que a skill não pode fazer por você (instalar um programa, entrar na sua conta do
GitHub, abrir uma sessão nova do agente), ela:

1. marca ⏸️ no Status;
2. diz **por que parou**, em uma frase;
3. diz **onde** você vai resolver (qual programa, qual site, qual janela);
4. lista os **passos** numerados e o que você deve ver na tela;
5. garante o que **não foi feito** ("Nada foi publicado");
6. quando a parada é por uma conferência que precisa de alguém sem esta conversa, traz duas linhas a
   mais: **Brief** (o arquivo com o pedido já escrito) e **Sessão nova** (como abrir o agente de novo
   e colar o pedido);
7. fecha com: **"Quando terminar, me peça de novo, eu continuo daqui."**

Resolva, volte à conversa e repita o pedido original. A skill retoma de onde parou.

### O Verify Gate e os números que ele devolve

O **Verify Gate** é o teste que decide se uma feature ficou pronta: um comando escrito no Define, que
o Build e a Release rodam. Ele devolve um número, e a skill traduz:

| Número | Quer dizer | O que acontece |
|---|---|---|
| `0` | pronto | a fase segue |
| `2` | o teste falhou | a skill corrige o que construiu e roda de novo; não termina com teste falhando |
| `3` | não deu para conferir | falta uma ferramenta no computador; a skill diz qual |
| `4` | precisa da sua assinatura | o aceite é visual: você confere a lista e responde com nome e data |
| `5` | a spec tem uma dúvida marcada | volte ao Define e responda a dúvida |
| `64` | o Define não tem um Verify Gate válido | volte ao Define |

---

## 4. O mapa do caminho

As 17 skills se dividem em quatro blocos, na ordem em que você vai usá-las.

```text
PREPARAR (uma vez por computador e por projeto; a new-session, a cada frente)
   sdd-checar-ambiente ──► sdd-iniciar-repo ──► sdd-higiene-dado ──► sdd-new-session
   "está tudo pronto?"      "pôr no git"         "alarme contra      "abrir uma frente
                                                  dado de cliente"    de trabalho"

CRIAR (uma vez por feature — o fluxo SDD)
   sdd-kb ──► sdd-brainstorm ──► sdd-define ──► sdd-governanca ──► sdd-ux-review ──► sdd-design ──► sdd-build
 (opcional)  "lapidar a ideia"  "o que precisa   (se trata         (se tem tela,     "como será      "a IA
 "ensinar                        fazer"           dinheiro)         arquivo ou        feito"          constrói"
  o contexto"                                                       mensagem)

FECHAR (no fim de cada sessão e de cada frente)
   sdd-handoff ──► sdd-release
   "passar o bastão"  "publicar"

TRANSVERSAIS (quando o caso pedir)
   sdd-iterate · sdd-playbook · sdd-prompt-builder · sdd-auditoria-harness
```

**A regra de ouro do método:** cada fase lê o documento que a anterior gravou. Não pule fases e
**nunca siga para a próxima com um documento que você não leu**. Corrigir uma frase no Define custa
minutos; corrigir depois que a IA construiu o app custa horas.

**Onde ficam os documentos**, todos dentro da pasta `sdd/` do projeto:

| Pasta | O que guarda |
|---|---|
| `sdd/features/` | `BRAINSTORM_NOME.md`, `DEFINE_NOME.md`, `DESIGN_NOME.md` |
| `sdd/reviews/` | as revisões de governança, de UX e do avaliador |
| `sdd/reports/` | `BUILD_REPORT_NOME.md` e, em `evidence/`, a prova de cada verificação |
| `sdd/handoffs/` | `HANDOFF_NOME.md`, a ficha da feature |
| `sdd/releases/` | o registro de cada publicação (ledger) |
| `sdd/kb/` | as bases de conhecimento |
| `sdd/config.yaml` · `sdd/playbook.md` | os comandos do projeto e as armadilhas já conhecidas |

A pasta `sdd/` **entra no git** junto com o código: é o histórico das decisões do projeto, e é ela que
deixa uma sessão nova continuar de onde a outra parou. O que não pode ir para o git é dado de
cliente, senha e certificado — e para isso existe o alarme da `sdd-higiene-dado`.

---

## 5. Catálogo das skills

Cada ficha tem o mesmo molde: para que serve, quando usar, quando não usar, como pedir (frase pronta
para copiar), o que produz e o que ela vai te perguntar. A ordem é a do mapa, não a alfabética — quem
está começando não sabe o nome da skill, sabe em que momento está.

### Bloco 1 — Preparar

#### sdd-checar-ambiente

| | |
|---|---|
| **Para que serve** | Olha o computador e o projeto e diz se está tudo pronto para trabalhar — sem mudar nada. |
| **Quando usar** | Depois de instalar; antes da primeira frente num projeto; quando algo estranho acontecer (um comando que não existe, um commit que falha); quando outra skill mandar. |
| **Quando não usar** | Para consertar: ela só diagnostica. O conserto é com o comando ou a skill que ela indicar. |
| **Como pedir** | *"use a skill sdd-checar-ambiente"* |
| **O que produz** | Uma linha ("tudo certo") ou uma lista do que impede, a mais grave primeiro, cada item com o comando que resolve. Nenhum arquivo. |
| **O que vai perguntar** | Nada — é só leitura. |

#### sdd-iniciar-repo

| | |
|---|---|
| **Para que serve** | Põe no git e numa cópia privada no GitHub um projeto que ainda não tem nenhuma versão salva — sem levar junto senha, certificado digital ou dado de cliente. |
| **Quando usar** | Logo depois do `git init` e do `init` do SDD Open, num projeto novo; ou quando a `sdd-new-session` disser que o projeto não está no GitHub. |
| **Quando não usar** | Projeto que já está no GitHub (ela avisa e para). Pasta dentro do iCloud, OneDrive, Dropbox ou Google Drive — ela pede para mover antes. |
| **Como pedir** | *"use a skill sdd-iniciar-repo para pôr este projeto no git"* |
| **O que produz** | O `.gitignore`, o alarme contra dado de cliente (se você aceitar), a primeira versão salva e a cópia num repositório **privado** no GitHub. |
| **O que vai perguntar** | Uma etapa por vez, cada uma com OK: conferir o que há na pasta → separar o que não pode sair → instalar o alarme → salvar a primeira versão → publicar no GitHub. Se encontrar CPF/CNPJ em arquivo, pergunta se são fictícios ou autorizados antes de salvar. |

#### sdd-higiene-dado

| | |
|---|---|
| **Para que serve** | Instala um **alarme de commit**: toda vez que você for salvar uma versão, ele confere e recusa se encontrar CPF ou CNPJ válidos, arquivo de senhas (`.env`), certificado digital (`.pfx`, `.p12`, `.pem`) ou planilha nova. |
| **Quando usar** | Ao preparar a máquina do escritório; quando a `sdd-iniciar-repo` oferecer; quando um commit for recusado e você quiser entender por quê. |
| **Quando não usar** | Para limpar dado que já foi para o git — ela não mexe no histórico. Para parecer sobre LGPD — ela só alarma. |
| **Como pedir** | *"use a skill sdd-higiene-dado para proteger este projeto"* |
| **O que produz** | O alarme instalado no projeto (um arquivo `pre-commit` dentro da pasta `.git`). |
| **O que vai perguntar** | "Posso instalar?" — com as opções e o efeito de cada uma. Quando um commit for barrado: corrigir, é dado fictício, ou gravar mesmo assim (só se você conferiu). |

#### sdd-new-session

| | |
|---|---|
| **Para que serve** | Abre uma **frente de trabalho**: uma cópia isolada do projeto, numa pasta própria fora da pasta do projeto, onde você trabalha numa coisa sem misturar com outra. |
| **Quando usar** | No começo de toda tarefa: nova feature, correção, experimento. |
| **Quando não usar** | Projeto sem nenhuma versão no GitHub — ela percebe, diz o que falta e não cria nada. |
| **Como pedir** | *"use a skill sdd-new-session — quero começar a feature de importar extratos"* |
| **O que produz** | Uma pasta nova, nascida da versão mais recente de produção, aberta no editor. O que ela descobre sozinha (a branch principal, o editor, o comando de testes) vai para o `sdd/config.yaml` da frente, só quando há evidência. |
| **O que vai perguntar** | O nome da frente (ela sugere). Se a conferência antes de criar achar problema (sem acesso ao GitHub, programa faltando), para com ⏸️ e diz o que fazer. |

### Bloco 2 — Criar (o fluxo SDD)

#### sdd-kb

| | |
|---|---|
| **Para que serve** | Monta uma **base de conhecimento**: o que você sabe sobre um assunto (um processo do escritório, uma norma, um manual), organizado para a IA consultar de verdade em vez de você reexplicar em toda conversa. |
| **Quando usar** | Antes de um fluxo SDD sobre um assunto que a IA não conhece; quando você se pega repetindo as mesmas explicações; para catalogar leis, normas e políticas internas (perfil normativo, com o período em que cada regra vale). |
| **Quando não usar** | Para documentação de produto ou manual de uso — a KB é para a IA, não para o cliente. |
| **Como pedir** | *"use a skill sdd-kb — quero ensinar a IA sobre o Simples Nacional do escritório"* |
| **O que produz** | Uma pasta em `sdd/kb/` com conceitos (para entender) e receitas (para fazer), o índice `sdd/kb/_index.yaml` e as fontes registradas. A `sdd-define` passa a citar o domínio pelo nome da pasta. |
| **O que vai perguntar** | Qual é o assunto e onde ele termina; se tem regra que vale por período (sim → perfil normativo); e, no fim, a sua revisão — quem responde pelo conteúdo é você. |

#### sdd-brainstorm

| | |
|---|---|
| **Para que serve** | Entende o problema antes de decidir a solução. Faz perguntas uma por vez, pede exemplos reais, mostra 2–3 jeitos de resolver e recomenda um. |
| **Quando usar** | Toda feature nova começa aqui, principalmente quando a ideia ainda está vaga. |
| **Quando não usar** | Quando problema, público, objetivos e limites já estão claros e escritos — aí vá direto ao Define. |
| **Como pedir** | *"use a skill sdd-brainstorm — quero um app para controlar os honorários do escritório"* |
| **O que produz** | `sdd/features/BRAINSTORM_NOME.md`: o problema, a abordagem escolhida, o que ficou de fora por enquanto. |
| **O que vai perguntar** | No mínimo 3 perguntas de descoberta; se você tem amostras (planilha, relatório, e-mail); qual abordagem seguir; e duas confirmações ("entendi certo?") antes de gravar. |

#### sdd-define

| | |
|---|---|
| **Para que serve** | Transforma o brainstorm numa lista do que o sistema **precisa fazer**, com testes de aceitação e o **Verify Gate** — o comando que decide se ficou pronto. |
| **Quando usar** | Logo depois do brainstorm, com o arquivo gravado. |
| **Quando não usar** | Para decidir como construir — isso é o Design. |
| **Como pedir** | *"use a skill sdd-define com o arquivo sdd/features/BRAINSTORM_HONORARIOS.md"* |
| **O que produz** | `sdd/features/DEFINE_NOME.md`: problema, usuários, objetivos por prioridade, critérios de sucesso com números, testes de aceitação, o que fica fora e o Verify Gate. Antes de entregar, ela confere o arquivo com `sdd/bin/verify-gate.sh --print` e com `sdd/bin/kb-dominios.py` (que só aceita bases que existem em `sdd/kb/`, ou "nenhum"). |
| **O que vai perguntar** | Só o que falta para ficar testável: números ("até 30 segundos ou até 2 minutos?"), casos de borda, o que fazer quando der erro. Uma pergunta principal por vez, com opções e "não sei". O que ela não souber vira uma dúvida marcada no documento, nunca um chute. |

#### sdd-governanca

| | |
|---|---|
| **Para que serve** | Revisão de governança para sistemas que tratam **dinheiro, saldo, lançamento, nota fiscal, tributo, folha ou dado pessoal**: compara o Define com um catálogo de regras (lançamento que não se apaga, partidas dobradas, trilha de auditoria…) e propõe requisitos que faltam. |
| **Quando usar** | Depois do Define e antes do Design, quando o sistema é financeiro, contábil ou fiscal. |
| **Quando não usar** | Sistema sem esses temas — ela responde "não se aplica" em uma linha. |
| **Como pedir** | *"use a skill sdd-governanca com sdd/features/DEFINE_HONORARIOS.md"* |
| **O que produz** | `sdd/reviews/GOVERNANCA_REVIEW_NOME.md` e, para cada lacuna que você mandar aplicar, um requisito novo no Define com o roteiro que prova que a ação proibida falha. |
| **O que vai perguntar** | Item a item: aplicar, recusar com motivo ou adiar. Ela recomenda; quem decide e responde é o profissional. |

#### sdd-ux-review

| | |
|---|---|
| **Para que serve** | Revisa a experiência de quem vai usar: o caminho de cada tarefa, onde a pessoa trava, os estados (vazio, erro, carregando), a acessibilidade — antes que o desenho endureça. |
| **Quando usar** | Em toda feature que alguém lê ou usa: tela, linha de comando, arquivo gerado, e-mail. |
| **Quando não usar** | Rotina que ninguém lê (ela registra o motivo e a fase fica ➖). |
| **Como pedir** | *"use a skill sdd-ux-review com sdd/features/DEFINE_HONORARIOS.md"* |
| **O que produz** | `sdd/reviews/UX_REVIEW_NOME.md`, com os requisitos de interação e o que é obrigatório para o Design. |
| **O que vai perguntar** | Se o Define não diz quem usa e em que situação (ou se você pedir), uma entrevista curta: quem usa, com que frequência, em que aparelho, e uma referência que você goste. |

#### sdd-design

| | |
|---|---|
| **Para que serve** | Decide **como** será feito, por escrito: os blocos do sistema, os arquivos que serão criados, as decisões técnicas e os motivos, como testar, o que fazer em cada erro. |
| **Quando usar** | Depois do Define (e das revisões de governança e UX, quando houver). |
| **Quando não usar** | Com o Define ainda cheio de dúvidas marcadas — ela devolve para responder antes. |
| **Como pedir** | *"use a skill sdd-design com sdd/features/DEFINE_HONORARIOS.md"* |
| **O que produz** | `sdd/features/DESIGN_NOME.md`, com a lista exata de arquivos que o Build vai tocar, conferido por `sdd/bin/design-lint.py`. |
| **O que vai perguntar** | Decisões técnicas que só você pode tomar (onde guardar os dados, com que sistema integrar), sempre com opções e uma recomendada. Se o projeto já tem padrões, ela segue sem perguntar. |

#### sdd-build

| | |
|---|---|
| **Para que serve** | A IA **constrói** o que o Design descreveu — só aqueles arquivos, na ordem, verificando cada passo — e roda o Verify Gate. Só termina quando ele devolve `0`. |
| **Quando usar** | Com o Define e o Design gravados, dentro de uma frente aberta pela `sdd-new-session`. |
| **Quando não usar** | Fora de uma frente, ou com o Design incompleto. |
| **Como pedir** | *"use a skill sdd-build com sdd/features/DESIGN_HONORARIOS.md"* |
| **O que produz** | O código do projeto e `sdd/reports/BUILD_REPORT_NOME.md`, com a prova de cada verificação em `sdd/reports/evidence/`. "Deve funcionar" não vale como prova. |
| **O que vai perguntar** | O **modo** de execução (ela recomenda um); se quer uma revisão por outro agente; e, se descobrir algo que o Design não previu, para e pergunta em vez de improvisar. Em features com mais de uma camada (tela e banco, por exemplo), alguém que não viu a conversa confere o resultado — às vezes isso pede uma parada ⏸️ para você abrir uma sessão nova. |

### Bloco 3 — Fechar

#### sdd-handoff

| | |
|---|---|
| **Para que serve** | Registra o estado do trabalho — feito, pendente, próximos passos, o que não pode quebrar — e gera um **prompt de retomada** que a próxima sessão entende sozinha. |
| **Quando usar** | Ao parar por hoje; quando a conversa ficou longa; ao terminar uma etapa; **sempre** depois do Build. |
| **Quando não usar** | Para escrever manual ou documentação de entrega. Para publicar — isso é a release. |
| **Como pedir** | *"use a skill sdd-handoff — vou parar por hoje"* |
| **O que produz** | `sdd/handoffs/HANDOFF_NOME.md` (um por feature, etapa nova no topo) e o bloco de texto para colar na próxima sessão. |
| **O que vai perguntar** | Quase nada: ela procura a ficha que a feature já tem e a atualiza; se não tiver certeza de qual é, propõe uma e confirma. |

#### sdd-release

| | |
|---|---|
| **Para que serve** | Leva a frente para produção com **um único ponto de aprovação**: confere sozinha (Verify Gate, relatório, segredo, base atualizada), mostra uma vez o que vai subir e só publica depois do seu OK. |
| **Quando usar** | De dentro da pasta da frente, quando o trabalho está pronto e o handoff feito. |
| **Quando não usar** | Com trabalho pela metade ou teste falhando — ela detecta e não publica. |
| **Como pedir** | *"use a skill sdd-release para publicar esta frente"* |
| **O que produz** | A versão integrada em produção e conferida, o registro em `sdd/releases/` e a ficha da feature atualizada. |
| **O que vai perguntar** | Uma pergunta só, no fim de um bloco que diz o que sobe (em palavras), o que muda em produção, se o envio publica sozinho e se a publicação espera os testes — **sim** publica, **não** encerra sem mudar nada. |

### Bloco 4 — Transversais (quando o caso pedir)

#### sdd-iterate

| | |
|---|---|
| **Para que serve** | Corrige um documento de fase (brainstorm, define ou design) quando o requisito ou o desenho muda no meio do caminho, mantendo o histórico e o Verify Gate coerentes. |
| **Quando usar** | "Mudou o requisito", "o design não funciona assim", ou quando o Verify Gate falha porque a premissa da spec estava errada. |
| **Quando não usar** | Para corrigir código — isso é o Build. |
| **Como pedir** | *"use a skill sdd-iterate — o cliente agora quer o relatório por semana, não por mês"* |
| **O que produz** | O documento atualizado no lugar, com a mudança registrada no histórico dele. |
| **O que vai perguntar** | Se a mudança deve descer para o documento seguinte (do Define para o Design, por exemplo) antes de fazer isso. |

#### sdd-playbook

| | |
|---|---|
| **Para que serve** | Mantém o **playbook** do projeto (`sdd/playbook.md`): as armadilhas que já morderam (landmines), cada uma com um código e o que fazer no lugar. As fases consultam o playbook antes de mexer num arquivo. |
| **Quando usar** | Ela trabalha sozinha em toda sessão; você a chama para ver ou revisar as armadilhas registradas. |
| **Quando não usar** | Para apagar ou reescrever o playbook — ele só cresce por acréscimo aprovado. |
| **Como pedir** | *"use a skill sdd-playbook — o que já mordeu neste projeto?"* |
| **O que produz** | Propostas de armadilha nova; quem aplica é a Release, com o seu OK em cada uma. |
| **O que vai perguntar** | Na Release: aprovar ou não cada armadilha proposta. |

#### sdd-prompt-builder

| | |
|---|---|
| **Para que serve** | Escreve e refina os **prompts que o seu sistema vai usar em produção** (quando o app que você está construindo também chama uma IA por dentro). |
| **Quando usar** | Quando o Design ou o Build criar ou alterar um prompt do sistema. |
| **Quando não usar** | Para textos lidos por pessoas (e-mail, manual, aviso na tela). |
| **Como pedir** | Em geral o Build chama sozinho; para usar à mão: *"use a skill sdd-prompt-builder para o classificador de extratos"* |
| **O que produz** | O prompt com contrato de saída e critérios de completude. |
| **O que vai perguntar** | O que entra, o que deve sair e o que fazer quando faltar contexto. |

#### sdd-auditoria-harness

| | |
|---|---|
| **Para que serve** | Faxina: inventaria tudo que o projeto acumulou de configuração de IA (comandos, skills, instruções, scripts) e aponta o que ninguém usa e o que ficou diferente do código — sem alterar nada. |
| **Quando usar** | Quando "a configuração cresceu demais" ou "os documentos ainda batem com o código?". |
| **Quando não usar** | Para segurança (código malicioso em material de terceiro) — isso pede uma auditoria de segurança, fora deste pacote. |
| **Como pedir** | *"use a skill sdd-auditoria-harness"* |
| **O que produz** | Um relatório `AUDITORIA_SDD_DATA.md`. A limpeza continua sendo decisão sua. |
| **O que vai perguntar** | Nada — é só leitura. |

---

## 6. Seu primeiro projeto, do zero à publicação

Um caso só, do começo ao fim. Imagine: você tem a pasta `Honorarios` com uma planilha e alguns
scripts, e quer transformar em um app que controla os honorários do escritório.

### Dia 1 — Preparar

**1. Conferir a pasta.** A pasta `Honorarios` não pode estar dentro do iCloud, OneDrive, Dropbox ou
Google Drive. Se estiver, mova antes de começar.

**2. Instalar o SDD Open.** Abra o agente **dentro da pasta `Honorarios`** e peça para rodar, um por
vez (troque `codex` pelo seu agente):

```bash
git init -b main
git clone https://github.com/robertodiasduarte/sdd-open.git ~/sdd-open
bash ~/sdd-open/bin/sdd-open.sh init --vendors codex --dry-run
bash ~/sdd-open/bin/sdd-open.sh init --vendors codex --yes
```

O `git init -b main` só cria o git vazio: nada é salvo ainda. Leia o plano do `--dry-run` antes do
`--yes`.

**3. Conferir o computador.**
> use a skill sdd-checar-ambiente

Resposta esperada: uma linha dizendo que está tudo certo, ou a lista do que falta. Se faltar algo
(python3, login no GitHub), siga os passos indicados e repita.

**4. Pôr o projeto no GitHub.**
> use a skill sdd-iniciar-repo para pôr este projeto no git

Ela percebe que o git já existe sem nenhuma versão salva e começa pelo inventário: mostra o que há na
pasta e sinaliza o que não pode sair (senhas, certificado, planilha com dado de cliente). Leia a
lista. Responda cada etapa. Aceite o alarme quando ela oferecer. No fim, o projeto está numa cópia
privada no GitHub.

**5. Abrir a primeira frente.**
> use a skill sdd-new-session — quero começar a feature de controle de honorários

Ela abre uma pasta nova, fora da pasta `Honorarios`, já no editor. **A partir daqui, trabalhe nessa
pasta**, não na original: abra o agente de novo dentro dela.

### Dia 1 — Criar

**6. Brainstorm.**
> use a skill sdd-brainstorm — quero um app para controlar os honorários: quem paga, quanto, quando venceu

Responda uma pergunta por vez. Quando ela pedir amostras, mande a planilha (ou diga que não tem).
Escolha a abordagem recomendada se não tiver motivo para outra. Confirme as duas paradas de
conferência. Resultado: `sdd/features/BRAINSTORM_CONTROLE_HONORARIOS.md`.

**Leia o arquivo.** Se algo saiu errado, diga agora.

**7. Define.**
> use a skill sdd-define com sdd/features/BRAINSTORM_CONTROLE_HONORARIOS.md

Ela vai perguntar o que falta para ficar testável. Resultado:
`sdd/features/DEFINE_CONTROLE_HONORARIOS.md`. **Leia** — principalmente "o que fica fora" e os testes
de aceitação: é isso que o app vai fazer, nem mais nem menos.

**8. Governança e UX.** Este sistema trata dinheiro e tem tela, então rode as duas revisões com o
Define antes de seguir:
> use a skill sdd-governanca com sdd/features/DEFINE_CONTROLE_HONORARIOS.md

> use a skill sdd-ux-review com sdd/features/DEFINE_CONTROLE_HONORARIOS.md

**9. Design.**
> use a skill sdd-design com sdd/features/DEFINE_CONTROLE_HONORARIOS.md

Decisões técnicas com opções e uma recomendada. Resultado:
`sdd/features/DESIGN_CONTROLE_HONORARIOS.md`. **Leia**: é a última parada barata.

### Dia 2 — Construir e fechar

**10. Build.**
> use a skill sdd-build com sdd/features/DESIGN_CONTROLE_HONORARIOS.md

Aceite o modo recomendado. Acompanhe o contador de tarefas no Status (`3 Tarefas 2/5`). No fim, ela
roda o Verify Gate; se falhar, corrige e repete — não termina com teste falhando. Resultado: o app
construído e `sdd/reports/BUILD_REPORT_CONTROLE_HONORARIOS.md`.

**11. Handoff.**
> use a skill sdd-handoff

Registra tudo e entrega o prompt de retomada. Guarde-o: é como você continua amanhã.

**12. Release.**
> use a skill sdd-release para publicar esta frente

Leia o bloco "o que sobe". Se estiver certo, **sim**. Pronto: a feature está em produção e a frente,
fechada.

---

## 7. O dia a dia depois do primeiro projeto

**Toda sessão de trabalho tem o mesmo ritmo:**

1. `sdd-new-session` — abre a frente (ou entre na pasta da frente que já existe).
2. Trabalhe: o fluxo SDD de uma feature, ou a continuação de uma.
3. `sdd-handoff` — antes de parar, sempre. Mesmo que tenha feito pouco.
4. `sdd-release` — só quando a frente está pronta.

**Para retomar:** abra o agente na pasta da frente e cole o prompt de retomada que o handoff gerou. Ele
manda ler `sdd/handoffs/HANDOFF_NOME.md` e traz o que a sessão nova precisa.

**Uma frente por assunto.** Se no meio da feature A surgir a urgência B, abra outra frente para B.
Elas não se misturam — é para isso que a `sdd-new-session` existe.

**Quando a IA não conhece o assunto** (uma norma, um processo seu), monte a base com a `sdd-kb` antes
do brainstorm. As fases seguintes partem do terreno mapeado.

**Mudou o combinado no meio do caminho?** Peça a `sdd-iterate` em vez de editar o documento à mão:
ela mantém o histórico e o Verify Gate coerentes.

---

## 8. Quando algo dá errado

As skills já tratam os casos abaixo. O que você precisa saber é só como reagir.

| O que aconteceu | O que fazer |
|---|---|
| **Status com ⏸️** | Falta algo que só você resolve. Siga os passos numerados (onde, o quê, o que ver na tela), volte e repita o pedido. Nada foi publicado. |
| **O `init` respondeu `CANCELADO`** | Faltou o `--yes`: o agente rodou sem um terminal onde você pudesse confirmar. Rode o `--dry-run`, leia o plano e repita com `--yes`. |
| **"este comando precisa de um repositório git"** | A pasta ainda não usa git. Confira que ela não está numa pasta sincronizada, rode `git init -b main` e repita o `init`. |
| **Verify Gate devolveu `2`, `3`, `4`, `5` ou `64`** | Veja a tabela da seção 3: `2` a skill corrige; `3` falta uma ferramenta; `4` precisa da sua assinatura; `5` volte ao Define e responda a dúvida; `64` volte ao Define. |
| **Commit recusado pelo alarme** | O arquivo tem CPF/CNPJ, senha ou certificado. Escolha: **corrigir** (tirar o dado), **é dado fictício** (ela registra e libera) ou **gravar mesmo assim** (só se você conferiu que pode sair do computador). |
| **Release não publicou** | Teste falhou, há segredo no que ia subir, ou a base está desatualizada. A skill diz qual. Corrija na frente e peça a release de novo. |
| **O `doctor` diz que uma skill está mais velha que o pacote** | Apague a pasta da skill em `.agents/skills/` e rode o `init` de novo com `--yes`; depois, `sync` (seção 2, "Quando sair versão nova"). |
| **A skill respondeu sem Status nem opções** | A skill pode não ter carregado, ou a versão é antiga. Confira a linha de identificação e rode o `doctor`. |
| **"Não reconheço este erro"** | Peça a `sdd-checar-ambiente` e, se persistir, copie a resposta e peça ajuda a quem conhece git. |
| **Perdi a conversa** | Abra o agente na pasta da frente e cole o último prompt de retomada. Se não tiver, peça: *"leia sdd/handoffs/HANDOFF_NOME.md e me diga onde paramos"*. |

**O que nunca fazer:**
- rodar um comando copiado da internet "para destravar" — pergunte à skill primeiro;
- desligar o alarme de commit para "ir mais rápido";
- publicar sem ler o bloco "o que sobe";
- trabalhar na pasta original do projeto quando há uma frente aberta;
- editar as cópias em `.claude/skills/` ou `.cursor/skills/`: elas são regeneradas pelo `sync`.

---

## 9. Glossário

| Termo | Em palavras |
|---|---|
| **agente de código** | O programa em que você conversa com a IA e que mexe nos arquivos (Claude Code, Codex CLI e os outros da seção 1). |
| **skill** | Um roteiro que a IA segue para fazer uma coisa com método. |
| **git** | O programa que guarda o histórico de versões do projeto no seu computador. |
| **repositório** | O projeto, com seu histórico, guardado pelo git. |
| **GitHub** | O site onde fica a cópia do repositório, fora do seu computador. **Privado** = só você vê. |
| **commit** | Salvar uma versão: uma foto do projeto naquele momento, com uma mensagem. |
| **alarme de commit** (pre-commit) | Uma conferência automática que roda antes de cada commit e recusa se encontrar dado que não pode sair. |
| **branch** | Uma linha de trabalho separada dentro do repositório. A de produção costuma chamar `main`. |
| **frente de trabalho** (worktree) | Uma pasta própria, com sua branch, onde você trabalha numa coisa sem misturar com outra. |
| **push** | Enviar os commits para o GitHub. |
| **PR** (pull request) | O pedido para integrar uma branch em produção, com revisão e testes automáticos. |
| **CI** | Os testes automáticos que rodam no GitHub a cada envio. |
| **release** | Publicar: integrar a frente em produção. |
| **fluxo SDD** | As fases brainstorm → define → design → build, cada uma lendo o documento da anterior. |
| **abordagem** | Um jeito de resolver o problema; a skill mostra dois ou três e recomenda um. |
| **amostra** | Um exemplo real do que entra e do que deve sair: uma planilha, um relatório, um e-mail. |
| **YAGNI** | A regra de deixar de fora o que não é necessário agora; fica anotado para depois. |
| **requisito** | Uma frase que diz o que o sistema precisa fazer. |
| **teste de aceitação** | A descrição de como saber que o requisito ficou certo. |
| **Verify Gate** | O comando que decide se a feature ficou pronta; devolve `0` quando passou (seção 3). |
| **dúvida marcada** | Um trecho da spec que ainda não tem resposta, escrito no lugar da dúvida; enquanto existir, o Verify Gate devolve `5`. |
| **conferidor** | Um pequeno programa em `sdd/bin/` que uma fase roda para checar o próprio documento. |
| **slot** | Uma linha do `sdd/config.yaml` com um comando do seu projeto (o de testes, o de publicar). Vazio quer dizer "pule este passo e diga que pulou". |
| **adaptador** | A cópia das skills e das regras no formato de um agente (`.claude/skills/`, `CLAUDE.md`). É gerada pelo `sync`; não edite. |
| **`sync`** | O comando que regenera os adaptadores a partir de `.agents/skills/`. |
| **`doctor`** | O diagnóstico da instalação: o que está instalado, o que está mais velho que o pacote, o que falta. |
| **landmine** | Uma armadilha que já mordeu o projeto, registrada no playbook com o que fazer no lugar. |
| **playbook** | O arquivo `sdd/playbook.md`, com as landmines do projeto. |
| **contexto fresco** | Uma sessão do agente que não viu a conversa do build — quem confere não é quem construiu. |
| **evidência** | O arquivo que prova uma verificação (a saída do comando, gravada em `sdd/reports/evidence/`). |
| **bloco do OK** | O quadro que a release mostra antes de publicar: o que sobe, o que muda e se o envio publica sozinho. |
| **ledger** | O registro de cada publicação em `sdd/releases/`. |
| **handoff** | Passar o bastão: o registro do estado do trabalho para a próxima sessão. |
| **prompt de retomada** | O bloco de texto que você cola na próxima sessão para continuar de onde parou. |
| **base de conhecimento** (KB) | O que você sabe sobre um assunto, organizado para a IA consultar, em `sdd/kb/`. |
| **KB Domains** | A linha do Define que diz quais bases de `sdd/kb/` a feature usa (ou "nenhum"). |
| **domínio** | Um assunto com fronteira clara; na KB, uma pasta. |
| **vigência** | O período em que uma regra vale. |

---

## 10. Perguntas frequentes

**Qual agente eu uso?**
O que você já tem. As skills são as mesmas nos sete, e os documentos ficam na mesma pasta `sdd/`. Dá
para preparar mais de um no mesmo projeto: `--vendors claude,codex`.

**Preciso de conta no GitHub?**
Para a `sdd-iniciar-repo`, a `sdd-new-session` e a `sdd-release`, sim — é lá que fica a cópia de
segurança e a integração. Para brainstorm, define e design, não.

**Onde ficam os meus documentos?**
Em `sdd/`, dentro da pasta do projeto (ou da frente), e eles entram no git junto com o código: são o
histórico das decisões e é por eles que uma sessão nova continua. Dado de cliente, senha e certificado
nunca entram — o alarme de commit cuida disso.

**Posso pular o brainstorm?**
Só se problema, público, objetivos e limites já estão claros e escritos. Na dúvida, não pule — custa
15 minutos e evita construir a coisa errada.

**A skill fez uma pergunta que não entendi.**
Responda **"não sei"**. Ela explica com um exemplo e pergunta de novo.

**A skill quer rodar um comando. Posso deixar?**
Se a skill explicou o que o comando faz e você está na etapa em que ela disse que faria isso, sim.
Toda ação que publica, apaga ou envia para fora passa antes por "Sua decisão".

**Quanto tempo leva o primeiro projeto?**
Preparar: 20 a 40 minutos (mais se faltar instalar coisas). Brainstorm + define + design: 1 a 2
horas de conversa. Build: depende do tamanho; a skill mostra o progresso. Em geral, um dia para algo
pequeno.

**Fiz besteira e quero voltar atrás.**
O git guarda todas as versões salvas. Diga ao agente o que aconteceu — e, se não souber explicar,
rode a `sdd-checar-ambiente` e cole a resposta para quem puder ajudar.

**Como sei que as skills estão atualizadas?**
A linha de identificação da primeira resposta traz a versão da skill no seu projeto e o link da mais
nova. O `doctor` compara as duas e diz o que fazer (seção 2, "Quando sair versão nova").

**Eu já uso o sdd-starter. E agora?**
Os nomes das skills coincidem de propósito: use **um ou outro** por projeto. O `doctor` avisa se
encontrar os dois.

---

*Este guia acompanha o SDD Open. Dúvidas e sugestões: abra uma issue no
[repositório](https://github.com/robertodiasduarte/sdd-open).*
