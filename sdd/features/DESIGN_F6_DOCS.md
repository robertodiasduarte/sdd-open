# DESIGN: F6 Docs do sdd-open

> Documentação e texto, sem mecanismo novo. O guia do aluno é adaptado do starter com 6 correções de fato. O quickstart ganha a regra do método e a tabela "onde roda". O roadmap sai em EN e PT, com o status literal do `comparison.md`. README e `AGENTS.md.tmpl` alcançam o pacote. As 7 skills de fase ganham "Por que cada regra existe" sem tocar num passo. Um teste novo, `tests/test_docs.py`, abre cada link relativo e confere o mínimo de cada documento. De passagem, corrige 2 links quebrados e uma frase falsa do `adaptation-guide.md` (P1).

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | F6_DOCS |
| **Date** | 2026-10-29 |
| **Author** | SDD Design by RDD (sessão com Roberto Dias Duarte) |
| **BRAINSTORM** | `sdd/features/BRAINSTORM_F6_DOCS.md` |
| **DEFINE** | `sdd/features/DEFINE_F6_DOCS.md` (v1.1) |
| **UX REVIEW** | não se aplica (DEFINE, Clarifications: sem tela; tom e glossário vêm do guia do starter e da camada da F4) |
| **LLM Prompts** | false |
| **Status** | Ready for Build |

---

## Architecture Overview

```text
 Fontes (leitura)                                   Pacote sdd-open (escrita)
 ─────────────────                                  ─────────────────────────
 sdd-starter/docs/guia-do-aluno.pt-BR.md ──adapta──► docs/pt-BR/guia-do-aluno.md (novo, só PT)
 sdd-starter/docs/quickstart.pt-BR.md ──regra+tabela► docs/quickstart.md · docs/pt-BR/quickstart.md
 plano, seção 8 + comparison.md (status) ─────────► docs/roadmap.md · docs/pt-BR/roadmap.md (novos)
                                                    docs/comparison.md · docs/pt-BR/comparison.md (1 link)
 achado P1 (link + frase falsa) ──────────────────► docs/adaptation-guide.md · docs/pt-BR/adaptation-guide.md
 .agents/skills/ (17) ────────────────────────────► README.md · README.pt-BR.md · AGENTS.md.tmpl
 sdd-starter/skills/sdd-release (10 regras) ──┐
 texto das 7 skills de fase ──────────────────┴────► ## Por que cada regra existe (7 SKILL.md, patch)
                                                     │  logo antes de ## Encerramento (obrigatório)
                                                     ▼
 tests/test_docs.py (novo) ── links e âncoras · guia · quickstarts · roadmaps · comparison ·
                              README/AGENTS.md.tmpl · seção nas 9 skills
 tests/test_contrato_build_release.py · tests/test_correcoes_w0.py ── versões novas (de propósito)

 Verify Gate (git archive HEAD → publish-gate ci [G2 PII, G3 MANIFEST] → unittest no piso)

 Fora do gate (sdd/reports/evidence/F6_DOCS/): comandos-intactos.log (v2.2.6 × HEAD, 7 skills) ·
 check-versions.log · contratos-intactos.log · baseline.log · sabotagem.log · codepoints.log · links-pr.log
```

---

## Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| Guia do aluno | Caminho do zero à release para quem nunca usou git, com as 17 skills | Markdown PT-BR |
| Quickstarts | Regra do método, "valide antes de seguir" por fase, tabela "onde roda" | Markdown EN + PT |
| Roadmaps | 5 temas planejados, deltas em avaliação, reconciliação planejada, sem data | Markdown EN + PT, tabela |
| README e `AGENTS.md.tmpl` | Mapa das 17 skills, `kb-dominios.py`, OK único, links novos | Markdown; o template vira o bloco gerenciado do `AGENTS.md` |
| Seções "Por que cada regra existe" | Motivo das regras de cada skill de fase, onde a regra mora | Markdown dentro de 7 `SKILL.md` |
| `tests/test_docs.py` | Prova o mínimo de cada documento e a existência de cada link relativo | unittest, stdlib, sem rede |
| Scripts de evidência | Comandos intactos, versões, contratos, baseline, sabotagem, code points | bash + Python em `sdd/reports/evidence/F6_DOCS/` (fora do commit do produto) |

---

## Key Decisions

### Decision 1: Guia do aluno: o que muda em relação ao starter

| **Status** | Accepted | · | **Date** | 2026-10-29 |

**Context:** o guia do starter (494 linhas) foi escrito para `npx skills add`, 15 skills, 2 agentes e a pasta `sdd/` fora do git. Copiar com troca de nomes deixaria 6 afirmações falsas no open.

**Choice:** `docs/pt-BR/guia-do-aluno.md` mantém os 10 blocos numerados do starter (`## 1. O que você precisa` … `## 10. Perguntas frequentes`), o sumário com âncoras e o molde das fichas, com estas correções:

| # | No starter | No open |
|---|---|---|
| 1 | `npx skills add … -g`, "quando sair versão nova: `npx skills update`" | `git clone` do sdd-open + `bash …/bin/sdd-open.sh init --vendors <agente> --dry-run` (ler o plano) e depois `--yes` (rodado pelo agente, sem terminal interativo, o `init` sem `--yes` sai CANCELADO e não escreve nada). Atualizar: `git pull` no clone → `doctor` → para cada skill que ele apontar, apagar `.agents/skills/<skill>` (edições suas nela se perdem) → `init --vendors … --yes` → `sync`. O `init` nunca sobrescreve skill instalada e o `sync` só regenera adaptadores |
| 2 | 2 agentes (Claude Code, Codex) | os 7, numa tabela "como chamar uma skill": Claude Code, Grok Build e GLM `/sdd-define`; Codex CLI `$sdd-define` ou pela descrição; Gemini CLI `/sdd-define`; Cursor `/sdd-define`; Kimi Code `/skill:sdd-define`. Em qualquer um vale "use a skill sdd-define" |
| 3 | 15 skills em 3 blocos + avançadas | 17 skills em 4 blocos: Preparar (checar-ambiente, iniciar-repo, higiene-dado, new-session) · Criar (kb, brainstorm, define, governanca, ux-review, design, build) · Fechar (handoff, release) · Transversais (iterate, playbook, prompt-builder, auditoria-harness) |
| 4 | `ux-review-builder` | `sdd-ux-review`, com a entrevista de público opcional da F5 |
| 5 | "A pasta `sdd/` não vai para o GitHub", documentos em `sdd/NOME.md` | `sdd/` é versionada: config, playbook, specs (`sdd/features/`), relatórios (`sdd/reports/`), revisões (`sdd/reviews/`), fichas (`sdd/handoffs/`) e ledger (`sdd/releases/`) entram no git e mostram o histórico das decisões; o `sync` nunca escreve nela |
| 6 | Linha de identificação com `sdd-starter/releases/latest` | `sdd-release v2.3.1 · out/2026 · versão atual: https://github.com/robertodiasduarte/sdd-open/releases/latest` |

