#!/usr/bin/env bash
# prompt-drift-scan.sh — este arquivo cheira a prompt de produção?
#
# A fase Build roda este script antes de gravar. Sem --conteudo, ele lê o arquivo em disco, que para um
# prompt novo ainda não existe e para um arquivo que vai ganhar o prompt ainda está limpo.
#
# Uso:
#   bash sdd/bin/prompt-drift-scan.sh --conteudo <caminho>   # avalia o texto da entrada padrão
#   bash sdd/bin/prompt-drift-scan.sh <caminho>...           # avalia arquivos em disco
#   bash sdd/bin/prompt-drift-scan.sh --self-test
#
# Sinais: pasta prompts/ · nome com "prompt" (exceto .md) · chamada direta ao SDK · system com texto
# fixo, em : ou =, ou role de sistema · o parâmetro do wrapper de LLM do projeto (prompts.wrapper_pattern de sdd/config.yaml) com texto
# fixo. O slot guarda a expressão do parâmetro (systemPrompt: ou callLLM\(); o script acrescenta
# "seguida de texto fixo". Parâmetro que recebe um nome importado não dispara: o prompt mora no arquivo
# importado, que o sinal de caminho pega.
# Exclusões: arquivo de teste, nas convenções comuns (a.test.x, a.spec.x, a_test.x, a_spec.x, test_a.x, ATest.x,
# ATests.x; pastas tests/, test/, spec/, __tests__/); .md fora de prompts/ não tem o conteúdo avaliado. A pasta
# prompts/ vence a exclusão por nome: prompts/test_a.txt conta, tests/prompts/a.txt não.
# Limites: a busca é por formas comuns, linha a linha, e não é exaustiva. Texto fixo na linha seguinte ao parâmetro,
# SDK fora da lista e texto montado por variável não disparam: para esses, use o slot. Sem git, a raiz é a pasta atual.
#
# Exit: 0 LIMPO · 2 DRIFT (ou self-test falhou) · 64 uso
# Compatível com bash 3.2, awk e grep POSIX.
export LC_ALL=C
unset CDPATH
set -u

ME="$(cd "$(dirname "$0")" && pwd -P)/$(basename "$0")"
LITERAL='[[:space:]]*[fFrRbBuU]{0,2}(`|'"'"'|")'
SDK='(messages\.create|chat\.completions|responses\.create|generateContent|generate_content)([^[:alnum:]_]|$)'
# A chave vale no início da linha, depois de { , ( [ ou de const/let/var: "file system:" e "package-ecosystem:" não.
INICIO='(^[[:space:]]*|[{,([][[:space:]]*|(const|let|var)[[:space:]]+)'
SYSTEM="$INICIO"'["'"'"']?system["'"'"']?\]?[[:space:]]*(:=|=>|:|=)'"$LITERAL"
ROLE="$INICIO"'["'"'"']?role["'"'"']?\]?[[:space:]]*(:=|=>|:|=)[[:space:]]*["'"'"']system["'"'"']'

TMP=""
limpar() { if [ -n "$TMP" ]; then rm -rf "${TMP:?}"; fi; }
trap limpar EXIT

erro_uso() {
  printf '🛑 %s\n' "$1" >&2
  printf 'RESULTADO: ERRO DE USO\n' >&2
  printf '→ %s\n' "$2" >&2
  exit 64
}

USO="bash sdd/bin/prompt-drift-scan.sh --conteudo <caminho> (texto na entrada padrão), ou <caminho>... para arquivos em disco"

ajuda() {
  cat <<'FIM'
prompt-drift-scan.sh — este arquivo cheira a prompt de produção?

  bash sdd/bin/prompt-drift-scan.sh --conteudo <caminho>   avalia o texto da entrada padrão, antes de gravar
  bash sdd/bin/prompt-drift-scan.sh <caminho>...           avalia arquivos em disco
  bash sdd/bin/prompt-drift-scan.sh --self-test            confere o próprio script

Se o projeto chama a IA por uma função própria, preencha prompts.wrapper_pattern em sdd/config.yaml
(por exemplo, systemPrompt:); sem isso, a varredura não vê essa função.

Saídas: 0 LIMPO · 2 DRIFT · 64 uso.
FIM
}

