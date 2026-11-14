#!/usr/bin/env bash
# sabotagem.sh <commit> <log>: cada mutante numa cópia nova de git archive; o teste nomeado tem de FALHAR (mutante morto)
set -u
W=/Users/robertoduarte/rdd-worktrees/sdd-open-f17c-starter-etapa3; C="$1"; LOG="$2"; vivos=0
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
muta "pasta-base ignorada (raiz da skill)" scripts/gerar-starter.py 't = t.replace("    raiz = origem / base\n", "    raiz = origem\n")' test_f17c_gerador.ModoWeb.test_at002_as_3_saem_so_do_modo_web
muta "sem a guarda de .. no citado" scripts/gerar-starter.py 't = t.replace("        if \".\" + \".\" in Path(rel).parts:", "        if False:").replace("        if \"..\" in Path(rel).parts:", "        if False:")' test_f17c_gerador.ModoWeb.test_at003_modo_web_quebrado_sai_65_sem_gravar
muta "modo web de volta a sdd/ plano" .agents/skills/sdd-build/web/MODO_WEB.md 't = t.replace("- gravar como `sdd/reports/BUILD_REPORT_{FEATURE}.md`.", "- gravar como `sdd/BUILD_REPORT_{FEATURE}.md`.")' test_f17c_textos.ModoWebGerado.test_at004_pastas_do_open_e_entrega_no_chat
muta "validador de volta no checklist do design" .agents/skills/sdd-design/web/MODO_WEB.md 't = t.replace("- [ ] A releitura do documento contra este checklist foi feita.", "- [ ] `scripts/validate_design.py` passa quando executável.")' test_f17c_textos.ModoWebGerado.test_at005_nenhuma_das_3_cita_validador
muta "molde do relatório sem Drift detectado" sdd/templates/BUILD_REPORT_TEMPLATE.md 't = t.replace("## Drift detectado\n", "## Drift\n")' test_f17c_textos.MoldesDoOpen
muta "validador da builder aceita a subpasta errada" .agents/skills/ux-review-builder/scripts/validate_generated_bundle.py 't = t.replace("sdd/(?!features/|reviews/)", "sdd/(?!features/|reviews/|architecture/)").replace("\\b(architecture|templates)/|", "\\b(templates)/|")' test_f17c_textos.ValidadorDaBuilder
echo "vivos=$vivos"; echo "rc=$vivos"
} > "$LOG" 2>&1
exit $vivos
