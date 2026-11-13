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
    # a pasta com ou sem a barra final: `sdd/hooks` também é citar o que só o init cria (F17b, passo 0); a
    # lookahead deixa de fora o nome mais longo (`sdd/reviews/` não é `sdd/review/`)
    re.compile(r"sdd/(?:bin|templates|hooks|review|patterns)(?:/|(?![A-Za-z0-9_-]))"), re.compile(r"sdd/playbook\.md"),
    re.compile(r"sdd/invariants\.md"), re.compile(r"sdd/WORKFLOW_CONTRACTS\.yaml"),
    re.compile(r"bin/sdd-open\.sh"), re.compile(r"init do sdd-open"), re.compile(r"`init` do sdd-open"),
]
MOLDE = re.compile(r"sdd/templates/[A-Za-z0-9_/-]+\.md")
PAR = re.compile(r"\.claude/skills/(sdd-[a-z0-9-]+)/`\s+ou\s+`\.agents/skills/\1/")
SEMVER = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


class Falha(Exception):
    def __init__(self, rc: int, msg: str):
        super().__init__(msg)
        self.rc = rc


def git(*args: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(cwd), *args], capture_output=True)


def ler(p: Path) -> str:
    """Texto sem traduzir o fim de linha (read_text troca CRLF por LF): o que nenhuma regra muda sai byte a byte."""
    return p.read_bytes().decode("utf-8")


def gravar_se_mudou(p: Path, texto: str) -> None:
    dado = texto.encode("utf-8")
    if dado != p.read_bytes():
        p.write_bytes(dado)


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
        texto = ler(p)
        vezes = texto.count(antes)
        if vezes != 1:
            raise Falha(65, "%s, bloco %d: o trecho casou %d vez(es) em %s; esperado exatamente 1 "
                            "(o texto do Open mudou? ajuste a troca)" % (arq.name, n, vezes, alvo))
        gravar_se_mudou(p, texto.replace(antes, depois, 1))
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
        # o CHANGELOG é histórico: um molde citado lá não vai para references/ (e o lint já o deixa de fora)
        if eh_texto(p) and p.name != "CHANGELOG.md":
            pendentes |= moldes_citados(ler(p), moldes_dir)
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


def reescrever(texto: str, skill: str, lista: list[str], moldes_dir: Path, markdown: bool,
               historico: bool = False) -> str:
    """Caminhos só no Markdown (num script, `<pasta desta skill>` viraria redirecionamento do shell); a URL do Open
    em todo arquivo de texto. O par que define a pasta (`.claude/skills/x/` ou `.agents/skills/x/`) fica como está."""
    texto = texto.replace(URL_OPEN, URL_STARTER)
    if not markdown:
        # num script, o caminho só aparece em mensagem, uso ou comentário (conferido): vira o nome da pasta, por extenso,
        # porque `<pasta desta skill>` num comando colado viraria redirecionamento (avaliador, ciclo 1, achado 1)
        # a irmã gerada também (F17b, passo 0): antes, só a própria skill; a irmã sobrava e o lint saía 65
        for nome in [skill] + [n for n in lista if n != skill]:
            texto = texto.replace(".agents/skills/%s/" % nome, "<pasta da skill %s>/" % nome)
        return texto
    if not historico:   # no CHANGELOG o molde fica como foi escrito: ele não vai para references/
        texto = MOLDE.sub(lambda m: PASTA_DESTA + "references/" + Path(m.group(0)).name
                          if (moldes_dir / m.group(0)).is_file() else m.group(0), texto)
    guardados: list[str] = []

    def guardar(m: re.Match) -> str:
        guardados.append(m.group(0))
        return "\x00%d\x00" % (len(guardados) - 1)

    for nome in lista:
        texto = re.sub(r"\.claude/skills/%s/`\s+ou\s+`\.agents/skills/%s/" % (re.escape(nome), re.escape(nome)), guardar, texto)
    texto = texto.replace(".agents/skills/%s/" % skill, PASTA_DESTA)
    for irma in lista:
        if irma != skill:
            texto = texto.replace(".agents/skills/%s/" % irma, PASTA_DAS + irma + "/")
    return re.sub(r"\x00(\d+)\x00", lambda m: guardados[int(m.group(1))], texto)


