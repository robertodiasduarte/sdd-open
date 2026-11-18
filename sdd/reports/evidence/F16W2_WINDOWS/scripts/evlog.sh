#!/usr/bin/env bash
# uso: evlog.sh <arquivo-log> <comando...>  — grava "$ comando", a saída e [exit=N] com o exit real
log="$1"; shift
{ printf '$ %s\n' "$*"; "$@" 2>&1; rc=$?; printf '[exit=%s]\n' "$rc"; } > "$log"
exit 0
