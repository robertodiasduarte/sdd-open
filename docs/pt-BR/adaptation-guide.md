<!-- Idioma: [English](../adaptation-guide.md) · **Português** -->

# Guia de adaptação

> *Tradução do [documento canônico em inglês](../adaptation-guide.md). Em caso de divergência, o original vale.*

O SDD Open foi extraído de um único codebase de produção. Este documento marca as costuras — o que
é genérico, o que você precisa configurar, e o que foi deliberadamente deixado de fora por ser
específico de onde ele veio.

## O que você precisa configurar

Tudo que é específico do projeto vive no `sdd/config.yaml`. Os comandos referenciam slots; eles
nunca fixam um comando no código.

```yaml
project:
  name: your-project
  test_cmd: "npm test"              # {{TEST_CMD}}
  typecheck_cmd: "tsc --noEmit"     # {{TYPECHECK_CMD}}

deploy:
  cmd: "./deploy.sh production"     # {{DEPLOY_CMD}}
  drift_check_cmd: ""               # {{DRIFT_CHECK_CMD}} — see "drift" below

release:
  landmines_cmd: "bash {{LANDMINES_CMD}}"   # {{LANDMINES_CMD}}
  changelog_hook: ""                # {{CHANGELOG_HOOK}}

prompts:
  builder_skill: "sdd-prompt-builder"   # já vem preenchido; troque pela sua se tiver outra
  wrapper_pattern: ""                   # se o projeto chama a IA por uma função própria: a expressão do parâmetro
                                        # dela, ex.: "systemPrompt:" ou "callLLM\\("; veja docs/pt-BR/llm-in-code.md
```

## O ponto de extensão que mais importa: landmines

O slot `release.landmines_cmd` do [`sdd/config.yaml`](../../sdd/config.example.yaml)
(`{{LANDMINES_CMD}}` nas skills) vem **vazio**: o release roda o seu script quando você o preenche.
Uma boa primeira versão tem três regras genéricas — um segredo literal em arquivo versionado, uma
migration aplicada fora de banda sem commit correspondente, e uma árvore de trabalho suja na hora do
release.

Esse vazio é deliberado. No codebase de onde isto veio, aquele script carrega dezenas de regras, e
cada uma delas é uma cicatriz: uma queda específica, uma falha silenciosa específica, uma
descoberta específica às 2h da manhã. Essas regras não valem nada pra você — elas nomeiam tabelas,
fornecedores e funções internas que você não tem — e publicá-las teria sido um inventário dos
pontos fracos de um sistema privado.

**O que se transfere é o hábito:** depois de cada incidente, codifique a detecção como um grep e
adicione na sua cópia. A estrutura do script suporta isso diretamente:

```bash
crit "secret literal in tracked file" \
  "$(diff_added | grep -nE '(sk-[A-Za-z0-9]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY)')"

warn "migration applied out of band has no matching commit" \
  "$(your_check_here)"
```

`crit` bloqueia o release, `warn` faz aparecer no veredito, `info` registra. Um framework não pode
entregar os seus post-mortems; pode entregar o lugar onde colocá-los.

## Drift: coisas deployadas fora do git

Se o seu projeto consegue deployar sem um commit — uma função serverless publicada por um console,
uma migration aplicada por um dashboard, uma config alterada numa UI — então o seu repositório pode
silenciosamente deixar de descrever o que está rodando. É pra esse modo de falha que o
`{{DRIFT_CHECK_CMD}}` existe.

Se tudo que você deploya passa pelo git, deixe vazio. Se não, escreva uma checagem que compare o
que está deployado com o que está commitado, e ligue ela ali. O fluxo de release vai executá-la na
fase de pré-voo.

## Smoke e checagem de schema: quatro slots rodados pelo `sdd/bin/slot.sh`

Quatro slots do [`sdd/config.yaml`](../../sdd/config.example.yaml) recebem um comando seu, rodado num momento fixo
por `bash sdd/bin/slot.sh <chave>`. Os quatro vêm **vazios**: slot vazio é pulado, e a fase diz que pulou.

