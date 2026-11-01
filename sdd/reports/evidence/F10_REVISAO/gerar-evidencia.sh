#!/usr/bin/env bash
# Evidência por AT da F10: roda o grupo de testes de cada AT no piso (bash 3.2 + Python do sistema) e grava
# AT-<faixa>.log com a receita do EVIDENCIA.md (rc antes de qualquer pipe; última linha [exit=N]).
set -u
cd "$(git rev-parse --show-toplevel)" || exit 64
E=sdd/reports/evidence/F10_REVISAO
export SDD_TEST_BASH=/bin/bash
grava() { # $1=nome do log $2..=módulos de teste
  nome="$1"; shift
  cmd="cd tests && SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest -v $*"
  out=$(cd tests && /usr/bin/python3 -B -m unittest -v "$@" 2>&1); rc=$?
  log="$E/$nome.log"
  printf '$ %s\n' "$cmd" > "$log"
  printf '%s\n' "$out" | tail -n 120 >> "$log"
  printf '[exit=%s]\n' "$rc" >> "$log"
  echo "$nome → $rc"
}
grava AT-001-005 test_revisao.Registry test_revisao.Exclusao
grava AT-006-007-024 test_revisao.Diff
grava AT-008-009 test_revisao.Contexto
grava AT-010-020-adapters test_revisao_adapters
grava AT-011-013-022-023-041 test_revisao.Vereditos
grava AT-014-015 test_revisao.SegundoRevisor
grava AT-016 test_revisao.Desempate
grava AT-017-019 test_revisao.Falhas
grava AT-020-021 test_revisao.Custo test_revisao.Registry.test_precos_tem_fonte_url_e_data_iso
grava AT-025-026 test_revisao.Conferir
grava AT-027-032-033-037 test_contrato_build_release.RevisaoAdversarial test_decisoes_lint
grava AT-028-031 test_fluxo.LoopF10 test_fluxo.Loop
grava AT-034-035 test_sdd_open.Projeto.test_init_copia_review_e_adapters_e_nunca_sobrescreve test_sdd_open.Projeto.test_doctor_avisa_adapter_diferente_do_pacote test_revisao.Registry.test_registry_de_fabrica_tem_as_4_engines_com_9_colunas_e_sem_cadeia
grava AT-036 test_revisao.Prompts
grava AT-041-docs test_docs
grava revisao-real-e-ciclos test_revisao.RevisaoReal test_revisao.AvaliadorCiclo1 test_revisao.AvaliadorCiclo2 test_revisao.RevisaoFinal test_revisao.RevisaoRodada2 test_fluxo.LoopF10
