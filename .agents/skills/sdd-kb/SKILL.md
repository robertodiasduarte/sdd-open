---
name: sdd-kb
description: "Constrói uma base de conhecimento (KB) que a IA consegue consultar de verdade: organiza o que você sabe sobre um domínio em conceitos (para entender) e receitas (para fazer), com porta de entrada, consulta rápida e limites de tamanho que mantêm o material utilizável. Grava em sdd/kb/, cria o índice do projeto na primeira vez e registra cada domínio novo. Para legislação e normas (perfil normativo), registra a vigência de cada regra, a fonte com SHA-256, os conflitos entre fontes e o mapa regra → fonte → teste. Recomendada antes de iniciar um fluxo SDD. A revisão do conteúdo é sempre do profissional: a IA organiza e redige, quem tem a responsabilidade técnica responde pelo que fica registrado. Use quando o usuário quiser ensinar seu contexto à IA, catalogar leis, normas, manuais ou políticas internas, documentar um processo, ou reclamar que precisa reexplicar as mesmas coisas em toda conversa."
compatibility: Requer python3 >= 3.9 (só stdlib) para o validador e bash >= 3.2 para o gate; sem filesystem, entrega os arquivos no chat.
license: MIT
metadata:
  author: Roberto Dias Duarte
  version: "2.2.1"
  updated: "2026-10"
---

# SDD KB

Na primeira resposta desta skill, comece com esta linha, uma vez só, antes do Status:
`sdd-kb v2.2.1 · out/2026 · versão atual: https://github.com/robertodiasduarte/sdd-open/releases/latest`

## Quick start

Transformar o que você sabe sobre um domínio em material que qualquer IA consulta sob demanda — em vez de você reexplicar tudo a cada conversa. A base mora em `sdd/kb/`: o índice em `sdd/kb/_index.yaml` e uma pasta por domínio.

1. Delimitar o domínio: o que entra, o que fica de fora — e perguntar se ele tem regra que vale por período (perfil **normativo**) e qual é a data-base.
2. Levantar o que você sabe, separando o que é **entender** do que é **fazer**.
3. Verificar se `sdd/kb/_index.yaml` existe; se não existir, criar.
4. Escrever o mínimo viável em `sdd/kb/<slug>/`: `index.md` + `quick-reference.md` + 1 conceito + 1 receita. No perfil normativo, também `fontes/CATALOGO.md`, ≥ 1 regra em `rules/` e o `RULE_MAP.md` gerado.
5. Respeitar os limites de tamanho de cada tipo.
6. Declarar a fonte de cada arquivo e marcar o que não foi verificado.
7. **Registrar o domínio no índice** — passo obrigatório.
8. **Pedir a revisão do profissional** — quem responde pelo conteúdo é ele, não a IA.

Consultar `.agents/skills/sdd-kb/references/kb-protocol.md` para a taxonomia e as regras, e `.agents/skills/sdd-kb/references/sourcing.md` para procedência. Os moldes estão em `.agents/skills/sdd-kb/assets/`, e `.agents/skills/sdd-kb/assets/example-kb/` é um KB completo de exemplo. Para o perfil normativo, ler `.agents/skills/sdd-kb/references/normativo.md` e usar `.agents/skills/sdd-kb/assets/example-kb-normativo/` como modelo. Use sempre esses caminhos, em `.agents/skills/`: a cópia que o `sync` gera para cada agente ganha um cabeçalho em cada arquivo, e um molde ou exemplo lido de lá sai com essas linhas.

## Quando usar / Quando não usar

Usar quando o usuário precisar que a IA conheça um contexto que ela não tem: leis, normas, manuais, instruções normativas, políticas internas, o processo do escritório, as regras de um cliente, uma ferramenta que ele domina. Usar também quando ele perceber que repete as mesmas explicações em toda conversa nova.

**Recomendada antes de iniciar um fluxo SDD** — com a base pronta, as fases seguintes partem do terreno já mapeado em vez de reconstruí-lo a cada conversa: a `sdd-define` só aceita no campo "KB Domains" os domínios que existem em `sdd/kb/`. Não é pré-requisito: o método funciona sem ela.

