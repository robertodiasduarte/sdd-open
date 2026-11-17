# DESIGN: F24 Release enxuta — a parte depois do push

> Technical design for implementing F24 Release enxuta

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | F24_RELEASE_ENXUTA |
| **Date** | 2026-11-16 |
| **Author** | design-agent |
| **DEFINE** | [DEFINE_F24_RELEASE_ENXUTA.md](./DEFINE_F24_RELEASE_ENXUTA.md) |
| **Status** | Ready for Build |

---

## Architecture Overview

```text
 RELEASE (sdd-release)                                         LOTE (sdd-playbook, sob demanda)
 ───────────────────                                           ───────────────────────────────
 FASE 0 item 0: trilha.sh {F} ─► TRILHA: curta|completa          numa frente nova (branch da padrão atualizada)
      └─ vai para o ledger (campo trilha:)                        │
 FASE 1 item 7: bloco do OK                                       ├─ playbook-curator.sh --fila  (lista as entradas)
      └─ push-de-papel.py ─► "O commit de papel publica?"         │
 ── OK ──                                                         ├─ por entrada E:
 FASE 2: 7b · 8 push · 9 deploy · 10 verificar+smoke (iguais)     │    --conferir-entrada E ─► staging fresco
      └─ smoke vermelho ⇒ a ÚNICA pergunta depois do OK           │       (refaz a colheita sobre a cópia; difere ⇒ recusa)
 FASE 3 (papel, sem pergunta):                                    │    --selar · fronteira --snapshot · curador fresco
   colheita:  playbook-curator.sh --enfileirar {F}                │    fronteira --comparar · --conferir-bloco
        └─► sdd/curadoria/fila/{F}/<AAAAMMDDTHHMMSSZ>/            │    AUTO entra · PERGUNTA ⇒ [D3] uma por item
             colheita.txt · colheita.rc · CURATOR-colhidos.txt    │
             DESIGN/BUILD_REPORT/HANDOFF/ledger/AVAL* (cópias)    ├─ um --aplicar só (IDs dos ADD pelo playbook da base)
             ausentes.txt (logs que o projeto não versiona)       ├─ playbook-lint · --anti-collapse · --validar-inv
        └─► --fila: >5 entradas ⇒ 1 linha de aviso                ├─ registro: fp das entradas julgadas ─►
   ficha:     ficha-publicado.py {F} (bloco Publicado do ledger)  │    sdd/releases/<F>/CURATOR-colhidos.txt ; git rm -r E
              + o agente escreve só Falta e alertas               ├─ commit chore(playbook): lote …
   arquivo:   ledger estado: shipado ⇒ git mv um a um             └─ [D1] enviar? (push-de-papel.py diz se publica)
   commit de papel único ─► landar como o passo 5 ─► push
   branch remota da frente: apagar se ancestral (recibo)
 FASE 4: relatório final (cita a ficha pelo caminho; recibo "Decidi sozinho"; comando de limpeza local)
```

---

## Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| `playbook-curator.sh --enfileirar` | prepara, colhe excluindo o que já está na fila, grava a entrada da fila (AT-001, AT-002) | Python embutido (mesmo programa) |
| `playbook-curator.sh --fila` | lista a fila; acima de 5 entradas, a linha de aviso e exit 10 (AT-005) | idem |
| `playbook-curator.sh --conferir-entrada` | refaz a colheita sobre a cópia da entrada, compara as impressões e prepara o staging do lote (AT-004, AT-010) | idem |
| `playbook-curator.sh --registrar` | grava as impressões das entradas julgadas no registro da feature e tira as entradas da fila (AT-002) | idem |
| `sdd/bin/ficha-publicado.py` | gera o bloco `## Publicado` da ficha a partir dos ledgers (AT-008) | Python 3.9 stdlib |
| `sdd/bin/trilha.sh` | decide a trilha curta ou completa pelo diff e pela ausência de DEFINE (AT-009) | bash 3.2 + git + awk |
| `sdd-release/scripts/push-de-papel.py` | diz se um push com aqueles arquivos dispara um workflow que publica (AT-006) | Python 3.9; reusa o parser do `deploy-espera-testes.py` |
| `sdd-release/SKILL.md` | FASES 2 a 4 novas: papel sem pergunta, uma parada só (AT-001, AT-006, AT-007, AT-009) | Markdown |
| `sdd-release/references/como-falar.md` | a tabela "Depois do push" para o aluno (AT-011) | Markdown |
| `sdd-playbook/references/lote.md` | o procedimento do lote (o antigo 17b, mudado de lugar) (AT-003, AT-004) | Markdown |
| `handoff-lint.py` + molde da ficha | aceitam o bloco Publicado como histórico; molde com os marcadores (AT-008, AT-009) | Python + Markdown |

---

## Key Decisions

### Decision 1: A fila é uma pasta versionada por publicação, que também é um staging

| **Status** | Accepted | · | **Date** | 2026-11-16 |
|------------|----------|---|----------|------------|

**Context:** o lote roda dias depois, em outra frente, quando a worktree da publicação já pode ter sido removida e a ficha já cresceu (o número de linha mudaria). A evidência que o curador abre (`arquivo:linha`) precisa estar congelada.

**Choice:** `sdd/curadoria/fila/<F>/<AAAAMMDDTHHMMSSZ>/` com `colheita.txt`, `colheita.rc`, `CURATOR-colhidos.txt` (as impressões excluídas na hora da colheita) e as cópias dos documentos do staging (só o nível de cima, os mesmos nomes). A pasta tem o formato de um staging, então `--colher <entrada>` funciona sobre ela. Um log `AVAL*-*.log` cujo original o git ignora (`git check-ignore -q` sai 0) não é copiado e vai para `ausentes.txt`. A entrada entra no commit de papel.

