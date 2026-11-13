# DEFINE: F17 — starter gerado a partir do Open

> Um gerador no Open (`scripts/`, ferramenta de quem mantém o pacote) produz, de uma tag publicada e sem rede, a cópia das
> 10 skills que funcionam sozinhas e a parte do sdd-starter que muda com elas (README, scripts e workflows), com
> cabeçalho `GENERATED`, soma de conferência e uma trava no CI do starter que recusa edição à mão. Antes da 1ª geração,
> o Open recebe o que o starter faz melhor nessas skills e conserta 2 defeitos achados na comparação.

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | F17_STARTER_GERADO |
| **Date** | 2026-11-12 |
| **Author** | define-agent (worktree `sdd-open-f17-starter-gerado`; branch `feat/f17-starter-gerado`, de `origin/main` `e22a1b2` = `v2.12.1`, mais o passo 0 em `aaf779c` e `13e1c2e`) |
| **Status** | Ready for Design |
| **Clarity Score** | 14/15 |
| **Entrada** | `sdd/features/BRAINSTORM_F17_STARTER_GERADO.md` (abordagem 1: trocas exatas fora da skill; caminho 1: em 2 etapas) |

---

## Problem Statement

O sdd-starter tem texto próprio em 16 skills que já divergiram do Open (ex.: `sdd-checar-ambiente` 1.2.0 no starter ×
1.5.1 no Open); todo ajuste é feito duas vezes ou se perde. O Roberto quer manter só o Open, e o starter tem de continuar
simples para o aluno iniciante, inclusive o da web.

## Target Users

| User | Pain Point |
|---|---|
| Roberto, mantenedor dos dois repositórios | ajusta duas cópias que já divergiram; esquece uma |
| Aluno do starter no terminal (Claude Code, Codex) | recebe skills de ambiente mais velhas que as do Open (sem `gh`, sem editor agnóstico, sem segurança) |
| Aluno do starter na web (claude.ai, ChatGPT) | precisa de skill que funcione sem scripts do `init`, com nome amigável e botão de prompt |
| Quem migra do starter para o Open | precisa saber quando migrar e não ter nada a converter |

---

## Goals

| Priority | Goal |
|---|---|
| **MUST** | gerador no Open: de uma tag publicada, sem rede, 10 skills geradas + README + `scripts/` + `.github/workflows/` do starter, com cabeçalho `GENERATED` e soma de conferência por arquivo |
| **MUST** | trocas exatas fora da skill (cada uma casa exatamente 1 vez); `agents/openai.yaml` por tabela única; lint final que reprova citação a arquivo do `init`; nada gravado quando algo falha |
| **MUST** | `check-gerado.py` gerado para o starter: recusa arquivo gerado editado, faltando ou a mais; rodado pelos 2 workflows |
| **MUST** | o Open recebe do starter: `sdd-new-session` (pré-voo à mão com a pasta sincronizada e os 4 casos; cópia para a frente das skills fora do git; 2 notas de "por quê"; 4 textos curtos), `sdd-prompt-builder` (drift conferido à mão sem o script), `sdd-auditoria-harness` (vários motores: `AGENTS.md`, `.agents/`, `.codex/`, `sdd/_index.md`, precedência `CLAUDE.md` × `AGENTS.md`) |
| **MUST** | consertos no Open: a `sdd-governanca` não cita mais `rdd-audita-schema`; o molde do brainstorm sem `pydantic`/`gcp`/`Terraform` |
| **MUST** | 1ª geração no clone do starter, numa branch, passando no `publish-check.sh`, no `check-versions.py` e no `gate.sh` da kb dele; PR e Release do starter com OK próprio do Roberto |
| **SHOULD** | aviso "quando migrar para o SDD Open" no fim de cada skill gerada; README do starter com a lista gerada × congelada até a F17b e o aviso da 1ª geração |
| **SHOULD** | cópias `~/.claude/skills/sdd-*` regeneradas pela tag publicada do Open (D6), com OK do Roberto na hora |
| **COULD** | lembrete da geração no roteiro de release do pacote (`CONTRIBUTING.md`) |

---

## Success Criteria

