---
regra: {ID-ESTÁVEL — nunca reaproveitar nem renumerar}
titulo: {uma linha: o que a regra exige}
vigencia:
  de: {AAAA-MM-DD}
  ate: null
fonte:
  id: {id em fontes/CATALOGO.md}
  localizador: {página, artigo, inciso ou seção onde a regra está escrita}
status: {confirmado | premissa | nao-confirmado}
conflito_com: []
implementacao: null
teste: null
severidade: null
codigo: null
---

# {ID} — {título}

## O que a regra diz

{A regra em 1-3 frases, fiel à fonte. Citação literal curta quando a redação importa.}

## Como esta base aplica

{A leitura adotada. Se for interpretação sem texto normativo explícito, o status é `premissa` e isto diz por quê.}

---

> **Uma regra por arquivo.** Mudou a regra numa data? Feche esta com `ate:` e crie outra a partir da nova data — o passado não se edita.
> `status: confirmado` exige fonte de degrau normativo (até `solucao-de-consulta`); artigo, curso ou prática própria sustentam no máximo `nao-confirmado`.
> `conflito_com` lista ids de regras ou de fontes do catálogo; todo conflito é explicado em `index.md › Conflitos entre fontes`.
> `implementacao` e `teste` apontam para o software que consome a regra (`scripts/engine.py:vbc`) e para o arquivo de teste, como caminho a partir da raiz do projeto (`tests/test_engine.py::test_vbc`), não um comando — `null` enquanto ninguém implementou. O `--strict` reprova regra implementada sem teste, ou com teste que não existe.
> Frontmatter: `chave: valor`, um nível de aninhamento com 2 espaços, listas `[a, b]`, `null`. Depois de editar, rode `python3 .agents/skills/sdd-kb/scripts/kb_normativo.py rule-map sdd/kb/<slug>`.
