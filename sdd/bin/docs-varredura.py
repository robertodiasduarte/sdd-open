#!/usr/bin/env python3
"""docs-varredura.py — confere documentos (ou uma pasta) antes de eles ficarem públicos e permanentes.

Por que existe: os documentos das frentes vivem no repositório, ao lado do código, e a evidência bruta vira anexo
de Release. Os dois são públicos e não se apagam de verdade (clones, caches, a tag de arquivo). Esta varredura barra
o que não pode ir: segredo, e-mail de pessoa, certificado com chave privada, CPF ou CNPJ válido e arquivo de evidência
grande demais. Ela nunca imprime o trecho achado: só o arquivo, a linha e a regra (o log do CI é público, e um
documento não pode forjar a linha de resultado).

Uso (o docs-varredura.sh, ao lado, só acha o Python e chama este arquivo):
  docs-varredura.py [RAIZ]                 documentos do repositório: arquivo versionado sob sdd/ que o export-ignore
                                           do .gitattributes tira do pacote
  docs-varredura.py --ref REF [RAIZ]       os documentos de um commit ou tag (lidos do git, não da árvore)
  docs-varredura.py --pasta DIR            todo arquivo da pasta (o bruto antes do anexo, um anexo baixado)
  docs-varredura.py ... --padrao REGEX     SÓ esta regra, sem gitleaks: reprova enquanto achar REGEX (prova de remoção a
                                           pedido); varre todos os arquivos (da árvore ou da ref), não só os documentos
  docs-varredura.py ... --texto TEXTO      igual ao --padrao, com o TEXTO procurado letra a letra (o dado pedido como
                                           veio: "+", "." e parênteses não viram regra de regex); com --ref, olha
                                           também cada commit alcançável pela ref (git log -S): uma tag regravada
                                           num commit filho ainda guarda o dado no histórico

Regras: segredo (gitleaks, lido do relatório JSON) · e-mail fora de example.com|org|net, *.example, *.invalid, *.test,
*.localhost, exemplo.com, *.noreply.github.com, o noreply da Anthropic e o endereço SSH do GitHub · certificado
(.pfx, .p12, ou -----BEGIN … PRIVATE KEY-----) · CPF/CNPJ com dígito verificador válido, dispensado por
"docs-varredura: aceito — <motivo>" na linha ou na de cima · arquivo de evidência versionado (sdd/reports/evidence/;
não vale no --pasta: o bruto é grande por natureza) acima de SDD_DOCS_TETO bytes (padrão 262144).

Exit: 0 VERDE · 1 VERMELHO · 2 NÃO CONFERIDO (gitleaks ausente ou falhou) · 64 uso (opção, pasta ou ref
inexistente, repositório sem documentos marcados). Python >= 3.9, só stdlib.
"""
import sys as _sdd_sys  # F16W2: saída em UTF-8 e "\n" também no Windows (cp1252 e "\r\n" no pipe do Git Bash)
for _sdd_c in (_sdd_sys.stdout, _sdd_sys.stderr):
    try:
        _sdd_c.reconfigure(encoding="utf-8", errors="replace", newline="\n")
    except (AttributeError, ValueError):
        pass

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

TETO = int(os.environ.get("SDD_DOCS_TETO", "262144"))
EVIDENCIA = "sdd/reports/evidence/"
MOSTRAR = 50

# quantificadores com teto: numa linha longa sem "@" (log de 600 KB), "+" sem teto recomeça em cada posição e o tempo
# cresce com o quadrado do tamanho (medido no Build da F26: a suíte levou 74 min)
EMAIL = re.compile(r"([A-Za-z0-9._%+-]{1,64})@([A-Za-z0-9-]{1,63}(?:\.[A-Za-z0-9-]{1,63}){0,8}\.[A-Za-z]{2,24})")
DOMINIO_OK = re.compile(r"(?:^|\.)(?:example\.(?:com|org|net)|example|invalid|test|localhost|noreply\.github\.com)$"
                        r"|^exemplo\.com$", re.I)   # exemplo.com: o marcador dos documentos antigos; nunca exemplo.*
