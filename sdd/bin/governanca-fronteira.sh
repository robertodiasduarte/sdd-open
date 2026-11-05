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
# Além dos arquivos, o snapshot guarda 3 estados do git que não aparecem no `git status` (linhas `#REF`,
# `#INDICE`, `#GIT`): a branch, o índice (um `git add`, ou a marca que esconde um arquivo editado:
# --assume-unchanged e --skip-worktree) e a configuração local, o `info/exclude` e os hooks de `.git`.
# Qualquer um que mude durante o despacho sai como FORA.
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
  git -C "$1" status --porcelain -z --untracked-files=all ${2:+--ignored=traditional} -- ${3:-.} > "${raw}" 2> "${raw}.err" || { rm -f "${raw}" "${raw}.err"; return 1; }
  # pasta sem permissão: o git avisa no stderr e sai 0, com a pasta fora da lista: enumeração parcial não é enumeração
  if grep -q 'could not open directory' "${raw}.err"; then
    cat "${raw}.err" >&2; echo "há pasta que o git não conseguiu abrir: a fronteira não mede" >&2
    rm -f "${raw}" "${raw}.err"; return 1
  fi
  rm -f "${raw}.err"
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
canon() { # realpath: resolve link de pasta E de arquivo; o trecho que ainda não existe fica como está
  python3 -c 'import os, sys; sys.stdout.write(os.path.realpath(sys.argv[1]))' "$1"
}
# 3 linhas com o estado do git que o `git status` não mostra: branch, índice e o que mora em .git
estado_git() { # $1 raiz
  python3 -c '
import hashlib, os, subprocess, sys
wt = sys.argv[1]
def git(*a):
    r = subprocess.run(["git", "-C", wt] + list(a), capture_output=True)
    return r.returncode, r.stdout
rc, ref = git("symbolic-ref", "-q", "HEAD")
ref = ref.decode("utf-8", "replace").strip() if rc == 0 and ref.strip() else "DETACHED"
rc, idx = git("ls-files", "-s", "-v", "-z")
rc1, comum = git("rev-parse", "--git-common-dir")
rc2, gd = git("rev-parse", "--git-dir")
if rc != 0 or rc1 != 0 or rc2 != 0:
    sys.exit(1)
def absoluto(p):
    p = p.decode("utf-8", "surrogateescape").strip()
    return p if os.path.isabs(p) else os.path.join(wt, p)
comum, gd = absoluto(comum), absoluto(gd)
alvos = [os.path.join(comum, "config"), os.path.join(comum, "info", "exclude"), os.path.join(gd, "config.worktree")]
hooks = os.path.join(comum, "hooks")
if os.path.isdir(hooks):
    alvos += [os.path.join(hooks, n) for n in sorted(os.listdir(hooks))]
h = hashlib.sha256()
for a in alvos:
    h.update(os.path.relpath(a, comum).encode("utf-8", "surrogateescape") + b"\0")
    if os.path.islink(a):
        h.update(b"link:" + os.readlink(a).encode("utf-8", "surrogateescape"))
    # um hook que é link executa o arquivo de destino: o que vale é o conteúdo dele, não só para onde aponta
    if os.path.isfile(a):
        try:
            with open(a, "rb") as f:
                h.update(hashlib.sha256(f.read()).digest())
            h.update(b"x" if os.access(a, os.X_OK) else b"-")
        except OSError:
            h.update(b"ilegivel")
    elif not os.path.islink(a):
        h.update(b"ausente")
print("#REF\t" + ref)
print("#INDICE\t" + hashlib.sha256(idx).hexdigest())
print("#GIT\t" + h.hexdigest())
' "$1"
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
    [ -d "$2" ] || uso
    WT="$(cd "$2" && pwd -P)" || uso
    TOP="$(git -C "${WT}" rev-parse --show-toplevel 2>/dev/null)" || { echo "não é um repositório git: ${WT}" >&2; uso; }
    # os caminhos do porcelain são relativos à RAIZ: um subdiretório viraria AUSENTE nos dois lados
    [ "$(cd "${TOP}" && pwd -P)" = "${WT}" ] || { echo "<raiz-do-worktree> tem de ser a raiz do repositório (${TOP}), não ${WT}" >&2; uso; }
    OUT="$3"; shift 3
    OUT_DIR="$(cd "$(dirname "${OUT}")" 2>/dev/null && pwd -P)" || { echo "pasta do snapshot inexistente: $(dirname "${OUT}")" >&2; uso; }
    case "${OUT_DIR}/" in "${WT}"/*) echo "o snapshot fica FORA do worktree (senão ele mesmo aparece como ??): ${OUT}" >&2; uso ;; esac
    # só agora, com o destino validado fora do worktree: um snapshot que falha daqui em diante não deixa o
    # arquivo de uma tentativa anterior no lugar (antes da validação, o rm apagaria um arquivo do projeto)
    rm -f "${OUT}"
    INCL=""; PERM=""
    for x in "$@"; do
      case "${x}" in *$'\n'*) echo "incluir com quebra de linha: a fronteira não mede" >&2; uso ;; esac
      c="$(canon "${x}")"
      case "${c}" in "${WT}"/*) ;; *) echo "incluir fora do worktree: ${c}" >&2; uso ;; esac
      INCL="${INCL}${c}
"
      # o permitido é resolvido AGORA, antes do despacho, e fica no snapshot: resolver depois deixaria um link
      # criado pelo agente no caminho permitido autorizar a escrita noutro arquivo
      PERM="${PERM}#PERMITIDO	${x}	${c}
"
    done
    lista="$(mktemp)"; parcial="${OUT}.parcial.$$"; trap 'rm -f "${lista}" "${parcial}"' EXIT
    todos_paths "${WT}" "${lista}" || { echo "a enumeração falhou (git status ou caminho com quebra de linha): snapshot não gravado" >&2; uso; }
    printf '%s' "${INCL}" | while IFS= read -r x; do [ -n "${x}" ] && printf '%s\n' "${x#"${WT}"/}"; done >> "${lista}"
    # hash e caminho canônico (realpath) num processo só: um link para o arquivo permitido vira o próprio
    # permitido; o link em si entra com o destino como "hash" (re-apontar o link também é escrita); arquivo
    # ilegível recusa o snapshot inteiro (nunca vira hash vazio)
    sort -u "${lista}" | python3 -c '
import hashlib, os, sys
wt = sys.argv[1]
saida = []
for p in sys.stdin.read().split("\n"):
    if not p:
        continue
    a = os.path.join(wt, p)
    if os.path.islink(a):
        saida.append("link:%s\t%s" % (os.readlink(a), a))
    r = os.path.realpath(a)
    if os.path.isfile(r):
        h = hashlib.sha256()
        try:
            with open(r, "rb") as f:
                for bloco in iter(lambda: f.read(1 << 20), b""):
                    h.update(bloco)
        except OSError as e:
            sys.stderr.write("não consegui ler %s: snapshot não gravado (%s)\n" % (a, e)); sys.exit(1)
        saida.append("%s\t%s" % (h.hexdigest(), r))
    else:
        saida.append("AUSENTE\t%s" % r)
sys.stdout.write("".join(l + "\n" for l in sorted(set(saida))))
' "${WT}" > "${parcial}" || { echo "não consegui gravar o snapshot" >&2; uso; }
    head_sha="$(git -C "${WT}" rev-parse -q --verify HEAD 2>/dev/null || echo AUSENTE)"
    eg="$(estado_git "${WT}")" || { echo "não consegui ler o estado do git (branch, índice, .git): snapshot não gravado" >&2; uso; }
    { printf '#HEAD\t%s\t%s\n' "${head_sha}" "${WT}"; printf '%s\n' "${eg}"; printf '%s' "${PERM}"; } >> "${parcial}" && mv "${parcial}" "${OUT}" || { echo "não consegui gravar o snapshot" >&2; uso; }
    printf 'RESULTADO: SNAPSHOT GRAVADO\n→ despache o agente e, logo que ele voltar, tire o snapshot de depois sem editar nada no meio.\n'
    ;;
  --comparar)
    [ "$#" -ge 4 ] && [ -f "$2" ] && [ -r "$2" ] && [ -f "$3" ] && [ -r "$3" ] || uso
    A="$2"; D="$3"; shift 3
    fora=0
    tmp="$(mktemp -d)"; trap 'rm -rf "${tmp}"' EXIT; dif="${tmp}/dif"
    # diferença simétrica por linha (sha + caminho): cobre novo, sumido e sobrescrito. O comm roda FORA
    # de substituição de processo: lá o rc dele se perde e um snapshot ilegível viraria "nada mudou".
    # grep -v sai 1 quando o snapshot só tem as linhas # (árvore limpa): isso não é erro de leitura
    { grep -v '^#' "${A}" || [ $? -eq 1 ]; } | sort > "${tmp}/a" && { grep -v '^#' "${D}" || [ $? -eq 1 ]; } | sort > "${tmp}/d" \
      || { echo "não consegui ler os snapshots" >&2; uso; }
    ha="$(grep '^#HEAD' "${A}" | head -1)"; hd="$(grep '^#HEAD' "${D}" | head -1)"
    [ -n "${ha}" ] && [ -n "${hd}" ] || { echo "snapshot sem a linha #HEAD (gravado por outra versão?): refaça os dois" >&2; uso; }
    comm -3 "${tmp}/a" "${tmp}/d" > "${dif}" || { echo "não consegui comparar os snapshots" >&2; uso; }
    sed $'s/^\t//' "${dif}" | cut -f2- > "${tmp}/mudou.0"
    # caminhos que são (ou passaram a ser) link: o permitido virar link é escrita fora do permitido
    sed $'s/^\t//' "${dif}" | grep '^link:' | cut -f2- | sort -u > "${tmp}/links" || true
    # o permitido como foi resolvido no snapshot de ANTES (nunca agora)
    grep '^#PERMITIDO' "${A}" > "${tmp}/perm" || true
    if [ "${ha}" != "${hd}" ]; then
      # o HEAD andou durante o despacho: todo arquivo dos commits novos conta (um commit limpa a árvore)
      wt="$(printf '%s' "${hd}" | cut -f3)"; sa="$(printf '%s' "${ha}" | cut -f2)"; sd="$(printf '%s' "${hd}" | cut -f2)"
      echo "FORA: HEAD mudou durante o despacho (${sa} → ${sd}): o agente commitou"; fora=1
      if [ "${sa}" != AUSENTE ] && [ "${sd}" != AUSENTE ]; then
        # sem sed: a raiz entra como texto, e um & ou uma barra vertical no nome da pasta quebraria a troca
        git -C "${wt}" diff --name-only -z "${sa}" "${sd}" 2>/dev/null | tr '\0' '\n' \
          | while IFS= read -r f; do [ -n "${f}" ] && printf '%s/%s\n' "${wt}" "${f}"; done >> "${tmp}/mudou.0"
      fi
    fi
    # estado do git que o status não mostra: mudou durante o despacho ⇒ FORA
    for chave in REF INDICE GIT; do
      va="$(grep "^#${chave}	" "${A}" | head -1 | cut -f2-)"; vd="$(grep "^#${chave}	" "${D}" | head -1 | cut -f2-)"
      [ -n "${va}" ] && [ -n "${vd}" ] || { echo "snapshot sem a linha #${chave} (gravado por outra versão?): refaça os dois" >&2; uso; }
      if [ "${va}" != "${vd}" ]; then
        case "${chave}" in
          REF)    echo "FORA: a branch mudou durante o despacho (${va} → ${vd})" ;;
          INDICE) echo "FORA: o índice do git mudou durante o despacho (git add, reset ou arquivo marcado para o git não olhar)" ;;
          GIT)    echo "FORA: a configuração, o exclude ou os hooks de .git mudaram durante o despacho" ;;
        esac
        fora=1
      fi
    done
    sort -u "${tmp}/mudou.0" > "${tmp}/mudou"
    while IFS= read -r p; do
      [ -z "${p}" ] && continue
      ok=0
      for perm in "$@"; do
        [ "${p}" = "${perm}" ] && ok=1
        while IFS="$(printf '\t')" read -r _ lit can; do
          [ "${lit}" = "${perm}" ] && [ "${p}" = "${can}" ] && ok=1
        done < "${tmp}/perm"
      done
      if grep -qxF -- "${p}" "${tmp}/links"; then
        printf 'FORA: %s (virou ou deixou de ser link durante o despacho)\n' "${p}"; fora=1
      elif [ "${ok}" = 1 ]; then printf 'MUDOU: %s\n' "${p}"; else printf 'FORA: %s\n' "${p}"; fora=1; fi
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
