# SDD Starter

**Skills de Spec-Driven Development para iniciantes, agnósticas de agente — by RDD.**

> 🇺🇸 **English version below** — click "English version" at the end of this page.

O SDD Starter é um conjunto de **skills** portáteis que guiam qualquer agente de IA — Claude (claude.ai ou Claude Code), ChatGPT, Codex ou qualquer agente de código — por um fluxo simples de desenvolvimento guiado por especificação:

```
💡 Brainstorm  →  📋 Define  →  📐 Design  →  🔨 Build  →  📄 Handoff
```

Cada fase produz um artefato Markdown que alimenta a próxima. Você termina com requisitos de verdade, arquitetura de verdade e código funcionando — em vez de um prompt único e uma reza. As aplicações que você especificar podem mirar qualquer alvo que seu agente consiga construir: Windows, macOS, web, Lovable, Base44 e outros.

Se você quer a versão avançada deste fluxo — com Verify Gate executável, contrato de exit codes e integração com CI — veja o projeto irmão **[SDD Open](https://github.com/robertodiasduarte/sdd-open)**. O SDD Starter é a rampa de entrada; o SDD Open é a rodovia.

## As skills

| Skill | Fase | Entrada | Saída |
|---|---|---|---|
| [`sdd-engenharia-reversa-saas`](skills/sdd-engenharia-reversa-saas/) | Estudar um sistema que já existe, antes do Brainstorm (opcional) | Um SaaS que você quer tomar como referência: fontes públicas e a sua própria conta | `ENGENHARIA_REVERSA_{SAAS}.md` (cada achado com a fonte e a classe, conferido por lint) |
| [`sdd-brainstorm`](skills/sdd-brainstorm/) | Explorar a ideia | Uma ideia, problema ou notas soltas | `BRAINSTORM_{FEATURE}.md` |
| [`sdd-define`](skills/sdd-define/) | Formalizar requisitos | O arquivo de Brainstorm | `DEFINE_{FEATURE}.md` (testes de aceitação EARS, Clarity Score, Verify Gate) |
| [`sdd-design`](skills/sdd-design/) | Arquitetar a solução | Brainstorm + Define | `DESIGN_{FEATURE}.md` (arquitetura, ADRs, File Manifest) |
| [`sdd-build`](skills/sdd-build/) | Implementar — e, se o manifest tem migration, aplica a migration no banco depois de confirmar o projeto (nome e ref) | Os três artefatos + projeto gravável | Código funcionando + `BUILD_REPORT_{FEATURE}.md` (com as migrations aplicadas e a prova) |
| [`sdd-handoff`](skills/sdd-handoff/) | Fechar o ciclo | O trabalho da sessão | `HANDOFF_{FEATURE}.md` + prompt de retomada |

E sete skills **complementares**, que não entram na sequência — elas alimentam as fases:

| Skill | Para quê | Entrada | Saída |
|---|---|---|---|
| [`sdd-kb`](skills/sdd-kb/) | Ensinar seu contexto à IA | O que você sabe sobre um domínio | Base de conhecimento consultável — para legislação e normas, com vigência por regra, hierarquia das fontes e registro de conflitos |
| [`sdd-prompt-builder`](skills/sdd-prompt-builder/) | Escrever o prompt de produção do seu app | O que o prompt precisa fazer + o contrato de saída | O prompt pronto, com fórmulas e regra para dado ausente |
| [`sdd-auditoria-harness`](skills/sdd-auditoria-harness/) | Faxina e deriva do seu harness, em qualquer motor | A raiz do repositório | `AUDITORIA_SDD_<data>.md` (read-only: não altera nada) |
| [`ux-review-builder`](skills/ux-review-builder/) | Criar o padrão de experiência do seu projeto e a sua `ux-review` — a revisão que roda entre o Define e o Design | Uma entrevista sobre público, referências e o que é inaceitável | `UX_STANDARD.md` + skill `ux-review` + `UX_REVIEW_TEMPLATE.md` |
| [`sdd-seguranca`](skills/sdd-seguranca/) | Conferir as falhas de segurança mais comuns de app feito com IA — e o que fazer quando algo vazou | O app, antes de publicar (ou o incidente) | Item a item, a conferência à mão de cada falha; no incidente, primeiro fechar a porta |
| [`sdd-loop-builder`](skills/sdd-loop-builder/) | Desenhar o laço de um agente de IA que repete até terminar | O processo que se repete | Quando ele para, quanto pode gastar e como confere que terminou |
| [`sdd-governanca`](skills/sdd-governanca/) | Saber o que o sistema vai ter de provar numa fiscalização — para app que trata dinheiro, tributo ou dado pessoal | O DEFINE, depois do Define e antes do Design | `GOVERNANCA_REVIEW_{FEATURE}.md` com as lacunas, a decisão de cada uma e os requisitos aplicados no DEFINE |

E cinco skills para **preparar o ambiente e trabalhar em frentes isoladas** no seu repositório (Claude Code ou Codex no terminal):

| Skill | Para quê | Quando chamar | O que faz |
|---|---|---|---|
| [`sdd-checar-ambiente`](skills/sdd-checar-ambiente/) | Saber se está tudo pronto | Antes da primeira frente, ou quando algo estranho acontecer | Diz em uma linha se o ambiente está pronto, ou o comando exato do que falta — inclusive senha, certificado A1 ou chave já salvos no git (read-only) |
| [`sdd-higiene-dado`](skills/sdd-higiene-dado/) | Barrar dado de cliente antes do git | Ao preparar a máquina do escritório | Com o seu OK, instala um alarme de commit que recusa CPF/CNPJ, `.env`, certificado A1 e planilha nova — e explica como corrigir |
| [`sdd-iniciar-repo`](skills/sdd-iniciar-repo/) | Pôr no git um projeto que ainda não usa | Uma vez, quando a pasta do projeto ainda não tem git | Confere a pasta, lista o que entraria (senha, certificado A1, planilha, arquivo grande), propõe o `.gitignore` e, com o seu OK em cada etapa, faz o primeiro commit e cria um repositório **privado** no GitHub |
| [`sdd-new-session`](skills/sdd-new-session/) | Abrir uma frente de trabalho | No começo de cada tarefa | Cria worktree + branch a partir da produção atualizada e prepara a pasta (dependências, `.env`, as skills que estão fora do git) |
| [`sdd-release`](skills/sdd-release/) | Fechar a frente e publicar | No fim da tarefa, de dentro da pasta da frente | Verifica (testes, segredo no diff, base atualizada), mostra uma vez o que vai para produção e só publica depois do seu OK |

Cada pasta de skill é autocontida: um `SKILL.md` com o procedimento completo, `references/` com os protocolos, `assets/` com os templates canônicos de saída e (quando aplicável) `scripts/` com um validador estrutural e `agents/openai.yaml` para agentes baseados em OpenAI.

## De onde vêm estas skills

Desde a 1ª geração (nov/2026), dez skills deste repositório são **geradas** a partir do [SDD Open](https://github.com/robertodiasduarte/sdd-open): `sdd-checar-ambiente`, `sdd-iniciar-repo`, `sdd-higiene-dado`, `sdd-new-session`, `sdd-kb`, `sdd-seguranca`, `sdd-auditoria-harness`, `sdd-prompt-builder`, `sdd-engenharia-reversa-saas` e `sdd-loop-builder`. Cada uma traz um `GERADO.txt` e não se edita aqui: quem melhora, melhora no Open, e a próxima geração traz a mudança. A 1ª geração foi uma atualização grande dessas dez (skills de ambiente com `gh`, editor e modo terminal; a skill de segurança; o mesmo texto do Open).

As outras oito (`sdd-brainstorm`, `sdd-define`, `sdd-design`, `sdd-build`, `sdd-handoff`, `sdd-release`, `sdd-governanca` e `ux-review-builder`) continuam como estavam, congeladas até a próxima etapa da geração.

## Instalação

Dois caminhos, dependendo do seu agente — instruções completas no [Quickstart](docs/quickstart.pt-BR.md):

- **Claude Code** — um comando: `npx skills add robertodiasduarte/sdd-starter -a claude-code -y` (instala em `.claude/skills/` do projeto; com `-g`, em `~/.claude/skills/`, valendo em todo projeto).
- **Codex** — o mesmo comando trocando o motor: `npx skills add robertodiasduarte/sdd-starter -a codex -y` (instala em `.agents/skills/` do projeto; com `-g`, em `~/.agents/skills/` — o Codex lê essa pasta e também `~/.codex/skills/`).
- **Cursor, Kimi, Gemini CLI e outros** — mesmo comando com o nome do seu agente em `-a`. Sem Node.js, clone este repositório e copie as pastas de `skills/` para o diretório de skills do seu agente.
- **claude.ai ou ChatGPT (web)** — baixe os `.zip` prontos, um por skill, anexados na [última Release](../../releases/latest) e faça o upload no seu agente.

Cada skill diz a própria versão e a data na primeira resposta (ex.: `sdd-define v1.0.0 · out/2026`). Se você instalou pelo `.zip` e a [última Release](../../releases/latest) traz uma versão mais nova, baixe de novo — o `.zip` não se atualiza sozinho.

## Documentação

- [Quickstart](docs/quickstart.pt-BR.md) ([EN](docs/quickstart.md)) — instale e rode seu primeiro fluxo em minutos.
- [Workflow](docs/workflow.pt-BR.md) ([EN](docs/workflow.md)) — como as quatro fases se encadeiam e o que cada artefato contém.
- [Exemplo: extensão que baixa suas NFS-e](exemplos/baixar-nfse/README.md) — um kit pronto para você construir a aplicação com o seu agente, em português.

## Contribuindo

As releases são curadas. Abra uma issue para discutir antes de enviar um PR — veja [CONTRIBUTING.md](CONTRIBUTING.md).

## Verificar o que você baixou

Cada Release publica um `SHA256SUMS.txt` junto dos zips. Para conferir que o arquivo é exatamente o que foi publicado aqui — sem alteração no caminho:

```bash
shasum -a 256 -c SHA256SUMS.txt     # macOS e Linux
```

Cada skill também declara a autoria no próprio `SKILL.md` (campo `metadata.author` e a linha de crédito no rodapé), então ela viaja junto com a pasta, mesmo instalada isoladamente.

## Licença e atribuição

MIT — veja [LICENSE](LICENSE). Uso, cópia e modificação são livres; o que a licença exige é que o aviso de copyright e a atribuição sejam preservados na redistribuição.

Autoria: **Roberto Dias Duarte**. Este projeto se apoia em conceitos do **AgentSpec** de Luan Moreno Maciel — veja [NOTICE](NOTICE).

---

<details>
<summary>🇺🇸 <strong>English version</strong> (click to expand)</summary>

# SDD Starter

**Beginner-friendly, agent-agnostic Spec-Driven Development skills — by RDD.**

> Skill content is currently written in **Brazilian Portuguese**; English skill versions are planned.

SDD Starter is a set of portable **skills** that guide any AI agent — Claude (claude.ai or Claude Code), ChatGPT, Codex, or any coding agent — through a simple Spec-Driven Development flow:

```
💡 Brainstorm  →  📋 Define  →  📐 Design  →  🔨 Build  →  📄 Handoff
```

Each phase produces a Markdown artifact that feeds the next one. You end up with real requirements, a real architecture, and working code — instead of a one-shot prompt and a prayer. The apps you specify can target anything your agent can build: Windows, macOS, web, Lovable, Base44, and more.

If you want the advanced version of this workflow — with an executable Verify Gate, exit-code contracts, and CI integration — see the sibling project **[SDD Open](https://github.com/robertodiasduarte/sdd-open)**. SDD Starter is the on-ramp; SDD Open is the highway.

## The skills

| Skill | Phase | Input | Output |
|---|---|---|---|
| [`sdd-engenharia-reversa-saas`](skills/sdd-engenharia-reversa-saas/) | Study a system that already exists, before the Brainstorm (optional) | A SaaS you want as a reference: public sources and your own account | `ENGENHARIA_REVERSA_{SAAS}.md` (each finding with its source and class, checked by a lint) |
| [`sdd-brainstorm`](skills/sdd-brainstorm/) | Explore the idea | An idea, problem, or rough notes | `BRAINSTORM_{FEATURE}.md` |
| [`sdd-define`](skills/sdd-define/) | Formalize requirements | The Brainstorm file | `DEFINE_{FEATURE}.md` (EARS acceptance tests, Clarity Score, Verify Gate) |
| [`sdd-design`](skills/sdd-design/) | Architect the solution | Brainstorm + Define | `DESIGN_{FEATURE}.md` (architecture, ADRs, File Manifest) |
| [`sdd-build`](skills/sdd-build/) | Implement — and, when the manifest has a migration, applies the migration to the database after confirming the project (name and ref) | All three artifacts + writable project | Working code + `BUILD_REPORT_{FEATURE}.md` (with the migrations applied and the proof) |
| [`sdd-handoff`](skills/sdd-handoff/) | Close the cycle | The session's work | `HANDOFF_{FEATURE}.md` + resume prompt |

Plus seven **complementary** skills that are not part of the sequence — they feed the phases:

| Skill | Purpose | Input | Output |
|---|---|---|---|
| [`sdd-kb`](skills/sdd-kb/) | Teach the AI your context | What you know about a domain | A consultable knowledge base — for laws and regulations, with per-rule validity dates, a source hierarchy and recorded conflicts |
| [`sdd-prompt-builder`](skills/sdd-prompt-builder/) | Write your app's production prompt | What the prompt must do + the output contract | The ready prompt, with formulas and a rule for missing data |
| [`sdd-auditoria-harness`](skills/sdd-auditoria-harness/) | Cleanup and drift of your harness, on any engine | The repository root | `AUDITORIA_SDD_<date>.md` (read-only: changes nothing) |
| [`ux-review-builder`](skills/ux-review-builder/) | Build your project's UX standard and your own `ux-review` — the review that runs between Define and Design | An interview on audience, references and what is unacceptable | `UX_STANDARD.md` + `ux-review` skill + `UX_REVIEW_TEMPLATE.md` |
| [`sdd-seguranca`](skills/sdd-seguranca/) | Check the most common security flaws of AI-built apps — and what to do when something leaked | The app, before shipping (or the incident) | Item by item, the manual check for each flaw; in an incident, close the door first |
| [`sdd-loop-builder`](skills/sdd-loop-builder/) | Design the loop of an AI agent that repeats until done | The repeating process | When it stops, how much it may spend and how it checks it is really done |
| [`sdd-governanca`](skills/sdd-governanca/) | Know what the system will have to prove in a tax audit — for apps that handle money, taxes or personal data | The DEFINE, after Define and before Design | `GOVERNANCA_REVIEW_{FEATURE}.md` with the gaps, the decision on each one and the requirements applied to the DEFINE |

And five skills to **prepare the environment and work in isolated workstreams** in your repository (Claude Code or Codex in the terminal):

| Skill | Purpose | When to call | What it does |
|---|---|---|---|
| [`sdd-checar-ambiente`](skills/sdd-checar-ambiente/) | Know whether everything is ready | Before the first workstream, or when something odd happens | Says in one line whether the environment is ready, or the exact command for what is missing — including passwords, A1 certificates or keys already committed to git (read-only) |
| [`sdd-higiene-dado`](skills/sdd-higiene-dado/) | Stop client data before it reaches git | When preparing the office machine | With your OK, installs a commit alarm that rejects CPF/CNPJ numbers, `.env`, A1 certificates and new spreadsheets — and explains how to fix it |
| [`sdd-iniciar-repo`](skills/sdd-iniciar-repo/) | Put a project that has no git into git | Once, when the project folder has no git yet | Checks the folder, lists what would go in (passwords, A1 certificates, spreadsheets, large files), proposes the `.gitignore` and, with your OK at each step, makes the first commit and creates a **private** GitHub repository |
| [`sdd-new-session`](skills/sdd-new-session/) | Open a workstream | At the start of each task | Creates worktree + branch from up-to-date production and prepares the folder (dependencies, `.env`, skills kept out of git) |
| [`sdd-release`](skills/sdd-release/) | Close the workstream and ship | At the end of the task, from inside the workstream folder | Checks (tests, secrets in the diff, up-to-date base), shows once what goes to production and ships only after your OK |

Each skill folder is self-contained: a `SKILL.md` with the full procedure, `references/` with protocols, `assets/` with the canonical output templates, and (where applicable) `scripts/` with a structural validator and `agents/openai.yaml` for OpenAI-based agents.

## Where these skills come from

Since the first generation (Nov 2026), ten skills in this repository are **generated** from [SDD Open](https://github.com/robertodiasduarte/sdd-open): `sdd-checar-ambiente`, `sdd-iniciar-repo`, `sdd-higiene-dado`, `sdd-new-session`, `sdd-kb`, `sdd-seguranca`, `sdd-auditoria-harness`, `sdd-prompt-builder`, `sdd-engenharia-reversa-saas` and `sdd-loop-builder`. Each one carries a `GERADO.txt` and is not edited here: improvements go to SDD Open, and the next generation brings them. The first generation was a large update of those ten.

The other eight (`sdd-brainstorm`, `sdd-define`, `sdd-design`, `sdd-build`, `sdd-handoff`, `sdd-release`, `sdd-governanca` and `ux-review-builder`) stay as they were, frozen until the next stage of the generation.

## Installation

Two paths, depending on your agent — full instructions in the [Quickstart](docs/quickstart.md):

- **Claude Code** — one command: `npx skills add robertodiasduarte/sdd-starter -a claude-code -y` (installs into the project's `.claude/skills/`; add `-g` for `~/.claude/skills/`).
- **Codex** — same command, different engine: `npx skills add robertodiasduarte/sdd-starter -a codex -y` (installs into the project's `.agents/skills/`; with `-g`, into `~/.agents/skills/` — Codex reads that folder and `~/.codex/skills/` too).
- **Cursor, Kimi, Gemini CLI and others** — same command with your agent's name in `-a`. Without Node.js, clone this repo and copy the folders under `skills/` into your agent's skills directory.
- **claude.ai or ChatGPT (web)** — download the ready-made per-skill `.zip` files attached to the [latest Release](../../releases/latest) and upload them to your agent.

Each skill states its own version and date in its first reply (e.g. `sdd-define v1.0.0 · out/2026`). If you installed from a `.zip` and the [latest Release](../../releases/latest) has a newer version, download it again — a `.zip` does not update itself.

## Documentation

- [Quickstart](docs/quickstart.md) ([PT-BR](docs/quickstart.pt-BR.md)) — install and run your first flow in minutes.
- [Workflow](docs/workflow.md) ([PT-BR](docs/workflow.pt-BR.md)) — how the four phases chain together, and what each artifact contains.
- [Example: a Chrome extension that downloads Brazilian service invoices](exemplos/baixar-nfse/README.md) — a ready kit to build with your agent, in Portuguese.

## Contributing

Releases are curated. Please open an issue to discuss before sending a PR — see [CONTRIBUTING.md](CONTRIBUTING.md).

## License & attribution

MIT — see [LICENSE](LICENSE). This project builds on concepts from **AgentSpec** by Luan Moreno Maciel — see [NOTICE](NOTICE).

</details>
