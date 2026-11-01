# sdd/bin/adapters/claude.sh — adapter da engine `claude` (CLI Claude Code, modo -p) para
# sdd/bin/adversarial-review.sh. Lido com `source`; nunca executado sozinho.
#
# Contrato (igual nos 4 adapters):
#   adapter_disponivel [MODELO]          0 se a engine pode ser chamada agora
#   adapter_invocar MODELO PROMPT OUT ERR grava a saída bruta em OUT e o stderr em ERR
#                                         0 ok · 65 sem credencial · 66 CLI ausente · outro = falha
#   adapter_extrair OUT                   1 linha JSON: texto, tokens_entrada, tokens_saida, modelo, custo_usd
#   adapter_credencial                    1 linha: onde a credencial vive (vai no → do exit 65)
#
# Invocação: sem ferramenta nenhuma (--tools ""), sem CLAUDE.md/skills/hooks do usuário (--safe-mode),
# sem sessão gravada, prompt por stdin (diff grande estoura o ARG_MAX por argumento).
# ⚠️ bash 3.2.

adapter_disponivel() {
  command -v claude >/dev/null 2>&1
}

adapter_credencial() {
  echo "login da CLI claude (rode claude e entre na conta) ou a chave que a própria CLI usa"
}

adapter_invocar() {
  modelo="$1"; prompt="$2"; out="$3"; err="$4"
  command -v claude >/dev/null 2>&1 || return 66
  set -- -p --output-format json --tools "" --safe-mode --no-session-persistence
  if [ "$modelo" != "-" ] && [ -n "$modelo" ]; then
    set -- "$@" --model "$modelo"
  fi
  claude "$@" < "$prompt" > "$out" 2> "$err"
}

adapter_extrair() {
  python3 -B -c '
import json, sys
def objeto(t):
    i = t.find("{")
    while i >= 0:
        try:
            return json.JSONDecoder().raw_decode(t[i:])[0]
        except ValueError:
            i = t.find("{", i + 1)
    return {}
try:
    d = objeto(open(sys.argv[1], encoding="utf-8", errors="replace").read())
except OSError:
    d = {}
u = d.get("usage") or {}
ent = None
if isinstance(u.get("input_tokens"), int):
    ent = sum(int(u.get(k) or 0) for k in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))
sai = u.get("output_tokens") if isinstance(u.get("output_tokens"), int) else None
mu = d.get("modelUsage") or {}
modelo = max(mu, key=lambda k: (mu[k] or {}).get("costUSD") or 0) if mu else None
texto = d.get("result") if isinstance(d.get("result"), str) and not d.get("is_error") else ""
custo = d.get("total_cost_usd") if isinstance(d.get("total_cost_usd"), (int, float)) else None
print(json.dumps({"texto": texto, "tokens_entrada": ent, "tokens_saida": sai, "modelo": modelo,
                  "custo_usd": custo}, ensure_ascii=False))
' "$1"
}
