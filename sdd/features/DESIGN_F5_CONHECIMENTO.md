# DESIGN: F5 Conhecimento do sdd-open

> A `sdd-kb` do sdd-starter entra como 17ª skill do open, com adaptação mínima: a pasta da KB é `sdd/kb/`, o texto segue a camada da F4, o `gate.sh` monta seus casos a partir dos exemplos e o `--strict` liga regra implementada a um teste que existe. O `sdd/bin/kb-dominios.py` fecha o "KB Domains" do DEFINE em `ls sdd/kb/` ou `nenhum`. A `sdd-ux-review` ganha a entrevista de público como entrada opcional do passo 1.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | F5_CONHECIMENTO |
| **Date** | 2026-10-29 |
| **Author** | SDD Design by RDD (sessão com Roberto Dias Duarte) |
| **BRAINSTORM** | `sdd/features/BRAINSTORM_F5_CONHECIMENTO.md` |
| **DEFINE** | `sdd/features/DEFINE_F5_CONHECIMENTO.md` (v1.4) |
| **UX REVIEW** | `sdd/reviews/UX_REVIEW_F5_CONHECIMENTO.md` (Ready for Design) |
| **LLM Prompts** | false |
| **Status** | Ready for Build |

---

## Architecture Overview

```text
 Projeto do aluno (o init copia a pasta inteira da skill)          Pacote sdd-open (não viaja)
 ─────────────────────────────────────────────────────            ─────────────────────────────
 .agents/skills/sdd-kb/                                            tests/test_sdd_kb_normativo.py (62, porte)
 ├── SKILL.md  ── camada F4 + 10 passos, caminhos sdd/kb/          tests/test_sdd_kb.py ──► gate.sh (pacote
 ├── references/ (como-falar, kb-protocol, normativo, sourcing)        e cópia só da skill; sabotagem do
 ├── assets/ (moldes, _index.yaml, example-kb, example-kb-normativo)  validador ⇒ gate 2) · --strict teste
 └── scripts/                                                      tests/test_kb_dominios.py ──► kb-dominios
     ├── kb_normativo.py  (sha · rule-map [--check])                tests/test_conversa.py (17 skills, entrevista
     ├── validate_kb.py   (0/2/64; --strict: + implementacao→teste)   via skill-lint --conversa)
     └── gate.sh ── monta $T/<caso>/sdd/kb/<dom> a partir de assets/
                   4 aceitas · 12 rejeitadas pelo motivo certo ──► RESULTADO: VERDE|VERMELHO

 sdd/kb/_index.yaml + sdd/kb/<slug>/   ◄── a sdd-kb grava; validate_kb.py confere
        │ ls (pastas, sem ocultas)
        ▼
 sdd/bin/kb-dominios.py <DEFINE> ◄── passo 10 da sdd-define (2.3.0)
        │ lê `| **KB Domains** | … |` · lê sdd/kb/<dom>/RULE_MAP.md (coluna Teste)
        ▼
 ✅ válido + "<dom>: <REGRA> → <teste>"  (o agente põe os testes no cmd do Verify Gate)
 🛑 … · RESULTADO: VERMELHO · → conserto   (1)  ·  uso errado (64)

 sdd-ux-review (2.3.0), passo 1 ──(DEFINE sem público, ou aluno pede)──► references/entrevista-publico.md
        └─► ## User and Context do UX_REVIEW (template intacto)

 Fora do gate (sdd/reports/evidence/F5_CONHECIMENTO/): comandos-intactos.log (v2.2.5 × HEAD) ·
 check-versions.log · baseline.log (3 módulos novos na v2.2.5) · sabotagem.log · codepoints.log
```

---

## Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| `sdd-kb/SKILL.md` + `references/` + `assets/` | Procedimento de 10 passos do starter, com a pasta fixa `sdd/kb/`, os caminhos de script do projeto e a camada da F4 | Markdown; moldes YAML/JSON/MD |
| `validate_kb.py` | Lint de estrutura, tamanho, placeholder, registro e perfil normativo; o `--strict` agora confere `implementacao` → `teste` | Python 3.9 stdlib, porte de 465 linhas + 1 função |
| `kb_normativo.py` | `sha <arquivo>` e `rule-map [--check] <domínio>` | Python 3.9 stdlib, porte |
| `gate.sh` | Prova, onde roda, que o validador aceita o bom e rejeita o ruim pelo motivo certo | bash 3.2 + Python inline para as trocas de texto |
| `sdd/bin/kb-dominios.py` | Confere o "KB Domains" contra `ls sdd/kb/` e lista os testes do RULE_MAP | Python 3.9 stdlib, novo em `sdd/bin/` (viaja pelo `init`) |
| Passo 10 da `sdd-define` | Roda o lint no DEFINE gravado; testes listados vão para o `cmd` | Markdown |
| `entrevista-publico.md` | Público, estágio, referência e URL em perguntas abertas, mais 1 confirmação | Markdown em `sdd-ux-review/references/` |
| Testes do pacote | Porte dos 62, gate, `--strict`, lint, contagens 16 → 17 | unittest + `tests/apoio.py` |
| Scripts de evidência | Comandos intactos, versões, baseline, sabotagem, code points | bash + Python em `sdd/reports/evidence/F5_CONHECIMENTO/` (fora do commit do produto) |

---

## Key Decisions

### Decision 1: Porte com adaptação mínima: o que muda no texto e nos scripts do starter

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-10-29 |

**Context:** a abordagem A do BRAINSTORM manda transplantar. A pasta da skill vai inteira para o projeto do aluno, então todo caminho escrito no texto precisa funcionar a partir da raiz do projeto. `tests/test_matriz_new_session.py::Portadas` reprova `openai.yaml`, o texto `sdd-starter` e `tests/` dentro da skill.

**Choice:** copiar `SKILL.md`, os 4 `references/`, os 10 moldes, o `assets/_index.yaml`, os 2 exemplos e os 2 scripts Python, e mudar só isto:
- **caminhos de script** no texto e nas mensagens: `scripts/validate_kb.py` e `scripts/kb_normativo.py` viram `.agents/skills/sdd-kb/scripts/…`, em `SKILL.md`, `references/normativo.md`, `assets/RULE_TEMPLATE.md`, `assets/CATALOGO_FONTES_TEMPLATE.md`, nas docstrings e nas 2 mensagens `FAIL` que mandam rodar o `rule-map`;
- **pasta da KB**: o passo 3 diz `sdd/kb/_index.yaml` (no starter, era "tipicamente na raiz da pasta de bases"), o passo 4 mostra a árvore `sdd/kb/<dominio>/` e o passo 10 manda apontar a IA para `sdd/kb/<slug>/`;
- **links e menções a moldes, exemplos e scripts** em `SKILL.md`, `references/` e `assets/*.md` usam `.agents/skills/sdd-kb/…`, a fonte que o `init` sempre cria (revisão do design, H1). O adaptador gerado (`.claude/skills/`, `.cursor/skills/`) ganha 2 linhas `sdd-open:generated` em todo arquivo não-JSON, então um molde ou exemplo lido de lá viria com cabeçalho, e o exemplo normativo reprovaria (SHA-256 e RULE_MAP);
- **`teste` é caminho**: `RULE_TEMPLATE.md` e `references/normativo.md` dizem que `teste` é o caminho do arquivo de teste a partir da raiz do projeto, com sufixo `:`/`::` opcional, não um comando, e que o `--strict` confere que ele existe (L2);
- **identificação e camada** (Decision 7);
- **`CHANGELOG.md`**: a entrada 2.2.0 no topo; o histórico 1.0.0–2.1.0 fica, sem o nome do repositório de origem (a entrada 2.2.0 diz "portada do starter");
- **fora**: `agents/openai.yaml` e o `gate.sh` original (reescrito, Decision 3).

As mensagens do `validate_kb.py` continuam em inglês (`PASS:`/`FAIL:`/`WARN:`), com as saídas 0/2/64.

