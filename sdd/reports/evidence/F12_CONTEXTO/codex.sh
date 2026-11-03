#!/usr/bin/env bash
# Prova da F12 no Codex CLI (P2, DEFINE AT-020): 2 execuções reais do `codex exec` numa cópia temporária e
# commitada do repositório (git archive HEAD). CODEX_HOME temporário só com o auth.json e HOME temporário: nenhuma
# skill, AGENTS.md ou plugin de fora do pacote é carregado. O prompt diz que não há subagente nem colaborador
# (o Codex 0.163 abre colaborador mesmo com --disable multi_agent; medido na F9). Cada log tem `$ comando`, a saída
# inteira e `[exit=N]`, e termina com as conferências do critério.
#   (a) codex-cartografo-40.log — sdd-define sobre um BRAINSTORM de pedidos, com sdd/patterns/dominio.md (cópia da
#       fixture): passa sse o despacho do cartógrafo saiu 40, há RESULTADO: AGUARDANDO_HUMANO e o brief existe.
#   (b) codex-revisor-40.log — só o passo 11 sobre um DEFINE de cobrança: passa sse o despacho do revisor saiu 40,
#       o brief existe e o verify-gate.sh sobre o DEFINE da cópia sai 5 com GOVERNANÇA NÃO REVISADA e as 2 saídas.
set -u
cd "$(git rev-parse --show-toplevel)" || exit 64
E="$PWD/sdd/reports/evidence/F12_CONTEXTO"
BASE="$(mktemp -d)"
CH="$BASE/codex-home"; H="$BASE/home"; mkdir -p "$CH" "$H"
cp "$HOME/.codex/auth.json" "$CH/auth.json" || exit 64
MODELO="$(sed -n 's/^model = "\(.*\)"$/\1/p' "$HOME/.codex/config.toml" | head -1)"

copia() { # $1 = pasta: cópia do HEAD com sdd/config.yaml (camada api) e o mapa de domínios de fixture
  mkdir -p "$1" && git archive HEAD | tar -x -C "$1" || exit 64
  cp sdd/config.example.yaml "$1/sdd/config.yaml"
  /usr/bin/python3 -B - "$1/sdd/config.yaml" <<'PY'
import sys
p = sys.argv[1]
s = open(p, encoding="utf-8").read().replace('  api: ""', '  api: "src/api/**"')
open(p, "w", encoding="utf-8").write(s)
PY
  mkdir -p "$1/sdd/patterns" "$1/sdd/features"
  cp sdd/fixtures/contexto/dominio.md "$1/sdd/patterns/dominio.md"
}
commita() { ( cd "$1" && git init -q 2>/dev/null; git add -A && git -c user.name=prova -c user.email=prova@example.com commit -q -m "$2" ) || exit 64; }

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

SEM_SUB="Nesta sessão não há subagente nem colaborador disponível: você não consegue abrir um papel fresco sozinho, então siga o caminho que a skill dá para esse caso (sessão nova). Esta execução não é interativa: em toda pergunta de decisão, escolha a opção recomendada e continue sem esperar resposta; quando a skill mandar parar, pare."

