<!-- Idioma: [English](../adversarial-review.md) · **Português** -->

# Revisão adversarial

`sdd/bin/adversarial-review.sh` pede a uma engine (o modelo de IA que revisa) que **revise** um diff
congelado, e a **outra** engine que **audite** essa revisão — o auditor não revisa o código de novo: dá um
veredito para cada achado e aponta o que a revisão deixou passar. Revisor e auditor rodam em cadeia, nunca
em paralelo: dois revisores lado a lado acham menos do que um revisor seguido de um crítico.

Um 2º revisor e um desempate entram sozinhos quando o diff pede. A saída é uma pasta que o
`sdd/bin/sdd-fluxo.sh loop` lê para decidir se o trabalho segue, se corrige ou se precisa de você.

## O que você preenche

Dois slots no `sdd/config.yaml` — `review.revisor1` e `review.auditor` —, com ids de `sdd/review/registry.tsv`:

```yaml
review:
  revisor1: claude                    # quem revisa; uma lista por vírgula é a cadeia (a 1ª é a padrão)
  auditor: openrouter:qwen/qwen3.7-plus  # quem audita — precisa ser outra engine
```

O registry vem com `claude`, `codex` (sempre `-s read-only`), `gemini` e `openrouter`, uma linha cada, e
**sem cadeia padrão**: com os slots vazios, a skill pergunta. `openrouter:<modelo>` usa a linha `openrouter`
com outro modelo. Engine nova é uma linha no registry (mais um adapter em `sdd/bin/adapters/`, se for uma
CLI nova). Os nomes de modelo moram no registry e em `sdd/review/precos.tsv`.

A pasta das revisões (`review.output_dir`, padrão `sdd/reports/reviews`) precisa estar ignorada pelo git —
o diff e as respostas das engines não vão para o repositório:

```bash
printf '%s\n' 'sdd/reports/reviews/' >> "$(git rev-parse --git-common-dir)/info/exclude"
```

## Como rodar

```bash
bash sdd/bin/adversarial-review.sh --feature MINHA_FEATURE           # revisa o diff da branch
bash sdd/bin/adversarial-review.sh --feature MINHA_FEATURE --dry-run # mostra o plano, não chama nada
```

- **Diff congelado:** a partir do merge-base com `origin/<branch padrão>`, com os arquivos novos não
  rastreados incluídos e as pastas de artefatos SDD de fora (elas entram como contexto). O `sha256` dele
  fica no `META.txt`.
- **Contexto SDD:** BRAINSTORM, DEFINE, DESIGN e BUILD_REPORT de `--feature`, até `review.context_max_kb`
  (180); o BRAINSTORM sai primeiro.
- **2º revisor** quando o diff toca superfície de segurança (`review.security_globs`, `layers.sql`, um trecho
  de caminho como `auth` ou `token`), tem 8+ arquivos, 120+ KB, toca 2+ camadas, ou o revisor foi raso
  (menos de 30 s sem achados). É a 1ª engine disponível do registry que não é o revisor nem o auditor. A
  falha dele nunca para a cadeia: o auditor roda assim mesmo, e o `loop` pede que você restaure uma engine
  ou dispense o 2º revisor naquela rodada.
- **Desempate** quando o auditor refuta um HIGH com evidência: uma engine fora da origem do achado e do
  auditor decide `DECISAO:PROCEDE` ou `DECISAO:REFUTADO`.

## Custo

Cada papel registra tokens e custo no `META.txt`, mais o total. O custo é o que a engine reporta (`US$`);
senão, uma estimativa pelo `sdd/review/precos.tsv` (`≈US$`); senão `assinatura` (incluído num plano); senão
`$?` — custo desconhecido nunca aparece como 0. O preço é o do modelo que respondeu: um modelo reportado
diferente do configurado, sem linha própria no `precos.tsv`, é `$?`. Uma chamada que estourou o teto de
tempo numa engine paga por token pode ter sido cobrada sem reportar, então o papel mostra `US$ x + $?`. Atualize o `precos.tsv` pela lista pública de preços do
provedor, com a URL e a data; nunca de memória.

## Privacidade

- As chamadas ao OpenRouter levam `provider.data_collection = "deny"` e `require_parameters = true`: só
  entram provedores que não retêm nem treinam com o dado. A chave vem só de `OPENROUTER_API_KEY` no
  ambiente — nunca de um arquivo, nunca num argumento.
- As CLIs rodam numa pasta temporária vazia, com o prompt por stdin e sem ferramenta de escrita
  (`claude --tools "" --safe-mode`, `codex -s read-only`, `gemini --approval-mode default`). Ferramentas de
  leitura podem continuar; o prompt diz que nenhuma é necessária.

## Exits e o que fazer

| Exit | `RESULTADO:` | O que quer dizer | O que fazer |
|---|---|---|---|
| 0 | REVIEW COMPLETA | revisor e auditor responderam no formato | `bash sdd/bin/sdd-fluxo.sh loop --review <pasta> …` |
| 64 | PAROU | uso, slot vazio, id desconhecido, diff vazio, diff acima de 8 MB, pasta não ignorada | a linha depois do `→` |
| 65 | PAROU | falha de credencial — a revisão **nunca** troca de engine por isso | conserte a credencial que o `→` nomeia |
| 66 | PAROU | CLI fora do `PATH`, e nenhuma outra engine na lista | instale a CLI ou acrescente uma engine à lista |
| 67 | PAROU | auditor = revisor, ou todas as engines da lista sem cota | escolha outro auditor, `--um-engine`, ou acrescente uma engine |
| 68 | REVIEW INVÁLIDA | uma resposta sem o bloco de vereditos — **nunca** "zero achados" | rode de novo; se repetir, troque aquela engine |

