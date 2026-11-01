"""openrouter.py — stub da API de chat da OpenRouter (formato medido em sdd/fixtures/revisao/saidas/openrouter.json):
servidor HTTP só em 127.0.0.1, porta livre escrita em SDD_STUB_ESTADO/openrouter.porta. Responde choices, model,
provider e usage (cost quando o cenário reporta). Cada requisição grava o corpo em openrouter.<n>.entrada e o header
Authorization em openrouter.<n>.auth. Requisição fora da fila = sentinela + HTTP 599 (nenhum sinal do registry casa).
O gate sobe um servidor por cenário, com a fila daquele cenário no ambiente. Ver comum.py."""
import http.server
import json
import os
import sys

from comum import custo, num, proximo, texto


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def responde(self, status, corpo):
        dados = corpo.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(dados)))
        self.end_headers()
        self.wfile.write(dados)

    def do_POST(self):
        corpo = self.rfile.read(int(self.headers.get("Content-Length") or 0))
        n, c = proximo("openrouter", [self.path], corpo)
        est = os.environ.get("SDD_STUB_ESTADO") or ""
        if est and n:
            with open(os.path.join(est, "openrouter.%d.auth" % n), "w", encoding="utf-8") as h:
                h.write(self.headers.get("Authorization") or "")
        if c is None:
            self.responde(599, "sentinela")
            return
        if c["status"] != "200":
            self.responde(int(c["status"]), c["falha"])
            return
        uso = {"prompt_tokens": num(c["tokens_entrada"]), "completion_tokens": num(c["tokens_saida"]),
               "total_tokens": num(c["tokens_entrada"]) + num(c["tokens_saida"])}
        if custo(c["custo"]) is not None:
            uso["cost"] = custo(c["custo"])
        self.responde(200, json.dumps({
            "id": "gen-stub-%d" % n, "provider": "StubProvider", "model": c["modelo"], "object": "chat.completion",
            "choices": [{"index": 0, "finish_reason": "stop",
                         "message": {"role": "assistant", "content": texto(c)}}],
            "usage": uso}, ensure_ascii=False))


def main():
    est = os.environ.get("SDD_STUB_ESTADO") or ""
    if not est:
        sys.stderr.write("openrouter.py: SDD_STUB_ESTADO vazio\n")
        sys.exit(64)
    srv = http.server.HTTPServer(("127.0.0.1", 0), Handler)
    tmp = os.path.join(est, "openrouter.porta.tmp")
    with open(tmp, "w") as h:
        h.write(str(srv.server_address[1]))
    os.replace(tmp, os.path.join(est, "openrouter.porta"))
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        srv.server_close()


if __name__ == "__main__":
    main()
