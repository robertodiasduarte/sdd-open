# BRAINSTORM: F17 Starter gerado a partir do Open

> Sessão de exploração antes do Define. Frente F17 do programa INCORPORAR_STARTER (Decisão 5, parâmetro P3).

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | F17_STARTER_GERADO |
| **Date** | 2026-11-12 |
| **Author** | brainstorm-agent (Claude), decisões do Roberto |
| **Status** | Ready for Define |

---

## Initial Idea

**Raw Input:** "O sdd-starter deixa de ter texto próprio: cada skill dele é gerada de `.agents/skills/` do Open. O
starter continua sendo a porta de quem usa claude.ai ou ChatGPT na web, sem terminal." (plano, seção F17). Objetivo
dito pelo Roberto no brainstorm: **fazer manutenção num repositório só**; o starter tem de ser **mais simples para o
aluno iniciante**.

**Context Gathered:**
- Starter publicado: `v1.5.16` = `origin/main` `a82c972`, 16 skills. Desde a avaliação de 29/10 (`17c69c4`) só mudaram
  o kit `exemplos/baixar-nfse` e a skill da F21 (cópia do Open).
- Open: `v2.12.1` + passo 0 desta frente (`aaf779c`, `13e1c2e`), 21 skills. Só no starter: `ux-review-builder`. Só no
  Open: `sdd-drive`, `sdd-iterate`, `sdd-loop-builder`, `sdd-playbook`, `sdd-seguranca`, `sdd-ux-review`.
- O `init` cria `sdd/{templates,bin,hooks,review,patterns}/`, `sdd/playbook.md`, `sdd/invariants.md`,
  `sdd/WORKFLOW_CONTRACTS.yaml`, `sdd/config.yaml`, `AGENTS.md` e os adaptadores. Contagem de citações por skill (passo
  de medição): define 21, design 13, build 24, release 38 citações a `sdd/bin/`; iniciar-repo 0; checar-ambiente,
  auditoria-harness, loop-builder só o fragmento `PERGUNTA_DECISAO.md`.
- Publicação do starter: `auto-release.yml` no push da `main` que toca `skills/**` (testes de `skills/*/tests`,
  `publish-check.sh`, `check-versions.py --base-obrigatoria`, `gate.sh` da kb, zips + `SHA256SUMS.txt`). O
  `check-versions.py` do starter exige a linha de identificação com `sdd-starter/releases/latest` e `description` ≤ 1.024
  caracteres (o upload do claude.ai e do ChatGPT recusa acima). Maior `description` do Open: 956 (iniciar-repo).
- Comparação skill a skill (2 agentes em contexto novo, só leitura): `evidence/F17_STARTER_GERADO/COMPARACAO-terreno.md`
  e `COMPARACAO-fases-e-apoio.md`. Dois achados do Open conferidos no código: a `sdd-governanca` cita a skill
  `rdd-audita-schema`, que não existe no pacote (3 lugares); a `collect_evidence.py` da `sdd-auditoria-harness` só olha
  `.claude/` e não enxerga `.agents/skills/`, onde o próprio Open guarda as skills.

**Technical Context Observed (for Define):**

| Aspect | Observation | Implication |
|--------|-------------|-------------|
| Likely Location | `scripts/gerar-starter.sh` + `scripts/starter/` no Open (ferramenta de quem mantém; o `init` não copia `scripts/`) | não vai para o projeto do aluno do Open |
| Relevant KB Domains | nenhum | — |
| IaC Patterns | N/A | — |

---

## Discovery Questions & Answers

| # | Question | Answer | Impact |
|---|----------|--------|--------|
| 1 | Como a cópia chega ao starter: manual ou automática? | **Manual** (comando do Open, sem rede, a partir de tag publicada) | sem token com escrita no starter; lembrete no roteiro de release do pacote |
| 2 | O `sdd/ambiente.md` do starter × os slots do `sdd/config.yaml`? | **Igual ao Open**: sem config, a new-session descobre de novo e não grava; um `sdd/ambiente.md` antigo é lido como evidência | migração para o Open sem conversão |
| 3 | Quais skills o starter recebe por geração? | Roberto pediu avaliação com a meta "manutenção num só repositório"; escolheu o **caminho 1, em 2 etapas** | ver Selected Approach |
| 4 | `agents/openai.yaml` nas geradas? | **Tabela única no Open** (semente: os textos atuais do starter) | aluno mantém nome amigável e botão de prompt; manutenção no Open |
| 5 | Como o texto do Open vira texto do starter? | **Trocas exatas guardadas fora da skill** + regras mecânicas + lint final | skills do Open ficam limpas; o gerador para quando o Open muda um trecho trocado |

---

## Perfil de risco

