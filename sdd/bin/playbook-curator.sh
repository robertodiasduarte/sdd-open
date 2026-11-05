#!/usr/bin/env bash
# playbook-curator.sh — curadoria do sdd/playbook.md (papel Curator do ACE): colhe dos documentos da
# feature o que ajudou e o que mordeu, aplica um delta APROVADO, cruza o delta com sdd/invariants.md,
# trava o par playbook + invariantes e confere o bloco que o curador (agente de contexto fresco)
# devolveu. Este script nunca decide: quem julga é o curador (brief em
# .agents/skills/sdd-playbook/references/curator.md) e quem decide a mudança de regra é a pessoa, no
# passo 17b da sdd-release. Explicação longa: docs/playbook-curation.md.
#
# Uso:
#   playbook-curator.sh --preparar <FEATURE> [--retomar]                      # exit 0 | 1 (sem documentos) | 2 | 64
#   playbook-curator.sh --colher <dir> <playbook> [--desde AAAA-MM-DD] [--inv <invariantes>]
#                                                                             # exit 0 | 1 (nada) | 2 | 64
#   playbook-curator.sh --aplicar <delta> <playbook> [conf=AAAA-MM-DD]        # stdout = playbook novo; 0 | 2 | 64
#   playbook-curator.sh --cruzar <delta|-> <playbook> <invariantes>           # 0 nada · 3 avisos · 2 inválido
#   playbook-curator.sh --validar-inv <playbook> <invariantes>                # a trava; 0 | 2
#   playbook-curator.sh --aplicar-inv <linhas> <invariantes>                  # stdout = invariantes novas; 0 | 2
#   playbook-curator.sh --selar <staging>                                     # stdout = selo (sha256 por arquivo)
#   playbook-curator.sh --conferir-bloco <colheita> <bloco> <playbook> <selo> <comparar>   # 0 | 2
#   playbook-curator.sh --self-test                                           # vermelhos antes dos verdes; 0 | 2
#
# --preparar copia (nunca move) para <temp>/sdd-curadoria-<hash da raiz>/<FEATURE>/ os documentos da
#   feature: DESIGN, BUILD_REPORT, AVAL*-*.log da evidência, AVALIACAO, ledger e HANDOFF. Só arquivo
#   regular, nunca link; procura também em sdd/archive/<FEATURE>/. Limpa o que sobrou da release anterior;
#   --retomar não copia nem limpa: só diz se há colheita na pasta (sessão nova depois da parada do curador).
# --colher lê só o nível de cima de <dir>:
#   DESIGN_*.md / BUILD_REPORT_*.md → seções "Landmines aplicáveis" / "Landmines lidas no build": a tabela é lida
#     pelo cabeçalho: o ID vem da coluna Fonte, LM-nnn ou ID, e o veredito da coluna Veredito ou Tratamento (começa
#     com ✔ ⇒ ajudou+1; com "mordeu" ⇒ mordeu+1). Sem esse cabeçalho, não conta nada: TABELA_SEM_CABECALHO.
#   AVAL*-*.log · AVALIACAO_*.md · *.yaml · BUILD_REPORT_*.md · HANDOFF_*.md → linha de achado (❌,
#     NEEDS_WORK, FAIL como palavra, WAIVED, mordeu_antes:) sem ✅: com LM-nnn ⇒ mordeu+1; sem LM e com
#     um termo de sup: (6+ caracteres, não só dígitos) ⇒ SUGESTAO (nunca delta)
#   BUILD_REPORT_*.md · HANDOFF_*.md → blocos de candidato ⇒ CANDIDATO (próximo ID) ou REJEITADO
#   <playbook> → ativo com mordeu >= 2 e promovido_para: — ⇒ PROMOVER? (pergunta obrigatória)
#   Cada linha julgável leva `fp=<10 hex>` (impressão do arquivo, do ID e do texto da linha). O que estiver
#   em <dir>/CURATOR-colhidos.txt (as colheitas já julgadas desta feature) não conta de novo: JA_JULGADO.
#   Exit 0 = há pelo menos 1 linha para julgar ou relatar; 1 = nada, de nenhum tipo.
#   Trace: 1 linha JSONL por feature em ${SDD_TRACE_DIR:-sdd/traces}/<FEATURE>.jsonl, com ts, feature, src,
#   kind, exit e os 7 contadores; SDD_TRACE=off desliga.
# --conferir-bloco reprova o bloco quando a fronteira de escrita não saiu verde (<comparar> é o stdout do
#   governanca-fronteira.sh --comparar), quando o staging mudou depois do --selar, quando falta linha da
#   colheita, e quando um AUTO não é igual (ID, verbo, +1 e arquivo:linha) a uma linha DELTA da colheita.
# Gramática do delta (1 verbo por linha; # comenta; tudo é validado antes de qualquer edição):
#   LM-020 ajudou+1 · LM-016 mordeu+1 · LM-004 promovido_para=<caminho>
#   ADD <seção> :: sup: `t1` `t2` :: regra. **Do instead:** ação. → ficha: x · promovido_para: —
#   TOMBSTONE LM-nnn :: motivo · REFINE LM-nnn :: novo texto depois de ::
# Gramática das invariantes (sdd/invariants.md, 1 linha por regra, sob "## Invariantes"):
#   - [INV-NNN] estado=ok|auto|humano origem=seed|LM-nnn[,LM-mmm] [check=<caminho>] :: <regra> · por quê: <texto> [· tarefa: … | · motivo: …]
#   e, sob "## Descartados":  - [LM-nnn] descartado :: <motivo>
#
# Exit: 0 ok · 1 nada a colher · 2 arquivo, delta, par ou bloco inválido (ou self-test falhou) ·
#       3 --cruzar com aviso · 64 uso. O programa Python chega pelo stdin: `--cruzar -` guarda o delta num
#       arquivo temporário antes.
# Compat: bash 3.2 + python3 >= 3.9, só stdlib. Não exige repositório git (o --self-test cria um temporário
# para chamar o playbook-lint.sh, que exige). Seções: PLAYBOOK_SECTIONS, com o mesmo default do playbook-lint.sh.
set -uo pipefail

if ! command -v python3 >/dev/null 2>&1; then
  echo "🛑 playbook-curator: python3 não encontrado no PATH." >&2
  printf 'RESULTADO: ERRO DE USO\n→ instale o Python 3.9 ou mais novo e rode de novo; nada foi lido nem gravado.\n' >&2
  exit 64
fi

# O programa Python chega pelo stdin; por isso o delta de `--cruzar -` é guardado antes num arquivo.
TMPIN=""
if [ "${1:-}" = "--cruzar" ] && [ "${2:-}" = "-" ]; then
  TMPIN="$(mktemp 2>/dev/null || mktemp -t pbcur)" || exit 64
  cat > "${TMPIN}"
  shift 2
  set -- --cruzar "${TMPIN}" ${1+"$@"}
fi

SDD_CURATOR_SELF="$0" SDD_CURATOR_BASH="${BASH:-bash}" python3 -B - ${1+"$@"} <<'PY'
from __future__ import annotations

import datetime
import glob
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

for _canal in (sys.stdout, sys.stderr):
    try:
        _canal.reconfigure(encoding="utf-8", errors="replace", newline="\n")
    except Exception:
        pass

SECOES_DEFAULT = "Sempre|Dados|Backend|Frontend|Infra / deploy|Reviews / harness|Domínio|Tombstones"
SUG_MIN = 6
ACHADO = re.compile(r"❌|mordeu_antes:|(^|[^A-Za-z0-9_-])(NEEDS_WORK|FAIL(ED|URES?)?|WAIVED)([^A-Za-z0-9_-]|$)")
COLUNAS_LICAO = ("fonte", "lm-nnn", "id")
COLUNAS_VEREDITO = ("veredito", "tratamento")
TITULO_LANDMINES = re.compile(r"^## Landmines (aplicáveis|lidas no build)")
RE_LM = re.compile(r"(?<![A-Za-z0-9_-])LM-\d{3}(?!\d)")
RE_BULLET = re.compile(r"^- \[(LM-\d{3})\]")
RE_DATA = re.compile(r"^\d{4}-\d{2}-\d{2}$")
RE_FEATURE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")
MECANISMO = ("hook em sdd/hooks/, comando de release.landmines_cmd ou asserção no Verify Gate, "
             "com um caso que falha antes")
RE_INV = re.compile(r"^- \[(INV-\d{3,})\] estado=(ok|auto|humano) origem=(seed|LM-\d{3}(?:,LM-\d{3})*)"
                    r"(?: check=(\S+))? :: (.+?) · por quê: (.+)$")
RE_DESC = re.compile(r"^- \[(LM-\d{3})\] descartado :: (.+)$")
TIPOS = ("contador", "sugestao", "add", "refine", "tombstone", "promover", "inv")
RECOMENDACOES = ("AUTO", "ACEITAR", "DESCARTAR", "NAO_JULGADO", "PERGUNTA OBRIGATÓRIA")
COLUNAS = ("#", "Tipo", "LM", "Delta", "Evidência", "Em linguagem simples", "Recomendação")
FINAIS = ("REJEITADOS:", "NAO_JULGADO:", "IGNORADOS/JA_COLHIDOS:", "CONTAMINAÇÃO:")
USO = """uso:
  playbook-curator.sh --preparar <FEATURE> [--retomar]
  playbook-curator.sh --colher <dir> <playbook> [--desde AAAA-MM-DD] [--inv <invariantes>]
  playbook-curator.sh --aplicar <delta> <playbook> [conf=AAAA-MM-DD]
  playbook-curator.sh --cruzar <delta|-> <playbook> <invariantes>
  playbook-curator.sh --validar-inv <playbook> <invariantes>
  playbook-curator.sh --aplicar-inv <linhas> <invariantes>
  playbook-curator.sh --selar <staging>
  playbook-curator.sh --conferir-bloco <colheita> <bloco> <playbook> <selo> <comparar>
  playbook-curator.sh --self-test"""


def data_ok(texto):
    if not RE_DATA.match(texto):
        return False
    try:
        datetime.date.fromisoformat(texto)
    except ValueError:
        return False
    return True


def diz(texto=""):
    print(texto)


def erro(texto=""):
    print(texto, file=sys.stderr)


def fim(resultado, seta, canal=None):
    canal = canal or sys.stdout
    print("RESULTADO: " + resultado, file=canal)
    print("→ " + seta, file=canal)


def uso(motivo):
    erro("🛑 playbook-curator: " + motivo)
    erro(USO)
    fim("ERRO DE USO", "corrija a chamada e rode de novo; nada foi lido nem gravado.", sys.stderr)
    sys.exit(64)


def falha(motivo, seta, codigo=2):
    erro("🛑 playbook-curator: " + motivo)
    fim("FALHA", seta, sys.stderr)
    sys.exit(codigo)


def ler(caminho):
    with open(caminho, encoding="utf-8", errors="replace") as f:
        return f.read()


def exige_utf8(caminho, oque):
    """Quem reescreve o arquivo não pode trocar um byte inválido por U+FFFD sem avisar: recusa antes de imprimir."""
    with open(caminho, "rb") as f:
        bruto = f.read()
    try:
        bruto.decode("utf-8")
    except UnicodeDecodeError as e:
        falha("%s tem bytes que não são UTF-8 (posição %d): gravar agora corromperia o texto." % (caminho, e.start),
              "converta %s para UTF-8 e rode de novo; nada foi impresso nem aplicado." % oque)


def secoes():
    return [s for s in (os.environ.get("PLAYBOOK_SECTIONS") or SECOES_DEFAULT).split("|") if s]


def raiz_do_projeto():
    try:
        r = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True,
                           stdin=subprocess.DEVNULL)
        if r.returncode == 0 and r.stdout.strip():
            return os.path.realpath(r.stdout.strip())
    except OSError:
        pass
    return os.path.realpath(os.getcwd())


# ── playbook ────────────────────────────────────────────────────────────────────────────────────
def parse_playbook(caminho):
    """Um dict por bullet: id, tipo (ativo|tomb), sec, ln, aj, mo, promo (1º token), sups, linha."""
    bullets, sec, atual = [], "", None
    for n, ln in enumerate(ler(caminho).split("\n"), 1):
        if ln.startswith("## "):
            sec, atual = ln[3:].strip(), None
            continue
        m = RE_BULLET.match(ln)
        if not m:
            # O lint aceita o campo na linha de continuação: quem não o lê ali erra a promoção e a trava.
            if atual is not None and ln.startswith("  ") and "promovido_para: " in ln and not atual["promo_lido"]:
                resto = ln.split("promovido_para: ")[-1].split()
                if resto:
                    atual["promo"] = resto[0].strip("`") or "—"
                atual["promo_lido"] = atual["promo_cont"] = True
            elif not ln.startswith("  "):
                atual = None
            continue
        b = {"id": m.group(1), "sec": sec, "ln": n, "aj": 0, "mo": 0, "promo": "—", "sups": [], "linha": ln, "promo_lido": False, "promo_cont": False,
             "tipo": "tomb" if re.match(r"^- \[LM-\d{3}\] ☠ ", ln) else "ativo"}
        if b["tipo"] == "ativo":
            a = re.search(r"ajudou=(\d+)", ln)
            o = re.search(r"mordeu=(\d+)", ln)
            b["aj"] = int(a.group(1)) if a else 0
            b["mo"] = int(o.group(1)) if o else 0
            if "promovido_para: " in ln:
                resto = ln.split("promovido_para: ")[-1].split()
                if resto:
                    b["promo"] = resto[0].strip("`") or "—"
                b["promo_lido"] = True
            if "sup: " in ln:
                trecho = ln.split("sup: ", 1)[1].split(" :: ", 1)[0]
                b["sups"] = re.findall(r"`([^`]+)`", trecho)
            atual = b
        else:
            atual = None
        bullets.append(b)
    return bullets


def carrega_playbook(caminho):
    if not os.path.isfile(caminho):
        falha("playbook não encontrado: " + caminho,
              "isto não é \"0 deltas\": confira o caminho do playbook e rode de novo.")
    bullets = parse_playbook(caminho)
    if not bullets:
        falha(caminho + " não tem nenhum bullet [LM-nnn]: não é um playbook",
              "isto não é \"0 deltas\": confira o arquivo (molde: sdd/playbook.md do pacote) e rode de novo.")
    return bullets


def promovido(b):
    return not b["promo"].startswith("—")


