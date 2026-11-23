# HANDOFF: F30 — Qualidade do código gerado (Uncle Bob × Open)

> Ficha da feature — **1 arquivo por feature**, slices como subseções (mais recente no topo).

## Ficha

| Attribute | Value |
|-----------|-------|
| **Feature** | F30_QUALIDADE_CODIGO |
| **Objetivo** | O código que o método gera segue Clean Code e TDD: lint e tipos a cada tarefa, regras de qualidade por stack, vermelho antes do verde, sabotagem do gate, refatorar depois do verde e métricas de forma no diff (só aviso) |
| **Status** | ⏸ pausado — S1 com DEFINE e DESIGN prontos; falta a revisão do DESIGN, e o Build não começou |
| **Última sessão** | 2026-11-23 |
| **Branch / pasta** | `f30-sdd-open-uncle-bob` · `/Users/robertoduarte/rdd-worktrees/f30-sdd-open-uncle-bob` (nascida de `origin/main` `4aa0cce`; 3 commits locais de documento, sem push) |
| **Artefatos** | `sdd/features/AVALIACAO_F30_UNCLE_BOB.md` · `sdd/features/ESCOPO_F30_QUALIDADE_CODIGO.md` · `sdd/features/DEFINE_F30_QUALIDADE_CODIGO.md` (v1.1) · `sdd/features/DESIGN_F30_QUALIDADE_CODIGO.md` (v1.0, S1) |
| **Verify Gate** | 🔴 2 (baseline esperado, antes do código) — `bash sdd/bin/verify-gate.sh sdd/features/DEFINE_F30_QUALIDADE_CODIGO.md` |

## Publicado

<!-- publicado:inicio (gerado por sdd/bin/ficha-publicado.py a partir de sdd/releases/; não edite à mão) -->
<!-- publicado:fim -->

## Feito

- **DEFINE da S1** (commit `c539af3`). Contém:
  - os ATs AT-001 a AT-009 em EARS, com as fatias como seções (S2 e S3 reservadas para `sdd-iterate`);
  - D1–D7 respondidas pelo Roberto: "1–7 como recomendado";
  - Governança, Segurança e Desempenho N.A.

  Conferido assim:
  - `verify-gate.sh --print` sai 0 e o `kb-dominios.py` sai 0;
  - o baseline do gate sai 2: grep F29, `check-versions` e `publish-gate` passam, e ele para no `test -f` dos 5 testes que ainda não existem.
- **DESIGN da S1** (commit `c539af3`): 7 decisões, 21 linhas no manifest e a varredura de landmines. `python3 sdd/bin/design-lint.py sdd/features/DESIGN_F30_QUALIDADE_CODIGO.md` sai 0.
- **Revisão do DESIGN:** `bash sdd/bin/sdd-fluxo.sh review-design sdd/features/DESIGN_F30_QUALIDADE_CODIGO.md` saiu 0, ou seja, é **EXIGIDA** (7 arquivos novos, limiar 3).

## Falta

1. Decidir os revisores e rodar a revisão do DESIGN; registrar cada nota no Advisor Ledger do DESIGN.
2. Build da S1: os 21 arquivos do manifest, a suíte inteira e o starter gerado numa pasta temporária com os grep da F29.
3. Release da S1 com 1 OK; depois, a geração seguinte do starter em `~/rdd-public/sdd-starter`.
4. S2 (itens 2, 6, 7) e S3 (itens 5, 8): ciclos DEFINE (por `sdd-iterate`, no mesmo DEFINE) → DESIGN → BUILD → RELEASE.
5. No fim de cada fatia: a linha da F30 no "Estado das frentes" de `sdd/features/PLANO_F4_F15_CONSOLIDADO.md` e esta ficha.

## Definition of Done

- [ ] S1 publicada: o Verify Gate sai 0 e a release foi feita com 1 OK; o starter foi regenerado
- [ ] S2 publicada: S2-b com o hash da árvore igual antes e depois; custo extra em tokens dos itens 2, 6 e 7 no BUILD_REPORT
- [ ] S3 publicada: ferramenta ausente dá "não medido", nunca "0 achados"; métrica só avisa
- [ ] CI 18 de 18 em cada release

## ⛔ Landmines desta feature

- **O Python 3.9 do sistema** (`/usr/bin/python3`) roda o `unittest discover` sem nenhum teste e sai 0 ("Ran 0 tests … OK"; medido em 2026-11-23). Por isso o gate tem `test -f` explícito dos 5 arquivos `tests/test_f30_*.py`. **Faça isto:** ao criar teste com outro nome, atualize o `test -f` do gate.
- **`sdd-build/web/MODO_WEB.md` tem 484 linhas** e vira o SKILL.md da build no starter. O teto é 500 (LM-038). **Faça isto:** condense o texto novo ou ponha o detalhe no catálogo (`web/references/`).
- **O repositório do Open não tem `sdd/config.yaml`**, e quase todas as fixtures também não. Por isso a linha `lint: slot vazio` ausente é **aviso**, nunca violação (Decision 3; DEFINE 1.1).

