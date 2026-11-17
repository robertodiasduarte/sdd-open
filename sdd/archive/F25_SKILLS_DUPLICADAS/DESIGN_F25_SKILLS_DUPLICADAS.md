# DESIGN: F25 Skills duplicadas — alerta e limpeza com autorização

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | F25_SKILLS_DUPLICADAS |
| **Date** | 2026-11-17 |
| **Author** | design-agent (sessão do Roberto) |
| **DEFINE** | [DEFINE_F25_SKILLS_DUPLICADAS.md](./DEFINE_F25_SKILLS_DUPLICADAS.md) (rev. 1.1) |
| **UX Review** | `sdd/reviews/UX_REVIEW_F25_SKILLS_DUPLICADAS.md` (8 MUST, todos de texto) |
| **Status** | Ready for Build |

---

## Architecture Overview

```text
                         sdd-checar-ambiente/scripts/
  ┌──────────────────────────── checar.sh ─────────────────────────────┐
  │ --frente  ─────────────── (como hoje; não lê skills, não fala delas)│
  │ --segredo/--editor(es) ── (como hoje)                               │
  │ normal ── seções 1–6 como hoje ── seção 7: dup_diagnostico ─► ⚠️    │
  │ --duplicadas ──────────────────────────► dup_plano_mostrar (só lê)  │
  │ --limpar <assinatura> ─────────────────► dup_limpar (a ÚNICA escrita)│
  └──────────────────────────────┬──────────────────────────────────────┘
                                 │ `.` (source)
  ┌──────────────────────── duplicadas.sh ─────────────────────────────┐
  │ dup_varrer   6 pastas (2 do Claude, 4 do Codex) → copias.tsv         │
  │              cópia = pasta REAL (atalho resolvido) · versão · origem │
  │              · chegada (npx: registro + pasta gerenciada | git | …)  │
  │ dup_grupos   (agente, nome) com 2+ reais distintos, nome do SDD      │
  │ dup_planejar hash de cada cópia → matriz de escolha → plano.tsv      │
  │ dup_assinatura = hash(plano.tsv)[:12]  (recalculado no --limpar)     │
  │ dup_limpar   lixeira ~/.sdd-lixeira/<AAAAMMDD-HHMMSS>/<rótulo>/<skill>│
  │              mover | npx (protege a outra pasta, confere depois)     │
  │              desfazer.sh regravado antes de cada remoção             │
  └─────────────────────────────────────────────────────────────────────┘
        lê: ~/.claude/skills ($CLAUDE_CONFIG_DIR) · <proj>/.claude/skills
            ~/.codex/skills ($CODEX_HOME) · ~/.agents/skills · <proj>/.agents/skills · <proj>/.codex/skills
            ~/.agents/.skill-lock.json ($XDG_STATE_HOME/skills) · git ls-files do projeto
```

O código central foi **prototipado e validado nesta fase** (Decision 13): está em
`sdd/reports/evidence/F25_SKILLS_DUPLICADAS/prototipo/`, com `duplicadas.sh` e `test_f25_skills_duplicadas.py`
inteiros e um `.diff` por arquivo que muda, todos aplicando limpo sobre `017f09a`. Numa cópia limpa (`git archive`)
com tudo aplicado, os módulos `test_f25_skills_duplicadas`, `test_checar`, `test_bash32`, `test_matriz_new_session`,
`test_f16_textos`, `test_f17_textos`, `test_conversa`, `test_gerar_starter` e `test_docs` passaram em `/bin/bash` 3.2
(145 testes; o do CLI de verdade também, com `SDD_F25_SKILLS_CLI`).

---

## Components

| Componente | Responsabilidade |
|---|---|
| `scripts/duplicadas.sh` (novo) | varredura, grupos, plano, assinatura, limpeza e gerador do `desfazer.sh`; só o `dup_limpar` escreve |
| `scripts/checar.sh` | 2 modos novos (`--duplicadas`, `--limpar`), o balde ⚠️ `ARRUMAR_DUP` e a seção 7 no modo normal |
| `SKILL.md` | v1.6.0, descrição (≤1024), etapa 3 **Limpar**, a exceção única da regra "Somente leitura", seção 7 com a tabela de pastas e a conferência sem bash |
| `references/como-falar.md` | glossário (skill duplicada, global, do projeto, lixeira), Status da etapa 3, Exemplo 3 com a pergunta `[D1 · não se desfaz]` |
| `tests/test_f25_skills_duplicadas.py` (novo) | AT-001 a AT-010 com HOME, projeto e `CODEX_HOME` temporários; npx e agentes falsos |
| `tests/test_checar.py` · `test_bash32.py` · `test_f16_textos.py` · `test_matriz_new_session.py` | HOME de teste no `Base` · `checar.sh` e `duplicadas.sh` no piso bash 3.2 · versão 1.6.0 · exceção estreita do reconhecedor de origem |

