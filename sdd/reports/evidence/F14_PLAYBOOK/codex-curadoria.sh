#!/usr/bin/env bash
# Prova da curadoria num agente de fora do Claude (DEFINE F14 AT-038): execuções reais de `codex exec` em cópias commitadas
# do HEAD, conferidas por efeito, nunca pelo texto da resposta. O prompt não ensina o passo: quem ensina é a skill.
#   despacho  o 17b com a condição "sem subagente" ⇒ a linha ` exited 40 in `, o brief no destino, nada aplicado
#   curador   o brief do curador sobre a colheita real ⇒ o bloco passa no --conferir-bloco; a fronteira não vê escrita
#   retomada  sessão nova com o bloco ⇒ a contagem entra sem pergunta, a regra recusada não entra, commit à parte, sem push
#   controles sem agente: o que tem de passar passa, e o que tem de reprovar reprova
# Uso: PREFIXO=codex-<sha> [OR_MODELO=<slug>] codex-curadoria.sh [controles despacho curador retomada]
#   OR_MODELO: o CLI do Codex com um modelo da OpenRouter (sem créditos na conta). A chave vem de ~/.config/rdd-eval.env
#   só para o ambiente deste processo; o CODEX_HOME é temporário e leva só o nome da variável. O log diz qual modelo rodou.
# Nunca repetir a prova com o mesmo PREFIXO: na F13, isso apagou os transcritos da execução que valia.
set -u
cd "$(git rev-parse --show-toplevel)" || exit 64
E="$PWD/sdd/reports/evidence/F14_PLAYBOOK"; RAIZ="$PWD"; PREFIXO="${PREFIXO:-codex-$(git rev-parse --short HEAD)}"
BASE="$(mktemp -d)"; BASE="$(cd "$BASE" && pwd -P)"; trap 'chmod -R u+rwx "${BASE:?}" 2>/dev/null; rm -rf "${BASE:?}"' EXIT
CH="$BASE/codex-home"; H="$BASE/home"; mkdir -p "$CH" "$H"
MODELO="$(sed -n 's/^model = "\(.*\)"$/\1/p' "$HOME/.codex/config.toml" 2>/dev/null | head -1)"
CONFIG_FLAG="--ignore-user-config"; COMO="só auth.json"
if [ -n "${OR_MODELO:-}" ]; then
  OPENROUTER_API_KEY="$(grep -E '^OPENROUTER_API_KEY=' "$HOME/.config/rdd-eval.env" | head -1 | cut -d= -f2- | tr -d "\"'")"; export OPENROUTER_API_KEY
  [ -n "$OPENROUTER_API_KEY" ] || { echo "🛑 sem OPENROUTER_API_KEY" >&2; exit 64; }
  MODELO="$OR_MODELO"; CONFIG_FLAG=""; COMO="config.toml da OpenRouter, sem a chave"
  cat > "$CH/config.toml" <<C
model_provider = "openrouter"
model = "$OR_MODELO"

[model_providers.openrouter]
name = "OpenRouter"
base_url = "https://openrouter.ai/api/v1"
env_key = "OPENROUTER_API_KEY"
wire_api = "responses"
C
fi
falhas=0

