#!/bin/bash
# real-rodada3.sh — revisão adversarial REAL sobre o diff da F11 (rodada 3 do loop, o teto).
# Revisor claude (CLI, assinatura) → auditor openrouter:qwen/qwen3.7-plus (API paga, data_collection=deny).
# A chave vem de ~/.config/rdd-eval.env só para o ambiente deste processo: nunca impressa, nunca gravada.
# Receita do EVIDENCIA.md: rc honesto antes de qualquer pipe; log em real.log terminando em [exit=N].
set -u
cd "$(git rev-parse --show-toplevel)" || exit 64
E=sdd/reports/evidence/F11_GATE
EX="$(git rev-parse --git-common-dir)/info/exclude"
grep -qx 'sdd/reports/reviews/' "$EX" 2>/dev/null || printf '%s\n' 'sdd/reports/reviews/' >> "$EX"
OPENROUTER_API_KEY="$(grep -E '^OPENROUTER_API_KEY=' "$HOME/.config/rdd-eval.env" | head -1 | cut -d= -f2- | tr -d "\"'")"
export OPENROUTER_API_KEY
log="$E/real-rodada3.log"
cmd='bash sdd/bin/adversarial-review.sh --reviewer claude --auditor openrouter:qwen/qwen3.7-plus --feature F11_GATE'
out=$(eval "$cmd" 2>&1); rc=$?
{
  printf '$ git rev-parse HEAD\n%s\n' "$(git rev-parse HEAD)"
  printf '$ %s\n%s\n[exit=%s]\n' "$cmd" "$out" "$rc"
} > "$log"
pasta=$(printf '%s\n' "$out" | sed -n 's/^pasta: //p' | tail -1)
if [ -n "$pasta" ] && [ -f "$pasta/META.txt" ]; then
  out2=$(cat "$pasta/META.txt" 2>&1); rc2=$?
  printf '$ cat %s/META.txt\n%s\n[exit=%s]\n' "$pasta" "$out2" "$rc2" >> "$log"
  out3=$(bash sdd/bin/sdd-fluxo.sh loop --review "$pasta" --ledger sdd/reports/evidence/F11_GATE/ledger-review.md --rodada 3 2>&1); rc3=$?
  printf '$ bash sdd/bin/sdd-fluxo.sh loop --review %s --ledger sdd/reports/evidence/F11_GATE/ledger-review.md --rodada 3\n%s\n[exit=%s]\n' "$pasta" "$out3" "$rc3" >> "$log"
  out4=$(bash sdd/bin/adversarial-review.sh --conferir "$pasta" 2>&1); rc4=$?
  printf '$ bash sdd/bin/adversarial-review.sh --conferir %s\n%s\n[exit=%s]\n' "$pasta" "$out4" "$rc4" >> "$log"
fi
if grep -q "$OPENROUTER_API_KEY" "$log" ${pasta:+"$pasta"/*} 2>/dev/null; then
  echo "🛑 a chave apareceu num arquivo gravado" >&2; exit 2
fi
echo "rc=$rc pasta=$pasta"
exit "$rc"
