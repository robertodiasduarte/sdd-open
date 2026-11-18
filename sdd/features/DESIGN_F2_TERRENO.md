# DESIGN: F2 Terreno do sdd-open

> Technical design for implementing F2 Terreno do sdd-open

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | F2_TERRENO |
| **Date** | 2026-10-29 |
| **Author** | SDD Design by RDD |
| **BRAINSTORM** | `sdd/features/BRAINSTORM_F2_TERRENO.md` |
| **DEFINE** | `sdd/features/DEFINE_F2_TERRENO.md` |
| **UX REVIEW** | N/A |
| **LLM Prompts** | false |
| **Status** | Ready for Build |

---

## Architecture Overview

```text
  fonte: sdd-starter 17c69c4 (skills/…)            transplante + adaptação mínima
  ┌─────────────────────────────────────┐   ─────────────────────────────────────────►
  │ checar-ambiente  higiene-dado        │
  │ iniciar-repo     (tests/ de cada um) │
  └─────────────────────────────────────┘

  .agents/skills/ (fonte do open; init copia, sync gera .claude/ e .cursor/ com cabeçalho)
  ┌───────────────────────────┐  ┌──────────────────────────┐  ┌─────────────────────────┐
  │ sdd-checar-ambiente 1.3.0 │  │ sdd-higiene-dado 1.1.1   │  │ sdd-iniciar-repo 1.1.1  │
  │ scripts/checar.sh         │  │ scripts/alarme.sh ──────┐│  │ scripts/inventario.sh   │
  │  (normal | --frente |     │  │ scripts/pre-commit.sh ◄─┘│  └─────────────────────────┘
  │   --segredo  ← NOVO)      │  │  (instalar tira as linhas │
  └──┬───────────────┬────────┘  │   sdd-open:generated)     │
     │ --segredo     │ --frente  └──────────────────────────┘
     │ (sem rede)    │ (rede com teto)
     ▼               ▼
  ┌──────────────────────┐   ┌──────────────────────────────────────────────────────────┐
  │ bin/sdd-open.sh      │   │ .agents/skills/sdd-new-session/SKILL.md 1.1.0            │
  │ doctor: ⚠️ por achado │   │ Passo 0: checar.sh --frente → tabela de tradução         │
  │ ✅ sem achado; exit 0 │   │          (fallback: Passo 0 à mão, sem bash/sem script)  │
  └──────────────────────┘   │ Passo 1: descoberta (evidência literal)                  │
                             │ Passo 2: cria a frente → grava slots VAZIOS no            │
                             │          <frente>/sdd/config.yaml com # descoberto …      │
                             └──────────────────────────────────────────────────────────┘

  tests/ (raiz; nunca copiado ao usuário)          Verify Gate: git archive HEAD → publish-gate ci
  test_checar · test_alarme · test_inventario      → unittest discover -s tests (F1 115 + F2)
  test_matriz_new_session · test_sdd_open (+doctor)
```

---

## Components

| Component | Purpose | Technology / Pattern | Inputs | Outputs | Dependencies |
|---|---|---|---|---|---|
| `checar.sh` (porte) | Diagnóstico só leitura do ambiente; `--frente` para o pré-voo; `--segredo` novo, só dado exposto | bash 3.2, porte do starter 1.2.0 | cwd = projeto; `--frente` / `--segredo` | Relatório 🔴/⚠️/✅; exit 0/1 conforme o modo | git; curl e ls-remote só nos modos normal e `--frente` |
| `alarme.sh` + `pre-commit.sh` (porte) | Instala/confere/remove o alarme de commit; o hook recusa CPF/CNPJ válido, `.env`, `.pfx`/`.p12`, `.pem` com chave, planilha nova | bash 3.2, porte do starter 1.1.0 | `verificar` / `instalar` / `desinstalar` | `.git/hooks/pre-commit`; exit 0/1/2 | git |
| `inventario.sh` (porte) | Inventário só leitura antes do 1º commit | bash 3.2, porte do starter 1.1.0 | cwd = pasta do projeto | Lista sinalizada | git, find |
| SKILL.md das 3 skills (porte) | Procedimento e conversa já nos símbolos `✅ ▶️ ⬜ ⏸️ ➖` | Agent Skills, Markdown | — | Instruções ao agente | os scripts ao lado |
| `doctor` (alterado) | Acrescenta a conferência de segredo salvo no git | bash 3.2, função `doctor()` de `bin/sdd-open.sh` | `$PKG/.agents/skills/sdd-checar-ambiente/scripts/checar.sh --segredo` | Linhas `ok`/`warn`; exit 0 inalterado | `checar.sh` do pacote |
| `sdd-new-session` 1.1.0 (alterada) | Pré-voo por script com tabela de tradução e fallback; descoberta gravada na frente | Markdown (contrato lido pelo agente) | Saída e exit do `checar.sh --frente`; repo e arquivos do projeto | Frente criada + slots gravados | `checar.sh` da pasta de skills vizinha |
| Suítes de teste | Contrato portado (105) + contratos novos (`--segredo`, alarme sem cabeçalho, `doctor`, matriz, conteúdo) | Python 3.9 stdlib `unittest`, caixa-preta | Scripts reais | Pass/fail por AT | `tests/apoio.py` (F1) |

