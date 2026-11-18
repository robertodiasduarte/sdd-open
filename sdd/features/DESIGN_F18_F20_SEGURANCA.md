# DESIGN: F18 + F20 — segurança embutida no fluxo (alerta) e ações preventivas (prevenção)

> Um catálogo de 22 fichas na skill nova `sdd-seguranca` é a fonte única; um script lê o catálogo e serve a varredura do release, as regras do `AGENTS.md`, as regras da stack no build e a lista da passada 0c; as skills de fase só apontam para ele.

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | F18_F20_SEGURANCA |
| **Date** | 2026-11-11 |
| **Author** | design-agent |
| **DEFINE** | `sdd/features/DEFINE_F18_F20_SEGURANCA.md` (v1.1) |
| **Status** | Ready for Build |

---

## Architecture Overview

```text
            .agents/skills/sdd-seguranca/references/CATALOGO_SEGURANCA.md   (22 fichas S01–S22: fonte única)
                                        │  lido só por um parser
                                        ▼
                         sdd/bin/seguranca-varredura.sh  (bash 3.2 + Python stdlib embutido)
       ┌──────────────┬───────────────┬──────────────┬───────────────┬──────────────────┐
       │ (padrão)     │ --agents      │ --regras     │ --checklist   │ --stack          │
       │ varredura    │ bloco do      │ frases da    │ lista fixa da │ stack + origem   │
       │ 0/1/2/64     │ AGENTS.md     │ stack (build)│ passada 0c    │                  │
       ▼              ▼               ▼              ▼               ▼
  sdd-release 0a   bin/sdd-open.sh  sdd-build     sdd-release 0c   sdd-seguranca (modos)
  (2 = NON_WAIVABLE init/sync        passo 4        (5 primeiro)
   1 = CONCERNS)   ({{SEGURANCA}})
                                        ▲
  stack: sdd/config.yaml security.stack ─┤  (vazio ⇒ detecta: supabase/ · vercel.json · package.json · .html)
  teto:  sdd/config.yaml security.max_warnings (vazio ⇒ 5)
  base:  origin/<project.default_branch> (ou --base; sem ela ⇒ tudo é acrescentado)

  Fases (texto, sem script novo):
  sdd-brainstorm ─ perfil de risco (3 linhas) ─▶ sdd-define passo 12 ─ sdd-seguranca modo Define (mesma sessão, sem trava)
       ─▶ linha | **Segurança** | no DEFINE ─▶ sdd-design ## Segurança ("como evitar" como decisão; design-lint avisa)
       ─▶ sdd-build (regras da stack; BUILD_REPORT ## Segurança: recusados e adiados) ─▶ sdd-release (varredura + 0c + fecho)
  A qualquer hora: sdd-seguranca modo incidente (references/INCIDENTE.md)
```

---

## Components

| Component | Purpose | Technology |
|---|---|---|
| Catálogo | 22 fichas com campos fixos: alerta, prevenção, prova à mão, AT modelo, referência pública | Markdown estruturado |
| `seguranca-varredura.sh` | único leitor do catálogo; varredura, stack, regras, checklist, bloco do `AGENTS.md` | bash 3.2 + `python3 -B -` embutido (molde de `eval-revisores.sh`) |
| `sdd-seguranca` | modos Define, checklist antes de publicar, app publicado, incidente | skill (SKILL.md + references) |
| `bin/sdd-open.sh` | `init`/`sync` preenchem `{{SEGURANCA}}` com a saída de `--agents` | bash |
| Skills de fase e templates | apontam para a skill e para o script | texto |
| `design-lint.py` | aviso (sem reprovar) quando o DEFINE tem item aplicado e o DESIGN não tem `## Segurança` | Python |

---

## Key Decisions

### Decision 1: Catálogo em fichas por item com campos fixos

| **Status** | Accepted | · | **Date** | 2026-11-11 |

**Context:** o brainstorm escolheu uma fonte estruturada única (abordagem A) e a descreveu como "tabela rígida". Com 13 campos, vários de uma frase inteira, uma tabela Markdown fica ilegível na web (quem usa claude.ai ou ChatGPT lê o arquivo) e exige escapar `|` dentro das expressões regulares.
**Choice:** `### Snn — <falha>` seguido de exatamente 13 linhas `- <campo>: <valor>`, nesta ordem: `stack`, `fase`, `gravidade`, `bloqueia`, `agents`, `gatilho`, `padrao`, `arquivos`, `frase`, `evitar`, `at`, `confira`, `ref`. Linha com forma de campo fora da ordem, campo repetido, campo faltando ou valor fora do domínio ⇒ catálogo ilegível (exit 64), nunca ignorado (LM-005).
**Rationale:** continua uma fonte só, lida por um parser só; fica legível como manual.
**Alternatives Rejected:** 1. tabela de 13 colunas — rejeitada pela leitura na web e pelo escape de `|`. · 2. TSV ao lado do Markdown — duas fontes.
**Consequences:** o DEFINE AT-008 passa de "22 linhas" para "22 itens" (DEFINE v1.1); o teste do catálogo confere a gramática.

### Decision 2: Um script, um parser, cinco modos

| **Status** | Accepted | · | **Date** | 2026-11-11 |

