#!/usr/bin/env bash
# at-logs.sh: um log por AT da F17c numa cópia de git archive do HEAD; 1ª linha "$ comando", fim "rc=N"
W=/Users/robertoduarte/rdd-worktrees/sdd-open-f17c-starter-etapa3; E="$W/sdd/reports/evidence/F17C_STARTER_ETAPA3"
C="$(git -C "$W" rev-parse --short HEAD)"; T="$(mktemp -d)"; git -C "$W" archive HEAD | tar -x -C "$T"; falhas=0
at() { local id="$1"; shift
  { echo "\$ cd <git archive $C>/tests && SDD_TEST_BASH=/bin/bash python3 -B -m unittest -v $*"
    (cd "$T/tests" && SDD_TEST_BASH=/bin/bash python3 -B -m unittest -v "$@" 2>&1); rc=$?; echo "rc=$rc"; } > "$E/$id.log"
  grep -q '^rc=0$' "$E/$id.log" || falhas=$((falhas+1)); echo "$id $(tail -1 "$E/$id.log")"; }
at AT-001 test_gerar_starter.Gera.test_at001_gera_as_18_e_nao_toca_no_resto test_gerar_starter.Gera.test_at005_duas_geracoes_iguais_byte_a_byte
at AT-002 test_f17c_gerador.ModoWeb.test_at002_as_3_saem_so_do_modo_web test_f17c_gerador.ModoWeb.test_sem_pasta_base_o_modo_continua_na_raiz_da_skill test_gerar_starter.SkillDeModo
at AT-003 test_f17c_gerador.ModoWeb.test_at003_modo_web_quebrado_sai_65_sem_gravar test_f17c_gerador.ModoWeb.test_at003_a_copia_crua_das_3_reprova_no_lint
at AT-004 test_f17c_textos.ModoWebGerado.test_at004_pastas_do_open_e_entrega_no_chat test_f17c_textos.ModoWebGerado.test_at004_handoffs_dos_protocolos_coerentes test_f17c_textos.UmJeitoSoDePasta
at AT-005 test_f17c_textos.ModoWebGerado.test_at005_define_e_design_nao_pedem_comando_ao_aluno test_f17c_textos.ModoWebGerado.test_at005_nenhuma_das_3_cita_validador test_f17c_textos.ModoWebGerado.test_at005_build_le_a_saida_do_comando_sem_o_verify_gate_sh
at AT-006 test_f17c_textos.MoldesDoOpen
at AT-007 test_f17c_textos.NaoFinjaNoOpen
at AT-008 test_f17c_gerador.ModoWeb.test_at008_um_byte_trocado_no_build_gerado_e_acusado test_gerar_starter.Gera.test_at007_o_starter_passa_nas_checagens_dele test_gerar_starter.Trava
at AT-009 test_f17c_gerador.ModoWeb.test_at009_versao_que_nao_sobe_nas_3 test_gerar_starter.Recusa.test_at007_versao_que_nao_sobe_reprova_antes_de_gravar
at AT-010 test_f17c_textos.CaminhoDoOpen test_agnostico test_check_versions test_conversa test_skill_lint test_decisoes_lint test_f17b_textos test_f21_textos test_gerar_starter.ReadmeEInit.test_at010_o_init_nao_copia_scripts
rm -rf "$T"; echo "falhas=$falhas"; exit $falhas
