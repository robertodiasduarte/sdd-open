---
name: sdd-design
description: Fase 2 do SDD Open — cria a arquitetura e a especificação técnica numa passada só, com decisões registradas (ADRs inline), manifest de arquivos, varredura de landmines do playbook por superfície, padrões de código prontos para copiar e estratégia de testes, gravando sdd/features/DESIGN_{FEATURE}.md. Use quando o DEFINE estiver pronto ou o usuário disser /sdd-design.
compatibility: Requer bash >= 3.2 e git >= 2.20; roda sdd/bin/playbook-lint.sh --grep por superfície do manifest.
license: MIT
metadata:
  author: RDD
  version: "2.0.0"
  fase: "2"
---

# sdd-design — Fase 2

> Abra a resposta com o banner: `🧠 DESIGN (Fase 2)`.

Plano + especificação + decisões num documento. O DESIGN diz **como** construir o que o
DEFINE contratou — e é o último ponto em que mudar de abordagem é barato.

## Entrada

`/sdd-design sdd/features/DEFINE_{FEATURE}.md`

## Processo

### 1. Contexto

Leia o DEFINE, o `UX_REVIEW_{FEATURE}.md` se existir, `sdd/templates/DESIGN_TEMPLATE.md`,
`AGENTS.md`, `sdd/config.yaml` (camadas em `layers:`) e `## Sempre` do playbook. Explore o
código: como o projeto já resolve problemas parecidos? Que convenções valem?

Extraia o flag **LLM Prompts** do DEFINE. Ausente ou em branco → ambíguo: pergunte antes de
seguir. Com `false`, rode um re-check silencioso (nomes de provedor, "prompt", paths de
prompt no escopo); hits → pergunte: corrigir o DEFINE, confirmar falso positivo, ou virar o
flag neste DESIGN (anotando em Revision History).

### 2. Arquitetura

Diagrama ASCII do sistema, componentes, fluxo de dados, pontos de integração externos.
Diagrama primeiro: desenhar clareia o pensamento.

### 3. Decisões (ADRs inline)

Para cada escolha significativa:

```markdown
### Decision N: {Nome}
| **Status** | Accepted | · | **Date** | YYYY-MM-DD |
**Context:** por que a decisão foi necessária
**Choice:** o que fazemos
**Rationale:** por quê
**Alternatives Rejected:** 1. … — rejeitada porque … · 2. …
**Consequences:** o trade-off que aceitamos · o que ganhamos
```

Decisões são permanentes: documente o **porquê**, não só o quê.

### 4. File Manifest

| # | Arquivo | Ação | Propósito | Dependências |
|---|---|---|---|---|

Todo arquivo a criar ou modificar. Sem dependência circular. Cada arquivo deve funcionar
sozinho.

### 4.5. Varredura de landmines (obrigatória, read-only)

Para cada superfície do manifest (nome de arquivo, tabela, comando, conceito central):

```bash
sdd/bin/playbook-lint.sh --grep "<termo>" sdd/playbook.md   # exit 1 = 0 hits (normal)
```

Toda landmine que casar entra na seção **`## Landmines aplicáveis`** com veredito
**✔ tratado** (como, ou qual arquivo do manifest trata) ou **N.A.** (por que não se aplica).
Zero achados → `varredura rodada em YYYY-MM-DD, 0 aplicáveis`. **Nunca omita a seção.**
Nunca escreva no playbook a partir daqui.

### 5. Code Patterns

Snippets prontos para copiar dos padrões-chave. Se o projeto tem padrões canônicos
(`sdd/patterns/` ou equivalente), **cite-os** e declare o que foi adaptado. Se não tem,
escreva o snippet e registre `candidato a pattern: <camada>`.

### 5.5. LLM Prompts (só se `true`)

Inventário: 1 linha por prompt de produção previsto (arquivo do manifest, tipo `one-shot` ×
`loop` — o processo re-prompta o modelo com base na própria saída anterior? então `loop`),
e um contrato por prompt: tom/audiência do DEFINE, formato de saída derivado do consumidor,
fallback aprovado, material de referência concreto, provedor/modelo já decididos. Não
escreva o prompt aqui: a fase Build o produz com o contrato em mãos.

### 6. Estratégia de testes

| Tipo | Escopo | Ferramenta | Meta |
|---|---|---|---|

Cubra cada AT do DEFINE. O gate composto (se houver) é listado aqui com um bloco por AT.

### 7. Gravar

`sdd/features/DESIGN_{FEATURE}.md`, Status `Ready for Build`.

## Review adversarial do DESIGN (recomendado)

É o ponto de **maior retorno** de uma revisão externa: mudar a abordagem custa pouco aqui e
muito depois do código. Peça a um **segundo vendor** (agente de outra família de modelos) que
revise o DESIGN com o contrato de `sdd/templates/fragments/ADVISOR_CONSULT.md` — veredito,
≤3 riscos ranqueados, correções específicas, o que ignorar. Toda nota recebe **APLICADA ·
REBATIDA_EVIDENCIA (com arquivo:linha) · REBATIDA_ESCOPO** no Advisor Ledger do DESIGN.
Nunca descartada em silêncio. Com um vendor só, use uma **sessão nova** do mesmo agente e
registre `diversidade: nenhuma` — mais fraco, mas honesto.

## Quality Gate

```text
[ ] Diagrama claro · decisões com rationale · manifest completo, sem ciclos
[ ] ## Landmines aplicáveis presente (✔ tratado / N.A. por achado, ou "0 aplicáveis")
[ ] Code patterns prontos para copiar; padrões canônicos citados ou candidato registrado
[ ] Estratégia de testes cobre todos os ATs
[ ] LLM Prompts: se true, inventário 100% + contrato por linha; se false, re-check com zero hits
[ ] Resposta fechada com o resumo de etapa (fragments/RESUMO_ETAPA.md)
```

## Encerramento (obrigatório)

Feche com o **resumo de etapa** (`sdd/templates/fragments/RESUMO_ETAPA.md`); o 🏃 é
`/sdd-design`.

**Próximo passo:** `/sdd-build sdd/features/DESIGN_{FEATURE}.md`
