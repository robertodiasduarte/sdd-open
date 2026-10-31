# Fragmento — Fluxo encadeado (o SDD só para para pedir decisão)

> Reusável. **Dono único** de: ordem das fases, quando uma fase chama a seguinte, linha de transição,
> recibo "Decidi sozinho", paradas que não são decisão e teto do loop de revisão. Lido pela subseção
> `### Fluxo encadeado` das skills de fase. As marcas de classe (`[D1 · não se desfaz]` …) e o formato
> de pergunta e de parada são do `PERGUNTA_DECISAO.md`. Os decisores são de `sdd/bin/sdd-fluxo.sh`.

## Por que existe

Cada fase terminava com "Próximo passo: rode a fase seguinte" e várias perguntavam "posso seguir?".
Quem liga o encadeamento quer o contrário: o SDD segue sozinho e **só interrompe quando a decisão é da
pessoa**. O risco do outro lado é a opacidade: um fluxo que não pergunta precisa dizer onde está, por que
não perguntou e o que decidiu sozinho.

## Ligar e desligar

- `flow.autonomous: false` (default, em `sdd/config.yaml`): nada encadeia; toda pergunta é feita, com a
  marca da classe. É o comportamento de sempre.
- `flow.autonomous: true`: a fase seguinte é chamada na mesma sessão quando o `seguir` sai 0; a pergunta
  `[auto · de rotina]` vira a opção recomendada e uma linha do recibo; as marcadas D1 a D5 continuam
  perguntadas.
- "Pare", numa fase, desliga só naquela chamada (`--parar`).
- Quem decide é o script: `bash sdd/bin/sdd-fluxo.sh estado` (0 ligado · 1 desligado · 64 valor inválido).

## A ordem

```text
define → (governanca, se dinheiro/tributo/dado pessoal) → (ux-review, se há interface) → design
       → revisão do DESIGN (se review-design diz EXIGIDO) → build → ⏸️ release (sempre pergunta: D1)
```

- **`seguir <fase> <DEFINE> <próxima>`** sai 0 só com o encadeamento ligado, `verify-gate.sh --print`
  0 no DEFINE, nenhum marcador de clarificação aberto e, na fase design, o `design-lint.py` 0 no DESIGN.
  Pares válidos: define → governanca, ux-review ou design · governanca → ux-review ou design ·
  ux-review → design · design → build · qualquer → release (sempre PARAR).
- **`review-design <DESIGN>`**: exit 0 EXIGIDO ⇒ a revisão de contexto fresco roda; exit 1 DISPENSAVEL ⇒
  segue sem rodar; exit 64 (manifest ilegível) ⇒ roda (default seguro) e registra. Dispensar um
  EXIGIDO é decisão da pessoa (D3).
- Brainstorm, iterate, new-session e release não encadeiam: o brainstorm não tem gate; o iterate volta
  à fase do documento; a fase seguinte à new-session roda na pasta nova (troca de janela); publicar é D1.

## Linha de transição

```text
✅ DEFINE pronto → seguindo para o DESIGN (encadeamento ligado em sdd/config.yaml)
→ /sdd-design sdd/features/DEFINE_PAGAMENTOS.md
```

O `seguir` imprime as duas linhas; a skill repassa a primeira, o recibo (se houver) e então chama a
próxima. Vem por último no fim da fase, logo antes da fase seguinte, para não competir com o recibo.
Com `PARAR: encadeamento desligado`, a skill não repassa nada: mostra o Próximo passo de sempre. Com
outro motivo de parar, diz o motivo em uma frase e mostra o Próximo passo.

## Recibo "Decidi sozinho"

No resumo de etapa, depois de "O que vem depois", quando o encadeamento estava ligado e alguma pergunta
`[auto]` foi decidida pela recomendada:

```text
**Decidi sozinho:**
- Gravei o DEFINE com os 6 testes de aceitação — porque o Verify Gate saiu 0 e não havia dúvida aberta · para desfazer: rode a fase Define de novo com "pare"
- Tratei o flag LLM Prompts como true — porque o DEFINE não dizia · para desfazer: escreva false em Technical Context do DEFINE e rode o Design de novo
```

Uma linha por decisão, na ordem em que foram tomadas; mais de 5 ⇒ agrupe por fase. Bloco vazio ⇒
omitido. Sem recibo, decisão automática é decisão invisível. No DESIGN, a mesma linha vai para o
Revision History com o prefixo `[auto]`.

## Paradas que não são decisão

| Parada | Exit | O que a mensagem traz |
|---|---|---|
| Sessão nova para um papel fresco (avaliador, revisor do DESIGN) num agente que não a abre sozinho | `despachar` 40 AGUARDANDO_HUMANO | a parada ⏸️ do `PERGUNTA_DECISAO.md`, o brief em `sdd/reports/briefs/BRIEF_<papel>_<F>.md` e o que colar de volta |
| Avaliador em `PASS_PENDENTE_RECIBO` (gate `manual-ux`) | `loop` 30 AGUARDANDO_RECIBO | o roteiro e "aguardando seu recibo" (`--recibo "nome AAAA-MM-DD"`) |
| Credencial ausente | — | qual credencial e onde ela vive; nada foi feito |

## Loop de revisão (a F10 liga a chamada)

- Teto: **3 rodadas** de revisão pós-build (`sdd-fluxo.sh loop --teto 3`) e **2 ciclos NEEDS_WORK** do
  avaliador. Revisão refeita depois de corrigir achado do avaliador conta rodada.
- Ledger da rodada, 1 linha por achado grave:
  `| <achado> | HIGH | APLICADA \| REBATIDA_EVIDENCIA \| REBATIDA_ESCOPO | rodada=N | <arquivo:linha ou motivo> |`.
  Sem `rodada=N` o decisor ignora a linha: os ids (R1, R2…) recomeçam a cada revisão.
- Grave o resultado com `--log evidence/<F>/LOOP-rodada-N.log`, nunca com `| tee`: o exit de um
  pipeline é o do `tee` (0), e o BLOQUEADO viraria "seguir".
- `BLOQUEADO` por teto ⇒ BUILD_REPORT `Status: Blocked` e **uma** pergunta, com o que foi tentado (n
  rodadas) e cada grave restante em 1 frase com o arquivo:

```markdown
**Sua decisão** — [D4 · limite de tentativas] **A revisão não convergiu em 3 rodadas: como seguimos?**
- **mais 1 rodada com outra abordagem** (recomendado) — mudo o jeito de corrigir os 2 achados restantes e rodo a revisão uma última vez.
- **aceitar e registrar como dívida** — os 2 achados viram pendência visível no relatório e no handoff; nada some.
- **voltar ao DESIGN** — paro o build; o DESIGN é revisto antes de qualquer correção nova.
- **não sei** — explico cada achado restante com o arquivo e o que já foi tentado.
```

- `BLOQUEADO` por impasse de evidência (o auditor refutou um achado grave com prova) ⇒ pergunta
  `[D5 · provas em conflito]` com os dois lados lado a lado.
