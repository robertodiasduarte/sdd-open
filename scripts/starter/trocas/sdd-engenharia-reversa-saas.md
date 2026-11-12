# Trocas da sdd-engenharia-reversa-saas para o starter.

## manifest.json
<<<< antes
      "verificacao": "sdd/bin/skill-lint.py --conversa e sdd/bin/sdd-decisoes-lint.sh --sites do sdd-open",
====
      "verificacao": "skill-lint --conversa e sdd-decisoes-lint --sites, rodados no sdd-open antes da geração",
>>>> depois

## references/ORQUESTRACAO_SDD.md
<<<< antes
(no SDD Open, `sdd/templates/`; em outras distribuições, um asset da própria skill)
====
(no SDD Open, a pasta de moldes do projeto; no starter, `assets/` da skill `sdd-brainstorm`)
>>>> depois

## SKILL.md
<<<< antes
(no SDD Open, `sdd/templates/BRAINSTORM_TEMPLATE.md`)
====
(no starter, `assets/BRAINSTORM_TEMPLATE.md` da skill `sdd-brainstorm`)
>>>> depois
