# DEFINE: F5 Conhecimento do sdd-open

> A `sdd-kb` do sdd-starter entra como 17ª skill do open, gravando em `sdd/kb/`, com o validador, um `gate.sh` que roda igual no pacote e no projeto do aluno e um `--strict` que liga cada regra implementada a um teste que existe. O campo "KB Domains" do DEFINE vira lista fechada, conferida por `sdd/bin/kb-dominios.py`. A `sdd-ux-review` ganha a entrevista de público e referências como entrada opcional.

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | F5_CONHECIMENTO |
| **Date** | 2026-10-29 |
| **Author** | SDD Define by RDD (sessão com Roberto Dias Duarte) |
| **Status** | Ready for Design |
| **Clarity Score** | 14/15 |

---

## Problem Statement

O sdd-open não tem como ensinar à IA o contexto de um projeto (leis, normas, processos, manuais). Isso aparece em quatro pontos:
- **Não há skill de base de conhecimento.** O aluno reexplica o mesmo contexto em toda conversa, e uma regra que vale por período fica errada sem aviso.
- **O "KB Domains" aceita qualquer texto** (`sdd/templates/DEFINE_TEMPLATE.md:158`: "nomes de pasta em `sdd/kb/` ou equivalente"). Nenhuma skill confere o campo, então o agente pode citar um domínio que não existe, e o Design vai procurar padrões onde não há nada.
- **No sdd-starter, a coluna `Teste` do RULE_MAP é texto livre.** Uma regra "implementada" pode apontar para um teste que não existe.
- **A `sdd-ux-review` parte do que o DEFINE diz sobre o usuário.** Quando o DEFINE não diz quem usa nem em que contexto, ela não tem um roteiro para perguntar.

---

## Target Users

| User | Role | Pain Point |
|---|---|---|
| Aluno que usa o open (contador, advogado, gestor), em geral sem git nem terminal | Ensina o domínio à IA e roda as skills de fase | Reexplica o contexto em toda conversa; não percebe quando uma regra venceu |
| Agente que roda `sdd-define`, `sdd-design` e `sdd-ux-review` | Preenche "KB Domains", escolhe testes para o gate e conduz a revisão de UX | Inventa nome de domínio; não sabe qual teste cobre qual regra; não sabe o que perguntar sobre o público |
| Roberto, mantenedor | Publica o pacote | Precisa provar, dos dois lados (LM-001), que o validador discrimina no pacote e na cópia que o `init` leva ao aluno |

---

## Goals

