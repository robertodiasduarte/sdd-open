#!/usr/bin/env bash
# gate.sh — o validador da KB tem de ACEITAR os exemplos e REJEITAR cada caso ruim, pelo motivo certo.
#
# Uso: bash .agents/skills/sdd-kb/scripts/gate.sh        (da raiz do projeto ou de qualquer pasta)
#
# Roda igual no pacote e no projeto do aluno: acha o validador e os exemplos pela própria pasta e monta
# cada caso num projeto temporário ($T/<caso>/sdd/kb/dom), copiado de assets/ com UMA mudança. Os casos
# nascem do exemplo atual, então nunca se afastam do que a skill entrega. Um validador que aceita caso
# ruim não discrimina; um que rejeita caso bom ensina a ignorá-lo — os dois deixam o gate vermelho.
#
# Exit: 0 verde · 2 vermelho. A cópia gerada pelo sync (.claude/skills, .cursor/skills) não serve de
# prova: lá cada arquivo ganha 2 linhas de cabeçalho e o exemplo normativo muda de SHA-256.
set -u
DIR="$(cd "$(dirname "$0")" && pwd)"
V="$DIR/validate_kb.py"; RM="$DIR/kb_normativo.py"; ASSETS="$DIR/../assets"
PY="${PYTHON:-python3}"
ACEITAS=0; REJEITADAS=0
T=""

falha() {  # $1 caso · $2 o que houve · $3 conserto — roda no shell principal, nunca dentro de $( )
  echo "🛑 $1: $2"
  [ -n "$T" ] && [ -f "$T/saida" ] && sed 's/^/    /' "$T/saida"
  echo "RESULTADO: VERMELHO"
  echo "→ $3"
  exit 2
}

MARCA='sdd-open'; MARCA="$MARCA:generated"   # montada em 2 partes: a fonte não pode conter a marca
if grep -qF "$MARCA" "$0"; then
  falha "cópia gerada pelo sync" "$0 tem o cabeçalho da cópia; os exemplos daqui não valem como prova" \
    "rode bash .agents/skills/sdd-kb/scripts/gate.sh"
fi
[ -f "$V" ] && [ -f "$RM" ] && [ -d "$ASSETS/example-kb" ] && [ -d "$ASSETS/example-kb-normativo" ] \
  || falha "pacote incompleto" "faltam scripts/ ou assets/ ao lado do gate.sh" "reinstale a skill sdd-kb"
T="$(mktemp -d)" || falha "pasta temporária" "mktemp -d falhou" "confira o espaço em disco e rode de novo"
trap 'rm -rf "${T:?}"' EXIT

projeto() {  # $1 caso · $2 exemplo de assets/ · $3 perfil — não imprime; o domínio fica em $T/$1/sdd/kb/dom
  rm -f "$T/saida"   # a saída do caso anterior não pode aparecer na falha deste
  mkdir -p "$T/$1/sdd/kb" && cp -R "$ASSETS/$2" "$T/$1/sdd/kb/dom" \
    || falha "$1" "a cópia do exemplo falhou" "confira assets/$2"
  printf 'version: "1.0"\ndomains:\n  dom:\n    name: caso %s\n    description: caso do gate\n    path: dom/\n    perfil: %s\n    updated: 2026-10-29\n' \
    "$1" "$3" > "$T/$1/sdd/kb/_index.yaml"
}

troca() {  # $1 caso · $2 arquivo (relativo ao domínio) · $3 âncora · $4 substituto (uma vez)
  "$PY" -B - "$T/$1/sdd/kb/dom/$2" "$3" "$4" <<'PY' || falha "$1" "âncora ausente: $3" "o exemplo mudou; atualize a âncora no gate.sh"
import sys
p, a, b = sys.argv[1:]
t = open(p, encoding="utf-8").read()
if a not in t:
    sys.exit(1)
open(p, "w", encoding="utf-8").write(t.replace(a, b, 1))
PY
}

anexa() {  # $1 caso · $2 arquivo (relativo ao domínio) · $3 texto (\n vira quebra de linha)
  printf '%b' "$3" >> "$T/$1/sdd/kb/dom/$2" || falha "$1" "não consegui escrever $2" "confira o espaço em disco"
}