---

## Key Decisions

### Decision 1: Testes portados em `tests/` com o caminho do script recalculado

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-10-29 |
| **Source** | DEFINE (Goals, Constraints) / Brainstorm decisão 1 |

**Context:** os testes do starter acham o script por `Path(__file__).resolve().parents[1] / "scripts"`; `init`/`sync` copiam a pasta inteira da skill para o projeto do usuário.

**Choice:** `tests/test_checar.py`, `test_alarme.py`, `test_inventario.py` com `SKILL = RAIZ / ".agents/skills/<skill>"` (de `apoio.RAIZ`); o resto da suíte de cada um fica como no starter (classes, helpers próprios, servidor HTTP local do `test_checar`), exceto os literais (Decision 6). Os testes novos de cada script entram no mesmo arquivo do script.

**Rationale:** diff mínimo contra o starter mantém os 105 testes como prova do comportamento portado.

**Alternatives Rejected:**
1. Reescrever as 3 suítes sobre `apoio.Sandbox` — perderia a correspondência 1:1 com o starter e a prova.
2. Testes dentro da skill — vão ao usuário e exigem mudar CI e gate.

**Consequences:**
- Três estilos de sandbox convivem em `tests/` (o do starter em 3 arquivos, o `apoio` no resto).
- O `discover -s tests` existente pega tudo sem mudança no CI.

### Decision 2: `checar.sh --segredo` reusa o bloco de dado exposto, sem rede

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-10-29 |
| **Source** | DEFINE (AT-004…AT-006) / Brainstorm decisão 2 |

**Context:** o bloco "6. dado de cliente e segredos" do `checar.sh` já faz exatamente a conferência pedida, mas só roda no fim do modo normal, depois das 2 consultas de rede.

**Choice:** extrair o laço de dado exposto para uma função `dado_exposto()` (definida junto dos helpers do topo), chamada no modo normal no mesmo ponto de hoje e num desvio novo `MODO=segredo` logo depois do `parse` de argumentos e **antes** de `pasta_sincronizada`/`alcance`: calcula `RAIZ`, fixa `PUBLICO=0`, chama `dado_exposto`, imprime só o bloco `🔴 Dado exposto` (ou nada) e sai 1 com achado, 0 sem achado; fora de repositório, sai 0 sem imprimir.

**Rationale:** um único código conferindo segredo para skill e `doctor`; sem rede, o modo cabe no fim de todo `init`.

**Alternatives Rejected:**
1. Copiar a lógica para dentro do `doctor` — duas fontes do mesmo achado divergiriam.
2. `doctor` rodar o modo normal — 13 s de rede no pior caso a cada `init`.

**Consequences:**
- O modo normal precisa continuar idêntico (os 53 testes portados provam).
- Com `PUBLICO=0` fixo, a frase é sempre "Tirar do git não apaga do histórico…", que é a verdadeira sem saber se o repositório é público.

### Decision 3: `doctor` traduz o bloco do `--segredo` para `warn`/`ok`

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-10-29 |
| **Source** | DEFINE (AT-007…AT-009, AT-020) |

**Context:** o `doctor` fala por `ok`/`warn` (`bin/lib/say.sh`; `warn` vai para stderr) e sempre sai 0 com a linha `RESULTADO`.

**Choice:** no fim de `doctor()`, rodar `(cd "$ROOT" && "$BASH" "$CHECAR" --segredo)` com `CHECAR="$PKG/.agents/skills/sdd-checar-ambiente/scripts/checar.sh"`; linha `- …` vira `warn`, linhas indentadas (comando e medida) saem logo abaixo com recuo; exit 0 ⇒ `ok "nenhum segredo salvo no git (.env, .pfx, .p12, .pem com chave privada)"`; exit diferente de 0/1 ⇒ `warn` dizendo que não conseguiu conferir; script ausente ⇒ `warn "pacote incompleto: …checar.sh ausente — baixe o sdd-open de novo"`.

**Rationale:** script do **pacote** casa com a versão da CLI; `$BASH` roda no mesmo bash do `doctor` (o teste com `SDD_TEST_BASH=/bin/bash` cobre o 3.2).

