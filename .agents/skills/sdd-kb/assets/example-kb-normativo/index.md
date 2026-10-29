# IBS e CBS na NF-e modelo 55 — ano-teste 2026

> **Do que trata:** quando a NF-e modelo 55 precisa do grupo `IBSCBS` e quais alíquotas de referência valem no ano-teste de 2026 — recorte de exemplo derivado de uma base real da Reforma Tributária do consumo.
> **Para quem:** quem configura emissor ou valida NF-e e precisa saber, para uma data de emissão, o que a SEFAZ exige.
> **Data-base:** 2026-09-27
> **Última revisão:** 2026-10-04
> **Revisado por:** PENDENTE DE REVISÃO (exemplo didático da skill — conferir na NT antes de qualquer uso)

## Comece por aqui

Para "o que vale numa data", vá direto ao [RULE_MAP.md](RULE_MAP.md): cada linha traz a vigência, a fonte com página e o status. Para entender por que 2026 é diferente dos anos seguintes, leia [concepts/ano-teste-2026.md](concepts/ano-teste-2026.md).

## Conceitos — para entender

| Arquivo | Do que trata |
|---|---|
| [concepts/ano-teste-2026.md](concepts/ano-teste-2026.md) | Por que 2026 tem alíquota de referência e grupo exigido por CRT em datas diferentes |

## Receitas — para fazer

| Arquivo | Resolve |
|---|---|
| [patterns/conferir-vigencia-antes-de-usar.md](patterns/conferir-vigencia-antes-de-usar.md) | Decidir se uma regra desta base vale para a data de emissão de uma nota |

## Regras, fontes, tabelas e casos

- [RULE_MAP.md](RULE_MAP.md) — 3 regras com vigência, fonte, status e código de rejeição (gerado; não editar à mão)
- [fontes/CATALOGO.md](fontes/CATALOGO.md) — NT 2025.002 v1.51, LC 214/2025, reportagens e o registro da captura (arquivo local com SHA-256 conferido pelo validador)
- [tabelas/2026-01-01/aliquotas-referencia.json](tabelas/2026-01-01/aliquotas-referencia.json) — alíquotas do ano-teste
- [casos/ub12-crt3-2026-09.json](casos/ub12-crt3-2026-09.json) — NF-e de CRT 3 sem `IBSCBS` em setembro/2026

## Consulta rápida

- [quick-reference.md](quick-reference.md) — datas por CRT e alíquotas de 2026

## Conflitos entre fontes

- **ALIQ-REF-2026** — reportagens especializadas (REPORT-2026) citavam "cerca de 0,1% de cada" para CBS e IBS em 2026; a NT 2025.002 v1.51 (p. 45, 47 e 49) fixa CBS 0,90%, IBS da UF 0,10% e IBS do município 0,00%. Esta base adota a NT, de degrau superior. O artigo da LC 214/2025 que fixa esses percentuais ainda não foi localizado aqui — por isso a regra cita a NT, não a lei.
- **UB12-10-EXC1** — no texto da Exceção 1 da UB12-10 (NT 2025.002 v1.51, p. 42), o ano "2026" aparece riscado e "2027" escrito no lugar. Esta base usa 2027 como premissa até a publicação de versão sem rasura.

## O que este domínio NÃO cobre

NFC-e, CT-e, NFS-e e demais documentos; cálculo de base e valores (regras UB16 em diante); enquadramento de CST e cClassTrib de uma operação; alíquotas a partir de 2027.

---

> **Responsabilidade:** esta base não é aconselhamento tributário, contábil ou jurídico. A IA organiza e redige; quem responde pelo conteúdo — lei, norma, alíquota, prazo, leiaute — é o profissional que revisou. Antes de um software consumir esta base, ela é revisada e validada com `validate_kb.py --strict`.
>
> **A data do arquivo e o nome não provam vigência.** Vale o que o catálogo registra: versão, data de captura e SHA-256 conferidos na fonte oficial.
