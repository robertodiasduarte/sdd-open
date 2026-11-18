#!/usr/bin/env python3
"""docs-migracao.py — traz os documentos da branch de documentos (pela tag de arquivo) para a main, uma vez (F26).

Por que existe: os documentos das frentes moraram numa branch separada até a F26. A migração leva o estado atual
deles para a main, num commit só, e deixa na tag de arquivo o que não deve ir para o git (o bruto, o acima do teto e o
que a varredura dos documentos reprova). Cada arquivo da tag fica numa lista com a categoria e o motivo; a
conferência lê a lista e o git, arquivo a arquivo, e só então a branch de documentos pode sair.

Uso (de quem mantém o pacote, na raiz do repositório):
  python3 scripts/docs-migracao.py --copiar TAG          grava os documentos na árvore e a lista
  python3 scripts/docs-migracao.py --conferir TAG        0 só se o commit da migração bate com a lista e a lista com
                                                         a tag (o commit que criou a lista: os commits de depois, como
                                                         a ficha da release ou uma entrada nova da fila, não contam)
  python3 scripts/docs-migracao.py --pode-aposentar TAG  0 só se a tag é o último commit da branch no remoto e a
                                                         conferência sai 0 [--remoto origin] [--branch docs/incorporar-starter]

Categorias da lista (sdd/reports/MIGRACAO_DOCS_F26.tsv): igual (mesmo blob na main) · ajustado (na main, com o
comentário de aceite da varredura antes de um número que não é CPF/CNPJ) · fora (só na tag: bruto, acima do teto, ou
reprovado pela varredura). "O que é documento" vem do docs-varredura.py (export-ignore sob sdd/): uma definição só.

Exit: 0 · 1 desvio (cada um numa linha 🔴) · 64 uso. Python >= 3.9, só stdlib.
"""
import sys as _sdd_sys  # F16W2: saída em UTF-8 e "\n" também no Windows
for _sdd_c in (_sdd_sys.stdout, _sdd_sys.stderr):
    try:
        _sdd_c.reconfigure(encoding="utf-8", errors="replace", newline="\n")
    except (AttributeError, ValueError):
        pass

import hashlib
import importlib.util
import os
import re
import subprocess
import sys
import tempfile

LISTA = "sdd/reports/MIGRACAO_DOCS_F26.tsv"
FILA = "sdd/curadoria/fila/"
BRUTO = [
    ("transcrição de modelo", re.compile(r"/(codex|claude|gemini|kimi|openrouter|deepseek|qwen)[-_][^/]*\.log$")),
    ("gabarito copiado", re.compile(r"/gabarito[^/]*/")),
    ("log de série", re.compile(r"(?i)/[^/]*seri(e|es)[^/]*$")),
    ("ensaio", re.compile(r"/ensaio[^/]*$")),
    ("conversa do teste do iniciante", re.compile(r"/INICIANTE-[^/]*$")),
]
ACEITE_MIGRACAO = "<!-- docs-varredura: aceito — número de id ou de run, não documento de pessoa (migração F26) -->"


def carregar_varredura(raiz):
    caminho = os.path.join(raiz, "sdd", "bin", "docs-varredura.py")
    spec = importlib.util.spec_from_file_location("docs_varredura", caminho)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def git(raiz, *args, entrada=None):
    return subprocess.run(["git", "-C", raiz] + list(args), input=entrada, capture_output=True)


def uso(msg):
    print("🛑 docs-migracao: " + msg, file=sys.stderr)
    print("RESULTADO: ERRO DE USO\n→ docs-migracao.py --copiar|--conferir|--pode-aposentar TAG", file=sys.stderr)
    sys.exit(64)


def blobs(raiz, ref, caminhos):
    """{caminho: (sha, tamanho)} em REF (só os que existem)."""
    if not caminhos:
        return {}
    r = git(raiz, "ls-tree", "-r", "-l", "-z", ref, "--", *caminhos)
    saida = {}
    for item in r.stdout.decode().split("\0"):
        if not item:
            continue
        meta, caminho = item.split("\t", 1)
        _, tipo, sha, tam = meta.split()
        if tipo == "blob":
            saida[caminho] = (sha, int(tam))
    return saida