def check_vivo(b):
    """O promovido_para aponta um arquivo que existe? Texto livre, ou arquivo que saiu, não vigia nada."""
    return promovido(b) and arquivo_do_projeto(b["promo"])


def arquivo_do_projeto(caminho):
    """Um arquivo que existe, com caminho relativo que não sai da raiz: `.`, `/`, `..` e uma pasta não vigiam nada."""
    return caminho_dentro(caminho) and os.path.isfile(caminho)


def caminho_dentro(caminho):
    """Relativo e sem sair da raiz: `.github/x` é legítimo; `/x`, `..` e `../x` não."""
    n = os.path.normpath(caminho)
    if os.path.isabs(caminho) or n == ".." or n.startswith("../"):
        return False
    raiz = os.path.realpath(os.getcwd())
    return (os.path.realpath(caminho) + os.sep).startswith(raiz + os.sep)  # um link não pode levar para fora


def proximo_id(bullets):
    return max(int(b["id"][3:]) for b in bullets) + 1


# ── delta ───────────────────────────────────────────────────────────────────────────────────────
RE_CONTADOR = re.compile(r"^(LM-\d{3}) (ajudou|mordeu)\+(\d+)$")
RE_PROMO = re.compile(r"^(LM-\d{3}) promovido_para=(\S+)$")
RE_TOMB = re.compile(r"^TOMBSTONE (LM-\d{3}) :: (.+)$")
RE_REFINE = re.compile(r"^REFINE (LM-\d{3}) :: (.+)$")
RE_ADD = re.compile(r"^ADD (.+?) :: (sup: `[^`]+`.*?) :: (.+)$")


def linhas_de_delta(texto):
    """[(número da linha no arquivo, linha)] sem comentário nem linha vazia."""
    return [(n, ln.rstrip("\r")) for n, ln in enumerate(texto.split("\n"), 1)
            if ln.strip() and not ln.lstrip().startswith("#")]


def validar_delta(linhas, bullets, caminho_pb, texto_pb=None):
    """Lista de (linha, mensagem). Vazia = delta dentro da gramática e coerente com o playbook."""
    erros = []
    por_id = {b["id"]: b for b in bullets}
    lista = secoes()
    titulos = None
    if texto_pb is not None:
        titulos = {ln[3:].strip() for ln in texto_pb.split("\n") if ln.startswith("## ")}
    aposentados, tocados = {}, {}

    def ativo(n, lm):
        b = por_id.get(lm)
        if b is None or b["tipo"] != "ativo":
            erros.append((n, "%s não existe como bullet ativo em %s (tombstone não se edita; ID nunca se reusa)"
                          % (lm, caminho_pb)))
            return None
        return b

    for n, ln in linhas:
        m = RE_CONTADOR.match(ln)
        if m:
            b = ativo(n, m.group(1))
            if b is not None and not re.search(m.group(2) + r"=\d+", b["linha"]):
                erros.append((n, "%s não tem o contador %s= no playbook" % (m.group(1), m.group(2))))
            tocados.setdefault(m.group(1), n)
            continue
        m = RE_PROMO.match(ln)
        if m:
            ativo(n, m.group(1))
            tocados.setdefault(m.group(1), n)
            continue
        m = RE_TOMB.match(ln)
        if m:
            ativo(n, m.group(1))
            if m.group(1) in aposentados:
                erros.append((n, "%s aposentado 2 vezes no mesmo delta" % m.group(1)))
            aposentados[m.group(1)] = n
            if titulos is not None and "Tombstones" not in titulos:
                erros.append((n, "%s não tem a seção ## Tombstones" % caminho_pb))
            continue
        m = RE_REFINE.match(ln)
        if m:
            ativo(n, m.group(1))
            if "Do instead:" not in m.group(2):
                erros.append((n, "REFINE sem 'Do instead:' no novo texto"))
            tocados.setdefault(m.group(1), n)
            continue
        m = RE_ADD.match(ln)
        if m:
            sec = m.group(1)
            if sec == "Tombstones":
                erros.append((n, "ADD em Tombstones não existe (aposentar = TOMBSTONE LM-nnn :: motivo)"))
            elif sec not in lista:
                erros.append((n, "ADD em seção fora da lista: '%s' (lista: %s)" % (sec, " · ".join(lista[:-1]))))
            if "Do instead:" not in m.group(3):
                erros.append((n, "ADD sem 'Do instead:'"))
            continue
        erros.append((n, "linha fora da gramática: '%s'" % ln))
    for lm, n in sorted(aposentados.items()):
        if lm in tocados:
            erros.append((n, "%s é aposentado e alterado no mesmo delta: escolha um dos dois" % lm))
    return erros


def imprime_erros_de_delta(erros):
    for n, msg in erros:
        erro("❌ delta linha %d: %s" % (n, msg))
    erro("🔴 delta inválido: %d erro(s) — nada aplicado" % len(erros))


# ── --preparar ──────────────────────────────────────────────────────────────────────────────────
def pasta_de_staging(raiz, feature):
    h = hashlib.sha1(raiz.encode("utf-8")).hexdigest()[:12]
    return os.path.join(tempfile.gettempdir(), "sdd-curadoria-" + h, feature)


DERIVADOS = ("colheita.txt", "curadoria.txt", "conferido.txt", "delta.txt", "novo.md", "inv.md", "inv-linhas.txt")
REGISTRO = "CURATOR-colhidos.txt"


def confere_pasta_exclusiva(pasta):
    """O nome da pasta é previsível: numa máquina compartilhada, outro usuário pode criá-la antes e plantar evidência."""
    if not hasattr(os, "getuid"):  # Windows: sem dono nem modo no sentido POSIX
        return
    st = os.lstat(pasta)
    if st.st_uid != os.getuid():
        raise OSError("%s é de outro usuário" % pasta)
    if st.st_mode & 0o077:
        raise OSError("%s não é exclusiva: outros usuários podem escrever ou ler nela (modo %o)" % (pasta, st.st_mode & 0o777))


def preparar(args):
    retomar = "--retomar" in args
    args = [a for a in args if a != "--retomar"]
    if len(args) != 1:
        uso("--preparar exige <FEATURE> [--retomar]")
    feature = args[0]
    if not RE_FEATURE.match(feature):
        uso("FEATURE inválida: '%s' (letras, números, - e _; começa por letra ou número)" % feature)
    raiz = raiz_do_projeto()
    stg = pasta_de_staging(raiz, feature)
    pai = os.path.dirname(stg)
    try:
        for p in (pai, stg):
            if os.path.islink(p):
                raise OSError("%s é um link" % p)
            os.makedirs(p, mode=0o700, exist_ok=True)
            confere_pasta_exclusiva(p)
        if not retomar:
            # A pasta é a mesma em toda release da feature: o que sobrou da anterior não entra nesta.
            for nome in os.listdir(stg):
                alvo = os.path.join(stg, nome)
                if os.path.isdir(alvo) and not os.path.islink(alvo):
                    shutil.rmtree(alvo)
                else:
                    os.remove(alvo)
    except OSError as e:
        falha("não consegui preparar a pasta de staging %s: %s" % (stg, e),
              "apague essa pasta, ou aponte TMPDIR para uma pasta só sua, e rode de novo; nada foi copiado.")
    diz("staging: " + stg)
    if retomar:
        tem = os.path.isfile(os.path.join(stg, "colheita.txt"))
        diz("RETOMADA: " + ("colheita anterior encontrada em " + os.path.join(stg, "colheita.txt") if tem
                            else "não há colheita nesta pasta; rode sem --retomar"))
        fim("RETOMADA" if tem else "NADA A RETOMAR",
            "recalcule as pastas e vá direto para a volta do curador; não refaça o selo nem o snapshot de antes." if tem
            else "a pasta temporária se perdeu: recomece a curadoria do início, com --preparar %s; nada foi aplicado." % feature)
        return 0 if tem else 1
    # sdd/archive/<F>/: a release que fechou o DoD já moveu os documentos para lá (passo 15b) antes da curadoria.
    arq = os.path.join("sdd", "archive", feature)
    padroes = [
        os.path.join("sdd", "features", "DESIGN_%s.md" % feature), os.path.join(arq, "DESIGN_%s.md" % feature),
        os.path.join("sdd", "reports", "BUILD_REPORT_%s.md" % feature), os.path.join(arq, "BUILD_REPORT_%s.md" % feature),
        os.path.join("sdd", "reports", "evidence", feature, "AVAL*-*.log"),
        os.path.join("sdd", "reviews", "AVALIACAO_%s_[0-9]*.md" % feature), os.path.join(arq, "AVALIACAO_%s_[0-9]*.md" % feature),
        os.path.join("sdd", "releases", feature, REGISTRO),
        os.path.join("sdd", "releases", feature, "*.yaml"),
        os.path.join("sdd", "handoffs", "HANDOFF_%s.md" % feature),
    ]
    copiados, documentos = 0, 0
    for padrao in padroes:
        base, nome = os.path.split(padrao)
        for origem in sorted(glob.glob(os.path.join(glob.escape(os.path.join(raiz, base)), nome))):
            rel = os.path.relpath(origem, raiz)
            if nome.startswith("AVALIACAO_") and not re.match(r"^AVALIACAO_%s_\d{8}" % re.escape(feature), os.path.basename(origem)):
                continue  # F1_2_2026… não é da feature F1
            destino = os.path.join(stg, os.path.basename(origem))
            if os.path.realpath(origem) != os.path.join(raiz, rel) or not os.path.isfile(origem):
                diz("ignorado (link ou não é arquivo): " + rel)
                continue
            if os.path.exists(destino):
                continue  # o de sdd/ vence o de sdd/archive/
            try:
                shutil.copyfile(origem, destino)
            except OSError as e:
                falha("não consegui copiar %s: %s" % (rel, e), "confira a permissão do arquivo e rode de novo.")
            copiados += 1
            if os.path.basename(origem).startswith(("DESIGN_", "BUILD_REPORT_")):
                documentos += 1
            diz("copiado: " + rel)
    if not documentos:
        erro("⚠️ não achei DESIGN nem BUILD_REPORT de %s em sdd/features, sdd/reports nem sdd/archive/%s." % (feature, feature))
        fim("STAGING SEM DOCUMENTOS",
            "se esta release é um conserto sem DESIGN nem BUILD_REPORT, registre \"Curadoria: 0 deltas (sem documentos)\"; senão confira o nome da feature: isto não é \"0 deltas\".")
        return 1
    fim("STAGING PRONTO (%d arquivo(s))" % copiados,
        "os originais não foram tocados; rode --colher \"%s\" sdd/playbook.md e guarde a saída em colheita.txt nessa pasta." % stg)
    return 0