| Slot | Quando | Exit `2` significa |
|---|---|---|
| `smoke.before_ok_cmd` | release, item 6b: depois de landar, antes do bloco do OK, sobre o commit que vai subir | FAIL-candidato no bloco do OK (corrigir, ou WAIVED com o seu motivo) |
| `smoke.before_push_cmd` | release, item 7b: depois do "sim", antes do push (a produção ainda roda o código velho) | só registro; nada segura o push |
| `smoke.after_deploy_cmd` | release, item 10: com o deploy confirmado | a release para e pergunta: reverter, corrigir ou seguir com motivo |
| `schema.check_cmd` | build, passo 4b: antes da prévia das migrations a aplicar | a migration **não** é aplicada |

O seu comando responde `0` ok · `2` reprovou · `10` nada a medir. Qualquer outro exit — ou um sinal — é
inconclusivo (o `slot.sh` sai `3`), nunca verde; slot vazio sai `11`, chamada ou config quebrado, `64`.

Ele roda na raiz do repositório, com os arquivos (os `.sql` da checagem de schema) no fim, um por argumento, e com
`SDD_MOMENTO`, `SDD_FEATURE`, `SDD_BASE`, `SDD_COMMIT` (o commit a medir), `SDD_ARVORE` (a pasta com a árvore
desse commit: antes do OK, o worktree temporário da release) e `SDD_SLOT_DIR`. Esta última é uma pasta fora do
repositório, a mesma nos três momentos do smoke de uma feature, de qualquer worktree: é por ela que o seu "antes"
e o seu "depois" se encontram. Ela é esvaziada no `before_ok`. Uma linha só, sem comentário `#` no comando; com
`|`, `;` ou `&&`, aponte para um script. Um smoke que mede uma página deve medir `SDD_COMMIT`/`SDD_ARVORE`, não a
pasta onde roda.

## Trabalho paralelo: worktrees

O fluxo assume que uma feature é desenvolvida numa branch a partir da branch default, e funciona
bem com `git worktree` quando várias features rodam ao mesmo tempo. O framework não exige
worktrees — ele exige que você não desenvolva na branch de onde você deploya.

Uma ressalva que vale internalizar se você adotar paralelismo pesado: com muitas worktrees vivas ao
mesmo tempo, as specs de cada uma descrevem futuros divergentes, e a verdade canônica fica
borrada. Essa é uma limitação real do framework hoje (veja [comparison.md](comparison.md) — o
specs-as-diffs do OpenSpec é uma resposta melhor, e está no roadmap).

## Agentes e modelos

O framework é agnóstico de modelo em princípio, com duas ressalvas práticas:

- **`/sdd-build --mode briefs` assume que existe um modelo barato** para workers paralelos, e exclui
  dele, por regra dura, itens de superfície de segurança e de prompt-engineering. Se você não tem
  uma estratégia de tiering, ignore esse modo; o loop in-context default é o caminho recomendado.
- **O review adversarial assume um segundo fornecedor.** O valor dele vem de um perfil de erro não
  correlacionado — uma família de modelo diferente revisando o trabalho da primeira. Revisar com o
  mesmo modelo que escreveu o código te dá concordância, não review.

Nomes de modelo estão deliberadamente ausentes das skills e dos templates: eles envelhecem mal. A revisão
adversarial é a exceção que confirma a regra — as engines e os modelos dela moram em
`sdd/review/registry.tsv` e `sdd/review/precos.tsv`, uma linha cada, e trocar de modelo é uma edição;
escolha os seus no `sdd/config.yaml` (`review.revisor1`, `review.auditor`). Veja
[adversarial-review.md](adversarial-review.md).

## O que ficou de fora, e por quê

| Deixado de fora | Por quê |
|---|---|
| Regras concretas de landmine | Cada uma documenta um incidente privado específico; inútil em outro lugar, imprudente de publicar |
| Skills de domínio (importação de dados, consulta de cadastro, fluxos de publicação) | Regra de negócio de um produto, não framework |
| Convenções da camada de memória/conhecimento | Uma camada privada de fatos acumulados do projeto; o framework não depende dela |
| Pipeline de deploy, ligação com CI, configuração de host | O seu vai diferir em cada detalhe |

## Encaixando no CI

A integração mínima útil é rodar o gate da spec que um pull request implementa:

```yaml
- run: sdd/bin/verify-gate.sh sdd/features/DEFINE_${{ env.FEATURE }}.md
```

Trate os exits `3` e `4` deliberadamente: `3` significa que falta algo no runner do CI (muitas
vezes é correto ignorar no CI e resolver localmente), `4` significa que um humano precisa assinar —
o que um job de CI não pode fazer por você. Mapear qualquer um dos dois para verde derrota o
mecanismo.
