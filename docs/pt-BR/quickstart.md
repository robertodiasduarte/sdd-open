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

Peça ao agente a fase Define sobre o exemplo que veio na instalação:

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

Depois: `/sdd-design`, `/sdd-build` (o gate é o critério de parada) e `/sdd-release` (uma
aprovação humana antes de publicar).

## 5. Quando o pacote atualizar

```bash
cd /tmp/sdd-open && git pull
cd meu-projeto && bash /tmp/sdd-open/bin/sdd-open.sh sync --check   # o que divergiu?
bash /tmp/sdd-open/bin/sdd-open.sh sync                             # regenera os adaptadores
```

`sync` **nunca** escreve em `sdd/` — suas specs, relatórios, fichas e playbook são seus.
Arquivos em `.claude/skills/`, `.cursor/skills/`, `CLAUDE.md` e `GEMINI.md` são gerados: edite
`.agents/skills/` e rode `sync`; edições neles são sobrescritas (o cabeçalho de cada um avisa).

## Diagnóstico a qualquer hora

```bash
bash /tmp/sdd-open/bin/sdd-open.sh doctor
```

Mostra bash/git/python3, o que está instalado e, por agente, se o adaptador foi gerado, se o
agente lê `.agents/skills/` nativamente, e se o CLI dele está no PATH.

## Vem do sdd-starter?

O [sdd-starter](https://github.com/robertodiasduarte/sdd-starter) é a rampa (skills para
agentes sem sistema de arquivos, como claude.ai e ChatGPT); o SDD Open é a rodovia. Os nomes
das skills coincidem de propósito: use **um ou outro** por projeto. O `doctor` avisa se
detectar os dois.
