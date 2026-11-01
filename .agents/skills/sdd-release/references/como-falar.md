# Como falar com o aluno — sdd-release

Quem chega à Release vai autorizar algo que não se desfaz: depois do push, a versão está publicada. A
seção "Como falar com o aluno" do `SKILL.md` dá o formato, e o item 7 da FASE 1 dá o bloco do OK; este
arquivo dá as palavras e um exemplo inteiro.

## Glossário (explique na primeira vez em que o termo aparecer)

- release — "a fase em que o que foi construído é publicado, com um único OK seu";
- push — "o envio das versões salvas para o GitHub; aqui, é o que publica";
- deploy — "a instalação da versão nova no lugar onde as pessoas usam o sistema";
- workflow — "a lista de passos que o GitHub roda sozinho quando recebe um push";
- Verify Gate — "a conferência final combinada no DEFINE: um comando que diz passou ou não passou";
- landmine — "uma armadilha conhecida do projeto, registrada no playbook com um número";
- drift — "uma mudança que chegou em produção sem estar salva no histórico";
- veredito — "o resumo das conferências: PASS (tudo certo), CONCERNS (passou com ressalvas) ou FAIL";
- waiver — "a sua decisão registrada de publicar mesmo com um achado, com o motivo";
- ledger — "o registro, gravado junto com a versão, do que foi publicado e quando";
- migration — "um arquivo que muda a estrutura do banco de dados".

Não fale em merge, fast-forward, tag ou `--stat` sem traduzir: "juntar na linha principal", "sem
reescrever nada", "o nome da versão", "a lista dos arquivos que mudaram".

## Status desta skill, preenchido

`Release: ✅ 1 Onde estou · ✅ 2 Verificar · ▶️ 3 Sua decisão · ⬜ 4 Publicar`

## Exemplo — resposta completa, com decisão (etapa 3 — Sua decisão)

Situação: a conferência de notas está pronta; todas as conferências passaram e o workflow do projeto só
publica depois que os testes passam.

**Status** — `Release: ✅ 1 Onde estou · ✅ 2 Verificar · ▶️ 3 Sua decisão · ⬜ 4 Publicar`
(no Status: "Verificar" são as conferências antes de publicar; "Publicar" é o envio e a instalação.)

**O que foi feito** — Juntei as 4 versões salvas desta tarefa numa só e conferi: a conferência final, o
relatório, o lint e o playbook passaram. Nada foi enviado ao GitHub ainda.

**Agora: etapa 3 — Sua decisão** — Os campos abaixo já foram conferidos por mim; você só responde à
última linha. **sim** publica exatamente o descrito; **não** encerra sem publicar.

**O que sobe:** 5 arquivos — 3 novos (`conferir.py`, `exemplo.xml`, `tests/test_conferir.py`) e 2 alterados
(`README.md`, `sdd/playbook.md`).
**O que muda em produção:** a planilha de pagamentos passa a vir marcada com as notas recebidas.
**O push publica sozinho?** sim, o workflow `deploy.yml` publica ao receber o push na `main`.
**O deploy espera os testes?** sim — o job que publica só roda depois do job de testes.
**Banco:** sem migração nesta frente.
**Verificações:** Verify Gate 0 · report-lint ok · lint ok · landmines ok · drift pulado — slot vazio
**Veredito:** 🟢 PASS
**Ledger:** `feature_id` conferencia-notas · `estado` shipado

**Posso finalizar (push + deploy + verificar)?**
- **sim** (recomendado) — publico os 5 arquivos acima: as 5 conferências passaram e o veredito é PASS.
- **não** — encerro sem publicar; tudo fica salvo nesta pasta.
- **não sei** — explico cada campo do bloco com o que ele quer dizer neste caso.

**Próximo passo** — Com o seu sim, publico e confiro o deploy; com o não, encerro aqui.

## Exemplo — antes do bloco, quando falta a revisão por outra engine (etapa 2 — Verificar)

Situação: o `adversarial-review.sh --conferir` saiu 2 — esta versão do código não tem revisão por outra
engine. A pergunta vem **antes** do bloco do OK, como uma pergunta própria; o bloco continua com uma só.

**Sua decisão** — [D3 · muda a regra do método] **Esta versão não tem revisão por outra engine. Como seguimos?**
- **rodar agora** (recomendado) — rodo o revisor e o auditor sobre o diff desta frente; leva em geral de 2 a
  15 minutos e mostro o custo no fim.
- **publicar sem revisão** — peço o motivo em uma frase; ele fica no registro da release.
- **não sei** — explico o que a revisão confere, com o último achado dela nesta frente, se houver.

As opções vêm logo depois da última linha do bloco: continua sendo uma pergunta só. Formato completo de
pergunta e de parada: `sdd/templates/fragments/PERGUNTA_DECISAO.md`.
