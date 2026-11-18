# DEFINE: F17b — starter gerado, etapa 2

> Mais 5 skills do starter passam a ser geradas do Open: brainstorm, handoff e governança (com o caminho sem
> terminal escrito no próprio texto do Open), a release (gerada de um modo iniciante, GitHub + Vercel, que mora dentro
> da `sdd-release` do Open) e a `ux-review-builder` (que vira a 22ª skill do Open). `docs/`, `exemplos/` e `tests/` do
> starter mudam para o Open. A simplicidade do aluno iniciante é critério de aceite medido. Define, design e build
> ficam congeladas até a F17c.

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | F17B_STARTER_ETAPA2 |
| **Date** | 2026-11-13 |
| **Author** | define-agent (worktree `sdd-open-f17b-starter-etapa2`; branch `feat/f17b-starter-etapa2`, de `origin/main` `d813954` = `v2.13.0`, mais o passo 0 em `ce281d7`) |
| **Status** | Ready for Design |
| **Clarity Score** | 14/15 |
| **Entrada** | `sdd/features/BRAINSTORM_F17B_STARTER_ETAPA2.md` (abordagem A1, por peso; escopo B1, duas frentes) |

---

## Problem Statement

Cinco skills do starter (brainstorm 1.1.0, handoff 1.1.0, governança 1.0.1, release 1.3.0, ux-review-builder 1.4.0) e
`docs/`, `exemplos/`, `tests/` ainda são texto próprio do starter, que diverge do Open (2.3.1, 2.1.2, 2.4.1, 2.11.1) e
exige manutenção dobrada. A release congelada confere o deploy pelo run de um workflow do GitHub Actions, e o aluno do
módulo 7 do RDD10+ v8 publica pela integração GitHub–Vercel. O texto do Open tem regras que o iniciante do starter não
tem hoje (perfil de risco obrigatório, linha de Verify Gate, prova por script, Status formal): gerar sem cuidado
deixaria o caminho do iniciante mais difícil.

## Target Users

| User | Pain Point |
|---|---|
| Roberto, mantenedor dos dois repositórios | 5 skills e 3 pastas mantidas em dobro |
| Aluno iniciante na web (claude.ai, ChatGPT) | precisa de brainstorm, handoff e governança que entreguem no chat, sem terminal e sem regra de mantenedor |
| Aluno do módulo 7 (terminal, GitHub + Vercel, sem o `init` do Open) | precisa de uma release curta, com 1 OK, que confira o deploy da Vercel e diga a URL |
| Quem usa o Open sem o `init` | hoje a `sdd-release` do Open não tem caminho para ele |

---

## Goals

| Priority | Goal |
|---|---|
| **MUST** | brainstorm, handoff e governança do Open com o caminho sem terminal (os itens C da comparação da F17) e na `lista.txt` do gerador |
| **MUST** | `sdd-release` do Open com `references/MODO_INICIANTE.md` (GitHub + Vercel), apontado por 1 linha do `SKILL.md`; o gerador monta a release do starter só desse arquivo (regra "skill de modo") |
| **MUST** | `ux-review-builder` 1.5.0 como 22ª skill do Open, com as convenções do Open, gerada para o starter |
| **MUST** | `docs/`, `exemplos/`, `tests/` do starter em `scripts/starter/raiz/`, atualizados e protegidos pela trava |
| **MUST** | simplicidade do iniciante medida: tabela de paradas com OK do Roberto em cada parada nova, teste do iniciante em agente sem ferramentas, release com 1 OK e sem token |
| **MUST** | 2ª geração pela tag num clone limpo do starter; PR e Release do starter com OK próprio do Roberto |
| **SHOULD** | a `sdd-ux-review` do Open lê o `UX_STANDARD.md` do projeto quando existir |
| **SHOULD** | README do starter (PT e EN) com 15 geradas e 3 congeladas até a F17c |
| **COULD** | `~/.claude/skills/sdd-*` regeneradas pela tag publicada (D6), com OK do Roberto na hora |

---

## Success Criteria

