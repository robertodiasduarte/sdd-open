# Governança do UX_STANDARD.md

## Fonte canônica e pasta do SDD

`UX_STANDARD.md` é a fonte canônica da experiência do projeto.

Os documentos do SDD ficam em `sdd/` na raiz do projeto — pasta visível, igual em qualquer agente. Se o projeto já tiver `.claude/sdd/`, continue nela. Os documentos ficam lado a lado, sem subpastas:

- `DEFINE_{FEATURE}.md` (gerado pela fase Define);
- `UX_STANDARD.md` e `UX_REVIEW_TEMPLATE.md` (gerados por esta meta-skill);
- `UX_REVIEW_{FEATURE}.md` (gerado pela `ux-review` a cada feature);
- `DESIGN_{FEATURE}.md` (gerado pela fase Design, que lê o UX_REVIEW).

Se o projeto guardar os documentos do Define em outra pasta, usar essa pasta — sem criar subpastas.

## Precedência

- `DEFINE` define o que a feature precisa fazer.
- `UX_STANDARD` define como a experiência deve se comportar.
- `UX_REVIEW_TEMPLATE` define como documentar a avaliação.
- Telas, componentes, capturas e o sistema existente mostram o estado atual; não substituem a fonte canônica.

Se `DEFINE` e `UX_STANDARD` entrarem em conflito relevante, a `ux-review` registra `MUST` e bloqueia o Design até haver decisão explícita.

## IDs estáveis

Cada regra verificável tem um ID único. Famílias recomendadas:

- `UX-CORE-*`: princípios universais;
- `UX-VIS-*`: hierarquia, densidade, tipografia e visual;
- `UX-NAV-*`: navegação e arquitetura de informação;
- `UX-INT-*`: interação e feedback;
- `UX-STATE-*`: estados do sistema;
- `UX-FORM-*`: formulários e entrada de dados;
- `UX-DATA-*`: tabelas, dashboards e dados;
- `UX-COPY-*`: tom de voz e microcopy;
- `UX-A11Y-*`: acessibilidade;
- `UX-RESP-*`: responsividade;
- `UX-MOTION-*`: movimento e microinterações;
- `UX-GAME-*`: gamificação, quando aplicável.

Nunca reutilizar um ID descontinuado para outro significado.

## Modo Criação

Criar a versão inicial depois da entrevista e da confirmação. Registrar a origem das decisões: informado pelo responsável, observado em material, recomendado e confirmado, ou não disponível.

## Modo Evolução

Antes de alterar a fonte canônica:

1. ler a versão atual;
2. preservar IDs e histórico;
3. apresentar o diff conceitual;
4. classificar cada mudança como adicionar, alterar, descontinuar ou manter;
5. pedir confirmação explícita;
6. atualizar versão e histórico;
7. regenerar os artefatos dependentes quando necessário.

Regra nova que nasce de uma lente cognitiva (as 7 lentes e o sinal de validação real da `ux-review`) entra com severidade SHOULD ou COULD. Para bloquear o Design, o responsável escreve uma regra própria em `MUST`, por este modo, com ID, critério verificável e versão — a lente sozinha nunca vira bloqueio.

## Autoridade da ux-review

A `ux-review` pode apontar lacuna no padrão e sugerir regra nova. Não pode editar o `UX_STANDARD.md` automaticamente. Uma revisão de feature não é canal implícito de governança do produto.

## Gate

Classificações:

- `MUST`: bloqueia o Design até correção ou aceite explícito do responsável;
- `SHOULD`: importante, segue obrigatoriamente no handoff;
- `COULD`: melhoria opcional;
- `WONT`: exclusão consciente nesta feature;
- `CONFORME`: evidência suficiente de atendimento;
- `NAO AVALIAVEL`: evidência insuficiente para concluir.

Um `MUST` aceito como exceção continua sendo uma violação aceita, não conformidade.

As lentes cognitivas têm classificação própria (`OK`, `RECOMENDAÇÃO`, `ALERTA`, `N.A.`) e ficam fora deste gate: não geram `MUST`, não entram no cálculo de `READY/BLOCKED FOR DESIGN` e nunca rebaixam uma regra canônica.
