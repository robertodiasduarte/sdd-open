# Regras de construção de prompts

Consultar este arquivo em toda geração ou refino de prompt.

## Princípios

1. Definir o contrato de saída antes das demais instruções.
2. Declarar o que significa concluir a tarefa.
3. Definir comportamento para contexto ausente ou incerto.
4. Adicionar verificação interna somente quando aumentar confiabilidade.
5. Tentar recuperação razoável antes de fallback quando resultado vazio ou parcial for plausível.
6. Consolidar regras repetidas em um único lugar.
7. Separar instruções da tarefa de material de referência.
8. Usar apenas a estrutura necessária para a complexidade real.

## Estrutura adaptativa

Sempre incluir:
- `<goal>`
- `<output_contract>`

Normalmente incluir, quando úteis:
- `<workflow_rules>`
- `<missing_context_rules>`

Incluir condicionalmente:
- `<formulas>` para qualquer cálculo, métrica, indicador, razão ou score.
- `<verification>` para saída estruturada, tarefa crítica, transformação, extração ou formato rígido.
- `<completeness_contract>` para slots, lotes, listas, itens contáveis, inventários ou seções obrigatórias.
- `<empty_result_recovery>` quando entrada parcial, ruidosa, esparsa ou ilegível for plausível.
- `<reference_material>` quando houver template, schema, política, exemplos, trechos canônicos ou material-fonte.
- `<stop_conditions>` quando houver critérios rígidos de término, falha parcial, overflow ou proibição de pausa para esclarecer.
- `<tools>` somente quando escolha, ordem ou configuração de ferramentas alterar materialmente a execução.

Omitir qualquer seção vazia ou decorativa.

## Orientação por seção

### `<goal>`

Declarar a tarefa, o artefato a produzir e o critério operacional de sucesso. Evitar narração de processo sem efeito na execução.

### `<output_contract>`

Definir exatamente:
- tipo de saída;
- estrutura obrigatória;
- conteúdo que deve aparecer;
- conteúdo proibido fora do artefato;
- convenção de fallback, quando aplicável.

Para formatos rígidos, declarar literalmente regras como `output only valid JSON`, `output only a complete HTML document` ou equivalentes.

### `<workflow_rules>`

Incluir somente regras operacionais essenciais, como ordem de extração, transformação, reconciliação, classificação, preservação estrutural ou formatação. Não repetir regras do contrato de saída.

### `<formulas>`

Escrever cada fórmula explicitamente, nomeando operandos e operação.

Exemplo:
`margem bruta = (receita líquida - custo dos produtos vendidos) ÷ receita líquida`

Não escrever apenas `calcule a margem`. Se um operando puder faltar, combinar esta seção com `<missing_context_rules>`.

### `<missing_context_rules>`

Definir o que fazer com informação incompleta, ambígua ou não extraível:
- não inventar;
- usar o fallback aprovado;
- marcar item como pendente, indisponível ou bloqueado no local apropriado;
- em execução autônoma, não fazer perguntas ao usuário.

### `<verification>`

Exigir uma checagem interna curta de:
- satisfação dos requisitos;
- completude;
- aderência às fontes;
- conformidade de formato;
- ausência de mudanças estruturais não autorizadas.

Corrigir falhas antes de emitir a resposta.

### `<completeness_contract>`

Definir:
- todos os itens obrigatórios a contabilizar;
- quando um item pode ser marcado indisponível;
- como tratar itens excedentes;
- condição objetiva de conclusão.

### `<empty_result_recovery>`

Quando aplicável, exigir pelo menos duas estratégias razoáveis antes de marcar um dado indisponível, por exemplo:
- consultar seção adjacente;
- usar rótulos próximos;
- comparar totais ou campos espelhados;
- tentar uma rota alternativa de parsing.

Depois de esgotar os fallbacks, aplicar a convenção aprovada e registrar a ocorrência quando o formato permitir.

### `<reference_material>`

Colocar aqui templates, schemas, políticas, estrutura canônica, exemplos ou grandes trechos-fonte. Não duplicar regras operacionais já definidas em outras seções.

### `<stop_conditions>`

Usar somente para critérios rígidos de término, falha parcial, overflow ou regras que impeçam pausa para esclarecimento.

### `<tools>`

Descrever apenas o que afeta a execução. Se configuração de ferramenta estiver resolvida na API, mencionar isso de forma breve.

## Otimização

Ao refinar um pedido:
1. Identificar a tarefa real.
2. Inferir o contrato de saída necessário.
3. Converter avisos em regras operacionais.
4. Consolidar restrições repetidas.
5. Mover material extenso para `<reference_material>`.
6. Definir comportamento de contexto ausente para execução autônoma.
7. Adicionar verificação, completude e recuperação vazia apenas quando justificadas.
8. Remover texto decorativo ou não operacional.
9. Produzir o menor prompt que preserve fidelidade, controle e recuperabilidade.

## Restrições de estilo

- Usar linguagem formal.
- Não usar emojis.
- Não inserir rótulos de configuração como `Reasoning Effort`, `Verbosity` ou `Mode`, a menos que o usuário peça esses rótulos literalmente no prompt.
- Não repetir a mesma regra em várias seções.
- Não adotar anatomia fixa para tarefas simples.
