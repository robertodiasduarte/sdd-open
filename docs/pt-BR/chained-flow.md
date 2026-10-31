<!-- Idioma: [English](../chained-flow.md) · **Português** -->

# Fluxo encadeado

Cada pergunta que uma skill faz leva a **classe da decisão**, e um script (`sdd/bin/sdd-fluxo.sh`) decide
por código de saída o que antes era decidido por leitura de texto: se um DESIGN precisa de revisão, se o
loop de revisão convergiu, se a fase seguinte pode começar sem perguntar e quando parar para uma sessão
nova do agente. Com o encadeamento ligado, o SDD segue sozinho com o gate verde e só para quando a decisão
é sua.

## Ligado e desligado

| | `flow.autonomous: false` (default) | `flow.autonomous: true` |
|---|---|---|
| Fim de cada fase | o Próximo passo de sempre | se tudo está pronto, a fase seguinte começa nesta sessão, depois da linha de transição |
| Pergunta `[auto · de rotina]` | é feita | vale a opção recomendada, e a decisão vai para o recibo **Decidi sozinho** |
| Perguntas `[D1]` a `[D5]` | são feitas | são feitas |
| Release | você pede | você pede: publicar não se desfaz e nunca começa sozinho |

Para ligar, troque `autonomous: false` por `true` no bloco `flow:` de `sdd/config.yaml`. Para parar uma vez,
diga "pare" à skill (ela passa `--parar`). Para conferir: `bash sdd/bin/sdd-fluxo.sh estado` (`0` ligado ·
`1` desligado · `64` valor que não é `true` nem `false`, tratado como desligado).

## As marcas

| Marca | Quando | Com o encadeamento ligado |
|---|---|---|
| `[D1 · não se desfaz]` | publicar, enviar, apagar, comprar, usar credencial | pergunta |
| `[D2 · muda o produto]` | escopo, regra de negócio, texto que a pessoa lê, dúvida do DEFINE | pergunta |
| `[D3 · muda a regra do método]` | playbook, gate, dispensar uma revisão | pergunta |
| `[D4 · limite de tentativas]` | o loop de revisão não convergiu (3 rodadas ou 2 ciclos do avaliador) | pergunta |
| `[D5 · provas em conflito]` | um achado grave refutado com evidência | pergunta |
| `[auto · de rotina]` | a recomendada resolve: modo de execução, onde gravar, formato | não pergunta |

A tabela é do `sdd/templates/fragments/PERGUNTA_DECISAO.md` (item 9). O
`bash sdd/bin/sdd-decisoes-lint.sh --sites .agents/skills sdd/templates/fragments` confere que toda
pergunta de decisão tem uma marca com o rótulo certo, uma opção recomendada e a primeira, "não sei" e
nenhuma opção "Outro".

## A linha de transição e o recibo

```text
✅ DEFINE pronto → seguindo para o DESIGN (encadeamento ligado em sdd/config.yaml)
→ /sdd-design sdd/features/DEFINE_PAGAMENTOS.md
```

`sdd-fluxo.sh seguir <fase> <DEFINE> <próxima>` só imprime essa linha (exit `0`) quando o encadeamento
está ligado, o documento da fase está em `Ready for …`, o bloco do Verify Gate é válido, não há dúvida
aberta no DEFINE e, no DESIGN, a revisão exigida está registrada no Advisor Ledger sem nota HIGH aberta.
Senão, sai `1` com o motivo (`PARAR: …`) e a skill mostra o Próximo passo. Antes da linha, o resumo da
fase traz o recibo:

```text
**Decidi sozinho:**
- Tratei o flag LLM Prompts como true — porque o DEFINE não dizia · para desfazer: escreva false no DEFINE e rode o Design de novo
```

## A parada para uma sessão nova (exit 40)

O avaliador do build e o revisor do DESIGN precisam de alguém que não viu a conversa. Quando o agente
abre esse papel sozinho, ele o faz. Quando não abre (ou está com essa capacidade desligada), a skill grava
o brief e roda `sdd-fluxo.sh despachar <papel> <FEATURE> <brief>`, que copia o brief para
`sdd/reports/briefs/BRIEF_<papel>_<FEATURE>.md`, imprime a parada ⏸️ com os passos e o que colar de
volta, e sai `40 AGUARDANDO_HUMANO`. Nada é publicado; a sessão de origem continua quando você cola o
retorno.

## Os verbos

| Verbo | Exits |
|---|---|
| `review-design <DESIGN>` | `0` EXIGIDO (≥ 3 arquivos novos no File Manifest, ou superfície de segurança: termo fixo, `review.security_globs` ou `layers.sql`) · `1` DISPENSAVEL · `64` manifest ilegível (rode a revisão assim mesmo) |
| `loop --review <dir> --ledger <arq> --rodada N` | `0` PRONTO · `10` CONTINUAR · `20` BLOQUEADO · `30` AGUARDANDO_RECIBO · `64` entrada ausente ou ilegível; grave com `--log`, nunca com `\| tee` |
| `despachar <papel> <FEATURE> <brief>` | `40` AGUARDANDO_HUMANO · `64` |
| `seguir <fase> <DEFINE> <próxima>` | `0` SEGUIR · `1` PARAR · `64` |
| `estado` | `0` ligado · `1` desligado · `64` valor inválido |
| `--self-test` | `0` quando todos os cenários batem |

O `loop` é o decisor da revisão adversarial depois do build; quem o chama é a frente que liga essa
revisão às skills.

## Limite: projeto que já tinha o pacote

Em `sdd/bin/` e `sdd/templates/`, o `init` acrescenta só o arquivo que falta e nunca sobrescreve o que já
existe; `sdd/fixtures/` é copiada só na primeira instalação. Num projeto que instalou o pacote antes desta
versão, os dois scripts e o `FLUXO_ENCADEADO.md` chegam, mas `sdd/fixtures/fluxo/` e
`sdd/fixtures/conversa/decisoes/` não (o `--self-test` dos dois scripts sai `64` nomeando a pasta) e o
`sdd/templates/fragments/PERGUNTA_DECISAO.md` continua com o item 9 antigo (o lint sai `64`: tabela das
marcas ausente). Copie esses arquivos do pacote para ter as marcas e os autotestes.