**Rationale:** os 62 testes portados conferem o texto das razões. Traduzir reabriria um validador já revisado (WONT do UX review). A camada manda o agente traduzir a saída.

**Alternatives Rejected:**
1. Traduzir as mensagens: retrabalho em ~60 linhas e nos asserts dos 62 testes, sem ganho para o aluno, que não lê a saída crua.
2. Manter `scripts/…` relativo: no projeto do aluno, o comando rodado da raiz falharia com "No such file".

**Consequences:** o `docs/cli-conventions.md` registra a exceção do `validate_kb.py`. Os scripts novos (`gate.sh`, `kb-dominios.py`) seguem a convenção do open. Um `.gitattributes` na raiz do pacote marca `.agents/skills/sdd-kb/assets/example-kb-normativo/fontes/**` como `-text`: num clone Windows com `core.autocrlf`, o arquivo da fonte não ganha CRLF e o SHA-256 do catálogo continua batendo (H1). Só `fontes/` importa: o resto é lido como texto, com fim de linha universal.

---

### Decision 2: Raiz do projeto e a checagem de `teste` no `--strict`

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-10-29 |

**Context:** o DEFINE (AT-005) pede que o `--strict` reprove a regra com `implementacao` sem `teste`, e o `teste` cujo arquivo não existe. O campo é um escalar do `RULE_TEMPLATE.md`, como `tests/test_engine.py::test_vbc`. O caminho é do projeto, não da pasta do domínio.

**Choice:**
- A função `raiz_do_projeto(root)` resolve o domínio. Se o pai se chama `kb` e o avô se chama `sdd`, a raiz é o bisavô (`<raiz>/sdd/kb/<slug>`). Nos outros casos, é `Path.cwd()`.
- Dentro do laço de regras de `check_normativo`, e só com `strict`:
  - um valor vazio, `null`, `—` ou `-` conta como ausente;
  - `implementacao` presente e `teste` ausente → `FAIL: rules/<arq>: implementacao <valor> has no teste — --strict requires the test the Verify Gate runs (RULE_TEMPLATE.md)`;
  - `teste` presente → arquivo = `teste.split(":", 1)[0].strip()`; caminho absoluto ou que resolve fora da raiz → `FAIL: … is outside the project root …`; se `(raiz / arquivo)` não é arquivo → `FAIL: rules/<arq>: teste <valor>: <arquivo> not found from the project root <raiz>`.
- Sem `--strict`, nada muda.

**Rationale:** sem `--strict`, a base pode ser escrita antes do software. O `--strict` já é o "antes de software consumir" do starter, e é lá que a rastreabilidade tem de valer.

**Alternatives Rejected:**
1. Raiz = a pasta do domínio: `tests/…` nunca existe lá.
2. Raiz = `git rev-parse --show-toplevel`: acrescenta dependência de git ao validador, e a cópia do gate não tem `.git`.

**Consequences:** o exemplo normativo (3 regras com `implementacao: null`) continua passando. A mensagem do RULE_MAP aponta o caminho certo (Decision 1).

---

### Decision 3: `gate.sh` autossuficiente: casos, mutações e moldura de saída

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-10-29 |

**Context:** a decisão 3 do BRAINSTORM diz que o gate roda igual no pacote e no projeto do aluno, sem o `tests/` do pacote. O UX review (MUST 4) pede a moldura de `docs/cli-conventions.md`, silêncio no sucesso e o caso nomeado na falha.

**Choice:**
- O gate acha `validate_kb.py`, `kb_normativo.py` e `../assets/` pela própria pasta (`DIR="$(cd "$(dirname "$0")" && pwd)"`). O interpretador é o da variável `PYTHON`, com `python3` quando ela não existe, e os testes passam `PYTHON=sys.executable` para rodar no piso.
- O gate cria `T=$(mktemp -d)` e arma um `trap` que apaga `$T` na saída, com a expansão `:?`, que aborta se `T` estiver vazia (regra da sessão: nada de `rm -rf` com variável sem guarda).
- Cada caso é um projeto `$T/<caso>/`, com `sdd/kb/_index.yaml` e `sdd/kb/<dom>/` copiado de `assets/`, mais **uma** troca de texto. A função `troca` (Python inline) reprova quando a âncora não existe: uma âncora sumida faz o gate sair 2, nunca passar sem testar.
- **Aceitas (4):**
  1. `example-kb` (geral);
  2. `example-kb-normativo`, que tem de imprimir `normativo: ` … `rule(s)`;
  3. `bom-codigo`: o `example-kb` com um conceito que tem um bloco JSON e chaves com espaço dentro de uma crase;
  4. `strict-teste-ok`: o normativo revisado, com `implementacao` e `teste` apontando para um arquivo criado em `$T/<caso>/tests/`, RULE_MAP regerado e `--strict`.
- **Rejeitadas (12)**, cada uma com o trecho da razão que o validador tem de imprimir:

  | Caso | Mutação | Razão esperada |
  |---|---|---|
  | `limite-conceito` | conceito com 151 linhas | `limit is 150` |
  | `limite-receita` | receita com 201 linhas | `limit is 200` |
  | `limite-consulta` | `quick-reference.md` com 101 linhas | `limit is 100` |
  | `nao-registrado` | `_index.yaml` sem o domínio | `is not registered` |
  | `placeholder` | chaves com espaço na prosa | `unsubstituted placeholder` |
  | `placeholder-codigo` | chave dupla com nome em maiúsculas num bloco cercado `text` | `unsubstituted placeholder` |
  | `sem-vigencia` | regra sem `de:` | `vigencia.de missing` |
  | `fonte-fora` | `fonte.id` inexistente | `not in fontes/CATALOGO.md` |
  | `sha-divergente` | 1 linha a mais no arquivo de `fontes/` | `differs from the catalog` |
  | `pendente-strict` | o exemplo como está, com `--strict` | `refuses an unreviewed normative KB` |
  | `teste-vazio-strict` | revisado, com `implementacao` e `teste: null`, RULE_MAP regerado | `has no teste` |
  | `teste-inexistente-strict` | revisado, com `teste` de arquivo ausente, RULE_MAP regerado | `not found from the project root` |

- Também confere o RULE_MAP do exemplo com `kb_normativo.py rule-map --check`.
- **Cópia gerada** (H1): se o próprio `gate.sh` contém a marca `sdd-open:generated`, ele está rodando de um adaptador. Nesse caso sai 2 com `🛑 cópia gerada pelo sync: os exemplos daqui têm cabeçalho e não valem como prova`, `RESULTADO: VERMELHO` e `→ rode bash .agents/skills/sdd-kb/scripts/gate.sh`.
- **Sem subshell** (M1): a função `projeto` não imprime nada, e o chamador usa o caminho fixo `$T/<caso>/sdd/kb/dom`. A `troca` que não acha a âncora chama `falha "<caso>" "âncora ausente: <âncora>" "o exemplo mudou; atualize a âncora no gate.sh"`, com as 3 linhas da moldura. Cada caso apaga `$T/saida` antes de rodar, e a saída de um caso não vaza para outro.
- **Fidelidade às fixtures** (L1): o `bom-codigo` anexa ao `quick-reference.md` do `example-kb` o trecho do `kb_good_codigo` do starter: uma tabela com crases, um bloco `json` e um bloco `text` com expressão de template de chave dupla minúscula. O `placeholder-codigo` põe uma chave dupla com nome em maiúsculas num bloco cercado `text`, como no starter.
- **Saída:**
  - sucesso: uma linha `RESULTADO: VERDE — 4 aceitas, 12 rejeitadas pelo motivo certo, RULE_MAP do exemplo em dia`, exit 0;
  - falha: `🛑 <caso>: <o que houve>`, a saída do validador indentada, `RESULTADO: VERMELHO` e `→ <conserto>`, exit 2.

**Rationale:** a mutação do exemplo atual não deriva do que a skill entrega, que é o mesmo argumento do starter para os 62 testes. Conferir a razão evita o falso verde em que o caso reprova por outro motivo (o RULE_MAP derivado, por exemplo).

