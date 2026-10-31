#!/usr/bin/env bash
# sdd-open.sh — instala e mantém o SDD Open num projeto.
#
#   bash <pacote>/bin/sdd-open.sh init  [--vendors a,b,c] [--yes] [--dry-run]
#   bash <pacote>/bin/sdd-open.sh sync  [--vendors a,b,c] [--yes] [--dry-run] [--check]
#   bash <pacote>/bin/sdd-open.sh doctor
#
# Fonte única: .agents/skills/sdd-*/ (o que você edita). Adaptadores por vendor são CÓPIAS
# marcadas "sdd-open:generated" — sync as reescreve. sdd/ é território do usuário: sync nunca
# escreve lá.
#
# Vendors: claude (cobre também Grok Build e GLM via Claude Code) · codex · gemini · cursor · kimi
#
# ⚠️ bash 3.2 · sem declare -A · ${VAR} com chaves antes de não-ASCII · exit medido sem pipe.

set -uo pipefail

PKG="$(cd "$(dirname "${0}")/.." && pwd -P)"
. "${PKG}/bin/lib/say.sh"
. "${PKG}/bin/lib/vendors.sh"
. "${PKG}/bin/lib/merge.sh"
. "${PKG}/bin/lib/plan.sh"

MARCA='sdd-open:generated'
VERBO="${1:-}"; [ $# -gt 0 ] && shift
VENDORS_ARG=""; ASSUME_YES=0; DRY_RUN=0; CHECK=0; VERBOSE=0

ajuda() {
  cat <<'TXT'
sdd-open — Spec-Driven Development agnóstico de agente

  init    prepara o projeto: sdd/, .agents/skills/, AGENTS.md e os adaptadores do seu agente
  sync    regenera os adaptadores a partir de .agents/skills/ (sdd/ nunca é tocado)
  doctor  mostra o que está instalado e o que cada agente vai enxergar

  --vendors claude,codex,gemini,cursor,kimi   quais agentes preparar (init) ou regenerar (sync)
  --dry-run                                   mostra o plano e não escreve nada
  --yes                                       aplica sem perguntar
  --check                                     (sync) só verifica se os adaptadores estão em dia
  --verbose                                   lista também o que já está correto

Exemplos:
  bash sdd-open/bin/sdd-open.sh init --vendors codex
  bash sdd-open/bin/sdd-open.sh sync --check
TXT
}

while [ $# -gt 0 ]; do
  case "${1}" in
    --vendors) VENDORS_ARG="${2:-}"; shift 2 ;;
    --vendors=*) VENDORS_ARG="${1#--vendors=}"; shift ;;
    --yes|-y) ASSUME_YES=1; shift ;;
    --dry-run) DRY_RUN=1; shift ;;
    --check) CHECK=1; shift ;;
    --verbose|-v) VERBOSE=1; shift ;;
    -h|--help) ajuda; exit 0 ;;
    *) die "opção desconhecida: ${1}" "rode sem argumentos para ver a ajuda" 64 ;;
  esac
done

case "${VERBO}" in
  ""|help|-h|--help) ajuda; exit 0 ;;
  init|sync|doctor) : ;;
  *) die "verbo desconhecido: ${VERBO}" "use init, sync ou doctor (rode sem argumentos para a ajuda)" 64 ;;
esac

# ── pré-condições (antes de qualquer escrita) ──────────────────────────────────
BASH_MAJOR="${SDD_OPEN_BASH_VERSINFO:-${BASH_VERSINFO[0]}}"   # SDD_OPEN_BASH_VERSINFO = costura de teste
BASH_MINOR="${BASH_VERSINFO[1]:-0}"
if [ "${BASH_MAJOR}" -lt 3 ] || { [ "${BASH_MAJOR}" -eq 3 ] && [ "${BASH_MINOR}" -lt 2 ]; }; then
  die "bash 3.2 ou superior é necessário (encontrado ${BASH_MAJOR}.${BASH_MINOR})" \
      "no Windows use Git Bash ou WSL; no Linux instale o pacote bash" 64
fi

ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" \
  || die "este comando precisa de um repositório git" \
         "rode 'git init' aqui, ou entre na pasta do seu projeto" 64

[ -w "${ROOT}" ] || die "sem permissão de escrita em ${ROOT}" \
                        "verifique o dono e as permissões da pasta (ls -ld '${ROOT}')" 1

# ── vendors ────────────────────────────────────────────────────────────────────
config_vendors() { # lê vendors: de sdd/config.yaml, se houver
  [ -f "${ROOT}/sdd/config.yaml" ] || return 0
  sed -n 's/^vendors:[[:space:]]*//p' "${ROOT}/sdd/config.yaml" | head -1 | tr -d '[]" '
}

VENDORS=""
if [ -n "${VENDORS_ARG}" ]; then
  lista="${VENDORS_ARG}"
elif [ "${VERBO}" != "init" ]; then
  lista="$(config_vendors)"
else
  lista=""
fi
if [ -n "${lista}" ]; then
  invalidos=""
  for v in $(vendores_da_lista "${lista}"); do
    case "${v}" in
      __INVALIDO__*) invalidos="${invalidos} ${v#__INVALIDO__}" ;;
      *) VENDORS="${VENDORS} ${v}" ;;
    esac
  done
  [ -z "${invalidos}" ] || die "vendor desconhecido:${invalidos}" \
    "use um ou mais de: ${VENDORS_SUPORTADOS} (separados por vírgula)" 64
fi
if [ "${VERBO}" = "init" ] && [ -z "${VENDORS}" ]; then
  die "init precisa saber para quais agentes preparar o projeto" \
      "passe --vendors com um ou mais de: ${VENDORS_SUPORTADOS}" 64
fi
# sync com o conjunto de vendors VAZIO degradava em silêncio (kimi R1, review pré-release): a lista
# do AGENTS.md saía vazia, nenhum adaptador era conferido e o --check seguinte dizia EM DIA.
if [ "${VERBO}" = "sync" ] && [ -z "${VENDORS}" ]; then
  die "sync não sabe para quais agentes sincronizar: sem --vendors e sem a linha 'vendors:' em sdd/config.yaml" \
      "passe --vendors com um ou mais de: ${VENDORS_SUPORTADOS} — ou restaure a linha 'vendors: <lista>' em sdd/config.yaml (init a grava)" 64
fi

# init repetido (sdd/ já existe): os vendors passam a ser a UNIÃO dos já configurados com os
# pedidos agora — o bloco do AGENTS.md e o config saem coerentes (avaliador, ciclo 1).
if [ "${VERBO}" = "init" ] && [ -f "${ROOT}/sdd/config.yaml" ]; then
  atuais="$(config_vendors)"
  # tr, não paste: sem o paste no PATH a lista esvaziava em silêncio e o init terminava INSTALADO sem vendor.
  VENDORS=" $(printf '%s\n%s\n' "$(printf '%s' "${atuais}" | tr ',' '\n')" "$(printf '%s' "${VENDORS}" | tr ' ' '\n')" | grep -v '^$' | awk '!seen[$0]++' | tr '\n' ' ')"
  VENDORS="${VENDORS% }"
fi

vendor_pedido() { case " ${VENDORS} " in *" ${1} "*) return 0 ;; *) return 1 ;; esac; }

# ── fonte das skills ───────────────────────────────────────────────────────────
# init copia do pacote para o projeto; sync parte do que está no projeto (é o que o usuário edita).
FONTE_SKILLS="${ROOT}/.agents/skills"
[ "${VERBO}" = "init" ] && FONTE_PKG_SKILLS="${PKG}/.agents/skills"

skills_da_fonte() { # imprime nomes sdd-* presentes na fonte indicada
  local base="${1}" d
  for d in "${base}"/sdd-*/; do
    [ -d "${d}" ] || continue
    basename "${d}"
  done
}

