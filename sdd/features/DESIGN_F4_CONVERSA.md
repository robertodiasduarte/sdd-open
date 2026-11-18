# DESIGN: F4 Conversa do sdd-open

> A camada "Como falar com o aluno" entra em 14 skills, com a mesma seção e um `references/como-falar.md` por skill. Um fragmento é o dono do formato de pergunta e de parada. Três lints e dois testes de contrato provam a camada, e um script de evidência prova que comandos e passos ficaram onde estavam.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | F4_CONVERSA |
| **Date** | 2026-10-29 |
| **Author** | SDD Design by RDD (sessão com Roberto Dias Duarte) |
| **BRAINSTORM** | `sdd/features/BRAINSTORM_F4_CONVERSA.md` |
| **DEFINE** | `sdd/features/DEFINE_F4_CONVERSA.md` (v1.1) |
| **UX REVIEW** | `N/A` |
| **LLM Prompts** | false |
| **Status** | Ready for Build |

---

## Architecture Overview

```text
                         sdd/templates/fragments/PERGUNTA_DECISAO.md   (dono do formato)
                                      ▲ citado por
   .agents/skills/<14 skills>/                                  sdd/fixtures/
   ├── SKILL.md ── ## Como falar com o aluno (seção comum)      ├── conversa/<7 casos>/   ──┐
   │              + linha de identificação, sem banner          ├── design/DESIGN_VALIDO.md ─┤
   └── references/como-falar.md (glossário, Status, exemplo)    └── handoff/HANDOFF_VALIDO.md┤
              │                                                                              │
              ▼                                                                              ▼
   sdd/bin/skill-lint.py --conversa ◄── tests/test_skill_lint.py ◄────────── fixtures (6 vermelhas + controle)
   sdd/bin/design-lint.py          ◄── tests/test_design_lint.py   (fixture + mutações)
   sdd/bin/handoff-lint.py         ◄── tests/test_handoff_lint.py  (fixture + mutações)
   tests/test_agnostico.py  ── varre .agents/skills, sdd/templates, AGENTS.md.tmpl, sdd/playbook.md
   tests/test_conversa.py   ── contrato de texto das 16 skills e do fragmento
              │
              ▼
   CI: publish-gate.yml "Skill frontmatter" → skill-lint --conversa · unittest (ubuntu + macOS piso)
   Fora do gate (evidence/F4_CONVERSA/): comandos-intactos.log (v2.2.4 × HEAD) · design-lint-reais.log ·
                                baseline.log (test_agnostico na v2.2.4) · check-versions.log
```

---

## Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| `PERGUNTA_DECISAO.md` | Formato único da pergunta (autorização, aberta, agrupada, eco, `[Dn]`) e da parada ⏸️ (campos `Brief:` e `Sessão nova:` que a F9 liga ao `exit 40`) | Markdown em `sdd/templates/fragments/` |
| Seção `## Como falar com o aluno` | As 5 partes, a tabela de etapas da skill e as regras curtas, autocontidas no `SKILL.md` | Markdown; bloco de regras idêntico nas 14 skills, tabela e Status próprios |
| `references/como-falar.md` | Glossário da skill, Status preenchido, ≥1 exemplo completo com decisão | Markdown, um por skill (14) |
| `skill-lint.py --conversa` | Confere a seção, a tabela, as 5 partes, o `como-falar.md` e as perguntas dos exemplos | Python 3.9 stdlib; flag nova, sem mudar o padrão |
| `design-lint.py` | Títulos de ADR (`### Decision N: <nome>`), File Manifest, `Total Files`, dependências, placeholder | Python 3.9 stdlib, novo em `sdd/bin/` |
| `handoff-lint.py` | Mínimo do `HANDOFF_TEMPLATE.md` do open, tolerante a seção extra | Python 3.9 stdlib, novo em `sdd/bin/` |
| `test_agnostico.py` | Reprova nome de ferramenta de um agente só no texto que vai para o projeto | unittest |
| `test_conversa.py` | Linha de identificação = versão, `updated`, sem banner, fragmento citado, passo de lint na design/handoff, conteúdo do fragmento | unittest |
| Script de evidência | `comandos-intactos.log`: títulos de passo e linhas de comando de cada skill, `v2.2.4` × HEAD, contra a lista de exceções | bash + Python inline em `sdd/reports/evidence/F4_CONVERSA/gerar-evidencia.sh` (fora do commit do produto) |

---

## Key Decisions

### Decision 1: Seção autocontida e bloco de regras idêntico nas 14 skills

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-10-29 |

**Context:** abordagem A do BRAINSTORM. A camada não pode depender de o agente abrir um segundo arquivo, e a Decisão 5 da frente quer as skills funcionando sozinhas quando o starter for gerado do open.

**Choice:**
- Cada `SKILL.md` recebe, logo depois da introdução e antes do primeiro `## Entrada`/`## Processo`, a seção `## Como falar com o aluno`. Ela tem três partes:
  - 3 linhas de abertura, que mandam ler o `como-falar.md` e citam o `PERGUNTA_DECISAO.md`;
  - a tabela `| Etapa | Nome para o aluno | Passos desta skill |`;
  - o **bloco de regras comum** (Code Pattern 1), copiado igual nas 14 skills, com troca só do exemplo de Status.
- O `como-falar.md` leva o que muda por skill: glossário, Status preenchido e exemplo.

**Rationale:** o bloco igual em todas permite ao `test_conversa` conferir as frases-chave nas 14 com uma lista só, e a deriva vira teste vermelho.

**Alternatives Rejected:**
1. Fragmento central com as regras (abordagem B). Rejeitada porque a camada some se o agente não abrir o fragmento, e porque quebra a skill como zip.
2. Texto livre por skill, adaptado do starter. Rejeitada porque cada skill derivaria, e o teste teria de conhecer 14 redações.

**Consequences:**
- Mudar uma regra reabre as 14 skills: o preço da autonomia.
- A F9 edita o bloco com um só substituto de texto.

---

### Decision 2: `skill-lint.py --conversa`: o que é seção, parte, pergunta e opção

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-10-29 |

**Context:** DEFINE AT-001 a AT-005. O lint vai para o projeto do usuário, e sem a flag nada pode mudar.

**Choice:** `--conversa` pode aparecer em qualquer posição de `argv`. Qualquer outro argumento que comece com `--` sai 64. Com a flag, além do frontmatter, o lint confere o seguinte.

