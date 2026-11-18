# Raio de impacto — F17c (antes da última rodada de revisão)

Superfícies mudadas e quem as usa fora do diff, conferidas por execução (pacote = `git archive` de `HEAD` da frente;
projeto = repositório novo em pasta temporária) ou por busca no repositório inteiro. A sessão percorreu as superfícies
em sequência (passo 0b da `sdd-release`).

| Superfície mudada | Quem usa fora do diff | Conferido | Resultado |
|---|---|---|---|
| `.agents/skills/sdd-{define,design,build}/web/` (pasta nova em cada skill) | `init`, `sync`, `sync --check`, `doctor`, adaptadores de vendor (`.claude/skills/`, cabeçalho `sdd-open:generated`) | `init --vendors claude,codex --yes` num projeto novo: `web/` copiada em `.agents/skills/` e `.claude/skills/`, com o cabeçalho no frontmatter do `MODO_WEB.md` (o mesmo lugar do `SKILL.md`); `doctor` sai 0 ("skills e sdd/bin/ em dia"); `sync --check` EM DIA | ok |
| idem | agente que descobre skills por `SKILL.md` aninhado (Claude Code, `npx skills add`) | o modo se chama `MODO_WEB.md`, não `SKILL.md`; `test_at010_modo_web_nao_e_um_skill_md` | ok |
| `scripts/starter/modos.tsv` com a 3ª coluna (pasta-base) | `scripts/gerar-starter.py` (`ler_modos`), `tests/test_f17b_textos.py` (`CaminhoCurto`), `tests/test_f17c_gerador.py` | `grep -rl modos.tsv` (só esses três); a linha da release, sem 3ª coluna, gera igual (`test_sem_pasta_base_o_modo_continua_na_raiz_da_skill`) | ok |
| `sdd/templates/{DEFINE,DESIGN,BUILD_REPORT}_TEMPLATE.md` | `report-lint.py`, `design-lint.py`, `verify-gate.sh`, `kb-dominios.py`, hooks, `playbook-curator.sh`, `patterns-lint.sh` e os testes que leem os moldes | `grep` em `sdd/bin`, `bin`, `sdd/hooks` por `ruff`, `mypy`, `Lint Check`, `Type Check`, `Tests (pytest)`, `Seleção de modo`, `Drift detectado`: nenhum consumidor por texto; os 12 módulos de teste que leem os moldes passam (356 testes) | ok |
| idem | skills geradas que levam molde | nenhuma das 18 cita esses três moldes pelo caminho (medido): nenhuma versão gerada muda por eles | ok |
| `ux-review-builder` 1.6.0: o validador exige `sdd/features/`, `sdd/reviews/` e "de onde estiver" | a `ux-review` que a builder gera (do `assets/UX_REVIEW_SKILL_TEMPLATE.md`) | pacote montado dos 3 moldes da builder (`sdd/UX_STANDARD.md`, `sdd/UX_REVIEW_TEMPLATE.md`, `ux-review/SKILL.md`) e validado: `pass: true`, 0 erros | ok |
| idem | pacote gerado pela builder 1.5.0 num projeto de aluno | reprova com `REGRA_DE_PASTA_AUSENTE` até ser regerado no modo Evolução | **mudança esperada**, registrada no CHANGELOG da builder |
| idem | `sdd-ux-review` do Open | já gravava em `sdd/reviews/UX_REVIEW_{FEATURE}.md` e lia `sdd/UX_STANDARD.md`: a builder passa a combinar com ela | ok |
| `sdd-engenharia-reversa-saas` 1.2.0: sempre `sdd/features/` | `scripts/validate_reverse.py` dela | o script não tem caminho fixo de pasta (`grep sdd/` vazio) | ok |
| define, design e build gerados nas pastas do Open | `sdd-governanca` gerada (lê `sdd/features/DEFINE_`), `RESUMO_ETAPA` gerado (aceita as duas), `sdd-release` gerada (lê `## Migrations aplicadas` do BUILD_REPORT), `exemplos/baixar-nfse/README.md` | leitura dos textos gerados no ensaio; o README do exemplo passou a `sdd/features/` e `sdd/reports/` | ok |
| `sdd-handoff` 2.2.1 com `assets/HANDOFF_EXAMPLE.md` | `handoff-lint.py`, hook do pre-commit (só `sdd/handoffs/`) | `handoff-lint` no exemplo sai 0; o hook não olha `.agents/` | ok |
| `.agents/skills` +31 arquivos | tempo dos testes de `init`/`sync` no CI (Windows ~5 min, teto 30) | medido no CI do PR (BUILD_REPORT) | a medir no PR |

Quebras achadas: **0** em código não modificado (a do validador da builder 1.5.0 é a mudança pedida, com registro).
