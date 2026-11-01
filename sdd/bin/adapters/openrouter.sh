# sdd/bin/adapters/openrouter.sh — adapter da engine `openrouter` (API REST da OpenRouter) para
# sdd/bin/adversarial-review.sh. Lido com `source`; nunca executado sozinho.
# Contrato das 4 funções: ver o cabeçalho de sdd/bin/adapters/claude.sh.
#
# Privacidade: toda chamada leva provider.data_collection = "deny" (só provedores que não retêm nem
# treinam com o dado) e provider.require_parameters = true. A chave vem só de OPENROUTER_API_KEY, lida
# dentro do Python (nunca em argumento de processo, log ou arquivo). usage.include = true faz a resposta
# trazer usage.cost (o custo real da chamada). Uso: --reviewer openrouter:<slug> troca o modelo.
# SDD_REVIEW_OPENROUTER_URL troca a URL só nos testes (servidor local).
# ⚠️ bash 3.2.

adapter_disponivel() {
  [ -n "${OPENROUTER_API_KEY:-}" ]
}

adapter_credencial() {
  echo "OPENROUTER_API_KEY no ambiente (export OPENROUTER_API_KEY=… antes de rodar; nunca num arquivo do repositório)"
}

adapter_invocar() {
  modelo="$1"; prompt="$2"; out="$3"; err="$4"
  if [ -z "${OPENROUTER_API_KEY:-}" ]; then
    echo "OPENROUTER_API_KEY ausente" > "$err"
    return 65
  fi
  python3 -B -c '
import json, os, sys, urllib.request, urllib.error
modelo, prompt, out, err = sys.argv[1:5]
url = os.environ.get("SDD_REVIEW_OPENROUTER_URL") or "https://openrouter.ai/api/v1/chat/completions"
corpo = {
    "model": modelo,
    "messages": [{"role": "user", "content": open(prompt, encoding="utf-8", errors="replace").read()}],
    "provider": {"data_collection": "deny", "require_parameters": True},
    "usage": {"include": True},
}
req = urllib.request.Request(url, data=json.dumps(corpo).encode("utf-8"), method="POST", headers={
    "Authorization": "Bearer " + os.environ["OPENROUTER_API_KEY"],
    "Content-Type": "application/json",
    "X-Title": "sdd-open adversarial-review",
})
try:
    with urllib.request.urlopen(req, timeout=3600) as r:
        open(out, "wb").write(r.read())
    sys.exit(0)
except urllib.error.HTTPError as e:
    open(out, "wb").write(e.read() or ("HTTP %d" % e.code).encode())
    open(err, "w").write("HTTP %d\n" % e.code)
    sys.exit(1)
except Exception as e:
    open(err, "w").write("falha de rede: %s\n" % e)
    sys.exit(1)
' "$modelo" "$prompt" "$out" "$err"
}

adapter_extrair() {
  python3 -B -c '
import json, sys
try:
    d = json.loads(open(sys.argv[1], encoding="utf-8", errors="replace").read())
except (OSError, ValueError):
    d = {}
if not isinstance(d, dict):
    d = {}
ch = d.get("choices") or [{}]
texto = ((ch[0] or {}).get("message") or {}).get("content") if not d.get("error") else ""
u = d.get("usage") or {}
modelo = d.get("model")
if modelo and d.get("provider"):
    modelo = "%s via %s" % (modelo, d["provider"])
num = lambda v: v if isinstance(v, int) else None
custo = u.get("cost") if isinstance(u.get("cost"), (int, float)) else None
print(json.dumps({"texto": texto if isinstance(texto, str) else "", "tokens_entrada": num(u.get("prompt_tokens")),
                  "tokens_saida": num(u.get("completion_tokens")), "modelo": modelo, "custo_usd": custo},
                 ensure_ascii=False))
' "$1"
}
