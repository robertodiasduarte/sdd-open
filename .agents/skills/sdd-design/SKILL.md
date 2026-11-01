---
name: sdd-design
description: Fase 2 do SDD Open — cria a arquitetura e a especificação técnica numa passada só, com decisões registradas (ADRs inline), manifest de arquivos, varredura de landmines do playbook por superfície, padrões de código prontos para copiar e estratégia de testes, gravando sdd/features/DESIGN_{FEATURE}.md. Use quando o DEFINE estiver pronto ou o usuário disser /sdd-design.
compatibility: Requer bash >= 3.2 e git >= 2.20; roda sdd/bin/playbook-lint.sh --grep por superfície do manifest.
license: MIT
metadata:
  author: Roberto Dias Duarte
  version: "2.3.0"
  updated: "2026-10"
  fase: "2"
---

# sdd-design — Fase 2

Na primeira resposta desta skill, comece com esta linha, uma vez só, antes do Status:
`sdd-design v2.3.0 · out/2026 · versão atual: https://github.com/robertodiasduarte/sdd-open/releases/latest`

Plano + especificação + decisões num documento. O DESIGN diz **como** construir o que o
DEFINE contratou — e é o último ponto em que mudar de abordagem é barato.

## Como falar com o aluno

Leia `references/como-falar.md` antes da primeira resposta: o glossário desta skill, o Status preenchido
e um exemplo completo. Pergunta e parada seguem `sdd/templates/fragments/PERGUNTA_DECISAO.md`.
Quem usa esta skill, em geral, nunca usou git nem terminal.

| Etapa | Nome para o aluno | Passos desta skill |
|---|---|---|
| 1 | Ler | 1 |
| 2 | Decisões | 2 e 3 |
| 3 | Componentes e arquivos | 4 e 4.5 |
| 4 | Fluxo, testes e erros | 5, 5.5 e 6 |
| 5 | Gravar | 7 |
| 6 | Conferir | 8 |

Toda resposta, nesta ordem (pule a parte sem conteúdo):

1. **Status** — uma linha que começa pelo nome da fase: `Design: ✅ 1 Ler · ▶️ 2 Decisões · ⬜ 3 Componentes e arquivos · ⬜ 4 Fluxo, testes e erros · ⬜ 5 Gravar · ⬜ 6 Conferir`
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
flag neste DESIGN (anotando em Revision History). Com o encadeamento ligado
(`bash sdd/bin/sdd-fluxo.sh estado` sai 0), essas perguntas são de rotina: flag ausente vira `true`
(o lado conservador), re-check com hits vira `true`, e os ajustes de verificabilidade que a revisão do
DESIGN propõe (o contrato de aceite, `sdd-build/references/contexto-fresco.md`, modo `contrato`) são aceitos; cada uma vira uma linha `[auto] <decisão> — porque <…> · para
desfazer: <…>` em Revision History e no recibo **Decidi sozinho**. Desligado, essas perguntas são
feitas como hoje, com a marca `[auto · de rotina]`.

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

### 8. Conferir

`python3 sdd/bin/design-lint.py sdd/features/DESIGN_{FEATURE}.md` sobre o arquivo gravado: títulos
`### Decision N: <nome>` em sequência, `**Total Files:**` igual às linhas do manifest, dependências sem
ciclo, nenhum placeholder. Vermelho ⇒ corrija o DESIGN e rode de novo antes de entregar.

## Review adversarial do DESIGN (recomendado)

É o ponto de **maior retorno** de uma revisão externa: mudar a abordagem custa pouco aqui e
muito depois do código. Uma engine do registry **revisa** o DESIGN e **outra audita** a revisão, em
cadeia — o revisor primeiro, o auditor depois, nunca os dois em paralelo (dois revisores lado a lado
acham menos que revisor e auditor encadeados). Commite o DEFINE e o DESIGN antes e rode:

```bash
bash sdd/bin/adversarial-review.sh --feature {FEATURE} \
  --paths "sdd/features/DEFINE_{FEATURE}.md sdd/features/DESIGN_{FEATURE}.md"
```

