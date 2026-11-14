#!/usr/bin/env bash
# at-logs.sh: um log por AT que se prova no Mac, com "$ comando", a saída e [exit=N] (rc real)
cd "$(git rev-parse --show-toplevel)/tests" || exit 64
E=../sdd/reports/evidence/F16W_WINDOWS
L=../sdd/reports/evidence/F16W_WINDOWS/scripts/evlog.sh
bash $L $E/AT-001.log /usr/bin/python3 -B -m unittest -v test_testes_por_modulo
bash $L $E/AT-002.log /usr/bin/python3 -B -m unittest -v test_testes_por_modulo.Executor.test_teto_mata_a_arvore_e_segue test_testes_por_modulo.Executor.test_uso_errado_sai_64_sem_rodar test_testes_por_modulo.Executor.test_saida_fora_do_cp1252_nao_derruba_o_executor
bash $L $E/AT-003.log /usr/bin/python3 -B -m unittest -v test_release_workflow.Windows
SDD_TEST_BASH=/bin/bash bash $L $E/AT-004.log /usr/bin/python3 -B -m unittest -v test_checar.TestRemoto test_checar.TestFrente test_checar.TestVigiaNoWindows test_f16_textos
bash $L $E/AT-006.log /usr/bin/python3 -B -m unittest -v test_windows
