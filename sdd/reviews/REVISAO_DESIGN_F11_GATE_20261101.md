# REVISÃO DO DESIGN F11_GATE — contexto fresco (modo contrato, antes do build)

> Bloco devolvido pelo revisor em contexto fresco (subagente sem a conversa do design), sobre
> `DESIGN_F11_GATE.md` v1.0 e `DEFINE_F11_GATE.md` v1.0, com a branch em `248301d` (= `v2.3.0`).
> Logs das sondas em `sdd/reports/evidence/F11_GATE/AVAL-DESIGN-*.log` (6; `gate-shell-evidencia` VERDE).
> As decisões sobre cada nota estão no Advisor Ledger do DESIGN (v1.1); aplicadas no DEFINE v1.1.

```text
<<<CONTRATO
FEATURE: F11_GATE · modo: contrato · DEFINE 1.0 + DESIGN 1.0 · HEAD 248301d = v2.3.0
VEREDITO: NEEDS_WORK (2 HIGH · 3 MEDIUM · 7 LOW)

Medições (sdd/reports/evidence/F11_GATE/):
- AVAL-DESIGN-01-urllib-proxy.log [exit=0] — A-002 em /usr/bin/python3 3.9.6 darwin: no_proxy=127.0.0.1,localhost → servidor local 200; https://openrouter.ai → só 127.0.0.1:9 (ConnectionRefused); NO_PROXY=* maiúsculo não vence o no_proxy minúsculo; no_proxy=* minúsculo herdado e não sobrescrito → DNS direto; example.invalid falha COM proxy e SEM proxy (a sonda do DESIGN não discrimina).
- AVAL-DESIGN-02-bashenv-bypass.log [exit=0] — adversarial-review.sh real + CLIs falsas: A controle → stub chamado; B BASH_ENV põe a pasta da CLI "real" à frente → pré-voo vê o stub, mas a CLI REAL É CHAMADA e a revisão sai 0; C BASH_FUNC_claude%% → a função é chamada.
- AVAL-DESIGN-03-meta-discriminacao.log [exit=0] — adapters sabotados por SDD_REVIEW_ADAPTERS: codex sem tokens → custo `assinatura` e modelo `-` NÃO mudam (só tokens); gemini sem modelo/tokens → custo `$?` NÃO muda; claude sem total_cost_usd → `US$ 0.0239` vira `assinatura`.
- AVAL-DESIGN-04-openrouter-precos.log [exit=0] — openrouter real ponta a ponta sem usage.cost: tokens 16/136 → 0.32/1.28 e 0.40/1.60 dão ambos `≈US$ 0.0002`; tokens 1234567/234567 → 0.6953 vs 0.8691; servidor recebeu Bearer <CHAVE> e data_collection=deny; a chave em 0 arquivos das pastas.
- AVAL-DESIGN-05-sabotagem-exclusao.log [exit=0] — `--reviewer claude --auditor claude`: intacto 67 sem chamada; S1 (sem o 67 antecipado, :435) 67 e claude CHAMADO; S2 (sem a exclusão em papel(), :869) 67 sem chamada = idêntico ao intacto.
- AVAL-DESIGN-06-fila-openrouter.log [exit=0] — o servidor sobe 1 vez (:28, :102), mas fila e estado são ambiente por cenário (:31, :73, :324); Pattern 1 faz sys.exit(99) (:274–279).

AJUSTES
1. AT-011/AT-009 · Decision 2 pré-voo, Security · HIGH · isolamento furável — o pré-voo confere command -v no shell do gate, mas os adapters rodam em `bash -c` novo (adapter_cmd :595–597), que executa BASH_ENV e importa funções exportadas (log 02 B: CLI real chamada, exit 0). "a sentinela pega CLI real" é falso. · Ajuste: While the gate runs, it shall invoke adversarial-review.sh with BASH_ENV and ENV unset and no BASH_FUNC_* variable; If, in a child /bin/bash -c started with that exact environment, command -v claude|codex|gemini does not print a path under <tmp>/bin, then exit 3 naming engine and value, before any call; When each scenario ends, assert <engine>.n equals the expected call count. · Verificar: BASH_ENV com PATH=<real>:$PATH e BASH_FUNC_claude%% → gate 3, marca vazia.
2. AT-002/AT-007/AT-009 (openrouter) · Decision 1, Pattern 1, Data Flow · HIGH · lacuna — o servidor sobe uma vez e nunca vê SDD_STUB_OPENROUTER/SDD_STUB_ESTADO; "sai 99" não existe em HTTP. · Ajuste: canal que o servidor lê a cada requisição (arquivo de fila + estado ativo) ou um servidor por cenário; requisição sem fila → sentinela + HTTP 599 corpo `sentinela`. · Verificar: auditor openrouter com fila vazia → sentinela, ❌, exit 2; `429,auditor` → openrouter.n == 2.
3. AT-002 + "≥ 12 asserções de campo" · MEDIUM · aceite circular — custo de codex/gemini e modelo do codex não dependem da extração (log 03); critério do gemini "≈US$ ou $?" não determinístico; precos.tsv sem gemini. · Ajuste: só contam asserções cujo valor esperado difere do META com adapter_extrair todo nulo: claude custo US$ + modelo; codex tokens; gemini modelo + tokens; openrouter custo US$ + modelo via; AT-002 diz codex modelo `-` e gemini `$?`. · Verificar: cópia de cada adapter com extração nula → gate 2 nomeando asserção daquela engine.
4. AT-005 + sabotagem "exclusão" · MEDIUM · estado sem critério — o cenário 67 só protege o 67 antecipado (:435); sem a exclusão em papel() (:869) fica idêntico (log 05 S2). · Ajuste: If the reviewer falls back to an engine with the auditor's identity (`--reviewer gemini,codex --auditor codex`, gemini `cota`), then assert auditor_exit 67, auditor_motivo contém `excluída`, reviewer_engine_efetivo codex, codex.n == 1. · Verificar: sabotar :869 → exit 2 nomeando; sabotar :435 → ❌ em "0 chamadas".
5. AT-002 (sem-custo)/AT-019 · Decision 2 · MEDIUM · acoplamento e aceite cego — ≈US$ depende de precos.tsv/registry resolvidos em BIN/../review, editáveis no projeto; meta_custo fixo quebra numa atualização legítima de preço; com 16/136 tokens duas tarifas dão o mesmo valor. · Ajuste: When asserting ≈US$, compute the expected value from the precos.tsv and registry.tsv that adversarial-review.sh resolves and from the stub tokens; stub reports ≥ 10^6 input and ≥ 10^5 output. · Verificar: preço trocado → gate 0; sabotar #17a → gate 2.

NOTAS MENORES (LOW)
1. Risks: a sonda example.invalid passa com proxy ignorado; conferir ConnectionRefusedError de 127.0.0.1:9. A-002 medida válida (vira "yes"); sobrescrever o no_proxy minúsculo.
2. AT-006/007/008: textos de falha dos stubs não medidos; citar fonte ou marcar sintético; cota real do gemini costuma vir com 429 (classe testa transitório antes) — caminho não exercitado.
3. AT-010: asserir que o servidor recebeu Authorization: Bearer <chave gerada>.
4. AT-014/Decision 3: tirar ` via <provedor>` da chave do auditor.
5. AT-017: verificar por proxies mortos + PATH sem CLIs + grep que proíba urllib, socket e adapters/ no eval-agree.sh.
6. AT-002: redação do codex "reports model" contradiz o Success Criteria; "or" do gemini vira valor único (coberto pelo ajuste 3).
7. Error Handling: teto de 120 s por execução × ~12 pode passar da A-003; definir o estouro total.
>>>
```
