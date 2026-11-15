"""Sabotagens da F16W2: cada mutante numa cópia nova de `git archive HEAD`; o teste que vigia a regra tem de cair.

uso: python3 -I sabotagem.py <repo> <pasta-de-trabalho>   (imprime uma linha por mutante e MORTO/VIVO)
"""
import os
import shutil
import subprocess
import sys

REPO, BASE = sys.argv[1], sys.argv[2]

MUTANTES = [
    ("S13 checar: TMPDIR sem escrita perde a saída", ".agents/skills/sdd-checar-ambiente/scripts/checar.sh",
     '    if [ "${f}" = /dev/null ]; then\n      git -c http.lowSpeedLimit=1', '    if false; then\n      git -c http.lowSpeedLimit=1',
     "test_checar.TestRemoto.test_tmpdir_sem_escrita_nao_perde_a_resposta_do_remoto"),
    ("S9 report-lint lê o stdin em cp1252", "sdd/bin/report-lint.py",
     'sys.stdin.buffer.read().decode("utf-8")', 'sys.stdin.buffer.read().decode("cp1252")',
     "test_f16w2_saida.SaidaCp1252"),
]

for nome, arq, de, para, teste in MUTANTES:
    d = os.path.join(BASE, nome.split()[0])
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    subprocess.run("git -C '%s' archive HEAD | tar -x -C '%s'" % (REPO, d), shell=True, check=True)
    p = os.path.join(d, arq)
    t = open(p, encoding="utf-8").read()
    if t.count(de) < 1:
        print("%s: ALVO NÃO ACHADO em %s" % (nome, arq)); continue
    open(p, "w", encoding="utf-8").write(t.replace(de, para))
    r = subprocess.run([sys.executable, "-B", "-m", "unittest", teste], cwd=os.path.join(d, "tests"),
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=1800,
                       env=dict(os.environ, SDD_TEST_BASH="/bin/bash"))
    ultima = [l for l in (r.stdout + r.stderr).splitlines() if l.strip()][-1]
    print("%s → %s (%s; rc=%d)" % (nome, "MORTO" if r.returncode != 0 else "VIVO", ultima, r.returncode))
    shutil.rmtree(d, ignore_errors=True)
