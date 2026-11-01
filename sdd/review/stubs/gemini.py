"""gemini.py — stub do `gemini -o json` (formato medido em sdd/fixtures/revisao/saidas/gemini.json): um objeto JSON
com response e stats.models.<modelo>.tokens (prompt, candidates). Não reporta custo. Lê o prompt do stdin.
Ver comum.py."""
import json
import sys

from comum import num, proximo, texto

entrada = sys.stdin.buffer.read()
n, c = proximo("gemini", sys.argv[1:], entrada)
if c is None:
    sys.stderr.write("stub gemini: chamada fora da fila do teste\n")
    sys.exit(99)
if c["status"] != "0":
    sys.stderr.write(c["falha"] + "\n")
    sys.exit(int(c["status"]))
te, ts = num(c["tokens_entrada"]), num(c["tokens_saida"])
saida = {"session_id": "stub-sessao-gemini", "response": texto(c),
         "stats": {"models": {c["modelo"]: {"api": {"totalRequests": 1, "totalErrors": 0},
                                            "tokens": {"prompt": te, "candidates": ts, "total": te + ts, "cached": 0}}},
                   "tools": {"totalCalls": 0}}}
sys.stdout.write(json.dumps(saida, ensure_ascii=False, indent=2))
