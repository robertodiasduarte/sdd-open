# duplicadas.sh — skills do SDD que o mesmo agente enxerga duas vezes (F25). Lido com `.` pelo checar.sh; não roda sozinho.
#
# Medido em 2026-11-17, na F25 do SDD Open (Claude Code 2.1, Codex 0.163, CLI skills 1.9.0):
#   - o Claude Code lê ${CLAUDE_CONFIG_DIR:-~/.claude}/skills e <projeto>/.claude/skills; com o mesmo nome, roda a GLOBAL;
#   - o Codex lê ${CODEX_HOME:-~/.codex}/skills, ~/.agents/skills, <projeto>/.agents/skills e <projeto>/.codex/skills; com
#     o mesmo nome, lista todas e o modelo escolhe uma;
#   - a instalação global pelo npx grava em ~/.agents/skills (Codex) ou em ~/.claude/skills (só Claude Code), com atalho de uma
#     para a outra quando é para os dois; o registro fica em ${XDG_STATE_HOME}/skills/.skill-lock.json ou
#     ~/.agents/.skill-lock.json;
#   - o npx skills remove <s> -g -a <agente> apaga também a pasta de mesmo nome que ele não instalou (em ~/.claude/skills e
#     em ~/.agents/skills): por isso a outra cópia é PROTEGIDA — vai para a lixeira e volta — durante o remove.
#
# Só o dup_limpar escreve (a exceção única da regra "Somente leitura" da skill). O resto só lê.
# Precisa de: RAIZ (a pasta do projeto), HOME e git. SDD_CHECAR_NPX existe para os testes (o padrão é o npx do PATH).
# Bash 3.2: nada de declare -A, mapfile nem ${x,,}; as tabelas são arquivos TSV numa pasta temporária.

DUP_TAB="$(printf '\t')"
DUP_TMP=""
dup_tmp() {
  [ -n "${DUP_TMP}" ] && return 0
  DUP_TMP="$(mktemp -d 2>/dev/null)" || return 1
  trap 'rm -rf "${DUP_TMP}"' EXIT
}
dup_registro_arquivo() {
  if [ -n "${XDG_STATE_HOME:-}" ]; then printf '%s/skills/.skill-lock.json' "${XDG_STATE_HOME}"
  else printf '%s/.agents/.skill-lock.json' "${HOME}"; fi
}
dup_claude_global() { printf '%s/skills' "${CLAUDE_CONFIG_DIR:-${HOME}/.claude}"; }
dup_agentes_global() { printf '%s/.agents/skills' "${HOME}"; }

# agente · escopo · rótulo · pasta. A ordem é a de quem FICA no empate: o projeto, depois ~/.agents, ~/.claude, ~/.codex.
dup_pastas() {
  printf 'claude\tprojeto\tprojeto-claude\t%s\n' "${RAIZ}/.claude/skills"
  printf 'codex\tprojeto\tprojeto-agents\t%s\n' "${RAIZ}/.agents/skills"
  printf 'codex\tprojeto\tprojeto-codex\t%s\n' "${RAIZ}/.codex/skills"
  printf 'codex\tglobal\thome-agents\t%s\n' "$(dup_agentes_global)"
  printf 'claude\tglobal\thome-claude\t%s\n' "$(dup_claude_global)"
  printf 'codex\tglobal\thome-codex\t%s\n' "${CODEX_HOME:-${HOME}/.codex}/skills"
}

# nome<TAB>source de cada skill no registro do npx (JSON.stringify com 2 espaços, como o CLI grava).
dup_registro() {
  local f; f="$(dup_registro_arquivo)"
  [ -f "${f}" ] || return 0
  LC_ALL=C awk '/^  "skills": \{/ { s = 1; next }
       s && /^  \}/ { s = 0 }
       s && /^    "[^"]+": \{/ { n = $0; sub(/^    "/, "", n); sub(/".*/, "", n) }
       s && n != "" && /^      "source": "/ { v = $0; sub(/^      "source": "/, "", v); sub(/".*/, "", v); print n "\t" v; n = "" }' "${f}"
}