O que entra de novo, por ser do open:
- **Requisitos** (bloco 1): além de computador, conta no GitHub e um dos 7 agentes, o git, o bash ≥ 3.2 (no Windows, Git Bash ou WSL) e o python3 ≥ 3.9, porque as fases rodam os conferidores de `sdd/bin/`. A skill de diagnóstico e o `doctor` dizem o que falta.
- **Instalação num projeto sem git** (bloco 6, Dia 1): o `init` para em pasta sem git. O caminho é: conferir que a pasta não está em iCloud, OneDrive, Dropbox ou Google Drive; `git init -b main` (só cria o git vazio, nada é salvo; mesmo comando do Passo 3 da `sdd-iniciar-repo`); `init --vendors … --dry-run` e `--yes`; a `sdd-iniciar-repo`, que reconhece "git sem nenhum commit" e segue do inventário.
- **O Verify Gate** no bloco 3 ("como as skills falam") e no bloco 8 ("quando algo dá errado"), com os exits traduzidos: 0 pronto · 2 vermelho, a skill corrige e roda de novo · 3 não deu para conferir (falta uma ferramenta) · 4 precisa da sua assinatura (aceite visual) · 5 a spec tem uma dúvida marcada, volte ao Define · 64 o DEFINE não tem gate válido.
- **A parada ⏸️** com as linhas **Brief** e **Sessão nova** (avaliador sem esta conversa).
- **Glossário** com os termos do open: Verify Gate e os exits, slot, adaptador e `sync`, `doctor`, landmine e playbook, contexto fresco, ledger, KB Domains, bloco do OK.
- **Bloco 7 (dia a dia):** retomada pela ficha `sdd/handoffs/HANDOFF_<FEATURE>.md`.

A ficha da `sdd-auditoria-harness` não cita a skill de segurança do repositório privado: diz "uma auditoria de segurança, fora deste pacote". Os exemplos continuam fictícios (pasta `Honorarios`), sem CPF, CNPJ, telefone, e-mail fora de `example.com` nem caminho de home. O guia não usa nenhum literal de `PROMESSA_VAZIA` (`tests/test_correcoes_w0.py`: `/drive`, `slice 2`, `Step 1.5`, `CONTEXTO de domínio` …) nem descreve convenções deste repositório (branch `docs/`, sessões numeradas).

**Rationale:** os 10 blocos já passaram por alunos no starter; o que muda são os fatos do open.

**Alternatives Rejected:**
1. Guia novo do zero, a partir das skills: rejeitado porque perde o tom e a ordem que já funcionaram.
2. Só um link para o guia do starter: rejeitado porque ensinaria `npx skills` e o layout errado de `sdd/`.

**Consequences:** cerca de 480 linhas a manter junto com as skills; o teste pega link quebrado e as premissas proibidas, não texto velho (risco aceito no BRAINSTORM).

### Decision 2: Quickstart: regra do método, 4 validações e a tabela "onde roda"

| **Status** | Accepted | · | **Date** | 2026-10-29 |

**Context:** o passo 4 do quickstart do open cobre o Define em detalhe e junta Design, Build e Release numa linha. O starter tem a regra do método e um "Valide antes de seguir" por fase.

**Choice:** nos dois idiomas, o passo 4 (`## 4. Sua primeira spec` / `## 4. Your first spec`) passa a ter, nesta ordem:
1. a regra em citação: PT "**A regra do método:** nunca siga para a próxima fase com um documento que você não leu. Corrigir uma frase agora custa minutos; corrigir depois que o código existe custa horas." EN "**The method's rule:** never move on to the next phase with a document you have not read. Fixing a sentence now costs minutes; fixing it after the code exists costs hours.";
2. Brainstorm (opcional), Define (o texto atual, intacto), Design (com a tabela) e Build, cada um terminando numa linha que começa por `**Valide antes de seguir:**` / `**Validate before moving on:**`;
3. Release: uma frase sobre o OK único, sem linha de validação (a skill já mostra o bloco).

A tabela fica dentro do Design, com o cabeçalho fixo `| Você quer… | Escreva no Design | No Build |` / `| You want… | Write in the Design | In the Build |` e 4 linhas: site ou sistema web; programa de Windows; programa de Mac; rotina sem tela (script que lê e gera arquivos). A 3ª coluna é igual em todas: "qualquer um dos 7 agentes, aberto na pasta do projeto". Logo abaixo, uma frase lista os 7 e diz por que vale para todos: o Build roda o Verify Gate num terminal, e todos os 7 têm um. Sem linha Lovable (BRAINSTORM, decisão 6).

**Correção P1 do passo 5** ("When the package updates" / "Quando o pacote atualizar"): hoje o bloco manda `git pull` + `sync --check` + `sync`, e o texto não diz que skill instalada não muda. O bloco passa a ser `git pull` no clone → `doctor` (que lista cada skill e cada `sdd/bin/*` mais velhos que o pacote) → para cada um, apagar e rodar `init --vendors … --yes` → `sync`, com uma frase dizendo que o `sync` só regenera adaptadores e que edições na pasta apagada se perdem. O resto do passo 5 (cabeçalho `sdd-open:generated`, `sync --check`) fica como está.

**Rationale:** a validação por fase é o hábito que mais evita retrabalho; a tabela responde à pergunta "onde eu construo?" sem eleger um agente (P2). O passo 5 de hoje deixa a skill velha respondendo "EM DIA" (`AVAL-DESIGN-atualizar-pull-sync.log`).

**Alternatives Rejected:**
1. Só a regra no topo, sem as 4 linhas: rejeitada porque a regra solta não vira hábito no momento da fase.
2. Manter a coluna "No Build" com nomes de agentes por linha: rejeitada porque sugere que um agente é melhor para um tipo de app.

**Consequences:** o passo 4 cresce cerca de 30 linhas em cada idioma; o resto do quickstart não muda.

### Decision 3: Roadmap: tabela com status literal, sem data

| **Status** | Accepted | · | **Date** | 2026-10-29 |

