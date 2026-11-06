#!/bin/bash
# ev.sh <log> <comando…> — grava "$ comando", a saída verbatim e [exit=N] com o exit real do comando.
log="$1"; shift
cmd="$*"
out=$(/bin/bash -c "$cmd" 2>&1); rc=$?
{ printf '$ %s\n' "$cmd"; printf '%s\n' "$out"; printf '[exit=%s]\n' "$rc"; } > "$log"
printf '%s [exit=%s]\n' "$log" "$rc"
