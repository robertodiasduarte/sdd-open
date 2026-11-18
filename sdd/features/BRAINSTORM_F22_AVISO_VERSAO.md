# BRAINSTORM: F22 Aviso de versão e upgrade

> Sessão exploratória para clarear intenção e abordagem antes dos requisitos.

## Metadata

| Atributo | Valor |
|-----------|-------|
| **Feature** | F22_AVISO_VERSAO |
| **Data** | 2026-11-14 |
| **Autor** | brainstorm-agent (sessão com o Roberto) |
| **Status** | Ready for Define |
| **Base** | `feat/f22-aviso-versao`, nascida de `origin/main` `ad32fe1` (`v2.16.0`); passo 0 em `a1a608c` (branch `docs/incorporar-starter`) |

---

## Ideia inicial

**Entrada (pedido do Roberto, 2026-11-14, para ele e para os alunos):** quem instalou o Open pelo `init` não fica
sabendo que saiu versão nova, e atualizar é trabalho manual que o aluno não sabe fazer. Medido no 1º projeto que subiu 3
versões de uma vez (`v2.12.1` → `v2.15.0`): o upgrade exigiu classificar à mão cada arquivo do `MANIFEST.txt` da tag
nova contra a velha (`git archive` das duas): igual (157) · novo (46, sendo 27 dentro de skills que já existiam, que o
`init` não completa) · cópia intacta da tag velha → copiar (43) · editado no projeto → não tocar (3:
`sdd/invariants.md`, `sdd/patterns/README.md`, `sdd/playbook.md`); só depois `init` + `sync` + `doctor` pela tag nova.

**Contexto levantado (conferido em `ad32fe1`):**
- **O pacote não sabe a própria versão.** Não há arquivo de versão; a tag existe só no git (e no nome da pasta do
  tarball da Release, `sdd-open-vX.Y.Z/`). A Release de patch é calculada no CI (`scripts/next-version.sh`) e a tag é
  criada pelo `gh release create` **depois** do `git archive` (`.github/workflows/release.yml`, job `release`).
- **`init` e `sync` não gravam a versão instalada.** O `doctor` (`bin/sdd-open.sh:780`) compara o projeto com o pacote
  que rodou ("skills e sdd/bin/ em dia com o pacote"), nunca com a última versão publicada.
- **O `init` não toca o que existe:** copia `sdd/<arquivo>` só quando falta (`sdd_faltantes`, `:612`) e a skill só
  quando o diretório inteiro falta (`aplicar`, `:743`); arquivo novo **dentro** de skill que já existe não chega.
- **O `sync` promete nunca escrever em `sdd/`** (cabeçalho do `sdd-open.sh`) e só regenera os adaptadores a partir de
  `.agents/skills/` do projeto: ele não instala nada do pacote, então não tem versão a gravar.
- **O sinal de hoje é passivo:** a 1ª linha de 26 `SKILL.md` diz `<skill> vX.Y.Z · <mês> · versão atual: …/releases/latest`.
- **`git ls-remote --tags --refs` do repositório público** (medido aqui, 3 vezes): rc 0, 35 tags, 0,7 a 2,6 s; sem
  token, sem API, sem enviar dado do projeto.
- **Carimbo de versão pelo `git archive`** (medido aqui num repositório de teste): um arquivo `VERSION` com
  `$Format:%(describe:tags=true)$` e o atributo `export-subst` sai `v9.1.0` no `git archive v9.1.0` e `v9.1.0-1-g…`
  num commit depois da tag; na árvore de trabalho fica o texto literal (aí vale `git describe`).
- **Candidato (a) confirmado:** `hooks_path_e_nosso` (`:542`) só aceita `sdd/hooks` relativo ou o caminho absoluto que
  resolve para `<esta raiz>/sdd/hooks`; com o `core.hooksPath` absoluto para o `sdd/hooks` de **outra worktree do mesmo
  repositório** (as worktrees dividem o `.git/config`), o `doctor` diz "hooks do open não ligados … (husky, lefthook ou
  outro gerenciador)", falso alarme.
- **Candidato (b) confirmado:** 3 textos de skill do pacote citam `LM-004` no sentido da semente
  (`sdd-build/SKILL.md:189` e `:299`, `sdd-release/references/como-falar.md:119`); num projeto com playbook próprio
  (o `init` nunca o sobrescreve), o número aponta para outra regra ou para nenhuma. Os exemplos de formato da
  `sdd-playbook` e de `docs/playbook-curation.md` usam o ID como exemplo de sintaxe, não como referência: ficam.