**Context:** o `comparison.md` promete um roadmap e marca "Specs como deltas" *(em avaliação)* e a reconciliação *(planejado)*. O critério 6 da Ficha exige que deltas continue declarado como não feito.

**Choice:** `docs/roadmap.md` e `docs/pt-BR/roadmap.md`, com o cabeçalho de idioma dos outros pares (`<!-- Language: **English** · [Português](pt-BR/roadmap.md) -->` e o inverso), um parágrafo "como ler" (planejado = intenção sem data; em avaliação = pode não acontecer) e uma tabela `| Tema | O que traz | Status |` / `| Theme | What it brings | Status |` com 7 linhas:

| Tema (PT / EN) | O que traz (resumo da seção 8 do plano) | Status |
|---|---|---|
| Hooks e evidência / Hooks and evidence | relatório que recusa evidência ignorada pelo git e avaliação pendente; baseline vermelho automático; hooks de `pre-commit` e `pre-push` instalados pelo `init` | planejado / planned |
| Fluxo encadeado / Chained flow | cada fase oferece a seguinte; classes de decisão; parada com retomada quando o agente não abre sessão nova | planejado / planned |
| Revisão adversarial / Adversarial review | revisão por outro vendor com diff congelado, registro de engines e gate offline | planejado / planned |
| Contexto e governança / Context and governance | mapa do domínio antes do Define, patterns do projeto, governança obrigatória em sistema financeiro | planejado / planned |
| `sdd-loop-builder` e `sdd-drive` | skill para LLM em laço no código; condução de várias fases com as mesmas paradas | planejado / planned |
| Reconciliação spec ↔ código / Spec ↔ code reconciliation | conferir que o manifest cobriu todo requisito | planejado / planned |
| Specs como deltas / Specs as deltas | spec como diferença contra um conjunto canônico | em avaliação / under evaluation |

Sem ano, sem versão futura, sem número interno de frente (F7–F14). Uma frase final diz que cada mecanismo traz o próprio documento quando sair, e que o `comparison.md` é a referência do que já existe.

**Rationale:** tabela com status por linha é o que o teste confere sem ambiguidade; o texto curto não promete o que o plano ainda pode mudar.

**Alternatives Rejected:**
1. Roadmap com datas ou versões: rejeitado porque o ritmo depende de sessões, não de calendário.
2. Uma seção por frente F7–F14: rejeitado porque os números são internos ao programa.

**Consequences:** o roadmap muda quando um tema sai (a linha passa a dizer *disponível em vX.Y.Z*, e o teste é ajustado de propósito).

### Decision 4: README e `AGENTS.md.tmpl`: o que entra e as frases fixas

| **Status** | Accepted | · | **Date** | 2026-10-29 |

**Context:** o README mostra 7 fases e 12 mecanismos; o `AGENTS.md.tmpl` lista as fases. Nenhum cita as skills de preparo, a KB nem o OK único.

**Choice:**
- **README (EN e PT):**
  - seção nova `## The 17 skills` / `## As 17 skills`, logo depois de "What ships" / "O que vem no pacote", com os 4 blocos da Decision 1 numa tabela `| Block | Skills | When |`;
  - o diagrama do fluxo ganha uma linha antes: "prepare once: sdd-checar-ambiente · sdd-iniciar-repo · sdd-higiene-dado · sdd-new-session · (optional) sdd-kb";
  - a linha da `sdd-release` em "What ships" (Graded release verdict) acrescenta a frase fixa: EN "a single approval, after one block that says what goes up and whether the push publishes by itself"; PT "um OK só, depois de um bloco que diz o que sobe e se o push publica sozinho";
  - uma linha nova em "What ships": KB com `sdd-kb` e `sdd/bin/kb-dominios.py`;
  - em "Documentation": o guia (`docs/pt-BR/guia-do-aluno.md`, "(PT)" no README em inglês) e o roadmap do idioma.
- **`AGENTS.md.tmpl`:**
  - a tabela ganha uma linha "Antes" com `sdd-checar-ambiente` · `sdd-iniciar-repo` · `sdd-higiene-dado` · `sdd-new-session` (preparar a máquina, o repositório e a frente) e uma linha "KB" com `sdd-kb` (opcional, `sdd/kb/`);
  - a linha da fase 1 acrescenta: "o KB Domains passa por `sdd/bin/kb-dominios.py`";
  - regra nova 7, numa linha: "**Publicar pede um OK só.** A `sdd-release` mostra um bloco com o que sobe e se o push publica sozinho, e só segue com o sim de quem usa.";
  - o marcador de vendors entre chaves duplas e as 6 regras numeradas atuais ficam como estão.

**Rationale:** as frases fixas ("um OK só", "single approval") são as âncoras que o teste confere; o texto ao redor pode evoluir.

**Alternatives Rejected:**
1. A frase do OK só na linha da fase 4 da tabela (versão 1.0 deste DESIGN): rejeitada na revisão (M4) porque o DEFINE pede uma regra, e a regra numerada é o que o agente lê como obrigação.
2. Listar as 17 skills no `AGENTS.md.tmpl` com descrição: rejeitada porque o agente já lê as `description` em `.agents/skills/`.

**Consequences:** o bloco gerenciado cresce 4 linhas no projeto de quem instala; o `sync --check` acusa o bloco antigo como desatualizado até o próximo `sync` (comportamento atual, coberto pelo `test_sync_reescreve_so_o_bloco_quando_a_fonte_muda`).

### Decision 5: "Por que cada regra existe": posição, formato e conteúdo por skill

| **Status** | Accepted | · | **Date** | 2026-10-29 |

**Context:** o open já tem a seção em 2 skills, no formato `- **regra** — motivo`. As 7 de fase terminam em `## Encerramento (obrigatório)` seguido do rodapé.

**Choice:** em cada uma das 7, a seção `## Por que cada regra existe` entra logo antes de `## Encerramento (obrigatório)`, com 4 a 10 itens. Cada item nomeia uma regra que a skill **já tem** e dá o motivo de quem usa, sem citar passo pelo número. Nenhum item traz pergunta em negrito com `?`, bloco cercado, `curl … | sh` nem nome de ferramenta de um agente só. Regras previstas:

| Skill (versão nova) | Regras com motivo |
|---|---|
| `sdd-brainstorm` 2.1.1 | uma pergunta por vez; mínimo de 3 antes das abordagens; sempre perguntar por amostras; liderar com a recomendação; YAGNI registrado, nunca inventado; 2 confirmações antes de gravar; nunca inventar a resposta do usuário numa sessão autônoma |
| `sdd-define` 2.3.1 | o aceite é um comando com exit; EARS com o padrão indesejado; recusar adjetivo sem número; marcador no lugar da dúvida, nunca suposição; teto de cerca de 10 ATs; KB Domains só de `ls sdd/kb/`; baseline vermelho do gate composto |
| `sdd-governanca` 2.2.1 | base legal só confirmada no catálogo; uma decisão por lacuna; N.A. sem relatório; o script de prova só sai 0 quando o banco recusa; nunca contra produção; quem escreveu o Define não se revisa; a skill recomenda, o profissional decide |
| `sdd-ux-review` 2.3.1 | interface inclui CLI, arquivo e e-mail; violação de princípio vira MUST; contraste medido, não estimado; lente nunca vira MUST; entrevista quando o DEFINE não diz o público ou quando o aluno pede; não rodar por cerimônia |
| `sdd-design` 2.1.1 | títulos `### Decision N:` fixos; manifest sem ciclo; varredura de landmines sempre registrada, mesmo com 0; o DESIGN não escreve o prompt de produção; revisão por outro vendor aqui, onde mudar é barato; `design-lint` no arquivo gravado |
| `sdd-build` 2.2.1 | o critério de parada é o gate; 1ª tarefa é o gate falhando; commit antes de qualquer revisão; quem julga não é quem constrói; evidência abrível, nunca "deve funcionar"; correção é redispatch fresco; migration provada por leitura; drift de prompt para e pergunta |
| `sdd-release` 2.3.1 | do starter, adaptadas ao open: o OK vem antes do push; `git add` por nome, nunca `-A`; a base é integrada antes do OK e reconferida antes do push (se mudou, re-landar, nunca `--force`); ledger dentro do commit atômico, append-only, sem SHA; o deploy é conferido pelo SHA publicado; nunca redisparar run antigo; uma pergunta só, na última linha do bloco; "o deploy espera os testes?" vem do script, não da memória; o agente nunca emite WAIVED; o comando remoto não pede senha (10 itens) |

Versão: patch nas 7 (`metadata.version` e a linha de identificação). `metadata.updated` continua `"2026-10"`.

**Rationale:** a seção no fim não desloca nenhum passo, não entra na camada de conversa e não muda o que o `comandos-intactos` extrai (o script a remove antes de comparar, como já faz com a camada).

**Alternatives Rejected:**
1. A seção no começo da skill: rejeitada porque empurra os passos para baixo e o agente lê a motivação antes do procedimento.
2. Motivo inline, ao lado de cada regra: rejeitado porque mexe nos passos, que o `comandos-intactos` protege.

**Consequences:** cada skill cresce 12 a 25 linhas (a maior, `sdd-release`, vai de 275 para cerca de 300, longe das 500); 3 testes que fixam versão mudam de propósito (manifest 21, 22).

### Decision 6: `tests/test_docs.py`: o que confere e como

| **Status** | Accepted | · | **Date** | 2026-10-29 |

**Context:** o DEFINE pede 7 grupos de checagem, sem rede, no piso Python 3.9. A varredura feita no design achou 2 links quebrados hoje (`adaptation-guide.md`, EN e PT), então a checagem de links tem baseline vermelho real além dos arquivos novos.

**Choice:** um módulo com 7 classes, lendo direto de `RAIZ` (`tests/apoio.py`), sem `Sandbox`:

| Classe | Confere |
|---|---|
| `Links` | todo `](alvo)` fora de bloco cercado em `README.md`, `README.pt-BR.md`, `CONTRIBUTING.md` e `docs/**/*.md`: alvo sem `http://`, `https://`, `mailto:` existe a partir da pasta do arquivo; `#âncora` (no próprio arquivo ou num `.md` da árvore) casa com um título pela regra do GitHub. A mensagem de falha lista `arquivo:linha → alvo` |
| `Guia` | 10 títulos `## 1.` a `## 10.`; um `#### sdd-<nome>` para cada pasta de `.agents/skills/`; os 7 agentes; `init --vendors`, `--yes`, `python3`, `doctor`; uma linha com `apague` e `init` (o caminho de atualização); `sdd-open/releases/latest`; nenhum de `npx skills`, `15 skills`, `ux-review-builder`, `sdd-starter/releases`, caminho no layout do starter (`sdd/BRAINSTORM_`, `sdd/DEFINE_`, `sdd/DESIGN_`, `sdd/BUILD_REPORT_`, `sdd/HANDOFF_`), nem uma linha em que `sdd/` venha seguido, até 80 caracteres depois, de "não vai para o GitHub" ou "fora do git" (a negação presa a `sdd/`; dizer que o `.env` não vai para o GitHub continua livre) |
| `Quickstart` | por idioma: a frase da regra; ≥ 4 linhas que começam por `**Valide antes de seguir:**` / `**Validate before moving on:**`; **dentro do trecho de `## 4.` até `## 5.`**, o cabeçalho fixo da tabela e os 7 agentes (fora dele seria circular: a tabela do topo já cita os 7); no trecho de `## 5.` até o próximo `## `, `doctor` e `init`; nenhum "Lovable" no arquivo |
| `Roadmap` | por idioma: o cabeçalho de idioma apontando o par; **só nas linhas de tabela** (`^\|`), as 7 linhas com o status da Decision 3, achadas por palavra-chave (PT: `Hooks`, `encadeado`, `adversarial`, `governança`, `sdd-loop-builder`, `Reconciliação`, `deltas`; EN: `Hooks`, `Chained`, `Adversarial`, `governance`, `sdd-loop-builder`, `reconciliation`, `deltas`); nenhum `20` seguido de 2 dígitos como palavra no arquivo |
| `Comparison` | por idioma: a linha que começa por `\| Specs as deltas` / `\| Specs como deltas`, **só na última célula** (a coluna do SDD Open; as outras colunas têm ✅ legítimo do OpenSpec): contém `em avaliação` / `under evaluation` e `❌`, e não contém `✅` |
| `ReadmeEAgents` | cada README: os 17 nomes, `kb-dominios.py`, `guia-do-aluno.md`, o roadmap do idioma, a frase fixa do OK e o link para o outro README; o `AGENTS.md.tmpl`: as 5 skills, `sdd/bin/kb-dominios.py`, `um OK só` e o marcador de vendors |
| `PorQueCadaRegra` | nas 9 skills: exatamente 1 título `## Por que cada regra existe`, com ou sem ` (não apague sem ler)`; ≥ 3 itens `- **…** —` até o próximo `## `; nas 7 de fase, o próximo `## ` é `## Encerramento (obrigatório)` |