**Alternatives Rejected:**
1. Copiar as 7 fixtures do starter para dentro da skill: ~20 arquivos que viajam ao aluno e podem derivar do exemplo.
2. Conferir só o exit: um caso podia reprovar pelo motivo errado e o gate passava.

**Consequences:** o DEFINE vai à v1.2 (AT-002 e o Success Criterion: 4 aceitas) e à v1.3 (AT-003 com a âncora ausente; AT-017, o gate rodado de uma cópia gerada). A sabotagem do gate é provada no `tests/test_sdd_kb.py`, rodando o gate sobre uma cópia da skill com o validador sabotado.

---

### Decision 4: `kb-dominios.py`: leitura do campo, regras e saída

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-10-29 |

**Context:** o item G e os AT-007 a AT-009. A decisão 2 do BRAINSTORM diz que o lint viaja e não depende da `sdd-kb`.

**Choice:**
- **Uso:** `kb-dominios.py <DEFINE.md>`. Sem argumento, com mais de 1 ou com o arquivo ausente, sai 64 com `uso:`. Se não consegue ler o arquivo, sai 1 com `🛑 … não consegui ler`, como o `design-lint`.
- **Raiz:** se o DEFINE está em `<raiz>/sdd/features/`, a raiz é `<raiz>`; nos outros casos, o diretório corrente. A pasta da KB é `<raiz>/sdd/kb/`.
- **Campo:** é a 1ª linha da seção `## Technical Context`, fora de bloco cercado, que casa `^\|\s*\*\*KB Domains\*\*\s*\|([^|]*)\|`. O valor é a célula 2, sem crases e sem espaço nas pontas. Os itens são separados por vírgula, e o item vazio é ignorado. Um prefixo `sdd/kb/` e a `/` final são tolerados.
- **Regras (exit 1)**, com uma linha `🛑` por problema:
  - linha ausente → `🛑 <arq>: falta a linha **KB Domains** no Technical Context`;
  - valor vazio, com chave de abertura ou de fechamento, ou que é `N/A`, `—`, `-` ou a sigla de "a definir" em inglês (sem caixa) → `🛑 KB Domains: '<valor>' não é lista de domínios`;
  - `nenhum` junto com outro item → `🛑 KB Domains: 'nenhum' vem sozinho`;
  - nome citado e `sdd/kb/` ausente → `🛑 KB Domains: sdd/kb/ não existe` e `→ rode a sdd-kb para criar a base, ou escreva nenhum`;
  - nome sem pasta → `🛑 KB Domains: '<nome>' não existe em sdd/kb/ (existem: a, b, …)`, com até 10 nomes e "e mais N", ou "(a pasta está vazia)".
  - Fecho: `RESULTADO: VERMELHO` e `→ corrija o KB Domains com nomes de 'ls sdd/kb/' ou escreva nenhum, e rode de novo` (o conserto de `sdd/kb/` ausente substitui este).
- **Pastas:** as entradas de `sdd/kb/` que são diretório e não começam por `.`. Os nomes são comparados exatos, com caixa. Pasta ilegível → `🛑 não consegui ler sdd/kb/ (…)`, exit 1, sem traceback.
- **Sucesso (exit 0):** `✅ <arq>: KB Domains válido (<itens>)` ou `(nenhum)`. Para cada domínio citado com `RULE_MAP.md`, o lint acha na tabela a coluna cujo cabeçalho é `Teste`. As células se separam por `|` **não escapado** (`(?<!\\)\|`), e o `\|` dentro da célula volta a `|`: o `rule-map` escapa o pipe de um localizador como `art. 5º | inciso II` (M2). Cada linha com valor diferente de `—` e não vazio vira `  <dom>: <REGRA> → <teste>`. Depois vem `RESULTADO: VERDE` e, se houver testes listados, `→ ponha estes testes no cmd do Verify Gate, ou registre no DEFINE por que não`, na ordem do `docs/cli-conventions.md` (L2).
- **Fluxo de saída:** o sucesso vai para o stdout; os `🛑`, `RESULTADO: VERMELHO` e `→` vão para o stderr, como no `design-lint`. Um RULE_MAP ilegível vira `⚠️ <dom>/RULE_MAP.md: não consegui ler (…)` e não muda o exit.

**Rationale:** a raiz e o formato da linha seguem o DEFINE_TEMPLATE do open, e o lint lê o RULE_MAP gerado, sem importar a skill.

**Alternatives Rejected:**
1. Exigir o registro no `_index.yaml`: duplicaria o `validate_kb.py`, e o item G fala em `ls`.
2. Aceitar `N/A`: o item G pede `nenhum` explícito.

**Consequences:** os DEFINE antigos com `N/A` só reprovam se alguém rodar o lint neles; a `sdd-define` só o roda no passo 10, no DEFINE que acabou de gravar.

---

### Decision 5: Passo 10 da `sdd-define` e a linha do `DEFINE_TEMPLATE.md`

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-10-29 |

**Context:** o passo novo não pode renumerar os passos 1–9 (AT-014). O UX review pede o estado vazio dito numa frase e o `name:` do índice ao lado do slug.

**Choice:**
- **No passo 3 (Extrair)**, uma frase nova: "KB Domains (Technical Context): só nomes de `ls sdd/kb/` (as pastas; o `_index.yaml` não conta) ou `nenhum`, conferidos de novo a cada Define. Sem `sdd/kb/`, escreva `nenhum` e diga ao aluno, em 1 frase, que a `sdd-kb` cria uma base. Ao mostrar um domínio pela 1ª vez, ponha ao lado o `name:` dele no `sdd/kb/_index.yaml`."
- **Depois do `### 9. Gravar`**, o passo novo `### 10. Conferir o KB Domains`, no molde do `### 8. Conferir` da `sdd-design`, **sem bloco cercado** (revisão do design, H2: o `extrai()` da F4 pega a linha inteira do bloco, com o comentário). O comando vai em crases na prosa: `python3 sdd/bin/kb-dominios.py sdd/features/DEFINE_<FEATURE>.md` (no `SKILL.md`, o nome da feature entre chaves, como no passo 8 da define). A frase seguinte diz que 0 segue e que 1 manda corrigir o campo e rodar de novo. Depois: "Os testes que ele listar (`<domínio>: <REGRA> → <teste>`) entram no `cmd` do Verify Gate; se algum não entrar, registre o motivo no DEFINE e rode `verify-gate.sh --print` de novo."

- **No Quality Gate**, 1 linha: `[ ] kb-dominios.py sai 0 (KB Domains de ls sdd/kb/ ou nenhum)`.
- **A 6ª etapa da tabela da camada** ("Gravar") passa a cobrir os passos `9 e 10`.
- **Template:** a célula passa a dizer "bases de conhecimento do projeto a consultar (nomes de pasta em `sdd/kb/`, de `ls sdd/kb/`), ou `nenhum` explícito", entre as chaves de placeholder do template, sem "ou equivalente".
- **Versão:** 2.3.0, com a linha de identificação.

**Rationale:** é o mesmo molde do `### 8. Conferir` da `sdd-design` na F4: o lint roda logo depois do arquivo gravado.

**Alternatives Rejected:**
1. Passo 8b antes do Gravar: o lint lê o arquivo, que ainda não existe nesse ponto.
2. Renumerar: quebra o AT-014 e o histórico de quem cita "passo 9".

**Consequences:** o `comandos-intactos` declara as 2 exceções da define: `+ passo ### 10. Conferir o KB Domains` e `+ cmd python3 sdd/bin/kb-dominios.py sdd/features/DEFINE_<FEATURE>.md` (no log, com o nome da feature entre chaves). O `ls sdd/kb/` do passo 3 não conta como comando para o regex (Decision 9).

---

### Decision 6: Entrevista da `sdd-ux-review`: perguntas abertas e uma confirmação

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-10-29 |

**Context:** a decisão 5 do BRAINSTORM; o UX review, MUST 1 e 2 (pergunta de fato com `(recomendado)` induz a resposta, e o "outro" do builder é proibido); o AT-011.