def conteudos(raiz, ref, caminhos):
    entrada = b"".join(("%s:%s\n" % (ref, c)).encode() for c in caminhos)
    r = git(raiz, "cat-file", "--batch", entrada=entrada)
    dados, pos, saida = r.stdout, 0, {}
    for c in caminhos:
        fim = dados.index(b"\n", pos)
        tam = int(dados[pos:fim].split()[2])
        saida[c] = dados[fim + 1:fim + 1 + tam]
        pos = fim + 1 + tam + 1
    return saida


def classe_bruta(caminho):
    for nome, rx in BRUTO:
        if rx.search("/" + caminho):
            return nome
    return ""


def achados_por_arquivo(dv, conteudo):
    """{caminho: [regras]} pela varredura dos documentos (regras próprias + gitleaks numa cópia)."""
    saida = {}
    with tempfile.TemporaryDirectory() as tmp:
        for c, d in conteudo.items():
            alvo = os.path.join(tmp, c)
            os.makedirs(os.path.dirname(alvo), exist_ok=True)
            with open(alvo, "wb") as f:
                f.write(d)
            for _, linha, regra in dv.regras_do_arquivo(c, d, True):
                saida.setdefault(c, []).append((linha, regra))
        segredos, motivo = dv.gitleaks(tmp)
        if segredos is None:
            raise RuntimeError(motivo)
        for c, linha, regra in segredos:
            saida.setdefault(c, []).append((linha, regra))
    return saida


def so_numero(regras):
    return bool(regras) and all(r.startswith(("CPF ", "CNPJ ")) for _, r in regras)


def blob_sha(dados):
    """O SHA-1 que o git daria a este conteúdo (git hash-object)."""
    return hashlib.sha1(b"blob %d\0" % len(dados) + dados).hexdigest()


def ajustar(dados, regras):
    """Comentário de aceite antes de cada linha com número que fecha a conta de CPF/CNPJ (só Markdown)."""
    linhas = dados.decode("utf-8").split("\n")
    for n in sorted({l for l, _ in regras}, reverse=True):
        linhas.insert(n - 1, ACEITE_MIGRACAO)
    return "\n".join(linhas).encode("utf-8")


def classificar(raiz, dv, tag):
    docs = dv.documentos(raiz, tag)
    conteudo = conteudos(raiz, tag, docs)
    achados = achados_por_arquivo(dv, conteudo)
    plano = {}
    for c in docs:
        bruto = classe_bruta(c)
        regras = achados.get(c, [])
        grande = c.startswith(dv.EVIDENCIA) and len(conteudo[c]) > dv.TETO
        if bruto:
            plano[c] = ("fora", "bruto: " + bruto)
        elif grande:
            plano[c] = ("fora", "acima do teto (%d bytes)" % len(conteudo[c]))
        elif regras and so_numero(regras) and c.endswith(".md"):
            plano[c] = ("ajustado", "comentário de aceite antes de %d número(s) que não são CPF/CNPJ" % len(regras))
        elif regras:
            plano[c] = ("fora", "varredura: " + ", ".join(sorted({r for _, r in regras})))
        else:
            plano[c] = ("igual", "")
    return docs, conteudo, achados, plano


def copiar(raiz, tag):
    dv = carregar_varredura(raiz)
    docs, conteudo, achados, plano = classificar(raiz, dv, tag)
    na_head = blobs(raiz, "HEAD", docs)
    tag_blobs = blobs(raiz, tag, docs)
    conflito = [c for c in docs if c in na_head and na_head[c][0] != tag_blobs[c][0] and plano[c][0] != "fora"]
    if conflito:
        for c in conflito:
            print("🔴 %s · já existe na HEAD com outro conteúdo; nada foi gravado" % c)
        print("RESULTADO: VERMELHO\n→ resolva o conflito (renomeie o documento da main) e rode de novo.")
        return 1
    for c in docs:
        cat = plano[c][0]
        if cat == "fora":
            continue
        dados = conteudo[c] if cat == "igual" else ajustar(conteudo[c], achados[c])
        alvo = os.path.join(raiz, c)
        os.makedirs(os.path.dirname(alvo), exist_ok=True)
        with open(alvo, "wb") as f:
            f.write(dados)
    with open(os.path.join(raiz, LISTA), "w", encoding="utf-8", newline="\n") as f:
        f.write("caminho\tcategoria\tmotivo\n")
        for c in docs:
            f.write("%s\t%s\t%s\n" % (c, plano[c][0], plano[c][1]))
    conta = {k: sum(1 for c in docs if plano[c][0] == k) for k in ("igual", "ajustado", "fora")}
    print("✅ %d documento(s) da tag: %d igual · %d ajustado · %d fora (lista em %s)"
          % (len(docs), conta["igual"], conta["ajustado"], conta["fora"], LISTA))
    print("RESULTADO: COPIADO\n→ commite só os documentos e a lista, num commit próprio, e rode --conferir.")
    return 0