# versão<TAB>origem de um SKILL.md. Versão = metadata.version do frontmatter ("" se ilegível). Origem pela linha de
# identificação: o trecho <repositório>/releases/latest do Open ou do starter — nunca a URL inteira, que o gerador do
# starter reescreve em todo arquivo de texto (o checar.sh do starter confundiria as duas).
dup_meta() {
  LC_ALL=C awk '
    NR == 1 && /^---[ \t\r]*$/ { fm = 1; next }
    fm == 1 && /^---[ \t\r]*$/ { fm = 2 }
    fm == 1 && v == "" && /^[ \t]+version:/ { s = $0; sub(/^[ \t]+version:[ \t]*/, "", s); gsub(/["\047 \r]/, "", s)
                                              v = (s ~ /^[0-9]+\.[0-9]+\.[0-9]+$/) ? s : "-" }
    o == "" && /sdd-open\/releases\/latest/ { o = "open" }
    o == "" && /sdd-starter\/releases\/latest/ { o = "starter" }
    END { if (v == "-") v = ""; print v "\t" (o == "" ? "outra" : o) }' "$1" 2>/dev/null
}

# Varre as pastas e grava ${DUP_TMP}/copias.tsv, uma linha por (agente, caminho):
#   1 agente · 2 escopo · 3 rótulo · 4 caminho · 5 real · 6 nome · 7 versão · 8 origem · 9 chegada (npx|git|atalho|manual)
# "real" é a pasta de verdade: dois caminhos com o mesmo real são uma cópia só (o atalho do npx não é duplicata).
dup_varrer() {
  dup_tmp || return 1
  local ag es ro pa rp e n r lk vo
  : > "${DUP_TMP}/brutas.tsv"
  while IFS="${DUP_TAB}" read -r ag es ro pa; do
    [ -d "${pa}" ] || continue
    rp="$(cd -P "${pa}" 2>/dev/null && pwd -P)" || continue
    for e in "${pa}"/*; do
      [ -f "${e}/SKILL.md" ] || continue
      n="${e##*/}"
      lk=0
      if [ -L "${e}" ]; then lk=1; r="$(cd -P "${e}" 2>/dev/null && pwd -P)" || continue; else r="${rp}/${n}"; fi
      vo="$(dup_meta "${e}/SKILL.md")"
      printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "${ag}" "${es}" "${ro}" "${e}" "${r}" "${n}" "${vo}" "${lk}" >> "${DUP_TMP}/brutas.tsv"
    done
  done <<EOF
$(dup_pastas)
EOF
  git -C "${RAIZ}" ls-files -- .claude/skills .agents/skills .codex/skills 2>/dev/null \
    | sed -n 's#/SKILL\.md$##p' | awk -v r="${RAIZ}" '{ print r "/" $0 }' > "${DUP_TMP}/git.txt"
  dup_registro > "${DUP_TMP}/registro.tsv"
  LC_ALL=C awk -F '\t' -v OFS='\t' -v cg="$(dup_claude_global)" -v ga="$(dup_agentes_global)" '
    FILENAME ~ /git\.txt$/ { git[$0] = 1; next }
    FILENAME ~ /registro\.tsv$/ { reg[$1] = $2; next }
    # 1ª passada nas brutas: o real de ~/.agents/skills/<nome>, quando existe
    pass == 0 { if ($3 == "home-agents") real_ga[$6] = $5; linhas[++m] = $0; next }
    END {
      for (i = 1; i <= m; i++) {
        split(linhas[i], f, "\t")
        ag = f[1]; es = f[2]; ro = f[3]; c = f[4]; r = f[5]; n = f[6]; v = f[7]; o = f[8]; lk = f[9]
        ch = lk ? "atalho" : "manual"
        if (es == "projeto") { if (c in git) ch = "git" }
        else if (n in reg) {
          s = reg[n]; ok = 1
          # o registro diz de que repositório veio (dono/repositório no GitHub); uma pasta local não diz nada
          if (s ~ /(^|\/)sdd-starter(\.git)?$/ && o != "starter") ok = 0
          if (s ~ /(^|\/)sdd-open(\.git)?$/ && o != "open") ok = 0
          # a pasta que o npx gerencia: a de ~/.agents/skills, ou a de ~/.claude/skills quando não há outra em ~/.agents
          if (ok && ((n in real_ga) ? r == real_ga[n] : c == cg "/" n)) ch = "npx"
        }
        print ag, es, ro, c, r, n, v, o, ch
      }
    }' "${DUP_TMP}/git.txt" "${DUP_TMP}/registro.tsv" "${DUP_TMP}/brutas.tsv" > "${DUP_TMP}/copias.tsv"
}

# Grupos duplicados: agente<TAB>nome, quando o agente lê 2+ cópias (reais distintos) de um nome do SDD.
# Nome do SDD: começa com sdd- ou é ux-review-builder, ou alguma cópia tem a linha de identificação do SDD.
dup_grupos() {
  LC_ALL=C awk -F '\t' '
    { k = $1 "\t" $6; if (!((k SUBSEP $5) in visto)) { visto[k SUBSEP $5] = 1; reais[k]++ }
      if ($6 ~ /^sdd-/ || $6 == "ux-review-builder" || $8 != "outra") sdd[$6] = 1 }
    END { for (k in reais) { split(k, p, "\t"); if (reais[k] >= 2 && (p[2] in sdd)) print k } }' "${DUP_TMP}/copias.tsv" \
    | LC_ALL=C sort
}

dup_rotulo_escopo() { case "$1" in projeto) echo "do projeto" ;; *) echo "global" ;; esac; }
dup_rotulo_origem() { case "$1" in open) echo "do SDD Open" ;; starter) echo "do starter" ;; *) echo "de outra origem" ;; esac; }
dup_rotulo_chegada() {
  case "$1" in
    npx) echo "instalada pelo npx" ;; git) echo "salva no git do projeto" ;; atalho) echo "atalho para outra pasta" ;;
    *) echo "copiada à mão" ;;
  esac
}
dup_agente() { case "$1" in claude) echo "Claude Code" ;; *) echo "Codex" ;; esac; }

# As cópias de um grupo, uma por real (o caminho de maior prioridade), na ordem de dup_pastas.
dup_copias_do_grupo() {   # $1 agente $2 nome
  LC_ALL=C awk -F '\t' -v a="$1" -v n="$2" '$1 == a && $6 == n && !($5 in v) { v[$5] = 1; print }' "${DUP_TMP}/copias.tsv"
}
# Para mostrar: as globais primeiro (a global é a que o Claude Code roda), depois as do projeto.
dup_copias_para_mostrar() {
  dup_copias_do_grupo "$1" "$2" | LC_ALL=C awk -F '\t' '$2 == "global"'
  dup_copias_do_grupo "$1" "$2" | LC_ALL=C awk -F '\t' '$2 == "projeto"'
}

