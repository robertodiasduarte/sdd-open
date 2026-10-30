#!/usr/bin/env bash
# test-baseline.sh — só falha de teste NOVA aborta o build; falha já conhecida fica registrada.
#
# Roda o comando de teste do projeto (`project.test_cmd` do sdd/config.yaml, ou --cmd), extrai os
# identificadores das falhas e compara com sdd/baselines/tests.txt (um id por linha; `#` comenta).
# Formatos reconhecidos: unittest, pytest, jest, vitest, go test, deno test. Saída que nenhum deles
# reconhece com o comando falhando é INCONCLUSIVO, nunca verde.
#
# Uso:
#   sdd/bin/test-baseline.sh                       # roda project.test_cmd (execução completa)
#   sdd/bin/test-baseline.sh --cmd '<comando>'     # outro comando (execução parcial: não poda o baseline)
#   sdd/bin/test-baseline.sh --touched [--base <ref>]  # só aborta por falha nova cujo id cita um arquivo
#                                                  # de teste tocado (test_*, *_test.*, *.test.*, *.spec.*)
#   sdd/bin/test-baseline.sh --aceitar '<id>'      # registra uma falha como conhecida (decisão humana)
#
# Exit: 0 só falhas conhecidas (ou PULADO: test_cmd vazio) · 2 falha nova · 3 INCONCLUSIVO · 64 uso.
# Só na execução completa sem falha nova o id que sarou sai do baseline (e é listado).
# ⚠️ bash 3.2 + python3 (stdlib). Faz parte do contrato da fase Build (passo 5b da sdd-build).

set -uo pipefail

uso() {
  echo "🛑 ${1}" >&2
  printf 'RESULTADO: ERRO DE USO\n→ uso: sdd/bin/test-baseline.sh [--cmd <comando>] [--touched [--base <ref>]] [--aceitar <id>]\n' >&2
  exit 64
}

CMD=""; CMD_DADO=0; TOUCHED=0; BASE=""; ACEITAR=""; ACEITAR_DADO=0
while [ $# -gt 0 ]; do
  case "${1}" in
    --cmd)     [ $# -ge 2 ] && [ -n "${2}" ] || uso "--cmd exige um comando"; CMD="${2}"; CMD_DADO=1; shift 2 ;;
    --touched) TOUCHED=1; shift ;;
    --base)    [ $# -ge 2 ] && [ -n "${2}" ] || uso "--base exige uma ref"; BASE="${2}"; shift 2 ;;
    --aceitar) [ $# -ge 2 ] && [ -n "${2}" ] || uso "--aceitar exige um id"; ACEITAR="${2}"; ACEITAR_DADO=1; shift 2 ;;
    -h|--help) sed -n '2,19p' "$0"; exit 64 ;;
    *)         uso "argumento inesperado: ${1}" ;;
  esac
done
command -v python3 >/dev/null 2>&1 || { echo "⚠️  python3 ausente"; printf 'RESULTADO: INCONCLUSIVO\n→ instale python3 >= 3.9.\n'; exit 3; }

ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || ROOT="$(pwd)"
cd "${ROOT}" || exit 64
BASELINE="sdd/baselines/tests.txt"

if [ "${ACEITAR_DADO}" = "1" ]; then
  python3 -B - "${BASELINE}" "${ACEITAR}" <<'PY'
import os, sys
arq, novo = sys.argv[1], sys.argv[2].strip()
linhas = open(arq, encoding="utf-8").read().splitlines() if os.path.isfile(arq) else []
if novo in [l.strip() for l in linhas]:
    print("ℹ️  `%s` já está no baseline." % novo)
else:
    os.makedirs(os.path.dirname(arq) or ".", exist_ok=True)
    with open(arq, "a", encoding="utf-8") as fh:
        fh.write(novo + "\n")
    print("✅ aceito: `%s` entrou em %s como falha conhecida." % (novo, arq))
