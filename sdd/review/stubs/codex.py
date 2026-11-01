"""codex.py — stub do `codex exec --json` (formato medido em sdd/fixtures/revisao/saidas/codex.jsonl): JSONL com
thread.started, turn.started, item.completed (agent_message) e turn.completed (usage). Não reporta modelo nem custo.
Lê o prompt do stdin (`codex exec … -`). Ver comum.py."""
import json
import sys

from comum import num, proximo, texto

entrada = sys.stdin.buffer.read()
n, c = proximo("codex", sys.argv[1:], entrada)
if c is None:
    sys.stderr.write("stub codex: chamada fora da fila do teste\n")
    sys.exit(99)
eventos = [{"type": "thread.started", "thread_id": "stub-thread-codex"}, {"type": "turn.started"}]
if c["status"] != "0":
    sys.stdout.write("\n".join(json.dumps(e) for e in eventos + [{"type": "turn.failed"}]) + "\n")
    sys.stderr.write(c["falha"] + "\n")
    sys.exit(int(c["status"]))
eventos += [{"type": "item.completed", "item": {"id": "item_0", "type": "agent_message", "text": texto(c)}},
            {"type": "turn.completed", "usage": {"input_tokens": num(c["tokens_entrada"]), "cached_input_tokens": 0,
                                                 "output_tokens": num(c["tokens_saida"]), "reasoning_output_tokens": 0}}]
sys.stdout.write("\n".join(json.dumps(e, ensure_ascii=False) for e in eventos) + "\n")