# Uma linha legível por cópia: "    global: <caminho> — versão X, do SDD Open, copiada à mão"
dup_linha_copia() {   # recebe a linha do copias.tsv
  local es c v o ch
  es="$(printf '%s' "$1" | cut -f2)"; c="$(printf '%s' "$1" | cut -f4)"; v="$(printf '%s' "$1" | cut -f7)"
  o="$(printf '%s' "$1" | cut -f8)"; ch="$(printf '%s' "$1" | cut -f9)"
  if [ -n "${v}" ]; then v="versão ${v}"; else v="versão ilegível"; fi
  printf '%s: %s — %s, %s, %s' "$(dup_rotulo_escopo "${es}")" "${c}" "${v}" "$(dup_rotulo_origem "${o}")" "$(dup_rotulo_chegada "${ch}")"
}

# A 1ª frase do item: o efeito no agente (UX U1).
dup_efeito() {   # $1 agente $2 nome $3 nº de cópias
  local g l gv pv
  if [ "$1" = claude ]; then
    g="$(dup_copias_do_grupo claude "$2" | LC_ALL=C awk -F '\t' '$2 == "global"' | head -1)"
    l="$(dup_copias_do_grupo claude "$2" | LC_ALL=C awk -F '\t' '$2 == "projeto"' | head -1)"
    gv="$(printf '%s' "${g}" | cut -f7)"; pv="$(printf '%s' "${l}" | cut -f7)"
    if [ -n "${gv}" ] && [ -n "${pv}" ] && [ "$(dup_compara "${gv}" "${pv}")" = "<" ]; then
      printf 'A skill %s está em %s lugares que o Claude Code lê, e ele roda a global (a %s), não a %s do projeto:' "$2" "$3" "${gv}" "${pv}"
    else
      printf 'A skill %s está em %s lugares que o Claude Code lê, e ele roda a global%s; a do projeto fica escondida:' "$2" "$3" "${gv:+ (a ${gv})}"
    fi
  else
    printf 'A skill %s está em %s lugares que o Codex lê, e ele escolhe uma sem dizer qual:' "$2" "$3"
  fi
}

# Compara duas versões x.y.z: imprime <, = ou >.
dup_compara() {
  LC_ALL=C awk -v a="$1" -v b="$2" 'BEGIN { split(a, x, "."); split(b, y, ".")
    for (i = 1; i <= 3; i++) { if (x[i] + 0 < y[i] + 0) { print "<"; exit } if (x[i] + 0 > y[i] + 0) { print ">"; exit } }
    print "=" }'
}

# Diagnóstico normal: chama $1 (a função do checar.sh que acrescenta um ⚠️) com a mensagem e o comando.
# Até 3 duplicatas, uma por item; acima disso, um item só com até 10 nomes e "e mais N" (UX U9).
dup_diagnostico() {   # $1 = função add_* · $2 = o comando que mostra o plano
  dup_varrer || return 0
  local grupos total ag n msg linhas c nomes k
  grupos="$(dup_grupos)"
  [ -n "${grupos}" ] || return 0
  total="$(printf '%s\n' "${grupos}" | wc -l | tr -d ' ')"
  if [ "${total}" -le 3 ]; then
    while IFS="${DUP_TAB}" read -r ag n; do
      linhas=""; k=0
      while IFS= read -r c; do
        k=$((k + 1)); linhas="${linhas}"$'\n'"    $(dup_linha_copia "${c}")"
      done <<EOF
$(dup_copias_para_mostrar "${ag}" "${n}")
EOF
      msg="$(dup_efeito "${ag}" "${n}" "${k}")${linhas}"
      "$1" "${msg}" "$2   (mostra o que eu tiraria e pergunta antes; nada muda sem o seu sim)"
    done <<EOF
${grupos}
EOF
  else
    nomes="$(printf '%s\n' "${grupos}" | cut -f2 | LC_ALL=C sort -u)"
    k="$(printf '%s\n' "${nomes}" | wc -l | tr -d ' ')"
    msg="$(printf '%s\n' "${nomes}" | head -10 | paste -sd, - | sed 's/,/, /g')"
    [ "${k}" -gt 10 ] && msg="${msg} e mais $((k - 10))"
    "$1" "${k} skills do SDD estão em mais de um lugar que o mesmo agente lê (${msg}): o agente pode estar rodando uma versão diferente da que o projeto traz." \
         "$2   (mostra cada uma, onde está e o que eu tiraria; nada muda sem o seu sim)"
  fi
}

# ── plano (--duplicadas) ──────────────────────────────────────────────────────
# Hash do conteúdo de uma pasta: caminho e hash de cada arquivo (.DS_Store fora), destino de cada atalho de dentro.
# Os arquivos vão ao git como ARGUMENTOS relativos: pela entrada (--stdin-paths), dentro de um repositório o git lê o
# caminho a partir da raiz dele, e no Git Bash um caminho absoluto (/c/…) não chega convertido ao git.exe.
dup_hash() {
  ( cd "$1" 2>/dev/null || exit 1
    find . -type f ! -name .DS_Store 2>/dev/null | LC_ALL=C sort > "${DUP_TMP}/h.f"
    find . -type l 2>/dev/null | LC_ALL=C sort > "${DUP_TMP}/h.l"
    set --
    while IFS= read -r f; do set -- "$@" "${f}"; done < "${DUP_TMP}/h.f"
    if [ "$#" -gt 0 ]; then git hash-object --no-filters -- "$@" > "${DUP_TMP}/h.h" || exit 1; else : > "${DUP_TMP}/h.h"; fi
    paste "${DUP_TMP}/h.f" "${DUP_TMP}/h.h"
    while IFS= read -r l; do printf '%s\t-> %s\n' "${l}" "$(readlink "${l}")"; done < "${DUP_TMP}/h.l"
  ) | git hash-object --no-filters --stdin
}
dup_real() { if [ -L "$1" ]; then (cd -P "$1" 2>/dev/null && pwd -P); else printf '%s' "$1"; fi; }

