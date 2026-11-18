# AVALIAÇÃO F9_FLUXO — ciclo 1 (contexto fresco, modo veredito)

> Bloco devolvido pelo avaliador em contexto fresco (subagente sem a conversa do build), numa worktree
> destacada no commit `bb91c42`. Guard antes do despacho: `sdd/reports/evidence/F9_FLUXO/guard-antes-do-avaliador.log`
> (VERDE). Sondas em `sdd/reports/evidence/F9_FLUXO/AVAL-*.log` (27). Decisão sobre cada achado no Advisor
> Ledger do `BUILD_REPORT_F9_FLUXO.md`.

```text
<<<AVALIACAO
VEREDITO: NEEDS_WORK

Modo veredito · ciclo 1 · F9_FLUXO · worktree destacada em bb91c42 · contrato DEFINE v1.3 / DESIGN v1.1.
Piso verde: suíte da worktree 735 OK (AVAL-suite.log); cmd do Verify Gate inteiro (git archive + publish-gate ci
G1–G5 + 735 testes na cópia sem .git) exit 0 (AVAL-verify-gate-cmd.log).

| AT | sonda | esperado | observado | resultado |
|---|---|---|---|---|
| AT-001 | review-design nas 7 fixtures e nos 8 DESIGNs F1–F8 | EXIGIDO 13/17/4/10/17/7/25/13; novos/numerado 3 | os 8 iguais; novos/numerado/pronto 3 e exit 0 | PASS |
| AT-002 | login, glob de security_globs com espaços, layers.sql | EXIGIDO nomeando o sinal | termo login, glob api/public/**, glob db/migrations/** | PASS |
| AT-003 | DESIGN_dispensavel | DISPENSAVEL: 2 …, exit 1 | idem | PASS |
| AT-004 | sem manifest, sem linha, pasta, binário, ausente | 64 + RESULTADO + → | 64 MANIFEST ILEGÍVEL | PASS |
| AT-005 | review-ok + ledger-rebatida + AVALIACAO_pass | PRONTO, 4 contadores, exit 0 | idem | PASS |
| AT-006 | aplicada, sem ledger, inválida, NEEDS_WORK c1, outra rodada, MED, HIGH+recibo pendente | 10 | 10 em todos | PASS |
| AT-007 | rodada 3 HIGH aberto, NEEDS_WORK c2, impasse, NEEDS_WORK c1 na rodada 3 | 20/20/20/10 | 20 D4 teto, 20 D4 ciclos, 20 D5, 10 | PASS |
| AT-008 | PASS_PENDENTE_RECIBO sem/com --recibo | 30; PRONTO com motivo do recibo | idem | PASS (LOW 10) |
| AT-009 | META ausente, 6 jsonl inválidos, ledger ausente, avaliação ambígua/vazia, args ruins; bordas A/B/C | 64 nunca 0; A/B/C 10 | 64 em todos; 10/10/10 | PASS |
| AT-010 | --log com 0/20, tee no self-test, --log numa 2ª chamada que sai 64 | [exit=N] real em toda chamada | certo para 0/10/20/30; no 64 o log não é regravado e fica PRONTO [exit=0] antigo, aceito pelo gate-shell-evidencia | FAIL (HIGH 1) |
| AT-011 | despachar sem git, com espaço, brief no destino relativo/absoluto, 2 papéis | 40, cópia idêntica, destino intacto, 6 rótulos, retorno por papel | idem, mtime preservado | PASS (MEDIUM 3) |
| AT-012 | 2 e 4 args, ava/x, F.9, brief vazio/ausente/pasta | 64 e nada gravado | idem | PASS (LOW 5) |
| AT-013 | 7 pares, caminho com espaço, cwd em subpasta | ✅ com concordância, ≤100, → /sdd-…, 0 | idem, máx. 88 caracteres | PASS |
| AT-014 | desligado, --parar, Draft, sem kind, marcador, ledger vazio, release de build e de define | PARAR + motivo + →, 1 | idem | PASS (MEDIUM 2) |
| AT-015 | sim, define→build, release→release, DEFINE ausente, arg faltando | 64 com ⚠️ e → | idem | PASS |
| AT-016 | sem python3 em todos os verbos; sem arg; verbo desconhecido | 64 | idem | PASS |
| AT-017 | --self-test em cópia sem .git, caminho com espaço | ✅ por cenário, 0 | 33 ✅, VERDE | PASS |
| AT-018 | --sites skills, fragments, juntos | 15 e 2 | 15 em 15, 2 em 2, 17 juntos | PASS |
| AT-019 | 25 casos, um por regra | 1 🛑 por motivo, redação do skill-lint, 2 | idem | PASS (LOW 14) |
| AT-020 | caminho inexistente, docs sem pergunta, --sites vazio | 64 | 64 | PASS |
| AT-021 | --self-test do lint | 4 reprovadas + controle 0 | VERDE | PASS |
| AT-022 | item 9 | 6 marcas, [Dn], estado, exceção do OK, exemplos marcados | presente | PASS (LOW 8) |
| AT-023 | FLUXO_ENCADEADO + test_agnostico | contrato completo | presente | PASS (LOW 6, 7) |
| AT-024 | subseção nas 9 | bloco idêntico, depois do Próximo passo, 1 linha | 1 hash para as 9 | PASS |
| AT-025 | config.example + parser (16 variações) | 2 slots com comentário | presentes | PASS |
| AT-026 | despachar no 5d, degrau 2, revisão do DESIGN | comando + parar no 40 | presente nos 3 | PASS |
| AT-027 | F6, F8, F10, F11 | frases-chave | presentes | PASS (LOW 9) |
| AT-028 | passo no publish-gate.yml + check-versions | 3 comandos; 9 minor, 6 patch | linhas 111-115; VERDE; conferido 1 a 1 | PASS |
| AT-029 | suíte, gate, skill-lint, playbook-lint | verde | 735 OK, G1–G5, 17 ✅, 🟢 | PASS |
| AT-030 | execução real do Codex | — | não rodado (brief) | NAO_VERIFICADO |
| AT-031 | execução real do Codex | — | não rodado (brief) | NAO_VERIFICADO |
| AT-032 | 5 sabotagens numa cópia; testes novos na v2.2.9 | cada uma derruba teste nomeado; vermelho na base | 5/5; base 69F+14E e 24F+1E | PASS |
| AT-033 | estado com 8 variações | 0,1,1,1,1,64,64,64 | idem | PASS |

ACHADOS
1. HIGH — `loop --log` não grava no exit 64 e o log antigo fica como prova falsa (sdd/bin/sdd-fluxo.sh:254-258 sai64, :425-437 log só no sucesso). 2ª chamada com entrada quebrada sai 64 e o arquivo continua PRONTO [exit=0], aceito pelo gate-shell-evidencia. Reprodução: loop … --log "$T/L.log" (0), depois loop --review "$T/nao" … --log "$T/L.log" (64), cat "$T/L.log" → PRONTO [exit=0]. AVAL-loop-log-obsoleto-no-64.log.
2. MEDIUM — `seguir design` segue com HIGH aberto quando o Advisor Ledger não tem coluna de severidade reconhecida (sdd-fluxo.sh:475, :549): cabeçalho `| # | Note | Sev | Verdict |` ou formato F5/F6 → severidade vazia → ✅ e exit 0. Deve falhar fechado. AVAL-seguir-ledger-sem-coluna-severidade.log.
3. MEDIUM — o retorno do exit 40 pede só a linha `VEREDITO: …`, mas a build grava o bloco <<<AVALIACAO … >>> verbatim e usa os ACHADOS como brief do ciclo 2 (sdd-fluxo.sh:73-74, sdd-build/SKILL.md:180-187, contexto-fresco.md:26 × :71/:74). Para o avaliador, pedir o bloco inteiro (mexe no AT-011/U5). AVAL-texto-retorno-do-40.log.
4. LOW — review-design lê um `## File Manifest` de exemplo dentro de bloco cercado (sdd-fluxo.sh:180): exemplo cercado antes do real → DISPENSAVEL 0, exit 1, com o real tendo 3 Create. AVAL-review-design-manifest-em-bloco-cercado.log.
5. LOW — despachar aceita papel com quebra de linha (sdd-fluxo.sh:53, grep linha a linha): sai 40 e cria BRIEF_ava<LF>x_F9.md. AVAL-despachar-papel-com-quebra-de-linha.log.
6. LOW — FLUXO_ENCADEADO.md:84 sugere `--log evidence/<F>/LOOP-rodada-N.log`; a pasta é sdd/reports/evidence/<F>/; pasta ausente → só aviso no stderr, sem log. AVAL-loop-log-pasta-ausente.log.
7. LOW — o contrato do `seguir` no fragmento (FLUXO_ENCADEADO.md:32-33) omite Status Ready for, gate sem kind/cmd e Advisor Ledger.
8. LOW — PERGUNTA_DECISAO.md:95 traz `**Brief:** sdd/reports/evidence/PAGAMENTOS/AVAL-brief.md`, contra o lugar fixo sdd/reports/briefs/BRIEF_<papel>_<F>.md. AVAL-texto-fragmentos.log.
9. LOW — sdd-design/SKILL.md:72-79 cita "a proposta de verificabilidade do avaliador", que não existe na skill; com o encadeamento desligado a pergunta do flag não diz que leva [auto · de rotina].
10. LOW — --recibo (sdd-fluxo.sh:390): "2026-10-31" sozinho sai 30; "Ana 2026-99-99" é aceito.
11. LOW — contexto-fresco.md:72 diz "sem recibo, tratar como NEEDS_WORK", contra o exit 30 AGUARDANDO_RECIBO.
12. LOW — fora de git, `estado` diz ligado e `seguir` para com "o Verify Gate do DEFINE não está válido (… saiu 64)" (sdd-fluxo.sh:526-529); o que falta é o git.
13. LOW — concordância nos motivos (sdd-fluxo.sh:523-525): "UX REVIEW não encontrado", "GOVERNANÇA não está pronto".
14. LOW — sdd-decisoes-lint.sh:81 não pega SHA em maiúsculas (7C640EB) nem só dígitos (1234567); `**Sua decisão:**` foge do lint (risco já declarado no DESIGN).
15. LOW — classificação trocada entre DESIGN e código: o DESIGN (manifest, linhas 55 e 58) marca sdd-design como auto e sdd-iterate como D2; o implementado é o inverso.
>>>
```
