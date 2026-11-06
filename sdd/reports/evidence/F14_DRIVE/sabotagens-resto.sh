#!/bin/bash
# sabotagens.sh — numa cópia de HEAD, 1 sabotagem por script novo e nas regras que mais protegem; o teste nomeado tem de cair.
R="$(git rev-parse --show-toplevel)"
VIVOS="$(mktemp)"
_um() { # nome · arquivo · de · para · padrão do teste
  local nome="$1" arq="$2" de="$3" para="$4" padrao="$5" T; T="$(mktemp -d)"
  git -C "$R" archive "$SHA" | tar -x -C "$T"
  python3 -B - "$T/$arq" "$de" "$para" <<'PY' || { echo "$nome: A SABOTAGEM NÃO SE APLICOU"; echo x >> "$VIVOS"; rm -rf "${T:?}"; return 1; }
import sys
p, de, para = sys.argv[1:4]
s = open(p, encoding="utf-8").read()
if s.count(de) < 1:
    sys.exit(1)
open(p, "w", encoding="utf-8").write(s.replace(de, para, 1))
PY
  saida="$(cd "$T" && SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover -s tests -p "$padrao" 2>&1)"; rc=$?
  printf '%s: rc=%s · %s\n' "$nome" "$rc" "$(printf '%s\n' "$saida" | grep -E '^(FAILED|OK)' | tr '\n' ' ')"
  printf '%s\n' "$saida" | grep -E '^(FAIL|ERROR):' | head -3 | cut -c1-120
  rm -rf "${T:?}"
  [ "$rc" -ne 0 ] || { echo "   ⚠️ a sabotagem NÃO derrubou teste"; echo x >> "$VIVOS"; }
}
SHA="$(git -C "$R" rev-parse HEAD)"
roda() { # em paralelo, até 4: cada resultado sai inteiro, de uma vez
  while [ "$(jobs -r | wc -l)" -ge 4 ]; do sleep 1; done
  ( saida="$(_um "$@")"; printf '%s\n' "$saida" ) &
}
D=sdd/bin/sdd-drive.sh; S=sdd/bin/deploy-do-sha.sh; A=sdd/bin/sdd-archive.py
roda "drive: concluir ignora o proximo" $D '    if nome != "AVALIAR_E_RELATAR":
        ult = ultimo_valido(p, st)' '    if False:
        ult = ultimo_valido(p, st)' test_drive.py
roda "drive: rename some do diff entre commits (H1 do ciclo 2)" $D '"--name-only", "--no-renames", "--ignore-submodules=none"' '"--name-only", "--ignore-submodules=none"' test_drive.py
roda "archive: sem fronteira de palavra" $A 'r"(?<![^\W_])" + re.escape(nfc(n)) + r"(?![^\W_])"' 're.escape(nfc(n))' test_sdd_archive.py
roda "deploy: corrida sai 2" $S 'fim(4, "⏳ ainda não sei — pedi para repetir o deploy' 'fim(2, "⏳ ainda não sei — pedi para repetir o deploy' test_deploy_do_sha.py
wait
vivos="$(wc -l < "$VIVOS" | tr -d ' ')"; rm -f "$VIVOS"
printf 'sabotagens vivas: %s\n' "$vivos"
[ "$vivos" -eq 0 ]