**Alternatives Rejected:**
1. `$ROOT/.agents/skills/…` — o usuário pode ter editado ou apagado.
2. Repassar o bloco cru — o `doctor` misturaria dois formatos de saída.

**Consequences:**
- O `doctor` passa a depender de um arquivo de `.agents/skills/` do pacote (existe em clone e em `git archive`).
- Exit e `RESULTADO` do `doctor` ficam como estão.

### Decision 4: Tabela da `new-session` com trecho literal do script, amarrada por teste nos dois sentidos

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-10-29 |
| **Source** | DEFINE (AT-015) / Brainstorm decisão 7 |

**Context:** as mensagens do `checar.sh` têm variáveis (`$PROVEDOR`, `$ONDE_HOST`, `$SLUG`); casar mensagem com linha de tabela por regex sobre variáveis é frágil.

**Choice:** a 1ª coluna de cada linha da tabela "Como traduzir cada achado" traz, entre crases, um **trecho literal** (≥ 12 caracteres, sem variável) da mensagem do script. O teste extrai do `checar.sh` as mensagens de bloqueio que o `--frente` pode emitir (`add_impede "…"`, `add_remoto "…"` e `MSG="…"` entre os marcadores `# ── 1. onde estou` e `# ── 4. frentes`, menos o bloco `# ── 3. git utilizável` até `# Alcance do origin`, que só roda no modo normal) e exige: (a) toda mensagem contém o trecho de alguma linha; (b) todo trecho da tabela aparece em alguma mensagem. A linha "Qualquer outro achado" não tem crase e fica fora da conta.

**Rationale:** script e tabela mudam em arquivos diferentes; o teste acusa a mensagem nova sem tradução e a linha órfã.

**Alternatives Rejected:**
1. Regex com placeholders — quebra a cada mudança de redação.
2. Conferir à mão — diverge calado.

**Consequences:**
- Os 4 comentários-marcador do `checar.sh` viram parte do contrato (o teste falha com mensagem clara se sumirem).

### Decision 5: `alarme.sh instalar` filtra o cabeçalho gerado antes de montar o hook

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-10-29 |
| **Source** | DEFINE (AT-010) / Brainstorm decisão 12 |

**Context:** na cópia gerada, as linhas 2–3 do `pre-commit.sh` são `# sdd-open:generated - …`; o `instalar` monta o hook com `sed -n '1,2p'` + `# versão:` + `sed '1,2d'`, o que levaria o cabeçalho para dentro de `.git/hooks/pre-commit` e tiraria a marca da linha 2.

**Choice:** `corpo="$(grep -v -F 'sdd-open:generated' "$ORIGEM")"` e a montagem passa a operar sobre `corpo`; da fonte sem cabeçalho, o hook sai byte a byte igual ao de hoje.

**Rationale:** o hook instalado não é arquivo gerado pelo `sync` e não pode dizer "sync reescreve este arquivo".

**Alternatives Rejected:**
1. Mudar o gerador para não marcar `.sh` — mexe no `sync` (fora de escopo).

**Consequences:**
- Instalar a partir da fonte ou da cópia gerada produz o mesmo hook.

### Decision 6: Literais do G2 montados em tempo de execução, host `.invalid` preservado

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-10-29 |
| **Source** | DEFINE (Constraints, AT-017) |

**Context:** 20 linhas de e-mail fora de `example.*` e 1 CPF formatado nas fontes; `git@exemplo.invalid` é host que não resolve, de propósito.

**Choice:** e-mails de identidade e sugestões → `example.com` (`voce@example.com` no `checar.sh` e nas SKILL.md; `teste@example.com` nos testes); `git@github.com` e `git@exemplo.invalid` nos testes montados como `"git" + "@" + "github.com"` / `"git" + "@" + "exemplo.invalid"` (constante no topo do arquivo); CPF de amostra por concatenação, como em `tests/test_publish_gate_patterns.py`.

**Rationale:** G2 verde sem mudar a semântica de rede dos testes.

**Alternatives Rejected:**
1. Trocar o host por `example.com` — resolve de verdade e o teste tentaria rede.

**Consequences:**
- A saída do `checar.sh` com a sugestão de `git config` muda de `exemplo.com` para `example.com`; o teste portado que confere esse texto é ajustado junto.

### Decision 7: Suíte mais lenta aceita, sem mexer nos tetos do script

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-10-29 |
| **Source** | DEFINE (Open Questions) / medição |

**Context:** `test_checar.py` leva ~106 s (casos de rede parada esperam o teto de 10 s do `alcance`); a suíte passa de ~35 s para ~2,5 min.

