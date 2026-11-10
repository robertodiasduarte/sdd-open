#!/usr/bin/env bash
# ledger-revisao-lint.sh — confere o ledger da revisão de uma frente (sdd/reviews/LEDGER_REVISAO_{F}.md): a decisão
# de cada achado da revisão adversarial e a marca de dano. Molde: sdd/templates/LEDGER_REVISAO_TEMPLATE.md.
# Critério de dano: sdd/review/CRITERIO_DANO.md. Quem lê o ledger: sdd-fluxo.sh loop --ledger (as 4 primeiras
# células) e eval-revisores.sh (todas).
#
# Por que existe: sem a marca de dano em cada linha, o custo por falha real não se mede; e um "sim" sem o teste
# que prova a falha é opinião, não medida.
#
# USO-INICIO
#   ledger-revisao-lint.sh <LEDGER_REVISAO_F.md>…
#       o arquivo é só do ledger: toda linha de tabela é o cabeçalho abaixo ou uma linha de dados de 7 células
#       (outra tabela no arquivo reprova; texto corrido, bloco cercado e comentário podem ficar):
#         | achado | sev | veredito | rodada | evidência | dano | revisão |
#         achado    o id como está no arquivo de vereditos da rodada: R<n> ou N<n>, com @<engine> quando a
#                   rodada teve 2 revisores (R1, R1@claude, N1)
#         sev       HIGH | MED | LOW
#         veredito  APLICADA | REBATIDA_EVIDENCIA | REBATIDA_ESCOPO
#         rodada    rodada=<N> (N inteiro, com sufixo de lote opcional: 5 ou 5a)
#         evidência não vazia; com dano = sim, traz `teste: <nome>` (test_…, arquivo::teste ou tests/…)
#         dano      sim | nao | ? ("?" só em arquivo com a linha `retroativo: sim`, sozinha, fora de bloco cercado)
#         revisão   a pasta EXTERNAL_REVIEW_<AAAAMMDD-HHMMSS> da rodada (com -<n> se o nome colidiu)
#       rodada em que a revisão não achou nada: uma linha fora da tabela,
#         sem achados: rodada=<N> EXTERNAL_REVIEW_<AAAAMMDD-HHMMSS>
#       bloco cercado por ``` e comentário <!-- --> não são conferidos
#       0 ok · 2 violação (arquivo:linha — motivo) · 64 uso, arquivo ilegível, ou arquivo sem linha de dados
#       e sem linha `sem achados:` (nada conferido nunca é verde)
# USO-FIM
#
# ⚠️ bash 3.2 (o /bin/bash do macOS) · núcleo em Python 3.9 stdlib.

set -u

case "${1:-}" in
  -h|--help)
    sed -n '/^# USO-INICIO$/,/^# USO-FIM$/p' "$0" | sed '1d;$d;s/^# \{0,1\}//'
    exit 0 ;;
esac

if ! command -v python3 >/dev/null 2>&1; then
  echo "🛑 ledger-revisao-lint: python3 não encontrado no PATH." >&2
  printf 'RESULTADO: ERRO DE USO\n→ instale o Python 3 (3.9 ou mais novo) e rode de novo.\n' >&2
  exit 64
fi

exec python3 -B - "$@" <<'PY'
import re, sys

SEV = ("HIGH", "MED", "LOW")
VEREDITOS = ("APLICADA", "REBATIDA_EVIDENCIA", "REBATIDA_ESCOPO")
DANO = ("sim", "nao", "?")
ACHADO_RE = re.compile(r"^[RN]\d+(@[A-Za-z0-9][A-Za-z0-9._:/-]*)?$")
RODADA_RE = re.compile(r"^rodada=\d+[a-z]?$")
PASTA = r"EXTERNAL_REVIEW_\d{8}-\d{6}(?:-\d+)?"
PASTA_RE = re.compile("^" + PASTA + "$")
SEM_ACHADOS_RE = re.compile(r"^\s*sem achados:\s*(rodada=\d+[a-z]?)\s+(" + PASTA + r")\s*$")
SEM_ACHADOS_QUASE = re.compile(r"^\s*[-*>]*\s*\**sem achados\b", re.I)
RETRO_RE = re.compile(r"^retroativo: sim$")
RETRO_QUASE = re.compile(r"^\s*[-*>]*\s*\**retroativo\**\s*:\**\s*sim\b", re.I)
TESTE_RE = re.compile(r"(?i)\bteste:\s*`?(?:[\w./-]+::[\w.:-]+|(?:[\w]+\.)*test_\w+(?:\.py)?(?:::[\w.:-]+)?|tests/[\w./-]+)")
SEPARADOR_RE = re.compile(r"^:?-+:?$")
CABECALHO = ["achado", "sev", "veredito", "rodada", "evidência", "dano", "revisão"]
CERCA_RE = re.compile(r"^ {0,3}(```|~~~)[\w+.-]*\s*$")   # a linha inteira é a cerca; código em linha não conta
SOLTA_RE = re.compile(r"^[\s>*\\\u200b\ufeff-]*")


