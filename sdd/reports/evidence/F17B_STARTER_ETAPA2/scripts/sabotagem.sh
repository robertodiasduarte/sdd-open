#!/usr/bin/env bash
# sabotagem.sh <commit> <log>: cada mutante numa cópia nova de git archive; o teste nomeado tem de FALHAR (mutante morto)
set -u
W=/Users/robertoduarte/rdd-worktrees/sdd-open-f17b-starter-etapa2; C="$1"; LOG="$2"; vivos=0
muta() { # $1 nome  $2 arquivo  $3 python que muda o texto (t)  $4.. testes
  local nome="$1" arq="$2" py="$3"; shift 3
  local d; d="$(mktemp -d)"; git -C "$W" archive "$C" | tar -x -C "$d"
  python3 - "$d/$arq" "$py" <<'PY'
import sys
from pathlib import Path
p = Path(sys.argv[1]); t = p.read_text(encoding="utf-8"); antes = t
exec(sys.argv[2])
assert t != antes, "o mutante não mudou nada"
p.write_text(t, encoding="utf-8")
PY
  (cd "$d/tests" && SDD_TEST_BASH=/bin/bash python3 -B -m unittest "$@" > "$d/out.log" 2>&1); rc=$?
  if [ $rc -ne 0 ]; then echo "✅ morto  $nome ($*)"; else echo "❌ VIVO   $nome ($*)"; vivos=$((vivos+1)); fi
  rm -rf "$d"
}
{
echo "\$ bash sabotagem.sh $C   # 6 mutantes, cada um numa cópia de git archive"
muta "compor sem exigir compatibility" scripts/gerar-starter.py 't = t.replace("for nome in (\"description\", \"compatibility\"):", "for nome in (\"description\",):")' test_gerar_starter.SkillDeModo.test_at003_modo_quebrado_sai_65_sem_gravar
muta "gerador sem tests/ em DONO_INTEIRO" scripts/gerar-starter.py 't = t.replace("\"docs\", \"exemplos\", \"tests\")", "\"docs\", \"exemplos\")")' test_gerar_starter.Gera.test_at001_gera_as_15_e_nao_toca_no_resto
muta "trava sem tests/ inteira" scripts/starter/raiz/scripts/check-gerado.py 't = t.replace("\"docs\", \"exemplos\", \"tests\")", "\"docs\", \"exemplos\")")' test_gerar_starter.Trava.test_at006_cada_mudanca_a_mao_sai_1
muta "release copiada inteira (sem a regra de modo)" scripts/gerar-starter.py 't = t.replace("        if skill in modos:\n            compor(origem, destino, modos[skill])\n        else:\n            shutil.copytree(origem, destino)", "        shutil.copytree(origem, destino)")' test_gerar_starter.SkillDeModo.test_at002_release_gerada_so_do_modo
muta "init sem a ux-review-builder" bin/sdd-open.sh 't = t.replace("for d in \"${base}\"/sdd-*/ \"${base}\"/ux-review-builder/; do", "for d in \"${base}\"/sdd-*/; do")' test_sdd_open.Projeto.test_init_instala_a_ux_review_builder
muta "lint sem pasta do init sem barra" scripts/gerar-starter.py 't = t.replace("(?:/|(?![A-Za-z0-9_-]))", "/")' test_f17b_passo0.LintSemBarra.test_pasta_do_init_sem_a_barra_reprova
echo "vivos=$vivos"; echo "rc=$vivos"
} > "$LOG" 2>&1
exit $vivos
