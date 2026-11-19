# DESIGN: F28 — revisores pelo OpenRouter (`sdd-configurar-revisores`)

> Uma skill que mede o estado da revisão adversarial deste computador com um script, traduz cada estado numa frase e
> num passo, conduz o aluno até o OpenRouter (ou as CLIs que ele tem) e grava a escolha no `git config` local; o
> `adversarial-review.sh` passa a ler essa escolha e a mostrar o plano mesmo sem diff.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | F28_REVISORES_OPENROUTER |
| **Date** | 2026-11-18 |
| **Author** | design-agent |
| **DEFINE** | [DEFINE_F28_REVISORES_OPENROUTER.md](./DEFINE_F28_REVISORES_OPENROUTER.md) (1.1) |
| **UX Review** | `sdd/reviews/UX_REVIEW_F28_REVISORES_OPENROUTER.md` (U1–U16) |
| **Status** | Ready for Build |

---

## Architecture Overview

```text
 fase (design · build · release)        checar.sh (modo normal)
   │ slots vazios / revisão falhou         │ ⚠️ "revisores não configurados" / "chave fora do ambiente"
   └──────────────┬────────────────────────┘
                  ▼
   sdd-configurar-revisores (SKILL.md: conversa, tabela de estados R01–R26)
     │ 1 Conferir        2 Escolher       3 Chave              4 Gravar              5 Provar
     ▼                                    │ aluno, fora da      ▼                     ▼
   scripts/diagnosticar.sh ───────────────┤ conversa:         diagnosticar.sh       diagnosticar.sh --testar
     lê: sdd/config.yaml (review:)        │  site OpenRouter    --gravar R A          (GET /key, GET /models,
         git config sdd.revisor1/auditor  │  scripts/           → git config --local   só leitura, 10 s)
         registry.tsv · precos.tsv        │  guardar-chave.sh     sdd.revisor1/auditor adversarial-review.sh
         PATH (claude, codex, gemini)     │  (ou janela do      (nunca a chave)         --dry-run (sem diff ok)
         [ -n "$OPENROUTER_API_KEY" ]     │   Windows)
         perfil do terminal (grep -q)     │
     imprime: ESTADO, frase, passo, par sugerido, preço, estimativa; exit por classe
                  │
                  ▼
   sdd/bin/adversarial-review.sh   flag > slot do sdd/config.yaml > git config deste computador
                                   --dry-run: origem, disponibilidade, 2º revisor e desempate possíveis
```

## Components

| Componente | Papel |
|---|---|
| `scripts/diagnosticar.sh` | mede o estado (só lê); `--testar` faz 2 GET de leitura; `--gravar` e `--marcar-reabertura` gravam só no `git config --local` |
| `scripts/guardar-chave.sh` | o aluno roda num terminal dele: pede a chave sem mostrar e grava a linha `export` no perfil (macOS, Linux, WSL) |
| `SKILL.md` + `references/` | a conversa (Status, decisões, paradas), a tabela de estados, o passo a passo do site e do perfil por sistema |
| `adversarial-review.sh` | lê o `git config` quando o slot está vazio; `--dry-run` sem diff, com origem, disponibilidade e os papéis extras |
| `checar.sh` | 2 avisos ⚠️ novos, só em projeto com a revisão |
| ganchos e docs | `sdd-design`, `sdd-build`, `sdd-release`, guia do aluno, `adversarial-review.md` (2 línguas), README, `AGENTS.md.tmpl` |

---

## Key Decisions

### Decision 1: Skill nova com script na pasta dela, no molde da sdd-checar-ambiente

| **Status** | Accepted | · | **Date** | 2026-11-18 |
|---|---|---|---|---|

**Context:** P1 pede um script que decide e uma skill que traduz e conduz; o `checar.sh` é o molde (script na pasta da
skill, relatório já no formato do aluno, teste que compara as mensagens com a tabela).

**Choice:** `.agents/skills/sdd-configurar-revisores/scripts/diagnosticar.sh` (bash 3.2 com o núcleo em Python 3.9
stdlib, como o `adversarial-review.sh`) e `scripts/guardar-chave.sh` (bash puro). O Python vem de
`sdd/bin/lib/python.sh` do projeto quando existe (o estado R01 já exige `sdd/bin/adversarial-review.sh`, então a
biblioteca está lá); sem ela, a guarda antiga (`command -v python3`).

**Rationale:** a skill só serve a projeto com a revisão do Open; o script ao lado dela é achado pela mesma regra da
`sdd-checar-ambiente` ("a pasta desta skill é a que contém este `SKILL.md`").

**Alternatives Rejected:** 1. script em `sdd/bin/` — rejeitada: o diagnóstico é da conversa desta skill, não do
fluxo; `sdd/bin/` é o que as fases chamam · 2. só texto na skill, sem script — rejeitada: "estado sem linha é
defeito" só se prova com um emissor de estados testável.

**Consequences:** a skill depende da revisão do Open (não vai ao starter, Decision 10) · ganhamos o teste de paridade
estados × tabela.

### Decision 2: A escolha mora no git config local; flag > slot > git config

| **Status** | Accepted | · | **Date** | 2026-11-18 |
|---|---|---|---|---|

**Context:** A2. O slot do `sdd/config.yaml` da frente só chega à branch padrão na integração; a pergunta voltaria
em cada frente aberta até lá, e a escolha depende do que este computador tem.

**Choice:** `git config --local sdd.revisor1 '<id>'` e `git config --local sdd.auditor '<id>'`. No
`adversarial-review.sh`, `lista()` passa a devolver a origem: a flag, senão o slot do `sdd/config.yaml`, senão
`git -C <raiz> config --get sdd.<chave>`. Numa worktree ligada, `--local` grava no config comum (vale para todas as
frentes). O `--dry-run` e a mensagem de slot vazio dizem a origem e citam a skill.