A regra de âncora do GitHub fica numa função `ancora(titulo)`: tira crases, normaliza em NFC, passa a minúsculas, mantém só o caractere de categoria Unicode letra (L*), marca (M*, inclusive o seletor de variação do ⏸️), dígito decimal (Nd) ou conector (Pc), espaço e `-`, e troca espaço por `-`; repetição ganha `-1`, `-2`. Os 7 agentes, os nomes de skill e as frases fixas ficam em constantes no topo do módulo.

**Rationale:** checagem de conteúdo mínimo por âncora fixa prova que o documento cobre o que o DEFINE pede sem amarrar a redação; a checagem de links pega a classe de defeito que já existe hoje.

**Alternatives Rejected:**
1. Checar links externos com rede: rejeitada (BRAINSTORM, YAGNI; os testes rodam sem rede).
2. Pôr os docs novos na lista G5 do `publish-gate.sh`: rejeitada porque `scripts/` fica intocado e o link do README já prova a existência.
3. Fixar as versões novas das 7 skills no `test_docs.py`: rejeitada porque viraria mais um teste a mudar a cada bump; a versão é provada pelo `check-versions.log` e o `test_conversa` já confere linha de identificação = frontmatter.

**Consequences:** o teste falha com mensagem que nomeia o arquivo e a âncora ausente; mudar uma frase fixa exige mudar a constante de propósito.

### Decision 7: Correção P1 do `adaptation-guide.md`

| **Status** | Accepted | · | **Date** | 2026-10-29 |

**Context:** `docs/adaptation-guide.md:34` e `docs/pt-BR/adaptation-guide.md:36` linkam o placeholder do comando de landmines como se fosse arquivo (`../` + o placeholder), e dizem que ele "ships as a mechanism with three generic rules" / "vem como um mecanismo com três regras genéricas". O pacote não traz esse script: o slot `release.landmines_cmd` sai vazio em `sdd/config.example.yaml:35`.

**Choice:** a frase passa a dizer que o slot `release.landmines_cmd` do `sdd/config.yaml` (com link para `../sdd/config.example.yaml`, e `../../sdd/config.example.yaml` no PT) **sai vazio**, e que uma boa primeira versão do seu script tem as três regras genéricas citadas. O resto do texto ("That emptiness is deliberate…", o exemplo `crit`) fica como está, porque continua verdadeiro.

**Rationale:** P1: defeito achado é corrigido antes de construir por cima; a classe `Links` ficaria vermelha sem isso.

**Alternatives Rejected:**
1. Excluir os 2 arquivos da checagem de links: rejeitada porque esconderia um link quebrado e uma frase falsa.
2. Criar o script de landmines com as 3 regras: rejeitada porque é mecanismo novo, fora do escopo (os hooks são da F8).

**Consequences:** 2 frases mudam; nenhuma mudança de comportamento.

### Decision 8: Evidência, contratos intactos e sabotagem

| **Status** | Accepted | · | **Date** | 2026-10-29 |

**Context:** AT-011, AT-012 e AT-014 precisam de `.git` e da tag `v2.2.6`, que a cópia do gate não tem.

**Choice:** em `sdd/reports/evidence/F6_DOCS/`, fora do commit do produto:
- `comandos-intactos.py`: cópia do script da F5 com `SKILLS` = as 7 de fase, base `v2.2.6`, `EXCECOES` vazio e `limpa()` removendo também a seção `## Por que cada regra existe` até o próximo `## `. Além da extração (passos, itens numerados, comandos), uma 2ª prova mais forte: o texto inteiro normalizado de `v2.2.6` e de HEAD tem de ser **igual**. A normalização tira só a seção nova e troca a versão de `version: "…"` e de `sdd-<skill> vX.Y.Z` por um marcador; qualquer outra diferença (regra em prosa, título sem número, linha de bloco) reprova e é impressa com `difflib.unified_diff` (Pattern 3);
- `gerar-evidencia.sh`:
  - logs `check-versions`, `comandos-intactos`, `skill-lint-conversa`, `linhas`, `escopo`;
  - `contratos-intactos`: `git diff --stat v2.2.6 HEAD -- sdd/bin sdd/fixtures sdd/templates sdd/playbook.md sdd/config.example.yaml scripts bin .github` vazio, mais `playbook-lint.sh --self-test`;
  - `codepoints`: os code points fora de ASCII nas 7 seções novas;
  - `testes-f6`: os módulos tocados, verbosos;
  - `baseline`: a árvore `v2.2.6` por `git archive`, com o `tests/test_docs.py` novo copiado dentro, deve falhar;
- `sabotagem.sh`: 3 sabotagens, cada uma num clone temporário de HEAD (nunca na worktree), rodando só `tests/test_docs.py`:
  1. troca o alvo de um link do sumário do guia por uma âncora inexistente;
  2. apaga a seção da `sdd-build`;
  3. troca `em avaliação` por `✅` na linha de deltas do `docs/pt-BR/comparison.md`.
  
  Cada uma tem de sair diferente de 0 com o nome do teste, e o clone limpo tem de sair 0.

**Rationale:** clone temporário em vez de `git checkout` na worktree: não arrisca deixar sabotagem para trás nem tocar nos artefatos não rastreados de `sdd/`.

**Alternatives Rejected:**
1. Sabotar na worktree e reverter com `git checkout`: rejeitada pelo risco acima; o efeito provado é o mesmo (o clone limpo sai 0).

**Consequences:** os scripts dependem de `git`, `/usr/bin/python3` e `/bin/bash`; rodam só na máquina de quem constrói.

---

## File Manifest

