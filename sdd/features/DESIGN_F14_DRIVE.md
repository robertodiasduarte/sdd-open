# DESIGN: F14 Drive e orquestração

> Technical design for implementing F14 Drive e orquestração

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | F14_DRIVE |
| **Date** | 2026-11-05 |
| **Author** | SDD Design by RDD |
| **BRAINSTORM** | `sdd/features/BRAINSTORM_F14_DRIVE.md` |
| **DEFINE** | `sdd/features/DEFINE_F14_DRIVE.md` (v1.9) |
| **UX REVIEW** | `sdd/reviews/UX_REVIEW_F14_DRIVE.md` (U1–U16) |
| **LLM Prompts** | false |
| **Status** | Ready for Build |

---

## Architecture Overview

```text
                 /sdd-drive <DEFINE> (o agente lê .agents/skills/sdd-drive/SKILL.md)
                                   │
                                   ▼
   iniciar · --dry-run · --resume · proximo · verificar [--fundo] · concluir · bloqueio · aguardar · recibo
                                   │
                    ┌──────────────┴───────────────┐
                    │        sdd/bin/sdd-drive.sh  │  bash 3.2 + núcleo Python 3.9 stdlib
                    │  estado em disco · 12 motivos│
                    └──┬─────────┬──────────┬──────┘
       verify-gate.sh  │         │          │ sdd-fluxo.sh seguir design … build --drive
       --print/--checar│         │          │ sdd-fluxo.sh despachar executor-drive (exit 40)
       e o gate real   ▼         ▼          ▼
         sdd/reports/progress/DRIVE_<F>.json     report-lint.py (no concluir)
         sdd/reports/progress/PROGRESS_<F>.md · DRIVE_<F>.lock
         sdd/reports/evidence/<F>/DRIVE-gate-r<k>.log
         sdd/reports/DRIVE_REPORT_<F>.md
                                   │
              ACAO: ESPERAR · DESIGN · REVISAO_DESIGN · RODADA · CORRIGIR · COMMITAR · VERIFICAR · AVALIAR_E_RELATAR
                                   │  o agente executa, com contexto fresco por tarefa
                                   ▼
                   ⛔ barreira: nenhum verbo publica. Publicar = sdd-release, com o OK da pessoa.

 sdd-release (delta)
   0b  → references/raio-de-impacto.md (1 agente fresco por superfície; sequencial sem subagente)
   10  → sdd/bin/deploy-do-sha.sh (gh run + git merge-base; redisparo único, nunca rerun)
   11  → regra do conflito de changelog · 15b → sdd/bin/sdd-archive.py para o passivo
```

---

## Components

| Component | Responsibility | Technology | Inputs | Outputs | Dependencies |
|---|---|---|---|---|---|
| `sdd-drive.sh` | decide a próxima ação, roda o gate, conta rodadas, grava estado e relatório | bash 3.2 + Python stdlib embutido | DEFINE, DESIGN, PROGRESS, estado, slot `drive.max_rounds` | `ACAO:` ou `motivo:`, exit, estado, DRIVE_REPORT | `verify-gate.sh`, `sdd-fluxo.sh`, `report-lint.py`, git |
| Skill `sdd-drive` | mapeia cada `ACAO:` para quem executa, faz as 2 perguntas, cuida da conversa | Markdown | saída do script | despachos, perguntas | escada de `contexto-fresco.md` |
| Brief `executor.md` | 1 tarefa por sessão fresca, commit atômico, PROGRESS | Markdown | DEFINE, DESIGN, PROGRESS | bloco `<<<RODADA` | modo ralph |
| `verify-gate.sh --checar` | confere marcador, Governança e bloco sem rodar o `cmd` | bash | DEFINE | exit 0/5/64 | nenhum |
| `sdd-fluxo.sh seguir --drive` | reaproveita o juiz de design → build com o encadeamento off | Python embutido | DEFINE, DESIGN | exit 0/1/64 | `design-lint.py` |
| `deploy-do-sha.sh` | diz se o commit está no ar; redispara 1 vez | bash 3.2 + Python stdlib | SHA, workflow, slots `deploy.*` | frase, exit | `gh`, git |
| `sdd-archive.py` | faxina retroativa por lote | Python stdlib | árvore de `sdd/`, histórico do git | lista ou `git mv` staged | git |
| `raio-de-impacto.md` | brief do agente por superfície | Markdown | superfície, antes e depois | consumidores, invariantes, `arquivo:linha` | `sdd/invariants.md` |
| `avaliador-guard.sh` (delta) | aceita documento não rastreado | bash | `git status` | exit 0/1/2/64 | git |
| `playbook-curator.sh` (delta) | não conta eco de comando nem diagnóstico próprio | Python embutido | logs | linhas da colheita | nenhum |

---

## Key Decisions

### Decision 1: O script decide, o agente executa

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-11-05 |

**Context:** o driver do privado é um script da ferramenta `Workflow`, que só existe no Claude Code. O Roberto escolheu a abordagem A no brainstorm.

**Choice:** `sdd-drive.sh` nunca chama agente. Cada verbo lê o estado e o disco e imprime uma ação com exit 10, ou uma parada com `motivo:`. A skill executa a ação e chama o script de novo.

**Rationale:** a verdade fica em script (regra 1 do 8.0); roda nos 7 agentes; a decisão é testável sem modelo.

**Alternatives Rejected:**
1. Script chama o programa do agente - exige permissão de escrita sem confirmação e não tem onde fazer pergunta.
2. Só texto na skill - rodadas e barreira dependeriam de o agente obedecer.

**Consequences:**
- Sem subagente, uma parada por tarefa.
- O script é testável por inteiro, com gate e `report-lint` de mentira numa cópia.

---

### Decision 2: Verbos, exits e ações

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-11-05 |

**Context:** o DEFINE fixa os motivos; falta a superfície de comando.

