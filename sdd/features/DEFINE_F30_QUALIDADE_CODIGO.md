# DEFINE: F30 — Qualidade do código gerado (Uncle Bob × Open)

> O código que o método gera passa a seguir as boas práticas consagradas (Clean Code, TDD): lint e tipos a
> cada tarefa, regras de qualidade por stack, disciplina de teste e métricas de forma no diff — em 3 fatias
> publicáveis (S1, S2, S3).

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | F30_QUALIDADE_CODIGO |
| **Date** | 2026-11-23 |
| **Author** | Roberto Dias Duarte (decisões) · define-agent (redação) |
| **Status** | Ready for Design (S1) · S2 e S3 a definir por `sdd-iterate` |
| **Clarity Score** | 14/15 |

Entradas: `sdd/features/AVALIACAO_F30_UNCLE_BOB.md` (o porquê, as 15 propostas, a nota) e
`sdd/features/ESCOPO_F30_QUALIDADE_CODIGO.md` (achados com linha, os 8 itens, D1–D7). Sem brainstorm: os dois
documentos fazem esse papel. Um ciclo DEFINE → DESIGN → BUILD → RELEASE por fatia; este arquivo cresce por
`sdd-iterate`, não por arquivo novo.

---

## Problem Statement

O SDD Open prova que o código **faz** o que o aceite pede (Verify Gate, evidência), mas não cuida da **forma**
do código: o passo "Verificar" de cada tarefa do Build é uma frase genérica
(`.agents/skills/sdd-build/SKILL.md:188`), o `project.lint_cmd` só roda de fato na release, o projeto típico de
aluno nem tem linter, e o agente não recebe nenhuma regra de qualidade (só as de segurança, `{{SEGURANCA}}`).
O efeito é código que passa no gate com erro de estilo, de tipos e helper duplicado, descoberto só no fim.

---

## Target Users

| User | Role | Pain Point |
|------|------|------------|
| Aluno iniciante (Open e Starter) | Constrói a 1ª feature com o agente, sem nunca ter usado terminal | Recebe código que "funciona" com erro de lint e de tipos que ele não sabe ver; o projeto dele nem tem linter |
| Aluno da Turma Bravo | Mantém um sistema real com o método | Código feito por agente recria helper que já existe e engole erro; o defeito aparece em manutenção |
| Roberto (mantenedor) | Ensina o método e defende a nota de aderência | Não pode dizer que o método segue Clean Code/TDD: nada no pacote cita nem mede isso |

---

## Goals

| Priority | Goal |
|----------|------|
| **MUST** | S1: lint e tipos rodam a cada tarefa do Build, com o slot cheio, e deixam evidência que o `report-lint.py` confere |
| **MUST** | S1: o AGENTS.md gerado traz as regras de qualidade da stack do projeto, e o Starter as traz no texto da build |
| **MUST** | S1: projeto sem linter recebe a sugestão do padrão da stack, sem nada instalado nem gravado sem o sim |
| **MUST** | S2: vermelho antes do verde, sabotagem do gate em cópia descartável e refatorar depois do verde (itens 2, 6, 7) |
| **SHOULD** | S3: duplicação e complexidade no diff, só aviso (itens 5, 8) |
| **COULD** | Medir a nota de aderência com projetos de exemplo (fora desta frente) |

---

## Success Criteria

- [ ] S1: 100% dos BUILD_REPORTs com `lint_cmd` ou `typecheck_cmd` cheio e sem o log correspondente são reprovados pelo `report-lint.py` (exit 1); 0 reprovações com o log certo ou com os dois slots vazios e a linha declarada.
- [ ] S1: `init` e `sync` em 3 fixtures (Python, JS/TS, sem stack) geram exatamente 1 bloco `### Qualidade ao construir`, com as 6 regras gerais e, nas 2 primeiras, as da stack.
- [ ] S1: o `checar.sh` numa fixture sem linter imprime a sugestão da stack em ≤ 1 bloco e a árvore fica idêntica (hash antes = depois).
- [ ] S1: o starter gerado traz as regras de qualidade no texto da `sdd-build` e passa nos `grep` da F29 (0 ocorrências).
- [ ] Todas as fatias: suíte inteira verde e CI 18 de 18.