**Rationale:** reusar o formato do staging deixa o `--colher`, o `--selar` e o `--conferir-bloco` como estão; versionar é o único jeito de o lote, numa worktree nova, achar a entrada.

**Alternatives Rejected:**
1. Fila só local (fora do git) — rejeitada porque o lote roda noutra worktree, nascida da branch padrão, que não teria a pasta.
2. Guardar só a colheita e recolher no lote a partir dos originais — rejeitada porque os originais mudam (a ficha cresce) e os logs podem ter sumido com a worktree.

**Consequences:** o repositório ganha cópias de documentos que já estão nele (algumas dezenas de KB por publicação, apagadas pelo lote). Log que o projeto não versiona fica de fora: na hora de enfileirar, a colheita é refeita sobre a própria entrada, e as impressões que só esse log provava vão para `ausentes.txt`; no lote, essas linhas são relatadas e nunca contadas, **por linha**, sem segurar o resto da entrada (AT-004).

---

### Decision 2: A exclusão pela fila acontece no staging, pelo mesmo registro de impressões

| **Status** | Accepted | · | **Date** | 2026-11-16 |
|------------|----------|---|----------|------------|

**Context:** sem lote entre duas publicações da mesma feature, a 2ª colheita repetiria as impressões da 1ª (elas só entram em `CURATOR-colhidos.txt` depois do julgamento).

**Choice:** `--enfileirar` grava no staging um `CURATOR-colhidos.txt` que é a união do registro da feature (`sdd/releases/<F>/CURATOR-colhidos.txt`) com as linhas `fp=` de toda entrada **boa** (`colheita.rc` = 0) da fila dessa feature, e só então chama a colheita. O `--colher` não muda: ele já trata como `JA_JULGADO` o que está nesse arquivo. Uma colheita sem linha de documento (só promoção ou invariante pendente, que é estado do playbook e volta em toda colheita) não é gravada (a saída é `NADA A COLHER`). Uma colheita que terminou (entrada nova ou `NADA A COLHER`) apaga as entradas falhas da mesma feature: ela cobre o que elas não colheram, porque as impressões delas nunca foram excluídas.

**Rationale:** um mecanismo só para "já julgado" e "já na fila"; as entradas da fila ficam disjuntas por impressão, e o lote pode julgá-las uma a uma.

**Alternatives Rejected:**
1. O lote junta as entradas e deduplica — rejeitada porque cada entrada tem a própria evidência congelada; juntar quebraria o `arquivo:linha`.
2. Uma entrada por feature, sobrescrita a cada publicação — rejeitada porque a evidência da 1ª publicação seria perdida.

**Consequences:** a linha `JA_JULGADO` passa a contar também o que está na fila (a frase diz "já julgada ou já na fila"). Duas publicações em worktrees paralelas ainda podem colher a mesma impressão; o `--conferir-entrada` tira do julgamento toda impressão que já está no registro (Decision 3).

---

### Decision 3: O lote refaz a colheita sobre a entrada e só julga o que bate

| **Status** | Accepted | · | **Date** | 2026-11-16 |
|------------|----------|---|----------|------------|

**Context:** a colheita passa dias no git; um push na branch padrão poderia plantar uma linha de contagem que nenhuma release colheu (S18 do Define), e o playbook mudou desde a colheita (IDs propostos, `PROMOVER?`, lição aposentada).

**Choice:** `--conferir-entrada <entrada> <playbook> [--inv]`, nesta ordem: (1) `colheita.rc` ≠ 0 ⇒ recusa; (2) a pasta da entrada tocada por mais de um commit (`git log --format=%H -- <entrada>`) ⇒ recusa; (3) **proveniência**: cada documento copiado (DESIGN, BUILD_REPORT, AVALIACAO, ledger, ficha, log de avaliação) tem de ter existido, com o mesmo conteúdo, no lugar dele no histórico (`git hash-object` da cópia e `git log --find-object=<blob> -- <caminhos de origem>` não vazio; os caminhos de origem são os mesmos que o `--preparar` lê, em `sdd/` e em `sdd/archive/<F>/`) ⇒ senão recusa, citando o documento; (4) copia a entrada para um staging novo (exclusivo, como o do `--preparar`), roda a colheita ali com `SDD_TRACE=off` e com o playbook de agora, e compara o conjunto de impressões (`fp=`) das linhas `DELTA`, `SUGESTAO`, `CANDIDATO` e `REJEITADO` da colheita guardada — menos as de `ausentes.txt`, as que já estão no registro e as de lição que não está mais ativa — com o da colheita refeita. Iguais ⇒ grava a colheita refeita como `colheita.txt` do staging, imprime `staging:` e sai 0 (1 quando não sobra nada a julgar). Diferentes ⇒ `RESULTADO: ENTRADA RECUSADA` com o motivo e exit 2. O `--enfileirar` avisa, na hora, quando um documento copiado difere do que está commitado (o lote recusaria a entrada).

**Rationale:** quem julga é a colheita refeita, com o playbook de agora (IDs e promoções certos); a guardada é a prova de que a release colheu aquilo. A comparação recusa a linha plantada numa entrada existente; a proveniência recusa a entrada fabricada inteira, com documentos que nunca estiveram no repositório (R3 da revisão do DESIGN). Quem consegue pôr um documento forjado no lugar original já controla os documentos da feature: esse risco é o mesmo de antes da F24.