**Choice:** verbos `iniciar`, `--dry-run`, `--resume [--max N] [--aceitar-gate-novo]`, `proximo`, `verificar`, `concluir`, `bloqueio <motivo>`, `aguardar <papel> <brief>`, `recibo <texto>`, `--self-test`, todos com `<DEFINE>` depois do verbo, menos o último. Exits: 0 concluído (`gate-verde`, `simulacao`), 10 continuar, 20 parada tabelada, 40 `aguardando-sessao`, 2 falha do próprio script (não consegue gravar, gate não executou), 64 uso. Ações: `ESPERAR`, `DESIGN`, `REVISAO_DESIGN`, `RODADA`, `CORRIGIR`, `COMMITAR`, `VERIFICAR`, `AVALIAR_E_RELATAR`. `verificar` aceita `--fundo`.

**Rationale:** mesmo vocabulário do `sdd-fluxo.sh` (`CONTINUAR` 10, `BLOQUEADO` 20, `AGUARDANDO_HUMANO` 40), que quem usa o método já leu.

**Alternatives Rejected:**
1. Um verbo só, com flags - mistura consulta e escrita.
2. Exit distinto por motivo - 12 códigos para quem só precisa ler a linha `motivo:`.

**Consequences:**
- O motivo vem em texto, numa linha própria, e a frase simples na seguinte.
- `RESULTADO:` usa `CONCLUIDO`, `CONTINUAR`, `PARADA`, `AGUARDANDO_HUMANO`, `FALHA`, `ERRO DE USO`.

---

### Decision 3: Estado em JSON, ações derivadas do disco

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-11-05 |

**Context:** `--resume` precisa continuar numa sessão sem memória; o estado não pode ficar mentindo se o agente fez a tarefa e a sessão caiu antes de avisar.

**Choice:** `DRIVE_<F>.json` guarda só o que o disco não diz: DEFINE, impressão digital e `cmd` do gate, commit inicial, limite, lista de gates (execução, rodada, commit, exit, log, impressão digital), trocas aceitas, recibos e o contador de repetição. Todo verbo, menos `iniciar`, `--dry-run` e `--resume --max`, para em `orcamento-rodadas` quando as rodadas usadas alcançam o limite (achado H1). A próxima ação é **sempre recalculada** do disco, nesta ordem:
1. gate rodando (trava viva) ⇒ `ESPERAR`;
2. sem DESIGN ⇒ `DESIGN`;
3. `seguir design … build --drive` sai 1 ⇒ `REVISAO_DESIGN` quando imprime o token `DRIVE_ACAO: REVISAO_DESIGN`, `DESIGN` com o motivo nos outros; sai 64 ⇒ exit 2;
4. `PROGRESS` com `- [ ]` ⇒ `RODADA`, com `tarefa: i de n — <arquivo>`; depois, algo fora dos documentos sem commit ⇒ `COMMITAR`;
5. último gate com a impressão digital atual, vermelho, e só documentos mudaram desde ele ⇒ `CORRIGIR`;
6. último gate com a impressão digital atual, verde, e só documentos mudaram desde ele ⇒ `AVALIAR_E_RELATAR`;
7. senão ⇒ `VERIFICAR`.
O gate grava o `HEAD` e a impressão digital de antes de começar: um commit ou uma troca aceita no meio não ganham esse verde. `concluir` só para em `gate-verde` quando esta ordem responderia `AVALIAR_E_RELATAR`. Gravação atômica (temporário + `os.replace`). Rodadas usadas = gates com exit 2; `k` = usadas + 1, limitado a N. "Só documentos" = `sdd/features/`, `sdd/reports/`, `sdd/reviews/`, `sdd/handoffs/`, `sdd/traces/`, a mesma lista para o que está sujo na árvore e para o `git diff` entre commits. O `PROGRESS` é semeado do manifest, e uma linha nova do manifest entra como `- [ ]` (L8).

**Rationale:** nada para sincronizar: uma sessão que caiu no meio volta certa, sem "marcar concluído".

**Alternatives Rejected:**
1. Máquina de estados com a fase gravada - a fase gravada diverge do disco na queda.
2. Registrar cada tarefa no estado - o `PROGRESS` já faz isso.

**Consequences:**
- O `PROGRESS` é o único registro das tarefas; sem `- [ ]` nem `- [x]`, `estado-invalido`.

---

### Decision 4: 1 rodada = passada + gate; repetição para na 3ª

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-11-05 |

**Context:** decisão D4 do Roberto: rodada é a passada inteira, sem teto de tarefas. Sem nenhum teto, uma tarefa que nunca marca `[x]` gira para sempre.

**Choice:** o contador de repetição guarda `ação + tarefa + HEAD + sha do DESIGN`. A 3ª resposta igual em `proximo` para com `bloqueio-humano`, nomeando a tarefa, o mesmo teto de `modos-e-retry.md`. `--resume` conta também, porque sem subagente toda volta passa por ele; só o `--resume` depois de `bloqueio-humano` zera. `verificar` sem nada além de documentos desde o último vermelho não roda o gate nem gasta rodada: `ACAO: CORRIGIR`. `ESPERAR` não conta como repetição.

**Rationale:** sem isso, rodada de 0 progresso consumiria o orçamento, ou o laço não pararia nunca.

**Alternatives Rejected:**
1. Teto de tarefas por rodada - decisão do Roberto descartou.
2. Contar por tempo - nenhum script mede o agente.

**Consequences:**
- Um gate instável não se repete sem commit novo de código. Quem quer repetir faz esse commit; `--resume` não libera, de propósito.

---

### Decision 5: Impressão digital do gate

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-11-05 |

**Context:** decisão D2 do Roberto: comando alterado no meio para com `gate-alterado`.

**Choice:** sha256 das linhas `kind:`, `cmd:`, `pass_when:`, `threshold:` e `manual_fallback:` da saída de `verify-gate.sh --print` (que ganha a última linha, aditiva), gravado no `iniciar`, em cada gate e comparado em `proximo`, `verificar`, `concluir` e `--resume`. `--aceitar-gate-novo` grava a nova e registra antes e depois no relatório; gate de outra impressão digital não conta como último (H2).