- [ ] O gerador sai 0 sobre uma réplica do starter `v1.5.17` e grava 15 skills; define, design e build ficam byte a byte iguais.
- [ ] A release gerada não traz nenhum arquivo do caminho pesado; a cópia crua da `sdd-release` reprova no lint (baseline vermelho).
- [ ] Sobre a saída gerada: `publish-check.sh` 0, `check-versions.py --base v1.5.17` 0, `gate.sh` da kb 0, `check-gerado.py` 0 e os 62 testes da raiz verdes.
- [ ] `SKILL.md` da `sdd-release` em ≤ 500 linhas; `check-versions.py --base v2.13.0` verde com 22 skills.
- [ ] **Tabela de paradas** em `evidence/F17B_STARTER_ETAPA2/PARADAS.md`: 4 skills (brainstorm, handoff, governança, release), starter `v1.5.17` × gerada; 0 parada nova sem OK do Roberto.
- [ ] **Teste do iniciante**: 3 execuções de cada (brainstorm, handoff, governança geradas) num agente em contexto novo, sem ferramentas, com pedido de aluno escrito antes; passa com 3 de 3 em cada: nenhum comando pedido ao aluno, documento no chat com o aviso de que nada foi gravado, nenhuma exigência de script ou Verify Gate. Logs em `evidence/`.
- [ ] Suíte do Open verde no Verify Gate; CI do PR verde nas 3 plataformas dentro dos tetos.
- [ ] Release do Open publicada; PR do starter com a 2ª geração, CI verde (10 checagens) e Release do starter, com OK próprio.

---

## Acceptance Tests

| ID | Padrão | Critério (EARS) | Gate (`kind`) |
|---|---|---|---|
| AT-001 | Event-driven | **When** o gerador roda com uma tag do Open e um clone do starter, ele **shall** gravar as 15 skills da lista (as 10 da F17 mais `sdd-brainstorm`, `sdd-handoff`, `sdd-governanca`, `sdd-release`, `ux-review-builder`) e, de `scripts/starter/raiz/`, também `docs/`, `exemplos/` e `tests/` (apagando ali o que saiu da semente); `skills/sdd-define/`, `skills/sdd-design/`, `skills/sdd-build/`, `LICENSE`, `NOTICE` e `CONTRIBUTING.md` **shall** ficar byte a byte iguais; o `README.md` gerado **shall** citar as 15 geradas e as 3 congeladas nos 2 idiomas | test |
| AT-002 | Ubiquitous | Para uma skill marcada como "de modo" (nesta frente, só a `sdd-release`), o `SKILL.md` gerado **shall** ser: frontmatter com `name` e `version` da skill do Open e a `description` e a `compatibility` do arquivo de modo; o cabeçalho `GENERATED`; o corpo de `references/MODO_INICIANTE.md`, com a linha de identificação (igual à do `SKILL.md` do Open) apontando o starter; o bloco "Quando migrar"; a skill gerada **shall** levar só os arquivos que o modo cita (com fechamento), mais `agents/openai.yaml` e `GERADO.txt`; nenhum arquivo do caminho pesado (`SKILL.md` do Open, outras `references/`) **shall** ir | test |
| AT-003 | Unwanted | **If** a skill de modo não tem o arquivo de modo, o modo cita arquivo que não existe na skill, ou o resultado cita caminho do `init`, **then** o gerador **shall** sair 65 com a causa e não gravar nada; aplicado à cópia crua da `sdd-release`, o lint **shall** reprovar (baseline vermelho) | test |
| AT-004 | Ubiquitous | O `MODO_INICIANTE.md` **shall** ter exatamente 1 ponto de aprovação (o OK antes de commit, merge ou push); **shall** usar só git e `gh` e nunca pedir, ler ou gravar token (nenhuma instrução de `vercel login`, `VERCEL_TOKEN`, `gh auth login` com token ou colar credencial); **shall** conferir o deploy da Vercel pelo status ou pelos checks do commit publicado (no PR, o check e o link de preview) e dizer a URL; **shall continue to** conferir pelo run do workflow quando o deploy é um workflow do Actions. **If** o check da Vercel falha ou não aparece, **then** **shall** dizer o que viu e onde olhar, sem refazer o deploy por conta própria. **Where** o projeto não tem `sdd/bin/`, a `sdd-release` do Open **shall** seguir o `MODO_INICIANTE.md` | test |
| AT-005 | Ubiquitous | A `sdd-brainstorm` do Open **shall** ter: sem acesso aos arquivos, entregar o documento no chat e dizer que nada foi gravado (nunca fingir que gravou); fato × inferência (fornecido, observado, inferido); não sobrescrever em silêncio um BRAINSTORM existente; YAGNI com zero cortes vale. A `sdd-handoff` **shall** ter: entrega no chat sem fingir que gravou; os modos "continuar" e "entregar"; pendências 🐛/✨ com "nenhuma" escrito quando não há. A `sdd-governanca` **shall** ter: prova por script só quando o DEFINE tem Verify Gate por comando (sem ele, prova manual); "onde entregar" (chat × arquivo); "quando não usar" | test |
| AT-006 | Unwanted | **If** a `sdd-brainstorm` ou a `sdd-handoff` geradas pedem ao aluno que rode um comando no caminho sem terminal (bloco de código de shell ou linha que manda rodar `bash`/`python3`), ou exigem linha de Verify Gate, **then** o teste **shall** reprovar; na `sdd-governanca` gerada, comando de prova só **shall** aparecer dentro do trecho condicionado ao Verify Gate por comando | test |
| AT-007 | Ubiquitous | O Open **shall** ter `.agents/skills/ux-review-builder/` 1.5.0 com a seção "Como falar com o aluno", `references/como-falar.md` e a linha de identificação, passando no `skill-lint.py --conversa`; as contagens dos testes **shall** ser 22 skills; a `sdd-ux-review` **shall** ler o `UX_STANDARD.md` do projeto quando ele existir | test |
| AT-008 | Event-driven | **When** a saída gerada sobre uma réplica do starter `v1.5.17` é conferida, `publish-check.sh`, `check-versions.py --base v1.5.17`, `skills/sdd-kb/scripts/gate.sh`, `check-gerado.py` e `python3 -B -m unittest discover -s tests` **shall** sair 0; um byte trocado num arquivo de `docs/`, `exemplos/` ou `tests/` gerado **shall** fazer o `check-gerado.py` sair 1 | test |
| AT-009 | Unwanted | **If** uma das 5 skills novas na lista tem versão menor ou igual à do starter (brainstorm 1.1.0, handoff 1.1.0, governança 1.0.1, release 1.3.0, ux-review-builder 1.4.0), **then** o gerador **shall** sair 65 antes de gravar (a regra da F17 vale para elas) | test |
| AT-010 | Non-regression | As 22 skills do Open **shall continue to** passar no `skill-lint.py --conversa`, no `test_agnostico.py` e no `check-versions.py`; o `SKILL.md` da `sdd-release` **shall continue to** ter ≤ 500 linhas e, com `sdd/bin/` presente, o caminho de hoje; o `init` **shall continue to** não copiar `scripts/starter/` | test |