| Priority | Goal |
|---|---|
| **MUST** | **`.agents/skills/sdd-kb/`** (nova, `metadata.version` 2.2.0, `updated: "2026-10"`), portada de `sdd-starter/skills/sdd-kb` 2.1.0 (`17c69c4`):<br>• `SKILL.md`, `CHANGELOG.md` (entrada 2.2.0) e os 4 `references/`;<br>• os 10 moldes e os exemplos `example-kb` e `example-kb-normativo` de `assets/`;<br>• `scripts/validate_kb.py`, `scripts/kb_normativo.py` e `scripts/gate.sh`.<br>**Ficam de fora** `agents/openai.yaml`, `tests/` dentro da skill e qualquer menção a `sdd-starter`. A pasta da KB é fixa: `sdd/kb/_index.yaml` e `sdd/kb/<slug>/`. Os comandos que o texto manda rodar usam os caminhos do projeto: `python3 .agents/skills/sdd-kb/scripts/validate_kb.py sdd/kb/<slug>` e `python3 .agents/skills/sdd-kb/scripts/kb_normativo.py rule-map sdd/kb/<slug>` |
| **MUST** | A `sdd-kb` segue a camada da F4:<br>• a linha de identificação `sdd-kb v2.2.0 · out/2026 · versão atual: https://github.com/robertodiasduarte/sdd-open/releases/latest`, "uma vez só, antes do Status";<br>• a seção `## Como falar com o aluno`, com a tabela de 5 etapas (Domínio, Entender × fazer, Escrever, Fonte e índice, Revisão do profissional) e o **bloco comum de regras** igual ao das 14 skills (as 7 `FRASES` de `tests/test_conversa.py`);<br>• `references/como-falar.md` citando `sdd/templates/fragments/PERGUNTA_DECISAO.md`, com ≥1 pergunta que tem `(recomendado)` na 1ª opção, **não sei** e nenhuma **Outro** |
| **MUST** | `validate_kb.py` mantém o que já faz e as saídas do starter (0 PASS · 2 FAIL · 64 uso). No `--strict`, ganha duas reprovações:<br>• a regra de `rules/*.md` com `implementacao` preenchida e `teste` vazio ou `null`;<br>• a regra com `teste` cujo arquivo não existe.<br>O arquivo é a parte de `teste` antes do 1º `:`, resolvida a partir da **raiz do projeto**: a pasta que contém `sdd/kb/` quando o domínio está em `<raiz>/sdd/kb/<slug>`, ou o diretório corrente nos outros casos. Sem `--strict`, nada disso é conferido, porque a base pode ser escrita antes do software |
| **MUST** | `scripts/gate.sh` autossuficiente (bash 3.2). Ele acha o validador, o `kb_normativo.py` e os exemplos pela própria pasta, e monta tudo numa pasta temporária, apagada no fim com `"${T:?}"`. O gate:<br>• **aceita** os 2 exemplos (o normativo como perfil normativo), a fixtura boa "código com chaves" (`kb_good_codigo` do starter) e o exemplo normativo revisado com `implementacao` e `teste` de arquivo que existe, no `--strict`;<br>• **confere** que o RULE_MAP do exemplo não derivou (`rule-map --check`);<br>• **rejeita** as 6 ruins do starter (`limite_concept`, `limite_pattern`, `limite_quick`, `naoregistrado`, `placeholder`, `placeholder_codigo`), 4 normativas (regra sem vigência, fonte fora do catálogo, SHA-256 divergente, `PENDENTE DE REVISÃO` no `--strict`) e as 2 do `--strict` novo (teste vazio com implementação; teste de arquivo inexistente).<br>PASS sai 0, com as contagens. Fixtura boa rejeitada, ruim aceita ou RULE_MAP derivado sai 2, com o nome da fixtura. Roda igual no pacote e numa cópia que só tem a pasta da skill |
| **MUST** | **`sdd/bin/kb-dominios.py <DEFINE.md>`** (novo; 0 · 1 · 64; Python stdlib; não importa nada da `sdd-kb`). Ele lê a linha `**KB Domains**` do `## Technical Context` e compara com as pastas de `sdd/kb/` da raiz do projeto (as entradas que são pasta, sem as ocultas).<br>**Sai 0** quando o valor é `nenhum` sozinho ou quando cada nome, separado por vírgula e sem crases, existe como pasta.<br>**Sai 1**, com 1 linha por problema e `RESULTADO: VERMELHO`, quando:<br>• falta a linha;<br>• o valor está vazio, é placeholder entre chaves ou `N/A`;<br>• `nenhum` vem junto com um nome;<br>• um nome não tem pasta;<br>• há nome citado e `sdd/kb/` não existe ("rode a sdd-kb ou escreva nenhum").<br>**Sai 64** em uso errado ou arquivo ausente. Arquivo ilegível sai 1, sem traceback.<br>Para cada domínio citado que tem `RULE_MAP.md`, imprime `<domínio>: <REGRA> → <teste>` para as linhas com teste preenchido |
| **MUST** | **`sdd-define`** (2.2.0 → 2.3.0):<br>• os passos 1–9 ficam como estão, e entra `### 10. Conferir o KB Domains`, que roda `python3 sdd/bin/kb-dominios.py sdd/features/DEFINE_{FEATURE}.md` (vermelho ⇒ corrigir e rodar de novo);<br>• os testes listados pelo lint entram no `cmd` do Verify Gate, ou o DEFINE registra por que não;<br>• a skill diz que o valor de "KB Domains" sai de `ls sdd/kb/` ou é `nenhum`, revalidado a cada Define.<br>No `sdd/templates/DEFINE_TEMPLATE.md`, a linha passa a dizer "nomes de pasta em `sdd/kb/` (`ls sdd/kb/`), ou `nenhum` explícito", sem "ou equivalente" |
| **MUST** | **`sdd-ux-review`** (2.2.0 → 2.3.0): os passos 1–8 ficam, e o passo 1 ganha 1 frase. Se o DEFINE não diz quem usa e em que contexto, ou se o aluno pedir, a skill conduz a entrevista de `references/entrevista-publico.md` (nova), uma pergunta por resposta, e grava o resultado em `## User and Context` do UX_REVIEW. O `references/entrevista-publico.md` traz, do `ux-review-builder` 1.4.0:<br>• as perguntas de público (com frequência de uso, familiaridade, volume, risco de erro e dispositivo), de estágio e de referência;<br>• o catálogo de referências;<br>• a URL opcional, com o protocolo de observação, os limites e "análise direta não disponível" quando a URL não abre;<br>• as 3 camadas Observado × Desejado × Recomendado.<br>Toda pergunta de decisão do arquivo segue o `PERGUNTA_DECISAO.md`: a recomendada primeiro, **não sei** e nenhuma **Outro**. O `sdd/templates/UX_REVIEW_TEMPLATE.md` não muda |
| **MUST** | Testes do pacote:<br>• `tests/test_sdd_kb_normativo.py` (os 62 do starter, com os caminhos `.agents/skills/sdd-kb/`);<br>• `tests/test_sdd_kb.py` (o `gate.sh` no pacote e numa cópia só da skill, o `--strict` novo dos dois lados e as saídas 0/2/64);<br>• `tests/test_kb_dominios.py` (cada caso do Goal do lint e o texto do passo 10).<br>Atualizações de propósito:<br>• `test_skill_lint.py` e `test_conversa.py` passam de 16 para 17 skills;<br>• `test_conversa.F4` ganha `sdd-kb`;<br>• `test_matriz_new_session.PORTADAS` ganha `sdd-kb`.<br>Todo arquivo novo entra no `MANIFEST.txt`, em ordem `LC_ALL=C` |
| **MUST** | Nenhuma regressão:<br>• os 388 testes;<br>• `sdd/bin/verify-gate.sh`, `report-lint.py`, `skill-lint.py`, `design-lint.py`, `handoff-lint.py`, `playbook-lint.sh`, `scripts/publish-gate.sh`, `scripts/check-versions.py` e os arquivos existentes de `sdd/fixtures/` idênticos byte a byte à `v2.2.5`;<br>• o bloco do OK da `sdd-release` e o passo 4 da `sdd-iterate` intactos;<br>• o bloco comum da camada sem mudança nas 14 skills |
| **MUST** | Exatamente 1 sabotagem por script novo ou alterado (`validate_kb.py`, `kb_normativo.py`, `gate.sh`, `kb-dominios.py`) |
| **SHOULD** | O `DESIGN_F5_CONHECIMENTO.md` anota que o `UX_REVIEW_TEMPLATE.md` vai ganhar a tabela WCAG 2.2 AA na W5 (item H), e a F5 não fixa nada que a contradiga |
| **SHOULD** | `docs/cli-conventions.md` ganha as saídas do `kb-dominios.py` e do `validate_kb.py` |

