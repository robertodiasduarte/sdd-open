#!/usr/bin/env bash
# sdd-higiene-dado: alarme de commit (pre-commit)
# Instalado pela skill sdd-higiene-dado (SDD Open by RDD) com o OK de quem usa este computador.
#
# Recusa o commit quando o que está indo para o git contém:
#   - CPF ou CNPJ com dígito verificador válido (com ou sem pontuação), nas linhas adicionadas;
#   - arquivo de senhas (.env, .env.*; exceto .env.example e .env.sample);
#   - certificado com chave privada (.pfx, .p12, ou .pem que contém PRIVATE KEY);
#   - planilha nova (.xlsx, .xls, .ods, .csv), de qualquer tamanho.
#
# Para pular só um commit, depois de conferir: git commit --no-verify
# Para remover este alarme: apague este arquivo (o caminho aparece na mensagem de recusa).
#
# Só lê o que está no stage; não altera nada. Requer bash, git e awk (macOS, Linux, Git Bash).

set -u

ACHADOS=""
NOMES=$'\n'
achado() { ACHADOS="${ACHADOS}  $1"$'\n'; }

# ── 1. pelo nome do arquivo ──────────────────────────────────────────────────
# --no-renames: arquivo renomeado aparece como novo (A), então é conferido de novo.
while IFS= read -r -d '' status && IFS= read -r -d '' arq; do
  base="$(basename "${arq}" | tr '[:upper:]' '[:lower:]')"
  motivo=""
  case "${base}" in
    .env.example|.env.sample) ;;
    .env|.env.*) motivo="arquivo de senhas (.env)" ;;
    *.pfx|*.p12) motivo="certificado digital com chave privada (ex.: certificado A1)" ;;
    *.pem) git show ":${arq}" 2>/dev/null | grep -q "PRIVATE KEY" && motivo="chave privada (.pem com PRIVATE KEY)" ;;
    *.xlsx|*.xls|*.ods|*.csv) [ "${status}" = "A" ] && motivo="planilha nova (pode conter dado de cliente)" ;;
  esac
  if [ -n "${motivo}" ]; then
    achado "${arq}: ${motivo}"
    NOMES="${NOMES}${arq}"$'\n'
  fi
done < <(git diff --cached --name-status -z --no-renames --diff-filter=ACM)

