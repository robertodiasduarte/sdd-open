#!/usr/bin/env bash
# Prova da F9 no Codex CLI (P2): 2 execuções reais do `codex exec` numa cópia temporária e commitada do
# repositório (sem .git o codex recusa e o verify-gate --print sai 64). CODEX_HOME temporário só com o
# auth.json e HOME temporário: nenhuma skill, AGENTS.md ou plugin de fora do pacote é carregado. O log de
# cada execução tem `$ comando`, a saída inteira e `[exit=N]`, e termina com as conferências do critério.
#   (a) codex-define-autonomo.log — sdd-define sobre sdd/fixtures/BRAINSTORM_EXEMPLO.md com flow.autonomous:
#       true; passa sse há uma linha começando "✅ DEFINE pronto → seguindo para " e outra começando "→ /sdd-".
#   (b) codex-despacho-40.log — sdd-build 5d com --disable multi_agent e 2 camadas tocadas; passa sse há
#       "[exit=40]", "RESULTADO: AGUARDANDO_HUMANO" e o brief existe na cópia.
set -u
cd "$(git rev-parse --show-toplevel)" || exit 64
E="$PWD/sdd/reports/evidence/F9_FLUXO"
BASE="$(mktemp -d)"
CH="$BASE/codex-home"; H="$BASE/home"; mkdir -p "$CH" "$H"
cp "$HOME/.codex/auth.json" "$CH/auth.json" || exit 64
MODELO="$(sed -n 's/^model = "\(.*\)"$/\1/p' "$HOME/.codex/config.toml" | head -1)"

copia() { # $1=pasta: cópia do HEAD, commitada, com sdd/config.yaml de encadeamento ligado
  mkdir -p "$1" && git archive HEAD | tar -x -C "$1" || exit 64
  cp sdd/config.example.yaml "$1/sdd/config.yaml"
  /usr/bin/python3 -B - "$1/sdd/config.yaml" "${2:-}" <<'PY'
import sys
p, camadas = sys.argv[1], sys.argv[2]
s = open(p, encoding="utf-8").read().replace("  autonomous: false", "  autonomous: true")
if camadas:
    s = s.replace('  api: ""\n  ui: ""', camadas)
open(p, "w", encoding="utf-8").write(s)
PY
  ( cd "$1" && git init -q && git add -A && git -c user.name=prova -c user.email=prova@example.com commit -q -m "cópia para a prova da F9" ) || exit 64
}

roda() { # $1=log $2=pasta $3=prompt [$4…]=opções extras do codex
  local log="$1" dir="$2" prompt="$3"; shift 3
  local out rc
  out="$(cd "$dir" && HOME="$H" CODEX_HOME="$CH" codex exec --ignore-user-config --ephemeral -s workspace-write \
    ${MODELO:+-m "$MODELO"} "$@" -C "$dir" "$prompt" 2>&1 < /dev/null)"; rc=$?
  { printf '$ HOME=<temporário> CODEX_HOME=<temporário, só auth.json> codex exec --ignore-user-config --ephemeral -s workspace-write %s -C <cópia> "<prompt abaixo>"\n' "$*"
    printf 'codex: %s\n' "$(codex --version 2>&1)"
    printf 'prompt: %s\n\n' "$prompt"
    printf '%s\n' "$out"
    printf '[exit=%s]\n' "$rc"; } > "$E/$log"
}

