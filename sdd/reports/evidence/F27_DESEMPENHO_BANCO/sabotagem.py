"""Mutantes da F27, numa cópia de git archive (LM-009): cada um tem de derrubar o teste nomeado."""
import os, shutil, subprocess, sys
copia = sys.argv[1]
V = "sdd/bin/desempenho-varredura.sh"; D = "sdd/bin/desempenho-diagnostico.sh"
MUT = [
 ("varredura sai 2 em vez de 1", V, 'rc, palavra, seta = 1, "AVISOS"', 'rc, palavra, seta = 2, "AVISOS"',
  "test_desempenho_varredura.Padroes.test_p01_politica_sem_select"),
 ("dispensa sem motivo aceita", V, 'if len(re.sub(r"\\s", "", motivo)) >= 3:', 'if True:',
  "test_desempenho_varredura.Dispensa.test_dispensa_sem_motivo_curta_ou_de_outro_item_nao_vale"),
 ("ficha de Supabase sem Supabase", V, 'ATIVOS = [f for f in ITENS if f["c"]["stack"] == "todas" or f["c"]["stack"] in STACK]', 'ATIVOS = list(ITENS)',
  "test_desempenho_varredura.Stack.test_postgres_sem_supabase_so_as_fichas_de_todas"),
 ("coleta sem consentimento", D, 'if op["--coletar"] and not op["--consentimento"]:', 'if False:',
  "test_desempenho_diagnostico.Consentimento.test_sem_consentimento_nada_roda"),
 ("índice não usado sem idade vira candidato", D, '    if DESDE is None:\n        passo = ("idade', '    if False:\n        passo = ("idade',
  "test_desempenho_diagnostico.Interpretacao.test_indice_nao_usado_e_a_idade_das_estatisticas"),
 ("legado conta como novo", V, 'if BASE is not None and na_base.get(k, 0) > 0:', 'if False:',
  "test_desempenho_varredura.Legado.test_achado_antigo_vira_contagem_e_nada_novo"),
]
env = dict(os.environ, SDD_TEST_BASH="/bin/bash")
falhou = 0
for nome, arq, antes, depois, teste in MUT:
    p = os.path.join(copia, arq)
    orig = open(p, encoding="utf-8").read()
    assert orig.count(antes) == 1, (nome, orig.count(antes))
    open(p, "w", encoding="utf-8").write(orig.replace(antes, depois))
    r = subprocess.run(["/usr/bin/python3", "-B", "-m", "unittest", teste], cwd=os.path.join(copia, "tests"),
                       env=env, capture_output=True, text=True, encoding="utf-8")
    open(p, "w", encoding="utf-8").write(orig)
    morto = r.returncode != 0
    print("%s mutante: %s → %s (%s)" % ("✅" if morto else "❌", nome, "MORTO" if morto else "VIVO", teste))
    falhou += 0 if morto else 1
print("[exit=%d]" % falhou)
sys.exit(falhou)