**Alternatives Rejected:**
1. Assinar a colheita com hash no ledger — rejeitada porque o ledger está no commit atômico, antes da colheita, e quem planta a colheita planta o hash junto.
2. Julgar a colheita guardada como está — rejeitada pela S18 e porque os IDs propostos e as promoções envelhecem.

**Consequences:** uma linha cujo documento foi copiado mas que a colheita de agora não reproduz (formato do playbook mudou) recusa a entrada; a saída é refazer a colheita com `--enfileirar` numa pasta com os documentos, como diz a mensagem.

---

### Decision 4: Um `--aplicar` só para o lote inteiro, sobre o playbook da branch padrão

| **Status** | Accepted | · | **Date** | 2026-11-16 |
|------------|----------|---|----------|------------|

**Context:** várias entradas podem propor o mesmo `LM-nnn` novo.

**Choice:** o lote junta num `delta.txt` só as linhas AUTO e as aceitas de todas as entradas, e o `--aplicar` numera os `ADD` pelo maior ID do playbook que recebe o delta (`proximo_id`, `playbook-curator.sh:281`, usado em `aplicar`, `:833`). O lote roda numa frente nascida da branch padrão atualizada; no envio, se a base andou, reaplica o mesmo `delta.txt` sobre o playbook da base (como o envio de hoje). O recibo mostra o ID final de cada lição nova.

**Rationale:** o mecanismo de numeração já existe e já é testado; basta não fatiar o `--aplicar`.

**Alternatives Rejected:**
1. Renumerar no `--conferir-bloco` — rejeitada porque cada bloco só conhece a própria colheita.

**Consequences:** o `--anti-collapse` mede o lote inteiro; acima do limite de 20%, a regra de hoje vale (contadores e `ADD` num commit, uma mudança de conteúdo por commit depois).

---

### Decision 5: O commit de papel é coberto pelo OK, e o bloco do OK diz se ele publica

| **Status** | Accepted | · | **Date** | 2026-11-16 |
|------------|----------|---|----------|------------|

**Context:** hoje o envio do commit da curadoria é uma 2ª pergunta `[D1]`; o commit de ficha e changelog não tem regra própria e dispara deploy em muitos projetos (28 de 49 deploys sem arquivo publicável, medido no projeto de origem).

**Choice:** o bloco do OK ganha uma linha, **"O commit de papel publica?"**, preenchida por `push-de-papel.py` com a lista que o commit de papel vai ter (ficha, `CHANGELOG.md`, entrada da fila, `sdd/archive/{F}/`, e os documentos que saem de `sdd/features`). A pergunta do OK passa a ser **"Posso finalizar (push + deploy + verificar + papel)?"**. Depois do deploy, o commit de papel é landado como no passo 5 e enviado como no passo 8, sem pergunta. `PUBLICA` ⇒ a ficha ganha a pendência ✨ com o trecho de `paths-ignore`. Envio que falha ⇒ o commit fica na branch da frente e o relatório dá o comando.

**Rationale:** a pessoa aprova uma vez, sabendo o que o papel vai causar; o que publica de verdade (o código) continua no mesmo OK.

**Alternatives Rejected:**
1. Papel sem push (fica para a próxima publicação) — rejeitada porque a ficha no `main` ficaria atrasada e a próxima frente nasceria sem ela.
2. Perguntar o envio do papel — rejeitada porque é a parada que o escopo tira.

**Consequences:** o bloco do OK muda (1 linha a mais e a pergunta); os testes que conferem os rótulos do bloco são atualizados no mesmo commit.

---

### Decision 6: A trilha é decidida antes do OK e gravada no ledger

| **Status** | Accepted | · | **Date** | 2026-11-16 |
|------------|----------|---|----------|------------|

**Context:** depois do push, `origin/{default_branch}...HEAD` fica vazio: a trilha não pode ser medida na FASE 3.

**Choice:** `bash sdd/bin/trilha.sh {F}` roda no pré-voo (FASE 0, item 0), contra `origin/{default_branch}`, e o resultado vai para o ledger como `trilha: curta | completa`. Curta = sem `DEFINE_{F}.md` em `sdd/features/` nem em `sdd/archive/{F}/`, e o diff desde o merge-base (`git diff --numstat <merge-base>`, com o que ainda não foi commitado, e os arquivos novos fora do git pelo `--no-index`), fora dos documentos do SDD (`sdd/features`, `reports`, `reviews`, `handoffs`, `releases`, `archive`, `curadoria`, `traces`, `contexto`) e do `CHANGELOG.md`, com até 3 arquivos e até 100 linhas (somadas as adicionadas e as removidas), sem binário. Exit 0 curta · 1 completa · 2 git falhou · 64 uso. O ledger guarda a trilha; a FASE 3 a lê de lá, e na trilha curta roda `handoff-lint.py --curta` (reprova a ficha com mais de 20 linhas).

**Rationale:** o ledger já é a fonte determinística e já entra no commit atômico; a FASE 3 lê um fato gravado em vez de lembrar.

**Alternatives Rejected:**
1. Medir na FASE 3 com o SHA de antes do push — rejeitada porque depende de lembrar um SHA entre sessões.

**Consequences:** o esquema do ledger ganha um campo opcional (`references/ledger.md`); ledger antigo sem o campo vale como `completa`.

---

### Decision 7: A curadoria muda de lugar; o texto do 17b vira `sdd-playbook/references/lote.md`

| **Status** | Accepted | · | **Date** | 2026-11-16 |
|------------|----------|---|----------|------------|

