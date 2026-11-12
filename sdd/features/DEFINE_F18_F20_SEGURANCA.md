# DEFINE: F18 + F20 — segurança embutida no fluxo (alerta) e ações preventivas (prevenção)

> Um catálogo próprio de 22 falhas de segurança de app feito com IA, com marca de stack e fase, alimenta ao mesmo tempo a prevenção (regras que o agente lê ao construir) e o alerta (perguntas no Brainstorm e no Define, seção no Design, varredura em toda publicação, com só 2 bloqueios), mais o modo incidente.

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | F18_F20_SEGURANCA |
| **Date** | 2026-11-11 |
| **Author** | define-agent (worktree `sdd-open-f18-f20-seguranca`; branch `feat/f18-f20-seguranca`, de `origin/main` `69b7f6b` = `v2.11.0`) |
| **Status** | Ready for Design |
| **Clarity Score** | 14/15 |
| **Entrada** | `sdd/features/BRAINSTORM_F18_F20_SEGURANCA.md` (abordagem A: catálogo estruturado único) |

---

## Problem Statement

O aluno que constrói com IA publica, sem saber, as falhas de segurança mais comuns de app gerado por IA (tabela sem RLS, chave no código, CORS aberto, HTML cru vindo do usuário, cabeçalhos ausentes), porque nenhuma fase do SDD Open pergunta por elas, previne ao construir ou confere antes de publicar: a passada 0c da `sdd-release` (`SKILL.md:155`) só roda quando o diff toca autenticação ou dados e não tem lista; CORS, cabeçalhos, XSS, injeção de SQL, prompt injection, source map e GraphQL têm zero menções em `.agents/skills/`; e o `AGENTS.md` gerado pelo `init` não traz nenhuma regra de segurança.

---

## Target Users

| User | Role | Pain Point |
|---|---|---|
| Aluno iniciante que constrói com Supabase, Vercel e um agente de código | percorre o fluxo e publica com a `sdd-release` | não sabe o nome das trancas nem que vêm desligadas; descobre no incidente |
| Aluno que usa o agente na web (claude.ai, ChatGPT), sem terminal | lê as skills e confere à mão | não roda script: precisa de cada item na forma "confira à mão" |
| Aluno sem Supabase nem Vercel (um script, uma CLI) | usa o mesmo pacote | aviso de stack que ele não tem é ruído que ensina a ignorar o aviso seguinte |
| Mantenedor do Open | mantém o pacote público e agnóstico | alerta e prevenção não podem divergir; nada da RDD no pacote |

---

## Goals

| Priority | Goal |
|---|---|
| **MUST** | skill nova `sdd-seguranca` 1.0.0 (21ª): catálogo S01–S22 em `references/CATALOGO_SEGURANCA.md` (fichas com campos fixos), modos Define, checklist antes de publicar, app publicado e incidente |
| **MUST** | `sdd/bin/seguranca-varredura.sh`: só leitura, sem rede, padrões lidos do catálogo, stack, teto, dispensa, 2 bloqueios só no que a publicação acrescenta |
| **MUST** | `sdd-release`: varredura no 0a de toda publicação (2 ⇒ NON_WAIVABLE, 1 ⇒ CONCERNS); 0c sempre, com a lista fixa do catálogo (os itens da stack, menos os da bancada: até 20), os de maior risco primeiro; fecho aponta o app publicado e o incidente |
| **MUST** | `AGENTS.md` do `init`/`sync`: 5 regras + 1 ponteiro, filtradas pela stack |
| **MUST** | `sdd-brainstorm` (3 perguntas → perfil de risco), `sdd-define` (passo de segurança), `sdd-design` (seção "Segurança" no template e no lint, com aviso), `sdd-build` (lê as regras da stack; BUILD_REPORT com os recusados e adiados) |
| **MUST** | slots `security.stack` e `security.max_warnings` em `sdd/config.example.yaml` |
| **MUST** | texto próprio: nenhum texto, prompt ou citação do material de origem; referência pública (OWASP/CWE) |
| **SHOULD** | cenários de comportamento da `sdd-seguranca` executados em contexto novo (LM-011) |
| **COULD** | varredura do app publicado pela rede (fica fora: YAGNI) |

