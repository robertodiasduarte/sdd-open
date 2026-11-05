#!/usr/bin/env python3
"""design-lint.py — confere um DESIGN contra o template do sdd-open (sdd/templates/DESIGN_TEMPLATE.md).

Só stdlib, Python >= 3.9. Uso:
    python3 sdd/bin/design-lint.py <DESIGN.md>     # exit 0 = válido · 1 = violações · 64 = uso

Regras:
  - `## Key Decisions` presente, com ≥1 decisão; todo título `###` dentro dela é
    `### Decision N: <nome>`, com N = 1, 2, 3… em ordem. Outras ferramentas leem esses títulos:
    renomear (`### Decisão 1`, `### ADR-1`) quebra quem lê.
  - `## File Manifest` com ≥1 linha de dados (`| 1 | …`), `**Total Files:** N` igual ao número de
    linhas, e a última coluna (Dependencies) citando só linhas que existem, sem a própria linha e sem
    ciclo (`None`, `—` e vazio = sem dependência). Ciclo deixa o build sem ordem possível.
  - Com a seção `## LLM Prompts` (só existe quando o DEFINE tem o flag `true`): o subtítulo `### Inventário`
    com as colunas Tipo, Versão, Completeness e Refator de? e ≥1 linha; Tipo é one-shot ou loop; um bloco
    `#### Prompt N:` por linha, cada um com Autônomo?, Verification interna e Eval mínimo pré-ship
    preenchidos. Molde: sdd/templates/fragments/LLM_PROMPTS_DESIGN.md. DESIGN sem a seção não muda.
  - Nenhum placeholder do template fora de código: nome em MAIÚSCULAS entre chaves, ou prosa entre
    chaves (o template só usa chaves; « » é aspa comum em português). Bloco cercado por ``` e trecho
    entre crases não contam.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

CERCA = re.compile(r"^(```|~~~).*?^\1[^\n]*$", re.M | re.S)
CRASE = re.compile(r"`[^`\n]*`")
PLACEHOLDER = re.compile(r"\{[A-Z][A-Z0-9_]{2,}\}|\{[^{}\n]*\s[^{}\n]*\}")
DECISAO = re.compile(r"^### Decision (\d+): \S")
LINHA_MANIFEST = re.compile(r"^\|\s*(\d+)\s*\|")
TOTAL = re.compile(r"\*\*Total Files:\*\*\s*(\d+)")
COLUNAS_PROMPT = ("Tipo", "Versão", "Completeness", "Refator de?")
CAMPOS_PROMPT = ("Autônomo?", "Verification interna", "Eval mínimo pré-ship")
BLOCO_PROMPT = re.compile(r"^#### Prompt \d+\s*:")
FRASE_PROMPTS = "a seção de prompts está fora do formato, que mudou na v2.5.0; nada no código precisa mudar; faltam:"
# Variações do título contam ("(v1)", ": 1", negrito); outra seção que só começa igual ("LLM Prompt Injection") não.
TITULO_PROMPTS = re.compile(r"^##\s+(\d+(?:\.\d+)*\.?\s*)?\*{0,2}LLM\s+prompts?\*{0,2}(\s*$|\s*[(:]|\s+[—–-])", re.I)
# Começa como a seção (no plural) e traz palavras a mais ("LLM Prompts v2", "LLM prompts de produção"): antes o
# lint pulava a conferência em silêncio. O título sozinho não decide: "LLM Prompts Review" é outro assunto. Só
# reprova quando o corpo tem cara de inventário (ver parece_inventario).
TITULO_PROMPTS_QUASE = re.compile(r"^##\s+(\d+(?:\.\d+)*\.?\s*)?\*{0,2}LLM\s+prompts\b", re.I)
CHAVE = re.compile(r"\{[^{}\n]*\}")
CHAVE_MOLDE = re.compile(r"\{[^{}\n\"':]*\}")
VAZIO_OU_TRACO = re.compile(r"^[\s`*–—-]*$")
CAMPOS_LOOP = ("Intenção", "Perfil de risco dos efeitos", "Ground truth disponível")


def secao(linhas: list, titulo: str):
    """Linhas do título `## <titulo>` até o próximo `## `; None se o título não existe."""
    for i, ln in enumerate(linhas):
        if ln.strip() == "## " + titulo:
            fim = next((j for j in range(i + 1, len(linhas)) if linhas[j].startswith("## ")), len(linhas))
            return linhas[i + 1:fim]
    return None


def ciclo(deps: dict):
    """Uma linha que participa de ciclo, ou None."""
    estado = {}

    def visita(n):
        estado[n] = 1
        for d in deps.get(n, ()):
            if estado.get(d) == 1:
                return d
            if d not in estado:
                achou = visita(d)
                if achou is not None:
                    return achou
        estado[n] = 2
        return None

    for n in sorted(deps):
        if n not in estado:
            achou = visita(n)
            if achou is not None:
                return achou
    return None


def celulas(ln: str) -> list:
    return [c.strip() for c in re.split(r"(?<!\\)\|", ln.strip().strip("|"))]


def parece_inventario(linhas: list, inicio: int) -> bool:
    """A seção que começa em `inicio` tem o subtítulo, um bloco de contrato ou a coluna do inventário?"""
    fim = next((j for j in range(inicio + 1, len(linhas)) if linhas[j].startswith("## ")), len(linhas))
    for ln in linhas[inicio + 1:fim]:
        if ln.startswith("### Inventário") or BLOCO_PROMPT.match(ln):
            return True
        if ln.lstrip().startswith("|") and any(c in celulas(ln) for c in ("Completeness", "Refator de?")):
            return True
    return False


def lint_prompts(linhas: list) -> list:
    """Faltas do inventário de prompts: [] com a seção certa ou sem a seção."""
    inicio = next((i for i, ln in enumerate(linhas) if TITULO_PROMPTS.match(ln)), None)
    if inicio is None:
        for i, ln in enumerate(linhas):
            if TITULO_PROMPTS_QUASE.match(ln) and parece_inventario(linhas, i):
                return [FRASE_PROMPTS, "  o título '%s' tem palavras a mais e a seção traz um inventário de prompts: "
                        "use só '## LLM Prompts' para ela ser conferida" % ln.strip()]
        return []
    fim_secao = next((j for j in range(inicio + 1, len(linhas)) if linhas[j].startswith("## ")), len(linhas))
    corpo = linhas[inicio + 1:fim_secao]
    faltas = []
    i_inv = next((i for i, ln in enumerate(corpo) if ln.startswith("### Inventário")), None)
    if i_inv is None:
        faltas.append("falta o subtítulo ### Inventário")
        return [FRASE_PROMPTS] + ["  " + f for f in faltas]
    fim = next((j for j in range(i_inv + 1, len(corpo)) if corpo[j].startswith("### ")), len(corpo))
    # Só a 1ª tabela: linhas seguidas, a partir da primeira.
    tabela = []
    for ln in corpo[i_inv + 1:fim]:
        if ln.lstrip().startswith("|"):
            tabela.append(ln)
        elif tabela:
            break
    n_linhas = 0
    tipos = []
    if not tabela:
        faltas.append("o inventário não tem tabela")
    else:
        cabecalho = celulas(tabela[0])
        faltas += ["falta a coluna %s no inventário" % c for c in COLUNAS_PROMPT if c not in cabecalho]
        dados = [ln for ln in tabela[1:] if not re.fullmatch(r"[\s|:-]+", ln)]
        n_linhas = len(dados)
        if not dados:
            faltas.append("o inventário não tem nenhuma linha de prompt")
        if "Tipo" in cabecalho:
            coluna = cabecalho.index("Tipo")
            for n, ln in enumerate(dados, 1):
                cels = celulas(ln)
                valor = cels[coluna].strip("`") if coluna < len(cels) else ""
                if any(CHAVE.search(c) for c in cels):
                    faltas.append("linha %d do inventário com o que está entre chaves sem preencher" % n)
                tipos.append(valor)
                if valor not in ("one-shot", "loop"):
                    faltas.append("linha %d do inventário com Tipo '%s' (esperado one-shot ou loop)" % (n, valor))
    blocos = [i for i, ln in enumerate(corpo) if BLOCO_PROMPT.match(ln)]
    for k, i in enumerate(blocos):
        fim_bloco = next((j for j in range(i + 1, len(corpo)) if corpo[j].startswith(("#### ", "### "))), len(corpo))
        trecho = corpo[i + 1:fim_bloco]
        titulo = corpo[i].lstrip("# ").split(":")[0]
        campos = CAMPOS_PROMPT + (CAMPOS_LOOP if k < len(tipos) and tipos[k] == "loop" else ())
        for campo in campos:
            achado = [celulas(ln) for ln in trecho
                      if ln.lstrip().startswith("|") and celulas(ln)[0].strip("*") == campo]
            if achado and len(achado[0]) >= 2 and CHAVE.search(achado[0][1]):
                faltas.append("%s com %s sem preencher" % (titulo, campo))
            elif not achado or len(achado[0]) < 2 or VAZIO_OU_TRACO.match(achado[0][1]):
                faltas.append("%s sem o campo %s" % (titulo, campo))
        # Qualquer outra linha do contrato com chaves no valor (também entre crases) é molde sem preencher.
        for ln in trecho:
            if not ln.lstrip().startswith("|"):
                continue
            cels = celulas(ln)
            nome = cels[0].strip("*") if cels else ""
            # Só o molde conta: `{"nota": 0}`, um JSON preenchido, é valor legítimo.
            if len(cels) >= 2 and nome not in campos and nome and CHAVE_MOLDE.search(cels[1]):
                faltas.append("%s com %s sem preencher" % (titulo, nome))
    if tabela and n_linhas and len(blocos) != n_linhas:
        faltas.append("são %d linha(s) no inventário e %d bloco(s) de contrato" % (n_linhas, len(blocos)))
    return [FRASE_PROMPTS] + ["  " + f for f in faltas] if faltas else []


def lint(texto: str) -> list:
    erros = []
    linhas = CERCA.sub("", texto).splitlines()
    prompts = lint_prompts(linhas)
    erros += prompts

    decisoes = secao(linhas, "Key Decisions")
    if decisoes is None:
        erros.append("falta a seção ## Key Decisions")
    else:
        numeros = []
        for ln in decisoes:
            if ln.startswith("### "):
                m = DECISAO.match(ln)
                if m:
                    numeros.append(int(m.group(1)))
                else:
                    erros.append(f"título fora do padrão '### Decision N: <nome>': {ln.strip()}")
        if not numeros and not any(ln.startswith("### ") for ln in decisoes):
            erros.append("## Key Decisions sem nenhuma '### Decision N: <nome>'")
        if numeros and numeros != list(range(1, len(numeros) + 1)):
            erros.append(f"decisões fora de sequência: {numeros} (esperado 1..{len(numeros)})")

    manifest = secao(linhas, "File Manifest")
    if manifest is None:
        erros.append("falta a seção ## File Manifest")
    else:
        deps = {}
        for ln in manifest:
            m = LINHA_MANIFEST.match(ln)
            if m:
                celulas = [c.strip() for c in ln.strip().strip("|").split("|")]
                deps[int(m.group(1))] = [int(x) for x in re.findall(r"\d+", celulas[-1])] if len(celulas) > 1 else []
        if not deps:
            erros.append("## File Manifest sem nenhuma linha de arquivo")
        total = TOTAL.search("\n".join(manifest))
        if not total:
            erros.append("## File Manifest sem a linha **Total Files:** N")
        elif deps and int(total.group(1)) != len(deps):
            erros.append(f"**Total Files:** {total.group(1)}, mas o manifest tem {len(deps)} linhas")
        for n, ds in sorted(deps.items()):
            for d in ds:
                if d == n:
                    erros.append(f"linha {n} do manifest depende de si mesma")
                elif d not in deps:
                    erros.append(f"linha {n} do manifest depende da linha {d}, que não existe")
        validas = {n: [d for d in ds if d in deps and d != n] for n, ds in deps.items()}
        c = ciclo(validas)
        if c is not None:
            erros.append(f"dependências do manifest formam ciclo (passa pela linha {c})")

    for n, ln in enumerate(CRASE.sub("", CERCA.sub(lambda m: "\n" * m.group(0).count("\n"), texto)).splitlines(), 1):
        m = PLACEHOLDER.search(ln)
        if m:
            erros.append(f"linha {n}: placeholder do template sem preencher: {m.group(0)}")
    return erros


def main(argv: list) -> int:
    if len(argv) != 2 or not Path(argv[1]).is_file():
        print("uso: design-lint.py <DESIGN.md>", file=sys.stderr)
        return 64
    try:
        texto = Path(argv[1]).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        print(f"🛑 {argv[1]}: não consegui ler: {e}", file=sys.stderr)
        print("RESULTADO: VERMELHO", file=sys.stderr)
        print("→ confira a permissão e a codificação (UTF-8) do arquivo e rode de novo", file=sys.stderr)
        return 1
    erros = lint(texto)
    for e in erros:
        print(f"🛑 {argv[1]}: {e}", file=sys.stderr)
    if erros:
        print("RESULTADO: VERMELHO", file=sys.stderr)
        if FRASE_PROMPTS in erros:
            outros = [e for e in erros if e != FRASE_PROMPTS and not e.startswith("  ")]
            print("→ copie as colunas e os campos de sdd/templates/fragments/LLM_PROMPTS_DESIGN.md"
                  + ("; corrija também os outros pontos acima" if outros else ""), file=sys.stderr)
        else:
            print("→ corrija o DESIGN nos pontos acima (molde: sdd/templates/DESIGN_TEMPLATE.md) e rode de novo",
                  file=sys.stderr)
        return 1
    print(f"✅ {argv[1]}: DESIGN válido")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
