# Build Protocol

## Objetivo

Implementar exatamente o que foi aprovado no Brainstorm → Define → Design, produzir evidência executável e gerar um Build Report auditável.

## Máquina de estados

`LOAD_INPUTS`
→ `INSPECT_PROJECT`
→ `COMPILE_TASKS`
→ `SELECT_MODE`
→ `PRE_REVIEW_DECISION`
→ `EXECUTE_TASK`
→ `INCREMENTAL_VERIFY`
→ `NEXT_TASK`
→ `VERIFY_GATE`
→ `COMPLEMENTARY_CHECKS`
→ `POST_REVIEW_DECISION`
→ `BUILD_REPORT`
→ `VALIDATE_REPORT`
→ `HANDOFF`

Estados de interrupção:
- `SPEC_CLARIFICATION`
- `DESIGN_ITERATION`
- `BLOCKED`
- `MANUAL_UX_WAITING_RECEIPT`

## Regra de autoridade

- DEFINE controla aceite.
- DESIGN controla implementação.
- Brainstorm controla intenção e YAGNI.
- Código real controla fatos atuais da base.
- Usuário controla decisões novas.

Nunca usar “o código já faz assim” para invalidar um requisito do DEFINE sem decisão humana.
Nunca usar uma ideia antiga do Brainstorm para reabrir uma decisão posterior do DEFINE/DESIGN.

## Regra de escrita

Somente editar paths previstos no File Manifest.

Exceções:
- arquivo de relatório;
- arquivo de progresso de modo ralph;
- artefato explicitamente exigido pelo tooling do próprio projeto e aprovado pelo usuário.

Mudança material de path/arquitetura → voltar ao Design.

## Regra de interação

Perguntar quando:
- há duas leituras plausíveis de requirement/design;
- o path/contrato real diverge da spec;
- falta comando de verificação;
- o mode ainda não foi escolhido;
- review pré/pós-build precisa de decisão;
- manual-ux exige receipt;
- drift é detectado;
- third failure bloqueia.

Não perguntar sobre detalhe local já resolvido por padrão evidente do projeto.

## Evidência mínima por tarefa

Registrar:
- task id;
- path;
- action;
- executor;
- verification command;
- exit/result;
- breve evidência.

“Implemented” sem verificação não é Complete.

## Stop conditions

Parar o Build como Blocked quando:
- projeto não está acessível e o usuário não escolheu o caminho do chat (ele salva o código e relata a conferência);
- DEFINE ou DESIGN precisa de mudança material;
- Verify Gate está red após tentativas razoáveis;
- gate está inconclusivo e a inconclusão não foi resolvida;
- gate pede clarificação ou está ausente/malformado no DEFINE;
- terceira falha da mesma aceitação;
- dependência externa imprescindível não está disponível;
- manual-ux ainda não tem receipt.

## Success condition

Build completo somente quando:
- manifest completo;
- verificação incremental registrada;
- Verify Gate green (`0`) ou manual-ux com receipt;
- checks complementares aplicáveis green;
- relatório relido contra o checklist de conclusão.

## Next step

Somente em Build completo:

```markdown
## Next Step

Execute o **SDD Handoff by RDD**.
```
