# python.sh — acha o Python que roda e o deixa como `python3` no PATH. Lido com `.` por todo script do
# pacote que chama python3 (F16). Não é executado sozinho e, na carga, nunca para o script.
#
#   . "$(dirname "${BASH_SOURCE[0]}")/lib/python.sh"
#   sdd_python_pronto || { <a mensagem de "python3 ausente" do script>; exit <o código dele>; }
#   sdd_python_exigir      # para o script que não tem mensagem própria: causa, RESULTADO: PAROU, exit 64
#
# Ordem: SDD_PYTHON (se definido; uma palavra, caminho com espaço vale) · python3 · python · py -3. Serve o
# 1º que roda e é 3.9 ou mais novo.
#   - o python3 do PATH serve ⇒ nada muda (o caminho de macOS e Linux);
#   - serve outro ⇒ um calço: pasta de `mktemp -d` com um executável `python3` que chama o escolhido, posta
#     à frente do PATH. Vale para `python3 …`, `exec python3`, `env python3`, `xargs` e o shebang
#     `#!/usr/bin/env python3` (função de bash não valeria para esses);
#   - nenhum serve ⇒ nada muda no PATH, e `sdd_python_pronto` falha dizendo a causa uma vez: nenhum Python;
#     um Python que existe e não roda (no Windows, o atalho da Microsoft Store, que sai 9009); um Python mais
#     velho que o 3.9; ou o calço que não pôde ser criado.
# SDD_PYTHON_RESOLVIDO (python3, ou a pasta do calço) vai para o ambiente: os processos filhos não testam de novo.
# ⚠️ bash 3.2.

SDD_PYTHON_MOTIVO=""
SDD_PYTHON_DITO=""

# Versão X.Y que o candidato imprime (vazio se não roda). Funciona também no Python 2.
sdd_python_versao() {
  "$@" -c 'import sys; sys.stdout.write("%d.%d" % sys.version_info[:2])' 2>/dev/null </dev/null
}

# Aspas simples para o sh do calço: a'b ⇒ 'a'\''b'.
sdd_python_aspas() { printf "'%s'" "$(printf '%s' "$1" | sed "s/'/'\\\\''/g")"; }

sdd_python_calco() {   # $1 = o comando, já entre aspas simples (ex.: 'python' ou 'py' -3)
  local d
  d="$(mktemp -d "${TMPDIR:-/tmp}/sdd-python.XXXXXX" 2>/dev/null)" \
    && printf '#!/bin/sh\nexec %s "$@"\n' "$1" > "${d}/python3" 2>/dev/null \
    && chmod +x "${d}/python3" 2>/dev/null \
    || { SDD_PYTHON_MOTIVO="não consegui criar o calço do Python na pasta temporária (${TMPDIR:-/tmp}): confira se ela existe e aceita escrita"; return 1; }
  SDD_PYTHON_RESOLVIDO="${d}"
  PATH="${d}:${PATH}"
  export SDD_PYTHON_RESOLVIDO PATH
}

# Testa um candidato: 0 serve; 1 existe e não serve (anota o motivo); 2 não existe.
sdd_python_testa() {
  local v
  command -v "$1" >/dev/null 2>&1 || return 2
  v="$(sdd_python_versao "$@")"
  case "${v}" in
    "") [ -n "${SDD_PYTHON_MOTIVO}" ] || SDD_PYTHON_MOTIVO="o ${*} deste computador existe, mas não roda (no Windows, costuma ser o atalho da Microsoft Store)"
        return 1 ;;
    [0-2].*|3.[0-8]) SDD_PYTHON_MOTIVO="o ${*} deste computador é o Python ${v}; o SDD Open precisa do 3.9 ou mais novo"
        return 1 ;;
  esac
  return 0
}

sdd_python_resolver() {
  case "${SDD_PYTHON_RESOLVIDO:-}" in
    "") ;;
    python3) return 0 ;;
    *) if [ -x "${SDD_PYTHON_RESOLVIDO}/python3" ]; then
         case ":${PATH}:" in
           *":${SDD_PYTHON_RESOLVIDO}:"*) ;;
           *) PATH="${SDD_PYTHON_RESOLVIDO}:${PATH}"; export PATH ;;
         esac
         return 0
       fi
       SDD_PYTHON_RESOLVIDO="" ;;
  esac
  if [ -n "${SDD_PYTHON:-}" ] && sdd_python_testa "${SDD_PYTHON}"; then
    sdd_python_calco "$(sdd_python_aspas "${SDD_PYTHON}")"; return 0
  fi
  if sdd_python_testa python3; then
    SDD_PYTHON_RESOLVIDO=python3; export SDD_PYTHON_RESOLVIDO; return 0
  fi
  if sdd_python_testa python; then sdd_python_calco "'python'"; return 0; fi
  if sdd_python_testa py -3; then sdd_python_calco "'py' -3"; return 0; fi
  return 0
}

# 0 se há um python3 que serve no PATH; senão diz a causa (uma vez por processo) e devolve 1.
sdd_python_pronto() {
  [ -n "${SDD_PYTHON_RESOLVIDO:-}" ] && return 0
  if [ -n "${SDD_PYTHON_MOTIVO}" ] && [ -z "${SDD_PYTHON_DITO}" ]; then
    printf '⚠️  %s.\n' "${SDD_PYTHON_MOTIVO}" >&2
    SDD_PYTHON_DITO=1
  fi
  return 1
}

# Para quem não tem mensagem própria de "python3 ausente".
sdd_python_exigir() {
  sdd_python_pronto && return 0
  printf '🛑 %s: precisa do Python 3.9 ou mais novo.\n' "${0##*/}" >&2
  printf 'RESULTADO: PAROU\n' >&2
  printf '→ instale o Python 3.9 ou mais novo (Windows: winget install --id Python.Python.3.12 -e; macOS: brew install python; Linux: sudo apt install python3), feche e abra o terminal e rode de novo.\n' >&2
  exit 64
}

sdd_python_resolver
