# DEFINE: F21 — Engenharia reversa de SaaS antes do Brainstorm

> A skill `sdd-engenharia-reversa-saas` entra no SDD Open como 20ª skill (1.1.0): porte fiel do zip 1.0.0 com a camada de conversa, a regra de pasta, o exemplo neutro e os 18 testes do lint na suíte do pacote; uma linha opcional na tabela de fases, entre a KB e o Brainstorm.

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | F21_ENGENHARIA_REVERSA |
| **Date** | 2026-11-10 |
| **Author** | define-agent (worktree `sdd-open-f21-f19`, branch `feat/f21-engenharia-reversa`, base `45e27a9` = `v2.8.0`) |
| **Status** | Ready for Design |
| **Clarity Score** | 14/15 |

---

## Problem Statement

Quem quer construir algo parecido com um SaaS que já existe não tem, no SDD Open, uma etapa para estudar esse produto com evidência e limites antes do Brainstorm. A skill que faz isso existe só como zip avulso (1.0.0): fora do `skill-lint.py --conversa`, do `test_agnostico.py` e da suíte do pacote, citando pelo nome um produto real de terceiro e gravando em pasta que não é a do Open.

---

## Target Users

| User | Role | Pain Point |
|---|---|---|
| Aluno que usa o Open num agente de código | pede o estudo de um SaaS antes de abrir o Brainstorm | começa o Brainstorm copiando o concorrente de memória, sem separar o que viu, o que leu e o que supôs |
| Aluno do starter (chat na web) | baixa o zip da skill na Release do starter | a skill não está lá (etapa depois da release do Open) |
| Mantenedor do Open | publica o pacote | skill fora dos lints e da suíte muda sem ninguém ver; exemplo com produto real num repositório público |

---

## Goals

| Priority | Goal |
|---|---|
| **MUST** | `.agents/skills/sdd-engenharia-reversa-saas/` 1.1.0 no padrão das skills do Open, com o protocolo ER-SDD-001 preservado |
| **MUST** | os 18 testes do lint do levantamento em `tests/`, verdes no Python 3.9 e no atual |
| **MUST** | regra de pasta "segue o projeto" e exemplo neutro, com teste de texto |
| **MUST** | linha opcional na tabela de fases do `AGENTS.md.tmpl`, do `README.md` e do `README.pt-BR.md`, e ficha no guia do aluno; nenhuma fase renumerada |
| **MUST** | contagem de skills 19 → 20 nos testes e no `MANIFEST.txt`; `init` e `sync` levam a skill nova como as outras |
| **SHOULD** | 7 execuções de comportamento em contexto novo (1 positivo + 2 negativos 3 vezes cada) com log na evidência |
| **SHOULD** | depois da `v2.9.0`: a skill no starter, igual arquivo a arquivo (etapa fora do gate, OK próprio) |
| **COULD** | executar os outros 14 cenários (fica para depois) |

---

## Success Criteria

- [ ] `python3 sdd/bin/skill-lint.py --conversa .agents/skills/*/SKILL.md` sai 0 sobre as 20 skills; `tests/test_agnostico.py` verde.
- [ ] `tests/test_validate_reverse.py` roda 18 testes verdes no `unittest discover -s tests`, com `/usr/bin/python3` (3.9.6) e com o Python atual.
- [ ] Linha de base vermelha: em `45e27a9` os testes novos de texto e de contagem falham (a pasta da skill não existe; a contagem é 19).
- [ ] 0 ocorrências do nome do produto real de terceiro e do nome de vitrine "by RDD" nos arquivos da skill.
- [ ] `python3 scripts/check-versions.py --base v2.8.0` sai 0 com 20 skills; `manifest.json` e `evals/cases.json` com `"version": "1.1.0"`.
- [ ] 2 sabotagens derrubam, cada uma, um teste nomeado: trocar a regra de pasta no `SKILL.md`; quebrar uma checagem do `validate_reverse.py`. Log em `sdd/reports/evidence/F21_ENGENHARIA_REVERSA/`.
- [ ] Verify Gate numa cópia por `git archive` (sem `.git`) sai 0 com a suíte inteira (1.717 testes em `45e27a9`; a contagem só sobe).
- [ ] Comportamento (evidência por log, fora do gate): "entrar na conta de outro escritório" ⇒ recusa com o texto canônico em 3 de 3; instrução embutida em página ⇒ não obedecida em 3 de 3; controle positivo ⇒ levantamento que o `validate_reverse.py` aprova (exit 0).
- [ ] Release `v2.9.0` publicada com `SHA256SUMS.txt` conferido por `shasum -a 256 -c`.
- [ ] Depois da release (fora do gate): cada arquivo da skill no starter com o SHA-256 do arquivo na tag `v2.9.0`; `curl` no link do zip da Release do starter ⇒ 200.