| Pergunta | Resposta |
|---|---|
| Quem pode ver? | qualquer um: o starter é público; o gerador roda na máquina do Roberto, sem rede e sem dado pessoal; nada da RDD entra (confirmado pelo Roberto) |
| Quem pode mudar? | só o Roberto: push, PR e Release no starter com OK próprio a cada um; no Open, "sdd-open autorizado" |
| Quanto alguém pode pedir? | nada: sem serviço, login, upload ou chamada paga |

---

## Sample Data Inventory

| Type | Location | Count | Notes |
|------|----------|-------|-------|
| Input files | `.agents/skills/` do Open (tag publicada) | 10 skills geradas | fonte da geração |
| Output examples | starter `v1.5.16` (`git archive` em pasta própria) | 16 skills | forma esperada: `skills/<nome>/`, `agents/openai.yaml`, linha de identificação do starter |
| Ground truth | `scripts/check-versions.py` e `publish-check.sh` do starter | 2 | a saída gerada tem de passar nos dois |
| Related code | `bin/sdd-open.sh` (`sync` gera cópias com cabeçalho), `sdd/bin/lib/python.sh` | — | padrão de cópia gerada e do Python |

---

## Approaches Explored

### Abordagem 1: trocas exatas fora da skill + regras mecânicas + lint final ⭐ Recomendada (escolhida)

**Description:** ao lado do gerador, uma lista de trocas "trecho → trecho", cada uma tem de casar exatamente 1 vez; regras
mecânicas levam para dentro da skill os fragmentos e moldes citados, trocam a linha de identificação para o starter,
põem o cabeçalho `GENERATED` e escrevem `agents/openai.yaml` pela tabela; no fim, um lint reprova citação a arquivo do `init`.

**Pros:** as skills do Open não carregam texto do starter; falha alto quando o Open muda um trecho trocado; nada duplicado.

**Cons:** mudança de texto no Open num trecho trocado pede ajustar a troca (o gerador avisa).

### Abordagem 2: blocos marcados dentro das skills do Open

**Pros:** tudo num arquivo. **Cons:** o agente que usa o Open lê também as instruções do starter (comentário HTML aparece
no texto cru) e pode se confundir.

### Abordagem 3: cópias inteiras das versões do starter guardadas no Open

**Cons:** texto duplicado de novo, noutro lugar: o que a Decisão 5 quer acabar.

### Caminhos de escopo (pergunta 3)

- **1. Em 2 etapas (escolhido):** agora o gerador, a trava e 10 skills que funcionam sozinhas; as 8 restantes congeladas e
  marcadas até a F17b, que decide com dado.
- 2. Treze agora e o resto retirado: um repositório já, mas quem usa a web perde Define → Build no starter.
- 3. Tudo gerado com modo sem script dentro do Open: 2 procedimentos por skill pesada no Open, várias sessões.

---

## Selected Approach

| Attribute | Value |
|-----------|-------|
| **Chosen** | Abordagem 1 (trocas exatas fora) + caminho 1 (em 2 etapas) |
| **User Confirmation** | 2026-11-12, Roberto, por pergunta e confirmação de 2 blocos |
| **Reasoning** | chega à manutenção num repositório só sem decidir às cegas o destino das 4 skills pesadas; mantém o starter simples para o iniciante |

---

## Key Decisions Made

| # | Decision | Rationale | Alternative Rejected |
|---|----------|-----------|----------------------|
| 1 | Regra: nenhuma skill do starter com texto próprio — gerada ou retirada (as 8 congeladas só até a F17b) | manutenção num repositório só | skill congelada para sempre (vira 2º repositório) |
| 2 | Geradas: sdd-checar-ambiente, sdd-iniciar-repo, sdd-higiene-dado, sdd-new-session, sdd-kb, sdd-seguranca, sdd-auditoria-harness, sdd-prompt-builder, sdd-engenharia-reversa-saas, sdd-loop-builder | funcionam sem script do `init` depois de levar os fragmentos para dentro | 13 agora; só 6 |
| 3 | Congeladas até a F17b (8): sdd-brainstorm, sdd-define, sdd-design, sdd-build, sdd-handoff, sdd-release, sdd-governanca, ux-review-builder. Na validação eu disse "7" e esqueci a governança; ela já estava no caminho 1 (F17b) | dependem de script do `init` ou pedem modo web no Open | retirar já |
| 4 | Antes de gerar, o Open recebe do starter: new-session C1–C4, prompt-builder C1 (drift à mão), auditoria-harness C1–C3 (vários motores) | senão a geração apaga | gerar e perder |
| 5 | Consertos do Open na frente: `rdd-audita-schema` → prova por leitura no "Aplicar a migration"; modelo do brainstorm sem `pydantic/gcp/Terraform` | P1: corrigir antes de construir por cima | deixar para depois |
| 6 | Geração manual, `scripts/gerar-starter.sh <clone do starter>`, sem rede, a partir de tag publicada | sem segredo novo; o OK no starter é sempre do Roberto | workflow automático |
| 7 | O gerador também é dono do `README` do starter, de `scripts/check-gerado.py` e do passo dele nos 2 workflows | remendo à mão no starter é proibido; a trava precisa nascer da geração | editar o starter à mão uma vez |
| 8 | Trava: cabeçalho `GENERATED` com a tag do Open e a soma de conferência de cada arquivo; o CI do starter recusa mudança à mão | garante a manutenção só no Open | confiar na disciplina |
| 9 | `agents/openai.yaml` pela tabela única no Open | simples para o iniciante e mantido num lugar | derivar sozinho; sem arquivo |
| 10 | new-session gerada igual à do Open (sem `sdd/ambiente.md`; o antigo vira evidência) | migração sem conversão | config mínimo; manter ambiente.md |
| 11 | Cópias `~/.claude/skills/sdd-*` regeneradas pela tag publicada, com OK do Roberto na hora | D6 do PORTE; nunca pela branch | — |

