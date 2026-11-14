# DEFINE: F17c — starter gerado, etapa 3

> As 3 últimas skills congeladas do starter (define, design, build) passam a ser geradas do Open, cada uma de um
> modo web que mora na skill do Open e nasce do texto congelado do starter `v1.5.18` (as paradas do aluno ficam
> iguais). O starter fica sem nenhuma congelada. O Open recebe 3 coisas que o starter faz melhor: o molde do relatório
> com as seções que a skill pede, moldes sem sobras de outro projeto e o "não finja" com a pergunta da 1ª vez do
> Verify Gate.

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | F17C_STARTER_ETAPA3 |
| **Date** | 2026-11-13 |
| **Author** | define-agent (worktree `sdd-open-f17c-starter-etapa3`; branch `feat/f17c-starter-etapa3`, de `origin/main` `e583889` = `v2.14.0`, mais o passo 0 em `53bba4a`) |
| **Status** | Ready for Design |
| **Clarity Score** | 14/15 |
| **Entrada** | `sdd/features/BRAINSTORM_F17C_STARTER_ETAPA3.md` (abordagem W1, skill de modo com o texto do starter) |

---

## Problem Statement

`sdd-define` 1.2.0, `sdd-design` 1.1.0 e `sdd-build` 1.2.0 do starter — as mais baixadas, ~30 por onda de alunos — são
texto próprio, congelado, que diverge do Open (2.6.1, 2.6.0, 2.9.1), grava em `sdd/` sem subpastas (ou `.claude/sdd/`)
enquanto as outras 15 skills geradas usam as pastas do Open, e traz validadores Python que o aluno da web não roda e 4
defeitos próprios (handoff do protocolo do define e do build, `sdd.config.yaml`, `- banco:` em `sdd/ambiente.md`). O
texto do Open tem ~48 paradas que o iniciante não tem hoje; gerar a partir dele deixaria o caminho do iniciante mais
difícil. No sentido inverso, o Open não tem o que o starter faz melhor: o molde do BUILD_REPORT não tem as seções
"Seleção de modo" e "Drift detectado" que a `sdd-build` exige, os moldes trazem restos de outro projeto, e define,
design e build não dizem "sem acesso, não finja".

## Target Users

| User | Pain Point |
|---|---|
| Roberto, mantenedor dos dois repositórios | 3 skills mantidas em dobro; o README do starter explica uma exceção de pastas |
| Aluno iniciante na web (claude.ai, ChatGPT) | precisa de define e design que entreguem no chat, sem script, com as paradas de hoje |
| Aluno com agente que escreve no projeto, sem o `init` do Open | precisa de um build que prove o gate lendo o comando, sem o `verify-gate.sh` |
| Quem usa o Open | relatório sem as seções que a skill pede; moldes com Terraform, GCP e pytest; nenhuma regra contra fingir |

---

## Goals

| Priority | Goal |
|---|---|
| **MUST** | define, design e build do Open com um modo web (o texto do starter `v1.5.18`, mudado só no necessário), apontado por 1 linha do `SKILL.md` de cada uma; o gerador monta a skill do starter só do modo |
| **MUST** | as 3 na `lista.txt` (18 geradas, nenhuma congelada); pastas do Open; prova sem script (validadores e seus testes não vão) |
| **MUST** | simplicidade do iniciante medida: tabela de paradas com OK do Roberto em cada parada nova; teste do iniciante 3 de 3 por skill |
| **MUST** | no Open: molde do BUILD_REPORT com "Seleção de modo" e "Drift detectado"; moldes de DEFINE, DESIGN e BUILD_REPORT sem sobras de outro projeto; "não finja" nas 3 e a pergunta da 1ª vez do Verify Gate no define |
| **MUST** | 3ª geração pela tag num clone limpo do starter, com as 9 checagens verdes; PR e Release do starter com OK próprio do Roberto |
| **SHOULD** | README, quickstart e workflow do starter (PT e EN) e o README do `exemplos/baixar-nfse` coerentes com as 18 geradas |
| **COULD** | `~/.claude/skills/sdd-*` regeneradas pela tag publicada (D6), com OK do Roberto na hora |