---

## Success Criteria

- [ ] Caso com segredo literal acrescentado ⇒ `seguranca-varredura.sh` sai 2 com `arquivo:linha`; caso com migração nova sem `enable row level security`, com Supabase ⇒ sai 2.
- [ ] Os mesmos achados só em linha que já existia na base ⇒ aviso "já existia", saída 1.
- [ ] 7 padrões de aviso (`select('*')`, HTML cru, `eval(`/`new Function(`, CORS `*`, `security definer` sem `revoke`, `getPublicUrl(`, source map em produção) ⇒ saída 1, cada aviso com id, gravidade, `arquivo:linha` e a prova "confira à mão"; cada padrão tem um par que não acusa.
- [ ] Projeto sem Supabase ⇒ zero aviso e zero regra de Supabase (varredura e `AGENTS.md`).
- [ ] 8 avisos com `max_warnings: 5` ⇒ 5 na tela, os mais graves, e "e mais 3"; a lista inteira no arquivo de `--saida`.
- [ ] Dispensa com motivo ⇒ o achado sai e aparece uma vez como aceito; dispensa sem motivo não vale.
- [ ] `AGENTS.md` gerado pelo `init` num projeto com Supabase traz as 5 regras; sem nenhuma stack, só a regra de todas as stacks e o ponteiro; acréscimo ≤ 2 KB.
- [ ] Cenários de comportamento da `sdd-seguranca`: 2 cenários × 3 execuções em contexto novo, critério escrito antes, as 3 aprovadas em cada.
- [ ] Linha de base vermelha: os testes novos falham em `69b7f6b` (`v2.11.0`).
- [ ] Sabotagens: ao menos 5 mutantes (bloqueio vira aviso; stack ignorada; dispensa sem motivo aceita; teto ignorado; regra de Supabase sem Supabase no `AGENTS.md`) derrubam, cada um, um teste nomeado.
- [ ] Verify Gate numa cópia de `git archive` sai 0, com a suíte inteira (a contagem só sobe a partir de 1.944, medida em `62f0b8c`).
- [ ] Release publicada com `SHA256SUMS.txt` conferido; o tempo dos jobs do CI conferido contra os tetos antes da tag.

---

## Acceptance Tests

