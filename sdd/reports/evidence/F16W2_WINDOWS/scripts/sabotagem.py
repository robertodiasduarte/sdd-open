"""Sabotagens da F16W2: cada mutante numa cópia nova de `git archive HEAD`; o teste que vigia a regra tem de cair.

uso: python3 -I sabotagem.py <repo> <pasta-de-trabalho>   (imprime uma linha por mutante e MORTO/VIVO)
"""
import os
import shutil
import subprocess
import sys

REPO, BASE = sys.argv[1], sys.argv[2]

MUTANTES = [
    ("S1 hook: NUL nunca achado", "sdd/hooks/pre-commit",
     '[ "${n:-0}" -gt 0 ] && achado H5', '[ "${n:-0}" -gt 99999 ] && achado H5',
     "test_f16w2_processos.Recusas"),
    ("S2 embutido sem a troca da saída", "sdd/bin/sdd-drive.sh",
     '        _sdd_c.reconfigure(encoding="utf-8", errors="replace", newline="\\n")', '        pass',
     "test_f16w2_saida.GuardaEmbutidos"),
    ("S11 hook: git grep com cor", "sdd/hooks/pre-commit",
     "git -c color.ui=never -c color.grep=never grep --no-color --cached", "git -c color.ui=always grep --color=always --cached",
     "test_f16w2_processos.Recusas"),
    ("S12 hook: nome sem LC_ALL=C", "sdd/hooks/pre-commit",
     '  local LC_ALL=C re="$1" resto="$2" l r=1', '  local re="$1" resto="$2" l r=1',
     "test_f16w2_processos.Recusas"),
    ("S13 checar: TMPDIR sem escrita perde a saída", ".agents/skills/sdd-checar-ambiente/scripts/checar.sh",
     '    if [ "${f}" = /dev/null ]; then\n      git -c http.lowSpeedLimit=1', '    if false; then\n      git -c http.lowSpeedLimit=1',
     "test_checar.TestRemoto.test_tmpdir_sem_escrita_nao_perde_a_resposta_do_remoto"),
    ("S3 design-lint sem a troca da saída", "sdd/bin/design-lint.py",
     '_canal.reconfigure(encoding="utf-8", errors="replace", newline="\\n")', 'pass',
     "test_f16w2_saida"),
    ("S4 vigia sem a marca", ".agents/skills/sdd-checar-ambiente/scripts/checar.sh",
     '[ -n "${m}" ] && [ -e "${m}" ] && r=137', ':',
     "test_checar.TestVigiaNoWindows"),
    ("S5 init: eh_binario nunca", "bin/sdd-open.sh",
     "eh_binario() { local LC_ALL=C x; IFS= read -r -d '' x < \"${1}\" 2>/dev/null; }",
     "eh_binario() { return 1; }",
     "test_f16w2_render"),
    ("S6 slot sem a rede do \\r", "sdd/bin/slot.sh",
     "LIDO=\"${LIDO//$'\\r'/}\"", ":",
     "test_f16w2_caminhos"),
    ("S7 validate_kb sem o drive", ".agents/skills/sdd-kb/scripts/validate_kb.py",
     'drive = re.match(r"^[A-Za-z]:[\\\\/]", teste)', "drive = None",
     "test_sdd_kb.Strict"),
    ("S8 alarme distingue maiúscula", ".agents/skills/sdd-higiene-dado/scripts/pre-commit.sh",
     "  shopt -s nocasematch\n  case \"${base}\" in", "  case \"${base}\" in",
     "test_f16w2_processos.Recusas"),
    ("S9 report-lint lê o stdin em cp1252", "sdd/bin/report-lint.py",
     'sys.stdin.buffer.read().decode("utf-8")', 'sys.stdin.buffer.read().decode("cp1252")',
     "test_f16w2_saida.SaidaCp1252"),
    ("S10 init: chmod +x esquecido", "bin/sdd-open.sh",
     'if [ -x "${fonte}" ]; then chmod +x "${dest}" || return 1', 'if false; then :',
     "test_f16w2_processos.Contagem.test_init_lanca_no_maximo_3_programas_por_arquivo_gerado"),
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