# ── raiz do projeto e slot ───────────────────────────────────────────────────
raiz_do_projeto() {
  local r
  # Um hook herda GIT_DIR: sem limpar, o script leria o config de outro repositório.
  r="$( (unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE; git rev-parse --show-toplevel) 2>/dev/null )"
  [ -n "$r" ] && [ -d "$r" ] || r="."
  (cd "$r" && pwd -P)
}

ler_slot() {  # imprime V<valor> ou M (malformado); nada se a chave não existe
  [ -f "$RAIZ/sdd/config.yaml" ] || return 0
  awk '
    NR == 1 { sub(/^\357\273\277/, "") }
    { sub(/\r$/, "") }
    /^["\047]?prompts["\047]?[[:space:]]*:[[:space:]]*\{.*wrapper_pattern/ { print "M"; exit }
    /^["\047]?prompts["\047]?[[:space:]]*:[[:space:]]*(#.*)?$/ { dentro = 1; next }
    /^[^[:space:]#]/ { dentro = 0 }
    dentro && /^[[:space:]]+["\047]?wrapper_pattern["\047]?[[:space:]]*:/ {
      v = $0
      sub(/^[[:space:]]+["\047]?wrapper_pattern["\047]?[[:space:]]*:[[:space:]]*/, "", v)
      q = substr(v, 1, 1); saida = ""; resto = ""
      if (q == "\"" || q == "\047") {
        fim = 0; i = 2
        while (i <= length(v)) {
          c = substr(v, i, 1)
          if (q == "\"" && c == "\\") {
            n = substr(v, i + 1, 1)
            if (n == "\\" || n == "\"") { saida = saida n; i += 2 } else { saida = saida c; i++ }
            continue
          }
          if (c == q) {
            if (q == "\047" && substr(v, i + 1, 1) == "\047") { saida = saida c; i += 2; continue }
            fim = i; break
          }
          saida = saida c; i++
        }
        if (!fim) { print "M"; exit }
        resto = substr(v, fim + 1)
        sub(/^[[:space:]]+/, "", resto)
        if (resto != "" && substr(resto, 1, 1) != "#") { print "M"; exit }
      } else {
        saida = v
        if (substr(saida, 1, 1) == "#") saida = ""
        sub(/[[:space:]]+#.*$/, "", saida)
        sub(/[[:space:]]+$/, "", saida)
        if (saida == "null" || saida == "Null" || saida == "NULL" || saida == "~") saida = ""
        c = substr(saida, 1, 1)
        if (c == "|" || c == ">" || c == "&" || c == "!") { print "M"; exit }
      }
      print "V" saida
      exit
    }' < "$RAIZ/sdd/config.yaml"
}

expressao_invalida() {  # 0 se o grep recusa a expressão
  grep -E -q -e "$1" </dev/null >/dev/null 2>&1
  [ "$?" -eq 2 ]
}

carregar_slot() {
  local lido cfg="$RAIZ/sdd/config.yaml" rc
  SLOT=""; WRAPPER=""
  # Fora do $( ): um erro_uso dentro da substituição só sairia da subshell, e o slot viraria vazio.
  # Ausente é vazio. Existir e não dar para ler (link quebrado, pasta, FIFO, permissão) nunca é vazio.
  if [ -L "$cfg" ] || [ -e "$cfg" ] || { [ -d "$RAIZ/sdd" ] && [ ! -x "$RAIZ/sdd" ]; }; then
    if [ ! -f "$cfg" ] || [ ! -r "$cfg" ]; then
      erro_uso "não consegui ler sdd/config.yaml" "confira o arquivo e a permissão: sem ele, o slot do wrapper não é lido"
    fi
  fi
  lido="$(ler_slot)"; rc=$?
  [ "$rc" -eq 0 ] || erro_uso "não consegui ler prompts.wrapper_pattern de sdd/config.yaml (exit $rc)" "confira o arquivo e rode de novo"
  case "$lido" in
    M*) erro_uso "prompts.wrapper_pattern malformado em sdd/config.yaml: use uma linha só, com a aspa fechada e nada depois dela" \
                 "corrija o slot; por exemplo: wrapper_pattern: \"systemPrompt:\"" ;;
    V*) SLOT="${lido#V}" ;;
  esac
  [ -n "$SLOT" ] || return 0
  WRAPPER="($SLOT)$LITERAL"
  if expressao_invalida "$SLOT" || expressao_invalida "$WRAPPER"; then
    erro_uso "prompts.wrapper_pattern não é uma expressão válida: $SLOT" "corrija o slot em sdd/config.yaml; por exemplo: wrapper_pattern: \"systemPrompt:\""
  fi
}

# ── normalização do caminho ──────────────────────────────────────────────────
# Caminho e raiz ficam físicos: num Mac, /var é link para /private/var, e um agente costuma passar
# caminho absoluto. Com --conteudo a pasta pode não existir: vale o ancestral existente mais profundo.
normalizar() {  # $1 → REL, DENTRO
  local p="$1" abs dir cauda="" fisico
  case "$p" in
    /*) abs="$p" ;;
    *)  abs="$(pwd -P)/$p" ;;
  esac
  dir="$abs"
  while [ ! -d "$dir" ]; do
    cauda="/${dir##*/}$cauda"
    dir="${dir%/*}"
    [ -n "$dir" ] || dir="/"
  done
  case "$cauda" in
    */../*|*/..) erro_uso "caminho com .. numa pasta que não existe: $p" "passe o caminho final, sem .." ;;
  esac
  fisico="$(cd "$dir" 2>/dev/null && pwd -P)" || erro_uso "não consegui entrar na pasta de $p" "confira a permissão da pasta"
  [ "$fisico" != "/" ] || fisico=""
  fisico="$fisico$cauda"
  case "$fisico" in
    "$RAIZ"/*) REL="${fisico#"$RAIZ"/}"; DENTRO=1 ;;
    *)         REL="$fisico"; DENTRO=0 ;;
  esac
}

pasta_de_teste() {  # usa REL e DENTRO
  # Fora da raiz, uma pasta acima do projeto chamada tests não decide nada.
  [ "$DENTRO" -eq 1 ] || return 1
  case "/$REL" in
    */tests/*|*/test/*|*/spec/*|*/__tests__/*) return 0 ;;
  esac
  return 1
}

nome_de_teste() {  # usa REL
  case "${REL##*/}" in
    *.test.*|*.spec.*|*_test.*|*_spec.*|test_*|*Test.*|*Tests.*) return 0 ;;
  esac
  return 1
}

