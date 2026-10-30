#!/usr/bin/env bash
# merge.sh — merges idempotentes em arquivos que o usuário pode já ter.
#
#   merge_agents_md <destino> <arquivo-com-o-corpo>   bloco marcado em AGENTS.md
#   merge_gemini_settings <destino>                   context.fileName em .gemini/settings.json
#
# Regra: preservar byte a byte tudo que é do usuário. Na dúvida, recusar e explicar — nunca
# adivinhar onde um bloco termina nem reescrever um JSON "mais ou menos".
#
# ⚠️ bash 3.2 · ${VAR} com chaves antes de não-ASCII · saída via say.sh (die = causa + conserto).

ABRE='<sdd-open-instructions>'
FECHA='</sdd-open-instructions>'

# Exit codes próprios deste módulo (65 = marcadores; 66 = JSON), documentados em cli-conventions.
# EOL: arquivo com CRLF (Git Bash no Windows) mantém CRLF; sem newline final mantém sem (AT-005:
# byte a byte fora dos marcadores — achado do avaliador fresco, ciclo 2).
_eol_de() { if grep -q $'\r' "${1}" 2>/dev/null; then printf '\r'; fi; }
_sem_newline_final() { [ -n "$(tail -c1 "${1}" 2>/dev/null)" ]; }
_tirar_newline_final() { local tmp="${1}.sddnl"; printf '%s' "$(cat "${1}")" > "${tmp}" && mv "${tmp}" "${1}"; }

merge_agents_md() { # $1=destino  $2=corpo
  local dest="${1}" corpo="${2}" n_abre n_fecha l_abre l_fecha eol sem_nl=0

  if [ ! -f "${dest}" ]; then
    { printf '%s\n' "${ABRE}"; cat "${corpo}"; printf '%s\n' "${FECHA}"; } > "${dest}"
    return 0
  fi
  eol="$(_eol_de "${dest}")"; _sem_newline_final "${dest}" && sem_nl=1

  # Marcador tem de ocupar a LINHA INTEIRA (tolerando \r no fim): os dois na mesma linha passariam na
  # contagem e na ordem, o awk entraria no bloco e nunca veria o fechamento — apagando tudo depois
  # (achado P1 do codex). Menção em prosa (com outro texto na linha) é ignorada de propósito.
  n_abre=$(grep -cE "^${ABRE}"$'\r'"?\$" "${dest}" || true)
  n_fecha=$(grep -cE "^${FECHA}"$'\r'"?\$" "${dest}" || true)
  if [ "${n_abre}" -ne "${n_fecha}" ] || [ "${n_abre}" -gt 1 ]; then
    die "${dest}: marcadores ${ABRE} desbalanceados ou duplicados (${n_abre} abertura, ${n_fecha} fechamento, contando só linhas inteiras)" \
        "deixe exatamente um par de marcadores, cada um sozinho na linha, e rode sync de novo — nada foi alterado" 65
  fi
  if [ "${n_abre}" -eq 1 ]; then
    l_abre=$(grep -nE "^${ABRE}"$'\r'"?\$" "${dest}" | cut -d: -f1)
    l_fecha=$(grep -nE "^${FECHA}"$'\r'"?\$" "${dest}" | cut -d: -f1)
    if [ "${l_fecha}" -le "${l_abre}" ]; then
      die "${dest}: marcador de fechamento (linha ${l_fecha}) aparece ANTES da abertura (linha ${l_abre})" \
          "corrija a ordem dos marcadores e rode sync de novo — nada foi alterado" 65
    fi
  fi

  if [ "${n_abre}" -eq 0 ]; then
    # Anexa ao fim preservando o EOL do arquivo; se não havia newline final, acrescenta um antes.
    { [ "${sem_nl}" = "1" ] && printf '%s\n' "${eol}"; printf '%s%s\n%s%s\n' "" "${eol}" "${ABRE}" "${eol}"
      sed "s/\$/${eol}/" "${corpo}"; printf '%s%s\n' "${FECHA}" "${eol}"; } >> "${dest}"
    return 0
  fi

  awk -v abre="${ABRE}" -v fecha="${FECHA}" -v corpo="${corpo}" -v eol="${eol}" '
    $0 == abre || $0 == abre "\r"   { print; while ((getline l < corpo) > 0) print l eol; close(corpo); dentro=1; next }
    $0 == fecha || $0 == fecha "\r" { print; dentro=0; next }
    !dentro { print }
  ' "${dest}" > "${dest}.sddtmp" && mv "${dest}.sddtmp" "${dest}"
  [ "${sem_nl}" = "1" ] && _tirar_newline_final "${dest}"
  return 0
}

# Devolve 0 se o bloco em <dest> já é idêntico ao corpo (para o plano marcar "=").
agents_md_em_dia() { # $1=destino $2=corpo
  local dest="${1}" corpo="${2}"
  [ -f "${dest}" ] || return 1
  awk -v abre="${ABRE}" -v fecha="${FECHA}" '
    $0 == abre || $0 == abre "\r"   { dentro=1; next }
    $0 == fecha || $0 == fecha "\r" { dentro=0; next }
    dentro { sub(/\r$/, ""); print }
  ' "${dest}" | cmp -s - "${corpo}"
}