| ID | Padrão | Critério (EARS) | Gate (`kind`) |
|---|---|---|---|
| AT-001 | Unwanted | **When** `sdd/bin/seguranca-varredura.sh` roda num repositório git, com a base `origin/<project.default_branch>` (ou `--base <ref>`), o script **shall** tratar como **acrescentada** cada linha que o diff da árvore de trabalho contra a base introduz; **if** uma linha acrescentada traz segredo literal (cabeçalho `-----BEGIN … PRIVATE KEY-----` seguido do corpo da chave, 40 ou mais caracteres base64 na mesma linha ou na seguinte; ou valor com os prefixos `sk-`, `sk_live_`, `ghp_`, `github_pat_`, `AKIA` seguido do corpo de chave, ou chave de serviço do Supabase atribuída com valor), **then** **shall** sair 2 com a linha `🛑 S11 <gravidade> <arquivo>:<linha>`, em qualquer caminho do repositório (inclusive `sdd/` e as pastas dos agentes), menos `node_modules/` e o próprio catálogo, e a prova "confira à mão" do item; **if** o mesmo achado está só em linha que já existia na base, **then** **shall** contá-lo como aviso "já existia", nunca como bloqueio; uma variável de ambiente lida pelo nome (`process.env.X`, `Deno.env.get("X")`, `os.environ["X"]`) **shall** não ser segredo; **if** a base não existe (sem remoto, sem a branch), **then** **shall** contar toda linha rastreada como acrescentada e dizer isso numa linha; o valor do segredo **shall** nunca aparecer na saída | test |
| AT-002 | Unwanted | **Where** a stack inclui Supabase, **if** uma migração acrescentada (arquivo `.sql` sob `supabase/migrations/` ou sob a camada `sql` de `layers:`) cria uma tabela com `create table` e nenhuma migração da árvore tem `enable row level security` para essa tabela, **then** a varredura **shall** sair 2 com `🛑 S01 <gravidade> <arquivo>:<linha do create table>`; **where** a stack não inclui Supabase, **shall** não avaliar S01 | test |
| AT-003 | Event-driven | **When** a varredura acha, nos arquivos de cada ficha, `select('*')`/`select("*")` no código (S02), `security definer` numa migração sem `revoke … from anon` no mesmo arquivo (S03; `from public` não basta, porque o papel anônimo tem grant próprio), `getPublicUrl(` (S04), `dangerouslySetInnerHTML`, `v-html` ou `.innerHTML =` (S12), `Access-Control-Allow-Origin` com valor `*` (S14), `productionBrowserSourceMaps: true` ou `sourcemap: true` em configuração de build (S15), `eval(` ou `new Function(` (S16), ela **shall** sair 1 (CONCERNS) e imprimir, por achado, `⚠️ <id> <gravidade> <arquivo>:<linha>`, e a prova "confira à mão" uma vez por item; cada padrão **shall** ter um caso que não acusa (ex.: `select('id, nome')`, CORS com origem fixa, `JSON.parse(`, comentário de documentação); sem achado, **shall** sair 0 com `RESULTADO: NADA ACHADO` | test |
| AT-004 | Unwanted | **If** a varredura acha mais avisos que `security.max_warnings` (vazio = 5), **then** **shall** mostrar os N mais graves (gravidade alta antes de média antes de baixa; empate pela ordem do id) e a linha `… e mais K aviso(s): lista inteira em <arquivo>`; os bloqueios **shall** aparecer sempre e não contar no teto; **when** recebe `--saida <arquivo>`, **shall** gravar a lista inteira (bloqueios, avisos, aceitos, "já existia") nesse arquivo | test |
| AT-005 | Unwanted | **Where** a linha do achado, ou a linha imediatamente acima, traz `sdd-seguranca: aceito S<nn> — <motivo>` com o id do achado e motivo não vazio, a varredura **shall** tirar o achado do bloqueio e do aviso e listá-lo uma vez como `✔ aceito S<nn> <arquivo>:<linha> — <motivo>`; **if** o motivo está vazio ou o id não casa, **then** **shall** manter o achado e acrescentar o aviso `dispensa sem motivo (ou de outro item) não vale` | test |
| AT-006 | State-driven | **While** o slot `security.stack` está vazio, a stack **shall** ser detectada pelo projeto: `supabase` com a pasta `supabase/` ou `@supabase/` no `package.json`; `vercel` com `vercel.json`, a pasta `.vercel/` ou `vercel` no `package.json`; `web` com `package.json` ou um `.html` rastreado; **while** o slot está preenchido, ele **shall** passar por cima (lista separada por vírgula; `nenhuma` = só os itens de stack `todas`); um item **shall** só disparar (varredura, regra do `AGENTS.md`, lista do Define e do release) quando a stack dele é `todas` ou está na stack do projeto; `--stack` **shall** imprimir a stack e a origem (detectada ou slot) | test |
| AT-007 | Event-driven | **When** `init` ou `sync` geram o bloco do SDD Open no `AGENTS.md`, o marcador do `AGENTS.md.tmpl` **shall** virar as regras do catálogo marcadas `agents=sim` cuja stack o projeto tem (no máximo 5) e uma linha que manda ler, antes de construir, as regras da stack na `sdd-seguranca` (`seguranca-varredura.sh --regras`); **when** a stack muda, `sync --check` **shall** acusar o bloco divergente e `sync` **shall** reescrevê-lo; o acréscimo **shall** ser ≤ 2 KB; sem o catálogo instalado, **shall** escrever só o ponteiro e seguir | test |
| AT-008 | Event-driven | **When** os testes leem `references/CATALOGO_SEGURANCA.md`, o catálogo **shall** ter exatamente 22 itens S01–S22, cada um com o título (id e falha) e os campos stack, fase, gravidade, bloqueia, `agents`, gatilho, padrão (ou `só à mão`), arquivos, frase preventiva, como evitar, AT modelo, confira à mão e referência pública, na ordem da gramática do DESIGN (Decision 1); `bloqueia=sim` **shall** valer só para S01 e S11; todo padrão **shall** ter caso que acusa e caso que não acusa nos testes; nenhum arquivo do pacote **shall** citar o material de origem nem nome da RDD fora dos já existentes | test |
| AT-009 | Event-driven | **When** as skills de fase rodam, os textos **shall** dizer: `sdd-brainstorm` — as perguntas quem pode ver, quem pode mudar e quanto alguém pode pedir, gravadas como perfil de risco de 3 linhas; `sdd-define` — um passo que chama a `sdd-seguranca` e grava a linha `\| **Segurança** \| … \|` no Technical Context (N.A. em 1 linha sem gatilho; com gatilho, ATs em EARS com teste negativo, aplicar, recusar com motivo ou adiar, até 5 por vez), rodado pela própria sessão do Define e sem trava no gate; `sdd-design` — a seção `## Segurança` no template, com o "como evitar" de cada item aceito como decisão, e o `design-lint.py` avisando (sem reprovar) DESIGN sem a seção quando o DEFINE tem item aceito; `sdd-build` — o passo de execução lê `seguranca-varredura.sh --regras` antes de escrever código e o BUILD_REPORT lista uma vez, numa tabela, os itens recusados e os adiados, com o motivo; `sdd-release` — a varredura no 0a de toda publicação (2 ⇒ NON_WAIVABLE com `arquivo:linha`; 1 ⇒ CONCERNS), a 0c em toda publicação com a lista fixa do catálogo (os de maior risco da stack primeiro) e o fecho apontando o "confira no app publicado" e o modo incidente; a `sdd-seguranca` **shall** ter os modos Define, checklist, app publicado e incidente, cada item com a forma "confira à mão"; todo texto novo **shall** passar no `tests/test_agnostico.py` e no `skill-lint.py --conversa` | test |
| AT-010 | Non-regression | O `checar.sh --segredo` e o `doctor` **shall continue to** acusar os mesmos arquivos; a `sdd-governanca` **shall continue to** disparar só pelos gatilhos dela; a `sdd-release` **shall continue to** pedir um OK só; o `verify-gate.sh` **shall continue to** ler só a linha `Governança` como trava; a suíte **shall continue to** passar no bash 3.2 do macOS (`SDD_TEST_BASH=/bin/bash`); as contagens fixadas (skills, versões, perguntas do `sdd-decisoes-lint`) **shall** mudar só pelo que esta frente acrescenta | test |

