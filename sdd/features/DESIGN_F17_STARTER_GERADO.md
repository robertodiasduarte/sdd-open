# DESIGN: F17 — starter gerado a partir do Open

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | F17_STARTER_GERADO |
| **Date** | 2026-11-12 |
| **Author** | design-agent |
| **DEFINE** | `sdd/features/DEFINE_F17_STARTER_GERADO.md` (v1.0) |
| **Status** | Ready for Build |

---

## Architecture Overview

```text
 sdd-open (este repositório)                                   clone do sdd-starter (destino)
 ─────────────────────────────                                 ───────────────────────────────
 tag vX.Y.Z ──git archive──► pasta temporária (árvore da tag)
                               │ .agents/skills/<10 da lista>
                               │ sdd/templates/… (moldes citados)
                               │ scripts/starter/{lista.txt, openai.tsv, trocas/, blocos/, raiz/}
                               ▼
 scripts/gerar-starter.py  ── 1. moldes: aplica trocas/_moldes/<arquivo>.md
                              2. por skill: copia → trocas/<skill>.md → regras mecânicas
                                 (moldes para dentro, caminhos, linha de identificação, GENERATED,
                                  bloco "quando migrar", agents/openai.yaml) → GERADO.txt
                              3. raiz/: README, scripts/, .github/workflows/ → GERADO.txt da raiz
                              4. lint do init em tudo o que foi gerado
                              5. só se 1–4 passaram: troca no destino ─────────────────────► skills/<10>/
                                                                                              README.md, scripts/,
                                                                                              .github/workflows/,
                                                                                              GERADO.txt
 starter CI (gerado): python3 scripts/check-gerado.py → 1 se arquivo gerado mudou, falta ou sobra
```

## Components

| Componente | Papel |
|---|---|
| `scripts/gerar-starter.py` | o gerador (Python 3.9 stdlib). Modos: `--tag <vX.Y.Z> <destino>` (gera) e `--lint <pasta>` (só o lint do init, para o teste do baseline) |
| `scripts/starter/lista.txt` | as 10 skills geradas, uma por linha (a ordem fixa a saída) |
| `scripts/starter/openai.tsv` | `skill<TAB>display_name<TAB>short_description<TAB>default_prompt` |
| `scripts/starter/trocas/<skill>.md` | trocas exatas daquela skill; `trocas/_moldes/<arquivo>.md` para moldes de `sdd/templates/` |
| `scripts/starter/blocos/GENERATED.md`, `MIGRAR.md` | o cabeçalho e o bloco final das skills geradas |
| `scripts/starter/raiz/` | o `README.md`, `scripts/` e `.github/workflows/` do starter, que o gerador copia (semente: os arquivos da `v1.5.16`, mais o `check-gerado.py` e o passo dele) |
| `scripts/starter/raiz/scripts/check-gerado.py` | a trava do starter |

---

## Key Decisions

### Decision 1: o gerador é Python, em `scripts/`, e lê tudo da tag

| **Status** | Accepted | · | **Date** | 2026-11-12 |

**Context:** o gerador é ferramenta de quem mantém; o aluno do Open não precisa dele. AT-001 exige ler da tag.
**Choice:** `scripts/gerar-starter.py` (como `scripts/check-versions.py`), chamado com `python3`. Ele extrai a árvore
inteira da tag por `git archive <tag>` lido com `tarfile` (sem depender do `tar` da máquina) para uma pasta temporária
e lê dali as skills, os moldes **e** os próprios dados (`scripts/starter/`). Nada é lido da árvore de trabalho, salvo o
código do gerador.
**Rationale:** a geração fica reprodutível pela tag; o `init` não copia `scripts/` (AT-010).
**Alternatives Rejected:** 1. `sdd/bin/gerar-starter.sh` — rejeitada porque o `init` copiaria o gerador para todo
projeto de aluno · 2. ler da árvore de trabalho — rejeitada: gera o que não foi publicado.
**Consequences:** mudança nos dados do gerador só vale depois de uma tag; o teste monta um repositório com tag.

### Decision 2: trocas exatas em arquivo Markdown com marcadores, aplicadas antes das regras mecânicas

| **Status** | Accepted | · | **Date** | 2026-11-12 |

**Context:** decisão 5 do brainstorm. Trecho de várias linhas em JSON ou TSV é ilegível.
**Choice:** cada troca é um bloco