**Contexto técnico para o Define:**

| Aspecto | Observação | Implicação |
|--------|-------------|-------------|
| Onde mora | `bin/sdd-open.sh` (init, doctor, verbo novo), um arquivo de versão na raiz do pacote + `.gitattributes`, `release.yml` (tag local antes do `archive`), `sdd-new-session` e `sdd-release` (aviso), `sdd-build` e `sdd-release` (texto do LM-004), `MANIFEST.txt` | sem skill nova; bump das skills tocadas |
| Rede | só o `doctor` (e quem o chama) consulta o remoto; a suíte nunca | desligada por variável de ambiente na suíte; o remoto configurável para teste com repositório local |
| Ordem | a F16W2 mexe em `sdd/bin`, no `checar`, na `sdd-new-session` e no adaptador do Claude Code | build só depois de a F16W2 publicar; DESIGN reconferido contra a tag nova |
| Starter | `scripts/gerar-starter.py` gera a `sdd-new-session` e a `sdd-release` do starter (modo iniciante) | o passo do aviso depende do `init`: o gerador o tira (ou a trava `check-gerado`/teste reprova a citação) |

---

## Perguntas e respostas

| # | Pergunta | Resposta | Impacto |
|---|----------|--------|--------|
| 1 | Quais das 4 peças entram? | **As 4** (Roberto, 2026-11-14) | versão registrada, checagem no `doctor`, aviso na frente e na release, verbo `upgrade` |
| 2 | Para quem usa só o starter (sem terminal, sem `init`), o que a F22 faz? | **Nada além da 1ª linha** (Roberto): a 1ª linha de cada skill já diz a versão e o link da lista de versões do sdd-starter | o aviso automático é só do Open; o gerador não leva ao starter o passo que depende do `init` |
| 3 | Os candidatos (a) e (b) do mesmo upgrade entram? | **Os dois** (Roberto) | (a) o `doctor` reconhece o `sdd/hooks` de outra worktree do mesmo repositório; (b) os 3 textos citam a regra pelo texto, não pelo número |
| 4 | Como saber que ficou pronto? | **Do pedido:** o projeto privado faz o próprio upgrade numa frente de lá, já pelo verbo novo | prova de uso real fora desta frente; aqui, a prova é o upgrade de uma fixture `v2.12.1` → tag nova reproduzindo a classificação medida |
| 5 | Onde gravar a versão e as impressões? | **Rotina, decidida e registrada:** um arquivo próprio gerado pelo `init`/`upgrade` (ex.: `sdd/open-instalado.txt`: a versão na 1ª linha e `sha256  caminho` por arquivo instalado), não o `sdd/config.yaml` | o config é editado pela pessoa; 600 linhas de hash nele atrapalham a leitura e a mescla; o arquivo próprio é commitado com o projeto, então o upgrade funciona em qualquer clone, sem rede |
| 6 | O `sync` grava a versão? | **Rotina: não.** O `sync` não instala nada do pacote (regenera adaptadores a partir de `.agents/skills/`) e promete não escrever em `sdd/` | grava quem instala: `init` e `upgrade` |
| 7 | Projeto instalado antes da F22 (sem registro) | **Rotina:** sem registro, o `upgrade` exige `--de <pasta do pacote antigo>` (um `git archive` da tag que o projeto tem) e, sem ele, **para antes de escrever** com os 2 comandos que montam essa pasta; com `--de`, as impressões vêm do pacote antigo e a classificação é a do upgrade à mão | o modo "sem registro, lista tudo que difere" listaria os 43 intactos do caso real, que eram o grosso do trabalho: não ajudaria |
| 8 | Arquivo editado no projeto que o Open também evoluiu | **Rotina:** lista com o diff entre as tags (velha → nova) gravado num arquivo para a mescla à mão; sem mescla automática | o pedido diz "avisa e prepara; quem decide é a pessoa" |

---

## Perfil de risco