Não usar para documentar um projeto de software em construção — para isso existem os artefatos do fluxo SDD. Não usar para copiar documentação pública: o KB guarda o que **você aprendeu** sobre aquilo, principalmente o que a documentação não diz.

## Dados necessários

Entrada mínima:
- o domínio a documentar e o que o usuário já sabe sobre ele.

Entradas opcionais:
- documentação, manuais ou normas de referência;
- exemplos reais de como o processo acontece hoje;
- um KB anterior a expandir;
- acesso ao projeto para gravar os arquivos.

Não exigir acesso a filesystem ou internet. Sem acesso ao projeto, entregar os arquivos no chat.

### Assets obrigatórios de saída

Os moldes de `.agents/skills/sdd-kb/assets/` são **assets de saída**: sempre usá-los para gerar os arquivos finais, em vez de reconstruir a estrutura de memória.

| Molde (em `.agents/skills/sdd-kb/assets/`) | Gera |
|---|---|
| `INDEX_TEMPLATE.md` | `index.md` |
| `QUICK_REFERENCE_TEMPLATE.md` | `quick-reference.md` |
| `CONCEPT_TEMPLATE.md` | `concepts/*.md` |
| `PATTERN_TEMPLATE.md` | `patterns/*.md` |
| `KB_INDEX_TEMPLATE.yaml` | `sdd/kb/_index.yaml`, na primeira execução |

No perfil normativo, somam-se:

| Molde (em `.agents/skills/sdd-kb/assets/`) | Gera |
|---|---|
| `INDEX_NORMATIVO_TEMPLATE.md` | `index.md` (no lugar do `INDEX_TEMPLATE.md`) |
| `RULE_TEMPLATE.md` | `rules/*.md` |
| `CATALOGO_FONTES_TEMPLATE.md` | `fontes/CATALOGO.md` |
| `TABELA_TEMPLATE.json` | `tabelas/AAAA-MM-DD/*.json` |
| `CASO_TEMPLATE.json` | `casos/*.json` |

## Como falar com o aluno

Leia `references/como-falar.md` antes da primeira resposta: o glossário desta skill, o Status preenchido
e um exemplo completo. Pergunta e parada seguem `sdd/templates/fragments/PERGUNTA_DECISAO.md`.
Quem usa esta skill, em geral, nunca usou git nem terminal.

| Etapa | Nome para o aluno | Passos desta skill |
|---|---|---|
| 1 | Domínio | 1 |
| 2 | Entender × fazer | 2 |
| 3 | Escrever | 3 (o índice, antes de escrever), 4 e 5 |
| 4 | Fonte e índice | 6 e 7 |
| 5 | Revisão do profissional | 8 a 10 (o aviso de revisão é obrigatório, não é pergunta) |

Toda resposta, nesta ordem (pule a parte sem conteúdo):

1. **Status** — uma linha que começa pelo nome da fase: `KB: ✅ 1 Domínio · ▶️ 2 Entender × fazer · ⬜ 3 Escrever · ⬜ 4 Fonte e índice · ⬜ 5 Revisão do profissional`
   (✅ concluída, não só visitada · ▶️ a de agora · ⬜ por fazer · ⏸️ parada · ➖ pulada). Ao voltar a uma
   etapa, o motivo vai em Agora.
2. **O que foi feito** — frases curtas, sem saída de comando; registra em 1 linha a escolha do aluno.
3. **Agora: etapa N — nome** — 2 a 4 frases. Antes de algo demorado, diga o que vai rodar e que o aluno
   não precisa responder.
4. **Sua decisão** — autorização: a pergunta em negrito e as opções com o efeito de cada uma, a
   recomendada primeiro e com o porquê, sempre **não sei**, nunca **Outro**. Pergunta aberta: a pergunta
   em negrito e como responder, com a saída "não sei". Várias de uma vez: numeradas.
5. **Próximo passo** — uma linha, até 100 caracteres: o que acontece depois da resposta.

