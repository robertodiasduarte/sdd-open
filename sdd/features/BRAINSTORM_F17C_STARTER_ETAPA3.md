# BRAINSTORM: F17c Starter gerado, etapa 3

> Sessão de exploração antes do Define. Frente F17c do programa INCORPORAR_STARTER (Decisão 5, parâmetro P3);
> fecha a geração do starter começada na F17 (`v2.13.0`, starter `v1.5.17`) e na F17b (`v2.14.0`, starter `v1.5.18`).

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | F17C_STARTER_ETAPA3 |
| **Date** | 2026-11-13 |
| **Author** | brainstorm-agent (Claude), decisões do Roberto |
| **Status** | Ready for Define |

---

## Initial Idea

**Raw Input:** "sdd-define, sdd-design e sdd-build em modo web, geradas do Open. Decisões abertas: o modo web das 3
(molde dentro da skill, prova sem script, entrega no chat) pela regra 'skill de modo' (references/<MODO>.md + 1 linha
no SKILL.md do Open) ou no próprio texto; o alinhamento das pastas (as congeladas gravam em sdd/ sem subpastas; as
geradas, nas pastas do Open); o exemplos/baixar-nfse (kit do build congelado, grava em sdd/); se o starter fica sem
nenhuma congelada ao fim. Meta do Roberto: manutenção num repositório só; o modo de trabalhar do iniciante continua
simples, sem restrições complexas (paradas novas só com o OK dele)."

**Context Gathered:**
- Open em `v2.14.0` + passo 0 desta frente (`53bba4a`: LM-025, LM-026, 13 contagens; `sdd-handoff` 2.2.1 com o
  exemplo preenchido). Starter em `v1.5.18` (`da907b7`): 15 skills geradas, 3 congeladas (define 1.2.0, design 1.1.0,
  build 1.2.0).
- **Comparação item a item** (agente em contexto novo, só leitura, 2026-11-13;
  `sdd/reports/evidence/F17C_STARTER_ETAPA3/COMPARACAO-define-design-build.md`): itens (C) por skill, tabela de paradas
  starter × Open, pastas, o que é ferramenta do mantenedor, o exemplo e os scripts. Fatos principais:
  - citações a arquivo do `init` no texto do Open: define 37 · design 34 · build 43 (as três são pesadas);
  - o texto congelado do starter passa no lint do `init` do gerador (`gerar-starter.py --lint`, as 3 VERDE);
  - paradas que só o Open tem: ~20 no define (cartógrafo, trava e revisor da governança, segurança, KB Domains, ≤~10
    ATs…), ~10 no design (landmines, patterns, revisão adversarial, Segurança com 5 itens…), ~18 no build (passo 0,
    contrato de aceite, 5c, 5d, `report-lint`, `test-baseline`…);
  - o `exemplos/baixar-nfse` (igual byte a byte à semente do Open) seria recusado pelo Define do Open (49 ATs, sem a
    linha Governança; `verify-gate.sh --checar` sai 5) e manda gravar tudo em `sdd/` e rodar "o validador";
  - os validadores das congeladas (`validate_define.py`, `validate_design.py`, `validate_build_report.py`) são
    opcionais, "quando houver filesystem e Python"; o aluno da web não os usa (inferência apoiada no quickstart);
  - defeito do Open: a `sdd-build` exige "Seleção de modo" e "Drift detectado" no relatório, e o molde
    `BUILD_REPORT_TEMPLATE.md` não tem nenhuma das duas; os moldes de DEFINE, DESIGN e BUILD_REPORT trazem restos de
    outro projeto (Terraform, GCP, Python/pytest, `src/|functions/|gen/`, `/build`);
  - defeitos do próprio starter: o protocolo do define termina em `HANDOFF_TO_UX_REVIEW` e a skill manda ao Design; o
    do build termina em `HANDOFF_TO_RELEASE` e a skill manda ao handoff; "Entradas opcionais: `sdd.config.yaml`"
    (arquivo que nada cria); a migration grava `- banco:` em `sdd/ambiente.md`, que a new-session gerada não usa.
- Downloads por zip (medidos na F17b, 25 Releases): build 273 · design 265 · define 262 (~30 por onda de alunos).
- Os `como-falar.md` do starter e do Open diferem nas 3 (74/64/76 linhas de diff); o `publish-check.sh` do starter
  exige `## Como falar com o aluno` no `SKILL.md` e `references/como-falar.md` nas 3.