While: N.A. (sem estado contínuo). Where: no AT-004 (projeto sem `sdd/bin/`).

Fora do gate, com evidência no BUILD_REPORT (critérios de aceite do Roberto, que bloqueiam a release): a tabela de
paradas com o OK dele, o teste do iniciante (3 de 3 por skill), a 2ª geração sobre o clone real do starter, o PR e a
Release do starter.

---

## Clarifications

### Session 2026-11-13

- [x] (escopo) Duas frentes: F17b = brainstorm, handoff, governança, release iniciante, ux-review-builder, `docs/`/`exemplos/`/`tests/`; F17c = define, design, build (brainstorm, perguntas 1 e 6).
- [x] (integrações) A release iniciante usa só git e `gh` e o login que já existe; nunca token (perfil de risco).
- [x] (restrições) Modo sem terminal por peso: leves no próprio texto; pesada em `references/MODO_INICIANTE.md` (brainstorm, pergunta 5).
- [x] (sinal de conclusão) A simplicidade é critério medido, com o OK do Roberto em cada parada nova (brainstorm, bloco 2).
- [x] (dados) Sem amostra do módulo 7: o comportamento do deploy da Vercel no GitHub é inferência da documentação pública, registrada assim no MODO_INICIANTE e no BUILD_REPORT.
- [x] (UX) Sem interface gráfica: UX review pulado. A experiência do aluno é medida pela tabela de paradas e pelo teste do iniciante.

### Session 2026-11-13 (governança)

- [x] (governança) N.A. — o revisor fresco leu o DEFINE: só gera e testa texto de skills, `docs/`/`exemplos/`/`tests/` e uma release GitHub + Vercel; nenhum dado da feature é valor, lançamento, documento fiscal, tributo, folha ou dado pessoal.

### Segurança

