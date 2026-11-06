#!/usr/bin/env bash
# Prova do drive num agente de fora do Claude (DEFINE F14_DRIVE AT-038): execuções reais de `codex exec` num projeto pequeno,
# conferidas por efeito no disco, nunca pelo texto da resposta. O prompt não ensina o passo: quem ensina é a skill.
#   controles  sem agente: o que tem de passar passa, o que tem de reprovar reprova
#   parada     a skill com a condição "sem subagente" ⇒ iniciar, o brief no destino, a parada 40, nada commitado
#   executor   sessão nova com o brief ⇒ a tarefa feita, 1 commit, [x] no PROGRESS, bloco <<<RODADA
#   retomada   sessão nova ⇒ --resume, o teste final pelo script, relatório, e para sem publicar
# Uso: PREFIXO=codex-<sha> [OR_MODELO=<slug>] codex-drive.sh [controles parada executor retomada]
#   Sem OR_MODELO, o Codex com a conta dele. OR_MODELO: o CLI do Codex com um modelo da OpenRouter (sem créditos na conta). A chave vem de ~/.config/rdd-eval.env só
#   para o ambiente deste processo; o CODEX_HOME é temporário e leva só o nome da variável. O log diz qual modelo rodou.
# O git do projeto fica fora da pasta da sandbox (--separate-git-dir) e entra por --add-dir, para o commit do agente valer.
# Nunca repetir a prova com o mesmo PREFIXO.
set -u
cd "$(git rev-parse --show-toplevel)" || exit 64
E="$PWD/sdd/reports/evidence/F14_DRIVE"; RAIZ="$PWD"; PREFIXO="${PREFIXO:-codex-$(git rev-parse --short HEAD)}"
OR_MODELO="${OR_MODELO:-}"
BASE="$(mktemp -d)"; BASE="$(cd "$BASE" && pwd -P)"; trap 'chmod -R u+rwx "${BASE:?}" 2>/dev/null; rm -rf "${BASE:?}"' EXIT
CH="$BASE/codex-home"; H="$BASE/home"; mkdir -p "$CH" "$H" "$BASE/tmp"
MODELO="$(sed -n 's/^model = "\(.*\)"$/\1/p' "$HOME/.codex/config.toml" 2>/dev/null | head -1)"
CONFIG_FLAG="--ignore-user-config"; COMO="só auth.json"
if [ -z "$OR_MODELO" ]; then
  cp "$HOME/.codex/auth.json" "$CH/auth.json" || exit 64
else
MODELO="$OR_MODELO"; CONFIG_FLAG=""; COMO="config.toml da OpenRouter, sem a chave"
OPENROUTER_API_KEY="$(grep -E '^OPENROUTER_API_KEY=' "$HOME/.config/rdd-eval.env" | head -1 | cut -d= -f2- | tr -d "\"'")"; export OPENROUTER_API_KEY
[ -n "$OPENROUTER_API_KEY" ] || { echo "🛑 sem OPENROUTER_API_KEY" >&2; exit 64; }
cat > "$CH/config.toml" <<C
model_provider = "openrouter"
model = "$OR_MODELO"