## Casos e testes em aberto

- Os 5 testes do gate (ainda não existem): `tests/test_f30_report_lint.py`, `tests/test_f30_textos.py`, `tests/test_f30_agents_qualidade.py`, `tests/test_f30_checar_linter.py` e `tests/test_f30_starter.py`.
- A-003 (detecção de stack por arquivo) e A-004 (o `lint_cmd` aceita lista de arquivos) ficaram para validar no Build.

## Eventos

- 2026-11-23 — O Roberto respondeu D1–D7 "como recomendado". D1 ajustada pelo código: os tipos usam o slot `project.typecheck_cmd`, **que já existe** (`sdd/config.example.yaml:12`), sem slot novo. D7: sai o "desligado no modo `lite`", porque a `sdd-build` não tem esse modo (o `lite` é perfil dos laços da `sdd-loop-builder`).
- 2026-11-23 — O DESIGN mudou o DEFINE para a versão 1.1:
  - AT-002: sem a linha `lint: slot vazio` é aviso;
  - o catálogo foi para `.agents/skills/sdd-build/web/references/CATALOGO_QUALIDADE.md` (Decision 1: o starter monta a build do `web/` e copia o que o modo cita, sem mudar o `gerar-starter.py`).
- 2026-11-23 — Pausa antes da revisão do DESIGN. `sdd.revisor1` e `sdd.auditor` estão vazios no git config, não há `sdd/config.yaml` e não há `OPENROUTER_API_KEY` no ambiente. O Roberto recusou a pergunta de quais engines usar e pediu para documentar e retomar em outra sessão.

## Recomendações

- Escolher os revisores primeiro. Engines no PATH: `claude`, `codex` e `gemini`. Pela memória do agente, o `codex` está sem créditos na conta e só roda via OpenRouter com `CODEX_HOME` temporário. Dois vendors (ex.: `--reviewer gemini --auditor claude`) dão mais que `--um-engine`.
- No Build, comece pelo `report-lint.py` e pelo `qualidade-regras.sh`, os dois mecanismos que os outros usam. Rode cada `test_f30_*` contra a árvore antes do mecanismo dele (baseline vermelho, LM-002).
- Antes do gate inteiro (≈ 30–50 min), rode nesta ordem:
  1. `python3 -B -m unittest discover -s tests -p 'test_gerar_starter.py'`;
  2. o mesmo com `test_conversa.py`;
  3. o mesmo com `test_decisoes_lint.py`;
  4. o mesmo com `test_windows.py`;
  5. o `publish-gate` sobre uma cópia de `git archive` (LM-035, 037, 038, 042, 044).

## Setup

1. `cd /Users/robertoduarte/rdd-worktrees/f30-sdd-open-uncle-bob && git status --short && git log --oneline -1`. Esperado: árvore limpa e `HEAD` no commit desta ficha (acima de `c539af3`).
2. `git fetch origin main && git log --oneline HEAD..origin/main`. Se listar commits, a `main` andou: rode `git rebase origin/main` antes do Build.

## Tarefas

1. **Revisar o DESIGN** — Pronto quando: `bash sdd/bin/adversarial-review.sh --feature F30_QUALIDADE_CODIGO --reviewer <engine> --auditor <outra> --paths "sdd/features/DEFINE_F30_QUALIDADE_CODIGO.md sdd/features/DESIGN_F30_QUALIDADE_CODIGO.md"` sair 0 e cada nota estiver no Advisor Ledger do DESIGN como APLICADA, REBATIDA_EVIDENCIA ou REBATIDA_ESCOPO (ou a dispensa estiver registrada com motivo, se o Roberto preferir).
2. **Fazer o Build da S1** (`/sdd-build sdd/features/DESIGN_F30_QUALIDADE_CODIGO.md`) — Pronto quando:
   - `bash sdd/bin/verify-gate.sh sdd/features/DEFINE_F30_QUALIDADE_CODIGO.md` sair 0;
   - `python3 sdd/bin/report-lint.py sdd/reports/BUILD_REPORT_F30_QUALIDADE_CODIGO.md` sair 0;
   - o BUILD_REPORT trouxer o starter gerado numa pasta temporária com os grep da F29 em 0.
3. **Fazer a Release da S1** (`/sdd-release`) com 1 OK; depois, gerar o starter em `~/rdd-public/sdd-starter` e atualizar o "Estado das frentes" e esta ficha.
4. **Repetir para a S2 e a S3**, com `sdd-iterate` sobre o mesmo DEFINE.

## Ship

- **Publicar:** cada fatia pela `sdd-release` (versão nova do Open), seguida da geração do starter.
- **Limpar:** só no fim da S3. Remover a worktree `git worktree remove /Users/robertoduarte/rdd-worktrees/f30-sdd-open-uncle-bob` e a branch `f30-sdd-open-uncle-bob` (rodado de fora da worktree), e arquivar em `sdd/archive/F30_QUALIDADE_CODIGO/`.

---

## Prompt de retomada