---

## Success Criteria

- [ ] `python3 sdd/bin/skill-lint.py --conversa .agents/skills/sdd-*/SKILL.md` sai 0 nas **17** skills.
- [ ] `bash .agents/skills/sdd-kb/scripts/gate.sh` sai 0 no pacote e numa cópia que só tem `.agents/skills/sdd-kb/`, com 4 aceitas e 12 rejeitadas.
- [ ] Os 62 testes normativos portados passam.
- [ ] `kb-dominios.py`:
  - sai 0 em 2 casos (`nenhum`; nomes que existem);
  - sai 1 em 7 casos (linha ausente, vazio, placeholder, `N/A`, `nenhum` com nome, nome sem pasta, `sdd/kb/` ausente);
  - sai 64 em 2 casos (sem argumento, arquivo ausente).
- [ ] `validate_kb.py --strict` sai 2 nos 2 casos novos e 0 com o arquivo de teste presente. Sem `--strict`, os 2 casos saem 0.
- [ ] A suíte sai 0 no piso `SDD_TEST_BASH=/bin/bash /usr/bin/python3` (Python 3.9.6 + bash 3.2.57), com mais de 388 testes e 0 falha.
- [ ] Baseline vermelha: os 3 módulos novos de teste falham na árvore `v2.2.5`.
- [ ] 4 de 4 sabotagens ficam vermelhas com o nome do teste e voltam ao verde com `git checkout`.
- [ ] `python3 scripts/check-versions.py --base v2.2.5 --base-obrigatoria` sai 0, com `sdd-define` 2.3.0, `sdd-ux-review` 2.3.0 e `sdd-kb` 2.2.0.
- [ ] Na `sdd-define` e na `sdd-ux-review`, o log de comandos intactos (`v2.2.5` × HEAD) mostra só as 2 exceções declaradas: o passo 10 e a frase do passo 1.
- [ ] `wc -l` ≤ 500 nas 17 `SKILL.md`.
- [ ] O CI do PR sai verde em `ubuntu-latest` (`gate`) e `macos-latest` (`testes-macos`), com 0 achado de integridade.
- [ ] Depois do push em `main`, a run do `release` mostra `testes` e `testes-macos` concluídos, `gh release view <tag> -R robertodiasduarte/sdd-open` lista `SHA256SUMS.txt`, e `shasum -a 256 -c` sai 0.