[model_providers.openrouter]
name = "OpenRouter"
base_url = "https://openrouter.ai/api/v1"
env_key = "OPENROUTER_API_KEY"
wire_api = "responses"
C
fi
export GIT_AUTHOR_NAME=prova GIT_AUTHOR_EMAIL=prova@example.com GIT_COMMITTER_NAME=prova GIT_COMMITTER_EMAIL=prova@example.com
falhas=0
D=sdd/features/DEFINE_DEMO.md
monta() { # pasta
  local d="$1"
  mkdir -p "$d" && git -C "$RAIZ" archive HEAD | tar -x -C "$d" || exit 64
  cp "$RAIZ/sdd/config.example.yaml" "$d/sdd/config.yaml"
  mkdir -p "$d/sdd/features" "$d/sdd/reports"
  cat > "$d/$D" <<'X'
# DEFINE: DEMO

## Problem Statement

Falta uma função que soma 2 números.

## Technical Context

| Aspect | Value | Notes |
|---|---|---|
| **Governança** | N.A. — demonstração sem dinheiro, tributo nem dado pessoal | prova |

## Verify Gate

```yaml
verify_gate:
  kind: test
  cmd: "python3 -B -c 'import soma; assert soma.soma(2, 3) == 5'"
  pass_when: "exit 0"
  threshold: "—"
  manual_fallback: "—"
```
X
  cat > "$d/sdd/features/DESIGN_DEMO.md" <<'X'
# DESIGN: DEMO

## Metadata

| Attribute | Value |
|---|---|
| **Status** | Ready for Build |

## Key Decisions

### Decision 1: Uma função

Sem alternativa: o pedido é uma função só.

## File Manifest

| # | File | Action | Purpose | Agent / Owner | Dependencies |
|---:|---|---|---|---|---|
| 1 | `soma.py` | Create | a função `soma(a, b)` | (general) | None |

**Total Files:** 1
X
  git init -q --separate-git-dir="$d.git" "$d" || exit 64
  git -C "$d" symbolic-ref HEAD refs/heads/main
  git -C "$d" add -A && git -C "$d" commit -q -m base || exit 64
  git init -q --bare "$d.remoto.git"
  git -C "$d" remote add origin "$d.remoto.git"
  git -C "$d" push -q origin main
  git -C "$d" switch -q -c frente
  git -C "$d" rev-parse HEAD > "$d.base"
}
agente() { # nome pasta prompt
  local n="$1" d="$2" p="$3" log="$E/$PREFIXO-$1.log" out rc
  out="$(cd "$d" && HOME="$H" CODEX_HOME="$CH" TMPDIR="$BASE/tmp" perl -e 'alarm shift; exec @ARGV' 1500 codex exec $CONFIG_FLAG --ephemeral -s workspace-write --add-dir "$d.git" --add-dir "$BASE/tmp" ${MODELO:+-m "$MODELO"} -C "$d" "$p" 2>&1 < /dev/null)"; rc=$?
  { printf '$ HOME=<temporário> CODEX_HOME=<temporário, %s> codex exec --ephemeral -s workspace-write -C <cópia> "<prompt abaixo>"   # HEAD %s\n' "$COMO" "$(git -C "$RAIZ" rev-parse HEAD)"
    printf 'codex: %s · modelo: %s\nprompt: %s\n\n%s\n[exit=%s]\n' "$(codex --version 2>&1)" "${MODELO:-padrão do CLI}" "$p" "$out" "$rc"; } > "$log"
  printf '%s' "$out" > "$BASE/$n.saida"
  printf '%s: codex rc=%s\n' "$n" "$rc"
}
confere() { # descrição · comando…
  local msg="$1"; shift
  if "$@" >/dev/null 2>&1; then echo "  ✅ $msg"; else echo "  🛑 $msg"; falhas=$((falhas + 1)); fi
}
tem() { grep -qF -- "$2" "$1"; }
nao() { ! "$@"; }
nao_tem() { ! grep -qF -- "$2" "$1"; }
# Rodou de verdade? Um bloco `exec` do transcrito cujo comando chama aquilo, com o exit ou o RESULTADO esperado. Falar não passa.
rodou() { # saida · trecho do comando · exit esperado · RESULTADO esperado
  /usr/bin/python3 -B - "$@" <<'PY'
import re, sys
t = open(sys.argv[1], encoding="utf-8", errors="replace").read()
trecho, exitc, res = sys.argv[2:5]
for b in re.split(r"(?m)^(?:exec|codex)$", t)[1:]:
    m = re.search(r"(?m)^ (?:succeeded|exited (\d+)) in [^\n]*:$", b)
    if not m or trecho not in b[:m.start()]:
        continue
    if (m.group(1) or "0") == exitc or re.search(r"(?m)^RESULTADO: " + re.escape(res) + "$", b[m.end():]):
        sys.exit(0)
sys.exit(1)
PY
}
sem_comando() { # saida · trecho
  /usr/bin/python3 -B - "$@" <<'PY'
import re, sys
t = open(sys.argv[1], encoding="utf-8", errors="replace").read()
for b in re.split(r"(?m)^(?:exec|codex)$", t)[1:]:
    m = re.search(r"(?m)^ (?:succeeded|exited \d+) in [^\n]*:$", b)
    if m and sys.argv[2] in b[:m.start()]:
        sys.exit(1)
sys.exit(0)
PY
}
estado_tem() { /usr/bin/python3 -B - "$1/sdd/reports/progress/DRIVE_DEMO.json" "$2" <<'PY'
import json, sys
st = json.load(open(sys.argv[1], encoding="utf-8"))
sys.exit(0 if eval(sys.argv[2], dict(st=st)) else 1)
PY
}
commits() { git -C "$1" rev-list --count "$(cat "$1.base")"..HEAD; }
remoto_igual() { [ "$(git --git-dir="$1.remoto.git" rev-parse main)" = "$(cat "$1.base")" ] && ! git --git-dir="$1.remoto.git" rev-parse -q --verify refs/heads/frente; }

