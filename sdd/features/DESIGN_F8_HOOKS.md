# DESIGN: F8 Hooks de git

> Um dispatcher em bash 3.2 (`sdd/hooks/pre-commit`) com as regras como funções, rodando todas e juntando os achados numa só recusa; um `pre-push` de aviso; o `init` copia `sdd/hooks/` como copia `sdd/bin/`, mostra a linha do `core.hooksPath` no plano e liga sob a confirmação única, sem nunca desligar um alarme alheio; a `sdd-higiene-dado` ganha o modo "ligado pelos hooks do projeto" (`git config sdd.higieneDado`); e o `init --vendors claude` gera, de `bin/adapters/claude/`, dois guards Python em `.claude/hooks/` e duas entradas no `.claude/settings.json`, com o mesmo merge seguro do Gemini.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | F8_HOOKS |
| **Date** | 2026-10-30 |
| **Author** | SDD Design by RDD (sessão com Roberto Dias Duarte) |
| **BRAINSTORM** | `sdd/features/BRAINSTORM_F8_HOOKS.md` |
| **DEFINE** | `sdd/features/DEFINE_F8_HOOKS.md` (v1.2) |
| **UX REVIEW** | `sdd/reviews/UX_REVIEW_F8_HOOKS.md` (9 MUST de texto de saída, U1–U9) |
| **LLM Prompts** | false |
| **Status** | Ready for Build |

Re-check do flag LLM Prompts (`false`): nenhum provedor ou modelo citado; a palavra "prompt" aparece só como campo do payload do hook do vendor (`tool_input.prompt`) em `bin/adapters/claude/`, não como texto enviado a um LLM. Zero hits relevantes.

---

## Architecture Overview

```text
 pacote sdd-open                                projeto do usuário (depois do init)
 ─────────────────────────                      ────────────────────────────────────────────────
 bin/sdd-open.sh init ──copia──────────────────► sdd/hooks/pre-commit   sdd/hooks/pre-push
   │  plano: "+ core.hooksPath = sdd/hooks …"      │ (dispatcher, bash 3.2)   │ (aviso, exit 0)
   │  estado: LIVRE | LIGADO | HIGIENE | OUTRO      │                          │
   │  git config core.hooksPath sdd/hooks ─────────┤                          │
   │  git config sdd.higieneDado on (migração) ────┤                          │
   │                                               ▼                          ▼
   │                                   git commit ──► H6 H2 H5 H3 H4 REPORT HIGIENE    git push ──► atrás de origin/<default>?
   │                                               │  lê sdd/config.yaml (project.*)
   │                                               │  chama sdd/bin/playbook-lint.sh --anti-collapse
   │                                               │  chama python3 sdd/bin/report-lint.py --stdin
   │                                               │  chama .agents/skills/sdd-higiene-dado/scripts/pre-commit.sh
   │                                               ▼
   │                                   🛑 [Hn] … · RESULTADO: COMMIT RECUSADO · → por classe   (ou silêncio)
   │
   ├─ doctor ──► ✅ hooks ligados (…) | ⚠️ por causa, com o comando
   │
   └─ --vendors claude ──render (sdd-open:generated)──► .claude/hooks/sdd-report-guard.py
        bin/adapters/claude/*.py                        .claude/hooks/sdd-avaliador-guard.py
        merge_claude_settings ────────────────────────► .claude/settings.json (2 entradas em hooks.PreToolUse)
                                                           │ Write/Edit de BUILD_REPORT_*.md ─► report-lint.py --stdin ─► deny | silêncio | ⚠️
                                                           │ despacho com "veredito" no prompt ─► avaliador-guard.sh ─► deny | silêncio | ⚠️

 .agents/skills/sdd-higiene-dado/scripts/alarme.sh
   sem hooksPath ────────────► .git/hooks/pre-commit (como hoje)
   hooksPath = sdd/hooks + marca do dispatcher ─► git config sdd.higieneDado on|off
   outro hooksPath / pre-commit alheio ──────────► recusa (exit 2), como hoje
```

---

## Components

| Componente | Responsabilidade | Arquivos |
|---|---|---|
| Dispatcher pre-commit | 5 regras + `report-lint` do staged + alarme da higiene; uma recusa só | `sdd/hooks/pre-commit` |
| Aviso pre-push | base velha em relação a `origin/<default_branch>` | `sdd/hooks/pre-push` |
| Instalador | copiar `sdd/hooks/`, estado dos hooks, linha do plano, `core.hooksPath`, migração da higiene, `doctor` | `bin/sdd-open.sh`, `bin/lib/vendors.sh` |
| Adaptador do Claude Code | render dos 2 guards e merge do `settings.json` | `bin/sdd-open.sh`, `bin/lib/merge.sh`, `bin/adapters/claude/*.py` |
| Higiene em modo hooks | `alarme.sh` reconhece o dispatcher; `instalar`/`desinstalar` viram config | `.agents/skills/sdd-higiene-dado/**` |
| Config | slot `project.context_file_max_kb` | `sdd/config.example.yaml` |
| Prova | fixtures, testes, evidência, sabotagem | `sdd/fixtures/hooks/`, `tests/` |
| Docs | `docs/hooks.md` + PT, roadmap, READMEs, guia, convenções | `docs/**`, `README*.md` |

---

## Key Decisions

### Decision 1: Um dispatcher em bash, regras como funções, todas rodam, uma recusa só

| **Status** | Accepted | · | **Date** | 2026-10-30 |

**Context:** o privado tem 6 guardas num `sh` de 154 linhas, cada uma saindo no primeiro erro com cor ANSI. O open fala com `🛑/⚠️/✅` + palavra, termina em `RESULTADO:` + `→`, e o aluno já conhece o molde do alarme da higiene (achados → por que → como corrigir → `--no-verify` por último).

**Choice:** `sdd/hooks/pre-commit` é bash 3.2, `set -u`, com a linha 2 fixa `# sdd-open: dispatcher de hooks (pre-commit)` (a marca que o `alarme.sh` procura). Lê a lista staged uma vez (`git diff --cached --name-only -z --diff-filter=ACMR`, em arquivo temporário, laço `read -r -d ''`) e o `sdd/config.yaml` (`project.default_branch`, `project.context_file_max_kb`) por `sed`, como o `report-lint.py` lê o seu slot. Roda, nesta ordem, H6 → H2 → H5 → H3 → H4 → REPORT → HIGIENE, cada regra numa função que acrescenta linhas a 3 acumuladores de texto (ACHADOS, CLASSES, AVISOS). No fim, se há achado: imprime em stderr o cabeçalho `sdd-open: commit recusado. Encontrei o que não pode entrar nesta versão:`, as linhas `🛑 [Hn] <arquivo>: <motivo>`, um bloco "Por que importa" com 1 frase por classe presente, a saída da higiene (se recusou), `RESULTADO: COMMIT RECUSADO`, um `→ [Hn] <como corrigir, com comando>` por classe e, por último, `→ se você conferiu e quer gravar mesmo assim, só desta vez: git commit --no-verify` seguido de `Agente de IA: não use --no-verify sem o OK explícito da pessoa.`; exit 1. Sem achado: só os ⚠️ acumulados (regra pulada), exit 0. Sem cor.

**Rationale:** o aluno vê tudo num ciclo; a saída segue `docs/cli-conventions.md` e o molde que a higiene já ensinou; um arquivo com funções é o que o `test_bash32.py` e o `grep` de bashismo cobrem.

**Alternatives Rejected:** 1. Um arquivo por regra em `pre-commit.d/` — 7 arquivos, e "apagado de propósito" vira indistinguível de "instalação incompleta" para o `doctor`. 2. Parar na primeira regra — menos saída, mais tentativas de commit. 3. Hook em Python — todo commit passaria a depender de `python3`.

**Consequences:** ~200 linhas num arquivo; desligar uma regra é editar o hook (território do usuário). Ganhamos uma recusa só, legível em texto puro, e a marca que faz a D10 funcionar.

### Decision 2: Regras H2, H3, H5 e H6 no próprio hook; H4 e REPORT delegam; toda dependência ausente avisa e segue

| **Status** | Accepted | · | **Date** | 2026-10-30 |

**Context:** H4 e REPORT já têm script no open (`playbook-lint.sh --anti-collapse`, `report-lint.py --stdin`); H2, H3, H5 e H6 são leitura do índice e do config. O hook roda no projeto do usuário, onde `bin/lib/vendors.sh` do pacote **não** existe.