---

## Acceptance Tests

| ID | Pattern | Criterion (EARS) | Gate (`kind`) |
|---|---|---|---|
| AT-001 | Event-driven | **When** `skill-lint.py --conversa` runs on the 17 `.agents/skills/sdd-*/SKILL.md`, the system **shall** exit 0, and `tests/test_conversa.py` **shall** find in `sdd-kb` the section, the 7 common-block phrases, the identification line equal to `metadata.version` and a `como-falar.md` citing `PERGUNTA_DECISAO.md` | test |
| AT-002 | Event-driven | **When** `bash .agents/skills/sdd-kb/scripts/gate.sh` runs in the package or in a directory holding only a copy of `.agents/skills/sdd-kb/`, the system **shall** exit 0 and end with `RESULTADO: VERDE` and the counts (4 accepted, 12 rejected), printing no per-case line | test |
| AT-003 | Unwanted | **If** the validator accepts a bad case, rejects a good case or rejects a bad case for another reason, a mutation anchor is missing, or the example RULE_MAP has drifted, **then** `gate.sh` **shall** exit 2 with a `🛑` line naming the case, `RESULTADO: VERMELHO` and a `→` line with the fix | test |
| AT-004 | Event-driven | **When** the 62 ported normative tests run against `.agents/skills/sdd-kb/`, each **shall** pass, asserting the exit code and the printed reason | test |
| AT-005 | Unwanted | **If** `validate_kb.py --strict` reads a rule with `implementacao` filled and `teste` empty or `null`, or with a `teste` whose file (the part before the first `:`) does not exist under the project root or lies outside it (absolute path, `../`), **then** it **shall** exit 2 naming the rule; **when** the file exists, it **shall** exit 0 | test |
| AT-006 | Non-regression | `validate_kb.py` without `--strict` **shall continue to** pass both example KBs and **shall** not check `teste`, and its exit codes **shall continue to** be 0/2/64 | test |
| AT-007 | Event-driven | **When** `kb-dominios.py` reads a DEFINE whose `**KB Domains**` is `nenhum`, or lists only names that exist as folders in `sdd/kb/`, the system **shall** exit 0, and for each listed domain with a `RULE_MAP.md` it **shall** print `<domínio>: <REGRA> → <teste>` for the rows with a test | test |
| AT-008 | Unwanted | **If** the `**KB Domains**` row is missing from `## Technical Context` (a row in another section does not count), empty, a placeholder in braces or `N/A`, mixes `nenhum` with a name, cites a name without a folder, or cites a name while `sdd/kb/` does not exist, **then** `kb-dominios.py` **shall** exit 1 with one `🛑` line per problem (an unknown name lists the existing folders, up to 10 and "e mais N"), `RESULTADO: VERMELHO` and a `→` line with the fix | test |
| AT-009 | Unwanted | **If** `kb-dominios.py` is called without an argument or with a missing file, **then** it **shall** exit 64; **if** the file exists and cannot be read, **then** it **shall** exit 1, never a traceback | test |
| AT-010 | Event-driven | **When** the `sdd-define` skill and `DEFINE_TEMPLATE.md` are read, the system **shall** find `### 10. Conferir o KB Domains` with the call `python3 sdd/bin/kb-dominios.py`, the rule that the value comes from `ls sdd/kb/` or is `nenhum`, and no "ou equivalente" in the template line | test |
| AT-011 | Event-driven | **When** the `sdd-ux-review` skill is read, step 1 **shall** point to `references/entrevista-publico.md` as optional input recorded in `## User and Context`; that file **shall** cover público, estágio, catálogo de referências, URL with "análise direta não disponível" and Observado × Desejado × Recomendado, fact questions (público, estágio, referência) **shall** be at least 3 open questions with a "não sei" way out, and the `perguntas()` function of `skill-lint.py` **shall** find exactly one decision question in it, `**Posso gravar este público em User and Context?**`, with `(recomendado)` first, **não sei** and no **Outro** | test |
| AT-012 | Unwanted | **If** `.agents/skills/sdd-kb/` contains `agents/openai.yaml`, a `tests/` folder, the text `sdd-starter`, a KB folder other than `sdd/kb/` (`pasta de bases`, `.claude/kb`, `kb_dir`), a `scripts/validate_kb.py` or `scripts/kb_normativo.py` mention without the `.agents/skills/sdd-kb/` prefix, or a relative `](assets/` / `](scripts/` link (the `CHANGELOG.md` history below 2.2.0 excepted), **then** `tests/test_matriz_new_session.py::Portadas` or `tests/test_sdd_kb.py` **shall** fail naming the file | test |
| AT-013 | Non-regression | The system **shall continue to** pass the 388 existing tests (with the deliberate 16 → 17 updates), keep `verify-gate.sh`, `report-lint.py`, `skill-lint.py`, `design-lint.py`, `handoff-lint.py`, `playbook-lint.sh`, `scripts/publish-gate.sh`, `scripts/check-versions.py` and the existing `sdd/fixtures/` files byte-identical to `v2.2.5`, and pass `publish-gate.sh` in `ci` mode with `test_agnostico.py` green | test |
| AT-014 | Non-regression | `sdd-define` and `sdd-ux-review` **shall continue to** have the same step headings and command lines as in `v2.2.5`, except step 10 and the sentence in step 1, evidenced in `evidence/F5_CONHECIMENTO/comandos-intactos.log` | test |
| AT-015 | Event-driven | **When** `check-versions.py --base v2.2.5 --base-obrigatoria` runs on the F5 tree, the system **shall** exit 0, evidenced in `evidence/F5_CONHECIMENTO/check-versions.log` | test |
| AT-017 | Unwanted | **If** `gate.sh` runs from an adapter copy generated by `init --vendors claude` (`.claude/skills/sdd-kb/scripts/`), **then** it **shall** exit 2 with a `🛑` line naming the generated copy and a `→` line pointing to `bash .agents/skills/sdd-kb/scripts/gate.sh`; **when** run from `.agents/skills/sdd-kb/scripts/` in the same project, it **shall** exit 0 | test |
| AT-016 | Unwanted | **If** a contract is broken on purpose in `validate_kb.py`, `kb_normativo.py`, `gate.sh` or `kb-dominios.py`, **then** at least one named test **shall** fail, and reverting it with `git checkout` **shall** turn the suite green again | test |