# ── --colher ────────────────────────────────────────────────────────────────────────────────────
class Colheita:
    def __init__(self, bullets, nome_pb):
        self.bullets = bullets
        self.ativos = {b["id"]: b for b in bullets if b["tipo"] == "ativo"}
        self.nome_pb = nome_pb
        self.hoje = datetime.date.today().isoformat()
        self.saida = []
        self.vistos = set()
        self.ignorados = set()
        self.proximo = proximo_id(bullets)
        self.candidatos = 0
        self.julgados = set()      # impressões digitais de curadorias anteriores (CURATOR-colhidos.txt)
        self.ja_julgados = 0
        self.linha_do = {}         # (tipo, LM) → índice da linha em saida: recebe as impressões seguintes

    @staticmethod
    def digital(*partes):
        """Mesma linha, no mesmo arquivo, para a mesma landmine = mesma impressão: o número da linha pode mudar."""
        return hashlib.sha1("\x1f".join(p.strip() for p in partes).encode("utf-8", "replace")).hexdigest()[:10]

    def ja_julgado(self, fp):
        if fp in self.julgados:
            self.ja_julgados += 1
            return True
        return False

    def delta(self, tipo, lm, arquivo, linha, texto=""):
        if lm not in self.ativos:
            if lm not in self.ignorados:
                self.ignorados.add(lm)
                self.saida.append("IGNORADO %s (não existe como bullet ativo em %s)" % (lm, self.nome_pb))
            return
        fp = self.digital(arquivo, tipo, lm, texto)
        if self.ja_julgado(fp):
            return  # contado numa curadoria anterior desta feature: não conta de novo
        if (tipo, lm) in self.vistos:
            # Outra linha da mesma lição nesta colheita: não conta agora, e também não pode contar na próxima
            # release. A impressão dela vai junto, para entrar no registro (CURATOR-colhidos.txt).
            k = self.linha_do[(tipo, lm)]
            if fp not in self.saida[k]:
                self.saida[k] += "," + fp
            return
        self.vistos.add((tipo, lm))
        self.linha_do[(tipo, lm)] = len(self.saida)
        self.saida.append("DELTA %s %s+1 · conf=%s · evidencia=%s:%d · fp=%s" % (lm, tipo, self.hoje, arquivo, linha, fp))

    def tabela(self, caminho, base):
        """Lê as 2 colunas que o cabeçalho nomeia. Nunca adivinha pelo conteúdo: 2 tentativas de adivinhar qual célula
        é o veredito deram contagem errada a outra lição. Sem o cabeçalho, não conta e relata."""
        linhas = ler(caminho).split("\n")
        dentro, col_id, col_ver, cabecalho, avisou = False, None, None, False, False
        for k, ln in enumerate(linhas):
            n = k + 1
            if TITULO_LANDMINES.match(ln):
                dentro, cabecalho, avisou = True, False, False
                continue
            if ln.startswith("## "):
                dentro = False
            if not dentro:
                continue
            if not ln.lstrip().startswith("|"):
                cabecalho = False
                continue
            cels = celulas(ln)
            if all(re.fullmatch(r":?-{2,}:?", c or "-") for c in cels):
                continue
            proxima = linhas[k + 1] if k + 1 < len(linhas) else ""
            if re.fullmatch(r"\s*\|[\s|:-]+\|?\s*", proxima):
                nomes = [c.strip(" *`").lower() for c in cels]
                col_id = next((nomes.index(x) for x in COLUNAS_LICAO if x in nomes), None)
                col_ver = next((nomes.index(x) for x in COLUNAS_VEREDITO if x in nomes), None)
                cabecalho = True
                continue
            if not RE_LM.search(ln):
                continue
            if not cabecalho or col_id is None or col_ver is None:
                if not avisou:
                    avisou = True
                    self.saida.append("TABELA_SEM_CABECALHO %s:%d (a tabela precisa das colunas %s e %s: não contei nada dela)"
                                      % (base, n, " ou ".join(COLUNAS_LICAO), " ou ".join(COLUNAS_VEREDITO)))
                continue
            if max(col_id, col_ver) >= len(cels):
                continue
            c = cels[col_ver].strip(" \t*`")
            veredito = "ajudou" if c.startswith("✔") else "mordeu" if re.match(r"^mordeu(\W|$)", c) else ""
            if veredito:
                for lm in sorted(set(RE_LM.findall(cels[col_id]))):
                    self.delta(veredito, lm, base, n, ln)

    def achados(self, caminho, base):
        linhas, tabela = [], False
        for n, ln in enumerate(ler(caminho).split("\n"), 1):
            if TITULO_LANDMINES.match(ln):
                tabela = True
                continue
            if ln.startswith("## "):
                tabela = False
            if tabela:
                continue  # quem julga essas linhas é tabela()
            if ACHADO.search(ln) and "✅" not in ln:
                linhas.append((n, ln))
        for n, ln in linhas:
            for lm in sorted(set(RE_LM.findall(ln))):
                self.delta("mordeu", lm, base, n, ln)
        sem_lm = [(n, ln) for n, ln in linhas if not RE_LM.search(ln)]
        if not sem_lm:
            return
        for b in self.bullets:
            lm = b["id"]
            if b["tipo"] != "ativo":
                continue
            termos = [t for t in b["sups"] if len(t) >= SUG_MIN and not t.isdigit()]
            casam = [(n, ln) for n, ln in sem_lm if any(t in ln for t in termos)]
            if not casam:
                continue
            novos = [(n, ln) for n, ln in casam if self.digital(base, "sug", lm, ln) not in self.julgados]
            if not novos:
                self.ja_julgados += 1
                continue
            fps = ",".join(self.digital(base, "sug", lm, ln) for _n, ln in novos)
            # Toda linha entra no registro: a que não sair agora voltaria como sugestão nova na próxima release.
            ja = self.linha_do.get(("sug", lm), self.linha_do.get(("mordeu", lm)))
            if ja is not None:
                self.saida[ja] += "," + fps
                continue
            termo = next(t for t in termos if t in novos[0][1])
            self.linha_do[("sug", lm)] = len(self.saida)
            self.saida.append("SUGESTAO mordeu? %s — termo `%s` em %s:%d (achado sem LM explícito; "
                              "confirmar a causa antes de virar delta) · fp=%s" % (lm, termo, base, novos[0][0], fps))

    def blocos_de_candidato(self, caminho, base):
        lista = secoes()
        linhas = ler(caminho).split("\n")
        i = 0
        while i < len(linhas):
            if not linhas[i].startswith("<<<CANDIDATO_PLAYBOOK"):
                i += 1
                continue
            inicio = i + 1
            j = inicio
            while j < len(linhas) and not linhas[j].startswith(">>>"):
                j += 1
            if j >= len(linhas):
                self.saida.append("REJEITADO candidato em %s:%d — bloco sem a linha >>> de fechamento" % (base, inicio))
                break
            self.candidato(linhas[inicio:j], base, inicio, lista)
            i = j + 1

    @staticmethod
    def campo(bloco, chave, continua=True):
        """Valor da chave + continuações indentadas, numa linha só."""
        for k, ln in enumerate(bloco):
            if ln.startswith(chave + ":"):
                partes = [ln[len(chave) + 1:].strip()]
                if continua:
                    for seg in bloco[k + 1:]:
                        if seg[:1] in (" ", "\t") and seg.strip():
                            partes.append(seg.strip())
                        else:
                            break
                return " ".join(p for p in partes if p).strip()
        return ""

    def candidato(self, bloco, base, inicio, lista):
        secao = self.campo(bloco, "secao", False)
        sup = self.campo(bloco, "sup", False)
        regra = self.campo(bloco, "regra")
        doi = self.campo(bloco, "Do instead")
        if doi and "Do instead:" not in regra:
            regra = (regra + " **Do instead:** " + doi).strip()
        evid = self.campo(bloco, "evidencia")
        ficha = self.campo(bloco, "ficha", False) or "—"
        antes = self.campo(bloco, "mordeu_antes", False)
        motivo = ""
        if not evid or evid == "—":
            motivo = "sem linha 'evidencia:' (lição sem verificação piora o contexto)"
        elif not secao or secao not in lista or secao == "Tombstones":
            motivo = "secao: '%s' não é uma das seções ativas" % secao
        elif "`" not in sup:
            motivo = "sup: sem termo em crase"
        elif "Do instead:" not in regra:
            motivo = "regra: sem 'Do instead:'"
        fp = self.digital(base, "cand", "\n".join(bloco))
        if self.ja_julgado(fp):
            return
        if motivo:
            self.saida.append("REJEITADO candidato em %s:%d — %s · fp=%s" % (base, inicio, motivo, fp))
            return
        self.candidatos += 1
        novo = "LM-%03d" % (self.proximo + self.candidatos - 1)
        self.saida.append("CANDIDATO #%d → %s · secao=%s · sup=%s · evidencia=%s · fp=%s"
                          % (self.candidatos, novo, secao, sup, evid, fp))
        corpo = regra
        if "ficha:" not in corpo:
            corpo += " → ficha: " + ficha
        if "promovido_para:" not in corpo:
            corpo += " · promovido_para: —"
        self.saida.append("   delta: ADD %s :: sup: %s :: %s" % (secao, sup, corpo))
        for lm in sorted(set(RE_LM.findall(antes))):
            self.delta("mordeu", lm, base, inicio, "mordeu_antes de " + fp)

    def promocoes(self):
        for b in self.bullets:
            if b["tipo"] == "ativo" and b["mo"] >= 2 and not promovido(b):
                self.saida.append("PROMOVER? %s mordeu=%d promovido_para=— :: promover a mecanismo? sugestão: %s (seção %s)"
                                  % (b["id"], b["mo"], MECANISMO, b["sec"]))


def data_do_documento(texto, design):
    if design:
        m = re.search(r"varredura (?:read-only )?rodada em (\d{4}-\d{2}-\d{2})", texto, re.I)
        if m:
            return m.group(1)
    m = re.search(r"\*\*Date\*\*[^0-9\n]*(\d{4}-\d{2}-\d{2})", texto)
    return m.group(1) if m else ""


def grava_trace(pasta, rc, n):
    """1 linha JSONL por feature da pasta. Nunca muda o exit da colheita."""
    if os.environ.get("SDD_TRACE", "on") == "off":
        return
    feats = []
    for prefixo in ("BUILD_REPORT_", "DESIGN_"):
        for f in sorted(glob.glob(os.path.join(glob.escape(pasta), prefixo + "*.md"))):
            nome = re.sub(r"[^A-Za-z0-9._-]", "_", os.path.basename(f)[len(prefixo):-3])
            if nome.startswith("."):
                nome = "_" + nome
            if nome and nome not in feats:
                feats.append(nome)
    if not feats:
        return
    destino = os.environ.get("SDD_TRACE_DIR") or os.path.join(raiz_do_projeto(), "sdd", "traces")
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        os.makedirs(destino, exist_ok=True)
        for feat in feats:
            linha = ('{"ts":%s,"feature":%s,"src":"curator","kind":"colher","exit":%d,"deltas":%d,"ajudou":%d,'
                     '"mordeu":%d,"candidatos":%d,"rejeitados":%d,"promocoes":%d,"sugestoes":%d}'
                     % (json.dumps(ts), json.dumps(feat), rc, n["a"] + n["m"], n["a"], n["m"], n["c"], n["r"],
                        n["p"], n["s"]))
            with open(os.path.join(destino, feat + ".jsonl"), "a", encoding="utf-8") as f:
                f.write(linha + "\n")
    except OSError:
        pass


def colher(args):
    if len(args) < 2:
        uso("--colher exige <dir> <playbook>")
    pasta, pb = args[0], args[1]
    desde, inv = "", ""
    resto = args[2:]
    while resto:
        if resto[0] == "--desde" and len(resto) >= 2:
            desde = resto[1]
            if not data_ok(desde):
                uso("--desde exige uma data AAAA-MM-DD: '%s'" % desde)
        elif resto[0] == "--inv" and len(resto) >= 2 and resto[1]:
            inv = resto[1]
        else:
            uso("opção desconhecida ou sem valor: " + resto[0])
        resto = resto[2:]
    if not os.path.isdir(pasta):
        uso("pasta não encontrada: " + pasta)
    bullets = carrega_playbook(pb)
    if inv and not os.path.isfile(inv):
        falha("invariantes não encontradas: " + inv,
              "isto não é \"0 deltas\": confira o caminho ou tire o --inv, e rode de novo.")

    c = Colheita(bullets, pb)
    registro = os.path.join(pasta, REGISTRO)
    if os.path.isfile(registro):
        c.julgados = set(re.findall(r"[0-9a-f]{10}", " ".join(re.findall(r"\bfp=([0-9a-f,]+)", ler(registro)))))
    lista = lambda padrao: sorted(f for f in glob.glob(os.path.join(glob.escape(pasta), padrao))
                                  if os.path.isfile(f))
    elegiveis = set()
    for f in lista("DESIGN_*.md"):
        elegiveis.add(f)
        base, texto = os.path.basename(f), ler(f)
        d = data_do_documento(texto, True)
        if desde and d and d < desde:
            c.saida.append("JA_COLHIDO %s (data %s < --desde %s)" % (base, d, desde))
            continue
        c.tabela(f, base)
    for f in lista("BUILD_REPORT_*.md"):
        elegiveis.add(f)
        base, texto = os.path.basename(f), ler(f)
        d = data_do_documento(texto, False)
        if desde and d and d < desde:
            c.saida.append("JA_COLHIDO %s (data %s < --desde %s)" % (base, d, desde))
            continue
        c.tabela(f, base)
        c.achados(f, base)
        c.blocos_de_candidato(f, base)
    for f in lista("AVAL*-*.log") + lista("AVALIACAO_*.md") + lista("*.yaml"):
        elegiveis.add(f)
        c.achados(f, os.path.basename(f))
    for f in lista("HANDOFF_*.md"):
        elegiveis.add(f)
        c.achados(f, os.path.basename(f))
        c.blocos_de_candidato(f, os.path.basename(f))
    c.promocoes()

    conta = lambda prefixo, meio="": sum(1 for ln in c.saida if ln.startswith(prefixo) and meio in ln)
    n = {"a": conta("DELTA ", " ajudou+1"), "m": conta("DELTA ", " mordeu+1"), "c": conta("CANDIDATO #"),
         "r": conta("REJEITADO "), "p": conta("PROMOVER? "), "s": conta("SUGESTAO ")}
    if inv:
        mordidos = [(0, "%s mordeu+1" % ln.split()[1]) for ln in c.saida
                    if ln.startswith("DELTA ") and " mordeu+1" in ln]
        avisos, _rc = cruzamento(mordidos, bullets, inv) if mordidos else ([], 0)
        c.saida.extend(ln for ln in avisos if not ln.startswith("resumo-inv:"))
        c.saida.extend(pendentes_antigos(bullets, inv, c.saida))
    if c.ja_julgados:
        c.saida.append("JA_JULGADO %d linha(s) já julgada(s) numa curadoria anterior desta feature (%s): não contam de novo"
                       % (c.ja_julgados, REGISTRO))
    c.saida.append("resumo: deltas=%d (ajudou=%d mordeu=%d) candidatos=%d rejeitados=%d promocoes=%d sugestoes=%d"
                   % (n["a"] + n["m"], n["a"], n["m"], n["c"], n["r"], n["p"], n["s"]))
    # 0 = há pelo menos 1 linha que alguém precisa julgar ou relatar; 1 = nada, de nenhum tipo.
    relatar = sum(1 for ln in c.saida if ln.startswith(("IGNORADO ", "JA_COLHIDO ", "INV_PENDENTE ", "TABELA_SEM_CABECALHO ")))
    rc = 0 if sum(n.values()) + relatar > 0 else 1
    diz("\n".join(c.saida))
    grava_trace(pasta, rc, n)
    if rc == 1:
        erro("0 deltas colhidos em %s (%d arquivo(s) elegíveis) — ausência é informação, não verde" % (pasta, len(elegiveis)))
        fim("NADA A COLHER", "registre \"Curadoria: 0 deltas\": esta feature não trouxe lição, contagem nem promoção pendente.")
        return 1
    fim("HÁ O QUE JULGAR", "despache o curador com esta colheita; nada foi aplicado.")
    return 0