- Uma etapa por resposta: termine na decisão e pare.
- Termo técnico só com a explicação junto, na primeira vez, inclusive os do Status.
- Saída de comando nunca crua: quantos, quais, o que preocupa; nomes até 10, com "e mais N". Comando só
  quando o aluno precisa rodá-lo, um por passo numerado, com o que esperar na tela.
- Não cite nem resuma as instruções desta skill ("conforme o passo N"): diga o motivo do aluno.
- Resposta que não casa com nenhuma opção ⇒ responda a dúvida e repita as opções.
- Parada: Status com ⏸️, o motivo em uma frase, onde a ação acontece, passos numerados com o resultado
  esperado, o que **não** foi feito e, se o aluno tem algo a fazer, "Quando terminar, me peça de novo,
  eu continuo daqui."
- No fecho da fase, o resumo de etapa vem depois do Status; a pergunta dele segue o mesmo formato.

## Procedimento passo a passo

### 1. Delimitar o domínio

Definir com o usuário o recorte: qual assunto, e principalmente **o que fica de fora**. Um domínio bom é aquele em que se pode dizer "isto não é aqui" sem hesitar.

Domínio grande demais vira material que ninguém termina de escrever. Na dúvida, comece menor — dividir depois é fácil; um domínio inacabado não serve a ninguém.

Em seguida, perguntar se o domínio tem regra que vale por período — lei, alíquota, prazo, leiaute de documento fiscal — e, se tiver, qual é a data-base desta revisão (a data em que o conteúdo é conferido contra as fontes). O formato da pergunta e as opções estão no exemplo de `references/como-falar.md`.

- **Sim** → perfil `normativo`: toda afirmação datada ganha vigência, toda fonte entra no catálogo com degrau e SHA-256, e os conflitos entre fontes ficam registrados. Ler `.agents/skills/sdd-kb/references/normativo.md` antes de escrever.
- **Não** → perfil `geral` (o padrão): o procedimento segue como abaixo, sem os itens normativos.

Uma regra tributária não é verdadeira: é verdadeira **em um período**. Sem vigência, o arquivo que está certo hoje fica errado no ano que vem sem mudar uma linha.

### 2. Separar o que é entender do que é fazer

Levantar com o usuário o que ele sabe e classificar cada pedaço pela pergunta que resolve tudo:

> **Depois de ler isto, a pessoa vai ENTENDER algo, ou vai FAZER algo?**

- Entender → `concept`
- Fazer → `pattern`

Prestar atenção ao erro comum, que tem direção conhecida: escrever como conceito o que na verdade é receita. O sintoma é um texto que explica muito bem e não permite executar nada. Quando o usuário descrever uma sequência de ações, isso é `pattern` — escreva os passos.

### 3. Verificar (ou criar) o índice do projeto

O índice de KBs do projeto é `sdd/kb/_index.yaml`.

**Se não existir, criar** a pasta `sdd/kb/` e o índice a partir de `.agents/skills/sdd-kb/assets/KB_INDEX_TEMPLATE.yaml`. Nunca presumir que ele já está lá e nunca falhar por causa disso: o índice ausente é o estado normal na primeira vez.

### 4. Escrever o mínimo viável

Produzir exatamente esta estrutura:

```
sdd/kb/<slug>/
├── index.md
├── quick-reference.md
├── concepts/
│   └── <um-conceito>.md
└── patterns/
    └── <uma-receita>.md
```

Quatro arquivos. Cada um pelo molde correspondente.

No perfil **normativo**, o mínimo cresce:

```
sdd/kb/<slug>/
├── index.md              ← INDEX_NORMATIVO_TEMPLATE: Data-base, Conflitos entre fontes, aviso
├── quick-reference.md
├── concepts/<um>.md      ← com `> **Vale para:** <período>` no cabeçalho (até a linha 15)
├── patterns/<uma>.md     ← com "Vale para:" no cabeçalho
├── rules/<ID>.md         ← ≥ 1 regra, uma por arquivo, com vigência e fonte
├── fontes/CATALOGO.md    ← cada documento citado: degrau, versão, captura, SHA-256
└── RULE_MAP.md           ← gerado: python3 .agents/skills/sdd-kb/scripts/kb_normativo.py rule-map sdd/kb/<slug>
```