**Choice:**
- **H6**: `branch=$(git symbolic-ref --quiet --short HEAD)`; recusa só se `branch` = `project.default_branch` (default `main`) **e** `git rev-parse --verify --quiet refs/remotes/origin/<branch>` existe. HEAD destacado ou sem o ref passa. O `→ [H6]` dá primeiro o comando que leva o que está preparado para uma branch nova (`git switch -c <nome>`: o staged vai junto, medido pela revisão) e só depois "para a próxima feature, peça a `sdd-new-session`" (nota M5); `--no-verify` fica para a última linha comum. `git cherry-pick` não roda o pre-commit (medido): o passo 5 da `sdd-release` não é barrado.
- **H2**: a lista de arquivos de contexto fica **dentro do hook** (`AGENTS.md CLAUDE.md GEMINI.md .cursorrules`, casada por basename em qualquer profundidade) **e** em `bin/lib/vendors.sh` (`vendor_arquivo_contexto` por vendor e a união `VENDOR_ARQUIVOS_CONTEXTO`); `tests/test_hooks.py` confere que as duas listas são iguais (mesma técnica do teste que compara o hook da higiene com a fonte). Tamanho por `git cat-file -s ":<f>"` (o blob staged); teto = slot inteiro > 0, senão 100.
- **H5**: extensões de texto da fonte do privado (`js mjs cjs ts tsx jsx php sh zsh bash md py sql json css scss html htm yaml yml toml txt csv xml svg ini cfg conf env jsonl mdx`) mais arquivo sem extensão cujo blob começa por `#!`; NUL detectado por `git cat-file blob ":<f>" | LC_ALL=C tr -d '\000' | wc -c` ≠ `git cat-file -s ":<f>"` (sem `grep -P`, que o BSD grep não tem). Binários conhecidos nunca entram. Blob que começa por BOM UTF-16 (`FF FE` ou `FE FF`: `.txt` do PowerShell, `.csv` exportado do Excel) é texto legítimo com NUL e **não** é achado: a regra o pula (nota L2 da revisão).
- **H3**: regex da fonte do privado (prefixo opcional `api|access|auth|db|ftp|smtp|client|private` + `password|passwd|senha|secret|token|key|api_key|access_key`, token completo, valor entre aspas com 6+ caracteres), aplicado com `git show ":<f>" | LC_ALL=C grep -Eio` (nunca `[[ =~ ]]`, cujos intervalos dependem da libc no bash 3.2; nota L3); placeholders (`${`, `{{`, `<`, `changeme`, `example`, `xxx`, `***`, sem distinguir caixa) passam; a mensagem traz só a chave. Depois, se `command -v gitleaks`: `gitleaks protect --staged -v --redact --no-banner 2>&1`; exit 1 → achado `[H3] gitleaks: …` com as linhas `File:`/`RuleID:` (ou `leaks found: N` quando não houver detalhe; nota L1); exit 0 → nada; outro exit → ⚠️ e segue.
- **H4**: `git diff --cached --name-status -z` com `D` ou `R*` em `sdd/playbook.md` → achado; `M` → grava HEAD e staged em temporários e chama `bash sdd/bin/playbook-lint.sh --anti-collapse`; exit 1 → achado com as linhas do lint; lint ausente → ⚠️ e segue. Playbook novo (`A`) passa.
- **REPORT**: para cada staged com basename `BUILD_REPORT_*.md` **cujo caminho não tem o componente `sdd/fixtures/` nem `sdd/templates/`** (as fixtures de `sdd/fixtures/evidencia/` reprovam de propósito e o `BUILD_REPORT_TEMPLATE.md` é um molde; os dois são copiados pelo `init`, e sem esta exceção o commit da própria instalação seria recusado — nota H1 e drift 1 do build): `git show ":<f>" | python3 -B sdd/bin/report-lint.py --stdin "<f>"`; exit 1 → achado `[REPORT] <f>` com as linhas `🛑` do lint; exit 0 → nada; `python3` ou o lint ausentes, ou exit ≥ 64 → ⚠️ nomeando a regra pulada. O lint confere evidência e `AVALIACAO` **no disco** (não no índice): relatório staged com logs ainda não adicionados passa no hook e é a release que confere (documentado em `docs/hooks.md`; nota L8).
- **HIGIENE**: `git config --get sdd.higieneDado` = `on` → `bash .agents/skills/sdd-higiene-dado/scripts/pre-commit.sh`, saída capturada; exit ≠ 0 → entra na recusa (a mensagem da higiene é autossuficiente e mascara o número); script ausente → ⚠️.

**Rationale:** só bash e git são obrigatórios para commitar; tudo que depende de `python3` ou de um script de `sdd/bin/` falha aberto **com aviso**, nunca em silêncio (regra 5 do PORTE vale para o `report-lint` da release, que é a verdade final).

**Alternatives Rejected:** 1. Gerar o hook pelo `init` com a lista do `vendors.sh` — o hook viraria arquivo gerado, e `sdd/` é território do usuário. 2. H6 sempre — bloquearia o commit do próprio `init` e o 1º commit da `sdd-iniciar-repo`. 3. `grep -P '\x00'` — não existe no macOS.

**Consequences:** uma lista duplicada com teste de sincronia; H6 não protege um repositório sem remoto (não há produção a proteger). Ganhamos um hook que roda igual nos 7 agentes e em bash 3.2.

### Decision 3: `init` trata `sdd/hooks/` como `sdd/bin/`, decide pelo estado dos hooks e nunca desliga alarme alheio

| **Status** | Accepted | · | **Date** | 2026-10-30 |

**Context:** `sdd_faltantes()` já lista o que falta em `sdd/` (templates, bin, playbook); o `init` completa sem sobrescrever e pede uma confirmação só; `core.hooksPath` desliga `.git/hooks/` inteiro.

**Choice:**
- `sdd_faltantes` passa a incluir `hooks`; `aplicar` cria `sdd/hooks/` e, depois da cópia, dá `chmod +x` em `sdd/hooks/pre-commit` e `pre-push` (sempre que existirem: a cópia por `cp` preserva o bit, mas um checkout em Windows pode perdê-lo).
- Função `hooks_estado` (em `sdd-open.sh`): `LIGADO` se `core.hooksPath` = `sdd/hooks` ou = `<raiz>/sdd/hooks` (o mesmo critério do `alarme.sh`; nota L7); `OUTRO <descrição>` se há outro `hooksPath` ou um `pre-commit` legado sem a marca `# sdd-higiene-dado: alarme de commit (pre-commit)`; `HIGIENE` se esse arquivo tem a marca; `LIVRE` nos demais casos. O arquivo legado é **sempre** `$(git rev-parse --git-common-dir)/hooks/pre-commit`, nunca `--git-path hooks/pre-commit`, que segue o `core.hooksPath` e apontaria para o próprio dispatcher (medido pela revisão; nota H3).
- `planejar` (só `init`): `LIGADO` → `plano_estado "core.hooksPath = sdd/hooks" emdia`; `LIVRE`/`HIGIENE` → `plano_estado "core.hooksPath = sdd/hooks — 5 regras passam a conferir cada commit (teto do arquivo de contexto, credencial, playbook, byte NUL, branch padrão); git commit --no-verify pula uma vez" novo`; `OUTRO` → `warn "hooks do open não ligados: já existe <descrição>. Nada foi alterado nele."` seguido de `warn "para ter as 5 regras, acrescente a ele a linha: bash sdd/hooks/pre-commit || exit 1"` (antes da confirmação, para o aluno decidir sabendo).
- `aplicar` (só `init`): `LIVRE`/`HIGIENE` → `git config core.hooksPath sdd/hooks`; `HIGIENE` → também `git config sdd.higieneDado on` e `warn "alarme da sdd-higiene-dado migrado: continua ligado, agora pelos hooks do projeto (sdd/hooks). Para desligar: bash .agents/skills/sdd-higiene-dado/scripts/alarme.sh desinstalar"`; o arquivo antigo fica (inerte). `OUTRO`/`LIGADO` → nada.
- Linha final do `init`: quando os hooks ficaram ligados **e** HEAD está em `project.default_branch` com `refs/remotes/origin/<branch>` presente, o `→` do `RESULTADO: INSTALADO` diz como commitar a instalação sem cair na H6: `leve a instalação para uma branch nova antes de commitar: git switch -c sdd-open-init` (nota M5). Sem remoto, ou fora da branch padrão, a linha de sempre.
- `doctor`: uma linha. `✅ hooks ligados (sdd/hooks: pre-commit com 5 regras + relatório + alarme da higiene <on|off>, pre-push)` quando `LIGADO` e os 2 arquivos têm `-x`; senão um `⚠️` por causa: `hooksPath` ausente → `rode init`; `OUTRO` → a linha para acrescentar; arquivo ausente → `rode init`; sem `-x` → `chmod +x sdd/hooks/<nome>`.
- `--dry-run` e `CANCELADO` continuam sem escrever nada (o `git config` fica em `aplicar`).
- Desligar (`git config --unset core.hooksPath`) **não é pegajoso**: o próximo `init` vê `LIVRE`, mostra a linha no plano e, com `--yes`, religa. `docs/hooks.md` diz isso com todas as letras (nota L6; um estado "desligado de propósito" é corte YAGNI consciente).

