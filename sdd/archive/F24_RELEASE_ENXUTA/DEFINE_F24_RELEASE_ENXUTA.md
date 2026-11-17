# DEFINE: F24 Release enxuta — a parte depois do push

> A `sdd-release` passa a terminar em poucos minutos depois do deploy: a curadoria só colhe e põe na fila, um commit
> só leva todo o papel, as limpezas viram padrão com recibo, a ficha cresce por acréscimo, o conserto pequeno ganha
> trilha curta e o aluno ouve, em palavras simples, para que serve cada etapa.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | F24_RELEASE_ENXUTA |
| **Date** | 2026-11-16 |
| **Author** | define-agent (sessão do Roberto) |
| **Status** | Ready for Design |
| **Clarity Score** | 14/15 |

---

## Problem Statement

Medido no projeto de origem em 16/11/2026: o deploy leva cerca de 2 min, mas do deploy pronto até o último commit
de papel passaram 19, 20 e 43 min em 3 publicações, porque depois do "1 OK" a `sdd-release` ainda pode parar até 6
vezes (smoke vermelho, apagar branches, remover worktree, perguntas de regra, envio do commit da curadoria,
arquivar o DoD), mais a oferta do prompt de retomada. A curadoria roda inteira em toda publicação, embora em 30
dias 18 de 30 curadorias não tenham trazido regra nova e, nas 4 detalhadas, 37 de 43 deltas fossem só contagem;
de 49 deploys em 3 dias, 28 não tinham arquivo publicável (18 de curadoria/playbook, 6 de ficha/DoD); e a mesma
publicação é escrita 6 vezes (bloco "Publicado", "Histórico de slices", ledger, changelog, relatório final e resumo
de etapa), com fichas de 140 a 234 linhas.

---

## Target Users

| User | Role | Pain Point |
|------|------|------------|
| Quem publica com o Open (em geral, aluno que nunca usou git) | dá o OK e espera a release terminar | depois do OK a sessão ainda pergunta e espera; não sabe o que cada etapa depois do push faz nem se pode deixar para depois |
| Mantenedor de um projeto com deploy automático | paga cada deploy e lê a ficha | push de papel dispara deploy sem código novo; a ficha repete o ledger e fica longa demais para ler |
| Mantenedor do Open | decide as regras do playbook | julga 30 curadorias por mês, das quais 18 sem regra nova, uma por publicação, no meio da release |

---

## Goals

| Priority | Goal |
|----------|------|
| **MUST** | Curadoria fora da publicação: a release só prepara, colhe e põe a colheita na fila; julgamento, contagem, perguntas de regra, aplicação e envio passam para um lote chamado pela `sdd-playbook`, sob demanda |
| **MUST** | As 4 garantias da curadoria continuam, agora no lote: falha da colheita nunca vale como "nada a colher"; quem separa contagem de regra é o conferidor; o curador é conferido pela fronteira de escrita; mudança de regra sempre pergunta |
| **MUST** | Com várias colheitas na fila, cada linha colhida conta uma vez só e os `LM-nnn` novos não colidem |
| **MUST** | Um commit de papel só depois do deploy (ficha, changelog, entrada da fila, arquivamento), com o bloco do OK dizendo se esse push publica |
| **MUST** | Depois do OK sobra uma parada possível: o smoke vermelho depois do deploy. Apagar a branch da frente e arquivar o DoD viram padrão, com recibo e como desfazer; o passo 20 sai |
| **MUST** | Ficha por acréscimo: o bloco "Publicado" sai do ledger por script; o agente escreve só "Falta" e os alertas; relatório final, ficha e resumo de etapa não repetem o mesmo conteúdo |
| **MUST** | Trilha curta para conserto pequeno, decidida por comando |
| **MUST** | Explicação da parte depois do push ao aluno: para que serve, o que acontece sem ela, se é obrigatória agora ou pode esperar |
| **SHOULD** | Quando o push do commit de papel publica, a ficha ganha a pendência de tirar os documentos do gatilho de deploy, com o trecho de workflow pronto |
| **COULD** | — |

---

## Success Criteria