**Rationale:** ler pela saída do `--print` usa o mesmo parser do gate, sem um 2º.

**Alternatives Rejected:**
1. Só avisar - decisão do Roberto.
2. Hash do DEFINE inteiro - um `DESIGN` iterado ou nota no DEFINE pararia sem motivo.

**Consequences:**
- Não protege de teste enfraquecido por dentro do `cmd`: isso é papel do avaliador e da revisão, e o `docs/sdd-drive.md` diz.

---

### Decision 6: `--checar` no `verify-gate.sh` e `--drive` no `seguir`

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-11-05 |

**Context:** o `--print` é isento de marcador e Governança, e o `seguir` para com o encadeamento desligado. O drive precisa das duas perguntas sem duplicar as regras.

**Choice:** `verify-gate.sh --checar <DEFINE>` roda marcador → linha → bloco → `kind` → `cmd` (que precisa ser executável, salvo em manual-ux) e sai antes de rodar, com 0, 5 ou 64, sem trace; manual-ux sai 0. `sdd-fluxo.sh seguir <fase> <DEFINE> <próxima> --drive` trata o encadeamento como ligado só nessa chamada, sem ler nem mudar `flow.autonomous`; `release` continua parando em D1; nos 3 motivos de revisão, imprime `DRIVE_ACAO: REVISAO_DESIGN`; a linha de transição diz `(execução do sdd-drive)`. Na entrada, `iniciar`, `--dry-run` e `--resume` conferem nos 2 arquivos vizinhos a capacidade (`--checar`, `--drive`): falta ⇒ exit 2 com a frase de atualizar `sdd/bin/` que a `sdd-release` já usa (H3).

**Rationale:** cada regra continua em um lugar; adivinhar por `grep` duplicaria a ordem que a F12 consertou.

**Alternatives Rejected:**
1. Reescrever no núcleo do drive - 2ª implementação de regras que já regrediram.
2. Variável de ambiente - agente não preserva ambiente entre comandos.

**Consequences:**
- Os 2 scripts ganham 1 opção; os exits existentes ficam iguais (AT-037).

---

### Decision 7: Encadeamento por execução, por texto no brief

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-11-05 |

**Context:** no checkpoint 1, o Roberto aprovou que chamar o drive liga o encadeamento só naquela execução.

**Choice:** a skill e o brief dizem que, nesta execução, `[auto · de rotina]` vale a recomendada e vira `sdd-drive.sh recibo`; D1 a D5 são perguntadas. Nada é gravado em `flow.autonomous`.

**Rationale:** nenhuma sessão de execução precisa do `estado` do `sdd-fluxo.sh`, porque o brief do executor não pergunta nada de rotina; uma escrita no config sobraria se a sessão caísse.

**Alternatives Rejected:**
1. `sdd-fluxo.sh estado` ler o estado do drive - muda contrato para um caso só.
2. Escrever `flow.autonomous: true` - sobra no arquivo em uma queda.

**Consequences:**
- O recibo sai no `DRIVE_REPORT`, seção `Decidi sozinho`.

---

### Decision 8: O que o `deploy-do-sha.sh` decide

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-11-05 |

**Context:** porte de `deploy-do-sha.mjs` (338 linhas), sem Node, sem nomes da RDD, e sem o caso `barrado`, próprio de um workflow de 2 jobs: a lista de passos passageiros já impede repetir ali.

**Choice:** a cada volta, runs do SHA ∪ runs da branch com esse SHA (a listagem por commit pode atrasar), só do workflow, da branch (`--branch`, o slot `project.default_branch`, `origin/HEAD`, `main`, nesta ordem), pelo campo `headBranch` também, e com `event` `push` ou `workflow_dispatch`. Desfechos e exits:
1. próprio verde ⇒ `✅ no ar`, 0;
2. próprio sem `success` (`cancelled`, `failure`, `timed_out`) e substituto verde, mais novo e que contém o commit ⇒ `✅ no ar via substituto`, 0;
3. run em andamento, próprio ou substituto ⇒ espera;
4. falha em passo passageiro, commit na ponta depois de `git fetch`, nada mais novo, nenhum redisparo ⇒ `gh workflow run`, marca em `<git-common-dir>/deploy-do-sha/redisparado-<sha>`, espera; sem run novo em `--sem-run` segundos ⇒ 4, nunca 2;
5. resto ⇒ `🔴 falhou` ou `🔴 não está no ar`, 2, com o motivo de não ter repetido;
6. nenhum run em `--sem-run` segundos, ou o teto ⇒ 4;
7. `gh` ou `git` ausente, ou `gh` sem login ⇒ 3. Uso, SHA desconhecido, sem workflow ⇒ 64.
Ancestral desconhecido fica em espera, nunca em "não contém". Teto pelo relógio. Cada chamada ao `gh` e ao `git` com limite de 60 s e `GIT_TERMINAL_PROMPT=0`. O exit 4 cita o último erro de consulta, quando houve.

**Rationale:** mesma regra do item 10, num lugar só, com os aprendizados das 5 revisões do privado: nunca `gh run rerun`, limite de 1 redisparo por SHA, e não por processo.

**Alternatives Rejected:**
1. `gh run watch` - não cobre substituto nem fila.
2. Manter o caso `barrado` - específico do workflow do privado; a F15 pode trazer se medir falta.

**Consequences:**
- A marca fica no `.git`; num sandbox só leitura, falha com aviso, e o `workflow_dispatch` na lista segue valendo como redisparo já feito.

---

### Decision 9: `sdd-archive.py`: lotes pelo nome e proteção pela ficha

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-11-05 |

**Context:** o privado usa a memória do Roberto para "frente aberta"; `5A`, `5B`, `5C` não dizem nada a quem lê.

