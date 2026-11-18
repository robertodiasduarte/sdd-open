# DESIGN: F14 Playbook, invariantes e sessão

> Technical design for implementing F14 Playbook, invariantes e sessão

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | F14_PLAYBOOK |
| **Date** | 2026-11-05 |
| **Author** | SDD Design by RDD |
| **BRAINSTORM** | `sdd/features/BRAINSTORM_F14_PLAYBOOK.md` |
| **DEFINE** | `sdd/features/DEFINE_F14_PLAYBOOK.md` (v1.7) |
| **UX REVIEW** | `sdd/reviews/UX_REVIEW_F14_PLAYBOOK.md` (U1–U14) |
| **LLM Prompts** | false |
| **Status** | Ready for Build |

---

## Architecture Overview

```text
 sdd-release 2.7.0, passo 17b (depois do push)                 sdd-new-session 1.4.0
 ─────────────────────────────────────────────                 ─────────────────────
 playbook-curator.sh --preparar F                              copiar-docs.sh <principal> <frente> <slug>
   │  copia DESIGN, BUILD_REPORT, AVAL*.log, AVALIACAO,          │  nome idêntico → COPIADO
   │  ledger e HANDOFF para a pasta de staging                   │  só parecido   → PARECIDO (não copia)
   ▼                                                             ▼
 --colher STG sdd/playbook.md [--desde] [--inv]                RESULTADO: N COPIADO(S) | NADA A COPIAR
   │  0 há o que julgar · 1 nada · outro exit FALHOU (para)
   ▼
 --selar (sha do staging, guardado fora dele)
 governanca-fronteira.sh --snapshot ──► curador (contexto fresco; brief references/curator.md; 5 campos)
   │                                      │ sem subagente: sdd-fluxo.sh despachar curador → exit 40
   ▼                                      ▼
 governanca-fronteira.sh --comparar ◄── bloco CURADORIA
   │  escreveu algo → descarta, redespacha 1 vez
   ▼
 --conferir-bloco colheita bloco playbook selo comparar
   │  2 → redespacha 1 vez · 0 → linhas AUTO e PERGUNTA
   ├─ AUTO ────────────────────────────────► delta.txt (sem pergunta; vai para o recibo)
   └─ PERGUNTA ► [D3 · muda a regra do método] ► aceitos ► delta.txt
                   --cruzar: aposentadoria que mexe em invariante = opção única
   ▼
 --aplicar delta.txt sdd/playbook.md > novo.md
   │  playbook-lint.sh novo.md → --anti-collapse → --aplicar-inv > inv.md → --validar-inv novo.md inv.md
   ▼
 copia por cima · CURATOR-colheita.log · CURATOR-delta.log · CURATOR-colhidos.txt · commit à parte
   ▼
 [D1 · não se desfaz] enviar o commit da curadoria? → aterrissa na base, lint e trava de novo, push
```

Nada muda em `sdd/hooks/`, `report-lint.py`, `verify-gate.sh` nem `adversarial-review.sh`. `governanca-fronteira.sh` e `governanca-bloco.py` mudam pela revisão focada (Decision 12).

---

## Components

| Component | Purpose | Technology / Pattern | Inputs | Outputs | Dependencies |
|---|---|---|---|---|---|
| `playbook-curator.sh` | preparar, colher, aplicar, cruzar, travar, gravar invariantes, selar e conferir o bloco (P1, C5, P2, P4) | bash 3.2 que entrega tudo a um núcleo Python stdlib embutido | pasta de staging, playbook, invariantes, delta, bloco | linhas de colheita, playbook novo, avisos, vereditos; exit 0/1/2/3/64 | `playbook-lint.sh` só no self-test |
| `sdd/invariants.md` | registro das regras permanentes (C5) | Markdown, 1 linha por invariante | curadoria | arquivo lido pela trava | `sdd/playbook.md` |
| Brief do curador | papel que julga e nunca escreve (P2) | `references/curator.md` da `sdd-playbook` | 5 campos | bloco de curadoria | `governanca-fronteira.sh`, `sdd-fluxo.sh` |
| Passo 17b | liga as peças na release (P3, P4) | texto da `sdd-release` | artefatos da feature | playbook e invariantes atualizados, evidência, commit | todos acima |
| `copiar-docs.sh` | leva os documentos de papel para a frente (N1) | bash 3.2 + git | checkout principal, pasta da frente, slug | linhas por arquivo; exit 0/2/64 | git |
| `HANDOFF_TEMPLATE.md` | molde com as 6 seções que faltavam (N3) | Markdown | — | ficha | `handoff-lint.py` |
| Consertos | `SDD_TRACE` nos testes, 2 lints, piso do anti-collapse, fronteira e restauração do DEFINE | Python e bash | — | — | — |
| Docs | explicam a curadoria | Markdown EN + PT | — | `docs/playbook-curation.md` | `tests/test_docs.py` |

---

## Key Decisions

### Decision 1: Um script bash com o núcleo em Python embutido, sem exigir git

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-11-05 |
| **Source** | DEFINE AT-001 a AT-022, AT-040; fonte no privado (724 linhas, bash + awk) |

**Context:** a fonte é awk dentro de bash e usa intervalo de repetição no awk, que o mawk do Ubuntu pode recusar; ela exige repositório git e faz `cd` para a raiz. Os testes do pacote rodam numa cópia de `git archive`, sem `.git`. O `sdd-fluxo.sh` já resolveu o mesmo problema com um núcleo Python stdlib num heredoc.

**Choice:** `sdd/bin/playbook-curator.sh` confere `python3` e passa os argumentos a um heredoc `python3 -B -`, com o caminho do próprio script numa variável de ambiente para o self-test se chamar. O núcleo lê e grava UTF-8 explícito, nunca depende de locale, não importa nada fora da stdlib e não usa sintaxe posterior ao Python 3.9. Caminhos são relativos à pasta de quem chama; a raiz do projeto (só para o trace e para o `--preparar`) é o `git rev-parse --show-toplevel` quando existe e a pasta atual quando não. As seções aceitas vêm de `PLAYBOOK_SECTIONS`, com o mesmo default do `playbook-lint.sh`; um teste compara os 2 defaults. Saídas: 0, 1, 2, 3 e 64, como na fonte. Todo modo menos o `--aplicar` termina o stdout com `RESULTADO:` e uma linha `→`; erro de uso manda os dois para stderr e sai 64.

**Rationale:** um parser só, testável e igual em macOS e Ubuntu; sem git, roda na cópia do gate.

**Alternatives Rejected:**
1. Porte literal em awk — risco de mawk e de BSD awk com UTF-8, que já custou rodadas na F13.
2. Script Python puro em `sdd/bin/` — os mecanismos do pacote chamados pelas skills são `.sh`, e o privado troca por nome na F15.

**Consequences:**
- `python3` passa a ser requisito do curator, como já é do `sdd-fluxo.sh`.
- O self-test chama o `playbook-lint.sh`, que exige git: fora de um repositório ele falha dizendo isso.

### Decision 2: O que a colheita lê e o que ela imprime

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-11-05 |
| **Source** | DEFINE AT-001 a AT-010, AT-019; P1 do plano |

**Context:** a fonte lê a memória do agente (`project_handoff_*`) e sugere mecanismos com caminhos do privado. No Open, a ficha mora em `sdd/handoffs/` e o avaliador grava `AVALIACAO_*.md`.

**Choice:** `--colher <dir> <playbook> [--desde AAAA-MM-DD] [--inv <invariantes>]` lê só o nível de cima de `<dir>`:
- tabelas das 2 seções de landmines (a do DESIGN e a do BUILD_REPORT), lidas pelo cabeçalho: o ID vem da coluna `Fonte`, `LM-nnn` ou `ID`, e o veredito da coluna `Veredito` ou `Tratamento`, que começa com `✔` (ajudou) ou com a palavra `mordeu` (mordeu); o resto não conta. Sem essas colunas, nada conta, e a tabela sai como `TABELA_SEM_CABECALHO`. A fonte casava por conteúdo porque a tabela tem 2 formas; 2 ciclos do avaliador mostraram que adivinhar a célula erra, e o cabeçalho resolve as 5 formas reais;
- linhas de achado em `AVAL*-*.log`, `AVALIACAO_*.md`, `*.yaml`, `BUILD_REPORT_*.md` e `HANDOFF_*.md`, fora daquelas tabelas: marca `❌`, `NEEDS_WORK`, `FAIL` (também `FAILED`, `FAILURE`, `FAILURES`) como palavra inteira, `WAIVED` ou `mordeu_antes:`, sem `✅` na linha. Com `LM-nnn` vira `DELTA … mordeu+1`; sem ID, e com um termo de `sup:` de 6 ou mais caracteres que não seja só dígitos, vira `SUGESTAO`;
- blocos de candidato em `BUILD_REPORT_*.md` e `HANDOFF_*.md`: `CANDIDATO` com o próximo ID (maior entre ativos e tombstones, mais 1) e a linha `delta: ADD`, ou `REJEITADO` com o motivo;
- o próprio playbook: `PROMOVER?` para ativo com `mordeu` de 2 para cima e `promovido_para: —`, com a sugestão fixa `hook em sdd/hooks/, comando de release.landmines_cmd ou asserção no Verify Gate, com um caso que falha antes`.