# ── cabeçalho GENERATED ────────────────────────────────────────────────────────
# Cada cópia carrega 2 linhas com o token sdd-open:generated, na sintaxe de comentário da
# linguagem do arquivo — um .py com cabeçalho HTML deixava de compilar. O formato vem de UMA
# tabela (perfil_arquivo): o escritor renderiza a partir dela e o verificador do --check lê o
# verificador dela. "Em dia" = igual byte a byte ao que o escritor renderiza agora.
# .json e binários (imagem, fonte, pdf, zip, ou qualquer arquivo com byte NUL) não têm comentário:
# a cópia sai sem cabeçalho, idêntica à fonte.

extensao() { # $1=caminho → extensão minúscula do basename, ou vazio
  local b; b="$(basename "${1}")"
  case "${b}" in *.*) printf '%s\n' "${b##*.}" | tr '[:upper:]' '[:lower:]' ;; *) printf '\n' ;; esac
}

tem_bom() { [ "$(head -c 3 "${1}" | od -An -tx1 | tr -d ' \n')" = "efbbbf" ]; }   # BOM UTF-8 no byte 0
sem_bom() { if tem_bom "${1}"; then tail -c +4 "${1}"; else cat "${1}"; fi; }

# Sob pipefail, o cmp -s só fecha o pipe cedo quando já achou diferença (= havia NUL).
eh_binario() { ! LC_ALL=C tr -d '\000' < "${1}" | cmp -s - "${1}"; }

eh_coding_py() { # $1=linha → 0 se é declaração de encoding do PEP 263 (# … coding: x / coding=x)
  # Regex do próprio PEP 263: sem nome de encoding (`# coding:` sozinho) não é declaração.
  local re='^[[:space:]]*#.*coding[:=][[:space:]]*[-_.a-zA-Z0-9]+'
  [[ "${1}" =~ ${re} ]]
}

# ÚNICA tabela do formato das cópias. Extensão de código decide o estilo; md e desconhecidas
# olham a linha 1 (frontmatter `---` ou shebang). As linhas lidas vêm sem BOM e sem \r (Windows).
# <manter> = quantas linhas do topo a linguagem exige que fiquem no topo: shebang, frontmatter e,
# no .py, a declaração de encoding (PEP 263: só vale na linha 1 ou 2). O cabeçalho entra depois delas.
perfil_arquivo() { # $1=fonte → "<estilo> <manter> <verificador> <bom>"
  # Bytes, não caracteres: num terminal UTF-8, uma fonte Latin-1 fazia o tr recusar a linha e o regex
  # do bash não casar — a cópia mudava conforme o locale de quem roda. C só dentro desta função.
  local LC_ALL=C; export LC_ALL
  local l1 l2 t1 n resto ext estilo="" verif="-" manter=0 bom=0
  tem_bom "${1}" && bom=1
  l1="$(sem_bom "${1}" | head -n 1 | tr -d '\r')"
  ext="$(extensao "${1}")"
  case "${ext}" in
    py)             estilo=hash;  verif=python ;;
    rb)             estilo=hash;  verif=ruby ;;
    sh|bash)        estilo=hash;  verif=bash ;;
    yaml|yml|toml|ps1|psm1) estilo=hash ;;
    js|mjs|cjs)     estilo=slash; verif=node ;;
    ts)             estilo=slash ;;
    css)            estilo=block ;;
    sql)            estilo=dash ;;
    json)           estilo=none;  verif=json ;;
    xml|svg)        estilo=html;  verif=xml ;;
    png|jpg|jpeg|gif|webp|ico|pdf|zip|gz|tgz|woff|woff2|ttf|otf) estilo=none ;;
  esac
  # Qualquer arquivo com byte NUL é binário para o cabeçalho, mesmo com extensão conhecida (XML em
  # UTF-16, por exemplo): cópia byte a byte. O verificador da extensão continua valendo.
  if [ "${estilo}" != "none" ] && eh_binario "${1}"; then estilo=none; fi
  case "${l1}" in
    '#!'*) manter=1; [ -n "${estilo}" ] || estilo=hash
           # bash -n só julga bash/sh: um .sh com #!/bin/zsh não pode ser acusado de não compilar.
           if [ "${verif}" = "bash" ]; then
             case "${l1}" in *bash*|*/sh|*/sh\ *|*' sh'|*' sh '*) : ;; *) verif="-" ;; esac
           fi ;;
  esac
  # PEP 263: a declaração de encoding vale na linha 1, ou na 2 quando a linha 1 é só comentário
  # (shebang incluso) ou vazia. Onde valer, ela e o que vem antes dela ficam no topo. O magic comment
  # do Ruby (`# encoding:`/`# coding:`) tem a mesma regra de posição e o mesmo regex casa os dois.
  if [ "${ext}" = "py" ] || [ "${ext}" = "rb" ]; then
    l2="$(sem_bom "${1}" | sed -n '2p' | tr -d '\r')"
    t1="${l1#"${l1%%[![:space:]]*}"}"
    if eh_coding_py "${l1}"; then manter=1
    else case "${t1}" in ''|'#'*) eh_coding_py "${l2}" && manter=2 ;; esac; fi
  fi
  # CSS: o @charset só é reconhecido nos primeiros bytes do arquivo. Se a linha dele continua com
  # conteúdo (um comentário aberto, por exemplo), não há ponto seguro: cópia byte a byte.
  if [ "${ext}" = "css" ]; then
    case "${l1}" in
      '@charset'*';'*)
        resto="${l1#*;}"; resto="${resto#"${resto%%[![:space:]]*}"}"
        if [ -n "${resto}" ]; then estilo=none; else manter=1; fi ;;
      '@charset'*) estilo=none ;;
    esac
  fi
  if [ -z "${estilo}" ]; then
    if [ "${l1}" = "---" ]; then estilo=hash; manter=1; else estilo=html; fi
  fi
  # XML (svg, plist, xsd…): a declaração <?xml ?> só vale no início — o comentário entra na linha
  # seguinte ao "?>" que a fecha (que pode estar adiante). Se a linha do "?>" continua com conteúdo
  # (<root><![CDATA[ …), não há ponto seguro para o comentário: cópia byte a byte, sem cabeçalho.
  if [ "${estilo}" = "html" ]; then
    case "${l1}" in
      '<?xml'*)
        n="$(sem_bom "${1}" | awk '/\?>/ {print NR; exit}')"
        if [ -n "${n}" ]; then
          resto="$(sem_bom "${1}" | sed -n "${n}p" | tr -d '\r')"; resto="${resto#*\?>}"
          resto="${resto#"${resto%%[![:space:]]*}"}"
          if [ -n "${resto}" ]; then estilo=none; else manter="${n}"; fi
        fi ;;
    esac
  fi
  printf '%s %s %s %s\n' "${estilo}" "${manter}" "${verif}" "${bom}"
}

linha_marca() { # $1=estilo $2=texto (o caminho vem do disco: o que fecharia o comentário é desarmado)
  # Cabeçalho 100% ASCII, inclusive o caminho: byte fora de ASCII vira '?'. Um .py com
  # `# coding: ascii` numa pasta com acento deixava de compilar pela cópia (V5-R1@codex).
  local t; t="$(printf '%s' "${2}" | LC_ALL=C tr -c ' -~' '?')"
  # Contrabarra também vira '?': com `# coding: unicode_escape`, um \n do caminho viraria quebra de linha
  # e o resto do comentário, código (R2@codex, volta 7).
  t="${t//\\/?}"
  case "${1}" in
    hash)  t="${t//coding:/coding :}"; t="${t//coding=/coding =}"   # caminho não vira declaração PEP 263
           printf '# %s\n' "${t}" ;;
    slash) printf '// %s\n' "${t}" ;;
    block) while :; do case "${t}" in *'*/'*) t="${t//\*\//* /}" ;; *) break ;; esac; done
           printf '/* %s */\n' "${t}" ;;
    dash)  printf -- '-- %s\n' "${t}" ;;
    html)  while :; do case "${t}" in *--*) t="${t//--/- -}" ;; *) break ;; esac; done   # XML proíbe -- em comentário
           printf '<!-- %s -->\n' "${t}" ;;
  esac
}