**Context:** varredura, regras do `AGENTS.md`, regras do build e lista do release leem o mesmo catálogo; a LM-005 registra divergência entre duas cópias da mesma regra.
**Choice:** `sdd/bin/seguranca-varredura.sh` com os modos: (padrão) varredura · `--stack` · `--regras` · `--checklist` · `--agents`. Opções: `--raiz <dir>` (padrão: raiz git do diretório atual), `--catalogo <arq>` (padrão: `<raiz>/.agents/skills/sdd-seguranca/references/CATALOGO_SEGURANCA.md`), `--base <ref>`, `--saida <arq>`. O `init`/`sync` chamam o **script do pacote** com `--agents --raiz <projeto> --catalogo <pacote>/…` (o bloco do `AGENTS.md` vem do pacote, como o resto do bloco).
**Rationale:** um parser; o `init` não reimplementa nada.
**Alternatives Rejected:** 1. módulo Python separado importado por dois scripts — duas portas de entrada para o mesmo arquivo. · 2. `init` com o próprio leitor — LM-005.
**Consequences:** o `init` passa a precisar de Python para as regras; sem Python, só o ponteiro e um ⚠️ dizendo por quê (Decision 9).

### Decision 3: "Acrescentado" pelo diff da árvore de trabalho contra a base

| **Status** | Accepted | · | **Date** | 2026-11-11 |

**Context:** bloquear só o que a publicação acrescenta (brainstorm, decisão 5); base `origin/<project.default_branch>` (DEFINE, clarificação).
**Choice:** linhas acrescentadas = `git -c core.quotepath=off diff --no-color --no-ext-diff -U0 --no-renames --src-prefix=a/ --dst-prefix=b/ <base> --` (prefixos e nomes com acento fixados, qualquer que seja o `diff.noprefix` e o `core.quotePath` da pessoa) (árvore de trabalho contra a base, inclui o que está commitado na branch e o que não está) + todo arquivo não rastreado e não ignorado (`git ls-files --others --exclude-standard`). Base: `--base`, senão `origin/<default_branch>` lido de `sdd/config.yaml` (vazio ⇒ `main`). `git rev-parse --verify --quiet <base>^{commit}` falha ⇒ toda linha é acrescentada e a saída diz `⚠️ base <ref> não existe: tudo conta como novo`. Achado em linha não acrescentada ⇒ `(já existia)`, nunca bloqueio. `--no-renames` porque um arquivo movido não pode esconder uma linha nova (LM-007).
**Rationale:** a 1ª publicação depois da instalação não trava por tabela antiga, e o projeto sem remoto não passa calado.
**Alternatives Rejected:** 1. diff só do commit (`HEAD`) — perde o que ainda não foi commitado. · 2. sem base, só avisar — a chave nova de quem não tem remoto passaria.
**Consequences:** S01 avalia **toda** `create table` das migrações da árvore: em linha acrescentada, bloqueia; em linha antiga, vira aviso "(já existia)". O `enable row level security` vale em qualquer migração da árvore (velha ou nova).

### Decision 4: Arquivos varridos e o que fica de fora

| **Status** | Accepted | · | **Date** | 2026-11-11 |