**Rationale:** um OK só (regra 7 do `AGENTS.md.tmpl`); o aluno lê o efeito na linha do plano (UX U1); nenhum alarme alheio é desligado (UX U5); a migração diz que a proteção continua (UX U6).

**Alternatives Rejected:** 1. Segunda pergunta só para os hooks — quebra "um OK só". 2. Migrar husky/lefthook — decisão do dono do projeto. 3. Apagar o `.git/hooks/pre-commit` da higiene na migração — apagar arquivo do usuário não é papel do `init`; o `desinstalar` da higiene faz isso.

**Consequences:** o ⚠️ de `OUTRO` aparece no plano e de novo no `doctor` (dois lugares, mesmo texto); aceito, porque o `doctor` é um relatório por si. Ganhamos `init` idempotente (`=` para o que já está ligado) e nenhuma proteção perdida em silêncio.

### Decision 4: `sdd-higiene-dado` 1.2.0 — modo "hooks do projeto" por `git config sdd.higieneDado` e pela marca do dispatcher

| **Status** | Accepted | · | **Date** | 2026-10-30 |

**Context:** o `alarme.sh` 1.1.1 recusa qualquer `core.hooksPath` (estado OUTRO); com a D3, todo projeto com o open passa a ter um.

**Choice:**
- `alarme.sh` calcula `MODO`: `hooks` quando `core.hooksPath` é `sdd/hooks` (ou o mesmo caminho absoluto sob a raiz) **e** `sdd/hooks/pre-commit` contém a marca do dispatcher; `arquivo` quando não há `hooksPath` (comportamento 1.1.1 intacto); `OUTRO` nos demais casos (exit 2, como hoje, com a linha para acrescentar à mão). O arquivo legado é `$(git rev-parse --git-common-dir)/hooks/pre-commit` (não `--git-path`, que seguiria o `hooksPath` até o dispatcher; nota H3). No modo arquivo esse caminho é o mesmo de hoje.
- Em `MODO=hooks`: `verificar` diz "o alarme roda pelos hooks do projeto (`sdd/hooks`) e está ligado/desligado (versão <v> da skill)"; `instalar` faz `git config sdd.higieneDado on` e diz "liguei o alarme nos hooks do projeto; nada foi gravado em `.git/`"; `desinstalar` faz `git config --unset sdd.higieneDado` e remove o arquivo legado **se e só se** ele tem a marca da higiene (resto da migração); `sdd/hooks/pre-commit` nunca é tocado (o teste afirma que ele continua existindo). Exits 0/1/2 iguais.
- `pre-commit.sh` (o alarme em si): detecções e exits **não mudam**; a única mensagem que muda é a última linha: "Para desinstalar o alarme: rm <HOOK>" só no modo arquivo (`HOOK` passa a vir de `--git-common-dir`, o mesmo caminho de hoje sem `hooksPath`); com `core.hooksPath` definido ela passa a ser "Para desinstalar o alarme: bash .agents/skills/sdd-higiene-dado/scripts/alarme.sh desinstalar", sem `rm` (AT-014 afirma o texto). Os 28 testes de `TestDeteccao`, `TestInstalacao` e `TestGeradores` rodam sem `hooksPath` e não veem a diferença.
- `tests/test_alarme.py::TestCopiaGerada` **muda necessariamente** (nota H2): ele roda `init --vendors claude`, que agora liga os hooks, e exigia um `.git/hooks/pre-commit`. Passa a afirmar o modo hooks: `sdd.higieneDado` = `on` depois do `instalar` pela cópia gerada, nada gravado em `.git/hooks/`, e o `verificar` da cópia dizendo que o alarme roda por `sdd/hooks`; o `git diff v2.2.8 -- tests/test_alarme.py` toca só essa classe.
- Versão 1.1.1 → 1.2.0 em `SKILL.md` (frontmatter e linha de identificação), `manifest.json`, `evals/cases.json`, `CHANGELOG.md`; `SKILL.md` ganha o modo nos passos 1–3 e 5 ("grava um arquivo em `.git/hooks` ou liga nos hooks do projeto, conforme o projeto já usa o sdd-open") e a seção "Scripts determinísticos"; `references/COMO_FUNCIONA.md` e `RUNTIME_COMPATIBILITY.md` ganham o segundo lugar. `ESCOPO_CONFIRMADO.md` (escopo aprovado da 1.0) não muda. A seção "Como falar com o aluno" e a camada de conversa não mudam.

**Rationale:** usa a cópia versionada da skill (não envelhece como `.git/hooks`); a proteção nunca some; qualquer `hooksPath` que não seja o nosso continua recusado.

**Alternatives Rejected:** 1. Encadear qualquer `.git/hooks/pre-commit` — código fora do git a cada commit. 2. Não mexer na higiene — quem tem o alarme perde ao rodar o `init`.

**Consequences:** bump minor; casos novos em `tests/test_alarme.py` (classe nova para o modo hooks) e a `TestCopiaGerada` reescrita; os outros 28 intactos. Ganhamos um alarme que convive com o dispatcher.

### Decision 5: Adaptador do Claude Code — fonte em `bin/adapters/claude/`, render com cabeçalho, merge de 2 entradas no `settings.json`

| **Status** | Accepted | · | **Date** | 2026-10-30 |

**Context:** P2 exige que o nome da ferramenta do vendor more só no que o `init` gera; `renderizar_gerado` já escreve cópias marcadas a partir de `.agents/skills/<skill>/<rel>`; `merge_gemini_settings` já edita JSON do usuário sem perder chave.

**Choice:**
- `renderizar_gerado` ganha um 4º parâmetro opcional, o prefixo da fonte (default `.agents/skills`), e `gerado_em_dia`/`escrever_gerado` o repassam; os adaptadores são renderizados com prefixo `bin/adapters` e skill `claude`. O cabeçalho sai `fonte: bin/adapters/claude/<f> (pacote sdd-open)`, porque esse caminho existe só no pacote, não no projeto; a mensagem do `--check` para cópia que não compila usa o prefixo real em vez de `.agents/skills/%s/%s` fixo (nota L4).
- `vendor_alvos claude` passa a listar também `.claude/hooks` e `.claude/settings.json`; `destinos_checar` confere permissão neles; `planejar`/`aplicar`/`--check` tratam `.claude/hooks/*` como tratam `.claude/skills/*` (`+`/`~`/`=`, "desatualizado: rode sync", verificador `python`). O vendor `claude` passa a exigir `python3` (como o Gemini já exige): a pré-condição é checada em `planejar`, antes de qualquer escrita, com `die` 64 e "nada foi alterado"; `docs/hooks.md` registra a mudança em relação à `v2.2.8` (nota L5).
- `merge_claude_settings <dest>` em `merge.sh`, nos moldes do Gemini: `python3 -I` lê o arquivo (vazio ou ausente vale objeto vazio), exige objeto no topo (senão `JSONERR` → exit 66 sem escrever), pega `hooks` → `PreToolUse` (lista), e acrescenta as 2 entradas do open quando nenhuma entrada existente tem um comando que cite `.claude/hooks/sdd-report-guard.py` (resp. `sdd-avaliador-guard.py`): a 1ª com matcher `Write|Edit|MultiEdit` e comando `python3 "$CLAUDE_PROJECT_DIR/.claude/hooks/sdd-report-guard.py"` com `timeout` 10; a 2ª com matcher `Agent|Task` e comando `python3 "$CLAUDE_PROJECT_DIR/.claude/hooks/sdd-avaliador-guard.py"`. Toda outra chave e entrada fica. Escreve com `indent=2`, `ensure_ascii=False` e `\n` final; imprime `ALTERADO`/`EMDIA`. `claude_settings_em_dia` devolve 0 quando as 2 entradas estão lá. `python3` ausente → `die` 64 antes de qualquer escrita (como o Gemini).
- `doctor` (vendor `claude`): a linha existente ganha "· hooks" quando `.claude/hooks/` e as 2 entradas existem; senão ⚠️ `rode sync --vendors claude`.