---

## Key Decisions

### Decision 1: Biblioteca à parte, lida pelo checar.sh

| **Status** | Accepted | · | **Date** | 2026-11-17 |

**Context:** o `checar.sh` tem 712 linhas e a feature acrescenta ~560 (varredura, plano, limpeza, desfazer).
**Choice:** `scripts/duplicadas.sh`, carregada com `.` pelo `checar.sh` nos 3 pontos que a usam; os modos continuam
sendo do `checar.sh` (`--duplicadas`, `--limpar`), como o DEFINE pede.
**Rationale:** um arquivo por responsabilidade; o `--frente`, o `--segredo` e o `--editor` nem carregam a biblioteca.
**Alternatives Rejected:** 1. tudo no `checar.sh` — rejeitada: 1.270 linhas num arquivo que o aluno não lê e que a
`sdd-new-session` roda em todo pré-voo · 2. script executável separado — rejeitada: o aluno e a skill continuam com um
comando só (`checar.sh`), e a identificação de versão fica num lugar.
**Consequences:** arquivo novo no pacote (MANIFEST, LM-037) e no `test_bash32`; o starter o leva junto (a pasta da skill
inteira é gerada).

### Decision 2: Pastas varridas e precedência vêm da medição

| **Status** | Accepted | · | **Date** | 2026-11-17 |

**Context:** os experimentos 1 e 2 (DEFINE, Clarifications) mediram o que cada agente lê.
**Choice:** Claude Code = `${CLAUDE_CONFIG_DIR:-~/.claude}/skills` e `<raiz>/.claude/skills`, "roda a global";
Codex = `${CODEX_HOME:-~/.codex}/skills`, `~/.agents/skills`, `<raiz>/.agents/skills`, `<raiz>/.codex/skills`, "vê todas e
escolhe uma". `<raiz>` = `git rev-parse --show-toplevel` (fora de repositório, a pasta atual).
**Rationale:** é o que os agentes fazem hoje (EXP-1, EXP-2); o teste do AT-002 refaz a medição do Codex sem modelo
sempre que o `codex` existe e falha se a lista de pastas mudar.
**Alternatives Rejected:** 1. as ~70 pastas que o `npx skills` conhece — rejeitada: o SDD suporta 2 agentes, e alarme
de agente que a pessoa não usa ensina a ignorar os outros · 2. `.agents/skills` acima da raiz (o Codex também lê) —
rejeitada: o `checar.sh` roda na raiz.
**Consequences:** `$CLAUDE_CONFIG_DIR` não foi medido (A-001 do DEFINE): segue o que o `npx skills` assume.

### Decision 3: A cópia é a pasta real

| **Status** | Accepted | · | **Date** | 2026-11-17 |

**Context:** com `-a claude-code -a codex`, o npx põe a cópia em `~/.agents/skills` e um atalho em `~/.claude/skills`
(EXP-3c). Contar caminhos daria duplicata falsa e, pior, "tirar" o atalho deixaria a cópia viva.
**Choice:** cada caminho é resolvido (`cd -P`); caminhos com o mesmo real são **uma** cópia. Duplicata = 2+ reais
distintos para o mesmo (agente, nome).
**Rationale:** é o que o agente carrega; o atalho e a cópia saem juntos (Decision 9).
**Alternatives Rejected:** 1. comparar só nomes — rejeitada pelo motivo acima.
**Consequences:** um atalho manual (que não veio do npx) não é escolhido para sair (Decision 6).

### Decision 4: Origem pelo trecho `<repositório>/releases/latest`, nunca pela URL inteira

| **Status** | Accepted | · | **Date** | 2026-11-17 |

**Context:** a origem (Open/starter) sai da linha de identificação de cada `SKILL.md`. O `gerar-starter.py` troca a URL
completa do Open pela do starter em **todo** arquivo de texto da skill, inclusive o `.sh` (`reescrever`, linha 204).
**Choice:** o awk casa `sdd-open\/releases\/latest` e `sdd-starter\/releases\/latest` (escapados), primeiro que aparecer.
**Rationale:** casando a URL inteira, o `checar.sh` do starter chamaria toda cópia de "starter".
**Alternatives Rejected:** 1. URL inteira — o bug acima · 2. comparar a descrição — muda entre versões.
**Consequences:** um teste confere que `duplicadas.sh` não contém a URL do Open e contém os 2 padrões (AT-010). O
`test_sem_referencia_ao_starter` (skills portadas não citam o starter) ganha uma exceção estreita: só as 2 linhas de
padrão do awk saem da conferência, e o teste exige que sejam exatamente 2 (texto, comentário e mensagem continuam
proibidos).

