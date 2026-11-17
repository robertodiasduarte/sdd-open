# DEFINE: F25 Skills duplicadas — alerta e limpeza com autorização

> A `sdd-checar-ambiente` passa a avisar quando o mesmo agente enxerga duas cópias de uma skill do SDD
> (global e do projeto, ou duas globais), dizendo onde está cada uma, a versão, a origem e qual delas o agente
> roda; e ganha um modo à parte que mostra o plano de limpeza e, só com o sim do aluno ao plano mostrado, tira a
> cópia mais velha para uma lixeira própria, com um comando que desfaz.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | F25_SKILLS_DUPLICADAS |
| **Date** | 2026-11-17 |
| **Author** | define-agent (sessão do Roberto), a partir de `sdd/features/ESCOPO_F25_SKILLS_DUPLICADAS.md` |
| **Status** | Ready for UX Review |
| **Clarity Score** | 14/15 |

---

## Problem Statement

A mesma skill `sdd-*` fica instalada em vários lugares do computador: global (pasta pessoal) e no projeto, em
versões e distribuições diferentes (Open × starter). O agente roda uma delas, e o aluno não sabe qual. No caso
medido no ESCOPO (seção 2.1), o Claude Code roda a `sdd-define` 2.6.1 global e esconde a 2.7.0 que o projeto
traz (experimento 1, abaixo). O Codex lista as três cópias da mesma skill e o modelo escolhe uma sem avisar
(experimento 2). O risco cresce por construção: a página do SDD manda instalar o starter **global**, e quem
depois adota o SDD Open num projeto passa a ter a mesma skill nos dois lugares.

---

## Target Users

| User | Role | Pain Point |
|------|------|------------|
| Aluno que instalou o starter global e depois adotou o Open num projeto (em geral, nunca usou terminal) | roda as skills pelo agente | vê um comportamento que não bate com a versão que acha que tem e não sabe por quê; não sabe que há duas cópias nem onde estão |
| Aluno com cópias antigas copiadas à mão (`~/.claude/skills`, `~/.codex/skills`) | idem | a cópia velha esconde a nova; apagar à mão arrisca apagar a errada ou desfazer o registro do `npx` |
| Mantenedor do Open | responde dúvidas de "a skill está diferente" | não tem como diagnosticar à distância qual cópia o agente do aluno roda |

---

## Goals

| Priority | Goal |
|----------|------|
| **MUST** | Os 3 experimentos da seção 2.3 do ESCOPO medidos com evidência e convertidos em regra: que pastas cada agente lê, qual cópia ele roda com o mesmo nome, onde o `npx skills` grava e o que o `remove` apaga |
| **MUST** | O diagnóstico normal avisa (⚠️, nunca 🔴 nem "impede") cada duplicata real: agente, caminho completo, versão e origem de cada cópia e qual o agente roda, sem alterar nada |
| **MUST** | Modo de plano (`--duplicadas`), só leitura: global × local com caminho, versão e origem, como a cópia chegou, a recomendação (tirar a mais velha) e uma assinatura do plano |
| **MUST** | Modo de aplicar (`--limpar <assinatura>`): sem a assinatura do plano que foi mostrado, ou com o plano mudado, não altera nada; com ela, lixeira própria conferida por hash, saída pelo `npx skills remove` para o que veio pelo `npx` (protegendo a outra cópia de mesmo nome), comando que desfaz no fim |
| **MUST** | A regra "Somente leitura" da skill ganha uma exceção escrita e única, nomeando o `--limpar` (DC1) |
| **MUST** | O par gerado pelo `sync` do Open (`.agents/skills` → `.claude/skills`) e o atalho (symlink) do `npx` não aparecem como duplicata; `--frente` continua saindo 0 e sem falar de duplicata |
| **MUST** | Starter com o mesmo comportamento, gerado (`gerar-starter.py` + troca), bash 3.2 |
| **SHOULD** | A explicação ao aluno (texto que ele lê) em `references/como-falar.md`: global × local com os caminhos, a pergunta de confirmação `[D1 · não se desfaz]` e o comando de desfazer |
| **COULD** | — |

---

## Success Criteria

