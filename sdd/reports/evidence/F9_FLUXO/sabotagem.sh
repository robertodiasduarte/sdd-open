#!/usr/bin/env bash
# Sabotagem da F9: 1 mutação por regra dos scripts novos (sdd-fluxo.sh em review-design, loop, seguir e
# despachar; sdd-decisoes-lint.sh na marca e no rótulo). Cada uma tem de deixar vermelho um teste nomeado;
# `git checkout` devolve o verde. Roda da raiz da worktree, com a árvore commitada.
set -u
cd "$(git rev-parse --show-toplevel)" || exit 64
export SDD_TEST_BASH=/bin/bash
falhas=0

sabota() { # $1=rótulo $2=arquivo $3=trecho original $4=trecho sabotado $5=módulo.Classe.teste
  /usr/bin/python3 -B - "$2" "$3" "$4" <<'PY' || { echo "✗ $1: trecho não encontrado"; falhas=$((falhas + 1)); return; }
import sys
p, a, b = sys.argv[1:4]
t = open(p, encoding="utf-8").read()
if t.count(a) != 1:
    sys.exit(1)
open(p, "w", encoding="utf-8").write(t.replace(a, b))
PY
  out="$(cd tests && /usr/bin/python3 -B -m unittest "$5" 2>&1)"; rc=$?
  nomes="$(printf '%s\n' "${out}" | grep -oE '^(FAIL|ERROR): [^ ]+' | sed -E 's/^(FAIL|ERROR): //' | sort -u | head -5 | tr '\n' ' ')"
  git checkout -q -- "$2"
  out2="$(cd tests && /usr/bin/python3 -B -m unittest "$5" 2>&1)"; rc2=$?
  if [ "${rc}" -ne 0 ] && [ "${rc2}" -eq 0 ]; then
    echo "✅ $1 → vermelho (${nomes}) · restaurado → verde"
  else
    echo "✗ $1 → rc sabotado=${rc}, rc restaurado=${rc2}"; falhas=$((falhas + 1))
  fi
}

sabota "review-design: limiar de 3 vira 99" sdd/bin/sdd-fluxo.sh \
  '    if novos >= 3:' '    if novos >= 99:' test_fluxo.ReviewDesign.test_tres_arquivos_novos_exige_e_modify_nao_conta
sabota "loop: linha MED fecha HIGH" sdd/bin/sdd-fluxo.sh \
  'if c[2] not in ("APLICADA", "REBATIDA_EVIDENCIA", "REBATIDA_ESCOPO") or c[1] != "HIGH":' \
  'if c[2] not in ("APLICADA", "REBATIDA_EVIDENCIA", "REBATIDA_ESCOPO"):' test_fluxo.Loop.test_continuar_por_cada_causa
sabota "seguir: não confere a revisão do DESIGN" sdd/bin/sdd-fluxo.sh \
  '                para("revisão do DESIGN exigida e não registrada no Advisor Ledger")' '                pass' \
  test_fluxo.Seguir.test_para_por_cada_motivo
sabota "despachar: sai 0 em vez de 40" sdd/bin/sdd-fluxo.sh \
  "  printf 'RESULTADO: AGUARDANDO_HUMANO\\n→ quando a pessoa colar o retorno, continue do passo que parou.\\n'
  exit 40" "  printf 'RESULTADO: AGUARDANDO_HUMANO\\n→ quando a pessoa colar o retorno, continue do passo que parou.\\n'
  exit 0" test_fluxo.Despachar.test_grava_o_brief_imprime_a_parada_e_sai_40
sabota "despachar: faixa [A-Za-z] de volta (aceita acento em UTF-8)" sdd/bin/sdd-fluxo.sh \
  "nome_ok() { case \"\$1\" in ''|*[!\"\$LETRAS\"]*) return 1 ;; esac; return 0; }" \
  "nome_ok() { case \"\$1\" in ''|*[!A-Za-z0-9_-]*) return 1 ;; esac; return 0; }" \
  test_fluxo.Despachar.test_nome_acentuado_sai_64_em_locale_utf8
sabota "seguir: severidade formatada não conta" sdd/bin/sdd-fluxo.sh \
  're.search(r"\bHIGH\b", re.sub(r"[*`_]", "", sev or "").upper())' '(sev or "").upper().startswith("HIGH")' \
  test_fluxo.Seguir.test_severidade_formatada_e_ledger_de_exemplo_cercado
sabota "decisoes-lint: pergunta sem marca passa" sdd/bin/sdd-decisoes-lint.sh \
  '    if not marcas:' '    if False:' test_decisoes_lint.Regras.test_cada_regra_reprova_pelo_motivo_certo
sabota "decisoes-lint: rótulo errado passa" sdd/bin/sdd-decisoes-lint.sh \
  '        elif ROTULOS.get(m.group(1)) != m.group(2).strip():' '        elif False:' \
  test_decisoes_lint.Regras.test_cada_regra_reprova_pelo_motivo_certo

[ "${falhas}" -eq 0 ] && echo "RESULTADO: VERDE — 8/8 sabotagens derrubaram um teste nomeado" || echo "RESULTADO: VERMELHO — ${falhas} sabotagem(ns) sem dente"
exit "${falhas}"