---

## Fatia S1 — Qualidade por stack (itens 1, 3, 4)

### Acceptance Tests — S1

> EARS (keywords em inglês, corpo em PT-BR). "Slot cheio" = `project.lint_cmd` ou `project.typecheck_cmd` não
> vazio no `sdd/config.yaml` do projeto. Os logs seguem o contrato de evidência: 1ª linha `$ <comando>`, saída
> verbatim, última linha `[exit=<n>]`.

| ID | Padrão | Critério (EARS) | Gate (`kind`) |
|----|--------|-----------------|---------------|
| AT-001 | Event-driven | **When** o `report-lint.py` confere um BUILD_REPORT de um projeto com `project.lint_cmd` cheio, the system **shall** exigir `sdd/reports/evidence/{F}/LINT.log` com a 1ª linha `$ <o comando do slot>` e a última `[exit=0]`, e, com `project.typecheck_cmd` cheio, o mesmo para `TIPOS.log`; log ausente, ignorado pelo git, de outro comando ou terminado em `[exit=` diferente de 0 ⇒ exit 1 com o conserto em 1 linha; a exceção é a dívida antiga: `[exit≠0]` com `LINT.antes.log`/`TIPOS.antes.log` da mesma 1ª linha também `[exit≠0]` ⇒ aviso, não violação | test |
| AT-002 | State-driven | **While** `project.lint_cmd` e `project.typecheck_cmd` estão vazios, the system **shall** aprovar o BUILD_REPORT (exit 0): com a linha `lint: slot vazio`, sem aviso; sem ela, com um aviso que nomeia a linha que falta, nunca com violação, e sem nunca bloquear o Build por falta de linter | test |
| AT-003 | Event-driven | **When** a tarefa do Build chega ao passo de verificar, the system **shall** mandar rodar `project.lint_cmd` e `project.typecheck_cmd` (os cheios) sobre os arquivos da tarefa, tratar erro como falha da escada de retry e, no fim do Build, gravar `LINT.log`/`TIPOS.log`; o texto da `sdd-build` nomeia os dois slots, os dois logs e a linha `lint: slot vazio` | test |
| AT-004 | Event-driven | **When** o `init` ou o `sync` gera o AGENTS.md num projeto Python ou JS/TS, the system **shall** escrever um bloco `### Qualidade ao construir` com as 6 regras gerais (em frase positiva) e as regras da stack, lidas de `.agents/skills/sdd-build/web/references/CATALOGO_QUALIDADE.md` pelo único leitor dele; sem stack reconhecida, só as gerais; rodar `sync` duas vezes deixa 1 bloco só | test |
| AT-005 | Unwanted | **If** o catálogo de qualidade não está no pacote, o Python não está pronto ou o leitor falha, **then** the system **shall** gerar o AGENTS.md com o ponteiro para as regras e um aviso com a causa (nunca o bloco vazio em silêncio), e o bloco de segurança fica como estava | test |
| AT-006 | Event-driven | **When** o `checar.sh` roda num projeto com stack reconhecida e sem linter ou checagem de tipos (sem config do linter e com os slots vazios), the system **shall** imprimir um aviso ⚠️ com o comando sugerido da stack (Python: `ruff check` e `mypy`; JS/TS: `eslint` e `tsc --noEmit`; PHP: `php -l` e `phpcs`) e o comando de instalar, na voz da `como-falar.md`, sem instalar nada e sem gravar arquivo (hash da árvore antes = depois) | test |
| AT-007 | Event-driven | **When** a `sdd-new-session` acha `lint_cmd` e `typecheck_cmd` sem evidência, the system **shall** rodar `checar.sh --linter`, traduzir a sugestão na voz da `como-falar.md` (o que o linter confere) e perguntar (`[D2]`) se grava os comandos no `sdd/config.yaml` da frente, gravando só com o sim e sem instalar nada | test |
| AT-008 | Event-driven | **When** o `gerar-starter.py` gera o starter numa pasta temporária, the system **shall** levar as regras de qualidade e o passo de verificar com lint e tipos no texto da `sdd-build` do starter (que não tem AGENTS.md), sem citar `sdd/bin/…`, e o starter gerado **shall** passar nos `grep` da F29 (0 ocorrências de `Não cite nem resuma`, `comece com esta linha`, `versão atual: http`) | test |
| AT-009 | Non-regression | The system **shall continue to** passar a suíte inteira (`python3 -m unittest discover -s tests`), o `publish-gate` em modo CI sobre uma cópia de `git archive` e o `check-versions.py --base origin/main`, com o bloco `### Segurança ao construir` do AGENTS.md igual ao de antes | test |