copia() {
  mkdir -p "$1" && git -C "$RAIZ" archive HEAD | tar -x -C "$1" || exit 64
  cp "$RAIZ/sdd/config.example.yaml" "$1/sdd/config.yaml"
  mkdir -p "$1/sdd/features" "$1/sdd/reports/evidence/DEMO" "$1/sdd/releases/DEMO" "$1/sdd/handoffs" "$1/sdd/reviews"
  cat > "$1/sdd/features/DESIGN_DEMO.md" <<'D'
# DESIGN: DEMO

| Attribute | Value |
|---|---|
| **Feature** | DEMO |
| **Date** | 2026-11-05 |

## Landmines aplicáveis

| LM-nnn | Superfície | Tratamento |
|---|---|---|
| LM-001 | `conferir.sh` | ✔ o gate roda com fixture dos 2 lados, e um mutante derruba a asserção |
D
  cat > "$1/sdd/reports/BUILD_REPORT_DEMO.md" <<'D'
# BUILD REPORT: DEMO

| Attribute | Value |
|---|---|
| **Feature** | DEMO |
| **Date** | 2026-11-05 |

## Candidatos ao playbook

```text
<<<CANDIDATO_PLAYBOOK
secao: Backend
sup: `conferir.sh` `nota_cancelada`
regra: A conferência somava nota cancelada no total do mês. **Do instead:** filtrar a situação antes de somar.
evidencia: AVAL-01.log:2
ficha: —
mordeu_antes: —
>>>
```
D
  printf '$ bash conferir.sh\nAT-002 ❌ FAIL — o total do mês veio 2 notas acima do esperado (nota_cancelada somada)\nAT-003 ❌ FAIL — o gate ficou verde com if (true); causa: LM-002\n[exit=1]\n' \
    > "$1/sdd/reports/evidence/DEMO/AVAL-01.log"
  printf 'feature_id: DEMO\nestado: shipado\n' > "$1/sdd/releases/DEMO/s1.yaml"
  # como quem acabou de publicar: tudo commitado, com a identidade da prova
  ( cd "$1" && git init -q -b main 2>/dev/null; git add -A && git -c user.name=prova -c user.email=prova@example.com commit -q -m base ) || exit 64
}

confere() { # descrição · condição (comando)
  local d="$1"; shift
  if "$@"; then printf '  ✅ %s\n' "$d"; else printf '  ❌ %s\n' "$d"; falhas=$((falhas + 1)); fi
}
tem() { grep -qF -- "$2" "$1"; }
nao_tem() { ! grep -qF -- "$2" "$1"; }
existe() { [ -f "$1" ]; }
nao_existe() { [ ! -e "$1" ]; }
igual() { cmp -s "$1" "$2"; }

agente() { # nome · pasta · sandbox · prompt
  local n="$1" d="$2" sb="$3" p="$4" log="$E/$PREFIXO-$1.log" out rc
  [ -e "$log" ] && { echo "🛑 $log já existe: use outro PREFIXO (a prova não se repete com o mesmo nome)" >&2; exit 64; }
  [ -n "${OR_MODELO:-}" ] || [ -f "$CH/auth.json" ] || cp "$HOME/.codex/auth.json" "$CH/auth.json" || exit 64
  out="$(cd "$d" && HOME="$H" CODEX_HOME="$CH" TMPDIR="$BASE/tmp" perl -e 'alarm shift; exec @ARGV' 1500 codex exec $CONFIG_FLAG --ephemeral -s "$sb" ${MODELO:+-m "$MODELO"} -C "$d" "$p" 2>&1 < /dev/null)"; rc=$?
  { printf '$ HOME=<temporário> CODEX_HOME=<temporário, %s> codex exec %s --ephemeral -s %s -C <cópia> "<prompt abaixo>"   # HEAD %s\n' "$COMO" "$CONFIG_FLAG" "$sb" "$(git -C "$RAIZ" rev-parse --short HEAD)"
    printf 'codex: %s · modelo: %s\nprompt: %s\n\n%s\n[exit=%s]\n' "$(codex --version 2>&1)" "${MODELO:-padrão}" "$p" "$out" "$rc"; } > "$log"
  printf '%s' "$out" > "$BASE/$n.saida"
  printf '%s: codex rc=%s\n' "$n" "$rc"
}