estica() {  # $1 caso · $2 arquivo · $3 total de linhas que o arquivo deve ter
  "$PY" -B - "$T/$1/sdd/kb/dom/$2" "$3" <<'PY' || falha "$1" "não consegui esticar $2" "confira o exemplo"
import sys
p, alvo = sys.argv[1], int(sys.argv[2])
n = len(open(p, encoding="utf-8").read().splitlines())
with open(p, "a", encoding="utf-8") as f:
    f.write("".join("Linha de enchimento %d.\n" % i for i in range(alvo - n)))
PY
}

regera() {  # $1 caso — RULE_MAP de volta em dia depois de mexer numa regra
  "$PY" -B "$RM" rule-map "$T/$1/sdd/kb/dom" > /dev/null 2>&1 || falha "$1" "rule-map falhou" "confira rules/ do exemplo"
}

revisa() {  # $1 caso — o exemplo normativo vem PENDENTE DE REVISÃO; a cópia ganha um revisor
  troca "$1" index.md "PENDENTE DE REVISÃO (exemplo didático da skill — conferir na NT antes de qualquer uso)" \
    "Revisora do Exemplo, registro de teste"
}

aceita() {  # $1 caso · $2 trecho obrigatório na saída (ou vazio) · $3… argumentos do validador
  caso="$1"; trecho="$2"; shift 2; rm -f "$T/saida"
  "$PY" -B "$V" "$@" > "$T/saida" 2>&1 || falha "$caso" "caso bom REJEITADO" "o validador passou a reprovar conteúdo válido"
  if [ -n "$trecho" ] && ! grep -qF -- "$trecho" "$T/saida"; then
    falha "$caso" "aceito sem '$trecho' na saída" "confira o perfil do domínio no _index.yaml"
  fi
  ACEITAS=$((ACEITAS + 1))
}

rejeita() {  # $1 caso · $2 razão esperada · $3… argumentos do validador
  caso="$1"; razao="$2"; shift 2; rm -f "$T/saida"
  if "$PY" -B "$V" "$@" > "$T/saida" 2>&1; then
    falha "$caso" "caso ruim ACEITO" "o validador deixou de conferir isto"
  fi
  grep -qF -- "$razao" "$T/saida" \
    || falha "$caso" "rejeitado por outro motivo (esperado: $razao)" "confira a mutação e o validador"
  REJEITADAS=$((REJEITADAS + 1))
}

dom() { printf '%s' "$T/$1/sdd/kb/dom"; }

# ── o RULE_MAP do exemplo, antes dos casos: derivado, ele derrubaria o caso aceito com o diagnóstico errado
rm -f "$T/saida"
"$PY" -B "$RM" rule-map --check "$ASSETS/example-kb-normativo" > "$T/saida" 2>&1 \
  || falha "RULE_MAP do exemplo" "assets/example-kb-normativo/RULE_MAP.md não bate com rules/" \
     "rode python3 .agents/skills/sdd-kb/scripts/kb_normativo.py rule-map .agents/skills/sdd-kb/assets/example-kb-normativo"

# ── aceitas ───────────────────────────────────────────────────────────────────
projeto geral example-kb geral
aceita geral "" "$(dom geral)"

projeto normativo example-kb-normativo normativo
aceita normativo "rule(s)" "$(dom normativo)"

projeto bom-codigo example-kb geral   # chaves em código são exemplo (JSON, template), não lacuna
anexa bom-codigo quick-reference.md '\n## Exemplos em código (não são placeholders)\n\n| Campo | Formato |\n|---|---|\n| `alternativas` | `{A: "...", B: "..."}` |\n| linha do log | `{modelo, id, letra, correta?, custo, ms}` |\n\n```json\n{"gabarito": "C", "anulada": false, "gabarito_status": "definitivo"}\n```\n\n```text\nOlá {{ $json.nome }}, sua guia { vencimento: 20 } está pronta.\n```\n'
aceita bom-codigo "" "$(dom bom-codigo)"