As engines vêm de `review.revisor1` e `review.auditor` (`sdd/config.yaml`); vazios, pergunte à pessoa
quais usar. Exit 0 ⇒ passe a pasta ao `bash sdd/bin/sdd-fluxo.sh loop --review <pasta> …`; 65 a 68 ⇒
repasse o `RESULTADO:` e o `→` (credencial, CLI ausente, auditor igual ao revisor, resposta fora do
formato — que nunca é "zero achados"). O contrato de resposta segue
`sdd/templates/fragments/ADVISOR_CONSULT.md`. Toda nota recebe **APLICADA ·
REBATIDA_EVIDENCIA (com arquivo:linha) · REBATIDA_ESCOPO** no Advisor Ledger do DESIGN.
Nunca descartada em silêncio. Com uma engine só, rode com `--um-engine`: a revisão registra
`diversidade: nenhuma` — mais fraca, mas honesta. Sem engine nenhuma, use uma **sessão nova** do
agente como revisor. Se esta sessão não abre o papel fresco
sozinha, grave o brief em `sdd/reports/briefs/BRIEF_revisor-design_{FEATURE}.md`, rode
`bash sdd/bin/sdd-fluxo.sh despachar revisor-design {FEATURE} sdd/reports/briefs/BRIEF_revisor-design_{FEATURE}.md`
e pare no exit 40, repassando a parada que ele imprime. Se a revisão é exigida:
`bash sdd/bin/sdd-fluxo.sh review-design sdd/features/DESIGN_{FEATURE}.md` (0 exigida · 1 dispensável ·
64 manifest ilegível: rode assim mesmo e registre o motivo).

## Quality Gate

```text
[ ] Diagrama claro · decisões com rationale · manifest completo, sem ciclos
[ ] ## Landmines aplicáveis presente (✔ tratado / N.A. por achado, ou "0 aplicáveis")
[ ] Code patterns prontos para copiar; padrões canônicos citados ou candidato registrado
[ ] Estratégia de testes cobre todos os ATs
[ ] LLM Prompts: se true, inventário 100% + contrato por linha; se false, re-check com zero hits
[ ] Resposta fechada com o resumo de etapa (fragments/RESUMO_ETAPA.md)
```

## Por que cada regra existe

- **Títulos `### Decision N:` fixos** — outras ferramentas leem as decisões por esse título; renomear
  para "Decisão 1" ou "ADR-1" faz o `design-lint` reprovar e quem lê as decisões deixar de achá-las.
- **Manifest sem ciclo e com `Total Files`** — com dependência circular não existe ordem de build
  possível; o total confere que nenhuma linha se perdeu.
- **Varredura de landmines sempre registrada, mesmo com 0 achados** — "0 aplicáveis" escrito prova que
  a varredura rodou; a seção ausente não distingue "rodou e não achou" de "esqueceu".
- **O DESIGN não escreve o prompt de produção** — escreve o contrato (tom, saída, fallback); o texto
  final sai no Build, pela skill de prompt, em vez de virar rascunho congelado no documento.
- **Revisão por outro vendor aqui, antes do código** — é o último ponto em que mudar de abordagem custa
  uma edição de texto; depois do build, custa reescrever.
- **`design-lint` no arquivo gravado** — conferir o rascunho na conversa não prova o arquivo que o Build
  vai ler.

## Encerramento (obrigatório)

Feche com o **resumo de etapa** (`sdd/templates/fragments/RESUMO_ETAPA.md`); o 🏃 é
`/sdd-design`.

**Próximo passo:** `/sdd-build sdd/features/DESIGN_{FEATURE}.md`

### Fluxo encadeado

Ao fechar, rode `bash sdd/bin/sdd-fluxo.sh seguir <fase> <DEFINE> <próxima>` só quando a linha
"Nesta skill" abaixo nomeia o `seguir` (contrato em `sdd/templates/fragments/FLUXO_ENCADEADO.md`).
Exit 0: escreva a linha de transição que o script imprimiu, o recibo **Decidi sozinho** (se houver) e
chame a próxima fase nesta sessão. Exit 1 com `encadeamento desligado`: só o Próximo passo acima, sem
repassar a linha. Exit 1 por outro motivo: diga o motivo em 1 frase e mostre o Próximo passo. Exit 64:
repasse a saída e trate como desligado. A pergunta `[auto · de rotina]` com o encadeamento ligado
vira a opção recomendada e uma linha do recibo; as marcadas D1 a D5 continuam perguntadas. "Pare"
desliga nesta chamada (`--parar`).

Nesta skill: `seguir design sdd/features/DEFINE_{FEATURE}.md build`, depois da revisão do DESIGN
quando `bash sdd/bin/sdd-fluxo.sh review-design sdd/features/DESIGN_{FEATURE}.md` diz que ela é
exigida (exit 0 ou 64); o `seguir` confere que ela foi registrada no Advisor Ledger.

---

Parte do SDD Open by RDD — https://github.com/robertodiasduarte/sdd-open
