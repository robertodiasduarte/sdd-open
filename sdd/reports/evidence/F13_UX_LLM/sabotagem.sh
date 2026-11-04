#!/bin/bash
# 1 sabotagem por script: o teste do contrato precisa falhar. Numa cópia do HEAD; nada muda no projeto.
cd "$(git rev-parse --show-toplevel)" || exit 64
T="$(mktemp -d)"; git archive HEAD | tar -x -C "$T"; cd "$T" || exit 64
sab() { # nome arquivo de para modulo
  cp "$2" "$2.orig"
  /usr/bin/python3 -B - "$2" "$3" "$4" <<'P'
import sys
p,a,b=sys.argv[1:4]; t=open(p,encoding='utf-8').read()
assert a in t, a
open(p,'w',encoding='utf-8').write(t.replace(a,b))
P
  out=$(SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover -s tests -p "$5.py" 2>&1); rc=$?
  printf '$ sabotagem %s (%s) → %s\n%s\n[exit=%s]\n\n' "$1" "$2" "$5" "$(printf '%s\n' "$out" | grep -E '^(FAIL|ERROR):|^(OK|FAILED)' | cut -c1-120 | head -8)" "$rc"
  mv "$2.orig" "$2"
}
sab contraste-arredonda sdd/bin/contraste.sh '* 100 + 1e-9)' '* 100 + 0.5)' test_contraste
sab contraste-sem-LC_ALL sdd/bin/contraste.sh 'export LC_ALL=C' ':' test_contraste
# Tirar só o LC_ALL=C não derruba nada: a saída é inteiro + ponto literal, e o idioma não a alcança; a guarda é proteção extra.
# Para provar que o teste de idioma tem dentes: imprimir com %f, sem a guarda (no macOS, com pt_BR, sai vírgula).
sab2() {
  cp sdd/bin/contraste.sh sdd/bin/contraste.sh.orig
  /usr/bin/python3 -B - <<'P2'
p='sdd/bin/contraste.sh'; t=open(p,encoding='utf-8').read()
a='printf "%d.%02d %s\\n", int(c / 100), c - int(c / 100) * 100,'
assert a in t, a
t=t.replace(a,'printf "%.2f %s\\n", c / 100,').replace('export LC_ALL=C',':')
open(p,'w',encoding='utf-8').write(t)
P2
  out=$(SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover -s tests -p "test_contraste.py" 2>&1); rc=$?
  printf '$ sabotagem contraste-com-%%f-sem-LC_ALL → test_contraste\n%s\n[exit=%s]\n\n' "$(printf '%s\n' "$out" | grep -E '^(FAIL|ERROR):|^(OK|FAILED)' | cut -c1-120 | head -8)" "$rc"
  mv sdd/bin/contraste.sh.orig sdd/bin/contraste.sh
}
sab2
sab scan-sem-wrapper sdd/bin/prompt-drift-scan.sh 'if [ -n "$WRAPPER" ] && casa "$WRAPPER" "$2"; then' 'if false; then' test_prompt_drift_scan
sab scan-grep2-vira-nao-achei sdd/bin/prompt-drift-scan.sh '  erro_uso "a busca falhou (exit $rc) ao avaliar $CAMINHO" "confira a permissão do arquivo e a expressão de prompts.wrapper_pattern"' '  return 1' test_prompt_drift_scan
sab scan-caminho-sem-normalizar sdd/bin/prompt-drift-scan.sh '  fisico="$(cd "$dir" 2>/dev/null && pwd -P)" || erro_uso "não consegui entrar na pasta de $p" "confira a permissão da pasta"' '  fisico="$dir"' test_prompt_drift_scan
sab lint-sem-tipo sdd/bin/design-lint.py 'if valor not in ("one-shot", "loop"):' 'if False:' test_design_lint
rm -rf "${T:?}"
