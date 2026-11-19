# DEFINE: F28 — revisores pelo OpenRouter (`sdd-configurar-revisores`)

> Uma skill nova, no molde da `sdd-checar-ambiente`, que descobre o estado da revisão adversarial deste computador
> (slots, chave do OpenRouter, CLIs instaladas), conduz o aluno passo a passo até os revisores configurados pelo
> OpenRouter (ou pelas CLIs que ele já tem, ou por uma engine só, com a consequência dita), grava a escolha como
> preferência deste computador e termina com a prova, sem gastar e sem a chave passar pela conversa.

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | F28_REVISORES_OPENROUTER |
| **Date** | 2026-11-18 |
| **Author** | define-agent (worktree `sdd-open-f28-revisores-openrouter`; branch `feat/f28-revisores-openrouter`, de `origin/main` `eaeb874` = `v2.24.0` + 3 commits de documento) |
| **Status** | Ready for UX Review |
| **Clarity Score** | 14/15 |
| **Entrada** | pedido direto do Roberto (2026-11-18), com fatos conferidos e decisões de partida: `sdd/handoffs/SESSION_PROMPT_F28_REVISORES_OPENROUTER.md` (sem brainstorm, por decisão do pedido) |

---

## Problem Statement

Quem instala o SDD Open recebe `review.revisor1: ""` e `review.auditor: ""`; o `init` não pergunta nada disso. Com os
slots vazios, a `sdd-design` e a `sdd-build` (passos 0 e 5c) mandam "perguntar à pessoa quais engines usar", o
`adversarial-review.sh` sai 64, e o aluno recebe uma pergunta sobre "engines" sem saber o que responder. Na
`sdd-release` (FASE 0, item 8), sem orientação, o caminho mais fácil é dispensar a revisão sempre. O caminho natural
de quem tem um agente só é o OpenRouter (dois modelos diferentes servem de revisor e auditor), mas ele exige conta,
crédito, chave e a chave no ambiente do agente — e nenhum documento do aluno explica isso: o guia do aluno não cita
revisor, auditor nem OpenRouter, e o `docs/pt-BR/adversarial-review.md` é técnico. O `checar.sh` não olha nada disso.
Pedido do Roberto: "fundamental explicar o passo a passo para alunos e não deixar o aluno sem orientação".

---

## Target Users

| User | Role | Pain Point |
|---|---|---|
| Aluno com um agente só (o caso comum) | chega à revisão do DESIGN ou do código | não sabe o que é engine, não tem chave de API, nunca editou o perfil do terminal; dispensa a revisão por falta de caminho |
| Aluno com 2 ou mais CLIs logadas (claude, codex, gemini) | idem | não sabe que já tem o necessário sem custo extra |
| Aluno que voltou depois de gravar a chave | reabre o agente e pede de novo | a skill não pode repetir o passo a passo inteiro nem fingir que a chave chegou |
| Aluno no Windows (Git Bash ou WSL) | idem | o perfil do terminal e a herança do ambiente são diferentes do Mac |
| Aluno que não quer ou não pode pagar o OpenRouter | idem | precisa de um caminho honesto (uma engine só, ou nenhuma por ora) com a consequência dita |
| Mantenedor do Open | mantém o pacote público e agnóstico | a chave nunca pode cair no repositório, na conversa ou num log; nome de modelo e preço só das tabelas com fonte e data |

---

## Goals

| Priority | Goal |
|---|---|
| **MUST** | skill nova `sdd-configurar-revisores` 1.0.0 em `.agents/skills/sdd-configurar-revisores/` (P1): `SKILL.md` com "Como falar com o aluno" e a tabela de estados, `references/como-falar.md`, o passo a passo do OpenRouter e do perfil por sistema em `references/`, e um script de diagnóstico em `scripts/` que só lê e decide por exit code |
| **MUST** | a chave nunca passa pela conversa, por argumento, arquivo do projeto ou log (P2); só o teste de existência e uma consulta de leitura que não cobra (P6) |
| **MUST** | a escolha vira preferência deste computador, em `git config --local sdd.revisor1` e `sdd.auditor` (A2); o `adversarial-review.sh` lê esses valores quando o slot do `sdd/config.yaml` está vazio; o slot e a flag continuam valendo antes |
| **MUST** | o `adversarial-review.sh --dry-run` mostra o plano mesmo sem diff (a frente recém-aberta) e diz quem faria o 2º revisor e o desempate, ou que não há engine para eles (A3) |
| **MUST** | ganchos (P7): `sdd-design`, `sdd-build` (passos 0 e 5c) e `sdd-release` (FASE 0, item 8, antes de aceitar a dispensa) oferecem a skill; o `checar.sh` da `sdd-checar-ambiente` ganha um aviso ⚠️, nunca 🔴 (A5) |
| **MUST** | documentação (P8): seção nova no guia do aluno, `docs/adversarial-review.md` e `docs/pt-BR/adversarial-review.md`, README e README.pt-BR (lista de skills), `MANIFEST.txt` |
| **MUST** | modelo e preço só do `registry.tsv` e do `precos.tsv` (P4); os nomes de tela do OpenRouter conferidos na página oficial no dia do Build |
| **SHOULD** | cenários de comportamento em contexto novo (LM-011): 3 estados (sem nada; chave gravada sem reabrir; chave colada no chat) × 2 execuções, com o critério de aprovado escrito antes |
| **COULD** | modelo por papel (`papeis:`), cofre do sistema, outro provedor — fora (ver Out of Scope) |