**Technical Context Observed (for Define):**

| Aspect | Observation | Implication |
|--------|-------------|-------------|
| Likely Location | `.agents/skills/sdd-{define,design,build}/` (o modo web e a linha no `SKILL.md`), `sdd/templates/{DEFINE,DESIGN,BUILD_REPORT}_TEMPLATE.md`, `scripts/gerar-starter.py`, `scripts/starter/{lista.txt,openai.tsv,modos.tsv,raiz/}` | o gerador pode precisar de uma pasta-base por modo (os arquivos do modo colidem com os do Open: `como-falar.md`, `aplicar-migration.md`) |
| Relevant KB Domains | nenhum | — |
| IaC Patterns | N/A | — |

---

## Discovery Questions & Answers

| # | Question | Answer | Impact |
|---|----------|--------|--------|
| 0a | Curadoria da F17b (passo 0) | LM-025 e LM-026 entram; as 13 contagens aplicadas; as 2 sugestões de "mordeu" recusadas | `53bba4a` |
| 0b | Pendentes leves da F17b | só o exemplo do handoff entra; o version gate real e o `--conferir` com `--paths` ficam | `53bba4a` |
| 1 | De que texto nasce o modo web das 3 | **do texto congelado do starter `v1.5.18`**, levado ao Open como arquivo de modo, mudando só o necessário | as paradas do aluno ficam iguais; o exemplo continua válido |
| 2 | O que o starter faz melhor entra também no Open | **o defeito do molde do relatório, os moldes sem sobras e "não finja" + pergunta da 1ª vez do Verify Gate**; o desvio geral do build fica fora | 3 itens de P3 nas skills e moldes do Open |
| 3 | Pastas das geradas | **as do Open** (`sdd/features/`, `sdd/reports/`), como as da F17b | as 18 skills do starter com um jeito só |
| 4 | O `exemplos/baixar-nfse` | **atualizar o README** (pastas, sem validador, o nome "SDD Build by RDD" pelo botão) | o kit continua de ponta a ponta |

---

## Perfil de risco

| Pergunta | Resposta |
|---|---|
| Quem pode ver? | qualquer um: Open e starter são públicos; o gerador roda sem rede na máquina do Roberto; nada da RDD entra (nomes de aluno, caminhos do Wordpress, chaves, código do privado, texto do e-book de segurança) |
| Quem pode mudar? | só o Roberto: no Open com "sdd-open autorizado"; no starter, OK próprio para cada push, PR e merge (o merge publica a Release) |
| Quanto alguém pode pedir? | nada no Open nem no starter (sem serviço, login, upload ou chamada paga); o build do aluno pode aplicar migration no banco dele, com a confirmação que já existe (nome e ref do projeto); nenhum token é pedido |

---

## Sample Data Inventory

| Type | Location | Count | Notes |
|------|----------|-------|-------|
| Input files | `skills/sdd-{define,design,build}/` do starter `v1.5.18` (clone em `/Users/robertoduarte/rdd-worktrees/sdd-starter-f17c-ref`) | 3 skills, 33 arquivos | a base do modo web e da tabela de paradas |
| Output examples | `scripts/starter/raiz/exemplos/baixar-nfse/` (= starter `v1.5.18`) | 5 arquivos | BRAINSTORM, DEFINE (manual-ux), DESIGN, GOVERNANCA_REVIEW, README |
| Ground truth | `COMPARACAO-define-design-build.md` | 1 | itens (C), paradas, pastas |
| Related code | `scripts/gerar-starter.py` (`compor()`), `tests/test_gerar_starter.py` | — | a regra "skill de modo" da F17b |

---

## Approaches Explored

### Abordagem W1: skill de modo com o texto do starter ⭐ Recomendada (escolhida)