def linhas_uteis(texto):
    """As linhas (n, texto) fora de bloco cercado e de comentário <!-- -->, e os avisos (n, motivo) de bloco que
    abriu e não fechou. A mesma função está no ledger-revisao-lint.sh e no eval-revisores.sh: os dois leem o ledger
    do mesmo jeito."""
    uteis, avisos, cercado, comentario, onde = [], [], False, False, 0
    for n, ln in enumerate(texto.lstrip("\ufeff").split("\n"), 1):
        ln = ln.rstrip("\r")
        if comentario:
            comentario = "-->" not in ln
            continue
        if CERCA_RE.match(ln):
            cercado, onde = not cercado, n
            continue
        if cercado:
            continue
        if ln.lstrip().startswith("<!--"):
            comentario, onde = "-->" not in ln, n
            continue
        uteis.append((n, ln))
    if cercado:
        avisos.append((onde, "bloco cercado aberto e não fechado: o resto do arquivo não foi lido"))
    if comentario:
        avisos.append((onde, "comentário <!-- aberto e não fechado: o resto do arquivo não foi lido"))
    return uteis, avisos


def linha_solta(ln):
    """Uma linha que não começa por `|` mas tem forma de linha do ledger: a barra inicial atrás de citação, item de
    lista ou barra invertida, ou 4 ou mais barras verticais. Ela não é lida como tabela; por isso é acusada."""
    resto = SOLTA_RE.sub("", ln, count=1)
    return resto.startswith("|") or len(re.findall(r"(?<!\\)\|", ln)) >= 4


def uso(motivo):
    print("🛑 ledger-revisao-lint: " + motivo, file=sys.stderr)
    print("RESULTADO: ERRO DE USO\n→ rode `ledger-revisao-lint.sh --help` para ver o uso.", file=sys.stderr)
    sys.exit(64)


def celulas(ln):
    c = [x.strip() for x in re.split(r"(?<!\\)\|", ln)][1:]
    if c and c[-1] == "":
        c = c[:-1]
    return c


args = sys.argv[1:]
if not args:
    uso("faltou o arquivo do ledger")
for a in args:
    if a.startswith("-"):
        uso("opção desconhecida: " + a)
textos = []
for arq in args:   # todos os caminhos são lidos antes: um arquivo ilegível não esconde as violações dos outros
    try:
        with open(arq, encoding="utf-8") as h:
            textos.append((arq, h.read()))
    except (OSError, UnicodeDecodeError):
        uso("não consegui ler %s" % arq)

for s in (sys.stdout, sys.stderr):   # a saída tem acento: nunca depende do locale de quem roda
    try:
        s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

violacoes, total, limpas, vistos, vazios, pastas_limpas = [], 0, 0, {}, [], {}
for arq, texto in textos:   # as rodadas ditas sem achados valem entre os arquivos passados juntos
    for n, ln in linhas_uteis(texto)[0]:
        m = SEM_ACHADOS_RE.match(ln)
        if m:
            pastas_limpas.setdefault(m.group(2), "%s:%d" % (arq, n))