**Context:** as 4 garantias da curadoria são texto de skill conferido por `tests/test_f14_textos.py` (o recorte `17b. … 18.`).

**Choice:** o procedimento (staging, despacho, fronteira, `--conferir-bloco`, contagem entra e regra pergunta, aplicar e conferir 3 vezes, evidência, commit, recibo e envio) vai para `references/lote.md`, adaptado ao lote (várias entradas, `--conferir-entrada` no lugar do `--preparar`/`--colher`, `--registrar` no lugar do `grep … >> CURATOR-colhidos.txt`). Os testes da F14 passam a recortar esse arquivo. O exemplo da curadoria sai do `como-falar.md` da release e vai para o da `sdd-playbook`. O brief do curador e o `WORKFLOW_CONTRACTS.yaml` passam a dizer "lote da `sdd-playbook`".

**Rationale:** "mudam de lugar mas não somem": as mesmas frases e os mesmos testes, apontados para o lugar novo.

**Alternatives Rejected:**
1. Reescrever o procedimento do zero — rejeitada porque cada frase dele veio de uma correção com teste.

**Consequences:** a `sdd-release` cai de 500 para cerca de 410 linhas; o `sdd-fluxo.sh` (que a `feat/f23b3-cadeia-revisao` também altera) **não** muda: o despacho `curador` continua igual.

---

### Decision 8: A tabela "Depois do push" é o contrato entre a skill e o que se diz ao aluno

| **Status** | Accepted | · | **Date** | 2026-11-16 |
|------------|----------|---|----------|------------|

**Context:** item 6 do escopo; o modelo é a tabela do pré-voo da `sdd-new-session`, conferida por `tests/test_matriz_new_session.py`.

**Choice:** cada etapa das FASES 2 a 4 da `sdd-release` começa por `N. **<Nome>.**`. Em `references/como-falar.md`, a seção `## Depois do push — o que é cada etapa` tem a tabela `| Etapa | Para que serve | Sem ela | Agora ou pode esperar |`, com o nome em negrito na 1ª coluna, igual ao da skill. O teste confere os dois sentidos, as 4 colunas preenchidas, e que nenhuma célula cita número de passo (`passo \d`, `item \d`, `\d+[a-z]?\.`). A skill manda: ao entrar no pós-push, uma frase por etapa (a coluna "Para que serve"); a linha inteira quando a pessoa pede ou responde "não sei".

**Rationale:** o nome é a chave que liga skill e tabela; o teste acusa a etapa nova sem explicação e a explicação órfã.

**Alternatives Rejected:**
1. Explicação dentro de cada item da skill — rejeitada porque a skill é instrução para o agente, e o texto do aluno mora no `como-falar.md` (padrão de todas as skills).

**Consequences:** renomear uma etapa obriga a renomear a linha da tabela, de propósito.

---

## File Manifest

| # | File | Action | Purpose | Agent | Dependencies |
|---|------|--------|---------|-------|--------------|
| 1 | `sdd/bin/playbook-curator.sh` | Modify | `--enfileirar`, `--fila`, `--conferir-entrada` (com a proveniência), `--registrar`; `JA_JULGADO` diz "já julgada ou já na fila"; o `--self-test` continua verde (os casos novos ficam em `tests/test_f24_release_enxuta.py`) (AT-001 a AT-005, AT-010) | (general) | None |
| 2 | `sdd/bin/ficha-publicado.py` | Create | bloco `## Publicado` a partir dos ledgers, idempotente (AT-008) | (general) | None |
| 3 | `sdd/bin/trilha.sh` | Create | trilha curta ou completa (AT-009) | (general) | None |
| 4 | `.agents/skills/sdd-release/scripts/push-de-papel.py` | Create | o push com estes arquivos publica? (AT-006) | (general) | None |
| 5 | `sdd/bin/handoff-lint.py` | Modify | aceita o bloco Publicado (≥1 linha) como histórico; `--curta` reprova a ficha com mais de 20 linhas (AT-009) | (general) | 2 |
| 6 | `sdd/templates/HANDOFF_TEMPLATE.md` | Modify | seção `## Publicado` com os marcadores; "Histórico de slices" só com o que o ledger não diz (AT-008) | (general) | 2 |
| 7 | `.agents/skills/sdd-playbook/references/lote.md` | Create | o procedimento do lote (o 17b mudado de lugar) (AT-003, AT-004) | (general) | 1 |
| 8 | `.agents/skills/sdd-playbook/SKILL.md` | Modify | etapa "Lote", gatilho "rode o lote", papel Curator no lote; versão 2.3.0 (AT-003) | (general) | 7 |
| 9 | `.agents/skills/sdd-playbook/references/curator.md` | Modify | quem despacha é o lote; a colheita vem do `--conferir-entrada` (AT-003) | (general) | 7 |
| 10 | `.agents/skills/sdd-playbook/references/como-falar.md` | Modify | o exemplo da curadoria (perguntas D3, recibo, envio D1), vindo da release (AT-003, AT-004) | (general) | 7 |
| 11 | `.agents/skills/sdd-release/SKILL.md` | Modify | trilha no pré-voo; linha do papel no OK; FASES 2 a 4 novas; "Quando pular o SDD formal"; versão 2.16.0, porque a F23B3 publicou a 2.15.0 (AT-001, AT-005 a AT-009) | (general) | 1, 2, 3, 4 |
| 12 | `.agents/skills/sdd-release/references/como-falar.md` | Modify | tabela "Depois do push"; tira o exemplo da curadoria; exemplo do bloco do OK com a linha do papel (AT-011) | (general) | 11 |
| 13 | `.agents/skills/sdd-release/references/ledger.md` | Modify | campo `trilha:` (AT-009) | (general) | 3 |
| 14 | `.agents/skills/sdd-handoff/SKILL.md` | Modify | bloco Publicado gerado; na release, só Falta e alertas; limpeza sem oferta quando chamada pela release; versão 2.3.0 (AT-008) | (general) | 2 |
| 15 | `sdd/WORKFLOW_CONTRACTS.yaml` | Modify | `curador.activation` = lote da `sdd-playbook` (AT-003) | (general) | 7 |
| 16 | `sdd/invariants.md` | Modify | "quem escreve é o lote de curadoria da `sdd-playbook`" (AT-003) | (general) | 7 |
| 17 | `docs/playbook-curation.md` | Modify | fila e lote (EN) | (general) | 1, 7 |
| 18 | `docs/pt-BR/playbook-curation.md` | Modify | fila e lote (PT) | (general) | 1, 7 |
| 19 | `docs/pt-BR/guia-do-aluno.md` | Modify | a linha "Depois de publicar" (AT-011) | (general) | 11 |
| 20 | `docs/cli-conventions.md` | Modify | exits dos modos e scripts novos | (general) | 1, 2, 3, 4 |
| 21 | `sdd/fixtures/f24/` | Create | projeto com playbook e invariantes; 2 publicações da mesma feature; colheita que falha; bloco reprovado; entrada com linha plantada; 3 ledgers (1 ilegível); workflows com e sem `paths-ignore`; repositórios de diff pequeno e grande (montados no teste) | (general) | None |
| 22 | `tests/test_f24_release_enxuta.py` | Create | AT-001 a AT-011 | (general) | 1, 2, 3, 4, 5, 6, 7, 8, 11, 12, 21 |
| 23 | `tests/test_f14_textos.py` | Modify | recorta `lote.md` no lugar do 17b; os mesmos trechos (AT-011, não-regressão das garantias) | (general) | 7, 10, 11, 12 |
| 24 | `tests/test_contrato_build_release.py` | Modify | versão 2.15.0 da `sdd-release` e rótulos do bloco do OK | (general) | 11 |
| 25 | `MANIFEST.txt` | Modify | os arquivos novos do pacote | (general) | 2, 3, 4, 7, 21, 22 |