---

## Success Criteria

- [ ] O gerador sai 0 sobre uma réplica do starter `v1.5.18` e grava as 18 skills; nenhuma pasta de `skills/` fica sem `GERADO.txt`.
- [ ] As 3 geradas não trazem nenhum arquivo do caminho do Open nem `scripts/`/`tests/`; a cópia crua de cada uma reprova no lint (baseline vermelho).
- [ ] Sobre a saída gerada: `publish-check.sh` 0, `check-versions.py --base v1.5.18` 0, `gate.sh` da kb 0, `check-gerado.py` 0 e os testes da raiz verdes.
- [ ] `check-versions.py --base v2.14.0` verde com 22 skills; contagens fixadas atualizadas.
- [ ] **Tabela de paradas** em `evidence/F17C_STARTER_ETAPA3/PARADAS.md`: 3 skills, starter `v1.5.18` × gerada; 0 parada nova sem OK do Roberto.
- [ ] **Teste do iniciante**: 3 execuções de cada uma das 3 geradas, num agente em contexto novo sem ferramentas (`claude -p --tools ""`, pasta vazia, sem MCP), em várias voltas, com roteiro e critério escritos antes; passa com 3 de 3 em cada. Define e design: documento entregue no chat sem afirmar que gravou, nenhum comando pedido ao aluno, nenhum script exigido. Build: sem o projeto, não finge (nenhum arquivo dito escrito, nenhum teste dito rodado, nenhuma pasta dita gravável), diz que precisa do projeto acessível e **recomenda** abrir num agente que grave arquivos e não pede comando ao aluno; se o aluno diz que só tem o chat (ou pede), o caminho do chat vale, desde que nunca tome "ok" ou resposta vaga como escolha e não marque tarefa feita nem afirme conferência sem o relato dele; todas as voltas do roteiro são julgadas, e o veredito é de um leitor em contexto novo pelo critério em prosa (o juiz por expressão regular só faz triagem). Pergunta sem entrega no fim do roteiro reprova. Logs em `evidence/`. **Ambiente do build (decisões do Roberto, 2026-11-14):** o `claude -p` anuncia ao modelo uma pasta gravável, então o build roda pela API de chat da OpenRouter (`anthropic/claude-opus-5.5`, sem pasta nem ferramenta); define e design ficam no `claude -p`.
- [ ] Suíte do Open verde no Verify Gate; CI do PR verde nas 3 plataformas dentro dos tetos.
- [ ] Release do Open publicada; PR do starter com a 3ª geração, CI verde e Release do starter, com OK próprio.

---

## Acceptance Tests

