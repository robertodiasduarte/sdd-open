#!/usr/bin/env bash
# copiar-docs.sh — leva para a frente nova os documentos SDD de papel (BRAINSTORM, DEFINE, DESIGN, UX
# review, revisão de governança) que estão no checkout principal e ainda NÃO foram salvos no git. A
# worktree nasce da branch padrão do remoto e não herda esses arquivos; sem a cópia, a frente abre sem a
# spec da própria feature.
#
# Uso: copiar-docs.sh <checkout-principal> <pasta-da-frente> <slug-da-frente>
#
# Regra única: só copia quando o nome é IDÊNTICO. De `DEFINE_RELATORIO_MENSAL.md` sai a feature
# `relatorio-mensal` (minúsculas, hífen no lugar do que não é letra nem número); ela precisa ser igual ao
# slug. Quando um só começa com o outro, a linha sai como PARECIDO e nada é copiado: cópia errada é pior
# que cópia ausente. Nunca sobrescreve o que a frente já tem e nunca segue link simbólico.
#
# Documento que JÁ está salvo no git do checkout principal e não existe na frente (o commit ainda não foi
# enviado, e a frente nasce da branch padrão do remoto) sai como NAO_COPIADO, com o que fazer: o script não
# copia arquivo rastreado, porque na frente ele viraria uma segunda versão do mesmo arquivo.
#
# Saída: uma linha por arquivo (COPIADO, JA_EXISTE, PARECIDO, IGNORADO, NAO_COPIADO), depois RESULTADO: e →.
# Exit: 0 (inclusive sem nada a copiar) · 2 uma cópia falhou · 64 uso, pasta inexistente ou <principal>
# fora de um repositório git.
# Compat: bash 3.2, git >= 2.20. Sem arrays associativos.
set -uo pipefail
export LC_ALL=C

uso() {
  echo "🛑 copiar-docs: $1" >&2
  echo "uso: copiar-docs.sh <checkout-principal> <pasta-da-frente> <slug-da-frente>" >&2
  printf 'RESULTADO: ERRO DE USO\n→ corrija a chamada e rode de novo; nada foi copiado.\n' >&2
  exit 64
}

[ "$#" -eq 3 ] || uso "são 3 argumentos"
PRINCIPAL="$1"; FRENTE="$2"; SLUG="$3"
[ -n "${SLUG}" ] || uso "o slug da frente está vazio"
case "${SLUG}" in *[!abcdefghijklmnopqrstuvwxyz0123456789-]*) uso "slug inválido: '${SLUG}' (minúsculas, números e hífen)" ;; esac
[ -d "${PRINCIPAL}" ] || uso "checkout principal não encontrado: ${PRINCIPAL}"
[ -d "${FRENTE}" ] || uso "pasta da frente não encontrada: ${FRENTE}"
git -C "${PRINCIPAL}" rev-parse --show-toplevel >/dev/null 2>&1 || uso "${PRINCIPAL} não é um repositório git"

TMP="$(mktemp -d 2>/dev/null || mktemp -d -t copiardocs)" || uso "não consegui criar a pasta temporária"
trap 'rm -rf "${TMP}"' EXIT

copiados=0; parecidos=0; falhas=0; nao_copiados=0; ignorados=0

# sem acento (RELATÓRIO = relatorio, como o slug da frente); minúsculas; o que não é letra nem número vira
# hífen; sem hífen nas pontas. As letras acentuadas entram por alternação: em LC_ALL=C cada uma são 2 bytes.
kebab() {
  printf '%s' "$1" \
    | sed -E -e 's/(á|à|â|ã|ä|Á|À|Â|Ã|Ä)/a/g' -e 's/(é|è|ê|ë|É|È|Ê|Ë)/e/g' -e 's/(í|ì|î|ï|Í|Ì|Î|Ï)/i/g' \
             -e 's/(ó|ò|ô|õ|ö|Ó|Ò|Ô|Õ|Ö)/o/g' -e 's/(ú|ù|û|ü|Ú|Ù|Û|Ü)/u/g' -e 's/(ç|Ç)/c/g' -e 's/(ñ|Ñ)/n/g' \
    | tr 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' 'abcdefghijklmnopqrstuvwxyz' \
    | sed -e 's/[^a-z0-9][^a-z0-9]*/-/g' -e 's/^-//' -e 's/-$//'
}

