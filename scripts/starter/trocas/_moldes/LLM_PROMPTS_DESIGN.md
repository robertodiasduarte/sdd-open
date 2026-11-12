# Trocas do molde LLM_PROMPTS_DESIGN.md para o starter: sem o design-lint nem o script de drift do pacote.

## sdd/templates/fragments/LLM_PROMPTS_DESIGN.md
<<<< antes
não existe. `sdd/bin/design-lint.py` confere as colunas e os campos. A Design não escreve prompt nem
====
não existe. A Design não escreve prompt nem
>>>> depois

## sdd/templates/fragments/LLM_PROMPTS_DESIGN.md
<<<< antes
- **Antes de gravar**, o texto gerado passa por `bash sdd/bin/prompt-drift-scan.sh --conteudo <caminho>`.
  Num arquivo deste inventário, a saída 2 é o esperado e o arquivo é gravado.
====
- **Antes de gravar**, confira o texto gerado pelos sinais de drift (seção "Drift detection" de
  `references/sdd-integration.md` da `sdd-prompt-builder`); num arquivo deste inventário, o sinal é o esperado.
>>>> depois