---

## Acceptance Tests

| ID | Padrão | Critério (EARS) | Gate (`kind`) |
|---|---|---|---|
| AT-001 | Ubiquitous | O pacote **shall** conter `.agents/skills/sdd-engenharia-reversa-saas/` com `SKILL.md`, `CHANGELOG.md`, `manifest.json`, `evals/cases.json`, `assets/ENGENHARIA_REVERSA_TEMPLATE.md`, `scripts/validate_reverse.py` e, em `references/`, `PROTOCOLO_ENGENHARIA_REVERSA.md`, `ORQUESTRACAO_SDD.md`, `RUNTIME_COMPATIBILITY.md`, `COMO_FUNCIONA.md`, `FONTES.md`, `ESCOPO_CONFIRMADO.md` e `como-falar.md`; **shall not** conter `LICENSE.txt`, `VALIDACAO.md` nem `tests/`; o frontmatter **shall** ter `name` igual à pasta, `description` ≤ 1024, `compatibility`, `license: MIT` e `metadata` com `author`, `version: "1.1.0"` e `updated: "2026-11"`; `manifest.json` e `evals/cases.json` **shall** trazer a mesma versão; o `MANIFEST.txt` **shall** listar cada arquivo | test |
| AT-002 | Ubiquitous | O `SKILL.md` **shall** ter a linha de identificação `sdd-engenharia-reversa-saas v1.1.0 · nov/2026 · versão atual: …/releases/latest`, a seção `## Como falar com o aluno` com a tabela de etapas, as 5 partes da resposta, o bloco comum de regras das skills do pacote e o Status começando por `Engenharia reversa:`; `references/como-falar.md` **shall** existir, citar `sdd/templates/fragments/PERGUNTA_DECISAO.md` e passar no `skill-lint.py --conversa` (≥ 1 pergunta de decisão, 1 recomendada e primeira, **não sei**, nunca **Outro**, Próximo passo ≤ 100 caracteres) | test |
| AT-003 | Event-driven | **When** `python3 <skill>/scripts/validate_reverse.py <levantamento.md>` roda sobre um levantamento com as 14 seções na ordem, IDs `E`/`F` consistentes e as 7 dimensões cobertas, o script **shall** imprimir o JSON com `"ok": true` e sair 0, sem alterar o arquivo, a partir de qualquer pasta corrente, no Python ≥ 3.9 | test |
| AT-004 | Unwanted | **If** o levantamento tem achado `observado` sem evidência de `sessao_autorizada`, referência a evidência inexistente, fonte `indisponivel` sustentando achado, inferência sem suporte, ID duplicado, dimensão faltando, conclusão `concluida_no_escopo` com lacuna, marcador `{…}` do template sem preencher, tabela truncada ou seção obrigatória duplicada, ou o arquivo não existe, **then** o script **shall** sair diferente de 0 com o código do erro (ou falha segura, sem traceback, no arquivo ausente) | test |
| AT-005 | Optional feature | **Where** o projeto tem `sdd/config.yaml`, o texto da skill **shall** mandar gravar os três documentos em `sdd/features/`; sem `sdd/config.yaml`, em `sdd/` na raiz; `.claude/sdd/` **shall** aparecer só como a pasta a continuar quando ela já existe e não há `sdd/config.yaml`; a mesma regra **shall** estar no `SKILL.md` e em `references/ORQUESTRACAO_SDD.md`, sem a frase antiga "se `.claude/sdd/` já existir, continuar nela" | test |
| AT-006 | Unwanted | **If** algum arquivo da pasta da skill cita o nome do produto real de terceiro usado como exemplo na 1.0.0, o nome de vitrine "SDD Brainstorm by RDD" / "SDD Define by RDD", ou um termo de ferramenta de um agente só (lista de `tests/test_agnostico.py`), **then** a suíte **shall** falhar nomeando o arquivo e a linha; o exemplo **shall** ser "um sistema de BPO financeiro", e as dependências **shall** ser citadas como `sdd-brainstorm` e `sdd-define`, com ou sem prefixo de plugin | test |
| AT-007 | Ubiquitous | O `AGENTS.md.tmpl` **shall** ter, na tabela de fases, uma linha `ER` da `sdd-engenharia-reversa-saas` depois da linha `KB` e antes da linha `0`, marcada como opcional e citando `ENGENHARIA_REVERSA_{SAAS}.md`; `README.md` e `README.pt-BR.md` **shall** citar a skill na célula **Create/Criar**, depois de `sdd-kb` e antes de `sdd-brainstorm`, marcada opcional, ter uma linha própria na tabela de conceitos citando `ENGENHARIA_REVERSA_{SAAS}.md`, e dizer 20 skills onde diziam 19; `docs/pt-BR/guia-do-aluno.md` **shall** dizer 20 skills e ter a ficha `#### sdd-engenharia-reversa-saas` com "como pedir" e o limite em uma frase (fontes públicas e conta própria, sem copiar marca; sem pesquisa na web o levantamento sai parcial); `docs/cli-conventions.md` **shall** ter a linha do `validate_reverse.py` na tabela de exits (0 ok · 2 reprovado ou uso) com a exceção declarada (a saída é JSON, sem `RESULTADO:`) | test |
| AT-008 | Event-driven | **When** `bash bin/sdd-open.sh init --vendors claude --yes` roda num projeto novo, o projeto **shall** receber `.agents/skills/sdd-engenharia-reversa-saas/` inteira e a cópia gerada em `.claude/skills/sdd-engenharia-reversa-saas/`, e o `validate_reverse.py` da cópia gerada **shall** sair 0 sobre um levantamento válido; `sync --check` **shall** sair 0 logo depois | test |
| AT-009 | Non-regression | O pacote **shall continue to**: passar as 19 skills existentes no `skill-lint.py --conversa`; manter as linhas `Antes`, `KB`, `0`, `1`, `Gov`, `UX`, `2`, `3`, `4` da tabela de fases do `AGENTS.md.tmpl` com os mesmos rótulos e skills; manter verdes `tests/test_docs.py`, `tests/test_conversa.py`, `tests/test_agnostico.py`, `tests/test_decisoes_lint.py` e `tests/test_sdd_open.py`; e a `sdd-brainstorm` e a `sdd-define` **shall continue to** oferecer as âncoras que a skill nova usa: `sdd/templates/BRAINSTORM_TEMPLATE.md` e o mínimo de 3 perguntas na primeira; `sdd/templates/DEFINE_TEMPLATE.md`, "Mínimo 12/15", as 9 categorias de ambiguidade e o Verify Gate na segunda | test |
| AT-010 | Ubiquitous | `evals/cases.json` **shall** manter os 17 cenários `ER-01` a `ER-17`; `manifest.json` **shall** declarar quantos foram executados nesta frente e quantos seguem `escrito_nao_executado`, sem afirmar verificação que não rodou aqui (lint de outro pacote, validador de outra meta-skill), e `testes_escritos` **shall** apontar `tests/test_validate_reverse.py` | test |

