#!/usr/bin/env python3
"""skill-lint.py — valida um SKILL.md contra a spec Agent Skills (agentskills.io/specification).

Só stdlib. Uso:
    python3 sdd/bin/skill-lint.py <caminho/SKILL.md> [...]      # exit 0 = todos válidos · 1 = algum inválido

Regras verificadas:
  - frontmatter YAML na linha 1 (`---` ... `---`), chaves simples `nome: valor`
  - name: obrigatório, 1–64 chars, ^[a-z0-9]+(-[a-z0-9]+)*$, igual ao nome da pasta
  - description: obrigatória, 1–1024 chars, não vazia
  - compatibility (opcional): ≤500 chars
  - corpo ≤500 linhas (recomendação da spec — aviso, não erro; use references/)
Linhas de comentário `#` dentro do frontmatter são ignoradas (é onde o sdd-open marca cópias geradas).
"""
import os
import re
import sys

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


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


def main(argv):
    if len(argv) < 2:
        print("uso: skill-lint.py <SKILL.md> [...]", file=sys.stderr)
        return 64
    falhou = False
    for p in argv[1:]:
        erros, avisos = lint(p)
        for a in avisos:
            print(f"⚠️  {p}: {a}")
        if erros:
            falhou = True
            for e in erros:
                print(f"🛑 {p}: {e}", file=sys.stderr)
        else:
            print(f"✅ {p}: frontmatter válido")
    if falhou:
        print("RESULTADO: VERMELHO", file=sys.stderr)
        print("→ corrija o frontmatter apontado acima (spec: agentskills.io/specification)", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