- **Seção:** linhas de `## Como falar com o aluno` até o próximo `## `. Exatamente 1 ocorrência do título.
- **Tabela:** uma linha `^\|\s*Etapa\s*\|` dentro da seção.
- **5 partes:** as substrings `**Status**`, `**O que foi feito**`, `**Agora`, `**Sua decisão**` e `**Próximo passo**` dentro da seção.
- **Referência:** se a seção cita `references/como-falar.md`, o arquivo tem de existir ao lado do `SKILL.md`. Sem citação, não é exigido; é o Grupo 1, como iniciar-repo e higiene-dado.
- **Perguntas** (só no `como-falar.md`, depois de tirar blocos cercados por crases triplas e o prefixo `> `):
  - uma linha com trecho em negrito terminado em `?` (`\*\*[^*\n]*\?\*\*`) seguida de ≥1 linha `^\s*[-*+]\s+\*\*([^*]+)\*\*`; linha em branco (ou `>` vazio) antes ou entre opções e linha recuada de continuação não encerram a lista; o prefixo `> ` é tirado;
  - sem opções, é pergunta aberta e não é conferida.

  Em cada pergunta de decisão:
  - exatamente 1 opção com `(recomendado)` (sem caixa), e ela é a 1ª;
  - 1 opção de rótulo `não sei`;
  - nenhuma de rótulo `outro`/`outra`/`other`.

  O arquivo precisa de ≥1 pergunta de decisão.
- **Próximo passo:** cada linha que começa com `**Próximo passo**` no `como-falar.md`, depois de tirar o rótulo e o separador inicial (` — `, `:`, espaços), tem ≤100 caracteres (`len()` do texto).

Cada erro sai como `🛑 <arquivo>: <motivo>` em stderr. O exit é 1, e a última linha continua sendo `RESULTADO: VERMELHO` seguida de `→ …`.

**Rationale:**
- As substrings em negrito são as que as 2 skills portadas já usam, então elas passam sem edição.
- "Pergunta de decisão = negrito com `?` + opções" separa autorização (conferida) de pergunta aberta (livre), como no item 7 da camada.

**Alternatives Rejected:**
1. Exigir `como-falar.md` sempre. Rejeitada porque obrigaria a mudar iniciar-repo e higiene-dado, que estão fora de escopo.
2. Conferir as perguntas também no `SKILL.md`. Rejeitada porque o bloco do OK da release e o pré-voo da new-session têm perguntas com regra própria (`test_contrato_build_release`).

**Consequences:**
- O lint confere formato, não tom.
- Uma opção "não sei" escrita como `**não sei, explique**` não conta: o rótulo tem de ser exato.

---

### Decision 3: Fixtures em `sdd/fixtures/` e mutações dentro dos testes

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-10-29 |

**Context:** o item D pede fixtures que reprovam, e a W2 vai acrescentar casos D1–D5 "nas mesmas fixtures". O AT-020 exige as fixtures existentes intactas.

**Choice:**
- **`skill-lint`:** 7 pastas em `sdd/fixtures/conversa/`, cada uma com o nome da skill igual à pasta (o lint exige):
  - `conversa-controle` (passa);
  - `conversa-sem-secao`;
  - `conversa-sem-como-falar`;
  - `conversa-sem-recomendado`;
  - `conversa-dois-recomendados`;
  - `conversa-sem-nao-sei`;
  - `conversa-com-outro`.
- **`design-lint` e `handoff-lint`:** um arquivo válido cada (`sdd/fixtures/design/DESIGN_VALIDO.md`, `sdd/fixtures/handoff/HANDOFF_VALIDO.md`). O teste deriva cada caso vermelho por substituição de texto na cópia, em pasta temporária.

**Rationale:**
- As fixtures de skill são pastas completas, e é isso que a W2 estende.
- Os casos de DESIGN/HANDOFF são variações de uma linha, que ficam legíveis como mutação e não somam 13 arquivos.
- O precedente é `sdd/fixtures/playbook/`.

**Alternatives Rejected:**
1. Tudo inline nos testes. Rejeitada porque o item D quer fixture que a W2 reaproveita.
2. Um arquivo por caso vermelho de DESIGN/HANDOFF. Rejeitada porque o texto seria repetido 13 vezes.

**Consequences:**
- O `init` copia `sdd/fixtures/` na 1ª instalação, então essas pastas chegam ao usuário como exemplo, como as do playbook.
- Elas não ficam em `.agents/skills/`, então nenhum agente as carrega como skill.

---

### Decision 4: Regras do `design-lint.py`, com placeholder só fora de código

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-10-29 |

**Context:**
- Item E e DEFINE AT-008/AT-009/AT-010.
- Os DESIGN_F1–F3 reais têm dependências no formato `None`, `1` ou `1, 2, 7`.
- O `Total Files` deles bate com o número de linhas.
- Eles citam o nome da feature entre chaves, sempre dentro de crases (`DESIGN_<F>.md` na forma do template).

**Choice:**
- **Texto analisado:** sem os blocos cercados por crases triplas e sem os trechos entre crases simples.
- **Key Decisions:**
  - `## Key Decisions` presente;
  - todo `### ` até o próximo `## ` casa `^### Decision (\d+): \S`;
  - os números são 1..n em ordem;
  - n ≥ 1.
- **File Manifest:**
  - em `## File Manifest`, as linhas de dados são as que casam `^\|\s*\d+\s*\|`; precisa haver ≥1;
  - `**Total Files:** N` presente e N = número de linhas;
  - a última célula de cada linha dá as dependências pelos números `\d+` (`None`, `—` e vazio = sem dependência). Cada número tem de ser uma linha existente e diferente da própria, e o grafo não pode ter ciclo (DFS).
- **Placeholder** (`\x7b`/`\x7d` = chaves; `« »` não conta, é aspa comum em português): `\x7b[A-Z][A-Z0-9_][A-Z0-9_]+\x7d` ou `\x7b[^\x7b\x7d\n]*\s[^\x7b\x7d\n]*\x7d`, fora de código.
- **Saída:** cada violação vira uma linha `🛑 <arquivo>: <regra>`; exit 1 com `RESULTADO: VERMELHO`; exit 0 com `✅ <arquivo>: DESIGN válido`. Sem argumento ou arquivo ausente, 64; arquivo que existe e não se lê (permissão, bytes fora de UTF-8), 1 com `🛑` e `RESULTADO: VERMELHO`.

**Rationale:** é o mínimo que a F12 precisa (títulos) mais o que a `sdd-build` usa (manifest ordenável). O resto do `validate_design.py` do starter (inventário LLM, rastreabilidade) foi cortado pelo YAGNI.