# .gemini/settings.json: acrescenta AGENTS.md a context.fileName sem perder nenhuma chave.
# JSON inválido é ERRO nomeando a linha — nunca sobrescreve o arquivo do usuário.
merge_gemini_settings() { # $1=destino
  local dest="${1}" saida rc
  command -v python3 >/dev/null 2>&1 || die "o adaptador gemini precisa de python3 para editar .gemini/settings.json com segurança" \
    "instale python3 ou rode init sem o vendor gemini" 64
  mkdir -p "$(dirname "${dest}")"
  saida=$(python3 -I - "${dest}" <<'PY' 2>&1
import json, os, sys
dest = sys.argv[1]
data = {}
if os.path.exists(dest):
    with open(dest, encoding="utf-8") as f:
        raw = f.read()
    if raw.strip():
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            print(f"JSONERR {e.lineno}: {e.msg}")
            sys.exit(66)
    if not isinstance(data, dict):
        print("JSONERR 1: o topo do arquivo não é um objeto")
        sys.exit(66)
ctx = data.setdefault("context", {})
if not isinstance(ctx, dict):
    print("JSONERR 1: 'context' não é um objeto")
    sys.exit(66)
fn = ctx.get("fileName", [])
if isinstance(fn, str):
    fn = [fn]
if "AGENTS.md" not in fn:
    fn = list(fn) + ["AGENTS.md"]
    ctx["fileName"] = fn
    with open(dest, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("ALTERADO")
else:
    ctx["fileName"] = fn
    print("EMDIA")
PY
  ); rc=$?
  case "${rc}" in
    0) return 0 ;;
    66) die "${dest} não é JSON válido (${saida#JSONERR })" \
            "corrija ou renomeie o arquivo e rode sync de novo — nada foi alterado" 66 ;;
    *) die "falha inesperada ao editar ${dest} (python3 saiu ${rc}): ${saida}" \
           "verifique o arquivo manualmente" 1 ;;
  esac
}

# 0 se AGENTS.md já está em context.fileName (para o plano marcar "=").
gemini_settings_em_dia() { # $1=destino
  [ -f "${1}" ] || return 1
  python3 -I - "${1}" <<'PY' >/dev/null 2>&1
import json, sys
d = json.load(open(sys.argv[1], encoding="utf-8"))
fn = d.get("context", {}).get("fileName", [])
fn = [fn] if isinstance(fn, str) else fn
sys.exit(0 if "AGENTS.md" in fn else 1)
PY
}

# .claude/settings.json: acrescenta as 2 entradas de hook do sdd-open (os guards gerados em .claude/hooks/)
# a hooks.PreToolUse, sem perder chave nem entrada de outra origem. Uma entrada do open conta como presente
# quando algum item da lista tem um comando que cita o nome do script. JSON inválido é ERRO nomeando a
# linha — nunca sobrescreve o arquivo do usuário. Mesma casca do merge do Gemini.
merge_claude_settings() { # $1=destino
  local dest="${1}" saida rc
  command -v python3 >/dev/null 2>&1 || die "o adaptador claude precisa de python3 para editar .claude/settings.json com segurança (e para os guards de .claude/hooks/)" \
    "instale python3 ou rode init sem o vendor claude" 64
  mkdir -p "$(dirname "${dest}")"
  saida=$(python3 -I - "${dest}" <<'PY' 2>&1
import json, os, sys
dest = sys.argv[1]
ENTRADAS = (
    ("Write|Edit|MultiEdit", 'python3 "$CLAUDE_PROJECT_DIR/.claude/hooks/sdd-report-guard.py"', 10),
    ("Agent|Task", 'python3 "$CLAUDE_PROJECT_DIR/.claude/hooks/sdd-avaliador-guard.py"', None),
)
data = {}
if os.path.exists(dest):
    with open(dest, encoding="utf-8") as f:
        raw = f.read()
    if raw.strip():
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            print(f"JSONERR {e.lineno}: {e.msg}"); sys.exit(66)
    if not isinstance(data, dict):
        print("JSONERR 1: o topo do arquivo não é um objeto"); sys.exit(66)
hooks = data.setdefault("hooks", {})
if not isinstance(hooks, dict):
    print("JSONERR 1: 'hooks' não é um objeto"); sys.exit(66)
pre = hooks.setdefault("PreToolUse", [])
if not isinstance(pre, list):
    print("JSONERR 1: 'hooks.PreToolUse' não é uma lista"); sys.exit(66)

def presente(nome):
    for e in pre:
        if not isinstance(e, dict):
            continue
        for h in e.get("hooks") or []:
            if isinstance(h, dict) and nome in str(h.get("command", "")):
                return True
    return False

alterado = False
for matcher, cmd, timeout in ENTRADAS:
    nome = cmd.rsplit("/", 1)[-1].rstrip('"')
    if presente(nome):
        continue
    h = {"type": "command", "command": cmd}
    if timeout:
        h["timeout"] = timeout
    pre.append({"matcher": matcher, "hooks": [h]})
    alterado = True
if alterado:
    with open(dest, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("ALTERADO")
else:
    print("EMDIA")
PY
  ); rc=$?
  case "${rc}" in
    0) return 0 ;;
    66) die "${dest} não é JSON válido (${saida#JSONERR })" \
            "corrija ou renomeie o arquivo e rode sync de novo — nada foi alterado" 66 ;;
    *) die "falha inesperada ao editar ${dest} (python3 saiu ${rc}): ${saida}" \
           "verifique o arquivo manualmente" 1 ;;
  esac
}

# 0 se as 2 entradas do sdd-open já estão em hooks.PreToolUse (para o plano marcar "=").
claude_settings_em_dia() { # $1=destino
  [ -f "${1}" ] || return 1
  python3 -I - "${1}" <<'PY' >/dev/null 2>&1
import json, sys
d = json.load(open(sys.argv[1], encoding="utf-8"))
pre = (d.get("hooks") or {}).get("PreToolUse") or []
cmds = " ".join(str(h.get("command", "")) for e in pre if isinstance(e, dict) for h in (e.get("hooks") or []) if isinstance(h, dict))
sys.exit(0 if "sdd-report-guard.py" in cmds and "sdd-avaliador-guard.py" in cmds else 1)
PY
}