def commit_da_migracao(raiz):
    """O commit que criou a lista na história da HEAD (o mais antigo, se ela foi apagada e recriada), ou ""."""
    r = git(raiz, "log", "--diff-filter=A", "--format=%H", "HEAD", "--", LISTA)
    criadores = [x for x in r.stdout.decode().split() if x]
    return criadores[-1] if criadores else ""


def ler_lista(raiz, ref="HEAD"):
    r = git(raiz, "show", ref + ":" + LISTA)
    if r.returncode != 0:
        return None
    linhas = r.stdout.decode("utf-8").split("\n")[1:]
    return [tuple((ln.split("\t") + ["", ""])[:3]) for ln in linhas if ln.strip()]


def conferir(raiz, tag, falar=True):
    dv = carregar_varredura(raiz)
    erros = []
    # A conferência olha o commit da migração, não a HEAD: depois dele a main segue a vida (a release atualiza a
    # ficha e o plano, a colheita põe entrada na fila), e isso não desfaz a prova de que a migração foi fiel.
    mig = commit_da_migracao(raiz)
    lista = ler_lista(raiz, mig) if mig else None
    if lista is None:
        erros.append((LISTA, "a lista da migração não está na HEAD"))
    else:
        docs, conteudo, achados, plano = classificar(raiz, dv, tag)
        vistos = {}
        for c, cat, motivo in lista:
            vistos[c] = vistos.get(c, 0) + 1
        for c in sorted(vistos):
            if vistos[c] > 1:
                erros.append((c, "aparece %d vezes na lista" % vistos[c]))
            if c not in plano:
                erros.append((c, "está na lista e não é documento da tag"))
        for c in docs:
            if c not in vistos:
                erros.append((c, "documento da tag fora da lista"))
        tag_b = blobs(raiz, tag, docs)
        head_b = blobs(raiz, mig, docs)
        for c, cat, motivo in lista:
            if c not in plano:
                continue
            if cat in ("igual", "ajustado") and plano[c][0] != cat:   # revisão do código, R3: a categoria se recalcula
                erros.append((c, "%s na lista, mas a tag pede %s" % (cat, plano[c][0])))
                continue
            if cat == "igual" and (c not in head_b or head_b[c][0] != tag_b[c][0]):
                erros.append((c, "igual na lista, mas o commit da migração não tem o mesmo conteúdo da tag"))
            elif cat == "ajustado" and (c not in head_b or head_b[c][0] != blob_sha(ajustar(conteudo[c], achados[c]))
                                        or not motivo.strip()):
                # revisão do código, R3: o ajustado é exatamente o da tag com o comentário de aceite, nada além
                erros.append((c, "ajustado na lista, mas ausente, sem motivo ou diferente do ajuste da tag"))
            elif cat == "fora":
                if c in head_b:
                    erros.append((c, "fora na lista, mas está no commit da migração"))
                if plano[c][0] != "fora":   # achado N1 da revisão do DESIGN: "fora" só com motivo que se prova
                    erros.append((c, "fora na lista sem ser bruto, acima do teto ou reprovado pela varredura"))
            elif cat not in ("igual", "ajustado", "fora"):
                erros.append((c, "categoria desconhecida: %s" % cat))
        # Nenhum arquivo de fora das pastas de documento veio da tag. Com merge por squash, o commit que cria a lista
        # traz também o código da frente (revisão do código, R4): o que reprova é o arquivo que ficou igual ao da tag
        # sem ser igual antes do commit, não o fato de o commit tocar código.
        r = git(raiz, "show", "--name-only", "--no-renames", "--format=", mig)
        tocados = [x for x in r.stdout.decode().split("\n") if x]
        nao_doc = sorted(set(tocados) - dv.eh_documento(raiz, tocados))
        pai = git(raiz, "rev-parse", "--verify", "--quiet", mig + "^1").stdout.decode().strip()
        b_mig, b_tag = blobs(raiz, mig, nao_doc), blobs(raiz, tag, nao_doc)
        b_pai = blobs(raiz, pai, nao_doc) if pai else {}
        for c in nao_doc:
            if c in b_mig and c in b_tag and b_mig[c][0] == b_tag[c][0] and b_pai.get(c, ("",))[0] != b_tag[c][0]:
                erros.append((c, "o commit da migração (%s) trouxe da tag um arquivo que não é documento" % mig[:7]))
        r = git(raiz, "ls-tree", "-r", "--name-only", mig, "--", FILA)
        pendentes = sorted({"/".join(x.split("/")[:5]) for x in r.stdout.decode().split("\n") if x.count("/") >= 5})
        for e in pendentes:
            erros.append((e, "entrada da fila da curadoria ainda pendente (rode o lote antes da migração)"))
    if falar:
        for c, motivo in erros[:50]:
            print("🔴 %s · %s" % (c, motivo))
        if len(erros) > 50:
            print("   … e mais %d" % (len(erros) - 50))
        if erros:
            print("RESULTADO: VERMELHO\n→ %d desvio(s) entre a main, a lista e a tag." % len(erros))
        else:
            print("✅ o commit da migração (%s) bate com a lista e a lista com a tag %s, arquivo a arquivo." % (mig[:7], tag))
            print("RESULTADO: VERDE\n→ siga.")
    return 1 if erros else 0