- [ ] Com `HOME` de teste reproduzindo a tabela 2.1 do ESCOPO, o diagnóstico normal lista as 3 duplicatas (agente, 2 caminhos completos, versão e origem de cada cópia, qual roda) e o hash da árvore do HOME e do projeto é igual antes e depois (0 arquivos mudados).
- [ ] O `--limpar` com assinatura ausente, errada ou de um plano que mudou (1 arquivo a mais numa cópia) sai ≠ 0 e muda 0 arquivos, sem criar `~/.sdd-lixeira`.
- [ ] Com a assinatura certa, 100% das cópias do plano ficam na lixeira com hash igual ao do original, 0 cópias fora do plano mudam (inclusive a cópia manual de mesmo nome que o `npx skills remove` apagaria, medido no experimento 3), e o comando de desfazer devolve a árvore com hash igual ao de antes (inclusive `~/.agents/.skill-lock.json`).
- [ ] O diagnóstico normal não demora mais que 1 s a mais que hoje num HOME com 3 pastas de 18 skills cada (medido no BUILD).
- [ ] `checar.sh --frente` sai 0 nos 3 cenários de duplicata da fixture.
- [ ] Suíte inteira verde, com `test_checar.py` rodado em `/bin/bash` 3.2, e o starter gerado sem edição à mão (`gerar-starter.py` + `check-gerado.py` verdes).

---

## Acceptance Tests