---

## Clarifications

### Session 2026-10-29

- [x] (Scope) Decisão 4 do plano → `sdd/kb/` fixo, sem slot (BRAINSTORM, decisão 1). Integrado em Goals e AT-007/AT-010.
- [x] (Data model) O formato de `teste` vem do `RULE_TEMPLATE.md` (um escalar, como `tests/test_engine.py::test_vbc`). → O arquivo é a parte antes do 1º `:`. A raiz é a pasta que contém `sdd/kb/`, porque o RULE_MAP é do projeto e não da pasta do domínio. Fora de `sdd/kb/`, vale o diretório corrente. Integrado em AT-005.
- [x] (Data model) "Pasta em `sdd/kb/`" = entrada que é diretório e não começa por `.`. `_index.yaml` é arquivo e não conta. O `kb-dominios.py` não exige que o domínio esteja registrado no `_index.yaml`: o registro é conferido pelo `validate_kb.py`. Integrado em AT-007/AT-008.
- [x] (Edge cases) `N/A`, que o DEFINE_F4 e os anteriores usavam, passa a reprovar: o item G pede `nenhum` explícito. Os DEFINE antigos não são relidos pelo lint, que só roda no passo 10 da define. Integrado em AT-008.
- [x] (Edge cases) A raiz do projeto do `kb-dominios.py` é a pasta 2 níveis acima do DEFINE quando ele está em `<raiz>/sdd/features/`; nos outros casos, o diretório corrente. → Detalhe de Design; o AT-007 é testado com a árvore `<tmp>/sdd/features` + `<tmp>/sdd/kb`.
- [x] (Constraints) O `cmd` do gate não pode ter aspas duplas internas e roda da raiz com `bash -c`. A cópia por `git archive` não tem `.git` nem `sdd/features/`. → AT-014 e AT-015 são `test` com log em `evidence/F5_CONHECIMENTO/`, fora do `cmd`, como na F4. Integrado em Verify Gate.
- [x] (UX flow) A feature tem interface: o texto que o aluno lê na `sdd-kb` e a entrevista da `sdd-ux-review`. → Status `Ready for UX Review`. A obediência de um agente real à entrevista não é executável em teste (A-002).
- [x] (Integrations) Os 62 testes do starter chamam o validador por caminho. → Só o caminho muda: `skills/sdd-kb` vira `.agents/skills/sdd-kb`. Integrado em AT-004.

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