print("RESULTADO: VERDE")
print("→ commite %s junto com o motivo no BUILD_REPORT." % arq)
PY
  exit $?
fi

if [ "${CMD_DADO}" = "0" ]; then
  CMD="$(python3 -B - <<'PY'
import re
try:
    linhas = open("sdd/config.yaml", encoding="utf-8", errors="replace").read().splitlines()
except OSError:
    linhas = []
dentro = False
for l in linhas:
    if re.match(r"^\S", l):
        dentro = l.split("#", 1)[0].strip() == "project:"
        continue
    m = re.match(r"^\s+test_cmd:\s*(.*)$", l) if dentro else None
    if m:
        v = m.group(1).strip()
        if v[:1] in "\"'" and v[0] in v[1:]:
            v = v[1:v.rindex(v[0])]
        else:
            v = v.split(" #", 1)[0].strip()
        print(v)
        break
PY
)"
  if [ -z "${CMD}" ]; then
    echo "ℹ️  project.test_cmd vazio em sdd/config.yaml: não há comando de teste para comparar."
    printf 'RESULTADO: PULADO\n→ preencha project.test_cmd (ou passe --cmd) para usar o baseline de testes.\n'
    exit 0
  fi
fi

TOCADOS=""
if [ "${TOUCHED}" = "1" ]; then
  if [ -z "${BASE}" ]; then
    DB="$(sed -n 's/^[[:space:]]*default_branch:[[:space:]]*//p' sdd/config.yaml 2>/dev/null | head -1 | sed 's/[[:space:]]*#.*$//' | tr -d "\"' ")"
    BASE="origin/${DB:-main}"
  fi
  TOCADOS="$( { git -c core.quotepath=false diff --name-only "${BASE}...HEAD" \
                && git -c core.quotepath=false diff --name-only HEAD \
                && git -c core.quotepath=false ls-files --others --exclude-standard; } 2>/dev/null)" \
    || uso "--touched: git diff ${BASE}...HEAD falhou (base inválida?)"
fi

MODO="completo"
[ "${CMD_DADO}" = "1" ] && MODO="parcial"
[ "${TOUCHED}" = "1" ] && MODO="touched"

SAIDA="$(mktemp 2>/dev/null || mktemp -t testbase)" || exit 64
trap 'rm -f "${SAIDA}"' EXIT
echo "▶ testes: ${CMD}"
bash -c "${CMD}" > "${SAIDA}" 2>&1
RC=$?

python3 -B - "${SAIDA}" "${RC}" "${BASELINE}" "${MODO}" "${TOCADOS}" <<'PY'
import os
import re
import sys

saida, rc, arq, modo, tocados = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4], sys.argv[5]
txt = open(saida, encoding="utf-8", errors="replace").read()

ids = []


def add(i):
    i = i.strip()
    if i and i not in ids:
        ids.append(i)


# unittest: "FAIL: test_x (mod.Classe)" (3.9–3.10) ou "FAIL: test_x (mod.Classe.test_x)" (3.11+)
for m in re.finditer(r"^(?:FAIL|ERROR): (\S+) \(([^)\s]+)\)\s*$", txt, re.M):
    nome, onde = m.group(1), m.group(2)
    add(onde if onde.endswith("." + nome) else onde + "." + nome)
# pytest: "FAILED caminho::teste - msg" / "ERROR caminho - msg"
for m in re.finditer(r"^(?:FAILED|ERROR) (\S+\.py(?:::\S+)?)(?: - .*)?$", txt, re.M):
    add(m.group(1))
# jest: "● Suite › teste"
for m in re.finditer(r"^\s*● (.+?)\s*$", txt, re.M):
    if not m.group(1).startswith("Console"):
        add(m.group(1))
# vitest: " FAIL  arquivo.test.ts > suite > teste"
for m in re.finditer(r"^\s*(?:FAIL|×|✗)\s+(\S+\.(?:test|spec)\.[cm]?[jt]sx?)\s+>\s+(.+?)\s*$", txt, re.M):
    add(m.group(1) + " > " + m.group(2))