| ID | Padrão | Critério (EARS) | Gate (`kind`) |
|----|--------|-----------------|---------------|
| AT-001 | Event-driven (experimento 1) | **When** o Claude Code (2.1.x) encontra uma skill com o mesmo nome em `~/.claude/skills` e em `.claude/skills` do projeto, the medição **shall** registrar qual das duas ele lista (medido: a global; a do projeto some; uma skill só do projeto aparece; `~/.agents/skills` e `.agents/skills` não são lidas), e o `checar.sh` **shall** varrer para o Claude Code só `${CLAUDE_CONFIG_DIR:-~/.claude}/skills` e `<raiz>/.claude/skills` e dizer, na duplicata global × projeto, que ele roda a global | test (fixture) + medição `EXP-1-CLAUDE-PRECEDENCIA.log` |
| AT-002 | Event-driven (experimento 2) | **When** o Codex (0.163) encontra a mesma skill em várias pastas, the medição **shall** registrar quais pastas ele lê e o que faz com o nome repetido (medido sem modelo, por `codex debug prompt-input`: lê `${CODEX_HOME:-~/.codex}/skills`, `~/.agents/skills`, `<raiz>/.agents/skills` e `<raiz>/.codex/skills`; nenhuma pasta `.claude`; lista todas as cópias de mesmo nome), e o `checar.sh` **shall** varrer exatamente essas pastas para o Codex e dizer que ele vê as N cópias e escolhe uma; um teste **shall** refazer a medição quando o `codex` existir, com HOME e `CODEX_HOME` de teste, e falhar se a lista de pastas mudar | test |
| AT-003 | Event-driven + Unwanted (experimento 3) | **When** o `npx skills add … -g` instala para o Claude Code, para o Codex ou para os dois, the medição **shall** registrar onde grava (medido: `-a claude-code` ⇒ cópia em `~/.claude/skills`; `-a codex` ⇒ `~/.agents/skills`; os dois ⇒ cópia em `~/.agents/skills` e atalho em `~/.claude/skills`; registro em `~/.agents/.skill-lock.json`), e o `checar.sh` **shall** reconhecer como "veio pelo npx" a cópia cuja skill está no registro e cujo conteúdo é a pasta que o `npx` gerencia, e contar como **uma** cópia um atalho que aponta para outra cópia varrida. **If** o `npx skills remove <skill> -g` roda com outra pasta de mesmo nome em `~/.claude/skills` que não veio dele, **then** a medição **shall** registrar que ela também é apagada (medido) — a base do AT-009 | test (fixture) + medição `EXP-3-NPX.log` |
| AT-004 | Event-driven + Non-regression | **When** o diagnóstico normal roda num HOME de teste que reproduz a tabela 2.1 (sdd-brainstorm, sdd-define e sdd-release em `~/.claude/skills` do Open, `~/.agents/skills` do starter pelo `npx` e `.claude/skills` do projeto, nas versões da tabela), the `checar.sh` **shall** pôr em `⚠️ Vale arrumar`, depois dos itens de dado e antes dos outros, um item por duplicata (por agente e skill) com cada cópia numa linha — global ou projeto, caminho completo, versão, origem (Open, starter ou outra) — e qual o agente roda, mais o comando do plano; com mais de 3 duplicatas, um item só com até 10 nomes e "e mais N"; e the system **shall continue to** não alterar nenhum arquivo (hash da árvore do HOME e do projeto igual antes e depois) e sair 0 | test |
| AT-005 | Unwanted | **If** as cópias de mesmo nome estão em pastas que agentes diferentes leem (o par `.agents/skills` → `.claude/skills` gerado pelo `sync` do Open; `~/.agents/skills` × `~/.claude/skills`), ou uma é atalho para a outra, ou o nome não tem nenhuma cópia do SDD (skill de terceiro repetida), **then** o `checar.sh` **shall** não apontar duplicata | test (negativo) |
| AT-006 | Event-driven | **When** o aluno pede o plano (`checar.sh --duplicadas`), the system **shall** mostrar, por duplicata, cada cópia com global ou projeto, caminho completo, versão, origem e como chegou (pelo `npx`, salva no git do projeto, copiada à mão), qual o agente roda hoje e a recomendação; para cópia global a tirar, **shall** dizer que ela vale para todos os projetos deste computador; **shall** terminar com a assinatura do plano e o comando `--limpar <assinatura>` só quando houver o que aplicar; e **shall** não alterar nenhum arquivo | test |
| AT-007 | Optional feature (matriz da escolha) | **Where** as versões são legíveis e diferentes, the plano **shall** recomendar tirar todas as cópias mais velhas e manter a mais nova; **where** a versão é igual e a origem é a mesma, com conteúdo igual, **shall** recomendar tirar a global (sobra), e com conteúdo diferente **shall** não escolher e dizer por quê; **where** a versão é igual e as origens são Open × starter, **shall** tratar como a mesma versão e recomendar tirar a global; **where** uma versão é ilegível, ou uma cópia não é do SDD, ou uma cópia é atalho que não veio do `npx`, **shall** não escolher e só avisar; **where** a mais velha é a cópia do projeto salva no git, **shall** não tirá-la e recomendar atualizar o projeto (remédio pela origem dela: SDD Open ou `npx`), dizendo que tirar a cópia apareceria como mudança a salvar | test (matriz) |
| AT-008 | Unwanted | **If** o `--limpar` roda sem assinatura, com uma assinatura que não é a do plano recalculado na hora, ou o plano mudou entre ver e aplicar (uma cópia ganhou ou perdeu arquivo, mudou de versão, uma cópia nova apareceu), ou falta o `npx` para um item que veio dele, ou a lixeira não pode ser criada, **then** the system **shall** sair ≠ 0 com a frase do motivo e o próximo passo, sem alterar nenhum arquivo e sem criar `~/.sdd-lixeira` | test (negativo) |
| AT-009 | Event-driven + Unwanted | **When** o `--limpar` roda com a assinatura do plano recalculado, the system **shall**, antes de tirar qualquer coisa, gravar em `~/.sdd-lixeira/<AAAAMMDD-HHMMSS>/` o `desfazer.sh` e a lista do que vai sair; copiar cada cópia do plano para `<lixeira>/<origem>/<skill>` e conferir o hash; tirar a cópia copiada à mão; tirar a que veio do `npx` com `npx skills remove <skill> -g -a <agente> -y`, depois de guardar o registro do `npx` e de tirar para a lixeira a outra pasta de mesmo nome que o `remove` apagaria, devolvendo-a ao lugar logo depois, com o hash conferido; e terminar a saída com `bash <lixeira>/desfazer.sh`. Rodar o `desfazer.sh` **shall** devolver a árvore com hash igual ao de antes (pastas e registro do `npx`), sem sobrescrever pasta que reapareceu. **If** o `npx` não tira a cópia, ou some ou muda qualquer cópia fora do plano, **then** the system **shall** devolver da lixeira o que saiu daquele item, dizer o que aconteceu e sair ≠ 0. Caminho com espaço, aspas ou `$` no nome da pasta **shall** sair e voltar intacto | test |
| AT-010 | Ubiquitous + Non-regression | The `SKILL.md` da `sdd-checar-ambiente` **shall** ter a exceção única à regra "Somente leitura", nomeando o `--limpar` e o sim do aluno ao plano, e descrever a conferência à mão sem bash; o `references/como-falar.md` **shall** ter a explicação global × local com os caminhos, a pergunta `[D1 · não se desfaz]` antes do `--limpar` e o comando de desfazer. The system **shall continue to**: sair 0 no `--frente` com duplicatas, sem falar delas (a tabela "Como traduzir cada achado" da `sdd-new-session` não muda); manter `--segredo`, `--editor` e `--editores` iguais; passar `test_checar.py` em `/bin/bash` 3.2 e o `checar.sh` no `test_bash32.py`; gerar o starter só por `scripts/gerar-starter.py` (troca em `scripts/starter/trocas/sdd-checar-ambiente.md` para o que só vale com o `init`); passar a suíte inteira | test |