O gate só enxerga o que está commitado (`git archive HEAD`), então o Build commita na branch antes de rodar. `PUBLISH_GATE_MODE=ci` é necessário porque o modo padrão exige a camada privada de padrões. A suíte roda no piso (Python 3.9 do macOS, bash 3.2) e cobre AT-001 a AT-013, AT-016 e AT-017. O `gate.sh` é chamado de dentro do `tests/test_sdd_kb.py`.

Ficam fora do `cmd`, com log em `evidence/F5_CONHECIMENTO/`, porque precisam de `.git`: AT-014, AT-015, a baseline vermelha e a Release (último Success Criterion).

---

## Out of Scope

- A tabela WCAG 2.2 AA e a leitura de `UX_REVIEW_*.md` anteriores (item H, W5/F13). O `UX_REVIEW_TEMPLATE.md` não muda.
- Do `ux-review-builder`, ficam de fora:
  - o `UX_STANDARD.md`, a skill `ux-review` gerada, o template dele e o `validate_generated_bundle.py`;
  - `GOVERNANCE.md`, `GENERATION_CONTRACT.md`, `UNIVERSAL_PRINCIPLES.md`, `RUNTIME_COMPATIBILITY.md` e `COMO_FUNCIONA.md`;
  - `evals/` e `manifest.json`.