**Choice:** lotes `com-ledger` e `sem-ledger`, com destino `sdd/archive/<F>/`, o mesmo do passo 15b; `soltos`, com destino `sdd/archive/_REPORTS_<AAAA-MM>/`, o mês do último commit do arquivo. Protegido = `sdd/handoffs/HANDOFF_<F>.md` cujo `Status` não começa em ✅ (a regra do `handoff-lint.py`), ou nome da feature, como palavra inteira (`F1` não casa `F14`), ou de um documento do grupo citado em ficha aberta. Lista por `git log --date=short --format=%cd --name-only -z --no-renames` e `git ls-files -z`: `%cs` não existe no piso 2.20, e nome com acento sairia entre aspas. Nome do grupo: o que vem depois de um prefixo conhecido, sem sufixo minúsculo `_s2` e sem data; `_V2` maiúsculo é parte do nome.

**Rationale:** porte fiel do que importa, trocando a fonte da proteção.

**Alternatives Rejected:**
1. Mover sem lote - 1 commit por lote é o que permite reverter.
2. Apagar - nunca; `git mv` preserva o histórico.

**Consequences:**
- Em repositório sem histórico dos documentos (como este), a idade é "desconhecida" e o arquivo não rastreado é pulado.

---

### Decision 10: Raio de impacto: passo e brief

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-11-05 |

**Context:** O2 pede um subagente por superfície, citando invariantes do módulo.

**Choice:** o 0b lista as superfícies do diff e despacha `references/raio-de-impacto.md` com só `superficie:`, `antes:`, `depois:`, `invariantes:` e `worktree:`. Sem subagente, a mesma sessão percorre as superfícies em sequência (a tabela de degradação diz sequencial, não exit 40). Retorno `<<<RAIO`, com `consumidor: arquivo:linha · quebra|ok` e `invariante: INV-nnn · ok|viola`. Consumidor quebrado ou invariante violada alimenta o 0d como NON_WAIVABLE, que já existe. Sem `sdd/invariants.md`, diz e segue.

**Rationale:** quebra nasce em código não modificado; olhar uma superfície de cada vez é o que o privado mediu.

**Alternatives Rejected:**
1. Script que acha consumidores - depende da linguagem de cada projeto.

**Consequences:**
- Mais um brief; o bloco do OK não muda, e o achado entra pelo Veredito.

---

### Decision 11: As 2 pendências

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-11-05 |

**Context:** decisão do Roberto: guarda do avaliador e L10.

**Choice:** `avaliador-guard.sh`: linha `??` sob as 4 pastas não entra em `SUJOS`, conta em `DOCS`, e a saída ganha a frase de U12; rastreado modificado segue sujo. `--permitir` fica. Curator: em `achados()`, linha que, depois do prefixo `│` do gate, começa em `$ ` ou `+ ` ou casa `(❌ (delta|invariantes) linha \d+:|🔴 trava INV:|\S+\.md:\d+: ❌ )` é ignorada. `$ cmd` de várias linhas e log de sonda dentro de log escapam, e o curador os descarta: é o limite de uma heurística sobre texto livre (LM-005).

**Rationale:** a regra da F7 é proteger trabalho do build; documento novo não rastreado não é restaurável por `git checkout`, e o aviso diz o risco. A L10 é estreitada por forma exata, sem adivinhar texto (LM-005).

**Alternatives Rejected:**
1. Slot com os prefixos - mais um campo para 1 caso.
2. Ignorar todo `AVAL*-*.log` - perderia achado real desses logs.

**Consequences:**
- `git clean` num avaliador pode levar documento não rastreado; o brief já proíbe, e o aviso diz.

---

### Decision 12: Instalação, versões e Release

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-11-05 |

**Context:** skill nova muda contagens; `sdd/bin/**` e `sdd/config.example.yaml` já disparam a Release.

**Choice:** `sdd-drive` 1.0.0, `sdd-release` 2.8.0. Nada do script novo depende de fixture em pasta nova: o `init` não traz `sdd/fixtures/` num projeto já instalado, então o self-test monta tudo em memória (H3). Contagens 18 → 19 em `test_skill_lint`, `test_conversa`, `test_docs`; roadmap de 3 para 2 temas; contagem de perguntas em `test_decisoes_lint`. `v2.7.0` por tag, push atômico. O brief `executor-drive` entra como caso próprio do `despachar`.

**Rationale:** decisão 5 do brainstorm da F14.

**Alternatives Rejected:**
1. Patch automático (`v2.6.1`) - traz comando novo para quem instala.

**Consequences:**
- O `init` copia a skill, os scripts e as fixtures sem mudança em `bin/sdd-open.sh`.

---

## File Manifest