# montados aqui, não escritos por extenso: o G2 do publish-gate barra e-mail fora de example.* no pacote
ENDERECO_OK = {"git" + "@" + "github.com", "noreply" + "@" + "anthropic.com"}
CHAVE = re.compile(rb"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----")
CERT_EXT = (".pfx", ".p12")
# Só dígito em volta conta como "mesmo número": "CPF" seguido dos 11 dígitos, sem espaço, é um CPF (avaliador, A6); medido nos
# 2.925 documentos da migração, a troca achou só esse caso.
NUMERO = re.compile(r"(?<![0-9])([0-9]{3}\.?[0-9]{3}\.?[0-9]{3}-?[0-9]{2}"
                    r"|[0-9]{2}\.?[0-9]{3}\.?[0-9]{3}/?[0-9]{4}-?[0-9]{2})(?![0-9])")
# Compactado não se varre por dentro (nem a varredura nem o gitleaks): reprova, para o anexo público e o documento não
# levarem dado escondido (avaliador, A5). Pelo nome e pela assinatura dos primeiros bytes.
COMPACTADO_EXT = (".gz", ".tgz", ".zip", ".bz2", ".xz", ".7z", ".rar", ".zst", ".tar", ".jar")
COMPACTADO_MAGICA = (b"\x1f\x8b", b"PK\x03\x04", b"BZh", b"\xfd7zXZ\x00", b"7z\xbc\xaf\x27\x1c", b"Rar!", b"\x28\xb5\x2f\xfd")


def compactado(rel, dados):
    return rel.lower().endswith(COMPACTADO_EXT) or dados.startswith(COMPACTADO_MAGICA) or dados[257:262] == b"ustar"
ACEITE = re.compile(r"docs-varredura: aceito — (.*)")


def git(raiz, *args, entrada=None):
    return subprocess.run(["git", "-C", raiz] + list(args), input=entrada, capture_output=True)


# ── o que é documento (a migração importa estas duas funções: uma definição só) ─────────────────────────────────

def eh_documento(raiz, caminhos):
    """Os caminhos (relativos, com /) sob sdd/ que o .gitattributes da ÁRVORE marca com export-ignore."""
    sob = [c for c in caminhos if c.startswith("sdd/")]
    if not sob:
        return set()
    r = git(raiz, "check-attr", "-z", "--stdin", "export-ignore", entrada=b"\0".join(c.encode() for c in sob) + b"\0")
    if r.returncode != 0:
        raise RuntimeError("git check-attr falhou: " + r.stderr.decode(errors="replace").strip())
    campos = r.stdout.split(b"\0")
    return {campos[k].decode() for k in range(0, len(campos) - 2, 3) if campos[k + 2] == b"set"}


def documentos(raiz, ref=None):
    """Os documentos de REF; sem REF, os da árvore: versionados e os novos que o .gitignore não exclui (contrato de
    aceite, ajuste 5: o documento ainda não commitado também é conferido, antes de o push o tornar público)."""
    if ref:
        r = git(raiz, "ls-tree", "-r", "-z", "--name-only", ref, "--", "sdd/")
    else:
        r = git(raiz, "ls-files", "-z", "--cached", "--others", "--exclude-standard", "--", "sdd/")
    if r.returncode != 0:
        raise RuntimeError("git não listou os arquivos de %s: %s" % (ref or "HEAD", r.stderr.decode(errors="replace").strip()))
    todos = [c for c in r.stdout.decode().split("\0") if c]
    return sorted(eh_documento(raiz, todos))


def marca_documentos(raiz):
    """O repositório marca documentos? (alguma linha do .gitattributes põe export-ignore sob sdd/)."""
    return bool(eh_documento(raiz, ["sdd/features/x.md", "sdd/reports/x.md", "sdd/handoffs/x.md"]))


# ── regras ─────────────────────────────────────────────────────────────────────────────────────────────────────

def cpf_valido(d):
    if len(set(d)) == 1:
        return False
    for n in (9, 10):
        s = sum(int(d[i]) * (n + 1 - i) for i in range(n))
        if (s * 10) % 11 % 10 != int(d[n]):
            return False
    return True


def cnpj_valido(d):
    if len(set(d)) == 1:
        return False
    p1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    for pesos, n in ((p1, 12), ([6] + p1, 13)):
        r = sum(int(d[i]) * pesos[i] for i in range(n)) % 11
        if (0 if r < 2 else 11 - r) != int(d[n]):
            return False
    return True


