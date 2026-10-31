#!/usr/bin/env bash
# alarme.sh — instala, confere e remove o alarme de commit da skill sdd-higiene-dado.
#
# Uso (de dentro da pasta do projeto):
#   bash alarme.sh verificar     só lê: diz se dá para instalar e o que já existe
#   bash alarme.sh instalar      grava .git/hooks/pre-commit (só depois do OK da pessoa)
#   bash alarme.sh desinstalar   remove o alarme, se for o desta skill
#
# Dois modos, decididos pelo projeto:
#   arquivo — sem core.hooksPath: o alarme é gravado em .git/hooks/pre-commit (como sempre foi);
#   hooks   — o projeto usa os hooks do sdd-open (core.hooksPath = sdd/hooks, com o dispatcher): o alarme
#             é ligado/desligado pela configuração `git config sdd.higieneDado on|off`; o dispatcher o chama
#             no fim de cada commit. Nada é gravado em .git/.
# Nunca mexe em alarme de outra origem (husky, lefthook, outro core.hooksPath, pre-commit escrito à mão).
# Saída: 0 = feito ou só informação; 2 = recusado (outro alarme); 1 = erro (fora de um repositório git).

set -u

MARCA="# sdd-higiene-dado: alarme de commit (pre-commit)"
MARCA_DISPATCHER="# sdd-open: dispatcher de hooks (pre-commit)"
AQUI="$(cd "$(dirname "$0")" && pwd)"
ORIGEM="${AQUI}/pre-commit.sh"

versao_skill() { grep -m1 '^  version:' "${AQUI}/../SKILL.md" 2>/dev/null | sed 's/.*: *//; s/"//g'; }
versao_de() { grep -m1 '^# versão:' "$1" 2>/dev/null | sed 's/^# versão: *//'; }

git rev-parse --show-toplevel >/dev/null 2>&1 || {
  echo "Esta pasta não é um repositório git. Abra o terminal na pasta do projeto e rode de novo."
  exit 1
}

