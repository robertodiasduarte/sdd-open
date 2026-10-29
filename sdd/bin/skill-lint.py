#!/usr/bin/env python3
"""skill-lint.py — valida um SKILL.md contra a spec Agent Skills (agentskills.io/specification).

Só stdlib. Uso:
    python3 sdd/bin/skill-lint.py <caminho/SKILL.md> [...]      # exit 0 = todos válidos · 1 = algum inválido
    python3 sdd/bin/skill-lint.py --conversa <SKILL.md> [...]   # também a camada de conversa · 64 = uso

Regras verificadas:
  - frontmatter YAML na linha 1 (`---` ... `---`), chaves simples `nome: valor`
  - name: obrigatório, 1–64 chars, ^[a-z0-9]+(-[a-z0-9]+)*$, igual ao nome da pasta
  - description: obrigatória, 1–1024 chars, não vazia
  - compatibility (opcional): ≤500 chars
  - corpo ≤500 linhas (recomendação da spec — aviso, não erro; use references/)
Linhas de comentário `#` dentro do frontmatter são ignoradas (é onde o sdd-open marca cópias geradas).

Com --conversa (o CI do pacote liga; skill própria do usuário não precisa da camada):
  - seção `## Como falar com o aluno`, uma vez só, com a tabela de etapas (coluna `Etapa`) e as 5 partes
    da resposta: **Status**, **O que foi feito**, **Agora…**, **Sua decisão**, **Próximo passo**
  - se a seção manda ler `references/como-falar.md`, o arquivo existe ao lado do SKILL.md
  - em cada pergunta de decisão desse arquivo (negrito terminado em `?` seguido de opções `- **rótulo**`):
    exatamente 1 opção `(recomendado)`, e ela é a primeira; a opção **não sei**; nenhuma opção **Outro**
    (formato em sdd/templates/fragments/PERGUNTA_DECISAO.md). Pergunta aberta, sem opções, não é conferida
  - o arquivo tem ≥1 pergunta de decisão, e cada `**Próximo passo**` de exemplo cabe em 100 caracteres
"""
import os
import re
import sys

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
SECAO = "## Como falar com o aluno"
PARTES = ("**Status**", "**O que foi feito**", "**Agora", "**Sua decisão**", "**Próximo passo**")
CERCA = re.compile(r"^(```|~~~).*?^\1[^\n]*$", re.M | re.S)
PERGUNTA = re.compile(r"\*\*[^*\n]*\?\*\*")
OPCAO = re.compile(r"^\s*-\s+\*\*([^*\n]+)\*\*(.*)$")
CONTINUACAO = re.compile(r"^\s+\S")
PROXIMO = re.compile(r"^\*\*Próximo passo\*\*[\s:—–-]*(.*)$")


def parse_frontmatter(text):
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, "frontmatter ausente: a linha 1 deve ser '---'"
    fm, i = {}, 1
    chave_atual = None
    while i < len(lines):
        ln = lines[i]
        if ln.strip() == "---":
            return fm, None
        if ln.strip().startswith("#") or not ln.strip():
            i += 1
            continue
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)$", ln)
        if m and not ln.startswith(" "):
            chave_atual = m.group(1)
            val = m.group(2).strip()
            # Plain scalar (sem aspas, sem >- / |) com ': ' ou ' #' dentro é YAML INVÁLIDO
            # ("mapping values are not allowed here") — o skills-ref e o PyYAML rejeitam; o
            # agente não carrega a skill. Achado do avaliador fresco em 2026-09-05.
            if val and val[0] not in '"\'>|' and (": " in val or " #" in val):
                return None, f"linha {i + 1}: valor de '{chave_atual}' contém ': ' ou ' #' sem aspas — YAML inválido; use aspas ou o bloco >-"
            fm[chave_atual] = val.strip('"').strip("'").lstrip(">|-").strip()
        elif chave_atual and ln.startswith(" "):
            # continuação de valor multi-linha (description longa) ou mapa aninhado (metadata)
            fm[chave_atual] = (fm[chave_atual] + " " + ln.strip()).strip()
        else:
            return None, f"linha {i + 1} do frontmatter não é 'chave: valor': {ln!r}"
        i += 1
    return None, "frontmatter sem '---' de fechamento"


def yaml_real(text):
    """Se PyYAML existir, parse de verdade do frontmatter (a confirmação mais forte)."""
    try:
        import yaml  # noqa
    except ImportError:
        return None
    partes = text.split("\n---", 2)
    bloco = text.splitlines()
    fim = next((i for i in range(1, len(bloco)) if bloco[i].strip() == "---"), None)
    if fim is None:
        return "frontmatter sem fechamento"
    try:
        yaml.safe_load("\n".join(bloco[1:fim]))
    except Exception as e:  # noqa
        return f"PyYAML rejeitou o frontmatter: {str(e).splitlines()[0]}"
    return None


def lint(path):
    erros, avisos = [], []
    try:
        text = open(path, encoding="utf-8").read()
    except OSError as e:
        return [f"não consegui ler: {e}"], []
    fm, err = parse_frontmatter(text)
    if err:
        return [err], []
    ye = yaml_real(text)
    if ye:
        return [ye], []
    pasta = os.path.basename(os.path.dirname(os.path.abspath(path)))
    name = fm.get("name", "")
    if not name:
        erros.append("name: obrigatório")
    else:
        if not (1 <= len(name) <= 64):
            erros.append(f"name: {len(name)} chars (limite 64)")
        if not NAME_RE.match(name):
            erros.append(f"name: {name!r} — só minúsculas, dígitos e hífens simples, sem começar/terminar com hífen")
        if name != pasta:
            erros.append(f"name: {name!r} difere do nome da pasta {pasta!r}")
    desc = fm.get("description", "")
    if not desc.strip():
        erros.append("description: obrigatória e não vazia")
    elif len(desc) > 1024:
        erros.append(f"description: {len(desc)} chars (limite 1024)")
    comp = fm.get("compatibility", "")
    if comp and len(comp) > 500:
        erros.append(f"compatibility: {len(comp)} chars (limite 500)")
    n_linhas = len(text.splitlines())
    if n_linhas > 500:
        avisos.append(f"{n_linhas} linhas — a spec recomenda ≤500; mova detalhe para references/")
    return erros, avisos