if [ -z "${SO_B:-}" ]; then
# (a) passo 1.5: cartógrafo
A="$BASE/a"; copia "$A"
cp sdd/fixtures/contexto/INPUT_FIXTURE_PEDIDOS.md "$A/sdd/features/BRAINSTORM_PEDIDOS.md"
commita "$A" "cópia para a prova da F12 (a)"
roda codex-cartografo-40.log "$A" "Siga a skill do projeto em .agents/skills/sdd-define/SKILL.md (leia o arquivo inteiro e as referências que ela manda ler) para gerar sdd/features/DEFINE_PEDIDOS.md a partir de sdd/features/BRAINSTORM_PEDIDOS.md, começando pelo passo 1.5 (contexto de domínio). $SEM_SUB" --disable multi_agent
{
  echo "── conferência do critério (a)"
  # o exit 40 de verdade: a linha do transcript do Codex. Só o texto AGUARDANDO_HUMANO não prova (o agente lê o
  # código-fonte e ele entra no log): foi assim que a execução sobre 3ebeeea deu um PASS falso.
  grep -nE '^ exited 40 in ' "$E/codex-cartografo-40.log"; ok1=$?
  grep -c 'RESULTADO: AGUARDANDO_HUMANO' "$E/codex-cartografo-40.log"; ok2=$?
  test -f "$A/sdd/reports/briefs/BRIEF_cartografo_PEDIDOS.md"; ok3=$?
  echo "test -f sdd/reports/briefs/BRIEF_cartografo_PEDIDOS.md → $ok3"
  [ "$ok3" = 0 ] && sed -n '1,12p' "$A/sdd/reports/briefs/BRIEF_cartografo_PEDIDOS.md"
  [ "$ok1" = 0 ] && [ "$ok2" = 0 ] && [ "$ok3" = 0 ] && echo "AT-020a: PASS" || echo "AT-020a: FAIL"
} >> "$E/codex-cartografo-40.log" 2>&1
fi

# (b) passo 11: revisor de governança sobre um DEFINE de cobrança
B="$BASE/b"; copia "$B"
cp sdd/fixtures/DEFINE_FIXTURE_GOVERNANCA.md "$B/sdd/features/DEFINE_PEDIDOS.md"
commita "$B" "cópia para a prova da F12 (b)"
roda codex-revisor-40.log "$B" "O DEFINE desta feature já está gravado em sdd/features/DEFINE_PEDIDOS.md. Siga a skill do projeto em .agents/skills/sdd-define/SKILL.md e execute somente o passo 11 (Governança) sobre esse DEFINE, sem refazer os outros passos. $SEM_SUB" --disable multi_agent
{
  echo "── conferência do critério (b)"
  grep -nE '^ exited 40 in ' "$E/codex-revisor-40.log"; ok1=$?
  grep -c 'RESULTADO: AGUARDANDO_HUMANO' "$E/codex-revisor-40.log"; ok2=$?
  test -f "$B/sdd/reports/briefs/BRIEF_revisor-governanca_PEDIDOS.md"; ok3=$?
  echo "test -f sdd/reports/briefs/BRIEF_revisor-governanca_PEDIDOS.md → $ok3"
  [ "$ok3" = 0 ] && sed -n '1,12p' "$B/sdd/reports/briefs/BRIEF_revisor-governanca_PEDIDOS.md"
  echo "\$ bash sdd/bin/verify-gate.sh sdd/features/DEFINE_PEDIDOS.md (na cópia)"
  g="$(cd "$B" && SDD_TRACE=off bash sdd/bin/verify-gate.sh sdd/features/DEFINE_PEDIDOS.md 2>&1)"; grc=$?
  printf '%s\n[exit=%s]\n' "$g" "$grc"
  printf '%s' "$g" | grep -q 'GOVERNANÇA NÃO REVISADA'; ok4=$?
  printf '%s' "$g" | grep -q 'rode só o passo 11 (Governança)'; ok5=$?
  # o marcador gravado ANTES do despacho distingue da v2.3.1 (a linha pendente da fixture já dava 5 lá)
  grep -n 'NEEDS CLARIFICATION: governança não rodou' "$B/sdd/features/DEFINE_PEDIDOS.md"; ok6=$?
  [ "$ok1" = 0 ] && [ "$ok2" = 0 ] && [ "$ok3" = 0 ] && [ "$grc" = 5 ] && [ "$ok4" = 0 ] && [ "$ok5" = 0 ] && [ "$ok6" = 0 ] && echo "AT-020b: PASS" || echo "AT-020b: FAIL"
} >> "$E/codex-revisor-40.log" 2>&1

rm -rf "${BASE:?}"
grep -h '^AT-020[ab]:' "$E/codex-cartografo-40.log" "$E/codex-revisor-40.log" 2>/dev/null