---

## Tabela de estados do aluno (requisito central)

Cada linha é um estado que o diagnóstico reconhece e o que o aluno ouve e faz. **Estado sem linha é defeito**: o
teste confere que todo estado que o script emite tem linha na tabela da skill, e vice-versa (AT-001). Os nomes
finais (`Rnn`), a ordem de precedência e o texto exato são do Design; o conjunto mínimo é este.

| Estado | Como se reconhece (só leitura) | O que o aluno ouve | O que o aluno faz |
|---|---|---|---|
| sem revisão neste projeto | não há `sdd/bin/adversarial-review.sh` | este projeto não tem a revisão adversarial do SDD Open; nada a configurar | instalar o SDD Open (`init`) ou seguir sem ela |
| sem bash | a skill roda em PowerShell puro | a revisão roda em bash; no Windows, Git Bash ou WSL | abrir o agente pelo Git Bash (ou WSL) e pedir de novo |
| pronto | revisor e auditor resolvidos, engines diferentes, cada uma disponível (CLI no PATH; para o OpenRouter, a chave no ambiente) | está configurado; mostra o plano (`--dry-run`) | nada; a revisão roda quando a fase pedir |
| vazio, com 2+ CLIs | slots e `git config` vazios; 2 ou mais de `claude`, `codex`, `gemini` no PATH | dá para usar o que já tem, sem custo extra | escolher: as 2 CLIs (recomendado) · OpenRouter · uma engine só · não sei |
| vazio, com 1 ou 0 CLI, sem chave | slots vazios; chave ausente no ambiente e no perfil | o caminho é o OpenRouter (custa por uso); explica revisor e auditor | escolher: OpenRouter (recomendado, passo a passo) · uma engine só · agora não · não sei |
| chave gravada, agente não reaberto | chave ausente no ambiente do agente, mas presente no perfil do terminal (ou nas variáveis do Windows), conferida sem ler o valor | a chave está gravada, mas este agente foi aberto antes dela | parada: fechar e abrir o agente (e o editor, se o agente roda nele); pedir de novo |
| chave presente, slots vazios | chave no ambiente, slots vazios | a chave chegou; escolher os modelos | ver o par sugerido, o custo e o que sai do computador; dar o OK de gravar |
| chave recusada | consulta da chave devolve 401 ou 403 | a chave não vale: copiada pela metade, apagada ou revogada | criar outra chave e regravar (passos) |
| sem crédito | consulta da chave diz que a conta nunca pôs crédito; ou 402 na revisão real | a conta não tem crédito | pôr crédito (passos), pedir de novo |
| limite da chave esgotado | a chave tem limite de gasto e o que resta é zero | o limite de gasto desta chave acabou | aumentar o limite da chave ou criar outra (passos) |
| sem limite de gasto | a chave não tem limite de gasto | aviso: sem teto, um erro pode gastar mais que o previsto | pôr um limite na chave (passos); seguir é possível |
| muitas chamadas agora | 429 | o OpenRouter pediu para esperar | esperar 1 minuto e pedir de novo |
| sem internet | erro de rede ou nenhuma resposta no teto de tempo | não alcancei o OpenRouter; nada foi gravado | conferir a internet; pedir de novo |
| modelo inexistente | o modelo do par (ou do slot) não aparece na lista pública de modelos | o modelo saiu do OpenRouter | atualizar o pacote (`upgrade`), ou dizer outro modelo (preço desconhecido, `$?`), ou outra opção |
| sem provedor que não guarde o dado | "No endpoints found" na revisão real | nenhum provedor desse modelo aceita a regra de não guardar o dado | trocar o modelo daquele papel |
| slots cheios, chave ausente | slot ou `git config` usa `openrouter`, chave ausente | o projeto já escolheu o OpenRouter; falta só a chave | só o passo a passo da chave (não pergunta modelos) |
| slot cheio com CLI ausente | o slot nomeia uma CLI que não está no PATH | a engine escolhida não está neste computador | instalar a CLI, ou (se a escolha é deste computador) trocar |
| só um slot cheio | revisor sem auditor, ou o contrário | falta o outro papel | escolher o que falta |
| auditor igual ao revisor | mesma engine (mesmo adapter e modelo) | ninguém audita a própria revisão | escolher outro modelo ou outra engine para auditar |
| id desconhecido | o slot nomeia uma engine que o registry não tem | o nome não existe na lista | corrigir para um nome da lista |
| chave colada no chat | a mensagem do aluno contém algo com a forma de uma chave | não uso esta chave: ela ficou na conversa; revogue-a e crie outra | revogar e criar outra (passos); nunca repetir a chave |
| uma engine só escolhida | o aluno escolheu `--um-engine` | a auditoria terá os mesmos pontos cegos (`diversidade: nenhuma`); nada é gravado (a regra "auditor diferente do revisor" fica), e cada fase oferece `--um-engine` naquela revisão | nada; fica registrado na revisão |
| agora não | o aluno adiou | consequência: a release vai pedir a dispensa com motivo | pedir a skill quando quiser |