**Alternatives Rejected:**
1. Portar o `validate_design.py`. Rejeitada porque ele foi feito para o template do starter.
2. Aceitar `### Decisão N`. Rejeitada porque a F12 lê o título em inglês, que é o do template.

**Consequences:** um DESIGN antigo com `### ADR-1` reprova. Isso é o que se quer daqui para frente, e o lint só roda no DESIGN recém-gravado pela `sdd-design`.

---

### Decision 5: Regras do `handoff-lint.py`: mínimo do template do open

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-10-29 |

**Context:** pergunta 5 do BRAINSTORM, item F e DEFINE AT-011/AT-012. O Prompt de retomada é um bloco cercado que carrega comandos reais (variável de shell com chaves, `awk` com bloco de ação) e, por descuido, `«placeholder»`.

**Choice:**
- **Estrutura:**
  - 1º título `# HANDOFF:`;
  - seção `^## Ficha` com linhas de tabela que casam `\|\s*\**Objetivo\**\s*\|`, `…Status…` e `…Verify Gate…`;
  - `## Prompt de retomada` com ≥1 bloco cercado (abertura e fechamento), delimitada sem os blocos de código; dispensada quando a célula Status da Ficha começa por ✅;
  - `## Histórico de slices` com ≥1 `^### .+ [—-] \d\d\d\d-\d\d-\d\d\s*$`.
- **Placeholder:**
  - fora de código, as 3 formas da Decisão 4;
  - dentro de bloco cercado, só `«…»` e nome em MAIÚSCULAS entre chaves sem `$` antes.
- **Frases vagas** (fora de código): `como (discutimos|discutido|combinamos|combinado|vimos antes|falamos|conversamos)`, `conforme (conversamos|discutimos|combinado|falado)`, `continu(ar|e) de onde paramos`.
- **Seções aceitas:** qualquer outra seção passa, e `## Eventos` não é exigido.
- **Saída e exits:** os mesmos da Decisão 4.

**Rationale:** confere o que a `sdd-handoff` do open promete ("autossuficiente, sem placeholder, sem 'como discutimos'") sem amarrar a W5, que acrescenta seções.

**Alternatives Rejected:**
1. Formato do starter. Rejeitado na pergunta 5.
2. Placeholder em prosa também dentro de código. Rejeitado porque um `awk` com bloco de ação reprovaria um prompt correto.

**Consequences:** o `HANDOFF_INCORPORAR_STARTER.md` desta família (formato do starter) reprova no lint. Ele é escrito pela `sdd-handoff` do usuário, não pela do pacote, e não é fixture.

---

### Decision 6: `test_agnostico.py`: termos, escopo e adaptadores

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-10-29 |

**Context:** pergunta 7 do BRAINSTORM, regra 10 do plano (8.0) e DEFINE AT-015/AT-016.

**Choice:**
- **Termos:** `TERMOS = re.compile(r"\b(AskUserQuestion|TodoWrite|PreToolUse|PostToolUse|subagent_type)\b|\b(Task|Agent) tool\b|(?<![\w./-])/model\b")`.
- **Escopo:** todo arquivo de texto (`.md`, `.py`, `.sh`, `.yaml`, `.yml`, `.json`, `.tmpl`, `.txt`) sob `.agents/skills/` e `sdd/templates/`, mais `AGENTS.md.tmpl` e `sdd/playbook.md`.
- **`ADAPTADORES`:** tupla de prefixos de caminho isentos, hoje vazia e comentada. O `init --vendors` gera o adaptador a partir de `bin/lib/vendors.sh`, que fica fora do escopo. O que for específico de um vendor e entrar em `sdd/templates/` na F7/F8 é declarado ali.
- **Função `achados(raiz) -> list[str]`** (`arquivo:linha: termo`), testada assim:
  - na `RAIZ` (vazio);
  - numa árvore temporária com `AskUserQuestion` num `SKILL.md` (1 achado);
  - num controle com "subagente" e `app/models/x` (vazio).

**Rationale:**
- Lista de termos explícita, sem heurística.
- "Subagente" é o conceito que a tabela de degradação usa.
- A guarda `(?<![\w./-])` evita confundir `/model` com `app/models` ou `src/model`.

**Alternatives Rejected:**
1. Proibir "subagente". Rejeitado na pergunta 7.
2. Varrer só `SKILL.md`/`references/`. Rejeitado porque não pegaria o `CLARIFY.md`.

**Consequences:** os 2 hits atuais (`CLARIFY.md:45` e `BUILD_REPORT_TEMPLATE.md:75`) são reescritos no mesmo commit:
- "via `AskUserQuestion`" vira "pela ferramenta de pergunta do seu agente, ou em texto";
- "via Task tool" vira "despachado a um agente especialista".

---

### Decision 7: Onde entra o passo de lint na `sdd-design` e na `sdd-handoff`

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-10-29 |

**Context:**
- Pergunta 6 do BRAINSTORM.
- Na `sdd-design`, o último passo é `### 7. Gravar`.
- Na `sdd-handoff`, o arquivo é gravado nos passos 2 e 3, e o último passo é `### 4. Oferecer limpeza`.
- Renumerar um passo mudaria a ordem, que é a regra que a F4 prova.

**Choice:**
- `sdd-design`: novo `### 8. Conferir` com `python3 sdd/bin/design-lint.py sdd/features/DESIGN_<FEATURE>.md` (na skill, com o marcador de feature que ela já usa; vermelho ⇒ corrija e rode de novo antes de entregar).
- `sdd-handoff`: novo `### 3b. Conferir a ficha` com `python3 sdd/bin/handoff-lint.py sdd/handoffs/HANDOFF_<FEATURE>.md`, entre o 3 e o 4.
- O DEFINE AT-014 passa a dizer "o passo logo depois do que grava o arquivo" (DEFINE v1.1).

**Rationale:** os dois lints rodam sobre o arquivo final, e nenhum passo existente muda de número nem de lugar.

**Alternatives Rejected:**
1. Lint como último passo da `sdd-handoff`, depois da limpeza. Rejeitado porque a limpeza pode arquivar o arquivo antes da conferência.
2. Renumerar o "Oferecer limpeza" para 5. Rejeitado porque muda a ordem dos passos.

**Consequences:** o `comandos-intactos.log` mostra exatamente 1 título novo e 1 comando novo em cada uma das duas skills.

---

### Decision 8: `sdd-checar-ambiente`: Status antes do relatório do script

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-10-29 |

