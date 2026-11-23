# DESIGN: F30 — Qualidade do código gerado · fatia S1 (itens 1, 3, 4)

> Lint e tipos a cada tarefa do Build com evidência conferida, regras de qualidade por stack no AGENTS.md e no
> texto da build do starter, e sugestão do linter da stack quando o projeto não tem um, sem instalar nada.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | F30_QUALIDADE_CODIGO (fatia S1) |
| **Date** | 2026-11-23 |
| **Author** | design-agent |
| **DEFINE** | [DEFINE_F30_QUALIDADE_CODIGO.md](./DEFINE_F30_QUALIDADE_CODIGO.md) |
| **Status** | Ready for Build |

---

## Architecture Overview

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
    `n ≠ 0` com `LINT.antes.log` (ou `TIPOS.antes.log`) gravado antes da 1ª tarefa, com a **mesma 1ª linha** e
    também `[exit≠0]`, é dívida antiga. Nesse caso vira **aviso** ("o comando já falhava antes do build: confira
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
  `TIPOS.antes.log`. No fim, grava `LINT.log` e `TIPOS.log` com a mesma 1ª linha. O lint roda sobre os arquivos do
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
- **php:** `composer.json` ou `*.php`. Config: `phpcs.xml`, `phpcs.xml.dist`, `.php-cs-fixer*`.
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

---

## File Manifest

| # | File | Action | Purpose | Agent | Dependencies |
|---|---|---|---|---|---|
| 1 | `.agents/skills/sdd-build/web/references/CATALOGO_QUALIDADE.md` | Create | Fonte única: Q01–Q06 gerais, Qnn por stack, `## Ferramentas por stack` (Decisions 1, 5) | (general) | None |
| 2 | `sdd/bin/qualidade-regras.sh` | Create | Único leitor do catálogo: `--stack`, `--regras`, `--agents` (Decision 2) | (general) | 1 |
| 3 | `AGENTS.md.tmpl` | Modify | Bloco `### Qualidade ao construir` com `{{QUALIDADE}}` (Decision 7) | (general) | None |
| 4 | `bin/sdd-open.sh` | Modify | `gerar_corpo_agents` preenche `{{QUALIDADE}}`; ponteiro e warn com causa (Decision 7) | (general) | 2, 3 |
| 5 | `sdd/bin/report-lint.py` | Modify | `check_lint`: LINT.log/TIPOS.log com slot cheio; aviso sem a linha `lint: slot vazio` (Decision 3) | (general) | None |
| 6 | `.agents/skills/sdd-build/SKILL.md` | Modify | Passo 3 lê `qualidade-regras.sh --regras`; passo 4 "Verificar" com os 2 slots, arquivos da tarefa, escada, logs e a linha de slot vazio; versão 2.15.0 (≤ 500 linhas, LM-038) | (general) | 2, 5 |
| 7 | `.agents/skills/sdd-build/web/MODO_WEB.md` | Modify | Seção 6 com as 6 regras e a citação de `references/CATALOGO_QUALIDADE.md`; seção 10 com lint e tipos do projeto e evidência; linha de versão 2.15.0; sem `sdd/bin/` (LM-035); ≤ 500 linhas | (general) | 1 |
| 8 | `sdd/templates/BUILD_REPORT_TEMPLATE.md` | Modify | Verification Results cita `LINT.log`/`TIPOS.log` e a linha `lint: slot vazio` | (general) | 5 |
| 9 | `sdd/templates/fragments/EVIDENCIA.md` | Modify | Contrato: os 2 logs com slot cheio, a linha com slot vazio | (general) | 5 |
| 10 | `.agents/skills/sdd-checar-ambiente/scripts/checar.sh` | Modify | `qualidade_sugestao`, ⚠️ no modo normal, modo `--linter` (Decisions 5, 6) | (general) | None |
| 11 | `.agents/skills/sdd-checar-ambiente/SKILL.md` | Modify | Bullet do ⚠️ de linter e o modo `--linter`; versão menor nova | (general) | 10 |
| 12 | `.agents/skills/sdd-new-session/SKILL.md` | Modify | Slots: com `lint_cmd`/`typecheck_cmd` sem evidência, `checar.sh --linter` → pergunta `[D2]`, grava só com sim; linha na tradução; versão menor nova | (general) | 10 |
| 13 | `sdd/config.example.yaml` | Modify | Comentário de `typecheck_cmd`/`lint_cmd`: rodam a cada tarefa do Build; vazios ⇒ o checar sugere | (general) | None |
| 14 | `tests/test_f30_report_lint.py` | Create | AT-001, AT-002 | (general) | 5 |
| 15 | `tests/test_f30_textos.py` | Create | AT-003, AT-007 | (general) | 6, 7, 12 |
| 16 | `tests/test_f30_agents_qualidade.py` | Create | AT-004, AT-005 e os modos do `qualidade-regras.sh` | (general) | 2, 4 |
| 17 | `tests/test_f30_checar_linter.py` | Create | AT-006 + paridade catálogo × `checar.sh` | (general) | 1, 10 |
| 18 | `tests/test_f30_starter.py` | Create | AT-008 (gera o starter numa pasta temporária) | (general) | 1, 7 |
| 19 | `tests/test_decisoes_lint.py` | Modify | Contagem de perguntas +1 (LM-044) | (general) | 12 |
| 20 | `MANIFEST.txt` | Modify | Itens 1, 2, 14–18 (LM-037) | (general) | 1, 2, 14, 15, 16, 17, 18 |
| 21 | `scripts/gerar-starter.py` | Verify | Sem mudança prevista (Decision 1); o `test_gerar_starter.py` e o AT-008 conferem. Muda só se o lint do gerador acusar citação | (general) | 7 |

**Total Files:** 21

Mais tarde, no Release: `sdd/features/PLANO_F4_F15_CONSOLIDADO.md` (Estado das frentes), a ficha
`sdd/handoffs/HANDOFF_F30_QUALIDADE_CODIGO.md` e a geração do starter em `~/rdd-public/sdd-starter`.

---

## Landmines aplicáveis

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

O Verify Gate do DEFINE (`git archive HEAD` → `publish-gate` → `test -f` dos 5 testes → `test_f30_*` → suíte
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
| unit/integração | AT-001, AT-002: `report-lint.py` em repo git temporário com `sdd/config.yaml` (lint cheio; tipos cheio; os 2; vazio com e sem a linha), logs certo, ausente, ignorado, de outro comando, `[exit=1]`, sem `[exit=` | unittest | exit 1 exato nas 5 falhas; 0 nos certos; aviso no vazio sem a linha |
| texto | AT-003, AT-007: `sdd-build/SKILL.md` passo 4 cita `project.lint_cmd`, `project.typecheck_cmd`, `LINT.log`, `TIPOS.log`, `lint: slot vazio`, "arquivos da tarefa"; new-session cita `checar.sh --linter` e a pergunta `[D2` de gravar o slot | unittest | presentes; frase positiva (sem "não cite") |
| integração | AT-004, AT-005: `init` e `sync` com o pacote em fixtures python, js+ts e sem stack; `sync` 2× ⇒ 1 bloco; catálogo removido de uma cópia do pacote; Python ausente (PATH restrito); `qualidade-regras.sh --stack/--regras/--agents` e uso errado (64) | unittest + `Sandbox`/`path_restrito` de `tests/apoio.py` | bloco certo; ponteiro e warn com a causa; bloco de segurança igual |
| integração | AT-006: `checar.sh` (normal e `--linter`) em fixtures python, js, ts, php, sem stack, com linter configurado e com slot cheio; hash da árvore (`git status --porcelain` + sha de cada arquivo) antes = depois | unittest | ⚠️ só onde falta; `--linter` sai 0/1; árvore idêntica |
| paridade | catálogo `## Ferramentas por stack` × tabela do `checar.sh` | unittest | iguais nos 2 sentidos |
| integração | AT-008: `gerar-starter.py` para uma pasta temporária; o `sdd-build/SKILL.md` gerado tem as 6 regras e o passo de verificar; `references/CATALOGO_QUALIDADE.md` copiado; 0 `sdd/bin/`; 0 ocorrências dos 3 padrões da F29 | unittest | verde |
| regressão | AT-009: suíte inteira, `publish-gate`, `check-versions.py --base origin/main` | gate | exit 0 |

Baseline vermelho: cada `test_f30_*` é rodado contra a árvore antes do código do mecanismo dele e precisa falhar.

---

## Error Handling

| Error Type | Handling | Retry? |
|------------|----------|--------|
| Catálogo ilegível ou ficha fora do formato | `qualidade-regras.sh` sai 64 com `arquivo:linha` e o motivo; o `sdd-open.sh` cai no ponteiro com a causa | No |
| Python ausente | Ponteiro e o aviso do `sdd_python_pronto` (dito uma vez) | No |
| `lint_cmd` que não aceita arquivos | Decision 4 | No |
| `checar.sh --linter` fora de projeto | Sai 1 (nada a sugerir) | No |

## Configuration

| Config Key | Type | Default | Description |
|------------|------|---------|-------------|
| `project.lint_cmd` | string | `""` | Já existia; passa a rodar a cada tarefa do Build |
| `project.typecheck_cmd` | string | `""` | Já existia; passa a rodar a cada tarefa do Build |

Nenhuma chave nova na S1 (D1). `qualidade.*` entra na S3 (D5) e `build.refatorar` na S2 (D7).

---

## Segurança

1. Segredos: N.A. — nenhum segredo novo.
2. Tabelas: N.A. — sem banco.
3. Credencial de agente ou integração: N.A.
4. Cabeçalhos e CORS: N.A. — sem host.
5. Itens aplicados no Define: nenhum (Segurança N.A. na S1). O `checar.sh` continua só lendo (AT-006 confere o
   hash da árvore).

## Desempenho

N.A. — sem banco. O `checar.sh` só faz `[ -f ]` e uma leitura de `pyproject.toml`/`package.json`: custo
desprezível perto das chamadas de rede dele.

## Observability

Os logs `LINT.log`/`TIPOS.log` são a observabilidade: ficam em `sdd/reports/evidence/{F}/` e vão para o commit.

---

## Advisor Ledger

| # | Fonte | Nota | Decisão | Evidência |
|---|---|---|---|---|
| N1 | auditor claude (`sdd/reports/reviews/EXTERNAL_REVIEW_20261123-201231/auditor.md`) | MED: a queda para o projeto inteiro reprova sempre com dívida antiga | APLICADA | Decision 3 (exceção com log de antes) e Decision 4 |
| N2 | auditor claude (mesma pasta) | MED: `tsc`/`mypy` com arquivos anexados ignoram config ou conferem tudo | APLICADA | Decision 4 (tipos rodam como estão) |
| — | revisor openrouter `qwen/qwen3.7-plus` e 2º revisor codex `gpt-6.1-sol` | 0 achados (o revisor terminou em 26 s) | — | diversidade: vendor · US$ 0,49 |

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-11-23 | design-agent | S1: 7 decisões, 21 arquivos |
| 1.1 | 2026-11-23 | design-agent | Revisão do DESIGN (openrouter qwen + codex, auditor claude): N1 e N2 aplicadas nas Decisions 3 e 4 (log de antes; tipos sem arquivos anexados) |

---

## Next Step

**Ready for:** `/sdd-build sdd/features/DESIGN_F30_QUALIDADE_CODIGO.md`