renderizar_gerado() { # $1=fonte $2=skill $3=arquivo-relativo [$4=prefixo da fonte] → conteúdo exato da cópia no stdout
  local LC_ALL=C; export LC_ALL   # idem perfil_arquivo: o caminho e as linhas mantidas são bytes
  local estilo manter verif bom
  # Prefixo default: a skill do projeto. Os adaptadores de hook vêm de bin/adapters/<vendor>/ do PACOTE —
  # caminho que não existe no projeto, por isso o cabeçalho diz de onde ele vem.
  local prefixo="${4:-.agents/skills}" sufixo=""
  [ -n "${4:-}" ] && sufixo=" (pacote sdd-open)"
  read -r estilo manter verif bom <<PERFIL
$(perfil_arquivo "${1}")
PERFIL
  if [ "${estilo}" = "none" ]; then cat "${1}"; return; fi
  [ "${bom}" = "1" ] && printf '\357\273\277'
  # printf '%s\n' garante o \n depois das linhas mantidas mesmo num arquivo sem \n final.
  [ "${manter}" -gt 0 ] && printf '%s\n' "$(sem_bom "${1}" | head -n "${manter}")"
  # O caminho vem do disco e entra num comentário de outra linguagem: só [A-Za-z0-9._/-] passa, o resto vira
  # '?'. Um codec da fonte (utf-7, unicode_escape) ou um fechador de comentário no nome não vira código (V8-R1).
  local caminho; caminho="$(printf '%s' "${prefixo}/${2}/${3}" | LC_ALL=C tr -c 'A-Za-z0-9._/-' '?')"
  linha_marca "${estilo}" "${MARCA} - fonte: ${caminho}${sufixo}"
  linha_marca "${estilo}" "${MARCA} - sync reescreve este arquivo; edite a fonte e rode sync"
  sem_bom "${1}" | tail -n +"$((manter + 1))"
}

mesmo_bit_x() { local a=0 b=0; [ -x "${1}" ] && a=1; [ -x "${2}" ] && b=1; [ "${a}" = "${b}" ]; }

escrever_gerado() { # $1=fonte $2=destino $3=skill $4=arquivo-relativo [$5=prefixo da fonte]
  local fonte="${1}" dest="${2}"
  mkdir -p "$(dirname "${dest}")" || return 1
  renderizar_gerado "${fonte}" "${3}" "${4}" "${5:-}" > "${dest}" || return 1
  # Shebang preservado só serve para ./script se o bit de execução vier junto.
  if [ -x "${fonte}" ]; then chmod +x "${dest}" || return 1; else chmod a-x "${dest}" || return 1; fi
}

# Sob pipefail, o cmp -s só fecha o pipe cedo (SIGPIPE no render) quando JÁ achou diferença, então o
# resultado continua certo. Mas o printf do render escreveria "write error: Broken pipe" no terminal, 1 linha
# por cópia divergente (avaliador ciclo 6: 40–80 linhas no 1º sync pós-upgrade). O stderr desse render é
# descartado: ele só compara. A escrita de verdade (escrever_gerado) não passa por pipe e mostra os erros reais.
gerado_em_dia() { # $1=fonte $2=destino $3=skill $4=arquivo-relativo [$5=prefixo] → 0 se idêntico ao render atual
  [ -f "${2}" ] || return 1
  renderizar_gerado "${1}" "${3}" "${4}" "${5:-}" 2>/dev/null | cmp -s - "${2}" || return 1
  mesmo_bit_x "${1}" "${2}"
}

# Verificador de sintaxe do --check, sem efeito colateral (compile() não grava __pycache__). O python
# roda com -I (isolado): sem o diretório atual no sys.path, um json.py ou xml/ do projeto não é importado
# nem executado pelo --check (R2@codex, volta 6). Pelo mesmo motivo node e ruby rodam sem NODE_OPTIONS/RUBYOPT:
# um --require herdado (o Yarn PnP usa) faria o node --check executar módulo do projeto (R1@codex, volta 7).
compila() { # $1=arquivo $2=verificador do perfil → 0 compila · 1 não compila · 2 sem verificador
  case "${2}" in
    python) command -v python3 >/dev/null 2>&1 || return 2
            python3 -I -c 'import sys; compile(open(sys.argv[1],"rb").read(), sys.argv[1], "exec")' "${1}" >/dev/null 2>&1 || return 1 ;;
    bash)   bash -n "${1}" >/dev/null 2>&1 || return 1 ;;
    node)   command -v node >/dev/null 2>&1 || return 2
            env -u NODE_OPTIONS node --check "${1}" >/dev/null 2>&1 || return 1 ;;
    ruby)   command -v ruby >/dev/null 2>&1 || return 2
            env -u RUBYOPT ruby -c "${1}" >/dev/null 2>&1 || return 1 ;;
    json)   if command -v jq >/dev/null 2>&1; then jq empty "${1}" >/dev/null 2>&1 || return 1
            elif command -v python3 >/dev/null 2>&1; then python3 -I -m json.tool "${1}" >/dev/null 2>&1 || return 1
            else return 2; fi ;;
    xml)    command -v python3 >/dev/null 2>&1 || return 2
            python3 -I -c 'import sys, xml.etree.ElementTree as E; E.parse(sys.argv[1])' "${1}" >/dev/null 2>&1 || return 1 ;;
    *)      return 2 ;;
  esac
  return 0
}

nome_verificador() { # $1=verificador do perfil → o comando que a pessoa roda à mão
  case "${1}" in python) printf 'python3' ;; bash) printf 'bash -n' ;; node) printf 'node --check' ;; json) printf 'jq (ou python3 -m json.tool)' ;; xml) printf 'python3 (xml)' ;; ruby) printf 'ruby -c' ;; esac
}

# ── plano ──────────────────────────────────────────────────────────────────────
plano_reset
declare_alvos_skills() { # $1=diretório destino (.claude/skills | .cursor/skills) $2=modo plan|apply|check
  local destdir="${1}" modo="${2}" skill f rel dest alvo _estilo _manter verif _bom rc
  for skill in $(skills_da_fonte "${FONTE_SKILLS}"); do
    while IFS= read -r f; do
      [ -n "${f}" ] || continue
      rel="${f#${FONTE_SKILLS}/${skill}/}"
      dest="${ROOT}/${destdir}/${skill}/${rel}"
      alvo="${destdir}/${skill}/${rel}"
      case "${modo}" in
        plan)  if gerado_em_dia "${f}" "${dest}" "${skill}" "${rel}"; then plano_estado "${alvo}" emdia
               elif [ -e "${dest}" ]; then plano_estado "${alvo}" atualizar
               else plano_estado "${alvo}" novo; fi ;;
        apply) gerado_em_dia "${f}" "${dest}" "${skill}" "${rel}" || escrever_gerado "${f}" "${dest}" "${skill}" "${rel}" || return 1 ;;
        check)
          if [ ! -e "${dest}" ]; then
            printf '%s (ausente: rode sync)\n' "${alvo}"; DIVERGENTES=$((DIVERGENTES + 1))
          elif ! gerado_em_dia "${f}" "${dest}" "${skill}" "${rel}"; then
            printf '%s (desatualizado: rode sync)\n' "${alvo}"; DIVERGENTES=$((DIVERGENTES + 1))
          else
            # Em dia byte a byte. O verificador ainda pode achar a cópia quebrada: ou a fonte já
            # nasce quebrada (o autor conserta) ou o render está errado (bug do sdd-open).
            read -r _estilo _manter verif _bom <<PERFIL