| # | File | Action | Purpose | Agent / Owner | Dependencies |
|---:|---|---|---|---|---|
| 1 | `sdd/bin/verify-gate.sh` | Modify | `--checar` (Decision 6) | (general) | None |
| 2 | `sdd/bin/sdd-fluxo.sh` | Modify | `seguir --drive`, caso `executor-drive` no `despachar` (Decisions 6, 12) | (general) | None |
| 3 | `sdd/bin/sdd-drive.sh` | Create | verbos, estado, motivos, relatório, self-test (Decisions 1 a 5) | (general) | 1, 2 |
| 6 | `sdd/bin/deploy-do-sha.sh` | Create | Decision 8 | (general) | None |
| 8 | `sdd/bin/sdd-archive.py` | Create | Decision 9 | (general) | None |
| 9 | `sdd/bin/avaliador-guard.sh` | Modify | documento não rastreado (Decision 11) | (general) | None |
| 10 | `sdd/bin/playbook-curator.sh` | Modify | L10 (Decision 11) | (general) | None |
| 11 | `sdd/config.example.yaml` | Modify | `drive.max_rounds`, `deploy.workflow`, `deploy.transient_steps` | (general) | None |
| 12 | `sdd/WORKFLOW_CONTRACTS.yaml` | Modify | bloco `sdd_drive` e `raio_de_impacto` | (general) | 3 |
| 13 | `.agents/skills/sdd-drive/SKILL.md` | Create | a skill (AT-019) | (general) | 3 |
| 14 | `.agents/skills/sdd-drive/references/como-falar.md` | Create | glossário e as 2 perguntas (U2, U4, U5) | (general) | 13 |
| 15 | `.agents/skills/sdd-drive/references/executor.md` | Create | brief do executor (AT-020) | (general) | 13 |
| 16 | `.agents/skills/sdd-release/SKILL.md` | Modify | 0b, 10, 11, 15b; 2.8.0 | (general) | 6, 8 |
| 17 | `.agents/skills/sdd-release/references/raio-de-impacto.md` | Create | Decision 10 | (general) | 16 |
| 18 | `docs/sdd-drive.md` | Create | mecanismo, com exemplo e a tabela de motivos (U11) | (general) | 3 |
| 19 | `docs/pt-BR/sdd-drive.md` | Create | versão em português | (general) | 18 |
| 20 | `docs/roadmap.md` | Modify | sai a linha `sdd-drive` | (general) | 18 |
| 21 | `docs/pt-BR/roadmap.md` | Modify | sai a linha `sdd-drive` | (general) | 19 |
| 22 | `docs/cli-conventions.md` | Modify | palavras novas e os 3 comandos | (general) | 3, 6, 8 |
| 23 | `docs/pt-BR/guia-do-aluno.md` | Modify | a 19ª skill | (general) | 13 |
| 24 | `README.md` | Modify | tabela de skills e link | (general) | 18 |
| 25 | `README.pt-BR.md` | Modify | tabela de skills e link | (general) | 19 |
| 26 | `AGENTS.md.tmpl` | Modify | linha da skill | (general) | 13 |
| 27 | `MANIFEST.txt` | Modify | os arquivos novos | (general) | 3, 6, 8, 13 a 15, 17 a 19, 28 a 31 |
| 28 | `tests/test_drive.py` | Create | AT-001 a AT-018, inclusive a chamada do `--self-test` | (general) | 3 |
| 29 | `tests/test_deploy_do_sha.py` | Create | AT-022 a AT-026, com `gh` de mentira e cenários no próprio teste | (general) | 6 |
| 30 | `tests/test_sdd_archive.py` | Create | AT-028 a AT-030 | (general) | 8 |
| 31 | `tests/test_f14_drive_textos.py` | Create | AT-017, AT-019 a AT-021, AT-027, AT-031, AT-035, AT-036 | (general) | 12 a 17 |
| 32 | `tests/test_avaliador_guard.py` | Modify | AT-032, AT-033 | (general) | 9 |
| 33 | `tests/test_playbook_curator.py` | Modify | AT-034 | (general) | 10 |
| 34 | `tests/test_verify_gate.py` | Modify | `--checar` e `manual_fallback:` no `--print`, dos 2 lados | (general) | 1 |
| 35 | `tests/test_fluxo.py` | Modify | `seguir --drive`, `executor-drive` | (general) | 2 |
| 36 | `tests/test_skill_lint.py` | Modify | 18 → 19 | (general) | 13 |
| 37 | `tests/test_conversa.py` | Modify | 18 → 19 | (general) | 13 |
| 38 | `tests/test_docs.py` | Modify | 18 → 19; roadmap de 3 para 2 temas; `docs/sdd-drive.md` | (general) | 18 a 25 |
| 39 | `tests/test_decisoes_lint.py` | Modify | contagem de perguntas | (general) | 13, 14 |
| 40 | `tests/test_contrato_build_release.py` | Modify | pino da versão 2.8.0; item 10 | (general) | 16 |
| 41 | `tests/test_f14_textos.py` | Modify | pino da versão 2.8.0 | (general) | 16 |

**Total Files:** 38 (fora o que a suíte mostrar que referencia a contagem de skills ou o item 10, registrado como drift no BUILD_REPORT).

### Agent Assignment Rationale

| Agent / Owner | Files Assigned | Why |
|---|---|---|
| (general) | todos | modo default (um agente), como nas F9–F14; sem catálogo de agentes no repositório |

**Agent Discovery:** Not available

Fora do commit (evidência, branch `docs/`): `sdd/reports/evidence/F14_DRIVE/` (`ev.sh`, baseline, sabotagens, prova em agente real, `ledger-review.md`, `real-rodada.sh`).

---

## Landmines aplicáveis

Varredura rodada em 2026-11-05 com `playbook-lint.sh --grep` sobre `drive`, `verify-gate`, `heurística`, `git archive`, `untracked`, `review`, `baseline`, `exit 0`.

| LM-nnn | Superfície | Tratamento |
|---|---|---|
| LM-001 | `sdd-drive.sh`, textos da skill | ✔ tratado: cada motivo roda com fixture dos 2 lados; os testes de texto conferem nome e ordem, e o efeito é provado num agente real (AT-038) |
| LM-002 | testes novos, `--checar` | ✔ tratado: vermelhos antes dos verdes no self-test; baseline vermelha na `v2.6.0`; `--checar` sai 5 e 64 em teste, antes do verde |
| LM-003 | `avaliador-guard.sh` e a revisão real | ✔ tratado: a guarda só libera não rastreado nas 4 pastas; a revisão roda com tudo commitado |
| LM-005 | filtro da colheita (L10) | ✔ tratado: filtro por forma exata da linha, com o caso vizinho (achado real no mesmo log) em teste |
| LM-006 | `sdd-drive.sh --self-test` | ✔ tratado: o self-test monta repositório próprio; roda na cópia de `git archive`, sem `.git` |

---

## Code Patterns

### Pattern 1: bash que entrega ao núcleo Python

```bash
if ! command -v python3 >/dev/null 2>&1; then
  echo "🛑 sdd-drive: python3 não encontrado" >&2
  exit 64
fi
SDD_DRIVE_BIN="$BIN" python3 -I -B - "$@" <<'PY'
```

O núcleo vem do stdin; todo filho roda com `stdin=DEVNULL`. `-I` tira a pasta do projeto do `sys.path`: um `json.py` do usuário não pode entrar no lugar do módulo (L1). `$(cat <<'PY'` não serve: um apóstrofo no núcleo dá erro de sintaxe no bash 3.2, e `/dev/fd/3` não abre em Python nativo do Windows.

### Pattern 2: toda parada passa por um lugar

