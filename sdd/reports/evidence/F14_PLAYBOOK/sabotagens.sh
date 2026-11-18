#!/bin/bash
# sabotagens.sh — numa cópia de HEAD, 1 sabotagem por script novo (e nas 2 regras que mais protegem); o teste nomeado tem de cair.
R="$(git rev-parse --show-toplevel)"
roda() { # nome · arquivo · python que troca o texto (de, para) · padrão do teste
  local nome="$1" arq="$2" de="$3" para="$4" padrao="$5" T; T="$(mktemp -d)"
  git -C "$R" archive HEAD | tar -x -C "$T"
  python3 -B - "$T/$arq" "$de" "$para" <<'PY' || { echo "$nome: a sabotagem não se aplicou"; rm -rf "${T:?}"; return 1; }
import sys
p, de, para = sys.argv[1:4]
s = open(p, encoding="utf-8").read()
if s.count(de) < 1:
    sys.exit(1)
open(p, "w", encoding="utf-8").write(s.replace(de, para, 1))
PY
  saida="$(cd "$T" && SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover -s tests -p "$padrao" 2>&1)"; rc=$?
  printf '%s: rc=%s · %s\n' "$nome" "$rc" "$(printf '%s\n' "$saida" | grep -E '^(FAILED|OK)' | tr '\n' ' ')"
  printf '%s\n' "$saida" | grep -E '^(FAIL|ERROR):' | head -3 | cut -c1-120
  rm -rf "${T:?}"
  if [ "$rc" -eq 0 ] && [ "${CONHECIDA:-}" = "$nome" ]; then
    echo "   ⚠️ VIVA CONHECIDA: pendência da F14_DRIVE; o teste que a derruba está em pendencia-r5-teste-lado2.patch (decisão D4 do Roberto: sem mudança de código depois da rodada 4)"
    conhecidas=$((conhecidas + 1))
  else
    [ "$rc" -ne 0 ] || { echo "   ⚠️ a sabotagem NÃO derrubou teste"; vivos=$((vivos + 1)); }
  fi
}
vivos=0; conhecidas=0; CONHECIDA="copiar-docs: salvos voltam a incluir o índice (R5)"
roda "curator: AUTO por existência, sem a igualdade da evidência" sdd/bin/playbook-curator.sh 'elif not re.match(re.escape(esperada) + r"(\D|$)", ev_txt):' 'elif False:' test_curadoria_bloco.py
roda "curator: todo bullet conta como promovido" sdd/bin/playbook-curator.sh 'return not b["promo"].startswith("—")' 'return True' test_playbook_curator.py
roda "curator: --aplicar imprime mesmo com delta inválido" sdd/bin/playbook-curator.sh '    erros = validar_delta(linhas, bullets, pb, texto)
    if erros:' '    erros = validar_delta(linhas, bullets, pb, texto)
    if False:' test_playbook_curator.py