**Rationale:** mesma mecânica já testada (cabeçalho, `--check`, merge seguro); o vendor aparece só em `bin/adapters/claude/` e no gerado; o `--check` compila os `.py`.

**Alternatives Rejected:** 1. Comando em linha no JSON — ilegível e sem `--check`. 2. Scripts em `sdd/bin/` — o formato do payload é do vendor e `sdd/bin/` é agnóstico.

**Consequences:** `test_sdd_open.py` com `--vendors claude` passa a ver `.claude/hooks/` e `.claude/settings.json` no projeto (os testes que contam arquivos são ajustados). Ganhamos um adaptador regenerável e conferível.

### Decision 6: Guards em Python, fail-open com aviso; o despacho do avaliador é reconhecido pela palavra `veredito`

| **Status** | Accepted | · | **Date** | 2026-10-30 |

**Context:** o payload do hook do vendor é JSON no stdin; a resposta é JSON no stdout; a fonte do privado (`claude-build-report-guard.py`, `claude-avaliador-guard.py`) é Python fail-open. O open não tem nome fixo de subagente; a `sdd-build` 5d manda o brief com "modo `veredito`".

**Choice:**
- `sdd-report-guard.py`: lê o JSON; age só se `tool_name` ∈ Write/Edit/MultiEdit e o basename de `tool_input.file_path` casa `BUILD_REPORT_*.md` **e** o caminho não tem o componente `sdd/fixtures/` (mesma exceção do hook; nota H1). Calcula o conteúdo resultante como `resulting_content()` do privado (Write → `content`; Edit → aplica `old_string`→`new_string`, com `replace_all`; `MultiEdit` → cada item de `edits`; `old_string` ausente do arquivo → nada a conferir). Chama `python3 -B <projeto>/sdd/bin/report-lint.py --stdin <file_path>` com o conteúdo no stdin (`projeto` = `CLAUDE_PROJECT_DIR`, senão `cwd` do payload, senão o diretório atual). Exit 1 → imprime o JSON de `deny` com a razão começando por `🛑 sdd-open: gravação de <basename> negada — o relatório não passa no report-lint:` e a saída do lint (UX U9); exit 0 → nada; lint ausente, exit ≥ 64, payload ilegível ou exceção → `systemMessage` começando por `⚠️ sdd-open:` e dizendo "não conferido"; exit 0 sempre. `SDD_REPORT_GUARD=off` → `systemMessage` "guard desligado — declare no BUILD_REPORT".
- `sdd-avaliador-guard.py`: age só se `tool_name` ∈ Agent/Task e `veredito` aparece (sem distinguir caixa) em `tool_input.prompt` ou `tool_input.description`. Chama `bash <projeto>/sdd/bin/avaliador-guard.sh`; exit 1 → `deny` com razão `🛑 sdd-open: despacho do avaliador negado — há trabalho não commitado:` + saída do guard; exit 0 → nada (se a saída trouxer `⚠️`, como no bypass `SDD_AVALIADOR_GUARD=off`, vira `systemMessage`); exit 2/64 ou exceção → `systemMessage` "não conferido".
- Os dois só usam stdlib e rodam em Python 3.9.

**Rationale:** hook quebrado não pode travar toda escrita nem todo despacho; a razão começa pelo que foi negado, para o agente traduzir ao aluno; `veredito` é o único sinal que existe no brief do open.

**Alternatives Rejected:** 1. Guard em todo despacho — travaria advisor e workers. 2. Nome fixo de subagente — o open não tem. 3. Falha fechada — contra a fonte e contra a regra "falha aberta, mas avisa" do plano.

**Consequences:** um brief de avaliador sem a palavra `veredito` não é guardado (a `sdd-build` já a exige); um advisor cujo prompt cite "veredito" passa pelo guard (custo: um commit). Ganhamos a E6 sem tocar em `sdd/bin/`.

### Decision 7: Fixtures montadas em execução onde o publish-gate reprovaria; testes por sandbox; `test_agnostico` vigia `sdd/hooks/`

| **Status** | Accepted | · | **Date** | 2026-10-30 |

**Context:** o G1 do publish-gate roda `gitleaks detect` na árvore inteira (o `generic-api-key` casa `password`/`token` com valor de entropia alta) e o G2 reprova CPF/CNPJ e 11+ dígitos; um arquivo de 101 KB ou com byte NUL em `sdd/fixtures/` é peso e ruído.

**Choice:**
- Em disco, `sdd/fixtures/hooks/` leva só o que o gate aceita e o teste reusa: `config-placeholder.json` (o caso que **passa** o H3; medido pela revisão: `gitleaks detect` sai 0 sobre ele), `payload-write-build-report.json`, `payload-edit-build-report.json`, `payload-agent-veredito.json` (payloads dos guards, com o caminho do arquivo preenchido pelo teste) e `settings-com-outros-hooks.json` (um `settings.json` de usuário com outra entrada, para o merge). Arquivo acima do teto, byte NUL, credencial, CPF/CNPJ e playbook colapsado são montados pelo teste em tempo de execução (o playbook reusa `sdd/fixtures/playbook/`; o `BUILD_REPORT` reusa `sdd/fixtures/evidencia/`).
- **O literal do teste também é varrido pelo G1** (medido pela revisão: um valor de alta entropia em `tests/test_hooks.py` dá `leaks found: 2`; nota M4): valores de credencial que devem **reprovar** o H3 são gerados em execução (`random.Random(semente)`, alfanumérico ≥ 10) ou são literais de baixa entropia sem dígito (`abcdefghij`); CPF/CNPJ seguem o `dv_cpf`/`dv_cnpj` do `test_alarme.py`. Antes do commit do build, `gitleaks detect --source tests --no-git --exit-code 1` e o mesmo sobre `sdd/fixtures/hooks` saem 0 (`evidence/F8_HOOKS/gitleaks-tests.log`).
- `tests/test_hooks.py`: sandbox por teste (`tests/apoio.py`), repositório com `sdd/hooks/`, `sdd/bin/`, `sdd/config.yaml` e `.agents/skills/sdd-higiene-dado/` copiados, `core.hooksPath` ligado; um método por AT (AT-007 a AT-016), inclusive um remoto "origin" simulado (`git remote add` + `git fetch` de um clone local) para H6 e pre-push, e um `gitleaks` falso no `PATH` (script que sai 1 ou 0). Para a falha aberta sem `python3`, o teste monta um diretório de `PATH` só com links para `bash`, `git`, `awk`, `sed`, `grep`, `tr`, `wc`, `basename`, `mktemp`, `cat`, `head`, `cmp`, `dirname` (sem `python3`): tirar `/usr/bin` do `PATH` levaria junto o `git` e o `awk` no macOS (nota L9).
- `tests/test_claude_adapter.py`: `init --vendors claude` e `sync` (AT-020, AT-021) e os 2 guards com payload no stdin (AT-022 a AT-024).
- `tests/test_sdd_open.py`: casos novos de `init`/`doctor` (AT-001 a AT-006); `tests/test_alarme.py`: classe nova para o modo hooks (AT-017, AT-018), 29 testes intactos (AT-019).
- `tests/test_agnostico.py`: `sdd/hooks` entra no `ESCOPO` (o hook vai para o projeto do usuário e tem de ser agnóstico); `bin/adapters/` fica fora. `tests/test_bash32.py`: varre também `sdd/hooks/*`. `tests/test_docs.py`: tupla do roadmap sem "Hooks", `docs/hooks.md` + PT linkados e com `--no-verify`.
- Sabotagem (AT-029): 7 mutações, uma por script, registradas em `evidence/F8_HOOKS/sabotagem.log`; baseline vermelha (AT-030): os testes novos sobre a árvore `v2.2.8`, em `baseline.log`.

**Rationale:** regra 6 do PORTE (fixture e teste dos dois lados) sem violar G1/G2 nem inchar o repositório; o teste de sincronia das listas (Decision 2) e o de agnosticismo são o que impede deriva.

**Alternatives Rejected:** 1. Fixtures binárias/grandes em disco — peso e falso positivo do gate. 2. Excluir `sdd/fixtures/hooks/` do gitleaks por `.gitleaksignore` — abriria porta para vazamento real.