`tabelas/AAAA-MM-DD/` (valores por vigência) e `casos/` (entrada → resultado esperado) entram quando o domínio tem esse material. Mudou uma regra numa data? Feche a antiga com `ate:` e crie outra — o passado não se edita. Um domínio só com conceitos não ajuda a executar; um só com receitas não ajuda a decidir quando aplicá-las — por isso os dois são obrigatórios desde o começo.

Escrever mais de um conceito ou receita é bem-vindo quando o material existe. O mínimo é piso, não teto.

### 5. Respeitar os limites de tamanho

| Tipo | Limite |
|---|---|
| `quick-reference.md` | 100 linhas |
| `concepts/*.md` | 150 linhas |
| `patterns/*.md` | 200 linhas |

Explicar ao usuário **por que** existem, quando ele perguntar ou quando um arquivo estourar: a IA carrega o arquivo junto com todo o resto do contexto, e material grande demais não gera erro visível — ela passa a **ignorar partes** em silêncio. Um arquivo de 400 linhas não é mais completo; é menos confiável.

Estourou o limite? Quase sempre há dois assuntos no arquivo. Separar é melhor que resumir.

### 6. Declarar a fonte

Cada arquivo diz de onde veio o que está escrito: documentação, norma, ou prática própria — todas legítimas. E o que não foi verificado é **marcado como não verificado**, em uma frase.

Suposição escrita como fato é o erro mais caro de um KB: ela não se distingue do resto e se propaga com confiança. Ver `.agents/skills/sdd-kb/references/sourcing.md`.

No perfil normativo, a fonte tem **degrau** (Constituição > lei complementar > lei > decreto > ato normativo > ato técnico > solução de consulta > doutrina > prática própria). Regra sustentada só por doutrina ou prática própria fica `nao-confirmado`. E **a data do arquivo e o nome não provam vigência**: o catálogo registra versão, data de captura e SHA-256 (`python3 .agents/skills/sdd-kb/scripts/kb_normativo.py sha sdd/kb/<slug>/fontes/<arquivo>`).

Nunca incluir dados de pessoas reais, senhas ou chaves. Exemplos fictícios funcionam igual.

### 7. Registrar o domínio no índice

**Passo obrigatório, e o mais esquecido.** Acrescentar o bloco do domínio em `sdd/kb/_index.yaml`, com nome, descrição, caminho e data.

Um domínio que existe em pasta mas não está no índice é invisível: nem a pessoa nem a IA descobrem que ele existe. Em um acervo real de 43 domínios, 4 estavam nessa situação — bases inteiras que ninguém encontrava.

### 8. Entregar

Se houver filesystem de projeto gravável, gravar os arquivos em `sdd/kb/<slug>/`, sem sobrescrever silenciosamente material existente.

Se **não** houver filesystem acessível, entregar todos os arquivos no chat, em blocos separados e identificados pelo caminho, e fechar com estas três informações, nesta ordem:

1. que os arquivos **não foram gravados**;
2. a **estrutura de pastas sugerida** (com os nomes de arquivo, a partir de `sdd/kb/`);
3. **o que fazer com eles** — salvar na estrutura indicada e apontar a IA para essa pasta nas próximas conversas.

Nunca falhar em silêncio nem dar a entender que gravou.

### 9. Fechar com a revisão do profissional (obrigatório)

Antes de dar a base por pronta, deixar explícito que **a revisão do conteúdo é do usuário, não sua**:

> Revise cada arquivo antes de usar esta base para valer. Eu organizei e redigi, mas quem
> responde pelo que está escrito é você — principalmente onde há lei, norma, política ou
> prazo. Confira o que ficou registrado e corrija o que não estiver fiel à fonte.

