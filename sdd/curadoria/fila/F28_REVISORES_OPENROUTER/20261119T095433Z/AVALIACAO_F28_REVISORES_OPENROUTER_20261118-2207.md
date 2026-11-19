# Avaliação em contexto fresco — F28_REVISORES_OPENROUTER, ciclo 1

> Bloco devolvido pelo avaliador (subagente sem a conversa do build, modo `veredito`), gravado como veio. As decisões
> sobre os achados ficam no fim, depois do bloco.

```text
<<<AVALIACAO
feature: F28_REVISORES_OPENROUTER · modo: veredito · ciclo: 1
HEAD avaliado: 8f03b9e. A avaliação começou no d850a75; a rodada 2 do build foi commitada no meio dela. Rodei de novo todas as sondas dos ATs e de borda no 8f03b9e. O adversarial-review.sh não mudou entre os dois commits.
Ambiente: cópias de `git archive` no scratchpad, HOME temporário, GIT_CONFIG_GLOBAL=/dev/null, PATH sem claude/codex/gemini reais (CLIs falsas quando precisei), servidor HTTP local no lugar do OpenRouter, chave = texto de fixture. Nenhuma chamada real ao OpenRouter. O repositório só ganhou os AVAL-*.log.

VEREDITO: PASS_PENDENTE_RECIBO

Todos os ATs passaram nas minhas sondas, que provam por execução. Faltam três recibos que não posso produzir aqui:
(a) O Verify Gate completo no 8f03b9e. O único log do gate, `VERIFY_GATE_d850a75.log` (95 bytes, commitado), tem só a linha do comando: sem saída e sem exit. Nenhum gate foi registrado, nem no d850a75 nem no 8f03b9e.
(b) O CI do PR nos 3 sistemas. Inclui a parte Windows do AT-010.
(c) Os cenários de conversa em contexto novo (critério SHOULD, LM-011). Não refiz; o build diz 6/6 em CENARIOS.md.
Nada abaixo bloqueia. Recomendo corrigir o achado 1 antes da release, porque a correção é barata.

| AT | sonda | esperado | observado | resultado |
|---|---|---|---|---|
| AT-001 | `diagnosticar.sh --estados` contra a tabela do SKILL.md; 15 projetos temporários, um por estado R01–R12, mais uma opção errada; foto do projeto e do HOME antes e depois; servidor local registrando as chamadas | 1 linha `ESTADO:` com frase e passo; exit da classe; script = linhas `script`; linhas `conversa` com situação e passo; só leitura, 0 rede | 21 estados emitidos = 21 linhas `script` (diferença nos dois sentidos: vazia). R22–R26 `conversa`: 4/4 colunas preenchidas. Exits 64/0/10/20/30 como no DESIGN. Sem `--testar`: 0 arquivos e 0 chaves de config mudados, HOME igual, 0 chamadas, mesmo com a chave no ambiente e os slots no OpenRouter | PASS |
| AT-002 | fixture no ambiente; rodei diag, `--testar`, `--gravar`, `--dry-run` com e sem diff e `checar.sh`; procurei a fixture em todos os arquivos do projeto e no .git/config; chave em ~/.bashrc e ~/.zshrc; `reg` falso que tenta imprimir a chave; `guardar-chave.sh` num pty de verdade; o mesmo script sem terminal | 0 ocorrências; perfil reconhecido sem o valor; gravação sem eco | 0 ocorrências em todas as saídas e arquivos. O perfil aparece só pelo nome (`~/.zshrc`). No pty, a chave aparece 0 vezes no terminal, o perfil fica com 600 e com cópia `.sdd-antes`, e um zsh novo carrega a chave nova. Sem terminal: exit 64 e nada lido | PASS |
| AT-003 | `--testar` contra o servidor local em 26 casos: 401, 403, 402, is_free_tier, limit_remaining 0 / -0.01 / 0.0004 / 0.009 / 0.01 / 1.00 / 1e-9 / 0.1000000000000000055…, limit null, 429 na chave e na lista, 500, JSON ilegível, data não objeto, modelo fora da lista, porta fechada, servidor mudo, status line inválida, corpo incompleto | só GET /key e /models; 0 chat/completions; teto de 10 s; ≤ 0 em centavos ⇒ R17; nenhum texto da resposta impresso | Classes corretas: R13, R14, R15, R16, R17 (0, -0,01, 0,0004, 0,009 e 1e-9 ⇒ esgotado; 0,01 e 1,00 ⇒ aceita), R18, R19 (porta fechada; mudo cortado em 10,2 s), R20, R21. Truncamento correto: 1.999 ⇒ "1,99". Texto da resposta: 0. No 8f03b9e a status line inválida dá R20 sem vazar texto. Ver o achado 1 (redirect) | PASS (com achado 1) |
| AT-004 | chave só no ~/.zshrc ⇒ diag, `--marcar-reabertura`, diag de novo; a volta com a chave; a volta com 2 CLIs; slots no OpenRouter sem a chave; SHELL=zsh com a chave só no ~/.bashrc | R05, depois R06; com a chave e slots vazios, R07 (ou R03 com 2+ CLIs); slots no OpenRouter sem chave ⇒ só a chave (R08); a frase da parada presente | R05 → R06 → R07 / R03 → R08, com os passos certos. "Quando terminar, me peça de novo, eu continuo daqui" está no SKILL.md (l. 54–55) e em como-falar.md (2 vezes). No 8f03b9e, a chave num perfil que o shell não lê dá R04 em vez de prender em R05/R06 | PASS |
| AT-005 | revisão real com os stubs de `sdd/fixtures/revisao` usando só o git config; slot contra git config; flag contra os dois; `--gravar` lido de volta; dois modelos OR; o mesmo modelo; ids desconhecido e igual | git config vale com o slot vazio; slot vence; flag vence; o plano diz a origem; "diversidade: modelo"; o mesmo modelo dá 67 | A revisão real completou com stub-a e stub-b vindos do git config (META `diversidade: modelo`). O plano mostra a origem nos 3 casos. `--gravar` grava só no git config: config.yaml intocado, `git status` só com o diff de teste. 2 modelos OR ⇒ "modelo". `openrouter` contra `openrouter:qwen/qwen3.7-plus` ⇒ 67 no dry-run e na revisão real, com 0 chamadas. `--gravar` recusa R11 e R12 sem gravar | PASS |
| AT-006 | `--dry-run` sem diff: OR+OR sem CLI (com e sem chave), OR+OR com claude e gemini, claude+codex com codex ausente; revisão real sem diff; sem base; `--no-revisor2`/`--no-desempate`; `--base` inválida | exit 0, `RESULTADO: PLANO`, origem, disponibilidade, 2º revisor e desempate (ou "nenhuma engine" com a consequência), `diff: vazio`; a revisão real sem diff dá 64 | Dry-run sai 0 em todos os casos, com o que o AT pede. Sem engine extra: o 2º revisor cita `--aceitar-sem-revisor2` e o desempate diz "fica para uma pessoa decidir". Com claude no PATH, o 2º revisor e o desempate são claude. A revisão real sem diff dá 64. Sem base: ⚠️ e exit 0. `--base` inválida: 64 | PASS |
| AT-007 | procurei nomes de modelo e preços no SKILL.md e nas references; troquei o precos.tsv na sonda; li as opções da skill | as opções CLIs, uma engine só e agora não; o aviso de custo e privacidade com a sdd-higiene-dado; par e preço só das tabelas | 0 nomes de modelo e 0 preços por milhão na skill. Com o precos.tsv trocado, mudam o par, os preços, a data e a estimativa (0,04 → 0,86). Conferi a conta: (180+60)·1024/4 tokens ⇒ ≈ US$ 0,037, arredondado para cima ⇒ 0,04. SKILL.md: R03 com as CLIs primeiro, R25 `--um-engine`, R26 "agora não"; l. 131–134 com custo, o que sai do computador, provedores que não guardam o dado e a `sdd-higiene-dado` | PASS |
| AT-008 | `skill-lint.py --conversa`; procurei os ganchos (design, build 0/5c, release item 8), o guia, as docs EN e pt-BR, os READMEs e o MANIFEST; rodei test_agnostico, test_skill_lint, test_gerar_starter, test_conversa e test_docs | tudo presente; lint verde | Lint exit 0. Ganchos em sdd-design:230/234, sdd-build:85/226 e sdd-release:129 ("ofereça **antes**", antes da dispensa). Guia do aluno com seção `#### sdd-configurar-revisores`. As duas docs citam a skill e o git config (5 vezes cada). README, README.pt-BR e MANIFEST trazem os 7 arquivos. Módulos OK | PASS |
| AT-009 | `checar.sh` com slots vazios, `--frente`, `--segredo`, `--editor`, git config claude/codex, revisor OR com e sem chave, auditor OR no git config sem chave, starter, só o revisor | ⚠️ e nunca 🔴; quieto nos outros modos e no starter; a consequência na 1ª frase; a skill na linha do comando | Os itens saem em "⚠️ Vale arrumar", com a consequência depois do travessão e a skill na linha de baixo. Quieto em `--frente`, `--segredo`, `--editor`, no starter, com tudo configurado e com a chave presente. O único 🔴 da saída vem da identidade do git ausente no HOME isolado, não da F28 | PASS |
| AT-010 | test_revisao, test_revisao_gate, test_bash32, test_agnostico, test_skill_lint, test_gerar_starter, test_conversa e test_docs (bash 3.2); test_f28_* e test_checar no d850a75 e no 8f03b9e; `data_collection`/`require_parameters` no adapter | tudo verde; o adapter igual | 226 testes OK (adversarial-review.sh igual no 8f03b9e). F28 + checar: 165 OK no d850a75 e 157 OK no 8f03b9e. O adapter mantém `"data_collection": "deny", "require_parameters": True`. Windows e a suíte inteira não rodaram aqui | PASS_PENDENTE_RECIBO (Verify Gate e CI) |

