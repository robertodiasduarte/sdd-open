<!-- Idioma: [English](README.md) · **Português** -->

# SDD Open by RDD

**Aceite executável, não prosa — no agente que você já usa.**

Spec-Driven Development para **Claude Code, Codex CLI, Gemini CLI, Cursor, Kimi Code, Grok
Build e GLM via Claude Code**. Uma fonte só (`.agents/skills/` + `AGENTS.md`), adaptadores
gerados por agente, e um mecanismo que os outros frameworks não têm: toda spec carrega um
comando com exit code que decide se a fase acabou.

```yaml
verify_gate:
  kind: test
  cmd: "npm test -- src/checkout/pricing.test.ts"
  pass_when: "exit 0"
```

Isso não é documentação. `sdd/bin/verify-gate.sh` roda o comando, e as fases Build e Release
tratam o resultado como bloqueante. Aceite deixa de ser um parágrafo que alguém lê por cima e
vira uma coisa que a máquina executa.

## Instalar (2 comandos)

```bash
git clone https://github.com/robertodiasduarte/sdd-open.git /tmp/sdd-open
cd meu-projeto && bash /tmp/sdd-open/bin/sdd-open.sh init --vendors codex   # ou claude, gemini, cursor, kimi
```

O `init` mostra o plano, pede sua confirmação, e termina com um diagnóstico por agente. Nada
seu é sobrescrito. [Quickstart completo →](docs/pt-BR/quickstart.md)

## O que vem no pacote

| Mecanismo | O que faz | Onde |
|---|---|---|
| **Verify Gate** | aceite como comando, com contrato de 6 estados (`0/2/3/4/5/64`) — inclusive *inconclusivo* e *precisa de assinatura humana*, porque "verde ou vermelho" mente quando falta ferramenta ou o critério é estético. Saída sempre termina em `RESULTADO:` + o que fazer; `--strict` para CI | `sdd/bin/verify-gate.sh` · `sdd/templates/fragments/VERIFY_GATE.md` |
| **Gramática EARS** | testes de aceitação em padrões fixos (When / While / If–Then / Where / shall); o padrão *unwanted* obriga a nomear o modo de falha antes de construir | `fragments/EARS.md` |
| **Protocolo de clarificação** | ambiguidade vira marcador na spec, nunca suposição; marcador ativo = exit `5`, um estado próprio que nenhum loop "corrige" iterando o design | `fragments/CLARIFY.md` |
| **Veredito graduado de release** | PASS / CONCERNS / FAIL / WAIVED; dispensa é humana, de classe restrita, com motivo escrito. Publicar pede um OK só, depois de um bloco que diz o que sobe e se o push publica sozinho | skill `sdd-release` |
| **Contrato de evidência** | no relatório de build um critério só vira `true` com arquivo abrível ou recibo humano datado — "deve funcionar" é `false` | `sdd/bin/report-lint.py` · `fragments/EVIDENCIA.md` |
| **Playbook de landmines (ACE-lite)** | armadilhas com ID estável, contadores *ajudou/mordeu*, superfícies greppáveis e atualização só por delta — uma sessão propõe, a fase Release aplica com OK humano | `sdd/playbook.md` · `sdd/bin/playbook-lint.sh` · skill `sdd-playbook` |
| **Avaliação em contexto fresco** | quem julga não é quem constrói: um agente sem a conversa do build prova cada critério executando, nunca lendo o diff | skill `sdd-build` › `references/contexto-fresco.md` |
| **Engenharia de prompt como entregável** | quando a spec inventaria um prompt de produção, a fase Build o escreve por uma skill com contrato de saída explícito, fórmulas escritas por extenso e regra para contexto ausente — em vez de deixar o modelo estimar. Ligada como slot substituível (`prompts.builder_skill`), já com um default | skill `sdd-prompt-builder` |
| **Review adversarial de 2º vendor** | resposta em formato fixo (veredito, ≤3 riscos, correções, o que ignorar); toda nota é aplicada ou rebatida por escrito | `fragments/ADVISOR_CONSULT.md` |
| **Auditoria read-only do harness** | harness acumula: comando que ninguém chama, agente que ninguém despacha, doc que derivou do código. Uma passada read-only inventaria cada comando, agente, skill, hook e script, mede referências de entrada e recência, e emite um único `AUDITORIA_SDD_<data>.md` — nunca apaga: a faxina em si continua decisão humana | skill `sdd-auditoria-harness` · `scripts/collect_evidence.py` |
| **Revisão de governança** | em sistema financeiro, contábil ou fiscal, compara o DEFINE com um catálogo curado (lançamento que não se apaga, fechamento de período, trilha de auditoria, segregação de funções, aritmética exata…) e recomenda requisitos em EARS com teste negativo que o Verify Gate executa; base legal só citada quando confirmada no catálogo; uma decisão por item, e a recusa fica registrada como risco aceito | skill `sdd-governanca` |
| **Base de conhecimento** | o que você sabe sobre um domínio (um processo, uma norma, um manual) organizado em conceitos e receitas que o agente consulta; em norma, o período em que cada regra vale, a fonte com SHA-256 e o mapa regra → fonte → teste. O Define só cita domínio que existe, conferido por `sdd/bin/kb-dominios.py` | skill `sdd-kb` · `sdd/kb/` |
| **Handoff por ficha** | um arquivo por feature no repositório, com prompt de retomada autossuficiente — sem depender da memória de nenhum agente | skill `sdd-handoff` · `sdd/handoffs/` |

