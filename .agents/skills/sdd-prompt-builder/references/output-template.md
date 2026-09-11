# Template de saída do prompt

Usar este esqueleto de forma adaptativa. Remover seções que não forem justificadas pela tarefa.

```text
<GENERATED_PROMPT>
<goal>
{{USER_GOAL_REFINED}}
</goal>

<output_contract>
{{USER_OUTPUT_CONTRACT}}
</output_contract>

<workflow_rules>
{{USER_WORKFLOW_RULES}}
</workflow_rules>

<formulas>
{{USER_FORMULAS}}
</formulas>

<missing_context_rules>
{{USER_MISSING_CONTEXT_RULES}}
</missing_context_rules>

<verification>
{{USER_VERIFICATION_RULES}}
</verification>

<completeness_contract>
{{USER_COMPLETENESS_CONTRACT}}
</completeness_contract>

<empty_result_recovery>
{{USER_EMPTY_RESULT_RECOVERY}}
</empty_result_recovery>

<reference_material>
{{USER_REFERENCE_MATERIAL}}
</reference_material>

<stop_conditions>
{{USER_STOP_CONDITIONS}}
</stop_conditions>

<tools>
{{USER_TOOLS}}
</tools>
</GENERATED_PROMPT>
```

## Regra de emissão

A resposta da skill deve conter um único TXT BLOCK com o prompt final pronto para uso. Não adicionar wrapper TypeScript, constante exportada, path de arquivo ou explicação fora do artefato, salvo se o caller pedir explicitamente um formato diferente permitido pelo contrato.