**Rationale:** é o mesmo caminho do `sdd.editor` da `sdd-new-session`, que os alunos já viram; o slot continua sendo a
escolha do time e vence.

**Alternatives Rejected:** 1. gravar o slot na frente — rejeitada (A2) · 2. git config vencendo o slot — rejeitada:
o time perderia o poder de fixar as engines · 3. arquivo próprio em `.git/` — rejeitada: o `git config` já é lido
por `git config --get`, sem parser novo.

**Consequences:** uma fonte a mais para as engines (dita no plano) · nenhuma mudança na cadeia nem na identidade.

### Decision 3: --dry-run mostra o plano sem diff e diz quem faria os papéis extras

| **Status** | Accepted | · | **Date** | 2026-11-18 |
|---|---|---|---|---|

**Context:** a prova da skill roda numa frente recém-aberta, sem diff; hoje o `--dry-run` sai 64 ("está vazio")
antes de mostrar as engines. A3: com revisor e auditor no OpenRouter, o 2º revisor e o desempate saem das outras
engines do registry, se houver.

**Choice:** no `--dry-run`, as linhas das engines vêm antes do diff: `revisor :` e `auditor :` com modelo, origem e
`disponível` / `indisponível — <a credencial que falta>` (pela `adapter_disponivel` de cada adapter, sem rede),
`diversidade:`, `2º revisor (se acionado):` e `desempate (se acionado):` com a engine ou `nenhuma engine disponível —
<consequência>`. Depois, o diff: vazio ⇒ `diff: vazio, nada a revisar ainda — o plano das engines vale`, exit 0, `RESULTADO: PLANO`; sem
base ⇒ `⚠️ diff: sem base para comparar (…) — a revisão real vai parar até a branch padrão existir no remoto`, exit 0
(a configuração das engines está certa; a base é outro conserto, dito com a consequência). Com diff, o resto como hoje. A escolha do 2º revisor e do desempate passa para uma função
única (`extra_disponivel`) que a revisão real e o `--dry-run` chamam: a regra de hoje, sem mudança.

**Rationale:** a prova precisa de exit 0 no caso do aluno; a função única impede o plano de dizer uma coisa e a
revisão fazer outra.

**Alternatives Rejected:** 1. o diagnóstico calcular os papéis extras sozinho — rejeitada: duas cópias da regra ·
2. aceitar o 64 "está vazio" como prova — rejeitada: o aluno veria um erro no fim da configuração.

**Consequences:** a revisão real sem diff continua 64 (AT-006, AT-010) · a ordem das linhas do `--dry-run` muda (os
testes leem trechos, não a ordem).

### Decision 4: Prova sem gastar — 2 GET de leitura, números como decimal

| **Status** | Accepted | · | **Date** | 2026-11-18 |
|---|---|---|---|---|