- [ ] Depois do "sim" do OK, o texto da `sdd-release` tem exatamente 1 pergunta possível (o smoke vermelho depois do deploy), conferido por teste sobre as FASES 2 a 4 da skill.
- [ ] Depois do push do código, a release faz no máximo 1 commit e 1 push (o de papel); o commit da curadoria some da release (0 commits de playbook por publicação).
- [ ] Numa fixture com 2 publicações da mesma feature sem lote entre elas, o lote aplica cada contagem 1 vez (0 contagem em dobro) e 2 lições novas saem com IDs seguidos, sem colidir com o playbook da base.
- [ ] O bloco "Publicado" gerado para uma fixture de 3 ledgers tem 3 linhas, e rodar o gerador 2 vezes dá o mesmo arquivo, byte a byte.
- [ ] A ficha da trilha curta tem no máximo 20 linhas e passa no `handoff-lint.py`.
- [ ] A suíte inteira passa no macOS e no Windows (job `testes-windows` do CI), com 0 falha, e o starter sai do gerador sem edição à mão.

---

## Acceptance Tests

| ID | Padrão | Critério (EARS) | Gate (`kind`) |
|----|--------|-----------------|---------------|
| AT-001 | Event-driven + Unwanted | **When** a release chega à curadoria, the system **shall** rodar só `playbook-curator.sh --preparar` e `--colher` e gravar na fila da curadoria uma entrada com a colheita e o exit dela, sem despachar curador, sem perguntar regra, sem aplicar nem enviar nada do playbook; **If** o `--colher` sai com qualquer código fora de `0` e de `1` com `RESULTADO: NADA A COLHER`, **then** a entrada **shall** ficar na fila marcada como falha, com o código, e a ficha **shall** dizer `Curadoria: FALHOU (rc=N)`, nunca `0 deltas` | test |
| AT-002 | State-driven | **While** a fila tem colheita ainda não julgada de uma feature, the system **shall** deixar fora de uma colheita nova da mesma feature toda linha cuja impressão (`fp=`) já está na fila ou em `CURATOR-colhidos.txt`; **and when** o lote julga a fila, cada impressão **shall** entrar uma vez só em `CURATOR-colhidos.txt` e cada contagem **shall** somar no máximo +1 por impressão | test |
| AT-003 | Event-driven | **When** a pessoa chama o lote pela `sdd-playbook`, the system **shall**, para cada entrada da fila: despachar o curador em contexto fresco com os 5 campos, conferir o bloco com `--conferir-bloco` (fronteira de escrita e selo do staging), aplicar sem pergunta só as linhas `AUTO` e levar cada linha `PERGUNTA` à pessoa como `[D3 · muda a regra do método]`; e **shall** aplicar o que entrou de todas as entradas num `--aplicar` só, sobre o playbook da branch padrão, de modo que os `ADD` recebem IDs seguidos a partir do maior ID da base | test |
| AT-004 | Unwanted | **If** o bloco de uma entrada reprova 2 vezes no `--conferir-bloco`, ou o curador escreve no playbook, **then** the system **shall** não aplicar nada dessa entrada, mantê-la na fila com o motivo e seguir com as outras; a linha cuja evidência não foi copiada para a entrada (log que o projeto não versiona) **shall** ser relatada e nunca contada, sem segurar o resto da entrada; e o envio do commit do lote **shall** pedir `[D1 · não se desfaz]`, dizendo se esse push publica | test (negativo) |
| AT-005 | Optional feature | **Where** a fila tem mais de 5 entradas, the release **shall** imprimir 1 linha com o número de entradas e o comando do lote, sem perguntar e sem rodar o lote; com 5 ou menos, nenhuma linha | test (matriz) |
| AT-006 | Event-driven | **When** o deploy e o smoke depois do deploy terminam (ou a decisão do smoke vermelho foi tomada), the release **shall** fazer um só commit com a ficha, o `CHANGELOG.md`, a entrada da fila e os `git mv` do arquivamento (`git diff --cached --name-only` só com esses) e enviá-lo sem nova pergunta; o bloco do OK **shall** dizer, antes do "sim", se o push desse commit publica, pela resposta de um script que lê `on.push` (`paths`, `paths-ignore`, `branches`) dos workflows contra a lista de arquivos do commit (`PUBLICA`, `NAO_PUBLICA`, `NAO_SEI`); com `PUBLICA`, a ficha **shall** ganhar a pendência ✨ de tirar `sdd/**` e `*.md` do gatilho, com o trecho de workflow | test |
| AT-007 | Event-driven + Unwanted | **When** o commit de papel está na branch padrão do remoto, the release **shall**, sem pergunta e com 1 linha de recibo cada (o que fez e o comando que desfaz): apagar a branch da frente no remoto, se ela existe lá e já está toda integrada em `origin/{default_branch}` (por conteúdo, `git cherry`: a release aterrissa por cherry-pick); arquivar com `git mv` os documentos da feature quando o ledger desta release diz `estado: shipado` (dentro do commit de papel); e dar, no relatório, o comando que remove a worktree e a branch local, rodado de fora. **If** o envio do commit de papel falha ou a branch tem commit que não entrou, **then** a release **shall** não apagar nada, deixar o commit na branch da frente e dar o comando de envio no relatório, sem perguntar. O texto das FASES 2 a 4 **shall** ter uma única pergunta (o smoke vermelho) e nenhuma oferta de prompt de retomada | test |
| AT-008 | Event-driven + Unwanted | **When** um script gera o bloco "Publicado" da ficha a partir de `sdd/releases/<F>/*.yaml`, the system **shall** escrever 1 linha por release (data, slice, versão, estado, veredito, deploy e o SHA do commit que trouxe o ledger, lido do git), só entre os marcadores do bloco, sem tocar o resto da ficha, e o mesmo resultado byte a byte numa 2ª execução; **If** um ledger não é legível, **then** a linha dele **shall** dizer `n/d (ledger ilegível: <arquivo>)` e o script **shall** sair ≠ 0. A skill **shall** mandar o agente escrever só "Falta" e os alertas, e o relatório final **shall** citar a ficha pelo caminho, sem imprimi-la, e o resumo de etapa não repete as linhas do relatório | test |
| AT-009 | Optional feature | **Where** a frente não tem `DEFINE_<F>.md` (nem em `sdd/features/` nem em `sdd/archive/<F>/`) e o diff desde o ponto em que ela nasceu de `origin/{default_branch}`, com o que ainda não foi commitado e fora dos documentos do SDD (`sdd/features`, `reports`, `reviews`, `handoffs`, `releases`, `archive`, `curadoria`, `traces`, `contexto`) e do `CHANGELOG.md`, tem até 3 arquivos e até 100 linhas mudadas (sem arquivo binário), um comando **shall** imprimir `TRILHA: curta`; em qualquer outro caso, `TRILHA: completa` com o motivo. Na trilha curta, a ficha **shall** ter até 20 linhas fora do prompt de retomada (Ficha, Publicado, Falta) e passar no `handoff-lint.py --curta`, que reprova acima de 20; as FASES 0 a 2 **shall** continuar iguais nas duas trilhas | test (matriz) |
| AT-010 | Unwanted | **If** a colheita guardada numa entrada da fila não é igual à colheita refeita pelo `--colher` sobre os documentos copiados na própria entrada (linha a mais, a menos ou diferente), ou um documento copiado nunca esteve no lugar dele no histórico do git (entrada fabricada), ou a pasta da entrada mudou depois do commit que a criou, **then** o lote **shall** não despachar o curador nem aplicar nada dessa entrada e **shall** mantê-la na fila com o motivo | test (negativo) |
| AT-011 | Ubiquitous + Non-regression | The `references/como-falar.md` da `sdd-release` **shall** ter uma linha por etapa depois do push, com o nome para o aluno, "para que serve", "sem ela" e "agora ou pode esperar", sem número de passo, e um teste **shall** conferir que toda etapa das FASES 2 a 4 tem a sua linha e toda linha tem a sua etapa, como a tabela do pré-voo da `sdd-new-session`. The system **shall continue to**: ter os itens 8 a 10 da FASE 2 (reconferir a base, deploy conferido pelo SHA, smoke depois do deploy) e o ledger dentro do commit atômico; passar `playbook-curator.sh --self-test` e a suíte inteira no macOS e no Windows; gerar o starter só por `scripts/gerar-starter.py` | test |