- [ ] `gerar-starter` sai 0 numa cópia do starter `v1.5.16` e grava as 10 skills; as 8 congeladas, `docs/`, `exemplos/`, `tests/`, `LICENSE`, `NOTICE` e `CONTRIBUTING.md` ficam byte a byte iguais.
- [ ] Duas gerações da mesma tag em pastas diferentes: saída idêntica byte a byte (`diff -r` vazio).
- [ ] A cópia crua de `.agents/skills/` reprova no lint do `init` (baseline vermelho); a gerada passa.
- [ ] Uma troca que não casa (0 ou 2 vezes) ou skill sem linha na tabela do `openai.yaml` ⇒ saída ≠ 0, nada gravado no destino.
- [ ] Sobre a saída gerada: `publish-check.sh` 0, `check-versions.py --base v1.5.16` 0, `gate.sh` da kb 0, `check-gerado.py` 0; um byte trocado num arquivo gerado ⇒ `check-gerado.py` 1 com o caminho.
- [ ] `collect_evidence.py` num repositório só com `.agents/skills/` acha as skills (hoje: 0 itens).
- [ ] `grep -rn 'rdd-audita' .agents sdd` vazio; o molde do brainstorm sem `pydantic`, `gcp`, `Terraform`.
- [ ] Suíte do Open verde no Verify Gate; CI do PR verde nas 3 plataformas, dentro dos tetos.
- [ ] Release do Open publicada; PR do starter com a 1ª geração, CI verde e Release do starter (com OK próprio).

---

## Acceptance Tests

| ID | Padrão | Critério (EARS) | Gate (`kind`) |
|---|---|---|---|
| AT-001 | Event-driven | **When** o gerador roda com uma tag publicada do Open e a pasta de um clone do starter, ele **shall** ler a árvore do Open **da tag** (nunca da árvore de trabalho), sem rede, e gravar no destino exatamente as 10 skills da lista (`sdd-checar-ambiente`, `sdd-iniciar-repo`, `sdd-higiene-dado`, `sdd-new-session`, `sdd-kb`, `sdd-seguranca`, `sdd-auditoria-harness`, `sdd-prompt-builder`, `sdd-engenharia-reversa-saas`, `sdd-loop-builder`), o `README.md`, o `.gitattributes`, o `GERADO.txt` da raiz, os arquivos de `scripts/` e de `.github/workflows/` do starter (apagando ali o que saiu da semente), e sair 0; tudo o mais no destino **shall** ficar byte a byte igual | test |
| AT-002 | Unwanted | **If** a tag não existe, o destino não tem a forma do starter (`skills/` e `scripts/check-versions.py`) ou o destino tem mudança não commitada, **then** o gerador **shall** sair 64 com a causa em uma linha e não gravar nada; **if** uma troca casa 0 ou mais de 1 vez, uma skill da lista não tem linha na tabela do `openai.yaml` ou o lint do `init` acha uma citação, ou uma skill gerada muda em relação ao destino sem versão maior que a dele, **then** **shall** sair 65 citando a troca, a skill ou o `arquivo:linha`, sem gravar nada no destino | test |
| AT-003 | Ubiquitous | Cada skill gerada **shall** ter: o frontmatter da skill do Open depois das trocas (`name`, `description` e `version` intactos); a linha de identificação apontando para `https://github.com/robertodiasduarte/sdd-starter/releases/latest`; logo depois do frontmatter, o cabeçalho `GENERATED` com a instrução "edite no sdd-open e gere de novo" (a tag e o commit do Open ficam só no `GERADO.txt` da raiz: com a tag em cada skill, toda geração mudaria as 10 e o version gate do starter pediria versão nova em todas); os arquivos que a skill do Open cita de `sdd/templates/` dentro dela, com o caminho reescrito; `agents/openai.yaml` com os 3 campos da tabela; no fim do `SKILL.md`, o bloco "Quando migrar para o SDD Open"; e o arquivo de conferência com o sha256 de cada arquivo da skill | test |
| AT-004 | Unwanted | **If** um arquivo gerado cita caminho que só o `init` do Open cria (`sdd/bin/`, `sdd/templates/`, `sdd/hooks/`, `sdd/review/`, `sdd/patterns/`, `sdd/playbook.md`, `sdd/invariants.md`, `sdd/WORKFLOW_CONTRACTS.yaml`, `bin/sdd-open.sh`, `.agents/skills/<nome>/` fora do par que define a pasta da skill ("`.claude/skills/x/` ou `.agents/skills/x/`"), `` `sync` `` ou "init do sdd-open"), **then** o lint **shall** reprovar com `arquivo:linha` (cada citação da linha conta; só não reprova a que está dentro do trecho de uma linha de `scripts/starter/lint-aceitos.tsv`, que leva o motivo; os caminhos se casam com a barra final); aplicado à cópia crua de `.agents/skills/` das 10, **shall** reprovar (baseline vermelho) | test |
| AT-005 | Ubiquitous | Duas gerações da mesma tag **shall** produzir saída idêntica byte a byte (ordem fixa, sem data nem caminho da máquina no conteúdo) | test |
| AT-006 | Event-driven | **When** `python3 scripts/check-gerado.py` roda na raiz do starter, ele **shall** conferir, para cada skill com arquivo de conferência, o sha256 de cada arquivo listado e sair 1 com o caminho quando um arquivo difere, falta ou existe na pasta sem estar na lista; os arquivos de `scripts/`, `.github/workflows/` e o `README.md` gerados **shall** ser conferidos do mesmo jeito; tudo igual ⇒ sai 0; os 2 workflows gerados **shall** rodá-lo antes dos testes | test |
| AT-007 | Event-driven | **When** a saída gerada sobre o starter `v1.5.16` é conferida, `publish-check.sh`, `check-versions.py --base v1.5.16` e `skills/sdd-kb/scripts/gate.sh` **shall** sair 0 (em teste do Open, com uma réplica mínima do starter montada em pasta temporária) | test |
| AT-008 | Ubiquitous | A `sdd-new-session` do Open **shall** ter o pré-voo à mão com a checagem de pasta sincronizada e os 4 casos (pasta pessoal, git numa subpasta, pasta vazia, sem git), a cópia para a frente das skills de `.claude/skills` e `.agents/skills` sem arquivo versionado com a conferência da `sdd-release`, as 2 notas de "por quê" e os 4 textos curtos; a `sdd-prompt-builder` **shall** ter a conferência do drift à mão quando `sdd/bin/prompt-drift-scan.sh` não existe; a `collect_evidence.py` da `sdd-auditoria-harness` **shall** inventariar `AGENTS.md`, `.agents/{skills,agents,scripts}` e `.codex/` (num repositório só com `.agents/skills/` acha as skills) e a skill **shall** avisar a precedência `CLAUDE.md` × `AGENTS.md` | test |
| AT-009 | Unwanted | **If** o pacote cita a skill `rdd-audita-schema` ou o molde do brainstorm traz `pydantic`, `gcp` ou `Terraform`, **then** o teste **shall** reprovar; a coluna pós-build da `sdd-governanca` **shall** apontar a prova por leitura do passo "Aplicar a migration" da `sdd-build` | test |
| AT-010 | Non-regression | As 21 skills do Open **shall continue to** passar no `skill-lint.py --conversa`, no `test_agnostico.py` e no `check-versions.py`; o `doctor` **shall continue to** avisar `agents/openai.yaml` de skill do starter no mesmo projeto; nenhum arquivo de `scripts/starter/` **shall** ser copiado pelo `init` para o projeto do aluno | test |

