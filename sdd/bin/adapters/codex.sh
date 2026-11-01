# sdd/bin/adapters/codex.sh — adapter da engine `codex` (Codex CLI, `codex exec`) para
# sdd/bin/adversarial-review.sh. Lido com `source`; nunca executado sozinho.
# Contrato das 4 funções: ver o cabeçalho de sdd/bin/adapters/claude.sh.
#
# Invocação: sandbox somente leitura (-s read-only: o modelo pode ler, nunca escrever), fora de
# repositório git (--skip-git-repo-check, a pasta é temporária e vazia), sem sessão gravada (--ephemeral),
# eventos em JSONL (--json), prompt por stdin (`-`). O codex não reporta custo: o META usa o registry.
# ⚠️ bash 3.2.

adapter_disponivel() {
  command -v codex >/dev/null 2>&1
}

adapter_credencial() {
  echo "login da CLI codex (rode codex login)"
}

adapter_invocar() {
  modelo="$1"; prompt="$2"; out="$3"; err="$4"
  command -v codex >/dev/null 2>&1 || return 66
  set -- exec -s read-only --skip-git-repo-check --ephemeral --json
  if [ "$modelo" != "-" ] && [ -n "$modelo" ]; then
    set -- "$@" -m "$modelo"
  fi
  codex "$@" - < "$prompt" > "$out" 2> "$err"
}

adapter_extrair() {
  python3 -B -c '
import json, sys
texto, ent, sai, erro = "", None, None, False
try:
    linhas = open(sys.argv[1], encoding="utf-8", errors="replace").read().splitlines()
except OSError:
    linhas = []
for ln in linhas:
    try:
        d = json.loads(ln)
    except ValueError:
        continue
    if not isinstance(d, dict):
        continue
    t = d.get("type")
    item = d.get("item") or {}
    if t == "item.completed" and item.get("type") == "agent_message" and isinstance(item.get("text"), str):
        texto = item["text"]
    elif t == "turn.completed":
        u = d.get("usage") or {}
        ent = u.get("input_tokens") if isinstance(u.get("input_tokens"), int) else None
        sai = u.get("output_tokens") if isinstance(u.get("output_tokens"), int) else None
    elif t in ("error", "turn.failed"):
        erro = True
print(json.dumps({"texto": "" if erro else texto, "tokens_entrada": ent, "tokens_saida": sai,
                  "modelo": None, "custo_usd": None}, ensure_ascii=False))
' "$1"
}