Um delta por ID e tipo; ID citado que não é bullet ativo sai `IGNORADO` uma vez; com `--desde`, arquivo de data anterior sai `JA_COLHIDO`. A última linha antes do `RESULTADO:` é `resumo: deltas=N (ajudou=A mordeu=M) candidatos=C rejeitados=R promocoes=P sugestoes=S`. Toda linha a julgar leva `fp=` (impressão do arquivo, do tipo, do ID e do texto da linha, sem o número da linha); o que está em `CURATOR-colhidos.txt` na pasta sai como `JA_JULGADO` e não conta. Campo `promovido_para:` ausente vale como `—`, e a crase em volta do caminho não faz parte dele. Exit 0 com pelo menos 1 linha de qualquer tipo, 1 sem nenhuma, 2 para playbook ou invariantes ausentes ou sem bullet, 64 para uso ou pasta ausente. Trace: 1 linha JSONL por feature da pasta em `SDD_TRACE_DIR` (default `sdd/traces` na raiz), `src` `curator`, `kind` `colher`, no arquivo `<F>.jsonl`, com `ts`, `feature`, `src`, `kind`, `exit` e os 7 contadores; `SDD_TRACE=off` não grava; falha de gravação nunca muda o exit.

**Rationale:** as regras são as medidas no privado (cada uma nasceu de um caso real registrado no cabeçalho da fonte); mudam as fontes, a sugestão e a leitura da tabela, que passa a ser pelo cabeçalho.

**Alternatives Rejected:**
1. Colher recursivamente — arrastaria evidência de outra feature.
2. Sugestão de mecanismo por seção — as seções são configuráveis no Open; a lista fixa de 3 destinos vale para qualquer uma.

**Consequences:**
- Quem tem achado em arquivo de outro nome não é colhido; o doc diz quais nomes valem.
- A linha de resumo fica antes do `RESULTADO:`; quem lia "a última linha" no privado ajusta na F15.

### Decision 3: `--preparar` faz o staging por cópia numa pasta refazível

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-11-05 |
| **Source** | DEFINE AT-024, AT-041; P4 do plano; UX lente L3 |

**Context:** no privado o staging é um parágrafo com `cp` e glob. Glob arrasta feature de nome parecido, e uma pasta de `mktemp` se perde quando a sessão para no exit 40.

**Choice:** `--preparar <F>` valida o nome com o alfabeto do `sdd-fluxo.sh despachar` (letras, números, `_`, `-`), cria a pasta `<temp>/sdd-curadoria-<12 hex do sha1 da raiz>/<F>/`, **apaga o que sobrou da release anterior** e copia, só arquivo regular e nunca link: `DESIGN_<F>.md` e `BUILD_REPORT_<F>.md` (de `sdd/features`, `sdd/reports` ou `sdd/archive/<F>/`, porque o passo 15b pode ter movido), `sdd/reports/evidence/<F>/AVAL*-*.log`, `AVALIACAO_<F>_<8 dígitos>*.md`, `sdd/releases/<F>/*.yaml` e `CURATOR-colhidos.txt`, e `sdd/handoffs/HANDOFF_<F>.md`. Imprime `staging: <pasta>`, uma linha por arquivo e o `RESULTADO:`. `--retomar` não copia nem limpa: diz se há colheita (sessão nova depois da parada). Os originais nunca são movidos nem editados. Exit 0; 1 sem DESIGN nem BUILD_REPORT (não é "0 deltas"); 64 para nome inválido; 2 se a pasta não pôde ser criada.

**Rationale:** a regra "cópia, nunca `mv`" vira comportamento testável; o nome refazível deixa a sessão seguinte achar a colheita.

**Alternatives Rejected:**
1. Deixar o `cp` no texto da skill — é a parte que o agente erra (glob, `mv`).
2. Staging dentro do projeto — apareceria no `git status` e no snapshot da fronteira.

**Consequences:**
- A pasta fica em disco até o sistema limpar o temporário; ela só tem cópias.

### Decision 4: `--aplicar` valida tudo antes e deixa o stdout puro

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-11-05 |
| **Source** | DEFINE AT-011 a AT-013; UX U9 |

**Context:** o stdout do `--aplicar` é o arquivo novo; qualquer linha a mais corrompe o playbook.

**Choice:** gramática de 1 verbo por linha, com `#` de comentário: `LM-nnn ajudou+N`, `LM-nnn mordeu+N`, `LM-nnn promovido_para=<caminho sem espaço>`, `ADD <seção> :: sup: <termos em crase> :: <regra com Do instead:>`, `TOMBSTONE LM-nnn :: <motivo>`, `REFINE LM-nnn :: <texto com Do instead:>`. A validação percorre o delta inteiro e junta os erros com o número da linha; com 1 erro, exit 2 e nada em stdout. Sem erro: contadores somados, `conf=` renovada nos bullets tocados (3º argumento `AAAA-MM-DD` ou `conf=AAAA-MM-DD`, default hoje), `ADD` no fim da seção com o próximo ID (seção da lista que falta nasce no lugar certo: o playbook do pacote só traz as 2 obrigatórias), `TOMBSTONE` tira o bullet e as continuações dele e acrescenta a linha `☠` no fim da seção de tombstones, `REFINE` troca o texto depois de `::`. `RESULTADO:` e `→` vão para stderr. A mesma função de validação serve ao `--cruzar` e ao `--conferir-bloco`.

**Rationale:** uma gramática só, 3 consumidores.

**Alternatives Rejected:**
1. Editar o arquivo no lugar — tira do passo 17b a chance de rodar o lint antes de copiar.

**Consequences:**
- Seção vazia que recebe `ADD` ganha o bullet logo abaixo do título.

### Decision 5: Invariantes com a trava dentro do curator

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-11-05 |
| **Source** | DEFINE AT-014 a AT-019; abordagem A do brainstorm; UX U5, U8 |

**Context:** a trava do privado roda um gerador de catálogo que o Open não tem. O que ela garante são 4 coisas: gramática, origem viva, universo classificado e ID único.

**Choice:** `sdd/invariants.md` com a gramática do DEFINE. Universo = ativos com `mordeu` de 1 para cima ou `promovido_para` preenchido. `--validar-inv <playbook> <invariantes>` reprova, uma linha `🔴 trava INV:` por defeito: linha fora da gramática abaixo da 1ª invariante; ID repetido; `auto` sem `· tarefa:`; `humano` sem `· motivo:`; `ok` sem `check=` e sem origem promovida; `check=` cujo caminho não existe a partir da pasta atual; origem que é tombstone ou não existe; descartado que é tombstone; bullet do universo que não é origem nem descartado. Quando só há bullets sem classificação, a 1ª linha diz que o registro é novo na v2.6.0 e quantas lições faltam. `--aplicar-inv <linhas> <invariantes>` é o único que grava as invariantes: troca a linha do mesmo ID, acrescenta as novas, remove com `REMOVER <id>` e imprime o arquivo novo (revisão, D6). `--cruzar <delta ou -> <playbook> <invariantes>` é só leitura: valida o delta, agrega as aposentadorias por invariante e imprime `INV_AFETADA` com `ajuste:` (lista sem a origem; origem única vira `origem=seed`, com `check=` vindo do `promovido_para` do bullet aposentado; sem saída válida, diz isso) e `ou: retirar o TOMBSTONE`; para descartado aposentado, `INV_AFETADA descarte`; para bullet que entra no universo, `INV_PENDENTE` com a proposta A (ID seguinte ao maior, em sequência) e a B. `resumo-inv: afetadas=N pendentes=M`; exit 3 com aviso, 0 sem, 2 inválido. O `sdd/invariants.md` do pacote nasce com 1 invariante de origem LM-004 (migration provada por leitura, check derivado do `promovido_para` dela). Num projeto que já tem o seu playbook, o `init` instala só o esqueleto, sem essa linha: a LM-004 dele pode não existir ou ser outra lição (revisão, D1).

**Rationale:** a trava não depende de apresentação; a regra do `check=` existente impede "ok" apontando para arquivo que saiu.

**Alternatives Rejected:**
1. Portar o gerador de catálogo — corte YAGNI do brainstorm.
2. Trava só para o que o delta muda — deixaria passar invariante órfã já existente.

