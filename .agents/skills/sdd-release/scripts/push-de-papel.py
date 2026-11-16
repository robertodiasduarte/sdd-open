#!/usr/bin/env python3
"""push-de-papel.py — um push só com estes arquivos dispara um workflow que publica?

Responde à linha "O commit de papel publica?" do bloco do OK da sdd-release. O commit de papel leva a ficha, o
changelog, a entrada da fila da curadoria e o arquivamento; num projeto em que todo push na branch padrão publica,
ele dispara um deploy sem código novo. Só lê <raiz>/.github/workflows/; não executa nada nem acessa a rede. O
leitor de YAML e o reconhecimento do passo que publica são os do deploy-espera-testes.py, ao lado.

  PUBLICA      exit 0  algum workflow que publica roda com um push desses arquivos na branch
  NAO_PUBLICA  exit 1  nenhum workflow que publica roda (paths, paths-ignore ou branches deixam de fora)
  NAO_SEI      exit 2  workflow ilegível, workflow_run, workflow reutilizável, filtro que não sei ler, ou job com
                       nome de publicar cujo passo não reconheci — a skill diz "não consegui afirmar"
               exit 64 uso, ou o deploy-espera-testes.py não está ao lado (nunca NAO_PUBLICA por falta dele)

Uso:
    python3 .agents/skills/sdd-release/scripts/push-de-papel.py [raiz] --branch <branch padrão> <arquivo> [<arquivo>…]
Os arquivos são caminhos relativos à raiz, com /. Python >= 3.9, só stdlib.
"""
import importlib.util
import os
import re
import sys

USO = "uso: push-de-papel.py [raiz] --branch <branch padrão> <arquivo> [<arquivo>…]"
TRECHO = "paths-ignore: ['sdd/**', '**/*.md']"


def carrega_vizinho():
    caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), "deploy-espera-testes.py")
    if not os.path.isfile(caminho):
        return None
    spec = importlib.util.spec_from_file_location("deploy_espera_testes", caminho)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def glob_para_regex(p):
    """Glob dos filtros do GitHub Actions: * não passa de /, ** passa, ? é 1 caractere."""
    out, i = [], 0
    while i < len(p):
        if p.startswith("**", i):
            i += 2
            if p.startswith("/", i):
                i += 1
                out.append("(?:.*/)?")
            else:
                out.append(".*")
        elif p[i] == "*":
            out.append("[^/]*")
            i += 1
        elif p[i] == "?":
            out.append("[^/]")
            i += 1
        elif p[i] in "[]{}":
            raise ValueError("padrão com %s não suportado: %s" % (p[i], p))
        else:
            out.append(re.escape(p[i]))
            i += 1
    return re.compile("^" + "".join(out) + "$")


def casa(item, padroes):
    """O último padrão que casa decide; "!" nega (a regra do GitHub Actions para paths e branches)."""
    r = False
    for p in padroes:
        neg = p.startswith("!")
        if glob_para_regex(p[1:] if neg else p).match(item):
            r = not neg
    return r


def lista(v):
    if v is None:
        return None
    if isinstance(v, list):
        return [str(x) for x in v]
    return [str(v)]


def dispara(ev, branch, arquivos):
    """True/False para um evento push com os filtros dele; ValueError quando o filtro não é legível."""
    if ev is None or ev == "" or ev == {}:
        return True
    if not isinstance(ev, dict):
        raise ValueError("filtro do push num formato que não sei ler")
    br, br_ig = lista(ev.get("branches")), lista(ev.get("branches-ignore"))
    tags = lista(ev.get("tags"))
    if br is not None and br_ig is not None:
        raise ValueError("branches e branches-ignore no mesmo push")
    if br is None and br_ig is None and tags is not None:
        return False  # só tags: um push de branch não roda
    if br is not None and not casa(branch, br):
        return False
    if br_ig is not None and casa(branch, br_ig):
        return False
    pa, pa_ig = lista(ev.get("paths")), lista(ev.get("paths-ignore"))
    if pa is not None and pa_ig is not None:
        raise ValueError("paths e paths-ignore no mesmo push")
    if pa is not None:
        return any(casa(a, pa) for a in arquivos)
    if pa_ig is not None:
        return any(not casa(a, pa_ig) for a in arquivos)
    return True


def evento_push(wf):
    """(tem_push, filtros, workflow_run)."""
    on = wf.get("on", wf.get("true"))
    if isinstance(on, dict):
        return "push" in on, on.get("push"), "workflow_run" in on
    nomes = set(str(x) for x in on) if isinstance(on, list) else ({str(on)} if on else set())
    return "push" in nomes, None, "workflow_run" in nomes