| ID | Padrão | Critério (EARS) | Gate (`kind`) |
|---|---|---|---|
| AT-001 | Event-driven | **When** o gerador roda com uma tag do Open e um clone do starter, ele **shall** gravar as 18 skills da lista (as 15 da F17b mais `sdd-define`, `sdd-design`, `sdd-build`), cada uma com `GERADO.txt`; `LICENSE`, `NOTICE` e `CONTRIBUTING.md` **shall** ficar byte a byte iguais; o `README.md` e o quickstart gerados **shall** citar as 18 geradas, nenhuma congelada, nos 2 idiomas, sem citar os validadores `validate_define.py`, `validate_design.py`, `validate_build_report.py`; o README de `exemplos/baixar-nfse` **shall** apontar `sdd/features/` e `sdd/reports/` e não citar validador | test |
| AT-002 | Ubiquitous | Para `sdd-define`, `sdd-design` e `sdd-build`, o `SKILL.md` gerado **shall** ser o frontmatter (`name` e `version` da skill do Open; `description` e `compatibility` do modo), o cabeçalho `GENERATED`, o corpo do modo web com a linha de identificação igual à do `SKILL.md` do Open apontando o starter, e o bloco "Quando migrar"; a skill gerada **shall** levar só os arquivos que o modo cita (com fechamento), entre eles `references/como-falar.md`, mais `agents/openai.yaml` e `GERADO.txt`; nenhum arquivo do caminho do Open (o `SKILL.md` dele, `references/cartografo.md`, `references/modos-e-retry.md`, `references/contexto-fresco.md`, o `references/aplicar-migration.md` do Open) e nenhum `scripts/` ou `tests/` **shall** ir | test |
| AT-003 | Unwanted | **If** uma skill de modo não tem o arquivo de modo, o modo cita arquivo que não existe na pasta do modo, ou o resultado cita caminho do `init`, **then** o gerador **shall** sair 65 com a causa e não gravar nada; aplicado à cópia crua de `sdd-define`, `sdd-design` e `sdd-build` do Open, o lint **shall** reprovar (baseline vermelho) | test |
| AT-004 | Ubiquitous | Os 3 modos web **shall** gravar o DEFINE e o DESIGN em `sdd/features/` e o BUILD_REPORT em `sdd/reports/` (nunca em `sdd/` sem subpasta nem em `.claude/sdd/`); sem acesso aos arquivos, **shall** entregar o documento no chat sem dizer que gravou; **shall** fechar o DEFINE com o próximo passo no Design, e o BUILD_REPORT completo com o próximo passo no handoff, sem `HANDOFF_TO_UX_REVIEW` nem `HANDOFF_TO_RELEASE` contraditórios; **shall not** citar `sdd.config.yaml` nem gravar `- banco:` em `sdd/ambiente.md` (o registro da migration é só a seção `## Migrations aplicadas` do BUILD_REPORT) | test |
| AT-005 | Unwanted | **If** o define ou o design gerados pedem ao aluno que rode um comando (bloco de código de shell, ou linha que manda rodar `bash`/`python`/`python3`), ou qualquer das 3 geradas cita `validate_define.py`, `validate_design.py` ou `validate_build_report.py` como passo, **then** o teste **shall** reprovar; o build gerado **shall** conferir o Verify Gate lendo a saída do comando (`exit 0` verde, qualquer outro vermelho; a ferramenta que não rodou é inconclusiva), sem o `verify-gate.sh` | test |
| AT-006 | Ubiquitous | No Open, o `sdd/templates/BUILD_REPORT_TEMPLATE.md` **shall** ter as seções que a `sdd-build` exige, inclusive "Seleção de modo" (sinais, recomendação, decisão do usuário) e "Drift detectado"; os moldes `DEFINE_TEMPLATE.md`, `DESIGN_TEMPLATE.md` e `BUILD_REPORT_TEMPLATE.md` **shall not** trazer Terraform, Terragrunt, GCP, Cloud Run, Cloud Logging, Pydantic, `ruff`, `mypy`, `pytest` como ferramenta fixa, `src/ \| functions/ \| gen/ \| deploy/`, `/build`, `/release` nem `/iterate` | test |
| AT-007 | Ubiquitous | No Open, `sdd-define`, `sdd-design` e `sdd-build` **shall** dizer que, sem acesso ao código ou ao projeto, o agente não afirma ter inspecionado, escrito ou rodado nada e não inventa caminho (no design, pergunta a stack e a estrutura mínima antes do File Manifest); o `sdd-define` **shall** perguntar na 1ª vez, sem comando conhecido, "existe um comando que devolve 0 quando funciona?" e, sem comando, usar `manual-ux` com 3 a 5 frases "Eu abri … e vi …"; **shall not** escolher `manual-ux` sem fazer a pergunta, salvo na UX pura (aparência, que nenhum comando julga), que vai direto a `manual-ux` | test |
| AT-008 | Event-driven | **When** a saída gerada sobre uma réplica do starter `v1.5.18` é conferida, `publish-check.sh`, `check-versions.py --base v1.5.18`, `skills/sdd-kb/scripts/gate.sh`, `check-gerado.py` e `python3 -B -m unittest discover -s tests` **shall** sair 0; um byte trocado num arquivo de `skills/sdd-build/` gerado **shall** fazer o `check-gerado.py` sair 1 | test |
| AT-009 | Unwanted | **If** `sdd-define`, `sdd-design` ou `sdd-build` têm versão menor ou igual à do starter (1.2.0, 1.1.0, 1.2.0), **then** o gerador **shall** sair 65 antes de gravar | test |
| AT-010 | Non-regression | As 22 skills do Open **shall continue to** passar no `skill-lint.py --conversa`, no `test_agnostico.py`, no `check-versions.py` e no `sdd-decisoes-lint.sh`; com `sdd/bin/` presente, `sdd-define`, `sdd-design` e `sdd-build` **shall continue to** seguir o caminho de hoje (a linha do modo web é condicionada); as 15 skills geradas na F17b **shall continue to** sair iguais, salvo as que levam um molde mudado e a `ux-review-builder` e a `sdd-engenharia-reversa-saas`, que passam às pastas do Open (decisão do Roberto, revisão do DESIGN), sempre com versão nova; o `init` **shall continue to** não copiar `scripts/starter/` | test |

