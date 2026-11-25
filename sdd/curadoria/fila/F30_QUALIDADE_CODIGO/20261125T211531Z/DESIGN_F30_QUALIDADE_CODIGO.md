# DESIGN: F30 — Qualidade do código gerado · fatias S1 (itens 1, 3, 4), S2 (itens 2, 6, 7) e S3 (itens 5, 8)

> **S3:** complexidade e duplicação só no que o diff trouxe, numa seção de avisos do BUILD_REPORT que nunca reprova
> (Decisions 15 a 19).
>
> **S2:** vermelho antes do verde conferido pelo `report-lint.py` (coluna `Antes`), sabotagem do gate numa cópia
> descartável (`sabotagem.sh`) e o passo Refatorar entre Verificar e Marcar (Decisions 8 a 14).
>
> **S1:** lint e tipos a cada tarefa do Build com evidência conferida, regras de qualidade por stack no AGENTS.md e no
> texto da build do starter, e sugestão do linter da stack quando o projeto não tem um, sem instalar nada.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | F30_QUALIDADE_CODIGO (fatia S3; a S1 está na v2.26.0 e a S2 na v2.27.3) |
| **Date** | 2026-11-25 (S3) · 2026-11-24 (S2) · 2026-11-23 (S1) |
| **Author** | design-agent |
| **DEFINE** | [DEFINE_F30_QUALIDADE_CODIGO.md](./DEFINE_F30_QUALIDADE_CODIGO.md) |
| **Status** | Ready for Build |

---

## Architecture Overview

S3:

```text
   sdd/config.yaml qualidade.* (10 · 60 · 5 · 50) ─┐
   git diff -U0 (base..árvore) + arquivos novos ───┤
                                                   ▼
   sdd/bin/metricas-diff.sh ── Python 1: limites, arquivos de código do diff, linhas novas ⇒ lista NUL em mktemp
        ├─ bash: `command -v lizard` ─ xargs -0 lizard --csv ────────┐  ausente / exit≠0 / ilegível
        ├─ bash: `command -v jscpd`  ─ jscpd . --reporters json ─────┤  ⇒ "não medido: …"
        └─ Python 2: só função/par com linha no diff ◀───────────────┘
             stdout: `## Qualidade (avisos)` (colada no BUILD_REPORT) · stderr: RESULTADO + → · exit 0 (64 = uso)
   BUILD_REPORT ──▶ report-lint.py check_qualidade(): config com `qualidade:` ⇒ seção obrigatória; sem ele ⇒ aviso
```

S2:

```text
   DESIGN § Testing Strategy ── tabela de sabotagens (AT · arquivo · trocar · por) ── revisada com o DESIGN
        │
   sdd-build, por tarefa: 3 Escrever ─ antes do código: comando do AT ⇒ evidence/{F}/AT-nnn.antes.log (vermelho;
        │                              `shall continue to`: verde)
        ├─ 4 Verificar (teste, lint, tipos) ─ 5 Refatorar (só os arquivos da tarefa; build.refatorar: false pula)
        └─ 6 Marcar
   sdd-build 5a: por linha da tabela ──▶ sdd/bin/sabotagem.sh ──▶ git archive HEAD ⇒ pasta temporária
        cópia limpa verde? ─ troca o trecho (1 vez) ─ comando de novo: vermelho ⇒ 0 + AT-nnn.sabotagem.log
                                                                    verde    ⇒ 2 "o teste não pega o defeito"
        (a árvore de trabalho só recebe o log; a cópia é apagada por trap)
   BUILD_REPORT (coluna Antes) ──▶ report-lint.py: ats_do_define() classifica novo · continua · fora;
        novo ⇒ antes vermelho do mesmo comando; continua ⇒ antes verde; fora ⇒ N.A.; sem a coluna ⇒ aviso
```

S1:

```text
                 .agents/skills/sdd-build/web/references/CATALOGO_QUALIDADE.md   (fonte única: regras Qnn + ferramentas)
                        │ lido só por                                    │ copiado como está (citado pelo MODO_WEB)
                        ▼                                                ▼
   sdd/bin/qualidade-regras.sh  ──--agents──▶ bin/sdd-open.sh init/sync ──▶ AGENTS.md  "### Qualidade ao construir"
     (--stack · --regras · --agents)          ({{QUALIDADE}} de AGENTS.md.tmpl;        (+ ponteiro; falha ⇒ só ponteiro
                        │                       falha ⇒ ponteiro + warn com causa)        e ⚠️ com a causa)
                        └──--regras──▶ sdd-build (Open), passo 3 "Escrever"
                                                                         starter: sdd-build/SKILL.md (do MODO_WEB)
                                                                                  + references/CATALOGO_QUALIDADE.md

   sdd-build passo 4 "Verificar" ── project.lint_cmd / project.typecheck_cmd (cheios) sobre os arquivos da tarefa
        │ erro ⇒ escada de retry                     fim do Build ⇒ evidence/{F}/LINT.log, TIPOS.log
        ▼                                                         ▼
   BUILD_REPORT ───────────────────────────────▶ sdd/bin/report-lint.py  check_lint():
                                                   slot cheio ⇒ log obrigatório (1ª linha `$ <slot>…`, fim `[exit=0]`)
                                                   slots vazios ⇒ `lint: slot vazio` (ausente = aviso, nunca violação)

   checar.sh (modo normal) ── stack sem linter e slots vazios ──▶ ⚠️ Vale arrumar  (comando de instalar + slot)
   checar.sh --linter ──▶ `stack<TAB>lint<TAB>tipos<TAB>instalar` ──▶ sdd-new-session: [D2] gravar o slot? (só com sim)
