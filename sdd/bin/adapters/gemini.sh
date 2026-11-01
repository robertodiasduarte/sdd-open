# sdd/bin/adapters/gemini.sh — adapter da engine `gemini` (Gemini CLI) para
# sdd/bin/adversarial-review.sh. Lido com `source`; nunca executado sozinho.
# Contrato das 4 funções: ver o cabeçalho de sdd/bin/adapters/claude.sh.
#
# Invocação: saída JSON (-o json), aprovação manual de ferramenta (--approval-mode default: sem terminal,
# nenhuma ferramenta que pede aprovação roda), prompt por stdin, pasta temporária vazia. O gemini não
# reporta custo: o META usa o registry. Sem projeto Google configurado, a CLI sai com
# ProjectIdRequiredError — o registry trata como falha de credencial (65).
# ⚠️ bash 3.2.

adapter_disponivel() {
  command -v gemini >/dev/null 2>&1
}

adapter_credencial() {
  echo "login da CLI gemini e a variável GOOGLE_CLOUD_PROJECT, ou GEMINI_API_KEY no ambiente"
}

adapter_invocar() {
  modelo="$1"; prompt="$2"; out="$3"; err="$4"
  command -v gemini >/dev/null 2>&1 || return 66
  set -- -o json --approval-mode default
  if [ "$modelo" != "-" ] && [ -n "$modelo" ]; then
    set -- "$@" -m "$modelo"
  fi
  gemini "$@" < "$prompt" > "$out" 2> "$err"
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
modelos = ((d.get("stats") or {}).get("models")) or {}
modelo = next(iter(modelos), None)
tok = ((modelos.get(modelo) or {}).get("tokens") or {}) if modelo else {}
ent = tok.get("prompt") if isinstance(tok.get("prompt"), int) else None
sai = tok.get("candidates") if isinstance(tok.get("candidates"), int) else None
texto = d.get("response") if isinstance(d.get("response"), str) and not d.get("error") else ""
print(json.dumps({"texto": texto, "tokens_entrada": ent, "tokens_saida": sai, "modelo": modelo,
                  "custo_usd": None}, ensure_ascii=False))
' "$1"
}
