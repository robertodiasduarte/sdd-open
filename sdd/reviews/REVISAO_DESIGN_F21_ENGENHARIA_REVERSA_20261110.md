# Revisão do DESIGN — F21_ENGENHARIA_REVERSA (2026-11-10)

Revisor: agente de contexto novo, só leitura (rodou `init` e `sync --check` num projeto temporário fora do repositório). Entrada: DEFINE v1.0, DESIGN v1.0, `ADVISOR_CONSULT.md` e a pasta do pacote 1.0.0 como dado. 38 chamadas de ferramenta, ~6,7 min.

**VEREDITO: PRONTO COM AJUSTES** — 3 HIGH, 6 MED, 4 LOW; cada HIGH deixaria o Verify Gate vermelho.

| # | Sev. | Nota | Evidência citada pelo revisor |
|---|---|---|---|
| 1 | HIGH | o hash M06 de `FONTES.md`/`manifest.json` tem 13 dígitos seguidos e casa `[0-9]{11,}` do `publish-gate` | `scripts/publish-gate-patterns.txt:17`; `scripts/publish-gate.sh:80,106` |
| 2 | HIGH | o teste do lint usa `ROOT` em 4 lugares; o Pattern 1 só redirecionava o script | `tests/test_validate_reverse.py` do pacote, linhas 10-11, 146, 163, 170 |
| 3 | HIGH | `tests/test_decisoes_lint.py` fixa "26 pergunta(s) em 21 arquivo(s)"; a marca de classe é exigida em cada pergunta | `tests/test_decisoes_lint.py:34-37`; `sdd/bin/sdd-decisoes-lint.sh:99-131,150` |
| 4 | MED | AT-009 com SHA-256 fixo das duas skills orquestradas é armadilha para a próxima frente | `git log` das duas `SKILL.md` (17 e 7 commits) |
| 5 | MED | os README não têm tabela de fases; AT-007 contradizia a Decision 5 | `README.md:48,53-58`; `README.pt-BR.md:48,56` |
| 6 | MED | texto do pacote contradiz as dependências do Open (molde em `sdd/templates/`, governança dentro do Define, versões) | `sdd-define/SKILL.md:8,233`; `sdd-brainstorm/SKILL.md:8,78` |
| 7 | MED | o lint byte a byte foge de `docs/cli-conventions.md` sem exceção declarada | `docs/cli-conventions.md:19-22,85-96` |
| 8 | MED | links relativos do `SKILL.md` abrem, na cópia gerada, o molde com cabeçalho | `tests/test_sdd_kb.py:243-245` |
| 9 | MED | `ESCOPO_CONFIRMADO.md` cita o produto real e o DESIGN mandava não reescrevê-lo | linha 56 do arquivo no pacote |
| 10 | LOW | "19 skills" em texto público sem teste | `README.md:51`; `docs/pt-BR/guia-do-aluno.md:6,209` |
| 11 | LOW | comparação de SHA-256 sem `.gitattributes` | `.gitattributes:1-2` |
| 12 | LOW | `__pycache__` dentro da pasta da skill; leitura sem `encoding` | inferência, não executada |
| 13 | LOW | skill portada fora da lista `PORTADAS` | `tests/test_matriz_new_session.py:101-125` |

Conferidos sem achado: só 3 testes contam skills; o `init` não tem lista fixa de skills; `check-versions.py` aceita skill nova; a Decision 3 está certa (`.md` sem frontmatter ganha 2 linhas de comentário no topo, `.py` com shebang ganha 2 linhas depois dele e compila, `.json` sai idêntico); nada no teste do lint exige Python ≥ 3.10; `init --vendors claude --yes` e `sync --check` existem e saíram 0 num projeto temporário.

Vereditos por nota: Advisor Ledger do `DESIGN_F21_ENGENHARIA_REVERSA.md` (as 13 APLICADA).
