# Trocas do molde RESUMO_ETAPA.md para o starter: sem a revisão adversarial do pacote.

## sdd/templates/fragments/RESUMO_ETAPA.md
<<<< antes
> `/design`, `/build`, a fase Release e `sdd/bin/adversarial-review.sh`. É o **dono único** do formato: as
====
> `/design`, `/build` e a fase Release. É o **dono único** do formato: as
>>>> depois

## sdd/templates/fragments/RESUMO_ETAPA.md
<<<< antes
| review adversarial | `<review.output_dir>/EXTERNAL_REVIEW_*/` (padrão `sdd/reports/reviews/`) **com `reviewer.md` + `META.txt` dentro** (o `sdd/bin/adversarial-review.sh` grava por TIMESTAMP, sem `{F}` no nome — conferir pelo `diff_sha256`/branch do META que o diff revisado é o desta frente; `auditor_exit ≠ 0` = auditor FALHOU, não "zero achados") |
| /sdd-build | `sdd/reports/BUILD_REPORT_{F}.md` |
====
| /sdd-build | `sdd/reports/BUILD_REPORT_{F}.md` |
>>>> depois