**Padrões considerados:**
- **While:** AT-002 (slots vazios).
- **If–Then:** AT-005 (catálogo, Python ou leitor fora). O `lint_cmd` que não aceita lista de arquivos é decisão
  do Design (cair para o repositório inteiro sem bloquear pelo que é antigo), não AT.
- **Where:** N.A. — não há flag de config nova na S1 (D1: os slots já existem).

### Fora da S1

- Instalar linter (D2: só propõe).
- Slot novo de tipos (D1: o `project.typecheck_cmd` já existe em `sdd/config.example.yaml:12`).
- Bloquear por código antigo: o lint do Build vale para os arquivos da tarefa.

---

## Fatia S2 — Disciplina de teste (itens 2, 6, 7)

> A definir por `sdd-iterate` depois da release da S1. Decisões já tomadas: D3, D4 e D7 (ver Clarifications).
> Proposta de AT no ESCOPO §6 (S2-a, S2-b, S2-c). Segurança só no S2-b: a sabotagem nunca toca a árvore de
> trabalho (hash conferido no teste). Medir o custo extra em tokens dos itens 2, 6 e 7 no BUILD_REPORT.

---

## Fatia S3 — Métricas no diff, só aviso (itens 5, 8)

> A definir por `sdd-iterate` depois da release da S2. Decisão já tomada: D5. Proposta de AT no ESCOPO §6
> (S3-a, S3-b). Ferramenta ausente é "não medido", nunca "0 achados".

---

## Clarifications

### Session 2026-11-23

- [x] (escopo) D1 — Erro de lint ou de tipos no Build bloqueia ou avisa, e onde fica o comando de tipos? → **Bloqueia** com o slot cheio, pela escada de retry; tipos no slot **`project.typecheck_cmd`, que já existe** (o ESCOPO supunha slot novo; o passo 5b da `sdd-build` já o lê no fim do Build). Integrado em AT-001, AT-003.
- [x] (restrições) D2 — Projeto sem linter: instala ou propõe? → **Propõe** o comando exato; slot gravado só com o sim. Integrado em AT-006, AT-007.
- [x] (escopo) D3 — Vermelho antes do verde vale para quais ATs? → ATs `test`/`cmd` de comportamento novo; `shall continue to` exige verde antes; exit 4 fora. Integrar na S2.
- [x] (escopo) D4 — Sabotagem: quantas e quem escolhe? → Uma por AT de superfície de risco (critério do `CRITERIO_DANO.md`) e ≥ 1 por feature, **declaradas no DESIGN**. Integrar na S2.
- [x] (NFRs) D5 — Limites das métricas → complexidade 10, 60 linhas, 5 parâmetros, `jscpd --min-tokens 50`, em `qualidade.*` do config. Integrar na S3.
- [x] (integrações) D6 — Onde fica o catálogo? → Arquivo novo na skill da build (`web/references/CATALOGO_QUALIDADE.md`, para o starter receber; Decision 1 do DESIGN) e **script irmão novo** (não um modo do `seguranca-varredura.sh`: a taxonomia de stack é outra). Integrado em AT-004, AT-005.
- [x] (sinal de conclusão) D7 — Refatorar depois do verde vem ligado? → Ligado, `build.refatorar: false` desliga. Sai o "desligado no modo `lite`": a `sdd-build` não tem esse modo (o `lite` é perfil dos laços da `sdd-loop-builder`). Integrar na S2.

