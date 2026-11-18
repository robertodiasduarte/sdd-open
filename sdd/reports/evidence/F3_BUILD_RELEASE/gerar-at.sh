#!/usr/bin/env bash
# Gera AT-nnn.log da F3: cada log roda, no piso (/usr/bin/python3 3.9 + /bin/bash 3.2), os testes que
# provam aquele AT. 1ª linha = o comando; depois a saída verbatim (sem as ResourceWarning do checar).
set -u
cd "$(git rev-parse --show-toplevel)" || exit 64
E=sdd/reports/evidence/F3_BUILD_RELEASE
export SDD_TEST_BASH=/bin/bash

at() { # $1=AT-nnn $2..=testes (módulo.Classe.teste) rodados de tests/
  local id="${1}"; shift
  local cmd="cd tests && SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest -v $*"
  { echo "\$ ${cmd}"; (cd tests && /usr/bin/python3 -B -m unittest -v "$@" 2>&1) | grep -v ResourceWarning | tail -n 200; } > "${E}/${id}.log"
  printf '%s %s\n' "${id}" "$(grep -E '^(OK|FAILED)' "${E}/${id}.log" | tail -1)"
}
cmdlog() { # $1=AT-nnn $2=comando (bash -c)
  { echo "\$ ${2}"; bash -c "${2}" 2>&1 | tail -n 200; echo "exit=${PIPESTATUS[0]}"; } > "${E}/${1}.log"
  printf '%s %s\n' "${1}" "$(tail -1 "${E}/${1}.log")"
}

M=test_report_lint.Migrations
D=test_deploy_espera_testes.DeployEsperaTestes
P=test_sdd_open.Projeto
C=test_contrato_build_release
at AT-001 $M.test_migration_com_log_passa
at AT-002 $M.test_migration_sem_linha_reprova $M.test_migration_sem_a_secao_reprova \
  $M.test_pasta_migrations_conta_como_migration $M.test_sql_citado_fora_da_secao_de_arquivos_nao_conta \
  $M.test_titulos_reais_numerados_ou_com_prefixo_contam
at AT-003 $M.test_prova_que_nao_prova_reprova $M.test_exit_0_reprova_mesmo_com_log_valido \
  $M.test_log_sem_linha_de_comando_reprova
at AT-004 $M.test_projeto_sem_nome_e_ref_reprova $M.test_projeto_so_com_travessoes_reprova $M.test_sem_data_reprova
at AT-005 $M.test_recibo_vale_mesmo_com_gate_test $M.test_ja_aplicada_em_vale_como_data
at AT-006 $M.test_layers_sql_preenchido_conta_como_migration $M.test_layers_sql_vazio_usa_so_o_glob_fixo
at AT-007 $M.test_migration_apagada_nao_exige_linha $M.test_relatorio_sem_migration_nao_exige_a_secao
at AT-008 test_report_lint.ReportLint
at AT-009 $D.test_release_do_sdd_open_espera_por_needs $D.test_lista_de_passos_no_mesmo_recuo_da_chave_e_lida
at AT-010 $D.test_workflow_real_que_publica_sem_teste_e_nao $D.test_lint_sozinho_nao_conta_como_teste \
  $D.test_instalar_a_ferramenta_de_teste_nao_e_testar $D.test_alvo_de_make_que_comeca_com_test_nao_e_teste \
  $D.test_acao_que_faz_push_de_imagem_publica
at AT-011 $D.test_suite_informativa_com_set_e_e_exit_0_nao_segura $D.test_continue_on_error_no_passo_de_teste_nao_segura \
  $D.test_continue_on_error_no_job_de_teste_nao_segura $D.test_ou_true_no_comando_de_teste_nao_segura \
  $D.test_if_always_no_job_que_publica_nao_segura $D.test_if_always_em_qualquer_passo_que_publica_nao_segura \
  $D.test_if_always_num_job_do_meio_do_needs_nao_segura $D.test_pipe_sem_pipefail_nao_segura_e_shell_bash_segura
at AT-012 $D.test_teste_no_mesmo_job_com_continue_on_error_so_fora_do_teste_e_sim $D.test_lint_sozinho_nao_conta_como_teste
at AT-013 $D.test_workflow_run_e_nao_sei $D.test_workflow_reutilizavel_e_nao_sei \
  $D.test_teste_em_script_proprio_e_nao_sei_nunca_nao $D.test_yaml_que_nao_consigo_ler_e_nao_sei \
  $D.test_teste_com_if_nao_garante_e_nao_sei $D.test_set_e_sem_exit_0_no_fim_e_nao_sei \
  $D.test_job_com_nome_de_deploy_nao_reconhecido_impede_o_sim $D.test_workflow_so_de_workflow_call_e_avaliado_por_quem_chama \
  $D.test_arquivo_que_nao_abre_e_nao_sei_com_resultado
at AT-014 $D.test_sem_pasta_de_workflows_nao_se_aplica $D.test_workflow_que_so_testa_nao_se_aplica \
  $D.test_workflow_so_de_pull_request_nao_publica_a_main $D.test_argumento_que_nao_e_pasta_e_64
at AT-015 $P.test_doctor_avisa_skill_mais_velha_que_a_do_pacote
at AT-016 $P.test_doctor_avisa_sdd_bin_diferente_do_pacote $P.test_doctor_em_dia_com_o_pacote $P.test_doctor_termina_em_resultado
at AT-017 $C.SddRelease
at AT-018 $C.SddBuild
at AT-019 $C.TemplateEPlaybook
cmdlog AT-020 'T=$(mktemp -d) && git archive HEAD | tar -x -C $T && PUBLISH_GATE_MODE=ci bash scripts/publish-gate.sh $T'
cmdlog AT-021 'python3 -B scripts/check-versions.py --base v2.2.2 --base-obrigatoria'
cmdlog AT-022 'git diff --stat v2.2.2 HEAD -- sdd/bin/verify-gate.sh sdd/fixtures/ scripts/publish-gate.sh scripts/publish-gate-patterns.txt .github/ && echo "(diff vazio: verify-gate, fixtures, publish-gate e workflows iguais a v2.2.2)" && cd tests && SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest test_verify_gate test_skill_lint test_playbook_lint test_sdd_open 2>&1 | grep -v ResourceWarning | tail -n 4'