```

## Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| Catálogo de qualidade | Fonte única das 6 regras gerais, das regras por stack e das ferramentas sugeridas por stack | Markdown com fichas de formato fixo |
| `qualidade-regras.sh` | Único leitor do catálogo: detecta a stack, imprime as regras para o AGENTS.md e para o build | bash 3.2 + Python 3.9 stdlib (molde do `seguranca-varredura.sh`) |
| `sdd-open.sh` (`gerar_corpo_agents`) | Preenche `{{QUALIDADE}}` como já preenche `{{SEGURANCA}}` | bash |
| `report-lint.py` (`check_lint`) | Exige `LINT.log`/`TIPOS.log` com o slot cheio | Python stdlib |
| `checar.sh` (⚠️ e `--linter`) | Sugere o linter da stack, só lendo | bash |
| Textos das skills | Build (Open e web), new-session, checar-ambiente | Markdown |
| `report-lint.py` (S2: `ats_do_define`, coluna `Antes`) | Vermelho antes do verde por AT (Decisions 8, 9) | Python stdlib |
| `sabotagem.sh` (S2) | Sabotagem declarada numa cópia de `git archive HEAD` (Decision 10) | bash 3.2 + Python stdlib |
| `metricas-diff.sh` (S3) | Complexidade e duplicação do diff, só aviso (Decisions 15 a 18) | bash 3.2 + Python stdlib; `lizard` e `jscpd` do PATH, opcionais |
| `report-lint.py` (S3: `check_qualidade`) | A seção de avisos existe (Decision 19) | Python stdlib |
| `disciplina-de-teste.md` (S2) | Texto único das 3 práticas, citado pelo Open e pelo starter (Decision 13) | Markdown |

---

## Key Decisions

### Decision 1: Catálogo em `sdd-build/web/references/`, não em `sdd-build/references/`
| **Status** | Accepted | · | **Date** | 2026-11-23 |

**Context:** D6 pediu arquivo novo na skill da build. O starter monta a `sdd-build` só do `web/MODO_WEB.md`, e os
arquivos que o modo cita vêm da pasta-base `web/` (`scripts/starter/modos.tsv`; `scripts/gerar-starter.py:374-423`).
Um catálogo em `sdd-build/references/` não chegaria ao starter sem código novo no gerador.

**Choice:** `.agents/skills/sdd-build/web/references/CATALOGO_QUALIDADE.md`. O `MODO_WEB.md` cita
`references/CATALOGO_QUALIDADE.md` (o gerador copia), e o `SKILL.md` do Open e o `sdd-open.sh` apontam para o
caminho com `web/`.

**Rationale:** uma fonte só, sem cópia gerada (LM-005: duas cópias do mesmo dado derivam), e nenhuma mudança no
`gerar-starter.py`.

**Alternatives Rejected:** 1. O gerador renderiza um `references/qualidade.md` a partir do catálogo: rejeitada,
porque é código novo e um 2º texto para manter em sincronia. · 2. Uma troca em `scripts/starter/trocas/`: rejeitada,
porque copiaria o catálogo inteiro à mão.

**Consequences:** o catálogo não pode citar `sdd/bin/…` (LM-035: lint do gerador); a frase "quem lê por máquina"
diz "o script de regras de qualidade do SDD Open", sem o caminho. Ganho: o starter recebe o catálogo de graça.

### Decision 2: Script irmão `sdd/bin/qualidade-regras.sh`, só de leitura do catálogo
| **Status** | Accepted | · | **Date** | 2026-11-23 |

**Context:** D6. A segurança detecta supabase, vercel e web; a qualidade precisa de python, js, ts, php e sql.

**Choice:** script novo, no molde de `seguranca-varredura.sh` (cabeçalho `USO-INICIO/USO-FIM`, guarda do Python
por `lib/python.sh`, núcleo Python embutido). Modos: `--stack`, `--regras` e `--agents`, com as opções `--raiz` e
`--catalogo`. Saídas: 0, ou 64 com a causa em `🛑 qualidade-regras: …`. Sem varredura de código: as métricas são
da S3.

**Rationale:** o leitor da segurança continua com um dono; a stack de qualidade se detecta por arquivo e não
interfere na publicação.

**Alternatives Rejected:** 1. Modo `--qualidade` no `seguranca-varredura.sh`: rejeitada, porque ficariam 2
taxonomias de stack num script de 652 linhas. · 2. Ler o catálogo direto no `sdd-open.sh` com `sed`: rejeitada,
porque é um 2º parser (LM-005).

**Consequences:** um arquivo a mais no `MANIFEST.txt` (LM-037). A detecção de stack (Decision 5) fica neste script
e no `checar.sh`, com teste de paridade.

### Decision 3: Evidência de lint em logs próprios, e slot vazio é aviso, nunca violação
| **Status** | Accepted | · | **Date** | 2026-11-23 |

**Context:** AT-001 e AT-002. O repositório do próprio Open e quase todas as fixtures de teste não têm
`sdd/config.yaml` com `lint_cmd`. Exigir a linha `lint: slot vazio` como violação reprovaria todo BUILD_REPORT
antigo e as fixtures de cerca de 14 módulos de teste.

**Choice:** em `report-lint.py`, a função nova `check_lint(content, root, feature, warnings)`:
- para cada slot cheio (`project.lint_cmd` ⇒ `LINT.log`; `project.typecheck_cmd` ⇒ `TIPOS.log`), o log em
  `sdd/reports/evidence/{F}/` é obrigatório. Ele precisa:
  - existir e não estar ignorado pelo git (reusa `git_ignorado`);
  - ter a 1ª linha começando por `$ ` + o comando do slot (prefixo: o Build acrescenta os arquivos da tarefa);
  - ter a última linha não vazia no formato `[exit=<n>]` (LM-018), com `n = 0`. Exceção (revisão do DESIGN, N1):
    `n ≠ 0` com `LINT.antes.log` (ou `TIPOS.antes.log`) gravado antes da 1ª tarefa, com o **mesmo comando do slot**
    (o de antes não tem os arquivos novos; revisão do código, N1) e também `[exit≠0]`, é dívida antiga. Nesse caso vira **aviso** ("o comando já falhava antes do build: confira
    que os erros são os de antes"). Verde antes e vermelho depois é violação.

  Cada falha é uma violação com o conserto em 1 linha.
- os dois slots vazios (ou config ausente) ⇒ procura `lint: slot vazio` fora de cerca; achou ⇒ nada; não achou ⇒
  **aviso** (`warnings`), sem violação.

**Rationale:** bloqueia só o que é objetivo (slot cheio e erro); o slot vazio nunca reprova (restrição do DEFINE).
O DEFINE AT-002 foi ajustado para "aviso" (Revision History do DEFINE 1.1).

**Alternatives Rejected:** 1. Violação sem a linha: rejeitada pelo raio de impacto acima. · 2. Um log só com os
dois comandos: rejeitada, porque não dá para conferir a 1ª linha de cada um.

**Consequences:** um BUILD_REPORT com slot cheio e log com exit 1 é reprovado, salvo quando o log de antes prova a
dívida antiga (aviso). Bloqueia só o que é objetivo: verde antes e vermelho depois.

### Decision 4: Lint sobre os arquivos da tarefa, com queda declarada para o projeto inteiro
| **Status** | Accepted | · | **Date** | 2026-11-23 |

**Context:** ESCOPO §7: o aluno não pode travar por erro de lint de código antigo. A-004.

**Choice:**
- **Lint:** o passo "Verificar" roda `<lint_cmd> <arquivos da tarefa>`. Quando o comando não aceita lista de
  arquivos (`npm run lint` sem `--`, `make lint`), roda inteiro e conta só os erros que citam arquivos da tarefa.
- **Tipos** (revisão do DESIGN, N2): o `typecheck_cmd` roda **como está**, sem arquivos anexados. O `tsc --noEmit`
  com arquivos ignora o `tsconfig.json`, e o `mypy .` com arquivos confere o projeto inteiro do mesmo jeito.
- **Antes da 1ª tarefa**, o Build roda cada slot cheio na forma em que vai rodar no fim e grava `LINT.antes.log` e
  `TIPOS.antes.log`. No fim, grava `LINT.log` (o lint sobre todos os arquivos de código do manifest) e `TIPOS.log`. O lint roda sobre os arquivos do
  manifest que já existiam antes; para os arquivos novos, a execução de antes é o comando sem eles.

**Rationale:** cumpre "só bloqueia o objetivo" sem herdar a dívida antiga.

**Alternatives Rejected:** 1. Sempre o projeto inteiro: rejeitada, porque trava o aluno na dívida antiga. · 2.
Detectar por script se o comando aceita arquivos: rejeitada como frágil (LM-005, heurística sobre texto livre).

**Consequences:** com dívida antiga, o par antes/depois mostra se a tarefa acrescentou erro: verde→vermelho
bloqueia, vermelho→vermelho avisa (Decision 3). São 2 execuções a mais por slot no Build inteiro, não por tarefa.

### Decision 5: Detecção de stack por arquivo, a mesma tabela em 2 leitores com teste de paridade
| **Status** | Accepted | · | **Date** | 2026-11-23 |

**Context:** o `checar.sh` vai para o starter dentro da `sdd-checar-ambiente`, que não depende da `sdd-build`.
Ele não pode ler o catálogo da outra skill.

**Choice:** o catálogo tem a seção `## Ferramentas por stack`, com uma ficha por stack:

| Campo | O que diz |
|---|---|
| `detecta` | arquivos que indicam a stack |
| `config` | arquivos ou chaves que indicam linter já configurado |
| `lint` | comando de lint sugerido |
| `tipos` | comando de tipos sugerido |
| `instalar` | comando de instalar |

O `checar.sh` tem a mesma tabela embutida (função `qualidade_sugestao`). O `test_f30_checar_linter.py` compara os
campos `lint`, `tipos` e `instalar` das duas cópias, nos 2 sentidos.

Stacks:
- **python:** `pyproject.toml`, `setup.py`, `requirements.txt` ou `*.py` na raiz ou em `src/`. Config:
  `ruff.toml`, `.ruff.toml`, `.flake8`, `mypy.ini`, ou `[tool.ruff]`/`[tool.mypy]`/`[tool.flake8]` no `pyproject.toml`.
- **js:** `package.json`. Config: `eslint.config.*`, `.eslintrc*`, `"eslintConfig"` ou script `"lint"` no
  `package.json`.
- **ts:** `tsconfig.json` (soma-se à js).
- **php:** `composer.json` ou `*.php`. Config: `phpcs.xml`, `phpcs.xml.dist`, `.php-cs-fixer*`. Sem comando de tipos: o `php -l` confere um arquivo por chamada e travaria no slot que roda sem arquivos (DEFINE 1.4).
- **sql:** só no `--regras`/`--agents` (pasta `migrations/`, `supabase/migrations/` ou `*.sql`). Sem ferramenta
  sugerida.

Sugere quando a stack existe, `project.lint_cmd` **e** `project.typecheck_cmd` estão vazios (ou o config está
ausente) e não há config de linter.

**Rationale:** LM-005 (duas cópias com teste que compara o texto); o starter funciona sem a `sdd-build` ao lado.

**Alternatives Rejected:** 1. O `checar.sh` lê o catálogo da `sdd-build` se existir: rejeitada, porque teria
comportamento diferente conforme a skill instalada (LM-017). · 2. Só a new-session sugere: rejeitada, porque o
diagnóstico avulso (`sdd-checar-ambiente`) também deve ver.

**Consequences:** mudar uma ferramenta exige mudar as 2 cópias; o teste acusa o esquecimento.

### Decision 6: Modo `checar.sh --linter` para a new-session, e o ⚠️ só no modo normal
| **Status** | Accepted | · | **Date** | 2026-11-23 |

**Context:** o pré-voo da new-session (`--frente`) transforma todo achado em 🔴. A sugestão de linter não pode
impedir a frente.

**Choice:**
- **Modo normal:** um `add_arrumar` por stack sem linter, do tipo "Este projeto em Python não tem conferência de
  estilo (linter) nem de tipos configurada: o código que o agente escreve sai sem ela." O 2º campo do item é o
  comando de instalar, com o par lint/tipos e o slot onde gravar.
- **`--linter`:** sem git e sem rede, imprime `stack<TAB>lint<TAB>tipos<TAB>instalar` por stack a sugerir. Sai 0 com
  sugestão e 1 sem nenhuma. A tabela de tradução fica na seção de slots da new-session: o resultado vira a pergunta
  `[D2 · muda o produto]` "gravo o comando de lint e de tipos no `sdd/config.yaml` desta frente?". Grava só com o
  sim; o comando de instalar o aluno roda.
- `--frente` não muda.

**Rationale:** D2 (propõe, nunca instala); a frente nunca é impedida por qualidade.

**Alternatives Rejected:** 1. Achado ⚠️ no `--frente`: rejeitada, porque o `--frente` não tem ⚠️ (tudo é 🔴).

**Consequences:** uma pergunta nova de decisão no pacote: o número do `test_decisoes_lint` sobe (LM-044).

### Decision 7: Bloco `### Qualidade ao construir` no molde exato da segurança
| **Status** | Accepted | · | **Date** | 2026-11-23 |