Considerados: **While** em AT-006 (o estado do slot `security.stack` decide a origem da stack). **If/Then** em AT-001 (segredo; achado que já existia), AT-002 (tabela sem RLS), AT-004 (acima do teto) e AT-005 (dispensa inválida). **Where** em AT-002 (stack com e sem Supabase) e AT-005 (linha com dispensa). Não-regressão em AT-010, porque a frente mexe em 5 skills de fase, no `init`/`sync` e na `sdd-release`.

O comportamento da `sdd-seguranca` diante de um DEFINE real (N.A. sem gatilho; com gatilho, propor sem decidir pelo aluno) não é AT do gate local: é critério com evidência, executado em contexto novo: 2 cenários × 3 execuções (sem gatilho ⇒ N.A. em 1 linha; DEFINE com login e Supabase ⇒ propõe ATs sem decidir pelo aluno), com o critério de aprovado escrito antes (LM-011).

---

## Clarifications

### Session 2026-11-11

- [x] (escopo) F18 ondas 1–3 + F20 entregas 1–5 numa sessão; starter pela F17 (brainstorm, decisão 2).
- [x] (terminologia) Sem citar o material de origem; texto próprio e referência pública (brainstorm, decisão 1).
- [x] (restrições) 2 bloqueios para toda tabela nova; bloqueio só no acrescentado; dispensa com motivo na linha (decisões 4 a 6).
- [x] (NFR) teto de 5 avisos por fase; lista inteira em arquivo (decisão 7).
- [x] (UX) Sem interface: texto de skill e saída de terminal no padrão de `docs/cli-conventions.md`. UX review pulado.
- [x] (integrações) A revisão de segurança do Define é feita pela própria sessão, sem trava no gate: o alerta não bloqueia e a seleção é mecânica (gatilho + stack + fase); integrado em AT-009 e AT-010.
- [x] (dados) Base da varredura: `origin/<project.default_branch>`; sem ela, toda linha conta como acrescentada e a saída diz isso; integrado em AT-001.
- [x] (sinal de conclusão) Itens adiados vão para o BUILD_REPORT com os recusados; integrado em AT-009.
- [x] (sinal de conclusão) Cenários de comportamento: 2 × 3 execuções em contexto novo; integrado no parágrafo abaixo dos ATs e nos critérios de sucesso.

