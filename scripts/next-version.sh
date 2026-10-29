#!/usr/bin/env bash
# next-version.sh — the tag of the next Release and the base to compare it against.
#
# Reads the vX.Y.Z tags of the repository in the current directory and prints, on stdout, three
# lines that fit straight into $GITHUB_OUTPUT:
#   TAG=vX.Y.Z   the tag to publish
#   NEW=1|0      1 = the tag does not exist yet (latest + 1 patch); 0 = HEAD already carries it
#   BASE=vA.B.C  the highest vX.Y.Z tag below TAG (what check-versions --base compares to)
#
# Usage:
#   scripts/next-version.sh            # push to main: HEAD's own tag, or latest + 1 patch
#   scripts/next-version.sh vX.Y.Z     # tag push: publish exactly this tag, which must be on HEAD
#
# Rules:
#   - only tags matching ^v[0-9]+\.[0-9]+\.[0-9]+$ count; ordering is by version, so v2.10.0
#     sorts above v2.9.0;
#   - a commit that already carries a vX.Y.Z tag never gets a second one: it publishes that tag
#     (a manual minor pushed together with main must not become v2.3.0 + v2.3.1);
#   - a new tag is only computed for a HEAD that descends from the latest one: a stale re-run of
#     an old commit must not publish old content as the newest version;
#   - the tag list is read whole in a loop, never through `| head -1`: under pipefail the early
#     close of the pipe kills the producer with SIGPIPE once the list grows.
#
# Exit: 0 ok · 1 no vX.Y.Z tag, tag not on HEAD, or HEAD behind the latest tag · 64 usage / not git.
# Messages go to stderr; stdout carries only the three lines.
#
# ⚠️ bash 3.2 · ${VAR} with braces before non-ASCII · no sort -V (absent on older macOS).

set -uo pipefail

falha() { # $1=exit $2=cause $3=fix
  printf '🛑 %s\nRESULTADO: SEM VERSÃO\n→ %s\n' "${2}" "${3}" >&2
  exit "${1}"
}

valida() { printf '%s\n' "${1}" | grep -qE '^v[0-9]+\.[0-9]+\.[0-9]+$'; }

menor() { # $1 < $2 (both vX.Y.Z) → 0
  local a1 a2 a3 b1 b2 b3
  IFS=. read -r a1 a2 a3 <<< "${1#v}"
  IFS=. read -r b1 b2 b3 <<< "${2#v}"
  [ "${a1}" -lt "${b1}" ] && return 0; [ "${a1}" -gt "${b1}" ] && return 1
  [ "${a2}" -lt "${b2}" ] && return 0; [ "${a2}" -gt "${b2}" ] && return 1
  [ "${a3}" -lt "${b3}" ]
}

[ $# -le 1 ] || falha 64 "uso: next-version.sh [vX.Y.Z]" "passe no máximo a tag empurrada."
PEDIDA="${1:-}"
if [ -n "${PEDIDA}" ] && ! valida "${PEDIDA}"; then
  falha 64 "tag fora do padrão vX.Y.Z: '${PEDIDA}'" "só tags vX.Y.Z viram Release; rc e afins não publicam."
fi

git rev-parse --git-dir >/dev/null 2>&1 \
  || falha 64 "não é um repositório git: ${PWD}" "rode na raiz do clone do sdd-open."

# Valid tags, highest version first.
VALIDAS=""
while IFS= read -r t; do
  [ -n "${t}" ] && valida "${t}" && VALIDAS="${VALIDAS}${t} "
done <<EOF
$(git for-each-ref --sort=-v:refname --format='%(refname:short)' 'refs/tags/v*' 2>/dev/null)
EOF

# Highest valid tag on HEAD, if any.
NA_HEAD=""
while IFS= read -r t; do
  [ -z "${NA_HEAD}" ] && [ -n "${t}" ] && valida "${t}" && NA_HEAD="${t}"
done <<EOF
$(git tag --points-at HEAD --list 'v*' --sort=-v:refname 2>/dev/null)
EOF

[ -n "${VALIDAS}" ] || falha 1 "nenhuma tag vX.Y.Z no repositório — sem ela não há de onde contar a próxima versão." \
  "crie a primeira tag à mão (git tag -a v1.0.0 -m '…') e empurre; depois a release segue sozinha."

if [ -n "${PEDIDA}" ]; then
  # Tag push: publish the pushed tag itself, never another tag that happens to share the commit.
  case " $(git tag --points-at HEAD --list 'v*' 2>/dev/null | tr '\n' ' ') " in
    *" ${PEDIDA} "*) TAG="${PEDIDA}"; NEW=0 ;;
    *) falha 1 "a tag ${PEDIDA} não aponta para HEAD." "faça checkout do commit da tag (o evento de push de tag já faz)." ;;
  esac
elif [ -n "${NA_HEAD}" ]; then
  TAG="${NA_HEAD}"; NEW=0
else
  set -- ${VALIDAS}
  ULTIMA="${1}"
  git merge-base --is-ancestor "${ULTIMA}" HEAD 2>/dev/null \
    || falha 1 "HEAD não descende da última release (${ULTIMA}) — publicar daqui chamaria conteúdo velho de versão nova." \
         "rode a release a partir de um commit de main posterior a ${ULTIMA}; re-run de execução antiga não publica."
  IFS=. read -r M m p <<< "${ULTIMA#v}"
  TAG="v${M}.${m}.$((p + 1))"; NEW=1
fi

BASE=""
for t in ${VALIDAS}; do
  if menor "${t}" "${TAG}"; then BASE="${t}"; break; fi
done

printf 'TAG=%s\nNEW=%s\nBASE=%s\n' "${TAG}" "${NEW}" "${BASE}"
exit 0