**Choice:**
- `references/entrevista-publico.md`, com as seções: Quando usar · Como conduzir (uma pergunta por resposta, no máximo 2 esclarecimentos do mesmo assunto, pular o que o DEFINE já responde) · As perguntas · Catálogo de referências · URL de referência · Das respostas ao registro · Confirmação.
- **As perguntas abertas**, no formato "Pergunta aberta" do fragmento, cada uma com "Responda com …, ou 'não sei'":
  - **público**, com exemplos no texto (contador ou equipe contábil, cliente do escritório, empresário ou gestor, equipe administrativa interna, público misto), seguido só do que muda a UX: frequência de uso, familiaridade com tecnologia, volume de informação, risco de erro e dispositivo;
  - **estágio** (projeto novo, em desenvolvimento, sistema existente, redesign). Fora de "novo", a skill pergunta por capturas, marca, paleta ou design system;
  - **referência**, com o catálogo de 9 linhas do builder. "Outra referência" vira "Uma referência sua". No "não sei", a skill pergunta por sensações e sugere 2 ou 3 para comparar;
  - **URL**, opcional.
- **A URL**:
  - o protocolo de observação do `URL_ANALYSIS.md` (12 itens) e os limites;
  - "quando o agente consegue abrir páginas", sem nome de ferramenta;
  - quando a página não abre, a skill pede uma captura de tela ou uma descrição e marca "análise direta não disponível".
- **O registro:** as 3 camadas Observado × Desejado × Recomendado. Só o confirmado vira linha de `## User and Context` (Primary User, User Goal, Primary Pain, Device/Context). O resto vai para "Open UX Questions".
- **A confirmação** é a única pergunta com opções: `**Posso gravar este público em User and Context?**`, com **sim** (recomendado), **ajustar** e **não sei**.
- **No passo 1 da `SKILL.md`**, ao fim do item, uma frase: "Se o DEFINE não diz quem usa e em que contexto, ou se o aluno pedir, conduza antes a entrevista de `references/entrevista-publico.md` e grave o resultado em `## User and Context`."
- **Versão:** 2.3.0.

**Rationale:** mantém o formato da F4 onde há decisão, e não inventa recomendação onde a resposta é um fato.

**Alternatives Rejected:**
1. Opções fechadas para o público, com uma "recomendada": induz a resposta.
2. Copiar o `INTERVIEW_GUIDE.md` inteiro: as seções de identidade visual, tom e governança alimentam o `UX_STANDARD`, que não entra.

**Consequences:** o AT-011 é provado rodando o `skill-lint --conversa` numa skill temporária cujo `references/como-falar.md` é o `entrevista-publico.md`. O texto entra no item 1, numa linha nova, então os primeiros 60 caracteres do item não mudam e o `comandos-intactos` não acusa diferença.

**Nota para a W5 (item H):** o `UX_REVIEW_TEMPLATE.md` vai ganhar a tabela WCAG 2.2 AA. A F5 não muda o template nem fixa critério de contraste, alvo ou nível de conformidade que a contradiga. A entrevista não pergunta por acessibilidade; isso fica com a tabela da W5.

---

### Decision 7: Camada de conversa da `sdd-kb`: bloco comum e etapas

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-10-29 |

**Context:** a `sdd-kb` do starter reprova no `skill-lint --conversa`, e a seção dela não usa o bloco comum das 14 (`FRASES`).

**Choice:**
- **A seção do starter é trocada pela da F4:**
  - abertura de 3 linhas, citando `sdd/templates/fragments/PERGUNTA_DECISAO.md`;
  - a tabela de 5 etapas do starter, com os passos: Domínio `1` · Entender × fazer `2` · Escrever `3 a 5` · Fonte e índice `6 e 7` · Revisão do profissional `8 a 10` ("o aviso de revisão é obrigatório, não é pergunta");
  - o bloco comum copiado byte a byte da `sdd-define`, com o Status `KB: ✅ 1 Domínio · ▶️ 2 Entender × fazer · ⬜ 3 Escrever · ⬜ 4 Fonte e índice · ⬜ 5 Revisão do profissional`.
- **A última regra do bloco** ("No fecho da fase, o resumo de etapa…") **fica**: no build se viu que ela está nas 14 skills, até na `sdd-playbook`, e o bloco segue byte a byte igual nas 15 (correção de build, DESIGN v1.2).
- **A identificação:** `sdd-kb v2.2.0 · out/2026 · versão atual: https://github.com/robertodiasduarte/sdd-open/releases/latest`, "uma vez só, antes do Status".
- **O `como-falar.md`:**
  - mantém o glossário do starter;
  - o exemplo tem a pergunta do perfil com **não** (recomendado: o perfil geral não exige vigência; se aparecer lei ou alíquota, a skill volta a perguntar), **sim** e **não sei**;
  - cita o fragmento;
  - o Próximo passo tem ≤100 caracteres.
- **A seção final "Next Step" do starter** fica, com o texto: a base está em `sdd/kb/<slug>/`; aponte a IA para essa pasta nas próximas conversas; se a base prepara uma feature, o próximo passo é `/sdd-brainstorm`.

**Rationale:** com o bloco comum idêntico, o `test_conversa` cobre a `sdd-kb` junto com as outras 14, e a F9 troca o bloco nas 15 de uma vez.

**Alternatives Rejected:**
1. Manter a seção do starter e só consertar o `como-falar.md`: passaria no lint e falharia nas `FRASES`.

**Consequences:** `test_conversa.F4` passa a ter 15 nomes; o comentário diz "as 14 da F4 + a sdd-kb da F5".

---

### Decision 8: Testes: porte dos 62, casos em tempo de execução, nenhuma fixture nova em `sdd/fixtures/`

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-10-29 |

**Context:** o AT-013 manda as fixtures existentes de `sdd/fixtures/` ficarem idênticas. O `init` copia `sdd/fixtures/` para o aluno, e o publish-gate reprova literal sensível em `tests/`.

**Choice:**
- **`tests/test_sdd_kb_normativo.py`:**
  - cópia do starter, com `ROOT = Path(__file__).resolve().parents[1]` e `SKILL = ROOT / ".agents" / "skills" / "sdd-kb"`;
  - a docstring diz de onde veio, sem o nome do repositório;
  - o interpretador é `sys.executable`, que já é o do starter. Na conferência, se ele chamar `python3` literal, troca por `sys.executable`.
- **`tests/test_sdd_kb.py`** (`apoio.Sandbox`):
  - gate no pacote = 0, com `RESULTADO: VERDE — 4 aceitas, 12 rejeitadas`;
  - gate numa cópia de `.agents/skills/sdd-kb/` dentro de `self.tmp`, sem o resto do pacote, = 0;
  - gate com a cópia do `validate_kb.py` sabotada (a checagem de limite de conceito desligada) = 2 e `🛑 limite-conceito`;
  - gate com uma âncora inexistente (o exemplo de cópia alterado) = 2;
  - `--strict`: os 2 casos vermelhos e o verde, direto no validador;
  - sem `--strict`, os 2 casos = 0;
  - uso 64 (sem argumento; `--xyz`);
  - gate de uma **cópia gerada** (H1): `init --vendors claude` num projeto do `Sandbox` com o pacote; o gate de `.claude/skills/sdd-kb/scripts/` sai 2 com `🛑 cópia gerada` e `→ … .agents/skills/sdd-kb/scripts/gate.sh`; o de `.agents/skills/sdd-kb/scripts/` sai 0;
  - gate com âncora ausente: as 3 linhas da moldura (`🛑 <caso>`, `RESULTADO: VERMELHO`, `→`), não só o exit (M1); no sucesso, a saída é **uma** linha;
  - texto (M4): a `SKILL.md` cita `sdd/kb/_index.yaml` e `.agents/skills/sdd-kb/scripts/validate_kb.py`. Nenhum arquivo da skill, fora do histórico do `CHANGELOG.md` (as entradas abaixo da 2.2.0), cita `pasta de bases`, `.claude/kb`, `kb_dir`, `sdd-starter` ou `scripts/validate_kb.py`/`scripts/kb_normativo.py` sem o prefixo `.agents/skills/sdd-kb/`. Também não há link relativo `](assets/` nem `](scripts/`. A falha nomeia arquivo:linha, e o teste tem de ficar vermelho no texto cru do starter;
  - não há `agents/`.