**Choice:** manter. Não criar variável para encurtar o teto nem mudar `.github/` (o Success Criterion exige `git diff v2.2.1 -- .github/` vazio).

**Rationale:** encurtar o teto mudaria o comportamento que os testes provam; 2,5 min cabe no CI e no gate.

**Alternatives Rejected:**
1. Variável `SDD_CHECAR_TETO` — superfície nova só para teste.

**Consequences:**
- O Verify Gate e o CI ficam ~2 min mais longos.

---

## File Manifest

| # | File | Action | Purpose | Agent / Owner | Dependencies |
|---:|---|---|---|---|---|
| 1 | `.agents/skills/sdd-checar-ambiente/scripts/checar.sh` | Create | Porte + `dado_exposto()` + `--segredo`; `voce@example.com`; `IDENT` e o caso "sem `sdd-iniciar-repo`" sem `sdd-starter`/`npx` | (general) | None |
| 2 | `.agents/skills/sdd-checar-ambiente/SKILL.md` | Create | Porte; `version: "1.3.0"`; `--segredo` documentado; `sdd/ambiente.md` → slots de `sdd/config.yaml`; identificação e rodapé do sdd-open; e-mail em `example.com` | (general) | 1 |
| 3 | `.agents/skills/sdd-higiene-dado/scripts/pre-commit.sh` | Create | Porte; linha 3 "SDD Open by RDD" | (general) | None |
| 4 | `.agents/skills/sdd-higiene-dado/scripts/alarme.sh` | Create | Porte + filtro `sdd-open:generated` no `instalar` | (general) | 3 |
| 5 | `.agents/skills/sdd-higiene-dado/SKILL.md` | Create | Porte; `version: "1.1.1"`; identificação e rodapé do sdd-open; inventário do bundle sem `agents/openai.yaml` | (general) | 3, 4 |
| 6 | `.agents/skills/sdd-higiene-dado/manifest.json` | Create | Porte; `version` 1.1.1 | (general) | 5 |
| 7 | `.agents/skills/sdd-higiene-dado/evals/cases.json` | Create | Porte; `version` 1.1.1 | (general) | 5 |
| 8 | `.agents/skills/sdd-higiene-dado/CHANGELOG.md` | Create | Porte + entrada 1.1.1 (porte para o sdd-open; hook sem cabeçalho gerado) | (general) | 5 |
| 9 | `.agents/skills/sdd-higiene-dado/references/COMO_FUNCIONA.md` | Create | Porte literal (sem referência ao starter) | (general) | None |
| 10 | `.agents/skills/sdd-higiene-dado/references/ESCOPO_CONFIRMADO.md` | Create | Porte literal | (general) | None |
| 11 | `.agents/skills/sdd-higiene-dado/references/RUNTIME_COMPATIBILITY.md` | Create | Porte literal | (general) | None |
| 12 | `.agents/skills/sdd-iniciar-repo/scripts/inventario.sh` | Create | Porte | (general) | None |
| 13 | `.agents/skills/sdd-iniciar-repo/SKILL.md` | Create | Porte; `version: "1.1.1"`; `npx … sdd-starter` → a `sdd-higiene-dado` que vem com o sdd-open; `voce@example.com`; identificação e rodapé do sdd-open | (general) | 4, 12 |
| 14 | `.agents/skills/sdd-new-session/SKILL.md` | Modify | 1.1.0: pré-voo por `checar.sh --frente`, tabela com trecho literal, Passo 0 à mão como fallback, descoberta com evidência literal, gravação só em slot vazio do config da frente, parada em `default_branch` divergente | (general) | 1, 13 |
| 15 | `bin/sdd-open.sh` | Modify | `doctor()` chama `checar.sh --segredo` do pacote (Decision 3) | (general) | 1 |
| 16 | `tests/test_checar.py` | Create | 53 portados + `--segredo` (AT-004…AT-006) | (general) | 1 |
| 17 | `tests/test_alarme.py` | Create | 28 portados + hook sem cabeçalho a partir da cópia gerada por `init` real (AT-010) | (general) | 3, 4, 15 |
| 18 | `tests/test_inventario.py` | Create | 24 portados | (general) | 12 |
| 19 | `tests/test_matriz_new_session.py` | Create | Matriz nos dois sentidos (AT-015), conteúdo da `new-session` (AT-016), sem refs ao starter nem `openai.yaml` nas 3 portadas (AT-002, AT-003) | (general) | 1, 2, 5, 13, 14 |
| 20 | `tests/test_sdd_open.py` | Modify | `doctor` com `.env`, limpo e com pacote sem `checar.sh` (AT-007…AT-009); `bash -n` nas cópias geradas dos 4 scripts (AT-019) | (general) | 15 |
| 21 | `MANIFEST.txt` | Modify | +17 arquivos novos (1–13, 16–19) em ordem `LC_ALL=C` | (general) | 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 16, 17, 18, 19 |
| 22 | `tests/test_skill_lint.py` | Modify | `test_as_13_skills_reais_passam` → `test_as_16_skills_reais_passam` (drift do Build, decisão do Roberto) | (general) | 2, 5, 13 |