Considerados: **While** — N.A.: a skill é texto e um lint sem estado; o estado do ciclo (`Estado e retomada`) é campo do documento, coberto por AT-004. **If/Then** em AT-004 (levantamento inválido) e AT-006 (texto proibido). **Where** em AT-005 (com e sem `sdd/config.yaml`). Não-regressão em AT-009, porque a frente mexe na tabela de fases e na contagem de skills, que já têm contrato.

O comportamento do modelo diante de um pedido de acesso indevido ou de instrução embutida não é AT: não é determinístico nem roda sem rede. Fica em Success Criteria, provado por log de execução real, e o texto que sustenta a recusa é conferido por AT-006/AT-010 (o texto canônico de recusa continua no `SKILL.md`).

---

## Clarifications

### Session 2026-11-10

- [x] (escopo) Starter agora ou pela F17? → logo após a `v2.9.0`, etapa separada com OK próprio; fora do Verify Gate (brainstorm, pergunta 1).
- [x] (dados) Pasta de saída → segue o projeto; integrado em AT-005.
- [x] (escopo) O que fica no pacote → padrão das skills do Open; integrado em AT-001.
- [x] (terminologia) Exemplo com produto real → neutro; integrado em AT-006.
- [x] (sinal de conclusão) Cenários de comportamento → 1 positivo + 2 negativos 3 vezes cada, por log; integrado em Success Criteria e AT-010.
- [x] (restrições) Igualdade Open ↔ starter → arquivo a arquivo, não o zip; no starter os testes ficam dentro da pasta.
- [x] (NFRs) Python → a 1.0.0 declara 3.10+; medido em 2026-11-10: os 18 testes passam no 3.9.6. A 1.1.0 declara Python ≥ 3.9, como o resto do pacote; integrado em AT-003.
- [x] (integrações) Fluxo encadeado → a skill não usa o `sdd-fluxo.sh seguir`; a transição para o Brainstorm é a do protocolo dela.
- [x] (UX) Sem interface: texto de skill, um lint e documentos. UX review pulado.
- [x] (revisão do DESIGN, 2026-11-10) 13 notas do revisor fresco; as que mudam o aceite entraram aqui (v1.1): AT-007 (os README não têm tabela de fases: célula Create/Criar e tabela de conceitos; 20 skills; linha em `docs/cli-conventions.md`) e AT-009 (âncoras de contrato no lugar do texto fixo de `v2.8.0`; que esta frente não editou as duas skills prova-se por `git diff --quiet v2.8.0 HEAD -- <as duas pastas>` no BUILD_REPORT). Ledger completo no DESIGN.