Padrões considerados:
- **While:** AT-002 (fila com colheita ainda não julgada).
- **If/Then:** AT-001 (colheita que falha), AT-004 (bloco reprovado, escrita do curador, evidência ausente), AT-007 (envio do papel que falha), AT-008 (ledger ilegível), AT-010 (colheita guardada alterada).
- **Where:** AT-005 (fila acima do limite, matriz acima e abaixo) e AT-009 (trilha curta ou completa, matriz).

---

## Clarifications

### Session 2026-11-16

- [x] (integrações) As contagens podem ser aplicadas direto da colheita? → **Não.** O `--conferir-bloco` exige o bloco do curador (`sdd/bin/playbook-curator.sh:1362`), e o curador pode descartar uma contagem que não confere com a evidência (`.agents/skills/sdd-playbook/references/curator.md`, processo item 2: "Não confere ⇒ `DESCARTAR (motivo)`"; o conferidor aceita `DESCARTAR` em linha `contador`). Além disso, um `mordeu+1` numa lição `INV_PENDENTE` vira pergunta (`playbook-curator.sh`, ramo `m.group(2) == "mordeu" and m.group(1) in col["pend"]`). Aplicar direto pularia o filtro do curador. Pela regra do Roberto, **a contagem também vai para o lote**. Integrado em AT-001 e AT-003.
- [x] (dados) Como o lote evita contar 2 vezes? → Hoje a impressão de cada linha (`fp=`, de arquivo, tipo, lição e texto, sem o número da linha) só entra em `CURATOR-colhidos.txt` depois do julgamento (17b item 7), então 2 publicações sem lote no meio colheriam as mesmas impressões. Regra: a colheita nova exclui também as impressões que já estão na fila, e o lote grava todas as que julgou. As entradas da fila ficam disjuntas por impressão. Integrado em AT-002.
- [x] (dados) Como os `LM-nnn` novos não colidem? → O `--aplicar` já numera os `ADD` na hora, pelo maior ID do playbook que recebe o delta (`proximo_id`, `playbook-curator.sh:281` e `:833`), não pelo ID que a colheita propôs. Com um `--aplicar` só, sobre o playbook da branch padrão, os IDs saem seguidos e sem colisão. O recibo do lote mostra o ID final. Dois lotes em paralelo colidem no push e se resolvem como o envio de hoje (reaplicar sobre a base). Integrado em AT-003.
- [x] (dados) Onde fica a fila e o que ela guarda? → Decisão do agente, para o Roberto reverter: uma pasta por publicação dentro de `sdd/curadoria/fila/<F>/`, versionada (ela entra no commit de papel), com a colheita, o exit e a cópia dos documentos que a colheita cita, porque a worktree da frente pode ter sido removida quando o lote roda e a ficha cresce depois (o número da linha mudaria). Os logs de avaliação (`AVAL*-*.log`) só são copiados quando o projeto já versiona a evidência (o mesmo teste do 17b item 8); quando não versiona, a linha que cita um deles vai para o lote como "evidência ausente" (AT-004), nunca contada e nunca apagada em silêncio. O caminho exato é do Design.
- [x] (NFRs) Limite da fila → **mais de 5 entradas**. No projeto de origem houve ~1 curadoria por dia, e 12 de 30 trouxeram regra nova; com 5 publicações na fila, espera-se ~2 perguntas de regra paradas, cerca de uma semana de trabalho. Número fixo, sem slot (o padrão é o mesmo para todos). Integrado em AT-005.
- [x] (escopo) "DoD fechou" por comando → o ledger desta release com `estado: shipado` (o campo já aparece no bloco do OK, que a pessoa aprovou); `parcial` e `pausa` não arquivam. Integrado em AT-007.
- [x] (escopo) Que branch se apaga? → A da frente, no remoto, quando existe lá e é ancestral de `origin/{default_branch}` (o comando que desfaz é `git push origin <sha>:refs/heads/<branch>`). A branch local não se apaga de dentro da worktree em que está: o relatório dá o comando, rodado de fora, como o MODO_INICIANTE já faz. Integrado em AT-007.
- [x] (escopo) Critério da trilha curta → sem DEFINE (nem arquivado) e diff até 3 arquivos e até 100 linhas fora dos documentos do SDD e do `CHANGELOG.md`, sem binário, contando o que ainda não foi commitado (a release mede antes do commit atômico); decisão do agente, para o Roberto reverter. `sdd/bin/` não é documento: no próprio Open, é código. A trilha curta só encurta a parte depois do push (ficha curta; curadoria só com a colheita, que sem DESIGN nem BUILD_REPORT já dá `0 deltas (sem documentos)`); as verificações antes do OK não mudam. Integrado em AT-009.
- [x] (terminologia) "Publicado" × "Feito" → o molde da ficha tem `## Feito`, e o projeto de origem usa um bloco "Publicado". O bloco gerado é uma seção própria, `## Publicado`, entre marcadores; `## Feito` fica para o que não está no ledger. O `handoff-lint.py` passa a aceitar o bloco "Publicado" com ≥1 linha como histórico, para a ficha curta não precisar de um "Histórico de slices" que repete o ledger.
- [x] (UX) Explicação ao aluno → mora em `references/como-falar.md` da `sdd-release`; uma frase por etapa no fluxo normal, a explicação completa quando o aluno pede ou responde "não sei". O MODO_INICIANTE (projeto sem `sdd/bin/`) já não tem curadoria nem limpeza perguntada e **não é alterado**, para não conflitar com a `feat/f23b3-cadeia-revisao`.
- [x] (UX) UX review → N.A.: a fatia não tem tela. A saída é texto de skill e de script no padrão das outras skills, já revisado na F4. A `/sdd-ux-review` fica ➖ por esta decisão.
- [x] (restrições) Conflito com a `feat/f23b3-cadeia-revisao` → ela altera `sdd-release/SKILL.md` (versão 2.15.0 e o item 8 da FASE 0a), `references/MODO_INICIANTE.md` (2 linhas), `sdd/playbook.md` e `sdd/bin/sdd-fluxo.sh`. Conflito certo na linha de versão da skill e possível no `sdd-fluxo.sh` (o despacho do curador). Quem publicar depois rebaseia sobre a outra e escolhe a versão seguinte da skill. Registrado em Constraints.