```text
## <caminho relativo à skill>
<<<< antes
<texto exato do Open, várias linhas>
====
<texto do starter; vazio apaga>
>>>> depois
```

Aplicada ao texto **cru** do Open (o que quem mantém vê); tem de casar exatamente 1 vez, senão exit 65 citando a troca
(arquivo de trocas e nº do bloco), o arquivo alvo e quantas vezes casou. Troca para arquivo que não existe = 65.
**Rationale:** falha alto quando o Open muda o trecho; o texto do Open fica limpo.
**Alternatives Rejected:** 1. regex — rejeitada por LM-005 (heurística sobre texto livre abre o caso vizinho) · 2. blocos
dentro das skills — rejeitada no brainstorm.
**Consequences:** mudança de texto num trecho trocado pede ajustar a troca, e o gerador avisa.

### Decision 3: regras mecânicas fixas, na ordem

| **Status** | Accepted | · | **Date** | 2026-11-12 |

**Choice:** depois das trocas, para cada arquivo de texto da skill:
1. **moldes:** cada `sdd/templates/<caminho>` citado vira o arquivo `references/<nome>` dentro da skill (copiado do molde
   já trocado pelo `_moldes/`) e a citação vira `<pasta desta skill>/references/<nome>`; um molde que cita outro molde
   leva o outro também (fechamento transitivo);
2. **a própria pasta:** `.agents/skills/<esta skill>/` vira `<pasta desta skill>/`;
3. **pasta de irmã gerada:** `.agents/skills/<irmã da lista>/` vira `<pasta das skills>/<irmã>/`;
4. **linha de identificação:** `releases/latest` do sdd-open vira o do sdd-starter, só na linha que começa por `` `<skill> v ``;
5. **`SKILL.md`:** depois do `---` que fecha o frontmatter, o `blocos/GENERATED.md` com a tag; no fim, `blocos/MIGRAR.md`;
6. **`agents/openai.yaml`:** escrito da linha da skill no `openai.tsv` (sem linha ⇒ 65);
7. **`GERADO.txt`:** `# GENERATED …` e uma linha `<sha256>  <caminho relativo à skill>` por arquivo, ordenada
   (formato do `shasum -c`).
**Rationale:** o que é igual em todas as skills não vira troca por skill.
**Consequences:** citação a caminho de skill **não** gerada (ex.: `.agents/skills/sdd-build/`) sobra e o lint reprova:
vira troca.

### Decision 4: o lint do init é uma lista fechada de padrões, com o `CHANGELOG.md` fora

| **Status** | Accepted | · | **Date** | 2026-11-12 |

**Choice:** reprova, com `arquivo:linha`, as ocorrências de `sdd/bin/`, `sdd/templates/`, `sdd/hooks/`, `sdd/review/`,
`sdd/patterns/`, `sdd/playbook.md`, `sdd/invariants.md`, `sdd/WORKFLOW_CONTRACTS.yaml`, `bin/sdd-open.sh`,
`.agents/skills/<nome>/` e "init do sdd-open". Fica fora o `CHANGELOG.md` (é histórico, não instrução). `sdd/config.yaml`
e `AGENTS.md` **não** entram: o primeiro é lido "se existir" pela new-session (decisão 10 do brainstorm) e o segundo é
arquivo comum a vários agentes.
**Rationale:** lista fechada é verificável; baseline vermelho na cópia crua (AT-004).
**Alternatives Rejected:** detectar "dependência do init" pelo sentido — rejeitada (LM-005).

### Decision 5: a troca no destino só depois de tudo passar, e o destino tem de estar limpo

| **Status** | Accepted | · | **Date** | 2026-11-12 |

**Choice:** o gerador monta a saída inteira numa pasta temporária, roda o lint e só então: apaga e recopia cada
`skills/<skill da lista>/`, sobrescreve os arquivos de `raiz/` e grava o `GERADO.txt` da raiz. Destino com `git status
--porcelain` não vazio ⇒ 64 antes de tudo (o git é a rede de segurança de uma falha de escrita no meio).
Modo dos arquivos: o bit de execução vem da tag.
**Consequences:** uma falha de disco no meio deixa o destino sujo, recuperável por `git checkout`/`git clean` no starter.

### Decision 6: o gerador é dono de `README.md`, `scripts/` e `.github/workflows/` do starter

| **Status** | Accepted | · | **Date** | 2026-11-12 |

