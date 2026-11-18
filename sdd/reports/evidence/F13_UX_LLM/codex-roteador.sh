#!/usr/bin/env bash
# Prova do roteador num agente real (DEFINE F13 AT-020, AT-021): 3 execuções de `codex exec` em cópias commitadas do HEAD,
# conferidas por efeito em confere_roteador.py, e 2 controles sem agente que precisam reprovar. O prompt não ensina o
# roteador: quem ensina é a skill. CODEX_HOME temporário só com o auth.json.
# Uso: codex-roteador.sh [feliz sem-skill sem-tipo]   (sem argumento, as 3)
set -u
cd "$(git rev-parse --show-toplevel)" || exit 64
E="$PWD/sdd/reports/evidence/F13_UX_LLM"; A="$E/amostra"; PREFIXO="${PREFIXO:-codex}"
BASE="$(mktemp -d)"; trap 'rm -rf "${BASE:?}"' EXIT; CH="$BASE/codex-home"; H="$BASE/home"; mkdir -p "$CH" "$H"
cp "$HOME/.codex/auth.json" "$CH/auth.json" || exit 64
MODELO="$(sed -n 's/^model = "\(.*\)"$/\1/p' "$HOME/.codex/config.toml" | head -1)"
copia() {
  mkdir -p "$1" && git archive HEAD | tar -x -C "$1" || exit 64
  cp sdd/config.example.yaml "$1/sdd/config.yaml"
  mkdir -p "$1/sdd/features"; cp "$A/DEFINE_NOTAS.md" "$A/DESIGN_NOTAS.md" "$1/sdd/features/"
}
# Calço: registra cada chamada real do scan (argumentos, saída e se o arquivo já existia) fora da cópia, em $SCANLOG.
calco() {
  mv "$1/sdd/bin/prompt-drift-scan.sh" "$1/sdd/bin/.scan-real.sh"
  cat > "$1/sdd/bin/prompt-drift-scan.sh" <<CALCO
#!/usr/bin/env bash
ultimo=""; for a in "\$@"; do ultimo="\$a"; done
if [ -e "\$ultimo" ]; then existia=1; else existia=0; fi
"\$BASH" "\$(dirname "\$0")/.scan-real.sh" "\$@"; rc=\$?
printf '%s\\trc=%s\\texistia=%s\\n' "\$*" "\$rc" "\$existia" >> "$2"
exit \$rc
CALCO
}
commita() { ( cd "$1" && git init -q 2>/dev/null; git add -A && git -c user.name=prova -c user.email=prova@example.com commit -q -m base ) || exit 64; }
PROMPT="Você é a fase Build deste projeto. Siga .agents/skills/sdd-build/SKILL.md. Os artefatos são sdd/features/DEFINE_NOTAS.md e sdd/features/DESIGN_NOTAS.md. O modo é default: não pergunte. Sem revisão de contexto fresco nesta execução. Execute só a tarefa 1 do File Manifest, conforme o passo 4 da skill, e pare depois dela, sem Verify Gate. Registre o que fez em sdd/reports/BUILD_REPORT_NOTAS.md, em poucas linhas. Sem commit. Se algo impedir a tarefa, faça a pergunta que a skill manda fazer, na sua mensagem final, e pare."
roda() { # nome pasta scanlog
  local n="$1" d="$2" log="$E/$PREFIXO-$1.log" out rc
  out="$(cd "$d" && HOME="$H" CODEX_HOME="$CH" codex exec --ignore-user-config --ephemeral -s workspace-write ${MODELO:+-m "$MODELO"} -C "$d" "$PROMPT" 2>&1 < /dev/null)"; rc=$?
  { printf '$ HOME=<temporário> CODEX_HOME=<temporário, só auth.json> codex exec --ignore-user-config --ephemeral -s workspace-write -C <cópia> "<prompt abaixo>"   # HEAD=%s\n' "$(git rev-parse --short HEAD)"
    printf 'codex: %s\nprompt: %s\n\n%s\n[exit=%s]\n' "$(codex --version 2>&1)" "$PROMPT" "$out" "$rc"; } > "$log"
  printf '\n$ python3 -B confere_roteador.py %s <cópia> %s\n' "$n" "$(basename "$log")" >> "$log"
  cp "$3" "$E/$PREFIXO-$1.scan.txt" 2>/dev/null || : > "$E/$PREFIXO-$1.scan.txt"
  printf '$ cat %s (o calço na cópia: cada chamada real do scan)\n' "$PREFIXO-$1.scan.txt" >> "$log"; cat "$E/$PREFIXO-$1.scan.txt" >> "$log"
  c="$(/usr/bin/python3 -B "$E/confere_roteador.py" "$n" "$d" "$log" "$3" 2>&1)"; rc2=$?
  printf '%s\n[exit=%s]\n' "$c" "$rc2" >> "$log"
  [ -f "$d/src/notas/LOOP_SPEC.md" ] && cp "$d/src/notas/LOOP_SPEC.md" "$E/$PREFIXO-$1.LOOP_SPEC.txt"
  [ -f "$d/sdd/reports/BUILD_REPORT_NOTAS.md" ] && cp "$d/sdd/reports/BUILD_REPORT_NOTAS.md" "$E/$PREFIXO-$1.relatorio.txt"
  echo "$n: codex rc=$rc confere rc=$rc2"; printf '%s\n' "$c"
}
for n in "${@:-feliz sem-skill sem-tipo}"; do for m in $n; do
  d="$BASE/$m"; copia "$d"
  case "$m" in
    sem-skill) rm -rf "${d:?}/.agents/skills/sdd-loop-builder" ;;
    sem-tipo)  /usr/bin/python3 -B - "$d/sdd/features/DESIGN_NOTAS.md" <<'P'
import re, sys
p = sys.argv[1]; t = open(p, encoding="utf-8").read()
t = t.replace("| # | Nome | Tipo | Arquivo", "| # | Nome | Arquivo").replace("|---|---|---|---|---|---|---|---|---|---|---|\n| 1 | notas_de_versao | loop |", "|---|---|---|---|---|---|---|---|---|---|\n| 1 | notas_de_versao |")
open(p, "w", encoding="utf-8").write(t)
P
    ;;
  esac
  : > "$BASE/scan-$m.log"; calco "$d" "$BASE/scan-$m.log"
  commita "$d"
  roda "$m" "$d" "$BASE/scan-$m.log"
done; done
rm -rf "${BASE:?}"