### Decision 5: "Veio pelo npx" = registro + pasta gerenciada + repositório coerente com a origem

| **Status** | Accepted | · | **Date** | 2026-11-17 |

**Context:** o caso do ESCOPO tem o registro do npx com `sdd-define` (starter em `~/.agents/skills`) e uma cópia do Open
à mão em `~/.claude/skills`; as duas ficam em pastas que o npx gerencia.
**Choice:** é do npx a cópia cujo nome está no registro (`${XDG_STATE_HOME}/skills/.skill-lock.json` ou
`~/.agents/.skill-lock.json`, JSON de 2 espaços) **e** que é a pasta de `~/.agents/skills/<nome>` (ou, sem ela, a de
`~/.claude/skills/<nome>`) **e** cuja origem bate com o `source` do registro quando ele é `…/sdd-open` ou `…/sdd-starter`
(regex `(^|/)sdd-(open|starter)(\.git)?$`; um caminho local não diz nada).
**Rationale:** separa a cópia do npx da manual no caso real; o protótipo pegou um falso negativo com `source ~ /sdd-open/`
casando o caminho do scratchpad (`…-sdd-open-f25-…`), daí a âncora no fim.
**Alternatives Rejected:** 1. recalcular o `skillFolderHash` do registro — rejeitada: o algoritmo é interno do CLI e
muda entre versões · 2. só o registro — classificaria a cópia manual como npx e a mandaria ao `remove`.
**Consequences:** cópia do npx mal classificada como manual sairia movida e a linha do registro ficaria; o `update -g`
a traria de volta (EXP-3e). O teste do CLI de verdade prova a classificação no caso do ESCOPO.

### Decision 6: A matriz de escolha e as duas travas

| **Status** | Accepted | · | **Date** | 2026-11-17 |

**Context:** DC2 manda tirar a mais velha; o ESCOPO, seção 4, deixa o desempate e o caso "projeto no git" ao pipeline.
**Choice:** por grupo, nesta ordem: cópia de outra origem, versão ilegível ou atalho manual ⇒ **não escolhe** (só avisa);
senão fica a de maior versão, e entre iguais a de maior prioridade (projeto, `~/.agents`, `~/.claude`, `~/.codex`); se
duas cópias com a versão máxima têm a **mesma origem e conteúdos diferentes** ⇒ não escolhe ("uma foi editada"); Open
× starter com a mesma versão contam como a mesma versão. Cada uma das outras sai, exceto: **a do projeto salva no git**
(vira "atualize o projeto", pela origem dela) e **a manual que outra pasta aponta** (não escolhe). Trava final: um nome
cujo tirar deixaria algum agente sem cópia neste projeto sai do plano inteiro, com o motivo em cada grupo daquele nome.
**Rationale:** o Open e o starter usam o mesmo número de versão e textos diferentes (A-002): sem a regra Open × starter, o
caso mais comum nunca seria limpo. A trava final apareceu no protótipo (atalho do Claude para a cópia do Codex).
**Alternatives Rejected:** 1. tirar também a do projeto no git — rejeitada no DEFINE (quebra o projeto de quem trabalha
junto e volta na próxima atualização) · 2. escolher a mais recente por data de arquivo — a data não diz a versão.
**Consequences:** o plano pode terminar sem nada a tirar ("Nada a tirar automaticamente"), sem linha `--limpar`.

### Decision 7: Assinatura = hash do plano canônico, recalculado no --limpar

| **Status** | Accepted | · | **Date** | 2026-11-17 |

**Context:** DC1: aplicar só o plano mostrado.
**Choice:** `plano.tsv` traz, em ordem estável, cada cópia de cada grupo (com o hash do conteúdo: arquivos e destinos de
atalho, `.DS_Store` fora), cada decisão e cada item a tirar; a assinatura são os 12 primeiros hex do
`git hash-object --stdin` dele. O `--limpar` recalcula tudo e compara.
**Rationale:** sem arquivo de estado; qualquer mudança em qualquer cópia envolvida (um arquivo a mais, outra versão, uma
cópia nova) muda a assinatura e o `--limpar` sai 2 sem tocar em nada.
**Alternatives Rejected:** 1. gravar o plano em disco no `--duplicadas` — rejeitada: o `--duplicadas` deixaria de ser só
leitura · 2. assinatura só dos caminhos — não pegaria uma cópia editada entre ver e aplicar.
**Consequences:** aplicar só parte do plano não existe: a opção "mostrar uma por uma" da UX Review virou "mostrar o
plano como veio" (UX U6, anotado lá).

### Decision 8: Lixeira, desfazer.sh e a exceção única

| **Status** | Accepted | · | **Date** | 2026-11-17 |