**Context:** remendo à mão no starter é proibido; a trava precisa nascer da geração; AT-007 precisa rodar os mesmos
scripts que o starter roda.
**Choice:** `scripts/starter/raiz/` espelha esses caminhos. Semente: os arquivos da `v1.5.16`, com 3 mudanças —
`check-gerado.py` novo; o passo "Generated files gate" nos workflows `ci.yml` e `auto-release.yml`, antes dos testes; o
`README.md` com a lista gerada × congelada, o aviso da 1ª geração e o link do irmão avançado trocado de "SpecGate"
(nome abandonado) para o SDD Open. `docs/`, `exemplos/`, `tests/`, `LICENSE`, `NOTICE`, `CONTRIBUTING.md` continuam do
starter até a F17b.
**Consequences:** mudar a infra do starter passa a ser no Open.

### Decision 7: a trava `check-gerado.py`

| **Status** | Accepted | · | **Date** | 2026-11-12 |

**Choice:** na raiz do starter: lê o `GERADO.txt` da raiz e o de cada `skills/*/` que tiver um. Para cada um: arquivo
listado ausente ⇒ falta; sha diferente ⇒ mudou; na pasta da skill, arquivo não listado (fora `GERADO.txt`, `.DS_Store`
e `__pycache__/`) ⇒ sobra. Qualquer um ⇒ exit 1 com `<caminho>: mudou|falta|sobra` e `RESULTADO: …`. `GERADO.txt`
ilegível ⇒ 64. Sem nada gerado ⇒ 0 com aviso. Python stdlib, sem rede.

### Decision 8: troca ou linha da tabela contam como mudança da skill no `check-versions.py` do Open

| **Status** | Superseded (revisão do DESIGN, itens 2 e 3: deixaria vermelho o version gate do próprio Open neste PR e não cobre moldes nem blocos; trocada pela conferência de versão no gerador, Decision 10) | · | **Date** | 2026-11-12 |

**Context:** o version gate do starter exige versão maior quando a pasta da skill muda; uma mudança só na troca ou no
`openai.tsv` mudaria a cópia gerada sem mudar a versão, e o CI do starter reprovaria.
**Choice:** com `--base`, o `check-versions.py` do Open trata mudança em `scripts/starter/trocas/<skill>.md` ou na linha
da skill em `scripts/starter/openai.tsv` como mudança da skill (exige bump). Mudança em `blocos/` ou nas trocas de
`_moldes/` afeta todas: o teste do gerador avisa e o bump vai em todas as geradas.
**Consequences:** a 1ª geração precisa que toda skill gerada tenha versão maior que a do starter: a única igual hoje é
a `sdd-engenharia-reversa-saas` (1.1.0 nos dois), que vai a 1.1.1 com a linha no CHANGELOG.

### Decision 9: o que o Open recebe do starter, e onde

| **Status** | Accepted | · | **Date** | 2026-11-12 |

**Choice:** `sdd-new-session` 1.6.0 (C1 pré-voo à mão: a checagem da pasta sincronizada e os 4 casos, apontando o
texto que já existe na `sdd-checar-ambiente`; C2 cópia para a frente das skills sem arquivo versionado em
`.claude/skills` e `.agents/skills`, e a conferência da `sdd-release` lá; C3 as 2 notas em "Por que cada regra existe";
C4 os 4 textos curtos) · `sdd-prompt-builder` 2.2.0 (sem o `prompt-drift-scan.sh`, os sinais à mão) ·
`sdd-auditoria-harness` 1.2.0 (`collect_evidence.py` e SKILL.md com `AGENTS.md`, `.agents/{skills,agents,scripts}`,
`.codex/`, `sdd/_index.md`; aviso de precedência sem citar número de versão de ferramenta) · `sdd-governanca` 2.4.1
(pós-build = prova por leitura do passo "Aplicar a migration" da `sdd-build`) · `sdd/templates/BRAINSTORM_TEMPLATE.md`
(placeholders neutros).

---

### Decision 10: o gerador confere a versão contra o destino antes de gravar

| **Status** | Accepted | · | **Date** | 2026-11-12 |

