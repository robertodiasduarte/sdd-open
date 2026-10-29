# {NOME DO DOMÍNIO}

> **Do que trata:** {uma frase — o recorte normativo deste conhecimento}
> **Para quem:** {quem consulta isto, e com que pergunta na cabeça}
> **Data-base:** {AAAA-MM-DD — a data em que o conteúdo foi conferido contra as fontes do catálogo}
> **Última revisão:** {AAAA-MM-DD}
> **Revisado por:** {nome e registro profissional de quem conferiu — ou `PENDENTE DE REVISÃO`}

## Comece por aqui

{2-3 frases: qual arquivo ler primeiro. Para "o que vale em tal data", aponte para [RULE_MAP.md](RULE_MAP.md).}

## Conceitos — para entender

| Arquivo | Do que trata |
|---|---|
| [concepts/{arquivo}.md](concepts/{arquivo}.md) | {uma linha} |

## Receitas — para fazer

| Arquivo | Resolve |
|---|---|
| [patterns/{arquivo}.md](patterns/{arquivo}.md) | {uma linha} |

## Regras, fontes, tabelas e casos

- [RULE_MAP.md](RULE_MAP.md) — cada regra com vigência, fonte, status, implementação e teste (gerado; não editar à mão)
- [fontes/CATALOGO.md](fontes/CATALOGO.md) — cada documento citado, com degrau normativo, versão, data de captura e SHA-256
- `tabelas/` — valores por vigência (uma pasta por data de início) · `casos/` — entrada e resultado esperado por regra

## Conflitos entre fontes

{Uma linha por conflito: as duas fontes, o que cada uma diz, qual regra é afetada (pelo id) e o que esta base adota até a próxima revisão. Sem conflito: "Nenhum conflito registrado até a data-base."}

## O que este domínio NÃO cobre

{Delimitar é tão útil quanto cobrir.}

---

> **Responsabilidade:** esta base não é aconselhamento tributário, contábil ou jurídico. A IA organiza e redige; quem responde pelo conteúdo — lei, norma, alíquota, prazo, leiaute — é o profissional que revisou. Antes de um software consumir esta base, ela é revisada e validada com `validate_kb.py --strict`.
>
> **A data do arquivo e o nome não provam vigência.** Vale o que o catálogo registra: versão, data de captura e SHA-256 conferidos na fonte oficial.