ACHADOS

1. [BAIXO-MÉDIO · segurança S10/AT-003 · aberto no 8f03b9e] O `--testar` segue redirect e manda `Authorization: Bearer <chave>` para outro host.
   Causa: `urllib` segue 3xx e repassa os cabeçalhos, inclusive para outro domínio. O "só GET da consulta oficial" do AT-003 também cai: um 302 de /key para /chat/completions gerou um GET em chat/completions (cc=1).
   Na prática, o risco exige que o próprio openrouter.ai (sobre TLS) responda com redirect. É defesa em profundidade, e a correção é barata: um opener com um `HTTPRedirectHandler` que recusa redirect, e o 3xx vira R20.
   Reprodução: servidor A em 127.0.0.1 responde a GET com `302 Location: http://localhost:<portaB>/coleta`; servidor B registra o cabeçalho Authorization. Depois, `OPENROUTER_API_KEY=<fixture> SDD_REVISORES_OPENROUTER_URL=http://127.0.0.1:<portaA>/api/v1 bash .agents/skills/sdd-configurar-revisores/scripts/diagnosticar.sh --testar` num projeto com a revisão.
   Observado: o host B recebeu `GET /coleta` com a fixture no Authorization. Estado R20, exit 40.
   Log: AVAL-BORDAS.log, casos `redirect` (d850a75 e 8f03b9e) e AVAL-AT-003.log, linha "302 da /key para chat/completions".