### Session 2026-11-10 (governança)

- [x] (governança) revisor fresco → N.A.: skill de texto e lint sem estado, sem tema de governança; fronteira "só o permitido mudou", bloco válido.

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

Cobertura: AT-003 e AT-004 em `tests/test_validate_reverse.py` (os 18 testes da 1.0.0, apontando para o script na pasta da skill); AT-001, AT-002, AT-005, AT-006, AT-007, AT-009 (âncoras das duas skills orquestradas) e AT-010 em `tests/test_f21_textos.py`; AT-002 também em `tests/test_skill_lint.py` (as 20 com `--conversa`), `tests/test_conversa.py` e `tests/test_decisoes_lint.py` (a marca de classe em cada pergunta de decisão); AT-007 também em `tests/test_docs.py`; AT-008 em `tests/test_f21_textos.py` com um projeto temporário; AT-009 pelo resto da suíte. A cópia por `git archive` não tem `.git`: o teste do `init` monta o próprio projeto temporário.

---

## Out of Scope

- Página `/sdd/` da plataforma (frente de outro repositório).
- F20, F16 e F17.
- Os 14 cenários de comportamento não escolhidos.
- Zip byte a byte idêntico entre Open e starter; gerador de zip no Open.
- Slot novo no `sdd/config.yaml`, hook ou `seguir` do fluxo encadeado para esta skill.
- Reescrever o protocolo no molde das skills de fase.
- Editar a `sdd-brainstorm` ou a `sdd-define`.

---

## Constraints

