# Changelog

## 1.5.0 - 2026-11

- A skill passa a morar no SDD Open (era só do sdd-starter, que agora a recebe gerada do Open): linha de
  identificação com a versão do Open; o `agents/openai.yaml` sai da pasta e vira linha da tabela do gerador.
- Num projeto com a `sdd-ux-review`, o padrão fica em `sdd/UX_STANDARD.md` e é ela que o lê; a `ux-review`
  gerada vira opcional. Entrevista, regras, artefatos e validador não mudam.

## 1.4.0 - 2026-10

- Seção "Como falar com o aluno": 6 etapas com nome fixo (Modo · Público · Referências · Regras ·
  Governança · Gerar e entregar); toda resposta com status, o que foi feito, agora, decisão com opções e
  próximo passo; sem citar as próprias instruções. Glossário e exemplo em `references/como-falar.md`
  (novo no inventário).
- Entrevista, regras, governança, artefatos gerados, validador e cenários não mudam.

## 1.3.0 - 2026-10

- A `ux-review` gerada aplica 7 lentes cognitivas — Alcance (Fitts), Escolhas por passo (Hick-Hyman), Retomada (Zeigarnik), Convenção (Jakob), Progresso real (Gradiente de meta), Destaque único (Von Restorff), Agrupamento (Miller) — e o sinal de validação real. Elas recomendam e alertam, nunca bloqueiam: não geram `MUST`, não mudam o resultado do gate e nunca rebaixam uma regra existente; cada lente aponta a regra que manda quando há sobreposição (ex.: alvo abaixo de 24 px continua `MUST` pela `UX-CORE-005`).
- Jornada ganha a linha Interrupção → Retomada (análise, não estado obrigatório).
- O relatório ganha a seção de lentes, a linha das lentes no `Gate Outcome` e as recomendações `(lente Lx)` no handoff.
- Modo Evolução: regra derivada de lente nasce SHOULD ou COULD; bloquear exige regra própria.
- Validador: campo `warnings`. `LENTES_COGNITIVAS_AUSENTES` avisa modelo anterior à 1.3.0 e não reprova — bundles 1.2 continuam passando.
- 4 testes e 4 cenários comportamentais novos.

## 1.2.0 - 2026-10

- Versão e data no frontmatter (`metadata.updated`) e linha de identificação na primeira resposta, para quem baixou o .zip saber se a cópia envelheceu.

## 1.1.0 - 2026-09-30

- A `ux-review` gerada segue a pasta do SDD do método: `sdd/` na raiz do projeto (ou a pasta do SDD que o projeto já usa), com os documentos lado a lado, sem subpastas — a mesma pasta em que o Define grava e o Design lê.
- Entrega em dois caminhos: no chat, os três artefatos para download; no agente, os documentos na pasta do SDD e a `ux-review/` pronta para instalar.
- Texto revisado e acentuado; a entrevista descreve o que pergunta, sem rotular quem responde.
- Catálogo de referências renomeado para `references/CATALOGO_DE_REFERENCIAS.md`.
- Removidos os registros internos de construção da 1.0.0.
- Validador: aceita texto acentuado; recusa `ux-review` que aponte para subpasta (`SUBPASTA_SDD_NA_FILHA`) ou sem a regra de pasta completa (`REGRA_DE_PASTA_AUSENTE`); arquivo vazio é checado, não pulado; ID citado em exceção ou histórico não conta como duplicado; acha a `ux-review/` na raiz do projeto quando os documentos estão na pasta do SDD, ou recebe `--skill`.
- `UX-CORE-008` (Consistência) mantém a severidade-base `SHOULD` também no gate da `ux-review`.

## 1.0.0 - 2026-09-21

- Criada a meta-skill `ux-review-builder`.
- Entrevista progressiva, catálogo inicial de referências (Apple/iPhone, ChatGPT, Nubank, Notion, Linear, Stripe e combinações) e análise opcional de URL com separação observado/desejado/recomendado.
- Modos Criação e Evolução do `UX_STANDARD.md`; dez princípios universais; IDs canônicos estáveis; gate `MUST` antes do Design.
- Modelos para `UX_STANDARD.md`, skill `ux-review` e `UX_REVIEW_TEMPLATE.md`; validador estrutural e testes locais.
