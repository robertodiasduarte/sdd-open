<!-- Idioma: [English](../quickstart.md) · **Português** -->

# Quickstart

Do zero a um gate bloqueante em dez minutos — no agente que você já usa.

## O seu agente, em uma linha

| Agente | Instalar | Invocar uma fase | O que é gerado para ele |
|---|---|---|---|
| **Claude Code** | `bash sdd-open/bin/sdd-open.sh init --vendors claude` | `/sdd-define …` | `CLAUDE.md` (1 linha: `@AGENTS.md`) + cópias em `.claude/skills/` |
| **Codex CLI** | `… init --vendors codex` | peça pela descrição ou `$sdd-define` | **nada** — lê `AGENTS.md` e `.agents/skills/` nativamente |
| **Gemini CLI** | `… init --vendors gemini` | `/sdd-define …` (skill) | `GEMINI.md` + `context.fileName` em `.gemini/settings.json`; skills via `.agents/skills/`. ⚠️ CLI 0.22.x aponta para modelos aposentados por padrão: passe `-m gemini-3.7-flash` (ou o atual). Conta Workspace com login em cache exige `GOOGLE_CLOUD_PROJECT`; alternativa: `GEMINI_API_KEY` + `"security":{"auth":{"selectedType":"gemini-api-key"}}` no `settings.json` |
| **Cursor** | `… init --vendors cursor` | `/sdd-define …` | cópias em `.cursor/skills/` |
| **Kimi Code** | `… init --vendors kimi` | `/skill:sdd-define …` | **nada** — lê `AGENTS.md` e `.agents/skills/` nativamente |
| **Grok Build** · **GLM via Claude Code** | `… init --vendors claude` | `/sdd-define …` | o mesmo do Claude Code (ambos leem `CLAUDE.md` e `.claude/`) |

Vários agentes no mesmo projeto: `--vendors claude,codex,gemini`.

## Por agente

### Claude Code
`init --vendors claude`. Gera `CLAUDE.md` com a linha `@AGENTS.md` (import) e copia as skills para
`.claude/skills/`. Invoque `/sdd-define …`. Hooks e subagentes do Claude Code funcionam normalmente
com as skills.

### Codex CLI
`init --vendors codex`. Nada é gerado: o Codex lê `AGENTS.md` e `.agents/skills/` nativamente. Peça a
fase pela descrição ("rode a fase Define sobre …") ou use `$sdd-define`. Provado headless em
2026-09-05: `codex exec -s workspace-write "…"` produziu um DEFINE com gate parseável em 154 s.

### Gemini CLI
`init --vendors gemini`. Gera `GEMINI.md` e acrescenta `AGENTS.md` a `context.fileName` em
`.gemini/settings.json`; as skills vêm de `.agents/skills/` (alias nativo). ⚠️ O CLI 0.22.x usa modelos
aposentados por padrão: passe `-m gemini-3.7-flash` (ou o modelo atual). Conta Workspace com login em
cache pede `GOOGLE_CLOUD_PROJECT`; alternativa: `GEMINI_API_KEY` +
`"security":{"auth":{"selectedType":"gemini-api-key"}}` em `.gemini/settings.json`. Provado headless
em 2026-09-05: 64 s, e o agente fechou com o micro-kanban do resumo de etapa.

### Cursor
`init --vendors cursor`. Copia as skills para `.cursor/skills/` (o Cursor não lê `.agents/`). AGENTS.md
é lido nativamente. Invoque `/sdd-define …`.

### Kimi Code
`init --vendors kimi`. Nada é gerado: lê `AGENTS.md` e `.agents/skills/` (também `.kimi/skills`).
Invoque `/skill:sdd-define …`.

### Grok Build e GLM via Claude Code
`init --vendors claude`. O Grok Build lê `CLAUDE.md`, `.claude/` e `AGENTS.md` sem configuração. O GLM
roda dentro do Claude Code (`ANTHROPIC_BASE_URL` apontando para o provedor) e herda o mesmo adaptador.

> **Em CI ou pipeline:** `init` e `sync` pedem confirmação e, sem terminal interativo, saem
> `RESULTADO: CANCELADO` sem escrever nada. Passe `--yes`.

## 0. Vale usar o fluxo inteiro?

| A mudança é… | Faça |
|---|---|
| descritível em uma frase, raio pequeno | pule as fases; converse com o modelo, rode seus testes |
| um bug com causa conhecida | `/sdd-define` (spec de bug precisa de um `shall continue to`) e `/sdd-build` |
| comportamento novo, vários arquivos, caro errar | o fluxo completo abaixo |

## 1. Instalar

