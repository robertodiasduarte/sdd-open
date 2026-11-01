# AVALIAÇÃO F9_FLUXO — ciclo 2 (contexto fresco, modo veredito)

> Bloco devolvido pelo avaliador em contexto fresco (subagente sem a conversa do build), numa worktree
> destacada no commit `524f957`. Guard antes do despacho: `sdd/reports/evidence/F9_FLUXO/guard-antes-do-avaliador-ciclo2.log`
> (VERDE). A sessão do avaliador caiu 2 vezes por erro de rede (ENOTFOUND) e foi retomada com o mesmo
> contexto. Sondas em `sdd/reports/evidence/F9_FLUXO/AVAL2-*.log` (31). Decisão sobre cada achado no Advisor
> Ledger do `BUILD_REPORT_F9_FLUXO.md`.

```text
<<<AVALIACAO
VEREDITO: NEEDS_WORK

Modo veredito · ciclo 2 · F9_FLUXO · worktree destacada em 524f957 · contrato DEFINE v1.5 / DESIGN v1.1.
Piso verde: suíte /bin/bash 3.2.57 + /usr/bin/python3 3.9 → 741 OK (AVAL2-suite.log); cmd inteiro do Verify
Gate → exit 0 (AVAL2-verify-gate-cmd.log); sdd-fluxo.sh --self-test 33 ✅ (AVAL2-self-test-fluxo.log);
sdd-decisoes-lint.sh --self-test VERDE; --sites 15 / 2 / 17; skill-lint --conversa 17/17; test_agnostico OK;
grep de bash 3.2 sem achado.

Achados do ciclo 1 → corrigido?
1 HIGH loop --log no 64: SIM (AVAL2-c1-01) — bordas novas N3/N4 · 2 MEDIUM Ledger sem coluna: SIM (AVAL2-c1-02) —
vizinho N2 · 3 MEDIUM retorno do 40: SIM (AVAL2-c1-03) · 4 LOW manifest cercado: SIM (AVAL2-c1-04; 8 DESIGNs
13/17/4/10/17/7/25/13) — mesma falha no Ledger, N5 · 5 LOW papel com LF: SIM em LC_ALL=C (AVAL2-c1-05) —
regressão em UTF-8, N1 · 6 LOW --log/pasta: SIM · 7 LOW contrato do seguir: SIM · 8 LOW brief: SIM · 9 LOW
sdd-design: SIM — resíduo N6 · 10 LOW recibo: SIM (7 inválidos → 30; 2 válidos → 0) · 11 LOW exit 30: SIM ·
12 LOW fora de git: SIM · 13 LOW concordância: SIM · 14 LOW SHA: PARCIAL (maiúsculas pegas; só dígitos e só
letras não; risco declarado) · 15 LOW classificação: SIM.
Sabotagem das correções (AVAL2-sabotagem-correcoes.log): 3/3 derrubam teste nomeado e restauram.

Tabela por AT: AT-001..AT-011, AT-013, AT-015..AT-029, AT-032, AT-033 PASS; AT-009/AT-010 PASS com LOW N3/N4;
AT-012 FAIL (N1); AT-014 FAIL parcial (N2); AT-030/AT-031 NAO_VERIFICADO (execução real fora daqui).

ACHADOS NOVOS
N1. HIGH (regressão do LOW 5) — sdd/bin/sdd-fluxo.sh:53 `case "$1" in ''|*[!A-Za-z0-9_-]*)`: no bash 3.2 com
locale UTF-8 a faixa segue a ordenação do locale e aceita É, ç, ã, ß, ñ; `despachar avaliação F9 b.md` sai 40 e
grava BRIEF_avaliação_F9.md (AT-011/AT-012 pedem 64). O bb91c42 (grep -Eq) recusava nos 3 locales; a suíte só
testa ASCII. Reprodução: LC_ALL=pt_BR.UTF-8 /bin/bash sdd/bin/sdd-fluxo.sh despachar avaliação F9 b.md → 40.
AVAL2-reg-despachar-nome-acentuado-locale.log.
N2. MEDIUM — sdd-fluxo.sh:608 `(sev or "").upper().startswith("HIGH")`: severidade não é limpa de `*`, crase ou
emoji; `**HIGH**`, `HIGH` entre crases ou `🔴 HIGH` com PENDENTE → ✅ e exit 0. AVAL2-reg-seguir-severidade-formatada.log.
N3. LOW — sdd-fluxo.sh:268-273, :316-318: só SystemExit é capturado; `--teto ²` passa no isdigit(), quebra no
int(), traceback exit 1 e o log antigo [exit=0] fica; --log que não grava sai 0 com aviso.
AVAL2-reg-loop-log-excecao.log, AVAL2-reg-loop-log-bordas.log.
N4. LOW — sdd-fluxo.sh:44-49, :710: sem python3, o precisa_python sai 64 antes de gravar o --log; o log antigo
PRONTO [exit=0] fica. AVAL2-reg-loop-log-sem-python3.log.
N5. LOW — sdd-fluxo.sh:513: ledger() lê um `## Advisor Ledger` de exemplo dentro de bloco cercado (a falha do
LOW 4, corrigida só no review-design); exemplo com HIGH APLICADA antes do real com PENDENTE → ✅ 0.
AVAL2-reg-seguir-ledger-em-bloco-cercado.log.
N6. LOW — .agents/skills/sdd-design/SKILL.md:77-78 cita "contrato de aceite … (modo `contrato`)", que só existe em
sdd-build/references/contexto-fresco.md:33; falta apontar onde.
>>>
```
