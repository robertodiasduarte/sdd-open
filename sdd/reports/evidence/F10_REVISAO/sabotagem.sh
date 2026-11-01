#!/usr/bin/env bash
# Sabotagem da F10: 1 mutação por regra (adversarial-review.sh: exclusão, parser de vereditos, classe de
# falha, custo, --conferir, 2º revisor; sdd-fluxo.sh loop: desempate e 2º revisor indisponível). Cada uma tem
# de deixar vermelho um teste nomeado; `git checkout` devolve o verde. Roda numa worktree temporária
# destacada no HEAD (a árvore de trabalho fica intacta: a revisão real confere o sha256 dela).
set -u
raiz="$(git rev-parse --show-toplevel)" || exit 64
W="$(mktemp -d)/sab"
git -C "$raiz" worktree add -q --detach "$W" HEAD || exit 64
trap 'git -C "$raiz" worktree remove --force "$W"' EXIT
cd "$W" || exit 64
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

AR=sdd/bin/adversarial-review.sh
sabota "exclusão: auditor igual ao revisor passa" $AR \
  'if chave(auditores[0]) == chave(revisores[0]) and not flags["--um-engine"]:' 'if False:' \
  test_revisao.Exclusao.test_auditor_igual_ao_revisor_e_67_sem_chamar_nada
sabota "vereditos: resposta sem bloco vira zero achados" $AR \
  '    ls = bloco(texto)
    if ls is None:
        return None, "bloco <<<VERDICTS ausente ou malformado"
    out = []
    for l in ls:
        try:
            j = json.loads(l)
        except ValueError:
            return None, "linha do bloco não é JSON: " + l[:80]
        if not isinstance(j, dict) or any' '    ls = bloco(texto) or []
    out = []
    for l in ls:
        try:
            j = json.loads(l)
        except ValueError:
            return None, "linha do bloco não é JSON: " + l[:80]
        if not isinstance(j, dict) or any' \
  test_revisao.Vereditos.test_revisor_sem_bloco_e_68_e_nunca_zero_achados
sabota "falha: credencial vira persistente (troca de engine)" $AR \
  '    if rc == 65 or re.search(d["sinal_auth"], bruto):
        return "auth"' '    if rc == 65 or re.search(d["sinal_auth"], bruto):
        return "persistente"' test_revisao.Falhas.test_auth_para_sem_chamar_a_proxima
sabota "custo: desconhecido vira US\$ 0" $AR \
  'return "assinatura" if d["cobranca"] == "assinatura" else "$?"' \
  'return "assinatura" if d["cobranca"] == "assinatura" else "US$ 0.0000"' test_revisao.Custo.test_quatro_formas_e_nunca_zero_desconhecido
sabota "conferir: não compara o sha256" $AR \
  '    if sha != meta.get("diff_sha256"):' '    if False:' test_revisao.Conferir.test_confere_e_deixa_de_conferir_com_1_byte
sabota "2º revisor: limiar de 8 arquivos vira 999" $AR \
  '    if len(arqs) >= SEGUNDO_REVISOR_MIN_ARQUIVOS:' '    if len(arqs) >= 999:' \
  test_revisao.SegundoRevisor.test_gatilhos_e_constantes
sabota "loop: desempate REFUTADO não fecha" sdd/bin/sdd-fluxo.sh \
  '            if id_ == alvo and decisao == "DECISAO:REFUTADO":' '            if False:' \
  test_fluxo.LoopF10.test_desempate_refutado_fecha_e_procede_mantem_aberto
sabota "loop: 2º revisor indisponível passa" sdd/bin/sdd-fluxo.sh \
  '        elif r2_ec in ("65", "66") or r2_eng == "indisponível":' '        elif False:' \
  test_fluxo.LoopF10.test_segundo_revisor_indisponivel_sem_dispensa_e_bloqueado_d3

sabota "ciclo 1: papel que falha sem engine grava -" $AR \
  '            reg["engine_efetivo"] = ultimo["id"]' '            pass' \
  test_revisao.AvaliadorCiclo1.test_1_segundo_revisor_sem_cli_bloqueia_o_loop_d3

sabota "ciclo 2: índice copiado com mtime novo (copyfile)" $AR \
  '            shutil.copy2(idx, tidx)' '            shutil.copyfile(idx, tidx)' \
  test_revisao.AvaliadorCiclo2.test_1_edicao_do_mesmo_tamanho_no_mesmo_instante_do_indice_entra_no_diff
sabota "ciclo 2: dispensa do 2º revisor sem motivo" sdd/bin/sdd-fluxo.sh \
  '+ r"\s*(?:—|–|-{1,2})\s*\S.{2,}$", ln.rstrip())' '+ r"", ln.rstrip())' \
  test_fluxo.LoopF10.test_dispensa_sem_motivo_nao_vale

sabota "rodada 1: auditoria parcial passa" $AR \
  '            if faltam:
                aud_v, erro = None,' '            if False:
                aud_v, erro = None,' test_revisao.RevisaoFinal.test_r1_codex_auditoria_parcial_e_68
sabota "rodada 1: --revisor2 igual ao revisor passa" $AR \
  'if r2_forcado and chave(r2_forcado) in (chave(revisores[0]), chave(auditores[0])):' 'if False:' \
  test_revisao.RevisaoFinal.test_r2_codex_revisor2_igual_ao_revisor_ou_ao_auditor_e_64

sabota "rodada 2: linha com crases e conteúdo some do bloco" $AR \
  'if l.strip() and not re.match(r"^```[A-Za-z]*$", l.strip())]' 'if l.strip() and not l.strip().startswith("```")]' \
  test_revisao.RevisaoRodada2.test_r1_codex_linha_com_crases_e_conteudo_e_68_e_cerca_sozinha_passa

[ "${falhas}" -eq 0 ] && echo "RESULTADO: VERDE — 14/14 sabotagens derrubaram um teste nomeado" || echo "RESULTADO: VERMELHO — ${falhas} sabotagem(ns) sem dente"
exit "${falhas}"