def perguntas(texto):
    """[(linha, pergunta, [(rótulo, resto)])] das perguntas de decisão, fora de bloco de código."""
    linhas = [ln[2:] if ln.startswith("> ") else ln for ln in CERCA.sub("", texto).splitlines()]
    saida = []
    for i, ln in enumerate(linhas):
        m = PERGUNTA.findall(ln)
        if not m:
            continue
        opcoes, j = [], i + 1
        while j < len(linhas):
            o = OPCAO.match(linhas[j])
            if o:
                opcoes.append((o.group(1).strip(), o.group(2)))
            elif not (opcoes and CONTINUACAO.match(linhas[j])):
                break  # linha recuada logo depois de uma opção é a continuação dela
            j += 1
        if opcoes:
            saida.append((i + 1, m[-1], opcoes))
    return saida


def lint_conversa(path, text):
    erros = []
    linhas = text.splitlines()
    inicios = [i for i, ln in enumerate(linhas) if ln.strip() == SECAO]
    if not inicios:
        return [f"seção '{SECAO}' ausente (a camada de conversa; ver sdd/templates/fragments/PERGUNTA_DECISAO.md)"]
    if len(inicios) > 1:
        erros.append(f"seção '{SECAO}' repetida ({len(inicios)} vezes)")
    fim = next((i for i in range(inicios[0] + 1, len(linhas)) if linhas[i].startswith("## ")), len(linhas))
    secao = "\n".join(linhas[inicios[0]:fim])
    if not re.search(r"(?m)^\|\s*Etapa\s*\|", secao):
        erros.append("seção sem a tabela de etapas (coluna 'Etapa')")
    for parte in PARTES:
        if parte not in secao:
            erros.append(f"seção sem a parte {parte}{'**' if not parte.endswith('**') else ''}")
    if "references/como-falar.md" not in secao:
        return erros
    ref = os.path.join(os.path.dirname(os.path.abspath(path)), "references", "como-falar.md")
    if not os.path.isfile(ref):
        return erros + ["a seção manda ler references/como-falar.md, e o arquivo não existe"]
    try:
        texto_ref = open(ref, encoding="utf-8").read()
    except (OSError, UnicodeDecodeError) as e:
        return erros + [f"não consegui ler references/como-falar.md: {e}"]
    achadas = perguntas(texto_ref)
    if not achadas:
        erros.append("references/como-falar.md sem nenhuma pergunta de decisão (negrito com '?' seguido de opções)")
    for n, pergunta, opcoes in achadas:
        onde = f"references/como-falar.md:{n} {pergunta}"
        rec = [k for k, (rotulo, resto) in enumerate(opcoes) if "(recomendado)" in (rotulo + resto).lower()]
        if not rec:
            erros.append(f"{onde} — nenhuma opção (recomendado)")
        elif len(rec) > 1:
            erros.append(f"{onde} — {len(rec)} opções (recomendado); deve haver exatamente 1")
        elif rec[0] != 0:
            erros.append(f"{onde} — a opção (recomendado) não é a primeira")
        rotulos = [r.lower() for r, _ in opcoes]
        if "não sei" not in rotulos:
            erros.append(f"{onde} — sem a opção **não sei**")
        if any(r in ("outro", "outra", "other") for r in rotulos):
            erros.append(f"{onde} — tem a opção **Outro**: resposta fora das opções é tratada como dúvida")
    for n, ln in enumerate(CERCA.sub("", texto_ref).splitlines(), 1):
        m = PROXIMO.match(ln.strip())
        if m and len(m.group(1).strip()) > 100:
            erros.append(f"references/como-falar.md:{n} **Próximo passo** com {len(m.group(1).strip())} caracteres (limite 100)")
    return erros


def main(argv):
    args = argv[1:]
    conversa = "--conversa" in args
    args = [a for a in args if a != "--conversa"]
    desconhecidas = [a for a in args if a.startswith("--")]
    if not args or desconhecidas:
        if desconhecidas:
            print(f"skill-lint: opção desconhecida: {desconhecidas[0]}", file=sys.stderr)
        print("uso: skill-lint.py [--conversa] <SKILL.md> [...]", file=sys.stderr)
        return 64
    falhou = False
    for p in args:
        erros, avisos = lint(p)
        if conversa and not erros:
            erros = lint_conversa(p, open(p, encoding="utf-8").read())
        for a in avisos:
            print(f"⚠️  {p}: {a}")
        if erros:
            falhou = True
            for e in erros:
                print(f"🛑 {p}: {e}", file=sys.stderr)
        else:
            print(f"✅ {p}: frontmatter válido" + (" · camada de conversa ok" if conversa else ""))
    if falhou:
        print("RESULTADO: VERMELHO", file=sys.stderr)
        print("→ corrija o apontado acima (frontmatter: agentskills.io/specification; conversa: "
              "sdd/templates/fragments/PERGUNTA_DECISAO.md)", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