# ── os sinais ────────────────────────────────────────────────────────────────
casa() {  # $1 expressão · $2 arquivo → 0 casou · 1 não casou; qualquer outra saída é erro, nunca "não achei"
  local rc
  grep -E -q -e "$1" -- "$2" 2>/dev/null
  rc=$?
  case "$rc" in
    0) return 0 ;;
    1) return 1 ;;
  esac
  erro_uso "a busca falhou (exit $rc) ao avaliar $CAMINHO" "confira a permissão do arquivo e a expressão de prompts.wrapper_pattern"
}

achou() { printf '%s :: %s\n' "$CAMINHO" "$1"; ACHOU=1; }

avaliar() {  # $1 caminho · $2 arquivo com o conteúdo
  local base minusculo
  CAMINHO="$1"
  normalizar "$1"
  pasta_de_teste && return 0

  case "$(printf '/%s' "$REL" | tr 'A-Z' 'a-z')" in
    */prompts/*) achou "pasta prompts/"; return 0 ;;
  esac
  nome_de_teste && return 0
  base="${REL##*/}"
  minusculo="$(printf '%s' "$base" | tr 'A-Z' 'a-z')"
  case "$minusculo" in
    *.md) return 0 ;;
    *prompt*) achou "nome com prompt"; return 0 ;;
  esac

  if casa "$SDK" "$2"; then achou "chamada direta ao SDK"; return 0; fi
  if casa "$SYSTEM" "$2"; then achou "system com texto fixo"; return 0; fi
  if casa "$ROLE" "$2"; then achou "role de sistema"; return 0; fi
  if [ -n "$WRAPPER" ] && casa "$WRAPPER" "$2"; then
    achou "parâmetro do wrapper com texto fixo (prompts.wrapper_pattern)"
  fi
  return 0
}

