"""Baseline do L4 do ciclo 2: a função afirma_sdd_fora_do_git() de um test_docs.py (caminho em argv[1])
contra as 4 paráfrases do avaliador. Exit 0 = pegou as 4; 1 = deixou passar alguma."""
import importlib.util
import sys

spec = importlib.util.spec_from_file_location("v", sys.argv[1])
v = importlib.util.module_from_spec(spec)
sys.path.insert(0, sys.argv[2])  # a pasta tests/ da árvore, para o import de apoio
spec.loader.exec_module(v)
frases = ("A pasta `sdd/` fica só no seu computador, fora do GitHub.",
          "A pasta `sdd/` está no `.gitignore`.",
          "Não suba a pasta `sdd/` para o GitHub.",
          "Os arquivos de `sdd/` não são enviados ao GitHub.")
falhas = 0
for f in frases:
    pego = bool(v.afirma_sdd_fora_do_git(f))
    falhas += 0 if pego else 1
    print(("pego      " if pego else "NÃO PEGO  ") + f)
sys.exit(1 if falhas else 0)