**Consequences:** os testes constroem mais do que leem; `conftest`-style helpers ficam em cada arquivo de teste (a suíte é unittest puro). Ganhamos G1/G2 verdes e os dois lados de cada regra provados.

### Decision 8: Docs, slot e versões — o aviso mora no produto

| **Status** | Accepted | · | **Date** | 2026-10-30 |

**Context:** a Release é `v2.2.9` automática; o público não lê lista de Releases; o roadmap tem a linha "Hooks" que a F8 entrega.

**Choice:** `sdd/config.example.yaml` ganha `project.context_file_max_kb: 100` com o comentário do que é e do default; `docs/hooks.md` e `docs/pt-BR/hooks.md` (tabela regra · o que recusa · como corrigir · exemplo de mensagem; "O limite: `--no-verify`" dizendo que a verdade final é o `report-lint` da release e o CI, e que o hook confere a evidência no disco; "Desligar" com `git config --unset core.hooksPath` e o aviso de que o próximo `init` religa; "No Claude Code" nomeando o vendor só ali e registrando que esse vendor passa a exigir `python3`), linkados do `README.md` e do `README.pt-BR.md` na lista de docs; roadmap EN/PT sem a linha "Hooks" (6 linhas); `docs/cli-conventions.md` ganha `COMMIT RECUSADO` na lista de palavras e a linha de exits dos hooks (`pre-commit` 0/1; `pre-push` 0); a ficha da `sdd-higiene-dado` no guia do aluno diz os dois lugares do alarme; `.github/workflows/release.yml` ganha `sdd/hooks/**` em `paths:` (1 linha), para um conserto só no hook publicar Release (nota L10; `tests/test_release_workflow.py` continua verde). Em toda mensagem e doc, o hook é descrito como "5 regras + relatório + alarme", nunca só "5 regras" (nota L10). `MANIFEST.txt` recebe todo arquivo novo em ordem `LC_ALL=C`.

**Rationale:** decisão 9 do brainstorm; `test_docs.py` prova links e conteúdo; o publish-gate G3 prova o manifest.

**Alternatives Rejected:** 1. Só `docs/hooks.md` em inglês — o público é PT e todos os docs do pacote têm as duas línguas. 2. Tag `v2.3.0` — recusada no brainstorm.

**Consequences:** 2 docs novos a manter; nenhuma skill de fase muda (só a higiene). Ganhamos a explicação completa num lugar só e o roadmap honesto.

---

## File Manifest

| # | File | Action | Purpose | Agent | Dependencies |
|---|------|--------|---------|-------|--------------|
| 1 | `sdd/hooks/pre-commit` | Create | dispatcher: H6, H2, H5, H3 (+gitleaks), H4, REPORT, HIGIENE; recusa única (Decisions 1, 2) | (general) | None |
| 2 | `sdd/hooks/pre-push` | Create | aviso de base velha (Decision 2) | (general) | None |
| 3 | `bin/lib/vendors.sh` | Modify | `vendor_arquivo_contexto`, `VENDOR_ARQUIVOS_CONTEXTO`; `vendor_alvos claude` com `.claude/hooks` e `.claude/settings.json` (Decisions 2, 5) | (general) | None |
| 4 | `bin/lib/merge.sh` | Modify | `merge_claude_settings`, `claude_settings_em_dia` (Decision 5) | (general) | None |
| 5 | `bin/adapters/claude/sdd-report-guard.py` | Create | guard de Write/Edit do `BUILD_REPORT` (Decision 6) | (general) | None |
| 6 | `bin/adapters/claude/sdd-avaliador-guard.py` | Create | guard do despacho do avaliador (Decision 6) | (general) | None |
| 7 | `bin/sdd-open.sh` | Modify | `sdd_faltantes` com `hooks`, `chmod +x`, `hooks_estado`, linha do plano, `core.hooksPath`, migração, `doctor`; render dos adaptadores com prefixo, `--check` e `doctor` do vendor `claude` (Decisions 3, 5) | (general) | 3, 4, 5, 6 |
| 8 | `sdd/config.example.yaml` | Modify | slot `project.context_file_max_kb: 100` (Decision 8) | (general) | None |
| 9 | `.agents/skills/sdd-higiene-dado/scripts/alarme.sh` | Modify | modo hooks: marca do dispatcher, `sdd.higieneDado` (Decision 4) | (general) | 1 |
| 10 | `.agents/skills/sdd-higiene-dado/scripts/pre-commit.sh` | Modify | linha de desinstalar quando há `core.hooksPath` (Decision 4) | (general) | None |
| 11 | `.agents/skills/sdd-higiene-dado/SKILL.md` | Modify | 1.2.0: modo hooks nos passos, identificação, scripts (Decision 4) | (general) | 9 |
| 12 | `.agents/skills/sdd-higiene-dado/manifest.json` | Modify | 1.2.0 (Decision 4) | (general) | None |
| 13 | `.agents/skills/sdd-higiene-dado/evals/cases.json` | Modify | 1.2.0 (Decision 4) | (general) | None |
| 14 | `.agents/skills/sdd-higiene-dado/CHANGELOG.md` | Modify | entrada 1.2.0 (Decision 4) | (general) | None |
| 15 | `.agents/skills/sdd-higiene-dado/references/COMO_FUNCIONA.md` | Modify | o segundo lugar do alarme (Decision 4) | (general) | None |
| 16 | `.agents/skills/sdd-higiene-dado/references/RUNTIME_COMPATIBILITY.md` | Modify | `core.hooksPath = sdd/hooks` deixa de recusar (Decision 4) | (general) | None |
| 17 | `sdd/fixtures/hooks/config-placeholder.json` | Create | H3: placeholders que passam (Decision 7) | (general) | None |
| 18 | `sdd/fixtures/hooks/payload-write-build-report.json` | Create | payload Write para o guard (Decision 7) | (general) | None |
| 19 | `sdd/fixtures/hooks/payload-edit-build-report.json` | Create | payload Edit para o guard (Decision 7) | (general) | None |
| 20 | `sdd/fixtures/hooks/payload-agent-veredito.json` | Create | payload de despacho com `veredito` (Decision 7) | (general) | None |
| 21 | `sdd/fixtures/hooks/settings-com-outros-hooks.json` | Create | `settings.json` de usuário com outra entrada (Decision 7) | (general) | None |
| 22 | `tests/test_hooks.py` | Create | AT-007 a AT-016; sincronia das listas de contexto (Decision 7) | (general) | 1, 2, 3, 17 |
| 23 | `tests/test_claude_adapter.py` | Create | AT-020 a AT-024 (Decision 7) | (general) | 4, 5, 6, 7, 18, 19, 20, 21 |
| 24 | `tests/test_sdd_open.py` | Modify | AT-001 a AT-006; contagens com `.claude/hooks` (Decisions 3, 5) | (general) | 7 |
| 25 | `tests/test_alarme.py` | Modify | classe nova: AT-017, AT-018; os 29 intactos (Decision 4) | (general) | 9, 10 |
| 26 | `tests/test_docs.py` | Modify | roadmap sem "Hooks"; `docs/hooks*.md` (Decision 8) | (general) | 29, 30, 31, 32, 33, 34 |
| 27 | `tests/test_bash32.py` | Modify | varre `sdd/hooks/*` (Decision 7) | (general) | 1, 2 |
| 28 | `tests/test_agnostico.py` | Modify | `sdd/hooks` no `ESCOPO` (Decision 7) | (general) | 1, 2 |
| 29 | `docs/hooks.md` | Create | regras, dispatcher, limite do `--no-verify`, desligar, adaptador (Decision 8) | (general) | None |
| 30 | `docs/pt-BR/hooks.md` | Create | idem, PT (Decision 8) | (general) | None |
| 31 | `docs/roadmap.md` | Modify | sem a linha "Hooks" (Decision 8) | (general) | None |
| 32 | `docs/pt-BR/roadmap.md` | Modify | sem a linha "Hooks" (Decision 8) | (general) | None |
| 33 | `README.md` | Modify | link para `docs/hooks.md` (Decision 8) | (general) | 29 |
| 34 | `README.pt-BR.md` | Modify | link para `docs/pt-BR/hooks.md` (Decision 8) | (general) | 30 |
| 35 | `docs/pt-BR/guia-do-aluno.md` | Modify | ficha da higiene: os dois lugares do alarme (Decision 8) | (general) | None |
| 36 | `docs/cli-conventions.md` | Modify | `COMMIT RECUSADO`; exits dos hooks (Decision 8) | (general) | None |
| 37 | `MANIFEST.txt` | Modify | 14 arquivos novos, `LC_ALL=C` (Decision 8) | (general) | 1, 2, 5, 6, 17, 18, 19, 20, 21, 22, 23, 29, 30 |
| 38 | `.github/workflows/release.yml` | Modify | `sdd/hooks/**` em `paths:` (Decision 8, nota L10) | (general) | None |