fechar() {
  if [ -z "$SLOT" ]; then
    printf '⚠️ prompts.wrapper_pattern vazio: procurei só os sinais genéricos; se o projeto chama a IA por uma função própria, esta varredura não a vê.\n'
    printf '   Preencha o slot em sdd/config.yaml (ex.: systemPrompt:), ou ignore se o projeto usa o SDK direto.\n'
  fi
  if [ "$ACHOU" -eq 1 ]; then
    printf 'RESULTADO: DRIFT\n'
    printf '→ se é prompt de produção, inventarie no DESIGN; se não é, registre o falso positivo no relatório\n'
    exit 2
  fi
  printf 'RESULTADO: LIMPO\n'
  printf '→ nenhum sinal de prompt de produção; siga\n'
  exit 0
}

# ── self-test: monta um projeto numa pasta temporária; não depende de nada instalado ──
auto_teste() {
  local falhas=0 total=0 proj

  TMP="$(mktemp -d)" || { printf 'RESULTADO: VERMELHO\n→ mktemp falhou\n' >&2; return 2; }
  proj="$TMP/proj"
  mkdir -p "$proj/sdd" "$proj/src/prompts" "$proj/tests" "$proj/fora/tests"
  printf 'prompts:\n  wrapper_pattern: "systemPrompt:|callLLM\\\\("  # comentário\n' > "$proj/sdd/config.yaml"

  # Sem git: a raiz é a pasta do caso, mesmo que a temporária esteja dentro de um repositório.
  roda() { (cd "$proj" && unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE && GIT_CEILING_DIRECTORIES="$TMP" "$BASH" "$ME" "$@"); }

  disco() {  # exit esperado · texto esperado · caminho · conteúdo
    local rc saida
    total=$((total + 1))
    mkdir -p "$(dirname "$proj/$3")"
    printf '%s\n' "$4" > "$proj/$3"
    saida="$(roda "$3" 2>&1 </dev/null)"; rc=$?
    if [ "$rc" -ne "$1" ] || ! printf '%s' "$saida" | grep -qF -- "$2"; then
      printf '🛑 caso em disco %s: exit %s (esperado %s, com "%s")\n' "$3" "$rc" "$1" "$2" >&2
      falhas=$((falhas + 1))
    fi
  }
  conteudo() {  # exit esperado · texto esperado · caminho · conteúdo
    local rc saida
    total=$((total + 1))
    saida="$(printf '%s\n' "$4" | roda --conteudo "$3" 2>&1)"; rc=$?
    if [ "$rc" -ne "$1" ] || ! printf '%s' "$saida" | grep -qF -- "$2"; then
      printf '🛑 caso --conteudo %s: exit %s (esperado %s, com "%s")\n' "$3" "$rc" "$1" "$2" >&2
      falhas=$((falhas + 1))
    fi
  }
  uso_errado() {  # descrição · argumentos: precisa sair 64, sem LIMPO
    local rc saida desc="$1"
    shift
    total=$((total + 1))
    saida="$(roda "$@" 2>&1 </dev/null)"; rc=$?
    if [ "$rc" -ne 64 ] || printf '%s' "$saida" | grep -qF 'RESULTADO: LIMPO'; then
      printf '🛑 caso de uso (%s): exit %s (esperado 64, sem LIMPO)\n' "$desc" "$rc" >&2
      falhas=$((falhas + 1))
    fi
  }
  slot() { printf 'prompts:\n  wrapper_pattern: %s\n' "$1" > "$proj/sdd/config.yaml"; }
  slot_padrao() { printf 'prompts:\n  wrapper_pattern: "systemPrompt:|callLLM\\\\("  # comentário\n' > "$proj/sdd/config.yaml"; }

  # Sinais, antes de gravar: o caminho não existe em disco.
  conteudo 2 'pasta prompts/'  prompts/novo.txt            'qualquer texto'
  conteudo 2 'pasta prompts/'  src/novo/prompts/v1/a.ts    'qualquer texto'
  conteudo 2 'nome com prompt' src/Agent_Prompt.py         'x = 1'
  conteudo 2 'chamada direta ao SDK' src/a.py              'client.messages.create(model=m)'
  conteudo 2 'chamada direta ao SDK' src/b.py              'client.chat.completions.create(model=m)'
  conteudo 2 'chamada direta ao SDK' src/b2.py             'client.responses.create(model=m)'
  conteudo 2 'chamada direta ao SDK' src/b3.js             'model.generateContent(x)'
  conteudo 2 'chamada direta ao SDK' src/b4.py             'model.generate_content(x)'
  conteudo 0 'RESULTADO: LIMPO'      src/b5.py             'messages.createdAt = agora'
  conteudo 2 'system com texto fixo' src/c.ts              'run({ system: "x", input: y })'
  conteudo 2 'system com texto fixo' src/d.json            '{ "system": "x" }'
  conteudo 2 'system com texto fixo' src/d2.py             'ask(system="x")'
  conteudo 2 'system com texto fixo' src/d3.py             'ask(system=f"x")'
  conteudo 2 'role de sistema' src/d4.ts                   '{ role: "system", content: x }'
  conteudo 2 'pasta prompts/' src/Prompts/d5.txt           'qualquer texto'
  conteudo 2 'pasta prompts/' prompts/test_d6.txt          'qualquer texto'
  conteudo 2 'parâmetro do wrapper' src/e.ts               'await ask({ systemPrompt: `x` })'
  conteudo 2 'parâmetro do wrapper' src/f.ts               'await callLLM("x")'
  conteudo 2 'parâmetro do wrapper' src/g.ts               "await callLLM('x')"
  # Exclusões.
  conteudo 0 'RESULTADO: LIMPO' src/h.ts                   'await ask({ systemPrompt: SYSTEM_X })'
  conteudo 0 'RESULTADO: LIMPO' src/i.ts                   'await callLLM(SYSTEM_X)'
  conteudo 0 'RESULTADO: LIMPO' src/a.test.ts              'await callLLM("x")'
  conteudo 0 'RESULTADO: LIMPO' src/a.spec.js              'await callLLM("x")'
  conteudo 0 'RESULTADO: LIMPO' src/a_test.go              'await callLLM("x")'
  conteudo 0 'RESULTADO: LIMPO' src/test_a.py              'await callLLM("x")'
  conteudo 0 'RESULTADO: LIMPO' tests/j.py                 'await callLLM("x")'
  conteudo 0 'RESULTADO: LIMPO' src/test/k.py              'await callLLM("x")'
  conteudo 0 'RESULTADO: LIMPO' src/__tests__/l.js         'await callLLM("x")'
  conteudo 0 'RESULTADO: LIMPO' spec/l2.rb                 'await callLLM("x")'
  conteudo 0 'RESULTADO: LIMPO' src/a_spec.rb              'await callLLM("x")'
  conteudo 0 'RESULTADO: LIMPO' src/FooTest.java           'await callLLM("x")'
  conteudo 0 'RESULTADO: LIMPO' src/FooTests.cs            'await callLLM("x")'
  conteudo 0 'RESULTADO: LIMPO' tests/prompts/l3.txt       'qualquer texto'
  conteudo 0 'RESULTADO: LIMPO' docs/m.md                  'use client.messages.create'
  conteudo 0 'RESULTADO: LIMPO' docs/prompt-guia.md        'qualquer texto'
  conteudo 0 'RESULTADO: LIMPO' .github/dependabot.yml     'package-ecosystem: "npm"'
  conteudo 0 'RESULTADO: LIMPO' src/n.yml                  'filesystem: "ext4"'
  conteudo 0 'RESULTADO: LIMPO' src/o.yml                  "operating_system: 'linux'"
  conteudo 0 'RESULTADO: LIMPO' src/o2.yml                 'file_role: "system"'
  conteudo 0 'RESULTADO: LIMPO' src/o3.yml                 'file system: "ext4"'
  conteudo 0 'RESULTADO: LIMPO' src/o4.yml                 'role: "system:admin"'
  # Em disco: 2 lados e nomes de todos os achados.
  disco 2 'src/p.ts :: chamada direta' src/p.ts            'client.messages.create(x)'
  disco 2 'pasta prompts/'             src/prompts/q.txt   'qualquer texto'
  disco 0 'RESULTADO: LIMPO'           src/r.py            'soma = a + b'

  # O slot: alternativa inteira, vazio com aviso, comentário depois da aspa, CRLF, aspas simples.
  slot '"foo|bar:"'
  conteudo 2 'parâmetro do wrapper' src/s.ts 'foo "x"'
  conteudo 0 'RESULTADO: LIMPO'     src/s.ts 'foo SYSTEM_X'
  slot '""  # vazio'
  conteudo 0 'wrapper_pattern vazio' src/t.ts 'soma = a + b'
  conteudo 2 'wrapper_pattern vazio' src/t.ts 'client.messages.create(x)'
  rm -f "$proj/sdd/config.yaml"
  conteudo 0 'wrapper_pattern vazio' src/t.ts 'soma = a + b'
  printf 'prompts:\r\n  wrapper_pattern: "systemPrompt:"\r\n' > "$proj/sdd/config.yaml"
  conteudo 2 'parâmetro do wrapper' src/u.ts 'ask({ systemPrompt: `x` })'
  slot 'null'
  conteudo 0 'wrapper_pattern vazio' src/t.ts 'soma = a + b'
  slot "'callLLM\\('"
  conteudo 2 'parâmetro do wrapper' src/v.ts 'callLLM("x")'
  slot 'systemPrompt:  # sem aspas'
  conteudo 2 'parâmetro do wrapper' src/w.ts 'ask({ systemPrompt: `x` })'

  # Saída 64: nunca conclui LIMPO.
  # src/r.py existe: a saída 64 só pode vir do slot.
  slot '"("'
  uso_errado 'expressão inválida (' src/r.py
  slot '"["'
  uso_errado 'expressão inválida [' src/r.py
  slot '"systemPrompt:'
  uso_errado 'aspa sem fechar' src/r.py
  slot '"x" y'
  uso_errado 'texto depois da aspa' src/r.py
  slot '>-'
  uso_errado 'bloco de YAML em vez de 1 linha' src/r.py
  printf 'prompts: { wrapper_pattern: "x" }\n' > "$proj/sdd/config.yaml"
  uso_errado 'mapa em linha com o slot' src/r.py
  printf 'prompts: {}\n' > "$proj/sdd/config.yaml"
  disco 0 'wrapper_pattern vazio' src/r.py 'soma = a + b'
  rm -f "$proj/sdd/config.yaml"
  ln -s /nao/existe/config.yaml "$proj/sdd/config.yaml"
  uso_errado 'sdd/config.yaml é um link quebrado' src/r.py
  rm -f "$proj/sdd/config.yaml"; mkdir "$proj/sdd/config.yaml"
  uso_errado 'sdd/config.yaml é uma pasta' src/r.py
  rmdir "$proj/sdd/config.yaml"
  slot_padrao
  uso_errado 'sem argumento'
  uso_errado 'caminho inexistente' src/nao-existe.ts
  uso_errado 'pasta' src
  uso_errado 'opção desconhecida' --nada
  uso_errado '--conteudo sem caminho' --conteudo
  uso_errado '--conteudo com 2 caminhos' --conteudo a b
  uso_errado '--conteudo sem nada na entrada' --conteudo src/x.ts
  total=$((total + 1))
  saida_pasta="$(printf 'x\n' | roda --conteudo src 2>&1)"; rc_pasta=$?
  if [ "$rc_pasta" -ne 64 ]; then
    printf '🛑 caso de uso (--conteudo com pasta): exit %s (esperado 64)\n' "$rc_pasta" >&2; falhas=$((falhas + 1))
  fi
  # Busca que falha (exit 2 num grep de conteúdo): com o stub, nunca vira "não achei".
  mkdir -p "$TMP/stub"
  printf '#!/bin/sh\ncase " $* " in *" -- "*) exit 2 ;; esac\nexec %s "$@"\n' "$(command -v grep)" > "$TMP/stub/grep"
  chmod +x "$TMP/stub/grep"
  total=$((total + 1))
  saida_pasta="$(printf 'x = 1\n' | PATH="$TMP/stub:$PATH" roda --conteudo src/y.py 2>&1)"; rc_pasta=$?
  if [ "$rc_pasta" -ne 64 ]; then
    printf '🛑 caso de uso (grep com saída 2): exit %s (esperado 64)\n' "$rc_pasta" >&2; falhas=$((falhas + 1))
  fi
  uso_errado '.. em pasta inexistente' --conteudo nao/existe/../a.ts
  if [ "$(id -u)" != "0" ]; then
    printf 'x\n' > "$proj/src/ilegivel.ts"; chmod 000 "$proj/src/ilegivel.ts"
    uso_errado 'arquivo ilegível' src/ilegivel.ts
    chmod 600 "$proj/src/ilegivel.ts"
    chmod 000 "$proj/sdd/config.yaml"
    uso_errado 'sdd/config.yaml ilegível' src/ilegivel.ts
    chmod 600 "$proj/sdd/config.yaml"
  fi

  if [ "$falhas" -ne 0 ]; then
    printf 'RESULTADO: VERMELHO\n' >&2
    printf '→ %s de %s caso(s) falharam: corrija o script; não afrouxe o sinal para passar\n' "$falhas" "$total" >&2
    return 2
  fi
  printf '✅ %s casos conferidos\n' "$total"
  printf 'RESULTADO: VERDE\n'
  printf '→ o prompt-drift-scan.sh está pronto para uso\n'
  return 0
}

