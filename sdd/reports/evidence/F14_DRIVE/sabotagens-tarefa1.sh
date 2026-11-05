#!/bin/bash
# sabotagens-tarefa1.sh — numa cópia de HEAD, 1 sabotagem por conserto da rodada 4 da F14; o teste nomeado tem de cair.
R="$(git rev-parse --show-toplevel)"
vivos=0
roda() { # nome · arquivo · de · para · padrão do teste
  local nome="$1" arq="$2" de="$3" para="$4" padrao="$5" T; T="$(mktemp -d)"
  git -C "$R" archive HEAD | tar -x -C "$T"
  python3 -B - "$T/$arq" "$de" "$para" <<'PY' || { echo "$nome: a sabotagem não se aplicou"; vivos=$((vivos + 1)); rm -rf "${T:?}"; return 1; }
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
  [ "$rc" -ne 0 ] || { echo "   ⚠️ a sabotagem NÃO derrubou teste"; vivos=$((vivos + 1)); }
}
roda "R5 (rodada 3): salvos voltam a incluir o índice" .agents/skills/sdd-new-session/scripts/copiar-docs.sh 'git -C "${PRINCIPAL}" ls-tree -r -z --name-only HEAD -- "${dir}"' 'git -C "${PRINCIPAL}" ls-files -z -- "${dir}"' test_copiar_docs.py
roda "R1: stdout sem newline fixo" sdd/bin/playbook-curator.sh ', newline="\n")' ')' test_playbook_curator.py
roda "R2: --aplicar sem a recusa de byte inválido" sdd/bin/playbook-curator.sh '    exige_utf8(pb, "o playbook")' '    pass' test_playbook_curator.py
roda "R2 lado 2: recusa também o UTF-8 válido" sdd/bin/playbook-curator.sh '        bruto.decode("utf-8")' '        bruto.decode("ascii")' test_playbook_curator.py
roda "R3: seta volta a omitir o PARECIDO com link" .agents/skills/sdd-new-session/scripts/copiar-docs.sh '[ "${parecidos}" -eq 0 ] || junta' '[ "${parecidos}" -eq 0 ] || [ "${ignorados}" -gt 0 ] || junta' test_copiar_docs.py
roda "R3 lado 2: frase sai sem o caso dela" .agents/skills/sdd-new-session/scripts/copiar-docs.sh '[ "${ignorados}" -eq 0 ] || junta' 'true && junta' test_copiar_docs.py
roda "R4: tira a leitura do brief" .agents/skills/sdd-release/SKILL.md 'se ele já tem o campo' 'se ele tiver' test_f14_textos.py
roda "R5: sem a conferência da pasta exclusiva" sdd/bin/playbook-curator.sh '            confere_pasta_exclusiva(p)' '            pass' test_playbook_curator.py
roda "R5 lado 2: recusa até a pasta 700" sdd/bin/playbook-curator.sh 'if st.st_mode & 0o077:' 'if st.st_mode & 0o777:' test_playbook_curator.py
printf 'sabotagens vivas: %s\n' "$vivos"
[ "$vivos" -eq 0 ]