**Total Files:** 38

Agent Discovery: Not available (um agente faz o build, modo default).

---

## Landmines aplicáveis

Varredura rodada em 2026-10-30 com `sdd/bin/playbook-lint.sh --grep` sobre 16 termos (hook, pre-commit, hooksPath, init, settings.json, higiene, gitleaks, NUL, playbook, credencial, json, worktree, chmod, config.yaml, adaptador, doctor): 0 hits diretos. Duas landmines genéricas se aplicam pelo processo:

| LM-nnn | Superfície | Tratamento |
|---|---|---|
| LM-002 | todo teste novo | ✔ tratado: cada teste afirma a classe/texto da saída, não só o exit; os testes novos rodam na árvore `v2.2.8` e ficam vermelhos (`baseline.log`, AT-030) |
| LM-003 | revisão de contexto fresco | ✔ tratado: commit antes de cada revisão; o avaliador roda numa worktree destacada do commit; `avaliador-guard.sh` com os 4 prefixos desta família |
| LM-004 | — | N.A.: sem migration |

---

## Contrato de aceite

Negociado em 2026-10-30 com a revisão de contexto fresco do DESIGN v1.0 (`sdd/reviews/REVISAO_DESIGN_F8_HOOKS_20261030.md`, modo `contrato`). Os 5 ajustes foram **ACEITOS** e aplicados no DEFINE v1.2:

| # | Alvo | Classe | Decisão |
|---|---|---|---|
| 1 | AT-013, Decisions 2 e 6 | premissa contradita pelo código (o `init` copia fixtures que reprovam) | ACEITA — `BUILD_REPORT_*.md` sob `sdd/fixtures/` é pulado pelo hook e pelo guard; o commit da instalação passa |
| 2 | AT-019, Decision 4 | aceite falso ("29 intactos") | ACEITA — 28 intactos; `TestCopiaGerada` reescrita para o modo hooks |
| 3 | Decision 4, Pattern 3 | risco de apagar o dispatcher (`--git-path` segue o `hooksPath`) | ACEITA — arquivo legado por `--git-common-dir`; AT-014 afirma a linha sem `rm`; AT-017 afirma que o dispatcher sobrevive ao `desinstalar` |
| 4 | Constraints (G1), Decision 7 | o G1 varre `tests/` | ACEITA — valores gerados em execução ou de baixa entropia; `gitleaks detect` sobre `tests/` e `sdd/fixtures/hooks` antes do commit |
| 5 | AT-012, Decisions 2 e 3 | efeito contrário ao fluxo do aluno (H6 no commit do `init`) | ACEITA — `→ [H6]` com `git switch -c <nome>`; `→` final do `init` diz como commitar a instalação |

Ajuste já feito no Define antes da revisão (DEFINE v1.1): o comando das entradas do `settings.json` usa `"$CLAUDE_PROJECT_DIR/…"` entre aspas (AT-020), e a exceção da linha de desinstalar do `pre-commit.sh` entra em Constraints.

---

## Agent Assignment Rationale

| Agent | Files | Why |
|---|---|---|
| (general) | 1–38 | Modo default: hook, instalador, alarme e guards compartilham o vocabulário de saída, a leitura do `sdd/config.yaml` e as marcas que se reconhecem (dispatcher ↔ `alarme.sh`); um autor mantém os nomes coerentes |

---

## Code Patterns

### Pattern 1: Regra como função que acumula (bash 3.2, `pre-commit`)

```bash
ACHADOS=""; CLASSES=""; AVISOS=""
achado()
{
  ACHADOS="$ACHADOS  🛑 [$1] $2"$'\n'
  case " $CLASSES " in *" $1 "*) ;; *) CLASSES="$CLASSES $1" ;; esac
}
aviso()
{
  AVISOS="$AVISOS⚠️  $1"$'\n'
}

regra_h2() { # teto do arquivo de contexto, pelo blob staged
  local f base sz
  while IFS= read -r -d '' f; do
    base=$(basename "$f")
    case " $ARQUIVOS_CONTEXTO " in *" $base "*) ;; *) continue ;; esac
    sz=$(git cat-file -s ":$f" 2>/dev/null || echo 0)
    [ "$sz" -gt $((TETO_KB * 1024)) ] && achado H2 "$f: $sz bytes (teto $TETO_KB KB)"
  done < "$STAGED"
}
```

O laço lê de um arquivo (`$STAGED`, NUL-separado), nunca de `$(…)`, que descartaria o NUL. O config entra por `sed -n` numa variável validada (`case "$v" in ''|*[!0-9]*) v=100 ;; esac`).

### Pattern 2: Recusa única no padrão do pacote (UX U2, U8)

```text
sdd-open: commit recusado. Encontrei o que não pode entrar nesta versão:

  🛑 [H2] AGENTS.md: 204800 bytes (teto 100 KB)
  🛑 [H3] .vscode/sftp.json: credencial em texto claro (chave: password)

Por que importa:
  [H2] o arquivo de contexto entra inteiro em toda sessão do agente; acima do teto, estoura a janela.
  [H3] o que entra no git fica no histórico e vai junto em todo push; rotacionar vira o único conserto.

RESULTADO: COMMIT RECUSADO
→ [H2] mova o conteúdo volumoso para docs/ ou sdd/; ou ajuste project.context_file_max_kb em sdd/config.yaml
→ [H3] troque o valor por um placeholder (CHANGEME, example) ou tire o arquivo: git restore --staged ".vscode/sftp.json"
→ se você conferiu e quer gravar mesmo assim, só desta vez: git commit --no-verify
  Agente de IA: não use --no-verify sem o OK explícito da pessoa.
```

### Pattern 3: Estado dos hooks no `init` (bash 3.2, `sdd-open.sh`)

```bash
hooks_estado() { # → LIVRE | LIGADO | HIGIENE | OUTRO <descrição>
  local hp hook
  hp=$(git config --get core.hooksPath 2>/dev/null || true)
  # --git-common-dir, nunca --git-path hooks/…: este segue o core.hooksPath até o dispatcher
  hook="$(git rev-parse --git-common-dir 2>/dev/null)/hooks/pre-commit"
  if [ "$hp" = "sdd/hooks" ] || [ "$hp" = "$ROOT/sdd/hooks" ]; then printf 'LIGADO\n'
  elif [ -n "$hp" ]; then printf 'OUTRO core.hooksPath = %s\n' "$hp"
  elif [ -f "$hook" ] && grep -qF "$MARCA_HIGIENE" "$hook"; then printf 'HIGIENE\n'
  elif [ -f "$hook" ]; then printf 'OUTRO um pre-commit em %s\n' "$hook"
  else printf 'LIVRE\n'; fi
}
```

### Pattern 4: Guard fail-open (Python 3.9, `bin/adapters/claude/`)

```python
def main():
    try:
        payload = json.load(sys.stdin)
    except Exception as exc:
        return aviso("payload do hook ilegível (%s) — BUILD_REPORT não conferido" % type(exc).__name__)
    # ... filtra tool_name e basename, calcula o conteúdo resultante, chama o lint ...
    if rc == 1:
        return negar("🛑 sdd-open: gravação de %s negada — o relatório não passa no report-lint:\n%s" % (nome, saida))
    if rc != 0:
        return aviso("report-lint saiu %d — BUILD_REPORT não conferido" % rc)

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # hook quebrado não trava a escrita
        aviso("erro interno (%s) — BUILD_REPORT não conferido" % exc)
    sys.exit(0)
```

`negar` escreve o objeto com `hookSpecificOutput` (evento `PreToolUse`, `permissionDecision` igual a `deny`, `permissionDecisionReason` com a razão); `aviso` escreve o objeto com `systemMessage` começando por `⚠️ sdd-open:`. Os dois usam `json.dumps(..., ensure_ascii=False)`.

### Pattern 5: Merge de entrada no `settings.json` (Python embutido em `merge.sh`)