# Monta ${DUP_TMP}/plano.tsv (o texto canônico que a assinatura cobre). Registros, nesta ordem:
#   C agente nome escopo rótulo caminho real versão origem chegada hash      (cada cópia de cada grupo)
#   D agente nome tipo real motivo                                             (tirar · projeto · nao)
#   T real nome rótulo método versão hash agentes-npx                          (o que o --limpar tira, um por real)
dup_planejar() {
  dup_varrer || return 1
  local ag n c r h
  dup_grupos > "${DUP_TMP}/grupos.tsv"
  : > "${DUP_TMP}/hashes.tsv"
  while IFS="${DUP_TAB}" read -r ag n; do
    dup_copias_do_grupo "${ag}" "${n}"
  done < "${DUP_TMP}/grupos.tsv" > "${DUP_TMP}/doplano.tsv"
  cut -f5 "${DUP_TMP}/doplano.tsv" | LC_ALL=C sort -u | while IFS= read -r r; do
    [ -n "${r}" ] && printf '%s\t%s\n' "${r}" "$(dup_hash "${r}")"
  done > "${DUP_TMP}/hashes.tsv"
  LC_ALL=C awk -F '\t' -v OFS='\t' -v cg="$(dup_claude_global)" -v ga="$(dup_agentes_global)" '
    function prio(ro) { return ro == "projeto-claude" ? 1 : ro == "projeto-agents" ? 2 : ro == "projeto-codex" ? 3 : ro == "home-agents" ? 4 : ro == "home-claude" ? 5 : 6 }
    function cmp(a, b,   x, y, i) { split(a, x, "."); split(b, y, ".")
      for (i = 1; i <= 3; i++) { if (x[i] + 0 < y[i] + 0) return -1; if (x[i] + 0 > y[i] + 0) return 1 } return 0 }
    FILENAME ~ /hashes\.tsv$/ { hash[$1] = $2; next }
    FILENAME ~ /copias\.tsv$/ { usa[$1 "\t" $6 "\t" $5] = 1; caminhos[$5]++; if ($4 != $5) link_de[$5] = link_de[$5] "\t" $4
                                todos[$1 "\t" $6] = todos[$1 "\t" $6] "\t" $5; ch_de[$5] = (ch_de[$5] == "" ? $9 : ch_de[$5]); next }
    { g = $1 "\t" $6; if (!(g in ng)) { ordem[++G] = g }
      i = ++ng[g]; ag[g] = $1; nm[g] = $6; es[g, i] = $2; ro[g, i] = $3; cm[g, i] = $4; re[g, i] = $5; ve[g, i] = $7; or[g, i] = $8; chg[g, i] = $9 }
    END {
      for (k = 1; k <= G; k++) {
        g = ordem[k]; m = ng[g]; nao = ""
        for (i = 1; i <= m; i++) print "C", ag[g], nm[g], es[g, i], ro[g, i], cm[g, i], re[g, i], ve[g, i], or[g, i], chg[g, i], hash[re[g, i]]
        for (i = 1; i <= m && nao == ""; i++) {
          if (or[g, i] == "outra") nao = "a cópia " cm[g, i] " não é do SDD (não tem a linha de identificação); tire à mão a que não quiser"
          else if (ve[g, i] == "") nao = "não consegui ler a versão de " cm[g, i] "; compare as cópias e tire à mão a que não quiser"
          else if (chg[g, i] == "atalho") nao = cm[g, i] " é um atalho para outra pasta; desfazer atalho à mão é mais seguro"
        }
        if (nao == "") {
          mx = ve[g, 1]; for (i = 2; i <= m; i++) if (cmp(ve[g, i], mx) > 0) mx = ve[g, i]
          fica = 0
          for (i = 1; i <= m && nao == ""; i++) {
            if (cmp(ve[g, i], mx) != 0) continue
            for (j = i + 1; j <= m; j++)
              if (cmp(ve[g, j], mx) == 0 && or[g, i] == or[g, j] && hash[re[g, i]] != hash[re[g, j]])
                nao = "as cópias " cm[g, i] " e " cm[g, j] " dizem " mx " e têm textos diferentes: uma delas foi editada; compare e diga qual quer manter"
            if (!fica || prio(ro[g, i]) < prio(ro[g, fica])) fica = i
          }
        }
        if (nao != "") { print "D", ag[g], nm[g], "nao", "-", nao; continue }
        for (i = 1; i <= m; i++) {
          if (i == fica) continue
          motivo = (cmp(ve[g, i], mx) < 0) ? "mais velha" : "sobra"
          if (chg[g, i] == "git") { print "D", ag[g], nm[g], "projeto", re[g, i], or[g, i]; continue }
          if (chg[g, i] != "npx" && caminhos[re[g, i]] > 1) {
            print "D", ag[g], nm[g], "nao", "-", "outra pasta aponta para " cm[g, i] "; tire à mão"; continue }
          print "D", ag[g], nm[g], "tirar", re[g, i], motivo
          tira[re[g, i]] = 1; tnome[re[g, i]] = nm[g]; tro[re[g, i]] = ro[g, i]; tch[re[g, i]] = chg[g, i]; tve[re[g, i]] = ve[g, i]
        }
      }
      # nenhum agente pode ficar sem a skill neste projeto: um nome que sumiria de um agente sai do plano inteiro
      for (u in todos) {
        split(u, p, "\t"); n = p[2]; resta = 0; nr = split(todos[u], rs, "\t")
        for (q = 2; q <= nr; q++) if (!(rs[q] in tira)) resta = 1
        if (!resta && !(corta[n] == "claude")) corta[n] = p[1]   # o "for in" não tem ordem: o Claude vence, sempre igual
      }
      # o motivo vai em cada grupo daquele nome: o agente que ficaria sem a skill pode nem ter grupo (uma cópia só)
      for (k = 1; k <= G; k++) {
        g = ordem[k]; n = nm[g]
        if (n in corta) print "D", ag[g], n, "nao", "-", "tirar deixaria o " (corta[n] == "claude" ? "Claude Code" : "Codex") " sem a " n " neste projeto"
      }
      for (r in tira) {
        n = tnome[r]
        if (n in corta) continue
        a = ""
        if (tch[r] == "npx") {
          if (r == cg "/" n || index(link_de[r], "\t" cg "/" n)) a = "claude-code"
          if (r == ga "/" n || index(link_de[r], "\t" ga "/" n)) a = a (a == "" ? "" : " ") "codex"
        }
        print "T", r, n, tro[r], (tch[r] == "npx" ? "npx" : "mover"), tve[r], hash[r], a
      }
    }' "${DUP_TMP}/hashes.tsv" "${DUP_TMP}/copias.tsv" "${DUP_TMP}/doplano.tsv" > "${DUP_TMP}/plano.0"
  # ordem estável: C e D na ordem dos grupos; T ordenado pelo caminho (a assinatura não pode depender da ordem do awk)
  { grep '^[CD]	' "${DUP_TMP}/plano.0"; grep '^T	' "${DUP_TMP}/plano.0" | LC_ALL=C sort; } > "${DUP_TMP}/plano.tsv"
  # um nome cortado pela regra acima não pode ficar com D "tirar" no texto
  LC_ALL=C awk -F '\t' 'FILENAME ~ /plano\.0$/ { if ($1 == "D" && $4 == "nao" && $6 ~ /^tirar deixaria/) corta[$3] = 1; next }
       !($1 == "D" && $4 == "tirar" && ($3 in corta))' "${DUP_TMP}/plano.0" "${DUP_TMP}/plano.tsv" > "${DUP_TMP}/plano.1"
  mv "${DUP_TMP}/plano.1" "${DUP_TMP}/plano.tsv"
}
dup_assinatura() { git hash-object --no-filters --stdin < "${DUP_TMP}/plano.tsv" | cut -c1-12; }

