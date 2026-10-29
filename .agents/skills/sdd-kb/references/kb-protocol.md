# Protocolo da Base de Conhecimento

Referência de apoio da skill `sdd-kb`. Contém a taxonomia e as regras que o procedimento aplica.

---

## 1. A pergunta que classifica tudo

Antes de escrever qualquer arquivo, responda:

> **Depois de ler isto, a pessoa vai ENTENDER alguma coisa, ou vai FAZER alguma coisa?**

- **Entender** → é um `concept`.
- **Fazer** → é um `pattern`.

Essa única pergunta resolve a maior parte das dúvidas de organização. E o erro mais comum tem direção conhecida: as pessoas escrevem `concept` onde caberia `pattern`. O resultado é uma enciclopédia — tudo explicado, nada executável — que ninguém consulta na hora do trabalho.

Quando estiver em dúvida, pergunte o que a pessoa vai fazer logo depois de ler. Se ela vai executar passos, escreva os passos.

---

## 2. Os tipos

O núcleo são quatro, e todo domínio começa com eles:

| Tipo | O que é | Limite | Teste |
|---|---|---|---|
| `concept` | Modelo mental: o que é, por que existe, o que costuma ser confundido | 150 linhas | "depois de ler, eu **entendo**" |
| `pattern` | Receita executável: passos, sinal de sucesso, o que fazer quando dá errado | 200 linhas | "depois de ler, eu **faço**" |
| `quick-reference` | Consulta rápida: tabela de decisão, valores que se esquece, erros comuns | 100 linhas | "eu **decido** em segundos" |
| `index` | Porta de entrada: o que este domínio cobre, por onde começar, o que ele não cobre | — | "eu sei **se é aqui** e por onde começar" |

Quando o domínio cresce, três tipos de apoio aparecem — nenhum é necessário no começo:

| Tipo | Onde | O que é |
|---|---|---|
| `reference` | `reference/*.md` | Consulta exaustiva (lista completa, transcrição de norma, tabela longa). Sem limite de linhas: ninguém lê inteiro, consulta-se |
| `spec` | `specs/*.yaml` | O mesmo conhecimento em formato que um programa lê (catálogo, critérios, enum), com `source` e data de validação no topo |
| registro | bloco em `sdd/kb/_index.yaml` | Nome, descrição, caminho, perfil e data do domínio. Obrigatório — é o que torna o domínio encontrável |

No **perfil normativo** (`perfil: normativo` no registro), mais quatro, todos ligados a datas e fontes — detalhes em [normativo.md](normativo.md):

| Tipo | Onde | O que é | Obrigatório? |
|---|---|---|---|
| `rule` | `rules/*.md` | Regra atômica com vigência, fonte, status e (opcional) implementação e teste | sim, ≥ 1 |
| catálogo de fontes | `fontes/CATALOGO.md` | Cada documento citado, com degrau normativo, versão, data de captura e SHA-256 | sim |
| `tabela` | `tabelas/AAAA-MM-DD/*.json` | Valores por vigência — uma pasta por data de início | quando houver |
| `caso` | `casos/*.json` | Entrada e resultado esperado de uma regra (o antigo `test-case`) | quando houver |

O `RULE_MAP.md` não é um tipo que se escreve: é gerado a partir de `rules/`.

---

## 3. Por que existem limites de linha

Os limites não são preferência de estilo. Eles existem porque a IA que vai consultar este material carrega o arquivo **junto com todo o resto do contexto** da conversa. Um arquivo muito grande consome espaço que faria falta para o problema em si — e, na prática, o que acontece não é um erro visível: a IA começa a **ignorar partes** do que leu, silenciosamente.

Um arquivo de 400 linhas não é "mais completo". Ele é menos confiável, porque você não sabe qual metade foi efetivamente usada.

Quando um arquivo estoura o limite, quase sempre há dois assuntos dentro dele. Separar é melhor do que resumir: você mantém o conteúdo e recupera a confiabilidade.

---

## 4. O mínimo viável são quatro arquivos

Um domínio começa com:

```
sdd/kb/<slug>/
├── index.md              ← porta de entrada
├── quick-reference.md    ← consulta rápida
├── concepts/
│   └── {um-conceito}.md  ← pelo menos um
└── patterns/
    └── {uma-receita}.md  ← pelo menos um
```

Por que exatamente esses quatro: um domínio só com conceitos não ajuda a executar; um só com receitas não ajuda a decidir quando aplicá-las; sem `index` ninguém sabe por onde entrar; sem `quick-reference` quem já conhece precisa reler tudo.

Cresça acrescentando arquivos aos mesmos diretórios. Não crie estrutura nova antes de precisar dela.

---

## 5. O registro é obrigatório

Todo domínio precisa ser registrado no índice do projeto (`sdd/kb/_index.yaml`). Um domínio que existe em pasta mas não está no índice é **invisível**: quem consulta o índice não descobre que ele existe, e a IA não sabe que pode consultá-lo.

Isso não é hipótese. Em um acervo real de 43 domínios, 4 estavam fora do índice — bases inteiras que ninguém encontrava. Por isso o registro é o último passo obrigatório, e o validador reprova quem o pula.

Se o índice ainda não existe no projeto, crie-o a partir de `assets/KB_INDEX_TEMPLATE.yaml` na primeira vez. Nunca presuma que ele já está lá.

---

## 6. Escrever com procedência

Uma base de conhecimento vale pelo que se pode confiar nela. Duas regras:

1. **Diga de onde veio.** Cada arquivo declara a fonte no topo: documentação oficial, manual, norma, ou sua própria prática. "Prática do escritório" é uma fonte legítima e honesta.
2. **Marque o que não foi verificado.** Se você acha que é assim mas não confirmou, escreva que não confirmou. Uma linha marcada como incerta é útil; uma linha errada apresentada como certa contamina tudo em volta.

Detalhes em [sourcing.md](sourcing.md).

---

## 7. Anti-padrões

| ❌ Não faça | Por quê |
|---|---|
| Escrever `concept` que na verdade é receita | Vira enciclopédia que ninguém usa na hora do trabalho |
| Colocar passo a passo dentro de `concept` | O leitor procura execução em `patterns/` e não encontra |
| Estourar o limite "porque o assunto é grande" | O assunto grande são dois assuntos |
| Criar o domínio e não registrar | Base invisível |
| Copiar documentação inteira para dentro do KB | O KB é o que você aprendeu sobre aquilo, não uma cópia |
| Deixar `{placeholder}` do template | Sinal de arquivo não terminado; o validador reprova |
| Um `quick-reference` com explicação | Explicação pertence ao conceito; consulta rápida é lembrete |

---

## 8. Checklist de qualidade

No perfil normativo, somam-se: data-base no `index.md`; seção "Conflitos entre fontes"; aviso "não é aconselhamento tributário"; "Vale para:" em cada concept e pattern; toda regra com vigência e fonte catalogada; `RULE_MAP.md` regerado.


- [ ] Cada arquivo passou pelo teste "entender ou fazer"
- [ ] O mínimo de quatro arquivos existe
- [ ] Nenhum arquivo excede o limite do seu tipo
- [ ] Cada arquivo declara a fonte
- [ ] O que não foi verificado está marcado como tal
- [ ] `index.md` diz o que o domínio **não** cobre
- [ ] O domínio está registrado no índice
- [ ] Nenhum `{placeholder}` sobrou