**Context:** AT-004 e AT-005. O molde em `bin/sdd-open.sh:445-470` já trata catálogo ausente, Python ausente e
leitor que falha, e o merge entre marcadores já é idempotente.

**Choice:**
- `AGENTS.md.tmpl` ganha, logo depois do bloco de segurança, `### Qualidade ao construir` com 2 linhas de
  introdução e a linha `{{QUALIDADE}}`.
- `gerar_corpo_agents` chama `qualidade-regras.sh --agents --raiz "${ROOT}" --catalogo <pkg>/…/CATALOGO_QUALIDADE.md`
  e, numa falha, usa só `QUA_PONTEIRO`, com `warn "AGENTS.md: regras de qualidade da stack fora (<motivo>) — o
  ponteiro para o catálogo de qualidade ficou"`.
- Um 2º par `-e '/^{{QUALIDADE}}$/{' -e "r …" -e 'd' -e '}'` no mesmo `sed`.
- `--agents` imprime as 6 gerais, as da stack detectada e, por último, o ponteiro (``- Antes de cada tarefa, rode
  `bash sdd/bin/qualidade-regras.sh --regras` …``).

**Rationale:** o mesmo caminho testado da F18/F20; o bloco de segurança fica igual (AT-009).

**Alternatives Rejected:** 1. As regras gerais escritas à mão no template: rejeitada, porque seriam 2 fontes.

**Consequences:** o `sync --check` passa a acusar divergência nos projetos já sincronizados (esperado: é o bloco
novo).

### Decision 8: A coluna `Antes` liga a cobrança do vermelho antes; sem ela, aviso
| **Status** | Accepted | · | **Date** | 2026-11-24 |

**Context:** AT-010 e AT-012. Todo BUILD_REPORT anterior à S2 (os deste repositório, os dos alunos e as fixtures de
pelo menos 8 módulos de teste) tem AT `true` sem `AT-nnn.antes.log`. Cobrar sempre reprovaria todos.

**Choice:** a tabela de critérios ganha a coluna `Antes` (entre Critério e Resultado no molde; o `report-lint.py` a
acha pelo nome, como já acha Resultado e Evidência). Com a coluna, a regra é estrita (Decision 9). Sem a coluna e com
pelo menos um AT `true`, 1 aviso: "a tabela de critérios não tem a coluna `Antes` (relatório anterior à v2.27.0): o
vermelho antes do verde não foi conferido". Cada tabela vale por si (o cabeçalho de cada tabela é relido).

**Rationale:** o mesmo molde da linha `lint: slot vazio` (Decision 3): o relatório novo nasce do molde com a coluna,
a `sdd-build` manda preenchê-la, e o antigo não quebra.

**Alternatives Rejected:** 1. Cobrar sempre: rejeitada pelo raio de impacto acima. · 2. Ligar por data do DEFINE ou
por versão do pacote: rejeitada, porque data em texto livre é heurística (LM-005) e o relatório não carrega a versão.
· 3. Flag no `sdd/config.yaml`: rejeitada, porque o projeto sem config (este repositório) nunca cobraria.

**Consequences:** um relatório que apague a coluna volta ao aviso. O aviso aparece na saída do `report-lint` de toda
release; a `sdd-release` não o trata como violação. Fica registrado em "Fora da S2" do DEFINE.

### Decision 9: O DEFINE classifica o AT; o antes tem o mesmo comando do depois
| **Status** | Accepted | · | **Date** | 2026-11-24 |

**Context:** D3 e AT-010, AT-011. O relatório não sabe se o AT é de comportamento novo; o DEFINE sabe.

**Choice:** função nova `ats_do_define(root, feature)` no `report-lint.py`: lê as tabelas do DEFINE da feature (o mesmo
achado do `define_gate_kind`) e, para cada linha `| AT-nnn |`, guarda:
- `kind`: a célula da coluna cujo cabeçalho cita `kind` (ou `Gate`), sem crases, em minúsculas; sem essa coluna, o
  `kind` do `verify_gate`;
- `continua`: o padrão do AT, não uma palavra solta na linha (revisão do DESIGN, N1). Vale quando uma célula,
  sem `*` e crases, **começa** por `The system shall continue to` (o molde EARS de não-regressão, sem diferença de
  maiúsculas) ou por `Non-regression`/`Não-regressão` (a coluna Padrão). Um critério que só cita a expressão no meio
  (o AT-011 deste DEFINE) é de comportamento novo.

Classes: `novo` (kind começa por `test` ou `cmd`, não `continua`) · `continua` (kind `test`/`cmd` e `continua`) ·
`fora` (outro kind, inclusive `manual-ux`). Para cada AT `true` numa tabela com `Antes`:
- `novo` e `continua` exigem na célula o `` `…/AT-nnn.antes.log` `` desta feature (o mesmo `problema_do_log` da
  evidência: dentro de `evidence/{F}/`, existe, não vazio, 1ª linha `$ `), não ignorado pelo git, com a última linha
  `[exit=<n>]` (o `ler_log_lint` da S1);
- `novo`: `n` fora de 0, 126 e 127 (126/127: a ferramenta nem rodou, como na S1); `continua`: `n = 0`;
- a 1ª linha do antes é igual à do log da evidência (o `AT-nnn.log` citado; sem ele, o 1º log da evidência; sem log,
  só a avaliação, não compara);
- `fora` aceita `N.A. (<motivo>)`; `N.A.` em `novo` ou `continua` é violação;
- AT fora do DEFINE, ou DEFINE ausente: aviso com a causa, sem violação.

Classe de violação nova `vermelho antes`, com o conserto: "rode o comando do AT antes do código e grave
`evidence/{F}/AT-nnn.antes.log` (vermelho; `shall continue to`: verde), citado na coluna `Antes`".

**Rationale:** o "mesmo comando" impede o antes de um comando qualquer que falha; excluir 126/127 impede o vermelho de
ferramenta ausente (LM-002: a asserção precisa avaliar).

**Alternatives Rejected:** 1. O relatório declarar a classe: rejeitada, porque quem constrói escolheria a classe fácil.
· 2. Exigir também o vermelho "avaliando" (marcador de asserção, como o `gate-baseline.sh`): rejeitada nesta fatia
porque o formato de saída varia por ferramenta; fica o 126/127 e a revisão.

**Consequences:** um teste que falha por erro de importação conta como vermelho (o módulo ainda não existe): é o
vermelho natural do TDD em Python.

### Decision 10: `sabotagem.sh` numa cópia de `git archive HEAD`, com a cópia limpa conferida antes
| **Status** | Accepted | · | **Date** | 2026-11-24 |

**Context:** D4, AT-013 e AT-014; LM-009 (sabotagem que desfaz com `git checkout` apagou conserto não commitado).

**Choice:** script novo, no molde do `gate-baseline.sh` (cabeçalho de uso, `RESULTADO:` + `→`, guarda do Python por
`lib/python.sh`, bash 3.2):

```text
bash sdd/bin/sabotagem.sh --feature F --at AT-nnn --arquivo <caminho> --trocar '<trecho>' --por '<trecho>' --cmd '<comando>'
```

1. Uso: os 6 argumentos são obrigatórios; `--arquivo` absoluto (`/…`, `C:…`, `\…`) ou com um componente `..` ⇒ 64;
   fora de repositório git ⇒ 64; `--arquivo` fora do `HEAD` (`git cat-file -e HEAD:<arquivo>`) ⇒ 64 com "commite antes".
2. Cópia: `mktemp -d`, `git archive HEAD | tar -x -C <cópia>`, `trap` que apaga a pasta em `EXIT INT TERM HUP`.
   Mudança não commitada na árvore: aviso de que a cópia é do último commit (não para).