### Session 2026-11-16 (governança)

- [x] (governança) N.A. — revisor fresco, 2026-11-16: sem dinheiro, lançamento, nota fiscal, tributo, folha nem dado pessoal.

### Segurança

- Gatilho: `ia` (o lote despacha um agente, o curador, que lê documentos e a colheita guardada no git). Stack detectada: nenhuma (só itens `stack: todas`).
- S20 (agente com poder demais): já atendido pelo AT-003 e pelo AT-004 (fronteira de escrita, selo do staging, conferidor e pergunta para toda mudança de regra).
- S18 (instrução escondida em conteúdo externo): **aplicado** no AT-010. A colheita passa a morar no git por dias, e qualquer push na branch padrão poderia plantar uma linha de contagem que nenhuma release colheu; o lote refaz a colheita sobre os documentos da entrada e só julga o que bate. Decidido pela opção recomendada, sob o pedido do Roberto de seguir o pipeline com os padrões; reversível na revisão do DESIGN.

---

## Verify Gate

```yaml
verify_gate:
  kind: test
  cmd: "T=$(mktemp -d) && git archive HEAD | tar -x -C $T && PUBLISH_GATE_MODE=ci bash scripts/publish-gate.sh $T && cd $T/tests && SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest test_f24_release_enxuta && cd $T && SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover -s tests -p 'test_*.py'"
  pass_when: "exit 0"
  threshold: "—"
  manual_fallback: "—"
```