### Session 2026-11-11 (governança)

- [x] (governança) N.A. — o revisor fresco leu o DEFINE pelo sentido: "valor" é valor de segredo ou de cabeçalho, "quanto alguém pode pedir" é limite de requisições, "dado pessoal" só no fora de escopo. 1ª tentativa contada como falha: a fronteira acusou `sdd/traces/F18_F20_SEGURANCA.jsonl`, gravado pelo `verify-gate.sh` que a sessão do Define rodou 1 s depois da foto de antes (não pelo revisor); 2ª tentativa com foto nova: só o permitido mudou, nenhum arquivo gravado.

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

Cobertura: AT-001 a AT-006 no teste da varredura (repositórios git temporários com base e diff, casos que acusam e que não acusam, chaves falsas montadas em tempo de execução); AT-007 em `tests/test_sdd_open.py` (`init` e `sync` com e sem Supabase, tamanho, `sync --check`); AT-008 no teste do catálogo (forma, bloqueios, cobertura de padrões) e no teste de texto que varre o pacote; AT-009 no teste de textos da frente, `tests/test_agnostico.py`, `tests/test_skill_lint.py` e `tests/test_design_lint.py`; AT-010 na suíte inteira.

---

## Out of Scope

- Starter (`sdd-starter`): recebe pela F17.
- Texto, prompt, checklist ou citação do material de origem.
- Ferramentas e repositório da RDD (inclusive a linha do mentor de appsec do plano).
- Varredura do app publicado pela rede.
- Detectar dado pessoal pelo nome da coluna.
- Padrão de varredura para log injection, desserialização, JWT, pacote inventado, IDOR, injeção de SQL, limite de tentativas e cadastro aberto (ficam "só à mão").
- Mudar o `verify-gate.sh` ou a trava da governança.

---

## Constraints

| Type | Constraint | Impact |
|---|---|---|
| Technical | bash 3.2 + Python stdlib; script novo de `sdd/bin` lê `sdd/bin/lib/python.sh` com a guarda `sdd_python_pronto`; `sdd/bin/*.sh` sempre com `bash` | `tests/test_bash32.py`, `tests/test_python_resolver.py` |
| Technical | a varredura só lê e nunca usa rede | AT-001 a AT-006 |
| Agnóstico | texto novo sem nome de ferramenta de um agente só; cada item com "confira à mão" | `tests/test_agnostico.py` |
| Público | repositório público: nada da RDD; chave falsa dos testes montada em tempo de execução (o pacote não carrega texto com forma de segredo); número com 11 dígitos barrado (LM-012) | `publish-gate.sh` |
| Contexto | o `AGENTS.md` gerado continua abaixo do `project.context_file_max_kb` | AT-007 |
| Skills | skill tocada sobe `metadata.version`; skill nova muda as contagens fixadas | `scripts/check-versions.py --base v2.11.0` |
| CI | o teto de cada job é olhado antes da tag (Ubuntu 45, macOS 75, Windows 30 min) | release |
| Processo | `git add` por caminho; suíte com `-B`; sabotagem só em cópia de `git archive` (LM-009) | build |

