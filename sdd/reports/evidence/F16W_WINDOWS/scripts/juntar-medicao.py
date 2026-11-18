#!/usr/bin/env python3
"""juntar-medicao.py <pasta com testes-windows-fatia-N/resumo.tsv>: tabela markdown por módulo, ordenada por estado."""
import sys
from pathlib import Path

base = Path(sys.argv[1])
linhas, fatias = [], {}
for tsv in sorted(base.glob("testes-windows-fatia-*/resumo.tsv")):
    f = tsv.parent.name.rsplit("-", 1)[-1]
    for l in tsv.read_text(encoding="utf-8").splitlines()[1:]:
        m, est, t, fa, er, pu, seg = l.split("\t")
        linhas.append((est, m, f, int(t), int(fa), int(er), int(pu), float(seg)))
        fatias[f] = fatias.get(f, 0.0) + float(seg)
ordem = {"TETO": 0, "ERRO": 1, "FALHOU": 2, "OK": 3}
linhas.sort(key=lambda x: (ordem.get(x[0], 9), x[1]))
tot = [sum(x[i] for x in linhas) for i in (3, 4, 5, 6)]
print("| unidade | fatia | estado | testes | falhas | erros | pulados | s |\n|---|---|---|---|---|---|---|---|")
for est, m, f, t, fa, er, pu, seg in linhas:
    print("| %s | %s | %s | %d | %d | %d | %d | %.0f |" % (m, f, est, t, fa, er, pu, seg))
por = {}
for x in linhas:
    por[x[0]] = por.get(x[0], 0) + 1
print("\n**%d unidades** (%s); **%d testes**: %d falhas, %d erros, %d pulados." % (
    len(linhas), ", ".join("%s %d" % kv for kv in sorted(por.items())), *tot))
print("Tempo por fatia (s, soma dos módulos): " + ", ".join("%s=%.0f" % kv for kv in sorted(fatias.items(), key=lambda k: int(k[0]))))
