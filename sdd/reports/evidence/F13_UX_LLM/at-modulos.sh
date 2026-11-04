#!/bin/bash
# Um log por módulo, com o exit real. Em bash: no zsh, a lista não se divide em palavras.
E=sdd/reports/evidence/F13_UX_LLM
while read -r nome modulo; do
  /bin/bash "$E/ev.sh" "$E/at-$nome.log" "SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover -s tests -p '$modulo.py'" >/dev/null
  printf '%s: %s | %s | %s\n' "$nome" "$(grep -m1 '^Ran ' "$E/at-$nome.log")" "$(tail -2 "$E/at-$nome.log" | head -1)" "$(tail -1 "$E/at-$nome.log")"
done <<'L'
contraste test_contraste
scan test_prompt_drift_scan
lint test_design_lint
textos test_f13_textos
contagens-skills test_skill_lint
conversa test_conversa
decisoes test_decisoes_lint
docs test_docs
agnostico test_agnostico
L
