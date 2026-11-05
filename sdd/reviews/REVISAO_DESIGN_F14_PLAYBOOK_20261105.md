# REVISAO DESIGN: F14_PLAYBOOK

- **Data:** 2026-11-05 · **Modo:** contrato · **Lido:** DEFINE v1.2 e DESIGN v1.0
- **Quem revisou:** agente de contexto fresco; não viu a conversa do build
- **Veredito:** NEEDS_WORK — 5 propostas de aceite; 2 HIGH · 9 MEDIUM · 6 LOW
- **Logs:** `sdd/reports/evidence/F14_PLAYBOOK/AVAL-DESIGN-01` a `-26-*.log`
- **Como mediu:** a árvore mudou durante a revisão (o build rodava na mesma pasta), então as sondas de base rodaram numa cópia de `git archive HEAD` (= `v2.5.0`). Nada do projeto foi editado.

## Propostas de ajuste de aceite

| # | Alvo | Problema | Como verificar |
|---|---|---|---|
| P1 | AT-024, AT-006, AT-007 | saída 1 da colheita tem 3 regras diferentes; colheita só com `PROMOVER?`, `SUGESTAO` ou `REJEITADO` termina como "nada", e a pessoa não sabe que o candidato foi rejeitado; saídas 126 e 127 sem destino | decidir pelo `resumo:`; outro exit ou resumo ausente = FALHOU |
| P2 | AT-020, AT-021 | "AUTO que está na colheita" não exige igualdade: `+5` ou evidência em outra linha existente passam; `sugestao` com `AUTO` contraria o DEFINE; `mordeu` AUTO com `INV_PENDENTE` trava depois do `--aplicar` | 4 mutantes do bloco de exemplo; sabotagem trocando igualdade por "existe" |
| P3 | AT-023, AT-038(a) | "sai 40 com o brief no destino" já passa na `v2.5.0`; o texto de hoje diz "nada foi publicado" e "começa a ler o DEFINE" | conferir as frases novas e a ausência das 2 antigas |
| P4 | AT-026, AT-027 | pasta de destino ausente na frente; documento commitado no principal e não enviado sai `NADA A COPIAR`; nome com acento nunca casa | origin bare + commit local sem push; destino ausente; feature com acento |
| P5 | `cmd` do gate; Success Criteria | o gate roda sem git: `check-versions`, AT-037 e a existência dos testes novos ficam fora; o comando `-m unittest tests.…` dá `ModuleNotFoundError` até no controle; `SDD_TRACE=off` derruba 9 de 29 e `SDD_TRACE_DIR` herdado derruba 8 e vaza 7 arquivos | AT-030 com as 2 variáveis e a pasta que fica ausente |

Fora do limite de 5: AT-029 é circular (o lint aceita seção a mais; a fixture antiga já passa); AT-007, AT-016 e AT-021 dizem "última linha = resumo" e o AT-040 põe `RESULTADO:` depois; AT-002 não exclui as linhas das 2 tabelas de landmines.

## Achados do DESIGN