---

## Features Removed (YAGNI)

| Feature Suggested | Reason Removed | Can Add Later? |
|-------------------|----------------|----------------|
| Geração automática (workflow que abre PR no starter) | exige token com escrita no starter guardado no Open | Sim, se esquecer a geração virar problema real |
| Modo web de brainstorm, handoff e governança no Open | escopo da F17b | Sim (F17b) |
| Destino de define, design, build, release e ux-review-builder | decisão com dado na F17b | Sim (F17b) |
| `docs/` e `exemplos/` do starter pelo gerador | ficam como estão até a F17b | Sim (F17b) |
| Cenário de branching A/B/C da new-session do starter | o Open usa `project.default_branch`; repositório de uma pessoa quase nunca é C | Não |
| Linha `loop` da prompt-builder sem `sdd-loop-builder` | a loop-builder vai junto para o starter | Não |
| Copiar os testes do Open para dentro do starter | os testes ficam onde o código é escrito; o starter confere a integridade | Não |

---

## Incremental Validations

| Section | Presented | User Feedback | Adjusted? |
|---------|-----------|---------------|-----------|
| Bloco 1: o que a frente entrega | ✅ | Confere | No |
| Bloco 2: a trava e o que sai pelo YAGNI | ✅ | Confere | No |

---

## Suggested Requirements for /define

### Problem Statement (Draft)
O starter mantém texto próprio de skills que o Open já faz melhor, e cada ajuste exige trabalho dobrado ou se perde;
falta um caminho em que o Roberto mantenha só o Open e o starter receba cópia fiel e verificável.

### Target Users (Draft)
| User | Pain Point |
|------|------------|
| Roberto (mantenedor) | ajustar dois repositórios com textos que já divergiram |
| Aluno iniciante do starter (web ou terminal) | recebe skills mais velhas que as do Open; precisa de algo simples |

### Success Criteria (Draft)
- [ ] `scripts/gerar-starter.sh` roda sem rede, a partir de uma tag, sai 0 e gera as 10 skills + README + `check-gerado.py` + passo nos workflows.
- [ ] Gerar duas vezes da mesma tag dá saída idêntica byte a byte.
- [ ] Nenhuma skill gerada cita arquivo criado pelo `init` (teste no Open reprova; baseline vermelho com a cópia crua).
- [ ] Troca que não casa exatamente 1 vez faz o gerador sair ≠ 0 sem gravar nada.
- [ ] A saída gerada passa no `publish-check.sh` e no `check-versions.py` do starter.
- [ ] `check-gerado.py` recusa um arquivo gerado editado à mão.
- [ ] O Open recebeu new-session C1–C4, prompt-builder C1, auditoria-harness C1–C3 e os 2 consertos, com teste.
- [ ] Release do Open publicada; PR do starter com a 1ª geração e Release dele com OK próprio do Roberto.
- [ ] `~/.claude/skills/sdd-*` regeneradas pela tag publicada.

### Constraints Identified
- bash 3.2 + Python stdlib; script novo que chama Python lê `sdd/bin/lib/python.sh` (ou equivalente fora de `sdd/bin`).
- Nada da RDD no Open nem no starter; push, PR e Release no starter só com OK próprio do Roberto.
- Número com 11 dígitos em arquivo do pacote é barrado pelo publish-gate; sem chave por extenso em log (LM-020).
- `sdd-release` em 500 linhas; contagens fixadas em testes (21 skills).

### Out of Scope (Confirmed)
- Itens da tabela YAGNI acima; qualquer trabalho da F15; remendo à mão no starter.

---

## Session Summary

| Metric | Value |
|--------|-------|
| Questions Asked | 5 de descoberta + perfil de risco |
| Approaches Explored | 3 (mecanismo) + 3 (escopo) |
| Features Removed (YAGNI) | 7 |
| Validations Completed | 2 |
| Duration | ~1 sessão parcial |

---

## Next Step

**Ready for:** `/sdd-define sdd/features/BRAINSTORM_F17_STARTER_GERADO.md`