**Context:**
- A skill manda "responder com a saída [do `checar.sh`], exatamente como veio, sem frase antes, sem frase depois".
- O relatório do script já é traduzido para o aluno: blocos 🔴/⚠️ com o comando exato e a linha ✅ com a identificação.
- A Decisão 3 da frente quer o Status abrindo toda resposta.

**Choice:**
- A resposta passa a ser:
  - a linha de Status (`Ambiente: ✅ 1 Verificar · ▶️ 2 Explicar`, ou `✅ 2 Explicar` quando saudável);
  - seguida do relatório do script como veio.
- A frase "sem frase antes" vira "só o Status antes".
- O relatório não é retraduzido: a camada reconhece que ele já está no formato do aluno.
- A "Sua decisão" só aparece na conversa que segue, quando o aluno pergunta por um item. O `como-falar.md` traz esse exemplo: um 🔴 de pasta sincronizada, com parada ⏸️.
- A linha de identificação continua sendo a do fim da linha ✅, que o script lê do `SKILL.md`. Não entra uma 2ª no começo.
- O DEFINE, exceção (d), fica: "na `sdd-checar-ambiente`, o Status vem antes do relatório do script" (DEFINE v1.1).

**Rationale:**
- Com o Status, a skill obedece à Decisão 3 sem duplicar a tradução que o script já faz.
- Uma 2ª linha de identificação quebraria o "sem frase antes" que sobra.

**Alternatives Rejected:**
1. Traduzir o relatório pela camada. Rejeitado porque duplica o que o script já faz, e o texto e o teste do script ficariam fora de sincronia.
2. Exceção à Decisão 3. Rejeitado no checkpoint 1.

**Consequences:** o `test_conversa` confere a identificação da checar-ambiente pela linha `sdd-checar-ambiente v1.4.0 · out/2026` já existente.

---

### Decision 9: Prova de comandos intactos por extração ordenada

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-10-29 |

**Context:** DEFINE AT-018. A cópia do gate não tem `.git`, e um diff lido à mão em 14 skills deixa passar.

**Choice:**
- O `gerar-evidencia.sh` roda um Python inline que, para cada uma das 14 skills, extrai em ordem:
  - de `git show v2.2.4:<SKILL.md>` e do HEAD:
    - os títulos de passo (`^(##|###|####) (\d|Passo \d|FASE \d)`);
    - os trechos entre crases que contêm `sdd/bin`, `git `, `gh `, `bash `, `python3` ou `scripts/`;
  - do texto todo, as linhas de lista numerada `^\s*\d+[a-z]?\. ` com o 1º trecho em negrito.
- O `difflib.unified_diff` das duas listas é comparado com a lista `EXCECOES` por skill:
  - `sdd-design`: `+### 8. Conferir` e `+python3 sdd/bin/design-lint.py …`;
  - `sdd-handoff`: `+### 3b. Conferir a ficha` e `+python3 sdd/bin/handoff-lint.py …`.
- Diferença fora da lista ⇒ `FALHA <skill>`, e o script sai 1.
- O log mostra, por skill, `idêntico` ou as linhas permitidas.

**Rationale:** a ordem fica provada (listas ordenadas) e o comando também (trecho literal). A troca do banner pela linha de identificação não cita comando, então não aparece.

**Alternatives Rejected:**
1. Teste na suíte. Rejeitado porque não há `.git` na cópia do gate.
2. `grep '^[-+]'` no diff. Rejeitado porque pega a tradução legítima (lição do DEFINE do starter).

**Consequences:** um comando que muda de lugar entre passos aparece no diff. Ele vira correção ou exceção discutida, nunca silêncio.

---

### Decision 10: Contrato de texto no `test_conversa.py`, `check-versions.py` intacto

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-10-29 |

**Context:** DEFINE AT-006/AT-007/AT-014/AT-017. O `check-versions.py` é o gate da release, e mudá-lo é risco fora do escopo.

