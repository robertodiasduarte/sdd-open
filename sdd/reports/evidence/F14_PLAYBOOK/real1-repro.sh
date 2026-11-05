#!/bin/bash
# Reprodução dos achados da rodada 1, antes do conserto: exit real de cada caso.
R="$(git rev-parse --show-toplevel)"; C="$R/sdd/bin/playbook-curator.sh"; T="$(mktemp -d)"; trap 'chmod -R u+rwx "${T:?}"; rm -rf "${T:?}"' EXIT
export SDD_TRACE=off; cd "$T" || exit 64
echo "## 1. playbook sem permissão (R1@claude, R2@codex): esperado exit 2, nunca 1"
mkdir st; printf '# P\n\n## Sempre\n\n- [LM-901] ajudou=0 mordeu=0 · conf=2026-01-01 · sup: `filas_de_envio` :: r. **Do instead:** x. · promovido_para: —\n\n## Tombstones\n' > pb.md
chmod 000 pb.md; /bin/bash "$C" --colher st pb.md >o1 2>e1; echo "exit=$?"; grep -c Traceback e1; chmod 600 pb.md
echo "## 2. sugestão em 2 arquivos (R3): a 2ª release não pode trazer sugestão nova"
printf '❌ a filas_de_envio parou\n' > st/AVAL-1.log; printf '❌ de novo filas_de_envio\n' > st/AVAL-2.log
/bin/bash "$C" --colher st pb.md > c1; grep ' · fp=' c1 > st/CURATOR-colhidos.txt; /bin/bash "$C" --colher st pb.md > c2; grep -c '^SUGESTAO' c2
echo "## 3. restauração com link no intermediário (R1@codex): alvo tem de ficar intacto"
mkdir w; printf 'antes\n' > w/DEFINE.antes; printf 'mexido\n' > w/DEFINE.md; printf 'vitima\n' > w/vitima.txt; ln -s vitima.txt w/DEFINE.md.restaurando
# a sequência é a que está no texto da skill naquele momento: o log "antes" foi gravado com a anterior, sem o 1º rm
SEQ="$(grep -oE '`[^`]*DEFINE_<F>\.md\.restaurando[^`]*`' "$R/.agents/skills/sdd-define/SKILL.md" | head -1 | tr -d '`')"
printf 'sequência: %s\n' "$SEQ"
( cd w && mkdir -p sdd/features && mv DEFINE.md sdd/features/DEFINE_X.md && mv DEFINE.md.restaurando sdd/features/DEFINE_X.md.restaurando && ln -sf ../../vitima.txt sdd/features/DEFINE_X.md.restaurando && T="$PWD" && S2="$(printf '%s' "$SEQ" | sed 's/<F>/X/g')" && T="$T" /bin/bash -c "T='$PWD'; $S2"; echo "exit=$?"; printf 'vitima agora: '; cat vitima.txt; ls -la sdd/features/DEFINE_X.md | cut -c1-10 )
false && ( cd w && cp DEFINE.antes DEFINE.md.restaurando && rm -f DEFINE.md && mv DEFINE.md.restaurando DEFINE.md && cmp DEFINE.antes DEFINE.md; echo "exit=$?"; printf 'vitima agora: '; cat vitima.txt; ls -la DEFINE.md | cut -c1-10 )
echo "## 4. fronteira com git traduzido (R4@claude): LC_ALL=C fixado no script"
git init -q fr; cd fr; printf 'a\n' > a; git add a; git -c user.email=a@b.c -c user.name=t commit -qm a; mkdir oculto; chmod 000 oculto
LANG=de_DE.UTF-8 LC_ALL=de_DE.UTF-8 LANGUAGE=de /bin/bash "$R/sdd/bin/governanca-fronteira.sh" --snapshot "$PWD" "$T/s1" >o4 2>&1; echo "exit=$?"; chmod 755 oculto; cd "$T"
echo "## 5. check por link que sai da raiz (R4@codex): esperado exit 2"
mkdir -p pj/sdd; printf 'x\n' > fora.sh; ln -s "$T/fora.sh" pj/sdd/check.sh; cp pb.md pj/p.md; printf '## Invariantes\n\n- [INV-001] estado=ok origem=seed check=sdd/check.sh :: R · por quê: p\n' > pj/i.md
( cd pj && /bin/bash "$C" --validar-inv p.md i.md >/dev/null 2>&1; echo "exit=$?" )