**Context:** revisão do DESIGN, itens 2 e 3.
**Choice:** a tag e o commit ficam só no `GERADO.txt` da raiz; o cabeçalho e o `GERADO.txt` de cada skill não os
levam. Antes de gravar, para cada skill gerada que já existe no destino e mudou, a versão do Open tem de ser maior
que a do destino e o `updated` não pode voltar; senão, 65. É a mesma regra do `check-versions.py --base` do starter,
aplicada antes: muda molde, bloco, troca ou o Open, o gerador diz qual skill precisa de versão nova.
**Consequences:** a 1ª geração pede a `sdd-engenharia-reversa-saas` 1.1.1.

### Decision 11: outros ajustes da revisão do DESIGN

| **Status** | Accepted | · | **Date** | 2026-11-12 |

**Choice:** regras de caminho só em `.md`, com o par que define a pasta (`.claude/skills/x/` ou `.agents/skills/x/`)
preservado; a URL do Open trocada em todo arquivo de texto; o lint reprova `.agents/skills/<skill que o starter não
recebe>/` (lista fechada, tirada da tag) e "`init` do sdd-open"; a seção `### Fluxo encadeado` sai inteira;
`scripts/starter/lint-aceitos.tsv` para citação que fica com motivo (código da higiene-dado que convive com o
dispatcher do Open), e aceite sem uso reprova; o `check-gerado.py` acusa arquivo a mais em `scripts/` e
`.github/workflows/`, a falta do `GERADO.txt` da raiz e a skill gerada apagada; o publish-check do starter pula o
`GERADO.txt` (11 dígitos num sha256); o gerador é dono do `.gitattributes` do starter; o gerador recusa rodar se o
código dele difere do que está na tag; o README ganha `sdd-seguranca` e `sdd-loop-builder`, com teste.

## File Manifest

| # | Arquivo | Ação | Propósito | Dependências |
|---|---|---|---|---|
| 1 | `sdd/templates/BRAINSTORM_TEMPLATE.md` | modificar | placeholders neutros (AT-009) | — |
| 2 | `.agents/skills/sdd-governanca/{SKILL.md,references/CATALOGO_GOVERNANCA.md,references/PROCEDIMENTO.md,assets/GOVERNANCA_REVIEW_TEMPLATE.md,CHANGELOG.md?}` | modificar | sem `rdd-audita-schema`; 2.4.1 (AT-009) | — |
| 3 | `.agents/skills/sdd-auditoria-harness/{SKILL.md,scripts/collect_evidence.py}` | modificar | vários motores; 1.2.0 (AT-008) | — |
| 4 | `.agents/skills/sdd-prompt-builder/{SKILL.md,references/sdd-integration.md}` | modificar | drift à mão; 2.2.0 (AT-008) | — |
| 5 | `.agents/skills/sdd-new-session/{SKILL.md,references/como-falar.md}` | modificar | C1–C4; 1.6.0 (AT-008) | — |
| 6 | `.agents/skills/sdd-engenharia-reversa-saas/{SKILL.md,CHANGELOG.md,manifest.json,evals/cases.json}` | modificar | 1.1.1 (Decision 8) | — |
| 7 | `scripts/starter/lista.txt`, `openai.tsv`, `blocos/{GENERATED,MIGRAR}.md` | criar | dados do gerador | — |
| 8 | `scripts/starter/raiz/{README.md,scripts/check-versions.py,scripts/publish-check.sh,scripts/package.sh,scripts/check-gerado.py,.github/workflows/ci.yml,.github/workflows/auto-release.yml,.github/workflows/release.yml}` | criar | infra do starter (Decisions 6, 7) | 7 |
| 9 | `scripts/gerar-starter.py` | criar | o gerador (Decisions 1–5) | 7, 8 |
| 10 | `scripts/starter/trocas/*.md`, `trocas/_moldes/*.md` | criar | trocas medidas pelo lint (AT-004) | 9 |
| 11 | `scripts/check-versions.py` | modificar | Decision 8 | 7 |
| 12 | `tests/test_gerar_starter.py` | criar | AT-001–AT-007, AT-010 (init) | 9–11 |
| 13 | `tests/test_f17_textos.py` | criar | AT-008, AT-009 | 1–6 |
| 14 | testes com versão fixada (`test_f14_textos`, `test_matriz_new_session`, …) | modificar | bumps | 2–6 |
| 15 | `MANIFEST.txt`, `CONTRIBUTING.md` | modificar | arquivos novos; o lembrete da geração na release (COULD) | 7–13 |

**Total Files:** 15

---

## Landmines aplicáveis