projeto strict-teste-ok example-kb-normativo normativo
revisa strict-teste-ok
troca strict-teste-ok rules/UB12-10-CRT3.md "implementacao: null" "implementacao: src/engine.py:vbc"
troca strict-teste-ok rules/UB12-10-CRT3.md "teste: null" "teste: tests/test_engine.py::test_vbc"
mkdir -p "$T/strict-teste-ok/tests" && echo "# teste do caso" > "$T/strict-teste-ok/tests/test_engine.py"
regera strict-teste-ok
aceita strict-teste-ok "rule(s)" "$(dom strict-teste-ok)" --strict

# ── rejeitadas: perfil geral ──────────────────────────────────────────────────
projeto limite-conceito example-kb geral
estica limite-conceito concepts/regime-de-competencia.md 151
rejeita limite-conceito "limit is 150" "$(dom limite-conceito)"

projeto limite-receita example-kb geral
estica limite-receita patterns/conferir-antes-de-fechar.md 201
rejeita limite-receita "limit is 200" "$(dom limite-receita)"

projeto limite-consulta example-kb geral
estica limite-consulta quick-reference.md 101
rejeita limite-consulta "limit is 100" "$(dom limite-consulta)"

projeto nao-registrado example-kb geral
printf 'version: "1.0"\ndomains:\n  outro:\n    name: outro\n    description: outro\n    path: outro/\n    updated: 2026-10-29\n' \
  > "$T/nao-registrado/sdd/kb/_index.yaml"
rejeita nao-registrado "is not registered" "$(dom nao-registrado)"

projeto placeholder example-kb geral
troca placeholder concepts/regime-de-competencia.md "prática consolidada do escritório" "{uma fonte a confirmar}"
rejeita placeholder "unsubstituted placeholder" "$(dom placeholder)"

projeto placeholder-codigo example-kb geral
anexa placeholder-codigo patterns/conferir-antes-de-fechar.md '\n```text\n{{NOME_DO_RELATORIO}}\n```\n'
rejeita placeholder-codigo "unsubstituted placeholder" "$(dom placeholder-codigo)"

# ── rejeitadas: perfil normativo ──────────────────────────────────────────────
projeto sem-vigencia example-kb-normativo normativo
troca sem-vigencia rules/UB12-10-EXC1.md "  de: 2026-08-03
" ""
rejeita sem-vigencia "vigencia.de missing" "$(dom sem-vigencia)"

projeto fonte-fora example-kb-normativo normativo
troca fonte-fora rules/UB12-10-EXC1.md "  id: NT2025002-151" "  id: FONTE-QUE-NAO-EXISTE"
rejeita fonte-fora "not in fontes/CATALOGO.md" "$(dom fonte-fora)"

projeto sha-divergente example-kb-normativo normativo
anexa sha-divergente fontes/registro-captura-2026-09-27.txt 'linha acrescentada depois da captura\n'
rejeita sha-divergente "differs from the catalog" "$(dom sha-divergente)"

projeto pendente-strict example-kb-normativo normativo
rejeita pendente-strict "refuses an unreviewed normative KB" "$(dom pendente-strict)" --strict

projeto teste-vazio-strict example-kb-normativo normativo
revisa teste-vazio-strict
troca teste-vazio-strict rules/UB12-10-CRT3.md "implementacao: null" "implementacao: src/engine.py:vbc"
regera teste-vazio-strict
rejeita teste-vazio-strict "has no teste" "$(dom teste-vazio-strict)" --strict

projeto teste-inexistente-strict example-kb-normativo normativo
revisa teste-inexistente-strict
troca teste-inexistente-strict rules/UB12-10-CRT3.md "implementacao: null" "implementacao: src/engine.py:vbc"
troca teste-inexistente-strict rules/UB12-10-CRT3.md "teste: null" "teste: tests/test_engine.py::test_vbc"
regera teste-inexistente-strict
rejeita teste-inexistente-strict "not found from the project root" "$(dom teste-inexistente-strict)" --strict

echo "RESULTADO: VERDE — $ACEITAS aceitas, $REJEITADAS rejeitadas pelo motivo certo, RULE_MAP do exemplo em dia"
exit 0