$(perfil_arquivo "${f}")
PERFIL
            compila "${dest}" "${verif}"; rc=$?
            if [ "${rc}" = "1" ]; then
              if compila "${f}" "${verif}"; then
                printf '%s (a cópia gerada não compila com %s, mas a fonte compila: bug do sdd-open — abra uma issue)\n' "${alvo}" "$(nome_verificador "${verif}")"
              else
                printf '%s (a fonte .agents/skills/%s/%s não compila com %s: corrija a fonte; sync não resolve)\n' "${alvo}" "${skill}" "${rel}" "$(nome_verificador "${verif}")"
              fi
              DIVERGENTES=$((DIVERGENTES + 1))
            elif [ "${rc}" = "2" ] && [ "${verif}" != "-" ]; then
              detalhe "sem $(nome_verificador "${verif}" | cut -d' ' -f1): ${alvo} conferido só byte a byte"
            fi
          fi ;;
      esac
    done <<EOF
$(find "${FONTE_SKILLS}/${skill}" -type f 2>/dev/null | sort)
EOF
  done
}

# Adaptadores de hook do vendor (bin/adapters/<vendor>/* do PACOTE, no init e no sync): cópias em <destdir>
# com o mesmo cabeçalho sdd-open:generated. O nome da ferramenta do vendor mora só nesses arquivos e no gerado.
declare_alvos_adaptadores() { # $1=vendor $2=diretório destino (.claude/hooks) $3=modo plan|apply|check
  local vendor="${1}" destdir="${2}" modo="${3}" f rel dest alvo _estilo _manter verif _bom rc
  for f in "${PKG}/bin/adapters/${vendor}"/*; do
    [ -f "${f}" ] || continue
    rel="$(basename "${f}")"; dest="${ROOT}/${destdir}/${rel}"; alvo="${destdir}/${rel}"
    case "${modo}" in
      plan)  if gerado_em_dia "${f}" "${dest}" "${vendor}" "${rel}" bin/adapters; then plano_estado "${alvo}" emdia
             elif [ -e "${dest}" ]; then plano_estado "${alvo}" atualizar
             else plano_estado "${alvo}" novo; fi ;;
      apply) gerado_em_dia "${f}" "${dest}" "${vendor}" "${rel}" bin/adapters \
               || escrever_gerado "${f}" "${dest}" "${vendor}" "${rel}" bin/adapters || return 1 ;;
      check)
        if [ ! -e "${dest}" ]; then
          printf '%s (ausente: rode sync)\n' "${alvo}"; DIVERGENTES=$((DIVERGENTES + 1))
        elif ! gerado_em_dia "${f}" "${dest}" "${vendor}" "${rel}" bin/adapters; then
          printf '%s (desatualizado: rode sync)\n' "${alvo}"; DIVERGENTES=$((DIVERGENTES + 1))
        else
          read -r _estilo _manter verif _bom <<PERFIL
$(perfil_arquivo "${f}")
PERFIL
          compila "${dest}" "${verif}"; rc=$?
          if [ "${rc}" = "1" ]; then
            printf '%s (a cópia gerada não compila com %s; a fonte é bin/adapters/%s/%s do pacote — abra uma issue)\n' \
              "${alvo}" "$(nome_verificador "${verif}")" "${vendor}" "${rel}"
            DIVERGENTES=$((DIVERGENTES + 1))
          fi
        fi ;;
    esac
  done
}

CORPO_AGENTS="$(mktemp)"; trap 'rm -f "${CORPO_AGENTS}"' EXIT
gerar_corpo_agents() {
  sed -e "s|{{VENDORS}}|$(printf '%s' "${VENDORS}" | sed 's/^ *//; s/ /, /g')|g" "${PKG}/AGENTS.md.tmpl" > "${CORPO_AGENTS}"
}

agents_md_checar() { # valida marcadores sem escrever (mesmas regras do merge: linha inteira, 1 par, ordem)
  local dest="${ROOT}/AGENTS.md" n_abre n_fecha l_abre l_fecha
  [ -f "${dest}" ] || return 0
  n_abre=$(grep -cE "^${ABRE}"$'\r'"?\$" "${dest}" || true); n_fecha=$(grep -cE "^${FECHA}"$'\r'"?\$" "${dest}" || true)
  if [ "${n_abre}" -ne "${n_fecha}" ] || [ "${n_abre}" -gt 1 ]; then
    die "AGENTS.md: marcadores ${ABRE} desbalanceados ou duplicados (${n_abre} abertura, ${n_fecha} fechamento, contando só linhas inteiras)" \
        "deixe exatamente um par de marcadores, cada um sozinho na linha, e rode de novo — nada foi alterado" 65
  fi
  if [ "${n_abre}" -eq 1 ]; then
    l_abre=$(grep -nE "^${ABRE}"$'\r'"?\$" "${dest}" | cut -d: -f1); l_fecha=$(grep -nE "^${FECHA}"$'\r'"?\$" "${dest}" | cut -d: -f1)
    [ "${l_fecha}" -gt "${l_abre}" ] || die "AGENTS.md: marcador de fechamento (linha ${l_fecha}) não vem DEPOIS da abertura (linha ${l_abre})" \
        "corrija a ordem dos marcadores e rode de novo — nada foi alterado" 65
  fi
}

# Destinos que serão escritos precisam ser graváveis ANTES da primeira escrita (codex P2):
# a raiz gravável não prova que AGENTS.md ou .gemini/settings.json são.
# Escopado ao PLANO (kimi R2): só os destinos que este verbo, para estes vendors, escreveria —
# `.cursor/skills` somente-leitura não barra `init --vendors codex`; `sync` nunca toca sdd/config.yaml.
destinos_checar() {
  local d arquivos="AGENTS.md" dirs=""
  if [ "${VERBO}" = "init" ]; then arquivos="${arquivos} sdd/config.yaml"; dirs="${dirs} sdd .agents/skills"; fi
  vendor_pedido claude && { arquivos="${arquivos} CLAUDE.md .claude/settings.json"; dirs="${dirs} .claude/skills .claude/hooks"; }
  vendor_pedido cursor && dirs="${dirs} .cursor/skills"
  vendor_pedido gemini && { arquivos="${arquivos} GEMINI.md .gemini/settings.json"; dirs="${dirs} .gemini"; }
  for d in ${arquivos}; do
    [ -e "${ROOT}/${d}" ] && [ ! -w "${ROOT}/${d}" ] && die "sem permissão de escrita em ${d}" \
      "verifique o dono e as permissões (ls -l '${ROOT}/${d}') — nada foi alterado" 1
  done
  for d in ${dirs}; do
    [ -d "${ROOT}/${d}" ] && [ ! -w "${ROOT}/${d}" ] && die "sem permissão de escrita em ${d}/" \
      "verifique o dono e as permissões (ls -ld '${ROOT}/${d}') — nada foi alterado" 1
  done
  return 0
}

# Adaptadores ÓRFÃOS: skill que sumiu da fonte mas continua copiada no vendor. sync nunca
# apaga (território do usuário); sinaliza em --check e avisa no sync (kimi R2).
orfaos_listar() { # $1=destdir → imprime paths órfãos
  local destdir="${1}" d nome
  for d in "${ROOT}/${destdir}"/sdd-*/; do
    [ -d "${d}" ] || continue
    nome="$(basename "${d}")"
    [ -d "${FONTE_SKILLS}/${nome}" ] || printf '%s/%s (órfão: a fonte .agents/skills/ não tem mais esta skill)\n' "${destdir}" "${nome}"
  done
}

GEMINI_MD_CORPO='As instruções deste projeto estão em AGENTS.md (carregado via context.fileName em .gemini/settings.json).'
gemini_md_em_dia() { [ -f "${ROOT}/GEMINI.md" ] && [ "$(cat "${ROOT}/GEMINI.md")" = "${GEMINI_MD_CORPO}" ]; }