# Remédio para a cópia do projeto salva no git que é a mais velha: atualizar o projeto, pela origem dela.
dup_remedio_projeto() {
  case "$1" in
    open) echo "atualize o SDD Open do projeto pelo upgrade (passo a passo: https://github.com/robertodiasduarte/sdd-open/blob/main/docs/pt-BR/upgrade.md)" ;;
    *) echo "atualize as skills do projeto: npx skills update (nesta pasta, sem -g)" ;;
  esac
}

# O plano, para o aluno. $1 = o comando do checar.sh (para a linha de aplicar). Só lê.
dup_plano_mostrar() {
  dup_planejar || { echo "🛑 Não consegui ler as pastas de skills. Nada mudou."; return 1; }
  if ! grep -q '^C	' "${DUP_TMP}/plano.tsv"; then
    echo "✅ Nenhuma skill do SDD está duplicada para o mesmo agente. Nada a limpar."
    return 0
  fi
  local i=0 ag n ag2 n2 tipo r mot linha c cm es ve k g nt mt h ags a
  echo "Plano de limpeza das skills duplicadas — nada mudou ainda."
  echo "(global = vale para todos os projetos deste computador · do projeto = só nesta pasta)"
  while IFS="${DUP_TAB}" read -r ag n; do
    i=$((i + 1)); k="$(dup_copias_do_grupo "${ag}" "${n}" | wc -l | tr -d ' ')"
    echo
    if [ "${ag}" = claude ]; then echo "${i}. ${n} — o Claude Code lê ${k} cópias e roda a global:"
    else echo "${i}. ${n} — o Codex lê ${k} cópias e escolhe uma sem dizer qual:"; fi
    while IFS= read -r c; do echo "   $(dup_linha_copia "${c}")"; done <<EOF
$(dup_copias_para_mostrar "${ag}" "${n}")
EOF
    while IFS="${DUP_TAB}" read -r linha ag2 n2 tipo r mot; do
      [ "${ag2}" = "${ag}" ] && [ "${n2}" = "${n}" ] || continue
      case "${tipo}" in
        nao) echo "   Não escolho: ${mot}." ;;
        projeto) echo "   A mais velha é a do projeto, salva no git: não a tiro (tirar apareceria como mudança a salvar e voltaria na próxima atualização); $(dup_remedio_projeto "${mot}")." ;;
        tirar)
          c="$(LC_ALL=C awk -F '\t' -v r="${r}" -v a="${ag}" '$5 == r && $1 == a' "${DUP_TMP}/copias.tsv" | head -1)"
          es="$(printf '%s' "${c}" | cut -f2)"; ve="$(printf '%s' "${c}" | cut -f7)"; cm="$(printf '%s' "${c}" | cut -f4)"
          [ "${cm}" = "${r}" ] || cm="${cm} (atalho para ${r}: os dois saem juntos)"
          if [ "${mot}" = "mais velha" ]; then echo "   Recomendo: tirar a $(dup_rotulo_escopo "${es}") ${cm} (${ve}, a mais velha)."
          else echo "   Recomendo: tirar a $(dup_rotulo_escopo "${es}") ${cm} (${ve}: a mesma versão da que fica; sobra)."; fi
          [ "${es}" = global ] && echo "   Ela vale para todos os projetos deste computador: os que não têm cópia própria ficam sem a ${n}."
          ;;
      esac
    done < <(grep '^D	' "${DUP_TMP}/plano.tsv")
  done < "${DUP_TMP}/grupos.tsv"
  nt="$(grep -c '^T	' "${DUP_TMP}/plano.tsv")"
  echo
  if [ "${nt}" -eq 0 ]; then
    echo "Nada a tirar automaticamente: veja o que fazer em cada item acima."
    return 0
  fi
  echo "Se você disser sim, tiro ${nt} cópia(s), uma por vez, e guardo cada uma antes em ${HOME}/.sdd-lixeira (dá para desfazer)."
  while IFS="${DUP_TAB}" read -r linha r n g mt ve h ags; do
    [ "${mt}" = npx ] || continue
    echo "A cópia ${r} veio pelo npx: sai pelo npx skills remove ${n} -g $(for a in ${ags}; do printf -- '-a %s ' "${a}"; done)-y."
    for c in "$(dup_claude_global)/${n}" "$(dup_agentes_global)/${n}"; do
      { [ -e "${c}" ] || [ -L "${c}" ]; } || continue
      [ "$(dup_real "${c}")" = "${r}" ] && continue
      echo "  Esse comando também apagaria ${c}, que não está no plano: ela vai para a lixeira por um instante e volta ao lugar logo depois."
    done
  done < <(grep '^T	' "${DUP_TMP}/plano.tsv")
  echo "Assinatura deste plano: $(dup_assinatura) (muda se qualquer cópia mudar)."
  echo "Para aplicar só este plano: $1 --limpar $(dup_assinatura)"
}