### Segurança

- S1: N.A. — scripts locais que só leem o projeto (o `checar.sh` não instala nem grava); sem login, rota, dado de terceiros ou chamada paga. A fatia S2 trata a única superfície (sabotagem em cópia descartável).

---

## Verify Gate

```yaml
verify_gate:
  kind: test
  cmd: "! grep -rlE 'Não cite nem resuma|comece com esta linha|versão atual: http' .agents/skills && /usr/bin/python3 scripts/check-versions.py --base origin/main && T=$(mktemp -d) && git archive HEAD | tar -x -C $T && PUBLISH_GATE_MODE=ci bash scripts/publish-gate.sh $T && cd $T && test -f tests/test_f30_report_lint.py && test -f tests/test_f30_textos.py && test -f tests/test_f30_agents_qualidade.py && test -f tests/test_f30_checar_linter.py && test -f tests/test_f30_starter.py && SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover -s tests -p 'test_f30_*.py' && SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover -s tests -p 'test_*.py'"
  pass_when: "exit 0"
  threshold: "—"
  manual_fallback: "—"
```

Cobertura: AT-001 e AT-002 em `tests/test_f30_report_lint.py`; AT-003 em `tests/test_f30_textos.py`; AT-004 e
AT-005 em `tests/test_f30_agents_qualidade.py` (init/sync em fixtures Python, JS e sem stack; catálogo ausente);
AT-006 em `tests/test_f30_checar_linter.py` (hash da árvore antes e depois); AT-007 em `tests/test_f30_textos.py`;
AT-008 em `tests/test_f30_starter.py` (gera o starter numa pasta temporária) e no `grep` do gate; AT-009 na
suíte inteira, no `publish-gate` e no `check-versions.py`. O gate roda sobre o que está commitado (`git archive
HEAD`). Baseline vermelho: os 5 `test -f` saem 1 antes do código. Eles existem porque, no Python 3.9 do sistema, o `discover` sem nenhum teste sai 0 (medido em 2026-11-23: "Ran 0 tests … OK"), e assim não provaria nada (LM-002).

---

## Out of Scope

- Itens 9 a 15 da avaliação: dimensão de manutenibilidade na revisão (reavaliar depois da S3), código morto,
  cobertura no diff, hook de formatação, regra de dependência da *Clean Architecture* (opção futura da Turma
  Bravo), mutação completa, checklist SOLID.
- Instalar ferramenta no projeto do aluno sem o sim dele.
- Medir a nota de aderência (candidata a frente seguinte).

---

## Constraints

| Type | Constraint | Impact |
|------|------------|--------|
| Technical | Só bloqueia o que é objetivo: teste e erro de lint ou de tipos com o slot cheio; métrica só avisa; ferramenta ausente é "não medido" | Nenhum gate subjetivo; slot vazio nunca reprova o Build |
| Technical | Texto novo de skill em frase positiva, sem banner e sem "não cite" (F29) | Grep da F29 no gate (AT-008) |
| Technical | SKILL.md ≤ 500 linhas (LM-038); `sdd-build/SKILL.md` tem 357 e `sdd-build/web/MODO_WEB.md` (que vira o SKILL.md do starter) tem 484 | Regras do starter vão para `web/references/`, citadas pelo modo |
| Technical | Texto de skill da `scripts/starter/lista.txt` não cita `sdd/bin/…` (LM-035) | O starter recebe as regras como texto, não pelo script |
| Technical | Arquivo novo no pacote entra no `MANIFEST.txt` no mesmo commit (LM-037); bash 3.2 e Git Bash (F16W); `subprocess` de teste com `encoding="utf-8"` (LM-014); plataforma pelas constantes de `tests/apoio.py` (LM-042) | Checklist do Design |
| Resource | Starter regenerado a cada fatia publicada, em `~/rdd-public/sdd-starter` | Passo da release |

---

## Technical Context

