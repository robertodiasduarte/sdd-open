# Como funciona

Esta skill ajuda a transformar um SaaS de referência em insumos para planejar uma solução própria. Primeiro investiga o produto; depois conduz as conversas SDD que escolhem o que construir e definem como aceitar a entrega futura.

Exemplo de pedido:

> Use a skill sdd-engenharia-reversa-saas para investigar um sistema de BPO financeiro (informe o nome ou a URL) e conduzir o Brainstorm e o Define de uma nova solução para BPO financeiro.

Informar uma URL ajuda a evitar produtos homônimos. Não é necessário ter conta: a análise começa pelas fontes públicas e declara o que não conseguiu verificar. Materiais ou demonstrações fornecidos podem aprofundar o levantamento.

São produzidos três documentos Markdown: engenharia reversa do SaaS, Brainstorm da nova solução e Define da nova solução. O Brainstorm exige decisões e validações suas. O Define pode continuar como rascunho se faltar um critério importante ou uma forma real de verificar o software futuro.

O caso do BPO financeiro é ilustrativo. A skill pode investigar outros SaaS, sempre separando o que viu, o que está documentado, o que foi relatado e o que é hipótese. Não garante descobrir regras internas nem que todos os recursos estejam visíveis.

Para continuar depois:

> Retome este ciclo a partir do relatório de engenharia reversa e dos documentos SDD já salvos.

As skills `sdd-brainstorm` e `sdd-define` precisam estar disponíveis no ambiente. Este pacote não inclui cópias delas. A integração ocorre antes do Brainstorm, por documentos e contexto; não altera comandos nem configurações do projeto.