# ── limpeza (--limpar <assinatura>): a ÚNICA escrita da skill, só depois do sim do aluno ao plano mostrado ───────────
# A lixeira é ~/.sdd-lixeira/<AAAAMMDD-HHMMSS>/<rótulo>/<skill>; o desfazer.sh é regravado a cada passo (antes de tirar
# cada coisa), para valer mesmo se a limpeza parar no meio.
DUP_L=""
dup_desfazer_item() {   # acrescenta uma linha (volta|liga) ao desfazer.sh: $1 função, $2 e $3 os caminhos
  printf '%s %q %q\n' "$1" "$2" "$3" >> "${DUP_L}/.itens"
  dup_desfazer_grava
}
dup_desfazer_grava() {
  local lock depois
  lock="$(dup_registro_arquivo)"
  depois="$(cat "${DUP_L}/npx/depois.cksum" 2>/dev/null)"
  {
    printf '#!/usr/bin/env bash\n'
    printf '# Desfaz a limpeza de skills duplicadas de %s (sdd-checar-ambiente, checar.sh --limpar).\n' "${DUP_L##*/}"
    printf '# Devolve cada pasta ao lugar de onde saiu e o registro do npx como estava. Não sobrescreve o que existir de novo.\n'
    printf 'set -u\nfalhou=0\n'
    cat <<'CORPO'
volta() {   # volta <guardada> <lugar>
  [ -e "$1" ] || [ -L "$1" ] || return 0
  if [ -e "$2" ] || [ -L "$2" ]; then
    if diff -r "$1" "$2" >/dev/null 2>&1; then rm -rf "$1"; echo "✅ já estava no lugar: $2"; return 0; fi
    echo "⚠️ $2 existe de novo e é diferente: não sobrescrevi; a cópia guardada continua em $1"; falhou=1; return 0
  fi
  if mkdir -p "$(dirname "$2")" && mv "$1" "$2"; then echo "✅ voltou: $2"; else echo "🛑 não consegui devolver $2"; falhou=1; fi
}
liga() {   # liga <para onde o atalho aponta> <atalho>
  if [ -e "$2" ] || [ -L "$2" ]; then return 0; fi
  if mkdir -p "$(dirname "$2")" && ln -s "$1" "$2"; then echo "✅ atalho de volta: $2"; else echo "🛑 não consegui refazer o atalho $2"; falhou=1; fi
}
registro() {   # registro <guardado> <atual> <cksum que a limpeza deixou>
  [ -f "$1" ] || return 0
  if [ -n "$3" ] && [ -f "$2" ] && [ "$(cksum < "$2")" = "$3" ]; then
    if cp "$1" "$2"; then echo "✅ registro do npx de volta: $2"; return 0; fi
  fi
  if [ -f "$2" ] && cmp -s "$1" "$2"; then return 0; fi
  echo "⚠️ o registro do npx ($2) mudou depois da limpeza: não mexi. Para o npx voltar a cuidar da skill, instale-a de novo pelo npx."
  falhou=1
}
CORPO
    cat "${DUP_L}/.itens" 2>/dev/null
    printf 'registro %q %q %q\n' "${DUP_L}/npx/skill-lock.json" "${lock}" "${depois}"
    printf 'if [ "${falhou}" = 0 ]; then echo "Pronto: tudo voltou ao lugar."; fi\nexit "${falhou}"\n'
  } > "${DUP_L}/desfazer.sh.novo" && mv "${DUP_L}/desfazer.sh.novo" "${DUP_L}/desfazer.sh"
}