Mesma casca do `merge_gemini_settings`: `python3 -I -` com heredoc, `JSONERR <linha>: <msg>` e exit 66 quando o JSON é inválido ou o topo não é objeto; `data.setdefault("hooks", dict())` e `hooks.setdefault("PreToolUse", list())`; uma entrada do open é considerada presente quando algum item da lista tem um `hooks[].command` que contém o nome do script; só então nada é acrescentado. Saída `ALTERADO`/`EMDIA`; o shell mapeia 66 para `die` com "nada foi alterado".

### Pattern 6: Receita de evidência com `rc` honesto (F7)

```bash
out=$(bash -c "$cmd" 2>&1); rc=$?
printf '$ %s\n%s\n[exit=%s]\n' "$cmd" "$out" "$rc" > "$E/$nome.log"
```

Nunca um formatador (`tail`, `sed`, `sort`) no último estágio da linha `$`; `bash sdd/bin/gate-shell-evidencia.sh sdd/reports/evidence/F8_HOOKS` confere.

---

## Data Flow

1. **`init`**: `planejar` → `hooks_estado` → linha do plano (ou ⚠️ de OUTRO) → confirmação única → `aplicar` copia `sdd/hooks/` (completa), `chmod +x`, `git config core.hooksPath sdd/hooks` (LIVRE/HIGIENE), `git config sdd.higieneDado on` + ⚠️ (HIGIENE) → `doctor` → `RESULTADO: INSTALADO`.
2. **`git commit`**: git chama `sdd/hooks/pre-commit` na raiz da worktree → lê `sdd/config.yaml` e a lista staged → H6 → H2 → H5 → H3 (+gitleaks) → H4 → REPORT → HIGIENE → recusa única (exit 1) ou ⚠️ acumulados (exit 0).
3. **`git push`**: git chama `sdd/hooks/pre-push <remote> <url>` com as refs no stdin → compara cada sha local com `refs/remotes/<remote>/<default_branch>` → ⚠️ ou silêncio → exit 0.
4. **`alarme.sh`**: `MODO` (arquivo | hooks | OUTRO) → `verificar`/`instalar`/`desinstalar` agem no arquivo ou na config.
5. **Claude Code**: Write/Edit → `sdd-report-guard.py` lê o payload → conteúdo resultante → `report-lint.py --stdin` → deny/silêncio/⚠️; Agent/Task com `veredito` → `sdd-avaliador-guard.py` → `avaliador-guard.sh` → deny/silêncio/⚠️.

---

## Integration Points

| Com | Como | Contrato |
|---|---|---|
| `sdd/bin/report-lint.py` (F7) | `--stdin <caminho>` com o blob staged ou o conteúdo simulado | exits 0/1/64; saída com `🛑 [classe]` |
| `sdd/bin/avaliador-guard.sh` (F7) | chamado pelo guard do despacho | exits 0/1/2/64 |
| `sdd/bin/playbook-lint.sh` | `--anti-collapse <head> <staged>` | exits 0/1/64 |
| `.agents/skills/sdd-higiene-dado/scripts/pre-commit.sh` | chamado pelo dispatcher quando `sdd.higieneDado=on` | exit 0/1; mensagem própria |
| `git` | `core.hooksPath`, `sdd.higieneDado`, `cat-file`, `diff --cached -z`, `symbolic-ref`, `rev-parse --git-path` | git ≥ 2.20 |
| `gitleaks` (opcional) | `protect --staged --redact --no-banner` | exit 0/1; outro exit vira ⚠️ |
| Claude Code | `.claude/settings.json` → `hooks.PreToolUse`; payload JSON no stdin; `permissionDecision`/`systemMessage` no stdout | A-002 do DEFINE |

---

## Testing Strategy

| Camada | O que | Onde | ATs |
|---|---|---|---|
| Unit/contrato (sandbox git por teste) | cada regra do hook dos dois lados; remoto simulado; `PATH` sem `python3`; `gitleaks` falso | `tests/test_hooks.py` | AT-007 a AT-016 |
| Unit/contrato | `init`/`doctor` nos 4 estados; `--dry-run`; idempotência | `tests/test_sdd_open.py` | AT-001 a AT-006 |
| Unit/contrato | `alarme.sh` em modo hooks e OUTRO; 29 intactos | `tests/test_alarme.py` | AT-017 a AT-019 |
| Unit/contrato | render, merge, `--check`; guards com payload | `tests/test_claude_adapter.py` | AT-020 a AT-024 |
| Lint de pacote | agnosticismo, bash 3.2, docs, versões | `tests/test_agnostico.py`, `test_bash32.py`, `test_docs.py`, `check-versions` | AT-025 a AT-027 |
| Piso | suíte com `SDD_TEST_BASH=/bin/bash /usr/bin/python3` | Verify Gate | todos do `cmd` |
| CI | Ubuntu + macOS | PR | AT-028 |
| Baseline vermelha | testes novos na árvore `v2.2.8` | `baseline.log` | AT-030, LM-002 |
| Sabotagem | 7 mutações | `sabotagem.log` | AT-029 |
| Revisão de contexto fresco | DESIGN (contrato) e build (veredito) | `sdd/reviews/` | todos |

---

## Error Handling

| Situação | Comportamento |
|---|---|
| `python3` ausente no commit | REPORT pula com `⚠️ python3 ausente: BUILD_REPORT não conferido neste commit (a release confere)`; exit segue o resto |
| `sdd/bin/report-lint.py` ou `playbook-lint.sh` ausentes | ⚠️ nomeando a regra pulada e `rode init (completa sdd/bin)` |
| `sdd/config.yaml` ausente ou slot inválido | defaults (`main`, 100) sem aviso: é o estado de um projeto recém-instalado |
| `git diff --cached` falha | `🛑 não consegui ler o índice` + `RESULTADO: COMMIT RECUSADO` (fail-closed: sem lista, não dá para conferir) |
| `gitleaks` sai ≠ 0 e ≠ 1 | ⚠️ e segue |
| higiene ligada e `pre-commit.sh` ausente | ⚠️ `alarme da higiene ligado mas o script não existe — rode init` |
| `init` sem permissão em `.claude/settings.json` ou `.git/config` | `die` em `destinos_checar` antes de escrever (como hoje) |
| `settings.json` inválido | exit 66, nada escrito |
| guard: payload ilegível, lint ausente, exceção | `systemMessage` ⚠️, exit 0 |
| hook sem `-x` | o git o ignora: `doctor` acusa com `chmod +x` |

---

## Configuration

| Chave | Default | Quem lê | Observação |
|---|---|---|---|
| `project.context_file_max_kb` | `100` | `sdd/hooks/pre-commit` (H2) | inteiro > 0; vazio/ausente/inválido → 100 |
| `project.default_branch` | `main` | `pre-commit` (H6), `pre-push` | já existe |
| `core.hooksPath` (git) | — | `init` grava `sdd/hooks`; `doctor`, `alarme.sh` leem | relativo à raiz da worktree |
| `sdd.higieneDado` (git) | — | `pre-commit`, `alarme.sh`, `init` (migração) | `on` liga o alarme pelo dispatcher |
| `SDD_REPORT_GUARD`, `SDD_AVALIADOR_GUARD` | — | guards | `off` = bypass declarado no BUILD_REPORT |

Nenhum segredo.

---

## Security Considerations

- **H3 nunca imprime o valor** da credencial, só a chave (teste AT-008 afirma a ausência); `gitleaks` roda com `--redact`.
- **O hook só lê o índice** (`cat-file`, `diff --cached`); não altera arquivo nem config. Quem grava config é o `init` (com confirmação) e o `alarme.sh` (com o OK da pessoa).
- **`init` nunca desliga alarme alheio** nem apaga `.git/hooks/*`.
- **Guards fail-open**: um guard quebrado não trava o agente, mas avisa; o `report-lint` da release continua a verdade (`docs/hooks.md`).
- **`core.hooksPath` relativo** aponta para dentro do repositório: nada fora da árvore é executado por causa do open.
- **Fixtures limpas** (Decision 7): G1 e G2 do publish-gate conferem.

---

## Observability

- `doctor` mostra o estado dos hooks e do alarme numa linha.
- A recusa do hook é texto puro e vai inteira para o log do agente; a classe entre colchetes permite contar recusas por regra num log (`grep -c '🛑 \[H3\]'`).
- Sem trace do hook (fora de escopo; sinal S da UX review registrado como pergunta aos alunos).

---

## Requirements Traceability

