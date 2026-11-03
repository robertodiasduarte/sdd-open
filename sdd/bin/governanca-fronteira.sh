#!/usr/bin/env bash
# governanca-fronteira.sh — fronteira de escrita dos agentes frescos do sdd-define: o cartógrafo (passo
# 1.5, só pode gravar sdd/contexto/<slug>.md) e o revisor de governança (passo 11, só pode gravar o
# relatório). Comparar só a linha do `git status` não vê a sobrescrita de um arquivo que já aparecia
# antes do despacho (o DEFINE recém-salvo é `??`): o snapshot guarda o sha256 de cada caminho.
#
# Uso:
#   governanca-fronteira.sh --snapshot <raiz-do-worktree> <arquivo-do-snapshot> [incluir…]
#       grava "<sha256|AUSENTE>\t<caminho absoluto>" para cada caminho de `git status --porcelain -z --untracked-files=all`
#       mais os IGNORADOS de sdd/ (--ignored=traditional: com --untracked-files=all, arquivo a arquivo). O arquivo do snapshot fica FORA do worktree (dentro ⇒ 64). [incluir…] =
#       caminhos absolutos que entram SEMPRE (o arquivo permitido): com sha se existem, AUSENTE se não.
#   governanca-fronteira.sh --comparar <antes> <depois> <permitido>…
#       para cada caminho novo, sumido ou com sha diferente: "MUDOU: <caminho>" se permitido, "FORA: <caminho>" senão.
#
# O snapshot também guarda o HEAD (linha `#HEAD`): um agente que edita um arquivo limpo e COMMITA deixa a
# árvore limpa de novo, e só o HEAD que andou denuncia — cada arquivo do commit sai como FORA.
#
# Exit: 0 só caminhos permitidos mudaram · 1 há FORA · 64 uso, snapshot ausente/ilegível ou enumeração que
# falhou (fronteira não verificada nunca vale como "nada mudou").
# Limites declarados: arquivo ignorado FORA de sdd/ (ex.: __pycache__/) não entra no snapshot; escrita FORA do
# worktree não é vista (a barreira ali são as permissões da sessão).
# Ordem de bytes sempre (LC_ALL=C): snapshot ordenado num locale e comparado noutro inventaria diferença.
# porcelain -z: sem -z o git escapa nome não-ASCII em octal e a sobrescrita fica invisível.
set -uo pipefail
export LC_ALL=C

uso() {
  echo "uso: $0 --snapshot <raiz-do-worktree> <arquivo-do-snapshot> [incluir…] | --comparar <antes> <depois> <permitido>…" >&2
  printf 'RESULTADO: ERRO DE USO\n→ a fronteira NÃO foi verificada; corrija a chamada e rode de novo.\n' >&2
  exit 64
}