```bash
git clone https://github.com/robertodiasduarte/sdd-open.git /tmp/sdd-open
cd meu-projeto            # precisa ser um repositório git
bash /tmp/sdd-open/bin/sdd-open.sh init --vendors codex --dry-run    # mostra o plano, não escreve
bash /tmp/sdd-open/bin/sdd-open.sh init --vendors codex              # pede confirmação, aplica
```

O `init` mostra um plano (`+` criar · `~` modificar bloco · `=` já correto) e só escreve depois
do seu `y`. Nada seu é sobrescrito: se você já tem um `AGENTS.md`, só o bloco entre
`<sdd-open-instructions>` e `</sdd-open-instructions>` é dele. Ao terminar, o `doctor` roda
sozinho e diz, por agente, o que foi gerado e o que é nativo.

Requisitos: `bash ≥ 3.2`, `git`. `python3` só para o adaptador Gemini e para os validadores.
No Windows, use Git Bash ou WSL.

## 2. Aponte o config para o seu projeto

Edite `sdd/config.yaml`:

```yaml
project:
  test_cmd: "npm test"
  typecheck_cmd: "tsc --noEmit"
layers:
  api: "src/api/**"
  ui: "src/ui/**"
deploy:
  cmd: "./deploy.sh production"
```

Slot vazio significa "pule este passo e diga que pulou" — nunca "adivinhe um comando".

## 3. Confira a instalação

```bash
sdd/bin/verify-gate.sh sdd/fixtures/DEFINE_FIXTURE_CONTROLE.md;             echo "exit=$?"  # 0
sdd/bin/verify-gate.sh sdd/fixtures/DEFINE_FIXTURE_NEEDS_CLARIFICATION.md;  echo "exit=$?"  # 5
```

`0` e `5` provam que o runner e o contrato de exit funcionam. Se o segundo devolver `0`, a
detecção de ambiguidade está quebrada — não siga, porque suposição silenciosa é exatamente o
que ela existe para pegar.

Cada saída termina em `RESULTADO: <PALAVRA>` e uma linha `→` dizendo o que fazer. Em CI e em
pipelines com `&&`, use `--strict`: inconclusivo, assinatura pendente e clarificação deixam de
valer como sucesso.

## 4. Sua primeira spec

> **A regra do método:** nunca siga para a próxima fase com um documento que você não leu.
> Corrigir uma frase agora custa minutos; corrigir depois que o código existe custa horas.

Cada fase lê o documento que a anterior gravou, então todas terminam do mesmo jeito: você lê o que
ela produziu antes de pedir a próxima.

**Brainstorm (opcional).** Quando a ideia ainda está vaga, `/sdd-brainstorm <sua ideia>` faz uma
pergunta por vez, compara 2–3 abordagens e grava `sdd/features/BRAINSTORM_<FEATURE>.md`.

**Valide antes de seguir:** a ideia está descrita como você pensou? Falta ou sobra alguma coisa?
Peça a correção agora.

**Define.** Peça ao agente a fase Define sobre o exemplo que veio na instalação:

```text
/sdd-define sdd/fixtures/BRAINSTORM_EXEMPLO.md
```

O agente vai empurrar de volta em três pontos, todos deliberados:

- **Testes de aceitação em EARS.** Não "o desconto deve funcionar", mas
  *"**When** o cliente aplica um código válido, the system **shall** recalcular o total em
  <500 ms"*. O padrão *unwanted* obriga a nomear o modo de falha antes de construir.
- **Ambiguidade vira marcador.** Onde a spec não sabe, o agente escreve
  `[NEEDS CLARIFICATION: …]` no lugar exato — e o gate devolve `5` até você responder.
- **O gate é um comando.** O DEFINE só sai com um bloco `## Verify Gate` que
  `sdd/bin/verify-gate.sh --print` lê sem erro.

**Valide antes de seguir:** leia os testes de aceitação e o que fica fora — é isso que vai ser
construído, nem mais nem menos.

**Design.** `/sdd-design sdd/features/DEFINE_<FEATURE>.md` escreve o plano técnico e a lista exata
de arquivos que o Build vai tocar. Diga onde a solução vai rodar: isso decide o Design, não o agente
com que você constrói.

| Você quer… | Escreva no Design | No Build |
|---|---|---|
| um site ou sistema web | aplicativo web (SaaS) | qualquer um dos 7 agentes, aberto na pasta do projeto |
| um programa de Windows | executável (.exe) para Windows | qualquer um dos 7 agentes, aberto na pasta do projeto |
| um programa de Mac | aplicativo para macOS | qualquer um dos 7 agentes, aberto na pasta do projeto |
| uma rotina sem tela | script de linha de comando que lê e gera arquivos | qualquer um dos 7 agentes, aberto na pasta do projeto |

