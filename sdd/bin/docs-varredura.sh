#!/usr/bin/env bash
# docs-varredura.sh — confere documentos (ou uma pasta, como o bruto antes do anexo) antes de ficarem públicos:
# segredo, e-mail de pessoa, certificado, CPF/CNPJ válido, evidência grande demais. Nunca imprime o trecho achado.
# As regras e o uso estão em docs-varredura.py, ao lado; este arquivo só acha o Python e o chama.
#
# USO-INICIO
#   docs-varredura.sh [RAIZ]                documentos do repositório (sob sdd/, fora do pacote pelo export-ignore)
#   docs-varredura.sh --ref REF [RAIZ]      os documentos de um commit ou tag
#   docs-varredura.sh --pasta DIR           todo arquivo da pasta
#   ... --padrao REGEX                      só esta regra, em todos os arquivos: reprova enquanto achar REGEX
#   ... --texto TEXTO                       igual, com o TEXTO letra a letra (o dado pedido como veio, sem regex)
#       0 VERDE · 1 VERMELHO · 2 NÃO CONFERIDO (sem gitleaks) · 64 uso
#   Dispensa de um CPF/CNPJ: "docs-varredura: aceito — <motivo>" na linha dele ou na de cima.
# USO-FIM
#
# ⚠️ bash 3.2 (o /bin/bash do macOS) · Python 3.9 stdlib.

set -u
# F16: o Python que roda vira python3 (no Windows, python ou py -3). Só builtins (o PATH pode não ter dirname); sem
# a biblioteca (projeto sincronizado antes dela, ou script copiado sozinho), vale a guarda de antes.
_sdd_0="${0//\\//}"   # caminho do Windows (C:\…\x.sh) vira C:/…/x.sh
if [ "${_sdd_0%/*}" = "${_sdd_0}" ]; then _sdd_bin=.; else _sdd_bin="${_sdd_0%/*}"; fi
if [ -f "${_sdd_bin}/lib/python.sh" ]; then . "${_sdd_bin}/lib/python.sh"
else sdd_python_pronto() { command -v python3 >/dev/null 2>&1; }; sdd_python_exigir() { :; }
  export PYTHONIOENCODING="${PYTHONIOENCODING:-utf-8}"; fi   # F16W2: sem a biblioteca, ao menos o UTF-8

case "${1:-}" in
  -h|--help)
    sed -n '/^# USO-INICIO$/,/^# USO-FIM$/p' "$0" | sed '1d;$d;s/^# \{0,1\}//'
    exit 0 ;;
esac

if ! sdd_python_pronto; then
  echo "🛑 docs-varredura: python3 não encontrado no PATH." >&2
  printf 'RESULTADO: PAROU\n→ instale o Python 3 (3.9 ou mais novo) e rode de novo; nada foi lido.\n' >&2
  exit 64
fi
if [ ! -f "${_sdd_bin}/docs-varredura.py" ]; then
  echo "🛑 docs-varredura: não achei docs-varredura.py ao lado deste script." >&2
  printf 'RESULTADO: PAROU\n→ rode o init do sdd-open de novo: ele completa o que falta em sdd/bin/.\n' >&2
  exit 64
fi
exec python3 -B "${_sdd_bin}/docs-varredura.py" "$@"