| # | Sev. | Onde | Problema | Correção sugerida |
|---|---|---|---|---|
| D1 | HIGH | `bin/sdd-open.sh:553`, `:636-648`; `sdd/playbook.md:17` | o `init` nunca sobrescreve o playbook do projeto, mas instalaria o `sdd/invariants.md` do pacote com `origem=LM-004`; playbook instalado antes da `v2.2.3` não tem a LM-004: a trava sai 2 na 1ª curadoria, sem a frase amigável; projeto cuja LM-004 é outra lição fica com a INV-001 presa a ela | instalar o registro do pacote só junto com o playbook; nos outros casos, o esqueleto |
| D2 | HIGH | DESIGN, Decision 6; DEFINE AT-003, AT-019, AT-021 | `sugestao` como `AUTO` contraria "só linha de contador que existe na colheita"; `mordeu+1` de sugestão não gera `INV_PENDENTE` e pode travar depois do `--aplicar` | P2; contagem com `INV_PENDENTE` vai na mesma opção da classificação |
| D3 | MEDIUM | DESIGN, 3 lugares | 3 regras para a saída 1 | P1 |
| D4 | MEDIUM | `sdd-release` 160-163; molde do handoff | as fontes acumulam entre releases da mesma feature; `--desde` só filtra DESIGN e BUILD_REPORT: um `WAIVED … LM-nnn` antigo é recontado como `mordeu+1` AUTO | definir a data; filtrar todas as fontes, ou só colher o que é da release corrente |
| D5 | MEDIUM | `governanca-fronteira.sh:20-21` | o staging fica fora do worktree e a fronteira não o vê: 1 linha a mais na evidência e na colheita do staging e o `--comparar` sai 0 | selar o staging antes do despacho e o conferidor reprovar se o selo mudou |
| D6 | MEDIUM | DESIGN, Decisions 5 e 8 | nenhum modo grava o `sdd/invariants.md`: quem edita é o agente, à mão; no conflito só o playbook tem reaplicação | modo que aplica as linhas `inv` e devolve o arquivo novo |
| D7 | MEDIUM | `sdd-release` 252-254 | o passo 15b move os artefatos para `sdd/archive/` antes do 17b; o `--preparar` sai 0 sem nada e a colheita vira "0 deltas" | procurar também no archive; sair diferente de 0 sem DESIGN nem BUILD_REPORT |
| D8 | MEDIUM | DESIGN, Decision 3 | a pasta de staging é a mesma em toda release e nunca é limpa; `RETOMADA:` sem instrução | `--preparar` apaga os derivados, salvo com `--retomar` |
| D9 | MEDIUM | `sdd-new-session` 232, 237-239 | "documento salvo no git já está na frente" é falso com commit não enviado; destino ausente e acento sem comportamento | P4 |
| D10 | MEDIUM | `sdd-decisoes-lint.sh`, `skill-lint.py`, `test_decisoes_lint.py:44-51` | "cada item com aceitar, recusar e não sei" não cabe no formato de 1 recomendada por pergunta; o `SKILL.md` da release não pode ganhar pergunta de decisão | fixar a forma no DESIGN e manter os exemplos só no `como-falar.md` |
| D11 | MEDIUM | `playbook-lint.sh:74`; `sdd/playbook.md:17` | o lint aceita bullet sem `promovido_para:`; com `mordeu=2` e sem o campo, a pergunta obrigatória nunca dispara; rabo do `ADD` e do `REFINE` e crase em volta do caminho sem definição | campo ausente conta como `—`; `REFINE` preserva o rabo; tirar a crase |
| D12 | LOW | `sdd-fluxo.sh:85-100`; `governanca-fronteira.sh:177` | "o que o agente lê" do curador cai no default "o DEFINE"; a seta da fronteira manda "regrave o DEFINE"; um `--colher` repetido pelo curador grava trace e vira `FORA` | variável por papel; o brief proíbe `--colher` |
| D13 | LOW | `sdd-fluxo.sh:63-71` | `--preparar` aceita ponto no nome e o `despachar` recusa | o mesmo alfabeto |
| D14 | LOW | Pattern 1 | o programa chega pelo stdin: `--cruzar -` precisa de contorno; o lint faz `cd` para a raiz | registrar; caminho absoluto ao lint |
| D15 | LOW | molde do BUILD_REPORT | barra vertical dentro da célula de delta sem escape definido | aceitar `\|` |
| D16 | LOW | `docs/hooks.md:29` + PT; manifest | os 2 documentos dizem "mais de 20%" sem o piso e não estão no manifest; dependências faltando nas linhas 38 e 42 | acrescentar |
| D17 | LOW | `verify-gate.sh:80-82`; `report-lint.py:376` | chaves e nome do arquivo do trace fora do contrato; o comando do 1º Success Criterion grava `sdd/traces/FIXTURE.jsonl` na árvore; glob de `AVALIACAO` pega feature de nome mais longo | fixar; `SDD_TRACE=off`; padrão com data |

<<<CONTRATO
veredito: NEEDS_WORK
propostas: 5
achados: 2 HIGH · 9 MEDIUM · 6 LOW
logs: AVAL-DESIGN-01 a AVAL-DESIGN-26 em sdd/reports/evidence/F14_PLAYBOOK/
>>>