gemini_settings_checar() {
  local dest="${ROOT}/.gemini/settings.json" saida
  # python3 é pré-condição do adaptador gemini: checar ANTES de qualquer escrita (o DESIGN
  # promete "nada foi alterado"; o avaliador viu init escrever sdd/ e depois morrer — ciclo 2).
  command -v python3 >/dev/null 2>&1 || die "o adaptador gemini precisa de python3 para editar .gemini/settings.json com segurança" \
    "instale python3 ou rode sem o vendor gemini — nada foi alterado" 64
  [ -f "${dest}" ] || return 0
  saida=$(python3 -I -c 'import json,sys
try:
    json.load(open(sys.argv[1], encoding="utf-8"))
except json.JSONDecodeError as e:
    print(f"{e.lineno}: {e.msg}"); sys.exit(66)' "${dest}" 2>&1) || \
    die ".gemini/settings.json não é JSON válido (linha ${saida})" \
        "corrija ou renomeie o arquivo e rode de novo — nada foi alterado" 66
}

# .claude/settings.json: python3 é pré-condição do adaptador claude (guards e merge), checada ANTES de
# qualquer escrita, como no Gemini; JSON inválido também para tudo antes de escrever.
claude_settings_checar() {
  local dest="${ROOT}/.claude/settings.json" saida
  command -v python3 >/dev/null 2>&1 || die "o adaptador claude precisa de python3 para editar .claude/settings.json com segurança e para os guards de .claude/hooks/" \
    "instale python3 ou rode sem o vendor claude — nada foi alterado" 64
  [ -f "${dest}" ] || return 0
  # Sintaxe E forma (topo objeto, hooks objeto, PreToolUse lista): o merge recusaria depois de sdd/, skills e
  # core.hooksPath já gravados, e "nada foi alterado" seria falso (avaliador do build, ciclo 1).
  saida=$(python3 -I -c 'import json,sys
try:
    d = json.load(open(sys.argv[1], encoding="utf-8"))
except json.JSONDecodeError as e:
    print(f"{e.lineno}: {e.msg}"); sys.exit(66)
if not isinstance(d, dict):
    print("1: o topo do arquivo não é um objeto"); sys.exit(66)
h = d.get("hooks", {})
if not isinstance(h, dict):
    print("1: a chave hooks não é um objeto"); sys.exit(66)
if not isinstance(h.get("PreToolUse", []), list):
    print("1: hooks.PreToolUse não é uma lista"); sys.exit(66)' "${dest}" 2>&1) || \
    die ".claude/settings.json não é JSON válido (linha ${saida})" \
        "corrija ou renomeie o arquivo e rode de novo — nada foi alterado" 66
}

# ── hooks de git (sdd/hooks) ────────────────────────────────────────────────────
MARCA_HIGIENE='# sdd-higiene-dado: alarme de commit (pre-commit)'
HOOKS_ESTADO=""   # calculado em planejar (init)

# O arquivo de hook legado é SEMPRE <git-common-dir>/hooks/pre-commit: `git rev-parse --git-path
# hooks/pre-commit` segue o core.hooksPath e, com o dispatcher ligado, apontaria para ele mesmo.
hook_legado() {
  local common; common="$(git rev-parse --git-common-dir 2>/dev/null)"
  case "${common}" in /*) ;; *) common="${ROOT}/${common}" ;; esac
  printf '%s/hooks/pre-commit' "${common}"
}

# 0 quando $1 é sdd/hooks relativo, ou um caminho absoluto que resolve (links simbólicos inclusos: /tmp
# no macOS) para <raiz>/sdd/hooks. O alarme.sh da higiene usa o mesmo critério.
hooks_path_e_nosso() {
  local hp="${1%/}"; hp="${hp#./}"   # o git aceita sdd/hooks/ e ./sdd/hooks (edição manual): são o mesmo lugar
  [ "${hp}" = "sdd/hooks" ] && return 0
  case "${hp}" in /*) [ -d "${hp}" ] && [ "$(cd "${hp}" 2>/dev/null && pwd -P)" = "$(cd "${ROOT}/sdd/hooks" 2>/dev/null && pwd -P)" ] ;; *) return 1 ;; esac
}

hooks_estado() { # → LIVRE | LIGADO | HIGIENE | OUTRO <descrição>
  local hp legado
  hp="$(git config --get core.hooksPath 2>/dev/null || true)"
  legado="$(hook_legado)"
  if [ -n "${hp}" ] && hooks_path_e_nosso "${hp}"; then printf 'LIGADO\n'
  elif [ -n "${hp}" ]; then printf 'OUTRO core.hooksPath = %s (husky, lefthook ou outro gerenciador)\n' "${hp}"
  elif [ -f "${legado}" ] && grep -qF "${MARCA_HIGIENE}" "${legado}"; then printf 'HIGIENE\n'
  elif [ -f "${legado}" ]; then printf 'OUTRO um pre-commit em %s\n' "${legado}"
  else printf 'LIVRE\n'; fi
}

hooks_executaveis() { [ -x "${ROOT}/sdd/hooks/pre-commit" ] && [ -x "${ROOT}/sdd/hooks/pre-push" ]; }

# 0 quando HEAD está em project.default_branch e origin/<branch> existe: o pre-commit (H6) recusaria
# o commit da própria instalação, e a linha final do init diz como contornar.
na_branch_padrao_com_remoto() {
  local b db
  db="$(sed -n '/^project:/,/^[^[:space:]#]/ s/^[[:space:]]*default_branch:[[:space:]]*//p' "${ROOT}/sdd/config.yaml" 2>/dev/null \
    | head -1 | sed 's/[[:space:]]*#.*$//' | tr -d '"'"'"' ')"
  [ -n "${db}" ] || db=main
  b="$(git symbolic-ref --quiet --short HEAD 2>/dev/null)" || return 1
  [ "${b}" = "${db}" ] && git rev-parse --verify --quiet "refs/remotes/origin/${db}" >/dev/null 2>&1
}

LINHA_ACRESCENTAR='bash sdd/hooks/pre-commit || exit 1'

# Arquivos do pacote que sustentam as skills (bin, hooks, templates, playbook, config) e faltam em sdd/
# do projeto — relativos a sdd/. Vazio = árvore completa. Fixtures ficam fora (exemplos, apagáveis).
sdd_faltantes() {
  local rel
  ( cd "${PKG}/sdd" && find templates bin hooks playbook.md -type f | sort ) | while IFS= read -r rel; do
    [ -e "${ROOT}/sdd/${rel}" ] || printf '%s\n' "${rel}"
  done
  [ -f "${ROOT}/sdd/config.yaml" ] || printf 'config.yaml\n'
}

# metadata.version do frontmatter de uma SKILL.md (vazio se não houver).
versao_skill() {
  sed -n "2,/^---\$/ s/^ *version: *[\"']*\([0-9][0-9.]*\)[\"']*.*\$/\1/p" "$1" | head -1
}

# versao_menor A B: sai 0 se A < B (X.Y.Z, campo a campo); A vazia conta como 0.0.0.
versao_menor() {
  awk -v a="${1:-0.0.0}" -v b="$2" 'BEGIN { split(a, x, "."); split(b, y, ".")
    for (i = 1; i <= 3; i++) { if (x[i] + 0 < y[i] + 0) exit 0; if (x[i] + 0 > y[i] + 0) exit 1 }
    exit 1 }'
}

planejar() {
  destinos_checar
  # bloco do AGENTS.md
  gerar_corpo_agents; agents_md_checar
  if [ ! -f "${ROOT}/AGENTS.md" ]; then plano_estado "AGENTS.md" novo
  elif agents_md_em_dia "${ROOT}/AGENTS.md" "${CORPO_AGENTS}"; then plano_estado "AGENTS.md (bloco sdd-open)" emdia
  else plano_estado "AGENTS.md (só o bloco entre os marcadores)" atualizar; fi

  if [ "${VERBO}" = "init" ]; then
    if [ ! -d "${ROOT}/sdd" ]; then plano_estado "sdd/ (templates, fixtures, bin, hooks, playbook, config)" novo
    else
      n_falt=$(sdd_faltantes | grep -c . || true)
      if [ "${n_falt}" = "0" ]; then plano_estado "sdd/ (já existe — não será tocado)" emdia
      else plano_estado "sdd/ (já existe — completar ${n_falt} arquivo(s) do pacote ausente(s); o que existe não será tocado)" atualizar; fi
    fi
    # Hooks de git: a linha do plano diz o EFEITO (é o único aviso que o aluno recebe de que o projeto
    # passa a recusar commits). Alarme alheio nunca é desligado: só a linha para acrescentar a ele.
    HOOKS_ESTADO="$(hooks_estado)"
    case "${HOOKS_ESTADO}" in
      LIGADO) plano_estado "core.hooksPath = sdd/hooks" emdia ;;
      LIVRE|HIGIENE) plano_estado "core.hooksPath = sdd/hooks — 5 regras + relatório + alarme passam a conferir cada commit (teto do arquivo de contexto, credencial, playbook, byte NUL, branch padrão); git commit --no-verify pula uma vez" novo ;;
      OUTRO*)
        warn "hooks do open não ligados: já existe ${HOOKS_ESTADO#OUTRO }. Nada foi alterado nele."
        warn "para ter as 5 regras + relatório, acrescente a ele a linha: ${LINHA_ACRESCENTAR}" ;;
    esac
    for skill in $(skills_da_fonte "${FONTE_PKG_SKILLS}"); do
      if [ -d "${FONTE_SKILLS}/${skill}" ]; then plano_estado ".agents/skills/${skill} (já existe — fonte do usuário, não será tocada)" emdia
      else plano_estado ".agents/skills/${skill}" novo; fi
    done
  fi

  vendor_pedido claude && {
    claude_settings_checar
    if [ -f "${ROOT}/CLAUDE.md" ] && grep -qF '@AGENTS.md' "${ROOT}/CLAUDE.md"; then plano_estado "CLAUDE.md" emdia
    elif [ -f "${ROOT}/CLAUDE.md" ]; then plano_estado "CLAUDE.md (acrescentar @AGENTS.md)" atualizar
    else plano_estado "CLAUDE.md" novo; fi
    declare_alvos_adaptadores claude ".claude/hooks" plan
    if claude_settings_em_dia "${ROOT}/.claude/settings.json"; then plano_estado ".claude/settings.json" emdia
    elif [ -f "${ROOT}/.claude/settings.json" ]; then plano_estado ".claude/settings.json (hooks += 2 guards do sdd-open)" atualizar
    else plano_estado ".claude/settings.json" novo; fi
  }
  vendor_pedido gemini && {
    gemini_settings_checar
    if gemini_md_em_dia; then plano_estado "GEMINI.md" emdia
    elif [ -f "${ROOT}/GEMINI.md" ]; then plano_estado "GEMINI.md (conteúdo divergente)" atualizar
    else plano_estado "GEMINI.md" novo; fi
    if gemini_settings_em_dia "${ROOT}/.gemini/settings.json"; then plano_estado ".gemini/settings.json" emdia
    elif [ -f "${ROOT}/.gemini/settings.json" ]; then plano_estado ".gemini/settings.json (context.fileName += AGENTS.md)" atualizar
    else plano_estado ".gemini/settings.json" novo; fi
  }
  # cópias de skills só fazem sentido quando a fonte já existe (no init, será criada antes)
  local fonte_para_plano="${FONTE_SKILLS}"
  [ "${VERBO}" = "init" ] && [ ! -d "${FONTE_SKILLS}" ] && fonte_para_plano="${FONTE_PKG_SKILLS}"
  FONTE_SKILLS_SAVE="${FONTE_SKILLS}"; FONTE_SKILLS="${fonte_para_plano}"
  vendor_pedido claude && declare_alvos_skills ".claude/skills" plan
  vendor_pedido cursor && declare_alvos_skills ".cursor/skills" plan
  FONTE_SKILLS="${FONTE_SKILLS_SAVE}"
  for v in codex kimi; do vendor_pedido "${v}" && detalhe "= ${v}: nada a gerar ($(vendor_nativo_motivo "${v}"))"; done
}