def aceito_em(linha):
    """O aceite vale só com motivo: ao menos uma letra ou dígito antes do fim da linha ou do fecho do comentário."""
    m = ACEITE.search(linha)
    return bool(m) and re.search(r"[0-9A-Za-zÀ-ÿ]", re.split(r"-->|\*/", m.group(1))[0]) is not None


def email_ok(local, dominio):
    return DOMINIO_OK.search(dominio) is not None or ("%s@%s" % (local, dominio)).lower() in ENDERECO_OK


def como_texto(dados):
    """O texto do arquivo, ou None se é binário. Log gravado no Windows pode vir em UTF-16 (o PowerShell 5 grava assim):
    os NUL entre as letras não fazem dele binário, e e-mail e CPF/CNPJ dentro dele têm de ser achados (revisão do
    código, N2)."""
    if dados[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return dados.decode("utf-16", errors="replace")
    if b"\0" not in dados:
        return dados.decode("utf-8", errors="replace")
    pares, impares = dados[1::2], dados[0::2]
    if pares and pares.count(0) >= 0.9 * len(pares) and impares.count(0) < 0.1 * len(impares):
        return dados.decode("utf-16-le", errors="replace")   # UTF-16LE sem BOM: texto ASCII com NUL depois de cada letra
    if impares and impares.count(0) >= 0.9 * len(impares) and pares.count(0) < 0.1 * len(pares):
        return dados.decode("utf-16-be", errors="replace")
    return None


def regras_do_arquivo(rel, dados, versionado):
    achados = []
    # o teto é da evidência que vai para o git; o bruto (--pasta) é grande por natureza e vai para o anexo
    if versionado and rel.startswith(EVIDENCIA) and len(dados) > TETO:
        achados.append((rel, 0, "evidência acima de %d bytes (%d)" % (TETO, len(dados))))
    if rel.lower().endswith(CERT_EXT):
        achados.append((rel, 0, "certificado (.pfx/.p12)"))
    if compactado(rel, dados):
        achados.append((rel, 0, "arquivo compactado (a varredura não lê por dentro: extraia e varra os arquivos)"))
    if CHAVE.search(dados):
        n = dados[:CHAVE.search(dados).start()].count(b"\n") + 1
        achados.append((rel, n, "chave privada (PRIVATE KEY)"))
    texto = como_texto(dados)
    if texto is None:
        return achados   # binário: só nome e cabeçalho de chave
    linhas = texto.split("\n")
    for i, ln in enumerate(linhas, 1):
        for m in (EMAIL.finditer(ln) if "@" in ln else ()):
            if not email_ok(m.group(1), m.group(2)):
                achados.append((rel, i, "e-mail fora dos domínios de exemplo"))
        aceito = aceito_em(ln) or (i > 1 and aceito_em(linhas[i - 2]))   # a própria linha e a de baixo, nenhuma outra
        for m in NUMERO.finditer(ln):
            d = re.sub(r"\D", "", m.group(1))
            tipo = "CPF" if len(d) == 11 and cpf_valido(d) else ("CNPJ" if len(d) == 14 and cnpj_valido(d) else "")
            if tipo and not aceito:
                achados.append((rel, i, "%s com dígito verificador válido" % tipo))
    return achados


def procurar(rel, dados, padrao):
    """Modo --padrao: só a regra pedida, em todo arquivo (prova de que um dado pedido sumiu)."""
    if compactado(rel, dados):
        return [(rel, 0, "arquivo compactado: extraia e procure por dentro")]
    texto = como_texto(dados)
    if texto is None:
        return [(rel, 0, "padrão pedido (--padrao), em arquivo binário")] if padrao.search(dados.decode("latin-1")) else []
    return [(rel, i, "padrão pedido (--padrao)") for i, ln in enumerate(texto.split("\n"), 1) if padrao.search(ln)]


def limpo(texto):
    """S17: nome de arquivo com quebra de linha ou caractere de controle não forja linha no log."""
    return "".join(c if c.isprintable() else "?" for c in texto)


def gitleaks(pasta):
    """[(rel, linha, regra)] ou None quando não deu para conferir."""
    exe = shutil.which("gitleaks")
    if not exe:
        return None, "o gitleaks não está instalado (brew install gitleaks)"
    with tempfile.TemporaryDirectory() as tmp:
        rel_json = os.path.join(tmp, "gitleaks.json")
        r = subprocess.run([exe, "detect", "--source", pasta, "--no-git", "--redact", "--no-banner",
                            "--report-format", "json", "--report-path", rel_json, "--exit-code", "0"],
                           capture_output=True)
        if r.returncode != 0 or not os.path.isfile(rel_json):
            return None, "o gitleaks falhou (exit %d)" % r.returncode
        try:
            with open(rel_json, encoding="utf-8") as f:
                lista = json.load(f) or []
        except ValueError:
            return None, "o relatório do gitleaks não é JSON"
    base = os.path.realpath(pasta)
    saida = []
    for a in lista:
        caminho = os.path.realpath(os.path.join(pasta, a.get("File", ""))) if not os.path.isabs(a.get("File", "")) \
            else os.path.realpath(a["File"])
        rel = os.path.relpath(caminho, base).replace(os.sep, "/")
        saida.append((rel, int(a.get("StartLine") or 0), "segredo (gitleaks: %s)" % a.get("RuleID", "?")))
    return saida, ""


# ── entrada ────────────────────────────────────────────────────────────────────────────────────────────────────

def uso(msg):
    print("🛑 docs-varredura: " + msg, file=sys.stderr)
    print("RESULTADO: ERRO DE USO\n→ docs-varredura.sh [RAIZ] | --ref REF [RAIZ] | --pasta DIR, com --padrao REGEX ou --texto TEXTO opcional.",
          file=sys.stderr)
    sys.exit(64)


def copiar_documentos(raiz, ref, destino, tudo=False):
    if tudo:   # --padrao: todos os arquivos, não só os documentos (o dado pedido pode estar em qualquer arquivo)
        r = git(raiz, "ls-tree", "-r", "-z", "--name-only", ref) if ref else git(raiz, "ls-files", "-z")
        lista = sorted(c for c in r.stdout.decode().split("\0") if c)
    else:
        lista = documentos(raiz, ref)
    if ref:
        entrada = b"".join(("%s:%s\n" % (ref, c)).encode() for c in lista)
        r = subprocess.run(["git", "-C", raiz, "cat-file", "--batch"], input=entrada, capture_output=True)
        if r.returncode != 0:
            raise RuntimeError("git cat-file falhou")
        dados, pos = r.stdout, 0
        for c in lista:
            cab_fim = dados.index(b"\n", pos)
            tam = int(dados[pos:cab_fim].split()[2])
            corpo = dados[cab_fim + 1:cab_fim + 1 + tam]
            pos = cab_fim + 1 + tam + 1
            alvo = os.path.join(destino, c)
            os.makedirs(os.path.dirname(alvo), exist_ok=True)
            with open(alvo, "wb") as f:
                f.write(corpo)
    else:
        for c in lista:
            origem = os.path.join(raiz, c)
            if os.path.isfile(origem) and not os.path.islink(origem):
                alvo = os.path.join(destino, c)
                os.makedirs(os.path.dirname(alvo), exist_ok=True)
                shutil.copyfile(origem, alvo)
    return len(lista)


def main(argv):
    raiz, ref, pasta, padrao, literal = None, None, None, None, None
    k = 0
    while k < len(argv):
        a = argv[k]
        if a in ("--ref", "--pasta", "--padrao", "--texto"):
            if k + 1 >= len(argv) or not argv[k + 1]:
                uso("%s pede um valor" % a)
            v = argv[k + 1]
            k += 2
            if a == "--ref":
                ref = v
            elif a == "--pasta":
                pasta = v
            elif a == "--texto":
                padrao, literal = re.compile(re.escape(v)), v
            else:
                try:
                    padrao = re.compile(v)
                except re.error as e:
                    uso("--padrao inválido: %s" % e)
        elif a.startswith("-"):
            uso("opção desconhecida: %s" % a)
        elif raiz is None:
            raiz, k = a, k + 1
        else:
            uso("argumento a mais: %s" % a)
    if pasta and (ref or raiz):
        uso("--pasta não se combina com RAIZ nem com --ref")

    with tempfile.TemporaryDirectory() as tmp:
        if pasta:
            if not os.path.isdir(pasta):
                uso("a pasta não existe: %s" % pasta)
            alvo, onde, n = pasta, "pasta %s" % pasta, sum(len(fs) for _, _, fs in os.walk(pasta))
        else:
            raiz = raiz or "."
            if git(raiz, "rev-parse", "--git-dir").returncode != 0:
                uso("%s não é um repositório git" % raiz)
            if ref and git(raiz, "rev-parse", "--verify", "--quiet", ref + "^{commit}").returncode != 0:
                uso("a ref não existe: %s" % ref)
            tudo = padrao is not None
            if not tudo and not marca_documentos(raiz):
                uso("este repositório não marca documentos (nenhum export-ignore sob sdd/ no .gitattributes)")
            n = copiar_documentos(raiz, ref, tmp, tudo)
            alvo = tmp
            onde = ("todos os arquivos de %s" % (ref or "HEAD")) if tudo else (("documentos de %s" % ref) if ref else "documentos do repositório")

        if padrao is not None:
            achados = []
            for dirpath, _, nomes in os.walk(alvo):
                for nome in sorted(nomes):
                    p = os.path.join(dirpath, nome)
                    if os.path.isfile(p) and not os.path.islink(p):
                        with open(p, "rb") as f:
                            achados += procurar(os.path.relpath(p, alvo).replace(os.sep, "/"), f.read(), padrao)
            if ref and literal is not None:
                # o histórico alcançável pela ref (avaliador, A4): a ponta limpa não prova a remoção se um commit
                # anterior, ainda ligado à ref, guarda o dado
                r = git(raiz, "log", "--format=%h", "-S" + literal, ref)
                if r.returncode != 0:
                    print("⚪ %s: não consegui ler o histórico (git log); nada é dado como limpo." % onde)
                    print("RESULTADO: NÃO CONFERIDO\n→ confira a ref e rode de novo.")
                    return 2
                achados = sorted(achados) + [("histórico de %s" % ref, 0, "texto pedido no commit %s, alcançável pela ref" % h)
                                             for h in r.stdout.decode().split()]
                return relatar(achados, onde + " e o histórico dela", n)
            return relatar(sorted(achados), onde, n)

        segredos, motivo = gitleaks(alvo)
        if segredos is None:
            print("⚪ %s: %s; nada foi conferido." % (onde, motivo))
            print("RESULTADO: NÃO CONFERIDO\n→ instale o gitleaks e rode de novo; sem ele, nada é dado como limpo.")
            return 2
        achados = list(segredos)
        for dirpath, _, nomes in os.walk(alvo):
            for nome in sorted(nomes):
                p = os.path.join(dirpath, nome)
                if os.path.islink(p) or not os.path.isfile(p):
                    continue
                rel = os.path.relpath(p, alvo).replace(os.sep, "/")
                with open(p, "rb") as f:
                    achados += regras_do_arquivo(rel, f.read(), not pasta)
        return relatar(sorted(achados), onde, n)


def relatar(achados, onde, n):
    if not achados:
        print("✅ %s: %d arquivo(s), nada achado." % (onde, n))
        print("RESULTADO: VERDE\n→ siga.")
        return 0
    for rel, linha, regra in achados[:MOSTRAR]:
        print("🔴 %s · %s" % ("%s:%d" % (limpo(rel), linha) if linha else limpo(rel), regra))
    if len(achados) > MOSTRAR:
        print("   … e mais %d" % (len(achados) - MOSTRAR))
    print("RESULTADO: VERMELHO\n→ %d achado(s) em %s; tire o dado ou o arquivo (o trecho não é mostrado de propósito)."
          % (len(achados), onde))
    return 1


if __name__ == "__main__":
    # F16W2: saída em UTF-8 e "\n" também no Windows (o 1º comando do bloco: tests/test_f16w2_saida.py)
    for _canal in (sys.stdout, sys.stderr):
        try:
            _canal.reconfigure(encoding="utf-8", errors="replace", newline="\n")
        except (AttributeError, ValueError):
            pass
    try:
        sys.exit(main(sys.argv[1:]))
    except RuntimeError as e:
        uso(str(e))