| # | File | Action | Purpose | Agent | Dependencies |
|---|------|--------|---------|-------|--------------|
| 1 | `tests/test_docs.py` | Create | As 7 classes (Decision 6); escrito primeiro, para o baseline vermelho | (general) | None |
| 2 | `docs/adaptation-guide.md` | Modify | Correção P1: link e frase do slot de landmines (Decision 7) | (general) | 1 |
| 3 | `docs/pt-BR/adaptation-guide.md` | Modify | Idem, em PT (Decision 7) | (general) | 1 |
| 4 | `docs/roadmap.md` | Create | Roadmap EN (Decision 3) | (general) | 1 |
| 5 | `docs/pt-BR/roadmap.md` | Create | Roadmap PT (Decision 3) | (general) | 1 |
| 6 | `docs/comparison.md` | Modify | "on the roadmap here" vira link para `roadmap.md` (SHOULD) | (general) | 4 |
| 7 | `docs/pt-BR/comparison.md` | Modify | Idem, em PT | (general) | 5 |
| 8 | `docs/quickstart.md` | Modify | Regra, 4 validações, tabela "onde roda" (Decision 2) | (general) | 1 |
| 9 | `docs/pt-BR/quickstart.md` | Modify | Idem, em PT (Decision 2) | (general) | 1 |
| 10 | `docs/pt-BR/guia-do-aluno.md` | Create | Guia adaptado (Decision 1) | (general) | 5, 9 |
| 11 | `README.md` | Modify | As 17 skills, KB, OK único, links do guia e do roadmap (Decision 4) | (general) | 4, 10 |
| 12 | `README.pt-BR.md` | Modify | Idem, em PT (Decision 4) | (general) | 5, 10 |
| 13 | `AGENTS.md.tmpl` | Modify | Linhas Antes e KB, `kb-dominios.py`, "um OK só" (Decision 4) | (general) | None |
| 14 | `.agents/skills/sdd-brainstorm/SKILL.md` | Modify | 2.1.1; seção (Decision 5) | (general) | None |
| 15 | `.agents/skills/sdd-define/SKILL.md` | Modify | 2.3.1; seção (Decision 5) | (general) | None |
| 16 | `.agents/skills/sdd-governanca/SKILL.md` | Modify | 2.2.1; seção (Decision 5) | (general) | None |
| 17 | `.agents/skills/sdd-ux-review/SKILL.md` | Modify | 2.3.1; seção (Decision 5) | (general) | None |
| 18 | `.agents/skills/sdd-design/SKILL.md` | Modify | 2.1.1; seção (Decision 5) | (general) | None |
| 19 | `.agents/skills/sdd-build/SKILL.md` | Modify | 2.2.1; seção (Decision 5) | (general) | None |
| 20 | `.agents/skills/sdd-release/SKILL.md` | Modify | 2.3.1; seção (Decision 5) | (general) | None |
| 21 | `tests/test_contrato_build_release.py` | Modify | Versões fixadas: release 2.3.0 → 2.3.1, build 2.2.0 → 2.2.1 | (general) | 19, 20 |
| 22 | `tests/test_correcoes_w0.py` | Modify | Versão fixada da build 2.2.0 → 2.2.1 | (general) | 19 |
| 23 | `MANIFEST.txt` | Modify | 1, 4, 5 e 10, em ordem `LC_ALL=C` | (general) | 1, 4, 5, 10 |
| 24 | `sdd/reports/evidence/F6_DOCS/comandos-intactos.py` | Create | AT-011 (Decision 8); fora do commit do produto | (general) | 14, 15, 16, 17, 18, 19, 20 |
| 25 | `sdd/reports/evidence/F6_DOCS/gerar-evidencia.sh` | Create | Logs da Decision 8; fora do commit do produto | (general) | 23, 24 |
| 26 | `sdd/reports/evidence/F6_DOCS/sabotagem.sh` | Create | 3 sabotagens (AT-014); fora do commit do produto | (general) | 1, 10, 19, 7 |

**Total Files:** 26

---

## Landmines aplicáveis

Varredura rodada em 2026-10-29 (`playbook-lint.sh --grep` por `docs`, `README`, `AGENTS.md`, `MANIFEST`, `SKILL.md`, `versão`, `link`, `teste`: 0 hits por superfície); pela leitura do playbook, 3 se aplicam ao método.

| Landmine (⛔) | Fonte | Veredito | Como / Por quê |
|---------------|-------|----------|----------------|
| Gate que só confere fiação | `LM-001` | ✔ tratado | `test_docs.py` tem os dois lados: verde na árvore nova, vermelho no baseline `v2.2.6` e nas 3 sabotagens (manifest 26) |
| Asserção sem baseline vermelho | `LM-002` | ✔ tratado | Manifest 1 vem antes de tudo; `baseline.log` roda o teste novo na árvore `v2.2.6` |
| Review de "não commitado" revisando o vazio | `LM-003` | ✔ tratado | O build commita antes do gate e antes da revisão de contexto fresco; o brief cita o SHA |
| Migration provada por `exit 0` | `LM-004` | N.A. | Sem migration no manifest |

---

## Contrato de aceite

N.A. (1 camada): o manifest só toca Markdown, `AGENTS.md.tmpl`, texto de skill e testes, sem `api`/`ui`/`sql`. A revisão de contexto fresco do DESIGN e a do build continuam obrigatórias pela sessão.

---

## Agent Assignment Rationale

Agent Discovery: Not available. Tudo fica `(general)`, no modo default, na mesma conversa: o guia, os quickstarts e o README repetem os mesmos nomes e frases fixas, e um autor só os mantém iguais.

---

## Code Patterns

### Pattern 1: Âncora do GitHub e extração de links (`tests/test_docs.py`)

```python
CERCA = re.compile(r"^(```|~~~)")
LINK = re.compile(r"\]\(([^)\s]+)\)")
TITULO = re.compile(r"^#+\s+(.*?)\s*#*\s*$")


def ancora(titulo):
    t = unicodedata.normalize("NFC", titulo.replace("`", "").strip()).lower()
    fica = [c for c in t
            if c in " -" or unicodedata.category(c)[0] in "LM" or unicodedata.category(c) in ("Nd", "Pc")]
    return "".join(fica).replace(" ", "-")


def linhas_fora_de_cerca(path):
    dentro = False
    for n, ln in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if CERCA.match(ln.lstrip()):
            dentro = not dentro
            continue
        if not dentro:
            yield n, ln


def ancoras(path):
    vistas, saida = dict(), set()
    for _, ln in linhas_fora_de_cerca(path):
        m = TITULO.match(ln)
        if m:
            base = ancora(m.group(1))
            k = vistas.get(base, 0)
            vistas[base] = k + 1
            saida.add(base if k == 0 else base + "-" + str(k))
    return saida
```

### Pattern 2: Seção "Por que cada regra existe" (formato)

```markdown
## Por que cada regra existe

- **O critério de parada é o Verify Gate** — "parece pronto" muda com o cansaço de quem constrói; um
  comando com exit dá a mesma resposta para todo mundo, inclusive para a release, que roda o gate de novo.
- **Commit antes de qualquer revisão** — um revisor de "o que não foi commitado" olhando uma árvore já
  commitada revisa o vazio, e um review que passou sobre nada é pior que nenhum.