| Aspect | Value | Notes |
|--------|-------|-------|
| **Deployment Location** | `.agents/skills/sdd-build/` (SKILL.md, `references/`, `web/`), `.agents/skills/sdd-checar-ambiente/scripts/checar.sh`, `.agents/skills/sdd-new-session/`, `AGENTS.md.tmpl`, `bin/sdd-open.sh`, `sdd/bin/report-lint.py`, `sdd/bin/` (script irmão novo), `sdd/config.example.yaml`, `scripts/gerar-starter.py`, `tests/` | É o pacote do método; o aluno recebe pelo `init`/`sync` e pelo starter |
| **KB Domains** | nenhum | O repositório não tem `sdd/kb/`; a `sdd-kb` cria uma base quando houver domínio a catalogar |
| **IaC Impact** | None | — |
| **LLM Prompts** | false | Muda texto de skill (instrução ao agente de desenvolvimento), não prompt que roda em produção; nenhum sinal forte |
| **CONTEXTO de domínio** | nenhum (pulado: sem mapa de domínios em `sdd/patterns/dominio.md`; os achados com linha do ESCOPO §2 fazem esse papel) | — |
| **Governança** | N.A. — não trata dinheiro, saldo, tributo, folha nem dado pessoal (texto de skill e scripts do método); N.A. decidido pelo Roberto no escopo da frente | 2026-11-23 |
| **Segurança** | N.A. — S1 sem login, rota, dado de terceiros ou chamada paga; o S2-b (sabotagem em cópia descartável) terá a sua | 2026-11-23 |
| **Desempenho** | N.A. — sem banco | 2026-11-23 |

---

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|----|------------|------------------|------------|
| A-001 | O molde `{{SEGURANCA}}` (`bin/sdd-open.sh:446-470`) serve para `{{QUALIDADE}}` sem mexer no da segurança | Refatorar a geração do AGENTS.md; risco para AT-009 | [x] lido em 2026-11-23 |
| A-002 | O `sdd-build/web/MODO_WEB.md` é a fonte do SKILL.md da build no starter e pode citar `references/…` da pasta `web/` | As regras não chegam ao starter (AT-008) | [x] `scripts/gerar-starter.py:333-357` |
| A-003 | Detectar a stack por arquivo (`pyproject.toml`/`requirements.txt`/`*.py`, `package.json`/`tsconfig.json`, `composer.json`/`*.php`) basta para sugerir o linter | Sugestão errada; o aluno recusa | [ ] Design |
| A-004 | O `lint_cmd` dos projetos aceita lista de arquivos na maioria dos casos | Cair para o repositório inteiro, sem bloquear pelo que é antigo (Design) | [ ] Design |

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---------|-------------|-------|
| Problem | 3 | Achados com arquivo e linha no ESCOPO §2 |
| Users | 3 | 3 personas com dor própria |
| Goals | 3 | MUST/SHOULD por fatia |
| Success | 3 | Contagens e exit codes |
| Scope | 2 | S2 e S3 decididas em D3–D7, mas os ATs delas vêm por `sdd-iterate` |
| **Total** | **14/15** | |

---

## Open Questions

None for S1 — ready for Design. S2 e S3: ATs por `sdd-iterate`, com as decisões já registradas.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-11-23 | define-agent | S1 (itens 1, 3, 4) com D1–D7 decididas; S2 e S3 reservadas |
| 1.3 | 2026-11-23 | build | AT-007: a tradução fica no passo dos slots da new-session, não na tabela do `--frente` (Decision 6: o `--frente` não fala de linter) |
| 1.2 | 2026-11-23 | design-agent | AT-001: exceção da dívida antiga pelo log de antes (revisão do DESIGN, N1) |
| 1.1 | 2026-11-23 | design-agent | AT-002: sem a linha `lint: slot vazio` é aviso, não violação (o repositório e as fixtures não têm config; Decision 3 do DESIGN). AT-004: catálogo em `sdd-build/web/references/` (Decision 1) |

---

## Next Step

**Ready for:** `/sdd-design sdd/features/DEFINE_F30_QUALIDADE_CODIGO.md` (S1). UX Review pulado: sem tela; o
texto ao aluno segue as `references/como-falar.md` das skills tocadas.
