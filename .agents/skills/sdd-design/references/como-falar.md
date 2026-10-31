# Como falar com o aluno — sdd-design

Quem chega ao Design traz requisitos prontos e nenhum vocabulário de arquitetura. A seção "Como falar
com o aluno" do `SKILL.md` dá o formato; este arquivo dá as palavras e um exemplo inteiro.

## Glossário (explique na primeira vez em que o termo aparecer)

- arquitetura — "o desenho de como as partes do sistema se encaixam";
- componente — "uma parte do sistema com uma função só (ler os XMLs, montar a planilha, avisar)";
- decisão técnica / ADR — "uma escolha registrada com o motivo e o que foi descartado, para ninguém
  refazer a discussão depois";
- File Manifest / manifest — "a lista dos arquivos que vão ser criados ou alterados, em ordem";
- landmine — "uma armadilha que já mordeu alguém neste projeto, registrada no playbook com um número";
- playbook — "o caderno do projeto com as armadilhas conhecidas e o que fazer em vez disso";
- fluxo de dados — "o caminho que a informação percorre, do que entra até o que sai";
- integração — "uma conversa do sistema com outro sistema (um banco, um serviço na internet)";
- lint — "uma conferência automática do documento, que reprova o que está incompleto";
- DESIGN — "o documento desta fase; a próxima (Build) constrói a partir dele".

Não fale em stack, endpoint, idempotência, observabilidade ou schema sem traduzir: "as ferramentas
usadas", "o endereço que recebe pedidos", "pode repetir sem estragar", "como a gente enxerga o que o
sistema está fazendo", "o formato das informações".

## Status desta skill, preenchido

`Design: ✅ 1 Ler · ▶️ 2 Decisões · ⬜ 3 Componentes e arquivos · ⬜ 4 Fluxo, testes e erros · ⬜ 5 Gravar · ⬜ 6 Conferir`

## Exemplo — resposta completa, com decisão (etapa 2 — Decisões)

Situação: o DEFINE da conferência de notas pede ler os XMLs de uma pasta; falta escolher onde guardar o
que já foi conferido.

**Status** — `Design: ✅ 1 Ler · ▶️ 2 Decisões · ⬜ 3 Componentes e arquivos · ⬜ 4 Fluxo, testes e erros · ⬜ 5 Gravar · ⬜ 6 Conferir`
(no Status: "Conferir" é a conferência automática do documento no fim, que reprova o que ficou
incompleto.)

**O que foi feito** — Li o brainstorm e o DEFINE: 4 objetivos e 6 testes de aceitação. O playbook do
projeto não tem armadilha registrada para leitura de XML.

**Agora: etapa 2 — Decisões** — Antes de listar os arquivos, uma escolha muda o resto: onde fica a
memória do que já foi conferido, para a nota repetida não ser marcada duas vezes.

**Sua decisão** — [D2 · muda o produto] **Onde guardar as notas já conferidas?**
- **uma coluna na própria planilha** (recomendado) — nada novo para instalar; a planilha já é o que você
  abre todo mês.
- **um arquivo à parte** — a planilha fica limpa, mas são 2 arquivos para manter juntos.
- **um banco de dados** — aguenta milhares de notas; para as 40 por mês das amostras, é peça demais.
- **não sei** — mostro como cada opção fica com as 2 notas repetidas da amostra.

**Próximo passo** — Com a escolha registrada, monto a lista de arquivos, em ordem.

Formato completo de pergunta e de parada: `sdd/templates/fragments/PERGUNTA_DECISAO.md`.