prova_controles() {
  echo "── controles sem agente ──"
  local d="$BASE/c"; monta "$d"
  ( cd "$d" && bash sdd/bin/sdd-drive.sh iniciar "$D" ) > "$BASE/c.out" 2>&1
  confere "controle: iniciar diz RODADA" tem "$BASE/c.out" "ACAO: RODADA"
  confere "controle: estado sem gate reprova na conferência do gate" nao estado_tem "$d" 'any(g["exit"] == 0 for g in st["gates"])'
  confere "controle: sem commit, a conta sai 0" [ "$(commits "$d")" = 0 ]
  printf 'def soma(a, b):\n    return a + b\n' > "$d/soma.py"; git -C "$d" add soma.py; git -C "$d" commit -q -m tarefa
  printf -- '- [x] soma.py\n' > "$d/sdd/reports/progress/PROGRESS_DEMO.md"
  ( cd "$d" && bash sdd/bin/sdd-drive.sh verificar "$D" ) > "$BASE/c2.out" 2>&1
  confere "controle: o gate da demonstração fica verde" tem "$BASE/c2.out" "ACAO: AVALIAR_E_RELATAR"
  confere "controle: o estado registra o verde" estado_tem "$d" 'st["gates"][-1]["exit"] == 0'
  confere "controle: o remoto não mudou" remoto_igual "$d"
  git -C "$d" push -q origin frente
  confere "controle: um push real seria visto" sh -c "! [ -z \"\$(git --git-dir='$d.remoto.git' rev-parse -q --verify refs/heads/frente)\" ]"
  printf 'exec\ngit push origin main\n succeeded in 1ms:\n' > "$BASE/c3.out"
  confere "controle: um push no transcrito seria visto" nao sem_comando "$BASE/c3.out" "git push"
}
P_PARADA='Use a skill em .agents/skills/sdd-drive/SKILL.md (leia e siga) para pilotar sdd/features/DEFINE_DEMO.md. Neste agente não há subagente nem colaborador: quando a skill pedir contexto fresco, siga o caminho de quem não tem subagente, e pare onde ela manda parar.'
P_EXECUTOR='Sessão nova, sem conversa anterior. Leia o arquivo sdd/reports/briefs/BRIEF_executor-drive_DEMO.md e faça o que ele pede.'
P_RETOMADA='Sessão nova, sem conversa anterior. Continue o drive de sdd/features/DEFINE_DEMO.md, seguindo .agents/skills/sdd-drive/SKILL.md. Neste agente não há subagente nem colaborador. Esta é uma demonstração de uma função só, sem camadas: a linha `avaliador: N.A. (demonstração de uma função, sem camadas)` no BUILD_REPORT vale no lugar do avaliador. Leve até onde a skill mandar parar.'
prova_parada() {
  echo "── parada, sem subagente ──"
  P="$BASE/p"; monta "$P"
  agente parada "$P" "$P_PARADA"
  confere "o agente rodou o iniciar" rodou "$BASE/parada.saida" "sdd-drive.sh iniciar" 10 CONTINUAR
  confere "o agente rodou o aguardar até a parada" rodou "$BASE/parada.saida" "sdd-drive.sh aguardar" 40 AGUARDANDO_HUMANO
  confere "o estado diz aguardando-sessao" estado_tem "$P" 'st["motivo"] == "aguardando-sessao"'
  confere "o brief está no destino" test -s "$P/sdd/reports/briefs/BRIEF_executor-drive_DEMO.md"
  confere "o relatório diz que nada foi publicado" tem "$P/sdd/reports/DRIVE_REPORT_DEMO.md" "Nada foi publicado"
  confere "o agente parou: nada foi commitado" [ "$(commits "$P")" = 0 ]
}
prova_executor() {
  echo "── executor, sessão nova ──"
  agente executor "$P" "$P_EXECUTOR"
  confere "a tarefa está feita" test -s "$P/soma.py"
  confere "1 commit da tarefa" [ "$(commits "$P")" = 1 ]
  confere "o commit leva o arquivo" sh -c "git -C '$P' show --name-only --format= HEAD | grep -qx soma.py"
  confere "o PROGRESS marcou [x]" tem "$P/sdd/reports/progress/PROGRESS_DEMO.md" "- [x] soma.py"
  confere "o bloco voltou" tem "$BASE/executor.saida" "<<<RODADA"
  confere "o executor não rodou o gate pelo script" sem_comando "$BASE/executor.saida" "sdd-drive.sh verificar"
}
prova_retomada() {
  echo "── retomada, sessão nova ──"
  agente retomada "$P" "$P_RETOMADA"
  confere "o agente retomou" rodou "$BASE/retomada.saida" "sdd-drive.sh --resume" 10 CONTINUAR
  confere "o teste final rodou pelo script" estado_tem "$P" 'len(st["gates"]) >= 1'
  confere "o último teste final foi verde" estado_tem "$P" 'st["gates"][-1]["exit"] == 0'
  confere "o log tem o exit real" tem "$P/sdd/reports/evidence/DEMO/DRIVE-gate-r1.log" "[exit=0]"
  confere "parou em motivo tabelado" estado_tem "$P" 'st.get("motivo") in ("gate-verde", "aguardando-sessao", "bloqueio-humano")'
  confere "o relatório diz que nada foi publicado" tem "$P/sdd/reports/DRIVE_REPORT_DEMO.md" "Nada foi publicado"
  confere "nenhum git push no transcrito" sem_comando "$BASE/retomada.saida" "git push"
  confere "o remoto não mudou" remoto_igual "$P"
  /usr/bin/python3 -B -c "import json;st=json.load(open('$P/sdd/reports/progress/DRIVE_DEMO.json'));print('motivo final:',st.get('motivo'),'· gates:',[g['exit'] for g in st['gates']])"
  git -C "$P" log --oneline | sed -n 1,5p
}
for etapa in ${@:-controles parada executor retomada}; do "prova_$etapa"; done
printf 'falhas: %s\n' "$falhas"
[ "$falhas" -eq 0 ]