Padrões considerados:
- **While:** N.A. — a feature não tem estado que dure entre chamadas além da lixeira; o "plano mudou entre ver e aplicar" é tratado como gatilho indesejado (AT-008), e o recálculo na hora do `--limpar` é o que o prova.
- **If/Then:** AT-003 (o `remove` do `npx` apaga a pasta de mesmo nome), AT-005 (falso positivo), AT-008 (assinatura ausente, errada, plano mudado, sem `npx`, lixeira impossível), AT-009 (`npx` que não tira, cópia fora do plano que muda).
- **Where:** AT-007 (matriz da escolha da cópia a tirar).
- **shall continue to:** AT-004 (diagnóstico normal só lê, sai 0) e AT-010 (`--frente`, os outros modos, bash 3.2, starter gerado).

---

## Clarifications

### Session 2026-11-17 (decididas no ESCOPO pelo Roberto — não se reabrem)

- [x] (escopo) DC1 — a limpeza fica na mesma skill `sdd-checar-ambiente`, num modo à parte; o diagnóstico normal só lê e avisa; o modo de limpeza mostra o plano e aplica só com o sim e só o plano mostrado; a regra "Somente leitura" ganha uma exceção escrita e única nomeando esse modo; vale igual no Open e no starter. Integrado em AT-006, AT-008, AT-009 e AT-010.
- [x] (UX) DC2 — a recomendação é tirar a cópia mais velha; antes, a skill explica que há uma global e uma local, com caminho completo, versão e origem de cada uma, e pede confirmação. Integrado em AT-006, AT-007 e na pergunta `[D1 · não se desfaz]` do AT-010.
- [x] (dados) DC3 — lixeira própria `~/.sdd-lixeira/<data-hora>/<origem>/<skill>` e comando que desfaz; o que veio pelo `npx` sai com `npx skills remove` depois da cópia para a lixeira; o que foi copiado à mão é movido. Integrado em AT-009.
- [x] (terminologia) DC4 — os nomes das skills do starter não mudam. Integrado em Out of Scope.

### Session 2026-11-17 (experimentos da seção 2.3 — medidos, viram regra)