---

## Success Criteria

- [ ] Todo estado da tabela tem um caso de teste do diagnóstico, e todo estado que o script emite tem linha na tabela da skill (contagem igual nos dois lados).
- [ ] Em todos os casos dos testes, com `OPENROUTER_API_KEY` posta como texto de fixture, a saída do diagnóstico, do `--dry-run` e dos arquivos que a skill grava não contém esse texto: 0 ocorrências.
- [ ] O diagnóstico, sem `--testar`, faz 0 chamadas de rede e muda 0 arquivos e 0 chaves do `git config`.
- [ ] Com `--testar`, só chamadas de leitura (a consulta da chave e a lista pública de modelos) chegam ao servidor local: 0 chamadas a `chat/completions`; teto de 10 s por chamada.
- [ ] `git config --local sdd.revisor1`/`sdd.auditor` preenchidos e slots vazios ⇒ a revisão usa esses valores; slot cheio ⇒ o slot vence; flag ⇒ a flag vence (3 casos).
- [ ] `--dry-run` numa frente sem diff sai 0 com o plano; a revisão real sem diff continua saindo 64.
- [ ] Linha de base vermelha: os testes novos falham em `eaeb874`.
- [ ] Sabotagens: ao menos 5 mutantes (o diagnóstico imprime a chave; chama `chat/completions` no teste; grava no `sdd/config.yaml`; o `--dry-run` volta a sair 64 sem diff; o `checar.sh` marca 🔴; "limite esgotado" com `== 0` no lugar de `≤ 0`) derrubam, cada um, um teste nomeado.
- [ ] Verify Gate numa cópia de `git archive` sai 0, com a suíte inteira; CI do PR verde nos 3 sistemas.

---

## Acceptance Tests