aplicar() {
  # Toda escrita checa o exit: uma cópia que falha no meio NÃO pode terminar em INSTALADO
  # (kimi R1 / codex P2, review pós-build). O pré-check de destinos roda no plano.
  local falha_escrita="falha ao escrever no projeto — instalação incompleta"
  if [ "${VERBO}" = "init" ]; then
    # sdd/ é território do usuário: init NUNCA sobrescreve o que existe, mas COMPLETA o que falta
    # (grok A1, review pré-release): um init interrompido deixava sdd/ oco e o retry recomendado pelo
    # próprio die pulava todas as cópias por ver o diretório — e terminava INSTALADO.
    primeira_vez=1; [ -d "${ROOT}/sdd" ] && primeira_vez=0
    mkdir -p "${ROOT}/sdd/features" "${ROOT}/sdd/reports" "${ROOT}/sdd/reviews" "${ROOT}/sdd/releases" \
             "${ROOT}/sdd/handoffs" "${ROOT}/sdd/contexto" "${ROOT}/sdd/templates" "${ROOT}/sdd/fixtures" "${ROOT}/sdd/bin" \
             "${ROOT}/sdd/hooks" \
      || die "${falha_escrita} (mkdir sdd/)" "verifique permissões e espaço em disco; rode init de novo" 1
    # fixtures são exemplos: copiadas só na 1ª instalação (o usuário pode apagá-las de propósito).
    if [ "${primeira_vez}" = "1" ]; then
      cp -R "${PKG}/sdd/fixtures/." "${ROOT}/sdd/fixtures/" || die "${falha_escrita} (sdd/fixtures)" "verifique permissões e espaço em disco; rode init de novo" 1
    fi
    faltantes="$(sdd_faltantes)"
    if [ -n "${faltantes}" ]; then
      printf '%s\n' "${faltantes}" | while IFS= read -r rel; do
        [ -n "${rel}" ] || continue
        if [ "${rel}" = "config.yaml" ]; then
          # vendors: é um placeholder no example; init o PREENCHE (a única diferença entre os 2 arquivos).
          cp "${PKG}/sdd/config.example.yaml" "${ROOT}/sdd/config.yaml" || exit 1
        else
          mkdir -p "$(dirname "${ROOT}/sdd/${rel}")" && cp "${PKG}/sdd/${rel}" "${ROOT}/sdd/${rel}" || exit 1
        fi
      done || die "${falha_escrita} (sdd/)" "verifique permissões e espaço em disco; rode init de novo — ele completa só o que falta" 1
    fi
    # init repetido (sdd/ já existia) com vendors novos: MESCLAR na linha vendors: do config, senão
    # sync/--check seguem olhando só os vendors do primeiro init (achado do avaliador, ciclo 1).
    if [ -f "${ROOT}/sdd/config.yaml" ]; then
      uniao="$(printf '%s' "${VENDORS}" | sed 's/^ *//; s/ /,/g')"
      if grep -q '^vendors:' "${ROOT}/sdd/config.yaml"; then
        sed -e "s|^vendors:.*|vendors: ${uniao}|" "${ROOT}/sdd/config.yaml" > "${ROOT}/sdd/config.yaml.sddtmp" && mv "${ROOT}/sdd/config.yaml.sddtmp" "${ROOT}/sdd/config.yaml" \
          || die "${falha_escrita} (sdd/config.yaml)" "verifique permissões; rode init de novo" 1
      else
        printf 'vendors: %s\n' "${uniao}" >> "${ROOT}/sdd/config.yaml" || die "${falha_escrita} (sdd/config.yaml)" "verifique permissões; rode init de novo" 1
      fi
    fi
    mkdir -p "${FONTE_SKILLS}" || die "${falha_escrita} (.agents/skills)" "verifique permissões; rode init de novo" 1
    for skill in $(skills_da_fonte "${FONTE_PKG_SKILLS}"); do
      [ -d "${FONTE_SKILLS}/${skill}" ] || cp -R "${FONTE_PKG_SKILLS}/${skill}" "${FONTE_SKILLS}/${skill}" \
        || die "${falha_escrita} (.agents/skills/${skill})" "verifique permissões; rode init de novo" 1
    done
    # Hooks: bit de execução (o git ignora em silêncio um hook sem ele; um checkout no Windows pode
    # perdê-lo) e core.hooksPath, só quando não há alarme alheio. O alarme da higiene já instalado em
    # .git/hooks migra para o dispatcher (sdd.higieneDado=on); o arquivo antigo fica, inerte.
    for h in pre-commit pre-push; do
      [ -f "${ROOT}/sdd/hooks/${h}" ] && { chmod +x "${ROOT}/sdd/hooks/${h}" || die "${falha_escrita} (chmod sdd/hooks/${h})" "verifique permissões; rode init de novo" 1; }
    done
    case "${HOOKS_ESTADO}" in
      LIVRE|HIGIENE)
        git config core.hooksPath sdd/hooks || die "${falha_escrita} (core.hooksPath)" "verifique a permissão de .git/config; rode init de novo" 1
        if [ "${HOOKS_ESTADO}" = "HIGIENE" ]; then
          git config sdd.higieneDado on || die "${falha_escrita} (sdd.higieneDado)" "verifique a permissão de .git/config; rode init de novo" 1
          warn "alarme da sdd-higiene-dado migrado: continua ligado, agora pelos hooks do projeto (sdd/hooks). Para desligar: bash .agents/skills/sdd-higiene-dado/scripts/alarme.sh desinstalar"
        fi ;;
    esac
  fi

  merge_agents_md "${ROOT}/AGENTS.md" "${CORPO_AGENTS}" || die "${falha_escrita} (AGENTS.md)" "verifique permissões; rode de novo" 1

  vendor_pedido claude && {
    if [ ! -f "${ROOT}/CLAUDE.md" ]; then printf '@AGENTS.md\n' > "${ROOT}/CLAUDE.md" || die "${falha_escrita} (CLAUDE.md)" "verifique permissões; rode de novo" 1
    elif ! grep -qF '@AGENTS.md' "${ROOT}/CLAUDE.md"; then printf '%s\n' '' '@AGENTS.md' >> "${ROOT}/CLAUDE.md" || die "${falha_escrita} (CLAUDE.md)" "verifique permissões; rode de novo" 1; fi
    declare_alvos_skills ".claude/skills" apply || die "${falha_escrita} (.claude/skills)" "verifique permissões; rode de novo" 1
    for o in $(orfaos_listar ".claude/skills" | cut -d' ' -f1); do warn "adaptador órfão mantido (sync nunca apaga): ${o} — remova à mão se não quiser mais a skill"; done
    declare_alvos_adaptadores claude ".claude/hooks" apply || die "${falha_escrita} (.claude/hooks)" "verifique permissões; rode de novo" 1
    merge_claude_settings "${ROOT}/.claude/settings.json"
  }
  vendor_pedido cursor && {
    declare_alvos_skills ".cursor/skills" apply || die "${falha_escrita} (.cursor/skills)" "verifique permissões; rode de novo" 1
    for o in $(orfaos_listar ".cursor/skills" | cut -d' ' -f1); do warn "adaptador órfão mantido (sync nunca apaga): ${o} — remova à mão se não quiser mais a skill"; done
  }
  vendor_pedido gemini && {
    gemini_md_em_dia || printf '%s\n' "${GEMINI_MD_CORPO}" > "${ROOT}/GEMINI.md" || die "${falha_escrita} (GEMINI.md)" "verifique permissões; rode de novo" 1
    merge_gemini_settings "${ROOT}/.gemini/settings.json"
  }
  return 0
}

