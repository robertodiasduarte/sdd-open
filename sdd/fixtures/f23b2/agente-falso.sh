#!/usr/bin/env bash
# Agente falso do tests/test_f23b2_papeis.py (README desta pasta). Roda na cópia do caso, pelo papel-serie.sh.
set -u
[ -n "${FALSO_LOG:-}" ] && printf '%s %s %s %s\n' "$SDD_PAPEL" "$SDD_CASO" "$SDD_REP" "$SDD_MODELO" >> "$FALSO_LOG"
[ -f "$SDD_BRIEF" ] || { echo "sem brief" >&2; exit 3; }
case "${FALSO_MODO:-}" in
  grava-projeto) printf 'escrita fora da cópia\n' > "$FALSO_PROJETO/vazou.txt" ;;
  remoto) git remote add origin https://example.com/x.git ;;
  dorme) sleep 30 ;;
esac
if [ "${FALSO_MODO:-}" != "sem-sessao" ]; then
  nome="$("$FALSO_PYTHON" -c 'import os, re; print(re.sub(r"[^A-Za-z0-9]", "-", os.path.realpath(os.getcwd()).replace("\\", "/")))')"
  s="$CLAUDE_CONFIG_DIR/projects/$nome"
  mkdir -p "$s"
  ts="$(date -u +%Y-%m-%dT%H:%M:%S.000Z)"
  printf '{"type":"user","timestamp":"%s","message":{"role":"user","content":"brief"}}\n' "$ts" > "$s/sessao.jsonl"
  printf '{"type":"assistant","timestamp":"%s","requestId":"r1","message":{"id":"m1","model":"%s","role":"assistant","content":[],"usage":{"input_tokens":1000,"output_tokens":100000,"cache_read_input_tokens":0,"cache_creation_input_tokens":0}}}\n' "$ts" "$SDD_MODELO" >> "$s/sessao.jsonl"
fi
cat "$FALSO_RESPOSTAS/$SDD_MODELO/$SDD_CASO.txt" 2>/dev/null
exit 0
