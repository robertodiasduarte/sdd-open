#!/usr/bin/env bash
# Sabotagem da F8: 1 mutação por script alterado ou novo. Cada uma tem de deixar vermelho um teste
# nomeado; `git checkout` devolve o verde. Roda da raiz da worktree, com a árvore commitada.
set -u
cd "$(git rev-parse --show-toplevel)" || exit 64
export SDD_TEST_BASH=/bin/bash
falhas=0

sabota() { # $1=rótulo $2=arquivo $3=trecho original $4=trecho sabotado $5=módulo de teste [$6=classe.teste]
  /usr/bin/python3 -B - "$2" "$3" "$4" <<'PY' || { echo "✗ $1: trecho não encontrado"; falhas=$((falhas + 1)); return; }
import sys
p, a, b = sys.argv[1:4]
t = open(p, encoding="utf-8").read()
if t.count(a) != 1:
    sys.exit(1)
open(p, "w", encoding="utf-8").write(t.replace(a, b))
PY
  local alvo="$5"; [ -n "${6:-}" ] && alvo="$5.$6"
  out="$(cd tests && /usr/bin/python3 -B -m unittest "$alvo" 2>&1)"; rc=$?
  nomes="$(printf '%s\n' "${out}" | grep -oE '^(FAIL|ERROR): [^ ]+' | sed -E 's/^(FAIL|ERROR): //' | sort -u | head -5 | tr '\n' ' ')"
  git checkout -q -- "$2"
  out2="$(cd tests && /usr/bin/python3 -B -m unittest "$alvo" 2>&1)"; rc2=$?
  if [ "${rc}" -ne 0 ] && [ "${rc2}" -eq 0 ]; then
    echo "✅ $1 → vermelho (${nomes}) · restaurado → verde"
  else
    echo "✗ $1 → rc sabotado=${rc}, rc restaurado=${rc2}"; falhas=$((falhas + 1))
  fi
}

sabota "pre-commit: H2 sem teto" sdd/hooks/pre-commit \
  '[ "${sz:-0}" -gt "$limite" ] && achado H2' '[ "${sz:-0}" -gt 999999999 ] && achado H2' test_hooks Hooks.test_h2_teto_do_arquivo_de_contexto
sabota "pre-push: nunca atrás" sdd/hooks/pre-push \
  'if [ "${behind:-0}" -gt 0 ]; then' 'if [ "${behind:-0}" -gt 999999 ]; then' test_hooks Hooks.test_pre_push_avisa_base_velha_e_sai_0
sabota "sdd-open.sh: init não liga o hooksPath" bin/sdd-open.sh \
  '        git config core.hooksPath sdd/hooks || die' '        true || die' test_sdd_open Hooks.test_init_liga_os_hooks_e_a_linha_do_plano_diz_o_efeito
sabota "vendors.sh: .cursorrules fora da lista" bin/lib/vendors.sh \
  'VENDOR_ARQUIVOS_CONTEXTO="AGENTS.md CLAUDE.md GEMINI.md .cursorrules"' 'VENDOR_ARQUIVOS_CONTEXTO="AGENTS.md CLAUDE.md GEMINI.md"' test_hooks Hooks.test_lista_de_arquivos_de_contexto_igual_a_do_pacote
sabota "merge.sh: entrada do avaliador não entra" bin/lib/merge.sh \
  '    pre.append({"matcher": matcher, "hooks": [h]})' '    pre.append({"matcher": matcher, "hooks": [h]}) if "report" in nome else None' test_claude_adapter Projeto.test_init_gera_os_guards_e_as_entradas_do_settings
sabota "alarme.sh: sdd/hooks tratado como outro" .agents/skills/sdd-higiene-dado/scripts/alarme.sh \
  '    MODO="hooks"' '    MODO="outro"' test_alarme TestModoHooks
sabota "pre-commit.sh da higiene: rm volta com hooksPath" .agents/skills/sdd-higiene-dado/scripts/pre-commit.sh \
  "  DESINSTALAR='Para desinstalar o alarme: bash .agents/skills/sdd-higiene-dado/scripts/alarme.sh desinstalar'" "  DESINSTALAR='Para desinstalar o alarme: rm \"sdd/hooks/pre-commit\"'" test_alarme TestModoHooks.test_recusa_pelo_dispatcher_ensina_desinstalar_sem_rm
sabota "report-guard: exit 1 do lint não nega" bin/adapters/claude/sdd-report-guard.py \
  '    if r.returncode == 1:
        negar(' '    if r.returncode == 99:
        negar(' test_claude_adapter Projeto.test_report_guard_nega_write_que_o_lint_reprova
sabota "avaliador-guard: ignora a palavra veredito" bin/adapters/claude/sdd-avaliador-guard.py \
  '    if "veredito" not in texto.lower():' '    if "veredito" in texto.lower():' test_claude_adapter Projeto.test_avaliador_guard_nega_com_arvore_suja_e_so_com_veredito

git diff --quiet -- sdd/hooks bin .agents/skills/sdd-higiene-dado || { echo "✗ a árvore não voltou ao commit"; falhas=$((falhas + 1)); }
if [ "${falhas}" -eq 0 ]; then echo "🟢 9/9 sabotagens vermelhas e restauradas"; exit 0; fi
echo "🛑 ${falhas} sabotagem(ns) sem dentes"; exit 1