doctor() {
  local v bin st n_falt
  say "sdd-open doctor — projeto: ${ROOT}"
  printf '  bash %s.%s · git %s · python3 %s\n' "${BASH_VERSINFO[0]}" "${BASH_VERSINFO[1]}" \
    "$(git --version 2>/dev/null | sed 's/git version //')" \
    "$(command -v python3 >/dev/null 2>&1 && python3 -I -c 'import sys;print(".".join(map(str,sys.version_info[:2])))' || echo 'ausente')"
  if [ -d "${ROOT}/sdd" ]; then
    n_falt=$(sdd_faltantes | grep -c . || true)
    if [ "${n_falt}" = "0" ]; then ok "sdd/ presente ($(ls "${ROOT}/sdd/features" 2>/dev/null | wc -l | tr -d ' ') feature(s) em sdd/features/)"
    else warn "sdd/ incompleto — ${n_falt} arquivo(s) do pacote ausente(s), ex.: sdd/$(sdd_faltantes | head -1) — rode init de novo (completa sem tocar o que existe)"; fi
  else warn "sdd/ ausente — rode init"; fi
  [ -f "${ROOT}/AGENTS.md" ] && grep -qF "${ABRE}" "${ROOT}/AGENTS.md" && ok "AGENTS.md com o bloco sdd-open" \
                             || warn "AGENTS.md sem o bloco sdd-open — rode init ou sync"
  [ -d "${FONTE_SKILLS}" ] && ok ".agents/skills/ com $(skills_da_fonte "${FONTE_SKILLS}" | wc -l | tr -d ' ') skill(s) sdd-*" \
                            || warn ".agents/skills/ ausente"
  # Hooks de git: ligados (hooksPath + bit de execução) ou um ⚠️ por causa, cada um com o comando.
  local he h
  he="$(hooks_estado)"
  case "${he}" in
    LIGADO)
      if hooks_executaveis; then
        ok "hooks ligados (sdd/hooks: pre-commit com 5 regras + relatório + alarme da higiene $(git config --get sdd.higieneDado 2>/dev/null || echo off), pre-push)"
      else
        for h in pre-commit pre-push; do
          if [ ! -f "${ROOT}/sdd/hooks/${h}" ]; then warn "hooks: sdd/hooks/${h} ausente — rode init (completa sdd/hooks)"
          elif [ ! -x "${ROOT}/sdd/hooks/${h}" ]; then warn "hooks: sdd/hooks/${h} sem permissão de execução (o git o ignora em silêncio) — rode: chmod +x sdd/hooks/${h}"; fi
        done
      fi ;;
    OUTRO*) warn "hooks do open não ligados: já existe ${he#OUTRO }. Para ter as 5 regras + relatório, acrescente a ele a linha: ${LINHA_ACRESCENTAR}" ;;
    *) warn "hooks do open não ligados (core.hooksPath vazio) — rode init" ;;
  esac
  local lista_doc="${VENDORS}"; [ -z "${lista_doc}" ] && lista_doc="${VENDORS_SUPORTADOS}"
  for v in ${lista_doc}; do
    bin="$(vendor_binario "${v}")"
    if command -v "${bin}" >/dev/null 2>&1; then st="CLI encontrado"; else st="CLI não encontrado no PATH"; fi
    case "${v}" in
      codex|kimi) ok "${v}: nativo — nada a gerar ($(vendor_nativo_motivo "${v}")) · ${st}" ;;
      claude) if [ ! -d "${ROOT}/.claude/skills" ]; then warn "claude: adaptador não gerado — rode sync --vendors claude"
              elif [ -f "${ROOT}/.claude/hooks/sdd-report-guard.py" ] && [ -f "${ROOT}/.claude/hooks/sdd-avaliador-guard.py" ] \
                   && command -v python3 >/dev/null 2>&1 && claude_settings_em_dia "${ROOT}/.claude/settings.json"; then
                ok "claude: gerado (.claude/skills · CLAUDE.md · .claude/hooks + settings.json) · ${st} · cobre também Grok Build e GLM"
              else warn "claude: adaptador incompleto (guards de .claude/hooks ou .claude/settings.json; exige python3) — rode sync --vendors claude"; fi ;;
      cursor) if [ -d "${ROOT}/.cursor/skills" ]; then ok "cursor: gerado (.cursor/skills) · ${st}"
              else warn "cursor: adaptador não gerado — rode sync --vendors cursor"; fi ;;
      gemini) if [ -f "${ROOT}/GEMINI.md" ] && gemini_settings_em_dia "${ROOT}/.gemini/settings.json"; then ok "gemini: gerado (GEMINI.md · .gemini/settings.json) · ${st}"
              else warn "gemini: adaptador incompleto — rode sync --vendors gemini"; fi ;;
    esac
  done
  if ls "${ROOT}"/.agents/skills/sdd-*/agents/openai.yaml >/dev/null 2>&1 || ls "${ROOT}"/.claude/skills/sdd-*/agents/openai.yaml >/dev/null 2>&1; then
    warn "skills do sdd-starter detectadas no mesmo projeto: os nomes sdd-* colidem — use um ou outro por projeto"
  fi
  # Pacote mais novo que o projeto: init nunca sobrescreve .agents/skills/<skill> nem sdd/bin/*, então
  # quem já instalou continua com a versão velha sem saber. Só aponta; quem apaga é a pessoa.
  local s vp vq f atrasados=0 pkg_skills="${PKG}/.agents/skills"
  for s in $(skills_da_fonte "${pkg_skills}"); do
    [ -f "${FONTE_SKILLS}/${s}/SKILL.md" ] || continue
    vq="$(versao_skill "${pkg_skills}/${s}/SKILL.md")"; vp="$(versao_skill "${FONTE_SKILLS}/${s}/SKILL.md")"
    [ -n "${vq}" ] && versao_menor "${vp}" "${vq}" || continue
    warn "${s} ${vp:-sem versão} no projeto, ${vq} no pacote — para receber: apague .agents/skills/${s} e rode init (edições suas nela se perdem)"
    atrasados=$((atrasados + 1))
  done
  for f in "${PKG}"/sdd/bin/*; do
    [ -f "${f}" ] && [ -f "${ROOT}/sdd/bin/${f##*/}" ] || continue
    cmp -s "${f}" "${ROOT}/sdd/bin/${f##*/}" && continue
    warn "sdd/bin/${f##*/} difere do pacote — se você não editou, apague e rode init"
    atrasados=$((atrasados + 1))
  done
  [ "${atrasados}" = "0" ] && ok "skills e sdd/bin/ em dia com o pacote"
  # Segredo já salvo no git (.env, .pfx, .p12, .pem com chave privada): o checar.sh do PACOTE, que casa
  # com esta versão da CLI, no modo --segredo — só leitura e sem rede, porque o doctor roda em todo init.
  local checar="${PKG}/.agents/skills/sdd-checar-ambiente/scripts/checar.sh" saida rc l
  if [ ! -f "${checar}" ]; then
    warn "pacote incompleto: .agents/skills/sdd-checar-ambiente/scripts/checar.sh ausente — baixe o sdd-open de novo"
  else
    saida="$(cd "${ROOT}" && "${BASH}" "${checar}" --segredo 2>&1)"; rc=$?
    case "${rc}" in
      0) ok "nenhum segredo salvo no git (.env, .pfx, .p12, .pem com chave privada)" ;;
      1) printf '%s\n' "${saida}" | while IFS= read -r l; do
           case "${l}" in
             '- '*) warn "${l#- }" ;;
             ''|'🔴 '*) : ;;
             *) printf '      %s\n' "${l#  }" >&2 ;;   # comando, medida, ou resto de um nome com quebra de linha
           esac
         done ;;
      *) warn "não consegui conferir segredo salvo no git (checar.sh saiu ${rc})" ;;
    esac
  fi
}