While: N.A. (sem estado contínuo). Where: no AT-010 (com `sdd/bin/` presente) e na linha do modo web (projeto sem
`sdd/bin/` ou sem acesso aos arquivos).

Fora do gate, com evidência no BUILD_REPORT (critérios de aceite do Roberto, que bloqueiam a release): a tabela de
paradas com o OK dele, o teste do iniciante (3 de 3 por skill), a 3ª geração sobre o clone real do starter, o PR e a
Release do starter.

---

## Clarifications

### Session 2026-11-13

- [x] (escopo) O modo web das 3 nasce do texto congelado do starter `v1.5.18`, não do recorte do Open (brainstorm, pergunta 1).
- [x] (escopo) No Open entram o defeito do molde do relatório, os moldes sem sobras e "não finja" + pergunta da 1ª vez; o desvio geral do build fica fora (pergunta 2).
- [x] (restrições) Pastas do Open nas 3 geradas (pergunta 3); o exemplo `baixar-nfse` fica, com o README atualizado (pergunta 4).
- [x] (sinal de conclusão) Simplicidade medida como na F17b; para o build, a "entrega" sem o projeto é a parada honesta (não fingir e pedir o projeto), registrada no critério do teste do iniciante antes de rodar.
- [x] (dados) A amostra é o texto congelado da `v1.5.18` e o exemplo `baixar-nfse`; nada da RDD.
- [x] (UX) Sem interface gráfica: UX review pulado. A experiência do aluno é medida pela tabela de paradas e pelo teste do iniciante.

### Session 2026-11-13 (governança)

- [x] (governança) N.A. — revisor em contexto novo, 2026-11-13: ver a linha Governança do Technical Context.

### Segurança

- [x] N.A. para a feature (texto de skills e gerador local, sem rede). O build gerado mantém a confirmação do projeto antes de aplicar migration (nome e ref) e a prova por leitura, que a `v1.5.18` já tinha: não é parada nova.

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
`v1.5.18`); AT-004 a AT-007 em testes de texto (sobre o Open e sobre a saída gerada); AT-010 nas suítes existentes.

---

## Out of Scope

- O desvio geral (6 perguntas) no build do Open; segurança e governança com trava no define e no design web.
- Validadores Python no zip do aluno; unificar o texto do Open e o do modo web.
- O `docs/guia-do-aluno.pt-BR.md` do clone local do starter (trabalho do Roberto).
- Geração automática por workflow; qualquer trabalho da F15; o repositório privado.

## Constraints