Cobertura:
- AT-001 a AT-010: um módulo novo, `tests/test_f24_release_enxuta.py`, chamado pelo nome no `cmd` (sem ele, o gate fica vermelho: é o baseline vermelho). Fixtures em `sdd/fixtures/f24/`: um projeto com playbook e invariantes, 2 publicações da mesma feature (com linhas repetidas e 2 candidatos), uma colheita que falha, um bloco reprovado, uma entrada da fila com uma linha de contagem plantada, 3 ledgers (1 ilegível), workflows com e sem `paths-ignore`, e diffs de conserto pequeno e grande.
- AT-003 e AT-004 despacham o curador: o teste usa blocos de curador gravados (o mesmo jeito de `tests/test_curadoria_bloco.py`); o lote é conferido pelos scripts, não pela obediência do agente.
- AT-007 e AT-011 (texto): testes sobre `.agents/skills/sdd-release/SKILL.md`, `references/como-falar.md`, `sdd-playbook/SKILL.md` e `sdd-handoff/SKILL.md`.
- AT-011 (não-regressão): a suíte inteira, que inclui `test_playbook_curator.py`, `test_curadoria_bloco.py`, `test_contrato_build_release.py` e `test_gerar_starter.py`.

O gate roda de um `git archive HEAD`, como na F22 e na F23. O Windows é provado pelo job `testes-windows` do CI do PR.