While: N.A. (o gerador não tem estado contínuo). Where: N.A. (sem variação por plataforma além do que o teste pula
por constante de `tests/apoio.py`).

Fora do gate, com evidência no BUILD_REPORT: a 1ª geração sobre o clone real do starter (log do gerador, do
`check-gerado.py` e dos 3 scripts do starter), o PR e a Release do starter, e a regeneração de `~/.claude/skills/sdd-*`.

---

## Clarifications

### Session 2026-11-12

- [x] (escopo) Caminho 1, em 2 etapas: 10 geradas agora; congeladas até a F17b (8): sdd-brainstorm, sdd-define, sdd-design, sdd-build, sdd-handoff, sdd-release, sdd-governanca, ux-review-builder (brainstorm, perguntas 3 e validação).
- [x] (integrações) Geração manual, sem rede, a partir de tag publicada; push, PR e Release no starter com OK próprio (brainstorm, pergunta 1).
- [x] (dados) `sdd/ambiente.md` não é gerado; a new-session gerada é a do Open (brainstorm, pergunta 2).
- [x] (UX) `agents/openai.yaml` pela tabela única no Open, com os textos atuais do starter como semente (pergunta 4). Sem interface gráfica: UX review pulado.
- [x] (restrições) Trocas exatas fora da skill, cada uma casando 1 vez; lint final (pergunta 5).
- [x] (escopo, decisão de rotina) O gerador é dono de **todo** `scripts/` e `.github/workflows/` do starter, não só do `check-gerado.py` e de 1 passo: assim o AT-007 roda no Open com os mesmos scripts que o starter roda, e o starter não fica com infra de texto próprio. Semente = os arquivos atuais do starter, mais o passo do `check-gerado.py`. Avisado ao Roberto no fecho do Define.
- [x] (sinal de conclusão) A 1ª geração sobre o clone real, o PR e a Release do starter e o D6 ficam fora do gate, com evidência.

### Session 2026-11-12 (governança)