**Consequences:**
- No 1º uso, projeto com lições antigas no universo responde a 1 item por lição (U8).
- Sem `sdd/invariants.md` o passo pula o cruzamento e diz que pulou.

### Decision 6: `--conferir-bloco` é o juiz do bloco e decide o que entra sem pergunta

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-11-05 |
| **Source** | DEFINE AT-020, AT-021; P2 e P3 do plano |

**Context:** "toda linha da colheita aparece" e "aceitar exige `arquivo:linha`" são regras de texto no privado. Se o agente que conduz a release separasse à mão o que é contagem, uma contagem inventada chegaria ao playbook sem pergunta.

**Choice:** `--conferir-bloco <colheita> <bloco> <playbook> <selo> <comparar>` confere antes de tudo a fronteira (`FORA:` ou falta de `RESULTADO: SÓ O PERMITIDO MUDOU` no `<comparar>` reprovam) e o selo do staging gravado por `--selar` (arquivo mudado, novo ou sumido reprova, derivado ou não: entre o selo e a conferência, ninguém legítimo grava ali), porque a fronteira não vê o staging, que fica fora do worktree (revisão, D5). Depois lê o bloco entre `<<<CURADORIA` e `>>>` (exatamente 1 par), a tabela de 7 colunas (`#`, `Tipo`, `LM`, `Delta`, `Evidência`, `Em linguagem simples`, `Recomendação`) e as 4 linhas finais (`REJEITADOS:`, `NAO_JULGADO:`, `IGNORADOS/JA_COLHIDOS:`, `CONTAMINAÇÃO:`). Tipos: `contador`, `sugestao`, `add`, `refine`, `tombstone`, `promover`, `inv`. Recomendações: `AUTO`, `ACEITAR`, `DESCARTAR`, `NAO_JULGADO`, `PERGUNTA OBRIGATÓRIA`. Reprova com exit 2, um defeito por linha:
- cobertura: cada `DELTA` tem linha `contador` com o mesmo ID e verbo; cada `SUGESTAO` tem linha `sugestao` com o ID; cada `CANDIDATO` tem linha `add` com o ID proposto ou linha `refine` que cita `candidato #n`; cada `REJEITADO` aparece em `REJEITADOS:` pelo `arquivo:linha`; cada `PROMOVER?` tem linha `promover`; `IGNORADO` e `JA_COLHIDO` aparecem na linha própria; cada `INV_PENDENTE` tem linha `inv` com o ID;
- `AUTO` só em `contador`, e **igual** a uma linha `DELTA` da colheita: o mesmo ID, verbo, `+1` e `arquivo:linha`; `sugestao` confirmada usa `ACEITAR` e vira pergunta (revisão, D2);
- `ACEITAR` (menos em `inv`) pede a célula de evidência começando por `arquivo:linha`, com o arquivo presente na pasta da colheita e a linha dentro dele;
- `promover` só com `PERGUNTA OBRIGATÓRIA`;
- célula de linguagem simples vazia; linha `CONTAMINAÇÃO:` ausente; célula de delta fora da gramática (a da Decision 4, ou a de invariante em `inv`).

Válido: imprime `AUTO <delta>` por linha automática, `PERGUNTA <n> <tipo> <delta>` por linha de política recomendada `ACEITAR` ou `PERGUNTA OBRIGATÓRIA` (e por contador `mordeu` de lição com `INV_PENDENTE`, que decide junto com a classificação), `AVISO` quando a contaminação é `sim`, `resumo-bloco: auto=N pergunta=M descartar=K nao_julgado=J contaminacao=sim|nao` e o `RESULTADO:`. A pasta de staging é a do arquivo de colheita.

**Rationale:** o que entra sem pergunta é decidido por um programa que confere a colheita, não por quem conduz a release nem pelo curador.

**Alternatives Rejected:**
1. Confiar na coluna do curador — é o ponto A-001 das premissas.
2. Lista de jargão proibido — corte YAGNI; a coluna só precisa existir.

**Consequences:**
- O que entra sem pergunta é só o que o script colheu; a sugestão, mesmo confirmada, pergunta.

### Decision 7: Curador como brief, provado só-leitura pela fronteira

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-11-05 |
| **Source** | DEFINE AT-023, AT-038; UX U2; regra 10 do 8.0 |

**Context:** o agente do privado é um arquivo de agente de um vendor, com lista de ferramentas. No Open, papel fresco é brief em `references/` mais a escada de `contexto-fresco.md`.

**Choice:** `.agents/skills/sdd-playbook/references/curator.md` com: identidade (julga, não decide, não escreve); a entrada de 5 campos `feature`, `staging`, `colheita`, `playbook`, `worktree`; o processo por tipo de linha da colheita; o cruzamento com `--cruzar -` quando `<worktree>/sdd/invariants.md` existe; a coluna de linguagem simples em até 2 frases (o que aconteceu, o que muda); o bloco de retorno com as 7 colunas e as 4 linhas finais; a regra de contaminação. `sdd/WORKFLOW_CONTRACTS.yaml` ganha `curador` com `campos`, `tipos`, `recomendacoes`, `retorno`, `validador`, `fronteira`, `permitido`, `redespachos` e `falha`. O `sdd-fluxo.sh despachar` ganha o caso `curador`: o motivo da parada abre com `A publicação já terminou e não depende deste passo.`, o retorno pedido é o bloco de `<<<CURADORIA` até `>>>`, e o "não foi feito" é `a curadoria do playbook ainda não foi aplicada; nada foi despublicado.` Só-leitura: o brief é gravado em `sdd/reports/briefs/BRIEF_curador_<F>.md` antes do `governanca-fronteira.sh --snapshot`; depois do retorno, `--comparar` com o brief como único permitido. Saída diferente de 0 descarta o bloco e redespacha 1 vez.

**Rationale:** o mesmo mecanismo do revisor de governança, sem modo novo no script da fronteira.

**Alternatives Rejected:**
1. Arquivo de agente por vendor — fere a regra 10.
2. Confiar em "não escreva" — texto sem prova.

**Consequences:**
- O snapshot fica em `<temp>/sdd-fronteira-<hash>/<F>/curador/`, como os outros 2 papéis.

### Decision 8: Passo 17b reescrito, com 2 perguntas possíveis depois do push

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-11-05 |
| **Source** | DEFINE AT-024, AT-025; UX U1 a U6, U8, U12; P3 e P4 do plano |

**Context:** hoje o 17b é 1 parágrafo, e o commit do playbook fica na branch da frente sem dizer como chega à branch padrão. No privado ele é enviado sem pergunta, porque lá o push desses arquivos não publica nada. No Open isso não vale para todo projeto: no próprio sdd-open, um push em `main` que toca `sdd/playbook.md` publica uma Release.

**Choice:** o 17b vira uma lista numerada, na ordem do AT-024, com os comandos exatos. Pontos de decisão:
- colheita com saída 1: registra `Curadoria: 0 deltas`, diz à pessoa que a feature não trouxe lição nem contagem, e termina;
- qualquer outra saída que não 0 ou 1: para o passo, registra `Curadoria: FALHOU (rc=N)` e diz a causa, o conserto e que a publicação não foi afetada;
- bloco reprovado 2 vezes, ou fronteira violada 2 vezes: `Curadoria: FALHOU (bloco inválido)`; nada é aplicado;
- linhas `AUTO` vão para o `delta.txt` sem pergunta e para o recibo, com 1 frase por contagem;
- linhas `PERGUNTA` viram perguntas `[D3 · muda a regra do método]`, uma por item, numeradas, em lotes de até 5, cada uma com `aceitar` (recomendada), `recusar` e `não sei`: é a forma que o `sdd-decisoes-lint.sh` lê, e o exemplo fica só em `references/como-falar.md`, porque o `SKILL.md` não pode ganhar pergunta (revisão, D10); aposentadoria que o `--cruzar` liga a uma invariante vem com o ajuste na mesma opção;
- aplicação numa cópia, 3 conferências, cópia por cima; anti-collapse reprovando por tamanho: aplicar em 2 ou mais commits (contadores e `ADD` primeiro; depois 1 mudança de conteúdo por vez);
- evidência: `CURATOR-colheita.log` e `CURATOR-delta.log` em `sdd/reports/evidence/<F>/`, no formato `$ comando`, saída, `[exit=N]`, e o registro `CURATOR-colhidos.txt` em `sdd/releases/<F>/`;
- commit só com `sdd/playbook.md`, `sdd/invariants.md` (se mudou), o registro e, se o projeto versiona evidência, os 2 logs;
- envio: pergunta `[D1 · não se desfaz]` **Posso enviar o commit da curadoria para a branch padrão?**, com a resposta do item 7 sobre o push publicar sozinho; `sim` aterrissa como no passo 5 (worktree temporário da base e cherry-pick; em conflito, reaplica o `delta.txt` sobre o playbook da base com `--aplicar`, em vez de resolver à mão), roda o lint e a trava de novo e faz o push; `deixar para a próxima publicação` mantém o commit na branch da frente e registra na ficha o comando de envio.