# ── --aplicar ───────────────────────────────────────────────────────────────────────────────────
def aplicar(args):
    if len(args) not in (2, 3):
        uso("--aplicar exige <delta> <playbook> [conf=AAAA-MM-DD]")
    delta, pb = args[0], args[1]
    conf = args[2] if len(args) == 3 else ""
    if conf.startswith("conf="):
        conf = conf[5:]
    conf = conf or datetime.date.today().isoformat()
    if not data_ok(conf):
        uso("conf inválida: '%s' (AAAA-MM-DD ou conf=AAAA-MM-DD)" % conf)
    if not os.path.isfile(delta):
        falha("delta não encontrado: " + delta, "confira o caminho do delta e rode de novo; nada foi aplicado.")
    bullets = carrega_playbook(pb)
    texto = ler(pb)
    linhas = linhas_de_delta(ler(delta))
    erros = validar_delta(linhas, bullets, pb, texto)
    if erros:
        imprime_erros_de_delta(erros)
        fim("DELTA INVÁLIDO", "corrija as linhas acima e rode de novo; nada foi impresso nem aplicado.", sys.stderr)
        return 2
    if not linhas:
        # Byte a byte: sem nada a aplicar, nem o fim de linha nem um byte inválido podem mudar.
        sys.stdout.flush()
        with open(pb, "rb") as f:
            sys.stdout.buffer.write(f.read())
        sys.stdout.buffer.flush()
        erro("⚠️ delta vazio: a saída é igual à entrada.")
        fim("NADA A APLICAR", "nenhuma linha de delta fora de comentário; o playbook não muda.", sys.stderr)
        return 0
    exige_utf8(pb, "o playbook")

    aj, mo, promo, refine, tomb, adds = {}, {}, {}, {}, {}, []
    nid = proximo_id(bullets)
    for _n, ln in linhas:
        m = RE_CONTADOR.match(ln)
        if m:
            alvo = aj if m.group(2) == "ajudou" else mo
            alvo[m.group(1)] = alvo.get(m.group(1), 0) + int(m.group(3))
            continue
        m = RE_PROMO.match(ln)
        if m:
            promo[m.group(1)] = m.group(2)
            continue
        m = RE_TOMB.match(ln)
        if m:
            tomb[m.group(1)] = m.group(2)
            continue
        m = RE_REFINE.match(ln)
        if m:
            refine[m.group(1)] = m.group(2)
            continue
        m = RE_ADD.match(ln)
        corpo = m.group(3)
        if "promovido_para:" not in corpo:
            corpo += " · promovido_para: —"
        adds.append((m.group(1), "- [LM-%03d] ajudou=0 mordeu=0 · conf=%s · %s :: %s" % (nid, conf, m.group(2), corpo)))
        nid += 1

    final_com_quebra = texto.endswith("\n")
    brutas = texto.split("\n")
    if final_com_quebra:
        brutas = brutas[:-1]
    # blocos: [título ou None, [linhas do corpo]]
    blocos = [[None, []]]
    for ln in brutas:
        if ln.startswith("## "):
            blocos.append([ln, []])
        else:
            blocos[-1][1].append(ln)
    aposentadas = []
    # Seção da lista que falta no playbook nasce no lugar certo: o lint só exige Sempre e Tombstones.
    ordem = secoes()
    titulos = [b[0][3:].strip() for b in blocos if b[0]]
    for sec, _linha in adds:
        if sec in titulos:
            continue
        depois = [k for k, b in enumerate(blocos) if b[0] and b[0][3:].strip() in ordem
                  and ordem.index(b[0][3:].strip()) > ordem.index(sec)]
        pos = depois[0] if depois else len(blocos)
        blocos.insert(pos, ["## " + sec, [""]])
        titulos.append(sec)
    por_id = {b["id"]: b for b in bullets}
    for bloco in blocos:
        novo, pulando, lm_atual = [], False, None
        for ln in bloco[1]:
            m = RE_BULLET.match(ln)
            if m:
                pulando = False
                lm = m.group(1)
                lm_atual = lm
                if lm in tomb:
                    aposentadas.append("- [%s] ☠ %s :: %s" % (lm, conf, tomb[lm]))
                    pulando = True
                    continue
                tocado = False
                if lm in aj:
                    ln = re.sub(r"ajudou=(\d+)", lambda x: "ajudou=%d" % (int(x.group(1)) + aj[lm]), ln, count=1)
                    tocado = True
                if lm in mo:
                    ln = re.sub(r"mordeu=(\d+)", lambda x: "mordeu=%d" % (int(x.group(1)) + mo[lm]), ln, count=1)
                    tocado = True
                if lm in refine:
                    # o texto novo troca a regra; a ficha e o promovido_para do bullet ficam, se o texto não os traz
                    k = ln.find(" :: ")
                    velho = ln[k + 4:] if k >= 0 else ""
                    novo_texto = refine[lm]
                    ficha = re.search(r"→ ficha: [^·]*", velho)
                    if ficha and "ficha:" not in novo_texto:
                        novo_texto = novo_texto.rstrip() + " " + ficha.group(0).rstrip()
                    if "promovido_para:" not in novo_texto and not por_id[lm]["promo_cont"]:
                        k_pp = velho.rfind("promovido_para: ")  # a última, como o parser: a regra pode citar o nome do campo
                        novo_texto = novo_texto.rstrip() + " · " + (velho[k_pp:] if k_pp >= 0 else "promovido_para: —")
                    ln = (ln[:k + 4] if k >= 0 else ln + " :: ") + novo_texto
                    tocado = True
                if lm in promo:
                    if "promovido_para: " in ln:
                        # a última ocorrência, como o parser lê: o texto da regra pode citar o nome do campo
                        ln = ln[:ln.rindex("promovido_para: ")] + "promovido_para: " + promo[lm]
                    elif not por_id[lm]["promo_cont"]:  # na continuação, a troca é lá embaixo
                        ln = ln.rstrip() + " · promovido_para: " + promo[lm]
                    tocado = True
                if tocado:
                    ln = re.sub(r"conf=\d{4}-\d{2}-\d{2}", "conf=" + conf, ln, count=1)
                novo.append(ln)
                continue
            if pulando and ln.startswith("  ") and ln.strip():
                continue  # continuação do bullet aposentado
            if ln.startswith("  ") and lm_atual in promo and por_id[lm_atual]["promo_cont"] and "promovido_para: " in ln:
                ln = ln[:ln.rindex("promovido_para: ")] + "promovido_para: " + promo[lm_atual]
            pulando = False
            novo.append(ln)
        bloco[1] = novo

    def acrescenta(corpo, linhas_novas):
        """Põe as linhas novas depois da última linha com texto, antes dos brancos do fim da seção."""
        fim_texto = len(corpo)
        while fim_texto > 0 and not corpo[fim_texto - 1].strip():
            fim_texto -= 1
        cauda = corpo[fim_texto:]
        cabeca = corpo[:fim_texto]
        if not cabeca:
            cabeca = [""]
            cauda = cauda or [""]
        return cabeca + linhas_novas + cauda

    for bloco in blocos:
        if bloco[0] is None:
            continue
        nome = bloco[0][3:].strip()
        daqui = [linha for sec, linha in adds if sec == nome]
        if daqui:
            bloco[1] = acrescenta(bloco[1], daqui)
        if nome == "Tombstones" and aposentadas:
            bloco[1] = acrescenta(bloco[1], aposentadas)
    saida = []
    for titulo, corpo in blocos:
        if titulo is not None:
            saida.append(titulo)
        saida.extend(corpo)
    sys.stdout.write("\n".join(saida) + ("\n" if final_com_quebra else ""))
    fim("DELTA APLICADO (%d linha(s))" % len(linhas),
        "o stdout é o playbook novo: rode o playbook-lint.sh nele antes de copiar por cima.", sys.stderr)
    return 0


# ── invariantes ─────────────────────────────────────────────────────────────────────────────────
def parse_invariantes(caminho):
    """dict: tem_secao, invs [dict], descs [dict], fora [(linha, texto)]."""
    r = {"tem_secao": False, "invs": [], "descs": [], "fora": []}
    sec, vistos = "", {"Invariantes": False, "Descartados": False}
    for n, ln in enumerate(ler(caminho).split("\n"), 1):
        ln = ln.rstrip("\r")
        if ln.startswith("## "):
            sec = ln[3:].strip()
            if sec == "Invariantes":
                r["tem_secao"] = True
            continue
        if sec not in vistos or not ln.strip():
            continue
        if sec == "Invariantes":
            m = RE_INV.match(ln)
            if m:
                vistos[sec] = True
                r["invs"].append({"id": m.group(1), "estado": m.group(2), "origem": m.group(3),
                                  "check": m.group(4) or "", "regra": m.group(5), "resto": m.group(6), "linha": ln, "ln": n})
            elif vistos[sec] or ln.startswith("- ["):
                r["fora"].append((n, ln))
        else:
            m = RE_DESC.match(ln)
            if m:
                vistos[sec] = True
                r["descs"].append({"id": m.group(1), "linha": ln, "ln": n})
            elif vistos[sec] or ln.startswith("- ["):
                r["fora"].append((n, ln))
    return r


def origens(inv):
    return [o for o in inv["origem"].split(",") if o.startswith("LM-")]


def pendentes_antigos(bullets, caminho_inv, ja_na_saida):
    """Lições que JÁ estão no universo e não têm classificação: sem esta pergunta, a trava para e ninguém pergunta."""
    inv = parse_invariantes(caminho_inv)
    classificados = {d["id"] for d in inv["descs"]}
    for i in inv["invs"]:
        classificados.update(origens(i))
    ja = set(re.findall(r"INV_PENDENTE (LM-\d{3})", "\n".join(ja_na_saida)))
    proximo = max([int(i["id"][4:]) for i in inv["invs"]] or [0]) + len(ja)
    saida = []
    for b in bullets:
        if b["tipo"] != "ativo" or b["id"] in classificados or b["id"] in ja or not (b["mo"] >= 1 or promovido(b)):
            continue
        proximo += 1
        saida.append("INV_PENDENTE %s (já no universo, sem classificação)" % b["id"])
        saida.append("   proposta A: - [INV-%03d] estado=<ok|auto|humano> origem=%s :: <regra> · por quê: <…> · tarefa|motivo: <…>"
                     % (proximo, b["id"]))
        saida.append("   proposta B: - [%s] descartado :: <motivo>" % b["id"])
    return saida


def cruzamento(linhas, bullets, caminho_inv):
    """(avisos, rc). linhas = delta já validado. rc 0 nada · 3 há aviso."""
    por_id = {b["id"]: b for b in bullets}
    inv = parse_invariantes(caminho_inv)
    classificados = set()
    for i in inv["invs"]:
        classificados.update(origens(i))
    desc = {d["id"]: d["linha"] for d in inv["descs"]}
    classificados.update(desc)
    maior = max([int(i["id"][4:]) for i in inv["invs"]] or [0])
    saida, aposentar, vistos, pendentes, afetadas = [], [], set(), 0, 0
    for _n, ln in linhas:
        m = RE_TOMB.match(ln)
        if m:
            if m.group(1) not in aposentar:
                aposentar.append(m.group(1))
            continue
        m = RE_CONTADOR.match(ln)
        p = RE_PROMO.match(ln)
        if not ((m and m.group(2) == "mordeu") or p):
            continue
        lm = (m or p).group(1)
        b = por_id.get(lm)
        if lm in classificados or lm in vistos or b is None or b["tipo"] != "ativo":
            continue
        if b["mo"] != 0 or promovido(b):
            continue  # já estava no universo: não é entrada nova
        if m:
            if int(m.group(3)) == 0:
                continue
            motivo = "mordeu 0→%d" % int(m.group(3))
        else:
            motivo = "promovido"
        vistos.add(lm)
        pendentes += 1
        saida.append("INV_PENDENTE %s (%s) · delta: %s" % (lm, motivo, ln))
        saida.append("   proposta A: - [INV-%03d] estado=<ok|auto|humano> origem=%s :: <regra> · por quê: <…> · tarefa|motivo: <…>"
                     % (maior + pendentes, lm))
        saida.append("   proposta B: - [%s] descartado :: <motivo>" % lm)
    for i in inv["invs"]:
        todas = i["origem"].split(",")
        tirados = [o for o in todas if o in aposentar]
        if not tirados:
            continue
        resto = [o for o in todas if o not in aposentar]
        promo_tirado = next((por_id[o]["promo"] for o in tirados if o in por_id and check_vivo(por_id[o])), "")
        afetadas += 1
        saida.append("INV_AFETADA %s origem=%s · delta: TOMBSTONE %s" % (i["id"], i["origem"], ",".join(tirados)))
        velho = " origem=%s " % i["origem"]
        if resto:
            novo = i["linha"].replace(velho, " origem=%s " % ",".join(resto), 1)
            outro = any(o in por_id and check_vivo(por_id[o]) for o in resto)
            if promo_tirado and not outro and not i["check"]:
                novo = novo.replace(" origem=%s " % ",".join(resto),
                                    " origem=%s check=%s " % (",".join(resto), promo_tirado), 1)
            saida.append("   ajuste: " + novo)
        else:
            novo = i["linha"].replace(velho, " origem=seed ", 1)
            if promo_tirado:
                if i["check"]:
                    novo = novo.replace(" check=%s " % i["check"], " check=%s " % promo_tirado, 1)
                else:
                    novo = novo.replace(" origem=seed ", " origem=seed check=%s " % promo_tirado, 1)
                saida.append("   ajuste: " + novo)
            elif not (i["estado"] == "ok" and not i["check"]):
                saida.append("   ajuste: " + novo)
            else:
                saida.append("   (origem=seed deixaria %s estado=ok sem check: não é saída válida)" % i["id"])
        saida.append("   ou: retirar o TOMBSTONE " + " e ".join(tirados))
    for lm in aposentar:
        if lm in desc:
            afetadas += 1
            saida.append("INV_AFETADA descarte %s · delta: TOMBSTONE %s" % (lm, lm))
            saida.append("   ajuste: REMOVER " + lm)
            saida.append("   ou: retirar o TOMBSTONE " + lm)
    saida.append("resumo-inv: afetadas=%d pendentes=%d" % (afetadas, pendentes))
    return saida, (3 if afetadas + pendentes else 0)


def cruzar(args):
    if len(args) != 3:
        uso("--cruzar exige <delta|-> <playbook> <invariantes>")
    delta, pb, inv = args
    for nome, caminho in (("delta", delta), ("playbook", pb), ("invariantes", inv)):
        if not os.path.isfile(caminho):
            falha("%s não encontrado: %s" % (nome, caminho), "confira o caminho e rode de novo; nada foi cruzado.")
    bullets = carrega_playbook(pb)
    if not parse_invariantes(inv)["tem_secao"]:
        falha("%s sem a seção '## Invariantes'" % inv, "confira o arquivo de invariantes (molde: sdd/invariants.md do pacote).")
    linhas = linhas_de_delta(ler(delta))
    erros = validar_delta(linhas, bullets, pb, ler(pb))
    if erros:
        imprime_erros_de_delta(erros)
        fim("DELTA INVÁLIDO", "corrija as linhas acima e rode de novo; nada foi cruzado.", sys.stderr)
        return 2
    avisos, rc = cruzamento(linhas, bullets, inv)
    diz("\n".join(avisos))
    if rc:
        fim("HÁ AVISO DE INVARIANTE", "cada INV_AFETADA vai na mesma opção do delta que a causa; cada INV_PENDENTE vai na mesma opção da contagem que a causa.")
    else:
        fim("SEM AVISO", "o delta não mexe em nenhuma invariante.")
    return rc