**Context:** o catálogo, as skills e os documentos SDD citam os próprios padrões (`eval(`, `dangerouslySetInnerHTML`); varrê-los é falso positivo garantido.
**Choice:** varre `git ls-files -co --exclude-standard`, menos: `.agents/`, `.claude/`, `.cursor/`, `.gemini/`, `.codex/`, `.kimi/`, `sdd/`, `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `node_modules/`; pula arquivo binário (byte nulo nos primeiros 8 KB) e arquivo acima de 1 MB, contando quantos pulou numa linha. Cada ficha restringe ainda mais por `arquivos:` (globs `fnmatch` separados por vírgula, casados contra o caminho relativo e contra o nome; `*` = todos os varridos). S01 também aceita os globs de `layers: sql:`.
**Rationale:** o pacote do SDD não é o app do aluno; o resto do repositório é.
**Alternatives Rejected:** 1. slot de pastas ignoradas — YAGNI (a dispensa na linha resolve o caso pontual). · 2. não varrer `tests/` — o teste do aluno também pode ter chave real.
**Consequences:** no próprio pacote, os testes da varredura têm linhas que acusam; elas levam a dispensa na linha (dogfood da Decision 7).

### Decision 5: As duas regras que bloqueiam

| **Status** | Accepted | · | **Date** | 2026-11-11 |

**Context:** S01 e S11 são as únicas `bloqueia: sim`. S01 não é uma linha só (a tabela e o RLS podem estar em arquivos diferentes); S11 é uma família de formatos.
**Choice:** `padrao: regra:rls` — para cada `create table [if not exists] <nome>` das migrações (palavras-chave sem diferença de caixa; tabela de outro esquema que não `public` fica fora, porque a API não a expõe), normaliza o nome (tira `public.` e aspas, minúsculas) e procura `alter table [only] [if exists] <nome> enable row level security` em qualquer migração da árvore, com a mesma normalização; sem ⇒ 🛑. `padrao: re:` para S11 com a alternância dos formatos: cabeçalho de chave privada (`-----BEGIN [A-Z ]*PRIVATE KEY-----`), `\bsk-(?:proj-|svcacct-|admin-)?` seguido de 32 ou mais caracteres de chave com pelo menos um dígito (uma classe CSS como `sk-fading-circle-spinner` não é chave), `sk_live_[A-Za-z0-9]{16,}`, `ghp_[A-Za-z0-9]{30,}`, `github_pat_[A-Za-z0-9_]{30,}`, `AKIA[0-9A-Z]{16}`, e `SERVICE_ROLE[A-Z_]*\s*[:=]\s*['"]?eyJ[A-Za-z0-9_-]{10,}`. A saída mostra id, arquivo e linha, **nunca** o trecho.
**Rationale:** formato com corpo de chave não casa com `process.env.X`, `Deno.env.get("X")` nem `os.environ["X"]` (o nome sem valor).
**Alternatives Rejected:** 1. entropia — falso positivo em hash e id. · 2. lista de nomes de variável — o nome não é o segredo.
**Consequences:** chave fora desses formatos passa (registrado em Assumptions e no `confira`); os testes montam as chaves falsas em tempo de execução, e o pacote não carrega texto com forma de segredo.

### Decision 6: Teto e ordem dos avisos

| **Status** | Accepted | · | **Date** | 2026-11-11 |

**Context:** teto de 5 por fase (brainstorm, decisão 7).
**Choice:** `security.max_warnings` (vazio ou inválido ⇒ 5; inteiro ≥ 1). Ordem (AT-004): gravidade `alta` > `media` > `baixa`; no empate, novo antes de "já existia"; depois o id; depois arquivo e linha. A tela mostra os N primeiros avisos e `… e mais K aviso(s): lista inteira em <arquivo>` (sem `--saida`: `… e mais K aviso(s): rode com --saida <arquivo> para ver todos`). Bloqueios sempre aparecem e não contam. `--saida` grava tudo: bloqueios, avisos, aceitos, "já existia", pulados.
**Rationale:** o mais grave e o mais novo primeiro; nada some (está no arquivo).
**Alternatives Rejected:** sem teto — ruído.
**Consequences:** a `sdd-release` passa `--saida sdd/reports/evidence/{F}/SEGURANCA.log`.

### Decision 7: Dispensa na linha

| **Status** | Accepted | · | **Date** | 2026-11-11 |

**Context:** falso positivo não pode travar para sempre nem sumir calado (brainstorm, decisão 6).
**Choice:** a expressão `sdd-seguranca: aceito (S\d\d) [—-] (.*)` na linha do achado ou na de cima, dentro de qualquer comentário (motivo vazio também é reconhecido, para poder ser acusado). O motivo termina no fim do comentário (`*/`, `-->`), tem todo trecho com forma de segredo trocado por `[…]` e no máximo 160 caracteres: o valor de uma chave nunca chega à saída. Id igual ao do achado e motivo com pelo menos 3 caracteres que não são espaço ⇒ o achado vira `✔ aceito Snn <arquivo>:<linha> — <motivo>`, listado uma vez, fora do bloqueio, do aviso e do teto. Id diferente ou motivo curto ⇒ o achado continua e ganha `⚠️ dispensa sem motivo (ou de outro item) não vale: <arquivo>:<linha>`.
**Rationale:** o motivo fica no código, ao lado do que ele dispensa, e o relatório o mostra.
**Alternatives Rejected:** arquivo de exceções separado — perde o vínculo com a linha.
**Consequences:** a dispensa de S11 numa linha com uma chave real é possível; o `confira` de S11 diz que chave real nunca se dispensa: se vazou, é incidente.

### Decision 8: Stack e slots

| **Status** | Accepted | · | **Date** | 2026-11-11 |

**Context:** P2: um item só dispara com a stack dele (DEFINE AT-006).
**Choice:** `security.stack` cheio passa por cima (lista por vírgula de `supabase`, `vercel`, `web`, ou `nenhuma`); valor desconhecido ⇒ uso, exit 64 com o valor. Vazio ⇒ detecta: `supabase` (pasta `supabase/` ou `"@supabase/` no `package.json`), `vercel` (`vercel.json`, pasta `.vercel/` ou `"vercel"` no `package.json`), `web` (`package.json`, ou um `.html` na lista de arquivos varridos). Item com `stack: todas` sempre vale. Leitura do `sdd/config.yaml` pelo mesmo mini-parser de mapa de 1 nível que `report-lint.py` usa (copiado, não importado: o script é autossuficiente).
**Rationale:** detecção que acerta o caso comum; o slot conserta o resto.
**Alternatives Rejected:** só slot — o aluno não preenche.
**Consequences:** `--stack` imprime `stack: supabase, web (detectada)` ou `(slot security.stack)`.

### Decision 9: O bloco de segurança do `AGENTS.md`

| **Status** | Accepted | · | **Date** | 2026-11-11 |

**Context:** 5 regras + 1 ponteiro, filtradas pela stack; `sync` refaz quando a stack muda (DEFINE AT-007).
**Choice:** o `AGENTS.md.tmpl` ganha uma linha que é só `{{SEGURANCA}}`, dentro de uma seção `### Segurança ao construir`. `gerar_corpo_agents` roda `bash "${PKG}/sdd/bin/seguranca-varredura.sh" --agents --raiz "${ROOT}" --catalogo "${PKG}/.agents/skills/sdd-seguranca/references/CATALOGO_SEGURANCA.md"` num arquivo temporário e troca a linha por ele (`sed -e '/^{{SEGURANCA}}$/{' -e "r ${arq}" -e 'd' -e '}'`). `--agents` imprime até 5 linhas `- <frase>` (fichas `agents: sim` da stack) e a linha fixa do ponteiro. Exit ≠ 0, sem Python ou sem catálogo ⇒ só o ponteiro, e o `init`/`sync` imprimem `⚠️ AGENTS.md: regras de segurança da stack fora (<motivo>) — o ponteiro para a sdd-seguranca ficou` (LM-017: o caminho reserva nunca é calado). Como o corpo esperado depende da stack, o `sync --check` acusa o bloco divergente quando a stack muda.
**Rationale:** o bloco continua gerado do pacote, num lugar só; o tamanho cresce ≤ 2 KB.
**Alternatives Rejected:** regras fixas no template sem filtro — regra de Supabase em projeto sem Supabase.
**Consequences:** um teste mede que o caminho principal rodou (as frases da stack aparecem), não só que o bloco saiu.

### Decision 10: Revisão de segurança do Define na própria sessão, sem trava

| **Status** | Accepted | · | **Date** | 2026-11-11 |

**Context:** decisão do Roberto no Define (clarificação): a mesma sessão roda a `sdd-seguranca`; o alerta não bloqueia.
**Choice:** passo 12 da `sdd-define`, depois da governança: segue o modo Define da skill. Sem gatilho (`gatilho:` das fichas: login, rota pública, dado de terceiros, upload, chamada a IA paga, banco) no DEFINE nem no perfil de risco do BRAINSTORM ⇒ `| **Segurança** | N.A. — <motivo> | <data> |`. Com gatilho, as fichas com `at:` da stack e do gatilho, até 5 por vez, em ordem de gravidade, uma pergunta `[D2 · muda o produto]` por item: **aplicar** (o `at:` adaptado vira AT novo com teste negativo e entra no Verify Gate) · **recusar com motivo** · **adiar**. Linha final: `| **Segurança** | <a> aplicados (Snn, …) · <r> recusados (Snn, …) · <d> adiados (Snn, …) | <data> |`, e uma subseção `### Segurança` em `## Clarifications` com o motivo de cada recusa e adiamento. O `verify-gate.sh` não lê a linha (não muda).
**Rationale:** catálogo mecânico; o custo de uma 2ª parada em todo Define não se paga sem trava.
**Alternatives Rejected:** revisor fresco com trava, como a governança — recusado pelo Roberto.
**Consequences:** o `sdd-decisoes-lint` passa a contar 1 pergunta a mais; o build e o design leem a linha e a subseção.

### Decision 11: Onde cada fase encosta

| **Status** | Accepted | · | **Date** | 2026-11-11 |

**Context:** brainstorm, bloco 1 validado.
**Choice:**
- `sdd-brainstorm` 2.3.0: no passo 2, uma pergunta aberta com as 3 (quem pode ver · quem pode mudar · quanto alguém pode pedir), com "não sei"; o template ganha `## Perfil de risco` com as 3 linhas.
- `sdd-define` 2.6.0: passo 12 (Decision 10); o template ganha a linha `| **Segurança** | pendente | passo 12 |` no Technical Context.
- `sdd-design` 2.6.0: o template troca `## Security Considerations` por `## Segurança` com 5 itens fixos (onde mora cada segredo · RLS por tabela · credencial de cada agente · cabeçalhos e CORS do host · itens aplicados no Define, com o `evitar:` da ficha como decisão); `design-lint.py` imprime `⚠️` e sai 0 quando o DEFINE ao lado tem a linha `Segurança` com `aplicados` > 0 e o DESIGN não tem `## Segurança` com conteúdo.
- `sdd-build` 2.9.0 (passo 4, antes da 1ª tarefa): `bash sdd/bin/seguranca-varredura.sh --regras` e seguir as frases; no BUILD_REPORT, `## Segurança` com a tabela `Item · Decisão · Motivo` dos recusados e adiados (vazia ⇒ `nenhum`), uma vez.
- `sdd-release` 2.11.0: item 10 do 0a (varredura com `--saida`; 2 ⇒ NON_WAIVABLE; 1 ⇒ CONCERNS e os avisos no bloco do OK; 64/127 ⇒ abortar com a frase de atualizar `sdd/bin/`); 0c em **toda** publicação, seguindo `--checklist` (os 5 `agents: sim` primeiro) contra o diff; na tabela NON_WAIVABLE, "bloqueio da varredura de segurança"; no fecho, a linha que aponta o modo "app publicado" e o modo incidente da `sdd-seguranca`.
**Rationale:** cada fase lê o que precisa do mesmo catálogo.
**Alternatives Rejected:** copiar trechos do catálogo nas skills — duas fontes.
**Consequences:** 5 skills sobem de versão; contagens fixadas mudam.

### Decision 12: Saída e exits

| **Status** | Accepted | · | **Date** | 2026-11-11 |

**Context:** `docs/cli-conventions.md`.
**Choice:** varredura: `0` `RESULTADO: NADA ACHADO` · `1` `RESULTADO: AVISOS` · `2` `RESULTADO: BLOQUEADO` · `64` `RESULTADO: ERRO DE USO` (opção, slot inválido, catálogo ilegível com `arquivo:linha`, fora de git sem `--raiz`). Os modos `--stack`, `--regras`, `--checklist`, `--agents` saem 0 ou 64. Python ausente ⇒ guarda `sdd_python_pronto` com a mensagem própria e exit 64.
**Rationale:** palavras novas (`AVISOS`, `NADA ACHADO`) no vocabulário; `BLOQUEADO` já existe.
**Alternatives Rejected:** exit 1 para bloqueio — confunde com aviso.
**Consequences:** linha nova na tabela de exits de `docs/cli-conventions.md`.

---

## File Manifest

| # | File | Action | Purpose | Agent | Dependencies |
|---|------|--------|---------|-------|--------------|
| 1 | `.agents/skills/sdd-seguranca/references/CATALOGO_SEGURANCA.md` | Create | 22 fichas, texto próprio, referência pública | (general) | None |
| 2 | `sdd/bin/seguranca-varredura.sh` | Create | parser único e os 5 modos | (general) | 1 |
| 3 | `tests/test_seguranca_varredura.py` | Create | AT-001 a AT-006 (repositórios temporários, casos que acusam e que não acusam) | (general) | 2 |
| 4 | `tests/test_seguranca_catalogo.py` | Create | AT-008 (gramática, bloqueios, cobertura de padrão, sem citação do material de origem) | (general) | 1, 2 |
| 5 | `sdd/config.example.yaml` | Modify | slots `security.stack` e `security.max_warnings` | (general) | None |
| 6 | `AGENTS.md.tmpl` | Modify | seção "Segurança ao construir" com `{{SEGURANCA}}`; linha da `sdd-seguranca` na tabela | (general) | None |
| 7 | `bin/sdd-open.sh` | Modify | `gerar_corpo_agents` com `--agents` e o ⚠️ do caminho reserva | (general) | 2, 6 |
| 8 | `tests/test_sdd_open.py` | Modify | AT-007 (com e sem Supabase, sem catálogo, `sync --check`, tamanho) | (general) | 7 |
| 9 | `.agents/skills/sdd-seguranca/references/INCIDENTE.md` | Create | modo incidente: fechar, preservar, dimensionar, corrigir, comunicar (LGPD/ANPD), registrar | (general) | None |
| 10 | `.agents/skills/sdd-seguranca/references/como-falar.md` | Create | glossário, Status e exemplo | (general) | None |
| 11 | `.agents/skills/sdd-seguranca/SKILL.md` | Create | 4 modos, gatilhos, N.A., camada de conversa | (general) | 1, 9, 10 |
| 12 | `.agents/skills/sdd-seguranca/manifest.json` | Create | núcleo, caminhos, executados, pendentes | (general) | 11 |
| 13 | `.agents/skills/sdd-seguranca/evals/cases.json` | Create | os 2 cenários executados e os escritos | (general) | 11 |
| 14 | `sdd/templates/BRAINSTORM_TEMPLATE.md` | Modify | `## Perfil de risco` | (general) | None |
| 15 | `sdd/templates/DEFINE_TEMPLATE.md` | Modify | linha `Segurança` no Technical Context | (general) | None |
| 16 | `sdd/templates/DESIGN_TEMPLATE.md` | Modify | `## Segurança` com 5 itens | (general) | None |
| 17 | `sdd/templates/BUILD_REPORT_TEMPLATE.md` | Modify | `## Segurança` (recusados e adiados) | (general) | None |
| 18 | `sdd/bin/design-lint.py` | Modify | aviso sem reprovar | (general) | 16 |
| 19 | `tests/test_design_lint.py` | Modify | o aviso e o exit 0 | (general) | 18 |
| 20 | `.agents/skills/sdd-brainstorm/SKILL.md` | Modify | as 3 perguntas e o perfil de risco; 2.3.0 | (general) | 14 |
| 21 | `.agents/skills/sdd-define/SKILL.md` | Modify | passo 12; 2.6.0 | (general) | 11, 15 |
| 22 | `.agents/skills/sdd-design/SKILL.md` | Modify | seção Segurança; 2.6.0 | (general) | 16, 18 |
| 23 | `.agents/skills/sdd-build/SKILL.md` | Modify | `--regras` no passo 4; tabela no BUILD_REPORT; 2.9.0 | (general) | 2, 17 |
| 24 | `.agents/skills/sdd-release/SKILL.md` | Modify | 0a item 10, 0c fixa, NON_WAIVABLE, fecho; 2.11.0 | (general) | 2, 11, 34 |
| 25 | `tests/test_f18_f20_textos.py` | Create | AT-009 e versões | (general) | 11, 20–24 |
| 26 | `docs/security.md` | Create | como a segurança entra no fluxo (inglês) | (general) | 2, 11 |
| 27 | `docs/pt-BR/security.md` | Create | o mesmo em português | (general) | 26 |
| 28 | `docs/cli-conventions.md` | Modify | palavras e exits do script novo | (general) | 2 |
| 29 | `README.md` | Modify | skill na lista; link do doc | (general) | 26 |
| 30 | `README.pt-BR.md` | Modify | o mesmo | (general) | 27 |
| 31 | `docs/pt-BR/guia-do-aluno.md` | Modify | ficha `#### sdd-seguranca` | (general) | 11 |
| 32 | `MANIFEST.txt` | Modify | arquivos novos | (general) | 1–31 |
| 33 | `tests/test_skill_lint.py`, `tests/test_docs.py`, `tests/test_f14_textos.py`, `tests/test_decisoes_lint.py` e outros com contagem ou versão fixada | Modify | 21 skills, versões e perguntas novas (AT-010) | (general) | 11, 20–24 |
| 34 | `.agents/skills/sdd-release/references/seguranca.md` | Create | o detalhe da varredura, da 0c e do fecho (a `sdd-release` cabe em 500 linhas) | (general) | 2, 11 |

**Total Files:** 34

---

## Landmines aplicáveis

Varredura rodada em 2026-11-11 pelas superfícies do manifest (`verify-gate`, `git archive`, `baseline`, `heurística`, `regressão`, `publish-gate`, `[0-9]{11,}`, `subprocess`, `PYTHONIOENCODING`, `fallback`, `evals`, `cenário comportamental`, `sabotagem`, `edição por script`, `exit 0`, `review`, `openrouter`, `Windows`, `manifest.json`); entradas inteiras lidas.

| Landmine (⛔) | Fonte | Veredito | Como / Por quê |
|---|---|---|---|
| Gate que só confere fiação | LM-001 | ✔ tratado | os testes executam a varredura em repositórios temporários com caso que acusa e caso que não acusa; mutantes do critério de sucesso |
| Asserção que não avalia nada | LM-002 | ✔ tratado | cada teste novo roda contra `69b7f6b` (cópia de `git archive`) e tem de cair lá |
| Review sobre diff vazio | LM-003 | ✔ tratado | commit antes de cada rodada; `git diff --stat` conferido contra a lista da revisão |
| Heurística sobre texto livre que regride | LM-005 | ✔ tratado | o catálogo é a fonte estruturada (Decision 1); um parser só (Decision 2); linha com forma de campo fora da gramática é erro |
| Self-test fora do git | LM-006 | ✔ tratado | o Verify Gate roda em cópia de `git archive`; a varredura (modo padrão) fora de git sai 64 com a causa, e o teste confere o exit exato; os modos de leitura (`--stack`, `--regras`, `--checklist`, `--agents`) funcionam sem git |
| Rename esconde código | LM-007 | ✔ tratado | `--no-renames` no diff (Decision 3) |
| Saldo da OpenRouter | LM-008 | ✔ tratado | `/credits` antes de cada rodada paga, anotado no ledger |
| Sabotagem que desfaz conserto | LM-009 | ✔ tratado | mutantes só em cópia de `git archive` |
| 2º revisor que estoura o teto | LM-010 | ✔ tratado | `--no-revisor2`, com a dispensa registrada no `--conferir` |
| Cenário nunca executado | LM-011 | ✔ tratado | 2 cenários × 3 execuções em contexto novo, com o critério escrito antes |
| Número com 11 dígitos no pacote | LM-012 | ✔ tratado | nenhum id de run nem hash inteiro nos arquivos novos; a referência pública usa ids curtos (CWE-nnn) |
| Teste sumido por edição por corte | LM-013 | ✔ tratado | `grep -c "def test_"` antes e depois de cada edição de teste por script |
| `text=True` sem encoding | LM-014 | ✔ tratado | os testes usam `Sandbox.roda` de `tests/apoio.py` (`encoding="utf-8"`) |
| Python num pipe no Windows | LM-015 | ✔ tratado | o script lê `sdd/bin/lib/python.sh`, que exporta `PYTHONIOENCODING` |
| Teto por grupo de processos | LM-016 | N.A. | a varredura não usa rede nem teto de tempo |
| Fallback silencioso | LM-017 | ✔ tratado | o caminho reserva do `AGENTS.md` imprime ⚠️ com o motivo (Decision 9), e um teste prova que o caminho principal rodou |
| Migração "aplicada" sem prova | LM-004 | N.A. | esta frente não aplica migração; S01 só lê texto |

---

## Contrato de aceite

N.A. (1 camada): o manifest toca o pacote (texto de skill, scripts e testes); `layers:` do pacote está vazio.

---

## Agent Assignment Rationale

| Agent | Files Assigned | Why This Agent |
|---|---|---|
| (general) | 1–33 | o pacote não tem agentes especialistas; o build é desta sessão |

---

## Code Patterns

### Pattern 1: Ficha do catálogo

```markdown
### S01 — Tabela sem RLS
- stack: supabase
- fase: define
- gravidade: alta
- bloqueia: sim
- agents: sim
- gatilho: banco
- padrao: regra:rls
- arquivos: supabase/migrations/*.sql
- frase: Toda tabela nasce com RLS ligada e uma política por operação, restrita ao dono da linha; nenhuma política usa `true`.
- evitar: <decisão de design em 1 a 2 frases>
- at: If um usuário de outra conta, ou sem login, consulta a tabela <T>, then the system shall devolver zero linhas (teste com duas contas e uma anônima).
- confira: <passo a passo à mão, sem script>
- ref: OWASP A01:2021 · CWE-284
```

Domínios: `stack`: todas, supabase, vercel ou web · `fase`: define, design, build, release ou bancada · `gravidade`: alta, media ou baixa · `bloqueia` e `agents`: sim ou nao · `gatilho`: login, rota-publica, dado-de-terceiros, upload, ia, banco ou sempre (vírgula) · `padrao`: `re:` + expressão entre crases, `regra:rls`, `regra:definer` ou `só à mão`.

### Pattern 2: Carga do Python e Python embutido (molde de `eval-revisores.sh`)

```bash
#!/usr/bin/env bash
# seguranca-varredura.sh — … (cabeçalho com uso, modos e exits)
set -uo pipefail
_d="${BASH_SOURCE[0]%/*}"; [ "${_d}" = "${BASH_SOURCE[0]}" ] && _d=.
if [ -f "${_d}/lib/python.sh" ]; then . "${_d}/lib/python.sh"
else sdd_python_pronto() { command -v python3 >/dev/null 2>&1; }; sdd_python_exigir() { :; }; fi
if ! sdd_python_pronto; then
  echo "🛑 seguranca-varredura: python3 não encontrado no PATH." >&2
  echo "RESULTADO: ERRO DE USO" >&2
  echo "→ instale o Python 3.9 ou mais novo e rode de novo; nada foi lido." >&2
  exit 64
fi
exec python3 -B - "$@" <<'PY'
…
PY
```

(O trecho que acha a pasta do script copia o de `eval-revisores.sh` à letra, inclusive o caminho com `\` do Windows: LM-017.)

### Pattern 3: Dispensa na linha

```js
// sdd-seguranca: aceito S16 — avalia só a expressão fixa da planilha de teste, nunca texto do usuário
const f = new Function("return 1 + 1");
```

### Pattern 4: Troca do marcador no `init`

```bash
gerar_corpo_agents() {
  local regras motivo=""
  regras="$(mktemp)"
  if ! bash "${PKG}/sdd/bin/seguranca-varredura.sh" --agents --raiz "${ROOT}" \
        --catalogo "${PKG}/.agents/skills/sdd-seguranca/references/CATALOGO_SEGURANCA.md" > "${regras}" 2>/dev/null; then
    motivo="…"; printf '%s\n' "- Antes de construir, leia as regras de segurança da stack: …(ponteiro)…" > "${regras}"
    warn "AGENTS.md: regras de segurança da stack fora (${motivo}) — o ponteiro para a sdd-seguranca ficou"
  fi
  sed -e "s|{{VENDORS}}|…|g" -e '/^{{SEGURANCA}}$/{' -e "r ${regras}" -e 'd' -e '}' "${PKG}/AGENTS.md.tmpl" > "${CORPO_AGENTS}"
  rm -f "${regras}"
}
```

### Pattern 5: Linha do DEFINE

```markdown
| **Segurança** | 2 aplicados (S01, S07) · 1 recusado (S13) · 0 adiados | sessão do Define, 2026-11-11 |
```

---

## Data Flow

```text
1. Brainstorm: 3 perguntas → ## Perfil de risco (3 linhas)
2. Define, passo 12: gatilho? ─ não → | Segurança | N.A. — … |
                               └ sim → fichas com at: (stack + gatilho), ≤5 por vez → aplicar/recusar/adiar
                                       → AT novo + Verify Gate · ### Segurança em Clarifications · linha final
3. Design: ## Segurança (5 itens; "evitar" dos aplicados) · design-lint avisa se faltar
4. Build: --regras antes da 1ª tarefa · BUILD_REPORT ## Segurança (recusados e adiados)
5. Release 0a item 10: varredura --saida evidence/{F}/SEGURANCA.log → 0 | 1 CONCERNS | 2 NON_WAIVABLE | 64 abortar
   Release 0c: --checklist contra o diff (5 primeiro) · fecho: app publicado + incidente
6. init/sync: --agents → {{SEGURANCA}} no bloco do AGENTS.md
```

---

## Integration Points

| External System | Integration Type | Authentication |
|---|---|---|
| git | leitura (`ls-files`, `diff`, `rev-parse`) | — |
| `sdd/config.yaml` | leitura (slots `security.*`, `project.default_branch`, `layers.sql`) | — |

---

## Testing Strategy

| Tipo | Escopo | Ferramenta | Meta |
|---|---|---|---|
| Unidade/integração | varredura em repositórios git temporários: S11 (6 formatos + 3 leituras por nome que não acusam), S01 (com e sem RLS, nome com `public.` e aspas, RLS em outra migração, sem Supabase), 7 avisos com par negativo, "já existia", base ausente, teto com 8 avisos, `--saida`, dispensa válida e inválida, `--stack` (4 detecções + slot + `nenhuma` + inválido), catálogo ilegível (64), fora de git (64), valor do segredo nunca na saída | `unittest` + `tests/apoio.py` | AT-001 a AT-006 |
| Contrato | catálogo: 22 itens, 13 campos em ordem, domínios, `bloqueia: sim` só S01 e S11, cada `re:` com caso positivo e negativo listado no teste; nenhum arquivo do pacote cita o material de origem (termos montados em tempo de execução) | `unittest` | AT-008 |
| Integração | `init` com e sem Supabase, sem stack, catálogo ausente (⚠️ e ponteiro), `sync --check` divergente ao mudar a stack, acréscimo ≤ 2 KB | `unittest` (`tests/test_sdd_open.py`) | AT-007 |
| Texto | as 5 skills e a nova (passos, linhas, versões), `test_agnostico.py`, `skill-lint.py --conversa`, `design-lint` com o aviso | `unittest` | AT-009 |
| Regressão | suíte inteira, bash 3.2 do macOS, contagens | Verify Gate em `git archive` | AT-010 |
| Sabotagem | 5 mutantes (bloqueio vira aviso; stack ignorada; dispensa sem motivo aceita; teto ignorado; regra de Supabase sem Supabase no `AGENTS.md`) em cópia de `git archive` | script na pasta temporária | cada um derruba um teste nomeado |
| Comportamento | `sdd-seguranca` modo Define: 2 cenários × 3 execuções em contexto novo, critério escrito antes | subagente | 6 de 6 aprovadas |

---

## Error Handling

| Error Type | Handling Strategy | Retry? |
|---|---|---|
| Python ausente | guarda com mensagem própria, exit 64 | Não |
| Catálogo ausente ou fora da gramática | `🛑 catálogo ilegível: <arquivo>:<linha> — <motivo>`, exit 64 (o release aborta com a frase de atualizar) | Não |
| Fora de repositório git sem `--raiz` | exit 64 com a causa | Não |
| Base inexistente | ⚠️ e tudo conta como novo (Decision 3) | Não |
| Arquivo binário ou > 1 MB | pulado e contado | Não |
| Slot inválido (`security.stack` desconhecido, `max_warnings` não inteiro) | stack: exit 64 com o valor; teto: ⚠️ e 5 | Não |
| `--agents` falha no `init` | só o ponteiro + ⚠️ com o motivo | Não |

---

## Configuration

| Config Key | Type | Default | Description |
|---|---|---|---|
| `security.stack` | string | `""` | vazio = detectar; lista de `supabase`, `vercel`, `web`, ou `nenhuma` |
| `security.max_warnings` | int | `5` | avisos na tela por varredura; o resto vai para o arquivo de `--saida` |

---

## Segurança

- **Segredos:** a varredura nunca imprime o trecho do segredo, só id, arquivo e linha; os testes montam as chaves falsas em tempo de execução.
- **Rede:** nenhuma; só `git` local.
- **Arquivo não confiável:** a varredura lê texto do repositório do aluno como dado; nunca executa nada dele (sem `eval`, sem import).
- **Material de origem:** o catálogo tem texto próprio e referência pública; o teste do catálogo reprova citação.
- **Itens aplicados no Define:** N.A. para esta frente (o pacote não é app com login nem banco).

---

## Observability

A varredura imprime a stack e a origem, a base usada, quantos arquivos varreu e quantos pulou; `--saida` guarda a lista inteira como evidência da publicação.

---

## Advisor Ledger

| # | Nota | Severidade | Veredito | Evidência |
|---|---|---|---|---|
| R1 | S11 `sk-` casava identificador kebab e travava a publicação | MED | APLICADA | Decision 5; `test_r1_identificador_kebab_com_sk_nao_e_segredo` |
| R2 | ordem dos avisos contrariava o AT-004 | MED | APLICADA | Decision 6; `test_r2_o_mais_grave_vem_antes_mesmo_que_ja_existisse` |
| R3 | S01 não avisava tabela antiga | MED | APLICADA | Decisions 3 e 5 (o script já avaliava; texto corrigido) |
| R4 | motivo da dispensa podia levar o segredo para a saída | MED | APLICADA | Decision 7; `test_r4_motivo_da_dispensa_nunca_leva_o_segredo` |
| R5 | motivo vazio não era reconhecido | MED | APLICADA | Decision 7 (texto; o script já acusava) |
| R6 | AT-003 tirava o S03 das migrações | MED | APLICADA | DEFINE v1.2, AT-003 |
| R7 | contradição sobre `--raiz` fora de git | MED | APLICADA | linha da LM-006 em Landmines |
| R8 | diff sensível a `diff.noprefix` e nome com acento | MED | APLICADA | Decision 3; `test_r8_nome_com_acento_e_diff_sem_prefixo` |
| R9 | caixa das palavras-chave do S01 | MED | APLICADA | Decision 5; `test_r9_palavras_chave_em_maiusculas` |
| R10 | `revoke … from public` não fecha a função no Supabase | LOW | APLICADA | DEFINE v1.2, AT-003; `test_r10_revoke_so_de_public_nao_basta` |
| R11 | Goal com "20 itens fixos" | LOW | APLICADA | DEFINE v1.2, Goals |
| R12 | Goal com "tabela rígida" | LOW | APLICADA | DEFINE v1.2, Goals |

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | 2026-11-11 | design-agent | Initial version |
| 1.3 | 2026-11-11 | build | Avaliador, ciclo 1: a chave (S11) é procurada em todos os caminhos, menos `node_modules/` e o catálogo (A1; a exclusão de pastas da Decision 4 fica só para os padrões de código); o cabeçalho PEM só conta com o corpo da chave (40+ base64 na mesma linha ou na seguinte), porque documentação mostra o cabeçalho; S14 aceita o `]` de `headers['…'] = '*'` (A2); S12 casa `innerHTML +=` (A3) |
| 1.2 | 2026-11-11 | build | Desvios do build: `sdd-build` sobe para 2.9.0 (já estava em 2.8.0); o detalhe da segurança na `sdd-release` vai para `references/seguranca.md` (linha 34), porque o teste da conversa limita a skill a 500 linhas |
| 1.1 | 2026-11-11 | design-agent | Revisão do DESIGN, rodada 1 (12 achados, todos aplicados): S11 `sk-` exige 32+ caracteres com dígito (R1); ordem dos avisos pela gravidade primeiro (R2); S01 avalia toda `create table`, nova bloqueia e antiga avisa, sem diferença de caixa (R3, R9); motivo da dispensa cortado no fim do comentário e sem segredo, motivo vazio reconhecido e acusado (R4, R5); prefixos do diff fixados (R8); S03 exige `revoke … from anon` (R10); os modos de leitura funcionam fora de git (R7) |

---

## Next Step

**Ready for:** `/sdd-build sdd/features/DESIGN_F18_F20_SEGURANCA.md`