**Description:** cada uma das 3 ganha no Open um modo web com o texto congelado do starter `v1.5.18` (SKILL.md e os
arquivos que ele cita: references, assets com o molde e o exemplo), mudado só onde precisa: pastas do Open, prova sem
script (os validadores saem; o que eles conferiam vira releitura), os 4 defeitos do starter consertados, a linha de
identificação igual à do Open. O `SKILL.md` do Open ganha 1 linha ("sem `sdd/bin/` ou sem acesso aos arquivos? siga o
modo web"); `modos.tsv` ganha 3 linhas; o gerador monta a skill do starter só do modo, como a release na F17b.

**Pros:** as paradas do aluno são as de hoje (nenhuma nova a aprovar, salvo as que a mudança de pasta criar); o
exemplo `baixar-nfse` continua válido; o texto passa a morar no Open (um repositório só); a regra do gerador já existe.

**Cons:** no Open, cada uma das 3 tem dois textos que não se atualizam sozinhos (mesmo custo da release na F17b); os
arquivos do modo colidem de nome com os do Open (`como-falar.md`, `aplicar-migration.md`): o modo precisa de pasta
própria e o gerador, de uma pasta-base.

### Abordagem W2: modo recortado do texto do Open

**Pros:** um texto só por skill, mais alinhado. **Cons:** ~30 paradas novas para o aluno, cada uma com OK; o exemplo
seria recusado (49 ATs, sem Governança); bem mais trabalho.

### Abordagem W3: caminho web no próprio texto do Open (seção "Sem terminal")

**Cons:** rejeitada pela regra da F17b (por peso): 34 a 43 citações ao `init` por skill viram dezenas de trocas, e o
`SKILL.md` do build já tem 333 linhas.

---

## Selected Approach

| Attribute | Value |
|-----------|-------|
| **Chosen** | W1 (skill de modo com o texto do starter) |
| **User Confirmation** | 2026-11-13, Roberto: "Do texto do starter" (contra o recorte do Open) |
| **Reasoning** | a simplicidade do iniciante fica como está, sem 30 paradas novas, e a manutenção vai para o Open |

---

## Key Decisions Made

| # | Decision | Rationale | Alternative Rejected |
|---|----------|-----------|----------------------|
| 1 | define, design e build entram na `lista.txt` (18) como skills de modo; o starter fica **sem nenhuma congelada** | fecha a Decisão 5; o README deixa de ter a exceção | manter alguma congelada |
| 2 | O modo web de cada uma é o texto congelado do starter `v1.5.18`, levado ao Open numa pasta própria da skill, com o molde e o exemplo dentro | o aluno não perde nem ganha parada | recortar do texto do Open (W2) |
| 3 | Prova sem script: `validate_define.py`, `validate_design.py`, `validate_build_report.py` e os `tests/` deles **não vão**; o que conferiam vira a releitura do checklist que a própria skill já tem | o aluno da web não os roda; o modo web é "prova sem script" | levar os validadores como opcionais |
| 4 | Pastas do Open nas 3 geradas (`sdd/features/DEFINE_`, `DESIGN_`; `sdd/reports/BUILD_REPORT_`); `.claude/sdd/` sai; na web, tudo no chat | as 18 com um jeito só; a governança gerada já lê `sdd/features/` | `sdd/` plano |
| 5 | Os 4 defeitos do starter consertados no modo (handoff do protocolo do define e do build, `sdd.config.yaml`, `- banco:` em `sdd/ambiente.md`) | o texto passa a ser do Open e vai para o mesmo padrão | levar os defeitos |
| 6 | No Open (P3): o molde do BUILD_REPORT ganha "Seleção de modo" e "Drift detectado"; os 3 moldes perdem as sobras de outro projeto; define, design e build do Open ganham "sem acesso, não finja" (no design: pergunte a stack, não invente caminho) e, no define, a pergunta da 1ª vez do Verify Gate com o `manual-ux` de frases "Eu abri … e vi …" | o que o starter faz melhor e serve a todo usuário do Open | o desvio geral do build (parada nova no Open; fica para outra frente) |
| 7 | `exemplos/baixar-nfse`: os documentos ficam; o README muda (pastas novas, sem o validador, o nome "SDD Build by RDD" continua pelo botão do `openai.tsv`) | o kit de ponta a ponta continua | tirar o exemplo; deixar o README errado |
| 8 | **Simplicidade do iniciante é critério medido**, como na F17b: tabela de paradas starter `v1.5.18` × gerada, com o OK do Roberto em cada parada nova; teste do iniciante (`claude -p --tools ""`, pasta vazia, sem MCP, várias voltas, roteiro e critério escritos antes, 3 de 3 por skill; pergunta sem entrega reprova) | pedido do Roberto | confiar só no lint |

---

## Features Removed (YAGNI)

| Feature Suggested | Reason Removed | Can Add Later? |
|-------------------|----------------|----------------|
| Desvio geral (6 perguntas) no build do Open | parada nova para quem usa o Open; decisão do Roberto | Sim (outra frente) |
| Segurança no Define e `## Segurança` de 5 itens no Design do modo web | seria parada nova; a `sdd-seguranca` já é gerada e avulsa no starter | Sim, com OK do Roberto |
| Governança com trava no Define web | parada nova; a `sdd-governanca` gerada já faz a revisão avulsa | Não neste modo |
| Validadores Python no zip do aluno | prova sem script (Decision 3) | Sim, se um aluno pedir |
| Unificar o texto do Open e o do modo | é a W2; o custo de dois textos foi aceito | Sim (frente própria) |

---

## Incremental Validations

| Section | Presented | User Feedback | Adjusted? |
|---------|-----------|---------------|-----------|
| Passo 0 (curadoria e pendentes) | ✅ | 4 decisões, todas na recomendação | No |
| Abordagem, itens no Open, pastas, exemplo | ✅ | 4 decisões, todas na recomendação | No |
| Bloco final: o que entra, YAGNI e critérios | ✅ | Confere (Roberto, 2026-11-13) | No |

---

## Suggested Requirements for /define

### Problem Statement (Draft)
As 3 skills mais baixadas do starter (define, design, build) ainda são texto próprio, congelado, que diverge do Open e
grava em `sdd/` sem subpastas, enquanto as outras 15 já são geradas. Gerar as 3 do Open sem mudar o modo de trabalhar
do aluno iniciante, e trazer para o Open o que o starter faz melhor.

### Target Users (Draft)
| User | Pain Point |
|------|------------|
| Roberto (mantenedor) | três skills mantidas em dois repositórios |
| Aluno iniciante na web (claude.ai, ChatGPT) | precisa de define e design que entreguem no chat, sem script |
| Aluno com agente que escreve no projeto, sem o `init` | precisa de um build curto, com prova sem o `verify-gate.sh` |
| Usuário do Open | molde do relatório sem as seções que a skill pede; moldes com restos de outro projeto |

### Success Criteria (Draft)
- [ ] `lista.txt` com 18; a geração pela tag sai 0; nenhuma congelada; README e quickstart (2 idiomas) dizem isso e onde
      cada documento fica; os validadores saem do quickstart.
- [ ] As 3 geradas saem só do modo web (como a release); nenhum arquivo do caminho do Open vai; lint do `init` verde;
      `publish-check` do starter verde (`## Como falar com o aluno` e `references/como-falar.md`).
- [ ] **Tabela de paradas** das 3 (starter `v1.5.18` × gerada): nenhuma parada nova sem o OK do Roberto.
- [ ] **Teste do iniciante** com define, design e build gerados: 3 de 3 por skill, critério escrito antes.
- [ ] O exemplo `baixar-nfse` coerente com as geradas (pastas, sem validador).
- [ ] No Open: o molde do BUILD_REPORT com "Seleção de modo" e "Drift detectado"; moldes sem as sobras; "não finja" e a
      pergunta da 1ª vez do Verify Gate; testes com baseline vermelho.
- [ ] Versões das 3 maiores que as do starter; `check-versions.py --base v2.14.0` verde; contagens fixadas atualizadas.
- [ ] Release do Open; geração final pela tag num clone limpo do starter com as 9 checagens verdes; PR e Release do
      starter com OK próprio do Roberto.

### Constraints Identified
- bash 3.2 + Python stdlib; o gerador só roda igual ao da tag (64); nada da RDD; nada da F15 (a frente não toca a
  `sdd-release`, salvo se o build mexer na migração do relatório).
- 11 dígitos no pacote (LM-012): o exemplo de DEFINE do starter (CPF) passa pelo `publish-gate` do Open.
- Contagens fixadas: 22 skills; 31 perguntas em 26 arquivos do `sdd-decisoes-lint` (o texto do starter pode trazer
  perguntas novas); versões em `test_f*_textos`.

### Out of Scope (Confirmed)
- Itens da tabela YAGNI; remendo à mão no starter; qualquer trabalho da F15.

---

## Session Summary

| Metric | Value |
|--------|-------|
| Questions Asked | 4 (passo 0) + 4 (frente) + perfil de risco e amostras (registrados da F17b, mesmo terreno) |
| Approaches Explored | 3 |
| Features Removed (YAGNI) | 5 |
| Validations Completed | 3 |
| Duration | ~1 sessão parcial |

---

## Next Step

**Ready for:** `/sdd-define sdd/features/BRAINSTORM_F17C_STARTER_ETAPA3.md`
