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
  VENDORS=" $(printf '%s\n%s\n' "$(printf '%s' "${atuais}" | tr ',' '\n')" "$(printf '%s' "${VENDORS}" | tr ' ' '\n')" | grep -v '^$' | awk '!seen[$0]++' | paste -sd' ' -)"
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
# SKILL.md começa com frontmatter YAML: o cabeçalho vai como comentário YAML nas linhas 2-3.
# Outros arquivos recebem 2 linhas de comentário HTML no topo. Ambos carregam o token
# sdd-open:generated — a comparação desconta as linhas que o contêm.
escrever_gerado() { # $1=fonte $2=destino $3=skill $4=arquivo-relativo
  local fonte="${1}" dest="${2}" skill="${3}" rel="${4}" l1
  mkdir -p "$(dirname "${dest}")" || return 1
  l1="$(head -n 1 "${fonte}")"
  if [ "${l1}" = "---" ]; then
    { printf -- '---\n'
      printf '# %s — edite .agents/skills/%s/%s e rode sync\n' "${MARCA}" "${skill}" "${rel}"
      printf '# %s — edições neste arquivo são sobrescritas\n' "${MARCA}"
      tail -n +2 "${fonte}"
    } > "${dest}" || return 1
  else
    { printf '<!-- %s — edite .agents/skills/%s/%s e rode sync -->\n' "${MARCA}" "${skill}" "${rel}"
      printf '<!-- %s — edições neste arquivo são sobrescritas -->\n' "${MARCA}"
      cat "${fonte}"
    } > "${dest}" || return 1
  fi
}

gerado_em_dia() { # $1=fonte $2=destino → 0 se idêntico descontado o cabeçalho
  [ -f "${2}" ] || return 1
  grep -vF "${MARCA}" "${2}" | cmp -s - "${1}"
}

# ── plano ──────────────────────────────────────────────────────────────────────
plano_reset
declare_alvos_skills() { # $1=diretório destino (.claude/skills | .cursor/skills) $2=modo plan|apply|check
  local destdir="${1}" modo="${2}" skill f rel dest
  for skill in $(skills_da_fonte "${FONTE_SKILLS}"); do
    while IFS= read -r f; do
      [ -n "${f}" ] || continue
      rel="${f#${FONTE_SKILLS}/${skill}/}"
      dest="${ROOT}/${destdir}/${skill}/${rel}"
      case "${modo}" in
        plan)  if gerado_em_dia "${f}" "${dest}"; then plano_estado "${destdir}/${skill}/${rel}" emdia
               elif [ -e "${dest}" ]; then plano_estado "${destdir}/${skill}/${rel}" atualizar
               else plano_estado "${destdir}/${skill}/${rel}" novo; fi ;;
        apply) gerado_em_dia "${f}" "${dest}" || escrever_gerado "${f}" "${dest}" "${skill}" "${rel}" || return 1 ;;
        check) gerado_em_dia "${f}" "${dest}" || { printf '%s\n' "${destdir}/${skill}/${rel}"; DIVERGENTES=$((DIVERGENTES + 1)); } ;;
      esac
    done <<EOF
$(find "${FONTE_SKILLS}/${skill}" -type f 2>/dev/null | sort)
EOF
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
  vendor_pedido claude && { arquivos="${arquivos} CLAUDE.md"; dirs="${dirs} .claude/skills"; }
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
  saida=$(python3 -c 'import json,sys
try:
    json.load(open(sys.argv[1], encoding="utf-8"))
except json.JSONDecodeError as e:
    print(f"{e.lineno}: {e.msg}"); sys.exit(66)' "${dest}" 2>&1) || \
    die ".gemini/settings.json não é JSON válido (linha ${saida})" \
        "corrija ou renomeie o arquivo e rode de novo — nada foi alterado" 66
}

# Arquivos do pacote que sustentam as skills (bin, templates, playbook, config) e faltam em sdd/ do
# projeto — relativos a sdd/. Vazio = árvore completa. Fixtures ficam fora (exemplos, apagáveis).
sdd_faltantes() {
  local rel
  ( cd "${PKG}/sdd" && find templates bin playbook.md -type f | sort ) | while IFS= read -r rel; do
    [ -e "${ROOT}/sdd/${rel}" ] || printf '%s\n' "${rel}"
  done
  [ -f "${ROOT}/sdd/config.yaml" ] || printf 'config.yaml\n'
}

