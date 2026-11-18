#!/bin/bash
# sabotagens.sh — numa cópia de HEAD, 1 sabotagem por script novo e nas regras que mais protegem; o teste nomeado tem de cair.
R="$(git rev-parse --show-toplevel)"
VIVOS="$(mktemp)"
_um() { # nome · arquivo · de · para · padrão do teste
  local nome="$1" arq="$2" de="$3" para="$4" padrao="$5" T; T="$(mktemp -d)"
  git -C "$R" archive "$SHA" | tar -x -C "$T"
  python3 -B - "$T/$arq" "$de" "$para" <<'PY' || { echo "$nome: A SABOTAGEM NÃO SE APLICOU"; echo x >> "$VIVOS"; rm -rf "${T:?}"; return 1; }
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
  [ "$rc" -ne 0 ] || { echo "   ⚠️ a sabotagem NÃO derrubou teste"; echo x >> "$VIVOS"; }
}
SHA="$(git -C "$R" rev-parse HEAD)"
roda() { # em paralelo, até 4: cada resultado sai inteiro, de uma vez
  while [ "$(jobs -r | wc -l)" -ge 4 ]; do sleep 1; done
  ( saida="$(_um "$@")"; printf '%s\n' "$saida" ) &
}
D=sdd/bin/sdd-drive.sh; S=sdd/bin/deploy-do-sha.sh; A=sdd/bin/sdd-archive.py
roda "drive: limite não barra" $D 'def barra_orcamento(p, st):
    if vermelhos(st) >= st["maximo"]:' 'def barra_orcamento(p, st):
    if False:' test_drive.py