ROOT="$(git rev-parse --show-toplevel)"
HOOKS_PATH="$(git config --get core.hooksPath 2>/dev/null || true)"
# O arquivo do alarme é sempre <git-common-dir>/hooks/pre-commit (vale para todas as worktrees). Não usar
# `git rev-parse --git-path hooks/pre-commit`: ele segue o core.hooksPath e, com o dispatcher do sdd-open
# ligado, apontaria para o próprio dispatcher — um `rm` apagaria os hooks do projeto.
COMMON="$(git rev-parse --git-common-dir 2>/dev/null)"
case "${COMMON}" in /*) ;; *) COMMON="${ROOT}/${COMMON}" ;; esac
HOOK="${COMMON}/hooks/pre-commit"
VERSAO="$(versao_skill)"

# Modo: arquivo (sem hooksPath) | hooks (sdd/hooks com o dispatcher) | outro (qualquer outro hooksPath)
# Relativo (sdd/hooks) ou absoluto que resolve para <raiz>/sdd/hooks (links simbólicos inclusos: /tmp no macOS).
hooks_path_e_nosso() {
  [ "${1}" = "sdd/hooks" ] && return 0
  case "${1}" in /*) [ -d "${1}" ] && [ "$(cd "${1}" 2>/dev/null && pwd -P)" = "$(cd "${ROOT}/sdd/hooks" 2>/dev/null && pwd -P)" ] ;; *) return 1 ;; esac
}
MODO="arquivo"
if [ -n "${HOOKS_PATH}" ]; then
  if hooks_path_e_nosso "${HOOKS_PATH}" \
     && [ -f "${ROOT}/sdd/hooks/pre-commit" ] && grep -qF "${MARCA_DISPATCHER}" "${ROOT}/sdd/hooks/pre-commit"; then
    MODO="hooks"
  else
    MODO="outro"
  fi
fi

# Estado: LIVRE (nada instalado) | NOSSO (alarme desta skill) | OUTRO (alarme de outra origem)
case "${MODO}" in
  outro)
    ESTADO="OUTRO"; DESCR="o projeto usa outro gerenciador de alarmes (core.hooksPath = ${HOOKS_PATH}, comum com husky)" ;;
  hooks)
    if [ "$(git config --get sdd.higieneDado 2>/dev/null || true)" = "on" ]; then
      ESTADO="NOSSO"; DESCR="o alarme desta skill está ligado pelos hooks do projeto (sdd/hooks), versão ${VERSAO} da skill"
    else
      ESTADO="LIVRE"; DESCR="o projeto usa os hooks do sdd-open (sdd/hooks) e o alarme desta skill está desligado neles"
    fi ;;
  arquivo)
    if [ -f "${HOOK}" ] && grep -qF "${MARCA}" "${HOOK}"; then
      ESTADO="NOSSO"; DESCR="o alarme desta skill já está instalado (versão $(versao_de "${HOOK}"))"
    elif [ -f "${HOOK}" ]; then
      ESTADO="OUTRO"; DESCR="já existe outro alarme de commit em ${HOOK}"
    else
      ESTADO="LIVRE"; DESCR="nenhum alarme de commit instalado"
    fi ;;
esac

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
    case "${MODO}:${ESTADO}" in
      hooks:LIVRE) echo "Dá para ligar: o alarme passa a rodar pelos hooks do projeto (sdd/hooks) a cada commit, sem gravar nada em .git/." ;;
      hooks:NOSSO) echo "Ligar de novo não muda nada. Para desligar: bash \"${AQUI}/alarme.sh\" desinstalar" ;;
      arquivo:LIVRE) echo "Dá para instalar: o alarme seria gravado em ${HOOK} e vale para todas as frentes deste projeto." ;;
      arquivo:NOSSO) echo "Instalar de novo atualiza para a versão ${VERSAO}. Para remover: bash \"${AQUI}/alarme.sh\" desinstalar" ;;
      *:OUTRO) como_acrescentar; exit 2 ;;
    esac
    ;;
  instalar)
    [ "${ESTADO}" = "OUTRO" ] && { echo "Recusado: ${DESCR}."; como_acrescentar; exit 2; }
    if [ "${MODO}" = "hooks" ]; then
      git config sdd.higieneDado on
      echo "Alarme ligado nos hooks do projeto (sdd/hooks), versão ${VERSAO} da skill; nada foi gravado em .git/."
      echo "Vale para todas as frentes deste projeto. Para pular um commit, depois de conferir: git commit --no-verify"
      echo "Para desligar: bash \"${AQUI}/alarme.sh\" desinstalar"
    else
      mkdir -p "$(dirname "${HOOK}")"
      # A cópia que o sync do sdd-open gera (.claude/skills, .cursor/skills) traz 2 linhas sdd-open:generated
      # depois do shebang: elas não vão para o hook, que não é arquivo gerado e não é reescrito pelo sync.
      corpo="$(grep -v -F 'sdd-open:generated' "${ORIGEM}")"
      { printf '%s\n' "${corpo}" | sed -n '1,2p'; echo "# versão: ${VERSAO}"; printf '%s\n' "${corpo}" | sed '1,2d'; } > "${HOOK}"
      chmod +x "${HOOK}"
      echo "Alarme instalado em ${HOOK} (versão ${VERSAO})."
      echo "Vale para todas as frentes deste projeto. Para pular um commit, depois de conferir: git commit --no-verify"
      echo "Para desinstalar: bash \"${AQUI}/alarme.sh\" desinstalar   (ou: rm \"${HOOK}\")"
    fi
    ;;
  desinstalar)
    case "${MODO}:${ESTADO}" in
      hooks:NOSSO)
        git config --unset sdd.higieneDado 2>/dev/null || true
        # Resto de uma migração: o arquivo antigo da higiene em .git/hooks fica inerte com o hooksPath ligado;
        # sai aqui, se ainda tiver a marca desta skill. O dispatcher (sdd/hooks/pre-commit) nunca é tocado.
        if [ -f "${HOOK}" ] && grep -qF "${MARCA}" "${HOOK}"; then rm -f "${HOOK}"; fi
        echo "Alarme desligado dos hooks do projeto (sdd/hooks). Os hooks do sdd-open continuam no lugar." ;;
      hooks:LIVRE) echo "Não há alarme desta skill ligado neste projeto. Nada foi alterado." ;;
      arquivo:NOSSO) rm -f "${HOOK}"; echo "Alarme removido de ${HOOK}." ;;
      arquivo:LIVRE) echo "Não há alarme desta skill instalado neste projeto. Nada foi alterado." ;;
      *:OUTRO) echo "Recusado: ${DESCR}, e ele não é desta skill. Nada foi alterado."; exit 2 ;;
    esac
    ;;
  *)
    echo "Uso: bash alarme.sh verificar | instalar | desinstalar"
    exit 1
    ;;
esac
exit 0
