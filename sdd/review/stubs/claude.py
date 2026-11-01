"""claude.py — stub da CLI `claude -p --output-format json` (formato medido em sdd/fixtures/revisao/saidas/claude.json):
um objeto JSON com result, total_cost_usd, usage e modelUsage. Lê o prompt do stdin. Ver comum.py."""
import json
import sys

from comum import custo, num, proximo, texto

entrada = sys.stdin.buffer.read()
n, c = proximo("claude", sys.argv[1:], entrada)
if c is None:
    sys.stderr.write("stub claude: chamada fora da fila do teste\n")
    sys.exit(99)
if c["status"] != "0":
    sys.stderr.write(c["falha"] + "\n")
    sys.exit(int(c["status"]))
te, ts = num(c["tokens_entrada"]), num(c["tokens_saida"])
saida = {"type": "result", "subtype": "success", "is_error": False, "duration_ms": 1200, "num_turns": 1,
         "result": texto(c), "session_id": "stub-sessao-claude", "total_cost_usd": custo(c["custo"]),
         "usage": {"input_tokens": te, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0,
                   "output_tokens": ts},
         # costUSD por modelo diferente do total de propósito: o gate prova que o custo vem de total_cost_usd
         "modelUsage": {c["modelo"]: {"inputTokens": te, "outputTokens": ts,
                                      "costUSD": round(custo(c["custo"]) / 2, 6) if custo(c["custo"]) else None}}}
sys.stdout.write(json.dumps(saida, ensure_ascii=False))