Isso não é formalidade. Uma base de conhecimento é consultada **justamente quando a pessoa não
sabe** — ou seja, no momento em que ela não tem como perceber que a informação está errada. Um
erro aqui não fica isolado: é repetido com confiança, por você e pela IA, e passa a orientar
decisões. Quando o domínio envolve norma ou obrigação, o custo do erro é do profissional.

Apontar nominalmente os trechos que mais pedem conferência: números, prazos, valores, condições
de aplicação de regra, e tudo que ficou marcado como não verificado (passo 6).

Se o usuário disser que não vai revisar agora, registrar no `index.md` que a base está
**pendente de revisão** — melhor uma base marcada como não conferida do que uma que aparenta
autoridade que ainda não tem.

No perfil normativo, o aviso vai também no `index.md`, por escrito: **esta base não é
aconselhamento tributário**, contábil ou jurídico. E uma base pendente de revisão não deve
alimentar software: `validate_kb.py --strict` reprova o domínio normativo marcado como
`PENDENTE DE REVISÃO` e a regra com `implementacao` que não aponta um `teste` existente — rode-o
antes de qualquer skill, agente ou sistema consumir a base.

### 10. Mostrar como usar daqui em diante

Fechar dizendo, em duas ou três linhas, como o usuário passa a consultar isto: apontar a IA para `sdd/kb/<slug>/` no início da conversa, ou pedir que ela leia o `index.md` antes de responder sobre o assunto. Num fluxo SDD, o nome da pasta vai no campo "KB Domains" do DEFINE.

Um KB que o usuário não sabe acionar não muda nada no dia a dia dele.

## Validações e checklist de qualidade

Antes de declarar concluído, verificar:

- [ ] Domínio delimitado, com o que fica de fora explícito no `index.md`.
- [ ] Cada arquivo passou pelo teste "entender ou fazer".
- [ ] Nenhuma receita foi escrita como conceito.
- [ ] Os quatro arquivos do mínimo viável existem em `sdd/kb/<slug>/`.
- [ ] Nenhum arquivo excede o limite do seu tipo.
- [ ] Cada arquivo declara a fonte.
- [ ] O não verificado está marcado como tal.
- [ ] Nenhum dado de pessoa real, senha ou chave.
- [ ] O domínio está registrado em `sdd/kb/_index.yaml`.
- [ ] Nenhum placeholder entre chaves sobrou.
- [ ] O usuário foi avisado de que a revisão do conteúdo é dele, com os trechos críticos apontados.
- [ ] Base não revisada está marcada como pendente de revisão no `index.md`.
- [ ] O usuário sabe como consultar o KB nas próximas conversas.

No perfil normativo, também:

- [ ] Data-base no `index.md`, seção "Conflitos entre fontes" e o aviso "não é aconselhamento tributário".
- [ ] "Vale para:" no cabeçalho de cada conceito e receita.
- [ ] Cada regra com vigência (`de`, e `ate` quando encerrada), fonte catalogada com localizador e status honesto.
- [ ] Cada fonte no catálogo com degrau, versão, data de captura e, quando o arquivo está em `fontes/`, SHA-256.
- [ ] Regra que um software implementa tem `implementacao` e `teste` (o caminho do arquivo de teste a partir da raiz do projeto).
- [ ] `RULE_MAP.md` regerado depois da última mudança em `rules/`.

Quando houver filesystem, o validador confere mecanicamente parte disso, da raiz do projeto:

```
python3 .agents/skills/sdd-kb/scripts/validate_kb.py sdd/kb/<slug>            # escrever
python3 .agents/skills/sdd-kb/scripts/validate_kb.py sdd/kb/<slug> --strict   # antes de software consumir
```

Saída `PASS` com código 0; problemas listados com código 2; uso errado, 64. Linhas `WARN:` (base pendente de revisão, data-base antiga, domínio geral que parece normativo) não mudam o código de saída. O perfil vem do registro do domínio em `sdd/kb/_index.yaml`. As mensagens do validador são em inglês: traduza para o aluno (quantos problemas, quais, o que preocupa).