---

## Technical Context

| Aspect | Value | Notes |
|---|---|---|
| **Deployment Location** | `.agents/skills/sdd-seguranca/` (nova), `.agents/skills/{sdd-brainstorm,sdd-define,sdd-design,sdd-build,sdd-release}/`, `sdd/bin/seguranca-varredura.sh`, `sdd/bin/design-lint.py`, `sdd/templates/` (BRAINSTORM, DESIGN, BUILD_REPORT), `sdd/config.example.yaml`, `AGENTS.md.tmpl`, `bin/sdd-open.sh`, `README.md`, `README.pt-BR.md`, `docs/`, `tests/`, `MANIFEST.txt` | produto do Open |
| **KB Domains** | nenhum | o Open não tem `sdd/kb/`; a skill `sdd-kb` cria uma base quando o projeto quiser |
| **IaC Impact** | None | — |
| **LLM Prompts** | false | nenhum prompt de produção; "prompt injection" e "chamada a IA" aparecem como **tema** do catálogo, não como código do pacote |
| **CONTEXTO de domínio** | nenhum (pulado: o Open não tem `sdd/patterns/dominio.md`) | `contexto-lint.sh --sugerir` → PULAR |
| **Governança** | N.A. — skill de segurança, varredura só leitura e textos de fase; sem dinheiro, saldo, lançamento, nota fiscal, tributo, folha nem dado pessoal ("dado pessoal" só no fora de escopo) | revisor fresco, 2026-11-11 |

---

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|---|---|---|---|
| A-001 | Os 7 padrões de aviso acham o caso comum por texto sem falso positivo frequente | o aluno aprende a ignorar o aviso; cada padrão tem o par negativo, e o falso positivo real é medido em uso | [ ] |
| A-002 | `create table` + `enable row level security` por nome de tabela cobre as migrações do Supabase (com e sem `public.` e aspas) | tabela com nome escrito diferente escapa ou bloqueia sem motivo; o Design fixa a normalização | [ ] |
| A-003 | O `init` consegue ler o catálogo da skill no pacote ao gerar o `AGENTS.md` | o bloco sai só com o ponteiro (AT-007 cobre o caso) | [ ] |

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---|---|---|
| Problem | 3 | lacunas medidas com arquivo e linha |
| Users | 3 | 4 papéis, inclusive o sem stack e o da web |
| Goals | 3 | MUST/SHOULD/COULD |
| Success | 3 | casos, sabotagens e cenários nomeados, com números |
| Scope | 2 | escopo grande (5 skills de fase + skill nova) numa sessão |
| **Total** | **14/15** | |

---

## Open Questions

None - ready for Design.

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | 2026-11-11 | define-agent | Initial version |
| 1.4 | 2026-11-11 | build | Avaliador, ciclo 2: AT-002 cita a gravidade na linha do bloqueio (B1); AT-003 diz que a prova à mão sai uma vez por item |
| 1.3 | 2026-11-11 | build | Avaliador, ciclo 1: AT-001 diz a gravidade na linha do bloqueio (A4) e que a chave é procurada também em `sdd/` e nas pastas dos agentes (A1) |
| 1.2 | 2026-11-11 | design-agent | Revisão do DESIGN, rodada 1: AT-003 tira o "fora de migração" (S03 vive nas migrações) e exige `revoke … from anon` (R6, R10); Goals sem "tabela rígida" e com a lista do catálogo no lugar de "20 itens fixos" (R11, R12) |
| 1.1 | 2026-11-11 | design-agent | DESIGN, Decision 1: o catálogo vira fichas por item com campos fixos (legível na web, sem escapar `\|`); AT-008 diz "22 itens" e lista os 13 campos |

---

## Next Step

**Ready for:** `/sdd-design sdd/features/DEFINE_F18_F20_SEGURANCA.md` — UX review pulado: a feature não tem interface (texto de skill, scripts de terminal).