```python
def parada(st, motivo, extra=""):
    if st is not None:
        st["motivo"] = motivo
        grava_estado(st)
        grava_relatorio(st, motivo, extra)
    print("motivo: " + motivo)
    print(FRASES[motivo])
    if extra:
        print(extra)
    fim(*RESULTADOS[motivo])
    sys.exit(EXITS[motivo])
```

### Pattern 3: a próxima ação é uma função pura do disco

```python
def proxima(st, raiz):
    if gate_rodando(st, raiz):
        return ("ESPERAR", "")
    if not existe_design(st, raiz):
        return ("DESIGN", "")
    rc, acao_seguir, motivo = seguir_design(st, raiz)
    if rc == 64:
        falha("sdd-fluxo.sh seguir saiu 64: " + motivo)
    if rc != 0:
        return (acao_seguir or "DESIGN", motivo)
    pend, total = tarefas(st, raiz)
    if pend:
        return ("RODADA", "tarefa: %d de %d — %s" % (total - len(pend) + 1, total, pend[0]))
    return depois_das_tarefas(st, raiz)
```

### Pattern 4: `gh` e `git` sempre com limite

```python
def roda(cmd, cwd, teto=60):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=teto, stdin=subprocess.DEVNULL)
```

`TimeoutExpired` e `OSError` viram "consulta falhou, tento de novo", nunca desfecho.

### Pattern 5: log de evidência com o exit real

```python
with open(log, "w", encoding="utf-8") as f:
    f.write("$ verify-gate.sh " + st["define"] + "\n")
    f.flush()
    r = subprocess.run(["bash", gate, st["define"]], cwd=raiz, stdout=f, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
    f.write("[exit=%d]\n" % r.returncode)
```

---

## Data Flow

```text
1. iniciar: --checar (5 ou 64 ⇒ parada) → branch ≠ padrão → --print ⇒ impressão digital → grava estado → próxima ação (10)
2. DESIGN: o agente roda a fase Design; proximo reconfere com seguir … --drive
3. RODADA: PROGRESS semeado do manifest; executor fresco: 1 tarefa, 1 commit, [x], <<<RODADA; proximo
4. VERIFICAR: sem mudança fora dos documentos ⇒ trava → gate (--fundo: destacado) → log → recarrega o estado → grava → solta a trava
     exit 0 ⇒ AVALIAR_E_RELATAR (avaliador, BUILD_REPORT) → concluir → report-lint → gate-verde (0)
     exit 2 ⇒ gasta rodada → CORRIGIR (DESIGN ou tarefa reaberta) → volta a 3 · no limite ⇒ orcamento-rodadas (20)
     exit 3, 4, 5, 64 ⇒ parada, sem gastar rodada
5. Queda: --resume recalcula do disco; não gasta rodada.
6. Toda parada reescreve o DRIVE_REPORT; nada é publicado.

release: 0b por superfície → OK → push → deploy-do-sha.sh (espera, substituto, redisparo único) → ficha
```

---

## Integration Points

| System | Type | Auth | Direction | Timeout/Retry | Failure Behavior |
|---|---|---|---|---|---|
| GitHub Actions por `gh` | CLI | login do `gh` da pessoa | leitura e 1 `workflow run` | 60 s por chamada; volta a cada 15 s; teto 2400 s | ausente ⇒ exit 3; consulta falha ⇒ tenta de novo até o teto; dispatch recusado ⇒ exit 2 |
| git | CLI local | — | leitura; `git mv` no archive; `fetch` no deploy | 60 s no `fetch` | fetch falho ⇒ não redispara |
| Agente de código | humano ou subagente | — | a skill chama | — | sem subagente ⇒ exit 40 |

---

## Testing Strategy

| Layer | What | How | Mapped to |
|---|---|---|---|
| Unidade por CLI | motivos, ações, retomada, impressão digital | `tests/test_drive.py`, com cópia de `sdd-drive.sh` e `verify-gate.sh` de mentira numa sandbox `git init` | AT-001 a AT-016 |
| Self-test | 12 motivos e 6 exits com o `verify-gate.sh` real | `--self-test`, em pasta temporária, chamado por `tests/test_drive.py` | AT-018 |
| Deploy | 7 desfechos | `gh` de mentira no `PATH`, com cenários no teste e registro de chamadas; git real | AT-022 a AT-026 |
| Archive | lotes, proteção, `git mv` | repositório na sandbox, `--hoje` fixo | AT-028 a AT-030 |
| Barreira por efeito | `git` e `gh` de mentira, toda a sequência de verbos | nada de push, release ou workflow run no registro | AT-017 |
| Texto | skill, passo, contratos | nomes e ordem iguais nos 4 lugares; recorte do item 10 | AT-019 a AT-021, AT-027, AT-031, AT-035, AT-036 |
| Agente real | efeito no disco | Codex CLI com `deepseek/deepseek-v4-pro`, modelo declarado | AT-038 |
| Sabotagem | 1 por script novo e 1 por regra central | `sabotagens.sh` | Regra 6 do 8.0 |
| Baseline | testes novos vermelhos na `v2.6.0` | `gate-baseline.sh` e cópia da tag | LM-002 |

Verify Gate: `kind: test` de sempre. Tetos de CI: os testes novos não usam rede nem o `cmd` real.

---

## Error Handling

