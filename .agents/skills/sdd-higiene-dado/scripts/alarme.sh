#!/usr/bin/env bash
# alarme.sh — instala, confere e remove o alarme de commit da skill sdd-higiene-dado.
#
# Uso (de dentro da pasta do projeto):
#   bash alarme.sh verificar     só lê: diz se dá para instalar e o que já existe
#   bash alarme.sh instalar      grava .git/hooks/pre-commit (só depois do OK da pessoa)
#   bash alarme.sh desinstalar   remove o alarme, se for o desta skill
#
# Nunca mexe em alarme de outra origem (husky, lefthook, core.hooksPath, pre-commit escrito à mão).
# Saída: 0 = feito ou só informação; 2 = recusado (outro alarme); 1 = erro (fora de um repositório git).

set -u

MARCA="# sdd-higiene-dado: alarme de commit (pre-commit)"
AQUI="$(cd "$(dirname "$0")" && pwd)"
ORIGEM="${AQUI}/pre-commit.sh"

versao_skill() { grep -m1 '^  version:' "${AQUI}/../SKILL.md" 2>/dev/null | sed 's/.*: *//; s/"//g'; }
versao_de() { grep -m1 '^# versão:' "$1" 2>/dev/null | sed 's/^# versão: *//'; }

git rev-parse --show-toplevel >/dev/null 2>&1 || {
  echo "Esta pasta não é um repositório git. Abra o terminal na pasta do projeto e rode de novo."
  exit 1
}

HOOKS_PATH="$(git config --get core.hooksPath 2>/dev/null || true)"
HOOK="$(git rev-parse --path-format=absolute --git-path hooks/pre-commit 2>/dev/null || git rev-parse --git-path hooks/pre-commit)"
VERSAO="$(versao_skill)"

# Estado: LIVRE (nada instalado) | NOSSO (alarme desta skill) | OUTRO (alarme de outra origem)
if [ -n "${HOOKS_PATH}" ]; then
  ESTADO="OUTRO"; DESCR="o projeto usa outro gerenciador de alarmes (core.hooksPath = ${HOOKS_PATH}, comum com husky)"
elif [ -f "${HOOK}" ] && grep -qF "${MARCA}" "${HOOK}"; then
  ESTADO="NOSSO"; DESCR="o alarme desta skill já está instalado (versão $(versao_de "${HOOK}"))"
elif [ -f "${HOOK}" ]; then
  ESTADO="OUTRO"; DESCR="já existe outro alarme de commit em ${HOOK}"
else
  ESTADO="LIVRE"; DESCR="nenhum alarme de commit instalado"
fi

como_acrescentar() {
  cat <<TXT
Não instalei para não interferir no alarme que já existe.
Para acrescentar esta verificação à mão, inclua no alarme existente (ex.: .husky/pre-commit) a linha:
  bash "${ORIGEM}" || exit 1
TXT
}

case "${1:-}" in
  verificar)
    echo "Estado: ${DESCR}."
    case "${ESTADO}" in
      LIVRE) echo "Dá para instalar: o alarme seria gravado em ${HOOK} e vale para todas as frentes deste projeto." ;;
      NOSSO) echo "Instalar de novo atualiza para a versão ${VERSAO}. Para remover: bash \"${AQUI}/alarme.sh\" desinstalar" ;;
      OUTRO) como_acrescentar; exit 2 ;;
    esac
    ;;
  instalar)
    [ "${ESTADO}" = "OUTRO" ] && { echo "Recusado: ${DESCR}."; como_acrescentar; exit 2; }
    mkdir -p "$(dirname "${HOOK}")"
    # A cópia que o sync do sdd-open gera (.claude/skills, .cursor/skills) traz 2 linhas sdd-open:generated
    # depois do shebang: elas não vão para o hook, que não é arquivo gerado e não é reescrito pelo sync.
    corpo="$(grep -v -F 'sdd-open:generated' "${ORIGEM}")"
    { printf '%s\n' "${corpo}" | sed -n '1,2p'; echo "# versão: ${VERSAO}"; printf '%s\n' "${corpo}" | sed '1,2d'; } > "${HOOK}"
    chmod +x "${HOOK}"
    echo "Alarme instalado em ${HOOK} (versão ${VERSAO})."
    echo "Vale para todas as frentes deste projeto. Para pular um commit, depois de conferir: git commit --no-verify"
    echo "Para desinstalar: bash \"${AQUI}/alarme.sh\" desinstalar   (ou: rm \"${HOOK}\")"
    ;;
  desinstalar)
    case "${ESTADO}" in
      NOSSO) rm -f "${HOOK}"; echo "Alarme removido de ${HOOK}." ;;
      LIVRE) echo "Não há alarme desta skill instalado neste projeto. Nada foi alterado." ;;
      OUTRO) echo "Recusado: ${DESCR}, e ele não é desta skill. Nada foi alterado."; exit 2 ;;
    esac
    ;;
  *)
    echo "Uso: bash alarme.sh verificar | instalar | desinstalar"
    exit 1
    ;;
esac
exit 0
