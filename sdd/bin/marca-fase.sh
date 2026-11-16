#!/usr/bin/env bash
# marca-fase.sh — grava a marca de início ou de fim de uma fase do SDD no trace da feature, para o
# custo-feature.sh dividir o custo das sessões do agente entre as fases. Doc: docs/adversarial-review.md
# (seção custo-feature) e sdd/templates/fragments/MARCA_FASE.md.
#
# Por que existe: o custo de uma sessão só pode ser atribuído a uma fase se alguém disser quando a fase começou
# e terminou. A marca é gravada pela skill de fase, com o horário, no mesmo arquivo em que o verify-gate.sh já
# grava as voltas do gate: um arquivo por feature com tudo o que o contador lê.
#
# USO-INICIO
#   marca-fase.sh inicio|fim <fase> <FEATURE>
#       fase:    a-z, 0-9 e hífen, começando por letra, até 40 caracteres (brainstorm, define, ux-review,
#                design, build, release)
#       FEATURE: A-Z, a-z, 0-9, _, . e -, até 80 caracteres (o feature_id dos artefatos)
#       grava 1 linha JSONL em ${SDD_TRACE_DIR:-sdd/traces}/<FEATURE>.jsonl, na raiz do repositório git
#       (fora de um repositório, na pasta atual): {"ts","feature","src":"fase","evento","fase"}
#       nunca apaga nem reescreve o arquivo; SDD_TRACE=off desliga (a mesma chave do verify-gate.sh)
#       0 MARCADO (ou DESLIGADO com SDD_TRACE=off) · 64 uso: evento, fase ou feature inválidos (com tabulação,
#         quebra de linha ou outro caractere de controle, nada é gravado), ou a pasta do trace não aceita escrita
# USO-FIM
#
# ⚠️ bash 3.2 (o /bin/bash do macOS) · sem Python.

set -u

uso() {
  echo "🛑 marca-fase: $1" >&2
  printf 'RESULTADO: PAROU\n→ rode `marca-fase.sh --help` para ver o uso; nada foi gravado.\n' >&2
  exit 64
}

case "${1:-}" in
  -h|--help)
    sed -n '/^# USO-INICIO$/,/^# USO-FIM$/p' "$0" | sed '1d;$d;s/^# \{0,1\}//'
    exit 0 ;;
esac

[ "$#" -eq 3 ] || uso "são 3 argumentos: inicio|fim <fase> <FEATURE>"
evento="$1"; fase="$2"; feature="$3"
case "${evento}" in inicio|fim) ;; *) uso "o evento é inicio ou fim (veio outra coisa)" ;; esac
# Os dois padrões barram aspas, barra invertida, espaço e todo caractere de controle: a linha JSON sai sem escape
# e ninguém forja uma linha nova no trace (S17). LC_ALL=C: a faixa a-z não aceita letra acentuada de outro locale.
printf '%s' "${fase}" | LC_ALL=C grep -Eq '^[a-z][a-z0-9-]{0,39}$' \
  && [ "$(printf '%s' "${fase}" | wc -l | tr -d ' ')" = "0" ] \
  || uso "fase inválida: só a-z, 0-9 e hífen, começando por letra, até 40 caracteres"
printf '%s' "${feature}" | LC_ALL=C grep -Eq '^[A-Za-z0-9_.-]{1,80}$' \
  && [ "$(printf '%s' "${feature}" | wc -l | tr -d ' ')" = "0" ] \
  || uso "feature inválida: só A-Z, a-z, 0-9, _, . e -, até 80 caracteres, sem espaço, tabulação ou quebra de linha"

if [ "${SDD_TRACE:-on}" = "off" ]; then
  printf 'RESULTADO: DESLIGADO\n→ SDD_TRACE=off: nenhuma marca gravada.\n'
  exit 0
fi

raiz="$(git rev-parse --show-toplevel 2>/dev/null)" || raiz=""
[ -n "${raiz}" ] || raiz="$(pwd)"
dir="${SDD_TRACE_DIR:-sdd/traces}"
case "${dir}" in /*|[A-Za-z]:*) ;; *) dir="${raiz}/${dir}" ;; esac
mkdir -p "${dir}" 2>/dev/null || uso "não consegui criar a pasta do trace (${dir})"
ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
printf '{"ts":"%s","feature":"%s","src":"fase","evento":"%s","fase":"%s"}\n' "${ts}" "${feature}" "${evento}" "${fase}" \
  >> "${dir}/${feature}.jsonl" 2>/dev/null || uso "não consegui gravar em ${dir}/${feature}.jsonl"
printf 'MARCADO: %s %s %s %s\n' "${evento}" "${fase}" "${feature}" "${ts}"
printf 'RESULTADO: MARCADO\n→ siga com a fase; o custo-feature.sh lê esta marca.\n'
exit 0