def pode_aposentar(raiz, tag, remoto, branch):
    r = git(raiz, "ls-remote", remoto, "refs/heads/" + branch)
    remoto_sha = (r.stdout.decode().split() or [""])[0]
    tag_sha = git(raiz, "rev-parse", tag + "^{commit}").stdout.decode().strip()
    erros = []
    if r.returncode != 0 or not remoto_sha:
        erros.append("não li a branch %s em %s" % (branch, remoto))
    elif remoto_sha != tag_sha:
        erros.append("a tag %s (%s) não é o último commit de %s em %s (%s)" % (tag, tag_sha[:7], branch, remoto, remoto_sha[:7]))
    if conferir(raiz, tag, falar=False) != 0:
        erros.append("a conferência da migração não sai 0 (rode --conferir)")
    for e in erros:
        print("🔴 " + e)
    if erros:
        print("RESULTADO: NÃO PODE\n→ nada foi apagado; resolva e rode de novo.")
        return 1
    print("✅ a tag guarda o último commit de %s e a main bate com ela." % branch)
    print("RESULTADO: PODE\n→ apagar a branch e a worktree de documentos ainda pede o OK do Roberto.")
    return 0


def main(argv):
    if len(argv) < 2 or argv[0] not in ("--copiar", "--conferir", "--pode-aposentar"):
        uso("modo e tag obrigatórios")
    modo, tag, resto = argv[0], argv[1], argv[2:]
    remoto, branch = "origin", "docs/incorporar-starter"
    k = 0
    while k < len(resto):
        if resto[k] in ("--remoto", "--branch") and k + 1 < len(resto):
            if resto[k] == "--remoto":
                remoto = resto[k + 1]
            else:
                branch = resto[k + 1]
            k += 2
        else:
            uso("argumento desconhecido: %s" % resto[k])
    raiz = git(".", "rev-parse", "--show-toplevel").stdout.decode().strip()
    if not raiz:
        uso("rode dentro do repositório")
    if git(raiz, "rev-parse", "--verify", "--quiet", tag + "^{commit}").returncode != 0:
        print("🔴 a tag %s não existe neste repositório" % tag)
        print("RESULTADO: VERMELHO\n→ crie a tag de arquivo no último commit da branch de documentos.")
        return 1
    if modo == "--copiar":
        return copiar(raiz, tag)
    if modo == "--conferir":
        return conferir(raiz, tag)
    return pode_aposentar(raiz, tag, remoto, branch)


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