- O slot `project.kb_dir`; o `init` criar `sdd/kb/`; a migração de KBs em `.claude/kb/`.
- Ficam sem verificação:
  - o caminho do teste dentro do `cmd` do Verify Gate;
  - a relevância do domínio citado para a feature;
  - rodar os testes do RULE_MAP no `--strict`;
  - o `doctor` validar a KB.
- O encadeamento e as classes D1–D5 (F9); o fail-open do `report-lint` (F7); docs, guia do aluno e roadmap (F6).
- Mudanças em `sdd-design`, `sdd-brainstorm` e nas outras 12 skills.
- Alterar o sdd-starter ou o repositório privado.

---

## Constraints

| Type | Constraint | Impact |
|---|---|---|
| Technical | bash 3.2, sem `declare -A`, `mapfile`, `readlink -f`, `grep -P` nem `${x^^}`; Python ≥ 3.9 só com stdlib, rodado com `python3 -B`; nenhum `rm -rf` com variável sem `"${X:?}"` | `gate.sh`, `kb-dominios.py` e os testes rodam no macOS de fábrica e no CI macOS, que afirma o piso |
| Technical | Integridade do CI em `.agents/skills/`: nenhum Unicode invisível e nenhum `curl … \| sh` literal. Em teste, a amostra com Unicode invisível se monta com `chr()` | Conferir os code points depois de escrever o texto portado |
| Technical | G2 do publish-gate: nenhum literal casa com `scripts/publish-gate-patterns.txt` | Exemplos e mutações sem CPF/CNPJ/telefone/e-mail real, sem 11+ dígitos e sem caminho `/Users/`; números de lei e código de rejeição curtos passam |
| Technical | G3: o `MANIFEST.txt` é allowlist nos dois sentidos, em ordem `LC_ALL=C` | Os ~35 arquivos novos da skill e os 3 testes entram no mesmo commit; `sdd/features|handoffs|reports|reviews/` ficam fora |
| Technical | `tests/test_agnostico.py` | Nenhum nome de ferramenta de um agente só no texto portado; a análise de URL fala em "quando o agente consegue abrir páginas", sem citar ferramenta |
| Technical | A camada da F4 é contrato: o bloco comum das 14 skills não muda; a linha de identificação vem "uma vez só, antes do Status", com a versão do frontmatter | A `sdd-kb` copia o bloco comum sem alterar uma frase |
| Technical | Toda skill tocada sobe de versão | `sdd-define` 2.3.0 e `sdd-ux-review` 2.3.0; a `sdd-kb` nasce em 2.2.0 |
| Technical | `SKILL.md` ≤ 500 linhas | A `sdd-kb` (325 linhas no starter) ganha a camada e perde a seção antiga dela |
| Technical | Decisões que não se reabrem: camada sempre ligada; Status `✅ ▶️ ⬜ ⏸️ ➖` com o nome da fase; pergunta com a recomendada primeiro, **não sei** e sem **Outro**; o open como fonte canônica; artefatos SDD na branch `docs/` | — |
| Other | Push em `main` só com o OK do Roberto citando "sdd-open" na mesma mensagem, depois de PR com CI verde; a versão (`v2.2.6` automática × `v2.3.0` por tag à mão) é perguntada nesse OK | A Release depende desse OK |

---

## Technical Context