def avaliar(raiz, branch, arquivos, mod):
    pasta = os.path.join(raiz, ".github", "workflows")
    arqs = sorted(f for f in os.listdir(pasta) if f.endswith((".yml", ".yaml"))) if os.path.isdir(pasta) else []
    achados = []
    for arq in arqs:
        try:
            with open(os.path.join(pasta, arq), encoding="utf-8", errors="replace") as fh:
                wf = mod.carregar(fh.read())
        except (mod.Ilegivel, OSError) as e:
            achados.append(("NAO_SEI", "não consegui ler %s (%s)" % (arq, e)))
            continue
        if not isinstance(wf, dict):
            achados.append(("NAO_SEI", "não consegui ler %s" % arq))
            continue
        jobs = wf.get("jobs") if isinstance(wf.get("jobs"), dict) else {}
        publica = [jid for jid, j in jobs.items() if isinstance(j, dict) and any(mod.publica(s) for s in mod.passos(j))]
        reusa = [jid for jid, j in jobs.items() if isinstance(j, dict) and j.get("uses")]
        suspeito = [jid for jid, j in jobs.items() if isinstance(j, dict) and jid not in publica
                    and mod.PARECE_PUBLICAR.search(jid + " " + str(j.get("name") or ""))]
        if not publica and not reusa and not suspeito and not mod.PARECE_PUBLICAR.search(arq + " " + str(wf.get("name") or "")):
            continue  # não publica: um push que o dispara não importa aqui
        tem_push, filtros, wf_run = evento_push(wf)
        if wf_run:
            achados.append(("NAO_SEI", "%s roda por workflow_run: depende de outro workflow que não avalio daqui" % arq))
            continue
        if not tem_push:
            continue
        try:
            roda = dispara(filtros, branch, arquivos)
        except ValueError as e:
            achados.append(("NAO_SEI", "%s: %s" % (arq, e)))
            continue
        if not roda:
            achados.append(("NAO_PUBLICA", "%s não roda com estes arquivos (os filtros do push os deixam de fora)" % arq))
        elif publica:
            achados.append(("PUBLICA", "%s roda com o push na %s e publica (job %s)" % (arq, branch, ", ".join(publica))))
        else:
            achados.append(("NAO_SEI", "%s roda com o push na %s; o job %s tem nome de publicar ou chama outro "
                            "workflow, e não reconheci o passo" % (arq, branch, ", ".join(reusa + suspeito) or "(nenhum)")))
    for res in ("PUBLICA", "NAO_SEI"):
        sel = [f for r, f in achados if r == res]
        if sel:
            return res, sel, achados
    return "NAO_PUBLICA", [f for r, f in achados if r == "NAO_PUBLICA"], achados


def main(argv):
    args = argv[1:]
    if any(a in ("-h", "--help") for a in args):
        print(__doc__.strip())
        return 0
    raiz = "."
    if args and not args[0].startswith("--"):
        raiz, args = args[0], args[1:]
    if len(args) < 3 or args[0] != "--branch" or not args[1]:
        print(USO, file=sys.stderr)
        return 64
    branch = args[1]
    arquivos = [a.replace("\\", "/") for a in args[2:]]
    arquivos = [a[2:] if a.startswith("./") else a for a in arquivos]
    if not os.path.isdir(raiz):
        print("🛑 %s não é uma pasta" % raiz, file=sys.stderr)
        print(USO, file=sys.stderr)
        return 64
    mod = carrega_vizinho()
    if mod is None:
        print("🛑 não achei o deploy-espera-testes.py ao lado deste script: sem ele, não sei o que publica",
              file=sys.stderr)
        print("RESULTADO: ERRO DE USO")
        print("→ atualize o pacote (o upgrade traz os dois juntos); nada foi avaliado.")
        return 64
    res, frases, todos = avaliar(raiz, branch, arquivos, mod)
    for r, f in todos:
        print({"PUBLICA": "🚀", "NAO_PUBLICA": "✅", "NAO_SEI": "❓"}[r] + " " + f)
    if res == "PUBLICA":
        resposta = ("sim — " + "; ".join(frases) + ". Recomendo tirar os documentos do gatilho do deploy, no "
                    "evento push do workflow: " + TRECHO)
    elif res == "NAO_SEI":
        resposta = "não consegui afirmar — " + "; ".join(frases)
    elif frases:
        resposta = "não — " + "; ".join(frases)
    else:
        resposta = "não — nenhum workflow que publica roda com um push na %s" % branch
    print("RESULTADO: " + res)
    print("→ O commit de papel publica? " + resposta)
    return {"PUBLICA": 0, "NAO_PUBLICA": 1, "NAO_SEI": 2}[res]


if __name__ == "__main__":
    # No Windows, o stdout num pipe (o Git Bash do aluno) é cp1252 e o print troca \n por \r\n (LM-015).
    for _canal in (sys.stdout, sys.stderr):
        try:
            _canal.reconfigure(encoding="utf-8", errors="replace", newline="\n")
        except (AttributeError, ValueError):
            pass
    sys.exit(main(sys.argv))