**Choice:** o `tests/test_conversa.py` confere:
- **nas 16 skills:**
  - toda ocorrência de `` `<nome> v<X.Y.Z> · `` no `SKILL.md` tem a versão do frontmatter, e há ≥1;
  - `updated:` no `metadata`;
  - nenhuma linha `Abra a resposta com o banner`;
- **nas 14 da F4:**
  - a seção cita `sdd/templates/fragments/PERGUNTA_DECISAO.md`;
  - o bloco comum de regras tem as frases-chave (lista `FRASES` do Code Pattern 1);
  - `como-falar.md` existe;
- **na design e na handoff:** o passo e o comando de lint (AT-014);
- **no fragmento:** os campos (AT-007).

**Rationale:** a regra fica onde mora o contrato de texto (como no `test_contrato_build_release`), e a release continua com o mesmo gate.

**Alternatives Rejected:**
1. Ampliar o `check-versions.py`. Rejeitado porque mexe no gate da release.

**Consequences:**
- Cada frente que mudar uma versão também muda a linha de identificação, ou o teste reprova.
- Os testes que fixam versões (`test_correcoes_w0`, `test_contrato_build_release`, `test_matriz_new_session`) são atualizados de propósito.

---

## File Manifest

| # | File | Action | Purpose | Agent | Dependencies |
|---|------|--------|---------|-------|--------------|
| 1 | `sdd/templates/fragments/PERGUNTA_DECISAO.md` | Create | Formato da pergunta (autorização, aberta, agrupada, eco, `[Dn]` reservado) e da parada ⏸️ com `Brief:`/`Sessão nova:` | (general) | None |
| 2 | `sdd/bin/skill-lint.py` | Modify | Flag `--conversa` (Decisão 2); docstring com as regras; sem a flag, idêntico | (general) | None |
| 3 | `sdd/fixtures/conversa/*/SKILL.md` e `references/como-falar.md` | Create | 7 casos: controle + 6 que reprovam (Decisão 3) | (general) | 1, 2 |
| 4 | `tests/test_skill_lint.py` | Modify | 16 skills com `--conversa`; sem flag numa skill sem seção = 0; cada fixture 1 com o motivo; controle 0; flag desconhecida = 64 | (general) | 2, 3 |
| 5 | `sdd/bin/design-lint.py` | Create | Regras da Decisão 4; 0 · 1 · 64 | (general) | None |
| 6 | `sdd/fixtures/design/DESIGN_VALIDO.md` | Create | DESIGN válido no template do open, com bloco de código contendo um placeholder entre chaves (não conta) | (general) | 5 |
| 7 | `tests/test_design_lint.py` | Create | Fixture 0; 7 mutações 1; 64 sem argumento e com arquivo ausente | (general) | 5, 6 |
| 8 | `sdd/bin/handoff-lint.py` | Create | Regras da Decisão 5; 0 · 1 · 64 | (general) | None |
| 9 | `sdd/fixtures/handoff/HANDOFF_VALIDO.md` | Create | HANDOFF preenchido a partir do template, sem `## Eventos`, com um `awk` de bloco de ação e `$HOME` entre chaves no prompt | (general) | 8 |
| 10 | `tests/test_handoff_lint.py` | Create | Fixture 0; + seção extra 0; 6 mutações 1; 64 | (general) | 8, 9 |
| 11 | `tests/test_agnostico.py` | Create | `achados()` na RAIZ, fixture que reprova e controle (Decisão 6) | (general) | None |
| 12 | `sdd/templates/fragments/CLARIFY.md` | Modify | Linha 45 sem `AskUserQuestion` | (general) | 11 |
| 13 | `sdd/templates/BUILD_REPORT_TEMPLATE.md` | Modify | Linha 75 sem "Task tool" | (general) | 11 |
| 14 | `tests/test_conversa.py` | Create | Contrato de texto da Decisão 10 | (general) | 1 |
| 15 | `.agents/skills/sdd-brainstorm/SKILL.md` e `references/como-falar.md` | Modify | Seção + referência; sem banner; identificação; 2.0.0 → 2.1.0 + `updated` | (general) | 1, 2, 14 |
| 16 | `.agents/skills/sdd-define/SKILL.md` e `references/como-falar.md` | Modify | Idem; 2.1.0 → 2.2.0 | (general) | 1, 2, 14 |
| 17 | `.agents/skills/sdd-design/SKILL.md` e `references/como-falar.md` | Modify | Idem + `### 8. Conferir` com o `design-lint`; 2.0.0 → 2.1.0 | (general) | 1, 2, 5, 14 |
| 18 | `.agents/skills/sdd-build/SKILL.md` e `references/como-falar.md` | Modify | Idem, com o contador Tarefas N/M; 2.1.1 → 2.2.0 | (general) | 1, 2, 14 |
| 19 | `.agents/skills/sdd-handoff/SKILL.md` e `references/como-falar.md` | Modify | Idem + `### 3b. Conferir a ficha` com o `handoff-lint`; 2.0.0 → 2.1.0 | (general) | 1, 2, 8, 14 |
| 20 | `.agents/skills/sdd-new-session/SKILL.md` e `references/como-falar.md` | Modify | Idem; 1.1.0 → 1.2.0 | (general) | 1, 2, 14 |
| 21 | `.agents/skills/sdd-release/SKILL.md` e `references/como-falar.md` | Modify | Idem; o bloco do OK e a pergunta única ficam intactos; 2.2.0 → 2.3.0 | (general) | 1, 2, 14 |
| 22 | `.agents/skills/sdd-iterate/SKILL.md` e `references/como-falar.md` | Modify | Idem; passo 4 intacto (W0); 2.0.1 → 2.1.0 | (general) | 1, 2, 14 |
| 23 | `.agents/skills/sdd-governanca/SKILL.md` e `references/como-falar.md` | Modify | Idem; 2.1.0 → 2.2.0 | (general) | 1, 2, 14 |
| 24 | `.agents/skills/sdd-ux-review/SKILL.md` e `references/como-falar.md` | Modify | Idem; 2.1.0 → 2.2.0 | (general) | 1, 2, 14 |
| 25 | `.agents/skills/sdd-playbook/SKILL.md` e `references/como-falar.md` | Modify | Idem; a leitura do início de sessão continua silenciosa; 2.0.0 → 2.1.0 | (general) | 1, 2, 14 |
| 26 | `.agents/skills/sdd-prompt-builder/SKILL.md` e `references/como-falar.md` | Modify | Idem; o TXT BLOCK de saída fica como está; 2.0.0 → 2.1.0 | (general) | 1, 2, 14 |
| 27 | `.agents/skills/sdd-auditoria-harness/SKILL.md` e `references/como-falar.md` | Modify | Idem; 1.0.0 → 1.1.0 | (general) | 1, 2, 14 |
| 28 | `.agents/skills/sdd-checar-ambiente/SKILL.md` e `references/como-falar.md` | Modify | Idem, com a Decisão 8; 1.3.0 → 1.4.0 | (general) | 1, 2, 14 |
| 29 | `tests/test_correcoes_w0.py` | Modify | Versões esperadas: iterate 2.1.0, build 2.2.0 | (general) | 18, 22 |
| 30 | `tests/test_contrato_build_release.py` | Modify | Versões esperadas: release 2.3.0, build 2.2.0 | (general) | 18, 21 |
| 31 | `tests/test_matriz_new_session.py` | Modify | Versão esperada 1.2.0 | (general) | 20 |
| 32 | `.github/workflows/publish-gate.yml` | Modify | Passo `Skill frontmatter`: `python3 sdd/bin/skill-lint.py --conversa .agents/skills/sdd-*/SKILL.md` | (general) | 2 |
| 33 | `tests/test_release_workflow.py` | Modify | Espera a linha nova do passo | (general) | 32 |
| 34 | `docs/cli-conventions.md` | Modify | Tabela de exit codes com `design-lint.py` · `handoff-lint.py` e a flag `--conversa` | (general) | 2, 5, 8 |
| 35 | `CONTRIBUTING.md` | Modify | "Run `python3 sdd/bin/skill-lint.py --conversa` on every `SKILL.md` you touch" | (general) | 2 |
| 36 | `MANIFEST.txt` | Modify | Arquivos novos (1, 3, 5–11, 14 e os 14 `como-falar.md`) em ordem `LC_ALL=C` | (general) | 1, 3, 5, 6, 7, 8, 9, 10, 11, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28 |

**Total Files:** 36

---

## Landmines aplicáveis

| Landmine (⛔) | Fonte | Veredito | Como / Por quê |
|---------------|-------|----------|----------------|
| Fixture só do lado verde não prova o lint | `LM-001` | ✔ tratado | 6 fixtures que reprovam no `skill-lint` e mutações nos dois lints novos (Decisão 3); 4 sabotagens |
| Baseline vermelho antes do código | `LM-002` | ✔ tratado | Testes 4, 7, 10, 11 e 14 escritos e rodados antes dos scripts e das skills; vermelho em `evidence/F4_CONVERSA/baseline.log` |
| Unicode invisível digitado pelo agente (alerta da M1) | handoff, etapa M1 | ✔ tratado | Depois de escrever cada skill, conto os code points fora de ASCII e aceito só emoji, FE0F, ZWJ e letras do português; o passo "Skill integrity" do CI reconfere |
| `curl … \| sh` literal reprova no CI | handoff, etapa M1 | ✔ tratado | Nenhum exemplo de comando remoto no texto novo |
| Literal que casa com `publish-gate-patterns.txt` | `tests/apoio.py` | ✔ tratado | Exemplos e fixtures sem CPF/CNPJ/telefone/e-mail fora de `example.com`/caminho `/Users/` |
| Skill portada citando o starter | `tests/test_matriz_new_session.py` (`Portadas`) | ✔ tratado | O `como-falar.md` da checar-ambiente não cita "sdd-starter" nem "sdd/ambiente.md" |

---

## Contrato de aceite

N.A. (1 camada): o manifest só toca texto de skill/template, scripts Python de `sdd/bin/` e testes, sem `api`/`ui`/`sql`. A revisão de contexto fresco antes do PR continua obrigatória pela sessão.

---

## Agent Assignment Rationale

Agent Discovery: Not available. Tudo `(general)` e em modo default, na mesma conversa: os 14 `SKILL.md` compartilham o bloco comum e o glossário, e um autor só mantém a redação igual.

---

## Code Patterns

### Pattern 1: Bloco comum da seção (igual nas 14; só a tabela e o exemplo de Status mudam)

```markdown
## Como falar com o aluno