- [x] (integrações) Precedência no Claude Code → com o mesmo nome, ele lista a **global** e esconde a do projeto; ele não lê `~/.agents/skills` nem `.agents/skills`. O HOME de teste não serve para o Claude Code (sem login: "Not logged in"); a medição usou o HOME real **só lido** (projeto temporário com `.claude/skills/sdd-define` marcada, `--no-session-persistence`, nada gravado em pasta de skills) e a lista de skills desta própria sessão. Evidência: `sdd/reports/evidence/F25_SKILLS_DUPLICADAS/EXP-1-CLAUDE-PRECEDENCIA.log`. Integrado em AT-001.
- [x] (integrações) Pastas que o Codex lê → `${CODEX_HOME:-~/.codex}/skills`, `~/.agents/skills`, `<raiz>/.agents/skills`, `<raiz>/.codex/skills`; com o mesmo nome em várias, **lista todas** e o modelo escolhe. Medido sem modelo, com HOME e `CODEX_HOME` de teste. Evidência: `EXP-2-CODEX-PASTAS.log`. Integrado em AT-002.
- [x] (integrações) Onde o `npx skills` grava e o que o `remove` apaga → ver AT-003. Achado que tocou a DC3: `npx skills remove <skill> -g` (com `-a claude-code` ou sem `-a`) apaga a pasta de mesmo nome em `~/.claude/skills` mesmo quando ela é cópia manual que não está no registro, sem lixeira; com `-a codex` e outra cópia de mesmo nome, diz "Successfully removed" e não tira nada; e uma pasta do `npx` tirada sem tirar a linha do registro volta, espalhada em ~45 pastas de agentes, no próximo `npx skills update -g`. Evidência: `EXP-3-NPX.log` (CLI `skills` 1.9.0, HOME de teste).
- [x] (escopo) **Pergunta ao Roberto, 2026-11-17, `[D2 · muda o produto]`** — "Como a limpeza deve tirar uma cópia que veio pelo npx?", porque o `npx skills remove` sozinho não aplica só o plano mostrado → **Proteger e usar o npx** (a recomendada): copiar a escolhida para a lixeira, tirar para a lixeira, por um instante, a outra pasta de mesmo nome que o `remove` apagaria (o plano mostra isso), rodar `npx skills remove <skill> -g -a <agente> -y`, devolver a outra pasta e conferir que só o plano foi aplicado; se não, desfazer e avisar. Integrado em AT-009.

### Session 2026-11-17 (decididas pelo pipeline — prós e contras no DESIGN)

- [x] (escopo) Nome dos modos → `--duplicadas` (plano, só leitura) e `--limpar <assinatura>` (aplicar). Assinatura = hash curto do texto canônico do plano (cada item: ação, caminho, hash do conteúdo da cópia, versão, origem, como sai), recalculado na hora do `--limpar`: qualquer mudança nas cópias muda a assinatura. A favor: amarra "o que foi mostrado" a "o que é aplicado" sem arquivo de estado; contra: o aluno não consegue aplicar um plano de ontem se algo mudou — e é isso que se quer.
- [x] (UX) O desfazer → um `desfazer.sh` gravado pelo `--limpar` dentro da própria pasta da lixeira, antes de tirar qualquer coisa. A favor: a exceção da regra "Somente leitura" continua única (só o `--limpar` escreve), e o desfazer funciona mesmo quando a cópia tirada era a da própria `sdd-checar-ambiente` que rodou; contra: um arquivo de script na lixeira.
- [x] (dados) Gravidade → ⚠️ "Vale arrumar", nunca 🔴 nem "impede" (o ESCOPO pede); dentro do ⚠️, logo depois dos itens de dado (`.env`, npm) e antes dos demais, porque o agente pode estar rodando a versão errada de todas as fases. A frase diz o que o agente faz: no Claude Code, "roda a global"; no Codex, "vê as N e escolhe uma sem avisar qual".
- [x] (dados) "Mais velha" → `metadata.version` do frontmatter, comparado número a número (semver). O Open e o starter usam o mesmo número para a mesma skill (conferido: `sdd-define`, `sdd-brainstorm`, `sdd-release`, `sdd-checar-ambiente`, `sdd-kb` iguais no Open e em `~/.agents/skills`), mas o texto difere entre as distribuições; por isso versão igual com origens Open × starter conta como a mesma versão (sai a global), e versão igual com a mesma origem e conteúdo diferente é cópia editada (não escolhe). Versão ilegível ⇒ não escolhe. Mais de 2 cópias (Codex) ⇒ mantém a mais nova e tira as outras que a regra escolher.
- [x] (dados) Ordem de quem fica no empate (conteúdo igual) → fica a do projeto; entre globais, fica `~/.agents/skills` (onde a página e o `npx` instalam), depois `~/.claude/skills`, depois `${CODEX_HOME:-~/.codex}/skills`.
- [x] (escopo) Mais velha salva no git do projeto → o plano **não** a tira: recomenda atualizar o projeto (num projeto do SDD Open, o upgrade dele; numa cópia do projeto que veio pelo `npx`, `npx skills update`) e diz que tirá-la apareceria como mudança a salvar e voltaria no próximo `sync`. O aluno vê as duas cópias (DC2). A favor: não quebra o projeto de quem trabalha junto nem briga com o `sync`; contra: a duplicata fica até o upgrade — e o upgrade é o remédio que resolve. Previsto no ESCOPO, seção 4.
- [x] (UX) Cópia global a tirar → o plano diz que ela vale para todos os projetos deste computador e que os projetos sem cópia própria ficam sem a skill (voltar: `desfazer.sh`, ou instalar de novo). Achado do Define: o ESCOPO não cobria; a DC2 continua (a recomendação é tirar a mais velha), o aviso só completa a explicação.
- [x] (escopo) Duplicata entre duas pastas globais → conta só quando o mesmo agente lê as duas: pelo experimento 2, `~/.agents/skills` × `${CODEX_HOME:-~/.codex}/skills` (Codex). `~/.agents/skills` × `~/.claude/skills` não é duplicata (agentes diferentes).
- [x] (escopo) Skill de terceiro → nomes sem nenhuma cópia do SDD ficam fora (alarme fora do SDD ensina a ignorar os outros). Nome do SDD com uma cópia de outra origem ⇒ avisa, nunca propõe limpeza.
- [x] (escopo) Atalho (symlink) → a cópia é a pasta real; vários caminhos que levam à mesma pasta real contam como uma cópia. Cópia com atalho que não veio do `npx` ⇒ não escolhe (só avisa): desfazer atalho à mão é fácil de errar.
- [x] (UX) Muitas duplicatas → até 3 itens detalhados no diagnóstico normal; acima disso, um item com até 10 nomes e "e mais N", e o detalhe fica no `--duplicadas`.
- [x] (escopo) `--frente` → não ganha mensagem: a duplicata não bloqueia a abertura de frente, e o pré-voo continua só git, repositório, remoto e acesso; a tabela da `sdd-new-session` não muda.
- [x] (escopo) Sem bash (PowerShell) → a `SKILL.md` descreve a conferência à mão (as pastas por agente, a versão de cada cópia); a limpeza à mão é só com os comandos entregues, um por vez, com o sim do aluno; nada automático.
- [x] (escopo) Versão da skill → 1.6.0 (minor: modo novo). O Open não tem `CHANGELOG.md` na raiz: a versão sobe na `SKILL.md` e a publicação fica no ledger da release (corrigido no Design, revisão 1.1).
- [x] (UX) UX Review → curta, sobre o texto que o aluno lê: Status, explicação global × local com caminhos, pergunta de confirmação, comando de desfazer (`sdd/reviews/UX_REVIEW_F25_SKILLS_DUPLICADAS.md`).