def identificacao(texto: str, skill: str) -> str:
    linhas, trocadas = texto.split("\n"), 0
    for i, ln in enumerate(linhas):
        if ln.startswith("`%s v" % skill) and URL_STARTER in ln:
            trocadas += 1
    if trocadas != 1:
        raise Falha(65, "%s: a linha de identificação apareceu %d vez(es); esperado 1" % (skill, trocadas))
    return "\n".join(linhas)


def sem_fluxo_encadeado(texto: str, skill: str) -> str:
    """No starter não há encadeamento de fases (nem o sdd-fluxo.sh): a seção sai do título até o `---` seguinte."""
    linhas = texto.split("\n")
    titulos = [i for i, ln in enumerate(linhas) if ln == "### Fluxo encadeado"]
    if not titulos:
        return texto
    if len(titulos) > 1:
        raise Falha(65, "%s/SKILL.md tem %d seções '### Fluxo encadeado'; esperado no máximo 1" % (skill, len(titulos)))
    ini = titulos[0]
    fim = next((i for i in range(ini + 1, len(linhas)) if linhas[i] == "---"), None)
    if fim is None:
        raise Falha(65, "%s/SKILL.md: a seção '### Fluxo encadeado' não termina num '---'" % skill)
    return "\n".join(linhas[:ini] + linhas[fim:])


# ── skill de modo (Decision 2 do DESIGN_F17B_STARTER_ETAPA2) ─────────────────
# Arquivo citado pelo modo = `references/…`, `assets/…` ou `scripts/…` com extensão, relativo à skill. Limite
# conhecido: um `scripts/x.sh` do projeto do aluno citado no texto também casa e, sem esse arquivo na skill, o
# gerador sai 65; escreva a citação de outro jeito (ex.: "o script de deploy do projeto").
CITA = re.compile(r"(?<![\w/.-])((?:references|assets|scripts)/[A-Za-z0-9_./-]+\.[A-Za-z0-9]+)")


def ler_modos(arq: Path) -> dict[str, tuple[str, str]]:
    """`skill<TAB>arquivo de modo[<TAB>pasta-base]`, relativos à skill: o SKILL.md do starter sai só do arquivo de
    modo. A pasta-base (F17c, Decision 1) é de onde vêm os arquivos que o modo cita, com o mesmo caminho relativo
    (`web/references/x.md` vai como `references/x.md`); sem ela, a raiz da skill."""
    modos = {}
    if not arq.is_file():
        return modos
    for linha in arq.read_text(encoding="utf-8").splitlines():
        if not linha.strip() or linha.startswith("#"):
            continue
        c = linha.split("\t")
        if len(c) not in (2, 3) or not all(x.strip() for x in c):
            raise Falha(65, "modos.tsv: linha sem 2 ou 3 campos (skill, arquivo de modo[, pasta-base]): %s" % linha[:60])
        base = c[2] if len(c) == 3 else "."
        for rel in (c[1], base):
            if Path(rel).is_absolute() or ".." in Path(rel).parts:
                raise Falha(65, "modos.tsv: o caminho %s de %s sai da pasta da skill" % (rel, c[0]))
        modos[c[0]] = (c[1], base)
    return modos


def frontmatter(texto: str, onde: str) -> tuple[list[str], str]:
    """Linhas do frontmatter (sem os `---`) e o corpo depois dele."""
    if not texto.startswith("---\n") or "\n---\n" not in texto[3:]:
        raise Falha(65, "%s: sem frontmatter" % onde)
    fim = texto.index("\n---\n", 3)
    return texto[4:fim].split("\n"), texto[fim + len("\n---\n"):]


def campo(linhas: list[str], nome: str) -> list[str]:
    """O bloco de um campo de topo (a linha `nome:` e as indentadas que a seguem)."""
    for i, ln in enumerate(linhas):
        if ln.startswith(nome + ":"):
            j = i + 1
            while j < len(linhas) and (linhas[j].startswith(" ") or not linhas[j].strip()):
                j += 1
            return linhas[i:j]
    return []