Leia `references/como-falar.md` antes da primeira resposta: o glossário desta skill, o Status preenchido
e um exemplo completo. Pergunta e parada seguem `sdd/templates/fragments/PERGUNTA_DECISAO.md`.
Quem usa esta skill, em geral, nunca usou git nem terminal.

| Etapa | Nome para o aluno | Passos desta skill |
|---|---|---|
| 1 | Plano | 1, 1.5 e 2–3 |

Toda resposta, nesta ordem (pule a parte sem conteúdo):

1. **Status** — uma linha que começa pelo nome da fase: `Build: ✅ 1 Plano · ▶️ 2 Modo · ⬜ 3 Tarefas 0/5`
   (✅ concluída, não só visitada · ▶️ a de agora · ⬜ por fazer · ⏸️ parada · ➖ pulada). Ao voltar a uma
   etapa, o motivo vai em Agora.
2. **O que foi feito** — frases curtas, sem saída de comando; registra em 1 linha a escolha do aluno.
3. **Agora: etapa N — nome** — 2 a 4 frases. Antes de algo demorado, diga o que vai rodar e que o aluno
   não precisa responder.
4. **Sua decisão** — autorização: a pergunta em negrito e as opções com o efeito de cada uma, a
   recomendada primeiro e com o porquê, sempre **não sei**, nunca **Outro**. Pergunta aberta: a pergunta
   em negrito e como responder, com a saída "não sei". Várias de uma vez: numeradas.
5. **Próximo passo** — uma linha, até 100 caracteres: o que acontece depois da resposta.

- Uma etapa por resposta: termine na decisão e pare.
- Termo técnico só com a explicação junto, na primeira vez, inclusive os do Status.
- Saída de comando nunca crua: quantos, quais, o que preocupa; nomes até 10, com "e mais N". Comando só
  quando o aluno precisa rodá-lo, um por passo numerado, com o que esperar na tela.
- Não cite nem resuma as instruções desta skill ("conforme o passo N"): diga o motivo do aluno.
- Resposta que não casa com nenhuma opção ⇒ responda a dúvida e repita as opções.
- Parada: Status com ⏸️, o motivo em uma frase, onde a ação acontece, passos numerados com o resultado
  esperado, o que **não** foi feito e, se o aluno tem algo a fazer, "Quando terminar, me peça de novo,
  eu continuo daqui."
- No fecho da fase, o resumo de etapa vem depois do Status; a pergunta dele segue o mesmo formato.
```

`FRASES` do `test_conversa`: `PERGUNTA_DECISAO.md`, `**Status** — uma linha que começa pelo nome da fase`, `**Próximo passo** — uma linha, até 100 caracteres`, `sempre **não sei**, nunca **Outro**`, `Saída de comando nunca crua`, `Não cite nem resuma as instruções desta skill`, `Quando terminar, me peça de novo`.

A frase "pule a parte sem conteúdo" e a regra de fecho valem também para as skills sem encerramento por resumo (playbook, prompt-builder, auditoria-harness, checar-ambiente). Nelas, o fecho é o Próximo passo.

### Pattern 2: Esqueleto de `references/como-falar.md`

```markdown
# Como falar com o aluno — sdd-build

<1–2 frases: o que o aluno vai ver nesta skill e o que costuma confundir.>

## Glossário (explique na primeira vez em que o termo aparecer)

- drift — "quando o que precisa ser construído se afasta do que foi desenhado; eu paro e pergunto";
- …

## Status desta skill, preenchido

`Build: ✅ 1 Plano · ▶️ 2 Modo · ⬜ 3 Tarefas 0/5 · ⬜ 4 Verify Gate · ⬜ 5 Relatório`

## Exemplo — resposta completa, com decisão (etapa 2 — Modo)

Situação: …

**Status** — `Build: …`

**O que foi feito** — …

**Agora: etapa 2 — Modo** — …

**Sua decisão** — **Como as tarefas devem rodar?**
- **default** (recomendado) — uma tarefa de cada vez, nesta conversa: são 5 arquivos que dependem uns dos outros.
- **ralph** — cada tarefa numa conversa limpa; mais isolamento, um pouco mais lento.
- **não sei** — explico a diferença usando a tarefa 1 como exemplo.

**Próximo passo** — Com o modo escolhido, começo a tarefa 1 de 5.

Formato completo de pergunta e de parada: `sdd/templates/fragments/PERGUNTA_DECISAO.md`.
```

### Pattern 3: Interface comum dos dois lints novos

```python
#!/usr/bin/env python3
"""design-lint.py — confere um DESIGN contra o template do sdd-open. Só stdlib, Python >= 3.9.

Uso: python3 sdd/bin/design-lint.py <DESIGN.md>     # 0 válido · 1 violações · 64 uso
"""
from __future__ import annotations
import re, sys
from pathlib import Path