**Context:** DC3 (lixeira e desfazer) e DC1 (uma exceção escrita e única à regra "Somente leitura").
**Choice:** `~/.sdd-lixeira/<AAAAMMDD-HHMMSS>[-N]/<rótulo>/<skill>`, com `LEIA.txt`, `npx/skill-lock.json` (o registro
antes) e `desfazer.sh`. O `desfazer.sh` é **regravado antes de cada remoção** (cabeçalho com `volta`, `liga` e `registro`
+ os itens até ali + o rodapé), com os caminhos em `printf %q`; ele não sobrescreve pasta que reapareceu diferente
(`diff -r`), e só devolve o registro se ele ainda é o que a limpeza deixou (`cksum`). A última linha da saída do
`--limpar` é `Para desfazer: bash <caminho em %q>`.
**Rationale:** o desfazer vale mesmo se a limpeza parar no meio, e mesmo depois que a cópia da própria
`sdd-checar-ambiente` saiu (ele não depende da skill). A exceção da regra continua sendo só o `--limpar`.
**Alternatives Rejected:** 1. modo `--desfazer` no `checar.sh` — rejeitada: seria uma 2ª escrita (a exceção deixaria de
ser única) e sumiria junto com a cópia da skill que saiu · 2. só imprimir os `mv` de volta — perde o registro do npx e
os atalhos.
**Consequences:** comprovado com caminho `Ana O'Neil $HOME "x"` (AT-009) e com o CLI de verdade.

### Decision 9: Saída pelo npx protegida (decisão do Roberto) e HOME explícito

| **Status** | Accepted | · | **Date** | 2026-11-17 |

**Context:** EXP-3: `npx skills remove <s> -g` apaga a pasta de mesmo nome em `~/.claude/skills` e em `~/.agents/skills`,
registrada ou não; `-a codex` com outra cópia viva diz "Successfully removed" e não tira nada. O Roberto escolheu
"Proteger e usar o npx" (`[D2]`, 2026-11-17).
**Choice:** para cada item do npx: guarda a cópia (hash conferido) e o registro; refaz no `desfazer.sh` os atalhos do npx
que apontam para ela; move para `protegidas/<rótulo>/<skill>` a **outra** pasta de mesmo nome em `~/.claude/skills` ou
`~/.agents/skills` (a que o `remove` apagaria); tira um retrato das cópias do nome nas outras 4 pastas; roda
`HOME="${HOME}" npx --yes skills remove <s> -g -a <agentes> -y` (agentes = os de `claude-code`/`codex` cujo caminho global
leva a esta cópia); devolve a protegida; e confere: a cópia saiu (senão "o npx não tirou", nada mudou, sai 1) e o
retrato não mudou (senão devolve a cópia e o registro, "o npx mexeu numa pasta fora do plano", sai 1).
**Rationale:** aplica só o plano mostrado com a saída que a DC3 pede. O `HOME` explícito nasceu de um quase-acidente
desta fase: com `env -i`, o `HOME=` do script deixa de ser exportado e o `node` do CLI cai na pasta pessoal real (o
classificador barrou o comando; o HOME real foi conferido intacto).
**Alternatives Rejected:** 1. mover e editar o registro à mão — recusada pelo Roberto · 2. caso misto só avisa — idem.
**Consequences:** sem teto de tempo no `npx` (o `remove` é local; o download do pacote, na 1ª vez, é do npx): se ele
pendurar, o aluno interrompe e o `desfazer.sh` devolve a protegida. Todo npx de teste recusa HOME fora da pasta de teste
(exit 99).

### Decision 10: Diagnóstico normal — ⚠️ entre os de dado e os outros; --frente sem mensagem

| **Status** | Accepted | · | **Date** | 2026-11-17 |

**Context:** ESCOPO: "arrumar", nunca "impede"; a `sdd-new-session` não pode ser bloqueada.
**Choice:** balde `ARRUMAR_DUP`, impresso depois de `ARRUMAR_DADO` e antes de `ARRUMAR`; até 3 grupos, um item por grupo
(1ª frase = o efeito no agente, UX U1; depois cada cópia numa linha, global antes do projeto); acima de 3, um item com
até 10 nomes e "e mais N". A seção 7 fica depois da 6, onde o `--frente` já saiu: ele não lê skills.
**Rationale:** ordem por consequência (a regra da skill); o pré-voo continua só git, repositório, remoto e acesso, e a
tabela "Como traduzir cada achado" da `sdd-new-session` não muda (`test_matriz_new_session` verde).
**Alternatives Rejected:** 1. 🔴 quando o Claude roda a mais velha — rejeitada pelo ESCOPO · 2. sempre detalhado — 18
grupos na máquina medida viram ~60 linhas.
**Consequences:** medido: 0,35 s a mais com 18 duplicatas reais (meta do DEFINE: ≤ 1 s).

