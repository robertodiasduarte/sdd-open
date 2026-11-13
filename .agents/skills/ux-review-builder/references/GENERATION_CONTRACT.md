# Contrato dos artefatos gerados

## Artefato 1: UX_STANDARD.md

Fonte canônica verificável, versionada e independente do agente. Contém os dez princípios universais, as regras específicas do projeto com IDs estáveis, critérios observáveis, governança e histórico.

Não contém caminho de pasta: a localização segue a regra da pasta do SDD em `references/GOVERNANCE.md`.

## Artefato 2: skill ux-review

Deve:

- ler `DEFINE_{FEATURE}.md`, `UX_STANDARD.md` e `UX_REVIEW_TEMPLATE.md` na pasta do SDD;
- aceitar BRAINSTORM, capturas de tela, mockups, design system, componentes e URLs como contexto opcional;
- mapear a jornada: antes, entrada, ação central, feedback, recuperação, conclusão e acompanhamento;
- revisar clareza, eficiência, confiança, acessibilidade, responsividade, estados, continuidade, acabamento e padrões específicos do projeto;
- citar IDs canônicos nos achados quando aplicável;
- classificar `MUST`, `SHOULD`, `COULD`, `WONT`, `CONFORME` e `NAO AVALIAVEL`;
- aplicar as lentes cognitivas (7 lentes + sinal de validação real) como recomendação e alerta, com a regra existente que manda em cada uma, sem gerar `MUST` nem mudar o resultado do gate;
- mapear, na jornada, a linha Interrupção → Retomada;
- bloquear o Design quando houver `MUST` não resolvido ou não aceito explicitamente;
- nunca alterar o `UX_STANDARD.md` automaticamente;
- gravar `UX_REVIEW_{FEATURE}.md` na mesma pasta, a partir do modelo;
- manter o papel de gate entre o Define e o Design, sem substituir o Design nem a auditoria do sistema.

## Artefato 3: UX_REVIEW_TEMPLATE.md

Agnóstico de projeto, com:

- metadados e versões das fontes;
- resumo de UX;
- usuário e contexto;
- mapa da jornada;
- conformidade canônica;
- achados com ID de regra, prioridade, evidência e recomendação;
- checagem dos princípios universais e dos North Stars do projeto;
- lentes cognitivas, fora do gate, e a linha das lentes no resultado do gate;
- estratégia visual baseada no UX_STANDARD, sem tokens de outro projeto;
- interações e estados obrigatórios;
- copy;
- acessibilidade e responsividade;
- gamificação quando aplicável;
- handoff para o Design;
- resultado do gate;
- perguntas abertas, histórico e próximo passo.

## Coerência cruzada

Os três artefatos usam os mesmos IDs, categorias e classificações. O status das lentes cognitivas (`OK`, `RECOMENDAÇÃO`, `ALERTA`, `N.A.`) é uma classificação à parte, que não substitui nem se mistura com a das regras canônicas. Se um conceito existir no modelo mas não puder ser sustentado pelo `UX_STANDARD.md`, marcar como `NAO AVALIAVEL` ou `não se aplica` — nunca inventar regra.
