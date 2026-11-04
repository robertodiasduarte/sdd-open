#!/bin/bash
# Controles sem agente da conferência: 1 execução válida montada precisa passar; cada variação ruim precisa reprovar.
E="$(cd "$(dirname "$0")" && pwd)"; T="$(mktemp -d)"; trap 'rm -rf "${T:?}"' EXIT
falhas=0
PROMPT='Você redige um item por commit visível, em Markdown, com o hash do commit no fim de cada item.'
base() { # $1 pasta: cópia válida, git limpo fora de src/notas e do relatório
  mkdir -p "$1/src/notas" "$1/sdd/features" "$1/sdd/reports"; printf 'x\n' > "$1/sdd/features/DESIGN_NOTAS.md"
  (cd "$1" && git init -q && git add -A && git -c user.name=p -c user.email=p@example.com commit -qm base)
  cat > "$1/src/notas/LOOP_SPEC.md" <<'M'
<LOOP_SPEC v="2" perfil="standard" nome="x">
</LOOP_SPEC>
| 1 | coletar | código | a → b | v | — | 0 | — |
| 2 | redigir | LLM | a → b | v | 100 | 0 | src/notas/redigir.txt |
| 3 | reescrever | LLM | a → b | v | 100 | 0 | src/notas/reescrever.txt |
M
  printf '%s\n' "$PROMPT" > "$1/src/notas/redigir.txt"; printf '%s\n' "$PROMPT" > "$1/src/notas/reescrever.txt"
  printf -- '- Triagem do inventário sem Tipo: loop.\n' > "$1/sdd/reports/BUILD_REPORT_NOTAS.md"
}
log_ok() { cat <<'L'
exec
/bin/zsh -lc 'cat .agents/skills/sdd-loop-builder/SKILL.md' in /x
 succeeded in 0ms:
name: sdd-loop-builder
exec
/bin/zsh -lc 'cat .agents/skills/sdd-prompt-builder/SKILL.md' in /x
 succeeded in 0ms:
name: sdd-prompt-builder

codex
Pronto.
L
}
scan_ok() { for f in LOOP_SPEC.md redigir.txt reescrever.txt; do printf -- '--conteudo src/notas/%s\trc=0\texistia=0\n' "$f"; done; }
conf() { /usr/bin/python3 -B "$E/confere_roteador.py" "$1" "$2" "$3" "$4" 2>&1; }
espera() { # rc esperado · nome · modo · pasta · log · scanlog
  local s rc; s="$(conf "$3" "$4" "$5" "$6")"; rc=$?
  if [ "$rc" -ne "$1" ]; then falhas=$((falhas+1)); printf '❌ %s: rc=%s (esperado %s)\n%s\n' "$2" "$rc" "$1" "$s"; else printf '✅ %s: rc=%s — %s\n' "$2" "$rc" "$(printf '%s' "$s" | head -1 | cut -c1-90)"; fi
}
novo() { d="$T/$1"; base "$d"; log_ok > "$T/$1.log"; scan_ok > "$T/$1.scan"; }
novo ok
espera 0 'execução válida, caminho feliz' feliz "$d" "$T/ok.log" "$T/ok.scan"
espera 0 'execução válida, sem Tipo' sem-tipo "$d" "$T/ok.log" "$T/ok.scan"
d="$T/v"; mkdir -p "$d/src/notas"; : > "$d/src/notas/LOOP_SPEC.md"; : > "$d/src/notas/redigir.txt"; : > "$d/src/notas/reescrever.txt"; printf 'nada\n' > "$T/v.log"; : > "$T/v.scan"
espera 1 '3 arquivos vazios' feliz "$d" "$T/v.log" "$T/v.scan"
novo s; printf 'exec\n/bin/zsh -lc ls in /x\n succeeded in 0ms:\n\ncodex\nleia sdd-loop-builder/SKILL.md e sdd-prompt-builder/\n' > "$T/s.log"
espera 1 'skills só em prosa, sem comando' feliz "$d" "$T/s.log" "$T/s.scan"
novo l; sed -i.bak 's/cat \.agents\/skills\/sdd-loop-builder\/SKILL.md/ls .agents\/skills\/sdd-loop-builder\/SKILL.md/' "$T/l.log"
espera 1 'ls da skill não é leitura' feliz "$d" "$T/l.log" "$T/l.scan"
novo c; sed -i.bak "s/-lc 'cat \.agents\/skills\/sdd-loop-builder/-lc 'echo cat .agents\/skills\/sdd-loop-builder/" "$T/c.log"
espera 1 'echo cat não é leitura' feliz "$d" "$T/c.log" "$T/c.scan"
novo f; /usr/bin/python3 -B - "$T/f.log" <<'P'
import sys
p=sys.argv[1]; t=open(p,encoding='utf-8').read().replace(' succeeded in 0ms:\nname: sdd-loop-builder',' exited 1 in 0ms:\ncat: não existe',1); open(p,'w',encoding='utf-8').write(t)
P
espera 1 'leitura da skill que falhou' feliz "$d" "$T/f.log" "$T/f.scan"
novo cp; /usr/bin/python3 -B - "$T/cp.log" <<'P'
import sys
# Leitura válida num comando composto cujo último passo sai 1: o conteúdo está na saída, e isso basta.
p=sys.argv[1]; t=open(p,encoding='utf-8').read().replace(' succeeded in 0ms:\nname: sdd-loop-builder',' exited 1 in 0ms:\nname: sdd-loop-builder',1); open(p,'w',encoding='utf-8').write(t)
P
espera 0 'leitura válida em comando composto que sai 1' feliz "$d" "$T/cp.log" "$T/cp.scan"
novo n; : > "$T/n.scan"
espera 1 'nenhuma chamada real do scan' feliz "$d" "$T/n.log" "$T/n.scan"
novo x; sed -i.bak 's/rc=0/rc=64/' "$T/x.scan"
espera 1 'scan que saiu 64' feliz "$d" "$T/x.log" "$T/x.scan"
novo y; sed -i.bak 's/rc=0/rc=127/' "$T/y.scan"
espera 1 'scan que nem rodou (127)' feliz "$d" "$T/y.log" "$T/y.scan"
novo w; sed -i.bak 's/existia=0/existia=1/' "$T/w.scan"
espera 1 'gravou antes de varrer' feliz "$d" "$T/w.log" "$T/w.scan"
novo u; printf -- '--conteudo src/notas/LOOP_SPEC.md\trc=0\texistia=0\n' > "$T/u.scan"
espera 1 '1 scan só, para 3 arquivos' feliz "$d" "$T/u.log" "$T/u.scan"
novo o; /usr/bin/python3 -B - "$T/o.log" <<'P'
import sys
p=sys.argv[1]; t=open(p,encoding='utf-8').read().replace('sdd-loop-builder/SKILL','TROCA').replace('sdd-prompt-builder/SKILL','sdd-loop-builder/SKILL').replace('TROCA','sdd-prompt-builder/SKILL'); open(p,'w',encoding='utf-8').write(t)
P
espera 1 'skill de prompt antes da do laço' feliz "$d" "$T/o.log" "$T/o.scan"
novo g; printf 'y\n' > "$d/sdd/features/DESIGN_NOTAS.md"
espera 1 'DESIGN reescrito' feliz "$d" "$T/g.log" "$T/g.scan"
novo r; printf 'x\n' > "$d/sdd/reports/qualquer.sh"
espera 1 'arquivo a mais em sdd/reports' feliz "$d" "$T/r.log" "$T/r.scan"
novo m; printf ' \n' > "$d/src/notas/redigir.txt"
espera 1 'prompt de 1 espaço' feliz "$d" "$T/m.log" "$T/m.scan"
novo t; printf -- '- Nenhuma triagem foi feita; loop não avaliado.\n' > "$d/sdd/reports/BUILD_REPORT_NOTAS.md"
espera 1 'relatório diz que não houve triagem' sem-tipo "$d" "$T/t.log" "$T/t.scan"
novo t2; printf -- '- A triagem não foi feita; loop ignorado.\n' > "$d/sdd/reports/BUILD_REPORT_NOTAS.md"
espera 1 'relatório diz que a triagem não foi feita' sem-tipo "$d" "$T/t2.log" "$T/t2.scan"
d="$T/a"; mkdir -p "$d"; (cd "$d" && git init -q); printf 'exec\n/bin/zsh -lc ls in /x\n succeeded in 0ms:\nsaída com [D2 · muda o produto]\n\ncodex\nFeito.\n' > "$T/a.log"; : > "$T/a.scan"
espera 1 'sem-skill com D2 só na saída de um comando' sem-skill "$d" "$T/a.log" "$T/a.scan"
d="$T/b"; mkdir -p "$d/src/agente"; printf 'x\n' > "$d/src/agente/p.txt"; (cd "$d" && git init -q); printf 'codex\n[D2 · muda o produto] pergunta\n' > "$T/b.log"; : > "$T/b.scan"
espera 1 'sem-skill com prompt improvisado noutra pasta' sem-skill "$d" "$T/b.log" "$T/b.scan"
d="$T/c0"; mkdir -p "$d"; (cd "$d" && git init -q); printf 'codex\n**Sua decisão** — [D2 · muda o produto] **?**\n' > "$T/c0.log"; : > "$T/c0.scan"
espera 0 'sem-skill válido' sem-skill "$d" "$T/c0.log" "$T/c0.scan"
echo "controles com resultado errado: $falhas"; [ "$falhas" -eq 0 ]