### Session 2026-11-17 (governança)

- [x] (governança) N.A. — a feature não trata dinheiro, lançamento, nota fiscal, tributo, folha nem dado pessoal (lê e move pastas de skills do computador). Registrado por instrução explícita do Roberto no pedido da sessão ("Sem governança: registre N.A."), sem despacho de revisor fresco.

### Segurança

- Gatilhos da `sdd-seguranca` (login, rota pública, dado de terceiros, upload, IA, banco): nenhum. A feature não chama modelo, não tem rota nem banco, e o dado que lê é o nome, a versão e a origem de skills instaladas. ⇒ N.A.
- Fora do catálogo, como requisito de engenharia já nos ATs: o `--limpar` apaga pastas fora do git (por isso a assinatura, a lixeira conferida por hash e a pergunta `[D1 · não se desfaz]`, AT-008/AT-009/AT-010); o `desfazer.sh` é gerado com caminhos vindos do disco, então nomes com espaço, aspas e `$` são testados (AT-009).

---

## Verify Gate

```yaml
verify_gate:
  kind: test
  cmd: "T=$(mktemp -d) && git archive HEAD | tar -x -C $T && cd $T/tests && SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest test_f25_skills_duplicadas test_checar test_bash32 test_matriz_new_session test_f16_textos test_f17_textos test_gerar_starter && cd $T && PUBLISH_GATE_MODE=ci bash scripts/publish-gate.sh $T && SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover -s tests -p 'test_*.py'"
  pass_when: "exit 0"
  threshold: "—"
  manual_fallback: "—"
```