| ID | Padrão | Critério (EARS) | Gate (`kind`) |
|---|---|---|---|
| AT-001 | Event-driven | **When** o script de diagnóstico da skill roda num projeto, ele **shall** imprimir exatamente uma linha `ESTADO: <id>` de um dos estados da tabela da skill, com a frase do aluno e o próximo passo, e sair com o código da classe do estado (fixado pelo Design); **shall** ser só leitura: sem `--testar`, nenhuma chamada de rede, nenhum arquivo e nenhuma chave de `git config` mudados; o conjunto de estados que o script pode emitir **shall** ser igual ao conjunto de linhas da tabela da skill marcadas `script`, e cada linha marcada `conversa` **shall** ter a situação e o que fazer (teste que compara os dois lados) | test |
| AT-002 | Unwanted | **If** `OPENROUTER_API_KEY` está no ambiente (fixture que não parece chave real), **then** o diagnóstico, o `--dry-run` do `adversarial-review.sh`, o `checar.sh` e todo arquivo ou chave de `git config` que a skill grava **shall** não conter o valor; a existência **shall** ser testada só por `[ -n "${OPENROUTER_API_KEY:-}" ]` (ou o equivalente que não imprime), e a chave **shall** ser lida só dentro do Python, do ambiente, nunca de argumento; **if** o perfil do terminal guarda a chave, **then** o diagnóstico **shall** reconhecê-lo sem imprimir a linha nem o valor; o passo a passo **shall** gravar a chave sem que ela apareça na tela, no histórico do terminal ou na conversa, e a skill **shall** mandar revogar uma chave colada no chat e nunca usá-la nem repeti-la | test |
| AT-003 | Event-driven | **When** o diagnóstico recebe `--testar` com a chave no ambiente, **shall** fazer só `GET` da consulta oficial da chave e da lista pública de modelos (URL trocável por variável de teste, servidor local), com teto de 10 s cada, e classificar: aceita · recusada (401/403) · sem crédito (a conta nunca pôs crédito) · limite da chave esgotado · sem limite de gasto (aviso) · muitas chamadas (429) · sem internet (erro de rede ou teto) · modelo inexistente; cada um com a frase do aluno e o passo; **shall** nunca imprimir texto que veio da resposta (rótulo da chave, mensagem de erro), só a classe e números; todo valor em dólar lido da API ou do `precos.tsv` **shall** ser lido como decimal exato (nunca ponto flutuante binário) e mostrado truncado em centavos, e a chave **shall** contar como "limite esgotado" quando o que resta, truncado em centavos, é ≤ 0 (com 0, -0,01 e 0,0004 ⇒ esgotado; com 1,00 ⇒ aceita); **shall** fazer 0 chamadas a `chat/completions` | test |
| AT-004 | State-driven | **While** a chave não está no ambiente do agente mas está no perfil do terminal deste sistema (zsh no macOS, bash no Linux e no WSL, as variáveis de usuário do Windows no Git Bash), o diagnóstico **shall** dar o estado "chave gravada, agente não reaberto", com a parada (fechar e abrir o agente e o editor) e "Quando terminar, me peça de novo, eu continuo daqui"; **when** o aluno volta com a chave no ambiente e os slots vazios, **shall** seguir para a escolha dos modelos sem repetir os passos da conta e da chave; **while** os slots já usam `openrouter` e a chave falta, **shall** conduzir só os passos da chave, sem perguntar modelos | test |
| AT-005 | Event-driven | **When** o aluno dá o OK de gravar, a skill **shall** gravar `git config --local sdd.revisor1 '<id>'` e `git config --local sdd.auditor '<id>'` (ids do registry, como `openrouter:<modelo>`), nunca o `sdd/config.yaml` nem a chave; o `adversarial-review.sh` **shall** usar esses valores quando o slot do `sdd/config.yaml` está vazio, o slot **shall** vencer o `git config`, a flag (`--reviewer`/`--auditor`) **shall** vencer os dois, e o plano **shall** dizer de onde veio cada valor; dois modelos diferentes do OpenRouter **shall** dar `diversidade: modelo`; o mesmo modelo nos dois **shall continue to** dar 67 | test |
| AT-006 | Event-driven | **When** `adversarial-review.sh --dry-run` roda numa frente sem diff, **shall** sair 0 com `RESULTADO: PLANO`, o revisor e o auditor com a origem, a disponibilidade de cada engine (sem rede: CLI no PATH, chave presente), quem seria o 2º revisor e o desempate pela regra de hoje (a 1ª engine disponível do registry fora da origem dos papéis) ou `nenhuma engine disponível` com a consequência (2º revisor: a release pede `--aceitar-sem-revisor2 "<motivo>"`; desempate: o achado fica para uma pessoa), e `diff: vazio`; a revisão real sem diff **shall continue to** sair 64 | test |
| AT-007 | Unwanted | **If** o aluno não quer ou não pode usar o OpenRouter, **then** a skill **shall** oferecer as CLIs que ele já tem (com 2 ou mais, a opção sem custo extra vem primeiro), uma engine só (`--um-engine`, com "diversidade: nenhuma" dita) e "agora não" (com a consequência na release); **where** a escolha é o OpenRouter, a skill **shall**, antes do OK de gravar, dizer em frases curtas que custa dinheiro por uso fora de qualquer assinatura, que o diff e os documentos SDD saem do computador, que só entram provedores que não guardam nem treinam com o dado, e lembrar a `sdd-higiene-dado`; e **shall** mostrar o par de modelos e o preço lidos do `registry.tsv` e do `precos.tsv`, sem nome de modelo nem preço escrito no `SKILL.md` ou nas `references/` | test |
| AT-008 | Event-driven | **When** os textos são lidos pelos testes, **shall** valer: a skill tem "Como falar com o aluno", a tabela de estados, passos numerados com um comando ou um clique por passo e o que esperar na tela, toda pergunta com a recomendada primeiro e **não sei**, o glossário (engine, revisor, auditor, chave de API, variável de ambiente, token, perfil do terminal, crédito), a parada com "Quando terminar, me peça de novo, eu continuo daqui", o caminho fora do computador (conta, crédito, chave, limite de gasto, guardar a chave) com os nomes de tela conferidos e a data; a `sdd-design`, a `sdd-build` (passos 0 e 5c) e a `sdd-release` (FASE 0, item 8, antes da dispensa) oferecem a skill; o guia do aluno tem a seção nova; `docs/adversarial-review.md` e `docs/pt-BR/adversarial-review.md` citam a skill e o `git config`; a skill está no README, no README.pt-BR e no `MANIFEST.txt`; todo texto novo passa no `tests/test_agnostico.py`, no `skill-lint.py --conversa` e no `tests/test_gerar_starter.py` | test |
| AT-009 | State-driven | **While** o projeto tem `sdd/bin/adversarial-review.sh` e nem o slot nem o `git config` têm revisor e auditor, o `checar.sh` no modo normal **shall** dar um item ⚠️ com a skill que resolve, nunca 🔴, e **shall** dar outro ⚠️ quando o revisor ou o auditor usa `openrouter` e a chave falta no ambiente; no `--frente`, no `--segredo` e no `--editor` **shall** não falar disso; sem `sdd/bin/adversarial-review.sh` (o starter), **shall** não falar disso; cada item novo **shall** dizer a consequência na 1ª frase e, na linha do comando, a skill que resolve (o modo normal repassa o relatório como veio, sem tabela de tradução) | test |
| AT-010 | Non-regression | A revisão real **shall continue to** dar os mesmos exits (64 a 68), a mesma cadeia e a mesma regra de identidade ("o mesmo adapter com o mesmo modelo é a mesma engine"); o `adversarial-review-gate.sh` **shall continue to** sair 0; o `--conferir` e o `--ledger` **shall continue to** dar o mesmo resultado; o adapter do OpenRouter **shall continue to** mandar `data_collection = "deny"` e `require_parameters = true`; a `sdd-release` **shall continue to** pedir um OK só e aceitar a dispensa com motivo; o `checar.sh` **shall continue to** dar a mesma saída nos casos dos testes dele; a suíte **shall continue to** passar no bash 3.2 do macOS (`SDD_TEST_BASH=/bin/bash`) e no Windows | test |

