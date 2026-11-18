#!/usr/bin/env bash
# sabotagem.sh <commit>: cada mutante numa cópia nova de git archive; morto = o teste que o cobre cai (rc ≠ 0).
set -u
C="$1"; RAIZ="$(git rev-parse --show-toplevel)"; mortos=0; total=0
mut() {   # mut <nome> <arquivo> <python que muda o texto em s> <módulo.teste>
  local nome="$1" arq="$2" py="$3" alvo="$4" T rc
  T="$(mktemp -d)"; git -C "$RAIZ" archive "$C" | tar -x -C "$T"
  python3 - "$T/$arq" "$py" <<'PY'
import sys
p, codigo = sys.argv[1], sys.argv[2]
s = open(p, encoding="utf-8").read(); antes = s
exec(codigo)
assert s != antes, "o mutante não mudou nada"
open(p, "w", encoding="utf-8").write(s)
PY
  (cd "$T/tests" && python3 -B -m unittest "$alvo" >"$T/saida.txt" 2>&1); rc=$?
  total=$((total+1)); if [ "$rc" != 0 ]; then mortos=$((mortos+1)); echo "MORTO  $nome ($alvo rc=$rc)"; else echo "VIVO   $nome ($alvo rc=0)"; fi
  rm -rf "$T"
}
mut "executor não mata a árvore no teto" scripts/testes-por-modulo.py \
  's = s.replace("            matar_arvore(p)\n", "            pass\n")' test_testes_por_modulo.Executor.test_teto_mata_a_arvore_e_segue
mut "fatias: tudo na 1ª" scripts/testes-por-modulo.py \
  's = s.replace("i = min(range(n), key=lambda k: (cargas[k], k))", "i = 0")' test_testes_por_modulo.Executor.test_fatias_disjuntas_completas_e_estaveis
mut "unidade volta a ser o módulo" scripts/testes-por-modulo.py \
  's = s.replace("cont.setdefault(i.rsplit(\".\", 1)[0], [])", "cont.setdefault(i.split(\".\", 1)[0], [])")' test_testes_por_modulo.Executor.test_classes_viram_unidades_e_a_herdada_conta_uma_vez
mut "subprocess de texto sem encoding no produto" sdd/bin/sdd-fluxo.sh \
  's = s.replace("capture_output=True, text=True, encoding=\"utf-8\", errors=\"replace\")", "capture_output=True, text=True)", 1)' test_windows.Decodificacao
mut "vigia do checar não corta nada" .agents/skills/sdd-checar-ambiente/scripts/checar.sh \
  's = s.replace("      kill -\"${s}\" -- \"-${p}\" 2>/dev/null\n", "      :\n")' test_checar.TestRemoto.test_ssh_pendurado_vigia
mut "matriz cancela as outras fatias" .github/workflows/release.yml \
  's = s.replace("      fail-fast: false", "      fail-fast: true")' test_release_workflow.Windows
mut "executor mata só o filho, não o grupo (avaliador, ciclo 1, A2)" scripts/testes-por-modulo.py \
  's = s.replace("os.killpg(p.pid, signal.SIGKILL)", "pass")' test_testes_por_modulo.Executor.test_teto_mata_a_arvore_e_segue
mut "teto aceita nan (avaliador, A1)" scripts/testes-por-modulo.py \
  's = s.replace("if not math.isfinite(teto) or teto <= 0:", "if teto <= 0:")' test_testes_por_modulo.Executor.test_uso_errado_sai_64_sem_rodar
mut "classe grande inteira numa unidade" scripts/testes-por-modulo.py \
  's = s.replace("GRUPO = 12 ", "GRUPO = 999 ")' test_testes_por_modulo.Executor.test_classe_grande_vira_partes_que_somam_tudo
mut "rc_do_vigia sem o caso vizinho (rc 0 tarde vira corte)" .agents/skills/sdd-checar-ambiente/scripts/checar.sh \
  's = s.replace("if no_windows && [ \"$1\" != 0 ] &&", "if no_windows &&")' test_checar.TestVigiaNoWindows.test_regra_do_relogio_e_o_caso_vizinho
echo "total: $mortos de $total mortos"