def compor(origem: Path, destino: Path, modo_rel: str, base: str = ".") -> None:
    skill = origem.name
    modo = origem / modo_rel
    if not modo.is_file():
        raise Falha(65, "%s: o arquivo de modo %s não existe" % (skill, modo_rel))
    raiz = origem / base
    if not raiz.is_dir():
        raise Falha(65, "%s: a pasta-base %s do modo não existe" % (skill, base))
    # o arquivo de modo, visto da pasta-base (para não ir como arquivo citado)
    modo_na_base = modo.resolve().relative_to(raiz.resolve()).as_posix() if raiz.resolve() in modo.resolve().parents else None
    fm_modo, corpo = frontmatter(ler(modo), "%s/%s" % (skill, modo_rel))
    fm_open, resto = frontmatter(ler(origem / "SKILL.md"), "%s/SKILL.md" % skill)
    # as duas: sem a compatibility do modo, a do Open (que fala de slots e scripts do init) vazaria para o starter
    for nome in ("description", "compatibility"):
        if not campo(fm_modo, nome):
            raise Falha(65, "%s/%s: o frontmatter do modo não tem %s" % (skill, modo_rel, nome))
    desc = re.sub(r'^description:\s*"?|"?\s*$', "", " ".join(x.strip() for x in campo(fm_modo, "description")))
    if len(desc) > 1024:   # o upload do claude.ai e do ChatGPT recusa acima disso (o check-versions do starter também)
        raise Falha(65, "%s/%s: a description do modo tem %d caracteres; o limite é 1.024" % (skill, modo_rel, len(desc)))
    ident = [ln for ln in resto.split("\n") if ln.startswith("`%s v" % skill)]
    if len(ident) != 1 or corpo.count(ident[0]) != 1:
        raise Falha(65, "%s: o modo tem de trazer, uma vez, a mesma linha de identificação do SKILL.md (%s)"
                    % (skill, ident[0][:40] if ident else "ausente no SKILL.md"))
    # o frontmatter do Open, com description e compatibility trocados pelos blocos do modo (o campo do Open
    # pode ter linhas de continuação, como `description: >-`: elas saem junto)
    final, pular = [], False
    for ln in fm_open:
        topo = bool(ln.strip()) and not ln.startswith(" ")
        if topo:
            nome = ln.split(":", 1)[0]
            pular = nome in ("description", "compatibility") and bool(campo(fm_modo, nome))
            final.extend(campo(fm_modo, nome) if pular else [ln])
        elif not pular:
            final.append(ln)
    destino.mkdir(parents=True)
    (destino / "SKILL.md").write_bytes(("---\n%s\n---\n%s" % ("\n".join(final), corpo)).encode("utf-8"))
    pendentes, feitos = set(CITA.findall(corpo)), set()
    while pendentes:
        rel = pendentes.pop()
        if rel in feitos or rel == modo_na_base:
            continue
        if ".." in Path(rel).parts:
            raise Falha(65, "%s: o modo cita %s, que sai da pasta-base" % (skill, rel))
        if not (raiz / rel).is_file():
            raise Falha(65, "%s: o modo cita %s, que não existe em %s" % (skill, rel, "a skill" if base == "." else base + "/"))
        feitos.add(rel)
        (destino / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(raiz / rel), str(destino / rel))
        if eh_texto(raiz / rel):
            pendentes |= set(CITA.findall(ler(raiz / rel)))


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
        if any('"' in x or "\\" in x for x in c):
            raise Falha(65, "openai.tsv: aspas ou barra invertida quebrariam o YAML: %s" % linha[:60])
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
def ler_aceites(arq: Path) -> list[tuple[str, str, str]]:
    """`<arquivo relativo à raiz do starter>\t<trecho exato da linha>\t<motivo>`: citação que fica, com o motivo."""
    if not arq.is_file():
        return []
    aceites = []
    for linha in arq.read_text(encoding="utf-8").splitlines():
        if not linha.strip() or linha.startswith("#"):
            continue
        c = linha.split("\t")
        if len(c) != 3 or not all(x.strip() for x in c):
            raise Falha(65, "lint-aceitos.tsv: linha sem os 3 campos (arquivo, trecho, motivo): %s" % linha[:60])
        aceites.append((c[0], c[1], c[2]))
    return aceites