for arq, texto in textos:
    retroativo = False
    uteis, abertos = linhas_uteis(texto)
    for n, motivo in abertos:
        violacoes.append("%s:%d — %s" % (arq, n, motivo))
    for n, ln in uteis:
        if RETRO_RE.match(ln):
            retroativo = True
        elif RETRO_QUASE.match(ln):
            violacoes.append("%s:%d — a marca de retroativo é a linha `retroativo: sim`, sozinha, sem negrito, "
                             "citação ou maiúscula" % (arq, n))
    dados, sem_achados, cabecalho_ruim = 0, 0, False
    for n, ln in uteis:
        if not re.match(r"^\s*\|", ln):
            m = SEM_ACHADOS_RE.match(ln)
            if m:
                sem_achados += 1
            elif SEM_ACHADOS_QUASE.match(ln):
                violacoes.append("%s:%d — rodada sem achados se escreve `sem achados: rodada=<N> "
                                 "EXTERNAL_REVIEW_<AAAAMMDD-HHMMSS>`" % (arq, n))
            elif linha_solta(ln):
                dados += 1
                violacoes.append("%s:%d — linha com forma de linha do ledger fora da tabela: toda linha do ledger "
                                 "começa por `|` (sem citação, item de lista nem barra invertida antes)" % (arq, n))
            continue
        c = celulas(ln)
        if not c or all(SEPARADOR_RE.match(x) for x in c):
            continue
        # O arquivo é só do ledger: toda linha de tabela é o cabeçalho do molde ou uma linha de dados. Não há
        # "outra tabela" a pular: uma regra que adivinhava qual tabela era o ledger deixou linha sem conferir.
        nomes = [x.strip("*` ").lower() for x in c]
        if nomes == CABECALHO:
            cabecalho_ruim = False
            continue
        if nomes[0] == "achado" or nomes[0].startswith("achado "):
            cabecalho_ruim = True
            violacoes.append("%s:%d — o cabeçalho não é o do molde: `| achado | sev | veredito | rodada | "
                             "evidência | dano | revisão |`" % (arq, n))
            continue
        dados += 1
        if cabecalho_ruim:
            continue   # com o cabeçalho fora do molde as colunas não se sabem: uma mensagem só, a do cabeçalho

        def acusa(motivo):
            violacoes.append("%s:%d — %s" % (arq, n, motivo))

        if len(c) < 7:
            acusa("a linha tem %d célula(s), o ledger da revisão tem 7: falta a célula `dano` (e a pasta da revisão); "
                  "este arquivo só tem a tabela do ledger" % len(c))
            continue
        if len(c) > 7:
            acusa("a linha tem %d células, o ledger da revisão tem 7: escape `|` dentro de célula com `\\|`" % len(c))
            continue
        achado, sev, veredito, rodada, evidencia, dano, pasta = c
        if not ACHADO_RE.match(achado):
            acusa("achado `%s` fora do formato R<n> ou N<n>, com @<engine> opcional: copie o id do arquivo de "
                  "vereditos" % achado)
        if sev not in SEV:
            acusa("severidade `%s` fora de HIGH, MED, LOW" % sev)
        if veredito not in VEREDITOS:
            acusa("veredito `%s` fora de APLICADA, REBATIDA_EVIDENCIA, REBATIDA_ESCOPO" % veredito)
        if not RODADA_RE.match(rodada):
            acusa("rodada `%s` fora do formato rodada=<N>" % rodada)
        if not evidencia or evidencia in ("—", "-"):
            acusa("evidência vazia")
        if not PASTA_RE.match(pasta):
            acusa("revisão `%s` não é uma pasta EXTERNAL_REVIEW_<AAAAMMDD-HHMMSS>" % pasta)
        if dano not in DANO:
            acusa("dano `%s` fora de sim, nao, ?" % dano)
        elif dano == "sim":
            if veredito != "APLICADA":
                acusa("dano = sim com veredito %s: só achado APLICADA pode ser falha com dano" % veredito)
            elif not TESTE_RE.search(evidencia):
                acusa("dano = sim sem `teste: <nome>` na evidência: cite o teste que falha no código antigo "
                      "(test_…, arquivo::teste ou tests/…)")
        elif dano == "?" and not retroativo:
            acusa("dano = ? num ledger que não é retroativo: marque sim ou nao (ou declare `retroativo: sim`)")
        if pasta in pastas_limpas:
            acusa("a revisão %s está marcada `sem achados` em %s e tem achado nesta linha" % (pasta, pastas_limpas[pasta]))
        chave = (pasta, achado)
        if chave in vistos:
            acusa("achado %s repetido na revisão %s (1ª vez em %s)" % (achado, pasta, vistos[chave]))
        else:
            vistos[chave] = "%s:%d" % (arq, n)
    if not dados and not sem_achados:
        vazios.append(arq)
    total += dados
    limpas += sem_achados

# as violações saem sempre, mesmo quando outro arquivo não tem nada a conferir
if violacoes or vazios:
    for v in violacoes:
        print("🛑 " + v, file=sys.stderr)
    for arq in vazios:
        print("🛑 %s — nenhuma linha de dados nem linha `sem achados:`: nada conferido nunca é verde" % arq,
              file=sys.stderr)
if vazios and not violacoes:
    print("RESULTADO: ERRO DE USO\n→ grave as linhas do ledger pelo molde (sdd/templates/LEDGER_REVISAO_TEMPLATE.md) "
          "e rode de novo.", file=sys.stderr)
    sys.exit(64)
if violacoes:
    print("RESULTADO: VERMELHO\n→ corrija as linhas acima (molde: sdd/templates/LEDGER_REVISAO_TEMPLATE.md; "
          "critério: sdd/review/CRITERIO_DANO.md) e rode de novo.", file=sys.stderr)
    sys.exit(2)
print("✅ ledger da revisão: %d linha(s) e %d rodada(s) sem achados em %d arquivo(s), cada linha com veredito, dano "
      "e a pasta da revisão." % (total, limpas, len(args)))
print("RESULTADO: VERDE\n→ passe o arquivo ao `sdd-fluxo.sh loop --ledger` e ao `eval-revisores.sh`.")
PY