| Error Type | Handling Strategy | User-Facing Message | Retry? |
|---|---|---|---|
| DEFINE sem gate, com dúvida, branch padrão | parada tabelada, sem estado | frase do motivo e a seta | Não |
| Estado ilegível ou de outro DEFINE | `estado-invalido`, sem adivinhar | caminho do arquivo e o que fazer | Não |
| Não conseguiu gravar estado ou relatório | exit 2, com a causa | `RESULTADO: FALHA` | Não |
| Gate não executa (bash ausente) | exit 2 | a causa | Não |
| `verify-gate.sh` ou `sdd-fluxo.sh` antigos ao lado do script | exit 2 na entrada, sem estado | qual arquivo e como atualizar `sdd/bin/` | Não |
| Agente morto no meio do gate | trava de processo morto se libera; o log sem `[exit=N]` fica, e a execução seguinte usa outro `k` | `ESPERAR` enquanto vive, depois `VERIFICAR` | Sim |
| Slot `drive.max_rounds` inválido | exit 64 | diz de onde veio | Não |
| `PROGRESS` sem linhas | `estado-invalido` | como recriar | Não |
| Consulta ao `gh` falha ou expira | tenta de novo até o teto | linha `⏳` em stderr; o exit 4 cita o último erro | Sim |
| Ancestral desconhecido | espera; no teto, exit 4 | diz qual SHA não conhece | Sim |
| Falha passageira | 1 redisparo | diz o que fez | Sim, 1 vez |
| `git mv` falha | exit 2, para no 1º | o arquivo e a causa | Não |
| Documento em bytes não UTF-8 no DEFINE | `define-invalido` | o arquivo | Não |

---

## Configuration

| Config Key | Type | Default | Description |
|---|---|---|---|
| `drive.max_rounds` | inteiro ≥ 1 | `3` | tentativas de ficar verde, por execução; `--max` sobrepõe |
| `deploy.workflow` | texto | `""` | arquivo do workflow que publica; vazio = a release passa o nome que leu |
| `deploy.transient_steps` | lista separada por vírgula | `""` | nomes de passos em que repetir é seguro; vazio = nunca repete |

Sem segredo: `gh` usa o login da pessoa.

---

## Security Considerations

- **Publicação:** nenhum verbo do drive publica; o teste corre todos os verbos com `git` e `gh` de mentira e lê o registro (AT-017). `deploy-do-sha.sh` só roda depois do OK e só redispara o que já foi aprovado, na ponta da branch.
- **`gh run rerun` proibido:** publicaria código velho por cima do novo; o registro do `gh` de mentira prova que nunca é chamado.
- **Injeção por nome:** `<F>` validado contra lista explícita, sem faixa `[A-Za-z]`; comandos por lista, sem shell.
- **Gate alterado:** impressão digital (Decision 5).
- **Caminhos:** o DEFINE precisa estar dentro do repositório; link que sai da raiz é recusado no estado e no relatório.
- **`sdd-archive.py`:** nunca apaga; só `git mv` de arquivo rastreado, sem commit, nunca em `sdd/releases/`, `sdd/archive/` ou `evidence/`.
- **Chave da OpenRouter:** só no ambiente do processo da revisão e da prova; nunca em arquivo.

---

## Observability

- `sdd/reports/DRIVE_REPORT_<F>.md`: motivo, rodadas, commits, trocas de gate e recibos.
- Trace do `verify-gate.sh` em `sdd/traces/<F>.jsonl`, a cada `verificar`; `--checar` não grava.
- `sdd/reports/evidence/<F>/DRIVE-gate-r<k>.log`, com `[exit=N]` real, para o `gate-shell-evidencia.sh`.
- `deploy-do-sha.sh`: progresso em stderr, frase única em stdout.

---

## Requirements Traceability

| Requirement / AT | Design Element | Test / Gate |
|---|---|---|
| AT-001 a AT-007 | Decisions 2, 3, 4, 6; manifest 1, 2, 3 | `tests/test_drive.py` |
| AT-008 a AT-010 | Decisions 3, 4; Pattern 5 | `tests/test_drive.py` |
| AT-011 | Decision 5 | `tests/test_drive.py` |
| AT-012 a AT-016 | Decisions 2, 3 | `tests/test_drive.py` |
| AT-017, AT-018 | Decision 1; manifest 3, 4, 5 | `tests/test_f14_drive_textos.py`, `--self-test` |
| AT-019, AT-020 | Decisions 2, 7; manifest 13, 14, 15, 12, 2 | `tests/test_f14_drive_textos.py`, `tests/test_fluxo.py` |
| AT-021 | Decision 10; manifest 16, 17 | `tests/test_f14_drive_textos.py` |
| AT-022 a AT-026 | Decision 8; manifest 6, 7 | `tests/test_deploy_do_sha.py` |
| AT-027 | Decision 8; manifest 16 | `tests/test_f14_drive_textos.py`, `tests/test_contrato_build_release.py` |
| AT-028 a AT-030 | Decision 9; manifest 8 | `tests/test_sdd_archive.py` |
| AT-031 | manifest 16 | `tests/test_f14_drive_textos.py` |
| AT-032, AT-033 | Decision 11; manifest 9 | `tests/test_avaliador_guard.py` |
| AT-034 | Decision 11; manifest 10 | `tests/test_playbook_curator.py` |
| AT-035 | manifest 11 | `tests/test_f14_drive_textos.py` |
| AT-036 | Decision 12; manifest 18 a 27 | `tests/test_docs.py`, `tests/test_f14_drive_textos.py` |
| AT-037 | Decision 6 | a suíte inteira |
| AT-038 | Testing Strategy | `sdd/reports/evidence/F14_DRIVE/codex-drive.sh` |

---

## Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Suíte acima dos 25 min no Ubuntu (17m41s na última) | testes novos só com stub; medir no PR; se passar, ajustar o teto em commit próprio, como na F12 |
| Agente pula uma ação do script | o estado é recalculado do disco; a prova em agente real (AT-038) mede |
| Consertos da revisão criam regressão (F12, F13, F14) | teste de ataque dos 2 lados em cada conserto; orçamento decidido antes de cada rodada |
| Falso alarme do DeepSeek | medir antes de consertar |
| `gh` muda campo do `--json` | campos pedidos por lista, e falta de campo vira "não sei", nunca verde |

---

## Advisor Ledger

Revisão de contexto fresco do DESIGN v1.0 (`sdd/reviews/REVISAO_DESIGN_F14_DRIVE_20261105.md`, modo `contrato`, logs `AVAL-DESIGN-*.log`): NEEDS_WORK, 4 HIGH, 14 MEDIUM, 8 LOW, 5 propostas.