O Build roda o Verify Gate num terminal, e os 7 têm um: Claude Code, Codex CLI, Gemini CLI,
Cursor, Kimi Code, Grok Build e GLM via Claude Code.

**Valide antes de seguir:** é a última parada barata. Depois daqui, mudança significa reescrever
código.

**Build.** `/sdd-build sdd/features/DESIGN_<FEATURE>.md` constrói só os arquivos do manifest e
termina quando o Verify Gate sai `0`.

**Valide antes de seguir:** use o que foi construído e compare com o Define; o que estiver diferente
volta ao agente antes da release.

**Release.** `/sdd-release <o que liberar>` roda as verificações de novo, mostra um bloco — o que
sobe e se o push publica sozinho — e faz uma pergunta só. Nada é publicado sem o seu sim.

## 5. Quando o pacote atualizar

```bash
cd /tmp/sdd-open && git pull
cd meu-projeto && bash /tmp/sdd-open/bin/sdd-open.sh doctor   # o que ficou para trás do pacote?
```

O `init` nunca sobrescreve uma skill nem um script de `sdd/bin/` que você já tem, e o `sync` só
regenera os adaptadores — então nenhum dos dois, sozinho, traz a versão nova de uma skill. O `doctor`
aponta cada skill com versão mais velha que a do pacote e cada arquivo de `sdd/bin/` diferente dele.
Para cada skill apontada:

```bash
rm -r .agents/skills/sdd-build                                 # a pasta que o doctor apontou; edições suas nela se perdem
bash /tmp/sdd-open/bin/sdd-open.sh init --vendors codex --yes  # copia de volta a versão do pacote
bash /tmp/sdd-open/bin/sdd-open.sh sync --yes                  # regenera os adaptadores a partir dela
```

Um arquivo de `sdd/bin/` segue o mesmo caminho: apague-o (se você não o editou) e rode o `init`.

`sync` **nunca** escreve em `sdd/` — suas specs, relatórios, fichas e playbook são seus.
Arquivos em `.claude/skills/`, `.cursor/skills/`, `CLAUDE.md` e `GEMINI.md` são gerados: edite
`.agents/skills/` e rode `sync`; edições neles são sobrescritas.

Cada cópia leva um cabeçalho `sdd-open:generated` de duas linhas, escrito na sintaxe de comentário
do próprio arquivo, para que os scripts continuem rodando: `#` em `.py`/`.rb`/`.sh`/`.bash`/`.ps1`/`.yaml`/`.yml`/`.toml`,
`//` em `.js`/`.mjs`/`.cjs`/`.ts`, `/* */` em `.css`, `--` em `.sql` e `<!-- -->` em Markdown e no resto.
Shebang (`#!`) e o `---` do frontmatter do Markdown ficam na linha 1, com o cabeçalho logo abaixo,
e o bit de execução é copiado. **`.json` e binários (imagem, fonte, PDF, zip, qualquer arquivo com byte NUL) não têm comentário:
a cópia sai sem cabeçalho, idêntica à fonte.** Em XML/SVG, a declaração `<?xml …?>` do início fica
na linha 1; em Python e Ruby, a declaração `# coding:` (PEP 263) também. O cabeçalho é ASCII puro:
no caminho do arquivo que ele cita, o que não for letra, dígito, `.`, `_`, `/` ou `-` aparece como `?`.

O `sync --check` só chama uma cópia de "em dia" quando ela é, byte a byte, o que o `sync` escreveria
agora. Com `python3`, `bash`, `node`, `ruby` ou `jq` disponíveis, ele também confere se a cópia compila. Cada
linha divergente diz o motivo: `desatualizado` (rode `sync`), `a fonte … não compila` (corrija a
fonte; o `sync` não resolve) ou `a cópia gerada não compila … bug do sdd-open` (abra uma issue).
Depois de uma atualização que muda o formato do cabeçalho, o primeiro `sync` reescreve todos os
adaptadores uma vez.

## Diagnóstico a qualquer hora

```bash
bash /tmp/sdd-open/bin/sdd-open.sh doctor
```

Mostra bash/git/python3, o que está instalado e, por agente, se o adaptador foi gerado, se o
agente lê `.agents/skills/` nativamente, e se o CLI dele está no PATH.

## Vem do sdd-starter?

O [sdd-starter](https://github.com/robertodiasduarte/sdd-starter) é a rampa (skills para
agentes sem sistema de arquivos, como claude.ai e ChatGPT); o SDD Open é a rodovia. Os nomes
das skills coincidem de propósito: use **um ou outro** por projeto. O `doctor` avisa
quando as skills do starter estão na pasta do projeto; a instalação global do starter (na pasta
pessoal do agente, como `~/.claude/skills/` ou `~/.agents/skills/`) ele não vê — remova as pastas
`sdd-*` de lá antes.