dup_guardar() {   # cópia conferida por hash: $1 origem $2 destino $3 hash esperado
  mkdir -p "$(dirname "$2")" && cp -Rp "$1" "$2" 2>/dev/null && [ "$(dup_hash "$2")" = "$3" ] && return 0
  rm -rf "$2"; return 1
}
# Retrato das outras cópias do nome nas pastas que o npx -g não deveria tocar (as do projeto e a do ~/.codex).
dup_retrato() {   # $1 nome
  local ag es ro pa
  while IFS="${DUP_TAB}" read -r ag es ro pa; do
    case "${ro}" in home-claude|home-agents) continue ;; esac
    { [ -e "${pa}/$1" ] || [ -L "${pa}/$1" ]; } || continue
    printf '%s\t%s\n' "${pa}/$1" "$(dup_hash "$(dup_real "${pa}/$1")")"
  done <<EOF
$(dup_pastas)
EOF
}

DUP_FEITO=""   # o relatório do que saiu, uma linha por cópia
dup_tirar_mover() {   # $1 real $2 nome $3 rótulo $4 versão $5 hash
  local g="${DUP_L}/$3/$2"
  dup_guardar "$1" "${g}" "$5" || { DUP_ERRO="não consegui guardar uma cópia de $1 na lixeira; ela continua no lugar"; return 1; }
  dup_desfazer_item volta "${g}" "$1"
  rm -rf "$1" 2>/dev/null
  if [ -e "$1" ]; then DUP_ERRO="não consegui tirar $1 (a cópia guardada fica em ${g})"; return 1; fi
  DUP_FEITO="${DUP_FEITO}- $1 ($4) → ${g}"$'\n'
}
dup_tirar_npx() {   # $1 real $2 nome $3 rótulo $4 versão $5 hash $6 agentes
  local g="${DUP_L}/$3/$2" cg ga p q protegidas="" ligacoes="" antes depois saiu a args="" lock
  cg="$(dup_claude_global)/$2"; ga="$(dup_agentes_global)/$2"; lock="$(dup_registro_arquivo)"
  dup_guardar "$1" "${g}" "$5" || { DUP_ERRO="não consegui guardar uma cópia de $1 na lixeira; ela continua no lugar"; return 1; }
  dup_desfazer_item volta "${g}" "$1"
  for p in "${cg}" "${ga}"; do   # os atalhos do npx que apontam para esta cópia: o remove os apaga, o desfazer os refaz
    if [ -L "${p}" ] && [ "$(dup_real "${p}")" = "$1" ]; then
      dup_desfazer_item liga "$(readlink "${p}")" "${p}"; ligacoes="${ligacoes}${p}${DUP_TAB}$(readlink "${p}")"$'\n'
    fi
  done
  mkdir -p "${DUP_L}/npx"
  [ -f "${DUP_L}/npx/skill-lock.json" ] || cp -p "${lock}" "${DUP_L}/npx/skill-lock.json" 2>/dev/null
  # a outra pasta de mesmo nome que o remove apagaria (medido): vai para a lixeira e volta logo depois
  for p in "${cg}" "${ga}"; do
    { [ -e "${p}" ] || [ -L "${p}" ]; } || continue
    [ "$(dup_real "${p}")" = "$1" ] && continue
    if [ "${p}" = "${cg}" ]; then q="${DUP_L}/protegidas/home-claude/$2"; else q="${DUP_L}/protegidas/home-agents/$2"; fi
    if [ -L "${p}" ]; then
      dup_desfazer_item liga "$(readlink "${p}")" "${p}"; printf 'L\t%s\t%s\n' "${p}" "$(readlink "${p}")" >> "${DUP_L}/.protegidas"; rm -f "${p}"
    else
      dup_guardar "${p}" "${q}" "$(dup_hash "${p}")" || { DUP_ERRO="não consegui proteger ${p} antes do npx; nada saiu desta skill"; dup_volta_protegidas; rm -rf "${g}"; return 1; }
      dup_desfazer_item volta "${q}" "${p}"; printf 'D\t%s\t%s\n' "${p}" "${q}" >> "${DUP_L}/.protegidas"; rm -rf "${p}"
    fi
  done
  antes="$(dup_retrato "$2")"
  for a in $6; do args="${args} -a ${a}"; done
  # shellcheck disable=SC2086
  # HOME explícito: o npx tem de agir na mesma pasta pessoal que o plano leu (um HOME não exportado faria o node cair na
  # pasta pessoal do sistema)
  HOME="${HOME}" "${SDD_CHECAR_NPX:-npx}" --yes skills remove "$2" -g ${args} -y </dev/null > "${DUP_L}/npx/remove-$2.log" 2>&1
  saiu=1
  { [ -e "$1" ] || [ -L "$1" ]; } && saiu=0
  while IFS="${DUP_TAB}" read -r p q; do [ -n "${p}" ] && { [ -e "${p}" ] || [ -L "${p}" ]; } && saiu=0; done <<EOF
${ligacoes}
EOF
  depois="$(dup_retrato "$2")"
  dup_volta_protegidas || { DUP_ERRO="o npx rodou, mas não consegui devolver uma pasta protegida; rode o desfazer"; return 1; }
  if [ "${saiu}" = 0 ]; then
    dup_registro_devolve
    rm -rf "${g}"
    DUP_ERRO="o npx não tirou $1 (ele diz que outra ferramenta ainda usa esta skill); nada mudou nesta cópia"
    return 1
  fi
  if [ "${antes}" != "${depois}" ]; then
    mv "${g}" "$1" 2>/dev/null
    while IFS="${DUP_TAB}" read -r p q; do [ -n "${p}" ] && ln -s "${q}" "${p}" 2>/dev/null; done <<EOF
${ligacoes}
EOF
    dup_registro_devolve
    DUP_ERRO="o npx mexeu numa pasta fora do plano; devolvi $1 e o registro; confira com o plano de novo"
    return 1
  fi
  cksum < "${lock}" > "${DUP_L}/npx/depois.cksum" 2>/dev/null || : > "${DUP_L}/npx/depois.cksum"
  dup_desfazer_grava
  DUP_FEITO="${DUP_FEITO}- $1 ($4, saiu pelo npx skills remove) → ${g}"$'\n'
}
dup_volta_protegidas() {
  local t p q ok=0
  [ -f "${DUP_L}/.protegidas" ] || return 0
  while IFS="${DUP_TAB}" read -r t p q; do
    if [ "${t}" = L ]; then [ -e "${p}" ] || [ -L "${p}" ] || ln -s "${q}" "${p}" || ok=1
    elif [ -e "${q}" ]; then
      if [ -e "${p}" ] || [ -L "${p}" ]; then ok=1; else mkdir -p "$(dirname "${p}")" && mv "${q}" "${p}" || ok=1; fi
    fi
  done < "${DUP_L}/.protegidas"
  rm -f "${DUP_L}/.protegidas"
  return "${ok}"
}
dup_registro_devolve() {
  local lock; lock="$(dup_registro_arquivo)"
  [ -f "${DUP_L}/npx/skill-lock.json" ] || return 0
  cmp -s "${DUP_L}/npx/skill-lock.json" "${lock}" 2>/dev/null || cp -p "${DUP_L}/npx/skill-lock.json" "${lock}"
}