**Total Files:** 25

Outros testes de texto que citam o 17b, o passo 18 ou a curadoria na release (`test_docs.py`, `test_fluxo.py`, `test_gerar_starter.py`, `test_sdd_open.py`, `test_decisoes_lint.py`) são conferidos no build pela suíte; o que mudar entra com o motivo no BUILD_REPORT.

---

## Landmines aplicáveis

| Landmine (⛔) | Fonte | Veredito | Como / Por quê |
|---------------|-------|----------|----------------|
| gate que confere só fiação | LM-001 | ✔ tratado | os testes executam os scripts com fixtures dos dois lados (fila acima e abaixo do limite, entrada plantada e íntegra, trilha curta e completa) |
| asserção sem baseline vermelho | LM-002 | ✔ tratado | o `cmd` chama `tests.test_f24_release_enxuta` pelo nome: sem o módulo, o gate fica vermelho; cada teste é rodado contra a árvore de antes |
| número longo barrado pelo publish-gate | LM-012 | ✔ tratado | nome da entrada `AAAAMMDDTHHMMSSZ` (8 dígitos seguidos); SHA de 7 caracteres no bloco Publicado; fixtures sem número de 11 dígitos |
| edição de teste por corte de âncora | LM-013 | ✔ tratado | `test_f14_textos.py` muda o recorte, não corta testes: a contagem de `def test_` antes e depois vai para o BUILD_REPORT |
| `subprocess` sem `encoding` no Windows | LM-014 | ✔ tratado | todo `subprocess` dos testes e do `ficha-publicado.py` (chama o `git`) passa `encoding="utf-8", errors="replace"` |
| saída do Python num pipe no Windows | LM-015 | ✔ tratado | `ficha-publicado.py` e `push-de-papel.py` reconfiguram stdout e stderr no início, como o `deploy-espera-testes.py` |
| fallback silencioso que esconde o caminho errado | LM-017 | ✔ tratado | `push-de-papel.py` sem o parser vizinho sai 64 com a causa, nunca `NAO_PUBLICA`; teste chama pelo caminho real |
| `PIPESTATUS` no zsh | LM-018 | ✔ tratado | a evidência do build é gravada por script `bash` com `rc=$?` |
| fonte de valor comparada com ela mesma | LM-024 | ✔ tratado | `trilha.sh` e `push-de-papel.py` recebem a branch padrão do slot `project.default_branch` e comparam com `origin/<ela>`; a release passa o mesmo valor ao `deploy-do-sha.sh` |
| `ls a b` para "algum existe" | LM-025 | ✔ tratado | `trilha.sh` testa `sdd/features/DEFINE_{F}.md` e `sdd/archive/{F}/DEFINE_{F}.md` com `[ -f ]`, um de cada vez; teste de cada caso |
| teste de texto que procura comando e deixa passar a obrigação em prosa | LM-026 | ✔ tratado | o teste da parada única procura também as frases de oferta ("oferecer", "ofereça", "quer que eu") nas FASES 2 a 4, não só a marca `[D` |
| juiz por regex de comportamento de LLM | LM-028 | N.A. | nenhum juiz de comportamento: os testes conferem scripts e texto de skill |
| `bash` sem caminho no Windows | LM-029 | ✔ tratado | o Python embutido do curador chama a colheita refeita por função, não por subprocesso; o teste chama os scripts pela constante de bash da suíte |
| executor que mascara o ambiente do aluno | LM-030 | ✔ tratado | os testes novos usam `tests/apoio.py` (lê em bytes, sem `PYTHONIOENCODING`) |
| PATH restrito no Windows | LM-034 | N.A. | nenhum teste tira ferramenta do PATH |