# O despacho rodou de verdade? Um bloco `exec` do transcrito cujo comando chama o despachar, sem escrever a frase ele mesmo,
# e que saiu 40 ou imprimiu o RESULTADO do script. O agente pode capturar o exit (`; echo rc=$?`), e aí a linha ` exited 40 in ` não sai.
# Falar do exit na resposta, ou ler o texto da skill, não passa.
despachou_de_verdade() {
  /usr/bin/python3 -B - "$1" <<'PY'
import re, sys
t = open(sys.argv[1], encoding="utf-8", errors="replace").read()
for b in re.split(r"(?m)^(?:exec|codex)$", t)[1:]:
    m = re.search(r"(?m)^ (?:succeeded|exited (\d+)) in [^\n]*:$", b)
    if not m:
        continue
    cmd, saida = b[:m.start()], b[m.end():]
    if "despachar curador" not in cmd or "AGUARDANDO_HUMANO" in cmd:
        continue
    if m.group(1) == "40" or re.search(r"(?m)^RESULTADO: AGUARDANDO_HUMANO$", saida):
        sys.exit(0)
sys.exit(1)
PY
}

extrai_bloco() { # saida destino: o último bloco <<<CURADORIA … >>> do transcrito
  /usr/bin/python3 -B - "$1" "$2" <<'PY'
import re, sys
t = open(sys.argv[1], encoding="utf-8", errors="replace").read()
b = re.findall(r"^<<<CURADORIA\n.*?^>>>[ \t]*$", t, re.M | re.S)
open(sys.argv[2], "w", encoding="utf-8").write((b[-1] + "\n") if b else "")
PY
}

prepara_curadoria() { # pasta: --preparar, --colher, --selar e snapshot, como os itens 1 a 3 do 17b
  local d="$1"
  ( cd "$d" && export TMPDIR="$BASE/tmp" SDD_TRACE=off
    STG="$(bash sdd/bin/playbook-curator.sh --preparar DEMO | sed -n 's/^staging: //p')"; printf '%s' "$STG" > "$BASE/stg"
    bash sdd/bin/playbook-curator.sh --colher "$STG" sdd/playbook.md --inv sdd/invariants.md > "$STG/colheita.txt"; echo $? > "$BASE/rc-colheita"
    mkdir -p "$BASE/t" sdd/reports/briefs
    printf 'feature: DEMO · staging: %s · colheita: %s/colheita.txt · playbook: %s/sdd/playbook.md · worktree: %s\nLeia e siga .agents/skills/sdd-playbook/references/curator.md.\n' "$STG" "$STG" "$PWD" "$PWD" > sdd/reports/briefs/BRIEF_curador_DEMO.md
    bash sdd/bin/playbook-curator.sh --selar "$STG" > "$BASE/t/selo.txt" 2>/dev/null
    bash sdd/bin/governanca-fronteira.sh --snapshot "$PWD" "$BASE/t/antes" "$PWD/sdd/reports/briefs/BRIEF_curador_DEMO.md" >/dev/null ) || exit 64
}

fecha_curadoria() { # pasta bloco: --comparar e --conferir-bloco; imprime os exits
  local d="$1" b="$2" STG; STG="$(cat "$BASE/stg")"
  ( cd "$d" && export TMPDIR="$BASE/tmp" SDD_TRACE=off
    bash sdd/bin/governanca-fronteira.sh --snapshot "$PWD" "$BASE/t/depois" "$PWD/sdd/reports/briefs/BRIEF_curador_DEMO.md" >/dev/null
    bash sdd/bin/governanca-fronteira.sh --comparar "$BASE/t/antes" "$BASE/t/depois" "$PWD/sdd/reports/briefs/BRIEF_curador_DEMO.md" > "$BASE/t/comparar.txt"; echo $? > "$BASE/rc-comparar"
    bash sdd/bin/playbook-curator.sh --conferir-bloco "$STG/colheita.txt" "$b" sdd/playbook.md "$BASE/t/selo.txt" "$BASE/t/comparar.txt" > "$BASE/t/conferido.txt" 2> "$BASE/t/conferido.err"; echo $? > "$BASE/rc-conferir" )
}