---

## Out of Scope

- O workflow de deploy e a conta do smoke do projeto de origem (ficam para depois).
- Rodar o lote sozinho (cron, gancho, encadeamento): o lote só roda quando alguém o chama.
- Modo opcional, slot de configuração ou exceção para iniciante: o padrão novo vale para todos.
- Mudar os itens 8 a 10 da FASE 2, o bloco do OK além da linha nova do push de papel, e o ledger no commit atômico.
- O MODO_INICIANTE (projeto sem `sdd/bin/`).
- Editar o workflow de deploy do projeto do usuário: a release só recomenda, com o trecho pronto.
- Reescrever fichas antigas: o bloco "Publicado" passa a valer na próxima publicação de cada feature.
- Apagar a branch local ou a worktree de dentro dela.

---

## Constraints

| Type | Constraint | Impact |
|------|------------|--------|
| Technical | bash 3.2 e Python 3.9 stdlib, como o resto de `sdd/bin/`; Windows (Git Bash + Python nativo) | scripts novos com saída UTF-8 e `\n`, testados no job `testes-windows` |
| Technical | As garantias da curadoria mudam de lugar e não somem (falha ≠ nada a colher; conferidor separa; fronteira; regra pergunta) | o lote reusa `--conferir-bloco`, `--selar`, `governanca-fronteira.sh` e `--validar-inv`, sem afrouxar nenhum |
| Technical | Nada é corrigido direto no starter | as skills mudam no Open e o starter é gerado |
| Technical | `MANIFEST.txt` a cada arquivo novo do pacote | o publish-gate reprova arquivo fora do manifesto |
| Technical | Repositório público | nenhum nome de feature, conta ou dado do projeto de origem; os números entram como "medido no projeto de origem" |
| Process | Conflito com a `feat/f23b3-cadeia-revisao` (linha de versão da `sdd-release`, item 8 da FASE 0a, `MODO_INICIANTE.md`, `sdd/playbook.md`, `sdd-fluxo.sh`) | a F23B3 foi publicada primeiro (2026-11-16, `fb7ee82`); a F24 rebaseou sobre ela, sobe a `sdd-release` para 2.16.0, muda no MODO_INICIANTE só a linha de versão e não toca o `sdd-fluxo.sh` |
| Process | A linha da F24 em "Estado das frentes" do plano só se edita na worktree `sdd-open-docs-f16`, com commit e push na mesma sessão, com o OK do Roberto | fora do commit desta branch |
| Process | Os artefatos SDD desta frente (DEFINE, DESIGN, relatórios) não vão para a `main` | ficam fora do commit de código |

---

## Technical Context