`references/como-falar.md` ganha o exemplo das 2 perguntas, o recibo e o glossário (curadoria, delta, aposentar, promover, invariante). A lista de abortos da skill não muda: a curadoria nunca aborta uma release já publicada.

**Rationale:** "um OK antes do push" continua verdadeiro para todo push; a contagem entra no arquivo sem pergunta, mas não sai da máquina sem um sim.

**Alternatives Rejected:**
1. Enviar sem pergunta, como o privado — publicaria uma Release do próprio sdd-open sem OK.
2. Rodar a curadoria antes do OK da release — os achados dispensados (`WAIVED`) só existem depois dele.
3. Nunca enviar — o commit se perde quando a branch da frente é apagada (defeito do texto atual).

**Consequences:**
- Release com contagem tem 1 pergunta a mais (o envio); com mudança de regra, 2 numeradas na mesma resposta.
- `tests/test_decisoes_lint.py` passa a contar 23 perguntas em 20 arquivos nas skills (3 no exemplo da curadoria).

### Decision 9: `copiar-docs.sh` na `sdd-new-session`

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-11-05 |
| **Source** | DEFINE AT-026 a AT-028; UX U7; N1 do plano |

**Context:** a skill do Open é só texto. A regra "só com nome idêntico" é o tipo de regra que vira `cp` com glob na mão do agente.

**Choice:** `.agents/skills/sdd-new-session/scripts/copiar-docs.sh <principal> <frente> <slug>`, bash 3.2. Para `sdd/features` e `sdd/reviews` do checkout principal, lista com `git -C <principal> ls-files --others -z` os arquivos `.md` do nível de cima não salvos no git (ignorados incluídos), mais, para avisar, os salvos no git que faltam na frente (`NAO_COPIADO`: commit ainda não enviado; revisão, D9); tira o prefixo `BRAINSTORM_`, `DEFINE_`, `DESIGN_`, `UX_REVIEW_` ou `GOVERNANCA_REVIEW_` (outro prefixo não entra); passa a feature para minúsculas sem acento, com hífen no lugar do que não é letra nem número, e compara com o slug. A pasta de destino nasce quando falta. Igual: copia se o destino não existe (`COPIADO`), senão `JA_EXISTE`. Um começa com o outro: `PARECIDO`, com os 2 nomes e o motivo. Link simbólico na origem ou pasta de destino que é link: `IGNORADO`. Termina em `RESULTADO: <N> COPIADO(S)` ou `RESULTADO: NADA A COPIAR` e uma linha `→` que diz onde copiar à mão quando houve parecido. Exit 0; 64 para argumento faltando, pasta inexistente ou `<principal>` fora de um repositório git; 2 se uma cópia falhar. O passo 2 da skill chama o script logo depois do `git worktree add` e repassa o resultado em palavras.

**Rationale:** cópia errada é pior que cópia ausente; o script nunca sobrescreve e nunca segue link.

**Alternatives Rejected:**
1. Só arquivo não rastreado e não ignorado, como o privado — projeto que ignora `sdd/features/` nunca teria cópia; na frente, o mesmo `.gitignore` vale.
2. Em `sdd/bin/` — o script só serve a esta skill, como o `deploy-espera-testes.py` na `sdd-release`.

**Consequences:**
- Documento salvo no git nunca é copiado: na frente, ele viraria uma segunda versão do mesmo arquivo.

### Decision 10: Molde do handoff com 6 seções a mais

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-11-05 |
| **Source** | DEFINE AT-029; UX U10; N3 do plano |

**Context:** o `handoff-lint.py` exige a ficha, o prompt de retomada e o histórico, e aceita seção a mais. O handoff real desta família usa eventos, recomendações, veredito, preparo, tarefas e publicação.

**Choice:** o molde ganha, entre a seção de testes em aberto e o prompt de retomada: `Eventos` (linha nova por mudança de escopo, nunca sobrescrita), `Recomendações`, `Veredito` (o da release, com o registro de dispensa quando houver), `Setup` (como preparar a pasta: base, worktree, dependências), `Tarefas` (numeradas, cada uma com "Pronto quando") e `Ship` (o que publicar e o que limpar). Cada uma com 1 linha de orientação e 1 exemplo de forma. Fixture `sdd/fixtures/handoff/HANDOFF_COMPLETO.md`, preenchida a partir do molde. A `sdd-handoff` ganha 1 frase dizendo que as 6 seções são preenchidas quando há o que dizer, e sobe para 2.1.2.

**Rationale:** o lint não muda; o molde passa a ter o que o handoff real já tem.

**Alternatives Rejected:**
1. Tornar as seções obrigatórias no lint — quebraria fichas existentes.

**Consequences:**
- Ficha antiga continua válida.

### Decision 11: Quatro consertos de pendência

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-11-05 |
| **Source** | DEFINE AT-030 a AT-032; handoff, etapas F12 e F13 |

**Context:** pendências 🐛 registradas, mais 1 achada neste Design: o `--anti-collapse` reprova qualquer mudança de conteúdo em playbook de até 4 bullets (1 de 4 são 25%), o que impediria promover ou aposentar no playbook do próprio pacote.

**Choice:**
- `tests/apoio.py`: o ambiente base da sandbox nasce sem `SDD_TRACE` e sem `SDD_TRACE_DIR`.
- `design-lint.py`: o título da seção de prompts aceita prefixo numérico com mais de um nível; um título de nível 2 que começa por essas 2 palavras no plural, traz palavras a mais e tem no corpo o subtítulo do inventário, um bloco de contrato ou uma coluna dele sai 1 com o título e o conserto (o corpo decide: a seção de mesmo começo sobre outro assunto é contrato da F13, em `tests/test_design_lint.py`, e continua passando); dentro de cada bloco de contrato, qualquer linha de tabela com chaves no valor (também entre crases) sai como "sem preencher".
- `prompt-drift-scan.sh`: `wrapper_pattern` sem aspas que começa com colchete, chave ou asterisco e a chave de prompts que abre mapa de fluxo em várias linhas saem 64 dizendo qual forma não é lida; o self-test ganha 1 caso para cada motivo de saída 64 que não tinha dente.
- `playbook-lint.sh --anti-collapse`: 1 bullet alterado sempre passa; o limite de 20% vale de 2 alterados para cima.

**Rationale:** defeito conhecido se corrige antes de construir por cima (P1).

**Alternatives Rejected:**
1. Deixar o anti-collapse como está e dividir em commits — 1 mudança não se divide.

**Consequences:**
- O privado tem a mesma regra dos 20%; a sincronização fica para a F15.

### Decision 12: Revisão focada da fronteira de escrita

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-11-05 |
| **Source** | DEFINE AT-033; risco aceito na F12 |

**Context:** 3 commits da F12 ligados à fronteira e à restauração do DEFINE não tiveram revisão externa própria, e cada rodada final achou um defeito ali. Esta frente passa a usar a fronteira num 3º papel.

**Choice:** antes de codar o 17b, um agente de contexto fresco revisa `sdd/bin/governanca-fronteira.sh`, o passo 11 da `sdd-define` (itens 2, 4 e 5) e `tests/test_governanca_fronteira.py`, executando sondas numa sandbox temporária, e grava `sdd/reviews/REVISAO_FRONTEIRA_F14_PLAYBOOK_20261105.md`. Cada HIGH ou MEDIUM é aplicado com teste dos 2 lados (o caso relatado e o caso legítimo vizinho) ou rebatido com motivo no BUILD_REPORT. Os arquivos que a correção tocar entram como drift do manifest.

**Rationale:** a correção vem antes do reuso.

**Alternatives Rejected:**
1. Deixar para a revisão adversarial da release — ela lê o diff, e esses arquivos podem nem estar nele.

**Resultado (build):** veredito NEEDS_WORK, 0 HIGH, 3 MEDIUM, 6 LOW. Aplicados: F1 (`governanca-bloco.py` reprova com `FORA:` ou sem o veredito verde), F2 (a cópia vem antes do `rm`), F3 (`#REF`, `#INDICE` e `#GIT` no snapshot), F4 (pasta que o git não abre sai 64), F8 (sem `sed` na lista do commit), F9 (texto da retomada). Ficam como pendência, LOW: F5 (repositório aninhado que já existia), F6 (só permissão em arquivo já sujo), F7 (grafia diferente do permitido, falso vermelho que só aparece com a chamada fora da skill).