Considerados: **While** em AT-004 (chave gravada sem reabrir; slots cheios sem chave) e AT-009 (revisores não
configurados). **If/Then** em AT-002 (chave no ambiente, no perfil, colada no chat) e AT-007 (sem OpenRouter); os
gatilhos indesejados de rede e de conta (401/403, sem crédito, limite, 429, sem internet, modelo inexistente) estão
em AT-003. **Where** em AT-007 (escolha do OpenRouter). Não-regressão em AT-010, porque a frente mexe no
`adversarial-review.sh`, no `checar.sh` e em 3 skills de fase.

O comportamento da skill numa conversa real não é AT do gate local: é critério com evidência (SHOULD), em contexto
novo, 3 cenários × 2 execuções, com o critério de aprovado escrito antes (LM-011): (1) projeto sem nada, um agente só
⇒ explica revisor e auditor, recomenda o OpenRouter com o porquê, oferece "não sei", termina numa decisão; (2) chave
no perfil sem reabrir ⇒ reconhece e para com a instrução de reabrir, sem repetir a conta; (3) aluno cola algo com a
forma de chave ⇒ manda revogar, não repete o texto, não grava.

---

## Clarifications

### Session 2026-11-18

Pedido do Roberto para esta frente: em cada decisão, a recomendação vira o padrão e fica registrada; perguntar só
o crítico (OK de publicar; apagar o que não é desta frente; afrouxar proteção; mudar escopo; rodada acima do teto;
gastar dinheiro ou precisar de chave real). Nenhuma pergunta desta sessão foi crítica. Decidi sozinho:

- [x] (escopo) P1 a P8 do pedido valem como estão; nome da skill: `sdd-configurar-revisores`.
- [x] (UX) Há interface: a conversa com o aluno e a saída do script. O UX review roda (pedido do Roberto).
- [x] (dados, A2) **Onde gravar a escolha:** `git config --local sdd.revisor1` e `sdd.auditor`, como o
  `sdd.editor` da `sdd-new-session`. Prós: vale na hora para todas as frentes deste repositório (inclusive as já
  abertas), nunca é commitado, a pergunta não volta em cada frente; a escolha depende do que este computador tem
  (CLIs, chave). Contra: o `adversarial-review.sh` precisa ler o `git config` quando o slot está vazio (uma fonte a
  mais, dita no plano). Alternativa recusada: gravar no `sdd/config.yaml` da frente, que só chega à branch padrão na
  integração (a pergunta voltaria em cada frente até lá) e imporia ao time a escolha de um computador. Ordem: flag >
  slot do `sdd/config.yaml` (escolha do time) > `git config` (escolha deste computador). Integrado em AT-005.
- [x] (integrações, A3) **2º revisor e desempate com os dois papéis no OpenRouter:** o código de hoje exclui pela
  base do id (`openrouter`) e pela identidade; sobram `claude`, `codex` e `gemini`, se estiverem no PATH. Sem
  nenhuma: o 2º revisor sai `indisponível` (só é acionado com superfície de risco ou revisor raso; a release aceita
  com `--aceitar-sem-revisor2 "<motivo>"`), e o desempate fica para uma pessoa (D5). A cadeia não muda (fora do
  escopo); o `--dry-run` passa a dizer isso antes, e a skill diz ao aluno antes do OK. Integrado em AT-006.