**Context:** P6 e G09. Conferido em 2026-11-18: `GET /api/v1/key` devolve `data.limit`, `data.limit_remaining`,
`data.usage`, `data.is_free_tier` (https://openrouter.ai/docs/api-reference/limits); `GET /api/v1/credits` exige
chave de gestão (https://openrouter.ai/docs/api-reference/get-credits); `GET /api/v1/models` é pública (480 modelos
na consulta de 2026-11-18). Ler a chave não gera texto de modelo; a cobrança do OpenRouter é por geração.

**Choice:** `diagnosticar.sh --testar` faz, com teto de 10 s cada: `GET <base>/key` com `Authorization: Bearer`
(a chave lida de `os.environ` dentro do Python) e, se a chave foi aceita, `GET <base>/models` sem chave. `<base>` =
`SDD_REVISORES_OPENROUTER_URL` (só nos testes) ou `https://openrouter.ai/api/v1`. Classes, nesta ordem: erro de rede
ou teto ⇒ R19; 401/403 ⇒ R15; 402 ⇒ R16; 429 ⇒ R18; qualquer outro status, JSON ilegível ou de forma
inesperada (sem `data` objeto) ⇒ R20 (nunca "aceita" sem a resposta reconhecida); `is_free_tier: true` ⇒ R16; `limit_remaining`
não nulo e, truncado em centavos, ≤ 0 ⇒ R17; um modelo do par (ou dos slots) fora da lista ⇒ R21; `limit` nulo ⇒ R14
(aceita, com aviso); senão R13. JSON lido com `parse_float=Decimal` e `parse_int=Decimal`; mostrado truncado em
centavos (`quantize(Decimal("0.01"), ROUND_DOWN)`), com vírgula. Da resposta só se leem esses 4 campos e a lista de
`id` dos modelos; nenhum texto da resposta é impresso.

**Rationale:** ver se a chave vale, se tem crédito e limite, e se os modelos existem, sem uma chamada paga.

**Alternatives Rejected:** 1. `/credits` — rejeitada: exige chave de gestão · 2. uma chamada barata a
`chat/completions` — rejeitada: gasta, e a regra da frente proíbe gasto na prova · 3. `float` — rejeitada (G09).

O teto de 10 s vale para a chamada inteira (a consulta roda numa thread com prazo pelo relógio), não só por
operação do socket. Com os dois revisores em CLIs, o `--testar` não consulta o OpenRouter (uma chave antiga no
ambiente não derruba a prova do caminho sem custo).

**Consequences:** "sem crédito" só por `is_free_tier` e 402 (quem já pôs e gastou tudo aparece como 402 na revisão real,
traduzido pela tabela, R16) · teste sem rede, com servidor local.

### Decision 5: A chave é gravada pelo aluno, sem aparecer — script no terminal dele ou a janela do Windows

| **Status** | Accepted | · | **Date** | 2026-11-18 |
|---|---|---|---|---|

**Context:** P2 e A1. Quem lê nunca editou um perfil; um `export` digitado fica no histórico.

**Choice:** macOS, Linux e WSL: `bash <pasta da skill>/scripts/guardar-chave.sh`, rodado pelo aluno numa janela de
terminal dele. O script exige terminal (`[ -t 0 ]`, senão sai 64 sem ler nada), escolhe o perfil (`$SHELL` termina
em `zsh` ⇒ `~/.zshrc`; bash no macOS ⇒ o 1º que existir de `~/.bash_profile`, `~/.bash_login`, `~/.profile` (o shell de login lê só esse;
criar um `.bash_profile` novo esconderia o `.profile`), ou `~/.bash_profile` sem nenhum; bash no Linux e no WSL ⇒
`~/.bashrc`), recusa perfil que é atalho (repositório de configurações, G16), avisa sem mostrar quando outro perfil
também tem uma linha da chave (uma chave antiga pode vencer a nova), lê a chave com `read -rs` (não aparece), recusa vazio (exit 1, nada
gravado), avisa sem mostrar se não começa por `sk-or-`, guarda uma cópia do perfil em `<perfil>.sdd-antes` na 1ª vez,
tira as linhas `OPENROUTER_API_KEY=` antigas e acrescenta `# OpenRouter — sdd-configurar-revisores` e
`export OPENROUTER_API_KEY='<chave>'` com o `printf` embutido do bash (sem processo novo). Imprime só o perfil usado e
o próximo passo. Git Bash no Windows: o script sai 64 apontando a janela "Variáveis de ambiente" (o editor no Windows
não lê o `~/.bashrc`; as variáveis do usuário valem para o Git Bash e para o editor).

**Rationale:** um comando por passo, a chave nunca na tela, no histórico ou na conversa.

**Alternatives Rejected:** 1. `export` digitado — rejeitada: histórico · 2. `setx` no Windows — rejeitada: a chave
vira argumento de processo · 3. o agente gravar — rejeitada: a chave passaria pela conversa.

**Consequences:** a chave fica em claro no perfil (G16, risco aceito; o passo a passo avisa sobre pasta sincronizada
e dotfiles publicados) · testado com pty no macOS e no Linux; o caminho do Windows é texto conferido (não testado:
sem Windows nesta sessão).

### Decision 6: Reconhecer a volta — perfil sem ler o valor e a marca de reabertura

| **Status** | Accepted | · | **Date** | 2026-11-18 |
|---|---|---|---|---|

**Context:** AT-004 e U6/U7: o agente herda o ambiente de quando foi aberto; a skill precisa saber se a chave está
gravada e se o aluno já tentou reabrir.

**Choice:** chave no perfil = `grep -qE '^[[:space:]]*(export[[:space:]]+)?OPENROUTER_API_KEY=' <arquivo>` sobre
`~/.zshrc`, `~/.zprofile`, `~/.zshenv`, `~/.zshrc.local`, `~/.bashrc`, `~/.bash_profile`, `~/.bash_login`, `~/.profile`,
`~/.bashrc.local` (só o código de saída); no Git
Bash, `MSYS2_ARG_CONV_EXCL='*' reg query 'HKCU\Environment' /v OPENROUTER_API_KEY` com a saída descartada (o `reg`
trocável por `SDD_REVISORES_REG` e o sistema por `SDD_REVISORES_SISTEMA`, só nos testes). **Herança do ambiente:** o agente aberto no terminal
herda o ambiente daquele terminal; o VS Code, ao iniciar, abre um shell de login interativo para ler o ambiente
(https://code.visualstudio.com/docs/configure/command-line, conferido em 2026-11-18), então a extensão enxerga o
`~/.zshrc` depois de o editor ser fechado por completo e aberto. **Não testado nesta versão:** Cursor e outros
editores da mesma família (presumido igual, por serem derivados do VS Code), a herança das variáveis do usuário
pelo Git Bash e pelo editor no Windows (fonte não oficial, tutorial da Alura; sem Windows na conferência), WSL. O
estado R06 cobre o caso em que reabrir não basta (abrir pelo terminal; no Windows, sair e entrar na conta). Na parada, a skill roda
`diagnosticar.sh --marcar-reabertura` (grava `git config --local sdd.revisores.reabrir <AAAA-MM-DD>`); na volta, chave
ainda ausente com a marca ⇒ R06 (reabriu e a chave não chegou: abrir o agente por um terminal novo; no Windows, sair e
entrar na conta); sem a marca ⇒ R05. `--gravar` apaga a marca.

**Rationale:** a skill diz "o que já foi feito" pelo que mede, não pela memória da conversa.

**Alternatives Rejected:** 1. ler o perfil inteiro — rejeitada: imprimiria a chave · 2. só a memória da conversa —
rejeitada: a volta é numa sessão nova.

**Consequences:** um 3º valor no `git config` (`sdd.revisores.reabrir`), dito na skill.

### Decision 7: O par sugerido e a estimativa saem das tabelas

| **Status** | Accepted | · | **Date** | 2026-11-18 |
|---|---|---|---|---|

**Context:** P4. Nada de nome de modelo nem preço no `SKILL.md`.

**Choice:** revisor = `openrouter:<modelo da linha openrouter do registry>`; auditor = `openrouter:<1º outro modelo
openrouter do precos.tsv>`. Sem dois modelos diferentes ⇒ o diagnóstico diz que o pacote não tem par e oferece
"dizer o meu modelo". Estimativa por revisão: entrada do revisor = (`review.context_max_kb` + 60) × 1024 ÷ 4 tokens,
saída 8.000; auditor = entrada do revisor + 8.000, saída 4.000; preço do `precos.tsv` em decimal; mostrada como "até
≈ US$ x" arredondada **para cima** em centavos (é um teto) e "menos de US$ 0,01" abaixo disso. O Build confere a lista
pública e grava o preço e a data no `precos.tsv` (2026-11-18: `deepseek/deepseek-v4-flash` passou a 0,09 / 0,18).

**Rationale:** o aluno vê preço com fonte e data; o mantenedor troca o par numa linha.

**Alternatives Rejected:** 1. o par escrito no `SKILL.md` — rejeitada (P4) · 2. escolher pelo menor preço da lista
pública inteira — rejeitada: modelo sem medida de qualidade no pacote.

**Consequences:** a estimativa é uma conta, dita como teto · a skill nunca escreve nome de modelo de memória.

### Decision 8: Estados com id, classe por exit e paridade com a tabela

| **Status** | Accepted | · | **Date** | 2026-11-18 |
|---|---|---|---|---|

**Context:** "estado sem linha é defeito".

**Choice:** saída do diagnóstico: `ESTADO: Rnn NOME`, `aluno: <frase>`, `passo: <próximo passo>`, as linhas de
medida (revisor, auditor e origem; chave no agente e no perfil; CLIs; par, preço e estimativa quando o caminho é o
OpenRouter), `RESULTADO: <PALAVRA>` e `→ <seta>`. Exits: 0 PRONTO (R02, R13, R14) · 10 ESCOLHA (R03, R04, R07, R10) ·
20 PARADA (R05, R06, R08, R09) · 30 CONSERTO (R11, R12) · 40 TESTE (R15–R21) · 64 USO (R01, opção errada). Precedência
sem `--testar`: R01 → R12 → R11 → R05/R06 (só com slots vazios, um slot só, ou algum slot no OpenRouter) → R08 →
R10 → R09 → R02; com os dois slots vazios: R03 (2+ CLIs, mesmo com a chave presente) → R07 (chave) → R04. A
tabela do `SKILL.md` tem uma linha por estado, com a coluna "quem reconhece" (`script` ou `conversa`); R22–R26 são
de conversa (sem bash, "No endpoints found", chave no chat, uma engine só, agora não). O teste compara os ids `script`
da tabela com os que o script emite nos casos e com a lista do próprio script.

**Rationale:** a skill repassa a frase, nunca o id (U12); o id é o contrato entre o script e a tabela.

**Alternatives Rejected:** 1. exit por estado (26 códigos) — rejeitada: a skill decide pela classe, a frase vem
pronta · 2. só texto livre — rejeitada: sem paridade testável.

**Consequences:** estado novo = 1 linha no script + 1 na tabela, ou o teste fica vermelho.

### Decision 9: Aviso no checar.sh, nunca impedimento

| **Status** | Accepted | · | **Date** | 2026-11-18 |
|---|---|---|---|---|

**Context:** A5 e U15.

**Choice:** no modo normal, depois das skills duplicadas, só com `${RAIZ}/sdd/bin/adversarial-review.sh`: revisor ou
auditor vazios (slot lido por `awk` no bloco `review:` do `sdd/config.yaml`, depois `git config --get`) ⇒ `add_arrumar`
"Os revisores da revisão adversarial não estão configurados — sem eles, a publicação pede para seguir sem revisão." /
"peça ao agente: use a skill sdd-configurar-revisores"; algum dos dois começa por `openrouter` e
`[ -z "${OPENROUTER_API_KEY:-}" ]` ⇒ "A revisão adversarial usa o OpenRouter e a chave dele (OPENROUTER_API_KEY) não
está no ambiente deste agente — a revisão vai parar por credencial." / a mesma linha da skill. Nada no `--frente`,
`--segredo`, `--editor`, `--editores`, `--duplicadas`.

**Rationale:** quem roda o `checar` descobre a skill; não impede o trabalho.

**Alternatives Rejected:** 1. chamar o `diagnosticar.sh` — rejeitada: dependência entre skills, e o starter gera o
`checar.sh` sem a skill nova · 2. 🔴 — rejeitada: a revisão é dispensável com motivo.

**Consequences:** o leitor do slot no `checar.sh` é o mínimo (`revisor1:`/`auditor:` dentro de `review:`), coberto
por teste com aspas, comentário e valor vazio.

### Decision 10: Ganchos nas fases, docs e fora do starter

| **Status** | Accepted | · | **Date** | 2026-11-18 |
|---|---|---|---|---|

**Context:** P7, P8, A-004 (conferido: `grep adversarial-review scripts/starter scripts/gerar-starter.py` acha só um
molde de resumo; o starter não traz a revisão).

**Choice:** `sdd-design` (linha das engines vazias) e `sdd-build` (passos 0 e 5c) oferecem a skill como pergunta
(U14) em vez de "pergunte quais usar"; `sdd-release`, FASE 0 item 8, com `--conferir` exit 2 e revisores não
configurados, oferece a skill **antes** da pergunta D3 de dispensa (a D3 fica igual). Docs: guia do aluno (catálogo,
Dia 1, "Quando algo dá errado"), `docs/adversarial-review.md` e `docs/pt-BR/adversarial-review.md` (seção do git
config e do `--dry-run`), README e README.pt-BR (24 skills, bloco Preparar), `AGENTS.md.tmpl` (linha Antes),
`sdd/config.example.yaml` (comentário). A skill não entra em `scripts/starter/lista.txt`.

**Rationale:** o aluno encontra a skill onde hoje encontra a pergunta sem resposta.

**Alternatives Rejected:** 1. o `init` perguntar os revisores — rejeitada: o `init` roda antes de o aluno saber o que
é revisão, e sem a chave · 2. levar ao starter — rejeitada: lá não há revisão.

**Consequences:** contagens fixadas mudam: 23 → 24 skills (`test_skill_lint`, `test_conversa`, `test_docs`,
`test_f21_textos`, `test_f27_textos`), perguntas do `sdd-decisoes-lint` (`test_decisoes_lint`); skills tocadas sobem
versão (`sdd-checar-ambiente` 1.7.0, `sdd-design`, `sdd-build`, `sdd-release` +minor).

---

## File Manifest

| # | File | Action | Purpose | Agent | Dependencies |
|---|------|--------|---------|-------|--------------|
| 1 | `sdd/bin/adversarial-review.sh` | Modify | git config como 3ª fonte, origem, `extra_disponivel`, `--dry-run` sem diff (Decisions 2, 3) | (general) | None |
| 2 | `sdd/review/precos.tsv` | Modify | preço e data conferidos em 2026-11-18 (Decision 7) | (general) | None |
| 3 | `sdd/config.example.yaml` | Modify | comentário do bloco `review:` (git config, a skill) | (general) | 1 |
| 4 | `.agents/skills/sdd-configurar-revisores/scripts/diagnosticar.sh` | Create | estados, `--testar`, `--gravar`, `--marcar-reabertura` (Decisions 4, 6, 7, 8) | (general) | 1, 2 |
| 5 | `.agents/skills/sdd-configurar-revisores/scripts/guardar-chave.sh` | Create | gravar a chave no perfil sem mostrá-la (Decision 5) | (general) | None |
| 6 | `.agents/skills/sdd-configurar-revisores/references/PASSO_A_PASSO.md` | Create | site do OpenRouter (conta, crédito, chave com limite), perfil por sistema, reabrir, revogar; nomes de tela com a fonte e a data | (general) | 5 |
| 7 | `.agents/skills/sdd-configurar-revisores/references/como-falar.md` | Create | glossário, Status preenchido, exemplos de decisão e de parada | (general) | None |
| 8 | `.agents/skills/sdd-configurar-revisores/SKILL.md` | Create | conversa em 5 etapas, tabela R01–R26, regras de segredo | (general) | 4, 5, 6, 7 |
| 9 | `.agents/skills/sdd-configurar-revisores/manifest.json` | Create | núcleo, caminhos, executados, pendentes | (general) | 8 |
| 10 | `.agents/skills/sdd-configurar-revisores/evals/cases.json` | Create | os 3 cenários do DEFINE com o critério de aprovado | (general) | 8 |
| 11 | `.agents/skills/sdd-checar-ambiente/scripts/checar.sh` | Modify | 2 avisos ⚠️ (Decision 9) | (general) | None |
| 12 | `.agents/skills/sdd-checar-ambiente/SKILL.md` | Modify | item no "O que verificar", versão 1.7.0 | (general) | 11 |
| 13 | `.agents/skills/sdd-design/SKILL.md` | Modify | oferta da skill com as engines vazias | (general) | 8 |
| 14 | `.agents/skills/sdd-build/SKILL.md` | Modify | oferta nos passos 0 e 5c | (general) | 8 |
| 15 | `.agents/skills/sdd-release/SKILL.md` | Modify | oferta no item 8 da FASE 0, antes da D3 | (general) | 8 |
| 16 | `.agents/skills/sdd-release/references/como-falar.md` | Modify | a pergunta da oferta, antes do exemplo D3 | (general) | 15 |
| 17 | `docs/adversarial-review.md` | Modify | git config, `--dry-run` sem diff, a skill | (general) | 1, 8 |
| 18 | `docs/pt-BR/adversarial-review.md` | Modify | o mesmo em português | (general) | 1, 8 |
| 19 | `docs/pt-BR/guia-do-aluno.md` | Modify | catálogo, Dia 1, "Quando algo dá errado" | (general) | 8 |
| 20 | `README.md` | Modify | 24 skills, bloco Preparar | (general) | 8 |
| 21 | `README.pt-BR.md` | Modify | o mesmo em português | (general) | 8 |
| 22 | `AGENTS.md.tmpl` | Modify | a skill na linha Antes | (general) | 8 |
| 23 | `MANIFEST.txt` | Modify | os 7 arquivos novos da skill e os 2 módulos de teste | (general) | 4–10, 24, 25 |
| 24 | `tests/test_f28_revisores.py` | Create | AT-001–AT-004, AT-007, AT-008: diagnóstico, servidor local, pty, paridade, textos | (general) | 4–10, 13–22 |
| 25 | `tests/test_f28_revisao_slots.py` | Create | AT-005, AT-006, AT-010: git config, origem, `--dry-run` sem diff, coerência com o diagnóstico | (general) | 1, 4 |
| 26 | `tests/test_checar.py` | Modify | AT-009: avisos, modos sem aviso, sem a revisão, chave nunca impressa | (general) | 11 |
| 27 | `tests/test_skill_lint.py` | Modify | 23 → 24 skills | (general) | 8 |
| 28 | `tests/test_conversa.py` | Modify | 24 skills e a nova na lista | (general) | 8 |
| 29 | `tests/test_docs.py` | Modify | 24 skills | (general) | 8 |
| 30 | `tests/test_decisoes_lint.py` | Modify | a contagem de perguntas com a skill nova | (general) | 7, 8, 16 |
| 31 | `tests/test_f21_textos.py` | Modify | "## The 24 skills" | (general) | 20, 21 |
| 32 | `tests/test_f27_textos.py` | Modify | "## The 24 skills" | (general) | 20, 21 |

**Total Files:** 32

---

## Landmines aplicáveis

| Landmine (⛔) | Fonte | Veredito | Como / Por quê |
|---------------|-------|----------|----------------|
| Asserção que não avalia nada | LM-001, LM-002 | ✔ tratado | linha de base vermelha em `eaeb874` e 6 sabotagens numa cópia de `git archive` (Testing Strategy) |
| Revisão sobre diff vazio | LM-003 | ✔ tratado | commitar antes de cada `adversarial-review.sh`; conferir o `--stat` |
| Sabotagem com `git checkout` apaga conserto | LM-009 | ✔ tratado | mutantes só numa cópia de `git archive` |
| OpenRouter estourando o teto cobra sem resposta | LM-010 | ✔ tratado | a revisão desta frente usa claude e codex (assinatura); a skill põe limite de gasto na chave (S20) |
| Cenário escrito e nunca executado | LM-011 | ✔ tratado | 3 cenários × 2 execuções com o critério escrito antes (#10) |
| Número com 11+ dígitos no pacote | LM-012 | ✔ tratado | fixtures curtas; nenhum id de run; o publish-gate roda no gate |
| `subprocess` de teste sem `encoding` | LM-014 | ✔ tratado | `encoding="utf-8", errors="replace"` em todo `subprocess` dos testes novos |
| `bash` sem caminho no Windows | LM-029 | ✔ tratado | testes pela constante `BASH` de `tests/apoio.py`; o Python do diagnóstico chama o bash por `SDD_REVISORES_BASH="${BASH:-bash}"` |
| Calço no PATH muda como o Python roda | LM-032 | N.A. | nenhum calço novo; o diagnóstico usa a `sdd/bin/lib/python.sh` |
| PATH de links no Windows | LM-034 | ✔ tratado | CLIs falsas por `path_restrito` de `tests/apoio.py`, nunca links |
| Skill do starter cita `sdd/bin/…` | LM-035 | ✔ tratado | `checar.sh` está na lista do starter: rodar `test_gerar_starter.py` antes do gate; o texto novo do `checar.sh` não cita arquivo que só o `init` cria (a condição usa `${RAIZ}/sdd/bin/…` como teste de existência; se o lint reclamar, troca em `scripts/starter/trocas/`) |
| Arquivo novo fora do `MANIFEST.txt` | LM-037 | ✔ tratado | #23 no mesmo commit de cada arquivo novo; `publish-gate` sobre `git archive` antes do gate |
| `os.name` em teste | LM-042 | ✔ tratado | `WINDOWS`, `SEM_PTY`, `SEM_PATH_SEM_FERRAMENTA` de `tests/apoio.py` |
| `HOME` atribuído dentro do script não chega ao filho | LM-043 | ✔ tratado | `HOME=<pasta de teste>` passado no `env` de cada chamada; o diagnóstico lê `$HOME` do próprio ambiente |

---

## Contrato de aceite

N.A. (1 camada): o Open não declara `layers:`; o manifest é texto de skill, scripts de terminal e testes. O avaliador
fresco roda assim mesmo no Build, como nas frentes anteriores, por decisão de rotina (o custo é baixo e a frente mexe
no `adversarial-review.sh`).

---

## Agent Assignment Rationale

| Agent | Files Assigned | Why This Agent |
|-------|----------------|----------------|
| (general) | 1–32 | o repositório não tem agentes especialistas; o Build faz direto |

---

## Code Patterns

candidato a pattern: nenhum (o Open não tem `sdd/patterns/`).

### Pattern 1: Origem do slot (adversarial-review.sh)

```python
ORIGEM = {"flag": "flag", "slot": "sdd/config.yaml", "git": "este computador (git config sdd.%s)"}

def lista(flag, chave, papel):
    """(engines, origem): a flag, senão o slot do sdd/config.yaml, senão o git config deste computador (F28)."""
    if op[flag] is not None:
        v, origem = op[flag], "flag"
    else:
        v, origem = slot(cfg, "review", chave) or "", "sdd/config.yaml"
        if not v.strip():
            v = git(raiz, "config", "--get", "sdd." + chave)[1].strip()
            origem = ORIGEM["git"] % chave if v else "—"
    ids = [x.strip() for x in v.split(",") if x.strip()]
    return [resolve(x, papel) for x in ids], origem
```

### Pattern 2: Papel extra numa função só

```python
def extra_disponivel(papel_extra, excl_bases, chaves):
    """A 1ª engine disponível do registry fora das bases excluídas e das identidades já usadas; None sem nenhuma.
    A revisão real (2º revisor, desempate) e o --dry-run chamam esta função: o plano não diverge da revisão."""
    for e in ORDEM:
        if e in excl_bases:
            continue
        d = candidato(e, papel_extra)
        if d and chave(d) not in chaves and disponivel(d):
            return d
    return None
```

### Pattern 3: Teste da chave sem imprimir a resposta (diagnosticar.sh, núcleo Python)

```python
from decimal import Decimal, ROUND_DOWN
def get(url, chave=None):
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + chave} if chave else {})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, json.loads(r.read().decode("utf-8", "replace"),
                                        parse_float=Decimal, parse_int=Decimal)
    except urllib.error.HTTPError as e:
        return e.code, None          # o corpo do erro nunca é lido nem impresso
    except (OSError, ValueError):
        return None, None            # rede, teto de 10 s, JSON ilegível

centavos = lambda v: v.quantize(Decimal("0.01"), rounding=ROUND_DOWN)
st, j = get(BASE + "/key", os.environ["OPENROUTER_API_KEY"])
d = (j or {}).get("data") or {}
resta = d.get("limit_remaining")
if isinstance(resta, Decimal) and centavos(resta) <= 0:
    estado("R17")
```

### Pattern 4: Gravar a chave sem mostrá-la (guardar-chave.sh)

```bash
[ -t 0 ] || { echo "🛑 rode este comando numa janela de terminal sua, não pelo agente."; exit 64; }
printf 'Cole a chave do OpenRouter e tecle Enter (ela não aparece): '
IFS= read -rs K; printf '\n'
[ -n "${K}" ] || { echo "Nada foi gravado: a chave veio vazia."; exit 1; }
# … cópia do perfil na 1ª vez; linhas antigas fora (laço de leitura, sem sed -i); depois:
printf '# OpenRouter — sdd-configurar-revisores\nexport OPENROUTER_API_KEY='"'"'%s'"'"'\n' "${K}" >> "${PERFIL}"
unset K
```

---

## Data Flow

1. A fase (ou o `checar`, ou o aluno) chama a skill → `diagnosticar.sh` → estado e classe.
2. ESCOLHA ⇒ pergunta do caminho (U3). OpenRouter ⇒ blocos do `PASSO_A_PASSO.md` (U4) → `guardar-chave.sh` no
   terminal do aluno → `--marcar-reabertura` → parada (U6).
3. Volta ⇒ `diagnosticar.sh` (R07) → `--testar` (R13/R14) → aviso de custo e privacidade (U8) → OK → `--gravar R A`.
4. Prova ⇒ `--testar`, leitura de volta do `git config`, `adversarial-review.sh --dry-run` → 3 linhas ✅ (U10).

## Integration Points

| Ponto | Contrato |
|---|---|
| OpenRouter `GET /api/v1/key` | Bearer; `data.{limit, limit_remaining, usage, is_free_tier}`; conferido 2026-11-18 |
| OpenRouter `GET /api/v1/models` | público; `data[].id` |
| `git config --local` | `sdd.revisor1`, `sdd.auditor`, `sdd.revisores.reabrir` |
| `adversarial-review.sh` | lê as 2 primeiras chaves; `--dry-run` mostra a origem |

---

## Testing Strategy

| Tipo | Escopo | Ferramenta | Meta |
|---|---|---|---|
| unidade/integração | `diagnosticar.sh`: cada estado R01–R21 num projeto git temporário (registry e precos de fixture, `PATH` restrito com CLIs falsas, `HOME` temporário com perfis sintéticos, `SDD_REVISORES_SISTEMA=windows` + `reg` falso) | `unittest` + `subprocess` | AT-001, AT-004 |
| servidor local | `--testar` contra `http.server` em thread que registra método e caminho de cada chamada: 200 (com e sem limite, `is_free_tier`, `limit_remaining` 0, -0,01, 0,0004, 1,00), 401, 403, 429, 500, JSON quebrado, sem servidor (porta fechada), modelo fora da lista; corpo de erro com texto-sonda | `unittest` | AT-003, G09; 0 chamadas a `chat/completions`; texto-sonda nunca na saída |
| segredo | fixture `fixture-nao-e-chave-<hex curto>` em `OPENROUTER_API_KEY`; procurada na saída do diagnóstico, do `--dry-run`, do `checar.sh` e no `.git/config` | `unittest` | AT-002: 0 ocorrências |
| pty | `guardar-chave.sh` com `pty.fork`: chave gravada, eco desligado (a chave não volta pelo terminal), linha antiga trocada, cópia do perfil, vazio ⇒ exit 1, sem terminal ⇒ 64, Git Bash ⇒ 64 | `unittest` + `pty` (`SEM_PTY`) | AT-002 |
| revisão | `adversarial-review.sh` com stubs: git config × slot × flag (3 casos), origem no `--dry-run`, `--dry-run` sem diff (exit 0) e a revisão real sem diff (64), papéis extras com e sem engine; coerência: o diagnóstico e o `--dry-run` resolvem os mesmos ids em 4 configurações | `unittest` | AT-005, AT-006 |
| textos | tabela R01–R26 × estados do script; etapas, glossário, parada, "não sei", recomendada primeiro, nenhum nome de modelo nem preço no `SKILL.md`/`references/`, ganchos, docs, README, `MANIFEST.txt` | `unittest`, `skill-lint.py --conversa`, `test_agnostico.py`, `test_gerar_starter.py` | AT-007, AT-008 |
| checar | avisos no modo normal; nenhum nos outros modos e sem a revisão | `tests/test_checar.py` | AT-009 |
| regressão | suíte inteira, bash 3.2, gate offline da revisão | Verify Gate, CI do PR (3 sistemas) | AT-010 |
| sabotagem | numa cópia de `git archive`: diagnóstico imprime a chave; `--testar` chama `chat/completions`; `--gravar` escreve no `sdd/config.yaml`; `--dry-run` sem diff volta a 64; `checar.sh` usa `add_impede`; `≤ 0` vira `== 0` | script temporário | cada mutante derruba um teste nomeado |
| comportamento | 3 cenários × 2 execuções em contexto novo, critério escrito antes | subagente fresco | SHOULD do DEFINE |

---

## Error Handling

| Erro | Tratamento |
|---|---|
| rede, teto de 10 s | R19, "nada foi gravado" |
| 401/403 · 429 · 5xx | R15 · R18 · R20; o corpo nunca é lido |
| JSON ilegível | R20 |
| `git config` falha ao gravar | `--gravar` sai 30 com a frase "não consegui gravar neste computador" e o comando à mão |
| registry ou precos ilegíveis | exit 64 com o arquivo e o conserto (`init` completa) |
| sem Python | a guarda da `python.sh`, exit 64 |

## Configuration

| Chave | Onde | Efeito |
|---|---|---|
| `sdd.revisor1`, `sdd.auditor` | `git config --local` | engines deste computador, depois da flag e do slot |
| `sdd.revisores.reabrir` | `git config --local` | marca da parada da reabertura |
| `SDD_REVISORES_OPENROUTER_URL`, `SDD_REVISORES_SISTEMA`, `SDD_REVISORES_REG` | ambiente | só nos testes |

---

## Segurança

1. **Onde mora cada segredo:** `OPENROUTER_API_KEY` só no ambiente do agente e no perfil do terminal do aluno (macOS,
   Linux, WSL) ou nas variáveis do usuário do Windows; nunca no projeto, no `git config`, em argumento, na conversa ou
   num log. Quem lê: o Python do adapter e do `--testar`, por `os.environ`.
2. **Quem vê e quem muda cada tabela (RLS):** N.A. — sem banco.
3. **Credencial de cada agente ou integração:** a chave do aluno, com limite de gasto pedido no passo a passo e
   avisado quando falta (R14); o interruptor é apagar a chave na página de chaves (dito em `PASSO_A_PASSO.md`).
4. **Cabeçalhos e CORS do host:** N.A. — sem servidor.
5. **Itens aplicados no Define:**
   - S10 Senha ou segredo guardado errado → a chave mora só no perfil ou nas variáveis do Windows, gravada por
     `guardar-chave.sh` sem passar pela tela; o diagnóstico só testa existência (`[ -n … ]`, `grep -q`, `reg query`
     sem saída).
   - S17 Log que aceita linha forjada e S18 Instrução escondida → o diagnóstico nunca imprime texto da resposta do
     OpenRouter (o corpo de erro nem é lido; do JSON só 4 campos numéricos ou booleanos e a lista de `id`).
   - S20 Agente com poder demais e sem teto → limite de gasto na chave (passo a passo) e o aviso R14; a prova não
     chama `chat/completions`.

## Desempenho

N.A. — a frente não tem banco.

## Observability

| Aspect | Implementation |
|--------|----------------|
| Logging | nenhum log novo; a saída do diagnóstico é a mensagem ao aluno |
| Metrics | o sinal S da UX review: `review_externo: dispensado` nas releases |
| Tracing | N.A. |

---

## Advisor Ledger

Revisão do DESIGN: D1 com o claude revisando e sem auditor (codex sem créditos na conta, gemini sem credencial; nada
gasto no OpenRouter); D2 com `--um-engine` (claude revisou e auditou, `diversidade: nenhuma`), US$ 1,76 nominal, por
assinatura. Ledger da revisão: `sdd/reviews/LEDGER_REVISAO_F28_REVISORES_OPENROUTER.md`.

| # | Nota | Severidade | Veredito | Evidência |
|---|---|---|---|---|
| 1 | D1 · R1–R7 (claude revisou; auditor falhou: codex sem créditos, gemini sem credencial) | MED/LOW | sem resultado — refeita na D2 | `EXTERNAL_REVIEW_20261118-211157`, exit 65 |
| 2 | D2 · R1 R05/R06 antes do pronto prendia quem usa só CLIs | MED | APLICADA | Decision 8 (precedência); `diagnosticar.sh` (condição com `usa_or`/vazios) |
| 3 | D2 · R2 JSON ilegível virava "sem internet"; forma inesperada dava traceback | MED | APLICADA | Decision 4; `diagnosticar.sh` (`ilegível` ⇒ R20; `data` não objeto ⇒ R20) |
| 4 | D2 · R3 bash no macOS gravava no `~/.bashrc`; chave antiga noutro perfil | MED | APLICADA | Decision 5; `guardar-chave.sh` (`~/.bash_profile`, aviso de outro perfil) |
| 5 | D2 · R4 R07 antes de R03 escondia a opção sem custo | MED | APLICADA | Decision 8; DEFINE 1.2, Clarification A4 |
| 6 | D2 · R5 herança do ambiente sem fonte e sem o que não foi testado | MED | APLICADA | Decision 6 |
| 7 | D2 · R6 teto de 10 s por operação, não pela chamada | LOW | APLICADA | Decision 4 (prazo pelo relógio) |
| 8 | D2 · R7 aspas na chave quebravam o perfil | LOW | APLICADA | Decision 5; `guardar-chave.sh` recusa fora de `[A-Za-z0-9_-]` |
| 9 | D2 · R8 "sem base" escondido como "vazio" | LOW | APLICADA (o auditor rebateu pela Decision 3; o ponto vale) | Decision 3, mensagem com a consequência |
| 10 | D2 · N1 status não classificado aceitava a chave | MED | APLICADA | Decision 4 (402 ⇒ R16; outro ⇒ R20) |

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-11-18 | design-agent | Initial version |
| 1.1 | 2026-11-18 | design-agent | Revisão D1 (sem auditor) e D2 (uma engine só): precedência dos estados (R1, R4), JSON ilegível e status não classificado (R2, N1), perfil do bash no macOS e chave antiga em outro perfil (R3), herança do ambiente com fonte e o que não foi testado (R5), teto pela chamada inteira (R6), caracteres da chave (R7), "sem base" como aviso (R8); "uma engine só" não é gravada (a regra auditor ≠ revisor fica) |

---

## Next Step

**Ready for:** `/sdd-build sdd/features/DESIGN_F28_REVISORES_OPENROUTER.md`