| Landmine (⛔) | Fonte | Veredito | Como / Por quê |
|---|---|---|---|
| gate que só confere fiação | LM-001 | ✔ tratado | o teste executa o gerador numa réplica e confere a saída e os exits dos 2 lados |
| asserção sem baseline vermelho | LM-002 | ✔ tratado | lint sobre a cópia crua reprova (AT-004); `check-gerado.py` com 1 byte trocado sai 1 |
| review sobre diff vazio | LM-003 | ✔ tratado | commit antes de cada rodada; `git diff --stat` conferido |
| script que só roda num repo git | LM-006 | ✔ tratado | o gerador é testado com repositório temporário e tag; a suíte roda numa cópia de `git archive` no gate |
| `git diff --name-only` e rename | LM-007 | ✔ tratado | o Decision 8 usa `--no-renames` no diff de `scripts/starter/` |
| `limit_remaining` não é saldo | LM-008 | ✔ tratado | `/credits` antes de cada rodada paga |
| sabotagem com `git checkout --` | LM-009 | ✔ tratado | sabotagem só em cópia de `git archive` |
| teto da OpenRouter cobra sem resposta | LM-010 | ✔ tratado | revisão por partes (`--paths`) se o diff for grande |
| cenário escrito e não executado | LM-011 | N.A. | sem cenário de comportamento novo nesta frente (o `incidente-chave` já rodou no passo 0) |
| 11 dígitos no pacote | LM-012 | ✔ tratado | o `GERADO.txt` não entra no Open; os sha256 só no starter; nada de id de run em arquivo do pacote |
| edição por âncora apaga testes | LM-013 | ✔ tratado | edições de teste por troca exata; contagem de testes antes e depois |
| `text=True` sem `encoding` | LM-014 | ✔ tratado | todo `subprocess` do teste e do gerador com `encoding="utf-8"` |
| Python do Windows em pipe | LM-015 | N.A. | o gerador roda na máquina de quem mantém; o `check-gerado.py` escreve só ASCII nas linhas de resultado |
| heurística sobre texto livre | LM-005 | ✔ tratado | trocas exatas (Decision 2) e lista fechada (Decision 4), sem regex de sentido |
| fallback que esconde o caminho errado | LM-017 | ✔ tratado | sem fallback calado: tag, destino, troca e tabela falham alto |
| zsh sem `PIPESTATUS` | LM-018 | ✔ tratado | logs de evidência por script bash com `rc=$?` |
| `2>/dev/null` em aviso dito uma vez | LM-019 | N.A. | o gerador não chama `sdd_python_pronto` |

---

## Contrato de aceite

N.A. (1 camada: scripts e textos do pacote).

---

## Agent Assignment Rationale

| Agent | Files Assigned | Why This Agent |
|---|---|---|
| (general) | todos | sem especialista no harness |

---

## Code Patterns

### Pattern 1: aplicar uma troca exata

```python
def aplicar(texto, antes, depois, onde):
    n = texto.count(antes)
    if n != 1:
        raise Falha(65, "%s: a troca casou %d vez(es); esperado 1" % (onde, n))
    return texto.replace(antes, depois, 1)
```

### Pattern 2: árvore da tag sem a árvore de trabalho

```python
r = subprocess.run(["git", "-C", raiz, "archive", "--format=tar", tag + "^{commit}"], capture_output=True)
if r.returncode != 0: raise Falha(64, "tag não encontrada: " + tag)
with tarfile.open(fileobj=io.BytesIO(r.stdout)) as t:
    t.extractall(tmp)   # conteúdo do próprio repositório, pasta temporária nova
```

---

## Data Flow

tag → árvore temporária → moldes trocados → 10 skills montadas → raiz montada → lint → (só verde) destino → `GERADO.txt`.

## Integration Points

`git` (archive, status do destino); o starter (só a pasta do clone, sem rede). Nenhuma API.

## Testing Strategy

| Camada | Teste |
|---|---|
| gerador | `tests/test_gerar_starter.py`: repositório temporário = `git archive HEAD` do Open + commit + tag; réplica mínima do starter (as 8 congeladas com `SKILL.md` mínimo, `docs/`, `exemplos/`, `tests/`, a infra da `v1.5.16`); casos dos AT-001 a AT-007 e o caminho triste de cada exit |
| baseline | lint sobre a cópia crua das 10 ⇒ ≠ 0; `check-gerado.py` com 1 byte trocado ⇒ 1 |
| textos | `tests/test_f17_textos.py` (AT-008, AT-009) |
| auditoria | `collect_evidence.py` num repositório só com `.agents/skills/` acha a skill (vermelho na base) |
| real | 1ª geração sobre um clone do starter em pasta própria: logs em `evidence/F17_STARTER_GERADO/` |