**Consequences:**
- O manifest cresceu 8 arquivos (linhas 54 a 61): os do conserto, mais os 2 documentos de hooks.

### Decision 13: Instalação, gatilho de release e documentação

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-11-05 |
| **Source** | DEFINE AT-034, AT-035; UX U11 |

**Context:** o `init` instala os arquivos soltos de `sdd/` por uma lista (`playbook.md`, `WORKFLOW_CONTRACTS.yaml`); o `release.yml` publica por lista de caminhos.

**Choice:** `invariants.md` entra na lista do `bin/sdd-open.sh` (instala se falta, nunca sobrescreve; sem o playbook do pacote na mesma execução, só o esqueleto) e `sdd/invariants.md` na lista de `paths` do `release.yml`. `docs/playbook-curation.md` e a versão em português: o que é curadoria, um exemplo do início ao fim, a gramática do delta e das invariantes, as saídas do script e o que fica fora. READMEs com o link; `docs/cli-conventions.md` com as saídas e palavras novas; o guia do aluno com 1 parágrafo na ficha da `sdd-release`. O roadmap não muda: continua com 3 linhas.

**Rationale:** o mecanismo vem com o documento dele, como nas frentes F8 a F13.

**Alternatives Rejected:**
1. Mexer no `AGENTS.md.tmpl` — a regra 3 dele já manda nunca reescrever o playbook; as invariantes só são tocadas na curadoria.

**Consequences:**
- Projeto já instalado recebe o esqueleto de `sdd/invariants.md` no próximo `init`.

### Decision 14: Versões, contagens e Release

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-11-05 |
| **Source** | DEFINE AT-036; brainstorm, pergunta 3 |

**Context:** toda skill tocada sobe de versão e atualiza a linha de identificação; 3 testes fixam versões.

**Choice:** `sdd-playbook` 2.2.0, `sdd-release` 2.7.0, `sdd-new-session` 1.4.0, `sdd-handoff` 2.1.2, `sdd-define` 2.5.1, todas com `updated` de novembro de 2026 e a linha de identificação igual. A contagem de skills fica em 18. `tests/test_decisoes_lint.py` registra a contagem medida depois das 2 perguntas novas. Release `v2.6.0` por tag, com push atômico de `main` e da tag, depois do OK que cita "sdd-open".

**Rationale:** decisão do Roberto no brainstorm.

**Alternatives Rejected:**
1. Patch automático `v2.5.1` — recusado no brainstorm.

**Consequences:**
- A 2ª entrega parte da `v2.6.0`.

### Decision 15: Provas

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-11-05 |
| **Source** | DEFINE AT-037 a AT-039; brainstorm, pergunta 4 |

**Context:** o Codex ficou sem créditos no início desta sessão, e o Roberto os repôs durante o build (conferido com execução real); Gemini e Grok seguem sem login.

**Choice:**
- baseline: os arquivos de teste novos rodam numa cópia da `v2.5.0` e precisam falhar lá;
- sabotagem: 1 por script novo (`playbook-curator.sh`, `copiar-docs.sh`), com o teste que cai;
- avaliador de contexto fresco em modo `veredito`, até 2 ciclos; um 3º é pergunta `[D4 · limite de tentativas]`;
- revisão adversarial real: `--reviewer claude --auditor openrouter:qwen/qwen3.7-plus --revisor2 codex`, teto de 3 rodadas, `--conferir` no commit final;
- prova em agente de fora do Claude (AT-038), depois do último conserto, com arquivos de nome novo a cada execução: (a) passo 17b com a condição "sem subagente" e o efeito ` exited 40 in ` mais o brief no destino; (b) o brief do curador sobre as fixtures, conferido por `--conferir-bloco` e pela fronteira. O agente é o Codex CLI, com o modelo próprio dele; o mesmo CLI com modelo via OpenRouter fica como reserva.

**Rationale:** critério de efeito, nunca de texto; lição da F12 e da F13.

**Alternatives Rejected:**
1. Provar no próprio Claude Code — não testa o padrão agnóstico.

**Consequences:**
- Se os créditos acabarem de novo, a reserva evita parar a prova; o relatório diz qual modelo rodou.

---

## File Manifest

| # | File | Action | Purpose | Agent / Owner | Dependencies |
|---:|---|---|---|---|---|
| 1 | `sdd/bin/playbook-curator.sh` | Create | os 8 modos e o self-test (Decisions 1 a 6) | (general) | None |
| 2 | `sdd/invariants.md` | Create | registro com 1 invariante de origem LM-004 (Decision 5) | (general) | None |
| 3 | `sdd/fixtures/playbook/curadoria/DESIGN_FIXTURE.md` | Create | tabela de landmines de teste | (general) | None |
| 4 | `sdd/fixtures/playbook/curadoria/BUILD_REPORT_FIXTURE.md` | Create | 4 candidatos de teste | (general) | None |
| 5 | `sdd/fixtures/playbook/curadoria/AVAL-AT-002.log` | Create | achados de teste | (general) | None |
| 6 | `sdd/fixtures/playbook/curadoria/playbook-base.md` | Create | base do `--aplicar` e do próximo ID | (general) | None |
| 7 | `sdd/fixtures/playbook/curadoria/playbook-mordeu2.md` | Create | escada de promoção | (general) | None |
| 8 | `sdd/fixtures/playbook/curadoria/playbook-inv.md` | Create | cruzamento com invariantes | (general) | None |
| 9 | `sdd/fixtures/playbook/curadoria/invariants-inv.md` | Create | invariantes de teste | (general) | None |
| 10 | `sdd/fixtures/playbook/curadoria/delta-lm020.txt` | Create | delta de 1 contador | (general) | None |
| 11 | `sdd/fixtures/playbook/curadoria/bloco-ok.txt` | Create | bloco de curadoria válido para a colheita das fixtures | (general) | 3, 4, 5, 6 |
| 12 | `sdd/fixtures/playbook/curadoria/replay/BUILD_REPORT_REPLAY.md` | Create | `mordeu` em negrito na célula e `FAIL` dentro de identificador | (general) | None |
| 13 | `sdd/fixtures/playbook/curadoria/replay/playbook-replay.md` | Create | playbook do replay | (general) | None |
| 14 | `.agents/skills/sdd-playbook/references/curator.md` | Create | brief do curador (Decision 7) | (general) | 1 |
| 15 | `.agents/skills/sdd-playbook/SKILL.md` | Modify | papéis, invariantes, ponteiro para o brief; 2.2.0 | (general) | 1, 2, 14 |
| 16 | `.agents/skills/sdd-playbook/references/como-falar.md` | Modify | glossário (UX U4) | (general) | None |
| 17 | `sdd/bin/sdd-fluxo.sh` | Modify | caso `curador` no `despachar` (Decision 7) | (general) | None |
| 18 | `sdd/WORKFLOW_CONTRACTS.yaml` | Modify | contrato `curador` (Decision 7) | (general) | 1, 14 |
| 19 | `.agents/skills/sdd-release/SKILL.md` | Modify | passo 17b; 2.7.0 (Decision 8) | (general) | 1, 2, 14, 17 |
| 20 | `.agents/skills/sdd-release/references/como-falar.md` | Modify | 2 perguntas, recibo, glossário (Decision 8) | (general) | 19 |
| 21 | `.agents/skills/sdd-new-session/scripts/copiar-docs.sh` | Create | cópia por nome idêntico (Decision 9) | (general) | None |
| 22 | `.agents/skills/sdd-new-session/SKILL.md` | Modify | chama o script no passo 2; 1.4.0 | (general) | 21 |
| 23 | `sdd/templates/HANDOFF_TEMPLATE.md` | Modify | 6 seções (Decision 10) | (general) | None |
| 24 | `sdd/fixtures/handoff/HANDOFF_COMPLETO.md` | Create | ficha preenchida do molde novo | (general) | 23 |
| 25 | `.agents/skills/sdd-handoff/SKILL.md` | Modify | 1 frase sobre as seções; 2.1.2 | (general) | 23 |
| 26 | `tests/apoio.py` | Modify | sandbox sem `SDD_TRACE` (Decision 11) | (general) | None |
| 27 | `sdd/bin/design-lint.py` | Modify | título e chaves (Decision 11) | (general) | None |
| 28 | `sdd/bin/prompt-drift-scan.sh` | Modify | 2 formas do slot e 2 casos do self-test (Decision 11) | (general) | None |
| 29 | `sdd/bin/playbook-lint.sh` | Modify | piso de 1 alterado no anti-collapse (Decision 11) | (general) | None |
| 30 | `bin/sdd-open.sh` | Modify | `invariants.md` na lista do `init` (Decision 13) | (general) | 2 |
| 31 | `.github/workflows/release.yml` | Modify | `sdd/invariants.md` nos `paths` (Decision 13) | (general) | 2 |
| 32 | `docs/playbook-curation.md` | Create | explica a curadoria (Decision 13) | (general) | 1, 2, 19 |
| 33 | `docs/pt-BR/playbook-curation.md` | Create | versão PT | (general) | 32 |
| 34 | `README.md` | Modify | link do doc | (general) | 32 |
| 35 | `README.pt-BR.md` | Modify | link do doc | (general) | 33 |
| 36 | `docs/cli-conventions.md` | Modify | saídas e palavras novas | (general) | 1, 21 |
| 37 | `docs/pt-BR/guia-do-aluno.md` | Modify | curadoria na ficha da `sdd-release` | (general) | 19 |
| 38 | `tests/test_playbook_curator.py` | Create | AT-001 a AT-013, AT-022, AT-040, AT-041 | (general) | 1, 3, 4, 5, 6, 7, 10, 12, 13, 29 |
| 39 | `tests/test_playbook_invariantes.py` | Create | AT-014 a AT-019 | (general) | 1, 2, 8, 9 |
| 40 | `tests/test_curadoria_bloco.py` | Create | AT-020, AT-021 | (general) | 1, 11 |
| 41 | `tests/test_copiar_docs.py` | Create | AT-026, AT-027 | (general) | 21 |
| 42 | `tests/test_f14_textos.py` | Create | AT-023 a AT-025, AT-028, AT-029, AT-034 a AT-036 | (general) | 14, 15, 17, 18, 19, 20, 22, 23, 24, 25, 31 |
| 43 | `tests/test_apoio_ambiente.py` | Create | AT-030 | (general) | 26 |
| 44 | `tests/test_design_lint.py` | Modify | AT-031 | (general) | 27 |
| 45 | `tests/test_prompt_drift_scan.py` | Modify | AT-032 | (general) | 28 |
| 46 | `tests/test_fluxo.py` | Modify | `despachar curador` (AT-023) | (general) | 17 |
| 47 | `tests/test_decisoes_lint.py` | Modify | contagem nova de perguntas | (general) | 20 |
| 48 | `tests/test_contrato_build_release.py` | Modify | pino da `sdd-release` e anti-collapse | (general) | 19, 29 |
| 49 | `tests/test_matriz_new_session.py` | Modify | pino da `sdd-new-session` | (general) | 22 |
| 50 | `tests/test_sdd_open.py` | Modify | `init` instala e preserva as invariantes (AT-034) | (general) | 30 |
| 51 | `tests/test_docs.py` | Modify | doc novo e links | (general) | 32, 33, 34, 35 |
| 52 | `tests/test_handoff_lint.py` | Modify | fixture completa passa (AT-029) | (general) | 24 |
| 53 | `MANIFEST.txt` | Modify | arquivos novos, `LC_ALL=C sort` | (general) | 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 21, 24, 32, 33, 38, 39, 40, 41, 42, 43 |
| 54 | `sdd/bin/governanca-fronteira.sh` | Modify | F3, F4, F8 (Decision 12) | (general) | None |
| 55 | `sdd/bin/governanca-bloco.py` | Modify | F1 (Decision 12) | (general) | None |
| 56 | `.agents/skills/sdd-define/SKILL.md` | Modify | F2, F9; 2.5.1 (Decision 12) | (general) | None |
| 57 | `tests/test_governanca_fronteira.py` | Modify | AT-045, com os 2 lados | (general) | 54 |
| 58 | `tests/test_governanca_bloco.py` | Modify | AT-045, com os 2 lados | (general) | 55 |
| 59 | `tests/test_f12_textos.py` | Modify | a sequência nova da restauração | (general) | 56 |
| 60 | `docs/hooks.md` | Modify | o piso do anti-collapse (AT-042) | (general) | 29 |
| 61 | `docs/pt-BR/hooks.md` | Modify | o piso do anti-collapse (AT-042) | (general) | 29 |

