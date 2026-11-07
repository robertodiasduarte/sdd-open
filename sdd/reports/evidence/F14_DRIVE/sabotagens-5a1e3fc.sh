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
D=sdd/bin/sdd-drive.sh; S=sdd/bin/deploy-do-sha.sh; A=sdd/bin/sdd-archive.py
# R1@codex e R3@claude, rodada 5
roda "drive: trava de estado sem flock" $D 'fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)' 'pass' test_drive.py
roda "drive: trava que não abre volta ao laço" $D '            falha("não consegui abrir a trava %s: %s" % (rel, e), "apague %s e rode de novo; o estado ficou como estava." % rel)' '            time.sleep(0.05)
            continue' test_drive.py
roda "drive: trava em arquivo que saiu do caminho vale" $D 'if os.path.samestat(os.fstat(fd), os.stat(caminho)):' 'if True:' test_drive.py
roda "drive: larga sem apagar" $D '                os.remove(caminho)  # ainda com a trava' '                pass  # ainda com a trava' test_drive.py
# R2@claude
roda "deploy: 401 no disparo guarda a marca" $S '                                d.desmarcar()  # o 401 diz' '                                pass  # o 401 diz' test_deploy_do_sha.py
# R4@claude e o teste que faltava
roda "archive: solto recente sem classificação" $A '            recentes.append((os.path.basename(p), 1, idade(p), a.dias_b))' '            nao_class.append(p)' test_sdd_archive.py
roda "archive: slice não protege" $A '        if g not in abertas:
            abertas[g], arquivo[g] = corpo, nome' '        if False:
            abertas[g], arquivo[g] = corpo, nome' test_sdd_archive.py
roda "archive: cita ficha que não existe" $A 'abertas[g], arquivo[g] = corpo, nome' 'abertas[g], arquivo[g] = corpo, "HANDOFF_%s.md" % g' test_sdd_archive.py
# R1@claude
roda "release: repetir o 4 sem teto" .agents/skills/sdd-release/SKILL.md '**no máximo 8 chamadas** (os mesmos 40 minutos)' '' test_f14_drive_textos.py
roda "release: repete nenhum run" .agents/skills/sdd-release/SKILL.md 'Saiu 4 com "não achei nenhum run"? Não repita' 'Saiu 4' test_f14_drive_textos.py
wait
vivos="$(wc -l < "$VIVOS" | tr -d ' ')"; rm -f "$VIVOS"
printf 'sabotagens: %s no total\n' "$(grep -c '^roda ' "$0")"
printf 'sabotagens vivas: %s\n' "$vivos"
[ "$vivos" -eq 0 ]
