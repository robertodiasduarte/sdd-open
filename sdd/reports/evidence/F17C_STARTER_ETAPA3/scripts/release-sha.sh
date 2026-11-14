#!/usr/bin/env bash
# release-sha.sh <repo> <tag> <pasta vazia> <log>: baixa os assets da Release e confere o SHA256SUMS.txt
R="$1"; T="$2"; D="$3"; L="$4"
{ echo "\$ gh release download $T --repo $R --dir <pasta vazia> && (cd <pasta> && shasum -a 256 -c SHA256SUMS.txt)"
  gh release download "$T" --repo "$R" --dir "$D" && (cd "$D" && shasum -a 256 -c SHA256SUMS.txt); rc=$?
  echo "rc=$rc"; } > "$L" 2>&1