def lint(pasta: Path, aceites: list[tuple[str, str, str]] = (), fora: list[str] = (), sem_uso: bool = True) -> list[str]:
    """`fora`: skills do Open que o starter não recebe; citar a pasta delas (`.agents/skills/<nome>/`) é citar o que
    não existe lá. As geradas podem ser citadas: o par que define a pasta fica, e o resto vira <pasta …>."""
    padroes = LINT_INIT + [re.compile(r"\.agents/skills/%s/" % re.escape(n)) for n in fora] + \
        [re.compile(r"\.agents/skills/sdd-[a-z0-9-]+/"), re.compile(r"`sync`")]
    achados, usados = [], set()
    for p in arquivos(pasta):
        if p.name == "CHANGELOG.md" or not eh_texto(p):
            continue
        texto = p.read_text(encoding="utf-8", errors="replace")
        # o par que define a pasta (`.claude/skills/x/` ou `.agents/skills/x/`) é texto certo no starter: some do lint
        # (só de skill gerada: o par de uma skill que o starter não recebe aponta o que não existe lá; rodada 5, R2)
        texto = PAR.sub(lambda m: m.group(0) if m.group(1) in fora else re.sub(r"[^\n]", " ", m.group(0)), texto)
        for n, ln in enumerate(texto.split("\n"), 1):
            for rx in padroes:
                # cada citação da linha conta; um aceite cobre só a citação que está dentro do trecho dele
                # (revisão, rodada 2, R4: antes, o aceite de uma citação calava outra na mesma linha)
                rel = p.relative_to(pasta).as_posix()
                for m in rx.finditer(ln):
                    cobre = [i for i, (arq, trecho, _) in enumerate(aceites) if arq == rel
                             and any(o.start() <= m.start() and m.end() <= o.end()
                                     for o in re.finditer(re.escape(trecho), ln))]
                    if cobre:
                        usados.update(cobre)
                    else:
                        achados.append("%s:%d: %s" % (rel, n, m.group(0)))
    for i, (arq, trecho, _) in enumerate(aceites):
        if sem_uso and i not in usados:
            achados.append("lint-aceitos.tsv: o aceite de %s ('%s') não casou com nada; tire a linha" % (arq, trecho[:40]))
    return achados


# ── geração ──────────────────────────────────────────────────────────────────
def montar(arvore: Path, saida: Path, tag: str, commit: str) -> list[str]:
    dados = arvore / "scripts" / "starter"
    lista = [ln.strip() for ln in (dados / "lista.txt").read_text(encoding="utf-8").splitlines()
             if ln.strip() and not ln.startswith("#")]
    tabela = ler_openai(dados / "openai.tsv")
    modos = ler_modos(dados / "modos.tsv")
    for skill in modos:
        if skill not in lista:
            raise Falha(65, "modos.tsv cita %s, que não está na lista.txt" % skill)
    # O cabeçalho e o GERADO.txt de cada skill NÃO levam a tag: com ela, toda geração mudaria as 10 skills e o
    # version gate do starter pediria versão nova em todas (revisão do DESIGN, item 2). A tag fica só na raiz.
    cabecalho = (dados / "blocos" / "GENERATED.md").read_text(encoding="utf-8")
    migrar = (dados / "blocos" / "MIGRAR.md").read_text(encoding="utf-8")
    nota = "# GENERATED pelo sdd-open com scripts/gerar-starter.py — não edite aqui: edite no sdd-open e gere de novo."
    nota_raiz = "# GENERATED pelo sdd-open %s (commit %s) com scripts/gerar-starter.py — não edite aqui." % (tag, commit)
    fora = sorted(p.name for p in (arvore / ".agents" / "skills").iterdir() if p.is_dir() and p.name not in lista)

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
        if skill in modos:
            compor(origem, destino, *modos[skill])
        else:
            shutil.copytree(origem, destino)
        n_trocas = aplicar_trocas(destino, dados / "trocas" / ("%s.md" % skill))
        s = destino / "SKILL.md"
        gravar_se_mudou(s, sem_fluxo_encadeado(ler(s), skill))
        trazer_moldes(destino, moldes)
        for p in arquivos(destino):
            if eh_texto(p):
                gravar_se_mudou(p, reescrever(ler(p), skill, lista, moldes, p.suffix == ".md",
                                              p.name == "CHANGELOG.md"))
        s = destino / "SKILL.md"
        gravar_se_mudou(s, com_cabecalho(identificacao(ler(s), skill), skill, cabecalho, migrar))
        (destino / "agents").mkdir(exist_ok=True)
        (destino / "agents" / "openai.yaml").write_text(openai_yaml(tabela[skill]), encoding="utf-8")
        (destino / "GERADO.txt").write_bytes(lista_gerado(destino, nota))
        relatorio.append("✅ %s: %d arquivo(s), %d troca(s)%s" % (skill, len(arquivos(destino)) - 1, n_trocas,
                                                              ", de modo (%s)" % modos[skill][0] if skill in modos else ""))

    shutil.copytree(dados / "raiz", saida, dirs_exist_ok=True)
    achados = lint(saida, ler_aceites(dados / "lint-aceitos.tsv"), fora)
    if achados:
        raise Falha(65, "o lint do init achou %d citação(ões) a arquivo que só o init cria:\n  %s"
                    % (len(achados), "\n  ".join(achados)))
    infra = [p.relative_to(saida).as_posix() for p in arquivos(saida) if not p.relative_to(saida).parts[0] == "skills"]
    linhas = [nota_raiz]
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