**Total Files:** 61

### Agent Assignment Rationale

| Agent / Owner | Files Assigned | Why |
|---|---|---|
| (general) | 1–61 | modo default (um agente), como nas F9–F13; sem catálogo de agentes no repositório |

**Agent Discovery:** Not available

Fora do commit (evidência, branch `docs/`): `sdd/reports/evidence/F14_PLAYBOOK/` (`ev.sh`, baseline, sabotagens, prova em agente real, `ledger-review.md`, `real-rodada.sh`) e `sdd/reviews/REVISAO_FRONTEIRA_F14_PLAYBOOK_20261105.md`. A correção que a revisão da fronteira pedir entra como drift (Decision 12).

---

## Landmines aplicáveis

Varredura rodada em 2026-11-05 com `playbook-lint.sh --grep` sobre `playbook`, `curator`, `grep`, `exit 0`, `baseline`, `git status`, `untracked`, `review`, `asserção`, `handoff`, `worktree`.

| LM-nnn | Superfície | Tratamento |
|---|---|---|
| LM-001 | `playbook-curator.sh`, `copiar-docs.sh`, textos do 17b | ✔ tratado: cada regra roda com fixture dos 2 lados; os testes de texto conferem ordem e comando, e o efeito é provado num agente real |
| LM-002 | testes novos e o self-test | ✔ tratado: vermelhos antes dos verdes no self-test; baseline vermelha na `v2.5.0`; exit 2 ou 64 da colheita nunca vale como "0 deltas" |
| LM-003 | `copiar-docs.sh` e a revisão real | ✔ tratado: o script lê os não salvos no git por `ls-files --others`; a revisão roda com tudo commitado |

---

## Code Patterns

### Pattern 1: bash que entrega ao núcleo Python

```bash
#!/usr/bin/env bash
set -uo pipefail
if ! command -v python3 >/dev/null 2>&1; then echo "python3 não encontrado" >&2; exit 64; fi
SDD_CURATOR_SELF="$0" exec python3 -B - "$@" <<'PY'
import sys
# núcleo: só stdlib, Python 3.9
PY
```

### Pattern 2: veredito no fim, fora do stdout do `--aplicar`

```python
def fim(resultado, seta, canal=sys.stdout):
    print("RESULTADO: " + resultado, file=canal)
    print("→ " + seta, file=canal)
```

### Pattern 3: validar o delta inteiro antes de qualquer saída

```python
erros = validar_delta(linhas, ativos, secoes)
if erros:
    for n, msg in erros:
        print("❌ delta linha %d: %s" % (n, msg), file=sys.stderr)
    fim("DELTA INVÁLIDO", "corrija as linhas acima; nada foi aplicado", sys.stderr)
    sys.exit(2)
```

### Pattern 4: teste contra o contrato observável

```python
rc, out, err = self.roda([BASH, CURATOR, "--aplicar", delta, base], self.r)
self.assertEqual(rc, 2)
self.assertEqual(out, "")
self.assertIn("não existe como bullet ativo", err)
```

### Pattern 5: log de evidência com o exit real

```bash
out=$(bash sdd/bin/playbook-curator.sh --colher "$STG" sdd/playbook.md 2>&1); rc=$?
printf '$ %s\n%s\n[exit=%s]\n' "playbook-curator.sh --colher" "$out" "$rc" > "$EV/CURATOR-colheita.log"
```

---

## Data Flow

```text
Release, passo 17b
1. --preparar F            → pasta de staging com cópias
2. --colher                → colheita.txt (DELTA, SUGESTAO, CANDIDATO, REJEITADO, PROMOVER?, IGNORADO, JA_COLHIDO, INV_PENDENTE, resumo)
   ├─ 1 com NADA A COLHER  → "Curadoria: 0 deltas" e fim
   └─ outro exit           → "Curadoria: FALHOU (rc=N)" e fim
3. brief + snapshot        → curador → curadoria.txt → comparar
4. --conferir-bloco        → AUTO … / PERGUNTA …
5. AUTO → delta.txt; PERGUNTA → resposta da pessoa → delta.txt; --cruzar → ajuste de invariante na mesma opção
6. --aplicar > novo.md     → lint → anti-collapse → --validar-inv → copia por cima
7. CURATOR-*.log, commit, pergunta do envio, aterrissagem, lint e trava de novo, push

Nova sessão
8. git worktree add        → copiar-docs.sh → COPIADO, JA_EXISTE, PARECIDO, IGNORADO → RESULTADO
```

---

## Integration Points