def validar_inv(args):
    if len(args) != 2:
        uso("--validar-inv exige <playbook> <invariantes>")
    pb, caminho_inv = args
    if not os.path.isfile(pb) or not os.path.isfile(caminho_inv):
        erro("🔴 trava INV: arquivo ausente (%s / %s)" % (pb, caminho_inv))
        fim("TRAVA", "nada foi copiado; confira os 2 caminhos e rode de novo.")
        return 2
    bullets = parse_playbook(pb)
    por_id = {b["id"]: b for b in bullets}
    inv = parse_invariantes(caminho_inv)
    defeitos, pendentes = [], []
    if not inv["tem_secao"]:
        defeitos.append("%s não tem a seção '## Invariantes'" % caminho_inv)
    for n, ln in inv["fora"]:
        defeitos.append("linha %d fora da gramática: %s — veja a gramática no cabeçalho de sdd/bin/playbook-curator.sh" % (n, ln[:80]))
    vistos = set()
    for i in inv["invs"]:
        if i["id"] in vistos:
            defeitos.append("%s aparece 2 vezes — renumere a mais nova (ID nunca se reusa)" % i["id"])
        vistos.add(i["id"])
        if re.search(r"· (tarefa|motivo):\s*($|·)", i["resto"]) and not (
                (i["estado"] == "auto" and not re.search(r"· tarefa:\s*[^\s·]", i["resto"]))
                or (i["estado"] == "humano" and not re.search(r"· motivo:\s*[^\s·]", i["resto"]))):
            defeitos.append("%s tem '· tarefa:' ou '· motivo:' vazio — preencha ou tire o campo" % i["id"])
        if i["estado"] == "auto" and not re.search(r"· tarefa:\s*[^\s·]", i["resto"]):
            defeitos.append("%s é estado=auto sem '· tarefa:' — diga o comando ou o alvo que a automatiza" % i["id"])
        if i["estado"] == "humano" and not re.search(r"· motivo:\s*[^\s·]", i["resto"]):
            defeitos.append("%s é estado=humano sem '· motivo:' — diga por que máquina não pega" % i["id"])
        if i["check"] and (not caminho_dentro(i["check"]) or os.path.isdir(i["check"])):
            defeitos.append("%s tem check=%s: use o caminho de um arquivo, relativo à raiz do projeto" % (i["id"], i["check"]))
        elif i["check"] and not os.path.exists(i["check"]):
            defeitos.append("%s tem check=%s, que não existe a partir desta pasta — corrija o caminho ou mude o estado"
                            % (i["id"], i["check"]))
        tem_promovido = False
        for o in origens(i):
            b = por_id.get(o)
            if b is None:
                defeitos.append("%s tem origem=%s, que não existe no playbook — corrija a origem" % (i["id"], o))
            elif b["tipo"] == "tomb":
                defeitos.append("%s tem origem=%s, que está aposentada — aprove o ajuste proposto pelo --cruzar "
                                "(origem=seed ou a lista sem %s) ou retire o TOMBSTONE %s" % (i["id"], o, o, o))
            elif check_vivo(b):
                tem_promovido = True
        if i["estado"] == "ok" and not i["check"] and not tem_promovido:
            defeitos.append("%s é estado=ok sem check= e sem origem promovida para um arquivo que existe — aponte o check ou mude o estado" % i["id"])
    classificados = set()
    for i in inv["invs"]:
        classificados.update(origens(i))
    descartados = set()
    for d in inv["descs"]:
        if d["id"] in descartados:
            defeitos.append("%s aparece 2 vezes em ## Descartados — deixe uma linha só" % d["id"])
        descartados.add(d["id"])
        if d["id"] in classificados:
            defeitos.append("%s é origem de uma invariante e também está em ## Descartados — escolha um dos dois" % d["id"])
        b = por_id.get(d["id"])
        if b is None:
            defeitos.append("%s está em ## Descartados e não existe no playbook — remova a linha" % d["id"])
        elif b["tipo"] == "tomb":
            defeitos.append("%s está em ## Descartados e foi aposentada — remova a linha do descarte ou retire o TOMBSTONE %s"
                            % (d["id"], d["id"]))
    classificados |= descartados
    for b in bullets:
        if b["tipo"] == "ativo" and (b["mo"] >= 1 or promovido(b)) and b["id"] not in classificados:
            pendentes.append(b["id"])
    if not defeitos and not pendentes:
        diz("🟢 trava INV: par válido (%d invariante(s), %d descartado(s), pendentes=0)" % (len(inv["invs"]), len(descartados)))
        fim("PAR VÁLIDO", "copie os 2 arquivos por cima dos originais.")
        return 0
    if pendentes and not defeitos:
        erro("o registro de invariantes é novo na v2.6.0: %d lição(ões) do playbook ainda não foram classificadas." % len(pendentes))
    for d in defeitos:
        erro("🔴 trava INV: " + d)
    for lm in pendentes:
        erro("🔴 trava INV: %s entra no universo sem classificação — aprove a proposta A (virar invariante) ou a B "
             "(descartar com motivo), ou retire o delta" % lm)
    fim("TRAVA", "nada foi copiado; resolva cada linha acima com a pessoa e rode de novo.")
    return 2


# ── --aplicar-inv ───────────────────────────────────────────────────────────────────────────────
def aplicar_inv(args):
    """Linhas aprovadas (invariante, descarte, REMOVER INV-nnn, REMOVER LM-nnn) → invariantes novas no stdout."""
    if len(args) != 2:
        uso("--aplicar-inv exige <linhas> <invariantes>")
    caminho_linhas, caminho_inv = args
    for nome, caminho in (("linhas", caminho_linhas), ("invariantes", caminho_inv)):
        if not os.path.isfile(caminho):
            falha("%s não encontrado: %s" % (nome, caminho), "confira o caminho e rode de novo; nada foi aplicado.")
    texto = ler(caminho_inv)
    atual = parse_invariantes(caminho_inv)
    erros, trocas, remover, novas_inv, novos_desc = [], {}, set(), [], []
    ids_inv = {i["id"] for i in atual["invs"]}
    regra_por_id = {i["id"]: i["regra"] for i in atual["invs"]}
    vistas_nas_linhas = set()
    ids_desc = {d["id"] for d in atual["descs"]}
    if not atual["tem_secao"]:
        erros.append((0, "%s não tem a seção '## Invariantes'" % caminho_inv))
    for n, ln in linhas_de_delta(ler(caminho_linhas)):
        m = RE_INV.match(ln)
        if m:
            if m.group(1) in vistas_nas_linhas:
                erros.append((n, "%s aparece 2 vezes nas linhas aprovadas: cada ID entra uma vez" % m.group(1)))
            vistas_nas_linhas.add(m.group(1))
            if m.group(1) in regra_por_id and regra_por_id[m.group(1)] != m.group(5):
                erros.append((n, "%s já existe em %s com outra regra: isto é uma invariante nova com ID repetido; "
                                 "renumere a nova, nunca a que já estava lá" % (m.group(1), caminho_inv)))
            elif m.group(1) in ids_inv:
                trocas[m.group(1)] = ln
            else:
                novas_inv.append(ln)
                ids_inv.add(m.group(1))
            continue
        m = RE_DESC.match(ln)
        if m:
            if m.group(1) in ids_desc:
                trocas[m.group(1)] = ln
            else:
                novos_desc.append(ln)
                ids_desc.add(m.group(1))
            continue
        m = re.match(r"^REMOVER (INV-\d{3,}|LM-\d{3})$", ln)
        if m:
            if m.group(1) not in ids_inv and m.group(1) not in ids_desc:
                erros.append((n, "%s não está em %s: nada a remover" % (m.group(1), caminho_inv)))
            remover.add(m.group(1))
            continue
        erros.append((n, "linha fora da gramática das invariantes: '%s'" % ln[:80]))
    if erros:
        for n, msg in erros:
            erro("❌ invariantes linha %d: %s" % (n, msg))
        fim("LINHAS INVÁLIDAS", "corrija as linhas acima e rode de novo; nada foi impresso nem aplicado.", sys.stderr)
        return 2
    exige_utf8(caminho_inv, "o arquivo de invariantes")
    final_com_quebra = texto.endswith("\n")
    brutas = texto.split("\n")
    if final_com_quebra:
        brutas = brutas[:-1]
    blocos = [[None, []]]
    for ln in brutas:
        if ln.startswith("## "):
            blocos.append([ln, []])
        else:
            blocos[-1][1].append(ln)
    if novos_desc and not any(t == "## Descartados" for t, _c in blocos if t):
        blocos.append(["## Descartados", [""]])

    def acrescenta(corpo, linhas_novas):
        k = len(corpo)
        while k > 0 and not corpo[k - 1].strip():
            k -= 1
        cabeca, cauda = corpo[:k], corpo[k:]
        if not cabeca:
            cabeca, cauda = [""], (cauda or [""])
        return cabeca + linhas_novas + cauda

    for bloco in blocos:
        nome = bloco[0][3:].strip() if bloco[0] else ""
        if nome not in ("Invariantes", "Descartados"):
            continue
        corpo = []
        for ln in bloco[1]:
            m = RE_INV.match(ln) if nome == "Invariantes" else RE_DESC.match(ln)
            chave = m.group(1) if m else None
            if chave in remover:
                continue
            corpo.append(trocas.get(chave, ln) if chave else ln)
        extra = novas_inv if nome == "Invariantes" else novos_desc
        bloco[1] = acrescenta(corpo, extra) if extra else corpo
    saida = []
    for titulo, corpo in blocos:
        if titulo is not None:
            saida.append(titulo)
        saida.extend(corpo)
    sys.stdout.write("\n".join(saida) + ("\n" if final_com_quebra else ""))
    fim("INVARIANTES APLICADAS", "o stdout é o arquivo novo: rode --validar-inv com o playbook novo antes de copiar por cima.", sys.stderr)
    return 0


# ── --selar ─────────────────────────────────────────────────────────────────────────────────────
def sha_do_arquivo(caminho):
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for pedaco in iter(lambda: f.read(65536), b""):
            h.update(pedaco)
    return h.hexdigest()


def selo_da_pasta(pasta):
    """{caminho relativo: sha256} de tudo na pasta: entre o selo e a conferência, ninguém legítimo grava ali."""
    selo = {}
    for atual, pastas, arquivos in os.walk(pasta):
        pastas.sort()
        for nome in sorted(arquivos + [p for p in pastas if os.path.islink(os.path.join(atual, p))]):
            alvo = os.path.join(atual, nome)
            rel = os.path.relpath(alvo, pasta)
            if os.path.islink(alvo):
                selo[rel] = "LINK"
            elif os.path.isfile(alvo):
                selo[rel] = sha_do_arquivo(alvo)
    return selo


def selar(args):
    if len(args) != 1 or not os.path.isdir(args[0]):
        uso("--selar exige a pasta de staging")
    selo = selo_da_pasta(args[0])
    if "colheita.txt" not in selo:
        falha("a pasta %s não tem colheita.txt: sele depois de colher" % args[0],
              "rode --colher, guarde a saída em colheita.txt e sele de novo.")
    for nome, sha in sorted(selo.items()):
        diz("%s  %s" % (sha, nome))
    fim("SELO IMPRESSO (%d arquivo(s))" % len(selo),
        "guarde o stdout FORA da pasta de staging (na pasta do snapshot) e passe ao --conferir-bloco.", sys.stderr)
    return 0


# ── --conferir-bloco ────────────────────────────────────────────────────────────────────────────
def celulas(ln):
    partes = re.split(r"(?<!\\)\|", ln.strip())
    if partes and partes[0] == "":
        partes = partes[1:]
    if partes and partes[-1] == "":
        partes = partes[:-1]
    return [p.strip().replace("\\|", "|") for p in partes]


def recomendacao(texto):
    t = texto.strip().strip("*`").strip()
    for r in sorted(RECOMENDACOES, key=len, reverse=True):
        if t == r or t.startswith(r + " ") or t.startswith(r + "("):
            return r
    return ""