## Error Handling

Exits do gerador: 0 gerado · 64 uso (tag inexistente, destino sem a forma do starter, destino sujo) · 65 troca/tabela/
lint · 1 erro de escrita. Cada saída ≠ 0 diz a causa em uma linha e `RESULTADO:` + `→`.

## Configuration

Sem slot novo.

## Segurança

1. **Onde mora cada segredo:** N.A. — sem segredo; o gerador não usa rede nem credencial.
2. **Quem vê e quem muda cada tabela (RLS):** N.A. — sem banco.
3. **Credencial de cada agente ou integração:** N.A. — push, PR e Release no starter são do Roberto, com OK próprio.
4. **Cabeçalhos e CORS do host:** N.A. — sem host.
5. **Itens aplicados no Define:** N.A. (linha Segurança do DEFINE).

## Observability

| Aspect | Implementation |
|---|---|
| Logging | saída do gerador: uma linha por skill gerada e o resumo `RESULTADO:` |
| Metrics | — |
| Tracing | — |

## Advisor Ledger

| # | Nota | Severidade | Veredito | Evidência |
|---|---|---|---|---|
| 1 | `GERADO.txt` reprova no publish-check do starter (11 dígitos num sha256) | HIGH | APLICADA | `scripts/starter/raiz/scripts/publish-check.sh` (`--exclude=GERADO.txt`); `test_at007_o_starter_passa_nas_checagens_dele` |
| 2 | tag no cabeçalho muda as 10 skills a cada geração | HIGH | APLICADA | Decision 10; `test_at003_cada_skill_gerada` (sem a tag na skill) |
| 3 | Decision 8 deixa vermelho o version gate do Open | HIGH | APLICADA | Decision 8 superada pela 10 |
| 4 | teste do gerador não roda no Verify Gate (sem .git) | HIGH | APLICADA | `tests/test_gerar_starter.py` copia as pastas e cria repositório e tag no Sandbox; verde em cópia de `git archive` com o Python 3.9.6 |
| 5 | `check-gerado.py` fácil de burlar | HIGH | APLICADA | `test_at006_cada_mudanca_a_mao_sai_1` (8 casos) |
| 6 | regra 2 estraga comando em script e a definição da pasta | MEDIUM | APLICADA | Decision 11; `test_regra_de_pasta_so_no_markdown_e_o_par_que_define_a_pasta_fica` |
| 7 | lint deixa passar texto só do Open; URL do Open em runtime | MEDIUM | APLICADA | Decision 11; trocas da iniciar-repo e da new-session; `test_at003` (sem `sdd-open/releases/latest`) |
| 8 | padrão `.agents/skills/<nome>/` indefinido | MEDIUM | APLICADA | Decision 11 (lista fechada das não geradas) |
| 9 | réplica do AT-007 sem caso de versão | MEDIUM | APLICADA | réplica com as 8 versões reais; `test_at007_versao_que_nao_sobe_reprova_antes_de_gravar` |
| 10 | regra 1 subespecificada | MEDIUM | APLICADA | regex fechada; molde repetido ⇒ 65; troca da engenharia-reversa; medido: 17 trocas no total (A-001) |
| 11 | README sem as 2 skills novas | LOW/MEDIUM | APLICADA | `test_readme_cita_toda_skill_gerada` |
| 12 | modo, fim de linha, reprodutibilidade, `tests/` das skills | LOW | APLICADA em parte | modo vem da tag; `.gitattributes`; gerador igual ao da tag. Os `tests/` que o starter tinha dentro de 4 skills somem: os equivalentes rodam no Open (REBATIDA_ESCOPO: decisão do brainstorm, testes ficam onde o código é escrito) |

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.1 | 2026-11-12 | design-agent | Revisão do DESIGN em contexto novo (12 notas, 5 HIGH): Decisions 10 e 11, Decision 8 superada |
| 1.0 | 2026-11-12 | design-agent | Initial version |

## Next Step

**Ready for:** `/sdd-build sdd/features/DEFINE_F17_STARTER_GERADO.md`