# go: "--- FAIL: TestX (0.00s)"
for m in re.finditer(r"^\s*--- FAIL: (\S+)", txt, re.M):
    add(m.group(1))
# go: pacote que nem compilou ("FAIL\texemplo/x [build failed]") — os testes dele não rodaram
for m in re.finditer(r"^FAIL\s+(\S+)\s+\[(build|setup) failed\]", txt, re.M):
    add("%s failed: %s" % (m.group(2), m.group(1)))
# deno: "nome => ./arquivo.ts:12:6" (bloco de falhas)
for m in re.finditer(r"^(.+?) => (?:\./)?(\S+?):\d+:\d+\s*$", txt, re.M):
    add(m.group(2) + "::" + m.group(1).strip())

linhas = open(arq, encoding="utf-8").read().splitlines() if os.path.isfile(arq) else []
conhecidos = [l.strip() for l in linhas if l.strip() and not l.strip().startswith("#")]


def resultado(palavra, acao, codigo):
    print("RESULTADO: " + palavra)
    print("→ " + acao)
    sys.exit(codigo)


nao_rodou = rc == 127 or re.search(r"command not found|: not found", txt)
if not ids and (rc != 0 or nao_rodou):
    print("⚠️  o comando saiu %d e nenhuma falha foi reconhecida (formatos: unittest, pytest, jest, vitest, go, deno)." % rc)
    if nao_rodou:
        print("⚠️  a ferramenta de teste não rodou (comando não encontrado).")
    if conhecidos:
        print("⚠️  baseline não podado (execução parcial)")
    resultado("INCONCLUSIVO", "rode onde a ferramenta exista, ou confira a saída do comando; isto não é verde.", 3)

novos = [i for i in ids if i not in conhecidos]
velhos = [i for i in ids if i in conhecidos]
fora = []
if modo == "touched":
    tocs = []
    teste = re.compile(r"(^test_|_test\.|\.test\.|\.spec\.|_spec\.|^test\.|Test\.)")
    for t in tocados.splitlines():
        t = t.strip()
        if t and not t.startswith("sdd/") and teste.search(os.path.basename(t)):
            tocs += [t, os.path.splitext(os.path.basename(t))[0]]
    fora = [i for i in novos if not any(t and t in i for t in tocs)]
    novos = [i for i in novos if i not in fora]

for i in novos:
    print("🛑 nova: " + i)
for i in fora:
    print("⚠️  nova, fora do diff (não aborta com --touched): " + i)
for i in velhos:
    print("ℹ️  conhecida: " + i)

if modo == "completo" and not novos:
    sarou = [k for k in conhecidos if k not in ids]
    if sarou:
        manter = [l for l in linhas if l.strip() not in sarou]
        try:
            tmp = arq + ".tmp"
            with open(tmp, "w", encoding="utf-8") as fh:
                fh.write("".join(l + "\n" for l in manter))
            os.replace(tmp, arq)
        except OSError as exc:
            print("⚠️  não consegui reescrever %s (%s): nada foi removido." % (arq, exc))
            resultado("INCONCLUSIVO", "dê permissão de escrita a %s e rode de novo." % arq, 3)
        for k in sarou:
            print("✅ sarou — removido do baseline (commite %s): %s" % (arq, k))
elif conhecidos:
    print("⚠️  baseline não podado (execução parcial)")

if novos:
    print("🛑 %d falha(s) nova(s); %d conhecida(s)." % (len(novos), len(velhos)))
    resultado("VERMELHO", "corrija as falhas novas; aceitar uma é decisão sua: bash sdd/bin/test-baseline.sh --aceitar '<id>'", 2)
print("✅ nenhuma falha nova (%d conhecida(s))." % len(velhos))
resultado("VERDE", "siga para o próximo passo.", 0)
PY
exit $?