| External System | Integration Type | Authentication | Direction | Failure / Retry |
|---|---|---|---|---|
| None em runtime | N/A | N/A | N/A | os scripts novos não usam rede |
| git (só `copiar-docs.sh` e o self-test, pelo lint) | CLI | nenhuma | local | fora de repositório: exit 64 com a causa |
| OpenRouter + CLIs (só a revisão real, fora do pacote) | `adversarial-review.sh` | `OPENROUTER_API_KEY` só no ambiente do processo | out | exits já contratados pela F10 |
| Codex CLI (só a prova, fora do pacote) | CLI | a conta do Roberto | out | sem créditos, a reserva via OpenRouter; sem retry automático |

---

## Testing Strategy

| Type | Scope | Files | Tools | Coverage Goal |
|---|---|---|---|---|
| Unit, por subprocess | cada modo do curator, dos 2 lados | `test_playbook_curator.py`, `test_playbook_invariantes.py`, `test_curadoria_bloco.py` | unittest, sandbox de `apoio.py` | todo AT de AT-001 a AT-022, AT-040 e AT-041 com caso que passa e caso que reprova |
| Unit, com git | `copiar-docs.sh` | `test_copiar_docs.py` | `git init` na sandbox | idêntico, parecido, existente, link, uso |
| Texto | 17b, brief, yaml, molde, docs | `test_f14_textos.py` | leitura e ordem | campos, tipos e recomendações iguais nos 3 lugares; ordem do 17b |
| Regressão | lints tocados, fluxo, init, docs | arquivos de teste modificados | unittest | contratos antigos intactos |
| Self-test | curator no pacote | `--self-test` | fixtures de `curadoria/` | vermelhos antes dos verdes |
| Verify Gate | suíte inteira no piso | `cmd` do DEFINE | bash 3.2, Python 3.9 | exit 0 |
| Integration, agente real | 17b e brief | evidência | agente liberado | efeito observado, com controles |

Baseline vermelha: os 6 arquivos de teste novos falham numa cópia da `v2.5.0`. Sabotagens: tirar a checagem de `AUTO` contra a colheita no curator; trocar a comparação exata por prefixo no `copiar-docs.sh`.

---

## Error Handling

| Error Type | Handling Strategy | Retry? |
|---|---|---|
| Uso errado de um modo | mensagem com a forma certa em stderr, `RESULTADO: ERRO DE USO`, exit 64 | não |
| Playbook ausente ou sem bullet | exit 2 com o caminho; o 17b registra FALHOU | não |
| Delta inválido | todos os erros com linha, stdout vazio, exit 2 | corrigir e rodar de novo |
| Bloco inválido ou fronteira violada | redespacho 1 vez; depois FALHOU, nada aplicado | 1 |
| Trava de invariante | `🔴 trava INV:` com as saídas; volta à pessoa | não |
| Trace que não grava | ignora; o exit não muda | não |
| Cópia que falha no `copiar-docs.sh` | exit 2 com o arquivo; os já copiados ficam | não |

---

## Configuration

| Config Key | Type | Default | Description |
|---|---|---|---|
| `PLAYBOOK_SECTIONS` (ambiente) | texto | o do `playbook-lint.sh` | seções aceitas, separadas por barra vertical |
| `SDD_TRACE`, `SDD_TRACE_DIR` (ambiente) | texto | ligado, `sdd/traces` | trace da colheita |
| `PLAYBOOK_CURATOR_FIXTURES` (ambiente) | caminho | `sdd/fixtures/playbook/curadoria` | fixtures do self-test |

Nenhum slot novo em `sdd/config.yaml` nesta entrega.

---

## Security Considerations

- O curador recebe só 5 campos e é conferido pela fronteira de escrita; contaminação é registrada no bloco.
- `--preparar` e `copiar-docs.sh` copiam só arquivo regular, nunca seguem link e nunca sobrescrevem documento da frente.
- Nomes de feature são validados antes de virar caminho; o nome no trace é sanitizado.
- Nenhuma credencial é lida ou gravada; a chave da OpenRouter existe só no ambiente do processo da revisão.
- Nenhum push sem pergunta: o envio da curadoria é D1.

---

## Observability

| Aspect | Implementation |
|---|---|
| Logging | `CURATOR-colheita.log` e `CURATOR-delta.log` na pasta de evidência da feature |
| Metrics | trace JSONL da colheita com os 7 contadores; linha `Curadoria:` na ficha |
| Tracing | N/A |

---

## Requirements Traceability

| Requirement / AT | Design Element | Test / Gate |
|---|---|---|
| AT-001 a AT-010 (P1) | Decisions 1, 2; manifest 1, 3 a 7, 12, 13 | `tests/test_playbook_curator.py` |
| AT-011 a AT-013 (P1) | Decisions 4, 11; manifest 1, 10, 29 | `tests/test_playbook_curator.py` |
| AT-014 a AT-019 (C5) | Decision 5; manifest 1, 2, 8, 9 | `tests/test_playbook_invariantes.py` |
| AT-020, AT-021 (P2, P3) | Decision 6; manifest 1, 11 | `tests/test_curadoria_bloco.py` |
| AT-022, AT-040 | Decision 1; manifest 1 | `tests/test_playbook_curator.py` |
| AT-041, AT-042 (P4) | Decisions 3, 11; manifest 1, 29 | `tests/test_playbook_curator.py` |
| AT-043, AT-044 | Decisions 2, 5; manifest 1 | `tests/test_playbook_invariantes.py`, `tests/test_playbook_curator.py` |
| AT-045 | Decision 12; manifest 54 a 59 | `tests/test_governanca_fronteira.py`, `tests/test_governanca_bloco.py`, `tests/test_f12_textos.py` |
| AT-023 (P2) | Decision 7; manifest 14, 17, 18 | `tests/test_f14_textos.py`, `tests/test_fluxo.py` |
| AT-024, AT-025 (P3, P4) | Decision 8; manifest 19, 20 | `tests/test_f14_textos.py`, `tests/test_decisoes_lint.py` |
| AT-026 a AT-028 (N1) | Decision 9; manifest 21, 22 | `tests/test_copiar_docs.py`, `tests/test_f14_textos.py` |
| AT-029 (N3) | Decision 10; manifest 23, 24, 25 | `tests/test_handoff_lint.py`, `tests/test_f14_textos.py` |
| AT-030 | Decision 11; manifest 26 | `tests/test_apoio_ambiente.py` |
| AT-031, AT-032 | Decision 11; manifest 27, 28 | `tests/test_design_lint.py`, `tests/test_prompt_drift_scan.py` |
| AT-033 | Decision 12 | relatório em `sdd/reviews/` e BUILD_REPORT (smoke) |
| AT-034, AT-035 | Decision 13; manifest 30 a 37 | `tests/test_sdd_open.py`, `tests/test_docs.py`, `tests/test_f14_textos.py` |
| AT-036 | Decision 14 | `tests/test_f14_textos.py`, `check-versions.py` |
| AT-037 a AT-039 | Decision 15 | logs em `sdd/reports/evidence/F14_PLAYBOOK/` (smoke) |

---

## Risks and Mitigations

| Risk | Impact | Mitigation | Residual Risk |
|---|---|---|---|
| O agente pula o `--conferir-bloco` e separa as contagens à mão | Contagem inventada no playbook | texto do 17b com a ordem conferida por teste; prova em agente real | Médio até a prova rodar |
| Créditos do Codex acabarem de novo | AT-038 sem execução no modelo próprio | reserva via OpenRouter, com o modelo dito no relatório | Baixo |
| A trava assusta projeto com lições antigas | Curadoria parada no 1º uso | frase da v2.6.0 e 1 item por lição | Baixo |
| Regra do privado perdida na reescrita em Python | Colheita diferente | os casos do self-test do privado viram a lista mínima de casos | Baixo |
| A suíte passa do teto do macOS | CI cancelado | testes sem rede; git só onde precisa; medir no PR | Baixo: 28 de 45 min |
| Conserto tardio traz regressão | Defeito depois da revisão | teste de ataque dos 2 lados em cada conserto | Médio; lição da F12 e da F13 |
| A pergunta do envio vira ruído | Pessoa responde sem ler | recomendada primeiro, com o que o push faz | Baixo |

---

## Advisor Ledger

Revisão de contexto fresco do DESIGN v1.0 (`sdd/reviews/REVISAO_DESIGN_F14_PLAYBOOK_20261105.md`, modo `contrato`, logs `AVAL-DESIGN-*.log`): NEEDS_WORK, 2 HIGH, 9 MEDIUM, 6 LOW, 5 propostas. Revisão focada da fronteira (`sdd/reviews/REVISAO_FRONTEIRA_F14_PLAYBOOK_20261105.md`, logs `AVAL-FRONTEIRA-*.log`): NEEDS_WORK, 0 HIGH, 3 MEDIUM, 6 LOW. As 2 voltaram com o build já em andamento: os consertos foram feitos no código e neste documento antes do 1º commit e antes do gate.