# $1 = assinatura · $2 = o comando do checar.sh · $3 = a pasta desta skill (a cópia que está rodando sai por último)
dup_limpar() {
  local sig="${1:-}" cmd="$2" eu="${3:-}" atual base stamp i r n ro mt ve h ags nt lista
  if [ -z "${sig}" ]; then
    printf '🛑 Falta a assinatura do plano. Nada foi tirado.\n→ peça o plano: %s --duplicadas\n' "${cmd}"; return 2
  fi
  dup_planejar || { echo "🛑 Não consegui ler as pastas de skills. Nada foi tirado."; return 2; }
  atual="$(dup_assinatura)"
  if [ "${sig}" != "${atual}" ]; then
    printf '🛑 O plano mudou desde que você o viu (alguma cópia mudou, apareceu ou sumiu). Nada foi tirado.\n→ peça o plano de novo: %s --duplicadas\n' "${cmd}"
    return 2
  fi
  nt="$(grep -c '^T	' "${DUP_TMP}/plano.tsv")"
  if [ "${nt}" -eq 0 ]; then echo "✅ O plano não tem nada a tirar. Nada foi tirado."; return 0; fi
  if grep '^T	' "${DUP_TMP}/plano.tsv" | cut -f5 | grep -qx npx && ! command -v "${SDD_CHECAR_NPX:-npx}" >/dev/null 2>&1; then
    printf '🛑 Uma das cópias veio pelo npx e o npx não está disponível neste terminal. Nada foi tirado.\n→ instale o Node.js (https://nodejs.org), abra o terminal de novo e peça o plano outra vez.\n'
    return 2
  fi
  base="${HOME}/.sdd-lixeira"; stamp="$(date +%Y%m%d-%H%M%S)"; DUP_L="${base}/${stamp}"; i=2
  while [ -e "${DUP_L}" ]; do DUP_L="${base}/${stamp}-${i}"; i=$((i + 1)); done
  if ! mkdir -p "${DUP_L}" 2>/dev/null; then
    printf '🛑 Não consegui criar a lixeira em %s. Nada foi tirado.\n→ confira se a sua pasta pessoal aceita gravação e peça o plano de novo.\n' "${DUP_L}"
    return 2
  fi
  : > "${DUP_L}/.itens"
  printf 'Cópias de skills tiradas por sdd-checar-ambiente --limpar em %s. Para devolver tudo: bash desfazer.sh\n' "${stamp}" > "${DUP_L}/LEIA.txt"
  dup_desfazer_grava
  # a cópia de onde este script roda sai por último (o bash já leu o que precisa; a pasta pode sumir depois)
  lista="$(grep '^T	' "${DUP_TMP}/plano.tsv" | LC_ALL=C awk -F '\t' -v eu="${eu}" '{ print ($2 == eu ? 1 : 0) "\t" $0 }' | LC_ALL=C sort -s -k1,1n | cut -f2-)"
  DUP_ERRO=""
  while IFS="${DUP_TAB}" read -r i r n ro mt ve h ags; do
    if [ "${mt}" = npx ]; then dup_tirar_npx "${r}" "${n}" "${ro}" "${ve}" "${h}" "${ags}" || break
    else dup_tirar_mover "${r}" "${n}" "${ro}" "${ve}" "${h}" || break; fi
  done <<EOF
${lista}
EOF
  if [ -n "${DUP_FEITO}" ]; then
    printf '✅ Tirei %s; estão guardadas em %s:\n%s' "$(printf '%s' "${DUP_FEITO}" | grep -c '^- ') cópia(s)" "${DUP_L}" "${DUP_FEITO}"
  fi
  if [ -n "${DUP_ERRO}" ]; then
    if [ -n "${DUP_FEITO}" ]; then printf '⚠️ Parei: %s. As cópias seguintes não foram tocadas.\n' "${DUP_ERRO}"
    else printf '🛑 %s. Nada foi tirado.\n' "${DUP_ERRO}"; fi
  fi
  printf 'Para desfazer: bash %q\n' "${DUP_L}/desfazer.sh"
  [ -z "${DUP_ERRO}" ]
}
