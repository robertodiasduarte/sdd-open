# Trocas da sdd-brainstorm para o starter: o playbook só existe num projeto com o init do sdd-open.

## SKILL.md
<<<< antes
Leia `AGENTS.md`, `sdd/templates/BRAINSTORM_TEMPLATE.md` e a seção `## Sempre` de
`sdd/playbook.md`. Explore a estrutura do projeto e os commits recentes: o que já existe que
====
Leia `AGENTS.md` (se existir) e `sdd/templates/BRAINSTORM_TEMPLATE.md`. Explore a estrutura do
projeto e os commits recentes (se tiver acesso a eles): o que já existe que
>>>> depois

## SKILL.md
<<<< antes
Fase 1: /sdd-define     → sdd/features/DEFINE_{F}.md
UX:     /sdd-ux-review  → sdd/reviews/UX_REVIEW_{F}.md
Fase 2: /sdd-design     → sdd/features/DESIGN_{F}.md
Fase 3: /sdd-build      → código + sdd/reports/BUILD_REPORT_{F}.md
Fase 4: /sdd-release    → publicação com 1 OK + sdd/releases/{F}/
====
Fase 1: /sdd-define     → DEFINE_{F}.md
UX:     ux-review       → UX_REVIEW_{F}.md (a do seu projeto, criada pela ux-review-builder)
Fase 2: /sdd-design     → DESIGN_{F}.md
Fase 3: /sdd-build      → código + BUILD_REPORT_{F}.md
Fase 4: /sdd-release    → publicação com 1 OK
>>>> depois

## SKILL.md
<<<< antes
compatibility: Requer bash >= 3.2 e git >= 2.20; funciona em qualquer agente que leia AGENTS.md e .agents/skills/.
====
compatibility: Funciona na web (claude.ai, ChatGPT), onde o documento sai no chat, e em qualquer agente com acesso ao projeto.
>>>> depois

## SKILL.md
<<<< antes
**Próximo passo:** `/sdd-define sdd/features/BRAINSTORM_{FEATURE}.md`
====
**Próximo passo:** peça a skill `sdd-define` com este BRAINSTORM (na web, mande o documento junto com o pedido).
>>>> depois
