# Avaliação em contexto fresco — quem julga não é quem constrói

## Por que existe

Um build que lê o próprio diff e "vê o handler" conclui que o botão funciona. Ninguém clicou.
Features foram publicadas com "Enviar não faz nada" exatamente assim. O avaliador nasce **sem
a conversa do build**, lê o DEFINE como contrato e **prova cada critério executando**: comando,
chamada HTTP, clique. Nunca lendo o diff.

Duas landmines que este papel neutraliza:
- **Asserção de fiação ≠ comportamento** — o `grep` acha a chamada, mas a condição pode ser
  sempre-verdadeira.
- **Régua validada contra o par que a construiu é circular** — por isso o brief abaixo é
  **tudo** o que o avaliador recebe.

## Como despachar (qualquer agente)

O valor está no contexto limpo, não na API de subagente. Use o que o seu vendor tiver, nesta
ordem de preferência:

1. **Subagente em contexto limpo** (Claude Code, Codex, Kimi Code, Grok Build e outros que
   suportam agentes): despache com o brief abaixo como prompt inteiro.
2. **Sessão nova** do mesmo agente: grave o brief em `sdd/reports/briefs/BRIEF_avaliador_{F}.md`
   e abra uma sessão nova que só lê esse arquivo.
3. **Outro vendor** em sessão nova: idem, e ganha diversidade de erro.

⛔ O brief **não** leva BUILD_REPORT, diff, resumo do que foi feito, nem hipóteses do build.
Se vier, o avaliador registra `CONTAMINAÇÃO` e o veredito perde valor.

## Brief — modo `contrato` (antes de codar, ≥2 camadas)

```text
modo: contrato · FEATURE: {F} · DEFINE: sdd/features/DEFINE_{F}.md ·
DESIGN: sdd/features/DESIGN_{F}.md · projeto: {caminho absoluto}

Você não viu a conversa do build. Leia o DEFINE (## Acceptance Tests e ## Verify Gate) e o
DESIGN. Para cada AT, pergunte: é verificável por execução? o estado que quebra tem critério?
o cmd do gate cobre este AT? o aceite é circular (prova a fiação, não o comportamento)? o
efeito é observável? Proponha ≤5 ajustes, cada um com: alvo · classe · problema · redação em
EARS · como verificar (comando/sonda). Rode as sondas read-only que puder AGORA (git diff,
grep, execução das fixtures) e cite o que mediu. Não escreva em arquivo algum. Devolva o bloco
<<<CONTRATO … >>>.
```

## Brief — modo `veredito` (depois do build)

```text
modo: veredito · ciclo: {1|2} · FEATURE: {F} · DEFINE: sdd/features/DEFINE_{F}.md ·
DESIGN: sdd/features/DESIGN_{F}.md · projeto: {caminho absoluto} · URL base: {se houver} ·
credenciais: {"autorizadas pelo humano nesta sessão" | "não autorizadas"}

Você não viu a conversa do build. Leia o DEFINE como contrato. Para cada AT, PROVE por
execução (comando, chamada, clique) — nunca lendo diff. Superfície visual: derive um roteiro
clicável dos ATs e do manual_fallback e execute-o; sem browser/sessão, devolva o roteiro em
NAO_VERIFICADO, nunca PASS. Só leitura em produção (GET, consultas SELECT, rotas idempotentes);
nada que grave ou envie. Devolva <<<AVALIACAO … >>> com: veredito PASS | NEEDS_WORK |
PASS_PENDENTE_RECIBO, tabela por AT (sonda · esperado · observado · resultado) e ACHADOS
(cada um com reprodução exata). Não escreva em arquivo algum.
```

## O que o build faz com o veredito

| Veredito | Ação |
|---|---|
| `PASS` | seguir; os ATs provados citam `sdd/reviews/AVALIACAO_{F}_{ts}.md` como evidência |
| `NEEDS_WORK` | os ACHADOS são o brief de correção do ciclo seguinte (redispatch fresco); corrigir, rodar o gate, re-despachar com `ciclo: 2`. Máximo 2 ciclos → `Status: Blocked` com os achados abertos. Nunca contornar o critério |
| `PASS_PENDENTE_RECIBO` | só em gate manual-ux: mostrar o roteiro ao humano e colher `recibo: nome YYYY-MM-DD`; sem recibo, tratar como NEEDS_WORK |

Persista o bloco verbatim em `sdd/reviews/AVALIACAO_{F}_{YYYYMMDD-HHMM}.md` — é a evidência
que o `report-lint.py` exige para o veredito no BUILD_REPORT. Registre a contagem de achados:
zero achados em três features seguidas é sinal de calibração, não de perfeição.