- [x] (governança) N.A. — o revisor fresco leu o DEFINE: gerador que copia texto de skills e da infraestrutura do starter; nenhum dado de dinheiro, lançamento, nota, tributo, folha ou dado pessoal ("sem número de 11 dígitos" só impede um CPF no pacote).

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

Cobertura: AT-001 a AT-007 e AT-010 (parte do `init`) num teste novo do gerador, com um repositório git temporário
com tag e uma réplica mínima do starter; AT-008 e AT-009 em testes de texto e de `collect_evidence.py`; AT-010 nas
suítes existentes (`test_skill_lint`, `test_agnostico`, `test_sdd_open`).

---

## Out of Scope

- Modo web de brainstorm, handoff e governança; destino de define, design, build, release e ux-review-builder (F17b).
- `docs/` e `exemplos/` do starter; geração automática por workflow; cenário de branching A/B/C.
- Testes do Open copiados para dentro do starter.
- Qualquer trabalho da F15; qualquer coisa no repositório privado.

## Constraints

- bash 3.2 e Python 3.9 stdlib; teste pula plataforma só por constante de `tests/apoio.py`.
- Nada da RDD nos dois repositórios; sem número de 11 dígitos em arquivo do pacote; sem chave por extenso em log.
- `MANIFEST.txt` a cada arquivo novo; contagem de 21 skills não muda (o gerador não é skill).
- O starter é público e pede OK próprio do Roberto para push, PR e Release; nenhum remendo à mão nele.

## Technical Context

| Aspect | Value | Notes |
|---|---|---|
| **Deployment Location** | `scripts/` do Open (gerador, `scripts/starter/` com trocas, tabela e moldes da infra do starter), `.agents/skills/{sdd-new-session,sdd-prompt-builder,sdd-auditoria-harness,sdd-governanca}/`, `sdd/templates/BRAINSTORM_TEMPLATE.md`, `tests/` | ferramenta de quem mantém; o `init` não copia `scripts/` |
| **KB Domains** | nenhum | o Open não tem `sdd/kb/`; a skill `sdd-kb` cria uma base quando o projeto quiser |
| **IaC Impact** | None | — |
| **LLM Prompts** | false | nenhum prompt de produção; `default_prompt` do `openai.yaml` é texto de botão, não prompt de runtime do pacote |
| **CONTEXTO de domínio** | nenhum (pulado: o Open não tem `sdd/patterns/dominio.md`) | `contexto-lint.sh --sugerir` → PULAR |
| **Governança** | N.A. — gerador de texto de skills e da infraestrutura do starter; sem dinheiro, lançamento, nota fiscal, tributo, folha nem dado pessoal | revisor fresco, 2026-11-12 |
| **Segurança** | N.A. — sem login, rota pública, dado de terceiros, envio de arquivo, banco nem chamada paga: o gerador roda local, sem rede, e o starter é público por desenho | 2026-11-12 |

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|---|---|---|---|
| A-001 | Os textos do Open das 10 skills ficam autossuficientes com trocas exatas em número pequeno (dezenas, não centenas) | o gerador vira manutenção pesada; o Design mede antes | [ ] |
| A-002 | O `gate.sh` da kb do Open roda dentro de `skills/sdd-kb/` do starter | o CI do starter quebra; o Design confere caminhos | [ ] |
| A-003 | O starter aceita versões que pulam números (checar 1.2.0 → 1.5.1) | o version gate só exige maior: conferido no `check-versions.py` do starter | [x] |

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---|---|---|
| Problem | 3 | divergência medida skill a skill |
| Users | 3 | 4 papéis |
| Goals | 3 | MUST/SHOULD/COULD |
| Success | 3 | comandos e saídas nomeados |
| Scope | 2 | dois repositórios e 4 skills do Open numa sessão |
| **Total** | **14/15** | |

## Open Questions

None - ready for Design.

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.3 | 2026-11-12 | build | Avaliador, ciclo 2 (achados de letra): AT-001 lista `.gitattributes`, `GERADO.txt` e a limpeza; AT-003 frontmatter depois das trocas; AT-004 com os aceites e a barra |
| 1.2 | 2026-11-12 | build | Avaliador, ciclo 1, achado 1: AT-004 diz o recorte (o par que define a pasta fica; `sync` reprova) |
| 1.1 | 2026-11-12 | design-agent | Revisão do DESIGN, item 2: a tag sai do cabeçalho das skills (AT-003); AT-002 ganha o 65 da versão que não sobe contra o destino |
| 1.0 | 2026-11-12 | define-agent | Initial version |

## Next Step

**Ready for:** `/sdd-design sdd/features/DEFINE_F17_STARTER_GERADO.md` — UX review pulado: sem interface gráfica.