CERCA = re.compile(r"^(```|~~~).*?^\1[^\n]*$", re.M | re.S)
CRASE = re.compile(r"`[^`\n]*`")
PLACEHOLDER = re.compile(r"\x7b[A-Z][A-Z0-9_][A-Z0-9_]+\x7d|\x7b[^\x7b\x7d\n]*\s[^\x7b\x7d\n]*\x7d")

def sem_codigo(texto: str) -> str:
    return CRASE.sub("", CERCA.sub("", texto))

def secao(texto: str, titulo: str) -> str | None:  # do título até o próximo '## '
    ...

def lint(texto: str) -> list[str]:
    ...  # cada item: "regra: detalhe"

def main(argv: list[str]) -> int:
    if len(argv) != 2 or not Path(argv[1]).is_file():
        print("uso: design-lint.py <DESIGN.md>", file=sys.stderr); return 64
    erros = lint(Path(argv[1]).read_text(encoding="utf-8"))
    for e in erros:
        print("🛑 " + argv[1] + ": " + e, file=sys.stderr)
    if erros:
        print("RESULTADO: VERMELHO", file=sys.stderr)
        print("→ corrija o DESIGN nos pontos acima e rode de novo", file=sys.stderr)
        return 1
    print("✅ " + argv[1] + ": DESIGN válido"); return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
```

### Pattern 4: Mutação de fixture nos testes

```python
CASOS = {
    "decisao_em_portugues": ("### Decision 1: ", "### Decisão 1: "),
    "total_errado": ("**Total Files:** 3", "**Total Files:** 4"),
}

def test_mutacoes_reprovam(self):
    base = FIXTURE.read_text(encoding="utf-8")
    for nome, (de, para) in CASOS.items():
        with self.subTest(caso=nome):
            self.assertIn(de, base)                    # a mutação tem de achar o que trocar
            p = self.escreve(self.tmp, "DESIGN_X.md", base.replace(de, para, 1))
            rc, out, err = self.roda([PYTHON, "-B", SCRIPT, p], self.tmp)
            self.assertEqual(rc, 1, out + err)
```

---

## Data Flow

```text
1. Aluno chama a skill → o agente lê SKILL.md (seção + tabela) → lê references/como-falar.md
   → responde: [identificação na 1ª vez] · Status · O que foi feito · Agora · Sua decisão · Próximo passo
2. Decisão → formato do PERGUNTA_DECISAO.md (recomendada 1ª, não sei, sem Outro) → resposta do aluno
   → eco em 1 linha no "O que foi feito" seguinte | resposta fora das opções → dúvida + opções de novo
3. Bloqueio → parada ⏸️ (motivo, onde, passos, o que não foi feito, Brief:/Sessão nova: se houver)
4. sdd-design grava DESIGN → design-lint (0 segue · 1 corrige e roda de novo)
   sdd-handoff grava HANDOFF → handoff-lint (0 · 1)
