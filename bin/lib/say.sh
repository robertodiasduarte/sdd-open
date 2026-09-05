#!/usr/bin/env bash
# say.sh — vocabulário de saída do SDD Open.
#
# Regra única: todo símbolo vem acompanhado de PALAVRA. Ninguém depende de cor nem de
# emoji isolado para entender o que aconteceu (leitores de tela, pipes, terminais sem cor).
# Convenções completas: docs/cli-conventions.md
#
# ⚠️ bash 3.2: sem declare -A, sem ${var,,}. Expansão colada em não-ASCII usa ${VAR}.

# NO_COLOR é convenção POSIX: se definida (mesmo vazia), nada de cor.
if [ -n "${NO_COLOR+definida}" ] || [ ! -t 1 ]; then
  _C_DIM=""; _C_OFF=""
else
  _C_DIM=$(printf '\033[2m'); _C_OFF=$(printf '\033[0m')
fi

# Ação em curso.
say() { printf '▶ %s\n' "${1}"; }

# Sucesso de um passo.
ok() { printf '✅ %s\n' "${1}"; }

# Atenção que NÃO bloqueia.
warn() { printf '⚠️  %s\n' "${1}" >&2; }

# Detalhe só com --verbose.
detalhe() { [ "${VERBOSE:-0}" = "1" ] && printf '%s   %s%s\n' "${_C_DIM}" "${1}" "${_C_OFF}"; return 0; }

# Bloqueio: causa na 1ª linha, conserto na 2ª, sempre.
# Uso: die "<causa>" "<o que fazer>" [exit_code]
# Contrato do AT-011: todo estado que não é sucesso termina em `RESULTADO: <PALAVRA>` + `→`.
die() {
  printf '🛑 %s\n' "${1}" >&2
  printf 'RESULTADO: ERRO\n' >&2
  if [ $# -gt 1 ] && [ -n "${2}" ]; then
    printf '→ %s\n' "${2}" >&2
  fi
  exit "${3:-1}"
}

# Veredito final de um comando: PALAVRA + o que fazer agora.
# É o que impede um estado ambíguo de parecer sucesso.
resultado() { # $1=PALAVRA  $2=ação
  printf 'RESULTADO: %s\n' "${1}"
  printf '→ %s\n' "${2}"
}