### Decision 11: Testes — HOME sempre temporário, npx e agentes falsos, CLI de verdade opcional

| **Status** | Accepted | · | **Date** | 2026-11-17 |

**Context:** o modo normal passa a ler a pasta pessoal; o `test_checar.py` roda com o HOME de quem roda.
**Choice:** `test_f25` com HOME, projeto e `CODEX_HOME` temporários; `claude` e `codex` falsos no PATH (o `codex --version`
de verdade grava em `~/.codex/tmp`, o que quebraria o hash da árvore); `SDD_CHECAR_NPX` = npx falso com o efeito medido
(e as variantes `nada` e `demais`); CLI de verdade quando `SDD_F25_SKILLS_CLI` aponta um `cli.mjs` (fonte local, sem rede).
No `test_checar.py`, o `Base` passa um HOME temporário **fora** de `self.tmp` (o `TestSomenteLeitura` fotografa
`self.tmp`, e o npm e o codex de verdade gravam na pasta pessoal) e tira `CODEX_HOME`, `CLAUDE_CONFIG_DIR` e
`XDG_STATE_HOME`. Testes com atalho são pulados no Windows (pede privilégio; o npx de lá copia).
**Rationale:** nenhum teste toca o HOME real (ESCOPO, seção 5); o relatório não depende da máquina.
**Alternatives Rejected:** 1. variável só para o teste apontar as pastas — rejeitada: o teste deixaria de exercitar o
`HOME` de verdade.
**Consequences:** LM-014 e LM-029 tratados no teste (encoding e `BASH` no `desfazer`).

### Decision 12: Windows — hash por argumento, a cópia que roda sai por último

| **Status** | Accepted | · | **Date** | 2026-11-17 |

**Context:** no Git Bash, um caminho absoluto `/c/…` passado pela **entrada** de um programa nativo não é convertido; e a
cópia velha pode ser a da própria `sdd-checar-ambiente` que está rodando (o Claude roda a global).
**Choice:** `dup_hash` passa os arquivos ao `git hash-object --no-filters` como argumentos relativos (o protótipo pegou
que, pela entrada, o git lê o caminho a partir da raiz do repositório); a cópia cujo real é a pasta desta skill sai por
último.
**Rationale:** o bash já leu a biblioteca inteira (`.` lê o arquivo todo) e o `checar.sh` segue pelo descritor aberto.
**Alternatives Rejected:** 1. `cygpath -w` na entrada — só existe no Git Bash, e o relativo resolve nos dois.
**Consequences:** A-004 do DEFINE fica provada no macOS pelo teste do CLI; no Windows, pelo job `testes-windows` do CI.

### Decision 13: O código central sai prototipado do Design

| **Status** | Accepted | · | **Date** | 2026-11-17 |

**Context:** o drive faz cada linha do manifest numa sessão nova, sem esta conversa; a lógica (varredura, matriz,
assinatura, proteção do npx, desfazer) é sutil e foi descoberta medindo.
**Choice:** o protótipo validado fica em `sdd/reports/evidence/F25_SKILLS_DUPLICADAS/prototipo/` (arquivos novos inteiros e
um `.diff` por arquivo que muda); cada tarefa do manifest aplica o seu e roda a verificação dela.
**Rationale:** "padrões prontos para copiar", levado ao fim: o executor confere contra o DEFINE em vez de redescobrir.
**Alternatives Rejected:** 1. só descrever e deixar o executor escrever — rejeitada: 3 defeitos que o protótipo achou
(hash dentro de repositório, falso negativo do `source`, motivo da trava sem grupo) voltariam.
**Consequences:** o protótipo vai no commit de documentos, não no pacote.

### Decision 14: Versão 1.6.0, sem CHANGELOG na raiz, sem troca nova no starter

| **Status** | Accepted | · | **Date** | 2026-11-17 |

**Context:** o Open não tem `CHANGELOG.md` na raiz; o starter é gerado.
**Choice:** a versão sobe na `SKILL.md` (minor: modo novo); o remédio "atualize o projeto" aponta para o guia
`…/sdd-open/blob/main/docs/pt-BR/upgrade.md` (não é a URL que o gerador troca e não cita `bin/sdd-open.sh`), e o texto
não usa `` `sync` `` nem `npx skills add` — por isso nenhuma troca nova em `scripts/starter/trocas/`.
**Rationale:** LM-035: o `test_gerar_starter` passou com o texto final (o 1º rascunho citava `` `sync` `` e reprovou ali).
**Alternatives Rejected:** 1. troca para o remédio — desnecessária: o remédio depende da origem da cópia do projeto, não
da distribuição que roda o `checar.sh`.
**Consequences:** o `test_f16_textos` passa a fixar 1.6.0.

---