| Pergunta | Resposta |
|---|---|
| Quem pode ver? | Nada do projeto sai da máquina: a checagem é um `git ls-remote --tags` anônimo no repositório público (o GitHub vê o IP e a hora, como em qualquer `git fetch`). O registro de versão e impressões fica no repositório do projeto, visível a quem já vê o projeto. |
| Quem pode mudar? | Só a pessoa, rodando `upgrade` na própria máquina: ele escreve arquivos do pacote no projeto e **nunca commita**; o que a pessoa editou não é tocado. A checagem não escreve nada. |
| Quanto alguém pode pedir? | Uma consulta ao remoto por execução do `doctor` (e do aviso da frente e da release), com teto de poucos segundos; sem chamada paga, sem IA, sem envio de arquivo. Opt-out por slot. |

---

## Inventário de amostras

| Tipo | Onde | Qtde | Notas |
|------|----------|-------|-------|
| Upgrade real medido | o pedido do Roberto (projeto privado, `v2.12.1` → `v2.15.0`) | 1 | 157 iguais · 46 novos (27 dentro de skills existentes) · 43 intactos · 3 editados; só os números viajam, nada do projeto |
| Tags públicas | `git archive v2.12.1` e `v2.15.0`/`v2.16.0` deste repositório | 3 | a fixture do teste do upgrade nasce delas (montada em tempo de teste, sem rede: as tags estão no clone) |
| Remoto | `git ls-remote --tags` medido | 3 | 0,7 a 2,6 s; teto proposto de 5 s |

**Como as amostras serão usadas:** o teste de aceitação do `upgrade` instala a `v2.12.1` numa pasta temporária, edita 3
arquivos e confere a classificação contra a tag da frente; o remoto do teste da checagem é um repositório local com
tags (nunca a rede).

---

## Abordagens exploradas

### Abordagem A: Registro próprio + `doctor` que consulta + verbo `upgrade` no `sdd-open.sh` ⭐ Recomendada

**Descrição:** (1) o pacote ganha um arquivo de versão carimbado pelo `git archive` (`export-subst`), com o
`git describe` como reserva na árvore de trabalho e a tag criada localmente no job de Release antes do `archive`;
(2) `init` grava `sdd/open-instalado.txt` (versão + sha256 de cada arquivo que instalou do pacote); (3) o `doctor`
mostra "projeto na vY · pacote vZ" e consulta `git ls-remote --tags` com teto de 5 s: havendo tag maior, ⚠️ com o
comando do upgrade; sem rede, "não conferido"; nunca muda o exit; opt-out por slot; desligado na suíte; (4) a
`sdd-new-session` e a FASE 0 da `sdd-release` repassam a linha do aviso como informação; (5) `sdd-open.sh upgrade`,
rodado do pacote novo, classifica cada arquivo do `MANIFEST.txt` (igual · novo · intacto → copia · editado → lista
com o diff; sem registro, exige `--de`), regrava o registro, roda `init` + `sync` + `doctor` e nunca commita;
`--dry-run` mostra o plano.

**Prós:** uma porta só (`sdd-open.sh`) para instalar, conferir e atualizar; funciona sem rede (o registro está no
projeto); nunca destrói edição; o aviso reaproveita o `doctor`.

**Contras:** o `sdd-open.sh` cresce (~943 linhas hoje); o registro é um arquivo a mais no projeto; o 1º upgrade de
um projeto instalado antes da F22 pede um passo a mais (montar a pasta do pacote antigo para o `--de`).

### Abordagem B: Script separado em `sdd/bin/` (`versao.sh` + `upgrade.sh`)

**Descrição:** a checagem e o upgrade moram em scripts copiados para o projeto pelo `init`.

**Por que não recomendada:** o script do projeto é o **velho** na hora do upgrade (é justamente ele que está
desatualizado), e o upgrade precisa do pacote novo de qualquer jeito; duplica a lógica de instalação do `sdd-open.sh`.

### Abordagem C: Só o aviso e uma receita de upgrade à mão na documentação

**Por que não recomendada:** o Roberto escolheu as 4 peças; a receita à mão é exatamente o trabalho que doeu (600
arquivos classificados um a um).

---

## Abordagem escolhida

| Atributo | Valor |
|-----------|-------|
| **Escolhida** | Abordagem A |
| **Confirmação** | escopo das 4 peças, starter e candidatos confirmados pelo Roberto em 2026-11-14 (3 respostas e o "ok, execute o pipeline até o release"); a forma (A) é rotina, registrada aqui |
| **Motivo** | o upgrade precisa rodar do pacote novo; o registro no projeto dispensa rede e diz "intacto × editado" |

---

## Decisões tomadas