```text
Retomar a feature F30_QUALIDADE_CODIGO do sdd-open (frente f30-sdd-open-uncle-bob).

Contexto: a F30 faz o código gerado pelo método seguir Clean Code e TDD (itens 1–8 da avaliação), em 3 fatias
publicáveis: S1 qualidade por stack (itens 1, 3, 4), S2 disciplina de teste (2, 6, 7), S3 métricas no diff, só
aviso (5, 8). A S1 tem DEFINE (v1.1, AT-001..AT-009, D1–D7 decididas "como recomendado") e DESIGN (7 decisões,
21 arquivos) commitados em c539af3. Paramos ANTES da revisão do DESIGN, que é exigida (review-design saiu 0:
7 arquivos novos). Os revisores não estão configurados (git config sdd.revisor1/sdd.auditor vazios, sem
sdd/config.yaml, sem OPENROUTER_API_KEY no ambiente).

Pasta: /Users/robertoduarte/rdd-worktrees/f30-sdd-open-uncle-bob · branch f30-sdd-open-uncle-bob (de origin/main
4aa0cce; commits locais de documento, sem push).
Leia primeiro: sdd/handoffs/HANDOFF_F30_QUALIDADE_CODIGO.md, depois sdd/features/DEFINE_F30_QUALIDADE_CODIGO.md
e sdd/features/DESIGN_F30_QUALIDADE_CODIGO.md (o porquê: AVALIACAO_F30_UNCLE_BOB.md e ESCOPO_F30_QUALIDADE_CODIGO.md).
Leia a seção "## Sempre" de sdd/playbook.md.
Estado do gate: `bash sdd/bin/verify-gate.sh sdd/features/DEFINE_F30_QUALIDADE_CODIGO.md` saiu 2 em 2026-11-23
(baseline esperado: para no `test -f` dos 5 tests/test_f30_*.py, que ainda não existem).

Setup: git status limpo; `git fetch origin main && git log --oneline HEAD..origin/main` (se andou, rebase).

Próxima ação: perguntar ao Roberto quais engines revisam o DESIGN (no PATH: claude, codex, gemini; o codex só roda
via OpenRouter com CODEX_HOME temporário; recomendação: gemini revisa, claude audita) e rodar
`bash sdd/bin/adversarial-review.sh --feature F30_QUALIDADE_CODIGO --reviewer <engine> --auditor <outra> --paths "sdd/features/DEFINE_F30_QUALIDADE_CODIGO.md sdd/features/DESIGN_F30_QUALIDADE_CODIGO.md"`;
registrar cada nota no Advisor Ledger do DESIGN. Depois: /sdd-build da S1 → /sdd-release (1 OK) → gerar o starter
em ~/rdd-public/sdd-starter → atualizar "Estado das frentes" (sdd/features/PLANO_F4_F15_CONSOLIDADO.md) e a ficha.
Então S2 e S3 com sdd-iterate no mesmo DEFINE.

Restrições: só bloqueia o objetivo (teste e erro de lint/tipos com slot cheio); métrica só avisa; ferramenta
ausente = "não medido", nunca "0 achados"; nada instala no projeto do aluno sem o sim (D2); texto novo de skill em
frase positiva, sem banner e sem "não cite" (F29); a sabotagem da S2 roda em cópia descartável e a árvore fica
idêntica (hash no teste); medir no BUILD_REPORT o custo em tokens dos itens 2, 6 e 7.

Não faça: não mexa no bloco "### Segurança ao construir" do AGENTS.md (AT-009); não cite sdd/bin/ no catálogo nem no
MODO_WEB.md (LM-035, vão para o starter); não deixe a linha "lint: slot vazio" ausente virar violação (Decision 3).
Landmines: MODO_WEB.md tem 484 de 500 linhas (LM-038); arquivo novo no MANIFEST.txt no mesmo commit (LM-037);
pergunta [D2] nova na new-session sobe a contagem do test_decisoes_lint (LM-044); subprocess com encoding utf-8
(LM-014); plataforma pelas constantes de tests/apoio.py (LM-042); o /usr/bin/python3 3.9 roda discover vazio com
exit 0 (por isso o test -f no gate).
```

---

## Histórico de slices

### S1 — Define e Design — 2026-11-23

- O DEFINE foi gravado com as fatias como seções. D1–D7 foram decididas, e a D1 corrigida pelo código: o slot `typecheck_cmd` já existe.
- Achado ao conferir o baseline: no Python 3.9, o discover vazio sai 0. Por isso entrou o `test -f` no gate.
- O DESIGN resolveu 7 decisões:
  - o catálogo fica em `web/references/` (o starter o recebe sem mudar o gerador);
  - o script irmão é o `qualidade-regras.sh`;
  - o slot vazio é aviso;
  - o lint roda sobre os arquivos da tarefa;
  - a tabela de ferramentas tem 2 cópias com teste de paridade;
  - o `checar.sh` ganha o modo `--linter`;
  - o bloco do AGENTS.md segue o molde da segurança.
- Parado antes da revisão do DESIGN: os revisores não estão configurados, e o Roberto pediu para retomar em outra sessão.