Varredura rodada em 2026-11-16 pelos termos do manifest (`playbook-curator`, `curadoria`, `colheita`, `sdd-release`, `ficha`, `ledger`, `workflow`, `paths-ignore`, `git mv`, `branch`, `teste de texto`, `regex`, `Windows`, `MANIFEST`, `exit`, `glob`, `CHANGELOG`, `trace`): 13 IDs, entradas inteiras lidas.

---

## Contrato de aceite

N.A. (1 camada: scripts do método e texto das skills; sem UI, banco ou serviço).

---

## Agent Assignment Rationale

| Agent | Files Assigned | Why This Agent |
|-------|----------------|----------------|
| (general) | 1 a 25 | o repositório não tem agentes especialistas; a fase Build faz direto |

**Agent Discovery:**
- Scanned: `.claude/agents/`, `.codex/agents/` (inexistentes no Open)

---

## Code Patterns

### Pattern 1: `--enfileirar` (dentro do programa Python do curador)

```python
def enfileirar(args):
    feature, inv = ...                                  # <FEATURE> [--inv <invariantes>]
    rc_prep, stg = preparar_staging(feature)            # o corpo do --preparar, sem o fim()
    if rc_prep == 1:
        fim("STAGING SEM DOCUMENTOS", 'registre "Curadoria: 0 deltas (sem documentos)"; nada foi enfileirado.')
        return 1
    fila = os.path.join(raiz, "sdd", "curadoria", "fila", feature)
    fps = set()                                         # o registro já veio para o staging pelo --preparar
    for e in entradas(fila):                            # pastas AAAAMMDDTHHMMSSZ, em ordem
        if rc_da_entrada(e) == 0:                       # só as boas: a falha nunca excluiu nada
            fps |= fps_de(os.path.join(e, "colheita.txt"))  # o que já está na fila não conta de novo
    escreve(os.path.join(stg, REGISTRO), "".join("fp=%s\n" % f for f in sorted(fps)))
    rc, saida = colher_em(stg, playbook, inv)           # mesma função do --colher; trace como hoje
    if (rc == 1 and nada_a_colher(saida)) or so_estado_do_playbook(saida):
        remove_entradas_falhas(fila)                    # a colheita terminou: cobre o que as falhas não colheram
        fim("NADA A COLHER", 'registre "Curadoria: 0 deltas"; nada foi enfileirado.')
        return 1
    destino = os.path.join(fila, agora_utc())           # AAAAMMDDTHHMMSSZ; colisão ⇒ +1 s
    copia_staging(stg, destino, ignorados_pelo_git)     # AVAL* ignorado ⇒ ausentes.txt
    escreve(os.path.join(destino, "colheita.rc"), "%d\n" % rc)
    if rc != 0:
        fim("COLHEITA FALHOU (rc=%d)" % rc, 'registre "Curadoria: FALHOU (rc=%d)"; a entrada fica na fila.' % rc)
        return 2
    remove_entradas_falhas(fila, exceto=destino)        # a colheita nova cobre o que elas não colheram
    diz("fila: " + os.path.relpath(destino, raiz))
    fim("ENFILEIRADO", "ponha a pasta da entrada no commit de papel; o lote a julga depois.")
    return 0
```

### Pattern 2: bloco gerado entre marcadores (idempotente)

```python
INI, FIM = "<!-- publicado:inicio (gerado por sdd/bin/ficha-publicado.py; não edite) -->", "<!-- publicado:fim -->"

def substitui_bloco(texto, linhas):
    bloco = INI + "\n" + "\n".join(linhas) + "\n" + FIM
    if INI in texto and FIM in texto:
        a, b = texto.index(INI), texto.index(FIM) + len(FIM)
        return texto[:a] + bloco + texto[b:]
    secao = "## Publicado\n\n" + bloco + "\n\n"
    i = texto.find("\n## Feito")                        # sem "## Feito": antes do 1º "## " depois de "## Ficha"
    return texto[:i + 1] + secao + texto[i + 1:] if i >= 0 else texto.rstrip("\n") + "\n\n" + secao
```

Linha: `- 2026-11-16 · s1 · v2.19.0 · shipado · PASS · deploy real · trilha completa · a1b2c3d`, a mais recente no topo. O SHA vem de `git log --diff-filter=A --format=%h -1 -- <ledger>`; sem git ou sem commit, `sha n/d`.

### Pattern 3: glob de `paths` do GitHub Actions

```python
def glob_para_regex(p):
    out, i = [], 0
    while i < len(p):
        if p.startswith("**", i):
            out.append(".*"); i += 2
            if p.startswith("/", i): i += 1; out[-1] = "(?:.*/)?"
        elif p[i] == "*": out.append("[^/]*"); i += 1
        elif p[i] == "?": out.append("[^/]"); i += 1
        else: out.append(re.escape(p[i])); i += 1
    return re.compile("^" + "".join(out) + "$")

def casa(arquivo, padroes):          # o último padrão que casa decide; "!" nega
    r = False
    for p in padroes:
        neg = p.startswith("!")
        if glob_para_regex(p[1:] if neg else p).match(arquivo):
            r = not neg
    return r
```