# ── execução ───────────────────────────────────────────────────────────────────
case "${VERBO}" in
  doctor)
    doctor; resultado "DIAGNÓSTICO CONCLUÍDO" "se algum item está ⚠️, a linha diz qual comando resolve."; exit 0 ;;
  sync)
    [ -d "${FONTE_SKILLS}" ] || die ".agents/skills/ não existe neste projeto" "rode init primeiro" 64
    if [ "${CHECK}" = "1" ]; then
      DIVERGENTES=0
      vendor_pedido claude && {
        declare_alvos_skills ".claude/skills" check
        orfaos_listar ".claude/skills" | while IFS= read -r o; do [ -n "${o}" ] && printf '%s\n' "${o}"; done
        n_orf=$(orfaos_listar ".claude/skills" | grep -c . || true); DIVERGENTES=$((DIVERGENTES + n_orf))
        { [ -f "${ROOT}/CLAUDE.md" ] && grep -qF '@AGENTS.md' "${ROOT}/CLAUDE.md"; } || { printf 'CLAUDE.md (sem a linha @AGENTS.md)\n'; DIVERGENTES=$((DIVERGENTES + 1)); }
        declare_alvos_adaptadores claude ".claude/hooks" check
        claude_settings_em_dia "${ROOT}/.claude/settings.json" || { printf '.claude/settings.json (guards do sdd-open fora de hooks.PreToolUse)\n'; DIVERGENTES=$((DIVERGENTES + 1)); }
      }
      vendor_pedido cursor && {
        declare_alvos_skills ".cursor/skills" check
        orfaos_listar ".cursor/skills" | while IFS= read -r o; do [ -n "${o}" ] && printf '%s\n' "${o}"; done
        n_orf=$(orfaos_listar ".cursor/skills" | grep -c . || true); DIVERGENTES=$((DIVERGENTES + n_orf))
      }
      vendor_pedido gemini && {
        gemini_md_em_dia || { printf 'GEMINI.md (ausente ou conteúdo divergente)\n'; DIVERGENTES=$((DIVERGENTES + 1)); }
        gemini_settings_em_dia "${ROOT}/.gemini/settings.json" || { printf '.gemini/settings.json (AGENTS.md fora de context.fileName)\n'; DIVERGENTES=$((DIVERGENTES + 1)); }
      }
      gerar_corpo_agents
      agents_md_em_dia "${ROOT}/AGENTS.md" "${CORPO_AGENTS}" || { printf 'AGENTS.md (bloco sdd-open)\n'; DIVERGENTES=$((DIVERGENTES + 1)); }
      if [ "${DIVERGENTES}" = "0" ]; then resultado "EM DIA" "todos os adaptadores refletem .agents/skills/."; exit 0; fi
      resultado "DIVERGENTE (${DIVERGENTES})" "os arquivos acima são gerados: edite a fonte em .agents/skills/ e rode sync; edições neles são sobrescritas. Órfãos não são apagados: remova à mão."
      exit 1
    fi ;;
esac

say "${VERBO} — plano"
planejar
plano_resumo
if ! plano_tem_mudanca; then
  [ "${VERBO}" = "init" ] && doctor
  resultado "EM DIA" "nada a fazer."; exit 0
fi
if [ "${DRY_RUN}" = "1" ]; then resultado "DRY-RUN" "nada foi escrito; rode sem --dry-run para aplicar."; exit 0; fi
confirmar
aplicar
if [ "${VERBO}" = "init" ]; then
  doctor
  dica="abra seu agente e peça a fase Define (ex.: /sdd-define ou /skill:sdd-define)."
  # Na branch padrão com remoto, o pre-commit recém-ligado (H6) recusaria o commit da própria instalação.
  if [ "$(hooks_estado)" = "LIGADO" ] && na_branch_padrao_com_remoto; then
    dica="leve a instalação para uma branch nova antes de commitar (a branch padrão já tem remoto e o hook recusa commit direto): git switch -c sdd-open-init · depois, ${dica}"
  fi
  resultado "INSTALADO" "${dica}"
else
  resultado "SINCRONIZADO" "adaptadores regenerados a partir de .agents/skills/."
fi