- bash 3.2 e Python 3.9 stdlib; pulo de plataforma só por constante de `tests/apoio.py`.
- Nada da RDD nos dois repositórios; sem número de 11 dígitos no pacote; CPF ou CNPJ de exemplo passa pelo `publish-gate` do Open.
- `MANIFEST.txt` a cada arquivo novo; contagens fixadas (22 skills; perguntas do `sdd-decisoes-lint`; versões em `test_f*_textos`).
- O gerador só roda igual ao da tag; o starter pede OK próprio para push, PR e merge.

## Technical Context

| Aspect | Value | Notes |
|---|---|---|
| **Deployment Location** | `.agents/skills/{sdd-define,sdd-design,sdd-build}/` (o modo web e a linha no `SKILL.md`), `sdd/templates/{DEFINE,DESIGN,BUILD_REPORT}_TEMPLATE.md`, `scripts/gerar-starter.py`, `scripts/starter/`, `tests/` | ferramenta de quem mantém; o `init` não copia `scripts/` |
| **KB Domains** | nenhum | o Open não tem `sdd/kb/` |
| **IaC Impact** | None | — |
| **LLM Prompts** | false | nenhum prompt de produção; `default_prompt` do `openai.yaml` é texto de botão |
| **CONTEXTO de domínio** | nenhum (pulado: o Open não tem `sdd/patterns/dominio.md`) | — |
| **Governança** | N.A. — a feature gera texto de skills, moldes e docs/exemplos do starter; o exemplo baixar-nfse e o CPF de exemplo do texto congelado são material didático já publicado (este coberto pelo publish-gate), não dado tratado pela feature: nenhum valor, lançamento, documento fiscal, tributo, folha ou dado pessoal | revisor em contexto novo, 2026-11-13 |
| **Segurança** | N.A. — sem login, rota pública, dado de terceiros, envio de arquivo, banco nem chamada paga na feature | 2026-11-13 |

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|---|---|---|---|
| A-001 | O texto congelado das 3 passa no `publish-gate` do Open (o exemplo de DEFINE do starter usa CPF) | troca do número por um de exemplo, sem mudar parada; o Design confere | [ ] |
| A-002 | Os arquivos do modo web cabem numa pasta própria da skill do Open sem quebrar o `skill-lint`, o `test_agnostico` e o `sdd-decisoes-lint` do Open | ajuste de texto ou de escopo dos lints; o Design mede antes | [ ] |
| A-003 | Um agente sem ferramentas segue o modo web gerado (entrega no chat; o build não finge) | o teste do iniciante reprova e o texto volta para ajuste | [ ] |

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---|---|---|
| Problem | 3 | versões, downloads, paradas e defeitos medidos |
| Users | 3 | 4 papéis |
| Goals | 3 | MUST/SHOULD/COULD |
| Success | 3 | comandos, contagens e critério do teste do iniciante |
| Scope | 2 | dois repositórios, 3 skills, 3 moldes e a pasta-base do modo no gerador |
| **Total** | **14/15** | |

## Open Questions

None - ready for Design.

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.3 | 2026-11-14 | build-agent | Avaliador, ciclo 3 (decisões do Roberto): "só tenho o chat" abre o caminho do chat com regras; o veredito do teste do iniciante do build é de um leitor em contexto novo |
| 1.2 | 2026-11-14 | build-agent | Avaliador, ciclo 2 (decisões do Roberto): AT-007 isenta a UX pura da pergunta da 1ª vez; o critério do build web pede que ele recomende um agente que grave, e o teste do build roda pela OpenRouter, julgando todas as voltas |
| 1.1 | 2026-11-13 | design-agent | AT-010: a `ux-review-builder` e a `sdd-engenharia-reversa-saas` passam às pastas do Open (decisão do Roberto, revisão do DESIGN, nota 4) |
| 1.0 | 2026-11-13 | define-agent | Initial version |

## Next Step

**Ready for:** `/sdd-design sdd/features/DEFINE_F17C_STARTER_ETAPA3.md` — UX review pulado: sem interface gráfica.