# nome do arquivo → feature em minúsculas com hífen; vazio se o prefixo não é de documento de papel
feature_de() {
  local base="$1" feat
  case "${base}" in */*) return 0 ;; esac
  case "${base}" in *.md) ;; *) return 0 ;; esac
  case "${base}" in
    BRAINSTORM_*)        feat="${base#BRAINSTORM_}" ;;
    DEFINE_*)            feat="${base#DEFINE_}" ;;
    DESIGN_*)            feat="${base#DESIGN_}" ;;
    UX_REVIEW_*)         feat="${base#UX_REVIEW_}" ;;
    GOVERNANCA_REVIEW_*) feat="${base#GOVERNANCA_REVIEW_}" ;;
    *) return 0 ;;
  esac
  kebab "${feat%.md}"
}

uma_pasta() {  # $1 = sdd/features | sdd/reviews
  local dir="$1" rel base fk dest lista="${TMP}/lista"
  [ -d "${PRINCIPAL}/${dir}" ] || return 0
  if [ -L "${PRINCIPAL}/sdd" ] || [ -L "${PRINCIPAL}/${dir}" ]; then
    printf 'IGNORADO %s (a pasta é um link no checkout principal)\n' "${dir}"; ignorados=$((ignorados + 1)); return 0
  fi
  # --others: o que o git não tem salvo, ignorado ou não. -z: nome com espaço ou acento chega inteiro.
  # --others + o que só está no índice: git add sem commit também é "não salvo": a frente não recebe por commit.
  { git -C "${PRINCIPAL}" ls-files --others -z -- "${dir}" \
    && git -C "${PRINCIPAL}" diff --cached --name-only --diff-filter=A -z -- "${dir}"; } > "${lista}.z" 2>/dev/null \
    || { echo "🛑 copiar-docs: o git não listou ${dir} em ${PRINCIPAL}" >&2; falhas=$((falhas + 1)); return 0; }
  while IFS= read -r -d '' rel; do
    [ -n "${rel}" ] || continue
    base="${rel#${dir}/}"
    fk="$(feature_de "${base}")"       # só o nível de cima e só os 5 prefixos
    [ -n "${fk}" ] || continue
    if [ "${fk}" = "${SLUG}" ]; then
      if [ -L "${PRINCIPAL}/${rel}" ] || [ ! -f "${PRINCIPAL}/${rel}" ]; then
        printf 'IGNORADO %s (é um link ou não é arquivo: não copio)\n' "${rel}"; ignorados=$((ignorados + 1)); continue
      fi
      dest="${FRENTE}/${rel}"
      if [ -e "${dest}" ] || [ -L "${dest}" ]; then
        printf 'JA_EXISTE %s (a frente já tem este arquivo: mantive o dela)\n' "${rel}"; continue
      fi
      if [ -L "${FRENTE}/sdd" ] || [ -L "${FRENTE}/${dir}" ]; then
        printf 'IGNORADO %s (a pasta de destino é um link: não copio)\n' "${rel}"; ignorados=$((ignorados + 1)); continue
      fi
      if mkdir -p "${FRENTE}/${dir}" && cp "${PRINCIPAL}/${rel}" "${dest}"; then
        printf 'COPIADO %s\n' "${rel}"; copiados=$((copiados + 1))
      else
        echo "🛑 copiar-docs: a cópia de ${rel} falhou" >&2; falhas=$((falhas + 1))
      fi
    else
      case "${fk}" in "${SLUG}"*) parecido=1 ;; *) case "${SLUG}" in "${fk}"*) parecido=1 ;; *) parecido=0 ;; esac ;; esac
      if [ "${parecido}" -eq 1 ]; then
        printf "PARECIDO %s (feature '%s' ≈ frente '%s'): não copiei, porque o nome não é idêntico.\n" "${rel}" "${fk}" "${SLUG}"
        parecidos=$((parecidos + 1))
      fi
    fi
  done < "${lista}.z"
  # salvo no git do principal e ausente na frente: o commit ainda não chegou à branch de onde a frente nasceu
  git -C "${PRINCIPAL}" ls-tree -r -z --name-only HEAD -- "${dir}" > "${lista}.z" 2>/dev/null || return 0
  while IFS= read -r -d '' rel; do
    [ -n "${rel}" ] || continue
    fk="$(feature_de "${rel#${dir}/}")"
    [ "${fk}" = "${SLUG}" ] || continue
    if [ ! -e "${FRENTE}/${rel}" ] && [ ! -L "${FRENTE}/${rel}" ]; then
      printf 'NAO_COPIADO %s (está salvo no git do checkout principal, mas não na branch de onde a frente nasceu)\n' "${rel}"
      nao_copiados=$((nao_copiados + 1))
    fi
  done < "${lista}.z"
}

uma_pasta sdd/features
uma_pasta sdd/reviews

if [ "${falhas}" -gt 0 ]; then
  printf 'RESULTADO: FALHA (%d copiado(s), %d falha(s))\n→ confira a permissão das pastas e rode de novo; o que já foi copiado fica.\n' "${copiados}" "${falhas}"
  exit 2
fi
if [ "${copiados}" -gt 0 ]; then
  printf 'RESULTADO: %d COPIADO(S)\n' "${copiados}"
else
  printf 'RESULTADO: NADA A COPIAR\n'
fi
# Uma seta só, que junta todos os casos: cadeia de elif esconde a orientação de quem perde a precedência.
seta=""
junta() { seta="${seta}${seta:+ }$1"; }
[ "${nao_copiados}" -eq 0 ] || junta "${nao_copiados} documento(s) desta frente estão em um commit do checkout principal que ainda não foi enviado: envie esse commit e atualize a frente, ou copie à mão para ${FRENTE}/."
[ "${ignorados}" -eq 0 ] || junta "${ignorados} item(ns) com link não foram copiados: confira as linhas IGNORADO e copie à mão o que for desta frente."
[ "${parecidos}" -eq 0 ] || junta "Se algum PARECIDO for desta frente, copie à mão para ${FRENTE}/sdd/features/ (ou sdd/reviews/); os demais ficam onde estão."
if [ -z "${seta}" ]; then
  if [ "${copiados}" -gt 0 ]; then
    seta="os documentos da feature já estão na frente; os originais continuam no checkout principal."
  else
    seta="nenhum documento com o nome desta frente estava fora do git; siga normalmente."
  fi
fi
printf '→ %s\n' "${seta}"
exit 0