- **`tests/test_kb_dominios.py`** (`apoio.Sandbox`):
  - monta `<tmp>/sdd/features/DEFINE_X.md` e `<tmp>/sdd/kb/<dom>/` por caso: 2 verdes, 7 vermelhos, 2 de uso, 1 ilegível (bytes `\xff\xfe` escritos e conferidos);
  - a lista de testes do RULE_MAP, com um RULE_MAP do exemplo cuja coluna Teste foi preenchida;
  - a lista truncada em 10 + "e mais N";
  - o texto do passo 10 e do template (AT-010).
- **`tests/test_conversa.py`:**
  - as contagens 16 → 17 e `F4` + `sdd-kb`;
  - uma classe nova `EntrevistaPublico` (AT-011): a frase do passo 1 da ux-review; os termos obrigatórios do arquivo; nenhuma linha `- **Outro`/`- **outro`; o `skill-lint --conversa` sobre a skill temporária (Decision 6); e, contra o aceite circular (M3), a função `perguntas()` do `sdd/bin/skill-lint.py`, carregada por `importlib`, acha **exatamente 1** pergunta de decisão no arquivo, a `**Posso gravar este público em User and Context?**`, e o arquivo tem ≥3 perguntas abertas com a saída "não sei".
- **Atualizações de propósito:** `tests/test_skill_lint.py` (2 testes, 16 → 17), `tests/test_matriz_new_session.py` (`PORTADAS` + `sdd-kb`) e `tests/test_conversa.py` (16 → 17).
- **`tests/test_kb_dominios.py`** também cobre o RULE_MAP com `\|` num localizador (M2): a lista mostra o teste, não a implementação.

**Rationale:** casos em tempo de execução não viajam ao aluno nem mexem em `sdd/fixtures/`.

**Alternatives Rejected:**
1. Fixtures em `sdd/fixtures/kb/`: o `init` as levaria ao aluno, sem uso para ele.

**Consequences:** a suíte cresce em cerca de 62 + 20 + 16 + 4 testes. O tempo extra é o do gate, com ~16 chamadas ao validador, cerca de 3 s.

---

### Decision 9: Versões, exceções de comando e o que fica intacto

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-10-29 |

**Context:** o `check-versions --base v2.2.5 --base-obrigatoria` e o AT-013/AT-014.

**Choice:**
- **Versões:** `sdd-kb` 2.2.0 (nova; o `check-versions` não compara skill que não existe na base), `sdd-define` 2.3.0 e `sdd-ux-review` 2.3.0, as 3 com `updated: "2026-10"`.
- **O `comandos-intactos.py` da F5** é o da F4 com `SKILLS = ("sdd-define", "sdd-ux-review")`, base `v2.2.5` e `EXCECOES` só com a `sdd-define`: as 2 linhas da Decision 5. O regex de comando da F4 (`sdd/bin`, `git`, `gh`, `bash`, `python3`, `scripts/`) não pega o `ls sdd/kb/`. A frase do passo 1 da ux-review não aparece, porque o regex de item só lê os primeiros 60 caracteres e a frase entra numa linha nova.
- **Ficam iguais byte a byte à `v2.2.5`** (log `contratos-intactos.log`, por `git diff --quiet v2.2.5 -- …`):
  - os scripts de `sdd/bin/`: `verify-gate.sh`, `report-lint.py`, `skill-lint.py`, `design-lint.py`, `handoff-lint.py` e `playbook-lint.sh`;
  - os de `scripts/`: `publish-gate.sh` e `check-versions.py`;
  - `sdd/fixtures/` e `UX_REVIEW_TEMPLATE.md`.

**Rationale:** prova mecânica de que só mudou o declarado.

**Alternatives Rejected:**
1. Bump minor da `sdd-kb` como 2.1.1: a camada nova, o `--strict` e a pasta fixa são funcionalidade.

**Consequences:** a pergunta de versão do pacote (`v2.2.6` automática × `v2.3.0` à mão) vai para o bloco do OK da `sdd-release`.

---

## File Manifest

| # | File | Action | Purpose | Agent | Dependencies |
|---|------|--------|---------|-------|--------------|
| 1 | `.agents/skills/sdd-kb/scripts/kb_normativo.py` | Create | Porte; docstring e mensagem do `rule-map` com o caminho do projeto (Decision 1) | (general) | None |
| 2 | `.agents/skills/sdd-kb/scripts/validate_kb.py` | Create | Porte + `raiz_do_projeto` e a checagem de `teste` no `--strict` (Decision 2); caminho na mensagem do RULE_MAP | (general) | 1 |
| 3 | `.agents/skills/sdd-kb/assets/` (10 moldes, `_index.yaml`, `example-kb/`, `example-kb-normativo/`) | Create | Porte; `RULE_TEMPLATE.md` e `CATALOGO_FONTES_TEMPLATE.md` com o caminho do projeto; RULE_MAP do exemplo regerado pelo 1 | (general) | 1 |
| 4 | `.agents/skills/sdd-kb/scripts/gate.sh` | Create | Gate autossuficiente: 4 aceitas, 12 rejeitadas pelo motivo certo, RULE_MAP em dia (Decision 3) | (general) | 1, 2, 3 |
| 5 | `.agents/skills/sdd-kb/references/kb-protocol.md`, `normativo.md`, `sourcing.md` | Create | Porte; caminhos `sdd/kb/` e `.agents/skills/sdd-kb/scripts/` | (general) | 1, 2 |
| 6 | `.agents/skills/sdd-kb/references/como-falar.md` | Create | Formato da F4: glossário, Status, exemplo com pergunta válida, fragmento citado (Decision 7) | (general) | None |
| 7 | `.agents/skills/sdd-kb/SKILL.md` | Create | 2.2.0; identificação; seção da F4; passos com `sdd/kb/` e caminhos do projeto (Decisions 1, 7) | (general) | 3, 4, 5, 6 |
| 8 | `.agents/skills/sdd-kb/CHANGELOG.md` | Create | Entrada 2.2.0 + histórico sem o nome do repositório de origem | (general) | 7 |
| 9 | `sdd/bin/kb-dominios.py` | Create | Lint do KB Domains (Decision 4); 0 · 1 · 64 | (general) | None |
| 10 | `sdd/templates/DEFINE_TEMPLATE.md` | Modify | Linha KB Domains sem "ou equivalente" (Decision 5) | (general) | None |
| 11 | `.agents/skills/sdd-define/SKILL.md` | Modify | 2.3.0; frase do passo 3; `### 10. Conferir o KB Domains`; Quality Gate; tabela de etapas (Decision 5) | (general) | 9, 10 |
| 12 | `.agents/skills/sdd-ux-review/references/entrevista-publico.md` | Create | Entrevista em perguntas abertas + 1 confirmação (Decision 6) | (general) | None |
| 13 | `.agents/skills/sdd-ux-review/SKILL.md` | Modify | 2.3.0; frase no passo 1 (Decision 6) | (general) | 12 |
| 14 | `tests/test_sdd_kb_normativo.py` | Create | Porte dos 62 testes (Decision 8) | (general) | 2, 3 |
| 15 | `tests/test_sdd_kb.py` | Create | Gate (pacote, cópia, sabotagem, âncora), `--strict` dos dois lados, uso, texto da skill (Decision 8) | (general) | 4, 7 |
| 16 | `tests/test_kb_dominios.py` | Create | Casos do lint, lista do RULE_MAP, truncamento, texto do passo 10 e do template (Decision 8) | (general) | 9, 10, 11 |
| 17 | `tests/test_conversa.py` | Modify | 16 → 17; `F4` + `sdd-kb`; classe `EntrevistaPublico` (Decision 8) | (general) | 7, 12, 13 |
| 18 | `tests/test_skill_lint.py` | Modify | 16 → 17 nos 2 testes das skills reais | (general) | 7 |
| 19 | `tests/test_matriz_new_session.py` | Modify | `PORTADAS` + `sdd-kb` | (general) | 7 |
| 20 | `docs/cli-conventions.md` | Modify | Saídas do `kb-dominios.py` e do `gate.sh`; exceção do `validate_kb.py` (`PASS:`/`FAIL:`/`WARN:`, 0/2/64) | (general) | 4, 9 |
| 21 | `MANIFEST.txt` | Modify | Os arquivos novos de 1–9, 12, 14–16 e 25, em ordem `LC_ALL=C` | (general) | 1, 2, 3, 4, 5, 6, 7, 8, 9, 12, 14, 15, 16, 25 |
| 22 | `sdd/reports/evidence/F5_CONHECIMENTO/comandos-intactos.py` | Create | AT-014 (Decision 9); fora do commit do produto | (general) | 11, 13 |
| 23 | `sdd/reports/evidence/F5_CONHECIMENTO/gerar-evidencia.sh` | Create | `baseline`, `check-versions`, `comandos-intactos`, `contratos-intactos`, `codepoints`, `suite-piso`; fora do commit do produto | (general) | 21, 22 |
| 24 | `sdd/reports/evidence/F5_CONHECIMENTO/sabotagem.sh` | Create | 4 sabotagens (AT-016): `validate_kb.py`, `kb_normativo.py`, `gate.sh`, `kb-dominios.py`; fora do commit do produto | (general) | 14, 15, 16 |
| 25 | `.gitattributes` | Create | `.agents/skills/sdd-kb/assets/example-kb-normativo/fontes/** -text` (Decision 1, H1) | (general) | 3 |

