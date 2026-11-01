# stub.sh — adapter de TESTE de sdd/bin/adversarial-review.sh (tests/test_revisao.py). Nunca chama rede.
# Ligado por SDD_REVIEW_ADAPTERS=sdd/fixtures/revisao/adapters e pelo registry-stub.tsv.
#
# O MODELO nomeia o cenário: uma resposta em ../respostas/<cenario>.md (sai 0) ou <cenario>.txt (texto de
# falha, sai 1); "dorme" (passa de qualquer teto), "sem-cli" (66), "sem-chave" (65). Uma lista "a+b"
# responde a na 1ª chamada e b nas seguintes (contador em SDD_REVIEW_STUB_ESTADO). Modelo começado por
# "off" = engine indisponível. SDD_REVIEW_STUB_ESTADO também recebe uma cópia de cada prompt.
# SDD_REVIEW_STUB_RESPOSTAS troca a pasta das respostas (cópia do stub como 2º adapter).
# SDD_REVIEW_STUB_CUSTO = custo (US$) que a "engine" reporta; vazio = não reporta.
# ⚠️ bash 3.2.

STUB_DIR="$(cd "$(dirname "$BASH_SOURCE")" && pwd)"
RESP="${SDD_REVIEW_STUB_RESPOSTAS:-$STUB_DIR/../respostas}"

adapter_disponivel() {
  case "${1:-}" in off*) return 1 ;; esac
  return 0
}

adapter_credencial() {
  echo "credencial do stub (exemplo de teste)"
}

adapter_invocar() {
  modelo="$1"; prompt="$2"; out="$3"; err="$4"
  cen="$modelo"
  est="${SDD_REVIEW_STUB_ESTADO:-}"
  if [ -n "$est" ]; then
    mkdir -p "$est"
    k=$(ls "$est" | grep -c '^prompt-' )
    cp "$prompt" "$est/prompt-$((k + 1)).md"
    chave=$(printf '%s' "$modelo" | tr -c 'A-Za-z0-9' '_')
    n=0
    [ -f "$est/conta-$chave" ] && n=$(cat "$est/conta-$chave")
    n=$((n + 1))
    printf '%s' "$n" > "$est/conta-$chave"
    case "$modelo" in
      *+*)
        if [ "$n" -le 1 ]; then cen="${modelo%%+*}"; else cen="${modelo#*+}"; fi ;;
    esac
  fi
  case "$cen" in
    dorme) sleep 30; return 0 ;;
    sem-cli) return 66 ;;
    sem-chave) echo "chave ausente" > "$err"; return 65 ;;
  esac
  if [ -f "$RESP/$cen.md" ]; then
    cp "$RESP/$cen.md" "$out"; return 0
  fi
  if [ -f "$RESP/$cen.txt" ]; then
    cp "$RESP/$cen.txt" "$out"; return 1
  fi
  echo "cenário desconhecido: $cen" > "$err"
  return 1
}

adapter_extrair() {
  python3 -B -c '
import json, os, sys
try:
    t = open(sys.argv[1], encoding="utf-8").read()
except OSError:
    t = ""
c = os.environ.get("SDD_REVIEW_STUB_CUSTO")
print(json.dumps({"texto": t, "tokens_entrada": 1000 if t else None, "tokens_saida": 200 if t else None,
                  "modelo": "stub-modelo", "custo_usd": float(c) if c else None}, ensure_ascii=False))
' "$1"
}