roda "curator: trava ignora origem aposentada" sdd/bin/playbook-curator.sh 'elif b["tipo"] == "tomb":
                defeitos.append("%s tem origem=%s, que está aposentada' 'elif False:
                defeitos.append("%s tem origem=%s, que está aposentada' test_playbook_invariantes.py
roda "curator: selo não confere o staging" sdd/bin/playbook-curator.sh 'if selado.get(nome) != agora.get(nome):' 'if False:' test_curadoria_bloco.py
roda "curator: contador repetido passa" sdd/bin/playbook-curator.sh 'if len(numeros) > 1:' 'if False:' test_curadoria_bloco.py
roda "curator: 2ª linha da mesma lição não entra no registro" sdd/bin/playbook-curator.sh 'self.saida[k] += "," + fp' 'pass' test_playbook_curator.py
roda "curator: seção que falta não nasce" sdd/bin/playbook-curator.sh 'blocos.insert(pos, ["## " + sec, [""]])' 'pass' test_playbook_curator.py
roda "lint: anti-collapse sem o piso" sdd/bin/playbook-lint.sh 'if [ "${mudou}" -gt 1 ] && [ $((mudou * 100))' 'if [ $((mudou * 100))' test_playbook_curator.py
roda "curator: veredito só de célula curta (o conserto que regrediu)" sdd/bin/playbook-curator.sh 'else "mordeu" if re.match(r"^mordeu(\W|$)", c) else ""' 'else "mordeu" if (re.match(r"^mordeu(\W|$)", c) and len(c) <= 24) else ""' test_playbook_curator.py
roda "curator: ID de qualquer célula da linha (a regressão do ciclo 3)" sdd/bin/playbook-curator.sh 'RE_LM.findall(cels[col_id])' 'RE_LM.findall(ln)' test_playbook_curator.py
roda "curator: tabela sem cabeçalho conta do mesmo jeito" sdd/bin/playbook-curator.sh 'if not cabecalho or col_id is None or col_ver is None:' 'if False:' test_playbook_curator.py
roda "curator: check que sai da raiz passa" sdd/bin/playbook-curator.sh 'if os.path.isabs(caminho) or n == ".." or n.startswith("../"):
        return False
    raiz = os.path.realpath(os.getcwd())
    return (os.path.realpath(caminho) + os.sep).startswith(raiz + os.sep)  # um link não pode levar para fora' 'return True' test_playbook_invariantes.py
roda "curator: check por link que sai da raiz passa" sdd/bin/playbook-curator.sh 'return (os.path.realpath(caminho) + os.sep).startswith(raiz + os.sep)  # um link não pode levar para fora' 'return True' test_playbook_invariantes.py
roda "copiar-docs: prefixo no lugar de nome idêntico" .agents/skills/sdd-new-session/scripts/copiar-docs.sh 'if [ "${fk}" = "${SLUG}" ]; then' 'case "${fk}" in "${SLUG}"*) igual=1 ;; *) igual=0 ;; esac; if [ "${igual}" = 1 ]; then' test_copiar_docs.py
roda "fronteira: índice fora da comparação" sdd/bin/governanca-fronteira.sh 'for chave in REF INDICE GIT; do' 'for chave in REF GIT; do' test_governanca_fronteira.py
roda "bloco: FORA: não invalida" sdd/bin/governanca-bloco.py 'if l.startswith("FORA:"):' 'if False:' test_governanca_bloco.py
roda "apoio: sandbox herda SDD_TRACE" tests/apoio.py 'if k not in ("SDD_TRACE", "SDD_TRACE_DIR")' 'if True' test_apoio_ambiente.py
roda "fronteira: branch.* volta a contar (R1 da rodada 3)" sdd/bin/governanca-fronteira.sh 'if e and not e.lower().startswith(b"branch."))' 'if e)' test_governanca_fronteira.py
roda "fronteira: o config inteiro fora da medida (o outro lado de R1)" sdd/bin/governanca-fronteira.sh 'h.update(b"\0".join(sorted(e for e in cfg.split(b"\0") if e and not e.lower().startswith(b"branch."))))' 'pass' test_governanca_fronteira.py
roda "design-lint: JSON preenchido volta a ser chave (R2)" sdd/bin/design-lint.py 'nome not in campos and nome and CHAVE_MOLDE.search(cels[1])' 'nome not in campos and nome and CHAVE.search(cels[1])' test_design_lint.py
roda "design-lint: molde nunca conta nos campos extras (o outro lado de R2)" sdd/bin/design-lint.py 'nome not in campos and nome and CHAVE_MOLDE.search(cels[1])' 'False' test_design_lint.py
roda "curator: REFINE guarda a 1ª ocorrência (R3)" sdd/bin/playbook-curator.sh 'k_pp = velho.rfind("promovido_para: ")' 'k_pp = velho.find("promovido_para: ")' test_playbook_curator.py
roda "curator: campo vazio passa (R4)" sdd/bin/playbook-curator.sh 'defeitos.append("%s tem '"'"'· tarefa:'"'"' ou '"'"'· motivo:'"'"' vazio — preencha ou tire o campo" % i["id"])' 'pass' test_playbook_invariantes.py
roda "copiar-docs: só no índice some da lista (R5)" .agents/skills/sdd-new-session/scripts/copiar-docs.sh '&& git -C "${PRINCIPAL}" diff --cached --name-only --diff-filter=A -z -- "${dir}"; }' '; }' test_copiar_docs.py
roda "copiar-docs: salvos voltam a incluir o índice (R5)" .agents/skills/sdd-new-session/scripts/copiar-docs.sh 'git -C "${PRINCIPAL}" ls-tree -r -z --name-only HEAD -- "${dir}"' 'git -C "${PRINCIPAL}" ls-files -z -- "${dir}"' test_copiar_docs.py
roda "copiar-docs: seta sem o aviso do link (R6)" .agents/skills/sdd-new-session/scripts/copiar-docs.sh 'elif [ "${ignorados}" -gt 0 ]; then' 'elif false; then' test_copiar_docs.py
printf 'sabotagens vivas: %s · vivas conhecidas: %s\n' "$vivos" "$conhecidas"
[ "$vivos" -eq 0 ]