**Total Files:** 25

---

## Landmines aplicáveis

| Landmine (⛔) | Fonte | Veredito | Como / Por quê |
|---------------|-------|----------|----------------|
| Fixture só do lado verde não prova o validador | `LM-001` | ✔ tratado | 12 casos rejeitados pela razão certa no gate; sabotagem do validador derruba o gate; `kb-dominios` com 7 vermelhos |
| Baseline vermelho antes do código | `LM-002` | ✔ tratado | `test_sdd_kb.py`, `test_kb_dominios.py` e a classe `EntrevistaPublico` escritos antes dos arquivos que testam; vermelho em `evidence/F5_CONHECIMENTO/baseline.log` |
| Unicode invisível no texto portado | handoff, etapa M1 | ✔ tratado | `codepoints.log`: code points fora de ASCII em `.agents/skills/sdd-kb/`, `entrevista-publico.md` e nas skills tocadas; só emoji, FE0F, ZWJ, letras do português e a tipografia já usada (— · → × ≤ ≥ « ») |
| Literal do G2 nos exemplos normativos | `tests/apoio.py`, A-003 | ✔ tratado | O `publish-gate.sh` em modo `ci` roda dentro do Verify Gate |
| Skill portada citando o starter, com `openai.yaml` ou `tests/` | `Portadas` | ✔ tratado | `PORTADAS` + `sdd-kb` (manifest 19) |
| `rm -rf` com variável vazia | prompt da sessão | ✔ tratado | O `trap` do gate usa a expansão `:?` (Decision 3) |
| `sed -i` diferente em BSD e GNU | bash 3.2/macOS | ✔ tratado | As trocas de texto do gate são feitas em Python inline (`troca`) |

---

## Contrato de aceite

N.A. (1 camada): o manifest só toca texto de skill/template, scripts Python/bash da skill e de `sdd/bin/`, e testes, sem `api`/`ui`/`sql`. A revisão de contexto fresco do build continua obrigatória pela sessão.

---

## Agent Assignment Rationale

Agent Discovery: Not available. Tudo fica `(general)` e no modo default, na mesma conversa. O porte e a camada compartilham o mesmo texto, e um autor só mantém os caminhos e o bloco comum iguais.

---

## Code Patterns

### Pattern 1: Esqueleto do `gate.sh` (bash 3.2)

```bash
#!/usr/bin/env bash
# gate.sh — o validador da KB tem de ACEITAR os exemplos e REJEITAR cada caso ruim pelo motivo certo.
# Roda igual no pacote e no projeto do aluno: acha tudo pela própria pasta e monta os casos numa
# pasta temporária a partir de assets/. Exit 0 verde · 2 vermelho.
set -u
DIR="$(cd "$(dirname "$0")" && pwd)"
V="$DIR/validate_kb.py"; RM="$DIR/kb_normativo.py"; ASSETS="$DIR/../assets"
# PY = $PYTHON ou python3; T = mktemp -d; trap que apaga $T com a expansão :? (Decision 3)
ACEITAS=0; REJEITADAS=0

falha() {  # $1 caso · $2 o que houve · $3 conserto — roda no shell principal, nunca dentro de $( )
  echo "🛑 $1: $2"; [ -f "$T/saida" ] && sed 's/^/    /' "$T/saida"
  echo "RESULTADO: VERMELHO"; echo "→ $3"; exit 2
}
grep -q 'sdd-open:generated' "$0" && falha "cópia gerada pelo sync" "os exemplos daqui têm cabeçalho e não valem como prova" \
  "rode bash .agents/skills/sdd-kb/scripts/gate.sh"
projeto() {  # $1 caso · $2 exemplo de assets/ · $3 perfil — não imprime; o domínio fica em $T/$1/sdd/kb/dom
  mkdir -p "$T/$1/sdd/kb" && cp -R "$ASSETS/$2" "$T/$1/sdd/kb/dom" || falha "$1" "cópia do exemplo falhou" "confira assets/$2"
  printf 'version: "1.0"\ndomains:\n  dom:\n    name: caso\n    description: caso\n    path: dom/\n    perfil: %s\n    updated: 2026-10-29\n' "$3" > "$T/$1/sdd/kb/_index.yaml"
}
troca() {  # $1 caso · $2 arquivo · $3 âncora · $4 substituto — a âncora sumida é falha, nunca um caso sem teste
  "$PY" - "$2" "$3" "$4" <<'PY' || falha "$1" "âncora ausente: $3" "o exemplo mudou; atualize a âncora no gate.sh"
import sys; p, a, b = sys.argv[1:]
t = open(p, encoding="utf-8").read()
if a not in t: sys.exit(1)
open(p, "w", encoding="utf-8").write(t.replace(a, b, 1))
PY
}
rejeita() {  # $1 caso · $2 razão esperada · $3… argumentos do validador
  caso="$1"; razao="$2"; shift 2; rm -f "$T/saida"
  if "$PY" -B "$V" "$@" > "$T/saida" 2>&1; then falha "$caso" "caso ruim ACEITO" "o validador deixou de conferir isto"; fi
  grep -qF -- "$razao" "$T/saida" || falha "$caso" "rejeitado por outro motivo (esperado: $razao)" "confira a mutação e o validador"
  REJEITADAS=$((REJEITADAS + 1))
}
```

### Pattern 2: Checagem de `teste` no `--strict` (`validate_kb.py`)

```python
VAZIO = (None, "", "—", "-", "null")


def raiz_do_projeto(root):
    """<raiz>/sdd/kb/<slug> → <raiz>; fora disso, o diretório corrente (o comando roda da raiz)."""
    r = root.resolve()
    if r.parent.name == "kb" and r.parent.parent.name == "sdd":
        return r.parents[2]
    return Path.cwd()


# dentro de check_normativo, no laço `for path, fm in rules:`, depois do status:
        if strict:
            impl, teste = _s(fm.get("implementacao")), _s(fm.get("teste"))
            impl = None if impl in VAZIO else impl
            teste = None if teste in VAZIO else teste
            if impl and not teste:
                ok = fail("%s: implementacao %r has no teste — --strict requires the test the Verify Gate runs (RULE_TEMPLATE.md)" % (name, impl)) and ok
            elif teste:
                arquivo = teste.split(":", 1)[0].strip()
                if not (projeto / arquivo).is_file():
                    ok = fail("%s: teste %r: %s not found from the project root %s" % (name, teste, arquivo, projeto)) and ok
```