| Requirement | Design | Files |
|---|---|---|
| AT-001, AT-002, AT-005 | Decision 3 (estado, plano, `chmod`, idempotência) | 7, 24 |
| AT-003, AT-004 | Decision 3 (OUTRO, HIGIENE) | 7, 24 |
| AT-006 | Decision 3 (`doctor`) | 7, 24 |
| AT-007 | Decision 2 (H2), Pattern 1 | 1, 3, 8, 22 |
| AT-008, AT-009 | Decision 2 (H3, gitleaks) | 1, 17, 22 |
| AT-010 | Decision 2 (H4) | 1, 22 |
| AT-011 | Decision 2 (H5) | 1, 22 |
| AT-012 | Decision 2 (H6) | 1, 22 |
| AT-013 | Decision 2 (REPORT) | 1, 22 |
| AT-014 | Decision 2 (HIGIENE), Decision 4 | 1, 10, 22 |
| AT-015 | Decision 1, Pattern 2 | 1, 22 |
| AT-016 | Decision 2 (pre-push) | 2, 22 |
| AT-017, AT-018, AT-019 | Decision 4 | 9, 10, 25 |
| AT-020, AT-021 | Decision 5, Pattern 5 | 3, 4, 7, 21, 23 |
| AT-022, AT-023 | Decision 6, Pattern 4 | 5, 18, 19, 23 |
| AT-024 | Decision 6 | 6, 20, 23 |
| AT-025 | Decision 7 | 27, 28 |
| AT-026 | Decision 8 | 26, 29–34 |
| AT-027 | Decision 4 | 11, 12, 13, 14 |
| AT-028 | Decisions 5, 7, 8 | 24, 37 |
| AT-029, AT-030 | Decision 7 (sabotagem, baseline) | 1, 2, 3, 5, 6, 7, 9 |
| MUST UX U1–U9 | Decisions 1, 3, 4, 6; Patterns 2, 3, 4 | 1, 7, 9, 5, 6 |

---

## Risks and Mitigations

| Risco | Mitigação |
|---|---|
| `core.hooksPath` relativo não resolver numa worktree secundária | AT-001/AT-012 rodam também numa worktree criada por `git worktree add`; é o uso do privado |
| `gitleaks` do G1 reprovar `config-placeholder.json` | A fixture leva só placeholders de baixa entropia; `gitleaks detect` sobre a fixture antes do commit (A-004) |
| `test_sdd_open.py` contar arquivos de `.claude/` e quebrar com `.claude/hooks/` | Ajustar as contagens no mesmo commit (linha 24 do manifest) |
| O hook rodar num projeto cujo `sdd/bin/` é mais velho (sem `--stdin`) | `report-lint` sai 64 → ⚠️ e segue; `doctor` já avisa `sdd/bin` diferente do pacote |
| `read -r -d ''` em bash 3.2 | Funciona em 3.2 (o `pre-commit.sh` da higiene já usa); `test_bash32` e o CI em macOS cobrem |
| H3 com falso positivo em `package-lock.json` | Token completo com delimitador antes da chave (fonte do privado); teste com `"parse-passwd": "^1.0.0"` |
| Dois ⚠️ iguais (plano e `doctor`) quando OUTRO | Aceito (Decision 3); o texto é o mesmo |
| `SKILL.md` da higiene passar de 500 linhas | 204 hoje; acréscimo previsto ~15 |

---

## Advisor Ledger

Revisão de contexto fresco do DESIGN v1.0 (`sdd/reviews/REVISAO_DESIGN_F8_HOOKS_20261030.md`, modo `contrato`, logs `AVAL-DESIGN-*.log`): NEEDS_WORK, 3 HIGH, 2 MEDIUM, 10 LOW.

| # | Nota | Severidade | Veredito | Evidência |
|---|---|---|---|---|
| H1 | O `init` copia `sdd/fixtures/evidencia/BUILD_REPORT_*.md`, que reprovam no lint (4/4); o 1º commit depois do `init` seria recusado e `test_sdd_open.Projeto.setUp` cairia | HIGH | APLICADA (Decisions 2 e 6; AT-013) | `AVAL-DESIGN-report-lint-fixtures.log` |
| H2 | `TestCopiaGerada` roda `init --vendors claude` e exige `.git/hooks/pre-commit`; "29 intactos" era falso | HIGH | APLICADA (Decision 4; AT-019) | `tests/test_alarme.py:332-348` |
| H3 | `git rev-parse --git-path hooks/pre-commit` segue o `hooksPath`: o `desinstalar` e a linha `rm <HOOK>` apontariam para o dispatcher | HIGH | APLICADA (Decisions 3 e 4; AT-014, AT-017) | `AVAL-DESIGN-git-path-hooksPath.log` |
| M4 | O G1 (`gitleaks detect`) varre `tests/`: literal de alta entropia no teste reprova o gate | MEDIUM | APLICADA (Decision 7; Constraints) | `AVAL-DESIGN-gitleaks-literal-teste.log` |
| M5 | H6 recusaria o commit da própria instalação em `main` com remoto; o `→` previsto não resolvia | MEDIUM | APLICADA (Decisions 2 e 3; AT-012, AT-001) | `AVAL-DESIGN-cherry-pick-hook.log` |
| L1 | `gitleaks protect` sem `-v` só diz `leaks found: N` | LOW | APLICADA (Decision 2) | `AVAL-DESIGN-gitleaks-protect.log` |
| L2 | Texto UTF-16 (PowerShell, Excel) tem NUL e seria recusado pela H5 | LOW | APLICADA (Decision 2: BOM UTF-16 pula) | `AVAL-DESIGN-h5-utf16.log` |
| L3 | `[[ =~ ]]` com intervalos no bash 3.2 depende da libc | LOW | APLICADA (Decision 2: `grep -E`) | — |
| L4 | Cabeçalho `fonte: bin/adapters/…` aponta para caminho do pacote; mensagem do `--check` fixa em `.agents/skills` | LOW | APLICADA (Decision 5) | `bin/sdd-open.sh:354` |
| L5 | Vendor `claude` passa a exigir `python3` | LOW | APLICADA (Decision 5; `docs/hooks.md`) | `bin/sdd-open.sh:427` |
| L6 | Desligar não é pegajoso: o próximo `init --yes` religa | LOW | REBATIDA_ESCOPO (documentado em `docs/hooks.md`; estado "desligado de propósito" é corte YAGNI) | — |
| L7 | `hooks_estado` × `alarme.sh` divergem no `hooksPath` absoluto | LOW | APLICADA (Decision 3) | — |
| L8 | O lint confere evidência no disco, não no índice | LOW | APLICADA (Decision 2; `docs/hooks.md`) | — |
| L9 | "PATH sem python3" tiraria também git e awk no macOS | LOW | APLICADA (Decision 7) | — |
| L10 | `sdd/hooks/**` fora dos `paths:` do `release.yml`; "5 regras" × 7 classes | LOW | APLICADA (Decision 8; manifest 38) | `.github/workflows/release.yml` |

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.3 | 2026-10-30 | SDD Build by RDD | Ciclo 2 da revisão do build (`AVALIACAO_F8_HOOKS_20261030-ciclo2.md`, PASS, 2 LOW aplicados): H3 itera todas as ocorrências (`credencial_real`) em vez de `head -1` (Decision 2); `hooks_path_e_nosso` normaliza `sdd/hooks/` e `./sdd/hooks` (Decisions 3 e 4) |
| 1.2 | 2026-10-30 | SDD Build by RDD | Ciclo 1 da revisão do build (`AVALIACAO_F8_HOOKS_20261030-ciclo1.md`, 1 MEDIUM + 5 LOW, todos aplicados): `claude_settings_checar` confere a forma (topo, `hooks`, `PreToolUse`) antes de escrever (Decision 5); H3 com regex de `.env` sem aspas e número de versão como placeholder (Decision 2); recusa só do alarme com cabeçalho próprio e `→ [alarme]` (Decision 1); `hooks_path_e_nosso` por `pwd -P` no `init` e no `alarme.sh` (Decisions 3 e 4); união de vendors sem `paste` |
| 1.1 | 2026-10-30 | SDD Design by RDD | Revisão de contexto fresco do DESIGN: 14 notas aplicadas e 1 rebatida por escopo (Advisor Ledger); Contrato de aceite com 5 ajustes ACEITOS; manifest 38 (`release.yml`); DEFINE v1.2 |
| 1.0 | 2026-10-30 | SDD Design by RDD | Versão inicial |

---

## Next Step

Execute o **SDD Build by RDD**.
