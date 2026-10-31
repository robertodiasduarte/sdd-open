# Fragmento — Pergunta de decisão e parada

> Reusável. Lido pelo `references/como-falar.md` de cada skill e pelo bloco "O que precisa de você"
> do `RESUMO_ETAPA.md`. É o **dono único** do formato: as skills apontam para cá e trazem só os
> próprios exemplos. O `sdd/bin/skill-lint.py --conversa` confere as perguntas desses exemplos.

## Por que existe

Quem responde à skill, em geral, nunca usou git nem terminal, e decide sem abrir arquivo. Pergunta sem
opção vira "pode" sem saber o que autoriza; opção sem efeito vira chute; e uma parada sem passos deixa a
pessoa sem saber o que fazer.

## Pergunta de autorização

Quando a skill precisa de um sim, de uma escolha entre caminhos conhecidos ou de um OK antes de algo que
não se desfaz:

```markdown
**Sua decisão** — [auto · de rotina] **Posso gravar o DEFINE com estes 6 testes de aceitação?**
- **sim** (recomendado) — gravo o arquivo e sigo para o Verify Gate: os 6 testes cobrem os 4 objetivos.
- **mostrar antes** — mostro os 6 testes, um por linha, e pergunto de novo.
- **não** — paro aqui; nada é gravado.
- **não sei** — explico o que é um teste de aceitação com o teste 1 como exemplo.
```

1. A pergunta vai em negrito e termina em `?`. Ela é decidível sem abrir arquivo: o contexto necessário
   está na própria resposta.
2. Uma opção por linha, `- **rótulo** — efeito`. O efeito diz o que acontece, não o que a opção "é".
3. A recomendada vem **primeiro**, com `(recomendado)` e o porquê no efeito. Exatamente uma.
4. Números em vez de adjetivos: "6 testes", "3 arquivos", "leva uns 4 minutos"; nunca "alguns", "rápido".
5. Identificadores técnicos (AT-003, LM-004, um SHA) só no fim do efeito, entre parênteses: `(ref: AT-003)`.
   A frase tem de fazer sentido sem eles.
6. Sempre a opção **não sei**: a skill responde à dúvida e repete as opções.
7. Nunca uma opção **Outro** escrita. Quem quer outra coisa diz, e a resposta que não casa com nenhuma
   opção é tratada como dúvida: responder e repetir as opções. Se a ferramenta de pergunta do agente
   acrescentar um campo livre sozinha, ele continua lá; a skill não escreve um.
8. **Eco** de 1 linha: no "O que foi feito" da resposta seguinte, o eco registra a escolha: *"Você escolheu
   **sim**: gravei o DEFINE com os 6 testes."*
9. **Classe da decisão.** Toda pergunta de decisão leva **uma** marca logo antes do negrito, com o
   rótulo fixo da classe (a forma geral, `[Dn]` + rótulo):
   `**Sua decisão** — [D1 · não se desfaz] **Posso publicar estas 5 mudanças?**`. A marca diz o tipo
   da decisão em palavras e se ela continua sendo perguntada com o encadeamento ligado
   (`flow.autonomous: true`; ver `sdd/templates/fragments/FLUXO_ENCADEADO.md`).

   | Marca | Quando | Com o encadeamento ligado |
   |---|---|---|
   | `[D1 · não se desfaz]` | efeito fora da pasta que o git não desfaz: publicar, enviar, apagar, comprar, usar credencial | pergunta |
   | `[D2 · muda o produto]` | muda o que a feature faz ou o texto que a pessoa lê: escopo, regra de negócio, dúvida do DEFINE | pergunta |
   | `[D3 · muda a regra do método]` | muda regra que vale para todas as features: playbook, gate, dispensar uma revisão | pergunta |
   | `[D4 · limite de tentativas]` | o loop de revisão não convergiu: 3 rodadas ou 2 ciclos do avaliador | pergunta |
   | `[D5 · provas em conflito]` | dois lados com prova: um achado grave refutado com evidência | pergunta |
   | `[auto · de rotina]` | a recomendada resolve: modo de execução, onde gravar, formato | não pergunta: vale a recomendada, e a decisão vai para o recibo "Decidi sozinho" |

   Antes da primeira pergunta `[auto · de rotina]` da sessão, rode `bash sdd/bin/sdd-fluxo.sh estado`:
   0 ligado · 1 desligado · 64 valor inválido (avise com a linha que ele imprimiu e trate como
   desligado). A pergunta do OK da `sdd-release` ("Posso finalizar…?") é D1 por construção e não leva
   marca: o texto dela é contrato. `sdd/bin/sdd-decisoes-lint.sh --sites` confere a marca e o rótulo.

## Pergunta aberta

Quando a resposta não cabe em opções (um nome, um número, um caminho):

```markdown
**Sua decisão** — [D2 · muda o produto] **Qual é o tempo máximo aceitável para processar um extrato?** Responda com um número
e a unidade (por exemplo, "30 segundos"), ou "não sei": aí eu proponho um valor com base nas amostras.
```

Não invente opções para uma pergunta aberta. Diga como responder e deixe a saída "não sei".

## Várias perguntas de uma vez

Só quando a etapa precisa delas juntas, até 5, numeradas; a pessoa pode responder pelos números
("1 sim, 2 mostrar antes"). Cada uma segue o formato acima.

## Parada ⏸️

Quando a etapa não pode seguir sem uma ação da pessoa (instalar algo, fazer login, abrir uma sessão
nova do agente para um avaliador sem esta conversa):

```markdown
**Status** — `Build: ✅ 1 Plano · ✅ 2 Modo · ✅ 3 Tarefas 5/5 · ⏸️ 4 Verify Gate · ⬜ 5 Relatório`

**Por que parei:** a conferência final precisa de alguém que não viu esta conversa, e este agente não
abre uma conversa nova sozinho.

**Onde:** numa janela nova do seu agente, na mesma pasta do projeto.

**Passos:**
1. Abra uma sessão nova do agente nesta pasta → você vê o agente pronto, sem histórico.
2. Cole o pedido que está no arquivo do brief → o agente começa a ler o DEFINE.
3. Quando ele terminar, copie a última linha (`VEREDITO: …`) → é ela que eu preciso.

**O que não foi feito:** o relatório não foi gravado e nada foi publicado.

**Brief:** `sdd/reports/evidence/PAGAMENTOS/AVAL-brief.md`

**Sessão nova:** abra o agente nesta pasta e cole o conteúdo do brief.

Quando terminar, me peça de novo, eu continuo daqui.
```

- O Status mostra ⏸️ na etapa parada.
- **Por que parei:** uma frase, com o motivo da pessoa, não a regra da skill.
- **Onde:** terminal, navegador, pasta, outra janela do agente.
- **Passos:** numerados, um comando por passo quando houver comando, com o que esperar na tela.
- **O que não foi feito:** sempre ("Nada foi publicado.", "Nenhuma frente foi criada.").
- **Brief:** e **Sessão nova:** só quando a parada é por uma sessão sem esta conversa: o caminho do
  arquivo que a skill gravou e como abrir a sessão. Sem isso, as duas linhas somem.
- A frase final só quando a pessoa tem algo a fazer.
