## 1. Veredito geral

**REPROVADO**

A trava de estado pode ser tomada de um processo ainda vivo, permitindo gravações concorrentes que apagam recibos ou resultados de gates. Isso compromete a retomada e o controle de rodadas, que são responsabilidades centrais do drive.

## 2. Conformidade com o DEFINE e o DESIGN

- **AT-001 a AT-020 — drive:** os verbos, ações, motivos, relatórios e testes estão representados no diff. Entretanto, R1 compromete a serialização prometida pelo DESIGN e pode invalidar a persistência exigida por AT-008, AT-012 e AT-016.
- **AT-021 e AT-027 — release:** o texto incorpora o raio de impacto por superfície e delega a verificação do deploy ao script, preservando drift, smoke e a advertência sobre testes.
- **AT-022 a AT-026 — deploy:** há implementação e testes para os desfechos previstos, incluindo substituto, redisparo único e consultas inconclusivas.
- **AT-028 a AT-037 — archive e integrações:** o diff apresenta os mecanismos, documentos, configuração e testes correspondentes.
- **Limitação de verificação:** os logs do Verify Gate não foram fornecidos inline; AT-038 permanece pendente no BUILD_REPORT, e não há evidência inline do CI e da release exigidos pelos critérios de sucesso.

## 3. Achados

### R1 — Trava de estado expira enquanto seu proprietário ainda está vivo

`sdd/bin/sdd-drive.sh:330` · **HIGH** · **CONFIRMED**

A trava é removida somente por ter mais de 60 segundos, sem verificar se o processo proprietário terminou, permitindo que dois comandos alterem o mesmo estado simultaneamente.

**Cenário concreto:** um `proximo` carrega o estado e fica suspenso por mais de 60 segundos antes de gravá-lo. Outra chamada, como `recibo`, remove a trava por idade, carrega o estado e grava um novo recibo. Quando o primeiro processo retoma, grava sua cópia anterior e apaga esse recibo. Pelo mesmo mecanismo, pode apagar um gate registrado por outra chamada, inclusive um vermelho que deveria consumir uma rodada. A gravação atômica protege cada arquivo individualmente, mas não impede essa perda de atualizações.

## 4. Bloco de vereditos

<<<VERDICTS
{"achado":"R1","arquivo":"sdd/bin/sdd-drive.sh","linha":330,"severidade":"HIGH","confianca":"CONFIRMED","resumo":"A trava de estado expira sem verificar seu proprietário, permitindo gravações concorrentes que apagam recibos ou resultados de gates."}
VERDICTS>>>