`paths` ⇒ dispara se algum arquivo casa; `paths-ignore` ⇒ dispara se algum arquivo não casa; os dois no mesmo evento, `branches` com padrão que o parser não entende, `workflow_run` ou workflow ilegível ⇒ `NAO_SEI`. Só conta o workflow que publica (o mesmo `publica()` e `PARECE_PUBLICAR` do `deploy-espera-testes.py`, importados por `importlib` do arquivo vizinho).

### Pattern 4: tabela "Depois do push" (como-falar.md da release)

```markdown
## Depois do push — o que é cada etapa

| Etapa | Para que serve | Sem ela | Agora ou pode esperar |
|---|---|---|---|
| **Push** | envia a versão aprovada para o GitHub; neste projeto, é o que publica | nada chega a quem usa | agora |
| **Colheita** | guarda o que esta feature ensinou, para ser julgado depois junto com outras | a lição se perde quando a pasta da frente for apagada | agora; o julgamento pode esperar |
```

---

## Data Flow

1. **Pré-voo:** `trilha.sh {F}` ⇒ `TRILHA:`; vai para o ledger.
2. **Antes do OK:** `push-de-papel.py . --branch {default_branch} <arquivos do papel>` ⇒ a linha "O commit de papel publica?".
3. **Depois do deploy e do smoke:** `playbook-curator.sh --enfileirar {F} [--inv]` ⇒ entrada na fila (ou `0 deltas`, ou `FALHOU`); `playbook-curator.sh --fila` ⇒ exit 10 e 1 linha quando passa de 5.
4. `ficha-publicado.py {F}` ⇒ bloco Publicado; o agente escreve Falta e alertas; ledger `estado: shipado` ⇒ `git mv` um a um.
5. Commit de papel ⇒ landar ⇒ push ⇒ branch remota da frente apagada se ancestral ⇒ relatório final.
6. **Lote (outro dia, numa frente nova):** `--fila` ⇒ por entrada `--conferir-entrada` ⇒ curador ⇒ `--conferir-bloco` ⇒ perguntas ⇒ um `--aplicar` ⇒ conferências ⇒ `--registrar <entradas julgadas>` ⇒ commit ⇒ `[D1]` envio.

---

## Integration Points

| External System | Integration Type | Authentication |
|-----------------|-----------------|----------------|
| git (local e remoto) | `git log`, `git check-ignore`, `git diff --numstat`, `git push origin --delete` | a do remoto, com `GIT_TERMINAL_PROMPT=0` |
| GitHub Actions | leitura de `.github/workflows/*.yml` | nenhuma (arquivo local) |

---

## Testing Strategy

| Test Type | Scope | Files | Tools | Coverage Goal |
|-----------|-------|-------|-------|---------------|
| AT-001 | `--enfileirar`: entrada criada, só colhe (sem despacho, sem playbook mexido); colheita que falha (playbook ilegível) ⇒ entrada com `colheita.rc` ≠ 0, exit 2, `FALHOU`; nada a colher ⇒ exit 1 sem entrada; texto da release sem despacho do curador | fixtures + `test_f24` | unittest | casos feliz e negativo |
| AT-002 | 2 `--enfileirar` da mesma feature sem lote ⇒ a 2ª só com as linhas novas; `--registrar` grava cada `fp` uma vez; aplicar as 2 entradas dá +1 por impressão | idem | unittest | contagem em dobro = 0 |
| AT-003 | lote sobre 2 entradas com blocos gravados: AUTO entra, PERGUNTA sai como pergunta; 2 `ADD` de entradas diferentes ⇒ IDs seguidos a partir do maior da base | idem | unittest + scripts | IDs sem colisão |
| AT-004 | bloco reprovado 2 vezes e `FORA:` no playbook ⇒ nada aplicado, entrada fica; log ignorado pelo git ⇒ `ausentes.txt`, a linha dele relatada e fora da comparação, o resto da entrada segue; texto do `lote.md` com o `[D1]` do envio | idem | unittest | 3 negativos |
| AT-005 | `--fila` com 5 e com 6 entradas | idem | unittest (matriz) | exit 0 sem linha · exit 10 com 1 linha |
| AT-006 | `push-de-papel.py`: sem `paths`, com `paths-ignore: [sdd/**, '**/*.md']`, com `paths: [src/**]`, `workflow_run`, workflow ilegível; texto do OK e do commit de papel | idem | unittest | PUBLICA · NAO_PUBLICA · NAO_SEI |
| AT-007 | texto: FASES 2 a 4 com 1 `[D` só (o smoke), sem "oferecer"/"ofereça"/prompt de retomada; apagar a branch remota só se ancestral; arquivamento por `estado: shipado`; recibo com o comando que desfaz | `test_f24` | unittest | — |
| AT-008 | `ficha-publicado.py` com 3 ledgers (1 ilegível) ⇒ 3 linhas, exit 2, resto da ficha intacto, 2ª execução igual byte a byte; texto da handoff e da release | idem | unittest | idempotência |
| AT-009 | `trilha.sh` em repositórios montados no teste: 2 arquivos/40 linhas sem DEFINE (curta, também sem commit), com DEFINE, com DEFINE arquivado, 4 arquivos, 101 linhas, binário (completa); ficha curta de fixture passa no `handoff-lint.py --curta`, e a de 21 linhas reprova | idem | unittest (matriz) | os 7 casos |
| AT-010 | entrada com linha `DELTA` plantada; entrada com documento mexido por um 2º commit; entrada fabricada inteira num commit só, com documento que nunca esteve no lugar dele ⇒ `ENTRADA RECUSADA`, exit 2 | idem | unittest | 3 negativos |
| AT-011 | tabela "Depois do push" × etapas das FASES 2 a 4 (os dois sentidos, sem número de passo); `test_f14_textos.py` repontado; suíte inteira, `--self-test` | `test_f24`, suíte | unittest | macOS + `testes-windows` |