| Type | Constraint | Impact |
|---|---|---|
| Technical | bash 3.2 + Python ≥ 3.9, só biblioteca padrão; testes sem rede | o CI roda no 3.9.6 do macOS |
| Técnico | skill nova entra em todo teste que conta skills (19 → 20) e em `MANIFEST.txt` | `tests/test_skill_lint.py`, `tests/test_conversa.py`, `tests/test_docs.py` |
| Público | repositório público: nada de outro repositório; exemplo em domínio neutro | AT-006; `scripts/publish-gate.sh` |
| Contrato da skill | não renumera fase, não instala hook, não mexe em config | AT-009 |
| Segurança | o zip é dado: pasta própria fora do repositório, scripts de trabalho fora dela, `python3 -I` | vale no build |
| Processo | push, merge, tag e Release do Open autorizados ("sdd-open autorizado"); o starter pede OK próprio | etapa pós-release |
| Skills | skill tocada sobe `metadata.version` (`scripts/check-versions.py`) | `sdd-release` já em 2.9.1 na branch |

---

## Technical Context

| Aspect | Value | Notes |
|---|---|---|
| **Deployment Location** | `.agents/skills/sdd-engenharia-reversa-saas/` (nova), `tests/test_validate_reverse.py` e `tests/test_f21_textos.py` (novos), `tests/test_skill_lint.py`, `tests/test_conversa.py`, `tests/test_docs.py`, `tests/test_decisoes_lint.py`, `tests/test_matriz_new_session.py`, `AGENTS.md.tmpl`, `README.md`, `README.pt-BR.md`, `docs/pt-BR/guia-do-aluno.md`, `docs/cli-conventions.md`, `.gitattributes`, `MANIFEST.txt` | produto do Open; o `init` copia `.agents/skills/*` e o `sync` gera as cópias por agente |
| **KB Domains** | nenhum | o Open não tem `sdd/kb/`; a skill `sdd-kb` cria uma base quando o projeto quiser |
| **IaC Impact** | None | CI existente (`publish-gate.yml`, `release.yml`) |
| **LLM Prompts** | false | a skill é instrução de processo lida pelo agente, como as outras 19; nenhum prompt de runtime de aplicação é criado |
| **CONTEXTO de domínio** | nenhum (pulado: o Open não tem `sdd/patterns/dominio.md`) | `contexto-lint.sh --sugerir` → PULAR |
| **Governança** | N.A. — skill de texto e lint sem estado; sem dinheiro, saldo, lançamento, NF, tributo, folha nem dado pessoal | revisor fresco, 2026-11-10 |

---

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|---|---|---|---|
| A-001 | O `init` copia qualquer pasta de `.agents/skills/` sem lista fixa de nomes | a skill nova não chegaria ao projeto; AT-008 prova | [ ] (teste do AT-008) |
| A-002 | A marca que o `sync` põe nas cópias geradas não quebra o `validate_reverse.py` (comentário no topo de `.py`) nem o `manifest.json` (JSON não recebe marca) | a cópia do agente não rodaria; AT-008 prova | [ ] (teste do AT-008) |
| A-003 | Os 18 testes continuam válidos com o script em `.agents/skills/…/scripts/` e o teste em `tests/` | precisaria adaptar a importação; medido no build | [ ] |

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---|---|---|
| Problem | 3 | skill existe fora das convenções; 3 efeitos nomeados |
| Users | 3 | 3 papéis com a dor de cada um |
| Goals | 3 | MUST/SHOULD/COULD fechados no brainstorm |
| Success | 3 | contagens, exits, linha de base e 3 de 3 |
| Scope | 2 | o starter é etapa pós-release, fora do gate |
| **Total** | **14/15** | |

---

## Open Questions

None - ready for Design.

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | 2026-11-10 | define-agent | Initial version |
| 1.1 | 2026-11-10 | define-agent | notas da revisão fresca do DESIGN: AT-007 e AT-009 |
| 1.2 | 2026-11-10 | define-agent | avaliação ciclo 1 (A5): o comando do `skill-lint` no Success Criteria ganha os caminhos; sem mudança de aceite |

---

## Next Step

**Ready for:** `/sdd-design sdd/features/DEFINE_F21_ENGENHARIA_REVERSA.md` — UX review pulado: a feature não tem interface (texto de skill, um lint e documentos).
