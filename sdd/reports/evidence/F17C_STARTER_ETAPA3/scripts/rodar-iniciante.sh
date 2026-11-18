#!/usr/bin/env bash
# rodar-iniciante.sh <pasta das skills geradas> <pasta das skills congeladas v1.5.18>: por skill (define, design,
# build), 3 execuções da gerada e 3 do controle ao mesmo tempo; um log por execução
set -u
cd "$(dirname "$0")/.." || exit 64
G="$1"; C="$2"
for s in ${SKILLS:-sdd-define sdd-design sdd-build}; do
  for n in 1 2 3; do
    for t in g c; do
      if [ "$t" = g ]; then d="$G/$s"; else d="$C/$s"; fi
      ( python3 -I scripts/iniciante2.py "$d" INICIANTE-roteiro.json "$s" "$t-$n" "INICIANTE-$s-${SERIE:+$SERIE-}$t-$n.log"; echo "$s ${SERIE:+$SERIE-}$t-$n rc=$?" ) &
    done
  done
  wait
done
