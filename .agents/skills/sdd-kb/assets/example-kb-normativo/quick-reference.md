# IBS e CBS na NF-e — consulta rápida

> Para quem já entende o domínio. Cada linha remete à regra no [RULE_MAP.md](RULE_MAP.md).

## Grupo IBSCBS exigido — por CRT e data de emissão

| CRT do emitente | Homologação | Produção | Regra |
|---|---|---|---|
| 3 (regime normal) | desde 2026-07-01 | desde 2026-08-03 | UB12-10-CRT3 |
| 1, 2 e 4 (Simples, MEI) | — | a partir de 2027-01-04 | fora deste recorte |

## Alíquotas de referência — 2026

| Tributo | Alíquota | Regra |
|---|---|---|
| CBS | 0,90% | ALIQ-REF-2026 |
| IBS da UF | 0,10% | ALIQ-REF-2026 |
| IBS do município | 0,00% | ALIQ-REF-2026 |

## Erros comuns

| ❌ Não faça | ✅ Faça |
|---|---|
| Usar a data do arquivo da NT como início de vigência | Usar a data que o texto da regra fixa (coluna Vigência do RULE_MAP) |
| Aplicar a alíquota de 2026 a nota de 2027 | Conferir `vigencia.ate` da regra antes de usar |
| Citar reportagem como fonte de alíquota | Citar a NT ou a lei, com página ou artigo |

## Onde procurar o resto

| Assunto | Arquivo |
|---|---|
| Começar do zero | [index.md](index.md) |
| Vigência, fonte e status de cada regra | [RULE_MAP.md](RULE_MAP.md) |