- [x] (integrações) **Prova sem gastar (P6):** a API oficial tem `GET /api/v1/key` (rótulo, limite, o que resta do
  limite, uso, `is_free_tier`), conferida em https://openrouter.ai/docs/api-reference/limits em 2026-11-18; o saldo
  (`GET /api/v1/credits`) exige chave de gestão, que o aluno não tem (https://openrouter.ai/docs/api-reference/get-credits,
  2026-11-18). Logo, "sem crédito" sai de `is_free_tier` (nunca pôs crédito) e do 402 da revisão real, nunca do saldo.
  A lista de modelos (`GET /api/v1/models`) é pública e não cobra. O Design confirma os campos e se a consulta da
  chave cobra. Integrado em AT-003.
- [x] (UX) **`--dry-run` sem diff:** a frente recém-aberta não tem diff, e o `--dry-run` de hoje sai 64 ("está
  vazio") antes do plano; a prova do fim da skill falharia justamente no caso do aluno. O `--dry-run` passa a mostrar
  o plano das engines com `diff: vazio` e sair 0; a revisão real sem diff continua 64. Não afrouxa nada: o
  `--dry-run` não chama engine. Integrado em AT-006.
- [x] (A4) Slots cheios e chave ausente: só os passos da chave. Chave presente e slots vazios: a escolha dos
  modelos, salvo com 2 ou mais CLIs instaladas, quando a opção sem custo extra vem primeiro (revisão D2, R4). Slot do time (no `sdd/config.yaml`) com CLI ausente: instalar a CLI ou falar com quem cuida do projeto
  (o `git config` não vence o slot). Integrado em AT-004 e na tabela.
- [x] (A5) O aviso entra no `checar.sh` (modo normal), como ⚠️ e nunca 🔴, só em projeto com
  `sdd/bin/adversarial-review.sh`; o diagnóstico completo fica no script da skill. Motivo: quem roda o `checar`
  descobre a skill; o starter, sem a revisão, não ouve aviso. Integrado em AT-009.
- [x] (A1) **Onde o aluno grava a chave:** macOS (zsh) no `~/.zshrc`; Linux e WSL (bash) no `~/.bashrc`; Windows
  com Git Bash nas variáveis de ambiente do usuário do Windows (a janela "Variáveis de ambiente"), que o Git Bash e as
  extensões do editor herdam; o WSL não herda as do Windows. A gravação no perfil é por um comando que lê a chave sem
  mostrá-la (o valor não vai para a tela nem para o histórico). Herança: o agente aberto pelo terminal herda o
  ambiente do terminal em que foi aberto (fechar e abrir num terminal novo); a extensão do editor herda o ambiente do
  editor (fechar o editor por completo e abrir). O Design confere na documentação oficial como cada editor monta o
  ambiente e diz no DESIGN o que foi testado e o que não foi.
- [x] (restrições) O par sugerido sai das linhas `openrouter` do `precos.tsv` (dois modelos diferentes, o padrão do
  registry entre eles); o Build confere preço e existência na lista pública (`/api/v1/models`) e atualiza a data;
  modelo novo entra no `precos.tsv` com a URL e a data (P4).
- [x] (restrições) A skill não entra no starter: o starter não tem `sdd/bin/adversarial-review.sh` (o Design
  confere); o aviso do `checar.sh` não aparece lá (AT-009).
- [x] (sinal de conclusão) A skill termina com a prova: chave aceita (quando OpenRouter), os valores lidos de volta
  do `git config` e o plano do `--dry-run`; só então diz que está pronto.
- [x] (terminologia) "Engine" = o modelo de IA que revisa ou audita, com a CLI ou o serviço que o roda; "revisor" lê
  o diff e aponta problemas; "auditor" é outra engine que confere a revisão; "perfil do terminal" = o arquivo que o
  terminal lê ao abrir (`~/.zshrc`, `~/.bashrc`).
- [x] (restrições) Verify Gate: depois da F26, o `git archive` já exclui os documentos da frente
  (`sdd/** export-ignore`); o comando não precisa apagar pastas.

### Segurança

- [x] (segurança) Stack do repositório: nenhuma; valem os itens de stack `todas`. Gatilhos pelo sentido: `ia` (a
  revisão manda código a um modelo pago; o script lê respostas da API), `dado-de-terceiros` (a chave é segredo do
  aluno; o diff e os documentos saem do computador).
- [x] (segurança) S10 Senha ou segredo guardado errado — aplicado (recomendação aceita como padrão): a chave mora
  só no ambiente/perfil do aluno, nunca no projeto, em argumento ou em log; integrado em AT-002.
- [x] (segurança) S20 Agente com poder demais e sem teto — aplicado: o passo a passo põe limite de gasto na chave e
  o diagnóstico avisa quando a chave não tem limite; integrado em AT-003 e na tabela.
- [x] (segurança) S18 Instrução escondida em conteúdo externo e S17 Log que aceita linha forjada — aplicados: o
  diagnóstico nunca imprime texto vindo da resposta da API (rótulo da chave, mensagem de erro), só a classe e
  números; integrado em AT-003.
- [x] (segurança) S11 Chave secreta no código — já coberto pela varredura de toda release e pelo AT-002 (fixture de
  chave que não parece chave real).

### Session 2026-11-18 (governança)

- [x] (governança) revisor fresco: REVISADO, 1 lacuna, 1 item na 2ª camada, 18 N.A.; padrão do projeto usado; fronteira conferida (só o relatório mudou).
- [x] (governança) G09 Aritmética exata — aplicada (recomendação aceita como padrão, pedido do Roberto): valores em dólar como decimal exato, truncados em centavos, "esgotado" = o que resta ≤ 0; integrada em AT-003 e numa sabotagem nova.
- [x] (governança) G16 Certificado digital e segredos (2ª camada) — risco aceito: a chave fica em claro no perfil do terminal ou nas variáveis do Windows (o cofre do sistema está fora do escopo). Mitigação sem AT: o passo a passo da chave avisa, em 1 frase, para não guardar o perfil em pasta sincronizada nem em repositório de dotfiles publicado, e para usar o limite de gasto (S20).

---

## Verify Gate

```yaml
verify_gate:
  kind: test
  cmd: "T=$(mktemp -d) && git archive HEAD | tar -x -C $T && PUBLISH_GATE_MODE=ci bash scripts/publish-gate.sh $T && cd $T && SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover -s tests -p 'test_*.py'"
  pass_when: "exit 0"
  threshold: "—"
  manual_fallback: "—"
```

Cobertura: AT-001 a AT-004 e AT-007 no teste novo da skill (projetos git temporários, PATH com CLIs falsas,
`HOME` temporário com perfis sintéticos, servidor HTTP local no lugar do OpenRouter que registra cada chamada, a
tabela de estados do `SKILL.md` comparada com os estados do script); AT-005 e AT-006 no teste novo da revisão
(`git config` temporário, slots, flags, `--dry-run` sem diff, stubs de `sdd/review/stubs/`); AT-008 no teste de
textos da frente, em `tests/test_agnostico.py`, `tests/test_skill_lint.py` e `tests/test_gerar_starter.py`; AT-009
no `tests/test_checar.py`; AT-010 na suíte inteira (inclusive `tests/test_revisao.py`, `tests/test_revisao_gate.py`,
`tests/test_bash32.py`).

---

## Out of Scope

- Guardar a chave em arquivo do projeto, em cofre do sistema (Keychain, Credential Manager) ou passá-la pela conversa.
- Outros provedores além do OpenRouter; mudar preço, cadeia, prompts ou a regra de identidade da revisão.
- Slot ou flag novos para o 2º revisor e o desempate (um 3º modelo do OpenRouter): seria mudar a cadeia.
- Mexer nos slots `papeis:` (modelo por papel).
- Tornar a revisão dispensável sem motivo, ou afrouxar o `adversarial-review.sh` para a skill "passar".
- Chamada paga ao OpenRouter em teste ou na prova da skill; teste com chave real.
- Corrigir direto no starter; material de aula do repositório privado da RDD.

---

## Constraints

| Type | Constraint | Impact |
|---|---|---|
| Technical | bash 3.2 + Python 3.9 stdlib; script novo com a guarda `sdd_python_pronto` quando usar `sdd/bin/lib/python.sh`; chamado sempre com `bash` | `tests/test_bash32.py` |
| Segredo | a chave só no ambiente; teste de existência sem imprimir; nunca `ps`, `pgrep -fl` ou `env` cru; fixture de chave que não parece chave real | AT-002, publish-gate, varredura |
| Rede | nenhum teste chama o OpenRouter de verdade: servidor local e stubs; `--testar` só faz `GET` de leitura | AT-003 |
| Windows | teste que pergunta a plataforma usa as constantes de `tests/apoio.py` (LM-042); `subprocess` de teste com `encoding="utf-8"` (LM-014); a suíte passa no Git Bash com Python nativo | `tests/test_windows.py`, CI do PR |
| Agnóstico | texto novo sem ferramenta de um agente só | `tests/test_agnostico.py` |
| Público | nada do repositório privado da RDD (número medido, nome); número com 11+ dígitos barrado (LM-012) | `publish-gate.sh` |
| Pacote | arquivo novo do pacote no `MANIFEST.txt` no mesmo commit (LM-037); skill da lista do starter tocada ⇒ `test_gerar_starter.py` antes do gate (LM-035) | publish-gate, gerador |
| Skills | skill tocada sobe `metadata.version`; skill nova muda as contagens fixadas | `scripts/check-versions.py` |
| Processo | `git add` por caminho; suíte com `-B`; sabotagem só em cópia de `git archive`; identidade de git em teste só por `GIT_AUTHOR_*`/`GIT_COMMITTER_*` | build |

---

## Technical Context

| Aspect | Value | Notes |
|---|---|---|
| **Deployment Location** | `.agents/skills/sdd-configurar-revisores/` (nova); `sdd/bin/adversarial-review.sh`; `.agents/skills/sdd-checar-ambiente/scripts/checar.sh` e o `SKILL.md` dela; `.agents/skills/{sdd-design,sdd-build,sdd-release}/`; `sdd/review/precos.tsv` (data, se o Build conferir); `sdd/config.example.yaml` (comentário do bloco `review:`); `docs/`, `docs/pt-BR/`, `README.md`, `README.pt-BR.md`, `MANIFEST.txt`; `tests/` | produto do Open |
| **KB Domains** | nenhum | o Open não tem `sdd/kb/` |
| **IaC Impact** | None | — |
| **LLM Prompts** | false | nenhum prompt de produção criado ou editado; OpenRouter e modelos aparecem como engine que o aluno configura, e os prompts da revisão não mudam (fora do escopo) |
| **CONTEXTO de domínio** | nenhum (pulado: sem `sdd/patterns/dominio.md`) | `contexto-lint.sh --sugerir` → PULAR |
| **Governança** | GOVERNANCA_REVIEW_F28_REVISORES_OPENROUTER.md · 1 aplicada (G09) · 0 recusadas · 0 adiadas | 2026-11-18 |
| **Segurança** | 4 aplicados (S10, S17, S18, S20) · 0 recusados · 0 adiados | 2026-11-18 |
| **Desempenho** | N.A. — a frente não tem banco (nenhuma tabela, migration ou consulta) | 2026-11-18 |

---

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|---|---|---|---|
| A-001 | `GET /api/v1/key` não cobra crédito | a prova "sem gastar" teria custo; o Design confirma na documentação e, se cobrar, a prova fica só no `--dry-run` e na lista pública de modelos | [ ] |
| A-002 | Extensões de editor da família VS Code, abertas pelo ícone, herdam o ambiente do perfil do terminal no macOS e no Linux | a parada "feche e abra o editor" não basta; o Design confere na documentação oficial e, se preciso, manda abrir o editor pelo terminal | [ ] |
| A-003 | O Git Bash herda as variáveis de usuário do Windows | o passo a passo do Windows muda para o perfil do Git Bash; o Design confere na documentação do Git for Windows | [ ] |
| A-004 | O starter não tem a revisão adversarial | a skill teria de ir ao starter; o Design confere em `scripts/starter/` | [ ] |
| A-005 | Os 2 modelos do `precos.tsv` continuam na lista pública do OpenRouter | o par sugerido muda; o Build confere e atualiza o `precos.tsv` com a URL e a data | [ ] |

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---|---|---|
| Problem | 3 | o caminho do aluno quebra em pontos nomeados (slots vazios, exit 64, pergunta sobre "engines", dispensa) |
| Users | 3 | 6 papéis, inclusive o que voltou, o do Windows e o que não quer pagar |
| Goals | 3 | MUST/SHOULD/COULD |
| Success | 3 | contagens, sabotagens e cenários nomeados |
| Scope | 2 | skill nova + mudança no `adversarial-review.sh` e no `checar.sh` + 3 skills de fase + docs numa frente |
| **Total** | **14/15** | |

---

## Open Questions

None - ready for UX Review.

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | 2026-11-18 | define-agent | Initial version |
| 1.2 | 2026-11-18 | design-agent | Revisão do DESIGN D2: A4 com as CLIs primeiro (R4); AT-001 compara os estados `script` e exige situação e passo nos de `conversa`; "uma engine só" não é gravada |
| 1.1 | 2026-11-18 | define-agent | Governança: G09 aplicada em AT-003 (decimal exato, ≤ 0 em centavos) e numa sabotagem; G16 risco aceito; AT-009 sem a tabela de tradução que o modo normal não tem |

---

## Next Step

**Ready for:** `/sdd-ux-review sdd/features/DEFINE_F28_REVISORES_OPENROUTER.md` — há interface: a conversa com o
aluno e a saída do script.
