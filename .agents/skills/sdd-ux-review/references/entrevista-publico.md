# Entrevista de público e referências — entrada opcional do passo 1

Quando o DEFINE não diz quem usa a feature e em que contexto, a revisão de UX não tem de quem partir.
Esta entrevista descobre isso sem exigir vocabulário de UX ou de design: perguntas de fato, abertas, uma
por resposta, e uma confirmação no fim. Pergunta e parada seguem `sdd/templates/fragments/PERGUNTA_DECISAO.md`.

## Quando usar

- O DEFINE não diz quem usa, com que frequência ou em que aparelho; ou
- o aluno pede para "pensar no público" antes da revisão.

Se o DEFINE já responde, pule a entrevista: não pergunte de novo o que está escrito.

## Como conduzir

- Uma pergunta por resposta. No máximo 2 esclarecimentos sobre o mesmo assunto antes de seguir.
- Pule o que o DEFINE ou a conversa já responderam.
- As perguntas de fato são **abertas**: não ofereça opções com uma "recomendada", que induziria a
  resposta. Dê exemplos no texto e deixe a saída "não sei".
- Resposta que não responde à pergunta é dúvida: explique com um exemplo e repita a pergunta.

## As perguntas

### Público

**Quem vai usar esta parte do sistema na maior parte do tempo?** Responda com quem é e o que faz (por exemplo: contador ou equipe contábil, cliente do escritório, empresário ou gestor, equipe administrativa interna, ou público misto), ou "não sei": aí eu proponho um público a partir do DEFINE e você corrige.

Depois, pergunte só o que muda a experiência, uma coisa por vez e só se ainda não estiver claro:
frequência de uso (todo dia, uma vez por mês), familiaridade com tecnologia, volume de informação na tela,
o risco de um erro (o que acontece se a pessoa errar) e o aparelho mais usado.

**Com que frequência essa pessoa vai usar, e em qual aparelho?** Responda com a frequência e o aparelho (por exemplo: "todo dia, no computador do escritório" ou "uma vez por mês, pelo celular"), ou "não sei": aí eu sigo com o caso mais exigente e marco como suposição.

### Estágio

**Em que estágio está o projeto: novo, em desenvolvimento, sistema que já existe ou redesenho?** Responda com o estágio, ou "não sei": aí eu olho o que já existe no repositório e digo o que encontrei.

Fora de "novo", pergunte se existem capturas de tela, marca, paleta, design system ou telas parecidas
que a revisão deve respeitar.

### Referência

**Qual destas referências mais se aproxima da sensação que você quer?** Responda com uma ou duas linhas do catálogo abaixo, com uma referência sua, ou "não sei": aí eu pergunto por sensações (sério ou amigável, compacto ou espaçoso, calmo ou energético) e sugiro 2 ou 3 para comparar.

### URL de referência (opcional)

**Tem algum site ou sistema cuja experiência você gostaria que o projeto lembrasse?** Responda com o endereço, ou "não sei": a URL é opcional, e a revisão segue sem ela.

## Catálogo de referências

São atalhos de linguagem para descrever a experiência, não cópia visual nem uso de marca.

| Referência | Sensação | O que pode virar princípio |
|---|---|---|
| Apple / iPhone | Premium, calmo, limpo, acabado | Hierarquia imediata, densidade calibrada, consistência, microinterações cuidadas |
| ChatGPT | Simples, direto, centrado no conteúdo | Pouco ruído, foco na tarefa, interação autoexplicativa |
| Nubank | Humano, moderno, acessível | Linguagem simples, confiança, menos burocracia percebida |
| Notion | Organizado, neutro, flexível | Estrutura de trabalho, modularidade, descoberta progressiva |
| Linear | Rápido, sofisticado, profissional | Eficiência, atalhos, densidade controlada, resposta imediata |
| Stripe | Informação complexa com acabamento | Clareza em dados, configurações bem agrupadas |
| Apple + ChatGPT | Premium e muito simples | Acabamento alto com pouca fricção e foco no próximo passo |
| Uma referência sua | Um produto que você citar | Extrair princípios observáveis e confirmar o que aproveitar |

## URL: como observar

Só quando o agente consegue abrir páginas. A consulta observa e propõe princípio; não copia layout,
identidade, texto ou implementação.

O que observar:
- a primeira hierarquia visual percebida;
- a densidade e o uso de espaço;
- a navegação e a arquitetura aparente;
- as ações primárias e secundárias;
- os formulários e a validação visível;
- os estados de retorno (carregando, erro, sucesso);
- a tipografia, o contraste e a legibilidade aparentes;
- o uso de cor e de ícone com significado;
- as interações e microinterações observáveis;
- o comportamento em tela menor, quando dá para ver;
- o tom de voz e os textos curtos da interface;
- o que parece reduzir ou aumentar a fricção.

Limites: não deduza tecnologia, intenção do designer nem comportamento que não viu; não suponha que a
referência serve ao público deste projeto. Se a página não abrir, peça uma captura de tela ou uma
descrição e registre "análise direta não disponível".

## Das respostas ao registro

Separe sempre três camadas antes de gravar:

1. **Observado** — o que é visível na referência ou no sistema que já existe.
2. **Desejado** — o que o aluno disse que quer para o próprio projeto.
3. **Recomendado** — o que a revisão sugere, com o motivo para quem usa o sistema.

Só o confirmado vira linha de `## User and Context` do UX_REVIEW (Primary User, User Goal, Primary Pain,
Device/Context). O que ficou em dúvida vai para `## Open UX Questions`. Frase vaga ("quero simples como o
ChatGPT") vira proposta verificável ("pouca competição visual, ação principal evidente, conteúdo em
primeiro plano") e é apresentada para confirmar, nunca como fato.

## Confirmação

Depois das perguntas, mostre o resumo em 5 linhas (público, frequência e aparelho, estágio, referência,
o que fica em dúvida) e pergunte:

**Sua decisão** — **Posso gravar este público em User and Context?**
- **sim** (recomendado) — gravo as 4 linhas confirmadas e sigo para a jornada: com o público definido, cada passo da jornada tem de quem partir.
- **ajustar** — você diz o que muda; eu corrijo o resumo e pergunto de novo.
- **não sei** — explico com um exemplo o que cada linha muda na revisão e pergunto de novo.

No "O que foi feito" da resposta seguinte, registre a escolha em 1 linha: *"Você escolheu **sim**: gravei
o público em User and Context."*