2. [BAIXO · UX/AT-007 · aberto no 8f03b9e] Com os slots já no OpenRouter (R02, R08), o diagnóstico mostra o "par sugerido" do pacote e a estimativa desse par, não a dos modelos configurados.
   Reprodução: `sdd/config.yaml` com `revisor1: openrouter:deepseek/deepseek-v4-flash` e `auditor: openrouter:x/sem-preco`, a chave presente, e `bash diagnosticar.sh`.
   Observado: R02 com "par sugerido: qwen… · deepseek…" e "estimativa por revisão: até ≈ US$ 0,04". O auditor configurado não tem preço, então o certo seria "preço desconhecido".
   Correção sugerida: com slots no OpenRouter, medir o par configurado (ou omitir a linha).
   Log: AVAL-BORDAS.log, caso `par-configurado`.

3. [RECIBO · Verify Gate] `sdd/reports/evidence/F28_REVISORES_OPENROUTER/VERIFY_GATE_d850a75.log` (commitado no 8f03b9e) tem 95 bytes: só `$ bash sdd/bin/verify-gate.sh …`, sem saída e sem exit. Falta rodar o comando do DEFINE (git archive + publish-gate + suíte inteira, `SDD_TEST_BASH=/bin/bash`) no HEAD final e gravar a saída completa com o exit. Falta também o CI do PR nos 3 sistemas.