roda "drive: gate alterado não para" $D 'if sha != st["gate_sha"]:' 'if False:' test_drive.py
roda "drive: verde do comando antigo vale" $D 'if not st["gates"] or st["gates"][-1].get("impressao") != st["gate_sha"]:' 'if not st["gates"]:' test_drive.py
roda "drive: código sujo passa" $D 'if not e_documento(reg[3:]):' 'if False:' test_drive.py
roda "drive: tudo sujo vira COMMITAR (o outro lado)" $D 'if not e_documento(reg[3:]):' 'if True:' test_drive.py
roda "drive: 2 gates juntos" $D '        if not pega_trava(p):' '        if pega_trava(p) and False:' test_drive.py
roda "drive: repetição sem teto" $D 'if rep["n"] >= REPETICOES:' 'if False:' test_drive.py
roda "drive: concluir publica" $D '    parada(p, st, "gate-verde",' '    git(p.raiz, "push", "origin", "HEAD")
    parada(p, st, "gate-verde",' test_drive.py
roda "drive: seguir sem motivo vira DESIGN" $D 'if rc not in (0, 1) or (rc == 1 and not parou):' 'if False:' test_drive.py
roda "drive: verde grava o HEAD de depois do gate" $D 'commit=commit_testado, exit=rc' 'commit=p.head(), exit=rc' test_drive.py
roda "drive: gate grava a impressão de depois" $D 'impressao=impressao_testada)' 'impressao=st["gate_sha"])' test_drive.py
roda "drive: variável do fundo chega ao gate" $D 'env_gate.pop("SDD_DRIVE_TRAVA_HERDADA", None)' 'pass' test_drive.py
roda "drive: rename tira código sem acusar" $D 'if k < len(itens) and not e_documento(itens[k]):' 'if False:' test_drive.py
roda "drive: extensão não conta (M2 do ciclo 3)" $D 'return caminho.startswith(SO_DOCUMENTOS) and caminho.lower().endswith(EXT_DOCUMENTO)' 'return caminho.startswith(SO_DOCUMENTOS)' test_drive.py
roda "drive: submodule some do diff (M1 do ciclo 3)" $D '"--no-renames", "--ignore-submodules=none", "-z"' '"--no-renames", "-z"' test_drive.py
roda "drive: gate sem log prova (M3 do ciclo 3)" $D 'return g if confirma else None' 'return g' test_drive.py
roda "drive: bloqueio não segura (L4 do ciclo 3)" $D 'if st.get("motivo") == "bloqueio-humano":' 'if False:' test_drive.py
roda "drive: branch só no início (L5 do ciclo 3)" $D '    motivo = branch_proibida(p)
    if motivo:
        parada(p, st, "branch-padrao", motivo)' '    pass' test_drive.py
roda "drive: estado com forma errada passa" $D '    if not forma_ok(st):' '    if not isinstance(st, dict) or any(k not in st for k in CAMPOS_ESTADO):' test_drive.py
roda "drive: concluir ignora o proximo" $D '    if nome != "AVALIAR_E_RELATAR":
        ult = ultimo_valido(p, st)' '    if False:
        ult = ultimo_valido(p, st)' test_drive.py
roda "drive: vizinho antigo passa" $D 'if not os.path.isfile(caminho) or marca not in ler(caminho):' 'if False:' test_drive.py
roda "drive: frase do verde sem a barreira" $D 'O teste final passou e os relatórios estão prontos. Nada foi publicado.' 'O teste final passou e os relatórios estão prontos.' test_drive.py
roda "drive: self-test não confere" $D '        if not ok:
            falhas.append(nome)' '        if False:
            falhas.append(nome)' test_drive.py
roda "drive: rename some do diff entre commits (H1 do ciclo 2)" $D '"--name-only", "--no-renames", "--ignore-submodules=none"' '"--name-only", "--ignore-submodules=none"' test_drive.py
roda "drive: a 2ª tabela vira tarefa" $D '                break  # só a 1ª tabela' '                continue  # só a 1ª tabela' test_drive.py
roda "drive: a variável abre a trava" $D 'if os.environ.get("SDD_DRIVE_TRAVA_HERDADA") != "1":
        return False
    for _ in range(40):' 'if os.environ.get("SDD_DRIVE_TRAVA_HERDADA") == "1":
        return True
    for _ in range(40):' test_drive.py
roda "archive: caixa e palavra (M2 e M3 do ciclo 2)" $A ', nfc(nome), re.I):' ', nfc(nome)):' test_sdd_archive.py
roda "archive: sem fronteira de palavra" $A 'r"(?<![^\W_])" + re.escape(nfc(n)) + r"(?![^\W_])"' 're.escape(nfc(n))' test_sdd_archive.py
roda "deploy: job falho sem passo repete" $S 'achados = ["job %s" % job.get("name")]' 'achados = []' test_deploy_do_sha.py
roda "deploy: workflow desconhecido espera o teto" $S 'if re.search(r"could not find any workflows|^HTTP 404", str(e), re.I):' 'if False:' test_deploy_do_sha.py
roda "deploy: cancelado não espera (R1 da rodada 3)" $S 'elif conc != "failure" and not novos and time.time() - inicio < sem_run:' 'elif False:' test_deploy_do_sha.py
roda "deploy: toda falha do disparo é recusa (R2 da rodada 3)" $S 'if re.search(r"HTTP 4\d\d", str(e)):' 'if True:' test_deploy_do_sha.py
roda "deploy: marca depois do disparo" $S '                        if d.marcar():' '                        if True:' test_deploy_do_sha.py
roda "drive: anotação zera a repetição (R1 da rodada 2)" $D 'identidade = re.sub(r" — .*$", "", detalhe, flags=re.S) if nome == "RODADA" else detalhe' 'identidade = detalhe' test_drive.py
roda "drive: resume zera sempre (R2 da rodada 1)" $D '    if st.get("motivo") == "bloqueio-humano":
        st["repeticao"] = dict(chave="", n=0)' '    st["repeticao"] = dict(chave="", n=0)' test_drive.py
roda "drive: link sai do repositório (R2 da rodada 2)" $D '        confere_dentro(self)' '        pass' test_drive.py
roda "drive: trava em 2 tempos (R10 da rodada 1)" $D '        os.link(tmp, trava(p))' '        open(trava(p), "x").close(); time.sleep(0.2); os.replace(tmp, trava(p))' test_drive.py
roda "drive: sem a trava de estado (R2 do Codex)" $D '    segura_estado(p)
    st, defeito = le_estado(p)' '    st, defeito = le_estado(p)' test_drive.py
roda "deploy: marca sem exclusividade (R1 do Codex)" $S 'with open(m, "x", encoding="utf-8") as f:' 'with open(m, "w", encoding="utf-8") as f:' test_deploy_do_sha.py
roda "deploy: fetch que falha sai 64 (R1 de Claude)" $S '        if busca.returncode != 0:' '        if False:' test_deploy_do_sha.py
roda "deploy: só o 1º passo falho conta" $S '                        if real:
                            fim(2' '                        if passos[0] not in transitorios:
                            fim(2' test_deploy_do_sha.py
roda "deploy: outro evento conta" $S 'and r.get("event") in ("push", "workflow_dispatch")]' ']' test_deploy_do_sha.py
roda "deploy: outra branch conta" $S 'if isinstance(r, dict) and r.get("headBranch") == self.branch' 'if isinstance(r, dict)' test_deploy_do_sha.py
roda "deploy: rerun no lugar do dispatch" $S 'd.gh("workflow", "run", workflow, "--ref", branch)' 'd.gh("run", "rerun", str(alvo_run))' test_deploy_do_sha.py
roda "deploy: repete fora da ponta" $S 'if ponta != x:' 'if False:' test_deploy_do_sha.py
roda "deploy: substituto sem conferir que contém" $S 'if c is True:' 'if True:' test_deploy_do_sha.py
roda "deploy: repetido 2 vezes" $S 'if ja_redisparou:
                            fim(2' 'if False:
                            fim(2' test_deploy_do_sha.py
roda "deploy: corrida sai 2" $S 'fim(4, "⏳ ainda não sei — pedi para repetir o deploy' 'fim(2, "⏳ ainda não sei — pedi para repetir o deploy' test_deploy_do_sha.py
roda "archive: prefixo curto primeiro" $A 'key=len, reverse=True))' 'key=len))' test_sdd_archive.py
roda "archive: documento solto citado sai" $A 'elif nfc(os.path.basename(p)).casefold() in citado:' 'elif False:' test_sdd_archive.py
roda "archive: slice não protege" $A 'abertas.setdefault(re.sub(r"_s\d+[a-z]?$", "", m.group(1)), corpo)' 'pass' test_sdd_archive.py
roda "archive: edição sem commit não conta" $A 'if nfc(p) in sujos:' 'if False:' test_sdd_archive.py
roda "archive: --aplicar sem lote" $A 'if a.aplicar and not a.lote:' 'if False:' test_sdd_archive.py
roda "archive: move não rastreado" $A '        if nfc(src) not in rastreados:
            continue' '        if False:
            continue' test_sdd_archive.py
roda "archive: ✅ em qualquer lugar fecha a ficha" $A 's.group(1).strip().startswith("✅")' '"✅" in s.group(1)' test_sdd_archive.py
roda "archive: citação casa vizinho" $A 'r"(?<![^\W_])" + re.escape(nfc(n).casefold()) + r"(?![^\W_])"' 're.escape(nfc(n).casefold())' test_sdd_archive.py
roda "archive: citação só na caixa exata (M4 do ciclo 3)" $A 'citado = nfc("\n".join(abertas.values())).casefold()' 'citado = "\n".join(abertas.values())' test_sdd_archive.py
roda "archive: prefixo protege todos (L12 do ciclo 3)" $A 'n = ficha_do_nome(sem_prefixo(os.path.basename(p)))
            if n:
                return' 'n = ficha_do_nome(os.path.basename(p))
            if n:
                return' test_sdd_archive.py
roda "archive: simulação muda arquivo" $A 'if not a.aplicar:
        print("Nada foi movido.")' 'if False:
        print("Nada foi movido.")' test_sdd_archive.py
roda "gate: --checar não confere o cmd" sdd/bin/verify-gate.sh 'if [ "${KIND}" != "manual-ux" ] && { [ -z "${CMD}" ] || [ "${CMD#N/A}" != "${CMD}" ]; }; then' 'if false; then' test_verify_gate.py
roda "gate: --checar grava trace" sdd/bin/verify-gate.sh '[ "${CHECAR}" = "1" ] && return 0' ':' test_verify_gate.py
roda "fluxo: --drive ainda lê o slot" sdd/bin/sdd-fluxo.sh 'rc, linha = (0, "") if drive else estado(raiz)' 'rc, linha = estado(raiz)' test_fluxo.py
roda "guarda: não rastreado em qualquer pasta passa" sdd/bin/avaliador-guard.sh 'sdd/features/*|sdd/handoffs/*|sdd/reports/*|sdd/reviews/*) DOCS' '*) DOCS' test_avaliador_guard.py
roda "guarda: documento volta a travar (o outro lado)" sdd/bin/avaliador-guard.sh 'if [ "${st}" = "??" ]; then' 'if false; then' test_avaliador_guard.py
roda "curador: conta eco e diagnóstico (L10)" sdd/bin/playbook-curator.sh ' and not NAO_E_ACHADO.match(ln)' '' test_playbook_curator.py
roda "curador: ignora todo ❌ (o outro lado de L10)" sdd/bin/playbook-curator.sh 'NAO_E_ACHADO = re.compile(r"^\s*(?:│\s*)*(\$ |\+ |❌ (delta|invariantes) linha \d+:|🔴 trava INV:|\S+\.md:\d+: ❌ )")' 'NAO_E_ACHADO = re.compile(r"^.*❌")' test_playbook_curator.py
roda "release: item 10 volta a ter a lógica" .agents/skills/sdd-release/SKILL.md 'Verde não prova teste:' 'gh run list --commit: Verde não prova teste:' test_f14_drive_textos.py
wait
vivos="$(wc -l < "$VIVOS" | tr -d ' ')"; rm -f "$VIVOS"
printf 'sabotagens: %s no total\n' "$(grep -c '^roda ' "$0")"
printf 'sabotagens vivas: %s\n' "$vivos"
[ "$vivos" -eq 0 ]