Para provar que o validador desta instalação discrimina — aceita os exemplos e rejeita 12 casos ruins, cada um pelo motivo certo — rode `bash .agents/skills/sdd-kb/scripts/gate.sh`. Uma linha `RESULTADO: VERDE` com as contagens, exit 0.

## Tratamento de exceções

- **Domínio grande demais:** propor um recorte menor e nomear os domínios vizinhos que ficam para depois. Registrar no `index.md` o que não é coberto.
- **Usuário só tem conceitos, nenhuma receita:** perguntar o que ele **faz** com aquele conhecimento. Quase sempre a receita existe e não foi verbalizada.
- **Usuário só tem receitas:** perguntar por que os passos são assim. O conceito costuma estar na resposta.
- **Índice do projeto não existe:** criar `sdd/kb/_index.yaml` a partir do molde. É o estado normal na primeira vez, não um erro.
- **Já existe KB deste domínio:** expandir o existente — novos conceitos e receitas nos mesmos diretórios — em vez de criar domínio paralelo.
- **Arquivo estourou o limite:** procurar os dois assuntos dentro dele e separar. Resumir só quando genuinamente for um assunto só.
- **Sem filesystem:** entregar tudo no chat com as três informações do passo 8.
- **Material com dado real:** trocar por exemplo fictício equivalente antes de escrever.
- **Duas fontes dizem coisas diferentes:** registrar o conflito na regra (`conflito_com`) e no `index.md`, dizer o que a base adota e por quê. Nunca escolher em silêncio.
- **Regra mudou:** fechar a regra antiga com `ate:` e criar outra a partir da nova data; regerar o `RULE_MAP.md`.
- **Software vai consumir a base:** `--strict` antes; o software referencia regra por id e fonte por SHA-256, sem copiar conceitos, e cada regra implementada aponta o teste que o Verify Gate do DEFINE roda (ver "KB consumido por software" em `.agents/skills/sdd-kb/references/normativo.md`).
- **O gate saiu vermelho:** a linha `🛑` diz o caso e a linha `→` o conserto; traduza para o aluno. Rodado da cópia gerada pelo `sync`, ele recusa e aponta o de `.agents/skills/`.

## Examples

**Processo do escritório**
`Quero que a IA saiba como funciona o fechamento mensal aqui.`

Delimitar (fechamento contábil, sem apuração de tributos), separar o conceito que explica as decisões da receita que executa as conferências, escrever os quatro arquivos em `sdd/kb/fechamento-mensal/`, registrar.

**Ferramenta que o usuário domina**
`Uso essa ferramenta há anos e toda vez preciso reexplicar pra IA.`

Levantar o que ele sabe que a documentação não diz — armadilhas, o que dá errado, quando não usar. É exatamente o material que falta à IA.

**Legislação com vigência**
`Quero uma base da Reforma Tributária para alimentar meu validador de NF-e.`

Perfil normativo, data-base perguntada no passo 1. Cada regra da nota técnica vira um arquivo em `rules/` com vigência e página; a NT, a lei complementar e as reportagens consultadas entram no catálogo com degrau; o "2026 riscado, 2027 escrito por cima" vira conflito registrado. `kb_normativo.py rule-map` gera o `RULE_MAP.md` (o `validate_kb.py` só confere que ele não derivou), e o validador de NF-e referencia cada regra por id, com o teste de cada uma na coluna Teste.

**Conhecimento disperso**
`Tenho anotações espalhadas sobre isso.`

Ler o material, classificar cada pedaço em entender/fazer, e mostrar ao usuário o que ficou de fora do recorte antes de escrever.

**Sem filesystem**
`(no chat da web) Monta uma base de conhecimento disso aqui.`

Entregar os quatro arquivos no chat, identificados pelo caminho, com a estrutura de pastas e a instrução de como apontar a IA para eles depois.

## Next Step

Base de conhecimento criada em `sdd/kb/<slug>/`. Aponte a IA para essa pasta no início das próximas conversas sobre o assunto; se a base prepara uma feature, o próximo passo é `/sdd-brainstorm`.

---

Parte do SDD Open by RDD — https://github.com/robertodiasduarte/sdd-open
