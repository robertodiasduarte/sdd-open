# Como falar com o aluno — sdd-define

Quem chega ao Define traz um brainstorm e nenhum vocabulário de requisitos. A seção "Como falar com o
aluno" do `SKILL.md` dá o formato; este arquivo dá as palavras e um exemplo inteiro.

## Glossário (explique na primeira vez em que o termo aparecer)

- requisito — "uma frase que diz o que o sistema precisa fazer, de um jeito que dê para conferir depois";
- MUST / SHOULD / COULD — "o que é obrigatório, o que é importante mas pode esperar, e o que seria bom
  ter";
- critério de sucesso — "como a gente vai saber que deu certo: um número ou algo que dá para observar";
- teste de aceitação — "uma frase do tipo 'quando acontece X, o sistema faz Y', que vira a prova de que
  o requisito foi atendido";
- EARS — "o jeito padronizado de escrever essas frases (quando…, se…, enquanto…); as palavras ficam em
  inglês porque é uma convenção";
- Clarity Score — "uma nota de 0 a 15 que mede se o documento está claro o bastante para seguir";
- Verify Gate — "a conferência final: um comando que roda e diz passou ou não passou";
- escopo / fora de escopo — "o que entra nesta entrega e o que fica explicitamente de fora";
- DEFINE — "o documento desta fase; a próxima (Design) parte dele".

Não fale em stakeholder, NFR, edge case ou data model sem traduzir: "quem é afetado", "exigência de
velocidade ou segurança", "caso raro", "que informações o sistema guarda".

## Status desta skill, preenchido

`Define: ✅ 1 Ler o brainstorm · ✅ 2 Requisitos · ✅ 3 Testes de aceitação · ▶️ 4 Perguntas · ⬜ 5 Verify Gate · ⬜ 6 Gravar`

## Exemplo de resposta completa

Situação: o brainstorm de uma "planilha de conferência de notas" está lido e os requisitos rascunhados;
faltou decidir o que acontece quando um PDF não pode ser lido.

**Status** — `Define: ✅ 1 Ler o brainstorm · ✅ 2 Requisitos · ✅ 3 Testes de aceitação · ▶️ 4 Perguntas · ⬜ 5 Verify Gate · ⬜ 6 Gravar`
(no Status: "Requisitos" são as frases que dizem o que o sistema precisa fazer; "Testes de aceitação", as
frases "quando X, o sistema faz Y" que provam cada requisito; "Verify Gate", a conferência final — um
comando que roda e diz passou ou não passou.)

**O que foi feito** — Li o brainstorm inteiro e escrevi 6 requisitos (frases que dizem o que a planilha
precisa fazer, de um jeito que dá para conferir): 4 obrigatórios e 2 que podem esperar. Para cada um há
um teste de aceitação — uma frase "quando acontece X, o sistema faz Y" que vira a prova depois.

**Agora: etapa 4 — Perguntas** — Ficou uma dúvida que eu não posso decidir sozinho, porque muda o que o
sistema faz: o que acontece quando um PDF vem ilegível (escaneado torto, protegido por senha). Nada é
gravado ainda; esta etapa só fecha as dúvidas.

**Sua decisão** — [D2 · muda o produto] **Quando um PDF não puder ser lido, o que o sistema faz?**
- **pula e lista no fim** (recomendado): a planilha sai com as notas legíveis e uma aba "não lidas" com
  o nome de cada arquivo; você confere essas à mão.
- **para tudo e avisa**: nenhuma planilha sai até você resolver o arquivo; mais seguro, mas um único PDF
  ruim trava a conferência do mês.
- **tenta ler como imagem**: o sistema usa reconhecimento de texto na imagem; demora mais e pode errar
  números — eu acrescentaria um requisito de conferência.
- **não sei** — eu mostro com dois PDFs da sua amostra como cada opção ficaria.

**Próximo passo** — Com a sua resposta, eu escrevo o requisito e o teste correspondente e passo para a
conferência final (Verify Gate).
