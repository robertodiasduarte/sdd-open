#!/usr/bin/env bash
# contraste.sh — razão de contraste WCAG 2.x entre 2 cores, com veredito contra um piso.
#
# Uso:
#   bash sdd/bin/contraste.sh '<fg>' '<bg>' [alpha] [--piso N]
#   bash sdd/bin/contraste.sh --self-test
#
# Cor: #rgb ou #rrggbb, sempre entre aspas (sem aspas, o # começa um comentário no shell).
# Alpha (0 a 1): compõe o primeiro plano sobre o fundo, em sRGB, antes de linearizar, como o navegador.
# Piso: 4.5 por padrão; texto grande, borda e ícone usam --piso 3. Até 2 casas, maior que zero.
#
# O resultado é truncado de propósito: calculadoras costumam arredondar, e 4,496 arredondado apareceria
# como 4.50 e passaria.
#
# Exit: 0 PASSA · 2 REPROVA (ou self-test falhou) · 64 uso
# Compatível com bash 3.2 e awk POSIX.
export LC_ALL=C
set -u

ME="$(cd "$(dirname "$0")" && pwd -P)/$(basename "$0")"
COR='^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$'
ALFA='^(0(\.[0-9]*)?|\.[0-9]+|1(\.0*)?)$'
PISO='^([0-9]+(\.[0-9]{1,2})?|\.[0-9]{1,2})$'

erro_uso() {
  printf '🛑 %s\n' "$1" >&2
  printf 'RESULTADO: ERRO DE USO\n' >&2
  printf '→ %s\n' "$2" >&2
  exit 64
}

EXEMPLO="bash sdd/bin/contraste.sh '#767676' '#ffffff'"

ajuda() {
  cat <<'FIM'
contraste.sh — razão de contraste WCAG entre 2 cores, com veredito.

  bash sdd/bin/contraste.sh '#767676' '#ffffff'            texto comum (piso 4.5:1)
  bash sdd/bin/contraste.sh '#767676' '#ffffff' --piso 3   texto grande, borda, ícone
  bash sdd/bin/contraste.sh '#000000' '#ffffff' .5         primeiro plano com transparência

A cor vai entre aspas: sem aspas, o # começa um comentário no shell.
O resultado é truncado de propósito: calculadoras costumam arredondar, e 4,496
arredondado apareceria como 4.50 e passaria.

Saídas: 0 PASSA · 2 REPROVA · 64 uso.
FIM
}