## File Manifest

| # | File | Action | Purpose | Agent | Dependencies |
|---|------|--------|---------|-------|--------------|
| 1 | `.agents/skills/sdd-checar-ambiente/scripts/duplicadas.sh` | Create | a biblioteca: copiar `prototipo/duplicadas.sh.txt` byte a byte; verificar com `bash -n`, `/bin/bash -n` e `cmp` | (general) | None |
| 2 | `.agents/skills/sdd-checar-ambiente/scripts/checar.sh` | Modify | `git apply prototipo/checar.sh.diff.txt`: modos `--duplicadas`/`--limpar`, balde `ARRUMAR_DUP`, seção 7; verificar com `bash -n` e um `--duplicadas` numa pasta temporária com HOME temporário | (general) | 1 |
| 3 | `.agents/skills/sdd-checar-ambiente/SKILL.md` | Modify | `git apply prototipo/SKILL.md.diff.txt`: v1.6.0, descrição, etapa 3, exceção única, seção 7; verificar com `python3 sdd/bin/skill-lint.py --conversa` | (general) | 2 |
| 4 | `.agents/skills/sdd-checar-ambiente/references/como-falar.md` | Modify | `git apply prototipo/como-falar.md.diff.txt`: glossário, Status da etapa 3, Exemplo 3; verificar com `skill-lint.py --conversa` e `test_conversa` | (general) | 3 |
| 5 | `tests/test_f25_skills_duplicadas.py` | Create | copiar `prototipo/test_f25_skills_duplicadas.py.txt`; verificar rodando o módulo em `/bin/bash` (verde) | (general) | 1, 2, 3, 4 |
| 6 | `tests/test_checar.py` | Modify | `git apply prototipo/test_checar.py.diff.txt`: HOME temporário fora de `self.tmp` no `Base`; verificar com o módulo inteiro | (general) | 2 |
| 7 | `tests/test_bash32.py` | Modify | `git apply prototipo/test_bash32.py.diff.txt`: os `.sh` da `sdd-checar-ambiente` no piso bash 3.2 | (general) | 1, 2 |
| 8 | `tests/test_f16_textos.py` | Modify | `git apply prototipo/test_f16_textos.py.diff.txt`: versão 1.6.0 | (general) | 3 |
| 9 | `tests/test_matriz_new_session.py` | Modify | `git apply prototipo/test_matriz_new_session.py.diff.txt`: exceção estreita do reconhecedor (Decision 4) | (general) | 1 |
| 10 | `MANIFEST.txt` | Modify | `git apply prototipo/MANIFEST.txt.diff.txt`: as 2 linhas novas (LM-037); verificar com `grep -x` das duas | (general) | 1, 5 |
| 11 | `tests/test_decisoes_lint.py` | Modify | o contador de perguntas de decisão do pacote sobe 1 (a `[D1 · não se desfaz]` do Exemplo 3 do `como-falar.md`): em `test_skills_do_pacote_27_perguntas`, `"34 pergunta(s) em 29 arquivo(s)"` → `"35 pergunta(s) em 29 arquivo(s)"`, acrescentando ao comentário da linha ` · F25: +1 (Exemplo 3 da sdd-checar-ambiente)`; verificar com o módulo `test_decisoes_lint` | (general) | 4 |

**Total Files:** 11

`prototipo/` = `sdd/reports/evidence/F25_SKILLS_DUPLICADAS/prototipo/`, com `.txt` no fim de cada nome (documento, não código: o protótipo não vai à branch de código nem ao pacote; o `.diff.txt` aplica com `git apply` igual). Todos os `.diff` aplicam limpo sobre `017f09a`
(`git apply --check`, conferido). Se um `git apply` não aplicar (a árvore mudou), a tarefa vira `bloqueio:`: o executor não
reescreve à mão.

---

## Landmines aplicáveis

