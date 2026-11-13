#!/usr/bin/env bash
# at-logs.sh: um log por AT da F17b numa cópia de git archive do HEAD; 1ª linha "$ comando", fim "rc=N"
W=/Users/robertoduarte/rdd-worktrees/sdd-open-f17b-starter-etapa2; E="$W/sdd/reports/evidence/F17B_STARTER_ETAPA2"
C="$(git -C "$W" rev-parse --short HEAD)"; T="$(mktemp -d)"; git -C "$W" archive HEAD | tar -x -C "$T"; falhas=0
at() { local id="$1"; shift
  { echo "\$ cd <git archive $C>/tests && SDD_TEST_BASH=/bin/bash python3 -B -m unittest -v $*"
    (cd "$T/tests" && SDD_TEST_BASH=/bin/bash python3 -B -m unittest -v "$@" 2>&1); rc=$?; echo "rc=$rc"; } > "$E/$id.log"
  grep -q '^rc=0$' "$E/$id.log" || falhas=$((falhas+1)); echo "$id $(tail -1 "$E/$id.log")"; }
at AT-001 test_gerar_starter.Gera.test_at001_gera_as_15_e_nao_toca_no_resto test_gerar_starter.Gera.test_at005_duas_geracoes_iguais_byte_a_byte
at AT-002 test_gerar_starter.SkillDeModo.test_at002_release_gerada_so_do_modo test_gerar_starter.SkillDeModo.test_at002_arquivo_citado_pelo_modo_vai_junto_com_o_fecho
at AT-003 test_gerar_starter.SkillDeModo.test_at003_modo_quebrado_sai_65_sem_gravar test_gerar_starter.SkillDeModo.test_at003_a_release_crua_reprova_no_lint
at AT-004 test_f17b_textos.ModoIniciante
at AT-005 test_f17b_textos.SemTerminal
at AT-006 test_gerar_starter.CaminhoDoIniciante test_f17b_textos.CaminhoCurto
at AT-007 test_f17b_textos.UxReviewBuilder test_skill_lint test_sdd_open.Projeto.test_init_instala_a_ux_review_builder
at AT-008 test_gerar_starter.Gera.test_at007_o_starter_passa_nas_checagens_dele test_gerar_starter.Trava
at AT-009 test_gerar_starter.SkillDeModo.test_at009_versao_que_nao_sobe_numa_skill_nova_da_lista test_gerar_starter.Recusa.test_at007_versao_que_nao_sobe_reprova_antes_de_gravar
at AT-010 test_agnostico test_check_versions test_conversa test_f17b_textos.ModoIniciante.test_o_open_aponta_o_modo_e_a_release_fica_no_teto test_gerar_starter.ReadmeEInit.test_at010_o_init_nao_copia_scripts test_sdd_open.Projeto.test_doctor_avisa_a_ux_review_builder_do_starter
rm -rf "$T"; echo "falhas=$falhas"; exit $falhas