- [x] N.A. para a feature (texto de skills e gerador local, sem rede). O `MODO_INICIANTE.md` mantém a checagem que a release do starter `v1.5.17` já fazia (segredo no diff e no histórico da frente antes do push): não é parada nova.

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

Cobertura: AT-001 a AT-003, AT-008 e AT-009 no teste do gerador (repositório temporário com tag e réplica do starter
`v1.5.17`); AT-004 a AT-007 em testes de texto (sobre o Open e sobre a saída gerada); AT-010 nas suítes existentes.

---

## Out of Scope

- define, design e build em modo web (F17c).
- Outros hosts além da Vercel; deploy pela CLI da Vercel; revisão adversarial, ledger e curadoria no modo iniciante.
- O `docs/guia-do-aluno.pt-BR.md` do clone local do starter (trabalho do Roberto).
- Geração automática por workflow; qualquer trabalho da F15; o repositório privado.

## Constraints

- bash 3.2 e Python 3.9 stdlib; pulo de plataforma só por constante de `tests/apoio.py`.
- Nada da RDD nos dois repositórios; sem número de 11 dígitos no pacote; sem chave por extenso em log.
- `MANIFEST.txt` a cada arquivo novo; contagens fixadas mudam de 21 para 22 skills (e a de perguntas do `sdd-decisoes-lint`, se a skill nova tiver pergunta de decisão).
- O gerador só roda igual ao da tag; o starter pede OK próprio para push, PR e Release.

## Technical Context

| Aspect | Value | Notes |
|---|---|---|
| **Deployment Location** | `.agents/skills/{sdd-brainstorm,sdd-handoff,sdd-governanca,sdd-release,sdd-ux-review}/`, `.agents/skills/ux-review-builder/` (nova), `scripts/gerar-starter.py`, `scripts/starter/`, `tests/` | ferramenta de quem mantém; o `init` não copia `scripts/` |
| **KB Domains** | nenhum | o Open não tem `sdd/kb/`; a skill `sdd-kb` cria uma base quando o projeto quiser |
| **IaC Impact** | None | — |
| **LLM Prompts** | false | nenhum prompt de produção; `default_prompt` do `openai.yaml` é texto de botão |
| **CONTEXTO de domínio** | nenhum (pulado: o Open não tem `sdd/patterns/dominio.md`) | `contexto-lint.sh --sugerir` → PULAR |
| **Governança** | N.A. — gerador e texto de skills, `docs/`/`exemplos/`/`tests/` e release GitHub + Vercel; sem dinheiro, lançamento, nota fiscal, tributo, folha nem dado pessoal | revisor fresco, 2026-11-13 |
| **Segurança** | N.A. — sem login, rota pública, dado de terceiros, envio de arquivo, banco nem chamada paga na feature; a release iniciante usa só o login que o `gh` e o git já têm | 2026-11-13 |

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|---|---|---|---|
| A-001 | Com a integração GitHub–Vercel, o deploy aparece como status/check do commit e como deployment no GitHub, com link de preview no PR | a conferência do MODO_INICIANTE olha o lugar errado; o Design consulta a documentação e o texto diz o que é inferência | [ ] |
| A-002 | Brainstorm, handoff e governança do Open ficam sem citação ao `init` com os moldes para dentro e poucas trocas (≤ 10 por skill) | o gerador vira manutenção pesada; o Design mede antes | [ ] |
| A-003 | Um agente sem ferramentas segue o caminho sem terminal das skills geradas | o teste do iniciante reprova e o texto volta para ajuste | [ ] |

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---|---|---|
| Problem | 3 | versões e downloads medidos |
| Users | 3 | 4 papéis |
| Goals | 3 | MUST/SHOULD/COULD |
| Success | 3 | comandos, contagens e critério do teste do iniciante |
| Scope | 2 | dois repositórios, 6 skills e a regra nova do gerador |
| **Total** | **14/15** | |

## Open Questions

None - ready for Design.

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.1 | 2026-11-13 | design-agent | Revisão do DESIGN, nota 5: ordem do AT-002 (GENERATED depois do frontmatter; a identificação vem no corpo do modo) e a `compatibility` do modo |
| 1.0 | 2026-11-13 | define-agent | Initial version |

## Next Step

**Ready for:** `/sdd-design sdd/features/DEFINE_F17B_STARTER_ETAPA2.md` — UX review pulado: sem interface gráfica.