| Landmine (⛔) | Fonte | Veredito | Como / Por quê |
|---------------|-------|----------|----------------|
| Gate que só confere fiação | LM-001 | ✔ tratado | o `test_f25` roda o `checar.sh` com fixtures dos dois lados (duplicata e falso positivo; assinatura certa e errada; npx que tira, que não tira e que tira demais); no Build, um mutante que derruba uma asserção nomeada |
| Asserção sem baseline vermelho | LM-002 | ✔ tratado | no Build, o `test_f25` roda contra a árvore de `017f09a` (sem a feature) e tem de falhar; log `BASELINE-VERMELHO.log` |
| Review sobre diff vazio | LM-003 | ✔ tratado | o drive commita por tarefa; a revisão confere `git diff --stat` com o manifest |
| Script que só roda dentro de um repositório | LM-006 | ✔ tratado | o gate roda de um `git archive HEAD`; os testes montam o próprio repositório |
| `subprocess` sem `encoding` no Windows | LM-014 | ✔ tratado | todo `subprocess` do `test_f25` com `encoding="utf-8"` |
| Caminho do Windows / degradação calada | LM-017 | ✔ tratado | Decision 12 (hash por argumento); o `DIR_SKILL` usa o mesmo `dirname "$0"` que o `SKILL_MD` já usa |
| `[exit=]` vazio no zsh | LM-018 | ✔ tratado | os logs de evidência do Build saem de um script em `bash` com `rc=$?` |
| `bash` sem caminho no Windows (WSL) | LM-029 | ✔ tratado | o `desfazer` do teste roda com o `BASH` do módulo |
| Texto que só vale com o `init` derruba o gerador do starter | LM-035 | ✔ tratado | Decision 14; `test_gerar_starter` verde com o texto final, rodado antes do gate |
| Arquivo novo fora do `MANIFEST.txt` | LM-037 | ✔ tratado | tarefa 10 |
| `SKILL.md` no teto de 500 linhas | LM-038 | ✔ tratado | a `SKILL.md` fica com 330 linhas |
| Vigia de teto no Windows | LM-016 | N.A. | o código novo não tem vigia de tempo (Decision 9) |
| `ls a b`, cor do git, rename | LM-025 · LM-033 · LM-007 | N.A. | não há `ls` com vários caminhos; `ls-files` e `hash-object` não colorem; não há conferência de rename |

Varredura rodada em 2026-11-17 (`playbook-lint.sh --grep` por `checar.sh`, `duplicadas`, `npx`, `symlink`, `HOME`,
`MANIFEST.txt`, `SKILL.md`, `starter`, `trocas`, `lista.txt`, `test_checar`, `bash`, `grep`, `exit`, `baseline`,
`verify-gate`, `git`, `status`, `Windows`, `teto`, `mktemp`).

---

## Contrato de aceite

N.A. (1 camada: a skill `sdd-checar-ambiente` e os testes dela).

---

## Agent Assignment Rationale

| Agent | Files Assigned | Why This Agent |
|-------|----------------|----------------|
| (general) | 1–10 | não há agentes especialistas no harness deste repositório; cada tarefa é aplicar o protótipo validado e rodar a verificação dela |

---

## Code Patterns

### Pattern 1: A chamada protegida ao npx (o coração da Decision 9)

```bash
# a outra pasta de mesmo nome que o remove apagaria (medido): vai para a lixeira e volta logo depois
for p in "${cg}" "${ga}"; do
  { [ -e "${p}" ] || [ -L "${p}" ]; } || continue
  [ "$(dup_real "${p}")" = "$1" ] && continue          # o atalho do npx para esta cópia sai junto
  …guarda em protegidas/, registra no desfazer.sh, tira do lugar…
done
antes="$(dup_retrato "$2")"
HOME="${HOME}" "${SDD_CHECAR_NPX:-npx}" --yes skills remove "$2" -g ${args} -y </dev/null > "${DUP_L}/npx/remove-$2.log" 2>&1
depois="$(dup_retrato "$2")"
dup_volta_protegidas
# a cópia ainda está lá ⇒ "o npx não tirou"; o retrato mudou ⇒ "o npx mexeu numa pasta fora do plano"
```

### Pattern 2: O npx de teste com trava de HOME

```bash
#!/usr/bin/env bash
case "${HOME}" in "@TMP@"/*) ;; *) echo "npx de teste: recusa, HOME fora da pasta de teste: ${HOME}" >&2; exit 99 ;; esac
```

O resto está inteiro em `prototipo/` (Decision 13). Candidato a pattern: nenhum (`sdd/patterns/` não existe no Open).

---

## Data Flow

```text
--duplicadas:  dup_varrer → dup_grupos → hashes → matriz (awk) → plano.tsv → texto + assinatura   (nada gravado)
--limpar SIG:  dup_planejar → assinatura == SIG? → npx disponível? → mkdir lixeira → LEIA.txt + desfazer.sh
               → por item (o da própria skill por último): guardar (hash) → desfazer.sh → mover | npx protegido
               → conferir → relatório → "Para desfazer: bash <…>/desfazer.sh"
```

---

## Integration Points

| Ponto | Como |
|---|---|
| `sdd-new-session` | chama `checar.sh --frente`: nada muda (o `--frente` não lê skills) |
| `doctor` do `sdd-open.sh` | chama `checar.sh --segredo`: nada muda |
| `npx skills` (CLI 1.9.0) | só `remove <s> -g -a <agente> -y`, com proteção e conferência; o registro só é lido e guardado |
| `gerar-starter.py` | gera a skill inteira, `duplicadas.sh` incluído; sem troca nova |

---

## Testing Strategy