Cobertura:
- AT-001 a AT-010: módulo novo `tests/test_f25_skills_duplicadas.py`, chamado pelo nome no `cmd` (sem ele, o gate fica vermelho: é o baseline vermelho). Fixtures montadas no próprio teste, sempre com HOME, `CODEX_HOME` e projeto em pasta temporária: a tabela 2.1; o par `.agents` → `.claude` gerado; atalho do `npx`; cópia de terceiro; versão ilegível; mesma versão Open × starter; mesma versão e origem com conteúdo diferente; cópia do projeto salva no git; pasta com espaço, aspas e `$`.
- O `npx` no teste é um falso (variável de ambiente, como o `gh` falso do `test_checar.py`) que reproduz o comportamento medido no experimento 3: apaga `~/.claude/skills/<skill>` e `~/.agents/skills/<skill>` e tira a linha do registro; um 2º falso diz que tirou e não tira nada. O teste com o CLI de verdade roda quando `SDD_F25_SKILLS_CLI` aponta para um `cli.mjs` (fonte local, sem rede), e o BUILD guarda o log.
- AT-001 e AT-003 (medição): os logs `EXP-*.log` são a evidência da medição; o teste cobre a regra que saiu dela. AT-002 refaz a medição do Codex quando o `codex` existe (sem modelo, sem rede).
- AT-010: testes de texto sobre `SKILL.md` e `references/como-falar.md`; `test_matriz_new_session.py` (nenhuma mensagem nova no `--frente`); `test_bash32.py` passa a incluir o `checar.sh`; `test_gerar_starter.py` e a suíte inteira.

O gate roda de um `git archive HEAD`, como na F23 e na F24. O Windows é provado pelo job `testes-windows` do CI do PR.

---

## Out of Scope

- Renomear skills do starter (DC4).
- Limpar a máquina do Roberto: é caso de teste descrito, não alvo; o primeiro uso real é depois da F25 publicada, pela própria skill.
- A página /sdd/ do site (frente própria, depois da F25 publicada).
- Duplicata de skill que não é do SDD (nenhuma cópia do SDD com aquele nome).
- Outros agentes além do Claude Code e do Codex (o `npx` conhece ~70; a F25 cobre os dois que o SDD suporta).
- `.agents/skills` em pastas acima da raiz do projeto (o Codex também as lê; o `checar.sh` roda na raiz).
- Atualizar a cópia (o `--limpar` só tira; atualizar é o upgrade do Open ou o `npx skills update`, recomendados no texto).
- Editar o registro do `npx` à mão (a saída é pelo `npx skills remove`, decisão do Roberto; o registro só é guardado e devolvido inteiro pelo desfazer).

---

## Constraints

| Type | Constraint | Impact |
|------|------------|--------|
| Technical | bash 3.2 (o `/bin/bash` do macOS) e Git Bash no Windows; sem `jq`, sem Python no script | comparação de versão e hash de pasta em shell; `git hash-object` para os hashes |
| Technical | Testes **sempre** com HOME, `CODEX_HOME` e projeto temporários; nenhum teste toca o HOME real | variáveis de ambiente para o `npx` falso e o CLI de verdade |
| Technical | O `--limpar` é a única escrita da skill (DC1) e só depois do sim ao plano mostrado | o desfazer é um script gravado na lixeira, não um modo |
| Technical | Comportamento do `npx skills` medido na versão 1.9.0; outra versão pode mudar | o `--limpar` confere depois de cada `remove` e devolve o que sair do plano (AT-009) |
| Technical | Nada é corrigido direto no starter; texto que cita o que só o `init` cria sai por troca (LM-035) | rodar `test_gerar_starter.py` antes do gate inteiro |
| Technical | `SKILL.md` com teto de 500 linhas (LM-038); hoje 297 | detalhe novo vai para `references/` |
| Technical | Repositório público | os números da máquina do Roberto entram como "caso medido no ESCOPO"; nada do projeto de origem além do que o ESCOPO já traz |
| Process | Os artefatos SDD desta frente vão num commit de documentos separado do commit de código, como na F24 | — |

---

## Technical Context