## Encerramento (obrigatório)
```

### Pattern 3: Seção limpa no `comandos-intactos.py`

```python
def limpa(texto):
    texto = re.sub(r"\n## Como falar com o aluno\n.*?(?=\n## )", "\n", texto, flags=re.S)
    texto = re.sub(r"\n## Por que cada regra existe[^\n]*\n.*?(?=\n## )", "\n", texto, flags=re.S)
    texto = re.sub(r"\nNa primeira resposta desta skill, comece com esta linha, uma vez só"
                   r"(?:, antes do Status)?:\n`[^`\n]+`\n", "\n", texto)
    return texto


def normaliza(texto):
    """Texto inteiro sem a seção nova e com as 2 versões trocadas por um marcador (2ª prova, M1)."""
    texto = re.sub(r"\n## Por que cada regra existe[^\n]*\n.*?(?=\n## )", "\n", texto, flags=re.S)
    texto = re.sub(r'(?m)^(  version: )"[0-9.]+"$', r'\1"VERSAO"', texto)
    return re.sub(r"(`sdd-[a-z-]+ v)[0-9.]+( ·)", r"\1VERSAO\2", texto)
```

---

## Data Flow

1. O build escreve `tests/test_docs.py` e roda-o: vermelho (docs novos ausentes, 2 links quebrados, seção ausente em 7 skills).
2. Corrige o `adaptation-guide.md` (EN, PT); a classe `Links` deixa de acusar esses 2.
3. Escreve roadmaps, quickstarts, comparison, guia, READMEs, `AGENTS.md.tmpl` e as 7 seções com os bumps; a cada arquivo, roda a classe correspondente.
4. Atualiza os 2 testes de versão e o `MANIFEST.txt`; roda a suíte inteira no piso.
5. Commit na branch; Verify Gate `--strict` (cópia por `git archive` → publish-gate ci → suíte); `gerar-evidencia.sh` e `sabotagem.sh`.
6. Revisão de contexto fresco do build sobre o SHA; ciclo 2 se NEEDS_WORK.
7. PR: CI ubuntu + macOS; abrir o sumário do guia na página do PR (A-002) e registrar em `links-pr.log`.
8. Bloco do OK; OK do Roberto citando "sdd-open"; push fast-forward; Release `v2.2.7` conferida pelo hash.

Caminho de erro: link ou âncora quebrados → a classe `Links` nomeia `arquivo:linha → alvo`; o build corrige o doc, não o teste. Frase fixa ausente → a classe nomeia a frase e o arquivo.

---

## Integration Points

| Sistema | Tipo | Direção | Falha |
|---|---|---|---|
| GitHub Actions (`publish-gate.yml`, job `testes-macos`) | CI no PR e em `main` | saída | vermelho ⇒ corrigir antes do OK; nenhum push |
| GitHub Releases (`release.yml`) | publicação no push de `main` | saída | run sem `testes` e `testes-macos` verdes não publica; `SHA256SUMS.txt` ausente ⇒ registrar e investigar, sem novo push às cegas |
| Página do PR (renderização do Markdown) | conferência humana das âncoras | leitura | âncora que não abre ⇒ ajustar `ancora()` e o título, e registrar como achado de A-002 |

Nenhuma integração em tempo de execução: o produto desta frente é texto.

---

## Testing Strategy

| Tipo | Escopo | Ferramenta | Meta |
|---|---|---|---|
| Unit (conteúdo) | AT-001 a AT-007, AT-009, AT-010 (seção e posição) | `tests/test_docs.py` | verde em HEAD; vermelho em `v2.2.6` (baseline) |
| Unit (links) | AT-008 | `tests/test_docs.py::Links` | 0 links quebrados; baseline vermelho real (os 2 do `adaptation-guide.md`) |
| Regressão | AT-013 | suíte inteira no piso (`SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B`) | > 499 testes, 0 falha; `test_conversa` 17/17; `test_agnostico` verde |
| Contrato | AT-010 (versão), AT-012 | `check-versions.py --base v2.2.6 --base-obrigatoria` | exit 0; log com as 7 versões novas |
| Contrato | AT-011 | `comandos-intactos.py` (7 skills, exceções vazias) | exit 0 |
| Contrato | AT-013 (byte a byte) | `git diff --stat v2.2.6 HEAD` nos caminhos intocados | saída vazia |
| Mutação | AT-014 | `sabotagem.sh` (3) | 3 vermelhos nomeados; clone limpo verde |
| Gate | todos os de `cmd` | `verify-gate.sh --strict sdd/features/DEFINE_F6_DOCS.md` | exit 0 |
| Humano | A-002 | sumário do guia aberto no PR | 10 âncoras abrem |

---

## Error Handling

| Erro | Tratamento |
|---|---|
| Arquivo de doc ilegível ou não UTF-8 | o teste falha nomeando o arquivo (leitura direta com `encoding="utf-8"`; o erro aparece com o caminho) |
| Link para pasta (sem arquivo) | existe = passa; o GitHub abre a listagem |
| Âncora para arquivo que não é `.md` | só a existência do arquivo é conferida |
| Título com crase, acento ou pontuação | `ancora()` (Pattern 1); divergência com o GitHub é risco aceito e conferido no PR |
| Literal de dado pessoal num doc | G2 do publish-gate dentro do Verify Gate reprova; o build troca o exemplo |
| Skill acima de 500 linhas | `skill-lint` avisa e `test_skill_lint` reprova; o build encurta os itens |
| Bump esquecido | `check-versions` reprova; `test_contrato_build_release` reprova a versão velha |

---

## Configuration

Nenhum slot novo em `sdd/config.yaml`. Constantes do `tests/test_docs.py` no topo do módulo: os 7 agentes, as 4 skills de preparo, as frases fixas (Decisions 2, 4) e as palavras-chave do roadmap (Decision 6). `MANIFEST.txt` recebe 4 linhas.

---

## Security Considerations

- **Dado pessoal nos docs:** o guia do starter usa exemplos fictícios; o G2 do publish-gate roda sobre a árvore inteira dentro do gate.
- **Integridade das skills:** as 7 seções passam pela varredura "Skill integrity" do CI (Unicode invisível, `curl … | sh`); `codepoints.log` confere antes do push.
- **Agnosticismo (P2):** `test_agnostico` cobre as 7 seções e o `AGENTS.md.tmpl`; os docs tratam os 7 agentes por igual.
- **Nada de credencial, URL privada ou caminho de home:** o guia cita só `github.com/robertodiasduarte/sdd-open` e `example.com`.

---

## Observability

- Cada falha do `test_docs.py` diz arquivo, linha e o que falta.
- `sdd/reports/evidence/F6_DOCS/*.log`: 1ª linha é o comando, depois a saída, com `exit=` no fim.
- Release: run `release` com `testes` e `testes-macos` antes do `Publicar release`; `SHA256SUMS.txt` conferido com `shasum -a 256 -c`.

---

## Requirements Traceability

| Requirement / AT | Design Element | Test / Gate |
|---|---|---|
| MUST guia / AT-001, AT-002 | Decision 1; manifest 10 | `test_docs.Guia`, `Links` |
| MUST quickstarts / AT-003 | Decision 2; manifest 8, 9 | `test_docs.Quickstart` |
| MUST roadmap / AT-004 | Decision 3; manifest 4, 5 | `test_docs.Roadmap` |
| Não regressão comparison / AT-005 | Decision 3; manifest 6, 7 | `test_docs.Comparison` |
| MUST README / AT-006 | Decision 4; manifest 11, 12 | `test_docs.ReadmeEAgents` |
| MUST `AGENTS.md.tmpl` / AT-007 | Decision 4; manifest 13 | `test_docs.ReadmeEAgents`, `test_agnostico` |
| MUST links / AT-008 | Decisions 6, 7; manifest 1, 2, 3 | `test_docs.Links` |
| MUST seções / AT-009, AT-010 | Decision 5; manifest 14–20 | `test_docs.PorQueCadaRegra`, `test_conversa`, `check-versions.log` |
| MUST passos intactos / AT-011 | Decisions 5, 8; manifest 24 | `comandos-intactos.log` |
| MUST versões / AT-012 | Decision 5; manifest 21, 22 | `check-versions.log`, `test_contrato_build_release`, `test_correcoes_w0` |
| MUST não regressão / AT-013 | Decision 8; manifest 23 | Verify Gate, `contratos-intactos.log`, `linhas.log` |
| MUST sabotagem / AT-014 | Decision 8; manifest 26 | `sabotagem.log` |
| SHOULD link no comparison | manifest 6, 7 | `test_docs.Links` |

---

## Risks and Mitigations

| Risk | Impact | Mitigation | Residual Risk |
|---|---|---|---|
| A regra de âncora do teste diverge do GitHub (acento, pontuação) | Sumário passa no teste e não abre | Conferir as 10 âncoras na página do PR (A-002) | Baixo |
| Item de "Por que" descreve regra que a skill não tem | O motivo vira regra nova escondida | Cada item cita uma regra do texto atual (tabela da Decision 5); revisão de contexto fresco confere | Baixo |
| A seção nova quebra o `comandos-intactos` ou o bloco do OK | AT-011 ou `test_contrato_build_release` vermelhos | Seção sem bloco cercado e sem rótulos do bloco do OK; `limpa()` a remove | Nenhum |
| Guia com afirmação errada sobre comportamento de skill | Aluno espera o que não acontece | Fatos conferidos no texto das skills (Decision 1); revisão de contexto fresco lê guia × skills | Médio, aceito (texto velho com o tempo) |
| Literal de PII copiado do starter | G2 vermelho | Gate roda o publish-gate | Nenhum |
| O `sync --check` acusa o bloco do `AGENTS.md` antigo | Usuário vê "DIVERGENTE" depois de atualizar | Comportamento esperado de toda mudança no template; o quickstart já manda rodar `sync` | Aceito |

---

## Advisor Ledger

Revisão de contexto fresco do DESIGN v1.0 (modo contrato, pedida pelo Roberto), gravada em `sdd/reviews/REVISAO_DESIGN_F6_DOCS_20261029.md`, com as sondas em `evidence/F6_DOCS/AVAL-DESIGN-*.log`. Veredito: NEEDS_WORK (3 HIGH, 4 MEDIUM, 3 LOW). Os 3 HIGH reproduzidos antes de aplicar (H2: `bin/sdd-open.sh:603-610` e o log do revisor; H3: `sdd-release/SKILL.md`, FASE 1 itens 5–7 e FASE 2 item 8).

| Nota | Decisão | Onde |
|---|---|---|
| H1 `✅` legítimo do OpenSpec na linha de deltas | APPLIED: só a última célula | Decision 6; DEFINE AT-005 |
| H2 `git pull` + `sync` não atualiza skill | APPLIED: caminho `doctor` → apagar → `init --yes` → `sync` no guia; correção P1 do passo 5 dos 2 quickstarts; o teste confere `doctor` e `init` | Decisions 1, 2, 6; DEFINE Goals, AT-001, AT-003 |
| H3 regra do starter que o open não tem; ledger ausente | APPLIED (inclusive a menor da ux-review) | Decision 5 |
| M1 `comandos-intactos` cego a prosa | APPLIED: 2ª prova por igualdade do texto normalizado | Decision 8; Pattern 3; DEFINE AT-011 |
| M2 7 agentes conferidos fora do passo 4 seria circular | APPLIED: trecho `## 4.`…`## 5.` | Decision 6; DEFINE AT-003 |
| M3 python3, bash, `--yes`, `git init -b main` | APPLIED | Decision 1; DEFINE Goal do guia |
| M4 regra do `AGENTS.md.tmpl` | APPLIED pela regra 7 (o DEFINE já pedia regra; nenhuma iteração do DEFINE) | Decision 4 |
| L1 âncora com marca Unicode | APPLIED: categorias L*, M*, Nd, Pc e NFC | Decision 6; Pattern 1 |
| L2 literal proibido largo; palavra-chave fora da tabela | APPLIED | Decision 6 |
| L3 cobertura do gate; `PROMESSA_VAZIA`; branch `docs/` | APPLIED | Decision 1; DEFINE Verify Gate e Constraints |

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.1 | 2026-10-29 | SDD Design by RDD | Revisão de contexto fresco (Advisor Ledger): 10 notas aplicadas; DEFINE v1.1. Achado novo de P1: o passo 5 dos 2 quickstarts ensina uma atualização que não atualiza (Decision 2) |
| 1.0 | 2026-10-29 | SDD Design by RDD | Versão inicial. Achados do design: 2 links quebrados e uma frase falsa no `adaptation-guide.md` (Decision 7, P1); 3 testes que fixam versão (manifest 21, 22) |

---

## Next Step

Execute o **SDD Build by RDD**.
