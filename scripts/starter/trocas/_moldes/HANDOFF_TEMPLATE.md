# Trocas do molde HANDOFF_TEMPLATE.md para o starter: sem o verify-gate.sh e o playbook do sdd-open, e sem a
# linha do Verify Gate (o aluno do starter, na web, não tem gate por comando).

## sdd/templates/HANDOFF_TEMPLATE.md
<<<< antes
| **Artefatos** | `sdd/features/DEFINE_{F}.md` · `sdd/features/DESIGN_{F}.md` · `sdd/reports/BUILD_REPORT_{F}.md` |
| **Verify Gate** | {🟢 0 · 🔴 2 · inconclusivo 3 · assinatura 4 · clarificar 5} — `sdd/bin/verify-gate.sh sdd/features/DEFINE_{F}.md` |
====
| **Artefatos** | `DEFINE_{F}.md` · `DESIGN_{F}.md` · `BUILD_REPORT_{F}.md` (onde o projeto os guarda) |
>>>> depois

## sdd/templates/HANDOFF_TEMPLATE.md
<<<< antes
- {armadilha que mordeu ou quase mordeu, com o "faça isto em vez disso"; candidata ao `sdd/playbook.md`}
====
- {armadilha que mordeu ou quase mordeu, com o "faça isto em vez disso"}
>>>> depois

## sdd/templates/HANDOFF_TEMPLATE.md
<<<< antes

Estado do gate: `sdd/bin/verify-gate.sh sdd/features/DEFINE_{F}.md` saiu {N} em {data}.
====
>>>> depois