planejar() {
  destinos_checar
  # bloco do AGENTS.md
  gerar_corpo_agents; agents_md_checar
  if [ ! -f "${ROOT}/AGENTS.md" ]; then plano_estado "AGENTS.md" novo
  elif agents_md_em_dia "${ROOT}/AGENTS.md" "${CORPO_AGENTS}"; then plano_estado "AGENTS.md (bloco sdd-open)" emdia
  else plano_estado "AGENTS.md (só o bloco entre os marcadores)" atualizar; fi

  if [ "${VERBO}" = "init" ]; then
    if [ ! -d "${ROOT}/sdd" ]; then plano_estado "sdd/ (templates, fixtures, bin, playbook, config)" novo
    else
      n_falt=$(sdd_faltantes | grep -c . || true)
      if [ "${n_falt}" = "0" ]; then plano_estado "sdd/ (já existe — não será tocado)" emdia
      else plano_estado "sdd/ (já existe — completar ${n_falt} arquivo(s) do pacote ausente(s); o que existe não será tocado)" atualizar; fi
    fi
    for skill in $(skills_da_fonte "${FONTE_PKG_SKILLS}"); do
      if [ -d "${FONTE_SKILLS}/${skill}" ]; then plano_estado ".agents/skills/${skill} (já existe — fonte do usuário, não será tocada)" emdia
      else plano_estado ".agents/skills/${skill}" novo; fi
    done
  fi

  vendor_pedido claude && {
    if [ -f "${ROOT}/CLAUDE.md" ] && grep -qF '@AGENTS.md' "${ROOT}/CLAUDE.md"; then plano_estado "CLAUDE.md" emdia
    elif [ -f "${ROOT}/CLAUDE.md" ]; then plano_estado "CLAUDE.md (acrescentar @AGENTS.md)" atualizar
    else plano_estado "CLAUDE.md" novo; fi
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
  fi

  merge_agents_md "${ROOT}/AGENTS.md" "${CORPO_AGENTS}" || die "${falha_escrita} (AGENTS.md)" "verifique permissões; rode de novo" 1

  vendor_pedido claude && {
    if [ ! -f "${ROOT}/CLAUDE.md" ]; then printf '@AGENTS.md\n' > "${ROOT}/CLAUDE.md" || die "${falha_escrita} (CLAUDE.md)" "verifique permissões; rode de novo" 1
    elif ! grep -qF '@AGENTS.md' "${ROOT}/CLAUDE.md"; then printf '%s\n' '' '@AGENTS.md' >> "${ROOT}/CLAUDE.md" || die "${falha_escrita} (CLAUDE.md)" "verifique permissões; rode de novo" 1; fi
    declare_alvos_skills ".claude/skills" apply || die "${falha_escrita} (.claude/skills)" "verifique permissões; rode de novo" 1
    for o in $(orfaos_listar ".claude/skills" | cut -d' ' -f1); do warn "adaptador órfão mantido (sync nunca apaga): ${o} — remova à mão se não quiser mais a skill"; done
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
    "$(command -v python3 >/dev/null 2>&1 && python3 -c 'import sys;print(".".join(map(str,sys.version_info[:2])))' || echo 'ausente')"
  if [ -d "${ROOT}/sdd" ]; then
    n_falt=$(sdd_faltantes | grep -c . || true)
    if [ "${n_falt}" = "0" ]; then ok "sdd/ presente ($(ls "${ROOT}/sdd/features" 2>/dev/null | wc -l | tr -d ' ') feature(s) em sdd/features/)"
    else warn "sdd/ incompleto — ${n_falt} arquivo(s) do pacote ausente(s), ex.: sdd/$(sdd_faltantes | head -1) — rode init de novo (completa sem tocar o que existe)"; fi
  else warn "sdd/ ausente — rode init"; fi
  [ -f "${ROOT}/AGENTS.md" ] && grep -qF "${ABRE}" "${ROOT}/AGENTS.md" && ok "AGENTS.md com o bloco sdd-open" \
                             || warn "AGENTS.md sem o bloco sdd-open — rode init ou sync"
  [ -d "${FONTE_SKILLS}" ] && ok ".agents/skills/ com $(skills_da_fonte "${FONTE_SKILLS}" | wc -l | tr -d ' ') skill(s) sdd-*" \
                            || warn ".agents/skills/ ausente"
  local lista_doc="${VENDORS}"; [ -z "${lista_doc}" ] && lista_doc="${VENDORS_SUPORTADOS}"
  for v in ${lista_doc}; do
    bin="$(vendor_binario "${v}")"
    if command -v "${bin}" >/dev/null 2>&1; then st="CLI encontrado"; else st="CLI não encontrado no PATH"; fi
    case "${v}" in
      codex|kimi) ok "${v}: nativo — nada a gerar ($(vendor_nativo_motivo "${v}")) · ${st}" ;;
      claude) if [ -d "${ROOT}/.claude/skills" ]; then ok "claude: gerado (.claude/skills · CLAUDE.md) · ${st} · cobre também Grok Build e GLM"
              else warn "claude: adaptador não gerado — rode sync --vendors claude"; fi ;;
      cursor) if [ -d "${ROOT}/.cursor/skills" ]; then ok "cursor: gerado (.cursor/skills) · ${st}"
              else warn "cursor: adaptador não gerado — rode sync --vendors cursor"; fi ;;
      gemini) if [ -f "${ROOT}/GEMINI.md" ] && gemini_settings_em_dia "${ROOT}/.gemini/settings.json"; then ok "gemini: gerado (GEMINI.md · .gemini/settings.json) · ${st}"
              else warn "gemini: adaptador incompleto — rode sync --vendors gemini"; fi ;;
    esac
  done
  if ls "${ROOT}"/.agents/skills/sdd-*/agents/openai.yaml >/dev/null 2>&1 || ls "${ROOT}"/.claude/skills/sdd-*/agents/openai.yaml >/dev/null 2>&1; then
    warn "skills do sdd-starter detectadas no mesmo projeto: os nomes sdd-* colidem — use um ou outro por projeto"
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
  resultado "INSTALADO" "abra seu agente e peça a fase Define (ex.: /sdd-define ou /skill:sdd-define)."
else
  resultado "SINCRONIZADO" "adaptadores regenerados a partir de .agents/skills/."
fi
