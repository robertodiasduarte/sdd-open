# Fragment: ADVISOR CONSULT — contrato do review adversarial de 2º vendor

> **Uso:** sempre que uma consulta formal ao advisor (review de 2º vendor) for disparada
> nos pontos do SDD — DESIGN pré-build (`design.md`), rescue de gate teimoso (`build.md`),
> review pré-release (`release.md`). O **QUANDO** consultar é política própria
> (memória `feedback_codex_review_quando_vale`); este fragment define o **FORMATO** da
> consulta, da resposta e da disposição das notas.
> Consulta informal/exploratória continua livre — o contrato vale para os pontos formais.

---

## 1. O que vai NA consulta (compilado pelo orquestrador)

```markdown
TIPO: plan-review (DESIGN pré-build) | delivery-review (pós-build/pré-release)
      | conflito (resultados se contradizem) | judgment call
TAREFA + CRITÉRIOS DE SUCESSO: {colados do DEFINE — Verify Gate + acceptance criteria}
PERGUNTA: {UMA pergunta focada — nunca "revise tudo"}
MATERIAL: {o diff/DESIGN/output, inline}
```

Uma consulta = uma pergunta. Se há duas perguntas, são duas consultas (ou a segunda não
merecia o advisor).

## 2. Formato de resposta EXIGIDO (anexar verbatim ao prompt do advisor)

```text
Responda EXATAMENTE neste formato, máximo 300 palavras no total:

1. VERDICT — 1 linha (ex.: "shippable com 1 fix" / "não shipe: risco X" /
   "abordagem errada: reconsiderar Y").
2. TOP RISKS — 1 a 3 pontos de falha, RANQUEADOS por severidade. Nunca mais de 3.
3. SPECIFIC FIXES — mudanças concretas, citando arquivo/linha/trecho. Nada vago.
4. WHAT TO IGNORE — o que está sendo superestimado e NÃO deve virar trabalho.

Não reescreva o material. Não elogie (se está bom, 1 linha no VERDICT basta).
Gaste palavras apenas onde elas mudam uma decisão.
```

**Por quê este formato:** o teto de 3 risks força ranqueamento (o HIGH não se perde no meio
de 15 nits); o `WHAT TO IGNORE` auto-calibra o reviewer — é difícil inflar achados quando a
própria resposta precisa declarar quais não importam.

## 3. Disposição das notas (obrigatória — Advisor Ledger)

**Toda nota do advisor recebe UM dos três vereditos, por escrito. Nunca descartada em silêncio.**

Tabela no report da fase (BUILD_REPORT / relatório do release / DESIGN changelog):

```markdown
### Advisor Ledger

| # | Nota | Severidade | Veredito | Evidência |
|---|------|-----------|----------|-----------|
| 1 | {resumo 1 linha} | HIGH | APLICADA | commit `abc123` |
| 2 | {resumo 1 linha} | MED  | REBATIDA_EVIDENCIA | `scripts/x.sh:42` — a linha já trata o caso |
| 3 | {resumo 1 linha} | LOW  | REBATIDA_ESCOPO | fora do slice; backlog: {onde ficou registrado} |
```

### Os três vereditos (ônus de prova SIMÉTRICO)

| Veredito | Quando | Evidência EXIGIDA |
|---|---|---|
| **APLICADA** | a nota procede e virou mudança | commit/arquivo do fix, ou item de checklist/automação criado (MED/LOW vira fix, automação ou checklist — nunca "aceito e esquecido") |
| **REBATIDA_EVIDENCIA** | a nota é falsa ou mal caracterizada, e **existe código que a contradiz** | **`arquivo:linha` obrigatório** apontando o trecho que refuta. Sem citação, este veredito é proibido |
| **REBATIDA_ESCOPO** | a nota procede mas está **fora do slice** | **item de backlog criado**, com onde foi registrado. Nunca é descarte |

**Por que três, e por que evidência dos dois lados:** o formato anterior (`APLICADA｜REBATIDA`)
era assimétrico — acusar exigia `arquivo:linha`, mas rebater bastava "motivo de 1 linha". É o
**Caso B** medido no paper Adversarial Review (arXiv:2608.18167): o crítico cede a uma rebatida
fraca e o bug real some do processo (F1 despenca para 0.286). Restringir o veredito a três
opções com ônus simétrico é a correção medida no paper — F1 0.457 → 0.533 com a **mesma** dupla
revisor+auditor. Custa uma linha a mais de disciplina e impede que "não é bem assim" enterre
um achado válido.

**Regra de rebaixamento:** se você escreveu `REBATIDA_EVIDENCIA` mas não consegue citar
`arquivo:linha` que contradiga, o veredito correto é `REBATIDA_ESCOPO` (se for escopo) ou
`APLICADA` (se, no fundo, a nota procede). Discordância sem evidência não é neutra — é a
falha que este ledger existe para prevenir.

- Itens do bloco `WHAT TO IGNORE` do advisor não entram no ledger (já são a disposição deles).
- Uma nota rebatida hoje, com evidência registrada, é ouro quando o mesmo tema reaparece.

## 4. Proveniência do engine (obrigatória quando houve fallback)

O `/adversarial-review` declara em `META.txt` e no cabeçalho do relatório qual engine rodou
cada papel. **Se o engine default não rodou, o ledger diz isso** — uma linha antes da tabela:

```markdown
> ⚠️ Fallback de engine: o auditor default (`codex`) não rodou (PERSISTENTE: quota).
> Esta auditoria foi produzida por `grok`.
```

Silenciar a troca transforma o ledger em falso-verde: um artefato auditado por um engine de
reserva parece idêntico a um auditado pelo default medido. Mesmo princípio do precedente
provedor de mensageria — aceitação registrada não é entrega.