3. Contenção: na cópia, o arquivo é regular, não é link simbólico e o caminho real fica dentro da cópia; senão 64.
4. Cópia limpa: `bash -c "<cmd>"` com `cwd` na cópia, `SDD_TRACE=off`, entrada `/dev/null`. Saiu ≠ 0 ⇒ 3 ("o comando
   já falha sem a sabotagem: o vermelho dela não provaria nada"); 126/127 ⇒ 3 ("o comando nem rodou").
5. Troca: Python lê o arquivo em UTF-8 e exige o trecho **exatamente 1 vez** (0 ou mais de 1 ⇒ 3, com a contagem);
   grava a troca só na cópia.
6. Com a sabotagem: 126/127 ⇒ 3; ≠ 0 ⇒ **0** ("o teste pega o defeito"); 0 ⇒ **2** ("o teste não pega o defeito:
   reforce a asserção do AT"). Em 0 e 2 grava `sdd/reports/evidence/{F}/AT-nnn.sabotagem.log`: 1ª linha `$ <cmd>`,
   2 linhas `# sabotagem: …` e `# sem a sabotagem: exit 0`, a saída (últimas 200 linhas) e `[exit=<n>]` da execução
   sabotada (LM-018: `rc=$?` sem pipe). Em 3 e 64, nenhum log.

**Rationale:** a árvore de trabalho só recebe o log; a cópia limpa conferida antes impede o falso "pegou" de um comando
que já falhava; o trecho único impede sabotar mais do que o DESIGN declarou.

**Alternatives Rejected:** 1. `git worktree add` descartável: rejeitada, porque grava em `.git/worktrees` (a árvore
muda) e deixa resto se o processo morre. · 2. Aplicar e desfazer na árvore: rejeitada pelo LM-009. · 3. Ler a
sabotagem direto da tabela do DESIGN: rejeitada nesta fatia (tabela Markdown com `|` dentro de código é frágil); a
`sdd-build` copia os valores da tabela para a chamada.

**Consequences:** a cópia não tem `.git` (LM-006): comando que depende de git roda sem ele, como no Verify Gate. O
custo é 2 execuções do comando do AT por sabotagem, só de tempo, sem tokens a mais além da chamada.

### Decision 11: Sabotagens declaradas no DESIGN, rodadas no 5a da Build
| **Status** | Accepted | · | **Date** | 2026-11-24 |

**Context:** D4: uma por AT de superfície de risco (dado, dinheiro, acesso, publicação, disponibilidade, do
`sdd/review/CRITERIO_DANO.md`) e ≥ 1 por feature, declaradas no DESIGN para o construtor não escolher a fácil.

**Choice:** a seção 6 da `sdd-design` (estratégia de testes) e o `DESIGN_TEMPLATE.md` ganham a tabela
`| AT | Arquivo | Trocar | Por | O que o teste deve acusar |`. A `sdd-build`, no 5a, roda o `sabotagem.sh` uma vez por
linha, depois do AT verde; exit 0 ⇒ o log vai para a evidência do AT; 2 ⇒ falha da tarefa (reforçar o teste, pela
escada); 3 ⇒ corrigir a declaração (trecho que não casa 1 vez) pelo `sdd-iterate` do DESIGN, ou registrar.

**Rationale:** declarado antes, revisado na revisão do DESIGN, executado por máquina.

**Alternatives Rejected:** 1. `report-lint.py` exigir `AT-nnn.sabotagem.log`: adiado (Fora da S2 do DEFINE), porque
o relatório não sabe quais AT são de risco sem ler a tabela do DESIGN.

**Consequences:** o ≥ 1 por feature fica no texto e na revisão, não em máquina.

### Decision 12: Passo Refatorar entre Verificar e Marcar, ligado por padrão
| **Status** | Accepted | · | **Date** | 2026-11-24 |

**Context:** D7 e AT-015. O `MODO_WEB.md:236` diz "não refatorar código adjacente sem necessidade".

**Choice:** a tarefa do Build passa a ter: 3 Escrever (antes, o vermelho), 4 Verificar, **5 Refatorar**, 6 Marcar.
Refatorar = com teste, lint e tipos verdes, rever **só os arquivos da tarefa** (nome que diz o que é, duplicação
interna, função que faz mais de uma coisa, pelas regras do catálogo de qualidade), rodar de novo o teste do arquivo,
o lint e os tipos, e seguir só verde; vermelho ⇒ desfazer a refatoração. `build.refatorar: false` no
`sdd/config.yaml` pula o passo, e o relatório diz `refatorar: desligado` na Seleção de modo. Chave ausente = ligado.
No `MODO_WEB.md`, o item "Surgical change" passa a dizer: refatorar só o que a tarefa tocou, depois do verde.

**Rationale:** concilia a regra do escoteiro com a mudança cirúrgica: o limite é o arquivo da tarefa.

**Alternatives Rejected:** 1. Refatorar no fim do Build, de uma vez: rejeitada, porque o diff junta tarefas e o teste
que pega o erro fica longe da mudança.

**Consequences:** custo em tokens por tarefa (medido, Decision 14).

### Decision 13: Um texto só para a disciplina, em `web/references/`, com 1 linha de ponteiro
| **Status** | Accepted | · | **Date** | 2026-11-24 |

**Context:** LM-038 (`sdd-build/SKILL.md` 370, `MODO_WEB.md` 488 de 500) e LM-035 (texto que vai ao starter não cita
`sdd/bin/…`). A Decision 1 já pôs o catálogo em `web/references/` para o starter recebê-lo sem código no gerador.

**Choice:** `.agents/skills/sdd-build/web/references/disciplina-de-teste.md` com as 3 práticas (vermelho antes do
verde e as exceções do D3; sabotagem numa cópia descartável, declarada no DESIGN; refatorar depois do verde e a chave
que desliga), em frase positiva, sem `sdd/bin/…` (o script é "o script de sabotagem do SDD Open"). O `SKILL.md` do Open
ganha 1 linha de ponteiro em cada passo tocado e a linha do `sabotagem.sh` no 5a; o `MODO_WEB.md` troca a linha 236 e
acrescenta 1 linha na seção 10.

**Rationale:** uma fonte (LM-005), o starter recebe de graça, as skills ficam longe do teto.

**Alternatives Rejected:** 1. Dois textos (um do Open com o comando, um do starter): rejeitada (LM-005). · 2. Troca em
`scripts/starter/trocas/`: rejeitada, porque a `sdd-build` do starter sai do modo, não do `SKILL.md`.

**Consequences:** o `test_f30_textos_s2.py` gera o starter e confere o arquivo copiado e a ausência de `sdd/bin/`.

### Decision 14: Custo em tokens medido com a mesma tarefa de exemplo, com e sem os passos novos
| **Status** | Accepted | · | **Date** | 2026-11-24 |

**Context:** ESCOPO §7 e a restrição da frente: medir o custo extra dos itens 2, 6 e 7.

**Choice:** uma tarefa de exemplo fixa (um módulo Python pequeno com teste, numa pasta temporária fora do repositório)
feita por 2 agentes de contexto fresco, do mesmo modelo: (A) os passos de antes (Escrever, Verificar, Marcar);
(B) os passos novos (vermelho antes com o log, a sabotagem declarada, Refatorar). Os tokens vêm do uso que o próprio
executor de agente reporta ao fim (nunca de soma de linhas do registro local, LM-036). O BUILD_REPORT registra A, B, a
diferença e a %, com o modelo e a data, na seção "Custo dos passos novos".

**Rationale:** a mesma tarefa isola o custo dos passos; o número entra no relatório como medido, com a amostra (n=1).

**Alternatives Rejected:** 1. Estimar por contagem de palavras do texto novo: rejeitada, porque o custo vem das
execuções, não da leitura.

**Consequences:** n=1 é instável: o relatório diz isso ao lado do número.

### Decision 15: Um script só, e a medição contra a base da frente
| **Status** | Accepted | · | **Date** | 2026-11-25 |

**Context:** AT-017, AT-019. O aviso só serve se falar do código que a frente trouxe.

**Choice:** `sdd/bin/metricas-diff.sh [--raiz DIR] [--base REF]`, no molde do `qualidade-regras.sh`.
- **Base:** `git merge-base HEAD <ref>`, com `<ref>` = `--base`, ou `origin/<project.default_branch>` (padrão `main`),
  ou a branch local de mesmo nome quando o remoto não existe; nenhuma ⇒ 64 com "passe `--base`".
- **Linhas do diff:** a árvore de trabalho contra a base. `git diff --name-status -z -M` dá os pares (antigo, novo);
  por arquivo, `git diff -U0 -M` e só as linhas `@@ … +c,d @@`. Trecho só apagado (`d=0`) conta quando `ini <= c < fim`: o git
  aponta a linha **anterior** ao trecho, e na última linha da função ele fica depois dela (revisão, N3). Arquivo novo
  fora do índice (`ls-files -o --exclude-standard -z`) é novo inteiro. Opções fixas: `core.quotepath=off`,
  `color.ui=never`, `--no-ext-diff --no-textconv
  --text --inter-hunk-context=0 -M` (LM-033). Só arquivo comum (link simbólico fica fora).
- **Código:** por extensão. Complexidade: as linguagens comuns do `lizard`. Duplicação: as mesmas, mais `sh`, `bash` e
  `sql`. Fora: as pastas do método e de terceiros (a mesma lista do `qualidade-regras.sh`). Arquivo do diff que é código
  só da 2ª lista é dito na seção: "fora da medição de complexidade (linguagem sem suporte): N".

**Rationale:** renomear sem mudar não vira código novo; a árvore entra porque o Build pode medir antes do commit.

**Alternatives Rejected:** 1. `lizard`/`jscpd` no repositório inteiro: rejeitada, porque a dívida antiga afoga o aviso. ·
2. O `--changed` do `jscpd` 5: rejeitada, porque só existe na 5 e compara com o HEAD, não com a base da frente.

**Consequences:** uma função antiga e grande com 1 linha mudada aparece: é aviso, e é o momento de ver.

### Decision 16: O bash chama as ferramentas; o Python lê a saída
| **Status** | Accepted | · | **Date** | 2026-11-25 |

**Context:** no Windows, o `jscpd` é um calço (`jscpd`, `jscpd.cmd`) que o `subprocess` do Python não acha pelo nome, e
o Git Bash acha. O teste usa ferramentas falsas, que no Windows também são scripts `sh`.

**Choice:** as ferramentas rodam numa **cópia** no `mktemp`: `arvore/` (todo o código do projeto) e `diff/` (só o código
do diff), sem `.jscpd.json`, `package.json` nem `.gitignore` do projeto (revisão, N2: a chave `jscpd` do `package.json`
mudaria a medida). `command -v` no bash; `lizard --csv` por `xargs -0 -n 50` sobre a lista NUL (nomes com espaço; teto da linha
de comando); `jscpd . --min-tokens N --min-lines 0 --max-lines 1000000 --max-size 6mb --reporters json --output <mktemp> --config
<vazio> --silent`, uma vez em `diff/` e outra em `arvore/`. Arquivo do diff acima de 5 MB é dito como não medido. Cada ferramenta: entrada `/dev/null` (a lista, no `xargs`), stdout e stderr
em arquivos do `mktemp`, `rc=$?` sem pipe, apagados por `trap`. Nunca `npx` (baixaria o pacote; D2).

**Rationale:** o mesmo caminho nos 3 sistemas. `--max-lines` e `--max-size` altos porque o `jscpd` pula calado o arquivo
acima do padrão, e pular calado é o falso "nenhum".

**Alternatives Rejected:** 1. `python3 -m lizard`: rejeitada, porque importaria do diretório do projeto. · 2.
`node_modules/.bin/jscpd`: rejeitada nesta fatia (YAGNI); o PATH é a regra que a mensagem explica.

**Consequences:** sem teto de tempo por ferramenta: o teto que mata grupo não funciona no Git Bash (LM-016).

### Decision 17: Não medido é um estado por métrica, e nunca vira "nenhum"
| **Status** | Accepted | · | **Date** | 2026-11-25 |

**Context:** AT-018; LM-002 e LM-017 (a saída graciosa que esconde o caminho errado).

**Choice:** cada métrica termina em um de 3 estados: `não medido: …`, `nenhum aviso (N medidos)` ou a lista. Só vira
`nenhum aviso` com prova de que mediu: `lizard` saiu 0, o CSV inteiro tem 11 colunas com inteiros, e pelo menos 1
função do diff foi lida, toda de arquivo pedido; `jscpd` saiu 0 nas duas passadas, os JSON têm `duplicates` (lista) e
`statistics.total.sources` ≥ 1, e a passada em `diff/` prova que o código novo foi lido (revisão, N1). Os motivos de
não medido: `<ferramenta> ausente — instale com …` · `<ferramenta> falhou (exit N: 1ª linha do erro)` · `<ferramenta>
devolveu saída que não entendi` · `nenhum arquivo de código no diff` · `nenhuma função do diff encontrada` · `jscpd não
leu nenhum arquivo do diff`. Instalar: `python3 -m pip install lizard` e `npm install -g jscpd`. Com o diff sem código, as
ferramentas não são chamadas, e a ausência não é dita.

**Rationale:** é o risco nº 1 da fatia: a ausência de medida ler como qualidade.

**Alternatives Rejected:** 1. Exit próprio para "não medido": rejeitada, porque o DEFINE pede exit 0 sempre que rodou.

**Consequences:** o `RESULTADO:` (stderr) diz `AVISOS`, `NÃO MEDIDO` ou `NADA ACHADO`, nesta precedência.

### Decision 18: A seção em stdout, com teto de 20 itens por métrica
| **Status** | Accepted | · | **Date** | 2026-11-25 |

**Choice:** stdout é só a seção Markdown (`RESULTADO:` em stderr, como o `--aplicar` do `playbook-curator.sh`), com
`### Complexidade` e `### Duplicação`. Item de função: `` `arq:ini-fim` `nome`: complexidade 15 (limite 10) · 70 linhas
(limite 60) · 6 parâmetros (limite 5) ``, só as medidas acima do limite, a pior primeiro. Item de par:
`` `a:ini-fim` repete `b:ini-fim` (N linhas, N tokens) ``. Pares ficam só se os dois lados são código e ao menos um
toca o diff; repetidos são unidos. Acima de 20: "e mais N". Nomes sem quebra de linha, caractere de controle nem crase.

**Rationale:** o relatório recebe texto pronto e curto; o dado do projeto não abre outra seção no relatório.

**Alternatives Rejected:** 1. O script gravar no BUILD_REPORT: rejeitada, porque só o Build edita o relatório.

**Consequences:** o agente cola a saída; o `report-lint` confere só que a seção existe.

### Decision 19: A chave `qualidade:` no config liga a exigência da seção
| **Status** | Accepted | · | **Date** | 2026-11-25 |

**Context:** AT-021. O ESCOPO pede que o `report-lint.py` exija a seção; o relatório antigo não a tem.

**Choice:** `check_qualidade`: procura, fora de cerca, o título `## Qualidade (avisos)` com ao menos uma linha não vazia
antes do próximo `## `. Faltou: com o mapa `qualidade:` no `sdd/config.yaml`, violação da classe `qualidade`; sem ele,
aviso. O conteúdo da seção não é lido. As 4 chaves entram no `config.example.yaml` com os padrões do D5.

**Rationale:** o projeto novo nasce com o mapa; o antigo, que o `upgrade` não mescla, só recebe o aviso.

**Alternatives Rejected:** 1. Exigir pela coluna `Antes`: rejeitada, porque reprovaria os relatórios da S2. · 2. Nunca
exigir: rejeitada, porque o ESCOPO pede.

**Consequences:** quem acrescenta o mapa à mão e roda o lint num relatório antigo cola a seção uma vez.

---

## File Manifest

Fatia S3 (a ordem é a do TDD). Os manifests da S1 (21 arquivos) e da S2 (15) estão nas versões 1.2 (`c4fa53c`) e 2.2
(`fce8c61`) deste DESIGN.

| # | File | Action | Purpose | Agent | Dependencies |
|---|---|---|---|---|---|
| 1 | `tests/test_f30_metricas.py` | Create | AT-017 a AT-021 (repositório git temporário, ferramentas falsas com a saída real, PATH restrito, hash da árvore) | (general) | None |
| 2 | `tests/test_f30_textos_s3.py` | Create | AT-022 (textos, molde, config, starter gerado) | (general) | None |
| 3 | `sdd/bin/metricas-diff.sh` | Create | Decisions 15 a 18 | (general) | 1 |
| 4 | `sdd/bin/report-lint.py` | Modify | `check_qualidade` (Decision 19) | (general) | 1 |
| 5 | `.agents/skills/sdd-build/web/references/metricas-do-diff.md` | Create | O que medir, como ler e o que dizer quando a ferramenta falta; sem `sdd/bin/` | (general) | 2 |
| 6 | `.agents/skills/sdd-build/SKILL.md` | Modify | Chamada no 5b e ponteiro; seção obrigatória no 6; versão 2.17.0 | (general) | 3, 5 |
| 7 | `.agents/skills/sdd-build/web/MODO_WEB.md` | Modify | 1 linha de ponteiro; versão 2.17.0; ≤ 500 linhas | (general) | 5 |
| 8 | `sdd/templates/BUILD_REPORT_TEMPLATE.md` | Modify | Seção `## Qualidade (avisos)` (e no molde do starter, `sdd-build/web/assets/BUILD_REPORT_TEMPLATE.md`) | (general) | 3 |
| 9 | `sdd/templates/fragments/EVIDENCIA.md` | Modify | Contrato da seção | (general) | 4 |
| 10 | `sdd/config.example.yaml` | Modify | `qualidade:` com os 4 limites | (general) | None |
| 11 | `docs/cli-conventions.md` | Modify | Linha do `metricas-diff.sh` e palavras novas | (general) | 3 |
| 12 | `tests/test_f15_slots_textos.py` | Modify | Versão fixa da `sdd-build` | (general) | 6 |
| 13 | `tests/test_f18_f20_textos.py` | Modify | Versão fixa da `sdd-build` | (general) | 6 |
| 14 | `tests/test_correcoes_w0.py` | Modify | Versão fixa da `sdd-build` | (general) | 6 |
| 15 | `tests/test_contrato_build_release.py` | Modify | Versão fixa da `sdd-build` | (general) | 6 |
| 16 | `tests/test_f19_textos.py` | Modify | Versão fixa da `sdd-build` | (general) | 6 |
| 17 | `MANIFEST.txt` | Modify | Itens 1, 2, 3, 5 (LM-037) | (general) | 1, 2, 3, 5 |

**Total Files:** 17

Mais tarde, no Release: o ledger (minor v2.28.0), o PLANO, a ficha e a geração de teste do starter num clone limpo.

---

## Landmines aplicáveis — S3

Varredura em 2026-11-25 por superfície (mktemp, PATH, jscpd, xargs, MANIFEST, config.yaml, csv, report-lint, pip,
starter, npx, git diff, Windows, SKILL.md) mais o `## Sempre`.

| LM | Veredito | Como |
|---|---|---|
| LM-001, LM-002 | ✔ tratado | Os testes executam o script com a ferramenta, sem ela, quebrada e ilegível; `AT-nnn.antes.log` vermelho; `test -f` no gate |
| LM-003 | ✔ tratado | Commitar antes de cada revisão; conferir o `git diff --stat` |
| LM-004 | N.A. | Sem migration |
| LM-006 | ✔ tratado | A fixture cria o próprio git; o gate roda sem `.git` |
| LM-014, LM-015 | ✔ tratado | `Sandbox.roda` e troca da saída no Python embutido |
| LM-016 | ✔ tratado | Sem teto por grupo de processos (Decision 16) |
| LM-017 | ✔ tratado | "Não medido" tem teste próprio, por causa (Decision 17) |
| LM-018 | ✔ tratado | `rc=$?` sem pipe |
| LM-019 | ✔ tratado | `sdd_python_pronto` sem `2>/dev/null` |
| LM-029, LM-034, LM-042 | ✔ tratado | `BASH`, `path_restrito` e constantes de `tests/apoio.py` |
| LM-033 | ✔ tratado | Opções fixas do git (Decision 15) |
| LM-035 | ✔ tratado | `metricas-do-diff.md` e `MODO_WEB.md` sem `sdd/bin/` |
| LM-037 | ✔ tratado | Item 17; `publish-gate` em modo CI numa cópia antes do gate |
| LM-038 | ✔ tratado | `wc -l` antes e depois (380 e 489); texto longo em `references/` |
| LM-043 | ✔ tratado | Nenhum `npx`; o teste não chama ferramenta real da rede |
| LM-044 | N.A. | Nenhuma pergunta `[Dn]` nova |
| Demais | N.A. | Superfícies fora da S3 |

---

## Landmines aplicáveis — S2

Varredura em 2026-11-24 por superfície (sabotagem, mutante, `git archive`, `mktemp`, baseline, `exit 0`, `[exit=`,
evidência, MANIFEST.txt, starter, subprocess, Windows, SKILL.md) mais o `## Sempre`.

| LM | Veredito | Como |
|---|---|---|
| LM-001 | ✔ tratado | Os testes executam `report-lint.py` e `sabotagem.sh` com fixtures dos dois lados; o AT-015 é contrato de texto |
| LM-002 | ✔ tratado | Cada `test_f30_*` novo é rodado antes do código e grava o `AT-nnn.antes.log` vermelho; `test -f` no gate |
| LM-003 | ✔ tratado | Commitar antes de cada revisão externa; conferir `git diff --stat` |
| LM-006 | ✔ tratado | `sabotagem.sh` roda numa cópia sem `.git`; testes conferem o exit exato (0, 2, 3, 64) |
| LM-009 | ✔ tratado | A sabotagem nunca toca a árvore: cópia de `git archive`; hash antes = depois no teste |
| LM-014 | ✔ tratado | `subprocess` via `Sandbox.roda` de `tests/apoio.py` |
| LM-018 | ✔ tratado | O log da sabotagem grava `rc=$?` sem pipe e termina em `[exit=<n>]`; o `report-lint` exige o fim |
| LM-029, LM-042 | ✔ tratado | `BASH` e constantes de plataforma de `tests/apoio.py`; o link simbólico com `SEM_SYMLINK` |
| LM-035 | ✔ tratado | `disciplina-de-teste.md` e `MODO_WEB.md` sem `sdd/bin/`; rodar `test_gerar_starter.py` antes do gate |
| LM-036 | ✔ tratado | Custo em tokens pelo uso que o executor reporta, nunca somando o registro local (Decision 14) |
| LM-037 | ✔ tratado | Item 15; `publish-gate` em modo CI numa cópia antes do gate |
| LM-038 | ✔ tratado | `wc -l` antes e depois; o texto longo vai para `web/references/`; rodar `test_conversa.py` |
| LM-044 | N.A. | Nenhuma pergunta `[Dn]` nova |
| Demais | N.A. | Superfícies fora da S2 (migration, OpenRouter, evals, juiz, HOME de CLI) |

---

## Landmines aplicáveis — S1

Varredura rodada em 2026-11-23, por superfície (AGENTS.md, sdd-open.sh, sync, init, catálogo, report-lint,
evidência, checar.sh, new-session, starter, gerar-starter, MODO_WEB, SKILL.md, MANIFEST.txt, `[exit=`, subprocess,
Windows, test_decisoes_lint, como-falar, git, status, config.yaml, stack, lint), mais o `## Sempre`.

| LM | Veredito | Como |
|---|---|---|
| LM-001 | ✔ tratado | Os testes executam os scripts com fixtures dos 2 lados (log certo e errado, stack com e sem linter); nenhum AT por `grep` de fiação, salvo os de texto (AT-003, AT-007), que são contrato de texto |
| LM-002 | ✔ tratado | Gate com `test -f` (o discover do 3.9 sem testes sai 0, medido); cada teste novo é rodado contra a árvore de antes (falha por ausência do mecanismo) |
| LM-003 | ✔ tratado | Commitar antes da revisão externa; conferir `git diff --stat` |
| LM-005 | ✔ tratado | Catálogo com um leitor só (Decision 2); tabela de ferramentas em 2 cópias com teste de paridade (Decision 5) |
| LM-006 | ✔ tratado | O gate roda numa cópia de `git archive` sem `.git`; o `report-lint` já trata fora de git; testar o exit exato (1 e 64) |
| LM-009 | N.A. | Sem sabotagem na S1 (é da S2) |
| LM-014 | ✔ tratado | `subprocess` nos testes novos via `tests/apoio.py` (`encoding="utf-8", errors="replace"`) |
| LM-015 | ✔ tratado | O núcleo Python do `qualidade-regras.sh` reconfigura stdout/stderr no início (molde da segurança) |
| LM-017 | ✔ tratado | O caminho de reserva (ponteiro) tem teste próprio (AT-005) e o caminho principal também (AT-004) |
| LM-018 | ✔ tratado | O contrato de log exige `[exit=<n>]` no fim; o texto da build manda gravar por script `bash` com `rc=$?` |
| LM-019 | ✔ tratado | `sdd_python_pronto` chamado sem `2>/dev/null` no `gerar_corpo_agents` (molde existente) |
| LM-020 | N.A. | Nenhuma chave falsa nos logs |
| LM-023 | N.A. | Sem lista de exceções no lint |
| LM-025 | ✔ tratado | Detecção de arquivo por `[ -f ]` num laço no `checar.sh`, nunca `ls a b` |
| LM-029 | ✔ tratado | Testes chamam bash pela constante `BASH` de `tests/apoio.py` |
| LM-033 | ✔ tratado | O `checar.sh --linter` não lê saída do git; o `report-lint` reusa `git_ignorado` (já existente) |
| LM-034, LM-042 | ✔ tratado | Plataforma e PATH restrito pelas constantes e ajudantes de `tests/apoio.py` |
| LM-035 | ✔ tratado | Catálogo e MODO_WEB sem `sdd/bin/…`; rodar `test_gerar_starter.py` antes do gate |
| LM-037 | ✔ tratado | Item 20 do manifest; `PUBLISH_GATE_MODE=ci bash scripts/publish-gate.sh <cópia>` antes do gate |
| LM-038 | ✔ tratado | `wc -l` em `sdd-build/SKILL.md` (357), `MODO_WEB.md` (484), `sdd-new-session/SKILL.md` (431) e `sdd-checar-ambiente/SKILL.md` (339) antes e depois; rodar `test_conversa.py` |
| LM-044 | ✔ tratado | Item 19 do manifest |
| LM-004, 007, 008, 010–013, 016, 021, 022, 024, 026–028, 030–032, 036, 039–041, 043 | N.A. | Superfícies fora da S1 (migration, rename, OpenRouter, evals, teto de tempo, juiz, papéis, HOME de CLI) |

---

## Contrato de aceite

O Verify Gate do DEFINE (`git archive HEAD` → `publish-gate` → `test -f` dos 10 testes (5 da S1, 3 da S2, 2 da S3) → `test_f30_*` → suíte
inteira) é o contrato. O avaliador de contexto fresco recebe o DEFINE, este DESIGN e o diff.

---

## Code Patterns

### Pattern 1: ficha do catálogo (formato fixo, lido por máquina)

```markdown
### Q04 — Reusar antes de criar
- stack: todas
- frase: Antes de criar uma função, procure no projeto uma que já faça o mesmo e reuse-a; duas funções iguais divergem no primeiro conserto.

## Ferramentas por stack

### python
- detecta: pyproject.toml, setup.py, requirements.txt, *.py
- config: ruff.toml, .ruff.toml, .flake8, mypy.ini, pyproject.toml[tool.ruff], pyproject.toml[tool.mypy], pyproject.toml[tool.flake8]
- lint: ruff check
- tipos: mypy .
- instalar: python3 -m pip install ruff mypy
```

### Pattern 2: `check_lint` no `report-lint.py`

```python
LOGS_LINT = (("lint_cmd", "LINT.log"), ("typecheck_cmd", "TIPOS.log"))
SLOT_VAZIO_RE = re.compile(r"^\s*[-*]?\s*`?lint: slot vazio`?", re.MULTILINE)

def check_lint(content, root, feature, warnings):
    proj, viol = ler_mapa(root, "project"), []
    cheios = [(s, log, proj.get(s, "").strip()) for s, log in LOGS_LINT if proj.get(s, "").strip()]
    if not cheios:
        if not SLOT_VAZIO_RE.search(strip_fences(content)):
            warnings.append("lint e tipos com slot vazio, e o relatório não diz — escreva a linha `lint: slot vazio`")
        return viol
    for slot, nome, cmd in cheios:
        rel = f"sdd/reports/evidence/{feature}/{nome}"
        # existe · não ignorado · 1ª linha "$ <cmd>" (prefixo) · última não vazia "[exit=0]"
        ...
    return viol
```

### Pattern 3: preenchimento no `gerar_corpo_agents`

```bash
sed -e "s|{{VENDORS}}|…|g" \
    -e '/^{{SEGURANCA}}$/{' -e "r ${regras}" -e 'd' -e '}' \
    -e '/^{{QUALIDADE}}$/{' -e "r ${qualidade}" -e 'd' -e '}' "${PKG}/AGENTS.md.tmpl" > "${CORPO_AGENTS}"
```

### Pattern 4 (S2): a classe do AT e o antes no `report-lint.py`

```python
NOVO, CONTINUA, FORA = "novo", "continua", "fora"

def classe_do_at(kind, continua):
    if not kind.startswith(("test", "cmd")):
        return FORA
    return CONTINUA if continua else NOVO

def problema_antes(at, classe, cell, evid, root, report_dir, feature, warnings):
    if classe == FORA:
        return None                        # N.A. (<motivo>) ou o log: os dois valem
    # novo/continua: o `AT-nnn.antes.log` desta feature, no formato do contrato, não ignorado
    ...
    if classe == NOVO and rc in ("0", "126", "127"):
        return f"`{rel}` terminou em `[exit={rc}]`: o antes de um AT de comportamento novo tem de falhar"
    if classe == CONTINUA and rc != "0":
        return f"`{rel}` terminou em `[exit={rc}]`: `shall continue to` exige o antes verde"
```

### Pattern 5 (S2): o núcleo do `sabotagem.sh`

```bash
COPIA=$(mktemp -d "${TMPDIR:-/tmp}/sdd-sabotagem.XXXXXX") || inconclusivo "não consegui criar a pasta temporária"
limpa() { rm -rf "${COPIA}"; }
trap limpa EXIT INT TERM HUP
git -C "${RAIZ}" archive HEAD | tar -x -C "${COPIA}" || inconclusivo "git archive falhou"
ALVO="${COPIA}/${ARQUIVO}"
roda_na_copia() { ( cd "${COPIA}" && SDD_TRACE=off bash -c "${CMD}" ) </dev/null >"${SAIDA}" 2>&1; }
roda_na_copia; rc_limpo=$?            # sem pipe (LM-018)
```

### Pattern 6 (S2): a tabela de sabotagens no DESIGN

```markdown
| AT | Arquivo | Trocar | Por | O que o teste deve acusar |
|---|---|---|---|---|
| AT-003 | `src/conta.py` | `if saldo < valor:` | `if False:` | o saque acima do saldo passa |
```

Candidato a pattern: nenhum (o repositório não usa `sdd/patterns/` de camada).

---

## Data Flow

1. `init`/`sync`: `qualidade-regras.sh --agents` → linhas → `{{QUALIDADE}}` → bloco entre marcadores do AGENTS.md.
2. Build: o passo 3 lê `--regras`; o passo 4 roda os slots sobre os arquivos da tarefa; o fim grava os logs; o
   `report-lint` confere.
3. `checar.sh` (normal) → ⚠️ com a sugestão; new-session → `checar.sh --linter` → pergunta → slot (só com o sim).

## Integration Points

Nenhum serviço externo. Ferramentas do aluno (ruff, eslint, tsc, phpcs) são só sugeridas, nunca chamadas pelo Open.

---

## Testing Strategy

| Tipo | Escopo | Ferramenta | Meta |
|---|---|---|---|
| integração | AT-017 a AT-020 (S3): `metricas-diff.sh` num repo git com base e frente; ferramentas falsas que devolvem a saída real (`lizard` 1.26.1, `jscpd` 5.4.3) e a mesma fixture com as ferramentas reais quando estão no PATH; ausentes (uma, outra, as 2), exit≠0, CSV e JSON ilegíveis; função intocada, só apagada, renomeada, arquivo novo fora do índice, nome com espaço e acento; limites do config e inválidos; sem código no diff; sem base; sem git | unittest | exit 0 (64 no uso); achados exatos; nunca "0 achados"/"nenhum aviso" sem medida; hash da árvore igual |
| integração | AT-021 (S3): `report-lint.py` com e sem `qualidade:` no config, seção presente, vazia, em cerca, ausente | unittest | 1 só com o mapa e sem a seção; aviso sem o mapa |
| texto | AT-022 (S3): skill, molde, config, contrato, convenções, starter gerado | unittest | presentes; frase positiva |
| integração | AT-010, AT-011, AT-012 (S2): `report-lint.py` num repo git temporário com DEFINE (kinds `test`, `manual-ux`, um `shall continue to`) e relatório com e sem a coluna `Antes`; antes vermelho, verde, ausente, de outro comando, sem `[exit=`, 127, ignorado, `N.A.` em AT novo; DEFINE ausente | unittest | exit 1 exato nas falhas, com a classe `vermelho antes`; 0 nos pares certos; aviso sem a coluna |
| integração | AT-013, AT-014 (S2): `sabotagem.sh` numa fixture git com um teste forte e um fraco; troca que não casa, que casa 2 vezes, caminho absoluto, com `..`, link simbólico para fora, comando que já falha, comando 127, arquivo fora do HEAD, fora de git; `TMPDIR` da fixture sem resto | unittest | 0/2/3/64 exatos; hash da árvore (fora o log) igual antes e depois em todos; log só em 0 e 2 |
| texto | AT-015 (S2): `sdd-build/SKILL.md` (vermelho antes, coluna `Antes`, `sabotagem.sh` no 5a, Refatorar entre Verificar e Marcar, `build.refatorar`), `sdd-design/SKILL.md` e `DESIGN_TEMPLATE.md` (tabela de sabotagens, `CRITERIO_DANO.md`), `BUILD_REPORT_TEMPLATE.md` (coluna `Antes`), `config.example.yaml`; starter gerado com `references/disciplina-de-teste.md` e sem `sdd/bin/` | unittest | presentes, na ordem; frase positiva |
| regressão | AT-016 (S2): o relatório da S1 (`git show c4fa53c:…`) passa no `report-lint` novo com o aviso da coluna; testes do `report-lint`; suíte inteira no gate | unittest + gate | exit 0 |
| unit/integração | AT-001, AT-002: `report-lint.py` em repo git temporário com `sdd/config.yaml` (lint cheio; tipos cheio; os 2; vazio com e sem a linha), logs certo, ausente, ignorado, de outro comando, `[exit=1]`, sem `[exit=` | unittest | exit 1 exato nas 5 falhas; 0 nos certos; aviso no vazio sem a linha |
| texto | AT-003, AT-007: `sdd-build/SKILL.md` passo 4 cita `project.lint_cmd`, `project.typecheck_cmd`, `LINT.log`, `TIPOS.log`, `lint: slot vazio`, "arquivos da tarefa"; new-session cita `checar.sh --linter` e a pergunta `[D2` de gravar o slot | unittest | presentes; frase positiva (sem "não cite") |
| integração | AT-004, AT-005: `init` e `sync` com o pacote em fixtures python, js+ts e sem stack; `sync` 2× ⇒ 1 bloco; catálogo removido de uma cópia do pacote; Python ausente (PATH restrito); `qualidade-regras.sh --stack/--regras/--agents` e uso errado (64) | unittest + `Sandbox`/`path_restrito` de `tests/apoio.py` | bloco certo; ponteiro e warn com a causa; bloco de segurança igual |
| integração | AT-006: `checar.sh` (normal e `--linter`) em fixtures python, js, ts, php, sem stack, com linter configurado e com slot cheio; hash da árvore (`git status --porcelain` + sha de cada arquivo) antes = depois | unittest | ⚠️ só onde falta; `--linter` sai 0/1; árvore idêntica |
| paridade | catálogo `## Ferramentas por stack` × tabela do `checar.sh` | unittest | iguais nos 2 sentidos |
| integração | AT-008: `gerar-starter.py` para uma pasta temporária; o `sdd-build/SKILL.md` gerado tem as 6 regras e o passo de verificar; `references/CATALOGO_QUALIDADE.md` copiado; 0 `sdd/bin/`; 0 ocorrências dos 3 padrões da F29 | unittest | verde |
| regressão | AT-009: suíte inteira, `publish-gate`, `check-versions.py --base origin/main` | gate | exit 0 |

Baseline vermelho: cada `test_f30_*` é rodado contra a árvore antes do código do mecanismo dele e precisa falhar.
Na S2, esse antes vira `evidence/F30_QUALIDADE_CODIGO/AT-nnn.antes.log`, citado na coluna `Antes` do relatório
(o próprio contrato novo, aplicado à S2).

**Sabotagens (S3; Decision 11).** Superfície de risco: o AT-018 e o AT-019 guardam a verdade do aviso; o AT-021, a
**publicação** (o `report-lint` é gate da release).

| AT | Arquivo | Trocar | Por | O que o teste deve acusar |
|---|---|---|---|---|
| AT-018 | `sdd/bin/metricas-diff.sh` | `if estado == "ausente":` | `if estado == "nunca":` | a ferramenta ausente deixa de sair como "ausente" com o comando de instalar |
| AT-019 | `sdd/bin/metricas-diff.sh` | `if not toca_o_diff(plano["diff"], f[0], f[5], f[6]):` | `if False:` | a função que o diff não tocou aparece |
| AT-021 | `sdd/bin/report-lint.py` | `if tem_secao_qualidade(content):` | `if True:` | o relatório sem a seção passa com `qualidade:` no config |

**Sabotagens (S2; Decision 11).** Superfície de risco pelo `sdd/review/CRITERIO_DANO.md`: o AT-010 guarda a
**publicação** (o `report-lint` é gate da release) e o AT-013 guarda **dado** (a árvore de trabalho do aluno).

| AT | Arquivo | Trocar | Por | O que o teste deve acusar |
|---|---|---|---|---|
| AT-010 | `sdd/bin/report-lint.py` | `if classe == NOVO and rc in ("0", "126", "127"):` | `if classe == NOVO and rc in ("126", "127"):` | o antes verde de um AT novo passa |
| AT-013 | `sdd/bin/sabotagem.sh` | `SAIDA="${TRAB}/saida.txt"` | `SAIDA="${RAIZ}/saida.txt"` | a saída do comando cai na árvore de trabalho: o hash muda |

---

## Error Handling

| Error Type | Handling | Retry? |
|------------|----------|--------|
| Catálogo ilegível ou ficha fora do formato | `qualidade-regras.sh` sai 64 com `arquivo:linha` e o motivo; o `sdd-open.sh` cai no ponteiro com a causa | No |
| Python ausente | Ponteiro e o aviso do `sdd_python_pronto` (dito uma vez) | No |
| `lint_cmd` que não aceita arquivos | Decision 4 | No |
| `checar.sh --linter` fora de projeto | Sai 1 (nada a sugerir) | No |
| S2: `sabotagem.sh` com uso errado, caminho fora da cópia, fora de git, arquivo fora do HEAD | 64 com a causa e o uso; nenhum log | No |
| S2: comando que já falha sem a sabotagem, 126/127, trecho que não casa exatamente 1 vez, `git archive` que falha | 3 (inconclusivo) com a causa; nenhum log | No |
| S3: ferramenta ausente, quebrada ou com saída ilegível | "não medido" com a causa, exit 0 (Decision 17) | No |
| S3: limite inválido, sem git, sem base | 64 com a causa | No |
| S2: DEFINE ausente ou AT fora dele, no `report-lint` | Aviso com a causa; o vermelho antes não é conferido | No |

## Configuration

| Config Key | Type | Default | Description |
|------------|------|---------|-------------|
| `project.lint_cmd` | string | `""` | Já existia; passa a rodar a cada tarefa do Build |
| `project.typecheck_cmd` | string | `""` | Já existia; passa a rodar a cada tarefa do Build |

| `qualidade.max_complexidade` · `max_linhas` · `max_parametros` · `min_tokens` | inteiro ≥ 1 | 10 · 60 · 5 · 50 | S3 (D5): limites dos avisos; o mapa presente liga a exigência da seção (Decision 19) |
| `build.refatorar` | bool | `true` | S2 (D7, Decision 12): o passo Refatorar da tarefa; `false` pula e o relatório diz `refatorar: desligado` |

Nenhuma chave nova na S1 (D1). 

---

## Segurança

1. Segredos: N.A. — nenhum segredo novo.
2. Tabelas: N.A. — sem banco.
3. Credencial de agente ou integração: N.A.
4. Cabeçalhos e CORS: N.A. — sem host.
5. Itens aplicados no Define: nenhum (Segurança N.A. na S1). O `checar.sh` continua só lendo (AT-006 confere o
   hash da árvore).
6. S2, `sabotagem.sh` (a única superfície da fatia): a troca acontece só na cópia de `git archive HEAD` numa pasta
   de `mktemp -d`; o caminho declarado é recusado se for absoluto, tiver `..` ou, na cópia, for link simbólico ou
   tiver o caminho real fora dela (um link versionado apontaria para a árvore de trabalho); a cópia é apagada por
   `trap` em `EXIT INT TERM HUP`; a árvore só recebe o log (AT-013 e AT-014 conferem o hash). O comando roda por
   `bash -c` com a mesma confiança do `cmd` do Verify Gate: vem do DESIGN do próprio projeto, sem dado de
   terceiros, rede ou chamada paga.

7. S3, `metricas-diff.sh`: ferramentas do PATH, locais, só de leitura; config próprio para o `jscpd`; saída temporária
   em `mktemp`, apagada por `trap`; nomes do projeto sem quebra de linha nem crase na seção; nada instalado (D2).

## Desempenho

S3: um `git diff` por arquivo mudado, a cópia do código e duas passadas do `jscpd`, uma vez por Build.

N.A. — sem banco. O `checar.sh` só faz `[ -f ]` e uma leitura de `pyproject.toml`/`package.json`: custo
desprezível perto das chamadas de rede dele.

## Observability

S2: `AT-nnn.antes.log` e `AT-nnn.sabotagem.log`, ao lado dos `AT-nnn.log`. Os logs `LINT.log`/`TIPOS.log` são a observabilidade: ficam em `sdd/reports/evidence/{F}/` e vão para o commit.

---

## Advisor Ledger

| # | Fonte | Nota | Decisão | Evidência |
|---|---|---|---|---|
| N1 | auditor claude (`sdd/reports/reviews/EXTERNAL_REVIEW_20261123-201231/auditor.md`) | MED: a queda para o projeto inteiro reprova sempre com dívida antiga | APLICADA | Decision 3 (exceção com log de antes) e Decision 4 |
| N2 | auditor claude (mesma pasta) | MED: `tsc`/`mypy` com arquivos anexados ignoram config ou conferem tudo | APLICADA | Decision 4 (tipos rodam como estão) |
| — | revisor openrouter `qwen/qwen3.7-plus` e 2º revisor codex `gpt-6.1-sol` | 0 achados (o revisor terminou em 26 s) | — | diversidade: vendor · US$ 0,49 |
| S2-N1 | auditor claude (`sdd/reports/reviews/EXTERNAL_REVIEW_20261124-083851/auditor.md`) | MED: `shall continue to` em qualquer lugar da linha classificaria o AT-011 (comportamento novo que cita a expressão) como não-regressão | APLICADA | Decision 9 (2.1): a classe vem do início da célula; fixture com a expressão citada no meio |
| — | S2, rodada D1: revisor openrouter `qwen/qwen3.7-plus` (28 s, 0 achados) e 2º revisor codex `gpt-6.1-sol` (0 achados) | — | — | diversidade: vendor · US$ 0,67 |
| S3-N1 | auditor claude (`sdd/reports/reviews/EXTERNAL_REVIEW_20261125-064417/auditor.md`) | MED: `sources` ≥ 1 no repositório inteiro não prova que o `jscpd` leu o diff | APLICADA | Decisions 16 e 17 (passada só em `diff/`); teste `test_jscpd_que_leu_o_projeto_mas_nao_o_diff` |
| S3-N2 | auditor claude (mesma pasta) | MED: a chave `jscpd` do `package.json` mudaria a medida | APLICADA | Decision 16 (cópia sem config do projeto); teste `test_config_do_projeto_nao_chega_a_ferramenta` |
| S3-N3 | auditor claude (mesma pasta) | MED: o trecho só apagado marcaria a função anterior, intacta | APLICADA | Decision 15 (`ini <= c < fim`); teste `test_apagar_o_que_vem_depois_nao_marca_a_funcao_anterior` |
| — | S3: revisor openrouter `qwen/qwen3.7-plus` (46 s, 0 achados); 2º revisor dispensado pelo script (sem superfície de risco) | — | — | diversidade: vendor · US$ 0,73 |

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 3.6 | 2026-11-25 | build | Rodadas 5 a 7 (codex e auditor): números das ferramentas conferidos, `..` recusado, `--min-lines 0` (medido: o padrão perde trecho de até 5 linhas, e 1 perde o de 1 linha), cobertura com `.vue`. CI do PR: o gancho `sdd/hooks/pre-commit` (fora do manifest) perde linhas no Windows, corrigido |
| 3.5 | 2026-11-25 | build | Rodada 4 (codex e auditor): número enorme no CSV, limite sem teto de dígitos, pasta temporária em outra unidade do Windows |
| 3.4 | 2026-11-25 | build | Rodada 3 (codex): `TMPDIR` relativo, `color.diff`, número fora de faixa; raio de impacto: fixtures de `test_hooks` e `test_claude_adapter` com a seção |
| 3.3 | 2026-11-25 | build | Rodada 2 (codex) e avaliador: mapa numa linha só (64 no script, exigência no lint), remoto sem ancestral ⇒ 64, arquivo grande ou sem leitura dito, cópia em UTF-8, `TMPDIR` no projeto, seta por causa |
| 3.2 | 2026-11-25 | build | Revisão do código, rodada 1 (auditor claude): nome de arquivo do `jscpd` normalizado e conferido na cópia (N1); `--raiz` numa subpasta mede a subpasta, por `--relative` (N2). Molde do starter com a seção |
| 3.1 | 2026-11-25 | design-agent | Revisão do DESIGN da S3: N1, N2 e N3 aplicadas (cópia temporária, prova no diff, trecho só apagado) |
| 3.0 | 2026-11-25 | design-agent | S3: Decisions 15 a 19, manifest de 17 arquivos, landmines e sabotagens da S3 |
| 2.1 | 2026-11-24 | design-agent | Revisão do DESIGN, rodada D1 (auditor claude, N1): a classe `continua` vem do início da célula (molde EARS ou Padrão), não de qualquer ocorrência na linha |
| 2.2 | 2026-11-24 | build | Sabotagem do AT-013 trocada depois do código: a declarada (`ALVO` apontado para a raiz) era barrada pela checagem de caminho (exit 64) e não punha o hash da árvore à prova |
| 2.0 | 2026-11-24 | design-agent | S2: Decisions 8 a 14, manifest de 15 arquivos, landmines e sabotagens da S2; o manifest da S1 fica na 1.2 (`c4fa53c`) |
| 1.0 | 2026-11-23 | design-agent | S1: 7 decisões, 21 arquivos |
| 1.2 | 2026-11-23 | build | Revisão do código (auditor claude, N1 e N2): a dívida antiga confere o comando do slot, não a 1ª linha inteira; o log final cobre todos os arquivos de código do manifest. Avaliador (ciclo 1): PHP sem `php -l` |
| 1.1 | 2026-11-23 | design-agent | Revisão do DESIGN (openrouter qwen + codex, auditor claude): N1 e N2 aplicadas nas Decisions 3 e 4 (log de antes; tipos sem arquivos anexados) |

---

## Next Step

**Ready for:** `/sdd-build sdd/features/DESIGN_F30_QUALIDADE_CODIGO.md`