---

## Error Handling

| Error Type | Handling Strategy | Retry? |
|------------|-------------------|--------|
| colheita falha na release | entrada com `colheita.rc`, `Curadoria: FALHOU (rc=N)` na ficha; a publicação segue | um `--enfileirar` novo, que apaga as entradas falhas da feature |
| entrada recusada no lote | nada aplicado dela; motivo no recibo; fica na fila | refazer com `--enfileirar` numa pasta com os documentos |
| bloco reprovado 2 vezes | nada aplicado dela; fica na fila | próximo lote |
| envio do commit de papel falha | commit fica na branch da frente; relatório com o comando; branch remota não é apagada | o comando do relatório |
| ledger ilegível | `n/d (ledger ilegível: …)`, exit 2; a ficha é gravada com as outras linhas | consertar o ledger e rodar de novo |
| workflow ilegível | `NAO_SEI` ⇒ "não consegui afirmar" no bloco do OK | — |

---

## Configuration

| Config Key | Type | Default | Description |
|------------|------|---------|-------------|
| — | — | — | nenhum slot novo (decisão do Roberto: sem modo opcional); limite da fila fixo em 5 |

---

## Segurança

1. **Onde mora cada segredo:** N.A. — nenhum segredo novo; os scripts só leem arquivos do projeto e o git.
2. **Quem vê e quem muda cada tabela (RLS):** N.A. — sem banco.
3. **Credencial de cada agente ou integração:** o curador continua sem escrita (fronteira de escrita + selo do staging); o push do commit de papel e o `git push origin --delete` usam a credencial de quem publica, cobertos pelo OK; o envio do lote pede `[D1]`.
4. **Cabeçalhos e CORS do host:** N.A. — sem host.
5. **Itens aplicados no Define:** S18 (instrução escondida em conteúdo externo) → o lote nunca julga a colheita guardada: `--conferir-entrada` refaz a colheita sobre as cópias da entrada e recusa a entrada quando as impressões diferem ou quando a pasta foi mexida depois do commit que a criou (Decision 3); o curador continua com a linha `CONTAMINAÇÃO:` e só 5 campos.

---

## Observability

| Aspect | Implementation |
|--------|----------------|
| Logging | o trace da colheita (`sdd/traces/<F>.jsonl`, `src: curator`) continua; a colheita refeita no lote roda com `SDD_TRACE=off` para não contar 2 vezes |
| Metrics | `--fila` diz quantas entradas e de quais features |
| Tracing | — |

---

## Advisor Ledger

Rodada 1 (2026-11-16, `EXTERNAL_REVIEW_20261116-191150`, `--paths` DEFINE + DESIGN): claude revisa (US$ 0,7630 nominal, assinatura), openrouter qwen/qwen3.7-plus audita (US$ 0,0281), codex desempata (assinatura). O auditor discordou de R1 e R2, concordou de R3 a R6 e trouxe N1; o desempate refutou R1.

| # | Nota | Severidade | Veredito | Evidência |
|---|---|---|---|---|
| R1 | o diff não traz implementação nem o módulo de teste do Verify Gate | HIGH | REBATIDA_ESCOPO | a revisão é do DESIGN (`--paths` DEFINE + DESIGN); o código vem no build, e o módulo ausente é o baseline vermelho declarado no DEFINE (Verify Gate › Cobertura); desempate: REFUTADO |
| R2 | DEFINE e DESIGN no diff, contra a Constraint de não ir para a `main` | HIGH | REBATIDA_EVIDENCIA | os artefatos ficam sem commit nesta branch (DEFINE › Constraints › Process); o diff os leva porque o `adversarial-review.sh` inclui os não rastreados com `--paths`; o gate roda de `git archive HEAD`, que só leva o commitado |
| R3 | entrada fabricada inteira passa no `--conferir-entrada` | MED | APLICADA | Decision 3, passo (3): proveniência de cada documento copiado por `git log --find-object` nos caminhos de origem; AT-010 e Testing Strategy com o caso fabricado |
| R4 | impressões de entrada falha somem sem julgamento | MED | APLICADA | Decision 2: só entradas boas excluem; colheita que termina (entrada nova ou `NADA A COLHER`) apaga as falhas; Pattern 1 |
| R5 | evidência ausente por linha (Decision 1) × por entrada (AT-004) | MED | APLICADA | por linha: AT-004 do DEFINE reescrito; Decision 1 › Consequences; Testing Strategy |
| R6 | trilha curta com DEFINE arquivado: AT-009 × Decision 6 | LOW | APLICADA | AT-009 do DEFINE cita `sdd/archive/<F>/` |
| N1 | limite de 20 linhas da ficha curta sem conferência | MED | APLICADA | `handoff-lint.py --curta` (manifest 5), rodado na trilha curta (Decision 6); AT-009 |

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-11-16 | design-agent | Initial version |
| 1.1 | 2026-11-16 | design-agent | Revisão do DESIGN, rodada 1: R3 a R6 e N1 aplicados; R1 e R2 rebatidos. Medido no build adiantado: a colheita só de promoção pendente não entra na fila (Decision 2); a trilha exclui só os documentos do SDD e conta o não commitado (Decision 6) |

---

## Next Step

**Ready for:** `/sdd-build sdd/features/DESIGN_F24_RELEASE_ENXUTA.md`
