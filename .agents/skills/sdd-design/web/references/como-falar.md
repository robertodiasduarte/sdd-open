# Como falar com o aluno — sdd-design

Quem chega ao Design traz requisitos prontos e nenhum vocabulário de arquitetura. A seção "Como falar
com o aluno" do `SKILL.md` dá o formato; este arquivo dá as palavras e um exemplo inteiro.

## Glossário (explique na primeira vez em que o termo aparecer)

- arquitetura — "o desenho de como as partes do sistema se encaixam";
- componente — "uma parte do sistema com uma função só (ler os PDFs, montar a planilha, avisar)";
- decisão técnica / ADR — "uma escolha registrada com o motivo e o que foi descartado, para ninguém
  refazer a discussão depois";
- File Manifest / manifest — "a lista dos arquivos que vão ser criados ou alterados, em ordem";
- fluxo de dados — "o caminho que a informação percorre, do que entra até o que sai";
- integração — "uma conversa do sistema com outro sistema (um banco, um serviço na internet)";
- DESIGN — "o documento desta fase; a próxima (Build) constrói a partir dele".

Não fale em stack, endpoint, idempotência, observabilidade ou schema sem traduzir: "as ferramentas
usadas", "o endereço que recebe pedidos", "pode repetir sem estragar", "como a gente enxerga o que o
sistema está fazendo", "o formato das informações".

## Status desta skill, preenchido

`Design: ✅ 1 Ler · ▶️ 2 Decisões · ⬜ 3 Componentes e arquivos · ⬜ 4 Fluxo, testes e erros · ⬜ 5 Conferir · ⬜ 6 Gravar`

## Exemplo de resposta completa

Situação: DEFINE da "planilha de conferência de notas" lido; o projeto já tem um script em Python que lê
PDFs; é preciso decidir onde a planilha fica guardada.

**Status** — `Design: ✅ 1 Ler · ▶️ 2 Decisões · ⬜ 3 Componentes e arquivos · ⬜ 4 Fluxo, testes e erros · ⬜ 5 Conferir · ⬜ 6 Gravar`
(no Status: "Componentes" são as partes do sistema, cada uma com uma função; "Fluxo" é o caminho que a
informação percorre; "Conferir" é a conferência automática do documento, que reprova o que está
incompleto.)

**O que foi feito** — Li o brainstorm e o DEFINE e olhei a pasta do projeto: já existe um programa que
lê PDFs (vou reaproveitá-lo) e não existe nada que gere planilhas. Nenhum arquivo foi alterado.

**Agora: etapa 2 — Decisões** — Antes de desenhar as partes do sistema (os componentes), preciso fechar
as escolhas que mudam o desenho. Sobrou uma que é sua, porque depende de como você trabalha: onde a
planilha pronta fica guardada. Cada escolha fica registrada com o motivo, para ninguém refazer a
discussão depois.

**Sua decisão** — [D2 · muda o produto] **Onde a planilha de conferência fica guardada?**
- **na pasta do projeto, uma por mês** (recomendado): simples, funciona sem internet, e o histórico fica
  no próprio computador; você abre no Excel como hoje.
- **no Google Drive da empresa**: outras pessoas veem na hora, mas o sistema passa a depender de login
  e de internet — entra uma integração a mais para construir e testar.
- **nos dois**: gera na pasta e envia uma cópia; mais trabalho, e duas cópias podem divergir.
- **não sei** — eu mostro como fica o dia a dia em cada caso.

**Próximo passo** — Com a sua escolha, eu desenho os componentes e a lista de arquivos (etapa 3) e volto
com o primeiro rascunho para você olhar.