`projeto = raiz_do_projeto(root)` é calculado uma vez, no início de `check_normativo`.

### Pattern 3: Interface do `kb-dominios.py`

```python
#!/usr/bin/env python3
"""kb-dominios.py <DEFINE.md> — o KB Domains do DEFINE só cita pastas de sdd/kb/, ou diz `nenhum`.

0 = válido (lista os testes do RULE_MAP dos domínios citados) · 1 = violação · 64 = uso.
Lê a 1ª linha `| **KB Domains** | … |` fora de bloco de código. A raiz do projeto é a pasta acima de
sdd/features/ quando o DEFINE está lá; senão, o diretório corrente. Não importa nada da sdd-kb.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

LINHA = re.compile(r"^\|\s*\*\*KB Domains\*\*\s*\|([^|]*)\|")
NAO_LISTA = ("n/a", "na", "—", "-", "")  # e a sigla de "a definir" em inglês, sem caixa


def main(argv: list[str]) -> int:
    if len(argv) != 2 or argv[1].startswith("-") or not Path(argv[1]).is_file():
        print("uso: kb-dominios.py <DEFINE.md>", file=sys.stderr)
        return 64
    ...
    print("RESULTADO: VERDE")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
```

### Pattern 4: Skill temporária para checar as perguntas da entrevista (AT-011)

```python
def test_perguntas_da_entrevista_passam_no_lint(self):
    s = self.tmp / "skills" / "sdd-entrevista"
    (s / "references").mkdir(parents=True)
    (s / "SKILL.md").write_text(ler(SKILLS / "sdd-ux-review/SKILL.md").replace(
        "name: sdd-ux-review", "name: sdd-entrevista", 1), encoding="utf-8")
    shutil.copy(ENTREVISTA, s / "references" / "como-falar.md")
    rc, out, err = roda([PYTHON, "-B", RAIZ / "sdd/bin/skill-lint.py", "--conversa", s / "SKILL.md"])
    self.assertEqual(rc, 0, out + err)
```

---

## Data Flow

```text
1. Aluno pede uma base → sdd-kb: Status KB · 1 pergunta (perfil) → … → grava sdd/kb/_index.yaml
   (1ª vez) e sdd/kb/<slug>/ → validate_kb.py sdd/kb/<slug> (0 segue · 2 corrige; a saída é traduzida)
   → aviso de revisão do profissional → como usar
2. Software vai consumir → validate_kb.py --strict: PENDENTE, implementacao sem teste, teste ausente ⇒ 2
3. Alguém quer provar o validador → bash .agents/skills/sdd-kb/scripts/gate.sh → 16 casos em $T → VERDE|VERMELHO
4. sdd-define grava DEFINE (KB Domains de ls sdd/kb/ ou nenhum) → passo 10: kb-dominios.py
   → 0: testes do RULE_MAP → cmd do Verify Gate → verify-gate.sh --print · 1: corrige e roda de novo
5. sdd-ux-review passo 1: DEFINE sem público → entrevista (perguntas abertas, 1 por resposta)
   → resumo Observado × Desejado × Recomendado → confirmação → ## User and Context → passos 2–8
6. Pacote: commit → Verify Gate (publish-gate ci + suíte no piso, gate.sh dentro do test_sdd_kb)
   → PR → CI ubuntu + macOS → OK do Roberto → push main → release
```

Caminho de erro: o gate vermelho no CI bloqueia o PR. O `kb-dominios.py` vermelho impede a entrega do DEFINE: a skill corrige o campo e roda de novo, sem pedir OK.

---

## Integration Points

| External System | Integration Type | Authentication |
|-----------------|-----------------|----------------|
| GitHub Actions (`publish-gate.yml`, `release.yml`) | Sem mudança de workflow; os testes novos entram pelo `unittest discover` e o `skill-lint --conversa` cobre a 17ª skill pelo glob `sdd-*` | `GITHUB_TOKEN` do workflow; falha = PR vermelho, sem retry |
| Agente do aluno (qualquer vendor do `init`) | Lê `SKILL.md` e `references/`; roda os scripts da skill e o `sdd/bin/kb-dominios.py` | N/A. A URL de referência só é aberta quando o agente consegue; senão, captura ou descrição |

---

## Testing Strategy

| Test Type | Scope | Files | Tools | Coverage Goal |
|-----------|-------|-------|-------|---------------|
| Porte | 62 mutações do exemplo normativo | `tests/test_sdd_kb_normativo.py` | unittest | AT-004 |
| Contrato de script | `gate.sh` (pacote, cópia, cópia gerada pelo `init`), `validate_kb.py --strict`, uso | `tests/test_sdd_kb.py` | unittest + `apoio.Sandbox` | AT-002, AT-003, AT-005, AT-006, AT-012, AT-017 |
| Contrato de script | `kb-dominios.py` | `tests/test_kb_dominios.py` | unittest + `apoio.Sandbox` | AT-007–AT-010 |
| Contrato de texto | 17 skills, `sdd-kb`, entrevista | `tests/test_conversa.py`, `test_skill_lint.py`, `test_matriz_new_session.py` | unittest + `skill-lint --conversa` | AT-001, AT-011, AT-012 |
| Regressão | Suíte inteira no piso + publish-gate | `tests/` | Verify Gate do DEFINE | AT-013 |
| Evidência fora do gate | comandos, versões, baseline, contratos, code points | `sdd/reports/evidence/F5_CONHECIMENTO/gerar-evidencia.sh` | bash + git + Python | AT-014, AT-015 e a baseline vermelha |
| Sabotagem | 4 scripts | `sdd/reports/evidence/F5_CONHECIMENTO/sabotagem.sh` | troca por padrão + `git checkout` | AT-016: 4 de 4 vermelhas com o nome do teste |
| CI | PR | `.github/workflows/*.yml` | GitHub Actions | `gate` + `testes-macos` verdes |

Baseline vermelho: os testes novos são escritos antes dos arquivos e rodam no HEAD da branch antes do código. Em `v2.2.5`, falham porque `.agents/skills/sdd-kb/`, `sdd/bin/kb-dominios.py` e `entrevista-publico.md` não existem.

---

## Error Handling

| Error Type | Handling Strategy | Retry? |
|------------|-------------------|--------|
| Uso errado (`kb-dominios.py`, `validate_kb.py`, `kb_normativo.py`) | `uso:` em stderr, exit 64 | No |
| DEFINE ilegível (não UTF-8) | `🛑 … não consegui ler: <erro>`, `RESULTADO: VERMELHO`, `→ confira a permissão e a codificação (UTF-8)`, exit 1 | No |
| RULE_MAP ilegível no `kb-dominios.py` | `⚠️` sem mudar o exit: o RULE_MAP é do `validate_kb.py` | No |
| Conteúdo inesperado no validador | O `try/except` do starter (`normative check stopped …`) com FAIL e exit 2, nunca traceback | No |
| Âncora de mutação ausente no gate | `troca` sai ≠ 0 → gate exit 2 nomeando o caso | No |
| Falta `python3` no aluno | O gate sai 2 com `🛑` do shell ("command not found") e `RESULTADO: VERMELHO`; a `sdd-kb` já diz que o validador exige filesystem e Python | No |
| Diferença não declarada no `comandos-intactos` | `FALHA <skill>` e exit 1; corrigir a skill, nunca ampliar a lista em silêncio | No |

---

## Configuration

| Config Key | Type | Default | Description |
|------------|------|---------|-------------|
| `PYTHON` (env do `gate.sh`) | caminho | `python3` | Interpretador usado no gate; os testes passam o da suíte |
| `--strict` (`validate_kb.py`) | flag | desligada | Antes de software consumir: revisão assinada e `implementacao` → `teste` |
| Pasta da KB | caminho fixo | `sdd/kb/` | Decisão 4 do plano: sem slot no `sdd/config.yaml` |