# ── 2. CPF/CNPJ nas linhas adicionadas ───────────────────────────────────────
# Só arquivos de texto (o git marca binário como "Binary files differ" e não mostra linhas).
# Pesos do dígito verificador calculados por fórmula, não escritos como sequência de dígitos.
# LC_ALL=C: CSV exportado do Excel no Windows vem em Latin-1; num terminal UTF-8 o awk
# pararia no primeiro acento e o CPF desse arquivo passaria sem alarme.
CONTEUDO="$(git -c core.quotePath=false diff --cached -U0 --no-color --no-renames --no-ext-diff --diff-filter=ACM 2>/dev/null \
| HD_NOMES="${NOMES}" LC_ALL=C awk '
function repetido(s,   i) { for (i = 2; i <= length(s); i++) if (substr(s, i, 1) != substr(s, 1, 1)) return 0; return 1 }
function cpf_ok(s,   i, t, r) {
  if (repetido(s)) return 0
  t = 0; for (i = 1; i <= 9; i++) t += substr(s, i, 1) * (11 - i)
  r = (t * 10) % 11; if (r == 10) r = 0; if (r != substr(s, 10, 1) + 0) return 0
  t = 0; for (i = 1; i <= 10; i++) t += substr(s, i, 1) * (12 - i)
  r = (t * 10) % 11; if (r == 10) r = 0; return r == substr(s, 11, 1) + 0
}
function cnpj_ok(s,   i, t, r, w) {
  if (repetido(s)) return 0
  t = 0; for (i = 1; i <= 12; i++) { w = (i <= 4) ? 6 - i : 14 - i; t += substr(s, i, 1) * w }
  r = t % 11; r = (r < 2) ? 0 : 11 - r; if (r != substr(s, 13, 1) + 0) return 0
  t = 0; for (i = 1; i <= 13; i++) { w = (i <= 5) ? 7 - i : 15 - i; t += substr(s, i, 1) * w }
  r = t % 11; r = (r < 2) ? 0 : 11 - r; return r == substr(s, 14, 1) + 0
}
BEGIN {
  D2 = "[0-9][0-9]"; D3 = "[0-9][0-9][0-9]"; D4 = "[0-9][0-9][0-9][0-9]"
  CPF_M = "^" D3 "\\." D3 "\\." D3 "-" D2 "$"
  CNPJ_M = "^" D2 "\\." D3 "\\." D3 "/" D4 "-" D2 "$"
  n = split(ENVIRON["HD_NOMES"], l, "\n"); for (i = 1; i <= n; i++) if (l[i] != "") pular[l[i]] = 1
}
# Cabeçalho de arquivo só entre "diff --git" e o primeiro "@@": uma linha de conteúdo que
# comece com "++ " não é confundida com o nome do arquivo.
/^diff --git / { cab = 1; next }
cab && /^\+\+\+ / { arq = substr($0, 5); sub(/^b\//, "", arq); next }
/^@@ / { cab = 0; split($3, h, ","); linha = substr(h[1], 2) + 0; next }
cab { next }
/^\+/ {
  if (!(arq in pular)) {
    n = split(substr($0, 2), tok, /[^0-9A-Za-z.\/_-]+/)
    for (i = 1; i <= n; i++) {
      t = tok[i]; sub(/^[.\/-]+/, "", t); sub(/[.\/-]+$/, "", t)
      tipo = ""
      if (t ~ CPF_M || t ~ CNPJ_M) { d = t; gsub(/[^0-9]/, "", d) }
      else if (t ~ /^[0-9]+$/) d = t
      else continue
      if (length(d) == 11 && cpf_ok(d)) tipo = "CPF " substr(d, 1, 3) ".***.***-" substr(d, 10, 2)
      else if (length(d) == 14 && cnpj_ok(d)) tipo = "CNPJ " substr(d, 1, 2) ".***.***/****-" substr(d, 13, 2)
      if (tipo != "") {
        qtd[arq]++
        if (qtd[arq] <= 3) print arq ":" linha ": " tipo
        else if (qtd[arq] == 4) print arq ": (mais números no mesmo arquivo)"
      }
    }
  }
  linha++; next
}
')"
[ -n "${CONTEUDO}" ] && while IFS= read -r l; do achado "${l}"; done <<< "${CONTEUDO}"

[ -z "${ACHADOS}" ] && exit 0

# Como desinstalar depende de onde o alarme mora. Com core.hooksPath definido, ele roda pelo dispatcher do
# sdd-open (sdd/hooks) e sai por `alarme.sh desinstalar`; sem hooksPath, é o arquivo em <git-common-dir>/hooks.
# Nunca `git rev-parse --git-path hooks/pre-commit`: ele segue o core.hooksPath e o `rm` apagaria o dispatcher.
if [ -n "$(git config --get core.hooksPath 2>/dev/null || true)" ]; then
  DESINSTALAR='Para desinstalar o alarme: bash .agents/skills/sdd-higiene-dado/scripts/alarme.sh desinstalar'
else
  COMMON="$(git rev-parse --git-common-dir 2>/dev/null)"
  case "${COMMON}" in /*) ;; *) COMMON="$(git rev-parse --show-toplevel)/${COMMON}" ;; esac
  DESINSTALAR="Para desinstalar o alarme: rm \"${COMMON}/hooks/pre-commit\""
fi
{
  printf '\nsdd-higiene-dado: commit recusado. Encontrei o que não deveria ir para o git:\n\n'
  printf '%s\n' "${ACHADOS}"
  cat <<'TXT'
Por que importa: o que entra no git fica no histórico e vai junto em todo push.
Apagar depois não desfaz: quem já copiou o repositório continua com o dado.

Como corrigir:
  1. Tire o arquivo deste commit:      git restore --staged "<arquivo>"
  2. Se ele nunca deve ir para o git:  echo "<arquivo>" >> .gitignore
  3. Se o dado é necessário, use um fictício ou anonimizado.

Se você conferiu e o dado é fictício ou autorizado, grave mesmo assim:
  git commit --no-verify
Isso pula o alarme só neste commit. Agente de IA: não use --no-verify sem o OK
explícito da pessoa.

TXT
  printf '%s\n\n' "${DESINSTALAR}"
} >&2
exit 1