Um 429 (limite por minuto) é tentado de novo 2 vezes na mesma engine; cota, cobrança e tempo esgotado passam
para a próxima engine da lista, com uma linha ⚠️ dizendo quem respondeu no lugar.

## Uma engine só

`--um-engine` deixa a mesma engine revisar e auditar, em chamadas separadas. O `META.txt` e o ledger da
release registram `diversidade: nenhuma`, e a saída avisa: a auditoria tem os mesmos pontos cegos da
revisão. Mais fraca, mas honesta — e nunca em silêncio.

## Na release

A `sdd-release` exige um review externo **desta** versão do código:

```bash
bash sdd/bin/adversarial-review.sh --conferir    # 0: imprime a linha review_externo para o ledger
bash sdd/bin/adversarial-review.sh --ledger sdd/releases/<F>/<arquivo>.yaml   # 0: o ledger tem a linha
```

O `--conferir` recalcula o diff e compara o `sha256`. Sem uma revisão que confira, a release pergunta — antes
do OK único — se roda a revisão agora ou se publica sem ela, com um motivo escrito que vai para o ledger como
`review_externo: dispensado — <motivo>`. O `--ledger` roda na pasta da frente, logo depois do commit da
release: a pasta da revisão é ignorada pelo git e só existe ali.

Quando o diff pedia um 2º revisor e a revisão rodou com `--no-revisor2`, o `--conferir` não a aceita sozinha:
acrescente `--aceitar-sem-revisor2 "<motivo>"`, e o motivo vai para a linha do ledger como
`revisor2=dispensado — <motivo>`.

## Gate offline

```bash
bash sdd/bin/adversarial-review-gate.sh       # -v mostra também o valor lido em cada conferência
```

Ele roda a revisão de ponta a ponta com os adapters **reais**, contra stubs que respondem no formato de cada
engine (`sdd/review/stubs/`: um JSON como o do `claude -p`, o JSONL do `codex exec`, o JSON do
`gemini -o json` e um servidor HTTP local com a forma da API da OpenRouter). Confere no `META.txt` o que cada
adapter extraiu — vereditos, engine e modelo, tokens, custo — e o contrato (exits 65, 67, 68; 429 tentado de
novo na mesma engine; cota passando para a próxima; nenhuma engine chamada fora do roteiro de cada cenário; a
chave nunca num arquivo). Sem rede e sem crédito: os proxies apontam para uma porta morta, a chave é falsa e
gerada na execução, e as CLIs no `PATH` dos adapters são os stubs (uma função exportada ou um `BASH_ENV` não
conseguem trocá-las).

| Exit | `RESULTADO:` | Significado |
|---|---|---|
| 0 | GATE VERDE | todas as conferências passaram |
| 2 | GATE VERMELHO | alguma falhou; cada ❌ diz o campo e o valor lido |
| 3 | GATE QUEBRADO | o gate não conseguiu se isolar (stub ausente, registry sem as 4 engines, CLI real à frente no shell dos adapters); nada foi chamado |
| 64 | PAROU | uso |

O gate prova as 4 engines do pacote (`sdd/review/registry.tsv` ao lado de `sdd/bin/`), não engines que você
acrescentou. Os textos de falha dos stubs são sintéticos (marcados no `cenarios.tsv`): uma CLI que muda a
mensagem de erro é pega pela revisão real, não aqui. Uma CLI que muda o formato de saída: atualize o
`<engine>.py` dela e as linhas dela no `cenarios.tsv`.

## eval-agree

```bash
bash sdd/bin/eval-agree.sh [<pasta das revisões>]   # padrão: review.output_dir
```

Lê as revisões já feitas (`EXTERNAL_REVIEW_*/META.txt` e `auditor.verdicts.jsonl`) e mostra, por auditor
(engine e modelo), quantos vereditos foram AGREE, DISAGREE_EVIDENCE, DISAGREE_CONCERN e NOVO, e a
`taxa_agree` = AGREE / (AGREE + DISAGREE_EVIDENCE + DISAGREE_CONCERN). Um auditor que quase sempre concorda
pode não estar auditando: compare com outra engine no papel de auditor. A taxa reflete os diffs que este
projeto revisou, não um benchmark. Nunca chama engine. Exits: `0` MEDIDO · `2` SEM DADOS (também quando a pasta padrão ainda não existe) ·
`64` uso, ou uma pasta passada que não existe.

## Limites

- As engines veem só o diff e o contexto SDD: não veem produção, o banco nem um deploy feito fora do git.
- Um projeto que instalou o pacote antes desta versão recebe `sdd/review/` e `sdd/bin/adapters/` pelo `init`
  (ele completa o que falta), mas fica com o `sdd/config.yaml` antigo: acrescente os slots `review.*` à mão,
  a partir do `sdd/config.example.yaml`.