| Aspect | Value | Notes |
|---|---|---|
| **Deployment Location** | `.agents/skills/sdd-kb/**` (nova); `.agents/skills/sdd-define/SKILL.md`; `.agents/skills/sdd-ux-review/SKILL.md` + `references/entrevista-publico.md`; `sdd/bin/kb-dominios.py`; `sdd/templates/DEFINE_TEMPLATE.md`; `tests/test_sdd_kb.py`, `test_sdd_kb_normativo.py`, `test_kb_dominios.py`, `test_skill_lint.py`, `test_conversa.py`, `test_matriz_new_session.py`; `docs/cli-conventions.md`; `MANIFEST.txt` | Fonte: `/Users/robertoduarte/rdd-public/sdd-starter`, em `17c69c4` |
| **KB Domains** | nenhum | O open não tem `sdd/kb/`; a F5 cria o mecanismo, não uma KB do próprio pacote |
| **IaC Impact** | None | O push em `main` publica a Release sozinho, porque toca `.agents/skills/**`, `sdd/bin/**` e `sdd/templates/**` |
| **LLM Prompts** | false | `SKILL.md` e `references/` são instruções de orquestração lidas pelo agente de desenvolvimento; nenhum prompt de runtime de produto |

---

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|---|---|---|---|
| A-001 | Os 388 testes passam no piso em `2fcdda1`, antes da F5 | O Build partiria de base vermelha | yes (handoff da F4: 388 OK no piso e no CI); reconferir no início do Build |
| A-002 | O agente conduz a entrevista de público uma pergunta por vez e lê o `references/` quando a skill manda | O UX review sai sem público; os passos 2–8 continuam valendo | no; não é executável em teste, e a conferência num agente real fica como pendência, como a A-002 da F4 |
| A-003 | O conteúdo dos exemplos do starter não tem literal que o publish-gate reprove | O G2 reprovaria o pacote | yes; varredura de `[0-9]{11,}`, `@`, `.invalid` e `git@` sem achado (brainstorm). Reconferir com o `publish-gate.sh` no Build |
| A-004 | Os 62 testes do starter dependem só do caminho da skill, não do layout `skills/` | O porte dos testes exigiria reescrita | parcial: o cabeçalho usa `ROOT / "skills" / "sdd-kb"`; conferir o resto no Build |

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---|---:|---|
| Problem | 3 | Quatro sintomas com o local (`DEFINE_TEMPLATE.md:158`, coluna `Teste` livre, skill ausente, entrevista ausente) |
| Users | 3 | Aluno, agente e mantenedor, com a dor de cada um |
| Goals | 3 | Vêm das 6 decisões e dos 2 checkpoints, com versões, saídas e casos enumerados |
| Success | 2 | Todo critério mecânico é observável; a entrevista conduzida num agente real fica para conferência humana |
| Scope | 3 | Arquivos, exceções de comando e o destino do que ficou fora (W5, F6, F7, F9) |
| **Total** | **14/15** | |

Minimum to proceed: **12/15**.

---

## Open Questions

None - ready for Design.

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | 2026-10-29 | SDD Define by RDD | Initial version |
| 1.4 | 2026-10-29 | SDD Build by RDD | Revisão de contexto fresco do build, ciclo 1 (M1, L3): AT-008 lê só o `## Technical Context`; AT-005 reprova `teste` fora da raiz |
| 1.3 | 2026-10-29 | SDD Design by RDD | Revisão de contexto fresco do DESIGN (H1, M1, M3, M4): AT-003 com âncora ausente e razão errada; AT-011 com exatamente 1 pergunta de decisão e ≥3 abertas; AT-012 com os caminhos proibidos; AT-017 novo (gate de uma cópia gerada pelo `init`) |
| 1.2 | 2026-10-29 | SDD Design by RDD | O gate aceita 4 casos: o 4º é o lado verde da checagem nova do `--strict` (exemplo normativo revisado, teste presente); AT-002 e Success Criteria |
| 1.1 | 2026-10-29 | sdd-ux-review | `sdd/reviews/UX_REVIEW_F5_CONHECIMENTO.md`: Status → Ready for Design; AT-002/AT-003/AT-008 com a moldura de `docs/cli-conventions.md` (`🛑`, `RESULTADO:`, `→`; nomes existentes na falha; gate silencioso no sucesso); AT-011: perguntas de fato são abertas, só a confirmação final tem opções |

---

## Next Step

Execute o **SDD Design by RDD**.