**Total Files:** 22

### Agent Assignment Rationale

| Agent / Owner | Files Assigned | Why |
|---|---|---|
| (general) | 1–22 | Porte de bash/Markdown e testes Python stdlib num repositório pequeno; nenhum catálogo de agentes especializado no projeto |

**Agent Discovery:** Not available

---

## Code Patterns

Os padrões escrevem `$VAR` sem chaves só por causa do lint deste documento; no código, vale o estilo do `bin/sdd-open.sh` (variável sempre entre chaves, principalmente antes de texto não-ASCII).

### Pattern 1: Desvio `--segredo` no `checar.sh`

```bash
MODO=normal
[ "$#" -gt 0 ] && case "$1" in
  --frente) MODO=frente ;;
  --segredo) MODO=segredo ;;   # só dado exposto, sem rede: o doctor do sdd-open chama este modo
esac
# … helpers (add_*, tem, sair, meta, relatorio) …

# Arquivo com segredo que o git já guarda (ls-files / grep --cached). Não abre nada para escrita.
dado_exposto() {
  local f b
  if [ "$PUBLICO" -eq 1 ]; then ONDE="Este repositório é público: o arquivo já está na internet."
  else ONDE="Tirar do git não apaga do histórico: se já houve push, quem tem acesso ao repositório tem o arquivo."; fi
  # … os dois laços de hoje (ls-files -z; grep --cached -l -z -I -e "PRIVATE KEY" -- '*.pem' '*.PEM') …
}

if [ "$MODO" = segredo ]; then
  RAIZ="$(git rev-parse --show-toplevel 2>/dev/null || true)"
  [ -n "$RAIZ" ] || exit 0
  PUBLICO=0; dado_exposto
  [ -n "$EXPOSTO" ] || exit 0
  printf '🔴 Dado exposto\n%s' "$EXPOSTO"; exit 1
fi
```

### Pattern 2: `doctor` lendo o `--segredo`

```bash
  local checar="$PKG/.agents/skills/sdd-checar-ambiente/scripts/checar.sh" saida rc l
  if [ ! -f "$checar" ]; then
    warn "pacote incompleto: .agents/skills/sdd-checar-ambiente/scripts/checar.sh ausente — baixe o sdd-open de novo"
  else
    saida="$(cd "$ROOT" && "$BASH" "$checar" --segredo 2>&1)"; rc=$?
    case "$rc" in
      0) ok "nenhum segredo salvo no git (.env, .pfx, .p12, .pem com chave privada)" ;;
      1) printf '%s\n' "$saida" | while IFS= read -r l; do
           case "$l" in '- '*) warn "$(printf '%s' "$l" | cut -c3-)" ;; '  '*) printf '      %s\n' "$(printf '%s' "$l" | cut -c3-)" >&2 ;; esac
         done ;;
      *) warn "não consegui conferir segredo salvo no git (checar.sh saiu $rc)" ;;
    esac
  fi
```

### Pattern 3: Hook sem o cabeçalho gerado (`alarme.sh instalar`)

```bash
    corpo="$(grep -v -F 'sdd-open:generated' "$ORIGEM")"   # a cópia de .claude/skills traz 2 linhas do sync
    ( printf '%s\n' "$corpo" | sed -n '1,2p'; echo "# versão: $VERSAO"; printf '%s\n' "$corpo" | sed '1,2d' ) > "$HOOK"
```

### Pattern 4: Teste da matriz (`tests/test_matriz_new_session.py`)