def conferir_bloco(args):
    if len(args) != 5:
        uso("--conferir-bloco exige <colheita> <bloco> <playbook> <selo> <comparar>")
    colheita, bloco, pb, caminho_selo, caminho_comparar = args
    for nome, caminho in (("colheita", colheita), ("bloco", bloco), ("selo", caminho_selo),
                          ("saída do --comparar da fronteira", caminho_comparar)):
        if not os.path.isfile(caminho):
            falha("%s não encontrado: %s" % (nome, caminho), "confira o caminho e rode de novo; nada foi conferido.")
    bullets = carrega_playbook(pb)
    texto_pb = ler(pb)
    staging = os.path.dirname(os.path.abspath(colheita))
    defeitos = []

    # 1. O curador só leu? A fronteira do projeto (stdout do --comparar) e o selo do staging respondem.
    linhas_cmp = [ln.strip() for ln in ler(caminho_comparar).split("\n")]
    for ln in linhas_cmp:
        if ln.startswith("FORA:"):
            defeitos.append("a fronteira acusou escrita fora do permitido — " + ln)
    if "RESULTADO: SÓ O PERMITIDO MUDOU" not in linhas_cmp:
        defeitos.append("a saída do --comparar não tem a linha 'RESULTADO: SÓ O PERMITIDO MUDOU': fronteira não verificada nunca vale como 'nada mudou'")
    selado = {}
    for ln in ler(caminho_selo).split("\n"):
        m = re.match(r"^([0-9a-f]{64}|LINK)  (.+)$", ln)
        if m:
            selado[m.group(2)] = m.group(1)
    if "colheita.txt" not in selado:
        defeitos.append("o selo não cobre a colheita.txt: sele a pasta com --selar depois de colher e antes de despachar")
    else:
        agora = selo_da_pasta(staging)
        for nome in sorted(set(selado) | set(agora)):
            if selado.get(nome) != agora.get(nome):
                como = "mudou" if nome in selado and nome in agora else ("sumiu" if nome in selado else "apareceu")
                defeitos.append("o staging mudou depois do selo: %s %s" % (nome, como))

    col = {"delta": [], "sug": [], "cand": [], "rej": [], "promo": [], "ign": [], "ja": [], "pend": []}
    evid_da_colheita = {}
    for ln in ler(colheita).split("\n"):
        m = re.match(r"^DELTA (LM-\d{3}) (ajudou|mordeu)\+1\b.*?evidencia=(.+?:\d+)(?: · fp=|$)", ln)
        if m:
            col["delta"].append((m.group(1), m.group(2)))
            evid_da_colheita[(m.group(1), m.group(2))] = m.group(3)
            continue
        for chave, padrao in (("sug", r"^SUGESTAO mordeu\? (LM-\d{3})"), ("rej", r"^REJEITADO candidato em (.+?:\d+) — "),
                              ("promo", r"^PROMOVER\? (LM-\d{3})"), ("ign", r"^IGNORADO (LM-\d{3})"),
                              ("ja", r"^JA_COLHIDO (\S+)"), ("ja", r"^TABELA_SEM_CABECALHO (.+?:\d+) "), ("pend", r"^INV_PENDENTE (LM-\d{3})")):
            m = re.match(padrao, ln)
            if m:
                col[chave].append(m.group(1))
                break
        else:
            m = re.match(r"^CANDIDATO #(\d+) → (LM-\d{3})", ln)
            if m:
                col["cand"].append((m.group(1), m.group(2)))

    linhas = ler(bloco).split("\n")
    aberturas = [k for k, ln in enumerate(linhas) if ln.startswith("<<<CURADORIA")]
    corpo = []
    if len(aberturas) != 1:
        defeitos.append("o bloco precisa de exatamente 1 linha <<<CURADORIA (achei %d)" % len(aberturas))
    else:
        fecho = next((k for k in range(aberturas[0] + 1, len(linhas)) if linhas[k].startswith(">>>")), None)
        if fecho is None:
            defeitos.append("o bloco não tem a linha >>> de fechamento")
        else:
            corpo = linhas[aberturas[0] + 1:fecho]

    rows, finais, viu_cabecalho = [], {}, False
    for ln in corpo:
        if ln.lstrip().startswith("|"):
            cs = celulas(ln)
            if cs and cs[0] == "#":
                viu_cabecalho = True
                if tuple(cs) != COLUNAS:
                    defeitos.append("cabeçalho da tabela diferente de: | " + " | ".join(COLUNAS) + " |")
                continue
            if cs and all(re.fullmatch(r":?-{2,}:?", c or "-") for c in cs):
                continue
            if len(cs) != 7:
                defeitos.append("linha da tabela com %d células (esperado 7; barra dentro da célula vai como \\|): %s"
                                % (len(cs), ln.strip()[:80]))
                continue
            if any(r["n"] == cs[0] for r in rows):
                defeitos.append("o número %s aparece em mais de uma linha da tabela" % cs[0])
            rows.append(dict(zip(("n", "tipo", "lm", "delta", "evid", "simples", "rec"), cs)))
            continue
        for f in FINAIS:
            if ln.startswith(f):
                finais[f] = ln[len(f):].strip()
    if corpo and not viu_cabecalho:
        defeitos.append("a tabela não tem o cabeçalho: | " + " | ".join(COLUNAS) + " |")
    for f in FINAIS:
        if corpo and f not in finais:
            defeitos.append("falta a linha %s" % f)
    if corpo and "CONTAMINAÇÃO:" in finais and not re.match(r"^(não|sim)\b", finais["CONTAMINAÇÃO:"].lower()):
        defeitos.append("a linha CONTAMINAÇÃO: precisa dizer 'não' ou 'sim — <o que veio>'")

    autos, perguntas, contagem = [], [], {"DESCARTAR": 0, "NAO_JULGADO": 0}
    for r in rows:
        rotulo = "linha %s" % r["n"]
        tipo = r["tipo"].strip("`* ")
        rec = recomendacao(r["rec"])
        delta = r["delta"].strip()
        if delta.startswith("`") and delta.endswith("`") and delta.count("`") == 2:
            delta = delta[1:-1].strip()
        r["tipo"], r["rec_n"], r["delta_n"] = tipo, rec, delta
        if tipo not in TIPOS:
            defeitos.append("%s: Tipo '%s' fora da lista (%s)" % (rotulo, tipo, ", ".join(TIPOS)))
            continue
        if not rec:
            defeitos.append("%s: Recomendação '%s' fora da lista (%s)" % (rotulo, r["rec"], ", ".join(RECOMENDACOES)))
            continue
        if not r["simples"].strip("—–-` *."):
            defeitos.append("%s: a célula 'Em linguagem simples' está vazia" % rotulo)
        if rec == "AUTO" and tipo != "contador":
            defeitos.append("%s: AUTO só vale para contador que a colheita trouxe; '%s' vai para pergunta (use ACEITAR)" % (rotulo, tipo))
            continue
        if rec == "ACEITAR" and tipo in ("contador", "promover"):
            defeitos.append("%s: '%s' não usa ACEITAR (contador: AUTO; promover: PERGUNTA OBRIGATÓRIA)" % (rotulo, tipo))
        if rec == "PERGUNTA OBRIGATÓRIA" and tipo not in ("promover", "inv"):
            defeitos.append("%s: PERGUNTA OBRIGATÓRIA só vale para promover e inv" % rotulo)
        if tipo == "promover" and rec not in ("PERGUNTA OBRIGATÓRIA",):
            defeitos.append("%s: promoção só com a recomendação PERGUNTA OBRIGATÓRIA (veio %s)" % (rotulo, rec))
        # A coluna LM diz de quem é a linha: 1 ID, o mesmo do delta. Sem isso, 1 linha cobre 2 da colheita.
        if tipo in ("contador", "sugestao", "promover", "tombstone", "refine"):
            ids_lm, ids_delta = RE_LM.findall(r["lm"]), RE_LM.findall(delta)[:1]
            if len(ids_lm) != 1 or (ids_delta and ids_lm != ids_delta):
                defeitos.append("%s: a coluna LM ('%s') tem de ser 1 ID, o mesmo do delta ('%s')" % (rotulo, r["lm"], delta))
        if rec == "DESCARTAR" and not re.search(r"\(\s*[^)\s]", r["rec"]):
            defeitos.append("%s: DESCARTAR pede o motivo: DESCARTAR (motivo)" % rotulo)
        if rec in ("DESCARTAR", "NAO_JULGADO"):
            contagem[rec] += 1
            continue
        # daqui para baixo: linha que entra (AUTO) ou vai para pergunta (ACEITAR, PERGUNTA OBRIGATÓRIA)
        forma = {"contador": RE_CONTADOR, "sugestao": RE_CONTADOR, "add": RE_ADD, "refine": RE_REFINE,
                 "tombstone": RE_TOMB, "promover": RE_PROMO}.get(tipo)
        if forma is not None and not forma.match(delta):
            defeitos.append("%s: o delta '%s' não é da forma de uma linha '%s': a frase da pessoa falaria de uma coisa, e entraria outra"
                            % (rotulo, delta[:40], tipo))
            continue
        if tipo == "add" and not RE_LM.search(r["lm"]):
            defeitos.append("%s: a linha add leva na coluna LM o ID proposto pela colheita" % rotulo)
        if tipo == "inv":
            if not (RE_INV.match(delta) or RE_DESC.match(delta) or re.match(r"^REMOVER (INV-\d{3,}|LM-\d{3})$", delta)):
                defeitos.append("%s: a célula Delta de uma linha inv é a linha completa da invariante ou do descarte, ou REMOVER <id>" % rotulo)
        else:
            erros = validar_delta([(0, delta)], bullets, pb, texto_pb)
            for _n, msg in erros:
                defeitos.append("%s: Delta fora da gramática — %s" % (rotulo, msg))
            if rec == "ACEITAR":
                m = re.match(r"^`?([^:`|]+?):(\d+)", r["evid"].strip())
                if not m:
                    defeitos.append("%s: ACEITAR exige a Evidência começando por arquivo:linha" % rotulo)
                else:
                    alvo = os.path.join(staging, os.path.basename(m.group(1)))
                    if os.path.basename(m.group(1)) in (os.path.basename(colheita), "colheita.rc"):
                        defeitos.append("%s: a colheita não é evidência de si mesma: cite o documento de onde a linha veio" % rotulo)
                    elif not os.path.isfile(alvo):
                        defeitos.append("%s: a evidência %s não existe na pasta da colheita" % (rotulo, m.group(1)))
                    elif not 1 <= int(m.group(2)) <= len(ler(alvo).split("\n")):
                        defeitos.append("%s: a evidência %s:%s aponta para uma linha que o arquivo não tem"
                                        % (rotulo, m.group(1), m.group(2)))
        if tipo == "sugestao":
            m = RE_CONTADOR.match(delta)
            if not m or m.group(2) != "mordeu" or m.group(3) != "1" or m.group(1) not in col["sug"]:
                defeitos.append("%s: a sugestão '%s' não está na colheita como SUGESTAO desse ID (o delta é LM-nnn mordeu+1)" % (rotulo, delta))
        if rec == "AUTO":
            # Igualdade, não existência: o mesmo ID, verbo, +1 e arquivo:linha de UMA linha DELTA da colheita.
            m = RE_CONTADOR.match(delta)
            chave = (m.group(1), m.group(2)) if m else None
            esperada = evid_da_colheita.get(chave, "")
            ev_txt = r["evid"].strip().strip("`")
            if not m or m.group(3) != "1":
                defeitos.append("%s: AUTO pede um delta de contador com +1 (LM-nnn ajudou+1 ou LM-nnn mordeu+1)" % rotulo)
            elif chave not in col["delta"]:
                defeitos.append("%s: o contador '%s' não está na colheita — contagem que o script não colheu não entra sozinha"
                                % (rotulo, delta))
            elif not re.match(re.escape(esperada) + r"(\D|$)", ev_txt):
                defeitos.append("%s: a evidência do contador '%s' tem de ser a da colheita (%s), não outra linha" % (rotulo, delta, esperada))
            elif m.group(2) == "mordeu" and m.group(1) in col["pend"]:
                perguntas.append(r)  # põe a lição no universo das invariantes: decide junto com a classificação
            else:
                autos.append(r)
        else:
            perguntas.append(r)

    # O conjunto que pode entrar precisa valer junto: as linhas passam 1 a 1 e travariam no --cruzar do item 5.
    conjunto = [(0, r["delta_n"]) for r in rows if r.get("rec_n") in ("AUTO", "ACEITAR", "PERGUNTA OBRIGATÓRIA") and r["tipo"] != "inv"]
    for _n, msg in validar_delta(conjunto, bullets, pb, texto_pb):
        if "aposentado" in msg:
            defeitos.append("o conjunto do bloco não vale junto — %s" % msg)

    # cobertura, 1 para 1: toda linha da colheita aparece no bloco, e é o delta que diz de quem é a linha
    def delta_de(r):
        return RE_CONTADOR.match(r.get("delta_n", ""))

    contadores = {}
    for r in rows:
        m = delta_de(r)
        if r["tipo"] == "contador" and m:
            contadores.setdefault((m.group(1), m.group(2)), []).append(r["n"])
    for chave, numeros in sorted(contadores.items()):
        if len(numeros) > 1:
            defeitos.append("o contador %s %s+1 aparece em %d linhas (%s): cada um entra uma vez"
                            % (chave[0], chave[1], len(numeros), ", ".join(numeros)))
    # O que pode entrar, de qualquer tipo, soma 1 vez: 2 linhas sugestao somariam +2 para 1 achado.
    entrando = {}
    for r in rows:
        m = delta_de(r)
        if m and r.get("rec_n") in ("AUTO", "ACEITAR"):
            entrando.setdefault((m.group(1), m.group(2)), []).append(r["n"])
    for chave, numeros in sorted(entrando.items()):
        if len(numeros) > 1 and chave not in [k for k, v in contadores.items() if len(v) > 1]:
            defeitos.append("a contagem %s %s+1 aparece em %d linhas (%s): cada uma entra uma vez"
                            % (chave[0], chave[1], len(numeros), ", ".join(numeros)))
    for lm, verbo in col["delta"]:
        if (lm, verbo) not in contadores:
            defeitos.append("a colheita tem DELTA %s %s+1 e o bloco não tem a linha contador dele" % (lm, verbo))

    def tem(tipo, lm):
        return any(r["tipo"] == tipo and RE_LM.findall(r["lm"]) == [lm] for r in rows)

    def cita(ref, texto):
        # `arquivo:13` não é citado por `arquivo:131`, nem `x.md` por `ax.md`
        return re.search(r"(?<![\w.-])" + re.escape(ref) + r"(?![\w])", texto) is not None

    for lm in col["sug"]:
        if not tem("sugestao", lm):
            defeitos.append("a colheita tem SUGESTAO para %s e o bloco não tem a linha sugestao dele" % lm)
    for num, lm in col["cand"]:
        citado = any(r["tipo"] == "refine" and re.search(r"candidato #%s\b" % num, r["evid"] + " " + r["simples"], re.I)
                     for r in rows)
        if not (tem("add", lm) or citado):
            defeitos.append("a colheita tem CANDIDATO #%s → %s e o bloco não tem linha add com esse ID nem refine que cite 'candidato #%s'"
                            % (num, lm, num))
    for ref in col["rej"]:
        if not cita(ref, finais.get("REJEITADOS:", "")):
            defeitos.append("a colheita tem REJEITADO em %s e a linha REJEITADOS: não o cita" % ref)
    for lm in col["promo"]:
        if not tem("promover", lm):
            defeitos.append("a colheita tem PROMOVER? %s e o bloco não tem a linha promover dele" % lm)
    for ref in col["ign"] + col["ja"]:
        if not cita(ref, finais.get("IGNORADOS/JA_COLHIDOS:", "")):
            defeitos.append("a colheita tem IGNORADO/JA_COLHIDO %s e a linha IGNORADOS/JA_COLHIDOS: não o cita" % ref)
    for lm in col["pend"]:
        if not any(r["tipo"] == "inv" and lm in (r["lm"] + " " + r["delta"]) for r in rows):
            defeitos.append("a colheita tem INV_PENDENTE %s e o bloco não tem a linha inv dele" % lm)

    contaminado = finais.get("CONTAMINAÇÃO:", "").lower().startswith("sim")
    if defeitos:
        for d in defeitos:
            erro("🔴 bloco: " + d)
        fim("BLOCO INVÁLIDO", "despache o curador de novo com as linhas acima; nada foi aplicado.")
        return 2
    for r in autos:
        diz("AUTO " + r["delta_n"])
        diz("   simples: " + r["simples"])
    for r in perguntas:
        diz("PERGUNTA %s %s %s" % (r["n"], r["tipo"], r["delta_n"]))
        diz("   simples: " + r["simples"])
    if contaminado:
        diz("AVISO contaminação declarada pelo curador: " + finais["CONTAMINAÇÃO:"])
    diz("resumo-bloco: auto=%d pergunta=%d descartar=%d nao_julgado=%d contaminacao=%s"
        % (len(autos), len(perguntas), contagem["DESCARTAR"], contagem["NAO_JULGADO"], "sim" if contaminado else "nao"))
    fim("BLOCO VÁLIDO", "aplique as linhas AUTO sem perguntar e leve as linhas PERGUNTA à pessoa.")
    return 0