| Aspect | Value | Notes |
|--------|-------|-------|
| **Deployment Location** | `.agents/skills/sdd-checar-ambiente/` (`SKILL.md`, `references/como-falar.md`, `scripts/checar.sh`), `scripts/starter/trocas/sdd-checar-ambiente.md` (se o texto do remédio citar o que só o `init` cria), `scripts/duplicadas.sh` (novo, lido pelo `checar.sh`), `tests/test_f25_skills_duplicadas.py`, `tests/test_checar.py` (HOME de teste), `tests/test_bash32.py`, `tests/test_f16_textos.py` (versão), `MANIFEST.txt` | a tabela "Como traduzir cada achado" da `sdd-new-session` não muda (o `--frente` não ganha mensagem) |
| **KB Domains** | nenhum | o Open não tem `sdd/kb/` |
| **IaC Impact** | None | — |
| **LLM Prompts** | false | nenhum prompt de produção; a skill é instrução de agente do método, e o script não chama modelo |
| **CONTEXTO de domínio** | nenhum (pulado: o Open não tem `sdd/patterns/dominio.md`) | o mapa do que o código já faz está em `scripts/checar.sh` e no ESCOPO, seção 2.4 |
| **Governança** | N.A. — sem dinheiro, lançamento, nota fiscal, tributo, folha nem dado pessoal; registrado por instrução do Roberto no pedido da sessão | 2026-11-17 |
| **Segurança** | N.A. — nenhum gatilho do catálogo (sem login, rota, dado de terceiros, upload, IA nem banco); a remoção fora do git é coberta pelos AT-008 e AT-009 | 2026-11-17 |

---

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|----|------------|------------------|------------|
| A-001 | O Claude Code lê `$CLAUDE_CONFIG_DIR/skills` no lugar de `~/.claude/skills` quando a variável existe (o `npx skills` assume isso) | um aluno com a variável teria a pasta global errada no diagnóstico | [ ] não medido (sem login no HOME de teste); o padrão `~/.claude` foi medido |
| A-002 | O Open e o starter usam o mesmo `metadata.version` para a mesma skill de uma mesma release | a regra "Open × starter com a mesma versão = mesma versão" escolheria errado | [x] 5 skills conferidas (Open v2.20.0 × `~/.agents/skills`) |
| A-003 | O `npx skills remove <skill> -g -a <agente>` só toca a pasta global do agente indicado e `~/.agents/skills/<skill>` | a proteção do AT-009 deixaria passar uma pasta | [x] código do CLI 1.9.0 (`removeInstalledSkills`) e EXP-3; o `--limpar` confere depois de cada `remove` |
| A-004 | Apagar a pasta de onde o próprio `checar.sh` roda (cópia velha da `sdd-checar-ambiente`) não interrompe o script no macOS, no Linux e no Git Bash | o `--limpar` pararia no meio | [ ] o Design decide a ordem (tirar essa cópia por último) e o teste prova no macOS; o Windows, pelo CI |

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---------|-------------|-------|
| Problem | 3 | caso medido, três cópias e três versões, e o que cada agente roda medido |
| Users | 3 | aluno do starter que adota o Open; quem tem cópias manuais antigas; mantenedor |
| Goals | 3 | DC1–DC4 e a decisão do `npx` fixam o quê; os experimentos fixam as pastas |
| Success | 3 | hash da árvore, 0 arquivos mudados, tempo +1 s, exit codes |
| Scope | 2 | o comportamento do `npx` pode mudar de versão; coberto pela conferência depois do `remove`, não pela spec |
| **Total** | **14/15** | |

---

## Open Questions

Nenhuma — pronto para a UX Review e o Design.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-11-17 | define-agent | Versão inicial, com os 3 experimentos medidos e a decisão do Roberto sobre a saída pelo `npx` |
| 1.1 | 2026-11-17 | design | Sem `CHANGELOG.md` na raiz do Open; a biblioteca `scripts/duplicadas.sh` e os testes que mudam entram na Deployment Location |

---

## Next Step

**Ready for:** `/sdd-ux-review sdd/features/DEFINE_F25_SKILLS_DUPLICADAS.md` (curta: o texto que o aluno lê), depois
`/sdd-design sdd/features/DEFINE_F25_SKILLS_DUPLICADAS.md`.