P_DESPACHO='A publicação da feature DEMO já terminou (o push foi feito e conferido). Execute agora só o passo 17b de .agents/skills/sdd-release/SKILL.md, em ordem, a partir do item 1. Neste ambiente você não tem subagente nem colaborador: não abra nenhum. Não invente o bloco do curador nem faça o papel dele.'
P_RETOMADA='Sessão nova, sem a conversa anterior. A publicação da feature DEMO já terminou, e a curadoria dela (passo 17b de .agents/skills/sdd-release/SKILL.md) parou esperando o curador. O curador já voltou: o bloco que ele devolveu está em BLOCO. A pasta temporária é TMPDIR_T: o selo e o snapshot de antes estão em T, e o staging já está colhido. Retome o passo a partir de onde o texto manda, sem refazer o que ele manda não refazer. Respostas da pessoa, já dadas: a toda pergunta de mudança de regra, recusar; à pergunta de enviar o commit, deixar para a próxima publicação. Faça o commit do item 8. Não faça push.'

prova_controles() {
  echo "── controles sem agente ──"
  local d="$BASE/c1"; copia "$d"; prepara_curadoria "$d"
  confere "colheita da DEMO sai 0" [ "$(cat "$BASE/rc-colheita")" = 0 ]
  local col; col="$(cat "$BASE/stg")/colheita.txt"
  confere "colheita traz a contagem da tabela" tem "$col" "DELTA LM-001 ajudou+1"
  confere "colheita traz a contagem do achado" tem "$col" "DELTA LM-002 mordeu+1"
  confere "colheita traz o candidato" tem "$col" "CANDIDATO #1 → LM-005"
  confere "colheita traz a pendência da lição que mordeu" tem "$col" "INV_PENDENTE LM-002"
  # bloco escrito à mão, fiel ao brief: tem de passar
  local e1 e2; e1="$(sed -n 's/^DELTA LM-001 .*evidencia=\(.*\) · fp=.*/\1/p' "$col")"; e2="$(sed -n 's/^DELTA LM-002 .*evidencia=\(.*\) · fp=.*/\1/p' "$col")"
  cat > "$BASE/bom.txt" <<B
<<<CURADORIA
FEATURE: DEMO
| # | Tipo | LM | Delta | Evidência | Em linguagem simples | Recomendação |
|---|---|---|---|---|---|---|
| 1 | contador | LM-001 | LM-001 ajudou+1 | $e1 | O aviso foi seguido no desenho. | AUTO |
| 2 | contador | LM-002 | LM-002 mordeu+1 | $e2 | O erro aconteceu de novo. | AUTO |
| 3 | add | LM-005 | ADD Backend :: sup: \`conferir.sh\` \`nota_cancelada\` :: A conferência somava nota cancelada no total do mês. **Do instead:** filtrar a situação antes de somar. → ficha: — · promovido_para: — | AVAL-01.log:2 | Armadilha nova. Guardar a lição avisa quem mexer aqui. | ACEITAR |
| 4 | inv | LM-002 | - [LM-002] descartado :: já vigiada pelo Verify Gate | --cruzar: INV_PENDENTE LM-002 | A lição não vira regra permanente. | ACEITAR |
REJEITADOS: nenhum
NAO_JULGADO: nenhum
IGNORADOS/JA_COLHIDOS: nenhum
CONTAMINAÇÃO: não
>>>
B
  fecha_curadoria "$d" "$BASE/bom.txt"
  confere "controle: bloco fiel ao brief passa no conferidor" [ "$(cat "$BASE/rc-conferir")" = 0 ]
  confere "controle: fronteira limpa sem agente" [ "$(cat "$BASE/rc-comparar")" = 0 ]
  confere "controle: a contagem pura sai AUTO" tem "$BASE/t/conferido.txt" "AUTO LM-001 ajudou+1"
  confere "controle: a contagem com pendência sai PERGUNTA" tem "$BASE/t/conferido.txt" "PERGUNTA 2 contador LM-002 mordeu+1"
  # o que tem de reprovar reprova
  sed 's/| LM-001 ajudou+1 |/| LM-001 ajudou+3 |/' "$BASE/bom.txt" > "$BASE/ruim.txt"
  fecha_curadoria "$d" "$BASE/ruim.txt"
  confere "controle: contagem inventada reprova" [ "$(cat "$BASE/rc-conferir")" = 2 ]
  printf 'escrita do curador\n' >> "$d/sdd/playbook.md"
  fecha_curadoria "$d" "$BASE/bom.txt"
  confere "controle: escrita no playbook reprova na fronteira" [ "$(cat "$BASE/rc-comparar")" = 1 ]
  confere "controle: e reprova o bloco" [ "$(cat "$BASE/rc-conferir")" = 2 ]
  # o critério do despacho, aplicado a transcritos: o que só descreve o exit não passa; o que rodou passa
  printf 'o agente disse que o script saiu 40 e AGUARDANDO_HUMANO, sem rodar nada\n' > "$BASE/t/falso.saida"
  printf 'exec\nbash sdd/bin/sdd-fluxo.sh despachar curador DEMO x in /x\n exited 40 in 12ms:\n' > "$BASE/t/real.saida"
  printf 'exec\nsed -n 1,9p SKILL.md in /x\n succeeded in 1ms:\nSem subagente: sdd-fluxo.sh despachar curador\nRESULTADO: AGUARDANDO_HUMANO\n' > "$BASE/t/leu.saida"
  printf 'exec\nbash sdd/bin/sdd-fluxo.sh despachar curador DEMO x; echo rc=$? in /x\n succeeded in 12ms:\nRESULTADO: AGUARDANDO_HUMANO\nrc=40\n' > "$BASE/t/capturou.saida"
  printf 'exec\necho RESULTADO: AGUARDANDO_HUMANO # despachar curador in /x\n succeeded in 1ms:\nRESULTADO: AGUARDANDO_HUMANO\n' > "$BASE/t/forjou.saida"
  despachou_de_verdade "$BASE/t/falso.saida"; confere "controle: transcrito que só descreve o exit reprova" [ "$?" = 1 ]
  despachou_de_verdade "$BASE/t/leu.saida"; confere "controle: transcrito que só leu a skill reprova" [ "$?" = 1 ]
  despachou_de_verdade "$BASE/t/forjou.saida"; confere "controle: comando que escreve a frase ele mesmo reprova" [ "$?" = 1 ]
  despachou_de_verdade "$BASE/t/real.saida"; confere "controle: transcrito com a linha real passa" [ "$?" = 0 ]
  despachou_de_verdade "$BASE/t/capturou.saida"; confere "controle: transcrito com o exit capturado passa" [ "$?" = 0 ]
  printf '%s\n' "controles: $falhas falha(s)"
}

prova_despacho() {
  echo "── despacho ──"
  local d="$BASE/despacho"; copia "$d"; mkdir -p "$BASE/tmp"
  cp "$d/sdd/playbook.md" "$BASE/pb.antes"; local h; h="$(git -C "$d" rev-parse HEAD)"
  agente despacho "$d" workspace-write "$P_DESPACHO"
  local s="$BASE/despacho.saida"
  confere "o transcrito mostra o despachar saindo 40 num comando real" despachou_de_verdade "$s"
  confere "o transcrito traz a frase da publicação" tem "$s" "A publicação já terminou e não depende deste passo"
  confere "o brief está no destino" existe "$d/sdd/reports/briefs/BRIEF_curador_DEMO.md"
  confere "o brief leva só os 5 campos e o ponteiro" tem "$d/sdd/reports/briefs/BRIEF_curador_DEMO.md" "references/curator.md"
  confere "o playbook não mudou" igual "$d/sdd/playbook.md" "$BASE/pb.antes"
  confere "nenhum commit" [ "$(git -C "$d" rev-parse HEAD)" = "$h" ]
  # a linha do bloco de exemplo do brief fala de LM-020; um bloco inventado sobre a DEMO fala das lições dela
  confere "o agente não inventou o bloco" nao_tem "$s" "| contador | LM-001 |"
}

prova_curador() {
  echo "── curador ──"
  local d="$BASE/curador"; copia "$d"; mkdir -p "$BASE/tmp"; prepara_curadoria "$d"
  cp "$d/sdd/playbook.md" "$BASE/pb.antes"
  local stg; stg="$(cat "$BASE/stg")"
  agente curador "$d" workspace-write "$(cat "$d/sdd/reports/briefs/BRIEF_curador_DEMO.md")"
  extrai_bloco "$BASE/curador.saida" "$BASE/t/curadoria.txt"
  cp "$BASE/t/curadoria.txt" "$E/$PREFIXO-curador.bloco.txt"
  confere "há um bloco na resposta" [ -s "$BASE/t/curadoria.txt" ]
  fecha_curadoria "$d" "$BASE/t/curadoria.txt"
  { printf '$ governanca-fronteira.sh --comparar (na cópia)\n'; cat "$BASE/t/comparar.txt"; printf '[exit=%s]\n' "$(cat "$BASE/rc-comparar")"
    printf '$ playbook-curator.sh --conferir-bloco (na cópia)\n'; cat "$BASE/t/conferido.txt" "$BASE/t/conferido.err"; printf '[exit=%s]\n' "$(cat "$BASE/rc-conferir")"; } >> "$E/$PREFIXO-curador.log"
  # O item 4 do 17b: reprovado só pelo bloco, sem escrita, 1 redespacho com o campo conferencia:, mesmo selo e mesmo snapshot.
  if [ "$(cat "$BASE/rc-conferir")" = 2 ] && [ "$(cat "$BASE/rc-comparar")" = 0 ]; then
    echo "  ↻ reprovado na 1ª vez: 1 redespacho, como manda o item 4"
    printf 'conferencia: %s\n' "$(grep '^🔴 bloco:' "$BASE/t/conferido.err" | tr '\n' ' ')" >> "$d/sdd/reports/briefs/BRIEF_curador_DEMO.md"
    agente curador2 "$d" workspace-write "$(cat "$d/sdd/reports/briefs/BRIEF_curador_DEMO.md")"
    extrai_bloco "$BASE/curador2.saida" "$BASE/t/curadoria.txt"
    cp "$BASE/t/curadoria.txt" "$E/$PREFIXO-curador2.bloco.txt"
    fecha_curadoria "$d" "$BASE/t/curadoria.txt"
    { printf '$ governanca-fronteira.sh --comparar (na cópia)\n'; cat "$BASE/t/comparar.txt"; printf '[exit=%s]\n' "$(cat "$BASE/rc-comparar")"
      printf '$ playbook-curator.sh --conferir-bloco (na cópia)\n'; cat "$BASE/t/conferido.txt" "$BASE/t/conferido.err"; printf '[exit=%s]\n' "$(cat "$BASE/rc-conferir")"; } >> "$E/$PREFIXO-curador2.log"
  fi
  confere "o curador não escreveu no projeto" [ "$(cat "$BASE/rc-comparar")" = 0 ]
  confere "o bloco passa no conferidor" [ "$(cat "$BASE/rc-conferir")" = 0 ]
  confere "o playbook não mudou" igual "$d/sdd/playbook.md" "$BASE/pb.antes"
  confere "sem contaminação declarada" tem "$BASE/t/conferido.txt" "contaminacao=nao"
  confere "a contagem da tabela entra sem pergunta" tem "$BASE/t/conferido.txt" "AUTO LM-001 ajudou+1"
  confere "a lição nova vira pergunta" grep -q '^PERGUNTA [0-9]* add ADD Backend' "$BASE/t/conferido.txt"
  [ "$(cat "$BASE/rc-conferir")" = 0 ] || { sed 's/^/     │ /' "$BASE/t/conferido.err" | head -20; }
}

prova_retomada() {
  echo "── retomada ──"
  # usa o bloco da execução do curador desta mesma corrida; sem ele, não há o que retomar
  [ -s "$BASE/t/curadoria.txt" ] || { echo "  ❌ sem bloco do curador: rode curador antes"; falhas=$((falhas + 1)); return; }
  [ "$(cat "$BASE/rc-conferir")" = 0 ] || { echo "  ❌ o bloco do curador não passou: não há o que retomar"; falhas=$((falhas + 1)); return; }
  local d="$BASE/curador" h stg; h="$(git -C "$d" rev-parse HEAD)"; stg="$(cat "$BASE/stg")"
  cp "$d/sdd/playbook.md" "$BASE/pb.antes"; cp "$BASE/t/selo.txt" "$BASE/selo.antes"; cp "$BASE/t/antes" "$BASE/snap.antes"
  local p="${P_RETOMADA//BLOCO/$BASE/t/curadoria.txt}"; p="${p//TMPDIR_T/$BASE/t}"; p="${p//em T,/em $BASE/t (selo.txt e antes),}"
  agente retomada "$d" workspace-write "$p"
  confere "a contagem pura entrou no playbook" grep -q '^- \[LM-001\] ajudou=1 ' "$d/sdd/playbook.md"
  confere "a lição recusada não entrou" nao_tem "$d/sdd/playbook.md" "nota_cancelada"
  confere "a contagem com pendência recusada não entrou" grep -q '^- \[LM-002\] ajudou=0 mordeu=0 ' "$d/sdd/playbook.md"
  confere "o selo não foi refeito" igual "$BASE/t/selo.txt" "$BASE/selo.antes"
  confere "o snapshot de antes não foi refeito" igual "$BASE/t/antes" "$BASE/snap.antes"
  if [ "$(git -C "$d" rev-list --count "$h"..HEAD)" = 0 ] && tem "$BASE/retomada.saida" "index.lock': Operation not permitted"; then
    # o sandbox workspace-write do Codex protege .git; o AT-038 não pede commit, e isto fica dito, não contado como passou
    echo "  ⚠️ commit NÃO PROVADO neste agente: o sandbox do Codex barrou a escrita em .git"
    confere "o registro foi gravado" existe "$d/sdd/releases/DEMO/CURATOR-colhidos.txt"
  else
    confere "houve 1 commit novo" [ "$(git -C "$d" rev-list --count "$h"..HEAD)" = 1 ]
    git -C "$d" show --stat --format='commit: %s' HEAD > "$BASE/commit.txt" 2>&1
    confere "o commit leva o playbook" tem "$BASE/commit.txt" "sdd/playbook.md"
    confere "o commit leva o registro" tem "$BASE/commit.txt" "CURATOR-colhidos.txt"
  fi
  ( cd "$d" && SDD_TRACE=off bash sdd/bin/playbook-curator.sh --validar-inv sdd/playbook.md sdd/invariants.md >/dev/null 2>&1 ); confere "a trava aceita o par final (exit real)" [ "$?" = 0 ]
  confere "nenhum push: não há remoto" [ -z "$(git -C "$d" remote)" ]
  { printf '$ git log --oneline (na cópia)\n'; git -C "$d" log --oneline | head -3; printf '[exit=0]\n'; printf '$ grep LM-00 sdd/playbook.md (na cópia)\n'; grep -E '^- \[LM-00[12]\]' "$d/sdd/playbook.md" | cut -c1-90; printf '[exit=0]\n'; } >> "$E/$PREFIXO-retomada.log"
}

for etapa in ${@:-controles despacho curador retomada}; do
  case "$etapa" in
    controles) prova_controles ;;
    despacho)  prova_despacho ;;
    curador)   prova_curador ;;
    retomada)  prova_retomada ;;
    *) echo "etapa desconhecida: $etapa" >&2; exit 64 ;;
  esac
done
if [ -n "${OR_MODELO:-}" ] && grep -qF -- "$OPENROUTER_API_KEY" "$E/$PREFIXO"-* 2>/dev/null; then
  echo "🛑 a chave apareceu num log da prova"; falhas=$((falhas + 1))
fi
printf 'RESULTADO: %s falha(s)\n' "$falhas"
[ "$falhas" -eq 0 ]
