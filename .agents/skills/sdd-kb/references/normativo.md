# Perfil normativo: quando a regra vale por período

Referência de apoio da skill `sdd-kb`. Vale para o domínio registrado com `perfil: normativo` em `sdd/kb/_index.yaml`.

---

## O problema

Uma regra tributária não é verdadeira: ela é verdadeira **em um período**. "O ICMS cai 90% em 2029" está certo hoje e estará errado em 2030 sem que ninguém mude uma linha do arquivo. Um KB que guarda a regra sem a vigência envelhece em silêncio — e é consultado justamente por quem não sabe que ele envelheceu.

O perfil normativo dá a cada afirmação datada quatro coisas que o perfil geral não exige: **de quando até quando vale**, **de qual degrau normativo veio**, **onde duas fontes se contradizem** e **qual software e qual teste a implementam**.

## Quando usar

Use `normativo` quando o domínio tem regra que muda com o tempo: lei, alíquota, prazo, tabela, leiaute de documento fiscal, regra de validação. Use `geral` para domínio atemporal (uma ferramenta, um processo interno, um conceito contábil estável). Na dúvida, o validador avisa: domínio `geral` com marcadores normativos (LC, art., NT, vigência, alíquota, EC) recebe `WARN: parece normativo`.

## A estrutura

```
sdd/kb/<slug>/
├── index.md            ← + Data-base, Conflitos entre fontes, aviso de responsabilidade
├── quick-reference.md
├── concepts/           ← + `> **Vale para:** <período ou atemporal>` no cabeçalho
├── patterns/           ← + linha "Vale para:" no cabeçalho
├── rules/              ← regra atômica com vigência (obrigatório, ≥ 1)
├── fontes/CATALOGO.md  ← cada documento citado (obrigatório)
├── tabelas/AAAA-MM-DD/ ← valores por vigência (quando houver)
├── casos/              ← entrada → resultado esperado (quando houver)
└── RULE_MAP.md         ← gerado a partir de rules/ (obrigatório)
```

## Data-base

A data em que o conteúdo foi conferido contra as fontes do catálogo. Ela responde "até quando posso confiar nisto?". Pergunte-a no passo 1 e registre no `index.md` (`> **Data-base:** AAAA-MM-DD`). Para uma data posterior à data-base, a base não responde sozinha: confira a fonte. O validador avisa quando a data-base passa de um ano.

## Regras (`rules/`)

Uma regra por arquivo, com id estável — nunca reaproveitar nem renumerar. Frontmatter do molde `RULE_TEMPLATE.md`:

| Campo | Obrigatório | O que é |
|---|---|---|
| `regra` | sim | id estável (ex.: o id da NT, `UB12-10`, ou um id próprio) |
| `vigencia.de` / `vigencia.ate` | `de` sim | datas reais do calendário; `ate: null` enquanto em vigor |
| `fonte.id` / `fonte.localizador` | sim | id do catálogo + página, artigo ou seção |
| `status` | sim | `confirmado` · `premissa` (interpretação sem texto explícito) · `nao-confirmado` |
| `conflito_com` | não | ids de regras ou de fontes em conflito; explicar no `index.md` |
| `implementacao` / `teste` | não | onde o software implementa (`scripts/engine.py:vbc`) e o **caminho do arquivo de teste** a partir da raiz do projeto, com sufixo `:`/`::` opcional (`tests/test_engine.py::test_vbc`) — não um comando; o `--strict` confere que o arquivo existe e que regra implementada tem teste |
| `severidade` / `codigo` | não | E/A/I e código de rejeição, quando a regra é de validação |

**Mudou a regra? Não edite o passado.** Feche a regra antiga com `ate:` e crie outra a partir da nova data. O histórico continua respondendo por notas antigas.

**`confirmado` exige degrau normativo.** Regra cuja única fonte é `doutrina` ou `pratica-propria` não pode ser `confirmado` — o validador reprova. A honestidade passa a ser da estrutura, não só de quem redige.

## Catálogo de fontes (`fontes/CATALOGO.md`)

Uma linha por documento: id, documento, degrau, versão, origem (URL oficial), data de captura, arquivo e SHA-256. **A data do arquivo e o nome não provam vigência**: a versão e o hash provam qual texto foi lido. Guardou o arquivo em `fontes/`? O validador recalcula o SHA-256 e reprova se o arquivo mudou — versão nova é linha nova, com id novo. Calcule com `python3 .agents/skills/sdd-kb/scripts/kb_normativo.py sha sdd/kb/<slug>/fontes/<arquivo>`.

## Conflitos entre fontes

Em norma tributária, conflito é o normal: código de rejeição diferente na NT e no informe técnico, tag com dois nomes, ano riscado e reescrito. Registre na regra (`conflito_com`) e explique no `index.md`, seção `## Conflitos entre fontes`: as duas fontes, o que cada uma diz e o que a base adota até a próxima revisão. Não harmonize em silêncio. O validador exige que toda regra com conflito apareça nessa seção.

## Tabelas por vigência (`tabelas/`)

Uma pasta por data de **início** (`tabelas/2026-01-01/`), um arquivo por tabela (`aliquotas-referencia.json`, molde `TABELA_TEMPLATE.json`). `vigencia.de` igual ao nome da pasta; para a mesma tabela, a anterior fecha (`ate`) antes de a seguinte começar. Tabela que não mudou não ganha pasta nova — um arquivo por mudança, não por ano.

## Casos (`casos/`)

Entrada e resultado esperado de uma regra (molde `CASO_TEMPLATE.json`), com `data_fato` dentro da vigência da regra. É o gabarito que o software consumidor executa; o KB guarda, o software roda. Sem dado real: CNPJ, nome e chave de acesso fictícios.

## RULE_MAP

`python3 .agents/skills/sdd-kb/scripts/kb_normativo.py rule-map sdd/kb/<slug>` gera o `RULE_MAP.md`: cada regra com vigência, fonte (documento · localizador · degrau), status, conflito, implementação, teste, severidade e código. Não edite à mão — o validador compara com o gerado.

## KB consumido por software

Quando uma skill, um agente ou um sistema usa esta base:

1. Valide com `python3 .agents/skills/sdd-kb/scripts/validate_kb.py sdd/kb/<slug> --strict` — ele reprova base ainda `PENDENTE DE REVISÃO` e regra com `implementacao` sem um `teste` que exista.
2. Copie o `RULE_MAP.md` e referencie a regra **pelo id**, com o SHA-256 da fonte do catálogo. Não copie conceitos e receitas para dentro do software: quando a base mudar, a cópia não muda.
3. Preencha `implementacao` e `teste` nas regras que o software implementa e regere o RULE_MAP. Assim a rastreabilidade regra → fonte → código → teste mora num lugar só.
4. Ao atualizar a base, compare o SHA das fontes: hash diferente é texto diferente, mesmo com o mesmo nome de arquivo.

## Aviso de responsabilidade

O `index.md` normativo traz, sempre: a base **não é aconselhamento tributário**, contábil ou jurídico; quem responde pelo conteúdo é o profissional que revisou. O validador reprova o índice sem esse aviso.