# ── --self-test ─────────────────────────────────────────────────────────────────────────────────
def self_test():
    eu = os.environ.get("SDD_CURATOR_SELF") or ""
    sh = os.environ.get("SDD_CURATOR_BASH") or "bash"
    if not eu or not os.path.isfile(eu):
        falha("não sei o caminho deste script (SDD_CURATOR_SELF)", "rode como: bash sdd/bin/playbook-curator.sh --self-test")
    eu = os.path.abspath(eu)
    lint = os.path.join(os.path.dirname(eu), "playbook-lint.sh")
    pacote = os.path.abspath(os.path.join(os.path.dirname(eu), "..", ".."))  # os check= das fixtures partem daqui
    fx = os.environ.get("PLAYBOOK_CURATOR_FIXTURES") or os.path.join(os.path.dirname(eu), "..", "fixtures", "playbook", "curadoria")
    fx = os.path.abspath(fx)
    falhas = []
    nomes = ["DESIGN_FIXTURE.md", "BUILD_REPORT_FIXTURE.md", "AVAL-AT-002.log", "playbook-base.md", "playbook-mordeu2.md",
             "playbook-inv.md", "invariants-inv.md", "delta-lm020.txt", "bloco-ok.txt",
             os.path.join("replay", "BUILD_REPORT_REPLAY.md"), os.path.join("replay", "playbook-replay.md")]
    ausentes = [n for n in nomes if not os.path.isfile(os.path.join(fx, n))]
    diz("self-test — fixtures em " + fx)
    if ausentes:
        for n in ausentes:
            erro("  ❌ fixture ausente: " + n)
        erro("🔴 self-test: fixtures do pacote ausentes (o init só as copia na 1ª instalação)")
        fim("SELF-TEST FALHOU", "copie sdd/fixtures/playbook/curadoria do pacote, ou aponte PLAYBOOK_CURATOR_FIXTURES para ela.")
        return 2
    tmp = tempfile.mkdtemp(prefix="pbcur-")
    try:
        amb = dict(os.environ, SDD_TRACE_DIR=os.path.join(tmp, "traces"))
        amb.pop("SDD_TRACE", None)

        def roda(args, entrada=None, env=None):
            r = subprocess.run([sh, eu] + args, capture_output=True, encoding="utf-8", errors="replace", cwd=pacote,
                               env=env or amb, input=entrada, stdin=None if entrada is not None else subprocess.DEVNULL)
            return r.returncode, r.stdout, r.stderr

        def espera(descr, rc_esperado, padrao, args, proibido="", entrada=None):
            rc, so, se = roda(args, entrada)
            tudo = so + se
            if rc != rc_esperado:
                falhas.append(descr)
                diz("  ❌ %s → exit %d (esperado %d)" % (descr, rc, rc_esperado))
            elif padrao and not re.search(padrao, tudo, re.M):
                falhas.append(descr)
                diz("  ❌ %s → exit ok, mas a saída não tem /%s/" % (descr, padrao))
            elif proibido and re.search(proibido, tudo, re.M):
                falhas.append(descr)
                diz("  ❌ %s → exit ok, mas a saída TEM /%s/ (proibido)" % (descr, proibido))
            else:
                diz("  ✅ %s → exit %d" % (descr, rc))
            return rc, so, se

        def confere(descr, ok):
            if ok:
                diz("  ✅ " + descr)
            else:
                falhas.append(descr)
                diz("  ❌ " + descr)

        def grava(nome, texto):
            p = os.path.join(tmp, nome)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w", encoding="utf-8") as f:
                f.write(texto)
            return p

        # O lint exige um repositório git, e a cópia em que o Verify Gate roda não tem: o self-test leva o dele.
        repo_lint = os.path.join(tmp, "repo-lint")
        os.makedirs(repo_lint)
        amb_lint = {k: v for k, v in os.environ.items() if k not in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE")}
        try:
            git_ok = subprocess.run(["git", "init", "-q"], cwd=repo_lint, env=amb_lint, capture_output=True).returncode == 0
        except OSError:
            git_ok = False
        if not git_ok:
            erro("🔴 self-test: não consegui criar o repositório temporário do lint (git init)")
            fim("SELF-TEST FALHOU", "confira se o git está instalado e rode de novo.")
            return 2

        def lint_ok(args):
            r = subprocess.run([sh, lint] + args, capture_output=True, encoding="utf-8", errors="replace", cwd=repo_lint,
                               env=amb_lint, stdin=subprocess.DEVNULL)
            return r.returncode, r.stdout + r.stderr

        base = os.path.join(fx, "playbook-base.md")
        m2 = os.path.join(fx, "playbook-mordeu2.md")
        pi, ii = os.path.join(fx, "playbook-inv.md"), os.path.join(fx, "invariants-inv.md")
        rp = os.path.join(fx, "replay")
        vazio = os.path.join(tmp, "vazio")
        os.makedirs(vazio)

        diz("— VERMELHOS (se algum passar, o curator não avalia nada) —")
        espera("--colher em pasta vazia, playbook sem promoção pendente ⇒ exit 1 e '0 deltas'", 1,
               r"0 deltas colhidos", ["--colher", vazio, os.path.join(rp, "playbook-replay.md")])
        espera("--colher sem playbook ⇒ exit 2, nunca '0 deltas' verde", 2, r"playbook não encontrado",
               ["--colher", vazio, os.path.join(tmp, "nao-existe.md")], proibido=r"NADA A COLHER")
        espera("--colher em pasta que não existe ⇒ exit 64", 64, r"pasta não encontrada",
               ["--colher", os.path.join(tmp, "nao-existe"), base])
        d = grava("d-inexistente.txt", "LM-999 ajudou+1\n")
        rc, so, _se = espera("--aplicar com ID inexistente ⇒ exit 2", 2, r"não existe como bullet ativo", ["--aplicar", d, base])
        confere("--aplicar inválido ⇒ stdout vazio (nada a copiar)", so == "")
        d = grava("d-tomb.txt", "LM-022 ajudou+1\n")
        espera("--aplicar contador em tombstone ⇒ exit 2", 2, r"não existe como bullet ativo", ["--aplicar", d, base])
        d = grava("d-sec.txt", "ADD Seção Inventada :: sup: `x` :: r. **Do instead:** y.\n")
        espera("--aplicar ADD em seção fora da lista ⇒ exit 2", 2, r"fora da lista", ["--aplicar", d, base])
        d = grava("d-mal.txt", "LM-020 ajudou++\n")
        espera("--aplicar linha malformada ⇒ exit 2", 2, r"fora da gramática", ["--aplicar", d, base])
        espera("candidato sem evidencia ⇒ REJEITADO e nunca CANDIDATO", 0, r"REJEITADO .*sem linha 'evidencia:'",
               ["--colher", fx, base], proibido=r"CANDIDATO #.*termo_candidato_b")
        espera("candidato sem 'Do instead' ⇒ REJEITADO", 0, r"REJEITADO .*regra: sem 'Do instead:'",
               ["--colher", fx, base], proibido=r"CANDIDATO #.*termo_candidato_d")
        espera("veredito N.A. não conta; linha fora da seção não conta", 0, r"DELTA LM-020 ajudou\+1",
               ["--colher", fx, base], proibido=r"DELTA LM-016 ajudou|DELTA LM-021")
        espera("linha ✅ que cita LM-020 não vira mordeu", 0, "", ["--colher", fx, base], proibido=r"DELTA LM-020 mordeu")
        espera("--desde posterior ⇒ JA_COLHIDO e sem ajudou", 0, r"JA_COLHIDO DESIGN_FIXTURE\.md",
               ["--colher", fx, base, "--desde", "2026-09-03"], proibido=r"DELTA LM-020 ajudou")
        espera("FAIL dentro de identificador não vira mordeu (replay)", 0, r"DELTA LM-003 ajudou\+1",
               ["--colher", rp, os.path.join(rp, "playbook-replay.md")], proibido=r"DELTA LM-003 mordeu")
        d = grava("c-mal.txt", "LM-030 ajudou++\n")
        rc, so, _se = espera("--cruzar com delta malformado ⇒ exit 2", 2, r"fora da gramática", ["--cruzar", d, pi, ii])
        confere("--cruzar inválido ⇒ stdout vazio", so == "")
        sem = grava("c-sem-inv.md", "# nada\n")
        espera("--cruzar com invariantes sem a seção ⇒ exit 2", 2, r"sem a seção", ["--cruzar", d, pi, sem])
        t30 = grava("c-t30.txt", "TOMBSTONE LM-030 :: teste\n")
        _rc, so, _se = roda(["--aplicar", t30, pi, "2026-09-24"])
        pi_tomb = grava("pi-tomb.md", so)
        espera("trava: aposentadoria de origem sem ajuste ⇒ exit 2 com a invariante e a lição", 2,
               r"trava INV: INV-001 tem origem=LM-030.*retire o TOMBSTONE LM-030", ["--validar-inv", pi_tomb, ii])
        pend = grava("pi-pend.md", ler(pi).replace("- [LM-036] ajudou=0 mordeu=0", "- [LM-036] ajudou=0 mordeu=1"))
        espera("trava: lição nova no universo sem classificação ⇒ exit 2 nomeando a lição", 2,
               r"trava INV: LM-036 entra no universo sem classificação", ["--validar-inv", pend, ii])
        colh = grava("stg/colheita.txt", roda(["--colher", fx, base])[1])
        for n in ("DESIGN_FIXTURE.md", "BUILD_REPORT_FIXTURE.md", "AVAL-AT-002.log"):
            shutil.copyfile(os.path.join(fx, n), os.path.join(tmp, "stg", n))
        selo = grava("selo.txt", roda(["--selar", os.path.join(tmp, "stg")])[1])
        verde = grava("comparar-ok.txt", "RESULTADO: SÓ O PERMITIDO MUDOU\n→ siga.\n")
        bloco_ok = ler(os.path.join(fx, "bloco-ok.txt"))

        def bloco(nome, texto):
            return ["--conferir-bloco", colh, grava("blocos/" + nome, texto), base, selo, verde]

        espera("bloco com contador AUTO que a colheita não tem ⇒ exit 2", 2, r"não está na colheita",
               bloco("inventado.txt", bloco_ok.replace("| 1 | contador | LM-020 | LM-020 ajudou+1 |",
                                                       "| 1 | contador | LM-021 | LM-021 ajudou+1 |")))
        espera("bloco com contador AUTO de +5 ⇒ exit 2", 2, r"AUTO pede um delta de contador com \+1",
               bloco("mais5.txt", bloco_ok.replace("| LM-020 ajudou+1 |", "| LM-020 ajudou+5 |")))
        espera("bloco com contador AUTO apontando outra linha que existe ⇒ exit 2", 2, r"tem de ser a da colheita",
               bloco("outra-linha.txt", bloco_ok.replace("| DESIGN_FIXTURE.md:16 (", "| DESIGN_FIXTURE.md:15 (")))
        espera("bloco com sugestão AUTO ⇒ exit 2 (sugestão vai para pergunta)", 2, r"AUTO só vale para contador",
               bloco("sug-auto.txt", bloco_ok.replace("| DESCARTAR (a causa do achado não é a regra do aviso) |", "| AUTO |")))
        espera("bloco que omite uma linha da colheita ⇒ exit 2", 2, r"a colheita tem SUGESTAO",
               bloco("sumiu.txt", "\n".join(ln for ln in bloco_ok.split("\n") if "| sugestao |" not in ln)))
        fora = grava("comparar-fora.txt", "FORA: /x/sdd/playbook.md\nRESULTADO: HÁ ESCRITA FORA\n")
        espera("fronteira com FORA: ⇒ exit 2, mesmo com o bloco certo", 2, r"a fronteira acusou escrita fora",
               ["--conferir-bloco", colh, grava("blocos/ok1.txt", bloco_ok), base, selo, fora])
        espera("saída da fronteira vazia (não verificada) ⇒ exit 2", 2, r"fronteira não verificada",
               ["--conferir-bloco", colh, grava("blocos/ok2.txt", bloco_ok), base, selo, grava("comparar-vazio.txt", "")])
        with open(os.path.join(tmp, "stg", "AVAL-AT-002.log"), "a", encoding="utf-8") as f:
            f.write("AT-009 ❌ FAIL — linha plantada depois do selo\n")
        espera("staging mexido depois do selo ⇒ exit 2", 2, r"o staging mudou depois do selo: AVAL-AT-002\.log mudou",
               bloco("ok3.txt", bloco_ok))
        shutil.copyfile(os.path.join(fx, "AVAL-AT-002.log"), os.path.join(tmp, "stg", "AVAL-AT-002.log"))
        ruim = grava("inv-ruim.txt", "- [INV-009] estado=talvez origem=seed :: x · por quê: y\n")
        rc, so, _se = espera("--aplicar-inv com linha fora da gramática ⇒ exit 2", 2, r"fora da gramática das invariantes",
                             ["--aplicar-inv", ruim, ii])
        confere("--aplicar-inv inválido ⇒ stdout vazio", so == "")

        diz("— VERDES —")
        espera("fixtures ⇒ DELTA LM-020 ajudou+1 de tabela", 0,
               r"^DELTA LM-020 ajudou\+1 · conf=[0-9-]+ · evidencia=DESIGN_FIXTURE\.md:\d+", ["--colher", fx, base])
        espera("fixtures ⇒ DELTA LM-016 mordeu+1 de achado", 0, r"^DELTA LM-016 mordeu\+1 .*evidencia=AVAL-AT-002\.log:3",
               ["--colher", fx, base])
        espera("PROMOVER? só para mordeu >= 2 não promovido", 0, r"^PROMOVER\? LM-004 mordeu=2 .*promover a mecanismo",
               ["--colher", fx, m2], proibido=r"PROMOVER\? LM-00[12]")
        espera("pasta vazia com promoção pendente no playbook ⇒ exit 0: a pergunta de promoção é obrigatória", 0,
               r"^PROMOVER\? LM-004[\s\S]*promocoes=1", ["--colher", vazio, base])
        espera("próximo ID = maior entre ativos e tombstones + 1 (tombstone nunca reusado)", 0, r"^CANDIDATO #1 → LM-023 ",
               ["--colher", fx, base])
        espera("'Do instead:' em chave própria e continuação indentada ⇒ CANDIDATO #2 numa linha só", 0,
               r"^   delta: ADD Backend :: sup: `termo_candidato_c` `chave_propria` :: Regra em duas linhas, com continuação indentada\. \*\*Do instead:\*\* ação em chave própria, também em duas linhas\. → ficha: — · promovido_para: —$",
               ["--colher", fx, base])
        espera("SUGESTAO por termo de sup:, sem virar DELTA", 0, r"^SUGESTAO mordeu\? LM-020 — termo `fila_de_envio`",
               ["--colher", fx, base], proibido=r"DELTA LM-020 mordeu")
        espera("**mordeu** na célula de veredito ⇒ mordeu+1, não ajudou (replay)", 0,
               r"^DELTA LM-005 mordeu\+1 .*evidencia=BUILD_REPORT_REPLAY\.md:\d+",
               ["--colher", rp, os.path.join(rp, "playbook-replay.md")], proibido=r"DELTA LM-005 ajudou")
        dl = os.path.join(fx, "delta-lm020.txt")
        rc, so, _se = espera("--aplicar ⇒ contador somado e conf nova", 0, r"^- \[LM-020\] ajudou=1 mordeu=0 · conf=2026-09-02 ·",
                             ["--aplicar", dl, base, "conf=2026-09-02"])
        confere("continuação do LM-020 preservada", "\n  continuação de teste do LM-020" in so)
        confere("stdout do --aplicar é só o playbook (sem RESULTADO:)", "RESULTADO:" not in so)
        d = grava("d-composto.txt", "# composto\nLM-020 ajudou+2\nLM-016 mordeu+1\nLM-004 promovido_para=sdd/hooks/pre-commit\n"
                  "ADD Reviews / harness :: sup: `termo_novo` `outro` :: Regra nova. **Do instead:** ação nova. → ficha: —\n"
                  "TOMBSTONE LM-021 :: aposentado no self-test\nREFINE LM-001 :: regra refinada. **Do instead:** ação refinada. · promovido_para: —\n")
        rc, so, _se = roda(["--aplicar", d, base, "2026-09-02"])
        comp = grava("composto.md", so)
        confere("--aplicar composto ⇒ texto esperado (2 contadores, promoção, ADD=LM-023, TOMBSTONE, REFINE)",
                rc == 0 and all(re.search(p, so, re.M) for p in (
                    r"^- \[LM-020\] ajudou=2 mordeu=0", r"^- \[LM-016\] ajudou=0 mordeu=1",
                    r"^- \[LM-004\] .*promovido_para: sdd/hooks/pre-commit$",
                    r"^- \[LM-023\] ajudou=0 mordeu=0 · conf=2026-09-02 · sup: `termo_novo` `outro` :: Regra nova",
                    r"^- \[LM-021\] ☠ 2026-09-02 :: aposentado no self-test",
                    r"^- \[LM-001\] ajudou=0 mordeu=0 · conf=2026-09-02 · sup: `termo_base` :: regra refinada")))
        rc, saida = lint_ok([comp])
        confere("a saída do composto passa no playbook-lint.sh" + ("" if rc == 0 else " — " + saida.strip()[:200]), rc == 0)
        d = grava("d-cont.txt", "LM-020 ajudou+3\nLM-016 mordeu+2\nLM-004 ajudou+1\n")
        cont = grava("cont.md", roda(["--aplicar", d, base, "2026-09-02"])[1])
        rc, saida = lint_ok(["--anti-collapse", base, cont])
        confere("delta só de contadores atravessa o --anti-collapse com 0 alterados", rc == 0 and "0 (0%)" in saida)
        rc, saida = lint_ok(["--anti-collapse", base, comp])
        confere("o --anti-collapse bloqueia o composto (3 de 6 reescritos)", rc == 1 and "reescritos" in saida)
        d = grava("d-nada.txt", "# só comentário\n")
        confere("delta vazio ⇒ saída idêntica à entrada", roda(["--aplicar", d, base])[1] == ler(base))
        d = grava("c-nada.txt", "LM-031 mordeu+1\nLM-030 ajudou+1\n")
        espera("--cruzar sem aposentadoria de origem nem lição nova no universo ⇒ exit 0", 0,
               r"^resumo-inv: afetadas=0 pendentes=0$", ["--cruzar", d, pi, ii], proibido=r"INV_")
        espera("--cruzar aposentando origem única promovida ⇒ origem=seed + check do bullet", 3,
               r"^   ajuste: - \[INV-001\] estado=ok origem=seed check=sdd/bin/playbook-curator\.sh :: Regra um", ["--cruzar", t30, pi, ii])
        d = grava("c-t31.txt", "TOMBSTONE LM-031 :: t\n")
        espera("--cruzar aposentando 1 de 2 origens ⇒ lista sem ela", 3,
               r"^   ajuste: - \[INV-002\] estado=humano origem=LM-032 :: Regra dois", ["--cruzar", d, pi, ii])
        d = grava("c-t3132.txt", "TOMBSTONE LM-031 :: t\nTOMBSTONE LM-032 :: t\n")
        espera("--cruzar com 2 aposentadorias da mesma invariante ⇒ 1 ajuste agregado", 3,
               r"^   ajuste: - \[INV-002\] estado=humano origem=seed :: Regra dois", ["--cruzar", d, pi, ii],
               proibido=r"origem=LM-03[12] ::")
        d = grava("c-t33.txt", "TOMBSTONE LM-033 :: t\n")
        espera("--cruzar aposentando origem única com check curado ⇒ origem=seed mantendo o check", 3,
               r"^   ajuste: - \[INV-003\] estado=ok origem=seed check=sdd/bin/playbook-lint\.sh ::", ["--cruzar", d, pi, ii])
        d = grava("c-t35.txt", "TOMBSTONE LM-035 :: t\n")
        espera("--cruzar aposentando lição descartada ⇒ remover a linha do descarte", 3, r"^INV_AFETADA descarte LM-035",
               ["--cruzar", d, pi, ii])
        espera("--cruzar sempre oferece retirar a aposentadoria", 3, r"^   ou: retirar o TOMBSTONE LM-030$", ["--cruzar", t30, pi, ii])
        d = grava("c-pend.txt", "LM-036 mordeu+1\nLM-037 promovido_para=sdd/bin/x.sh\n")
        espera("--cruzar com 2 lições novas no universo ⇒ INV-006 e INV-007 em sequência", 3,
               r"proposta A: - \[INV-006\] .*origem=LM-036[\s\S]*proposta A: - \[INV-007\] .*origem=LM-037", ["--cruzar", d, pi, ii])
        espera("--cruzar lê o delta do stdin (-)", 3, r"^INV_AFETADA INV-001", ["--cruzar", "-", pi, ii], entrada=ler(t30))
        espera("--colher --inv ⇒ INV_PENDENTE para mordeu 0→1 sem classificação", 0, r"^INV_PENDENTE LM-005 \(mordeu 0→1\)",
               ["--colher", rp, os.path.join(rp, "playbook-replay.md"), "--inv", ii])
        espera("trava: par base ⇒ exit 0", 0, r"trava INV: par válido", ["--validar-inv", pi, ii])
        ajuste = next((ln[len("   ajuste: "):] for ln in roda(["--cruzar", t30, pi, ii])[1].split("\n")
                       if ln.startswith("   ajuste: ")), "")
        linhas_inv = grava("inv-linhas.txt", ajuste + "\n- [LM-036] descartado :: teste\nREMOVER LM-035\n")
        rc, so, _se = roda(["--aplicar-inv", linhas_inv, ii])
        ii_aj = grava("ii-aj.md", so)
        confere("--aplicar-inv troca a linha do mesmo ID, acrescenta o descarte novo e remove o pedido",
                rc == 0 and "origem=seed check=sdd/bin/playbook-curator.sh" in so and "- [LM-036] descartado :: teste" in so
                and "[LM-035]" not in so and so.count("[INV-001]") == 1 and "RESULTADO:" not in so)
        ii_aj = grava("ii-aj.md", so.replace("- [LM-036] descartado :: teste\n", "").replace("## Descartados\n", "## Descartados\n\n- [LM-035] descartado :: ferramenta, não regra\n"))
        espera("trava: aposentadoria + ajuste proposto pelo --cruzar ⇒ exit 0", 0, r"trava INV: par válido",
               ["--validar-inv", pi_tomb, ii_aj])
        espera("bloco de exemplo confere com a colheita das fixtures ⇒ exit 0, AUTO e PERGUNTA", 0,
               r"^AUTO LM-020 ajudou\+1[\s\S]*^PERGUNTA \d+ add ADD [\s\S]*^resumo-bloco: auto=2 pergunta=3",
               bloco("ok.txt", bloco_ok))
        # contagem que põe a lição no universo das invariantes não entra sozinha: vai junto da classificação
        os.makedirs(os.path.join(tmp, "stg2"))
        shutil.copyfile(os.path.join(rp, "BUILD_REPORT_REPLAY.md"), os.path.join(tmp, "stg2", "BUILD_REPORT_REPLAY.md"))
        prp = os.path.join(rp, "playbook-replay.md")
        colh2 = grava("stg2/colheita.txt", roda(["--colher", os.path.join(tmp, "stg2"), prp, "--inv", ii])[1])
        selo2 = grava("selo2.txt", roda(["--selar", os.path.join(tmp, "stg2")])[1])
        ev = dict(re.findall(r"^DELTA (LM-\d{3}) \w+\+1 .*?evidencia=(\S+)", ler(colh2), re.M))
        bloco2 = grava("blocos/replay.txt", "<<<CURADORIA\nFEATURE: REPLAY\n| " + " | ".join(COLUNAS) + " |\n|---|---|---|---|---|---|---|\n"
                       "| 1 | contador | LM-003 | LM-003 ajudou+1 | %s | O aviso foi seguido. | AUTO |\n"
                       "| 2 | contador | LM-005 | LM-005 mordeu+1 | %s | O erro aconteceu de novo. | AUTO |\n"
                       "| 3 | inv | LM-005 | - [LM-005] descartado :: defeito de ferramenta | --cruzar: INV_PENDENTE LM-005 | A lição não vira regra permanente. | ACEITAR |\n"
                       "REJEITADOS: nenhum\nNAO_JULGADO: nenhum\nIGNORADOS/JA_COLHIDOS: nenhum\nCONTAMINAÇÃO: não\n>>>\n"
                       % (ev.get("LM-003", "?"), ev.get("LM-005", "?")))
        espera("contador que põe a lição no universo das invariantes ⇒ PERGUNTA, não AUTO", 0,
               r"^AUTO LM-003 ajudou\+1[\s\S]*^PERGUNTA 2 contador LM-005 mordeu\+1[\s\S]*^PERGUNTA 3 inv ",
               ["--conferir-bloco", colh2, bloco2, prp, selo2, verde], proibido=r"^AUTO LM-005")
        # o que já foi julgado numa curadoria anterior não conta de novo
        shutil.copyfile(colh2, os.path.join(tmp, "stg2", "CURATOR-colhidos.txt"))
        espera("colheita repetida com o registro do já julgado ⇒ exit 1 e JA_JULGADO, sem DELTA", 1,
               r"^JA_JULGADO 2 linha", ["--colher", os.path.join(tmp, "stg2"), prp], proibido=r"^DELTA ")

        # trace: vermelho (desligado ⇒ nada) antes do verde (1 linha JSON válida por feature)
        tr = os.path.join(tmp, "traces")
        shutil.rmtree(tr, ignore_errors=True)
        roda(["--colher", fx, base], env=dict(amb, SDD_TRACE="off"))
        confere("SDD_TRACE=off ⇒ nenhum trace", not os.path.exists(os.path.join(tr, "FIXTURE.jsonl")))
        roda(["--colher", fx, base])
        ok = False
        try:
            j = json.loads(ler(os.path.join(tr, "FIXTURE.jsonl")).strip().split("\n")[-1])
            ok = j.get("src") == "curator" and j.get("kind") == "colher" and j.get("exit") == 0 and all(
                isinstance(j.get(k), int) for k in ("deltas", "ajudou", "mordeu", "candidatos", "rejeitados", "promocoes", "sugestoes"))
        except (OSError, ValueError):
            ok = False
        confere("--colher grava o resumo em traces/FIXTURE.jsonl (src curator, 7 contadores)", ok)
        esquisito = os.path.join(tmp, "aspas")
        os.makedirs(esquisito)
        grava(os.path.join("aspas", 'BUILD_REPORT_qu"o te.md'), "# BUILD REPORT\n\n**Date**: 2026-09-09\n")
        roda(["--colher", esquisito, base])
        ok = False
        try:
            json.loads(ler(os.path.join(tr, "qu_o_te.jsonl")).strip())
            ok = True
        except (OSError, ValueError):
            ok = False
        confere("feature com aspas e espaço ⇒ nome de arquivo sanitizado e JSON válido", ok)
        antes = len(ler(os.path.join(tr, "FIXTURE.jsonl")).strip().split("\n"))
        roda(["--colher", vazio, base])
        confere("pasta sem relatório nem design ⇒ sem trace novo",
                len(ler(os.path.join(tr, "FIXTURE.jsonl")).strip().split("\n")) == antes)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if falhas:
        erro("🔴 self-test: %d falha(s) — o curator NÃO está provando o que promete" % len(falhas))
        fim("SELF-TEST FALHOU", "o 1º caso com ❌ acima diz a regra que quebrou.")
        return 2
    diz("🟢 self-test: todos os vermelhos e os verdes confirmados")
    fim("SELF-TEST OK", "o curator prova o que promete nesta máquina.")
    return 0


def main(argv):
    if not argv:
        uso("falta o modo")
    modo, args = argv[0], argv[1:]
    if modo == "--preparar":
        return preparar(args)
    if modo == "--colher":
        return colher(args)
    if modo == "--aplicar":
        return aplicar(args)
    if modo == "--cruzar":
        return cruzar(args)
    if modo == "--validar-inv":
        return validar_inv(args)
    if modo == "--aplicar-inv":
        return aplicar_inv(args)
    if modo == "--selar":
        return selar(args)
    if modo == "--conferir-bloco":
        return conferir_bloco(args)
    if modo == "--self-test":
        if args:
            uso("--self-test não recebe argumento")
        return self_test()
    uso("modo desconhecido: " + modo)


try:
    sys.exit(main(sys.argv[1:]))
except BrokenPipeError:
    sys.exit(0)
except Exception as e:
    # Sem isto, o Python sai 1, o código de "leu tudo e não achou nada", e uma falha de leitura vira "0 deltas".
    erro("🛑 playbook-curator: não consegui terminar: %s: %s" % (type(e).__name__, e))
    fim("FALHA", "isto não é \"0 deltas\": confira a permissão dos arquivos citados e rode de novo; nada foi aplicado.", sys.stderr)
    sys.exit(2)
PY
rc=$?
[ -z "${TMPIN}" ] || rm -f "${TMPIN}"
exit "${rc}"