medir() {  # fg bg alpha piso → "N.NN VEREDITO"
  awk -v fg="$1" -v bg="$2" -v a="$3" -v piso="$4" '
    function hx(s, c,  i) {
      s = tolower(s); sub(/^#/, "", s)
      if (length(s) == 3) s = substr(s,1,1) substr(s,1,1) substr(s,2,1) substr(s,2,1) substr(s,3,1) substr(s,3,1)
      for (i = 0; i < 3; i++)
        c[i] = 16 * (index("0123456789abcdef", substr(s, 2*i+1, 1)) - 1) + index("0123456789abcdef", substr(s, 2*i+2, 1)) - 1
    }
    function lin(v) { v /= 255; return v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ^ 2.4 }
    BEGIN {
      alfa = a + 0
      hx(bg, b); hx(fg, f)
      for (i = 0; i < 3; i++) f[i] = alfa * f[i] + (1 - alfa) * b[i]
      L1 = 0.2126 * lin(f[0]) + 0.7152 * lin(f[1]) + 0.0722 * lin(f[2])
      L2 = 0.2126 * lin(b[0]) + 0.7152 * lin(b[1]) + 0.0722 * lin(b[2])
      if (L1 < L2) { t = L1; L1 = L2; L2 = t }
      # Centésimos inteiros: o 1e-9 só protege a imprecisão de ponto flutuante em casos exatos (21,00).
      c = int((L1 + 0.05) / (L2 + 0.05) * 100 + 1e-9)
      p = int(piso * 100 + 0.5)
      printf "%d.%02d %s\n", int(c / 100), c - int(c / 100) * 100, (c >= p ? "PASSA" : "REPROVA")
    }'
}

auto_teste() {
  local falhas=0 total=0

  caso() {  # exit esperado · 1ª linha esperada ("" = só o exit) · argumentos
    local quer_rc="$1" quer="$2" saida rc primeira
    shift 2
    total=$((total + 1))
    saida="$("$BASH" "$ME" "$@" 2>/dev/null)"; rc=$?
    primeira="${saida%%$'\n'*}"
    if [ "$rc" -ne "$quer_rc" ] || { [ -n "$quer" ] && [ "$primeira" != "$quer" ]; }; then
      printf '🛑 caso: %s → exit %s, "%s" (esperado: exit %s, "%s")\n' "$*" "$rc" "$primeira" "$quer_rc" "$quer" >&2
      falhas=$((falhas + 1))
    fi
  }

  # Oráculos calculados fora do script, em Python.
  caso 0 '21.00:1 PASSA (piso 4.5:1)'   '#000000' '#ffffff'
  caso 0 '4.54:1 PASSA (piso 4.5:1)'    '#767676' '#ffffff'
  caso 2 '4.47:1 REPROVA (piso 4.5:1)'  '#777777' '#ffffff'
  caso 2 '4.47:1 REPROVA (piso 4.5:1)'  '#777' '#FFF'
  caso 2 '4.49:1 REPROVA (piso 4.5:1)'  '#6c7b67' '#ffffff'
  caso 0 '4.50:1 PASSA (piso 4.5:1)'    '#71796f' '#ffffff'
  caso 2 '1.00:1 REPROVA (piso 4.5:1)'  '#fff' '#fff'
  caso 2 '3.97:1 REPROVA (piso 4.5:1)'  '#000' '#fff' .5
  caso 0 '21.00:1 PASSA (piso 4.5:1)'   '#000' '#fff' 1
  caso 2 '1.00:1 REPROVA (piso 4.5:1)'  '#000' '#fff' 0
  caso 0 '4.47:1 PASSA (piso 3:1)'      '#777777' '#ffffff' --piso 3
  caso 0 '4.47:1 PASSA (piso 3:1)'      --piso 3 '#777777' '#ffffff'
  caso 2 '4.47:1 REPROVA (piso 4.48:1)' '#777777' '#ffffff' --piso 4.48
  caso 2 '4.54:1 REPROVA (piso 4.55:1)' '#767676' '#ffffff' --piso 4.55
  caso 0 '4.54:1 PASSA (piso 4.08:1)'   '#767676' '#ffffff' --piso 4.08

  # Entradas inválidas: nunca há razão na saída padrão.
  caso 64 ''
  caso 64 '' '#zzz' '#fff'
  caso 64 '' '#12345' '#fff'
  caso 64 '' 'rgba(0,0,0,.5)' '#fff'
  caso 64 '' '#000'
  caso 64 '' '#000' '#fff' .5 .5
  caso 64 '' '#000' '#fff' 2
  caso 64 '' '#000' '#fff' --piso
  caso 64 '' '#000' '#fff' --piso 0
  caso 64 '' '#000' '#fff' --piso 0.00
  caso 64 '' '#000' '#fff' --piso 4.555
  caso 64 '' '#000' '#fff' --piso abc
  caso 64 '' '#000' '#fff' --nada

  if [ "$falhas" -ne 0 ]; then
    printf 'RESULTADO: VERMELHO\n' >&2
    printf '→ %s de %s caso(s) falharam: corrija o script; nunca o oráculo\n' "$falhas" "$total" >&2
    return 2
  fi
  printf '✅ %s casos conferidos\n' "$total"
  printf 'RESULTADO: VERDE\n'
  printf '→ o contraste.sh está pronto para uso\n'
  return 0
}

[ "$#" -gt 0 ] || erro_uso "faltam as 2 cores. Sem aspas, o # começa um comentário no shell, e as cores não chegam ao comando." "$EXEMPLO"

n=0; fg=""; bg=""; alfa="1"; piso="4.5"
while [ "$#" -gt 0 ]; do
  case "$1" in
    --self-test)
      [ "$n" -eq 0 ] && [ "$#" -eq 1 ] || erro_uso "--self-test não aceita outros valores" "bash sdd/bin/contraste.sh --self-test"
      auto_teste; exit $?
      ;;
    -h|--help)
      ajuda; exit 0
      ;;
    --piso)
      [ "$#" -ge 2 ] || erro_uso "--piso sem valor" "use, por exemplo, --piso 3"
      piso="$2"; shift 2
      ;;
    -*)
      erro_uso "opção desconhecida: $1" "$EXEMPLO"
      ;;
    *)
      n=$((n + 1))
      case "$n" in
        1) fg="$1" ;;
        2) bg="$1" ;;
        3) alfa="$1" ;;
        *) erro_uso "valores demais: são 2 cores e, se houver, 1 transparência" "$EXEMPLO" ;;
      esac
      shift
      ;;
  esac
done

[ "$n" -ge 2 ] || erro_uso "faltam cores: são 2, o primeiro plano e o fundo, cada uma entre aspas" "$EXEMPLO"

for cor in "$fg" "$bg"; do
  if ! [[ "$cor" =~ $COR ]]; then
    case "$cor" in
      rgb*) erro_uso "cor não reconhecida: $cor. Aceito #rgb ou #rrggbb." "a transparência vai como 3º valor: bash sdd/bin/contraste.sh '#000000' '#ffffff' .5" ;;
      *)    erro_uso "cor não reconhecida: $cor. Aceito #rgb ou #rrggbb." "$EXEMPLO" ;;
    esac
  fi
done
[[ "$alfa" =~ $ALFA ]] || erro_uso "transparência fora de 0 a 1: $alfa" "use um valor como .5 ou 0.5"
[[ "$piso" =~ $PISO ]] || erro_uso "piso inválido: $piso. Aceito número com até 2 casas." "use, por exemplo, --piso 3"
case "$piso" in
  *[1-9]*) ;;
  *) erro_uso "piso inválido: $piso. Precisa ser maior que zero." "use, por exemplo, --piso 3" ;;
esac

resultado="$(medir "$fg" "$bg" "$alfa" "$piso")"
razao="${resultado%% *}"
veredito="${resultado##* }"

printf '%s:1 %s (piso %s:1)\n' "$razao" "$veredito" "$piso"
printf 'RESULTADO: %s\n' "$veredito"
if [ "$veredito" = "PASSA" ]; then
  printf '→ anote o par e o número na tabela da UX review\n'
  exit 0
fi
printf '→ afaste as 2 cores até %s:1; texto grande, borda e ícone usam --piso 3\n' "$piso"
exit 2