5. Pacote: PR → CI skill-lint --conversa + unittest (ubuntu, macOS piso) → push main → release
```

Caminho de erro: o `skill-lint --conversa` vermelho no CI bloqueia o PR. O lint vermelho dentro da skill impede a entrega do documento, e a skill corrige e roda de novo, sem pedir OK.

---

## Integration Points

| External System | Integration Type | Authentication |
|-----------------|-----------------|----------------|
| GitHub Actions (`publish-gate.yml`, `release.yml`) | Passo de CI alterado (`--conversa`) | `GITHUB_TOKEN` do workflow, sem mudança. Falha = PR vermelho, sem retry automático |
| Agente do aluno (qualquer um dos 5 vendors do `init`) | Lê `SKILL.md` e `references/` | N/A. Se não abrir a referência, as regras do `SKILL.md` continuam valendo |

---

## Testing Strategy

| Test Type | Scope | Files | Tools | Coverage Goal |
|-----------|-------|-------|-------|---------------|
| Unit (contrato de script) | `skill-lint --conversa`, `design-lint`, `handoff-lint` | `tests/test_skill_lint.py`, `test_design_lint.py`, `test_handoff_lint.py` | unittest + `apoio.Sandbox` | AT-001–AT-005, AT-008, AT-009, AT-011–AT-013: todo caso vermelho do DEFINE com 1 teste nomeado |
| Contrato de texto | 16 skills, fragmento, design/handoff | `tests/test_conversa.py` | unittest | AT-006, AT-007, AT-014, AT-017 |
| Agnosticismo | Árvore publicada | `tests/test_agnostico.py` | unittest | AT-015; AT-016 pela evidência na `v2.2.4` |
| Regressão | Suíte inteira no piso | `tests/` | `SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover` | AT-020: 326 + novos, 0 falha |
| Evidência fora do gate | Comandos intactos, DESIGNs reais, versões, baseline | `sdd/reports/evidence/F4_CONVERSA/gerar-evidencia.sh` | bash + Python inline + git | AT-010, AT-016, AT-018, AT-019 |
| Sabotagem | 3 scripts + lista do `test_agnostico` | `sdd/reports/evidence/F4_CONVERSA/sabotagem.sh` | sed por padrão + `git checkout` | AT-021: 4 de 4 vermelhas com nome do teste |
| CI | PR | `.github/workflows/*.yml` | GitHub Actions | AT-022: `gate` + `testes-macos` verdes |

Baseline vermelho: os testes 4, 7, 10, 11 e 14 são escritos antes dos scripts, das fixtures e das skills e rodam no HEAD da branch antes do código. O vermelho deles vai para `evidence/F4_CONVERSA/baseline.log`.

---

## Error Handling

| Error Type | Handling Strategy | Retry? |
|------------|-------------------|--------|
| Arquivo ausente ou sem argumento (3 lints) | Mensagem de uso em stderr, exit 64 | No |
| Arquivo não UTF-8 | `🛑 não consegui ler: <erro>`, exit 1 (como o `skill-lint` atual) | No |
| Flag desconhecida no `skill-lint` | Uso em stderr, exit 64 | No |
| Erro interno do lint (exceção) | Não é engolido: traceback e exit ≠ 0 (falha fechado) | No |
| Mutação de teste que não acha o trecho na fixture | `assertIn(de, base)` antes de mutar: a fixture que mudou faz o teste falhar, em vez de passar sem testar | No |
| Exceção não declarada no `comandos-intactos` | `FALHA <skill>` e exit 1; corrigir a skill ou registrar a exceção no BUILD_REPORT, nunca ampliar a lista em silêncio | No |

---

## Configuration

| Config Key | Type | Default | Description |
|------------|------|---------|-------------|
| `--conversa` (flag do `skill-lint.py`) | bool | desligada | Liga a conferência da camada; o CI do pacote liga |
| `ADAPTADORES` (`tests/test_agnostico.py`) | tupla de prefixos | `()` | Caminhos isentos por serem adaptador declarado de vendor |
| `EXCECOES` (`gerar-evidencia.sh`) | dict skill → linhas | design e handoff | Diferenças de comando permitidas |

Nenhum slot novo em `sdd/config.yaml` (Decisão 2 da frente).

---

## Security Considerations

- Texto novo sem Unicode invisível, sem `curl … | sh` literal e sem literal de `publish-gate-patterns.txt`: o CI, o G2 e a conferência de code points depois de escrever.
- Os lints só leem o arquivo indicado, sem rede e sem `eval`.
- Nenhum exemplo de `como-falar.md` traz dado real de pessoa ou empresa.

---

## Observability

- Os lints terminam com `RESULTADO:` + `→` no vermelho e `✅` no verde, a mesma convenção de `docs/cli-conventions.md`.
- Evidência em `sdd/reports/evidence/F4_CONVERSA/`:
  - `baseline.log`, `GATE.log`, `suite-piso.log`, `check-versions.log`;
  - `comandos-intactos.log`, `design-lint-reais.log`;
  - `sabotagem.log`, `codepoints.log`, `ci-pr.log`.

---

## Requirements Traceability

| Requirement / AT | Design Element | Test / Gate |
|---|---|---|
| MUST seção nas 14 / AT-001, AT-006 | Decision 1; manifest 15–28; Pattern 1 | `tests/test_skill_lint.py`, `tests/test_conversa.py` |
| MUST `como-falar.md` / AT-004, AT-005 | Decision 2; Pattern 2; manifest 15–28 | `tests/test_skill_lint.py` (16 reais com `--conversa`) |
| MUST Status sem banner, Próximo passo ≤100 / AT-005, AT-006 | Decision 1; Pattern 1 | `tests/test_conversa.py`, `tests/test_skill_lint.py` |
| MUST fragmento / AT-007 | manifest 1 | `tests/test_conversa.py` |
| MUST `--conversa` e fixtures / AT-001–AT-005 | Decisions 2, 3; manifest 2–4 | `tests/test_skill_lint.py` |
| MUST `design-lint` / AT-008–AT-010, AT-013 | Decision 4; manifest 5–7 | `tests/test_design_lint.py`; `evidence/F4_CONVERSA/design-lint-reais.log` |
| MUST `handoff-lint` / AT-011–AT-013 | Decision 5; manifest 8–10 | `tests/test_handoff_lint.py` |
| MUST lint na design/handoff / AT-014 | Decision 7; manifest 17, 19 | `tests/test_conversa.py` |
| MUST agnosticismo / AT-015, AT-016 | Decision 6; manifest 11–13 | `tests/test_agnostico.py`; `evidence/F4_CONVERSA/baseline.log` |
| MUST versões e identificação / AT-017, AT-019 | Decision 10; manifest 15–31 | `tests/test_conversa.py`; `evidence/F4_CONVERSA/check-versions.log` |
| MUST comandos intactos / AT-018 | Decisions 7, 8, 9 | `evidence/F4_CONVERSA/comandos-intactos.log` |
| MUST não regressão / AT-020 | manifest 29–31, 33; nada em `verify-gate.sh`/`report-lint.py`/`playbook-lint.sh`/`publish-gate.sh` | Verify Gate (suíte no piso) |
| MUST sabotagem / AT-021 | Testing Strategy (Sabotagem) | `evidence/F4_CONVERSA/sabotagem.log` |
| CI / AT-022 | manifest 32, 33 | CI do PR (`gate`, `testes-macos`) |

---

## Risks and Mitigations

| Risk | Impact | Mitigation | Residual Risk |
|---|---|---|---|
| O bloco comum, copiado 14 vezes, diverge numa edição futura | A camada fica inconsistente entre as skills | `FRASES` do `test_conversa` nas 14 | Uma frase fora da lista pode divergir: aceito |
| O `--conversa` reprova as 2 skills portadas (Grupo 1) | CI vermelho por algo fora de escopo | Regras da Decisão 2 tiradas do texto real delas; rodar o lint nas 16 antes de mexer nas 14 | Nenhum |
| O placeholder do `design-lint` reprova um DESIGN real por `<F>` em crase | Falso vermelho na `sdd-design` | Código (cerca e crase) é tirado antes; AT-010 roda nos 3 DESIGN reais | Placeholder em prosa sem crase reprova: é o que se quer |
| A seção nova empurra um título de passo ou um comando para outro lugar | Ordem dos passos muda sem ninguém ver | `comandos-intactos.log` por skill com exceções fechadas (Decision 9) | Nenhum |
| Unicode invisível ou literal do G2 no texto novo | CI vermelho ou vazamento | Conferência de code points (`codepoints.log`), G2 no gate | Nenhum |
| O agente ignora a camada | Aluno continua recebendo relatório técnico | As regras ficam no `SKILL.md`, não só na referência | Não verificável em teste: pendência no handoff (A-002) |

---

## Advisor Ledger

None — no formal external design review. A revisão de contexto fresco do build vai para o BUILD_REPORT.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-10-29 | SDD Design by RDD | Initial version |
| 1.1 | 2026-10-29 | SDD Build by RDD | Revisão de contexto fresco de `4e77a1f` (0 HIGH, 4 MEDIUM, 8 LOW). Decisão 2: opções também depois de linha em branco e com `*`; rótulo que começa por Outro/Outra; Próximo passo também como `**Próximo passo:**` e em citação; seção dentro de bloco de código não conta; sem a flag, a mensagem do frontmatter é a da v2.2.4. Decisão 4: `« »` não é placeholder; arquivo ilegível sai 1 com `RESULTADO:`. Decisão 5: a seção do prompt é delimitada sem os blocos de código (`## ` dentro do prompt não a encerra); ficha com Status ✅ dispensa o prompt. Decisão 6: todo arquivo de texto do escopo, com ou sem extensão; `Task tool`/`Agent tool` sem caixa. Identificação vem antes do Status na 1ª resposta. Ciclo 2 (PASS, 6 LOW): `>` vazio na citação e plural Outros/Outras no `skill-lint`; ✅ como 1º símbolo do Status no `handoff-lint`; texto não-UTF-8 é achado no `test_agnostico` (falha fechado), binário (com NUL) é pulado; corpo do DESIGN alinhado ao código |

---

## Next Step

Execute o **SDD Build by RDD**.