# SO_B=1 roda só o (b) (a 1ª execução do (b) ficou em codex-despacho-subagente.log: com --disable multi_agent
# o Codex 0.163 ainda abriu um colaborador — degrau 1 da escada —, então a condição "sem subagente" vai no prompt).
if [ -z "${SO_B:-}" ]; then
# (a) sdd-define com o encadeamento ligado
A="$BASE/a"; copia "$A"
roda codex-define-autonomo.log "$A" "Siga a skill do projeto em .agents/skills/sdd-define/SKILL.md (leia o arquivo inteiro e as referências que ela manda ler) para gerar sdd/features/DEFINE_EXEMPLO.md a partir de sdd/fixtures/BRAINSTORM_EXEMPLO.md. Esta execução não é interativa: em toda pergunta de decisão, escolha a opção recomendada e continue sem esperar resposta. Ao fechar a fase, siga a subseção '### Fluxo encadeado' do Encerramento da skill. Se o script disser para seguir, escreva a linha de transição e pare aí, sem começar a fase seguinte."
{
  echo "── conferência do critério (a)"
  grep -cE '^✅ DEFINE pronto → seguindo para ' "$E/codex-define-autonomo.log"; ok1=$?
  grep -cE '^→ /sdd-' "$E/codex-define-autonomo.log"; ok2=$?
  grep -c '.agents/skills/sdd-define/SKILL.md' "$E/codex-define-autonomo.log"
  ls "$A/sdd/features/" 2>&1
  [ "$ok1" = 0 ] && [ "$ok2" = 0 ] && echo "AT-030: PASS" || echo "AT-030: FAIL"
} >> "$E/codex-define-autonomo.log" 2>&1
fi

# (b) sdd-build 5d sem subagente, com 2 camadas tocadas pelo manifest da feature de fixture
B="$BASE/b"; copia "$B" '  api: "conta.py"
  ui: "tests/**"'
cp sdd/fixtures/fluxo/DEFINE_pronto.md "$B/sdd/features/DEFINE_X.md" 2>/dev/null || { mkdir -p "$B/sdd/features" && cp sdd/fixtures/fluxo/DEFINE_pronto.md "$B/sdd/features/DEFINE_X.md"; }
cp sdd/fixtures/fluxo/DESIGN_pronto.md "$B/sdd/features/DESIGN_X.md"
printf 'def conta(caminho):\n    with open(caminho, encoding="utf-8") as f:\n        return sum(1 for _ in f)\n' > "$B/conta.py"
mkdir -p "$B/tests" && printf 'import unittest\n' > "$B/tests/test_conta.py"
( cd "$B" && git add -A && git -c user.name=prova -c user.email=prova@example.com commit -q -m "build da feature X" ) || exit 64
roda codex-despacho-40.log "$B" "O build da feature X já foi feito e commitado nesta pasta (DEFINE em sdd/features/DEFINE_X.md, DESIGN em sdd/features/DESIGN_X.md). Siga a skill do projeto em .agents/skills/sdd-build/SKILL.md e as referências que ela cita, e execute somente o passo 5d (avaliador de contexto fresco) para esta feature, ciclo 1. Nesta sessão não há subagente nem colaborador disponível: você não consegue abrir um papel fresco sozinho, então siga o caminho que a skill dá para esse caso. Esta execução não é interativa: não espere resposta; quando a skill mandar parar, pare." --disable multi_agent
{
  echo "── conferência do critério (b)"
  grep -c '\[exit=40\]\|exit 40\|saiu 40\|exit=40' "$E/codex-despacho-40.log"
  grep -c 'RESULTADO: AGUARDANDO_HUMANO' "$E/codex-despacho-40.log"; ok2=$?
  test -f "$B/sdd/reports/briefs/BRIEF_avaliador_X.md"; ok3=$?
  echo "test -f sdd/reports/briefs/BRIEF_avaliador_X.md → $ok3"
  [ "$ok3" = 0 ] && sed -n '1,8p' "$B/sdd/reports/briefs/BRIEF_avaliador_X.md"
  [ "$ok2" = 0 ] && [ "$ok3" = 0 ] && echo "AT-031: PASS" || echo "AT-031: FAIL"
} >> "$E/codex-despacho-40.log" 2>&1

rm -rf "${BASE:?}"
grep -h '^AT-03[01]:' "$E/codex-define-autonomo.log" "$E/codex-despacho-40.log" 2>/dev/null
