#!/usr/bin/env bash
# AT-016 da F5: 1 sabotagem por script novo ou alterado. Cada uma quebra o contrato de propósito (troca de
# texto exata, conferida), roda os testes da F5 no piso e tem de deixar ≥1 teste vermelho com o nome;
# depois `git checkout` do arquivo e os mesmos testes voltam ao verde. Roda da raiz, com a árvore limpa.
set -u
cd "$(git rev-parse --show-toplevel)" || exit 64
MODS="test_sdd_kb test_sdd_kb_normativo test_kb_dominios"
falhas=0

roda() { (cd tests && SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest $MODS 2>&1); }

sabota() { # $1 nome · $2 arquivo · $3 trecho · $4 substituto
  echo "── $1 ($2)"
  /usr/bin/python3 -B - "$2" "$3" "$4" <<'PY' || { echo "   âncora da sabotagem ausente"; falhas=$((falhas + 1)); return; }
import sys
p, a, b = sys.argv[1:]
t = open(p, encoding="utf-8").read()
if t.count(a) != 1: sys.exit(1)
open(p, "w", encoding="utf-8").write(t.replace(a, b))
PY
  saida="$(roda)"
  vermelhos="$(printf '%s\n' "$saida" | grep -E '^(FAIL|ERROR): ' | sort -u)"
  if [ -n "$vermelhos" ]; then printf '   vermelho:\n%s\n' "$(printf '%s\n' "$vermelhos" | sed 's/^/     /')"
  else echo "   ✗ NENHUM teste ficou vermelho"; falhas=$((falhas + 1)); fi
  git checkout -q -- "$2"
  if roda | grep -q '^OK$'; then echo "   verde de novo depois do git checkout"
  else echo "   ✗ não voltou ao verde"; falhas=$((falhas + 1)); fi
}

sabota "validate_kb.py --strict deixa de exigir teste" .agents/skills/sdd-kb/scripts/validate_kb.py \
  "            if impl and not teste:" "            if False and impl and not teste:"
sabota "kb_normativo.py rule-map --check aceita RULE_MAP derivado" .agents/skills/sdd-kb/scripts/kb_normativo.py \
  'if not target.is_file() or target.read_text(encoding="utf-8") != text:' 'if False:'
sabota "gate.sh não reprova caso ruim aceito" .agents/skills/sdd-kb/scripts/gate.sh \
  '    falha "$caso" "caso ruim ACEITO" "o validador deixou de conferir isto"' '    : "$caso"'
sabota "kb-dominios.py aceita nome sem pasta" sdd/bin/kb-dominios.py \
  "for n in nomes if n not in existentes]" "for n in nomes if False]"

git diff --quiet -- .agents sdd/bin && echo "árvore limpa no fim" || { echo "✗ árvore suja no fim"; falhas=$((falhas + 1)); }
echo "sabotagens com falha: $falhas"
exit $((falhas > 0))
