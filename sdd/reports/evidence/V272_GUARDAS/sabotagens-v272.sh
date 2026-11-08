#!/usr/bin/env bash
# Sabotagens da v2.7.2 (S5 e S8 saíram na rodada 3: com a regra "a linha começa pela chamada", tirar o
# comentário virou código morto e foi removido; os casos de comentário seguem nos testes): cada uma desfaz um pedaço da correção; o teste novo tem de cair. Restaura sempre.
set -u
cd "$1" || exit 64
B=$(mktemp -d); cp bin/sdd-open.sh sdd/hooks/pre-commit bin/adapters/claude/sdd-report-guard.py "$B/"
restaura() { cp "$B/sdd-open.sh" bin/sdd-open.sh; cp "$B/pre-commit" sdd/hooks/pre-commit; cp "$B/sdd-report-guard.py" bin/adapters/claude/sdd-report-guard.py; }
roda() { # $1=nome $2=teste
  ( cd tests && python3 -m unittest "$2" >/dev/null 2>&1 ); rc=$?
  if [ "$rc" -ne 0 ]; then echo "✅ morta: $1 (teste caiu)"; else echo "❌ VIVA: $1 (teste passou com a sabotagem)"; fi
  restaura
}
python3 - <<'PY'
p="bin/adapters/claude/sdd-report-guard.py"; s=open(p).read(); a="    if not em_sdd_reports(caminho, projeto):\n        return\n"; assert a in s; open(p,"w").write(s.replace(a,""))
PY
roda "S1 guard sem o filtro de pasta" test_claude_adapter.Projeto.test_report_guard_so_julga_o_relatorio_em_sdd_reports
python3 - <<'PY'
p="sdd/hooks/pre-commit"; s=open(p).read()
a='      sdd/reports/*/*) continue ;;              # subpasta de sdd/reports/: não é o relatório da feature\n      sdd/reports/BUILD_REPORT_*.md) ;;\n'; assert a in s
open(p,"w").write(s.replace(a,'      */BUILD_REPORT_*.md|BUILD_REPORT_*.md) ;;\n'))
PY
roda "S2 pre-commit volta a casar pelo nome" test_hooks.Hooks.test_report_so_julga_o_relatorio_em_sdd_reports
python3 - <<'PY'
p="sdd/hooks/pre-commit"; s=open(p).read()
a='      sdd/reports/*/*) continue ;;              # subpasta de sdd/reports/: não é o relatório da feature\n'; assert a in s
open(p,"w").write(s.replace(a,''))
PY
roda "S3 pre-commit aceita subpasta de sdd/reports" test_hooks.Hooks.test_report_so_julga_o_relatorio_em_sdd_reports
python3 - <<'PY'
p="bin/sdd-open.sh"; s=open(p).read()
a='    if chama_o_nosso "${pc}"; then'; assert a in s; open(p,"w").write(s.replace(a,'    if false; then'))
PY
roda "S4 hooks_estado ignora o encadeamento" test_sdd_open.Hooks.test_gancho_encadeado_no_outro_gerenciador_e_reconhecido
python3 - <<'PY'
p="bin/sdd-open.sh"; s=open(p).read()
a='      if [ ! -x "${h}" ]; then'; assert a in s; open(p,"w").write(s.replace(a,'      if false; then'))
PY
roda "S6 doctor não confere o bit de execução" test_sdd_open.Hooks.test_gancho_encadeado_no_outro_gerenciador_e_reconhecido
python3 - <<'PY'
p="bin/sdd-open.sh"; s=open(p).read()
a='  elif chama_o_nosso "${legado}"; then'; assert a in s; open(p,"w").write(s.replace(a,'  elif false; then'))
PY
roda "S7 pre-commit legado encadeado não reconhecido" test_sdd_open.Hooks.test_pre_commit_legado_que_chama_o_nosso_e_encadeado
python3 - <<'PY'
p="bin/sdd-open.sh"; s=open(p).read()
a='stubs_do_husky "$(dirname "${pc}")" && chama_o_nosso'; assert a in s; open(p,"w").write(s.replace(a,'false && chama_o_nosso'))
PY
roda "S9 husky v9: a linha no script não é vista (R1@claude)" test_sdd_open.Hooks.test_husky_v9_linha_no_script_e_bit_no_stub
python3 - <<'PY'
p="bin/sdd-open.sh"; s=open(p).read()
a='if (index(t, l) == 1) achou = 1'; assert a in s; open(p,"w").write(s.replace(a,'if (index(t, l)) achou = 1'))
PY
roda "S10 chamada entre aspas conta como encadeada (R1@codex r2)" test_sdd_open.Hooks.test_gancho_encadeado_no_outro_gerenciador_e_reconhecido
python3 - <<'PY'
p="bin/sdd-open.sh"; s=open(p).read()
a='  [ -f "$1/h" ] && [ -f "$1/pre-commit" ] \\\n'; assert a in s; open(p,"w").write(s.replace(a,'  return 0\n  [ -f "$1/h" ] && [ -f "$1/pre-commit" ] \\\n'))
PY
roda "S11 qualquer pasta _ vale como husky (R1@claude e R2@codex r2)" test_sdd_open.Hooks.test_husky_v9_linha_no_script_e_bit_no_stub
python3 - <<'PY'
p="bin/sdd-open.sh"; s=open(p).read()
a='t ~ /^\\.[[:space:]]/ && t ~ /\\/h"?[[:space:]]*$/'; assert a in s; open(p,"w").write(s.replace(a,'index(t, "/h")'))
PY
roda "S12 /h comentado ou só citado no stub vale como husky (R1@codex r3 e r5)" test_sdd_open.Hooks.test_husky_v9_linha_no_script_e_bit_no_stub
python3 - <<'PY'
p="bin/sdd-open.sh"; s=open(p).read()
a='  case "${hp}" in "~") hp="${HOME}" ;; "~/"*) hp="${HOME}/${hp#\\~/}" ;; esac\n'; assert a in s; open(p,"w").write(s.replace(a,''))
PY
roda "S13 ~ no core.hooksPath não é expandido (R1@claude r3)" test_sdd_open.Hooks.test_hooks_path_com_til_e_expandido
git diff --quiet -- bin sdd/hooks || true; echo "restaurado: $(git diff --stat -- bin sdd/hooks | tail -1)"
