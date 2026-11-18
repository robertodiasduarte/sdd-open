#!/usr/bin/env bash
# anexar-bruto.sh — anexa a evidência bruta de uma frente (transcrições de modelo, gabaritos copiados, logs de série)
# à Release da versão que ela prova, como evidencia-bruta-<FEATURE>.tar.gz, depois de a varredura dos documentos sair
# limpa sobre ela. O bruto não vai para o git (sdd/reports/evidence/*/bruto/ está no .gitignore): ele é grande e o que
# um lint ou uma pessoa lê já está nos documentos. O anexo é público e permanente; por isso a varredura vem antes.
#
# USO-INICIO
#   anexar-bruto.sh FEATURE TAG          na raiz do projeto, depois de a Release da TAG existir
#       0 anexado e conferido pela lista do arquivo baixado, ou "sem bruto" (a pasta não existe ou está vazia)
#       1 nada anexado: a Release da TAG não existe, a varredura não saiu limpa, o envio falhou ou o anexo baixado
#         não tem os mesmos arquivos da pasta (o motivo em 1 linha)
#       64 uso (argumentos, fora de um repositório git)
#   SDD_ANEXAR_GH: o programa gh a usar (padrão: gh), para os testes.
# USO-FIM
#
# ⚠️ bash 3.2 (o /bin/bash do macOS) · tar, gh e o Python da varredura (a lista dos arquivos).

set -u -o pipefail

case "${1:-}" in
  -h|--help)
    sed -n '/^# USO-INICIO$/,/^# USO-FIM$/p' "$0" | sed '1d;$d;s/^# \{0,1\}//'
    exit 0 ;;
esac

F="${1:-}"; TAG="${2:-}"
if [ -z "$F" ] || [ -z "$TAG" ] || [ $# -ne 2 ]; then
  echo "🛑 anexar-bruto: uso: anexar-bruto.sh FEATURE TAG" >&2
  exit 64
fi
case "$F" in *[!A-Za-z0-9_]*) echo "🛑 anexar-bruto: FEATURE só com letras, números e _: $F" >&2; exit 64 ;; esac
raiz="$(git rev-parse --show-toplevel 2>/dev/null)" || { echo "🛑 anexar-bruto: rode dentro do repositório." >&2; exit 64; }
GH="${SDD_ANEXAR_GH:-gh}"
# F16: o mesmo Python da varredura (no Windows, python ou py -3), que a lista dos arquivos usa
[ -f "$raiz/sdd/bin/lib/python.sh" ] && . "$raiz/sdd/bin/lib/python.sh"
# A lista de uma pasta: caminhos relativos em NFC, ordenados. O tar do macOS grava o nome decomposto ("a" + til) e a
# pasta pode ter o composto ("ã"): sem normalizar, o anexo certo sairia ANEXO DIFERENTE (revisão do código, R7).
listar() {
  python3 - "$1" <<'FIM_LISTAR'
import os, sys, unicodedata
r = sys.argv[1]
nomes = [unicodedata.normalize("NFC", os.path.relpath(os.path.join(d, f), r).replace(os.sep, "/"))
         for d, _, fs in os.walk(r) for f in fs]
sys.stdout.write("".join(n + "\n" for n in sorted(nomes)))
FIM_LISTAR
}
pasta="$raiz/sdd/reports/evidence/$F/bruto"
nome="evidencia-bruta-$F.tar.gz"

if [ ! -d "$pasta" ] || [ -z "$(find "$pasta" -type f 2>/dev/null | head -1)" ]; then
  echo "➖ bruto: $F não tem sdd/reports/evidence/$F/bruto/ com arquivos; nada a anexar."
  echo "RESULTADO: SEM BRUTO"
  exit 0
fi
# só arquivo e pasta: um link entraria no .tar.gz como link (apontando para fora da pasta) e a conferência não o veria
if [ -n "$(find "$pasta" ! -type f ! -type d 2>/dev/null | head -1)" ]; then
  echo "🔴 bruto: a pasta tem link ou arquivo especial; nada foi anexado. Troque cada link pelo arquivo (cp -L) e rode de novo."
  echo "RESULTADO: NADA ANEXADO"
  exit 1
fi
if ! "$GH" release view "$TAG" >/dev/null 2>&1; then
  echo "🔴 bruto: a Release $TAG não existe (ou o gh não está logado); nada foi anexado, o bruto fica na pasta."
  echo "RESULTADO: NADA ANEXADO"
  exit 1
fi
if ! bash "$raiz/sdd/bin/docs-varredura.sh" --pasta "$pasta" >/dev/null 2>&1; then
  echo "🔴 bruto: a varredura dos documentos não saiu limpa sobre o bruto; nada foi anexado. Veja: bash sdd/bin/docs-varredura.sh --pasta sdd/reports/evidence/$F/bruto"
  echo "RESULTADO: NADA ANEXADO"
  exit 1
fi

tmp="$(mktemp -d 2>/dev/null || mktemp -d -t bruto)" || exit 1
trap 'rm -rf "$tmp"' EXIT
mkdir "$tmp/baixado" "$tmp/extraido"
listar "$pasta" > "$tmp/pasta.txt" || { echo "🔴 bruto: não consegui listar a pasta; nada foi anexado."; echo "RESULTADO: NADA ANEXADO"; exit 1; }
# COPYFILE_DISABLE: o tar do macOS poria no anexo um "._<arquivo>" de atributos para cada arquivo (medido no Build)
if ! COPYFILE_DISABLE=1 tar -czf "$tmp/$nome" -C "$pasta" .; then
  echo "🔴 bruto: não consegui juntar o bruto num .tar.gz; nada foi anexado."
  echo "RESULTADO: NADA ANEXADO"
  exit 1
fi
if ! "$GH" release upload "$TAG" "$tmp/$nome" --clobber >/dev/null 2>&1; then
  echo "🔴 bruto: o envio do anexo à Release $TAG falhou; rode de novo (o --clobber troca um anexo pela metade)."
  echo "RESULTADO: NADA ANEXADO"
  exit 1
fi
# a prova é o que foi publicado, não o exit do envio: baixa de volta, extrai e lista do mesmo jeito que a pasta
if ! "$GH" release download "$TAG" --pattern "$nome" --dir "$tmp/baixado" --clobber >/dev/null 2>&1 \
   || ! tar -xzf "$tmp/baixado/$nome" -C "$tmp/extraido" \
   || ! listar "$tmp/extraido" > "$tmp/anexo.txt"; then
  echo "🔴 bruto: enviei, mas não consegui baixar o anexo de volta para conferir; confira a página da Release $TAG."
  echo "RESULTADO: NÃO CONFERIDO"
  exit 1
fi
# a lista e os bytes: um anexo velho com os mesmos nomes (o --clobber que não trocou, um cache) não passa
if ! cmp -s "$tmp/pasta.txt" "$tmp/anexo.txt" || ! cmp -s "$tmp/$nome" "$tmp/baixado/$nome"; then
  echo "🔴 bruto: o anexo da Release $TAG não tem os mesmos arquivos da pasta; rode de novo."
  echo "RESULTADO: ANEXO DIFERENTE"
  exit 1
fi
echo "✅ bruto: $nome anexado à Release $TAG ($(wc -l < "$tmp/pasta.txt" | tr -d ' ') arquivo(s), conferido pelo anexo baixado: a lista e os bytes)."
echo "RESULTADO: ANEXADO"
exit 0