| # | Nota | Severidade | Veredito | Onde |
|---|---|---|---|---|
| A1 | Depois de `orcamento-rodadas`, o limite não barrava | proposta | ACEITA | DEFINE AT-012; Decision 3 |
| A2 | Gate antigo vale depois de aceitar o novo | proposta | ACEITA | DEFINE AT-011; Decisions 3, 5 |
| A3 | Scripts vizinhos antigos | proposta | ACEITA | DEFINE AT-002; Decision 6 |
| A4 | Verde sem `git add` | proposta | ACEITA | DEFINE AT-010, AT-014; Decision 3 |
| A5 | Barreira provada por efeito, frases fixas no teste | proposta | ACEITA | DEFINE AT-017; Testing Strategy |
| H1 | Orçamento não barra por script | HIGH | APLICADA | Decision 3; DEFINE AT-012 |
| H2 | Gate antigo depois de `--aceitar-gate-novo` | HIGH | APLICADA | Decisions 3, 5; DEFINE AT-011 |
| H3 | Upgrade com diagnóstico falso; fixture que não chega | HIGH | APLICADA: conferência de capacidade, `seguir` 64 vira exit 2, self-test sem fixture em pasta | Decisions 6, 12; DEFINE AT-002, AT-005 |
| H4 | Gate longo e 2 gates juntos | HIGH | APLICADA, com `--fundo` além do pedido: nem todo agente tem comando em segundo plano | Decision 2, 3; DEFINE AT-008, AT-019 |
| M1 | `manual_fallback` fora do `--print` | MEDIUM | APLICADA | Decision 5 |
| M2 | Log invertido | MEDIUM | APLICADA | Pattern 5; DEFINE AT-008 |
| M3 | Verde pode não ser do commit | MEDIUM | APLICADA | DEFINE AT-010 |
| M4 | Commit só de documento gasta rodada | MEDIUM | APLICADA | Decision 3; DEFINE AT-010 |
| M5 | Lugar do `--checar` | MEDIUM | APLICADA | Decision 6; DEFINE AT-037 |
| M6 | Fonte da branch padrão; HEAD destacado | MEDIUM | APLICADA | DEFINE AT-002; Decision 8 |
| M7 | Corrida depois do redisparo | MEDIUM | APLICADA | Decision 8; DEFINE AT-024 |
| M8 | Filtro por `event` | MEDIUM | APLICADA | Decision 8; DEFINE AT-022 |
| M9 | `--ours` depende da operação | MEDIUM | APLICADA, por `git show origin/<branch>:CHANGELOG.md`; diverge do texto do plano, com o motivo no DEFINE | DEFINE AT-031 |
| M10 | Filtro da L10 deixa o diagnóstico do lint | MEDIUM | APLICADA | Decision 11; DEFINE AT-034 |
| M11 | Log sobrescrito | MEDIUM | APLICADA | DEFINE AT-008 |
| M12 | "Sem ✅" diverge do lint | MEDIUM | APLICADA | Decision 9; DEFINE AT-030 |
| M13 | DEFINE e DESIGN discordam | MEDIUM | APLICADA | DEFINE AT-001, AT-005 |
| M14 | Cobertura do gate | MEDIUM | APLICADA: AT-038 por evidência, `--self-test` com teste | DEFINE AT-038; Testing Strategy |
| L1 | `NUCLEO` e `json.py` do projeto | LOW | APLICADA, por `-I` e stdin; `/dev/fd/3` recusado: não abre em Python nativo do Windows, que o README declara | Pattern 1 |
| L2 | Token estável no `seguir --drive` | LOW | APLICADA | Decisions 3, 6 |
| L3 | Lacunas do archive | LOW | APLICADA | Decision 9 |
| L4 | Detalhes do `deploy-do-sha.sh` | LOW | APLICADA | Decision 8 |
| L5 | Escopo dos testes de texto | LOW | APLICADA | DEFINE AT-033; Testing Strategy |
| L6 | Manual-ux terminal; gate instável | LOW | APLICADA | Decision 4 |
| L7 | Verbos sem contrato | LOW | APLICADA | DEFINE AT-013, AT-016 |
| L8 | Manifest e PROGRESS | LOW | APLICADA | Decision 3; DEFINE AT-006 |

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | 2026-11-05 | SDD Design by RDD | Initial version |
| 1.1 | 2026-11-05 | revisão do DESIGN | 31 notas aplicadas (Advisor Ledger) |
| 1.8 | 2026-11-06 | revisão real, rodada 4 | trava de estado curta; marca do redisparo por criação exclusiva |
| 1.7 | 2026-11-05 | revisão real, rodada 2 | a repetição conta a posição; `confere_dentro`; `--resume` não grava com gate rodando |
| 1.6 | 2026-11-05 | revisão real, rodada 1 | `--resume` conta a repetição; `COMMITAR` na ordem das ações; trava atômica; `tasklist` no Windows; `ledger-review.md` |
| 1.5 | 2026-11-05 | avaliador, ciclo 3 | submodule, extensão de documento, log que confirma o gate, citação em qualquer caixa; limites declarados em `docs/sdd-drive.md` (`AVALIACAO_F14_DRIVE_20261105-ciclo3.md`) |
| 1.4 | 2026-11-05 | avaliador, ciclo 2 | `--no-renames` no diff entre commits; só a 1ª tabela do manifest; a ficha protege por palavra inteira, em qualquer caixa (`AVALIACAO_F14_DRIVE_20261105-ciclo2.md`) |
| 1.3 | 2026-11-05 | avaliador, ciclo 1 | ordem, HEAD de antes do gate, estado por forma inteira, sem fixture em pasta (`AVALIACAO_F14_DRIVE_20261105-ciclo1.md`) |
| 1.2 | 2026-11-05 | build | drift: o documento virou `docs/sdd-drive.md`, porque a varredura da W0 (`tests/test_correcoes_w0.py`) proíbe o padrão do comando do privado em qualquer caminho; `docs/verify-gate-contract.md` cita o `--checar` |

---

## Next Step

Execute o **SDD Build by RDD**.