| Aspect | Value | Notes |
|--------|-------|-------|
| **Deployment Location** | `.agents/skills/sdd-release/` (`SKILL.md`, `references/como-falar.md`, `scripts/` para a leitura do gatilho do push), `.agents/skills/sdd-playbook/` (`SKILL.md`, `references/curator.md`: o lote), `.agents/skills/sdd-handoff/SKILL.md`, `sdd/bin/playbook-curator.sh` (fila, exclusão pela fila), `sdd/bin/` (gerador do bloco "Publicado", trilha), `sdd/bin/handoff-lint.py`, `sdd/templates/HANDOFF_TEMPLATE.md`, `sdd/fixtures/f24/`, `tests/test_f24_release_enxuta.py`, `MANIFEST.txt`, `docs/` (a página da curadoria) | `scripts/` é do mantenedor; o starter sai do gerador |
| **KB Domains** | nenhum | o Open não tem `sdd/kb/` |
| **IaC Impact** | None | — |
| **LLM Prompts** | false | nenhum prompt de produção: o brief do curador é instrução de agente do método, não runtime de produto (sinal fraco "curador", descartado: já existe e só muda de quem chama) |
| **CONTEXTO de domínio** | nenhum (pulado: o Open não tem `sdd/patterns/dominio.md`) | `contexto-lint.sh --sugerir` → PULAR |
| **Governança** | N.A. — o DEFINE trata das etapas da sdd-release depois do push, sem dinheiro, lançamento, nota fiscal, tributo, folha nem dado pessoal | revisor fresco, 2026-11-16 |
| **Segurança** | 1 aplicado (S18) · 0 recusados · 0 adiados; S20 já atendido pelos AT-003 e AT-004 | 2026-11-16 |

---

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|----|------------|------------------|------------|
| A-001 | A impressão `fp=` não depende do número da linha (arquivo, tipo, lição e texto) | a exclusão pela fila falharia quando a ficha cresce | [x] `Colheita.digital`, `playbook-curator.sh` |
| A-002 | O `--aplicar` numera os `ADD` pelo playbook que recebe o delta, não pela colheita | IDs colidiriam com várias colheitas | [x] `proximo_id` em `aplicar` (`playbook-curator.sh:833`) |
| A-003 | O curador pode descartar uma contagem | a contagem poderia sair direto da colheita | [x] `curator.md`, processo item 2 |
| A-004 | Ler `on.push` dos workflows basta para dizer se um push de papel publica, e o que o script não entende vira `NAO_SEI` | push de papel publicaria sem aviso | [ ] o Design reusa o mini-parser do `deploy-espera-testes.py` e prova com fixtures |
| A-005 | Copiar na fila os documentos que a colheita cita não leva ao git nada que o projeto deixou de fora (os logs só com evidência versionada) | vazaria arquivo ignorado | [ ] o Design confere o teste de "versiona evidência" do 17b item 8 |

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---------|-------------|-------|
| Problem | 3 | números medidos no projeto de origem |
| Users | 3 | três perfis com a dor |
| Goals | 3 | 6 itens do escopo, com as garantias que não mudam |
| Success | 3 | contagens e fixtures |
| Scope | 2 | 3 decisões do agente para o Roberto reverter: onde fica a fila, o limite 5 e o critério da trilha curta |
| **Total** | **14/15** | |

---

## Open Questions

None - ready for Design. As 3 decisões do agente estão em Clarifications, para o Roberto reverter se quiser.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-11-16 | define-agent | Initial version (escopo de 6 itens, uma fatia) |
| 1.4 | 2026-11-16 | build-agent | Revisão do código, rodada 4 (R4@claude): o limite da ficha curta conta fora do prompt de retomada, que a ficha aberta precisa ter |
| 1.3 | 2026-11-16 | build-agent | Revisão do código, rodada 3 (R5): a branch remota se apaga quando está toda integrada por conteúdo (`git cherry`), não quando é ancestral — a release aterrissa por cherry-pick |
| 1.2 | 2026-11-16 | build-agent | `cmd` do Verify Gate roda o módulo da F24 de dentro de `tests/` (o `apoio` mora lá; de fora, o import falhava antes de testar) |
| 1.1 | 2026-11-16 | design-agent | Revisão do DESIGN (rodada 1): AT-004 trata a evidência ausente por linha (R5); AT-009 cita o DEFINE arquivado, os documentos do SDD e o `handoff-lint.py --curta` (R6, N1); AT-010 recusa também a entrada fabricada e a pasta mexida (R3) |

---

## Next Step

**Ready for:** `/sdd-design sdd/features/DEFINE_F24_RELEASE_ENXUTA.md` (sem interface: UX review pulada, ver Clarifications)