# $1 raiz · $2 "todos"|"ignorados" · $3 pathspec · $4 arquivo onde acrescentar. rc do git e do python checados.
paths() {
  local raw; raw="$(mktemp)"
  git -C "$1" status --porcelain -z --untracked-files=all ${2:+--ignored=traditional} -- ${3:-.} > "${raw}" || { rm -f "${raw}"; return 1; }
  python3 -c '
import sys
so_ign = sys.argv[1] == "ignorados"
r = sys.stdin.buffer.read().split(b"\0")
i = 0
while i < len(r):
    e = r[i]; i += 1
    if len(e) < 4:
        continue
    xy, p = e[:2], e[3:]
    if xy[:1] in (b"R", b"C"):          # renomeado/copiado: o registro seguinte é a origem
        if b"\n" in p or (i < len(r) and b"\n" in r[i]):
            sys.stderr.write("caminho com quebra de linha: a fronteira não mede\n"); sys.exit(1)
        if not so_ign:
            sys.stdout.buffer.write(p + b"\n")
            if i < len(r) and r[i]:
                sys.stdout.buffer.write(r[i] + b"\n")
        i += 1
        continue
    if so_ign and xy != b"!!":
        continue
    if b"\n" in p:
        sys.stderr.write("caminho com quebra de linha: a fronteira não mede: %r\n" % p); sys.exit(1)
    sys.stdout.buffer.write(p + b"\n")
' "${2:-todos}" < "${raw}" >> "$4"; local rc=$?
  rm -f "${raw}"; return "${rc}"
}
# caminho absoluto canônico: o ancestral mais próximo que existe passa por `pwd -P` (no macOS /var é link
# para /private/var; sem isso o permitido não casa com a raiz canonizada e vira FORA ou "fora do worktree")
canon() {
  local p="$1" resto="" base
  case "${p}" in /*) ;; *) p="$(pwd -P)/${p}" ;; esac
  while [ ! -d "${p}" ]; do
    base="$(basename "${p}")"; resto="/${base}${resto}"; p="$(dirname "${p}")"
    [ "${p}" = "/" ] && break
  done
  printf '%s%s' "$(cd "${p}" && pwd -P)" "${resto}"
}
todos_paths() { # $1 raiz · $2 arquivo de saída
  : > "$2"
  paths "$1" "" "" "$2" || return 1
  if [ -d "$1/sdd" ]; then paths "$1" ignorados sdd/ "$2" || return 1; fi
  return 0
}

case "${1:-}" in
  --snapshot)
    [ "$#" -ge 3 ] || uso
    # snapshot que falha, por qualquer motivo, não deixa o arquivo de uma tentativa anterior no lugar
    rm -f "$3"
    [ -d "$2" ] || uso
    WT="$(cd "$2" && pwd -P)" || uso
    TOP="$(git -C "${WT}" rev-parse --show-toplevel 2>/dev/null)" || { echo "não é um repositório git: ${WT}" >&2; uso; }
    # os caminhos do porcelain são relativos à RAIZ: um subdiretório viraria AUSENTE nos dois lados
    [ "$(cd "${TOP}" && pwd -P)" = "${WT}" ] || { echo "<raiz-do-worktree> tem de ser a raiz do repositório (${TOP}), não ${WT}" >&2; uso; }
    OUT="$3"; shift 3
    OUT_DIR="$(cd "$(dirname "${OUT}")" 2>/dev/null && pwd -P)" || { echo "pasta do snapshot inexistente: $(dirname "${OUT}")" >&2; uso; }
    case "${OUT_DIR}/" in "${WT}"/*) echo "o snapshot fica FORA do worktree (senão ele mesmo aparece como ??): ${OUT}" >&2; uso ;; esac
    INCL=""
    for x in "$@"; do
      case "${x}" in *$'\n'*) echo "incluir com quebra de linha: a fronteira não mede" >&2; uso ;; esac
      x="$(canon "${x}")"
      case "${x}" in "${WT}"/*) ;; *) echo "incluir fora do worktree: ${x}" >&2; uso ;; esac
      INCL="${INCL}${x}
"
    done
    lista="$(mktemp)"; parcial="${OUT}.parcial.$$"; trap 'rm -f "${lista}" "${parcial}"' EXIT
    todos_paths "${WT}" "${lista}" || { echo "a enumeração falhou (git status ou caminho com quebra de linha): snapshot não gravado" >&2; uso; }
    printf '%s' "${INCL}" | while IFS= read -r x; do [ -n "${x}" ] && printf '%s\n' "${x#"${WT}"/}"; done >> "${lista}"
    sort -u "${lista}" | while IFS= read -r p; do
      [ -z "${p}" ] && continue
      if [ -f "${WT}/${p}" ]; then h="$(shasum -a 256 "${WT}/${p}" | cut -d' ' -f1)"; else h=AUSENTE; fi
      printf '%s\t%s\n' "${h}" "${WT}/${p}"
    done | sort > "${parcial}" || { echo "não consegui gravar o snapshot" >&2; uso; }
    head_sha="$(git -C "${WT}" rev-parse -q --verify HEAD 2>/dev/null || echo AUSENTE)"
    printf '#HEAD\t%s\t%s\n' "${head_sha}" "${WT}" >> "${parcial}" && mv "${parcial}" "${OUT}" || { echo "não consegui gravar o snapshot" >&2; uso; }
    printf 'RESULTADO: SNAPSHOT GRAVADO\n→ despache o agente e, logo que ele voltar, tire o snapshot de depois sem editar nada no meio.\n'
    ;;
  --comparar)
    [ "$#" -ge 4 ] && [ -f "$2" ] && [ -r "$2" ] && [ -f "$3" ] && [ -r "$3" ] || uso
    A="$2"; D="$3"; shift 3
    fora=0
    tmp="$(mktemp -d)"; trap 'rm -rf "${tmp}"' EXIT; dif="${tmp}/dif"
    # diferença simétrica por linha (sha + caminho): cobre novo, sumido e sobrescrito. O comm roda FORA
    # de substituição de processo: lá o rc dele se perde e um snapshot ilegível viraria "nada mudou".
    # grep -v sai 1 quando o snapshot só tem a linha #HEAD (árvore limpa): isso não é erro de leitura
    { grep -v '^#HEAD' "${A}" || [ $? -eq 1 ]; } | sort > "${tmp}/a" && { grep -v '^#HEAD' "${D}" || [ $? -eq 1 ]; } | sort > "${tmp}/d" \
      || { echo "não consegui ler os snapshots" >&2; uso; }
    ha="$(grep '^#HEAD' "${A}" | head -1)"; hd="$(grep '^#HEAD' "${D}" | head -1)"
    [ -n "${ha}" ] && [ -n "${hd}" ] || { echo "snapshot sem a linha #HEAD (gravado por outra versão?): refaça os dois" >&2; uso; }
    comm -3 "${tmp}/a" "${tmp}/d" > "${dif}" || { echo "não consegui comparar os snapshots" >&2; uso; }
    sed $'s/^\t//' "${dif}" | cut -f2- > "${tmp}/mudou.0"
    if [ "${ha}" != "${hd}" ]; then
      # o HEAD andou durante o despacho: todo arquivo dos commits novos conta (um commit limpa a árvore)
      wt="$(printf '%s' "${hd}" | cut -f3)"; sa="$(printf '%s' "${ha}" | cut -f2)"; sd="$(printf '%s' "${hd}" | cut -f2)"
      echo "FORA: HEAD mudou durante o despacho (${sa} → ${sd}): o agente commitou"; fora=1
      if [ "${sa}" != AUSENTE ] && [ "${sd}" != AUSENTE ]; then
        git -C "${wt}" diff --name-only -z "${sa}" "${sd}" 2>/dev/null | tr '\0' '\n' | sed "s|^|${wt}/|" >> "${tmp}/mudou.0"
      fi
    fi
    sort -u "${tmp}/mudou.0" > "${tmp}/mudou"
    while IFS= read -r p; do
      [ -z "${p}" ] && continue
      ok=0
      for perm in "$@"; do [ "${p}" = "${perm}" ] || [ "${p}" = "$(canon "${perm}")" ] && ok=1; done
      if [ "${ok}" = 1 ]; then printf 'MUDOU: %s\n' "${p}"; else printf 'FORA: %s\n' "${p}"; fora=1; fi
    done < "${tmp}/mudou"
    if [ "${fora}" = 1 ]; then
      printf 'RESULTADO: ESCRITA FORA DO PERMITIDO\n→ não apague nada: liste os caminhos FORA para a pessoa conferir, regrave o DEFINE se ele mudou e conte como falha (1 redespacho).\n'
    else
      printf 'RESULTADO: SÓ O PERMITIDO MUDOU\n→ siga com o arquivo que o agente gravou.\n'
    fi
    exit "${fora}"
    ;;
  *) uso ;;
esac