| Tipo | Escopo | Ferramenta | Meta |
|---|---|---|---|
| comportamento | AT-001 a AT-009 | `tests/test_f25_skills_duplicadas.py` (HOME temporário, npx falso, agentes falsos) | verde em `/bin/bash` 3.2 e no Windows (CI) |
| medição viva | AT-002 (Codex) | `codex debug prompt-input` com HOME e `CODEX_HOME` de teste | pula sem `codex`; falha se a lista de pastas mudar |
| integração | AT-009 com o CLI real | `SDD_F25_SKILLS_CLI=<cli.mjs>` | roda no Build, com log |
| texto | AT-010 | `test_f25` (SKILL.md, como-falar, reconhecedor), `skill-lint --conversa`, `test_conversa` | verde |
| não-regressão | AT-010 | `test_checar`, `test_matriz_new_session`, `test_f16_textos`, `test_f17_textos`, `test_bash32`, `test_gerar_starter`, suíte inteira | verde |
| baseline vermelho | LM-002 | `test_f25` contra `017f09a` | vermelho |

Mapa AT → teste: AT-001 `AT001Claude` · AT-002 `AT002Codex` · AT-003 `AT003Npx` · AT-004 `AT004Diagnostico` · AT-005
`AT005NaoEDuplicata` · AT-006 `AT006Plano` · AT-007 `AT007Matriz` · AT-008 `AT008Recusa` · AT-009 `AT009Limpar` · AT-010
`AT010Textos` + os módulos de não-regressão.

---

## Error Handling

| Situação | Saída |
|---|---|
| sem assinatura · assinatura de outro plano | `🛑 … Nada foi tirado.` + `→ peça o plano (de novo)`, exit 2 |
| item do npx sem `npx` no PATH | `🛑 … o npx não está disponível … Nada foi tirado.`, exit 2 |
| lixeira não pode ser criada | `🛑 Não consegui criar a lixeira em … Nada foi tirado.`, exit 2 |
| cópia não confere ao guardar | o item para; os anteriores ficam na lixeira; `⚠️ Parei: …`, exit 1 |
| npx não tira · npx tira fora do plano | devolve o que saiu do item; `🛑`/`⚠️` com o motivo, exit 1 |
| `desfazer.sh` com pasta que reapareceu diferente | não sobrescreve; `⚠️ … existe de novo e é diferente`, exit 1 |
| sem git (`--duplicadas`/`--limpar`) | `🛑 O git não está instalado … Nada mudou.`, exit 2 |

---

## Configuration

Nenhum slot novo. Variáveis lidas: `HOME`, `CLAUDE_CONFIG_DIR`, `CODEX_HOME`, `XDG_STATE_HOME` (as dos agentes e do npx);
`SDD_CHECAR_NPX` só para os testes.

---

## Segurança

1. **Onde mora cada segredo:** N.A. — a feature não lê nem grava segredo; o registro do npx não guarda credencial.
2. **Quem vê e quem muda cada tabela (RLS):** N.A. — sem banco.
3. **Credencial de cada agente ou integração:** N.A. — o `npx skills remove` é local; nenhuma chamada usa credencial.
4. **Cabeçalhos e CORS do host:** N.A. — sem host.
5. **Itens aplicados no Define:** nenhum (Segurança N.A.). Requisitos de engenharia: a remoção fora do git só com a
   assinatura do plano mostrado e o sim `[D1]`; o `desfazer.sh` com caminhos em `%q` (testado com espaço, aspas e `$`);
   o npx com `HOME` explícito; os npx de teste recusam HOME fora da pasta de teste.

---

## Observability

| Aspect | Implementation |
|--------|----------------|
| Logging | `~/.sdd-lixeira/<…>/npx/remove-<skill>.log` (a saída do npx) e `LEIA.txt` |
| Metrics | N.A. |
| Tracing | N.A. |

---

## Advisor Ledger

| # | Nota | Severidade | Veredito | Evidência |
|---|---|---|---|---|

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-11-17 | design-agent | Versão inicial, com o protótipo validado em `prototipo/` |
| 1.2 | 2026-11-17 | drive (CORRIGIR, rodada 2) | Raio de impacto que faltou: o `test_decisoes_lint` conta as perguntas de decisão do pacote, e o Exemplo 3 acrescenta 1 (tarefa 11) |
| 1.1 | 2026-11-17 | drive (CORRIGIR, rodada 1) | O publish-gate reprova documento commitado na branch de código: os documentos ficam fora dela (como na F24, que os leva à `docs/incorporar-starter`), e o protótipo ganhou `.txt` no nome para o drive o tratar como documento |

---

## Next Step

**Ready for:** `/sdd-build sdd/features/DESIGN_F25_SKILLS_DUPLICADAS.md` (pelo `sdd-drive`).
