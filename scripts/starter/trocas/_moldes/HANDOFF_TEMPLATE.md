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

## sdd/templates/HANDOFF_TEMPLATE.md
<<<< antes
> Gerado por `python3 sdd/bin/ficha-publicado.py {FEATURE}` a partir de `sdd/releases/{FEATURE}/`: uma linha por
> release, a mais recente no topo. Não edite à mão; o que o ledger já diz não se repete nas outras seções.

<!-- publicado:inicio (gerado por sdd/bin/ficha-publicado.py a partir de sdd/releases/; não edite à mão) -->
<!-- publicado:fim -->
====
> Uma linha por publicação, a mais recente no topo; o que está aqui não se repete nas outras seções.

- {data} · {o que subiu, em 1 frase} · {commit ou PR}
>>>> depois