```python
CHECAR = RAIZ / ".agents/skills/sdd-checar-ambiente/scripts/checar.sh"
SESSAO = RAIZ / ".agents/skills/sdd-new-session/SKILL.md"
MSG = re.compile(r'(?:add_(?:impede|remoto)\s+|MSG=)"((?:[^"\\]|\\.)*)"')

def mensagens_do_frente() -> list[str]:
    texto = CHECAR.read_text(encoding="utf-8")
    ini, fim = texto.index("# ── 1. onde estou"), texto.index("# ── 4. frentes")
    regiao = texto[ini:fim]
    a, b = regiao.index("# ── 3. git utilizável"), regiao.index("# Alcance do origin")
    regiao = regiao[:a] + regiao[b:]          # identidade do git: só no modo normal
    return MSG.findall(regiao)

def trechos_da_tabela() -> list[str]:
    secao = SESSAO.read_text(encoding="utf-8").split("### Como traduzir cada achado", 1)[1]
    secao = re.split(r"\n###? ", secao, 1)[0]
    linhas = [l for l in secao.splitlines() if l.startswith("|") and not l.startswith("|---")]
    return [m for l in linhas[1:] for m in re.findall(r"`([^`]+)`", l.split("|")[1])]
```

### Pattern 5: Literal montado em tempo de execução

```python
ARROBA = "@"
SSH_GITHUB = "git" + ARROBA + "github.com"          # o G2 do publish-gate reprova o literal
SSH_INVALIDO = "git" + ARROBA + "exemplo.invalid"   # .invalid: nunca resolve, o teste não sai para a rede
CPF_FORMATADO = "000." + "000." + "000-" + "00"
```

### Pattern 6: Sabotagem no Build (prova de que o teste discrimina)

```bash
# 1. quebrar o contrato no script   2. rodar só a suíte dele e anotar o teste vermelho
python3 -B -m unittest discover -s tests -p 'test_checar.py'
# 3. desfazer e conferir verde
git checkout -- .agents/skills/sdd-checar-ambiente/scripts/checar.sh
```

Sabotagens planejadas: `checar.sh` tira `*.p12` do `case` de `dado_exposto`; `alarme.sh` sem o `grep -v` do cabeçalho; `pre-commit.sh` aceita qualquer dígito verificador de CPF; `inventario.sh` deixa de sinalizar arquivo > 50 MB; `doctor` sem a chamada ao `--segredo`.

---

## Data Flow

```text
doctor (fim de todo init, ou sozinho)
1. bin/sdd-open.sh doctor → linhas de hoje (bash/git/python, sdd/, AGENTS.md, skills, vendors)
   │
   ▼
2. CHECAR do pacote existe? não → ⚠️ pacote incompleto
   │ sim
   ▼
3. cd ROOT && bash CHECAR --segredo → git ls-files / git grep --cached (só leitura, sem rede)
   │  exit 0 → ✅ nenhum segredo salvo no git
   │  exit 1 → ⚠️ "<o que é> <arquivo> está salvo no git. Tirar do git não apaga…" + comando + medida
   │  outro  → ⚠️ não consegui conferir
   ▼
4. RESULTADO: DIAGNÓSTICO CONCLUÍDO → exit 0 (inalterado)

sdd-new-session
1. git --version (3 casos de hoje)
   │
   ▼
2. bash + <skills>/sdd-checar-ambiente/scripts/checar.sh existe?
   │ sim → checar.sh --frente
   │        exit 1 → traduz pela tabela, "Nada foi criado.", PARA
   │        exit 0 + "✅ Pronto para abrir a frente" → segue
   │        outra coisa → Passo 0 à mão
   │ não → Passo 0 à mão (PowerShell coberto)
   ▼
3. Descoberta: default_branch (cheio e ≠ HEAD do remoto → PARA e pergunta), editor, worktree_base,
   test_cmd / lint_cmd (CI > package.json scripts.test sem placeholder > Makefile test:; senão vazio)
   │
   ▼
4. Checagem de colisão → fetch refspec explícito → git worktree add <base>/<slug> -b <slug> origin/<padrão>
   │
   ▼
5. <frente>/sdd/config.yaml existe? sim → grava só slots vazios, com "# descoberto por sdd-new-session
   (AAAA-MM-DD): <evidência>" na linha de cima, sem commit · não → não grava e diz como resolver
   │
   ▼
6. Resposta: caminho, branch, slots gravados + evidência, como encerrar, aviso da janela nova
```

---

## Integration Points

| External System | Integration Type | Authentication | Direction | Failure / Retry |
|---|---|---|---|---|
| git local | CLI (`ls-files`, `grep --cached`, `rev-parse`) | N/A | in | Fora de repositório ⇒ `--segredo` sai 0 calado; erro de git ⇒ nada listado |
| Remoto `origin` (só `--frente` e modo normal) | `git ls-remote` com teto de 10 s, sem prompt | Credencial já existente do usuário; nunca pede senha | in | Classificado em login/host/rede/outro; sem retry |
| API do GitHub (só modo normal) | `curl --max-time 3` anônimo | Nenhuma | in | Falha ⇒ visibilidade desconhecida, nada dito |
| `.git/hooks/pre-commit` | Arquivo gravado por `alarme.sh instalar` | N/A | out | `core.hooksPath` ou hook de outra origem ⇒ exit 2 sem gravar |

---

## Testing Strategy

| Test Type | Scope / Requirement | Files | Tools | Pass Signal |
|---|---|---|---|---|
| Unit (porte) | Contratos de `checar.sh`, `alarme.sh`/`pre-commit.sh`, `inventario.sh` (AT-011…AT-014) | `tests/test_checar.py`, `tests/test_alarme.py`, `tests/test_inventario.py` | unittest, git isolado, HTTP local | 105 testes OK |
| Unit (novo) | `--segredo` positivo, negativo e sem rede (AT-004…AT-006) | `tests/test_checar.py` | unittest; `origin` que pendura + `SDD_CHECAR_GITHUB_API` inalcançável + teto de 3 s | exit 1/0 e tempo < 3 s |
| Integration | Hook sem cabeçalho a partir da cópia gerada por `init` real (AT-010) | `tests/test_alarme.py` | unittest + `bin/sdd-open.sh init --yes --vendors claude` | hook sem `sdd-open:generated`; `verificar` diz que é desta skill |
| Integration | `doctor` com `.env`, limpo e pacote sem `checar.sh` (AT-007…AT-009); `bash -n` nas cópias geradas (AT-019) | `tests/test_sdd_open.py` | unittest + `apoio.Sandbox` (`copia` do pacote para AT-009) | ⚠️/✅ esperados, exit 0, `RESULTADO:` |
| Contract | Matriz nos dois sentidos, conteúdo da `new-session`, refs proibidas, `openai.yaml` (AT-002, AT-003, AT-015, AT-016) | `tests/test_matriz_new_session.py` | unittest + `re` | 0 mensagem sem linha, 0 linha órfã |
| Regression | 115 da F1, exits do gate, fixtures, `sync` idempotente (AT-020) | `tests/*.py` existentes | unittest | verdes sem alteração |
| Sabotage | 5 sabotagens (AT-021) | BUILD_REPORT | Pattern 6 | teste nomeado vermelho → `git checkout` → verde |
| E2E / Verify Gate | Árvore commitada inteira (AT-001, AT-017, AT-018) | `sdd/features/DEFINE_F2_TERRENO.md` | `bash sdd/bin/verify-gate.sh --strict` + `python3 scripts/check-versions.py --base v2.2.1 --base-obrigatoria` | exit 0 nos dois |

Além do gate: `SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover -s tests -p 'test_*.py'` (piso bash 3.2 + Python 3.9) e `python3 sdd/bin/skill-lint.py .agents/skills/sdd-*/SKILL.md`.

---

## Error Handling

| Error Type | Detection | Handling Strategy | Retry? | Observability |
|---|---|---|---|---|
| `checar.sh` ausente no pacote | `[ ! -f ]` no `doctor` | ⚠️ pacote incompleto; exit 0 | No | linha ⚠️ |
| `checar.sh --segredo` quebra | exit diferente de 0 e 1 | ⚠️ não consegui conferir (com o exit) | No | linha ⚠️ |
| `--segredo` fora de repositório | `rev-parse` vazio | exit 0 sem saída | N/A | — |
| Script ausente/antigo na `new-session` | arquivo ausente, sem bash, exit 0 sem a linha ✅ | Passo 0 à mão | No | resposta diz qual caminho usou |
| `default_branch` cheio diverge do remoto | comparação com HEAD do `remote show origin` | para e pergunta; nada criado | No | decisão na resposta |
| Frente sem `sdd/config.yaml` | arquivo ausente na pasta nova | não grava; diz para versionar `sdd/` na branch padrão | No | linha na resposta |
| Outro alarme de commit | `core.hooksPath` ou hook sem a marca | exit 2, sem gravar, ensina a acrescentar à mão | No | saída do `alarme.sh` |

---

## Configuration

| Config Key | Type | Source / Default | Sensitive? | Description |
|---|---|---|---|---|
| `project.default_branch` | string | `sdd/config.yaml` (exemplo: `main`) | No | Lido pela `new-session`; divergência do remoto para a skill |
| `project.test_cmd` / `project.lint_cmd` | string | `sdd/config.yaml` (vazio) | No | Gravados pela `new-session` na frente só com evidência literal |
| `editor` / `worktree_base` | string | `sdd/config.yaml` (vazio) | No | Gravados pela `new-session` na frente quando vazios |
| `SDD_CHECAR_GITHUB_API` | env | `https://api.github.com` | No | Já existe no `checar.sh`; os testes apontam para servidor local |
| `SDD_TEST_BASH` | env | bash do PATH | No | Já existe em `tests/apoio.py`; roda a suíte no bash 3.2 |

---

## Security Considerations

- `--segredo` e `inventario.sh` só leem (`ls-files`, `grep --cached`, `find`); nada abre arquivo de segredo para escrita nem imprime o conteúdo dele, só o caminho.
- A mensagem não promete limpeza: diz que tirar do git não apaga do histórico e manda trocar senha, revogar certificado ou gerar chave nova.
- `alarme.sh` nunca sobrescreve hook de outra origem (husky, lefthook, `core.hooksPath`) e só desinstala o próprio.
- Nenhum comando de rede pede senha (`GIT_TERMINAL_PROMPT=0`, `BatchMode=yes`, teto de 10 s); o `--segredo` não sai para a rede.
- PII nos testes: CPF/CNPJ/e-mail/`git@` montados em tempo de execução; o G2 do publish-gate confere a árvore inteira no gate.

---

## Observability

| Aspect | Implementation | Signal / Why |
|---|---|---|
| Logging | `doctor`: linhas `ok`/`warn` e `RESULTADO:`; `checar.sh`: blocos 🔴/⚠️/✅ | O usuário vê o achado e o comando que resolve |
| Metrics | Contagem de testes por suíte no BUILD_REPORT (≥ 220) e tempo da suíte | Success Criteria do DEFINE |
| Tracing | N/A | Scripts locais curtos |

---

## Requirements Traceability

| Requirement / AT | Design Element | Test / Gate |
|---|---|---|
| MUST porte das 3 skills / AT-002, AT-003 | Manifest 1–13 | `test_matriz_new_session.py`, `skill-lint.py` |
| MUST 105 testes em `tests/` / AT-001, AT-011…AT-014 | Decision 1; manifest 16–18 | `test_checar.py`, `test_alarme.py`, `test_inventario.py` |
| MUST `--segredo` / AT-004…AT-006 | Decision 2; Pattern 1 | `test_checar.py` |
| MUST `doctor` / AT-007…AT-009 | Decision 3; Pattern 2 | `test_sdd_open.py` |
| SHOULD hook sem cabeçalho / AT-010 | Decision 5; Pattern 3 | `test_alarme.py` |
| SHOULD matriz / AT-015 | Decision 4; Pattern 4 | `test_matriz_new_session.py` |
| MUST `new-session` 1.1.0 / AT-016 | Manifest 14; Data Flow | `test_matriz_new_session.py` |
| AT-017 | Decision 6; Pattern 5 | Verify Gate (publish-gate `ci`) |
| AT-018 | Versões em 2, 5, 6, 7, 13, 14 | `check-versions.py --base v2.2.1 --base-obrigatoria` |
| AT-019 | Scripts portados sem sintaxe nova | `test_sdd_open.py` (`bash -n` nas cópias) |
| MUST sem regressão / AT-020 | Nenhum arquivo de `sdd/`, `scripts/publish-gate*`, `.github/` muda | suíte da F1 + `git diff v2.2.1` vazio |
| MUST sabotagem / AT-021 | Pattern 6 | BUILD_REPORT |

---

## Risks and Mitigations

| Risk | Impact | Mitigation | Residual Risk |
|---|---|---|---|
| Extrair `dado_exposto()` muda o modo normal | Regressão no diagnóstico completo | Os 53 testes portados rodam antes e depois da extração | Baixo |
| Teste portado depende de texto com `exemplo.com`/`npx` | Teste vermelho por mudança de redação | Ajustar o teste no mesmo commit, com a justificativa no BUILD_REPORT | Baixo |
| `$BASH` vazio ou não-bash ao rodar o `doctor` | `--segredo` não roda | `doctor` já roda dentro de bash (`set -uo pipefail`, `BASH_VERSINFO`); `$BASH` é sempre definido pelo bash | Baixo |
| Agente não segue a tabela/descoberta da `new-session` | Comportamento diferente do contrato | AT-015/AT-016 garantem o texto; A-003 do DEFINE registra o limite | Médio (aceito) |
| Suíte ~2,5 min | Gate e CI mais lentos | Decision 7 | Aceito |
| skill-lint: `description` da `sdd-iniciar-repo` com 46 caracteres de folga | Reprovação se a adaptação alongar | Adaptação não toca a `description`, ou só encurta | Baixo |

---

## Advisor Ledger

None — no formal external design review.

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | 2026-10-29 | SDD Design by RDD | Initial version |
| 1.1 | 2026-10-29 | SDD Build by RDD | Item 22: o teste da F1 `test_skill_lint.py` fixava 13 skills; com as 3 portadas são 16. Drift registrado no BUILD_REPORT; Roberto escolheu fixar 16 e renomear o teste |

---

## Next Step

Execute o **SDD Build by RDD**.