| # | Nota | Severidade | Veredito | Onde |
|---|---|---|---|---|
| P1 | Saída 1 com 3 regras; rejeitado e sugestão terminam como "nada" | proposta | ACEITA, por outro caminho: o exit 0 passa a valer para qualquer linha, e o 17b não precisa ler o resumo | DEFINE AT-007, AT-024; Decision 2 |
| P2 | `AUTO` por existência, não por igualdade | proposta | ACEITA | DEFINE AT-020, AT-021; Decision 6 |
| P3 | AT do despacho já passava na base | proposta | ACEITA | DEFINE AT-023 |
| P4 | Destino ausente, commit não enviado, acento | proposta | ACEITA | DEFINE AT-026, AT-027; Decision 9 |
| P5 | O gate não cobre versões, AT-037 e testes novos | proposta | ACEITA em parte: AT-030 e o comando do Success Criteria corrigidos, teste confere os arquivos novos. RECUSADA a mudança do `cmd`: o prompt da sessão o fixou, como na F13 | DEFINE AT-030; Clarifications |
| D1 | `init` instala invariante de lição que o projeto pode não ter | HIGH | APLICADA: esqueleto | Decision 5, 13; DEFINE AT-034 |
| D2 | Sugestão como `AUTO` contraria o DEFINE | HIGH | APLICADA | Decision 6; DEFINE AT-021 |
| D3 | 3 regras para a saída 1 | MEDIUM | APLICADA | Decision 2 |
| D4 | A mesma linha conta de novo a cada release da feature | MEDIUM | APLICADA, com registro por impressão digital em vez de data | Decision 2; DEFINE AT-044 |
| D5 | A fronteira não vê o staging | MEDIUM | APLICADA: `--selar` | Decision 6; DEFINE AT-020 |
| D6 | Nenhum modo grava as invariantes | MEDIUM | APLICADA: `--aplicar-inv` | Decision 5; DEFINE AT-043 |
| D7 | O passo 15b move os documentos antes do 17b | MEDIUM | APLICADA | Decision 3; DEFINE AT-041 |
| D8 | Staging nunca é limpo; `RETOMADA:` sem instrução | MEDIUM | APLICADA: limpa, `--retomar` | Decision 3 |
| D9 | "Já está na frente" é falso com commit não enviado | MEDIUM | APLICADA | Decision 9 |
| D10 | Forma da pergunta não cabe no lint | MEDIUM | APLICADA: uma pergunta por item, numerada, só no `como-falar.md`. Não adotada a forma "aceitar os N" da nota, que tira a decisão por item | Decision 8 |
| D11 | Bullet sem `promovido_para:`; rabo do `REFINE`; crase | MEDIUM | APLICADA | Decision 2; `test_playbook_curator.py` |
| D12 | Papel do curador cai no default; seta da fronteira fala do DEFINE; `--colher` repetido grava | LOW | APLICADA | Decision 7; 17b, item 3; brief |
| D13 | Alfabeto do nome diferente do `despachar` | LOW | APLICADA | Decision 3 |
| D14 | `--cruzar -` sem stdin; lint com `cd` | LOW | APLICADA: arquivo temporário no bash; o self-test passa caminho absoluto | script |
| D15 | Barra vertical na célula | LOW | APLICADA: `\|` | Decision 6; brief |
| D16 | Docs de hooks e dependências | LOW | APLICADA | manifest 60, 61 |
| D17 | Trace fora do contrato; comando grava na árvore; glob de `AVALIACAO` | LOW | APLICADA | Decision 2; DEFINE Success Criteria; AT-041 |
| F1 | Bloco dá ✅ com `FORA:` | MEDIUM | APLICADA | Decision 12; AT-045 |
| F2 | Restauração apaga o DEFINE | MEDIUM | APLICADA | Decision 12; AT-045 |
| F3 | Índice, branch e `.git` fora do snapshot | MEDIUM | APLICADA | Decision 12; AT-045 |
| F4 | Pasta ilegível vira verde | LOW | APLICADA | Decision 12; AT-045 |
| F5 | Repositório aninhado que já existia | LOW | REBATIDA_ESCOPO: pendência no handoff; pede percorrer pasta, com custo de tempo em repositório grande | Decision 12 |
| F6 | Só permissão em arquivo já sujo | LOW | REBATIDA_ESCOPO: pendência no handoff | Decision 12 |
| F7 | Grafia do permitido | LOW | REBATIDA_ESCOPO: as 3 skills passam a mesma string nos 2 snapshots; pendência no handoff | Decision 12 |
| F8 | Raiz com `&` | LOW | APLICADA | Decision 12; AT-045 |
| F9 | Retomada lava a escrita | LOW | APLICADA no texto; a guarda por arquivo fica como pendência | Decision 12; AT-045 |
| H1 a H4 | Avaliador, ciclo 1: self-test sem git; conferidor sem correspondência 1 para 1; contagem dobra entre releases; seção da lista não entrava | HIGH | APLICADAS | `AVALIACAO_F14_PLAYBOOK_20261105-ciclo1.md`; DEFINE v1.4 |
| M1 a M8 | Avaliador, ciclo 1: campo na continuação; só IGNORADO saía 1; ajuste com check morto; selo sem os derivados; 3 erros de texto; ID igual pisado; lições antigas e evidência não versionada; 12 mutantes vivos | MEDIUM | APLICADAS | idem |
| L1 a L6, L8, L9 | Avaliador, ciclo 1 | LOW | APLICADAS | idem |
| L7 | `wrapper_pattern` em lista de bloco vira slot vazio | LOW | REBATIDA_ESCOPO: pendência no handoff; a forma de 1 linha, que é a documentada, já sai 64 | handoff |
| N-H1, N-M1, N-M2, N-M3 | Avaliador, ciclo 2: veredito longo perdia a contagem (regressão do conserto L1); seta do `--retomar`; avaliação de feature de nome parecido; contagem dobra em frente nova | HIGH e MEDIUM | APLICADAS; em N-M3, o registro vai para `sdd/releases/<F>/`, com limite declarado para quem não versiona nem isso | `AVALIACAO_F14_PLAYBOOK_20261105-ciclo2.md`; DEFINE v1.5 |
| N-L1 a N-L8, parte de N-L11 | Avaliador, ciclo 2 | LOW | APLICADAS | idem |
| N-L9, N-L10, resto de N-L11 | CRLF em delta real; `git branch` e `git tag` na fronteira; marcas de conflito no `--aplicar`; `NAO_JULGADO` no registro | LOW | REBATIDA_ESCOPO: pendência no handoff | handoff |
| R1@claude, R2@codex, R1@codex | Revisão real, rodada 1: exceção saía 1, lida como "0 deltas"; link no nome intermediário da restauração | HIGH | APLICADAS, com a sequência do texto executada por teste | ledger da revisão; AT-007, AT-045 |
| N3-H1 | Avaliador, ciclo 3: a nota dava a contagem à lição errada (2ª regressão seguida da mesma regra) | HIGH | APLICADA na causa: a tabela é lida pelo cabeçalho | `AVALIACAO_F14_PLAYBOOK_20261105-ciclo3.md`; DEFINE v1.6 |
| N3-M1, N3-M2, N3-M3 | `check=` em `.github/`; item 8 sem comando para `sdd/releases`; registro perdido no conflito | MEDIUM | APLICADAS | idem |
| N3-L1, N3-L2, N3-L3, N3-L5, N3-L6, N3-L7 | Avaliador, ciclo 3 | LOW | APLICADAS | idem |
| N3-L4 | Item 6 "nada aplicado": o registro fica fora do git | LOW | REBATIDA_ESCOPO: sem dado errado; a frente nova só rejulga | handoff |
| L10 | Log de sonda é colhido como achado real | LOW | REBATIDA_ESCOPO: pendência no handoff; `SUGESTAO` já pede confirmação, e o curador lê a linha antes do AUTO | handoff |

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | 2026-11-05 | SDD Design by RDD | Initial version |
| 1.5 | 2026-11-05 | revisão real, rodada 1 | Decisions 6 e 8; Data Flow; Advisor Ledger |
| 1.4 | 2026-11-05 | avaliador, ciclo 3 | Decision 2: leitura pelo cabeçalho; Advisor Ledger |
| 1.3 | 2026-11-05 | avaliador, ciclo 2 | Advisor Ledger; Decision 2 |
| 1.2 | 2026-11-05 | avaliador, ciclo 1 | Advisor Ledger; seção da lista que nasce no `--aplicar` |
| 1.1 | 2026-11-05 | revisões frescas | Advisor Ledger; Decisions 2, 3, 5, 6, 8, 9, 11, 12, 13; manifest 54 a 61 |

---

## Next Step

Execute o **SDD Build by RDD**.
