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

## sdd/templates/fragments/RESUMO_ETAPA.md
<<<< antes
## 📍 Linha de produção — {FEATURE}

✅ setup — ✅ /brainstorm — ✅ /define — ➖ /ux-review — 🏃 /design — ⬜ review adversarial — ⬜ /build — ⬜ /release
====
## 📍 Linha de produção — {FEATURE}

✅ setup — ✅ /brainstorm — ✅ /define — ➖ /ux-review — 🏃 /design — ⬜ /build — ⬜ /release
>>>> depois

## sdd/templates/fragments/RESUMO_ETAPA.md
<<<< antes
```markdown
✅ setup — ✅ /brainstorm — ✅ /define — ➖ /ux-review — 🏃 /design — ⬜ review adversarial — ⬜ /build — ⬜ /release
```
====
```markdown
✅ setup — ✅ /brainstorm — ✅ /define — ➖ /ux-review — 🏃 /design — ⬜ /build — ⬜ /release
```
>>>> depois

## sdd/templates/fragments/RESUMO_ETAPA.md
<<<< antes
✅ setup — ✅ /brainstorm — ✅ /define — ➖ /ux-review — 🏃 /design
⬜ review adversarial — ⬜ /build — ⬜ /release
====
✅ setup — ✅ /brainstorm — ✅ /define — ➖ /ux-review — 🏃 /design
⬜ /build — ⬜ /release
>>>> depois

## sdd/templates/fragments/RESUMO_ETAPA.md
<<<< antes
✅ setup — ➖ /sdd-brainstorm — ✅ /sdd-define — ✅ /sdd-ux-review — ✅ /sdd-design — 🏃 review adversarial — ⬜ /sdd-build — ⬜ /sdd-release
====
✅ setup — ➖ /sdd-brainstorm — ✅ /sdd-define — ✅ /sdd-ux-review — 🏃 /sdd-design — ⬜ /sdd-build — ⬜ /sdd-release
>>>> depois

## sdd/templates/fragments/RESUMO_ETAPA.md
<<<< antes
| /sdd-define | `sdd/features/DEFINE_{F}.md` |
| /sdd-ux-review | `sdd/reviews/UX_REVIEW_{F}.md` |
| /sdd-design | `sdd/features/DESIGN_{F}.md` |
====
| /sdd-define | `sdd/features/DEFINE_{F}.md` ou `sdd/DEFINE_{F}.md` |
| /sdd-ux-review | `sdd/reviews/UX_REVIEW_{F}.md` ou `sdd/UX_REVIEW_{F}.md` |
| /sdd-design | `sdd/features/DESIGN_{F}.md` ou `sdd/DESIGN_{F}.md` |
>>>> depois

## sdd/templates/fragments/RESUMO_ETAPA.md
<<<< antes
| /sdd-build | `sdd/reports/BUILD_REPORT_{F}.md` |
| /sdd-release | `sdd/releases/{F}/` **com ledger do slice ATUAL** — famílias com vários slices (ex.: `ALERTAS_AULA_GRUPO` tem s1/s2/s3) já têm ledger no `main`: casar o slice desta frente, senão a fase Release sai `✅` antes do ship |
====
| /sdd-build | `sdd/reports/BUILD_REPORT_{F}.md` ou `sdd/BUILD_REPORT_{F}.md` |
| /sdd-release | a frente publicada: o commit dela na principal, ou o PR dela aberto ou integrado |
>>>> depois