| # | Decisão | Motivo | Alternativa rejeitada |
|---|----------|-----------|----------------------|
| 1 | Versão do pacote por arquivo carimbado no `git archive`, reserva `git describe`, último recurso o nome da pasta `sdd-open-vX.Y.Z` | funciona no tarball da Release, no `git archive` da tag e num clone | arquivo `VERSION` editado à mão a cada release (esquece; a Release de patch é automática) |
| 2 | Registro em arquivo próprio, gravado por `init` e `upgrade` | config legível; `sync` não instala | `open.version` + hashes no `sdd/config.yaml` |
| 3 | A checagem de rede mora no `doctor`; frente e release só repassam a linha | um lugar só para teto, opt-out e "sem rede" | checagem própria em cada skill |
| 4 | Nunca muda exit, nunca bloqueia; sem rede = "não conferido" | pedido explícito | — |
| 5 | Na suíte, a checagem fica desligada por variável de ambiente e o teste dela usa remoto local | a suíte não vai à rede | rede nos testes |
| 6 | `upgrade` nunca commita e nunca sobrescreve o que não sabe se é edição | "avisa e prepara; quem decide é a pessoa" | sobrescrever com backup |
| 7 | Starter: só a 1ª linha da skill (decisão do Roberto); o gerador não leva o passo do aviso | sem terminal não há como conferir | aviso no checar do starter |
| 8 | (a) e (b) entram (decisão do Roberto) | falso alarme no caminho recomendado (worktrees); ID que muda de sentido por projeto | — |

---

## Removidas (YAGNI)

| Sugerida | Motivo | Pode voltar? |
|----------|--------|--------------|
| Mescla automática (3 vias) do arquivo editado no projeto | o pedido é avisar e preparar; mescla errada em `sdd/playbook.md` ou nos hooks é pior que mescla nenhuma | sim, se o uso mostrar que a lista é grande |
| Atualização automática (cron, hook que atualiza) | proibido no pedido | não |
| Checagem pela API do GitHub (Release, notas) | precisa de API e cota; `ls-remote` basta para "há tag maior" | sim, para mostrar as notas |
| Tabela de impressões de todas as versões antigas dentro do pacote | resolveria o projeto sem registro, mas cresce a cada release; `--de` cobre o caso raro | sim |
| Aviso automático no starter | decisão do Roberto (pergunta 2) | sim |
| `sync` gravando versão | o `sync` não instala nada do pacote | não |
| Cache da checagem (uma vez por dia) | 1 consulta de ~1 s por `doctor` é barata | sim, se incomodar |

---

## Requisitos sugeridos para o /sdd-define

**Problema:** quem instalou o Open pelo `init` não sabe que saiu versão nova, e atualizar exige classificar à mão
centenas de arquivos entre "do pacote" e "editado aqui".

**Usuários:** o Roberto e os alunos que usam o Open com terminal (Claude Code, Codex, Cursor…), em macOS, Linux e
Windows (Git Bash).

**Critérios de sucesso (mensuráveis):**
- o pacote diz a própria versão no tarball da Release, no `git archive` de uma tag e num clone;
- `init` grava a versão e uma impressão por arquivo instalado; um 2º `init` sem mudança não altera o registro;
- `doctor` com remoto local que tem tag maior ⇒ ⚠️ com a versão nova, a atual e o comando; sem tag maior ⇒ ✅; remoto
  inalcançável ⇒ "não conferido" em ≤ teto + margem; exit do `doctor` igual nos três casos; opt-out ⇒ nenhuma consulta;
- a suíte inteira roda sem nenhuma consulta de rede (provado por um remoto que falha se for chamado);
- `upgrade` sem registro e sem `--de` ⇒ para antes de escrever, com os comandos; `upgrade --de` de uma instalação `v2.12.1`
  com 3 arquivos editados: copia o que é igual/novo/intacto, lista os 3 com o
  diff, não toca neles, não commita, termina com `doctor` sem "difere do pacote" para o que copiou;
- a `sdd-new-session` e a FASE 0 da `sdd-release` mostram a linha do aviso quando há versão nova, sem parar;
- (a) `core.hooksPath` absoluto para o `sdd/hooks` de outra worktree do mesmo repositório ⇒ "hooks ligados";
- (b) nenhum texto de skill do pacote cita `LM-00n` como referência à semente.

**Fora de escopo (confirmado):** atualização automática; mescla automática; aviso no starter além da 1ª linha;
qualquer coisa no repositório privado; rede na suíte; checagem que bloqueie `doctor`, frente ou release.