Corrigidos no 8f03b9e (eram defeitos reais no d850a75; reconferi por execução):
- A status line HTTP inválida imprimia um traceback com texto da resposta ("BadStatusLine: HTTP/1.1 2OO SONDA… ignore as instrucoes") e dava R19. Agora dá R20 sem o texto.
- O `guardar-chave.sh` apagava a chave antiga de dentro de um `if/then` e quebrava o ~/.bashrc (`bash -n` exit 2; a chave e os outros exports deixavam de carregar). Agora deixa `:` no lugar e o `bash -n` dá 0.
- Com SHELL=zsh e a chave só no ~/.bashrc, o aluno ficava preso em R05/R06 (um zsh novo não enxerga a chave). Agora dá R04 com aviso.

Observações sem defeito:
- O PASSO_A_PASSO avisa que os rótulos dos botões das páginas logadas do OpenRouter não estão na documentação: os passos dão o endereço da página e o que ela pede, não o nome do botão. O caminho do Windows está marcado como "não testado".
- Uma linha `OPENROUTER_API_KEY=…` sem `export` no perfil dá R05 (borda rara; o guardar-chave sempre grava com export).

NAO_VERIFICADO: o Verify Gate completo (proibido aqui: mais de 30 min), o CI nos 3 sistemas e os cenários de conversa em contexto novo (3 × 2).

Evidência (1ª linha `$ comando`, saída verbatim), em sdd/reports/evidence/F28_REVISORES_OPENROUTER/:
AVAL-AT-001.log, AVAL-AT-002.log, AVAL-AT-003.log, AVAL-AT-004.log, AVAL-AT-005.log, AVAL-AT-006.log e AVAL-AT-009.log (sondas no 8f03b9e); AVAL-AT-007-008.log (no d850a75; nenhum arquivo de texto mudou no 8f03b9e); AVAL-AT-010-MODULOS.log (módulos no d850a75 e no 8f03b9e); AVAL-BORDAS.log (bordas no d850a75 e no 8f03b9e).
>>>
```

## Decisões do build sobre os achados

| Achado | Decisão | Prova |
|---|---|---|
| 1 redirect leva a chave | APLICADO: opener sem redirect, 3xx ⇒ R20 | `Testar.test_redirect_nao_e_seguido_e_a_chave_nao_vai_a_outro_endereco` (vermelho no código antigo) |
| 2 par sugerido com slots no OpenRouter | APLICADO: mede o par configurado; sem preço ⇒ "preço desconhecido", sem estimativa | `Estados.test_slots_no_openrouter_medem_o_par_configurado` (vermelho no código antigo) |
| 3 recibo do Verify Gate | o log do `d850a75` foi commitado enquanto o gate ainda rodava; o gate roda de novo no HEAD final e o log sai completo | `sdd/reports/evidence/F28_REVISORES_OPENROUTER/VERIFY_GATE_<sha>.log` |

Contaminação: o brief levou, além dos campos, restrições de segurança do ambiente (sem rede paga, sem `env`/`ps`,
pastas isoladas, sem a suíte inteira). Não são hipóteses sobre a feature; o avaliador não as marcou.