## As 17 skills

| Bloco | Skills | Quando |
|---|---|---|
| **Preparar** | `sdd-checar-ambiente` · `sdd-iniciar-repo` · `sdd-higiene-dado` · `sdd-new-session` | uma vez por computador e por projeto (está tudo pronto? pôr no git, alarme de commit contra dado de cliente); a new-session a cada frente de trabalho |
| **Criar** | `sdd-kb` (opcional) · `sdd-brainstorm` · `sdd-define` · `sdd-governanca` · `sdd-ux-review` · `sdd-design` · `sdd-build` | uma vez por feature — o fluxo SDD |
| **Fechar** | `sdd-handoff` · `sdd-release` | no fim de cada sessão e de cada frente |
| **Transversais** | `sdd-iterate` · `sdd-playbook` · `sdd-prompt-builder` · `sdd-auditoria-harness` | quando o caso pedir |

Nunca usou git nem terminal? O [guia do aluno](docs/pt-BR/guia-do-aluno.md) mostra o caminho
inteiro, da primeira instalação à primeira publicação.

## O fluxo

```text
preparar uma vez:  sdd-checar-ambiente · sdd-iniciar-repo · sdd-higiene-dado · sdd-new-session · (opcional) sdd-kb

/sdd-brainstorm → /sdd-define → /sdd-governanca → /sdd-ux-review → /sdd-design → /sdd-build → /sdd-release
  (opcional)           ↑       (se há dinheiro)     (se há UI)          ↑             │             │
                       └───────── /sdd-iterate corrige o rumo ──────────┘             │             │
                                                                                      ▼             ▼
                                                            o Verify Gate roda aqui — e de novo aqui — bloqueando as duas vezes
```

`sdd-handoff` e `sdd-playbook` são transversais: fecham sessões e acumulam o que mordeu.

## Como funciona o agnosticismo

- **Uma fonte:** `.agents/skills/sdd-*/` — o padrão [Agent Skills](https://agentskills.io) que
  Codex, Gemini CLI e Kimi Code leem nativamente.
- **Um contrato:** `AGENTS.md` com um bloco gerenciado (`<sdd-open-instructions>…`) que convive
  com o que você já tinha no arquivo.
- **Adaptadores gerados**, nunca mantidos à mão: `sdd-open.sh sync` escreve `.claude/skills/`,
  `.cursor/skills/`, `CLAUDE.md`, `GEMINI.md` e `.gemini/settings.json` a partir da fonte, com
  cabeçalho que avisa; `sync --check` detecta quando alguém editou a cópia.
- **Território do usuário:** `sdd/` (specs, relatórios, fichas, playbook, config) nunca é
  tocado pelo `sync`.

Funciona em macOS, Linux e Windows (Git Bash/WSL): bash 3.2, zero zsh, zero symlink.

## Documentação

- [Quickstart](docs/pt-BR/quickstart.md) ([EN](docs/quickstart.md)) — instalar, configurar, a primeira spec
- [Convenções de saída](docs/cli-conventions.md) — o vocabulário dos comandos e os exit codes
- [Contrato do Verify Gate](docs/pt-BR/verify-gate-contract.md) ([EN](docs/verify-gate-contract.md))
- [Guia de adaptação](docs/pt-BR/adaptation-guide.md) ([EN](docs/adaptation-guide.md)) — slots do config, landmines, worktrees
- [Comparativo](docs/pt-BR/comparison.md) ([EN](docs/comparison.md)) — Spec-Kit, OpenSpec, BMAD, Kiro, Tessl
- [Roadmap](docs/pt-BR/roadmap.md) ([EN](docs/roadmap.md)) — o que está planejado e o que está em avaliação
- [Guia do aluno](docs/pt-BR/guia-do-aluno.md) — passo a passo para quem nunca usou git nem terminal

## Trilha

- **[sdd-starter](https://github.com/robertodiasduarte/sdd-starter)** — a rampa: skills para
  agentes sem sistema de arquivos (claude.ai, ChatGPT). Sem gate executável.
- **SDD Open** — a rodovia: este repositório. Os nomes das skills coincidem de propósito; use
  um ou outro por projeto.

## Idioma

As skills, templates e mensagens dos comandos estão em **português do Brasil** — a língua da
comunidade de onde isto vem. A mecânica (gate, exit codes, layout) é neutra. README e
quickstart existem em inglês.

## Contribuindo, licença e atribuição

Releases são curadas; abra uma issue antes de um PR — [CONTRIBUTING.md](CONTRIBUTING.md).
MIT — [LICENSE](LICENSE). A estrutura de fases descende do **AgentSpec** de Luan Moreno Maciel;
o que foi acrescentado está listado em [NOTICE](NOTICE).