---

## Security Considerations

- Os scripts só leem o que recebem e a pasta `sdd/kb/`, sem rede e sem `eval`. O gate só escreve em `mktemp -d` e apaga com a expansão `:?`.
- Os exemplos e os casos não têm dado real de pessoa ou empresa, nem literal de `publish-gate-patterns.txt`. A KB real `programa-irpf` não entra em lugar nenhum (decisão 6 do BRAINSTORM).
- A entrevista não reproduz ativo, texto ou implementação da URL de referência; observa e propõe princípio (limites do `URL_ANALYSIS.md`).
- Texto novo sem Unicode invisível e sem `curl … | sh` literal.

---

## Observability

- `kb-dominios.py` e `gate.sh` terminam em `RESULTADO:`, com `→` no vermelho (`docs/cli-conventions.md`).
- Evidência em `sdd/reports/evidence/F5_CONHECIMENTO/`:
  - `baseline.log`, `GATE.log`, `suite-piso.log`, `check-versions.log`;
  - `comandos-intactos.log`, `contratos-intactos.log`, `codepoints.log`;
  - `sabotagem.log`, `skill-lint-conversa.log`, `gate-kb.log`, `ci-pr.log`, `release.log`.
- Sinal depois da entrega (UX review, lente S): DEFINE com `nenhum` × domínio real; reprovações do `kb-dominios.py` no 1º run.

---

## Requirements Traceability

| Requirement / AT | Design Element | Test / Gate |
|---|---|---|
| MUST skill portada / AT-012 | Decision 1; manifest 1–8 | `tests/test_sdd_kb.py`, `test_matriz_new_session.py` |
| MUST camada F4 / AT-001 | Decision 7; manifest 6, 7 | `tests/test_conversa.py`, `test_skill_lint.py` |
| MUST `--strict` teste / AT-005, AT-006 | Decision 2; Pattern 2; manifest 2 | `tests/test_sdd_kb.py`, `test_sdd_kb_normativo.py` |
| MUST `gate.sh` / AT-002, AT-003, AT-017 | Decision 3; Pattern 1; manifest 4 | `tests/test_sdd_kb.py` |
| MUST porte dos 62 / AT-004 | Decision 8; manifest 14 | `tests/test_sdd_kb_normativo.py` |
| MUST `kb-dominios.py` / AT-007–AT-009 | Decision 4; Pattern 3; manifest 9 | `tests/test_kb_dominios.py` |
| MUST passo 10 e template / AT-010 | Decision 5; manifest 10, 11 | `tests/test_kb_dominios.py` |
| MUST entrevista / AT-011 | Decision 6; Pattern 4; manifest 12, 13 | `tests/test_conversa.py` |
| MUST não regressão / AT-013 | Decision 9; manifest 17–19, 21 | Verify Gate |
| MUST comandos intactos / AT-014 | Decision 9; manifest 22 | `evidence/F5_CONHECIMENTO/comandos-intactos.log` |
| MUST versões / AT-015 | Decision 9 | `evidence/F5_CONHECIMENTO/check-versions.log` |
| MUST sabotagem / AT-016 | Testing Strategy; manifest 24 | `evidence/F5_CONHECIMENTO/sabotagem.log` |
| SHOULD WCAG na W5 | Decision 6 (nota) | — |
| SHOULD `cli-conventions` | manifest 20 | revisão |

---

## Risks and Mitigations

| Risk | Impact | Mitigation | Residual Risk |
|---|---|---|---|
| Os 62 testes dependem de detalhe do layout do starter além do caminho | O porte exigiria reescrita | Rodar o arquivo portado antes de mexer no validador; ajustar só o cabeçalho | Baixo |
| A mutação do gate reprova por um 2º motivo (RULE_MAP derivado) | O gate passa sem provar o caso | Razão esperada conferida com `grep -F`; o RULE_MAP é regerado nos casos que mudam regra | Nenhum |
| O exemplo normativo marcado `PENDENTE` impede o caso positivo do `--strict` | O lado verde da checagem nova fica sem prova | Caso `strict-teste-ok` troca a linha do revisor numa cópia | Nenhum |
| Texto portado com caractere invisível ou literal do G2 | CI vermelho | `codepoints.log` + publish-gate dentro do Verify Gate | Nenhum |
| O agente não roda o passo 10 | KB Domains inventado passa | O passo fica logo depois do Gravar, como o `design-lint` da F4; o Quality Gate da define tem a linha | Não verificável em teste (A-002 do DEFINE) |
| O `kb-dominios.py` reprova DEFINE antigo com `N/A` | Atrito numa reedição | O lint só roda no DEFINE gravado agora; a mensagem diz o conserto | Aceito |

---

## Advisor Ledger

Revisão de contexto fresco do DESIGN v1.0 (modo contrato, pedida pelo Roberto), gravada em `sdd/reviews/REVISAO_DESIGN_F5_CONHECIMENTO_20261029.md`, com as sondas em `evidence/F5_CONHECIMENTO/AVAL-DESIGN-*.log`. Veredito: NEEDS_WORK (2 HIGH, 4 MEDIUM, 2 LOW).

| Nota | Decisão | Onde |
|---|---|---|
| H1 adaptador gerado e CRLF quebram o exemplo | APPLIED em parte: caminhos `.agents/skills/sdd-kb/…`, o gate recusa a cópia gerada e o `.gitattributes` só em `fontes/` (o resto é lido como texto; o `-text` amplo mudaria a forma como o git trata ~30 arquivos sem ganho) | Decisions 1, 3, 8; manifest 25; AT-017 |
| H2 exceção do `comandos-intactos` não bate com o bloco | APPLIED: passo 10 em prosa, sem bloco cercado | Decision 5 |
| M1 subshell engole `falha` | APPLIED | Decision 3; Pattern 1; AT-003 |
| M2 `\|` no RULE_MAP | APPLIED | Decision 4; Decision 8 |
| M3 aceite circular da entrevista | APPLIED: `perguntas()` do `skill-lint` por `importlib`, exatamente 1 pergunta de decisão, ≥3 abertas | Decision 8; AT-011 |
| M4 teste de texto fraco | APPLIED | Decision 8; AT-012 |
| L1 fidelidade das fixtures do starter | APPLIED | Decision 3 |
| L2 `teste` é caminho; ordem `RESULTADO` → `→` | APPLIED | Decisions 1, 4 |

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.4 | 2026-10-29 | SDD Build by RDD | Ciclo 2 (PASS, 3 LOW aplicados): domínio ilegível e BOM no `kb-dominios.py`; `kb_normativo.py` quebrado com diagnóstico próprio no gate; contenção do `teste` pela forma do caminho (`normpath`), não pelo destino do link |
| 1.3 | 2026-10-29 | SDD Build by RDD | Ciclo 1 da revisão do build (M1–M3, L1–L6): KB Domains só do Technical Context; `sdd/kb/` ilegível sem traceback; `teste` fora da raiz reprova; o gate confere o RULE_MAP do exemplo antes dos casos e limpa a saída por caso; a linha 🛑 da cópia gerada traz o caminho; testes de caso bom rejeitado e de outro motivo |
| 1.2 | 2026-10-29 | SDD Build by RDD | Decision 7: a regra "No fecho da fase…" fica no bloco da `sdd-kb` (está nas 14, inclusive na `sdd-playbook`), e o bloco é idêntico nas 15 |
| 1.1 | 2026-10-29 | SDD Design by RDD | Revisão de contexto fresco (Advisor Ledger): 8 notas aplicadas, a H1 em parte; manifest 25 (`.gitattributes`); DEFINE v1.3 |
| 1.0 | 2026-10-29 | SDD Design by RDD | Initial version. DEFINE v1.2: o gate aceita 4 casos (o 4º, `strict-teste-ok`, é o lado verde da checagem nova do `--strict`, que precisa do exemplo revisado) |

---

## Next Step

Execute o **SDD Build by RDD**.
