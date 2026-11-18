#!/usr/bin/env python3
"""rejulgar.py <log>…: julga de novo, com os juízes atuais de iniciante2.py, as respostas gravadas em logs do iniciante (build)."""
import importlib.util, re, sys
from pathlib import Path
spec = importlib.util.spec_from_file_location("j", Path(__file__).resolve().parent / "iniciante2.py")
j = importlib.util.module_from_spec(spec); spec.loader.exec_module(j)
falhas = 0
for f in sys.argv[1:]:
    t = Path(f).read_text(encoding="utf-8")
    resp = re.findall(r"----- volta \d+ — skill \([^)]*\) -----\n(.*?)(?=\n----- volta \d+ — aluno|\n===== veredito)", t, re.S)
    a = j.julgar("build", resp, [], any(j.entregou("build", r, []) for r in resp))
    falhas += bool(a)
    print("%s: %d volta(s) · %s" % (Path(f).name, len(resp), "PASSA" if not a else "REPROVA " + " | ".join(x[:90] for x in a)))
sys.exit(0)