def versao(skill_md: Path) -> tuple[str, str]:
    texto = skill_md.read_text(encoding="utf-8")
    v = re.search(r'^\s+version:\s*"?([0-9.]+)"?\s*$', texto, re.M)
    u = re.search(r'^\s+updated:\s*"?([0-9-]+)"?\s*$', texto, re.M)
    return (v.group(1) if v else ""), (u.group(1) if u else "")


def conferir_versoes(saida: Path, destino: Path) -> None:
    """O version gate do starter (check-versions.py --base) exige versão maior em toda skill que muda. Conferir
    aqui, antes de gravar, evita gerar algo que o CI de lá reprova."""
    erros = []
    for pasta in sorted((saida / "skills").iterdir()):
        antiga = destino / "skills" / pasta.name
        if not (antiga / "SKILL.md").is_file():
            continue
        # o que o git e o check-gerado.py não veem (lixo do Finder, cache do Python) não é mudança (rodada 6, R1)
        def lista(base: Path) -> list[str]:
            return sorted(p.relative_to(base).as_posix() for p in arquivos(base)
                          if p.name != ".DS_Store" and "__pycache__" not in p.parts and p.suffix != ".pyc")
        iguais = lista(pasta) == lista(antiga) and \
            all((pasta / r).read_bytes() == (antiga / r).read_bytes() for r in lista(pasta))
        if iguais:
            continue
        (vn, un), (va, ua) = versao(pasta / "SKILL.md"), versao(antiga / "SKILL.md")
        mn, ma = SEMVER.match(vn), SEMVER.match(va)
        if mn and ma and tuple(map(int, mn.groups())) <= tuple(map(int, ma.groups())):
            erros.append("%s: a cópia gerada mudou e a versão não subiu (%s no starter, %s no Open): suba a versão "
                         "da skill no Open" % (pasta.name, va, vn))
        if un and ua and un < ua:
            erros.append("%s: updated voltou no tempo (%s → %s)" % (pasta.name, ua, un))
    if erros:
        raise Falha(65, "o version gate do starter reprovaria:\n  " + "\n  ".join(erros))


# as mesmas pastas que o check-gerado.py confere inteiras (docs, exemplos e tests desde a F17b)
DONO_INTEIRO = ("scripts", ".github/workflows", "docs", "exemplos", "tests")


def gravar(saida: Path, destino: Path) -> None:
    # arquivo que saiu da semente sai do destino; senão a trava o acusaria como sobra (revisão, rodada 1, R2)
    for pasta in DONO_INTEIRO:
        for p in (arquivos(destino / pasta) if (destino / pasta).is_dir() else []):
            if not (saida / pasta / p.relative_to(destino / pasta)).is_file():
                p.unlink()
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
            lista = [ln.strip() for ln in (RAIZ_OPEN / "scripts/starter/lista.txt").read_text(encoding="utf-8").splitlines()
                     if ln.strip() and not ln.startswith("#")]
            fora = sorted(p.name for p in (RAIZ_OPEN / ".agents" / "skills").iterdir() if p.is_dir() and p.name not in lista)
            achados = lint(Path(a.lint), ler_aceites(RAIZ_OPEN / "scripts/starter/lint-aceitos.tsv"), fora, sem_uso=False)
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
            if not (arvore / "scripts" / "gerar-starter.py").is_file() or not (arvore / "scripts" / "starter").is_dir():
                raise Falha(64, "a tag %s não tem o gerador do starter (é anterior à F17): gere de uma tag que já o tenha"
                            % a.tag)   # rodada 6, R2: antes, traceback com exit 1
            if (arvore / "scripts" / "gerar-starter.py").read_bytes() != Path(__file__).read_bytes():
                raise Falha(64, "este gerador difere do que está na tag %s: rode o da tag, de uma worktree dela "
                                "(git worktree add --detach /tmp/open-%s %s && python3 /tmp/open-%s/scripts/gerar-starter.py "
                                "--tag %s <starter>)" % (a.tag, a.tag, a.tag, a.tag, a.tag))
            relatorio = montar(arvore, saida, a.tag, commit)
            conferir_versoes(saida, destino)
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