# ── despacho ─────────────────────────────────────────────────────────────────
[ "$#" -gt 0 ] || erro_uso "falta dizer o que avaliar" "$USO"

case "$1" in
  -h|--help)
    ajuda; exit 0
    ;;
  --self-test)
    [ "$#" -eq 1 ] || erro_uso "--self-test não aceita outros valores" "bash sdd/bin/prompt-drift-scan.sh --self-test"
    auto_teste; exit $?
    ;;
  --conteudo)
    [ "$#" -eq 2 ] && [ -n "$2" ] || erro_uso "--conteudo precisa de exatamente 1 caminho" "$USO"
    case "$2" in
      */|.|..|*/.|*/..) erro_uso "--conteudo precisa do caminho de um arquivo: $2" "$USO" ;;
    esac
    [ ! -d "$2" ] || erro_uso "--conteudo precisa do caminho de um arquivo: $2 é uma pasta" "$USO"
    RAIZ="$(raiz_do_projeto)"
    carregar_slot
    [ ! -t 0 ] || erro_uso "--conteudo espera o texto na entrada padrão, e ela é o terminal" "passe o texto que vai gravar pela entrada padrão"
    TMP="$(mktemp -d)" || erro_uso "não consegui criar a pasta temporária" "confira o espaço em disco e tente de novo"
    cat > "$TMP/conteudo"
    [ -s "$TMP/conteudo" ] || erro_uso "nada chegou pela entrada padrão" "passe o texto pela entrada padrão; arquivo vazio não precisa de varredura"
    ACHOU=0
    avaliar "$2" "$TMP/conteudo"
    fechar
    ;;
  -*)
    erro_uso "opção desconhecida: $1" "$USO"
    ;;
esac

RAIZ="$(raiz_do_projeto)"
carregar_slot
for p in "$@"; do
  [ -e "$p" ] || erro_uso "caminho inexistente: $p" "confira o caminho do manifest, ou use --conteudo para arquivo novo"
  [ -f "$p" ] || erro_uso "não é um arquivo: $p" "passe os arquivos, um por um"
  [ -r "$p" ] || erro_uso "não consegui ler: $p" "confira a permissão do arquivo"
done
ACHOU=0
for p in "$@"; do
  avaliar "$p" "$p"
done
fechar
