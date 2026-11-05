# BUILD REPORT: REPLAY — sintético (self-test do playbook-curator.sh)

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | REPLAY |
| **Date** | 2026-09-24 |

## Landmines lidas no build

| ID | Veredito | Como |
|----|----------|------|
| `LM-003` | ✔ tratado | o gate roda com o caso vermelho antes do verde |
| `LM-005` | **mordeu** | o exit gravado no log era o do pipe, não o do comando |

## Notas

Rodei com DOCS_EXTRACT_FORCE_FAIL=1 para provar o vermelho do LM-003: a palavra dentro do nome da variável não é achado.
