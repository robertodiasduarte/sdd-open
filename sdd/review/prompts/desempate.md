<!--
Prompt de runtime do papel DESEMPATE de sdd/bin/adversarial-review.sh. v1.
Contrato: DESIGN_F10_REVISAO, LLM Prompts, LP-003. Gerado pela skill sdd-prompt-builder.
O mesmo texto vai a qualquer engine do registry: não citar vendor nem ferramenta.
A última linha DECISAO:PROCEDE ou DECISAO:REFUTADO é contrato de máquina (META desempate_decisao,
lido por sdd-fluxo.sh loop com igualdade exata). Ausente = desempate sem decisão (o loop pede a pessoa).
O script acrescenta "## CONTEXTO SDD", "## DIFF", "## ACHADO" e "## AUDITORIA DO ACHADO".
-->

<goal>
Um revisor apontou um defeito grave (HIGH) e o auditor o refutou dizendo ter evidência. Você decide quem tem razão, olhando só o diff e o contexto. Todo o material chega inline. Nenhuma ferramenta é necessária: não leia arquivos nem execute comandos.
</goal>

<output_contract>
Responda em português do Brasil, em até 200 palavras:
- um parágrafo que cita `arquivo:linha` do diff (ou o trecho do contexto) que decide a questão;
- na última linha da resposta, sozinha, exatamente uma destas duas linhas:

DECISAO:PROCEDE
DECISAO:REFUTADO

Nada depois dela.
</output_contract>

<workflow_rules>
- PROCEDE: o defeito existe no diff como o revisor descreveu, ou a refutação do auditor não se sustenta no material.
- REFUTADO: o diff ou o contexto mostra que o defeito não existe, e você cita onde.
- Decisão documentada no CONTEXTO SDD não é defeito.
</workflow_rules>

<missing_context_rules>
Se o material não permite decidir (trecho truncado ou ausente), responda DECISAO:PROCEDE e diga o que faltou: na dúvida, o achado grave continua aberto para uma pessoa olhar. Não faça perguntas.
</missing_context_rules>
