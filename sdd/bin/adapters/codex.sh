# sdd/bin/adapters/codex.sh — adapter da engine `codex` (Codex CLI, `codex exec`) para
# sdd/bin/adversarial-review.sh. Lido com `source`; nunca executado sozinho.
# Contrato das 4 funções: ver o cabeçalho de sdd/bin/adapters/claude.sh.
#
# Invocação: sandbox somente leitura (-s read-only: o modelo pode ler, nunca escrever), fora de
# repositório git (--skip-git-repo-check, a pasta é temporária e vazia), sem sessão gravada (--ephemeral),
# eventos em JSONL (--json), prompt por stdin (`-`). O codex não reporta custo: o META usa o registry.
# F23B3: a saída não traz o modelo (medido em 2026-11-16); adapter_modelo_padrao o lê do config.toml. Os tokens saem
# no significado da B1: entrada SEM o cache lido (o codex o conta dentro de input_tokens), cache lido e criado à parte;
# cache criado > 0 sai None (não se mediu se ele também está dentro da entrada).
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
texto, ent, sai, lido, criado, erro = "", None, None, None, None, False
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
        bruto = u.get("input_tokens") if isinstance(u.get("input_tokens"), int) else None
        sai = u.get("output_tokens") if isinstance(u.get("output_tokens"), int) else None
        c = u.get("cached_input_tokens")
        lido = c if isinstance(c, int) and bruto is not None and 0 <= c <= bruto else None
        ent = bruto - lido if lido is not None else bruto
        w = u.get("cache_write_input_tokens")
        criado = 0 if w == 0 else None   # ausente ou > 0: não se sabe (n/d, nunca zero)
    elif t in ("error", "turn.failed"):
        erro = True
print(json.dumps({"texto": "" if erro else texto, "tokens_entrada": ent, "tokens_saida": sai,
                  "tokens_cache_lido": lido, "tokens_cache_criado": criado,
                  "modelo": None, "custo_usd": None}, ensure_ascii=False))
' "$1"
}

adapter_modelo_padrao() {
  # O modelo que o codex usa sem -m: a linha `model = "…"` do topo do config.toml (antes da 1ª [seção]).
  # Perfil e -c não entram (o adapter não os usa). Nome fora do formato = nada (exit 1).
  python3 -B -c '
import re, sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", newline="\n")
except (AttributeError, ValueError):
    pass
try:
    linhas = open(sys.argv[1], encoding="utf-8", errors="replace").read().splitlines()
except OSError:
    sys.exit(1)
for ln in linhas:
    if ln.lstrip().startswith("["):
        break
    m = re.match(r"^\s*model\s*=\s*\"([A-Za-z0-9._:/@-]{1,80})\"\s*(?:#.*)?\Z", ln)
    if m:
        print(m.group(1))
        sys.exit(0)
sys.exit(1)
' "${CODEX_HOME:-$HOME/.codex}/config.toml"
}
