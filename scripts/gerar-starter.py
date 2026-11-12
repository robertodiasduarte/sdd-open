#!/usr/bin/env python3
"""Gera o sdd-starter a partir de uma tag publicada do sdd-open (F17, Decisão 5).

O starter deixa de ter texto próprio nas skills que funcionam sem o `init`: cada uma é gerada daqui. A geração
lê tudo da TAG (nunca da árvore de trabalho), não usa rede e só toca o destino quando tudo passou.

Uso (de quem mantém o pacote; o `init` não copia scripts/ para o projeto do aluno):
  python3 scripts/gerar-starter.py --tag vX.Y.Z <pasta de um clone do sdd-starter>
  python3 scripts/gerar-starter.py --lint <pasta>     # só o lint do init, sobre qualquer pasta

O que entra no destino (o resto dele fica byte a byte igual):
  skills/<cada skill de scripts/starter/lista.txt>/   apagada e regravada, com GERADO.txt
  README.md, scripts/*, .github/workflows/*           de scripts/starter/raiz/
  GERADO.txt                                          sha256 de cada arquivo acima (o check-gerado.py confere)

Passos, por skill: as trocas exatas de scripts/starter/trocas/<skill>.md (cada uma casa exatamente 1 vez) →
regras mecânicas (moldes de sdd/templates/ para dentro da skill, caminhos de .agents/skills/, linha de
identificação do starter, cabeçalho GENERATED, bloco "quando migrar", agents/openai.yaml) → lint do init.

Exit: 0 gerado · 64 uso (tag inexistente, destino sem a forma do starter, destino com mudança não commitada) ·
65 troca que não casa 1 vez, skill sem linha no openai.tsv, molde em conflito ou lint do init · 1 erro de escrita.
Só biblioteca padrão.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

RAIZ_OPEN = Path(__file__).resolve().parents[1]
URL_OPEN = "https://github.com/robertodiasduarte/sdd-open/releases/latest"
URL_STARTER = "https://github.com/robertodiasduarte/sdd-starter/releases/latest"
TEXTO = {".md", ".py", ".sh", ".json", ".yaml", ".yml", ".txt", ".toml", ".tsv"}
PASTA_DESTA = "<pasta desta skill>/"
PASTA_DAS = "<pasta das skills>/"

# Caminhos que só o `init` do sdd-open cria (Decision 4 do DESIGN_F17_STARTER_GERADO). O CHANGELOG.md fica de
# fora: é histórico, não instrução. sdd/config.yaml e AGENTS.md não entram: o primeiro é lido "se existir", o
# segundo é arquivo comum a vários agentes.
LINT_INIT = [
    re.compile(r"sdd/bin/"), re.compile(r"sdd/templates/"), re.compile(r"sdd/hooks/"),
    re.compile(r"sdd/review/"), re.compile(r"sdd/patterns/"), re.compile(r"sdd/playbook\.md"),
    re.compile(r"sdd/invariants\.md"), re.compile(r"sdd/WORKFLOW_CONTRACTS\.yaml"),
    re.compile(r"bin/sdd-open\.sh"), re.compile(r"\.agents/skills/[a-z0-9-]+/"), re.compile(r"init do sdd-open"),
]
MOLDE = re.compile(r"sdd/templates/[A-Za-z0-9_./-]+\.md")


class Falha(Exception):
    def __init__(self, rc: int, msg: str):
        super().__init__(msg)
        self.rc = rc


def git(*args: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(cwd), *args], capture_output=True)


def sha(dado: bytes) -> str:
    return hashlib.sha256(dado).hexdigest()


# ── a árvore da tag ──────────────────────────────────────────────────────────
def extrair_tag(tag: str, destino: Path) -> str:
    r = git("rev-parse", "--verify", "--quiet", "refs/tags/%s^{commit}" % tag, cwd=RAIZ_OPEN)
    if r.returncode != 0:
        raise Falha(64, "a tag %s não existe neste repositório (a geração parte sempre de uma tag publicada)" % tag)
    commit = r.stdout.decode().strip()
    r = git("archive", "--format=tar", commit, cwd=RAIZ_OPEN)
    if r.returncode != 0:
        raise Falha(64, "git archive %s falhou: %s" % (tag, r.stderr.decode(errors="replace").strip()))
    with tarfile.open(fileobj=io.BytesIO(r.stdout)) as t:
        for m in t.getmembers():
            p = Path(m.name)
            if p.is_absolute() or ".." in p.parts:
                raise Falha(65, "caminho inesperado no archive: %s" % m.name)
            if m.isdir():
                (destino / p).mkdir(parents=True, exist_ok=True)
            elif m.isfile():
                alvo = destino / p
                alvo.parent.mkdir(parents=True, exist_ok=True)
                alvo.write_bytes(t.extractfile(m).read())
                os.chmod(alvo, 0o755 if m.mode & 0o111 else 0o644)
            # link e outros tipos ficam de fora; uma skill que dependa deles reprova adiante (arquivo ausente)
    return commit[:12]


# ── trocas exatas ────────────────────────────────────────────────────────────
def ler_trocas(arq: Path) -> list[tuple[str, str, str, int]]:
    """Blocos `## <alvo>` + `<<<< antes` … `====` … `>>>> depois`. Devolve (alvo, antes, depois, nº do bloco)."""
    trocas, alvo, estado, antes, depois, n = [], None, None, [], [], 0
    for i, linha in enumerate(arq.read_text(encoding="utf-8").split("\n"), 1):
        if estado is None:
            if linha.startswith("## "):
                alvo = linha[3:].strip()
            elif linha == "<<<< antes":
                if not alvo:
                    raise Falha(65, "%s:%d: troca sem '## <arquivo>' antes" % (arq.name, i))
                estado, antes, depois, n = "antes", [], [], n + 1
            elif linha.strip() and not linha.startswith("#") and not linha.startswith(">"):
                raise Falha(65, "%s:%d: linha fora de um bloco de troca" % (arq.name, i))
        elif estado == "antes":
            if linha == "====":
                estado = "depois"
            else:
                antes.append(linha)
        else:
            if linha == ">>>> depois":
                if not "".join(antes).strip():
                    raise Falha(65, "%s: bloco %d com o trecho de antes vazio" % (arq.name, n))
                trocas.append((alvo, "\n".join(antes), "\n".join(depois), n))
                estado = None
            else:
                depois.append(linha)
    if estado is not None:
        raise Falha(65, "%s: bloco %d sem '>>>> depois'" % (arq.name, n))
    return trocas


def aplicar_trocas(base: Path, arq: Path) -> int:
    if not arq.is_file():
        return 0
    trocas = ler_trocas(arq)
    for alvo, antes, depois, n in trocas:
        p = base / alvo
        if not p.is_file():
            raise Falha(65, "%s, bloco %d: o arquivo %s não existe" % (arq.name, n, alvo))
        texto = p.read_text(encoding="utf-8")
        vezes = texto.count(antes)
        if vezes != 1:
            raise Falha(65, "%s, bloco %d: o trecho casou %d vez(es) em %s; esperado exatamente 1 "
                            "(o texto do Open mudou? ajuste a troca)" % (arq.name, n, vezes, alvo))
        p.write_text(texto.replace(antes, depois, 1), encoding="utf-8")
    return len(trocas)


# ── regras mecânicas ─────────────────────────────────────────────────────────
def arquivos(pasta: Path) -> list[Path]:
    return sorted(p for p in pasta.rglob("*") if p.is_file())


def eh_texto(p: Path) -> bool:
    return p.suffix in TEXTO


def moldes_citados(texto: str, arvore: Path) -> set[str]:
    return {m for m in MOLDE.findall(texto) if (arvore / m).is_file()}


def trazer_moldes(skill_dir: Path, moldes_dir: Path) -> None:
    """Fechamento transitivo: um molde citado pode citar outro; todos vão para references/ da skill."""
    pendentes = set()
    for p in arquivos(skill_dir):
        if eh_texto(p):
            pendentes |= moldes_citados(p.read_text(encoding="utf-8"), moldes_dir)
    feitos: set[str] = set()
    while pendentes:
        m = pendentes.pop()
        if m in feitos:
            continue
        feitos.add(m)
        pendentes |= moldes_citados((moldes_dir / m).read_text(encoding="utf-8"), moldes_dir) - feitos
    nomes: dict[str, str] = {}
    for m in sorted(feitos):
        nome = Path(m).name
        if nome in nomes:
            raise Falha(65, "%s: dois moldes com o mesmo nome (%s, %s)" % (skill_dir.name, nomes[nome], m))
        nomes[nome] = m
        alvo = skill_dir / "references" / nome
        if alvo.exists():
            raise Falha(65, "%s: o molde %s colide com references/%s da skill" % (skill_dir.name, m, nome))
        alvo.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(moldes_dir / m, alvo)
        os.chmod(alvo, 0o644)


def reescrever(texto: str, skill: str, lista: list[str], moldes_dir: Path) -> str:
    texto = MOLDE.sub(lambda m: PASTA_DESTA + "references/" + Path(m.group(0)).name
                      if (moldes_dir / m.group(0)).is_file() else m.group(0), texto)
    texto = texto.replace(".agents/skills/%s/" % skill, PASTA_DESTA)
    for irma in lista:
        if irma != skill:
            texto = texto.replace(".agents/skills/%s/" % irma, PASTA_DAS + irma + "/")
    return texto


def identificacao(texto: str, skill: str) -> str:
    linhas, trocadas = texto.split("\n"), 0
    for i, ln in enumerate(linhas):
        if ln.startswith("`%s v" % skill) and URL_OPEN in ln:
            linhas[i] = ln.replace(URL_OPEN, URL_STARTER)
            trocadas += 1
    if trocadas != 1:
        raise Falha(65, "%s: a linha de identificação apareceu %d vez(es); esperado 1" % (skill, trocadas))
    return "\n".join(linhas)


def com_cabecalho(texto: str, skill: str, cabecalho: str, migrar: str) -> str:
    if not texto.startswith("---\n"):
        raise Falha(65, "%s/SKILL.md não começa pelo frontmatter" % skill)
    fim = texto.index("\n---\n", 4) + len("\n---\n")
    return texto[:fim] + cabecalho + texto[fim:].rstrip("\n") + "\n" + migrar


def ler_openai(arq: Path) -> dict[str, tuple[str, str, str]]:
    tab = {}
    for linha in arq.read_text(encoding="utf-8").splitlines():
        if not linha.strip() or linha.startswith("#"):
            continue
        c = linha.split("\t")
        if len(c) != 4 or not all(x.strip() for x in c):
            raise Falha(65, "openai.tsv: linha sem os 4 campos: %s" % linha[:60])
        tab[c[0]] = (c[1], c[2], c[3])
    return tab


def openai_yaml(campos: tuple[str, str, str]) -> str:
    nome, curta, prompt = campos
    return ('interface:\n  display_name: "%s"\n  short_description: "%s"\n  default_prompt: "%s"\n'
            % (nome, curta, prompt))


def lista_gerado(pasta: Path, cabecalho: str, ignora: tuple[str, ...] = ()) -> bytes:
    linhas = [cabecalho]
    for p in arquivos(pasta):
        rel = p.relative_to(pasta).as_posix()
        if rel != "GERADO.txt" and rel not in ignora:
            linhas.append("%s  %s" % (sha(p.read_bytes()), rel))
    return ("\n".join(linhas) + "\n").encode("utf-8")


# ── lint do init ─────────────────────────────────────────────────────────────
def lint(pasta: Path) -> list[str]:
    achados = []
    for p in arquivos(pasta):
        if p.name == "CHANGELOG.md" or not eh_texto(p):
            continue
        for n, ln in enumerate(p.read_text(encoding="utf-8", errors="replace").split("\n"), 1):
            for rx in LINT_INIT:
                m = rx.search(ln)
                if m:
                    achados.append("%s:%d: %s" % (p.relative_to(pasta).as_posix(), n, m.group(0)))
                    break
    return achados


# ── geração ──────────────────────────────────────────────────────────────────
def montar(arvore: Path, saida: Path, tag: str, commit: str) -> list[str]:
    dados = arvore / "scripts" / "starter"
    lista = [ln.strip() for ln in (dados / "lista.txt").read_text(encoding="utf-8").splitlines()
             if ln.strip() and not ln.startswith("#")]
    tabela = ler_openai(dados / "openai.tsv")
    cabecalho = (dados / "blocos" / "GENERATED.md").read_text(encoding="utf-8").format(tag=tag, commit=commit)
    migrar = (dados / "blocos" / "MIGRAR.md").read_text(encoding="utf-8")
    nota = "# GENERATED pelo sdd-open %s (commit %s) com scripts/gerar-starter.py — não edite aqui." % (tag, commit)

    # moldes: cópia de sdd/templates/ com as trocas de _moldes aplicadas uma vez
    moldes = saida.parent / "moldes"
    shutil.copytree(arvore / "sdd" / "templates", moldes / "sdd" / "templates")
    for arq in sorted((dados / "trocas" / "_moldes").glob("*.md")):
        aplicar_trocas(moldes, arq)

    relatorio = []
    for skill in lista:
        origem = arvore / ".agents" / "skills" / skill
        if not origem.is_dir():
            raise Falha(65, "lista.txt cita %s, que não existe em .agents/skills/ da tag" % skill)
        if skill not in tabela:
            raise Falha(65, "%s não tem linha em scripts/starter/openai.tsv" % skill)
        destino = saida / "skills" / skill
        shutil.copytree(origem, destino)
        n_trocas = aplicar_trocas(destino, dados / "trocas" / ("%s.md" % skill))
        trazer_moldes(destino, moldes)
        for p in arquivos(destino):
            if eh_texto(p):
                p.write_text(reescrever(p.read_text(encoding="utf-8"), skill, lista, moldes), encoding="utf-8")
        s = destino / "SKILL.md"
        s.write_text(com_cabecalho(identificacao(s.read_text(encoding="utf-8"), skill), skill, cabecalho, migrar),
                     encoding="utf-8")
        (destino / "agents").mkdir(exist_ok=True)
        (destino / "agents" / "openai.yaml").write_text(openai_yaml(tabela[skill]), encoding="utf-8")
        (destino / "GERADO.txt").write_bytes(lista_gerado(destino, nota))
        relatorio.append("✅ %s: %d arquivo(s), %d troca(s)" % (skill, len(arquivos(destino)) - 1, n_trocas))

    shutil.copytree(dados / "raiz", saida, dirs_exist_ok=True)
    achados = lint(saida)
    if achados:
        raise Falha(65, "o lint do init achou %d citação(ões) a arquivo que só o init cria:\n  %s"
                    % (len(achados), "\n  ".join(achados[:40])))
    infra = [p.relative_to(saida).as_posix() for p in arquivos(saida) if not p.relative_to(saida).parts[0] == "skills"]
    linhas = [nota]
    for rel in sorted(infra + ["skills/%s/GERADO.txt" % s for s in lista]):
        linhas.append("%s  %s" % (sha((saida / rel).read_bytes()), rel))
    (saida / "GERADO.txt").write_text("\n".join(linhas) + "\n", encoding="utf-8")
    return relatorio


def conferir_destino(destino: Path) -> None:
    if not (destino / "skills").is_dir() or not (destino / "scripts" / "check-versions.py").is_file():
        raise Falha(64, "%s não tem a forma do sdd-starter (skills/ e scripts/check-versions.py)" % destino)
    r = git("status", "--porcelain", "--untracked-files=all", cwd=destino)
    if r.returncode != 0:
        raise Falha(64, "%s não é um repositório git (o git é a rede de segurança da geração)" % destino)
    if r.stdout.strip():
        raise Falha(64, "%s tem mudança não commitada ou arquivo não rastreado: commite ou guarde antes" % destino)


def gravar(saida: Path, destino: Path) -> None:
    for p in arquivos(saida):
        rel = p.relative_to(saida)
        if rel.parts[0] == "skills" and len(rel.parts) > 1:
            continue
        alvo = destino / rel
        alvo.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(p, alvo)
        os.chmod(alvo, os.stat(p).st_mode & 0o777)
    for pasta in sorted((saida / "skills").iterdir()):
        alvo = destino / "skills" / pasta.name
        if alvo.exists():
            shutil.rmtree(alvo)
        shutil.copytree(pasta, alvo)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Gera o sdd-starter a partir de uma tag do sdd-open.")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--tag", help="tag publicada do sdd-open (ex.: v2.13.0)")
    g.add_argument("--lint", metavar="PASTA", help="só o lint do init sobre a pasta")
    ap.add_argument("destino", nargs="?", help="pasta de um clone do sdd-starter")
    try:
        a = ap.parse_args(argv)
    except SystemExit as e:
        return 64 if e.code else 0
    try:
        if a.lint:
            achados = lint(Path(a.lint))
            for x in achados:
                print("🛑 %s" % x)
            if achados:
                print("RESULTADO: CITA ARQUIVO DO INIT\n→ troque a citação (scripts/starter/trocas/) e gere de novo.")
                return 65
            print("RESULTADO: VERDE\n→ nenhuma citação a arquivo que só o init cria.")
            return 0
        if not a.destino:
            raise Falha(64, "falta a pasta do clone do sdd-starter")
        destino = Path(a.destino).resolve()
        conferir_destino(destino)
        with tempfile.TemporaryDirectory(prefix="gerar-starter-") as tmp:
            arvore, saida = Path(tmp) / "open", Path(tmp) / "saida"
            arvore.mkdir()
            saida.mkdir()
            commit = extrair_tag(a.tag, arvore)
            relatorio = montar(arvore, saida, a.tag, commit)
            try:
                gravar(saida, destino)
            except OSError as e:
                print("🛑 erro de escrita no destino: %s" % e)
                print("RESULTADO: DESTINO PELA METADE\n→ no starter: git checkout -- . && git clean -fd; e gere de novo.")
                return 1
        for linha in relatorio:
            print(linha)
        print("RESULTADO: GERADO\n→ no starter: python3 scripts/check-gerado.py, os testes dele e um commit numa branch.")
        return 0
    except Falha as e:
        print("🛑 %s" % e)
        print("RESULTADO: NADA FOI GRAVADO\n→ corrija a causa acima e rode de novo.")
        return e.rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
